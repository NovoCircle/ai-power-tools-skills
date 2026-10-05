# The extract snapshot — retention, pruning and replay

The extract is the slowest, least repeatable part of the build: it is the only step
that talks COM, and COM call timing has been measured varying by about 150x. Every
later stage reads the dump rather than the repository, which is what lets the
transform be iterated without paying for EA again.

It is also the **only record of what the repository contained at that instant**. So
it is kept, under the `run_id` of the run that took it, and `_load_run` records
which one a build consumed.

Called a **snapshot** because that is already this project's vocabulary. Not a
"baseline" — that is a specific and different thing in EA, and `ea-change-management`
owns it.

---

## 1. Why a build has to be replayable

Three things that have actually happened, not hypotheticals.

**A transform fix cannot be retested against the data that exposed it.** Seven
separate transform faults were found across a single rework. Each retest meant
re-running the extract against a repository that had moved on, so the fix was never
checked against the rows that produced the fault.

**The repository changes underneath a build.** The model is shared. A package count
was observed moving three times in twenty minutes while measurements were running,
because another session was creating and deleting scratch packages. The extract is
the only artifact that pins an instant.

**A disputed figure cannot be settled after the fact.** The selling point here is a
reconciled number. When one is disputed a month later, "re-run it and see" is not an
answer — the repository is different now, and the difference is exactly what is in
dispute. `_load_run.run_at` is the as-of date for any figure quoted from a build;
the snapshot is the evidence behind that date.

---

## 2. Running it

```bash
python <skills-dir>/_shared/tools/extract.py --out ./extracts \
    --run-id <run-id> --run-at '<YYYY-MM-DD HH:MM:SS>' [--package-id N] [--keep 10]
```

`--package-id N` scopes to one subtree; omit it for the whole repository. `--server-path <dir>`
is needed only if `ea_mcp_server` is not importable, for the row parser.

**`--run-at` has to be exactly `YYYY-MM-DD HH:MM:SS`, and `--run-id` has to be one path
component** — letters, digits, dot, dash, underscore, starting with a letter or digit and *not
ending in a dot*. Both are checked before EA is touched, and neither is cosmetic. Retained
snapshots are ordered by `run_at` as a *string*, so `2026-10-05T08:00:00` or `05/10/2026` sorts
wrongly against the others, and that sort decides what gets deleted. A `run_id` containing a
path separator would put the snapshot somewhere retention cannot see it, where it is never
pruned but still loadable; a `run_id` ending in a dot is one Windows silently renames, so the
directory and the manifest inside it end up naming different things — which stops retention for
the whole store, not just that snapshot.

**A `run_id` that differs from a retained one only in CASE is refused**, before anything is
written, naming both. `Run-A` and `run-a` are two run_ids to this tool and one directory to the
filesystem, so the second would replace the first's rows while retention went on reporting it
under its own name — and a replay of the first build would then report the substitution as
tampering. The store keeps a `run_id` exactly as given rather than case-folding it: the value is
recorded verbatim in `_load_run.extract_run_id`, and folding it would mean a build's provenance
cell no longer holds what you passed. Re-running the *same* `run_id` is still supported, and is
still the one way a snapshot is replaced.

**Do not pull the row data through `execute_sql` instead.** A mid-sized model is a few
thousand rows across ten tables; `execute_sql` has no row cap and returns every result
*twice*, once parsed and once as raw XML (APT-2026-0221), so a repository-wide pull is
materialized twice and travels through a context window. None of it needs to reach the
database that way. This talks to EA directly and writes to disk.

**Read the printed counts before going on.** An unexpectedly small `object` or
`objectproperties` count means the scope is wrong, and it is much cheaper to notice
there than after the reconciliation.

**The `run_id` and the digest are printed before retention runs**, because they are
what `build_database` needs and it refuses half a reference — so a problem in some
other directory in the store must not cost you them. Exit codes: **0** done; **1**
the snapshot is retained and its digest is printed but retention did not complete, so
the store needs attention before the next run; **2** nothing was retained, and the
message says what to do about it.

