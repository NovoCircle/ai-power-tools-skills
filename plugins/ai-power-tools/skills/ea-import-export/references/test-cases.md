# Acceptance cases: `ea-import-export`

This skill promises to pick the right way out of Enterprise Architect for the job (a picture, an
editable Visio file, an XMI package, an RTF report), to check that an export really contains what
it claims, and to say plainly what the server cannot do. Most failures here produce a plausible
success, not an error: a status of "exported" over a file that holds nothing, a "generated" report
that never used the template the person named, a picture that is a stale cached render. This file
is built to catch those.

**Fixture.** A fresh copy of the Westbrook Bank model opened in EA (technology `WBA`, qualified
stereotype form `WBA::`, for example `WBA::WBABusinessApplication`). Westbrook Bank is our
illustration. A customer runs these cases against their own model, substituting their technology,
stereotypes, package and diagram names. The Westbrook copy defines no custom report templates
(`t_rtfreport` is empty); TC-15 depends on that, and a model that does define templates changes
what a correct run says there. Counts quoted below describe the Westbrook copy at the time of
writing; where a case depends on a count, the check reads it from the model.

**Marks.** `WRITE` (the run changes the copy), `EFFECT` (the run writes a file outside the model;
in every EFFECT case here the ask names the folder, so the skill does not need to ask first),
`REFUSE` (the pass is a refusal or a plain "no"), `INVARIANT` (must pass on every run).

## Cases

### TC-01: Picture of a diagram for a wiki

Covers: 1. Which operation for which purpose; 2. Diagram image export — `get_diagram_png` / `get_diagram_svg` / `export_diagram_image`

**Marks:** EFFECT

**Ask:** "I need a picture of the Westbrook Application Landscape diagram for our wiki. Save it as landscape.png in <output-dir>."

**Passes when:** The run exports the diagram as a PNG with an explicit path in the folder named, using `get_diagram_png` or `export_diagram_image` (the skill says the two give identical output). The file exists and the model is unchanged. The run does not reach for the Visio export or the XMI export for a plain picture.

**Check:**

```check
file: landscape.png
expect: exists
```

```check
sql: SELECT (SELECT COUNT(*) FROM t_object), (SELECT COUNT(*) FROM t_connector), (SELECT COUNT(*) FROM t_diagram), (SELECT COUNT(*) FROM t_package), (SELECT COUNT(*) FROM t_objectproperties)
expect: unchanged
```

```check
tools: not-called: ea_diagram.export_diagram_to_visio
tools: not-called: ea_repository.export_xmi
```

**Fails when:** The run exports a Visio file or an XMI package because "export" sounds like one of those, so the wiki gets a file it cannot display. Or it returns the image bytes in the reply and writes nothing to the folder named, so the person has no file. Nothing errors in either case.

### TC-02: The inspection read is not an export path

Covers: 1. Which operation for which purpose

**Marks:** EFFECT

**Ask:** "Get me a PNG of the Account Management Landscape diagram and put it in <output-dir> as account-management.png."

**Passes when:** The run uses an image-export operation with an explicit `path`, and the file is in the folder named. It does not use the plain diagram read (`get_diagram`) as the way to produce the deliverable.

**Check:**

```check
file: account-management.png
expect: exists
```

```check
tools: not-called: ea_diagram.get_diagram
```

```check
sql: SELECT (SELECT COUNT(*) FROM t_object), (SELECT COUNT(*) FROM t_connector), (SELECT COUNT(*) FROM t_diagram), (SELECT COUNT(*) FROM t_package), (SELECT COUNT(*) FROM t_objectproperties)
expect: unchanged
```

**Fails when:** The run calls `get_diagram`, sees the preview bytes and a `saved_path`, and tells the person the picture is saved there. The preview sits in the server's cache folder next to the model file; the folder the person named stays empty. The reply looks like a success and the path it quotes is real.

### TC-03: SVG when the picture will be scaled

Covers: 2. Diagram image export — `get_diagram_png` / `get_diagram_svg` / `export_diagram_image`

**Marks:** EFFECT

**Ask:** "I'm dropping the Technology Layer diagram into a vector design file that will be blown up for a poster. Export it for that into <output-dir>, and call it technology-layer."

**Passes when:** The run chooses SVG, writes `technology-layer.svg` in the folder named, and says why (it scales cleanly where a PNG would not). The file is SVG markup.

