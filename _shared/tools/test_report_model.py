#!/usr/bin/env python3
"""Tests for the report model.

    python -m pytest _shared/tools/test_report_model.py -q

Nothing here touches a repository, a COM object or the filesystem.
"""
from __future__ import annotations

from ea_census import Entity, ElementCensus, TagStat
from report_model import (
    DEFAULT_SPARSE_THRESHOLD,
    FRAME_TABLES,
    build_report_model,
    detect_multi_value_candidates,
)

NS = "WestbrookBankArchitecture"

MDG = {
    "tech_id": "WBA",
    "technology_name": "WBA (Westbrook Bank Architecture)",
    "stereotypes": [
        {"name": "WBABusinessApplication", "alias": "Business Application",
         "base_metaclass": "Component", "notes": "Core business application",
         "tagged_values": [
             {"name": "criticality", "type": "enumeration", "description": "Criticality",
              "values": ["Mission-Critical", "Business-Critical", "Important", "Standard"]},
             {"name": "humanInLoopRequired", "type": "boolean", "values": ["true", "false"]},
             {"name": "businessOwner", "type": "String", "description": "Owning team"},
         ]},
    ],
}


def entity(key, stereo, n, metaclass="Component", fqname="", profile=""):
    e = Entity(key=key, stereotype=stereo, fqname=fqname, profile=profile)
    e.guids.update("{%s%d}" % (stereo, i) for i in range(n))
    e.metaclasses[metaclass] = n
    return e


def stat(tag, present, populated, values=None):
    s = TagStat(tag=tag, present=present, populated=populated)
    for v in (values or []):
        s.values[v] += 1
    return s


def census_of(*entities):
    c = ElementCensus()
    c.entities = list(entities)
    return c


def test_alias_from_the_technology_becomes_the_table_name():
    e = entity("%s::WBABusinessApplication" % NS, "WBABusinessApplication", 3,
               fqname="%s::WBABusinessApplication" % NS, profile=NS)
    m = build_report_model(census_of(e), {}, MDG)
    assert m.tables[0].name == "business_application"
    assert m.tables[0].alias == "Business Application"
    assert m.tables[0].declared is True


def test_undeclared_entity_still_gets_a_table():
    e = entity("Thing|Component", "Thing", 2)
    m = build_report_model(census_of(e), {}, MDG)
    assert m.tables[0].name == "thing"
    assert m.tables[0].declared is False


def test_a_single_instance_entity_still_gets_a_table():
    """An earlier prototype skipped stereotypes with fewer than three instances
    and dropped sixteen of them - exactly the governance drift a census exists
    to surface."""
    e = entity("Rare|Class", "Rare", 1, metaclass="Class")
    m = build_report_model(census_of(e), {}, MDG)
    assert [t.name for t in m.tables] == ["rare"]
    assert m.tables[0].row_count == 1


def test_declared_type_drives_sql_type():
    key = "%s::WBABusinessApplication" % NS
    e = entity(key, "WBABusinessApplication", 4, fqname=key, profile=NS)
    stats = {key: [stat("criticality", 4, 4, ["Standard"] * 4),
                   stat("humanInLoopRequired", 4, 4, ["true"] * 4)]}
    cols = {c.source_tag: c for c in build_report_model(census_of(e), stats, MDG).tables[0].columns}
    assert cols["criticality"].sql_type == "TEXT"
    assert cols["humanInLoopRequired"].sql_type == "INTEGER"


def test_declared_enum_domain_beats_the_observed_one():
    """Observation only ever shows the values that happen to have been used, so
    the declared domain is the truth and the gap between them is a finding."""
    key = "%s::WBABusinessApplication" % NS
    e = entity(key, "WBABusinessApplication", 4, fqname=key, profile=NS)
    stats = {key: [stat("criticality", 4, 4, ["Standard", "Standard", "Important", "Important"])]}
    col = build_report_model(census_of(e), stats, MDG).tables[0].columns[0]
    assert col.enum_source == "declared"
    assert len(col.enum_values) == 4           # not the 2 observed


def test_observed_domain_used_when_nothing_is_declared():
    e = entity("Thing|Component", "Thing", 4)
    stats = {"Thing|Component": [stat("status", 4, 4, ["a", "a", "b", "b"])]}
    col = build_report_model(census_of(e), stats, MDG).tables[0].columns[0]
    assert col.enum_source == "observed"
    assert col.enum_values == ["a", "b"]


def test_sparse_tags_go_to_overflow_and_are_named_not_dropped():
    e = entity("Thing|Component", "Thing", 100)
    stats = {"Thing|Component": [stat("common", 100, 100, ["x"] * 100),
                                 stat("rare", 2, 1, ["y"])]}
    t = build_report_model(census_of(e), stats, MDG, sparse_threshold=0.05).tables[0]
    assert [c.source_tag for c in t.columns] == ["common"]
    assert t.overflow_tags == ["rare"]          # routed, and visible


