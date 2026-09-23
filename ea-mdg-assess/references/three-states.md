# Installed, embedded, and loaded — three different questions

Every one of these payloads was captured live against the Westbrook Bank demo repository
(`<model-dir>\WestbrookBank.qea`) on 2026-09-23, with EA already running and the model open.
Nothing here was constructed from the spec — where a call's answer looks incomplete or odd,
that's what it actually returned.

---

## `list_registered_technologies` — what EA's Manage Technology dialog would show

```
ea_mdg(operation="list_registered_technologies", params={})
```

Relevant rows out of 26 returned:

```
{ "name": "WBA", "version": "1.0",
  "location": "Workstation file (exact path not exposed by EA's COM API)",
  "enabled": true },
{ "name": "WestbrookBankArchitecture", "version": "",
  "location": "Workstation file (exact path not exposed by EA's COM API)",
  "enabled": false }
```

Two rows, same underlying organization, different identifiers, different `enabled` state. This is
not a bug — the response's own `completeness_note` says as much: the same technology can appear
under more than one registration at once. What it means in practice: asking "is Westbrook Bank's
technology registered?" doesn't have a single yes/no answer. Ask about a specific `name` string,
and read `enabled` for that row specifically. A technology disabled purely by an unticked box in
Manage Technology, with no separate embedded copy, cannot be told apart from "not registered at
all" through this call — see the `completeness_note` field for the exact limitation.

Every other row in the 26 was a Sparx-shipped language (ArchiMate2/3, BPMN family, TOGAF, UAF,
SysML variants, and so on), all `enabled: true`, all `location: "Sparx-installed"`. One
exception: `UML` was present with `enabled: false` and an empty `version` — a Sparx-shipped
language can be disabled too, not just custom ones.

---

## `get_embedded_mdgs` — what the model file itself carries

```
ea_mdg(operation="get_embedded_mdgs", params={})
```

```
{
  "embedded_mdgs": [],
  "count": 0,
  "ea17_note": "Empty result. In EA 17+, ImportTechnology() does not write to t_document. Verify via COM: repo.IsTechnologyLoaded('your_tech_id'), or check Specialize > Technologies > Manage Technology in the EA UI."
}
```

Zero results, on a repository that has WBA visibly loaded (elements stereotyped with it, and
`list_registered_technologies` confirms a workstation-file registration). The `ea17_note` explains
why: EA 17+ simply doesn't record technology imports in `t_document`, the table this call reads.
An empty result from this call is not evidence of anything. It answers "did EA 17 happen to write
a `t_document` row for this," which is a narrower and less useful question than "embedded mdgs"
implies. Don't use it to conclude a technology isn't embedded — use `list_registered_technologies`
or the EA UI's Manage Technology dialog instead, per the note.

---

## `get_mdg_from_runtime` — what looks like "loaded," and what it actually is

```
ea_mdg(operation="get_mdg_from_runtime", params={"tech_id": "WBA"})
```

Requires `tech_id` — calling it with `params={}` fails with `missing_required_params`. It answers
for one named technology, not the whole repository.

```
{
  "tech_id": "WBA",
  "stereotypes": [
    {"name": "WBABusinessApplication", "alias": "Business Application", "base_metaclass": "Component"},
    {"name": "WBAVendorSystem",        "alias": "Vendor System",        "base_metaclass": "Component"},
    {"name": "WBABusinessService",     "alias": "Business Service",     "base_metaclass": "Component"},
    {"name": "WBAAIService",           "alias": "AI Service",           "base_metaclass": "Component"},
    {"name": "WBAAIGateway",           "alias": "AI Gateway",           "base_metaclass": "Component"},
    {"name": "WBADataAsset",           "alias": "Data Asset",           "base_metaclass": "Object"},
    {"name": "TechNode",               "alias": "Technology Node",      "base_metaclass": "Node"}
  ],
  "diagram_types": [],
  "source": "static"
}
```

Two things to notice, both consequences of `"source": "static"`:

1. **Seven stereotypes, not the shipped technology's full fourteen**, no tagged values on any of
   them, and no diagram types — even though the shipped `WBA_MDG.xml` defines all three. This
   table is a hand-curated summary baked into the server for languages it already recognizes, not
   a parse of the actual MDG XML.
2. **`WBADataAsset`'s `base_metaclass` reads `Object`**, where the shipped technology's own spec
   defines it against `Class`. Also present: `TechNode`, which isn't a canonical WBA stereotype at
   all. Flag mismatches like this rather than silently treating either side as correct — see the
   "known defects" convention in `_shared/references/westbrook-example.md` §11. The point for this
   skill isn't which side is right; it's that this call cannot tell you, because it isn't reading
   the deployed technology at all for a `tech_id` it already has a static entry for.

The fallback path — the one that genuinely checks EA — only runs for a `tech_id` **not** in the
server's static/cached tables. There, the server calls `repo.IsTechnologyLoaded(tech_id)` directly
and returns one of:

- `{"error": "cannot_determine", ...}` — the probe itself failed; treat as unknown, not absent
- `{"error": "mdg_loaded_no_definition", "loaded": true, ...}` — confirmed loaded, but the server
  has no parsed stereotype/diagram-type table for it; run `parse_mdg_xml` on its XML to populate
  one
- `{"error": "unknown_mdg", "loaded": false, ...}` — a verified negative for that exact id string,
  not a guess. EA 17's COM surface can't enumerate custom technology ids, so this only confirms
  the one string you passed; the real registration may exist under a different id

So: for a technology this server has never heard of, `get_mdg_from_runtime` is a real, live
"loaded" probe. For `WBA`, `ArchiMate3`, and the other names it recognizes, it is not — it is a
reference table that can be stale in exactly the ways shown above. Knowing which of the two
behaviors you're getting requires knowing whether the id is in the server's static table, which
isn't visible from the call itself. When in doubt, don't rely on this call alone for a "is it
really loaded" answer on a known id — check the EA UI's Manage Technology dialog directly, or the
`enabled` field from `list_registered_technologies`.
