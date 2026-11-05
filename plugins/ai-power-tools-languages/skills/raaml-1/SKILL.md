---
name: raaml-1
description: The OMG Risk Analysis and Assessment Modeling Language (RAAML) 1.0, a SysML-based language for recording safety and reliability analyses in a system model - situations and scenarios, failure modes and effects analysis (FMEA) with risk priority numbers, fault tree analysis (FTA) with events and AND, OR, NOT, XOR, SEQ, INHIBIT and MAJORITY_VOTE gates, STPA control structures and unsafe control actions, Goal Structuring Notation (GSN) assurance case arguments, and ISO 26262 hazard analysis and risk assessment (HARA, HAZOP, hazardous events, ASIL, safety goals). Use when someone is modeling hazards, risks, failure modes, causes, effects, fault trees, unsafe control actions, loss scenarios, safety cases, safety requirements or ASIL decomposition, or asks what RAAML, a situation, a controlling measure or a fault tree gate allows.
---

# Risk Analysis and Assessment Modeling Language (RAAML) 1.0

RAAML is the Object Management Group's extension of SysML for safety and reliability analysis. It is a model structure, not an analysis method: it gives you the elements and links to record an FMEA, a fault tree, an STPA, a GSN argument or an ISO 26262 hazard analysis in the same model as the system, and to trace between them. SysML is its foundation: a RAAML model is a SysML model, so the SysML concepts (blocks, parts, value properties, constraint blocks, requirements) are not re-described here; see the SysML language skill (`sysml-1`).

RAAML 1.0 is the version this skill describes. Newer versions exist (1.1, December 2025; 1.2 beta, September 2026) and are not covered.

## What you are creating

A RAAML model is a set of **situations**. A situation is a SysML block that describes a set of occurrences of some kind: a system in a place, at a time, in a state. Everything else is a kind of situation, a link between situations, or a measure aimed at one.

- You specialize **library classes** (such as an FMEA item, a basic event or an accident scenario) and give them parts and values. The language is "a library approach heavily with a light UML profile".
- **Steps** of a scenario are composite part properties typed by sub-situations. **Values** are value properties with a default value. When your class inherits from a library class, its properties **redefine or subset** the library's, and a redefining property's type must be narrower.
- Links between situations are **Causality** (and its kinds). Links to the rest of the system model are **RelevantTo** (context) and **Violates** (a requirement or constraint that is violated). Measures are **Detection**, **Prevention**, **Mitigation** and **Recommendation**; each has a situation as its supplier.
- A small set of **markers** identifies the kind of class (situation, failure mode, fault tree gate, goal ...). The same names are used for the library class and the marker, so "FailureMode" can mean either; the language file lists each name once.

The language has a Core, a General layer shared by all methods, and one package per method.

## Diagram types and what each admits

RAAML defines **no diagram type of its own** apart from the GSN icon notation. It reuses SysML diagrams and expects tables. Full lists are in `language.yaml` under `diagram_types`; the 16 package views of clause 10 are under `viewpoints`.

| Kind | Form | Use it for |
|---|---|---|
| Block definition (SysML) | diagram | Defining situations, scenarios and library specializations; FMEA items; operational conditions, accident scenarios and hazardous events; safety goal decomposition |
| Internal block (SysML) | diagram | Composing scenarios; chaining causes, failure modes and effects across system levels; the STPA control structure; mapping losses to hazards |
| Parametric (SysML) | diagram | The RPN formula and the gate probability formulas |
| Requirement (SysML) | diagram | Safety goals and their decomposition; requirements that an analysis produces |
| Fault tree | diagram | Events, gates, trees and transfer nodes. No frame is defined; event and gate markers carry icons |
| GSN argument | diagram | Goals, strategies, solutions, context, assumptions, justifications and the two GSN links |
| Control structure | diagram | Controllers, controlled processes, actuators, sensors, control actions and feedback |
| Situation, FMEA, unsafe control action, HAZOP tables | table | Rows are situations (indented = specializations); columns are attributes; a composite sub-situation is a column group. Described in clause 7.3.2 and the informative Examples |

## Concepts, grouped

The language has 153 concepts. The groups below follow the standard's packages. Spelling is the standard's (no spaces).

