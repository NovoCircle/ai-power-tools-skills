#!/usr/bin/env python3
"""Pull the rows a census and a reporting database need out of a live EA repository.

The one impure module in the set: it talks COM and writes files, and computes
nothing a pure module could. Bulk extraction runs here rather than through tool
calls, so the rows go to disk and never through a context window.

PORTABLE SQL ONLY: plain SELECTs, parenthesized joins, no CTEs and no window
functions. EA reports a statement its backend cannot run as a modal dialog that
holds the COM connection, so every later call appears to hang.

Each run writes a snapshot under its own `run_id`, built in
`<root>/.incomplete-<run_id>` and renamed into place once complete, and
`load_run` records which snapshot a build consumed, so a build can be replayed
without EA. Retention is bounded by `KEEP_RUNS` and `prune_snapshots` reports
everything it removes: snapshots that aged out, and leftover directories that
carry `SENTINEL_NAME`, which only this module writes. Anything else in the
store root is left alone, and no link is ever followed.

Run from a directory where EA is already running with the model open:

    python extract.py --out ./extracts --run-id <id> --run-at '<timestamp>'
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import stat
import sys
import time
from dataclasses import dataclass
from datetime import datetime

#: Every query orders its rows totally - by a key, by grouping columns plus a
#: key, or by every selected column - so two extracts of an unchanged repository
#: write identical files and hash the same. Long-text columns are not sorted on:
#: t_xref orders by XrefID and t_objectproperties by PropertyID. `resolve_scope`'s
#: statement is ordered too, and `test_every_shipped_query_orders_its_rows`
#: checks every statement.

#: Rows pulled whole. Small, repository-wide, and needed by the census.
CENSUS_QUERIES = {
    "object": ("SELECT Object_ID, ea_guid, Name, Object_Type, Stereotype, Package_ID "
               "FROM t_object ORDER BY Object_ID"),
    "xref": ("SELECT Client, Description FROM t_xref WHERE Name = 'Stereotypes' "
             "ORDER BY Client, XrefID"),
    "objectproperties": ("SELECT Object_ID, Property, Value FROM t_objectproperties "
                         "ORDER BY Object_ID, Property, PropertyID"),
    "package": "SELECT Package_ID, Parent_ID, Name FROM t_package ORDER BY Package_ID",
}

#: Structural content. Column names and reserved-word brackets are read from
#: EA's schema rather than guessed: t_attribute needs [Type], [Scope], [Default];
#: t_operation needs [Type], [Scope]; and t_diagram's type column is
#: Diagram_Type, NOT Type. Its primary key is Diagram_ID, where t_attribute's is
#: ID and t_operation's is OperationID.
#: t_connector carries ea_guid so a connector's stereotype provenance can be
#: looked up in t_xref - without it `rel_all.profile` could only ever be empty.
STRUCTURE_QUERIES = {
    "attribute": ("SELECT ID, Object_ID, Name, [Type], [Scope] FROM t_attribute "
                  "ORDER BY Object_ID, ID"),
    "operation": ("SELECT OperationID, Object_ID, Name, [Type], [Scope] "
                  "FROM t_operation ORDER BY Object_ID, OperationID"),
    "diagram": ("SELECT Diagram_ID, Name, Diagram_Type, Package_ID FROM t_diagram "
                "ORDER BY Package_ID, Diagram_ID"),
    "diagramobjects": ("SELECT Diagram_ID, Object_ID FROM t_diagramobjects "
                       "ORDER BY Diagram_ID, Object_ID"),
    "connector": ("SELECT Connector_ID, ea_guid, Name, Connector_Type, Stereotype, "
                  "Start_Object_ID, End_Object_ID FROM t_connector "
                  "ORDER BY Connector_ID"),
    "connectortag": ("SELECT PropertyID, ElementID, Property, [VALUE] "
                     "FROM t_connectortag ORDER BY ElementID, Property, PropertyID"),
}


#: Every table a snapshot holds, which is also what its digest covers.
TABLE_NAMES = tuple(CENSUS_QUERIES) + tuple(STRUCTURE_QUERIES)

MANIFEST_NAME = "extract-manifest.json"

#: Written into every directory this module creates, before anything else, and
#: deleted last when one is removed. The sweep in `prune_snapshots` removes only
#: directories that carry it. Not a `.json` name, so it is not a table file and
#: not covered by the digest.
SENTINEL_NAME = ".extract-snapshot"

#: A snapshot is written under this prefix and renamed into place only once it is
#: complete. The prefix is not a valid `run_id`, so an in-progress or abandoned
#: write can never be mistaken for a snapshot.
INCOMPLETE_PREFIX = ".incomplete-"

#: A snapshot being REPLACED by a re-run of its own `run_id` is renamed under this
#: prefix before the new one is renamed into place, and deleted only afterwards.
#: Also not a valid `run_id`, for the same reason, and swept by `prune_snapshots`
#: if deleting it fails - so the replacement never leaves the store unbounded.
SUPERSEDED_PREFIX = ".superseded-"

#: How many snapshots are retained. On the reference model of about 300 elements
#: a snapshot is about 244 KiB, so ten runs are about 2.4 MiB. Retention has no
#: off switch.
KEEP_RUNS = 10


class SnapshotError(Exception):
    """A retained extract could not be produced as asked, or the store cannot be written safely.

    Raised for a snapshot that is missing or whose rows differ from what the build
    recorded, a `run_id` that is unusable or differs only in case from one in the
    store, two directories claiming one `run_id`, and a finished extract that could
    not be moved into place.
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


