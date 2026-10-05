#!/usr/bin/env python3
"""Tests for the SQL view emitter.

    python -m pytest _shared/tools/test_sql_views.py -q

Nothing here touches a database. The generator is pure, so what is testable
hermetically is the SHAPE of the SQL; whether it returns the right rows AND the
right VALUES is settled by running the views against a real SQL Server
repository and comparing every table, cell by cell, against the reporting
database built from the same census.

Several of these encode defects that comparison found, because every one of them
produced a view that ran perfectly well and returned the wrong rows - or the
right rows carrying the wrong values, which is the half a row count cannot see.

A FIXTURE WITH NO EDGE CASE IN IT CANNOT FAIL ON ONE
---------------------------------------------------
Four defects reached a second review behind a well-formed fixture: it held no
dangling `Parent_ID`, no self-parented package, no NULL package name, and its
columns were all TEXT, so the typed path was never compared at all. The INTEGER
and REAL columns below and `edge_packages()` are the fixture's deliberately
malformed half, and they are the reason those four can now fail here.

Assertions over generated SQL are scoped to the CLAUSE that was wrong -
`column_expr`, `pkg_anchor`, `pkg_recursive` - because a match anywhere in a
600-line script certifies the clause it names and nothing else. Twice now a
defect has sat in one clause while the one beside it was already right.
"""
from __future__ import annotations

import pytest

from ddl import FRAME_DDL, physical
from frame import package_rows
from report_model import (BOOLEAN_FALSE, BOOLEAN_TRUE, SQL_TYPES, UNCOERCIBLE,
                          Column, ReportModel, Table, coerce_value)
from sql_views import (SQLSERVER_TYPES, SUPPORTED_DIALECTS, DialectError,
                       build_views, drop_script, placement_predicate)

#: The shared fixture's own examples, and NOT all TEXT. `report_model.SQL_TYPES`
#: maps a declared boolean to INTEGER and a decimal or double to REAL, so a
#: technology declaring either produces a column `coerce_value` does not pass
#: through - which is the whole of CR-0230-01 and was untestable while every
#: column here was TEXT.
TYPED_COLS = (("criticality", "TEXT"),
              ("audit_logging_enabled", "INTEGER"),
              ("uptime", "REAL"))


def declared(name="business_application", key="WBA::WBABusinessApplication",
             cols=TYPED_COLS, overflow=()):
    return Table(name=name, entity_key=key, stereotype="WBABusinessApplication",
                 profile="WBA", declared=True, overflow_tags=list(overflow),
                 columns=[Column(name=c, source_tag=c, sql_type=t) for c, t in cols])


def edge_packages():
    """A package list carrying every malformation `frame.package_rows` guards.

    None of these is in the live fixture, because a model EA built does not
    contain them - which is exactly why the view's handling of them went two
    rounds of review unexamined. `package_rows` is the authority each test below
    compares against, so the expected values are derived rather than asserted
    from memory.
    """
    return [
        {"Package_ID": 1, "Parent_ID": 0, "Name": "Model"},
        {"Package_ID": 2, "Parent_ID": 99, "Name": "Orphan"},
        {"Package_ID": 3, "Parent_ID": 3, "Name": "SelfParent"},
        {"Package_ID": 4, "Parent_ID": 1, "Name": None},
        {"Package_ID": 5, "Parent_ID": 4, "Name": "UnderNullName"},
    ]


def column_expr(sql: str, column: str) -> str:
    """The value expression the entity view emits for ONE column, by itself."""
    subquery = sql.split(f") AS [{column}]")[0].rpartition("(SELECT TOP 1 ")[2]
    return subquery.split("FROM t_objectproperties")[0]


def pkg_anchor(sql: str) -> str:
    return sql.split("UNION ALL")[0]


def pkg_recursive(sql: str) -> str:
    return sql.split("UNION ALL")[1]


def adhoc(name="business_actor", key="BusinessActor|Actor"):
    # stereotype is derived from the key, because the census keeps them in step
    # and the emitter now reads  rather than re-parsing the key.
    return Table(name=name, entity_key=key, stereotype=key.rpartition("|")[0],
                 profile="", declared=False)


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
    assert "sb.fqname = N'WBA::WBABusinessApplication'" in sql
    assert "o.Object_Type" not in sql


def test_an_ad_hoc_table_matches_on_NAME_AND_METACLASS():
    """`ea_census.entity_key` keys an ad-hoc application `name|metaclass`
    because a bare name is ambiguous across languages."""
    sql = placement_predicate(adhoc(key="BusinessActor|Actor"))
    assert "sb.stereo_name = N'BusinessActor'" in sql
    assert "o.Object_Type = N'Actor'" in sql
    assert "sb.fqname = N''" in sql


