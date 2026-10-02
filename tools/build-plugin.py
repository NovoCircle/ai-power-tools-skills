#!/usr/bin/env python3
"""Package the plugin as `dist/ai-power-tools.plugin` for the Cowork channel.

Claude Code installs this plugin from the marketplace by cloning the repo, so it
needs nothing built. Cowork does not read that marketplace: the desktop app
enumerates Cowork's plugins itself from its own stores, one of which is fed by
an in-app upload that accepts a `.zip` or `.plugin` archive. This script builds
that archive.

A `.plugin` IS a zip -- the desktop normalises the extension before validating
it -- with the plugin's own contents at the archive root, so `.claude-plugin/`
sits at the top level.

The skill content is not copied or transformed: both channels ship the exact
bytes under `plugins/ai-power-tools/`, so there is one source of truth and no
way for the two to drift.
"""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "ai-power-tools"
MANIFEST = ROOT / "manifest.json"
DIST = ROOT / "dist"

#: The desktop upload rejects anything larger. Checked here so the failure
#: surfaces at build time rather than in front of a customer.
MAX_UPLOAD_BYTES = 209_715_200

_RESIDUE_DIRS = {"__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache"}
_RESIDUE_SUFFIXES = {".pyc", ".pyo"}


def _is_build_residue(p: Path) -> bool:
    return (any(part in _RESIDUE_DIRS for part in p.parts)
            or p.suffix in _RESIDUE_SUFFIXES)


def main() -> int:
    plugin_json = PLUGIN / ".claude-plugin" / "plugin.json"
    if not plugin_json.is_file():
        print(f"Missing {plugin_json}", file=sys.stderr)
        return 1

    # The two channels are versioned from different files, so they can drift.
    # A customer comparing them would see the same skills under two version
    # numbers, with no way to tell which is newer. Refuse instead.
    plugin_version = json.loads(plugin_json.read_text(encoding="utf-8"))["version"]
    bundle_version = json.loads(MANIFEST.read_text(encoding="utf-8"))["bundle_version"]
    if plugin_version != bundle_version:
        print(f"Version drift: plugin.json {plugin_version} != "
              f"manifest.json bundle_version {bundle_version}", file=sys.stderr)
        return 1

    marketplace = ROOT / ".claude-plugin" / "marketplace.json"
    entry = next((p for p in json.loads(marketplace.read_text(encoding="utf-8"))["plugins"]
                  if p["name"] == "ai-power-tools"), None)
    if entry is None or entry.get("version") != plugin_version:
        print(f"Version drift: marketplace.json entry != plugin.json "
              f"{plugin_version}", file=sys.stderr)
        return 1

    files = sorted(p for p in PLUGIN.rglob("*")
                   if p.is_file() and not _is_build_residue(p))
    if not files:
        print(f"No files under {PLUGIN}", file=sys.stderr)
        return 1

    DIST.mkdir(exist_ok=True)
    out = DIST / "ai-power-tools.plugin"
    # Fixed timestamps: the same input must produce the same archive, so a
    # rebuild that changed nothing is visibly identical.
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            info = zipfile.ZipInfo(str(f.relative_to(PLUGIN).as_posix()),
                                   date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, f.read_bytes())

    size = out.stat().st_size
    if size > MAX_UPLOAD_BYTES:
        print(f"{out.name} is {size} bytes — over the "
              f"{MAX_UPLOAD_BYTES}-byte desktop upload limit", file=sys.stderr)
        return 1

    print(f"{out.relative_to(ROOT)} — {len(files)} files, {size} bytes, "
          f"version {plugin_version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
