# UML 2.5.1 in our own words

The Object Management Group's Unified Modeling Language, version 2.5.1 (formal/17-12-05, December 2017), summarized section by section. Section numbers are the specification's. Short quotations are under 15 words. The normative machine-readable model (`UML.xmi`, ptc/18-01-01) is the source for the metamodel facts (classes, generalizations, multiplicities, constraint names); the document is the source for notation and prose. Where the two disagree, the standard says the machine-readable files win (clause 2).

How to use this file: `language.yaml` holds the machine-readable facts (concepts, relationship kinds, metamodel associations, diagram types, constraints). `rules.md` lists every constraint with its id. This file explains them. A rule id such as `UML-SM-012` is defined in `rules.md`.

## 1. What UML is (clauses 1 to 6)

UML is a graphical language for visualizing, specifying, constructing and documenting systems. It is defined by an abstract syntax (a metamodel of 242 classes and 13 enumerations, in 14 packages), a concrete syntax (notation, drawn in diagrams), semantics, and two interchange mechanisms (XMI for models, UML DI for diagrams). A model is the set of elements; a diagram is a view of part of it.

**Conformance (clause 2).** Five independent types: abstract syntax (create, read, update and delete instances of concrete metaclasses, and validate well-formedness against the metamodel constraints); concrete syntax (do the same for notation); model interchange (import and export conformant XMI for all valid models, including profiles; a UML 2.5 tool also reads and writes UML 2.4.1 XMI); diagram interchange (UML DI, Annex B); semantic conformance (a demonstrable way to interpret UML semantics; the normative semantics are clause 6.3 and the Semantics subclauses of clauses 7 to 22). Items the standard calls undefined or not specified are open to customization that does not contradict it.

**Key words (5.1).** The specification uses shall, should and may in the usual requirement sense. Rule strength in this skill follows that: formal constraints are errors; "should" statements are warnings.

**The 14 packages and their clauses.**

| Clause | Package | What it defines |
|---|---|---|
| 7 | Common Structure | Element, relationships, templates, namespaces, imports, types, multiplicity, constraints, dependencies |
| 8 | Values | Literals, expressions, opaque expressions, time and duration, intervals |
| 9 | Classification | Classifiers, generalization, features, properties, operations, parameters, generalization sets, instance specifications |
| 10 | Simple Classifiers | Data types, enumerations, signals, interfaces, behaviored classifiers |
| 11 | Structured Classifiers | Structured classifiers, ports, classes, associations, components, collaborations |
| 12 | Packages | Packages, package merge, models, profiles, stereotypes, extensions |
| 13 | Common Behavior | Behaviors, events, triggers |
| 14 | StateMachines | Behavior state machines, redefinition, protocol state machines |
| 15 | Activities | Activities, control nodes, object nodes, executable nodes, groups |
| 16 | Actions | Actions of all kinds, pins, structured and expansion regions |
| 17 | Interactions | Lifelines, messages, occurrences, fragments, interaction uses, and four diagram forms |
| 18 | UseCases | Use cases, actors, include, extend |
| 19 | Deployments | Deployment, artifacts, nodes |
| 20 | InformationFlows | Information flows and items |
| 21, 22 | Primitive Types, Standard Profile | Integer, Boolean, String, Real, UnlimitedNatural; 33 standard stereotypes |

## 2. Diagrams (Annex A and B)

A diagram has a contents area and, optionally, a frame with a heading `[kind] name [parameters]` at the upper left. Heading kinds: activity (act), class, component (cmp), deployment (dep), interaction (sd), package (pkg), state machine (stm), use case (uc). The primary symbols in the contents area decide the diagram's type. Two groups: **structure diagrams** (class, object, package, composite structure, component, deployment, profile) and **behavior diagrams** (use case, activity, state machine, sequence, communication, timing, interaction overview). The taxonomy is logical, not strict: kinds can be mixed (for example a state machine nested in an internal structure). Annex B (diagram interchange) gives each diagram a model element: none for structure diagrams except composite structure (a structured classifier or an instance of one), none for use case diagrams, exactly one StateMachine, Activity or Interaction for the others; interaction diagrams carry a kind (sequence, communication, overview, timing, table).

