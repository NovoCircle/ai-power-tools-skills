---
name: ea-reporting-database
description: Build a queryable relational database from a Sparx EA repository - every element, relationship, tagged value, attribute and diagram placement, typed by the technology that governs them - and prove it matches the repository by counting back. Use when someone wants to query, roll up, or report across a whole model rather than element by element, wants EA content in a database an agent or a SQL client can read, or asks for a refreshable extract. Also use when a count taken from EA is disputed and you need a reconciled figure. For Power BI specifically - a dataset, a .pbip, TMDL or a semantic model - follow sections 3.1 to 3.3 here, up to but not including build_database, and then continue with ea-power-bi, which decides whether a relational database is built at all.
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
own DDL generated *for that target* — never retrofitted from SQLite's dialect. **Parquet and Power
BI belong to `ea-power-bi`**, which continues from §3.3 here and decides whether `build_database` runs.

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

**The snapshot is kept, not overwritten.** It is the only record of what the repository contained
at that instant, and a build can be replayed from it with no EA connection at all, producing a
byte-identical database. Retention is bounded at **10 runs** (measured: 244 KiB per snapshot on the
~300-element reference model) and pruning **prints what it removed** — pass that on, because a
figure stops being defensible the moment its evidence goes. Flags, why not `execute_sql`, the
uncapped scope walk, the digest, pruning and replay:
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

### 3.3 Transform and load

All of this is local Python. Every decision is in the modules; this is the order they go in.

```python
import json, pathlib, sys
sys.path.insert(0, r"<skills-dir>/_shared/tools")

from ea_census import build_stereotype_index, census_elements, tag_coverage
from report_model import build_report_model
from frame import (package_rows, element_rows, relationship_rows, diagram_rows,
                   diagram_object_rows, attribute_rows, operation_rows, dangling)
from pivot import pivot
from load import build_database, database_counts, scalar_counts, record_reconciliation
from reconcile import reconcile, domain_violations, format_report
from dictionary import data_dictionary, manifest as build_manifest
from extract import open_snapshot

out = pathlib.Path("./out")
# Minted before the extract and passed to it (§3.2), not invented here.
run_id, run_at = "<run-id>", "<YYYY-MM-DD HH:MM:SS>"
# An old build is REPLAYED with load.replay_snapshot(db, its_run_id, "./extracts"), not this call:
snap = open_snapshot("./extracts", run_id)  # that one checks the digest the build recorded.
objects, xrefs, props = snap.tables["object"], snap.tables["xref"], snap.tables["objectproperties"]
packages, connectors = snap.tables["package"], snap.tables["connector"]
attributes, operations = snap.tables["attribute"], snap.tables["operation"]
diagrams, diagram_objects = snap.tables["diagram"], snap.tables["diagramobjects"]
mdg = json.loads(pathlib.Path("mdg.json").read_text(encoding="utf-8"))

# --- census: which stereotype, from which technology, on how many elements
xref_index = build_stereotype_index(xrefs)
census = census_elements(objects, xref_index)
guid_by_id = {int(o["Object_ID"]): o["ea_guid"] for o in objects}
tag_stats = {e.key: tag_coverage(e, props, lambda r: guid_by_id.get(int(r["Object_ID"]), ""))
             for e in census.entities}

# --- model: tables, columns, types, domains
model = build_report_model(census, tag_stats, mdg,
                           namespace="<profile namespace>", strip_prefix="<stereotype prefix>")

# --- rows
result = pivot(model, objects, props, census.placement,
               excluded_guids=census.excluded_guids,
               guid_of_property=lambda r: guid_by_id.get(int(r["Object_ID"]), ""))

in_scope = {o["ea_guid"] for o in objects} - census.excluded_guids
profile_of = lambda g: next((s.profile for s in xref_index.get(g, []) if s.profile), "")
frame_rows = {
    "pkg": package_rows(packages),
    "element": element_rows(objects, model, census.placement,
                            excluded_guids=census.excluded_guids),
    "rel_all": relationship_rows(connectors, guid_by_id, guids_in_scope=in_scope,
                                 profile_of=profile_of),
    "diagram": diagram_rows(diagrams),
    "attribute": attribute_rows(attributes, guid_by_id, guids_in_scope=in_scope),
    "operation": operation_rows(operations, guid_by_id, guids_in_scope=in_scope),
}
frame_rows["diagram_object"] = diagram_object_rows(
    diagram_objects, guid_by_id,
    diagram_ids={r["diagram_id"] for r in frame_rows["diagram"]}, guids_in_scope=in_scope)

# Every guid reference must resolve against the key map. Should be empty; check, do not assume.
checkable = dict(frame_rows, tag_value=result.tag_value, overflow_tag=result.overflow)
assert not dangling(checkable), dangling(checkable)[:5]

# --- load
loaded = build_database(out / "reporting.sqlite", model, result, frame_rows,
                        run_id=run_id, run_at=run_at, repository="<model file>",
                        extract_run_id=snap.run_id, extract_digest=snap.digest,
                        overwrite=False)
```

**The two parameters with placeholders above.** `namespace` is the profile namespace as it appears
in `t_xref` FQNames, which is **not** the technology id — the id is often a short code where the
namespace is the long form. Do not guess: `infer_technology_namespace(census, declared)` reads it
off the census, where `declared` is `{s["name"] for s in mdg["stereotypes"]}`. `strip_prefix` is the
stereotype prefix to drop when naming tables, so `WBABusinessApplication` becomes
`business_application`; pass `""` to keep it. Neither is load-bearing for correctness.

`run_id` and `run_at` are **yours to supply**, to the extract and the loader alike: neither has a
clock, because a module that stamps its own timestamp cannot be tested for the value it stamps.

