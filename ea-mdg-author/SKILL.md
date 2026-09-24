---
name: ea-mdg-author
description: Author a Sparx EA MDG Technology XML file — define stereotypes, tagged values, toolbox pages, and custom diagram types. Use when creating or modifying any MDG technology for Sparx EA.
---

# Authoring a Sparx EA MDG Technology

*Verified against EA 17.0 Build 1704. All XML patterns here load and deploy correctly.*

## Before you start — does this MDG already have a source model?

This skill treats the `.xml` file as the source of truth. If the technology you're editing has a
source model in an EA repository (profile packages, a design metamodel, a build/export procedure
someone follows to produce the shipped XML), **stop and use `ea-mdg-model-build` instead.**

⚠ **Hand-editing an MDG that has a source model causes permanent, silent divergence.** The XML
edit works today — but the next time anyone runs the model-driven export/build procedure, it
overwrites the file from the profile packages and your edit is gone, with no warning and no
record that it ever existed. There's no reconciliation step; the export doesn't know your edit
happened. If you're not sure whether a technology has a source model, ask before editing its XML
directly.

## Quick Reference

| Task | Key Rule |
|------|----------|
| All `id=` attributes | **≤ 12 characters** (EA hard limit — silently fails if exceeded) |
| File encoding | Must be `utf-8` |
| UMLProfile `id` | Must match the technology `id` for toolbox namespace resolution |
| `bgcolor` color values | COLORREF integer: B×65536 + G×256 + R. `-1` = use EA theme default |
| Tagged value type | Use `enumeration` (not `enum`) and `String` (capital S) |
| Test after every structural change | Use `ea-mdg-deploy` skill |

---

## Tool Selection

When automating MDG work, pick the right tool tier:

| Operation | Use |
|-----------|-----|
| Author MDG XML, read/write files | Claude Code file tools (`Write`, `Read`, `Edit`) |
| Parse and validate MDG XML | `ea_mdg(operation="parse_mdg_xml", params={"path_or_content": "..."})` |
| Install MDG at application scope | `ea_mdg(operation="install_mdg", params={"scope": "user"})` |
| Install MDG as model-embedded | `ea_mdg(operation="install_mdg", params={"scope": "embedded"})` — or COM `repo.ImportTechnology()` if MCP times out |
| Verify MDG is loaded | COM: `repo.IsTechnologyLoaded("WBA")` — **not** `get_embedded_mdgs` (unreliable in EA 17) |
| Fix `Object_Type` in database | `repo.Execute()` DML — **not** `elem.Type` COM setter (silently fails for ArchiMate types) |
| Dismiss EA dialogs | Computer use screenshot → click → screenshot again |

> **`get_embedded_mdgs` is unreliable in EA 17+ for model-embedded MDGs.** Use
> `repo.IsTechnologyLoaded("WBA")` or check Specialize → Technologies → Manage Technology
> in the EA UI instead.

---

## Authoring workflow

An MDG Technology XML file has three parallel sections wrapped in one `<MDG.Technology>` root: a
UML Profile (element and connector stereotypes with their tagged values), a Diagram Profile
(custom diagram types), and one or more UIToolboxes (the palette pages EA shows for each diagram
type). All three share the same `<UMLProfile profiletype="uml2">` wrapper, and the technology's
`id=` must match everywhere it is referenced — that single mismatch is the most common reason a
toolbox fails to resolve.

The full skeleton, with the three sections annotated, is in
[references/xml-skeleton.md](references/xml-skeleton.md) (also covers file-encoding rules).

Build in this order:

1. **Element stereotypes** — one `<Stereotype>` per concept, applied to a UML base type.
2. **Connector stereotypes** — only if the technology needs its own relationship semantics.
3. **Custom diagram types** — bind each to a toolbox page by exact name.
4. **Toolbox pages** — the palette items EA shows for each diagram type.
5. **Quick Linker rules** (optional) — hover-menu connector creation, if you added connector stereotypes.
6. **Companion validation sidecar** — a `<tech_id>_rules.yaml`, never `<Scripts>` (MCP can't reach EA's script engine).
7. **Deploy and verify** — hand off to `ea-mdg-deploy`.

### Section 1 — Element Stereotype

Each element stereotype wraps a UML base type (`Class`, `Component`, `Activity`, ...) and carries
its tagged values. The real `WBABusinessApplication` stereotype — full XML, the attribute rules,
and the tagged-value `type=` table — is in
[references/stereotypes.md](references/stereotypes.md).