| Diagram type | Group | Frame | Defined by | Admits (the skill's reading of the notation) |
|---|---|---|---|---|
| Class diagram | structure | class | Annex A names clause 11 (Structured Classifiers); notation also in 9, 10, 12, 7.7 | Class, AssociationClass, Interface, DataType, PrimitiveType, Enumeration, EnumerationLiteral, Signal, Reception, Component, Property, Operation, Parameter, Association, Generalization, GeneralizationSet, Dependency, Abstraction, Realization, Substitution, Usage, InterfaceRealization, TemplateBinding, TemplateSignature, TemplateParameter, Package, PackageImport, ElementImport, PackageMerge, InstanceSpecification, Constraint, Comment, Stereotype application |
| Object diagram | structure | (no frame kind of its own; a class diagram frame is used) | Annex A names clause 9 (Classification), 9.8 | InstanceSpecification, Slot, InstanceValue, ValueSpecification, links (InstanceSpecification classified by an Association), EnumerationLiteral, Constraint, Comment, Package |
| Package diagram | structure | package | Annex A names clause 12 (Packages); notation 12.2.4, 7.4.4 | Package, Model, Profile, PackageableElement (members shown inside or by circle-plus), PackageImport, ElementImport, PackageMerge, Dependency, Constraint, Comment |
| Composite structure diagram | structure | (none of the eight frame kinds; Annex B gives it exactly one model element, a structured classifier or its instance) | Annex A names clause 11 (Structured Classifiers), 11.2 to 11.3, 11.7 | StructuredClassifier (Class, Component, Collaboration), Property (parts and roles), Port, Connector, ConnectorEnd, CollaborationUse, Collaboration, Interface (ball and socket), InterfaceRealization, Usage, Dependency (role binding), InstanceSpecification, Constraint, Comment |
| Component diagram | structure | component | Annex A names clause 11 (Structured Classifiers), 11.6 | Component, Interface, Port, Connector (assembly, delegation), ComponentRealization, InterfaceRealization, Usage, Dependency, Class, Artifact (artifacts compartment), Package, Property, Constraint, Comment |
| Deployment diagram | structure | deployment | Annex A names clause 19 (Deployments) | Node, Device, ExecutionEnvironment, Artifact, DeploymentSpecification, Deployment, Manifestation, CommunicationPath, Component, InstanceSpecification (of nodes and artifacts), Property (nested structure), Dependency, Package, Constraint, Comment |
| Profile diagram | structure | package (a profile is a package; no separate frame kind) | Annex A names clause 12 (Packages), 12.3 | Profile, Stereotype, Class (as metaclass reference), Extension, ExtensionEnd, ProfileApplication, ElementImport and PackageImport (as reference), Package, Class, DataType, PrimitiveType, Enumeration, Association, Generalization, Property (tag definition), Image, Constraint, Comment |
| Use case diagram | behavior | use case | Annex A names clause 18 (Use Cases) | UseCase, Actor, subject classifier (boundary rectangle), ExtensionPoint, Association (actor to use case), Include, Extend, Generalization (between actors and between use cases), Dependency, Package, Constraint, Comment, Component, Class, Collaboration |
| Activity diagram | behavior | activity | Annex A names clause 15 (Activities); actions in 16 | Activity, ActivityNode, Action (and its subclasses), ControlNode (InitialNode, ActivityFinalNode, FlowFinalNode, DecisionNode, MergeNode, ForkNode, JoinNode), ObjectNode (ActivityParameterNode, CentralBufferNode, DataStoreNode, ExpansionNode, Pin, InputPin, OutputPin, ValuePin, ActionInputPin), ActivityEdge (ControlFlow, ObjectFlow), ActivityPartition, InterruptibleActivityRegion, StructuredActivityNode (ConditionalNode, LoopNode, SequenceNode, ExpansionRegion), ExceptionHandler, Variable, Constraint (pre and post conditions, guards), Comment |
| State machine diagram | behavior | state machine | Annex A names clause 14 (State Machines) | StateMachine, ProtocolStateMachine, Region, State, FinalState, Pseudostate, ConnectionPointReference, Transition, ProtocolTransition, Trigger, Event, Behavior (entry, exit, do, effect), Constraint (guard, state invariant), Comment |
| Sequence diagram | behavior | interaction (sd) | Annex A names clause 17 (Interactions), 17.8 | Interaction, Lifeline, Message, Gate, ExecutionSpecification (ActionExecutionSpecification, BehaviorExecutionSpecification), OccurrenceSpecification, MessageOccurrenceSpecification, DestructionOccurrenceSpecification, CombinedFragment, ConsiderIgnoreFragment, InteractionOperand, InteractionConstraint, InteractionUse, PartDecomposition, StateInvariant, Continuation, GeneralOrdering, TimeConstraint, TimeObservation, DurationConstraint, DurationObservation, Constraint, Comment |
| Communication diagram | behavior | interaction (sd) | Annex A names clause 17 (Interactions), 17.9 | Interaction, Lifeline, Message (with sequence expression), Connector (the links the messages travel on), Comment |
| Timing diagram | behavior | interaction (sd) | Annex A names clause 17 (Interactions), 17.11 | Interaction, Lifeline (state or condition timeline, general value lifeline), Message, MessageLabel notation, StateInvariant, OccurrenceSpecification, DestructionOccurrenceSpecification, GeneralOrdering, TimeConstraint, TimeObservation, DurationConstraint, DurationObservation, Comment |
| Interaction overview diagram | behavior | interaction (sd) | Annex A names clause 17 (Interactions), 17.10 | Interaction (inline), InteractionUse, InitialNode, ActivityFinalNode, FlowFinalNode, DecisionNode, MergeNode, ForkNode, JoinNode, ControlFlow, InteractionConstraint (guards), Constraint, Comment |

The standard gives no closed list of what each diagram admits. The lists above are this skill's reading and are guidance, not rules.

## 3. The concepts, package by package

Each table is one package. "Abstract" classes are never instantiated directly. A concept can have more than one generalization.

### 3.1 Common Structure (clause 7)

| Concept | Definition | Generalization | Abstract? | Section |
|---|---|---|---|---|
| Abstraction | A dependency whose two sides stand for the same idea at different levels of abstraction or from different viewpoints; the base for Realization, Substitution, Usage's siblings and similar mappings. | Dependency | No | 7.8.1 |
| Comment | A piece of free text that can be attached to any set of elements. | Element | No | 7.8.2 |
| Constraint | A condition or restriction, written in natural language or a machine-readable language, that states part of the meaning of one or more elements. | PackageableElement | No | 7.8.3 |
| Dependency | A relationship saying that some client elements need some supplier elements for their specification or implementation, so a change to a supplier may affect the client. | DirectedRelationship, PackageableElement | No | 7.8.4 |
| DirectedRelationship | A relationship with a defined direction, from one or more source elements to one or more target elements. | Relationship | Yes | 7.8.5 |
| Element | The root of the metamodel: anything that can appear in a model; it can own other elements and comments. | none (root) | Yes | 7.8.6 |
| ElementImport | Brings one named element from another namespace into the importing namespace so it can be used there under its unqualified name or an alias. | DirectedRelationship | No | 7.8.7 |
| MultiplicityElement | An element that carries a multiplicity: an inclusive range of non-negative whole numbers (lower to a possibly unlimited upper) for how many values or instances are allowed. | Element | Yes | 7.8.8 |
| NamedElement | An element that may have a name (given directly or by a string expression), a visibility, and a qualified name built from its owning namespaces. | Element | Yes | 7.8.9 |
| Namespace | An element that owns or imports named elements, so those can be identified by name inside it. | NamedElement | Yes | 7.8.10 |
| PackageImport | Imports all the non-private members of a package into the importing namespace, so they can be named without qualification. | DirectedRelationship | No | 7.8.11 |
| PackageableElement | A named element that a package may own directly; also usable as the parametered element of a template parameter. | ParameterableElement, NamedElement | Yes | 7.8.12 |
| ParameterableElement | An element that can be exposed as a formal template parameter, or supplied as an actual parameter when a template is bound. | Element | Yes | 7.8.13 |
| Realization | An abstraction in which the client (an implementation) realizes the supplier (a specification); used for refinement, transformation, template instantiation and the like. | Abstraction | No | 7.8.14 |
| Relationship | The abstract notion of some kind of relationship among elements. | Element | Yes | 7.8.15 |
| TemplateBinding | Binds a template to actual parameters, by owning the substitutions of actual parameters for the template's formal parameters. | DirectedRelationship | No | 7.8.16 |
| TemplateParameter | Exposes one parameterable element as a formal parameter of a template. | Element | No | 7.8.17 |
| TemplateParameterSubstitution | Pairs an actual parameter with a formal template parameter as part of a template binding. | Element | No | 7.8.18 |
| TemplateSignature | Bundles the formal template parameters of one template. | Element | No | 7.8.19 |
| TemplateableElement | An element that can be defined as a template and can be bound to other templates. | Element | Yes | 7.8.20 |
| Type | Constrains the values that a typed element can represent. | PackageableElement | Yes | 7.8.21 |
| TypedElement | A named element that may have a type. | NamedElement | Yes | 7.8.22 |
| Usage | A dependency in which the client needs the supplier for its full implementation or operation. | Dependency | No | 7.8.23 |
| VisibilityKind (enumeration) | The four levels of visibility an element can have. Literals: public, private, protected, package. | none | n/a | 7.8.24 |

### 3.2 Values (clause 8)

| Concept | Definition | Generalization | Abstract? | Section |
|---|---|---|---|---|
| Duration | A value specification for the length of time between two instants. | ValueSpecification | No | 8.6.1 |
| DurationConstraint | A constraint that restricts a duration, given by a duration interval, measured between one or two constrained elements. | IntervalConstraint | No | 8.6.2 |
| DurationInterval | A range between a minimum and a maximum duration. | Interval | No | 8.6.3 |
| DurationObservation | A reference to a duration seen during execution; it names the elements observed and whether the observation is on entry to or exit from each. | Observation | No | 8.6.4 |
| Expression | A node in an expression tree: a symbol with an ordered, possibly empty list of operand value specifications. | ValueSpecification | No | 8.6.5 |
| Interval | A range between a minimum and a maximum value specification. | ValueSpecification | No | 8.6.6 |
| IntervalConstraint | A constraint whose specification is an interval. | Constraint | No | 8.6.7 |
| LiteralBoolean | A literal true or false value. | LiteralSpecification | No | 8.6.8 |
| LiteralInteger | A literal whole number. | LiteralSpecification | No | 8.6.9 |
| LiteralNull | A literal that stands for the absence of a value. | LiteralSpecification | No | 8.6.10 |
| LiteralReal | A literal real number. | LiteralSpecification | No | 8.6.11 |
| LiteralSpecification | A value specification that gives a literal constant. | ValueSpecification | Yes | 8.6.12 |
| LiteralString | A literal character string. | LiteralSpecification | No | 8.6.13 |
| LiteralUnlimitedNatural | A literal natural number or the unlimited value (written *). | LiteralSpecification | No | 8.6.14 |
| Observation | A value determined by watching events that occur relative to other model elements. | PackageableElement | Yes | 8.6.15 |
| OpaqueExpression | A value computed either by a UML behavior or by text written in some other language, with one body per language. | ValueSpecification | No | 8.6.16 |
| StringExpression | An expression that yields a string by joining string operands or sub-expressions, some of which may be template parameters. | TemplateableElement, Expression | No | 8.6.17 |
| TimeConstraint | A constraint on a point in time, given by a time interval. | IntervalConstraint | No | 8.6.18 |
| TimeExpression | A value specification that stands for a time value. | ValueSpecification | No | 8.6.19 |
| TimeInterval | A range between a minimum and a maximum time expression. | Interval | No | 8.6.20 |
| TimeObservation | A reference to an instant seen during execution; it names the element observed and whether the observation is on entry or on exit. | Observation | No | 8.6.21 |
| ValueSpecification | The specification of a possibly empty set of values; can be used as a template parameter or an actual parameter in a binding. | TypedElement, PackageableElement | Yes | 8.6.22 |

### 3.3 Classification (clause 9)

| Concept | Definition | Generalization | Abstract? | Section |
|---|---|---|---|---|
| BehavioralFeature | A feature that specifies part of the behavior of a classifier's instances; implemented by behaviors (methods) and invoked in answer to a request. | Feature, Namespace | Yes | 9.9.2 |
| Classifier | A classification of instances according to their features; the base of every class-like thing. | Namespace, Type, TemplateableElement, RedefinableElement | Yes | 9.9.4 |
| ClassifierTemplateParameter | A template parameter that exposes a classifier as the formal parameter. | TemplateParameter | No | 9.9.5 |
| Feature | A structural or behavioral characteristic declared by classifiers. | RedefinableElement | Yes | 9.9.6 |
| Generalization | A taxonomic link from a more specific classifier to a more general one; instances of the specific one are also instances of the general one, and it inherits the general one's features. | DirectedRelationship | No | 9.9.7 |
| GeneralizationSet | A named set of generalizations that share a general classifier, with flags saying whether the subclasses cover all instances and whether they overlap. | PackageableElement | No | 9.9.8 |
| InstanceSpecification | A model element standing for an instance in the modeled system; its slots give values for the features of its classifiers. | DeploymentTarget, PackageableElement, DeployedArtifact | No | 9.9.9 |
| InstanceValue | A value specification that points at an instance specification. | ValueSpecification | No | 9.9.10 |
| Operation | A behavioral feature with a name, parameters, a return type and conditions, used to invoke an associated behavior. | TemplateableElement, ParameterableElement, BehavioralFeature | No | 9.9.11 |
| OperationTemplateParameter | A template parameter that exposes an operation as the formal parameter. | TemplateParameter | No | 9.9.12 |
| Parameter | An argument used to pass information into or out of an invocation of a behavioral feature or behavior. | MultiplicityElement, ConnectableElement | No | 9.9.13 |
| ParameterSet | A group of parameters that are alternative sets of inputs or outputs of a behavior or behavioral feature. | NamedElement | No | 9.9.16 |
| Property | A structural feature; owned by a classifier it is an attribute, and it may be an association end; owned by an association it is a navigable or non-navigable end. | ConnectableElement, DeploymentTarget, StructuralFeature | No | 9.9.17 |
| RedefinableElement | An element that a specializing classifier can redefine in its own context. | NamedElement | Yes | 9.9.18 |
| RedefinableTemplateSignature | A template signature that lets a specialization of a template classifier add formal parameters. | RedefinableElement, TemplateSignature | No | 9.9.19 |
| Slot | Gives values on an instance specification for one structural feature. | Element | No | 9.9.20 |
| StructuralFeature | A typed feature that specifies the structure of a classifier's instances. | MultiplicityElement, TypedElement, Feature | Yes | 9.9.21 |
| Substitution | A relationship saying the substituting classifier complies with the contract of the contract classifier, so its instances can stand wherever the contract classifier's are expected. | Realization | No | 9.9.22 |
| AggregationKind (enumeration) | Whether a property is a plain association end, a shared aggregation (hollow diamond) or a composite aggregation (filled diamond). Literals: none, shared, composite. | none | n/a | 9.9.1 |
| CallConcurrencyKind (enumeration) | How concurrent calls to a behavioral feature are handled. Literals: sequential, guarded, concurrent. | none | n/a | 9.9.3 |
| ParameterDirectionKind (enumeration) | The direction of a parameter. Literals: in, inout, out, return. | none | n/a | 9.9.14 |
| ParameterEffectKind (enumeration) | What a behavior does to the values passed through a parameter. Literals: create, read, update, delete. | none | n/a | 9.9.15 |

### 3.4 Simple Classifiers (clause 10)

| Concept | Definition | Generalization | Abstract? | Section |
|---|---|---|---|---|
| BehavioredClassifier | A classifier that may realize interfaces and owns behaviors, one of which can describe the behavior of the classifier itself. | Classifier | Yes | 10.5.1 |
| DataType | A type whose instances are identified only by their value. | Classifier | No | 10.5.2 |
| Enumeration | A data type whose values are the enumeration literals listed in the model. | DataType | No | 10.5.3 |
| EnumerationLiteral | A user-defined value of an enumeration. | InstanceSpecification | No | 10.5.4 |
| Interface | Declares a coherent set of services that behaviored classifiers provide by realizing the interface. | Classifier | No | 10.5.5 |
| InterfaceRealization | A realization from a behaviored classifier to an interface: the classifier conforms to the interface's contract. | Realization | No | 10.5.6 |
| PrimitiveType | A predefined data type with no substructure; its algebra may be defined outside UML. | DataType | No | 10.5.7 |
| Reception | A declaration that a classifier is prepared to react to receiving a signal. | BehavioralFeature | No | 10.5.8 |
| Signal | A kind of asynchronous communication between objects: a reaction is triggered in the receiver and nothing is returned. | Classifier | No | 10.5.9 |

### 3.5 Structured Classifiers (clause 11)

| Concept | Definition | Generalization | Abstract? | Section |
|---|---|---|---|---|
| Association | Classifies a set of links, each link being a tuple of objects typed by the association's ends; the base of association relationships. | Relationship, Classifier | No | 11.8.1 |
| AssociationClass | Both a class and an association: it connects classifiers and also has its own features. | Class, Association | No | 11.8.2 |
| Class | Classifies objects and specifies the features that give them structure and behavior; may have an internal structure and ports. | BehavioredClassifier, EncapsulatedClassifier | No | 11.8.3 |
| Collaboration | Describes a structure of collaborating roles that together achieve some functionality. | StructuredClassifier, BehavioredClassifier | No | 11.8.4 |
| CollaborationUse | Applies the pattern described by a collaboration to a particular situation, binding roles to elements. | NamedElement | No | 11.8.5 |
| Component | A modular, replaceable part of a system that encapsulates its contents and exposes provided and required interfaces. | Class | No | 11.8.6 |
| ComponentRealization | A realization that names the classifiers that realize a component's contract. | Realization | No | 11.8.7 |
| ConnectableElement | An element, such as a part or port, that plays a role in a structured classifier and can be attached to connectors. | TypedElement, ParameterableElement | Yes | 11.8.8 |
| ConnectableElementTemplateParameter | A template parameter that exposes a connectable element as the formal parameter. | TemplateParameter | No | 11.8.9 |
| Connector | A link between two or more connectable elements, enabling communication between the instances that play those roles only. | Feature | No | 11.8.10 |
| ConnectorEnd | An endpoint of a connector, attaching it to a connectable element. | MultiplicityElement | No | 11.8.11 |
| EncapsulatedClassifier | A structured classifier that may own ports, its typed interaction points. | StructuredClassifier | Yes | 11.8.13 |
| Port | A property of an encapsulated classifier that is a distinct interaction point with its environment or with its internal parts. | Property | No | 11.8.14 |
| StructuredClassifier | A classifier with an internal structure of connected parts, each playing a role in the classifier's behavior. | Classifier | Yes | 11.8.15 |
| ConnectorKind (enumeration) | Whether a connector is an assembly connector or a delegation connector. Literals: assembly, delegation. | none | n/a | 11.8.12 |

### 3.6 Packages (clause 12)

| Concept | Definition | Generalization | Abstract? | Section |
|---|---|---|---|---|
| Extension | The association that says a stereotype extends a metaclass, so stereotypes can be added to and removed from instances of that metaclass. | Association | No | 12.4.1 |
| ExtensionEnd | The end of an extension that ties it to the stereotype; its multiplicity is 0..1 (or 1 when required). | Property | No | 12.4.2 |
| Image | A graphical image, held inline or at a location, that can serve as a stereotype's icon. | Element | No | 12.4.3 |
| Model | A package that captures a view of a system, abstracted for a purpose that decides what it includes. | Package | No | 12.4.4 |
| Package | A namespace for grouping packageable elements and other packages; it can merge other packages and have profiles applied. | PackageableElement, TemplateableElement, Namespace | No | 12.4.5 |
| PackageMerge | Says that a receiving package is extended with the contents of a merged package. | DirectedRelationship | No | 12.4.6 |
| Profile | A package that defines limited extensions to a reference metamodel to adapt it to a platform or domain. | Package | No | 12.4.7 |
| ProfileApplication | Shows that a profile has been applied to a package. | DirectedRelationship | No | 12.4.8 |
| Stereotype | Defines how an existing metaclass may be extended and lets domain-specific terms or notation be used for it. | Class | No | 12.4.9 |

### 3.7 Common Behavior (clause 13)

| Concept | Definition | Generalization | Abstract? | Section |
|---|---|---|---|---|
| AnyReceiveEvent | An event for the receipt of any message that no other trigger of the behavior handles explicitly. | MessageEvent | No | 13.4.1 |
| Behavior | The specification of how a behaviored classifier changes state over time, either as a definition of possible executions or as an illustrative subset. | Class | Yes | 13.4.2 |
| CallEvent | The receipt by an object of a message that invokes a call of an operation. | MessageEvent | No | 13.4.3 |
| ChangeEvent | A change in the system that makes a stated condition become true. | Event | No | 13.4.4 |
| Event | The specification of an occurrence that may trigger effects in an object. | PackageableElement | Yes | 13.4.5 |
| FunctionBehavior | An opaque behavior that does not read or change any objects or external data. | OpaqueBehavior | No | 13.4.6 |
| MessageEvent | The receipt by an object of an operation call or a signal instance. | Event | Yes | 13.4.7 |
| OpaqueBehavior | A behavior specified as text in a language other than UML. | Behavior | No | 13.4.8 |
| SignalEvent | The receipt of an asynchronous signal instance. | MessageEvent | No | 13.4.9 |
| TimeEvent | An event that occurs at a given point in time, absolute or relative. | Event | No | 13.4.10 |
| Trigger | The point at which an event occurrence may trigger an effect in a behavior; may be qualified by the port on which the event occurred. | NamedElement | No | 13.4.11 |

### 3.8 StateMachines (clause 14)

| Concept | Definition | Generalization | Abstract? | Section |
|---|---|---|---|---|
| ConnectionPointReference | The use, inside a submachine state, of an entry or exit point pseudostate defined in the state machine the submachine state refers to. | Vertex | No | 14.5.1 |
| FinalState | A state that, when entered, says the enclosing region is complete; when every region of a state machine is complete the whole behavior is complete. | State | No | 14.5.2 |
| ProtocolConformance | Says that a specific protocol state machine conforms to a general one, or that a behavioral state machine abides by the general protocol. | DirectedRelationship | No | 14.5.3 |
| ProtocolStateMachine | A state machine defined for a classifier that states which behavioral features can be called in which states and under what conditions, giving the legal call sequences. | StateMachine | No | 14.5.4 |
| ProtocolTransition | A legal transition for an operation, described by a pre-condition, a trigger and a post-condition; attached to at most one behavioral feature. | Transition | No | 14.5.5 |
| Pseudostate | A transient vertex of a state machine graph; the machine never rests in it but passes through within a single run-to-completion step. | Vertex | No | 14.5.6 |
| Region | A top-level part of a state machine or composite state that contains vertices and transitions; several regions run in parallel. | Namespace, RedefinableElement | No | 14.5.8 |
| State | A situation during which some (usually implicit) invariant holds; simple, composite (one or more regions) or submachine. | Namespace, Vertex | No | 14.5.9 |
| StateMachine | Event-driven behavior expressed as traversal of a graph of vertices joined by transitions triggered by event occurrences. | Behavior | No | 14.5.10 |
| Transition | An arc from exactly one source vertex to exactly one target vertex; the pieces of a compound transition take the machine from one stable configuration to another. | Namespace, RedefinableElement | No | 14.5.11 |
| Vertex | A node in a state machine graph, source or target of any number of transitions. | NamedElement, RedefinableElement | Yes | 14.5.13 |
| PseudostateKind (enumeration) | The ten kinds of pseudostate. Literals: initial, deepHistory, shallowHistory, join, fork, junction, choice, entryPoint, exitPoint, terminate. | none | n/a | 14.5.7 |
| TransitionKind (enumeration) | Whether a transition is internal, local or external (affects exit and entry of the source and target). Literals: internal, local, external. | none | n/a | 14.5.12 |

### 3.9 Activities (clause 15)

| Concept | Definition | Generalization | Abstract? | Section |
|---|---|---|---|---|
| Activity | A parameterized behavior given as the coordinated sequencing of subordinate units (nodes and edges). | Behavior | No | 15.7.1 |
| ActivityEdge | A directed connection between two activity nodes. | RedefinableElement | Yes | 15.7.2 |
| ActivityFinalNode | A final node that stops the whole execution of its owning activity or structured activity node. | FinalNode | No | 15.7.3 |
| ActivityGroup | A set of activity nodes and edges in an activity; the base of partitions and interruptible regions. | NamedElement | Yes | 15.7.4 |
| ActivityNode | A point in the flow of an activity that edges connect. | RedefinableElement | Yes | 15.7.5 |
| ActivityParameterNode | An object node that accepts values from the activity's input parameters or supplies values to its output parameters. | ObjectNode | No | 15.7.6 |
| ActivityPartition | A group that collects nodes that share a characteristic, such as who performs them (a swimlane). | ActivityGroup | No | 15.7.7 |
| CentralBufferNode | An object node that manages flows from several sources to several targets. | ObjectNode | No | 15.7.8 |
| ControlFlow | An edge carrying control tokens (or control-typed object tokens) that controls when executable nodes run. | ActivityEdge | No | 15.7.9 |
| ControlNode | An activity node that coordinates flows. | ActivityNode | Yes | 15.7.10 |
| DataStoreNode | A central buffer for persistent data. | CentralBufferNode | No | 15.7.11 |
| DecisionNode | A control node that routes each token to one of its outgoing edges. | ControlNode | No | 15.7.12 |
| ExceptionHandler | Names a handler body to run if a stated kind of exception occurs while the protected executable node runs. | Element | No | 15.7.13 |
| ExecutableNode | A node whose execution can be controlled by control flows and which can have exception handlers. | ActivityNode | Yes | 15.7.14 |
| FinalNode | A control node at which a flow stops. | ControlNode | Yes | 15.7.15 |
| FlowFinalNode | A final node that ends one flow by consuming its tokens, without ending the activity. | FinalNode | No | 15.7.16 |
| ForkNode | A control node that splits one flow into several concurrent flows. | ControlNode | No | 15.7.17 |
| InitialNode | A control node that offers one control token when the activity starts. | ControlNode | No | 15.7.18 |
| InterruptibleActivityRegion | A group of nodes in which all tokens can be terminated when an interrupting edge fires. | ActivityGroup | No | 15.7.19 |
| JoinNode | A control node that synchronizes several flows into one. | ControlNode | No | 15.7.20 |
| MergeNode | A control node that accepts one of several alternative flows; it does not synchronize. | ControlNode | No | 15.7.21 |
| ObjectFlow | An edge carrying object tokens that hold values; supports multicast, multireceive, token selection and transformation. | ActivityEdge | No | 15.7.22 |
| ObjectNode | A node that holds tokens in the object flow, with optional selection, upper bound and required state. | TypedElement, ActivityNode | Yes | 15.7.23 |
| Variable | A connectable element that stores values during an activity; an alternative to object flows for passing data. | ConnectableElement, MultiplicityElement | No | 15.7.25 |
| ObjectNodeOrderingKind (enumeration) | The order in which an object node offers the tokens it holds. Literals: unordered, ordered, LIFO, FIFO. | none | n/a | 15.7.24 |

### 3.10 Actions (clause 16)

| Concept | Definition | Generalization | Abstract? | Section |
|---|---|---|---|---|
| AcceptCallAction | An accept-event action that receives a synchronous call request and yields the return information a later reply action needs. | AcceptEventAction | No | 16.14.1 |
| AcceptEventAction | An action that waits for the occurrence of one or more specific events. | Action | No | 16.14.2 |
| Action | The fundamental unit of executable functionality: a transformation or processing step in the modeled system; usable in activities and interactions. | ExecutableNode | Yes | 16.14.3 |
| ActionInputPin | An input pin that runs an action to determine the values it supplies to another action. | InputPin | No | 16.14.4 |
| AddStructuralFeatureValueAction | Adds values to a structural feature. | WriteStructuralFeatureAction | No | 16.14.5 |
| AddVariableValueAction | Adds values to a variable. | WriteVariableAction | No | 16.14.6 |
| BroadcastSignalAction | Sends a signal instance to all potential target objects in the system; the sender continues at once and gets no reply. | InvocationAction | No | 16.14.7 |
| CallAction | An action that invokes a behavior with argument values and, if synchronous, receives reply values. | InvocationAction | Yes | 16.14.8 |
| CallBehaviorAction | A call action that invokes a behavior directly. | CallAction | No | 16.14.9 |
| CallOperationAction | A call action that sends an operation call request to a target object, which may invoke the associated behavior. | CallAction | No | 16.14.10 |
| Clause | One branch of a conditional node: a test section and a body section executed only if the test is true. | Element | No | 16.14.11 |
| ClearAssociationAction | Destroys all links of an association in which a given object takes part. | Action | No | 16.14.12 |
| ClearStructuralFeatureAction | Removes all values of a structural feature. | StructuralFeatureAction | No | 16.14.13 |
| ClearVariableAction | Removes all values of a variable. | VariableAction | No | 16.14.14 |
| ConditionalNode | A structured node that chooses one of several alternative sets of executable nodes to run. | StructuredActivityNode | No | 16.14.15 |
| CreateLinkAction | Creates links. | WriteLinkAction | No | 16.14.16 |
| CreateLinkObjectAction | Creates link objects (instances of association classes). | CreateLinkAction | No | 16.14.17 |
| CreateObjectAction | Creates an instance of a given classifier. | Action | No | 16.14.18 |
| DestroyLinkAction | Destroys links, including link objects. | WriteLinkAction | No | 16.14.19 |
| DestroyObjectAction | Destroys objects. | Action | No | 16.14.20 |
| ExpansionNode | An object node marking a collection input or output of an expansion region. | ObjectNode | No | 16.14.22 |
| ExpansionRegion | A structured node whose content runs once per element of its input collections. | StructuredActivityNode | No | 16.14.23 |
| InputPin | A pin that holds input values for an action to consume. | Pin | No | 16.14.24 |
| InvocationAction | The base of actions that request behavior invocation. | Action | Yes | 16.14.25 |
| LinkAction | The base of actions that identify links to act on through link end data. | Action | Yes | 16.14.26 |
| LinkEndCreationData | Link end data giving values for one end of a link to be created. | LinkEndData | No | 16.14.27 |
| LinkEndData | Identifies one end of a link to be read or written by a link action, through the end object and any qualifier values. | Element | No | 16.14.28 |
| LinkEndDestructionData | Link end data giving values for one end of a link to be destroyed. | LinkEndData | No | 16.14.29 |
| LoopNode | A structured node for an iterative loop with setup, test and body sections. | StructuredActivityNode | No | 16.14.30 |
| OpaqueAction | An action whose functionality is not specified in UML. | Action | No | 16.14.31 |
| OutputPin | A pin that holds output values an action produces. | Pin | No | 16.14.32 |
| Pin | An object node and multiplicity element that supplies input values to an action or takes its output values. | ObjectNode, MultiplicityElement | Yes | 16.14.33 |
| QualifierValue | Part of link end data: the value for one qualifier of that end. | Element | No | 16.14.34 |
| RaiseExceptionAction | Causes an exception; the input value becomes the exception object. | Action | No | 16.14.35 |
| ReadExtentAction | Retrieves the current instances of a classifier. | Action | No | 16.14.36 |
| ReadIsClassifiedObjectAction | Tests whether an object is classified by a given classifier. | Action | No | 16.14.37 |
| ReadLinkAction | Navigates an association to retrieve the objects at one end. | LinkAction | No | 16.14.38 |
| ReadLinkObjectEndAction | Retrieves an end object from a link object. | Action | No | 16.14.39 |
| ReadLinkObjectEndQualifierAction | Retrieves a qualifier end value from a link object. | Action | No | 16.14.40 |
| ReadSelfAction | Retrieves the context object of the behavior execution it runs in. | Action | No | 16.14.41 |
| ReadStructuralFeatureAction | Retrieves the values of a structural feature. | StructuralFeatureAction | No | 16.14.42 |
| ReadVariableAction | Retrieves the values of a variable. | VariableAction | No | 16.14.43 |
| ReclassifyObjectAction | Changes the classifiers that classify an object. | Action | No | 16.14.44 |
| ReduceAction | Reduces a collection to a single value by repeatedly combining elements with a reducer behavior. | Action | No | 16.14.45 |
| RemoveStructuralFeatureValueAction | Removes values from a structural feature. | WriteStructuralFeatureAction | No | 16.14.46 |
| RemoveVariableValueAction | Removes values from a variable. | WriteVariableAction | No | 16.14.47 |
| ReplyAction | Returns reply values to the caller of an earlier accept-call action, completing the call. | Action | No | 16.14.48 |
| SendObjectAction | Sends an input object to a target object as a request message; the sender continues at once. | InvocationAction | No | 16.14.49 |
| SendSignalAction | Creates a signal instance from argument pins and sends it to a target object; the sender continues at once. | InvocationAction | No | 16.14.50 |
| SequenceNode | A structured node that runs its executable nodes in order. | StructuredActivityNode | No | 16.14.51 |
| StartClassifierBehaviorAction | Starts the classifier behavior of the input object. | Action | No | 16.14.52 |
| StartObjectBehaviorAction | Starts the execution of a behavior, or of an object's classifier behavior, with optional arguments. | CallAction | No | 16.14.53 |
| StructuralFeatureAction | The base of actions that operate on structural features. | Action | Yes | 16.14.54 |
| StructuredActivityNode | An action that is also an activity group and whose behavior is given by the nodes and edges it owns. | Namespace, ActivityGroup, Action | No | 16.14.55 |
| TestIdentityAction | Tests whether two values are the same object. | Action | No | 16.14.56 |
| UnmarshallAction | Retrieves the values of an object's structural features and puts them on output pins. | Action | No | 16.14.57 |
| ValuePin | An input pin that gets its value from a value specification. | InputPin | No | 16.14.58 |
| ValueSpecificationAction | Evaluates a value specification and provides the result. | Action | No | 16.14.59 |
| VariableAction | The base of actions that operate on a given variable. | Action | Yes | 16.14.60 |
| WriteLinkAction | The base of link actions that create and destroy links. | LinkAction | Yes | 16.14.61 |
| WriteStructuralFeatureAction | The base of structural feature actions that change values. | StructuralFeatureAction | Yes | 16.14.62 |
| WriteVariableAction | The base of variable actions that change values. | VariableAction | Yes | 16.14.63 |
| ExpansionKind (enumeration) | How an expansion region runs its content over the elements of its input. Literals: parallel, iterative, stream. | none | n/a | 16.14.21 |

### 3.11 Interactions (clause 17)

| Concept | Definition | Generalization | Abstract? | Section |
|---|---|---|---|---|
| ActionExecutionSpecification | An execution specification that stands for the execution of an action. | ExecutionSpecification | No | 17.12.1 |
| BehaviorExecutionSpecification | An execution specification that stands for the execution of a behavior. | ExecutionSpecification | No | 17.12.2 |
| CombinedFragment | An expression over interaction fragments, made of an operator and operands, that describes many traces compactly. | InteractionFragment | No | 17.12.3 |
| ConsiderIgnoreFragment | A combined fragment for consider and ignore, which list the messages that are pertinent or can be dropped. | CombinedFragment | No | 17.12.4 |
| Continuation | A label at the start or end of an alternative operand that lets one branch continue into another fragment. | InteractionFragment | No | 17.12.5 |
| DestructionOccurrenceSpecification | The destruction of the object a lifeline represents. | MessageOccurrenceSpecification | No | 17.12.6 |
| ExecutionOccurrenceSpecification | A moment at which an action or behavior starts or finishes. | OccurrenceSpecification | No | 17.12.7 |
| ExecutionSpecification | The execution of a unit of behavior or action on a lifeline, bounded by a start and a finish occurrence. | InteractionFragment | Yes | 17.12.8 |
| Gate | A message end that connects a message crossing the boundary of a fragment with the matching message inside it. | MessageEnd | No | 17.12.9 |
| GeneralOrdering | A binary ordering saying one occurrence must come before another in a valid trace; allows partial orders. | NamedElement | No | 17.12.10 |
| Interaction | A unit of behavior focused on the observable exchange of information between connectable elements. | InteractionFragment, Behavior | No | 17.12.11 |
| InteractionConstraint | A Boolean expression that guards an operand of a combined fragment, with optional loop bounds. | Constraint | No | 17.12.12 |
| InteractionFragment | The most general unit of an interaction; each fragment is like a small interaction. | NamedElement | Yes | 17.12.13 |
| InteractionOperand | One operand of the expression a combined fragment states, with an optional guard. | InteractionFragment, Namespace | No | 17.12.14 |
| InteractionUse | A reference to another interaction, standing for its contents at that place, with arguments and gates. | InteractionFragment | No | 17.12.16 |
| Lifeline | An individual participant in an interaction; always a single interacting entity. | NamedElement | No | 17.12.17 |
| Message | A particular communication between lifelines of an interaction. | NamedElement | No | 17.12.18 |
| MessageEnd | What can occur at an end of a message. | NamedElement | Yes | 17.12.19 |
| MessageOccurrenceSpecification | The occurrence of a message event: sending or receiving a signal, or invoking or receiving an operation call. | MessageEnd, OccurrenceSpecification | No | 17.12.21 |
| OccurrenceSpecification | The basic semantic unit of interactions; sequences of occurrences give an interaction its meaning. | InteractionFragment | No | 17.12.23 |
| PartDecomposition | The description of the internal interactions of one lifeline relative to an interaction. | InteractionUse | No | 17.12.24 |
| StateInvariant | A runtime constraint on participants, placed on a lifeline, such as attribute values or states. | InteractionFragment | No | 17.12.25 |
| InteractionOperatorKind (enumeration) | The operator of a combined fragment. Literals: seq, alt, opt, break, par, strict, loop, critical, neg, assert, ignore, consider. | none | n/a | 17.12.15 |
| MessageKind (enumeration) | Whether both ends of a message are known, or it is lost, found or unknown. Literals: complete, lost, found, unknown. | none | n/a | 17.12.20 |
| MessageSort (enumeration) | The kind of communication action that generated a message. Literals: synchCall, asynchCall, asynchSignal, createMessage, deleteMessage, reply. | none | n/a | 17.12.22 |

### 3.12 UseCases (clause 18)

| Concept | Definition | Generalization | Abstract? | Section |
|---|---|---|---|---|
| Actor | A role played by a user or another system that interacts with the subject. | BehavioredClassifier | No | 18.2.1 |
| Extend | A relationship from an extending use case to an extended use case saying how and when the extending behavior can be inserted into the extended behavior. | NamedElement, DirectedRelationship | No | 18.2.2 |
| ExtensionPoint | A point in a use case's behavior where an extending use case may add behavior. | RedefinableElement | No | 18.2.3 |
| Include | A relationship saying a use case contains the behavior of another use case. | DirectedRelationship, NamedElement | No | 18.2.4 |
| UseCase | A set of actions performed by the subject that yields an observable result of value to one or more actors or other stakeholders. | BehavioredClassifier | No | 18.2.5 |

### 3.13 Deployments (clause 19)

| Concept | Definition | Generalization | Abstract? | Section |
|---|---|---|---|---|
| Artifact | A physical piece of information used or produced by development or by deploying and running a system: a model file, source file, script, executable, database table or document. | Classifier, DeployedArtifact | No | 19.5.1 |
| CommunicationPath | An association between two deployment targets through which they exchange signals and messages. | Association | No | 19.5.2 |
| DeployedArtifact | An artifact or artifact instance that has been deployed to a deployment target. | NamedElement | Yes | 19.5.3 |
| Deployment | The allocation of an artifact or artifact instance to a deployment target, optionally configured by a deployment specification. | Dependency | No | 19.5.4 |
| DeploymentSpecification | An artifact that holds the execution parameters of a component artifact deployed on a node. | Artifact | No | 19.5.5 |
| DeploymentTarget | The location for a deployed artifact. | NamedElement | Yes | 19.5.6 |
| Device | A physical computational resource with processing capability on which artifacts may be deployed; may consist of other devices. | Node | No | 19.5.7 |
| ExecutionEnvironment | A node that offers an execution environment for components deployed on it as executable artifacts. | Node | No | 19.5.8 |
| Manifestation | The concrete physical rendering of one or more model elements by an artifact. | Abstraction | No | 19.5.9 |
| Node | A computational resource on which artifacts may be deployed; nodes are joined by communication paths to form networks. | Class, DeploymentTarget | No | 19.5.10 |

### 3.14 InformationFlows (clause 20)

| Concept | Definition | Generalization | Abstract? | Section |
|---|---|---|---|---|
| InformationFlow | The circulation of information from sources to targets in a general way, without saying how it is conveyed or in what sequence; may be realized by connectors, messages or activity edges. | DirectedRelationship, PackageableElement | No | 20.2.1 |
| InformationItem | An abstract kind of information that can flow, without detail; other classifiers may represent it. | Classifier | No | 20.2.2 |

## 4. Relationship kinds

Everything a modeler draws as a line, an arrow, a nesting or a connection. The ends and their types fix what may be related. `language.yaml` also lists every association of the metamodel.

| Kind | Metaclass | Generalization | From | To | Notation | Section | Notes |
|---|---|---|---|---|---|---|---|
| Association | Association | Relationship,Classifier | memberEnd:Property[2..*] (ends typed by endType) | - | A solid line between classifiers (or one classifier and itself), or a diamond with a line per end (required for more than two ends); name, derived slash, read-direction arrow, end adornments. | 11.5.3, 11.5.4, 11.8.1 | Binary unless n-ary. Only a binary association can have an aggregation end. Ends owned by a class or listed as navigableOwnedEnd are navigable. |
| Aggregation (shared) | Property (aggregation = shared) on an end of a binary Association | - | whole end | part end | Hollow diamond on the line at the aggregate end, smaller than an association diamond. | 11.5.3, 11.5.4, 9.9.1 | At most one end of an association has aggregation shared or composite. |
| Composition (composite aggregation) | Property (aggregation = composite, isComposite derived) | - | whole end (upper bound at most 1) | part end | Filled diamond at the aggregate end. | 11.5.3, 11.5.4, 9.9.17 | The composing end has upper bound at most 1 (Property::multiplicity_of_composite). |
| Association class | AssociationClass | Class,Association | - | - | A class symbol joined to the association path (or its diamond) by a dashed line; one shared name. | 11.5.3.2, 11.5.4, 11.8.2 | Cannot generalize an Association or a Class; attributes, member ends and opposite ends have distinct names. |
| Link | InstanceSpecification whose classifier is an Association | InstanceSpecification | - | - | Association notation between instance specifications (names underlined when needed). | 9.8.4, 9.9.9 | Navigation arrows, if shown, agree with the association. |
| Generalization | Generalization | DirectedRelationship | specific:Classifier[1] (owner) | general:Classifier[1] | Solid line with a hollow triangle at the general classifier; separate-target or shared-target style. | 9.9.7, 9.2.4, 9.7.4 | Hierarchy is directed and acyclic; parents are not final; a Generalization may belong to GeneralizationSets. |
| Generalization set | GeneralizationSet | PackageableElement | - | - | Name on generalization lines, shared arrowhead, or a dashed line across arrows; {complete | incomplete, disjoint | overlapping}; power type after a colon. |
| Dependency | Dependency | DirectedRelationship,PackageableElement | client:NamedElement[1..*] | supplier:NamedElement[1..*] | Dashed arrow from client (tail) to supplier (head), optional keyword and name; dot junction for sets. | 7.8.4, 7.7.4 | Superclass of the dependency kinds below. |
| Abstraction | Abstraction | Dependency | client | supplier (same concept, different abstraction level) | Dependency with <<abstraction>> or a standard stereotype <<derive>>, <<refine>>, <<trace>>; optional mapping expression. | 7.8.1, 7.7.4, 22.3 |  |
| Realization | Realization | Abstraction | client (implementation) | supplier (specification) | Dashed line with a hollow triangular arrowhead at the realized element. | 7.8.14, 7.7.4 |  |
| Substitution | Substitution | Realization | substitutingClassifier:Classifier[1] | contract:Classifier[1] | Dependency with <<substitute>>. | 9.9.22, 9.2.4 |  |
| Usage | Usage | Dependency | client | supplier | Dependency with <<use>>; standard stereotypes <<call>>, <<create>>, <<instantiate>>, <<responsibility>>, <<send>> restrict it further. | 7.8.23, 22.3 | A socket attached to a classifier is a Usage of an Interface. |
| Interface realization | InterfaceRealization | Realization | implementingClassifier:BehavioredClassifier[1] | contract:Interface[1] | A ball (lollipop) attached to the realizing classifier, or a dashed line with a hollow triangle to the interface rectangle. | 10.5.6, 10.4.4 |  |
| Component realization | ComponentRealization | Realization | abstraction:Component[1] (owner) | realizingClassifier:Classifier[1..*] | Dashed line with a hollow triangle (same as Realization). | 11.8.7, 11.6.4 |  |
| Role binding | Dependency owned by a CollaborationUse (roleBinding) | Dependency | client element in the context classifier | supplier role in the collaboration | Dashed line from the occurrence ellipse to the client, labeled with the supplier's name; or ordinary dependency arrows with <<occurrence>>. | 11.8.5, 11.7.4 | All clients in one classifier, all suppliers in one collaboration. |
| Manifestation | Manifestation | Abstraction | artifact:Artifact[1] (owner) | utilizedElement:PackageableElement[1] | Dashed open arrow with <<manifest>>. | 19.5.9, 19.3.4 |  |
| Deployment | Deployment | Dependency | location:DeploymentTarget[1] | deployedArtifact:DeployedArtifact[*] | Dashed arrow from artifact to target with <<deploy>>, or nesting inside the target. | 19.5.4, 19.2.4 | Configured by DeploymentSpecifications, which need an ExecutionEnvironment target. |
| Template binding | TemplateBinding | DirectedRelationship | boundElement:TemplateableElement[1] | signature:TemplateSignature[1] | Dashed arrow from bound element to template with <<bind>> and substitutions. | 7.8.16, 7.3.4 |  |
| Element import | ElementImport | DirectedRelationship | importingNamespace:Namespace[1] | importedElement:PackageableElement[1] | Dashed open arrow with <<element import>> / <<element access>> (private), optional alias. | 7.8.7, 7.4.4 |  |
| Package import | PackageImport | DirectedRelationship | importingNamespace:Namespace[1] | importedPackage:Package[1] | Dashed open arrow with <<import>> (public) or <<access>> (private). | 7.8.11, 7.4.4 |  |
| Package merge | PackageMerge | DirectedRelationship | receivingPackage:Package[1] | mergedPackage:Package[1] | Dashed open arrow with <<merge>>. | 12.4.6, 12.2.4 | No cycles; not with itself or a containing or contained package. |
| Profile application | ProfileApplication | DirectedRelationship | applyingPackage:Package[1] | appliedProfile:Profile[1] | Dashed open arrow with <<apply>> or, if isStrict, <<strict>>. | 12.4.8, 12.3.4 |  |
| Extension | Extension | Association | metaclass:Class[1] | ExtensionEnd typed by Stereotype[1] | Arrow from the stereotype to the metaclass with a filled triangle; {required} when isRequired. | 12.4.1, 12.3.4 | Binary; the extension end is composite. |
| Include | Include | DirectedRelationship,NamedElement | includingCase:UseCase[1] | addition:UseCase[1] | Dashed open arrow from the base use case with <<include>>. | 18.2.4, 18.1.4 | A use case cannot include one that includes it. |
| Extend | Extend | DirectedRelationship,NamedElement | extension:UseCase[1] (extending) | extendedCase:UseCase[1]; extensionLocation:ExtensionPoint[1..*]; condition:Constraint[0..1] | Dashed open arrow from the extending use case with <<extend>>; condition and extension points in an attached note. | 18.2.2, 18.1.4 | Extension points belong to the extended use case. |
| Protocol conformance | ProtocolConformance | DirectedRelationship | specificMachine:ProtocolStateMachine[1] | generalMachine:ProtocolStateMachine[1] | (no distinct notation read) | 14.5.3 |  |
| Information flow | InformationFlow | DirectedRelationship,PackageableElement | informationSource:NamedElement[1..*] | informationTarget:NamedElement[1..*]; conveyed:Classifier[1..*] | Dependency-style dashed arrow with <<flow>>; item names near it. | 20.2.1, 20.1.4 | Realized by relationships, connectors, activity edges or messages. |
| Connector | Connector (a Feature, not a Relationship) | Feature | end:ConnectorEnd[2..*] | role:ConnectableElement[1] per end; type:Association[0..1] | Line like an association, optionally with ball-and-socket for simple ports; assembly or delegation. | 11.8.10, 11.2.4 |  |
| Communication path | CommunicationPath | Association | - | - | Association notation between nodes. | 19.5.2, 19.4.4 | Ends are deployment targets. |
| Transition | Transition | Namespace,RedefinableElement | source:Vertex[1] | target:Vertex[1] | Directed arc labeled trigger [guard] / effect. | 14.5.11, 14.2.4 |  |
| Activity edge (control flow, object flow) | ActivityEdge (ControlFlow, ObjectFlow) | RedefinableElement | source:ActivityNode[1] | target:ActivityNode[1] | Open-arrowhead line; guard in brackets, weight in braces. | 15.7.2, 15.7.9, 15.7.22, 15.2.4 | Control flows carry control; object flows carry object tokens; no object flow at executable nodes. |
| Message | Message | NamedElement | sendEvent:MessageEnd[0..1] | receiveEvent:MessageEnd[0..1] | Arrows by messageSort; lost and found with circles. | 17.12.18, 17.4.4 | Cannot cross combined fragment or operand boundaries. |
| General ordering | GeneralOrdering | NamedElement | before:OccurrenceSpecification[1] | after:OccurrenceSpecification[1] | Dotted line with a mid-line arrowhead. | 17.12.10, 17.5.4 |  |
| Comment annotation | Comment.annotatedElement | Element | Comment | annotatedElement:Element[*] | Note symbol with a dashed line to each annotated element. | 7.8.2, 7.2.4 |  |
| Constraint application | Constraint.constrainedElement | PackageableElement | Constraint | constrainedElement:Element[*] (ordered) | { constraint } text near the element, in a note, or on a dashed line between two elements. | 7.8.3, 7.6.4 |  |

## 5. Notation and semantics, by clause

My summaries of the notation and requirement sentences of each clause. The drawing rules are conventions (see `language.yaml`, `conventions`), not constraints.

### Notation and semantics notes, clauses 7 and 9 (own words)

#### 7 Common structure
- 7.2.4: Element, Relationship, DirectedRelationship have no notation of their own; each descendant defines its own. Relationships are usually a line between the related elements, directed from sources to targets for directed ones.
- 7.2.4 Comment: a note symbol (rectangle, folded upper-right corner) holding the body; one dashed line to each annotated element; the line may be dropped when the context makes it clear.
- 7.3.4 Templates: a template element carries a small dashed rectangle (usually upper right) listing its formal template parameters; the list must not be empty though it may be hidden. Parameter syntax: name [: kind] [= default]. A bound element looks like any element of that kind. A TemplateBinding is a dashed arrow from the bound element to the template with keyword <<bind>>, optionally listing substitutions `name -> actual`; alternatively the bound element's name carries `Template<name -> actual, ...>`.
- 7.4.4 Namespaces: no general notation. A NamedElement name built from a StringExpression is shown between `$` signs, with an optional alias given first. A PackageImport or ElementImport is a dashed open-arrow from the importing namespace to the imported package or element, keyword <<import>> (public) or <<access>> (private), with an optional alias; a textual form `{import qualified-name}` / `{access ...}` / `{element import ... as alias}` is also allowed.
- 7.5.4 Multiplicity: `lower..upper` text; in square brackets inside a text string (attribute), bare next to a symbol (association end); `1` stands for `1..1`, `*` for `0..*`; optional `{ordered|unordered, unique|nonunique}`.
- 7.6.4 Constraint: text in braces `{ [name :] boolean-expression }`; either in a note attached by dashed lines to each constrained element, next to a single constrained element, after an element's text string, as a dashed line between two elements (an arrowhead orders the two constrained elements), or across three or more paths of one kind. A tool shall make the constrained element determinable.
- 7.7.4 Dependency: dashed arrow from client (tail) to supplier (arrowhead), optional keyword or stereotype and name. Sets of clients or suppliers join at a dot. Usage is a Dependency with <<use>>; Abstraction is a Dependency with <<abstraction>> or a predefined stereotype (for example <<derive>>, <<refine>>, <<trace>>); Realization is a dashed line with a hollow triangular arrowhead on the realized element; Substitution is a Dependency with <<substitute>>.

#### 9 Classification
- 9.2.4 Classifier default notation: solid-outline rectangle with the name (centered, bold, normally starting with an uppercase letter) and compartments below. A keyword for the metaclass goes in guillemets above the name (listed in Annex C); no keyword for Class. Abstract classifier: name in italics or `{abstract}`. Compartments may be suppressed, and then nothing can be inferred about their contents. "attributes" is mandatory and first, "operations" mandatory and below, "receptions" mandatory and below that. Features may be grouped under public/private/protected headings. Owned classifiers or constraints may optionally be shown in extra compartments.
- 9.2.4 Generalization: a line with a hollow triangle at the general classifier; separate-target or shared-target style. Substitution: Dependency with <<substitute>>. Inherited members: caret `^` before the normal text (and optionally lighter color).
- 9.3.4 Classifier templates: template parameter syntax `name [: kind] [> constraint] [= default]`; `{contract}` before the constraint means allowSubstitutable is true; kind may be hidden when it is Class.
- 9.4.4 Features: static features underlined; an ellipsis may end a feature list; `{readOnly}` marks a read-only structural feature; redefinition either by `{redefines x}` or implicitly by an indistinguishable feature in a more general classifier. Parameter syntax: [direction] name : type [mult] [= default] [{ordered|unordered|unique|nonunique|seq|sequence}], direction defaults to in.
- 9.5.4 Property syntax: [visibility] [/] name [: type] [[mult]] [= default] [{modifiers}], visibility + - # ~; modifiers readOnly, union, subsets x, redefines x, ordered, unordered, unique, nonunique, seq, id, plus constraints. Any part may be suppressed. An attribute may alternatively be shown with association notation carrying only an aggregation adornment.
- 9.6.4 Operation syntax: [visibility] name ( [parameter-list] ) [: [return-type] [[mult]] [{modifiers}]], modifiers redefines x, query, ordered, unordered, unique, nonunique, seq, constraints; template parameters in angle brackets between name and parameter list; keywords exception and stream in the property string.
- 9.7.4 GeneralizationSet: a name on a generalization line designates the set; lines sharing one arrowhead and one label form one set; or a dashed line across separate arrowheads. Constraint labels: {complete|incomplete, disjoint|overlapping}; defaults are incomplete and overlapping. Power type: colon plus the power type name next to the set.
- 9.8.4 InstanceSpecification: like the classifier notation but with an underlined `name : Classifier[, Classifier]` ; a link (instance of an association) uses the association notation between instance specifications; anonymous is an underlined colon; slots shown as `feature = value`; an InstanceValue is shown as the name of its instance or as the instance's symbol; nested rectangles for role-playing instances, with name syntax `name / role : classifier`.

### Notation and semantics notes, clauses 10 and 11 (own words)

#### 10 Simple classifiers
- 10.2.4 DataType: classifier rectangle with <<dataType>> (or just its name when referenced); attributes then operations compartments. PrimitiveType: keyword <<primitive>>. Enumeration: keyword <<enumeration>>, literals one per line in a "literals" compartment below operations; attributes and operations compartments usually suppressed.
- 10.3.4 Signal: classifier symbol with <<signal>>; receptions go in the receptions compartment with the keyword <<signal>>.
- 10.4.4 Interface: classifier symbol with <<interface>>, or the ball (lollipop) attached by a solid line to the realizing classifier (InterfaceRealization), or the socket (half circle) attached to the classifier that requires it (Usage). Inherited interfaces on a ball carry a caret. A dependency arrow may join a socket to a ball.

#### 11 Structured classifiers
- 11.2.4 Internal structure: a mandatory compartment named "internal structure", below attributes and operations, holding part boxes (solid outline for composite parts, dashed outline for non-composite roles) and connectors. Part box name syntax is the property syntax; multiplicity may sit in the top right corner. Ports appear as small squares on the part box boundary, name and [multiplicity] beside them. A classifier other than Class carries its keyword in the part box. A Connector is drawn like an association; its name string is `[name] : association-or-association-class-name`; ends carry association-end adornments; if no multiplicity is shown the end matches the role's multiplicity (times the port's if attached to a port). Optional: ball-and-socket for assembly connectors between simple ports (a single required or provided interface each), and a channeled form for n-ary connectors. Collaboration uses can also appear in this compartment.
- 11.3.4 Port: a small square on or inside the boundary of the encapsulated classifier (inside only when connected to elements in an inner compartment, where it must lie within or overlap that compartment). Type after a colon; a conjugated port shows the type with a tilde; provided interface as ball, required as socket. A behavior port is joined by a line to a small state symbol inside the classifier. An unnamed port denotes a different port wherever drawn.
- 11.4.4 Class: the classifier symbol; four mandatory compartments (attributes, operations, receptions, internal structure) plus optional ones; no keyword needed. An active class has an extra vertical bar on each side. A constructor is an operation with one return parameter of the owning class's type, stereotyped <<Create>>; an instance specification may be the supplier of a usage from that operation. A metaclass may carry <<Metaclass>>.
- 11.5.3 Association semantics: an association declares that links may exist between instances; a link has one value per member end. Not every link need be classified by an association. Unique and ordered flags on ends affect link identity and ordering. For an end, the value of the opposite end is the collection of instances linked to chosen instances at the other ends; its cardinality is constrained by the multiplicity. Specialization of an association means links of the specializing association are also links of the specialized one. Composite aggregation: binary only, isComposite on the part end; an end may be shared or composite only if the association is binary and the other end is neither. Navigability: an end owned by a class, or a navigableOwnedEnd of the association, is navigable; otherwise not; tools may still navigate. Qualifiers partition the instances linked to a qualified instance; with a non-zero lower bound the qualifier values must be a finite set. An AssociationClass is both an Association and a Class (one name, features of both; attributes, member ends and opposite ends all have distinct names) and cannot be a generalization of an Association or a Class.
- 11.5.4 Association notation: a solid line between two classifiers (or one classifier to itself), or a diamond with a line to each end for any association and necessarily for more than two ends. Adornments: name near the symbol, slash for derived, property string, a solid triangular read-direction arrow (documentation only), generalization arrows between associations. Ends: name, visibility, multiplicity, property modifiers; an open arrowhead for navigable, a small x for not navigable; hollow diamond for shared aggregation and filled for composite, placed at the aggregate end; an optional small filled dot for "owned by the classifier", which must then be applied consistently on a diagram; the old convention equating navigability with ownership is deprecated. Association class: a class symbol joined to the association path (or its diamond) by a dashed line, one shared name. Navigability display options apply per diagram: show all arrows and crosses, suppress all, or suppress crosses and two-way arrows. Qualifier: small rectangle on the qualified end between the line and the classifier, holding the qualifier attributes one per line; it may not be suppressed.
- 11.6.4 Component: classifier rectangle with <<component>> or the component icon (two small rectangles on the left side), or both; provided and required interfaces as balls and sockets or as interface rectangles linked by dependencies; optional compartments "provided interfaces", "required interfaces", "realizations", "artifacts", "packaged elements". ComponentRealization is drawn like Realization (dashed line, hollow triangle).
- 11.7.4 Collaboration: a dashed ellipse with the name, optionally with an internal structure compartment; or a composite structure diagram; or a classifier rectangle with a keyword. A CollaborationUse is a dashed ellipse `occurrence : Collaboration` in the internal structure compartment with a dashed line per role binding, labeled at the client end with the supplier's name; alternatively a dashed arrow with <<occurrence>> and ordinary dependency arrows for bindings.

