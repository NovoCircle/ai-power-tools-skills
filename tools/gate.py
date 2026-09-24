#!/usr/bin/env python3
"""Release gate for the AI Power Tools Skills library.

Enforces the standing rule in C:\\SparxServices\\CLAUDE.md: no real customer
names, no absolute local paths, no personal identifiers in anything we ship.
Westbrook Bank is the only permitted example organization.

Usage:
    python tools/gate.py            # check the whole library
    python tools/gate.py ea-com     # check one skill

Exit code 0 = clean, 1 = violations found.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------
# Rule 1 — known real-customer identifiers. Denylist: catches what we know.
# --------------------------------------------------------------------------
# A path is fine when the user-specific segment is an obvious placeholder:
#   C:\Users\<you>\AppData\...   — the reader substitutes their own name.
# Only a *real* username or our own working tree is a violation.
PLACEHOLDER_PATH = re.compile(r"[A-Za-z]:\\{1,2}Users\\{1,2}[<%{$]")

FORBIDDEN = [
    (re.compile(r"\bTVO\b"), "real customer identifier 'TVO'"),
    (re.compile(r"\bTEA\b"), "real customer identifier 'TEA'"),
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
    # Sparx-shipped / standard technologies
    "ArchiMate", "ArchiMate2", "ArchiMate3", "BPMN", "BPMN2", "BPMN20",
    "UML", "SysML", "SysML15", "SysML16", "TOGAF", "DoDAF", "MODAF", "NIEM",
    "UPDM", "SPEM", "SOMF", "BPEL", "XSD", "WSDL", "ERD", "DMN", "CMMN",
    "MDG", "EA", "XMI", "SQL", "COM", "API", "XML", "YAML", "JSON", "HTML",
    "PNG", "SVG", "CSV", "UTF", "BOM", "URL", "ID", "OK", "NOT", "AND", "OR",
}
QEA_FILE = re.compile(r"\b([A-Za-z][A-Za-z0-9_-]*)\.(?:qea|eapx|eap|feap)\b")
MDG_NS = re.compile(r"\b([A-Z][A-Za-z0-9_]{1,30})::")

# --------------------------------------------------------------------------
# Rule 3 — encoding hygiene
# --------------------------------------------------------------------------
MOJIBAKE = re.compile(r"â€|Ã¢|â†|Â ")
FENCE = re.compile(r"^```")
CURLY = re.compile(r"[\u2018\u2019\u201c\u201d]")

MAX_SKILL_LINES = 400

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv"}
# tools/ holds this script, whose own patterns would trip it.
SKIP_FILES = {"gate.py"}


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
            if ident not in KNOWN_IDS and not ident.startswith("WBA"):
                out.append(f"{rel}:{n}: unrecognized MDG namespace '{ident}::' — "
                           f"if this is a real customer technology, convert it")

    if path.name == "SKILL.md" and len(lines) > MAX_SKILL_LINES:
        out.append(f"{rel}: {len(lines)} lines — over the {MAX_SKILL_LINES}-line limit; "
                   f"move detail into references/")

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
            f = ROOT / rel
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

    for skill_dir in sorted(p for p in ROOT.iterdir() if p.is_dir()):
        if skill_dir.name.startswith((".", "_")) or skill_dir.name == "tools":
            continue
        for f in skill_dir.rglob("*"):
            if f.is_file() and f.suffix.lower() in {".md", ".yaml", ".yml"}:
                rel = f.relative_to(ROOT).as_posix()
                if rel not in listed:
                    out.append(f"{rel}: present in the repo but not in manifest.json "
                               f"— it will not ship")
    return out


def check_op_drift(target: Path) -> list[str]:
    """Every operation a skill names must exist in the server's dispatch tables.

    This is the drift that is invisible until a customer hits it: a skill
    confidently instructs the model to call an operation that was renamed or
    never existed, and the failure surfaces as a confusing error on someone
    else's machine. The server has already shipped links to two skills that
    were never written; this is the same class in the other direction.

    Only explicit ``operation="name"`` call sites are checked. That is
    deliberately narrow — prose mentioning a name in backticks is not a call,
    and flagging it would train people to ignore the gate.

    Skipped silently when the server source is not available (for example on a
    machine that only has the skills repo checked out). A check that cannot
    run must not masquerade as a check that passed, so this prints a notice.
    """
    # Loaded by path: the filename contains a hyphen, so it is not importable
    # by name.
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "gen_operations", Path(__file__).resolve().parent / "gen-operations.py")
    if spec is None or spec.loader is None:
        print("  (op-drift check skipped: tools/gen-operations.py not found)")
        return []
    gen = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(gen)
    except Exception as e:
        print(f"  (op-drift check skipped: {e})")
        return []

    server = gen.DEFAULT_SERVER
    if not server.is_file():
        print(f"  (op-drift check skipped: server source not found at {server})")
        return []

    try:
        known: set[str] = set()
        for ops in gen.collect_operations(server).values():
            known.update(ops)
    except Exception as e:
        print(f"  (op-drift check skipped: {e})")
        return []

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


def main() -> int:
    # Findings quote source lines that may contain em-dashes and smart quotes.
    # A cp1252 console would raise UnicodeEncodeError mid-report and truncate it.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    target = ROOT / sys.argv[1] if len(sys.argv) > 1 else ROOT
    if not target.exists():
        print(f"no such path: {target}")
        return 2

    findings: list[str] = []
    for f in iter_files(target):
        findings.extend(check_file(f))
    findings.extend(check_op_drift(target))
    if target == ROOT:
        findings.extend(check_manifest())

    if not findings:
        print("GATE GREEN — no violations")
        return 0

    blocking = [f for f in findings if "over the" not in f]
    print(f"GATE RED — {len(findings)} finding(s), {len(blocking)} blocking\n")
    for f in findings:
        print(f"  {f}")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
