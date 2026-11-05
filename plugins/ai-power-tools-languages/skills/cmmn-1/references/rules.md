# CMMN 1.1 rules

Generated from `language.yaml` (`constraints`). Do not edit by hand; change the language file and regenerate.

Each rule has a stable id of the form `CMMN-<CAT>-nnn`. The number never changes once assigned. A rule that is retired keeps its id and is marked withdrawn rather than reused.

The file holds 152 rules: 122 must, 5 should, 25 note. Section references are to the clauses, tables and pages of the CMMN 1.1 specification (formal/16-12-01); "p." gives the printed page.

## Strength

| Strength | Meaning | Treatment |
|---|---|---|
| must | The standard states it as a requirement ("MUST", "SHALL", "cannot", "only"), or a table or schema fixes it. A model that breaks it is not well formed. | An error. |
| should | The standard gives it as guidance, or states it in a way that conflicts with another clause and the rule's text says how the conflict was read. | A warning. |
| note | An explanation, option, or statement of expected practice recorded for completeness. | Advice only. |

Where the standard contradicts itself, the library follows its machine-readable model (the case model schema); where that is silent, the stricter reading; where neither settles it, the note on the rule says what was done. One deliberate exception: the schema relaxes some lower bounds (one case file, one case plan model, at least one case file item, one condition) so that incomplete models can be exchanged (9.1). The rules keep the text's bound as the rule and the note records the relaxation.

## Applies when

A rule with no `applies_when` applies to every model. `execution` means the rule is about a running case instance (clause 8) and is checked only when cases are executed; all LIF rules carry it, as does the TSK rule about failed references.

## Checkable

| Value | Meaning |
|---|---|
| `static` | a property or relationship of elements that a validator reading the saved model can check |
| `partial` | checkable only for the structure, in simple cases, or by reading what is drawn |
| `runtime` | describes running state; needs a live case instance |
| `none` | not a property of a model (a requirement on tools, drawing, or explanation) |

Rules whose strength is `must` and whose `checkable` is `static` are the candidates for machine checks; the rest are review guidance.

## Categories

| Category | Name | Covers | Rules |
|---|---|---|---|
| STR | Structure | The shape of a case: case file, case plan model, case file items and where they may sit. | 13 |
| REF | References and scope | Which definitions a plan item may refer to, and what must resolve inside the case. | 8 |
| CRT | Criteria and sentries | Entry and exit criteria, sentries, on-parts, and which standard events are legal. | 10 |
| PLN | Planning | Planning tables, discretionary items, and where each may refer. | 13 |
| TSK | Tasks | Blocking, parameters, and the references of process, case and decision tasks. | 11 |
| CTL | Item control | The plan item control and its manual activation, required and repetition rules. | 9 |
| DEC | Decorators | Which decorator goes on which shape, and what it shows. | 11 |
| EXP | Expressions | Conditions and timer expressions. | 5 |
| NOT | Notation | Shapes, lines and conformance of the drawing. | 10 |
| REL | Links between shapes | What connectors, discretionary associations and associations may join. | 7 |
| DI | Diagram interchange | Shapes, edges and diagrams as they are exchanged. | 15 |
| LIF | Lifecycle and execution | Run-time behavior of a case instance. Applies only when a case is executed. | 21 |
| XCH | Exchange and extension | The interchange file, references, and extension. | 8 |
| CONF | Conformance | What it takes to claim conformance. | 4 |
| GUID | Guidance | Advice the standard gives for modeling well. | 7 |

Multiplicities of the individual relationships are in `language.yaml` and are not repeated here. The decorator table (which decorator goes on which shape) is under `decorators` in `language.yaml` and in rules DEC-001 to DEC-009.

