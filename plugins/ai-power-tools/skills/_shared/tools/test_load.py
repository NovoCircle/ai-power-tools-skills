#!/usr/bin/env python3
"""Tests for the SQLite loader.

    python -m pytest _shared/tools/test_load.py -q

These touch the filesystem, because the thing under test is a file. They touch no
repository and no COM object, and every database goes in pytest's `tmp_path`.

Several of these are NEGATIVE tests - they break something on purpose and assert
that the check notices. Up to this point every check in this toolchain had passed
on its first run, which proves the checks run and proves nothing at all about
whether they can detect a fault.
"""
from __future__ import annotations

import sqlite3

import pytest

from ddl import FRAME_DDL, physical
from ea_census import Entity, ElementCensus, TagStat
from load import (
    LOAD_RUN,
    LoadError,
    build_database,
    database_counts,
    entity_columns,
    record_reconciliation,
    scalar_counts,
)
from frame import element_rows
from pivot import pivot
from reconcile import domain_violations, reconcile
from report_model import build_report_model

NS = "WestbrookBankArchitecture"
RUN = "run-0001"
AT = "2026-10-01 12:00:00"

MDG = {
    "tech_id": "WBA",
    "technology_name": "WBA (Westbrook Bank Architecture)",
    "stereotypes": [
        {"name": "WBABusinessApplication", "alias": "Business Application",
         "base_metaclass": "Component", "notes": "Core business application",
         "tagged_values": [
             {"name": "criticality", "type": "enumeration",
              "description": "How badly its loss would hurt",
              "values": ["Mission-Critical", "Business-Critical", "Standard"]},
             {"name": "businessOwner", "type": "String",
              "description": "Owning team"},
         ]},
    ],
}


def _census(*entities):
    c = ElementCensus()
    c.entities = list(entities)
    return c


def _entity(key, stereo, guids, metaclass="Component", fqname="", profile=""):
    e = Entity(key=key, stereotype=stereo, fqname=fqname, profile=profile)
    e.guids.update(guids)
    e.metaclasses[metaclass] = len(guids)
    return e


def _stat(tag, present, populated, values):
    s = TagStat(tag=tag, present=present, populated=populated)
    for v in values:
        s.values[v] += 1
    return s


@pytest.fixture
def fixture():
    """One declared stereotype, two elements, two tags - enough to exercise
    typing, an enumeration, the bridge and the audit row."""
    key = f"{NS}::WBABusinessApplication"
    ent = _entity(key, "WBABusinessApplication", ["{A}", "{B}"],
                  fqname=key, profile=NS)
    stats = {key: [_stat("criticality", 2, 2, ["Standard", "Mission-Critical"]),
                   _stat("businessOwner", 2, 2, ["Payments", "Lending"])]}
    model = build_report_model(_census(ent), stats, MDG)
    elements = [
        {"ea_guid": "{A}", "Object_ID": 1, "Name": "Core Ledger",
         "Object_Type": "Component", "Package_ID": 5},
        {"ea_guid": "{B}", "Object_ID": 2, "Name": "Card Switch",
         "Object_Type": "Component", "Package_ID": 5},
    ]
    props = [
        {"ea_guid": "{A}", "Property": "criticality", "Value": "Mission-Critical"},
        {"ea_guid": "{A}", "Property": "businessOwner", "Value": "Payments"},
        {"ea_guid": "{B}", "Property": "criticality", "Value": "Standard"},
        {"ea_guid": "{B}", "Property": "businessOwner", "Value": "Lending"},
    ]
    placement = {"{A}": [key], "{B}": [key]}
    pv = pivot(model, elements, props, placement)
    return model, pv, elements, placement, _census(ent)


# --- schema -----------------------------------------------------------------

def test_every_frame_and_entity_table_is_created(fixture, tmp_path):
    model, pv, elements, placement, _ = fixture
    db = tmp_path / "r.sqlite"
    build_database(db, model, pv, {"element": element_rows(elements, model, placement)},
                   run_id=RUN, run_at=AT)
    conn = sqlite3.connect(str(db))
    names = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    conn.close()
    assert {physical(n) for n in FRAME_DDL} <= names
    assert {t.name for t in model.tables} <= names


def test_insert_column_order_matches_the_create_table(fixture):
    model, _, _, _, _ = fixture
    cols = entity_columns(model)["business_application"]
    assert cols[:3] == ["ea_guid", "name", "metaclass"]
    assert cols[3:] == [c.name for c in model.tables[0].columns]


