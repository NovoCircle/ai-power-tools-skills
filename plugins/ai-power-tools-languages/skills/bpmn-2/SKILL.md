---
name: bpmn-2
description: The OMG Business Process Model and Notation (BPMN) 2.0.2, the standard language for modeling business processes. It covers process flows (activities, events, gateways, sequence flow), pools and lanes, collaborations with message flows between participants, conversations, choreographies, data objects and stores, sub-processes, compensation and transactions, executable processes (execution semantics) and the mapping of an executable process to WS-BPEL. Use when someone is modeling or reviewing a business process, drawing a process flow or swimlane diagram, choosing between an exclusive, inclusive, parallel, event-based or complex gateway, using start, intermediate, boundary or end events, connecting pools with message flows, building a collaboration, conversation or choreography diagram, deciding what a connection or event may be, making a process executable, or mapping a BPMN process to BPEL.
---

# BPMN 2.0.2

BPMN is the Object Management Group's language for describing how work flows through an organization, and how organizations exchange messages. It has a drawn notation, a precise metamodel behind the notation, an interchange format, and (for processes meant to run) execution semantics and a mapping to WS-BPEL. It is a modeling language, not a method.

This skill describes version 2.0.2 (OMG formal/13-12-09). It covers the whole standard: the four conformance types, the execution rules that apply when a process is marked executable, and the WS-BPEL mapping. The ISO edition of BPMN was not compared.

## What you are creating

A BPMN model is a set of **flow objects** (events, activities, gateways) joined by **connecting objects** (sequence flow, message flow, association, data association, conversation link), arranged in **swimlanes** (pools and lanes), with **data** (objects, stores, inputs and outputs) and **artifacts** (groups, annotations) alongside. A diagram shows one view of it.

The model describes types of work, not one particular instance. A task called "Check credit" describes what is done every time; tokens, which the standard uses to explain behavior, are a thinking aid and appear in no diagram.

Every model element has an id, a name and optional documentation. The standard defines no mandatory business attributes beyond those of the elements; it does not model organizations, strategy, data structures or business rules (7.2), so describe those elsewhere and refer to them.

## The four diagram kinds

The standard gives no closed list of diagram types. This library uses the four names of its conformance wording (2.2.1, 2.5).

| Diagram | Shows | Admits | Does not admit |
|---|---|---|---|
| **Process** | The flow of one process: what is done, in what order, decided how | Tasks, sub-processes, call activities; events; gateways; sequence flows; data objects, data stores, data associations; associations, groups, text annotations; pools and lanes as swimlanes | Choreography activities. Message flows appear only when the process sits inside a collaboration |
| **Collaboration** | Two or more participants (pools) and the messages between them | Pools, empty (black box) or holding a process (white box); message flows between pools or to flow objects inside them; conversation nodes and links; a choreography drawn between the pools; artifacts | A message flow between two objects in one pool; a sequence flow across a pool boundary |
| **Choreography** | The expected message exchange between participants, with no one in control | Choreography tasks, sub-choreographies, call choreographies; a small subset of events; constrained gateways; sequence flows; annotations and groups; message decorators; participant bands | Data objects and stores, ordinary activities, data associations, pools and lanes of its own. Message flows are not drawn |
| **Conversation** | Who talks to whom about what, one hexagon per topic | Pools (usually empty); Conversation, Sub-Conversation and Call Conversation nodes; conversation links; optionally the message flows a conversation expands into | A choreography between the pools (usually); a link that joins two non-conversation ends |

A Conversation diagram is a particular use of a Collaboration diagram (9.5). Choose the diagram from the question being asked: "how does our process run?" is a Process diagram; "who exchanges what with whom?" is a Collaboration; "what is the agreed protocol, regardless of who runs it?" is a Choreography; "which topics tie these parties together?" is a Conversation.

## The concepts, in plain words

The schema behind the standard has 133 types; `language.yaml` lists them all with their generalization. The spelling there is the schema's own type name without spaces. What follows is the working vocabulary.

### Containers
- **Process**: a graph of activities, events, gateways and sequence flows that does work. It is **private** (internal to one organization; executable or not) or **public** (shows only what other participants can see; never executable). It can be reused through a Call Activity.
- **Collaboration**: participants, message flows, and optionally the processes and choreographies between them. **Choreography** and **Global Conversation** are kinds of collaboration.

