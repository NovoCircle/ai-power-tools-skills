# Integration case: reporting to Power BI

One end-to-end case for a cross-product feature: EA content reaches a reporting database, becomes a
generated Power BI project, is opened, refreshed and published from Power BI Desktop, is refreshed
by the Power BI service, and is then asked about in Microsoft 365 Copilot. It joins two skills
(`ea-reporting-database`, `ea-power-bi`), the server's reporting operations, the Power BI
generator and four Microsoft products that no single skill case can reach. It is kind I in
`TEST-REGISTER.md` (`tools/register.py` reads this folder).

The shape follows `tools/acceptance-case-template.md` as far as it fits: a `Covers:` line, marks, an
ask, a pass, executable checks where a check can be executable, and a failure description. Two
things do not fit and are stated rather than bent. The `Covers:` line names `<skill>: <heading>`
pairs, because the case spans two skills. And most of the case happens in products the step 5
runner cannot drive, so those stages record **evidence** (below) and are judged by the person
running the case.

**Fixture.** A fresh copy of the Westbrook Bank model opened in EA, with its technology loaded. The
reporting database is built from that copy, so the model's contents are the test data. Westbrook
Bank is our illustration. A customer runs this case against their own model, substituting their
technology, stereotypes, tagged values and package names, and computes their own expected answers
(stage 8 says how). Every figure below was measured on the Westbrook copy on one day and shows the
shape of an answer; it is not a value to assert. The model changes, so a run recomputes each
expected value from the data it just built.

**Marks.** `BLOCKED`: the step 5 runner skips this case. `EFFECT`: the run writes a reporting
database, a Power BI project and a published model. `REFUSE` and `WRITE` are not used.

**Placeholders.** `<output-dir>` is the folder the run writes the projects to. `<sql-server>` is a
local SQL Server instance the person can create databases on. `<fabric-sql-server>` and
`<fabric-database>` are the connection host and the name of a SQL database in Microsoft Fabric.
`<workspace>` is a Power BI workspace on a Fabric capacity (a trial capacity is enough).
`<dashboard-fixture>` is a Power BI project holding a report built by hand over a generated model
(stage 9). A run substitutes its own values; none of them is written into this file.

## Cases

### TC-01: Reporting to Power BI, end to end

Covers: ea-reporting-database: 5. The build, step by step; ea-reporting-database: 8. Keeping it fresh: the refresh; ea-power-bi: 4. Generate the project; ea-power-bi: 5. Open it, and regenerate it; ea-power-bi: 6. Refresh

**Marks:** BLOCKED, EFFECT

**Blocked for the automated runner because** the case needs Power BI Desktop, the Power BI service,
Microsoft 365 Copilot and a Microsoft Fabric capacity. The step 5 runner (a background helper agent
calling the server) can start none of them, and two need an interactive Microsoft sign-in. The case
is run **by hand with computer use before a release**, by a conversation that has been granted
Enterprise Architect, Power BI Desktop and a browser, one stage at a time, recording evidence as it
goes. It does not count toward the 80% skill threshold.

**Ask:** "Put the Westbrook Bank model into a reporting database, generate the Power BI project
from it, open it in Power BI Desktop and refresh it, then publish it so my team can ask Copilot
questions about our applications. I'll do it once against our local SQL Server and once against the
SQL database we have in Fabric."

**Setup:** The Westbrook copy is open in EA (no dialog showing). The local SQL Server instance
`<sql-server>` is running and the person's Windows account can create a database on it. The Fabric
SQL database `<fabric-database>` exists on `<fabric-sql-server>` and the person's Microsoft account
can sign in to it. `<workspace>` exists on a Fabric capacity. Power BI Desktop is installed and
signed in to the same account. Microsoft 365 Copilot Chat is available to that account. The person
has approved a descriptions file (stage 4) holding the glossary of two business terms below, which
the skill would otherwise stop and ask about.

**Passes when:** Stages 1 to 7 each end in their stated state, and stage 9's values are unchanged.
Stage 8's answers were graded against expected values that three sources agree on, and the way 2
and way 3 results are no worse than the baseline (rule in stage 8). The model in EA is unchanged at
the end.

