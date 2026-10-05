#!/usr/bin/env python3
"""Tests for the semantic model contract.

    python -m pytest _shared/tools/test_semantic_model.py -q

Nothing here touches a repository, a COM object, Power BI or the filesystem.

Several of these assert MEASURED facts rather than design preferences, and say
so where they do. The relationship count is one: 38 is what the hub shape
produces for 29 vocabulary tables, and it is the number a live apply confirmed.
"""
from __future__ import annotations

from ddl import FRAME_DDL, physical
from report_model import Column, ReportModel, Table
from semantic_model import (DEFAULT_MEASURE_HOST, HUB, build_semantic_model,
                            tmdl_type, traversal_measures)


def model(n_tables=2, cols=(("criticality", "TEXT"),)):
    tables = [
        Table(name=f"entity_{i}", entity_key=f"k{i}", stereotype=f"S{i}",
              description=f"Entity {i}",
              columns=[Column(name=c, source_tag=c, sql_type=t) for c, t in cols])
        for i in range(n_tables)
    ]
    return ReportModel(technology_id="WBA", tables=tables)


# ------------------------------------------------------------------- types


def test_sql_types_map_to_tmdl_types():
    assert tmdl_type("TEXT") == "string"
    assert tmdl_type("INTEGER") == "int64"
    assert tmdl_type("REAL") == "double"


def test_an_unknown_sql_type_falls_back_to_string_rather_than_raising():
    """A column whose type we cannot map is still a column. Dropping it would
    lose data silently, which is worse than showing it as text."""
    assert tmdl_type("BLOB") == "string"
    assert tmdl_type("") == "string"


# -------------------------------------------------------------- the tables


def test_every_vocabulary_table_becomes_a_visible_table():
    sm = build_semantic_model(model(n_tables=3))
    for i in range(3):
        t = sm.table(f"entity_{i}")
        assert t is not None
        assert not t.is_hidden


def test_the_frame_is_hidden_not_excluded():
    """Settled for APT-2026-0211: excluding the frame costs graph traversal and
    understates every multi-valued tag. Hiding keeps both and still shows the
    customer only their vocabulary."""
    sm = build_semantic_model(model())
    hidden = {t.name for t in sm.tables if t.is_hidden}
    assert physical("tag_value") in hidden
    assert physical("pkg") in hidden
    assert HUB in hidden


def test_the_hub_is_hidden_and_hosts_no_measures():
    """MEASURED: Power BI keeps a hidden table VISIBLE when it hosts visible
    measures. Measures on the hub therefore defeat the hiding and `_keymap`
    appears in a field list promised to be business vocabulary."""
    sm = build_semantic_model(model())
    hub = sm.table(HUB)
    assert hub.is_hidden
    assert hub.measures == []


def test_the_measure_host_is_visible_business_named_and_fully_column_hidden():
    sm = build_semantic_model(model())
    host = sm.table(DEFAULT_MEASURE_HOST)
    assert host is not None
    assert not host.is_hidden
    assert not host.name.startswith("_")
    assert host.source_name == physical("rel_all")
    assert host.measures, "the host exists to carry the traversal measures"
    assert all(c.is_hidden for c in host.columns), \
        "a visible host with visible columns puts source_guid in the field list"


def test_the_measure_host_can_be_renamed():
    """A customer's vocabulary is theirs. Nothing downstream may assume the
    default name."""
    sm = build_semantic_model(model(), measure_host="Connections")
    assert sm.table("Connections") is not None
    assert sm.table(DEFAULT_MEASURE_HOST) is None
    assert any("'Connections'" in m.expression for m in sm.table("Connections").measures)


def test_frame_columns_come_from_the_ddl_rather_than_being_restated():
    """`ddl.FRAME_DDL` is the single declared place the frame's shape lives.
    Restating the columns is how the two drift - it happened once already, with
    `overflow_tag` defined in the DDL and missing from the model."""
    sm = build_semantic_model(model())
    for frame_key, spec in FRAME_DDL.items():
        name = physical(frame_key)
        table = sm.table(DEFAULT_MEASURE_HOST if name == physical("rel_all") else name)
        assert [c.name for c in table.columns] == [c for c, _ in spec]


