# BPMN 2.0.2 rules

Generated from `language.yaml` (`constraints`). Do not edit by hand; change the language file and regenerate.

Each rule has a stable id of the form `BPMN-<CAT>-nnn`. The number never changes once assigned. A rule that is retired keeps its id and is marked withdrawn rather than reused.

The file holds 263 rules: 96 from the modeling clauses (2 to 12 and 15), and 167 from the execution semantics, the WS-BPEL mapping, correlation, resources, services and the annexes.

## Strength

| Strength | Meaning | Treatment |
|---|---|---|
| must | The standard states it as a requirement ("must", "shall", "cannot", "only"), or it is a structural limit the schema or a table fixes. A model that breaks it is not well formed. | An error. |
| should | The standard gives it as guidance, or states it in a way that conflicts with another clause and the rule's text says how the conflict was read. | A warning. |
| note | An explanation, option or statement of runtime behavior that is recorded for completeness. | Advice only. |

Where the standard contradicts itself, the library follows its machine-readable model (schema or CMOF); where that is silent, the stricter table; where there is no table, the notes in `standard.md` section 17 say what was done. A rule graded `should` for that reason says so in its text.

## Applies when

A rule with no `applies_when` applies to every model. Otherwise:

| Value | The rule is checked when |
|---|---|
| `executable` | the process is marked executable (`isExecutable` is true). Rules from the execution clauses and the attribute rules that matter only for execution. |
| `bpel-mapping` | the mapping to WS-BPEL is requested for the process. The standard defines no flag for this; whoever applies the rules supplies the trigger. |

## Checkable

| Value | Meaning |
|---|---|
| `static` | a property or relationship of elements that a validator reading the saved model can check |
| `partial` | checkable for the structure, in simple cases, or only with graph analysis (soundness, reachability, block structure) |
| `runtime` | describes running state; needs a live instance |
| `none` | not a property of a model (a requirement on tools, drawing, or explanation) |

A rule marked `basis: inferred` in `language.yaml` is our inference from absence or from combining clauses, not a sentence of the standard. Rules whose strength is `must` and whose `checkable` is `static` are the candidates for machine checks; the rest are review guidance. Drawing sentences that the standard words as requirements carry a `see_conventions` pointer to the drawing rules in `language.yaml`.

## Categories

| Category | Name | Covers | Rules |
|---|---|---|---|
| CONN | Connection and containment | Which objects may connect to which, what pools, lanes, conversation nodes and choreography activities may hold, and the structural limits on collaborations and calls. | 24 |
| EVT | Events | Start, intermediate, boundary and end events: the flows they take, the triggers allowed, link pairing, event sub-processes and compensation visibility. | 27 |
| ACT | Activities and processes | Flow conditions on activities, default flows, instantiation, loops, ad-hoc contents and the public process. | 11 |
| DATA | Data | Data objects, inputs and outputs, I/O specifications and data associations. | 4 |
| GATE | Gateways | Merge and split, direction, markers, and the configuration of event-based and complex gateways. | 9 |
| CHOR | Choreography | Choreography activities, their initiator, markers, events and gateways. | 9 |
| CONF | Conformance, notation and interchange | Obligations on tools, notation extension, interchange files and the diagram-interchange references. | 12 |
| INST | Execution scope and process instances | What Clause 13 covers, and how a process instance starts, runs and completes. | 16 |
| LIFE | Activity behavior and life cycle | Input and output sets, the life-cycle states, and what each task kind does when it runs. | 23 |
| SUBP | Sub-process, ad-hoc and loop behavior | Sub-process instantiation, ad-hoc sub-processes, standard loops and multi-instance. | 22 |
| EXGW | Gateway execution | How tokens move through parallel, exclusive, inclusive, event-based and complex gateways. | 12 |
| EXEV | Events at runtime | Catching, boundary, event sub-process and end event behavior. | 10 |
| COMP | Compensation and transaction | Compensation handlers and their order, and the three outcomes of a transaction. | 16 |
| BPEL | WS-BPEL mapping | What a process must meet to be mapped, and how constructs map. | 36 |
| CORR | Correlation | Key-based and context-based routing of messages to instances. | 12 |
| RSRC | Resources and roles | Resources, parameters, resource roles and performers. | 9 |
| SERV | Services | Interfaces, operations, end points and who supports them. | 5 |
| ANNX | Annexes | The informative annexes. | 6 |

Section references are to the clauses, tables and annexes of OMG formal/13-12-09; "p." gives the printed page.

## CONN: Connection and containment

| Id | Strength | Applies when | Checkable | Rule | Section |
|---|---|---|---|---|---|
| BPMN-CONN-001 | must |  | static | A message flow must connect two separate pools (the pool boundary or objects inside); it must not connect two objects within the same pool. | 9.4 p. 119; 10.3 p. 152; 10.5.2 to 10.5.4 |
| BPMN-CONN-002 | must |  | static | A sequence flow has exactly one source and one target, drawn from events, activities (process) or choreography activities (choreography), and gateways. | 8.4.13 p. 95 |
| BPMN-CONN-003 | must |  | static | Sequence flows cannot cross a pool boundary; they may cross lane boundaries. | 7.6.1 p. 40; 9.3 p. 111 |
| BPMN-CONN-004 | must |  | static | Within an expanded sub-process, objects cannot connect to objects outside it (except boundary-attached start/end events). | 7.6.1 p. 40; 10.5.2; 10.5.3 |
| BPMN-CONN-005 | must |  | static | An artifact (association, group, text annotation) must not be the source or target of a sequence flow or a message flow. | 8.4.1 pp. 64 to 65 |
| BPMN-CONN-006 | must |  | static | Pool, lane, data object, group and text annotation cannot have sequence flows; lane, gateway, data object, group and text annotation cannot have message flows. | 7.6.1 to 7.6.2 pp. 41 to 42 |
| BPMN-CONN-007 | must |  | static | A message flow's source and target are pools/participants, activities or events only. | 9.4 p. 122; Table 9.8 |
| BPMN-CONN-008 | must |  | static | A black-box pool has no sequence flows; message flows attach to its boundary. | 9.3 p. 111 |
| BPMN-CONN-009 | note |  | static | A pool contains one process; a private process is fully inside one pool. | 9.3 p. 111; 10.2.1.1 p. 148 |
| BPMN-CONN-010 | must |  | static | A Collaboration's `choreographyRef` is not applicable to a Choreography (a choreography cannot reference another choreography). | Table 9.1 p. 109 |
| BPMN-CONN-011 | must |  | static | Choreography Activities must not be flow elements of a Process; Activities, Data Associations and Data Objects must not be flow elements of a Choreography. | Table 8.45 p. 87 |
| BPMN-CONN-012 | must |  | static | LaneSets are not used in Choreographies or Sub-Choreographies. | Table 8.45 p. 87; 11.8.2 p. 362 |
| BPMN-CONN-013 | must |  | static | Pools and lanes are not used inside a choreography; participants appear as bands. | 11.8.2 p. 362 |
| BPMN-CONN-014 | must |  | static | Neither Data Objects nor Data Stores are used in a Choreography. | 11.3 p. 319 |
| BPMN-CONN-015 | must |  | static | A Conversation Link must connect to exactly one conversation node; if one end is not a conversation node the other must be. | Table 9.13 p. 133 |
| BPMN-CONN-016 | must |  | static | A GlobalConversation must not contain conversation nodes; a GlobalChoreographyTask must not contain flow elements. | 9.5.5 p. 131; 11.5.4 p. 335 |
| BPMN-CONN-017 | must |  | static | A Call Conversation must not call a Choreography or a GlobalChoreographyTask; a Call Activity calls only a Process or a GlobalTask. | Tables 9.12, 10.23 pp. 131, 185 |
| BPMN-CONN-018 | must |  | partial | A Call Activity's I/O specification must exactly match the called element's data inputs, outputs, input sets and output sets. | 10.3.6 p. 184 |
| BPMN-CONN-019 | must |  | static | A conversation node has two or more participants; a Choreography Activity has two or more participants. | Table 9.10 p. 128; Table 11.1 p. 322 |
| BPMN-CONN-020 | must |  | static | If a Collaboration contains a Choreography, `isClosed` must be the same in both. | 9.5.8 p. 136 |
| BPMN-CONN-021 | must |  | static | All lanes in one LaneSet must use a partition element of the same type. | 10.8 p. 307 |
| BPMN-CONN-022 | must |  | partial | A lane that represents a conversation: its flow elements must send and receive as part of that conversation. | 9.6 p. 136 |
| BPMN-CONN-023 | must |  | none | One and only one pool may be drawn without a boundary; every other pool must have one. | 9.3 p. 111 |
| BPMN-CONN-024 | must |  | static | Participant multiplicity: maximum is at least 1 and at least the minimum; minimum defaults to 0. | Table 9.5 p. 117 |

## EVT: Events

