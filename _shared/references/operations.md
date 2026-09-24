# EA MCP operations reference

**Generated — do not edit by hand.** Produced by `tools/gen-operations.py` from the
server's dispatch tables. Re-run it after any server change rather than editing here.

Server version: `2.2.0` · 113 operations across 6 meta-tools.

Every operation is called the same way:

```
<meta_tool>(operation="<name>", params={"arg": value, ...})
```

All arguments go inside `params`. Passing them as top-level keys is the single most
common call error and produces a format error, not a result.

If an operation is not in this list, it does not exist. Do not infer one from a pattern.

---

## `ea_model` — 49 operations

| Operation | What it does |
|---|---|
| `add_parameter` | Add a parameter to an operation. |
| `create_attribute` | Add an attribute to an element. |
| `create_connector` | Create a connector from client (source) to supplier (target). |
| `create_connectors_bulk` | Create multiple connectors in one call with idempotency built in. |
| `create_element` | Create a new element in the given package. |
| `create_element_in_language` | Create an element using a language-qualified type. |
| `create_elements_bulk` | Create multiple elements in one call with idempotency built in. |
| `create_external_reference_element` | Create a placeholder element representing an object in an external system, with the four standardized tagged values applied automatically. |
| `create_operation` | Add an operation to an element. |
| `create_package` | Create a new package under the given parent. |
| `delete_attribute` | Delete an attribute from its parent element. |
| `delete_connector` | Permanently delete a connector. |
| `delete_connector_tagged_value` | Delete a tagged value from a connector by name. |
| `delete_element` | Permanently delete an element. |
| `delete_operation` | Delete an operation from its parent element. |
| `delete_package` | Permanently delete a package and everything inside it (elements, diagrams, nested packages). |
| `delete_tagged_value` | Delete a tagged value from an element by name. |
| `duplicate_package` | Duplicate a package subtree with fresh GUIDs on every package, element, attribute, and operation it contains -- the API equivalent of EA's UI-only "Paste as New" action, which has no COM route (see the section comment above this function for what was checked). |
| `find_composite_diagram_mismatches` | Audit a package (optionally its whole subtree) for elements where the two halves of the composite-diagram mechanism disagree. |
| `find_elements_by_name` | Find elements by name. |
| `find_orphan_elements` | Find elements with no connectors (orphans). |
| `find_packages_by_name` | Find packages by name. |
| `get_connector` | Fetch a connector (relationship) by ID or GUID. |
| `get_connector_tags` | Return all tagged values on a connector across EA's tag stores. |
| `get_connectors_for_element_filtered` | SQL-based connector lookup with direction and type filtering. |
| `get_current_selection` | Return currently-selected elements in the current diagram. |
| `get_element` | Fetch an element by ID or GUID. |
| `get_element_tags` | Return all tagged values on an element across EA's three tag stores. |
| `get_package` | Fetch a package by ID or GUID. |
| `list_attributes` | List all attributes on an element. |
| `list_child_packages` | List immediate child packages of a given package. |
| `list_connector_tagged_values` | List all tagged values on a connector. |
| `list_connectors_for_element` | List all connectors attached to an element (both directions). |
| `list_elements_in_package` | List elements directly contained in a package. |
| `list_operations` | List all operations (methods) on an element, including their parameters. |
| `list_package_tree` | Recursively walk the package hierarchy under `root_package_id`. |
| `list_root_packages` | List all root-level packages (top-level models) in the repository. |
| `list_tagged_values` | List all tagged values on an element. |
| `move_element` | Move an element to a different package. |
| `select_element_in_browser` | Highlight an element in EA's Browser (project tree). |
| `set_composite_diagram` | Set or clear an element's composite (navigation/drill-down) diagram link, writing both halves of the mechanism together so they can never land out of sync (APT-2026-0059). |
| `set_connector_tagged_value` | Create or update a tagged value on a connector. |
| `set_tagged_value` | Create or update a tagged value on an element. |
| `traverse_element_subgraph` | Return a compact subgraph N hops out from element_id. |
| `update_attribute` | Update an attribute by its GUID. |
| `update_connector` | Update properties on a connector. |
| `update_element` | Update properties on an element. |
| `update_operation` | Update an operation by GUID. |
| `update_package` | Update properties on an existing package. |

---

## `ea_diagram` — 21 operations

| Operation | What it does |
|---|---|
| `add_connectors_to_diagram_bulk` | Add connectors to a diagram's visual layer (t_diagramlinks). |
| `add_element_to_diagram` | Place an existing element on a diagram. |
| `add_elements_to_diagram_bulk` | Place multiple existing elements on a diagram in one call. |
| `create_diagram` | Create a new diagram in a package. |
| `create_diagram_in_language` | Create a diagram using a language-qualified diagram type. |
| `delete_diagram` | Permanently delete a diagram. |
| `export_diagram_image` | Export a diagram to an image file. |
| `export_diagram_to_visio` | Export a diagram to a Microsoft Visio (.vsdx) file. |
| `find_diagrams_by_name` | Find diagrams by name. |
| `get_current_diagram` | Return the diagram currently open/focused in the EA UI, or None. |
| `get_diagram` | Fetch a diagram with an inline PNG preview. |
| `get_diagram_png` | Render a diagram as PNG and return the bytes inline. |
| `get_diagram_svg` | Render a diagram as SVG and return the markup inline. |
| `layout_diagram` | Apply an auto-layout to a diagram using EA's Project.LayoutDiagramEx(). |
| `list_diagrams_in_package` | List diagrams in a package, optionally walking children. |
| `open_diagram` | Open a diagram in the EA UI (user-visible). |
| `reload_diagram` | Force a diagram to redraw (useful after bulk edits). |
| `remove_element_from_diagram` | Remove an element's placement from a diagram. |
| `set_diagram_object` | Reposition and/or restyle an element that is ALREADY placed on a diagram, without removing and re-adding it. |
| `set_diagram_objects_bulk` | Reposition and/or restyle multiple elements already placed on a diagram in one call. |
| `update_diagram` | Update a diagram's properties. |

