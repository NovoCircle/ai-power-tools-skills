# The schema, and queries that answer real questions

Every query here was run against a built database before being written down. The figures are from
the Westbrook Bank reference model and are there to show the *shape* of an answer, not as numbers
to expect.

---

## 1. Two kinds of table, and you can tell them apart by name

**Unprefixed tables are the business vocabulary.** One per stereotype found in the repository,
named from the technology's alias: `business_application`, `vendor_system`, `data_asset`. These
are what a report is built on. The list differs per repository, because it is discovered from
what the model actually contains rather than from what the technology declares.

**Tables prefixed `_` are plumbing.** Keys, bridges, coverage and audit. They sort to the bottom
of any table list and they are not where a report gets its facts — but several of them are where
a report gets its facts *right*, so they are not optional either.

On the reference model that is **29 vocabulary tables and 11 plumbing tables**.

### `_keymap` — the one that makes the rest work

| Column | |
|---|---|
| `ea_guid` | EA's stable natural key. Primary key. Survives a rebuild where a row number does not |
| `entity_table` | Which vocabulary table this element landed in. **The first table only** for a multi-stereotype element |
| `package_id` | Joins to `_pkg` |

It carries no `name`, no `metaclass` and no `stereotype`, because those belong to the vocabulary
tables and duplicating them here is what used to make the database read as EA's metamodel.

**Why it exists at all:** a reference to "any of 29 vocabulary tables" is polymorphic, and a
relational model has exactly three ways to express that — a discriminator column, one bridge
table per type, or a shared key table. This is the third. Diagram membership and relationship
endpoints resolve against it, never against a vocabulary table.

**Every row in it landed somewhere.** `entity_table` is never NULL. An element carrying no
stereotype has no vocabulary term, so it is not in the database at all — see §6.

### `_tag_value` — the multi-value bridge

`ea_guid`, `tag`, `value`. **One row per value**, not per tag. Keyed by element rather than by
table, so a multi-stereotype element's values appear once and counts taken through it are not
doubled.

### `_tag_coverage` — read before trusting any aggregate

`table_name`, `tag`, `present`, `populated`, `total`, `coverage`. `present` is how many elements
carry the tag at all; `populated` is how many have a non-empty value; `coverage` is
`populated / total`.

### The rest

| Table | Columns |
|---|---|
| `_pkg` | `package_id`, `parent_id`, `name`, `path`, `depth` — `path` is the `/`-joined name chain |
| `_rel_all` | `connector_id`, `source_guid`, `target_guid`, `connector_type`, `stereotype`, `profile`, `name` |
| `_overflow_tag` | `ea_guid`, `tag`, `value` — tags too sparse to earn a column, kept rather than dropped |
| `_diagram` | `diagram_id`, `name`, `diagram_type`, `package_id`. Geometry is deliberately not captured |
| `_diagram_object` | `diagram_id`, `ea_guid` |
| `_attribute` | `attribute_id`, `element_guid`, `name`, `attr_type`, `scope` |
| `_operation` | `operation_id`, `element_guid`, `name`, `return_type`, `scope` |
| `_load_run` | `run_id`, `run_at`, `repository`, `spec_hash`, `rows_loaded`, `reconciled`, `mismatches`, `extract_run_id`, `extract_digest` |

A row in `_rel_all`, `_diagram_object`, `_attribute` or `_operation` whose element is out of
scope is **dropped at load time** rather than written with an unresolvable key. A dangling row
inflates a count and makes an inner join quietly return fewer rows than the total being read.

---

## 2. Counting something, honestly

```sql
SELECT criticality, COUNT(*) AS n
  FROM business_application
 GROUP BY criticality
 ORDER BY n DESC;
```

```
Business-Critical  21
Mission-Critical   11
Standard            8
Important           6
                    1     <- empty, and it will be in every such result
```

Then, always, the coverage that count rests on:

```sql
SELECT tag, populated, total, ROUND(coverage * 100, 1) AS pct
  FROM _tag_coverage
 WHERE table_name = 'business_application'
 ORDER BY coverage;
```