| Id | Strength | Applies when | Checkable | Rule | Section |
|---|---|---|---|---|---|
| BPMN-EVT-001 | must |  | static | A Start Event is optional. If an End Event exists there must be at least one Start Event, and if a Start Event exists there must be at least one End Event; the pairing applies per process level. | 10.5.2 p. 238; 10.5.3 p. 246 |
| BPMN-EVT-002 | must |  | static | A Start Event must not be a sequence-flow target (exception: boundary-attached start of an expanded sub-process); it must be a source; all its outgoing flows have no condition. | 10.5.2 p. 244 |
| BPMN-EVT-003 | must |  | static | A Start Event must not be a message-flow source; it may be a target (each incoming message flow is one trigger). | 10.5.2 p. 245 |
| BPMN-EVT-004 | must |  | static | An End Event must be a sequence-flow target; it must not be a source (exception: boundary-attached end of an expanded sub-process). | 10.5.3 p. 248 |
| BPMN-EVT-005 | must |  | static | An End Event must not be a message-flow target; with outgoing message flows its result must be Message or Multiple (Multiple if more than one). | 10.5.3 p. 248 |
| BPMN-EVT-006 | must |  | none | If no Start Event is used, the implicit start has no trigger; if no End Event is used, the implicit end has no result. | 10.5.2 p. 238; 10.5.3 p. 246 |
| BPMN-EVT-007 | must |  | static | An Intermediate Event in normal flow must be a sequence-flow target and a source (a Link source event need not have an outgoing flow). | 10.5.4 p. 258 |
| BPMN-EVT-008 | must |  | static | A boundary Intermediate Event must not be a sequence-flow target and must be a source. A Compensation boundary event must not have an outgoing sequence flow (an association is allowed). | 10.5.4 p. 258 |
| BPMN-EVT-009 | must |  | static | Boundary event triggers allowed: Message, Timer, Error, Escalation, Cancel, Compensation, Conditional, Signal, Multiple, Parallel Multiple. None and Link must not be boundary events; Error and Cancel must not be used in normal flow. | 10.5.4 pp. 249, 257 to 258; 10.5.5 p. 262 |
| BPMN-EVT-010 | must |  | static | A Cancel boundary event may be attached only to a Transaction sub-process; a Cancel End Event may be used only within a Transaction sub-process. | 10.5.4 p. 257; 10.5.5 p. 261 |
| BPMN-EVT-011 | must |  | static | `cancelActivity` possible values: true or false for Message, Timer, Escalation, Conditional, Signal, Multiple; always true for Error and Cancel; not applicable to Compensation. | Table 10.92 p. 257 |
| BPMN-EVT-012 | must |  | static | Link events: a source link must have a matching target link with the same name; many sources may share one target; a source link must not have multiple targets; a link event must not be both target and source of a flow; a link pair stays within one process level. | 10.5.4 pp. 252, 258 |
| BPMN-EVT-013 | must |  | static | A message intermediate event has one incoming or one outgoing message flow, not both. | 10.5.4 p. 259 |
| BPMN-EVT-014 | must |  | static | A Compensation Start Event must not be used in a top-level process; it may start an Event Sub-Process. | 10.5.5 p. 262 |
| BPMN-EVT-015 | must |  | static | The None Start Event may start a top-level process or a sub-process but must not start an Event Sub-Process; a None catching intermediate event is normal-flow only. | 10.5.5 p. 271 |
| BPMN-EVT-016 | must |  | static | Sub-process (embedded or called) start events are None only. | Table 10.85 p. 241 |
| BPMN-EVT-017 | must |  | partial | A Conditional Start Event's condition must not refer to the process instance's data (it does not exist yet). | Table 10.84 p. 240 |
| BPMN-EVT-018 | must | executable | static | For executable processes: a Conditional event needs a formal expression; a Message event needs its Message; timer attributes (`timeDate`, `timeCycle`, `timeDuration`) are mutually exclusive and ISO-8601. | 10.5.5 pp. 264, 270, 273 |
| BPMN-EVT-019 | must |  | static | A Parallel Multiple event must set `parallelMultiple=true`. | 10.5.5 p. 271 |
| BPMN-EVT-020 | must | executable | partial | A throw/catch event carrying data needs one data input (throw) or data output (catch) per event definition, with an equivalent item definition. | 10.5.1 p. 234; 10.4.1 p. 217 |
| BPMN-EVT-021 | must |  | partial | An activity must have a boundary Compensation event or contain a Compensation Event Sub-Process to be compensated; the activity must be visible from the compensation throw event. | 10.5.3 p. 247; 10.5.4 p. 251 |
| BPMN-EVT-022 | must |  | static | For an interrupting event (Error, Escalation, Message, Signal, Timer, Conditional, Multiple, Parallel Multiple), only one Event Sub-Process for the same event declaration may be modeled; this excludes further non-interrupting handlers for it. | 10.5.6 p. 278 |
| BPMN-EVT-023 | should |  | partial | The flow leaving a non-interrupting boundary event or event sub-process runs in parallel; care must be taken when it merges into the main flow; typically it ends in its own End Event. | 10.5.6 p. 276 |
| BPMN-EVT-024 | must |  | static | An Event Sub-Process must not have incoming or outgoing sequence flows; must have exactly one Start Event; the start must have a defined trigger. | 10.3.5 p. 174; 10.5.2 p. 241 |
| BPMN-EVT-025 | note |  | none | The standard's text on event sub-process start triggers (10.3.5) lists seven, while Table 10.86 lists nine (it adds Timer and Parallel Multiple). The table governs. | 10.3.5 p. 174 vs p. 241 (see section 7) |
| BPMN-EVT-026 | must |  | none | Throwing events use a dark (filled) marker, catching events an unfilled marker; Start events are thin, End events thick, Intermediate events double. | 7.5 p. 39; 10.5.2 to 10.5.4 |
| BPMN-EVT-027 | note |  | runtime | If an Event Sub-Process inline handler and a boundary event handle the same definition: re-throw triggers the boundary event; otherwise the activity completes normally. | 10.5.6 pp. 278 to 279 |

## ACT: Activities and processes

| Id | Strength | Applies when | Checkable | Rule | Section |
|---|---|---|---|---|---|
| BPMN-ACT-001 | must |  | static | A conditional outgoing flow from an activity needs at least one other outgoing flow; a conditional flow from a gateway has no mini-diamond; a source gateway must not be Parallel or Event-based. | 8.4.13 p. 95 |
| BPMN-ACT-002 | should |  | static | A default flow has no condition (any condition is ignored) and is allowed only from Exclusive, Inclusive or Complex gateways or from an activity. | 8.4.13 p. 96; Table 10.3 p. 150 |
| BPMN-ACT-003 | note |  | static | An activity with no incoming flow is instantiated with the process (exceptions: compensation activities, event sub-processes); an activity with no outgoing flow ends a path. | 10.3 p. 151 |
| BPMN-ACT-004 | must | executable | static | A repeated activity needs `loopCharacteristics` when the process is executable; `startQuantity` and `completionQuantity` are at least 1. | Table 10.3 p. 150 |
| BPMN-ACT-005 | must |  | static | A Receive Task that instantiates the process must have `instantiate=true` and no incoming sequence flow. | 10.3.3.1 p. 159 |
| BPMN-ACT-006 | note |  | none | A User Task is not a Manual Task: a Manual Task is not tracked by an engine; both show a human icon. | 10.3.4 p. 163 |
| BPMN-ACT-007 | must |  | none | Border styles are reserved: thick for Call Activity, dotted for Event Sub-Process, double for Transaction; none are allowed on a Task. | 10.3.3 p. 154; 10.3.5 p. 171 |
| BPMN-ACT-008 | must |  | none | Sub-process markers: loop and multi-instance cannot be shown together; markers are grouped and centered at the bottom. | 10.3.5 p. 172 |
| BPMN-ACT-009 | must |  | static | Ad-hoc sub-process: must contain activities; may contain data objects, sequence flows, associations, data associations, groups, message flows, gateways, intermediate events; must not contain start events, end events, conversations or choreography activities. | 10.3.5 p. 181 |
| BPMN-ACT-010 | must | executable | static | Multi-instance: `loopCardinality` or `loopDataInput` must be specified. | Table 10.29 p. 191 |
| BPMN-ACT-011 | must | executable | static | A public process is not executable (value may not be true). In an executable process `isImmediate` on a flow may not be false. | Table 10.1 p. 146; Table 8.51 p. 97 |

## DATA: Data

| Id | Strength | Applies when | Checkable | Rule | Section |
|---|---|---|---|---|---|
| BPMN-DATA-001 | must |  | static | An Embedded Sub-Process must not define Data Inputs and Outputs directly. | 10.4.1 p. 210 |
| BPMN-DATA-002 | must | executable | static | Every I/O specification defines at least one InputSet and one OutputSet. | Table 10.58 p. 212 |
| BPMN-DATA-003 | must |  | static | A data association's source and target are item-aware elements with the same item definition, or it has a transformation; with no transformation exactly one source. A data input or output directly in a top-level process is not a data-association target/source. | 10.4.1 pp. 212, 214, 220 |
| BPMN-DATA-004 | must |  | static | Data Objects are contained in a Process or Sub-Process; Properties are contained in a flow element and not drawn; only processes, activities and events may hold properties. | 10.4.1 pp. 204, 208 |

## GATE: Gateways