### Events (circles)
- Start events only catch, end events only throw, intermediate events catch or throw. Start is a thin line, intermediate double, end thick; throwing events have a filled marker, catching events an unfilled one.
- An event has no trigger (**None**), one (**Message, Timer, Conditional, Signal, Link, Escalation, Error, Cancel, Compensation, Terminate**) or several (**Multiple**: any one; **Parallel Multiple**: all).
- A **boundary event** is an intermediate catch event on the edge of an activity. Interrupting, it cancels the activity; non-interrupting, the activity keeps running and the event's flow runs in parallel.
- Where each type may appear is a table (Table 10.93; recorded in `language.yaml` under `event_placement`). For example: Error and Cancel only on a boundary or as end events, Cancel only with a Transaction, Link only in normal flow, Terminate only at an end, and a sub-process starts with None only.

### Activities (rounded rectangles)
- **Task**: atomic work. Kinds: **Service** (automated service), **Send**, **Receive**, **User** (a person working with software), **Manual** (no software or engine), **Business Rule**, **Script**. The plain Task is the Abstract Task.
- **Sub-Process**: an activity with a process inside it, collapsed (plus marker) or expanded. It defines a scope. Special kinds: **Event Sub-Process** (started by its own event while the parent runs, dotted border), **Transaction** (double border), **Ad-Hoc Sub-Process** (no required order, tilde marker).
- **Call Activity** (thick border): calls a global Process or a Global Task.
- **Loop characteristics**: a **Standard Loop** repeats while a condition holds; **Multi-Instance** creates several instances in parallel or in sequence.

### Gateways (diamonds)
Gateways control how sequence flows split and join; they do no work. **Exclusive** (one path), **Inclusive** (every path whose condition is true), **Parallel** (all paths, waits for all), **Event-Based** (the first event to occur wins), **Complex** (an activation condition you write).

### Data
**Data Object** (and a reference to it), **Data Store**, **Data Input** and **Data Output** with **input sets** and **output sets**, and the **Data Association** that moves data between them. Tokens never travel along data associations. A **Message** is the content exchanged between participants, shown as an envelope.

### Connecting objects
**Sequence Flow** (order inside a process; plain, conditional or default; "exception flow" is the informal name for flow leaving a boundary event), **Message Flow** (between participants), **Association** (links text or an artifact to an element), **Data Association**, **Conversation Link**.

### Swimlanes
A **Participant**, drawn as a **Pool**, is a business entity or role in a collaboration. A **Lane** partitions a process, usually inside a pool, and may be nested; what a lane means is your choice (role, department, system). A participant can have a **multiplicity** (how many instances).

### Artifacts
**Group** (informal box around related elements, may span pools), **Text Annotation**. Neither changes flow.

### Choreography and conversation
A **Choreography Task** is one or two message exchanges between two or more participants, drawn with a band per participant; the initiating participant's band is plain and the others are lightly shaded. A **Sub-Choreography** is a compound one; a **Call Choreography** calls another. A **Conversation** hexagon groups message flows that share a correlation (everything about one order); **Sub-Conversation** and **Call Conversation** nest and reuse.

### Supporting concepts
**Correlation** (keys and properties that route a message to the right running instance), **Resources and roles** (who performs an activity), **Interfaces and operations** (the services a participant offers), and the named **Signal**, **Error** and **Escalation** payloads. They matter most for executable processes.

## Connection rules in summary

The standard states them as two tables with refinements in prose. Both are in `language.yaml` under `relationships`.

**Sequence flow** (Table 7.3): a start event, task, sub-process, gateway or intermediate event may flow to a task, sub-process, gateway, intermediate event or end event. An end event never has an outgoing sequence flow; a start event never has an incoming one. In a choreography the same table applies to choreography activities. Pools, lanes, data objects, groups and annotations take no sequence flow.

**Message flow** (Table 7.4): a pool, task, sub-process, throwing message event or message end event may send to a pool, task, sub-process, catching message event or message start event. A message flow may not join two objects in the same pool, and lanes, gateways, data objects, groups and annotations cannot have message flows.

