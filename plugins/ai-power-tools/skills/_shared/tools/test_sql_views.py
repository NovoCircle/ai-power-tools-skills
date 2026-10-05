#!/usr/bin/env python3
"""Tests for the SQL view emitter.

    python -m pytest _shared/tools/test_sql_views.py -q

Nothing here touches a database. The generator is pure, so what is testable
hermetically is the SHAPE of the SQL; whether it returns the right rows is
settled by `research/reporting-database/acceptance_pipeline.py --sqlserver`,
which runs the views against a real SQL Server repository and compares every
table against the database built from the same census.

Several of these encode defects that acceptance run found, because every one of
them produced a view that ran perfectly well and returned the wrong rows.
"""
from __future__ import annotations

import pytest

from ddl import FRAME_DDL, physical
from report_model import Column, ReportModel, Table
from sql_views import (SUPPORTED_DIALECTS, DialectError, build_views,
                       drop_script, placement_predicate)


def declared(name="business_application", key="WBA::WBABusinessApplication",
             cols=(("criticality", "TEXT"),), overflow=()):
    return Table(name=name, entity_key=key, stereotype="WBABusinessApplication",
                 declared=True, overflow_tags=list(overflow),
                 columns=[Column(name=c, source_tag=c, sql_type=t) for c, t in cols])


def adhoc(name="business_actor", key="BusinessActor|Actor"):
    return Table(name=name, entity_key=key, stereotype="BusinessActor",
                 declared=False)


def model(tables=None):
    return ReportModel(technology_id="WBA", namespace="WBA",
                       tables=list(tables) if tables else [declared()])


# ------------------------------------------------------------- the dialect


def test_only_a_tested_dialect_is_emitted():
    """Emitting SQL for an untested backend hands a customer a script nobody has
    run. APT-2026-0218 is already open on a join that may not survive Jet."""
    with pytest.raises(DialectError, match="not a supported dialect"):
        build_views(model(), dialect="jet")


def test_the_supported_list_is_explicit():
    assert SUPPORTED_DIALECTS == ("sqlserver",)
    assert build_views(model(), dialect="sqlserver").dialect == "sqlserver"


# ----------------------------------------------------------- the view set


def test_a_view_per_vocabulary_table_plus_the_frame_plus_the_parser():
    vs = build_views(model([declared(), adhoc()]))
    assert len(vs.views) == 2 + len(FRAME_DDL) + 1
    assert "_stereo_block" in vs.views
    for frame_key in FRAME_DDL:
        assert physical(frame_key) in vs.views


def test_the_parser_and_the_hub_come_first():
    """The key map reads the parser and everything else is scoped to the key
    map - the same ordering reason the loader writes the frame first."""
    names = build_views(model()).names
    assert names.index("_stereo_block") < names.index(physical("element"))
    assert names.index(physical("element")) < names.index(physical("rel_all"))


def test_views_are_named_as_the_database_names_its_tables():
    vs = build_views(model())
    assert physical("element") == "_keymap"
    assert "_keymap" in vs.views
    assert "element" not in vs.views


def test_the_drop_script_reverses_the_order_so_a_regeneration_re_runs():
    vs = build_views(model())
    assert drop_script(vs).index("_stereo_block") > drop_script(vs).index("_keymap")


# -------------------------------------------------------------- placement


def test_a_profile_bound_table_matches_on_its_FQNAME():
    sql = placement_predicate(declared(key="WBA::WBABusinessApplication"))
    assert "sb.fqname = 'WBA::WBABusinessApplication'" in sql
    assert "o.Object_Type" not in sql


def test_an_ad_hoc_table_matches_on_NAME_AND_METACLASS():
    """`ea_census.entity_key` keys an ad-hoc application `name|metaclass`
    because a bare name is ambiguous across languages."""
    sql = placement_predicate(adhoc(key="BusinessActor|Actor"))
    assert "sb.stereo_name = 'BusinessActor'" in sql
    assert "o.Object_Type = 'Actor'" in sql
    assert "sb.fqname = ''" in sql


def test_an_ad_hoc_table_also_falls_back_to_the_bare_stereotype_column():
    """MEASURED. An element with NO xref row at all is still stereotyped - the
    census says so and two elements on the reference model are exactly that.
    Without this clause the key map came out 2 short and both their tables were
    empty, while every view still ran without error."""
    sql = placement_predicate(adhoc(key="SystemSoftware|Component"))
    assert "NOT EXISTS" in sql
    assert "o.Stereotype = 'SystemSoftware'" in sql


def test_reading_only_the_fqname_form_is_what_emptied_fourteen_tables():
    """Regression guard with the measurement attached: 14 of 29 vocabulary
    tables returned 0 rows when ad-hoc applications were not placed."""
    sql = placement_predicate(adhoc())
    assert "fqname" in sql and "stereo_name" in sql


# ------------------------------------------------------------- the parsing