| Id | Strength | Applies when | Checkable | Rule | Section |
|---|---|---|---|---|---|
| BPMN-GATE-001 | must |  | static | A Gateway must merge or split: it needs multiple incoming or multiple outgoing flows. | 10.6.1 p. 289 |
| BPMN-GATE-002 | must |  | static | `gatewayDirection`: unspecified may have both; mixed must have both multiple in and multiple out; converging must have multiple in and not multiple out; diverging must have multiple out and not multiple in. | 10.6.1 p. 289 |
| BPMN-GATE-003 | note |  | static | A gateway with no incoming flow and no Start Event performs its divergence at instantiation; the only gateway that may start a process without incoming flow is an instantiating Event-Based Gateway. | 10.6.1 p. 288; 10.5.6 p. 275 |
| BPMN-GATE-004 | must |  | none | Inclusive gateway uses a circle marker; parallel a plus; complex an asterisk; exclusive an "X" marker that is optional but a diagram should be consistent. | 10.6.2 to 10.6.5 |
| BPMN-GATE-005 | must |  | static | An Event-Based Gateway has two or more outgoing flows with no condition. | 10.6.6 p. 296 |
| BPMN-GATE-006 | must |  | static | Event-Based Gateway targets: intermediate events or Receive Tasks (not both kinds together); receive tasks have no attached intermediate events; valid event triggers are Message, Signal, Timer, Conditional and Multiple of those; target elements have no other incoming flows. | 10.6.6 p. 297 |
| BPMN-GATE-007 | must |  | static | An Event-Based Gateway that instantiates a process has no incoming flows; `eventGatewayType=Parallel` is allowed only when `instantiate=true`; parallel instantiating messages share correlation. | 10.6.6 p. 298 |
| BPMN-GATE-008 | must | executable | runtime | Complex gateway: no token produced on reset; each outgoing flow should get a token on activation or on reset, not both. | 10.6.5 p. 295 |
| BPMN-GATE-009 | note | executable | runtime | If no default and no condition is true on an Exclusive or Inclusive gateway, a runtime exception occurs; an inclusive decision should be designed so at least one path is taken. | 10.6.2 p. 290; 10.6.3 p. 291 |

## CHOR: Choreography

| Id | Strength | Applies when | Checkable | Rule | Section |
|---|---|---|---|---|---|
| BPMN-CHOR-001 | must |  | partial | The initiator of a choreography activity must have been involved (as initiator or receiver) in the previous choreography activity. | 11.5.6 p. 336 |
| BPMN-CHOR-002 | must |  | none | The non-initiating participant band must be lightly shaded; a return message icon is light-filled and the initiating message icon unfilled. | 11.5.1 pp. 323, 325 |
| BPMN-CHOR-003 | must |  | none | Choreography task/sub-choreography markers (loop, parallel or sequential multi-instance) must match `loopType`; only one marker at a time. | 11.5.1 pp. 325 to 326 |
| BPMN-CHOR-004 | must |  | static | A choreography allows only the event types and positions of Tables 11.6 to 11.8, recorded in event_placement.choreography. | 11.6 pp. 339 to 344 |
| BPMN-CHOR-005 | must |  | partial | Choreography gateways: for an enforceable choreography conditions must be formal expressions; data must come from an earlier message seen by all participants affected; participants affected must share the same understanding of the data. | 11.7.1 p. 344 |
| BPMN-CHOR-006 | must |  | static | Event-Based Gateway in a choreography: no message intermediate events; timers and signals may be used; no other event types. | 11.7.2 p. 349 |
| BPMN-CHOR-007 | must |  | partial | Parallel gateway: the senders after the gateway must be involved in all choreography activities before it. | 11.7.4 p. 358 |
| BPMN-CHOR-008 | must |  | partial | Gateways may be chained without choreography activities between them if the participant constraints before and after the chain hold. | 11.7.6 p. 361 |
| BPMN-CHOR-009 | note |  | none | The notation overview (7.3.2) says a Choreography Task involves two participants, while 11.5.1 and Table 11.1 say two or more bands. The latter governs (see BPMN-CONN-019). | pp. 30, 322 to 323 (see section 7) |

## CONF: Conformance, notation and interchange

| Id | Strength | Applies when | Checkable | Rule | Section |
|---|---|---|---|---|---|
| BPMN-CONF-001 | must |  | none | An implementation that draws BPMN diagrams shall use the standard's shapes, icons and markers; size, color, line style and label position are flexible except where stated. | 2.2.3 p. 8; 7.5 p. 39 |
| BPMN-CONF-002 | must |  | none | Permitted extensions: new markers; new artifact shapes that do not conflict; colors with their own semantics; line styles that do not conflict. An extension must not change a shape (square to triangle, rounded to square). | 2.2.3 p. 8 |
| BPMN-CONF-003 | must |  | none | The line styles of sequence flows, message flows and text associations must not be modified or duplicated. | 7.5 p. 40 |
| BPMN-CONF-004 | must |  | none | Extension attributes must not contradict BPMN semantics; the footprint of events, activities and gateways must not be altered; a mandatory extension must be understood, an optional extension may be ignored. | 7.7 p. 42 |
| BPMN-CONF-005 | must |  | none | Structural conformance: implementations must conform to the connection rules; conditional rules must match the attribute values. | 2.2.4 p. 8 |
| BPMN-CONF-006 | must |  | none | For every mandatory attribute, a conforming tool must provide some way to create and view its values for every element that has it. | 2.2.6 p. 9 |
| BPMN-CONF-007 | must |  | none | A conforming tool is not required to support optional features; if it supports one it must support it as specified. | 2.2.7 p. 9 |
| BPMN-CONF-008 | should |  | none | Incomplete models may be interchanged; importers should disregard missing "required" XSD attributes and reduce lower bounds. | 15.1 p. 475 |
| BPMN-CONF-009 | must |  | static | The root of an interchange file is `definitions`; each file declares a `targetNamespace`; the file set must be self-contained. | 15.3.1 p. 475 |
| BPMN-CONF-010 | must |  | static | In BPMN DI, a shape, edge or plane references exactly one model element; an element is not depicted twice in one diagram (except participant bands in a choreography); z-order is the document order. | 12.2.1 p. 368 |
| BPMN-CONF-011 | note |  | none | Tokens are a thinking aid; modeling and execution tools need not implement tokens. A token does not travel along a message flow. | 7.2 p. 25 |
| BPMN-CONF-012 | must |  | none | A tool may claim a sub-class (Descriptive, Analytic, Common Executable) only if it supports every element in it and every attribute listed for each element. | 2.2.1 p. 3 |

## INST: Execution scope and process instances

| Id | Strength | Applies when | Checkable | Rule | Section |
|---|---|---|---|---|---|
| BPMN-INST-001 | note | executable | none | Clause 13 is stated to be required only for Process Execution Conformance and Complete Conformance, and not for Process Modeling, Choreography or BPEL Process Execution Conformance. Clause 2.4 defines BPEL Process Execution Conformance as Process Execution plus the mapping, so for that type the clause applies; this file follows 2.4. | 13.1 (p. 425) |
| BPMN-INST-002 | note | executable | static | Ten elements are non-operational (Manual Task, Abstract Task, DataState, IORules, Ad-Hoc Process, physical ItemDefinitions, the two WhileExecuting set attributes, Process isClosed, SequenceFlow isImmediate); a Process Execution implementation may ignore them and may extend them optionally. | 13.1 (p. 425) |
| BPMN-INST-003 | note | executable | none | Tokens are a thinking aid for defining behavior; tools need not implement tokens. | 13.3.1 (p. 427) |
| BPMN-INST-004 | note | executable | none | Execution semantics are described informally in text per element: operational semantics, exception issues, workflow patterns supported. | 13.1 (p. 425) |
| BPMN-INST-005 | must | executable | runtime | Each occurrence of a Start Event creates a new Process instance, unless the Start Event shares a Conversation with other Start Events; then a new instance is created only if none exists for that Conversation's correlation information. | 13.2; 13.5.1 (pp. 426; 439) |
| BPMN-INST-006 | must | executable | runtime | A later Start Event occurrence with the same correlation information as the one that created an instance is routed to that instance. | 13.2 (p. 426) |
| BPMN-INST-007 | should | executable | static | A global Process should have neither an empty Start Event nor a Gateway or Activity without incoming Sequence Flows (the Event-Based Gateway is the exception). 13.2 words this as a requirement, but 13.3.1, 13.3.4 and BPMN-ACT-003 describe both as normal entry points, so this file treats it as guidance. | 13.2 (p. 426) |
| BPMN-INST-008 | note | executable | static | A Process can also be instantiated by an Event-Based Gateway or a Receive Task that has no incoming Sequence Flow and instantiate=true. | 13.2 (p. 426) |
| BPMN-INST-009 | must | executable | runtime | Instantiating exclusive Event-Based Gateway: the first matching event creates the instance and the other events from the same gateway are no longer awaited. | 13.2 (p. 426) |
| BPMN-INST-010 | must | executable | runtime | Instantiating parallel Event-Based Gateway: the first matching event creates the instance, the instance then waits for the remaining events, and all of them must carry the same correlation information; the instance completes only when all have occurred. | 13.2; 13.4.4 (pp. 426; 437) |
| BPMN-INST-011 | note | executable | partial | Several Start Events are alternatives (a started instance does not wait for the others); a Multiple Parallel Start Event is the way to wait for several triggers; several instantiating parallel Event-Based Gateways may coexist, each group being an alternative. | 13.2 (p. 426) |
| BPMN-INST-012 | must | executable | runtime | Each occurring Start Event places a token on its outgoing Sequence Flows. | 13.2 (p. 426) |
| BPMN-INST-013 | must | executable | runtime | A Process instance is completed if and only if (a) an instantiating parallel gateway's successor events have all occurred, (b) no token remains, and (c) no Activity is still active. | 13.2 (p. 426) |
| BPMN-INST-014 | must | executable | partial | For an instance to complete, all tokens must reach a node without outgoing Sequence Flows. A model where some token cannot reach one (dead end, trapping loop) can never complete. | 13.2 (p. 426) |
| BPMN-INST-015 | must | executable | runtime | A token reaching an End Event triggers that event type's behavior (message sent, signal sent). A token reaching a Terminate End Event terminates the whole Process abnormally; 13.5.6 adds that other instances are unaffected. | 13.2; 13.5.6 (pp. 426; 443) |
| BPMN-INST-016 | should | executable | runtime | Process-level end: the instance completes iff all start nodes were visited (every Start Event triggered; for every starting Event-Based Gateway one of its events triggered) and no token remains. This conflicts with the alternative-start rule BPMN-INST-011, so this file treats it as guidance. | 13.5.6 (p. 443) |