### Notes, clause 12 Packages and profiles (own words)

#### 12.2 Packages
- A package is a namespace for its packaged elements and imported members. The URI should be unique and unchanged once assigned (no need to be dereferenceable).
- PackageMerge: a directed relationship from the receiving package (source) to the merged package (target) that combines the target's contents into the source by matching rules. A model with merges means the same as the expanded model; a package may not merge itself, directly or indirectly. Any reference to an element in the receiving package denotes the merged result, not the increment; imports of the merged package still see the original. If a merge constraint is violated the merge is ill-formed and the model invalid. Explicit transformations exist only for Package, Class, DataType, Property, Association, Operation, Constraint, Enumeration and EnumerationLiteral; everything else is deep-copied, and an unmatched element of any other metatype with the same name and metatype as a receiving element is an error unless the two are exact copies.
- General merge rules: no cycles in the merge graph; a package cannot merge a package containing it or contained in it; matching typed elements have conforming types (same type, or for classes and data types a common supertype); a receiving element has no explicit references to merged elements; redefinitions of matching elements must not conflict. Results: visibility private only if both private; abstract only if both abstract; final only if both final; derived if either derived; lower bound the lesser, upper bound the greater; stereotypes from either side kept; isReadOnly only if both; isOrdered if either; isUnique false if either; constraints must not contradict and are all kept. Matching: packages, classes, data types, properties, associations by name and metatype; operations by name and parameter order and types; enumeration literals by owner and name (same order). Associations: only binary ones use the special rules; the receiving end must be composite if the merged end is, and owned by the association if the merged end is.
- Model: a package with a viewpoint string, describing a system for some stakeholders at some abstraction; relationships between models are typically Abstraction dependencies stereotyped <<Refine>> or <<Trace>>.

