"""Tests of the files that carry the sysml-1 language: its guide on the language shelf, its EA files, and its ruleset.

Hermetic: reads files only, starts no Enterprise Architect and no server. What it holds to:

* the id is the same in the six places the packaging design names (shelf folder, `SKILL.md` name, `language.yaml` id,
  `ea.yaml` language, ruleset `meta.language`, ruleset file name);
* the guide names no tool, no internal file, no local path, no customer, and uses no em dash;
* every `implements` in the ruleset resolves to a rule id in the guide, and that id is in `references/rules.md`;
* every concept in the guide takes an element type, is left as the default rectangle, or has a stated reason, and every
  shape the guide names that is not a rectangle is written down in `layout`.

Run:  python -m pytest tools/test_lang_sysml_1.py
"""
from __future__ import annotations

# The backlog item that asks for this language's entry.
PINS = ("APT-2026-0394",)

import re
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

from gate import FORBIDDEN

LANG = "sysml-1"
ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"
SHELF = PLUGINS / "ai-power-tools-languages" / "skills" / LANG
SHARED = PLUGINS / "ai-power-tools" / "skills" / "_shared" / "languages" / LANG
RULESET = PLUGINS / "ai-power-tools" / "rulesets" / LANG / f"{LANG}_rules.yaml"

ELEMENT_TYPES = {"box", "large-box", "event-circle", "small-node", "decision-diamond", "data-item", "actor",
                 "attached-item", "note", "container", "line-label"}
SHIPPED = [p for base in (SHELF, SHARED, RULESET.parent) for p in sorted(base.rglob("*")) if p.is_file()]
SHELF_FILES = [p for p in SHIPPED if SHELF in p.parents]

TOOL_WORDS = re.compile(r"\b(sparx|MDG|toolbox|quick ?linker|t_object|t_connector|\.qea|visio|archi tool|camunda|cameo|"
                        r"magicdraw|signavio|bizagi|lucidchart|draw\.io)\b|\bEA\b", re.I)
INTERNAL = re.compile(r"research[/\\]|ea-samples-run|skill-draft|ruleset-draft|ea-reference|STANDARD-NOTES|OPEN-POINTS|"
                      r"open points?\b|\bAP[TV]-\d{4}-\d+|ea-catalog|EA-RESOURCES|language-library")
DASH = re.compile("[" + chr(0x2014) + chr(0x2013) + "]")


def _load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


GUIDE = _load(SHELF / "language.yaml")
EA = _load(SHARED / "ea.yaml")
RULES = _load(RULESET)


def test_the_files_exist_where_the_packaging_design_puts_them():
    for path in (SHELF / "SKILL.md", SHELF / "language.yaml", SHELF / "references" / "standard.md",
                 SHELF / "references" / "rules.md", SHARED / "ea.yaml", SHARED / "howto.md", RULESET):
        assert path.is_file(), path


def test_the_id_is_the_same_in_every_place():
    skill = (SHELF / "SKILL.md").read_text(encoding="utf-8")
    assert re.search(rf"^name: {re.escape(LANG)}$", skill, re.M)
    assert GUIDE["id"] == LANG
    assert EA["language"] == LANG
    assert RULES["meta"]["language"] == LANG
    assert RULESET.name == f"{LANG}_rules.yaml"


def test_the_skill_description_fits_the_limit():
    skill = (SHELF / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r"^description:\s*(.*?)(?=^\w[\w-]*:|^---)", skill, re.S | re.M)
    assert m and 0 < len(m.group(1).strip()) <= 1024


def test_the_skill_points_at_the_layout_standard():
    skill = (SHELF / "SKILL.md").read_text(encoding="utf-8")
    section = skill.split("## How it is drawn", 1)[1]
    assert "../_languages/layout-standard.yaml" in section.split("\n## ", 1)[0]


@pytest.mark.parametrize("path", SHELF_FILES, ids=lambda p: p.relative_to(SHELF).as_posix())
def test_the_shelf_names_no_tool(path):
    hits = {m.group(0) for m in TOOL_WORDS.finditer(path.read_text(encoding="utf-8"))}
    assert not hits, hits


