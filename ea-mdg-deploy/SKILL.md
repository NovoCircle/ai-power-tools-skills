---
name: ea-mdg-deploy
description: Deploy and test a Sparx EA MDG Technology — embed it into a .qea model file or install application-wide, then verify it works correctly. Use after authoring or modifying an MDG XML file.
---

# Deploying and Testing a Sparx EA MDG Technology

*Verified against EA 17.0 Build 1704.*

## Two Deployment Modes

| Mode | Location | Who gets it | When to use |
|------|----------|-------------|-------------|
| **Model-embedded** | Inside `.qea` project file | Anyone who opens the .qea | Preferred — travels with the model |
| **Application-level** | `%APPDATA%\Sparx Systems\EA\MDGTechnologies\` | This machine only | Legacy; requires install per user |

**Never have both at the same time for the same tech ID** — EA will show a duplicate entry with an asterisk (`*`) in Manage Technologies, and the asterisk entry cannot be removed via the UI.

### Model vs. runtime technologies — and the search-path auto-registration trap

The table above is about *where the file lives*. Separately, a technology can be **model-driven**
(built from profile packages inside a repository — see `ea-mdg-model-build`) or **direct-XML**
(hand-authored or generated once — this skill's usual case). Either kind can be deployed either
Model-embedded or Application-level; the two axes are independent.

⚠ **EA auto-registers any MDG file found on its search path**, regardless of deployment mode. The
path list is at `Manage Technology ▸ Advanced`, and it routinely includes a user's `Downloads`
folder. A build (or a stray copy) written there registers itself silently, shadows the intended
Model-embedded copy, and makes deployment look successful on the author's machine while nothing
changes for anyone else who opens the repository. The search path is **not** recursive — placing
files in a subfolder is safe. Before trusting any deployment, check Manage Technology with "Hide
disabled Technologies" unticked and confirm **exactly one** entry for the tech ID, at `Location:
Model` (or whichever location you intended) — more than one entry means something on the search
path is shadowing the copy you meant to test.

---

## Tool Selection for MDG Deployment

| Operation | Use |
|-----------|-----|
| Model-embedded install (preferred) | `ea_mdg(operation="install_mdg", params={"scope": "embedded"})` |
| Model-embedded install fallback | COM `repo.ImportTechnology(xml_str)` via `ea-com` |
| Application-level install | `ea_mdg(operation="install_mdg", params={"scope": "user"})` |
| Verify MDG loaded | COM `repo.IsTechnologyLoaded("WBA")` → True |
| Verify Location: Project | EA UI → Specialize → Technologies → Manage Technology |
| Dismiss overwrite dialog | Computer use → screenshot → click Yes → screenshot again |
| Fix wrong `Object_Type` in database | COM `repo.Execute()` DML (NOT `elem.Type` setter) |

---

## Deploy: Model-Embedded (Preferred)

Uses `Repository.ImportTechnology(xml_string)` via COM. This writes the MDG directly into the `.qea` SQLite database.

```python
import os
from ea_com import EA

# MDG_FILE: path to your own MDG XML file
MDG_FILE = r"<mdg-dir>\WBA_MDG.xml"
APPDATA_MDG = os.path.join(
    os.environ["APPDATA"],
    "Sparx Systems", "EA", "MDGTechnologies", "WBA_MDG.xml"
)

# Remove any application-level copy first to prevent duplicates
if os.path.exists(APPDATA_MDG):
    os.remove(APPDATA_MDG)
    print(f"Removed APPDATA copy: {APPDATA_MDG}")

# MDG XML must be UTF-8 encoded — read with the same encoding
with open(MDG_FILE, encoding="utf-8") as f:
    xml = f.read()

with EA() as ea:
    result = ea.repo.ImportTechnology(xml)
    print(f"ImportTechnology() returned: {result}")
    # True = success, False = XML error (check for ID > 12 chars, malformed XML, etc.)

