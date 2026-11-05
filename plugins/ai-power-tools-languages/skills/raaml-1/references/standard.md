# RAAML 1.0 in plain words

This is a section-by-section account of the OMG Risk Analysis and Assessment Modeling Language (RAAML) 1.0 (formal/22-12-06, with its normative machine-readable models and the informative Examples), in our own words. Clause numbers and printed page numbers are the standard's. Short quoted phrases are under 15 words. The full list of concepts, relationships and rules is in `language.yaml` and `rules.md`; this file explains how they fit together.

## 1. Scope and purpose (clauses 1, 5, 6)

RAAML adds to SysML the means to record safety and reliability analyses inside a system model. SysML can hold requirements, structure and behavior, but not the constructs for failure, hazard, risk and assurance. A group of industry experts worked since 2016 to define them so that analyses can be shared between organizations and tools instead of being re-invented in each (1.2, p. 4).

It is a language for tool builders and senior safety specialists. It gives the model structure behind the "traditional representations" of the field: trees, tables, argument diagrams. It does not prescribe how to carry out an analysis (Examples 1.1, 2.3). The methods it covers are Failure Mode and Effects Analysis (FMEA), Fault Tree Analysis (FTA), Systems-Theoretic Process Analysis (STPA), the Goal Structuring Notation (GSN) and the hazard analysis and risk assessment of ISO 26262 road vehicle functional safety, including HAZOP.

It is two things at once: the normative **Libraries and Profiles** document, and an informative **Examples** document (a glucose meter, a wheel braking system, a steering assist function).

## 2. How the language is built (7.1, 7.2, 9)

RAAML is a UML profile and a set of model libraries. It imports the whole SysML profile, so a RAAML model is a SysML model (9, p. 19). Its authors chose "a library approach heavily with a light UML profile" (7.2, p. 11) for three reasons: ordinary structural modeling (blocks, parts, generalization) can carry the safety data with no special tooling; users can extend the libraries by specializing classes, because practice differs between aerospace, automotive, nuclear and other domains; and changing a library is easier than changing a profile.

In practice:

- The **library** supplies predefined classes with properties. A user's analysis element specializes a library class. Attributes are redefined or subset in the user's class.
- The **profile** supplies markers. A marker identifies a class (or property) as a situation, a failure mode, a fault tree gate, a goal, and so on, and carries an icon where one is defined. The marker for situations "is only needed to distinguish situations from other types of blocks" (9.1.2, p. 22).
- Most names appear twice, once as a library class and once as a marker (FailureMode, FMEAItem, UnsafeControlAction, LossScenario, the fault tree events and gates). `language.yaml` lists each name once and records the layer.
- The packages are Core and General (shared by all methods) and one package for each method: FMEA, FTA, STPA, GSN and ISO 26262. GSN has a profile only. Core, General, FMEA, FTA, STPA and ISO 26262 each have both.
- Every package's content is listed in `language.yaml` under `concepts.groups`.

## 3. Conformance (2)

There are two types. **Interchange conformance**: a tool can import and export conformant XMI for all valid RAAML models. **View specification conformance**: a tool implements the views the specification defines (clause 10, section 11 below). A vendor may implement one method alone (FMEA, FTA, STPA, GSN or ISO 26262) and claim conformance to it. These are obligations on tools, not properties of a model, and are recorded as notes.

## 4. Modeling principles for situations (7.3)

All safety and reliability data are captured as **situations** and **scenarios**, using ordinary structural modeling (7.3, pp. 11-16).

- A situation is a block. A scenario is built by inheriting from other scenarios and composing other situations as parts. Library scenarios are templates to inherit from, and multi-level composite situations can be built.
- Each **step** of a scenario is a part property (composite) typed by a sub-situation, usually with an association too.
- Each **attribute value** of a situation is a value property typed by a value type, with the value in its default value.
- When a user situation inherits from a library situation, its properties redefine or subset the library's. A redefining property's type must be narrower than the redefined one's. If several values are wanted for one library attribute, several properties subset it; names of subsetting properties are not regulated, though a naming scheme of parent name plus number is recommended.
- A user may add other properties; those are user extensions and not part of the language.
- A user situation can inherit from a library situation through intermediate situations, which expresses generality and specificity between real-world situations.

**Example from the standard**: the library describes a typical automotive situation by traffic and people, vehicle usage, road condition, location, environmental condition and an exposure level. A user's "Highway Driving Straight at Speed" sets exposure E4, traffic "free flow", usage "driving at speed" and two locations (city roads, highway) as two subsetting properties, and leaves road and environmental conditions unspecified. A more specific situation (the same in wet conditions) generalizes it and redefines exposure as E3.

