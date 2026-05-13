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

---

## Deploy: Model-Embedded (Preferred)

Uses `Repository.ImportTechnology(xml_string)` via COM. This writes the MDG directly into the `.qea` SQLite database.

```python
import os
from ea_com import EA

MDG_FILE = r"C:\SparxServices\westbrook-build\wba-mdg\WBA_MDG.xml"
APPDATA_MDG = r"C:\Users\RyanSchmierer\AppData\Roaming\Sparx Systems\EA\MDGTechnologies\WBA_MDG.xml"

# Remove any application-level copy first to prevent duplicates
if os.path.exists(APPDATA_MDG):
    os.remove(APPDATA_MDG)
    print(f"Removed APPDATA copy: {APPDATA_MDG}")

# MDG XML must be windows-1252 encoded — read with the same encoding
with open(MDG_FILE, encoding="windows-1252") as f:
    xml = f.read()

with EA() as ea:
    result = ea.repo.ImportTechnology(xml)
    print(f"ImportTechnology() returned: {result}")
    # True = success, False = XML error (check for ID > 12 chars, malformed XML, etc.)

print("Done. Restart EA to verify.")
```

**What happens after ImportTechnology:**
- The technology is stored in the `t_propertytypes` or `t_stereotypes` tables in the `.qea` SQLite file
- EA must be restarted for the new/updated technology to take full effect
- `ImportTechnology` returns `False` if EA shows an error dialog — common causes:
  - `id=` attribute longer than 12 characters → shorten it
  - Malformed XML → validate with `xmllint` or Python's `xml.etree.ElementTree`
  - Namespace mismatch (stereotype references wrong tech ID)

---

## Deploy: Application-Level (APPDATA Install)

Only use this for machine-specific installs (e.g., a developer's local tooling MDG):

```python
import shutil, os

MDG_FILE = r"C:\SparxServices\westbrook-build\wba-mdg\WBA_MDG.xml"
APPDATA_MDG = os.path.join(
    os.environ["APPDATA"],
    "Sparx Systems", "EA", "MDGTechnologies", "WBA_MDG.xml"
)
os.makedirs(os.path.dirname(APPDATA_MDG), exist_ok=True)
shutil.copy2(MDG_FILE, APPDATA_MDG)
print(f"Installed to: {APPDATA_MDG}")
```

Verified APPDATA path on this machine: `C:\Users\RyanSchmierer\AppData\Roaming\Sparx Systems\EA\MDGTechnologies`

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

## Deploy: Import Package as MDG Technology (EA 17.1+ ONLY)

**Specialize > Publish Technology > Import Package as MDG Technology**

This path does **not exist in EA 17.0 Build 1704**. If you are running EA 17.0, use the MTS Wizard method instead.

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
- ✅ Your toolbox page(s) appear (e.g., "APM Elements", "APM Connectors")
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

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ImportTechnology()` returns `False` | ID > 12 chars, XML error, or dialog shown | Check EA for error dialog; validate XML; check all `id=` attrs ≤ 12 chars |
| Duplicate entry with `*` in Manage Technologies | Both APPDATA and model copies exist | Delete APPDATA copy, restart EA |
| Technology shows but toolbox is empty | `ToolboxPage name` doesn't match `toolbox` property value in DiagramProfile | Make them identical |
| Diagram type missing from New Diagram dialog | DiagramProfile not loaded or wrong `Apply type` | Verify DiagramProfile section uses `Apply type="Diagram_Logical"` (not `"Logical"`) |
| Tagged values don't appear | Stereotype name mismatch between Profile and Toolbox | Verify `APM::Application` format — prefix must match UMLProfile Documentation `id` |
| `DeleteTechnology()` returns True but entry persists | COM removes from registry but not memory | Restart EA — deletion takes effect after restart |
| MDG file rejected on load | File is UTF-8 encoded | Must be `windows-1252` — re-save with correct encoding |

---

## File Encoding (Critical)

MDG Technology XML files **must be encoded as `windows-1252`**. UTF-8 causes EA to silently reject the file.

When writing MDG XML from Python:
```python
with open("APM_MDG.xml", "w", encoding="windows-1252") as f:
    f.write(xml_content)
```

When reading MDG XML to pass to `ImportTechnology`:
```python
with open("APM_MDG.xml", encoding="windows-1252") as f:
    xml = f.read()
```

---

## Scripts

- `C:\SparxServices\westbrook-build\wba-mdg\install_wba_mdg.py` — application-level install (APPDATA)
- `C:\SparxServices\westbrook-build\wba-mdg\ea_com.py` — COM API module, run directly for a quick check:
  ```
  python ea_com.py          # check: loads, prints tech status
  python ea_com.py restart  # save + restart EA + reconnect + print tech status
  ```
