# Compositional Grammars — Choosing and Judging a Diagram Layout

Detail supporting [`../SKILL.md`](../SKILL.md). This file is about judgment: which shape of
diagram suits which content, and what separates a composed diagram a reader trusts from one they
squint at. It is deliberately not API documentation — the arithmetic and the parameter names live
in [`../tools/compose.py`](../tools/compose.py), whose docstrings are the reference for those.

Read the coordinate convention below before anything else. It is the one piece of mechanical
knowledge in this file, and it is the single easiest thing to get backwards.

---

## 1. EA's coordinate system

Sparx EA does not use screen coordinates. Verified against EA 17.1:

| Edge | Sign | Relationship |
|---|---|---|
| `left`, `right` | positive, increasing rightward | `right > left` |
| `top`, `bottom` | **negative**, increasing upward | **`top > bottom` numerically** |

Therefore:

```
width  = right - left
height = top - bottom          <-- not bottom - top
```

A real element as EA placed it: `left=50, top=-50, right=190, bottom=-110`. That box is 140 wide
and 60 tall.

Three consequences that trip people up:

- **Moving an element down the diagram makes `top` and `bottom` more negative.** A band stack
  descends by subtracting.
- **The visually topmost rect is the one with the largest `top`.** So the bounding box of a set of
  rects takes the *maximum* of the tops and the *minimum* of the bottoms.
- **An intersection test written for screen coordinates reports the wrong answer**, and it does so
  silently — two boxes that genuinely overlap come back as disjoint. Anything that checks for
  collisions has to be written for this axis, and tested against a known-overlapping pair.

Everything downstream inherits an error here: the layout looks plausible in the numbers, and then
elements sit on top of each other in the diagram. Pin the convention with a test before building
on it.

---

## 2. What a grammar is, and why the split matters

A compositional grammar is a rule for turning *content with a known shape* into *geometry*. It is
not a layout algorithm in the graph-drawing sense — nothing here minimizes edge crossings or
relaxes a force model. Each grammar assumes the content already has a structure (an ordered set of
bands, a set of parallel sequences) and places boxes accordingly, by arithmetic alone.

That restraint is the point. A grammar is deterministic and inspectable: given the same content and
the same sizing you get the same diagram, every time, and you can reason about why a box is where
it is. EA's own automatic layouts are the right tool when the content has no such structure — a
dense dependency graph, for instance. Reach for a grammar when the content *does* have structure
and you want the diagram to show it.

The capability splits three ways, and each corner holds a different kind of knowledge:

| Corner | Holds | Lives in |
|---|---|---|
| Prose | Judgment — which grammar suits this content, what good looks like, when to refuse | `SKILL.md`, this file |
| Code | Arithmetic — deterministic, unit-testable, no repository access at all | `tools/compose.py` |
| Data | Language specifics — sizing, spacing, routing per modeling language | the bindings |

The practical test of the split: **`compose.py` contains no modeling-language names.** No profile,
no technology id, no stereotype. A band of boxes is the same arithmetic whether the boxes are
drawn as capabilities, application components or process steps. If a change to the engine needs a
branch on which language is in play, the specifics belong in a binding instead, and the engine
should be taking one more parameter.

---

## 3. Status — four of five are built

The analysis first resolved the corpus into **four** grammars. Measuring the rows grouped under
"computed geometry" before building it showed they do not share an arithmetic: placing items on a
circle, packing rectangles so their *areas* encode a number, and drawing a waveform against a time
axis are three unrelated pieces of code. The polar one was split out and built.

| Grammar | Status |
|---|---|
| Layered bands | **Implemented** — `compose_layered_bands` |
| Lanes | **Implemented** — `compose_lanes` |
| Nested grid | **Implemented** — `compose_nested_grid` |
| Radial | **Implemented** — `compose_radial` |
| Computed geometry | **Not built.** What remains under the name: treemaps, and timing diagrams |

Do not tell a user computed geometry is available, and do not improvise a call to it. If content
plainly wants it, either compose it from the implemented grammars and say what you approximated, or
hand the geometry over explicitly and say you did it by hand.

---

## 4. Layered bands

Horizontal bands stacked top to bottom, each band holding items laid out left to right.

### What it suits

Content where the vertical axis carries a *meaning* — a layering, a tiering, an order of
abstraction — and the horizontal axis carries only membership.

- Reference models and layered architectures: channels above applications above data above
  infrastructure.
