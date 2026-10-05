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

A COUNT OF PASSING TESTS IS NOT ASSURANCE. This file was green on 385 tests with
four defects in it that each destroyed or falsified the retained evidence: a replay
from a substituted extract returning 1 object where the build had 3 and raising
nothing, pruning deleting a directory outside the snapshot root, an aborted extract
leaking a directory nothing could see, and a run deleting the snapshot it had just
reported as retained. Every test added for those carries the measurement that
motivated it in its docstring, because the next reader's question is not "does this
pass" but "what would have to break for it to fail".
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

    `[Type]`, `[Scope]` and `[VALUE]` are bracketed in the shipped SQL because
    they are reserved words in EA's backends; the rows come back under the bare
    name.
    """
    return [c.strip().strip("[]") for c in clause.split(",")]


def _as_the_backend_would_order_them(rows, sql):
    """Apply the statement's own `ORDER BY` and projection, the way a backend does.

    The fake HAS to do this. A fake that hands back a fixed Python list makes any
    assertion about row order pass by construction - which is exactly how the
    digest-determinism claim came to be asserted by a test that could never fail.
    With the ordering emulated, dropping an `ORDER BY` from a shipped query shows
    up as a failure instead.

    It also has to SORT ON COLUMNS THE PROJECTION DOES NOT SELECT and then drop
    them, which is what the two queries that most need a tie-break do: `t_xref`
    orders by `XrefID` and `t_objectproperties` by `PropertyID`, neither of which
    is selected, because the alternative is sorting on a memo column and a backend
    that refuses to sort one reports it as a modal dialog. Filtering those columns
    out BEFORE sorting, as this fake used to, emulates no tie-break at all for
    exactly the two tables the design singles out - `sorted` is stable, so ties
    simply keep their input order and a dropped tie-break cannot be detected. The
    comment that justified it ("rows that tie on every selected column are
    byte-identical, so their order cannot change the digest") is false for
    `t_objectproperties`, where `Value` is selected and is not in the `ORDER BY`.
    """
    order = _ORDER_BY.search(sql)
    if order:
        rows = sorted(rows, key=lambda r: tuple(
            _sort_key(r.get(c)) for c in _columns(order.group(1))))
    selected = _columns(_SELECT.search(sql).group(1))
    return [{k: v for k, v in r.items() if k in selected} for r in rows]


def _answering_from(tables):
    """The row-parser half of the fake: a statement in, its rows out.

    Routes on the `FROM t_<name>` in the statement rather than on call order, so
    the fake cannot quietly drift out of step with the query constants. The word
    boundary is load-bearing: `t_object` is a prefix of `t_objectproperties`.
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


def _ea_is_reachable(patched, tables=None):
    """Put a fake `win32com.client` and row parser into `sys.modules`.

    `main()` imports both and returns 2 if it cannot reach them, so testing what it
    PRINTS - and in what order, which is a finding in its own right - needs them
    present. The repository echoes the statement and the "parser" answers from the
    fixture: the same seam `fake_extractor` uses, one layer out.
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


def test_a_manifests_sql_log_is_its_own_and_does_not_grow_afterwards(tmp_path):
    """W31. `manifest["sql_log"] = ex.sql_log` stored the Extractor's live list by
    reference, so a second extract through the same Extractor retro-edited the
    first manifest. Measured:

        after run 1: returned manifest sql_log length = 10
        after run 2: run 1's RETURNED manifest sql_log length = 20
        r1 ON-DISK sql_log: 10 | r2 ON-DISK: 20 | same list object: True

    The on-disk copies were fine - they were serialized at write time - but the
    returned manifest is what a caller records from, and run 2's own manifest
    claims twenty statements, ten of which produced a *different* snapshot. That
    contradicts the acceptance criterion that the issued SQL travels with the
    snapshot it produced. Nothing shipped constructs an `Extractor`, so this is not
    reachable from a documented path; it is one word, and `extract()` is a public
    function.
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
    """Two extracts of the same repository state hash the same. The digest answers
    "are these the same rows", not "is this the same run".

    True by construction - the digest covers the ten table files and neither
    `run_id` nor `run_at` - so the half of this property that CAN fail is row
    order, and that is the test below.
    """
    take_snapshot(tmp_path, run_id="a", run_at="2026-10-01 08:00:00")
    take_snapshot(tmp_path, run_id="b", run_at="2026-10-02 08:00:00")
    assert (snapshot_digest(snapshot_dir(tmp_path, "a"))
            == snapshot_digest(snapshot_dir(tmp_path, "b")))


def test_the_digest_does_not_depend_on_the_order_the_backend_returned_rows(tmp_path):
    """W3. The shipped claim is "two extracts of an unchanged repository hash the
    same", and nothing supported it: none of the ten queries carried an `ORDER BY`,
    so no backend promised an order. Measured on the branch that shipped without
    one - the same rows in a different order produced a different digest AND a
    byte-different database, so two builds of a genuinely unchanged repository could
    disagree and a customer would read row-order churn as model change.

    `t_objectproperties` is the soft spot: no unique index on
    (Object_ID, Property), one element can carry two tags of the same name, and
    which came back first was whatever the backend felt like. The fixture now
    holds that case - two `criticality` tags on element 1 - and the matching one
    for `t_xref`, so this comparison is over tables that genuinely need their
    tie-breaks.
    """
    take_snapshot(tmp_path, run_id="in-order", run_at="2026-10-01 08:00:00")
    take_snapshot(tmp_path, run_id="reversed", run_at="2026-10-02 08:00:00",
                  tables={name: list(reversed(rows))
                          for name, rows in TABLES.items()})
    assert (snapshot_digest(snapshot_dir(tmp_path, "in-order"))
            == snapshot_digest(snapshot_dir(tmp_path, "reversed")))


def test_every_shipped_query_orders_its_rows():
    """The mechanism the claim above rests on, pinned where it lives. A query added
    later without an `ORDER BY` makes the digest non-deterministic for that table
    and nothing else here would notice - the fixtures would still agree with
    themselves.

    W30. This used to iterate the two query dicts only, so "EVERY QUERY ORDERS ITS
    ROWS" (`extract.py:70`) and "every query carries an `ORDER BY`"
    (`the-extract-snapshot.md:132`) were both false against an ELEVENTH statement
    the check could not see: `resolve_scope`'s `t_package` walk. Measured in a
    scoped manifest's own `sql_log`:

        11 statements; last: SELECT Package_ID, Parent_ID FROM t_package
        has ORDER BY: False

    Its order cannot move the digest - the ids are re-sorted host-side - but
    `sql_log` is a shipped deliverable and its CONTENT is order-dependent, and a
    universal claim with one exception in it is what two rounds of review kept
    finding in this module. So the check now counts the statements the module
    actually issues rather than the ones that happen to live in a dict.
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
    """W19. The test above asserts two digests are EQUAL, so it proves nothing
    unless weakening a query's order can make them differ - and for half the
    shipped queries it could not. Measured on the branch: `attribute`, `operation`,
    `diagram`, `connector` and `connectortag` each had a ONE-ROW fixture, so
    `reversed()` was a no-op and the comparison was a file against itself. Those
    five queries were given a non-total `ORDER BY` - `connector` by `Stereotype`,
    `connectortag` by `Property`, `attribute` and `operation` by `[Scope]`,
    `diagram` by `Diagram_Type` - and the suite stayed green at 37 passed. The
    other guard, `test_every_shipped_query_orders_its_rows`, is
    `assert "ORDER BY" in sql`: it catches absence and cannot tell a total order
    from a wrong one.

    Separately, `_as_the_backend_would_order_them` dropped any `ORDER BY` column
    the projection does not select, which is `XrefID` and `PropertyID` - the two
    tie-breaks `extract.py` singles out - so for `t_xref` and `t_objectproperties`
    the fake emulated NO tie-break at all.

    So this is the net's own test, and W32 narrows what it claims. For each of
    the ten shipped queries in turn, its order is weakened BY DROPPING THE LAST
    `ORDER BY` COLUMN and the digests must then differ. That one mutation class is
    what is proven here - 10 of 10 - and it is the mistake a reviewer actually
    makes: a tie-break left off, or a single-column order deleted outright.

    IT IS NOT "the net can fail for any weakening of any query", which is what the
    old name and docstring said. Replacing a query's whole `ORDER BY` with a
    different single column is a weaker mutation and the fixture does not catch
    two of them: `connector ORDER BY Stereotype` and `attribute ORDER BY [Scope]`
    leave the digest stable, because the fixture has no TIE on either substituted
    column, so the rows come back in one sequence either way. Measured, with the
    other three for contrast:

        connector     ORDER BY Stereotype     digest moved: False
        attribute     ORDER BY [Scope]        digest moved: False
        connectortag  ORDER BY Property       digest moved: True
        operation     ORDER BY [Scope]        digest moved: True
        diagram       ORDER BY Diagram_Type   digest moved: True

    Giving those two fixtures a tie on the substituted column would close the gap
    and is deliberately not done here: the dropped-column class is the one the
    design rests on, and widening the fixture to chase a weaker class would change
    the rows every other test in this file measures against.
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
    """CR-0229-01. Pruning rebuilt the path from the manifest's own `run_id` -
    `rmtree(snapshot_dir(root, snap["run_id"]))` - instead of deleting the directory
    `list_snapshots` had just walked, and the manifest is deliberately outside the
    digest, so that field is unverified by design. What went is now reported as the
    directory that went."""
    take_snapshot(tmp_path, run_id="keep", run_at="2026-10-02 08:00:00")
    take_snapshot(tmp_path, run_id="drop", run_at="2026-10-01 08:00:00")

    removed = prune_snapshots(tmp_path, keep=1)
    assert [s["dir"] for s in removed] == [snapshot_dir(tmp_path, "drop")]
    assert [s["status"] for s in removed] == ["pruned"]
    assert not snapshot_dir(tmp_path, "drop").exists()
    assert snapshot_dir(tmp_path, "keep").is_dir()


def test_a_snapshot_restored_under_another_name_is_refused_not_pruned(tmp_path):
    """CR-0229-01, benign, and the code's own docstring invites it: ordering by the
    manifest's `run_at` is justified by a snapshot that "has been copied or
    restored". Reproduced on the branch: directories `run-archived`,
    `run-archived-restored` and `run-current`, and `prune_snapshots(keep=2)` deleted
    the ORIGINAL and kept the copy under a name `open_snapshot` can never find - so
    every build naming `run-archived` reported "has been pruned" with its rows still
    on disk, and retention reported it as a routine prune. `keep=1` then raised
    FileNotFoundError mid-loop, retention half-applied, because the duplicate
    `run_id` came back twice.

    Two names for one snapshot is now a loud refusal: one of them is wrong, and
    acting on either means deleting or replaying evidence nobody asked for.
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
    """CR-0229-01, the sharp end. Reproduced: editing one manifest's `run_id` to
    another path made pruning `rmtree` THAT path - an unrelated directory outside the
    root was deleted, the snapshot meant to be pruned survived, and
    `prune_snapshots` reported the outside path as removed. Editing the manifest
    leaves the digest intact, because the digest covers the table files only."""
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
    """CR-0229-04. `list_snapshots` skips a directory with no manifest and the
    manifest is written LAST, so a killed extract left table JSON under a snapshot
    name that pruning could not see and the "KiB on disk" line could not count -
    permanently. Reproduced: three such directories beside one good snapshot, and
    `prune_snapshots(keep=1)` returned [] with all four still on disk.

    The failure is the one the module documents as realistic: EA reports a statement
    its backend cannot run as a modal dialog that holds the COM connection, every
    later call appears to hang, and the run gets killed.
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
    """The rename into place is the commit, and on Windows it needs exclusive access
    to the whole subtree - an external scanner holding a file written a moment ago
    failed one with ACCESS_DENIED, observed once in about four hundred runs of this
    suite. It is retried, and if it still will not go the rows are NOT thrown away:
    they cost a COM extract against a repository that has already moved on. The
    operator finishes the job with a rename, and nothing reads the directory until
    they do."""
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
    """CR-0229-05(a), and it needs no failure at all to happen. `_RUN_ID` is
    case-sensitive; NTFS is not, and neither is `Path.exists`. Measured on the
    branch, with `Run-A` then `run-a` - both accepted by `validate_run_id`:

        after run 1, dirs: ['Run-A']   digest d687065edc54
        after run 2, dirs: ['run-a']   digest bddf304f85f9
        list_snapshots: [('run-a', '2026-10-02 08:00:00')]
        prune reports: []
        replay of the FIRST build: refused - 'Run-A' hashes to bddf304f...

    Three things wrong at once. `Run-A`'s rows were nowhere on disk. Nothing said
    so - `prune_snapshots` returned `[]` and `list_snapshots` showed one snapshot
    where the operator believed there were two, against a module that promises
    going is never silent. And the loss was MISATTRIBUTED: the replay reported
    "hashes to X, but the build recorded Y", which the shipped refusal table
    defines as a different extract under the same `run_id`, i.e. tampering.

    It also contradicted `extract.py` verbatim - "No OTHER snapshot is overwritten
    ... a different `run_id` is a different snapshot beside it".
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
    """CR-0229-05(b). `_commit` deleted the existing snapshot BEFORE the rename,
    above the retry and outside every handler - the retry guarded the
    non-destructive step and the destructive one sat bare, on a platform whose
    documented failure mode is exactly a held file. Measured on a repeat `run_id`
    (which `extract.py` documents as supported) with one file open inside it:

        second run raised PermissionError: [WinError 32] ... from extract.py:501
        SnapshotError, i.e. caught by main() -> exit 2?  False
        r1 on disk: 5 of the 10 table files; manifest still there?  False
        list_snapshots sees: []   prune reclaims: [('.incomplete-r1','incomplete')]
        STILL on disk after a full prune: ['r1']

    So: a destroyed manifest, a half-deleted snapshot, a husk invisible to every
    function and to the KiB figure that survived a full prune, a traceback instead
    of exit 2, and the earlier build told its evidence "has been pruned, or was
    never kept" - false twice over. This was a REGRESSION against the commit that
    overwrote in place, where the same interruption left a coherent, visible,
    loadable snapshot. So the bar is: no worse than that.

    Renaming the old snapshot aside first means the failure happens before
    anything is destroyed. Its rows are whole, it is still listed, and it still
    verifies against the digest the first build recorded.
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
    """CR-0229-05, the window itself. There must be no instant in which the
    snapshot's own name holds NEITHER the old rows nor the new ones, because that
    instant is what the measurement above is: the old manifest already gone, the
    new directory not yet renamed in, and nothing left that `list_snapshots`,
    `open_snapshot` or the sweep could see.

    Here the move-aside succeeds and the commit itself is then refused - the
    `WinError 5` the module documents as observed once in about four hundred runs.
    The old snapshot goes back under its own name, so the store holds one whole
    snapshot at every point, and the new rows are still kept.
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
    """The double failure: the commit rename refused AND the putback of the aside.

    The narrowest failure `_commit` has - two independent refusals of the same
    directory inside one call - and the only one that does not leave a snapshot
    under the `run_id`. Both W23 and W24 are about what the module SAYS in that
    state, so both need it.
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
    """W23. `_commit`'s docstring promised "every failure leaves one whole snapshot
    under it" and the shipped reference promised "at every instant that `run_id`
    holds one whole, loadable snapshot ... the retained snapshot stays readable and
    replayable UNDER ITS OWN NAME". One path breaks both, and it is a path the same
    function implements: the commit rename is refused and so is the putback.
    Reproduced:

        dirs: ['.incomplete-r1', '.superseded-r1']        <- no r1
        list_snapshots: []
        does the message mention pruning will reclaim?   False
        NEXT PRUNE destroys both:
          [('.incomplete-r1','incomplete'), ('.superseded-r1','superseded')]
        on disk after: []

    The rows are all there, and that part of the message was true. What was missing
    is the one thing the operator needed: nothing is retained under `r1`, so
    retention cannot see either copy, and THE NEXT PRUNE RECLAIMS BOTH - including
    the retained snapshot it was just told to keep. This was the only one of the
    four failure messages in `_commit` that omitted the pruning disclosure; the
    other three say "pruning will reclaim" in those words.

    And `superseded` reported the retained snapshot's only copy as "the copy a
    re-run of that run_id replaced", which on this path is false twice over.
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
    """W24. In that same state `open_snapshot(root, 'r1')` answered "it has been
    pruned, or was never kept" - verbatim, with the rows sitting in
    `.superseded-r1`. That is the exact false message CR-0229-05(b) was refused
    for, surviving on a narrower path, and it contradicts the refusal the operator
    had just been handed: that one says both sets of rows are on disk.

    The two facts are different and a replay has to be told which it is. Pruned
    means the evidence is gone and the figure cannot be defended. This means the
    evidence is on disk under a name nothing reads, and one rename recovers it.
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
    """W25. `validate_new_run_id` compared `d.name.casefold()` against the new
    `run_id`, and the debris names carry the run_id's OWN case - so
    `.incomplete-Run-A` never casefold-matched a bare `run-a` and the collision
    scan walked past it. From the W23 state, which is reachable without an operator
    mistake and where those rows are the ONLY copy:

        state: ['.incomplete-Run-A', '.superseded-Run-A']
        the .incomplete- rows the previous message promised were intact: 3 objects
        run as 'run-a': ACCEPTED.  state: ['.superseded-Run-A', 'run-a']
          -> .incomplete-Run-A was silently reclaimed: True
        replay of the FIRST build: "extract snapshot 'Run-A' hashes to c46bbc2b...,
          but the build recorded e60e6f58..."

    `extract()` treats `.incomplete-<run_id>` as leftovers of "this run_id" and
    reclaims it, and NTFS makes `.incomplete-Run-A` that directory for `run-a`. So
    the case collision CR-0229-05(a) was refused for is reached one directory over,
    it destroys rows a refusal message promised were intact, and it is misreported
    as tampering - all three of that finding's consequences.

    The refusal has to name the `run_id` to pass, not the prefixed directory, which
    is not a valid `run_id` and could not be passed to anything.
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
    """CR-0229-04's other half: bounded has to hold for a run killed so hard that
    nothing cleaned up after it. The leftover is named so that it can never be
    mistaken for a snapshot - it is skipped by retention and refused by a replay -
    and pruning reclaims it and SAYS SO. A directory nothing can see is a directory
    nothing ever reclaims, which is the unbounded store by another route."""
    root = tmp_path / "extracts"
    take_snapshot(root, run_id="good", run_at="2026-10-01 08:00:00")
    debris = root / f"{INCOMPLETE_PREFIX}killed"
    debris.mkdir()
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
    """CR-0229-06. The sweep matched `.incomplete-*` only, and `list_snapshots`
    requires a manifest - so a manifest-less directory under a PLAIN name was
    invisible to both, and to the KiB-on-disk figure, and survived a full prune
    permanently. Measured with two of them beside one good snapshot:

        plain-named manifest-less dirs: swept = []
        still on disk: ['good','legacy-1','legacy-2']
        list_snapshots counted 4,374 of the 5,344 bytes actually there

    That is the acceptance criterion - retention bounded, and the bound stated -
    failing by a second route, and it made the shipped reference's "whatever a hard
    kill does leave is swept by the next `prune_snapshots`" false as written.

    Prefix-matching was the mistake: debris does not only arrive by the route
    designed for it. Both producers are real and neither writes the prefix - the
    husk a refused replacement used to leave, and a prune stopped by a held file
    (next test). So the rule is what the store can SEE, not what it is called:
    every directory that is not a loadable snapshot is reclaimed, and reported.
    """
    root = tmp_path / "extracts"
    take_snapshot(root, run_id="good", run_at="2026-10-01 08:00:00")
    for name in ("legacy-1", "legacy-2"):
        husk = root / name
        husk.mkdir()
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
    """CR-0229-08, and the reason this test exists rather than an assertion
    somewhere smaller. The sweep CR-0229-06 added tested only "is it a directory,
    and was it not a loadable snapshot" - which is not a rule about debris at all.
    `--out` is free text, nothing checks that the root belongs to this tool, and
    there is no confirmation step, so pointing it at a populated directory
    reclaimed every subdirectory in it. Reproduced through `main()` with NO failure
    of any kind, against a path an operator could plausibly type:

        before: ['.git', 'README.md', 'docs', 'extracts', 'research', 'src']
        exit: 0
        after:  ['README.md', 'x']
        SWEPT .git (0 KiB) - ... which is what a delete stopped by a held file
          leaves. Nothing could be replayed from it ...

    `.git` and the working tree gone, irreversibly, each deletion reported as 0 KiB
    of something no held file had anything to do with, and the run reporting
    SUCCESS. The item's own repro uses `--out ./out`; `--out .` does this to a
    checkout. It was a regression of that round: at the two earlier heads the sweep
    matched `.incomplete-*` and left such directories alone.

    So the sweep answers from POSITIVE evidence - `_is_debris`: one of the two
    prefixes this module writes, or at least one `<table>.json` - and this test
    drives the whole thing through `main()`, because every cheaper check passed
    while the defect was live.

    Two assertions carry the weight. Everything unrelated is STILL THERE after a
    successful run, `.git` included. And nothing unrelated is REPORTED, because a
    sweep report is a list of what went and a line naming a directory that did not
    go is the same false statement in a quieter form.
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
    """The other half of CR-0229-08: the narrowing must not undo CR-0229-06. Both
    real debris producers are here at once, beside directories that are not this
    tool's and must survive - which is the combination neither finding's own test
    covers on its own.

    `.incomplete-killed` is the prefix route. `legacy-1` is the plain-named husk a
    stopped delete leaves, identified by the table file it still holds, which is
    what CR-0229-06 was refused for missing. `docs` and `archive-2026-09` hold no
    table file at their top level and carry no prefix, so nothing here can say what
    they are - and a tool that cannot say what something is does not delete it.

    `archive-2026-09` is the case that makes the rule matter rather than just being
    safe: a whole loadable snapshot one directory down. The old sweep destroyed one
    and reported it as `unreadable`, 0 KiB, "nothing could be replayed from it" -
    measured at 5,349 real bytes of replayable rows.
    """
    root = tmp_path / "extracts"
    take_snapshot(root, run_id="good", run_at="2026-10-01 08:00:00")

    killed = root / f"{INCOMPLETE_PREFIX}killed"
    killed.mkdir()
    (killed / "object.json").write_text("[]", encoding="utf-8")
    husk = root / "legacy-1"
    husk.mkdir()
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
    """W34, which the CR-0229-08 narrowing is supposed to close, so it is checked
    rather than assumed. A junction is a directory to `is_dir()` and the old sweep
    therefore tried to reclaim one on every prune - and could not, because
    `shutil.rmtree` refuses a reparse point. Measured at the previous head:

        sweep reported: [('shortcut', 'held', 8)]   junction still present: True
        TARGET survived: True                       main() exit: 1

    So it sat in the HELD block for ever and `main()` returned 1 for ever, with the
    store reported as over its bound by a directory retention was never entitled to
    delete. The good news was measured too and holds: no traversal through the
    junction, the target and its contents were never at risk.

    It carries no prefix and holds no table file, so `_is_debris` now says no and
    the retry budget is not spent on it at all.
    """
    root = tmp_path / "extracts"
    take_snapshot(root, run_id="good", run_at="2026-10-01 08:00:00")
    target = tmp_path / "somewhere-else"
    target.mkdir()
    (target / "precious.txt").write_text("not retention's to delete",
                                         encoding="utf-8")
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
    """CR-0229-08's report limb, and W27. `bytes` summed `d.iterdir()`, top level
    only, so a swept TREE was reported as 0 KiB - measured at 0 against 5,353 real
    bytes. Against the module's own rule that silently discarding the evidence
    behind a quoted figure is the failure retention exists to prevent, a deletion
    announced as nothing is not meaningfully louder than a silent one.

    Kept separate from the narrowing because it survives it: debris legitimately
    has subdirectories - a killed run writes its table files one level down from
    nothing, and a copied store brings whatever was in it.
    """
    root = tmp_path / "extracts"
    take_snapshot(root, run_id="good", run_at="2026-10-01 08:00:00")
    debris = root / f"{INCOMPLETE_PREFIX}killed"
    (debris / "nested").mkdir(parents=True)
    (debris / "object.json").write_text("[]", encoding="utf-8")
    (debris / "nested" / "rows.json").write_text("y" * 4000, encoding="utf-8")
    real = sum(f.stat().st_size for f in debris.rglob("*") if f.is_file())

    removed = prune_snapshots(root, keep=KEEP_RUNS)
    assert [s["bytes"] for s in removed] == [real]
    assert real > 4000, "the fixture has to have more below the top level than in it"


def test_the_swept_report_claims_no_cause_it_did_not_check(tmp_path):
    """W28. The `unreadable` sentence told the operator the directory was "what a
    delete stopped by a held file leaves", and `main()` added "Nothing could be
    replayed from it". Neither was checked, and in every CR-0229-08 reproduction
    both were false: no held file was involved anywhere, and one of the
    directories was a loadable snapshot.

    `superseded` had the same shape - "the copy a re-run of that run_id replaced" -
    which is false on the one path where it is the ONLY copy and nothing replaced
    it (see the putback test below).

    This asserts the absence of a claim, which is a weak test on its own, so it
    pins the mechanism too: a status may not be swept without a sentence, and the
    sentences are keyed to exactly the statuses `_debris_status` can return.
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
    husk = root / "legacy-1"
    husk.mkdir()
    (husk / "object.json").write_text("[]", encoding="utf-8")
    assert [s["status"] for s in prune_snapshots(root, keep=KEEP_RUNS)] == [
        "unreadable"], "and the keying is live, not just a constant"


def test_a_prune_stopped_by_a_held_file_is_reported_not_raised(tmp_path):
    """CR-0229-06's second producer - and the same lesson as CR-0229-05, applied to
    the delete retention has always done. Measured with one table file held open:

        prune raised PermissionError: [WinError 32]      <- raw, mid-loop
        'drop' dir now: 5 table files, no manifest
        list_snapshots sees: ['keep']
        a SECOND full prune reclaims: []
        still on disk: ['drop', 'keep']

    `shutil.rmtree` stops at the first file it cannot remove, and the manifest goes
    early in directory order - so the failed prune MANUFACTURED the invisible
    plain-named husk of the test above, then raised out of the loop, which also
    cost the caller the report of everything that had already gone.

    Retried now, and a directory that will not go is reported as `held` rather than
    raised: one locked directory cannot cost the report, the operator is told it is
    still there, and whatever is left of it is swept by the next prune. A `held`
    entry is the one status that means "still on disk".
    """
    root = tmp_path / "extracts"
    take_snapshot(root, run_id="keep", run_at="2026-10-02 08:00:00")
    take_snapshot(root, run_id="drop", run_at="2026-10-01 08:00:00")

    with open(snapshot_dir(root, "drop") / "object.json", encoding="utf-8"):
        removed = prune_snapshots(root, keep=1)
        assert [(s["run_id"], s["status"]) for s in removed] == [("drop", "held")]
        assert snapshot_dir(root, "drop").exists(), "held means still there"

    assert [(s["run_id"], s["status"]) for s in prune_snapshots(root, keep=1)] == [
        ("drop", "unreadable")]
    assert [p.name for p in root.iterdir()] == ["keep"]


def test_a_held_prune_target_can_be_gutted_and_held_does_not_deny_it(
        tmp_path, capsys):
    """W38. `shutil.rmtree` stops at the first file it cannot remove - AFTER
    deleting everything ahead of it - so whether a refused prune leaves a loadable
    snapshot or a husk depends on where the locked file sorts against
    `extract-manifest.json`. The test above holds `object.json`, which sorts
    *after* it, so the manifest goes and the directory degrades into swept
    `unreadable` debris. That is the benign variant, and it was the only one
    covered. Both measured:

        holding connector.json (sorts BEFORE the manifest):
          files 11 -> 10; manifest survived: True; missing: ['attribute.json']
          still LISTED as a snapshot: ['keep','drop']
          the KiB figure counts it: 10495 | open_snapshot('drop') -> raw
          FileNotFoundError

        holding object.json (sorts AFTER the manifest):
          files 11 -> 5; manifest survived: False; still LISTED: ['keep']

    The first variant is the `held` path manufacturing a snapshot that is listed,
    counted toward `keep` and no longer replayable out of one that was whole - and
    the shipped status table said `held` means it "is still there", which reads as
    a promise that it is intact.

    Scope, honestly: only snapshots already outside `keep` reach the delete, so
    this is confined to directories already selected for deletion and it
    self-heals on the next prune. That is why the fix is the REPORT rather than the
    deletion, and why this test pins the wording and the self-healing rather than
    asserting the gutting cannot happen.
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
    """W36, W26 and W9, which are one edit. `list_snapshots` read the manifest with
    a bare `json.loads` and an unguarded `man["run_at"]`, and `prune_snapshots`
    calls it BEFORE the sweep - so one unreadable manifest raised out of every
    prune, that directory survived for ever, and it blocked the reclamation of
    everything else in the store. Three classes, all measured:

        truncated manifest -> JSONDecodeError out of list_snapshots AND
          prune_snapshots; dirs after a full prune: ['good', 'legacy-1'];
          main() exit 1, stderr "Unterminated string starting at: line 1
          column 24" and the message names NO path
        valid JSON that is not an object ([]) -> AttributeError: 'list' object has
          no attribute 'get', which main() did not catch at all
        a manifest with no `run_at` -> KeyError('run_at'), uncaught, a traceback
          where the exit-1 contract promises a message - and this is the case
          `test_main_prints_the_reference_before_it_prunes`'s own docstring names

    Reachable without an operator mistake: a partial copy while restoring an
    archived snapshot, which the shipped reference tells operators to do, or a
    disk-full during the manifest write.

    A directory this function cannot read is not a snapshot - which is all it ever
    needed to be. It is then debris like any other, swept if it holds table files,
    and `main()` completes.
    """
    for label, body in (("truncated", '{"run_id": "legacy-1", "run_a'),
                        ("not an object", "[]"),
                        ("no run_at", '{"run_id": "legacy-1"}')):
        root = tmp_path / label
        take_snapshot(root, run_id="good", run_at="2026-10-01 08:00:00")
        bad = root / "legacy-1"
        bad.mkdir()
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
    """W29. `open_snapshot` did not enforce the directory/manifest agreement
    `list_snapshots` does, and it returned the MANIFEST's `run_id` as the
    snapshot's identity. Observed:

        open_snapshot(root, 'run-archived-restored').run_id == 'run-archived'

    The documented build passes `extract_run_id=snap.run_id` (`SKILL.md:200`), so
    that call persists a provenance claim naming a directory the build did not
    read - and the next replay of that build looks up `run-archived`, finds the
    original, and reconciles perfectly against the wrong rows. The shipped refusal
    table already promised this one: "Two directories claiming one `run_id` ->
    `SnapshotError` naming both" (`the-extract-snapshot.md:297`), which was true
    for `list_snapshots` and `prune_snapshots` and false here.
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
    """CR-0229-06's other limb. `main()` called `prune_snapshots` and then
    `list_snapshots` with no `try`, and both sat AHEAD of the only lines that print
    the `run_id` and the digest. Measured, with a valid new snapshot already on
    disk and one restored copy elsewhere in the store:

        the new snapshot is on disk and valid: True  digest d687065edc54
        prune raised SnapshotError -> main() has NO handler here
        => the operator never sees 'snapshot ... retained at ...' or 'digest ...'

    Any store-level condition in a directory unrelated to this run does it: a held
    file, a trailing-dot name, a manifest missing `run_at`. And because
    `build_database` now refuses half a reference - correctly - an operator who
    cannot read the digest cannot record provenance at all, so the build ships with
    none. The reorder bought nothing: `protect` is what stops this run being
    pruned, not the printing order.

    So the reference goes out first and retention reports its own failure, with a
    distinct exit code, against a snapshot that is on disk and replayable.
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
    """W39. `main()` was exercised by exactly ONE test, and it was the exit-1 path -
    so the whole `retention:` / `PRUNED` / `SWEPT` print block shipped unexercised.
    That is how CR-0229-08's wording and W37's exit-code contradiction stayed
    invisible through two rounds: both live in output nothing read.

    Exit 0 with a prune that actually removes something, which is the ordinary
    run: the retention line, and the PRUNED block saying out loud that a figure
    quoted from those builds can no longer be reproduced from its own rows.
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
    """W39's second half. `superseded` is in the shipped status table
    (`the-extract-snapshot.md`) and in `_SWEPT_REASON`, and NO test ever produced
    it - so the one status whose wording W23 found false was documented, shipped,
    and never once observed by the suite.

    Here a re-run's aside cannot be deleted at the time, which is the state the
    status exists for, and the next run reports it.
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
    """W37. The eleven snapshot `write_text` calls are the one step this whole
    commit is premised on being refusable, and nothing retried them and nothing
    caught them: `main()`'s `try` took `SnapshotError` only. Reproduced by refusing
    the sixth write:

        main() -> UNCAUGHT PermissionError: [Errno 5] Access is denied
        process exit 1 | a digest line was printed: False | store contents: []

    Exit 1 is DOCUMENTED as "the snapshot is retained and its digest is printed but
    retention did not complete". Here nothing was retained, no digest was printed
    and the store was empty, so an operator or a CI step keying off exit 1 is told
    its provenance is recoverable when there is no provenance at all. 2 is the code
    that means nothing was retained, and that is what this is.
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


# --- a run never deletes the snapshot it has just reported as retained -------

def test_the_run_just_written_is_never_pruned(tmp_path):
    """CR-0229-02. `main()` printed "snapshot <id> retained" and "pass
    extract_run_id and extract_digest to build_database", and THEN pruned on a
    lexicographic sort over the `--run-at` the operator typed. Reproduced: ten
    snapshots dated 2026-10-01..10, then `--run-id backfill --run-at
    '2026-09-01 08:00:00'` - written, and deleted by the same invocation, after the
    operator had already been told to record `extract_run_id=backfill`.

    Reachable without an error: restating an as-of date, re-extracting an archived
    model, or clock skew on a second machine.
    """
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
    """CR-0229-07, which reopened CR-0229-02 in the public function the shipped
    reference tells a reader to call. `protected = {str(p) for p in protect}`
    iterates a bare string into its characters. Measured as the verbatim
    CR-0229-02 reproduction:

        prune_snapshots(root, keep=10, protect="backfill")
          removed: ['backfill']
          backfill still on disk? False
          the protected set actually built: {'c','a','i','b','l','f','k'}

    No error, no report, and `prune_snapshots` promises the opposite - "`protect`
    names run_ids that are never pruned however the order comes out". `main()`
    happens to pass a tuple, so the CLI was safe; `the-extract-snapshot.md`
    documents the call as `protect=(this_run_id,)`, where a forgotten trailing
    comma was all that stood between a reader and deleting the evidence behind the
    build they had just made. A collection or nothing.
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
    """CR-0229-02's cause. `--run-at` was free text, and retention order is a
    lexicographic sort over it: `2026-10-05T08:00:00` and `05/10/2026` both sort
    wrongly against space-separated values, and the sort decides what gets DELETED.
    Refused before any query is issued - a bad timestamp found after the COM round
    trip is one found too late."""
    for bad in ("2026-10-05T08:00:00", "05/10/2026", "2026-10-5 8:00:00",
                "2026-10-05", "2026-10-05 08:00", "", "yesterday"):
        with pytest.raises(ValueError, match="YYYY-MM-DD HH:MM:SS"):
            take_snapshot(tmp_path, run_id="r", run_at=bad)
    with pytest.raises(ValueError, match="not a real date"):
        take_snapshot(tmp_path, run_id="r", run_at="2026-13-45 00:00:00")
    assert list(tmp_path.iterdir()) == [], "refused before anything was written"


def test_a_run_id_that_is_a_path_is_refused_rather_than_escaping_the_root(tmp_path):
    """W4, referred to Security. Verified to escape on the branch: `snapshot_dir`
    was `Path(root) / str(run_id)`, so `..\\escaped` wrote outside the root and an
    absolute `run_id` escaped it entirely - pathlib discards the left operand on an
    absolute right operand. `list_snapshots(root)` then returned [], so the snapshot
    was invisible to retention and never pruned, while `open_snapshot` still loaded
    it: a traversal and an unbounded store in one move. At replay time the value
    comes out of `_load_run` in a database file that may have traveled, so it is
    not an operator-only input."""
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
    """W16. `_RUN_ID` allowed a trailing dot, which the Win32 path layer strips, so
    `run_id='run.'` was accepted and created a directory called `run` holding a
    manifest that named `run.` - which is the two-directories-one-run_id condition
    `list_snapshots` refuses. Measured:

        extract(run_id='run.') succeeded, manifest run_id = 'run.'
        directories actually created: ['run']
        list_snapshots -> SnapshotError: directory 'run' ... naming 'run.'
        ... a second, legitimate extract then succeeds, and list_snapshots STILL
            raises

    From that point every `list_snapshots`, `prune_snapshots` and retention report
    raised for the WHOLE store, so retention stopped entirely - unbounded again -
    and every later run died before printing its own digest. One character class,
    and `validate_run_id` promises "one safe path component" on a platform where a
    trailing dot is not one.
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

    `build_database` refuses to write that pair now, so the only way to produce one
    is the way one would really arrive: a row written before the refusal existed, or
    edited since.
    """
    conn = sqlite3.connect(str(db))
    conn.execute('UPDATE "_load_run" SET "extract_digest" = \'\'')
    conn.commit()
    conn.close()


def test_a_build_cannot_record_half_an_extract_reference(tmp_path):
    """CR-0229-03, the first of three gaps that lined up. `extract_run_id` and
    `extract_digest` defaulted to "" INDEPENDENTLY with nothing validating that they
    arrive as a pair, so a build could record a snapshot name with nothing to check
    it against. Measured consequence on the branch: with `extract_digest=""`
    recorded and the snapshot then replaced by a different extract under the same
    `run_id`, `replay_snapshot` returned 1 object where the original build had 3 and
    raised nothing.

    A figure quoted from such a build is worse than one with no snapshot behind it,
    because it carries provenance that looks checked and is not.
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
    """CR-0229-03, the third gap. `if expect_digest and digest != expect_digest`
    short-circuited on an empty string, so the substitution check was skipped by the
    ABSENCE of a value rather than by a decision. `open_snapshot` is public and
    reachable directly, so the refusal belongs here too and not only in
    `extract_reference`.

    `None` is the first build reading the extract it has just taken, which has no
    recorded figure to check against yet. An empty string is not that case.
    """
    take_snapshot(tmp_path)
    with pytest.raises(SnapshotError, match="empty digest is not a digest"):
        open_snapshot(tmp_path, RUN, expect_digest="")
    assert open_snapshot(tmp_path, RUN, expect_digest=None).run_id == RUN


def test_a_replay_with_no_recorded_digest_refuses_a_substituted_extract(tmp_path):
    """CR-0229-03 end to end - the reviewer's reproduction, now a test. The build
    records a run_id with no digest, the snapshot is replaced by a DIFFERENT extract
    under the same name, and the replay previously returned 1 object where the
    original build had 3, raising nothing. This is the failure `load.py` claims is
    designed out and the one the module calls worse than a missing snapshot: it
    would reconcile perfectly and still answer about the wrong moment.
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