def test_an_ad_hoc_table_also_falls_back_to_the_bare_stereotype_column():
    """MEASURED. An element with NO xref row at all is still stereotyped - the
    census says so and two elements on the reference model are exactly that.
    Without this clause the key map came out 2 short and both their tables were
    empty, while every view still ran without error."""
    sql = placement_predicate(adhoc(key="SystemSoftware|Component"))
    assert "NOT EXISTS" in sql
    assert "o.Stereotype = N'SystemSoftware'" in sql


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
    assert "NOT IN (N'regulatory_scope')" in sql


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
    assert "N'WBA::it''s'" in sql


def test_the_shape_is_chosen_from_profile_not_by_sniffing_the_key():
    """A bare `t_object.Stereotype` holding a QUALIFIED name yields a key with
    both `|` and `::`. Sniffing the key would read that as profile-bound,
    compare it against `fqname`, match nothing, and leave the table silently
    empty. `profile` says what the census already decided."""
    t = Table(name="odd", entity_key="WBA::Name|Class", stereotype="Name",
              profile="", declared=False)
    sql = placement_predicate(t)
    assert "sb.stereo_name = N'Name'" in sql
    assert "o.Object_Type = N'Class'" in sql
    assert "sb.fqname = N'WBA::Name|Class'" not in sql


def test_a_stereotype_name_containing_a_pipe_still_splits_correctly():
    """The metaclass is taken from the LAST `|`, so a name carrying one does not
    mis-partition."""
    t = Table(name="odd", entity_key="we|ird|Component", stereotype="we|ird",
              profile="", declared=False)
    assert "o.Object_Type = N'Component'" in placement_predicate(t)


def test_package_depth_is_zero_based_like_frame_package_rows():
    """`frame.package_rows` computes `len(names) - 1`, so a root is 0. The view
    anchored at 1 and was off by one on EVERY row of a shipped, customer-visible
    column - and the live acceptance could not see it, because it compared row
    counts only."""
    sql = build_views(model()).views[physical("pkg")]
    assert "0 AS depth" in sql
    assert "1 AS depth" not in sql


def test_an_orphan_or_self_parented_package_is_a_ROOT_not_dropped():
    """`frame.package_rows` keeps both deliberately: losing a package loses every
    element under it from the grouping. Dropping it here would also orphan those
    elements from `_keymap.package_id`, which `semantic_model` calls the only
    path to the package tree.

    A ROOT IN EVERY COLUMN, not only in the `WHERE`. This test asserted two
    strings in the anchor's predicate and passed for a whole review round while
    the row it kept carried a `parent_id` pointing outside the view and, for a
    NULL-named package, a NULL `path`. Keeping the row and keeping its columns
    right are two separate things, so both are asserted here, against what
    `package_rows` actually returns for the same packages."""
    rows = {r["package_id"]: r for r in package_rows(edge_packages())}
    assert set(rows) == {1, 2, 3, 4, 5}, "no package is dropped"
    assert rows[2]["depth"] == 0 and rows[3]["depth"] == 0, "both are roots"

    sql = build_views(model()).views[physical("pkg")]
    anchor = pkg_anchor(sql)
    assert "p.Parent_ID = p.Package_ID" in anchor
    assert "NOT EXISTS" in anchor
    assert "CAST(NULL AS int) AS Parent_ID" in anchor, \
        "a kept root must not carry the parent that made it one"
    assert "COALESCE(p.Name, '')" in anchor, "nor a NULL name into its path"


def test_coverage_is_scoped_by_placement_not_by_entity_table():
    """The same defect `_overflow_tag` documents fixing. `entity_table` names
    only the FIRST table a multi-stereotype element landed in, so coverage
    computed a total of 46 against the model's own row_count of 47 - the
    measured multi-stereotype case, reappearing in a different view."""
    sql = build_views(model()).views[physical("tag_coverage")]
    assert "entity_table" not in sql
    assert "sb.fqname" in sql


def test_coverage_counts_distinct_elements_not_joined_rows():
    """`t_objectproperties` has no unique index on (Object_ID, Property), so a
    repeated tag would inflate `total` past the model's row count."""
    assert "COUNT(DISTINCT o.ea_guid)" in build_views(model()).views[physical("tag_coverage")]


