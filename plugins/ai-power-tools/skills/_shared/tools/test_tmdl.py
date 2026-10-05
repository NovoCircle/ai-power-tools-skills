#!/usr/bin/env python3
"""Tests for TMDL rendering, including the cross-path identity guarantee.

    python -m pytest _shared/tools/test_tmdl.py -q

Nothing here touches a repository, a COM object, Power BI or the filesystem.

THE IDENTITY TEST IS THE POINT OF THIS FILE. Three paths emit a Power BI model -
`APT-2026-0211` from the reporting database, `APT-2026-0212` direct from EA,
`APT-2026-0230` live against the repository - and the product's claim is that a
customer gets the same model whichever they pick. `test_only_the_partition_*`
is what makes that claim checkable instead of aspirational.
"""
from __future__ import annotations

import json
import re

from ddl import physical
from report_model import Column, ReportModel, Table
from semantic_model import DEFAULT_MEASURE_HOST, HUB, build_semantic_model
from tmdl import (NEWLINE, ParquetSource, SqlSource, ident, lineage_tag,
                  m_literal,
                  render_culture, render_definition, render_model,
                  render_relationships, render_table)


def report_model(n_tables=2):
    tables = [
        Table(name=f"entity_{i}", entity_key=f"k{i}", stereotype=f"S{i}",
              description=f"Entity {i} holds things.",
              columns=[Column(name="criticality", source_tag="criticality",
                              sql_type="TEXT", description="How critical.")])
        for i in range(n_tables)
    ]
    return ReportModel(technology_id="WBA", tables=tables)


def semantic(n_tables=2):
    return build_semantic_model(report_model(n_tables))


PARQUET = ParquetSource(directory=r"C:\out\parquet")
SQL = SqlSource(server="SERVER\\INSTANCE", database="EARepository")


def strip_partition(text: str) -> str:
    """Drop the partition block, which is the one part allowed to differ."""
    out, skipping = [], False
    for line in text.split(NEWLINE):
        if line.startswith("\tpartition "):
            skipping = True
            continue
        if skipping:
            if line.startswith("\tannotation "):
                skipping = False
            else:
                continue
        out.append(line)
    return NEWLINE.join(out)


# ------------------------------------------------------- the format rules


def test_every_rendered_file_uses_crlf():
    """Read off a real 2.158 project. A generated file that deviates is
    rejected on apply, so this is not a style question."""
    for path, text in render_definition(semantic(), PARQUET).items():
        assert "\r\n" in text, path
        assert not re.search(r"(?<!\r)\n", text), f"{path} has a bare LF"


def test_indentation_is_tabs_and_never_spaces():
    """TMDL is tab-indented. Spaces do not parse."""
    text = render_table(semantic().table("entity_0"), PARQUET)
    for line in text.split(NEWLINE):
        if line and line[0].isspace():
            assert line.startswith("\t"), repr(line)


def test_a_description_precedes_the_object_it_describes():
    """TMDL `///` lines attach to the NEXT declaration. Putting one after the
    declaration describes the wrong thing."""
    lines = render_table(semantic().table("entity_0"), PARQUET).split(NEWLINE)
    i = lines.index("/// Entity 0 holds things.")
    assert lines[i + 1] == "table entity_0"
    j = next(k for k, l in enumerate(lines) if l == "\t/// How critical.")
    assert lines[j + 1] == "\tcolumn criticality"


def test_a_description_is_collapsed_to_one_line():
    """A newline inside a `///` line ends the comment and the rest becomes
    syntax."""
    sm = semantic()
    sm.table("entity_0").description = "two\nlines\there"
    assert "/// two lines here" in render_table(sm.table("entity_0"), PARQUET)


def test_identifiers_are_quoted_only_when_they_have_to_be():
    assert ident("entity_0") == "entity_0"
    assert ident("_keymap") == "_keymap"
    assert ident("Business Application") == "'Business Application'"
    assert ident("it's") == "'it''s'"


# ------------------------------------------------------------ table files