**Scope resolution has no depth cap.** `resolve_scope` walks the whole package tree
host-side and reports the depth it reached, because recursive CTEs are not portable and
Jet has none. The shipped `_package_subtree_ids` stops at depth 8 and `continue`s past
anything deeper with no warning and no flag (APT-2026-0216), so a deep tree silently
loses its leaves. The only guard here is a `seen` set, against a cycle.

The queries stay inside a narrow portable subset — plain SELECTs, parenthesized joins,
no CTEs, no window functions. Not fastidiousness: EA reports a statement its backend
cannot run as a **modal dialog** that holds the COM connection until a human dismisses
it, and every later call then appears to hang rather than erroring.

---

## 3. The layout

```
<snapshot-root>/
  <run-id>/
    object.json  xref.json  objectproperties.json  package.json
    attribute.json  operation.json  diagram.json  diagramobjects.json
    connector.json  connectortag.json
    extract-manifest.json
```

`extract-manifest.json` carries `run_id`, `run_at`, `digest`, the resolved `scope`,
the row `counts` and the `sql_log` — every statement issued, with its row count and
elapsed time. That is what makes the snapshot **enough on its own**: a replayed
build can state what it was built from, including the exact SQL, without inferring
any of it.

**`run_id` and `run_at` are supplied, never read off a clock.** The same rule
`build_database` follows, for the same reason: an identity a module invents for
itself cannot be tested for the value it stamps, and it cannot afterwards be matched
against the build that consumed it. Mint the `run_id` once, before the extract, and
give the same value to both.

### The digest

`digest` is a sha256 over the ten table files in name order. It deliberately does
**not** cover `extract-manifest.json`, which carries it — a digest cannot cover
itself — and it does not cover `run_id` or `run_at`. So it answers "are these the
same rows", not "is this the same run": two extracts of an unchanged repository hash
the same, which is the useful property. It is what turns the reference in `_load_run`
from a label into an identity, and it is what lets a snapshot be *proven* to be the
one a figure came from.

That property rests on something: **every query carries an `ORDER BY`**, because the
digest is over file *bytes* and no backend promises a row order without one. Each is a
total order — a primary key, or the grouping columns plus a key, or every selected
column, where a tie is then two byte-identical rows whose order cannot change the
file. `t_objectproperties` is the one that matters: it has no unique index on
`(Object_ID, Property)`, so one element can carry two tags of the same name and which
came back first was otherwise the backend's choice. Long-text columns are deliberately
*not* sorted on — `t_xref.Description` is a memo, and a backend that will not sort one
reports it as the modal dialog described above — so `t_xref` orders by `XrefID` and
`t_objectproperties` by `PropertyID`, neither of which is selected. Without this, the
same rows in a different order produce a different digest and a byte-different
database, and a reader would see row-order churn as model change.

---

## 4. Retention is bounded, and the bound is stated

`KEEP_RUNS = 10` snapshots. The figure was measured rather than guessed:

| Model | Rows | Snapshot on disk |
|---|---|---|
| Reference model, ~300 elements | 2,052 | **244 KiB** (about 122 bytes a row) |
| Ten retained snapshots of it | — | **2.4 MiB** |
| Projected at ~31,000 elements | ~205,000 | **~24 MiB** each, ~240 MiB for ten |

**Retention is on, and there is no off switch.** With those figures the trade is not
worth offering: a few megabytes against a build nobody can replay is not a decision
a customer should be asked to make badly. The bound is what keeps it honest — an
unbounded store of every extract forever is a different defect, and on a large
repository the JSON is not small.

The projection is a projection. It assumes the measured bytes-per-row holds, and
only the ~300-element figure is measured. Say which is which if it matters.

### Pruning reports what it removed

```python
removed = prune_snapshots(root, keep=10, protect=(this_run_id,))
```

Returns a list of `{run_id, run_at, bytes, dir, status}` for everything it acted on,
newest-first ordering decided by the manifest's own `run_at` rather than by file
mtime — a snapshot that has been copied or restored keeps the moment the extract was
*taken*, and that is the moment a figure is as-of.

