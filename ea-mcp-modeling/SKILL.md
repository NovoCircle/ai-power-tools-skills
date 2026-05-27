---
name: ea-mcp-modeling
description: How to build and maintain Sparx EA models through the ea-mcp-server MCP tools â€” correct build order, known defects and workarounds, verification patterns, and governance considerations. Use this skill whenever constructing or modifying an EA repository via MCP tool calls.
---

# EA Modeling via MCP â€” Patterns and Practices

*Grounded in the Westbrook Bank full-repository build session.  Every pattern here either
prevented a defect or fixed one.*

> **â—  Verification discipline â€” trust the EA model, not your memory.**
>
> When a user (or a downstream step) asks anything about the current state of the
> model â€” *“does element X exist?”*, *“what's in package P?”*, *“is connector C still
> there?”*, *“what's the tagged value of T on element E?”* â€” you MUST answer from a
> read tool call issued **in the current turn**, not from your memory of what you
> created earlier in the session. Memory is an index, not a source of truth.
>
> This is the single largest cause of perceived hallucinations in this tool. Elements
> can be renamed, moved, deleted, or silently fail to persist between turns; another
> user or script can mutate the model out-of-band; an EA crash can roll back a
> transaction. Any answer about model state that is not backed by a fresh read call
> is a guess, and confident guesses destroy user trust.
>
> **Canonical verification primitives by question type:**
>
> | Question | Tool |
> |---|---|
> | Does element X exist? | `ea_model("find_elements_by_name", {"name": "X", "exact": True})` or `ea_analyze("execute_sql", {"sql": "SELECT Object_ID FROM t_object WHERE Name = 'X'"})` |
> | Full state of element by ID | `ea_model("get_element", {"element_id": <id>})` |
> | What's in package P? | `ea_model("list_elements_in_package", {"package_id": <id>})` |
> | Package hierarchy | `ea_model("list_package_tree", {"package_id": <id>})` or `list_child_packages` |
> | Tagged values on E? | `ea_model("get_element_tags", {"element_id": <id>})` or SQL against `t_objectproperties` |
> | Connectors on/around E? | `ea_model("list_connectors_for_element", {"element_id": <id>})` or `ea_analyze("trace_connectors", ...)` |
> | What stereotypes are in use? | `ea_analyze("summarize_stereotype_usage", {})` |
> | What connector patterns are in use? | `ea_analyze("summarize_connector_patterns", {})` |
> | What's on diagram D? | `ea_diagram("get_diagram", {"diagram_id": <id>})` |
> | Anything not covered above | `ea_analyze("execute_sql", {"sql": "..."})` â€” always available, always authoritative |
>
> **Rules:**
>
> 1. **Never assert model state from prior-turn memory.** Even one turn old is too
>    old for a state assertion. Re-query.
> 2. **Returned IDs/GUIDs are the only authoritative reference.** Names can collide
>    or be renamed. Persist IDs, not names, across turns.
> 3. **After a `/clear` or any session boundary, your memory is gone.** Re-orient
>    with `ea_repository("get_repository_info")` and targeted SQL before answering
>    anything about model contents.
> 4. **After long sessions (>30 turns), reverify before any factual claim.**
>    Silent failures and out-of-band changes accumulate.
> 5. **If a verify call is too expensive to run, say so.** "I created X earlier in
>    this session but haven't re-verified" is acceptable; "X exists" without a
>    fresh read call is not.
>
> The cost of a verification call is almost always < 1k tokens (see Â§15, Â§17). The
> cost of one confidently-wrong answer is your user's trust in everything else you
> said.

> **Server v1.3.0 â€” meta-tool dispatch refactor.** All individual MCP tools have been
> consolidated into 6 meta-tool dispatchers: `ea_model`, `ea_diagram`, `ea_analyze`,
> `ea_mdg`, `ea_validate`, and `ea_repository`. Call syntax: instead of
> `create_package(name=”Foo”, parent_package_id=1)`, use
> `ea_model(operation=”create_package”, params={“name”: “Foo”, “parent_package_id”: 1})`.
> All underlying operations and behavior are unchanged â€” only the dispatch layer is new.

> **Writing raw SQL?** EA's table/column naming is deeply inconsistent and
> the #1 source of wasted turns is "invalid column name" errors (e.g.,
> `t_object.Note` is SINGULAR; `t_taggedvalue` uses `TagValue` not `Value`;
> connector endpoints are `Start_Object_ID`/`End_Object_ID`). Before writing
> any non-trivial SQL via `ea_analyze(operation="execute_sql", ...)`, call
> `ea_analyze(operation="describe_table", params={"table_name": "t_xxx"})` or
> consult [`references/sql_schema.md`](references/sql_schema.md). The server
> now pre-validates SQL and returns `did_you_mean` suggestions before
> round-tripping to EA.

---

## 0. Pre-flight Checks

Before creating anything, orient yourself in the live repository.

```
ea_model(operation=”list_root_packages”, params={})
```

