#!/usr/bin/env python3
"""Tests for the host-side pivot.

    python -m pytest _shared/tools/test_pivot.py -q

Nothing here touches a repository, a COM object or the filesystem.

The emphasis is on the places data can go missing or be double-counted, because
"the load never discards data" is the property this module is for.
"""
from __future__ import annotations

from pivot import pivot
from report_model import Column, ReportModel, Table


def col(tag, multi=False, present=1, populated=1):
    return Column(name=tag.lower(), source_tag=tag, multi_valued=multi,
                  present=present, populated=populated, coverage=1.0)


def model_with(*tables):
    return ReportModel(tables=list(tables))


def tbl(name, key, cols=(), overflow=(), rows=1):
    return Table(name=name, entity_key=key, stereotype=name,
                 columns=list(cols), overflow_tags=list(overflow), row_count=rows)


ELEMENTS = [
    {"ea_guid": "{1}", "Name": "Payments", "Object_Type": "Component"},
    {"ea_guid": "{2}", "Name": "Ledger", "Object_Type": "Class"},
]


def props(*triples):
    return [{"ea_guid": g, "Property": p, "Value": v} for g, p, v in triples]


def test_tags_become_columns_on_the_entity_row():
    m = model_with(tbl("app", "K", [col("criticality")]))
    r = pivot(m, ELEMENTS, props(("{1}", "criticality", "High")), {"{1}": ["K"]})
    row = r.rows["app"][0]
    assert row["ea_guid"] == "{1}"
    assert row["name"] == "Payments"
    assert row["metaclass"] == "Component"
    assert row["criticality"] == "High"


def test_a_column_with_no_value_is_present_as_none_not_absent():
    """A missing key and a null are different things downstream."""
    m = model_with(tbl("app", "K", [col("criticality"), col("owner")]))
    r = pivot(m, ELEMENTS, props(("{1}", "criticality", "High")), {"{1}": ["K"]})
    row = r.rows["app"][0]
    assert "owner" in row and row["owner"] is None


def test_a_multi_stereotype_element_gets_a_row_in_each_table():
    """It IS several things, so it belongs in several tables. A census that
    reads only t_object.Stereotype puts it in one and undercounts the other."""
    m = model_with(tbl("app", "A", [col("criticality")]),
                   tbl("sor", "B", [col("criticality")]))
    r = pivot(m, ELEMENTS, props(("{1}", "criticality", "High")), {"{1}": ["A", "B"]})
    assert [x["ea_guid"] for x in r.rows["app"]] == ["{1}"]
    assert [x["ea_guid"] for x in r.rows["sor"]] == ["{1}"]


def test_a_multi_stereotype_element_writes_its_tag_values_only_ONCE():
    """The bridge is keyed by element, not by table. Writing it per table would
    double every count taken through it - which is the exact failure mode the
    bridge exists to prevent."""
    m = model_with(tbl("app", "A", [col("criticality")]),
                   tbl("sor", "B", [col("criticality")]))
    r = pivot(m, ELEMENTS, props(("{1}", "criticality", "High")), {"{1}": ["A", "B"]})
    assert len(r.tag_value) == 1
    assert r.tag_value[0] == {"ea_guid": "{1}", "tag": "criticality", "value": "High"}


def test_an_empty_value_produces_no_bridge_row():
    """An empty tag is coverage, not a value. Writing it would create a phantom
    dimension member that groups rows under nothing."""
    m = model_with(tbl("app", "K", [col("owner")]))
    r = pivot(m, ELEMENTS, props(("{1}", "owner", "")), {"{1}": ["K"]})
    assert r.tag_value == []
    assert r.rows["app"][0]["owner"] == ""


def test_multi_valued_tags_split_only_when_the_model_says_so():
    m = model_with(tbl("app", "K", [col("scope", multi=True)]))
    r = pivot(m, ELEMENTS, props(("{1}", "scope", "GLBA, FFIEC")), {"{1}": ["K"]})
    assert sorted(x["value"] for x in r.tag_value) == ["FFIEC", "GLBA"]


def test_an_unsplit_tag_keeps_its_comma():
    """The guard against corrupting a team name like "Risk, Compliance & Audit",
    which is one value. The declared type cannot tell the two cases apart."""
    m = model_with(tbl("app", "K", [col("owner")]))
    r = pivot(m, ELEMENTS, props(("{1}", "owner", "Risk, Compliance & Audit")), {"{1}": ["K"]})
    assert [x["value"] for x in r.tag_value] == ["Risk, Compliance & Audit"]


