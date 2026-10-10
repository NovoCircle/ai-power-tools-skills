#!/usr/bin/env python3
"""Release gate for the AI Power Tools Skills library.

Enforces the standing rule in C:\\SparxServices\\CLAUDE.md: no real customer
names, no absolute local paths, no personal identifiers in anything we ship.
Westbrook Bank is the only permitted example organization. Also enforces that
nothing from the Sparx diagram gallery — corpus image or example subject —
reaches the bundle.

Usage:
    python tools/gate.py            # check the whole library
    python tools/gate.py ea-com     # check one skill

Exit code 0 = clean, 1 = violations found.
"""
from __future__ import annotations

import re
from typing import Optional
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Manifest paths are install-relative, so they do not say where a file sits in
#: the repo. Skills live under the plugin -- one tree serving both the
#: marketplace and the packaged `.plugin` -- while the rulesets stay at the root
#: because `ea-validation` pins a raw.githubusercontent URL into them.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _layout import source_path as _source_path, asset_dirs as _asset_dirs  # noqa: E402

# --------------------------------------------------------------------------
# Rule 1 — known real-customer identifiers. Denylist: catches what we know.
# --------------------------------------------------------------------------
# A path is fine when the user-specific segment is an obvious placeholder:
#   C:\Users\<you>\AppData\...   — the reader substitutes their own name.
# Only a *real* username or our own working tree is a violation.
PLACEHOLDER_PATH = re.compile(r"[A-Za-z]:\\{1,2}Users\\{1,2}[<%{$]")

# "TEA Framework" is a technology that genuinely ships with stock Sparx
# Enterprise Architect, so that exact phrase is allowed. Anything that reads as a
# CUSTOMER extension of it is not: TEA on its own, TEA:: as a stereotype prefix,
# TEA inside a customer's own identifier like "CA EDD TEA", and "TEA Framework"
# followed by extension wording (Extension, Custom, Customization, Profile, MDG,
# Toolbox, Add-in). A customer MDG built on the Sparx technology therefore still
# trips the gate for a human decision. The same rule is in the server repo's gate.
FORBIDDEN = [
    (re.compile(r"\bTVO\b"), "real customer identifier 'TVO'"),
    (re.compile(r"\bTEA\b(?!\s+Framework\b(?!\s+(?i:Extensions?|Extended|Custom|"
                r"Customi[sz](?:ed|ation)|Profiles?|MDG|Toolbox(?:es)?|Add-?ins?)\b))"),
     "real customer identifier 'TEA'"),
    (re.compile(r"\bCA\s+EDD\b|\bEDD\b"), "real customer identifier 'EDD'"),
    (re.compile(r"TechVentures", re.I), "non-canonical example org 'TechVentures'"),
    (re.compile(r"RyanSchmierer|rschmierer", re.I), "personal identifier"),
    (re.compile(r"[A-Za-z]:\\\\?(?:SparxServices|Users)\b"), "absolute local path"),
    (re.compile(r"/c/(?:SparxServices|Users)\b"), "absolute local path"),
]

