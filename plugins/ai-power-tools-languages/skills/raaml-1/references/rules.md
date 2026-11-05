# RAAML 1.0 rules

Generated from `language.yaml` (`constraints`). Do not edit by hand; change the language file and regenerate.

Each rule has a stable id of the form `RAAML-<CAT>-nnn`. The number never changes once assigned. A rule that is retired keeps its id and is marked withdrawn rather than reused.

## Strength

| Strength | Meaning |
|---|---|
| must | The standard states it as a numbered constraint, in OCL, as "must" or "only", or as a multiplicity in its machine-readable model. A model that breaks it is not well formed. Reported as an error. |
| should | The standard recommends it, or states a reference formula or a modeling practice that its profile does not enforce. Reported as a warning. |
| note | The standard states it as a description, an intention or a statement about tools. Advice only; not reported on its own. |

## Checkable

| Value | Meaning |
|---|---|
| static | A check that sees only the saved model can decide it. |
| partial | Only the structure or simple cases can be checked; the rest needs judgment. |
| runtime | Needs instances or an executing evaluation (for example a probability calculation). |
| none | Not a property of a model (guidance, definition or a rule about a tool). |

## Categories

| Category | Name | Covers | Rules |
|---|---|---|---|
| SIT | Situation modeling | How situations, scenarios and their attributes are modeled: the root, redefinition, steps, value properties, and what the standard leaves to the modeler. | 10 |
| REL | Relationship endpoints | Which kinds of element a relationship may join: RelevantTo, Violates, the controlling measures, and the Causality family. | 8 |
| MARK | Marker applicability | Where a profile marker may be applied: fault tree events, gates and trees, FMEA items, transfer nodes. | 8 |
| CARD | Cardinality and required parts | How many of one thing another must or may have: failure modes, causes, effects, top events, gate inputs and outputs, accident scenarios, values. | 19 |
| VAL | Values and formulas | Value ranges and formulas: fault tree probabilities, the gate reference formulas, the risk priority number. | 14 |
| GSN | Argument structure | Which GSN nodes the two GSN relationships may join, and how a node is named and identified. | 9 |
| STPA | Control and loss analysis | The shape of an unsafe control action and a loss scenario, the causal links, and the control loop. | 7 |
| ISO | Hazard analysis and risk assessment | Rationale requirements, ASIL decomposition, malfunction classes, and the flow from malfunction to safety requirement. | 11 |
| CONF | Conformance | What conformance means for a tool. Not properties of a model. | 4 |
| GUID | Guidance | Method notes and design intent that are not checkable. | 6 |

Counts: 96 rules: 49 must, 19 should, 28 note. Section references are to the clauses of the RAAML 1.0 specification (formal/22-12-06); "p." gives the printed page; "[n]" is the number of the item in an entry's Constraints list; "Examples" is the informative Examples document (ptc/21-11-22). Multiplicities on the individual relationships and attributes are in `language.yaml` and are not repeated here.

## SIT: Situation modeling

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| RAAML-SIT-001 | should | partial | Every situation specializes AnySituation, directly or through intermediate situations. AnySituation is the universal root of all situations. | 9.1.1, p. 20; 7.3, p. 12 |
| RAAML-SIT-002 | should | partial | A situation is modeled as a block. The steps of a scenario are composite part properties typed by sub-situations. Attribute values of a situation are value properties whose type describes the possible values and whose default value holds the value. | 7.3, p. 12 |
| RAAML-SIT-003 | should | partial | A user situation that inherits from a library situation redefines or subsets the properties of the library situation. | 7.3, p. 12 |
| RAAML-SIT-004 | must | static | A redefining property has a type that is narrower than (a specialization of) the type of the property it redefines. The normal rules of property redefinition apply. | 7.3.1 item c, p. 13 |
| RAAML-SIT-005 | note | none | Properties a user adds beyond those the library defines are user-specific extensions and are not part of this language. | 7.3, p. 12 |
| RAAML-SIT-006 | note | none | Generalization between two situations means the occurrences of the specific situation are a subset of the occurrences of the general one. | 9.1, p. 19 |
| RAAML-SIT-007 | should | partial | The steps of a scenario have a causal ordering, shown by Causality relationships or specializations of them. | 9.2.1 (Scenario), p. 32 |
| RAAML-SIT-008 | note | none | A situation may omit any parameter it need not be specific about. Whether to model a composite situation with sub-situations or a single situation is the modeler's choice, depending on the depth of analysis. | 9.1, pp. 19-20 |
| RAAML-SIT-009 | note | none | The names of subsetting properties are not regulated. A scheme of parent property name plus a number is strongly recommended. | 7.3.1 item e, p. 13 |
| RAAML-SIT-010 | note | none | Quantitative attributes of a situation, such as probability of occurrence, are value properties; formulas that relate attributes to each other and to system attributes are constraint blocks and may be written in any language the tool can compute. | 9.1, Table 9.1, pp. 19-20 |