## STR: Structure

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| CMMN-STR-001 | must | A Case has exactly one case file and exactly one case plan model. *The schema allows zero of each so that incomplete models can be exchanged (9.1). Treat the lower bound as relaxed only for exchange.* | 5.2.1, Table 5.14, p. 20 | static |
| CMMN-STR-002 | must | The case plan model is a Stage, and it is the outermost stage of the case. | 5.2.1; 5.4; 5.4.8 | static |
| CMMN-STR-003 | must | The case plan model has no default control. | 5.4.1, Table 5.18, p. 24 | static |
| CMMN-STR-004 | must | Only the stage that is the case plan model may have stage-level exit criteria, and they refer to sentries contained in that stage. | 5.4.8, Table 5.34, p. 38 | static |
| CMMN-STR-005 | must | The case plan model has no entry criteria. | 8.4.1, p. 111; Table 6.1 | static |
| CMMN-STR-006 | must | A case file holds at least one case file item. *The schema allows none (interchange of incomplete models).* | 5.3.1, Table 5.16, p. 22 | static |
| CMMN-STR-007 | must | Every case file item has exactly one case file item definition. | 5.3.2, Table 5.17, p. 22 | static |
| CMMN-STR-008 | must | The children of a case file item never include that item or any item it is nested in (no containment cycle). | 5.3.2, Table 5.17, p. 23 | static |
| CMMN-STR-009 | must | The target references of a case file item never lead back to that item or to any item that refers to it (no reference cycle). | 5.3.2, Table 5.17, p. 23 | static |
| CMMN-STR-010 | must | A Definitions that contains a Case contains the imports and the case file item definitions that the case file items of that case need. | 5.1.2, Table 5.3, p. 12 | static |
| CMMN-STR-011 | should | For a case file item definition typed as an XML Schema element, complex type or simple type, an Import brings the schema into the model. *For other definition types the use of Import is not specified.* | 5.1.3, p. 13 | partial |
| CMMN-STR-012 | must | A Role is specific to its Case and is not known outside it. | 5.2.1, Table 5.14, p. 20 | partial |
| CMMN-STR-013 | must | When no extension is used, a reference to an information element means its latest version; the standard defines no versioning of case file items. | 5.3.2.1, p. 23 | none |

## REF: References and scope

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| CMMN-REF-001 | must | Reference associations between elements contained in a Case resolve within that Case, unless a rule says otherwise. | 5.1.1, p. 10 | static |
| CMMN-REF-002 | must | A PlanItem refers to exactly one PlanItemDefinition. | 5.4.5, Table 5.24, p. 30 | static |
| CMMN-REF-003 | must | A PlanItem never refers to the Stage that is the case plan model. | 5.4.5, Table 5.24, p. 30 | static |
| CMMN-REF-004 | must | A PlanItem never refers to a PlanFragment that is not a Stage. *Such a fragment can only be discretionary.* | 5.4.5, Table 5.24, p. 30 | static |
| CMMN-REF-005 | must | A PlanItem inside a Stage never refers to that Stage or to any Stage the Stage is nested in. | 5.4.5, Table 5.24, p. 30 | static |
| CMMN-REF-006 | must | A PlanItem refers only to a PlanItemDefinition defined in its own Stage or in a Stage that encloses it, up to the case plan model. A PlanItem inside a PlanFragment uses definitions of the fragment's parent Stage or above. | 5.4.1, p. 25; 5.4.5, Table 5.24, p. 30; 5.4.5.4, p. 31 | static |
| CMMN-REF-007 | must | Two Stages contained in the same parent do not refer to each other's contained elements; each may refer to elements of the parent. | 5.4.1, p. 25 | static |
| CMMN-REF-008 | must | A ProcessTask refers to a Process, and a DecisionTask to a Decision, contained by the Definitions that also contains the Case. | 5.1.2, Table 5.3, p. 13 | static |

## CRT: Criteria and sentries

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| CMMN-CRT-001 | must | A Sentry has an IfPart or at least one OnPart. | 5.4.6, p. 33 | static |
| CMMN-CRT-002 | must | The entry and exit criteria of a PlanItem refer to Sentries contained by the Stage or PlanFragment that contains the PlanItem. | 5.4.5.1, Table 5.25, p. 31 | static |
| CMMN-CRT-003 | must | A PlanItem defined by an EventListener has no entry criteria. | 5.4.5, Table 5.24, p. 30; 7.5.2.6 | static |
| CMMN-CRT-004 | must | A PlanItem defined by an EventListener or a Milestone has no exit criteria. | 5.4.5, Table 5.24, p. 30 | static |
| CMMN-CRT-005 | must | A PlanItem or DiscretionaryItem defined by a non-blocking Task has no exit criteria. | 5.4.5, Table 5.24, p. 30; 5.4.9.2, Table 5.37, p. 41 | static |
| CMMN-CRT-006 | must | Entry criteria belong only to items whose definition is a Task, Stage or Milestone. Exit criteria belong only to the case plan model and to items whose definition is a Task or Stage. | 7.5.2.6; 7.5.2.7; Tables 7.13, 7.14, pp. 101 to 102 | static |
| CMMN-CRT-007 | must | The standard event of a PlanItemOnPart or PlanItemStartTrigger is a transition of the lifecycle of the source PlanItem's kind: the Stage and Task lifecycle for a Stage or Task, the EventListener and Milestone lifecycle for an EventListener or Milestone. *Both tables point to 8.4.3 for the Stage and Task case; the Stage and Task lifecycle is in 8.4.2 (read as a typo).* | 5.4.2.1.3, Table 5.21; 5.4.6.3, Table 5.30, pp. 27, 35 | static |
| CMMN-CRT-008 | must | When a PlanItemOnPart names an exit criterion, that criterion is contained in the PlanItem the on-part names as its source. | 5.4.6.3, Table 5.30, p. 35 | static |
| CMMN-CRT-009 | must | When a PlanItemOnPart names an exit criterion, its standard event is exit. *The table words this as "when sentryRef is specified"; read as the exit criterion reference.* | 5.4.6.3, Table 5.30, p. 35 | static |
| CMMN-CRT-010 | must | A CaseFileItemOnPart and a CaseFileItemStartTrigger name exactly one source CaseFileItem and a transition from the CaseFileItem lifecycle. | 5.4.2.1.2, Table 5.20; 5.4.6.2, Table 5.28, pp. 27, 34 | static |

