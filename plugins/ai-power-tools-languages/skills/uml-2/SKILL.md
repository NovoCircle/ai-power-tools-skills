---
name: uml-2
description: The OMG Unified Modeling Language (UML) 2.5.1, the general-purpose modeling language for software and systems - its 14 diagram types (class, object, package, composite structure, component, deployment, profile, use case, activity, state machine, sequence, communication, timing, interaction overview), the metaclasses on them (Class, Interface, Association, Component, UseCase, Actor, Activity, Action, StateMachine, State, Transition, Lifeline, Message, Node, Artifact, Package, Profile, Stereotype), and the relationship kinds (association, aggregation, composition, generalization, dependency, realization, usage, include, extend, deployment). Use when someone is drawing or checking UML, asks what a UML diagram admits, which relationship connects two kinds of element, what a UML constraint or well-formedness rule requires, how a UML concept is named in the standard, or when another modeling language (such as a profile or extension of UML) needs the UML concept it reuses.
---

# Unified Modeling Language (UML) 2.5.1

UML is the Object Management Group's language for visualizing, specifying, constructing and documenting systems. It is defined by a metamodel (242 classes in 14 packages), a notation drawn in diagrams, semantics, and interchange formats. A diagram is a view of part of a model; the same element can appear on several diagrams. This skill describes the standard only. Concept names are exactly the standard's (no spaces) so that languages built on UML, such as profiles for systems engineering or service architecture, can point here.

## What you are creating

A **model**: a tree of packages owning elements (classifiers, behaviors, relationships), plus **diagrams** that show parts of it. You decide the question first, then the diagram:

| Question | Diagram type |
|---|---|
| What things exist and how are they related? | Class (types) or Object (instances at one moment) |
| How is a big model organized? | Package |
| How is one thing built from collaborating parts? | Composite structure |
| What deployable parts exist and what do they offer and need? | Component |
| What runs where? | Deployment |
| How is the language itself extended for a domain? | Profile |
| What do users get from the system? | Use case |
| What is the flow of work, data and control? | Activity |
| What states does one thing go through, and what triggers each change? | State machine |
| Who sends what to whom, in what order? | Sequence |
| Which participants talk to which, and in what numbered order? | Communication |
| How do conditions change over time? | Timing |
| How do several interactions fit together? | Interaction overview |

## The 14 diagram types and what each admits

Annex A of the standard names the clause that defines each diagram's constructs and says the boundaries are not strictly enforced: diagram kinds can be mixed. The lists below are this skill's reading of the notation (guidance, not rules). Frame heading kinds: activity, class, component, deployment, interaction (sd), package, state machine, use case; object, composite structure and profile diagrams have no heading kind of their own.

**Structure diagrams**

- **Class diagram** (clause 11, with 9, 10, 12): Class, AssociationClass, Interface, DataType, PrimitiveType, Enumeration, Signal, Reception, Component; Property, Operation, Parameter; Association (with aggregation, composition, qualifiers), Generalization and GeneralizationSet, Dependency and its kinds, InterfaceRealization; Package and imports; templates and bindings; Constraint, Comment. Not lifelines, messages, transitions.
- **Object diagram** (clause 9.8): InstanceSpecification, Slot, InstanceValue, links (instance specifications classified by an association).
- **Package diagram** (clause 12): Package, Model, Profile, imports (PackageImport, ElementImport), PackageMerge, Dependency, and the packaged elements shown inside.
- **Composite structure diagram** (clause 11.2, 11.3, 11.7): the internal structure of a StructuredClassifier: parts and roles (Property), Port, Connector with ends, Collaboration and CollaborationUse, interfaces as ball and socket.
- **Component diagram** (clause 11.6): Component with provided and required Interface, Port, assembly and delegation Connector, ComponentRealization.
- **Deployment diagram** (clause 19): Node, Device, ExecutionEnvironment, Artifact, DeploymentSpecification, Deployment, Manifestation, CommunicationPath, instances of nodes and artifacts.
- **Profile diagram** (clause 12.3): Profile, Stereotype, Extension (with ExtensionEnd), ProfileApplication, metaclass and metamodel references, profile-defined classes and data types, Image.

