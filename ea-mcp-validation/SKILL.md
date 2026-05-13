---
name: ea-mcp-validation
description: Author and run YAML sidecar conformance rules against a Sparx EA model via the validate_model MCP tool. Use when you need to check that an MDG-modeled repository meets its required tagged values, connector cardinality, and endpoint stereotype constraints.
---

# Validating a Sparx EA Model Against a YAML Sidecar Ruleset

*Tool: `validate_model` (AI Power Tools for EA, v0.5+)*

## When to use

- After importing or building a model that uses a custom MDG, to confirm every element carries the required tagged values.
- Before exporting a model snapshot for downstream consumption.
- As an automated gate in a model-CI pipeline.

## Sidecar YAML shape

A YAML file with a top-level `rules` list. Each rule has:

```yaml
- id: TVO-TVR-001
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
| `element` | `stereotypes.any_of` | Iterate every element whose stereotype is in the list. Add `tagged_value_filter` to narrow further. |
| `connector` | `connector_stereotype` | Iterate every connector with that stereotype. |

### Supported condition types

| `condition.type` | Use for |
|---|---|
| `tagged_value_required` | One or more tags on the selected element must be non-empty. |
| `tagged_value_constraint` | One or more tags must take a value from `value_must_be_one_of`. |
| `connector_count` | Element must have between `min` and `max` connectors of a given stereotype (`direction: incoming \| outgoing`). |
| `connector_endpoint_stereotype` | Connector source/target must be in `source_must_be_one_of` / `target_must_be_one_of`. |

## Running the validator

```python
# Full scan — every rule in the file
result = validate_model(rules_path_or_content="path/to/rules.yaml")

# Demo mode — only rules with demo_trigger: true
result = validate_model(
    rules_path_or_content="path/to/rules.yaml",
    mode="demo_validation",
)

# Scope to a single package subtree
result = validate_model(
    rules_path_or_content="path/to/rules.yaml",
    package_id=42,
)
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
      "rule_id": "TVO-TVR-001",
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

- Keep `id` codes short and grouped by category (`TVO-TVR-*` for tagged-value rules, `TVO-CNX-*` for connector rules).
- Set `severity: warning` for "should-have" rules (e.g. *Department has Members*) and `error` only for structural violations.
- Mark rules `demo_trigger: true` when they cover the happy-path subset you want to run as a quick smoke check.
- Pair this skill with `ea-mdg-author` — for every required tag in your MDG, add a `tagged_value_required` rule here.

## Common pitfalls

- **Stereotype namespace.** EA stores stereotypes as `TechID::StereotypeName`. The sidecar matches on the bare name; `validate_model` strips the prefix when comparing.
- **Quoting tag values.** `OrgLevel` is stored as a string even when typed `int`. Use `value_must_be_one_of: ["1", "2", "3", "4"]` (strings).
- **Connector direction.** `outgoing` = "this element is the source"; `incoming` = "this element is the target". Reports-to runs subordinate→manager, so an Employee's `reports-to` count is *outgoing* from the subordinate.

## See also

- `ea-mdg-author` — for the matching MDG XML (stereotypes + tags + OCL).
- `ea-mdg-deploy` — for getting that MDG into the model so rules have something to validate.