def test_a_hidden_table_says_so_and_a_visible_one_does_not():
    """Asserted as a whole LINE: a hidden COLUMN renders `\\t\\tisHidden`, which
    contains the table form as a substring and would pass a loose check."""
    sm = semantic()
    assert "\tisHidden" in render_table(sm.table(HUB), PARQUET).split(NEWLINE)
    assert "\tisHidden" not in render_table(sm.table("entity_0"), PARQUET).split(NEWLINE)


def test_a_hidden_column_says_so():
    text = render_table(semantic().table("entity_0"), PARQUET)
    guid = text.split("\tcolumn ea_guid")[1].split("\tcolumn")[0]
    assert "\t\tisHidden" in guid


def test_an_int_column_carries_a_format_string():
    sm = semantic()
    pkg = render_table(sm.table(physical("pkg")), PARQUET)
    block = pkg.split("\tcolumn package_id")[1].split("\tcolumn")[0]
    assert "\t\tformatString: 0" in block


def test_measures_render_on_the_host_and_nowhere_else():
    sm = semantic()
    host = render_table(sm.table(DEFAULT_MEASURE_HOST), PARQUET)
    assert "\tmeasure 'Inbound edges' =" in host
    assert "USERELATIONSHIP" in host
    assert "\tmeasure" not in render_table(sm.table(HUB), PARQUET)


def test_a_measure_name_with_a_space_is_quoted():
    host = render_table(semantic().table(DEFAULT_MEASURE_HOST), PARQUET)
    assert "\tmeasure 'Outbound edges (zero-filled)' = COALESCE(" in host


def test_a_table_ends_with_the_result_type_annotation():
    text = render_table(semantic().table("entity_0"), PARQUET)
    assert text.rstrip(NEWLINE).endswith("\tannotation PBI_ResultType = Table")


# ----------------------------------------------------------- lineage tags


def test_a_lineage_tag_is_derived_so_two_runs_match():
    """Minting fresh GUIDs per run is what would break an existing report's
    field bindings."""
    assert lineage_tag("table", "entity_0") == lineage_tag("table", "entity_0")
    assert render_table(semantic().table("entity_0"), PARQUET) == \
        render_table(semantic().table("entity_0"), PARQUET)


def test_different_objects_get_different_tags():
    assert lineage_tag("table", "a") != lineage_tag("table", "b")
    assert lineage_tag("table", "a") != lineage_tag("column", "a")


def test_a_tag_does_not_depend_on_the_partition_source():
    """A customer moving between paths keeps their report. If the tag moved with
    the source, every field binding would break on the switch."""
    sm = semantic()
    parquet = {l for l in render_table(sm.table("entity_0"), PARQUET).split(NEWLINE)
               if "lineageTag" in l}
    sql = {l for l in render_table(sm.table("entity_0"), SQL).split(NEWLINE)
           if "lineageTag" in l}
    assert parquet == sql


# --------------------------------------------------------- relationships


def test_the_inactive_relationship_is_marked_and_the_active_ones_are_not():
    text = render_relationships(semantic())
    assert "\tisActive: false" in text
    assert text.count("\tisActive: false") == 1


def test_a_one_to_one_emits_both_directions_and_the_cardinality():
    text = render_relationships(semantic(n_tables=3))
    assert text.count("\tcrossFilteringBehavior: bothDirections") == 3
    assert text.count("\tfromCardinality: one") == 3


def test_a_many_to_one_emits_neither():
    """`automatic` and `many` are the defaults. Stating them adds noise to a
    file the customer is expected to read."""
    sm = semantic()
    rel = next(r for r in sm.relationships if r.from_table == physical("tag_value"))
    text = render_relationships(sm)
    block = text.split(f"relationship {rel.name}")[1].split("relationship ")[0]
    assert "crossFilteringBehavior" not in block
    assert "fromCardinality" not in block