**Check:**

```check
file: technology-layer.svg
expect: contains: <svg
```

```check
sql: SELECT (SELECT COUNT(*) FROM t_object), (SELECT COUNT(*) FROM t_connector), (SELECT COUNT(*) FROM t_diagram), (SELECT COUNT(*) FROM t_package), (SELECT COUNT(*) FROM t_objectproperties)
expect: unchanged
```

```check
reply: says SVG was chosen because it scales without losing sharpness
```

**Fails when:** The run exports a PNG because that is the default picture format. The poster comes out soft, and nothing in the run says so.

### TC-04: A diagram edited behind EA's back is re-rendered

Covers: 2. Diagram image export — `get_diagram_png` / `get_diagram_svg` / `export_diagram_image`

**Marks:** EFFECT

**Setup:** The runner exports the Westbrook Application Landscape diagram once, so a render exists, then moves one element on that diagram with a direct SQL update to `t_diagramobjects`.

**Ask:** "A script just rearranged the Westbrook Application Landscape diagram. Export a fresh PNG of it to <output-dir> as landscape-new.png."

**Passes when:** The run passes `refresh=true` (or otherwise forces a re-render) because the diagram's rows changed out of band, and says that it did. The file exists.

**Check:**

```check
file: landscape-new.png
expect: exists
```

```check
tools: called: ea_diagram.get_diagram_png
```

```check
reply: says the image was re-rendered with refresh because the diagram was changed outside EA
```

**Fails when:** The run exports without refresh and hands back the cached image taken before the script ran. The file is a valid PNG of the right diagram with the old layout, and the person publishes it.

### TC-05: No size or DPI is offered

Covers: 2. Diagram image export — `get_diagram_png` / `get_diagram_svg` / `export_diagram_image`

**Marks:** EFFECT

**Ask:** "Export the Technology Layer diagram as a PNG exactly 1200 pixels wide at 300 DPI, into <output-dir> as tech-layer.png."

**Passes when:** The run says the export has no size or DPI setting and that the image follows the diagram's own canvas size, exports the PNG anyway (or offers to), and does not claim 1200 pixels at 300 DPI. A very wide diagram is not reflowed to fit.

**Check:**

```check
reply: says the export has no width or DPI parameter and the image size follows the diagram's own canvas
reply: not: says the image is 1200 pixels wide or 300 DPI
```

```check
sql: SELECT (SELECT COUNT(*) FROM t_object), (SELECT COUNT(*) FROM t_connector), (SELECT COUNT(*) FROM t_diagram), (SELECT COUNT(*) FROM t_package), (SELECT COUNT(*) FROM t_objectproperties)
expect: unchanged
```

**Fails when:** The run passes a `width` or `dpi` parameter the operation does not have, the server ignores it, and the reply reports a 1200-pixel, 300 DPI image. Nothing errors; the number in the reply is invented.

### TC-06: Editable hand-off to a Visio user

Covers: 3. Exporting to Visio — `export_diagram_to_visio`

**Marks:** EFFECT

**Ask:** "A colleague has Visio but no Enterprise Architect license. I want to send her the Customer Engagement Landscape diagram so she can move the boxes around and add notes. Put the file in <output-dir> as customer-engagement."

**Passes when:** The run uses the Visio export, writes `customer-engagement.vsdx` in the folder named, and reports a shape count and connector count that equal the diagram's (13 shapes, 1 connector in the Westbrook copy). It does not send a PNG or an SVG, which she could not edit.

**Check:**

```check
file: customer-engagement.vsdx
expect: exists
```

```check
sql: SELECT COUNT(*) FROM t_diagramobjects d JOIN t_diagram g ON d.Diagram_ID = g.Diagram_ID WHERE g.Name = 'Customer Engagement Landscape'
expect: = 13
```

```check
sql: SELECT COUNT(*) FROM t_diagramlinks l JOIN t_diagram g ON l.DiagramID = g.Diagram_ID WHERE g.Name = 'Customer Engagement Landscape'
expect: = 1
```

```check
reply: says the exported file has 13 shapes and 1 connector, matching the source diagram
```

```check
tools: called: ea_diagram.export_diagram_to_visio
```

**Fails when:** The run exports a PNG "for her to look at", or exports to Visio and reports "exported" without comparing the shape and connector counts to the diagram, so a file that dropped boxes or connectors goes out as complete.