## LIFE: Activity behavior and life cycle

| Id | Strength | Applies when | Checkable | Rule | Section |
|---|---|---|---|---|---|
| BPMN-LIFE-001 | should | executable | static | An Activity with several incoming Sequence Flows is in uncontrolled flow: each arriving token enables it independently, as if an implied Exclusive Gateway sat in front. If tokens need to be controlled, non-exclusive Gateways should be modeled explicitly before the Activity. | 13.3.1 (p. 427) |
| BPMN-LIFE-002 | note | executable | static | An Activity with no incoming Sequence Flow is instantiated when its containing Process or Sub-Process is instantiated (exception: Compensation Activities). | 13.3.1 (p. 427) |
| BPMN-LIFE-003 | must | executable | runtime | When an Activity reaches Completed, every outgoing Sequence Flow gets a token: several unconditional flows act as a parallel split; several conditional flows as an inclusive split; a mix acts as both combined. | 13.3.1; 13.3.2 (pp. 427; 429) |
| BPMN-LIFE-004 | note | executable | static | An Activity with no outgoing Sequence Flow ends without producing tokens, and the container's termination semantics then apply. | 13.3.1 (p. 427) |
| BPMN-LIFE-005 | note | executable | none | Token movement along a flow has no timing constraint. isImmediate=false (or unset, read as false) lets other activities run while a token is in transit; true forbids it. (isImmediate is non-operational, BPMN-INST-002.) | 13.3.1 (p. 427) |
| BPMN-LIFE-006 | must | executable | partial | Ready: an Activity is ready when startQuantity tokens are available (startQuantity is 1 or more). | 13.3.2 (p. 429) |
| BPMN-LIFE-007 | must | executable | partial | Ready to Active: when some data InputSet becomes available. InputSets are evaluated in list order, the first available one is used and later ones are not evaluated; the Activity waits until one is available. InputSet order is therefore significant. | 13.3.2 (p. 429) |
| BPMN-LIFE-008 | must | executable | runtime | An InputSet is available if each of its required data inputs is available; a data input is required unless it is optional in that InputSet. | 13.3.2 (p. 429) |
| BPMN-LIFE-009 | must | executable | runtime | A Ready or Active Activity can be Withdrawn in a race: for Tasks after an Event-Based Exclusive Gateway, the first Task or Event to complete withdraws the others. | 13.3.2 (p. 429) |
| BPMN-LIFE-010 | must | executable | runtime | An Active Activity that fails moves to Failed; a fault in its environment moves it to Terminated; normal end of work moves it to Completing. | 13.3.2 (p. 429) |
| BPMN-LIFE-011 | must | executable | runtime | Completing is an intermediate state that waits for non-interrupting event handlers; no new non-interrupting handler may be created while Completing (a handler may be created only while Active). 13.3.2 words this as 'should' and 13.5.4 states it flatly; this file takes the flat form. | 13.3.2 (p. 429) |
| BPMN-LIFE-012 | must | executable | runtime | An interrupting event or interrupting Event Sub-Process moves the Activity to Failing (error) or Terminating (any other event). Nested activities not yet in a final state, and non-interrupting Event Sub-Processes, are terminated; the Activity's data context is kept while an interrupting Event Sub-Process runs and released when it reaches a final state. | 13.3.2 (p. 429) |
| BPMN-LIFE-013 | must | executable | partial | Completed: after all completion dependencies are met, completionQuantity tokens go onto the outgoing flows (an implicit Parallel Gateway when several) and a data OutputSet is selected. | 13.3.2 (p. 429) |
| BPMN-LIFE-014 | must | executable | partial | OutputSet selection: OutputSets are checked in list order; one is available if all its required data outputs are available; the first available is used and its output Data Associations push data into the context. If none is available a runtime exception is thrown. If an IORule exists, the chosen OutputSet together with the InputSet used must satisfy it, else a runtime exception. OutputSet order is significant. | 13.3.2 (p. 429) |
| BPMN-LIFE-015 | must | executable | runtime | Only a Completed Activity can be compensated; it still ends Completed when no compensation is triggered or no handler exists. If a handler is invoked it goes Compensating, then Compensated (success), Failed (exception) or Terminated (termination). | 13.3.2 (p. 430) |
| BPMN-LIFE-016 | note | executable | none | Activity life cycle state machine (Figure 13.2): the states and transitions are in references/execution.md. | 13.3.2 (p. 428) |
| BPMN-LIFE-017 | must | executable | runtime | Service Task: on activation the operation's in-message is filled from the Task's data input and the operation is invoked; on completion the Task's data output is filled from the out-message. A fault returned by the service is treated as an interrupting error and the Activity fails. | 13.3.3 (p. 430) |
| BPMN-LIFE-018 | must | executable | runtime | Send Task: on activation the message is filled from the data input, sent, and the Task completes. | 13.3.3 (p. 430) |
| BPMN-LIFE-019 | must | executable | runtime | Receive Task: waits for its message, fills the data output from it, completes. With key-based correlation only one receive per CorrelationKey can be active (the message matches at most one instance); with predicate-based correlation the message may go to several Receive Tasks. With instantiate=true it may start an instance. | 13.3.3 (p. 430) |
| BPMN-LIFE-020 | must | executable | runtime | User Task: on activation it is distributed to the assigned person or group and completes when the work is done. | 13.3.3 (p. 430) |
| BPMN-LIFE-021 | note | executable | static | Manual Task and Abstract Task are conceptual only: a Manual Task is distributed to people but never executed by an IT system; an Abstract Task completes immediately on activation. Both are non-operational (BPMN-INST-002). | 13.3.3 (p. 430) |
| BPMN-LIFE-022 | must | executable | runtime | Business Rule Task: on activation the business rule is called, and the Task completes when it returns. Script Task: on activation the script is invoked, and the Task completes when it returns. | 13.3.3 (p. 430) |
| BPMN-LIFE-023 | should | executable | static | An executable Service, Send or Receive Task has to say which operation or message it uses (operationRef, messageRef); the standard does not require this, so an executable model without them cannot run on a service engine. (inferred) | 13.3.3 with 10.3.3.1 (pp. 430; 157 to 160) |

## SUBP: Sub-process, ad-hoc and loop behavior

