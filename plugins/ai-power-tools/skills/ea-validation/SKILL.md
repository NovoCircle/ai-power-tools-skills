---
name: ea-validation
description: Author and run YAML sidecar conformance rules against a Sparx EA model via the ea_validate meta-tool. Use when you need to check that an MDG-modeled repository meets its required tagged values, connector cardinality, and endpoint stereotype constraints.
---

# Validating a Sparx EA Model Against a YAML Sidecar Ruleset

*Tool: `ea_validate(operation="audit", params={...})` (AI Power Tools for EA, v3.6.0+)*

> **v1.3.0 — meta-tool dispatch.** All individual tools are now dispatched via 6 meta-tools.
> `validate_model` is exposed as `ea_validate(operation="audit", params={"rules_path_or_content": ...})`.
> The underlying behavior is unchanged.

> **Every ruleset in this package needs server 3.6.5 or later.** Check `update.server_version`
> from `ping` first. On an older server, don't run them: nearly every rule reports nothing,
> and that reads like a clean model. Tell the user to update the server.

> **Building a complete ruleset for a modeling language?** Use the `ea-ruleset-author`
> skill instead — it covers the full workflow: spec research → rule-category planning →
> YAML authoring → testing → publishing to the skills bundle. This skill covers the YAML
> syntax and the validator API.

## When to use

- After importing or building a model that uses a custom MDG, to confirm every element carries the required tagged values.
- Before exporting a model snapshot for downstream consumption.
- As an automated gate in a model-CI pipeline.
- To run a pre-built hosted ruleset (e.g. the ArchiMate 3.1 conformance set) without any local file.

## Sidecar YAML shape

A YAML file with a top-level `rules` list. Each rule has:

```yaml
- id: WBA-TVR-001
  name: Employee Required Fields
  category: tagged_value_completeness
  severity: error          # error | warning | info
  demo_trigger: true       # run in mode="demo_validation"

  selector:
    type: element                       # element | connector
    stereotypes:
      any_of: [Employee]
    tagged_value_filter:                # optional pre-filter
      - tag: OrgLevel
        value_in: ["2", "3", "4"]

  condition:
    type: tagged_value_required         # see condition types below
    tags:
      - name: JobTitle
        must_be_non_empty: true

  remediation:
    short: Populate all required Employee tagged values
```

### Supported selector types

| `selector.type` | Required keys | Meaning |
|---|---|---|
| `element` | `stereotypes.any_of` and/or `types.any_of` | Iterate every element whose stereotype is in the list, or whose EA type (`Object_Type`, such as `UseCase`) is; given both, it must match both. Add `tagged_value_filter` to narrow further. |
| `connector` | `connector_stereotype`, `connector_stereotypes` and/or `connector_types` | Iterate every connector with that stereotype, one of those stereotypes, or one of those EA types (`Connector_Type`, such as `Generalization`); given a stereotype and a type, it must match both. Selection by EA type needs a server released after 3.6.4. |

Connector ends, relationship-table rows and columns, and `contained_in` steps can name an element by EA type as `type:<Object_Type>`.

### Supported condition types

| `condition.type` | Use for |
|---|---|
| `tagged_value_required` | One or more tags on the selected element must be non-empty. |
| `tagged_value_constraint` | One or more tags must take a value from `value_must_be_one_of`. |
| `connector_count` | Element must have between `min` and `max` connectors of a given stereotype, or of a given EA type with `connector_type` (`direction: incoming \| outgoing`). |
| `connector_endpoint_stereotype` | Connector source/target must be in `source_must_be_one_of` / `target_must_be_one_of`. |
| `relationship_table` | The connector's source and target, as a pair, must allow its stereotype in a table from the ruleset's top-level `tables:`. A violation names the pair, the table and what the table allows there. Needs a server that supports it (released after 3.6.4); an older server ignores the rule and reports nothing for it. |
| `contained_in` | The element's containers, outward (the element it is attached to, else its package, then the packages above), must match `path`, one step per level by stereotype, `type:<Object_Type>` or name. Needs a server released after 3.6.4; an older server reports nothing for it. |
| `contains_count` | The element must hold between `min` and `max` direct children of the `child` kind; a package element's children are what its package holds. Needs a server released after 3.6.4. |
| `tagged_value_type_shipped` | A profile's tagged-value types (blank-`Type` attributes on stereotype-defining classes, per `ea-mdg-model-build`'s Phase 2 convention) must also appear in a **built MDG file's RefData** — i.e. must actually have been ticked on the MDG Technology Wizard's Tagged Value Types page, not just defined in `t_propertytypes`. Requires `built_mdg_path` (file path or raw XML). |

### `tagged_value_type_shipped` — catching "defined but never selected"