- **Core**: AnySituation (the universal root), Situation (marker), ControllingMeasure (abstract), RelevantTo, Violates, IDCarrier.
- **General**: AbstractEvent, AbstractCause / Cause, DysfunctionalEvent, UndesiredState, AbstractFailureMode / FailureMode, AbstractEffect / Effect, HarmPotential, Hazard, Scenario, AbstractRisk; markers Error, Fault, FailureState, Undeveloped; measures Detection, Prevention, Mitigation, Recommendation. The abstract classes carry untyped placeholder attributes (likelihood, occurrence, severity, detectability, score) that methods type; Cause, Effect and FailureMode type them as Real.
- **FMEA**: AbstractFMEAItem / FMEAItem (one failure mode, one or more causes, one or more final effects, an RPN), RPNCalculation, and seven failure mode classes (LossOfFunction, DegradationOfFunction, IntermittentFunction, PartialFunction, UnintendedFunction, ExceedingFunction, DelayedFunction).
- **FTA**: FTAElement, FTATree (one top event), Event and its kinds BasicEvent, IntermediateEvent, TopEvent, ConditionalEvent, DormantEvent, UndevelopedEvent, HouseEvent, ZeroEvent; Gate and its kinds AND, OR, NOT, XOR, SEQ, INHIBIT, MAJORITY_VOTE; seven reference constraint blocks; markers Tree, TransferIn, TransferOut.
- **STPA**: Controller, ControlledProcess, Actuator, Sensor, ControlAction, Feedback, ControlStructure; UnsafeControlAction with seven guidewords (Provided, NotProvided, STPAEarly, STPALate, OutOfSequence, TooLong, TooShort); LossScenario, ProcessModel with four deficiency kinds, Factor, Loss, RiskRealization.
- **GSN**: GSNNode, GSNArgumentNode, Goal, Strategy, Solution, ContextualInformation, Context, Assumption, Justification; InContextOf, SupportedBy.
- **ISO 26262**: OperationalCondition and its five kinds, AbstractOperationalSituation, TypicalAutomotiveSituation, five "Any" conditions; value types Exposure, Severity, Controllability, ASIL; AnyMalfunction and eight malfunction classes (Less, More, No, Intermittent, Unintended, ISO26262Early, ISO26262Late, Inverted); AutomotiveEffect (system, vehicle level), AccidentScenario, HazardousEvent; DependabilityRequirement, SafetyGoal and the functional, technical, software and hardware safety requirements; ASILDecompose, IndependenceRequirement, UserInfoRequirement, RecoveryRequirement, SafeState, OperatingMode; markers OperationalSituation, MalfunctioningBehavior, Verified, Confirmed, HazardAndRiskAssessment, LessonLearned, ASILAssignment, ASILOverrideRationale.

STPA and ISO 26262 each have an Early and a Late class; `language.yaml` keys them STPAEarly, STPALate, ISO26262Early and ISO26262Late, and the standard calls each one Early or Late.

## Relationships, in summary

There is **no allowed-pair matrix**. Endpoint rules are per relationship; all of them are in `language.yaml` (51 relationships) and `references/rules.md`.

- **Causality** joins any two situations; **Activation** (cause to dysfunctional event), **ErrorPropagation** and **ErrorRealization** (dysfunctional event to dysfunctional event) specialize it; so do ProcessModelFactor, ProcessModelConsequence and UnsafeControlActionHarmPotential in STPA.
- **RelevantTo** and **Violates**: the client must be a situation. **ControllingMeasure** and its four kinds: the supplier must be a situation.
- **GSN**: InContextOf runs from a goal or strategy to contextual information; SupportedBy runs from a goal or strategy (not undeveloped) to a goal, strategy or solution, and from a strategy only to a goal.
- **Part relationships** (composition): a scenario has steps; an FMEA item has failure mode, causes and final effects; a fault tree has a top event; a gate has inputs and one output; an unsafe control action has a context; a hazardous event has an accident scenario, hazards and effects; an accident scenario has operational situations and a malfunction. Multiplicities are in `language.yaml`.

## The rules that matter most

49 rules are errors (must), 19 are warnings (should), 28 are advice (note). The ones to check first:

