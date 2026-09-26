#!/usr/bin/env python3
"""Tests for the language-binding schema and the two pilot bindings.

Run from the repository root:

    python -m pytest ea-diagram-composition/tools/test_bindings.py -q

Hermetic. These tests read the shipped binding files from disk, which is the
point of several of them, but nothing here touches Sparx EA, a repository or a
COM object. The live generation tests - one diagram per pilot binding, composed,
placed, verified and linted - live with the server suite, because that is where
a `repo` fixture exists.

WHAT THESE TESTS ARE PROTECTING
-------------------------------
Three different things, and it is worth knowing which is which:

1. **The schema rejects what it should.** Every validation rule has a test that
   feeds it a document it must refuse. A validator that accepts everything is
   indistinguishable from no validator, and the failure it lets through is a
   diagram that came out wrong for a reason nobody can find.

2. **The pilots say what was measured.** The numbers in the shipped bindings
   came from real diagrams. Tests pin the ones that would be most damaging to
   "tidy up" - the technology ids, the `Business Process` space, the
   `ArchiMate_` prefix, the 30x30 events.

3. **The layer boundary holds.** `compose.py` knows no technology names, and
   the two bindings differ only in data. A single `if technology ==` in the
   engine would undo the design while every other test still passed.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from bindings import (  # noqa: E402
    CHANNELS,
    GRAMMARS,
    IMPLEMENTED_GRAMMARS,
    ROUTE_NAMES,
    TITLE_CONVENTIONS,
    Binding,
    BindingError,
    available_bindings,
    find_binding,
    load_binding,
    load_binding_text,
)
from compose import (  # noqa: E402
    DEFAULT_SPEC,
    compose_lanes,
    compose_layered_bands,
)

_BINDINGS_DIR = _HERE.parent / "bindings"

pytest.importorskip("yaml", reason="PyYAML is required to read bindings")


# ---------------------------------------------------------------------------
# A minimal valid document, and a helper to break one field at a time
# ---------------------------------------------------------------------------
MINIMAL = """
technology: WBA
diagram_types:
  Overview:
    grammar: layered-bands
    title: drawn
    sizing:
      default: {w: 100, h: 60}
    routing:
      default: Direct
    channels:
      fill: ~
      free: [border]