# --------------------------------------------------------------------------
# Rule 2 — unknown MDG/model identifiers. Allowlist: catches what we don't.
#
# A *new* customer name must trip the gate the first time it appears, so any
# MDG-shaped id or .qea filename that is neither Westbrook nor a Sparx-shipped
# technology is reported for a human decision.
# --------------------------------------------------------------------------
KNOWN_IDS = {
    # Westbrook Bank — the canonical example org
    "WBA", "WestbrookBankArchitecture", "WestbrookBank",
    # Sparx-shipped sample model. Every EA install has it, so citing it is how
    # a measurement in a shipped binding stays reproducible by the reader. It
    # is a vendor file, not anybody's model.
    "EAExample",
    # Sparx-shipped / standard technologies
    "ArchiMate", "ArchiMate2", "ArchiMate3", "BPMN", "BPMN2", "BPMN20",
    # BMM is the OMG Business Motivation Model, shipped by Sparx as
    # InternalTechnologies/BMM.xml, with bmm_* model patterns beside it.
    # Proof it is nobody's project code: EAExample.qea itself stores an
    # element whose stereotype FQName is `BMM::CourseOfAction`.
    "BMM",
    # EA's extended diagram set -- Data Modeling, Dashboard, Requirements
    # and others. A Sparx-shipped technology id, verified from the
    # reference model's own MDGDgm tokens, not a project code.
    "Extended",
    "UML", "SysML", "SysML15", "SysML16", "TOGAF", "DoDAF", "MODAF", "NIEM",
    # UPDM2 is the second-generation Sparx-shipped UPDM technology and appears
    # as an FQName namespace in real repositories (`UPDM2::Node`). `UPDM` alone
    # was listed, so a measurement citing the id EA actually writes was flagged.
    "UPDM", "UPDM2", "SPEM", "SOMF", "BPEL", "XSD", "WSDL", "ERD", "DMN", "CMMN",
    # EA's own internal UML profile. `EAUML::report package` is EA's machinery,
    # which the census has to recognize in order to EXCLUDE it - so the id has
    # to be nameable in our own source.
    "EAUML",
    # The UML 2 Standard Profile EA ships and applies by default. Real
    # repositories carry `StandardProfileL2::Realization` on ordinary
    # Realization connectors, so a skill citing what `t_xref` actually holds
    # was flagged as naming a customer technology.
    "StandardProfileL2",
    "MDG", "EA", "XMI", "SQL", "COM", "API", "XML", "YAML", "JSON", "HTML",
    "PNG", "SVG", "CSV", "UTF", "BOM", "URL", "ID", "OK", "NOT", "AND", "OR",
    # EA's strategic-modeling and mind-mapping MDGs, read from the reference
    # model's own `MDGDgm` values rather than guessed. Both look like a made-up
    # name to this rule precisely because neither spells a standard notation, and
    # both are Sparx-shipped: `StrategyMap` declares six diagram types
    # (StrategyMap, BalancedScorecard, ValueChain, DecisionTree, OrgChart,
    # FlowChart) and `MindMapping` declares one of its own name.
    "StrategyMap", "MindMapping",
    # UAF/UPDM. EA ships this as EIGHT separate technology ids, one per
    # viewpoint, not as one "UAF" — read from the loaded MDG, not guessed.
    # A binding names them because a binding binds exactly one id.
    "UAF", "UAFP", "UAFP_Framework", "UAFP_AV", "UAFP_AcV", "UAFP_OV",
    "UAFP_SOV", "UAFP_SV", "UAFP_SvcV", "UAFP_StV", "UAFP_CV", "UAFP_PV",
    "UAFP_TV", "UAFP_StdV",
    # TOGAF and Zachman, the two FRAMEWORK overlays. Same lesson as UAF: EA does
    # not ship one id per framework. TOGAF is two (`TOGAF Diagrams` and
    # `TOGAF_DataArchitecture`) and Zachman is seven (`ZF` plus one per framework
    # row), read from the loaded MDG rather than guessed. Only the ones without a
    # space belong here; the rest are in KNOWN_SPACED_IDS below, because MDG_NS
    # cannot see a space.
    "TOGAF_DataArchitecture", "ZF", "ZF_Interface", "TOGAF_Interface",
    # UAF/DoDAF/MODAF viewpoint abbreviations. Standard framework vocabulary
    # (Services, Capability, Project, Operational, Strategic, Acquisition,
    # Technical/Standards), not anybody's project code.
    "AV", "AcV", "OV", "SOV", "SV", "SvcV", "StV", "CV", "PV", "TV", "StdV",
    # Deliberately generic test stubs. Two or three interchangeable
    # technologies are needed to test ambiguity and override behavior, and
    # naming them after a real notation would imply the test says something
    # about that notation. No customer is involved.
    "Alpha", "Beta", "Overlay",
    # Generic placeholder model filenames in tests. Not anybody's model.
    "model", "missing",
}

# Sparx-shipped technology ids that CONTAIN A SPACE, which `MDG_NS` cannot see:
# it captures the last word only, so `TOGAF Diagrams::TOGAF_Interface` arrives as
# `Diagrams` and `ZF Owner::OwnerTime` as `Owner`. Putting those bare words into
# KNOWN_IDS would whitelist `Acme Diagrams::` and `Contoso Owner::` along with
# them, which is the opposite of what this rule is for, so the FULL id is matched
# against the line instead and the bare word stays unknown.
KNOWN_SPACED_IDS = (
    "TOGAF Diagrams",
    # Sparx-shipped, and the technology behind the corpus row whose
    # diagram type is TechnicalReferenceModel -- which was being counted
    # under TOGAF until it was measured.
    "FEAF Diagrams",
    "ZF Interface", "ZF Owner", "ZF Designer", "ZF Planner", "ZF Builder",
    "ZF Subcontractor",
    # Sparx-shipped (see the TEA note under Rule 1). Its own namespace is
    # allowed; a customer extension's namespace is not.
    "TEA Framework",
)
QEA_FILE = re.compile(r"\b([A-Za-z][A-Za-z0-9_-]*)\.(?:qea|eapx|eap|feap)\b")
MDG_NS = re.compile(r"\b([A-Z][A-Za-z0-9_]{1,30})::")

