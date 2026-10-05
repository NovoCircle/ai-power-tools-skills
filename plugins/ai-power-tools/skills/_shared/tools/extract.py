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

Bounded means bounded even when a run dies, which is why a snapshot is built in
`<root>/.incomplete-<run_id>` and renamed into place only once it is complete: a
killed extract - the modal dialog above is exactly how one gets killed - leaves
no half-written directory under a snapshot name. A directory no function can see
is a directory that is never reclaimed, and that is an unbounded store by another
route, so `prune_snapshots` sweeps and reports EVERY directory in the store that
is not a loadable snapshot - not only the ones written under a prefix it put
there. Debris does not only arrive by the route that was designed for it: a prune
stopped by a held file leaves a plain-named husk whose manifest has already gone,
and a sweep that matched a prefix walked straight past it.

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
from datetime import datetime

#: EVERY QUERY ORDERS ITS ROWS, and that is what makes the digest mean what the
#: documentation says it means: "two extracts of an unchanged repository hash the
#: same". Without an ORDER BY no backend promises an order, so the same rows could
#: be written in a different sequence and hash differently - and a customer would
#: read row-order churn as model change, the exact misreading the as-of-date
#: discipline exists to prevent.
#:
#: Each ORDER BY is a TOTAL order: either a primary key, or the grouping columns
#: plus a key, or every selected column (where ties are then byte-identical rows,
#: so their order cannot change the file). Long-text columns are deliberately NOT
#: sorted on - t_xref.Description is a memo, and a backend that refuses to sort
#: one reports it as the modal dialog described above - so t_xref orders by XrefID
#: and t_objectproperties by PropertyID, neither of which the projection selects.
#: t_objectproperties especially: it has no unique index on (Object_ID, Property),
#: one element can carry two tags of the same name with different values, and
#: which of them came first was previously whatever the backend felt like.

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

#: A snapshot is written under this prefix and renamed into place only once it is
#: complete. The prefix is not a valid `run_id`, so an in-progress or abandoned
#: write can never be mistaken for a snapshot.
INCOMPLETE_PREFIX = ".incomplete-"

#: A snapshot being REPLACED by a re-run of its own `run_id` is renamed under this
#: prefix before the new one is renamed into place, and deleted only afterwards.
#: Also not a valid `run_id`, for the same reason, and swept by `prune_snapshots`
#: if deleting it fails - so the replacement never leaves the store unbounded.
SUPERSEDED_PREFIX = ".superseded-"

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

    Also for the four ways the store itself can stop making sense: a `run_id`
    that is not one safe path component, a `run_id` the filesystem cannot tell
    from one already there, two directories claiming one `run_id`, and a finished
    extract that could not be moved into place. Each of them would otherwise be
    answered by a guess about which evidence was meant - and the last two are
    answered on a platform where a delete or a rename can simply be refused, so
    they are raised only once the store has been left holding whole snapshots.
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


#: A `run_id` names ONE directory under the snapshot root and nothing else.
#: Validated rather than trusted, because it does not only come from an operator's
#: `--run-id`: at replay time it comes out of `_load_run` in a database file that
#: may have traveled. Unvalidated, `..\escaped` writes outside the root and an
#: absolute run_id escapes it entirely - pathlib discards the left operand on an
#: absolute right operand - leaving a snapshot that `open_snapshot` still loads
#: while `list_snapshots` cannot see it, so it is never pruned. That is both a
#: path traversal and the unbounded store the acceptance criteria rule out.
#:
#: A TRAILING DOT is not one safe path component on Windows, which is the platform
#: this module documents itself as running on: the Win32 path layer strips it, so
#: `run.` is accepted here and creates a directory called `run`. Observed - the
#: manifest then names `run.` while the directory is `run`, which is the two-names
#: refusal in `list_snapshots`, so from that moment every `list_snapshots`,
#: `prune_snapshots` and retention report raises for the WHOLE store and retention
#: stops: unbounded again, and every later run dies before printing its digest.
_RUN_ID = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9._-]{0,62}[A-Za-z0-9_-])?")

#: The one `run_at` format the documentation promises. Validated because it is not
#: decoration: retention order is a lexicographic sort over this string, so
#: `2026-10-05T08:00:00` and `05/10/2026` both sort wrongly against space-separated
#: values - and the sort decides what gets DELETED.
_RUN_AT = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}")