#: A `run_id` names one directory under the snapshot root. It is validated because
#: it also comes back out of `_load_run` at replay time, and a path would write
#: outside the root, where retention cannot see it. It may not end in a dot,
#: which Windows strips, giving a directory named differently from its manifest.
_RUN_ID = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9._-]{0,62}[A-Za-z0-9_-])?")

#: The one `run_at` format. Retention orders snapshots by sorting this string.
_RUN_AT = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}")


def validate_run_id(run_id: str) -> str:
    """The `run_id`, or `SnapshotError`.

    One path component of letters, digits, dot, dash or underscore, starting with a
    letter or digit and not ending in a dot.
    """
    if not isinstance(run_id, str) or not _RUN_ID.fullmatch(run_id):
        raise SnapshotError(
            f"run_id {run_id!r} is not usable as a snapshot name: it has to be a "
            f"single path component of letters, digits, dot, dash or underscore, "
            f"starting with a letter or digit and not ending in a dot. A run_id "
            f"that is a path writes the snapshot outside the root, where "
            f"retention cannot see it and so never prunes it, while a replay "
            f"still loads it; a run_id ending in a dot names a directory the "
            f"filesystem then calls something else, which stops retention for "
            f"the whole store.")
    return run_id


def validate_new_run_id(root, run_id: str) -> str:
    """`validate_run_id`, plus a refusal of a case-only collision with the store.

    A `run_id` that differs only in case from a directory already in the store,
    prefixed or not, is refused before anything is written: NTFS does not
    distinguish case, so writing it would replace that directory's rows under
    another name. The `run_id` is kept as given rather than case-folded, because it
    is recorded verbatim in the manifest and in `_load_run`.
    """
    validate_run_id(run_id)
    root = pathlib.Path(root)
    folded = run_id.casefold()
    for d in sorted(root.iterdir()) if root.is_dir() else []:
        if not d.is_dir():
            continue
        # A prefixed directory belongs to the run_id after its prefix.
        names = [d.name] + [d.name[len(p):] for p in
                            (INCOMPLETE_PREFIX, SUPERSEDED_PREFIX)
                            if d.name.startswith(p)]
        if run_id not in names and any(n.casefold() == folded for n in names):
            # `names[-1]` is the run_id the directory belongs to.
            raise SnapshotError(
                f"run_id {run_id!r} differs only in case from {d.name!r}, which "
                f"is already in {root}, and the filesystem does not tell the two "
                f"apart: writing this one would replace that snapshot's rows "
                f"while retention went on reporting it under its own name, and a "
                f"replay of the earlier build would report the substitution as "
                f"tampering. Pass {names[-1]!r} to re-run that extract, or a "
                f"run_id that differs by more than case.")
    return run_id


