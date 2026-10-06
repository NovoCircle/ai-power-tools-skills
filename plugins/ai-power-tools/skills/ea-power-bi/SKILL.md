---
name: ea-power-bi
description: Put a Sparx EA repository into Power BI as a generated semantic model - a complete .pbip project with TMDL, deliberately defined relationships, graph-traversal measures and the plumbing hidden - reading either the Parquet a reporting database emitted or Parquet emitted straight from EA. Use when someone wants EA content in Power BI, asks for a dataset, a .pbip, TMDL or a semantic model, or asks why Power BI's own relationship detection does not give them what they expect. Also use when they ask about refresh or a live connection, because what this produces is a snapshot and that has to be said before anything is built.
---

# EA data in Power BI, as a generated semantic model

*Tools: the emitters in [`../_shared/tools/`](../_shared/tools/) -
`parquet_out.py`, `semantic_model.py`, `tmdl.py`, `pbip.py`. The repository side of the work is
`ea-reporting-database`, which this skill continues rather than repeats.*

**Nothing here writes to EA.** The repository is read through the same extract
`ea-reporting-database` uses, and the output is a Power BI project on disk.

Run the `ea-start-here` preflight first - which repository is open, which technologies are
loaded. Then answer §1 before you emit anything.

---

## 1. Ask which path. Do this first

Getting EA data into Power BI is not one problem, and the choice is **a fact about the customer's
estate, not a preference**. Two questions settle it:

1. **What is your EA repository running on** - a file (`.qea`), or a database server?
2. **Do you want a queryable database as well as a Power BI dataset, or only the dataset?**

Put the options to them with the consequence of each attached:

| | What they say they want | What you emit | The consequence to state |
|---|---|---|---|
| **A** | "A database I can query **and** a Power BI dataset" | `reporting.sqlite`, Parquet, and a `.pbip` | A **snapshot**. Refreshing means re-running the build. Works with any repository, file-based included |
| **B** | "Only the Power BI dataset. I do not want a database to maintain" | Parquet and a `.pbip` | The same snapshot, same dataset, nothing left to maintain. Works with any repository |
| **C** | "Power BI reading the repository itself, **live**" | **Nothing. This skill does not emit a live connection** | Say that plainly and stop. A snapshot is not a substitute for live data |

**A and B are the same Power BI experience.** Power BI has **no SQLite connector** - verified
against the Power Query connector index - so on both paths Power BI reads Parquet. The only
difference is that A additionally leaves a queryable database behind. Do not describe them as two
different datasets; they are one dataset with a different amount of residue, and
[`references/the-path-choice.md`](references/the-path-choice.md) has the wording that keeps that
honest.

**Question 1 is the one that can rule an answer out.** A repository held in a file cannot have a
live connection at all, so for that customer the choice is A or B and saying so early saves a
conversation. A customer whose repository is on a database server is **not** thereby entitled to
one: this skill emits A and B only.

**When the answer is C, do not quietly build B.** Emitting a snapshot and letting a customer
believe Power BI is reading their repository is the single most expensive mistake available here,
because the report keeps working and the numbers go stale silently. Say what you can produce, say
it is a snapshot, and let them decide. Give no date for anything you cannot emit today.

---

## 2. What the project is, and what it is not

**It is a snapshot.** Both paths end with Power BI importing files our toolchain wrote. The
partition mode is `import`.

**Refreshing it means re-running the build.** That is the whole mechanism. **We ship no scheduler,
test none, and support none.** The build is a script, so a customer can schedule it themselves -
that is their arrangement, not a product feature, and must not be offered as one.

**The Parquet directory is written into the project as an absolute path.** The emitted project is
therefore specific to the machine and the folder it was generated for. Move the Parquet and the
project stops loading. Regenerate rather than edit the path by hand.

**Power BI Service refresh is untested.** The connector takes a local path; UNC and OneLake paths
have never been tried, and they are what Service refresh would need. Do not assert either way.

---

## 3. Three preconditions, each of which stops the build

**`pyarrow` must be installed.** It is deliberately not a shipped dependency - the transform stays
installable without a compiled wheel - so `build_parquet` raises `ParquetError` when it is absent.
**CSV is not a fallback.** The reason for Parquet is that it carries column names and types:
measured, the same three all-text tables loaded via Excel arrived as `Column1...ColumnN`, and from
Parquet they were right on the first attempt with no Power Query step. Excel is never an output
format.