#### 12.2.4 Package notation
- Large rectangle with a small tab on the top left (folder icon); members inside, or outside joined by lines with a circled plus at the package end. Name goes in the large rectangle if no members are shown inside, otherwise in the tab. Member visibility by + or - before the name (packages have no protected or package visibility). `{uri = ...}` after the name. Imported (non-packaged) elements may be shown dimmed. PackageMerge: dashed open arrow from receiving to merged package with <<merge>>. Model: folder symbol with a small triangle in the upper right (or in the tab), or <<model>>.

#### 12.3 Profiles
- A profile is a restricted metamodel extension; its main construct is the Stereotype. metaclassReference (ElementImport) and metamodelReference (PackageImport) give filtering rules. Filtering applies only when the ProfileApplication has isStrict true. A metaclass and its instances are available if explicitly referenced, or (absent explicit metaclass references) a member of a package referenced by a metamodel reference, or extended by a stereotype of the applied profile; a metaclassReference overrides a metamodelReference. Strict application of profiles with disjoint available sets is invalid. Applying a profile does not change the model; hidden metaclasses cannot be created or seen.
- A profile may define or import Classes, Associations, DataTypes, PrimitiveTypes, Enumerations and Stereotypes (and Extensions); all CMOF constraints apply. Profile-defined types may only type properties in profiles or be general classifiers of other profile-defined types; they cannot type model elements in the models the profile is applied to.
- Stereotypes take part only in binary associations; where the opposite class is not a stereotype, the opposite end is owned by the association. Profile-defined binary associations have at most one composite end. A composite property of a stereotype or profile-defined class may be typed only by a profile-defined class; a property typed by a profile-defined data type, primitive type or enumeration has no aggregation. A composite stereotype property cannot be typed by a stereotype or a metaclass.
- Applying a profile applies its nested and imported profiles recursively. Public stereotypes of an applied profile may be applied to applicable elements. Required extensions (isRequired true) mean every instance of the extended metaclass must carry the stereotype or the model is not well formed. The same stereotype (or a subtype) is never applied twice to one element. Removing a profile deletes its stereotype instances and leaves the rest of the model intact. A nested profile applied by itself must state its own metaclass and metamodel references; they are not inherited from the containing profile.
- Stereotype: extends one or more metaclasses through Extension (an association with a metaclass end and an ExtensionEnd), never by generalization. If it extends several metaclasses it applies to exactly one instance of one of them at a time. Stereotype properties are the tag definitions; values are tagged values. Tools must support stereotype ownedAttributes (operations and behaviors optional). Base properties are named `base_<Metaclass>`, the extension end `extension_<Stereotype>`. Image formats reserved: SVG, GIF, PNG, JPG, WMF, EMF, BMP, or `MIME:<type>`.
- Profile XMI: a profile's URI gives the namespace URI; a model with profiles applied serializes the model and the stereotype instances in separate parts so removing a profile does not change the model part.