| `status` | What it means |
|---|---|
| `pruned` | A snapshot that aged out. The loud one — a figure quoted from that build can no longer be reproduced from its own rows |
| `incomplete` | A `.incomplete-*` write that never finished |
| `superseded` | The copy a re-run of the same `run_id` replaced, left behind because deleting it was refused at the time |
| `unreadable` | Any other directory in the store that is not a loadable snapshot — what a delete stopped part-way leaves |
| `held` | It could not be removed and **is still there**. Reported, not raised, so one locked directory cannot cost you the report of everything that did go |

**`protect` takes a collection, and a bare string is refused.** `protect="backfill"`
iterates into its characters and protects nothing: it deleted `backfill` with no
error and nothing in the report. It now raises instead. Write the trailing comma —
`protect=(this_run_id,)`.

`dir` is the directory that went, and it is the directory `list_snapshots` walked —
never a path rebuilt from the manifest's `run_id`. The manifest sits outside the
digest, so nothing verifies that field, and a path built from an unverified field can
name any directory on the machine. For the same reason a directory whose manifest
names a *different* `run_id` is refused rather than acted on: a replay can only find
a snapshot under its directory name, so one of the two is wrong and guessing which
means deleting the wrong evidence. If you restore an archived snapshot beside the
live store, restore it under its own `run_id`.

**`protect` the run that has just been written.** Order is a lexicographic sort over
a supplied `run_at`, so a backfill or a restated as-of date sorts *oldest* — and a
run that printed "snapshot retained" and then deleted it has told you to record an
`extract_run_id` that no longer exists. `extract.py` passes its own `--run-id`
through. A protected snapshot is kept on top of `keep`, not instead of one.

**Say what went.** Silently discarding the evidence behind a figure somebody has
already quoted is the failure retention exists to prevent, so pruning never does it
quietly and neither should you. `extract.py` prints the list; a caller using the
function is expected to pass it on.

`keep=0` is refused. It would delete *every* snapshot, the extract behind the build
that just ran included, which is a deletion and not a retention policy.

### An extract that does not finish leaves nothing to find

A snapshot is written to `<root>/.incomplete-<run-id>` and renamed into place only
once its manifest is there. A run killed part-way — the modal dialog over an
unrunnable statement holds the COM connection, every later call appears to hang, and
the run gets killed — therefore leaves nothing under a snapshot name. That matters
because `list_snapshots` only recognizes a directory with a manifest: a half-written
one would be invisible to pruning *and* to the KiB-on-disk figure, and so would never
be reclaimed.

**The next `prune_snapshots` sweeps every directory in the store that is not a
loadable snapshot**, whatever it is called, and reports each one — `incomplete` for
the prefix this tool writes, `unreadable` for anything else, both separately from the
snapshots that aged out. Matching the prefix alone was not enough: debris does not
only arrive by the route designed for it. A delete stopped by a held file leaves a
directory under a *plain* name with its manifest already gone, which no function
could see and no prefix match would catch, and that survived a full prune forever.
Nothing can be replayed from any of it, and `open_snapshot` refuses the names it can.

The rename is the commit, and on Windows it needs exclusive access to the whole
subtree — a scanner holding a file written a moment ago can refuse it. Every step is
retried, 4 attempts over 0.75 s, and that includes the destructive ones: a *delete*
is refused by a held file exactly as readily as a rename.

**Re-running a `run_id` replaces its snapshot without ever leaving the name empty.**
The retained directory is renamed *aside*, the new one is renamed into place, and only
then is the aside deleted — so at every instant that `run_id` holds one whole,
loadable snapshot. Deleting first opened a window in which it held neither, and a held
file inside that window destroyed the old manifest, left half its table files under
the snapshot's own name, and told the earlier build its evidence "has been pruned".
If any step is refused the run **says so and keeps both sets of rows**: the retained
snapshot stays readable and replayable under its own name, and the new rows stay under
the temp name rather than being discarded after a COM round trip against a repository
which has since moved on. Rename that directory to the `run_id` to retain it; until
then nothing reads it, and pruning will reclaim it.

