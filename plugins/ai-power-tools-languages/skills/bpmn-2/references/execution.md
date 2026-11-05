# Executable processes and the WS-BPEL mapping

This file summarizes, in our own words, the parts of BPMN 2.0.2 that matter only when a process is meant to run: the execution semantics of Clause 13 (with the transaction text of 10.3.5), the correlation, resource and service rules that execution depends on, and the mapping to WS-BPEL of Clause 14. Section numbers and page numbers are the specification's; "p." is the printed page.

Rule ids (`BPMN-<CAT>-nnn`) point into `rules.md`. Rules from the execution clauses carry `applies_when: executable` in `language.yaml`, and rules from Clause 14 carry `applies_when: bpel-mapping`.

## 1. When these rules apply

**Executable.** A process is marked executable by its `isExecutable` attribute (Table 10.1). Rules whose `applies_when` is `executable` are checked only for processes with that attribute set to true. A public process may not be executable. A process that is not marked executable is documentation: it may leave out everything Clause 13 needs (operations, expressions, data types), and nothing here applies to it.

**BPEL mapping.** The standard has no flag that says "map this process to WS-BPEL" and no conformance attribute for it. Rules whose `applies_when` is `bpel-mapping` apply when a tool or a user requests the mapping for a given process. This trigger is not defined by the standard, so whoever applies the rules supplies it.

**What a validator can see.** Execution semantics is mostly about running state. Every rule in `language.yaml` carries `checkable`: `static` (a property or relationship of elements, checkable on a saved model), `partial` (checkable for the structure, in simple cases, or only with graph analysis), `runtime` (needs a running instance) or `none` (not a property of a model). Of the 167 rules that come from the execution, mapping, correlation, resource, service and annex clauses, 57 are static, 38 partial, 48 runtime and 24 not model properties.

## 2. What an execution implementation may ignore (13.1, p. 425)

Ten elements are non-operational: a Process Execution implementation may ignore them. A model that relies on any of them for behavior is not executable on an engine.

- Manual Task and Abstract Task
- Data State
- I/O rules
- Ad-Hoc Process
- Item definitions whose kind is Physical
- The "while executing" input-set reference on a Data Input and output-set reference on a Data Output
- The `isClosed` attribute of a Process
- The `isImmediate` attribute of a Sequence Flow

An executable process that contains one of these gets an advisory, not an error (BPMN-INST-002, BPMN-LIFE-021). Note that the table for Sequence Flow still requires `isImmediate` not to be false in an executable process (BPMN-ACT-011); the two statements are consistent, because the first lets an engine ignore the attribute and the second restricts what a model sets.

Clause 13 is informal text with tables for the gateways. Tokens are a thinking aid; tools need not implement them (13.3.1, p. 427) (BPMN-INST-003). Where Clause 13 and the schema use different attribute names, the schema's are used: `noneBehaviorEventRef`, `oneBehaviorEventRef`, `behavior`, `testBefore` and `activationCondition`.

## 3. Process instances (13.2, 13.5.1, 13.5.6)

- Each occurrence of a Start Event creates a new instance, unless the Start Event shares a Conversation with other Start Events; then a new instance is created only if none exists for that conversation's correlation information. A later occurrence with the same correlation information goes to the existing instance (BPMN-INST-005, BPMN-INST-006).
- An instance can also be created by an Event-Based Gateway, or by a Receive Task with `instantiate` true and no incoming sequence flow. For an exclusive instantiating gateway the first matching event creates the instance and the rest are no longer awaited. For a parallel instantiating gateway the first matching event creates it, the instance waits for the others, they must share correlation information, and it completes only when all have occurred (BPMN-INST-008, BPMN-INST-009, BPMN-INST-010).
- Several start events are alternatives; a Parallel Multiple start event is how to wait for several triggers. 13.5.6 instead says the process completes only after all start nodes were visited. The two statements conflict; the library records both and treats the second as guidance (BPMN-INST-011, BPMN-INST-016).
- A global process is, as written, required to have no empty start event and no activity or gateway without incoming flow. 13.3.1 and 13.3.4 describe those as normal entry points. The library treats the 13.2 sentence as guidance (BPMN-INST-007).
- A token reaching an End Event triggers that event type's behavior. A Terminate End Event ends the whole process abnormally and affects no other instance. An instance completes only when no token remains and no activity is still active, so a model in which some token can never reach a node without outgoing flow can never complete (BPMN-INST-013, BPMN-INST-014, BPMN-INST-015).

