#!/usr/bin/env python3
"""Tests for extract-snapshot retention, and the replay it exists to make possible.

    python -m pytest _shared/tools/test_snapshot.py -q

These touch the filesystem, because the thing under test is a directory of
files. They touch no repository and no COM object: a replay needs no EA, so a
test of replay must not need one either.

The acceptance test is `test_a_replayed_build_is_byte_identical_to_the_original`.
The rest test what it relies on - a snapshot is retained, identified, and
recorded by the build that used it - and the ways a replay or a prune could go
wrong without saying so.
"""
from __future__ import annotations

import json
import pathlib
import re
import shutil
import sqlite3
import subprocess
import sys
import types

import pytest

import extract as extract_module
from ea_census import build_stereotype_index, census_elements, tag_coverage
from extract import (
    CENSUS_QUERIES,
    INCOMPLETE_PREFIX,
    KEEP_RUNS,
    MANIFEST_NAME,
    SENTINEL_NAME,
    STRUCTURE_QUERIES,
    TABLE_NAMES,
    SUPERSEDED_PREFIX,
    Extractor,
    Snapshot,
    SnapshotError,
    extract,
    list_snapshots,
    main,
    open_snapshot,
    prune_snapshots,
    resolve_scope,
    snapshot_dir,
    snapshot_digest,
    validate_run_id,
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
#: Connector stereotypes, deliberately UNQUALIFIED - no `FQName`, no `WBA::`. The
#: reference technology declares no connector stereotype at all, so a prefixed one
#: would assert something the MDG does not; a bare string on
#: `t_connector.Stereotype` that comes from no MDG is what a real model carries.
#: See `_shared/references/westbrook-example.md` §6, whose observed-counts table
#: these two names come from rather than from an invented vocabulary.
_CONNECTOR_STEREO_USES = "@STEREO;Name=Uses;GUID={02};@ENDSTEREO;"
_CONNECTOR_STEREO_FLOWS = "@STEREO;Name=Flows;GUID={03};@ENDSTEREO;"

#: One snapshot's worth of `t_*` rows, in the shape `extract.py` writes them.
#: Deliberately includes an untyped element, so the census has a remainder to
#: carry and the replayed database has something non-trivial to reproduce.
#:
#: EVERY ONE OF THE TEN TABLES HAS MORE THAN ONE ROW, and for each one its
#: query's `ORDER BY` is the only thing deciding the sequence - which is the
#: property `test_a_dropped_order_by_column_moves_the_digest_for_all_ten_queries`
#: measures and W19 found missing. Five of these tables used to hold a single
#: row, so `reversed()` was a no-op and the determinism test compared a file
#: against itself: the five shipped queries could be given a non-total `ORDER BY`
#: and the suite stayed green at 37 passed.
#:
#: Two of them carry a deliberate TIE on the columns their query sorts by before
#: the tie-break: `xref` has two rows for one `Client`, and `objectproperties`
#: has two `criticality` tags on one element - the exact case `extract.py` singles
#: out, since `t_objectproperties` has no unique index on (Object_ID, Property).
#: Their tie-breaks, `XrefID` and `PropertyID`, are NOT selected by the shipped
#: projections, so the fixture carries them and `_as_the_backend_would_order_them`
#: projects them away after sorting, exactly as a backend does. Without them
#: those two queries could lose their tie-break with nothing noticing.
TABLES = {
    "object": [
        {"Object_ID": 1, "ea_guid": "{A}", "Name": "Core Ledger",
         "Object_Type": "Component", "Stereotype": STEREO, "Package_ID": 5},
        {"Object_ID": 2, "ea_guid": "{B}", "Name": "Card Switch",
         "Object_Type": "Component", "Stereotype": STEREO, "Package_ID": 5},
        {"Object_ID": 3, "ea_guid": "{C}", "Name": "Settlement Notes",
         "Object_Type": "Note", "Stereotype": "", "Package_ID": 5},
    ],
    # Two rows for one Client: a connector's stereotype provenance, which is why
    # `t_connector.ea_guid` is selected at all. `XrefID` is the tie-break and the
    # projection does not select it.
    "xref": [
        {"XrefID": 71, "Client": "{A}", "Description": _STEREO_BLOCK},
        {"XrefID": 72, "Client": "{B}", "Description": _STEREO_BLOCK},
        {"XrefID": 73, "Client": "{R1}", "Description": _CONNECTOR_STEREO_USES},
        {"XrefID": 74, "Client": "{R1}", "Description": _CONNECTOR_STEREO_FLOWS},
    ],
    # Two `criticality` tags on element 1, with different values: no unique index
    # on (Object_ID, Property) and `PropertyID` is the unselected tie-break.
    "objectproperties": [
        {"PropertyID": 61, "Object_ID": 1, "Property": "criticality",
         "Value": "Mission-Critical"},
        {"PropertyID": 62, "Object_ID": 1, "Property": "criticality",
         "Value": "Business-Critical"},
        {"PropertyID": 63, "Object_ID": 1, "Property": "businessOwner",
         "Value": "Payments"},
        {"PropertyID": 64, "Object_ID": 2, "Property": "criticality",
         "Value": "Standard"},
        {"PropertyID": 65, "Object_ID": 2, "Property": "businessOwner",
         "Value": "Lending"},
    ],
    "package": [
        {"Package_ID": 1, "Parent_ID": 0, "Name": "Model"},
        {"Package_ID": 5, "Parent_ID": 1, "Name": "Applications"},
    ],
    "attribute": [
        {"ID": 21, "Object_ID": 1, "Name": "ledgerCode", "Type": "String",
         "Scope": "Public"},
        {"ID": 22, "Object_ID": 1, "Name": "currency", "Type": "String",
         "Scope": "Private"},
    ],
    "operation": [
        {"OperationID": 31, "Object_ID": 1, "Name": "postEntry", "Type": "void",
         "Scope": "Public"},
        {"OperationID": 32, "Object_ID": 1, "Name": "reverseEntry",
         "Type": "void", "Scope": "Public"},
    ],
    "diagram": [
        {"Diagram_ID": 41, "Name": "Payments Landscape",
         "Diagram_Type": "Logical", "Package_ID": 5},
        {"Diagram_ID": 42, "Name": "Settlement Flow",
         "Diagram_Type": "Logical", "Package_ID": 5},
    ],
    "diagramobjects": [
        {"Diagram_ID": 41, "Object_ID": 1},
        {"Diagram_ID": 41, "Object_ID": 2},
        {"Diagram_ID": 42, "Object_ID": 2},
    ],
    "connector": [
        {"Connector_ID": 11, "ea_guid": "{R1}", "Name": "settles via",
         "Connector_Type": "Association", "Stereotype": "Uses",
         "Start_Object_ID": 1, "End_Object_ID": 2},
        {"Connector_ID": 12, "ea_guid": "{R2}", "Name": "clears through",
         "Connector_Type": "Association", "Stereotype": "",
         "Start_Object_ID": 2, "End_Object_ID": 1},
    ],
    "connectortag": [
        {"PropertyID": 51, "ElementID": 11, "Property": "channel", "VALUE": "ACH"},
        {"PropertyID": 52, "ElementID": 11, "Property": "channel",
         "VALUE": "SWIFT"},
        {"PropertyID": 53, "ElementID": 12, "Property": "channel", "VALUE": "ACH"},
    ],
}


class _EchoRepo:
    """Echoes the statement back. The fake rows come from the parser instead,
    which is the seam `Extractor` already has for EA's XML row parser."""

    def SQLQuery(self, sql):          # noqa: N802 - matches EA's COM name
        return sql


_ORDER_BY = re.compile(r"ORDER BY (.+)$", re.IGNORECASE)
_SELECT = re.compile(r"SELECT (.+?) FROM ", re.IGNORECASE)


def _sort_key(v):
    return (v is not None, isinstance(v, str), v)


def _columns(clause):
    """Column names out of a SELECT list or an ORDER BY list, brackets stripped.

    `[Type]`, `[Scope]` and `[VALUE]` are bracketed in the shipped SQL; the rows come
    back under the bare name.
    """
    return [c.strip().strip("[]") for c in clause.split(",")]


def _as_the_backend_would_order_them(rows, sql):
    """Apply the statement's own `ORDER BY` and projection, the way a backend does.

    Without this, any assertion about row order would pass by construction. It
    sorts on every `ORDER BY` column before dropping unselected ones, because
    `t_xref` and `t_objectproperties` break ties on `XrefID` and `PropertyID`,
    which they do not select.
    """
    order = _ORDER_BY.search(sql)
    if order:
        rows = sorted(rows, key=lambda r: tuple(
            _sort_key(r.get(c)) for c in _columns(order.group(1))))
    selected = _columns(_SELECT.search(sql).group(1))
    return [{k: v for k, v in r.items() if k in selected} for r in rows]


def _answering_from(tables):
    """The row-parser half of the fake: a statement in, its rows out.

    Routes on the `FROM t_<name>` in the statement rather than on call order. The
    word boundary matters: `t_object` is a prefix of `t_objectproperties`.
    """
    tables = TABLES if tables is None else tables

    def parse(sql):
        for name, rows in tables.items():
            if re.search(rf"FROM t_{name}\b", sql):
                return _as_the_backend_would_order_them(
                    [dict(r) for r in rows], sql)
        return []

    return parse


def fake_extractor(tables=None):
    """An `Extractor` that answers each query from `tables`."""
    return Extractor(_EchoRepo(), _answering_from(tables))


def take_snapshot(root, run_id=RUN, run_at=AT, tables=None):
    return extract(fake_extractor(tables), root, run_id=run_id, run_at=run_at)


def _ours(directory):
    """Make `directory` and mark it as this tool's, as `extract` does."""
    directory.mkdir(parents=True)
    (directory / SENTINEL_NAME).write_text("", encoding="utf-8")
    return directory


def _ea_is_reachable(patched, tables=None):
    """Put a fake `win32com.client` and row parser into `sys.modules`.

    `main()` imports both and returns 2 if it cannot, so testing what it prints
    needs them present. The repository echoes the statement and the parser answers
    from the fixture, the same seam `fake_extractor` uses.
    """
    answer = _answering_from(tables)
    client = types.ModuleType("win32com.client")
    client.GetActiveObject = lambda _name: types.SimpleNamespace(
        Repository=_EchoRepo())
    win32com = types.ModuleType("win32com")
    win32com.client = client
    server = types.ModuleType("ea_mcp_server.server")
    server._parse_rows_from_sql_xml = answer
    ea_mcp_server = types.ModuleType("ea_mcp_server")
    ea_mcp_server.server = server
    for name, module in (("win32com", win32com), ("win32com.client", client),
                         ("ea_mcp_server", ea_mcp_server),
                         ("ea_mcp_server.server", server)):
        patched.setitem(sys.modules, name, module)


def build(db_path, tables, *, run_id, run_at,
          extract_run_id="", extract_digest=""):
    """The documented build, over extract rows.

    Follows `ea-reporting-database/SKILL.md` rather than taking a shortcut through
    the census dataclasses, because the replay guarantee is a property of that
    pipeline.
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
        *(f"{n}.json" for n in TABLE_NAMES), MANIFEST_NAME, SENTINEL_NAME}
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


def test_a_manifests_sql_log_is_its_own_and_does_not_grow_afterwards(tmp_path):
    """A returned manifest holds a copy of the SQL log, so a later extract through
    the same `Extractor` does not add to it.
    """
    root = tmp_path / "extracts"
    ex = fake_extractor()
    first = extract(ex, root, run_id="r1", run_at="2026-10-01 08:00:00")
    issued = len(first["sql_log"])
    second = extract(ex, root, run_id="r2", run_at="2026-10-02 08:00:00")

    assert issued == 10
    assert len(first["sql_log"]) == 10, "run 1's manifest was edited by run 2"
    assert first["sql_log"] is not second["sql_log"]
    assert first["sql_log"] == json.loads(
        (snapshot_dir(root, "r1") / MANIFEST_NAME).read_text(
            encoding="utf-8"))["sql_log"]


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
    """Two extracts of the same rows hash the same whatever their `run_id` and
    `run_at`: the digest covers the table files only.
    """
    take_snapshot(tmp_path, run_id="a", run_at="2026-10-01 08:00:00")
    take_snapshot(tmp_path, run_id="b", run_at="2026-10-02 08:00:00")
    assert (snapshot_digest(snapshot_dir(tmp_path, "a"))
            == snapshot_digest(snapshot_dir(tmp_path, "b")))


def test_the_digest_does_not_depend_on_the_order_the_backend_returned_rows(tmp_path):
    """The same rows returned in reverse order give the same digest.

    The fixture holds two `criticality` tags on one element and two `t_xref`
    rows for one client, so the comparison covers the tables that need
    tie-breaks.
    """
    take_snapshot(tmp_path, run_id="in-order", run_at="2026-10-01 08:00:00")
    take_snapshot(tmp_path, run_id="reversed", run_at="2026-10-02 08:00:00",
                  tables={name: list(reversed(rows))
                          for name, rows in TABLES.items()})
    assert (snapshot_digest(snapshot_dir(tmp_path, "in-order"))
            == snapshot_digest(snapshot_dir(tmp_path, "reversed")))


def test_every_shipped_query_orders_its_rows():
    """Every table query carries an `ORDER BY`, and so does the one statement
    `resolve_scope` issues.
    """
    for name, sql in {**CENSUS_QUERIES, **STRUCTURE_QUERIES}.items():
        assert "ORDER BY" in sql.upper(), f"{name} has no deterministic order"
    assert len(TABLE_NAMES) == 10

    ex = fake_extractor()
    resolve_scope(ex, 1)
    assert len(ex.sql_log) == 1, "resolve_scope issues exactly one statement"
    for entry in ex.sql_log:
        assert "ORDER BY" in entry["sql"].upper(), (
            f"{entry['label']} has no deterministic order, so the shipped claim "
            f"that every query orders its rows is false for it")


def _with_a_weaker_order(sql):
    """The same statement with the LAST column dropped from its `ORDER BY`.

    The smallest real mistake, and the one a reviewer actually makes: a tie-break
    left off, or a single-column order deleted outright. Either leaves a sequence
    no backend promises.
    """
    match = _ORDER_BY.search(sql)
    kept = _columns(match.group(1))[:-1]
    return (sql[:match.start()] + (f"ORDER BY {', '.join(kept)}" if kept else "")
            ).rstrip()


def test_a_dropped_order_by_column_moves_the_digest_for_all_ten_queries(
        tmp_path, monkeypatch):
    """For each of the ten table queries, dropping the last `ORDER BY` column
    changes the digest, so the equality test above can fail.

    This proves that one mutation class only. Replacing a whole `ORDER BY` with
    a different single column is not always caught: the fixture has no tie on
    `connector.Stereotype` or `attribute.[Scope]`.
    """
    for name in TABLE_NAMES:
        source = CENSUS_QUERIES if name in CENSUS_QUERIES else STRUCTURE_QUERIES
        with monkeypatch.context() as patched:
            patched.setitem(source, name, _with_a_weaker_order(source[name]))
            root = tmp_path / name
            take_snapshot(root, run_id="in-order", run_at="2026-10-01 08:00:00")
            take_snapshot(root, run_id="reversed", run_at="2026-10-02 08:00:00",
                          tables={n: list(reversed(rows))
                                  for n, rows in TABLES.items()})
            assert (snapshot_digest(snapshot_dir(root, "in-order"))
                    != snapshot_digest(snapshot_dir(root, "reversed"))), (
                f"{name}: its ORDER BY could lose a column and nothing here "
                f"would notice, so the determinism claim is unsupported for it")


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
    """`keep=0` would delete every snapshot, including the extract behind the build
    that just ran. If that is genuinely wanted it is a deletion, not a retention
    policy."""
    take_snapshot(tmp_path)
    with pytest.raises(ValueError, match="at least 1"):
        prune_snapshots(tmp_path, keep=0)
    assert len(list_snapshots(tmp_path)) == 1


# --- pruning deletes what it walked, and nothing else ------------------------

def test_pruning_deletes_the_directory_it_walked(tmp_path):
    """Pruning deletes and reports the directory `list_snapshots` walked, never a
    path built from the manifest.
    """
    take_snapshot(tmp_path, run_id="keep", run_at="2026-10-02 08:00:00")
    take_snapshot(tmp_path, run_id="drop", run_at="2026-10-01 08:00:00")

    removed = prune_snapshots(tmp_path, keep=1)
    assert [s["dir"] for s in removed] == [snapshot_dir(tmp_path, "drop")]
    assert [s["status"] for s in removed] == ["pruned"]
    assert not snapshot_dir(tmp_path, "drop").exists()
    assert snapshot_dir(tmp_path, "keep").is_dir()


def test_a_snapshot_restored_under_another_name_is_refused_not_pruned(tmp_path):
    """Two directories whose manifests name one `run_id` make `prune_snapshots`
    raise rather than delete either.
    """
    take_snapshot(tmp_path, run_id="run-archived", run_at="2026-10-01 08:00:00")
    take_snapshot(tmp_path, run_id="run-current", run_at="2026-10-05 08:00:00")
    shutil.copytree(snapshot_dir(tmp_path, "run-archived"),
                    tmp_path / "run-archived-restored")

    with pytest.raises(SnapshotError, match="holds a manifest naming"):
        list_snapshots(tmp_path)
    with pytest.raises(SnapshotError, match="holds a manifest naming"):
        prune_snapshots(tmp_path, keep=1)

    assert snapshot_dir(tmp_path, "run-archived").is_dir(), "nothing was deleted"
    assert snapshot_dir(tmp_path, "run-current").is_dir()
    assert (tmp_path / "run-archived-restored").is_dir()


def test_pruning_cannot_delete_a_directory_outside_the_snapshot_root(tmp_path):
    """A manifest edited to name another path does not make pruning delete that
    path; the manifest is outside the digest.
    """
    root = tmp_path / "extracts"
    outside = tmp_path / "not-a-snapshot-store"
    outside.mkdir()
    (outside / "evidence.txt").write_text("someone else's", encoding="utf-8")

    take_snapshot(root, run_id="keep", run_at="2026-10-02 08:00:00")
    take_snapshot(root, run_id="drop", run_at="2026-10-01 08:00:00")
    manifest_path = snapshot_dir(root, "drop") / MANIFEST_NAME
    man = json.loads(manifest_path.read_text(encoding="utf-8"))
    man["run_id"] = str(outside)
    manifest_path.write_text(json.dumps(man, indent=2), encoding="utf-8",
                             newline="\n")

    with pytest.raises(SnapshotError, match="holds a manifest naming"):
        prune_snapshots(root, keep=1)
    assert (outside / "evidence.txt").is_file(), "deleted outside the root"
    assert snapshot_dir(root, "drop").is_dir()


# --- retention is bounded even when a run dies -------------------------------

def test_an_extract_that_dies_part_way_leaves_nothing_in_the_store(tmp_path):
    """An extract that fails part-way leaves nothing in the store, because the
    snapshot is written under the work prefix and renamed only when complete.
    """
    root = tmp_path / "extracts"
    take_snapshot(root, run_id="good", run_at="2026-10-01 08:00:00")

    def dies_on_the_last_table(sql):
        if re.search(r"FROM t_connectortag\b", sql):
            raise RuntimeError("the run was killed with the connection held")
        for name, rows in TABLES.items():
            if re.search(rf"FROM t_{name}\b", sql):
                return [dict(r) for r in rows]
        return []

    with pytest.raises(RuntimeError):
        extract(Extractor(_EchoRepo(), dies_on_the_last_table), root,
                run_id="killed", run_at="2026-10-02 08:00:00")

    assert not snapshot_dir(root, "killed").exists()
    assert [s["run_id"] for s in list_snapshots(root)] == ["good"]
    assert list(root.iterdir()) == [snapshot_dir(root, "good")]


def test_a_snapshot_that_cannot_be_committed_is_kept_not_discarded(tmp_path):
    """If the rename into place is refused, the finished rows stay under the work
    name and the message says how to keep them.
    """
    root = tmp_path / "extracts"

    def will_not_rename(self, target):
        raise PermissionError(5, "Access is denied")

    with pytest.MonkeyPatch.context() as patched:
        patched.setattr(pathlib.Path, "rename", will_not_rename)
        with pytest.raises(SnapshotError, match="rows are intact"):
            take_snapshot(root, run_id="held")

    assert not snapshot_dir(root, "held").exists()
    debris = root / f"{INCOMPLETE_PREFIX}held"
    assert len(json.loads((debris / "object.json").read_text(encoding="utf-8"))) == 3
    assert list_snapshots(root) == [], "and it is not a snapshot until renamed"


def test_a_run_id_that_collides_only_in_case_is_refused(tmp_path):
    """A `run_id` differing only in case from one in the store is refused before
    anything is written; the filesystem would not tell the two apart.
    """
    root = tmp_path / "extracts"
    first = take_snapshot(root, run_id="Run-A", run_at="2026-10-01 08:00:00")

    with pytest.raises(SnapshotError, match="differs only in case"):
        take_snapshot(root, run_id="run-a", run_at="2026-10-02 08:00:00",
                      tables=dict(TABLES, object=TABLES["object"][:1]))

    assert [p.name for p in root.iterdir()] == ["Run-A"], "refused before writing"
    assert [s["run_id"] for s in list_snapshots(root)] == ["Run-A"]
    assert len(open_snapshot(root, "Run-A",
                             expect_digest=first["digest"]).tables["object"]) == 3

    # Re-running the SAME run_id is still what the module documents it to be.
    take_snapshot(root, run_id="Run-A", run_at="2026-10-03 08:00:00",
                  tables=dict(TABLES, object=TABLES["object"][:1]))
    assert len(open_snapshot(root, "Run-A").tables["object"]) == 1


def test_a_rerun_that_cannot_replace_a_snapshot_leaves_the_retained_one_whole(
        tmp_path):
    """A re-run whose snapshot cannot be moved aside raises `SnapshotError`, and
    the retained snapshot is whole, listed, and verifies against its digest.
    """
    root = tmp_path / "extracts"
    first = take_snapshot(root, run_id="r1", run_at="2026-10-01 08:00:00")

    with open(snapshot_dir(root, "r1") / "object.json", encoding="utf-8"):
        with pytest.raises(SnapshotError, match="could not be moved aside"):
            take_snapshot(root, run_id="r1", run_at="2026-10-02 08:00:00",
                          tables=dict(TABLES, object=TABLES["object"][:1]))

    reopened = open_snapshot(root, "r1", expect_digest=first["digest"])
    assert len(reopened.tables["object"]) == 3, "the retained rows are all there"
    assert reopened.run_at == "2026-10-01 08:00:00"
    assert [s["run_id"] for s in list_snapshots(root)] == ["r1"]

    # And the new rows were kept, not discarded: they cost a COM extract.
    debris = root / f"{INCOMPLETE_PREFIX}r1"
    assert len(json.loads(
        (debris / "object.json").read_text(encoding="utf-8"))) == 1
    assert [(s["run_id"], s["status"]) for s in
            prune_snapshots(root, keep=KEEP_RUNS, protect=("r1",))] == [
        (debris.name, "incomplete")]


def test_a_replacement_that_fails_mid_commit_puts_the_old_snapshot_back(tmp_path):
    """When the commit rename is refused after the move-aside, the old snapshot is
    put back under its own name and the new rows are kept.
    """
    root = tmp_path / "extracts"
    first = take_snapshot(root, run_id="r1", run_at="2026-10-01 08:00:00")
    real_rename = pathlib.Path.rename

    def refuse_only_the_commit(self, target):
        if self.name.startswith(INCOMPLETE_PREFIX):
            raise PermissionError(5, "Access is denied")
        return real_rename(self, target)

    with pytest.MonkeyPatch.context() as patched:
        patched.setattr(pathlib.Path, "rename", refuse_only_the_commit)
        with pytest.raises(SnapshotError, match="rows are intact"):
            take_snapshot(root, run_id="r1", run_at="2026-10-02 08:00:00",
                          tables=dict(TABLES, object=TABLES["object"][:1]))

    assert len(open_snapshot(root, "r1",
                             expect_digest=first["digest"]).tables["object"]) == 3
    assert [s["run_id"] for s in list_snapshots(root)] == ["r1"]
    assert not (root / f"{SUPERSEDED_PREFIX}r1").exists(), "the aside went back"
    assert len(json.loads(
        (root / f"{INCOMPLETE_PREFIX}r1" / "object.json").read_text(
            encoding="utf-8"))) == 1


def _refuse_the_commit_and_the_putback(root, run_id):
    """Refuse both the commit rename and the putback of the aside.

    The one failure that leaves nothing under the `run_id`.
    """
    real_rename = pathlib.Path.rename
    out_dir = snapshot_dir(root, run_id)
    aside = root / f"{SUPERSEDED_PREFIX}{run_id}"

    def refuse(self, target):
        target = pathlib.Path(target)
        if target == out_dir and (self.name.startswith(INCOMPLETE_PREFIX)
                                  or self == aside):
            raise PermissionError(5, "Access is denied")
        return real_rename(self, target)

    return refuse


def test_a_failed_putback_says_both_sets_of_rows_will_be_pruned(tmp_path):
    """When the putback fails too, the message says both sets of rows are on disk
    and that the next prune reclaims both.
    """
    root = tmp_path / "extracts"
    first = take_snapshot(root, run_id="r1", run_at="2026-10-01 08:00:00")

    with pytest.MonkeyPatch.context() as patched:
        patched.setattr(pathlib.Path, "rename",
                        _refuse_the_commit_and_the_putback(root, "r1"))
        with pytest.raises(SnapshotError) as refusal:
            take_snapshot(root, run_id="r1", run_at="2026-10-02 08:00:00",
                          tables=dict(TABLES, object=TABLES["object"][:1]))

    message = str(refusal.value)
    assert sorted(p.name for p in root.iterdir()) == [
        f"{INCOMPLETE_PREFIX}r1", f"{SUPERSEDED_PREFIX}r1"]
    assert list_snapshots(root) == [], "nothing is retained under r1"
    assert "BOTH sets of rows are on disk" in message, "the true part, kept"
    assert "BEFORE THE NEXT PRUNE" in message, (
        "the operator is told to keep a directory that the next prune deletes")
    assert "reclaim BOTH" in message

    # The rows really are both there and really are both reclaimed, so the
    # disclosure is about this store and not a sentence added for the test.
    assert snapshot_digest(root / f"{SUPERSEDED_PREFIX}r1") == first["digest"]
    removed = prune_snapshots(root, keep=KEEP_RUNS)
    assert sorted((s["run_id"], s["status"]) for s in removed) == [
        (f"{INCOMPLETE_PREFIX}r1", "incomplete"),
        (f"{SUPERSEDED_PREFIX}r1", "superseded")]
    assert list(root.iterdir()) == []


def test_rows_moved_aside_are_not_reported_as_pruned_or_never_kept(tmp_path):
    """In that state `open_snapshot` says where the rows are, not that the snapshot
    was pruned or never kept.
    """
    root = tmp_path / "extracts"
    first = take_snapshot(root, run_id="r1", run_at="2026-10-01 08:00:00")
    with pytest.MonkeyPatch.context() as patched:
        patched.setattr(pathlib.Path, "rename",
                        _refuse_the_commit_and_the_putback(root, "r1"))
        with pytest.raises(SnapshotError):
            take_snapshot(root, run_id="r1", run_at="2026-10-02 08:00:00")

    with pytest.raises(SnapshotError) as refusal:
        open_snapshot(root, "r1", expect_digest=first["digest"])
    message = str(refusal.value)
    assert "has been pruned, or was never kept" not in message
    assert f"{SUPERSEDED_PREFIX}r1" in message and f"{INCOMPLETE_PREFIX}r1" in message
    assert "its rows are" in message
    assert "Nothing has been deleted" in message

    # And the rename the message names does recover the build's own evidence.
    (root / f"{SUPERSEDED_PREFIX}r1").rename(snapshot_dir(root, "r1"))
    assert open_snapshot(root, "r1", expect_digest=first["digest"]).run_id == "r1"

    # A genuinely pruned snapshot still gets the pruned message, so the new branch
    # did not simply replace one wrong answer with another.
    shutil.rmtree(snapshot_dir(root, "r1"))
    shutil.rmtree(root / f"{INCOMPLETE_PREFIX}r1")
    take_snapshot(root, run_id="other", run_at="2026-10-03 08:00:00")
    with pytest.raises(SnapshotError, match="has been pruned, or was never kept"):
        open_snapshot(root, "r1")


def test_a_case_collision_against_rows_moved_aside_is_refused_too(tmp_path):
    """The case-collision refusal also covers prefixed directories, and names the
    `run_id` to pass rather than the prefixed name.
    """
    root = tmp_path / "extracts"
    first = take_snapshot(root, run_id="Run-A", run_at="2026-10-01 08:00:00")
    with pytest.MonkeyPatch.context() as patched:
        patched.setattr(pathlib.Path, "rename",
                        _refuse_the_commit_and_the_putback(root, "Run-A"))
        with pytest.raises(SnapshotError):
            take_snapshot(root, run_id="Run-A", run_at="2026-10-02 08:00:00")
    assert sorted(p.name for p in root.iterdir()) == [
        f"{INCOMPLETE_PREFIX}Run-A", f"{SUPERSEDED_PREFIX}Run-A"]

    with pytest.raises(SnapshotError, match="differs only in case") as refusal:
        take_snapshot(root, run_id="run-a", run_at="2026-10-03 08:00:00")
    assert "Pass 'Run-A'" in str(refusal.value), (
        "the prefixed name is not a run_id and cannot be passed to anything")

    assert sorted(p.name for p in root.iterdir()) == [
        f"{INCOMPLETE_PREFIX}Run-A", f"{SUPERSEDED_PREFIX}Run-A"], "nothing went"
    assert snapshot_digest(root / f"{SUPERSEDED_PREFIX}Run-A") == first["digest"]

    # The reverse direction, and from a plain retained snapshot, both still hold.
    (root / f"{SUPERSEDED_PREFIX}Run-A").rename(snapshot_dir(root, "Run-A"))
    with pytest.raises(SnapshotError, match="differs only in case"):
        take_snapshot(root, run_id="RUN-A", run_at="2026-10-03 08:00:00")
    # And re-running the same run_id is still the one way to replace a snapshot.
    assert take_snapshot(root, run_id="Run-A", run_at="2026-10-04 08:00:00")[
        "run_at"] == "2026-10-04 08:00:00"


def test_the_debris_of_a_killed_run_is_not_a_snapshot_and_is_swept(tmp_path):
    """A work directory a killed run left is not listed, cannot be opened, and is
    swept and reported as `incomplete`.
    """
    root = tmp_path / "extracts"
    take_snapshot(root, run_id="good", run_at="2026-10-01 08:00:00")
    debris = _ours(root / f"{INCOMPLETE_PREFIX}killed")
    (debris / "object.json").write_text("[]", encoding="utf-8")

    assert [s["run_id"] for s in list_snapshots(root)] == ["good"]
    with pytest.raises(SnapshotError, match="not usable as a snapshot name"):
        open_snapshot(root, debris.name)

    removed = prune_snapshots(root, keep=KEEP_RUNS)
    assert [(s["run_id"], s["status"]) for s in removed] == [
        (debris.name, "incomplete")]
    assert removed[0]["bytes"] > 0, "the report has to carry what it reclaimed"
    assert not debris.exists()
    assert [s["run_id"] for s in list_snapshots(root)] == ["good"]


def test_a_plain_named_directory_that_is_not_a_snapshot_is_swept_too(tmp_path):
    """A plain-named directory this tool wrote, with no manifest, is swept and
    reported as `unreadable`, with its size.
    """
    root = tmp_path / "extracts"
    take_snapshot(root, run_id="good", run_at="2026-10-01 08:00:00")
    for name in ("legacy-1", "legacy-2"):
        husk = _ours(root / name)
        (husk / "object.json").write_text(
            json.dumps(TABLES["object"], indent=1), encoding="utf-8")

    removed = prune_snapshots(root, keep=KEEP_RUNS)
    assert [(s["run_id"], s["status"]) for s in removed] == [
        ("legacy-1", "unreadable"), ("legacy-2", "unreadable")]
    assert all(s["bytes"] > 0 for s in removed), "report what it reclaimed"
    assert [p.name for p in root.iterdir()] == ["good"]
    assert [s["run_id"] for s in list_snapshots(root)] == ["good"]


def test_an_unrelated_directory_in_the_store_root_is_not_touched_by_a_prune(
        tmp_path, capsys):
    """Directories this tool did not write survive a run through `main()`, `.git`
    included, and nothing about them is reported.
    """
    root = tmp_path / "an-operator-typed-this"
    root.mkdir()
    for name in (".git", "docs", "extracts", "research", "src"):
        (root / name).mkdir()
        (root / name / "payload.txt").write_text("x" * 100, encoding="utf-8")
    (root / ".git" / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")
    (root / "README.md").write_text("not a directory, and never was at risk",
                                    encoding="utf-8")
    before = sorted(p.name for p in root.iterdir())

    with pytest.MonkeyPatch.context() as patched:
        _ea_is_reachable(patched)
        code = main(["--out", str(root), "--run-id", "x",
                     "--run-at", "2026-10-05 08:00:00"])

    assert code == 0, "the run succeeded, which is exactly why this was dangerous"
    assert sorted(p.name for p in root.iterdir()) == sorted(before + ["x"]), (
        "a prune reclaimed directories in the store root that this tool never "
        "wrote and cannot identify as its own")
    assert (root / ".git" / "HEAD").read_text(encoding="utf-8") == (
        "ref: refs/heads/main")
    assert "SWEPT" not in capsys.readouterr().out, (
        "nothing was swept, so nothing may be reported as swept")

    # And the function on its own, so the property is not only true via the CLI.
    assert prune_snapshots(root, keep=KEEP_RUNS, protect=("x",)) == []
    assert sorted(p.name for p in root.iterdir()) == sorted(before + ["x"])


def test_the_sweep_still_takes_both_debris_shapes_beside_an_untouched_directory(
        tmp_path):
    """Prefixed and plain-named debris are swept in one prune, while a directory
    without the marker and a snapshot nested one level down are left alone.
    """
    root = tmp_path / "extracts"
    take_snapshot(root, run_id="good", run_at="2026-10-01 08:00:00")

    killed = _ours(root / f"{INCOMPLETE_PREFIX}killed")
    (killed / "object.json").write_text("[]", encoding="utf-8")
    husk = _ours(root / "legacy-1")
    (husk / "object.json").write_text(json.dumps(TABLES["object"], indent=1),
                                      encoding="utf-8")
    (root / "docs").mkdir()
    (root / "docs" / "notes.md").write_text("mine, not yours", encoding="utf-8")
    archive = root / "archive-2026-09"
    archive.mkdir()
    shutil.copytree(snapshot_dir(root, "good"), archive / "inner")
    replayable = snapshot_digest(archive / "inner")

    removed = prune_snapshots(root, keep=KEEP_RUNS)

    assert [(s["run_id"], s["status"]) for s in removed] == [
        (f"{INCOMPLETE_PREFIX}killed", "incomplete"), ("legacy-1", "unreadable")]
    assert all(s["bytes"] > 0 for s in removed), "report what it reclaimed"
    assert sorted(p.name for p in root.iterdir()) == [
        "archive-2026-09", "docs", "good"]
    assert snapshot_digest(archive / "inner") == replayable, (
        "a loadable snapshot nested under a plain name was destroyed and reported "
        "as 0 KiB of something nothing could be replayed from")


def test_a_directory_junction_in_the_store_root_is_left_alone(tmp_path):
    """A junction is never swept, even when its target looks like this tool's from
    inside, and it does not make `main()` exit 1.
    """
    root = tmp_path / "extracts"
    take_snapshot(root, run_id="good", run_at="2026-10-01 08:00:00")
    target = tmp_path / "somewhere-else"
    target.mkdir()
    (target / "precious.txt").write_text("not retention's to delete",
                                         encoding="utf-8")
    (target / "object.json").write_text("[]", encoding="utf-8")
    (target / SENTINEL_NAME).write_text("", encoding="utf-8")
    made = subprocess.run(["cmd", "/c", "mklink", "/J",
                           str(root / "shortcut"), str(target)],
                          capture_output=True, text=True)
    if made.returncode != 0:
        pytest.skip(f"no directory junction available here: "
                    f"{made.stderr.strip() or made.stdout.strip()}")

    assert prune_snapshots(root, keep=KEEP_RUNS) == [], (
        "a junction was reported as debris retention meant to remove")
    assert (root / "shortcut").is_dir()
    assert (target / "precious.txt").is_file()

    with pytest.MonkeyPatch.context() as patched:
        _ea_is_reachable(patched)
        assert main(["--out", str(root), "--run-id", "fresh",
                     "--run-at", "2026-10-05 08:00:00"]) == 0, (
            "a junction in the root used to make every run return 1 for ever")


def test_a_swept_directorys_size_is_counted_all_the_way_down(tmp_path):
    """A swept directory's reported size includes its subdirectories."""
    root = tmp_path / "extracts"
    take_snapshot(root, run_id="good", run_at="2026-10-01 08:00:00")
    debris = _ours(root / f"{INCOMPLETE_PREFIX}killed")
    (debris / "nested").mkdir()
    (debris / "object.json").write_text("[]", encoding="utf-8")
    (debris / "nested" / "rows.json").write_text("y" * 4000, encoding="utf-8")
    real = sum(f.stat().st_size for f in debris.rglob("*") if f.is_file())

    removed = prune_snapshots(root, keep=KEEP_RUNS)
    assert [s["bytes"] for s in removed] == [real]
    assert real > 4000, "the fixture has to have more below the top level than in it"


def test_the_swept_report_claims_no_cause_it_did_not_check(tmp_path):
    """Every swept status has a sentence, and none asserts a held file or that
    nothing could be replayed, which the sweep does not check.
    """
    reasons = extract_module._SWEPT_REASON
    assert set(reasons) == {"incomplete", "superseded", "unreadable"}
    for status, reason in reasons.items():
        assert "held" not in reason, (
            f"{status} asserts a held file as the cause; nothing checked for one")
        assert "replay" not in reason, (
            f"{status} asserts nothing could be replayed from it; the sweep never "
            f"looked, and a superseded aside is a full set of rows")
    assert "replaced" not in reasons["superseded"], (
        "a superseded aside is the only copy on the putback-failure path")

    root = tmp_path / "extracts"
    take_snapshot(root, run_id="good", run_at="2026-10-01 08:00:00")
    husk = _ours(root / "legacy-1")
    (husk / "object.json").write_text("[]", encoding="utf-8")
    assert [s["status"] for s in prune_snapshots(root, keep=KEEP_RUNS)] == [
        "unreadable"], "and the keying is live, not just a constant"


def test_a_prune_stopped_by_a_held_file_is_reported_not_raised(tmp_path):
    """A prune refused by a held file reports `held` instead of raising. The husk
    keeps its marker, so the next prune sweeps it.
    """
    root = tmp_path / "extracts"
    take_snapshot(root, run_id="keep", run_at="2026-10-02 08:00:00")
    take_snapshot(root, run_id="drop", run_at="2026-10-01 08:00:00")

    with open(snapshot_dir(root, "drop") / "object.json", encoding="utf-8"):
        removed = prune_snapshots(root, keep=1)
        assert [(s["run_id"], s["status"]) for s in removed] == [("drop", "held")]
        assert snapshot_dir(root, "drop").exists(), "held means still there"
        assert (snapshot_dir(root, "drop") / SENTINEL_NAME).is_file(), (
            "the marker is deleted last, so a refused delete keeps it")

    assert [(s["run_id"], s["status"]) for s in prune_snapshots(root, keep=1)] == [
        ("drop", "unreadable")]
    assert [p.name for p in root.iterdir()] == ["keep"]


def test_a_held_prune_target_can_be_gutted_and_held_does_not_deny_it(
        tmp_path, capsys):
    """A refused delete can leave a snapshot that is still listed but no longer
    loadable.

    `main()` says so in its `held` message rather than implying the directory is
    intact, and the next prune removes it.
    """
    root = tmp_path / "extracts"
    take_snapshot(root, run_id="keep", run_at="2026-10-02 08:00:00")
    take_snapshot(root, run_id="drop", run_at="2026-10-01 08:00:00")
    target = snapshot_dir(root, "drop")
    assert sorted(p.name for p in target.iterdir())[0] < MANIFEST_NAME, (
        "connector.json has to sort before the manifest or this tests nothing")

    with open(target / "connector.json", encoding="utf-8"):
        removed = prune_snapshots(root, keep=1)
        assert [(s["run_id"], s["status"]) for s in removed] == [("drop", "held")]
        # The gutting: the manifest outlived files that sorted ahead of it, so the
        # directory is still a listed snapshot and still occupies a retention slot.
        assert (target / MANIFEST_NAME).is_file()
        assert not (target / "attribute.json").exists()
        assert [s["run_id"] for s in list_snapshots(root)] == ["keep", "drop"]

    with pytest.MonkeyPatch.context() as patched:
        _ea_is_reachable(patched)
        with open(snapshot_dir(root, "drop") / "connector.json", encoding="utf-8"):
            code = main(["--out", str(root), "--run-id", "fresh", "--keep", "1",
                         "--run-at", "2026-10-05 08:00:00"])
    assert code == 1, "main() reports a directory it could not fully remove"
    held_block = capsys.readouterr().err
    assert "COULD NOT BE FULLY REMOVED" in held_block
    assert "may no longer be loadable" in held_block, (
        "`held` read as a promise the directory is intact, and it is not")

    # The next prune does reclaim it, so the store is not permanently over bound.
    assert [s["status"] for s in prune_snapshots(root, keep=1, protect=("fresh",))
            if s["run_id"] == "drop"] == ["pruned"]
    assert not snapshot_dir(root, "drop").exists()


def test_a_manifest_that_does_not_parse_does_not_stop_the_whole_store(tmp_path):
    """A manifest that is truncated, not an object, missing `run_at` or with a
    null `run_at` makes its directory unreadable debris rather than stopping
    the store. A manifest naming a different `run_id` still raises.
    """
    for label, body in (("truncated", '{"run_id": "legacy-1", "run_a'),
                        ("not an object", "[]"),
                        ("no run_at", '{"run_id": "legacy-1"}'),
                        ("null run_at",
                         '{"run_id": "legacy-1", "run_at": null}')):
        root = tmp_path / label
        take_snapshot(root, run_id="good", run_at="2026-10-01 08:00:00")
        bad = _ours(root / "legacy-1")
        (bad / MANIFEST_NAME).write_text(body, encoding="utf-8")
        (bad / "object.json").write_text("[]", encoding="utf-8")

        assert [s["run_id"] for s in list_snapshots(root)] == ["good"], label
        removed = prune_snapshots(root, keep=KEEP_RUNS)
        assert [(s["run_id"], s["status"]) for s in removed] == [
            ("legacy-1", "unreadable")], label
        assert [p.name for p in root.iterdir()] == ["good"], label

        with pytest.MonkeyPatch.context() as patched:
            _ea_is_reachable(patched)
            assert main(["--out", str(root), "--run-id", "fresh",
                         "--run-at", "2026-10-05 08:00:00"]) == 0, label

    # And the DELIBERATE refusal is not folded in with them: a manifest that parses
    # and names a different run_id is a real disagreement about which evidence is
    # meant, and is still loud.
    root = tmp_path / "two-names"
    take_snapshot(root, run_id="archived", run_at="2026-10-01 08:00:00")
    shutil.copytree(snapshot_dir(root, "archived"), root / "archived-restored")
    with pytest.raises(SnapshotError, match="holds a manifest naming"):
        list_snapshots(root)


def test_a_snapshot_under_another_name_is_refused_not_opened_under_the_manifests(
        tmp_path):
    """`open_snapshot` refuses a directory whose manifest names another `run_id`,
    as `list_snapshots` does.
    """
    root = tmp_path / "extracts"
    original = take_snapshot(root, run_id="run-archived", run_at="2026-10-01 08:00:00")
    shutil.copytree(snapshot_dir(root, "run-archived"), root / "run-archived-restored")

    with pytest.raises(SnapshotError, match="holds a manifest naming") as refusal:
        open_snapshot(root, "run-archived-restored")
    assert "'run-archived'" in str(refusal.value), "it names both"

    # Even with the right digest in hand, because the identity is the point: the
    # two directories hash the same, so the digest check could never catch this.
    assert snapshot_digest(root / "run-archived-restored") == original["digest"]
    with pytest.raises(SnapshotError, match="holds a manifest naming"):
        open_snapshot(root, "run-archived-restored",
                      expect_digest=original["digest"])

    # The snapshot under its own name is untouched by the new check.
    assert open_snapshot(root, "run-archived",
                         expect_digest=original["digest"]).run_id == "run-archived"


def test_main_prints_the_reference_before_it_prunes(tmp_path, capsys):
    """`main()` prints the run_id and digest before retention runs, and a
    retention failure elsewhere in the store exits 1 with the snapshot on disk.
    """
    root = tmp_path / "extracts"
    take_snapshot(root, run_id="archived", run_at="2026-10-01 08:00:00")
    shutil.copytree(snapshot_dir(root, "archived"), root / "archived-restored")

    with pytest.MonkeyPatch.context() as patched:
        _ea_is_reachable(patched)
        code = main(["--out", str(root), "--run-id", "fresh",
                     "--run-at", "2026-10-05 08:00:00"])

    printed = capsys.readouterr()
    assert "snapshot fresh retained at" in printed.out
    assert f"digest {open_snapshot(root, 'fresh').digest}" in printed.out
    assert "retention did not run" in printed.err
    assert "holds a manifest naming" in printed.err, "and says what is wrong"
    assert code == 1
    assert open_snapshot(root, "fresh").manifest["counts"]["object"] == 3


def test_main_exits_zero_and_reports_the_snapshots_it_pruned(tmp_path, capsys):
    """An ordinary run that prunes exits 0 and prints the retention line and the
    PRUNED block.
    """
    root = tmp_path / "extracts"
    for day in (1, 2, 3):
        take_snapshot(root, run_id=f"old-{day}", run_at=f"2026-10-0{day} 08:00:00")

    with pytest.MonkeyPatch.context() as patched:
        _ea_is_reachable(patched)
        code = main(["--out", str(root), "--run-id", "fresh", "--keep", "2",
                     "--run-at", "2026-10-05 08:00:00"])

    printed = capsys.readouterr()
    assert code == 0, printed.err
    assert "snapshot fresh retained at" in printed.out
    assert "retention: 2 snapshot(s) kept, limit 2" in printed.out
    assert "PRUNED 2 snapshot(s)" in printed.out
    assert "can no longer be reproduced from its own rows" in printed.out
    assert "old-1  taken 2026-10-01 08:00:00" in printed.out
    assert "old-2  taken 2026-10-02 08:00:00" in printed.out
    assert [s["run_id"] for s in list_snapshots(root)] == ["fresh", "old-3"]
    assert open_snapshot(root, "fresh").manifest["counts"]["object"] == 3


def test_main_reports_a_superseded_sweep_the_shipped_table_documents(
        tmp_path, capsys):
    """A re-run's aside that could not be deleted at the time is swept by the next
    run and reported as `superseded`.
    """
    root = tmp_path / "extracts"
    take_snapshot(root, run_id="r1", run_at="2026-10-01 08:00:00")
    real_reclaim = extract_module._reclaim

    with pytest.MonkeyPatch.context() as patched:
        patched.setattr(extract_module, "_reclaim",
                        lambda d: False if pathlib.Path(d).name.startswith(
                            SUPERSEDED_PREFIX) else real_reclaim(d))
        take_snapshot(root, run_id="r1", run_at="2026-10-02 08:00:00")

    assert (root / f"{SUPERSEDED_PREFIX}r1").is_dir(), "the aside stayed behind"
    assert [s["run_id"] for s in list_snapshots(root)] == ["r1"], (
        "and the commit still succeeded, which is why it is not a failure"
    )

    with pytest.MonkeyPatch.context() as patched:
        _ea_is_reachable(patched)
        code = main(["--out", str(root), "--run-id", "fresh",
                     "--run-at", "2026-10-05 08:00:00"])

    printed = capsys.readouterr()
    assert code == 0, printed.err
    assert f"SWEPT {SUPERSEDED_PREFIX}r1" in printed.out
    assert "renamed aside under this tool's replacement prefix" in printed.out
    assert "replaced" not in printed.out, (
        "on the putback-failure path it is the only copy and nothing replaced it")
    assert "could be replayed" not in printed.out, (
        "an aside is a full set of rows; the sweep never looked, so it may not "
        "tell the operator nothing could have been replayed from what it deleted")
    assert not (root / f"{SUPERSEDED_PREFIX}r1").exists()


def test_a_refused_snapshot_write_exits_two_not_the_code_that_promises_a_digest(
        tmp_path, capsys):
    """A refused snapshot write exits 2, prints no digest, and leaves the store as
    it was. Exit 1 would mean a snapshot was retained.
    """
    root = tmp_path / "extracts"
    take_snapshot(root, run_id="already-here", run_at="2026-10-01 08:00:00")
    real_write = pathlib.Path.write_text
    written = []

    def refuse_the_sixth_table_file(self, *args, **kwargs):
        if self.suffix == ".json":
            written.append(self.name)
            if len(written) == 6:
                raise PermissionError(5, "Access is denied")
        return real_write(self, *args, **kwargs)

    with pytest.MonkeyPatch.context() as patched:
        _ea_is_reachable(patched)
        patched.setattr(pathlib.Path, "write_text", refuse_the_sixth_table_file)
        code = main(["--out", str(root), "--run-id", "r2",
                     "--run-at", "2026-10-05 08:00:00"])

    printed = capsys.readouterr()
    assert code == 2, "exit 1 promises a retained snapshot and a printed digest"
    assert "digest" not in printed.out, "and there is no digest to print"
    assert "the extract did not complete" in printed.err
    assert "Nothing was retained" in printed.err

    # The store is as it was: the work directory is cleared and the snapshot that
    # was already retained is untouched and still replayable.
    assert [p.name for p in root.iterdir()] == ["already-here"]
    assert open_snapshot(root, "already-here").manifest["counts"]["object"] == 3


def test_a_directory_this_tool_did_not_write_is_never_swept_whatever_it_holds(
        tmp_path, capsys):
    """A table-file name is not evidence of ownership; `package.json` is one.
    Only the marker `extract` writes is."""
    root = tmp_path / "a-project"
    for name in ("frontend", "server"):
        (root / name / "src").mkdir(parents=True)
        (root / name / "package.json").write_text("{}", encoding="utf-8")
        (root / name / "src" / "a.ts").write_text("x", encoding="utf-8")

    with pytest.MonkeyPatch.context() as patched:
        _ea_is_reachable(patched)
        code = main(["--out", str(root), "--run-id", "x",
                     "--run-at", "2026-10-05 08:00:00"])

    assert code == 0
    assert sorted(p.name for p in root.iterdir()) == ["frontend", "server", "x"]
    assert (root / "frontend" / "src" / "a.ts").is_file()
    assert "SWEPT" not in capsys.readouterr().out


def test_a_copied_snapshot_under_an_unusable_name_is_left_alone(tmp_path):
    """A snapshot copied by Explorer keeps its marker and its manifest
    under a name that is not a valid run_id. It has a loadable manifest, so it is
    not swept."""
    root = tmp_path / "extracts"
    take_snapshot(root, run_id="good", run_at="2026-10-01 08:00:00")
    copy = root / "good - Copy"
    shutil.copytree(snapshot_dir(root, "good"), copy)
    digest = snapshot_digest(copy)

    assert prune_snapshots(root, keep=KEEP_RUNS) == []
    assert snapshot_digest(copy) == digest


def test_an_empty_work_directory_is_swept(tmp_path):
    """A run killed between creating its work directory and writing the marker
    leaves an empty prefixed directory, which is swept."""
    root = tmp_path / "extracts"
    take_snapshot(root, run_id="good", run_at="2026-10-01 08:00:00")
    (root / f"{INCOMPLETE_PREFIX}killed").mkdir()

    removed = prune_snapshots(root, keep=KEEP_RUNS)
    assert [(s["run_id"], s["status"]) for s in removed] == [
        (f"{INCOMPLETE_PREFIX}killed", "incomplete")]
    assert [p.name for p in root.iterdir()] == ["good"]


def test_an_extract_failure_that_is_not_an_os_error_exits_two(tmp_path, capsys):
    """A COM, parse or serialization failure inside `extract()` is a
    reportable outcome, not a traceback, and nothing is retained."""
    root = tmp_path / "extracts"
    take_snapshot(root, run_id="already-here", run_at="2026-10-01 08:00:00")

    def fail(*_args, **_kwargs):
        raise RuntimeError("the row parser could not read the response")

    with pytest.MonkeyPatch.context() as patched:
        _ea_is_reachable(patched)
        patched.setattr(extract_module, "_extract_into", fail)
        code = main(["--out", str(root), "--run-id", "r2",
                     "--run-at", "2026-10-05 08:00:00"])

    printed = capsys.readouterr()
    assert code == 2
    assert "RuntimeError" in printed.err
    assert "Nothing was retained" in printed.err
    assert [p.name for p in root.iterdir()] == ["already-here"]


# --- a run never deletes the snapshot it has just reported as retained -------

def test_the_run_just_written_is_never_pruned(tmp_path):
    """A run whose `run_at` sorts oldest is not pruned by its own invocation."""
    root = tmp_path / "extracts"
    for day in range(1, 11):
        take_snapshot(root, run_id=f"run-{day:02d}",
                      run_at=f"2026-10-{day:02d} 08:00:00")
    take_snapshot(root, run_id="backfill", run_at="2026-09-01 08:00:00")

    assert prune_snapshots(root, keep=KEEP_RUNS, protect=("backfill",)) == []
    assert open_snapshot(root, "backfill").run_id == "backfill"

    # And the sort really does put it last: unprotected, it is the one that goes.
    assert [s["run_id"] for s in prune_snapshots(root, keep=KEEP_RUNS)] == ["backfill"]


def test_protect_as_a_bare_string_is_refused_not_read_as_its_characters(tmp_path):
    """`protect` given a bare string is refused rather than iterated into its
    characters.
    """
    root = tmp_path / "extracts"
    for day in (1, 2):
        take_snapshot(root, run_id=f"run-{day:02d}",
                      run_at=f"2026-10-{day:02d} 08:00:00")
    take_snapshot(root, run_id="backfill", run_at="2026-09-01 08:00:00")

    with pytest.raises(ValueError, match="not the string"):
        prune_snapshots(root, keep=2, protect="backfill")
    assert snapshot_dir(root, "backfill").is_dir(), "nothing was deleted"

    assert prune_snapshots(root, keep=2, protect=("backfill",)) == []
    assert [s["run_id"] for s in prune_snapshots(root, keep=2)] == ["backfill"]


def test_a_run_at_the_sort_cannot_order_is_refused(tmp_path):
    """A `run_at` not in the one sortable format is refused before any query."""
    for bad in ("2026-10-05T08:00:00", "05/10/2026", "2026-10-5 8:00:00",
                "2026-10-05", "2026-10-05 08:00", "", "yesterday"):
        with pytest.raises(ValueError, match="YYYY-MM-DD HH:MM:SS"):
            take_snapshot(tmp_path, run_id="r", run_at=bad)
    with pytest.raises(ValueError, match="not a real date"):
        take_snapshot(tmp_path, run_id="r", run_at="2026-13-45 00:00:00")
    assert list(tmp_path.iterdir()) == [], "refused before anything was written"


def test_a_run_id_that_is_a_path_is_refused_rather_than_escaping_the_root(tmp_path):
    """A `run_id` that is a relative or absolute path is refused, so nothing is
    written outside the root.
    """
    root = tmp_path / "extracts"
    root.mkdir()
    for bad in ("..", ".", "", "../escaped", "..\\escaped", "a/b", "a\\b",
                str(tmp_path / "absolute"), ".hidden", "run id"):
        with pytest.raises(SnapshotError, match="not usable as a snapshot name"):
            take_snapshot(root, run_id=bad)
        with pytest.raises(SnapshotError, match="not usable as a snapshot name"):
            open_snapshot(root, bad)
    assert list(root.iterdir()) == []
    assert list_snapshots(root) == []


def test_a_run_id_ending_in_a_dot_is_refused(tmp_path):
    """A `run_id` ending in a dot is refused: Windows strips the dot, so the
    directory would not match its manifest.
    """
    root = tmp_path / "extracts"
    root.mkdir()
    for bad in ("run.", "r.", "snapshot-01."):
        with pytest.raises(SnapshotError, match="not usable as a snapshot name"):
            take_snapshot(root, run_id=bad)
    assert list(root.iterdir()) == [], "refused before anything was written"
    assert validate_run_id("r.1") == "r.1", "a dot INSIDE the name is still fine"


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
    """A build replayed from its retained extract, with no EA, is byte-identical to
    the original.

    The replay passes the original `run_id`; a new one would differ in that one
    cell by design.
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
    """A build from different rows is not byte-identical, so the test above can
    fail.

    The difference is in a typed element: an untyped one lands in no table and
    would not change the database.
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
    """Stated separately from the message test because this is the behavior that
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


def _blank_the_recorded_digest(db):
    """Leave a `_load_run` row holding a run_id and no digest.

    `build_database` refuses to write that pair, so this edits the row the way a
    database written earlier, or edited since, would hold it.
    """
    conn = sqlite3.connect(str(db))
    conn.execute('UPDATE "_load_run" SET "extract_digest" = \'\'')
    conn.commit()
    conn.close()


def test_a_build_cannot_record_half_an_extract_reference(tmp_path):
    """`build_database` refuses an extract `run_id` without its digest, and the
    reverse.
    """
    root = tmp_path / "extracts"
    manifest = take_snapshot(root)
    tables = open_snapshot(root, RUN).tables

    with pytest.raises(LoadError, match="both or neither"):
        build(tmp_path / "no-digest.sqlite", tables, run_id="build-1", run_at=AT,
              extract_run_id=RUN)
    with pytest.raises(LoadError, match="both or neither"):
        build(tmp_path / "no-run-id.sqlite", tables, run_id="build-1", run_at=AT,
              extract_digest=manifest["digest"])
    assert not (tmp_path / "no-digest.sqlite").exists(), "refused before writing"


def test_a_recorded_reference_with_no_digest_is_refused_not_returned(tmp_path):
    """CR-0229-03, the second gap. `extract_reference` guarded `if not row[0]` only,
    so a row with a run_id and an empty digest came back as `("run-0001", "")`
    instead of refusing - and the caller cannot tell that pair from a verified one.
    """
    root = tmp_path / "extracts"
    manifest = take_snapshot(root)
    db = tmp_path / "r.sqlite"
    build(db, open_snapshot(root, RUN).tables, run_id="build-1", run_at=AT,
          extract_run_id=RUN, extract_digest=manifest["digest"])
    _blank_the_recorded_digest(db)

    with pytest.raises(LoadError, match="half an extract reference"):
        extract_reference(db, "build-1")


def test_an_empty_expected_digest_is_a_refusal_not_a_skipped_check(tmp_path):
    """`open_snapshot` refuses an empty `expect_digest`; only `None` skips the
    check.
    """
    take_snapshot(tmp_path)
    with pytest.raises(SnapshotError, match="empty digest is not a digest"):
        open_snapshot(tmp_path, RUN, expect_digest="")
    assert open_snapshot(tmp_path, RUN, expect_digest=None).run_id == RUN


def test_a_replay_with_no_recorded_digest_refuses_a_substituted_extract(tmp_path):
    """A build with a run_id and no digest cannot be replayed from a different
    extract left under the same name.
    """
    root = tmp_path / "extracts"
    manifest = take_snapshot(root)
    db = tmp_path / "r.sqlite"
    build(db, open_snapshot(root, RUN).tables, run_id="build-1", run_at=AT,
          extract_run_id=RUN, extract_digest=manifest["digest"])
    _blank_the_recorded_digest(db)

    shutil.rmtree(snapshot_dir(root, RUN))
    take_snapshot(root, tables=dict(TABLES, object=TABLES["object"][:1]))
    assert len(open_snapshot(root, RUN).tables["object"]) == 1, "a different extract"

    with pytest.raises(LoadError, match="half an extract reference"):
        replay_snapshot(db, "build-1", root)


def test_a_run_id_that_is_not_in_the_database_is_not_silently_empty(tmp_path):
    manifest = take_snapshot(tmp_path / "extracts")
    db = tmp_path / "r.sqlite"
    build(db, open_snapshot(tmp_path / "extracts", RUN).tables,
          run_id="build-1", run_at=AT, extract_run_id=RUN,
          extract_digest=manifest["digest"])

    with pytest.raises(LoadError, match="no load_run row"):
        extract_reference(db, "build-does-not-exist")