"""


def _doc(**overrides: str) -> str:
    """Build a document from `MINIMAL` with one block swapped out.

    Keeps the rejection tests to the one line each is about, so a failure names
    the rule rather than a wall of YAML.
    """
    text = MINIMAL
    for old, new in overrides.items():
        marker = old.replace("__", " ")
        assert marker in text, f"{marker!r} not in the minimal document"
        text = text.replace(marker, new)
    return text


# ---------------------------------------------------------------------------
# The happy path first - every later test asserts a deviation from this
# ---------------------------------------------------------------------------
def test_minimal_document_loads():
    binding = load_binding_text(MINIMAL)
    assert binding.technology == "WBA"
    assert binding.display_name == "WBA"
    assert binding.extends is None
    assert binding.stereotype_prefix == ""
    assert sorted(binding.diagram_types) == ["Overview"]
    assert binding.viewpoints == {}
    assert binding.presentation_profiles == {}


def test_a_diagram_type_translates_to_a_layout_spec():
    dt = load_binding_text(MINIMAL).diagram_type("Overview")
    assert dt.spec() == {"item_width": 100, "item_height": 60}


def test_spec_overrides_win_over_the_binding():
    dt = load_binding_text(MINIMAL).diagram_type("Overview")
    assert dt.spec({"item_width": 200})["item_width"] == 200


def test_a_spec_override_naming_an_unknown_key_is_refused():
    """Refused here rather than by the engine.

    The engine's message would be about a spec key and would not mention the
    binding, sending the reader to the wrong file.
    """
    dt = load_binding_text(MINIMAL).diagram_type("Overview")
    with pytest.raises(BindingError, match="item_wdith"):
        dt.spec({"item_wdith": 200})


# ---------------------------------------------------------------------------
# Rejection cases - one per rule
# ---------------------------------------------------------------------------
def test_an_unknown_top_level_key_is_refused():
    with pytest.raises(BindingError, match="color_palette"):
        load_binding_text(MINIMAL + "color_palette: {}\n")


def test_a_misspelled_top_level_key_gets_the_right_one_named():
    with pytest.raises(BindingError, match="use diagram_types"):
        load_binding_text(MINIMAL.replace("diagram_types:", "diagramTypes:"))


def test_a_missing_technology_is_refused():
    with pytest.raises(BindingError, match=r"\.technology"):
        load_binding_text(MINIMAL.replace("technology: WBA", "extends: ~"))


def test_a_technology_id_containing_the_separator_is_refused():
    """`MDGDgm` values look like `BPMN2.0::Business Process`.

    An author who pastes the whole thing in as the technology id has bound a
    technology that does not exist, and every resolution against it returns
    nothing without complaining.
    """
    with pytest.raises(BindingError, match="part BEFORE"):
        load_binding_text(MINIMAL.replace("technology: WBA",
                                          "technology: WBA::Overview"))


def test_no_diagram_types_is_refused():
    with pytest.raises(BindingError, match="diagram_types"):
        load_binding_text("technology: WBA\ndiagram_types: {}\n")


def test_an_unknown_grammar_is_refused_and_the_four_are_named():
    with pytest.raises(BindingError) as exc:
        load_binding_text(_doc(**{"grammar:__layered-bands":
                                  "grammar: spiral"}))
    message = str(exc.value)
    assert "spiral" in message
    for grammar in GRAMMARS:
        assert grammar in message


def test_a_grammar_the_engine_cannot_compose_still_loads():
    """A grammar the engine has not built yet still loads and says so.

    Refusing it would force a binding author to record an implemented grammar
    for a diagram type that is genuinely something else - a lie stored as data.
    The binding records the truth and `grammar_is_implemented` is how a consumer
    finds out before composing rather than after.

    The example grammar is DERIVED rather than named. This test previously named
    `nested-grid`, and the day that grammar shipped the test failed for a reason
    that had nothing to do with the property under test. What it is really
    asserting is "whichever grammar is unbuilt, a binding may still name it",
    so it now asks `GRAMMARS` which one that is.
    """
    unbuilt = sorted(set(GRAMMARS) - IMPLEMENTED_GRAMMARS)
    if not unbuilt:
        pytest.skip(
            "every grammar in the vocabulary is implemented, so there is no "
            "unbuilt one to name; delete this test or add the next grammar to "
            "GRAMMARS first"
        )
    grammar = unbuilt[0]
    dt = load_binding_text(
        _doc(**{"grammar:__layered-bands": f"grammar: {grammar}"})
    ).diagram_type("Overview")
    assert dt.grammar == grammar
    assert dt.grammar_is_implemented is False


def test_an_unknown_title_convention_is_refused():
    with pytest.raises(BindingError) as exc:
        load_binding_text(_doc(**{"title:__drawn": "title: centered"}))
    for convention in TITLE_CONVENTIONS:
        assert convention in str(exc.value)


def test_a_missing_title_convention_is_refused():
    """Neither convention can be the silent default.

    A diagram with two titles and a diagram with none are equally likely
    mistakes, and the corpus split tracks notation rather than taste.
    """
    with pytest.raises(BindingError, match="title"):
        load_binding_text(_doc(**{"title:__drawn": "notes: nothing"}))


def test_sizing_without_a_default_is_refused():
    with pytest.raises(BindingError, match=r"sizing\.default"):
        load_binding_text(_doc(**{"default:__{w:__100,__h:__60}":
                                  "Widget: {w: 100, h: 60}"}))


def test_sizing_spelled_out_in_full_words_is_refused_with_the_short_key():
    with pytest.raises(BindingError, match="use 'w'"):
        load_binding_text(_doc(**{"default:__{w:__100,__h:__60}":
                                  "default: {width: 100, height: 60}"}))


@pytest.mark.parametrize("size", ["{w: 0, h: 60}", "{w: -5, h: 60}",
                                  "{w: 100.5, h: 60}", "{w: '100', h: 60}"])
def test_a_size_that_is_not_a_positive_whole_number_is_refused(size):
    with pytest.raises(BindingError, match=r"sizing\.default\.w"):
        load_binding_text(_doc(**{"default:__{w:__100,__h:__60}":
                                  f"default: {size}"}))


def test_a_spacing_key_the_engine_does_not_have_is_refused():
    with pytest.raises(BindingError, match="item_gap_z"):
        load_binding_text(MINIMAL + "    spacing:\n      item_gap_z: 10\n")


def test_the_pitch_key_from_the_original_sketch_names_what_to_use_instead():
    """The trap this schema was designed around.

    A pitch includes the box it steps over, so `pitch: 40` beside a 100-wide
    item is a layout the engine refuses. An author writing it deserves to be
    told which key they meant, not handed the engine's arithmetic complaint at
    generation time.

    Matched on the hint's own wording, not on `item_gap_x`: every unknown-key
    message ends in `Known keys: ..., item_gap_x, ...`, so matching the key name
    would pass with the hints dict empty and this test would be evidence of
    nothing. Remove the assertion and `pitch:` becomes a bare "unknown key"
    again, which is the failure the hint exists to prevent.
    """
    with pytest.raises(BindingError, match="includes the box it steps over"):
        load_binding_text(MINIMAL + "    spacing:\n      pitch: {h: 40}\n")


def test_every_spacing_key_the_engine_has_is_accepted():
    """Validation is against `compose.DEFAULT_SPEC` itself, so the two cannot
    drift: a spec key added to the engine is usable from a binding at once."""
    for key in DEFAULT_SPEC:
        load_binding_text(MINIMAL + f"    spacing:\n      {key}: 5\n")


def test_missing_routing_is_refused():
    with pytest.raises(BindingError, match="routing"):
        load_binding_text(MINIMAL.replace("    routing:\n      default: Direct\n",
                                          ""))


def test_a_route_ea_does_not_accept_is_refused():
    with pytest.raises(BindingError) as exc:
        load_binding_text(_doc(**{"default:__Direct": "default: Squiggly"}))
    assert "Squiggly" in str(exc.value)
    assert "OrthogonalSquare" in str(exc.value)


@pytest.mark.parametrize("spelling", ["OrthogonalSquare", "orthogonal square",
                                       "orthogonal-square", "ORTHOGONALSQUARE"])
def test_route_names_are_accepted_however_they_are_spelled(spelling):
    """Matching the server's own normalization, which strips non-alphanumerics
    and lowercases. A binding author should not have to guess the casing."""
    binding = load_binding_text(_doc(**{"default:__Direct":
                                        f"default: {spelling}"}))
    assert binding.diagram_type("Overview").default_route() == spelling


def _with_routing(*lines: str) -> str:
    """Splice extra keys into the routing block rather than appending them.

    Appending to `MINIMAL` lands the keys under `channels`, which is a different
    document that the schema correctly refuses for a different reason - and a
    test that passes because the wrong rule fired is worse than no test.
    """
    extra = "".join(f"      {line}\n" for line in lines)
    return MINIMAL.replace("      default: Direct\n",
                           "      default: Direct\n" + extra)


def test_trunk_for_gets_the_trunk_route_and_other_types_get_the_default():
    binding = load_binding_text(_with_routing("trunk_for: [Realization]",
                                              "trunk_route: TreeVertical"))
    dt = binding.diagram_type("Overview")
    assert dt.route_for("Realization") == "TreeVertical"
    assert dt.route_for("Association") == "Direct"


def test_trunk_for_without_a_trunk_route_defaults_to_orthogonal():
    dt = load_binding_text(
        _with_routing("trunk_for: [Realization]")).diagram_type("Overview")
    assert dt.route_for("Realization") == "OrthogonalSquare"


# ---------------------------------------------------------------------------
# Channels - the block the whole schema exists for
# ---------------------------------------------------------------------------
def test_a_missing_channels_block_is_refused():
    with pytest.raises(BindingError, match="channels"):
        load_binding_text(MINIMAL.replace(
            "    channels:\n      fill: ~\n      free: [border]\n", ""))


def test_a_channels_block_without_fill_is_refused():
    """`fill` is mandatory even when the answer is "nothing".

    Omitting it reads as "no opinion", and no opinion about fill is how an
    agent recolors ArchiMate's layer palette by lifecycle and breaks the
    notation while believing it added a feature.
    """
    with pytest.raises(BindingError, match=r"channels\.fill"):
        load_binding_text(MINIMAL.replace("      fill: ~\n", ""))


def test_fill_may_be_explicitly_unclaimed():
    dt = load_binding_text(MINIMAL).diagram_type("Overview")
    assert dt.claimed_channels() == {}
    assert dt.channel_is_free("border") is True
    assert dt.channel_is_free("fill") is False


def test_a_channel_cannot_be_both_claimed_and_free():
    """The cross-check that matters.

    A binding saying fill means layer AND that fill is free has told a
    consumer it is safe to overwrite the notation's own meaning.
    """
    with pytest.raises(BindingError, match="already claimed"):
        load_binding_text(_doc(**{"fill:__~": "fill: layer",
                                  "free:__[border]": "free: [fill, border]"}))


def test_a_claimed_channel_cannot_be_listed_free_either():
    with pytest.raises(BindingError, match="already claimed"):
        load_binding_text(
            MINIMAL.replace("free: [border]", "free: [border, icon]")
            + "      claimed:\n        icon: element type\n")


def test_fill_belongs_in_its_own_key_not_in_claimed():
    with pytest.raises(BindingError, match="one place too many"):
        load_binding_text(MINIMAL + "      claimed:\n        fill: layer\n")


def test_an_invented_channel_name_is_refused_and_the_real_ones_named():
    with pytest.raises(BindingError) as exc:
        load_binding_text(_doc(**{"free:__[border]": "free: [sparkle]"}))
    assert "sparkle" in str(exc.value)
    assert "opacity" in str(exc.value)


def test_a_duplicated_free_channel_is_refused():
    with pytest.raises(BindingError, match="duplicate"):
        load_binding_text(_doc(**{"free:__[border]":
                                  "free: [border, border]"}))


# ---------------------------------------------------------------------------
# Viewpoints
# ---------------------------------------------------------------------------
_VIEWPOINT = """
viewpoints:
  Landscape:
    diagram_type: Overview
    intent: [what is out there]
    admits: [Widget, Gadget]
