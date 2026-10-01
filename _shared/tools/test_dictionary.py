#!/usr/bin/env python3
"""Tests for the data dictionary and the build manifest.

    python -m pytest _shared/tools/test_dictionary.py -q

Nothing here touches a repository, a COM object or the filesystem.
"""
from __future__ import annotations

import json

from ddl import FRAME_DDL
from dictionary import FRAME_PURPOSE, data_dictionary, manifest
from ea_census import Entity, ElementCensus, TagStat
from load import LoadResult
from reconcile import Reconciliation
from report_model import build_report_model

NS = "WestbrookBankArchitecture"

MDG = {
    "tech_id": "WBA",
    "technology_name": "WBA (Westbrook Bank Architecture)",
    "stereotypes": [
        {"name": "WBABusinessApplication", "alias": "Business Application",
         "notes": "Core business application", "tagged_values": [
             {"name": "criticality", "type": "enumeration",
              "description": "How badly its loss would hurt",
              "values": ["Mission-Critical", "Standard"]},
         ]},
    ],
}


def _census(*entities):
    c = ElementCensus()
    c.entities = list(entities)
    return c


def _entity(key, stereo, n, metaclass="Component", fqname="", profile=""):
    e = Entity(key=key, stereotype=stereo, fqname=fqname, profile=profile)
    e.guids.update("{%s%d}" % (stereo, i) for i in range(n))
    e.metaclasses[metaclass] = n
    return e


def _stat(tag, present, populated, values):
    s = TagStat(tag=tag, present=present, populated=populated)
    for v in values:
        s.values[v] += 1
    return s


def _declared_model():
    key = f"{NS}::WBABusinessApplication"
    ent = _entity(key, "WBABusinessApplication", 4, fqname=key, profile=NS)
    stats = {key: [_stat("criticality", 4, 3, ["Standard"] * 2 + ["Mission-Critical"])]}
    return build_report_model(_census(ent), stats, MDG)


# --- the drift guard --------------------------------------------------------

def test_every_frame_table_has_a_stated_purpose():
    """`FRAME_TABLES` and `FRAME_DDL` drifted once, and the symptom was a table
    that existed while being invisible to everything reading the model. A
    dictionary silently missing a table is the same failure one layer up."""
    assert set(FRAME_PURPOSE) == set(FRAME_DDL)


def test_the_frame_section_lists_every_table_and_its_columns():
    md = data_dictionary(_declared_model())
    for name, spec in FRAME_DDL.items():
        assert f"`{name}`" in md
        for col, _ in spec:
            assert f"`{col}`" in md


# --- enrichment actually reaching a reader ---------------------------------

def test_the_alias_description_and_type_from_the_technology_all_appear():
    md = data_dictionary(_declared_model())
    assert "business_application" in md                   # alias -> table name
    assert "Business Application" in md                   # the alias itself
    assert "Core business application" in md              # stereotype notes
    assert "How badly its loss would hurt" in md          # tag description
    assert "WBABusinessApplication" in md


def test_a_declared_enumeration_is_labelled_declared():
    md = data_dictionary(_declared_model())
    assert "declared: `Mission-Critical`, `Standard`" in md


def test_an_observed_enumeration_is_labelled_observed_not_passed_off_as_declared():
    """Observation only shows what happened to be used. Presenting it as the
    technology's domain is how a missing value becomes an invisible gap."""
    key = "Thing|Component"
    ent = _entity(key, "Thing", 3)
    stats = {key: [_stat("status", 3, 3, ["live", "live", "dead"])]}
    md = data_dictionary(build_report_model(_census(ent), stats, {}))
    assert "observed: `dead`, `live`" in md
    assert "declared:" not in md


def test_coverage_is_reported_as_populated_over_total():
    md = data_dictionary(_declared_model())
    assert "75% (3/4)" in md                              # 3 populated of 4 rows


def test_an_undeclared_stereotype_is_called_out_not_quietly_tabled():
    ent = _entity("Ghost|Class", "Ghost", 2, metaclass="Class")
    md = data_dictionary(build_report_model(_census(ent), {}, MDG))
    assert "observed but never declared" in md


def test_a_heterogeneous_stereotype_gets_a_warning_with_the_spread():
    e = Entity(key="k", stereotype="WBASystemOfRecord", fqname=f"{NS}::X", profile=NS)
    e.guids.update({"{1}", "{2}", "{3}"})
    e.metaclasses.update({"Class": 1, "Component": 2})
    md = data_dictionary(build_report_model(_census(e), {}, MDG))
    assert "several metaclasses" in md
    assert "Class (1)" in md and "Component (2)" in md


def test_overflow_tags_are_named_so_the_routing_is_visible():
    key = "Thing|Component"
    ent = _entity(key, "Thing", 100)
    stats = {key: [_stat("common", 100, 100, ["x"] * 100),
                   _stat("rare", 2, 1, ["y"])]}
    md = data_dictionary(build_report_model(_census(ent), stats, {}))
    assert "overflow_tag" in md
    assert "`rare`" in md


def test_a_table_with_no_columns_says_so_rather_than_showing_an_empty_grid():
    ent = _entity("Bare|Component", "Bare", 2)
    md = data_dictionary(build_report_model(_census(ent), {}, {}))
    assert "no tagged values cleared the sparse threshold" in md


