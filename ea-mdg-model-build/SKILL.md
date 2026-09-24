---
name: ea-mdg-model-build
description: Build a Sparx EA MDG Technology from a model held inside the repository — requirements, design metamodel, profile packages, toolbox and diagram profiles, then export and generate the MDG XML. Use when the MDG has a source model in EA, or when a hand-authored MDG needs to be brought under model control.
---

# Building an MDG Technology from a Model

*Grounded in an end-to-end, model-driven build of the Westbrook Bank Architecture (`WBA`)
technology. Tool-surface claims verified against `ea-mcp-server` v2.0.0 (2026-09-21) — see the
note at the bottom of Quick Reference.*

Two ways exist to produce an MDG. This skill covers the model-driven one. `ea-mdg-author` covers the other.

| Path | Source of truth | Use when |
|---|---|---|
| **Model-driven** (this skill) | Profile packages in an EA repository | The MDG has a lifecycle — multiple versions, more than one author, a design metamodel that stakeholders review |
| **Direct XML** (`ea-mdg-author`) | The `.xml` file | One-off technology, a patch to a shipped file, or no repository to host the source |

⚠ **These two paths diverge permanently.** Hand-editing an MDG that has a source model means the next model-driven export silently discards the edit. Pick one per technology and record which in the profile package notes. To move from direct XML to model-driven, import the XML as a profile package first (`Publish Technology ▸ Import Package as UML Profile`), then never hand-edit again.

---

## Quick Reference

| Task | Route |
|---|---|
| Create stereotype, attribute, constraint | MCP API |
| Duplicate a package | **EA UI only** — Paste as New, new GUIDs |
| Connector tagged value (Quick Linker constraint) | **EA UI only** — no API route |
| Element background colour | **EA UI only** — `update_element` ignores `backcolor` |
| Export a profile | **EA UI only** — Publish Package as UML Profile |
| Build the MDG | **EA UI only** — MDG Technology Wizard |
| Reference data (tagged value types) | **EA UI only** — Settings ▸ Reference Data ▸ Project Types |
| Verify anything | MCP API + parse the built XML |

The rule that keeps this efficient: **build with the API, finish in the UI, verify with the API.**

> **Table current as of 2026-09-21.** Every "EA UI only" row above was confirmed against the
> live `ea_mcp_server/server.py` source, not just observed behaviour. Several are the direct
> target of in-flight backlog work in the same batch as this skill: package duplication
> (`APT-2026-0054`), connector tagged values (`APT-2026-0052`), the wizard export/build step
> (`APT-2026-0055`), and the `backcolor` no-op (`APT-2026-0044`, with a follow-up scoping item
> `APT-2026-0053`). None had shipped as of this writing. If any land, re-check this table against
> the shipped tool surface before the next skills-bundle release — do not assume the row is still
> accurate just because this skill wasn't touched.

---

## Phase 0 — Protect the baseline before you touch anything

Skipping this is the single most expensive mistake available, because one step in Phase 3 is irreversible in a way that leaves no error and no visible symptom.

| # | Task |
|---|---|
| 0.1 | Confirm the current technology is imported **and enabled** in the target repository |
| 0.2 | Re-export the current profiles and diff them against the deployed file; account for every delta |
| 0.3 | Rebuild a current-version-equivalent MDG from the source |
| 0.4 | Archive every artifact — profile XMLs, `.mts`, MDG — into a `Files` package |
| 0.5 | Baseline the source packages |
| 0.6 | Rename the baseline package roots unmistakably, e.g. `[3.0.14 BASELINE - DO NOT EDIT]` |

⚠ **0.4 gates Phase 3.** Tagged Value Types live in `t_propertytypes`, which is **repository-wide**. The moment a new-version type is added, any export from the old profile packages stops being the old version — silently, with no error and no visible change in the Browser. Archive first or the baseline is unrecoverable.

⚠ **0.1 must be done in the UI.** Untick "Hide disabled Technologies" in Manage Technology. Present-but-disabled is indistinguishable from absent through the API, and `get_mdg_from_runtime` is not a reliable probe (see Gotchas).