def test_values_land_where_the_dictionary_says_they_do(fixture, tmp_path):
    model, pv, _, _, _ = fixture
    db = tmp_path / "r.sqlite"
    build_database(db, model, pv, run_id=RUN, run_at=AT)
    conn = sqlite3.connect(str(db))
    rows = dict(conn.execute(
        'SELECT "name", "criticality" FROM "business_application"').fetchall())
    conn.close()
    assert rows == {"Core Ledger": "Mission-Critical", "Card Switch": "Standard"}


def test_declared_type_reaches_the_database_schema(fixture, tmp_path):
    model, pv, _, _, _ = fixture
    db = tmp_path / "r.sqlite"
    build_database(db, model, pv, run_id=RUN, run_at=AT)
    conn = sqlite3.connect(str(db))
    types = {r[1]: r[2] for r in
             conn.execute('PRAGMA table_info("business_application")')}
    conn.close()
    assert types["criticality"] == "TEXT"          # declared enumeration
    assert types["ea_guid"] == "TEXT"


# --- refusing to lose or clobber -------------------------------------------

def test_an_unknown_column_is_refused_not_silently_dropped(fixture, tmp_path):
    """The row count would still have matched, so the reconciliation would have
    reported RECONCILED while a value went missing."""
    model, pv, _, _, _ = fixture
    pv.rows["business_application"][0]["not_a_column"] = "x"
    with pytest.raises(LoadError, match="not_a_column"):
        build_database(tmp_path / "r.sqlite", model, pv, run_id=RUN, run_at=AT)


def test_a_missing_key_becomes_null_because_absent_is_a_real_value(fixture, tmp_path):
    model, pv, _, _, _ = fixture
    del pv.rows["business_application"][0]["business_owner"]
    db = tmp_path / "r.sqlite"
    build_database(db, model, pv, run_id=RUN, run_at=AT)
    conn = sqlite3.connect(str(db))
    n = conn.execute('SELECT COUNT(*) FROM "business_application" '
                     'WHERE "business_owner" IS NULL').fetchone()[0]
    conn.close()
    assert n == 1


def test_an_existing_database_is_not_overwritten_by_default(fixture, tmp_path):
    model, pv, _, _, _ = fixture
    db = tmp_path / "r.sqlite"
    db.write_text("not a database")
    with pytest.raises(LoadError, match="overwrite"):
        build_database(db, model, pv, run_id=RUN, run_at=AT)
    assert db.read_text() == "not a database"


def test_overwrite_replaces_it_when_asked(fixture, tmp_path):
    model, pv, _, _, _ = fixture
    db = tmp_path / "r.sqlite"
    db.write_text("not a database")
    res = build_database(db, model, pv, run_id=RUN, run_at=AT, overwrite=True)
    assert res.rows_by_table["business_application"] == 2


def test_the_loader_will_not_let_a_caller_write_the_audit_row(fixture, tmp_path):
    model, pv, _, _, _ = fixture
    with pytest.raises(LoadError, match=LOAD_RUN):
        build_database(tmp_path / "r.sqlite", model, pv, {LOAD_RUN: []},
                       run_id=RUN, run_at=AT)


def test_a_frame_table_that_does_not_exist_is_refused(fixture, tmp_path):
    model, pv, _, _, _ = fixture
    with pytest.raises(LoadError, match="invented"):
        build_database(tmp_path / "r.sqlite", model, pv, {"invented": []},
                       run_id=RUN, run_at=AT)


# --- the audit row ----------------------------------------------------------

def test_load_run_records_the_build_but_claims_nothing_about_reconciliation(
        fixture, tmp_path):
    model, pv, _, _, _ = fixture
    db = tmp_path / "r.sqlite"
    res = build_database(db, model, pv, run_id=RUN, run_at=AT,
                         repository="WestbrookBank.qea", spec_hash="abc123")
    conn = sqlite3.connect(str(db))
    row = conn.execute(
        'SELECT "run_id", "run_at", "repository", "spec_hash", "rows_loaded", '
        '"reconciled", "mismatches" FROM "_load_run"').fetchone()
    conn.close()
    assert row[:4] == (RUN, AT, "WestbrookBank.qea", "abc123")
    assert row[4] == res.rows_loaded
    assert row[5] is None and row[6] is None     # nothing has checked anything yet