### Notes, 12.3.4 profile notation and clause 13 common behavior (own words)

#### 12.3.4 Notation
- Extension: an arrow from the stereotype to the extended class with a filled triangle arrowhead; adornments as an association but typically elided, never navigability arrows; `{required}` near the end when isRequired is true; the end multiplicity 0..1 or 1 may stand in for {required}.
- Profile: package notation plus <<profile>>; metaclassReference and metamodelReference as import arrows with <<reference>>. ProfileApplication: dashed open arrow from the package to each applied profile, labeled <<apply>> or, when isStrict is true, <<strict>>. Stereotype: class notation plus <<stereotype>>.
- Applying a stereotype: its name in guillemets above or before the element's name (comma-separated list for several; near the keyword if the element has one); for unnamed graphical elements near the upper right corner. Matching of stereotype names to definitions is case-insensitive. Tagged values shown as name = value pairs in a comment symbol, in extra compartments (classifiers and states only, one per applied stereotype), or above the name in braces separated by semicolons. A stereotype icon (Image) may replace the box, be shown reduced inside it, sit next to a line, or precede textual notation; it replaces any default icon such as the actor stick figure.

#### 13.2 Behaviors (semantics)
- A Behavior specifies events that may occur over time; every behavior defines at least one event (its invocation). It is a Class, so it can be instantiated (a behavior execution), specialized, and own features. A reentrant behavior (default) may be invoked again before earlier invocations complete; a non-reentrant behavior shall not, and a second invoker blocks. Preconditions are assumed true on invocation (otherwise the outcome is intentionally undefined); postconditions hold on successful completion.
- Parameters: arguments for in and inout parameters (defaults used when no argument is given); results for inout, out and return. A streaming parameter passes values during execution; a reentrant behavior shall not have streaming parameters. If a behavior has exception output parameters, either none or exactly one has a value on completion. A behavior with input (output) parameter sets accepts (posts) values from only one set per execution.
- Context: an owned behavior of a behaviored classifier has that classifier as its context; otherwise the first behaviored classifier up the ownership chain (unless it is a behavior with its own context). A behavior nested in a class (nestedClassifier) is not in that class's context. A behavior without an instantiable context serves as its own context object. A classifier behavior is started when an instance is created; a passive class (isActive false) shall not have one.
- Operations and Receptions are the two behavioral features; only classes have behavioral features and only active classes have receptions. A behavior is the method of at most one behavioral feature; the feature is owned or inherited by the class that owns the behavior; at most one method per class and feature. Method resolution is not mandated; the simple object-oriented process searches up the generalization hierarchy and is ill-formed if no method or several are found along different paths. A method has parameters corresponding to the feature's; how they are matched is left open (exact, covariant, contravariant).
- Events and triggers: an Event is a packageable element and can be shared by triggers; a Trigger appears in a transition, accept-event action and similar. Event occurrences go to the context object's event pool; one occurrence is consumed by one behavior. A trigger that names ports needs a message event and matches only messages received through those ports. AnyReceiveEvent matches any message not handled by a more specific trigger. A ChangeEvent occurs when its Boolean expression becomes true. A TimeEvent is absolute (at) or relative (after, measured from when the behavior reached the wait point; relative time events must be used in a trigger).
- Trigger notation: call event or signal event by name with optional `(assigned-names)`; any-receive `all`; change `when <expression>`; relative `after <expr>`; absolute `at <expr>`. Events have no notation outside triggers.

