#!/usr/bin/env python3
"""Tests for frame-row shaping.

    python -m pytest _shared/tools/test_frame.py -q

Nothing here touches a repository, a COM object or the filesystem.
"""
from __future__ import annotations

from ddl import FRAME_DDL
from ea_census import Entity, ElementCensus
from frame import (
    attribute_rows,
    dangling,
    diagram_object_rows,
    diagram_rows,
    element_rows,
    operation_rows,
    package_rows,
    relationship_rows,
)
from report_model import build_report_model

NS = "WestbrookBankArchitecture"


def _census(*entities):
    c = ElementCensus()
    c.entities = list(entities)
    return c


def _entity(key, stereo, guids, metaclass="Component", fqname="", profile=""):
    e = Entity(key=key, stereotype=stereo, fqname=fqname, profile=profile)
    e.guids.update(guids)
    e.metaclasses[metaclass] = len(guids)
    return e


def _model():
    key = f"{NS}::WBABusinessApplication"
    ent = _entity(key, "WBABusinessApplication", ["{A}", "{B}"], fqname=key, profile=NS)
    return build_report_model(_census(ent), {}, {}), key


ELEMENTS = [
    {"ea_guid": "{A}", "Object_ID": 1, "Name": "Core Ledger",
     "Object_Type": "Component", "Package_ID": 5},
    {"ea_guid": "{B}", "Object_ID": 2, "Name": "Card Switch",
     "Object_Type": "Component", "Package_ID": 6},
]
GUID_BY_ID = {1: "{A}", 2: "{B}"}


# --- pkg --------------------------------------------------------------------

PACKAGES = [
    {"Package_ID": 4, "Parent_ID": 0, "Name": "Westbrook Bank"},
    {"Package_ID": 5, "Parent_ID": 4, "Name": "Applications"},
    {"Package_ID": 6, "Parent_ID": 5, "Name": "Payments"},
]


def test_path_and_depth_are_computed_from_the_parent_chain():
    rows = {r["package_id"]: r for r in package_rows(PACKAGES)}
    assert rows[4]["path"] == "Westbrook Bank" and rows[4]["depth"] == 0
    assert rows[6]["path"] == "Westbrook Bank/Applications/Payments"
    assert rows[6]["depth"] == 2


def test_a_package_whose_parent_is_out_of_scope_becomes_a_root_not_a_casualty():
    """Dropping it would drop every element under it from any grouping by path -
    a bigger error than a path that starts below the model root."""
    rows = {r["package_id"]: r for r in package_rows(PACKAGES, in_scope={5, 6})}
    assert set(rows) == {5, 6}
    assert rows[5]["parent_id"] is None
    assert rows[5]["path"] == "Applications"
    assert rows[6]["path"] == "Applications/Payments"


def test_a_package_that_is_its_own_parent_does_not_hang():
    rows = package_rows([{"Package_ID": 9, "Parent_ID": 9, "Name": "Loop"}])
    assert rows == [{"package_id": 9, "parent_id": None, "name": "Loop",
                    "path": "Loop", "depth": 0}]


def test_a_cycle_between_two_packages_does_not_hang():
    rows = {r["package_id"]: r for r in package_rows([
        {"Package_ID": 1, "Parent_ID": 2, "Name": "A"},
        {"Package_ID": 2, "Parent_ID": 1, "Name": "B"}])}
    assert set(rows) == {1, 2}
    assert all(r["path"] for r in rows.values())


def test_an_unparseable_package_id_is_skipped_not_fatal():
    rows = package_rows(PACKAGES + [{"Package_ID": None, "Parent_ID": 4, "Name": "?"}])
    assert [r["package_id"] for r in rows] == [4, 5, 6]


def test_package_rows_are_deterministic_regardless_of_input_order():
    assert package_rows(PACKAGES) == package_rows(list(reversed(PACKAGES)))


def test_package_rows_fit_the_frame_schema():
    assert set(package_rows(PACKAGES)[0]) == {c for c, _ in FRAME_DDL["pkg"]}


# --- element ----------------------------------------------------------------

def test_element_rows_name_where_each_element_landed():
    model, key = _model()
    rows = {r["ea_guid"]: r for r in element_rows(
        ELEMENTS, model, {"{A}": [key], "{B}": [key]})}
    assert rows["{A}"]["entity_table"] == model.tables[0].name
    assert rows["{A}"]["stereotype"] == "WBABusinessApplication"
    assert rows["{A}"]["profile"] == NS
    assert rows["{A}"]["object_id"] == 1