---

## `ea_analyze` — 11 operations

| Operation | What it does |
|---|---|
| `describe_table` | Return canonical column names, types, PK, and gotcha notes for an EA repository table (``t_object``, ``t_taggedvalue``, etc.). |
| `execute_sql` | Execute a raw SQL query against the EA repository. |
| `get_element_business_view` | Return a complete, business-language view of an element. |
| `get_updates_in_range` | Return packages, elements, or diagrams created or modified in a date range. |
| `get_user_activity` | Per-user modification counts in a date range. |
| `list_ea_tables` | List every EA repository table known to the MCP server, with PK. |
| `summarize_connector_patterns` | Source-stereotype -> connector-stereotype -> target-stereotype tuples. |
| `summarize_observed_metaclasses` | For a given stereotype, which EA Object_Types host it. |
| `summarize_stereotype_usage` | Stereotype + Object_Type frequency table for the whole repository. |
| `summarize_tagged_value_usage` | Tagged value usage frequencies, optionally scoped to a stereotype. |
| `trace_connectors` | Return the connected subgraph N hops from ``element_id`` as compact nodes + edges. |

---

## `ea_mdg` — 11 operations

| Operation | What it does |
|---|---|
| `assess_mdg_situation` | Classify the MDG state of the connected repository. |
| `get_embedded_mdgs` | Read MDGs embedded in the current EA project file (from t_document). |
| `get_mdg_from_runtime` | Return the stereotype, tagged value and diagram type definitions of the technology EA actually has loaded -- or decline to answer. |
| `get_mdg_search_paths` | Return EA's configured MDG technology search-path directories (Manage Technology > Advanced tab). |
| `install_mdg` | Install an MDG file into the EA environment. |
| `list_available_modeling_languages` | Enumerate modeling languages available in the connected EA instance. |
| `list_registered_technologies` | Enumerate every technology EA's Manage Technology dialog would show -- name, version, location, and enabled state -- including disabled ones, so a build/deploy workflow can spot the exact failure mode a real customer report hit: a technology registered on the author's workstation silently shadowing (and drifting ahead of, or behind) the model's own copy, with no operation previously surfacing registration/ location/enabled state to make that visible. |
| `parse_mdg_xml` | Parse MDG XML (file path or raw string) into the intermediate format. |
| `resolve_display_term` | Translate a technical stereotype/tag name to its business alias. |
| `set_active_mdg` | Record a preferred MDG for the session. |
| `write_mdg_xml` | Emit valid MDG XML from a normalized intermediate metamodel dict. |

---

## `ea_validate` — 1 operations

| Operation | What it does |
|---|---|
| `audit` | Run a YAML sidecar conformance ruleset against the current model. |

---

## `ea_repository` — 20 operations

| Operation | What it does |
|---|---|
| `aggregate_portfolio` | Group elements by tagged value for portfolio reporting. |
| `apply_baseline` | Roll back a package to a prior baseline (destructive). |
| `check_for_updates` | Report whether a newer version of ea-mcp-server is available. |
| `close_project` | Close the currently-open project without exiting EA. |
| `compare_baseline` | Compare a package against one of its baselines and return the diff. |
| `create_baseline` | Create a baseline snapshot of a package. |
| `create_model` | Create a new EA model file at `path` and open it. |
| `export_xmi` | Export a package as XMI for cross-tool interchange. |
| `generate_report` | Run an EA-native report template against a package. |
| `get_repository_info` | Return metadata about the currently-open EA project: file path, connection string, EA version, number of root packages. |
| `get_skill_update_diff` | Return the local and remote content of a skill file that has a conflict. |
| `import_xmi` | Import XMI into a package. |
| `install_skills` | Install Claude skills from the public skills bundle into the host's skill directory. |
| `launch_ea` | Start Enterprise Architect on the local machine. |
| `list_available_skills` | List the Claude skills available for installation from the public skills bundle (``NovoCircle/ai-power-tools-skills``). |
| `list_baselines` | List baselines registered against a package. |
| `open_model` | Open an existing EA model file (.qea, .qeax, .eap, .eapx) in the running EA instance. |
| `open_project` | Open a .qea, .qeax, .eap, or .eapx project file. |
| `prune_legacy_skills` | Remove skill directories superseded by a rename or withdrawal. |
| `resolve_skill_conflict` | Resolve a conflict between a locally-edited skill file and the server version. |