"""


def test_a_viewpoint_loads_and_reports_what_it_admits():
    vp = load_binding_text(MINIMAL + _VIEWPOINT).viewpoint("Landscape")
    assert vp.diagram_type == "Overview"
    assert vp.admits == ("Widget", "Gadget")
    assert vp.admits_concept("Widget") is True
    assert vp.admits_concept("Sprocket") is False


def test_a_viewpoint_naming_an_undeclared_diagram_type_is_refused():
    """The one place a viewpoint catalog can be quietly wrong.

    A viewpoint pointing at a diagram type nothing declares would be selected
    and then fail to compose, with the error appearing nowhere near the typo.
    """
    with pytest.raises(BindingError, match="not declared"):
        load_binding_text(
            MINIMAL + _VIEWPOINT.replace("diagram_type: Overview",
                                         "diagram_type: Ovreview"))


def test_a_viewpoint_may_override_the_grammar():
    """A capability map is a nested grid even though its diagram type composes
    as bands, so the override is load-bearing rather than decorative."""
    vp = load_binding_text(
        MINIMAL + _VIEWPOINT + "    grammar: nested-grid\n"
    ).viewpoint("Landscape")
    assert vp.grammar == "nested-grid"


def test_a_viewpoint_grammar_outside_the_four_is_refused():
    with pytest.raises(BindingError, match="spiral"):
        load_binding_text(MINIMAL + _VIEWPOINT + "    grammar: spiral\n")


def test_duplicate_admits_entries_are_refused():
    with pytest.raises(BindingError, match="duplicate"):
        load_binding_text(
            MINIMAL + _VIEWPOINT.replace("[Widget, Gadget]",
                                         "[Widget, Widget]"))


def test_viewpoints_admitting_ranks_narrowest_first():
    """A layered view of three applications is a layered view with two empty
    bands, so the narrower viewpoint that admits everything wins."""
    binding = load_binding_text(MINIMAL + """
viewpoints:
  Narrow:
    diagram_type: Overview
    admits: [Widget, Gadget]
  Wide:
    diagram_type: Overview
    admits: [Widget, Gadget, Sprocket, Cog]
""")
    ranked = binding.viewpoints_admitting(["Widget"])
    assert [vp.name for vp in ranked] == ["Narrow", "Wide"]
    assert binding.viewpoints_admitting(["Sprocket"])[0].name == "Wide"
    assert binding.viewpoints_admitting(["Unheard"]) == []


# ---------------------------------------------------------------------------
# Presentation profiles
# ---------------------------------------------------------------------------
def test_a_profile_says_what_it_shows_and_the_loader_inverts_it():
    """The polarity flip lives in exactly one place.

    A profile states what a reader sees; EA is told what to hide. Doing that
    inversion at each call site is how one of them ends up backwards.
    """
    binding = load_binding_text(MINIMAL + """
presentation_profiles:
  executive:
    connector_labels: false
    element_stereotypes: false
    collapse_parallel: true
    direction_only: true
""")
    profile = binding.profile("executive")
    assert profile.display_settings() == {"hide_connector_labels": True,
                                          "hide_element_stereotypes": True}
    assert profile.collapses_parallel is True


def test_a_profile_only_emits_settings_it_actually_states():
    """Silence is not a default.

    A profile that says nothing about stereotypes must leave them alone rather
    than assert a value it never chose - otherwise applying a profile undoes a
    deliberate choice made elsewhere.
    """
    binding = load_binding_text(
        MINIMAL + "presentation_profiles:\n  quiet:\n"
                  "    connector_labels: false\n")
    assert binding.profile("quiet").display_settings() == {
        "hide_connector_labels": True}


def test_a_profile_written_in_hide_flags_is_corrected():
    """A profile states what it SHOWS; the hint says so rather than just
    refusing the key.

    Matched on the hint's wording, not on `connector_labels`: that substring
    sits inside the rejected key itself (`hide_connector_labels`) and inside the
    message's `Known keys:` list, so it passes with no hint at all. Remove this
    assertion and an author who wrote the EA-facing polarity gets "unknown key"
    and no indication that the schema has the same setting the other way up.
    """
    with pytest.raises(BindingError, match="profiles say what they SHOW"):
        load_binding_text(
            MINIMAL + "presentation_profiles:\n  odd:\n"
                      "    hide_connector_labels: true\n")


def test_direction_only_without_collapsing_is_refused():
    """It only means something under collapsing, so a profile setting it alone
    reads as if it does something."""
    with pytest.raises(BindingError, match="collapse_parallel"):
        load_binding_text(
            MINIMAL + "presentation_profiles:\n  odd:\n"
                      "    direction_only: true\n")


def test_a_profile_flag_that_is_not_a_boolean_is_refused():
    with pytest.raises(BindingError, match="true or false"):
        load_binding_text(
            MINIMAL + "presentation_profiles:\n  odd:\n"
                      "    connector_labels: maybe\n")


def test_compartments_takes_a_keyword_or_a_list():
    binding = load_binding_text(MINIMAL + """
