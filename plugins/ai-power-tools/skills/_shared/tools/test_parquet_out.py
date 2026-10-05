#!/usr/bin/env python3
"""Tests for the Parquet sink.

    python -m pytest _shared/tools/test_parquet_out.py -q

Everything about the SHAPE of the output is pure and runs with pyarrow absent -
that is the point of keeping the dependency behind a flag. The handful of tests
that actually write a file skip when pyarrow is missing, and say so rather than
passing vacuously.
"""
from __future__ import annotations

import pytest

import parquet_out
from ddl import FRAME_DDL, physical
from load import LOAD_RUN, build_database, entity_columns
from parquet_out import (PYARROW_AVAILABLE, ParquetError, build_parquet,
                         parquet_schema, parquet_type)
from pivot import PivotResult
from report_model import Column, ReportModel, Table

needs_pyarrow = pytest.mark.skipif(not PYARROW_AVAILABLE,
                                   reason="pyarrow is not installed")


def model():
    return ReportModel(technology_id="WBA", tables=[
        Table(name="business_application", entity_key="k", stereotype="S",
              columns=[
                  Column(name="criticality", source_tag="criticality",
                         sql_type="TEXT"),
                  Column(name="audit_logging_enabled",
                         source_tag="auditLoggingEnabled", sql_type="INTEGER"),
                  Column(name="uptime", source_tag="uptime", sql_type="REAL"),
              ]),
    ])


def pivot_result():
    return PivotResult(
        rows={"business_application": [
            {"ea_guid": "{A}", "name": "Core Banking", "metaclass": "Component",
             "criticality": "Business-Critical", "audit_logging_enabled": 1,
             "uptime": 99.95},
            {"ea_guid": "{B}", "name": "Payments", "metaclass": "Component",
             "criticality": None, "audit_logging_enabled": None, "uptime": None},
        ]},
        tag_value=[{"ea_guid": "{A}", "tag": "regulatoryScope", "value": "GLBA"}],
        coverage=[{"table_name": "business_application", "tag": "criticality",
                   "present": 2, "populated": 1, "total": 2, "coverage": 0.5}],
    )


def frame_rows():
    return {"element": [{"ea_guid": "{A}", "entity_table": "business_application",
                         "package_id": 1},
                        {"ea_guid": "{B}", "entity_table": "business_application",
                         "package_id": 1}],
            "pkg": [{"package_id": 1, "parent_id": None, "name": "Apps",
                     "path": "Apps", "depth": 1}]}


# ------------------------------------------------------- types and schema


def test_declared_sql_types_map_to_parquet_types():
    assert parquet_type("TEXT") == "string"
    assert parquet_type("INTEGER") == "int64"
    assert parquet_type("REAL") == "double"


def test_an_unknown_type_falls_back_to_string():
    assert parquet_type("BLOB") == "string"
    assert parquet_type("") == "string"


def test_the_schema_covers_every_frame_table_and_every_entity_table():
    schemas = parquet_schema(model())
    for name in FRAME_DDL:
        assert physical(name) in schemas
    assert "business_application" in schemas
    assert len(schemas) == len(FRAME_DDL) + 1


def test_tables_are_keyed_by_their_physical_name():
    """Files are named as the database names its tables, so the semantic model's
    `source_name` finds them and a reconciliation needs no translation."""
    schemas = parquet_schema(model())
    assert "_keymap" in schemas
    assert "element" not in schemas


def test_frame_columns_come_from_the_ddl_in_order():
    schemas = parquet_schema(model())
    for name, spec in FRAME_DDL.items():
        assert [c for c, _ in schemas[physical(name)]] == [c for c, _ in spec]


def test_entity_columns_match_what_the_loader_inserts():
    """If the two disagree, one sink has a column the other does not and the
    `same shape` guarantee between 0211 and 0212 is already broken."""
    m = model()
    schemas = parquet_schema(m)
    for table, cols in entity_columns(m).items():
        assert [c for c, _ in schemas[table]] == cols


def test_a_column_keeps_its_declared_type_not_one_inferred_from_the_rows():
    """Inferring would make the schema a function of which rows are populated,
    so a refresh could silently change a column's type."""
    cols = dict(parquet_schema(model())["business_application"])
    assert cols["criticality"] == "string"
    assert cols["audit_logging_enabled"] == "int64"
    assert cols["uptime"] == "double"