- Capability maps, one band per level of the capability hierarchy.
- Technology stacks.
- Maturity or tier breakdowns, where each band is one tier.

The test: can you name what moving an item from one band to another would mean? If the answer is
"nothing, the bands are just rows I needed", this is the wrong grammar and the content is probably
a flat set.

### What makes it read well

- **The layer order is the reader's mental order.** Consumers at the top, foundations at the
  bottom, or the reverse — but one of the two, consistently, and matching whatever convention the
  audience already uses.
- **Uniform item size within a band.** This is a rule, not an accident of the implementation. A row
  of boxes at four different widths reads as four different kinds of thing even when it is one kind,
  and the reader spends attention decoding the variation instead of the content. Vary size
  *between* bands when the bands hold genuinely different kinds of thing; never within one.
- **Band heights that follow their contents.** A band with two items should not be as tall as a band
  with twelve. Fixed band heights leave holes that read as missing content.
- **Wrapping rather than shrinking.** When a band holds more items than fit, run them onto a second
  row at the same size. Shrinking boxes to fit one row destroys the uniform-size rule and makes the
  crowded band look less important than the sparse one.
- **A visible label strip per band.** The band's own rect, with room for its name, is what tells the
  reader the vertical axis means something.

### What makes it read badly

- **Too many bands.** Past about seven the layering stops being a structure and becomes a list.
  Group the bands or split the diagram.
- **One enormous band.** A band with forty items wrapped over five rows is a grid that has been
  mislabeled as a layer. Either the band should be several bands, or the content wants a nested
  grid.
- **Empty bands with no explanation.** An empty band is legitimate — it says "this layer exists and
  is deliberately unpopulated" — but only if the label makes that claim on purpose. The engine keeps
  an empty band's label row rather than collapsing it silently, so the emptiness is visible and the
  author has to mean it.
- **Centered bands with wildly different widths.** Centering looks tidy when band widths are
  similar and looks like a Christmas tree when they are not. Left alignment is the safer default,
  which is why it is the default.
- **Bands used to carry two dimensions at once.** If the horizontal position within a band also
  means something (time, priority), say so in the diagram, or use a grammar where it is explicit.
  A reader will not guess.

---

## 5. Lanes

Parallel tracks, each holding a sequence of items that flows along the track. Swimlanes.

### What it suits

Content with two axes where one is *sequence* and the other is *responsibility*.

- Process flows, one lane per role, actor, system or organizational unit.
- Value streams, one lane per stage owner.
- Handoff-heavy workflows, where the interesting content is who passes what to whom.
- Release or migration sequences, one lane per workstream.

The test: is there a step order, and does the identity of who performs each step matter? Both have
to be true. Only the order matters, and a single flow is clearer. Only the ownership matters, and
layered bands or a grid is clearer.

### What makes it read well

- **Items at the same sequence index line up on the flow axis.** This is the most important
  property of the grammar and the reason it is worth implementing rather than eyeballing. A handoff
  from one lane to the next should read as a step *across*; if the target step sits half a box
  ahead, the reader has to work out whether that offset means something. It does not, and they
  should never have to ask. The engine allocates one slot per sequence index, sized to the longest
  item at that index in any lane, and centers each item in its slot. A caller can verify it: every
  item comes back carrying the slot it was placed in.
- **Few lanes.** Three to six is comfortable. Beyond that the eye loses the horizontal track and
  the diagram becomes a scatter of boxes.
- **Lane thickness that follows the largest item in it.** A lane with one big item should be thick;
  its neighbors should not be padded to match.
- **Lanes that abut.** Swimlanes are a partition of one space, not a set of separate diagrams.
  Touching lane bands say that; gaps between them say the lanes are unrelated.
- **A label area inside the lane band**, at the leading edge — down the left of a horizontal lane,
  across the top of a vertical one. Labels floating outside the band drift when the diagram is
  edited.
- **An orientation chosen for the content, not out of habit.** Horizontal lanes suit long
  sequences and short lane names. Vertical lanes suit many lanes, or lane names long enough that a
  left-hand label column would eat the canvas.

### What makes it read badly

- **A lane that is nearly empty.** One item in a lane of twelve slots is eleven slots of white
  space the reader keeps scanning for content. Either the lane belongs on the diagram as a whole
  and its emptiness is the message — say so — or that participant is not part of this flow.
