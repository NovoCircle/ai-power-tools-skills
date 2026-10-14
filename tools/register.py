#!/usr/bin/env python3
"""Generate TEST-REGISTER.md, the skills library's register of what is tested.

    python tools/register.py --write              # regenerate TEST-REGISTER.md
    python tools/register.py --check              # exit 1 when the committed file is stale
    python tools/register.py --seed-known-gaps    # one-time: record today's gaps in register.toml

Nobody types the list of parts. It is read from the product itself:

  skill            plugins/ai-power-tools/skills/*/SKILL.md          requires A
  helper program   manifest.json: every shipped .py under a tools/
                   folder that is not test_*.py                      requires U
  data asset       manifest.json: every shipped .yaml                requires U
  plugin surface   tools/register.toml, [[hand_row]]                 requires U and D

and each part is matched to its tests:

  A  skill acceptance: <skill>/references/test-cases.md exists and at least one case in it
     carries a "Covers:" line naming a heading that exists in that skill's SKILL.md.
     A case is a TC-nn heading or table row; a Covers line belongs to the nearest case above it.
  U  program: test_<program>.py in the same folder.
     asset / surface: a test module whose module-level COVERS tuple names the unit
     (COVERS = ("asset:ruleset-archimate31/archimate31_rules.yaml",)).
     plugin surface: the test files and CI steps its hand row names.
  D  install-and-first-call: a case file at the path the hand row names.

The register records whether a test EXISTS, never whether it passed. It is read from files and
the syntax tree only: no skill module is imported (pyarrow and PyYAML are optional there) and
nothing starts Enterprise Architect.

Results file (optional, read when it exists): tools/results/skill-acceptance.json
    {"version": "3.6.4", "skills": {"ea-modeling": {"passed": 8, "total": 9}}}
A skill with an entry reads "cases: 9 · last run 3.6.4: 8/9"; with a threshold in register.toml
([thresholds] ea-modeling = 80, or default = 80) it adds ", threshold 80%". No runner writes this
file yet, so every skill reads "not run".

The file is written with LF line endings and posix paths so the equality check in
tools/test_register.py holds on Windows and Linux alike. Neither this file nor
TEST-REGISTER.md is listed in manifest.json: they do not ship.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parent.parent
REGISTER_PATH = ROOT / "TEST-REGISTER.md"
TOML_PATH = ROOT / "tools" / "register.toml"
RESULTS_PATH = ROOT / "tools" / "results" / "skill-acceptance.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _layout import plugin_skills  # noqa: E402

KIND_ORDER = ("U", "L", "A", "I", "C", "P", "D")

_SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "dist", ".release-staging",
              ".plugin-release-staging", ".venv", "node_modules"}

GAPS_BEGIN = "# BEGIN known-gaps"
GAPS_END = "# END known-gaps"


# --------------------------------------------------------------------------- model

@dataclass
class Cell:
    state: str                 # "present" | "exempt" | "missing"
    text: str                  # what the row shows
    ids: list = field(default_factory=list)   # the satisfying test ids, for the Test index
    reason: str = ""


@dataclass
class Unit:
    id: str
    group: str                 # skill | prog | asset | srf
    required: tuple
    cells: dict
    extra: dict = field(default_factory=dict)


@dataclass
class Model:
    units: list
    problems: list            # structural problems the meta-test reports
    config: dict
    results: dict

    def unit(self, uid):
        for u in self.units:
            if u.id == uid:
                return u
        return None

    def gaps(self):
        return sorted((u.id, k) for u in self.units for k in u.required
                      if u.cells[k].state == "missing")


# --------------------------------------------------------------------------- reading

def load_config(path: Path = TOML_PATH) -> dict:
    with path.open("rb") as fh:
        return tomllib.load(fh)


def _rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _norm(text: str) -> str:
    """A heading or a Covers name, compared with backticks, quotes and a leading # removed."""
    text = text.strip().strip("#").strip()
    text = text.replace("`", "").replace('"', "").replace("'", "").replace("“", "").replace("”", "")
    return re.sub(r"\s+", " ", text).strip()


def headings_of(skill_md: Path) -> set:
    found, fenced = set(), False
    for line in skill_md.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if not fenced:
            m = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
            if m:
                found.add(_norm(m.group(1)))
    return found


_CASE_ID = re.compile(r"\bTC-\d+\b")
_COVERS = re.compile(r"^\s*(?:[-*]\s*)?\**covers\**\s*:\s*\**\s*(.+?)\s*$", re.I)


