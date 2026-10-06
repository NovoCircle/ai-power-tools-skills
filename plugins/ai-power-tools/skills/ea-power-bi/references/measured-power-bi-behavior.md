# Measured Power BI behavior

**None of this is to be re-derived.** Every figure and every failure here was measured against a
live Power BI, and most of them cost a working session to find. Where something was *not* isolated
or *not* run, this file says so - an unmeasured claim quoted as measured is worse than no claim.

| | |
|---|---|
| Power BI Desktop | **2.158.1177.0** (26.09), Store build |
| Dates | **2026-10-02** for the Power BI behavior; **2026-10-05** for the both-sinks run |
| Model | the Westbrook Bank reference model - 29 stereotypes, 40 tables, 145 vocabulary elements of 298 |
| How it was read back | the engine's own schema views over ADOMD, and DAX output compared row by row against recorded ground truth. Not from screenshots |

---

## 1. Power BI's own relationship detection does not work here, and fails silently

40 tables loaded with no relationships defined. Auto-detect produced:

| | |
|---|---|
| Relationships proposed | **63** - the model needs **38** |
| Active / inactive | 34 / **29** |
| **Invented from shared enumeration values** | **28** - two tables related because both happened to hold a data-classification value |
| Source endpoint of the relationship table into the hub | **0 detected** |
| Target endpoint of the relationship table into the hub | **0 detected** |
| A real relationship switched off with no warning | diagram membership into the hub, deactivated because two paths competed |

So graph traversal - what depends on what, the entire reason to put architecture data in a BI tool
- is **absent**, diagram filtering is dead, and 28 relationships are fiction. **Nothing in Power BI
reports any of this.** The report looks finished.

This is the whole argument for generating the semantic model rather than letting it be inferred.

## 2. What the generated model does instead

Authored, then read back off the engine after the project was applied:

| | Authored | Landed |
|---|---|---|
| Relationships | 38 | **38** |
| Active / inactive | 37 / 1 | **37 / 1** |
| `crossFilteringBehavior: bothDirections` | 29 | **29** |
| `fromCardinality: one` | 29 | **29** |
| Tables | 40 | **40**, of which **10 hidden** |

**Nothing was silently deactivated.** The one inactive relationship is the reverse traversal
endpoint, inactive by design: a table pair may carry only one active relationship, and the inbound
measures reach the other through `USERELATIONSHIP`.

The relationship count is **entities + 9**, which is 38 on this model. It is not a constant.

---

## 3. Three things that each stop the project loading

### A relationship cannot carry a description

A `///` line before `relationship` sets a `description` property. The relationship object has none,
so **the entire project fails to open** - not that relationship, the whole project:

```
There's a problem with the definition content in your Power BI Project.
Property 'description' is unknown and is not expected in the situation it appears.
```

**No file is named and no line number is given.** The inner exception is what identifies it, which
is why "Copy details to clipboard" matters: the dialog text alone would not have located it.

**Tables, columns and measures do take descriptions; relationships do not.** The rationale for each
relationship is therefore carried in the model and deliberately not rendered.

### A base theme is required, and it can be ours

Three opens of the same 40-table model, changing only the theme:

| `report.json` | Result |
|---|---|
| No theme collection, no resource packages | Model loads. **Report fails** - "Something went wrong / Failed to load the report", whose details are an activity id and nothing else |
| Theme block plus **Power BI's own** theme file | **Opens clean** |
| Theme block plus a **minimal theme of ours** - a name, six data colors, three defaults | **Opens clean** |

So the theme is required, and redistributing Microsoft's file is not. Our own theme is emitted as
part of the project.

**Not isolated:** which part is strictly required - the theme collection, the resource-packages
entry, or the file on disk. All three were added together.

### The report half is stricter than the model half

Two measured failures, both from hand-writing `report.json`:

- `reportVersionAtImport` as a **string** aborts the open with a precise message and Power BI loads
  **nothing**. It is an object: `{visual, report, page}`.
- A `report.json` carrying only `$schema` opens the semantic model but fails the report with an
  opaque activity id - and then **every save path crashes** on a null reference, so the project
  cannot be saved at all even though its model loaded perfectly.

The working set is report schema `3.3.0`, the object form of `reportVersionAtImport`, the
resource-packages entry, and the referenced theme file actually present. The emitter replicates the
structure of a project Power BI itself wrote, read off disk, rather than the minimum that seems
reasonable.

---

## 4. TMDL format rules that are not preferences

- **Tab-indented.** Spaces do not parse.
- **CRLF, UTF-8 without a BOM.** Read off a real project, not assumed. A generated file that
  deviates is rejected on apply.
- **Descriptions are `///` lines preceding** the object they describe.
- **A one-to-one relationship must carry `crossFilteringBehavior: bothDirections`** or Power BI
  rejects the file. The message is explicit about it.
- **Power BI validates TMDL on apply and rejects the whole file on one violation.** Good for a
  generator - errors are loud and precise - and fatal for a hand edit.
- **Lineage tags are derived from each object's path**, so two runs over the same model produce
  byte-identical files.

**Not measured: whether a report's field bindings survive a lineage tag that genuinely changes.**
Ours are stable by construction, so the question has never been forced. Do not reassure a customer
about it.

---

## 5. Measures, and the row that is not there

**`SUMMARIZECOLUMNS` drops rows where every measure is BLANK.** Measured on the generated model:
the bare measures returned **65 of 145** rows; the zero-filled variants returned **145**. That is
why both forms ship, and why a table visual should use the zero-filled ones.

