# Custom diagram types, toolbox pages, and colours

Back to [SKILL.md](../SKILL.md).

## Section 2 — Custom Diagram Type

```xml
<Stereotype name="WBAApplicationView"
            alias="WBA Application Architecture"
            notes="Application portfolio architecture diagram."
            cx="90" cy="70"
            bgcolor="-1" fontcolor="-1" bordercolor="-1" borderWidth="-1">
  <AppliesTo>
    <Apply type="Diagram_Logical">
      <Property name="alias"     value="WBA Application Architecture"/>
      <Property name="diagramID" value="WBA-AppView"/>
      <Property name="toolbox"   value="WBA::WBA ArchiMate Elements"/>
    </Apply>
  </AppliesTo>
</Stereotype>
```

This is the real `WBAApplicationView` diagram stereotype. Its `toolbox` value must be the *exact*
toolbox page name declared in Section 3 below (`WBA ArchiMate Elements`) — not the technology's
namespace-style label. The shipped Westbrook demo MDG gets this wrong (it points at
`WBA::WBA ArchiMate`, which no toolbox page is named), so its custom diagrams fail to bind to
their toolbox. Treat that as a pitfall to avoid, not a pattern to copy.

**Rules:**
- `Apply type="Diagram_Logical"` — the correct value for EA 17 custom diagrams (NOT `"Logical"`)
- `Property name="toolbox"` — links to a toolbox page; format `<YourTechID>::PageName` where `PageName` matches the `<Stereotype name="...">` in UIToolboxes exactly
- `Property name="alias"` — the display name shown in the New Diagram dialog
- EA 17.0 shows the stereotype `name` (e.g., "WBAApplicationView") in the Model Builder/New Diagram dialog, NOT the `alias` attribute

---

## Section 3 — Toolbox Pages

```xml
<!-- Each toolbox page is one Stereotype with Apply type="ToolboxPage" -->
<!-- This is the real "WBA ArchiMate Elements" page — one of the WBA technology's three -->
<Stereotype name="WBA ArchiMate Elements" notes="">
  <AppliesTo>
    <Apply type="ToolboxPage"/>
  </AppliesTo>
  <TaggedValues>
    <!-- Each Tag is one item in the toolbox palette -->
    <!-- Tag name format: <YourTechID>::StereotypeName -->
    <!-- Tag default: the display label shown in the palette -->
    <Tag name="WBA::WBABusinessApplication" type="" description="" unit="" values="" default="Business Application"/>
    <Tag name="WBA::WBABusinessService"     type="" description="" unit="" values="" default="Business Service"/>
    <Tag name="WBA::WBAVendorSystem"        type="" description="" unit="" values="" default="Vendor System"/>
  </TaggedValues>
</Stereotype>

<!-- PROPOSED EXTENSION — not part of the shipped WBA technology (see Section 1 -
     Connector Stereotype above: WBA ships no connector stereotypes today). Shown only
     to teach how a connector toolbox page is wired up. -->
<Stereotype name="WBA Connectors (proposed)" notes="">
  <AppliesTo>
    <Apply type="ToolboxPage"/>
  </AppliesTo>
  <TaggedValues>
    <Tag name="WBA::WBARunsOn" type="" description="" unit="" values="" default="Runs On"/>
  </TaggedValues>
</Stereotype>
```

**Rules:**
- The `Stereotype name=` (e.g., `"WBA ArchiMate Elements"`) is the toolbox page name — it must exactly match the `toolbox` Property value in the DiagramProfile
- The `Tag name=` prefix (`WBA::`) must match the UMLProfile Documentation `id`
- Multiple pages allowed — one `Stereotype` per page, all inside the same UIToolboxes `<Content>`. The real WBA technology ships three: `WBA ArchiMate Elements`, `WBA BPMN Elements`, `WBA UML Elements`.

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
| Technology root | `WBA` |
| UML Profile | `WBA` (same as root — required for namespace) |
| Diagram Profile | `WBA-Diag` |
| Toolbox | `WBA-TB` |
