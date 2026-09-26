# Language Bindings — Diagram Conventions as Data

Detail supporting [`../SKILL.md`](../SKILL.md). This file is the normative schema for a binding:
every key, whether it is required, and what it is validated against. Which grammar suits which
content is judgment and lives in [`grammars.md`](grammars.md); the arithmetic lives in
[`../tools/compose.py`](../tools/compose.py).

---

## 1. What a binding is

Every modeling language has its own diagram types, its own sizing and spacing, its own title
convention, its own routing habits, and its own catalog of standard views. If those live in code,
every new notation is an engineering task and the library never covers more than the few that were
hard-coded. So they live in data instead — one YAML binding per technology — and adding a notation is
a data change rather than an engineering task.

The dependency runs one way only. `compose.py` contains no technology name and does not import the
loader: a binding is data that *feeds* the engine. A single `if technology == …` in the engine would
quietly undo the whole design.

## 2. Where bindings live, and how one is found

Bindings sit in `bindings/`, one file per technology. Two ship: `ArchiMate3` and `BPMN2.0`.

The filename is a slug of the technology id — lowercased, with anything outside letters, digits, `.`,
`_` and `-` flattened to `-`, so `BPMN2.0` becomes `bpmn2.0.yaml`. The **declared `technology` is
authoritative**: when no slug matches, the loader reads each file's declared id, so a file named
anything at all still binds the technology it says it does.

Bindings are parsed with `yaml.safe_load`, always. That is why a binding cannot carry executable
content — `!!python/object` is refused by the parser rather than by a check someone could forget to
run. PyYAML is required, and is loaded the way `validate_model` loads it: if it is missing, the error
says so and names the install.

```
pip install pyyaml
```

## 3. The closed vocabularies

Four vocabularies are fixed. A value outside them is refused on load.

**Grammars** — four, because the variety of real diagrams resolves into four. Three are implemented.

| Grammar | `compose.py` |
|---|---|
| `layered-bands` | implemented — `compose_layered_bands` |
| `lanes` | implemented — `compose_lanes` |
| `nested-grid` | implemented — `compose_nested_grid` |
| `computed-geometry` | not implemented |

**Channels** — the ten visual channels a diagram can carry a variable in: `fill`, `border`,
`border_width`, `line_color`, `line_style`, `font_color`, `opacity`, `icon`, `size`, `position`.

**Title conventions** — two: `drawn`, meaning the diagram carries a drawn title element on the
canvas, and `frame-header`, meaning EA's own diagram frame supplies it and drawing one would double
up.

**Routes** — the ten EA accepts, from a connector's Line Style submenu: `Direct`, `AutoRouting`,
`CustomLine`, `TreeVertical`, `TreeHorizontal`, `LateralVertical`, `LateralHorizontal`,
`OrthogonalSquare`, `OrthogonalRounded`, `Bezier`. Comparison ignores case and punctuation; the
string is stored as written. The server is the source of truth for these names — the loader's copy
exists so a typo is caught on load instead of at write time.

## 4. The schema

Every validation error names the offending key by its path into the document —
`diagram_types.Application.channels.fill`, `viewpoints.ApplicationCooperation.diagram_type` — so an
author can find it without guessing. Unknown keys are refused rather than ignored, and the common
mistakes are told what they probably meant.

### 4.1 Top level

| Key | Required | Validated against |
|---|---|---|
| `technology` | yes | Non-empty string, and must not contain `::`. This is the part *before* the `::` in an `MDGDgm=<Tech>::<DiagramType>` value, and it has to match EA verbatim. |
| `display_name` | no | Non-empty string. Defaults to `technology`. |
| `extends` | no | Technology id of another binding in the same directory. Cannot be this binding's own id; cycles are refused by name. |
| `stereotype_prefix` | no | String, `""` included. See §5.3 — `""` is a statement, not an omission. |
| `notes` | no | Non-empty string. |
| `diagram_types` | yes | Mapping, at least one entry. |
| `viewpoints` | no | Mapping. Absent is a legitimate answer for a notation that publishes no catalog. |
| `presentation_profiles` | no | Mapping. |

### 4.2 `diagram_types.<name>`

