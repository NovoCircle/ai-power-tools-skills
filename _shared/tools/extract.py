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

Run from a directory where EA is already running with the model open:

    python extract.py --out ./out [--package-id 4]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import time

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
STRUCTURE_QUERIES = {
    "attribute": "SELECT ID, Object_ID, Name, [Type], [Scope] FROM t_attribute",
    "operation": "SELECT OperationID, Object_ID, Name, [Type], [Scope] FROM t_operation",
    "diagram": "SELECT Diagram_ID, Name, Diagram_Type, Package_ID FROM t_diagram",
    "diagramobjects": "SELECT Diagram_ID, Object_ID FROM t_diagramobjects",
    "connector": ("SELECT Connector_ID, Name, Connector_Type, Stereotype, "
                  "Start_Object_ID, End_Object_ID FROM t_connector"),
    "connectortag": "SELECT PropertyID, ElementID, Property, [VALUE] FROM t_connectortag",
}


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


def extract(ex: Extractor, out_dir: pathlib.Path,
            root_package_id: int | None = None) -> dict:
    """Pull everything and write it to `out_dir`. Returns a manifest."""
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

    manifest = {
        "scope": scope,
        "counts": {k: len(v) for k, v in sorted(data.items())},
        "sql_log": ex.sql_log,
    }
    (out_dir / "extract-manifest.json").write_text(
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
    ap.add_argument("--out", default="./out", help="output directory (default ./out)")
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
    manifest = extract(ex, pathlib.Path(args.out), args.package_id)

    for k, v in manifest["counts"].items():
        print(f"  {k:<20} {v:>7} rows")
    s = manifest["scope"]
    if s["root_package_id"] is not None:
        print(f"\nscope: package {s['root_package_id']}, "
              f"{len(s['package_ids'])} packages, max depth {s['max_depth']}")
    total_ms = sum(e["ms"] for e in manifest["sql_log"])
    print(f"{len(manifest['sql_log'])} statements, {total_ms:.0f} ms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
