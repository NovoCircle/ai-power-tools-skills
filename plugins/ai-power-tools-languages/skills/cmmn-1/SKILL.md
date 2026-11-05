---
name: cmmn-1
description: The OMG Case Management Model and Notation (CMMN) 1.1, the standard for modeling a case, meaning knowledge work whose steps are not fully fixed in advance. It defines the case plan model, stages, plan fragments, tasks (human, process, case and decision tasks), milestones, event listeners (timer and user), case file items, sentries with entry and exit criteria, planning tables and discretionary items, and the decorators (required, repetition, manual activation, auto complete). Use when someone is modeling a case, case management, adaptive or ad hoc case work, a case plan, claims, disputes, investigations, permits or patient care as cases, or asks what CMMN allows, which decorator applies to which element, how plan items start and finish, or how a case differs from a BPMN process.
---

# Case Management Model and Notation (CMMN) 1.1

CMMN is the Object Management Group's standard for modeling a **case**: a proceeding about a subject, where people decide what to do next as the situation develops. It is the case-management counterpart of BPMN. BPMN draws a fixed sequence of steps; CMMN draws what *may* happen, under what conditions, and what a case worker can add while the case runs. The standard defines a metamodel, a notation, a diagram interchange format, execution semantics and an XML exchange format.

CMMN is declarative. Where a shape sits on the page means nothing; only the conditions attached to it do.

## What you are creating

A case model has two halves.

- **The case plan model**: the plan, drawn as a folder shape, with everything the case may do inside it.
- **The case file**: the information the case works on. Only the case file items that take part in the behavior are drawn.

A case has a **design time** (analysts define the work that always belongs to the case, and the *discretionary* work a case worker may add) and a **run time** (people perform the plan and add discretionary items to it as they go).

## The diagram type

CMMN defines **one diagram kind, the CMMN diagram**, and no viewpoints. A diagram depicts a whole definitions file, a case plan model, a stage, or a plan fragment.

A CMMN diagram admits:

- the case plan model, stages, plan fragments (discretionary only), tasks of every kind, milestones, event listeners
- entry criteria and exit criteria (the diamonds on item boundaries)
- planning tables (a decorator on a case plan model, stage or human task) and discretionary items
- case file items
- connectors (a dash-dot-dot line, which the text also calls dotted, for a sentry's on-part), discretionary associations (a dashed line from a human task to the discretionary items of its planning table), and associations with text annotations

It does not draw the case, roles, case file, process or decision definitions, parameters, or expressions. A plan item is drawn solid; a discretionary item is drawn dashed. A plan item appears at most once in one diagram.

## The concepts, in plain words

### The case and its information

- **Case**: the top-level concept. It has exactly one case file, exactly one case plan model, roles, and input and output parameters.
- **Role**: who may do human tasks, plan using discretionary items, and raise user events. Who fills a role is out of scope.
- **CaseFile** and **CaseFileItem**: the information. An item is a document, folder, XML structure or anything else, with a multiplicity and exactly one **CaseFileItemDefinition**. Items nest by containment or by reference; neither chain may loop.

### The plan

- **PlanItemDefinition** (abstract): a building block defined once and used by many plan items. Its kinds are Task, Stage, PlanFragment, Milestone and EventListener.
- **PlanItem**: one use of a definition inside a stage or plan fragment. It can rename it, override its control, and carry entry and exit criteria.
- **Stage**: a tracked group of plan items, an "episode" of the case. It can nest, have a planning table, and be the case plan model. `autoComplete` says whether it finishes by itself.
- **CasePlanModel**: the outermost stage of a case. It is never used by a plan item, has no default control and no entry criteria, may have exit criteria and a planning table.
- **PlanFragment**: a reusable pattern of plan items and sentries with no life of its own at run time. It can only be discretionary.
- **Milestone**: an achievable target that shows progress. No work is attached to it.
- **EventListener**: catches an event. **TimerEventListener** waits for a time (an ISO 8601 expression, optionally measured from a trigger). **UserEventListener** waits for an authorized role to raise it.

### Tasks

- **Task**: an atomic unit of work, blocking (default) or non-blocking. A non-blocking task finishes as soon as it starts and has no outputs.
- **HumanTask**: done by a case worker (one performer role at most). A non-blocking human task is a "manual" task the system does not track. It may have a planning table when blocking.
- **ProcessTask**: calls an external business process (BPMN 2.0, XPDL 2, WS-BPEL).
- **CaseTask**: starts another case with its own case file (reuse). A stage, by contrast, shares the current case file (composition).
- **DecisionTask**: calls an external decision (DMN 1.x).

A process, case or decision task names its target either directly or by an expression, never both. Parameters pass information through parameter mappings.

### Sentries and criteria

- **Sentry**: "on event if condition". It has zero or more **on-parts** (the events) and at most one **if-part** (a boolean condition). It must have at least one of them.
- **EntryCriterion**: the condition for a plan item to become available. **ExitCriterion**: the condition for it to terminate. Each points to a sentry in the same stage or plan fragment.
- An on-part names a case file item transition, or a plan item transition (the standard event). It may name one exit criterion of the source plan item, in which case the event is "exit".
- Any one satisfied entry criterion is enough; any one satisfied exit criterion is enough.

### Planning (run-time choices)

- **PlanningTable**: the scope for planning; may nest. **DiscretionaryItem**: a task, plan fragment or stage a case worker may add. **ApplicabilityRule**: a condition that decides whether a table item is offered.
- Planning can start from a stage's table (items join that stage) or from a human task's table (items join the human task's stage).

### Item control

A **PlanItemControl** holds up to three rules, each a boolean condition: **ManualActivationRule**, **RequiredRule** and **RepetitionRule**. It sits on a plan item or discretionary item, or as the default on a definition; an item's own control overrides the default. Defaults when a rule is absent: manual activation true, required false, repetition false.

## Which decorator goes on which element

Decorators show on a shape that behavior which the metamodel holds as a rule. A check means the decorator may appear on that shape.

| Shape | Planning table | Entry criterion | Exit criterion | AutoComplete | Manual activation | Required | Repetition |
|---|---|---|---|---|---|---|---|
| Case plan model | yes | no | yes | yes | no | no | no |
| Stage | yes | yes | yes | yes | yes | yes | yes |
| Task | human task only | yes | yes | no | yes | yes | yes |
| Milestone | no | yes | no | no | no | yes | yes |
| Event listener | no | no | no | no | no | no | no |
| Case file item | no | no | no | no | no | no | no |
| Plan fragment | no | no | no | no | no | no | no |

The glyphs: planning table (six-cell table), entry criterion (open diamond), exit criterion (solid diamond), AutoComplete (small black square), ManualActivation (small white right-pointing triangle), Required (bold exclamation mark), Repetition (a hash sign). Item-control decorators go at the bottom center; the planning table goes on the top border.

Where the table and the metamodel differ, the metamodel wins: a non-blocking task has no exit criterion and a non-blocking human task has no planning table.

## Relationship rules in summary

CMMN has no allowed-relationship matrix. Its relationships are the metamodel's containment and reference associations (full list in `language.yaml`), and three drawn links:

| Link | Drawn as | From | To |
|---|---|---|---|
| Connector | dash-dot-dot line; the text also calls it dotted, no arrowhead | a plan item (or its exit criterion, or a case file item) | an entry or exit criterion of the sentry holding the on-part |
| Discretionary association | dashed, no arrowhead | a human task that owns a planning table | a discretionary item of that table |
| Association | dotted, optional arrowhead | any element | any element (typically a text annotation) |

An artifact (association or text annotation) is never an end of a connector or a discretionary association. A connector has no execution meaning.

## The rules that matter most

The full list is in `references/rules.md` (152 rules, with ids). The ones that catch most mistakes:

1. **A case has exactly one case file and one case plan model** (CMMN-STR-001), and the case plan model is the outermost stage with no entry criteria and no default control (STR-002, STR-003, STR-005).
2. **A plan item refers to exactly one definition**, defined in its own stage or an enclosing one; never the case plan model, never a plain plan fragment, never its own stage (CMMN-REF-002 to REF-007). Sibling stages do not reach into each other.
3. **A sentry has an if-part or at least one on-part** (CMMN-CRT-001); criteria point to sentries in the same stage or plan fragment (CRT-002).
4. **Which items may have which criteria**: an event listener has no entry or exit criteria; a milestone has no exit criteria; a non-blocking task has no exit criteria (CMMN-CRT-003 to CRT-006).
5. **The standard event must fit the source's lifecycle**: stage and task events for a stage or task; occur-style events for an event listener or milestone (CMMN-CRT-007). An on-part that names an exit criterion uses the event "exit" (CRT-008, CRT-009).
6. **Planning rules**: a planning table is not empty and never contains itself; a discretionary item names a task, plan fragment or stage found in the right enclosing stage; a stage is not discretionary to itself or its nested stages; a non-blocking human task has no planning table (CMMN-PLN-001 to PLN-011).
7. **Task rules**: a non-blocking task has no outputs; a process, case or decision task has exactly one of a direct reference and an expression (CMMN-TSK-002 to TSK-005).
8. **Item-control rules**: a plan item control has at least one rule; event listeners get none of the three rules; milestones get no manual activation rule; a repeating plan item has an entry criterion with an on-part, or none (CMMN-CTL-002 to CTL-007).
9. **Run-time rules (clause 8)** apply only when cases are executed: the outermost stage starts Active, a stage completes by its autoComplete criteria, required items must finish first, suspend and terminate propagate down (CMMN-LIF-001 to LIF-021).

Strength: `must` rules are errors, `should` rules are warnings, `note` rules are advice.

## Westbrook Bank example (an illustration; substitute your own)

Westbrook Bank handles card disputes as a case. This is one way to model it; a reader models their own case in their own tool and technology.

- **Case plan model** "Card Dispute" with the AutoComplete decorator off (a person closes it).
- **Case file items**: "Dispute Claim" and "Supporting Document" (multiplicity zero or more).
- **Stage** "Investigate" (entry: the "Dispute Claim" create event). Inside it:
  - **Human task** "Review Claim", blocking, with the Required decorator. Its performer role is "Dispute Analyst".
  - **Decision task** "Assess Fraud Risk" calling an external decision, entry criterion fed by a connector from "Review Claim" (event: complete).
  - **Human task** "Request Documents", discretionary, listed in the planning table of "Review Claim". A dashed discretionary association joins them.
  - **Timer event listener** "Documents Overdue", a ten-day timer measured from the moment "Review Claim" starts (a start trigger on that plan item; a discretionary item is not a plan item until it is planned, so it cannot be the trigger source).
- **Process task** "Issue Provisional Credit" calling a payments process, with the ManualActivation decorator so an analyst starts it.
- **Milestone** "Dispute Resolved", entry criterion with an on-part on the stage "Investigate" (event: complete), and the Required decorator, so the case cannot complete before it is reached.
- **User event listener** "Customer Withdraws", raised by the role "Dispute Analyst"; an exit criterion on the case plan model listens for it (event: occur).

Check it against the rules: the listener has no criteria of its own (it only feeds one), the milestone has no exit criterion, the discretionary task refers to a definition in the stage that contains "Review Claim", and the case plan model has an exit criterion and no entry criterion.

## Data types and attributes

The standard gives partial coverage. It names no primitive type library: its class diagrams and attribute tables use String, Boolean, URI, QName and DateTime without defining them, and it defines the value lists that matter most (the case file item and plan item transitions, the multiplicity values, the property types, the definition types, and the process and decision implementation types). The attributes that carry a value are under `attributes` on the concepts that have them, for example `isBlocking` (default true) on a task and `autoComplete` (default false) on a stage. See `data_types` and the concept entries in `language.yaml`.

## How it is drawn

The notation is normative (clause 6) and covers every shape a person draws: the folder shape for the case plan model, a rounded rectangle for tasks (with a person, hand, folder, chevron or decision table icon for the kind), a cut-corner rectangle for stages, a stadium shape for milestones, a double-line circle for event listeners, open and solid diamonds for entry and exit criteria, a document shape for case file items, three line styles, and four decorators. Dashed outlines mean discretionary. Size, fill, line color and label position are free. See `notation` in `language.yaml`; what the standard does not settle is stated where it arises.

Sizes and spacing come from `../_languages/layout-standard.yaml`, and the mapping of each concept to a size class comes from `layout` in `language.yaml`.

## References

- `references/standard.md`: the standard in our own words, clause by clause, with citations.
- `references/rules.md`: every rule with its id, strength, clause and whether it can be checked from a saved model.
- `language.yaml`: the machine-readable facts: concepts with their generalizations, relationships with multiplicities, enumerations, lifecycles and transitions, decorators and Table 6.1, the diagram kind and what it admits, constraints, drawing conventions.
