#!/usr/bin/env python3
"""Pull the rows a census and a reporting database need out of a live EA repository.

THIS IS THE ONE IMPURE MODULE IN THE SET, DELIBERATELY. Everything else here is
a pure function over plain data. This file talks COM and writes files, and it is
confined to doing exactly that: it fetches rows and dumps them. It computes
nothing a pure module could compute, so there is one place to look when an
extraction is wrong and one place to test when it is not.

WHY A SCRIPT RATHER THAN TOOL CALLS
-----------------------------------
Bulk extraction cannot go through the agent loop. `execute_sql` returns each
result BOTH parsed and as raw XML with no row cap (APT-2026-0221), so a
repository-wide pull is materialised twice and travels through a context window.
This talks to EA directly and writes to disk; the transform then iterates over
the dump without re-querying EA, which also sidesteps the measured ~150x variance
in COM call timing.

PORTABLE SQL ONLY
-----------------
Plain SELECTs, parenthesised multi-table joins, no CTEs, no window functions, no
backend-specific syntax. This is not fastidiousness: EA reports a statement its
backend cannot run as a MODAL DIALOG that holds the COM connection until a human
dismisses it, and every later call then appears to hang rather than erroring.
Aggregation happens in Python, where it can be tested.

THE EXTRACT IS RETAINED, NOT OVERWRITTEN
----------------------------------------
Each run writes a SNAPSHOT under its own `run_id`, and `load_run` records which
snapshot a build consumed. This is what makes a build replayable with no EA
connection at all - the slowest, least repeatable part of the pipeline is paid
for once - and it is also the only record of what the repository contained at
that instant. The model is shared; a package count was observed moving three
times in twenty minutes while measurements were running. `load_run.run_at` is
already the as-of date for any figure quoted from a build, and the snapshot is
the evidence behind that date.

Retention is BOUNDED and pruning REPORTS what it removed - see `KEEP_RUNS` and
`prune_snapshots`. Silently discarding the evidence behind a figure somebody has
quoted is the failure retention exists to prevent, so it is never silent.

Run from a directory where EA is already running with the model open:

    python extract.py --out ./extracts --run-id <id> --run-at '<timestamp>'
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import shutil
import sys
import time
from dataclasses import dataclass

#: Rows pulled whole. Small, repository-wide, and needed by the census.
CENSUS_QUERIES = {
    "object": "SELECT Object_ID, ea_guid, Name, Object_Type, Stereotype, Package_ID FROM t_object",
    "xref": "SELECT Client, Description FROM t_xref WHERE Name = 'Stereotypes'",
    "objectproperties": "SELECT Object_ID, Property, Value FROM t_objectproperties",
    "package": "SELECT Package_ID, Parent_ID, Name FROM t_package",
}

#: Structural content. Column names and reserved-word brackets are read from
#: EA's schema rather than guessed: t_attribute needs [Type], [Scope], [Default];
#: t_operation needs [Type], [Scope]; and t_diagram's type column is
#: Diagram_Type, NOT Type. Its primary key is Diagram_ID, where t_attribute's is
#: ID and t_operation's is OperationID.
#: t_connector carries ea_guid so a connector's stereotype provenance can be
#: looked up in t_xref - without it `rel_all.profile` could only ever be empty.
STRUCTURE_QUERIES = {
    "attribute": "SELECT ID, Object_ID, Name, [Type], [Scope] FROM t_attribute",
    "operation": "SELECT OperationID, Object_ID, Name, [Type], [Scope] FROM t_operation",
    "diagram": "SELECT Diagram_ID, Name, Diagram_Type, Package_ID FROM t_diagram",
    "diagramobjects": "SELECT Diagram_ID, Object_ID FROM t_diagramobjects",
    "connector": ("SELECT Connector_ID, ea_guid, Name, Connector_Type, Stereotype, "
                  "Start_Object_ID, End_Object_ID FROM t_connector"),
    "connectortag": "SELECT PropertyID, ElementID, Property, [VALUE] FROM t_connectortag",
}


#: Every table a snapshot holds, which is also what its digest covers.
TABLE_NAMES = tuple(CENSUS_QUERIES) + tuple(STRUCTURE_QUERIES)

MANIFEST_NAME = "extract-manifest.json"

#: How many snapshots are retained, and the bound the acceptance criteria ask to
#: be STATED rather than guessed. MEASURED on the reference ~300-element model:
#: its ten table files plus the manifest are 244 KiB for 2,052 rows, about 122
#: bytes a row. Ten runs therefore cost 2.4 MiB there, and roughly 240 MiB on a
#: repository a hundred times its size.
#:
#: Which is why retention is ON and has no off switch: against the cost of a
#: build nobody can replay, a few megabytes is not a trade worth offering. The
#: bound is what keeps it honest - an unbounded store of every extract forever is
#: a different defect, and on a large repository the JSON is not small.
KEEP_RUNS = 10


class SnapshotError(Exception):
    """A retained extract could not be produced as the one that was asked for.

    Raised for a snapshot that has been pruned and for one whose rows are not
    the rows the build recorded. Both are loud on purpose: a replay that quietly
    used whatever was on disk would produce a figure nobody could defend, which
    is the whole failure retention exists to prevent.
    """


@dataclass
class Snapshot:
    """A retained extract, reopened. Enough on its own to state what a replayed
    build was built from: the rows, and the scope, counts and issued SQL that
    came with them."""
    run_id: str
    run_at: str
    digest: str
    manifest: dict
    tables: dict[str, list[dict]]


def snapshot_dir(root, run_id: str) -> pathlib.Path:
    return pathlib.Path(root) / str(run_id)


def snapshot_digest(directory) -> str:
    """sha256 over the table files, in name order.

    The manifest is deliberately NOT covered: it carries this value, and a digest
    cannot cover itself. What is being identified is the rows a build consumed,
    because that is what a disputed figure turns on.
    """
    h = hashlib.sha256()
    directory = pathlib.Path(directory)
    for name in sorted(TABLE_NAMES):
        h.update(name.encode("utf-8"))
        h.update((directory / f"{name}.json").read_bytes())
    return h.hexdigest()


def list_snapshots(root) -> list[dict]:
    """Retained snapshots, newest first, as `{run_id, run_at, bytes}`.

    Ordered by the manifest's own `run_at`, never by file mtime: a snapshot that
    has been copied or restored keeps the moment the extract was TAKEN, and that
    is the moment a figure is as-of.
    """
    root = pathlib.Path(root)
    if not root.is_dir():
        return []
    out = []
    for d in sorted(root.iterdir()):
        manifest = d / MANIFEST_NAME
        if not (d.is_dir() and manifest.is_file()):
            continue
        man = json.loads(manifest.read_text(encoding="utf-8"))
        out.append({
            "run_id": man["run_id"],
            "run_at": man["run_at"],
            "bytes": sum(f.stat().st_size for f in d.iterdir() if f.is_file()),
        })
    return sorted(out, key=lambda s: (s["run_at"], s["run_id"]), reverse=True)


def prune_snapshots(root, keep: int = KEEP_RUNS) -> list[dict]:
    """Delete all but the newest `keep` snapshots. Returns what it removed.

    The return value is the point of the function. Silently discarding the
    evidence behind a figure somebody has already quoted is precisely the failure
    this guards against, so every removal is reported with its run_id, its date
    and its size, and the caller is expected to say so out loud.
    """
    if keep < 1:
        raise ValueError(f"keep must be at least 1, got {keep!r}")
    removed = []
    for snap in list_snapshots(root)[keep:]:
        shutil.rmtree(snapshot_dir(root, snap["run_id"]))
        removed.append(snap)
    return removed


def open_snapshot(root, run_id: str, *, expect_digest: str = "") -> Snapshot:
    """Reopen the retained extract named `run_id`, or refuse to guess.

    Looks only ever at that one run_id's directory, so there is no path by which
    a replay reads a different extract than the one it asked for. Two failures,
    both loud:

    PRUNED - a `load_run` row naming a snapshot that is gone says so plainly, and
    lists what is still retained, because the alternative is a replay that
    rebuilds from whatever happened to be on disk and reports the result as the
    original figure.

    SUBSTITUTED - a snapshot whose rows do not hash to what the build recorded is
    a DIFFERENT extract under the same name. That is worse than a missing one: it
    would reconcile perfectly and still answer a question about the wrong moment.
    """
    directory = snapshot_dir(root, run_id)
    manifest_path = directory / MANIFEST_NAME
    if not manifest_path.is_file():
        retained = [s["run_id"] for s in list_snapshots(root)] or ["none"]
        raise SnapshotError(
            f"extract snapshot {run_id!r} is not retained under {root}: it has "
            f"been pruned, or was never kept. Retained now: "
            f"{', '.join(retained)}. The build that consumed it cannot be "
            f"replayed, and no other snapshot is a substitute for it - a figure "
            f"quoted from that build can only be reproduced from its own rows.")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    digest = snapshot_digest(directory)
    if digest != manifest["digest"]:
        raise SnapshotError(
            f"extract snapshot {run_id!r} does not match the digest in its own "
            f"manifest ({digest} vs {manifest['digest']}): its files have been "
            f"changed since it was written, so it is no longer evidence of "
            f"anything.")
    if expect_digest and digest != expect_digest:
        raise SnapshotError(
            f"extract snapshot {run_id!r} hashes to {digest}, but the build "
            f"recorded {expect_digest}. This is a different extract under the "
            f"same run_id; refusing to replay from it.")

    tables = {name: json.loads((directory / f"{name}.json").read_text(
        encoding="utf-8")) for name in TABLE_NAMES}
    return Snapshot(run_id=manifest["run_id"], run_at=manifest["run_at"],
                    digest=digest, manifest=manifest, tables=tables)


class Extractor:
    """Thin wrapper over EA's SQLQuery. Fetches and logs; decides nothing."""

    def __init__(self, repo, parse_rows):
        self.repo = repo
        self._parse = parse_rows
        self.sql_log: list[dict] = []

    def query(self, sql: str, label: str) -> list[dict]:
        t0 = time.perf_counter()
        rows = self._parse(self.repo.SQLQuery(sql) or "")
        ms = (time.perf_counter() - t0) * 1000
        # The issued-SQL log is a deliverable, not debug output: when a count is
        # questioned, the statement that produced it has to be readable.
        self.sql_log.append({"label": label, "ms": round(ms, 1),
                             "rows": len(rows), "sql": sql.strip()})
        return rows