# --------------------------------------------------------------------------
# Rule 3 — encoding hygiene
# --------------------------------------------------------------------------
# The first four alternatives are the historical list, kept so nothing that
# used to be caught stops being caught. The fifth is the general rule they
# were special cases of: a double-encoding always leaves a lead character of
# U+00C2 / U+00C3 / U+00E2 followed by another non-ASCII one. The old list
# missed "â‰", which let a mangled >= through in the sibling repo's shipped
# docs. Keep this in step with ea-mcp-server/build.py's _MOJIBAKE.
MOJIBAKE = re.compile("â€|Ã¢|â†|Â |[ÂÃâ][^\x00-\x7f]")
FENCE = re.compile(r"^```")
CURLY = re.compile(r"[\u2018\u2019\u201c\u201d]")

# --------------------------------------------------------------------------
# Rule 4 — the Sparx diagram gallery must not leak into the bundle.
#
# The 147-image benchmark corpus under research/sparx-diagram-gallery/ is
# Sparx Systems' copyrighted work. It is ours to measure against, not ours to
# republish. The same goes for the gallery's example subjects: Hardware
# Retailer, HSUV and Distiller are Sparx's inventions, so naming one in a
# shipped skill would borrow their work *and* break the Westbrook-only rule in
# CLAUDE.md. Our generated equivalents belong to Westbrook Bank and must be
# named that way.
#
# Two halves, because the leak has two shapes.
#
# 1. An image file. The bundle ships no images at all — skills are text and
#    the manifest lists only .md/.yaml — so "any image here" is the truer
#    rule, and the only one that survives a corpus image being renamed on the
#    way in. The catalog is read when it is reachable, purely to name *which*
#    corpus image it is; when research/ is absent (a customer or CI checkout
#    of the bundle alone) the image is still blocked, just described
#    generically. Enforcement never depends on the catalog, so a catalog that
#    rots cannot quietly disarm the rule.
#
# 2. A gallery example subject in bundle text or in a shipped path. Curated by
#    hand rather than derived from the catalog, because deciding which of the
#    147 filenames is Sparx's invention and which is ordinary industry
#    vocabulary is a judgment call — a list generated from the filenames would
#    have shipped `deployment-diagram` and `heat-map` as violations.
#
# Deliberately NOT caught. Each is a term a legitimate skill could reasonably
# use, and a rule that cries wolf is a rule someone switches off:
#   Travel Booking, Email Voting, Book Lending — gallery BPMN subjects, but
#     ordinary business-process vocabulary industry-wide.
#   Smart Home, Customer Login, Pedestrian Crossing, Manage Inventory, States
#     of Water — textbook state-machine and use-case subjects, nobody's to own.
#   Flip Flop, OpAmp, Liquid Tank, SysPhS — electronics and physics
#     vocabulary; SysPhS is an OMG standard name.
#   Connected Vehicle, Chef Automate — AWS and Chef reference architectures
#     the gallery reproduces. Someone else's marks, and a different problem.
#   Framework names (TOGAF, Zachman, ArchiMate viewpoint titles) — standards.
#   Either half of a two-word subject on its own: "hardware requirements" and
#     "book storage" are innocent, so the words must be adjacent. Inflections
#     past a plural or a -y ending are not caught either.
# --------------------------------------------------------------------------
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".svg"}

# Empty on purpose, and the only sanctioned way past the image rule. If a
# skill ever has a real reason to ship an image, check its provenance and add
# its bundle-relative path here: that is a one-line diff a reviewer can weigh,
# which loosening the rule is not.
ALLOWED_IMAGES: set[str] = set()

# Where the corpus index lives, relative to the workspace root. Not required
# to exist.
CATALOG_REL = Path("research/sparx-diagram-gallery/catalog-rescored.tsv")


