#!/usr/bin/env python3
"""Tests for the SQL view emitter.

    python -m pytest _shared/tools/test_sql_views.py -q

Nothing here touches a database; this checks the shape of the SQL.
`test_sql_views_sqlserver.py` compiles it. Where `frame.package_rows` or
`report_model.coerce_value` decides a value, the expectation is taken from it.

The fixture declares INTEGER and REAL columns as well as TEXT, and
`edge_packages()` carries the malformed package shapes `package_rows` handles.
Assertions are scoped to one clause - `column_expr`, `pkg_anchor`,
`pkg_recursive` - so each certifies that clause and not the whole script.
"""
from __future__ import annotations

import pathlib
import re

import pytest

from ddl import FRAME_DDL, physical
from frame import package_rows
from report_model import (BOOLEAN_FALSE, BOOLEAN_TRUE, SQL_TYPES, UNCOERCIBLE,
                          Column, ReportModel, Table, coerce_value)
from sql_views import (SQLSERVER_TYPES, SUPPORTED_DIALECTS, DialectError,
                       build_views, drop_script, placement_predicate)

#: Not all TEXT: `report_model.SQL_TYPES` maps a declared boolean or integer
#: to INTEGER and a decimal or double to REAL, so the typed path is exercised.
TYPED_COLS = (("criticality", "TEXT"),
              ("audit_logging_enabled", "INTEGER"),
              ("uptime", "REAL"))


def declared(name="business_application", key="WBA::WBABusinessApplication",
             cols=TYPED_COLS, overflow=()):
    return Table(name=name, entity_key=key, stereotype="WBABusinessApplication",
                 profile="WBA", declared=True, overflow_tags=list(overflow),
                 columns=[Column(name=c, source_tag=c, sql_type=t) for c, t in cols])


def edge_packages():
    """Packages with each malformation `frame.package_rows` handles.

    A dangling parent, a self-parent, a NULL name and a child under it. Tests
    compare the view against what `package_rows` returns for these.
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
    # stereotype is derived from the key, as the census keeps them in step.
    return Table(name=name, entity_key=key, stereotype=key.rpartition("|")[0],
                 profile="", declared=False)


def model(tables=None):
    return ReportModel(technology_id="WBA", namespace="WBA",
                       tables=list(tables) if tables else [declared()])


def empty_model():
    """A technology with no declared table.

    `model([])` substitutes a declared table, so the empty-model branches need
    this.
    """
    return ReportModel(technology_id="WBA", namespace="WBA", tables=[])


# ------------------------------------------------------------- the dialect


def test_only_a_tested_dialect_is_emitted():
    """An unsupported dialect is refused rather than emitted."""
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
    """An element with no stereotype block is placed by `t_object.Stereotype`
    and metaclass, as the census places it.
    """
    sql = placement_predicate(adhoc(key="SystemSoftware|Component"))
    assert "NOT EXISTS" in sql
    assert "o.Stereotype = N'SystemSoftware'" in sql


def test_reading_only_the_fqname_form_is_what_emptied_fourteen_tables():
    """An ad-hoc predicate reads the block's name as well as its FQName."""
    sql = placement_predicate(adhoc())
    assert "fqname" in sql and "stereo_name" in sql


# ------------------------------------------------------------- the parsing


def test_blocks_are_split_rather_than_substring_matched():
    """Whether an application has an FQName is a property of a block, so the
    Description is split into blocks rather than substring-matched.
    """
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
    """A diagram exists whether or not anything on it is placed."""
    assert physical("element") not in build_views(model()).views[physical("diagram")]


def test_overflow_is_scoped_by_placement_not_by_entity_table():
    """`entity_table` names only the first table a multi-stereotype element is
    placed in, so overflow is scoped by each table's placement predicate.
    """
    sql = build_views(model([declared(overflow=("pciScopeJustification",))])
                      ).views[physical("overflow_tag")]
    assert "entity_table" not in sql
    assert "sb.fqname" in sql


def test_overflow_does_NOT_filter_empty_values():
    """`pivot` writes an overflow row whether or not the value is populated, so
    the view keeps empty values. `_tag_value` drops them.
    """
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
    """EA's physical schema can change between builds, so a known build is
    stamped in the header.
    """
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


