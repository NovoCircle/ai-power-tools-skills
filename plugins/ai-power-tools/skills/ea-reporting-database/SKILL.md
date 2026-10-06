---
name: ea-reporting-database
description: Build a queryable relational database from a Sparx EA repository - every element, relationship, tagged value, attribute and diagram placement, typed by the technology that governs them - and prove it matches the repository by counting back. Use when someone wants to query, roll up, or report across a whole model rather than element by element, wants EA content in a database an agent or a SQL client can read, or asks for a refreshable extract. Also use when a count taken from EA is disputed and you need a reconciled figure. For Power BI specifically - a dataset, a .pbip, TMDL or a semantic model - follow sections 3.1 and 3.2 here, then continue with ea-power-bi, which decides whether a relational database is built at all.
---

# A reporting database from an EA repository

*Tools: `ea_mdg(operation="get_mdg_from_runtime", params={...})`,
`ea_analyze(operation="execute_sql", params={...})` (AI Power Tools for Sparx EA, v3.0.0+),
plus the transform modules in `../_shared/tools/`*

**This skill only reads the repository.** Nothing here creates, updates or deletes anything in
EA. The database it builds is a separate file; the model is untouched.

Run the `ea-start-here` preflight first — which repository is actually open, and which
technologies are actually loaded. Both answers change the output, and a build against the wrong
model is a wasted afternoon.

---

## 1. What this produces, and what it deliberately does not

Five files per build:

| File | What it is |
|---|---|
| `reporting.sqlite` | The database: one table per stereotype, plus eleven `_`-prefixed plumbing tables |
| `manifest.json` | Machine-readable build record, including the reconciliation verdict and `ok` |
| `reconciliation.txt` | The count-back, dimension by dimension, readable |
| `data-dictionary.md` | What every column means, where it came from, and **how populated it is** |
| `issued-sql.log` | Every statement the load issued, in order, with row counts |

**Not produced, on purpose:** no `.sql` DDL file (SQLite carries its own schema and nothing
would read it), no CSV, no Excel. The database is the deliverable, and a portable target gets its
own DDL generated *for that target* — never retrofitted from SQLite's dialect. Parquet and Power BI
belong to `ea-power-bi`, which continues from `prepare` in §3.3.

---

## 2. The shape of the output

**Entity tables** — one per stereotype actually found, named from the technology's alias where it
declares one (`Business Application` becomes `business_application`), snake-cased otherwise.
Columns are `ea_guid`, `name`, `metaclass`, then one per tagged value that cleared the sparse
threshold. `ea_guid` is the primary key: EA's stable natural key, which survives a rebuild where
a row number does not.

**Eleven plumbing tables**, fixed and technology-independent, all prefixed `_` so they sort below
the vocabulary and read as internal: `_keymap`, `_pkg`, `_rel_all`, `_tag_value`, `_tag_coverage`,
`_overflow_tag`, `_diagram`, `_diagram_object`, `_attribute`, `_operation`, `_load_run`. Columns:
[`references/the-schema.md`](references/the-schema.md).

`_keymap` is `ea_guid`, `entity_table`, `package_id` and nothing else — no name, metaclass or
stereotype, because those belong to the entity tables. Diagram membership and relationship
endpoints resolve against it: a reference to "any entity table" is polymorphic, and a shared key
table is how a relational model expresses it.

**Only elements that landed in an entity table are in the database.** One carrying no stereotype
has no vocabulary term, so it is out of scope — reported before the build by the governance gate
(§3.2b), never dropped silently. `_keymap`, `_tag_value` and `_tag_coverage` are load-bearing and
get their own rules in §5.

---

## 3. The build, step by step

### 3.1 Get the technology definition

```
ea_mdg(operation="get_mdg_from_runtime", params={"tech_id": "<id>"})
```

This supplies the aliases, descriptions, declared types and **complete** enumeration domains.
Save the result to `mdg.json` in your working directory.

Check `source` in the response. `"live"` means EA answered from the loaded technology, which is
what you want. If the operation declines, the technology is not loaded — go back to the
`ea-start-here` preflight rather than proceeding, because without it every column is `TEXT` with
an observed domain and the drift findings in §6 cannot be computed at all.

A repository with no technology loaded still builds. Say so explicitly in the report rather than
letting the thinner output pass as the normal one.

### 3.2 Extract

Run this locally against the open repository. **Mint the `run_id` first and pass it to both the
extract and the load** — that is what ties a build to the rows it was built from.

```bash
python <skills-dir>/_shared/tools/extract.py --out ./extracts \
    --run-id <run-id> --run-at '<YYYY-MM-DD HH:MM:SS>' [--package-id N]
```

It writes one JSON file per table plus `extract-manifest.json` into `./extracts/<run-id>/`.
**Read the printed counts.** An unexpectedly small `object` or `objectproperties` count means the
scope is wrong, and it is much cheaper to notice here than after the reconciliation.