**Refinements that catch most mistakes:**
- Sequence flows cannot cross a pool boundary; message flows can. Sequence flows may cross lane boundaries.
- A start event has no incoming sequence flow and at least one outgoing; an end event has at least one incoming and none outgoing.
- A boundary event has no incoming sequence flow (it is attached, not reached) and needs an outgoing one; the Compensation boundary event is the exception: it has an association to its handler instead.
- A gateway must split or join: several flows in, or several flows out.
- An Event Sub-Process has no sequence flows in or out.
- A conditional flow out of an activity needs another outgoing flow; a default flow comes from an exclusive, inclusive or complex gateway or from an activity.
- Inside an expanded sub-process, nothing connects to anything outside it, except events attached to its boundary.
- A black-box pool has no sequence flows; message flows attach to its edge.

## The rules that matter most

The full list, 263 rules with ids, is in `references/rules.md`. The ones to keep in front of you:

- A message flow connects two separate pools, never two objects in one pool. (BPMN-CONN-001)
- Sequence flows do not cross pool boundaries. (BPMN-CONN-003)
- Artifacts take no sequence or message flows. (BPMN-CONN-005)
- A conversation link joins exactly one conversation node. (BPMN-CONN-015)
- A start event is not a sequence-flow target and has an outgoing flow; an end event is a target and has none outgoing. If either an end event or a start event exists, so must the other. (BPMN-EVT-001, EVT-002, EVT-004)
- Intermediate events in normal flow have flow in and out; boundary events have flow out only. (BPMN-EVT-007, EVT-008)
- None and Link events are never boundary events; Error and Cancel are never in normal flow; a Cancel event belongs only to a Transaction. (BPMN-EVT-009, EVT-010)
- A link source has a matching target with the same name, within one process level. (BPMN-EVT-012)
- An Event Sub-Process has one start event and no sequence flows. (BPMN-EVT-024)
- A gateway merges or splits, and its direction must agree with its flow counts. (BPMN-GATE-001, GATE-002)
- An event-based gateway has two or more unconditional outgoing flows to events or receive tasks. (BPMN-GATE-005, GATE-006)
- A receive task that starts a process has `instantiate` set and no incoming flow. (BPMN-ACT-005)
- An ad-hoc sub-process holds activities and has no start or end events. (BPMN-ACT-009)
- A public process is not executable. (BPMN-ACT-011)
- A data association moves data between item-aware elements with matching definitions, or it transforms. (BPMN-DATA-003)
- The initiator of a choreography activity took part in the one before it. (BPMN-CHOR-001)

**How strength reads.** `must` is an error, `should` is a warning, `note` is advice. Rules that are about drawing (line weight, markers, shading) are marked `checkable: none` in `language.yaml` and detailed under `conventions`; they guide how a diagram looks and a saved model cannot break them.

## Executable processes

A process is **executable** when its `isExecutable` attribute is true. That tells every reader the process is meant to run on an engine, and it switches on extra rules (those with `applies_when: executable` in `language.yaml`). A process that is not marked executable is documentation and is exempt: you may leave out everything below. A public process cannot be marked executable.

What an executable process adds, in practice:
- Every Service, Send and Receive task, and every Message event, names the **operation** it uses; the operation has exactly one in-message and at most one out-message. Messages carry item definitions, normally typed by XML Schema. (BPMN-LIFE-023, BPMN-SERV-005)
- Conditions are **formal expressions** (the default language is XPath): sequence-flow conditions, conditional events, loop conditions and gateway activation conditions. A conditional event needs one; timer attributes are mutually exclusive. (BPMN-EVT-018)
- Repeated or multi-instance activities carry loop characteristics with a cardinality or a data input; `startQuantity` and `completionQuantity` are at least 1; every I/O specification has at least one input set and one output set. (BPMN-ACT-004, ACT-010, DATA-002)
- A diverging exclusive or inclusive gateway should have a default flow, because with no true condition and no default the engine throws. The order of an exclusive gateway's outgoing flows matters: the first true condition wins. (BPMN-EXGW-003)
- A sub-process starts with one empty start event or none at all; it has no non-empty start events. An event sub-process has one start event and is not connected to normal flow. (BPMN-SUBP-001, BPMN-EXEV-004)
- A parallel instantiating event-based gateway accepts message triggers only, with shared correlation. (BPMN-EXGW-007)
- Compensation handlers are not connected to normal flow and start with a catching Compensation event. (BPMN-COMP-002)
- Ten elements are non-operational (manual and abstract tasks, data states, I/O rules, ad-hoc processes, physical item definitions, "while executing" set references, `isClosed`, `isImmediate`). An engine may ignore them, so a model must not rely on them for behavior. (BPMN-INST-002)