def test_rows_loaded_excludes_the_audit_row_itself(fixture, tmp_path):
    model, pv, _, _, _ = fixture
    res = build_database(tmp_path / "r.sqlite", model, pv, run_id=RUN, run_at=AT)
    assert res.rows_by_table[LOAD_RUN] == 1
    assert res.rows_loaded == sum(
        n for t, n in res.rows_by_table.items() if t != LOAD_RUN)


def test_recording_a_reconciliation_marks_the_run(fixture, tmp_path):
    model, pv, _, _, census = fixture
    db = tmp_path / "r.sqlite"
    build_database(db, model, pv, run_id=RUN, run_at=AT)
    rec = reconcile(census, database_counts(db, model),
                    entity_key_of_table={t.name: t.entity_key for t in model.tables})
    assert record_reconciliation(db, RUN, rec) is True
    conn = sqlite3.connect(str(db))
    assert conn.execute('SELECT "reconciled", "mismatches" FROM "_load_run"'
                        ).fetchone() == (1, 0)
    conn.close()


def test_recording_against_a_run_that_is_not_there_reports_failure(fixture, tmp_path):
    """Returning True here would be the gate defect all over again: a verdict
    reported for a row that was never written."""
    model, pv, _, _, census = fixture
    db = tmp_path / "r.sqlite"
    build_database(db, model, pv, run_id=RUN, run_at=AT)
    rec = reconcile(census, database_counts(db, model),
                    entity_key_of_table={t.name: t.entity_key for t in model.tables})
    assert record_reconciliation(db, "some-other-run", rec) is False


# --- the issued-SQL log -----------------------------------------------------

def test_every_statement_is_logged_in_issue_order(fixture, tmp_path):
    model, pv, _, _, _ = fixture
    res = build_database(tmp_path / "r.sqlite", model, pv, run_id=RUN, run_at=AT)
    creates = [s for s in res.sql_log if s.startswith("CREATE TABLE")]
    assert len(creates) == len(FRAME_DDL) + len(model.tables)
    assert res.sql_log.index(creates[-1]) < next(
        i for i, s in enumerate(res.sql_log) if s.startswith("INSERT"))
    assert res.statements == len(res.sql_log)


def test_the_log_carries_statements_and_counts_but_never_a_value(fixture, tmp_path):
    """The log gets attached to tickets. The values are customer content."""
    model, pv, _, _, _ = fixture
    res = build_database(tmp_path / "r.sqlite", model, pv, run_id=RUN, run_at=AT)
    blob = "\n".join(res.sql_log)
    for secret in ("Mission-Critical", "Payments", "Core Ledger", "Lending"):
        assert secret not in blob
    assert 'INSERT INTO "business_application"' in blob
    assert "-- 2 rows" in blob


def test_a_table_that_received_nothing_is_logged_as_zero_not_omitted(
        fixture, tmp_path):
    model, pv, _, _, _ = fixture
    res = build_database(tmp_path / "r.sqlite", model, pv, run_id=RUN, run_at=AT)
    assert any('-- INSERT INTO "_diagram": 0 rows' == s for s in res.sql_log)


# --- reading it back --------------------------------------------------------

def test_counts_are_read_back_from_the_database_not_from_the_input(
        fixture, tmp_path):
    model, pv, _, _, _ = fixture
    db = tmp_path / "r.sqlite"
    build_database(db, model, pv, run_id=RUN, run_at=AT)
    assert database_counts(db, model) == {"business_application": 2}
    assert scalar_counts(db)["tag_value"] == 4


def test_a_row_deleted_after_the_load_is_caught_by_the_reconciliation(
        fixture, tmp_path):
    """The whole point of counting back. Build it, break it, and assert the check
    FAILS and the exit code is non-zero - the prototype printed NOT RECONCILED
    and returned 0, so every pipeline reading the status saw success."""
    model, pv, _, _, census = fixture
    db = tmp_path / "r.sqlite"
    build_database(db, model, pv, run_id=RUN, run_at=AT)

    conn = sqlite3.connect(str(db))
    conn.execute('DELETE FROM "business_application" WHERE "ea_guid" = \'{A}\'')
    conn.commit()
    conn.close()

    rec = reconcile(census, database_counts(db, model),
                    entity_key_of_table={t.name: t.entity_key for t in model.tables})
    assert not rec.ok
    assert rec.exit_code == 1
    assert [c.label for c in rec.failures] == ["business_application"]
    assert rec.failures[0].delta == -1