The key is the diagram type name as EA spells it, verbatim — BPMN's is `Business Process`, with a
space.

| Key | Required | Validated against |
|---|---|---|
| `base` | no | Non-empty string. The EA base diagram type this MDG diagram type is built on, which is what a caller passes to `create_diagram` to create one — `Logical` for `ArchiMate3::Application`, `Analysis` for `BPMN2.0::Business Process`. Nothing inside the skill consumes it; it is there for the call that makes the diagram. |
| `grammar` | yes | One of the four grammars. |
| `title` | yes | `drawn` or `frame-header`. |
| `sizing` | yes | §4.3. |
| `spacing` | no | §4.4. Omitted means the engine's own defaults. |
| `routing` | yes | §4.5. |
| `channels` | yes | §4.6. |
| `notes` | no | Non-empty string. |

### 4.3 `sizing`

A mapping of notation concept name to `{w, h}`, both positive whole numbers. `default` is required —
every diagram type needs a fallback box size, and per-concept entries are refinements of it. `width`
and `height` are refused with a pointer to `w` and `h`.

Keys are concept names as the notation's own specification writes them (`ApplicationComponent`), not
what EA stores. See §5.3.

> **Per-concept sizes are yours to apply.** `spec()` carries `sizing.default` and nothing else, and
> the engine sizes items uniformly within a band or a lane. A `Junction: {w: 20, h: 20}` entry does
> not take effect on its own — read it with `size_for` and act on it, or you will place 100x70
> junctions. See §7.

### 4.4 `spacing`

Any subset of `compose.DEFAULT_SPEC`'s keys — `item_gap_x`, `item_gap_y`, `item_gap_flow`,
`lane_gap`, `band_gap`, `wrap_width`, `align` and the rest — spelled the way the engine spells them.
Values are copied into the spec verbatim. See §5.1.

> **Each grammar reads its own keys, and nothing checks which ones you set.** `spacing` is validated
> against the whole of `DEFAULT_SPEC` without regard to the diagram type's `grammar`, so a `lanes`
> binding may carry band-only keys and a `layered-bands` binding may carry lane-only keys. Keys the
> composer for that grammar never reads are inert, not refused, and nothing reports them.
>
> | Read by | Spec keys |
> |---|---|
> | both composers | `origin_left`, `origin_top`, `item_width`, `item_height`, `label_height` |
> | `layered-bands` only | `item_gap_x`, `item_gap_y`, `h_pitch`, `row_pitch`, `wrap_width`, `align`, `band_pad_x`, `band_pad_y`, `band_gap`, `band_pitch`, `min_band_width` |
> | `lanes` only | `item_gap_flow`, `flow_pitch`, `lane_pad`, `lane_gap`, `min_lane_thickness`, `label_width` |
>
> The label key depends on orientation in `lanes`: a horizontal lane reserves `label_width` down its
> left, a vertical lane reserves `label_height` across its top. A band always uses `label_height`.
>
> **`compose_lanes` never reads `item_gap_x` or `item_gap_y`.** All three BPMN diagram types are
> `grammar: lanes` and all three set both, so in `bpmn2.0.yaml` those two are recorded measurements
> rather than layout input — kept for a future nested-grid or bands rendering, and labeled as such at
> the point they are set.

### 4.5 `routing`

| Key | Required | Validated against |
|---|---|---|
| `default` | yes | A route name. Leaving it unstated means every connector falls back to whatever EA last did, which is not a convention. |
| `trunk_for` | no | List of relationship type names this notation habitually draws as a shared trunk. |
| `trunk_route` | no | A route name. Defaults to `OrthogonalSquare` when `trunk_for` is present. |
| `notes` | no | Free text. |

### 4.6 `channels`

| Key | Required | Validated against |
|---|---|---|
| `fill` | yes | A string saying what the notation uses fill for, or `~`. |
| `claimed` | no | Mapping of channel name to a string saying what it already means. `fill` is not allowed here — it is declared by `fill`. |
| `free` | no | List of channel names, no duplicates, none of them already spoken for. |
| `notes` | no | Free text. |

See §5.2. This is the block the rest of the schema exists to protect.