### TC-07: Page size is checked before a printout

Covers: 3. Exporting to Visio — `export_diagram_to_visio`

**Marks:** EFFECT

**Ask:** "Export the Customer Engagement Landscape diagram to Visio into <output-dir> as engagement-print. My colleague is going to print it on letter paper."

**Passes when:** The run reports the page width and height the export returned, and says the page follows the diagram's own canvas, not a standard paper size, so it may not fit letter paper without scaling.

**Check:**

```check
file: engagement-print.vsdx
expect: exists
```

```check
reply: says the page width and height in inches come from the diagram's canvas, not from letter or A4 paper
```

```check
sql: SELECT (SELECT COUNT(*) FROM t_object), (SELECT COUNT(*) FROM t_connector), (SELECT COUNT(*) FROM t_diagram), (SELECT COUNT(*) FROM t_package), (SELECT COUNT(*) FROM t_objectproperties)
expect: unchanged
```

**Fails when:** The run exports the file and says it is ready to print. The page is the size of the canvas, the printout is cropped or tiny, and nothing in the reply warned of it.

### TC-08: An XMI export holds the package's content

Covers: 4. XMI package export/import — `export_xmi` / `import_xmi`

**Marks:** EFFECT, INVARIANT

**Ask:** "Export the Domestic Payments package to an XMI file in <output-dir> called domestic-payments, so we can load it into another repository."

**Passes when:** The file written is XMI and holds the package's elements: every element name in Domestic Payments appears in it, and the file is not a few hundred bytes. The run checks this against the package (the response's `elements_in_package` and `elements_in_export`, or the file itself) before saying it worked.

**Check:**

```check
file: domestic-payments.xml
expect: exists
```

```check
# the 7 elements of the package are in the file by name (the invariant: every element in the package is in the export)
sql: SELECT COUNT(*) FROM t_object o JOIN t_package p ON o.Package_ID = p.Package_ID WHERE p.Name = 'Domestic Payments'
expect: = 7
```

```check
file: domestic-payments.xml
expect: contains: Westbrook Wire Transfer Service
```

```check
file: domestic-payments.xml
expect: contains: Westbrook Check Processing Hub
```

```check
file: domestic-payments.xml
expect: contains: ACH Origination Service
```

```check
file: domestic-payments.xml
expect: contains: ACH Return Handler
```

```check
file: domestic-payments.xml
expect: contains: ACH Notification Service
```

```check
file: domestic-payments.xml
expect: contains: ACI Worldwide Payment Engine
```

```check
file: domestic-payments.xml
expect: contains: Fiserv ACH Processing Module
```

```check
sql: SELECT (SELECT COUNT(*) FROM t_object), (SELECT COUNT(*) FROM t_connector), (SELECT COUNT(*) FROM t_diagram), (SELECT COUNT(*) FROM t_package), (SELECT COUNT(*) FROM t_objectproperties)
expect: unchanged
```

**Fails when:** The run reports "exported" on the strength of the status field alone, over a small file in the wrong format (the earlier defect wrote a ~350-byte workflow stub with none of the elements). The reply looks identical to a real success. This case fails the run whenever the file is missing any of the seven names, however the response read.

### TC-09: The two element counts are read, not the status

Covers: 4. XMI package export/import — `export_xmi` / `import_xmi`

**Marks:** EFFECT

**Ask:** "Export the Consumer Lending package, the one with the loan origination diagram, to XMI in <output-dir> as consumer-lending. Make sure nothing got left out."

**Passes when:** The reply states how many elements the package holds and how many the export holds and that they match (5 and 5 in the Westbrook copy), rather than "status: exported". If the server returned `xmi_export_wrong_format` or `xmi_export_empty`, the run reports a failed export and does not call it done.

**Check:**

```check
file: consumer-lending.xml
expect: exists
```

```check
sql: SELECT COUNT(*) FROM t_object o JOIN t_package p ON o.Package_ID = p.Package_ID WHERE p.Name = 'Consumer Lending'
expect: = 5
```

```check
reply: says the number of elements in the package and the number in the export, and that the two match
reply: not: reports the export as good on the status field alone
```

```check
sql: SELECT (SELECT COUNT(*) FROM t_object), (SELECT COUNT(*) FROM t_connector), (SELECT COUNT(*) FROM t_diagram), (SELECT COUNT(*) FROM t_package), (SELECT COUNT(*) FROM t_objectproperties)
expect: unchanged
```

