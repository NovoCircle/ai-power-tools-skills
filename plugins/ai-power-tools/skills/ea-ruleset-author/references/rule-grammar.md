# YAML Rule Grammar Reference

Full grammar for the rules you write in Phase 3 of `ea-ruleset-author/SKILL.md`. Read
this before writing your first rule, then come back to it whenever you need the exact
shape of a template or table.

---

## Start with the meta block

```yaml
# {Language} Conformance Ruleset
# Language:     {Language full name and version}
# Enforced by:  AI Power Tools for Sparx EA — validate_model tool
#
# Stereotype note:
#   <How EA names the stereotypes for this language>
#
# Sources:
#   [S1] {Primary spec} — {URL}
#   [S2] {Secondary source} — {URL}

meta:
  version: "1.0"
  language: {Language name}
  organization: "(your organization)"
  mdg_family: {MDG family name as it appears in EA's MDG list}
  description: >
    {One paragraph summary of what the ruleset checks.}
  severity_levels:
    error:   {What error means for this language}
    warning: {What warning means}
    info:    Advisory note; not a conformance violation
```

## Rule template

```yaml
  - id: {LANG}-{CAT}-{NNN}
    name: {Short human-readable name}
    description: >
      {2-4 sentences. Explain WHY this rule exists, what spec section it comes
      from, and what the violation means architecturally. Cite your sources.
      Example: "An Assignment relationship must originate from an Active Structure
      element. [S1 §5.2]"}
    category: {category_code_lowercase}
    severity: error        # error | warning | info
    demo_trigger: false    # true for ~30% of rules

    selector:
      type: connector      # connector | element
      connector_stereotype: {StereotypeName}     # for connector selectors
      # OR for element selectors:
      stereotypes:
        any_of: ["{StereotypeName}"]

    condition:
      type: connector_endpoint_stereotype        # see condition types below
      source_must_be_one_of:
        - StereotypeName1
        - StereotypeName2
      target_must_be_one_of:
        - StereotypeName3

    remediation:
      short: >
        {One sentence telling the modeler exactly what to do to fix this.
        Be concrete: "Use Serving instead of Realization here."}
      auto_fixable: false
```

## Condition type reference

| `condition.type` | Use for | Key fields |
|-----------------|---------|-----------|
| `connector_endpoint_stereotype` | Connector source/target stereotype constraints | `source_must_be_one_of`, `target_must_be_one_of` |
| `relationship_table` | Connector source **and** target, as a pair, against a standard's allowed-relationship table carried in the ruleset | `table`, `skip_endpoints`, `unknown_endpoint` (ignore\|warn\|error); the table lives in the top-level `tables:` |
| `connector_count` | Element must have N connectors of a given stereotype or EA connector type | `connector_stereotype` and/or `connector_type`, `direction` (incoming\|outgoing), `min`, `max` |
| `contained_in` | Element must sit in the containers the rule lists, outward | `path`: one step per level, each `stereotype_one_of` and/or `name_one_of` |
| `contains_count` | Element must hold N direct children of a kind | `child` (`stereotype_one_of` and/or `name_one_of`), `min`, `max` |
| `tagged_value_required` | Element must have non-empty tags | `tags: [{name, must_be_non_empty}]` |
| `tagged_value_constraint` | Tag must be one of an enum | `tags: [{name, value_must_be_one_of}]` |

## Writing connector endpoint rules

The most powerful rule type. Write them in this order:

