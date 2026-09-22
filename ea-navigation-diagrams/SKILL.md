---
name: ea-navigation-diagrams
description: How to generate click-through "navigation diagrams" over hierarchical data in a Sparx EA repository — the composite-element mechanism, the nested-container layout, the exact write sequence, and verification. Use this skill whenever a repository contains or has just been loaded with hierarchical elements (capability models, taxonomies, org structures, product breakdowns, reference models) and the user wants to browse them by clicking down through levels rather than reading a tree diagram.
---

# EA Navigation Diagrams

**Skill Name:** ea-navigation-diagrams

**Purpose:** Turn a hierarchy that already exists in an EA repository into a set of drill-down diagrams, one per parent, where double-clicking a parent opens the diagram of its children. Companion to `ea-mcp-modeling` — that skill covers building the model; this one covers making the model navigable.

## What a navigation diagram is

A navigation diagram is an ordinary diagram that has been attached to an element as its **child diagram**, with the element flagged **composite**. On any diagram where that element appears, EA draws a small marker in the element's bottom-right corner — users describe it as the "eyeglasses" or "chain-link" icon — and double-clicking the element opens the child diagram.

Chained across levels, this turns a hierarchy into something a non-modeller can browse: a landing diagram of the top level, each box opening the level below it, all the way to the leaves. It replaces the classic one-big-tree diagram, which stops being readable past about thirty elements.

It is **not** a hyperlink element, **not** a diagram frame, and **not** a Navigation Cell. Those are different EA features with different storage and different behaviour.

## The mechanism — two parts, both required

| # | What | Where it lives | Value |
|---|------|----------------|-------|
| 1 | The diagram is made a child of the element | `t_diagram.ParentID` | the element's `Object_ID` |
| 2 | The element is flagged composite | `t_object.NType` | `8` (default is `0`) |

Both are required. This is the single most important fact in this skill:

- `ParentID` alone → the diagram is owned by the element and appears under it in the Browser, but the element shows **no marker and does not navigate on double-click**.
- `NType = 8` alone → nothing to navigate to.

A repository that has hand-built navigation diagrams will often contain a mix. Before extending someone's existing pattern, audit it:

```sql
SELECT o.Object_ID, o.Name, o.NType,
       (SELECT COUNT(*) FROM t_diagram d WHERE d.ParentID = o.Object_ID) AS child_diagrams
FROM t_object o
WHERE o.Package_ID = <pkg>
  AND EXISTS (SELECT 1 FROM t_diagram d2 WHERE d2.ParentID = o.Object_ID)
  AND o.NType <> 8
```

Any rows returned are elements that look navigable to the author but are not. Fixing them is `UPDATE t_object SET NType = 8 WHERE Object_ID IN (...)`.

This audit query is the highest-value check in this skill — it is exactly what would have caught the 6-of-21 "looks navigable but isn't" defect described below, automatically, before a user ever clicked and found nothing. Run it before extending any existing set, and offer to run it any time a user asks about navigation diagrams in a repository you didn't build yourself.

> **Note on `t_diagram.ParentID`:** despite what some schema documentation says, this column holds the parent **element's** `Object_ID`, not a parent diagram and not a package. `Package_ID` is the owning package and is independent of it. An element-owned diagram (`ParentID > 0`) appears in the Browser under the element, not in the package's diagram list, so it does not clutter the package and does not collide with same-named package-level diagrams.
>
> The `describe_table('t_diagram')` schema notes returned by `ea_analyze` currently state the opposite ("ParentID here is parent *diagram*, not package") — that is a documentation defect (tracked separately), not a description of this mechanism. Trust this skill's statement, not that note, until the doc is fixed.

## When to offer this

Offer to build navigation diagrams whenever **all** of these hold:

1. The repository contains a parent/child hierarchy — either element parentage (`t_object.ParentID`), a containment connector (`PartOf`, `Aggregation`, `Composition`, `Decomposition`, or an MDG equivalent), or a level tagged value (`Level` = 1/2/3, `Tier`, `Depth`).
2. It is more than one level deep and has more than roughly a dozen elements — below that a single diagram is better.
3. The hierarchy is reasonably stable. Navigation diagrams are cheap to rebuild, but they do need rebuilding when the hierarchy changes.

