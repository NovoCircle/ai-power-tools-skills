#!/usr/bin/env python3
"""Tests for extract-snapshot retention, and the replay it exists to make possible.

    python -m pytest _shared/tools/test_snapshot.py -q

These touch the filesystem, because the thing under test is a directory of files.
They touch no repository and no COM object, and that is not merely convenient: A
REPLAY NEEDS NO EA, so a test of replay must not need one either. If any test here
ever acquires a COM dependency, the property being tested has been lost.

THE ACCEPTANCE TEST is `test_a_replayed_build_is_byte_identical_to_the_original`.
Everything the item exists for reduces to that one assertion. The rest of this
file is either a property that test leans on - a snapshot is retained, it is
identified, the build records which one it used - or a NEGATIVE test around the
two ways a replay could go quietly wrong: the snapshot has been pruned, or a
different snapshot is sitting under the same name. Both have to be loud. A replay
that rebuilt from the wrong rows and reported the result as the original figure is
worse than one that refused, because nothing downstream would notice.
"""
from __future__ import annotations

import json
import re
import shutil
import sqlite3

import pytest

from ea_census import build_stereotype_index, census_elements, tag_coverage
from extract import (
    KEEP_RUNS,
    MANIFEST_NAME,
    TABLE_NAMES,
    Extractor,
    Snapshot,
    SnapshotError,
    extract,
    list_snapshots,
    open_snapshot,
    prune_snapshots,
    snapshot_dir,
    snapshot_digest,
)
from frame import (attribute_rows, diagram_object_rows, diagram_rows, element_rows,
                   operation_rows, package_rows, relationship_rows)
from load import (
    LoadError,
    build_database,
    extract_reference,
    replay_snapshot,
)
from pivot import pivot
from report_model import build_report_model

NS = "WestbrookBankArchitecture"
STEREO = "WBABusinessApplication"
RUN = "run-0001"
AT = "2026-10-01 12:00:00"