def test_an_untyped_element_is_still_in_the_frame_with_no_table():
    model, key = _model()
    els = ELEMENTS + [{"ea_guid": "{C}", "Object_ID": 3, "Name": "Spreadsheet",
                       "Object_Type": "Artifact", "Stereotype": "", "Package_ID": 5}]
    rows = {r["ea_guid"]: r for r in element_rows(els, model, {"{A}": [key]})}
    assert rows["{C}"]["entity_table"] is None
    assert rows["{C}"]["stereotype"] == ""


def test_an_observed_but_undeclared_stereotype_is_kept_not_blanked():
    """Architects pick stereotypes from whatever language EA has enabled. One that
    no loaded technology declares is a finding, not noise."""
    model, key = _model()
    els = ELEMENTS + [{"ea_guid": "{C}", "Object_ID": 3, "Name": "Thing",
                       "Object_Type": "Class", "Stereotype": "ArchiMate_Node",
                       "Package_ID": 5}]
    rows = {r["ea_guid"]: r for r in element_rows(els, model, {"{A}": [key]})}
    assert rows["{C}"]["stereotype"] == "ArchiMate_Node"
    assert rows["{C}"]["entity_table"] is None


def test_excluded_elements_do_not_reach_the_frame():
    model, key = _model()
    rows = element_rows(ELEMENTS, model, {"{A}": [key], "{B}": [key]},
                        excluded_guids={"{B}"})
    assert [r["ea_guid"] for r in rows] == ["{A}"]


def test_a_multi_stereotype_element_names_its_first_table_deterministically():
    a_key, b_key = f"{NS}::WBAAppA", f"{NS}::WBAAppB"
    ents = [_entity(a_key, "WBAAppA", ["{M}"], fqname=a_key, profile=NS),
            _entity(b_key, "WBAAppB", ["{M}"], fqname=b_key, profile=NS)]
    model = build_report_model(_census(*ents), {}, {})
    els = [{"ea_guid": "{M}", "Object_ID": 1, "Name": "Both",
            "Object_Type": "Component", "Package_ID": 1}]
    first = element_rows(els, model, {"{M}": [b_key, a_key]})[0]
    assert first["entity_table"] == model.tables[0].name
    assert element_rows(els, model, {"{M}": [a_key, b_key]})[0]["entity_table"] \
        == first["entity_table"]


def test_element_rows_fit_the_frame_schema():
    model, key = _model()
    rows = element_rows(ELEMENTS, model, {"{A}": [key]})
    assert set(rows[0]) == {c for c, _ in FRAME_DDL["element"]}


# --- rel_all ----------------------------------------------------------------

CONNECTORS = [
    {"Connector_ID": 10, "ea_guid": "{C10}", "Name": "uses",
     "Connector_Type": "Association", "Stereotype": "Uses",
     "Start_Object_ID": 1, "End_Object_ID": 2},
]


def test_a_relationship_with_both_endpoints_in_scope_is_kept():
    rows = relationship_rows(CONNECTORS, GUID_BY_ID)
    assert rows == [{"connector_id": 10, "source_guid": "{A}", "target_guid": "{B}",
                     "connector_type": "Association", "stereotype": "Uses",
                     "profile": "", "name": "uses"}]


def test_a_relationship_whose_endpoint_does_not_resolve_is_dropped():
    """A dangling edge inflates a count and makes an inner join quietly return
    fewer rows than the total somebody is reading."""
    c = dict(CONNECTORS[0], End_Object_ID=999)
    assert relationship_rows([c], GUID_BY_ID) == []


def test_a_relationship_leaving_the_scope_is_dropped():
    assert relationship_rows(CONNECTORS, GUID_BY_ID, guids_in_scope={"{A}"}) == []


def test_the_connector_profile_is_empty_unless_a_resolver_is_supplied():
    """Empty is honest for an extract that did not pull connector provenance. A
    guess here would read like a fact."""
    assert relationship_rows(CONNECTORS, GUID_BY_ID)[0]["profile"] == ""
    resolved = relationship_rows(CONNECTORS, GUID_BY_ID,
                                 profile_of=lambda g: NS if g == "{C10}" else "")
    assert resolved[0]["profile"] == NS


def test_relationship_rows_fit_the_frame_schema():
    rows = relationship_rows(CONNECTORS, GUID_BY_ID)
    assert set(rows[0]) == {c for c, _ in FRAME_DDL["rel_all"]}


# --- diagram, attribute, operation -----------------------------------------

