#!/usr/bin/env python3
"""The data-and-decision bindings: ERD, DMN, and the one that is NOT shipped.

Three notations were taken together because they are the same kind of problem -
small, EA-placed, data-shaped diagram types - and they came out three different
ways. This file pins all three, including the refusal:

  `ERD`       two diagrams in the reference model, whose tokens start `ERD_dp`.
              Bound, with its entity size and both item gaps deliberately unstated.
  `DMN1.1`    thirty-one diagrams. Bound, and the only binding in the tree whose
              gap populations are spread thinly enough across diagrams to state
              without a caveat about concentration.
  the data-modeling technology
              NOT bound, and `test_the_data_modeling_technology_is_deliberately
              _unbound_and_why` is the reason, derived from the tool rather than
              asserted. A table has no convention size, `sizing.default` is
              mandatory, and a mandatory slot nobody can measure is a diagram
              type that must not be keyed. Without this test the absence of a
              file is indistinguishable from nobody having got round to it.

EVERY FIGURE IS DERIVED, NOT RESTATED. The expected values come from
`measure_binding.py` run against the same model the bindings were authored from,
so re-measuring moves the test and the binding together. What IS written down
here are the ids, the diagram type names and the classifications - the facts a
binding cannot derive and would otherwise guess.

A SEPARATE FILE ON PURPOSE. `test_bindings.py` holds the schema suite and the
per-notation sections that came before these; two authors appending to one file
has already collided in this tree, so this one is added beside it rather than
into it.
"""
from __future__ import annotations

# No backlog item is pinned: these tests cover designed behavior, not a filed defect.
PINS = ()

import re
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_BINDINGS_DIR = _HERE.parent.parent / "_shared" / "languages"

import measure_binding as mb  # noqa: E402
from bindings import (  # noqa: E402
    DiagramTypeBinding,
    EA_PLACED_GRAMMARS,
    GRAMMARS,
    MDG_SEPARATOR,
    PLACED_BY_EA,
    available_bindings,
    find_binding,
    implemented_grammars,
    producible_grammars,
    resolve_diagram,
)
from compose import DEFAULT_SPEC  # noqa: E402

# ---------------------------------------------------------------------------
# The ids, read from the model's own `MDGDgm` values and written down here
# because they are not derivable and not guessable.
# ---------------------------------------------------------------------------
_ERD = "ERD"
#: What the stored token starts with. The model's inventory is keyed by this, not by
#: the id EA reports.
_ERD_GROUP = "ERD_dp"
_ERD_TYPE = "ERD_DP"
_ERD_FILE = "data-modeling-er/conventions.yaml"
_ERD_BASE = "Logical"

_DMN = "DMN1.1"
_DMN_TYPE = "DMNDiagram"
_DMN_FILE = "dmn-1/conventions.yaml"
_DMN_BASE = "Analysis"

#: The data-modeling family. Its technology id is EA's own built-in diagram-set
#: id, which carries five other diagram types this work has no opinion about; the
#: one in scope is the data model. Deliberately unbound - see the test.
_DATA = "Extended"
_DATA_TYPE = "Data Modeling"

#: Names somebody would plausibly guess, none of which starts a stored token, so a
#: token built on one resolves to nothing at all. The family names are what EA's own
#: user interface calls these notations, and `ERD` is also the id EA reports.
_GUESSED = ("ERD", "ERD_DP", "erd", "DMN", "DMN1.0", "DMN1.1.1", "DataModel",
            "Data Modeling")

_BOUND = ((_ERD, _ERD_TYPE, _ERD_BASE), (_DMN, _DMN_TYPE, _DMN_BASE))
_IDS = (_ERD, _DMN)

_MODEL = mb.resolve_model_path(None)
needs_model = pytest.mark.skipif(
    _MODEL is None,
    reason=(f"the reference model was not found - pass its location in "
            f"{mb.MODEL_ENV_VAR}; every figure in these bindings is measured "
            f"from it"),
)


def _group(technology: str) -> str:
    """What the stored tokens of a bound technology start with."""
    return _ERD_GROUP if technology == _ERD else technology


