"""Where a manifest path's file actually lives in this repository.

Manifest paths are INSTALL-relative: the installer writes each one straight
under the skills directory, and publish-bundle derives the flat release-asset
name from the same string. Neither says anything about where the file sits in
the repo -- and since the skills moved under the plugin, the two differ.

Shared by regen-manifest.py, gate.py and publish-bundle.py. It lived in all
three as a private copy first, which is one update away from a release that
stages the wrong tree.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Skills live inside the plugin so a single tree serves both delivery
#: channels: the marketplace for Claude Code, and the packaged `.plugin` for
#: Cowork, which only loads skills from `<plugin>/skills/`.
PLUGIN_SKILLS = ROOT / "plugins" / "ai-power-tools" / "skills"

#: Data entries -- the rulesets -- deliberately stay at the repository root.
#: `ea-validation` pins a raw.githubusercontent URL into
#: `main/ruleset-archimate31/...`, so moving that directory would break every
#: already-installed copy of that skill the moment it merged.


def source_path(rel: str) -> Path:
    """Resolve an install-relative manifest path to its file in the repo."""
    candidate = PLUGIN_SKILLS / rel
    return candidate if candidate.exists() else ROOT / rel


def source_dir(name: str) -> Path | None:
    """Where a manifest entry's directory lives, or None if it is missing."""
    for base in (PLUGIN_SKILLS, ROOT):
        if (base / name).is_dir():
            return base / name
    return None


def asset_dirs() -> list[tuple[Path, Path]]:
    """(base, directory) pairs to scan for assets the manifest forgot.

    `base` is what a found file is made relative to, so the result can be
    compared against the manifest's install-relative paths.
    """
    pairs: list[tuple[Path, Path]] = []
    if PLUGIN_SKILLS.is_dir():
        pairs += [(PLUGIN_SKILLS, d) for d in sorted(PLUGIN_SKILLS.iterdir())
                  if d.is_dir() and not d.name.startswith((".", "_"))]
    pairs += [(ROOT, d) for d in sorted(ROOT.iterdir())
              if d.is_dir() and not d.name.startswith((".", "_"))
              and d.name not in {"tools", "plugins", "docs", "dist"}]
    return pairs
