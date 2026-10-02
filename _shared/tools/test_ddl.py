#!/usr/bin/env python3
"""Tests for DDL generation.

    python -m pytest _shared/tools/test_ddl.py -q

Nothing here touches a repository, a COM object or the filesystem.
"""
from __future__ import annotations

from ddl import (FRAME_DDL, entity_table_ddl, frame_table_ddl, generate_ddl,
                 physical, quote)
from report_model import Column, ReportModel, Table


def table(name="business_application", cols=()):
    return Table(name=name, entity_key="k", stereotype="S",
                 columns=[Column(name=c, source_tag=c, sql_type=t) for c, t in cols])


def test_identifiers_are_double_quoted():
    assert quote("business_application") == '"business_application"'


def test_an_embedded_quote_is_doubled_not_stripped():
    """An identifier that closes its own quote early is an injection, not a
    cosmetic problem."""
    assert quote('we"ird') == '"we""ird"'


def test_entity_table_has_guid_primary_key():
    """ea_guid is EA's stable natural key and survives a rebuild; a row number
    does not."""
    sql = entity_table_ddl(table())
    assert '"ea_guid" TEXT NOT NULL' in sql
    assert 'PRIMARY KEY ("ea_guid")' in sql


def test_columns_carry_their_declared_sql_type():
    sql = entity_table_ddl(table(cols=[("criticality", "TEXT"), ("human_in_loop", "INTEGER")]))
    assert '"criticality" TEXT' in sql
    assert '"human_in_loop" INTEGER' in sql


def test_every_frame_table_generates_under_its_physical_name():
    for name in FRAME_DDL:
        sql = frame_table_ddl(name)
        assert sql.startswith(f'CREATE TABLE "{physical(name)}" (')
        assert sql.rstrip().endswith(");")


def test_every_frame_table_is_prefixed_so_the_vocabulary_sorts_first():
    """The customer is promised their business vocabulary. Plumbing that sorts
    in among it breaks that promise (APT-2026-0226)."""
    for name in FRAME_DDL:
        assert physical(name).startswith("_")


def test_the_hub_is_a_key_map_and_carries_no_business_columns():
    """`name`, `metaclass` and `stereotype` belong to the entity tables.
    Duplicating them here is what made the database read as EA's metamodel."""
    cols = {c for c, _ in FRAME_DDL["element"]}
    assert cols == {"ea_guid", "entity_table", "package_id"}
    assert physical("element") == "_keymap"


def test_the_load_bearing_frame_tables_exist():
    """`element` resolves relationship endpoints; without it every edge touching
    an untyped element dangles. `tag_value` is the multi-value bridge.
    `tag_coverage` is what stops a roll-up over an empty tag reading as 100%."""
    for required in ("element", "rel_all", "tag_value", "tag_coverage",
                     "overflow_tag", "load_run"):
        assert required in FRAME_DDL


def test_element_carries_entity_table_so_the_remainder_stays_queryable():
    cols = [c for c, _ in FRAME_DDL["element"]]
    assert "entity_table" in cols
    assert "ea_guid" in cols


def test_tag_value_is_one_row_per_value():
    assert [c for c, _ in FRAME_DDL["tag_value"]] == ["ea_guid", "tag", "value"]


def test_frame_comes_before_entity_tables():
    """A loader has to populate `element` before anything references it."""
    model = ReportModel(tables=[table()])
    out = generate_ddl(model)
    first_entity = next(i for i, s in enumerate(out) if '"business_application"' in s)
    first_frame = next(i for i, s in enumerate(out) if '"_keymap"' in s)
    assert first_frame < first_entity


def test_frame_can_be_suppressed():
    model = ReportModel(tables=[table()])
    out = generate_ddl(model, include_frame=False)
    assert len(out) == 1
    assert '"business_application"' in out[0]


def test_generation_is_deterministic():
    model = ReportModel(tables=[table("a"), table("b")])
    assert generate_ddl(model) == generate_ddl(model)


def test_no_backend_specific_syntax_leaks_in():
    """Plain CREATE TABLE only. EA reports a statement its backend cannot run as
    a modal dialog that holds the COM connection until someone dismisses it, so
    the subset is deliberately narrow."""
    model = ReportModel(tables=[table(cols=[("x", "TEXT")])])
    joined = "\n".join(generate_ddl(model))
    for banned in ("AUTOINCREMENT", "IDENTITY", "SERIAL", "`", "[", "ENGINE=", "IF NOT EXISTS"):
        assert banned not in joined


def test_the_two_frame_lists_do_not_drift():
    """REGRESSION. `report_model.FRAME_TABLES` and `ddl.FRAME_DDL` are two
    statements of the same fact and they drifted: `overflow_tag` was defined in
    the DDL and missing from the model's list, so the model advertised ten frame
    tables while eleven were created, and the one holding sparse tags was
    invisible to anything reading `model.frame`.
    """
    from report_model import FRAME_TABLES
    assert set(FRAME_TABLES) == set(FRAME_DDL)
    assert list(FRAME_TABLES) == list(FRAME_DDL)      # order too


def test_generate_ddl_emits_exactly_one_statement_per_table():
    from report_model import FRAME_TABLES
    model = ReportModel(tables=[table("a"), table("b")])
    assert len(generate_ddl(model)) == len(FRAME_TABLES) + 2