The MDG Technology Wizard's Tagged Value Types page is a *selection* step: a type
fully defined in `t_propertytypes` but never ticked there does not ship, and
nothing in the model shows this afterward. The symptom ("this field is free
text") is identical to "the type was never defined" but the fix is completely
different — see the `ea-mdg-model-build` skill's Phase 5/6 and Gotchas table.

```yaml
- id: mdg_tag_types_selected
  severity: warning
  selector:
    type: element
    stereotypes:
      any_of: [stereotype]     # EA's built-in stereotype-definition marker
  condition:
    type: tagged_value_type_shipped
    built_mdg_path: path/to/BuiltTechnology.xml   # or raw XML content
```

Scope to one profile package with the top-level `package_id` param on
`ea_validate`. Only types that are **both** referenced (blank `Type` on a
stereotype-defining class's attribute) **and** actually defined in
`t_propertytypes` are eligible to be flagged — a blank-`Type` attribute with
no `t_propertytypes` entry at all is the *other* failure mode (never defined)
and is out of scope for this rule.

> **Schema note.** No built MDG file with a populated `<TaggedValueTypes>`
> block was available to verify this parser against — every local fixture
> ships an always-empty `<TaggedValueTypes/>` stub. A populated fixture can be
> produced: reference data is reachable through
> `Project.ImportReferenceData` / `ExportReferenceData` and
> `Repository.PropertyTypes()`, and through the UI with computer use.
> The parser accepts any child element under
> `<TaggedValueTypes>` that carries a `name` attribute (written against the
> commonly observed `<TagType name="..." detail="..."/>` shape), so it
> shouldn't be brittle to minor schema variation — but re-verify against a
> real built file with reference data before relying on this for a
> high-stakes gate.

## Running the validator

```python
# Full scan — every rule in a local file
result = ea_validate(operation="audit", params={
    "rules_path_or_content": "path/to/rules.yaml"
})

# Demo mode — only rules with demo_trigger: true
result = ea_validate(operation="audit", params={
    "rules_path_or_content": "path/to/rules.yaml",
    "mode": "demo_validation",
})

# Scope to a single package subtree
result = ea_validate(operation="audit", params={
    "rules_path_or_content": "path/to/rules.yaml",
    "package_id": 42,
})

# A ruleset that ships in the plugin, by path from the plugin root
result = ea_validate(operation="audit", params={
    "rules_path_or_content": "<plugin root>/rulesets/archimate-3/archimate-3_rules.yaml",
})
```

### Shipped rulesets

These rulesets need server 3.6.5 or later. On 3.6.4 and earlier their rules report nothing, with no error, so a clean result there means nothing.

Rulesets ship in this plugin, one folder per language. Each path below is from the plugin root.

| Language id | Path | Rules | Standard version |
|-------------|------|-------|------------------|
| `archimate-3` | `rulesets/archimate-3/archimate-3_rules.yaml` | 4 | ArchiMate 3.1 |
| `bpmn-2` | `rulesets/bpmn-2/bpmn-2_rules.yaml` | 44 | BPMN 2.0.2 |
| `bmm-1` | `rulesets/bmm-1/bmm-1_rules.yaml` | 13 | BMM 1.3 |
| `dmn-1` | `rulesets/dmn-1/dmn-1_rules.yaml` | 6 | DMN 1.2 |
| `cmmn-1` | `rulesets/cmmn-1/cmmn-1_rules.yaml` | 11 | CMMN 1.1 |
| `soaml-1` | `rulesets/soaml-1/soaml-1_rules.yaml` | 3 | SoaML 1.0.1 |
| `vdml-1` | `rulesets/vdml-1/vdml-1_rules.yaml` | 17 | VDML 1.0 |
| `uml-2` | `rulesets/uml-2/uml-2_rules.yaml` | 25 | UML 2.5.1 |
| `sysml-1` | `rulesets/sysml-1/sysml-1_rules.yaml` | 21 | SysML 1.5 |
| `uaf-1` | `rulesets/uaf-1/uaf-1_rules.yaml` | 84 | UAF 1.0 |
| `updm-2` | `rulesets/updm-2/updm-2_rules.yaml` | 88 | UPDM 2.1 |
| `raaml-1` | `rulesets/raaml-1/raaml-1_rules.yaml` | 27 | RAAML 1.0 |
| `togaf-9` | `rulesets/togaf-9/togaf-9_rules.yaml` | 8 | TOGAF 9.1 |
| `data-modeling-er` | `rulesets/data-modeling-er/data-modeling-er_rules.yaml` | 6 | None: a composite of public sources |
| `requirements` | `rulesets/requirements/requirements_rules.yaml` | 14 | ISO/IEC/IEEE 29148:2018 |
| `business-modeling` | `rulesets/business-modeling/business-modeling_rules.yaml` | 3 | OMG UML 1.3 to 1.5 business modeling profile |
| `zachman` | `rulesets/zachman/zachman_rules.yaml` | 7 | Not versioned: rules as stated in 1992 |
| `csdm-5` | `rulesets/csdm-5/csdm-5_rules.yaml` | 14 | CSDM 5 |
| `it4it` | `rulesets/it4it/it4it_rules.yaml` | 72 | IT4IT 3.0, read from the public draft |

`rules_path_or_content` accepts a path, an `https://` URL (v1.2.0+) or inline YAML.

From a skill folder a path is `../../rulesets/<id>/<id>_rules.yaml`. On desktop chat and Claude Cowork,
which cannot read the plugin's files by path, pass the YAML as inline content.

The ArchiMate ruleset is at `rulesets/archimate-3/archimate-3_rules.yaml` in this plugin. It replaces
`ruleset-archimate31`. It has 4 rules in place of 27: one checks every relationship against the
standard's table, the 14 rules the standard doesn't require are gone, and the six collaboration and
interaction rules become two warnings, because the standard states those numbers in prose. On a server
older than 3.6.5,
the old set is at `https://raw.githubusercontent.com/NovoCircle/ai-power-tools-skills/v3.6.4/ruleset-archimate31/archimate31_rules.yaml`,
because that server can't read this one.

```python
# 1. Run the shipped ruleset by path
result = ea_validate(operation="audit", params={
    "rules_path_or_content": "<plugin root>/rulesets/archimate-3/archimate-3_rules.yaml"
})

# 2. A ruleset of your own can sit under ~/.claude/ai-power-tools/rulesets/ (needs v3.6.0+,
#    which expands the `~`). Rulesets carry no SKILL.md, so they never go among the skills.
result = ea_validate(operation="audit", params={
    "rules_path_or_content": "~/.claude/ai-power-tools/rulesets/my-rules/my_rules.yaml"
})

# 3. Or pass inline YAML content as a string (no file or URL required)
result = ea_validate(operation="audit", params={
    "rules_path_or_content": "rules:\n- id: QUICK-001\n  ..."
})
```

## Response shape

```python
{
  "ok": True,
  "mode": "full_scan",
  "rules_evaluated": 12,
  "violation_count": 3,
  "violations": [
    {
      "rule_id": "WBA-TVR-001",
      "severity": "error",
      "element_id": 4231,
      "element_name": "Jane Doe (CEO)",
      "message": "required tag 'JobTitle' is empty",
      "remediation": "Populate all required Employee tagged values",
    },
    ...
  ],
}
```

## Authoring tips

- Keep `id` codes short and grouped by category (`WBA-TVR-*` for tagged-value rules, `WBA-CNX-*` for connector rules).
- Set `severity: warning` for "should-have" rules (e.g. *Department has Members*) and `error` only for structural violations.
- Mark rules `demo_trigger: true` when they cover the happy-path subset you want to run as a quick smoke check.
- Pair this skill with `ea-mdg-author` — for every required tag in your MDG, add a `tagged_value_required` rule here.

## Common pitfalls

- **Stereotype namespace.** EA stores stereotypes as `<YourTechID>::StereotypeName`. The sidecar matches on the bare name; `ea_validate` strips the prefix when comparing.
- **Quoting tag values.** `OrgLevel` is stored as a string even when typed `int`. Use `value_must_be_one_of: ["1", "2", "3", "4"]` (strings).
- **Connector direction.** `outgoing` = "this element is the source"; `incoming` = "this element is the target". Reports-to runs subordinate→manager, so an Employee's `reports-to` count is *outgoing* from the subordinate.

## EA Computer Use — Latency Guidelines

Validation is MCP-only but the verification step (checking violations are cleared) may require
opening a diagram or the EA UI. Wait before screenshotting — 2–15 seconds depending on the
operation — and never retry without confirming the previous action failed. Full wait-time table
and the standard action/wait/screenshot pattern:
[`../_shared/references/latency.md`](../_shared/references/latency.md).

## See also

- `ea-ruleset-author` — full workflow for building and publishing a complete ruleset for a modeling language (ArchiMate, BPMN, UML, SysML, custom MDG, etc.).
- `ea-mdg-author` — for the matching MDG XML (stereotypes + tags + OCL).
- `ea-mdg-deploy` — for getting that MDG into the model so rules have something to validate.

## Verify in EA's UI

EA reports success it has not earned, and reports failure as a modal dialog that blocks the
COM connection rather than as an error you can catch. Neither shows up in a tool response.

- **If a call seems to hang, screenshot EA and read the dialog before concluding anything.**
  It names the cause. Dismiss from the front — dialogs stack, and a later call can be queued
  behind one raised by an earlier one. Windows reporting EA as "Responding" means nothing.
- **After any diagram create or edit, reload the diagram, screenshot it, and look.**
  `ok: true` means rows were written, not that elements landed where you intended, that
  styling applied, or that the result is readable.
- **Without computer use**, say so and ask the user to look — never report a hang you have
  not diagnosed or a diagram you have not seen.

Full procedure: [`../_shared/references/ea-ui-verification.md`](../_shared/references/ea-ui-verification.md)