⚠ **0.6 matters more than it looks.** A duplicated profile package has the same name as its source — both trees show a child called `WBA`. Renaming the baseline root is the cheapest protection for the remaining phases, and unlike locking it blocks nobody.

**Verifying baseline scope.** A package baseline covers the whole subtree. Confirm it rather than assume: a package holding no elements directly still produces a large compressed payload if its children are captured.

```sql
SELECT DocID, DocName, LENGTH(BinContent) AS bytes
FROM t_document WHERE DocType = 'Baseline'
```

> **Use `LENGTH`, never `OCTET_LENGTH`.** A `.qea` repository is SQLite, which has no
> `OCTET_LENGTH` function. EA answers an unrunnable query with a **modal dialog**, which blocks
> the calling tool until someone clicks OK at the machine — it does not return an error you can
> catch. `LENGTH(...)` returns the byte count of a BLOB and is the correct form.

---

## Phase 1 — Package structure

```
Model
├── <Tech> design metamodel V<n>     ArchiMate view, human-readable
└── <Tech> profile V<n>
    ├── <Tech>  «profile»            stereotypes, metaclasses, constraints
    ├── <Tech>  «diagram profile»    custom diagram types
    └── <Tech>  «toolbox profile»    toolbox pages, one diagram per toolbox
```

Duplicate with **Paste as New, generating new GUIDs**. There is no reliable API route — XMI export/import does not dependably strip GUIDs, and two packages claiming the same profile `id` is a worse problem than a manual copy.

**Verify the copy immediately** — element counts, attribute counts, connector counts and diagram populations against the source, and confirm no cross-package leakage back into the original's metaclasses.

Record the new package GUIDs and the toolbox **diagram** GUIDs. The profile `id` values in the built MDG are derived from them, and that is how you later prove a file was built from the right source.

---

## Phase 2 — Profile mechanics

Read from working stereotypes so new work matches. Every one of these is a modelling convention, not an EA feature you can look up.

| Aspect | Mechanism |
|---|---|
| Stereotype | Class with stereotype `«stereotype»`, in the `«profile»` package |
| Display name | Attribute `_metatype`, `Default` = friendly name |
| Enforcement | Attribute `_strictness`, `Default` = `profile` |
| Tagged value | Attribute. `Type` blank for enums — the type comes from reference data of the same name — or a primitive (`int`, `Date`) |
| ArchiMate base | **Generalization**, unstereotyped, to the `«Metaclass»` element |
| UML base | **Extension** connector to the plain `«Metaclass»` element |
| Quick Linker rule | **Dependency** stereotyped `stereotyped relationship`, with a **connector tagged value** `stereotype = <Tech>::<Relationship>` |

⚠ **A stereotype with no Extension never exports.** It will sit in the profile package looking complete — tags, `_metatype`, even constraints — and appear in no MDG. If a stereotype is missing from a built file, check its Extension first.

⚠ **Namespace-qualify every constraint value.** `WBA::WBABusinessApplication`, never `WBABusinessApplication`. Unqualified constraints do not resolve and fail silently. Where `_strictness = profile` is set, enforcement is live against a rule that cannot resolve — the worst combination.

⚠ **Connector tagged values have no API route.** `ea_model` has no operation for them and `update_connector` silently ignores one passed as a property. Set them through the UI: Inspector ▸ Relationships ▸ double-click the row ▸ Tags tab. Budget for this — it is the main manual cost of the profile phase. (Tracked as `APT-2026-0052`; if it ships, this becomes API-scriptable and this gotcha should be trimmed.)

**Telling identical connectors apart.** Two reflexive connectors on the same element are indistinguishable in EA's Relationships grid, which shows no name and no stereotype column. Set a temporary name on the new one, do the work, then clear it — and verify the clear.

---

## Phase 3 — Reference data

⚠ **Do not start until Phase 0.4 is archived.**

Tagged value types live in `t_propertytypes` and are repository-wide, not per-profile.

**Check what already exists before authoring anything.**

```sql
SELECT Property, Notes FROM t_propertytypes ORDER BY Property
```

A type is defined if `Notes` carries `Type=Enum;Values=...;` or `Type=Date;` etc. Types frequently already exist and have simply never been **selected into a build** — see Phase 5. A tag behaving as free text does not prove the type is missing.

