#!/usr/bin/env python3
"""The StrategyMap and MindMapping bindings, pinned against the model they came from.

Run from the repository root:

    python -m pytest ea-diagram-composition/tools/test_bindings_strategy.py -q

WHY THESE TWO ARE IN ONE FILE. Both were authored from one finding: the corpus
audit classifies their rows as `Custom` with the reason "Custom has no MDG
technology, so there is nothing to bind", and for these rows that reason is
false. EA registers `StrategyMap` and `MindMapping` as MDG technologies and the
reference model carries 19 and 4 diagrams of them. The tests below are the
finding's evidence kept runnable.

THE TESTS THAT MATTER MOST ARE THE PROVENANCE ONES. Every size and gap in the
two YAML documents is RE-MEASURED here from the model and compared, so a figure
that was never measured - or one that drifts when the model or the tool changes -
fails rather than shipping as authoritative. A fabricated spacing figure has
shipped in this directory before, matching nothing in the model it claimed to
come from, and `test_every_stated_number_is_the_measured_one` is what makes that
particular mistake impossible to repeat.

THE SECOND GROUP IS ABOUT WHAT IS ABSENT. `MIN_SAMPLE` exists to be obeyed, and
a slot left out inherits a measured value from the substrate, which is honest,
while a guessed slot is a wrong value that looks authoritative. So the omissions
are pinned too: `test_no_slot_the_tool_refuses_is_stated` asserts that nothing
either file states was refused by the tool, and the per-type tests name the
specific figures that were left on the floor and why.

A NOTE ON WHAT IS NOT TESTED HERE. That the two technology ids are CLAIMED by a
corpus family lives on the product side, in
`tests/benchmark/test_binding_coverage.py::test_the_shipped_bindings_are_all_claimed_and_all_load`,
because the family table is the benchmark's data and this bundle does not import
the product. Adding the ids to `FAMILIES` is what makes that test pass; nothing
here can see it.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import measure_binding as mb  # noqa: E402
from bindings import (  # noqa: E402
    GRAMMARS,
    find_binding,
    load_binding,
    resolve_diagram,
)

#: Technology ids exactly as `measure_binding.py --list` reports them. Pinned as
#: constants because an id is not guessable and a lookup on a guessed one
#: resolves to nothing without complaining.
STRATEGY = "StrategyMap"
MINDMAP = "MindMapping"

#: The four StrategyMap diagram types that are bound, and the two that are not.
STRATEGY_BOUND = ("StrategyMap", "DecisionTree", "OrgChart", "ValueChain")
STRATEGY_UNBOUND = ("BalancedScorecard", "FlowChart")

#: The EA base diagram type each bound type is drawn on, read from the model.
EXPECTED_BASES = {
    (STRATEGY, "StrategyMap"): "Logical",
    (STRATEGY, "DecisionTree"): "Analysis",
    (STRATEGY, "OrgChart"): "Logical",
    (STRATEGY, "ValueChain"): "Logical",
    (MINDMAP, "MindMapping"): "Analysis",
}

#: Every number either document states, as `(technology, diagram type) -> slots`.
#: This is the provenance table: each entry is re-measured below.
STATED_SIZES = {
    (STRATEGY, "StrategyMap"): {"default": (90, 60)},
    (STRATEGY, "DecisionTree"): {"default": (90, 50)},
    (STRATEGY, "OrgChart"): {"default": (90, 54)},
    (STRATEGY, "ValueChain"): {"default": (400, 50),
                               "VC_PrimaryActivity": (80, 100)},
    (MINDMAP, "MindMapping"): {"default": (90, 40)},
}
STATED_GAPS = {
    (STRATEGY, "StrategyMap"): {},
    (STRATEGY, "DecisionTree"): {},
    (STRATEGY, "OrgChart"): {"item_gap_x": 47, "item_gap_y": 59},
    (STRATEGY, "ValueChain"): {},
    (MINDMAP, "MindMapping"): {"item_gap_x": 70, "item_gap_y": 59},
}

#: The `StrategyMap::StrategyMap` default rests on a STATED SELECTION rather than
#: on the tool's default pool, because that pool has no unique mode: 650x200 (the
#: four perspective bands) and 90x60 (an attribute box) each occur 14 times. The
#: selection excludes the bands - which a bands composition does not size as items
#: - and EA's own navigation tiles. Kept here so the test measures the same thing
#: the YAML comment claims.
STRATEGY_MAP_BANDS = frozenset({
    "SM_FinancialPerspective",
    "SM_CustomerPerspective",
    "SM_InternalPerspective",
    "SM_LearningAndGrowthPerspective",
})
NOT_A_CONCEPT = frozenset({"NavigationCell"})

_BINDINGS = _HERE.parent / "bindings"

MODEL = mb.resolve_model_path(None)

needs_model = pytest.mark.skipif(
    MODEL is None,
    reason=("EAExample.qea not found - pass its location in "
            f"{mb.MODEL_ENV_VAR}; a machine without EA has nothing to measure"),
)


@pytest.fixture(scope="module")
def model():
    """Diagrams and the technology index, loaded once from a private copy."""
    with mb.open_model_copy(MODEL) as conn:
        return mb._load_diagrams(conn), mb.list_technologies(conn)


def measure(model, technology, diagram_type):
    diagrams, known = model
    return mb.measure_diagrams(diagrams, known, technology, diagram_type)


@pytest.fixture(scope="module")
def strategy():
    return find_binding(STRATEGY, _BINDINGS)


@pytest.fixture(scope="module")
def mindmap():
    return find_binding(MINDMAP, _BINDINGS)


def binding_for(strategy, mindmap, technology):
    return strategy if technology == STRATEGY else mindmap


ALL_TYPES = sorted(EXPECTED_BASES)


# ---------------------------------------------------------------------------
# 1. The premise. The technologies are real and the diagrams are theirs.
# ---------------------------------------------------------------------------
@needs_model
def test_both_technologies_are_registered_in_the_model(model):
    """The finding's first claim: these ids exist. They were reported as `Custom`,
    which is the family for "no MDG technology, so nothing to bind"."""
    _, known = model
    assert STRATEGY in known, sorted(known)
    assert MINDMAP in known, sorted(known)


@needs_model
def test_the_model_declares_the_diagram_types_the_bindings_name(model):
    _, known = model
    assert set(known[STRATEGY]) == set(STRATEGY_BOUND) | set(STRATEGY_UNBOUND)
    assert set(known[MINDMAP]) == {"MindMapping"}


@needs_model
@pytest.mark.parametrize("key", ALL_TYPES, ids=lambda k: f"{k[0]}::{k[1]}")
def test_every_bound_diagram_type_has_diagrams_of_its_own(model, key):
    technology, diagram_type = key
    m = measure(model, technology, diagram_type)
    assert m.diagrams > 0
    # By the MDG tag, never by the fallback: these diagrams SAY what they are, so
    # the binding is not resting on an inference about them.
    assert m.diagrams_by_mdg == m.diagrams
    assert m.diagrams_by_fallback == 0


@needs_model
def test_the_stereotype_vocabulary_is_the_notation_the_corpus_rows_describe(model):
    """THE PREMISE CHECK, per row. A binding authored on a resemblance is worse
    than none, so each type's vocabulary is read from the model and matched to
    what the catalog says the row is made of - not to the diagram type's name.
    """
    diagrams, known = model
    vocabulary = {}
    for d in diagrams.values():
        if d.technology in (STRATEGY, MINDMAP):
            vocabulary.setdefault((d.technology, d.diagram_type), set()).update(
                it.concept for it in d.items if it.concept)

    # strategy-map.png: "band header labels ... 5 fill colors", encoding
    # "perspective". The bands are the perspectives, and there are four of them.
    strategy_map = vocabulary[(STRATEGY, "StrategyMap")]
    assert STRATEGY_MAP_BANDS <= strategy_map
    assert {"SM_Objective", "SM_Attribute", "SM_Process"} <= strategy_map

    # decision-tree.png: "yellow=test orange=outcome".
    tree = vocabulary[(STRATEGY, "DecisionTree")]
    assert "DT_Test" in tree
    assert {"DT_OutcomeActivity", "DT_OutcomeObject"} & tree

    # organizational-chart.png: "classic org tree ... uniform boxes".
    assert vocabulary[(STRATEGY, "OrgChart")] == {"OC_Role"}

    # value-chain.png: "CHEVRON/arrow custom shapes; large outer arrow outline".
    assert {"VC_PrimaryActivity", "VC_SupportActivity", "VC_GrossSales"} == \
        vocabulary[(STRATEGY, "ValueChain")]

    # mind-mapping.png: "colored rounded nodes; central spine".
    mind = vocabulary[(MINDMAP, "MindMapping")]
    assert {"CentralTopic", "MainTopic", "Topic", "SubTopic"} <= mind


@needs_model
def test_every_mind_map_has_exactly_one_central_topic(model):
    """What makes `radial-tree` the right grammar rather than a guess: there is a
    hub, one per diagram, which is the thing the composer places at the center."""
    diagrams, _ = model
    found = [d for d in diagrams.values() if d.technology == MINDMAP]
    assert len(found) == 4
    for d in found:
        centers = [it for it in d.items if it.concept == "CentralTopic"]
        assert len(centers) == 1, d.name


@needs_model
def test_the_value_chain_carries_no_connectors(model):
    """Why `routing.default` on ValueChain is stated and never applies, and why
    both its gap populations are n=0 rather than thin."""
    m = measure(model, STRATEGY, "ValueChain")
    assert m.h_gap.n == 0 and m.v_gap.n == 0
    # Pairs were FOUND and every one was rejected as touching or overlapping,
    # which is the chevron abutment rather than an absence of neighbors.
    assert m.non_positive_h > 0 and m.non_positive_v > 0


# ---------------------------------------------------------------------------
# 2. Provenance. Never write a number you did not measure.
# ---------------------------------------------------------------------------
@needs_model
@pytest.mark.parametrize("key", ALL_TYPES, ids=lambda k: f"{k[0]}::{k[1]}")
def test_every_stated_number_is_the_measured_one(model, strategy, mindmap, key):
    technology, name = key
    binding = binding_for(strategy, mindmap, technology)
    bound = binding.diagram_types[name]
    m = measure(model, technology, name)

    # `own_sizing` / `own_spacing`, not the resolved pair: a figure is only this
    # technology's measurement if this document stated it, and the resolved values
    # carry the substrate's.
    assert {k: (v["w"], v["h"]) for k, v in bound.own_sizing.items()} == \
        STATED_SIZES[key]
    assert dict(bound.own_spacing) == STATED_GAPS[key]

    for concept, expected in STATED_SIZES[key].items():
        if concept == "default":
            continue
        stat = m.sizes[concept]
        assert stat.mode == expected, concept
        assert not stat.low_n, concept

    for axis, expected in STATED_GAPS[key].items():
        stat = m.h_gap if axis == "item_gap_x" else m.v_gap
        assert round(stat.median) == expected, axis
        assert not stat.low_n and not stat.concentrated, axis


@needs_model
def test_three_of_the_four_defaults_are_the_tools_own_pooled_mode(model,
                                                                 strategy,
                                                                 mindmap):
    """The ordinary case: the default is what `measure_binding.py` hands over."""
    for key in [(STRATEGY, "DecisionTree"), (STRATEGY, "OrgChart"),
                (STRATEGY, "ValueChain"), (MINDMAP, "MindMapping")]:
        technology, name = key
        binding = binding_for(strategy, mindmap, technology)
        stated = binding.diagram_types[name].own_sizing["default"]
        m = measure(model, technology, name)
        assert m.default_size is not None, key
        assert not m.default_size.low_n, key
        assert m.default_size.mode == (stated["w"], stated["h"]), key


@needs_model
def test_the_strategy_map_default_is_measured_over_the_selection_it_claims(
        model, strategy):
    """The one figure that is NOT the tool's default pool, and why.

    The pooled mode over all 86 elements is a TIE - 650x200 fourteen times and
    90x60 fourteen times - so rule 1 refuses it and the tool reports no unique
    mode. Excluding the four perspective BANDS, which a bands composition does
    not size as items, and EA's navigation tiles leaves a unique mode. Measured
    with the tool's own `size_stat` over that selection, which is how the UML
    file's figures were produced too.
    """
    diagrams, _ = model
    m = measure(model, STRATEGY, "StrategyMap")
    assert m.default_size.mode is None, "the pooled mode should still be a tie"

    sizes, band_sizes = [], []
    for d in diagrams.values():
        if d.technology != STRATEGY or d.diagram_type != "StrategyMap":
            continue
        for it in d.items:
            if not it.concept:
                continue
            size = (it.rect.width, it.rect.height)
            if it.concept in STRATEGY_MAP_BANDS:
                band_sizes.append(size)
            elif it.concept not in NOT_A_CONCEPT:
                sizes.append(size)

    stat = mb.size_stat(sizes)
    assert not stat.low_n
    assert stat.n == 63
    stated = strategy.diagram_types["StrategyMap"].own_sizing["default"]
    assert stat.mode == (stated["w"], stated["h"])

    # And the other half of the tie, which the YAML records and deliberately does
    # not state: the bands are 650x200, the strongest figure on this diagram type
    # and four observations short of the threshold per stereotype.
    bands = mb.size_stat(band_sizes)
    assert bands.mode == (650, 200) and bands.n == 20
    for concept in STRATEGY_MAP_BANDS:
        assert m.sizes[concept].low_n, concept
        assert concept not in strategy.diagram_types["StrategyMap"].own_sizing


# ---------------------------------------------------------------------------
# 3. The omissions. MIN_SAMPLE exists to be obeyed.
# ---------------------------------------------------------------------------
@needs_model
@pytest.mark.parametrize("key", ALL_TYPES, ids=lambda k: f"{k[0]}::{k[1]}")
def test_no_slot_the_tool_refuses_is_stated(model, strategy, mindmap, key):
    """Nothing low-n, tied or concentrated is written down as a convention.

    The mirror of the provenance test, and the one that catches the tempting
    mistake: an unanimous n=4 size looks like a fact and is four observations
    short of being one.
    """
    technology, name = key
    binding = binding_for(strategy, mindmap, technology)
    bound = binding.diagram_types[name]
    m = measure(model, technology, name)

    for concept, stat in m.sizes.items():
        if concept not in bound.own_sizing:
            continue
        assert not stat.low_n, f"{name}.{concept} is low-n and was stated"
        assert stat.mode is not None, f"{name}.{concept} has no unique mode"

    for axis, stat in (("item_gap_x", m.h_gap), ("item_gap_y", m.v_gap)):
        if axis in bound.own_spacing:
            assert not stat.low_n, f"{name}.{axis}"
            assert not stat.concentrated, f"{name}.{axis}"
        else:
            assert stat.low_n or stat.concentrated or stat.n == 0, (
                f"{name}.{axis} was measurable and is not stated")


@needs_model
def test_an_omitted_gap_inherits_a_measured_value_rather_than_an_engine_default(
        strategy, mindmap):
    """Why leaving a slot out is the correct answer and not a failure.

    Three of the five bound diagram types state no gaps at all. What answers in
    their place is the measured spacing of the UML diagram type each is drawn on,
    not the engine's inoffensive 20 - which is the whole value of `extends`.
    """
    uml = load_binding(_BINDINGS / "uml.yaml")
    for technology, name in [(STRATEGY, "StrategyMap"),
                             (STRATEGY, "DecisionTree"),
                             (STRATEGY, "ValueChain")]:
        bound = binding_for(strategy, mindmap, technology).diagram_types[name]
        assert bound.own_spacing == {}
        substrate = uml.diagram_types[bound.base]
        assert bound.spacing == substrate.spacing
        assert bound.substrate == f"UML::{bound.base}"
        assert bound.spacing, "the substrate should have stated gaps"


@needs_model
def test_the_two_unbound_strategy_types_have_no_statable_default(model):
    """BalancedScorecard and FlowChart are left out, and here is the arithmetic.

    Recorded as a test because an omission is otherwise indistinguishable from an
    oversight, and because either one would be easy to add with a number the tool
    refused to produce.
    """
    scorecard = measure(model, STRATEGY, "BalancedScorecard")
    # Unanimous and four observations short: 150x150 in 4 of 4.
    assert scorecard.default_size.mode == (150, 150)
    assert scorecard.default_size.low_n
    assert scorecard.default_size.n < mb.MIN_SAMPLE

    flow = measure(model, STRATEGY, "FlowChart")
    # Enough observations, and no unique mode: 74x45 and 100x70 tie at 6 each.
    assert flow.default_size.n >= mb.MIN_SAMPLE
    assert flow.default_size.mode is None

    for name in STRATEGY_UNBOUND:
        assert name not in find_binding(STRATEGY, _BINDINGS).diagram_types


@needs_model
def test_the_central_topic_is_the_omission_the_mind_map_notes_name(model):
    m = measure(model, MINDMAP, "MindMapping")
    central = m.sizes["CentralTopic"]
    assert central.low_n and central.n == 4
    # SubTopic is the other absence, and for the other reason: enough of them,
    # no dominant size, because a sub-topic is sized by the text it carries.
    sub = m.sizes["SubTopic"]
    assert not sub.low_n
    assert sub.mode_share < mb.DOMINANT_SHARE


# ---------------------------------------------------------------------------
# 4. The base notation, and the one-level inheritance constraint
# ---------------------------------------------------------------------------
@needs_model
@pytest.mark.parametrize("key", ALL_TYPES, ids=lambda k: f"{k[0]}::{k[1]}")
def test_every_base_is_read_from_the_model_and_unanimous(model, strategy,
                                                         mindmap, key):
    """`base` names the real EA `Diagram_Type`, and every diagram of the type
    agrees. Not guessed: a base nobody checked leaves the substrate silently
    absent, which is the failure the UML binding exists to prevent."""
    diagrams, _ = model
    technology, name = key
    observed = {d.base_type for d in diagrams.values()
                if d.technology == technology and d.diagram_type == name}
    expected = EXPECTED_BASES[key]
    # `_load_diagrams` lowercases the base type; the binding spells it as EA does.
    assert observed == {expected.lower()}, key
    assert binding_for(strategy, mindmap, technology).diagram_types[name].base \
        == expected


def test_the_bases_are_declared_by_the_parent_so_nothing_falls_through(strategy,
                                                                      mindmap):
    uml = load_binding(_BINDINGS / "uml.yaml")
    for binding in (strategy, mindmap):
        assert binding.extends == "UML"
        for bound in binding.diagram_types.values():
            assert bound.base in uml.diagram_types, bound.base
            assert bound.substrate == f"UML::{bound.base}"


def test_one_technology_sits_on_two_bases_which_is_why_base_is_per_type(strategy):
    """StrategyMap's own types split across `Logical` and `Analysis`, so a single
    `extends` could not have carried the substrate."""
    bases = {b.base for b in strategy.diagram_types.values()}
    assert bases == {"Logical", "Analysis"}


def test_extending_a_sibling_technology_would_inherit_nothing(tmp_path):
    """THE CONSTRAINT THAT DECIDED THE PARENT, verified rather than taken on trust.

    `_merge` does not union a parent's diagram types into the child's catalog and
    `_on_substrate` resolves `base` against the IMMEDIATE parent's catalog, so a
    chain deeper than one level finds no substrate and silently inherits nothing.
    Both new bindings therefore extend the ROOT. The failure is silent, which is
    why it is pinned here and not left as a comment.
    """
    def document(technology, extends, name, base):
        head = f"technology: {technology}\n"
        if extends:
            head += f"extends: {extends}\n"
        return head + (
            f"diagram_types:\n"
            f"  {name}:\n"
            + (f"    base: {base}\n" if base else "")
            + "    grammar: graph\n"
              "    title: frame-header\n"
              "    sizing: {default: {w: 90, h: 60}}\n"
              "    spacing: {}\n"
              "    routing: {default: Direct}\n"
              "    channels: {fill: ~, free: [fill]}\n")

    (tmp_path / "alpha.yaml").write_text(
        document("Alpha", None, "Logical", None).replace(
            "    spacing: {}\n", "    spacing: {item_gap_x: 77, item_gap_y: 88}\n"),
        encoding="utf-8", newline="\n")
    (tmp_path / "beta.yaml").write_text(
        document("Beta", "Alpha", "MidType", "Logical"),
        encoding="utf-8", newline="\n")
    (tmp_path / "overlay.yaml").write_text(
        document("Overlay", "Beta", "LeafType", "Logical"),
        encoding="utf-8", newline="\n")

    one_level = load_binding(tmp_path / "beta.yaml").diagram_types["MidType"]
    assert one_level.substrate == "Alpha::Logical"
    assert one_level.spacing == {"item_gap_x": 77, "item_gap_y": 88}

    two_levels = load_binding(tmp_path / "overlay.yaml").diagram_types["LeafType"]
    assert two_levels.substrate == ""
    assert two_levels.spacing == {}


# ---------------------------------------------------------------------------
# 5. Grammars, and the ones that were wanted
# ---------------------------------------------------------------------------
def test_every_grammar_is_in_the_vocabulary_and_producible(strategy, mindmap):
    for binding in (strategy, mindmap):
        for bound in binding.diagram_types.values():
            assert bound.grammar in GRAMMARS, bound.grammar
            assert bound.grammar_is_producible, bound.name


def test_a_composed_grammar_is_used_only_where_the_notation_imposes_one(strategy,
                                                                       mindmap):
    """Two of the five reach for a composed grammar and three do not, and the
    split is the point: `graph` is the usual honest answer for a tree EA's own
    layout places, and a composed grammar is claimed only where the notation's
    own figure is structural."""
    composed = {name: b.grammar for name, b in strategy.diagram_types.items()
                if b.geometry_is_composed}
    composed.update({name: b.grammar for name, b in mindmap.diagram_types.items()
                     if b.geometry_is_composed})
    assert composed == {
        # Perspective bands, one per band, and moving an objective between them
        # means something.
        "StrategyMap": "layered-bands",
        # Interlocking stages; EA's layout has no connectors to work from.
        "ValueChain": "chevron-stack",
        # A hub with branches of unequal weight below it.
        "MindMapping": "radial-tree",
    }
    # And the two trees are `graph`, not a composed grammar bent to fit. The
    # corpus calls them `tree-td` and `tree-lr`; neither name is in the
    # vocabulary, and inventing one to hold them would be a finding stored as
    # data.
    assert strategy.diagram_types["OrgChart"].grammar == "graph"
    assert strategy.diagram_types["DecisionTree"].grammar == "graph"
    for wanted in ("tree-td", "tree-lr"):
        assert wanted not in GRAMMARS


def test_the_composed_grammars_used_here_all_have_a_composer(strategy, mindmap):
    """Not a given: `computed-geometry` is in the vocabulary with nothing behind
    it, so a binding can name a grammar that cannot be composed. None of these
    does."""
    for binding in (strategy, mindmap):
        for bound in binding.diagram_types.values():
            if bound.geometry_is_composed:
                assert bound.grammar_is_implemented, bound.name


# ---------------------------------------------------------------------------
# 6. The prefix decision, and resolution
# ---------------------------------------------------------------------------
@needs_model
def test_strategy_map_has_a_prefix_per_diagram_type_not_per_technology(model):
    """WHY `stereotype_prefix` IS EMPTY IN A FILE WHOSE STEREOTYPES ARE PREFIXED.

    Six diagram types, six different prefixes, one slot in the schema. Any single
    value would make every lookup on the other five miss - silently. So the
    prefix is the empty statement and the `sizing` keys are spelled as EA stores
    them. This test is the evidence for that choice; if the schema ever grows a
    per-diagram-type prefix, this is the test that says what to fill it with.
    """
    prefixes = {}
    for name in tuple(STRATEGY_BOUND) + tuple(STRATEGY_UNBOUND):
        prefixes[name] = measure(model, STRATEGY, name).stereotype_prefix
    assert prefixes == {
        "StrategyMap": "SM_", "DecisionTree": "DT_", "OrgChart": "OC_",
        "ValueChain": "VC_", "BalancedScorecard": "BS_", "FlowChart": "FC_",
    }
    assert len(set(prefixes.values())) == 6

    # The mind map is the opposite case and is stated for the ordinary reason:
    # its stereotypes really are bare, so `""` is a measurement there.
    assert measure(model, MINDMAP, "MindMapping").stereotype_prefix == ""


def test_the_empty_prefix_round_trips_the_stored_names(strategy, mindmap):
    """The combination that makes the choice above correct rather than merely
    harmless: with no prefix, a `sizing` key spelled as EA stores it maps to
    itself in both directions."""
    assert strategy.stereotype_prefix == ""
    for concept in strategy.diagram_types["ValueChain"].own_sizing:
        if concept == "default":
            continue
        assert strategy.stereotype_for(concept) == concept
        assert strategy.concept_for(concept) == concept
    assert mindmap.stereotype_prefix == ""


@needs_model
def test_every_tagged_diagram_of_a_bound_type_resolves_exactly(model, strategy,
                                                               mindmap):
    """Resolution through the `qualified` path, for real StyleEx values.

    These diagrams state `MDGDgm=<Tech>::<DiagramType>` themselves, so nothing is
    inferred - which is the strongest confidence the resolver reports.
    """
    diagrams, _ = model
    installed = {STRATEGY, MINDMAP}
    catalog = {STRATEGY: strategy, MINDMAP: mindmap}
    seen = 0
    for d in diagrams.values():
        if d.technology not in installed:
            continue
        key = f"{d.technology}::{d.diagram_type}"
        resolution = resolve_diagram(
            installed, style_ex=f"MDGDgm={key};", diagram_type=d.raw_type,
            bindings=catalog)
        if d.diagram_type in STRATEGY_UNBOUND:
            # Deliberately unbound, and the resolver says so rather than falling
            # through to a sibling diagram type of the same technology.
            assert resolution.path == "unbound", key
            continue
        assert resolution.path == "qualified", key
        assert resolution.confidence == "exact"
        assert resolution.key == key
        seen += 1
    assert seen == 19 + 4 - 1 - 3  # 23 tagged diagrams less the 4 unbound ones


@needs_model
def test_neither_binding_makes_another_diagram_type_ambiguous(model, strategy,
                                                              mindmap):
    """The regression these two could have caused and do not.

    `resolve_diagram` matches a `Diagram_Type` against bound diagram type NAMES,
    so two bindings declaring one name make every diagram carrying it ambiguous.
    Checked against every binding on disk rather than against a list, so a
    binding another author adds is included the day it lands.
    """
    from bindings import available_bindings

    claimed = {}
    for technology in available_bindings(_BINDINGS):
        binding = find_binding(technology, _BINDINGS)
        for name in binding.diagram_types:
            claimed.setdefault(name, []).append(technology)
    for binding in (strategy, mindmap):
        for name in binding.diagram_types:
            assert claimed[name] == [binding.technology], \
                f"{name} is claimed by {claimed[name]}"


# ---------------------------------------------------------------------------
# 7. House rules the build gate enforces
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("filename", ["strategymap.yaml", "mindmapping.yaml"])
def test_the_documents_are_lf_only_and_carry_no_local_paths(filename):
    raw = (_BINDINGS / filename).read_bytes()
    assert b"\r" not in raw
    text = raw.decode("utf-8")
    for forbidden in (":\\", "C:/", "%APPDATA%", "Users\\"):
        assert forbidden not in text, forbidden