---

## 5. Replaying a build

No EA connection, no COM, nothing but the snapshot and the database.

```python
from load import replay_snapshot

snap = replay_snapshot("reporting.sqlite", run_id, snapshot_root)
# snap.tables["object"], snap.tables["xref"], ... exactly as the build read them
# snap.manifest["scope"], ["counts"], ["sql_log"] - what it was built from
```

Then run the §3.3 transform over `snap.tables` and load it. With the same `run_id`
and `run_at` the result is **byte-identical** to the original database: determinism
is already a requirement here, so that is the honest check, and it is the acceptance
test for this behavior (`test_snapshot.py`).

A real replay usually mints a **new** `run_id` for the new build and passes the
**old** `extract_run_id` — the build is a new build, the evidence is the old
evidence. The two databases then differ in that one cell by design.

`replay_snapshot` composes the digest check rather than leaving it to the caller, on
purpose: a replay that skipped it could rebuild from a different extract and report
the result as the original figure. **Use it rather than `open_snapshot` for a replay.**
`open_snapshot` reads the snapshot you name and has nothing to compare it against;
only `replay_snapshot` reaches into `_load_run` for the digest the build recorded.

Not optional means not optional by omission, either. `extract_run_id` and
`extract_digest` are recorded as a pair or not at all — `build_database` refuses one
without the other — and an empty digest is a refusal rather than a check nobody asked
for. There is no value of that pair that reaches a rebuild without the comparison
happening, because the one that used to was "no digest recorded", which read as
success.

### What it refuses, and why loudly

| Situation | What happens |
|---|---|
| Snapshot pruned or never kept | `SnapshotError` naming the `run_id`, saying it has been pruned, and listing what **is** retained |
| A different extract under the same `run_id` | `SnapshotError` — the recorded digest and the files disagree |
| Files edited since it was written | `SnapshotError` — it no longer matches its own manifest, so it is not evidence of anything |
| Build recorded no extract at all | `LoadError` — builds predating retention are in this state |
| No `_load_run` row for that `run_id` | `LoadError` — different fact from "recorded no extract", and not conflated with it |
| A recorded `extract_run_id` with no digest | `LoadError` — half a reference names a snapshot with nothing to verify it against |
| A `run_id` that is not one safe path component | `SnapshotError` — it would put the snapshot outside retention's reach, or under a name the filesystem changes |
| A `run_id` differing from a retained one only in case | `SnapshotError` naming both — the filesystem cannot tell them apart, so writing it would replace that snapshot's rows and the replay would read the loss as tampering |
| Two directories claiming one `run_id` | `SnapshotError` naming both — restore a snapshot under its own `run_id`, or remove the copy |
| A finished extract that cannot be moved into place | `SnapshotError`, exit 2 — nothing is deleted. The retained snapshot stays under its own name and the new rows stay under the temp name |

Only the asked-for `run_id` is ever read. The failure mode being designed out is the
quiet one: a store containing one perfectly loadable snapshot that is *not* the right
one would produce a plausible database answering about the wrong moment, and nothing
downstream would notice.

---

## 6. What this does not do

- **No pruning on a schedule.** Pruning happens when `extract.py` runs, or when the
  function is called. Nothing reaps in the background.
- **No cross-run comparison.** The snapshots are a point-in-time record and a
  "what changed, and when" report could be built on them, but nothing here reads two
  at once.
- **No compression.** Measured at 244 KiB on the reference model, it was not worth
  the opacity. Revisit with figures from a large repository, not with a guess.
- **Append-only history is explicitly not the model.** Each snapshot is a full dump
  of a scope at an instant, replaced only by its own re-run. The medallion-architecture
  bronze-layer pattern was examined for this and rejected: that layer is append-only
  and retains all history, where this reconciles a single moment back against its
  source. Do not import the vocabulary.