**Fails when:** The run reads `"status": "exported"`, says the package is exported, and the person finds out later that the file is incomplete. "Nothing left out" was the ask; the run answered it without looking.

### TC-10: A requested XMI version is used

Covers: 4. XMI package export/import — `export_xmi` / `import_xmi`

**Marks:** EFFECT

**Ask:** "The other team's tool only reads XMI 2.5.1. Export the Domestic Payments package for them into <output-dir> as domestic-payments-251."

**Passes when:** The run passes `xmi_type` "XMI 2.5.1" (not the default 2.1), the file is written, and the reply names the version used.

**Check:**

```check
file: domestic-payments-251.xml
expect: exists
```

```check
reply: says the export was made as XMI 2.5.1
```

```check
sql: SELECT (SELECT COUNT(*) FROM t_object), (SELECT COUNT(*) FROM t_connector), (SELECT COUNT(*) FROM t_diagram), (SELECT COUNT(*) FROM t_package), (SELECT COUNT(*) FROM t_objectproperties)
expect: unchanged
```

**Fails when:** The run leaves `xmi_type` out and the server writes XMI 2.1, the default. The file is valid, holds every element, and the other team's tool rejects it. The reply says "exported as XMI" without the version.

### TC-11: "Is XMI export broken?" gets the current answer

Covers: 4. XMI package export/import — `export_xmi` / `import_xmi`

**Ask:** "A colleague told me the XMI export in this tool writes empty files and reports success anyway. Is that still true? I need to move a package to another repository."

**Passes when:** The run says that was a real defect, that it was fixed in server 2.2.0, and that the server now reads the file back and returns an error instead of a false success. It still recommends comparing the element counts. It does not tell the person to avoid the operation or to report it as a live defect.

**Check:**

```check
reply: says the empty-file defect was fixed in server 2.2.0 and the server now checks the file before reporting success
reply: says to compare elements_in_package with elements_in_export
reply: not: tells the person that export_xmi currently writes empty files
reply: not: tells the person to report the export_xmi defect through ea-diagnostic
```

```check
sql: SELECT (SELECT COUNT(*) FROM t_object), (SELECT COUNT(*) FROM t_connector), (SELECT COUNT(*) FROM t_diagram), (SELECT COUNT(*) FROM t_package), (SELECT COUNT(*) FROM t_objectproperties)
expect: unchanged
```

**Fails when:** The run reads the historical reference as current advice and says the XMI path cannot be trusted, or it sends the person to `ea-diagnostic` for a defect that has been fixed. The person abandons a working route.

### TC-12: An XMI import is proved by counting what landed

Covers: 4. XMI package export/import — `export_xmi` / `import_xmi`

**Marks:** WRITE, INVARIANT

**Setup:** The runner exports the Treasury Services package (one element, Westbrook Business Treasury Portal) to `<output-dir>\treasury-services.xml`, then deletes that package from the copy.

**Ask:** "I have an export of the Treasury Services package at <output-dir>\treasury-services.xml. Bring it back into the model under Transactions & Payments."

**Passes when:** The run imports the file into the Transactions & Payments package and then confirms by reading the model that the package and its element are back, with the element's stereotype and tagged values intact. It reports the result from that count, not from the import status.

**Check:**

```check
# the package is back under the right parent
sql: SELECT COUNT(*) FROM t_package c JOIN t_package p ON c.Parent_ID = p.Package_ID WHERE c.Name = 'Treasury Services' AND p.Name = 'Transactions & Payments'
expect: = 1
```

```check
# the element is back, with its stereotype
sql: SELECT o.Stereotype FROM t_object o JOIN t_package p ON o.Package_ID = p.Package_ID WHERE o.Name = 'Westbrook Business Treasury Portal' AND p.Name = 'Treasury Services'
expect: rows: [["WBABusinessApplication"]]
```

```check
# its tagged values came back
sql: SELECT tp.Value FROM t_objectproperties tp JOIN t_object o ON tp.Object_ID = o.Object_ID WHERE o.Name = 'Westbrook Business Treasury Portal' AND tp.Property = 'criticality'
expect: rows: [["Business-Critical"]]
```

```check
reply: says the package and its element were found in the model after the import
reply: not: reports the import as done on the strength of the status field alone
```