- Every FMEA item has exactly one failure mode, at least one cause and at least one final effect, and no harm potential (CARD-001 to 004).
- A fault tree has exactly one top event; a gate has exactly one output event; an INHIBIT gate has a single input (CARD-005 to 007).
- A fault tree marker applies only to a class (or a property typed by one) that specializes the matching library element: events, gates, tree, undeveloped event, transfer-in (MARK-001 to 007).
- Probabilities are 0 to 1; a house event is 0 or 1; a zero event is always 0 (VAL-001 to 003).
- The client of RelevantTo and of Violates is a situation; the supplier of every controlling measure is a situation (REL-001 to 003).
- GSN links follow the permitted connections; a goal or strategy that supports others is developed (GSN-001 to 009).
- Each unsafe control action has exactly one context (CARD-011). A hazardous event has one accident scenario (CARD-012).
- Exposure, severity and controllability each have a rationale attached; an ASIL override has a rationale; ASIL decompositions come in pairs (ISO-001 to 005).
- A redefining property narrows the type of the property it redefines (SIT-004).
- The gate probability formulas, the RPN formula and the use of the situation root are reference or practice rules, graded as warnings.

## Example: a card payment authorization service

Westbrook Bank (fictitious) analyzes its card payment authorization service. Substitute your own system, names and numbers.

**FMEA.** The analysis is one FMEA item, "Authorization unavailable". Its **failure mode** specializes LossOfFunction: "Authorization service does not respond". Its **cause** specializes Cause: "Primary database fails" (occurrence 3). Its **final effect** specializes Effect: "Customer card payment is declined" (severity 7). Detectability of the failure mode is 4. The RPN calculation multiplies occurrence 3 x detectability 4 x severity 7 = 84. A RelevantTo link ties the item to the authorization service block in the system model; a Violates link ties the item to the stakeholder requirement "Cards are accepted 99.9% of the time"; a Prevention measure (a requirement to add a standby database) is linked with the failure situation as its supplier.

**Fault tree.** A tree specializes FTATree, with one top event "Customer cannot pay by card". An OR gate takes two inputs: an intermediate event "Authorization outage" and a basic event "Card network link down" (probability 0.01). The intermediate event is the output of an AND gate over "Primary database fails" (0.1) and "Standby failover fails" (0.2): 0.1 x 0.2 = 0.02. The OR gate gives 1 - (1 - 0.02)(1 - 0.01) = 0.0298 (assuming independence). Each event is typed by a library event class and carries the matching marker; the tree has one top event; the gates have one output each.

**GSN.** A goal "Card payments are acceptably available" is supported by a strategy "Argue over the fault tree and the FMEA", which is supported by two goals, each supported by a solution that points to the analysis. The top goal is in context of a context element "Service hours 24 x 7". Identifiers G1, G2 and so on are held in the identifier carrier, not in the names.

## Data types and attributes

The standard defines types only in part (coverage: partial). It adds four ISO 26262 value types: exposure (E0 to E4), severity (S0 to S3), controllability (C0 to C3) and ASIL (twenty literals: no assignment, QM, A to D and the decomposed forms such as B(D)), plus a restricted real for house event probability (0 or 1). Everything else is typed Real, Integer or String from SysML (`sysml-1`); probabilities are Reals from 0 to 1. The abstract classes leave some attributes untyped on purpose for methods to type. Attributes are listed on each concept under `attributes` for the 47 concepts that have them. See `data_types` in `language.yaml`.

## How it is drawn

The standard gives its own symbols only to fault tree events and gates and to goal structuring nodes (coverage: normative for those). Events: basic event a circle, conditional event an ellipse, dormant event a double-outline diamond, house event a house outline, zero event a house outline with a diagonal line; top and intermediate events have no icon. Gates: AND an arched gate with a flat base, OR a pointed curved gate, SEQ an AND gate with a triangle inside, XOR an OR gate with a second arch inside, INHIBIT a hexagon, MAJORITY_VOTE an arched gate with an m inside, NOT two triangles point to point; a transfer-in node is a triangle. Goal structuring: goal a rectangle, strategy a parallelogram, solution a circle, context a rounded rectangle, assumption and justification ellipses, undeveloped a small hollow diamond under the node. Every other concept is a SysML block box with its marker shown as a keyword in guillemets, and relationships are associations or dependencies drawn as in `sysml-1`. See `notation` in `language.yaml` for each symbol with its section.

Sizes and spacing come from `../_languages/layout-standard.yaml`; which element type each concept takes is in `layout` in `language.yaml`.

## Pointers

- `references/standard.md`: the standard in plain words, package by package.
- `references/rules.md`: every rule with its id, strength, whether a check can decide it, and its section.
- `language.yaml`: concepts with generalization, attributes and layer; relationships with roles and multiplicities; diagram and table kinds with what each admits; the 16 package views; constraints; conventions.
- The SysML language skill (`sysml-1`) for the SysML concepts RAAML reuses.