## PLN: Planning

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| CMMN-PLN-001 | must | A PlanningTable has at least one table item. | 5.4.9, Table 5.35, p. 40 | static |
| CMMN-PLN-002 | must | A PlanningTable never contains itself, directly or through nested planning tables. | 5.4.9, Table 5.35, p. 40 | static |
| CMMN-PLN-003 | must | A PlanningTable contains the ApplicabilityRules that its table items refer to. | 5.4.9.1, Table 5.36, p. 40 | static |
| CMMN-PLN-004 | must | The definition of a DiscretionaryItem is a Task, a PlanFragment or a Stage. | 5.4.9.2, Table 5.37, p. 41 | static |
| CMMN-PLN-005 | must | A DiscretionaryItem in the PlanningTable of a Stage refers to a definition in that Stage or in a Stage that encloses it. | 5.4.9.2, Table 5.37, p. 41 | static |
| CMMN-PLN-006 | must | A DiscretionaryItem in the PlanningTable of a HumanTask refers to a definition contained in the HumanTask's parent Stage or in a Stage that encloses it. | 5.4.9.2, Table 5.37, p. 41; 5.4.9.2.1, p. 42 | static |
| CMMN-PLN-007 | must | A Stage is not discretionary to itself or to any Stage nested in it. | 5.4.9.2, p. 41 | static |
| CMMN-PLN-008 | must | A Stage is not discretionary to a HumanTask that is the definition of a PlanItem contained in the Stage or its nested Stages. | 5.4.9.2, p. 42 | static |
| CMMN-PLN-009 | must | A HumanTask is not discretionary to itself. | 5.4.9.2, p. 42 | static |
| CMMN-PLN-010 | must | The entry and exit criteria of a DiscretionaryItem are contained in the Stage that holds the PlanningTable (directly or through nested tables), or in the Stage that holds the HumanTask that owns the table. | 5.4.9.2, p. 42 | static |
| CMMN-PLN-011 | must | A non-blocking HumanTask has no PlanningTable. | 5.4.10.4, Table 5.43, p. 47 | static |
| CMMN-PLN-012 | note | A PlanFragment that is not a Stage can only be used through a DiscretionaryItem, and when planned only its contained PlanItems are instantiated. | 5.4.4, p. 29; 5.4.9, p. 39 | none |
| CMMN-PLN-013 | note | A table item may list the Roles authorized to plan from it. For a HumanTask's table, the performer Role can also gate planning, or planners may need both the task role and the table item role. | 5.4.9; 5.4.10.4, pp. 40, 47 | none |

## TSK: Tasks

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| CMMN-TSK-001 | must | The isBlocking attribute of a Task defaults to true. | 5.4.10, Table 5.39, p. 45 | static |
| CMMN-TSK-002 | must | A non-blocking Task has no outputs. | 5.4.10, Table 5.39, p. 45 | static |
| CMMN-TSK-003 | must | A ProcessTask has exactly one of a process reference and a process reference expression. | 5.4.10.5, Table 5.44, p. 48 | static |
| CMMN-TSK-004 | must | A CaseTask has exactly one of a case reference and a case reference expression. | 5.4.10.6, Table 5.47, p. 49 | static |
| CMMN-TSK-005 | must | A DecisionTask has exactly one of a decision reference and a decision reference expression. | 5.4.10.7, Table 5.48, p. 50 | static |
| CMMN-TSK-006 | must | A ParameterMapping has exactly one source Parameter and one target Parameter. | 5.4.10.2, Table 5.41, p. 45 | static |
| CMMN-TSK-007 | must | The implementation type of a Process and of a Decision is a URI. *Defined values: BPMN 2.0, XPDL 2.x, WS-BPEL 2.0, WS-BPEL 1.x for processes; DMN 1.x for decisions.* | 5.4.10.5.1, Table 5.45; 5.4.10.7.1, Table 5.49, pp. 48, 51 | static |
| CMMN-TSK-008 | must | A task whose reference expression yields no existing Process, Case or Decision, or one whose parameters do not fit the task's mappings, fails: it moves to Failed when it becomes Active. (applies when: execution) | 5.4.10.5, 5.4.10.6, 5.4.10.7.1, pp. 47, 49, 51 | runtime |
| CMMN-TSK-009 | note | A non-blocking HumanTask is a "manual" task: the system does not track its lifecycle. | 5.4.10.4, p. 46 | none |
| CMMN-TSK-010 | note | A CaseTask starts another Case with its own case file (reuse); a Stage lives inside the current Case and shares its case file (composition). | 5.4.10.6, p. 49 | none |
| CMMN-TSK-011 | note | Outputs of a Task bound to a case file item show up as transitions of that item's lifecycle. Inputs of a Task and outputs of a Case only retrieve case file item instances. | 5.4.10.3, Table 5.42, p. 46 | none |