presentation_profiles:
  a: {compartments: all}
  b: {compartments: none}
  c: {compartments: [name, key-attributes]}
""")
    assert binding.profile("a").get("compartments") == "all"
    assert binding.profile("c").get("compartments") == ("name",
                                                        "key-attributes")
    with pytest.raises(BindingError, match="compartments"):
        load_binding_text(MINIMAL + "presentation_profiles:\n"
                                    "  d: {compartments: some}\n")


# ---------------------------------------------------------------------------
# Lookups fail loudly and name what exists
# ---------------------------------------------------------------------------
def test_an_unknown_lookup_names_what_is_declared():
    binding = load_binding_text(MINIMAL)
    with pytest.raises(BindingError, match="Overview"):
        binding.diagram_type("Missing")
    with pytest.raises(BindingError, match=r"\(none\)"):
        binding.viewpoint("Missing")
    with pytest.raises(BindingError, match=r"\(none\)"):
        binding.profile("Missing")


def test_mdgdgm_resolution_matches_only_its_own_technology():
    binding = load_binding_text(MINIMAL)
    assert binding.diagram_type_for_mdgdgm("WBA::Overview").name == "Overview"
    assert binding.diagram_type_for_mdgdgm("WBA::Elsewhere") is None
    assert binding.diagram_type_for_mdgdgm("WBAOther::Overview") is None
    assert binding.diagram_type_for_mdgdgm("") is None


# ---------------------------------------------------------------------------
# extends
# ---------------------------------------------------------------------------
def test_extends_inherits_what_the_child_does_not_restate(tmp_path):
    (tmp_path / "base.yaml").write_text(MINIMAL + """
presentation_profiles:
  detail: {connector_labels: true}
""", encoding="utf-8")
    (tmp_path / "house.yaml").write_text("""
technology: House
extends: WBA
stereotype_prefix: HSE_
diagram_types:
  Overview:
    grammar: lanes
    title: frame-header
    sizing:
      default: {w: 200, h: 80}
    routing:
      default: Direct
    channels:
      fill: ~
      free: []