| Id | Strength | Applies when | Checkable | Rule | Section |
|---|---|---|---|---|---|
| BPMN-SUBP-001 | must | executable | static | A Sub-Process is instantiated when a Sequence Flow token reaches it. It has either one unique empty Start Event (which gets the token) or no Start Event, in which case all Activities and Gateways without incoming Sequence Flows get a token. | 13.3.4 (p. 430) |
| BPMN-SUBP-002 | must | executable | static | A Sub-Process must not have any non-empty Start Events. | 13.3.4 (p. 430) |
| BPMN-SUBP-003 | note | executable | static | If a Sub-Process has no incoming flow but Start Events that are targets of flows from outside it, it is instantiated when one of those Start Events receives a token; several such Start Events are alternatives and each arrival creates a new instance. | 13.3.4 (p. 431) |
| BPMN-SUBP-004 | must | executable | runtime | A Sub-Process instance completes when no tokens remain in it and none of its Activities is active. | 13.3.4 (p. 431) |
| BPMN-SUBP-005 | must | executable | runtime | In a Sub-Process, a Terminate End Event terminates it abnormally (only the affected instance when multi-instance); a Cancel End Event terminates it abnormally and aborts the Transaction, with control leaving through a Cancel boundary event; other end events perform their type behavior. | 13.3.4; 13.5.6 (pp. 431; 443) |
| BPMN-SUBP-006 | must | executable | runtime | Sub-process-level end: the instance completes iff all its start nodes were visited and no token remains. | 13.5.6 (p. 443) |
| BPMN-SUBP-007 | must | executable | partial | A Call Activity has the same instantiation and termination semantics as a Sub-Process. The called global Process may also have non-empty Start Events; these are alternatives to its empty Start Event and are ignored when it is called from another Process. | 13.3.4 (p. 431) |
| BPMN-SUBP-008 | should | executable | static | A called global Process should therefore be callable through an empty Start Event or start-less activities; a process with only non-empty Start Events cannot be entered by a Call Activity. (inferred) | 13.3.4 with 10.3.6 (p. 431) |
| BPMN-SUBP-009 | must | executable | static | An Ad-Hoc Sub-Process or Process contains only Activities, Sequence Flows, Gateways and Intermediate Events, and may also contain Data Objects and Data Associations; it has no Start or End Events. | 13.3.5 (p. 431) |
| BPMN-SUBP-010 | note | executable | static | Activities inside an Ad-Hoc Sub-Process need not have incoming or outgoing flows; where flows are given they impose the usual ordering. | 13.3.5 (p. 431) |
| BPMN-SUBP-011 | note | executable | static | To mean anything, an Intermediate Event inside an Ad-Hoc Sub-Process needs outgoing Sequence Flows; it can fire several times while the Sub-Process is active. | 13.3.5 (p. 431) |
| BPMN-SUBP-012 | must | executable | runtime | Initially all Activities with no incoming flow are enabled; a human performer, not the engine, selects which enabled Activity runs. ordering=sequential: the next may start only after the previous terminated; ordering=parallel: any time, including several instances of the same Activity. | 13.3.5 (p. 431) |
| BPMN-SUBP-013 | must | executable | partial | After each inner Activity completes, completionCondition is evaluated: false updates the enabled set; true completes the Sub-Process without further activities; with ordering=parallel and cancelRemainingInstances=true running instances are cancelled, with false it waits for them to end. | 13.3.5 (p. 431) |
| BPMN-SUBP-014 | must | executable | runtime | When an inner Activity completes it produces completionQuantity tokens; propagation continues until every token sits on an Activity input, a converging Parallel or Complex Gateway, or an Intermediate Event; an inner Activity is enabled with no incoming flow or when enough tokens (startQuantity) are present. | 13.3.5 (p. 432) |
| BPMN-SUBP-015 | should | executable | static | The standard does not say how an Ad-Hoc Sub-Process without a completionCondition ends; in an executable model one should be given. (inferred) | 13.3.5 (gap) (p. 431) |
| BPMN-SUBP-016 | must | executable | partial | Standard loop: the inner Activity repeats while loopCondition is true; testBefore chooses pre-test or post-test; loopMaximum bounds the iterations (unbounded when absent). | 13.3.6 (p. 432) |
| BPMN-SUBP-017 | must | executable | partial | Multi-instance: the instance count is evaluated once (loopCardinality, or the size of the loopDataInput collection); isSequential chooses sequential or parallel creation; completionCondition is evaluated after every instance completes and, when true, cancels the rest, produces the outgoing tokens and completes the Activity. | 13.3.7 (p. 432) |
| BPMN-SUBP-018 | must | executable | partial | MultiInstance behavior: none throws the event definition for every completing instance; one throws it for the first completing instance; all throws no event; complex evaluates every ComplexBehaviorDefinition after each completion and throws the event of each whose condition is true (events are caught on the Activity boundary). | 13.3.7 (pp. 432 to 433) |
| BPMN-SUBP-019 | note | executable | static | For behavior none or one, the thrown event definition is referenced from the loop characteristics and carries the Activity's runtime attributes. The PDF names the references noneEvent and oneEvent; the XSD names them noneBehaviorEventRef and oneBehaviorEventRef. | 13.3.7 (p. 433) |
| BPMN-SUBP-020 | note | executable | partial | Multi-instance data flow: the input collection reaches loopDataInput through a DataInputAssociation from a Data Object (marked as a collection); each instance gets an inputDataItem; results flow to outputDataItem and loopDataOutput and out through a DataOutputAssociation. The extraction and update mechanisms are left unspecified. | 13.3.7 (p. 433) |
| BPMN-SUBP-021 | should | executable | none | The collection receiving multi-instance output should not be accessed until all items are written, since a concurrent Activity could read it before token flow guarantees completeness. | 13.3.7 (p. 433) |
| BPMN-SUBP-022 | must | executable | runtime | A multi-instance Activity is compensated only if all its instances completed successfully. | 13.3.7 (p. 433) |

## EXGW: Gateway execution

| Id | Strength | Applies when | Checkable | Rule | Section |
|---|---|---|---|---|---|
| BPMN-EXGW-001 | must | executable | runtime | Parallel Gateway: activated when every incoming flow holds at least one token; consumes exactly one token per incoming flow and produces exactly one on every outgoing flow; excess tokens stay; it cannot throw an exception. | 13.4.1; Table 13.1 (p. 434) |
| BPMN-EXGW-002 | must | executable | partial | Exclusive Gateway: each arriving token goes to exactly one outgoing flow; conditions are evaluated in order and the first true one wins; the default flow is taken if and only if none is true; if none is true and there is no default flow an exception is thrown. | 13.4.2; Table 13.2 (p. 435) |
| BPMN-EXGW-003 | should | executable | static | Because exclusive evaluation is ordered, the order of an Exclusive Gateway's outgoing flows is significant; a diverging Exclusive Gateway without a default flow can throw at runtime. (inferred) | 13.4.2; Table 13.2 (p. 435) |
| BPMN-EXGW-004 | must | executable | runtime | Inclusive Gateway is activated when at least one incoming flow has a token and no token on another path can still arrive on an empty incoming flow (the path-based synchronizing-merge rule of Table 13.3). On execution it consumes a token from every incoming flow that has one. | 13.4.3; Table 13.3 (p. 436) |
| BPMN-EXGW-005 | must | executable | partial | Inclusive Gateway outputs: all outgoing conditions are evaluated in any order; every true condition gets a token (must); the default flow gets one if and only if none is true; none true and no default throws an exception. | 13.4.3; Table 13.3 (p. 436) |
| BPMN-EXGW-006 | must | executable | runtime | Event-Based Gateway: pass-through merge; exactly one outgoing branch is taken, decided by the first event of the configuration to occur; the first Task or Event to complete withdraws the others; it cannot throw an exception. | 13.4.4; Table 13.4 (p. 437) |
| BPMN-EXGW-007 | must | executable | static | An Event-Based Gateway that starts a Process as a Parallel gateway allows only message-based triggers, and its Message triggers must belong to a Conversation with the same correlation information; after the first trigger the rest attach to the running instance. This is stricter than BPMN-GATE-006 and BPMN-GATE-007, which allow Signal, Timer and Conditional triggers; the stricter form applies to executable processes. | 13.4.4 (p. 437) |
| BPMN-EXGW-008 | must | executable | partial | Complex Gateway: each incoming gate has an activationCount (tokens present) usable in the activationExpression; the expression is a boolean over data and activationCounts and is not evaluated until a token is present. | 13.4.5 (p. 437) |
| BPMN-EXGW-009 | should | executable | partial | To avoid oscillation, activationCount should be used only in subexpressions of the form expr >= const, where expr uses only addition and const stays constant during the run. | 13.4.5 (pp. 437 to 438) |
| BPMN-EXGW-010 | must | executable | runtime | Complex Gateway has two states, waiting for start and waiting for reset (runtime attribute waitingForStart, initially true). In the first phase, once the activation expression is true, it consumes one token per incoming flow that has one, evaluates all outgoing conditions in any order, gives tokens to the true ones (default only if none is true; exception if none and no default), then moves to waiting for reset while remembering which flows it consumed from. | 13.4.5; Table 13.5 (pp. 438 to 439) |
| BPMN-EXGW-011 | must | executable | runtime | Complex Gateway reset: when no path can still deliver a token to an incoming flow that has neither a token nor a first-phase consumption, it consumes remaining tokens, evaluates outgoing conditions again (it may produce no token here, without an exception) and returns to waiting for start. Conditions may refer to waitingForStart and so evaluate differently in the two phases. | 13.4.5; Table 13.5 (pp. 438 to 439) |
| BPMN-EXGW-012 | note | executable | none | If a Complex Gateway's activation expression never becomes true, tokens block indefinitely and the Process can deadlock. The gateway throws an exception only when activated in waiting-for-start with no true outgoing condition and no default. | 13.4.5; Table 13.5 (p. 439) |

## EXEV: Events at runtime