**Behavior diagrams**

- **Use case diagram** (clause 18): UseCase, Actor, the subject, Association between actor and use case, Include, Extend, ExtensionPoint, Generalization.
- **Activity diagram** (clause 15, actions in 16): Activity, Action and its kinds, control nodes (initial, activity final, flow final, decision, merge, fork, join), object nodes and pins, ControlFlow and ObjectFlow, partitions, interruptible regions, structured nodes (conditional, loop, sequence, expansion region), exception handlers, variables.
- **State machine diagram** (clause 14): StateMachine (also ProtocolStateMachine), Region, State, FinalState, Pseudostate, ConnectionPointReference, Transition (ProtocolTransition), Trigger, entry/exit/do/effect behaviors, guards.
- **Sequence diagram** (clause 17): Interaction, Lifeline, Message (synchronous, asynchronous, reply, create, delete, lost, found), ExecutionSpecification, CombinedFragment and InteractionOperand, InteractionUse, Gate, StateInvariant, Continuation, GeneralOrdering, DestructionOccurrenceSpecification, time and duration constraints and observations.
- **Communication diagram** (clause 17.9): lifelines joined by links, messages numbered by sequence expressions; equivalent to a simple sequence diagram without fragments or uses.
- **Timing diagram** (clause 17.11): lifelines as state or value timelines on a linear time axis, messages, time constraints.
- **Interaction overview diagram** (clause 17.10): an activity-diagram variant whose nodes are inline interactions or interaction uses; alt is a decision and merge, par a fork and join, loop a cycle; branching must be properly nested.

## The concepts, grouped

Every concept below is a metaclass of the standard (full definitions, generalizations and sections in `language.yaml` and `references/standard.md`). Everything is an **Element**; a **NamedElement** has a name, qualified name and visibility; a **Relationship** relates elements; a **PackageableElement** can be owned by a Package.

- **Common structure (7):** Element, Comment, Relationship, DirectedRelationship, NamedElement, Namespace, PackageableElement, Type, TypedElement, MultiplicityElement, Constraint, Dependency (Abstraction, Realization, Usage), ElementImport, PackageImport, templates (TemplateSignature, TemplateParameter, TemplateBinding, TemplateParameterSubstitution), visibility kinds (public, private, protected, package).
- **Values (8):** ValueSpecification, literals (Boolean, Integer, Real, String, UnlimitedNatural, Null), OpaqueExpression, Expression, StringExpression, time and duration (TimeExpression, Duration, Interval variants, TimeConstraint, DurationConstraint, TimeObservation, DurationObservation).
- **Classification (9):** Classifier, Feature (StructuralFeature, BehavioralFeature), Property, Operation, Parameter, ParameterSet, Generalization, GeneralizationSet, Substitution, InstanceSpecification, Slot, InstanceValue, RedefinableElement, template parameters for classifiers and operations.
- **Simple classifiers (10):** DataType, PrimitiveType, Enumeration, EnumerationLiteral, Signal, Reception, Interface, InterfaceRealization, BehavioredClassifier.
- **Structured classifiers (11):** StructuredClassifier, EncapsulatedClassifier, Class, Association, AssociationClass, Component, ComponentRealization, Collaboration, CollaborationUse, ConnectableElement, Connector, ConnectorEnd, Port.
- **Packages and profiles (12):** Package, PackageMerge, Model, Profile, ProfileApplication, Stereotype, Extension, ExtensionEnd, Image.
- **Common behavior (13):** Behavior, OpaqueBehavior, FunctionBehavior, Event (CallEvent, SignalEvent, ChangeEvent, TimeEvent, AnyReceiveEvent), Trigger.
- **State machines (14):** StateMachine, ProtocolStateMachine, Region, Vertex, State, FinalState, Pseudostate (kinds initial, deepHistory, shallowHistory, join, fork, junction, choice, entryPoint, exitPoint, terminate), ConnectionPointReference, Transition (kinds internal, local, external), ProtocolTransition, ProtocolConformance.
- **Activities (15):** Activity, ActivityNode, ActivityEdge (ControlFlow, ObjectFlow), ControlNode kinds, ObjectNode kinds (ActivityParameterNode, CentralBufferNode, DataStoreNode), ExecutableNode, ActivityGroup (ActivityPartition, InterruptibleActivityRegion), ExceptionHandler, Variable.
- **Actions (16):** Action and its many kinds (invocation, object, structural feature, variable, link, event acceptance, structured and expansion nodes), Pin (InputPin, OutputPin, ValuePin, ActionInputPin).
- **Interactions (17):** Interaction, InteractionFragment, Lifeline, Message, MessageEnd, Gate, OccurrenceSpecification, ExecutionSpecification, CombinedFragment and operators (seq, alt, opt, break, par, strict, loop, critical, neg, assert, ignore, consider), InteractionOperand, InteractionConstraint, InteractionUse, PartDecomposition, StateInvariant, Continuation, GeneralOrdering.
- **Use cases (18):** UseCase, Actor, Include, Extend, ExtensionPoint.
- **Deployments (19):** Node, Device, ExecutionEnvironment, Artifact, DeploymentSpecification, Deployment, Manifestation, CommunicationPath, DeploymentTarget, DeployedArtifact.
- **Information flows (20):** InformationFlow, InformationItem.