- **Ragged lane lengths pretending to be alignment.** If lane A has eight steps and lane B has two,
  the grammar will still align B's two, but the diagram is claiming a parallelism that is not there.
- **A sequence index used for two different things.** If index 3 means "third step" in one lane and
  "third thing this team owns" in another, the alignment is actively lying. Lanes must share one
  sequence.
- **Lanes as a stand-in for layering.** A swimlane diagram with no flow along the lanes is layered
  bands with the wrong label. Use bands.
- **Crossings that are not drawn.** Lanes make handoffs legible only if the connectors between
  lanes are actually placed. A correct lane layout with no connectors is a seating plan.

---

## 6. Nested grid

Containers within containers, each container laid out as a grid of its children: a domain holding
subdomains holding applications.

`compose_nested_grid(nodes, spec=None)`. The input is a recursive tree rather than a flat list — a
node carrying `items` is a container and needs a `name`; a node without `items` is a leaf and needs
an `id`:

```python
compose_nested_grid([
    {"name": "Retail", "items": [
        {"name": "Onboarding", "items": [{"id": 101}, {"id": 102}]},
        {"id": 103}]},
    {"name": "Payments", "items": [{"id": 104}]},
])
```

Leaves and containers may sit side by side at any level, and a leaf at the top level comes back with
`container_id: None`.

### What it suits

Content where **containment is the whole structure** and there is no sequence: two or three levels of
grouping, and usually no connectors at all.

- Domain and subdomain maps; capability maps where the levels are genuine decomposition.
- Portfolio views grouped by owner; application taxonomies.
- Information models grouped by subject area.
- Organization structures, where the nesting *is* the reporting line.

The test: would an arrow between two of these boxes add anything? If the answer is yes, the content
is a graph and this is the wrong grammar. A nesting that also needs arrows to be read is not a
nesting.

### What makes it read well

- **Nesting stops at two or three levels.** Past three a reader can no longer tell which box owns
  which, and the outermost container becomes a frame rather than a statement. The engine **refuses**
  a fourth level rather than warning about it — `max_grid_depth` defaults to 3 and a caller who
  genuinely wants more raises it deliberately.
- **Containers sized by their contents.** A group holding twenty things should be visibly bigger than
  one holding two. Sizing containers alike is the fastest way to make a portfolio view lie about
  where the weight is.
- **Grids close to square, not one long row.** A grouping rendered as a single row reads as a list
  and the grouping disappears. The engine defaults to `ceil(sqrt(n))` columns; `grid_columns`
  overrides it per composition or per container when the content has a real column meaning.
- **Uniform cell size within a level.** Item size is stated by the *parent*, so sibling leaves
  cannot disagree — varying sizes among siblings is what most makes a generated diagram look
  machine-made. Levels may differ from each other; an override does not cascade to grandchildren.
- **Each container's label legible at the zoom the reader will actually use.** The title strip is an
  extra inset at the top of the container, above the padding, so a name never sits on its children.
- **Real whitespace between cells.** A grid packed edge to edge reads as one block. Note that a
  no-overlap check cannot see this: touching rects do not overlap, by design.

### What makes it read badly

- **Four or more levels deep.** See above; this is the one the grammar refuses outright.
- **Containers sized alike.** A container with two children looking as significant as one with
  twenty is a measurement error presented as a picture.
- **Arbitrary grouping.** A grid of "Other" is a confession, not a category. If a third of the
  content lands in it, the grouping is wrong.
- **An empty container with no explanation.** Legitimate — it says "this grouping exists and is
  deliberately unpopulated" — but only if that is meant. The engine keeps an empty container's label
  and one cell of space rather than collapsing it, so the emptiness is visible and the author has to
  own it.
- **Connectors added to "clarify" the nesting.** They contradict it. If the relationships matter more
  than the grouping, use a graph layout.

### Note on the EA mechanism

Nesting in EA is not only geometric. A box drawn inside another box is not the same as an element
genuinely owned by that container, and the two can disagree. **Get the model relationship right
first**; the geometry is the easy half. `container_id` on every item and `parent_id` on every
container are returned precisely so the ownership can be built from the same structure the geometry
came from, rather than inferred back out of the rectangles.

---

## 6a. Radial

A hub and its spokes: items distributed on a ring around a center, optionally with a further ring
hanging off each one.

`compose_radial(nodes, spec=None, hub=None)`. The hub is an **item**, not a container — it is one
of the things on the diagram rather than something enclosing them — and a node carrying `items`
gets its own outer ring, which is what turns a hub-and-spoke into a radial tree.

