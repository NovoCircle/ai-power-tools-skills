# The path choice, in words

The choice of how EA data reaches Power BI is **answerable from a fact about the customer's
estate**. It is not a preference, and it is not ours to make for them. This file holds the question
to ask, what each answer commits them to, and the wording for the two questions that follow it.

Read `SKILL.md` §1 first; this is the long form of it.

---

## 1. The two questions

**"What is your EA repository running on - a file, or a database server?"**

A repository held in a file is a `.qea` (or an older `.eapx` / `.eap`) sitting in a folder or on a
share. A DBMS-backed repository is one EA connects to over a connection string.

This question exists because it can **rule an answer out**. There is nothing to connect to in a
file-based repository, so no amount of wanting live data produces it. Asking first means the
customer hears a constraint rather than a refusal.

**"Do you want a queryable database as well as a Power BI dataset, or only the dataset?"**

Some customers want SQL access for reasons that have nothing to do with Power BI - an audit
extract, a join against another system, an agent that queries it. Others want a dataset and
nothing else to maintain. Both are legitimate and the answer is theirs.

---

## 2. What each answer commits them to

### A - reporting database and a dataset

They get `reporting.sqlite`, the Parquet files, and the `.pbip` project. The database carries its
own data dictionary, reconciliation report and issued-SQL log; `ea-reporting-database` owns all of
that.

What to state: **this is a snapshot, refreshed by re-running the build.** They now have two
artifacts to keep in step, and the Parquet is what Power BI reads - not the database.

### B - the dataset only

They get the Parquet files and the `.pbip` project. No relational stage is created at any point,
and nothing is left behind to maintain.

What to state: **the same snapshot and the same dataset as A.** What they give up is SQL access to
the result, not anything about the Power BI experience.

### C - Power BI reading the repository itself, live

**This skill does not emit it.** Say so in those words.

What to state: what you can produce is a snapshot; a snapshot is not a substitute for live data;
the distinction is real and blurring it is how a customer ends up with the wrong thing. Do not
build A or B and let a live connection be inferred. Do not offer a date, a workaround, or a
"for now".

If their repository is file-based, the answer is additionally that there is nothing live to
connect to - which is a property of their estate and does not change.

---

## 3. What is identical across A and B, and why that matters

**Power BI has no SQLite connector.** Verified against the Power Query connector index: Access,
SQL Server, Oracle, MySQL, MariaDB, DB2 and ODBC are all there; SQLite is not. So the reporting
database cannot be read by Power BI as a database at all, and **on both paths Power BI reads
Parquet.**

Consequently, identical across A and B:

| | |
|---|---|
| The tables | the vocabulary tables, plus eleven `_`-prefixed plumbing tables |
| The relationships | the hub shape, with exactly one relationship inactive by design |
| The measures | the traversal measures, both bare and zero-filled |
| The descriptions | from the technology, on tables, columns and measures |
| The field list | vocabulary plus the measure host; no `_`-prefixed table visible |
| The partition mode | `import`. A snapshot, on both |

Only the **sink** differs, and only in whether a database is written beside the Parquet. The
partition expression itself is byte-identical between A and B, because it points at Parquet in both
cases.

**So do not sell A and B as two different Power BI capabilities.** They are one capability with a
different amount of residue. A customer who picks B and later wants SQL access runs the other sink
over the same extract; their reports are unaffected.

---

## 4. The two questions that follow, and their answers

**"Can it refresh automatically?"**

No. Re-running the build is the refresh mechanism, and **we ship no scheduler, test none and
support none.** The build is a script, so they are free to schedule it themselves - that is their
arrangement, and presenting it as a product feature commits us to behavior we have never run.

The second half of the same question is whether Power BI Service can reach the files at all, which
would need a UNC or OneLake path. **Untested.** Do not assert either way.

**"Can I move the files?"**

Not without regenerating. The Parquet directory is written into the project as an absolute path, so
the emitted project belongs to the folder it was generated for. Regenerate rather than editing the
partition by hand - a hand-edited TMDL file is rejected whole, not line by line.

---

## 5. How to put the choice

Offer all three, in one message, with the consequence attached to each - not one option at a time,
and not a recommendation dressed as a question. The customer is choosing between things that are
differently true about their estate, and they can only do that if they can see the three together.

Then stop and wait. An emitted project is cheap to regenerate and expensive to explain, and a
customer who was never asked will reasonably assume they got the option they would have chosen.