def _qualified(technology: str, diagram_type: str) -> str:
    """`<Tech>::<DiagramType>`, built rather than written as a literal.

    Written out, the qualified form of a Sparx-shipped id that the release
    gate's allowlist does not carry trips the gate as an unrecognized MDG
    namespace. The value under test is the same either way.
    """
    return f"{technology}{MDG_SEPARATOR}{diagram_type}"


def _text(filename: str) -> str:
    return (_BINDINGS_DIR / filename).read_text(encoding="utf-8")


def _file_for(technology: str) -> str:
    return _ERD_FILE if technology == _ERD else _DMN_FILE


def _bound(technology: str, diagram_type: str) -> DiagramTypeBinding:
    binding = find_binding(technology)
    assert binding is not None, technology
    return binding.diagram_type(diagram_type)


# ---------------------------------------------------------------------------
# Measurement fixtures. The model is copied once per session, not once per call.
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def model():
    with mb.open_model_copy(_MODEL) as conn:
        yield mb._load_diagrams(conn), mb.list_technologies(conn)


@pytest.fixture(scope="module")
def measured(model):
    diagrams, known = model
    out = {}
    for technology, diagram_type in ((_ERD, _ERD_TYPE), (_DMN, _DMN_TYPE),
                                     (_DATA, _DATA_TYPE)):
        out[technology] = mb.measure_diagrams(
            diagrams, known, _group(technology), diagram_type)
    return out


# ---------------------------------------------------------------------------
# The files themselves
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("technology,diagram_type,base", _BOUND)
def test_each_binding_loads_and_is_found_by_its_declared_id(
        technology, diagram_type, base):
    binding = find_binding(technology)
    assert binding is not None
    assert binding.technology == technology
    assert available_bindings()[technology] == _file_for(technology)
    # One diagram type each, which is the whole catalog its technology declares
    # for the notation - see the MDG-data test.
    assert set(binding.diagram_types) == {diagram_type}
    assert binding.diagram_types[diagram_type].base == base


@pytest.mark.parametrize("filename", (_ERD_FILE, _DMN_FILE))
def test_each_binding_file_is_written_with_lf_line_endings(filename):
    """The release gate fails the build on a CR, and an editor supplies them
    silently, so the bytes are checked rather than trusted."""
    assert b"\r" not in (_BINDINGS_DIR / filename).read_bytes()


@pytest.mark.parametrize("technology,diagram_type,base", _BOUND)
def test_each_binding_declares_uml_underneath_it_and_resolves_its_substrate(
        technology, diagram_type, base):
    """EA is a UML tool, so every MDG technology is a stereotype layer over a
    UML diagram type rather than a peer notation beside it."""
    binding = find_binding(technology)
    assert binding.extends == "UML"
    dt = binding.diagram_types[diagram_type]
    assert dt.inherits, f"{technology} names a base its parent does not bind"
    assert dt.substrate == _qualified("UML", base)


@pytest.mark.parametrize("technology,diagram_type,base", _BOUND)
def test_each_binding_states_its_own_prefix_rather_than_inheriting_one(
        technology, diagram_type, base):
    """The live trap: the parent's measured `""` is right for a family drawn in
    plain UML and wrong for one whose MDG stereotypes its elements. One of these
    two has a real prefix and the other genuinely has none, so both must say so
    and the pair is what makes the assertion mean anything."""
    import yaml
    document = yaml.safe_load(_text(_file_for(technology)))
    assert "stereotype_prefix" in document, (
        f"{technology} does not state a prefix, so it inherits one")
    binding = find_binding(technology)
    assert binding.stereotype_prefix == (document["stereotype_prefix"] or "")


def test_the_two_bindings_disagree_about_the_prefix_and_that_is_the_point():
    erd, dmn = find_binding(_ERD), find_binding(_DMN)
    assert erd.stereotype_prefix == "ERD_"
    assert erd.stereotype_for("Entity") == "ERD_Entity"
    assert erd.concept_for("ERD_Entity") == "Entity"
    assert dmn.stereotype_prefix == ""
    assert dmn.stereotype_for("Decision") == "Decision"