## REL: Relationship endpoints

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| RAAML-REL-001 | must | static | The client of a RelevantTo relationship is a Situation. | 9.1.2 (RelevantTo) [1], p. 23 |
| RAAML-REL-002 | must | static | The supplier of a ControllingMeasure relationship (and of its kinds Detection, Prevention, Mitigation and Recommendation) is a Situation. | 9.1.2 (ControllingMeasure) [1], p. 23 |
| RAAML-REL-003 | must | static | The client of a Violates relationship is a Situation. | 9.1.2 (Violates) [1], p. 24 |
| RAAML-REL-004 | note | none | Violates connects a situation to a requirement, design constraint or any element that prescribes a characteristic of the system. RelevantTo connects a situation to the system-model element that gives it context. | 9.1.2, pp. 22-23 |
| RAAML-REL-005 | must | static | Every Causality relationship, and every specialization of it, joins two situations: the from end and the to end are AnySituation. | 9.1.1 (Causality), p. 21 |
| RAAML-REL-006 | must | static | Activation joins an abstract cause (the fault end) to a dysfunctional event (the error end). | 9.2.1 (Activation), p. 30 |
| RAAML-REL-007 | must | static | ErrorPropagation joins a dysfunctional event (the predecessor error) to a dysfunctional event (the successor error). | 9.2.1 (ErrorPropagation), p. 31 |
| RAAML-REL-008 | must | static | ErrorRealization joins a dysfunctional event (the predecessor error) to a dysfunctional event (the resulting failure). | 9.2.1 (ErrorRealization), p. 31 |

## MARK: Marker applicability

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| RAAML-MARK-001 | must | static | The Tree marker applies only to a class that specializes FTATree. | 9.4.2 (Tree) [1], p. 57 |
| RAAML-MARK-002 | must | static | A fault tree event marker (DormantEvent, BasicEvent, ConditionalEvent, ZeroEvent, HouseEvent, IntermediateEvent, TopEvent) applies only to a class that specializes the library event of the same name, or to a property whose type does. | 9.4.2 (each marker) [1], pp. 58-68 |
| RAAML-MARK-003 | must | static | A fault tree gate marker (AND, OR, SEQ, XOR, INHIBIT, MAJORITY_VOTE, NOT) applies only to a class that specializes the library gate of the same name, or to a property whose type does. | 9.4.2 (each marker) [1], pp. 62-67 |
| RAAML-MARK-004 | must | static | A class that carries both the BasicEvent and the Undeveloped markers specializes UndevelopedEvent. | 9.4.2 (BasicEvent) [2], p. 59 |
| RAAML-MARK-005 | must | static | A class that carries the Event marker also carries the Situation marker or a marker that specializes it. | 9.4.2 (Event), p. 57 |
| RAAML-MARK-006 | must | static | The FMEAItem marker applies only to a class that specializes AbstractFMEAItem. | 9.3.2 (FMEAItem) [1], p. 44 |
| RAAML-MARK-007 | must | static | The type of a TransferIn property is a fault tree that carries the TransferOut marker. | 9.4.2 (TransferIn) [1], p. 69 |
| RAAML-MARK-008 | note | none | The Undeveloped marker flags an incomplete concept. It combines with Goal or Strategy in an argument, or with a basic event in a fault tree. | 9.2.2 (Undeveloped), p. 38; 9.6.1, p. 82 |