def test_the_schema_is_pure_and_needs_no_pyarrow():
    """Asserted explicitly: the shape of the output must be reviewable and
    testable in an environment with no compiled wheel."""
    assert parquet_schema(model())


# ----------------------------------------------------------- the contract


def test_load_run_may_not_be_passed_in():
    with pytest.raises(ParquetError, match="written by this function"):
        build_parquet("x", model(), pivot_result(), {LOAD_RUN: []},
                      run_id="r", run_at="t")


def test_a_non_frame_table_is_refused_rather_than_ignored():
    with pytest.raises(ParquetError, match="not frame tables"):
        build_parquet("x", model(), pivot_result(), {"invented": []},
                      run_id="r", run_at="t")


def test_pyarrow_absent_says_so_and_does_not_offer_csv(monkeypatch):
    """A CSV fallback would quietly give back the defect Parquet was chosen to
    remove - the measured `Column1...ColumnN` load.

    The flag is patched rather than the test skipped, so this branch is covered
    whether or not the machine running the suite happens to have pyarrow. A
    guard that only runs on the machines where it cannot matter is not a test."""
    monkeypatch.setattr(parquet_out, "PYARROW_AVAILABLE", False)
    with pytest.raises(ParquetError) as e:
        build_parquet("x", model(), pivot_result(), run_id="r", run_at="t")
    assert "pyarrow" in str(e.value)
    assert "CSV is not a substitute" in str(e.value)


def test_the_argument_check_still_fires_first_when_pyarrow_is_absent(monkeypatch):
    """The ordering bug this caught: a caller who passed the wrong thing was
    told to install pyarrow, which sends them to fix the wrong problem."""
    monkeypatch.setattr(parquet_out, "PYARROW_AVAILABLE", False)
    with pytest.raises(ParquetError, match="not frame tables"):
        build_parquet("x", model(), pivot_result(), {"invented": []},
                      run_id="r", run_at="t")


# ------------------------------------------------------------- the writing


@needs_pyarrow
def test_one_file_per_table_is_written(tmp_path):
    result = build_parquet(tmp_path, model(), pivot_result(), frame_rows(),
                           run_id="r1", run_at="2026-10-02T00:00:00Z")
    assert len(result.files) == len(FRAME_DDL) + 1
    assert (tmp_path / "business_application.parquet").exists()
    assert (tmp_path / "_keymap.parquet").exists()


@needs_pyarrow
def test_the_types_survive_the_round_trip(tmp_path):
    import pyarrow.parquet as pq
    build_parquet(tmp_path, model(), pivot_result(), frame_rows(),
                  run_id="r1", run_at="t")
    schema = pq.read_schema(tmp_path / "business_application.parquet")
    assert str(schema.field("criticality").type) == "string"
    assert str(schema.field("audit_logging_enabled").type) == "int64"
    assert str(schema.field("uptime").type) == "double"


@needs_pyarrow
def test_an_absent_tagged_value_stays_null_rather_than_becoming_a_default(tmp_path):
    import pyarrow.parquet as pq
    build_parquet(tmp_path, model(), pivot_result(), frame_rows(),
                  run_id="r1", run_at="t")
    table = pq.read_table(tmp_path / "business_application.parquet")
    assert table.column("uptime").to_pylist() == [99.95, None]
    assert table.column("criticality").to_pylist() == ["Business-Critical", None]


@needs_pyarrow
def test_the_audit_row_carries_the_true_total_and_no_reconciliation_verdict(tmp_path):
    """A build that claims to be reconciled before anything checked it is the
    defect this column exists to expose."""
    import pyarrow.parquet as pq
    result = build_parquet(tmp_path, model(), pivot_result(), frame_rows(),
                           run_id="r1", run_at="t")
    row = pq.read_table(tmp_path / "_load_run.parquet").to_pylist()[0]
    assert row["run_id"] == "r1"
    assert row["reconciled"] is None
    assert row["mismatches"] is None
    assert row["rows_loaded"] == result.rows_written - 1


