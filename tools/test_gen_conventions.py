"""The layout standard, its EA translation, and the generated files.

Run:  python -m pytest tools/test_gen_conventions.py

Hermetic. What it holds: the generated `conventions.yaml` files are exactly what the sources
call for, every value in them is the standard's value times the unit rule, nothing the standard
states lacks a home, and each check fails on a planted error.
"""
from __future__ import annotations

# Backlog items this module pins.
PINS = ("APT-2026-0472",)

# The data assets this module covers (read by tools/register.py).
COVERS = ("asset:plugins/ai-power-tools/skills/_shared/languages/*",)

import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml", reason="PyYAML is required to read the layout standard")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import gen_conventions as gen  # noqa: E402

COMPOSE_TOOLS = ROOT / "plugins/ai-power-tools/skills/ea-diagram-composition/tools"
ADVISOR_TOOLS = ROOT / "plugins/ai-power-tools/skills/ea-diagram-advisor/tools"
for _path in (COMPOSE_TOOLS, ADVISOR_TOOLS):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))
import bindings  # noqa: E402
import compose  # noqa: E402
import compose_chevron  # noqa: E402
import compose_matrix  # noqa: E402
import lint  # noqa: E402

GENERATED = sorted((ROOT / gen.EA_REL).glob(f"*/{gen.GENERATED_NAME}"))
FIXTURE = json.loads((ROOT / "tools/fixtures/convention-grammars.json").read_text(encoding="utf-8"))
RECORDED = {f"{r['technology']}::{r['diagram_type']}": r["grammar"] for r in FIXTURE["rows"]}
NINE = ("archimate-3", "bpmn-2", "data-modeling-er", "dmn-1", "sysml-1", "togaf-9", "uaf-1",
        "uml-2", "zachman")
TWO_MAPS = ("sparx-mind-mapping", "sparx-strategy-map")


def _standard() -> dict:
    return yaml.safe_load((ROOT / gen.STANDARD_REL).read_text(encoding="utf-8"))


def _translation() -> dict:
    return yaml.safe_load((ROOT / gen.TRANSLATION_REL).read_text(encoding="utf-8"))