def test_a_model_with_no_vocabulary_tables_emits_SQL_that_compiles():
    """SQL Server rejects a CASE whose only result is the NULL constant
    (Msg 8133). The sibling empty-case views use typed CAST(NULL) columns."""
    sql = build_views(ReportModel(technology_id="WBA")).views[physical("element")]
    assert "WHEN 1 = 0 THEN NULL" not in sql
    assert "CAST(NULL AS nvarchar(40))" in sql


def test_literals_are_unicode_because_every_column_they_meet_is_nvarchar():
    """Without the N the literal is parsed under the database's default
    collation codepage, so a name outside it becomes `?` and the predicate
    matches nothing - an empty table caused by a customer's language."""
    assert "N'" in placement_predicate(declared())


def test_the_block_parser_strips_a_separator_already_in_the_data():
    """If a CHAR(1) ever appeared mid-block the fragment after it would fail the
    LIKE and be dropped, and the one before it would lose its FQName - silently
    demoting a profile-bound application to ad-hoc."""
    sql = build_views(model()).views["_stereo_block"]
    assert sql.count("REPLACE(") == 2


def test_the_name_field_is_not_matched_inside_FQName():
    """`Name=` is a substring of `FQName=`. Searching `;Name=` disambiguates
    completely, where the Python parser is order-independent and this was not."""
    assert "';Name='" in build_views(model()).views["_stereo_block"]


# -------------------------------------- the VALUES, which row counts cannot see
#
# Measured by running both view sets over a scratch SQL Server database holding
# only these edge cases, and comparing every cell against `frame.package_rows`
# and `pivot`. The "was" figures in each docstring are what the views returned
# before the fix beside them.


def test_a_dangling_or_self_parent_is_NULL_not_a_pointer_out_of_the_view():
    """MEASURED. `parent_id` 99 where the database holds NULL, for a package
    whose `Parent_ID` names no row; and 4 for a package that is its own parent,
    where the database holds NULL. The anchor was widened to KEEP both packages
    and the column they carry was not brought into line, so a shipped INTEGER
    column pointed at a row this view does not contain - or at itself, which is
    worse than cosmetic for anything that walks the chain."""
    rows = {r["package_id"]: r for r in package_rows(edge_packages())}
    assert rows[2]["parent_id"] is None, "dangling Parent_ID 99 -> NULL"
    assert rows[3]["parent_id"] is None, "self-parent -> NULL"

    anchor = pkg_anchor(build_views(model()).views[physical("pkg")])
    assert "CAST(NULL AS int) AS Parent_ID" in anchor
    assert "p.Parent_ID," not in anchor, \
        "NULLIF(Parent_ID, 0) in the outer SELECT strips zero and nothing else"


def test_a_NULL_package_name_does_not_empty_the_path_of_its_whole_subtree():
    """MEASURED. `path` came back NULL for the NULL-named package AND for its
    child, against `'Model/'` and `'Model//UnderNullName'` in the database:
    `NULL + '/' + 'x'` is NULL in SQL Server and the recursion carries that the
    whole way down, so one unnamed package empties a column for every descendant
    it has. The outer SELECT already coalesced the projected `name`; `path` was
    missed because it is computed rather than projected."""
    rows = {r["package_id"]: r for r in package_rows(edge_packages())}
    assert rows[4]["path"] == "Model/"
    assert rows[5]["path"] == "Model//UnderNullName"

    sql = build_views(model()).views[physical("pkg")]
    assert "CAST(COALESCE(p.Name, '') AS nvarchar(max)) AS path" in pkg_anchor(sql)
    assert "t.path + '/' + COALESCE(c.Name, '')" in pkg_recursive(sql)


def test_an_INTEGER_column_maps_eas_boolean_strings_the_way_the_pivot_does():
    """MEASURED. `'true'` on an INTEGER column was published as the string
    `'true'` where the database and Parquet hold `1`, so the measure
    `WHERE audit_logging_enabled = 1` matched nothing - which is the consequence
    `report_model.coerce_value` states in advance.

    EA has no boolean tagged-value type, so a declared boolean arrives as
    whatever the editor or the profile default wrote. `coerce_value` applies the
    mapping on the SQL TYPE, not on the declared type, so the view has to as
    well: INTEGER is all either path can see by then."""
    assert coerce_value("true", "INTEGER") == 1
    assert coerce_value("no", "INTEGER") == 0

    expr = column_expr(build_views(model()).views["business_application"],
                       "audit_logging_enabled")
    assert "THEN 1" in expr and "THEN 0" in expr
    for text in BOOLEAN_TRUE | BOOLEAN_FALSE:
        assert f"N'{text}'" in expr, f"EA writes {text!r} for a declared boolean"
    assert "LOWER(" in expr, \
        "the Python lowercases; a case-sensitive collation would not"