**The snapshot is kept, not overwritten**, so a build can be replayed from it with no EA
connection, byte-identical. Retention keeps **10 runs** and pruning **prints what it removed** —
pass that on. Flags, the digest, pruning and replay:
[`references/the-extract-snapshot.md`](references/the-extract-snapshot.md).

### 3.2b The governance gate — run this before you build anything

An element carrying no stereotype lands in no table, so it will not be in the database. Ask
before you build, not after — a customer must not discover it by failing to find a system.

```python
findings = assess(find_ungoverned(elements, tags), declared_shapes(mdg), elements)
print(format_report(findings))   # imports and row mapping: see the reference
```

Show the report and let them decide per element. Three outcomes, **not interchangeable**:

| Outcome | What to say |
|---|---|
| `ranked` | One candidate is backed by evidence the others are not. Offer it **with the reason**, never as certain |
| `unrankable` | Nothing separates the candidates. List them and ask. **Do not pick one** |
| `no_candidate` | The technology extends no stereotype for that metaclass. Offer to extend it (`ea-mdg-model-build`), or accept the exclusion. Never invent a suggestion |

To apply one, pass the **bare** stereotype name via `update_element` — EA resolves it against
the loaded technology and writes the fully-qualified form itself. **Take a baseline first**
(`ea-change-management`): this is the only step in this skill that writes to the model.

If the customer declines, say plainly which elements will not be in the database and carry on —
declining is a valid answer. The call, row mapping, loaded-technology precondition and
verification: [`references/the-governance-gate.md`](references/the-governance-gate.md).

### 3.3 Transform, load and reconcile

All of this is local Python, and the order is in `_shared/tools/pipeline.py`. Call it; do not
reassemble the steps by hand.

```python
import json, pathlib, sys
sys.path.insert(0, r"<skills-dir>/_shared/tools")
from extract import open_snapshot
from pipeline import prepare, build_reporting_database

run_id, run_at = "<run-id>", "<YYYY-MM-DD HH:MM:SS>"   # the ones passed to the extract (§3.2)
snap = open_snapshot("./extracts", run_id)
mdg = json.loads(pathlib.Path("mdg.json").read_text(encoding="utf-8"))

p = prepare(snap.tables, mdg, namespace="<profile namespace>",
            strip_prefix="<stereotype prefix>")
build = build_reporting_database(p, "./out", run_id=run_id, run_at=run_at,
                                 repository="<model file>",
                                 extract_run_id=snap.run_id, extract_digest=snap.digest)
print(build.reconciliation.summary())
sys.exit(build.reconciliation.exit_code)
```

To rebuild an old build from its own rows, get the snapshot with
`load.replay_snapshot(db, its_run_id, "./extracts")` instead of `open_snapshot`: it checks the
digest that build recorded.

**`namespace` and `strip_prefix`.** `namespace` is the profile namespace as it appears in `t_xref`
FQNames, which is **not** the technology id — the id is often a short code where the namespace is
the long form. Do not guess: `pipeline.infer_namespace(snap.tables, mdg)` reads it off the census.
`strip_prefix` is the stereotype
prefix to drop when naming tables, so `WBABusinessApplication` becomes `business_application`;
pass `""` to keep it. `prepare` also takes `sparse_threshold=` and `multi_valued=` (§5).

**Only placed elements are in the frame.** The key map holds the elements that landed in an entity
table, so `prepare` scopes every row that refers to an element to that set. An untyped element's
diagram placements, connectors and attributes are left out rather than written as rows that
resolve against nothing, and the reconciliation counts the same population, under the name
`element (placed in an entity table)`. `prepare` raises `PipelineError` if a row still dangles.

`run_id` and `run_at` are **yours to supply**: no module has a clock, because a module that stamps
its own timestamp cannot be tested for the value it stamps. `overwrite=False` is the default and
refuses an existing database — a refresh that silently replaces the one somebody is reporting off
is not a refresh.

`build_reporting_database` loads `reporting.sqlite`, reconciles it, records the verdict in
`_load_run`, and writes the other four files of §1. The repository side of every count is computed
from the raw extract rows, never by the function that produced the database side, because a figure
taken from both sides by one function checks nothing. `exit_code` is 0 only when every check **ran**
and matched: a count that could not be read back records as SKIPPED, which fails.
`build.recorded` is False if no `_load_run` row matched the `run_id`; then nothing was recorded, so
do not report the verdict as stored.

---

## 4. Reporting the result

Say these four things, in this order, and do not bury the third:

1. **Reconciled or not**, with the check count — `rec.summary()` gives the line.
2. **What was built**: entity tables, rows, and the five files with their location.
3. **What is outside the database**: untyped elements and excluded EA machinery, from the
   manifest. Neither is in the database, so a reader comparing a table count against EA's own
   element count will see the difference and should hear it from you first.
4. **The drift findings** (§6). They are the capability, not an appendix.

Never report a figure from an entity table without saying what the coverage behind it is.

---

## 5. Rules that are not obvious and cost real money when broken

