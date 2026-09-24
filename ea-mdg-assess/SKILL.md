---
name: ea-mdg-assess
description: Work out what modeling-language situation a Sparx EA repository is actually in — ad hoc stereotypes vs. a client-built MDG, and whether a technology is installed, embedded, or actually loaded — before picking ea-mdg-author or ea-mdg-model-build. Use at the start of any MDG task, when a stereotype behaves inconsistently, or whenever assess_mdg_situation's recommendation needs a second opinion.
---

# Assessing an MDG situation

`ea_mdg(operation="assess_mdg_situation", params={})` classifies the modeling-language state
of the connected repository so the next step is picked on evidence, not assumption. This skill
covers that call, the three supporting reads that let you check its answer, and what to do when
the answer and the model disagree.

Run this **before** `ea-mdg-author` or `ea-mdg-model-build`. Both of those skills assume you
already know which situation you're in; this is how you find out.

---

## 1. Run the assessment

```
ea_mdg(operation="assess_mdg_situation", params={})
```

No parameters. It reads the repository's stereotype usage and the currently-loaded languages,
and returns a scenario number, a plain-language description, and a `recommended_next_skill`.

Observed against the Westbrook Bank demo repository (`<model-dir>\WestbrookBank.qea`,
EA build 1716) on 2026-09-23:

```
{
  "scenario": 3,
  "description": "Client-built MDG exists but ad-hoc stereotypes are accumulating outside it.",
  "loaded_mdgs": ["WBA"],
  "ad_hoc_stereotype_count": 11,
  "covered_element_pct": 91,
  "recommended_next_skill": "ea-mdg-extend"
}
```

That last field is wrong. Read section 4 before you act on it.

## 2. What the scenarios mean

| # | Condition | Plain meaning | Do next |
|---|---|---|---|
| 1 | No client MDG loaded | Repository uses only Sparx-shipped languages (ArchiMate, BPMN, UML, ...), with or without informal stereotype conventions | `ea-mdg-model-build` if a profile model already exists in the repository to build from; otherwise `ea-mdg-author` to write one from scratch |
| 2 | Client MDG loaded, ad hoc usage under 5% of stereotyped elements | The technology is doing its job — the repository conforms | `ea-mdg-author` for further changes, or nothing at all |
| 3 | Client MDG loaded, ad hoc usage at or over 5% | The technology exists but people are stereotyping outside it — new concepts, duplicate ad hoc versions of existing ones, or drift | Extend the existing technology: `ea-mdg-author` if it's XML-authored, `ea-mdg-model-build` if it has a source model (check its profile package first — see `ea-start-here` §2) |

A fourth scenario, "external reference model needed," is named in the operation's own
documentation but was never observed to be returned in this session, on any input — the
underlying logic only ever produces 1, 2, or 3. Don't design a workflow around scenario 4 without
confirming the current server actually emits it.

The 5% threshold and the "ad hoc" label come from one thing: whether a stereotype in use matches
an entry in a loaded language's known stereotype set. Section 3 shows how to recompute that
yourself instead of trusting the number blindly.

## 3. Installed, embedded, and loaded are three different questions

This is the distinction `assess_mdg_situation` collapses into one scenario number, and unpacking
it is most of what "sanity-checking the assessment" means in practice. Full detail, including the
exact payload shape and *why* each call answers a narrower question than its name suggests, is in
[references/three-states.md](references/three-states.md). Short version, each observed live
against the Westbrook Bank repository:

| Question | Call | What it actually told us |
|---|---|---|
| Is a technology registered anywhere EA would show it in Manage Technology? | `list_registered_technologies` | `WBA` (enabled) **and** `WestbrookBankArchitecture` (disabled) both listed — two registrations of what a person would assume is "the same" technology |
| Does the model file itself carry a copy? | `get_embedded_mdgs` | Empty — `count: 0`, with a note that EA 17+ doesn't record this in `t_document` at all. Empty here proves nothing either way |
| Does EA have it loaded right now, for this session? | `get_mdg_from_runtime`, `params={"tech_id": "WBA"}` | Returned 7 stereotypes with `"source": "static"` — a hand-curated table baked into the server, **not** a live probe of what EA loaded. Reliable evidence of "loaded" only for a `tech_id` that *isn't* in that table, where the call falls back to a genuine `IsTechnologyLoaded()` COM check |