Typical subjects: business and technical capability models, technology reference models, product/service taxonomies, organisation structures, requirement and risk breakdowns, information/data domain models, value stream hierarchies.

**Always confirm the source of truth first.** A model can carry the hierarchy in element parentage *and* in connectors, and they can disagree. Element parentage is what EA's Browser and nesting render from, so prefer it; but say which one you used, and report the disagreement rather than silently picking one.

```sql
-- parentage view
SELECT ParentID, COUNT(*) FROM t_object WHERE Package_ID = <pkg> GROUP BY ParentID;
-- connector view
SELECT c.Start_Object_ID, COUNT(*) FROM t_connector c
 WHERE c.Stereotype LIKE '%PartOf%' GROUP BY c.Start_Object_ID;
```

## Build procedure

### Phase 0 — read the hierarchy

Pull the whole set in one query: `Object_ID`, `Name`, `ParentID`, and the level tag if present. Derive:

- **roots** — elements with no parent inside the scope
- **parents** — every element with at least one child (these get a diagram and `NType = 8`)
- **leaves** — no children, no diagram, no flag

Diagram count = 1 landing diagram + one per parent.

### Phase 1 — pick or copy a template

If the repository already has a navigation diagram the user likes, read its `t_diagram` row and copy `Diagram_Type`, `PDATA`, `Swimlanes` and `StyleEx` verbatim. `StyleEx` is what carries the MDG diagram profile (`MDGDgm=<Profile>::<Diagram>`), the theme (`Theme=:<n>`) and the connector-label suppression that keeps the picture clean.

With no template, a sensible default is diagram type `Logical` plus:

```
StyleEx:  ExcludeRTF=0;DocAll=0;HideQuals=0;AttPkg=1;SuppressFOC=1;SwimlanesActive=1;
          TConnectorNotation=UML 2.1;SPT=1;ShowNotes=0;SuppConnectorLabels=1;
          HideConnStereotype=1;SuppressedCompartments=;
PDATA:    HideRel=0;ShowTags=0;ShowReqs=0;ShowCons=0;ShowIcons=1;ShowShape=1;
          HideProps=0;HideStereo=0;ShowRec=1;FormName=;
```

### Phase 2 — create the diagram rows

One diagram per parent, plus one landing diagram with `ParentID = 0` in the package.

Name each child diagram after its element. Because element-owned diagrams surface under the element rather than in the package list, reusing the element name is unambiguous and is what hand-built examples do.

Insert only the identifying columns, then set the bulky repeated columns (`PDATA`, `StyleEx`, `Swimlanes`, the show/hide flags, dates) in a single follow-up `UPDATE` over the whole batch. Tag the batch — `Author`, or a temporary `Version` marker — so the follow-up update and the later ID lookup can find exactly these rows.

GUIDs must be the braced upper-case form. Dialects differ:

| Repository | GUID expression |
|---|---|
| MySQL | `CONCAT('{', UPPER(UUID()), '}')` |
| SQL Server | `CONCAT('{', UPPER(CONVERT(varchar(36), NEWID())), '}')` |
| Oracle | `'{' \|\| UPPER(REGEXP_REPLACE(...SYS_GUID()...)) \|\| '}'` |
| Access / SQLite (.eap, .qea) | generate host-side and pass a literal |

Then read back the assigned `Diagram_ID` for each `ParentID` — never assume the IDs are contiguous.

### Phase 3 — place the objects

Each child diagram holds the parent drawn as a large container with its immediate children laid out inside it. No connectors: the hierarchy is already expressed by the nesting, and connectors turn the picture back into the tree diagram this is meant to replace.

