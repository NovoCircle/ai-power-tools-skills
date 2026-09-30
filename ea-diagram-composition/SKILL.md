---
name: ea-diagram-composition
description: Compose Enterprise Architect diagrams that read as deliberate — choose a layout grammar, compute geometry, place and style elements and connectors, then verify and correct the result. Language-neutral; works with any modeling language, reading each notation's conventions from a data binding (several notations ship). Use when building a diagram from model content rather than hand-placing elements, or when a generated diagram looks untidy and you need to know why.
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

## Step 0 — resolve the language binding

Before choosing anything, ask whether the notation's conventions are already recorded. A **binding**
holds one technology's diagram types, sizing, spacing, title convention, routing and standard views
as data, so you are not guessing at what a diagram of that notation is supposed to look like.

```python
from bindings import bindings_for_technologies, resolve_diagram

catalog = bindings_for_technologies(installed)             # once per repository
res = resolve_diagram(installed, style_ex=style_ex, diagram_type=diagram_type,
                      bindings=catalog)                    # once per diagram
if res.resolved:
    dt = res.diagram_type                                  # this diagram type's conventions
```

`installed` is the technology ids EA reports for the repository, or a mapping keyed by them.
`style_ex` and `diagram_type` are the diagram's stored `StyleEx` and `Diagram_Type`. Pass both: about
half of real diagrams carry no MDG type in `StyleEx` and identify themselves by `Diagram_Type` alone.
For a diagram you are about to create, state what you create it as:
`style_ex="MDGDgm=<Technology>::<DiagramType>;"`.

Every answer carries a `path`, a `confidence` and a `reason`:

| `res.path` | Confidence | Means |
|---|---|---|
| `qualified` | exact | the diagram states its own `<Technology>::<DiagramType>` and it is bound |
| `diagram-type` | inferred | `Diagram_Type` names exactly one installed, bound diagram type |
| `base-type` | weak | only the EA base type matched, and base types are shared between siblings |
| `ambiguous` | none | several installed diagram types claim it; none is chosen (`res.candidates`) |
| `unbound` | none | nothing installed claims it |
| `not-installed` | none | it states a technology id the repository does not have |
| `unidentified` | none | it carries no MDG type and no `Diagram_Type`, so nothing was looked up |

**An unbound or ambiguous answer is a finding to report, not a gap to paper over.** Quote
`res.reason` and say what you did instead: compose with the engine's defaults for `unbound`; choose
one candidate explicitly, or use the defaults, for `ambiguous`. Never take the first candidate, and
never reach for a binding the resolver declined to give you. For `not-installed`, check the id
against the installed inventory: ids carry their own version and are not guessable. Report a `weak`
confidence beside the result rather than presenting it as settled.

`find_binding("<technology id>")` is the other entry point and a different tool. It loads one binding
by id and returns `None` silently when there is none, by design, for callers that already hold the
id. It checks nothing against what the repository has installed and cannot say why it found nothing,
so do not use it to pick a binding for a diagram.

### Can this diagram be produced, and who places it?

Four properties on `dt`, one question each. Read them in this order:

| Property | Question |
|---|---|
| `grammar_is_producible` | can we produce this type at all today? **Ask first.** |
| `geometry_is_composed` | do we compute the coordinates, or does EA place it and we tidy? |
| `grammar_is_implemented` | does the engine have a composer for it? Only for choosing a composer |
| `grammar_placement` | who places it: `engine`, `ea` or `diagram-type` |

- **Not producible** — the shape is recorded and nothing here can make it yet (`computed-geometry`
  has no composer; `ea-semantic` is dictated by the diagram type). Say so and stop. Do not compose the
  nearest shape you do have.
- **Producible and composed** — Step 2 onward.
- **Producible, not composed** (`graph`) — skip Step 2. Create the elements, call
  `ea_diagram("layout_diagram")` with the spacing from `dt.spec()`, then style (Step 3) and verify (Step 4).

Do not stop at `grammar_is_implemented`: it is False for a `graph` type EA would have laid out
perfectly well. A viewpoint can override its diagram type's grammar and carries the same properties
(`None` means it has no opinion of its own, so ask the diagram type).

For the diagram type you are building, it also answers:

| Question | From |
|---|---|
| what size, and how far apart | `dt.spec()`, ready for Step 2 |
| how connectors route | `dt.default_route()`, `dt.route_for(relationship)` |
| which visual channels are free | `dt.channel_is_free("fill")`, `dt.free_channels()` |
| whether to draw a title | `dt.draws_its_own_title` |
| which standard view fits the content | `binding.viewpoints_admitting([...])` |

Composing against another notation's binding is worse than composing against none.
`available_bindings()` lists what ships; [`references/bindings.md`](references/bindings.md) is the
schema and the loader API, and the resolution API is documented in `tools/bindings.py`.

## Step 1 — choose a grammar

Analysis of 147 professionally-drawn diagrams found their variety resolves into a handful of
compositional grammars, not 147 special cases. Picking the right one is most of the quality — and
when Step 0 found a binding, it has already been picked: the binding states the grammar for each of
its diagram types.