**Tables**: because FMEA, STPA and ISO 26262 users are used to tables, the same model can be shown as a table with a name column and one column per attribute. Specializations are indented rows; a composite sub-situation becomes a group of columns, so one hazardous event table can include accident scenario and operational situation columns. Rows added in a table must create the same underlying model structures as a diagram would (7.3.2).

## 5. Core (9.1)

The domain model has one central idea, the **situation**: a system in a given place, time and state. A situation is a classifier that describes a set of occurrences (one named aircraft being refueled at one gate at one time is a single occurrence). Parameters may be left out when they do not matter ("Fire in the engine compartment of the ship").

- **AnySituation** is the universal root; all situations inherit from it. It carries two ends, `from` and `to`, of the Causality association.
- **Causality** links one situation to another: direct, conditional, probabilistic or user-defined cause and effect, with many causes for one situation and many effects of one cause. All other situation relationships inherit from it.
- **Situation** (profile) marks a SysML block as a situation.
- **RelevantTo** (profile dependency) links a situation, as client, to a system-model element that gives it context. **Violates** links a situation, as client, to a requirement, design constraint or other element that prescribes a characteristic of the system. **ControllingMeasure** (abstract) links a measure to the situation it addresses, which must be the supplier.
- **IDCarrier** carries a human-readable identifier (one `Id` string) on any element.

Generalization between situations means a subset of occurrences. Quantitative attributes are value properties; formulas that relate attributes are constraint blocks (Table 9.1). The table also names DependabilityAttribute and AttributeRelation, which are not defined as elements.

## 6. General (9.2)

The General package holds concepts used by several methods. It exists to avoid duplicating common concepts, to give traceability between artifacts across the life cycle (a failure mode from a hazard analysis can be considered in an FMEA and in an FTA), and to give a base for new methods or domains.

**Events** (all specialize AnySituation):

- **AbstractEvent**: anything that changes the system or its environment; has a starting point in time. Placeholder `likelihood`.
- **AbstractCause**: a precursor event that activates others. Placeholders `occurrence` and `premitigationOccurrences`. **Cause** types them as Real.
- **DysfunctionalEvent**: an event that can cause dysfunctional behavior; generalizes failure and feared event.
- **UndesiredState**: an unintended condition at a specific time. **AbstractFailureMode** (a way a system or part can fail; placeholders `detectability`, `premitigationDetectabilities`) specializes it; **FailureMode** types them as Real. A failure is an instance of a failure mode.
- **AbstractEffect**: a dysfunctional event that is a consequence of another situation; placeholders `severity`, `premitigationSeverities`. **Effect** types them as Real.
- **HarmPotential**: a state in which harm is possible (malicious or not). **Hazard** is a non-malicious potential source of harm, short-term (fire) or long-term (toxic release).

**Scenarios and risk**: a **Scenario** is a composite situation of steps with causal ordering. An **AbstractRisk** is a scenario made of a harm potential, a triggering event and resulting harm, with an untyped `score` such as an RPN.

**Causal relationships** (all specialize Causality): **Activation** (a fault cause activates an error), **ErrorPropagation** (an error leads to another error), **ErrorRealization** (an error becomes a failure).