Behavior that only a running instance shows (the activity life cycle, token movement through gateways, what happens on interruption and compensation) is explained in `references/execution.md`. A validator that reads only a saved model cannot check it; these are the rules marked `runtime` in `language.yaml`. State them as explanation, not as findings.

## The WS-BPEL mapping

Clause 14 maps **one orchestration process (one pool)** to **one WS-BPEL 2.0 process**. It maps no diagrams, collaborations, choreographies or conversations. The standard defines no flag for "map this process"; the rules with `applies_when: bpel-mapping` apply when the mapping is requested.

To be mappable a process must:
- be **sound**: no deadlock, and never two tokens on one sequence flow (BPMN-BPEL-003);
- use only constructs the clause maps (service, send, receive and abstract tasks; embedded sub-processes and some event sub-processes; standard loops; multi-instance with flow condition All; message, timer, error, compensation and terminate events in the positions the clause lists; exclusive, event-based, inclusive and parallel gateways in block patterns). User, manual, business rule and script tasks, call activities, ad-hoc sub-processes, transactions, signal, escalation, link, conditional and cancel events and the complex gateway are not mentioned by the clause; absence is not a prohibition, since the semantic mapping lets any sound process map if the BPEL behaves the same (BPMN-BPEL-011, BPEL-029);
- give Service and Send tasks an operation and a connected participant, Receive tasks an operation, messages an XML-schema typed item definition, and each of those tasks a single input set and a single output set (BPMN-BPEL-009, BPEL-012, BPEL-025);
- have unique names that convert to valid XML names (BPMN-BPEL-008).

Block-structured models map directly (the syntactic mapping). Unstructured loops and merges need the extended mapping, which spawns derived processes or duplicates elements. The construct-by-construct table, the conditions and the notes on the clause are in `references/execution.md`.

## Telling similar concepts apart

- **User, manual or abstract task.** A user task is done by a person with software and tracked by the engine; a manual task is done without either and is not tracked; an abstract task is a placeholder that says nothing of how.
- **Pool or lane.** A pool is a participant in a collaboration; a lane partitions the process inside a pool. Message flows go between pools; sequence flows stay inside one.
- **Message flow or sequence flow.** A message flow carries a message between participants; a sequence flow orders work inside one process.
- **Interrupting or non-interrupting boundary event.** Interrupting cancels the activity and the flow leaves through the event; non-interrupting lets the activity finish and starts a parallel path.
- **Event sub-process or boundary event.** A boundary event reacts to something while one activity runs; an event sub-process reacts to something while its whole parent scope runs, and can see the parent's data.
- **Exclusive, inclusive or parallel gateway.** One path; every path whose condition is true; every path.
- **Event-based gateway or exclusive gateway.** An event-based gateway waits for the first event or message to occur; an exclusive gateway evaluates data conditions now.
- **Signal, message or escalation.** A message goes to one named receiver; a signal is broadcast to anyone listening; an escalation passes a problem up a level of the same process.
- **Compensation or cancel.** Compensation undoes the effects of an activity that already completed; cancel aborts a Transaction and triggers its compensation.
- **Process or choreography.** A process is one participant's logic; a choreography is the agreed message protocol between several, with no owner.
- **Conversation or collaboration.** A conversation names a topic that groups message flows; a collaboration shows the flows themselves.
- **Call activity or sub-process.** A sub-process lives inside this process; a call activity points at a separate, reusable process or global task.

## A short example

Westbrook Bank, a fictitious bank, takes a loan application from an applicant. Two parties, so a **Collaboration** diagram with two pools. Substitute your own organization, roles and steps.

**Pool "Applicant"** (a white-box pool, one process):
1. Start event (None) "Need a loan".
2. Send task "Submit loan application", with a message flow to the bank's pool.
3. Event-based gateway: waits for either of two message events or a timer.
   - Catching message event "Approval received" leads to an end event (None) "Loan approved".
   - Catching message event "Decline received" leads to an end event (None) "Loan declined".
   - Timer event "30 days" leads to an end event (None) "Application withdrawn".

