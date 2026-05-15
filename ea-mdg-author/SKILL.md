---
name: ea-mdg-author
description: Author a Sparx EA MDG Technology XML file — define stereotypes, tagged values, toolbox pages, and custom diagram types. Use when creating or modifying any MDG technology for Sparx EA.
---

# Authoring a Sparx EA MDG Technology

*Verified against EA 17.0 Build 1704. All XML patterns here load and deploy correctly.*

## Quick Reference

| Task | Key Rule |
|------|----------|
| All `id=` attributes | **≤ 12 characters** (EA hard limit — silently fails if exceeded) |
| File encoding | Must be `utf-8` |
| UMLProfile `id` | Must match the technology `id` for toolbox namespace resolution |
| `bgcolor` colour values | COLORREF integer: B×65536 + G×256 + R. `-1` = use EA theme default |
| Tagged value type | Use `enumeration` (not `enum`) and `String` (capital S) |
| Test after every structural change | Use `ea-mdg-deploy` skill |

---

## Tool Selection

When automating MDG work, pick the right tool tier:

| Operation | Use |
|-----------|-----|
| Author MDG XML, read/write files | Claude Code file tools (`Write`, `Read`, `Edit`) |
| Parse and validate MDG XML | `parse_mdg_xml` MCP tool |
| Install MDG at application scope | `install_mdg(scope="user")` MCP tool |
| Install MDG as model-embedded | `install_mdg(scope="embedded")` MCP tool — or COM `repo.ImportTechnology()` if MCP times out |
| Verify MDG is loaded | COM: `repo.IsTechnologyLoaded("TVO")` — **not** `get_embedded_mdgs` (unreliable in EA 17) |
| Fix `Object_Type` in database | `repo.Execute()` DML — **not** `elem.Type` COM setter (silently fails for ArchiMate types) |
| Dismiss EA dialogs | Computer use screenshot → click → screenshot again |

> **`get_embedded_mdgs` is unreliable in EA 17+ for model-embedded MDGs.** Use
> `repo.IsTechnologyLoaded("TVO")` or check Specialize → Technologies → Manage Technology
> in the EA UI instead.

---

## Canonical EA 17 File Structure

```xml
<?xml version="1.0" encoding="utf-8"?>
<MDG.Technology version="1.0" id="APM" name="APM Modeling Language">

  <Documentation id="APM" name="APM Modeling Language" version="1.0"
                 notes="Description shown in Manage Technologies dialog."
                 filename="" date="2026-01-01"/>

  <!-- SECTION 1: UML Profile — element/connector stereotypes + tagged values -->
  <UMLProfiles>
    <UMLProfile profiletype="uml2">
      <Documentation id="APM"
                     name="APMDomainProfile"
                     version="1.0"
                     alias="APM Profile"
                     notes="Stereotype definitions"/>
      <Content>
        <Stereotypes>
          <!-- stereotypes go here -->
        </Stereotypes>
        <TaggedValueTypes/>
      </Content>
    </UMLProfile>
  </UMLProfiles>

  <!-- SECTION 2: Diagram Profile — custom diagram types -->
  <DiagramProfile>
    <UMLProfile profiletype="uml2">
      <Documentation id="APM-Diag" name="APMDiagrams" version="1.0"
                     alias="APM Diagrams" notes="Custom diagram types"/>
      <Content>
        <Stereotypes>
          <!-- diagram stereotypes go here -->
        </Stereotypes>
        <TaggedValueTypes/>
      </Content>
    </UMLProfile>
  </DiagramProfile>

  <!-- SECTION 3: Toolboxes — palette pages shown in EA toolbox panel -->
  <UIToolboxes>
    <UMLProfile profiletype="uml2">
      <Documentation id="APM-TB" name="APM Elements" version="1.0"
                     notes="APM element palette"/>
      <Content>
        <Stereotypes>
          <!-- toolbox page stereotypes go here -->
        </Stereotypes>
        <TaggedValueTypes/>
      </Content>
    </UMLProfile>
  </UIToolboxes>

</MDG.Technology>
```

