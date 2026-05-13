"""Regenerate manifest.json with current file hashes.

Run after editing any SKILL.md / reference file. Reads the per-skill
metadata (description, version, min_server_version) from the existing
manifest.json and only refreshes the file list + sha256 map. If you
need to bump a skill's version or min_server_version, edit
manifest.json by hand first, then run this script — it will preserve
your edits.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "manifest.json"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    current = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for entry in current["skills"]:
        name = entry["name"]
        skill_dir = ROOT / name
        if not skill_dir.is_dir():
            print(f"Skill dir missing: {name}", file=sys.stderr)
            return 1
        files = sorted(str(p.relative_to(ROOT).as_posix())
                       for p in skill_dir.rglob("*") if p.is_file())
        if not files:
            print(f"No files under: {name}", file=sys.stderr)
            return 1
        entry["files"] = files
        entry["sha256"] = {f: sha256(ROOT / f) for f in files}

    MANIFEST.write_text(json.dumps(current, indent=2), encoding="utf-8")
    n_skills = len(current["skills"])
    n_files = sum(len(s["files"]) for s in current["skills"])
    print(f"manifest.json rewritten — {n_skills} skills, {n_files} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