```
businessOwner       44  47   93.6
regulatoryScope     44  47   93.6
technicalOwner      46  47   97.9
criticality         47  47  100.0
dataClassification  47  47  100.0
lifecycle           47  47  100.0
```

`criticality` is fully populated, so the roll-up above is sound. `businessOwner` is not, so a
roll-up by owner is missing three applications and must say so.

The worst-covered columns across the whole database, which is the first thing to look at on an
unfamiliar model:

```sql
SELECT table_name, tag, populated, total, ROUND(coverage * 100, 1) AS pct
  FROM _tag_coverage
 WHERE total > 0
 ORDER BY coverage ASC
 LIMIT 10;
```

```
vendor_system       pciScopeJustification   2  35    5.7
regulated_activity  technicalOwner          2   3   66.7
business_application businessOwner         44  47   93.6
```

A tag populated on 2 of 35 is not a dimension. Grouping by it produces a chart that is 94% one
empty bar.

---

## 3. The multi-value trap, measured

"How many applications are in scope for GLBA?"

**Right** — through the bridge:

```sql
SELECT COUNT(DISTINCT ea_guid) AS n
  FROM _tag_value
 WHERE tag = 'regulatoryScope' AND value = 'GLBA';
```
→ **31**

**Wrong** — exact match on the flattened column:

```sql
SELECT COUNT(*) AS n FROM business_application WHERE regulatory_scope = 'GLBA';
```
→ **14**

Same question, same data, and the second answer is 45% of the first. The flattened column holds
`GLBA, FFIEC` and `GLBA, SOX, FFIEC` as single strings; an exact match sees none of them. `LIKE
'%GLBA%'` is not the fix either — it would match a hypothetical `GLBA-adjacent` and miss nothing
only by luck.

The flattened column is for display. The bridge is for counting.

---

## 4. Gaps — the questions that find missing data

Elements missing a value somebody needs:

```sql
SELECT name
  FROM business_application
 WHERE business_owner IS NULL OR TRIM(business_owner) = ''
 ORDER BY name;
```

Governed content nobody has drawn:

```sql
SELECT k.entity_table, COUNT(*) AS n
  FROM _keymap k
  LEFT JOIN _diagram_object d ON d.ea_guid = k.ea_guid
 WHERE d.ea_guid IS NULL
 GROUP BY k.entity_table
 ORDER BY n DESC;
```

```
business_application   7
vendor_system          5
application_function   2
technology_function    1
```

And the reverse, which is the one people do not think to ask — diagrams holding no governed
content at all:

```sql
SELECT COUNT(*) FROM _diagram dg
 WHERE NOT EXISTS (SELECT 1 FROM _diagram_object d WHERE d.diagram_id = dg.diagram_id);
```
→ **10 of 25**

That is not a defect. Those are use-case, sequence, activity and state diagrams, whose content is
UML behavior rather than architecture vocabulary. A diagram catalog built from this database will
legitimately show fewer than half the diagrams in the repository, and a reader needs telling
once.

---

## 5. Traversal

What uses what, with both endpoints resolved against the key map:

```sql
SELECT s.entity_table AS source, r.connector_type, r.stereotype, t.entity_table AS target
  FROM _rel_all r
  INNER JOIN _keymap s ON s.ea_guid = r.source_guid
  INNER JOIN _keymap t ON t.ea_guid = r.target_guid
 WHERE r.stereotype = 'Uses'
 ORDER BY source, target;
```

```
ai_gateway  Association  Uses  ai_service
ai_service  Association  Uses  ai_model
...                                          19 rows
```

To get element names, join each side on to its vocabulary table — the key map tells you which
one. Roll up by where things live:

```sql
SELECT p.path, COUNT(*) AS elements
  FROM _keymap k
  INNER JOIN _pkg p ON p.package_id = k.package_id
 GROUP BY p.path
 ORDER BY elements DESC;
```

---

## 6. What is NOT in the database, and why

The database holds the business vocabulary. An element carrying no stereotype has no vocabulary
term, so it is not here. On the reference model that is **153 of 298 elements**:

| | |
|---|---|
| Package twins — EA stores every package as an object as well as a tree node | 85 |
| UML behavior and requirements — actors, use cases, actions, states | 68 |