def parse_cases(path: Path) -> dict:
    """{'ids': [TC ids], 'covers': [(case id or None, line number, [names])]}."""
    ids, covers, current, fenced = [], [], None, False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if fenced:
            continue
        m = _COVERS.match(line)
        if m:
            names = [n for n in (_norm(p) for p in m.group(1).split(";")) if n]
            covers.append((current, number, names))
            continue
        starter = re.match(r"^(?:#{2,6}\s+|\|\s*\**)(TC-\d+)\b", line)
        if starter:
            current = starter.group(1)
            if current not in ids:
                ids.append(current)
    return {"ids": ids, "covers": covers}


def _module_info(path: Path, root: Path) -> dict:
    """Test function ids, the module-level COVERS tuple and local-only hints, from the syntax tree."""
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(path))
    rel = _rel(path, root)
    tests, covers = [], None
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            tests.append(f"{rel}::{node.name}")
        elif isinstance(node, ast.ClassDef):
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and sub.name.startswith("test_"):
                    tests.append(f"{rel}::{node.name}.{sub.name}")      # a double colon here would trip tools/gate.py
        elif isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "COVERS" for t in node.targets):
            covers = node.value
    entries, bad = [], None
    if covers is not None:
        if isinstance(covers, (ast.Tuple, ast.List)) and all(
                isinstance(e, ast.Constant) and isinstance(e.value, str) for e in covers.elts):
            entries = [e.value for e in covers.elts]
        else:
            bad = "COVERS must be a tuple of string literals"
    return {"path": rel, "tests": tests, "covers": entries, "covers_error": bad,
            "needs_example_model": "EA_EXAMPLE_MODEL" in text}


def test_modules(root: Path) -> dict:
    found = {}
    for path in sorted(root.rglob("test_*.py")):
        rel = path.relative_to(root)
        if any(part in _SKIP_DIRS for part in rel.parts):
            continue
        found[rel.as_posix()] = _module_info(path, root)
    return found


def _manifest_files(root: Path) -> list:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    return sorted(f for skill in manifest["skills"] for f in skill["files"])


def _source(rel: str, root: Path) -> Path:
    for base in (plugin_skills(root), root):
        if (base / rel).exists():
            return base / rel
    return plugin_skills(root) / rel


def _is_program(rel: str) -> bool:
    parts = rel.split("/")
    return rel.endswith(".py") and "tools" in parts[:-1] and not parts[-1].startswith("test_")


def _is_asset(rel: str) -> bool:
    return rel.endswith((".yaml", ".yml"))


def _imports_of(path: Path) -> set:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module.split(".")[0])
    return names


def _doc_mentions(root: Path, skills_dir: Path) -> dict:
    """{skill folder name: text of every .md file under it}, for the using-skill scan."""
    out = {}
    for d in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        out[d.name] = "\n".join(p.read_text(encoding="utf-8") for p in sorted(d.rglob("*.md")))
    return out


def load_results(root: Path = ROOT) -> dict:
    path = root / "tools" / "results" / "skill-acceptance.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- build

def _cell(unit_id, kind, exemptions, present, text, ids=()):
    if present:
        return Cell("present", text, list(ids))
    reason = exemptions.get((unit_id, kind))
    if reason:
        return Cell("exempt", f"exempt: {reason}", [], reason)
    return Cell("missing", "—")


