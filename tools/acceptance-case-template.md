# Acceptance-case template

Every skill has one file of acceptance cases at `<skill>/references/test-cases.md`. A case states
what a person asks, what must be true afterwards, and what a failing run looks like. The runner
(plan step 5) starts a fresh agent with the skill, gives it the ask, and then executes the case's
checks. `tools/register.py` counts the cases and reads their `Covers:` lines.

The shape comes from the three Prolaborate files that existed first. They taught one lesson that
holds for every skill: **most failures produce plausible output, not an error.** The failure
description is the most useful part of a case, so write it as carefully as the pass.

Two things are added to that shape:

1. **Every check is executable.** It is a SQL query, an operation call, an HTTP read, or a stated
   test on the reply or the transcript. "The diagram looks right" is not a check.
2. **Every case names the promise it covers.** A `Covers:` line names one or more headings of the
   skill's `SKILL.md`, exactly as written there (backticks and quotes are ignored). The register
   fails a `Covers:` line that names a heading the skill does not have.

---

## File layout

```markdown
# Acceptance cases: `<skill-name>`

<Two or three sentences: what the skill promises, and which failures this file is built to
catch.>

**Fixture.** <What the run starts from: for EA skills, a fresh copy of the Westbrook Bank model
opened in EA; for Prolaborate skills, the local Prolaborate signed in to the Westbrook Bank
repository.> Westbrook Bank is our illustration. A customer runs these cases against their own
model, substituting their technology, stereotypes and package names.

**Marks.** <Only the marks this file uses; see "Marks" below.>

## Cases

### TC-01: <short name>
...

### TC-02: <short name>
...

## Invariants
<Only when the file has invariants. Explains each one, as prol-matrix does.>

## Headings not covered
<Every SKILL.md heading that no case covers, one line each, with the reason.>

## Findings
<Promises the skill makes that it cannot keep, found while writing the cases. Empty if none.>
```

---

## One case

````markdown
### TC-03: <short name, five words or so>

Covers: <SKILL.md heading>; <another heading, if the case covers two>

**Marks:** WRITE, INVARIANT            <- omit the line when the case has no marks

**Ask:** "<what the person types, in their own words, not in the skill's vocabulary>"

**Setup:** <only when the copy must hold something before the ask. The runner builds it on the
copy before the agent starts; the agent never builds its own setup.>

**Passes when:** <what a correct run does and ends with, in a sentence or two.>

**Check:**

```check
sql: SELECT COUNT(*) FROM t_object WHERE Stereotype = 'WBABusinessApplication' AND Name = 'Card Disputes'
expect: = 1
```

**Fails when:** <what a wrong run looks like, especially the wrong run that looks right.>
````

Rules for a case:

- **One promise per case.** If a heading makes three promises, it gets three cases. A case may
  cover two headings when one promise is stated in two places.
- **The ask is the customer's words.** "Add a new payments application called Card Disputes and
  link it to the core banking system", not "call `create_element` with stereotype
  `WBABusinessApplication`". The case tests whether the skill gets from the first to the second.
- **The pass is what must be true, not the steps taken.** Name a step only when the step is
  the promise (for example, "takes a baseline before the first write").
- **The failure names the specific wrong output.** "It fails" is not a failure description.
  "The element is created as a Component when the technology says Class; nothing errors, and the
  toolbox will never offer it" is one.
- **A refusal can be the pass.** When the right answer is to stop, say no, or hand off to another
  skill, the case passes on that and fails on doing the work.
- **"I could not determine X" is a pass** where X cannot be determined from the model. A
  confident wrong answer is the failure.

## Marks