def _subject(*words: str) -> re.Pattern:
    """Match a gallery subject however it is spelled.

    `Hardware Retailer` has to be caught as `hardware-retailer` in a filename
    and `HardwareRetailer` in an identifier as readily as in prose, so the gap
    between words matches a space, hyphen, underscore, or nothing at all. A
    trailing plural or -y is absorbed so `Distillery` and `Bookstores` count.
    """
    return re.compile(r"\b" + r"[\s_-]*".join(words) + r"(?:s|es|y|ies)?\b", re.I)


GALLERY_SUBJECTS = [
    (_subject("Hardware", "Retailer"), "Hardware Retailer"),
    (_subject("HSUV"), "HSUV"),
    (_subject("Hybrid", "SUV"), "Hybrid SUV"),
    (_subject("Distiller"), "Distiller"),
    (_subject("Book", "store"), "Bookstore"),
    (_subject("Nobel", "Prize"), "Nobel Prize"),
]
GALLERY_WHY = "Sparx's, not ours; convert to Westbrook Bank"

MAX_SKILL_LINES = 400

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", ".pytest_cache"}
# tools/ holds this script, whose own patterns would trip it.
# gate.py holds the forbidden patterns themselves, and test_gate.py holds
# the fixtures that prove they fire. Both are deliberately full of the
# strings this gate exists to reject, and neither is shipped - the
# manifest does not list tools/.
SKIP_FILES = {"gate.py", "test_gate.py"}


def iter_files(target: Path):
    for p in sorted(target.rglob("*")):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.name in SKIP_FILES:
            continue
        if p.suffix.lower() in {".md", ".yaml", ".yml", ".json", ".py", ".txt"}:
            yield p


def check_file(path: Path) -> list[str]:
    out: list[str] = []
    rel = path.relative_to(ROOT)
    raw = path.read_bytes()

    if raw.startswith(b"\xef\xbb\xbf"):
        out.append(f"{rel}:1: UTF-8 BOM — strip it")

    text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()

    for pattern, subject in GALLERY_SUBJECTS:
        if pattern.search(rel.as_posix()):
            out.append(f"{rel}: gallery example subject '{subject}' in the file path "
                       f"— {GALLERY_WHY}")

    in_fence = False
    for n, line in enumerate(lines, 1):
        if FENCE.match(line.strip()):
            in_fence = not in_fence
            continue

        for pattern, why in FORBIDDEN:
            if not pattern.search(line):
                continue
            if why == "absolute local path" and PLACEHOLDER_PATH.search(line):
                continue
            out.append(f"{rel}:{n}: {why} — convert to Westbrook Bank: {line.strip()[:90]}")

        for pattern, subject in GALLERY_SUBJECTS:
            if pattern.search(line):
                out.append(f"{rel}:{n}: gallery example subject '{subject}' "
                           f"— {GALLERY_WHY}: {line.strip()[:90]}")

        if MOJIBAKE.search(line):
            out.append(f"{rel}:{n}: mojibake — file was written as cp1252")

        if in_fence and CURLY.search(line):
            out.append(f"{rel}:{n}: curly quotes inside a code block — breaks copy/paste")

        for m in QEA_FILE.finditer(line):
            if m.group(1) not in KNOWN_IDS:
                out.append(f"{rel}:{n}: unrecognized model file '{m.group(0)}' — "
                           f"if this is a real customer model, convert it")
        for m in MDG_NS.finditer(line):
            ident = m.group(1)
            if ident in KNOWN_IDS or ident.startswith("WBA"):
                continue
            # A known id with a space in it: the capture is only its last word,
            # so the check is whether the text ending there IS the whole id.
            if any(line[:m.end(1)].endswith(full) for full in KNOWN_SPACED_IDS):
                continue
            out.append(f"{rel}:{n}: unrecognized MDG namespace '{ident}::' — "
                       f"if this is a real customer technology, convert it")

    if path.name == "SKILL.md" and len(lines) > MAX_SKILL_LINES:
        out.append(f"{rel}: {len(lines)} lines — over the {MAX_SKILL_LINES}-line limit; "
                   f"move detail into references/")

    return out


def _find_catalog() -> Optional[Path]:
    """Locate the corpus catalog by walking up from the library root.

    The skills library sits inside the workspace that also holds research/; a
    bundle-only checkout has no such parent to find, which is the expected
    case for a customer and for CI.
    """
    for base in (ROOT, *ROOT.parents):
        candidate = base / CATALOG_REL
        if candidate.is_file():
            return candidate
    return None


