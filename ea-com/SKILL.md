---
name: ea-com
description: Use the Sparx EA COM API from Python to read and modify EA models — connect to a running instance, run SQL queries, manage MDG technologies, create/update elements, and control EA lifecycle. Use when automating EA work from a Python script.
---

# Sparx EA COM API — Python Automation

*Verified against EA 17.0 Build 1704.*

## Module

All EA automation uses `ea_com.py`:

```
C:\SparxServices\westbrook-build\wba-mdg\ea_com.py
```

```python
from ea_com import EA, EAError
```

EA must be running with a project open before connecting.

---

## Connecting

```python
# Context manager — releases COM refs on exit, does NOT close EA
with EA() as ea:
    print(ea.project_path)

# Manual — use when you need the instance to outlive a block
ea = EA()
ea.connect()                        # default: 3 retries, 2s delay
ea.connect(retries=10, delay=3.0)   # for post-restart reconnect
```

Under the hood: `win32com.client.GetActiveObject("EA.App")` — attaches to the currently running EA instance. Fails if EA is not running or no project is open.

---

## Key Properties and Methods

### Project info
```python
ea.project_path      # → "C:\...\WestbrookBank.qea"  (repo.ConnectionString)
ea.repo              # → raw Repository COM object (escape hatch for unlisted methods)
ea.app               # → raw App COM object
```

### SQL queries
```python
rows = ea.sql("SELECT Name, Object_Type FROM t_object WHERE Object_Type = 'Class'")
# Returns: list of dicts, e.g. [{"Name": "MyApp", "Object_Type": "Class"}, ...]

ea.execute("UPDATE t_object SET Status = 'Approved' WHERE ea_guid = '{...}'")
# Returns: bool
```

EA returns SQL results as XML (`<EADATA><Dataset_0><Data><Row .../></Data>...`). The `sql()` helper parses that into a list of row dicts automatically.

**Useful tables:**
| Table | Contents |
|-------|----------|
| `t_object` | Elements (Class, Component, etc.) |
| `t_connector` | Relationships between elements |
| `t_diagram` | Diagrams |
| `t_package` | Packages |
| `t_attribute` | Attributes on elements |
| `t_operation` | Operations/methods on elements |
| `t_objectproperties` | Tagged values |
| `t_xref` | Cross-references (stereotypes, constraints) |

### Technology / MDG
```python
ea.is_technology_loaded("WBA")      # bool — is the MDG loaded?
ea.is_technology_enabled("WBA")     # bool — is it enabled for this project?
ea.technology_version("WBA")        # str — e.g. "1.0"
ea.activate_technology("WBA")       # bool — enable/toggle
ea.delete_technology("WBA")         # bool — marks for removal (takes effect after restart)
ea.repo.ImportTechnology(xml_str)   # bool — embed MDG XML into model (model-embedded deploy)
```

**Note:** `GetTechnologyList()` does NOT exist in EA 17.0. Use `IsTechnologyLoaded()` per tech ID.

### Element/package navigation
```python
elem = ea.get_element_by_guid("{GUID-HERE}")
pkg  = ea.get_package_by_guid("{GUID-HERE}")
ea.refresh()   # RefreshModelView(0) — refreshes the browser tree
```

### Lifecycle
```python
ea.save()           # SaveAllDiagrams()
ea.shutdown()       # ShutdownEA() — graceful close
ea2 = ea.close_and_reopen()   # save + shutdown + relaunch + reconnect, returns new EA instance
```

### Introspection (useful when exploring undocumented API)
```python
ea.repo_methods()   # list all public methods/properties on the Repository COM object
# Filter example:
tech_methods = [m for m in ea.repo_methods() if any(k in m for k in ("Tech", "MDG", "Import"))]
```

---

## Critical API Correction — GetElementsByQuery vs GetElementSet

**`Repository.GetElementsByQuery` does NOT run raw SQL.** Passing a SQL string to it silently returns an empty collection — no error, no warning.

```python
# WRONG — silently returns empty collection
elements = ea.repo.GetElementsByQuery(
    "SELECT Object_ID FROM t_object WHERE Stereotype = 'Application'", "")

# CORRECT — use GetElementSet with type parameter 2 (SQL against t_object)
elements = ea.repo.GetElementSet(
    "SELECT Object_ID FROM t_object WHERE Stereotype = 'Application'", 2)
```

