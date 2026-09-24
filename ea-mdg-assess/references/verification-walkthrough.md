# Reproducing the assessment by hand

`assess_mdg_situation`'s `ad_hoc_stereotype_count` and `covered_element_pct` aren't opaque — they
fold down from `summarize_stereotype_usage`, one row per stereotype in use. This walkthrough
recomputes both numbers from that call's own output, captured in the same session against the
same Westbrook Bank repository, so you can repeat the same check on any repository where the
scenario number looks surprising.

## 1. Pull the raw usage table

```
ea_analyze(operation="summarize_stereotype_usage", params={})
```

Observed:

```
{
  "items": [
    {"stereotype": "WBABusinessApplication", "object_type": "Component", "element_count": 52},
    {"stereotype": "WBAVendorSystem",         "object_type": "Component", "element_count": 35},
    {"stereotype": "WBADataAsset",            "object_type": "Object",    "element_count": 12},
    {"stereotype": "EATool",                  "object_type": "Component", "element_count": 9},
    {"stereotype": "WBABusinessService",      "object_type": "Component", "element_count": 8},
    {"stereotype": "ExternalReference",       "object_type": "Artifact",  "element_count": 1},
    {"stereotype": "VendorApplication",       "object_type": "Component", "element_count": 1}
  ],
  "total_elements_with_stereotype": 118,
  "distinct_stereotypes": 7
}
```

## 2. Split covered vs. ad hoc

A stereotype counts as **covered** if it appears in a loaded language's known stereotype set —
which, per `assess_mdg_situation`'s own loaded-languages check, means the loaded WBA technology or
any Sparx-shipped language currently active. Everything else is **ad hoc**.

Against the `get_mdg_from_runtime` static table for `WBA` (see
[three-states.md](three-states.md)), which lists `WBABusinessApplication`, `WBAVendorSystem`,
`WBABusinessService`, `WBAAIService`, `WBAAIGateway`, `WBADataAsset`, and `TechNode`:

| Stereotype | Count | In the WBA static table? | Bucket |
|---|---|---|---|
| `WBABusinessApplication` | 52 | yes | covered |
| `WBAVendorSystem` | 35 | yes | covered |
| `WBADataAsset` | 12 | yes | covered |
| `EATool` | 9 | no | ad hoc |
| `WBABusinessService` | 8 | yes | covered |
| `ExternalReference` | 1 | no | ad hoc |
| `VendorApplication` | 1 | no | ad hoc |

```
covered = 52 + 35 + 12 + 8   = 107
ad hoc  = 9 + 1 + 1          = 11
total   = 118

covered_pct = round(107 / 118 * 100) = round(90.68) = 91
```

Both numbers match `assess_mdg_situation`'s output exactly: `ad_hoc_stereotype_count: 11`,
`covered_element_pct: 91`. That agreement is the point of the exercise — when it *doesn't* match
on a real repository, trust this recomputation over the single summary number, because you can
see which specific stereotypes drove it.

## 3. Read past the number

The recomputation surfaces something the scenario number alone doesn't: two of the three ad hoc
stereotypes look like near-duplicates of technology stereotypes that already exist —
`VendorApplication` (1 element) sits next to `WBAVendorSystem` (35 elements), and `EATool` (9
elements, `Component`) has no obvious WBA counterpart at all. That's two different problems with
two different fixes (fold a near-duplicate into the existing stereotype vs. decide whether a new
concept belongs in the technology), and `assess_mdg_situation`'s single `ad_hoc_stereotype_count:
11` can't distinguish them. Always pull the per-stereotype table before deciding what "extend the
MDG" should actually do.

## 4. When the numbers don't reconcile

If your recomputed `covered`/`ad hoc` split doesn't match the assessment's reported numbers,
suspect one of:

- **A language loaded between the two calls.** `assess_mdg_situation` and
  `summarize_stereotype_usage` each read current state independently; if someone loads or unloads
  a technology between them, the two calls answer for different moments.
- **A stereotype string with a namespace prefix on one side and not the other.** The assessment
  strips everything before `::` when matching (`WBA::WBABusinessApplication` and
  `WBABusinessApplication` count the same); if you're matching by eye against the static table,
  do the same normalization or a legitimately-covered stereotype will look ad hoc.
- **A Sparx-shipped language's stereotype set covering something you didn't expect.** The
  "covered" bucket includes every currently-loaded Sparx-shipped language, not just the client
  MDG — a plain ArchiMate or BPMN stereotype in use counts as covered even with no client
  technology involved at all.