## 4. The activity life cycle (13.3.2, Figure 13.2, pp. 428 to 430)

An activity moves through thirteen states, two of them pseudo-states. The names are runtime vocabulary; they are not in the schema, so a saved model carries none of them. A tool that executes may use them; a validator of saved models cannot check them (BPMN-LIFE-016).

| State | Meaning | Leaves by |
|---|---|---|
| Inactive (initial) | Not reached yet | a token arrives: Ready |
| Ready | Enough tokens (`startQuantity`) are available | an input set becomes available: Active; interruption or a lost race: Withdrawn |
| Active | Work in progress | work done: Completing; error interruption: Failing; other interruption: Terminating; failure: Failed; environment fault: Terminated; race lost: Withdrawn |
| Completing | Work done, waiting for non-interrupting handlers | requirements met: Completed; interrupted: Failing or Terminating |
| Completed | Finished; outgoing tokens produced | compensation: Compensating; the process ends: Closed |
| Compensating | A compensation handler is running | success: Compensated; exception: Failed; termination: Terminated |
| Failing, Terminating | Interrupted, waiting for the interrupting handler to reach a final state | Failed, Terminated |
| Compensated, Failed, Terminated, Withdrawn | Final states | the process ends: Closed |
| Closed (final) | End of the life cycle | none |

Transitions, one row each:

| From | When | To |
|---|---|---|
| Inactive | A token arrives | Ready |
| Ready | Data InputSet available | Active |
| Ready | Activity interrupted: interrupting event, or alternative path selected after an Event-Based Gateway | Withdrawn |
| Active | Activity's work completed | Completing |
| Active | Activity interrupted by an interrupting event, error | Failing |
| Active | Activity interrupted by an interrupting event, not an error | Terminating |
| Active | Alternative path for Event Gateway selected | Withdrawn |
| Active | Activity fails during execution | Failed |
| Active | Fault in the environment | Terminated |
| Completing | Completing requirements done, assignments completed | Completed |
| Completing | Activity interrupted, error | Failing |
| Completing | Activity interrupted, non-error | Terminating |
| Completed | Compensation occurs | Compensating |
| Completed | The Process ends | Closed |
| Compensating | Compensation completes | Compensated |
| Compensating | Compensation failed (exception) | Failed |
| Compensating | Compensation interrupted (controlled or uncontrolled termination) | Terminated |
| Compensated | The Process ends | Closed |
| Failing | Interrupting handler reaches a final state | Failed |
| Terminating | Terminating requirements done | Terminated |
| Failed | The Process ends | Closed |
| Terminated | The Process ends | Closed |
| Withdrawn | The Process ends | Closed |

Points that matter (13.3.2):

- Ready becomes Active when some data input set becomes available. Input sets are evaluated in list order and the first available one is used, so their order is significant (BPMN-LIFE-007). An input set is available when each of its required data inputs is available (BPMN-LIFE-008).
- On Completed, the outgoing flows get `completionQuantity` tokens (an implicit parallel gateway when there are several) and an output set is chosen the same way: in list order, first available wins; if none is available a runtime exception is thrown (BPMN-LIFE-013, BPMN-LIFE-014).
- Only a Completed activity can be compensated. Without compensation or a handler it stays Completed (BPMN-LIFE-015).
- While Completing, no new non-interrupting handler may be created. The text words this loosely in one place and flatly in another; the library takes the flat form (BPMN-LIFE-011).
- When an activity is interrupted, nested activities in Ready or Active and non-interrupting event sub-processes are terminated; the activity's data context is kept while an interrupting event sub-process runs (BPMN-LIFE-012).

## 5. Token flow per construct (13.3.1, 13.4)