## Relationship rules in summary

A relationship is a metaclass whose ends have types; the types decide what may be related (`language.yaml`, `relationships`).

| Kind | From | To | Remember |
|---|---|---|---|
| Association | two or more typed ends | | Binary unless drawn as a diamond. Only a binary association can have an aggregation end. Ends owned by a class are navigable. |
| Aggregation / composition | whole end | part end | Diamond (hollow shared, filled composite) at the whole. The composing end has an upper bound of at most 1. |
| Generalization | specific Classifier | general Classifier | Hollow triangle at the general one. Acyclic; parents not final. |
| Dependency | client NamedElement | supplier NamedElement | Dashed arrow from client. Kinds: Abstraction (derive, refine, trace), Realization, Substitution, Usage (use, call, create, instantiate, send, responsibility). |
| InterfaceRealization | BehavioredClassifier | Interface | Ball; Usage of an interface is the socket. |
| ComponentRealization | Component | Classifier | A component's realizing classifiers. |
| Include | including UseCase | included UseCase | A use case cannot include one that includes it. |
| Extend | extending UseCase | extended UseCase | Extension points belong to the extended use case. |
| Deployment | DeploymentTarget | DeployedArtifact | Artifacts deploy to nodes; Manifestation links an artifact to what it implements. |
| ElementImport / PackageImport / PackageMerge | importing or receiving namespace | imported or merged element or package | Imports are public or private; merges must not cycle. |
| ProfileApplication / Extension | package / stereotype | profile / metaclass | Stereotypes extend a metaclass; they never generalize one. |
| Transition | source Vertex | target Vertex | Kinds internal, local, external. |
| ActivityEdge | source ActivityNode | target ActivityNode | Control flow carries control; object flow carries objects; no object flow at an executable node. |
| Message | send MessageEnd | receive MessageEnd | Both ends are in the same fragment. |
| InformationFlow | source NamedElement | target NamedElement | Realized by relationships, connectors, edges or messages. |

## The rules that matter most

`references/rules.md` lists all 580 (449 formal constraints and 131 prose rules) with ids. Errors are `must`; `should` rules are warnings. The ones people break most:

**Names and namespaces.** All members of a namespace are distinguishable by name (UML-COM-017). An Actor, UseCase and ExtensionPoint must be named (UML-UC-002, UML-UC-008, UML-UC-004). A namespace cannot import itself (UML-COM-018). Elements do not own themselves (UML-COM-005).