**Critical rules:**
- `<MDG.Technology id="APM">` and `<Documentation id="APM">` must match exactly — this is the tech ID used in COM API calls
- The UMLProfile `<Documentation id="APM">` must also match the technology id for toolbox `APM::StereotypeName` namespace resolution to work
- All three sections use the same `<UMLProfile profiletype="uml2">` wrapper

---

## Section 1 — Element Stereotype

```xml
<Stereotype name="Application"
            alias="Application"
            metatype="Application"
            notes="A business or IT application in the portfolio."
            isAbstract="false"
            bgcolor="15782580"
            fontcolor="-1"
            bordercolor="-1"
            borderWidth="-1"
            cx="130" cy="70">
  <AppliesTo>
    <Apply type="Class"/>
  </AppliesTo>
  <TaggedValues>
    <Tag name="owner" type="String"
         description="Business owner name or team"
         default="" unit="" values=""/>
    <Tag name="status" type="enumeration"
         description="Lifecycle phase"
         default="Active" unit=""
         values="Active,Retiring,Retired,Planned"/>
    <Tag name="criticality" type="enumeration"
         description="Business impact classification"
         default="Standard" unit=""
         values="Mission Critical,Business Critical,Standard"/>
    <Tag name="hostingModel" type="enumeration"
         description="Deployment model"
         default="On-Premise" unit=""
         values="On-Premise,SaaS,Hybrid"/>
  </TaggedValues>
</Stereotype>
```

**Attribute rules:**
- `name=` — the stereotype identifier used in `APM::Application` toolbox references
- `alias=` — display label shown in EA UI (can differ from name)
- `metatype=` — used in EA's element type display; set to same as `name` unless you have a reason to differ
- `bgcolor=` — COLORREF integer (see colour table below); `-1` = use EA theme default
- `cx` / `cy` — default element width/height in pixels on diagram canvas
- `Apply type=` options: `Class`, `Component`, `Node`, `Package`, `Interface`, `Dependency`, `Association`, `Realization`, etc.

**Tagged value `type=` options (verified EA 17):**

| type= value | EA display | Notes |
|-------------|------------|-------|
| `String` | Text field | Free text |
| `enumeration` | Dropdown | Comma-separated `values=` attribute |
| `Boolean` | Checkbox | `default="true"` or `"false"` |
| `Date` | Date picker | |
| `memo` | Multi-line | Long text |
| `RefGUID` | GUID picker | Link to another element |
| `url` | URL field | |
| `file` | File picker | |
| `Integer` | Numeric | |

> **Common mistake:** using `enum` or `Enumeration` — the correct value is `enumeration` (lowercase, full word).

### ⚠ Base Type and Project Browser Visibility

`<Apply type="..."/>` controls what `t_object.Object_Type` EA stores for elements of this
stereotype. The value must be a **standard UML type** that EA's Project Browser natively renders
— otherwise elements will be invisible in the browser tree even though they appear on diagram
canvases and are accessible via SQL.

**Safe base types (Project Browser renders them natively):**
`Class`, `Component`, `Node`, `Package`, `Interface`, `Actor`, `UseCase`, `Activity`,
`Artifact`, `Boundary`, `Collaboration`, `DataStore`, `Decision`

**Dangerous base types — only use if the corresponding MDG is active at project scope:**

| `Apply type=` | Requires |
|---|---|
| `BusinessActor`, `BusinessProcess`, etc. | ArchiMate3 MDG active at project scope |
| `ApplicationComponent`, `ApplicationService`, etc. | ArchiMate3 MDG active at project scope |
| Anything starting with a BPMN shape name | BPMN MDG active at project scope |