| Construct | Role | Activation or trigger | Token behavior |
|---|---|---|---|
| Parallel | converging | Enabled when every incoming flow has at least one token | Consumes exactly one token from each incoming flow; excess tokens stay |
| Parallel | diverging | Any token arriving | Produces exactly one token on every outgoing flow |
| Parallel | either | Cannot throw an exception |  |
| Exclusive | converging | Each token arriving on any incoming flow | Passes straight through; no synchronization |
| Exclusive | diverging | Each token arriving | Conditions evaluated in order; first true wins; default only if none true; exception if none true and no default |
| Inclusive | converging | At least one incoming flow has a token and no token elsewhere can still reach an empty incoming flow without passing the gateway | Consumes a token from each incoming flow that has one |
| Inclusive | diverging | On execution | Conditions evaluated in any order; every true one gets a token; default only if none true; exception if none true and no default |
| Event-Based | converging | Pass-through merge of incoming branches |  |
| Event-Based | diverging | Execution | Exactly one outgoing branch: whichever event or Receive Task fires first; others withdrawn; no exception possible |
| Event-Based (instantiating, exclusive) | start | First matching event | Creates the instance; other events no longer awaited |
| Event-Based (instantiating, parallel) | start | First matching event; only Message triggers allowed; same correlation | Creates the instance; instance waits for the others; completes when all occurred |
| Complex | converging | waitingForStart=true and activationExpression true (not evaluated before a token exists) | Consumes one token per incoming flow that has one; evaluates outgoing conditions; remembers consumed flows; sets waiting for reset |
| Complex | converging | waitingForStart=false and no path can still deliver a token to a flow that has not contributed | Consumes the remaining tokens; evaluates outgoing conditions (may give none, no exception); back to waiting for start |
| Complex | diverging | Either phase | Every true condition gets a token; default only if none true; exception only in the first phase when none true and no default |
| Activity (implicit) | multiple incoming | Any arriving token | Implied exclusive merge (uncontrolled flow) |
| Activity (implicit) | multiple outgoing | On reaching Completed | Every unconditional flow gets completionQuantity tokens; conditional flows act as inclusive split |

Rule pointers: Parallel BPMN-EXGW-001; Exclusive BPMN-EXGW-002, BPMN-EXGW-003; Inclusive BPMN-EXGW-004, BPMN-EXGW-005; Event-Based BPMN-EXGW-006, BPMN-EXGW-007; Complex BPMN-EXGW-008, BPMN-EXGW-009, BPMN-EXGW-010, BPMN-EXGW-011, BPMN-EXGW-012; activities as implicit gateways BPMN-LIFE-001, BPMN-LIFE-003.

Reading for a model builder:

- A diverging Exclusive or Inclusive gateway with no default flow can throw at runtime if no condition is true. Because exclusive evaluation is ordered, the order of its outgoing flows matters (BPMN-EXGW-003).
- A Complex gateway whose activation expression never becomes true blocks its tokens and can deadlock the process. `activationCount` should appear only in subexpressions of the form `expr >= const` (BPMN-EXGW-009, BPMN-EXGW-012).
- An activity with several incoming flows is an implied exclusive merge (uncontrolled flow). Several unconditional outgoing flows act as a parallel split and conditional ones as an inclusive split. If tokens must be controlled, put an explicit gateway first (BPMN-LIFE-001).
- An Event-Based Gateway that instantiates a process as a parallel gateway allows only Message triggers, which must share correlation. This is narrower than the general gateway rule and applies to executable processes (BPMN-EXGW-007).

## 6. Tasks, sub-processes, ad-hoc and loops (13.3.3 to 13.3.7)