Geometry that reproduces the common hand-built pattern (EA's Y axis is negative downward):

```
W, H        = 130, 80        # child box; widen for long names, keep H
HGAP, VGAP  = 40, 40
PAD_L/R     = 45
PAD_T       = 60             # room for the container's own title
PAD_B       = 40
ORIGIN      = (left 50, top -60)
COLS        = min(child_count, 4)

container.left   = 50
container.right  = 50 + PAD_L + PAD_R + COLS*W + (COLS-1)*HGAP
container.top    = -60
container.bottom = container.top - (PAD_T + PAD_B + ROWS*H + (ROWS-1)*VGAP)

child[i].left = 50 + PAD_L + col*(W + HGAP)
child[i].top  = -60 - PAD_T  - row*(H + VGAP)
```

The landing diagram is the same grid with no container — the roots laid out directly.

`Sequence` is z-order, lowest in front: give the container the highest number and the children `1..n`, or the container paints over them.

`ObjectStyle` carries the per-instance appearance. `DUID` must be unique within the diagram; deriving it from the `Object_ID` in hex (`LPAD(HEX(Object_ID), 8, '0')`) is deterministic and collision-free. `BCol` is a **BGR** integer, not RGB. Colour the container with the stereotype default (`BCol=-1`) and the children with a contrasting fill — this is the visual cue for "the thing you drilled into" versus "the things you can drill into next".

```
container: DUID=<8hex>;UCRect=1;NSL=0;BCol=-1;BFol=-1;LCol=-1;LWth=-1;fontsz=0;bold=0;
           black=0;italic=0;ul=0;charset=0;pitch=0;HideIcon=0;LBL=CX=<width>:CY=15:OX=0:
           OY=0:HDN=0:BLD=0:ITA=0:UND=0:CLR=-1:ALN=1:ALT=0:ROT=0;
child:     DUID=<8hex>;UCRect=1;NSL=0;BFol=-1;LCol=-1;LWth=-1;fontsz=0;bold=0;black=0;
           italic=0;ul=0;charset=0;pitch=0;HideIcon=0;BCol=<bgr>;LBL=CX=<width>:CY=15:…
```

As with the diagram rows, insert the geometry first with a one-character placeholder in `ObjectStyle`, then set the real style in two batch updates (one for containers, one for children) using `CONCAT` over `Object_ID` and `RectRight - RectLeft`. It keeps the statements small and the style consistent.

### Phase 4 — flag the parents composite

```sql
UPDATE t_object SET NType = 8 WHERE Object_ID IN (<every parent>)
```

Leaves stay at `NType = 0`. That is correct and meaningful: no marker tells the user there is nothing below.

> **API-gap note (check before using the raw SQL above):** as of this writing there is no MCP operation that sets `t_object.NType` or otherwise touches EA's `Element.CompositeDiagram` COM property — `ea_model("set_composite_diagram")` is proposed but not shipped (tracked as **APT-2026-0059**). Before doing the `UPDATE` by hand, call `ea_analyze("execute_sql", {"sql": "SELECT ..."})` or check the backlog to see whether `set_composite_diagram` (or equivalent) has landed in the running server version. If it has, use it instead — it is expected to set `t_diagram.ParentID` and `t_object.NType` together in one call, which removes the two-part-mechanism failure mode (§ "The mechanism", above) at the source. Until then, the raw SQL above is correct and is the only path.

### Phase 5 — verify, then refresh

```sql
SELECT
 (SELECT COUNT(*) FROM t_diagram       WHERE Diagram_ID BETWEEN <lo> AND <hi>) AS diagrams,
 (SELECT COUNT(*) FROM t_diagramobjects WHERE Diagram_ID BETWEEN <lo> AND <hi>) AS objects,
 (SELECT COUNT(*) FROM t_diagramobjects WHERE Diagram_ID BETWEEN <lo> AND <hi>
    AND LENGTH(ObjectStyle) < 10)                                              AS unstyled,
 (SELECT COUNT(*) FROM t_diagramlinks   WHERE DiagramID  BETWEEN <lo> AND <hi>) AS stray_links,
 (SELECT COUNT(*) FROM t_object WHERE Package_ID = <pkg> AND NType = 8)         AS composites
```

Expect: `diagrams` = 1 + parents, `objects` = roots + Σ(1 + children), `unstyled` = 0, `stray_links` = 0, `composites` = parents.

Then **render at least the landing diagram, one mid-level diagram and one leaf-level diagram and look at them.** Confirm the marker is present on every box that should drill down, the children sit inside the container, and no name is clipped. Counting rows is not verification; the deliverable is a picture.

EA caches diagrams it has already rendered, so a diagram written by SQL and previously opened will render stale. Call `ea_diagram("reload_diagram")` before rendering. Tell the user to reload the package in the Browser (right-click the package → *Contents → Reload Current Package*) or reopen the model — writes that go to the repository do not reach an EA session that already has the package cached.

## Why not `add_elements_to_diagram_bulk`

The bulk add is the natural tool for this and currently cannot produce the result:

- it re-runs a hierarchical auto-layout on every call and ignores supplied positions, so the container/nested arrangement is destroyed
- it auto-draws connectors between elements already on the diagram, reintroducing the tree
- it exposes no way to set `ObjectStyle`, so the parent/child colour cue cannot be applied

Until it grows `layout=none`, explicit positions and a per-object style argument, build the diagram objects by direct writes. Do the same for the composite flag — there is no API operation for `NType` (see the API-gap note in Phase 4, above).

**Tracking note:** both gaps have open backlog items — **APT-2026-0050** (`add_elements_to_diagram_bulk` position/style parameters, `layout=none` opt-out, `auto_connectors` opt-out) and **APT-2026-0059** (`set_composite_diagram`). As of this skill's last review, neither has shipped in `ea-mcp-server` — `add_elements_to_diagram_bulk` still takes only a plain `element_ids` list with no per-element position or style, and no operation anywhere sets `t_object.NType`. Re-check both before relying on this section: if `add_elements_to_diagram_bulk` has grown per-element `left/top/width/height/style` parameters and a `layout="none"` option, use it for Phase 3 instead of direct `t_diagramobjects` writes; if `set_composite_diagram` (or an equivalent) exists, use it for Phase 4 instead of the raw `UPDATE`. Direct SQL will still work as a fallback either way, but the API path is idempotent and less error-prone once available.

Where the API *does* work, use it: `ea_model("create_package")` for the staging/holding packages, `ea_diagram("reload_diagram")` for cache refresh, and `ea_diagram("get_diagram_png")` for visual verification.

## Known traps

| Trap | Detail |
|---|---|
| Silent property drop | `ea_diagram("create_diagram"/"update_diagram")` passes `properties` keys through to the COM object **case-sensitively** and ignores unknown keys without error. `ParentID` works; `parent_id` is accepted and discarded. Always check `applied_properties` in the response. |
| `t_diagramlinks` column name | It is `DiagramID`, not `Diagram_ID` as on `t_diagram` and `t_diagramobjects`. |
| `describe_table` argument | The parameter is `table`, not `table_name`. |
| BGR not RGB | `BCol=15658671` is `RGB(175,238,238)` — bytes reversed. |
| Filtering on a column you are also setting | `UPDATE … SET Version='1.0' WHERE Version='DD'` applies the `WHERE` first and then destroys the marker. Keep the batch marker out of the `SET` list, or re-identify rows by `Author` + creation date. |
| Long names | A 130×80 box holds roughly four short words. Measure the longest name in the set before fixing box width; a taxonomy of long phrases needs a wider box, not a smaller font. |
| Duplicate names among siblings | Legal in EA and common in imported taxonomies. Diagram names will duplicate too. Harmless, but say so rather than letting the user discover it. |

## Rebuilding after the hierarchy changes

Navigation diagrams are derived artefacts. When the source hierarchy is reloaded or edited:

- a **new parent** needs a diagram and `NType = 8`
- an element that **lost all its children** should have its diagram removed and `NType` reset to `0`, or it navigates to an empty picture
- a **renamed** element should have its child diagram renamed to match
- **moved** children need their diagram object rows rewritten on both the old and the new parent's diagram

The cheapest correct approach is to regenerate the whole set for the affected package rather than patch it. Identify the generated set by author/date or by a marker so a regeneration can find and replace exactly its own output.

**Never delete the user's existing diagrams to make room.** Move superseded diagrams to a clearly named holding package (`_to-delete (superseded diagrams)`) inside the same scope, tell the user what moved and why, and let them do the deleting.

## Reporting back

Tell the user, in plain language: how many diagrams were created and where, which elements are now navigable, which are leaves, what the entry-point diagram is called, and that the Browser needs a reload. Include the count of elements that were already navigable versus newly flagged if you fixed an existing set.