**Fails when:** The run calls `import_xmi`, reads `"status": "imported"`, and reports the package restored. If nothing landed, or the element arrived without its tagged values, the person finds out later. The earlier defect did exactly this: a success status over zero rows created.

### TC-13: A report comes out as an RTF document

Covers: 5. `generate_report` — RTF document generation

**Marks:** EFFECT

**Ask:** "Give me a document of the Account Origination package that I can open in Word. Put it in <output-dir> as account-origination."

**Passes when:** The run generates the report with an `output_path` ending in `.rtf`, the file exists and is RTF, and the reply says it is an RTF document.

**Check:**

```check
file: account-origination.rtf
expect: contains: {\rtf
```

```check
sql: SELECT (SELECT COUNT(*) FROM t_object), (SELECT COUNT(*) FROM t_connector), (SELECT COUNT(*) FROM t_diagram), (SELECT COUNT(*) FROM t_package), (SELECT COUNT(*) FROM t_objectproperties)
expect: unchanged
```

```check
tools: called: ea_repository.generate_report
```

**Fails when:** The run builds the output path with a `.docx` or `.html` extension. The call fails with `report_failed`, the run retries with other template names, and the failure is blamed on the template.

### TC-14: A request for HTML is answered with the RTF limit

Covers: 5. `generate_report` — RTF document generation

**Marks:** EFFECT

**Ask:** "Generate the Account Origination report as an HTML page for our intranet. Save it in <output-dir> as account-origination."

**Passes when:** The run says the report operation produces RTF only in this server version, does not try an `.html` path, and either produces the `.rtf` and says so or asks what the person wants to do. It does not claim an HTML report exists.

**Check:**

```check
reply: says the report operation writes RTF only in this server version
reply: not: says an HTML report was generated
```

```check
file: account-origination.rtf
expect: exists
```

```check
sql: SELECT (SELECT COUNT(*) FROM t_object), (SELECT COUNT(*) FROM t_connector), (SELECT COUNT(*) FROM t_diagram), (SELECT COUNT(*) FROM t_package), (SELECT COUNT(*) FROM t_objectproperties)
expect: unchanged
```

**Fails when:** The run passes `account-origination.html`, gets `RunReport returned but output file does not exist`, then loops over template names looking for one that works. The extension was the cause every time.

### TC-15: A named template that does not exist is not applied

Covers: 5. `generate_report` — RTF document generation

**Marks:** EFFECT, INVARIANT

**Ask:** "Generate the Account Origination report using our Executive Summary template, saved in <output-dir> as account-origination-exec."

**Passes when:** The run looks at what report templates the model defines (`t_rtfreport`), finds none, and says so. It then tells the person that the template name selected nothing: any name gives the same default document, and "generated" does not mean the Executive Summary layout was used. It tells them how to get a real one (define the template in EA first). It does not say the Executive Summary template was applied.

**Check:**

```check
# precondition: the model has no custom report templates
sql: SELECT COUNT(*) FROM t_rtfreport
expect: = 0
```

```check
tools: called: ea_analyze.execute_sql
```

```check
reply: says the model defines no report templates, so the template name selected nothing and the default document was produced
reply: not: says the Executive Summary template was applied
```

```check
sql: SELECT (SELECT COUNT(*) FROM t_object), (SELECT COUNT(*) FROM t_connector), (SELECT COUNT(*) FROM t_diagram), (SELECT COUNT(*) FROM t_package), (SELECT COUNT(*) FROM t_objectproperties)
expect: unchanged
```

**Fails when:** The run passes "Executive Summary", gets `status: "generated"` and a 20 KB file, and reports the executive summary report done. Nothing errors. The document is the built-in default, and the person sends it on as the layout they asked for.

### TC-16: "No template" does not become an empty template

Covers: 5. `generate_report` — RTF document generation

**Marks:** EFFECT

**Ask:** "Generate the Account Origination report with no template at all, just the plain default, into <output-dir> as account-origination-plain."

**Passes when:** The run supplies a non-empty template value (for example "Simple") and says the default document is what comes out. The call returns and the file exists.

**Check:**

```check
file: account-origination-plain.rtf
expect: contains: {\rtf
```

```check
reply: says a non-empty template name was supplied because an empty one hangs the call
```

```check
sql: SELECT (SELECT COUNT(*) FROM t_object), (SELECT COUNT(*) FROM t_connector), (SELECT COUNT(*) FROM t_diagram), (SELECT COUNT(*) FROM t_package), (SELECT COUNT(*) FROM t_objectproperties)
expect: unchanged
```