def test_a_tag_value_removed_after_the_load_is_caught_as_a_scalar_mismatch(
        fixture, tmp_path):
    model, pv, _, _, census = fixture
    db = tmp_path / "r.sqlite"
    build_database(db, model, pv, run_id=RUN, run_at=AT)

    conn = sqlite3.connect(str(db))
    conn.execute('DELETE FROM "_tag_value" WHERE "tag" = \'businessOwner\'')
    conn.commit()
    conn.close()

    rec = reconcile(census, database_counts(db, model),
                    entity_key_of_table={t.name: t.entity_key for t in model.tables},
                    scalars={"tag_value": (4, scalar_counts(db)["tag_value"])})
    assert rec.exit_code == 1
    assert [c.label for c in rec.failures] == ["tag_value"]


# --- element, the load-bearing frame table ---------------------------------
#
# The shaping itself is tested in test_frame.py. What matters here is that what
# that module produces is exactly what this one can insert.

def test_element_rows_fit_the_frame_schema_and_load(fixture, tmp_path):
    model, pv, elements, placement, _ = fixture
    rows = element_rows(elements, model, placement)
    assert set(rows[0]) == {c for c, _ in FRAME_DDL["element"]}
    res = build_database(tmp_path / "r.sqlite", model, pv, {"element": rows},
                         run_id=RUN, run_at=AT)
    assert res.rows_by_table["element"] == 2


# --- domain validation ------------------------------------------------------

def test_a_value_outside_the_declared_enumeration_is_reported(fixture):
    model, pv, _, _, _ = fixture
    pv.rows["business_application"][0]["criticality"] = "Pretty Important"
    v = domain_violations(model, pv.rows)
    assert [(x["column"], x["value"], x["count"]) for x in v] == \
        [("criticality", "Pretty Important", 1)]


def test_in_domain_values_report_nothing(fixture):
    model, pv, _, _, _ = fixture
    assert domain_violations(model, pv.rows) == []


def test_an_absent_value_is_coverage_not_a_violation(fixture):
    model, pv, _, _, _ = fixture
    pv.rows["business_application"][0]["criticality"] = None
    pv.rows["business_application"][1]["criticality"] = "   "
    assert domain_violations(model, pv.rows) == []


def test_an_observed_domain_cannot_be_violated():
    """It is by construction every value that was seen."""
    key = "Thing|Component"
    ent = _entity(key, "Thing", ["{A}", "{B}", "{C}"])
    # A value has to RECUR before observation will call it a domain at all - a
    # set of values each seen once is free text, not an enumeration.
    stats = {key: [_stat("status", 3, 3, ["live", "live", "dead"])]}
    model = build_report_model(_census(ent), stats, {})
    assert model.tables[0].columns[0].enum_source == "observed"
    rows = {model.tables[0].name: [{"ea_guid": "{A}", "status": "anything at all"}]}
    assert domain_violations(model, rows) == []


def test_a_domain_violation_does_NOT_fail_the_load_reconciliation(fixture, tmp_path):
    """The first live run reported NOT RECONCILED over a database that had loaded
    every one of 298 elements faithfully, because a value outside a declared
    enumeration was being counted as a load failure. It is not one: the value is in
    the repository and it is in the database. Surfacing the drift is the capability;
    failing the build on it would do so on every model carrying any drift at all."""
    model, pv, _, _, census = fixture
    pv.rows["business_application"][0]["criticality"] = "Pretty Important"
    db = tmp_path / "r.sqlite"
    build_database(db, model, pv, run_id=RUN, run_at=AT)
    rec = reconcile(census, database_counts(db, model),
                    entity_key_of_table={t.name: t.entity_key for t in model.tables})
    assert rec.ok
    assert rec.exit_code == 0
    # ...and the violation is still reported, just not as a failed load.
    assert len(domain_violations(model, pv.rows)) == 1


def test_a_multi_valued_column_is_checked_value_by_value():
    key = f"{NS}::WBAApp"
    ent = _entity(key, "WBAApp", ["{A}"], fqname=key, profile=NS)
    stats = {key: [_stat("scope", 1, 1, ["GLBA, SOX"])]}
    mdg = {"stereotypes": [{"name": "WBAApp", "tagged_values": [
        {"name": "scope", "type": "enumeration", "values": ["GLBA", "FFIEC"]}]}]}
    model = build_report_model(_census(ent), stats, mdg, multi_valued={"scope"})
    rows = {model.tables[0].name: [{"ea_guid": "{A}", "scope": "GLBA, SOX"}]}
    v = domain_violations(model, rows)
    assert [x["value"] for x in v] == ["SOX"]       # GLBA is declared, SOX is not