@needs_pyarrow
def test_existing_files_are_not_replaced_without_being_asked(tmp_path):
    build_parquet(tmp_path, model(), pivot_result(), frame_rows(),
                  run_id="r1", run_at="t")
    with pytest.raises(ParquetError, match="already in"):
        build_parquet(tmp_path, model(), pivot_result(), frame_rows(),
                      run_id="r2", run_at="t")
    build_parquet(tmp_path, model(), pivot_result(), frame_rows(),
                  run_id="r2", run_at="t", overwrite=True)


@needs_pyarrow
def test_both_sinks_report_the_same_warnings_and_notes(tmp_path):
    """The reason this test exists: they had already diverged. The Parquet sink
    replicated `uncoercible` and `excluded` but not `unplaced`, so a customer on
    the Parquet-only path never heard that tag rows reached no table - which is
    exactly the silent under-reporting 0212's own criteria name."""
    m, fr = model(), frame_rows()
    pr = pivot_result()
    pr.unplaced = [{"ea_guid": "{C}", "tag": "owner", "value": ""}]
    pr.uncoercible = [{"ea_guid": "{A}", "table": "business_application",
                       "column": "audit_logging_enabled", "sql_type": "INTEGER",
                       "value": "maybe"}]
    pr.excluded = [{"ea_guid": "{D}", "tag": "criticality", "value": "High"}]

    db = build_database(tmp_path / "r.sqlite", m, pr, fr, run_id="r1", run_at="t")
    pq_result = build_parquet(tmp_path / "parquet", m, pr, fr,
                              run_id="r1", run_at="t")
    assert pq_result.warnings == db.warnings
    assert pq_result.notes == db.notes
    assert any("reached no table" in w for w in pq_result.warnings)


@needs_pyarrow
def test_a_table_dropped_from_the_model_does_not_survive_a_re_emit(tmp_path):
    """The emitter owns the WHOLE set, as `build_database` does by unlinking the
    database first. Writing file by file would leave a `.parquet` for a table
    the model no longer has - a table invisible to a reconciliation keyed on the
    model, which is the failure mode this family has produced before."""
    build_parquet(tmp_path, model(), pivot_result(), frame_rows(),
                  run_id="r1", run_at="t")
    stale = tmp_path / "retired_stereotype.parquet"
    stale.write_bytes((tmp_path / "business_application.parquet").read_bytes())

    result = build_parquet(tmp_path, model(), pivot_result(), frame_rows(),
                           run_id="r2", run_at="t", overwrite=True)
    assert not stale.exists()
    assert any("retired_stereotype" in n for n in result.notes)


@needs_pyarrow
def test_a_stale_file_is_left_alone_when_overwrite_was_not_asked_for(tmp_path):
    """Deleting a file the caller did not name would be the sink reaching
    outside what it was asked to do."""
    stale = tmp_path / "not_ours.parquet"
    stale.write_bytes(b"not parquet")
    build_parquet(tmp_path, model(), pivot_result(), frame_rows(),
                  run_id="r1", run_at="t")
    assert stale.exists()


@needs_pyarrow
def test_the_two_sinks_agree_on_every_row_count(tmp_path):
    """THE 0211/0212 GUARANTEE. The same inputs through both sinks must produce
    the same shape - if they can disagree, none of the Power BI findings apply
    to one of the paths."""
    m, pr, fr = model(), pivot_result(), frame_rows()
    db = build_database(tmp_path / "r.sqlite", m, pr, fr,
                        run_id="r1", run_at="t")
    pq_result = build_parquet(tmp_path / "parquet", m, pr, fr,
                              run_id="r1", run_at="t")
    # `build_database` keys by pipeline name, this by physical name.
    assert {physical(k): v for k, v in db.rows_by_table.items()} == \
        pq_result.rows_by_table


def test_both_sinks_draw_their_warnings_from_the_same_place():
    """PURE, deliberately not `@needs_pyarrow`. The parity this guards is a
    property of the shared helper, not of the writer, and on a machine without
    the wheel the `@needs_pyarrow` version of this assertion does not run at
    all - which is how the divergence survived in the first place."""
    import load
    import parquet_out as po
    assert po.pivot_warnings is load.pivot_warnings
    assert po.pivot_notes is load.pivot_notes

    pr = pivot_result()
    pr.unplaced = [{"ea_guid": "{C}"}]
    assert any("reached no table" in w for w in load.pivot_warnings(pr))
