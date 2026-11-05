---
name: dmn-1
description: The OMG Decision Model and Notation (DMN) 1.2, a standard for describing and automating business decisions. Covers the decision requirements level (the Decision Requirements Graph, drawn as a Decision Requirements Diagram or DRD, with decisions, input data, business knowledge models, knowledge sources and decision services, joined by information, knowledge and authority requirements) and the decision logic level (decision tables with hit policies such as unique, any, priority, first, collect, rule order and output order; boxed expressions; literal expressions; invocations; contexts; FEEL and S-FEEL), plus the three conformance levels. Use when someone is modeling or reviewing decisions, decision tables, business rules as tables, decision requirements, decision services, FEEL expressions, or asks what DMN allows, what a hit policy means, whether a decision table is complete or has overlapping rules, or which elements a DRD may connect.
---

# Decision Model and Notation (DMN) 1.2

DMN is the Object Management Group's standard for modeling decisions. It gives business analysts a picture of how a decision depends on data, other decisions, areas of business knowledge and sources of authority, and it gives developers a precise, executable way to write the logic that computes each decision. It is a notation, a metamodel with an XML exchange format, and an expression language. It is not a method (clause 5.2.4).

This skill describes version 1.2 (January 2019). Later versions exist; this skill does not describe them.

## What you are creating

A DMN model answers two questions about a domain of decision-making:

1. **What decisions are made, and what does each one need?** This is the *decision requirements level*: a Decision Requirements Graph (DRG), drawn as one or more Decision Requirements Diagrams (DRDs).
2. **How is each decision computed?** This is the *decision logic level*: a value expression for each decision and each business knowledge model, often a decision table, written in FEEL or another language, shown as *boxed expressions*.

The levels can be used separately. A model can stop at the requirements level (human decision-making, high-level, natural language) or go all the way to executable logic (clause 5.2).

A decision here means the act of determining an output value from inputs, not the option chosen (5.3.1).

## Diagram types and what each admits

DMN defines one diagram type and one family of logic notations.

| Type | Admits | Notes |
|---|---|---|
| **Decision Requirements Diagram (DRD)** | Decision, Business Knowledge Model, Input Data, Knowledge Source, Decision Service (expanded or collapsed); Information, Knowledge and Authority Requirements; Text Annotation and Association | Shows all or part of a graph (a partial view). Under the Listed Input Data option, input data is listed inside each decision instead of being drawn. A decision service is drawn once per diagram, expanded or collapsed. Requirements join only the pairs in the table below. |
| **Boxed expressions** (decision logic notation) | Decision table; literal expression; invocation; context; list; relation; function definition | The notation for one decision's or knowledge model's logic, tied to the DRD element only by name. Not an interchange diagram type. Contexts, lists, relations and function definitions need Level 3. |

## Concepts, grouped

**Decision requirements level**

- **Decision**: the act of determining an output from inputs. May have a question and allowed answers, a value expression, and requirements.
- **Input Data**: information whose value comes from outside the model. It requires nothing.
- **Business Knowledge Model (BKM)**: a reusable function that encapsulates business know-how (rules, a decision table, an analytic model). Called by decisions and by other BKMs.
- **Decision Service**: a set of decisions exposed as a service: output decisions (returned), encapsulated decisions (evaluated inside), input decisions (supplied by the caller) and input data. Stateless; callable from a decision, a BKM or an outside process.
- **Knowledge Source**: an authority for a decision or knowledge model: a person, policy, regulation or analytic insight.
- **Information Requirement** (solid arrow): a decision needs another decision's result or an input data value.
- **Knowledge Requirement** (dashed arrow, open head): a decision or BKM invokes a BKM or decision service.
- **Authority Requirement** (dashed, filled circular head): an element depends on a knowledge source (or a knowledge source depends on a decision or input data). No execution meaning.
- **Text Annotation** and **Association**: comments on the diagram.
- **Business context** (organizational unit, performance indicator): placeholders; a decision can record who makes or owns it, which objectives it supports and which processes and tasks use it.

**Decision logic level**

- **Literal expression**: text in an expression language (FEEL by default).
- **Decision table**: input clauses, output clauses, annotation clauses and rules, with a hit policy.
- **Invocation**: a call of a BKM or decision service with a binding per parameter.
- **Context, List, Relation, Function Definition**: the other FEEL boxed expressions.
- **Item Definition** and **Information Item**: the data structure and range of values, and the variable that carries a value.

**Model container**: *Definitions* holds everything; *Import* brings in other models and schemas; *Element Collection* groups elements.