def test_the_entity_key_is_hidden_but_the_business_columns_are_not():
    sm = build_semantic_model(model(cols=[("criticality", "TEXT")]))
    cols = {c.name: c for c in sm.table("entity_0").columns}
    assert cols["ea_guid"].is_hidden
    assert not cols["name"].is_hidden
    assert not cols["criticality"].is_hidden


def test_entity_columns_match_the_ddl_shape():
    """`ea_guid`, `name`, `metaclass`, then the tag columns - the same order
    `ddl.entity_table_ddl` creates, so a column maps to its source."""
    sm = build_semantic_model(model(cols=[("criticality", "TEXT")]))
    assert [c.name for c in sm.table("entity_0").columns] == \
        ["ea_guid", "name", "metaclass", "criticality"]


def test_nothing_summarizes_by_default():
    """A tag column that silently sums is a wrong number in a report. The
    multi-valued ones especially: APT-2026-0210 found exact-match counting of a
    flattened tag understated by about half."""
    sm = build_semantic_model(model(cols=[("count_of_things", "INTEGER")]))
    for table in sm.tables:
        for column in table.columns:
            assert column.summarize_by == "none"


# ------------------------------------------------------- the relationships


def test_the_relationship_count_is_entities_plus_nine():
    """Nine fixed relationships hang off the hub whatever the technology is:
    five many-to-one bridges, two for `_rel_all`, the package route and diagram
    membership. On the reference model that is 29 + 9 = 38, which is what a live
    apply confirmed."""
    for n in (1, 5, 29):
        sm = build_semantic_model(model(n_tables=n))
        assert len(sm.relationships) == n + 9


def test_exactly_one_relationship_is_inactive_and_it_is_the_inbound_edge():
    """Auto-detect produced 29 inactive relationships out of 63 and deactivated
    a real one silently. The designed model has exactly one, by design."""
    sm = build_semantic_model(model(n_tables=29))
    assert len(sm.inactive) == 1
    rel = sm.inactive[0]
    assert rel.from_column == "target_guid"
    assert rel.to_table == HUB


def test_rel_all_relates_to_the_hub_twice_on_different_endpoints():
    """This is the whole graph traversal, and MEASURED: Power BI's auto-detect
    found ZERO of it, because the column names do not match."""
    sm = build_semantic_model(model())
    host = DEFAULT_MEASURE_HOST
    endpoints = {r.from_column: r for r in sm.relationships if r.from_table == host}
    assert set(endpoints) == {"source_guid", "target_guid"}
    assert endpoints["source_guid"].is_active
    assert not endpoints["target_guid"].is_active


def test_every_one_to_one_carries_both_directions():
    """Power BI rejects THE WHOLE TMDL FILE on apply when a one-to-one does not.
    Not the offending line - the file."""
    sm = build_semantic_model(model(n_tables=4))
    ones = [r for r in sm.relationships if r.from_cardinality == "one"]
    assert len(ones) == 4
    assert all(r.cross_filtering == "bothDirections" for r in ones)


def test_the_package_tree_is_reached_only_through_the_hub():
    """Vocabulary tables reaching `_pkg` independently is what created the
    ambiguous filter path Power BI resolved by silently switching off a real
    relationship."""
    sm = build_semantic_model(model(n_tables=3))
    to_pkg = [r for r in sm.relationships if r.to_table == physical("pkg")]
    assert len(to_pkg) == 1
    assert to_pkg[0].from_table == HUB


def test_the_diagram_package_loop_is_not_closed():
    """`_diagram.package_id` -> `_pkg` would close a loop through the hub via
    `_diagram_object`, and Power BI would deactivate one side without saying so.
    It is deliberately absent."""
    sm = build_semantic_model(model())
    assert not any(r.from_table == physical("diagram")
                   and r.from_column == "package_id"
                   for r in sm.relationships)


def test_attributes_and_operations_join_on_element_guid_not_ea_guid():
    """A detail that produces an empty relationship rather than an error if
    assumed."""
    sm = build_semantic_model(model())
    by_table = {r.from_table: r for r in sm.relationships}
    assert by_table[physical("attribute")].from_column == "element_guid"
    assert by_table[physical("operation")].from_column == "element_guid"