def test_an_empty_value_is_NULL_on_a_typed_column_and_EMPTY_on_TEXT():
    """MEASURED. An empty tag on an INTEGER column was published as `''` where
    the database holds NULL. Empty means nobody filled it in, which is a
    coverage fact - a `0` there invents data and makes `tag_coverage` disagree
    with the column it describes. On TEXT it stays `''`, which is what every
    build before this one wrote, and changing that would break a customer query
    testing `= ''`."""
    assert coerce_value("", "INTEGER") is None
    assert coerce_value("", "REAL") is None
    assert coerce_value("", "TEXT") == ""

    sql = build_views(model()).views["business_application"]
    for column in ("audit_logging_enabled", "uptime"):
        assert "= N'' THEN NULL" in column_expr(sql, column)
    assert "THEN NULL" not in column_expr(sql, "criticality")
    assert column_expr(sql, "criticality").strip() \
        == "LTRIM(RTRIM(COALESCE(p.Value, '')))"


def test_an_uncoercible_value_is_NULL_rather_than_published_silently():
    """MEASURED. `'maybe'` on a REAL column was published as the string
    `'maybe'`. The Python leaves the column unset and records a data-quality
    finding; the view has nowhere to put a finding, so NULL is the whole of what
    it can agree on - and publishing the text instead made the column `nvarchar`
    where the database declares it `float`, so `CAST(uptime AS float)` over the
    view failed outright with Msg 8114. That is the pyarrow refusal of
    APT-2026-0225 arriving by a second route.

    `TRY_CAST` is the agreement: NULL exactly where `int()` and `float()` raise.
    """
    assert coerce_value("maybe", "INTEGER") is UNCOERCIBLE
    assert coerce_value("maybe", "REAL") is UNCOERCIBLE

    sql = build_views(model()).views["business_application"]
    assert "TRY_CAST" in column_expr(sql, "audit_logging_enabled")
    assert "TRY_CAST" in column_expr(sql, "uptime")


def test_every_sql_type_the_model_can_declare_is_coerced_in_the_view():
    """The defect was not one type handled wrongly, it was the type IGNORED, so
    the guard is over every type `report_model.SQL_TYPES` can produce rather
    than over the two that happened to be measured."""
    types = sorted(set(SQL_TYPES.values()))
    assert types == ["INTEGER", "REAL", "TEXT"]
    cols = tuple((f"c_{t.lower()}", t) for t in types)
    sql = build_views(model([declared(cols=cols)])).views["business_application"]
    for name, sql_type in cols:
        expr = column_expr(sql, name)
        assert "LTRIM(RTRIM(" in expr, "the pivot strips before it coerces"
        assert ("TRY_CAST" in expr) == (sql_type != "TEXT"), \
            f"{sql_type} is {'typed' if sql_type != 'TEXT' else 'text'}"
        if sql_type != "TEXT":
            assert f"AS {SQLSERVER_TYPES[sql_type]})" in expr, \
                f"{sql_type} must cast to the DECLARED target type"


def test_an_integer_column_is_64_bit_like_every_other_path():
    """The type is part of the value, so the WIDTH is too.

    SQLite's INTEGER is 64-bit and `parquet_out.PARQUET_TYPES` maps INTEGER to
    `int64`, so casting to SQL Server's 32-bit `int` publishes a different value
    at the boundary. MEASURED against the live instance: a tagged value of
    3000000000 is 3000000000 in the reporting database and in Parquet, and
    `TRY_CAST(N'3000000000' AS int)` is NULL. 2147483647 agreed; 2147483648 did
    not - a boundary no fixture contains.

    Derived from `PARQUET_TYPES` rather than asserting the literal `bigint`,
    because the defect was a hand-written type expectation sitting beside value
    oracles that were all derived. A hand-written expectation agrees with
    whatever the code does."""
    from parquet_out import PARQUET_TYPES

    assert PARQUET_TYPES["INTEGER"] == "int64", "the other path is 64-bit"
    assert PARQUET_TYPES["REAL"] == "double"
    # 64-bit there must mean 64-bit here. `int` is 32-bit; `bigint` is not.
    assert SQLSERVER_TYPES["INTEGER"] == "bigint"
    assert SQLSERVER_TYPES["REAL"] == "float", "SQL Server float is 64-bit"

    sql = build_views(model([declared(cols=(("n", "INTEGER"),))])).views[
        "business_application"]
    expr = column_expr(sql, "n")
    assert "AS bigint)" in expr
    assert "AS int)" not in expr, "a 32-bit cast silently nulls 3000000000"