### What it suits

Content with **one center and peers around it**, where the peers have no order among themselves
that the reader needs. Capability wheels, service catalogs around an organization, a mind map, a
stakeholder map, a cycle of four or five stages.

The test: is there genuinely a center? A radial layout claims one. If every item is a peer and
nothing sits at the middle, the ring is decoration and a grid says the same thing more plainly.

### What makes it read well

- **Square-ish items.** This matters more than it sounds. Items are centered on their point of the
  circle, so a wide flat box reaches closer to the center at the top and bottom of the ring than at
  the diagonals, and the spokes come out visibly unequal in length. A ring of 140x60 boxes reads as
  slightly wrong for a reason most people cannot name. Circles or near-square boxes remove it.
- **Few enough to see the circle.** Past about a dozen the ring reads as a crowd. The engine widens
  the radius rather than letting items collide, so what you get is a very large circle rather than
  an overlap — which is the honest failure, but still a failure.
- **A hub that earns its place.** The center position is the most emphatic on the diagram.
- **One ring, or two at most.** The engine refuses a third by default.

### What makes it read badly

- **No real center.** See above; this is the common misuse.
- **A ring used to imply sequence.** A reader follows a cycle clockwise whether or not one is meant.
  If the order is arbitrary, say so, or use a grid.
- **Long labels.** A wide label forces a wide box, which is exactly what makes the spokes uneven.
- **Arcs you cannot draw.** Reference radial diagrams commonly use curved connectors. The connector
  vocabulary here has Direct, Auto, Custom, Tree, Lateral, Orthogonal and Bezier — **no arc**. A
  generated equivalent is structurally right and visually not identical; say so rather than
  reporting it as reproduced.

---

## 7. Computed geometry — *not built*

Positions derived from data rather than from structure: a two-axis placement where both coordinates
come from element properties. A risk/value bubble chart, a technology radar, a time-phased roadmap.

**What is left under this name is two unrelated things**, once the radial grammar was split out: a
**treemap**, where area encodes a quantity, and a **timing diagram**, with a time axis and step
waveforms. They are separate pieces of work and only the treemap looks worth building.

**Would suit:** portfolio assessments with two scored dimensions, radars with a ring per horizon,
roadmaps where horizontal position is a date.

**Would read well when:** both axes are labeled and their units stated; the scale is honest — a
linear axis for a linear measure, and no silent rescaling to fill the canvas; overlapping points
are resolved by a stated rule rather than left stacked; the source of every score is recorded
somewhere the reader can find.

**Would read badly when:** an axis is unlabeled — which turns a measurement into decoration; the
scores are invented to justify a position the author had already chosen; collision avoidance moves
a point far enough that its position no longer matches its data. A computed diagram claims
precision, so its geometry has to earn it. If the data is not good enough to defend, one of the
other grammars is the honest choice.

---

## 8. Reviewing any composed diagram

Whatever the grammar, these hold. The first three the engine guarantees arithmetically; the rest are
judgment and need a human, or an author acting like one.

1. **No two items overlap**, and no two containers overlap. Items sitting inside their own container
   is expected and is not an overlap — check items against items and containers against containers,
   never the two sets mixed.
2. **Every rect has positive width and height**, and obeys the sign convention in §1.
3. **The composition fits the canvas.** Check the returned bounding box against the space available
   before placing anything.
4. **Uniform sizing within a role.** Same band, same size. Same lane, same size. A box that is
   bigger for no stated reason will be read as more important.
5. **The axes mean something, and the diagram says what.** If the vertical axis is a layering, the
   band labels carry it. If the horizontal axis is a sequence, something on the diagram says so.
6. **A reader who was not in the room can name the structure.** If they cannot say why the boxes are
   arranged this way, the grammar was the wrong one or the content was not ready.

### Worked shape

An example composition over the Westbrook Bank reference model: three bands, centered, with
`Channels` holding three items at the default 140x60 and `Business Applications` holding two at
200x60. The top band's rect starts at `left=20, top=-20`; its items sit at `top=-48`, below the
label strip; the second band's rect starts at `top=-150`, below the first band's `bottom=-120` plus
the band gap. The `Data Platform` band is empty and keeps a label row 40 tall, so the layer is
visible and unpopulated rather than absent. The whole thing reports a bounding box 484 wide and 300
tall, which is what you compare against the canvas.