def test_a_relationship_carries_no_description():
    """MEASURED 2026-10-02, Power BI 2.158.1177.0. A `///` line before
    `relationship` sets a `description` property and `SingleColumnRelationship`
    has none, so THE WHOLE PROJECT fails to open:

        Property 'description' is unknown and is not expected in the situation
        it appears.

    No file is named and no line number is given. Tables, columns and measures
    do take descriptions; relationships do not. The rationale stays on
    `Relationship.why` and simply cannot travel in the TMDL."""
    text = render_relationships(semantic())
    assert "///" not in text
    assert text.startswith("relationship ")
    for block in text.split("relationship ")[1:]:
        assert block.count("fromColumn:") == 1


def test_the_reason_is_still_carried_on_the_model_even_though_it_is_not_emitted():
    sm = semantic()
    assert all(r.why for r in sm.relationships)
    assert "INACTIVE BY DESIGN" in sm.inactive[0].why


def test_endpoints_render_as_table_dot_column():
    text = render_relationships(semantic())
    assert f"\tfromColumn: {DEFAULT_MEASURE_HOST}.target_guid" in text
    assert f"\ttoColumn: {HUB}.ea_guid" in text


# ------------------------------------------------------- model and culture


def test_the_model_suppresses_auto_date_tables():
    """The auto date-table behavior was observed against a DATETIME column.
    Since APT-2026-0226 the schema exposes none - `date` and `datetime` both map
    to TEXT - so this asserts the suppression is EMITTED, not that it was
    re-observed on the current model."""
    assert "annotation __PBI_TimeIntelligenceEnabled = 0" in render_model(semantic())


def test_the_model_refs_every_table_exactly_once():
    sm = semantic(n_tables=3)
    text = render_model(sm)
    for t in sm.tables:
        assert text.count(f"ref table {ident(t.name)}{NEWLINE}") == 1


def test_the_query_order_lists_every_table():
    sm = semantic(n_tables=3)
    order = render_model(sm).split("PBI_QueryOrder = [")[1].split("]")[0]
    assert order.count(",") == len(sm.tables) - 1
    for t in sm.tables:
        assert f'"{t.name}"' in order


def test_the_culture_block_contains_valid_json():
    """An invalid linguisticMetadata payload is rejected with the whole file."""
    text = render_culture("en-US")
    raw = text[text.index("{"):text.rindex("}") + 1]
    assert json.loads(raw.replace("\t", "").replace("\r\n", "\n"))["Language"] == "en-US"


# -------------------------------------------------------------- partitions


def test_the_parquet_partition_imports_and_names_the_source_table():
    """The host table is named `Relationships` in the model but its rows come
    from `_rel_all`. The partition must follow the SOURCE name."""
    sm = semantic()
    text = render_table(sm.table(DEFAULT_MEASURE_HOST), PARQUET)
    assert "\t\tmode: import" in text
    assert r"C:\out\parquet\_rel_all.parquet" in text
    assert "Parquet.Document(File.Contents(" in text


def test_the_sql_partition_is_direct_query_by_default():
    """DirectQuery is the primary mode for APT-2026-0230, decided 2026-10-02."""
    text = render_table(semantic().table("entity_0"), SQL)
    assert "\t\tmode: directQuery" in text
    assert 'Sql.Database("SERVER\\INSTANCE", "EARepository")' in text
    assert 'Item="entity_0"' in text


def test_a_trailing_separator_on_the_directory_is_not_doubled():
    text = render_table(semantic().table("entity_0"),
                        ParquetSource(directory="C:/out/"))
    assert "C:/out/entity_0.parquet" in text


# -------------------------------------------- THE CROSS-PATH IDENTITY TEST


def test_the_same_files_are_emitted_whichever_path_is_chosen():
    assert set(render_definition(semantic(n_tables=4), PARQUET)) == \
        set(render_definition(semantic(n_tables=4), SQL))


def test_only_the_partition_differs_between_paths():
    """The product's claim, made checkable. Everything a customer sees - tables,
    columns, relationships, measures, descriptions, lineage tags - is identical
    across all three paths. Only where the rows come from changes."""
    parquet = render_definition(semantic(n_tables=4), PARQUET)
    sql = render_definition(semantic(n_tables=4), SQL)
    for path in parquet:
        assert strip_partition(parquet[path]) == strip_partition(sql[path]), path