> **Rule:** If you are building a standalone custom MDG that does not require ArchiMate3 or
> another extended MDG, always use `<Apply type="Class">` (or another standard UML type) as the
> base. The ArchiMate conceptual alignment is conveyed through the stereotype name, tagged values,
> and documentation — not the base type. Using `BusinessActor` as the base type when ArchiMate3
> is not project-loaded causes elements to be invisible in the Project Browser.

**If elements are already stored with the wrong base type**, the COM setter (`elem.Type = "Class"`)
silently ignores the change for ArchiMate-typed elements. Use `repo.Execute()` DML directly:

```python
repo.Execute(
    "UPDATE t_object SET Object_Type='Class' "
    "WHERE Object_Type='BusinessActor' "
    "AND Stereotype IN ('Employee','Department')"
)
```
Then close and reopen the project to flush EA's in-memory cache.

---

## Section 1 — Connector Stereotype

```xml
<Stereotype name="RunsOn"
            alias="Runs On"
            notes="Application runs on Technology Platform."
            isAbstract="false"
            bgcolor="-1" fontcolor="-1" bordercolor="-1"
            borderWidth="-1" cx="90" cy="70">
  <AppliesTo>
    <Apply type="Dependency"/>
  </AppliesTo>
  <TaggedValues>
    <Tag name="integrationPattern" type="enumeration"
         description="Integration pattern"
         default="Synchronous" unit=""
         values="Synchronous,Asynchronous,Batch"/>
  </TaggedValues>
</Stereotype>
```

Connector `Apply type=` options: `Dependency`, `Association`, `Realization`, `Aggregation`, `Composition`, `InformationFlow`, `Sequence`

---

## Section 2 — Custom Diagram Type

```xml
<Stereotype name="APMPortfolioView"
            alias="APM Portfolio View"
            notes="Application portfolio architecture diagram."
            cx="90" cy="70"
            bgcolor="-1" fontcolor="-1" bordercolor="-1" borderWidth="-1">
  <AppliesTo>
    <Apply type="Diagram_Logical">
      <Property name="alias"     value="APM Portfolio View"/>
      <Property name="diagramID" value="APM-PortView"/>
      <Property name="toolbox"   value="APM::APM Elements"/>
    </Apply>
  </AppliesTo>
</Stereotype>
```

**Rules:**
- `Apply type="Diagram_Logical"` — the correct value for EA 17 custom diagrams (NOT `"Logical"`)
- `Property name="toolbox"` — links to a toolbox page; format `TechID::PageName` where `PageName` matches the `<Stereotype name="...">` in UIToolboxes exactly
- `Property name="alias"` — the display name shown in the New Diagram dialog
- EA 17.0 shows the stereotype `name` (e.g., "APMPortfolioView") in the Model Builder/New Diagram dialog, NOT the `alias` attribute

---

## Section 3 — Toolbox Pages

```xml
<!-- Each toolbox page is one Stereotype with Apply type="ToolboxPage" -->
<Stereotype name="APM Elements" notes="">
  <AppliesTo>
    <Apply type="ToolboxPage"/>
  </AppliesTo>
  <TaggedValues>
    <!-- Each Tag is one item in the toolbox palette -->
    <!-- Tag name format: TechID::StereotypeName -->
    <!-- Tag default: the display label shown in the palette -->
    <Tag name="APM::Application"   type="" description="" unit="" values="" default="Application"/>
    <Tag name="APM::TechPlatform"  type="" description="" unit="" values="" default="Tech Platform"/>
    <Tag name="APM::BizCapability" type="" description="" unit="" values="" default="Biz Capability"/>
    <Tag name="APM::DataDomain"    type="" description="" unit="" values="" default="Data Domain"/>
  </TaggedValues>
</Stereotype>

<Stereotype name="APM Connectors" notes="">
  <AppliesTo>
    <Apply type="ToolboxPage"/>
  </AppliesTo>
  <TaggedValues>
    <Tag name="APM::RunsOn"      type="" description="" unit="" values="" default="Runs On"/>
    <Tag name="APM::Realises"    type="" description="" unit="" values="" default="Realises"/>
    <Tag name="APM::Integration" type="" description="" unit="" values="" default="Integration"/>
  </TaggedValues>
</Stereotype>
```