**Profile elements**: **FailureMode**, **Error** (the gap between a computed value and the true one), **Fault** (an abnormal condition that can reduce or remove a unit's ability to function), **FailureState** (a state entered after a failure mode occurs, tied to failure modes by RelevantTo), and the four measures **Detection** (raise the probability of detection), **Prevention** (lower probability of occurrence), **Mitigation** (lower severity) and **Recommendation** (connect the situation to an action item, normally a requirement), each a kind of ControllingMeasure. **Undeveloped** marks an incomplete concept: a goal, a strategy, or a basic event.

## 7. FMEA (9.3)

FMEA inspects as many components, assemblies and subsystems as possible to find failure modes, causes and effects.

- **AbstractFMEAItem** is an AbstractRisk with exactly one `failureMode`, one or more `cause` and one or more `finalEffect`, an `RPN` (the score), and earlier `previousRPNValues`. The inherited `harmPotential` is redefined to none, because FMEA does not use it. **FMEAItem** is the Real-valued version with a link to **RPNCalculation**, a constraint block that multiplies occurrence, detectability and severity.
- Seven failure-mode classes describe how a function fails: **LossOfFunction**, **DegradationOfFunction**, **IntermittentFunction**, **PartialFunction**, **UnintendedFunction**, **ExceedingFunction**, **DelayedFunction**.
- The **FMEAItem** marker may be applied only to a class that specializes AbstractFMEAItem.
- The Examples recommend a "simulation context" that composes the systems under analysis and the FMEA item, so causes, failure modes and effects chain across levels (an effect of a low-level item becomes a cause higher up). A table view has rows per FMEA item and columns for item, failure mode, cause, local effect, final effect, SEV, DET, OCC and RPN.

## 8. Fault Tree Analysis (9.4)

FTA is a top-down analysis in which an undesired state is analyzed with Boolean logic over lower-level events. The package follows IEC 61025 and can be extended (for example to dynamic or component fault trees). A cause of an FMEA item can be read as the event that leads to failure of an item, which links the two analyses.

- **FTAElement** is any event or gate; it has a `probability` from 0 to 1. **FTATree** is a collection of elements with exactly one `topEvent`.
- **Events**: **BasicEvent** (initiating failure, no further development), **IntermediateEvent** (derived by gates), **TopEvent** (the undesired event at the top), **ConditionalEvent** (a condition attached to a gate, mainly priority-AND and INHIBIT), **DormantEvent** (a latent failure found by periodic tests), **UndevelopedEvent** (not developed further for lack of consequence or information; carries both the basic-event and undeveloped markers), **HouseEvent** (switchable, probability 0 or 1), **ZeroEvent** (never occurs, probability 0). Events have an optional `priority`, used only to order inputs of a SEQ gate.
- **Gates** combine input events into one output event: **AND** (all inputs), **OR** (at least one), **NOT** (the input does not occur), **XOR** (exactly one), **SEQ** (all in a given sequence, priority-AND), **INHIBIT** (the single input occurs while an enabling condition holds), **MAJORITY_VOTE** (at least m of the inputs; m is a parameter, not necessarily half). A gate has zero or more inputs and one output.
- **Constraint blocks** give a reference probability formula for each gate (product for AND, SEQ and INHIBIT; complement of "none" for OR; a + b - 2ab for two XOR inputs; unity minus input for NOT; combinations for MAJORITY_VOTE). All assume independent inputs. They are reference implementations, not the only way to compute.
- **Markers** (profile): Tree, the seven event markers, the seven gate markers, **TransferIn** and **TransferOut**. Each event or gate marker applies only to a class that specializes the library element of the same name, or to a property typed by one. **TransferOut** marks a partial tree used inside another through **TransferIn**; its computed top probability becomes the probability of the TransferIn node. Fault trees can be partitioned and referenced this way.

## 9. STPA (9.5)

STPA is a hazard analysis based on control and systems theory rather than reliability theory (Leveson and Thomas, STPA Handbook).

- **Control structure** (profile): **Controller** sends **ControlAction**s and receives **Feedback**; **Actuator** passes control actions to the **ControlledProcess**; **Sensor** gives feedback from it. **ControlStructure** is a block composed of these, describing feedback control loops. The control structure can be a stand-alone diagram or built into the system model.
- **UnsafeControlAction** (UCA): in what context providing or not providing a control action may lead to an undesired result. Four parts: the controller (inferred from the model), the guideword (given by generalization), the control action (linked by RelevantTo) and the context (a sub-situation). Seven guideword classes specialize it: **Provided**, **NotProvided**, **Early**, **Late**, **OutOfSequence**, **TooLong**, **TooShort**. Each UCA has exactly one **Context**, an operational situation.
- **LossScenario**: a sequence from **Factor**s, through **ProcessModel** deficiencies, to a UCA. The four kinds of process model deficiency are **InadequateControllerDecisions**, **InadequateControlExecution**, **InadequateProcessBehavior** and **InadequateFeedbackAndInputs**.
- **Loss**: an unacceptable effect (loss of life, property damage, mission, finance, image, environment). **RiskRealization** is an association between a loss and a hazard.
- Causal links: **ProcessModelFactor** (factor to process model), **ProcessModelConsequence** (process model to UCA), **UnsafeControlActionHarmPotential** (UCA to harm potential).
- The Examples show UCAs as a table (rows are control actions, columns guidewords) or as diagrams, and a hierarchy of losses and hazards mapped by connectors.

## 10. GSN (9.6)

The profile implements the core notation of the Goal Structuring Notation version 2, which GSN's authors (the SCSC) made available under a Creative Commons license (9.6, p. 81). It covers the core notation only, with no library. GSN is an extension of the OMG Structured Assurance Case Metamodel (SACM); RAAML uses a UML profile reading so it integrates with SysML.

- **Nodes**: **Goal** (a claim), **Strategy** (the nature of the inference between a goal and its supporting goals), **Solution** (a reference to evidence). Goal and Strategy are the **argument nodes**.
- **Contextual information**: **Context**, **Assumption** (intentionally unsubstantiated) and **Justification** (rationale).
- **InContextOf** declares a contextual relationship; **SupportedBy** an inferential or evidential one. Permitted InContextOf: goal or strategy to context, assumption or justification. Permitted SupportedBy: goal to goal, strategy or solution; strategy to goal. A goal or strategy that supports others is not undeveloped.
- The short phrase of a node is the element name; the identifier ("G1") is a separate string, held in the identifier carrier.
- **Notation**: a node is drawn as the standard class-style box with the icon at the upper left or as an image with the name below; the preferred form uses the icon as the outline of the box. A goal or strategy that is also undeveloped is drawn with a combined notation.

## 11. ISO 26262 (9.7)

The package supports the analysis and requirement specification parts of the automotive functional safety standard, a risk-based standard derived from IEC 61508. It builds on Core and General, so the same elements can be reused in an FMEA.

- **HAZOP** is modeled by specializing failure mode as **MalfunctioningBehavior**, related to system behaviors through guidewords. Eight malfunction classes specialize **AnyMalfunction**: **Less**, **More**, **No**, **Intermittent**, **Unintended**, **Early**, **Late**, **Inverted**. Each must be connected to a behavioral element (a use case or a function).
- **Operational situations**: **OperationalCondition** parts (**TrafficAndPeople**, **VehicleUsage**, **RoadCondition**, **Location**, **EnvironmentalCondition**) compose **AbstractOperationalSituation** (with `Exposure`) and **TypicalAutomotiveSituation**. Five "Any" classes give the widest condition of each kind.
- **Value types**: **Exposure** (E0 to E4), **Severity** (S0 to S3), **Controllability** (C0 to C3), **ASIL** (QM, A to D, and decomposed forms). Exposure, severity and controllability each must have a rationale attached.
- **AccidentScenario**: operational situation(s) plus one malfunctioning behavior, with a controllability value. **HazardousEvent**: an accident scenario plus hazards, system-level and vehicle-level effects, and the ASIL as its score. **AutomotiveEffect** (system level, vehicle level) has a severity.
- **Safety requirements** (profile): **DependabilityRequirement** (abstract) and its kinds **SafetyGoal**, **FunctionalSafetyRequirement**, **TechnicalSafetyRequirement**, **SoftwareSafetyRequirement**, **HardwareSafetyRequirement**; relations **ASILDecompose** (applied in pairs; supplier at a higher abstraction), **IndependenceRequirement** (independence criterion for a valid decomposition), **UserInfoRequirement** and **RecoveryRequirement** (link a safe state to a requirement), **SafeState** and **OperatingMode**. A template, **ISO26262SafetyRequirementTemplate**, holds an ASIL and a fault tolerant time interval.
- **Other markers**: **OperationalSituation**, **MalfunctioningBehavior**, **Verified** and **Confirmed** (a hazardous event has been verified or confirmed; each holds a result), **HazardAndRiskAssessment** (a package that holds hazardous events), **LessonLearned**, **ASILAssignment** (an ASIL for a design element, with an optional override that needs an **ASILOverrideRationale**).
- Flow in the Examples: malfunctioning behavior, hazard and operational situation give an accident scenario; the hazardous event gives the risk level; safety goals derive from hazardous events, functional safety requirements from safety goals, technical from functional, hardware and software from technical.

## 12. Views (10)

Clause 10 lists 16 views, one per package, each a figure showing a set of elements of the specification's own model: Core Library, Core Profile, General Concepts Library and Profile, FMEA Library and Profile, FTA Events, Library and Profile, STPA Library and Profile, GSN Profile, ISO 26262 Library, All-Encompassing Operational Situations, RequirementManagement and the ISO 26262 Profile. The element lists are in `language.yaml` under `viewpoints`. Interchange and view conformance (section 3) refer to them. The text does not say whether a tool must show these exact figures to users.

## 13. Diagrams and tables

RAAML defines no diagram type of its own. It reuses SysML's block definition, internal block, parametric and requirement diagrams, and the informative Examples add fault tree diagrams, GSN argument diagrams, control structure diagrams and a family of tables. See `language.yaml` under `diagram_types`.

## 14. What RAAML reuses from SysML

See the SysML language skill (`sysml-1`) for the definitions of: Block (the base of every situation, FMEA item and control structure), ConstraintBlock and constraint properties (RPN and gate formulas), ValueType and value properties (attributes and values), part properties and generalization (scenario steps), Requirement and AbstractRequirement (safety requirements), DeriveReqt and Satisfy (ASIL decomposition and the state links), Rationale (override and value rationales), DirectedRelationshipPropertyPath (the target context and target property path of RelevantTo and ControllingMeasure), and the four diagrams named above. RAAML 1.0 cites SysML 1.6; that skill describes 1.5.

## 15. Newer versions

RAAML 1.1 (December 2025) and 1.2 beta (September 2026) exist. They are not described here; the language file lists their dates and addresses.