# ---------------------------------------------------------------------------
# The ids and the diagram types, against the MDG data
# ---------------------------------------------------------------------------
@needs_model
def test_the_ids_are_the_ones_the_model_carries_and_the_guessable_ones_are_not(
        model):
    """A binding keyed on a guessed id resolves to nothing, silently.

    Both of these ids carry something no reader would predict: the entity-
    relationship technology and its diagram type differ in case from each other
    and the family is called neither of them in EA's interface, and the decision
    technology carries its minor version.
    """
    _, known = model
    for technology in _IDS:
        assert _group(technology) in known, technology
    for guess in _GUESSED:
        assert guess not in known, f"{guess!r} is an id after all - re-check"


@needs_model
@pytest.mark.parametrize("technology,diagram_type,base", _BOUND)
def test_the_bound_diagram_type_is_the_whole_catalog_its_technology_declares(
        technology, diagram_type, base, model):
    """Nothing is declined here without being classified, because there is
    nothing to decline: each of these technologies declares exactly one diagram
    type, which is why one bound type is a complete binding rather than a
    partial one."""
    _, known = model
    assert set(known[_group(technology)]) == {diagram_type}


@needs_model
@pytest.mark.parametrize("technology,diagram_type,base", _BOUND)
def test_the_base_is_the_ea_diagram_type_the_model_records(
        technology, diagram_type, base, model):
    """`base` is the value `create_diagram` is called with, so it is read from
    the diagrams EA holds rather than remembered. Both of these sit on a base the
    parent binding measures, and they sit on two different ones."""
    diagrams, _ = model
    recorded = {d.raw_type for d in diagrams.values()
                if d.technology == _group(technology) and d.diagram_type == diagram_type}
    assert recorded == {base}
    assert find_binding("UML").diagram_types[base] is not None


# ---------------------------------------------------------------------------
# Sizes
# ---------------------------------------------------------------------------
@needs_model
@pytest.mark.parametrize("technology,diagram_type,base", _BOUND)
def test_neither_binding_states_a_per_concept_size_and_the_tool_agrees(
        technology, diagram_type, base, measured):
    """A concept size is stated exactly when the tool found a dominant,
    non-low-n mode that DIFFERS from the default. For both of these the set is
    empty, and for two different reasons the comments record: the concepts that
    dominate sit AT the default already, and the ones that do not are either
    below the sample threshold or have no mode at all.

    `own_sizing`, not `sizing`: the resolved mapping also carries the per-concept
    sizes the substrate measured, which are the parent's measurements and must
    not be judged as if this technology had made them.
    """
    m = measured[technology]
    dt = _bound(technology, diagram_type)
    expected = {
        concept for concept, st in m.sizes.items()
        if st.n >= m.min_sample and st.mode is not None
        and st.mode_share >= mb.DOMINANT_SHARE
        and st.mode != m.default_size.mode
    }
    assert expected == set(), (
        f"{technology}: the tool now finds a statable per-concept size for "
        f"{sorted(expected)}; state it or say why not")
    assert set(dt.own_sizing) == {"default"}


# ---------------------------------------------------------------------------
# Spacing - stated for one binding, refused for the other, both on the rules
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Every stated figure carries its evidence
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# The grammar: EA places both of these, and that is producible
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("technology,diagram_type,base", _BOUND)
def test_both_diagram_types_are_graphs_that_ea_places_and_we_can_still_produce(
        technology, diagram_type, base):
    """`graph` is the honest answer for both, and the pair of booleans it
    produces is the one a single flag could not hold: we have no composer, and
    the diagram is producible anyway because EA's own layout places it and we
    tidy afterwards. A consumer reading `grammar_is_implemented` alone would
    drop both of these as unsupported."""
    dt = _bound(technology, diagram_type)
    assert dt.grammar == "graph"
    assert dt.grammar in GRAMMARS and dt.grammar in EA_PLACED_GRAMMARS
    assert dt.grammar_placement == PLACED_BY_EA
    assert dt.geometry_is_composed is False
    assert dt.grammar_is_implemented is False
    assert dt.grammar not in implemented_grammars()
    assert dt.grammar_is_producible is True
    assert dt.grammar in producible_grammars()


@pytest.mark.parametrize("technology,diagram_type,base", _BOUND)
def test_the_spec_each_binding_builds_names_only_keys_the_engine_has(
        technology, diagram_type, base):
    """A `graph` binding still feeds the layout call: the item size and the two
    gaps are what EA is given as column and layer spacing, so they are read
    rather than inert - which is why they earn their place in a binding whose
    coordinates are not ours."""
    dt = _bound(technology, diagram_type)
    spec = dt.spec()
    assert set(spec) <= set(DEFAULT_SPEC)
    assert spec["item_width"], spec["item_height"]
    assert spec["item_gap_x"] > 0 and spec["item_gap_y"] > 0