def build(root: Path = ROOT, config: dict | None = None, results: dict | None = None) -> Model:
    config = load_config(root / "tools" / "register.toml") if config is None else config
    results = load_results(root) if results is None else results
    problems: list = []
    exemptions = {}
    for e in config.get("exemption", []):
        exemptions[(e.get("unit", ""), e.get("kind", ""))] = (e.get("reason") or "").strip()
    modules = test_modules(root)
    skills_dir = plugin_skills(root)
    manifest_files = _manifest_files(root)
    units: list = []

    # -- skills
    for sdir in sorted(p for p in skills_dir.iterdir() if p.is_dir() and (p / "SKILL.md").exists()):
        uid = f"skill:{sdir.name}"
        case_file = sdir / "references" / "test-cases.md"
        n_cases, ok_ids = 0, []
        if case_file.exists():
            parsed = parse_cases(case_file)
            n_cases = len(parsed["ids"])
            heads = headings_of(sdir / "SKILL.md")
            rel_case = _rel(case_file, root)
            for case, line, names in parsed["covers"]:
                bad = [n for n in names if n not in heads]
                if case is None:
                    problems.append(f"{rel_case}:{line}: a Covers line must follow a TC-nn case")
                elif bad:
                    problems.append(f"{rel_case}:{line}: Covers names no heading in "
                                    f"{sdir.name}/SKILL.md: {bad}")
                else:
                    ok_ids.append(f"{rel_case}#{case}")
        ok_ids = sorted(set(ok_ids))
        entry = (results.get("skills") or {}).get(sdir.name)
        if entry:
            run = f"last run {results.get('version', '?')}: {entry['passed']}/{entry['total']}"
            th = config.get("thresholds", {})
            threshold = th.get(sdir.name, th.get("default"))
            if threshold is not None:
                run += f", threshold {threshold}%"
        else:
            run = "not run"
        a_text = f"cases: {n_cases} · {run}"
        cell = _cell(uid, "A", exemptions, bool(ok_ids), a_text, ok_ids)
        if cell.state == "missing":
            cell.text = a_text        # a gap still shows its case count and run state
        units.append(Unit(uid, "skill", ("A",), {"A": cell},
                          {"cases": n_cases}))

    # -- who covers what
    covered_by: dict = {}
    for mod in modules.values():
        if mod["covers_error"]:
            problems.append(f"{mod['path']}: {mod['covers_error']}")
        for entry in mod["covers"]:
            covered_by.setdefault(entry, []).append(mod)

    # -- helper programs
    programs = [f for f in manifest_files if _is_program(f)]
    docs = _doc_mentions(root, skills_dir)
    importers: dict = {}
    for rel in programs:
        for name in _imports_of(_source(rel, root)):
            importers.setdefault(name, set()).add(rel)
    stems = {Path(p).stem: p for p in programs}

    def direct_users(rel):
        pat = re.compile(rf"(?<![\w-]){re.escape(Path(rel).name)}(?![\w])")
        return {name for name, text in docs.items() if name != "_shared" and pat.search(text)}

    def users(rel, seen=()):
        found = set(direct_users(rel))
        via = set()
        for parent in importers.get(Path(rel).stem, ()):
            if parent != rel and parent not in seen:
                inherited = users(parent, seen + (rel,))[0]
                via |= inherited - found
                found |= inherited
        return found, via

    for rel in sorted(programs):
        uid = f"prog:{rel}"
        sibling = _source(rel, root).parent / f"test_{Path(rel).stem}.py"
        mod = modules.get(_rel(sibling, root)) if sibling.exists() else None
        ids = list(mod["tests"]) if mod else []
        for extra in covered_by.get(uid, []):
            ids += [t for t in extra["tests"] if t not in ids]
        found, via = users(rel)
        cell = _cell(uid, "U", exemptions, bool(ids),
                     f"{len(ids)} tests ({Path(mod['path']).name})" if mod else f"{len(ids)} tests",
                     ids)
        units.append(Unit(uid, "prog", ("U",), {"U": cell},
                          {"users": sorted(found), "via": sorted(via),
                           "via_what": sorted(Path(p).name for p in importers.get(Path(rel).stem, ()))}))

    # -- data assets
    for rel in sorted(f for f in manifest_files if _is_asset(f)):
        uid = f"asset:{rel}"
        mods = covered_by.get(uid, [])
        ids = [t for m in mods for t in m["tests"]]
        local = bool(mods) and all(m["needs_example_model"] for m in mods)
        mod_names = ", ".join(Path(m["path"]).name for m in mods)
        text = f"present ({len(ids)} tests, {mod_names})" if mods else ""
        if local:
            text = f"present (runs locally only; {len(ids)} tests, {mod_names})"
        cell = _cell(uid, "U", exemptions, bool(ids), text, ids)
        units.append(Unit(uid, "asset", ("U",), {"U": cell}, {"local_only": local and bool(ids)}))

    # -- deployment surfaces (hand rows)
    workflow = (root / ".github" / "workflows" / "gate.yml")
    workflow_text = workflow.read_text(encoding="utf-8") if workflow.exists() else ""
    for row in config.get("hand_row", []):
        uid = row["unit"]
        required = tuple(row["required"])
        cells = {}
        if "U" in required:
            ids, n_tests, n_mod, n_step = [], 0, 0, 0
            for rel in row.get("u_tests", []):
                if rel in modules:
                    ids += modules[rel]["tests"]
                    n_tests += len(modules[rel]["tests"])
                    n_mod += 1
                else:
                    problems.append(f"{uid}: u_tests names {rel}, which is not a test module")
            for step in row.get("u_ci_steps", []):
                if re.search(rf"^\s*-?\s*name:\s*{re.escape(step)}\s*$", workflow_text, re.M):
                    ids.append(f".github/workflows/gate.yml::{step}")
                    n_step += 1
                else:
                    problems.append(f"{uid}: u_ci_steps names {step!r}, which is not a step in "
                                    ".github/workflows/gate.yml")
            parts = [f"{n_mod} test modules ({n_tests} tests)", f"{n_step} CI steps"]
            cells["U"] = _cell(uid, "U", exemptions, bool(ids), " + ".join(parts), ids)
        if "D" in required:
            case = row.get("d_case", "")
            exists = bool(case) and (root / case).is_file()
            cells["D"] = _cell(uid, "D", exemptions, exists, f"case file {case}", [case])
        units.append(Unit(uid, "srf", required, cells, {"note": row.get("note", "")}))

    model = Model(units, problems, config, results)
    problems.extend(validate(model, modules, covered_by))
    return model