""", encoding="utf-8")

    house = load_binding(tmp_path / "house.yaml")
    assert house.technology == "House"
    assert house.stereotype_prefix == "HSE_"
    # Restated: the child's version wins outright.
    assert house.diagram_type("Overview").grammar == "lanes"
    assert house.diagram_type("Overview").size_for() == (200, 80)
    # Not restated: inherited.
    assert "detail" in house.presentation_profiles


def test_a_child_inherits_the_parents_prefix_when_it_states_none(tmp_path):
    (tmp_path / "base.yaml").write_text(
        MINIMAL.replace("technology: WBA",
                        "technology: WBA\nstereotype_prefix: DM_"),
        encoding="utf-8")
    (tmp_path / "child.yaml").write_text(
        MINIMAL.replace("technology: WBA",
                        "technology: Child\nextends: WBA"),
        encoding="utf-8")
    assert load_binding(tmp_path / "child.yaml").stereotype_prefix == "DM_"


def test_extending_a_technology_with_no_binding_is_refused(tmp_path):
    (tmp_path / "orphan.yaml").write_text(
        MINIMAL.replace("technology: WBA",
                        "technology: Orphan\nextends: Nowhere"),
        encoding="utf-8")
    with pytest.raises(BindingError, match="Nowhere"):
        load_binding(tmp_path / "orphan.yaml")


def test_extending_itself_is_refused():
    with pytest.raises(BindingError, match="cannot extend itself"):
        load_binding_text(MINIMAL.replace("technology: WBA",
                                          "technology: WBA\nextends: WBA"))


def test_an_extends_cycle_is_refused_by_name(tmp_path):
    (tmp_path / "a.yaml").write_text(
        MINIMAL.replace("technology: WBA", "technology: A\nextends: B"),
        encoding="utf-8")
    (tmp_path / "b.yaml").write_text(
        MINIMAL.replace("technology: WBA", "technology: B\nextends: A"),
        encoding="utf-8")
    with pytest.raises(BindingError, match="cycle"):
        load_binding(tmp_path / "a.yaml")


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------
def test_a_binding_is_found_by_its_declared_id_not_its_filename(tmp_path):
    """The id is authoritative.

    Resolving by filename would let a renamed or re-slugged file bind the wrong
    technology, and composing against the wrong binding is worse than composing
    against none.
    """
    (tmp_path / "something-else.yaml").write_text(
        MINIMAL.replace("technology: WBA", "technology: Odd.Id/2"),
        encoding="utf-8")
    found = find_binding("Odd.Id/2", directory=tmp_path)
    assert found is not None and found.technology == "Odd.Id/2"


def test_an_unbound_technology_returns_none_rather_than_raising(tmp_path):
    """Most repositories use technologies nobody has bound. A caller should
    say so and fall back, not crash."""
    assert find_binding("Nothing", directory=tmp_path) is None
    assert find_binding("Nothing", directory=tmp_path / "absent") is None


def test_one_invalid_file_does_not_hide_the_valid_ones(tmp_path):
    (tmp_path / "good.yaml").write_text(MINIMAL, encoding="utf-8")
    (tmp_path / "broken.yaml").write_text("technology: Broken\n",
                                          encoding="utf-8")
    assert available_bindings(directory=tmp_path) == {"WBA": "good.yaml"}


def test_malformed_yaml_is_reported_as_such():
    with pytest.raises(BindingError, match="not valid YAML"):
        load_binding_text("technology: [unclosed\n")


def test_a_binding_cannot_carry_executable_content():
    """`safe_load`, always. A python-object tag is refused by the parser rather
    than by a check here that someone could forget to run."""
    with pytest.raises(BindingError, match="not valid YAML"):
        load_binding_text(
            "technology: !!python/object/apply:os.system ['echo hi']\n")


def test_a_document_that_is_not_a_mapping_is_refused():
    with pytest.raises(BindingError, match="expected a mapping"):
        load_binding_text("- just\n- a\n- list\n")


def test_reading_a_binding_that_is_not_there_names_the_path(tmp_path):
    with pytest.raises(BindingError, match="cannot read binding"):
        load_binding(tmp_path / "absent.yaml")


# ---------------------------------------------------------------------------
# The shipped pilots
# ---------------------------------------------------------------------------
def test_both_pilot_bindings_are_present_and_valid():
    assert available_bindings() == {"ArchiMate3": "archimate3.yaml",
                                    "BPMN2.0": "bpmn2.0.yaml"}


def test_every_shipped_binding_file_validates():
    files = sorted(_BINDINGS_DIR.glob("*.yaml"))
    assert files, "no bindings shipped"
    for path in files:
        load_binding(path)  # raises with the offending key if not


@pytest.mark.parametrize("technology,diagram_type", [
    ("ArchiMate3", "Application"),
    ("ArchiMate3", "Business"),
    ("ArchiMate3", "Technology"),
    ("ArchiMate3", "Motivation"),
    ("ArchiMate3", "Implementation"),
    ("BPMN2.0", "Business Process"),
    ("BPMN2.0", "Collaboration"),
    ("BPMN2.0", "Choreography"),
])
def test_the_technology_and_diagram_type_names_ea_actually_writes(
        technology, diagram_type):
    """Read from the MDG technology EA had loaded, and pinned.

    `BPMN2.0` is not `BPMN2`, and `Business Process` has a space in it. Both
    would have been guessed wrong, and a binding keyed on a guessed id resolves
    to nothing without complaining - so an `MDGDgm` lookup is the assertion,
    not a string comparison against the file.
    """
    binding = find_binding(technology)
    assert binding is not None
    resolved = binding.diagram_type_for_mdgdgm(
        f"{technology}::{diagram_type}")
    assert resolved is not None, (
        f"{technology}::{diagram_type} does not resolve")
    assert resolved.mdg_diagram_type == f"{technology}::{diagram_type}"


def test_the_archimate_stereotype_prefix_is_applied():
    """EA 17.1's built-in ArchiMate3 MDG prefixes its stereotype names, and the
    prefixed form is what `t_object.Stereotype` holds. Measured, and pinned
    because a reader who knows the ArchiMate specification would expect the
    bare concept name."""
    binding = find_binding("ArchiMate3")
    assert binding.stereotype_prefix == "ArchiMate_"
    assert (binding.stereotype_for("ApplicationComponent")
            == "ArchiMate_ApplicationComponent")
    assert (binding.concept_for("ArchiMate_ApplicationComponent")
            == "ApplicationComponent")


def test_bpmn_has_no_stereotype_prefix():
    binding = find_binding("BPMN2.0")
    assert binding.stereotype_prefix == ""
    assert binding.stereotype_for("Activity") == "Activity"


def test_a_stereotype_from_another_technology_passes_through_unchanged():
    """A model holds elements from other technologies and from none. A lookup
    helper is the wrong place to have an opinion about that."""
    binding = find_binding("ArchiMate3")
    assert binding.concept_for("BusinessProcess") == "BusinessProcess"
    assert binding.concept_for("") == ""


def test_bpmn_event_and_gateway_sizes_are_the_measured_ones():
    """A 110x60 "circle" is not a BPMN event.

    These are notation requirements, not preferences: the event sizes were
    unanimous or near-unanimous across 173 measured events and the gateway
    across all 61.
    """
    dt = find_binding("BPMN2.0").diagram_type("Business Process")
    assert dt.size_for() == (110, 60)
    for event in ("StartEvent", "EndEvent", "IntermediateEvent"):
        assert dt.size_for(event) == (30, 30), event
    assert dt.size_for("Gateway") == (42, 42)
    assert dt.size_for("DataObject") == (35, 50)


def test_an_unsized_concept_falls_back_to_the_default():
    dt = find_binding("BPMN2.0").diagram_type("Business Process")
    assert dt.size_for("SubProcess") == dt.size_for()
    assert dt.size_for("") == dt.size_for()


def test_archimate_claims_fill_on_every_diagram_type():
    """The finding the `channels` block exists to mechanize.

    ArchiMate's palette IS the notation. A binding that let an agent recolor
    fills by lifecycle would have broken the notation while looking like a
    feature, so this is asserted for every diagram type rather than the one
    that happened to get written first.
    """
    binding = find_binding("ArchiMate3")
    for name, dt in binding.diagram_types.items():
        assert "fill" in dt.claimed_channels(), name
        assert not dt.channel_is_free("fill"), name
        assert dt.free_channels(), f"{name} leaves nothing for a second variable"


def test_bpmn_claims_size_because_shape_carries_kind():
    for name, dt in find_binding("BPMN2.0").diagram_types.items():
        assert "size" in dt.claimed_channels(), name
        assert not dt.channel_is_free("size"), name


def test_every_shipped_diagram_type_leaves_some_channel_free():
    """A notation that claims everything gives a second variable nowhere to go,
    and a caller with nowhere to go recolors something it should not."""
    for technology in available_bindings():
        binding = find_binding(technology)
        for name, dt in binding.diagram_types.items():
            assert dt.free_channels(), f"{technology}::{name}"


def test_every_shipped_spec_composes_without_the_engine_complaining():
    """The seam, end to end, without EA.

    `compose.py` validates its spec and raises on a pitch smaller than the item
    it steps over. Running every shipped diagram type's spec through the engine
    its grammar names is how a binding with arithmetically impossible spacing
    is caught here rather than at generation time.
    """
    items = [{"id": 1, "name": "One"}, {"id": 2, "name": "Two"}]
    for technology in available_bindings():
        binding = find_binding(technology)
        for name, dt in binding.diagram_types.items():
            if not dt.grammar_is_implemented:
                continue
            spec = dt.spec()
            where = f"{technology}::{name}"
            if dt.grammar == "layered-bands":
                result = compose_layered_bands(
                    [{"name": "Band", "items": items}], spec)
            else:
                result = compose_lanes(
                    [{"name": "Lane", "items": items}], spec)
            assert len(result["items"]) == 2, where
            width, height = dt.size_for()
            for item in result["items"]:
                assert item["right"] - item["left"] == width, where
                assert item["top"] - item["bottom"] == height, where


def test_every_shipped_viewpoint_admits_something():
    """A viewpoint that admits nothing can never be selected, so it is a typo
    rather than a restriction."""
    for technology in available_bindings():
        binding = find_binding(technology)
        for name, vp in binding.viewpoints.items():
            assert vp.admits, f"{technology}::{name}"
            assert vp.intent, f"{technology}::{name} has no intent phrases"


def test_archimate_viewpoint_admits_lists_use_concepts_not_stereotypes():
    """`admits` is written the way the ArchiMate specification names things.

    Mixing the two forms in one list is the mistake the prefix design exists to
    prevent, and it would fail silently: a stereotype histogram matched against
    `ArchiMate_ApplicationComponent` in one entry and `ApplicationComponent` in
    the next would rank viewpoints on a coin toss.
    """
    binding = find_binding("ArchiMate3")
    for name, vp in binding.viewpoints.items():
        for concept in vp.admits:
            assert not concept.startswith(binding.stereotype_prefix), (
                f"{name} admits {concept!r}; use the concept name")


def test_both_pilots_define_the_same_three_presentation_profiles():
    """Presentation is a view concern, orthogonal to notation. The profiles are
    the same three in both pilots on purpose - what differs is what each
    notation has to suppress."""
    for technology in ("ArchiMate3", "BPMN2.0"):
        profiles = find_binding(technology).presentation_profiles
        assert sorted(profiles) == ["detail", "executive", "review"]
        assert profiles["executive"].collapses_parallel is True
        assert profiles["detail"].collapses_parallel is False


#: Every whole-diagram setting a profile is allowed to emit. Each was verified
#: BY RENDERING against content it could bite on -- not by writing it and
#: reading it back, which EA would echo regardless.
#:
#: `SuppressedCompartments` is deliberately absent. It was measured through six
#: value shapes against a class with attributes and operations and changed
#: nothing every time, so `compartments: none` cannot remove a compartment; it
#: reduces one to names. A profile that emitted it would promise a suppression
#: that silently does nothing.
VERIFIED_DISPLAY_SETTINGS = {
    "hide_connector_labels",
    "hide_element_stereotypes",
    "hide_connector_stereotypes",
    "hide_attribute_types",
    "hide_operation_return_types",
    "hide_operation_brackets",
    "show_element_notes",
}


def test_no_shipped_profile_promises_an_unverified_suppression():
    """A profile must not emit a setting nobody has watched EA obey.

    This list grew from two to seven once the six "unverified, not disproven"
    keys were measured against content they could actually suppress -- five
    worked, all through StyleEx. The seventh, `SuppressedCompartments`, did not,
    and is the reason this allowlist exists rather than a blanket "emit whatever
    the profile says".
    """
    for technology in available_bindings():
        binding = find_binding(technology)
        for name, profile in binding.presentation_profiles.items():
            emitted = set(profile.display_settings())
            assert emitted <= VERIFIED_DISPLAY_SETTINGS, (
                f"{technology}::{name} emits "
                f"{emitted - VERIFIED_DISPLAY_SETTINGS}")


def test_the_three_profiles_are_actually_different(): 
    """A profile scheme whose profiles emit the same settings is decoration.

    Asserted as strict progression on how much is hidden, which is the claim the
    names make: detail hides nothing, executive hides the most.
    """
    for technology in available_bindings():
        binding = find_binding(technology)
        hidden = {}
        for name in ("detail", "review", "executive"):
            settings = binding.profile(name).display_settings()
            hidden[name] = sum(1 for k, v in settings.items()
                               if v and k.startswith("hide_"))
        assert hidden["detail"] == 0, f"{technology}: detail hides something"
        assert hidden["detail"] < hidden["review"] < hidden["executive"], (
            f"{technology}: {hidden}")


def test_notes_is_the_one_setting_whose_polarity_does_not_flip():
    """EA does not draw element notes by default, so `notes: true` is a SHOW.

    Pinned because every other setting in this translation inverts, and a reader
    tidying the method for consistency would turn notes off in the detail
    profile and on in the executive one -- exactly backwards.
    """
    binding = find_binding("ArchiMate3")
    assert binding.profile("detail").display_settings()["show_element_notes"]         is True
    assert binding.profile("executive").display_settings()[
        "show_element_notes"] is False


# ---------------------------------------------------------------------------
# The layer boundary
# ---------------------------------------------------------------------------
_TECHNOLOGY_WORDS = ("archimate", "bpmn", "sysml", "togaf", "uaf", "dmn",
                     "zachman", "arcgis", "niem")


def _code_strings_in(source: str) -> list[str]:
    """Every string literal that is not a docstring, plus every name the code
    declares or uses.

    "Every name" has to mean every name, because the realistic leak is not
    `if technology == "ArchiMate3"` - it is an import or a public function that
    carries the notation in its own identifier. So the walk collects imported
    module names and aliases, function, async-function and class names,
    parameter names and keyword-argument names, not only `Name`, `Attribute`
    and string constants. Restricted to those three, the scan reports zero
    offenders for a module whose only leaks are `from archimate_tables import
    SIZES` and `def compose_archimate_bands(...)` - the two most likely ones.

    Comments and docstrings are excluded deliberately: `compose.py` is allowed
    to *mention* ArchiMate while explaining why it does not branch on it. What
    it may not do is act on the name. Note the exclusion is BY VALUE, so a
    function whose docstring were exactly `"ArchiMate3"` would also blank every
    `"ArchiMate3"` literal in the file - contrived enough to record here rather
    than engineer around.
    """
    tree = ast.parse(source)
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node, clean=False)
            if doc is not None:
                docstrings.add(doc)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value not in docstrings:
                out.append(node.value)
        elif isinstance(node, ast.Name):
            out.append(node.id)
        elif isinstance(node, ast.Attribute):
            out.append(node.attr)
        elif isinstance(node, ast.alias):
            out.append(node.name)
            if node.asname:
                out.append(node.asname)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                out.append(node.module)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                               ast.ClassDef)):
            out.append(node.name)
        elif isinstance(node, ast.arg):
            out.append(node.arg)
        elif isinstance(node, ast.keyword):
            if node.arg:
                out.append(node.arg)
    return out


def _code_strings(path: Path) -> list[str]:
    return _code_strings_in(path.read_text(encoding="utf-8"))


def _technology_offenders(strings: list[str]) -> list[str]:
    """The filter both layer-boundary tests apply, in one place.

    Shared so the synthetic-leak test below exercises the same predicate the
    real files are scanned with, rather than a paraphrase of it that could pass
    while the real one missed.
    """
    return [s for s in strings
            if any(word in s.lower() for word in _TECHNOLOGY_WORDS)]


def _imported_names(source: str) -> set[str]:
    """Every module or name an import statement brings into a namespace.

    Both halves of an import matter, and dotted paths are split. `from tools
    import bindings` and `from . import bindings as _b` name the loader in the
    *alias*, so reading only `ImportFrom.module` sees nothing; `import
    tools.bindings` hides it in a path segment.
    """
    out: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.ImportFrom) and node.module:
                out.update(node.module.split("."))
            for alias in node.names:
                out.update(alias.name.split("."))
                if alias.asname:
                    out.add(alias.asname)
    return out


# A module that leaks a notation name in every shape the scan has to reach, and
# also names notations in its docstrings, where they are allowed. Held as a
# string on purpose: nothing about this test needs a file on disk.
_LEAKY_MODULE = '''
"""A docstring may mention ArchiMate all it likes."""
from archimate_tables import SIZES
from tables import dmn_sizes
import bpmn_helpers
import plain_helpers as zachman_helpers
from .sysml_defaults import DEFAULTS


def compose_archimate_bands(spec):
    """A docstring may mention BPMN too."""
    return _apply(spec, archimate_mode=True)


def _apply(cfg, togaf_mode=False):
    return cfg.uaf_layout


async def load_niem_profile():
    return None


class BpmnLaneEngine:
    pass


TABLE = "zachman-grid"
'''

# Shape -> the name the scan must report for it. Keyed by the name so a miss
# names the shape that is invisible rather than just failing a set comparison.
_LEAK_SHAPES = {
    "archimate_tables": "the module of a `from <tech> import ...`",
    "dmn_sizes": "the name an import binds, from an innocent module",
    "bpmn_helpers": "a plain `import <tech>`",
    "zachman_helpers": "the alias an import is renamed to",
    "sysml_defaults": "the module of a relative `from .<tech> import ...`",
    "compose_archimate_bands": "a public function's own name",
    "archimate_mode": "a keyword argument at a call site",
    "togaf_mode": "a parameter in a signature",
    "uaf_layout": "an attribute being read",
    "load_niem_profile": "an async function's own name",
    "BpmnLaneEngine": "a class's own name",
    "zachman-grid": "a plain string literal",
}


def test_the_technology_name_scan_sees_every_shape_a_name_can_hide_in():
    """The test that makes the two layer-boundary tests below mean something.

    They assert an empty list. An empty list is also what a scan that looks in
    the wrong places returns, so without this the acceptance criterion could be
    "met" by a helper that sees nothing. `_LEAKY_MODULE` puts a notation name in
    each shape a real leak would take and this pins that the scan reports every
    one. Remove it and `_code_strings_in` can quietly stop visiting imports or
    function names - the shapes it originally missed - with all three tests
    still green.
    """
    offenders = set(_technology_offenders(_code_strings_in(_LEAKY_MODULE)))
    missed = {name: shape for name, shape in _LEAK_SHAPES.items()
              if name not in offenders}
    assert not missed, f"the scan cannot see a technology name in: {missed}"
    # And the deliberate exclusion still holds: docstrings may say the words.
    assert not [s for s in offenders if "docstring" in s.lower()]


def test_the_engine_contains_no_technology_name():
    """The acceptance criterion, as a test.

    A single `if technology == "ArchiMate3"` in `compose.py` - or an import,
    function or parameter named after a notation - would undo the whole design,
    new notations becoming engineering tasks again, while every other test in
    this suite still passed. The scan's reach is pinned separately above.
    """
    offenders = _technology_offenders(_code_strings(_HERE / "compose.py"))
    assert not offenders, f"compose.py acts on a technology name: {offenders}"


def test_the_loader_contains_no_technology_name_in_its_code_either():
    """The loader is allowed to document what it measured about ArchiMate and
    BPMN; it is not allowed to special-case them. Otherwise "conventions as
    data" is only true of the files."""
    offenders = _technology_offenders(_code_strings(_HERE / "bindings.py"))
    assert not offenders, f"bindings.py acts on a technology name: {offenders}"