Where a profile carries Enumeration classes on a data-types diagram, those value lists are usually accurate and complete. Transferring them into reference data is a transfer, not a harvesting exercise.

**Check defaults against real values in use.** A default absent from its own value list means the dropdown cannot round-trip data the repository already holds:

```sql
SELECT [Value], COUNT(*) FROM t_objectproperties WHERE Property = '<tag>' GROUP BY [Value]
```

`Value` is a reserved-word column on `t_objectproperties` — bracket it, or the query is rejected. (See the `ea-modeling` SQL reference for the full reserved-word list.)

⚠ **Renaming a tag orphans its values** in `t_objectproperties`. Fix trailing spaces and spelling before a production load, never after.

---

## Phase 4 — Toolbox and diagram profiles

Toolbox pages are **elements on the toolbox diagram**. Each page's entries are **attributes** on the page element:

| Attribute field | Meaning |
|---|---|
| `Name` | `<Tech>::<Stereotype>(UML::<Metaclass>)` |
| `Default` | The label shown in the toolbox |
| `Type` | Leave blank — a populated `Type` is a defect |

So toolbox work is `create_attribute` / `update_attribute` / `delete_attribute` against the page element. Fully API-scriptable.

**Deleting a stereotype leaves its toolbox entry behind.** Removing a stereotype from the profile does not touch the toolbox, and a dangling entry points at nothing. Sweep the toolbox after every stereotype removal.

**A stereotype on no toolbox page ships invisible.** It exists, it validates, and no user can place it.

---

## Phase 5 — Build

All UI. The sequence matters and several steps are easy to get subtly wrong. (Tracked for API scripting as `APT-2026-0055`; not yet available.)

1. **Export each profile** — `Specialize ▸ Publish Technology ▸ Publish Package as UML Profile`.
   - The UML profile exports from the `«profile»` package.
   - The diagram profile exports from the `«diagram profile»` package.
   - **Each toolbox exports from its diagram**, via `Publish Diagram as UML Profile`.
2. **Build the MDG** — `Specialize ▸ Publish Technology ▸ Generate MDG Technology`.

⚠ **Version is typed into the export dialog, not stored on the package.** Profile packages commonly carry `Version 1.0` while exporting as 3.0.14. A version stamp that lags across releases is a symptom of the dialog being left at its remembered value, not of a package field.

⚠ **`Publish Diagram as UML Profile` is greyed out unless the diagram is open.** Selecting it in the Browser is not enough.

⚠ **The wizard's Tagged Value Types page is a selection step, not an inclusion step.** Types not selected here do not ship, however completely they are defined. This is the usual cause of "the type exists but the field is still free text" — and because the omission is invisible in the model, it can persist across many releases. This step still has no API route, so the wizard itself can't be scripted around — but the omission can now be *detected*: `ea-validation`'s `tagged_value_type_shipped` rule condition compares a profile's blank-`Type` tagged-value attributes against a built MDG file's RefData and flags anything defined but not shipped (`APT-2026-0057`, shipped). Run it as part of Phase 6 verification.

⚠ **Match the Contents checkboxes to the shape of the current deployed file** rather than guessing. Parse the deployed file and tick to match:

```
<MDG.Technology>
  <Documentation/>      → (header fields)
  <UMLProfiles>         → Profiles
  <TaggedValueTypes>    → Tagged Value Types
  <DiagramProfile>      → Diagram Types
  <UIToolboxes>         → Toolboxes
```

**Filenames.** Use stable unversioned names in the build folder — the `.mts` references the profile XMLs **by filename**, so versioned names force a rename and an `.mts` rebuild every release, and a stale `.mts` silently ships the previous version's content. Add the version only when archiving.

---

## Phase 6 — Verify

Verification is API work and should be mechanical. Parse the built XML and compare against the source.

**The check that catches the expensive mistake:** the four profile `id` values must match the V<n> package and diagram GUIDs recorded in Phase 1, not the previous version's. A correctly-versioned file built from the wrong package source passes every other check.

The `id` is a 10-character slice of the GUID:

```
Package GUID {8D977401-A156-34A8-9198-C05706C802DE}
Profile id                          C05706C802
```

**A full structural diff is worth automating.** Load both files, build `{stereotype: {base, generalizes, bgcolor, tags, constraints}}` and compare. Anything other than the deltas you intended is a finding.

Checklist:

- [ ] Profile `id` values match the current source packages
- [ ] Every new stereotype has both `generalizes` and `baseStereotypes` populated
- [ ] Every constraint value is namespace-qualified
- [ ] Widened constraints list all targets, semicolon-separated
- [ ] Removed stereotypes absent — and similarly-named ones still present
- [ ] New tagged value types present on their stereotypes **and** in `RefData`
- [ ] All profiles stamped with the new version

⚠ **Match on exact strings, never prefixes.** Profiles routinely contain near-identical names (`AI Technology` vs `AI Type`) whose blast radius differs by an order of magnitude.

---

## Phase 7 — Deploy

An MDG is deployed either **into the repository** (a model technology, picked up by everyone connecting to it) or **as a file registered on a workstation** (a runtime technology, seen only by that machine). They look identical in Manage Technology apart from the `Location` field. See `ea-mdg-deploy`'s Two Deployment Modes table for the deployment-mode mechanics; this phase is about the specific traps that show up once a *model-driven* build is what's landing on top of them.

| Location | Scope |
|---|---|
| `Model` | Every user of that repository |
| A file path | That workstation only |

⚠ **EA auto-registers any MDG file found on its search path.** The path list is at `Manage Technology ▸ Advanced`, and it routinely includes a user's `Downloads` folder. A build written there registers itself silently, shadows the model copy, and makes deployment appear to succeed on the author's desktop while nothing changes for anyone else. The search path is **not** recursive — a subfolder is safe.

**Before validating any deployment**, check Manage Technology with "Hide disabled Technologies" unticked and confirm one entry, at `Location: Model`, at the expected version. More than one entry for the same technology means something is shadowing something else.

Then: import, confirm **enabled** rather than merely present, and validate on a scratch diagram — toolbox page, Quick Linker, tag dropdowns — before any content is touched.

---

## Gotchas

| Symptom | Cause |
|---|---|
| Stereotype missing from the built MDG | No Extension to a metaclass |
| Tag ships as free text despite a complete definition | Not selected on the wizard's Tagged Value Types page — run `ea-validation`'s `tagged_value_type_shipped` rule to detect this (`APT-2026-0057`, shipped) |
| Quick Linker rule never fires | Constraint value not namespace-qualified |
| Toolbox entry points at nothing | Stereotype deleted, toolbox not swept |
| New stereotype invisible to users | On no toolbox page |
| `update_element` returns `ok: true` and nothing changed | `backcolor` is silently ignored — set appearance in the UI (`APT-2026-0044`/`APT-2026-0053`, not yet fixed) |
| Connector tagged value not applied | No API route — `update_connector` ignores it silently (`APT-2026-0052`, not yet fixed) |
| `get_mdg_from_runtime` says `unknown_mdg` | Unreliable probe. Confirm in the UI (`APT-2026-0046`, not yet fixed) |
| `get_embedded_mdgs` returns empty | EA 17 no longer records imported technologies in `t_document` (`APT-2026-0046`, not yet fixed) |
| Only the author sees the new version | File-based registration shadowing the model copy |
| Export produces the previous version's content | `.mts` still referencing old filenames |
| A query hangs and EA shows "SQL API Open FAILED" | The SQL used a function this backend lacks (e.g. `OCTET_LENGTH` on a `.qea`). Click OK on the dialog; use `LENGTH(...)` |

---

## Working rules

- **Ask before writing SQL** against a live repository, and never assume `execute_sql` is read-only — it accepts writes.
- **Never edit the baseline packages.** Protect them by renaming; lock only where you know who the lock applies to.
- **Do not fix things out of sequence.** A toolbox defect found during profile work is recorded, not corrected — nothing exports until the build phase, and out-of-sequence edits are how verification stops being meaningful.
- **Measure against the repository, not against the plan.** Counts in planning documents go stale, and a sandbox is not production.