### Notes, clause 14 state machines (own words)

#### Notation (14.2.4)
- A state machine diagram is a graph of states and other vertices joined by transitions (arcs) or by control symbols. When redefinition is shown in a class diagram, the classifier rectangle carries <<statemachine>>.
- Composite state or state machine with regions: dashed lines divide the graph area into regions, each optionally named; a solid line separates the state's text compartments from the regions. A single-region composite state shows a nested graph.
- State: rounded rectangle with a name (optional; unnamed states are all distinct). Optional name tab (used with orthogonal regions). Compartments: name, internal behaviors (`entry / expr`, `exit / expr`, `do / expr`), internal transitions (`trigger [guard] / effect`), and for composite states a decomposition compartment. A hidden decomposition is shown by a small composite icon (two joined states, lower right). A submachine state's name is `state-name : referenced-state-machine`, with entry and exit connection point references on its border; entry/exit points are not needed when the default initial is used or the exit is a group transition from the boundary.
- State list notation (purely notational): one arc from a list of source state names to a common target.
- Pseudostate notation: initial = small filled circle (its transition may be labeled with the creation event only in a classifier-behavior state machine, otherwise unlabeled); shallow history = circle with H; deep history = circle with H*; entry point = small circle on the border; exit point = small circle with a cross on the border; junction = small filled circle; choice = diamond; terminate = cross; fork and join = short heavy bar; FinalState = circle around a small filled circle (its completion transition is unlabeled). Connection point reference: same symbols on a submachine state's border, or a "bracketed" `via name` form with graphical transitions.
- Transition text: `trigger [, trigger]* [ '[' guard ']' ] [ '/' behavior ]`; there is also a graphical flow-style transition notation for effect behaviors built from actions (transition-oriented diagrams).

