#!/usr/bin/env python3
"""Encoding normalizer for the AI Power Tools Skills library.

Fixes the three encoding defects tools/gate.py checks for:

  1. A leading UTF-8 BOM.
  2. Mojibake — text that was valid UTF-8, decoded as cp1252, then
     re-encoded as UTF-8 (so a single em dash reads back as three garbage
     Latin-1/punctuation characters). Repaired with the standard round
     trip, `s.encode('cp1252').decode('utf-8')`, applied only to spans
     that could plausibly BE such an artifact, and only kept when the
     round trip succeeds and actually changes the text.
  3. Curly quotes/apostrophes used inside fenced (```) code blocks, where
     they break copy/paste. Prose curly quotes outside fences are left
     alone — they're legitimate typography, and the gate does not flag
     them.

It also normalizes line endings to LF and drops a leading UTF-8 BOM, per
the "always UTF-8 without BOM, LF only" shipping rule for this repo.

Usage:
    python tools/normalize.py [paths...]

With no paths, the whole repository is scanned (the same file types
tools/gate.py checks: .md .yaml .yml .json .py .txt). A path may be a
file or a directory.

Dry run is the default and is the ONLY thing this script can do unless
you pass --apply:

    python tools/normalize.py                  # report only, writes nothing
    python tools/normalize.py --apply           # writes fixed files
    python tools/normalize.py path/to/one.md    # scope to one file/dir

Output streams (so a dry run can be captured as two clean artifacts):
    stdout  -- a unified diff of every change this run would make (or did
               make, with --apply). Empty if nothing changes.
    stderr  -- a human-readable per-file summary of fix counts, plus a
               final total line.

    python tools/normalize.py > dryrun.diff 2> summary.txt
"""
from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------
# File selection — mirrors tools/gate.py's iter_files() so "the whole repo"
# means the same thing to both tools.
# --------------------------------------------------------------------------
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv"}
SKIP_FILES = {"gate.py"}
CHECKED_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".py", ".txt"}


def iter_files(target: Path):
    if target.is_file():
        yield target
        return
    for p in sorted(target.rglob("*")):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.name in SKIP_FILES:
            continue
        if p.suffix.lower() in CHECKED_SUFFIXES:
            yield p


# --------------------------------------------------------------------------
# Mojibake repair
# --------------------------------------------------------------------------
# Every character that decoding a single byte 0x80-0xFF as cp1252 can
# produce. cp1252 leaves 5 byte values undefined (0x81, 0x8D, 0x8F, 0x90,
# 0x9D); those can never appear as a "decoded as cp1252" character, so they
# are excluded here too.
_UNDEFINED_CP1252_BYTES = {0x81, 0x8D, 0x8F, 0x90, 0x9D}
CP1252_ARTIFACT_CHARS = frozenset(
    bytes([b]).decode("cp1252")
    for b in range(0x80, 0x100)
    if b not in _UNDEFINED_CP1252_BYTES
)
# This set covers both halves of the pattern: the Latin-1-range characters
# (U+00A0-U+00FF, e.g. "â", "Â", "Ã" — what a UTF-8 lead/continuation byte
# 0xA0-0xFF looks like under cp1252) AND the punctuation-block characters
# that bytes 0x80-0x9F decode to under cp1252 (e.g. "€", "œ", the curly
# quotes, en/em dash). A genuine mojibake artifact always uses characters
# from *only* this set, because every byte in it came from misreading a
# UTF-8 byte as cp1252 in the first place. A character from outside this
# set (plain ASCII, or any already-correct Unicode character above U+00FF
# that isn't one of these specific punctuation marks) can never be part of
# one, so scanning for maximal runs of these characters can't wander into
# unrelated, correct text.


def _repair_run(run: str) -> str:
    """Repair one maximal run of cp1252-artifact characters.

    Applies the round trip repeatedly (bounded) so a run that was
    corrupted more than once collapses back to the original in a single
    pass of this script — which is what makes the overall transform
    idempotent: a second run has nothing left to fix, because there is
    nothing left that both survives the round trip AND changes.
    """
    seen = {run}
    current = run
    for _ in range(6):  # generous headroom; real corruption here is 1-2 layers
        try:
            nxt = current.encode("cp1252").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
        if nxt == current or nxt in seen:
            break
        current = nxt
        seen.add(current)
    return current


def repair_mojibake_line(line: str) -> tuple[str, int]:
    """Repair mojibake runs in a single line. Returns (new_line, n_runs_fixed)."""
    out: list[str] = []
    fixed = 0
    i, n = 0, len(line)
    while i < n:
        c = line[i]
        if c in CP1252_ARTIFACT_CHARS:
            j = i + 1
            while j < n and line[j] in CP1252_ARTIFACT_CHARS:
                j += 1
            run = line[i:j]
            repaired = _repair_run(run)
            if repaired != run:
                fixed += 1
            out.append(repaired)
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out), fixed


# --------------------------------------------------------------------------
# Curly quotes inside fenced code blocks
# --------------------------------------------------------------------------
# Matches tools/gate.py's own fence toggle exactly: any stripped line that
# starts with ``` flips fence state, whatever follows (a language tag, more
# backticks, indentation before it — gate.py strips the line before
# matching, so this does too, which is what keeps fences nested under list
# items in scope).
def is_fence_marker(line: str) -> bool:
    return line.strip().startswith("```")