## CTL: Item control

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| CMMN-CTL-001 | must | A PlanItemControl is the itemControl of a PlanItem or DiscretionaryItem, or the defaultControl of a PlanItemDefinition. | 5.4.11, p. 53 | static |
| CMMN-CTL-002 | must | A PlanItemControl contains at least one of a repetition rule, a required rule and a manual activation rule. | 5.4.11, p. 53 | static |
| CMMN-CTL-003 | must | When a PlanItem or DiscretionaryItem has an item control, it overrides the default control of its definition. | 5.4.5, Table 5.24, p. 30; 5.4.9.2, Table 5.37, p. 41 | partial |
| CMMN-CTL-004 | must | A ManualActivationRule is not part of the control of an EventListener or of a Milestone. | 5.4.11, Table 5.51, p. 52; Table 5.55, p. 55 | static |
| CMMN-CTL-005 | must | A RequiredRule is not part of the control of an EventListener. | 5.4.11, Table 5.51, p. 53; Table 5.55, p. 55 | static |
| CMMN-CTL-006 | must | A RepetitionRule is not part of the control of an EventListener. *A timer's repetition is written inside its timer expression instead (5.4.11.3, p. 55).* | 5.4.11, Table 5.51, p. 53; Table 5.55, p. 55 | static |
| CMMN-CTL-007 | must | A PlanItem with a repetition rule has an entry criterion whose Sentry has at least one OnPart, or has no entry criteria at all. *Read for several entry criteria as "at least one has an on-part, or there are none"; the standard does not say.* | 5.4.11, Table 5.51, p. 53 | static |
| CMMN-CTL-008 | must | When no manual activation rule exists the default is true, when no required rule exists the default is false, and when no repetition rule exists the default is false. *The decorator for a rule is drawn only when the rule is defined, so an item without the manual activation decorator is by this default one that waits for a person.* | 5.4.11, Table 5.51, pp. 52 to 53 | partial |
| CMMN-CTL-009 | must | Repetition and required apply to a Stage, Task and Milestone. Manual activation applies to a Stage and Task. None of the three applies to an EventListener. *Summary of the four rules above, kept for the table the standard gives.* | 5.4.11.3, Table 5.55, p. 55 | static |

## DEC: Decorators

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| CMMN-DEC-001 | must | The AutoComplete decorator, a small black square at the bottom center, appears on a Stage or on the case plan model when autoComplete is true, and on no other shape. | 6.13.1, p. 75; 7.5.2.3, p. 96; Table 6.1, p. 79 | partial |
| CMMN-DEC-002 | must | The ManualActivation decorator, a small white right-pointing triangle, appears on a Stage or Task that has a manual activation rule defined, and on no other shape. | 6.13.2, p. 76; Table 6.1, p. 79 | partial |
| CMMN-DEC-003 | must | The Required decorator, a bold exclamation mark, appears on a Stage, Task or Milestone that has a required rule defined, and on no other shape. | 6.13.3, p. 77; Table 6.1, p. 79 | partial |
| CMMN-DEC-004 | must | The Repetition decorator, two bold vertical bars crossed by two bold horizontal bars, appears on a Stage, Task or Milestone that has a repetition rule defined, and on no other shape. | 6.13.4, p. 78; Table 6.1, p. 79 | partial |
| CMMN-DEC-005 | must | The planning table decorator appears only on the case plan model, a Stage and a HumanTask, attached to the top border between the top left corner and the middle. | 6.12, p. 73; 7.5.2.5, p. 100; Table 6.1, p. 79 | partial |
| CMMN-DEC-006 | must | The entry criterion decorator, an open diamond, appears only on a Stage, Task or Milestone. | 6.6, p. 61; Table 6.1, p. 79 | partial |
| CMMN-DEC-007 | must | The exit criterion decorator, a solid diamond, appears only on the case plan model, a Stage or a Task. | 6.6, p. 62; Table 6.1, p. 79 | partial |
| CMMN-DEC-008 | must | An EventListener, a CaseFileItem and a PlanFragment carry none of the decorators of Table 6.1. | Table 6.1, p. 79 | partial |
| CMMN-DEC-009 | must | The ManualActivation, Required and Repetition decorators are drawn at the bottom center of the shape, and are shown when the rule is defined on the PlanItem, the DiscretionaryItem or the definition they use. | 7.5.2.4, p. 97 | partial |
| CMMN-DEC-010 | note | Table 6.1 lets any Task carry an exit criterion decorator; the metamodel forbids exit criteria on non-blocking Tasks. The metamodel rule governs. *Inferred reading; the standard does not reconcile the two.* | Table 6.1, p. 79; 5.4.5, Table 5.24, p. 30 | none |
| CMMN-DEC-011 | note | A tool may add decorators or indicators to highlight an attribute or a new subtype, provided they do not change a defined shape. | 2.2, p. 3 | none |