| Grammar | Use when the content is | Reads badly when |
|---|---|---|
| **layered-bands** | stratified — things sit *above* or *below* other things | there is no real hierarchy, and the bands are arbitrary |
| **lanes** | a flow with owners — who does what, in what order | the items do not actually sequence |
| **nested-grid** | containment — things live *inside* other things | nesting is deeper than about three levels |
| **radial** | one center with peers around it | there is no real center, or the ring implies an order that is not meant |
| **two-column-cycle** | a closed sequence whose steps carry content of their own — down one column, back up the other | the sequence does not actually close, or the boxes are empty |
| **computed-geometry** | quantitative — area or position carries a number (treemaps, timing diagrams) | the numbers do not vary enough to see |
| **graph** | a graph or tree where nothing dictates where a node sits — EA places it, you tidy | the content is really stratified, sequenced or nested, which a general layout ignores |
| **ea-semantic** | the diagram type itself dictates the arrangement — lifelines and message order, a waveform against a time axis | you place boxes on it: coordinates are the wrong output |

That is the full set, `bindings.GRAMMARS`: eight. Five have a composer (`layered-bands`, `lanes`,
`nested-grid`, `radial`, `two-column-cycle`). `computed-geometry` is ours to compute and not built yet. For the last two
we place nothing: `graph` is fully producible through EA's layout, `ea-semantic` is not producible.
See [`references/grammars.md`](references/grammars.md) for what each one is for, in detail, and for
the EA coordinate convention.

**If none fits, say so and use `graph`.** A forced grammar reads worse than an honest one. A capability model in swimlanes is not a swimlane diagram; it is a capability model
that has been made harder to read.

## Step 2 — compute the geometry

Only where `dt.geometry_is_composed` (Step 0). EA places a `graph` type; do not compute it.

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

report = lint.lint_diagram(verified, profile=profile, title_convention=dt.title,
                           roles=roles, rows=rows, columns=columns,
                           stacks=stacks, rings=rings)   # rings: [(hub, items, sweep), ...]
for finding in report.findings:        # errors AND warnings AND info, not just errors
    print(finding.severity, finding.rule, finding.subjects, "->", finding.correction)
for line in report.not_run:
    print("not judged:", line)
```

`tools/lint.py` reads a `verify_diagram` result and nothing else. Without a binding, omit
`title_convention`.

**The groupings are your job, not the linter's.** Which elements play one role, sit in one row or
column, form a stack or ring a hub are composition facts you know and geometry does not. Coordinates
cannot tell a stack from boxes that merely look stacked, nor a tall narrow vertical stack from a
horizontal one, so the linter will not guess. **A rule with no grouping does not run.**

| Pass | Shape | Rules |
|---|---|---|
| `roles` | `{role: elements}` | `uniform-sizing` |
| `rows`, `columns` | a list of groups; `columns` is the same shape, judged along y | `pitch` |
| `stacks` | `[(axis, containers), ...]` | `ragged-stack`, `staggered-stack` |
| `rings` | `[(hub, items, sweep), ...]` | `uneven-spokes`, `uneven-ring-angles` |

`axis` is `"vertical"` (read top to bottom: the bands should share a width and a left edge) or
`"horizontal"` (share a height and a top edge), from `lint.STACK_AXES`. Pass `columns` as well as
`rows` and the spacing rule judges the vertical axis too. A wrapped row is two rows. Do not declare a
deliberately tapering or stepped stack.

**`sweep` is in degrees, the same value you gave the radial composer, and it is required for the
angle rule.** A ring bunched into 200 degrees and a deliberate 200-degree fan are the same geometry;
only your intent tells them apart. A `(hub, items)` pair is still accepted, and gets spoke lengths
but no angle judgment: `uneven-ring-angles` does not run.

**Telling "did not run" from "ran and found nothing".** For stacks and rings, the metric key
(`worst_stack_extent_spread`, `worst_stack_alignment_spread`, `worst_spoke_spread`,
`worst_ring_angle_spread`) is absent from `report.metrics` when the rule did not run. Three rules
always record their key, so read the denominator beside it: `roles_measured`,
`pitch_groups_measured` and `title_convention_stated`. A zero (or False) denominator means nothing
was measured, so the count beside it is vacuous, not a result. `report.not_run` lists a grouping you did declare that could
not be judged: a ring with no sweep, or groups too small to compare anything within.
The label rules (`label-clipped`, `label-cramped`) also need `include_svg` on the `verify_diagram`
call, and say so on `not_run` when it is missing.

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
- **Pitch** — in a declared row or column, neighbors that touch (error, even when the spacing is
  perfectly even) or spacing that is uneven (warning). Judged on gaps for uniform sizes and on center
  pitch for mixed ones; `worst_pitch_spread` is the metric.
- **Inconsistent sizing** — elements in the same role at different sizes. This is the one people
  skip and it is the one that most makes a diagram look machine-made.
- **Ragged and staggered stacks** — containers that differ in cross-axis extent (`ragged-stack`), or
  that start at different leading edges (`staggered-stack`). Warnings.
- **Uneven spokes and ring angles** — ring items at unequal distances from the hub, or bunched to one
  side of it. Warnings.
- **Crossings** — a count of connectors crossing, `info` only. It cannot tell a removable crossing
  from a necessary one, so compare between passes rather than aiming for zero.
- **Unrouted connectors** — no explicit route, so the diagram depends on EA's default.
- **Inconsistent connector labels** — some named and some not, so the blank ones read as oversights.

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
- [`references/grammars.md`](references/grammars.md) — the grammars in detail, and EA's
  coordinate convention
- [`references/bindings.md`](references/bindings.md) — the language-binding schema, key by key, and
  the loader API in `tools/bindings.py`
- [`references/verification.md`](references/verification.md) — the verification contract, the
  stale-render trap, the bounded correction loop, and what the linter cannot see
- `tools/lint.py` — the linter. Consumes `verify_diagram` output, makes no repository calls, and
  names no modeling language
- `tools/compose.py` — the geometry engine. Pure arithmetic, no EA calls, unit-tested