def resolve_scope(ex: Extractor, root_package_id: int) -> tuple[list[int], int, bool]:
    """Package ids in the subtree under `root_package_id`, host-side.

    Returns (package_ids, max_depth_reached, truncated).

    Host-side because recursive CTEs are not portable and Jet has none. NO depth
    cap: the shipped `_package_subtree_ids` stops at depth 8 and `continue`s past
    anything deeper with no warning and no flag (APT-2026-0216), so a deep tree
    silently loses its leaves. This walks the whole tree and reports the depth it
    reached. The only guard is the `seen` set, against a cycle.
    """
    rows = ex.query("SELECT Package_ID, Parent_ID FROM t_package", "scope: t_package")
    children: dict[int, list[int]] = {}
    for r in rows:
        try:
            pid, parent = int(r["Package_ID"]), int(r["Parent_ID"] or 0)
        except (TypeError, ValueError):
            continue
        children.setdefault(parent, []).append(pid)

    out, seen = [int(root_package_id)], {int(root_package_id)}
    queue = [(int(root_package_id), 0)]
    deepest = 0
    while queue:
        current, depth = queue.pop(0)
        deepest = max(deepest, depth)
        for pid in sorted(children.get(current, [])):
            if pid in seen:
                continue
            seen.add(pid)
            out.append(pid)
            queue.append((pid, depth + 1))
    return sorted(out), deepest, False