**Power BI Desktop needs two preview features on:** the `.pbip` save option, and *Store semantic
model using TMDL format*. Confirm them in the customer's build before promising the project will
open; they were already on in the build this was measured against and the defaults have not been
checked.

**Everything here was measured on Power BI Desktop 2.158.1177.0.** Quote that version alongside
any behavior you describe.

---

## 4. The build

### 4.1 Up to the point the paths diverge

Follow `ea-reporting-database` §3.1 and §3.2, then build the half both paths share:

```python
import json, pathlib, sys
sys.path.insert(0, r"<skills-dir>/_shared/tools")
from extract import open_snapshot
from pipeline import prepare

out = pathlib.Path("./out")
run_id, run_at = "<run-id>", "<YYYY-MM-DD HH:MM:SS>"   # the ones passed to the extract
snap = open_snapshot("./extracts", run_id)
mdg = json.loads(pathlib.Path("mdg.json").read_text(encoding="utf-8"))
p = prepare(snap.tables, mdg, namespace="<profile namespace>",
            strip_prefix="<stereotype prefix>")
```

| | |
|---|---|
| `p.model` | the `ReportModel` - tables, columns, declared types, domains |
| `p.result` | the `PivotResult` - entity rows, `tag_value`, `overflow`, `coverage` |
| `p.frame_rows` | the frame: `pkg`, `element`, `rel_all`, `diagram`, `diagram_object`, `attribute`, `operation` |
| `run_id`, `run_at` | yours to supply; no module has a clock |

**On path A**, now run `build_reporting_database(p, out, ...)` exactly as `ea-reporting-database`
§3.3 shows, then carry on here. **On path B, do not.** Nothing else differs: the census, the report
model and the pivot are the same code, which is what makes the two paths produce the same dataset.

The governance gate in `ea-reporting-database` §3.2b is **not optional on either path**. An element
with no stereotype reaches no table, so it reaches no Power BI field list either, and a customer
must not discover that by failing to find a system in a report.

### 4.2 Emit the Parquet

```python
from parquet_out import build_parquet

pq = build_parquet(out / "parquet", p.model, p.result, p.frame_rows,
                   run_id=run_id, run_at=run_at, repository="<model file>")
print(f"{len(pq.files)} files, {pq.rows_written} rows")
for w in pq.warnings:
    print("WARNING:", w)
```

One file per table, named for the table, with declared types. `overwrite=False` is the default and
it refuses a directory that already holds Parquet - replacing the files somebody is reporting off
is not a refresh, so do it deliberately. **Read the warnings aloud.** They are the same ones the
database sink raises, from the same function, and they include tag rows that reached no table.

### 4.3 Reconcile, on either path

Path A reconciled inside `build_reporting_database`. **Path B reconciles too** - against the
Parquet **read back from disk**, with the repository side computed from the raw extract rows by the
same function.

Read the files back rather than trusting `pq.rows_by_table`: those counts come from the rows the
emitter held in memory, so comparing against them asserts the write rather than verifying it, and
a self-consistent output that under-reports is the failure this whole discipline exists to catch.
`pyarrow` is already present on this path, so the read-back is free:

```python
import pyarrow.parquet as pq_read
from ddl import FRAME_DDL, physical

on_disk = {f.stem: pq_read.read_metadata(f).num_rows
           for f in (out / "parquet").glob("*.parquet")}

def counted(name):
    # A table whose file failed to write is ABSENT from on_disk, not zero. Say
    # which one, rather than raising a bare KeyError from inside a comprehension.
    if name not in on_disk:
        raise KeyError(f"no parquet file was written for {name!r} - "
                       f"the build did not produce what it reported")
    return on_disk[name]

entity_counts = {t.name: counted(t.name) for t in p.model.tables}
frame_counts = {k: counted(physical(k)) for k in FRAME_DDL}
```

**On path B**, reconcile against those counts and write the two reports that need no database:

```python
from pipeline import reconcile_against, write_reports

rec = reconcile_against(p, entity_counts, frame_counts)
write_reports(p, rec, out, run_id=run_id, run_at=run_at, repository="<model file>")
print(rec.summary())
```