The trap: `get_mdg_from_runtime` sounds like it answers "loaded," and for an unfamiliar `tech_id`
it does. For `WBA` — already known to the server — it silently answers a different question
("what does our static definition say"), and that static definition itself only had 7 of the
canonical 14 stereotypes and no tagged values, which is a gap in the tool's own reference data,
not evidence the MDG XML is incomplete. Don't conclude anything about the *deployed* technology
from this call alone; cross-check against `parse_mdg_xml` on the actual `.xml` file (see
`ea-mdg-author`) if the static table's answer matters.

## 4. Sanity-check the assessment, don't just trust the number

`assess_mdg_situation`'s `ad_hoc_stereotype_count` and `covered_element_pct` are derived from
`summarize_stereotype_usage` under the hood. Recompute them from that call's own output rather
than treating the scenario number as ground truth — it takes one extra call and catches drift the
single number hides (for example: is the 91% covered by four stereotypes doing real work, or by
one stereotype used everywhere and three edge cases). The worked example, run against the same
repository in the same session and matching to the element, is in
[references/verification-walkthrough.md](references/verification-walkthrough.md).

## 5. When the recommendation is wrong — override it

**Observed live, 2026-09-23:** scenario 3 returned `"recommended_next_skill": "ea-mdg-extend"`.
There is no `ea-mdg-extend` directory in this repository. The server's own source (read directly,
not inferred) computes `"ea-mdg-author"` for scenario 3 — so the running server and its source are
out of sync, most likely a build that hasn't picked up a recent fix. Whatever the cause, treat the
field as unreliable until you've confirmed it names a real skill:

1. Read `description`, not just `recommended_next_skill` — it's plain language and doesn't drift
   the same way.
2. Match that description against `ea-start-here` §2's routing table yourself.
3. Confirm the target actually exists as a directory in this repository before telling anyone to
   go there. A recommendation naming a skill that isn't real is worse than no recommendation — it
   sends the next step into a dead end with apparent authority behind it.

Override it any time the scenario's plain-language `description` doesn't match what you already
know about the repository — for example, if you know a source model exists for the technology
but the assessment can't see that (it only looks at loaded languages and stereotype usage, not at
profile packages), pick `ea-mdg-model-build` over `ea-mdg-author` regardless of what came back.

## 6. Failure modes hit in this session

| Symptom | Cause | Fix |
|---|---|---|
| `get_mdg_from_runtime` returns `missing_required_params` | It requires `tech_id` — it does not assess the whole repository, only one named technology | Pass `params={"tech_id": "WBA"}` (or whatever `assess_mdg_situation`'s `loaded_mdgs` named) |
| `get_embedded_mdgs` returns `count: 0` on a repository with a technology clearly loaded | EA 17+ doesn't write technology imports to `t_document` | Don't treat this as "nothing embedded" — treat it as "this call can't see EA 17-style registrations," and check `list_registered_technologies` instead |
| `get_mdg_from_runtime` for a known `tech_id` looks authoritative but is missing stereotypes present in the shipped MDG | `"source": "static"` — a built-in table, not a live read | Cross-check against the actual `.xml` via `parse_mdg_xml` before concluding a stereotype is missing |
| Same technology name appears twice in `list_registered_technologies` with different `enabled` values | Two separate registrations (for example a workstation file copy under one id, and a differently-named entry under a display name) legitimately coexist | Not a bug — read `location` and `enabled` per row, don't assume one row speaks for the technology |
| `recommended_next_skill` names a skill directory that doesn't exist | Server/source drift — see section 5 | Never route on this field alone; confirm against `ea-start-here` and the actual directory listing |

---

## Reference files

| File | Covers |
|---|---|
| [references/three-states.md](references/three-states.md) | Full payloads for `list_registered_technologies`, `get_embedded_mdgs`, and `get_mdg_from_runtime` against the Westbrook Bank repository, and exactly which question each one does and doesn't answer |
| [references/verification-walkthrough.md](references/verification-walkthrough.md) | The `summarize_stereotype_usage` cross-check worked end to end against the same repository, reproducing `assess_mdg_situation`'s own numbers by hand |

This skill is read-only. If a task that follows it needs the EA desktop UI (deploying a fix via
`ea-mdg-author` or `ea-mdg-model-build`), see
[`../_shared/references/latency.md`](../_shared/references/latency.md) for wait guidance —
nothing here waits on the UI, so it isn't restated.

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