**Rules:**
- The `Stereotype name=` (e.g., `"APM Elements"`) is the toolbox page name — it must exactly match the `toolbox` Property value in the DiagramProfile
- The `Tag name=` prefix (`APM::`) must match the UMLProfile Documentation `id`
- Multiple pages allowed — one `Stereotype` per page, all inside the same UIToolboxes `<Content>`

---

## COLORREF Colour Reference

Formula: `B × 65536 + G × 256 + R`

| Colour | R | G | B | COLORREF |
|--------|---|---|---|----------|
| Light blue | 180 | 210 | 240 | **15782580** |
| Light grey | 221 | 221 | 221 | **14540253** |
| Light green | 204 | 255 | 204 | **13434828** |
| Light amber | 255 | 220 | 100 | **6610175** |

Verify any value: `R = val & 0xFF`, `G = (val >> 8) & 0xFF`, `B = (val >> 16) & 0xFF`

> **Common mistake:** the formula is BGR order (not RGB). `12632319 = 0x00C0C0FF = RGB(255,192,192)` = pink, not blue.

---

## ID Mapping Pattern

When IDs exceed 12 characters, map them systematically:

| Logical Name | MDG `id=` |
|---|---|
| Technology root | `APM` |
| UML Profile | `APM` (same as root — required for namespace) |
| Diagram Profile | `APM-Diag` |
| Toolbox | `APM-TB` |

---

## Namespace Consistency Checklist

Before deploying, verify:

- [ ] `<MDG.Technology id="APM">`
- [ ] `<Documentation id="APM">` (top-level)
- [ ] UMLProfile `<Documentation id="APM">` — **must match technology id**
- [ ] All toolbox `Tag name=` values: `APM::Application` etc.
- [ ] DiagramProfile `Property name="toolbox" value="APM::APM Elements"`
- [ ] COM calls: `Repository.IsTechnologyLoaded("APM")`

---

## Post-Install: Applying the MDG to Existing Repository Data

After deploying an MDG, EA does not automatically update existing elements. Ask the user whether
they want to migrate existing elements to use the new MDG's stereotypes and tagged values.

### Step 1 — Ask

> "The MDG is installed. Would you like to apply it to existing elements in the repository?
> I can find all elements that match the base type(s) of your stereotypes and offer to update
> their stereotype and initialise their tagged values."

If yes, proceed with Steps 2–4. If no, stop.

### Step 2 — Identify candidate elements

Use `execute_sql` (read-only) to find elements whose `Object_Type` matches the base type(s)
of your stereotypes and that do not yet have the MDG stereotype set:

```python
# Example: find all Class elements that aren't already stereotyped as TVO types
candidates = execute_sql("""
    SELECT o.Object_ID, o.Name, o.Object_Type, o.Stereotype, o.Package_ID
    FROM t_object o
    WHERE o.Object_Type = 'Class'
      AND (o.Stereotype IS NULL OR o.Stereotype NOT IN ('Employee','Department','WorkLocation'))
    ORDER BY o.Name
""")
```

Present the list to the user and confirm which elements to update before proceeding.

### Step 3 — Update elements

For each confirmed element, use `update_element` to set the stereotype and initial tagged values:

```python
update_element(
    element_id=obj_id,
    properties={"stereotype": "Employee"},
    tagged_values={
        "empID": "",
        "department": "",
        "hireDate": "",
    }
)
```

> **Do not use `repo.Execute()` DML to set stereotypes** — EA's internal cache won't update.
> Always use the `update_element` MCP tool for stereotype changes, so EA's runtime state
> stays consistent.

### Step 4 — Validate

Run the companion YAML sidecar immediately after the migration to find any elements that need
attention:

```python
validate_model(rules_path_or_content="TVO_rules.yaml")
```

Review violations and ask the user to fill in required tagged values before saving.

---

## Quick Linker Rules

Quick Linker (QL) is the hover menu EA shows on a diagram element when you pause over it. QL rules
are embedded in your MDG XML and control which connector types appear in that menu.

### Preferred approach — intermediate metamodel (write_mdg_xml)

When using `write_mdg_xml` to emit your MDG XML, declare QL rules directly on each source
stereotype in the intermediate metamodel dict:

```python
{
  "name": "Employee",
  "base_metaclass": "Class",
  "hide_uml_links": True,           # suppress EA's default UML entries
  "meaning_forwards": "Reports To", # label on the QL menu item
  "quicklinker_rules": [
    # Each entry: which connector to create → which target stereotype is allowed
    {"stereotype": "TVO::reports-to", "constraint": "TVO::Employee"},
    {"stereotype": "TVO::belongs-to", "constraint": "TVO::Department"},
    {"stereotype": "TVO::works-at",   "constraint": "TVO::WorkLocation"},
  ],
  # ... other fields
}
```

`write_mdg_xml` emits the correct `<stereotypedrelationships>` and `<Apply>` properties
automatically. The dict above produces:

```xml
<Stereotype name="Employee" ...>
  <AppliesTo>
    <Apply type="Class">
      <Property name="_HideUmlLinks" value="True"/>
      <Property name="_MeaningForwards" value="Reports To"/>
    </Apply>
  </AppliesTo>
  ...
  <stereotypedrelationships>
    <stereotypedrelationship stereotype="TVO::reports-to" constraint="TVO::Employee"/>
    <stereotypedrelationship stereotype="TVO::belongs-to" constraint="TVO::Department"/>
    <stereotypedrelationship stereotype="TVO::works-at"   constraint="TVO::WorkLocation"/>
  </stereotypedrelationships>
</Stereotype>
```

### Manual XML approach

If writing MDG XML directly, add these two elements to each source stereotype:

```xml
<Stereotype name="Employee" ...>
  <AppliesTo>
    <Apply type="Class">
      <Property name="_HideUmlLinks" value="True"/>
      <Property name="_MeaningForwards" value="Reports To"/>
    </Apply>
  </AppliesTo>
  <!-- ... TaggedValues ... -->
  <stereotypedrelationships>
    <stereotypedrelationship stereotype="TVO::reports-to" constraint="TVO::Employee"/>
    <stereotypedrelationship stereotype="TVO::belongs-to" constraint="TVO::Department"/>
    <stereotypedrelationship stereotype="TVO::works-at"   constraint="TVO::WorkLocation"/>
  </stereotypedrelationships>
</Stereotype>
```

### Rules

- `stereotype` — connector stereotype EA creates when user picks this menu item. Must be defined
  as a connector stereotype elsewhere in the same MDG XML.
- `constraint` — the target element stereotype the menu item is valid for. Format: `TechID::Name`.
- **`_HideUmlLinks: True`** — only set this when you have at least one QL rule. An empty hide
  produces an entirely empty QL menu and looks like a broken feature.
- **Legacy: Profile Diagram workflow.** Creating QL rules via a Profile Diagram in EA then
  generating via the MTS Wizard is the old approach. It still works but is not recommended when
  AI Power Tools is deployed — use the intermediate metamodel or hand-author the XML instead.

### Verifying QL in EA

1. Deploy MDG and restart EA.
2. Open a diagram, drop a source stereotype element.
3. Hover for 1–2 seconds — QL arrows appear; clicking shows your connector menu.
4. If the menu is empty: check `_HideUmlLinks` isn't set without QL rules, and that
   `constraint` uses the right namespace prefix (`TechID::StereotypeName`).

> **Computer use note:** the QL hover overlay disappears on focus change. Take a screenshot
> immediately after the menu appears — do not click elsewhere first.

