---
name: ea-import-export
description: Get content into and out of a Sparx EA repository — XMI package export/import, diagram export to PNG/SVG/Visio, and RTF report generation via ea_repository and ea_diagram. Use when a package or diagram needs to leave EA (another repository, a document, a stakeholder without an EA license) or an XMI file needs to come back in.
---

# Import / Export — Sparx EA

*Verified against a live Westbrook Bank repository. Every claim below was exercised against
that model in this session — see the verification table in each reference file for the exact
call and result. Where EA's own behavior surprised the author, that is flagged as a defect, not
smoothed over.*

## 1. Which operation for which purpose

| Need | Operation | Notes |
|---|---|---|
| A picture of a diagram for a document, wiki, or chat | `ea_diagram(operation="get_diagram_png")` / `get_diagram_svg` | Returns bytes inline **and** writes to `path` if given. Fast, no dialog. |
| Same, but you don't need the bytes in the response | `ea_diagram(operation="export_diagram_image", params={..., "format": "png"})` | Identical output to `get_diagram_png` — pick whichever return shape your caller wants. |
| Hand a diagram to a stakeholder who has Visio but not EA, so they can move/relabel shapes | `ea_diagram(operation="export_diagram_to_visio")` | Preserves shape geometry and connectors as editable Visio objects — see §3. |
| Move a package into another repository, or feed a tool that reads XMI | `ea_repository(operation="export_xmi")` / `import_xmi` | **Read the warning in §4 before relying on this for anything you can't afford to lose.** |
| A formatted document (headings, tagged values, prose) rather than a picture | `ea_repository(operation="generate_report")` | RTF only in this server version — see §5. |

Do **not** use the plain `ea_diagram(operation="get_diagram")` read call as an export path even
though it returns image bytes in its `preview_size_bytes`/`saved_path` fields — it is a
diagram-inspection call, and the preview it silently writes lands in the server's own cache
folder next to the model file, not wherever you intend the deliverable to go. Use
`get_diagram_png` / `get_diagram_svg` with an explicit `path` when the PNG or SVG itself is the
deliverable.

## 2. Diagram image export — `get_diagram_png` / `get_diagram_svg` / `export_diagram_image`

All three render faithfully: stereotype labels (`«WBABusinessApplication»`), package-qualified
element names, and box styling matched the live diagram exactly in verification.
`export_diagram_image` and `get_diagram_png` produced byte-identical output for the same diagram
and format.

```python
ea_diagram(operation="get_diagram_png", params={
    "diagram_id": 6,
    "path": "<scratch-dir>\\westbrook_app_landscape.png",
})
```

Pass `refresh=true` if the diagram's underlying rows may have changed out-of-band (direct SQL,
or another session) since it was last rendered — otherwise you may get a stale cached image.
SVG is the better choice when the picture will be scaled or embedded in another vector document;
PNG is fine for chat/Slack/wiki embedding. Neither operation offers a size/DPI parameter — the
image dimensions follow the diagram's own on-canvas size, so a very wide diagram produces a very
wide image rather than one that's reflowed to fit a page.

## 3. Exporting to Visio — `export_diagram_to_visio`

Verified against two diagrams — one with no connectors and one with 8 — and in both cases the
response's `shape_count` and `connector_count` matched the source diagram exactly, and the
`.vsdx` opened as a valid Office document (multi-part zip with `visio/document.xml`,
`visio/pages/page1.xml`). This is the right hand-off for a stakeholder who needs to keep working
with the diagram (move boxes, add annotations) but doesn't have an EA license.

```python
ea_diagram(operation="export_diagram_to_visio", params={
    "diagram_id": 6,
    "path": "<scratch-dir>\\westbrook_app_landscape.vsdx",
})
```

The response also returns `page_width_in` / `page_height_in` — check these before handing the
file over if the target audience will print it; EA's page size follows the diagram's own canvas,
not a standard paper size.

## 4. XMI package export/import — `export_xmi` / `import_xmi`