1. List ALL valid source stereotypes (err toward inclusion — EA's MDG may have inherited
   subtypes you don't know about)
2. List ALL valid target stereotypes
3. Write the description explaining WHY these constraints exist
4. Set severity: `error` — endpoint violations are always structural

**EA stereotype names: unqualified, but otherwise verbatim.** This is the single
easiest way to ship a ruleset that validates nothing. `validate_model` selects with
`Stereotype IN (...)` against `t_object` / `t_connector` -- exact string comparison, no
normalization and no prefix stripping. A name one character off selects nothing, the
rule reports no violations, and the output is indistinguishable from a clean model.

*Leave the technology NAMESPACE off.* The profile-qualified form
`ArchiMate3::ArchiMate_Assignment` is real, but it is stored in `t_xref` rows named
`Stereotypes` and reached through the API's `StereotypeEx`. The `Stereotype` column that
rules match on holds the unqualified name, so matching the qualified form finds nothing.

*Do not strip anything else.* A prefix that belongs to the stereotype's own name is not a
namespace, and whether a technology uses one is a fact about that technology:

| Technology | What `t_object.Stereotype` holds | Selector to write |
|---|---|---|
| EA built-in ArchiMate (1, 2 and 3.1) | `ArchiMate_Assignment` | `ArchiMate_Assignment` |
| EA built-in BPMN2.0 | `BusinessProcess` | `BusinessProcess` |

Both rows were measured on EA 17.1 build 1716, in the MDG declaration and in stored model
data. So for an ArchiMate ruleset the selector reads:

```yaml
    selector:
      type: connector
      connector_stereotype: ArchiMate_Assignment   # NOT `Assignment` — that matches 0
```

*Measure it, do not infer it.* Run `summarize_stereotype_usage`, or read
`SELECT DISTINCT Stereotype FROM t_object`, against a model actually built with the
technology. Do not take the name from the notation's specification, and do not take it
from the MDG's `metatype` attribute -- `metatype` is the concept name without the prefix,
which is precisely the trap. `ruleset-archimate31/archimate31_rules.yaml` carries the
worked measurement in its header, including what the unprefixed form did when it shipped.

*Sanity-check the run.* Zero violations and zero matched elements are the same output.
Confirm a ruleset matched more than zero elements before reporting a model as clean.

## Writing relationship-table rules

Use this when the language's standard publishes an allowed-relationship table (ArchiMate's
relationship tables, BPMN's connection rules, and so on). An endpoint rule checks the source
and the target separately, so it passes a connector whose two ends are each allowed somewhere
but not together. A relationship-table rule checks the pair.

The table goes in a top-level `tables:` section; one rule then checks every connector:

```yaml
tables:
  archimate-3.1-relationships:
    source: "ArchiMate 3.1 Appendix B, relationship tables"   # required: cite where the table comes from
    connectors:                                               # one letter per connector stereotype
      a: ArchiMate_Access
      r: ArchiMate_Realization
      v: ArchiMate_Serving
    cells:                                                    # source -> target -> allowed letters
      ArchiMate_BusinessProcess:
        ArchiMate_BusinessService: fortv
        ArchiMate_BusinessObject: ao

rules:
  - id: ARCHIMATE-REL-003
    severity: error
    selector:
      type: connector
      connector_stereotypes: any_of_table   # every stereotype the table's `connectors` names
    condition:
      type: relationship_table
      table: archimate-3.1-relationships
      skip_endpoints: [ArchiMate_Junction, ArchiMate_Grouping]   # judged by other rules
      unknown_endpoint: ignore              # an end the table does not name: ignore | warn | error
```

- **Generate the table, do not type it.** Build `cells` from the language's data (for the
  library languages, `relationships.allowed` in the language file), so the ruleset and the
  standard cannot drift. Cite the source; a table without `source` is refused.
- **A known pair with no cell allows nothing.** If both ends appear somewhere in the table but
  `cells[source][target]` is missing, every connector between them is a violation.
- **Prefixes are dropped in tables.** Unlike selector names, table names may carry the
  technology prefix (`ArchiMate3::ArchiMate_Serving`); it is removed before matching, because
  EA stores the short name. An element bound to another technology with the same short name
  matches too.
- **Pick `unknown_endpoint` deliberately.** `ignore` suits a model that mixes languages; `warn`
  or `error` suit a model that should hold only this language.
- **Prove it fires.** Seed one connector the table refuses and confirm the rule reports it,
  naming the pair and what the table allows there.