## CARD: Cardinality and required parts

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| RAAML-CARD-001 | must | static | An FMEA item has exactly one failure mode. | 9.3.1 (AbstractFMEAItem), p. 39 |
| RAAML-CARD-002 | must | static | An FMEA item has at least one cause. | 9.3.1 (AbstractFMEAItem), p. 39 |
| RAAML-CARD-003 | must | static | An FMEA item has at least one final effect. | 9.3.1 (AbstractFMEAItem), p. 39 |
| RAAML-CARD-004 | must | static | An FMEA item has no harm potential. The property is redefined to multiplicity zero because the method does not use it. | 9.3.1 (AbstractFMEAItem), p. 39 |
| RAAML-CARD-005 | must | static | A fault tree has exactly one top event. | 9.4.1 (FTATree), p. 45 |
| RAAML-CARD-006 | must | static | A gate has exactly one output event. | 9.4.1 (Gate), p. 50 |
| RAAML-CARD-007 | must | static | An INHIBIT gate has a single input event. Its enabling conditions are zero or more events. | 9.4.1 (INHIBIT), pp. 52-53 |
| RAAML-CARD-008 | should | static | A NOT gate has exactly one input event. | 9.4.1 (NOT; NOTConstraintBlock), pp. 51, 56 |
| RAAML-CARD-009 | should | partial | The priority of an event is used only to order the inputs of a priority-AND (SEQ) gate. | 9.4.1 (Event), p. 46 |
| RAAML-CARD-010 | must | static | A MAJORITY_VOTE gate has exactly one threshold m. | 9.4.1 (MAJORITY_VOTE), p. 53 |
| RAAML-CARD-011 | must | static | An unsafe control action has exactly one context, which is an operational situation. | 9.5.1 (UnsafeControlAction), p. 75 |
| RAAML-CARD-012 | must | static | A hazardous event has exactly one accident scenario. | 9.7.1 (HazardousEvent), p. 98 |
| RAAML-CARD-013 | must | static | An accident scenario has at least one operational situation, exactly one malfunctioning behavior and exactly one controllability value. | 9.7.1 (AccidentScenario), pp. 100-101 |
| RAAML-CARD-014 | must | static | An abstract operational situation has exactly one exposure value. | 9.7.1 (AbstractOperationalSituation), p. 92 |
| RAAML-CARD-015 | must | static | An automotive effect has exactly one severity value. | 9.7.1 (AutomotiveEffect), p. 99 |
| RAAML-CARD-016 | must | static | A safety requirement template has exactly one ASIL and one fault tolerant time interval. | 9.7.1 (ISO26262SafetyRequirementTemplate), p. 100 |
| RAAML-CARD-017 | must | static | An ASIL assignment has exactly one ASIL value and at most one override value. | 9.7.2 (ASILAssignment), p. 112 |
| RAAML-CARD-018 | must | static | A Verified or Confirmed marker carries exactly one result. | 9.7.2 (Verified; Confirmed), p. 110 |
| RAAML-CARD-019 | must | static | An identifier carrier holds exactly one identifier string. | 9.1.2 (IDCarrier), p. 24 |

## VAL: Values and formulas

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| RAAML-VAL-001 | must | static | The probability of a fault tree element is a real value from 0 to 1. | 9.4.1 (FTAElement), p. 45 |
| RAAML-VAL-002 | must | static | The probability of a house event is 0 or 1 and is set before the fault tree is evaluated. | 9.4.1 (HouseEvent), p. 49 |
| RAAML-VAL-003 | must | static | The probability of a zero event is always 0. | 9.4.1 (ZeroEvent), p. 49 |
| RAAML-VAL-004 | should | runtime | The probability of an intermediate event is derived by its gate from the probabilities of the events below it. The probability of the top event is the derived result of the tree calculation. Applies when: a probability evaluation is run. | 9.4.1 (IntermediateEvent; TopEvent), p. 47 |
| RAAML-VAL-005 | should | runtime | The probability of an AND gate output is the product of the input probabilities, assuming the inputs are independent. Applies when: a probability evaluation is run. | 9.4.1 (ANDConstraintBlock), p. 54 |
| RAAML-VAL-006 | should | runtime | The probability of an OR gate output is one minus the probability that no input occurs, assuming independence. Applies when: a probability evaluation is run. | 9.4.1 (ORConstraintBlock), p. 54 |
| RAAML-VAL-007 | should | runtime | The probability of a SEQ gate output is computed as for an AND gate, the product of the input probabilities. This cannot capture time dependence. Applies when: a probability evaluation is run. | 9.4.1 (SEQConstraintBlock), pp. 54-55 |
| RAAML-VAL-008 | should | runtime | For two inputs the probability of an XOR gate output is a + b - 2ab, applied iteratively for more inputs, assuming independence. Applies when: a probability evaluation is run. | 9.4.1 (XORConstraintBlock), p. 55 |
| RAAML-VAL-009 | should | runtime | The probability of an INHIBIT gate output is the product of the input probabilities and the condition probability, assuming independence. Applies when: a probability evaluation is run. | 9.4.1 (INHIBITConstraintBlock), pp. 55-56 |
| RAAML-VAL-010 | should | runtime | The probability of a MAJORITY_VOTE gate output is the combined probability of all input combinations in which at least m inputs occur, assuming independence. Applies when: a probability evaluation is run. | 9.4.1 (MAJORITY_VOTEConstraintBlock), p. 56 |
| RAAML-VAL-011 | should | runtime | The probability of a NOT gate output is one minus the probability of its input. Applies when: a probability evaluation is run. | 9.4.1 (NOTConstraintBlock), p. 56 |
| RAAML-VAL-012 | should | runtime | The risk priority number of an FMEA item is the product of occurrence, detectability and severity. Applies when: the RPN calculation is used. | 9.3.1 (RPNCalculation), p. 41 |
| RAAML-VAL-013 | note | none | The abstract event, cause, effect, failure mode and risk classes declare placeholder attributes (likelihood, occurrence, severity, detectability, score) with no type. Method-specific classes give them a type; the Real-valued Cause, Effect and FailureMode are the general implementations. | 9.2.1, pp. 25-34 |
| RAAML-VAL-014 | note | none | The majority threshold m of a MAJORITY_VOTE gate need not be half the number of inputs; for example 2 of 7 can be stipulated. | 9.4.1 (MAJORITY_VOTE), p. 53 |

