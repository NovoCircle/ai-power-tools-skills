---
name: ea-ruleset-author
description: >
  Build a YAML validation ruleset for a modeling language (ArchiMate, BPMN, UML, SysML,
  custom MDG, etc.) and publish it to the AI Power Tools skills bundle. Covers the full
  workflow: research → rule-category planning → YAML authoring → testing → publishing.
  Use this skill at the start of every new language ruleset, and keep it open throughout.
min_server_version: "1.2.0"
---

# Authoring a Validation Ruleset for a Modeling Language

A **ruleset** is a YAML file consumed by `validate_model` (server ≥ 1.2.0). It describes
what a correctly-formed model should look like for a given modeling language, and reports
every element or connector that does not conform. Once published to the skills bundle,
any user can run it with a single URL argument — no local file required.

This skill describes the repeatable six-phase workflow for building one ruleset from
scratch. Follow the phases in order, one language at a time.

---

## Overview — What You're Building

```
ruleset-{lang}/
└── {lang}_rules.yaml        ← one YAML file, all rules for the language
```

The YAML has two top-level keys:

| Key | Purpose |
|-----|---------|
| `meta:` | Human-readable header: language, version, sources, severity legend |
| `rules:` | List of rule objects, one per conformance constraint |

The ArchiMate 3.1 ruleset (`ruleset-archimate31/archimate31_rules.yaml`) is the canonical
reference implementation. Read it before starting a new language.

---

## Phase 1 — Research the Language Specification

### What to find

You need three things from the spec before writing a single rule:

1. **Element type table** — a complete list of all concept/element names and which
   structural category each belongs to (e.g., Active Structure, Behavior, Passive
   Structure, Motivation, etc.).
2. **Relationship validity table** — which relationship types are allowed between which
   element categories (or specific element pairs). This is usually in an appendix.
3. **Structural constraints** — "A Collaboration MUST have at least two members",
   "An Interaction MUST be assigned to a Collaboration", etc.

### Where to look

| Language | Primary source | Relationship table |
|----------|---------------|-------------------|
| ArchiMate 3.1 | pubs.opengroup.org/architecture/archimate31-doc/ | Appendix B |
| ArchiMate 3.1 (practical) | Archi Tool relationships.xml on GitHub | XML file |
| BPMN 2.0 | omg.org/spec/BPMN/2.0 | Table 7.1 |
| UML 2.5 | omg.org/spec/UML/2.5.1 | §7 Core |
| SysML 1.6 | omg.org/spec/SysML/1.6 | §9, §11, §15 |
| Custom MDG | The MDG XML file itself | `<Stereotypes>` section |

### Output of this phase

A short notes doc (or a scratch pad in the conversation) listing:

- Element categories (e.g., Active Structure = [BusinessActor, BusinessRole, ...])
- Relationship endpoint constraints (e.g., Assignment: source ∈ Active Structure, target ∈ Behavior)
- Structural well-formedness rules (e.g., Collaboration needs ≥ 2 members)
- Specification citations you'll use (`[S1 §5.2]`, `[S2 Table 7.1]`, etc.)

---

## Phase 2 — Plan Rule Categories

Group the rules you found in Phase 1 into named categories before writing YAML. This
determines your ID scheme and keeps the file organized.

### Standard category scheme (adapt as needed)

| Category code | Covers | Selector type |
|--------------|--------|---------------|
| `REL` | Relationship endpoint validity | `connector` |
| `COL` | Collaboration / group membership | `element` (connector_count) |
| `INT` | Interaction assignment to Collaboration | `element` (connector_count) |
| `WFR` | Well-formedness completeness (orphan checks) | `element` (connector_count) |
| `IMP` | Special layer / migration structures | `element` or `connector` |
| `CLR` | Cross-layer endpoint patterns | `connector` |

Not every language needs every category. BPMN might have `SEQ` (sequence flow), `GWY`
(gateway routing), `EVT` (event structure). Invent categories that match the language.

### ID scheme

```
{LANG}-{CAT}-{NNN}
```

Examples: `AM31-REL-001`, `BPMN2-SEQ-003`, `UML25-CLN-001`, `MYMDG-TV-002`

Use three-digit zero-padded numbers within each category. Leave gaps (e.g., 001, 003,
007) if you expect to insert rules later — or don't; renumbering is fine at authoring
time before publishing.

### Demo-trigger selection