def test_sparse_threshold_is_a_parameter_not_a_constant():
    e = entity("Thing|Component", "Thing", 100)
    stats = {"Thing|Component": [stat("rare", 2, 2, ["y", "z"])]}
    assert build_report_model(census_of(e), stats, MDG, sparse_threshold=0.5).tables[0].columns == []
    kept = build_report_model(census_of(e), stats, MDG, sparse_threshold=0.01).tables[0]
    assert [c.source_tag for c in kept.columns] == ["rare"]


def test_coverage_on_a_column_is_populated_not_present():
    e = entity("Thing|Component", "Thing", 10)
    stats = {"Thing|Component": [stat("owner", 10, 4, ["a"] * 4)]}
    col = build_report_model(census_of(e), stats, MDG, sparse_threshold=0.0).tables[0].columns[0]
    assert col.present == 10
    assert col.populated == 4
    assert col.coverage == 0.4


def test_multi_value_candidates_are_reported_but_not_split():
    """The module refuses to decide this. A genuinely multi-valued tag and a
    free-text field containing a comma are indistinguishable by declared type -
    both are String - and guessing corrupts data silently."""
    e = entity("Thing|Component", "Thing", 4)
    stats = {"Thing|Component": [stat("scope", 4, 4, ["GLBA, FFIEC", "GLBA, SOX", "SOX"])]}
    m = build_report_model(census_of(e), stats, MDG, sparse_threshold=0.0)
    assert "scope" in m.multi_value_candidates
    assert m.tables[0].columns[0].multi_valued is False      # NOT acted on


def test_multi_valued_is_set_only_when_the_caller_names_it():
    e = entity("Thing|Component", "Thing", 4)
    stats = {"Thing|Component": [stat("scope", 4, 4, ["GLBA, FFIEC"])]}
    m = build_report_model(census_of(e), stats, MDG, sparse_threshold=0.0,
                           multi_valued={"scope"})
    assert m.tables[0].columns[0].multi_valued is True


def test_candidate_detection_ignores_a_single_stray_comma():
    s = stat("owner", 10, 10, ["Team A", "Team B", "Risk, Compliance & Audit"])
    assert detect_multi_value_candidates([s], min_share=0.5) == []
    assert detect_multi_value_candidates([s], min_share=0.3) == ["owner"]


def test_colliding_table_names_are_qualified():
    a = entity("%s::WBABusinessService" % NS, "WBABusinessService", 2,
               fqname="%s::WBABusinessService" % NS, profile=NS)
    b = entity("TOGAF::BusinessService", "BusinessService", 1,
               fqname="TOGAF::BusinessService", profile="TOGAF")
    mdg = {"stereotypes": [
        {"name": "WBABusinessService", "alias": "Business Service", "tagged_values": []},
        {"name": "BusinessService", "alias": "Business Service", "tagged_values": []},
    ]}
    names = [t.name for t in build_report_model(census_of(a, b), {}, mdg).tables]
    assert names == ["business_service", "togaf_business_service"]
    assert len(set(names)) == 2


def test_heterogeneous_metaclass_is_carried_onto_the_table():
    e = Entity(key="k", stereotype="WBASystemOfRecord", fqname="%s::X" % NS, profile=NS)
    e.guids.update({"{1}", "{2}"})
    e.metaclasses.update({"Component": 1, "Class": 1})
    t = build_report_model(census_of(e), {}, MDG).tables[0]
    assert t.heterogeneous is True
    assert t.metaclasses == {"Class": 1, "Component": 1}


def test_exclusions_and_untyped_are_carried_into_the_model():
    c = census_of(entity("Thing|Component", "Thing", 1))
    c.excluded_ea_internal["EATool"] = 9
    c.excluded_profile_authoring["stereotype"] = 20
    c.untyped_guids.update({"{a}", "{b}"})
    m = build_report_model(c, {}, MDG)
    assert m.excluded["ea_internal:EATool"] == 9
    assert m.excluded["profile_authoring:stereotype"] == 20
    assert m.untyped_elements == 2


def test_frame_is_present_and_includes_the_load_bearing_tables():
    m = build_report_model(census_of(entity("T|Component", "T", 1)), {}, MDG)
    assert m.frame == list(FRAME_TABLES)
    for required in ("element", "rel_all", "tag_value", "tag_coverage", "load_run"):
        assert required in m.frame


def test_model_is_deterministic_and_serializable():
    e1 = entity("A|Component", "A", 3)
    e2 = entity("B|Component", "B", 3)
    stats = {"A|Component": [stat("x", 3, 3, ["v"] * 3)]}
    a = build_report_model(census_of(e1, e2), stats, MDG)
    b = build_report_model(census_of(e1, e2), stats, MDG)
    assert a.to_dict() == b.to_dict()
    assert isinstance(a.to_dict(), dict)


def test_default_threshold_is_declared_not_hidden():
    assert DEFAULT_SPARSE_THRESHOLD == 0.05