def test_the_numeric_types_are_written_only_in_the_type_map():
    """No string in the emitter names a numeric SQL Server type except the
    values of `SQLSERVER_TYPES`, so every view reads its widths from one place.
    `test_sql_views_sqlserver.py` checks the compiled column types."""
    import ast

    import sql_views

    tree = ast.parse(pathlib.Path(sql_views.__file__).read_text(encoding="utf-8"))
    docstrings = {id(n.body[0].value) for n in ast.walk(tree)
                  if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef))
                  and n.body and isinstance(n.body[0], ast.Expr)
                  and isinstance(n.body[0].value, ast.Constant)}
    type_map = next(n.value for n in tree.body if isinstance(n, ast.Assign)
                    and any(getattr(t, "id", "") == "SQLSERVER_TYPES"
                            for t in n.targets))
    allowed = {id(v) for v in type_map.values}
    numeric = re.compile(r"\b(bigint|int|smallint|tinyint|float|real|decimal|"
                         r"numeric|money)\b")
    found = [n.value for n in ast.walk(tree)
             if isinstance(n, ast.Constant) and isinstance(n.value, str)
             and id(n) not in docstrings and id(n) not in allowed
             and numeric.search(n.value)]
    assert not found, ("numeric types written outside SQLSERVER_TYPES: %r"
                       % found)


def test_package_depth_is_zero_based_like_frame_package_rows():
    """A root is depth 0, as `frame.package_rows` computes it."""
    sql = build_views(model()).views[physical("pkg")]
    # Read the seeded value, whatever type it is cast to.
    seed = re.search(r"CAST\(\s*(-?\d+)\s+AS\s+\w+\s*\)\s+AS depth|(-?\d+)\s+AS depth",
                     pkg_anchor(sql))
    assert seed, "the anchor must seed depth with a literal"
    assert int(seed.group(1) or seed.group(2)) == 0, "a root is depth 0, not 1"
    assert "depth + 1" in pkg_recursive(sql), "and each level adds one"


def test_an_orphan_or_self_parented_package_is_a_ROOT_not_dropped():
    """`frame.package_rows` keeps a dangling or self-parented package as a root.

    So does the view: the anchor admits it, with a NULL parent and a path that
    is not NULL.
    """
    rows = {r["package_id"]: r for r in package_rows(edge_packages())}
    assert set(rows) == {1, 2, 3, 4, 5}, "no package is dropped"
    assert rows[2]["depth"] == 0 and rows[3]["depth"] == 0, "both are roots"

    sql = build_views(model()).views[physical("pkg")]
    anchor = pkg_anchor(sql)
    assert "p.Parent_ID = p.Package_ID" in anchor
    assert "NOT EXISTS" in anchor
    want = "CAST(NULL AS %s) AS Parent_ID" % SQLSERVER_TYPES[
        dict(FRAME_DDL["pkg"])["parent_id"]]
    assert want in anchor, (
        "a kept root must not carry the parent that made it one")
    assert "COALESCE(p.Name, '')" in anchor, "nor a NULL name into its path"


def test_coverage_is_scoped_by_placement_not_by_entity_table():
    """`entity_table` names only the first table a multi-stereotype element is
    placed in, so coverage is scoped by placement.
    """
    sql = build_views(model()).views[physical("tag_coverage")]
    assert "entity_table" not in sql
    assert "sb.fqname" in sql


def test_coverage_counts_distinct_elements_not_joined_rows():
    """`t_objectproperties` has no unique index on (Object_ID, Property), so a
    repeated tag would inflate `total` past the model's row count."""
    assert "COUNT(DISTINCT o.ea_guid)" in build_views(model()).views[physical("tag_coverage")]


def test_a_model_with_no_vocabulary_tables_emits_SQL_that_compiles():
    """An empty model's key map uses typed NULL columns, not a `CASE` whose only
    result is NULL.
    """
    sql = build_views(ReportModel(technology_id="WBA")).views[physical("element")]
    assert "WHEN 1 = 0 THEN NULL" not in sql
    assert "CAST(NULL AS nvarchar(40))" in sql


def test_literals_are_unicode_because_every_column_they_meet_is_nvarchar():
    """Every column a literal is compared against is `nvarchar`, so literals
    carry the `N` prefix.
    """
    assert "N'" in placement_predicate(declared())


def test_the_block_parser_strips_a_separator_already_in_the_data():
    """A CHAR(1) already in the text is removed before CHAR(1) is used as the
    block separator.
    """
    sql = build_views(model()).views["_stereo_block"]
    assert sql.count("REPLACE(") == 2


def test_the_name_field_is_not_matched_inside_FQName():
    """`;Name=` does not occur inside `;FQName=`, so the name is read after it."""
    assert "';Name='" in build_views(model()).views["_stereo_block"]


# --------------------------- values, against `package_rows` and `coerce_value`