print("Done. Restart EA to verify.")
```

**What happens after ImportTechnology:**
- The technology registers in **`t_trxtypes`** in the `.qea` file. Not `t_document`, and not `t_propertytypes` or `t_stereotypes` — an earlier version of this line named those two and they are wrong, which matters because a reader who checks them finds nothing and cannot tell a failed embed from a successful one. `SELECT Description, TRX FROM t_trxtypes` is the query
- EA must be restarted for the new/updated technology to take full effect
- `ImportTechnology` returns `False` if EA shows an error dialog — common causes:
  - `id=` attribute longer than 12 characters → shorten it
  - Malformed XML → validate with `xmllint` or Python's `xml.etree.ElementTree`
  - Namespace mismatch (stereotype references wrong tech ID)

### ⚠ Post-ImportTechnology — Always Screenshot

`repo.ImportTechnology()` can show a modal **"Profile already exists. Overwrite?"** dialog that
blocks the COM thread. This is true even when `SuppressEADialogs = True` is set, in some EA
builds.

Standard pattern after any `ImportTechnology` call (or any model-mutating COM call):

1. Execute the COM call
2. **Immediately take a screenshot** (do not wait — you need to see if a dialog appeared)
3. Wait 3–5 seconds (EA is slow to render dialogs)
4. Take a **second screenshot**
5. If a dialog is visible: read it, dismiss it appropriately, then confirm the result
6. Only then proceed to the next step

**Operations that ALWAYS require a post-call screenshot:**
- `repo.ImportTechnology()`
- `repo.OpenFile()` / `repo.CloseFile()`
- `repo.Execute()` with INSERT/UPDATE/DELETE
- Any MDG re-import after a profile change

Never assume a COM call succeeded without taking a post-call screenshot.

---

## Deploy: Application-Level (APPDATA Install)

Only use this for machine-specific installs (e.g., a developer's local tooling MDG):

```python
import shutil, os

# MDG_FILE: path to your own MDG XML file
MDG_FILE = r"<mdg-dir>\WBA_MDG.xml"
APPDATA_MDG = os.path.join(
    os.environ["APPDATA"],
    "Sparx Systems", "EA", "MDGTechnologies", "WBA_MDG.xml"
)
os.makedirs(os.path.dirname(APPDATA_MDG), exist_ok=True)
shutil.copy2(MDG_FILE, APPDATA_MDG)
print(f"Installed to: {APPDATA_MDG}")
```

Typical APPDATA path: `%APPDATA%\Sparx Systems\EA\MDGTechnologies`

Restart EA after install.

---

## Bringing EA to Foreground (Critical)

**Never call `open_application("Enterprise Architect")` to bring EA to focus.** This always launches a new EA instance, opening a second EA window with no model. Instead:
- Use `left_click` on the EA taskbar button to bring the existing instance to the foreground
- Or use `win32gui.SetForegroundWindow(hwnd)` in a Python script

---

## Deploy: Manual (EA 17.0 — APPDATA Drop)

1. Save MDG Technology XML to `%APPDATA%\Sparx Systems\EA\MDGTechnologies\<name>.xml`
2. In EA: **Specialize > Technologies > Manage MDG Technologies**
3. Close the dialog — EA reloads from the folder on each open
4. Restart EA to pick up changes

---

## Deploy: MTS Wizard (EA 17.0 production assembly)

1. Create an MTS file referencing the profile XMLs
2. **Publish > Technology > Publish > Generate MDG Technology File**  
   (also accessible as **Specialize > Publish Technology > Generate Technology File** depending on your ribbon configuration)
3. Wizard produces assembled MDG Technology XML

---

## Deploy: from a profile package (EA 17.1+ ONLY)

EA 17.1 added two commands on **Specialize > Publish Technology** that work directly from a
`«mdg technology»` package tree, with no `.mts` and no intermediate profile exports. **They are
not the same command and the names do not say which is which:**

| Command | What it does | Leaves behind |
|---|---|---|
| **Save Package as MDG Technology** | Assembles the technology and writes it to a file | an `.xml` on disk. Nothing is installed |
| **Import Package as MDG Technology** | Loads the technology into the **session runtime** | nothing on disk, nothing embedded |

**If you want a deployable artifact, use Save.** Import is for trying a technology out in the
current session.

### Procedure — Save Package as MDG Technology

1. Select the `«mdg technology»` package in the Browser.
2. **Specialize > Publish Technology > Save Package as MDG Technology**.
3. A Save As dialog appears (`XML Export File (*.xml)`). Choose the path.
4. EA reports `MDG Technology successfully saved to file`.
5. **Read System Output.** It carries diagnostics the dialog does not, such as
   `WARNING: Duplicate profile name: …`. A build can report success and still have collided.
6. **Version-stamp the file.** Generated technologies come out with an empty `version` attribute,
   and setting the package `Version` beforehand does not carry through. Two unversioned builds are
   indistinguishable in Manage Technologies.
7. Deploy the resulting `.xml` by either route above — model-embedded or application-level. This
   command does not install anything.

The technology id is the **package name truncated to 12 characters** (`WBA Technology` →
`WBA Technolo`), so name the package for the id you want before publishing.

### Import Package as MDG Technology — what it does and does not do

⚠ **It reports success without leaving evidence.** `Repository.ImportPackageAsMDGTechnology(<package GUID>)`
is present on `Repository` and returns `True` for a valid GUID. Measured against a populated
14-stereotype source model: it returned `True` and **changed nothing** — `t_trxtypes` stayed at its
previous row count and the embedded profile blob stayed byte-identical.

So do not take `True`, or the UI's `MDG Technology successfully loaded into current model`, as
proof of a deploy. If you use this command, verify with **`repo.IsTechnologyLoaded(<id>)`** — the
session-runtime question, which is what this command actually affects. Checking `t_trxtypes` is
the wrong test and will report failure on a command that worked as designed.

Whether it can be made to embed with `SuppressEADialogs = True` / `EnableUIUpdates = False`, the
way `install_mdg` pushes `ImportTechnology` past its confirmation dialog, is **untested**.

### Version gate

| EA version | Build the MDG with |
|---|---|
| **17.1+** | `Save Package as MDG Technology` — above |
| **17.0 and earlier** | The MTS Wizard. These commands do not exist; the menu entries are absent, not greyed out |

Verified absent on **EA 17.0 Build 1704**. Check the build before routing someone down either
path — `ea_repository(operation="get_repository_info", params={})` reports `ea_version`.

---

## Restart EA via COM

After any deploy, restart EA to clear the technology cache:

```python
from ea_com import EA
import subprocess, time