#### Stage 1: preflight

The run finds out which repository is open and which technologies are loaded before it builds
anything.

```check
tools: called: ea_repository.get_repository_info
```

```check
tools: called: ea_mdg.assess_mdg_situation
```

```check
tools: before: ea_repository.get_repository_info ea_repository.build_reporting_database
```

#### Stage 2: the reporting database, local leg (path B, Windows authentication)

Profile `target`: `{"kind": "reporting_database", "server": "<sql-server>", "database":
"EAReporting", "schema": "logical"}`, with no `authentication` key. The run builds the business
layer, then checks it against the repository.

```check
tools: called: ea_repository.build_reporting_database
```

```check
tools: called: ea_repository.check_business_layer
```

Evidence: the build's reported table, view and row counts; the check's verdict; the SQL Server
version. The built layer must equal the repository: for each entity table, the row count in
`logical.<table>` equals the count of that stereotype in EA's `t_object`.

#### Stage 3: the reporting database, cloud leg (path B, `entra-interactive`)

The same profile with `target` `{"kind": "reporting_database", "server": "<fabric-sql-server>",
"database": "<fabric-database>", "schema": "logical", "authentication": "entra-interactive"}`.

- The Microsoft sign-in prompt appears once, in the "Windows Azure Authentication" window, and the
  person signs in. No prompt appears on any later call in the process.
- Build, check and replay each finish. `remove_business_layer` followed by a build leaves the same
  counts as before the remove.
- A refresh as the **first call of a fresh process**, then a second refresh in the same process,
  both finish without a new prompt.
- A build against a database name that does not exist on a Fabric SQL server stops and says to
  create the database in the Fabric portal. It does not try to create one.

```check
tools: called: ea_repository.replay_reporting_database
```

Evidence: the sign-in prompt screenshot (once), the table and row counts from the build, and the
check's verdict for the cloud database. A cloud-leg count that differs from the local leg's for the
same model is a failure.

#### Stage 4: the Power BI project, with and without descriptions

Run the generator twice from the same definition, into two project names under `<output-dir>`:

```
python <skills-dir>/_shared/tools/powerbi_model.py <output-dir>/WestbrookBank.definition.json <output-dir> --name WestbrookBankPowerBI --mode import
python <skills-dir>/_shared/tools/powerbi_model.py <output-dir>/WestbrookBank.definition.json <output-dir> --name WestbrookBankPowerBIDescribed --mode import --descriptions <output-dir>/WestbrookBank.descriptions.json
```