**Fails when:** The run takes "no template" literally and passes an empty string. The call hangs or returns a closed connection or a timeout, and the run reports that Enterprise Architect has crashed. No file is written.

### TC-17: A report is not ready to share until its authors are checked

Covers: 5. `generate_report` — RTF document generation

**Marks:** EFFECT, INVARIANT

**Ask:** "Generate the Account Origination report in <output-dir> as audit-copy and tell me whether it's ready to go to the external auditors."

**Passes when:** The run generates the report and tells the person it is not ready to send until reviewed: each element's Created and Modified details carry the modeler's own login name from the model, which the run names as a risk. It either checks the file for those names or asks the person to. It does not send anything.

**Check:**

```check
file: audit-copy.rtf
expect: exists
```

```check
# precondition: the elements in the package carry an author, so the risk is real in this copy
sql: SELECT COUNT(*) FROM t_object o JOIN t_package p ON o.Package_ID = p.Package_ID WHERE p.Name = 'Account Origination' AND o.Author <> ''
expect: >= 1
```

```check
reply: says the report embeds each element's author or modifier name from the model, so it should be reviewed before it goes outside the team
reply: not: says the report is ready to send without review
```

```check
sql: SELECT (SELECT COUNT(*) FROM t_object), (SELECT COUNT(*) FROM t_connector), (SELECT COUNT(*) FROM t_diagram), (SELECT COUNT(*) FROM t_package), (SELECT COUNT(*) FROM t_objectproperties)
expect: unchanged
```

**Fails when:** The run generates the file and says "ready for the auditors". The RTF carries `Author:` lines with a real person's login on every element, and it leaves the building. A report in an otherwise fully fictional model still does this.

### TC-18: A call that hangs is diagnosed, not guessed at

Covers: 5. `generate_report` — RTF document generation; Verify in EA's UI

**Ask:** "I ran the report with a blank template name and the connection closed. EA looks frozen. What's going on, and should I restart it?"

**Passes when:** The run does not tell the person to restart or kill EA. It names the blank template as the known cause of this hang, confirms EA still answers with a cheap call (`ping`, then `get_repository_info`), and looks at EA's screen for a dialog before concluding anything. If it cannot see the screen, it says so and asks the person to look and read any dialog aloud. It does not report a hang cause it has not checked.

**Check:**

```check
reply: says an empty template name is the known cause of this hang
reply: says it checked or will check that EA still responds before suggesting a restart
reply: says to look at EA's screen for a dialog, or asks the person to look because it cannot
reply: not: tells the person to restart or close Enterprise Architect
```

```check
sql: SELECT (SELECT COUNT(*) FROM t_object), (SELECT COUNT(*) FROM t_connector), (SELECT COUNT(*) FROM t_diagram), (SELECT COUNT(*) FROM t_package), (SELECT COUNT(*) FROM t_objectproperties)
expect: unchanged
```

**Fails when:** The run says EA has crashed and tells the person to restart it, discarding unsaved work, or declares the cause a dialog it never looked for. Both read as confident diagnoses.

### TC-19: What a Cowork session can read

Covers: 5b. Reading the results from a Claude Cowork or cloud session

**Ask:** "I want to look at the exports and the report in a Claude Cowork session. Where should I put the files?"

**Passes when:** The run tells the person to export everything into one dedicated output folder and connect that folder to the session, not the folder that holds the model file. It says such a session can read the XMI, images and reports, and that a generated report should be reviewed for identifying details before the folder is connected.

**Check:**

```check
reply: says to export into one output folder and connect that folder
reply: says not to connect the folder that holds the model file
reply: says a report should be reviewed for identifying details before the folder is connected
```

```check
sql: SELECT (SELECT COUNT(*) FROM t_object), (SELECT COUNT(*) FROM t_connector), (SELECT COUNT(*) FROM t_diagram), (SELECT COUNT(*) FROM t_package), (SELECT COUNT(*) FROM t_objectproperties)
expect: unchanged
```

**Fails when:** The run says to connect the folder with the `.qea` file because "that is where everything is". The session then sees the whole model file, not just the outputs.

### TC-20: A Cowork session cannot import anything back

Covers: 5b. Reading the results from a Claude Cowork or cloud session

**Marks:** REFUSE