def _doc(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.fixture
def tree(tmp_path) -> Path:
    """A copy of just the sources and generated files, to plant errors in."""
    for rel in (gen.SHELF_REL, gen.EA_REL):
        shutil.copytree(ROOT / rel, tmp_path / rel,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return tmp_path


def _edit(path: Path, change) -> None:
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    change(doc)
    path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")


# ---------------------------------------------------------------------------
# The adopted values (A42, A43). A change here is Ryan's decision, not a side effect.
# ---------------------------------------------------------------------------
def test_the_standard_holds_the_adopted_sizes():
    types = _standard()["element_types"]
    sizes = {name: (row.get("w"), row["h"]) for name, row in types.items()}
    assert sizes == {
        "box": (100, 70), "large-box": (130, 80), "event-circle": (30, 30),
        "small-node": (20, 20), "decision-diamond": (40, 40), "data-item": (40, 50),
        "actor": (45, 90), "attached-item": (15, 15), "note": (120, 60),
        "container": (150, 90), "line-label": (None, 15),
    }
    assert types["container"]["inner_padding"] == 12
    assert types["container"]["label_strip"] == 28
    assert types["line-label"]["clear_of_line"] == 10


def test_the_standard_holds_the_adopted_spacing():
    spacing = {name: row["value"] for name, row in _standard()["spacing"].items()}
    assert spacing == {"across": 80, "down": 50, "along_flow": 60, "between_lanes": 0,
                       "lane_thickness": 120, "between_bands": 30, "page_margin": 40}


def test_the_unit_is_a_ninety_sixth_of_an_inch():
    standard = _standard()
    assert standard["unit"]["per_inch"] == 96
    assert _translation()["unit"]["ea_units_per_standard_unit"] == 1


def test_every_row_states_its_reason():
    standard = _standard()
    for block in ("element_types", "spacing"):
        for name, row in standard[block].items():
            assert str(row.get("reason", "")).strip(), f"{block}.{name}"


def test_the_shelf_files_name_no_tool():
    """The shelf holds the standard and the language stubs, and neither names a tool."""
    words = re.compile(r"\b(sparx|MDG|toolbox|quick ?linker|t_object|t_connector|\.qea|visio|archi tool|"
                       r"camunda|cameo|magicdraw|signavio|bizagi|lucidchart|draw\.io)\b", re.I)
    files = [ROOT / gen.STANDARD_REL, *sorted((ROOT / gen.SHELF_REL).glob("*/language.yaml"))]
    assert len(files) >= 1 + len(NINE)
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert not words.search(text), path
        assert not re.search(r"\bEA\b", text), path


def test_nothing_shipped_here_holds_an_em_dash():
    files = [ROOT / gen.STANDARD_REL, ROOT / gen.TRANSLATION_REL, *GENERATED,
             *sorted((ROOT / gen.SHELF_REL).glob("*/language.yaml")),
             *sorted((ROOT / gen.EA_REL).glob("*/ea.yaml"))]
    for path in files:
        assert "—" not in path.read_text(encoding="utf-8"), path


# ---------------------------------------------------------------------------
# The drift check
# ---------------------------------------------------------------------------
def test_there_is_one_generated_file_per_map():
    assert {p.parent.name for p in GENERATED} >= set(NINE) | set(TWO_MAPS)


def test_the_generated_files_match_their_sources():
    assert gen.stale_files(ROOT) == [], "run python tools/gen_conventions.py and commit the result"


def test_a_hand_edit_to_a_generated_file_is_caught(tree):
    path = tree / gen.EA_REL / "bpmn-2" / gen.GENERATED_NAME
    path.write_text(path.read_text(encoding="utf-8").replace("w: 100", "w: 101", 1), encoding="utf-8")
    assert gen.stale_files(tree) == [path.relative_to(tree).as_posix()]


def test_a_changed_standard_makes_every_file_stale(tree):
    _edit(tree / gen.STANDARD_REL, lambda d: d["spacing"]["across"].update(value=90))
    assert len(gen.stale_files(tree)) == len(GENERATED)


def test_a_generated_file_with_no_source_is_caught(tree):
    orphan = tree / gen.EA_REL / "not-a-language" / gen.GENERATED_NAME
    orphan.parent.mkdir()
    orphan.write_text("technology: Orphan\n", encoding="utf-8")
    assert orphan.relative_to(tree).as_posix() in gen.stale_files(tree)


def test_the_command_line_check_passes_here_and_fails_on_drift(tree):
    script = ROOT / "tools" / "gen_conventions.py"
    run = lambda: subprocess.run([sys.executable, str(script), "--check", "--root", str(tree)],
                                 capture_output=True, text=True)
    assert run().returncode == 0
    path = tree / gen.EA_REL / "uml-2" / gen.GENERATED_NAME
    path.write_text("technology: UML\n", encoding="utf-8")
    failed = run()
    assert failed.returncode == 1 and "uml-2/conventions.yaml" in failed.stderr


def test_the_plugin_build_refuses_a_stale_generated_file(tree):
    spec = importlib.util.spec_from_file_location("build_plugin_for_test", ROOT / "tools" / "build-plugin.py")
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    assert build.generated_problems(tree) == []
    path = tree / gen.EA_REL / "dmn-1" / gen.GENERATED_NAME
    path.write_text("technology: DMN1.1\n", encoding="utf-8")
    problems = build.generated_problems(tree)
    assert len(problems) == 1 and "dmn-1/conventions.yaml" in problems[0]


def test_the_generated_text_is_deterministic_and_lf_only():
    for path, text in gen.expected_files(ROOT).items():
        assert "\r" not in text, path
        assert text.startswith("# GENERATED"), path


# ---------------------------------------------------------------------------
# The translation is exact
# ---------------------------------------------------------------------------
def test_every_route_and_arrangement_in_the_vocabulary_translates():
    standard, translation = _standard(), _translation()
    assert set(translation["routes"]) == set(standard["vocabulary"]["routes"])
    assert set(translation["arrangements"]) == set(standard["vocabulary"]["arrangements"])
    assert {bindings._normalize_route(v) for v in translation["routes"].values()} == set(bindings.ROUTE_NAMES)
    assert set(translation["arrangements"].values()) == set(bindings.GRAMMARS)
    assert translation["arrangements"]["type-fixed"] == "ea-semantic"
    assert set(standard["vocabulary"]["channels"]) == set(bindings.CHANNELS)
    assert tuple(standard["vocabulary"]["titles"]) == tuple(bindings.TITLE_CONVENTIONS)
    assert len(standard["vocabulary"]["arrangements"]) == 12


def test_every_standard_value_has_a_home_in_the_translation():
    standard, translation = _standard(), _translation()
    assert set(translation["spacing"]) == set(standard["spacing"])
    for targets in [*translation["spacing"].values(), *translation["container"].values()]:
        for target in targets:
            assert target["key"] in compose.DEFAULT_SPEC
    sized = set(standard["element_types"]) - set(translation["element_types"]["not_sized"])
    for name in sized:
        assert "w" in standard["element_types"][name], name


def test_every_sized_element_type_reaches_a_generated_file_or_is_waiting_for_a_guide():
    """An element type reaches EA through a default type or a size key in a map.

    `note` is the one type no map names yet. No convention file ever stated a size for a
    note, because no EA population settled one, and each guide's branch maps its own.
    """
    standard, translation = _standard(), _translation()
    used: set[str] = set()
    for _, language, ea in _languages():
        element_types = ((language or {}).get("layout") or {}).get("element_types") or {}
        for entry in (ea.get("layout_map") or {}).get("diagram_types", {}).values():
            used.add(entry.get("default_type", "box"))
            for target in (entry.get("size_keys") or {}).values():
                used.add(element_types.get(target, target))
    sized = set(standard["element_types"]) - set(translation["element_types"]["not_sized"])
    assert sized - used <= {"note"}


@pytest.mark.parametrize("path", GENERATED, ids=lambda p: p.parent.name)
def test_each_generated_gap_is_the_standards_times_the_unit_rule(path):
    standard, translation = _standard(), _translation()
    factor = translation["unit"]["ea_units_per_standard_unit"]
    want: dict[str, int] = {}
    for name, targets in translation["spacing"].items():
        for target in targets:
            want[target["key"]] = standard["spacing"][name]["value"] * factor * target.get("sign", 1)
    for name, targets in translation["container"].items():
        for target in targets:
            want[target["key"]] = standard["element_types"]["container"][name] * factor
    assert want["origin_top"] == -want["origin_left"]
    for name, body in _doc(path)["diagram_types"].items():
        assert body["spacing"] == want, name


@pytest.mark.parametrize("path", GENERATED, ids=lambda p: p.parent.name)
def test_each_generated_size_is_a_standard_types_size(path):
    allowed = {(row["w"], row["h"]) for row in _standard()["element_types"].values() if "w" in row}
    for name, body in _doc(path)["diagram_types"].items():
        assert "default" in body["sizing"], name
        for key, size in body["sizing"].items():
            assert (size["w"], size["h"]) in allowed, f"{name}.{key}"


def test_a_narrow_composer_gets_only_the_gaps_it_reads():
    """Every binding states every gap, and these composers refuse a key they don't have."""
    margin = _standard()["spacing"]["page_margin"]["value"]
    narrow = {"matrix": compose.compose_matrix, "radial-tree": compose.compose_radial_tree,
              "chevron-stack": compose.compose_chevron_stack}
    seen = set()
    for technology in bindings.available_bindings():
        for name, bound in bindings.find_binding(technology).diagram_types.items():
            if bound.grammar not in narrow:
                continue
            seen.add(bound.grammar)
            spec = dict(bound.spec())
            assert spec["origin_left"] == margin, name
            unknown = set(spec) - set(bindings._NARROW_SPEC_KEYS[bound.grammar])
            assert not unknown, (name, unknown)
    assert seen == set(narrow)
    mind_map = bindings.find_binding("MindMapping").diagram_type("MindMapping")
    compose.compose_radial_tree(
        [{"id": "branch", "children": [{"id": "leaf"}]}],
        dict(mind_map.spec()))


def test_a_route_outside_the_translation_is_refused(tree):
    _edit(tree / gen.TRANSLATION_REL, lambda d: d["routes"].pop("orthogonal"))
    with pytest.raises(gen.GenerationError, match="orthogonal"):
        gen.expected_files(tree)


def test_an_arrangement_outside_the_translation_is_refused(tree):
    _edit(tree / gen.TRANSLATION_REL, lambda d: d["arrangements"].pop("lanes"))
    with pytest.raises(gen.GenerationError, match="lanes"):
        gen.expected_files(tree)


def test_an_unknown_element_type_is_refused(tree):
    path = tree / gen.SHELF_REL / "bpmn-2" / "language.yaml"
    _edit(path, lambda d: d["layout"]["element_types"].update(StartEvent="hexagon"))
    with pytest.raises(gen.GenerationError, match="hexagon"):
        gen.expected_files(tree)


def test_a_size_key_with_nothing_behind_it_is_refused(tree):
    path = tree / gen.EA_REL / "bpmn-2" / "ea.yaml"
    _edit(path, lambda d: d["layout_map"]["diagram_types"]["Business Process"]["size_keys"].update(
        Gateway="NoSuchConcept"))
    with pytest.raises(gen.GenerationError, match="NoSuchConcept"):
        gen.expected_files(tree)


def test_an_arrangement_with_no_route_rule_must_state_a_route(tree):
    path = tree / gen.EA_REL / "togaf-9" / "ea.yaml"
    _edit(path, lambda d: d["layout_map"]["diagram_types"]["TOGAF_Interface"].pop("route"))
    with pytest.raises(gen.GenerationError, match="no default route"):
        gen.expected_files(tree)


def test_a_guide_that_lost_its_layout_block_is_named(tree):
    path = tree / gen.SHELF_REL / "bpmn-2" / "language.yaml"
    _edit(path, lambda d: d.pop("layout"))
    with pytest.raises(gen.GenerationError, match="layout"):
        gen.expected_files(tree)


def test_the_route_rule_supplies_what_a_language_leaves_out(tree):
    path = tree / gen.SHELF_REL / "bpmn-2" / "language.yaml"
    _edit(path, lambda d: d["layout"]["diagram_types"]["Process"].pop("route"))
    text = gen.generate_language(gen.Sources(tree), "bpmn-2")
    assert yaml.safe_load(text)["diagram_types"]["Business Process"]["routing"]["default"] == "OrthogonalSquare"


def test_a_diagram_type_with_nothing_listed_takes_the_defaults(tree):
    path = tree / gen.SHELF_REL / "bpmn-2" / "language.yaml"
    _edit(path, lambda d: d["layout"]["diagram_types"].update(Process={}))
    body = yaml.safe_load(gen.generate_language(gen.Sources(tree), "bpmn-2"))["diagram_types"]["Business Process"]
    assert body["grammar"] == "graph"
    assert body["title"] == "frame-header"
    assert body["routing"]["default"] == "Direct"


def test_a_guide_name_outside_the_layout_block_is_refused_not_defaulted(tree):
    path = tree / gen.EA_REL / "bpmn-2" / "ea.yaml"
    _edit(path, lambda d: d["layout_map"]["diagram_types"]["Choreography"].update(guide="Choreografy"))
    with pytest.raises(gen.GenerationError, match="Choreografy"):
        gen.expected_files(tree)
    ea = _doc(path)
    language = _doc(tree / gen.SHELF_REL / "bpmn-2" / "language.yaml")
    assert any("Choreografy" in p for p in gen.map_problems(ea, language, _standard(), {}))


def test_a_list_of_guide_names_is_judged_by_the_one_that_is_drawn(tree):
    """A map can send several guide views to one EA diagram. The first one supplies the layout."""
    ea = {"language": "wba", "layout_map": {"technology": "WBA", "diagram_types": {
        "One": {"guide": ["Real", "Another view"]}, "Two": {"guide": ["Typo", "Real"]}}}}
    language = {"id": "wba", "stub": True, "layout": {"diagram_types": {"Real": {}}}}
    problems = gen.map_problems(ea, language, _standard(), {})
    assert len(problems) == 1 and "`Two`" in problems[0] and "Typo" in problems[0]


def test_a_viewpoint_exception_with_a_reason_passes_the_check_and_the_build(tree):
    path = tree / gen.EA_REL / "archimate-3" / "ea.yaml"
    _edit(path, lambda d: d["layout_map"].setdefault("viewpoints", {}).update(
        Elsewhere={"guide": "NoSuchView", "diagram_type": "Business",
                   "reason": "EA ships it, and the standard has no such view."}))
    ea = _doc(path)
    language = _doc(tree / gen.SHELF_REL / "archimate-3" / "language.yaml")
    assert gen.map_problems(ea, language, _standard(), {}) == []
    text = gen.generate_language(gen.Sources(tree), "archimate-3")
    row = yaml.safe_load(text)["viewpoints"]["Elsewhere"]
    assert row == {"diagram_type": "Business"}
    generated = tree / gen.EA_REL / "archimate-3" / gen.GENERATED_NAME
    generated.write_text(text, encoding="utf-8")
    assert bindings.load_binding(generated).viewpoint("Elsewhere").diagram_type == "Business"


def test_a_viewpoint_with_no_reason_is_still_refused_by_both(tree):
    path = tree / gen.EA_REL / "archimate-3" / "ea.yaml"
    _edit(path, lambda d: d["layout_map"].setdefault("viewpoints", {}).update(
        Elsewhere={"guide": "NoSuchView", "diagram_type": "Business"}))
    language = _doc(tree / gen.SHELF_REL / "archimate-3" / "language.yaml")
    assert any("NoSuchView" in p for p in gen.map_problems(_doc(path), language, _standard(), {}))
    with pytest.raises(gen.GenerationError, match="NoSuchView"):
        gen.generate_language(gen.Sources(tree), "archimate-3")


def _catalog_with_no_maps(tmp_path) -> Path:
    for rel in (gen.STANDARD_REL, gen.TRANSLATION_REL):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / rel, tmp_path / rel)
    return tmp_path


def test_an_empty_catalog_fails_the_check_and_the_write(tmp_path):
    root = _catalog_with_no_maps(tmp_path)
    script = ROOT / "tools" / "gen_conventions.py"
    for args in (["--check"], []):
        done = subprocess.run([sys.executable, str(script), *args, "--root", str(root)],
                              capture_output=True, text=True)
        assert done.returncode != 0, args
        assert "no `ea.yaml` has a `layout_map`" in done.stderr


def test_the_plugin_build_refuses_an_empty_catalog(tmp_path):
    spec = importlib.util.spec_from_file_location("build_plugin_for_test", ROOT / "tools" / "build-plugin.py")
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    problems = build.generated_problems(_catalog_with_no_maps(tmp_path))
    assert len(problems) == 1 and "no `ea.yaml` has a `layout_map`" in problems[0]


@pytest.mark.parametrize("change,named", [
    (lambda m: m.update(presentation_profiles={"NoSuchProfile": {"show_notes": True}}), "NoSuchProfile"),
    (lambda m: m.update(viewpoints={"View": {"diagram_type": "Business"}}), "`guide`"),
    (lambda m: m.update(viewpoints={"View": {"guide": "Whatever"}}), "`diagram_type`"),
    (lambda m: m.pop("technology"), "`technology`"),
    (lambda m: m.pop("diagram_types"), "`diagram_types`"),
    (lambda m: m["diagram_types"].update(Business="not a mapping"), "archimate-3"),
], ids=["profile", "view-guide", "view-type", "technology", "diagram-types", "wrong-shape"])
def test_a_malformed_source_is_named_not_a_traceback(tree, change, named):
    _edit(tree / gen.EA_REL / "archimate-3" / "ea.yaml", lambda d: change(d["layout_map"]))
    with pytest.raises(gen.GenerationError) as caught:
        gen.expected_files(tree)
    assert named in str(caught.value)


def test_a_malformed_standard_is_named_not_a_traceback(tree):
    _edit(tree / gen.TRANSLATION_REL, lambda d: d.pop("unit"))
    with pytest.raises(gen.GenerationError, match="malformed"):
        gen.expected_files(tree)


def _sized_map(**entry) -> tuple[dict, dict]:
    ea = {"language": "wba", "stub": True, "layout_map": {"technology": "WBA", "diagram_types": {
        "Logical": {"size_keys": {"Thing": "actor"}, **entry}}}}
    language = {"id": "wba", "stub": True, "layout": {"element_types": {"Thing": "box"}}}
    return ea, language


def test_a_size_key_that_differs_from_the_guide_is_caught_by_the_check():
    ea, language = _sized_map()
    problems = gen.map_problems(ea, language, _standard(), {})
    assert len(problems) == 1 and "`Thing`" in problems[0] and "'actor'" in problems[0]
    ea["layout_map"]["diagram_types"]["Logical"]["size_keys"]["Thing"] = "box"
    assert gen.map_problems(ea, language, _standard(), {}) == []


def test_a_recorded_exception_or_a_stated_reason_clears_a_size_difference():
    ea, language = _sized_map(size_reason={"Thing": "EA draws this one as a stick figure."})
    assert gen.map_problems(ea, language, _standard(), {}) == []
    ea, language = _sized_map(size_reason={"Other": "Says nothing about Thing."})
    assert len(gen.map_problems(ea, language, _standard(), {})) == 1
    ea, language = _sized_map(size_reason="A sentence with no key excuses nothing in particular.")
    assert len(gen.map_problems(ea, language, _standard(), {})) == 1
    ea, language = _sized_map()
    language["layout"]["exceptions"] = {"Thing": {"reason": "Every tool draws it so.", "source": "8.1"}}
    assert gen.map_problems(ea, language, _standard(), {}) == []


def test_a_size_key_through_a_concept_is_compared_by_its_size_class():
    ea, language = _sized_map()
    language["layout"]["element_types"]["Person"] = "actor"
    ea["layout_map"]["diagram_types"]["Logical"]["size_keys"]["Thing"] = "Person"
    assert len(gen.map_problems(ea, language, _standard(), {})) == 1


def test_the_build_refuses_a_size_difference_nobody_stated(tree):
    path = tree / gen.EA_REL / "bpmn-2" / "ea.yaml"
    _edit(path, lambda d: d["layout_map"]["diagram_types"]["Business Process"].setdefault(
        "size_keys", {}).update(StartEvent="box"))
    with pytest.raises(gen.GenerationError, match="StartEvent"):
        gen.expected_files(tree)
    _edit(path, lambda d: d["layout_map"]["diagram_types"]["Business Process"].update(
        size_reason={"StartEvent": "Planted, and stated."}))
    gen.expected_files(tree)
    assert "size_reason" not in gen.generate_language(gen.Sources(tree), "bpmn-2")


# ---------------------------------------------------------------------------
# The engine's defaults and the tool's own figures
# ---------------------------------------------------------------------------
def test_the_engines_defaults_agree_with_the_standard():
    standard = _standard()
    container = standard["element_types"]["container"]
    defaults = compose.DEFAULT_SPEC
    assert defaults["band_pad_x"] == container["inner_padding"]
    assert defaults["band_pad_y"] == container["inner_padding"]
    assert defaults["lane_pad"] == container["inner_padding"]
    assert defaults["label_height"] == container["label_strip"]
    assert defaults["band_gap"] == standard["spacing"]["between_bands"]["value"]
    assert defaults["origin_left"] == standard["spacing"]["page_margin"]["value"]
    assert defaults["origin_top"] == -standard["spacing"]["page_margin"]["value"]
    box = standard["element_types"]["box"]
    assert defaults["item_gap_flow"] == standard["spacing"]["along_flow"]["value"]
    for spec in (defaults, compose_matrix.DEFAULT_MATRIX_SPEC):
        assert spec["item_width"] == box["w"]
        assert spec["item_height"] == box["h"]
        assert spec["item_gap_x"] == standard["spacing"]["across"]["value"]
        assert spec["item_gap_y"] == standard["spacing"]["down"]["value"]
    assert compose_chevron.DEFAULT_CHEVRON_SPEC["item_width"] == box["w"]
    assert compose_chevron.DEFAULT_CHEVRON_SPEC["item_height"] == box["h"]


@pytest.mark.parametrize("key,value", [("band_gap", 31), ("item_width", 140), ("item_height", 60),
                                       ("item_gap_x", 20), ("item_gap_y", 20), ("item_gap_flow", 30)])
def test_the_engine_check_fails_on_a_planted_difference(monkeypatch, key, value):
    monkeypatch.setitem(compose.DEFAULT_SPEC, key, value)
    with pytest.raises(AssertionError):
        test_the_engines_defaults_agree_with_the_standard()


@pytest.mark.parametrize("module,name", [("compose_matrix", "DEFAULT_MATRIX_SPEC"),
                                         ("compose_chevron", "DEFAULT_CHEVRON_SPEC")])
def test_the_engine_check_reads_the_composers_with_their_own_defaults(monkeypatch, module, name):
    monkeypatch.setitem(getattr(sys.modules[module], name), "item_width", 140)
    with pytest.raises(AssertionError):
        test_the_engines_defaults_agree_with_the_standard()


def test_lints_text_clearance_stays_the_tools_own_figure():
    assert lint.LABEL_MARGIN == _translation()["tool_figures"]["label_margin"]


# ---------------------------------------------------------------------------
# The sources' own names
# ---------------------------------------------------------------------------
def _languages() -> list[tuple[str, dict | None, dict]]:
    out = []
    for folder in sorted((ROOT / gen.EA_REL).iterdir()):
        ea_path = folder / "ea.yaml"
        if not ea_path.is_file():
            continue
        language_path = ROOT / gen.SHELF_REL / folder.name / "language.yaml"
        out.append((folder.name, _doc(language_path) if language_path.is_file() else None,
                    _doc(ea_path)))
    return out


def test_the_nine_stubs_and_the_two_maps_are_there():
    names = {name for name, _, _ in _languages()}
    assert set(NINE) | set(TWO_MAPS) <= names
    shelf = {p.parent.name for p in (ROOT / gen.SHELF_REL).glob("*/language.yaml")}
    assert set(NINE) <= shelf
    assert not set(TWO_MAPS) & shelf


@pytest.mark.parametrize("name,language,ea", _languages(), ids=lambda v: v if isinstance(v, str) else "")
def test_each_layout_block_and_map_passes_its_checks(name, language, ea):
    standard = _standard()
    if language is not None:
        assert gen.layout_problems(language, standard) == []
        assert language["id"] == name
    assert gen.map_problems(ea, language, standard, RECORDED) == []
    assert ea["language"] == name


def test_the_fixture_holds_thirty_two_rows_all_of_them_generated():
    assert len(RECORDED) == 32
    generated = {f"{doc['technology']}::{dt}" for doc in map(_doc, GENERATED) for dt in doc["diagram_types"]}
    assert set(RECORDED) <= generated


def _small_guide(**layout):
    return {"id": "wba", "layout": {"basis": "Ours.", **layout},
            "concepts": {"Thing": {"uml_base": ["Class", "Constraint"]}},
            "notation": {"elements": {"Hex": {"shape": "hexagon"}}}}


def test_a_shape_with_no_line_is_caught_and_a_stated_reason_clears_it():
    problems = gen.layout_problems(_small_guide(), _standard())
    assert any("`Hex`" in p for p in problems)
    assert any("`Thing`" in p and "UML Constraint" in p for p in problems)
    stated = {"not_drawn": {"reason": "Shown inside its owner.", "concepts": ["Hex", "Thing"]}}
    assert gen.layout_problems(_small_guide(no_element_type=stated), _standard()) == []


@pytest.mark.parametrize("groups,word", [
    ({"not_drawn": {"reason": "See the notation.", "concepts": "see `notation.not_specified`"}}, "not_drawn"),
    ({"not_drawn": {"reason": "No names at all."}}, "not_drawn"),
    ({"not_drawn": ["Hex"]}, "not_drawn"),
    (["Hex"], "no_element_type"),
], ids=["text-for-a-list", "no-list", "group-is-a-list", "block-is-a-list"])
def test_a_no_element_type_block_the_checks_cant_read_is_a_problem(groups, word):
    problems = gen.layout_problems(_small_guide(no_element_type=groups), _standard())
    assert any(word in p and "`Hex`" not in p for p in problems), problems
    # And none of its names clears the concepts it meant to.
    assert any("`Hex`" in p for p in problems)


def test_a_malformed_no_element_type_block_is_caught_on_a_stub_too():
    language = {"id": "wba", "stub": True, "layout": {"no_element_type": {"g": {"concepts": "Hex"}}}}
    assert gen.layout_problems(language, _standard()) != []


def test_a_diagram_type_is_checked_even_when_the_guide_lists_none():
    guide = _small_guide(diagram_types={"Made up": {}})
    assert any("`Made up`" in p for p in gen.layout_problems(guide, _standard()))


def test_element_types_may_name_what_the_notation_names():
    assert gen.layout_problems(_small_guide(element_types={"Hex": "decision-diamond", "Thing": "note"}), _standard()) == []


def test_a_map_on_another_technology_needs_a_reason():
    ea = {"language": "wba", "technology": "WBA", "layout_map": {"technology": "WBA Diagrams"}}
    assert any("differs" in p for p in gen.map_problems(ea, None, _standard(), {}))
    ea["layout_map"]["technology_reason"] = "EA registers these diagrams under another profile."
    assert gen.map_problems(ea, None, _standard(), {}) == []


def test_a_planted_wrong_arrangement_fails():
    ea = next(ea for name, _, ea in _languages() if name == "uml-2")
    language = next(lang for name, lang, _ in _languages() if name == "uml-2")
    language["layout"]["diagram_types"]["Class diagram"]["arrangement"] = "lanes"
    problems = gen.map_problems(ea, language, _standard(), RECORDED)
    assert any("Logical" in p and "arrangement" in p for p in problems)
    ea["layout_map"]["diagram_types"]["Logical"]["arrangement_reason"] = "Drawn in lanes on purpose."
    assert gen.map_problems(ea, language, _standard(), RECORDED) == []


def test_a_planted_unknown_type_and_vocabulary_word_fail():
    standard = _standard()
    language = {"id": "wba", "stub": True, "layout": {
        "element_types": {"Thing": "hexagon"},
        "diagram_types": {"View": {"arrangement": "spiral", "route": "wiggly", "title": "banner",
                                   "channels": {"free": ["smell"]}}},
    }}
    problems = "\n".join(gen.layout_problems(language, standard))
    for word in ("hexagon", "spiral", "wiggly", "banner", "smell"):
        assert word in problems


def test_an_exception_needs_a_reason_and_a_source():
    standard = _standard()
    language = {"id": "wba", "stub": True, "layout": {"exceptions": {"Thing": {"reason": "Because."}}}}
    assert any("reason and a source" in p for p in gen.layout_problems(language, standard))
    language["layout"]["exceptions"]["Thing"]["source"] = "Section 8."
    assert gen.layout_problems(language, standard) == []


def _guide(**overrides) -> dict:
    guide = {"id": "wba", "concepts": {"Task": {}, "Choice": {}}, "diagram_types": {"Process": {}},
             "notation": {"elements": {"Task": {"shape": "rounded rectangle"},
                                       "Choice": {"shape": "hexagon"}}},
             "layout": {"element_types": {}, "diagram_types": {}}}
    guide.update(overrides)
    return guide


def test_a_planted_hexagon_with_no_line_fails_and_a_rectangle_needs_none():
    standard = _standard()
    problems = gen.layout_problems(_guide(), standard)
    assert len(problems) == 1 and "Choice" in problems[0] and "hexagon" in problems[0]
    guide = _guide()
    guide["layout"]["element_types"]["Choice"] = "decision-diamond"
    assert gen.layout_problems(guide, standard) == []


def test_a_concept_the_guide_does_not_hold_fails():
    guide = _guide()
    guide["layout"]["element_types"].update(Choice="box", Ghost="box")
    problems = gen.layout_problems(guide, _standard())
    assert len(problems) == 1 and "Ghost" in problems[0]


def test_a_uml_base_not_drawn_as_a_box_needs_a_line():
    guide = {"id": "wba", "concepts": {"Link": {"uml_base": "Port"}, "Part": {"uml_base": "Class"}},
             "layout": {"element_types": {}}}
    problems = gen.layout_problems(guide, _standard())
    assert len(problems) == 1 and "Link" in problems[0]


def test_a_full_ea_yaml_must_agree_with_its_map():
    standard = _standard()
    language = {"id": "wba", "concepts": {"Task": {}}, "layout": {
        "element_types": {},
        "viewpoints": {"View": {"admits": ["Task", "Ghost"]}}}}
    ea = {"language": "wba", "technology": "BPMN2.0", "diagram_types": {"Process": {"token": "WBA::Process"}},
          "layout_map": {"technology": "WBA", "diagram_types": {"Elsewhere": {}}}}
    problems = "\n".join(gen.map_problems(ea, language, standard, {}))
    assert "differs from ea.yaml's 'BPMN2.0'" in problems
    assert "WBA::Elsewhere" in problems
    assert "Ghost" in problems


# ---------------------------------------------------------------------------
# Nothing crosses packages at run time (design section 13, check 5)
# ---------------------------------------------------------------------------
def test_the_helpers_work_with_the_shelf_removed(tmp_path):
    """Copy the EA plugin alone. The loader, composer, linter, and advisor still answer."""
    skills = tmp_path / "plugins/ai-power-tools/skills"
    for rel in ("_shared/languages", "ea-diagram-composition/tools", "ea-diagram-advisor/tools"):
        shutil.copytree(ROOT / "plugins/ai-power-tools/skills" / rel, skills / rel,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "test_*.py"))
    assert not (tmp_path / gen.SHELF_REL).exists()
    code = f"""
import sys
sys.path[:0] = [r"{skills / 'ea-diagram-composition/tools'}", r"{skills / 'ea-diagram-advisor/tools'}"]
import bindings, compose, lint, advise
binding = bindings.find_binding("BPMN2.0")
assert binding is not None, "no binding"
assert binding.diagram_type("Business Process").size_for("StartEvent") == (30, 30)
assert len(bindings.available_bindings()) >= 11
result = compose.compose_lanes(
    [{{"name": "A", "items": [{{"id": 1, "slot": 0}}]}}],
    dict(binding.diagram_type("Business Process").spec()))
assert result["items"]
assert hasattr(lint, "LABEL_MARGIN") and hasattr(advise, "__file__")
"""
    done = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=tmp_path)
    assert done.returncode == 0, done.stderr