def validate_run_at(run_at: str) -> str:
    """The `run_at`, or `ValueError`: exactly `YYYY-MM-DD HH:MM:SS`, a real date and time.

    Retention orders snapshots by sorting this string, so another format would sort
    wrongly against the rest.
    """
    if not isinstance(run_at, str) or not _RUN_AT.fullmatch(run_at):
        raise ValueError(
            f"run_at {run_at!r} is not 'YYYY-MM-DD HH:MM:SS' - the one format the "
            f"documentation promises and the only one retention can order. "
            f"Retained snapshots are sorted by this string, so a different format "
            f"sorts wrongly against the others and the sort decides what is "
            f"deleted.")
    try:
        datetime.strptime(run_at, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise ValueError(
            f"run_at {run_at!r} has the right shape but is not a real date and "
            f"time, so it is not an as-of date anything can be quoted against."
        ) from None
    return run_at


def snapshot_dir(root, run_id: str) -> pathlib.Path:
    """The one directory a snapshot lives in. `run_id` is validated, not trusted."""
    return pathlib.Path(root) / validate_run_id(run_id)


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


def _read_manifest(d: pathlib.Path) -> dict | None:
    """The manifest in `d`, or None if it is missing or is not an object with a
    string `run_at`. Raises `OSError` if it exists and cannot be read.
    """
    try:
        man = json.loads((d / MANIFEST_NAME).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except ValueError:
        return None
    if not isinstance(man, dict) or not isinstance(man.get("run_at"), str):
        return None
    return man


def _is_link(p: pathlib.Path) -> bool:
    """A symlink, or on Windows any reparse point, which includes a junction."""
    if p.is_symlink():
        return True
    try:
        attributes = getattr(os.lstat(p), "st_file_attributes", 0)
    except OSError:
        return False
    return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def list_snapshots(root) -> list[dict]:
    """Retained snapshots, newest first, as `{run_id, run_at, bytes, dir}`.

    `dir` is the directory walked and `run_id` its name, never a path built from
    the manifest, which the digest does not cover. Ordered by the manifest's
    `run_at`, not by file time. A directory whose name is not a valid `run_id`, or
    whose manifest is not readable, is skipped. A readable manifest naming a
    different `run_id` raises `SnapshotError`.
    """
    root = pathlib.Path(root)
    if not root.is_dir():
        return []
    out = []
    for d in sorted(root.iterdir()):
        manifest = d / MANIFEST_NAME
        if not (d.is_dir() and not _is_link(d) and manifest.is_file()
                and _RUN_ID.fullmatch(d.name)):
            continue
        # A missing or malformed manifest makes the directory not a snapshot, and
        # one that cannot be read now is skipped; neither stops the rest of the
        # store being read. A readable one naming another run_id does.
        try:
            man = _read_manifest(d)
        except OSError:
            continue
        if man is None:
            continue
        if man.get("run_id") != d.name:
            raise SnapshotError(
                f"snapshot directory {d.name!r} under {root} holds a manifest "
                f"naming {man.get('run_id')!r}. Nothing here will guess which is "
                f"right: a replay can only ever find this snapshot as "
                f"{d.name!r}, so retention acting on the manifest's name would "
                f"delete a different snapshot and report this one. Rename the "
                f"directory to its own run_id, or remove the copy.")
        out.append({
            "run_id": d.name,
            "run_at": man["run_at"],
            "bytes": sum(f.stat().st_size for f in d.iterdir() if f.is_file()),
            "dir": d,
        })
    return sorted(out, key=lambda s: (s["run_at"], s["run_id"]), reverse=True)


#: Both helpers below make up to `_ATTEMPTS` attempts, `_BACKOFF_SECONDS` apart,
#: then let the caller decide. On Windows a delete or rename fails while another
#: process holds a file inside the directory.
_ATTEMPTS = 4
_BACKOFF_SECONDS = 0.25


def _reclaim(directory) -> bool:
    """Delete `directory` with `_remove_tree`, retrying. True if it went, False if not.

    A link is refused, never followed. Never raises, so a caller removing several
    directories can report the one that would not go and carry on.
    """
    if _is_link(pathlib.Path(directory)):
        return False
    for attempt in range(_ATTEMPTS):
        try:
            _remove_tree(pathlib.Path(directory))
            return True
        except OSError:
            if attempt == _ATTEMPTS - 1:
                return False
            time.sleep(_BACKOFF_SECONDS)
    return False


def _remove_tree(directory: pathlib.Path) -> None:
    """Delete `directory`, its marker last. Stops at the first refusal.

    Deleting the marker last means a delete that is refused part-way leaves a
    directory that still carries it, so the next sweep can recognize and
    remove what is left.
    """
    marker = directory / SENTINEL_NAME
    for child in sorted(directory.iterdir()):
        if child == marker:
            continue
        if _is_link(child):
            raise OSError(f"{child} is a link, which is never followed")
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    if marker.exists():
        marker.unlink()
    directory.rmdir()


def _rename(src: pathlib.Path, dst: pathlib.Path) -> None:
    """`src.rename(dst)`, retried. Raises the last `OSError` if it will not go.

    Raises rather than returning a flag because every caller has to decide what
    to put back, and that decision is different at each step of the commit.
    """
    for attempt in range(_ATTEMPTS):
        try:
            src.rename(dst)
            return
        except OSError:
            if attempt == _ATTEMPTS - 1:
                raise
            time.sleep(_BACKOFF_SECONDS)


def _is_debris(d: pathlib.Path) -> bool:
    """Whether the sweep may remove `d`.

    Only a directory this module wrote: one carrying `SENTINEL_NAME`. Under
    one of the two prefixes it is removed whatever it holds; under any other
    name only when its manifest is missing or is not an object with a string
    `run_at`. An empty directory under a prefix is removed too, which is what a
    run killed between creating its work directory and writing the marker
    leaves. A link is never removed. Raises `OSError` if the manifest exists
    and cannot be read, and the caller leaves the directory alone.
    """
    if _is_link(d):
        return False
    prefixed = d.name.startswith((INCOMPLETE_PREFIX, SUPERSEDED_PREFIX))
    if prefixed and not any(d.iterdir()):
        return True
    if not (d / SENTINEL_NAME).is_file():
        return False
    return prefixed or _read_manifest(d) is None


def _debris_status(name: str) -> str:
    """Why a directory in the store is not a snapshot, for the prune report."""
    if name.startswith(INCOMPLETE_PREFIX):
        return "incomplete"
    if name.startswith(SUPERSEDED_PREFIX):
        return "superseded"
    return "unreadable"


#: What a swept directory is reported as: one sentence per status
#: `_debris_status` returns, each saying only what the code checked.
_SWEPT_REASON = {
    "incomplete": "a write under this tool's in-progress prefix that no run "
                  "renamed into place.",
    "superseded": "rows renamed aside under this tool's replacement prefix for "
                  "a re-run of that run_id, and not deleted at the time.",
    "unreadable": "a directory this tool wrote that has no loadable manifest, "
                  "so nothing here can open it as a snapshot.",
}


def prune_snapshots(root, keep: int = KEEP_RUNS, *, protect=()) -> list[dict]:
    """Delete all but the newest `keep` snapshots, and this tool's debris.

    Returns what it removed, each entry with a `status`:

      `pruned`      a snapshot that aged out.
      `incomplete`  a `.incomplete-*` directory no run renamed into place.
      `superseded`  a `.superseded-*` directory left by a replacement. Usually a
                    copy of rows a re-run replaced; after a failed putback in
                    `_commit` it is the only copy.
      `unreadable`  a directory this tool wrote that has no loadable manifest.
      `held`        it could not be fully removed, and what is left is on disk. It
                    may no longer be loadable: a refused delete stops at the file it
                    cannot remove, after removing the ones before it.

    What goes is a directory `list_snapshots` walked, or one `_is_debris` accepts.
    Anything else in the root is left alone and not reported, and so is a
    directory whose manifest cannot be read at the moment. A protected `run_id`
    is never removed.

    `protect` is a collection of run_ids that are never pruned; a bare string is
    refused. Pass the run just written: order is a sort over a supplied `run_at`, so
    a backfilled run would otherwise sort oldest. Protected snapshots are kept on
    top of `keep`. A second extract writing to the same root at the same time is not
    supported.
    """
    if keep < 1:
        raise ValueError(f"keep must be at least 1, got {keep!r}")
    if isinstance(protect, str):
        raise ValueError(
            f"protect takes a collection of run_ids, not the string {protect!r}: "
            f"a bare string iterates into its characters, so it protects nothing "
            f"and the snapshot it names is deleted with no error and nothing in "
            f"the report. Pass ({protect!r},).")
    protected = {str(p) for p in protect}
    snapshots = list_snapshots(root)
    # Decided before anything is deleted: a refused removal can take the manifest
    # with it, and the sweep must not report the same directory a second time.
    was_a_snapshot = {s["dir"] for s in snapshots}
    removed = []
    for snap in snapshots[keep:]:
        if snap["run_id"] in protected:
            continue
        gone = _reclaim(snap["dir"])
        removed.append(dict(snap, status="pruned" if gone else "held"))

    root = pathlib.Path(root)
    for d in sorted(root.iterdir()) if root.is_dir() else []:
        if not d.is_dir() or d in was_a_snapshot or d.name in protected:
            continue
        try:
            if not _is_debris(d):
                continue
        except OSError:
            continue
        status = _debris_status(d.name)
        # The whole tree, not only the top level.
        entry = {"run_id": d.name, "run_at": "",
                 "bytes": sum(f.stat().st_size
                              for f in d.rglob("*") if f.is_file()),
                 "dir": d, "status": status}
        if not _reclaim(d):
            entry["status"] = "held"
        removed.append(entry)
    return removed


def open_snapshot(root, run_id: str, *, expect_digest: str | None = None) -> Snapshot:
    """Reopen the retained extract named `run_id`, or raise `SnapshotError`.

    Looks only at that run_id's directory. Refuses a snapshot that is missing,
    naming what is retained or where a failed commit left its rows; one whose
    manifest names a different `run_id`; one whose files no longer match its own
    manifest's digest; and one that does not match `expect_digest`.

    `expect_digest=None` means there is no recorded digest to check yet, as for the
    first build reading the extract it has just taken. An empty string is refused
    rather than treated as no check.
    """
    directory = snapshot_dir(root, run_id)
    manifest_path = directory / MANIFEST_NAME
    if not manifest_path.is_file():
        # Before saying pruned, look under this run_id's prefixes, where a failed
        # commit leaves its rows.
        root = pathlib.Path(root)
        aside = [p for p in (root / f"{SUPERSEDED_PREFIX}{run_id}",
                             root / f"{INCOMPLETE_PREFIX}{run_id}") if p.is_dir()]
        if aside:
            raise SnapshotError(
                f"extract snapshot {run_id!r} is not retained under {root}, but "
                f"its rows are: {', '.join(p.name for p in aside)}. A run of this "
                f"run_id could not be committed and could not put back what it "
                f"moved aside, so nothing is under the snapshot name. Nothing "
                f"has been deleted. Rename "
                f"{SUPERSEDED_PREFIX}{run_id} to {run_id} to restore what was "
                f"retained, or {INCOMPLETE_PREFIX}{run_id} to complete that run - "
                f"and do it before the next prune, which reclaims both.")
        retained = [s["run_id"] for s in list_snapshots(root)] or ["none"]
        raise SnapshotError(
            f"extract snapshot {run_id!r} is not retained under {root}: it has "
            f"been pruned, or was never kept. Retained now: "
            f"{', '.join(retained)}. The build that consumed it cannot be "
            f"replayed, and no other snapshot is a substitute for it - a figure "
            f"quoted from that build can only be reproduced from its own rows.")

    manifest = _read_manifest(directory)
    if manifest is None:
        raise SnapshotError(
            f"extract snapshot {run_id!r} under {root} has a manifest that is not "
            f"an object with a run_at, so it cannot be replayed.")
    # The directory/manifest agreement `list_snapshots` enforces: the caller
    # records this run_id as the build's provenance.
    named = manifest.get("run_id") if isinstance(manifest, dict) else None
    if named != run_id:
        raise SnapshotError(
            f"extract snapshot {run_id!r} under {root} holds a manifest naming "
            f"{named!r}. Nothing here will "
            f"guess which is right: a build that recorded {run_id!r} can only "
            f"ever find it under that name, so replaying this would record "
            f"provenance naming a directory it did not read. Rename the "
            f"directory to its own run_id, or remove the copy.")
    digest = snapshot_digest(directory)
    if digest != manifest["digest"]:
        raise SnapshotError(
            f"extract snapshot {run_id!r} does not match the digest in its own "
            f"manifest ({digest} vs {manifest['digest']}): its files have been "
            f"changed since it was written, so it is no longer evidence of "
            f"anything.")
    if expect_digest is not None:
        if not expect_digest:
            raise SnapshotError(
                f"no digest was recorded for extract snapshot {run_id!r}, so a "
                f"replay from it cannot be verified and is refused. An empty "
                f"digest is not a digest: the check it would skip is the one that "
                f"tells this extract from a different one left under the same "
                f"run_id, and a figure quoted from an unverifiable replay carries "
                f"provenance that looks checked and is not.")
        if digest != expect_digest:
            raise SnapshotError(
                f"extract snapshot {run_id!r} hashes to {digest}, but the build "
                f"recorded {expect_digest}. This is a different extract under the "
                f"same run_id; refusing to replay from it.")

    tables = {name: json.loads((directory / f"{name}.json").read_text(
        encoding="utf-8")) for name in TABLE_NAMES}
    return Snapshot(run_id=run_id, run_at=manifest["run_at"],
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
    """Package ids in the subtree under `root_package_id`, walked host-side.

    Returns (package_ids, max_depth_reached, truncated). Host-side because
    recursive CTEs are not portable. There is no depth cap; the `seen` set guards
    against a cycle.
    """
    rows = ex.query("SELECT Package_ID, Parent_ID FROM t_package "
                    "ORDER BY Package_ID", "scope: t_package")
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
    """Pull everything into a snapshot under `root/<run_id>`. Returns its manifest.

    `run_id` and `run_at` are required and belong to the run's pipeline, as in
    `load.build_database`, so `load_run` can be tied to its evidence. A re-run of a
    `run_id` replaces that snapshot. A `run_id` differing from one in the store only
    in case is refused (`validate_new_run_id`).

    The snapshot is written in `<root>/.incomplete-<run_id>`, marked with
    `SENTINEL_NAME` first, and renamed into place by `_commit` once its manifest is
    written. Both arguments and the case collision are checked before any query is
    issued.
    """
    validate_run_at(run_at)
    validate_new_run_id(root, run_id)
    out_dir = snapshot_dir(root, run_id)
    work_dir = pathlib.Path(root) / f"{INCOMPLETE_PREFIX}{run_id}"
    if work_dir.exists() and not _reclaim(work_dir):
        raise SnapshotError(
            f"{work_dir} is left over from an earlier run of this run_id and "
            f"could not be removed. No query has been issued. Remove the "
            f"directory, or whatever is preventing its removal, and run "
            f"again.")
    try:
        work_dir.mkdir(parents=True)
        (work_dir / SENTINEL_NAME).write_text("", encoding="utf-8")
    except OSError as e:
        if work_dir.is_dir():
            _reclaim(work_dir)
        raise SnapshotError(
            f"the snapshot work directory {work_dir} could not be created "
            f"({e}), so no extract was taken.") from None
    try:
        manifest = _extract_into(ex, work_dir, root_package_id,
                                 run_id=run_id, run_at=run_at)
    except BaseException:
        _reclaim(work_dir)
        raise
    _commit(work_dir, out_dir)
    return manifest


def _commit(work_dir: pathlib.Path, out_dir: pathlib.Path) -> None:
    """Move a finished snapshot into place.

    A re-run replaces a retained snapshot by renaming it aside to
    `.superseded-<run_id>`, renaming the new one into place, and only then deleting
    the aside, so no moment holds neither. If the new one cannot be renamed into
    place, the aside is put back. Each failure raises `SnapshotError` saying which
    directory holds which rows and which rename recovers them.

    If the putback fails as well, nothing is under `<run_id>`: the retained rows are
    under `.superseded-<run_id>`, the new ones under `.incomplete-<run_id>`, and the
    next prune reclaims both. A `.superseded-<run_id>` left by an earlier
    replacement is deleted before the aside is made.
    """
    aside = None
    if out_dir.exists():
        aside = out_dir.with_name(f"{SUPERSEDED_PREFIX}{out_dir.name}")
        if aside.exists() and not _reclaim(aside):
            raise SnapshotError(
                f"the extract finished but {aside} is still there from an earlier "
                f"replacement of {out_dir.name} and could not be removed, so the "
                f"snapshot retained as {out_dir.name} cannot be moved aside. "
                f"Nothing has been deleted: that snapshot is untouched and the "
                f"new rows are intact under {work_dir.name}. Remove {aside.name} "
                f"and rename {work_dir.name} to {out_dir.name}, or run again.")
        try:
            _rename(out_dir, aside)
        except OSError as e:
            raise SnapshotError(
                f"the extract finished but the snapshot already retained as "
                f"{out_dir} could not be moved aside ({e}). Nothing has been "
                f"deleted - that "
                f"snapshot is still readable and still replayable - and the new "
                f"rows are intact under {work_dir.name}. Close whatever has it "
                f"open and rename {work_dir.name} to {out_dir.name}, or run "
                f"again. Until then nothing reads the new rows, and pruning will "
                f"reclaim them.") from None
    try:
        _rename(work_dir, out_dir)
    except OSError as e:
        if aside is not None:
            # The aside is the only copy of those rows, so it is put back first.
            try:
                _rename(aside, out_dir)
            except OSError as putback:
                raise SnapshotError(
                    f"the extract finished, {work_dir} could not be renamed to "
                    f"{out_dir} ({e}), and the snapshot that was moved aside to "
                    f"{aside} could not be put back either ({putback}). Nothing "
                    f"has been deleted: BOTH sets of rows are on disk, the "
                    f"retained ones under {aside.name} and the new ones under "
                    f"{work_dir.name}. Rename one of them to {out_dir.name} - "
                    f"{aside.name} restores what was retained, {work_dir.name} "
                    f"completes this run. DO IT BEFORE THE NEXT PRUNE: nothing "
                    f"is retained under {out_dir.name} until one of them is "
                    f"renamed, so retention cannot see either and pruning will "
                    f"reclaim BOTH.") from None
        raise SnapshotError(
            f"the extract finished but {work_dir} could not be renamed to "
            f"{out_dir} ({e}). "
            f"The rows are intact under that name - rename the directory "
            f"to {out_dir.name} to retain the snapshot. Until then nothing "
            f"reads it, and pruning will reclaim it.") from None
    if aside is not None:
        # The commit has succeeded. An aside that will not go is swept by the next
        # prune as `superseded`.
        _reclaim(aside)


def _extract_into(ex: Extractor, out_dir: pathlib.Path,
                  root_package_id: int | None, *, run_id: str, run_at: str) -> dict:
    """Query, filter to scope, and write one complete snapshot into `out_dir`."""
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
        "sql_log": list(ex.sql_log),
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

    # Checked before EA is reached: a bad value found after the COM round trip is
    # found too late.
    try:
        validate_new_run_id(args.out, args.run_id)
        validate_run_at(args.run_at)
        if args.keep < 1:
            raise ValueError(f"--keep must be at least 1, got {args.keep!r}: "
                             f"keeping none is a deletion, not a retention policy")
    except (SnapshotError, ValueError) as e:
        print(e, file=sys.stderr)
        return 2

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
    try:
        manifest = extract(ex, args.out, args.package_id,
                           run_id=args.run_id, run_at=args.run_at)
    except SnapshotError as e:
        # The message says where the rows are.
        print(e, file=sys.stderr)
        return 2
    except Exception as e:
        # Nothing was retained, which is what 2 means. Exit 1 means a retained
        # snapshot whose retention failed.
        print(f"the extract did not complete: {type(e).__name__}: {e}",
              file=sys.stderr)
        print("Nothing was retained and no digest was printed, so this build has "
              "nothing to record and must not claim it does. Exit 1 would have "
              "said the snapshot IS retained; on this path it is not.", file=sys.stderr)
        return 2

    for k, v in manifest["counts"].items():
        print(f"  {k:<20} {v:>7} rows")
    scope = manifest["scope"]
    if scope["root_package_id"] is not None:
        print(f"\nscope: package {scope['root_package_id']}, "
              f"{len(scope['package_ids'])} packages, max depth {scope['max_depth']}")
    total_ms = sum(e["ms"] for e in manifest["sql_log"])
    print(f"{len(manifest['sql_log'])} statements, {total_ms:.0f} ms")

    # The reference is printed before retention runs, so a problem elsewhere in the
    # store cannot cost this run its digest. `protect` keeps this run from being
    # pruned.
    print(f"\nsnapshot {args.run_id} retained at "
          f"{snapshot_dir(args.out, args.run_id)}")
    print(f"  digest {manifest['digest']}")
    print("  pass extract_run_id and extract_digest to build_database so the "
          "build records what it was built from")

    try:
        removed = prune_snapshots(args.out, args.keep, protect=(args.run_id,))
        retained = list_snapshots(args.out)
    except (SnapshotError, ValueError, OSError) as e:
        print(f"\nretention did not run: {e}", file=sys.stderr)
        print("The snapshot above IS retained and its digest is printed above, "
              "so this build can still record what it was built from. But the "
              "store was not pruned, so retention is not bounded until this is "
              "dealt with.", file=sys.stderr)
        return 1

    # Pruning is always reported.
    print(f"\nretention: {len(retained)} snapshot(s) kept, limit {args.keep}, "
          f"{sum(s['bytes'] for s in retained) / 1024:.0f} KiB on disk")
    pruned = [s for s in removed if s["status"] == "pruned"]
    if pruned:
        print(f"PRUNED {len(pruned)} snapshot(s) - any figure quoted from these "
              f"builds can no longer be reproduced from its own rows:")
        for s in pruned:
            print(f"  {s['run_id']}  taken {s['run_at']}  "
                  f"{s['bytes'] / 1024:.0f} KiB")
    for s in removed:
        if s["status"] in _SWEPT_REASON:
            print(f"SWEPT {s['run_id']} ({s['bytes'] / 1024:.0f} KiB) - "
                  f"{_SWEPT_REASON[s['status']]} No function here reads it, and "
                  f"left alone it would never have been reclaimed.")
    held = [s for s in removed if s["status"] == "held"]
    if held:
        print(f"HELD: {len(held)} director(ies) retention meant to remove COULD "
              f"NOT BE FULLY REMOVED. "
              f"What is left of each is on disk and may no longer be loadable, "
              f"because a refused delete stops at the file it cannot remove "
              f"after deleting everything ahead of it. The store stays over its "
              f"bound until they go:", file=sys.stderr)
        for s in held:
            print(f"  {s['dir']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
