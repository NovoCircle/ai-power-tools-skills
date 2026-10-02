# The schema, and queries that answer real questions

Every query here was run against a built database before being written down. The figures are from
the Westbrook Bank reference model (~300 elements, 1885 rows) and are there to show the *shape* of
an answer, not as numbers to expect.

---

## 1. The frame, column by column

Eleven tables, fixed, independent of any technology.

### `element` — the load-bearing one

| Column | |
|---|---|
| `ea_guid` | EA's stable natural key. Primary key. Survives a rebuild where a row number does not |
| `object_id` | EA's integer id. Useful for joining back to EA, not stable across repositories |
| `name`, `metaclass` | As EA holds them |
| `stereotype` | Resolved from `t_xref` when the element is typed; `t_object.Stereotype` as observed when not |
| `profile` | The profile namespace, empty when the application is ad-hoc rather than profile-bound |
| `entity_table` | Where it landed, or NULL. **The first table only** for a multi-stereotype element |
| `package_id` | Joins to `pkg` |

**Resolve relationship endpoints against this table, never against a typed one.** It holds every
in-scope element whatever its typing, so an edge touching an untyped element still resolves.

### `tag_value` — the multi-value bridge

`ea_guid`, `tag`, `value`. **One row per value**, not per tag. Keyed by element, not by table, so a
multi-stereotype element's values appear once and counts taken through it are not doubled.

### `tag_coverage` — read before trusting any aggregate

`table_name`, `tag`, `present`, `populated`, `total`, `coverage`. `present` is how many elements
carry the tag at all; `populated` is how many have a non-empty value. `coverage` is
`populated / total`.

### The rest

| Table | Columns |
|---|---|
| `pkg` | `package_id`, `parent_id`, `name`, `path`, `depth` — `path` is the `/`-joined name chain |
| `rel_all` | `connector_id`, `source_guid`, `target_guid`, `connector_type`, `stereotype`, `profile`, `name` |
| `overflow_tag` | `ea_guid`, `tag`, `value` — tags too sparse to earn a column, kept rather than dropped |
| `diagram` | `diagram_id`, `name`, `diagram_type`, `package_id`. Geometry is deliberately not captured |
| `diagram_object` | `diagram_id`, `ea_guid` |
| `attribute` | `attribute_id`, `element_guid`, `name`, `attr_type`, `scope` |
| `operation` | `operation_id`, `element_guid`, `name`, `return_type`, `scope` |
| `load_run` | `run_id`, `run_at`, `repository`, `spec_hash`, `rows_loaded`, `reconciled`, `mismatches` |

A row in `rel_all`, `diagram_object`, `attribute` or `operation` whose element is out of scope is
**dropped at load time** rather than written with an unresolvable key. A dangling row inflates a
count and makes an inner join quietly return fewer rows than the total being read.

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
  FROM tag_coverage
 WHERE table_name = 'business_application'
 ORDER BY coverage;
```

```
businessOwner      44  47   93.6
regulatoryScope    44  47   93.6
technicalOwner     46  47   97.9
criticality        47  47  100.0
```

`criticality` is fully populated, so the roll-up above is sound. `businessOwner` is not, so a
roll-up by owner is missing three applications and must say so.

The worst-covered columns across the whole database, which is the first thing to look at on an
unfamiliar model:

```sql
SELECT table_name, tag, populated, total, ROUND(coverage * 100, 1) AS pct
  FROM tag_coverage
 WHERE total > 0
 ORDER BY coverage ASC
 LIMIT 10;
```

---

## 3. The multi-value trap, measured

"How many applications are in scope for GLBA?"

**Right** — through the bridge:

```sql
SELECT COUNT(DISTINCT ea_guid) AS n
  FROM tag_value
 WHERE tag = 'regulatoryScope' AND value = 'GLBA';
```
→ **34**

**Wrong** — exact match on the flattened column:

```sql
SELECT COUNT(*) AS n FROM business_application WHERE regulatory_scope = 'GLBA';
```
→ **14**

Same question, same data, and the second answer is 41% of the first. The flattened column holds
`GLBA, FFIEC` and `GLBA, SOX, FFIEC` as single strings; an exact match sees none of them. `LIKE
'%GLBA%'` is not the fix either — it would match a hypothetical `GLBA-adjacent` and still miss
nothing by luck rather than by design.

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

Elements that are on no diagram at all — governed content nobody has drawn:

```sql
SELECT e.name, e.stereotype
  FROM element e
  LEFT JOIN diagram_object d ON d.ea_guid = e.ea_guid
 WHERE d.ea_guid IS NULL AND e.entity_table IS NOT NULL
 ORDER BY e.name;