| Id | Strength | Applies when | Checkable | Rule | Section |
|---|---|---|---|---|---|
| BPMN-EXEV-001 | must | executable | partial | A Start Event of an embedded Sub-Process or top-level Process creates an instance on each occurrence and then flows as usual. Only an Event-Based Gateway can exist without incoming flow in a Process; several such groups are allowed if they share a Conversation, and one event of each group must arrive. | 13.5.1 (pp. 439 to 440) |
| BPMN-EXEV-002 | must | executable | runtime | Intermediate catch event: waiting starts when the event is reached; the occurrence is consumed when it arrives. Message catch events use the Receive Task correlation behavior. | 13.5.2 (p. 440) |
| BPMN-EXEV-003 | must | executable | partial | Boundary event: the occurrence is consumed first; if cancelActivity is set the attached Activity is cancelled (all instances when multi-instance), else it continues; then flow follows the boundary event's outgoing flow. The text limits non-cancelling boundary events to Message, Signal, Timer and Conditional, while Table 10.92 also allows Escalation and Multiple; the table governs. | 13.5.3 (p. 440) |
| BPMN-EXEV-004 | must | executable | static | An Event Sub-Process starts with a Start Event, creates a scope, is instantiated only when that Start Event triggers, must not be connected to the rest of the Sequence Flows, cannot have boundary events attached, and runs in the context (data) of its parent. | 13.5.4 (p. 440) |
| BPMN-EXEV-005 | must | executable | partial | isInterrupting set on the Start Event: the Event Sub-Process cancels the enclosing Sub-Process (only the affected instance for multi-instance); not set (not possible for Error): the parent keeps running in parallel. The handler may re-throw the triggering event to continue outside the parent's boundary through a matching boundary event. | 13.5.4 (p. 440) |
| BPMN-EXEV-006 | must | executable | partial | An Event Sub-Process is initiated only while its parent is running. Several instances of non-interrupting handlers may run, started at different times. Only one interrupting handler may be initiated per event definition within a parent; once it starts, the parent is interrupted and no new handlers start. | 13.5.4 (pp. 440 to 441) |
| BPMN-EXEV-007 | must | executable | runtime | A parent in Completing stays there until its active Event Sub-Processes finish; no new ones start in Completing. After an error-triggered interrupting handler the parent is Failing until the handler reaches a final state; after a non-error interrupting handler it is Terminating; in both, the handler can read the parent's context and new handlers must not start. | 13.5.4 (p. 441) |
| BPMN-EXEV-008 | must | executable | runtime | An Event Sub-Process started by a Message uses the Receive Task correlation behavior. | 13.5.4 (p. 441) |
| BPMN-EXEV-009 | must | executable | runtime | Process-level Terminate End Event: the Process is abnormally terminated; no other Process instances are affected. | 13.5.6 (p. 443) |
| BPMN-EXEV-010 | must | executable | runtime | Sub-process-level Terminate End Event: the Sub-Process is abnormally terminated; for multi-instance only the affected instance; no other Sub-Process instance and no higher-level instance is affected. | 13.5.6 (p. 443) |

## COMP: Compensation and transaction

| Id | Strength | Applies when | Checkable | Rule | Section |
|---|---|---|---|---|---|
| BPMN-COMP-001 | must | executable | runtime | Compensation reverses effects of Activities that already completed; an Activity still active cannot be compensated but must be cancelled, and cancelling a Sub-Process can compensate its completed parts. | 13.5.5 (p. 441) |
| BPMN-COMP-002 | must | executable | static | A compensation handler is a Compensation Event Sub-Process (for a Process or Sub-Process) or an associated Compensation Activity (for any Activity). It is a set of Activities not connected to the rest of the model and starts with a catching Compensation event: a boundary event, or the Start Event of the Event Sub-Process. | 13.5.5 (p. 441) |
| BPMN-COMP-003 | must | executable | static | A handler attached through a boundary event can only do black-box compensation, modeled as a Compensation Activity (isForCompensation=true). | 13.5.5 (p. 441) |
| BPMN-COMP-004 | must | executable | runtime | A Compensation Event Sub-Process lives inside a Process or Sub-Process, sees a snapshot of the parent's data taken at completion, and may itself trigger compensation of the parent's activities. | 13.5.5 (p. 441) |
| BPMN-COMP-005 | note | executable | none | A Sub-Process attribute 'compensable' is said to switch on implicit default compensation (completed inner Activities compensated in reverse order). The attribute is defined nowhere else in the PDF and is not in the XSD. | 13.5.5 (p. 441) |
| BPMN-COMP-006 | must | executable | partial | Compensation is triggered by a throwing Compensation event (intermediate or end) that references the Activity; if clear from context it defaults to the current Activity; in a global context with no Activity named, all completed Activities of the Process are compensated. | 13.5.5 (p. 442) |
| BPMN-COMP-007 | must | executable | static | Triggering is synchronous by default (the thrower waits for the handler); waitForCompletion=false triggers without waiting. | 13.5.5 (p. 442) |
| BPMN-COMP-008 | should | executable | none | Each instance of a loop or multi-instance Sub-Process has its own Compensation Event Sub-Process and data snapshot; triggering compensation compensates all instances in the current scope. For a boundary compensation handler the same text says the handler runs once per instance, while the operational semantics say a Compensation Activity on a multi-instance Activity runs once for all instances. The two statements conflict, so this file treats the rule as guidance. | 13.5.5 (p. 442) |
| BPMN-COMP-009 | must | executable | runtime | Presumed abort: only completed Activities are compensated (compensating a failed Activity does nothing); the error handler must make sure no further compensation is needed. With no error Event Sub-Process for an error in a Sub-Process, the default is to compensate all its contained Activities automatically. | 13.5.5 (p. 442) |
| BPMN-COMP-010 | must | executable | runtime | A Compensation Event Sub-Process becomes enabled when its parent reaches Completed (data snapshot taken, one per instance for loops and multi-instance); an associated Compensation Activity becomes enabled when its Activity reaches Completed. | 13.5.5 (p. 442) |
| BPMN-COMP-011 | must | executable | runtime | Default compensation runs in reverse order of the original execution, concurrently where the originals had no dependency. A flow from A to B means B is compensated first; a data dependency between A and B means B is compensated first; in an Ad-Hoc Sub-Process B is compensated first if A completed before B started; loop and sequential multi-instance instances reverse their completion order; parallel multi-instance instances can compensate in parallel; if a boundary event of Sub-Process A leads to B and the event occurred, B is compensated before A. | 13.5.5 (pp. 442 to 443) |
| BPMN-COMP-012 | must |  | partial | A Transaction Sub-Process has three outcomes: success (normal outgoing flow), cancel (flow leaves via the Cancel boundary event after rollback and compensation), and hazard (flow leaves via an Error boundary event, with the Activity interrupted and no compensation). | 10.3.5 Transaction (p. 178) |
| BPMN-COMP-013 | must |  | runtime | Only cancellation of a Transaction triggers compensation; interruption by Error, Timer or anything on a non-Transaction Activity does not. | 10.3.5 Transaction (p. 178) |
| BPMN-COMP-014 | must |  | static | Cancellation is signalled by a Cancel End Event inside the Transaction or by a cancel message through the transaction protocol. Cancel End Event and Cancel boundary event are valid only in/on a Transaction (see BPMN-EVT-010). | 10.3.5 Transaction; 13.3.4 (pp. 178; 431) |
| BPMN-COMP-015 | must |  | runtime | On reaching non-Cancel end events a Transaction does not hand control up at once: the transaction protocol first verifies all participants finished; a participant problem can still redirect flow to the Cancel or Error event. | 10.3.5 Transaction (p. 178) |
| BPMN-COMP-016 | should | executable | static | For executable Processes the Transaction method should be a technology-specific URI (WS-AtomicTransaction or WS-BusinessActivity); ##compensate, ##store and ##image are kept for BPMN 1.1 compatibility. The PDF writes lowercase, the XSD default is ##Compensate. | 10.3.5 Table 10.21 (p. 178) |

## BPEL: WS-BPEL mapping