_LOADER_IMPORT_SHAPES = (
    "import bindings",
    "import tools.bindings",
    "from bindings import load_binding",
    "from tools import bindings",
    "from . import bindings as _b",
    "from .bindings import load_binding",
)


def test_the_import_check_sees_every_shape_the_import_could_take():
    """Same reason as the scan test: `assert "bindings" not in imported` passes
    trivially against a set built the wrong way.

    The original built it from `alias.name` for `import` but only `node.module`
    for `from ... import`, so `from tools import bindings` and `from . import
    bindings as _b` - the two shapes this directory's own sys.path trick makes
    likely - were both invisible. Remove this and the boundary test below can go
    back to reading half the import.
    """
    for shape in _LOADER_IMPORT_SHAPES:
        assert "bindings" in _imported_names(shape), shape


def test_the_engine_does_not_import_the_loader():
    """The dependency runs one way: a binding is data that feeds the engine.

    Remove this and `compose.py` could grow `from . import bindings` and start
    resolving conventions itself, which is the same design failure as branching
    on a technology id with an extra indirection in front of it.
    """
    source = (_HERE / "compose.py").read_text(encoding="utf-8")
    assert "bindings" not in _imported_names(source)


def test_route_names_match_the_server():
    """Pins this file's copy of the route vocabulary. It cannot see server drift.

    `_ROUTE_STYLES` plus `_BEZIER_MODE` in `ea_mcp_server.server` are the source
    of truth, and `bindings.py` holds a copy so a typo'd route in a binding is
    caught on load rather than at write time. This test does NOT compare the
    two, and deriving it is not available: the skills bundle must not import the
    server, because a customer install has the bundle and no server source on
    the path. The set below is a second copy, written here.

    So what it catches is an edit on THIS side - a route dropped from or renamed
    in `ROUTE_NAMES`, which would make bindings using it fail to load. What it
    cannot catch is a rename on the server side, which would leave both copies
    agreeing with each other and neither with EA.

    That drift is caught in the server's own suite.
    `tests/test_apt_2026_0144_binding_generation.py` takes every route it
    applies from `find_binding(...)` rather than restating one, and asserts the
    connector EA holds carries it - so a name this copy still lists that the
    server's route table no longer resolves fails there, at generation. Those
    tests need real EA and skip without it, so the protection lands when that
    suite runs, not on every green run of this file.

    Bezier is included even though EA reaches it a different way - a binding
    author should not have to know that.
    """
    assert ROUTE_NAMES == {
        "direct", "autorouting", "customline", "treevertical",
        "treehorizontal", "lateralvertical", "lateralhorizontal",
        "orthogonalsquare", "orthogonalrounded", "bezier",
    }


