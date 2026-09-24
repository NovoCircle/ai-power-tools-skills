---
name: ea-stakeholder-reporting
description: Turn a Sparx EA model into an answer a non-modeller can act on -- portfolio roll-ups by tagged value, plain-language element summaries, and business-facing display terms. Use when someone asks "how many X are Y", "what's mission-critical", "what's in scope for [a regulation]", or wants a model fact stated in business language instead of stereotype/tag names, and especially before quoting any count drawn from a tagged value.
---

# Reporting to stakeholders from a Sparx EA model

*Tools: `ea_analyze(operation="get_element_business_view"|"summarize_tagged_value_usage"|"summarize_stereotype_usage", params={...})`,
`ea_repository(operation="aggregate_portfolio", params={...})`,
`ea_mdg(operation="resolve_display_term", params={...})` (AI Power Tools for EA, v2.1.0+)*

This skill is read-only. None of the calls below create, update, or delete anything, and
none require a write confirmation. If a task built on this skill ever needs a scratch
element to demonstrate something, use a package named exactly `_sl44_scratch` and delete
it when done -- but the workflows here don't need one.

Run the `ea-start-here` preflight first if you haven't already this session (is the server
alive, which model is open, which technologies are active). This skill assumes that part
is done.

## When to use

- A stakeholder asks a counting or grouping question: "how many applications are
  mission-critical", "what's being sunset this year", "what's in PCI scope".
- You need to hand someone a fact about one specific system without making them read
  stereotype names or tag keys.
- Before you present any number derived from a tagged value, full stop -- coverage checking
  belongs in front of every roll-up, not just the ones that look suspicious.

## The gap this closes

An architect has a model. A stakeholder wants an answer in their own language: "Business
Application", not `WBABusinessApplication`; "22 mission-critical apps", not a stereotype
query. The model has the data. The gap is translation, plus one thing translation alone
doesn't fix: **a roll-up is only as honest as the tagged value is complete**, and nothing
in the tool output warns you when it isn't. That warning is on you.

---

## Step 0: check coverage before you quote a number

This is the most valuable habit in this skill. A roll-up over a tag that is only set on
some elements of a type produces a confident, wrong number -- it doesn't fail, it doesn't
warn, it just answers with whatever fraction of the data happens to be populated.

Verified against the live Westbrook Bank model (all counts below are real, not
illustrative):

| Stereotype | Total elements | `criticality` | `lifecycle` | `businessOwner` | `technicalOwner` | `dataClassification` |
|---|---|---|---|---|---|---|
| `WBABusinessApplication` | 52 | 52/52 | 52/52 | 42/52 | 44/52 | 45/52 |
| `WBAVendorSystem` | 35 | 35/35 | 35/35 | 35/35 | 35/35 (see note) | 35/35 |
| `WBADataAsset` | 12 | 0/12 | 0/12 | 0/12 | 0/12 | 12/12 |
| `WBABusinessService` | 8 | 0/8 (real) | 8/8 | 0/8 (real) | 0/8 (real) | 0/8 (real) |

Three genuinely different coverage failures live in that table, and they look identical
if you don't check:

1. **`WBADataAsset` and `criticality`/`lifecycle`/`businessOwner`/`technicalOwner`.** The
   tag isn't set on a single one of the 12 elements. It doesn't show up at all in
   `summarize_tagged_value_usage(params={"stereotype": "WBADataAsset"})` -- there's no
   zero-count row, the tag name is simply absent from the output. A roll-up call
   (`aggregate_portfolio`) over this combination returns `"total_elements": 0, "groups": []`,
   which reads exactly like "no data assets exist" instead of "this type doesn't track
   criticality." See `references/coverage-data.md` for the full transcript.
2. **`WBABusinessService` and everything except `lifecycle`.** The tag *is* set on all 8
   elements -- but the value is an empty string on every one of them. A check that only
   asks "is the tag present" reports 100% coverage. The real, usable coverage is 0%.
3. **`WBABusinessApplication` and the ownership/classification tags.** Real elements, real
   gaps: `businessOwner` is missing on 10 of 52, `technicalOwner` on 8, `dataClassification`
   on 7, `regulatoryScope` on 10. `criticality` and `lifecycle` happen to be fully
   populated here. Nothing about the stereotype tells you which tags will be complete --
   you have to check each one.

**The check, every time, before the roll-up:**

```
ea_analyze(operation="summarize_stereotype_usage", params={})
```

gives you the true denominator per stereotype (the counts in the table's second column
came from here). Then:

```
ea_analyze(operation="summarize_tagged_value_usage", params={"stereotype": "WBABusinessApplication"})
```