## EXP: Expressions

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| CMMN-EXP-001 | must | Every condition expression (the if-part, an applicability rule, and the manual activation, required and repetition rules) evaluates to boolean. | 5.4.6.4, Table 5.32; 5.4.11, Table 5.51; 5.4.11.1 to 5.4.11.3, pp. 36, 52 to 54 | partial |
| CMMN-EXP-002 | must | An Expression has an optional language. When absent, the expressionLanguage of the Definitions applies (default XPath); a stated language overrides it for that expression. | 5.1.2, Table 5.3, p. 12; 5.4.7, Table 5.33, p. 37 | static |
| CMMN-EXP-003 | must | The body of an Expression is valid in its language. | 5.4.7, Table 5.33, p. 37 | partial |
| CMMN-EXP-004 | must | A timer expression evaluates to an ISO 8601 date and time, duration or interval. | 5.4.2.1, Table 5.19, p. 26 | partial |
| CMMN-EXP-005 | note | Where an item with a contextRef is evaluated, evaluation starts at that case file item; when no context is given, it starts at the case file. | 5.4.6.4, Table 5.32, p. 36 | none |

## NOT: Notation

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| CMMN-NOT-001 | must | A tool that creates and displays CMMN models uses the standard's shapes, markers and decorators. Size, fill, line color and label position are free. | 2.2, pp. 2 to 3 | none |
| CMMN-NOT-002 | must | An extension does not change the specified shape of a defined element or decorator, does not add a shape that conflicts with any CMMN or BPMN shape, and does not use a line style that conflicts with CMMN or BPMN. | 2.2, p. 3 | none |
| CMMN-NOT-003 | must | An EventListener circle is drawn with a double line. | 6.10, p. 68 | none |
| CMMN-NOT-004 | must | A connector is a dotted line with no arrowheads. *Section 6.11 also calls the connector a dash-dot-dot line in one sentence; the same clause calls the on-part connector dotted.* | 6.11, p. 69 | none |
| CMMN-NOT-005 | must | A discretionary association is a dashed line with no arrowheads. | 6.11, p. 70 | none |
| CMMN-NOT-006 | must | An Association is drawn with a dotted single line. An arrowhead may be added in one or both directions to show direction. | 6.14.1, p. 81 | none |
| CMMN-NOT-007 | must | A TextAnnotation is an open rectangle drawn with a solid single line. | 6.14.2, p. 81 | none |
| CMMN-NOT-008 | should | Tools that support BPMN compatibility use the alternative shapes of 6.8.2.1 and 6.8.3.1; tools that support DMN compatibility use that of 6.8.4.1. *Optional for others.* | 6.8.2.1, 6.8.3.1, 6.8.4.1, pp. 65 to 68 | none |
| CMMN-NOT-009 | note | CMMN is declarative: the relative position of shapes carries no meaning. | 6.2, p. 60 | none |
| CMMN-NOT-010 | note | Only the case file items that take part in the behavior of the case are drawn; the information model itself is not drawn. | 6.2, p. 59 | none |