## GSN: Argument structure

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| RAAML-GSN-001 | must | static | The client of an InContextOf relationship is a goal or a strategy. | 9.6.1 (InContextOf) [1], p. 87 |
| RAAML-GSN-002 | must | static | The supplier of an InContextOf relationship is contextual information (a context, assumption or justification) or a non-GSN element. It is never another kind of GSN node. | 9.6.1 (InContextOf) [2], p. 87 |
| RAAML-GSN-003 | note | none | Permitted InContextOf connections are goal to context, goal to assumption, goal to justification, strategy to context, strategy to assumption and strategy to justification. | 9.6.1 (InContextOf), p. 87 |
| RAAML-GSN-004 | must | static | The client of a SupportedBy relationship is a goal or a strategy. | 9.6.1 (SupportedBy) [1], p. 88 |
| RAAML-GSN-005 | must | static | When the client of a SupportedBy relationship is a strategy, the supplier is a goal. | 9.6.1 (SupportedBy) [2], p. 88 |
| RAAML-GSN-006 | must | static | The supplier of a SupportedBy relationship is a GSN node or a non-GSN element. It is never contextual information. | 9.6.1 (SupportedBy) [3], p. 88 |
| RAAML-GSN-007 | must | static | The client of a SupportedBy relationship is not marked Undeveloped: a goal or strategy that supports others is developed. | 9.6.1 (SupportedBy) [4], p. 88 |
| RAAML-GSN-008 | note | none | Permitted SupportedBy connections are goal to goal, goal to strategy, goal to solution and strategy to goal. | 9.6.1 (SupportedBy), p. 87 |
| RAAML-GSN-009 | must | partial | The short phrase of a GSN node is the name of the element. Its human-readable identifier is stored separately, in the identifier carrier. | 9.6.1 (GSNNode), p. 83 |

## STPA: Control and loss analysis

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| RAAML-STPA-001 | must | static | ProcessModelFactor joins a Factor to a ProcessModel; ProcessModelConsequence joins a ProcessModel to an UnsafeControlAction; UnsafeControlActionHarmPotential joins an UnsafeControlAction to a HarmPotential. | 9.5.1, pp. 77-78 |
| RAAML-STPA-002 | should | partial | An unsafe control action has four parts: the controller that issues the control action (inferred from the control action and the system model), the guideword (given by generalization), the control action (linked by RelevantTo) and the context (a sub-situation). | 9.5.1 (UnsafeControlAction), p. 74 |
| RAAML-STPA-003 | should | partial | A loss scenario is a sequence of situations that starts from factors, passes through process model deficiencies and leads to an unsafe control action. | 9.5.1 (LossScenario), p. 72 |
| RAAML-STPA-004 | note | none | RiskRealization associates a loss with a hazard. | 9.5.1 (RiskRealization), p. 76 |
| RAAML-STPA-005 | note | none | Process model deficiencies come in four high-level kinds: inadequate controller decisions, inadequate control execution, inadequate process behavior, and inadequate feedback and inputs. | 9.5.1 (ProcessModel), p. 72 |
| RAAML-STPA-006 | note | none | A controller sends control actions to a controlled process through an actuator and receives feedback from the controlled process through a sensor. | 9.5.2, pp. 78-80 |
| RAAML-STPA-007 | note | none | The seven unsafe control action guidewords (Provided, NotProvided, Early, Late, OutOfSequence, TooLong, TooShort) can be tailored in the library as the user wishes. | 9.5.1, pp. 69-71; Examples 2.3 |

