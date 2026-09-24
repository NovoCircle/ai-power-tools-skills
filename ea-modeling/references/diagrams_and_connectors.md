# Diagrams and Connectors — Full Detail

Detail supporting [`../SKILL.md`](../SKILL.md) §5–§7. Read those sections first for the decision
points (`create_diagram_in_language` vs. the two-step fallback, when connector lines go missing);
this file carries the full mapping tables and code patterns.

---

## 1. Creating diagrams with MDG types

### Preferred approach — `create_diagram_in_language`

Use `create_diagram_in_language` when the target diagram type is defined by an MDG
profile. It routes through EA's COM diagram-factory path and sets both the EA base type
and the MDG `StyleEx` in one call, without needing the two-step workaround:

```python
ea_diagram(operation="create_diagram_in_language", params={
    "name": "Application Landscape",
    "package_id": <id>,
    "language_id": "ArchiMate3",              # MDG Technology ID
    "diagram_type": "Application",            # diagram type within that MDG
})
```

Common language_id / diagram_type pairs:

| Diagram | language_id | diagram_type |
|---|---|---|
| ArchiMate Application | `ArchiMate3` | `Application` |
| ArchiMate Technology | `ArchiMate3` | `Technology` |
| BPMN Business Process | `BPMN2.0` | `Business Process` |
| UML Component | `UML` | `Component` |

### Fallback — two-step workaround for `create_diagram`

If `create_diagram_in_language` is unavailable or you need fine-grained control:

```python
# Step 1: create with the base EA type (not the MDG string)
result = ea_diagram(operation="create_diagram", params={
    "name": "Application Landscape",
    "package_id": <id>,
    "type": "Logical",          # use EA base type, not "ArchiMate3::Application"
})
diagram_id = result["diagram_id"]

# Step 2: set the MDG StyleEx immediately
ea_diagram(operation="update_diagram", params={
    "diagram_id": diagram_id,
    "properties": {"StyleEx": "MDGDgm=ArchiMate3::Application;"},
})
```

### MDG type → EA base type → StyleEx mapping

| Intended diagram type | EA base type (`ea_diagram("create_diagram")` `type`) | StyleEx value |
|----------------------|--------------------------------------|---------------|
| ArchiMate Application | `Logical` | `MDGDgm=ArchiMate3::Application;` |
| ArchiMate Technology | `Logical` | `MDGDgm=ArchiMate3::Technology;` |
| BPMN Business Process | `Analysis` | `MDGDgm=BPMN2.0::Business Process;` |
| UML Component | `Component` | `MDGDgm=UML::Component;` |
| UML Class | `Class` | *(no StyleEx needed — native EA type)* |
| UML Sequence | `Sequence` | *(no StyleEx needed)* |

### Verify diagram type was stored

```
ea_analyze(operation="execute_sql", params={"sql": "SELECT Diagram_Type, StyleEx FROM t_diagram WHERE Diagram_ID = <id>"})
```

For a BPMN diagram, `Diagram_Type` should contain `"Business Process"` or `"BPMN"`, and
`StyleEx` should contain `"MDGDgm=BPMN2.0::Business Process"`.

---

## 2. Diagram layout

### `layout_diagram` — works as of server v1.0.0

The earlier GUID bug (REQ-004) is **fixed in v1.0.0**. Call `layout_diagram` freely.

`ea_diagram("add_elements_to_diagram_bulk")` auto-applies `"Hierarchical"` layout after placement by
default (`layout="Hierarchical"`). You can pass `layout=None` to skip it, or pass any
supported style name (`"Circular"`, `"Digraph"`, etc.) to override.

To manually trigger layout on a diagram at any time:
```
ea_diagram(operation="layout_diagram", params={"diagram_id": <id>, "style": "Hierarchical"})
```

---

## 3. Connector visibility on diagrams — t_diagramlinks

**This is the most important diagram trap.** Placing elements on a diagram via
`add_elements_to_diagram_bulk` does NOT automatically render the connectors between
those elements. EA stores two completely independent things:

| Store | What it is | Tools that write it |
|---|---|---|
| `t_connector` | The logical connector (exists in the model) | `ea_model("create_connector")`, `ea_model("create_connectors_bulk")` |
| `t_diagramlinks` | The diagram-visible rendering of that connector | `ea_diagram("add_connectors_to_diagram_bulk")` (auto-called by `ea_diagram("add_elements_to_diagram_bulk")`) |

If `t_diagramlinks` rows are missing, connectors are invisible on the diagram even though
`ea_model("get_connector")` and `ea_analyze("execute_sql")` against `t_connector` show them present.

**`ea_diagram("add_elements_to_diagram_bulk")` auto-repairs this** (since v1.0.4):
- After placing elements it calls `ea_diagram("add_connectors_to_diagram_bulk")` with `connector_ids=None`
  which auto-discovers every connector whose both endpoints are already on the diagram and
  are not yet in `t_diagramlinks`.
- This is controlled by the `auto_show_connectors=True` default.

If you manually add elements via `ea_diagram("add_element_to_diagram")` (single-element variant), you
must call `ea_diagram(operation="add_connectors_to_diagram_bulk", params={"diagram_id": <id>})` afterwards yourself — or use
the bulk variant which handles it automatically.

**To repair a diagram with missing connector lines** (e.g. diagrams built with v1.0.3 or
earlier):
```
ea_diagram(operation="add_connectors_to_diagram_bulk", params={"diagram_id": <id>})
```

---

## 4. Connectors

### Type → EA connector type mapping

| Relationship | `connector_type` | `stereotype` |
|-------------|-----------------|--------------|
| `«Uses»` | `Association` | `Uses` |
| `«Realizes»` | `Realization` | `Realizes` |
| `«Flows»` | `InformationFlow` | `Flows` |
| `«Dependency»` | `Dependency` | *(blank)* |
| Plain association | `Association` | *(blank)* |

> **Canon note (flagged, not changed in this split):** `_shared/references/westbrook-example.md`
> section 6 states the WBA MDG defines *no* connector stereotypes, and that any connector
> stereotype example should use plain unstereotyped UML types. That rule is about inventing
> vocabulary, and it does not apply here: `Uses`, `ConsumesService`, `Realizes` and `Flows` are
> stereotypes the Westbrook demo model actually applies to connectors, and the demo's own tests
> query them. EA allows a stereotype string on a connector that no MDG declares, which is exactly
> what the model does. Write them unqualified, as below — never as `WBA::Uses`, because they are
> not MDG-declared. See canon section 6(b).

### Governance rule: WBA-LFY-001 and connector stereotypes

The WBA-LFY-001 governance rule flags connectors where:
- The **source** element has `lifecycle` = `Strategic` or `Current`
- The **target** element has `lifecycle` = `Deprecated`
- The **connector stereotype** is one of: `Uses`, `ConsumesService`, `Realizes`, `Flows`

This means a plain `Association` with **no stereotype** does NOT trigger WBA-LFY-001, even if
it connects a Strategic source to a Deprecated target.

**Design rule:** If a connection to a Deprecated element is intentional and should NOT be
flagged as a governance violation (e.g. it documents an existing link for traceability, not
a new active consumption), use a plain unstereotyped `Association` rather than `«Uses»`.

### Verify connector endpoints before creation

Always confirm both endpoint elements exist before calling `ea_model("create_connector")`:
```
ea_analyze(operation="execute_sql", params={"sql": """
    SELECT Object_ID, Name, Stereotype, Lifecycle
    FROM t_object
    WHERE Object_ID IN (<source_id>, <target_id>)
"""})
```