def test_the_audit_tables_are_left_disconnected_rather_than_wired_to_something():
    """`_tag_coverage` is keyed by table and tag, not by element, so relating it
    would invent a join. `_load_run` is refresh audit."""
    sm = build_semantic_model(model())
    related = {r.from_table for r in sm.relationships} | \
              {r.to_table for r in sm.relationships}
    assert physical("tag_coverage") not in related
    assert physical("load_run") not in related


def test_relationship_names_are_unique_and_deterministic():
    first = build_semantic_model(model(n_tables=6))
    second = build_semantic_model(model(n_tables=6))
    names = [r.name for r in first.relationships]
    assert len(names) == len(set(names))
    assert names == [r.name for r in second.relationships]


def test_every_relationship_states_why_it_exists():
    """The next person to open the file will otherwise wonder whether the
    inactive one is a mistake."""
    sm = build_semantic_model(model(n_tables=2))
    assert all(r.why for r in sm.relationships)


def test_every_relationship_endpoint_resolves_to_a_table_in_the_model():
    """A relationship naming a table that is not emitted is rejected on apply."""
    sm = build_semantic_model(model(n_tables=4))
    names = {t.name for t in sm.tables}
    for r in sm.relationships:
        assert r.from_table in names, r.name
        assert r.to_table in names, r.name


# ------------------------------------------------------------- the measures


def test_inbound_traversal_uses_the_inactive_relationship():
    """MEASURED: without USERELATIONSHIP the inbound measure silently returns
    the OUTBOUND count. It is wrong and it looks plausible."""
    measures = {m.name: m for m in traversal_measures("Relationships", HUB)}
    inbound = measures["Inbound edges"].expression
    assert "USERELATIONSHIP" in inbound
    assert f"'{HUB}'[ea_guid]" in inbound
    assert "USERELATIONSHIP" not in measures["Outbound edges"].expression


def test_a_zero_filled_variant_exists_for_both_directions():
    """MEASURED: SUMMARIZECOLUMNS returned 65 of 145 rows when every measure on
    a row could be BLANK. The coalesced measure returns all 145."""
    measures = {m.name: m for m in traversal_measures("Relationships", HUB)}
    for name in ("Outbound edges (zero-filled)", "Inbound edges (zero-filled)"):
        assert measures[name].expression.startswith("COALESCE(")
        assert measures[name].expression.endswith(", 0)")


def test_measures_reference_the_host_by_its_model_name():
    """DAX names the table as the model does, not as the database does. A
    measure pointing at `_rel_all` breaks the moment the host is renamed."""
    measures = traversal_measures("Connections", HUB)
    assert all("'Connections'" in m.expression for m in measures)
    assert not any("_rel_all" in m.expression for m in measures)


def test_every_measure_is_described():
    for m in traversal_measures("Relationships", HUB):
        assert m.description


# ------------------------------------------------------------ determinism


def test_the_model_is_plain_serializable_data():
    """It is an artifact a customer can review, edit and re-apply, in the same
    lineage as the report model and the validation rulesets."""
    d = build_semantic_model(model()).to_dict()
    assert isinstance(d, dict)
    assert {"tables", "relationships", "hub", "measure_host"} <= set(d)


def test_two_builds_of_the_same_report_model_are_identical():
    assert build_semantic_model(model(n_tables=4)).to_dict() == \
        build_semantic_model(model(n_tables=4)).to_dict()


def test_a_measure_host_colliding_with_a_vocabulary_table_is_refused():
    """A collision is SILENT otherwise: `render_definition` keys files by table
    name so one disappears, and `model.tmdl` emits `ref table` twice."""
    import pytest
    with pytest.raises(ValueError, match="collides"):
        build_semantic_model(model(), measure_host="entity_0")


def test_the_collision_check_is_case_insensitive_as_analysis_services_is():
    import pytest
    with pytest.raises(ValueError, match="collides"):
        build_semantic_model(model(), measure_host="ENTITY_0")