`overwrite=False` is the default and refuses an existing file. A refresh that silently replaces the
database somebody is reporting off is not a refresh — delete it, or pass `overwrite=True`,
deliberately.

### 3.4 Reconcile, then write the deliverables

```python
db_scalars = scalar_counts(out / "reporting.sqlite")
oids = {int(o["Object_ID"]) for o in objects if o["ea_guid"] in in_scope}
rec = reconcile(census, database_counts(out / "reporting.sqlite", model),
                entity_key_of_table={t.name: t.entity_key for t in model.tables},
                scalars={
                    "pkg": (len(packages), db_scalars["pkg"]),
                    "element (in scope)": (len(in_scope), db_scalars["element"]),
                    "rel_all": (sum(1 for c in connectors
                                    if guid_by_id.get(int(c["Start_Object_ID"] or -1)) in in_scope
                                    and guid_by_id.get(int(c["End_Object_ID"] or -1)) in in_scope),
                                db_scalars["rel_all"]),
                    "tag_value": (sum(1 for p in props if (p.get("Value") or "").strip()
                                      and guid_by_id.get(int(p["Object_ID"])) in in_scope),
                                  db_scalars["tag_value"]),
                    "attribute": (sum(1 for a in attributes if int(a["Object_ID"]) in oids),
                                  db_scalars["attribute"]),
                    "operation": (sum(1 for o in operations if int(o["Object_ID"]) in oids),
                                  db_scalars["operation"]),
                    "diagram": (len(diagrams), db_scalars["diagram"]),
                })
violations = domain_violations(model, result.rows)
record_reconciliation(out / "reporting.sqlite", run_id, rec)

(out / "reconciliation.txt").write_text(format_report(rec) + "\n", encoding="utf-8", newline="\n")
(out / "data-dictionary.md").write_text(
    data_dictionary(model, run_id=run_id, run_at=run_at, repository="<model file>",
                    reconciliation=rec, domain_violations=violations),
    encoding="utf-8", newline="\n")
(out / "manifest.json").write_text(json.dumps(build_manifest(
    model, loaded, run_id=run_id, run_at=run_at, repository="<model file>",
    reconciliation=rec, domain_violations=violations), indent=2),
    encoding="utf-8", newline="\n")
(out / "issued-sql.log").write_text("\n".join(loaded.sql_log) + "\n",
                                    encoding="utf-8", newline="\n")

print(rec.summary())
sys.exit(rec.exit_code)
```

**Compute each repository-side figure from the raw extract rows**, as above — not by calling the
same function that produced the database side. A figure taken from both sides by one function
checks nothing, and would have hidden the frame bug that shipped an empty `element` table while
reporting a reconciled build.

`rec.exit_code` is 0 only when every check **ran** and matched. A skipped check is not a pass:
pass `None` on a side you genuinely cannot supply and it records as SKIPPED, which fails. The
prototype printed NOT RECONCILED and returned 0, so every pipeline reading the status saw success.

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
`sparse_threshold=` on `build_report_model` is a default that behaved sensibly on one model, not
a measured constant. Override it deliberately.

**Multi-valued tags are reported, never guessed.** `model.multi_value_candidates` lists tags whose
values often contain a comma. A genuinely multi-valued tag and a free-text field containing a
comma are both declared `String` and are indistinguishable by type — `Risk, Compliance & Audit` is
one team name. Pass `multi_valued={"tagName"}` to `build_report_model` only when a human or a
convention has decided. Guessing wrong splits data silently.

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
database, so the load was faithful, which is the only question the reconciliation answers. An
earlier version counted violations as reconciliation failures; the first real run then reported
NOT RECONCILED over a database that had loaded every element correctly, and it would have done
that on every model carrying any governance drift at all. Violations travel in the dictionary and
the manifest. The reconciliation stays a statement about load fidelity.

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
expectation before you correct it**: on the demo model a 41-row gap in `tag_value` was confirmed to
be exactly the excluded machinery before the figure was changed.

**`record_reconciliation` returns False.** No `load_run` row matched that `run_id`. Nothing was
recorded — do not treat it as success.

**A later spot-check in EA disagrees with the database by a few rows.** The reconciliation proves
the database matches **the extract**, and the extract is a point-in-time snapshot; on a shared
repository someone else's work lands in between and the two legitimately differ. That is the
design, not a flaw. `load_run.run_at` is the figure's as-of date and the retained snapshot is the
evidence behind it, so a disputed number is compared against the build it came from — replay it —
not against the model an hour later. Say the as-of date whenever a figure may be quoted back at
you. [`references/the-extract-snapshot.md`](references/the-extract-snapshot.md) §1.

**Jet (`.eapx`) is untested.** Everything here is measured against SQLite-backed `.qea` only
(APT-2026-0218). Say so rather than implying coverage.

**Volume is unmeasured.** The figures behind this skill come from a ~300-element model. Do not
quote a refresh window from it.

---

## Reference files

- [`references/the-schema.md`](references/the-schema.md) — every frame table, column by column,
  and worked queries for the questions people actually ask
- [`references/the-extract-snapshot.md`](references/the-extract-snapshot.md) — retention, the
  digest, pruning, and how to replay a build with no EA connection
- [`references/the-governance-gate.md`](references/the-governance-gate.md) — the pre-build gate:
  the three outcomes, how to apply a stereotype so it binds to the technology, and what to say
  when the customer declines
- [`../_shared/references/ea-ui-verification.md`](../_shared/references/ea-ui-verification.md) —
  the modal-dialog trap
- [`../_shared/references/westbrook-example.md`](../_shared/references/westbrook-example.md) — the
  canonical example model
- `../_shared/tools/` — the modules. Every one but `extract.py` and `load.py` is pure: no COM, no
  I/O, no clock. Their tests run with `python -m pytest ../_shared/tools -q` and need no EA.