def validate(model: Model, modules: dict, covered_by: dict) -> list:
    """Structural problems: stale exemptions, COVERS naming nothing."""
    ids = {u.id for u in model.units}
    out = []
    for e in model.config.get("exemption", []):
        unit, kind, reason = e.get("unit", ""), e.get("kind", ""), (e.get("reason") or "").strip()
        label = f"exemption ({unit!r}, {kind!r})"
        if not reason:
            out.append(f"{label} has no reason")
        u = model.unit(unit)
        if u is None:
            out.append(f"{label} names a unit that does not exist")
        elif kind not in u.required:
            out.append(f"{label} names a kind the unit does not require ({'/'.join(u.required)})")
    for entry, mods in sorted(covered_by.items()):
        if entry not in ids:
            for m in mods:
                out.append(f"{m['path']}: COVERS names {entry!r}, which is not a unit in the register")
    return out


# --------------------------------------------------------------------------- render

def _esc(text: str) -> str:
    return re.sub(r"\s+", " ", str(text)).replace("|", "\\|").strip()


def _verdict(unit: Unit) -> str:
    missing = [k for k in unit.required if unit.cells[k].state == "missing"]
    exempt = [k for k in unit.required if unit.cells[k].state == "exempt"]
    if missing:
        return "missing " + ", ".join(missing)
    if exempt:
        return f"complete ({len(exempt)} exemption{'s' if len(exempt) > 1 else ''})"
    return "complete"


def _table(header, rows):
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    lines += ["| " + " | ".join(_esc(c) for c in row) + " |" for row in rows]
    return lines