Traversal verified against recorded ground truth, row by row:

```
ground truth rows : 145      generated rows : 145
missing : 0      extra : 0      value mismatches : 0
discriminating cases (inbound > 0, outbound = 0) : 22  - all 22 correct
rows with edges in both directions               : 18
VERDICT: MATCH
```

The 22 discriminating cases are the ones a model that silently reuses the active relationship gets
wrong **while looking plausible**. Verifying that measures parse is not verifying that they are
right.

**The traversal measures have only ever been verified under Import.** They are DAX over an inactive
relationship, and nothing here says what they do under any other storage mode.

---

## 6. Hiding, and the table that will not hide

40 tables, 10 hidden. The field list shows the 29 vocabulary tables plus the measure host, and
**no `_`-prefixed table is visible** - confirmed in the Data pane.

**Power BI keeps a hidden table visible when it hosts visible measures.** That is why the traversal
measures live on a visible, business-named table with every column hidden individually, and never
on the hub: measures on the hub would put the plumbing back into a field list the customer was
promised would be their own vocabulary. The host renders as a measure group - measures, no columns.

The alternative, a synthetic one-row measure table, was rejected: it needs a constant partition.

**`SummarizationSetBy = Automatic` does not override an explicit `summarizeBy`** — 2026-10-05,
instrument `$SYSTEM.TMSCHEMA_COLUMNS` against the live engine. The annotation reads as a
contradiction beside an explicit setting, because it records that the *client* chose. It reported
`SummarizeBy = 2` (None) on all **235 real columns**, the INTEGER ones included; the 40 columns at
`1` (Default) are Power BI's own `RowNumber` columns. A model that *does* sum was open on a second
engine at the same time as a control, so this is not a reading taken in the absence of a contrast.

Without that explicit `summarizeBy: none` on every column, a numeric tagged value falls to the
default aggregation and the field list offers a sum of something nobody asked to add up.

---

## 7. Parquet, and the connector

- **The format carries the schema, and that is the point.** The same three all-text tables loaded
  through Excel arrived as `Column1...ColumnN`, because Power BI promotes row 0 to a header only
  when its types differ from the body. From Parquet the names and types were right on the first
  attempt with no Power Query step. A CSV fallback would hand back the defect the format was chosen
  to remove.
- **The connector takes one file per pass.** No folder option, no multi-select. Forty tables would
  be forty passes, which is why the Parquet is paired with a `.pbip` rather than shipped loose.
- Basic mode asks for a **URL** and accepted a local absolute path.
- **Power BI has no SQLite connector.** Checked against the Power Query connector index: Access,
  SQL Server, Oracle, MySQL, MariaDB, DB2 and ODBC are all present; SQLite is not. This is why the
  reporting database is never read directly and paths A and B converge on the same Parquet.
  **No date was recorded for this check** — it is stated undated rather than given a plausible one.
- **Untested: UNC and OneLake paths**, and ingestion by Fabric or Azure SQL. The UNC case is what
  Power BI Service refresh would need.
- Types are **declared**, from the technology, never inferred from the data - otherwise a refresh
  could silently change a column's type depending on which rows happen to be populated.

---

## 8. The update path, which came free

With **"Detect and reload external PBIP changes"** enabled, Power BI noticed the files change on
disk and offered *Apply external changes*. **A regenerated semantic model re-applies to an existing
project without rebuilding the report.** It warns that unsaved in-app edits will be overwritten, so
the generated files have to be the source of truth.

This was not designed for; it fell out of using `.pbip`. **The Power BI-side behavior was
established in earlier research and not re-run** in the live acceptance - determinism of the output
is asserted hermetically, which is a different claim.

Opening a `.pbip` at all needs two preview features: the **`.pbip` save option** and **Store
semantic model using TMDL format**. Both were already on in the build this was measured against;
**the defaults have not been checked**, so confirm before promising.

---

## 9. Both sinks, one extract - 2026-10-05

The whole chain was run through the database sink and the Parquet sink from a single extract, so the
two cannot drift:

| | |
|---|---|
| Reconciliation | **39 checks, 0 failures** |
| Both sinks | the same 40 tables, the same row count on every one |
| Values | **1,028 rows compared cell by cell** across the vocabulary, key map, traversal edges and tag bridge - identical |
| Parquet against the repository | reconciled **independently of the database** |
| Types | every column in all 40 tables carries its declared type |
| Cross-path | same file set; only the table files differ, and the partition really does differ |

Reconciled against the repository directly: key map **145**, traversal edges **56**, tag bridge
**780**, packages **88**, diagrams **25**.

---

## 10. What is not measured, and must not be implied

| | |
|---|---|
| **Volume** | Everything above sits at roughly 300 elements. There are **no figures for a large repository** and no claim may imply any |
| **Power BI Service refresh** | Needs a UNC or OneLake path. Untested |
| **Fabric, OneLake, Azure SQL, lakehouse** | Untested. Do not claim. Do not use the phrase "medallion architecture" |
| **Lineage tags under change** | Stable by construction; never tested against a tag that changed |
| **Re-apply to an existing report** | The Power BI-side behavior was not re-run in the live acceptance |
| **Jet (`.eapx`)** | Everything is measured against a SQLite-backed `.qea` only |
| **Which part of the theme block is required** | Not isolated |
| **Storage modes other than Import** | The measures have only been verified under Import |

Every figure here belongs to a **reference model**. Attribute them that way. They are illustrative
of the shape of a result, never what a customer should expect.