**Coverage is populated, not present.** A tagged value can be attached to every element and
filled in on a quarter of them. `tag_coverage.populated` is the filled-in count and
`_tag_coverage.present` is the attached count. A roll-up over a partly-populated tag produces a
confident wrong number, and a BI report is exactly where that gets believed.

**Aggregate through `_tag_value`, never the flattened column.** The bridge holds one row per
*value*. Measured: "how many applications are in scope for GLBA" answers **31** through the
bridge and **14** by exact match on the flattened column, which holds `GLBA, FFIEC` as a single
string. The flattened column is for display. Worked both ways in
[`references/the-schema.md`](references/the-schema.md) §3.

**Resolve relationship endpoints against `_keymap`, never against an entity table.** Join to a
typed table instead and every edge whose other end is a different stereotype dangles.

**`_keymap.entity_table` names the first table only.** An element carrying several stereotypes is
genuinely several things and appears in several entity tables; one column cannot hold a
one-to-many, and joining names with a separator would reintroduce the comma hazard. Join
`_keymap` to each entity table on `ea_guid` for the complete mapping.

**A sparse tag is routed, not dropped.** Below the threshold (default 5% populated coverage) a
tag becomes `_overflow_tag` rows instead of a column, and the data dictionary names which ones.
`sparse_threshold=` on `prepare` is a default that behaved sensibly on one model, not a measured
constant. Override it deliberately.

**Multi-valued tags are reported, never guessed.** `model.multi_value_candidates` lists tags whose
values often contain a comma. A genuinely multi-valued tag and a free-text field containing a
comma are both declared `String` and are indistinguishable by type — `Risk, Compliance & Audit` is
one team name. Pass `multi_valued={"tagName"}` to `prepare` only when a human or a convention
has decided. Guessing wrong splits data silently.

**An unknown column is refused, not dropped.** `build_database` raises `LoadError` on a row
carrying a key the table has no column for, because the row count would still have matched and the
reconciliation would have agreed.

---

## 6. Declared vs observed — the findings, not the errors

The technology declares what *should* exist. The repository shows what *does*. The gap is the
most valuable output here, and it is reported, never corrected.

`domain_violations(model, result.rows)` returns values outside a **declared** enumeration, with a
count per value. An observed domain cannot be violated — it is by construction every value seen —
so only declared domains are checkable, and the dictionary says which kind each column has.

**A domain violation is not a failed build.** The value is in the repository and it is in the
database, so the load was faithful, which is the only question the reconciliation answers.
Violations travel in the dictionary and the manifest; gating on them would fail every model
carrying any governance drift.

For the full drift picture — stereotypes declared and never used, observed and never declared,
metaclass mismatches, probable misassignments by tag shape — use `ea-mdg-assess`, which runs the
same census through `compare_declared_observed`. This skill reports what reaches the database;
that one reports what the technology and the repository disagree about.

**Known gap:** the census covers elements only, so ad-hoc stereotype applications on *connectors*
are not reported as drift (APT-2026-0223). `rel_all` does carry the facts — `profile` is empty
exactly when the application is ad-hoc rather than profile-bound — so the split is queryable even
though nothing surfaces it as a finding.

---

## 7. When it goes wrong

**A call appears to hang.** EA reports a statement its backend cannot run as a **modal dialog**
that holds the COM connection until a human dismisses it, so every later call appears to hang too.
Look at EA's screen before retrying. See
[`../_shared/references/ea-ui-verification.md`](../_shared/references/ea-ui-verification.md). This
is why the generated SQL stays inside a narrow portable subset.

**The reconciliation fails on one dimension.** Read the delta before changing anything. A
repository-side figure scoped differently from the load fails for the wrong reason — EA's own
machinery (report packages, model documents) is deliberately excluded from the load, so counting
its tagged values on the repository side compares two different populations. **Verify the
expectation before you correct it.**

**A later spot-check in EA disagrees with the database by a few rows.** The reconciliation proves
the database matches **the extract**, a point-in-time snapshot, and on a shared repository other
work lands in between. Compare a disputed number against the build it came from — replay it — and
say the as-of date (`load_run.run_at`) whenever a figure may be quoted back at you.

**Jet (`.eapx`) is untested.** Everything here is measured against SQLite-backed `.qea` only
(APT-2026-0218). Say so rather than implying coverage.

**Volume is unmeasured.** The figures behind this skill come from a ~300-element model. Do not
quote a refresh window from it.

---

## Reference files

- [`references/the-schema.md`](references/the-schema.md) — every frame table, and worked queries
- [`references/the-extract-snapshot.md`](references/the-extract-snapshot.md) — retention and replay
- [`references/the-governance-gate.md`](references/the-governance-gate.md) — the pre-build gate
- [`../_shared/references/ea-ui-verification.md`](../_shared/references/ea-ui-verification.md) —
  the modal-dialog trap
- [`../_shared/references/westbrook-example.md`](../_shared/references/westbrook-example.md) — the
  canonical example model
- `../_shared/tools/` — the modules, `pipeline.py` first. Their tests run with
  `python -m pytest ../_shared/tools -q` and need no EA.