def validate_run_id(run_id: str) -> str:
    """The `run_id`, or `SnapshotError`. One safe path component, nothing else.

    One component the PLATFORM agrees is one component: it may not end in a dot,
    because Windows silently strips that and hands back a directory under a
    different name than the manifest records (see `_RUN_ID`).
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
    """The `run_id` for a NEW extract, or `SnapshotError`.

    `validate_run_id`, plus the one check that needs the store to answer it: a
    `run_id` differing only in CASE from a directory already there is refused.

    THE DECISION, made explicitly because the two answers are not equivalent:
    the store keeps a `run_id` exactly as it was given and refuses a collision,
    rather than case-folding names. `run_id` is recorded verbatim in the manifest
    and in `_load_run.extract_run_id`, and `list_snapshots` refuses a directory
    whose manifest names a different `run_id` - so folding the directory name
    would put every snapshot in disagreement with its own manifest, and folding
    the recorded value too would mean a build's provenance cell no longer holds
    what the operator passed to it. Refusing keeps one `run_id` meaning one
    directory and one identity, and it refuses before anything is written.

    Unrefused this is silent destruction, not a cosmetic problem. `_RUN_ID` is
    case-sensitive, NTFS is not, and neither is `Path.exists`, so `Run-A` and
    `run-a` are two accepted run_ids and one directory. Observed: after the
    second run only `run-a` was on disk, `Run-A`'s rows were nowhere,
    `prune_snapshots` reported `[]` and `list_snapshots` showed one snapshot
    where the operator believed there were two, and the first build's replay
    reported "hashes to X, but the build recorded Y" - which this module's own
    refusal table defines as a DIFFERENT extract under the same `run_id`, i.e.
    tampering. Evidence destroyed, destruction unreported, cause misattributed.
    """
    validate_run_id(run_id)
    root = pathlib.Path(root)
    folded = run_id.casefold()
    for d in sorted(root.iterdir()) if root.is_dir() else []:
        if d.is_dir() and d.name != run_id and d.name.casefold() == folded:
            raise SnapshotError(
                f"run_id {run_id!r} differs only in case from {d.name!r}, which "
                f"is already in {root}, and the filesystem does not tell the two "
                f"apart: writing this one would replace that snapshot's rows "
                f"while retention went on reporting it under its own name, and a "
                f"replay of the earlier build would report the substitution as "
                f"tampering. Pass {d.name!r} to re-run that extract, or a run_id "
                f"that differs by more than case.")
    return run_id


def validate_run_at(run_at: str) -> str:
    """The `run_at`, or `ValueError`. Exactly `YYYY-MM-DD HH:MM:SS`.

    Retention order is a lexicographic sort over this value, so a format the sort
    does not understand is not a cosmetic problem: it decides which snapshot is
    deleted. A real calendar date too, not just the shape of one.
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


def list_snapshots(root) -> list[dict]:
    """Retained snapshots, newest first, as `{run_id, run_at, bytes, dir}`.

    `dir` is the directory this function actually walked, and `run_id` is that
    directory's name. Deliberately not a path re-derived from the manifest: the
    manifest is outside the digest by design (see `snapshot_digest`), so its
    contents are unverified, and a path built from an unverified field can name
    any directory on the machine - which for a caller that DELETES is the whole
    ballgame.

    Ordered by the manifest's own `run_at`, never by file mtime: a snapshot that
    has been copied or restored keeps the moment the extract was TAKEN, and that
    is the moment a figure is as-of.

    A directory whose name is not a usable `run_id` is not a snapshot and is
    skipped - that is what keeps an in-progress `.incomplete-*` write out of the
    store. A directory whose manifest names a DIFFERENT `run_id` is a loud
    `SnapshotError` rather than something to act on: `open_snapshot` can only find
    it under its directory name, so one of the two is wrong, and picking one would
    mean deleting or replaying evidence nobody asked for.
    """
    root = pathlib.Path(root)
    if not root.is_dir():
        return []
    out = []
    for d in sorted(root.iterdir()):
        manifest = d / MANIFEST_NAME
        if not (d.is_dir() and manifest.is_file() and _RUN_ID.fullmatch(d.name)):
            continue
        man = json.loads(manifest.read_text(encoding="utf-8"))
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