ea = EA()
ea.connect()
path = ea.project_path  # Save path before shutdown

ea.save()
time.sleep(0.5)
ea.shutdown()           # Calls repo.ShutdownEA()
time.sleep(8)           # Wait for process to fully exit

subprocess.Popen([r"C:\Program Files\Sparx Systems\EA\EA.exe", path])
time.sleep(12)          # Wait for EA to open and load project

new_ea = EA()
new_ea.connect(retries=10, delay=3.0)
```

Or use the convenience method:
```python
ea2 = ea.close_and_reopen()  # save + shutdown + relaunch + reconnect
```

---

## Verification Checklist

After deploying and restarting EA, verify each of these:

> **EA 17 note on `get_embedded_mdgs`:** The `get_embedded_mdgs` MCP tool queries `t_document`
> for embedded MDG XML. In EA 17, `ImportTechnology()` does not store the MDG in `t_document` —
> it uses a different internal location. `get_embedded_mdgs` will return empty even when the MDG
> is correctly embedded. Use COM verification (`IsTechnologyLoaded`) or the EA UI instead.

**Verification order (most reliable first):**
1. **COM:** `repo.IsTechnologyLoaded("WBA")` must return `True`
2. **EA UI:** Specialize → Technologies → Manage Technology → Location column shows **Project**
3. **MCP:** `ea_mdg(operation="get_embedded_mdgs", params={})` ← note: unreliable for model-embedded MDGs in EA 17

### 1. COM check (scripted)
```python
from ea_com import EA
with EA() as ea:
    tech = "WBA"
    print("Loaded :", ea.is_technology_loaded(tech))   # Should be True
    print("Enabled:", ea.is_technology_enabled(tech))  # Should be True
    print("Version:", ea.technology_version(tech))     # Should be "1.0"