gives you, per tag, a `count` and the `distinct_value_count` / `sample_values`. Read it as:
does `count` equal the denominator? Does the sample list include `""` as a value? If either
answer is concerning, don't present the roll-up as complete -- say what fraction it covers.

The `technicalOwner` note for `WBAVendorSystem`: coverage is structurally 35/35, but 8
real assignments to one team are split across two spellings --
`Infrastructure & Cloud Team` (6) and `Infrastructure &amp; Cloud Team` (2), an
HTML-entity-encoded ampersand that never got cleaned up on import. A `technicalOwner`
roll-up here reports two teams with 6 and 2 systems each, when the true answer is one team
with 8. Coverage counting misses this entirely -- it's a distinct-value problem, not a
blank-value problem. Full detail in `references/coverage-data.md`.

---

## Portfolio roll-ups: `aggregate_portfolio`

```
ea_repository(operation="aggregate_portfolio", params={
  "stereotype": "WBABusinessApplication",
  "group_by_tag": "criticality"
})
```

Real result against the live model, 52 elements:

| Criticality | Count |
|---|---|
| Business-Critical | 22 |
| Mission-Critical | 14 |
| Standard | 8 |
| Important | 8 |

That's a complete answer here because `criticality` has no coverage gap on this
stereotype (Step 0 confirmed it) -- say so, e.g. "22 of 52 business applications are
Business-Critical" rather than manufacturing false precision if a gap existed.

Useful, verified behavior of this operation:

- **`count_only: true`** drops the per-element `elements` list and returns just the
  group counts -- use it once you've confirmed the elements aren't needed, to keep the
  response small.
- **`package_id`** scopes the roll-up to one package's subtree. Against the Westbrook
  demo, the whole-repository count for `WBABusinessApplication` x `criticality` is 52;
  scoped to the "Westbrook Bank" root package it drops to 45 -- the other 7 live
  elsewhere in the repository (a scratch/test area, in this case). Scope explicitly
  when a stakeholder asked about one line of business, not the whole repository.
- **`group_by_tag` is case-insensitive** (`"Criticality"` and `"criticality"` return
  identical results) -- don't spend time getting the case exactly right.
- **A misspelled or non-existent `stereotype` returns the same shape as a real
  stereotype with zero coverage on that tag**: `{"total_elements": 0, "groups": []}`.
  There is no separate "stereotype not found" error. If a roll-up comes back empty,
  confirm the stereotype name against `summarize_stereotype_usage` before concluding
  anything about the data.