# ---------------------------------------------------------------------------
# Channels
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("technology,diagram_type,base", _BOUND)
def test_neither_binding_offers_a_channel_it_also_claims(
        technology, diagram_type, base):
    dt = _bound(technology, diagram_type)
    assert set(dt.claimed_channels()).isdisjoint(dt.free_channels())
    # Position is spoken for on both: EA computes it for a graph and overwrites
    # anything set beforehand, so it is not available to carry a variable.
    assert "position" in dt.claimed_channels()
    assert not dt.channel_is_free("position")


def test_the_two_bindings_differ_on_fill_and_both_say_why():
    """Fill is the channel the schema refuses to let a binding pass over in
    silence, and these two answer it differently on measured grounds: one
    notation fixes shapes and says nothing about color, the other has EA paint
    every element from its stereotype."""
    erd = _bound(_ERD, _ERD_TYPE)
    dmn = _bound(_DMN, _DMN_TYPE)
    assert erd.channels["fill"] is None
    assert erd.channel_is_free("fill")
    assert dmn.channels["fill"]
    assert "fill" in dmn.claimed_channels()
    assert not dmn.channel_is_free("fill")


def test_the_decision_binding_leaves_line_style_neither_claimed_nor_free():
    """Deliberately in neither list. Three requirement kinds coexist and the
    line tells them apart, so advertising it as free would invite overwriting
    that; which visual property EA's rendering uses was not verified, so
    claiming it would state something unmeasured."""
    dt = _bound(_DMN, _DMN_TYPE)
    for channel in ("line_style", "line_color"):
        assert channel not in dt.claimed_channels()
        assert not dt.channel_is_free(channel)


# ---------------------------------------------------------------------------
# What the model says about the two slots that are not numbers
# ---------------------------------------------------------------------------
@needs_model
@pytest.mark.parametrize("technology,diagram_type,base", _BOUND)
def test_the_frame_supplies_the_title_because_no_diagram_draws_one(
        technology, diagram_type, base, model):
    """Re-checked against the model rather than taken from the corpus, which
    records a drawn title for one of these. Not one diagram of either type
    carries a Text, Note or Boundary whose content IS the diagram's name, and a
    diagram with two titles is the worse of the two mistakes.

    Exact content, deliberately, and the looser test is why: matching the name as
    a SUBSTRING fires on the prose. Both notations put explanatory paragraphs on
    their example diagrams, and a paragraph that opens by naming the notation is
    not a title. A caption, a legend or an annotation is not one either - which is
    the same reasoning the parent binding declines a Text element on.
    """
    diagrams, _ = model
    with mb.open_model_copy(_MODEL) as conn:
        content = {oid: (name or "", note or "") for oid, name, note
                   in conn.execute("SELECT Object_ID, Name, Note FROM t_object")}
    selected = [d for d in diagrams.values()
                if d.technology == _group(technology) and d.diagram_type == diagram_type]
    assert selected
    drawn = [d.diagram_id for d in selected if d.name.strip() and any(
        i.object_type in mb.FURNITURE_TYPES
        and d.name.strip() in (text.strip()
                               for text in content.get(i.object_id, ("", "")))
        for i in d.items)]
    assert drawn == [], drawn
    assert _bound(technology, diagram_type).title == "frame-header"
    assert not _bound(technology, diagram_type).draws_its_own_title


@needs_model
def test_nesting_is_not_the_structure_on_either_type_so_no_grid_is_composed(
        model):
    """What refuses `nested-grid` for both, measured. One has no containment at
    all; the other has a real enclosure that is a minority of one concept while
    the requirement links are the content everywhere."""
    diagrams, _ = model

    def nesting(technology, diagram_type):
        inside, total, parents = 0, 0, set()
        for d in diagrams.values():
            if d.technology != _group(technology) or d.diagram_type != diagram_type:
                continue
            for a in d.items:
                total += 1
                for b in d.items:
                    if b.rect.contains(a.rect):
                        inside += 1
                        parents.add(b.stereotype or b.object_type)
                        break
        return inside, total, parents

    inside, total, _ = nesting(_ERD, _ERD_TYPE)
    assert total and inside == 0

    inside, total, parents = nesting(_DMN, _DMN_TYPE)
    assert 0 < inside < total / 2
    assert parents == {"DecisionService"}