def test_the_multi_value_separator_is_the_only_one_supported():
    """`pivot()` parameterises the separator and `build_views` does not thread it
    through, so the generated `STRING_SPLIT` hardcodes a comma. That is a real
    limit rather than a bug - but it is only safe while the default is the only
    value in use, so assert exactly that and fail loudly if the default moves."""
    import inspect

    from pivot import pivot

    default = inspect.signature(pivot).parameters["separator"].default
    assert default == ",", (
        "pivot's separator default changed; the views hardcode ',' in "
        "STRING_SPLIT and would now disagree with the Python path")


def test_a_single_valued_tag_is_trimmed_where_the_pivot_strips_it():
    """MEASURED. `'Business-Critical '` through the single-valued arm against
    `'Business-Critical'` in the database. `pivot` strips every value
    unconditionally before anything else sees it, and in Power BI those two are
    two different members of the same column - the same failure as blank versus
    empty string. The split arm already trimmed each part, and the identical
    expression was already in the `WHERE` one line above."""
    sql = build_views(model()).views[physical("tag_value")]
    assert "LTRIM(RTRIM(p.Value)) AS value" in sql
    assert "p.Value AS value" not in sql


def test_an_entity_column_is_trimmed_where_the_pivot_strips_it():
    """MEASURED. `' 7 '` on a REAL column: the database holds 7.0 because the
    pivot strips before coercing, and the view published `' 7 '` as text. On a
    TEXT column the same asymmetry splits one member into two."""
    sql = build_views(model()).views["business_application"]
    for column in ("criticality", "audit_logging_enabled", "uptime"):
        assert "LTRIM(RTRIM(" in column_expr(sql, column)


def test_the_entity_pivot_takes_the_HIGHEST_PropertyID_so_TOP_1_is_decided():
    """`t_objectproperties` has no unique index on `(Object_ID, Property)` and
    the reference model holds duplicates: six tags on one element, each twice,
    once populated and once NULL, the NULL having the higher `PropertyID`.

    Without an `ORDER BY`, `TOP 1` is nondeterministic - it happened to return
    the populated row, so the view disagreed with the database on one element
    and no row count could see it. The ordering was added and nothing guarded
    it: a docstring saying LOAD-BEARING is not a guard, and the next person to
    tidy this subquery drops it with every test still passing."""
    sql = build_views(model()).views["business_application"]
    assert sql.count("ORDER BY p.PropertyID DESC") == 3, "one per column"
    assert sql.count("SELECT TOP 1") == sql.count("ORDER BY p.PropertyID DESC"), \
        "a TOP 1 without an ORDER BY returns whichever row the backend likes"


def test_the_duplicate_tag_defect_is_REPRODUCED_rather_than_quietly_fixed():
    """DESC, not ASC, and that is deliberate. The pivot assigns column values in
    extract order and lets later rows overwrite, so an empty duplicate beats the
    populated value that came before it. Taking the HIGHEST `PropertyID` keeps
    the two paths identical, which is the contract; preferring the populated row
    here would make this view right and the shipped database wrong about the
    same element, and hide the defect instead of settling it.

    The defect is `pivot.py`'s and is owed its own item - as is `extract.py`
    reading `t_objectproperties` with no `ORDER BY`, which is why the docstring
    claims agreement with an OBSERVED extract order rather than a guaranteed
    one."""
    sql = build_views(model()).views["business_application"]
    assert "ORDER BY p.PropertyID ASC" not in sql
    assert "ORDER BY p.PropertyID DESC" in sql


def test_a_newline_in_a_model_string_cannot_escape_a_header_comment():
    """A `--` comment runs to end of line, so a CR or LF in a model-sourced
    string closes it and leaves the rest of that value as executable DDL in a
    script the customer runs with schema rights. Comment text was the one
    interpolation in the module not routed through `_lit` or `_q`."""
    m = ReportModel(technology_id="WBA",
                    technology_name="WBA\nDROP TABLE t_object;",
                    namespace="a\r\nb", tables=[declared()])
    header = build_views(m, ea_build="1716\nDROP TABLE t_package;").header
    for line in header.splitlines():
        assert line == "" or line.startswith("--"), f"executable line: {line!r}"
    assert "DROP TABLE t_object;" in header, "it is still reported, on one line"