The full class list, with generalizations, is in `language.yaml` (`concepts`).

## Relationship rules in summary

The kind of requirement is fixed by the two element types it joins. Permitted connections (required element, then the element that requires it):

| Required element | May be required by | Requirement |
|---|---|---|
| Decision | Decision | Information |
| Decision | Knowledge Source | Authority |
| Input Data | Decision | Information |
| Input Data | Knowledge Source | Authority |
| Business Knowledge Model | Decision, Business Knowledge Model | Knowledge |
| Decision Service | Decision, Business Knowledge Model | Knowledge |
| Knowledge Source | Decision, Business Knowledge Model, Knowledge Source | Authority |

That is 11 pairs. Nothing is required by a decision service or an input data element, and nothing else connects. Information requirements form a directed acyclic graph; no decision, BKM or service may require itself directly or indirectly. In the interchange form the requiring element holds the requirement and points at the required one; the arrow in a picture runs the other way, from required to requiring.

## Decision tables and hit policies

A decision table has zero or more input clauses, one or more output clauses (named if there are two or more), optional annotation clauses and at least one rule. Each rule has one input entry (a unary test or "-" for irrelevant) per input clause and one output entry per output clause, in the same order. A rule matches when every input value satisfies its entry; a rule with no input entries always matches.

| Hit policy | Letter | Returns | Needs |
|---|---|---|---|
| Unique (the default) | U | the one matching rule | no two rules overlap |
| Any | A | any matching rule | overlapping rules must give equal outputs |
| Priority | P | the highest-priority output | an ordered list of output values |
| First | F | the first match by rule order | rules numbered; order matters |
| Output order | O | all matches, by output priority | an ordered list of output values |
| Rule order | R | all matches, by rule order | rules numbered |
| Collect | C, C+ C< C> C# | all matches, or their sum, minimum, maximum or count | a numeric operator only with a single output |

The first four return one rule's output; the rest return a list or an aggregate. Two or more output clauses (compound output) never use a Collect operator. A crosstab is always Unique and complete.

**Overlap and completeness** are the checks people ask about most:

- Two input entries for the same input are *disjoint* if they share no value; "-" overlaps every entry. Two rules *overlap* if every corresponding pair of entries overlaps; they are disjoint if any one pair is disjoint. A Unique table must have no overlapping rules.
- A table is *complete* if its rules cover every combination of the *expected input values* of its inputs. You can judge completeness only for inputs whose input values are written down. The expected values should themselves be exclusive (not "<5, <10") and complete (not "<5, >5").
- A complete table gives no default output. An incomplete table may give one; with none, an unmatched input returns null. For full automation the logic must be complete.
- Rule order matters only for First and Rule order tables, which the standard warns hide the overall logic.

## Expressions and conformance

- **Level 1**: requirements, decision logic and decision tables. Expression text is not interpreted (it may be plain English).
- **Level 2**: Level 1 plus **S-FEEL**, a small subset of the expression language: arithmetic, comparisons, simple literals, intervals, and simple unary tests (a comma list, `not(...)` or "-"). Decision table cells are restricted to S-FEEL.
- **Level 3**: Level 2 plus full **FEEL** and the boxed contexts, lists, relations and function definitions.

FEEL is side-effect free and uses three-valued logic (true, false, null). Names may contain spaces; a name may not begin with a reserved word. Dates, times and durations have no literal form and are made with `date(...)`, `time(...)`, `date and time(...)` and `duration(...)`. A built-in function given a value outside its domain returns null. The skill carries the rules a validator needs (category FEEL in `references/rules.md`); the grammar is in the standard (clause 10.3.1.2).

## The rules that matter most

The full list, 142 rules with ids, is in `references/rules.md`. Keep these in front of you:

- Requirements connect only the 11 pairs above; no requirement ends in input data. (DMN-DRD-001, 002)
- Information requirements are acyclic; a decision, BKM or decision service does not require itself, directly or indirectly. (DMN-DRD-003 to 006)
- An information requirement names a required decision or a required input data, not both. (DMN-DRD-007)
- A decision service has one or more output decisions, at least one of the encapsulated or input decisions, and every decision its outputs need is encapsulated, supplied or required by a supplied one. (DMN-DRD-012 to 014)
- Names: an element name is unique among decisions, input data, BKMs, decision services and imports; ids are unique XML IDs. (DMN-NAME-001 to 005)
- A decision that calls a BKM combines or elaborates the result in a literal expression; an invocation is used only when it just binds parameters; every parameter is bound. (DMN-LOGIC-003 to 008)
- Output clauses are named when there are two or more, unnamed when there is one; entries follow clause order. (DMN-TBL-002, 003)
- The hit policy is one of seven, defaults to Unique, and a Unique table has no overlapping rules. (DMN-HIT-001, 002)
- Any tables may overlap only with equal outputs; Priority and Output order need an ordered output-values list; First and Rule order tables are numbered. (DMN-HIT-004, 005, 007)
- Collect operators go only with Collect and never with compound output. (DMN-HIT-008, 009)
- A table is complete over its expected input values; a complete table has no default. (DMN-COV-001, DMN-TBL-014)
- Under Level 2, table cells are S-FEEL. (DMN-FEEL-001, 002)
- A decision's task and process associations are consistent. (DMN-BCTX-001)

## A short example

Westbrook Bank, a fictitious bank, models how it approves a small-business loan.

The decision **Approve Loan** needs the result of the decision **Rate Applicant Risk** (information requirement) and the input data **Loan Application** (information requirement). **Rate Applicant Risk** needs the input data **Credit Report** and invokes the business knowledge model **Risk Rating Table** (knowledge requirement). **Risk Rating Table** is governed by the knowledge source **Westbrook Credit Policy** (authority requirement), and **Approve Loan** is governed by **Credit Committee** (authority requirement). A decision service **Loan Eligibility Service** offers **Approve Loan** to the origination process: its output decision is **Approve Loan**, its encapsulated decision is **Rate Applicant Risk**, its input data are **Loan Application** and **Credit Report**.

**Risk Rating Table** is a decision table, hit policy Unique, with two inputs and one output. Input values: Credit Score is "<600, [600..700], >700" and Debt Ratio is "<=0.35, >0.35". Rules: "<600" with "-" gives High; "[600..700]" with "<=0.35" gives Medium; "[600..700]" with ">0.35" gives High; ">700" with "-" gives Low. The four rules are disjoint (each pair differs on Credit Score) and together cover every combination of the expected values (three credit score ranges, two debt ratio ranges), so the table is complete and valid as a Unique table. Had a fifth rule said "-" and ">0.35" gives Medium, it would overlap rules 1, 3 and 4 and break the Unique policy; the table would need hit policy First or Priority instead, and then rule order or output priority would carry part of the meaning.

This is an illustration. Use your own decisions, data and knowledge, and your own conformance level.

## Data types and attributes

Coverage is full: the standard defines the data types a model uses. They are the FEEL types (number, string, boolean, time, date and time, two duration types, list, context, function, Null and Any), the Item Definition that builds a new type from them (a base type with allowed values, or nested components, optionally a collection), five enumerations (hit policy, aggregator, table orientation, function kind, association direction) and the plain value types of the metamodel attributes. S-FEEL uses the same types with simpler number and date definitions (9.3). `language.yaml` lists them under `data_types.types`, each with its section. Value attributes are on only some concept entries, under `attributes`, with the type, multiplicity and default where the standard gives them; the links between concepts are under `relationships.references`.

## How it is drawn

Coverage is normative. The decision requirements diagram uses a rectangle for a decision, a rectangle with two clipped corners for a business knowledge model, a stadium for input data, a shape with a wavy bottom for a knowledge source, and a rounded rectangle with a heavy border for a decision service (collapsed: a small plus square at the bottom center). Information requirements are solid lines with a filled arrowhead, knowledge requirements dashed with an open arrowhead, authority requirements dashed with a filled circle at the end, and associations dotted. Decision logic is drawn as boxed expressions: decision tables (double lines between input, output and annotation parts, three layouts), literal expressions, invocations, contexts, lists, relations and function definitions. `language.yaml` gives each drawn concept under `notation.elements` and `notation.relationships`, and `notation.not_specified` lists the concepts with no drawing. Size, color and label position are free except where the standard says otherwise (2.2.1). The pictures were read at screen resolution; a few pictures were not read.

Sizes and spacing come from `../_languages/layout-standard.yaml`, and the mapping of each concept to a size class comes from `layout` in `language.yaml`.

## References

- `references/standard.md`: the standard section by section, in our own words, with citations.
- `references/rules.md`: all 142 rules with stable ids (`DMN-<CAT>-nnn`), strength, checkable and source section.
- `language.yaml`: the machine-readable form: concepts and their generalizations, the requirement connection table, the metamodel references with multiplicities, diagram types, conformance levels, and the rules.