#: Every destructive step in this module goes through one of the two helpers
#: below, and both are bounded the same way: 4 attempts over 0.75 s, then the
#: caller decides. The platform property is the one the commit documents - on
#: Windows a delete or a rename needs exclusive access to the whole subtree, and
#: an external scanner holding a file written a moment ago fails it with
#: ACCESS_DENIED - and it applies to a delete exactly as much as to a rename.
#: Bounded on purpose: an unbounded retry would mask a persistent lock, where
#: falling through names the cause and lets the caller refuse or report.
_ATTEMPTS = 4
_BACKOFF_SECONDS = 0.25


def _reclaim(directory) -> bool:
    """Delete `directory` and its contents. True if it went, False if it is held.

    Never raises. A caller that is reclaiming debris has somewhere to put "could
    not", and an exception here would abandon a half-applied loop silently -
    `shutil.rmtree` stops at the first file it cannot remove, so the directory it
    leaves behind is exactly the kind of husk this function exists to clear.
    """
    for attempt in range(_ATTEMPTS):
        try:
            shutil.rmtree(directory)
            return True
        except OSError:
            if attempt == _ATTEMPTS - 1:
                return False
            time.sleep(_BACKOFF_SECONDS)


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


def _debris_status(name: str) -> str:
    """Why a directory in the store is not a snapshot, for the prune report."""
    if name.startswith(INCOMPLETE_PREFIX):
        return "incomplete"
    if name.startswith(SUPERSEDED_PREFIX):
        return "superseded"
    return "unreadable"


#: What a swept directory is reported AS. Keyed by the statuses `_debris_status`
#: returns, so a new kind of debris cannot be swept without a sentence saying
#: what it was: reclaiming something silently is the thing retention must not do.
_SWEPT_REASON = {
    "incomplete": "an extract that never finished.",
    "superseded": "the copy a re-run of that run_id replaced.",
    "unreadable": "a directory in the store that is not a loadable snapshot, "
                  "which is what a delete stopped by a held file leaves.",
}