- A tag whose values are free-text and sometimes hold **multiple values in one string**
  (Westbrook's `regulatoryScope` does this -- `"GLBA, FFIEC"` is one value, not two) means
  the group-by buckets by exact string. "How many applications are in GLBA scope" is not
  just the `"GLBA"` bucket; it's every bucket containing `GLBA` as a substring. Getting this
  wrong silently undercounts. See `references/coverage-data.md` for the worked numbers.

---

## Business view: `get_element_business_view`

```
ea_analyze(operation="get_element_business_view", params={"element_id": 91})
```

This is the per-element version of the same translation: stereotype names and tag keys
become business labels, and connections come out in plain language too. Real result for
a well-populated `WBABusinessApplication`:

```json
{
  "name": "Westbrook Fraud Decision Engine",
  "type": "Business Application",
  "properties": [
    {"label": "Business Owner", "value": "Fraud Risk Management", "technical_name": "businessOwner"},
    {"label": "Criticality", "value": "Mission-Critical", "technical_name": "criticality"},
    {"label": "Data Classification", "value": "Confidential", "technical_name": "dataClassification"},
    {"label": "Lifecycle", "value": "Current", "technical_name": "lifecycle"},
    {"label": "Regulatory Scope", "value": "FFIEC", "technical_name": "regulatoryScope"},
    {"label": "Technical Owner", "value": "Risk Technology Team", "technical_name": "technicalOwner"}
  ],
  "connections": [
    {"direction": "uses", "label": "Uses", "target_name": "NICE Actimize Fraud Risk Management", "target_type": "Vendor System"}
  ]
}
```

That's a complete stakeholder-ready summary in one call -- both endpoints of the
connection are already given business names, and the connector itself carries no
stereotype (`Uses` is one of the unqualified connector labels the demo model actually
uses; see the canon reference, section 6 -- do not prefix it `WBA::`).

**What happens when a tag isn't set:** the property is left out of the list entirely,
not shown with an empty value. A `WBADataAsset` element (which, per Step 0, never carries
`criticality`, `lifecycle`, `businessOwner`, or `technicalOwner`) returns only two
properties:

```json
{
  "name": "Customer Master Data",
  "type": "Data Asset",
  "properties": [
    {"label": "Data Classification", "value": "Confidential", "technical_name": "dataClassification"},
    {"label": "Regulatory Scope", "value": "GLBA, FFIEC", "technical_name": "regulatoryScope"}
  ],
  "connections": []
}
```

Reading a short `properties` list, don't assume "not applicable" -- it may just mean
"never populated." When a stakeholder needs to know whether a field is missing versus
inapplicable, cross-check with Step 0's coverage numbers for that stereotype rather than
inferring it from one element's output.

---

## Display terms: `resolve_display_term`

Stereotype names resolve reliably:

```
ea_mdg(operation="resolve_display_term", params={"kind": "stereotype", "technical_name": "WBABusinessApplication", "mdg_id": "WBA"})
-> {"alias": "Business Application", "found": true}
```

`mdg_id` is optional for a stereotype lookup -- omitting it still resolved
`WBADataAsset` to `"Data Asset"` correctly in testing.

**Tag names do not resolve the same way**, at least against this model at this server
version:

```
ea_mdg(operation="resolve_display_term", params={"kind": "tag", "technical_name": "criticality", "mdg_id": "WBA"})
-> {"alias": "criticality", "found": false, "mdg_id": ""}
```

`found` is `false` for every base tag tried (`criticality`, and the rest behave the
same). The alias comes back as the raw technical name, unresolved. This traces to
`ea_mdg(operation="get_mdg_from_runtime", params={"tech_id": "WBA"})`: every stereotype
entry it returns has an empty `tagged_value_definitions` list, so there's nothing for a
tag-kind lookup to match against.

**This is not a blocker** -- `get_element_business_view` and `aggregate_portfolio` both
already produce correct business labels for tags (`"Business Owner"`, `"Regulatory
Scope"`, and so on) through their own internal formatting, verified in the examples
above. When you need a tag's display label:

- If you're already calling `get_element_business_view` or `aggregate_portfolio`, use the
  `label`/`alias` field they return -- don't make a separate `resolve_display_term` call
  for a tag, it won't find one.
- If you need a label with neither of those in hand, title-case the camelCase technical
  name yourself (`businessOwner` -> "Business Owner") rather than relying on
  `resolve_display_term` to do it.
- Reserve `resolve_display_term(kind="stereotype", ...)` for stereotype names -- that path
  works.

---

## Failure modes you will actually hit

- **Empty roll-up, ambiguous cause.** `{"total_elements": 0, "groups": []}` means either
  "this stereotype doesn't exist" or "this stereotype exists but never sets this tag."
  Confirm the stereotype name against `summarize_stereotype_usage` before reporting a
  zero to anyone.
- **Blank counts as a value.** An empty string is a legitimate bucket
  (`aggregate_portfolio` will show `{"value": "", "count": N}`), and it looks like real
  data if you don't notice it's blank. Always scan for a `""` group before reading the
  rest of the table.
- **"None" is not the same as blank.** Westbrook's `regulatoryScope` uses the literal
  value `"None"` (explicitly assessed, not in scope for anything) alongside blank
  (never assessed at all). Collapsing the two loses a real distinction -- "not
  applicable" and "not yet reviewed" are different stakeholder answers.
- **Encoding drift splits one real bucket into two.** `Infrastructure & Cloud Team` /
  `Infrastructure &amp; Cloud Team` is the concrete case here; treat any roll-up with a
  suspiciously large number of near-duplicate group values as a signal to check for this
  before reporting team-by-team counts.
- **Comma-joined multi-value tags undercount a substring roll-up.** See the
  `regulatoryScope` example above; a plain `group_by_tag` equality match will miss any
  element whose value combines the term you're looking for with another.
- **A missing property in `get_element_business_view` doesn't self-explain.** It's silent
  on whether the field is unset or not tracked for that stereotype. Cross-check against
  `summarize_tagged_value_usage` for that stereotype when it matters.
- **`resolve_display_term(kind="tag", ...)` will not find a Westbrook base tag.** Get the
  label from the business-view/roll-up output instead, as above.

Full worked numbers, including the complete per-stereotype coverage matrix and the
`regulatoryScope` multi-value breakdown, are in `references/coverage-data.md`.

---

## A note on latency

Every operation in this skill is a repository read through the MCP server, not a UI
action -- there's no dialog to wait out and no "(Not Responding)" state to watch for.
If a task built on top of this skill also drives the EA desktop UI directly (opening a
diagram to walk a stakeholder through it, for example), see
`../_shared/references/latency.md` for wait guidance before screenshotting; it doesn't
apply to the calls in this skill itself.
