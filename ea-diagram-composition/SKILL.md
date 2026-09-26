---
name: ea-diagram-composition
description: Compose Enterprise Architect diagrams that read as deliberate — choose a layout grammar, compute geometry, place and style elements and connectors, then verify and correct the result. Language-neutral; works with any modeling language, reading each notation's conventions from a data binding (ArchiMate 3 and BPMN 2.0 ship). Use when building a diagram from model content rather than hand-placing elements, or when a generated diagram looks untidy and you need to know why.
---

# Composing diagrams that read well

A diagram is not a picture of a model. It is an argument about the model, made visually, and it
works when a reader can follow that argument without being told how.

This skill is about the part a model cannot tell you: **where things go**. It is language-neutral
— nothing here knows what ArchiMate or BPMN is — and it is meant to be used alongside whatever
language guidance applies to the content.

## The loop is the product

```
choose a grammar → compute geometry → place and style → verify → lint → correct
     (judgment)        (compose.py)       (MCP)         (MCP)   (rules)  (loop)
```

**Never hand a diagram to someone without looking at it.** Generating geometry and trusting it is
how overlapping boxes and clipped labels ship. The verify step is cheap and it is the difference
between "I made a diagram" and "I made a diagram that works".

Bound the loop — three correction passes is plenty. If it is still wrong after three, the grammar
was the wrong choice, not the spacing. Say so rather than iterating forever, and say what you tried.

## Step 0 — find the language binding

Before choosing anything, ask whether the notation's conventions are already recorded. A **binding**
holds one technology's diagram types, sizing, spacing, title convention, routing and standard views
as data, so you are not guessing at what an ArchiMate or a BPMN diagram is supposed to look like.

```python
from bindings import find_binding

binding = find_binding("ArchiMate3")          # or "BPMN2.0"; None if nothing is bound
dt = binding.diagram_type("Application")      # this diagram type's conventions
```

For the diagram type you are building, it answers:

| Question | From |
|---|---|
| which grammar | `dt.grammar`, and `dt.grammar_is_implemented` before relying on it |
| what size, and how far apart | `dt.spec()`, ready for Step 2 |
| how connectors route | `dt.default_route()`, `dt.route_for(relationship)` |
| which visual channels are free | `dt.channel_is_free("fill")`, `dt.free_channels()` |
| whether to draw a title | `dt.draws_its_own_title` |
| which standard view fits the content | `binding.viewpoints_admitting([...])` |

> `find_binding` returns `None` for a technology nobody has bound. That is normal — say so and fall
> back to the judgment below. Composing against another notation's binding is worse than composing
> against none.

Two bindings ship: ArchiMate 3 and BPMN 2.0. [`references/bindings.md`](references/bindings.md) is
the schema and the loader API.

## Step 1 — choose a grammar

Analysis of 147 professionally-drawn diagrams found their variety resolves into **four**
compositional grammars, not 147 special cases. Picking the right one is most of the quality — and
when Step 0 found a binding, it has already been picked: the binding states the grammar for each of
its diagram types.

| Grammar | Use when the content is | Reads badly when |
|---|---|---|
| **layered-bands** | stratified — things sit *above* or *below* other things | there is no real hierarchy, and the bands are arbitrary |
| **lanes** | a flow with owners — who does what, in what order | the items do not actually sequence |
| **nested-grid** | containment — things live *inside* other things | nesting is deeper than about three levels |
| **computed-geometry** | quantitative — size or angle carries meaning | the numbers do not vary enough to see |

Three are implemented (`layered-bands`, `lanes`, `nested-grid`). See
[`references/grammars.md`](references/grammars.md) for what each one is for, in detail, and for
the EA coordinate convention.

**If none fits, say so and fall back to a plain graph layout.** A forced grammar reads worse than
an honest one. A capability model in swimlanes is not a swimlane diagram; it is a capability model
that has been made harder to read.

## Step 2 — compute the geometry

```python
from compose import compose_layered_bands, compose_lanes

result = compose_layered_bands([
    {"name": "Channels",     "items": [{"id": 13477}, {"id": 13478}]},
    {"name": "Applications", "items": [{"id": 13479}]},
], {"align": "center"})
```

Plain data in, plain data out. Item ids are preserved verbatim — pass EA element ids as the
integers they are. Every returned item carries `left`/`top`/`right`/`bottom` in **EA's**
convention, plus its container and index; every container carries its own rect and a label rect.

**EA's y axis is upside down relative to intuition.** `top` and `bottom` are *negative*, and
`top > bottom`, so **`height = top - bottom`**. Getting this backwards silently flips every
vertical decision. The engine handles it; you only need to care when reading geometry yourself.

`spec` carries sizing and spacing. An unknown `spec` key raises rather than being ignored, so a
typo cannot silently produce a default layout. Where there is a binding, get the spec from it —
`dt.spec({"align": "center"})` — rather than writing the numbers by hand; a binding's are measured
from real diagrams, and yours are not.

## Step 3 — place and style

Place with `ea_diagram("add_elements_to_diagram_bulk")`, passing explicit
`left`/`top`/`right`/`bottom` per element and **`layout="none"`**.

> Passing a named layout style discards every coordinate you just computed. `layout="auto"`
> keeps them *only* because you supplied coordinates. `"none"` says what you mean.

Then style, in this order:

1. **Elements** — `ea_diagram("set_diagram_object_appearance")`, or the bulk form for a palette.
   Colors are `"#RRGGBB"` or a name.
