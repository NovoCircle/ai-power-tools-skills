# How a language file is laid out

Each language on this shelf has a folder named by its id, for example `bpmn-2`. The folder holds a `SKILL.md` that says when to use the guide, a `language.yaml` that holds the facts, and two reference pages. This page says how `language.yaml` is organized so a reader, or any tool's skills, can find the same thing in the same place for every language.

The files describe the language, never a diagramming tool. They say what the standard says and nothing more. Where a standard defines nothing, the file says so with `coverage: none` and does not fill the gap with a good idea.

## Rules that hold everywhere

- **No tool is named,** except in a citation of where something was read. A source system that defines the language is part of the language and stays.
- **Every fact carries its section.** A fact whose section was not read is left out and recorded as an open point by the people who maintain the guide.
- **Our own words.** Quotes are short.
- **Sizes and colors appear in `notation` only if the standard states them.** Our own layout conventions sit in a separate `layout` block, labeled as ours.

## The top-level keys

| Key | Holds |
|---|---|
| `id`, `name` | The language's id (the same as its folder name) and its display name |
| `concepts` | The things the language defines. Each has a name, a short definition, and the section that defines it |
| `relationships` | The links the language defines between concepts. Guides keep these in more than one place, listed below |
| `constraints` | Rules the standard states, each with its section |
| `data_types` | What the standard says about types and attributes |
| `notation` | How the standard draws the language |
| `layout` | Our conventions for drawing it: which size class each concept takes, and how each diagram type is arranged. Added with the shared layout standard |

## Where relationships sit

A guide holds its relationships in one of these places. A reader tries them in this order.

1. `concepts.relationships`, as a mapping or a list.
2. A top-level `relationships` list.
3. A top-level `relationships` mapping with one of the keys `items`, `types`, `list`, or `kinds`.
4. Nowhere named. Some languages define a connection table or only a metamodel reference, so nothing is named to draw.

## `data_types`

```yaml
data_types:
  coverage: full        # full | partial | none: how much the STANDARD defines, not how much we wrote
  section: "8.3"        # where the standard defines them; omit only for none
  note: One plain sentence on what this language does about types.
  types:                # required unless coverage is none
    - {name: Boolean, kind: primitive, section: "8.3.1"}
    - {name: ProcessType, kind: enumeration, values: [None, Public, Private], section: "8.3.2"}
    # kind: primitive | enumeration | structured | unit | other
  attributes:
    coverage: every_concept   # every_concept | some_concepts | none
    where: concepts           # concepts = on each concept entry, under `attributes`
```

A language built on another may add `inherits_from: uml-2` and list only what it adds. A concept that has attributes lists them under the key `attributes`, as mappings with at least `name` and, where the standard gives them, `type` and `multiplicity`.

## `notation`

```yaml
notation:
  coverage: normative   # normative | informative | none: what the STANDARD gives
  section: "7.2"
  note: One plain sentence, for example "No symbols are defined; Annex A gives three informal conventions."
  inherits_from: uml-2  # optional, for a language drawn with another's notation
  default: {shape: "the class box with the keyword above the name", line: "a labeled line", section: "9.1"}
  elements:             # concept name -> how it looks
    Task: {shape: rounded rectangle, marker: none, label: inside, section: "10.2"}
  relationships:        # relationship name -> how it looks
    SequenceFlow: {line: solid, target_end: filled arrowhead, source_end: none, label: optional, section: "10.5"}
  not_specified: []     # concepts and relationships the standard gives no drawing for
```

A shape is described in plain geometry and words a person could draw from: "rounded rectangle", "circle with a double outline", "dashed line with an open arrowhead". Every concept and relationship is covered by exactly one of `elements`, `relationships`, `default`, or `not_specified`. With `coverage: none`, `not_specified: all` is enough, and the note says so.

## `layout`

The `layout` block is ours, not the standard's. It maps each concept to a size class from `layout-standard.yaml` and says how each diagram type is arranged. It never restates a size: sizes and spacing live in the shared standard, in one unit, for all languages.

```yaml
layout:
  element_types:          # concept name -> size class. A concept left out takes `box`
    DecisionNode: decision-diamond
  no_element_type:        # concepts with no symbol of their own to size
    drawn_as_text:        # a group, named for what its concepts have in common
      reason: Shown as text inside another symbol, so there is no symbol to size.
      concepts: [CallEvent, TimeEvent]
  diagram_types:
    Class diagram:
      arrangement: graph
      route: straight
      title: frame-header
      trunk:              # optional: lines of these kinds join into one shared line
        route: tree-vertical
        for: [Generalization]
      channels:           # what each visual channel already means on this diagram type
        fill: null        # what fill means, or null if it means nothing
        claimed:          # channel -> what it means, so a second meaning can't use it
          size: Compartment content, because a box is sized by what it shows.
        free: [line_color, font_color]  # channels a second meaning may use
```

`no_element_type` accounts for the concepts that take no size class: text in a compartment, a marker, a line. Each group states one `reason` and lists its `concepts` by name. A list is required, so a sentence or a pointer to `notation.not_specified` doesn't count.

A diagram type that isn't listed takes the shared defaults. `trunk` says which relationship kinds are drawn as one shared line, with `route` naming how it runs and `for` naming the kinds. `channels` keeps a second meaning from colliding with the notation: `fill` and each entry under `claimed` say what a channel already carries, and `free` lists the channels left over. A channel can't be both claimed and free. The arrangements, routes, titles, and channels are all from the vocabulary in `layout-standard.yaml`.

## `SKILL.md`

Each guide's `SKILL.md` has two sections with these exact headings: `## Data types and attributes` and `## How it is drawn`. Each is a few plain lines that state the coverage, name what matters most, and point at `language.yaml`.

## What a passing check does not prove

The checks measure form. A drawing entry has to be something a person could draw from, so a guide that says "an icon is drawn" without saying what the icon looks like is not finished. Describe each icon, marker, and line style in words.
