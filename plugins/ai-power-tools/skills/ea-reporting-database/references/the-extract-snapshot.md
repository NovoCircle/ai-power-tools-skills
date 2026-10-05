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

**Do not pull the row data through `execute_sql` instead.** A mid-sized model is a few
thousand rows across ten tables; `execute_sql` has no row cap and returns every result
*twice*, once parsed and once as raw XML (APT-2026-0221), so a repository-wide pull is
materialized twice and travels through a context window. None of it needs to reach the
database that way. This talks to EA directly and writes to disk.

**Read the printed counts before going on.** An unexpectedly small `object` or
`objectproperties` count means the scope is wrong, and it is much cheaper to notice
there than after the reconciliation.

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
removed = prune_snapshots(root, keep=10)
```

Returns a list of `{run_id, run_at, bytes}` for everything it deleted, newest-first
ordering decided by the manifest's own `run_at` rather than by file mtime — a
snapshot that has been copied or restored keeps the moment the extract was *taken*,
and that is the moment a figure is as-of.

**Say what went.** Silently discarding the evidence behind a figure somebody has
already quoted is the failure retention exists to prevent, so pruning never does it
quietly and neither should you. `extract.py` prints the list; a caller using the
function is expected to pass it on.

`keep=0` is refused. That would delete the extract behind the build that just ran,
which is a deletion, not a retention policy.

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
the result as the original figure.

### What it refuses, and why loudly

| Situation | What happens |
|---|---|
| Snapshot pruned or never kept | `SnapshotError` naming the `run_id`, saying it has been pruned, and listing what **is** retained |
| A different extract under the same `run_id` | `SnapshotError` — the recorded digest and the files disagree |
| Files edited since it was written | `SnapshotError` — it no longer matches its own manifest, so it is not evidence of anything |
| Build recorded no extract at all | `LoadError` — builds predating retention are in this state |
| No `_load_run` row for that `run_id` | `LoadError` — different fact from "recorded no extract", and not conflated with it |

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