```

Untyped elements are present, not lost:

```sql
SELECT COUNT(*) AS untyped FROM element WHERE entity_table IS NULL;
```

On the reference model that is 153 of 298 — about half the repository carries no stereotype. They
are in `element` and their relationships are in `rel_all`, so nothing about them is lost; but a
reader comparing an entity-table total against EA's element count needs to be told.

---

## 5. Traversal

What uses what, with both endpoints resolved against `element`:

```sql
SELECT s.name AS source, r.connector_type, r.stereotype, t.name AS target
  FROM rel_all r
  INNER JOIN element s ON s.ea_guid = r.source_guid
  INNER JOIN element t ON t.ea_guid = r.target_guid
 WHERE r.stereotype = 'Uses'
 ORDER BY s.name, t.name;
```

Roll up by where things live:

```sql
SELECT p.path, COUNT(*) AS elements
  FROM element e
  INNER JOIN pkg p ON p.package_id = e.package_id
 WHERE e.entity_table IS NOT NULL
 GROUP BY p.path
 ORDER BY elements DESC;
```

---

## 6. Elements that are several things at once

`element.entity_table` names the first table only, so finding these needs a UNION across the
entity tables — which is **generated per model**, because the table list is discovered from the
data. That is the same reason the pivot is Python and not SQL.

```sql
SELECT ea_guid, COUNT(*) AS n, GROUP_CONCAT(t, ' + ') AS tables
  FROM (SELECT ea_guid, 'business_application' AS t FROM business_application
        UNION ALL
        SELECT ea_guid, 'system_of_record' AS t FROM system_of_record
        /* ...one SELECT per entity table; take the list from manifest.json */)
 GROUP BY ea_guid
HAVING n > 1;
```

On the reference model that returns exactly one element, in `business_application +
system_of_record`. It is deliberate fixture content: an element that genuinely is both.

Cheaper check when you only want to know *whether* any exist: compare the sum of entity-table row
counts in `manifest.json` against `SELECT COUNT(*) FROM element WHERE entity_table IS NOT NULL`.
Any excess is multi-stereotype placements.

---

## 7. Governance drift, from the database

Values outside a declared enumeration are reported in `manifest.json` under
`domain_violations` and in the data dictionary. They are findings, not load failures.

Connector stereotype provenance is queryable even though the census does not report it as drift
(APT-2026-0223):

```sql
SELECT stereotype, COUNT(*) AS n
  FROM rel_all
 WHERE stereotype <> '' AND (profile IS NULL OR profile = '')
 GROUP BY stereotype
 ORDER BY n DESC;
```

```
Uses        10
Flows        5
Serving      3
include      2
extend       2
access       2
Realization  1
Assignment   1
```

Those 26 carry an ad-hoc stereotype application — a name typed in, bound to no technology. Against:

```sql
SELECT profile, stereotype, COUNT(*) AS n
  FROM rel_all WHERE profile <> '' GROUP BY profile, stereotype ORDER BY n DESC;
```

```
BMM                 Uses          15
StandardProfileL2   Realization    6
BPMN1.1             Assignment     5
BIZBOK              realizes       4
GML                 Composition    1
```

**`Uses` appears on both lists** — 15 bound to `BMM`, 10 bound to nothing. Same name on the
connector, two different things in the repository, and no report built on the bare stereotype name
can tell them apart. That is the whole argument for resolving provenance rather than reading the
stereotype column.

It also shows what EA ships enabled: five languages in use on connectors in a model whose own
technology defines none of them.

---

## 8. What the last build did

```sql
SELECT run_id, run_at, rows_loaded, reconciled, mismatches
  FROM load_run ORDER BY run_at DESC;
```

`reconciled` is 1 only when every check ran and matched, NULL when nothing has checked yet, and 0
when the count-back failed. `mismatches` counts failures **and** skips, because a check that did
not run is not a check that passed.

Sparse tags that never became columns:

```sql
SELECT tag, COUNT(*) AS n FROM overflow_tag GROUP BY tag ORDER BY n DESC;
```