def test_the_flattened_column_survives_alongside_the_bridge():
    """Both, deliberately: the column is for display, the bridge is for
    measures. Dropping either breaks one of the two."""
    m = model_with(tbl("app", "K", [col("scope", multi=True)]))
    r = pivot(m, ELEMENTS, props(("{1}", "scope", "GLBA, FFIEC")), {"{1}": ["K"]})
    assert r.rows["app"][0]["scope"] == "GLBA, FFIEC"
    assert len(r.tag_value) == 2


def test_sparse_tags_are_routed_to_overflow_not_dropped():
    m = model_with(tbl("app", "K", [col("criticality")], overflow=["rare"]))
    r = pivot(m, ELEMENTS,
              props(("{1}", "criticality", "High"), ("{1}", "rare", "x")), {"{1}": ["K"]})
    assert r.overflow == [{"ea_guid": "{1}", "tag": "rare", "value": "x"}]
    assert "rare" not in r.rows["app"][0]


def test_a_value_on_an_element_in_no_table_still_reaches_the_bridge():
    """Nothing is lost: the bridge is keyed by element, not by table, so an
    element with no entity table still contributes its values. This is the
    honest remainder working, and it is why `unplaced` counts only rows that
    reached nowhere at all."""
    m = model_with(tbl("app", "K", [col("criticality")]))
    r = pivot(m, ELEMENTS, props(("{9}", "criticality", "High")), {"{1}": ["K"]})
    assert r.tag_value == [{"ea_guid": "{9}", "tag": "criticality", "value": "High"}]
    assert r.unplaced == []


def test_coverage_rows_come_from_the_model_so_one_number_has_one_source():
    m = model_with(tbl("app", "K", [col("criticality", present=8, populated=3)], rows=8))
    r = pivot(m, ELEMENTS, [], {})
    assert r.coverage == [{"table_name": "app", "tag": "criticality",
                           "present": 8, "populated": 3, "total": 8, "coverage": 1.0}]


def test_every_table_in_the_model_gets_a_row_list_even_when_empty():
    m = model_with(tbl("app", "A"), tbl("sor", "B"))
    r = pivot(m, ELEMENTS, [], {})
    assert r.rows == {"app": [], "sor": []}


def test_pivot_is_deterministic():
    m = model_with(tbl("app", "K", [col("criticality")]))
    p = props(("{2}", "criticality", "Low"), ("{1}", "criticality", "High"))
    a = pivot(m, ELEMENTS, p, {"{1}": ["K"], "{2}": ["K"]})
    b = pivot(m, ELEMENTS, list(reversed(p)), {"{2}": ["K"], "{1}": ["K"]})
    assert [x["ea_guid"] for x in a.rows["app"]] == [x["ea_guid"] for x in b.rows["app"]]
    assert a.tag_value == b.tag_value


def test_total_rows_counts_placements_not_elements():
    m = model_with(tbl("app", "A"), tbl("sor", "B"))
    r = pivot(m, ELEMENTS, [], {"{1}": ["A", "B"]})
    assert r.total_rows == 2


def test_tags_on_an_untyped_element_are_NOT_reported_as_lost():
    """REGRESSION. An element in no entity table still gets its values into the
    bridge, because the bridge is keyed by element rather than by table. Calling
    that "unplaced" reported 88 false losses on a real model and would have sent
    someone hunting a data-loss bug that did not exist."""
    m = model_with(tbl("app", "K", [col("criticality")]))
    r = pivot(m, ELEMENTS, props(("{2}", "owner", "Data Team")), {"{1}": ["K"]})
    assert r.unplaced == []
    assert r.tag_value == [{"ea_guid": "{2}", "tag": "owner", "value": "Data Team"}]


def test_an_empty_tag_on_an_untyped_element_IS_reported_as_unplaced():
    """The genuinely lost case: no column, no overflow, and nothing for the
    bridge to carry."""
    m = model_with(tbl("app", "K", [col("criticality")]))
    r = pivot(m, ELEMENTS, props(("{2}", "owner", "")), {"{1}": ["K"]})
    assert r.unplaced == [{"ea_guid": "{2}", "tag": "owner", "value": ""}]


def test_tags_on_excluded_elements_are_skipped_entirely():
    """REGRESSION. EA's report packages and model documents carry ReportName,
    ReportStatus and SearchValue tags. The census excludes those elements, so
    the pivot must not treat their tags as business data that failed to land."""
    m = model_with(tbl("app", "K", [col("criticality")]))
    r = pivot(m, ELEMENTS, props(("{2}", "ReportName", ""), ("{2}", "ReportStatus", "x")),
              {"{1}": ["K"]}, excluded_guids={"{2}"})
    assert r.unplaced == []
    assert r.tag_value == []