def _engine_grammars() -> set[str]:
    """The grammars `compose.py` actually implements, read from `compose.py`.

    One public `compose_<grammar>` function per grammar, with underscores
    standing in for the hyphens the vocabulary uses. Read from the module rather
    than from its `__all__`, so a grammar shipped without being exported still
    counts - the question is what the engine can do, not what it advertises.
    """
    import compose

    return {
        name[len("compose_"):].replace("_", "-")
        for name in dir(compose)
        if name.startswith("compose_") and callable(getattr(compose, name))
    }


def test_the_grammar_vocabulary_matches_what_the_engine_implements():
    """Four grammars; which of them are composable is read from `compose.py`.

    The flag in `GRAMMARS` is what a consumer trusts before it composes, so it
    has to be the engine's answer and not a remembered one. Comparing
    `IMPLEMENTED_GRAMMARS` to a set written here would have stayed green the day
    `compose_nested_grid` shipped - which is exactly the day a consumer should
    stop falling back to a plain graph layout for capability maps. Remove this
    and that lag becomes invisible.

    The four names themselves stay a literal: "the variety of real diagrams
    resolves into these four" is a finding, and a fifth appearing is a change to
    review rather than a set to follow.
    """
    assert set(GRAMMARS) == {"layered-bands", "lanes", "nested-grid",
                             "computed-geometry"}
    assert IMPLEMENTED_GRAMMARS == _engine_grammars()
    assert CHANNELS >= {"fill", "border", "opacity", "icon"}