def test_blocks_are_split_rather_than_substring_matched():
    """`has an FQName` is a property of a BLOCK, not of the row. A
    multi-stereotype element packs several blocks into one Description, so
    matching the whole string cannot tell an ad-hoc application apart from some
    other stereotype on the same element that happens to be profile-bound."""
    sql = build_views(model()).views["_stereo_block"]
    assert "STRING_SPLIT" in sql
    assert "CHAR(1)" in sql, "a single-character separator, so blocks are split"
    assert "'@STEREO;%'" in sql


def test_the_parser_covers_connector_properties_too():
    sql = build_views(model()).views["_stereo_block"]
    assert "x.Type" not in sql.split("WHERE")[1], \
        "filtering to element property here would hide connector stereotypes"
    assert "applies_to" in sql


# --------------------------------------------------------------- the frame


def test_the_key_map_names_the_first_table_in_model_order():
    """What `frame.element_rows` writes for a multi-stereotype element. A CASE
    returns on first match, which is exactly that rule."""
    vs = build_views(model([declared(name="first", key="WBA::A"),
                            declared(name="second", key="WBA::B")]))
    sql = vs.views[physical("element")]
    assert sql.index("'first'") < sql.index("'second'")
    assert "CASE" in sql


def test_relationships_require_both_endpoints_placed():
    """An edge touching an unplaced element dangles, and a dangling row makes an
    inner join quietly return fewer rows than a total read elsewhere."""
    sql = build_views(model()).views[physical("rel_all")]
    assert sql.count(f"JOIN [{physical('element')}]") == 2


def test_the_diagram_view_is_NOT_scoped_to_the_key_map():
    """A diagram exists whether or not anything on it is placed. Measured: 10 of
    25 diagrams hold no logical object at all."""
    assert physical("element") not in build_views(model()).views[physical("diagram")]


def test_overflow_is_scoped_by_placement_not_by_entity_table():
    """`entity_table` names only the FIRST table a multi-stereotype element
    landed in, so scoping on it drops that element's overflow for every other
    table. Measured: 2 rows emitted against the 69 the pivot writes."""
    sql = build_views(model([declared(overflow=("pciScopeJustification",))])
                      ).views[physical("overflow_tag")]
    assert "entity_table" not in sql
    assert "sb.fqname" in sql


def test_overflow_does_NOT_filter_empty_values():
    """The one place the frame's two bridges disagree: `pivot` writes an
    overflow row whether or not the value is populated, while `tag_value` writes
    only populated ones. The view matches the pivot, because the requirement is
    that the paths agree - differing silently here would hide the asymmetry
    rather than settle it."""
    sql = build_views(model([declared(overflow=("pciScopeJustification",))])
                      ).views[physical("overflow_tag")]
    overflow = sql.split("CREATE VIEW")[-1]
    assert "LTRIM(RTRIM(COALESCE(p.Value" not in overflow


def test_tag_value_DOES_filter_empty_values():
    sql = build_views(model()).views[physical("tag_value")]
    assert "LTRIM(RTRIM(COALESCE(p.Value, ''))) <> ''" in sql


def test_a_multi_valued_tag_is_split_and_a_single_valued_one_is_not():
    """A team name like "Risk, Compliance & Audit" is ONE value containing a
    comma. Only what the caller declared multi-valued is split."""
    t = declared(cols=(("regulatory_scope", "TEXT"),))
    t.columns[0].multi_valued = True
    sql = build_views(model([t])).views[physical("tag_value")]
    assert "STRING_SPLIT" in sql
    assert "NOT IN ('regulatory_scope')" in sql


# ------------------------------------------------------------ the header


def test_the_header_states_the_regeneration_trigger():
    """The views are static and the data is live, so an element stereotyped
    after generation appears immediately but a NEW STEREOTYPE does not get a
    view until they are regenerated. That has to be stated, not discovered."""
    vs = build_views(model())
    assert "Regenerate" in vs.header
    assert "new stereotype" in vs.header.lower()


def test_the_header_stamps_the_ea_build_when_given_one():
    """EA's physical schema is not a public contract, and in this path a change
    to it breaks views the CUSTOMER owns, silently, on upgrade."""
    assert "1716" in build_views(model(), ea_build="1716").header
    assert "ea build" not in build_views(model()).header


def test_the_script_is_runnable_as_one_file():
    script = build_views(model(), ea_build="1716").script()
    assert script.count("\nGO\n") == len(build_views(model()).views)
    assert script.startswith("--")


# ------------------------------------------------------------ determinism


def test_two_builds_of_the_same_model_are_identical():
    assert build_views(model([declared(), adhoc()])).script() == \
        build_views(model([declared(), adhoc()])).script()


def test_an_identifier_closing_its_own_bracket_is_escaped():
    sql = build_views(model([declared(name="we]ird", key="WBA::X")])).views["we]ird"]
    assert "[we]]ird]" in sql


def test_a_value_closing_its_own_quote_is_escaped():
    sql = placement_predicate(declared(key="WBA::it's"))
    assert "'WBA::it''s'" in sql