```

### 2. Manage Technologies dialog
- Open: **Specialise → Technologies → Manage Technologies** (or **Settings → MDG Technologies**)
- Look for your technology entry
- ✅ `Location` column shows **Project** (not APPDATA)
- ✅ Only **one entry** — no asterisk (`*`) duplicate
- ✅ Version matches your `<Documentation version=">` value

### 3. Diagram types
- Right-click a package in the browser → **Add Diagram**
- Expand the diagram type dropdown
- ✅ Your custom diagram types appear (e.g., "APMPortfolioView")
- Create one and confirm the diagram `Type` property shows your custom type name

### 4. Toolbox
- With a custom diagram open, look at the Toolbox panel
- If auto-switching doesn't happen, click the filter icon (≡) and select your technology
- ✅ Your toolbox page(s) appear (e.g., "WBA ArchiMate Elements", "WBA UML Elements")
- ✅ All expected stereotypes are listed

### 5. Stereotype application + tagged values
- Drag an element from your toolbox page onto a diagram
- Select it and check the Properties panel (Element tab)
- ✅ `Stereotype` shows `TechName: StereotypeName`
- ✅ Tagged values appear in the Properties panel under the stereotype group name
- Double-click the element to open full properties dialog
- ✅ A tab named after your technology appears
- ✅ All tagged values are listed on that tab

### 6. Quick Linker
- To enable Quick Linker: **Preferences → Objects → Links → Quick Linker: Enable ✓**
- With a diagram open, hover over an element for 1-2 seconds to see the QL arrows
- Note: The QL hover overlay cannot be captured by automated screenshot tools — it disappears on focus change

---

## EA Computer Use — Latency Guidelines

Wait before screenshotting — the right interval depends on the operation (2–15 seconds), not a
flat delay — and never retry without confirming the previous action failed. Full wait-time table
and the standard action/wait/screenshot pattern:
[`../_shared/references/latency.md`](../_shared/references/latency.md). See also "Post-
ImportTechnology — Always Screenshot" above for this skill's specific screenshot-before-waiting
sequence around the overwrite-confirmation dialog.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ImportTechnology()` returns `False` | ID > 12 chars, XML error, or dialog shown | Check EA for error dialog; validate XML; check all `id=` attrs ≤ 12 chars |
| Duplicate entry with `*` in Manage Technologies | Both APPDATA and model copies exist | Delete APPDATA copy, restart EA |
| Technology shows but toolbox is empty | `ToolboxPage name` doesn't match `toolbox` property value in DiagramProfile | Make them identical |
| Diagram type missing from New Diagram dialog | DiagramProfile not loaded or wrong `Apply type` | Verify DiagramProfile section uses `Apply type="Diagram_Logical"` (not `"Logical"`) |
| Tagged values don't appear | Stereotype name mismatch between Profile and Toolbox | Verify `WBA::WBABusinessApplication` format — prefix must match UMLProfile Documentation `id` |
| `DeleteTechnology()` returns True but entry persists | COM removes from registry but not memory | Restart EA — deletion takes effect after restart |
| MDG file rejected on load | Encoding declaration mismatch | Declare `encoding="utf-8"` in the XML prolog and save the file as UTF-8 |

---

## File Encoding (Critical)

MDG Technology XML files must be encoded as UTF-8 and declare `encoding="utf-8"` in the XML
prolog — the declaration and the actual byte encoding must agree, or EA rejects the file
outright. Full guidance (legacy `windows-1252` handling, read/write code patterns):
[`../_shared/references/file-encoding.md`](../_shared/references/file-encoding.md).

---

## Scripts

These are not shipped files — build them yourself from the code already in this skill:

- **Application-level install script** — wrap the "Deploy: Application-Level" snippet above in a standalone `.py` file to do an APPDATA install (copy `MDG_FILE` to `APPDATA_MDG`) in one run.
- **COM API quick-check script** — using the `ea_com.EA` class (see the `ea-com` skill), write a small script with a CLI switch:
  ```
  python your_script.py          # check: connect, then print IsTechnologyLoaded/is_technology_enabled/technology_version
  python your_script.py restart  # save + restart EA + reconnect (see "Restart EA via COM" above), then print tech status
  ```

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