def test_multi_value_candidates_are_surfaced_as_a_question():
    key = "Thing|Component"
    ent = _entity(key, "Thing", 4)
    stats = {key: [_stat("scope", 4, 4, ["GLBA, FFIEC", "GLBA, SOX"])]}
    md = data_dictionary(build_report_model(_census(ent), stats, {},
                                           sparse_threshold=0.0))
    assert "Possibly multi-valued, not acted on" in md
    assert "`scope`" in md


def test_the_caveats_a_reader_would_otherwise_rediscover_are_stated():
    md = data_dictionary(_declared_model())
    assert "Coverage is populated, not present" in md
    assert "tag_value" in md
    assert "first table only" in md


def test_untyped_and_excluded_elements_are_accounted_for():
    c = _census(_entity("Thing|Component", "Thing", 1))
    c.untyped_guids.update({"{a}", "{b}"})
    c.excluded_ea_internal["EATool"] = 9
    md = data_dictionary(build_report_model(c, {}, {}))
    assert "**2** element(s) carry no stereotype" in md
    assert "ea_internal:EATool" in md


def test_domain_violations_appear_under_the_table_they_belong_to():
    md = data_dictionary(_declared_model(), domain_violations=[
        {"table": "business_application", "column": "criticality",
         "tag": "criticality", "value": "Pretty Important", "count": 2}])
    assert "Outside the declared enumeration" in md
    assert "`Pretty Important`" in md
    assert "(2 row(s))" in md


def test_a_pipe_in_a_description_does_not_break_the_table_it_sits_in():
    mdg = {"stereotypes": [{"name": "Thing", "notes": "a | b",
                            "tagged_values": [
                                {"name": "t", "type": "String",
                                 "description": "x | y"}]}]}
    key = "Thing|Component"
    ent = _entity(key, "Thing", 2)
    stats = {key: [_stat("t", 2, 2, ["v", "v"])]}
    md = data_dictionary(build_report_model(_census(ent), stats, mdg))
    assert "x \\| y" in md
    assert "a \\| b" in md


def test_an_empty_model_produces_a_dictionary_rather_than_an_exception():
    md = data_dictionary(build_report_model(_census(), {}, {}))
    assert "The census found no stereotyped elements in scope." in md


def test_the_dictionary_is_deterministic():
    m = _declared_model()
    assert data_dictionary(m, run_id="r", run_at="t") == \
        data_dictionary(m, run_id="r", run_at="t")


def test_the_run_identity_is_recorded_when_given():
    md = data_dictionary(_declared_model(), run_id="run-7",
                         run_at="2026-10-01 12:00:00",
                         repository="WestbrookBank.qea")
    assert "`run-7`" in md
    assert "2026-10-01 12:00:00" in md
    assert "WestbrookBank.qea" in md


# --- the manifest -----------------------------------------------------------

def _load_result():
    return LoadResult(database="r.sqlite", run_id="run-7",
                      rows_by_table={"business_application": 4, "load_run": 1})


def test_the_manifest_is_json_serialisable():
    m = manifest(_declared_model(), _load_result(), run_id="run-7")
    assert json.loads(json.dumps(m))["run_id"] == "run-7"


def test_a_manifest_with_no_reconciliation_is_not_ok():
    """An absent check is not a pass. The release gate in this repository reports
    GREEN for a check it skipped, which is filed as a defect - not repeating it."""
    m = manifest(_declared_model(), _load_result(), run_id="run-7")
    assert m["ok"] is False
    assert m["reconciliation"] is None


def test_a_failed_reconciliation_makes_the_manifest_not_ok():
    rec = Reconciliation()
    rec.add("entity", "business_application", 4, 3)
    m = manifest(_declared_model(), _load_result(), reconciliation=rec)
    assert m["ok"] is False
    assert m["reconciliation"]["failures"] == 1


def test_a_skipped_check_also_makes_the_manifest_not_ok():
    rec = Reconciliation()
    rec.add("entity", "business_application", 4, 4)
    rec.skip("scalar", "connectors", "no repository figure supplied")
    m = manifest(_declared_model(), _load_result(), reconciliation=rec)
    assert m["ok"] is False


def test_a_passing_reconciliation_makes_the_manifest_ok():
    rec = Reconciliation()
    rec.add("entity", "business_application", 4, 4)
    m = manifest(_declared_model(), _load_result(), reconciliation=rec)
    assert m["ok"] is True


def test_the_manifest_carries_the_load_and_the_tables_it_built():
    m = manifest(_declared_model(), _load_result(), run_id="run-7")
    assert m["load"]["rows_loaded"] == 4          # load_run excluded
    assert m["tables"][0]["name"] == "business_application"
    assert m["tables"][0]["columns"] == ["criticality"]
    assert m["technology"]["id"] == "WBA"
    assert m["frame"] == list(FRAME_DDL)


def test_the_manifest_carries_domain_violations_for_a_pipeline_to_read():
    v = [{"table": "business_application", "column": "criticality",
          "tag": "criticality", "value": "Pretty Important", "count": 2}]
    m = manifest(_declared_model(), _load_result(), domain_violations=v)
    assert m["domain_violations"] == v


def test_warnings_from_the_load_survive_into_the_manifest():
    lr = _load_result()
    lr.warnings.append("3 tag row(s) reached no table")
    assert manifest(_declared_model(), lr)["load"]["warnings"] == [
        "3 tag row(s) reached no table"]