`GetElementsByQuery(queryName, searchTerm)` runs a **named model search** — the first argument is the name of a saved Search, not a SQL string. It will silently return 0 results if that search name doesn't exist.

`GetElementSet(sql, type)` where `type=2` means "SQL query against `t_object`" — this is the correct call for bulk element retrieval by SQL.

---

## EA Restart Pattern

Required after deploying an MDG, calling `DeleteTechnology`, or any operation that needs a fresh session:

```python
from ea_com import EA
import subprocess, time

ea = EA()
ea.connect()
path = ea.project_path

ea.save()
time.sleep(0.5)
ea.shutdown()
time.sleep(8)   # wait for process to fully exit

subprocess.Popen([r"C:\Program Files\Sparx Systems\EA\EA.exe", path])
time.sleep(12)  # wait for EA to open and be ready for COM

new_ea = EA()
new_ea.connect(retries=10, delay=3.0)
```

Or use the convenience wrapper:
```python
new_ea = ea.close_and_reopen(wait=6.0)
```

---

## Post-Action UI Check (Model-Mutating COM Calls)

EA COM calls that modify the model can raise blocking modal dialogs. The COM thread hangs
until the dialog is dismissed. Always take a screenshot after any model-mutating call.

**Operations that require a post-call screenshot:**
- `repo.ImportTechnology()` — "Profile already exists. Overwrite?"
- `repo.Execute()` with DML — SQL error dialogs
- `repo.OpenFile()` / `repo.CloseFile()` — save-changes prompts
- MDG re-import after any profile change

**Pattern:**
```python
# 1. Execute the COM call
ok = repo.ImportTechnology(xml_str)

# 2. Immediately take a screenshot and wait for dialogs to appear
# (use computer use: take_screenshot(), wait 3s, take_screenshot() again)

# 3. Dismiss any dialog visible in the screenshot before proceeding

# 4. Verify the result
print(f"IsTechnologyLoaded: {repo.IsTechnologyLoaded('TVO')}")
```

---

## Running the Module Directly

`ea_com.py` has a built-in smoke test:

```bash
python ea_com.py            # check mode: print project path, WBA tech status, sample elements
python ea_com.py restart    # restart mode: save + restart EA + reconnect + print tech status
```

---

## COM Object Hierarchy

```
EA.App
└── Repository
    ├── Models[]             # root packages
    │   └── Packages[]
    │       ├── Elements[]
    │       │   ├── Attributes[]
    │       │   ├── Operations[]
    │       │   └── TaggedValues[]
    │       └── Diagrams[]
    ├── SQLQuery(sql)        # raw XML result
    ├── Execute(sql)         # non-SELECT
    ├── ImportTechnology(xml)
    ├── IsTechnologyLoaded(id)
    ├── IsTechnologyEnabled(id)
    ├── GetTechnologyVersion(id)
    ├── ActivateTechnology(id)
    ├── DeleteTechnology(id)
    ├── GetElementSet(sql, 2)     # ← correct bulk element retrieval
    ├── GetElementByGuid(guid)
    ├── GetPackageByGuid(guid)
    ├── RefreshModelView(0)
    ├── SaveAllDiagrams()
    └── ShutdownEA()
```

---

## Common Patterns

### Find all elements of a stereotype
```python
# Via SQL helper (recommended — returns parsed list of dicts)
rows = ea.sql("""
    SELECT o.ea_guid, o.Name, o.Stereotype
    FROM t_object o
    WHERE o.Stereotype = 'Application'
""")

# Via COM GetElementSet (returns EA.Collection for iteration)
elements = ea.repo.GetElementSet(
    "SELECT Object_ID FROM t_object WHERE Stereotype = 'Application'", 2)
for elem in elements:
    print(elem.Name, elem.Stereotype)
```

### Read tagged values for an element
```python
rows = ea.sql("""
    SELECT p.Property, p.Value
    FROM t_objectproperties p
    WHERE p.Object_ID = (
        SELECT Object_ID FROM t_object WHERE ea_guid = '{YOUR-GUID}'
    )
""")
```

