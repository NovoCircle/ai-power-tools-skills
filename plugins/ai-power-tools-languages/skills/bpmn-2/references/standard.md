# BPMN 2.0.2, section by section

This is a summary of the OMG specification in our own words. It is not a substitute for the specification and does not reproduce its text; the few short quoted phrases are cited. Clause, table and annex numbers are the specification's. "p." is the printed page number (the PDF page is the printed page plus 30 in the body). Where the standard is silent or inconsistent, this file says so and says how the library reads it.

Source: Object Management Group, *Business Process Model and Notation (BPMN)*, version 2.0.2, formal/13-12-09 (the changebar edition is formal/13-12-10), with the normative machine-readable files listed in section 1. The ISO edition of BPMN 2.0.1 was not compared.

The specification text was read from the PDF. Its class diagrams are images and were not read; the class hierarchy in `language.yaml` comes from the normative schema (`Semantic.xsd`), which names 133 complex types. Where the PDF and the schema disagree on a name or value, the schema is followed (see section 17).

---

## 1. What the standard is

**Identity.** BPMN 2.0.2 is an OMG standard in the Business Modeling domain, document status formal. It supersedes 2.0.1; the cover notes "a minor change to Clause 15". The PDF cover dates it December 2013 (`formal/2013-12-09`); OMG's About page says January 2014. This library cites the document id and does not choose between the dates. Earlier formal versions were 1.0 (2007), 1.1 (2008) and 1.2 (2009).

**Nature.** BPMN is four things at once:

1. A graphical notation for process flow (Clauses 7 to 11).
2. A metamodel with an XML interchange format (Clauses 8 to 11 and 15; the schema and the CMOF files).
3. A diagram-interchange model that records where shapes sit (Clause 12, BPMN DI).
4. Execution semantics for processes marked executable (Clause 13), and a mapping of a subset to WS-BPEL (Clause 14).

**Scope limits.** Clause 7.2 excludes organizational models, functional breakdowns, data models, strategy models and business-rule models. BPMN draws the flow of work and messages; it does not describe who the organization is or what the data means.

**Normative machine-readable files.** `BPMN20.cmof`, `BPMNDI.cmof`, `DC.cmof`, `DI.cmof`, `Infrastructure.cmof`, the four schemas `BPMN20.xsd`, `BPMNDI.xsd`, `DC.xsd`, `DI.xsd`, plus `Semantic.xsd` and an XSLT between the XMI and the schema. The PDF cover also lists `Semantic.cmof`; the About page does not. Clauses 1 to 15 and these files are the substance; Annexes A to C are informative.

**Intellectual property.** RF-RAND. The specification is copyrighted by OMG and thirteen vendors; this library paraphrases.

---

## 2. Conformance (Clause 2)

