"""The test-suite conventions in TESTING.md, enforced.

Run:  python -m pytest tools/test_suite_conventions.py

Two rules, both cheap to break by accident and expensive to find later:

* Every test module declares ``PINS``, a tuple of the backlog ids it pins
  (``("APT-2026-0155",)``), or ``PINS = ()`` with a comment saying why. That makes
  ``grep -rn APT-2026-0155`` find the tests for an id even after a rename.
* Test module basenames are unique across the repository. pytest's default import
  mode puts each test file's directory on ``sys.path`` and imports it by basename,
  so two ``test_x.py`` files would collide.

This file is not shipped: it lives in ``tools/``, which ``manifest.json`` does not list.
"""
from __future__ import annotations

# Backlog items this module pins.
PINS = ("APT-2026-0488",)

import ast
import re
from collections import defaultdict
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

# Directories that hold copies or build output, never authored tests.
_SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "dist", ".release-staging",
              ".plugin-release-staging", ".venv", "node_modules"}

_ID = re.compile(r"APT-\d{4}-\d{4}")


def _test_modules() -> list[Path]:
    found = []
    for path in ROOT.rglob("test_*.py"):
        rel = path.relative_to(ROOT)
        if any(part in _SKIP_DIRS for part in rel.parts):
            continue
        found.append(path)
    return sorted(found)


_MODULES = _test_modules()


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _pins_of(path: Path):
    """The value assigned to module-level ``PINS``, or None when it is not assigned.

    Read from the syntax tree, not by importing: importing a test module runs its
    skip logic and its ``sys.path`` edits, and a module that fails to import would
    hide the very thing being checked.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "PINS" for t in node.targets):
            return node.value
    return None


def test_the_repository_has_test_modules_to_check():
    # A walk that finds nothing would make every check below pass vacuously.
    assert len(_MODULES) >= 28, [_rel(p) for p in _MODULES]


@pytest.mark.parametrize("path", _MODULES, ids=_rel)
def test_every_test_module_declares_pins(path):
    value = _pins_of(path)
    assert value is not None, (
        f"{_rel(path)} has no module-level PINS. Add PINS = (\"APT-2026-nnnn\", ...) for "
        "the backlog items it pins, or PINS = () with a comment saying why (see TESTING.md)")
    assert isinstance(value, ast.Tuple), (
        f"{_rel(path)}: PINS must be a tuple literal, for example PINS = (\"APT-2026-0155\",)")
    for element in value.elts:
        assert isinstance(element, ast.Constant) and isinstance(element.value, str), (
            f"{_rel(path)}: every PINS entry must be a string literal")
        assert _ID.fullmatch(element.value), (
            f"{_rel(path)}: {element.value!r} is not a backlog id of the form APT-2026-nnnn")


def test_test_module_basenames_are_unique():
    by_name = defaultdict(list)
    for path in _MODULES:
        by_name[path.name].append(_rel(path))
    clashes = {name: where for name, where in by_name.items() if len(where) > 1}
    assert not clashes, f"test module basenames must be unique across the repository: {clashes}"