@needs_model
def test_the_attribute_fan_that_erd_cites_for_refusing_radial(model):
    """`radial` was considered because attributes really do fan around their
    entity, and refused because each diagram has several fans rather than one
    ring. Both halves of that are figures in the file, so both are pinned: the
    split of the attribute connector between entity-to-attribute and
    attribute-to-attribute, and the number of entities that carry a fan at all.
    """
    diagrams, _ = model
    with mb.open_model_copy(_MODEL) as conn:
        stereotype = {oid: (s or "") for oid, s in conn.execute(
            "SELECT Object_ID, Stereotype FROM t_object")}
        on_diagram = {}
        for did, cid in conn.execute(
                "SELECT DiagramID, ConnectorID FROM t_diagramlinks"):
            on_diagram.setdefault(did, []).append(cid)
        connectors = {cid: (s or "", a, b) for cid, s, a, b in conn.execute(
            "SELECT Connector_ID, Stereotype, Start_Object_ID, End_Object_ID "
            "FROM t_connector")}
    from_entity = from_attribute = 0
    hubs_per_diagram = []
    for d in diagrams.values():
        if d.technology != _ERD_GROUP or d.diagram_type != _ERD_TYPE:
            continue
        here = {i.object_id for i in d.items}
        hubs = set()
        for cid in on_diagram.get(d.diagram_id, ()):
            kind, a, b = connectors.get(cid, ("", 0, 0))
            if kind != "ERD_Connector" or a not in here or b not in here:
                continue
            ends = {stereotype.get(a, ""), stereotype.get(b, "")}
            if "ERD_Entity" in ends:
                from_entity += 1
                hubs |= {o for o in (a, b) if stereotype.get(o) == "ERD_Entity"}
            else:
                from_attribute += 1
        hubs_per_diagram.append(len(hubs))
    assert (from_entity, from_attribute) == (21, 9)
    binding = find_binding(_ERD)
    assert f"{from_entity} join an entity" in binding.notes
    # Several fans, not one ring - which is what `radial` cannot compose.
    assert sorted(hubs_per_diagram) == [2, 6]


@needs_model
def test_the_top_down_reading_that_claims_position_on_the_decision_diagram(
        model):
    """The `position` claim is a measurement, so it is checked: the requiring
    element is drawn higher than the element it requires on a clear majority of
    requirement links, which is what makes moving an element up or down to
    encode something else a reversal rather than a decoration."""
    diagrams, _ = model
    kinds = {"InformationRequirement", "KnowledgeRequirement",
             "AuthorityRequirement"}
    with mb.open_model_copy(_MODEL) as conn:
        connectors = {cid: (stereotype or "", start, end) for cid, stereotype,
                      start, end in conn.execute(
                          "SELECT Connector_ID, Stereotype, Start_Object_ID, "
                          "End_Object_ID FROM t_connector")}
        on_diagram = {}
        for did, cid in conn.execute(
                "SELECT DiagramID, ConnectorID FROM t_diagramlinks"):
            on_diagram.setdefault(did, []).append(cid)
    higher = total = 0
    for d in diagrams.values():
        if d.technology != _DMN or d.diagram_type != _DMN_TYPE:
            continue
        middle = {i.object_id: (i.rect.top + i.rect.bottom) / 2
                  for i in d.items}
        for cid in on_diagram.get(d.diagram_id, ()):
            stereotype, start, end = connectors.get(cid, ("", 0, 0))
            if stereotype not in kinds or start not in middle or end not in middle:
                continue
            total += 1
            higher += middle[start] > middle[end]
    assert total >= 100, total
    share = higher / total
    assert share > 0.8, share
    dt = _bound(_DMN, _DMN_TYPE)
    assert "position" in dt.claimed_channels()


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("technology,diagram_type,base", _BOUND)
def test_a_diagram_that_names_itself_resolves_exactly_to_its_binding(
        technology, diagram_type, base):
    resolution = resolve_diagram(
        set(available_bindings()),
        style_ex=f"MDGDgm={_qualified(_group(technology), diagram_type)};DUID=A1B2;")
    assert resolution.resolved and resolution.path == "qualified"
    assert resolution.confidence == "exact"
    assert resolution.technology == technology
    assert resolution.diagram_type_name == diagram_type


