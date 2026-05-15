---
name: ea-mcp-quicklinker
description: Add Quick Linker rules and Apply-level properties (_HideUmlLinks, _MeaningForwards) to an MDG so EA shows context-sensitive connector menus when users hover over an element. Use when authoring or extending an MDG that needs guided connector creation.
---

# Quick Linker Rules for Sparx EA MDG

Quick Linker (QL) is the hover menu EA shows on a diagram element with the curved arrows. The menu's choices come from QL rules embedded in your MDG XML.

The AI Power Tools `write_mdg_xml` tool emits these rules when you populate the right keys on the intermediate metamodel. Two pieces:

1. **`<Apply>` Properties** — `_HideUmlLinks` and `_MeaningForwards` on the source stereotype.
2. **`<stereotypedrelationships>`** — the per-target-stereotype allowlist of connector stereotypes that can be created.

## Intermediate metamodel keys

```python
{
  "name": "Employee",
  "base_metaclass": "Class",
  "hide_uml_links": True,             # → <Property name="_HideUmlLinks" value="True"/>
  "meaning_forwards": "Reports To",   # → <Property name="_MeaningForwards" value="..."/>
  "quicklinker_rules": [
    {"stereotype": "TVO::reports-to", "constraint": "TVO::Employee"},
    {"stereotype": "TVO::belongs-to", "constraint": "TVO::Department"},
    {"stereotype": "TVO::works-at",   "constraint": "TVO::Location"},
  ],
  ...
}
```

This emits:

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
    <stereotypedrelationship stereotype="TVO::works-at"   constraint="TVO::Location"/>
  </stereotypedrelationships>
</Stereotype>
```

## Authoring rules

- **`stereotype`** — the connector stereotype EA will create when the user picks this menu item. Must match a connector stereotype defined elsewhere in the same MDG.
- **`constraint`** — the *target element* stereotype the user is allowed to drop on. EA will only show the menu when hovering over a source stereotype that has this rule.
- **`_HideUmlLinks: True`** — suppresses EA's default UML connector entries. **Only use when you have at least one QL rule for this stereotype** — otherwise the menu is empty.
- **`_MeaningForwards`** — text shown on the QL menu item label.

## Verifying the rules show up in EA

1. Deploy the MDG (`ea-mdg-deploy` skill).
2. Restart EA so the technology cache reloads.
3. Open a diagram, drop a source stereotype element on the canvas.
4. Hover for 1–2 seconds — the QL arrows appear; clicking one shows your menu.
5. If the menu is empty, check:
   - Did `_HideUmlLinks=True` hide the defaults without leaving QL rules?
   - Does the rule's `constraint` match an existing target stereotype name with the right namespace prefix?

## EA Computer Use — Latency Guidelines

Quick Linker verification always requires the EA diagram canvas — the hover overlay is only visible in the live EA UI.

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

## See also

- `ea-mdg-author` — full MDG XML structure.
- `ea-mdg-deploy` — getting the rules into a running EA session.
- EA help: search for "Quick Linker" or "_HideUmlLinks".
