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


def _bare(root: Path, directory: str, frontmatter: str) -> None:
    p = root / "plugins" / "ai-power-tools" / "skills" / directory / "SKILL.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"---\n{frontmatter}---\n\n# Skill\n", encoding="utf-8", newline="\n")


def test_a_missing_description_is_caught_and_blocking(library):
    _bare(library, "ea-example", "name: ea-example\n")
    found = gate.check_skill_frontmatter(library)
    assert "no description" in " | ".join(found)
    assert all(gate.is_blocking(f) for f in found)


@pytest.mark.parametrize("directory,frontmatter", [
    ("ea-example", "description: x\n"),                                  # no name
    ("ea-example", "name: ea-other\ndescription: x\n"),                  # directory mismatch
    ("a" * 65, f"name: {'a' * 65}\ndescription: x\n"),                   # too long
    ("Ea-Example", "name: Ea-Example\ndescription: x\n"),                # characters
    ("ea-example", f"name: ea-example\ndescription: {'x' * 1025}\n"),    # description length
])
def test_every_new_finding_type_is_blocking(library, directory, frontmatter):
    _bare(library, directory, frontmatter)
    found = gate.check_skill_frontmatter(library)
    assert found and all(gate.is_blocking(f) for f in found)


def test_a_name_containing_over_the_fails_strict(library, monkeypatch):
    # The finding echoes the name; the old substring classifier read that as the
    # advisory line-limit message and let the build pass.
    _bare(library, "takes-over-the-world", "name: Takes over the world\ndescription: x\n")
    for check in ("check_op_drift", "check_images", "check_ruleset_paths", "check_manifest",
                  "check_stated_server_version", "check_bundle_floor", "check_plugin_package"):
        monkeypatch.setattr(gate, check, lambda *a, **k: [])
    monkeypatch.setattr(gate, "op_drift_ran", lambda: True)
    monkeypatch.setattr(gate.sys, "argv", ["gate.py", "--strict"])
    findings = gate.check_skill_frontmatter(library)
    assert any("over the" in f for f in findings)
    assert all(gate.is_blocking(f) for f in findings)
    assert gate.main() == 1