def extract(ex: Extractor, root, root_package_id: int | None = None, *,
            run_id: str, run_at: str) -> dict:
    """Pull everything into a snapshot under `root/<run_id>`. Returns a manifest.

    `run_id` and `run_at` are REQUIRED and belong to the pipeline that owns the
    run, exactly as they do in `load.build_database` and for the same reason: an
    identity a module invents for itself cannot be tested for the value it
    stamps, and it cannot afterwards be matched against the build that consumed
    it. Passing the run's own id here is what ties `load_run` to its evidence.

    Nothing is overwritten. A second run with the same `run_id` rewrites that one
    snapshot; a different `run_id` is a different snapshot beside it.
    """
    out_dir = snapshot_dir(root, run_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    data: dict[str, list[dict]] = {}

    for name, sql in CENSUS_QUERIES.items():
        data[name] = ex.query(sql, f"census: {name}")
    for name, sql in STRUCTURE_QUERIES.items():
        data[name] = ex.query(sql, f"structure: {name}")

    scope = {"root_package_id": root_package_id, "package_ids": None,
             "max_depth": None, "truncated": False}
    if root_package_id is not None:
        ids, depth, truncated = resolve_scope(ex, root_package_id)
        scope.update({"package_ids": ids, "max_depth": depth, "truncated": truncated})
        in_scope = set(ids)
        data["object"] = [o for o in data["object"]
                          if _int(o.get("Package_ID")) in in_scope]
        guids = {o.get("ea_guid") for o in data["object"]}
        oids = {_int(o.get("Object_ID")) for o in data["object"]}
        data["objectproperties"] = [p for p in data["objectproperties"]
                                    if _int(p.get("Object_ID")) in oids]
        data["xref"] = [x for x in data["xref"] if x.get("Client") in guids]
        # Both endpoints must be in scope, or the edge dangles against `element`.
        data["connector"] = [c for c in data["connector"]
                             if _int(c.get("Start_Object_ID")) in oids
                             and _int(c.get("End_Object_ID")) in oids]
        data["attribute"] = [a for a in data["attribute"]
                             if _int(a.get("Object_ID")) in oids]
        data["operation"] = [o for o in data["operation"]
                             if _int(o.get("Object_ID")) in oids]
        data["diagram"] = [d for d in data["diagram"]
                           if _int(d.get("Package_ID")) in in_scope]
        dgm_ids = {_int(d.get("Diagram_ID")) for d in data["diagram"]}
        data["diagramobjects"] = [d for d in data["diagramobjects"]
                                  if _int(d.get("Diagram_ID")) in dgm_ids
                                  and _int(d.get("Object_ID")) in oids]

    for name, rows in data.items():
        (out_dir / f"{name}.json").write_text(
            json.dumps(rows, indent=1), encoding="utf-8", newline="\n")

    # The digest goes over the files as written, so it has to come after them.
    manifest = {
        "run_id": run_id,
        "run_at": run_at,
        "digest": snapshot_digest(out_dir),
        "scope": scope,
        "counts": {k: len(v) for k, v in sorted(data.items())},
        "sql_log": ex.sql_log,
    }
    (out_dir / MANIFEST_NAME).write_text(
        json.dumps(manifest, indent=2), encoding="utf-8", newline="\n")
    return manifest


def _int(v) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return -1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="./extracts",
                    help="snapshot root; this run lands in <out>/<run-id> "
                         "(default ./extracts)")
    ap.add_argument("--run-id", required=True,
                    help="identity for this snapshot. Pass the SAME value to "
                         "build_database so load_run records what it was built from")
    ap.add_argument("--run-at", required=True,
                    help="as-of timestamp for this snapshot, e.g. "
                         "'2026-10-05 14:30:00'. Supplied, never read off a clock")
    ap.add_argument("--keep", type=int, default=KEEP_RUNS,
                    help=f"retain this many snapshots (default {KEEP_RUNS})")
    ap.add_argument("--package-id", type=int, default=None,
                    help="restrict to this package subtree (default: whole repository)")
    ap.add_argument("--server-path", default=None,
                    help="path to the ea-mcp-server package, for the XML row parser")
    args = ap.parse_args(argv)

    if args.server_path:
        sys.path.insert(0, args.server_path)
    try:
        import win32com.client as w
        from ea_mcp_server.server import _parse_rows_from_sql_xml
    except ImportError as e:
        print(f"cannot reach EA or the row parser: {e}", file=sys.stderr)
        print("run this on a machine with EA and pywin32, and pass --server-path "
              "if ea_mcp_server is not importable", file=sys.stderr)
        return 2

    repo = w.GetActiveObject("EA.App").Repository
    ex = Extractor(repo, _parse_rows_from_sql_xml)
    manifest = extract(ex, args.out, args.package_id,
                       run_id=args.run_id, run_at=args.run_at)

    for k, v in manifest["counts"].items():
        print(f"  {k:<20} {v:>7} rows")
    s = manifest["scope"]
    if s["root_package_id"] is not None:
        print(f"\nscope: package {s['root_package_id']}, "
              f"{len(s['package_ids'])} packages, max depth {s['max_depth']}")
    total_ms = sum(e["ms"] for e in manifest["sql_log"])
    print(f"{len(manifest['sql_log'])} statements, {total_ms:.0f} ms")

    snap = snapshot_dir(args.out, args.run_id)
    print(f"\nsnapshot {args.run_id} retained at {snap}")
    print(f"  digest {manifest['digest']}")
    print("  pass extract_run_id and extract_digest to build_database so the "
          "build records what it was built from")

    # Pruning announces itself. A figure somebody quoted stops being defensible
    # the moment its evidence goes, so going is never quiet.
    removed = prune_snapshots(args.out, args.keep)
    retained = list_snapshots(args.out)
    print(f"\nretention: {len(retained)} snapshot(s) kept, limit {args.keep}, "
          f"{sum(s['bytes'] for s in retained) / 1024:.0f} KiB on disk")
    if removed:
        print(f"PRUNED {len(removed)} snapshot(s) - any figure quoted from these "
              f"builds can no longer be reproduced from its own rows:")
        for s in removed:
            print(f"  {s['run_id']}  taken {s['run_at']}  "
                  f"{s['bytes'] / 1024:.0f} KiB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