## REL: Links between shapes

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| CMMN-REL-001 | must | An artifact is never the source or the target of a connector. | 5.5, p. 56 | static |
| CMMN-REL-002 | must | An artifact is never the source or the target of a discretionary association. | 5.5, p. 56 | static |
| CMMN-REL-003 | must | A connector depicts an OnPart. Its target is an entry criterion or exit criterion linked to the Sentry that holds the OnPart. Its source is the PlanItem the OnPart names, or the exit criterion the OnPart names when it names one, or the CaseFileItem of a CaseFileItemOnPart. | 7.4.7, p. 89; 7.5.3.1, 7.5.3.2, Tables 7.17, 7.18, pp. 103 to 104 | partial |
| CMMN-REL-004 | must | A discretionary association runs from a PlanItem or DiscretionaryItem that is a HumanTask to a DiscretionaryItem that is defined in that HumanTask's planning table. | 7.4.7, pp. 88 to 89; 7.5.3.3, Table 7.19, p. 105 | partial |
| CMMN-REL-005 | must | An Association has a direction of None (no arrowhead), One (arrowhead at the target) or Both. | 5.5.1, Table 5.56, p. 57 | static |
| CMMN-REL-006 | note | Connectors are visual only and have no execution semantics. | 8.8, p. 124 | none |
| CMMN-REL-007 | note | Links between shapes, other than associations, are drawn for dependencies shown inside an expanded Stage or PlanFragment. | 6.11, p. 69 | none |

## DI: Diagram interchange

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| CMMN-DI-001 | must | Every shape and edge refers to a model element. A shape or edge with no reference, or an invalid one, is not depicted. The one exception is the edge for a discretionary association, which refers to no element. | 7.5, p. 92 | static |
| CMMN-DI-002 | must | A shape refers to a case plan model, a PlanItem, a DiscretionaryItem, an EntryCriterion, an ExitCriterion, a CaseFileItem or a TextAnnotation. | 7.4.6, Table 7.4, p. 87 | static |
| CMMN-DI-003 | must | A shape has bounds. | 7.4.6, Table 7.4, p. 87 | static |
| CMMN-DI-004 | must | An edge has at least two waypoints. | 7.4.7, Table 7.5, p. 89 | static |
| CMMN-DI-005 | must | A PlanItem is depicted at most once in one diagram, and it may be depicted in different diagrams. Connectors for OnParts may appear once per entry or exit criterion. | 7.4.1, p. 84 | static |
| CMMN-DI-006 | must | A diagram refers to a Definitions, a case plan model, a Stage or a PlanFragment. | 7.4.4, Table 7.2, p. 86 | static |
| CMMN-DI-007 | must | A diagram does not contain another diagram, and elements nested in a diagram have positive coordinates. | 7.4.4, p. 85 | static |
| CMMN-DI-008 | must | Shapes and edges are ordered so that what must be drawn on top comes after what lies beneath it. | 7.4.1, p. 84 | static |
| CMMN-DI-009 | must | The edge for an OnPart refers to that OnPart, gives no source, and gives as target the criterion linked to the Sentry that holds the OnPart. The edge for an Association refers to that Association and gives neither source nor target. | 7.4.7, Table 7.5, pp. 88 to 89 | static |
| CMMN-DI-010 | must | The edge for a discretionary association refers to no model element, gives as source the HumanTask item and as target the DiscretionaryItem, and shows no label. | 7.4.7, p. 88; 7.5.3, p. 93 | static |
| CMMN-DI-011 | must | A PlanItem is drawn with a solid border and a DiscretionaryItem with a dashed border. | 7.5.2.2, p. 93 | none |
| CMMN-DI-012 | must | When a planning table is expanded, its discretionary items are drawn inside the Stage or the case plan model, or, for a HumanTask, joined to it by discretionary associations. | 7.5.2.5, Table 7.12, p. 101 | none |
| CMMN-DI-013 | must | Entry and exit criterion shapes are attached to the border of the item they belong to. | 7.5.2.6, 7.5.2.7, pp. 101 to 102 | static |
| CMMN-DI-014 | note | The diagram interchange data does not decide whether a diagram is correct; to draw a diagram, both it and the referenced model are needed. | 7.1, 7.2, p. 83 | none |
| CMMN-DI-015 | note | Colors and fonts in styles have no CMMN meaning. | 7.4.9, p. 91 | none |

