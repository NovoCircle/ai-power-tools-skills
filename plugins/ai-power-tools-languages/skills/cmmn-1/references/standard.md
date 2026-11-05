# CMMN 1.1 in our own words

This is a section-by-section reading of the OMG Case Management Model and Notation, version 1.1 (formal/16-12-01, December 2016, https://www.omg.org/spec/CMMN/1.1/). It paraphrases the standard and quotes only short phrases. Section numbers are the standard's; page numbers are printed pages. The standard is the authority; where this file and the standard differ, the standard wins and the difference is a defect here.

Machine-readable forms the standard calls normative: the XML schemas `CMMN11.xsd` and `CMMN11CaseModel.xsd`, the diagram interchange schema `CMMNDI11.xsd`, and UML profile files, all at https://www.omg.org/spec/CMMN/20151109/. Where this file says "the schema", it means the case model schema.

No newer version was found. 1.0 (May 2014) is the only earlier formal version.

## 1 Scope (p. 1)

CMMN defines a metamodel and a notation for modeling a case, plus an interchange format. It is to case management what BPMN is to business processes, and is meant to be consistent with BPMN. Case management suits work that cannot be fully pre-planned: the path depends on circumstances and on decisions by knowledge workers. Typical uses: permits, insurance claims, patient care, mortgage processing, problem resolution.

## 2 Conformance (pp. 1 to 4)

Software may claim conformance only if it meets the applicable compliance points in full; otherwise it may say only that it is "based on" CMMN. Five compliance points:

| Point | What it requires |
|---|---|
| Visual Notation (2.2) | Use the standard's shapes, markers and decorators. Size, fill, line color, label position are free. Extensions allowed: new decorators or indicators, new shapes for a kind of case file item or plan item, colors, line styles. Not allowed: changing a defined shape, a new shape that conflicts with any CMMN or BPMN shape, a line style that conflicts with a CMMN or BPMN line style. |
| Case Modeling (2.3) | Clauses 5, 6 and 8 as listed in Table 2.1, the full metamodel, the full notation, the exchange format. For modeling-only tools. |
| BPMN Compatibility (2.4) | The optional alternative shapes of 6.8.2.1 and 6.8.3.1 become required. |
| DMN Compatibility (2.5) | The optional alternative shapes of 6.8.4.1 become required. |
| CMMN Complete (2.6) | Metamodel, notation, interchange format and the execution semantics. For tools that model and execute. |

The text is inconsistent about whether Visual Notation Conformance is required for the others (2.1 says required; 2.2 to 2.6 say "should"). This guide does not settle it.

## 4 Additional information (pp. 5 to 8)

A case is a proceeding about a subject in a situation to achieve an outcome. Case management is directed by people (a case manager or a team) with little predefined encoding of the work. Planning at run time is the defining characteristic: choosing tasks, ordering them, collaborating ad hoc. The case file holds data about the case; rules reference it. Execution semantics are shaped by the guard-stage-milestone approach to business entity lifecycles.

A case has two phases. **Design time**: analysts define the tasks that always belong to the case and the *discretionary* tasks that case workers may add. **Run time**: case workers perform the plan, and may add discretionary items to it while it runs (Figure 4.1).

## 5.1 Core infrastructure (pp. 9 to 19)

- **CMMNElement** (5.1.1): abstract base of every class. Attributes: an id, documentation, extension definitions and values. Reference associations between elements inside one case must resolve inside that case unless stated otherwise.
- **Documentation** (5.1.1.1): a text and a mime-type text format (default `text/plain`).
- **Definitions** (5.1.2): the outermost container of every interchange. It holds a name, a target namespace, a default expression language (default XPath), exporter, exporter version, author, creation date, imports, case file item definitions, cases, processes, decisions, relationships, the diagram interchange data and artifacts. A Definitions that contains a case must contain the imports and case file item definitions that the case's case file items need. Process tasks and decision tasks must refer to processes and decisions in the same Definitions.
- **Import** (5.1.3): an import type, a location and a namespace. For XML-Schema-typed definitions the import should be used to bring the schema in; for other types its use is not specified.
- **CaseFileItemDefinition** (5.1.4): a definition type URI, an optional structure reference (qualified name), an optional import reference, and properties. Definition types (Table 5.6): CMIS folder, CMIS document, CMIS relationship, XSD element, XSD complex type, XSD simple type, Unknown, Unspecified (the schema adds WSDL message and UML class).
- **Property** (5.1.4.1): a name and a type URI from Table 5.8 (string, boolean, integer, float, double, duration, dateTime, time, date, gYearMonth, gYear, gMonthDay, gDay, gMonth, hexBinary, base64Binary, anyURI, QName, decimal, Unspecified).
- **Extensibility** (5.1.5): a model can be extended without breaking conformance. An Extension binds an ExtensionDefinition to a Definitions (with a "must understand" flag, default false). An ExtensionDefinition groups attribute definitions; an ExtensionAttributeDefinition gives a name, type and whether values are references; an ExtensionAttributeValue holds the value or reference. With the XML schema these classes are not used; "any attribute" and "any element" do the job.
- **Relationship** (5.1.6): a typed link (type string, direction None, Forward, Backward or Both, one or more sources and targets) between CMMN elements and elements of any other model, so a case can be related to, for example, a use case, without changing either.

## 5.2 Case model elements (pp. 20 to 21)

- **Case** (5.2.1): has a name, one case file (the case file model), one case plan model (a Stage), roles, and input and output case parameters so it can be called, for example by another case.
- **Role** (5.2.2): authorizes case workers to perform human tasks, to plan using discretionary items, and to raise user events. Examples: doctor, patient, nurse. Who plays a role is outside the standard.

## 5.3 Information model (pp. 21 to 23)

- **CaseFile** (5.3.1): the logical container of the information a case uses as context; at least one case file item. It says nothing about physical storage.
- **CaseFileItem** (5.3.2): any information element: a CMIS folder or document, a whole hierarchy, an XML document. Name, a multiplicity (how many instances a case instance may hold), exactly one definition. Items nest by containment (children, parent) or are tied by reference (target references, source reference). Neither chain may contain a cycle. Where the content structure is known, an XML Schema can be imported.
- **Versioning** (5.3.2.1): not defined. When no extension is used, a reference to an information element means its latest version.

## 5.4 Plan model elements (pp. 23 to 55)

### 5.4.1 PlanItemDefinition

Abstract. The building block of plans. It has a name and an optional default control. Its subtypes: EventListener, Milestone, PlanFragment (with Stage), Task. A definition belongs to a stage and may be used from that stage and from stages nested inside it; one stage cannot refer to the content of a sibling stage. The case plan model stage has no default control.

### 5.4.2 EventListener

An event is something that happens during a case. Standard events are the transitions of the lifecycles of case file items, stages, tasks, milestones and event listeners. Elapsed time and a user's decision cannot be captured that way, so EventListener adds two kinds, each with its own lifecycle so that time and user events also become standard events handled by sentries.

- **TimerEventListener** (5.4.2.1): catches a point in time or an elapse. A timer expression (ISO 8601 date and time, duration or interval) and an optional start trigger that anchors the expression; if there is a trigger, the expression is relative to the moment the trigger occurs. Repetition is written inside the expression (the "R<n>/" notation).
- **StartTrigger** (5.4.2.1.1): abstract. CaseFileItemStartTrigger (a case file item transition on a given item) and PlanItemStartTrigger (a plan item transition on a given plan item) occur when that transition happens.
- **UserEventListener** (5.4.2.2): catches an event a user raises. It lists the roles authorized to raise it.

### 5.4.3 Milestone

An achievable target for judging progress. No work is attached to it. Finishing tasks or having key information typically achieves it.

### 5.4.4 PlanFragment

A set of plan items, possibly dependent on each other through sentries, that often occur together. Plan items and sentries are contained in it. It is a plan item definition because the whole combination can be added to a plan as a unit, but a plain plan fragment has no lifecycle at run time: only the items inside it are instantiated and tracked. A plain plan fragment can only be discretionary (a plan item cannot refer to it).

### 5.4.5 PlanItem

A use of a definition inside a plan fragment or stage. A definition is defined once and used by many plan items. A plan item has a name that overrides the definition's, an optional item control that overrides the definition's default control, a reference to exactly one definition, and entry and exit criteria.

Rules (Table 5.24):

- It must not refer to the case plan model stage, or to a plain plan fragment.
- It must not refer to the stage that contains it, or any stage enclosing it. Because plan items can refer to stages, stages can nest.
- It can only refer to a definition defined in its own stage or an enclosing one. A plan item inside a plan fragment refers to a definition in the fragment's parent stage or above. Example 5.4.5.4 works this out for a stage tree.
- An item defined by an event listener has no entry criteria; an item defined by an event listener or a milestone has no exit criteria; an item defined by a non-blocking task has no exit criteria.
- **Criterion** (5.4.5.1) is abstract: an optional name and a reference to a sentry. The sentry must be in the stage or plan fragment containing the plan item. **EntryCriterion** (5.4.5.2) is the condition for a plan item to become available. **ExitCriterion** (5.4.5.3) is the condition for it to terminate. Neither adds attributes.

### 5.4.6 Sentry

A sentry watches for events and conditions. It can be "on event if condition", "on event" or "if condition". Parts: zero or more **OnParts** (the events) and zero or one **IfPart** (the condition over the case file). It is satisfied when all on-parts have occurred and the if-part, if present, is true. A satisfied entry sentry makes the item available (a task or stage is enabled, a milestone is achieved); a satisfied exit sentry makes a task or stage terminate. A sentry must have an if-part or at least one on-part.

- **OnPart** (5.4.6.1): abstract, with an optional name. **CaseFileItemOnPart** (5.4.6.2): a case file item transition on a source case file item. **PlanItemOnPart** (5.4.6.3): a plan item transition on a source plan item, optionally by way of one exit criterion of that plan item (then the event must be "exit", and the criterion must belong to the source item). The event must belong to the lifecycle of the source's kind.
- **CaseFileItemTransition** (5.4.6.2.1, Table 5.29): addChild, addReference, create, delete, removeChild, removeReference, replace, update.
- **PlanItemTransition** (5.4.6.3.1, Table 5.31): close, complete, create, disable, enable, exit, fault, manualStart, occur, parentResume, parentSuspend, reactivate, reenable, resume, start, suspend, terminate. Which applies to which kind and which lifecycle states they connect is in `language.yaml` (lifecycles).
- **IfPart** (5.4.6.4): an optional context case file item (evaluation starts there; otherwise at the case file) and a condition expression that evaluates to boolean.

### 5.4.7 Expressions

Strings over the properties and items of the case file. Constant and time-based expressions are also allowed. An optional language URI overrides the Definitions default.

### 5.4.8 Stage

A plan fragment with a run-time lifecycle. It can be a plan item inside another stage, can have a planning table, and can be the case's plan model. Stages are the "episodes" of a case, though several can run in parallel.

- `autoComplete` (default false): if false, a user must complete the stage manually (suited to stages with discretionary items or optional work); see 8.6.1.
- `planningTable` (optional).
- `exitCriteria`: only the case plan model stage may have them, and they must refer to sentries inside that stage.
- The plan model stage may also hold sentries that serve as its exit criteria.

### 5.4.9 PlanningTable

Planning is a run-time effort. A planning table scopes it: which definitions a case worker may consider. Context is a stage (the table plans tasks and stages into that stage instance) or a human task (the table plans follow-up items into the stage containing the human task).

- **PlanningTable**: one or more table items; may nest; must not contain itself; contains the applicability rules its table items refer to.
- **TableItem** (5.4.9.1): a discretionary item or a planning table; may list authorized roles and applicability rules. An item with no applicability rule is applicable.
- **DiscretionaryItem** (5.4.9.2): identifies a task, plan fragment or stage a case worker may add; has a name, an optional item control that overrides the definition's default control, and entry and exit criteria. A discretionary item of a non-blocking task has no exit criteria. Placement rules: a stage's table refers to definitions in that stage or above; a human task's table refers to definitions in the human task's parent stage or above; a stage is never discretionary to itself, its nested stages, or a human task that is a plan item inside it; a human task is never discretionary to itself; criteria of a discretionary item sit in the stage that contains the table (or contains the human task that owns it). Example 5.4.9.2.1 works out a tree.
- **ApplicabilityRule** (5.4.9.3): a name, an optional context case file item, a condition expression. If false the table item is not shown for planning.

### 5.4.10 Task

An atomic unit of work. `isBlocking` (default true): a blocking task waits until the work is done; a non-blocking task completes as soon as it is instantiated. A non-blocking task has no outputs. It has input and output case parameters.

- **Parameter** (5.4.10.1): abstract, with a name. **ParameterMapping** (5.4.10.2): a source parameter, a target parameter and an optional transformation expression, for tasks that call processes, cases or decisions. **CaseParameter** (5.4.10.3): may bind to a case file item (`bindingRef`) and refine the binding with an expression.
- **HumanTask** (5.4.10.4): performed by a case worker; at most one performer role. Non-blocking means a "manual" task whose lifecycle the system does not track. It may have a planning table (not if non-blocking), which lets planning start from the task: follow-up items, a narrower table than the stage's, no extra single-item stages, and an extra role gate.
- **ProcessTask** (5.4.10.5): calls a **Process** (an abstraction of a process in another standard; implementation types BPMN 2.0, XPDL 2.x, WS-BPEL 2.0, WS-BPEL 1.x). Exactly one of a process reference and a process reference expression. An expression is evaluated when the task becomes active; if it yields no existing, compatible process, the task fails.
- **CaseTask** (5.4.10.6): starts an instance of another **Case** with its own case file (reuse) rather than embedding a stage in this case's file (composition). Exactly one of a case reference and an expression, same failure rule.
- **DecisionTask** (5.4.10.7): calls a **Decision** (implementation type DMN 1.x) with parameters; same one-of rule and failure rule.

### 5.4.11 PlanItemControl

Controls a plan item, discretionary item or (as a default) a definition. It holds at least one of three rules, each with a boolean condition, an optional context case file item and a name:

- **ManualActivationRule** (5.4.11.1): when true, an enabled task or stage waits for a human to start it; when false it starts by itself. If the rule is absent the default is considered true (Table 5.51).
- **RequiredRule** (5.4.11.2): when true, the item must reach Disabled, Completed, Terminated or Failed before its stage can complete. Absent means false.
- **RepetitionRule** (5.4.11.3): when true, the item may be instantiated again; each repetition is a new instance. Absent means false. Repetition is triggered when an entry criterion whose sentry has an on-part is satisfied; for an item with no entry criteria it is evaluated when an instance completes or terminates. The first instantiation is not a repetition; its value is discarded. A plan item with a repetition rule has an entry criterion with an on-part, or no entry criteria.

Applicability (Table 5.55): repetition and required apply to stage, task and milestone; manual activation applies to stage and task; none applies to event listeners (Table 5.51 says the same in prose; a timer's repetition is written in its timer expression).

### 5.5 Artifacts (pp. 55 to 57)

Two standard artifacts. **Association**: links an artifact or information to any element; direction None (default), One (arrowhead at the target) or Both. **TextAnnotation**: text and a text format for the reader; it does not affect execution. An artifact is never an end of a connector or a discretionary association. Tools may add other artifact types.

## 6 Notation (pp. 59 to 82)

CMMN is declarative: do not read meaning into where shapes sit. Only the case file items that matter to behavior are drawn; the information model is not drawn.

| Concept | Depiction |
|---|---|
| Case plan model (6.3) | A folder shape: a rectangle with a small tab at top left that can hold the case name. Everything in the plan sits inside. |
| Case file item (6.4) | A document shape: a rectangle with a cut upper-right corner. |
| Stage (6.5) | A rectangle with angled corners and a small box at bottom center: plus when collapsed, minus when expanded. Discretionary: same with short dashed lines. |
| Plan fragment (6.7) | Rectangle with dashed lines and softly rounded corners, with plus or minus marker. |
| Task (6.8) | A rectangle with rounded corners. Discretionary: dashed lines. |
| Human task (6.8.1) | Rounded rectangle with a hand symbol at upper left when non-blocking, a user symbol when blocking. |
| Case task (6.8.2) | Rounded rectangle with a folder symbol at upper left. |
| Process task (6.8.3) | Rounded rectangle with a chevron symbol at upper left. |
| Decision task (6.8.4) | Rounded rectangle with a decision table symbol at upper left. |
| Case, process, decision task for compatibility (6.8.2.1, 6.8.3.1, 6.8.4.1) | Optional alternative: the same symbol plus a collapsed marker and, for case and process task, a thick border. Required only for BPMN or DMN compatibility conformance. |
| Milestone (6.9) | A rectangle with half-rounded ends. May have entry criteria. |
| Event listener (6.10) | A double-line circle with an open center; the circle must be double. Timer: clock marker. User: user marker. |
| Entry criterion (6.6) | An open (shallow) diamond on the boundary of the item. |
| Exit criterion (6.6) | A solid diamond on the boundary of the item. |
| Planning table (6.12) | A small table shape of six cells with a plus (items not shown) or minus (items shown) in the bottom center cell, only as a decorator on the boundary of a stage or human task. Expanding it shows discretionary items inside the stage, or outside the human task joined by discretionary associations. |
| Connector (6.11) | A dotted line with no arrowheads, for an on-part: between a plan item (or its exit criterion, or a case file item) and the entry or exit criterion it feeds. By the sentry rule, connectors that feed one criterion are on-parts of one sentry and all must occur ("and"); connectors that feed different criteria are alternatives ("or"). The figures that show this (6.37, 6.38) are images and were not read. |
| Discretionary association (6.11) | A dashed line with no arrowheads from a human task to the discretionary items of its planning table. |
| Association (6.14.1) | A dotted single line, optional arrowhead(s). |
| Text annotation (6.14.2) | An open rectangle with a solid single line. |

Decorators (6.13, Table 6.1; see section 5.5 here and `language.yaml`):

| Decorator | Glyph | Means | Applies to |
|---|---|---|---|
| AutoComplete | small black square at bottom center | The stage has `autoComplete` true | Stage, case plan model |
| ManualActivation | small white right-pointing triangle | A manual activation rule is defined | Stage, task |
| Required | bold exclamation mark | A required rule is defined | Stage, task, milestone |
| Repetition | hash sign (two bold vertical bars crossed by two bold horizontal bars) | A repetition rule is defined | Stage, task, milestone |
| Planning table | six-cell table | The item has a planning table | Case plan model, stage, human task |
| Entry criterion | open diamond | The item has an entry criterion | Stage, task, milestone |
| Exit criterion | solid diamond | The item has an exit criterion | Case plan model, stage, task |

A decorator is visible when the rule is defined for the plan item or discretionary item, or for its definition (7.5.2.4). Event listeners, case file items and plan fragments take none of the decorators in Table 6.1.

Worked patterns of connectors (6.11.1): task C waits for tasks A and B (two connectors into one criterion), task C starts when A or B ends (a connector into each of two criteria), stage B depends on the exit of stage A, a task depends on a milestone, a timer, or a case file item.

## 7 CMMN diagram interchange (pp. 83 to 105)

Diagram interchange carries layout and look only; everything else comes from the model. Rendering needs both. It does not check that the diagram is correct. A diagram is "a snapshot": several diagrams can show parts of one model.

- **CMMNDI**: the container of shared styles and all diagrams of a Definitions.
- **CMMNDiagram**: name, documentation, resolution (default 300 units per inch), optional size, optional local and shared style, a reference to the element it depicts (a Definitions, case plan model, stage or plan fragment), and the ordered shapes and edges. Order is Z-order. Only positive coordinates. A diagram cannot contain another diagram.
- **CMMNShape**: bounds (required), a reference to a case plan model, plan item, discretionary item, entry criterion, exit criterion, case file item or text annotation; `isCollapsed` (stage and plan fragment); `isPlanningTableCollapsed`.
- **CMMNEdge**: at least two waypoints. An on-part connector references the on-part; the source is derived from the on-part's source (or its exit criterion) and the target is the entry or exit criterion that links to the on-part's sentry; an option shows or hides the standard event in the label. An association edge references the association. A discretionary association edge references no model element: its source is the plan item or discretionary item of the human task holding the table, its target is the discretionary item.
- **CMMNLabel**: derived from the element's name; position optional. No label on a discretionary association.
- **CMMNStyle**: fill, stroke and font properties, non-normative.
- A plan item is shown once per diagram (on-part connectors may appear once per criterion); it may appear in different diagrams.
- Depiction (7.5): plan items solid, discretionary items dashed; entry criteria attach to items referring to a task, stage or milestone; exit criteria attach to the case plan model or to items referring to a task or stage; decorators sit at the bottom center except the planning table (top border, between the top-left corner and the middle). When a planning table is expanded, its discretionary items are shown inside the stage or case plan model, or joined to the human task by discretionary associations.

## 8 Execution semantics (pp. 107 to 124)

Most semantics are lifecycles of case file items, stages, tasks, milestones and event listeners, plus behavior property rules. Connectors have no semantics (8.8).

**Case instance (8.2).** A case instance is the case file plus the plan model behavior plus roles. On creation all three are initialized and the outermost stage is Active. While the case is not Closed, the case file can change, planning can happen and people can be assigned.

**Case file item lifecycle (8.3).** States: Available, Discarded. Transitions: create (to Available), update, replace, addChild, removeChild, addReference, removeReference (all stay Available), delete (to Discarded, terminal). Task outputs bound to a case file item can cause these. Navigation operations (get instance by name, by name and index, property, child, parent, target, source) return an empty instance when nothing matches.

**Nine states (8.4, Table 8.4).** Active, Available, Closed, Completed, Disabled, Enabled, Failed, Suspended, Terminated. Terminal: Closed, Terminated, and Completed (except for a case, where Completed is semi-terminal). Semi-terminal (can be left, but counts as finished when judging whether a stage is done): Disabled, Failed.

**Case lifecycle (8.4.1).** The case lifecycle is the lifecycle of the outermost stage, which has no entry criteria and skips Available. Transitions: create (to Active), suspend, terminate (a human decision, propagated down), complete (when all required milestone, stage and task instances are finished and none is Active), fault (to Failed), re-activate (from Completed, Terminated, Failed or Suspended back to Active), close (from the same four states, terminal; the case file becomes read only and no further planning).

**Stage and task lifecycle (8.4.2).** Instances start Available when the containing stage becomes Active, or when a sentry whose on-part comes from outside the enclosing stage is satisfied (the enclosing stages become Active as needed). A missing entry criterion counts as satisfied. Transitions: create, enable (Available to Enabled, if the manual activation rule is true when the sentry is satisfied), start (Available to Active, if it is false), disable (Enabled to Disabled), reenable, manualStart (Enabled to Active), suspend and resume, fault (Active to Failed, not propagated), reactivate (Failed to Active), complete (Active to Completed), terminate (Active to Terminated), exit (any of Available, Active, Enabled, Disabled, Suspended, Failed to Terminated, by an exit criterion or when the parent terminates), parentSuspend and parentResume (return to the prior state). The required rule is evaluated at creation (value kept); the repetition rule is evaluated at creation (first value discarded); the manual activation rule is evaluated when the sentry is satisfied. A stage propagates suspend, resume and terminate to its children (Table 8.9).

**Event listener and milestone lifecycle (8.4.3).** States Available, Suspended, Completed, Terminated. Transitions: create, occur (Available to Completed: the event happens, or a user raises it, or an entry criterion of a milestone is satisfied), suspend, resume, terminate, parent terminate. A milestone's repetition and required rules are evaluated at creation.

**Sentry evaluation (8.5).** Any one of several entry criteria suffices to leave Available; likewise any one of several exit criteria triggers termination. A sentry with no on-part must have an if-part, evaluated whenever case file item events arrive.

**Behavior property rules (8.6).** Stage `autoComplete` (Table 8.12): with it true a stage completes when no child is Active and every required child is in Disabled, Completed, Terminated or Failed; with it false it also needs a manual completion (or, with no discretionary items and all children finished, may complete). Manual activation: true moves Available to Enabled, false to Active. Required: a required child must be Completed, Terminated, Failed or Disabled before the parent completes. Repetition: re-evaluated at each satisfied entry on-part (or, with no entry criteria, at completion or termination of an instance); a new instance is created if true. Applicability: only applicable table items are shown to an authorized case worker.

**Planning (8.7, Table 8.13).** Planning is allowed while a case plan model is Active, Failed, Suspended, Completed or Terminated; a stage is Active, Available, Enabled, Disabled, Failed or Suspended; a human task is Active. Planned items are instantiated at once if the stage is Active, otherwise when it becomes Active. Planning from a human task adds to its parent stage.

## 9 Exchange formats (pp. 125 to 126)

Incomplete models may be interchanged: importers disregard missing required attributes and reduced lower bounds in the schema. The root element of a file is `definitions`; a file set is self-contained through imports; each file has a target namespace that may differ across files; non-CMMN files such as XML Schemas and BPMN may be imported. References use ids (`IDREF`, `IDREFS`); across files they use a qualified name whose local part is the id.