def corpus_image_names(catalog: Optional[Path] = None) -> set[str]:
    """Lowercased basenames of the benchmark corpus images, read from the catalog.

    Column 1 of the TSV is the image filename. Reading it beats pasting 147
    filenames in here, which would rot the first time the corpus changed.

    Returns an empty set when the catalog is not reachable. That degrades the
    *description* of a finding, never the finding itself: check_images blocks
    every image either way, and only says which corpus image it is when it can
    prove it.
    """
    path = Path(catalog) if catalog is not None else _find_catalog()
    if path is None or not path.is_file():
        return set()

    names: set[str] = set()
    for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines()):
        first = line.split("\t", 1)[0].strip()
        if n == 0 or not first:
            continue
        if Path(first).suffix.lower() in IMAGE_SUFFIXES:
            names.add(first.lower())
    return names


def check_images(target: Path, catalog: Optional[Path] = None) -> list[str]:
    """No image ships from this library. See Rule 4.

    `catalog` overrides where the corpus index is read from, so tests exercise
    both the identified and the unidentified path on any machine.
    """
    corpus = corpus_image_names(catalog)
    out: list[str] = []
    for p in sorted(target.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        rel = p.relative_to(ROOT).as_posix()
        if rel in ALLOWED_IMAGES:
            continue
        if p.name.lower() in corpus:
            out.append(f"{rel}: benchmark corpus image '{p.name}' — Sparx Systems' "
                       f"copyrighted reference image; it stays in research/ and "
                       f"must not ship")
        else:
            out.append(f"{rel}: image file in the bundle — skills ship text only, so "
                       f"this is unreviewed artwork or a renamed corpus image; check "
                       f"its provenance and list it in ALLOWED_IMAGES if it is ours")
    return out


def check_manifest() -> list[str]:
    """Every manifest hash must match the file on disk, byte for byte.

    The installer verifies each download against this map and refuses a
    mismatch, so a stale hash means the skill cannot install. This is also
    the CRLF trap: a checkout that rewrites line endings after the map was
    generated silently invalidates it. `.gitattributes` pins LF; this is the
    check that proves it held.
    """
    import hashlib
    import json

    out: list[str] = []
    mf = ROOT / "manifest.json"
    if not mf.exists():
        return ["manifest.json: missing"]

    mf_raw = mf.read_bytes()
    if b"\r\n" in mf_raw:
        out.append("manifest.json: CRLF line endings — assets must ship as LF")

    m = json.loads(mf_raw.decode("utf-8"))
    listed: set[str] = set()
    for skill in m.get("skills", []):
        for rel, want in skill.get("sha256", {}).items():
            listed.add(rel)
            f = _source_path(rel, ROOT)
            if not f.exists():
                out.append(f"manifest.json: lists a missing file: {rel}")
                continue
            raw = f.read_bytes()
            got = hashlib.sha256(raw).hexdigest()
            if got != want:
                out.append(f"manifest.json: stale sha256 for {rel} "
                           f"(manifest {want[:12]}…, file {got[:12]}…) — "
                           f"run tools/regen-manifest.py")
            if b"\r\n" in raw:
                out.append(f"{rel}: CRLF line endings — assets must ship as LF")

    for base, skill_dir in _asset_dirs(ROOT):
        for f in skill_dir.rglob("*"):
            # Tool caches are not assets. `.pytest_cache/README.md` appears the
            # moment anybody runs the skill's own tests, and reporting it turns
            # the gate red for a reason nobody can act on -- which is how a
            # release gate stops being read.
            if any(part in SKIP_DIRS for part in f.parts):
                continue
            if f.is_file() and f.suffix.lower() in {".md", ".yaml", ".yml"}:
                rel = f.relative_to(base).as_posix()
                if rel not in listed:
                    out.append(f"{rel}: present in the repo but not in manifest.json "
                               f"— it will not ship")
    return out


_STATED_VERSION = re.compile(r"\bv(\d+\.\d+\.\d+)\+")


def check_stated_server_version() -> list[str]:
    """A server version a skill states in its tools line must be its floor.

    The tools line is the italic `*Tools: ...*` block under the title. When it
    names a server version (`v3.6.0+`), that version must equal the skill's
    `min_server_version` in manifest.json, which is the floor the installer
    enforces. A skill whose text says one version while the manifest says
    another tells the reader the wrong requirement. APT-2026-0337.
    """
    import json

    mf = ROOT / "manifest.json"
    if not mf.exists():
        return []
    out: list[str] = []
    for skill in json.loads(mf.read_text(encoding="utf-8")).get("skills", []):
        name, floor = skill.get("name", ""), skill.get("min_server_version", "")
        f = _source_path(f"{name}/SKILL.md", ROOT)
        if not f.exists():
            continue
        block: list[str] = []
        for line in f.read_text(encoding="utf-8").splitlines():
            if not block and not line.startswith(("*Tool:", "*Tools:")):
                continue
            block.append(line)
            if line.rstrip().endswith("*"):
                break
        for stated in _STATED_VERSION.findall("\n".join(block)):
            if stated != floor:
                out.append(f"{name}/SKILL.md: tools line states v{stated}+ but "
                           f"manifest.json min_server_version is {floor}")
    return out


def _version_key(v: str) -> tuple[int, ...]:
    return tuple(int(p) for p in v.split("."))


def check_bundle_floor() -> list[str]:
    """The bundle's `min_server_version` must not sit below any skill's.

    The installer enforces the bundle-level floor all-or-nothing and treats
    the per-skill floors as finer detail. A bundle floor below a skill's lets a
    server that is too old for that skill install the rest of the bundle and
    take delivery of a partial set that documents operations it does not have.
    """
    import json

    mf = ROOT / "manifest.json"
    if not mf.exists():
        return []
    data = json.loads(mf.read_text(encoding="utf-8"))
    bundle = data.get("min_server_version", "")
    floors = {s.get("name", ""): s["min_server_version"]
              for s in data.get("skills", []) if s.get("min_server_version")}
    if not floors:
        return []
    try:
        highest_name = max(floors, key=lambda n: _version_key(floors[n]))
        highest = floors[highest_name]
        if bundle and _version_key(bundle) >= _version_key(highest):
            return []
    except ValueError:
        return [f"manifest.json: a min_server_version is not a dotted number "
                f"(bundle {bundle!r})"]
    return [f"manifest.json: bundle min_server_version is {bundle or 'missing'} "
            f"but {highest_name} requires {highest}. Raise the bundle floor to "
            f"at least {highest}."]


def check_plugin_package() -> list[str]:
    """The plugin is skills only, and its version files and stamp agree.

    Fails when `plugin.json` declares `mcpServers` at all or the plugin tree has
    a top-level `bin/`: claude.ai refuses a plugin that points at an `.mcpb`,
    and a plugin's server never runs in Claude Desktop chat or Cowork, so the
    server is the separately installed Desktop extension. Also runs the version
    consistency check that `tools/build-plugin.py` runs, including the
    skills-version stamp in `ea-start-here`.
    """
    import importlib.util

    plugin = ROOT / "plugins" / "ai-power-tools"
    manifest = ROOT / "manifest.json"
    marketplace = ROOT / ".claude-plugin" / "marketplace.json"
    if not (plugin / ".claude-plugin" / "plugin.json").is_file():
        return []
    spec = importlib.util.spec_from_file_location(
        "build_plugin", Path(__file__).resolve().parent / "build-plugin.py")
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    out = [f"plugin: {p}" for p in build.package_problems(plugin)]
    if manifest.is_file() and marketplace.is_file():
        out.extend(f"plugin: {p}" for p in
                   build.version_problems(plugin, manifest, marketplace)[1])
    return out


_OP_DRIFT_RAN = True
_OP_DRIFT_SKIP_REASON: Optional[str] = None


def op_drift_ran() -> bool:
    """False when the last check_op_drift call could not read the server."""
    return _OP_DRIFT_RAN


def op_drift_skip_reason() -> Optional[str]:
    """Why the last check_op_drift call did not run, or None if it did."""
    return _OP_DRIFT_SKIP_REASON


def _op_drift_skipped(reason: str) -> list[str]:
    """Record that the check did not run, and say so.

    Every early return from check_op_drift comes through here. Three of them
    used to return quietly, having only printed a note: a missing
    gen-operations.py, a module that would not import, and a server whose
    operations could not be collected. Only the missing-server path set the
    flag, so the other three could leave the verdict a clean GREEN while the
    check had not run at all -- which is the defect this guards, one level in.
    """
    global _OP_DRIFT_RAN, _OP_DRIFT_SKIP_REASON
    _OP_DRIFT_RAN = False
    _OP_DRIFT_SKIP_REASON = reason
    print(f"  !! OP-DRIFT CHECK DID NOT RUN: {reason}")
    print("     Skills naming a renamed or invented operation will NOT be "
          "caught by this run.")
    return []


def check_op_drift(target: Path, server: Optional[Path] = None) -> list[str]:
    """Every operation a skill names must exist in the server's dispatch tables.

    This is the drift that is invisible until a customer hits it: a skill
    confidently instructs the model to call an operation that was renamed or
    never existed, and the failure surfaces as a confusing error on someone
    else's machine. The server has already shipped links to two skills that
    were never written; this is the same class in the other direction.

    Only explicit ``operation="name"`` call sites are checked. That is
    deliberately narrow — prose mentioning a name in backticks is not a call,
    and flagging it would train people to ignore the gate.

    `server` overrides where the dispatch tables are read from. It defaults to
    the sibling server checkout; tests pass their own so the detection logic is
    exercised everywhere, not only on a machine that happens to have both repos.

    Skipped when the server source is not available (for example in CI, where
    only this repo is checked out). A check that cannot run must not masquerade
    as a check that passed, so the notice is loud and `op_drift_ran()` reports
    whether the last call actually checked anything.
    """
    # Each call is authoritative about itself. Without this the flag only ever
    # moved one way: a run that skipped left it False for the life of the
    # process, so a later successful call still reported as skipped.
    global _OP_DRIFT_RAN, _OP_DRIFT_SKIP_REASON
    _OP_DRIFT_RAN = True
    _OP_DRIFT_SKIP_REASON = None

    # Loaded by path: the filename contains a hyphen, so it is not importable
    # by name.
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "gen_operations", Path(__file__).resolve().parent / "gen-operations.py")
    if spec is None or spec.loader is None:
        return _op_drift_skipped("tools/gen-operations.py not found")
    gen = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(gen)
    except Exception as e:
        return _op_drift_skipped(f"tools/gen-operations.py did not import: {e}")

    server = Path(server) if server is not None else gen.DEFAULT_SERVER
    if not server.is_file():
        return _op_drift_skipped(
            f"no server source at {server} (pass --server PATH to point at it)"
        )

    try:
        known: set[str] = set()
        for ops in gen.collect_operations(server).values():
            known.update(ops)
    except Exception as e:
        return _op_drift_skipped(f"could not read operations from {server}: {e}")

    call_site = re.compile(r'operation\s*=\s*["\']([a-z_][a-z0-9_]*)["\']')
    out: list[str] = []
    for path in iter_files(target):
        if path.suffix.lower() != ".md":
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for op in call_site.findall(line):
                if op not in known:
                    rel = path.relative_to(ROOT).as_posix()
                    out.append(
                        f"{rel}:{n}: names operation '{op}', which is not in the "
                        f"server's dispatch tables — renamed, removed, or invented"
                    )
    return out