def test_a_dangling_or_self_parent_is_NULL_not_a_pointer_out_of_the_view():
    """A dangling or self-parented package has a NULL `parent_id`, as in
    `package_rows`, not a pointer to a row the view does not contain.
    """
    rows = {r["package_id"]: r for r in package_rows(edge_packages())}
    assert rows[2]["parent_id"] is None, "dangling Parent_ID 99 -> NULL"
    assert rows[3]["parent_id"] is None, "self-parent -> NULL"

    anchor = pkg_anchor(build_views(model()).views[physical("pkg")])
    assert "CAST(NULL AS %s) AS Parent_ID" % SQLSERVER_TYPES[
        dict(FRAME_DDL["pkg"])["parent_id"]] in anchor
    assert "p.Parent_ID," not in anchor, \
        "NULLIF(Parent_ID, 0) in the outer SELECT strips zero and nothing else"


def test_a_NULL_package_name_does_not_empty_the_path_of_its_whole_subtree():
    """A NULL package name contributes `''` to `path`, as in `package_rows`, so it
    does not empty the path of its subtree.
    """
    rows = {r["package_id"]: r for r in package_rows(edge_packages())}
    assert rows[4]["path"] == "Model/"
    assert rows[5]["path"] == "Model//UnderNullName"

    sql = build_views(model()).views[physical("pkg")]
    assert "CAST(COALESCE(p.Name, '') AS nvarchar(max)) AS path" in pkg_anchor(sql)
    assert "t.path + '/' + COALESCE(c.Name, '')" in pkg_recursive(sql)


def test_an_INTEGER_column_maps_eas_boolean_strings_the_way_the_pivot_does():
    """On INTEGER, EA's boolean strings map to 1 and 0, compared lowercased, as
    `coerce_value` maps them.
    """
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
    """An empty value is NULL on a typed column and `''` on TEXT, as
    `coerce_value` returns.
    """
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
    """A value `coerce_value` cannot convert is NULL in the view, via `TRY_CAST`."""
    assert coerce_value("maybe", "INTEGER") is UNCOERCIBLE
    assert coerce_value("maybe", "REAL") is UNCOERCIBLE

    sql = build_views(model()).views["business_application"]
    assert "TRY_CAST" in column_expr(sql, "audit_logging_enabled")
    assert "TRY_CAST" in column_expr(sql, "uptime")


def test_every_sql_type_the_model_can_declare_is_coerced_in_the_view():
    """Every type `report_model.SQL_TYPES` can produce is handled: TEXT trimmed,
    the others cast to their `SQLSERVER_TYPES` type.
    """
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
    """INTEGER and REAL are 64-bit here, as they are in Parquet.

    Pinned to the literal types rather than to each other, so narrowing both
    maps together still fails.
    """
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
    """`pivot()` parameterizes the separator and `build_views` does not thread it
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
    """Both `_tag_value` arms trim, as `pivot` strips every value."""
    sql = build_views(model()).views[physical("tag_value")]
    assert "LTRIM(RTRIM(p.Value)) AS value" in sql
    assert "p.Value AS value" not in sql


def test_an_entity_column_is_trimmed_where_the_pivot_strips_it():
    """Every entity column trims before coercing, as `pivot` does."""
    sql = build_views(model()).views["business_application"]
    for column in ("criticality", "audit_logging_enabled", "uptime"):
        assert "LTRIM(RTRIM(" in column_expr(sql, column)


def test_the_entity_pivot_takes_the_HIGHEST_PropertyID_so_TOP_1_is_decided():
    """Every `TOP 1` carries `ORDER BY p.PropertyID DESC`, so which of two
    duplicate tag rows is read is decided.
    """
    sql = build_views(model()).views["business_application"]
    assert sql.count("ORDER BY p.PropertyID DESC") == 3, "one per column"
    assert sql.count("SELECT TOP 1") == sql.count("ORDER BY p.PropertyID DESC"), \
        "a TOP 1 without an ORDER BY returns whichever row the backend likes"


def test_the_duplicate_tag_defect_is_REPRODUCED_rather_than_quietly_fixed():
    """DESC, not ASC: the later duplicate wins, as in `pivot`, even when it is
    the empty one.

    That is a `pivot` defect (`APT-2026-0239`), reproduced so the paths agree.
    """
    sql = build_views(model()).views["business_application"]
    assert "ORDER BY p.PropertyID ASC" not in sql
    assert "ORDER BY p.PropertyID DESC" in sql


def test_a_newline_in_a_model_string_cannot_escape_a_header_comment():
    """A line break in a model value cannot end a header comment and leave DDL
    behind.
    """
    m = ReportModel(technology_id="WBA",
                    technology_name="WBA\nDROP TABLE t_object;",
                    namespace="a\r\nb", tables=[declared()])
    header = build_views(m, ea_build="1716\nDROP TABLE t_package;").header
    for line in header.splitlines():
        assert line == "" or line.startswith("--"), f"executable line: {line!r}"
    assert "DROP TABLE t_object;" in header, "it is still reported, on one line"
