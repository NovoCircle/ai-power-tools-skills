"""APT-2026-0481: the gate fails a SKILL.md that breaks VS Code's Agent Skills rules.

VS Code silently skips a skill whose `name` differs from its directory, runs past
64 characters, or uses anything but lowercase letters, digits and hyphens, and one
whose `description` runs past 1024 characters. Each failing fixture below breaks
exactly one rule; the passing fixture breaks none.

Run:  python -m pytest tools/test_gate_skill_frontmatter.py
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

PINS = ("APT-2026-0481",)

_GATE_PATH = Path(__file__).resolve().parent / "gate.py"
_spec = importlib.util.spec_from_file_location("gate_frontmatter_under_test", _GATE_PATH)
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)


@pytest.fixture
def library(tmp_path, monkeypatch):
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    return tmp_path


def _skill(root: Path, directory: str, name: str, description: str = "Does a thing.") -> Path:
    p = root / "plugins" / "ai-power-tools" / "skills" / directory / "SKILL.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"---\nname: {name}\ndescription: {description}\n---\n\n# Skill\n")
    return p


def _findings(root: Path) -> str:
    return " | ".join(gate.check_skill_frontmatter(root))


def test_a_conforming_skill_passes(library):
    _skill(library, "ea-example", "ea-example", "x" * gate.SKILL_DESCRIPTION_MAX)
    assert gate.check_skill_frontmatter(library) == []


def test_a_name_of_exactly_64_characters_passes(library):
    name = "a" * gate.SKILL_NAME_MAX
    _skill(library, name, name)
    assert gate.check_skill_frontmatter(library) == []


def test_a_65_character_name_is_caught(library):
    name = "a" * (gate.SKILL_NAME_MAX + 1)
    _skill(library, name, name)
    assert "65 characters" in _findings(library)


def test_an_uppercase_name_is_caught(library):
    _skill(library, "Ea-Example", "Ea-Example")
    assert "lowercase letters, digits and hyphens" in _findings(library)


def test_a_name_that_differs_from_its_directory_is_caught(library):
    _skill(library, "ea-example", "ea-other")
    assert "differs from its directory" in _findings(library)


def test_a_1025_character_description_is_caught(library):
    _skill(library, "ea-example", "ea-example", "x" * (gate.SKILL_DESCRIPTION_MAX + 1))
    assert "description is 1025 characters" in _findings(library)


def test_a_folded_multi_line_description_is_measured_as_one_value(library):
    p = library / "plugins" / "ai-power-tools" / "skills" / "ea-example" / "SKILL.md"
    p.parent.mkdir(parents=True)
    body = "\n".join("  " + "y" * 100 for _ in range(11))
    p.write_text(f"---\nname: ea-example\ndescription: >\n{body}\n---\n", encoding="utf-8", newline="\n")
    assert "description is" in _findings(library)


def test_a_skill_with_no_frontmatter_is_caught(library):
    p = library / "s" / "SKILL.md"
    p.parent.mkdir(parents=True)
    p.write_text("# Skill\n", encoding="utf-8", newline="\n")
    assert "no YAML frontmatter" in _findings(library)


def test_a_violation_is_blocking(library):
    _skill(library, "ea-example", "ea-other")
    assert all(gate.is_blocking(f) for f in gate.check_skill_frontmatter(library))