def prune_snapshots(root, keep: int = KEEP_RUNS, *, protect=()) -> list[dict]:
    """Delete all but the newest `keep` snapshots. Returns what it removed.

    The return value is the point of the function. Silently discarding the
    evidence behind a figure somebody has already quoted is precisely the failure
    this guards against, so every removal is reported with its run_id, its date,
    its size and the directory that went, and the caller is expected to say so out
    loud. Each entry carries a `status`:

      `pruned`      a snapshot that aged out. The loud one: a figure quoted from
                    that build can no longer be reproduced from its own rows.
      `incomplete`  a `.incomplete-*` write that never finished.
      `superseded`  the copy a re-run of the same `run_id` replaced, left behind
                    because deleting it was refused at the time.
      `unreadable`  any other directory in the store that is not a loadable
                    snapshot - the husk a stopped delete leaves, under its own
                    plain name. Nothing could be replayed from it.
      `held`        it could not be removed and IS STILL THERE. Reported rather
                    than raised, so one locked directory cannot cost the caller
                    the report of everything that did go.

    What goes is the directory `list_snapshots` walked. Never a path rebuilt from
    manifest content, which is unverified and could name anything.

    `protect` names run_ids that are never pruned however the order comes out, and
    THE RUN THAT HAS JUST BEEN WRITTEN BELONGS IN IT. Order is a lexicographic
    sort over a supplied `run_at`, so a backfill or a restated as-of date sorts
    oldest and the run would otherwise delete the snapshot it has just reported as
    retained. A protected snapshot is kept on top of `keep`, not instead of one.
    It is a COLLECTION of run_ids, and a bare string is refused rather than
    iterated into its characters: `protect="backfill"` built the set
    `{'c','a','i','b','l','f','k'}` and deleted `backfill` with no error and
    nothing in the report - the exact failure `protect` was added to prevent, in
    the public API the shipped reference tells a reader to call.

    EVERY directory in the store that is not a loadable snapshot goes too, and is
    reported. Not only the `.incomplete-*` prefix this module writes: debris does
    not only arrive by the route designed for it. A delete stopped by a held file
    leaves a plain-named directory whose manifest has already gone - observed,
    with five of ten table files left - which `list_snapshots` cannot see, the
    KiB-on-disk figure cannot count and a prefix match walked straight past, so it
    survived a full prune forever. A directory nothing can see is a directory
    nothing ever reclaims, which is the unbounded store by another route.

    Pruning runs at the end of an extract, by which point this run's own write has
    been renamed into place; a second extract running concurrently is outside the
    single-writer assumption the store makes everywhere else.
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
    # What the sweep below must not touch, decided BEFORE anything is deleted. A
    # removal that is refused part-way takes the manifest with it, so by the time
    # the sweep runs the directory no longer looks like a snapshot - and sweeping
    # it again in the same call would report one directory twice and spend the
    # retry budget twice over.
    was_a_snapshot = {s["dir"] for s in snapshots}
    removed = []
    for snap in snapshots[keep:]:
        if snap["run_id"] in protected:
            continue
        gone = _reclaim(snap["dir"])
        removed.append(dict(snap, status="pruned" if gone else "held"))

    root = pathlib.Path(root)
    for d in sorted(root.iterdir()) if root.is_dir() else []:
        if not d.is_dir() or d in was_a_snapshot:
            continue
        status = _debris_status(d.name)
        entry = {"run_id": d.name, "run_at": "",
                 "bytes": sum(f.stat().st_size for f in d.iterdir() if f.is_file()),
                 "dir": d, "status": status}
        if not _reclaim(d):
            entry["status"] = "held"
        removed.append(entry)
    return removed


def open_snapshot(root, run_id: str, *, expect_digest: str | None = None) -> Snapshot:
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

    `expect_digest=None` is the first build reading the extract it has just taken:
    there is no recorded figure to check against yet. An EMPTY STRING is not that
    case and is refused. Letting `""` mean "no check wanted" is what made the
    substitution check skippable - the one check that tells a substituted extract
    from the original, skipped by the absence of a value rather than by a decision.
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

    No OTHER snapshot is overwritten. A second run with the same `run_id` rewrites
    that one snapshot; a different `run_id` is a different snapshot beside it. A
    `run_id` that differs from one already in the store only in CASE is refused
    rather than treated as a second one, because the filesystem cannot tell them
    apart - see `validate_new_run_id`.

    The snapshot is built in `<root>/.incomplete-<run_id>` and renamed into place
    only once the manifest is written, so a run that dies part-way leaves nothing
    in the store: no half-written directory under a snapshot name, which pruning
    could not see and the on-disk figure could not count. Both arguments are
    validated before any query is issued - a bad `--run-at` found after the COM
    round trip is a bad `--run-at` found too late - and so is the case collision,
    for the same reason.
    """
    validate_run_at(run_at)
    validate_new_run_id(root, run_id)
    out_dir = snapshot_dir(root, run_id)
    work_dir = pathlib.Path(root) / f"{INCOMPLETE_PREFIX}{run_id}"
    if work_dir.exists() and not _reclaim(work_dir):
        raise SnapshotError(
            f"{work_dir} is left over from an earlier run of this run_id and "
            f"could not be removed: something is holding a file inside it. "
            f"Nothing has been deleted and no query has been issued. Close "
            f"whatever has it open, or remove the directory, and run again.")
    try:
        work_dir.mkdir(parents=True)
    except OSError as e:
        raise SnapshotError(
            f"the snapshot work directory {work_dir} could not be created "
            f"({e}), so no extract was taken and nothing was changed.") from None
    try:
        manifest = _extract_into(ex, work_dir, root_package_id,
                                 run_id=run_id, run_at=run_at)
    except BaseException:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise
    _commit(work_dir, out_dir)
    return manifest