- A **Service Task** fills the operation's in-message from its data input, invokes it, then fills its data output from the out-message; a fault from the service is treated as an interrupting error. A **Send Task** sends a message and completes. A **Receive Task** waits for its message, fills its data output and completes; with key-based correlation only one receive per key can be active, and with `instantiate` it may start an instance. A **User Task** is distributed to the assigned person or group and completes when the work is done. **Business Rule** and **Script** tasks call the rule or script and complete when it returns (BPMN-LIFE-017, BPMN-LIFE-018, BPMN-LIFE-019, BPMN-LIFE-020, BPMN-LIFE-022).
- An executable Service, Send or Receive Task should name the operation or message it uses. The standard does not require it, but an executable model without them cannot run on a service engine (BPMN-LIFE-023).
- A **Sub-Process** is instantiated when a sequence-flow token reaches it. It has either one unique empty Start Event, which gets the token, or none, in which case every activity and gateway without incoming flow gets a token. It must not have non-empty start events (BPMN-SUBP-001, BPMN-SUBP-002). A Call Activity behaves the same way, and a called process should be enterable through an empty Start Event or through start-less activities (BPMN-SUBP-007, BPMN-SUBP-008).
- An **Ad-Hoc Sub-Process** contains only activities, flows, gateways and intermediate events (and data objects and associations). A performer, not the engine, picks which enabled activity runs next; `ordering` is sequential or parallel; after each inner activity the completion condition is evaluated and, when true, the sub-process completes. The standard does not say how an ad-hoc sub-process without a completion condition ends, so an executable one should have one (BPMN-SUBP-009, BPMN-SUBP-012, BPMN-SUBP-013, BPMN-SUBP-015).
- **Loops.** A standard loop repeats while its condition holds, with `testBefore` choosing pre-test or post-test and `loopMaximum` bounding it. Multi-instance evaluates the instance count once (cardinality, or the size of the input collection), creates instances in parallel or in sequence, and evaluates the completion condition after each. Its `behavior` (None, One, All, Complex) decides which events are thrown as instances complete. A multi-instance activity is compensated only if every instance completed (BPMN-SUBP-016, BPMN-SUBP-017, BPMN-SUBP-018, BPMN-SUBP-022).

## 7. Events at runtime (13.5)

- A catching event waits from the moment it is reached. A boundary event consumes the occurrence first; if it cancels, the activity is cancelled (every instance, for multi-instance), then flow follows the event's outgoing flow. The text limits non-canceling boundary events to four types while Table 10.92 allows six; the table governs (BPMN-EXEV-003).
- An Event Sub-Process creates its own scope, is started only by its start event while its parent runs, is not connected to normal flow, has no boundary events and sees its parent's data. An interrupting handler cancels the enclosing sub-process; a non-interrupting one runs in parallel. Several non-interrupting instances may run; only one interrupting handler may start per event definition, and after it starts no new handler does (BPMN-EXEV-004, BPMN-EXEV-005, BPMN-EXEV-006, BPMN-EXEV-007).
- Message-triggered catching events, event sub-processes and start events use the Receive Task correlation behavior (BPMN-EXEV-002, BPMN-EXEV-008).
- Terminate and Cancel end events end a sub-process abnormally; for a multi-instance sub-process only the affected instance ends (BPMN-SUBP-005, BPMN-EXEV-009, BPMN-EXEV-010).

## 8. Compensation and transaction (13.5.5, 10.3.5)