@pytest.mark.parametrize("path", SHIPPED, ids=lambda p: p.relative_to(PLUGINS).as_posix())
def test_nothing_shipped_points_at_a_private_file_or_names_a_customer(path):
    text = path.read_text(encoding="utf-8")
    assert not INTERNAL.search(text), INTERNAL.search(text).group(0)
    for pattern, why in FORBIDDEN:
        assert not pattern.search(text), why
    assert not DASH.search(text), "dash"
    assert "\r" not in text and not text.startswith("\ufeff")


def _rule_ids():
    return {c["id"] for c in GUIDE["constraints"]}


def test_every_rule_implements_a_rule_of_the_guide():
    ids = _rule_ids()
    rules_md = (SHELF / "references" / "rules.md").read_text(encoding="utf-8")
    seen = []
    for rule in RULES["rules"]:
        implemented = []
        for key in ("implements", "also_implements"):
            value = rule.get(key)
            implemented += value if isinstance(value, list) else ([value] if value else [])
        assert implemented, rule["id"]
        seen += implemented
    assert not [i for i in seen if i not in ids]
    assert not [i for i in seen if i not in rules_md]


def _concepts():
    return GUIDE["concepts"]["elements"]


def _relationship_names():
    block = GUIDE.get("relationships") or {}
    out = set()
    for key in ("items", "types"):
        if isinstance(block.get(key), list):
            out |= {x["name"] for x in block[key] if isinstance(x, dict) and x.get("name")}
    return out


def test_the_layout_block_has_the_parts_the_design_names():
    layout = GUIDE["layout"]
    assert layout["basis"].startswith("Our conventions")
    assert layout["exceptions"] == {} or all(e.get("reason") and e.get("source") for e in layout["exceptions"].values())
    assert set(layout["element_types"].values()) <= ELEMENT_TYPES


def test_every_concept_and_relationship_has_an_element_type_or_a_stated_reason():
    layout = GUIDE["layout"]
    typed = set(layout["element_types"])
    none = {}
    for key, entry in layout["no_element_type"].items():
        assert entry["reason"], key
        for name in entry["concepts"]:
            none[name] = key
    names = set(_concepts())
    assert typed <= names, sorted(typed - names)
    assert set(none) <= names | _relationship_names(), sorted(set(none) - names - _relationship_names())
    assert not typed & set(none), sorted(typed & set(none))
    # A concept in neither list is drawn as a rectangle: that is the default, and the next test checks that it is true.
    assert _relationship_names() - names <= set(none), sorted(_relationship_names() - names - set(none))


# Words that say a shape is something other than a rectangle.
NOT_A_RECTANGLE = re.compile(r"\b(ellipse|oval|circle|diamond|hexagon|triangle|pentagon|arrow|cylinder|house|chevron|cloud|"
                             r"parallelogram|stick figure|folder|note symbol|small square|small hollow)\b")


def _leading_phrase(text: str) -> str:
    return re.split(r"[;:,.]| with | holding | above | beside | inside | where | and | or ", text.lower(), maxsplit=1)[0]


def test_every_shape_that_is_not_a_rectangle_is_written_down():
    layout = GUIDE["layout"]
    written = set(layout["element_types"])
    for entry in layout["no_element_type"].values():
        written |= set(entry["concepts"])
    notation = (GUIDE.get("notation") or {}).get("elements") or {}
    missing = []
    for name, entry in notation.items():
        shape = entry.get("shape") if isinstance(entry, dict) else None
        if name in _concepts() and shape and NOT_A_RECTANGLE.search(_leading_phrase(shape)) and name not in written:
            missing.append(name)
    assert not missing, missing
    # A language whose concepts are drawn as the UML element they extend writes down every base that is not a box.
    not_box = {"Comment": "note", "Constraint": "note", "Package": "container", "Interaction": "container",
               "Port": "attached-item"}
    wrong = []
    for name, concept in _concepts().items():
        base = str(concept.get("uml_base"))
        if base in not_box and not concept.get("abstract") and layout["element_types"].get(name) != not_box[base]:
            wrong.append((name, base))
    assert not wrong, wrong