The connector selector also accepts `connector_stereotypes: [A, B]` (a list) for any connector
condition.

## Selecting by EA type

A stereotype selector cannot see an element that carries no stereotype, and EA models UML
that way: a class, a use case or a port is told apart by EA's own type
(`t_object.Object_Type`), not by a stereotype. A rule can select by EA type, beside or
instead of stereotypes; given both, an item must match both.

```yaml
    selector:
      type: element
      types: {any_of: [UseCase]}            # t_object.Object_Type
    selector:
      type: connector
      connector_types: [Generalization]     # t_connector.Connector_Type
```

Anywhere a rule names an element at a connector's end, a table row or column, or a
container, write an EA type as `type:<Object_Type>`. The prefix keeps a type apart from a
stereotype of the same name.

```yaml
    condition:
      type: connector_endpoint_stereotype
      source_must_be_one_of: ["type:Actor", "type:UseCase"]
      target_must_be_one_of: ["type:UseCase"]
```

In a relationship table, an end uses its stereotype's row when the table has one, otherwise
its `type:` row. `connector_count` takes `connector_type` beside `connector_stereotype`.

- **Measure the type names.** Read `SELECT DISTINCT Object_Type FROM t_object` (or
  `Connector_Type FROM t_connector`) on a model built in EA. EA's names are its own
  (`StateNode`, `ActionPin`, `Sequence`), not always the standard's metaclass names.
- **Prefer stereotypes where they exist.** Many technologies put one stereotype on several
  EA types; select by type only for what has no stereotype, or to narrow a stereotype to one
  of its EA types.

## Writing where-it-sits rules

EA records where every element sits. An element's **container** is the element it is
attached to, if any (a port's owner, or an element nested under another in the Browser),
otherwise its package. A package's container is the package above it. So each element has
one chain of containers, read outward.

`contained_in` checks that chain. `path` has one step per level, innermost first; a step
names the container by stereotype or `type:` (`stereotype_one_of`), by name (`name_one_of`),
or both, and must match all it names.

```yaml
  - id: ZF-CELL-002
    selector:
      type: element
      stereotypes: {any_of: [BusinessEntity]}
    condition:
      type: contained_in
      path:
        - {stereotype_one_of: [ZFCell], name_one_of: [Semantic Data Model]}   # the cell
        - {name_one_of: [Owner]}                                              # the row it is in
```

`contains_count` bounds an element's **direct** children of a kind. A package element's
children are what its package holds; any other element's children are the elements attached
to it.

```yaml
    condition:
      type: contains_count
      child: {stereotype_one_of: [TopEvent]}
      min: 1
      max: 1
```

- **Use names only where the standard has nothing else.** Some frameworks identify a
  container only by its name (a framework row or column); where a stereotype exists, use it.
- **A missing container fails.** If the chain ends before the path does, the element is
  reported, with where it actually sits.

## Writing connector count rules

```yaml
    condition:
      type: connector_count
      connector_stereotype: Aggregation   # the edge label to count
      direction: incoming                 # incoming | outgoing
      min: 2                              # at least 2
      # max: 5                            # optional upper bound
```

`direction: incoming` = connectors pointing INTO this element (element is the target).
`direction: outgoing` = connectors pointing OUT of this element (element is the source).
Use `connector_type: Generalization` instead of, or beside, `connector_stereotype` to count by
EA connector type.

## Section comments

Use ASCII section headers to visually group rules:

```yaml
  # ═══════════════════════════════════════════════════════════════════════════
  # SECTION 1 — RELATIONSHIP ENDPOINT VALIDITY (REL)
  #
  # One or two lines explaining what this section covers and which spec
  # sections these rules come from.
  # ═══════════════════════════════════════════════════════════════════════════

  # ── Assignment ──────────────────────────────────────────────────────────────

  - id: WBA-REL-001
    ...
```

---

## See Also

- `ea-ruleset-author/SKILL.md` — the workflow this grammar supports
- `ruleset-archimate31/archimate31_rules.yaml` — the canonical reference implementation