# ---------------------------------------------------------------------------
# A map declares each diagram token it serves
# ---------------------------------------------------------------------------
def _plant_map(tree: Path, folder: str, technology: str, entries: dict) -> None:
    path = tree / gen.EA_REL / folder / "ea.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump({"language": folder, "layout_map": {
        "technology": technology, "extends": "UML", "stereotype_prefix": "",
        "diagram_types": entries}}), encoding="utf-8")


def _write_generated(tree: Path) -> None:
    for path, text in gen.expected_files(tree).items():
        path.write_bytes(text.encode("utf-8"))


def test_a_token_in_a_map_reaches_the_generated_file_and_the_resolver(tree):
    """The whole road: `layout_map`, then `conventions.yaml`, then the standard's sizes."""
    _plant_map(tree, "updm-2", "UPDM2", {"OV-2": {"token": "UPDM2_OV::OV-2", "base": "Logical"}})
    _plant_map(tree, "requirements", "EAExtended:Requirements",
               {"Requirements": {"token": "Extended::Requirements", "base": "Custom"}})
    _plant_map(tree, "business-modeling", "EAExtended",
               {"Business Modeling": {"token": "Extended::Business Modeling", "base": "Logical"}})
    _write_generated(tree)

    directory = tree / gen.EA_REL
    assert bindings.token_conflicts(directory) == {}
    box = _standard()["element_types"]["box"]
    installed = {"UML", "UPDM2", "EAExtended", "EAExtended:Requirements"}
    for token, folder, name in (
            ("UPDM2_OV::OV-2", "updm-2", "OV-2"),
            ("Extended::Requirements", "requirements", "Requirements"),
            ("Extended::Business Modeling", "business-modeling", "Business Modeling")):
        assert _doc(directory / folder / gen.GENERATED_NAME)["diagram_types"][name]["token"] == token
        resolution = bindings.resolve_diagram(installed, style_ex=f"MDGDgm={token};",
                                              directory=directory)
        assert resolution.path == "qualified", token
        assert resolution.binding.source == f"{folder}/{gen.GENERATED_NAME}"
        assert resolution.diagram_type.size_for() == (box["w"], box["h"])
        assert resolution.diagram_type.spec()["item_width"] == box["w"]