## LIF: Lifecycle and execution

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| CMMN-LIF-001 | must | When a Case instance is created, the outermost Stage instance is Active at once; it has no entry criteria and skips the Available state. (applies when: execution) | 8.2, 8.4.1, Table 8.6, pp. 107, 111 to 112 | runtime |
| CMMN-LIF-002 | must | A Case completes when every required Milestone, Stage and Task instance in the outermost Stage is finished and no Stage or Task instance is Active. (applies when: execution) | 8.4.1, Tables 8.5, 8.6, p. 112 | runtime |
| CMMN-LIF-003 | must | A Closed Case has a read-only case file and accepts no new Task or Stage instances. (applies when: execution) | 8.4.1, Table 8.5, p. 112 | runtime |
| CMMN-LIF-004 | must | A Stage or Task instance becomes Available when its containing Stage becomes Active, or when a Sentry with an OnPart sourced outside the enclosing Stage is satisfied (the enclosing Stages then become Active as needed). A missing entry criterion counts as satisfied. (applies when: execution) | 8.4.2, Table 8.7, p. 114 | runtime |
| CMMN-LIF-005 | must | When an entry Sentry is satisfied, the manual activation rule decides the next state: true moves the instance from Available to Enabled, false moves it to Active. (applies when: execution) | 8.4.2, Table 8.8, p. 115; 8.6.2, p. 122 | runtime |
| CMMN-LIF-006 | must | Disabled, Failed and (for finishing a Stage) Completed and Terminated instances count as finished when judging whether the parent Stage can complete. (applies when: execution) | 8.4, p. 111 | runtime |
| CMMN-LIF-007 | must | A Stage propagates suspend, resume and terminate to all its contained EventListener, Milestone, Stage and Task instances. A fault does not propagate. (applies when: execution) | 8.4.2, Tables 8.8, 8.9, pp. 115 to 119 | runtime |
| CMMN-LIF-008 | must | A Stage completes under Table 8.12: with autoComplete true, when no child is Active and every required child is Disabled, Completed, Terminated or Failed. With autoComplete false it also needs manual completion, unless all children are finished and there are no discretionary items. (applies when: execution) | 8.6.1, Table 8.12, p. 122 | runtime |
| CMMN-LIF-009 | must | A required instance is Disabled, Completed, Terminated or Failed before its parent Stage completes. The required rule is evaluated when the instance is created (and again on enabling if its value is false) and the value is kept. (applies when: execution) | 8.6.3, p. 122; 8.4.2, Table 8.8, pp. 115 to 116 | runtime |
| CMMN-LIF-010 | must | The repetition rule is evaluated when an instance is created and its first value is discarded. It is evaluated again whenever an entry criterion with an OnPart is satisfied and creates a new instance if true. With no entry criteria it is evaluated when an instance completes or terminates. (applies when: execution) | 5.4.11.3, p. 54 to 55; 8.6.4, pp. 122 to 123 | runtime |
| CMMN-LIF-011 | must | A Sentry is satisfied when all its OnParts have occurred and its IfPart, if any, is true; a Sentry with no OnPart is satisfied when its IfPart is true. (applies when: execution) | 8.5, p. 121 | runtime |
| CMMN-LIF-012 | must | One satisfied entry criterion is enough to leave Available; one satisfied exit criterion is enough to terminate an Active instance. (applies when: execution) | 8.5, p. 121 | runtime |
| CMMN-LIF-013 | must | Entry Sentries are evaluated while the item is Available; exit Sentries while the case plan model, Stage or Task is Active. (applies when: execution) | 8.5, p. 121 | runtime |
| CMMN-LIF-014 | must | An exit transition moves an Available, Enabled, Disabled, Active, Suspended or Failed Stage or Task instance to Terminated when an exit criterion is satisfied or when the parent terminates. (applies when: execution) | 8.4.2, Table 8.8, p. 116 | runtime |
| CMMN-LIF-015 | must | An EventListener or Milestone instance starts Available and moves to Completed on occur: the event happens, a person raises a user event, or an entry criterion of a Milestone is satisfied. It can be suspended, resumed and terminated. (applies when: execution) | 8.4.3, Tables 8.10, 8.11, pp. 120 to 121 | runtime |
| CMMN-LIF-016 | must | A CaseFileItem instance is Available when created. Update, replace, add or remove child and add or remove reference keep it Available. Delete moves it to Discarded, which is terminal. (applies when: execution) | 8.3, Tables 8.1, 8.2, pp. 107 to 108 | runtime |
| CMMN-LIF-017 | must | Planning is allowed only in the states of Table 8.13. Planned items are instantiated at once when the Stage is Active, otherwise when it becomes Active. Planning from a HumanTask adds items to its parent Stage. (applies when: execution) | 8.7, Table 8.13, p. 124 | runtime |
| CMMN-LIF-018 | must | Only table items whose applicability rule is true are shown to a case worker in an authorized Role; a table item with no applicability rule is applicable. (applies when: execution) | 5.4.9.1, Table 5.36, p. 40; 8.6.5, p. 124 | runtime |
| CMMN-LIF-019 | must | A blocking Task waits until its work is done. A non-blocking Task completes as soon as it is instantiated (a ProcessTask or CaseTask then has already started the called Process or Case). (applies when: execution) | 5.4.10, Table 5.39, p. 45; 5.4.10.5, 5.4.10.6, pp. 47, 49 | runtime |
| CMMN-LIF-020 | should | A TimerEventListener with a start trigger measures its timer expression from the moment the trigger occurs. (applies when: execution) | 5.4.2.1, Table 5.19, p. 26 | runtime |
| CMMN-LIF-021 | must | The navigation operations over the case file return an empty instance when nothing matches. (applies when: execution) | 8.3.1, Table 8.3, pp. 108 to 109 | runtime |