# The installed ruleset path. Rulesets carry no SKILL.md, so the installer
# deliberately writes them OUTSIDE the skills directory (see
# ``skills_installer._destination_root``). A skill that documents them under
# ~/.claude/skills sends the reader to a directory the installer never writes.
#
# Bundle 1.4.1 DID install them among the skills, and that stale copy was the
# only thing making the old documented path resolve. Pruning the copy exposed
# the bug: upgraders had been reading 1.4.1 rules and getting confident wrong
# answers, and fresh installs found nothing at all.
#
# Repo-relative mentions and raw.githubusercontent URLs are correct and must
# keep passing -- URL fetch reads the REPO layout, not the install layout. So
# this matches only a path rooted at the skills directory.
_RULESET_IN_SKILLS_DIR = re.compile(
    "[.]claude/skills/[^ ]*ruleset", re.I)
_INSTALLED_RULESET_DIR = "ai-power-tools/rulesets"
BACKSLASH = chr(92)


def check_ruleset_paths(target: Path) -> list[str]:
    """Two-sided: no skill may document the old path, and some skill must
    document the new one.

    The positive half matters because a rename or a deletion would satisfy the
    ban while quietly removing the only instruction a customer has for running
    a ruleset from disk.

    ``tools/`` is skipped. This function's own comment contains the string it
    forbids, and a guard that fires on its own explanation teaches the next
    reader to delete the explanation.
    """
    out: list[str] = []
    documents_new = False
    for f in iter_files(target):
        rel = f.relative_to(ROOT)
        if rel.parts and rel.parts[0] == "tools":
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        # Normalize separators here too. The first version checked the raw
        # text, so documenting the path in Windows form -- which is what a
        # customer on Windows needs, since the server does not expand `~` --
        # made this half fire on a correct change.
        if _INSTALLED_RULESET_DIR in text.replace(BACKSLASH, "/"):
            documents_new = True
        for n, line in enumerate(text.splitlines(), 1):
            if _RULESET_IN_SKILLS_DIR.search(line.replace(BACKSLASH, "/")):
                out.append(
                    f"{rel}:{n}: documents a ruleset under the skills directory. "
                    f"Rulesets install under ~/.claude/{_INSTALLED_RULESET_DIR}/ "
                    f"because they have no SKILL.md. The path as written resolves "
                    f"to nothing on a clean install, and to STALE 1.4.1 rules on "
                    f"a machine that upgraded."
                )
    if not documents_new:
        out.append(
            f"no shipped file documents the installed ruleset path "
            f"(~/.claude/{_INSTALLED_RULESET_DIR}/). A customer who installs a "
            f"ruleset has no instruction for running it from disk. If rulesets "
            f"stopped being installable, remove this check in the same change "
            f"and say why."
        )
    return out


