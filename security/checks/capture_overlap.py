#!/usr/bin/env python3
"""Customer content that may have travelled from research captures into skills.

Skills written by driving a customer system are authored from raw captures.
The captures hold real identifiers; the skills must not. `tools/gate.py`
cannot police that boundary: it knows a fixed list of names and cannot
recognize an unknown customer's vocabulary. This check lists the strings the
captures and the skills share, for a person to judge (APT-2026-0237).

Both sides are normalized before comparing -- URL-decoded twice, HTML
unescaped, case-folded, non-alphanumerics collapsed -- because each of those
hid a real instance from an earlier, literal sweep. Candidates come from every
identifier-bearing position in the captures: quoted literals, backticks, and
URL path and query segments. A candidate is listed only when it appears in the
skills under review and nowhere in the vocabulary: the rest of the shipped
skills, plus any product documentation passed with --known. That filter is
what turns thousands of shared product and API terms into a reviewable list.

This is not a pass/fail check, and it exits 0 whatever it finds. A hit proves
co-occurrence, not direction of travel; the output says so, every time.

Usage:
    python security/checks/capture_overlap.py --captures <research-dir> \\
        --scope "prol-*" [--known <vendor-docs-dir>] [--skills <skills-dir>]

--captures and --known may be given more than once.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SKILLS = ROOT / "plugins" / "ai-power-tools" / "skills"

#: Read before the list, every run, so whoever reads a hit is told what it does
#: and does not prove.
PROVENANCE = """\
WHAT A HIT MEANS
  Each line below is a string found both in a research capture and in a skill
  under review, and nowhere in the vocabulary. That proves co-occurrence only,
  not which way the string travelled. A capture can already hold the synthetic
  replacement its author put there, and research captures are not under version
  control, so their earlier state cannot be checked.
  Treat each hit as a question to answer, not a finding: product term, our own
  example (Westbrook Bank), or customer content that must be replaced. Do not
  gate a release on a hit until its provenance is settled.
"""

_TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".html", ".htm",
                  ".js", ".ts", ".py", ".sql", ".xml", ".csv", ".har", ".log"}
_MAX_FILE_BYTES = 20 * 1024 * 1024
_MIN_LENGTH = 4

_CANDIDATE = re.compile(
    r'"([^"\n]{3,120})"'
    r"|'([^'\n]{3,120})'"
    r"|`([^`\n]{3,120})`"
    r'|(https?://[^\s)>\]"\'`]+)')
_URL_PARTS = re.compile(r"[/?&=#]")
_NOT_ALNUM = re.compile(r"[^0-9a-z]+")


def normalize(text: str) -> str:
    text = html.unescape(unquote(unquote(text))).casefold()
    return _NOT_ALNUM.sub(" ", text).strip()


def _text_files(directory: Path):
    for path in sorted(directory.rglob("*")):
        if (path.is_file() and path.suffix.lower() in _TEXT_SUFFIXES
                and path.stat().st_size <= _MAX_FILE_BYTES):
            yield path


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def candidates(directories) -> dict:
    """Normalized candidate -> the first capture file it came from."""
    found: dict = {}
    for directory in directories:
        for path in _text_files(directory):
            for match in _CANDIDATE.finditer(_read(path)):
                raw = next(g for g in match.groups() if g)
                pieces = [raw]
                if raw.startswith(("http://", "https://")):
                    pieces += _URL_PARTS.split(raw)
                for piece in pieces:
                    key = normalize(piece)
                    if len(key) >= _MIN_LENGTH and not key.replace(" ", "").isdigit():
                        found.setdefault(key, path.relative_to(directory).as_posix())
    return found


def _padded(paths) -> str:
    return " " + " ".join(normalize(_read(p)) for p in paths) + " "


def compare(captures, skills_dir: Path, scope: str, known) -> list:
    """Hits as (candidate, capture file, [skill files]), sorted."""
    in_scope = [p for d in sorted(skills_dir.glob(scope)) if d.is_dir()
                for p in _text_files(d)]
    if not in_scope:
        raise SystemExit(f"no skill matches --scope {scope!r} under {skills_dir}")
    scoped = {p: f" {normalize(_read(p))} " for p in in_scope}
    rest = [p for p in _text_files(skills_dir) if p not in scoped]
    vocabulary = _padded(rest) + _padded(p for d in known for p in _text_files(d))

    hits = []
    for key, source in candidates(captures).items():
        padded = f" {key} "
        if padded in vocabulary:
            continue
        where = [p.relative_to(skills_dir).as_posix()
                 for p, text in scoped.items() if padded in text]
        if where:
            hits.append((key, source, where))
    return sorted(hits)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--captures", action="append", required=True, type=Path,
                        help="a research capture directory (repeatable)")
    parser.add_argument("--scope", required=True,
                        help='skill directories under review, a glob such as "prol-*"')
    parser.add_argument("--known", action="append", default=[], type=Path,
                        help="product documentation to treat as vocabulary (repeatable)")
    parser.add_argument("--skills", type=Path, default=DEFAULT_SKILLS,
                        help="the shipped skills directory (default: this repo's)")
    args = parser.parse_args(argv)
    for directory in [*args.captures, *args.known, args.skills]:
        if not directory.is_dir():
            parser.error(f"not a directory: {directory}")

    hits = compare(args.captures, args.skills, args.scope, args.known)
    out = sys.stdout
    if hasattr(out, "reconfigure"):             # a Windows console is cp1252
        out.reconfigure(encoding="utf-8", errors="replace")
    out.write(PROVENANCE + "\n")
    out.write(f"{len(hits)} candidate(s) in {args.scope}\n\n")
    for key, source, where in hits:
        out.write(f"{key!r}\n    capture: {source}\n    skills:  {', '.join(where)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