| Mark | Meaning |
|---|---|
| `WRITE` | The run changes the model. It runs only on the copy; the checks read the copy afterwards. |
| `EFFECT` | The run has an effect outside the model: a file written, a share link created. The case says what the effect is and whether the skill must ask first. |
| `REFUSE` | The pass is a refusal or a hand-off to another skill. The checks include that the write did not happen. |
| `INVARIANT` | This case must pass on every run (Ryan's decision of 2026-10-14). The rest count toward the 80% per-skill threshold. Use it for the cases where a failure is plausible and costly. |
| `BLOCKED` | The case needs setup that a model or tenant may not have (a second repository, a licensed add-in). A correct run reports the block. |

## Checks

A check is a fenced block tagged `check`. Each line is `key: value`. A case may have several
blocks; every one must hold. The runner reads them; the agent under test never sees them.

| Key | Value | Notes |
|---|---|---|
| `sql` | One `SELECT`, SQLite dialect, against the run's copy of the model | Only tables and columns in the server's `ea_mcp_server/schema.py` (`EA_SCHEMA`). No `TOP`, no SQL Server functions. Bare stereotype names (`t_object.Stereotype` holds `WBABusinessApplication`). `t_xref` holds the qualified name as an `FQName=` entry whose prefix is the profile name (the Westbrook copy stores `WestbrookBankArchitecture::WBABusinessApplication`), so match it with `LIKE '%::WBABusinessApplication%'`. |
| `call` | `<tool>.<operation> {json parameters}`, run through the built server after the agent finishes | For state SQL cannot reach (diagram layout, MDG runtime state, validation results). Read-only operations only. |
| `http` | `GET <path>` relative to the Prolaborate base URL, in the signed-in session | Prolaborate skills only. Read-only. |
| `file` | A path relative to the run's output folder (the folder the ask names, or the runner's working folder) | For cases whose product is a file: an MDG XML, a report, a Parquet set, a Power BI project. `expect:` `exists`, `contains: <text>`, or `xpath: <expression> = <value>` for XML. Pair it with a `call` to a parse operation (for example `ea_mdg.parse_mdg_xml`) when the file's structure is the promise. |
| `reply` | `says: <statement>` or `not: <statement>` | A test on the agent's final reply. Write one checkable statement per line ("says the matrix is read by name, so a rename breaks the link"), not a mood ("is helpful"). How a reply is graded is decided in the runner design. |
| `tools` | `called: <tool>.<operation>` or `not-called: <tool>.<operation>` | A test on the transcript. Use it for refusals and for promises about the method ("validates before reporting"). |
| `expect` | Follows a `sql`, `call`, `http` or `file` line | `= n`, `>= n`, `<= n`, `empty`, `rows: [[...], ...]`, `unchanged` (same result as the same query before the ask), or for `call`/`http` `<field.path> = <value>`. |

Paths in asks and checks use placeholders the runner substitutes per run: `<model-dir>` for the
folder holding the run's copy of the model, and `<name-dir>` (for example `<output-dir>`,
`<rules-dir>`, `<mdg-dir>`) for a writable folder the runner creates empty for the case. Never an
absolute path.

Common checks:

```check
# the model is unchanged: every read-only and every REFUSE case carries this
sql: SELECT (SELECT COUNT(*) FROM t_object), (SELECT COUNT(*) FROM t_connector), (SELECT COUNT(*) FROM t_diagram), (SELECT COUNT(*) FROM t_package), (SELECT COUNT(*) FROM t_objectproperties)
expect: unchanged
```

```check
# an element of the right stereotype and metaclass exists in the right package
sql: SELECT o.Object_Type FROM t_object o JOIN t_package p ON o.Package_ID = p.Package_ID WHERE o.Name = 'Card Disputes' AND o.Stereotype = 'WBABusinessApplication' AND p.Name = 'Domestic Payments'
expect: rows: [["Component"]]
```

```check
# a tagged value was set
sql: SELECT tp.Value FROM t_objectproperties tp JOIN t_object o ON tp.Object_ID = o.Object_ID WHERE o.Name = 'Card Disputes' AND tp.Property = 'criticality'
expect: rows: [["Mission-Critical"]]
```

```check
# a diagram holds the right number of objects
sql: SELECT COUNT(*) FROM t_diagramobjects d JOIN t_diagram g ON d.Diagram_ID = g.Diagram_ID WHERE g.Name = 'Technology Layer'
expect: = 15
```

Read names and values from the model, not from memory: tag names are lower camel case
(`criticality`, `businessOwner`), and EA stores `&` in names as `&amp;` (the package
`Audit &amp; Compliance`).

Write the SQL so it can be checked before the run: the review step dry-runs every `sql` line
against a read-only file copy of the model, so a column that does not exist fails at review, not
in a live EA where a bad statement raises a dialog that blocks every later call.

## Invariants

Where a failure looks plausible, add a mechanical invariant: a property of the output that can be
checked without a known-good answer. prol-matrix's is the model: every row key is in the source
list, every column key is in the target list, and the unplaced count is reported. A wrong join
fails it however convincing the grid looks. State what the invariant does not cover, too.

## Coverage

- Walk `SKILL.md` heading by heading. Every heading that states something the skill does, refuses
  or warns about gets at least one case.
- Headings that state nothing testable (`See also`, a latency table, a heading inside a code
  sample) go under **Headings not covered**, each with a one-line reason. A reviewer can then
  check the coverage from the file alone.
- The references count: a promise made in `references/*.md` is covered under the `SKILL.md`
  heading that points to it.

## Westbrook Bank

- Values come from `_shared/references/westbrook-example.md` and the model itself. Do not invent
  stereotypes, tags or packages; use the closest real one.
- **The qualified stereotype form is `WBA::`** (`WBA::WBABusinessApplication`) in every ask, pass
  and failure description. Where the canon file says otherwise, it is a known defect (DL-085);
  follow this template. SQL is the exception: it matches what the model stores (see Checks).
- `WestbrookBankArchitecture` is the display name only.
- A case may name Westbrook values; it must not assume a customer has them. The fixture
  paragraph says so once per file.
- No real customer names, no absolute local paths, no personal identifiers. US English.