> **Verified defect (server v2.1.0) — do not trust this path for real interchange without
> checking the output file yourself.** In this session, `export_xmi` against three different
> Westbrook Bank packages (a plain component package, one with tagged values and connectors, and
> one containing a BPMN diagram) every time wrote an **XPDL 2.2 workflow-package stub**, not a
> UML/XMI document — despite the tool's own response reporting `"xmi_type": "XMI 2.1"` and
> `"status": "exported"`. The written file contained a `PackageHeader` and an empty
> `TypeDeclarations` block; no elements, tagged values, or connectors were present. Re-importing
> that file with `import_xmi` into a scratch package reported `"status": "imported"` but created
> **zero** objects and **zero** child packages — confirmed by `execute_sql` counts of `t_object`
> and `t_package` against the target package, both `0`.
>
> **Practical guidance:**
> - Never trust `status: "exported"` / `status: "imported"` alone. Open the exported file (or
>   count rows in the target package after import) before treating the operation as complete.
> - If you need a package to actually survive a round trip today, use EA's baseline/compare
>   tooling (`ea_repository(operation="create_baseline")` etc.) or a `duplicate_package` copy
>   within the same repository instead of `export_xmi`/`import_xmi`.
> - If you hit this yourself and need to report it, escalate through **`ea-diagnostic`** with
>   the exported file attached — the "two failed attempts at the same thing" threshold in
>   `ea-start-here` §3 applies directly here.

Full repro steps, the exact file contents observed, and the SQL used to confirm zero import are
in [`references/xmi-export-import.md`](references/xmi-export-import.md).

## 5. `generate_report` — RTF document generation

```python
ea_repository(operation="generate_report", params={
    "template": "Simple",
    "package_id": 21,
    "output_path": "<scratch-dir>\\account_origination.rtf",
})
```

Three things verified in this session that are easy to get wrong:

1. **`output_path` must end in `.rtf`.** The same call with a `.html` path failed with
   `{"error": "report_failed", "detail": "RunReport returned but output file does not exist"}`
   regardless of the `template` value. This server version generates RTF only through this
   operation.
2. **`template` is not validated against anything in this repository.** This model has no
   custom report templates defined (`SELECT * FROM t_rtfreport` returns zero rows — check this
   first via `ea_analyze(operation="execute_sql", ...)` to see what's actually available). With
   no custom template to find, three different nonsense strings and the plausible-sounding
   `"Simple"` all produced the identical byte-for-byte 20,334-byte default document. A
   `"generated"` status is **not** confirmation your named template was used — open the output
   and check its heading.
3. **Never pass an empty string for `template`.** It reproducibly hung the call (once reported
   as a closed connection, once as a timeout) rather than failing fast. EA itself stayed
   responsive throughout — confirmed with `ping()` and `get_repository_info` immediately after —
   so this is a per-call hang, not a reason to restart EA.

The generated RTF embeds each element's Created/Modified `Author` field verbatim from the
model — that is the modeler's own EA/Windows username, not a Westbrook Bank tagged value. Check
report content for anything identifying before sharing a generated report outside the team.

Full discovery method for real templates once a project has them, and the complete test matrix,
are in [`references/generate-report.md`](references/generate-report.md).

## 6. EA Computer-Use — Latency

Every operation above is MCP-only and does not require driving the EA desktop UI. If you do open
the exported Visio file or generated RTF in their native apps to eyeball them, or open the
diagram in EA to compare against the export, use the standard wait-before-screenshot discipline:
[`../_shared/references/latency.md`](../_shared/references/latency.md).

## Reference files

- [`references/xmi-export-import.md`](references/xmi-export-import.md) — full `export_xmi`/`import_xmi` repro, file contents, and the SQL verification of the failed round trip
- [`references/generate-report.md`](references/generate-report.md) — template discovery, the RTF-only extension requirement, and the empty-template hang

## See also

- `ea-modeling` — for building the content you're about to export in the first place
- `ea-diagnostic` — escalation path for the `export_xmi` defect above, or any other repeated failure
- `_shared/references/westbrook-example.md` — canonical stereotypes/tags used in every example here

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