## XCH: Exchange and extension

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| CMMN-XCH-001 | must | The root element of an interchange file is definitions. The files of a model are self-contained: everything they use is imported, directly or indirectly. Each file declares a target namespace. | 9.3.1, p. 125 | static |
| CMMN-XCH-002 | must | References use identifiers; across files they use a qualified name whose local part is the identifier. | 9.3.2, pp. 125 to 126 | static |
| CMMN-XCH-003 | should | Importers of an incomplete model disregard missing required attributes and reduced lower bounds. | 9.1, p. 125 | none |
| CMMN-XCH-004 | must | An extension definition is bound to a Definitions by an Extension before it is used; mustUnderstand is false unless stated. *Not used when the XML schema is the exchange format.* | 5.1.5, 5.1.5.1, Table 5.9, pp. 16 to 17 | partial |
| CMMN-XCH-005 | must | The value of an extension attribute conforms to the type its definition gives. *Not used when the XML schema is the exchange format.* | 5.1.5.4, Table 5.12, p. 18 | partial |
| CMMN-XCH-006 | note | Extension attributes and elements may be lost in interchange; the standard elements stay intact. | 5.1.5, p. 15 | none |
| CMMN-XCH-007 | must | A Relationship has at least one source and one target and a direction of None, Forward, Backward or Both. | 5.1.6, Table 5.13, p. 19 | static |
| CMMN-XCH-008 | must | A Property type and a definition type are values of the lists in Tables 5.8 and 5.6, written as URIs. *The schema lists two more definition types (WSDL message, UML class).* | 5.1.4, 5.1.4.1, Tables 5.6, 5.8, pp. 14 to 15 | static |

## CONF: Conformance

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| CMMN-CONF-001 | note | Software may claim conformance only if it matches all applicable compliance points; otherwise it may only say it is based on the standard. | 2.1, p. 1 | none |
| CMMN-CONF-002 | should | A tool claiming Case Modeling, BPMN Compatibility or Complete conformance meets Visual Notation Conformance. *2.1 says required; 2.3, 2.4 and 2.6 say "should".* | 2.1, p. 1; 2.3, 2.4, 2.6, pp. 3 to 4 | none |
| CMMN-CONF-003 | note | A tool is not required to support an optional feature or one the standard calls non-normative; if it supports one, it supports it as specified. | 2.1, pp. 1 to 2 | none |
| CMMN-CONF-004 | note | CMMN Complete Conformance covers the metamodel, notation, diagram interchange, execution semantics and exchange format; Case Modeling Conformance does not require the execution semantics beyond what Table 2.1 lists. | 2.3, 2.6, Table 2.1, pp. 2 to 4 | none |

## GUID: Guidance

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| CMMN-GUID-001 | note | Use a Stage for an episode of a case that is tracked as a unit, and a PlanFragment for a reusable pattern of items and sentries that needs no tracking of its own. | 5.4.4, 5.4.8, pp. 28 to 29, 37 | none |
| CMMN-GUID-002 | note | To plan from a particular task, give a HumanTask a planning table instead of adding a Stage that holds a single item. | 5.4.10.4, pp. 46 to 47 | none |
| CMMN-GUID-003 | note | Set autoComplete to false on Stages that hold discretionary items or optional work. | 5.4.8, Table 5.34, p. 38 | none |
| CMMN-GUID-004 | note | A Milestone has no work of its own; it is reached by finishing Tasks or by information becoming available in the case file. | 5.4.3, p. 28 | none |
| CMMN-GUID-005 | note | Use a UserEventListener when a person's decision should drive the case directly, and a TimerEventListener when only the passing of time matters, instead of encoding either as data in the case file. | 5.4.2, p. 25 | none |
| CMMN-GUID-006 | note | A model may start entirely at the discretion of case workers and gain repeatable patterns as experience grows. | 4.2, p. 7 | none |
| CMMN-GUID-007 | note | Assignment of Roles to people or teams is outside the standard. | 5.2.2, p. 20 | none |