- Compensation reverses the effects of completed activities. An activity that is still active is cancelled, not compensated (BPMN-COMP-001).
- A handler is either a **Compensation Event Sub-Process** (for a process or sub-process; it sees a snapshot of the parent's data taken on completion) or an associated **Compensation Activity** (for any activity; a black box). A handler is not connected to normal flow and starts with a catching Compensation event (BPMN-COMP-002, BPMN-COMP-003, BPMN-COMP-004).
- Compensation is triggered by a throwing Compensation event (intermediate or end). It names the activity; if the activity is clear from context it defaults to the current one, and thrown in a global context with no activity named it compensates every completed activity. It is synchronous unless `waitForCompletion` is false (BPMN-COMP-006, BPMN-COMP-007).
- Presumed abort: compensating a failed activity does nothing. Without an error event sub-process, a sub-process that fails compensates its contained activities automatically (BPMN-COMP-009).
- Default order is the reverse of execution: a flow from A to B means B is compensated first; a data dependency, the same; in an ad-hoc sub-process, B first if A finished before B started; loop and sequential multi-instance instances reverse; parallel instances may compensate in parallel; a boundary-event branch is compensated before the activity it left (BPMN-COMP-011).
- Whether a boundary compensation handler runs once per instance of a multi-instance sub-process or once for all is stated both ways; the library records the conflict (BPMN-COMP-008). A sub-process attribute `compensable` that Clause 13 relies on is defined nowhere and is ignored (BPMN-COMP-005).
- A **Transaction** has three outcomes: success (normal flow), cancel (rollback, compensation, flow leaves by the Cancel boundary event) and hazard (flow leaves by an Error boundary event, the activity is interrupted, no compensation). Only cancellation compensates. The transaction protocol first confirms all participants before control moves up. For an executable process the method should be a technology-specific URI (BPMN-COMP-012, BPMN-COMP-013, BPMN-COMP-014, BPMN-COMP-015, BPMN-COMP-016).

## 9. Correlation, resources and services for execution

Execution depends on three groups of supporting concepts. Their rules are in `rules.md` under CORR, RSRC and SERV.

- **Correlation** (8.4.2). Key-based and context-based, as in `standard.md` section 10 (BPMN-CORR-003, BPMN-CORR-004, BPMN-CORR-005, BPMN-CORR-006, BPMN-CORR-007, BPMN-CORR-008, BPMN-CORR-009, BPMN-CORR-011).
- **Resources** (8.4.12, 10.3.1 to 10.3.4). A resource role references a resource or carries an assignment expression, never both; parameter bindings apply only with a resource reference; assignment expressions return users or groups (BPMN-RSRC-001, BPMN-RSRC-003, BPMN-RSRC-004, BPMN-RSRC-005).
- **Services** (8.5). An interface has at least one operation; an operation has exactly one in-message and at most one out-message; Service, Send and Receive tasks and Message event definitions name an operation, which is mandatory for message events in executable processes (BPMN-SERV-001, BPMN-SERV-002, BPMN-SERV-005).

## 10. The WS-BPEL mapping (Clause 14)

Clause 14 maps **one orchestration process (one pool)** to **one WS-BPEL 2.0 process**. It does not map diagrams, collaborations, choreographies or conversations (14.1, p. 445) (BPMN-BPEL-002, BPMN-BPEL-028). It is required for BPEL Process Execution Conformance (BPMN-BPEL-001). Two mappings exist: a **syntactic** one (14.2) for models built from block patterns, and a **semantic** one (14.3) that requires only the same observable behavior for other sound models (BPMN-BPEL-005, BPMN-BPEL-006, BPMN-BPEL-029). The mapped process must show the same observable behavior as the BPMN process.

### 10.1 Conditions a process must meet to be mappable

| # | Condition | Strength | Static check | Rule |
|---|---|---|---|---|
| 1 | One orchestration process, the process of one pool | must | static | BPMN-BPEL-002 |
| 2 | The process is sound: no deadlock, and no state with two tokens on a sequence flow | must | partial: needs reachability analysis; exact for structured models | BPMN-BPEL-003 |
| 3 | For the syntactic mapping, the graph decomposes into blocks (one entering and one leaving flow), blocks nested or disjoint | note | partial | BPMN-BPEL-004, BPMN-BPEL-005 |
| 4 | Service and Send tasks have an operation and a connected participant; Receive tasks have an operation | must | static | BPMN-BPEL-009, BPMN-BPEL-010 |
| 5 | Messages used by mapped tasks have a scalar, schema-typed item definition | must | partial | BPMN-BPEL-012 |
| 6 | A single input set and a single output set on Send, Service and Receive tasks | must | static | BPMN-BPEL-025 |
| 7 | Multi-instance only with flow condition All | must | static (inferred) | BPMN-BPEL-017 |
| 8 | Only the constructs the clause maps are used (section 10.3) | must | static (inferred) | BPMN-BPEL-011, BPMN-BPEL-015, BPMN-BPEL-018, BPMN-BPEL-019, BPMN-BPEL-020, BPMN-BPEL-021, BPMN-BPEL-022 |
| 9 | Names canonicalize to unique, valid XML names | must | static | BPMN-BPEL-008 |
| 10 | XPath context functions have string-literal arguments | must | static | BPMN-BPEL-027 |
| 11 | Unstructured loops and merges are allowed only through the extended mapping, with derived processes | must | partial | BPMN-BPEL-031, BPMN-BPEL-032, BPMN-BPEL-033, BPMN-BPEL-034 |

### 10.2 Constructs mapped

Status: `basic` is the syntactic mapping of 14.2; `extended` is 14.3; `not addressed` means the clause does not mention the construct. Absence is not a prohibition: the semantic mapping lets any sound process map if the BPEL behaves the same. User Task is mentioned once, as a candidate for a human-task extension (14.3, p. 469).

| BPMN construct | Condition | BPEL construct | Status | Section |
|---|---|---|---|---|
| Process (orchestration, in a pool) | must be sound; block-structured for the syntactic mapping | process (partnerLinks, variables, correlationSets, suppressJoinFailure=yes) | basic | 14.2.1 |
| Participant interface (own) | interfaces of the participant containing the process | partnerLink with myRole | basic | 14.2.1 |
| Participant interface (other participant) | interfaces of each other participant | partnerLink with partnerRole | basic | 14.2.1 |
| Data Object / Property | in the process or a scope; not from nested sub-processes | variable | basic | 14.2.1; 14.2.5 |
| CorrelationKey (key-based) | of the process's Conversations | correlationSet with properties and property aliases | basic | 14.2.1; 14.2.2 |
| Activity name |  | name (NCName, unique) | basic | Table 14.1 |
| Service Task | operation + connected participant | invoke | basic | 14.2.2 |
| Send Task | operation + connected participant | invoke | basic | 14.2.2 |
| Receive Task | operation; instantiate flag | receive (createInstance) | basic | 14.2.2 |
| Abstract Task (plain Task) |  | empty | basic | 14.2.2 |
| User Task |  | none in 14.2; BPEL4People suggested as an extension | extended (mentioned only) | 14.3 |
| Manual Task |  | not addressed | not addressed | 14 |
| Business Rule Task |  | not addressed | not addressed | 14 |
| Script Task |  | not addressed | not addressed | 14 |
| Call Activity / Global Task |  | not addressed | not addressed | 14 |
| Message | scalar item definition typed by an XML schema | WSDL 1.1 message (parts from top-level schema children) | basic | 14.2.2 |
| Interface, Operation | in-message, optional out-message, errors | WSDL 1.1 portType, operation, input, output, fault | basic | 14.2.2 |
| Embedded Sub-Process (ad-hoc false) |  | scope | basic | 14.2.2 |
| Ad-Hoc Sub-Process |  | not addressed | not addressed | 14 |
| Transaction Sub-Process |  | not addressed | not addressed | 14 |
| Event Sub-Process: non-interrupting Message |  | eventHandlers onEvent | basic | 14.2.2 |
| Event Sub-Process: Timer |  | eventHandlers onAlarm | basic | 14.2.2 |
| Event Sub-Process: Error |  | faultHandlers catch | basic | 14.2.2 |
| Event Sub-Process: Compensation |  | compensationHandler | basic | 14.2.2 |
| Event Sub-Process: interrupting Message, Signal, Escalation, Conditional |  | not addressed | not addressed | 14 |
| Standard loop, testTime before |  | while | basic | 14.2.2 |
| Standard loop, testTime after |  | repeatUntil (negated condition) | basic | 14.2.2 |
| Standard loop with loopMaximum |  | while or repeatUntil plus counter variable and assign | basic | 14.2.2 |
| Multi-instance, flow condition All |  | forEach (parallel unless sequential), scope | basic | 14.2.2 |
| Multi-instance, flow condition None, One, Complex |  | not addressed | not addressed | 14 |
| Message Start Event |  | receive createInstance=yes | basic | 14.2.3 |
| Error / Compensation Start Event | only in Event Sub-Process | see Event Sub-Process rows | basic | 14.2.3 |
| None, Timer, Conditional, Signal, Multiple Start Event |  | not addressed | not addressed | 14 |
| Message Intermediate Event (catch) | normal flow | receive createInstance=no | basic | 14.2.3 |
| Message Intermediate Event (throw) | normal flow | invoke | basic | 14.2.3 |
| Timer Intermediate Event | timeCycle or timeDate | wait for / wait until | basic | 14.2.3 |
| Compensation Intermediate Event (throw) | waitForCompletion true, inside error or compensation Event Sub-Process | compensate or compensateScope | basic | 14.2.3 |
| Signal, Escalation, Link, Conditional, Cancel intermediate events |  | not addressed | not addressed | 14 |
| None End Event |  | empty | basic | 14.2.3 |
| Message End Event |  | invoke | basic | 14.2.3 |
| Error End Event |  | throw | basic | 14.2.3 |
| Compensation End Event | waitForCompletion true, inside error or compensation Event Sub-Process | compensate or compensateScope | basic | 14.2.3 |
| Terminate End Event |  | exit | basic | 14.2.3 |
| Signal, Escalation, Cancel, Multiple End Event |  | not addressed | not addressed | 14 |
| Non-interrupting Message boundary event |  | scope with eventHandlers onEvent | basic | 14.2.3 |
| Non-interrupting Timer boundary event |  | scope with eventHandlers onAlarm | basic | 14.2.3 |
| Error boundary event |  | scope with faultHandlers (flow and links) | basic | 14.2.3 |
| Compensation boundary event |  | scope with compensationHandler | basic | 14.2.3 |
| Interrupting Message / Timer boundary; Signal, Escalation, Conditional boundary |  | not addressed | not addressed | 14 |
| Several boundary events on one Activity |  | superimposed on one scope; loops nested inside the scope | basic | 14.2.3 |
| Exclusive Gateway (data-based) block |  | if / elseif / else | basic | 14.2.4 |
| Event-Based Gateway block | Message events, Receive Tasks, Timer events | pick (createInstance from instantiate), onMessage, onAlarm | basic | 14.2.4 |
| Inclusive Gateway block (no otherwise gate) |  | flow with links and transitionConditions | basic | 14.2.4 |
| Parallel Gateway fork-join block |  | flow | basic | 14.2.4 |
| Sequence of Activities | unconditional flows | sequence | basic | 14.2.4 |
| Structured loop blocks | while or repeat shape | while / repeatUntil | basic | 14.2.4 |
| Complex Gateway |  | not addressed | not addressed | 14 |
| Input / Output Set (Send, Service, Receive) | single set | WSDL message with parts | basic | 14.2.5 |
| Data Input / Output Association | same structure as the message | toParts / fromParts | basic | 14.2.5 |
| Assignments on a Service Task |  | assign, invoke, assign | basic | 14.2.5 |
| XPath expressions with BPMN context functions | string-literal arguments | BPEL variable access (Table 14.2) | basic | 14.2.5 |
| Data Store, Group, Text Annotation, Pool/Lane, Conversation, Choreography |  | not addressed | not addressed | 14 |
| Unstructured block: distributed token recombination | sound process | semantic mapping, shape not fixed | extended | 14.3.1 |
| Loop from a gateway with 3 or more outgoing flows |  | while then switch in a sequence | extended | 14.3.2 |
| Interleaved loops |  | derived processes, spawn invoke and completion receive | extended | 14.3.3 |
| Infinite loop (no gateway) |  | while with condition 1 = 0 | extended | 14.3.4 |
| Element reached from several branches of a structured element |  | duplicate, or derived process invoked from each place | extended | 14.3.5 |

### 10.3 What the mapping does not cover

By a keyword scan of pp. 445 to 474, the clause does not mention: Script, Business Rule and Manual tasks, Call Activity, Global Task, Ad-Hoc Sub-Process, Transaction as a construct, Signal, Escalation, Link, Conditional and Cancel events, Complex Gateway, Data Store, Group, Text Annotation, pools and lanes as mapped constructs, and Choreography. Interrupting Message and Timer boundary events and interrupting event sub-processes of those types are not shown; only the non-interrupting ones are (BPMN-BPEL-011, BPMN-BPEL-015, BPMN-BPEL-018, BPMN-BPEL-019, BPMN-BPEL-020, BPMN-BPEL-021, BPMN-BPEL-022, BPMN-BPEL-028). These are inferred from absence, not stated.

### 10.4 Notes on the clause itself

- 14.2 uses the BPEL 2.0 `if`; 14.3 uses `switch`, a construct of BPEL 1.1 (BPMN-BPEL-036).
- 14.3 says to use the mappings of "sub clause 15.1"; 15.1 is about incomplete models, so this reads as a stale reference to 14.2 (BPMN-BPEL-030).
- The timer mapping uses time-cycle and time-date as `for` and `until` and does not mention time-duration (BPMN-BPEL-019).
- Loop attribute names: the clause writes `testTime`, the schema `testBefore`; the schema is followed (BPMN-BPEL-016).
- Unstructured shapes are mapped by the extended mapping: distributed token recombination, loops from a gateway with three or more outgoing flows, interleaved loops (derived processes that spawn each other), infinite loops (a loop with an always-false condition) and elements reached from several branches (duplicated or moved to a derived process) (BPMN-BPEL-031, BPMN-BPEL-032, BPMN-BPEL-033, BPMN-BPEL-034, BPMN-BPEL-035).