def test_only_table_files_differ_at_all():
    """`database.tmdl`, `model.tmdl`, `relationships.tmdl` and the culture carry
    no source information, so they must be byte-identical without stripping."""
    parquet = render_definition(semantic(n_tables=4), PARQUET)
    sql = render_definition(semantic(n_tables=4), SQL)
    differing = {p for p in parquet if parquet[p] != sql[p]}
    assert differing == {p for p in parquet if p.startswith("tables/")}


def test_the_partition_really_does_differ_so_the_test_above_can_fail():
    """A stripping test that passes because nothing differs proves nothing."""
    parquet = render_definition(semantic(), PARQUET)
    sql = render_definition(semantic(), SQL)
    assert parquet["tables/entity_0.tmdl"] != sql["tables/entity_0.tmdl"]


def test_an_import_parquet_path_and_a_direct_query_sql_path_are_the_two_shapes():
    """APT-2026-0211 and 0212 both end at Parquet, because Power BI has no
    SQLite connector. 0230 is the only path where Power BI talks to a database."""
    assert ParquetSource(directory="x").mode == "import"
    assert SqlSource(server="s", database="d").mode == "directQuery"


def test_the_definition_holds_one_file_per_table_plus_four():
    sm = semantic(n_tables=4)
    files = render_definition(sm, PARQUET)
    assert len(files) == len(sm.tables) + 4
    assert "database.tmdl" in files
    assert "model.tmdl" in files
    assert "relationships.tmdl" in files
    assert "cultures/en-US.tmdl" in files


# ---------------------------------------------- escaping at the boundary


def test_a_leading_digit_is_quoted_because_model_content_reaches_it():
    """MEASURED reachability: a tagged value named "2024 Target" becomes the
    column `2024_target` through `ea_census.snake_case` with no hand-editing.
    Unquoted it is invalid TMDL and Power BI rejects the whole project."""
    assert ident("2024_target") == "'2024_target'"
    assert ident("target_2024") == "target_2024"


def test_non_ascii_letters_are_quoted():
    """`str.isalnum()` is true for Greek, Cyrillic and accented letters, which
    are not safe to leave bare in TMDL."""
    assert ident("naive") == "naive"
    assert ident("na\u00efve").startswith("'")
    assert ident("\u03b1\u03b2\u03b3").startswith("'")


def test_an_m_literal_escapes_the_quote_that_would_end_it():
    """A `"` terminates the literal and admits arbitrary M, which runs on
    refresh on the analyst's machine."""
    assert m_literal('a"b') == 'a""b'
    assert '""' in m_literal('x" & Web.Contents("http://example.invalid") & "')


def test_an_m_literal_escapes_the_hash_that_introduces_an_escape():
    """`#(lf)` in a path silently becomes a newline; an unknown sequence is a
    parse error. Both are the same character doing the damage."""
    assert m_literal("a#(lf)b") == "a#(23)(lf)b"
    assert "#" not in m_literal("c#d").replace("#(23)", "")


def test_the_partition_sources_actually_use_the_escaper():
    """The point is escaping at the SINK. The safety that makes this
    unreachable today lives in `ea_census.snake_case`, two modules away, and is
    enforced by nothing here."""
    sm = semantic()
    hostile = ParquetSource(directory=r'C:\out" & Web.Contents("http://x") & "')
    line = next(l for l in render_table(sm.table("entity_0"), hostile).split(NEWLINE)
                if "Parquet.Document" in l)
    # Every quote from the injected value survives as a DOUBLED quote, so the
    # literal is never terminated early and the M that follows stays data.
    assert '""' in line
    assert line.count('"') % 2 == 0
    sql = render_table(sm.table("entity_0"),
                       SqlSource(server='s"x', database='d#(lf)y'))
    assert 's""x' in sql
    assert "#(23)(lf)" in sql