2. **Connectors** — `ea_diagram("add_connectors_to_diagram_bulk")` first, then
   `ea_diagram("set_diagram_link")` / `set_diagram_links_bulk` for routing, color and width.

**A connector needs a stored link row before it can be styled.** EA draws the relationship between
two placed elements whether or not a row exists, so a visible line is *not* evidence you can style
it. A link reported with `instance_id: 0` has nothing to write to; add it to the link layer first.

### Which appearance scope you mean

| You want | Use | Affects |
|---|---|---|
| this box, on this diagram | `ea_diagram("set_diagram_object_appearance")` | one placement |
| this element, everywhere | `ea_model("set_element_appearance")` | every diagram it appears on |

Reach for the first. The second is a model-wide default and changing it to fix one view will
surprise someone looking at another.

## Step 4 — verify

```
ea_diagram("verify_diagram", {"diagram_id": …})
```

One call: it reloads, renders, and returns the image **with** the full placed geometry — rects,
z-order, decoded connector routing and color, canvas extents.

**The reload is why this exists.** EA caches renders per diagram, so rendering after an
out-of-band write returns a stale image that looks completely plausible. `verify_diagram` reloads
unconditionally and has no flag to forget. Use it rather than `get_diagram_png` when the question
is "is this right".

For **"what color did EA actually draw"**, pass `include_svg` and read `stroke=` / `fill=` from
the markup. A color property read back tells you nothing — EA echoes whatever was written, so a
round-trip check confirms your own input and would pass against something that stored the value
and never drew with it.

## Step 5 — lint, then correct

```python
import lint

report = lint.lint_diagram(verified, profile=profile, roles=roles, rows=rows)
for finding in report.errors:
    print(finding.rule, finding.subjects, "->", finding.correction)
```

`tools/lint.py` reads a `verify_diagram` result and nothing else. **Pass `roles` and `rows`** —
which elements play the same role, which sit in one row. Those are composition facts you know and
geometry alone does not; the linter will not guess them, and the rules that need them simply do not
run without them.

**The loop is bounded: three passes, then report what is left.** `lint.is_stalled(previous, report)`
catches the other failure, a pass that changed nothing. Stop at the first stall.

Under a presentation profile, pass it so the linter does not report what the view deliberately
hides — `{**p.display_settings(), "collapses_parallel": p.collapses_parallel}`. A profile never
suppresses a structural defect; overlaps are wrong under every profile.

`report.clean` means **no errors**, not "nothing found", and it means "no defect this linter knows
how to measure" — not "this diagram reads well". See
[`references/verification.md`](references/verification.md) for the contract, the stale-render trap
and an explicit list of what the linter cannot see.

What it checks:

- **Overlaps** — two elements sharing space, where neither contains the other. Always wrong.
- **Clipping** — an element too small for its label.
- **Out of canvas** — placement beyond `cx`/`cy`; it renders but exports cut off.
- **Uneven pitch** — gaps between neighbors in a row that should be even.
- **Inconsistent sizing** — elements in the same role at different sizes. This is the one people
  skip and it is the one that most makes a diagram look machine-made.
- **Avoidable crossings** — connectors crossing where reordering would fix it.
- **Unrouted connectors** — no explicit route, so the diagram depends on EA's default.

Then two that are about honesty rather than tidiness:

- **Color encoding without a legend.** If fill carries meaning, the reader needs the key.
  Color a reader cannot decode is a diagram that misleads.
- **A missing title** where the convention calls for a drawn one. Many diagrams correctly use
  EA's frame header instead — check which applies before adding one.

## Judgment that scripts cannot encode

**Each notation already claims some visual channels.** ArchiMate's layer colors are spoken for;
recoloring them by lifecycle destroys the notation while looking like a feature. Before using a
channel, ask what it already means. If fill is taken, reach for border, opacity, or an icon. A
binding mechanizes the question: `dt.claimed_channels()` says what the notation has spoken for and
`dt.free_channels()` what is left, so the answer is recorded rather than recalled.

**One variable per channel.** Fill = lifecycle, *or* fill = ownership. Never both.

**Uniform sizing within a role is not cosmetic.** Varying size reads as varying importance. If
size does not mean something, make it constant.

**Empty space is structure.** A consistent gutter between bands tells the reader the bands are
peers. Cramming to fit a page destroys that.

**Fewer connectors is usually better than more.** A diagram showing every relationship shows
none of them. Ask what the diagram is *for*, and leave out what does not serve it — then say what
you left out.

## When you cannot make it work

Say so, plainly, and say why. "Twenty-eight elements with sixty connectors will not read at this
size; I suggest splitting by capability, or an executive view with connector labels suppressed" is
useful. Quietly shipping something illegible is not.

## Reference

- [`ea-diagram-advisor`](../ea-diagram-advisor/SKILL.md) — the step BEFORE this one: which diagram
  type and viewpoint to draw, from measured content. Use it when the diagram type was not given
- [`references/grammars.md`](references/grammars.md) — the four grammars in detail, and EA's
  coordinate convention
- [`references/bindings.md`](references/bindings.md) — the language-binding schema, key by key, and
  the loader API in `tools/bindings.py`
- [`references/verification.md`](references/verification.md) — the verification contract, the
  stale-render trap, the bounded correction loop, and what the linter cannot see
- `tools/lint.py` — the linter. Consumes `verify_diagram` output, makes no repository calls, and
  names no modeling language
- `tools/compose.py` — the geometry engine. Pure arithmetic, no EA calls, unit-tested