def test_the_diagram_type_column_is_diagram_type_not_type():
    rows = diagram_rows([{"Diagram_ID": 7, "Name": "Context",
                          "Diagram_Type": "Component", "Package_ID": 5,
                          "Type": "wrong"}])
    assert rows[0]["diagram_type"] == "Component"
    assert set(rows[0]) == {c for c, _ in FRAME_DDL["diagram"]}


def test_diagrams_outside_the_scope_are_dropped():
    assert diagram_rows([{"Diagram_ID": 7, "Name": "X", "Diagram_Type": "Class",
                          "Package_ID": 99}], in_scope={5}) == []


def test_a_placement_needs_both_a_known_diagram_and_a_known_element():
    rows = diagram_object_rows(
        [{"Diagram_ID": 7, "Object_ID": 1}, {"Diagram_ID": 7, "Object_ID": 999},
         {"Diagram_ID": 8, "Object_ID": 1}],
        GUID_BY_ID, diagram_ids={7})
    assert rows == [{"diagram_id": 7, "ea_guid": "{A}"}]


def test_attribute_rows_use_ID_and_carry_the_reserved_word_columns():
    rows = attribute_rows([{"ID": 3, "Object_ID": 1, "Name": "balance",
                            "Type": "decimal", "Scope": "Public"}], GUID_BY_ID)
    assert rows == [{"attribute_id": 3, "element_guid": "{A}", "name": "balance",
                     "attr_type": "decimal", "scope": "Public"}]
    assert set(rows[0]) == {c for c, _ in FRAME_DDL["attribute"]}


def test_operation_rows_use_OperationID_because_EA_is_inconsistent():
    rows = operation_rows([{"OperationID": 4, "Object_ID": 2, "Name": "post",
                            "Type": "void", "Scope": "Public"}], GUID_BY_ID)
    assert rows[0]["operation_id"] == 4
    assert rows[0]["return_type"] == "void"
    assert set(rows[0]) == {c for c, _ in FRAME_DDL["operation"]}


def test_an_attribute_or_operation_on_an_unknown_element_is_dropped():
    assert attribute_rows([{"ID": 3, "Object_ID": 999, "Name": "x"}], GUID_BY_ID) == []
    assert operation_rows([{"OperationID": 4, "Object_ID": 999, "Name": "x"}],
                          GUID_BY_ID) == []


def test_an_attribute_on_an_excluded_element_is_dropped():
    assert attribute_rows([{"ID": 3, "Object_ID": 2, "Name": "x"}], GUID_BY_ID,
                          guids_in_scope={"{A}"}) == []


# --- the dangling-reference check ------------------------------------------

def test_a_frame_whose_references_all_resolve_reports_nothing():
    model, key = _model()
    rows = {
        "element": element_rows(ELEMENTS, model, {"{A}": [key], "{B}": [key]}),
        "rel_all": relationship_rows(CONNECTORS, GUID_BY_ID),
        "tag_value": [{"ea_guid": "{A}", "tag": "t", "value": "v"}],
    }
    assert dangling(rows) == []


def test_a_dangling_relationship_endpoint_is_reported():
    model, key = _model()
    rows = {
        "element": element_rows([ELEMENTS[0]], model, {"{A}": [key]}),
        "rel_all": relationship_rows(CONNECTORS, GUID_BY_ID),
    }
    assert dangling(rows) == [
        {"table": "rel_all", "column": "target_guid", "value": "{B}"}]


def test_a_tag_value_pointing_at_an_element_not_in_the_frame_is_reported():
    model, key = _model()
    rows = {
        "element": element_rows([ELEMENTS[0]], model, {"{A}": [key]}),
        "tag_value": [{"ea_guid": "{ZZZ}", "tag": "t", "value": "v"}],
    }
    assert dangling(rows) == [
        {"table": "tag_value", "column": "ea_guid", "value": "{ZZZ}"}]


def test_every_frame_table_holding_a_guid_reference_is_checked():
    """A table added to the frame without being added here would never be checked,
    which is the silent-skip failure this toolchain keeps finding."""
    from frame import FOREIGN_GUIDS
    guid_columns = {
        name: tuple(c for c, t in spec
                    if t == "TEXT" and (c.endswith("guid") or c == "ea_guid"))
        for name, spec in FRAME_DDL.items()
    }
    expected = {n: c for n, c in guid_columns.items() if c and n != "element"}
    assert set(FOREIGN_GUIDS) == set(expected)
    for name, cols in expected.items():
        assert set(FOREIGN_GUIDS[name]) == set(cols), name