### Set a tagged value via COM
```python
# Via the element's TaggedValues collection (preferred for live EA session)
for tag in element.TaggedValues:
    if tag.Name == "status":
        tag.Value = "Retiring"
        tag.Update()
```

### ⚠ `elem.Type` Setter — Silent Failure for ArchiMate Types

Setting `elem.Type` via the COM setter silently does nothing for elements stored as
ArchiMate base types (`BusinessActor`, `BusinessProcess`, `ApplicationComponent`, etc.):

```python
# WRONG — silently ignored for ArchiMate-typed elements
elem.Type = "Class"
elem.Update()
# elem.Type still reads "Class" via COM (cached), but t_object still has "BusinessActor"
```

The correct fix is `repo.Execute()` DML directly against the database:

```python
# CORRECT — directly updates the stored Object_Type
repo.Execute(
    "UPDATE t_object SET Object_Type='Class' "
    "WHERE Object_Type='BusinessActor' "
    "AND Stereotype IN ('Employee','Department')"
)
# Then close and reopen the project to flush EA's in-memory cache
```

### Set a tagged value via SQL (bulk update)
```python
ea.execute("""
    UPDATE t_objectproperties
    SET Value = 'RiskTeam'
    WHERE Object_ID = 42 AND Property = 'businessOwner'
""")
```

---

## SQLite Schema Notes (EA 17 — Verified)

### MDG stereotypes are NOT in t_stereotype

`t_stereotype` is populated only for model-level (non-MDG) stereotypes. For MDG-defined stereotypes, always query `t_object`:

```sql
-- CORRECT — MDG stereotypes
SELECT Object_ID, Name, Stereotype, Object_Type
FROM t_object
WHERE Stereotype IS NOT NULL AND Stereotype != '';

-- t_stereotype is empty for MDG-only models
-- SELECT COUNT(*) FROM t_stereotype → returns 0
```

### t_attribute column names

The attribute default value column is `Default` (not `Default_Value`):

```sql
-- CORRECT
SELECT a.Name, a.[Default], a.Type
FROM t_attribute a
WHERE a.Object_ID = <element_id>;

-- WRONG — column does not exist
-- SELECT a.Default_Value FROM t_attribute ...
```

`[Default]` requires bracket quoting because `DEFAULT` is a SQL reserved word in SQLite.

### Tagged values
```sql
SELECT tv.Object_ID, tv.Property, tv.Value
FROM t_objectproperties tv
WHERE tv.Object_ID = <element_id>;
```

---

## Dependencies

- `pywin32`: `pip install pywin32`
- EA must be running with a project open
- Works on Windows only (COM is Windows-only)

---

## EA Computer Use — Latency Guidelines

When combining COM calls with computer use (screenshots, clicks):

| Operation | Wait before screenshot |
|-----------|----------------------|
| Any COM call that triggers a dialog | 3–5 seconds |
| `repo.OpenFile()` / `repo.CloseFile()` | 8–15 seconds |
| `repo.ImportTechnology()` | 3–8 seconds |
| `repo.Execute()` DML | 1–3 seconds |

> **"(Not Responding)"** in the EA title bar is normal during file and import operations.
> Wait the full interval and screenshot again before treating it as a failure.
> Never retry a COM call without confirming the previous call actually failed.

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `Could not connect to EA` | EA not running, or no project open | Launch EA, open project, retry |
| `AttributeError: GetTechnologyList` | Method doesn't exist in EA 17 | Use `IsTechnologyLoaded(id)` per tech |
| `ImportTechnology` returns False | XML error or EA showed a dialog | Check EA for modal dialog; validate XML; check ID lengths ≤ 12 chars |
| `GetElementsByQuery` returns empty | Raw SQL passed — wrong method | Use `GetElementSet(sql, 2)` instead |
| COM call succeeds but change not visible | Needs EA restart or `refresh()` | Call `ea.refresh()` or restart EA |
| `pywintypes.com_error: -2147221246` | EA closed while COM ref was held | Reconnect: `ea.connect()` |
| SQL error on `t_attribute.Default_Value` | Column doesn't exist | Use `a.[Default]` (bracket-quoted) |