`reconciliation.txt` and `data-dictionary.md` are path-B deliverables. Report the verdict in your
own output: path B has no database to record it in.

**On path A, check the Parquet too.** The database reconciliation proves the database matches the
repository; it says nothing about the files Power BI actually reads. Compare the read-back with the
database, both halves:

```python
from load import database_counts, scalar_counts

db = out / "reporting.sqlite"
assert entity_counts == database_counts(db, p.model)
assert frame_counts == scalar_counts(db)
```

Without the frame half the eleven `_`-prefixed files, `_keymap` among them, go unchecked, and Power
BI reads those too.

### 4.4 Emit the project

```python
from semantic_model import build_semantic_model
from tmdl import ParquetSource
from pbip import project_files

sm = build_semantic_model(p.model)
source = ParquetSource(directory=str((out / "parquet").resolve()))
files = project_files(sm, source, name="EAReporting")
```

`build_semantic_model` owns the relationships, the hidden plumbing and the traversal measures.
**Do not add relationships by hand and do not let Power BI detect any** - §7 and
[`references/measured-power-bi-behavior.md`](references/measured-power-bi-behavior.md) say what
auto-detect actually produces.

`project_files` returns every text file in the project keyed by its relative path, including a base
theme of our own. A theme is **required** - without one the model loads and the report fails with
an activity id and nothing else - and ours is emitted as part of the project, so
`required_static_resources(...)` is empty and there is no file to copy in. Pass
`base_theme=None` only to reproduce that failure.

`name=` is the project name and appears in every path inside it. One name per customer model is
enough; do not vary it between runs of the same model or the folders multiply.

### 4.5 Write the files. `newline=""` is load-bearing

```python
# The project root, beside the Parquet rather than inside it. ParquetSource
# baked an ABSOLUTE path into the partition above, so the project belongs to the
# folder it was generated for - move either one and the partition is wrong.
#
# Keep the root SHORT. Windows has a 260-character MAX_PATH, and a deep root
# plus the project's own nested paths can reach it. Whether Power BI itself
# imposes a limit is NOT measured - treat this as ordinary Windows caution, not
# as a figure we established.
project_root = out / "pbip"

for rel, text in files.items():
    path = project_root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)

print(f"project written to {project_root.resolve()}")
```

**Every string the emitters return is CRLF-terminated, UTF-8 without a BOM**, because that is what
Power BI itself writes and a project that deviates is rejected on apply. Without `newline=""`
Windows turns each `\r\n` into `\r\r\n`. This is a deliberate exception to the LF rule the rest of
this library follows - do not "fix" it, and do not read the files back with `read_text()`, which
normalizes CRLF to LF and breaks a round trip.

---

## 5. Opening it, and regenerating it

Open `<name>.pbip` at the top of `project_root` - the path §4.5 printed. Expect the semantic model
to load, then the report.

**A regenerated model re-applies to an existing project without rebuilding the report** -
established in earlier research and **not re-run in the live acceptance**, so treat it as expected
behavior rather than something we measured on this build. With
*Detect and reload external PBIP changes* enabled, Power BI notices the files changed on disk and
offers to apply the external changes. It warns that unsaved in-app edits will be overwritten,
which is correct: **the generated files are the source of truth.** Anyone who edits the model
inside Power BI will lose it on the next build, and that is worth saying once, early.

Lineage tags are derived from each object's path, so two runs over the same model produce
byte-identical files and a report's field bindings have nothing to survive. **Whether bindings
survive a tag that genuinely changes has never been tested** - say so rather than reassuring.

Do not call `open_application` on Power BI when an instance is already running; it spawns
duplicates. Open the project path instead.

---

## 6. What to say when you report back

Five things, in this order:

1. **Which path was taken**, and that the result is a **snapshot** with the as-of date from
   `run_at`.
2. **Reconciled or not**, with the check count. An unreconciled build is not a deliverable.
3. **What was emitted** - the Parquet file count, the project path, and the database if path A.
4. **What the field list will show**: the vocabulary tables plus the measure host. The plumbing is
   hidden, not absent, so a reader comparing against the database will see tables they cannot find
   in Power BI and should hear why from you first.