| Id | Strength | Applies when | Checkable | Rule | Section |
|---|---|---|---|---|---|
| BPMN-BPEL-001 | note | bpel-mapping | none | Clause 14 is required for BPEL Process Execution Conformance and Complete Conformance, and not for Process Modeling, Choreography or plain Process Execution Conformance. | 14.1 (p. 445) |
| BPMN-BPEL-002 | note | bpel-mapping | static | There is no mapping of the diagram itself: each pool's orchestration Process maps to its own WS-BPEL process. | 14.1 (p. 445) |
| BPMN-BPEL-003 | must | bpel-mapping | partial | To be mapped, an orchestration Process must be sound: no reachable state with a token that can never be removed (deadlock) and none with more than one token on a Sequence Flow (lack of synchronization). | 14.1 (p. 445) |
| BPMN-BPEL-004 | note | bpel-mapping | static | The Gateways and Sequence Flows form a directed graph; a block is a connected subgraph joined to the rest by exactly one entering and one leaving Sequence Flow; a block hierarchy is a set of blocks that are pairwise nested or disjoint and include the whole Process. | 14.1 (p. 445) |
| BPMN-BPEL-005 | note | bpel-mapping | partial | The syntactic mapping covers only models built from the block patterns of 14.2; the semantic mapping extends it to larger models by requiring the same observable behavior without fixing the BPEL shape. | 14.1; 14.2 (p. 446) |
| BPMN-BPEL-006 | must | bpel-mapping | none | The mapped BPEL process must show the same observable behavior as the BPMN Process. | 14.2 (p. 446) |
| BPMN-BPEL-007 | must | bpel-mapping | partial | Process: a Process (with its defining Collaboration) maps to a BPEL process whose partner links come from the interfaces of its own Participant (myRole) and of each other Participant (partnerRole); variables from the Data Objects and Properties in its graph (not those in nested Sub-Processes); correlation sets from the CorrelationKeys of its Conversations. Output uses suppressJoinFailure=yes. | 14.2.1 (pp. 447 to 448) |
| BPMN-BPEL-008 | must | bpel-mapping | static | Names: an Activity name maps to a BPEL name by removing characters not allowed in an XML NCName and adding a suffix for uniqueness. Link names (from Sequence Flow names) must be canonicalized the same way. | 14.2.2 Table 14.1; 14.2.4 (pp. 448; 463) |
| BPMN-BPEL-009 | must | bpel-mapping | static | Service Task and Send Task map to invoke; the partner link comes from the Participant they are linked to by Message Flows and the interface of their operation. A mappable Service or Send Task therefore needs an operation and a connected participant. | 14.2.2 (pp. 448 to 449) |
| BPMN-BPEL-010 | must | bpel-mapping | static | Receive Task maps to receive (createInstance from instantiate); the partner link comes from the interface of its operation. Abstract Task maps to empty. | 14.2.2 (pp. 448 to 449) |
| BPMN-BPEL-011 | must | bpel-mapping | static | The basic mapping defines no BPEL for User, Manual, Business Rule or Script Tasks, Call Activities, Ad-Hoc Sub-Processes or Transactions (the clause does not mention them). 14.3 says only that User Tasks could use BPEL4People. These are unmappable in the basic sense. (inferred) | 14.2.2; 14.3 (pp. 448 to 455; 469) |
| BPMN-BPEL-012 | must | bpel-mapping | partial | Messages with a scalar item definition typed by an XML schema map to a WSDL 1.1 message; the top-level child elements of the schema become the message parts. A Message therefore needs an XML-schema item definition to be mappable. | 14.2.2 Message (pp. 449 to 450) |
| BPMN-BPEL-013 | must | bpel-mapping | static | Interface and Operation map to a WSDL 1.1 portType and operations (in-message to input, out-message to output, errors to faults). | 14.2.2 (p. 450) |
| BPMN-BPEL-014 | must | bpel-mapping | partial | Key-based Correlation Keys map to BPEL properties, property aliases (message type and part from the key expression's message and message path), and correlation sets; the initiate flag is join or no according to whether the Message Flow initiates the Conversation. Several keys give several correlation elements. | 14.2.2 Conversations and Correlation (pp. 450 to 451) |
| BPMN-BPEL-015 | must | bpel-mapping | static | An embedded Sub-Process with ad-hoc false maps to a BPEL scope; Event Sub-Processes become handlers of the enclosing scope (or process): non-interrupting Message to onEvent, Timer to onAlarm, Error to faultHandlers catch, Compensation to compensationHandler. Interrupting Message, Signal, Escalation and Conditional Event Sub-Processes are not mapped. (inferred) | 14.2.2 Sub-Process (pp. 451 to 453) |
| BPMN-BPEL-016 | must | bpel-mapping | static | Standard loops: testTime before maps to while, after maps to repeatUntil (negated condition); a loopMaximum adds a counter variable and extra condition. The PDF names the attribute testTime, the XSD names it testBefore. | 14.2.2 Loops (pp. 453 to 455) |
| BPMN-BPEL-017 | must | bpel-mapping | static | Multi-instance Task maps to forEach (parallel unless sequential) only for the flow condition All; other behaviors (None, One, Complex) are not mapped. (inferred) | 14.2.2 Multi-Instance (p. 455) |
| BPMN-BPEL-018 | must | bpel-mapping | static | Start Events: only a Message Start Event maps to a top-level construct (receive createInstance=yes). Error and Compensation Start Events occur only in Event Sub-Processes. None, Timer, Conditional, Signal, Multiple and Parallel Multiple Start Events have no mapping in the text. (inferred) | 14.2.3 (p. 455) |
| BPMN-BPEL-019 | must | bpel-mapping | static | Intermediate Events: Message catch maps to receive, Message throw to invoke, Timer to wait (for or until), Compensation throw to compensate or compensateScope (when waitForCompletion is true and inside an error or compensation Event Sub-Process). Signal, Escalation, Link, Conditional and Cancel intermediate events have no mapping. Timer mapping uses timeCycle and timeDate, not timeDuration. (inferred) | 14.2.3 (pp. 456 to 457) |
| BPMN-BPEL-020 | must | bpel-mapping | static | End Events: None to empty, Message to invoke, Error to throw, Compensation to compensate or compensateScope, Terminate to exit. Signal, Escalation, Cancel and Multiple end events have no mapping. (inferred) | 14.2.3 (pp. 457 to 458) |
| BPMN-BPEL-021 | must | bpel-mapping | static | Boundary Events: non-interrupting Message to a scope with onEvent, non-interrupting Timer to onAlarm, Error to a scope with a fault handler (using flow and links so the handler path can rejoin), Compensation to a compensationHandler. Several boundary events on one Activity share one scope; a loop or multi-instance with boundary events sits inside that scope. Interrupting Message and Timer boundary events, and Signal, Escalation, Conditional boundary events, are not mapped. (inferred) | 14.2.3 Boundary Intermediate Events (pp. 458 to 460) |
| BPMN-BPEL-022 | must | bpel-mapping | static | Gateways: data-based Exclusive Gateway to if/else-if/else; Event-Based Gateway (Message events, Receive Tasks, Timer events in any mix) to pick with createInstance from instantiate; Inclusive Gateway (pattern without otherwise gate) to flow with links and transition conditions; Parallel fork-join to flow; chains of unconditional Activities to sequence. Complex Gateways have no mapping. (inferred) | 14.2.4 (pp. 461 to 464) |
| BPMN-BPEL-023 | must | bpel-mapping | partial | Loops built from Sequence Flows map to while (test first) or repeatUntil (test last) when they follow the structured while or repeat shape. | 14.2.4 (pp. 464 to 465) |
| BPMN-BPEL-024 | must | bpel-mapping | static | Data Objects map to BPEL variables typed by the item definition (declared in the process or the scope of the Sub-Process holding them). Properties map to variables named container.property: a Process property is global; an Event property lives in the enclosing Sub-Process scope; an Activity property lives in its enclosing scope, or its own scope if it is a Sub-Process. | 14.2.5 (pp. 465 to 466) |
| BPMN-BPEL-025 | must | bpel-mapping | static | Input and Output Sets: for Send and Service Tasks the single input set, and for Receive and Service Tasks the single output set, map to a WSDL message; each data input or output is a message part typed by its item definition. More than one set is not mapped. | 14.2.5 (pp. 466 to 467) |
| BPMN-BPEL-026 | must | bpel-mapping | partial | Data Associations map to toParts and fromParts of invoke or receive. If the Task's sets differ in structure from its message, assignments are needed (assign, invoke, assign). | 14.2.5 (pp. 467 to 469) |
| BPMN-BPEL-027 | must | bpel-mapping | static | XPath expressions are used as written, with the BPMN context functions rewritten to BPEL variable access (Table 14.2); the arguments must be literal strings so the rewrite is possible. | 14.2.5 Table 14.2 (p. 468) |
| BPMN-BPEL-028 | note | bpel-mapping | static | Data Stores, Groups, Text Annotations, Pools/Lanes as such, Choreographies and Conversations have no mapping (the clause does not mention them). (inferred) | 14 (pp. 445 to 474) |
| BPMN-BPEL-029 | must | bpel-mapping | none | Extended mapping: additional sound Process models whose block hierarchy contains unaddressed blocks can be mapped; the mapped BPEL must match the operational semantics of the BPMN Process. | 14.3 (p. 469) |
| BPMN-BPEL-030 | note | bpel-mapping | none | The extended mapping says the mappings of 'sub clause 15.1' should be used where applicable; 15.1 is about interchanging incomplete models, so this looks like a stale reference to 14.2. | 14.3 (p. 469) |
| BPMN-BPEL-031 | must | bpel-mapping | partial | Interleaved (overlapping, non-nested) loops: the looping part must be moved out into derived BPEL processes that spawn each other; the main process gets a one-way invoke named Spawn_<loop target>_Derived_Process followed by a receive named <loop target>_Derived_Process_Completed; derived processes are named <loop target>_Derived_Process and signal completion by a one-way invoke. Gateways there map to switch, not while. | 14.3.3 (pp. 470 to 472) |
| BPMN-BPEL-032 | must | bpel-mapping | partial | Loop with a decision of three or more outgoing flows (one looping back): maps to a while followed by a switch inside a sequence; the looping flow's condition becomes the while condition, the other outgoing flows become switch cases. | 14.3.2 (pp. 469 to 470) |
| BPMN-BPEL-033 | must | bpel-mapping | partial | Infinite loop (flow looping back with no gateway): maps to a while with an always-false condition such as 1 = 0, the looped activities inside it. | 14.3.4 (p. 473) |
| BPMN-BPEL-034 | must | bpel-mapping | partial | An element reached by flows that merge before all branches of a BPEL structured element merge must be duplicated into each branch, or moved to a derived process invoked from each place (named <target>_Derived_Process). A BPEL flow avoids duplication but is not always usable, for example under a pick. | 14.3.5 (pp. 473 to 474) |
| BPMN-BPEL-035 | note | bpel-mapping | partial | End Events can be combined with other BPMN objects to complete merging or joining of the paths of a BPEL structured element (Figure 14.2, distributed token recombination). | 14.3.1 (p. 469) |
| BPMN-BPEL-036 | note | bpel-mapping | none | Clause 14 mixes BPEL 2.0 syntax (if/else, 14.2) with BPEL 1.1 constructs (switch/case, 14.3). (inferred) | 14.2.4; 14.3 (pp. 461; 470) |

## CORR: Correlation

| Id | Strength | Applies when | Checkable | Rule | Section |
|---|---|---|---|---|---|
| BPMN-CORR-001 | note |  | none | Correlation ties a Message to an ongoing Conversation (instance routing). It applies at Collaboration, Choreography and Process level but happens at runtime in the Process. References to Send or Receive Tasks include message catch and throw events. | 8.4.2 (p. 72) |
| BPMN-CORR-002 | note |  | none | Two non-exclusive mechanisms exist: key-based and context-based correlation. | 8.4.2 (pp. 72 to 73) |
| BPMN-CORR-003 | must |  | partial | Key-based: every Message sent or received within a Conversation must carry in its payload the value of at least one of the Conversation's CorrelationKeys. | 8.4.2 (p. 72) |
| BPMN-CORR-004 | must |  | partial | A CorrelationKey is a composite key of CorrelationProperties (its partial keys); it is valid for use only if the Message populates all its properties; name is optional. | 8.4.2; Table 8.31 (pp. 72; 75) |
| BPMN-CORR-005 | must |  | static | Each CorrelationProperty needs at least one CorrelationPropertyRetrievalExpression, one per Message used in the Conversation; it may name a type. | 8.4.2; Table 8.32; Table 8.37 (pp. 72; 75; 77) |
| BPMN-CORR-006 | must |  | static | A CorrelationPropertyRetrievalExpression has a messagePath (FormalExpression) and a messageRef to the Message it extracts from; both are required. | Table 8.33; Table 8.39 (pp. 76; 78) |
| BPMN-CORR-007 | must |  | runtime | If a follow-up Message derives a CorrelationKey already initialized in the Conversation, the values must match; if the key was not yet initialized, its value becomes associated with the Conversation. | 8.4.2 (p. 72) |
| BPMN-CORR-008 | must |  | runtime | The first Send or Receive Task of a Conversation must populate at least one CorrelationKey instance from the first Message. | 8.4.2 Key-based (p. 75) |
| BPMN-CORR-009 | should |  | static | Context-based: a Process may supply a CorrelationSubscription (one per CorrelationKey, correlationKeyRef required) holding CorrelationPropertyBindings, one per CorrelationProperty of the key; each binding has a correlationPropertyRef and a dataPath FormalExpression, both required. The text says 'as many bindings as properties'; the XSD allows zero or more (so treat the count rule as should). | 8.4.2; Tables 8.34, 8.35; XSD (pp. 73; 76 to 78) |
| BPMN-CORR-010 | note |  | runtime | At runtime, subscription expressions are re-evaluated when the Data Objects or Properties they reference change, so the correlation condition can change during the run. The text calls the result 'SubscriptionProperty', a term not defined elsewhere. | 8.4.2 Context-based (pp. 76 to 77) |
| BPMN-CORR-011 | must |  | partial | The CorrelationKeys that apply to a Message Flow are those of its containers: Collaborations, Choreographies, Conversation Nodes, Choreography Activities. Several keys can apply at once. Calls of Collaborations and Choreographies count as containment, so the caller's keys apply to Message Flows in the called element. | 8.4.2 (p. 73) |
| BPMN-CORR-012 | note |  | none | The XSD (normative) defines CorrelationSubscription with a correlationKeyRef attribute and no 'process' element; Table 8.40 in the PDF shows a 'process' element and a correlationKeyRef element, and writes xsd:String. The XSD is followed. | Table 8.40; Semantic.xsd (p. 78) |

## RSRC: Resources and roles

| Id | Strength | Applies when | Checkable | Rule | Section |
|---|---|---|---|---|---|
| BPMN-RSRC-001 | must |  | static | A Resource is an abstract definition (not actual user IDs) that Activities reference; several Activities may use the same Resource. It has a required name and zero or more ResourceParameters. | 8.4.12; Table 8.49; Table 8.62 (pp. 93; 94; 100) |
| BPMN-RSRC-002 | note |  | static | A ResourceParameter (name, type, isRequired) is a query parameter resolved at runtime (for example against an organizational directory); an Activity referencing the Resource can bind values to it. | 8.4.12; Table 8.63 (pp. 93 to 94; 101) |
| BPMN-RSRC-003 | must |  | static | ResourceRole (on an Activity or a Process) refers to a Resource by resourceRef or carries a ResourceAssignmentExpression, not both: the PDF says 'should not be specified' for the other; the XSD makes them mutually exclusive. | 10.3.1 Table 10.5; XSD (pp. 152 to 153) |
| BPMN-RSRC-004 | must |  | static | ResourceParameterBindings (parameterRef, expression) apply only when resourceRef is given. | 10.3.1 Tables 10.5, 10.7 (pp. 153 to 154) |
| BPMN-RSRC-005 | must |  | partial | A ResourceAssignmentExpression must contain an Expression, and such Expressions must return resource entities (Users, Groups); several Expressions may return several Resources, all assigned to that ResourceRole subtype (potential owners, for example). | 10.3.1 Table 10.6 (p. 153) |
| BPMN-RSRC-006 | note |  | runtime | Parameterized assignment: the infrastructure may use zero or more of the declared parameters and may override some with deployment values; failed queries count as empty results; a query returns one Resource or a set. | 10.3.1 (p. 153) |
| BPMN-RSRC-007 | note |  | static | Performer: the resource that performs or is responsible for an Activity (individual, group, role or position, organization); no extra attributes. HumanPerformer specializes it for people; PotentialOwner specializes HumanPerformer for people who may claim a User Task and become its actual owner. In the XSD HumanPerformer and PotentialOwner add nothing; the PDF's Table 10.17 adds a peopleAssignment element the XSD does not have. | 10.3.2; 10.3.4; Tables 10.17, 10.18 (pp. 154; 165 to 168) |
| BPMN-RSRC-008 | note |  | runtime | User Task runtime instance attributes actualOwner (user who claimed it) and taskPriority are reported, not modeled. | 10.3.4 Table 10.14 (p. 165) |
| BPMN-RSRC-009 | should |  | none | User Task renderings are an optional extension point; a User Task can deploy on any compliant implementation whether or not it supports the rendering methods; extensions should reuse WS-HumanTask attributes. | 10.3.4 (pp. 164 to 165) |

## SERV: Services

| Id | Strength | Applies when | Checkable | Rule | Section |
|---|---|---|---|---|---|
| BPMN-SERV-001 | must |  | static | An Interface (name required, implementationRef optional such as a WSDL portType) defines at least one Operation and is used by CallableElements and Participants. | 8.5.1; Table 8.65; Table 8.67 (pp. 102 to 104) |
| BPMN-SERV-002 | must |  | static | An Operation (name required) has exactly one input Message (inMessageRef), at most one output Message (outMessageRef), and zero or more Errors it may return; implementationRef optional (for example a WSDL operation). The PDF's Table 8.66 says 'at most one input Message' for outMessageRef (typo). | 8.5.3; Table 8.66; Table 8.68 (pp. 103 to 104) |
| BPMN-SERV-003 | note |  | static | EndPoint is an empty extension point on RootElement for service addresses (for example WS-Addressing); the address definition is out of scope. EndPoints can be assigned to Participants (endPointRefs). | 8.5.2; 9.3 Table 9.2 (pp. 103; 115) |
| BPMN-SERV-004 | note |  | static | A Participant lists supported Interfaces (interfaceRef, zero or more) and EndPoints; Processes and GlobalTasks list supportedInterfaceRefs for the external behavior they provide. | 9.3 Table 9.2; 10.3.6 Table 10.24 (pp. 115; 186) |
| BPMN-SERV-005 | must | executable | static | Service, Send and Receive Tasks reference one Operation (operationRef, optional in the XSD); implementation default is ##WebService. A Message event definition's operationRef must be specified when the Process is executable. | 10.3.3.1; 10.5.5 Table 10.108 (pp. 157 to 160; 270) |

## ANNX: Annexes

| Id | Strength | Applies when | Checkable | Rule | Section |
|---|---|---|---|---|---|
| BPMN-ANNX-001 | note |  | none | Annex A (Changes from v1.2) is informative. It lists new Choreography and Conversation diagrams, non-interrupting events, event Sub-Processes, a formal metamodel, XMI and XSD interchange for syntax and diagrams, and XSLT between them; Reference Tasks were removed in favor of GlobalTasks. | Annex A (p. 479) |
| BPMN-ANNX-002 | note |  | none | Annex B (Diagram Interchange) is non-normative documentation of a subset of an alpha Diagram Definition specification (DC and DI packages) referenced by BPMN DI; the DG package is not documented. The normative DI/DC artifacts are the CMOF and XSD files. Annex B refers to 'Clause 13 - BPMN DI' but BPMN DI is Clause 12. | Annex B (pp. 481 to 498) |
| BPMN-ANNX-003 | note |  | none | Annex B states the DD design principle: interchange only graphics the user controls (positions, routing points); do not interchange graphics fixed by the language (shapes, line styles). | B.2 (pp. 481 to 482) |
| BPMN-ANNX-004 | note |  | none | Annex B DI package facts: a Diagram has a root DiagramElement; a DiagramElement references at most one model element; Plane children are ordered and the order is the z-order; Shape has bounds, Edge has two or more waypoints, optional source/target only when not derivable; Label bounds are optional (default position when absent) and the presence of a label means it is visible; Style properties are shared across elements; tool-specific data goes in the interchange format's extension mechanism. | B.3 to B.4 (pp. 483 to 497) |
| BPMN-ANNX-005 | note |  | none | Annex C (Glossary) is informative. It uses some older vocabulary (Abstract Process for Public Process; End Event results include Link; Trigger list includes Link) that disagrees with the normative clauses. | Annex C (pp. 499 to 502) |
| BPMN-ANNX-006 | note |  | none | There is no Annex D in this PDF: the table of contents ends with Annexes A, B and C. | Contents (p. viii) |

## Counts

must 196, should 16, note 51; total 263.