**Generalization and features.** Generalization hierarchies are acyclic (UML-CLS-005); a final specialization cannot be a parent (UML-CLS-004). A redefined property is inherited from a more general classifier (UML-CLS-033). An operation has at most one return parameter (UML-CLS-018). Multiplicity: the upper bound is not below the lower (UML-COM-008).

**Associations.** Only binary associations are aggregations (UML-STR-003); ends of an association with more than two ends are owned by it (UML-STR-004); every end has a type (UML-STR-005); an association class is not defined between itself and something else (UML-STR-006); the composing end of a composition has an upper bound of at most 1 (UML-CLS-032). An actor associates only with use cases, components and classes, in binary associations (UML-UC-001); use cases are in binary associations only (UML-UC-005).

**Interfaces, signals, ports, components.** All features of an interface are public (UML-SIM-003). A reception has its signal's name and structure (UML-SIM-004, UML-SIM-005). Only an active class owns receptions or has a classifier behavior (UML-STR-008). A port is composite and owned by an encapsulated classifier (UML-STR-020, UML-STR-022). Connector ends are attached to roles of the owning classifier or their ports (UML-STR-015). A component nests no classifiers (UML-STR-012).

**Use cases.** No use case includes one that includes it (UML-UC-007); two use cases of the same subject are not associated (UML-UC-006); extension points belong to the extended use case (UML-UC-003).

**State machines.** A region has at most one initial pseudostate, which has at most one outgoing transition with no trigger or guard (UML-SM-028, UML-SM-022, UML-SM-018). A final state has no outgoing transitions, regions, or behaviors (UML-SM-004, UML-SM-005). A join has two or more incoming and one outgoing transition, a fork one incoming and two or more outgoing (UML-SM-019, UML-SM-023). A state has a submachine or regions, not both (UML-SM-033). An internal transition has a state as source and target (UML-SM-040). Transitions do not cross from one region to another of the same composite state (UML-SEM-019). A region is owned by a state machine or a state, not both (UML-SM-027).

**Activities.** An initial node has no incoming edges and only control flows leave it (UML-ACT-033, UML-ACT-034); a final node has no outgoing edges (UML-ACT-030); a fork has one incoming edge, a join one outgoing edge, a merge one outgoing edge, a decision one or two incoming and at least one outgoing (UML-ACT-032, UML-ACT-036, UML-ACT-038, UML-ACT-020). A control flow has no object node at either end unless the node is of control type; an object flow has no executable node at either end (UML-ACT-015, UML-ACT-041). A guard `else` is used on at most one decision edge (UML-SEM-031). Edges owned by an activity connect nodes of that activity (UML-ACT-003).

**Interactions.** Both ends of a message lie in the same fragment (UML-INT-041); a message's signature is an operation or a signal and the names match (UML-INT-044); opt, loop, break, neg and assert fragments have exactly one operand (UML-INT-004); an execution specification starts and finishes on one lifeline (UML-INT-011); nothing follows a destruction on a lifeline (UML-INT-010); a lifeline has a selector exactly when the part it represents is multivalued (UML-INT-035).

**Deployment.** A node's internal structure consists of nodes only (UML-DEP-004); a deployment specification belongs to an execution environment (UML-DEP-002); communication paths connect deployment targets (UML-DEP-001).

**Packages, merge and profiles.** A package never merges itself, directly or indirectly, or a package that contains or is contained in it (UML-MRG-001, UML-MRG-002, UML-MRG-003). A stereotype generalizes or specializes only another stereotype and takes part only in binary associations (UML-PKG-009, UML-PKG-008); it extends a metaclass through an Extension, which is binary (UML-PKG-002); a stereotype is not applied twice to one element (UML-PRF-011); a required extension means every instance of the extended metaclass carries the stereotype (UML-PRF-012).

Rules about running models (reentrancy, token counts, guard truth at run time) are marked `runtime`; they cannot be checked on a saved model.

## Data types and attributes

