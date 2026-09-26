---
name: ea-diagram-advisor
description: Recommend which Enterprise Architect diagram type and viewpoint expresses what a user wants to understand — from their intent, the measured content of a scope, and the languages that content actually uses. Handles the hard case where a scope spans several modeling languages and no conformant view exists. Use when someone describes what they want to see rather than naming a diagram type, or before generating a diagram over content whose modeling languages you have not checked.
---

# Choosing the diagram, before drawing it

A user says what they want to **understand**. They should not have to know which of dozens of
diagram types across several modeling languages expresses it.

This skill turns that request into a recommendation with its reasoning attached. It does not draw
anything — hand the result to `ea-diagram-composition` once the choice is made.

**It recommends and explains; it never silently decides.** A user who asked for a specific diagram
type gets it, with a note when it fits badly. A recommender that quietly picks is indistinguishable
from one that is wrong.

---

## The rule that matters most

**Measure the content. Never guess it.**

Almost every bad diagram-type choice comes from assuming what is in a scope. The whole method here
is: profile what is actually there, attribute it to modeling languages, and let that decide whether
a conformant view even exists.

---

## Step 1 — measure the scope

Get the element set, then its stereotype histogram:

```
ea_analyze("traverse_element_subgraph", {...})      # the set, when scope is a subtree
ea_analyze("summarize_stereotype_usage", {...})     # the histogram
```

`summarize_stereotype_usage` gives stereotypes **as EA stores them** — prefixed or bare. That is
exactly what the next step needs; do not normalize them.

Also useful: `summarize_observed_metaclasses` for what base types are in play, and
`summarize_connector_patterns` for whether the content is a graph, a flow or a hierarchy — which
`ea-diagram-composition` needs later anyway.

**Ask for the concept vocabulary too**, from `get_mdg_from_runtime(tech_id=...)`, and pass it in.
Without it, attribution falls back to the concepts each binding happens to name — and a binding
names only what departs from its defaults, so the commonest concept in a language is often the one
it never lists. The advisor reports whatever it could not place rather than quietly absorbing it,
but it is better not to create the gap.

---

## Step 2 — profile, and ask the pivotal question

```python
import advise

profile = advise.profile_scope(histogram, bindings, known_concepts=vocabulary)
```

**Is this scope one modeling language, or several?** Everything downstream turns on it.

```python
profile.technologies        # {technology: element count}
profile.dominant            # the largest
profile.dominant_share      # how much of the scope it holds
profile.homogeneous         # dominant_share >= 90%
profile.is_bound            # is the dominant language one we have a binding for?
profile.unattributed_stereotypes
```

Three answers, not two, and they lead to different places:

| Profile | Meaning |
|---|---|
| homogeneous and bound | an ordinary, conformant view exists |
| mixed | **no conformant view exists** — see step 4 |
| dominant language unbound | most of this is a language with no binding here, usually a customer's own MDG. Not the same as mixed |

Look at `unattributed_stereotypes` before trusting anything. "I could not place 40% of this scope"
is the most useful thing to know, and it changes what the recommendation is worth.

---

## Step 3 — recommend

```python
for option in advise.recommend(profile, bindings, intent=what_the_user_said):
    print(option.kind, option.technology, option.viewpoint, option.diagram_type)
    for reason in option.reasons:
        print("  -", reason)
```

Ranked best first, on **coverage** (how much of the content the view admits), then **intent**, then
specificity — a narrower viewpoint says more about what a diagram is for.

**Show the reasoning.** It names the counts, the shares and the coverage arithmetic. A
recommendation whose justification could have been written without looking at the content is not a
measurement, and the user cannot tell the difference unless you show your working.

**Watch for `CLOSE CALL` in the reasons.** In a small scope many viewpoints admit everything
present, so coverage and intent tie and an arbitrary tiebreak picks the winner. When that happens,
say so and let the user choose on what the diagram is *for* — which the ranking cannot see.

---

## Step 4 — when no conformant view exists

A scope spanning several languages has no correct answer, and pretending otherwise is the damaging
case. Three options, in preference order:

1. **Dominant-language view.** Carries the majority; the rest appears as foreign content. Least
   surprising.
2. **Neutral custom view.** A base type with no profile, belonging to no language, so nothing on it
   is foreign. This is ordinary practice, not a workaround — a large share of real diagrams are
   plain base types.
3. **Split into linked conformant diagrams.** Every view stays valid; the cost is that no single
   picture shows the whole scope, which is usually the thing that was wanted.

### Two obligations, and they are not optional

**Say so.** Record on the diagram and in your response that the view is non-conformant and which
languages it spans. `option.non_conformance` is that sentence; put it somewhere the reader of the
diagram will see it, not only in the chat.

**Reconcile with validation.** `option.will_be_flagged` names the concepts a conformance check will
object to. Offer to scope those rules out or annotate them as accepted — **before** generating, so
the user decides rather than discovering a wall of findings afterwards.

```
ea_validate(... scoped to the new diagram ...)
```

Compare what comes back with `will_be_flagged`. A finding you did not predict means the profile
missed something; say so rather than quietly absorbing it.

---

## Judgment this skill cannot encode

**Coverage is not fitness.** A viewpoint that admits every concept in the scope may still be the
wrong argument to make about it. Coverage says a view *can* hold the content, never that it
*should*.

**The user's words are evidence, not instructions.** "Show me the application landscape" narrows
the choice; it does not settle it. Ask what decision the diagram supports if the ranking is close.

**A recommendation over unmeasured content is a guess with a footnote.** If the scope could not be
profiled, say the recommendation is weak and why.

**Adding a language is a data change, never a code change.** A view catalogue lives in a binding's
`viewpoints:` block. If advising on a new notation seems to need a change to `tools/advise.py`, the
knowledge is in the wrong place — a test enforces that no notation is named in the engine.

---

## Reference

- `tools/advise.py` — the ranking engine. Pure arithmetic, no repository calls, no notation names
- [`ea-diagram-composition`](../ea-diagram-composition/SKILL.md) — where the chosen view gets drawn;
  its `bindings/` are the view catalogues this skill ranks