#### Semantics (14.2.3, 14.3.3, 14.4.3), the statements a modeler can break
- A state machine that is the method of a behavioral feature has parameters that match the feature's.
- Simple state: no regions; composite: at least one region (orthogonal if more than one); submachine state: refers to a whole state machine. An executing machine is in exactly one active state configuration at a time.
- Initial pseudostate: source of at most one transition, which may have an effect but no trigger or guard; one per region. History pseudostates: only in composite states, at most one of each kind per region; a single outgoing default-history transition is allowed. Join: transitions into it come from different orthogonal regions and have no guard or trigger. Fork: its outgoing transitions go to orthogonal regions and have no guard or trigger. Entry point: in each region of the owner, at most one transition from the entry point to a vertex in that region; guards on these entry transitions must be true for the specification to be well formed. The predefined guard `else` may be attached to at most one outgoing transition of a choice or junction.
- Transition kinds: external (default), local (stays within the composite source; target differs from source; only inside a composite state), internal (self-transition on a state that is never exited; source must be a state). Guards are evaluated before the compound transition is enabled, except after a choice, where they are evaluated on arrival. No guard means always true. Which of several true guards is chosen is undefined.
- A transition's owner is not constrained, but its region must be owned (directly or indirectly) by the owning state machine; the innermost region containing both source and target is suggested. A transition from one region to another region of the same immediately enclosing composite state is not allowed.
- Run to completion: an event occurrence is dispatched only when the previous one is fully processed and a stable configuration is reached; each bottom-level orthogonal region fires at most one transition per step; the order across regions is undefined. A substate's transition has priority over a conflicting transition of a containing state. An internal transition conflicts only with transitions that exit the state.
- Redefinition (14.3.3): a state is redefined only by a state; a submachine state only by a submachine state whose submachine extends the redefined one's; a FinalState only by a FinalState; a Pseudostate only by one of the same kind; a ConnectionPointReference only by one whose state redefines the original's state. A redefining transition's source redefines the redefined transition's source; its target either redefines the target or is a new vertex; triggers add; guard and effect given by the redefining transition replace those of the redefined one, and are inherited when not given.
- Protocol state machines (14.4.3): defined in the context of a classifier, they give the legal orders of calls on its behavioral features from an external view; transition triggers are feature invocations, guards are pre-conditions, and post-conditions are stated; the effect of invoking a feature is not specified. A protocol state machine may be read as a specification or as executable, where legal transitions must match the triggered ones exactly.

### Notes, clause 15 activities (own words)

#### Notation (15.2.4 to 15.6.4)
- The graphical notation of 15.x is the only graphical notation for activities; a textual syntax may be used instead. An activity is its nodes and edges inside a round-cornered border (or the frame of Annex A) with the name at the upper left; activity parameter nodes sit on the border; preconditions and postconditions appear as text with <<precondition>> and <<postcondition>>; <<singleExecution>> marks isSingleExecution. The border may be omitted, and parameter nodes then go anywhere. An activity can also be drawn as a class with <<activity>>.
- Edges: open-arrowhead line between two nodes, name near the arrow, guard in square brackets near the tail, weight as `{weight = value}` (non-zero unlimited natural, `*` for unlimited). Connector notation: a small circle holding the edge name; every label must be paired exactly once, one end with one incoming edge and the other with one outgoing edge of the same flow type. Interrupting edge: lightning bolt (or zig-zag adornment). ObjectFlow between two pins can be drawn as two arrows meeting at the pins, and pins may be elided with a small square; <<selection>> and <<transformation>> notes attach behaviors to object flows; <<multicast>> and <<multireceive>> annotate object flows.
- Control nodes: initial = solid circle; activity final = solid circle inside a hollow circle; flow final = circle with an X; fork and join = a line segment (a fork has one incoming edge, a join one outgoing edge); `{joinSpec = expression}` beside a join; a combined join/fork uses one bar and maps to a join joined to a fork; merge and decision = diamond (a merge has two or more incoming edges and one outgoing; a decision has one incoming edge, plus a possible decision input flow, and several outgoing); `<<decisionInput>>` note and `<<decisionInputFlow>>` keyword; combined merge/decision is one diamond (at most one incoming flow marked as decision input flow).
- Object nodes: rectangle labeled with the type or `name:type`; `[state, ...]` below the name for inState; annotation `{upperBound = ..., ordering = unordered|ordered|FIFO|LIFO, ...}`; <<selection>> note for a selection behavior. Activity parameter node: object node symbol overlapping the border, labeled with the parameter's textual form; `{stream}` for streaming parameters, a small triangle for exception parameters. Central buffer: object node, optionally <<centralBuffer>>; data store: object node with <<datastore>>.
- Executable node: rectangle with rounded corners (specialized shapes for actions in clause 16). Exception handler: a lightning bolt from the protected node to a small square (the exception input), labeled with the exception type; alternatively a zig-zag on a straight line.
- Partitions: two parallel lines (horizontal or vertical) with the name in a box at one end (swimlanes); hierarchical and multidimensional partitioning allowed, a dimension (isDimension true) is named alongside its set of partitions; alternative: partition name in parentheses above the node name, comma-separated for several partitions, `::` for nesting; external partitions marked <<external>>. Interruptible region: dashed round-cornered rectangle around the contained nodes.

#### Semantics worth keeping (15.2.3 to 15.6.3)
- Execution is described with tokens (object, null and control). Tokens move across an edge only when offered and accepted; a token is accepted by at most one target (a fork copies). Control nodes do not hold tokens, except initial nodes and fork nodes. An executable node needs offers on all incoming control flows before starting, holds a control token while running, and offers control tokens on all outgoing control flows; all its edges are control flows (actions use pins for objects). An offer passes an edge only if the guard is true; no guard means true.
- Initial node: starting point; several initial nodes start several concurrent flows; it keeps its token until accepted. Activity final node: the first token to reach one ends the whole activity (or structured node). Flow final node ends only its own flow.
- Fork: exactly one incoming edge, all edges control or all object. Join: exactly one outgoing edge; joinSpec decides when it emits (default: a token on every incoming edge); object tokens only are offered onward if control and object tokens arrive mixed; isCombineDuplicate merges tokens with the same object. Merge: exactly one outgoing edge, all edges the same flow type, no synchronization. Decision: one or two incoming edges (two means one is the decision input flow), at least one outgoing; each token traverses at most one outgoing edge; a decision input behavior has a return parameter, no other outputs and no side effects, and its input parameters depend on which incoming flows exist; the guard `else` may be used on at most one outgoing edge of a decision node and is true only if no other outgoing edge accepts the token. Modelers should make at most one guard true for each token.
- Selection and transformation behaviors on object flows cannot have side effects; a selection behavior's input parameter is an unordered, non-unique 0..* bag and its output has upper bound 1.
- A variable shares data indirectly; actions reading and writing it must be sequenced by control flow to avoid races; values conform to the variable's type; multiplicity applies. Streaming input parameters: the activity does not finish until the posted values meet the lower bound. On completion, output parameter nodes for non-streaming outputs hold at least the lower-bound count of non-null tokens. Use exception parameters only when aborting all flows is intended (not with isSingleExecution).
- An activity with no streaming parameters completes when no node is executing or enabled, or when an activity final node is reached.

### Notes, clause 17 interactions (own words)

#### Notation and diagrams
- Frame: solid rectangle with a pentagon at the upper left containing `sd` and the interaction name and parameters; local attributes may appear near the top or in notes. Interaction overview diagrams may list their lifelines in the heading, since the lifelines do not appear.
- ExecutionSpecification: thin gray or white rectangle on the lifeline (or a wider labeled rectangle); overlapping executions overlap. StateInvariant: state symbol or constraint in braces on a lifeline. Lifeline: a rectangle head followed by a vertical (possibly dashed) line; head text `[name['['selector']']] [: type] [decomposition]`, where decomposition is `ref interactionident [strict]`; the identifier cannot be empty; the name `self` stands for the object of the enclosing classifier. Time runs down the page.
- Message: a line from send end to receive end, every segment horizontal or downward; asynchronous (asynchCall, asynchSignal) open arrowhead; synchronous (synchCall) filled arrowhead; reply dashed line with open or filled head; create dashed line with open head; delete must end in a DestructionOccurrenceSpecification (an X at the lifeline bottom); lost message small filled circle at the arrow end; found message small circle at the start; on communication diagrams messages carry an extra small arrow near name and sequence number. Label syntax: request `name [( [in-parameter-name =] value | - , ... )]`, all arguments named or none; matched by order to in and inout parameters or signal attributes, with an argument required for every one; a name given only when the message has a signature; reply `[target =] name [( out-parameter: value, ...)] [: value]`; `*` stands for any message. A reply's label may be omitted if obvious.
- GeneralOrdering: dotted line with an arrowhead mid-line. Gates: points on the frame or fragment at message ends, optionally named; message pairs at matched gates must have identical name, sort and signature and the same direction.
- CombinedFragment: solid rectangle with the operator in a pentagon at the upper left (several operators in one pentagon mean nested fragments); operands separated by dashed horizontal lines. InteractionConstraint: `[ boolean-expression | else ]` over the lifeline where the first event occurs; omitted means true. Consider/ignore: `ignore { names }` or `consider { names }` after the operator, combinable with other operators. Continuation: state-symbol shape, may cover several lifelines. Strict: vertical position is significant across all lifelines of the fragment. Coregion: brackets for a parallel fragment.
- Sequence diagram nodes (Table 17.1): frame, lifeline, execution specification, interaction use, combined fragment, state invariant, continuation, coregion, destruction occurrence, time constraint and time observation. Paths (Table 17.2): message (asynchronous, call, reply), lost, found, general ordering.
- Communication diagram: frame, lifelines, and messages drawn on the connectors between lifelines with a sequence expression: dot-separated sequence terms ending with a colon; each term `[integer | name] [recurrence]`, integers give order within the enclosing call level, names mark concurrent threads, recurrence is `*[iteration-clause]` (sequential) or `*||[...]` (concurrent) or a guard `[condition]`; correspond to simple sequence diagrams that use no interaction uses or combined fragments and ignore message overtaking.
- Interaction overview diagram: a variant of the activity diagram where, instead of object nodes, the nodes are inline interactions or interaction uses; alt is a decision with a matching merge, par a fork with a matching join, loop a simple cycle; branching and joining must be properly nested (stricter than activity diagrams); same frame as other interaction diagrams. In its purest form all nodes are interaction uses and no messages or lifelines show.
- Timing diagram: frame, lifelines with state or condition timelines (discrete or continuous), general value lifelines (value as text, crossing marks change), messages and message labels (labels with equal names mean one message that is visually interrupted), general ordering, destruction occurrence.

#### Semantics worth keeping
- An interaction means a pair of trace sets, valid and invalid; the union need not cover all traces. A lifeline's semantics is the interaction restricted to the occurrences on it; time increases down the page but distances carry no measurement.
- Message signature refers to an operation or a signal with the same name as the message; if a signal, messageSort is asynchSignal. Arguments of a non-reply message are evaluated at the send event. A reply message's arguments are expressions with at most one operand.
- alt: at most one operand is chosen, with a guard that is true; if a gate is used in one operand of an alt it is used by every operand. opt, loop, break, neg, assert have one operand. Neg makes the operand's traces invalid. Critical region traces cannot be interleaved with other occurrences on the covered lifelines. Assert: operand's sequences are the only valid continuations. Loop: iterates at least minint and at most maxint times; a separate guard stops it early or continues it. Continuations: after an alternative operand ends with continuation X, only fragments starting with X (or no continuation) can follow. Weak sequencing reduces to parallel merge on disjoint lifelines and to strict sequencing on a single lifeline.
- Part decomposition: a decomposed lifeline is treated exactly like an interaction use of the referenced interaction owned by the type of the lifeline's connectable element; combined fragments in the decomposition that mirror outer ones are called extra-global.

### Notes, clauses 2, 18 to 20, Annex A and C (own words)

#### Conformance (clause 2)
- Five independent conformance types: abstract syntax (create/read/update/delete instances of concrete metaclasses and validate well-formedness against the metamodel constraints), concrete syntax (notation CRUD; extra diagrams allowed), model interchange (import/export conformant XMI for all valid models incl. profiles; implies abstract syntax; UML 2.5 tools also load/save UML 2.4.1 XMI), diagram interchange (Annex B DI; implies concrete syntax and model interchange), semantic conformance (a demonstrable way to interpret UML semantics; normative semantics are 6.3 plus the Semantics subclauses of clauses 7 to 22; implies abstract syntax). Where the document and the machine-consumable XMI conflict, the XMI wins. Items called "undefined" or "not specified" are left for customization; customizations must not contradict the specification.