MDG = {
    "tech_id": "WBA",
    "technology_name": "WBA (Westbrook Bank Architecture)",
    "stereotypes": [
        {"name": STEREO, "alias": "Business Application",
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

_STEREO_BLOCK = (f"@STEREO;Name={STEREO};GUID={{01}};"
                 f"FQName={NS}::{STEREO};@ENDSTEREO;")

#: One snapshot's worth of `t_*` rows, in the shape `extract.py` writes them.
#: Deliberately includes an untyped element, so the census has a remainder to
#: carry and the replayed database has something non-trivial to reproduce.
TABLES = {
    "object": [
        {"Object_ID": 1, "ea_guid": "{A}", "Name": "Core Ledger",
         "Object_Type": "Component", "Stereotype": STEREO, "Package_ID": 5},
        {"Object_ID": 2, "ea_guid": "{B}", "Name": "Card Switch",
         "Object_Type": "Component", "Stereotype": STEREO, "Package_ID": 5},
        {"Object_ID": 3, "ea_guid": "{C}", "Name": "Settlement Notes",
         "Object_Type": "Note", "Stereotype": "", "Package_ID": 5},
    ],
    "xref": [
        {"Client": "{A}", "Description": _STEREO_BLOCK},
        {"Client": "{B}", "Description": _STEREO_BLOCK},
    ],
    "objectproperties": [
        {"Object_ID": 1, "Property": "criticality", "Value": "Mission-Critical"},
        {"Object_ID": 1, "Property": "businessOwner", "Value": "Payments"},
        {"Object_ID": 2, "Property": "criticality", "Value": "Standard"},
        {"Object_ID": 2, "Property": "businessOwner", "Value": "Lending"},
    ],
    "package": [
        {"Package_ID": 1, "Parent_ID": 0, "Name": "Model"},
        {"Package_ID": 5, "Parent_ID": 1, "Name": "Applications"},
    ],
    "attribute": [
        {"ID": 21, "Object_ID": 1, "Name": "ledgerCode", "Type": "String",
         "Scope": "Public"},
    ],
    "operation": [
        {"OperationID": 31, "Object_ID": 1, "Name": "postEntry", "Type": "void",
         "Scope": "Public"},
    ],
    "diagram": [
        {"Diagram_ID": 41, "Name": "Payments Landscape",
         "Diagram_Type": "Logical", "Package_ID": 5},
    ],
    "diagramobjects": [
        {"Diagram_ID": 41, "Object_ID": 1},
        {"Diagram_ID": 41, "Object_ID": 2},
    ],
    "connector": [
        {"Connector_ID": 11, "ea_guid": "{R1}", "Name": "settles via",
         "Connector_Type": "Association", "Stereotype": "",
         "Start_Object_ID": 1, "End_Object_ID": 2},
    ],
    "connectortag": [
        {"PropertyID": 51, "ElementID": 11, "Property": "channel", "VALUE": "ACH"},
    ],
}


class _EchoRepo:
    """Echoes the statement back. The fake rows come from the parser instead,
    which is the seam `Extractor` already has for EA's XML row parser."""

    def SQLQuery(self, sql):          # noqa: N802 - matches EA's COM name
        return sql


def fake_extractor(tables=None):
    """An `Extractor` that answers each query from `tables`.

    Routes on the `FROM t_<name>` in the statement rather than on call order, so
    the fake cannot quietly drift out of step with the query constants. The word
    boundary is load-bearing: `t_object` is a prefix of `t_objectproperties`.
    """
    tables = TABLES if tables is None else tables

    def parse(sql):
        for name, rows in tables.items():
            if re.search(rf"FROM t_{name}\b", sql):
                return [dict(r) for r in rows]
        return []

    return Extractor(_EchoRepo(), parse)


def take_snapshot(root, run_id=RUN, run_at=AT, tables=None):
    return extract(fake_extractor(tables), root, run_id=run_id, run_at=run_at)


def build(db_path, tables, *, run_id, run_at,
          extract_run_id="", extract_digest=""):
    """The documented build, over extract rows.

    Mirrors `ea-reporting-database/SKILL.md` §3.3 on purpose rather than taking a
    shortcut through the census dataclasses: the replay guarantee is a property of
    that pipeline, and a test of a different pipeline would not test it.
    """
    objects, xrefs = tables["object"], tables["xref"]
    props, packages = tables["objectproperties"], tables["package"]

    xref_index = build_stereotype_index(xrefs)
    census = census_elements(objects, xref_index)
    guid_by_id = {int(o["Object_ID"]): o["ea_guid"] for o in objects}

    def guid_of_property(row):
        return guid_by_id.get(int(row["Object_ID"]), "")

    tag_stats = {e.key: tag_coverage(e, props, guid_of_property)
                 for e in census.entities}
    model = build_report_model(census, tag_stats, MDG,
                               namespace=NS, strip_prefix="WBA")
    result = pivot(model, objects, props, census.placement,
                   excluded_guids=census.excluded_guids,
                   guid_of_property=guid_of_property)

    in_scope = {o["ea_guid"] for o in objects} - census.excluded_guids

    def profile_of(guid):
        return next((s.profile for s in xref_index.get(guid, []) if s.profile), "")

    frame_rows = {
        "pkg": package_rows(packages),
        "element": element_rows(objects, model, census.placement,
                                excluded_guids=census.excluded_guids),
        "rel_all": relationship_rows(tables["connector"], guid_by_id,
                                     guids_in_scope=in_scope,
                                     profile_of=profile_of),
        "diagram": diagram_rows(tables["diagram"]),
        "attribute": attribute_rows(tables["attribute"], guid_by_id,
                                    guids_in_scope=in_scope),
        "operation": operation_rows(tables["operation"], guid_by_id,
                                    guids_in_scope=in_scope),
    }
    frame_rows["diagram_object"] = diagram_object_rows(
        tables["diagramobjects"], guid_by_id,
        diagram_ids={r["diagram_id"] for r in frame_rows["diagram"]},
        guids_in_scope=in_scope)

    return build_database(db_path, model, result, frame_rows,
                          run_id=run_id, run_at=run_at,
                          repository="WestbrookBank.qea",
                          extract_run_id=extract_run_id,
                          extract_digest=extract_digest)


# --- the snapshot is retained, not overwritten -------------------------------

def test_a_run_lands_under_its_own_run_id(tmp_path):
    manifest = take_snapshot(tmp_path)
    directory = snapshot_dir(tmp_path, RUN)
    assert directory.is_dir()
    assert {p.name for p in directory.iterdir()} == {
        *(f"{n}.json" for n in TABLE_NAMES), MANIFEST_NAME}
    assert manifest["run_id"] == RUN
    assert manifest["run_at"] == AT


def test_a_second_run_does_not_overwrite_the_first(tmp_path):
    """The defect this item exists to fix, asserted directly. Before retention,
    the second run left no trace of what the first one saw."""
    take_snapshot(tmp_path, run_id="run-a", run_at="2026-10-01 09:00:00")
    thinner = dict(TABLES, object=TABLES["object"][:1])
    take_snapshot(tmp_path, run_id="run-b", run_at="2026-10-01 10:00:00",
                  tables=thinner)

    assert [s["run_id"] for s in list_snapshots(tmp_path)] == ["run-b", "run-a"]
    assert len(open_snapshot(tmp_path, "run-a").tables["object"]) == 3
    assert len(open_snapshot(tmp_path, "run-b").tables["object"]) == 1


def test_the_snapshot_carries_scope_counts_and_issued_sql(tmp_path):
    """"Enough on its own": a replayed build has to be able to state what it was
    built from without inferring any of it."""
    take_snapshot(tmp_path)
    snap = open_snapshot(tmp_path, RUN)
    assert snap.manifest["scope"]["root_package_id"] is None
    assert snap.manifest["counts"]["object"] == 3
    labels = [e["label"] for e in snap.manifest["sql_log"]]
    assert "census: object" in labels
    assert all(e["sql"].startswith("SELECT") for e in snap.manifest["sql_log"])


def test_newest_first_is_by_recorded_run_at_not_by_mtime(tmp_path):
    """A copied or restored snapshot keeps the moment the extract was TAKEN, and
    that is the moment a figure is as-of. File mtime would reorder it."""
    take_snapshot(tmp_path, run_id="late", run_at="2026-10-04 08:00:00")
    take_snapshot(tmp_path, run_id="early", run_at="2026-10-01 08:00:00")
    assert [s["run_id"] for s in list_snapshots(tmp_path)] == ["late", "early"]


def test_a_root_with_no_snapshots_is_empty_not_an_error(tmp_path):
    assert list_snapshots(tmp_path / "nothing-here") == []


# --- identity ----------------------------------------------------------------

def test_the_digest_covers_the_rows_and_changes_when_they_do(tmp_path):
    take_snapshot(tmp_path, run_id="a")
    take_snapshot(tmp_path, run_id="b", run_at=AT,
                  tables=dict(TABLES, object=TABLES["object"][:2]))
    assert (snapshot_digest(snapshot_dir(tmp_path, "a"))
            != snapshot_digest(snapshot_dir(tmp_path, "b")))


def test_the_digest_ignores_run_identity_so_it_identifies_the_rows(tmp_path):
    """Two extracts of the same repository state hash the same. The digest answers
    "are these the same rows", not "is this the same run"."""
    take_snapshot(tmp_path, run_id="a", run_at="2026-10-01 08:00:00")
    take_snapshot(tmp_path, run_id="b", run_at="2026-10-02 08:00:00")
    assert (snapshot_digest(snapshot_dir(tmp_path, "a"))
            == snapshot_digest(snapshot_dir(tmp_path, "b")))


# --- retention is bounded, and pruning says what it took ---------------------

def test_the_bound_is_stated_and_is_a_count_of_runs():
    assert KEEP_RUNS == 10


def test_pruning_keeps_the_newest_and_removes_the_rest(tmp_path):
    for i in range(5):
        take_snapshot(tmp_path, run_id=f"run-{i}",
                      run_at=f"2026-10-0{i + 1} 08:00:00")
    removed = prune_snapshots(tmp_path, keep=2)
    assert [s["run_id"] for s in removed] == ["run-2", "run-1", "run-0"]
    assert [s["run_id"] for s in list_snapshots(tmp_path)] == ["run-4", "run-3"]
    assert not snapshot_dir(tmp_path, "run-0").exists()


def test_pruning_reports_what_it_removed_with_date_and_size(tmp_path):
    """The return value IS the feature. Silently discarding the evidence behind a
    figure somebody has quoted is the failure retention exists to prevent, so a
    caller that wants to say what went can always do so."""
    take_snapshot(tmp_path, run_id="keep", run_at="2026-10-02 08:00:00")
    take_snapshot(tmp_path, run_id="drop", run_at="2026-10-01 08:00:00")
    removed = prune_snapshots(tmp_path, keep=1)
    assert len(removed) == 1
    assert removed[0]["run_id"] == "drop"
    assert removed[0]["run_at"] == "2026-10-01 08:00:00"
    assert removed[0]["bytes"] > 0


def test_pruning_within_the_bound_removes_nothing(tmp_path):
    take_snapshot(tmp_path)
    assert prune_snapshots(tmp_path, keep=KEEP_RUNS) == []
    assert len(list_snapshots(tmp_path)) == 1


def test_keeping_zero_snapshots_is_refused(tmp_path):
    """`keep=0` would delete the extract behind the build that just ran. If that
    is genuinely wanted it is a deletion, not a retention policy."""
    take_snapshot(tmp_path)
    with pytest.raises(ValueError, match="at least 1"):
        prune_snapshots(tmp_path, keep=0)
    assert len(list_snapshots(tmp_path)) == 1


# --- the build records which extract it consumed -----------------------------

def test_load_run_records_the_extract_the_build_consumed(tmp_path):
    manifest = take_snapshot(tmp_path / "extracts")
    snap = open_snapshot(tmp_path / "extracts", RUN)
    db = tmp_path / "r.sqlite"
    build(db, snap.tables, run_id="build-1", run_at=AT,
          extract_run_id=snap.run_id, extract_digest=snap.digest)

    conn = sqlite3.connect(str(db))
    row = conn.execute('SELECT "extract_run_id", "extract_digest" '
                       'FROM "_load_run"').fetchone()
    conn.close()
    assert row == (RUN, manifest["digest"])
    assert extract_reference(db, "build-1") == (RUN, manifest["digest"])


# --- THE ACCEPTANCE TEST -----------------------------------------------------

def test_a_replayed_build_is_byte_identical_to_the_original(tmp_path):
    """This is the whole item. A build is replayed from its retained extract, with
    no EA anywhere in reach, and the database that comes out is the same file.

    Byte equality rather than a row-count comparison because determinism is
    already a requirement here, so the strongest available check is the honest
    one - and because a reconciliation comparing a rebuild against itself would
    agree about a figure that had quietly changed.

    The replay passes the ORIGINAL `run_id`. A real replay would mint a new one
    and the databases would differ in that one cell by design; holding it fixed is
    what lets the rest of the file be compared byte for byte.
    """
    root = tmp_path / "extracts"
    manifest = take_snapshot(root)

    original = tmp_path / "original.sqlite"
    build(original, open_snapshot(root, RUN).tables, run_id="build-1", run_at=AT,
          extract_run_id=RUN, extract_digest=manifest["digest"])

    # Everything the first build read is now gone except the snapshot.
    snap = replay_snapshot(original, "build-1", root)
    assert isinstance(snap, Snapshot)

    replayed = tmp_path / "replayed.sqlite"
    build(replayed, snap.tables, run_id="build-1", run_at=AT,
          extract_run_id=snap.run_id, extract_digest=snap.digest)

    assert replayed.read_bytes() == original.read_bytes()


def test_the_byte_comparison_can_actually_fail(tmp_path):
    """The acceptance test above asserts two files are equal and passed on its
    first run, which proves it runs and proves nothing about whether it can detect
    a difference. Build from different rows and the same comparison must fail,
    otherwise byte-identity is a check that cannot fail and is worth nothing.

    It has to be a TYPED element that differs. Dropping the untyped one changes
    the extract and its digest but genuinely not the database, because an element
    carrying no stereotype lands in no table - so it would prove the opposite of
    what this test is for.
    """
    root = tmp_path / "extracts"
    take_snapshot(root, run_id="a")
    take_snapshot(root, run_id="b", run_at=AT,
                  tables=dict(TABLES, object=TABLES["object"][1:]))

    first, second = tmp_path / "a.sqlite", tmp_path / "b.sqlite"
    build(first, open_snapshot(root, "a").tables, run_id="build-1", run_at=AT)
    build(second, open_snapshot(root, "b").tables, run_id="build-1", run_at=AT)

    assert second.read_bytes() != first.read_bytes()


def test_a_replay_reproduces_the_snapshot_not_the_current_repository(tmp_path):
    """The property being bought. The repository moves on - another session creates
    and deletes packages while measurements run - and the replay still answers the
    question the original build answered.
    """
    root = tmp_path / "extracts"
    manifest = take_snapshot(root, run_id="old", run_at="2026-10-01 08:00:00")

    original = tmp_path / "original.sqlite"
    build(original, open_snapshot(root, "old").tables, run_id="build-1",
          run_at=AT, extract_run_id="old", extract_digest=manifest["digest"])

    # The model has moved on: an element is gone and another has been added.
    moved_on = dict(TABLES, object=TABLES["object"][1:] + [
        {"Object_ID": 4, "ea_guid": "{D}", "Name": "Scratch Package Content",
         "Object_Type": "Component", "Stereotype": STEREO, "Package_ID": 5}])
    take_snapshot(root, run_id="new", run_at="2026-10-05 08:00:00",
                  tables=moved_on)

    replayed = tmp_path / "replayed.sqlite"
    build(replayed, replay_snapshot(original, "build-1", root).tables,
          run_id="build-1", run_at=AT, extract_run_id="old",
          extract_digest=manifest["digest"])

    assert replayed.read_bytes() == original.read_bytes()
    conn = sqlite3.connect(str(replayed))
    names = {r[0] for r in conn.execute('SELECT "name" FROM "business_application"')}
    conn.close()
    assert names == {"Core Ledger", "Card Switch"}


# --- NEGATIVE: a replay that cannot be trusted must refuse -------------------

def test_a_pruned_extract_is_named_as_pruned(tmp_path):
    """The negative case the item asks for by name: a `load_run` row naming an
    extract that has been pruned must SAY SO, not fail obscurely and not quietly
    rebuild from a different one."""
    root = tmp_path / "extracts"
    manifest = take_snapshot(root, run_id="old", run_at="2026-10-01 08:00:00")
    db = tmp_path / "r.sqlite"
    build(db, open_snapshot(root, "old").tables, run_id="build-1", run_at=AT,
          extract_run_id="old", extract_digest=manifest["digest"])

    take_snapshot(root, run_id="newer", run_at="2026-10-05 08:00:00")
    assert [s["run_id"] for s in prune_snapshots(root, keep=1)] == ["old"]

    with pytest.raises(SnapshotError) as exc:
        replay_snapshot(db, "build-1", root)

    message = str(exc.value)
    assert "'old'" in message
    assert "pruned" in message
    assert "newer" in message, "must say what IS retained"
    assert "cannot be replayed" in message


def test_a_pruned_extract_does_not_fall_back_to_the_snapshot_that_remains(tmp_path):
    """Stated separately from the message test because this is the behaviour that
    actually matters: the one remaining snapshot is a perfectly loadable extract,
    and using it would produce a plausible database answering about the wrong
    moment. Only the asked-for run_id is ever read."""
    root = tmp_path / "extracts"
    manifest = take_snapshot(root, run_id="old", run_at="2026-10-01 08:00:00")
    db = tmp_path / "r.sqlite"
    build(db, open_snapshot(root, "old").tables, run_id="build-1", run_at=AT,
          extract_run_id="old", extract_digest=manifest["digest"])
    take_snapshot(root, run_id="newer", run_at="2026-10-05 08:00:00")
    prune_snapshots(root, keep=1)

    assert list_snapshots(root)[0]["run_id"] == "newer"
    with pytest.raises(SnapshotError):
        replay_snapshot(db, "build-1", root)


def test_a_different_extract_under_the_same_run_id_is_refused(tmp_path):
    """Worse than a missing snapshot: it would reconcile perfectly and still
    answer about the wrong rows."""
    root = tmp_path / "extracts"
    manifest = take_snapshot(root)
    db = tmp_path / "r.sqlite"
    build(db, open_snapshot(root, RUN).tables, run_id="build-1", run_at=AT,
          extract_run_id=RUN, extract_digest=manifest["digest"])

    shutil.rmtree(snapshot_dir(root, RUN))
    take_snapshot(root, tables=dict(TABLES, object=TABLES["object"][:2]))

    with pytest.raises(SnapshotError, match="different extract"):
        replay_snapshot(db, "build-1", root)


def test_a_snapshot_edited_since_it_was_written_is_refused(tmp_path):
    """It is no longer evidence of anything, whoever changed it and why."""
    take_snapshot(tmp_path)
    directory = snapshot_dir(tmp_path, RUN)
    rows = json.loads((directory / "object.json").read_text(encoding="utf-8"))
    rows[0]["Name"] = "Edited By Hand"
    (directory / "object.json").write_text(json.dumps(rows, indent=1),
                                          encoding="utf-8", newline="\n")

    with pytest.raises(SnapshotError, match="its own manifest"):
        open_snapshot(tmp_path, RUN)


def test_a_build_that_recorded_no_extract_says_so(tmp_path):
    """Builds predating retention are in this state. "No extract recorded" and "no
    such run" are different facts and conflating them is how a replay ends up
    reading whatever snapshot is nearest."""
    snap = take_snapshot(tmp_path / "extracts")
    assert snap["run_id"] == RUN
    db = tmp_path / "r.sqlite"
    build(db, open_snapshot(tmp_path / "extracts", RUN).tables,
          run_id="build-1", run_at=AT)

    with pytest.raises(LoadError, match="recorded no extract snapshot"):
        extract_reference(db, "build-1")


def test_a_run_id_that_is_not_in_the_database_is_not_silently_empty(tmp_path):
    manifest = take_snapshot(tmp_path / "extracts")
    db = tmp_path / "r.sqlite"
    build(db, open_snapshot(tmp_path / "extracts", RUN).tables,
          run_id="build-1", run_at=AT, extract_run_id=RUN,
          extract_digest=manifest["digest"])

    with pytest.raises(LoadError, match="no load_run row"):
        extract_reference(db, "build-does-not-exist")
