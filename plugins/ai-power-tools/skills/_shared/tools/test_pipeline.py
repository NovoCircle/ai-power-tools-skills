#!/usr/bin/env python3
"""Tests for the assembled reporting-database build.

    python -m pytest _shared/tools/test_pipeline.py -q

The fixture is the snapshot test's Westbrook Bank extract plus one element the
key map cannot hold: a component with no stereotype that sits on a diagram, is
the end of a connector, and owns an attribute.
"""
from __future__ import annotations

import copy
import json

import pytest

from ddl import FRAME_DDL
from load import database_counts, scalar_counts
from pipeline import (PipelineError, build_reporting_database, infer_namespace,
                      prepare, reconcile_against)
from test_snapshot import MDG, NS, TABLES

UNTYPED = "{U}"


def tables_with_an_untyped_element():
    t = copy.deepcopy(TABLES)
    t["object"].append({"Object_ID": 4, "ea_guid": UNTYPED, "Name": "Batch Scheduler",
                        "Object_Type": "Component", "Stereotype": "",
                        "Package_ID": 5})
    t["diagramobjects"].append({"Diagram_ID": 41, "Object_ID": 4})
    t["connector"].append({"Connector_ID": 13, "ea_guid": "{R3}", "Name": "triggers",
                           "Connector_Type": "Dependency", "Stereotype": "",
                           "Start_Object_ID": 1, "End_Object_ID": 4})
    t["attribute"].append({"ID": 23, "Object_ID": 4, "Name": "cron",
                           "Type": "String", "Scope": "Public"})
    t["objectproperties"].append({"PropertyID": 66, "Object_ID": 4,
                                  "Property": "businessOwner", "Value": "Ops"})
    return t


def prepared(tables=None):
    return prepare(tables or tables_with_an_untyped_element(), MDG,
                   namespace=NS, strip_prefix="WBA")


def build(tmp_path, p=None):
    return build_reporting_database(
        p or prepared(), tmp_path / "out", run_id="r1", run_at="2026-10-06 08:00:00",
        repository="WestbrookBank.qea", extract_run_id="x1", extract_digest="d1")


def test_an_untyped_element_is_left_out_of_every_frame_table():
    """Its diagram placement, its connector and its attribute reference an element
    the key map does not hold, so none of them is written."""
    p = prepared()
    assert UNTYPED not in p.placed
    assert UNTYPED not in {r["ea_guid"] for r in p.frame_rows["element"]}
    assert UNTYPED not in {r["ea_guid"] for r in p.frame_rows["diagram_object"]}
    assert UNTYPED not in {r["target_guid"] for r in p.frame_rows["rel_all"]}
    assert UNTYPED not in {r["element_guid"] for r in p.frame_rows["attribute"]}


def test_a_model_with_an_untyped_element_on_a_diagram_reconciles(tmp_path):
    """The case that stopped the documented build: it now loads, reconciles with
    every check run, and records the verdict."""
    b = build(tmp_path)
    assert b.reconciliation.exit_code == 0, b.reconciliation.summary()
    assert b.recorded
    assert "element (placed in an entity table)" in _report(tmp_path)


def test_the_five_files_are_written(tmp_path):
    build(tmp_path)
    assert sorted(p.name for p in (tmp_path / "out").iterdir()) == [
        "data-dictionary.md", "issued-sql.log", "manifest.json",
        "reconciliation.txt", "reporting.sqlite"]
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["reconciliation"]["ok"] is True


def test_an_existing_database_is_refused_unless_overwrite_is_passed(tmp_path):
    build(tmp_path)
    with pytest.raises(Exception, match="exists"):
        build(tmp_path)


def test_the_reconciliation_fails_when_a_count_read_back_is_wrong(tmp_path):
    """The repository side is computed from the extract, not from the frame, so a
    count that disagrees with it fails."""
    p = prepared()
    build(tmp_path, p)
    db = tmp_path / "out" / "reporting.sqlite"
    frame = scalar_counts(db)
    assert reconcile_against(p, database_counts(db, p.model), frame).exit_code == 0
    frame["rel_all"] += 1
    assert reconcile_against(p, database_counts(db, p.model), frame).exit_code != 0


@pytest.mark.parametrize("table", ["pkg", "rel_all", "attribute", "operation",
                                   "diagram"])
def test_a_row_that_never_reaches_the_database_fails_the_reconciliation(
        tmp_path, table):
    """The repository side is counted from the extract rows, so a frame row lost
    between `prepare` and the load is a mismatch rather than agreeing with itself."""
    p = prepared()
    assert p.frame_rows[table], f"the fixture needs at least one {table} row"
    p.frame_rows[table] = p.frame_rows[table][:-1]
    assert build(tmp_path, p).reconciliation.exit_code != 0


def test_a_tag_value_that_never_reaches_the_database_fails_the_reconciliation(
        tmp_path):
    p = prepared()
    p.result.tag_value.pop()
    assert build(tmp_path, p).reconciliation.exit_code != 0


def test_a_frame_count_that_is_missing_fails_rather_than_passing(tmp_path):
    p = prepared()
    build(tmp_path, p)
    db = tmp_path / "out" / "reporting.sqlite"
    frame = scalar_counts(db)
    del frame["attribute"]
    assert set(FRAME_DDL) - set(frame) == {"attribute"}
    assert reconcile_against(p, database_counts(db, p.model), frame).exit_code != 0


def test_a_frame_row_that_resolves_against_nothing_raises(monkeypatch):
    """If a frame builder ever writes a row the key map cannot resolve, `prepare`
    raises rather than handing back a frame that would not load cleanly."""
    import pipeline

    real = pipeline.diagram_object_rows
    monkeypatch.setattr(pipeline, "diagram_object_rows", lambda *a, **k: real(*a, **k) + [
        {"diagram_id": 41, "ea_guid": UNTYPED}])
    with pytest.raises(PipelineError, match="reference an element"):
        prepared()


def test_the_namespace_is_read_off_the_census():
    assert infer_namespace(tables_with_an_untyped_element(), MDG) == NS


def _report(tmp_path):
    return (tmp_path / "out" / "reconciliation.txt").read_text(encoding="utf-8")