# ---------------------------------------------------------------------------
# The cross-check the item asked for
# ---------------------------------------------------------------------------
def test_every_behavioral_difference_between_the_pilots_is_data():
    """The schema's real test: the two pilots are maximally different
    notations, and diffing them must account for every difference in behavior.

    Each assertion below is a way the two notations genuinely diverge, read
    from the loaded bindings. If any of them started coming from code instead,
    the value of the data layer would be gone - which is why this is one test
    listing all of them rather than several that could each be satisfied by a
    special case.
    """
    archimate = find_binding("ArchiMate3")
    bpmn = find_binding("BPMN2.0")

    # 1. Stereotype naming: prefixed against bare.
    assert archimate.stereotype_prefix == "ArchiMate_"
    assert bpmn.stereotype_prefix == ""

    # 2. Title convention: drawn against the diagram frame. Measured 13/13 and
    #    10/11 in the corpus, and the split tracks notation.
    assert all(dt.draws_its_own_title
               for dt in archimate.diagram_types.values())
    assert not any(dt.draws_its_own_title
                   for dt in bpmn.diagram_types.values())

    # 3. Grammar: stratified layers against lanes and flow.
    assert {dt.grammar for dt in archimate.diagram_types.values()} \
        == {"layered-bands"}
    assert {dt.grammar for dt in bpmn.diagram_types.values()} == {"lanes"}

    # 4. Sizing: one box size for nearly everything against a size per node
    #    kind, because BPMN shapes are not interchangeable.
    assert len(archimate.diagram_type("Application").sizing) < len(
        bpmn.diagram_type("Business Process").sizing)

    # 5. Spacing. Asserted on the keys each grammar ACTUALLY READS, which is not
    #    the same set. `compose_lanes` never reads `item_gap_x` or `item_gap_y`,
    #    so comparing those two across the pilots -- which an earlier version of
    #    this test did, calling it the headline difference -- compares numbers
    #    that cannot affect a composed BPMN diagram. They are kept in the binding
    #    as recorded measurements and the binding says so; they are not behavior.
    archimate_dt = archimate.diagram_type("Application")
    bpmn_dt = bpmn.diagram_type("Business Process")
    #    Bands: ArchiMate's own two axes differ, measured at ~75 against ~40.
    assert archimate_dt.spacing["item_gap_x"] > archimate_dt.spacing["item_gap_y"]
    #    Lanes: the load-bearing key is the one along the flow.
    assert bpmn_dt.spacing["item_gap_flow"] > 0
    assert "item_gap_flow" not in archimate_dt.spacing
    #    Pools abut; ArchiMate bands do not. Asserted on COMPOSED geometry,
    #    because `archimate3.yaml` deliberately does not set `band_gap` -- band
    #    gutters were never separately measured, so the engine default stands
    #    rather than a number nobody observed. Neither `.spacing` (the raw
    #    binding block) nor `.spec()` (which carries only what the binding
    #    states, leaving the engine to fill the rest) reports it, so a constant
    #    would be the wrong thing to read: what matters is that the bands come
    #    out apart and the lanes come out touching.
    assert bpmn_dt.spacing["lane_gap"] == 0
    assert "band_gap" not in archimate_dt.spacing

    two = [{"name": "Upper", "items": [{"id": 1}]},
           {"name": "Lower", "items": [{"id": 2}]}]
    bands = sorted(compose_layered_bands(two, archimate_dt.spec())["containers"],
                   key=lambda c: -c["top"])
    assert bands[0]["bottom"] > bands[1]["top"], (
        "ArchiMate bands abut; they should have a gutter between them")

    lanes = sorted(compose_lanes(two, bpmn_dt.spec())["containers"],
                   key=lambda c: -c["top"])
    assert lanes[0]["bottom"] == lanes[1]["top"], (
        "BPMN pools have a gutter; they should abut")

    # 6. Trunking: ArchiMate fans relationships into a shared trunk; BPMN does
    #    not, because its gateways make branching an explicit node.
    assert archimate.diagram_type("Application").routing["trunk_for"]
    assert "trunk_for" not in bpmn.diagram_type("Business Process").routing

    # 7. Claimed channels: both claim fill, for different reasons, and BPMN
    #    additionally claims size.
    assert "size" in bpmn.diagram_type("Business Process").claimed_channels()
    assert "layer" in archimate.diagram_type(
        "Application").claimed_channels()["fill"].lower()

    # 8. Viewpoint catalog: ArchiMate publishes one, BPMN does not. An empty
    #    catalog is a fact about the notation, not a gap in the binding.
    assert len(archimate.viewpoints) >= 12
    assert bpmn.viewpoints == {}

    # 9. Coverage: BPMN deliberately leaves two of its five diagram types
    #    unbound, because a conversation diagram is a graph and BPEL is an
    #    export format. Refusing to bind them is the honest answer.
    assert bpmn.diagram_type_for_mdgdgm("BPMN2.0::Conversation") is None
    assert bpmn.diagram_type_for_mdgdgm("BPMN2.0::BPEL") is None

    # 10. And the base diagram type EA creates them from differs.
    assert archimate.diagram_type("Application").base == "Logical"
    assert bpmn.diagram_type("Business Process").base == "Analysis"
