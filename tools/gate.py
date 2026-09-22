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