Mark ~30% of rules `demo_trigger: true` — these run in `mode: "demo_validation"` for
quick checks. Choose rules that:
- Cover the highest-volume element types
- Represent the most commonly made mistake for that language
- Collectively give a meaningful signal in <5 seconds

---

## Phase 3 — Write the YAML

### File and directory naming

```
ruleset-{lang}/
└── {lang}_rules.yaml
```

Use lowercase, hyphens in the directory name, underscores in the file name. Examples:
`ruleset-bpmn2/bpmn2_rules.yaml`, `ruleset-uml25/uml25_rules.yaml`.

### Start with the meta block

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

### Rule template

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

### Condition type reference

| `condition.type` | Use for | Key fields |
|-----------------|---------|-----------|
| `connector_endpoint_stereotype` | Connector source/target stereotype constraints | `source_must_be_one_of`, `target_must_be_one_of` |
| `connector_count` | Element must have N connectors of a given stereotype | `connector_stereotype`, `direction` (incoming\|outgoing), `min`, `max` |
| `tagged_value_required` | Element must have non-empty tags | `tags: [{name, must_be_non_empty}]` |
| `tagged_value_constraint` | Tag must be one of an enum | `tags: [{name, value_must_be_one_of}]` |

### Writing connector endpoint rules

The most powerful rule type. Write them in this order:

1. List ALL valid source stereotypes (err toward inclusion — EA's MDG may have inherited
   subtypes you don't know about)
2. List ALL valid target stereotypes
3. Write the description explaining WHY these constraints exist
4. Set severity: `error` — endpoint violations are always structural

**EA stereotype names:** EA stores stereotypes as bare names without namespace prefix.
The selector `connector_stereotype: Assignment` matches connectors whose stereotype is
`Assignment`, regardless of whether EA shows it as `ArchiMate3::Assignment` internally.
Use the bare name everywhere in the YAML.

### Writing connector count rules

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

### Section comments

Use ASCII section headers to visually group rules:

```yaml
  # ═══════════════════════════════════════════════════════════════════════════
  # SECTION 1 — RELATIONSHIP ENDPOINT VALIDITY (REL)
  #
  # One or two lines explaining what this section covers and which spec
  # sections these rules come from.
  # ═══════════════════════════════════════════════════════════════════════════

  # ── Assignment ──────────────────────────────────────────────────────────────

  - id: LANG-REL-001
    ...
```

---

## Phase 4 — Test

### Test 1: Zero violations on a clean known-good model

Open `WestbrookBank.qea` (or any clean baseline model) and run:

```python
result = validate_model(
    rules_path_or_content="path/to/ruleset.yaml"
)
```

**Expected:** `violation_count: 0` (assuming the model doesn't use this language's
stereotypes). If you get violations, check whether the stereotype names in the YAML
match what EA actually stores — inspect a connector or element via `get_element()` or
`get_connector()` to see the raw stereotype string.

### Test 2: URL fetch works

After committing the file to the skills repo, test the round-trip:

```python
result = validate_model(
    rules_path_or_content=(
        "https://raw.githubusercontent.com/NovoCircle/ai-power-tools-skills"
        "/main/ruleset-{lang}/{lang}_rules.yaml"
    )
)
```

**Expected:** `ok: true`, `rules_evaluated: {N}` matching your rule count. If you get
`rules_fetch_failed`, the file isn't on the right branch/path yet.

### Test 3: Rules fire on intentional violations (optional but recommended)

Create a scratch package in your test model with deliberate violations (e.g., draw an
Assignment connector from a DataObject to a BusinessProcess — a clear endpoint error).
Run the ruleset scoped to that package:

```python
result = validate_model(
    rules_path_or_content="path/to/ruleset.yaml",
    package_id={scratch_package_id}
)
```

Verify that exactly the rules you expect are reported.

---

## Phase 5 — Publish to the Skills Bundle

### Step 1: Place the file

```
NovoCircle/ai-power-tools-skills/
└── ruleset-{lang}/
    └── {lang}_rules.yaml
```

Commit and push to `main`.

### Step 2: Compute SHA256

```powershell
# Windows
certutil -hashfile ruleset-{lang}\{lang}_rules.yaml SHA256
# The hash output (remove spaces) goes in manifest.json
```

### Step 3: Update manifest.json

Add a new entry to the `skills` array:

```json
{
  "name": "ruleset-{lang}",
  "title": "{Language Name} Validation Ruleset",
  "description": "{N}-rule {Language Name} conformance ruleset for use with validate_model. {One sentence on what it covers.}",
  "version": "1.0.0",
  "min_server_version": "1.2.0",
  "files": [
    "ruleset-{lang}/{lang}_rules.yaml"
  ],
  "sha256": {
    "ruleset-{lang}/{lang}_rules.yaml": "{computed_sha256}"
  }
}
```

**Always set `min_server_version: "1.2.0"`** for rulesets — that's when URL fetching
was added and is the minimum version that can consume a hosted ruleset directly.

Bump `bundle_version` (patch increment: 1.3.0 → 1.3.1).

### Step 4: Cut a GitHub release on the skills repo

After committing manifest.json:

```powershell
cd C:\SparxServices\products\ai-power-tools-skills
git add ruleset-{lang}/ manifest.json
git commit -m "feat(ruleset): add {Language} {version} conformance ruleset ({N} rules)"
git push origin main

# Then cut a release on NovoCircle/ai-power-tools-skills so install_skills
# picks up the new manifest
gh release create "bundle-v{bundle_version}" \
  --repo NovoCircle/ai-power-tools-skills \
  --title "Skills bundle {bundle_version} — {Language} ruleset" \
  --notes "Adds {Language} validation ruleset ({N} rules). Requires server ≥ 1.2.0."
```

### Step 5: Verify via install_skills

```python
# List available skills — new ruleset should appear
list_available_skills()

# Install it
install_skills(names=["ruleset-{lang}"])

# Run it locally
validate_model(rules_path_or_content="~/.claude/skills/ruleset-{lang}/{lang}_rules.yaml")
```

---

## Ruleset Catalog

Track progress here as new rulesets are authored.

| Language | Directory | Rules | Status | Server req |
|----------|-----------|-------|--------|-----------|
| ArchiMate 3.1 | `ruleset-archimate31` | 27 | ✅ Published (bundle 1.3.0) | ≥ 1.2.0 |
| BPMN 2.0 | `ruleset-bpmn2` | — | ⏳ Planned | ≥ 1.2.0 |
| UML 2.5 | `ruleset-uml25` | — | ⏳ Planned | ≥ 1.2.0 |
| SysML 1.6 | `ruleset-sysml16` | — | ⏳ Planned | ≥ 1.2.0 |
| TOGAF ADM | `ruleset-togaf-adm` | — | ⏳ Planned | ≥ 1.2.0 |

---

## Common Pitfalls

**Stereotype name mismatch.** The most common failure. EA stores stereotypes in different
forms depending on MDG version. Check with:
```python
get_element(element_id=N)   # look at the "stereotype" field
# or
execute_sql(sql="SELECT stereotype FROM t_object WHERE Object_ID = N")
```
The raw value is what you put in the YAML. The validate_model tool strips the `Namespace::`
prefix, so use bare names.

**Wrong connector direction.** `direction: incoming` means the edge ENDS at this element
(element is the arrow target). `direction: outgoing` means the edge STARTS here (element
is the arrow source). When in doubt: draw the arrow in your head, then decide which end
the current element is at.

**Over-specifying targets on cross-layer rules.** For broad relationship types like
`Association`, the valid targets are nearly every element type. It's often better to write
a rule that checks the *source* only (e.g., "Influence must target Motivation elements")
and leave the source unrestricted, rather than enumerate 50 source stereotypes.

**Quoting vs unquoting stereotype names.** Both work in YAML:
```yaml
any_of: [BusinessActor]           # OK — YAML bare string
any_of: ["BusinessActor"]         # OK — explicitly quoted
```
Use quotes when a stereotype name contains special YAML characters (`:`, `#`, `&`, etc.).

**Not testing the URL before publishing.** Commit the file, wait for GitHub to index it
(usually <10 seconds), then test `validate_model` with the raw.githubusercontent.com URL
before updating the manifest. A broken URL in the manifest causes `install_skills` to fail
for all users.

**`meta:` block is not validated.** The server reads only `rules:`. The `meta:` block is
ignored at runtime but is critical for human readers and for future tooling. Always include
it; always cite sources.

---

## See Also

- `ea-mcp-validation` — YAML syntax reference and how to run the validator
- `ea-mdg-author` — Authoring the MDG Technology XML that defines the stereotypes you're validating
- ArchiMate 3.1 reference implementation: `ruleset-archimate31/archimate31_rules.yaml`