### 4.7 `viewpoints.<name>`

A standard view the notation itself defines — ArchiMate's viewpoints, TOGAF's deliverables, UAF's
views. Holding the catalog as data is what lets view selection stay generic instead of growing a
branch per notation.

| Key | Required | Validated against |
|---|---|---|
| `diagram_type` | yes | Must be a diagram type this binding declares. |
| `intent` | no | List of phrases a request might match. |
| `admits` | no | List of concept names, no duplicates. Concept names, not stored stereotypes. |
| `grammar` | no | One of the four. Overrides the diagram type's grammar for this viewpoint. |
| `notes` | no | Free text. |

### 4.8 `presentation_profiles.<name>`

How much detail a view shows, orthogonal to its diagram type. The same content can be duplicated
into a second diagram under a different profile, giving a live detail view *and* a live executive
view of one model rather than a screenshot of one of them.

A profile says what it **shows**; EA is told what to hide. The loader owns that inversion, so
`hide_connector_labels` in a binding is refused with a pointer to `connector_labels`.

| Key | Value |
|---|---|
| `description` | Non-empty string. |
| `connector_labels`, `connector_stereotypes`, `element_stereotypes`, `notes` | `true` or `false`. |
| `compartments` | `all`, `none`, or a list of compartment names. |
| `collapse_parallel` | `true` or `false` — collapse parallel connectors between a pair onto one line. |
| `direction_only` | `true` or `false`. Refused unless `collapse_parallel` is also set: it means nothing on its own and reads as if it does something. |

Every key is optional. A profile that says nothing about stereotypes leaves them alone rather than
asserting a default it never chose.

---

## 5. What the schema is strict about, and why

### 5.1 `spacing` uses the engine's own key names

`compose.py` distinguishes a **gap**, the space between two boxes, from a **pitch**, which runs
leading edge to leading edge and therefore includes the box it steps over. It raises when a pitch is
smaller than the item it has to step over.

> A binding author writing `pitch: 40` beside a 100-wide item has written a layout the engine
> refuses, and would not find out until generation time.

So `spacing` is validated against `compose.DEFAULT_SPEC` itself. A binding can only name a key the
engine really has, spelled the way the engine spells it, which makes the translation into a spec the
identity — the two cannot drift apart. `pitch:` is refused with the keys the author probably meant,
`item_gap_x` and `item_gap_y`, and so are `h`, `v`, `gap_x` and `gap_y`.

Values are not range-checked here. `compose.py` owns those rules, and duplicating them would give two
answers that can disagree. What is checked is the key, because an unknown key is the failure the
engine cannot see.

### 5.2 `channels` is mandatory, and so is `fill`

Each notation **already claims** some visual channels. A second variable has to go somewhere else,
and a binding that lets an agent recolor ArchiMate fills has broken the notation while looking like a
feature.

`fill` is required even when the answer is "nothing" — write `~`. Leaving the key out is not a
neutral default; it is a binding that has not said whether the most tempting channel on the diagram
is available.

A channel cannot be both claimed and free. Listing one in both places is refused, because it tells a
consumer it is safe to overwrite something the notation needs. The one exception falls out of that
rule rather than around it: when `fill` is `~`, fill is not spoken for, so it may appear in `free`.

Fill is sometimes worse than claimed — it is unavailable. Measured on EA 17.1 build 1716,
`ArchiMate_Node` and `ArchiMate_Grouping` ignore a per-diagram fill outright: the write succeeds, the
property reads back, and EA draws the element in its own colors, because the stereotype's shape
script paints it. Seven of nine sampled concepts honor it. Nine concepts is a sample rather than a
sweep, which is why this is a note in the binding and not data a consumer can query yet. In practice,
reach for `Device` or `SystemSoftware` over `Node` when a technology layer needs color coding.

### 5.3 `stereotype_prefix` — concept names in, stored stereotypes out

`admits` and `sizing` keys use concept names the way the notation's own specification writes them:
`ApplicationComponent`. What EA stores in `t_object.Stereotype` is the prefixed form,
`ArchiMate_ApplicationComponent`.