**Pool "Westbrook Bank"** with two lanes, "Loan Officer" and "Underwriting":
1. Message start event "Application received" (Loan Officer), the target of the applicant's message flow.
2. User task "Verify applicant identity" (Loan Officer).
3. Service task "Run credit check" (Underwriting), with a non-interrupting timer boundary event "Takes longer than 2 days" whose flow leads to a task "Remind underwriter" and then to its own end event.
4. Exclusive gateway "Credit acceptable?" with one conditional flow ("score at or above threshold") to the user task "Approve loan" (Underwriting), and a default flow to the next step.
5. "Approve loan" leads to a message end event "Approval sent", with a message flow to the applicant's "Approval received" event.
6. The default flow leads to a message end event "Decline sent", with a message flow to the applicant's "Decline received" event.

How it measures against the rules:
- Both message flows cross the pool boundary and none joins two objects in one pool. (CONN-001)
- No sequence flow crosses from one pool to the other; the lanes are only a partition of the bank's process. (CONN-003)
- Each start event has an outgoing flow and no incoming sequence flow; each end event has an incoming flow and none outgoing. (EVT-002, EVT-004)
- The boundary event is attached to "Run credit check", has no incoming sequence flow and has an outgoing one. (EVT-008)
- The exclusive gateway splits and has a default flow. (GATE-001, ACT-002)
- The event-based gateway has three unconditional outgoing flows to catching events. (GATE-005, GATE-006)

Three typical mistakes to avoid, taken from this diagram: drawing a sequence flow from "Submit loan application" to "Verify applicant identity" (it crosses a pool; use the message flow), drawing a message flow between the two lanes of the bank (the same pool; it is a sequence flow or nothing), and leaving the gateway "Credit acceptable?" with one incoming and one outgoing flow (it must split or join).

To make the bank's process executable, mark it `isExecutable`; "Run credit check" then names an operation with an in-message (the applicant's data) and an out-message (the score), the gateway condition becomes a formal expression over that score, and "Verify applicant identity" and "Approve loan" remain user tasks the engine hands to people.

## Data types and attributes

Coverage is partial. BPMN has no data model of its own: the structure of an item lives outside the model, by default in XML Schema, and expressions default to XPath (10.4). What the standard does define is the value type of each attribute, 11 enumerations (for example the process type, the gateway direction and the event-based gateway type) and a few diagram-interchange types. `language.yaml` lists them under `data_types.types`, each with its section. Attributes are carried on only some concept entries, under `attributes`, with the type and multiplicity where the standard states them; the references between concepts are under `relationships.references`.

## How it is drawn

Coverage is normative: the standard defines the shapes, line styles and markers, and expects a drawing implementation to use them, while size, color and label position stay free (2.2.3, 7.5). Events are circles (thin line to start, double line between, thick line to end), activities rounded rectangles, gateways diamonds with a marker for the kind, and pools rectangles with a name band. Sequence flow is a solid line with an arrowhead, message flow a dashed line with a circle at the start and an open arrowhead, association a dotted line. `language.yaml` gives each drawn concept under `notation.elements` and `notation.relationships`; `notation.not_specified` lists the concepts with no drawing. Each icon, marker and line style is described in words with its table of the depiction library (12.3); a few pictures of the depiction library were not read.

Sizes and spacing come from `../_languages/layout-standard.yaml`, and the mapping of each concept to a size class comes from `layout` in `language.yaml`.

## Where the standard is unclear

The standard is internally inconsistent in a few places (for example the triggers allowed for an event sub-process start, the number of participants in a choreography task, and some rules of Clause 13). `references/standard.md` section 17 lists each one and how this library reads it: the machine-readable model first, otherwise the stricter table.

## References

- `references/standard.md`: the standard clause by clause, in our own words, with citations and the list of its inconsistencies.
- `references/execution.md`: the activity life cycle, token flow, runtime behavior of events and compensation, and the WS-BPEL mapping.
- `references/rules.md`: all 263 rules with stable ids (`BPMN-<CAT>-nnn`), strength, when each applies and whether a saved model can be checked against it.
- `language.yaml`: the machine-readable form: concepts and their generalizations, variants, the sequence-flow and message-flow tables, event placement, diagram types, conformance sub-classes, the rules and the drawing conventions.