#### Annex A (diagrams)
- A diagram has a contents area and optionally a frame and heading. Heading syntax `[kind] name [parameters]` in a pentagon at the upper left; frame kinds: activity, class, component, deployment, interaction, package, state machine, use case; abbreviations act, cmp, dep, sd, pkg, stm, uc. The frame is mainly for diagrams with border elements (ports, entry/exit points). Without a frame there is no heading. The primary symbols in the contents area define the diagram type.
- Taxonomy: structure diagrams (static structure, independent of time) and behavior diagrams (dynamic behavior); the boundaries are not strictly enforced and mixing is allowed (for example a state machine nested inside an internal structure). Clauses that define each diagram's constructs: Activity Diagram - Activities; Class Diagram - Structured Classifiers; Communication Diagram - Interactions; Component Diagram - Structured Classifiers; Composite Structure Diagram - Structured Classifiers; Deployment Diagram - Deployments; Interaction Overview Diagram - Interactions; Object Diagram - Classification; Package Diagram - Packages; Profile Diagram - Packages; State Machine Diagram - State Machines; Sequence Diagram - Interactions; Timing Diagram - Interactions; Use Case Diagram - Use Cases.
- Annex B (diagram interchange) models 11 concrete diagram classes: UMLClassDiagram, UMLObjectDiagram, UMLPackageDiagram, UMLCompositeStructureDiagram, UMLComponentDiagram, UMLDeploymentDiagram, UMLProfileDiagram (all structure diagrams, with options for association display), UMLUseCaseDiagram, UMLStateMachineDiagram, UMLActivityDiagram, UMLInteractionDiagram (kind: sequence, communication, overview, timing, table). Structure diagrams have no model element except composite structure diagrams, which have exactly one (a structured classifier or an instance specification of one). A use case diagram has none; a state machine diagram exactly one StateMachine; an activity diagram exactly one Activity; an interaction diagram exactly one Interaction.

#### 18 Use cases
- UseCase: ellipse with name inside or below, optional stereotype keyword above; subject (system boundary) rectangle with name at the upper left, use case ellipses visually inside; the rectangle does not mean the subject owns the use cases; attributes and operations may be shown inside the oval; extension points in a compartment headed "extension points", each `name [: explanation]`; or the classifier rectangle with an ellipse icon at the upper right. Actor: stick figure with the name nearby, or a classifier rectangle with <<actor>>, or another icon for non-human actors. Extend: dashed open arrow from the extending use case to the extended use case with <<extend>>; the condition and extension point references may appear in a note attached to the arrow. Include: dashed open arrow from the base use case to the included one with <<include>>. Nesting of a use case in its owning classifier may be shown as a nested ellipse in a compartment.
- Semantics: each use case specifies a unit of useful functionality the subject provides and must be completed; two use cases specifying the same subject cannot be associated; the extended use case is meaningful alone, the extending one typically is not; Include inserts the addition's behavior into the including case.

#### 19 Deployments
- Deployment target (node) is drawn as a 3D box (perspective cube) labeled with its name preceded by a colon for instances; deployed elements and deployments may be drawn inside. Deployment: dashed dependency-style arrow from artifact to target, <<deploy>> when not drawn inside the target. DeploymentSpecification: classifier rectangle, optional <<deployment spec>>, attached to a deployed component with a dependency arrow. Artifact: class rectangle with <<artifact>> or a document icon. Manifestation: dashed open arrow with <<manifest>>. Device: node with <<device>>; ExecutionEnvironment: node with <<executionEnvironment>>. CommunicationPath: association notation between nodes. Semantics: a deployment specification can be associated only with deployment targets that are execution environments; the internal structure of a node consists only of other nodes.

#### 20 Information flows
- InformationFlow: Dependency-style notation (dashed arrow) with <<flow>>; the conveyed item's name near the arrow. InformationItem: classifier rectangle with <<information>> or a filled triangle; no visible sub-compartments; a filled isosceles triangle on a realizing channel shows direction (one triangle for several items in one direction); <<representation>> dashed arrows from an item to what it represents. Sources and targets are named elements (constrained by a rule to certain kinds); the channel can be realized by relationships, connectors, activity edges or messages; items are realized only by classes of all kinds, interfaces, signals and other information items.

#### Annex C keywords (normative)
- Keywords are reserved words in guillemets with three purposes: distinguish a metaclass sharing a general shape, distinguish a kind of relationship sharing a line style, or set a modifier value. Several keywords or stereotype labels on one element may each have guillemets or share one pair separated by commas. Using a keyword as a user stereotype is discouraged. The table (Table C.1) maps each keyword to its metamodel element and placement (box header, dashed-line label, line label, inline label, swimlane header, note label, top left corner, after name): abstraction, access, activity, actor, apply, artifact, bind, centralBuffer, collaboration, component, datastore, dataType, decisionInput, decisionInputFlow, deploy, deployment spec, device, element access, element import, enumeration, executionEnvironment, extend, extended, external, final, flow, import, include, information, interface, iterative, localPostcondition, localPrecondition, manifest, merge, model, multicast, multireceive, occurrence, parallel, postcondition, precondition, primitive, profile, protocol, reference, representation, selection, signal, singleExecution, statemachine, stream, Stereotype, strict, structured, substitute, transformation, use.

#### Annex D and E
- Annex D: examples (printed p. 750). Annex E: the XMI serialization of the metamodel, primitive types library, standard profile and UML DI, as the machine-consumable files; UML 2.5 tools must also read and write UML 2.4.1 XMI.

## 6. Keywords (Annex C)

Keywords are reserved words shown in guillemets. They distinguish a metaclass that shares a general shape, a kind of relationship that shares a line style, or set a modifier value. Several keywords or stereotype names on one element may each have guillemets or share one pair, separated by commas. Words in guillemets are not always keywords and not always stereotypes; using a keyword as a user stereotype name is discouraged and only possible where the contexts do not clash.

| Keyword | Metamodel element | Meaning | Placement |
|---|---|---|---|
| abstraction | Abstraction | Abstraction | dashed-line label |
| access | PackageImport | visibility = private | dashed-line label |
| activity | Activity | Activity | box header |
| actor | Actor | Actor | box header |
| apply | ProfileApplication | ProfileApplication | dashed-line label |
| artifact | Artifact | Artifact | box header |
| bind | TemplateBinding | TemplateBinding | dashed-line label |
| centralBuffer | CentralBufferNode | CentralBufferNode | box header |
| collaboration | Collaboration | Collaboration | box header |
| component | Component | Component | box header |
| datastore | DataStoreNode | DataStoreNode | box header |
| dataType | DataType | DataType | box header |
| decisionInput | Behavior | DecisionNode::decisionInput | note label |
| decisionInputFlow | ObjectFlow | DecisionNode::decisionInputFlow | line label |
| deploy | Deployment | Deployment | dashed-line label |
| deployment spec | DeploymentSpecification | DeploymentSpecification | box header |
| device | Device | Device | box header |
| element access | ElementImport | visibility = private | dashed-line label |
| element import | ElementImport | visibility = public | dashed-line label |
| enumeration | Enumeration | Enumeration | box header |
| executionEnvironment | ExecutionEnvironment | ExecutionEnvironment | box header |
| extend | Extend | Extend | dashed-line label |
| extended | Region | extendedRegion is not empty | after name |
| extended | StateMachine | extendedStateMachine is not empty | after name |
| external | ActivityPartition | isExternal = true | swimlane header |
| final | State | State::isLeaf | after name |
| flow | InformationFlow | InformationFlow | dashed-line label |
| import | PackageImport | visibility = public | dashed-line label |
| include | Include | Include | dashed-line label |
| information | InformationItem | InformationItem | box header |
| interface | Interface | Interface | box header |
| iterative | ExpansionRegion | mode = iterative | top left corner |
| localPostcondition | Constraint | Action::localPostcondition | box header |
| localPrecondition | Constraint | Action::localPrecondition | box header |
| manifest | Manifestation | Manifestation | dashed-line label |
| merge | PackageMerge | PackageMerge | dashed-line label |
| model | Model | Model | box header |
| multicast | ObjectFlow | isMulticast = true | line label |
| multireceive | ObjectFlow | isMultireceive = true | line label |
| occurrence | CollaborationUse | CollaborationUse | dashed-line label |
| parallel | ExpansionRegion | mode = parallel | top left corner |
| postcondition | Constraint | Behavior::postcondition | box header |
| precondition | Constraint | Behavior::precondition | box header |
| primitive | PrimitiveType | PrimitiveType | box header |
| profile | Profile | Profile | box header |
| protocol | ProtocolStateMachine | ProtocolStateMachine | after name / box header |
| reference | ElementImport | Profile::metaclassReference | dashed-line label |
| reference | PackageImport | Profile::metamodelReference | dashed-line label |
| representation | InformationItem::represented | represented | dashed-line label |
| selection | Behavior | ObjectFlow::selection | note label |
| signal | Signal | Signal | box header |
| singleExecution | Activity | isSingleExecution = true | inside box |
| statemachine | StateMachine | StateMachine | box header |
| stream | ExpansionRegion | mode = stream | top left corner |
| stereotype | Stereotype | Stereotype | box header |
| strict | ProfileApplication | isStrict = true | dashed-line label |
| structured | StructuredActivityNode | StructuredActivityNode | box header |
| substitute | Substitution | Substitution | dashed-line label |
| transformation | Behavior | ObjectFlow::transformation | note label |
| use | Usage | Usage | dashed-line label |

## 7. The Standard Profile (clause 22)

A conforming tool supports all the stereotypes of the Standard Profile. Each applies to the metaclass listed.

| Stereotype | Applies to | Meaning |
|---|---|---|
| Auxiliary | Class | A class that supports a more central class, typically with secondary logic or control flow; used with Focus. |
| BuildComponent | Component | A collection of elements defined for system-level development activities such as compilation and versioning. |
| Call | Usage | A usage whose source is an operation (or its class) and whose target is an operation (or its class): the source invokes the target. |
| Create | Usage | A usage saying the client classifier creates instances of the supplier classifier. |
| Create | BehavioralFeature | Marks a feature that creates an instance of the classifier to which it is attached (a constructor). |
| Derive | Abstraction | A derivation: the client can be computed from the supplier, perhaps kept for efficiency. |
| Destroy | BehavioralFeature | Marks a feature that destroys an instance of its classifier. |
| Document | Artifact | A human-readable file; subclass of File. |
| Entity | Component | A persistent information component representing a business concept. |
| Executable | Artifact | A program file that can run on a computer system; subclass of File. |
| File | Artifact | A physical file in the context of the system developed. |
| Focus | Class | A class that defines the core logic or control flow for one or more Auxiliary classes. |
| Framework | Package | A package of elements that specify a reusable architecture for all or part of a system. |
| Implement | Component | A component definition not meant to have its own specification; it implements a separate Specification it depends on. |
| ImplementationClass | Class | The implementation of a class in a programming language, where an instance has at most one class. |
| Instantiate | Usage | A usage among classifiers: operations of the client create instances of the supplier. |
| Library | Artifact | A static or dynamic library file; subclass of File. |
| Metaclass | Class | A class whose instances are also classes. |
| Metamodel | Model | A model that specifies the modeling concepts of a modeling language. |
| ModelLibrary | Package | A package of elements meant to be reused by other packages; it contains no profiles or stereotypes. |
| Process | Component | A transaction-based component. |
| Realization | Classifier | A classifier that specifies a domain of objects and also defines the physical implementation of them. |
| Refine | Abstraction | A refinement between model elements at different semantic levels; the mapping may or may not be computable. |
| Responsibility | Usage | A contract or obligation of an element in its relationship to other elements. |
| Script | Artifact | A script file that a computer system can interpret; subclass of File. |
| Send | Usage | A usage whose client is an operation and whose supplier is a signal: the operation sends the signal. |
| Service | Component | A stateless, functional component. |
| Source | Artifact | A source file that can be compiled into an executable file; subclass of File. |
| Specification | Classifier | A classifier that specifies a domain of objects without defining their physical implementation. |
| Subsystem | Component | A unit of hierarchical decomposition for large systems. |
| SystemModel | Model | A model that contains a collection of models of the same system and all relationships and constraints between elements of different models. |
| Trace | Abstraction | A trace between elements or sets of elements that represent the same concept in different models; used for tracking requirements and changes. |
| Type | Class | A class that specifies a domain of objects together with applicable operations, without defining physical implementation. |
| Utility | Class | A class with no instances; a named collection of static attributes and operations. |

## 8. Constraints

There are 580 rules: 449 formal constraints on metaclasses (clauses 7 to 20) and 131 prose rules. They are listed with ids in `rules.md` and as data in `language.yaml`. Notes on how to read them:

- A formal constraint is an invariant stated in OCL on one metaclass. Its name in the metamodel is kept (`Metaclass::name`) so it can be found in the machine-readable model.
- The metamodel also contains 225 defined query operations (derived values such as containing activity or consistency checks). They are definitions, not constraints, and are not rules here.
- Prose rules come from the semantics and notation clauses: package merge (12.2.3), profiles (12.3.3), the Standard Profile (22), and other well-formedness statements in clauses 9 to 20.
- Some rules concern a running model (reentrancy, token counts); they are marked `runtime`.
- Where the standard leaves behavior "undefined" or "not specified", no rule is stated and none should be inferred.