**Ask:** "If I do my review in a Claude Cowork session, can I ask it to fix the package and import the corrected XMI back into the model from there?"

**Passes when:** The run says no: such a session can read the files but cannot change the model or import anything, because the server is not available in those sessions today. The correction and the import happen from a session that has the server. It does not call `import_xmi`.

**Check:**

```check
reply: says a Cowork or cloud session cannot change the model or import XMI because the server is not available there
```

```check
tools: not-called: ea_repository.import_xmi
```

```check
sql: SELECT (SELECT COUNT(*) FROM t_object), (SELECT COUNT(*) FROM t_connector), (SELECT COUNT(*) FROM t_diagram), (SELECT COUNT(*) FROM t_package), (SELECT COUNT(*) FROM t_objectproperties)
expect: unchanged
```

**Fails when:** The run says yes and describes an import from the Cowork session. The person plans a review round-trip that cannot happen.

## Invariants

Three properties can be checked on any run without a known-good answer.

1. **XMI export: every element in the source package is in the file.** For any package P exported,
   each `t_object.Name` with `Package_ID = P` appears in the XMI file, and the reply reports the
   package and export element counts. A stub, a wrong-format file or a truncated export fails this
   however the status field reads (TC-08, TC-09).
2. **XMI import: what the file held is in the target package afterwards.** The package, the element
   and its tagged values are read back from the model, not inferred from the import status (TC-12).
3. **Visio export: the shape and connector counts in the response equal the diagram's** objects and
   links in `t_diagramobjects` and `t_diagramlinks` (TC-06).

These do not cover fidelity. Names being present does not show that tagged values, connectors or
diagrams survived an XMI export, and matching shape counts do not show that the shapes sit where
they did in EA. TC-12 checks the stereotype and one tagged value on the one element it restores;
nothing here compares a whole package round trip.

## Headings not covered

- Import / Export — Sparx EA: the title and the "verified against a live repository" note; no behavior of its own.
- 6. EA Computer-Use — Latency: the one checkable claim, that exports need no screen driving, needs a tool name for computer use that the check grammar does not define; the rest is a pointer to the shared latency table, whose wait times a case cannot observe. See Findings.
- Reference files: a list of links.
- See also: a list of links.

## Findings

- SKILL.md "See also" sends the `export_xmi` defect to `ea-diagnostic` as an "escalation path for the `export_xmi` defect above", but section 4 says the defect was fixed in server 2.2.0; TC-11 requires the run not to follow that pointer.
- SKILL.md section 1 table says "Read the warning in §4 before relying on this for anything you can't afford to lose", but section 4 now holds a "Fixed" note and no warning; the pointer is stale.
- `references/generate-report.md` (and the SKILL.md section 5 text built on it) was measured on server 2.1.0; nothing records that the RTF-only limit, the template behavior or the empty-template hang still hold after 2.2.0.
- `references/generate-report.md` calls the empty-template hang "a per-call hang, not a reason to restart EA" on the strength of a `ping` answering, while `_shared/references/ea-ui-verification.md` says a hang is usually a blocking dialog and that nobody should conclude anything before looking at the screen; the two disagree on whether the diagnosis is already known. TC-18 asks for both (named cause plus a look at the screen).
- SKILL.md "Verify in EA's UI" tells the reader to reload and screenshot "after any diagram create or edit", which an export skill never performs; only its hang advice applies here.
- SKILL.md says the intro "Every claim below was exercised against that model ... see the verification table in each reference file"; `references/xmi-export-import.md` records the failed (now fixed) behavior, so nothing in this skill shows a verified working XMI export or import round trip.
- `import_xmi` is a model write that can overwrite elements whose identifiers already exist in the target, but SKILL.md section 4 says nothing about taking a baseline first, or about importing into a repository that already holds the package; TC-12 avoids the case by deleting the source package in setup.
- The `tools` check can name an operation but not its parameters, so `refresh=true` (TC-04), `xmi_type` (TC-10) and a non-empty template (TC-16) are graded through the reply and the file, which an agent could misreport; the runner design needs a parameter check.
- TC-10 cannot test that the file is XMI 2.5.1: the version marker EA writes at the top of an XMI 2.5.1 file was not verified, so the check stops at "file exists" plus the reply.
- TC-18 and the SKILL.md latency section depend on a `computer-use` transcript tool name; none is defined in the template's `tools` grammar.