The prefix is data because it is not guessable. It was measured on EA 17.1 build 1716's built-in
ArchiMate3 MDG, which prefixes with `ArchiMate_`; BPMN2.0 uses no prefix, and an install carrying a
differently built MDG can differ again. `stereotype_for` applies the prefix and `concept_for` removes
it, so the conversion happens in one place.

### 5.4 `title` is explicit per diagram type

Neither convention can be the silent default: a diagram with two titles and a diagram with none are
equally likely mistakes. It is recorded per diagram type because the split tracks notation — measured
across the reference corpus, 13 of 13 ArchiMate diagrams draw a title and 10 of 11 BPMN diagrams rely
on EA's diagram frame.

> The corpus catalog spells the second convention `frame-only`. The schema spells it
> `frame-header`. They are the same convention.

### 5.5 A binding may name a grammar that cannot be composed

`computed-geometry` is a valid value with no code behind it. That is deliberate: recording an
implemented grammar for a diagram type that is genuinely something else would be a lie stored as
data, and the lie would be believed precisely because it composes.

`nested-grid` was in this position until it was implemented, which is what the arrangement is for:
ArchiMate's Organization and Capability viewpoints had been recorded as the nested grids they are,
so the day the grammar shipped they became composable without a single binding changing.

`DiagramTypeBinding.grammar_is_implemented` is how a consumer finds out before it composes rather
than after. `False` is a real answer, not an error — check it, say so, and fall back to a plain graph
layout instead of composing the wrong shape.

### 5.6 `extends` replaces whole entries

`extends` names a technology id and resolves against the same directory. Merging goes one level into
each catalog: a diagram type, viewpoint or profile the child restates **replaces the parent's
entirely** rather than merging field by field. Field-level merging would let a child inherit half a
convention — a parent's `channels` under a child's `grammar` — which is harder to reason about than
restating the type. A child that leaves `stereotype_prefix` empty inherits the parent's.

---

## 6. The loader API

`tools/bindings.py`. Anything invalid raises `BindingError`, whose message names the path into the
document.

| Call | Returns |
|---|---|
| `find_binding(technology, directory=None)` | The `Binding` for a technology id, or `None` if there is not one. Defaults to the skill's own `bindings/`. |
| `load_binding(path)` | Load, validate and resolve one file, following `extends`. |
| `load_binding_text(text, source)` | Validate and load from YAML text. No directory, so no `extends` resolution. |
| `available_bindings(directory=None)` | `{technology id: filename}` for every valid binding on hand. An invalid file is omitted rather than raising, so one bad file does not make the whole catalog unreadable; load it directly to see why. |

On `Binding`:

| Member | Does |
|---|---|
| `diagram_type(name)` | One `DiagramTypeBinding`. Raises, naming what is declared. |
| `viewpoint(name)` | One `Viewpoint`. Raises, naming what is declared. |
| `profile(name)` | One `PresentationProfile`. Raises, naming what is declared. |
| `stereotype_for(concept)` | `ApplicationComponent` to `ArchiMate_ApplicationComponent`. |
| `concept_for(stereotype)` | The inverse. A stereotype without the prefix comes back unchanged — models contain elements stereotyped from other technologies, or from none, and a lookup helper is the wrong place to have an opinion about that. |
| `diagram_type_for_mdgdgm(value)` | Resolve an `MDGDgm=<Tech>::<DiagramType>` value, or `None` when it names another technology, so a caller can try the next binding. Only about half of real diagrams carry `MDGDgm` at all; the rest identify themselves through `Diagram_Type`, so resolution needs a second path. |
| `viewpoints_admitting(concepts)` | Viewpoints that admit **every** concept given, narrowest first — the one admitting the fewest concepts overall leads, ties broken by name. Ranking is on admissibility only; intent matching belongs to the caller. |

On `DiagramTypeBinding`:

| Member | Does |
|---|---|
| `spec(overrides=None)` | Build a `compose.py` spec: `sizing.default` becomes `item_width` and `item_height`, and `spacing` is copied across verbatim. Caller overrides win, and an override naming a key the engine does not have is refused here, where the message can mention the binding. |
| `size_for(concept="")` | Box size for a concept, falling back to `default`. Takes the concept name, not the stored stereotype. |
| `claimed_channels()` | Channel to what the notation already uses it for, `fill` included. |
| `free_channels()` | Channels a second variable may legitimately use. |
| `channel_is_free(channel)` | Ask about one. |
| `default_route()` | The diagram type's default route. |
| `route_for(relationship)` | The route for a relationship type: `trunk_route` for anything in `trunk_for`, otherwise the default. |
| `draws_its_own_title` | Property. `True` when `title` is `drawn`. |
| `grammar_is_implemented` | Property. Whether `compose.py` can compose this grammar. See §5.5. |
| `mdg_diagram_type` | Property. The `<Tech>::<DiagramType>` string, to compare against a diagram's own `MDGDgm`. |

On `Viewpoint`: `admits_concept(concept)`, plus `diagram_type`, `intent` and `admits` as read-only
attributes.

On `PresentationProfile`: `display_settings()`, which returns `set_diagram_display` keyword arguments
(see §8), and `collapses_parallel`, a property saying whether to collapse parallel connectors between
a pair onto one line. Collapsing hides relationships, so a profile that sets it needs an annotation
on the diagram saying what was summarized.

## 7. Worked example

Composing an application view over the Westbrook Bank reference model.

```python
from bindings import find_binding
from compose import compose_layered_bands

binding = find_binding("ArchiMate3")
if binding is None:
    ...        # nothing bound for this technology: say so, fall back to a plain graph layout

dt = binding.diagram_type("Application")
if not dt.grammar_is_implemented:
    ...        # the binding records what the notation does; this one cannot be composed

result = compose_layered_bands(
    [
        {"name": "Channels", "items": [{"id": 13477}, {"id": 13478}]},
        {"name": "Business Applications", "items": [{"id": 13479}]},
    ],
    dt.spec({"align": "center"}),
)
```

Then place with `ea_diagram("add_elements_to_diagram_bulk")`, passing the returned
`left`/`top`/`right`/`bottom` per element and `layout="none"`, and route connectors with
`dt.default_route()` or `dt.route_for("Realization")`.

Three things the binding answers that the spec does not carry:

- `binding.stereotype_for("ApplicationComponent")` gives the stereotype to query or write.
- `dt.size_for("Junction")` gives a concept its own box size. The spec carries only the default, and
  the engine sizes items uniformly within a band or a lane, so a concept needing its own size needs a
  band of its own, a lane override, or that size applied when you place it.
- `dt.draws_its_own_title` says whether to add a title element or leave it to EA's frame.

## 8. Two limitations

**`find_binding` returns `None` for an unbound technology, and that is normal.** Most repositories
use several technologies nobody has bound. A caller should say so and fall back to a plain graph
layout rather than composing against the wrong binding — which is also why the declared `technology`
is checked rather than the filename trusted.

**`PresentationProfile.display_settings()` emits only settings verified to change what EA renders.**
There are seven: `hide_connector_labels`, `hide_element_stereotypes`, `hide_connector_stereotypes`,
`hide_attribute_types`, `hide_operation_return_types`, `hide_operation_brackets` and
`show_element_notes`. Each was established by rendering the diagram and reading the markup, against
content the setting could actually suppress — not by writing the value and reading it back, which EA
would echo either way.

**`compartments: none` does not remove a compartment.** EA's `SuppressedCompartments` was measured
through six value shapes against a class with populated attribute and operation compartments and
changed nothing every time, so there is no verified way to take a compartment off a diagram. What is
available is reducing its detail to names: `balance` rather than `balance: Decimal`, `getBalance`
rather than `getBalance(): Decimal`. So `none` and any explicit compartment list both mean "the least
detail EA will give us", and `all` means full detail. That is a smaller promise than the profile
vocabulary suggests, and it is stated rather than papered over — a profile must never promise a
suppression that silently does nothing.

**`notes` is the one setting whose polarity does not flip.** Everywhere else a profile says what it
shows and EA is told what to hide. Element notes are hidden by EA *by default*, so `notes: true`
becomes `show_element_notes: True` rather than a `hide_` flag set False. Tidying that for consistency
turns notes off in the detail view and on in the executive one, which is exactly backwards.