def is_blocking(finding: str) -> bool:
    """Whether a finding stops the release. Everything does but the line limit.

    Blocking is the default a new rule inherits, and the right one: a rule
    nobody has classified should hold the release, not slide past in a wall of
    warnings.
    """
    return "over the" not in finding


def main() -> int:
    # Findings quote source lines that may contain em-dashes and smart quotes.
    # A cp1252 console would raise UnicodeEncodeError mid-report and truncate it.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    import argparse
    parser = argparse.ArgumentParser(
        description="Release gate for the skills bundle.")
    parser.add_argument("path", nargs="?", default=None,
                        help="limit the scan to this path (default: the repo)")
    parser.add_argument("--server", metavar="PATH", default=None,
                        help="server.py to check operations against. Discovery "
                             "walks up from this repo and finds it in a normal "
                             "checkout and in a worktree; pass this when the "
                             "server lives somewhere else.")
    parser.add_argument("--strict", action="store_true",
                        help="fail when a check could not run. Use for releases. "
                             "CI leaves it off because the runner checks out only "
                             "this repository, so it has no server source and the "
                             "op-drift check cannot run there at all.")
    args = parser.parse_args()

    target = ROOT / args.path if args.path else ROOT
    if not target.exists():
        print(f"no such path: {target}")
        return 2

    findings: list[str] = []
    for f in iter_files(target):
        findings.extend(check_file(f))
    findings.extend(check_images(target))
    findings.extend(check_op_drift(target, Path(args.server) if args.server else None))
    findings.extend(check_ruleset_paths(target))
    if target == ROOT:
        findings.extend(check_manifest())
        findings.extend(check_stated_server_version())
        findings.extend(check_bundle_floor())
        findings.extend(check_plugin_package())

    # A check that did not run is not a check that passed. The verdict says so
    # whatever the findings, because the whole point of this item was a gate
    # reporting GREEN while one of its checks had been skipped.
    skipped = None if op_drift_ran() else op_drift_skip_reason()

    if not findings:
        if skipped is None:
            print("GATE GREEN — no violations")
            return 0
        print("GATE GREEN (1 check skipped) — no violations found, but "
              "op-drift did not run")
        print(f"  reason: {skipped}")
        if args.strict:
            print("  --strict: a skipped check fails the gate")
            return 1
        return 0

    blocking = [f for f in findings if is_blocking(f)]
    suffix = "" if skipped is None else ", 1 check skipped"
    print(f"GATE RED — {len(findings)} finding(s), {len(blocking)} blocking{suffix}\n")
    for f in findings:
        print(f"  {f}")
    if skipped is not None:
        print(f"\n  op-drift did not run: {skipped}")
    return 1 if (blocking or (args.strict and skipped is not None)) else 0


if __name__ == "__main__":
    sys.exit(main())