The descriptions file holds, as the person approved it, two entries on `Business Application`:
`lifecycle` ("Lifecycle stage. Applications being retired are those whose lifecycle is Sunset or
Archive.") and `criticality` ("How much the business depends on it. Critical applications are
those whose criticality is Mission-Critical or Business-Critical."). The run reads aloud the table,
relationship, inactive-relationship and measure counts and the size line (`tables + columns: full
model N, business layer M`, with a warning past 1,000).

```check
file: WestbrookBankPowerBI.pbip
expect: exists
```

```check
file: WestbrookBankPowerBI.SemanticModel/definition/tables/Business Application.tmdl
expect: contains: measure 'Business Application count' = COUNTROWS('Business Application')
```

```check
file: WestbrookBankPowerBI.SemanticModel/definition/tables/Business Application.tmdl
expect: contains: isHidden
```

```check
file: WestbrookBankPowerBI.SemanticModel/definition/tables/Business Application.tmdl
expect: not-contains: Applications being retired are those whose lifecycle is Sunset or Archive.
```

```check
file: WestbrookBankPowerBIDescribed.SemanticModel/definition/tables/Business Application.tmdl
expect: contains: Applications being retired are those whose lifecycle is Sunset or Archive.
```

```check
file: WestbrookBankPowerBI.SemanticModel/definition/tables/t_object.tmdl
expect: not-contains: ///
```

What the checks say: the count measure exists on an entity table, the key columns are hidden, a
description the person approved appears only in the project generated with the file, and EA's own
(physical) tables carry no description.

#### Stage 5: open and refresh in Power BI Desktop

Open `WestbrookBankPowerBIDescribed.pbip` in Power BI Desktop and refresh it, once against the
local database and once against the cloud database (the same project with its data source changed
in Desktop for the second pass, or a second project generated from the cloud leg's definition).
Both refreshes finish with no error and no relationship dialog. Then, through the modeling MCP
server or a DAX query view:

- `'Business Application count'` equals the SQL count of that stereotype in `logical`. A count taken
  with `COUNTROWS(ALL('Business Application'))` is one higher, because it includes the blank member
  (a documented property of the model); using it as the count is the failure.
- The six key columns (`ea_guid`, `source_guid`, `target_guid`, `connector_guid`, `connector_id`,
  `property_id`) are hidden on every business table that has them and on none of EA's tables.
- Every business table, column and measure has a description; no EA table has one.

Evidence: the Desktop version, the refresh verdict for each pass, the DAX results with the SQL
results beside them.

#### Stage 6: publish from Desktop

Publish `WestbrookBankPowerBIDescribed` to `<workspace>` **from Power BI Desktop**. The route
matters: a description written through the service's REST API was not seen by Copilot, and one
published from Desktop was (measured, 2026-10-19), so this stage publishes no other way. Record the
publish time. Then read the published model's descriptions back (DAX `INFO.VIEW.COLUMNS` through
the service's query endpoint) and confirm the two glossary entries are present.

#### Stage 7: service refresh, with no gateway on the cloud leg

In the service, set the published model's data-source credential once (the person's Microsoft
account) and run a refresh on demand. It finishes with no on-premises data gateway configured. The
local leg's published copy is not refreshed in the service: a local SQL Server would need a
gateway, which this case does not set up. Evidence: the refresh history row (status, start, end).

#### Stage 8: the 11 questions in Microsoft 365 Copilot

Wait at least 10 minutes after stage 6 (Copilot picked descriptions up within about 8 minutes). In
a **fresh Copilot chat each time**, ask each question three ways, twice each: **66 chats**.

1. **No report named:** the question alone.
2. **Report named:** "Using the WestbrookBankPowerBIDescribed report, " then the question.
3. **Model URL:** the published model's long-form URL, then the question.

Grades: **right**, **partly right** (part of a list, or the right number with a wrong
explanation), **wrong**, **no answer** (Copilot did not find the data). A cell passes when both runs
are right. Record the route Copilot says it used (which table, and whether it used the count
measure or its own DAX).

**Expected answers are computed three ways before any chat is graded**, from the data the stage 2
build produced: by SQL against the repository's own tables in EA, by SQL against the `logical`
views, and by DAX against the published model. All three must agree for a question. One that does
not is a defect in the layer or the model, and the Copilot grade for it is not recorded until it is
understood. The Westbrook answers measured on 2026-10-19 are in the last column as the shape of the
answer.

| # | Question (as a person asks it) | Kind | Expected answer, Westbrook 2026-10-19 |
|---|---|---|---|
| Q1 | How many business applications do we have? | Count by element type | 45 |
| Q2 | How many business applications are mission-critical? | Count by a tagged value | 11 |
| Q3 | Break down our business applications by criticality. | Count, grouped | Business-Critical 20, Mission-Critical 11, Standard 8, Important 6 |
| Q4 | How many business applications are in GLBA scope? | Multi-valued tagged value (text contains) | 28 |
| Q5 | Which vendor systems come from Envestnet? | List by a tagged value | Envestnet ENV2, Envestnet MoneyGuide Pro, Envestnet Tamarac Portfolio |
| Q6 | Which business services does the Westbrook Customer Self-Service Web use? | Connector traversal, forward | Customer Profile Service, Westbrook Account Master |
| Q7 | Which business applications use the Westbrook Account Master service? | Connector traversal, reverse | Westbrook Account Origination System, Westbrook Account Servicing Hub, Westbrook Customer Self-Service Web |
| Q8 | Which applications are being retired? | Business term (lifecycle Sunset or Archive) | Westbrook Enterprise Service Bus, Westbrook IVR & Self-Service (Sunset); Legacy Report Distribution Server, SFTP Batch Gateway (Archive) |
| Q9 | How many critical applications do we have? | Business term (Mission-Critical or Business-Critical) | 31 (11 + 20); 11 is wrong-but-defensible, record which |
| Q10 | Which business applications hold restricted data? | List by a tagged value | Westbrook Payment Network Gateway, Westbrook Wire Transfer Service |
| Q11 | How many vendor systems are in the model? | Count by element type | 35 |

The three computations, for the questions that show the pattern (the rest follow it, each with the
column and value its question names):

| Q | EA (`t_object` and `t_objectproperties`) | Reporting database (`logical`) | Published model (DAX) |
|---|---|---|---|
| Q1 | `SELECT COUNT(*) FROM t_object WHERE Stereotype = 'WBABusinessApplication'` | `SELECT COUNT(*) FROM logical.[Business Application]` | `EVALUATE ROW("n", [Business Application count])` |
| Q2 | the same, joined to `t_objectproperties` on `Property = 'criticality' AND Value = 'Mission-Critical'` | `... WHERE criticality = 'Mission-Critical'` | `EVALUATE ROW("n", CALCULATE([Business Application count], 'Business Application'[criticality] = "Mission-Critical"))` |
| Q4 | tag `regulatoryScope`, `Value LIKE '%GLBA%'` | `... WHERE regulatoryScope LIKE '%GLBA%'` | `EVALUATE ROW("n", CALCULATE([Business Application count], CONTAINSSTRING('Business Application'[regulatoryScope], "GLBA")))` |
| Q8 | tag `lifecycle`, `Value IN ('Sunset', 'Archive')` | `SELECT name FROM logical.[Business Application] WHERE lifecycle IN ('Sunset', 'Archive')` | `EVALUATE CALCULATETABLE(VALUES('Business Application'[name]), 'Business Application'[lifecycle] IN {"Sunset", "Archive"})` |
| Q11 | `Stereotype = 'WBAVendorSystem'` | `SELECT COUNT(*) FROM logical.[Vendor System]` | `EVALUATE ROW("n", [Vendor System count])` |
| Q7 | connectors of the stereotype between the two element ids | the `Con_Business Application Uses Business Service` view joined to both entity views on `source_guid` and `target_guid` | `EVALUATE FILTER(VALUES('Business Application'[name]), CALCULATE(COUNTROWS('Con_Business Application Uses Business Service'), 'Business Service'[name] = "Westbrook Account Master") > 0)` |

(EA's own tables store `&` in names as `&amp;`: compare after decoding. The DAX is the pattern a
run starts from and is confirmed or corrected on the first run. The agreement of the three answers
is the test, not the DAX text.)

**Q1's blank member.** The model carries a documented blank member on each entity table, so a plain
table or slicer over an entity's columns shows one row too many. Q1 graded **46 is wrong**, and the
record says whether Copilot used the count measure or its own DAX.

**Verdict rule for this stage.** The baseline, measured 2026-10-19 on the generator before the
descriptions and count measures existed, passed 6 of 11 questions with no report named, 9 of 11
with the report named and 9 of 11 with the model URL. This stage fails when way 2 or way 3 passes
fewer than 9 of 11. Way 1 is recorded and compared but not gated, because it depends on which
source Copilot chooses to search. Copilot is not deterministic: a single wrong cell is recorded with
both runs and is not on its own a failure.

**A control.** Q8 and Q9 are also asked, with the model URL, twice each, of a model published from
the project generated **without** the descriptions file. Q8 passing with the file and failing
without it is the evidence that the glossary reaches Copilot. A result that does not show that is
recorded as a finding.

#### Stage 9: the dashboard fixture's values are unchanged

`<dashboard-fixture>` holds a report built by hand over a model the generator made earlier: a table
of `Business Application` with `name`, `criticality`, `lifecycle` and `ea_guid` (V1), a slicer on
`criticality` (V2), a table of the inactive-relationship measure `Uses by target Business
Application` by `name` (V3), and a table of `Con_Business Application Uses Business Service` (V4).
Before regenerating, open it, refresh, and record each visual's values and the two cross-filters
(selecting one application in V1 and the number of rows V4 then shows; selecting one criticality in
V2 and the number of rows V1 then shows). Then regenerate the semantic model under it with the
generator from the same definition (the report folder is left alone), refresh again, and compare.

Pass: every recorded value is identical before and after, and V1, which binds the hidden `ea_guid`
column, still renders. Measured on the Westbrook fixture, 2026-10-19 (the values to compare against
are the ones recorded at the start of the run): V1 46 rows (45 applications and one blank row), V2
members (Blank), Business-Critical, Important, Mission-Critical, Standard, V3 total 1, V4 5 rows,
2 rows in V4 when V1 selects one application, 11 rows in V1 when V2 selects Mission-Critical.

#### Closing check

The model in EA is the same after the run as before: nothing in this feature writes to it.

```check
sql: SELECT (SELECT COUNT(*) FROM t_object), (SELECT COUNT(*) FROM t_connector), (SELECT COUNT(*) FROM t_diagram), (SELECT COUNT(*) FROM t_package), (SELECT COUNT(*) FROM t_objectproperties)
expect: unchanged
```

**What a run records.** One record per run, kept outside any repository (the workspace's
`research/integration-runs/<date>-reporting-to-power-bi/`, the convention the acceptance runs use):

| Stage | Evidence |
|---|---|
| Whole run | Date; skills version; server version; Power BI Desktop version; SQL Server version; the Copilot product and mode as shown on screen; the Westbrook model's file date |
| 1 | The two preflight replies |
| 2, 3 | Build and check output for each leg (table, view and row counts, verdicts); the cloud sign-in screenshot; the refresh-as-first-call result and the second refresh; the missing-database message |
| 4 | Both generator outputs (counts and the size line); the check results above |
| 5 | Refresh verdict per pass; DAX and SQL results side by side; the hidden-key and description checks |
| 6 | Publish time; the descriptions read back from the published model |
| 7 | The service refresh history row |
| 8 | The three-way expected answers per question, and where they disagree; the 66 grades with the route Copilot reported; the control; the verdict against the baseline |
| 9 | Before and after values of every visual and both cross-filters |
| Closing | The unchanged-model check |

**Fails when:** Any stage's state is not the stated one and nothing says so. Examples: a build that
finishes against the cloud database but reads back a different row count than the local one; a
project that opens in Desktop but refreshes with a relationship Power BI invented; descriptions that
sit in the published model's metadata but were written another way than from Desktop, so Copilot
never sees them and the run does not notice; a Q1 answer of 46 accepted as right; Q8 answered
"Sunset" only and graded right; a refresh that works because a gateway was quietly configured; a
hidden `ea_guid` that breaks the V1 table of an existing dashboard; Copilot's answers graded against
expected values that only one source computed.

## Headings not covered

Promises that belong to a skill's own case file rather than to the whole path:

- `ea-reporting-database`: the governance gate, the inclusion choice, the kept extract and replay
  (beyond the one replay), removal of the business layer (beyond the one remove in stage 3), and
  paths A and C. Each has cases in that skill's `references/test-cases.md`.
- `ea-power-bi`: path A and path C generation, DirectQuery, and what to say when it goes wrong. Same.

## Findings

- A read-only copy of the shipped Westbrook model, opened while preparing this case, holds 46
  business applications, where the 2026-10-19 measurement behind Q1 says 45 (it also holds one more
  Business-Critical and one more GLBA application than that measurement). The model changed after
  the measurement, so the Westbrook figures above are not asserted. Stage 8 computes them again.
- The DAX in stage 8 was written for this case and has not been run against a published model.
- `Covers:` here names section headings by number (`5. The build, step by step`). A change that
  renumbers a `SKILL.md` makes `python tools/register.py --check` report the line; update the line
  with the heading.