5. **The traversal measures and which to use in a visual.** Both forms ship: use the zero-filled
   ones in a table visual, because `SUMMARIZECOLUMNS` drops any row whose every measure is BLANK.

Never quote a figure out of this dataset without the coverage behind it. A roll-up over a
quarter-populated tag is a confident wrong number, and a BI report is exactly where it gets
believed.

---

## 7. When it goes wrong

**The project will not open and the message names no file.** Read the inner exception, not the
dialog - "Copy details to clipboard" is what locates it. Two measured causes, each of which stops
the **whole** project rather than the offending object: a `description` on a relationship, and
`reportVersionAtImport` written as a string. The emitters avoid both; a hand edit reintroduces
them.

**The model loads and the report fails** with "Something went wrong / Failed to load the report"
and an activity id. The theme is missing. Do not hand-write a `report.json`: one carrying only
`$schema` loads the model, fails the report, and then crashes every save path on a null reference,
so the project cannot even be saved.

**Power BI rejects the whole TMDL file on one violation.** Loud and precise, which is good for a
generator - but it means a single hand edit costs the entire apply. Regenerate instead of patching.

**A table visual is missing rows.** `SUMMARIZECOLUMNS` drops rows where every measure is BLANK -
measured on the Westbrook Bank reference model, 65 of 145 rows returned where the zero-filled
measures returned all 145. That ratio is illustrative of the shape of the problem, not a figure to
expect. Use the
zero-filled measures.

**Inbound and outbound edge counts are identical everywhere.** Something is reading the active
relationship for both directions. The inbound measures reach the inactive relationship through
`USERELATIONSHIP`; a model that lost it looks plausible and is wrong on exactly the elements that
matter.

**A hidden table is visible in the field list anyway.** It hosts a visible measure. Power BI keeps
a hidden table visible when it does, which is why the traversal measures live on a visible,
business-named table and **never on the hub**.

**`build_semantic_model` raises on the measure host name.** It collides with a vocabulary or frame
table, compared case-insensitively as Analysis Services does. Pass a different `measure_host=`;
the name is a parameter so the customer can rename it to their vocabulary.

**`ParquetError` about pyarrow.** §3. Install it or build the database instead - and do not
substitute CSV.

**Jet (`.eapx`) is untested**, and so is any repository larger than the ~300-element reference
model this was measured on. Say so rather than implying coverage.

---

## 8. What you may not claim

- **No automatic or scheduled refresh.** Both paths produce a snapshot and we ship no scheduler.
- **No Microsoft Fabric, OneLake, Azure SQL or lakehouse support.** None of it is tested. Do not
  use the phrase "medallion architecture".
- **No performance or scale figures.** Everything measured sits at roughly 300 elements.
- **No live connection from this skill**, and no date for one.
- **Never a real customer, model or modeling-language name.** Every example is Westbrook Bank.
- **Reference-model figures are always attributed as such**, never presented as what a customer
  will get.
- **It does not fix data quality.** Nothing in THIS skill changes a model at all. The one narrow
  case where the product offers to apply a stereotype belongs to `ea-reporting-database`'s
  governance gate, not here - do not claim it as this skill's behavior.
- **It does not replace Prolaborate, EA's own reporting, or a data warehouse.** It gets
  architecture data into the reporting tool the organization already has.

---

## Reference files

- [`references/the-path-choice.md`](references/the-path-choice.md) - the question to ask, in
  words, what each answer commits the customer to, and what is identical across the paths
- [`references/measured-power-bi-behavior.md`](references/measured-power-bi-behavior.md) - every
  measured fact behind this skill, with its date and instrument, so none of it is re-derived
- [`../ea-reporting-database/SKILL.md`](../ea-reporting-database/SKILL.md) - the repository side:
  census, governance gate, transform, load, reconciliation
- [`../_shared/references/westbrook-example.md`](../_shared/references/westbrook-example.md) - the
  canonical example model
- `../_shared/tools/` - the emitters. None of them touches COM, a clock or the network, so their
  tests run with `python -m pytest ../_shared/tools -q` and need neither EA nor Power BI.
  `semantic_model`, `tmdl` and `pbip` are pure in the full sense - they return strings and write
  nothing. `parquet_out` writes, creates and deletes files, so it is the one that owns a directory.