**Pitfall — wrong base type hides elements in the Project Browser.** `<Apply type="...">` sets
`t_object.Object_Type`. Using an ArchiMate or BPMN shape name (e.g. `BusinessActor`) as the base
type when that MDG isn't active at project scope makes elements invisible in the Project Browser
tree, even though they still appear on diagrams and in SQL. For a standalone custom MDG, always
base on a standard UML type (`Class`, `Component`, etc.) and carry the ArchiMate concept through
the stereotype name and tagged values instead. The full safe/dangerous base-type lists and the
`repo.Execute()` DML fix for elements already stored wrong are in
[references/stereotypes.md](references/stereotypes.md#base-type-and-project-browser-visibility).

### Section 1 — Connector Stereotype

**The shipped WBA technology defines no connector stereotypes.** For relationships between WBA
elements, use a plain UML connector type with no stereotype (`Dependency`, `Realization`,
`Association`, `Aggregation`). [references/stereotypes.md](references/stereotypes.md) shows how
you *would* add one — the example is a `WBARunsOn` connector labelled **PROPOSED EXTENSION — not
part of the shipped WBA technology**, kept only to teach the pattern.

### Section 2 — Custom Diagram Type

A diagram stereotype uses `Apply type="Diagram_Logical"` and points at a toolbox page by its
*exact* name via a `toolbox` property. The full XML and rules are in
[references/diagrams-toolboxes.md](references/diagrams-toolboxes.md).

**Pitfall — toolbox binding is a literal string match, not a namespace lookup.** The shipped
Westbrook demo MDG gets this wrong: its diagram profile points its `toolbox` property at
`WBA::WBA ArchiMate`, but no toolbox page is named that — the real page is `WBA ArchiMate
Elements`. Because the two strings don't match, the demo's custom diagrams never bind to their
toolbox. Treat that as a pitfall to avoid, not a pattern to copy — the `toolbox` value must equal
the toolbox page's `Stereotype name=` exactly.

### Section 3 — Toolbox Pages

One `<Stereotype>` per page, `Apply type="ToolboxPage"`, one `<Tag>` per palette item in the
format `<YourTechID>::StereotypeName`. The real WBA technology ships three pages: `WBA ArchiMate
Elements`, `WBA BPMN Elements`, `WBA UML Elements`. Full XML (including how a connector toolbox
page would be wired up) is in
[references/diagrams-toolboxes.md](references/diagrams-toolboxes.md).

The COLORREF color formula and the `id=` mapping pattern for names over 12 characters are also in
that reference file.

---

## Namespace Consistency Checklist

Before deploying, verify:

- [ ] `<MDG.Technology id="WBA">`
- [ ] `<Documentation id="WBA">` (top-level)
- [ ] UMLProfile `<Documentation id="WBA">` — **must match technology id**
- [ ] All toolbox `Tag name=` values: `WBA::WBABusinessApplication` etc.
- [ ] DiagramProfile `Property name="toolbox" value="WBA::WBA ArchiMate Elements"`
- [ ] COM calls: `Repository.IsTechnologyLoaded("WBA")`

---

## Post-Install: Applying the MDG to Existing Repository Data

After deploying an MDG, EA does not automatically update existing elements. Ask the user whether
they want to migrate existing elements to the new stereotypes and tagged values; if yes, walk
through: identify candidate elements with a read-only SQL query, present them for confirmation,
update each via the `update_element` MCP tool (never raw DML — EA's cache won't see it), then
re-run the validation sidecar to catch anything left incomplete. The full four-step workflow with
the SQL and Python calls is in
[references/post-install-migration.md](references/post-install-migration.md).

---

## Quick Linker Rules

Quick Linker (QL) is the hover menu EA shows on a diagram element, offering context-sensitive
connector creation. QL rules live in the MDG XML on the *source* stereotype and name a target
stereotype constraint. Add them only when you've also defined a connector stereotype — a plain,
un-stereotyped relationship (`Dependency`, `Realization`, `Association`) already appears in EA's
default QL menu with no extra XML. Setting `_HideUmlLinks` without at least one QL rule produces
an empty, apparently-broken menu.

The full rule syntax (both the `write_mdg_xml` intermediate-metamodel form and the manual XML
form), the legacy Profile Diagram / MTS Wizard note, and the EA verification steps are in
[references/quick-linker.md](references/quick-linker.md).

---

## Validation Rules — Do NOT Use `<Scripts>` with AI Power Tools

When AI Power Tools for Sparx EA is deployed, **do not embed validation rules in the MDG's
`<Scripts>` section** — that mechanism runs JavaScript inside EA's scripting engine, which the MCP
server cannot reach. Instead, every MDG produced by this skill ships a companion
`<tech_id>_rules.yaml` sidecar and runs it with `ea_validate`; see the `ea-validation` skill
for the schema. The wrong-vs-right XML/YAML comparison, the minimal rules template, and the
smoke-test command are in
[references/validation-sidecar.md](references/validation-sidecar.md).

---

## EA Computer Use — Latency Guidelines

MDG authoring primarily uses file tools, but deployment verification and any diagram-based
checks require the EA UI. Wait before screenshotting — 2–15 seconds depending on the operation —
and never retry without confirming the previous action failed. Full wait-time table and the
standard action/wait/screenshot pattern:
[`../_shared/references/latency.md`](../_shared/references/latency.md).

---

## Researching the Sparx EA API

- MDG Technology authoring → Sparx EA help, search "MDG Technology" or "UML Profile"
- Tagged value types → search "TaggedValueTypes"
- Diagram types → search "Diagram Stereotypes" or "Custom Diagram"
- When documentation is unclear, use `ea.repo_methods()` to enumerate available COM methods at runtime

---

## File Encoding (Critical)

MDG Technology XML files must declare and use `utf-8` encoding, with the declaration and the
actual byte encoding agreeing — EA rejects the file outright if they don't. Full guidance
(legacy `windows-1252` handling, read/write code patterns):
[`../_shared/references/file-encoding.md`](../_shared/references/file-encoding.md).

---

## Reference files

| File | Covers |
|------|--------|
| [references/xml-skeleton.md](references/xml-skeleton.md) | Full `<MDG.Technology>` skeleton; links to the shared file-encoding guidance |
| [references/stereotypes.md](references/stereotypes.md) | Element stereotype XML, attribute and tagged-value-type tables, base-type visibility pitfall and fix, connector stereotype XML |
| [references/diagrams-toolboxes.md](references/diagrams-toolboxes.md) | Custom diagram type XML, toolbox page XML, COLORREF table, ID mapping pattern |
| [references/post-install-migration.md](references/post-install-migration.md) | Four-step workflow for migrating existing elements onto a newly installed MDG |
| [references/quick-linker.md](references/quick-linker.md) | Quick Linker rule syntax, both authoring approaches, verification steps |
| [references/validation-sidecar.md](references/validation-sidecar.md) | Why not `<Scripts>`, YAML sidecar template, smoke-test command |

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