## ISO: Hazard analysis and risk assessment

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| RAAML-ISO-001 | must | static | The exposure of an operational situation has a rationale attached. | 9.7.1 (AbstractOperationalSituation), p. 92 |
| RAAML-ISO-002 | must | static | The severity of an automotive effect has a rationale attached. | 9.7.1 (AutomotiveEffect), p. 99 |
| RAAML-ISO-003 | must | static | The controllability of an accident scenario has a rationale attached. | 9.7.1 (AccidentScenario), p. 100 |
| RAAML-ISO-004 | must | static | An ASIL override value has an associated rationale (an ASIL override rationale). | 9.7.2 (ASILAssignment), p. 112 |
| RAAML-ISO-005 | must | static | ASILDecompose relations are applied in pairs: a requirement is never the supplier of a single ASILDecompose relation. | 9.7.2 (ASILDecompose), p. 105 |
| RAAML-ISO-006 | should | none | The supplier of an ASILDecompose relation is at a higher level of abstraction than its client. | 9.7.2 (ASILDecompose), p. 105 |
| RAAML-ISO-007 | must | partial | A malfunction class (Less, More, No, Intermittent, Unintended, Early, Late, Inverted) is connected to a behavioral element, a use case or a function. | 9.7.1, pp. 94-97 |
| RAAML-ISO-008 | should | partial | A UserInfoRequirement runs from a state (client) to a functional or technical safety requirement (supplier). A RecoveryRequirement links a safe state to a requirement that gives the recovery criteria. | 9.7.2, p. 106 |
| RAAML-ISO-009 | note | none | An IndependenceRequirement states an independence criterion that must be satisfied for an ASIL decomposition, between a parent requirement and two other children, to be valid. | 9.7.2 (IndependenceRequirement), p. 104 |
| RAAML-ISO-010 | note | none | Risk analysis identifies hazards that could result from a malfunctioning behavior; with an operational situation these give an accident scenario, held in a hazardous event that gives the risk level (ASIL). Safety goals derive from hazardous events; functional safety requirements from safety goals; technical safety requirements from functional ones; hardware and software safety requirements from technical ones. | 9.7, p. 89; Examples 2.5 (informative) |
| RAAML-ISO-011 | note | none | The ASIL of a hazardous event redefines the score of the abstract risk; its values are defined in an enumeration in the ISO 26262 package. | Examples 2.5 (informative), p. 24 |

## CONF: Conformance

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| RAAML-CONF-001 | note | none | Interchange conformance (type 1): a tool can import and export conformant XMI for all valid models of the language. | 2, p. 6 |
| RAAML-CONF-002 | note | none | View specification conformance (type 2): a tool implements the views the specification defines. | 2, p. 6 |
| RAAML-CONF-003 | note | none | A tool vendor may implement one method (FMEA, FTA, STPA, GSN or ISO 26262) and claim conformance to it. | 2, p. 6 |
| RAAML-CONF-004 | note | none | The language library and profile import the entire SysML profile, so a RAAML model is a SysML model. | 9, p. 19 |

## GUID: Guidance

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| RAAML-GUID-001 | note | none | The language relies heavily on model libraries with a light profile. Users extend the libraries by specializing library classes, because practices differ across domains and organizations. | 7.2, p. 11 |
| RAAML-GUID-002 | note | none | The general package gives a common base for the methods, traceability across safety and reliability artifacts, and a foundation on which new methods or domains can be built. | 9.2, pp. 24-25 |
| RAAML-GUID-003 | note | none | To combine FMEA and FTA, the cause of an FMEA item can be read as the event that leads to failure of a system item, so each analysis can verify the other. | 9.4, p. 44 |
| RAAML-GUID-004 | note | none | The fault tree package can be extended, for example for dynamic fault trees or component fault trees, while staying compatible with other modeled information. | 9.4, p. 44 |
| RAAML-GUID-005 | note | none | A recommendation connects a situation to an action item, normally a requirement that is managed further in requirements management (people responsible, due date, verification). | 9.2.2 (Recommendation), p. 37 |
| RAAML-GUID-006 | note | none | Tools are expected to offer traditional representations, tabular and tree views, over the model structure, because users of FMEA, STPA and ISO 26262 are used to tables and users of fault trees to a graphical tree. | 1.2, p. 4; 7.3, p. 12; Examples 1.2, 2.1 |