def render(model: Model) -> str:
    units = model.units
    by = lambda g: sorted((u for u in units if u.group == g), key=lambda u: u.id)  # noqa: E731
    out = [
        "# Test register: AI Power Tools skills library",
        "",
        "Generated by `python tools/register.py --write`. Do not edit by hand: the meta-test",
        "(`tools/test_register.py`) fails when this file differs from a fresh generation.",
        "Hand-kept inputs (exemptions, decisions, the known-gap list) are in `tools/register.toml`.",
        "",
        "This file records whether a test **exists**. Whether it passed belongs to the release record.",
        "Kinds: U = hermetic unit, A = skill acceptance, D = install-and-first-call.",
        "",
        "## Skills",
        "",
        "Required: A. Acceptance cases live in `<skill>/references/test-cases.md`; a case counts when it",
        "has a `Covers:` line naming a heading in that skill's SKILL.md.",
        "",
    ]
    out += _table(["Unit", "Required", "A", "Verdict"],
                  [[u.id, "A", u.cells["A"].text, _verdict(u)] for u in by("skill")])
    out += ["", "## Helper programs", "",
            "Required: U, a `test_<program>.py` beside the program. \"Used by\" is a scan of every",
            "skill's markdown for the program's file name, plus the programs that import it.", ""]
    rows = []
    for u in by("prog"):
        if u.extra["users"]:
            used = ", ".join(u.extra["users"])
            if u.extra["via"] and set(u.extra["via"]) == set(u.extra["users"]):
                used += f" (via {', '.join(u.extra['via_what'])})"
        else:
            used = "no using skill"
        rows.append([u.id, "U", u.cells["U"].text, used, _verdict(u)])
    out += _table(["Unit", "Required", "U", "Used by", "Verdict"], rows)
    out += ["", "## Data assets", "",
            "Required: U, a test module whose module-level `COVERS` names the asset. Tests that read",
            "`EAExample.qea` skip on a machine without Enterprise Architect, and the cell says so.", ""]
    out += _table(["Unit", "Required", "U", "Verdict"],
                  [[u.id, "U", u.cells["U"].text, _verdict(u)] for u in by("asset")])
    out += ["", "## Deployment surfaces", ""]
    out += _table(["Unit", "Required", "U", "D", "Verdict"],
                  [[u.id, " ".join(u.required),
                    u.cells["U"].text if "U" in u.cells else "n/a",
                    u.cells["D"].text if "D" in u.cells else "n/a",
                    _verdict(u)] for u in by("srf")])

    out += ["", "## Test index", "",
            "Every satisfying test id, grouped by unit and kind. A unit with no entry has no test of",
            "that kind. Function ids are read from the syntax tree, so a parametrized test is one id, and a",
            "method of a test class is written `Class.test_name`.", ""]
    for u in sorted(units, key=lambda u: u.id):
        for k in sorted(u.required, key=KIND_ORDER.index):
            cell = u.cells[k]
            if cell.ids:
                out.append(f"- `{u.id}` {k} ({len(cell.ids)})")
                out += [f"  - `{t}`" for t in cell.ids]

    out += ["", "## Exemptions", ""]
    exempt = [(u.id, k, u.cells[k].reason) for u in units for k in u.required
              if u.cells[k].state == "exempt"]
    if exempt:
        out += _table(["Unit", "Kind", "Reason"], sorted(exempt))
    else:
        out.append("None. A part may skip a kind of test only with a written reason in `tools/register.toml`.")

    out += ["", "## Decisions", "",
            "Quoted from `tools/register.toml`. Nothing here is decided until its status says so.", ""]
    decisions = model.config.get("decisions", {})
    rows = []
    for key in sorted(decisions):
        d = decisions[key]
        rows.append([key, d.get("question", ""), d.get("status", "pending"), d.get("answer", "")])
    out += _table(["#", "Question", "Status", "Answer"], rows)

    out += ["", "## Totals", ""]
    counts = []
    for group, label in (("skill", "Skill"), ("prog", "Helper program"),
                         ("asset", "Data asset"), ("srf", "Deployment surface")):
        for kind in KIND_ORDER:
            members = [u for u in units if u.group == group and kind in u.required]
            if members:
                s = [u.cells[kind].state for u in members]
                counts.append([label, kind, len(members), s.count("present"),
                               s.count("exempt"), s.count("missing")])
    out += _table(["Unit kind", "Required", "Units", "Present", "Exempt", "Missing"], counts)
    progs = by("prog")
    unused = [Path(u.id[5:]).name for u in progs if not u.extra["users"]]
    assets = by("asset")
    local = sum(1 for u in assets if u.extra["local_only"])
    with_u = sum(1 for u in assets if u.cells["U"].state == "present")
    out += ["",
            f"- Skills without A: {sum(1 for u in by('skill') if u.cells['A'].state == 'missing')} "
            f"of {len(by('skill'))}.",
            f"- Helper programs with no using skill: {len(unused)}"
            + (f" ({', '.join(unused)})." if unused else "."),
            f"- Data assets with U that run locally only: {local} of {with_u}.",
            f"- Gaps in all: {len(model.gaps())}."]
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------- known gaps

def known_gaps(config: dict) -> list:
    out = []
    for entry in config.get("known_gaps", []):
        unit, _, kind = entry.rpartition(" ")
        out.append((unit, kind))
    return sorted(out)


def seed_known_gaps(model: Model, path: Path = TOML_PATH) -> int:
    if known_gaps(load_config(path)):
        print("register.toml already holds a known-gap list; the ratchet only shrinks, by hand. "
              "Nothing written.", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8")
    start, end = text.find(GAPS_BEGIN), text.find(GAPS_END)
    if start < 0 or end < start:
        print(f"register.toml lacks the {GAPS_BEGIN} / {GAPS_END} markers", file=sys.stderr)
        return 2
    body = "known_gaps = [\n" + "".join(f'  "{u} {k}",\n' for u, k in model.gaps()) + "]\n"
    first_line_end = text.index("\n", start) + 1
    path.write_bytes((text[:first_line_end] + body + text[end:]).encode("utf-8"))
    print(f"seeded {len(model.gaps())} known gaps into {path.name}")
    return 0


# --------------------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="regenerate TEST-REGISTER.md")
    mode.add_argument("--check", action="store_true", help="fail when TEST-REGISTER.md is stale")
    mode.add_argument("--seed-known-gaps", action="store_true",
                      help="record today's gaps in register.toml (one time)")
    args = ap.parse_args(argv)
    model = build()
    if args.seed_known_gaps:
        return seed_known_gaps(model)
    text = render(model)
    if args.write:
        REGISTER_PATH.write_bytes(text.encode("utf-8"))
        print(f"wrote {REGISTER_PATH.name}: {len(model.units)} units, {len(model.gaps())} gaps")
        return 0
    current = REGISTER_PATH.read_bytes() if REGISTER_PATH.exists() else b""
    if current != text.encode("utf-8"):
        print("TEST-REGISTER.md is stale: run `python tools/register.py --write` and commit it",
              file=sys.stderr)
        return 1
    print("TEST-REGISTER.md is current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
