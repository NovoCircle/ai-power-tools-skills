"""Tests for capture_overlap.py. Run: python -m pytest security/checks"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import capture_overlap as co  # noqa: E402


def _tree(root: Path, files: dict) -> Path:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def _setup(tmp_path, capture, skill, other="", known=""):
    captures = _tree(tmp_path / "captures", {"walk.md": capture})
    skills = _tree(tmp_path / "skills", {"prol-x/SKILL.md": skill,
                                         "ea-y/SKILL.md": other})
    docs = _tree(tmp_path / "docs", {"api.md": known})
    return captures, skills, docs


def test_a_shared_string_is_listed_with_where_it_was_found(tmp_path):
    captures, skills, docs = _setup(
        tmp_path, 'profile "Quillmoor Ledger Map" opened', "Open Quillmoor Ledger Map.")
    hits = co.compare([captures], skills, "prol-*", [docs])
    assert hits == [("quillmoor ledger map", "walk.md", ["prol-x/SKILL.md"])]


def test_case_and_punctuation_do_not_hide_a_match(tmp_path):
    captures, skills, docs = _setup(
        tmp_path, "`quillmoor-ledger_map`", "The QUILLMOOR LEDGER MAP profile.")
    assert [h[0] for h in co.compare([captures], skills, "prol-*", [docs])] == [
        "quillmoor ledger map"]


def test_double_percent_encoding_in_a_url_does_not_hide_a_match(tmp_path):
    captures, skills, docs = _setup(
        tmp_path, "https://host.example/Matrix/View/Quillmoor%2520Ledger%2520Map/0",
        "See Quillmoor Ledger Map.")
    assert "quillmoor ledger map" in [
        h[0] for h in co.compare([captures], skills, "prol-*", [docs])]


def test_vocabulary_in_other_skills_or_known_docs_is_not_listed(tmp_path):
    captures, skills, docs = _setup(
        tmp_path, '"GetAllMatrixProfiles" and "Relationship Matrix"',
        "Call GetAllMatrixProfiles on the Relationship Matrix.",
        other="A Relationship Matrix compares two sets.",
        known="GetAllMatrixProfiles returns every profile.")
    assert co.compare([captures], skills, "prol-*", [docs]) == []


def test_numbers_and_short_strings_are_not_candidates(tmp_path):
    captures, skills, docs = _setup(
        tmp_path, '"2025" "abc" "1 16 2025"', "2025 abc 1/16/2025")
    assert co.compare([captures], skills, "prol-*", [docs]) == []


def test_the_output_carries_the_provenance_warning(tmp_path, capsys):
    captures, skills, docs = _setup(tmp_path, '"Quillmoor Ledger Map"',
                                    "Quillmoor Ledger Map")
    assert co.main(["--captures", str(captures), "--scope", "prol-*",
                    "--skills", str(skills), "--known", str(docs)]) == 0
    out = capsys.readouterr().out
    assert "co-occurrence only" in out
    assert out.index("WHAT A HIT MEANS") < out.index("quillmoor ledger map")