This returns every package at `Parent_ID = 0` (the true repository root) **and** at
`Parent_ID = 1` (EA's default “Model” node).  Note the IDs â€” you will need the correct
parent ID for your top-level package.

```
ea_repository(operation=”get_repository_info”, params={})
```

Confirms the project file and EA version.  If this fails, EA is not running or the MCP
server is not connected â€” stop and fix the connection before issuing any write calls.

The response also includes a `diagnostics` block â€” confirm whether opt-in diagnostics
is active and where reports will be written. See Â§16.

---

## 0.5 Decision: VBScript vs. MCP path

The MCP path is excellent for reasoning-heavy work but pays a per-call round-trip cost.
For pure deterministic catalog inserts at high volume, in-process VBScript via
**Specialize â†’ Scripting** in EA is faster and consumes no agent context. Rule of thumb:

| Workload | Path |
|----------|------|
| â‰¤30 elements (any catalog) | MCP â€” use `ea_model(“create_elements_bulk”)` |
| 30â€”100 elements | Either; MCP bulk is acceptable, VBScript is faster |
| >100 elements as a one-shot insert | VBScript |
| Verification, gap analysis, refinement, refactoring | **MCP, always** â€” token-cheap and reasoning-friendly |
| Diagram authoring (placing existing elements) | MCP â€” use `ea_diagram(“add_elements_to_diagram_bulk”)` |

For mixed workloads, do the bulk seed in VBScript, then drive verification and
incremental refinement through MCP.

---

## 1. Build Order

Always follow this sequence.  Skipping phases or working out of order causes referential
integrity problems that are hard to diagnose.

```
Phase 0 â€” Pre-flight (ea_model(“list_root_packages”), ea_repository(“get_repository_info”))
Phase 1 â€” Package hierarchy  (all packages, leaf-to-root NOT required; parent-first IS required)
Phase 2 â€” Elements           (create element â†’ set ALL tagged values immediately â†’ next element)
Phase 3 â€” Connectors         (all relationships between elements)
Phase 4 â€” Diagrams           (create diagram â†’ update StyleEx â†’ add elements)
Phase 5 â€” Verification       (ea_analyze(“execute_sql”) spot checks; element counts; connector queries)
```

**Why elements before connectors:** `create_connector` needs both endpoint `Object_ID`
values.  If you try to create connectors while elements are still being built you will
reference IDs that don't exist yet.

**Why tags atomically with element creation (v0.3.0+):** As of v0.3.0, pass tags via the
inline `tagged_values={...}` parameter on `create_element` (or as a key inside each
`create_elements_bulk` spec). One round trip per element instead of N+1. This is the
recommended pattern; the old "create then loop set_tagged_value" idiom still works but
costs roughly 5Ã— the round trips for typical catalog elements.

### Concurrency limits

**Do not issue parallel `create_package` calls.**  EA's COM single-threaded apartment
model serialises all COM calls through one thread; sending multiple `create_package` calls
in parallel causes race conditions in EA's internal package-tree cache and produces
intermittent `Object reference not set` or `Invalid Class` COM errors.

**Safe concurrency rules:**

| Operation | Max parallel calls | Notes |
|---|---|---|
| `ea_model("create_package")` | 1 (sequential only) | EA package tree is not thread-safe |
| `ea_model("create_element")` / `ea_model("create_elements_bulk")` | 1 at a time | Sequential is safe; bulk is preferred over many parallel singles |
| `ea_model("create_connector")` / `ea_model("create_connectors_bulk")` | 1 at a time | Same COM constraint |
| `ea_analyze("execute_sql")` (read-only) | Up to ~3 | Read path is safer but still best kept sequential |
| `ea_model("get_element")`, `ea_model("get_package")`, `ea_diagram("get_diagram")` | Up to ~3 | Read-only; usually safe |

In practice: **run all write calls sequentially.**  Use bulk tools
(`ea_model("create_elements_bulk")`, `ea_model("create_connectors_bulk")`, `ea_diagram("add_elements_to_diagram_bulk")`) to
amortise latency rather than firing multiple single-entity calls in parallel.

---

## 2. Creating the Root Package

### Root package parent (REQ-001) â€” fixed in v1.0.0

EA's repository root can be at parent ID 0 or 1 depending on how the project was created.
Always confirm the correct parent before creating your top-level package:

**Correct approach:**
```
ea_model(operation="list_root_packages", params={})
# â†’ find the ID of your intended parent (often 0 or 1 depending on server version)
ea_model(operation="create_package", params={"name": "WestbrookBank", "parent_package_id": <root_id>})
```

After creation, **verify** with SQL:
```
ea_analyze(operation="execute_sql", params={"sql": "SELECT Package_ID, Name, Parent_ID FROM t_package WHERE Name = ‘WestbrookBank’"})
```

If `Parent_ID` is `1` but you wanted `0`, fix it immediately:
```
ea_analyze(operation="execute_sql", params={"sql": "UPDATE t_package SET Parent_ID = 0 WHERE Name = ‘WestbrookBank’"})
```

This fix must be done before building any child packages â€” child `Parent_ID` values are set
at creation time and will be correct relative to their parent regardless of the root fix.

---

## 3. Package Names Containing `&`

### Ampersand encoding (REQ-002) â€” fixed in v1.0.0

EA's COM layer HTML-encodes `&` on some paths.  A package named `”Operations & Support”`
may be stored as `”Operations &amp; Support”`, breaking all path-based lookups.

**Defensive pattern â€” always verify after creating a package whose name contains `&`:**

```python
# 1. Create the package (name will be stored with &amp;)
result = ea_model(operation="create_package", params={"name": "Operations & Support", "parent_package_id": <id>})
pkg_id = result["package_id"]

# 2. Verify stored name
ea_analyze(operation="execute_sql", params={"sql": f"SELECT Name FROM t_package WHERE Package_ID = {pkg_id}"})
# â†’ will show "Operations &amp; Support"

# 3. Fix immediately with update_package
ea_model(operation="update_package", params={"package_id": pkg_id, "name": "Operations & Support"})

# 4. Re-verify
ea_analyze(operation="execute_sql", params={"sql": f"SELECT Name FROM t_package WHERE Package_ID = {pkg_id}"})
# â†’ should now show "Operations & Support"
```

**Affected characters:** `&` â†’ `&amp;`.  Also watch for `<`, `>`, `"` if they appear in
names.

---

## 4. Element Creation and Tagged Values

### Recommended pattern (v0.3.0+)

**More than ~5 elements at once â†’ use `create_elements_bulk`:**

```python
ea_model(operation="create_elements_bulk", params={"specs": [
    {
        "package_id": app_pkg_id,
        "name": "Customer Portal",
        "type": "Component",
        "stereotype": "WBABusinessApplication",
        "properties": {"Notes": "Internet banking front-end"},
        "tagged_values": {
            "criticality": "Mission Critical",
            "lifecycle": "Current",
            "businessOwner": "Retail Banking Ops",
            "technicalOwner": "Digital Eng",
            "dataClassification": "Confidential",
            "regulatoryScope": "PCI-DSS",
            "modelGovernanceClass": "Core",
        },
    },
    # ... more specs ...
]})
```

The bulk call is idempotent (existing name + package + stereotype is skipped, not
duplicated) and returns a structured `{created, skipped, failed, results}` summary.
Failures don't abort the batch.

**Single element (still valid for one-offs):**

```python
ea_model(operation=”create_element”, params={
    “package_id”: app_pkg_id,
    “name”: “Customer Portal”,
    “type”: “Component”,
    “stereotype”: “WBABusinessApplication”,
    “properties”: {“Notes”: “...”},
    “tagged_values”: {“criticality”: “Mission Critical”, “lifecycle”: “Current”},
})
```

The `properties` and `tagged_values` arguments are safe to use together. Tagged values are
idempotent by name â€” calling `ea_model(operation=”update_element”, params={“element_id”: ..., “tagged_values”: {“k”: “v2”}})` on an element where `k=v1` already exists
overwrites in place rather than creating a duplicate.

### MDG-native element creation â€" `create_element_in_language`

When the target element type is defined by an MDG profile (ArchiMate3, BPMN2.0, or a
custom MDG like WBA), prefer `create_element_in_language` over plain `create_element`.
It routes through EA’s COM `CreateElementInPackage` path which writes the stereotype into
`t_xref` (the MDG profile application store) rather than only `t_object.Stereotype`, and
sets the correct base metaclass automatically.

```python
ea_model(operation="create_element_in_language", params={
    "package_id": app_pkg_id,
    "name": "Customer Portal",
    "language_id": "WestbrookBankArchitecture",  # MDG Technology ID
    "language_type": "WBABusinessApplication",   # stereotype name within that MDG
    "properties": {"Note": "Internet banking front-end"},
    "tagged_values": {"criticality": "Mission Critical", "lifecycle": "Current"},
})
```

**When to use which:**

| Scenario | Use |
|---|---|
| Creating MDG-profile elements (ArchiMate, BPMN, custom MDG) | `ea_model("create_element_in_language")` |
| Generic UML elements (Class, Component, Node, etc.) | `ea_model("create_element")` |
| Bulk creation with MDG types | `ea_model("create_elements_bulk")` with `language_id`+`language_type` in each spec |
| Plain `ea_model("create_element")` with MDG `stereotype=` | Writes only `t_object.Stereotype`; may silently fail for some MDG types |

**Bulk with MDG routing:** Pass `language_id` and `language_type` inside each spec in
`create_elements_bulk`.  When both are present, the bulk call automatically routes that
spec through `create_element_in_language` instead of `create_element`:

```python
ea_model(operation="create_elements_bulk", params={"specs": [
    {
        "package_id": app_pkg_id,
        "name": "Customer Portal",
        "language_id": "WestbrookBankArchitecture",
        "language_type": "WBABusinessApplication",
        "tagged_values": {"criticality": "Mission Critical"},
    },
]})
```

### Stereotype â†’ Object_Type mapping

The WBA MDG stereotypes map to these EA `Object_Type` values:

| Stereotype | Object_Type (`ea_model("create_element")` `element_type`) |
|------------|---------------------------------------------|
| `WBABusinessApplication` | `Component` |
| `WBAVendorSystem` | `Component` |
| `WBABusinessService` | `Component` |
| `WBAAIService` | `Component` |
| `WBAAIGateway` | `Component` |
| `WBADataAsset` | `Object` |
| `TechNode` | `Node` |

### Full WBA MDG tagged value set

Set all applicable tags in one block immediately after `create_element`:

```
criticality         â†’ "Mission Critical" | "Business Critical" | "Important" | "Standard"
lifecycle           â†’ "Strategic" | "Current" | "Contained" | "Phasing Out" | "Deprecated" | "Retired"
businessOwner       â†’ team/person name string
technicalOwner      â†’ team/person name string
dataClassification  â†’ "Public" | "Internal" | "Confidential" | "Restricted"
regulatoryScope     â†’ "PCI-DSS" | "SOX" | "GDPR" | "CCPA" | "" (blank = none)
vendor              â†’ vendor name (for WBAVendorSystem only; blank for internal apps)
product             â†’ product name (for WBAVendorSystem only)
pciScopeJustification  â†’ free text (required when regulatoryScope contains "PCI")
pciControlOwner        â†’ team name (required when regulatoryScope contains "PCI")
modelGovernanceClass   â†’ "Core" | "Extended" | "Peripheral"
humanInLoop            â†’ "true" | "false" (for AI elements only)
auditLogging           â†’ "true" | "false" (for AI elements only)
```

### Verification after tagging

Spot-check a tagged element with SQL to confirm storage:
```
ea_analyze(operation=”execute_sql”, params={“sql”: “””
    SELECT p.Property, p.Value
    FROM t_objectproperties p
    WHERE p.Object_ID = <element_id>
    ORDER BY p.Property
“””})
```

Expect one row per tag.  If a tag is missing, `ea_model(operation=”set_tagged_value”, ...)` did not persist â€” retry
the call.  This is rare but happens on the first call to a new MDG-enabled project while
the tag schema is being initialised.

---

## 4.5 Stereotype Persistence â€” Where EA Stores What

**This is the most common source of silent failures.**  EA stores stereotype information
in up to three separate places, and which place it writes to depends on which tool and
path you use.

### Three stereotype storage locations

| Store | Table | Column | What writes here | What reads here |
|---|---|---|---|---|
| Simple stereotype | `t_object` | `Stereotype` | `ea_model(“create_element”)` with `stereotype=`, `ea_model(“update_element”)` with `properties={“Stereotype”:}` | EA browser, most queries |
| StereotypeEx (full MDG path) | `t_object` | `StereotypeEx` | `ea_model(“update_element”)` with `properties={“StereotypeEx”:}` | EA validation, profile-aware tools |
| MDG profile application | `t_xref` | `Description` | `ea_model(“create_element_in_language”)`, `ea_model(“create_elements_bulk”)` with `language_id`+`language_type` | EA MDG engine, diagram rendering |

### How each tool writes stereotypes

```
ea_model(operation=”create_element”, params={“stereotype”: “WBABusinessApplication”, ...})
  â†' writes t_object.Stereotype = “WBABusinessApplication”
  â†' does NOT write t_xref (MDG profile not applied)
  â†' element may not render correctly in MDG-aware diagrams

ea_model(operation=”create_element_in_language”, params={“language_id”: “WestbrookBankArchitecture”, “language_type”: “WBABusinessApplication”, ...})
  â†' writes t_object.Stereotype = “WBABusinessApplication”
  â†' writes t_object.StereotypeEx = “WBABusinessApplication=WestbrookBankArchitecture::WBABusinessApplication;”
  â†' writes t_xref row (MDG profile application, BaseClass=”element”)
  â†' element renders correctly in MDG-aware diagrams

ea_model(operation=”update_element”, params={“element_id”: ..., “properties”: {“StereotypeEx”: “WBABusinessApplication=WestbrookBankArchitecture::WBABusinessApplication;”}})
  â†' writes t_object.StereotypeEx
  â†' does two Update() calls internally (first for other props, second specifically for StereotypeEx)
  â†' returns stereotype_warning if EA rejected the value (readback is empty after Update)
  â†' does NOT create t_xref row â€” less reliable than create_element_in_language
```

### How to verify stereotype persistence

```sql
-- 1. Check t_object (basic + StereotypeEx)
SELECT Object_ID, Name, Stereotype, StereotypeEx
FROM t_object
WHERE Object_ID = <element_id>

-- 2. Check t_xref (MDG profile application)
SELECT XrefID, [Type], [Name], Client, Supplier, [Description]
FROM t_xref
WHERE Client = '<element_guid>'
  AND [Type] = 'element'

-- 3. Check tagged values (confirms MDG profile is active)
SELECT Property, [Value]
FROM t_objectproperties
WHERE Object_ID = <element_id>
```

If step 2 returns no rows, the MDG profile was not applied â€” the element's stereotype
is cosmetic only.  To fix, delete and recreate the element using `create_element_in_language`.

### Diagnosing `update_element` StereotypeEx failures

`update_element` now returns `stereotype_warning` in the response when the StereotypeEx
write was rejected by EA.  Check for this key:

```python
result = ea_model(operation=”update_element”, params={“element_id”: <id>, “properties”: {“StereotypeEx”: “...”}})
if result.get(“stereotype_warning”):
    # EA rejected the stereotype â€” use create_element_in_language instead
    print(result[“stereotype_warning”])
```

The most common rejection cause: the element's `Object_Type` (`t_object.Object_Type`)
doesn't match what the MDG profile expects as the base metaclass.  You cannot change
`Object_Type` after creation â€” recreate via `create_element_in_language`.

---

## 5. Creating Diagrams with MDG Types

### Preferred approach â€” `create_diagram_in_language`

Use `create_diagram_in_language` when the target diagram type is defined by an MDG
profile.  It routes through EA's COM diagram-factory path and sets both the EA base type
and the MDG `StyleEx` in one call, without needing the two-step workaround:

```python
ea_diagram(operation=”create_diagram_in_language”, params={
    “name”: “Application Landscape”,
    “package_id”: <id>,
    “language_id”: “ArchiMate3”,              # MDG Technology ID
    “language_type”: “Application”,           # diagram type within that MDG
})
```

Common language_id / language_type pairs:

| Diagram | language_id | language_type |
|---|---|---|
| ArchiMate Application | `ArchiMate3` | `Application` |
| ArchiMate Technology | `ArchiMate3` | `Technology` |
| BPMN Business Process | `BPMN2.0` | `Business Process` |
| UML Component | `UML` | `Component` |

### Fallback â€” two-step workaround for `create_diagram`

If `create_diagram_in_language` is unavailable or you need fine-grained control:

```python
# Step 1: create with the base EA type (not the MDG string)
result = ea_diagram(operation=”create_diagram”, params={
    “name”: “Application Landscape”,
    “package_id”: <id>,
    “type”: “Logical”,          # use EA base type, not “ArchiMate3::Application”
})
diagram_id = result[“diagram_id”]

# Step 2: set the MDG StyleEx immediately
ea_diagram(operation=”update_diagram”, params={
    “diagram_id”: diagram_id,
    “properties”: {“StyleEx”: “MDGDgm=ArchiMate3::Application;”},
})
```

### MDG type â†’ EA base type â†’ StyleEx mapping

| Intended diagram type | EA base type (`ea_diagram("create_diagram")` `type`) | StyleEx value |
|----------------------|--------------------------------------|---------------|
| ArchiMate Application | `Logical` | `MDGDgm=ArchiMate3::Application;` |
| ArchiMate Technology | `Logical` | `MDGDgm=ArchiMate3::Technology;` |
| BPMN Business Process | `Analysis` | `MDGDgm=BPMN2.0::Business Process;` |
| UML Component | `Component` | `MDGDgm=UML::Component;` |
| UML Class | `Class` | *(no StyleEx needed â€” native EA type)* |
| UML Sequence | `Sequence` | *(no StyleEx needed)* |

### Verify diagram type was stored

```
ea_analyze(operation="execute_sql", params={"sql": "SELECT Diagram_Type, StyleEx FROM t_diagram WHERE Diagram_ID = <id>"})
```

For a BPMN diagram, `Diagram_Type` should contain `"Business Process"` or `"BPMN"`, and
`StyleEx` should contain `"MDGDgm=BPMN2.0::Business Process"`.

---

## 6. Diagram Layout

### `layout_diagram` â€” works as of server v1.0.0

The earlier GUID bug (REQ-004) is **fixed in v1.0.0**.  Call `layout_diagram` freely.

`ea_diagram(“add_elements_to_diagram_bulk”)` auto-applies `”Hierarchical”` layout after placement by
default (`layout=”Hierarchical”`).  You can pass `layout=None` to skip it, or pass any
supported style name (`”Circular”`, `”Digraph”`, etc.) to override.

To manually trigger layout on a diagram at any time:
```
ea_diagram(operation=”layout_diagram”, params={“diagram_id”: <id>, “style”: “Hierarchical”})
```

---

## 6.5 Connector Visibility on Diagrams â€” t_diagramlinks

**This is the most important diagram trap.**  Placing elements on a diagram via
`add_elements_to_diagram_bulk` does NOT automatically render the connectors between
those elements.  EA stores two completely independent things:

| Store | What it is | Tools that write it |
|---|---|---|
| `t_connector` | The logical connector (exists in the model) | `ea_model("create_connector")`, `ea_model("create_connectors_bulk")` |
| `t_diagramlinks` | The diagram-visible rendering of that connector | `ea_diagram("add_connectors_to_diagram_bulk")` (auto-called by `ea_diagram("add_elements_to_diagram_bulk")`) |

If `t_diagramlinks` rows are missing, connectors are invisible on the diagram even though
`ea_model("get_connector")` and `ea_analyze("execute_sql")` against `t_connector` show them present.

**`ea_diagram(“add_elements_to_diagram_bulk”)` auto-repairs this** (since v1.0.4):
- After placing elements it calls `ea_diagram("add_connectors_to_diagram_bulk")` with `connector_ids=None`
  which auto-discovers every connector whose both endpoints are already on the diagram and
  are not yet in `t_diagramlinks`.
- This is controlled by the `auto_show_connectors=True` default.

If you manually add elements via `ea_diagram(“add_element_to_diagram”)` (single-element variant), you
must call `ea_diagram(operation=”add_connectors_to_diagram_bulk”, params={“diagram_id”: <id>})` afterwards yourself â€” or use
the bulk variant which handles it automatically.

**To repair a diagram with missing connector lines** (e.g. diagrams built with v1.0.3 or
earlier):
```
ea_diagram(operation=”add_connectors_to_diagram_bulk”, params={“diagram_id”: <id>})
```

---

## 7. Connectors

### Type â†’ EA connector type mapping

| Relationship | `connector_type` | `stereotype` |
|-------------|-----------------|--------------|
| `Â«UsesÂ»` | `Association` | `Uses` |
| `Â«RealizesÂ»` | `Realization` | `Realizes` |
| `Â«FlowsÂ»` | `InformationFlow` | `Flows` |
| `Â«DependencyÂ»` | `Dependency` | *(blank)* |
| Plain association | `Association` | *(blank)* |

### Governance rule: LFY-001 and connector stereotypes

The LFY-001 governance rule flags connectors where:
- The **source** element has `lifecycle` = `Strategic` or `Current`
- The **target** element has `lifecycle` = `Deprecated`
- The **connector stereotype** is one of: `Uses`, `ConsumesService`, `Realizes`, `Flows`

This means a plain `Association` with **no stereotype** does NOT trigger LFY-001, even if
it connects a Strategic source to a Deprecated target.

**Design rule:** If a connection to a Deprecated element is intentional and should NOT be
flagged as a governance violation (e.g. it documents an existing link for traceability, not
a new active consumption), use a plain unsterotyped `Association` rather than `Â«UsesÂ»`.

### Verify connector endpoints before creation

Always confirm both endpoint elements exist before calling `ea_model("create_connector")`:
```
ea_analyze(operation="execute_sql", params={"sql": """
    SELECT Object_ID, Name, Stereotype, Lifecycle
    FROM t_object
    WHERE Object_ID IN (<source_id>, <target_id>)
"""})
```

---

## 8. Element Placement and Package Tree Counts

### The recursive count problem

Tests (and EA's own metrics) count elements **recursively** through a package tree.  The
total for a capability area includes all elements in all sub-packages at every depth.

**Critical placement rule:**  Services and shared infrastructure elements that have a
conceptual "home" in one capability area but serve multiple areas should be placed in a
**top-level capability package** or in a shared infrastructure package â€” NOT inside a
sub-package of the capability area that happens to own them.

Placing a service inside a sub-package adds it to the recursive count of every ancestor
package, which can push parent-level counts above their expected bounds.

**How to check before placing an element:**

1. Find the target package's current recursive count:
```sql
-- Step 1: collect all package IDs in the subtree
-- (recursive CTE not available in EA's SQLite â€” use repeated queries or execute_sql loop)
SELECT COUNT(*) FROM t_object WHERE Package_ID IN (<pkg_id>, <child1>, <child2>, ...)
```

2. Compare against the test's expected range.  If the element would push the count above
the upper bound, find an alternative package.

---

## 9. Verification Queries

Use `execute_sql` throughout the build â€” it's the most reliable tool for confirming state.

### Count elements in a package subtree

```sql
SELECT COUNT(*) AS cnt
FROM t_object
WHERE Package_ID IN (
    SELECT Package_ID FROM t_package
    WHERE Package_ID = <root_pkg_id>
       OR Parent_ID  = <root_pkg_id>
       OR Parent_ID IN (
           SELECT Package_ID FROM t_package WHERE Parent_ID = <root_pkg_id>
       )
)
```

(Extend the IN nesting for deeper trees, or collect IDs iteratively.)

### Find all elements with a specific stereotype

```sql
SELECT o.Object_ID, o.Name, o.Stereotype, o.Package_ID
FROM t_object o
WHERE o.Stereotype = 'WBAVendorSystem'
ORDER BY o.Name
```

**Note:** MDG-defined stereotypes are stored in `t_object.Stereotype` â€” they are NOT in
`t_stereotype`. The `t_stereotype` table is empty for MDG-only models. Always query
`t_object` when looking for MDG stereotype usage.

### Check tagged values for a set of elements

```sql
SELECT o.Name, p.Property, p.Value
FROM t_object o
JOIN t_objectproperties p ON p.Object_ID = o.Object_ID
WHERE o.Package_ID IN (<pkg1>, <pkg2>)
  AND p.Property IN ('lifecycle', 'criticality', 'regulatoryScope')
ORDER BY o.Name, p.Property
```

### Find connectors involving a specific element

```sql
SELECT c.Connector_ID, c.Connector_Type, c.Stereotype,
       src.Name AS Source, tgt.Name AS Target
FROM t_connector c
JOIN t_object src ON src.Object_ID = c.Start_Object_ID
JOIN t_object tgt ON tgt.Object_ID = c.End_Object_ID
WHERE c.Start_Object_ID = <element_id>
   OR c.End_Object_ID   = <element_id>
```

### Check LFY-001 violations (pre-demo state: expect exactly 1)

```sql
SELECT src.Name AS source_name, tgt.Name AS target_name,
       c.Stereotype, src_lc.Value AS src_lifecycle, tgt_lc.Value AS tgt_lifecycle
FROM t_connector c
JOIN t_object src ON src.Object_ID = c.Start_Object_ID
JOIN t_object tgt ON tgt.Object_ID = c.End_Object_ID
JOIN t_objectproperties src_lc ON src_lc.Object_ID = src.Object_ID
                                AND src_lc.Property = 'lifecycle'
JOIN t_objectproperties tgt_lc ON tgt_lc.Object_ID = tgt.Object_ID
                                AND tgt_lc.Property = 'lifecycle'
WHERE c.Stereotype IN ('Uses', 'ConsumesService', 'Realizes', 'Flows')
  AND src_lc.Value IN ('Strategic', 'Current')
  AND tgt_lc.Value = 'Deprecated'
```

### Query element attributes (note: column is `Default`, not `Default_Value`)

```sql
SELECT a.Name, a.[Default], a.Type
FROM t_attribute a
WHERE a.Object_ID = <element_id>;
```

`[Default]` requires bracket quoting â€” `DEFAULT` is a reserved word in SQLite.

---

## 10. Working with the WBA MDG

### Confirm MDG is active before tagging

Before setting any WBA tagged values, confirm the MDG is loaded:
```
ea_analyze(operation="execute_sql", params={"sql": """
    SELECT * FROM t_document
    WHERE DocType = 'MDGXml' AND DocName = 'WestbrookBankArchitecture'
"""})
```

If the result is empty, the MDG has not been imported into the model.  Import it with the
`ea-mdg-deploy` skill before proceeding.

### Tagged value namespace confirmation

The first successful `ea_model(operation="set_tagged_value", ...)` response will include the fully-qualified tag name,
e.g. `WestbrookBankArchitecture::WBAVendorSystem::criticality`.  This confirms the MDG is
active and the tag schema is being honoured.

### MDG stereotype â†’ allowed tags

Not every stereotype supports every tag.  The WBA MDG schema restricts tags by stereotype:

| Tag | BA | VS | BS | AIS | AISG | DA |
|-----|----|----|----|----|------|-----|
| criticality | âœ“ | âœ“ | âœ“ | âœ“ | âœ“ | âœ“ |
| lifecycle | âœ“ | âœ“ | âœ“ | âœ“ | âœ“ | âœ“ |
| businessOwner | âœ“ | âœ“ | âœ“ | âœ“ | âœ“ | âœ“ |
| technicalOwner | âœ“ | âœ“ | âœ“ | âœ“ | âœ“ | âœ“ |
| dataClassification | âœ“ | âœ“ | âœ“ | âœ“ | âœ“ | âœ“ |
| regulatoryScope | âœ“ | âœ“ | âœ“ | âœ“ | âœ“ | âœ“ |
| vendor | â€” | âœ“ | â€” | â€” | â€” | â€” |
| product | â€” | âœ“ | â€” | â€” | â€” | â€” |
| pciScopeJustification | âœ“ | âœ“ | âœ“ | âœ“ | âœ“ | âœ“ |
| pciControlOwner | âœ“ | âœ“ | âœ“ | âœ“ | âœ“ | âœ“ |
| modelGovernanceClass | âœ“ | âœ“ | âœ“ | âœ“ | âœ“ | âœ“ |
| humanInLoop | â€” | â€” | â€” | âœ“ | âœ“ | â€” |
| auditLogging | â€” | â€” | â€” | âœ“ | âœ“ | â€” |

*(BA=WBABusinessApplication, VS=WBAVendorSystem, BS=WBABusinessService, AIS=WBAAIService, AISG=WBAAIGateway, DA=WBADataAsset)*

---

## 11. Idempotency â€” Check Before Creating

Never assume the repository is empty.  Always check for prior existence before creating:

```python
# Check package
ea_analyze(operation="execute_sql", params={"sql": "SELECT Package_ID FROM t_package WHERE Name = 'WestbrookBank' AND Parent_ID = 0"})

# Check element
ea_model(operation="find_elements_by_name", params={"name": "Customer Portal", "exact": True})
# or:
ea_analyze(operation="execute_sql", params={"sql": "SELECT Object_ID FROM t_object WHERE Name = 'Customer Portal' AND Package_ID = <pkg_id>"})

# Check connector
ea_analyze(operation="execute_sql", params={"sql": """
    SELECT Connector_ID FROM t_connector
    WHERE Start_Object_ID = <src> AND End_Object_ID = <tgt> AND Stereotype = 'Uses'
"""})
```

If the entity already exists, skip creation and record its existing ID.

---

## 12. Error Recovery Patterns

### Partial build recovery

If a build session is interrupted mid-way:
1. Call `ea_repository(operation="get_repository_info", params={})` and `ea_model(operation="list_root_packages", params={})` to confirm the EA connection.
2. Use SQL to audit what has been created vs. what the spec requires:
   ```sql
   SELECT COUNT(*) FROM t_object WHERE Stereotype LIKE 'WBA%'
   SELECT COUNT(*) FROM t_package WHERE ea_guid IS NOT NULL
   ```
3. Compare counts against the spec.  Identify the last completed element.
4. Resume from the next element in the build order â€” do not rebuild already-created content.

### Fixing a wrong name

Use `ea_model("update_package")` or `ea_model("update_element")` immediately:
```
ea_model(operation="update_package", params={"package_id": <id>, "name": "Correct Name"})
```
Then re-verify with SQL.

### Fixing a wrong parent (package in wrong location)

There is no `move_package` tool in v1.  Options:
1. `ea_analyze(operation=”execute_sql”, params={“sql”: “UPDATE t_package SET Parent_ID = <correct_parent> WHERE Package_ID = <id>”})` â€” direct SQL fix, verify afterward.
2. Delete and recreate the package (only viable if it has no children yet).

### Fixing a connector stereotype

To remove a stereotype from a connector:
```
ea_model(operation="update_connector", params={"connector_id": <id>, "stereotype": ""})
```
Then verify with SQL that `Stereotype` is blank in `t_connector`.

---

## 13. Pre-Demo vs. Post-Demo State

The Westbrook Bank spec defines two states:

**Pre-demo (what the repository is built to):**
- No AI Gateway element
- No AI Services elements
- Exactly 1 LFY-001 governance violation (ACH Return Handler â†’ Salesforce Legacy Data Export Feed)
- IMP-001 through IMP-011 imperfections present

**Post-demo (what the AI gateway demo creates live):**
- AI Gateway element added to AI Services package
- 3 AI Service elements added
- 2 new connectors from Customer Portal to AI Gateway services
- Some imperfections corrected live

Never create AI Gateway or AI Service elements during the initial build.  Use `ea_analyze("execute_sql")` to
confirm their absence before declaring the build complete:

```sql
SELECT COUNT(*) FROM t_object WHERE Stereotype IN ('WBAAIGateway', 'WBAAIService')
-- expected: 0
```

---

## 14. Quick-Reference: Most-Used Tools

| Task | Tool | Notes |
|------|------|-------|
| Orient in repo | `ea_model("list_root_packages")` | Always first |
| Get repo info | `ea_repository("get_repository_info")` | Confirms EA connection; check before any writes |
| Create package | `ea_model("create_package")` | Verify `&` names (may encode as `&amp;`) |
| Create one element | `ea_model("create_element")` | Pass `properties=`, `tagged_values=` inline |
| Create MDG element | `ea_model("create_element_in_language")` | Writes t_xref profile application; prefer over `create_element` for MDG types |
| Create many elements | `ea_model("create_elements_bulk")` | Idempotent; use for >5; supports `language_id`+`language_type` per spec |
| Set one tag | `ea_model("set_tagged_value")` | Use only for after-the-fact updates |
| Create connector | `ea_model("create_connector")` | Verify endpoints exist first |
| Create many connectors | `ea_model("create_connectors_bulk")` | Idempotent |
| Create diagram | `ea_diagram("create_diagram")` | Then `ea_diagram("update_diagram")` StyleEx |
| Create MDG diagram | `ea_diagram("create_diagram_in_language")` | Sets base type + StyleEx in one call |
| Add one element to diagram | `ea_diagram("add_element_to_diagram")` | Use for one-offs |
| Add many to diagram | `ea_diagram("add_elements_to_diagram_bulk")` | Idempotent; use for â‰¥3 |
| Bulk verify | `ea_analyze("execute_sql")` | Most reliable tool; use liberally |
| Describe table schema | `ea_analyze("describe_table")` | Use before writing non-trivial SQL |
| Fix names | `ea_model("update_package")` / `ea_model("update_element")` | Works even in v1 |
| Fix parent | `ea_analyze("execute_sql")` UPDATE | Only way in v1 for packages |
| Layout diagram | `ea_diagram("layout_diagram")` | Called automatically by `ea_diagram("add_elements_to_diagram_bulk")` |
| Repair connector lines | `ea_diagram("add_connectors_to_diagram_bulk")` | Run when connector lines are missing from a diagram |
| Summarize model | `ea_analyze("summarize_stereotype_usage")` | Token-cheap repo overview |

**Default response shape:** mutating tools return a minimal `{ok, *_id, guid, name, applied_*}` envelope. Pass `verbose=True` only if you actually need the full serialization in the response â€” see Â§15.

---

## 15. Token economy patterns

The MCP path's per-call response payload dominates context cost. A few habits keep
agentic sessions productive on large repos:

- **Default to `verbose=False`.** Mutating tools (`ea_model(“create_element”)`, `ea_model(“update_element”)`,
  `ea_model(“create_connector”)`, `ea_model(“update_connector”)`, `ea_diagram(“create_diagram”)`, `ea_diagram(“update_diagram”)`) return
  a minimal shape unless you set `verbose=True`. The minimal shape carries the new
  entity's id/guid/name â€” enough for follow-up calls. Need full state? Call
  `ea_model(“get_element”)` / `ea_model(“get_connector”)` / `ea_diagram(“get_diagram”)` afterward.
- **Verify in batch via `ea_analyze(“execute_sql”)`** â€” one round trip, structured rows. Don't loop
  `ea_model(“get_element”)` per ID to confirm a build.
- **Prefer `summarize_*`** (`ea_analyze("summarize_stereotype_usage")`, `ea_analyze("summarize_connector_patterns")`,
  `ea_analyze("summarize_tagged_value_usage")`) over assembling summaries from many `list_*` calls.
- **Bulk path saves ~95% of round-trip overhead** for catalog work. The token win
  compounds with the response-shape minimization: a 10-element single-call sequence
  with full responses costs ~2Ã— more tokens than the same work via
  `ea_model("create_elements_bulk")` returning summary records.
- **Budget rule of thumb:** catalog load >50 elements â†’ use VBScript (Â§0.5);
  verification, gap analysis, refinement of any size â†’ MCP.

### What users can control right now to reduce token spend

These are choices the **user makes when prompting** â€” not server settings:

| User action | Token impact |
|---|---|
| Ask Claude to build elements in bulk, not one at a time | ~95% fewer round-trip tokens |
| Ask for a SQL verification query instead of “check each element” | ~NÃ— fewer tokens |
| Ask for a summary (`ea_analyze(“summarize_stereotype_usage”)`) instead of “list all elements” | ~10â€”100Ã— fewer tokens |
| Avoid asking "show me the full element details" after every create | Saves ~75% per mutating response |
| Ask Claude to plan the full build order before executing | Front-loads reasoning, reduces back-and-forth during execution |
| Split large sessions: seed in VBScript, analyse/refine in MCP | Largest single saving for >50-element catalogs |

**What NOT to ask for in a large session:**
- "List all elements in this package" on large packages (use SQL COUNT queries instead)
- "Show me the full details of each connector" (use `ea_analyze("trace_connectors")` or SQL JOINs)
- "Verify every element was created correctly" element-by-element (one SQL query verifies everything)

---

## EA Computer Use — Latency Guidelines

This skill creates and modifies diagrams; many operations require checking the EA diagram canvas is up to date.

When any step requires taking a screenshot, clicking in EA, or verifying EA UI state:

| Operation | Wait before screenshot |
|-----------|----------------------|
| Any menu click or button in EA UI | 2–5 seconds |
| Opening a `.qea` project file | 5–15 seconds |
| Importing or deploying an MDG | 3–8 seconds |
| Expanding a package in Project Browser | 1–3 seconds |
| Any COM call that may trigger a dialog | 3–5 seconds |

**Standard pattern:**
1. Perform the action (click, COM call, MCP tool call that triggers EA UI change)
2. Wait the appropriate interval above
3. Take a screenshot to verify the result
4. If EA shows **"(Not Responding)"**: this is normal during file/import operations — wait another 5 seconds and screenshot again before concluding anything failed
5. **Never retry an action** without first confirming the previous one failed

> **"(Not Responding)"** in the EA title bar means EA is processing, not crashed. Wait — do not double-click, re-issue the command, or open a second EA instance.

---

## 16. Diagnostics mode (server v0.3.0+)

Opt-in â€” off by default. Set `EA_MCP_DIAGNOSTICS=1` in the MCP server's environment
to enable. When on, any tool that:

- raises an exception, or
- returns a structured error (`{"error": ...}` or `{"ok": False}`), or
- exceeds `EA_MCP_DIAGNOSTICS_TIMEOUT` seconds (default 30)

â€¦produces a Markdown issue report under `%LOCALAPPDATA%\ea-mcp-server\diagnostics\`
(or the path set via `EA_MCP_DIAGNOSTICS_DIR`). The report includes the failing tool's
arguments (long strings truncated), stack trace if applicable, EA build info, and the
last 25 tool calls leading up to the failure â€” critical for diagnosing order-dependent
bugs.

When diagnostics is on and a report is written, the tool's error response also includes:

```python
{
    "error": "...",
    "diagnostic_report": "C:\\Users\\<you>\\AppData\\Local\\ea-mcp-server\\diagnostics\\issue_<...>.md",
    "support_email": "help@novocircle.com",
    "support_message": "Diagnostics is enabled. A report was written. Please email it to help@novocircle.com.",
}
```

If you (or an agent acting on your behalf) hit a server failure or hang:

1. Stop work. Set `EA_MCP_DIAGNOSTICS=1`. Restart the MCP server.
2. Reproduce the failing call.
3. Open the report under `%LOCALAPPDATA%\ea-mcp-server\diagnostics\`.
4. Review the contents for anything you don't want to share, then email it to
   `help@novocircle.com`.

`ea_repository(operation=”get_repository_info”, params={})` returns the resolved diagnostics block (`enabled`,
`report_dir`, `support_email`) â€” call it to confirm the mode is active without
restarting.

---

## 17. Model selection and session hygiene (avoiding usage limits)

Claude Desktop usage limits are consumed by **context tokens** (what you send + what
Claude replies). EA modeling sessions can exhaust limits quickly if the session is
structured poorly. This section is about **user-controlled choices** that keep sessions
within budget.

### Model tier selection

Not every task needs the most capable model. Using the right tier cuts cost and
often runs faster.

| Task type | Recommended model | Why |
|---|---|---|
| Pure bulk authoring from a defined spec | **Haiku** (or VBScript) | Deterministic execution â€” no reasoning needed |
| Routine CRUD: create packages, elements, connectors | **Haiku** | Pattern-following, not reasoning |
| Verification queries, gap analysis, spot-checks | **Sonnet** | Needs to interpret SQL results + model context |
| Architectural analysis, pattern detection, governance review | **Sonnet** | Reasoning-heavy but not open-ended |
| MDG design, novel architectural frameworks, complex trade-off reasoning | **Opus** | Reserve for genuinely complex design decisions |

**Rule of thumb:** If you could write the VBScript yourself but prefer MCP for
convenience, use Haiku. If you're asking "what's wrong with this model?" or
"how should these elements connect?", use Sonnet. Only use Opus when the question
genuinely requires sustained complex reasoning.

### Session structure to avoid hitting limits

Large EA repositories + Claude Desktop = context exhaustion risk. Structure sessions
to stay productive:

**1. Split by phase, not by element**

Don't try to build an entire repository in one session. Break the work by build
phase (see Â§1):
- Session A: packages + pre-flight
- Session B: element bulk creation (or VBScript)
- Session C: connectors
- Session D: diagrams
- Session E: verification + governance checks

Each session starts fresh with minimal context and can focus cleanly.

**2. Seed context efficiently at session start**

Don't ask Claude to "figure out the state of the repository" â€” that burns context.
Instead, open each session with targeted SQL:
```
ea_analyze(operation="execute_sql", params={"sql": "SELECT COUNT(*) FROM t_object WHERE Stereotype LIKE 'WBA%'"})
ea_analyze(operation="execute_sql", params={"sql": "SELECT Package_ID, Name FROM t_package WHERE Parent_ID = <root>"})
```
Two round trips, minimal tokens, Claude knows exactly where it is.

**3. Avoid open-ended listing in mid-session**

"List all elements in the system" mid-session floods the context with data you
already have (or don't need). Use targeted SQL or `ea_model("find_elements_by_name")` with a
specific name instead.

**4. Ask for a plan first, then execute**

For complex builds: ask Claude to produce a build plan (package list, element
inventory, connector map) as a structured output *before* issuing any tool calls.
Review and correct the plan. Then execute it. This avoids multiple discovery
loops that each cost context.

**5. Keep confirmation brief**

After a bulk creation, ask "how many were created?" not "show me all the created
elements." The bulk tool's summary response (`{created, skipped, failed}`) is
exactly what you need â€” a single line, not a table.

**6. Use `/clear` between phases**

Claude Desktop's `/clear` command resets the context window. Use it between
major phases (e.g. after finishing element creation and before starting
connectors) so the connector phase starts with a clean window.

### When you see "approaching usage limit"

This means the context window is filling. Steps in priority order:

1. **Finish the current atomic operation** (don't abandon mid-bulk-create).
2. **Run one SQL verification** to capture the current state: element counts, last
   package ID created, etc. Save this somewhere (a note, a comment).
3. **Use `/clear`** to reset the window.
4. **Start the next session** by pasting the saved state summary as context â€”
   3â€“5 lines is enough for Claude to orient.

**Do NOT** ask for a "summary of everything done so far" just before hitting
the limit â€” that's the most expensive possible operation at the worst possible
time. The SQL state capture (step 2) is both cheaper and more reliable.

### Context cost per operation (approximate)

| Operation | Approx. context tokens (input + output) |
|---|---|
| `ea_model(“create_elements_bulk”)` (10 specs) | ~800â€”1,200 |
| `ea_model(“create_element”)` Ã— 10 (single calls) | ~3,000â€”5,000 |
| `ea_model(“list_elements_in_package”)` (50 elements, default) | ~400â€”800 |
| `ea_model(“list_elements_in_package”)` (50 elements, `verbose=True`) | ~8,000â€”15,000 |
| `ea_analyze(“execute_sql”)` verification query (10 rows) | ~300â€”600 |
| `ea_analyze(“summarize_stereotype_usage”)` (whole repo) | ~500â€”1,000 |
| `ea_model(“get_element”)` (single) | ~800â€”1,500 |

Default list operations return minimal shape `{element_id, guid, name}` â€” use `get_element` for full
detail on individual elements, or pass `verbose=True` to the list call only when you need all fields
at once. For existence/count verification, `ea_analyze(“execute_sql”)` is still the cheapest option.