---

## Validation Rules — Do NOT Use `<Scripts>` with AI Power Tools

When AI Power Tools for Sparx EA is deployed, **do not embed validation rules in the MDG's
`<Scripts>` section**. The `<Scripts>` mechanism runs JavaScript inside EA's scripting engine
and is not accessible to the MCP server.

```xml
<!-- WRONG — EA scripting, not accessible to validate_model tool -->
<Scripts>
  <Script name="TVO Conformance Rules" type="Normal" language="JavaScript">
    <![CDATA[
    function EA_GetRuleSetList() { return "TVO Conformance"; }
    function EA_OnRunRule(RuleSetID, RuleID, ObjectType, ObjectID) { ... }
    ]]>
  </Script>
</Scripts>
```

Instead, create a `<mdg_name>_rules.yaml` sidecar file and run it with the `validate_model`
MCP tool. See the `ea-mcp-validation` skill for the sidecar schema.

```yaml
# TechVentures_rules.yaml — run with validate_model(rules_path_or_content="...")
meta:
  version: "1.0"
  mdg_family: TVO
rules:
  - id: EMP-001
    severity: error
    selector:
      type: element
      stereotypes:
        any_of: ["Employee"]
    condition:
      type: tagged_value_required
      tags:
        - name: empID
          must_be_non_empty: true
```

### Creating the companion YAML sidecar

Every MDG produced by this skill must have a companion `<tech_id>_rules.yaml` file. Create it
as part of the MDG authoring workflow — one `tagged_value_required` rule for each tagged value
that is marked as mandatory in your MDG design.

Minimal template for a new MDG:

```yaml
meta:
  version: "1.0"
  mdg_family: TVO         # replace with your tech ID

rules:
  # One block per mandatory tagged value per stereotype.
  # Rule IDs: <TechID>-TVR-001, -002, ... for tagged-value rules
  #           <TechID>-CNX-001, -002, ... for connector rules

  - id: TVO-TVR-001
    severity: error
    demo_trigger: true    # mark the most critical check for quick smoke-testing
    selector:
      type: element
      stereotypes:
        any_of: ["Employee"]
    condition:
      type: tagged_value_required
      tags:
        - name: empID
          must_be_non_empty: true
    remediation:
      short: Populate the empID tagged value on this Employee

  # Repeat for each additional mandatory tag / stereotype combination
```

Run validation after every MDG install to confirm it finds violations on test data:
```
validate_model(rules_path_or_content="TVO_rules.yaml", mode="demo_validation")
```

---

## EA Computer Use — Latency Guidelines

MDG authoring primarily uses file tools, but deployment verification and any diagram-based checks require the EA UI.

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

## Researching the Sparx EA API

- MDG Technology authoring → Sparx EA help, search "MDG Technology" or "UML Profile"
- Tagged value types → search "TaggedValueTypes"
- Diagram types → search "Diagram Stereotypes" or "Custom Diagram"
- When documentation is unclear, use `ea.repo_methods()` to enumerate available COM methods at runtime

---

## File Encoding (Critical)

MDG Technology XML files **must declare and use `utf-8` encoding**. The Claude Code `Write` tool
always saves files as UTF-8 — the XML declaration must match.

```xml
<?xml version="1.0" encoding="utf-8"?>
```

When writing MDG XML from Python:
```python
with open("APM_MDG.xml", "w", encoding="utf-8") as f:
    f.write(xml_content)
```

When reading MDG XML to pass to `ImportTechnology`:
```python
with open("APM_MDG.xml", encoding="utf-8") as f:
    xml = f.read()
```

> **Legacy note:** Older EA versions and hand-written MDG files sometimes used `windows-1252`. If
> you receive an MDG XML file that is windows-1252 encoded, re-save it as UTF-8 and update the
> declaration. Do not mix the declaration and the actual byte encoding — EA will reject the file
> if they disagree.