Neither is a loss. The package tree is in `_pkg`; the behavioral content is a different kind of
modeling that no architecture technology types.

**The case that costs something** is an element carrying governance tagged values and no
stereotype. On the reference model there are three — Business-Critical, GLBA-scoped platforms
somebody classified deliberately and nobody stereotyped. They are not here, and their eighteen
tag values are not here either, which is why the GLBA count in §3 reads 31 rather than 34.

That is why the build runs a **governance gate before it generates anything** — see
[`the-governance-gate.md`](the-governance-gate.md). Applying a stereotype to one of those three
brings it, its tags and its relationships into the database on the next build.

---

## 7. Elements that are several things at once

`_keymap.entity_table` names the first table only, so finding these needs a UNION across the
vocabulary tables — generated per model, because the table list is discovered from the data.

```sql
SELECT ea_guid, COUNT(*) AS n, GROUP_CONCAT(t, ' + ') AS tables
  FROM (SELECT ea_guid, 'business_application' AS t FROM business_application
        UNION ALL
        SELECT ea_guid, 'system_of_record' AS t FROM system_of_record
        /* ...one SELECT per vocabulary table; take the list from manifest.json */)
 GROUP BY ea_guid
HAVING n > 1;
```

On the reference model that returns exactly one element, in `business_application +
system_of_record`. It is deliberate fixture content: an element that genuinely is both.

Cheaper check when you only want to know *whether* any exist: compare the summed vocabulary-table
row counts in `manifest.json` against `SELECT COUNT(*) FROM _keymap`. Any excess is
multi-stereotype placements.

---

## 8. Governance drift, from the database

Values outside a declared enumeration are reported in `manifest.json` under `domain_violations`
and in the data dictionary. They are findings, not load failures.

Connector stereotype provenance is queryable even though the census does not report it as drift
(APT-2026-0223):

```sql
SELECT stereotype, COUNT(*) AS n
  FROM _rel_all
 WHERE stereotype <> '' AND (profile IS NULL OR profile = '')
 GROUP BY stereotype ORDER BY n DESC;
```

```
Serving       3
access        2
Realization   1
Assignment    1
```

Those carry an ad-hoc stereotype application — a name typed in, bound to no technology. Against:

```sql
SELECT profile, stereotype, COUNT(*) AS n
  FROM _rel_all WHERE profile <> '' GROUP BY profile, stereotype ORDER BY n DESC;
```

```
WestbrookBankArchitecture  Uses          18
StandardProfileL2          Realization    6
BPMN1.1                    Assignment     5
WestbrookBankArchitecture  Flows          5
WestbrookBankArchitecture  realizes       4
BMM                        Uses           1
GML                        Composition    1
```

**`Uses` appears under two profiles** — 18 bound to `WestbrookBankArchitecture`, the model's own
technology, and 1 bound to `BMM`, a shipped language. Same name on the connector, two different
things in the repository, and no report built on the bare stereotype name can tell them apart.
That is the whole argument for resolving provenance rather than reading the stereotype column.

It also shows what EA ships enabled: four shipped languages (`StandardProfileL2`, `BPMN1.1`,
`BMM`, `GML`) in use on connectors beside the model's own technology.

---

## 9. What the last build did

```sql
SELECT run_id, run_at, rows_loaded, reconciled, mismatches
  FROM _load_run ORDER BY run_at DESC;
```

`reconciled` is 1 only when every check ran and matched, NULL when nothing has checked yet, and 0
when the count-back failed. `mismatches` counts failures **and** skips, because a check that did
not run is not a check that passed.

`extract_run_id` and `extract_digest` name the retained extract snapshot the build consumed, so a
figure can be traced to the rows behind it and the build can be replayed without touching EA. A
build whose `extract_run_id` is empty predates retention and cannot be replayed. See
[`the-extract-snapshot.md`](the-extract-snapshot.md).

Sparse tags that never became columns:

```sql
SELECT tag, COUNT(*) AS n FROM _overflow_tag GROUP BY tag ORDER BY n DESC;
```