def _commit(work_dir: pathlib.Path, out_dir: pathlib.Path) -> None:
    """Move a finished snapshot into place, or leave what is there and say so.

    The rename IS the commit, and on Windows it needs exclusive access to the whole
    subtree: an external scanner holding a file written a moment ago fails it with
    ACCESS_DENIED. Observed once in about four hundred runs of the test suite, so
    every step here is retried rather than treated as impossible - including the
    destructive ones, which is the whole point of this shape.

    A re-run of the same `run_id` has to REPLACE a snapshot, and deleting the old
    one before the rename is what made replacing it destructive. Deleting first
    opens a window in which the name holds NEITHER snapshot, and the delete is
    exactly as exposed to a held file as the rename it guards: observed on a
    documented repeat `run_id` with one file open, the old manifest was destroyed
    with five of ten table files left, `list_snapshots` returned `[]`, the husk
    survived a full prune, the earlier build was told its evidence "has been
    pruned, or was never kept", and the raw `PermissionError` escaped as a
    traceback rather than a refusal. Before the commit was made atomic the same
    interruption left a coherent, visible, loadable snapshot, so this is the step
    that has to be no worse than an in-place overwrite.

    So: the retained snapshot is renamed ASIDE, the new one is renamed into place,
    and only then is the aside deleted. There is no instant in which the name
    holds nothing, and every failure leaves one whole snapshot under it.

    If the commit cannot go through, the rows are NOT discarded. They cost a COM
    extract against a repository that has already moved on, and the operator can
    finish the job with a rename; nothing reads the directory until they do.
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
                f"{out_dir} could not be moved aside ({e}): something else is "
                f"holding a file inside it. Nothing has been deleted - that "
                f"snapshot is still readable and still replayable - and the new "
                f"rows are intact under {work_dir.name}. Close whatever has it "
                f"open and rename {work_dir.name} to {out_dir.name}, or run "
                f"again. Until then nothing reads the new rows, and pruning will "
                f"reclaim them.") from None
    try:
        _rename(work_dir, out_dir)
    except OSError as e:
        if aside is not None:
            # The aside is the ONLY copy of those rows. Putting it back matters
            # more than reporting this failure, so it happens first and a failure
            # to put it back replaces the message.
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
                    f"completes this run.") from None
        raise SnapshotError(
            f"the extract finished but {work_dir} could not be renamed to "
            f"{out_dir} ({e}): something else is holding a file inside it. "
            f"The rows are intact under that name - rename the directory "
            f"to {out_dir.name} to retain the snapshot. Until then nothing "
            f"reads it, and pruning will reclaim it.") from None
    if aside is not None:
        # The new snapshot is in place, so the commit has succeeded and a held
        # aside is not a reason to fail it: what is left is a copy of the rows
        # this run_id was asked to replace. It is not a snapshot - the prefix is
        # not a valid run_id - nothing reads it, and the next prune sweeps it and
        # reports it as `superseded`. Hence the ignored result.
        _reclaim(aside)


def _extract_into(ex: Extractor, out_dir: pathlib.Path,
                  root_package_id: int | None, *, run_id: str, run_at: str) -> dict:
    """Query, filter and write one complete snapshot into `out_dir`.

    Split out so `extract` is only the atomicity: build here, rename there.
    """
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

    # Before EA, not after: these three decide where the snapshot lands, how
    # retention orders it and how much of the store survives, so a bad one found
    # after the COM round trip is a bad one found too late. The case collision is
    # checked here too, for the same reason - it is the one check that needs the
    # store to answer it, and the store is readable without EA.
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
        # The rows survive, under the temp name, and the message says how to keep
        # them. An exit code rather than a traceback: this is a reportable outcome.
        print(e, file=sys.stderr)
        return 2

    for k, v in manifest["counts"].items():
        print(f"  {k:<20} {v:>7} rows")
    scope = manifest["scope"]
    if scope["root_package_id"] is not None:
        print(f"\nscope: package {scope['root_package_id']}, "
              f"{len(scope['package_ids'])} packages, max depth {scope['max_depth']}")
    total_ms = sum(e["ms"] for e in manifest["sql_log"])
    print(f"{len(manifest['sql_log'])} statements, {total_ms:.0f} ms")

    # THE REFERENCE GOES OUT FIRST, before retention runs. These three lines are
    # the only output that lets the build record what it was built from, and
    # `build_database` refuses half a reference - so a store-level problem in a
    # directory that has nothing to do with this run used to cost the operator the
    # digest and the build then shipped with no provenance at all. Observed: one
    # restored copy elsewhere in the store raised out of `prune_snapshots`, which
    # had no handler, and the retained/digest lines never printed. Nothing below
    # can prune this run - `protect` names it - so there is nothing to wait for.
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

    # Pruning announces itself. A figure somebody quoted stops being defensible
    # the moment its evidence goes, so going is never quiet.
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
                  f"{_SWEPT_REASON[s['status']]} Nothing could be replayed from "
                  f"it, and left alone it would never have been reclaimed.")
    held = [s for s in removed if s["status"] == "held"]
    if held:
        print(f"HELD: {len(held)} director(ies) retention meant to remove are "
              f"STILL THERE - something is holding a file inside them, and the "
              f"store stays over its bound until they go:", file=sys.stderr)
        for s in held:
            print(f"  {s['dir']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