A tool may claim conformance only if it meets every compliance point of the type it claims; a partial match may say only "based on" the standard. There are four conformance types, and a tool claiming one need not support the others. Complete Conformance means all four. (The clause's own sub-clause numbers run 2.1 to 2.4 while the headings run 2.2 to 2.5; this is a numbering slip, not a content gap.)

| Type | What it requires | Where |
|---|---|---|
| Process Modeling | The core packages (Infrastructure, Foundation, Common, Service). Process diagrams, Collaboration diagrams and Conversation diagrams with the shapes and markers as the standard draws them, the connection rules (structural conformance), process semantics, attribute mechanisms, and import and export of Process and Collaboration diagrams. Choreography elements are not expected. | 2.2 |
| Process Execution | Full operational semantics and the activity life cycle of Clause 13. Import of Process diagrams, including the definitional Collaboration. No graphical syntax is required. | 2.3 |
| BPEL Process Execution | Process Execution plus the BPMN-to-WS-BPEL mapping of Clause 14. | 2.4 |
| Choreography Modeling | The core packages, Choreography diagrams, pools and message flow, the choreography elements (Choreography Task, Global Choreography Task, Sub-Choreography, Message, a subset of events and gateways), and import and export of Choreography and Collaboration diagrams. | 2.5 |

### 2.1 Sub-classes of Process Modeling

Process Modeling Conformance has three optional sub-classes (2.2.1). A tool claiming a sub-class must support every element in it and every attribute the sub-class tables list for each element; attributes the tables do not list and the schema does not require are outside the sub-class.

| Sub-class | Intent | Content (summarized from Tables 2.1 to 2.4) |
|---|---|---|
| Descriptive | Visible elements and attributes for high-level modeling, "comfortable for analysts" who come from flowchart tools. Table 2.1. | Pool, lane set, plain sequence flow, message flow, exclusive and parallel gateways, plain, user and service tasks, collapsed and expanded sub-process, call activity, data object, data store reference, text annotation, association and data association, group, none, message, timer-start and terminate events as listed, documentation. |
| Analytic | Descriptive plus roughly half of the remaining constructs, chosen from training experience and an analysis of defense-architecture-framework usage. Table 2.2. | Conditional and default sequence flows, send and receive tasks, standard loop and multi-instance, inclusive and event-based gateways, default flow on exclusive gateways, link events, signal events, message and timer intermediate and boundary events (including non-interrupting), error, escalation and conditional events in the positions listed, and the Message. |
| Common Executable | For tools that emit executable models. XML Schema for data types, WSDL for service interfaces and XPath for data access are mandatory. Tables 2.3 and 2.4. | All three sequence-flow kinds, expanded sub-process, exclusive, parallel and event-based gateways, none start and end, user and service tasks, call activity, data object, text annotation, data association, message start and end, terminate end, message intermediate catch and throw, timer catch, error boundary; plus the supporting classes: loop characteristics, resources, I/O specification, data inputs and outputs, item definition, operation, message, error, assignment and three event definitions. |

Two footnotes matter. In Table 2.1 a data association is abstract and its serialization needs an invisible I/O specification behind it. "Documentation" is an attribute, not a visible element.

**Which subset suits an architect.** The visible notation an architect draws is closest to Analytic. Descriptive is too small for most real processes (no intermediate events, no inclusive or event-based gateway, no conditional flow). Common Executable adds mostly attributes an architect's model does not need. Full Process Modeling adds the remaining event types, ad-hoc and transaction sub-processes, compensation, multi-participant collaboration detail and conversations. This is an editorial reading, not the standard's.

---

## 3. How the metamodel is expressed

The schema `Semantic.xsd` has 133 complex types, 14 of them marked abstract, and 11 named enumerations. Every type derives from `BaseElement` (which carries an id, documentation and extension elements) except a few text and extension helpers. The abstract types in the schema are BaseElement, BaseElementWithMixedContent, RootElement, FlowElement, FlowNode, Activity, Event, CatchEvent, ThrowEvent, EventDefinition, Artifact, LoopCharacteristics, ChoreographyActivity and ConversationNode. The text of the PDF additionally treats Gateway, CallableElement, FlowElementsContainer, InteractionNode, ItemAwareElement and DataAssociation as abstract.

`language.yaml` names concepts as the schema does, without the leading `t`, and records the generalization of each. Some of the standard's own named concepts are not types but a type plus a condition on its attributes (Event Sub-Process, Boundary-attached events, the Multiple events, Compensation Activity, Black-box Pool, the Public and Private process kinds). The file lists these as variants of their class.

BPMN is also deliberately not a data model: it hooks onto external structures, with XML Schema as the default type system and XPath as the default expression language (10.4).

---

## 4. The concepts

The full list, with generalizations, is in `language.yaml`. The groups follow the standard's own chapters.

**Containers and process kinds (8.2, 9, 10.1, 11.1).**
- *Definitions* is the outermost container of every interchange file; it sets the namespace and the expression language.
- A *Process* is a graph of activities, events, gateways and sequence flows that does work in an organization. Attributes: process type (None, Private, Public), whether it is executable, whether it is closed, and what it supports. A private process lives inside one organization; it may be executable or not. A public process shows only the activities that talk to other participants and their order (its old name was "abstract"); a public process may not be executable (10.2, Table 10.1).
- A *Collaboration* is a set of participants (pools), the message flows between them, and optionally processes inside pools and choreographies between them. *Choreography* and *Global Conversation* are subtypes of Collaboration. A *Global Choreography Task* is a reusable, atomic choreography definition that holds no flow elements.

**Events (10.5).** Circles. Start events only catch, end events only throw, intermediate events catch or throw. Line weight tells them apart: thin for start, double thin for intermediate, thick for end. An event has zero event definitions (the None event), one (a typed event) or several (Multiple, or Parallel Multiple when the catching event waits for all). The ten typed definitions are Cancel, Compensate, Conditional, Error, Escalation, Link, Message, Signal, Terminate and Timer.
- A *Boundary Event* is an intermediate catch event attached to the edge of an activity. It is interrupting (the activity is cancelled) or non-interrupting.
- An *Implicit Throw Event* is a non-drawn throw event used by multi-instance activities.
- The positions each event type may occupy are in section 7.

**Activities (10.3).** Rounded rectangles. A *Task* is atomic; a plain Task is the Abstract Task. The specific tasks are Service, Send, Receive, User, Manual, Business Rule and Script. A User Task is scheduled by a task manager and tracked by the runtime; a Manual Task is done without an engine and is not tracked. A *Sub-Process* is an activity whose inside is modeled with activities, gateways, events and flows, and which defines a scope; it is collapsed (plus marker) or expanded. Three special sub-processes exist: the *Event Sub-Process* (a sub-process triggered by event, outside normal flow, dotted border), the *Transaction* (double border, three outcomes) and the *Ad-Hoc Sub-Process* (no required order; tilde marker). A *Call Activity* (thick border) calls a global Process or a Global Task. The Global Tasks are the plain one plus User, Manual, Script and Business Rule forms. Loop behavior is a *Standard Loop* (repeat while a condition holds) or *Multi-Instance* (several instances in parallel or in sequence). Resource roles (Performer, Human Performer, Potential Owner) say who does an activity.

**Gateways (10.6).** Diamonds that control divergence and convergence of sequence flows; they do no work. A gateway has a direction (Unspecified, Converging, Diverging, Mixed). The five kinds are Exclusive (one path, "X" marker optional), Inclusive (all true paths, circle marker), Parallel (all paths, plus marker), Complex (an activation expression, asterisk marker) and Event-Based (the first event wins, a race).

**Data (10.4).** *Data Objects* (and references to them), *Data Stores* (and references), *Properties*, *Data Inputs* and *Data Outputs* with their *I/O specification*, *input sets* and *output sets*, and the *Data Association* that moves data between item-aware elements. Tokens do not travel along data associations. A *Message* is the content of a communication between participants; on a diagram it is an envelope decorator on a message flow or choreography task.

**Connecting objects (7.3, 8.4.13, 9.4, 9.5.6).** *Sequence Flow* (order of flow elements; solid line; variants normal, conditional, default, and informally exception flow from a boundary event). *Message Flow* (a message between two participants; dashed line, circle at the start, open arrowhead). *Association* (dotted line linking text or an artifact to a flow object; a compensation association links a compensation boundary event to its handler). *Data Association*. *Conversation Link* (double thin line joining a conversation node to a participant). The standard calls Association both a connecting object (Table 7.1) and an artifact (8.4.1); in the schema it is an Artifact.

**Swimlanes (9.3, 10.8).** A *Participant*, drawn as a *Pool*, is a business entity or role in a collaboration; a pool holds a process (white box) or is empty (black box). *Partner Entity* and *Partner Role* are the kinds of participant; *Participant Multiplicity* gives minimum and maximum instance counts. A *Lane* is a sub-partition of a process, usually inside a pool, and may be nested; a *Lane Set* groups lanes of one partition. What a lane means is the modeler's choice.

**Artifacts (8.4.1).** Additional information that does not change flow: *Association*, *Group* (a dashed rounded box that groups elements of one category value, informally, possibly across pools) and *Text Annotation*. *Category* and *Category Value* back the group.

**Choreography (Clause 11).** A choreography is a kind of process that describes the expected message exchange between participants, with no central controller. Participants appear as bands on the activities, not as pools. A *Choreography Task* is atomic: one or two message exchanges between two or more participants, with one band per participant and one task-name band; the non-initiating bands are lightly shaded. A *Sub-Choreography* is a compound choreography activity. A *Call Choreography* calls a Choreography or a Global Choreography Task.

**Conversation (9.5).** A conversation is a logical grouping of message flows that share correlation (for example, everything about one order). A *Conversation* is a hexagon; a *Sub-Conversation* is a hexagon with a plus that opens into message flows and conversations; a *Call Conversation* calls a Global Conversation or a Collaboration. Conversation, participant and message-flow *associations* map the inside of a referenced diagram onto the outer one. A conversation node has two or more participants.

**Correlation (8.4.2).** Routes a message to the right process instance. See section 10.

**Resources and services (8.4.12, 8.5, 10.3.1 to 10.3.4).** See section 12.

**Supporting concepts.** Signal, Error and Escalation (named payload root elements), Expression and Formal Expression, Auditing and Monitoring (hooks whose content is out of scope), Rendering, Documentation, Extension, Relationship, Import.

---

## 5. Diagram kinds (7.2.1, 7.4, 9.5, 12.2.3.2)

**The standard does not give a closed list of diagram types.** It names three sub-models of an end-to-end model: *Processes* (orchestration: private non-executable, private executable, public), *Choreographies*, and *Collaborations*, which may include processes and choreographies and "a view of Conversations". Section 7.4 lists eleven example kinds of business process model and leaves their combination to tool vendors. The conformance clause speaks of Process, Collaboration, Conversation and Choreography diagrams, and Clause 7.6 uses the same names. BPMN DI (12.2.3.2) lets the root plane of a diagram point at a Process, Sub-Process, Ad-Hoc Sub-Process, Transaction, Collaboration, Choreography or Sub-Choreography.

This library uses the four conformance names. What each admits:

| Diagram | Admits | Excludes |
|---|---|---|
| **Process** | Tasks, sub-processes, call activities; events; gateways; sequence flows; data objects, data inputs and outputs, data stores, data associations; associations, groups, text annotations; pools and lanes when drawn as swimlanes (a private process sits in one pool); messages as decorators | Choreography activities. Message flows appear only when the process is shown inside a collaboration. |
| **Collaboration** | Two or more pools, each empty (black box) or holding a process (white box); message flows between pools or to flow objects in them; conversation nodes and links; choreographies drawn between pools; artifacts. All combinations of pools, processes and choreography are allowed. | Message flows between two objects in one pool; sequence flows across a pool boundary. Only one pool may be drawn without a boundary. |
| **Choreography** | Choreography tasks, sub-choreographies, call choreographies; a subset of events (section 7); constrained gateways (11.7); sequence flows; text annotations and groups; messages as decorators; participant bands. Inside a collaboration, pools are shown and the choreography sits between them. | Data objects and data stores, ordinary activities, data associations, pools and lanes of its own, lane sets. Message flows are not drawn. |
| **Conversation** | A particular use of a Collaboration diagram: pools (usually with no process), conversation nodes and conversation links; a conversation may be expanded into its message flows. | A choreography is usually not placed between the pools. Each link needs exactly one conversation node. |

A fifth item, the **BPMN DI diagram**, is the interchange form: shapes and edges on a plane, each referencing one model element, possibly partial. The standard defines no diagram names, frames, legends or title rules; text, color, size and lines belong to the modeler or the tool within the limits of 7.5.

---

## 6. Connection rules (7.6)

The standard states them as two tables with refinements in prose. The tables are in `language.yaml` under `relationships.connection_tables`. In both, a mark means "the row object may connect to the column object".

**Sequence flow (Table 7.3, 7.6.1).** Applies within a process diagram and a choreography diagram; in a choreography the activity rows and columns stand for choreography activities and sub-choreographies. Sources: start event, task, sub-process, gateway, intermediate event. Targets: task, sub-process, gateway, intermediate event, end event. Every source may reach every target. An end event is never a source and a start event is never a target. Pools, lanes, data objects, groups and text annotations cannot have sequence flows. The table is coarser than the prose; it does not separate boundary events, event sub-processes, link events or gateway types.

**Message flow (Table 7.4, 7.6.2).** Applies within a collaboration. Sources: pool, task, sub-process, throwing message intermediate event, message end event. Targets: message start event, pool, task, sub-process, catching message intermediate event. A message flow may not connect two objects in the same pool. Lanes, gateways, data objects, groups and text annotations cannot have message flows. The first column's marks in the printed table render with a different glyph from the others; the prose agrees that a start event may be a target (10.5.2), so all are read as "may connect".

**Refinements from the prose (selected).**
- Start event: no incoming sequence flow (except a start event attached to the boundary of an expanded sub-process), one or more outgoing, may receive message flows, never sends one.
- End event: at least one incoming sequence flow, none outgoing (same exception), never receives a message flow, may send one if its result is Message or Multiple.
- Intermediate event in normal flow: incoming and outgoing sequence flow (a link source event needs no outgoing flow); a message intermediate event has one incoming or one outgoing message flow, not both.
- Boundary event: no incoming sequence flow; outgoing flow required, except a Compensation boundary event, which has none and may have an association.
- Gateway: may have no message flows; must merge or split.
- Event Sub-Process: no incoming or outgoing sequence flows.
- Artifacts (association, group, text annotation): no sequence or message flows.
- Pool boundary: sequence flows cannot cross it; message flows can. Expanded sub-process boundary: inside objects cannot connect to outside objects.
- Data association: source and target are item-aware elements with matching item definitions or a transformation; without a transformation exactly one source.
- Conversation link: exactly one end is a conversation node.
- Conditional sequence flow out of an activity needs a mini-diamond and at least one other outgoing flow; out of a gateway it has no mini-diamond and the gateway must not be Parallel or Event-Based. A default flow comes from an Exclusive, Inclusive or Complex gateway or from an activity.

---

## 7. Which event types fit where

**Process events (Table 10.93, 10.5.5).** Thirteen event types (the ten definitions plus None, Multiple, Parallel Multiple) against eight positions: top-level start, interrupting and non-interrupting event sub-process start, intermediate catching, interrupting and non-interrupting boundary, intermediate throwing, and end. Highlights:

- Top-level start: None, Message, Timer, Conditional, Signal, Multiple, Parallel Multiple. Sub-process start (embedded or called): None only. Event sub-process start: Message, Timer, Escalation, Error, Compensation, Conditional, Signal, Multiple, Parallel Multiple; each interruptible except Error (always interrupting) and Compensation (no interrupting meaning).
- Intermediate: twelve types. In normal flow ten (all but Error and Cancel); on the boundary ten (all but None and Link).
- End: None, Message, Escalation, Error, Cancel, Compensation, Signal, Terminate, Multiple.
- Error and Cancel occur only on a boundary (Cancel only on a Transaction) and as end events; Compensation catches only at a boundary or an event sub-process start and throws in normal flow or at an end.

**Choreography events (Tables 11.6 to 11.8, 11.6).** A choreography allows far fewer: start (None, Timer, Conditional, Signal, Multiple of signals or timers), intermediate in normal flow (None, Timer, Conditional, Link, Signal catch, Multiple), boundary of a choreography activity (Message on a choreography task's receiver band, Timer, Conditional, Signal, Cancel, Compensation, Multiple), inside an event-based gateway (Timer, Conditional, Signal), and end (None, Terminate). The cells are in `language.yaml` under `event_placement`.

---

## 8. Processes and their kinds (Clause 10.1, 10.2)

A process has a graph of flow elements. Start and end events are optional, but if either exists the other must too, and the pairing holds per process level (10.5.2, 10.5.3). Without a start event, the process begins implicitly with no trigger; without an end event, it ends implicitly with no result.

- *Private, non-executable.* Documents internal behavior at the modeler's chosen detail.
- *Private, executable.* Modeled to be executed under Clause 13. Extra rules apply (see `execution.md`).
- *Public.* Only the externally visible interaction. Not executable.

A process may be reused through a Call Activity, which can also call a Global Task. A Call Activity's I/O specification has to match the called element's data inputs, outputs and sets exactly (10.3.6). A process can be instantiated by a start event, an instantiating Event-Based Gateway or a Receive Task with `instantiate` set and no incoming sequence flow.

### 8.1 Sub-processes

An expanded sub-process defines a scope; objects inside do not connect to objects outside (except through boundary-attached start and end events). An Embedded sub-process must not define data inputs and outputs directly. An Event Sub-Process has no incoming or outgoing sequence flow, exactly one start event with a defined trigger, and at most one interrupting handler per event definition. A Transaction may have a Cancel boundary event; a Cancel end event is valid only inside a Transaction. An Ad-Hoc sub-process must contain activities and may contain data objects, flows, associations, gateways and intermediate events, but no start events, end events, conversations or choreography activities.

### 8.2 Compensation

Compensation reverses effects of activities that already completed. An activity can be compensated only if it has a Compensation boundary event or contains a Compensation Event Sub-Process, and it must be visible from the throwing event (10.5.3, 10.5.4). A Compensation boundary event has no outgoing sequence flow; it may have an association to its handler, which is an activity with `isForCompensation`. See `execution.md` for the runtime behavior.

---

## 9. Collaboration and pools (Clause 9)

A collaboration lets processes of different participants interact. A pool may hold a process or be empty. A black-box pool has no sequence flows; message flows attach to its boundary. One and only one pool may be drawn without a boundary. A participant's multiplicity has a minimum (default 0) and a maximum that is at least 1 and at least the minimum. A lane that represents a conversation requires its flow elements to send and receive as part of that conversation (9.6). A collaboration that contains a choreography must agree with it on whether it is closed (9.5.8).

---

## 10. Correlation (8.4.2)

Correlation associates a message with an ongoing conversation, so that a long-running process instance receives the right message. There are two non-exclusive mechanisms.

- *Key-based.* A *Correlation Key* is a composite of *Correlation Properties*. Each property has one or more *retrieval expressions*, one per message in the conversation (a path expression plus the message it applies to). The first send or receive must populate at least one key; later messages are matched on the key value, and a follow-up that derives an already set key must match.
- *Context-based.* A process can attach a *Correlation Subscription* (a reference to a key) with *Property Bindings* that read the process's data objects and properties; the subscription is re-evaluated when the data changes.

Keys apply through containers: collaborations, choreographies, conversation nodes and choreography activities; calling a collaboration or choreography counts as containment. Where the PDF's table for Correlation Subscription differs from the schema, the schema is followed.

---

## 11. Choreography details (Clause 11)

- The initiator of a choreography activity must have taken part (as initiator or receiver) in the previous choreography activity (11.5.6).
- Loop markers (loop, parallel or sequential multi-instance) match the activity's loop type, one marker at a time. A return message icon is lightly filled and the initiating one is unfilled.
- Gateways (11.7): for an enforceable choreography, conditions must be formal expressions; the data must come from an earlier message seen by every participant affected, and they must share the same understanding of it. Event-Based Gateway: no message intermediate events, timers and signals allowed. Parallel Gateway: the senders after the gateway must have been involved in all activities before it. Gateways may be chained without activities between them if the participant constraints hold.
- Tables 11.6 to 11.8 restrict events (section 7).
- 7.3.2 says a choreography task involves two participants; 11.5.1 and Table 11.1 say two or more bands. This library follows the latter.

---

## 12. Resources and services

**Resources (8.4.12, 10.3.1 to 10.3.4).** A *Resource* is an abstract definition (name, parameters), not a list of user ids, that many activities can reuse. A *Resource Parameter* (name, type, required flag) is bound per activity by a *Resource Parameter Binding*. A *Resource Role* is attached to an activity or process and points to a resource or carries a *Resource Assignment Expression* that returns user or group entities, not both. Subtypes: *Performer* (the responsible resource), *Human Performer*, *Potential Owner* (may claim a User Task and become its actual owner). Runtime attributes of a User Task (actual owner, priority) are reported, not modeled.

**Services (8.5).** An *Interface* has a name and at least one *Operation*. An *Operation* has a name, exactly one in-message, at most one out-message and zero or more errors. An *End Point* is an empty extension point for addresses. Participants list the interfaces and end points they support; processes and global tasks list the interfaces they provide. Service, Send and Receive tasks and message event definitions name an operation, which is mandatory for message events in executable processes.

---

## 13. Execution semantics (Clause 13)

Required for Process Execution Conformance. It describes orchestration only, not choreography. The detailed material, the lifecycle, the token rules and handling of events and compensation, is in `execution.md`.

---

## 14. The WS-BPEL mapping (Clause 14)

Maps one orchestration process (one pool) to one WS-BPEL 2.0 process. There is no mapping of diagrams, collaborations, choreographies or conversations. A syntactic mapping covers block-structured models; a semantic mapping lets other sound models map if the observed behavior is the same. See `execution.md`.

---

## 15. Diagram interchange and depiction (Clause 12, Annex B)

BPMN DI records where shapes sit, not what they mean. A shape, edge or plane references exactly one model element; an element is not drawn twice in one diagram, except participant bands in a choreography; the order of a plane's children is the z-order. A shape or edge with no valid model element is not drawn. Edges have two or more waypoints. Labels are optional; a label's presence means it is visible.

Clause 12.3 is a catalog of what each element depicts as, selected by the element's class plus attribute values (a "depiction resolution"). It is a set of conventions for a renderer, not validation. The resolution keys are recorded in `language.yaml` under `conventions`. The catalog has table defects that the library does not treat as exact (section 17).

---

## 16. Annexes

- *Annex A, changes from 1.2* (informative): new Choreography and Conversation diagrams, non-interrupting events, event sub-processes, a formal metamodel, XMI and schema interchange. Reference Tasks were replaced by Global Tasks.
- *Annex B, Diagram Interchange* (non-normative): the Diagram Common and Diagram Interchange packages that back BPMN DI. It refers to BPMN DI as "Clause 13"; it is Clause 12. The design principle is to interchange only graphics the user controls (positions, routing points), not the ones the language fixes.
- *Annex C, Glossary* (informative): about fifty terms. Some differ from the normative clauses (it uses "Abstract Process" for the public process and lists Link among end-event results); the normative clauses govern.
- There is no Annex D.

---

## 17. Inconsistencies in the standard, and how this library reads them

Policy (settled): where the standard contradicts itself, follow its machine-readable model (schema or CMOF); where that is silent, follow the stricter table; where there is no table, see the notes below. The ids refer to `rules.md`.

| Where | Inconsistency | Reading |
|---|---|---|
| 10.3.5 against Table 10.86 | The text lists seven event sub-process start triggers; the table lists nine (adds Timer and Parallel Multiple) | The table governs (BPMN-EVT-025) |
| Table 10.86 against Table 10.93 | Compensation is non-interrupting in one and in the interrupting column of the other; the standard says it has no interrupting meaning | Treated as having no interrupting meaning |
| 7.3.2 against 11.5.1 | Two participants, or two or more | Two or more (BPMN-CHOR-009) |
| Schema against Table 10.50 | Transaction method values carry a `##` prefix in the schema | The schema's values |
| 10.5.6 | The text calls handlers with `cancelActivity` false "interrupting" under the non-interrupting heading | Typographical; `cancelActivity` false means non-interrupting |
| 7.3 and Table 7.1 against 8.4.1 | Association is a connecting object, and an artifact | The schema makes it an Artifact |
| Clause 13.1 against 2.4 | Clause 13 is said to be not required for BPEL Process Execution Conformance, which 2.4 defines as including Process Execution | 2.4 governs (BPMN-INST-001) |
| 13.2 against 13.3.1 and 13.3.4 | A global process is required to have no empty start event and no activity without incoming flow, yet both clauses describe them as normal entry points | Treated as guidance (BPMN-INST-007) |
| 13.2 against 13.5.6 | Start events are alternatives, or all must be visited | Both recorded; the conflict is flagged (BPMN-INST-016) |
| 13.5.3 against Table 10.92 | Non-canceling boundary events limited to four types, or six | The table (six) governs |
| 13.4.4 against 10.6.6 | Message triggers only, or also Signal, Timer and Conditional, for a parallel instantiating event-based gateway | The narrower rule applies to executable processes (BPMN-EXGW-007); the general rule stays |
| 13.5.5 | Compensation per instance of a multi-instance sub-process: once each, or once for all | Flagged; guidance only (BPMN-COMP-008) |
| 13.5.5 | Relies on a `compensable` sub-process attribute that no table or schema defines | Ignored (BPMN-COMP-005) |
| 13.3.7, 14.2.2 against the schema | `noneEvent`, `oneEvent`, `testTime`, `activationExpression` against `noneBehaviorEventRef`, `oneBehaviorEventRef`, `testBefore`, `activationCondition` | The schema's names |
| 13.3.2 | Nested activities "not in Ready, Active or a final state" are terminated; read literally this excludes the ones that need terminating | Read as those in Ready or Active |
| 13.3.2 against 13.5.4 | "Should" or flat prohibition on creating new non-interrupting handlers while Completing | The stricter (BPMN-LIFE-011) |
| 14.2 against 14.3 | BPEL 2.0 `if` against BPEL 1.1 `switch`; a stale reference to 15.1 | Both recorded (BPMN-BPEL-030, BPMN-BPEL-036) |
| Table 12.22 | Lists a catching Escalation in normal flow (Table 10.93 does not allow it), a non-interrupting boundary Timer as an intermediate catch event, a catching Signal with a Message definition, and names the schema lacks | Table 10.93 and the schema govern |
| 12.3 | Table numbers repeat (12.8 twice); the table captioned 12.15 is the expanded Transaction | Noted |
| 12.3 | For Ad-Hoc, Transaction and Call Activity, both the collapsed and expanded table accept an absent `isExpanded` | Absent means collapsed, as for the plain sub-process |
| 12.3 | Initiating rows accept "unspecified or greater than 1"; non-initiating rows differ; one table omits the `parallelMultiple` false condition; enumeration spelling | The schema's enumeration values; conditions completed |
| Table 8.40 and others against the schema | Correlation Subscription structure, Resource Role exclusivity, Human Performer's `peopleAssignment`, Operation's "input" for an output, an undefined "SubscriptionProperty" | The schema governs |
| Annex B, Annex C | Clause number; vocabulary | Normative clauses govern |