Coverage: full. The standard defines five primitive types in clause 21 (Boolean, Integer, Real, String, UnlimitedNatural) and writes their literals in 8.2.4. A model can add its own with DataType, PrimitiveType and Enumeration. The standard defines no units. The metamodel's 13 enumerations (VisibilityKind, AggregationKind, PseudostateKind, MessageSort and others) are listed with their values. Each concept entry in `language.yaml` lists its own attributes under `attributes`, with name, type, multiplicity and, where the standard gives them, default, derived, ordered and unique. A property that is an association end is in `relationships.metamodel_associations`, not on the concept. All of it is under `data_types` and `concepts.elements`.

## How it is drawn

Coverage: normative. UML gives a graphical notation, in text and figures, for most concepts, and states no sizes or colors. A classifier is a rectangle with a keyword in guillemets above its name. Generalization ends in a hollow triangle at the general classifier, a dependency is a dashed line with an open arrowhead, a realization is a dashed line with a hollow triangle, and aggregation and composition are a hollow and a filled diamond at the whole. States are rounded rectangles, actions are rounded rectangles with pentagon shapes for sending and accepting, a lifeline is a head with a dashed vertical line (a plain box in a communication diagram, a stepped state timeline in a timing diagram), and a node is a cube in perspective. Every concept and relationship kind has one entry under `notation` in `language.yaml`. Forty-six concepts (34 of them abstract) and one relationship kind, protocol conformance, have no drawing of their own and are listed under `notation.not_specified`. A language built on UML can name `inherits_from: uml-2` and draw the same way.

Sizes and spacing come from `../_languages/layout-standard.yaml`; the mapping of each concept to a size class is the `layout` block in `language.yaml`.

## A short example (illustration only)

Westbrook Bank, a fictitious bank, models retail accounts. The values are an illustration; substitute your own model.

- **Class diagram.** Class `Customer` and abstract class `Account` joined by a binary association: `Customer` end `owner` with multiplicity `1`, `Account` end `accounts` with multiplicity `1..*`, so a customer has at least one account. `SavingsAccount` and `CheckingAccount` each have a Generalization to `Account` (hollow triangle at `Account`); `Account` is abstract (name in italics). `Branch` owns `Account` by composition: filled diamond at `Branch`, with multiplicity `1` on the `Branch` end (at most 1 is required for the composing end). An Interface `FundsTransfer` is realized by `CheckingAccount` (ball).
- **Use case diagram.** Actor `Teller` and use cases `Open Account` and `Close Account` inside a subject rectangle `Retail Banking`; `Open Account` includes `Verify Identity` (`include` arrow from `Open Account`); `Waive Fee` extends `Close Account` at an extension point `fee assessed`.
- **State machine diagram** for `Account`: initial pseudostate to state `Open`; `Open` to `Frozen` on trigger `freeze` with guard `[review pending]`; `Frozen` to `Open` on `release`; `Open` to final state on `close`. The initial pseudostate has one outgoing transition and no trigger or guard.
- **Sequence diagram** `Transfer`: lifelines `:Teller`, `:CheckingAccount`, `:Ledger`; a synchronous message `debit(amount)` and its reply; a combined fragment `alt` with operands `[sufficient funds]` and `[else]`.
- **Deployment diagram:** a Node `<<device>> Branch Server` with an ExecutionEnvironment `Application Server` on which Artifact `accounts.war` is deployed; a CommunicationPath to a Node `Data Center`.

## References

- `references/standard.md` - the standard in our own words, by clause, with the notation notes, relationship kinds, keywords and the Standard Profile.
- `references/rules.md` - the 580 rules with ids, strength, section and what each applies to.
- `language.yaml` - the facts as data: 242 concepts with generalizations, 13 enumerations, 35 relationship kinds, 369 metamodel associations, 14 diagram types, keywords, Standard Profile, constraints, conventions.
- Not covered in depth: the execution semantics of Actions and the detailed semantics of clauses 9 to 11, which were read only through their constraints and notation.