@pytest.mark.parametrize("technology,diagram_type,base", _BOUND)
def test_the_diagram_type_name_is_claimed_by_this_binding_alone(
        technology, diagram_type, base):
    """The 53% path: most real diagrams carry no MDG tag and identify themselves
    through `Diagram_Type` only. Neither of these names may collide with another
    installed binding's, or every such diagram becomes ambiguous."""
    resolution = resolve_diagram(set(available_bindings()),
                                 diagram_type=diagram_type)
    assert not resolution.is_ambiguous, resolution.candidates
    assert resolution.path == "diagram-type"
    assert resolution.technology == technology


def test_a_plain_diagram_on_the_shared_base_still_resolves_to_the_base_notation():
    """Adding a binding drawn on `Logical` must not make every plain class
    diagram ambiguous: an exact diagram-type NAME beats the base type, and these
    two name their types something no base is called."""
    resolution = resolve_diagram(set(available_bindings()),
                                 diagram_type=_ERD_BASE)
    assert not resolution.is_ambiguous, resolution.candidates
    assert resolution.technology == "UML"
    assert resolution.path == "diagram-type"


# ---------------------------------------------------------------------------
# The refusal
# ---------------------------------------------------------------------------
@needs_model
def test_the_data_modeling_technology_is_deliberately_unbound_and_why(
        model, measured):
    """THE MOST IMPORTANT TEST IN THIS FILE, because it is the only record that
    a missing binding is a decision.

    `sizing.default` must be supplied by the diagram type or by its substrate -
    it is checked after the merge rather than required in the document - and the
    data model has no size of its own to put in it. Inheriting is now the honest
    answer here rather than a blocker, and the measurement below is why there is
    nothing to state. The table is the only concept on these diagrams that
    reaches the sample threshold at all and it has NO mode - every table is a
    different size, because the box is stretched around the columns it lists. The
    pooled mode that the tool does report is two unrelated single elements
    landing on one size, which is an accident with a share in the single digits.

    So the diagram type cannot be keyed honestly, and it is the only one of that
    technology's types in scope, so no file ships. Everything below is derived:
    if a later model gives the table a real modal size, this test fails and the
    binding should then be written.
    """
    _, known = model
    # The absence is a decision, not a lookup failure: the id and the type are
    # both in the data.
    assert _DATA in known and _DATA_TYPE in known[_DATA]
    assert find_binding(_DATA) is None
    for technology in available_bindings():
        assert _DATA_TYPE not in find_binding(technology).diagram_types

    m = measured[_DATA]
    assert m.diagrams >= 10, m.diagrams
    table = m.sizes["table"]
    assert table.n >= mb.MIN_SAMPLE
    assert table.mode is None, (
        "the table now has a modal size; write the binding")
    assert table.distinct == table.n, table.distinct
    # And the pooled figure the tool would hand over is an accident: no concept
    # supplies it dominantly and its share is nowhere near a convention.
    assert m.default_size.mode_share < 0.10, m.default_size.mode_share
    assert all(count == 1 for count in m.default_supply.values()), (
        m.default_supply)
    assert len(m.default_supply) > 1, (
        "one concept supplies the mode after all; re-judge it")


@needs_model
def test_a_data_model_diagram_resolves_to_no_binding_and_says_so_cleanly(
        model):
    """The intended outcome of the refusal: an unbound resolution that a caller
    can act on, rather than a wrong binding or a crash. Distinct from
    `not-installed`, and distinct from ambiguous."""
    installed = set(available_bindings()) | {_DATA}
    resolution = resolve_diagram(
        installed, style_ex=f"MDGDgm={_qualified(_DATA, _DATA_TYPE)};")
    assert not resolution.resolved
    assert resolution.path == "unbound"
    assert resolution.confidence == "none"
    assert not resolution.is_ambiguous
    assert resolution.binding is None and resolution.diagram_type is None
    assert resolution.technology == _DATA
    assert resolution.reason