CURLY_MAP = {
    "\u2018": "'",  # left single quote
    "\u2019": "'",  # right single quote / apostrophe
    "\u201c": '"',  # left double quote
    "\u201d": '"',  # right double quote
}


def straighten_curly_line(line: str) -> tuple[str, int]:
    count = 0
    out = []
    for c in line:
        if c in CURLY_MAP:
            out.append(CURLY_MAP[c])
            count += 1
        else:
            out.append(c)
    return "".join(out), count


# --------------------------------------------------------------------------
# Per-file processing
# --------------------------------------------------------------------------
class FileResult:
    def __init__(self, path: Path):
        self.path = path
        self.bom_stripped = 0
        self.crlf_normalized = 0
        self.mojibake_runs = 0
        self.curly_straightened = 0
        self.original_text: str | None = None
        self.new_text: str | None = None
        self.skipped_reason: str | None = None

    @property
    def changed(self) -> bool:
        return self.original_text is not None and self.new_text != self.original_text

    def summary_line(self) -> str:
        rel = self.path.relative_to(ROOT) if self.path.is_relative_to(ROOT) else self.path
        if self.skipped_reason:
            return f"{rel}: SKIPPED — {self.skipped_reason}"
        return (
            f"{rel}: bom_stripped={self.bom_stripped} "
            f"mojibake_runs_repaired={self.mojibake_runs} "
            f"curly_quotes_straightened={self.curly_straightened} "
            f"crlf_lines_normalized={self.crlf_normalized}"
        )


def process_file(path: Path) -> FileResult:
    res = FileResult(path)
    try:
        raw = path.read_bytes()
    except OSError as exc:
        res.skipped_reason = f"could not read ({exc})"
        return res

    if raw.startswith(b"\xef\xbb\xbf"):
        res.bom_stripped = 1
        raw = raw[3:]

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        res.skipped_reason = f"not valid UTF-8 after BOM strip ({exc})"
        return res

    # original_text is the file's logical content with any BOM already
    # conceptually removed (a stripped BOM always counts as a change).
    res.original_text = text

    raw_lines = text.split("\n")
    # Track and normalize CRLF -> LF without losing "did this file have
    # CRLF at all" as a reportable fact.
    normalized_lines = []
    for rl in raw_lines:
        if rl.endswith("\r"):
            res.crlf_normalized += 1
            normalized_lines.append(rl[:-1])
        else:
            normalized_lines.append(rl)

    in_fence = False
    out_lines: list[str] = []
    for line in normalized_lines:
        fixed_line, n_fixed = repair_mojibake_line(line)
        res.mojibake_runs += n_fixed

        if is_fence_marker(fixed_line):
            in_fence = not in_fence
            out_lines.append(fixed_line)
            continue

        if in_fence:
            fixed_line, n_curly = straighten_curly_line(fixed_line)
            res.curly_straightened += n_curly

        out_lines.append(fixed_line)

    res.new_text = "\n".join(out_lines)
    return res


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def make_diff(res: FileResult) -> str:
    rel = res.path.relative_to(ROOT) if res.path.is_relative_to(ROOT) else res.path
    rel_posix = rel.as_posix() if hasattr(rel, "as_posix") else str(rel)
    a_lines = [l + "\n" for l in res.original_text.split("\n")]
    b_lines = [l + "\n" for l in res.new_text.split("\n")]
    diff = difflib.unified_diff(
        a_lines,
        b_lines,
        fromfile=f"a/{rel_posix}",
        tofile=f"b/{rel_posix}",
        lineterm="\n",
    )
    return "".join(diff)


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
        sys.stderr.reconfigure(encoding="utf-8", newline="\n")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="*", help="files or directories to check (default: whole repo)")
    parser.add_argument("--apply", action="store_true", help="write fixes to disk (default: dry run, writes nothing)")
    args = parser.parse_args()

    targets = [Path(p).resolve() for p in args.paths] if args.paths else [ROOT]

    files: list[Path] = []
    for t in targets:
        if not t.exists():
            print(f"no such path: {t}", file=sys.stderr)
            return 2
        files.extend(iter_files(t))

    total_bom = total_moji = total_curly = total_crlf = 0
    changed_files = 0
    skipped = 0

    for path in files:
        res = process_file(path)
        if res.skipped_reason:
            skipped += 1
            print(res.summary_line(), file=sys.stderr)
            continue
        if not res.changed:
            continue

        changed_files += 1
        total_bom += res.bom_stripped
        total_moji += res.mojibake_runs
        total_curly += res.curly_straightened
        total_crlf += res.crlf_normalized

        print(res.summary_line(), file=sys.stderr)

        diff_text = make_diff(res)
        if diff_text:
            sys.stdout.write(diff_text)

        if args.apply:
            path.write_bytes(res.new_text.encode("utf-8"))

    mode = "APPLIED" if args.apply else "DRY RUN"
    print(
        f"\n{mode}: {changed_files} file(s) changed "
        f"(bom={total_bom} mojibake_runs={total_moji} "
        f"curly_quotes={total_curly} crlf_lines={total_crlf}), "
        f"{skipped} file(s) skipped",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