def test_two_maps_claiming_one_token_fail_the_check(tree):
    for folder in ("one", "two"):
        _plant_map(tree, folder, folder.title(), {"View": {"token": "WBA_Shared::View"}})
    with pytest.raises(gen.GenerationError, match=r"'WBA_Shared::View' is claimed by one, two"):
        gen.expected_files(tree)
    with pytest.raises(gen.GenerationError, match="more than one claim"):
        gen.stale_files(tree)
    assert gen.main(["--check", "--root", str(tree)]) == 2


def test_a_stated_token_that_collides_with_a_map_with_no_token_fails_the_check(tree):
    _plant_map(tree, "one", "One", {"View": {"token": "BPMN2.0::Business Process"}})
    with pytest.raises(gen.GenerationError, match="bpmn-2, one"):
        gen.expected_files(tree)


def test_a_map_states_a_token_whole_and_on_a_name_that_holds_the_separator():
    ea = {"language": "wba", "layout_map": {"technology": "WBA", "diagram_types": {
        "WBA_A::View": {},
        "Other": {"token": "NoSeparator"},
        "Fine": {"token": "WBA_A::Fine"},
    }}}
    problems = "\n".join(gen.map_problems(ea, None, _standard(), {}))
    assert "`WBA_A::View` holds `::`" in problems
    assert "`Other` has token 'NoSeparator'" in problems
    assert "Fine" not in problems


def test_a_stated_token_must_be_one_ea_yaml_lists():
    ea = {"language": "wba", "technology": "WBA",
          "diagram_types": {"View": {"token": "WBA_A::View"}},
          "layout_map": {"technology": "WBA", "diagram_types": {
              "View": {"token": "WBA_A::View"},
              "Guess": {"token": "WBA_A::Guess"},
              "Read": {"token": "WBA_B::Read", "token_reason": "Read from a sample model."},
          }}}
    problems = gen.map_problems(ea, None, _standard(), {})
    assert problems == ["wba layout_map: `WBA_A::Guess` is not in ea.yaml's `diagram_types`"]


def test_a_map_may_use_the_id_the_api_reports():
    ea = {"language": "wba", "technology": "WBA", "api_technology_id": "WBA1.0",
          "layout_map": {"technology": "WBA1.0"}}
    assert gen.map_problems(ea, None, _standard(), {}) == []
    ea["api_technology_id"] = "WBA2.0"
    assert any("differs" in p for p in gen.map_problems(ea, None, _standard(), {}))
