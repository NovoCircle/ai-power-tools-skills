# SoaML 1.0.1, section by section

This is a summary of the OMG specification in our own words. It is not a substitute for the specification, and it does not reproduce its text; the few short quoted phrases are cited. Section numbers are the specification's. "p." is the printed page. Where the standard is silent or inconsistent, this file says so rather than filling the gap.

Source: Object Management Group, *Service oriented architecture Modeling Language (SoaML)*, version 1.0.1, formal/12-05-10, May 2012 (https://www.omg.org/spec/SoaML/1.0.1). Machine-readable forms published with it: the UML profile (ptc/12-05-03) and the metamodel (ptc/12-05-02), both under the 20120501 base address.

## 1. What the standard is

**Identity.** SoaML is an OMG standard in the Modeling Platform category. Version 1.0.1 is the latest; 1.0 (March 2012) came before it. (About page.)

**Nature.** SoaML gives two equivalent expressions of one language for specifying and designing services in a service-oriented architecture: a UML profile (the form people use in ordinary UML modeling) and a metamodel that extends UML. Both capture the same semantics (1). Everything SoaML adds is built on UML 2.1 concepts. SoaML is not a method and defines no diagram kinds of its own.

**Scope (1).** SoaML covers: identifying services and the requirements they fulfill; specifying services (the functions provided, what consumers must provide, the protocols for using them, the information exchanged); defining service consumers and providers and how they are connected; policies for using and providing services; classification schemes for organizing model content; and links to business motivation, business process and use case models. It deliberately stays at the basic service-modeling concepts so other standards can extend it.

**Conformance (2).** A tool is compliant if it implements UML at the L3 level and SoaML's extensions, either as a profile or as a metamodel merged into UML. Three compliance points exist: P1 (the profile), P2 (the metamodel, basic) and P3 (the metamodel with the business motivation link). The categorization package is optional in P1. Nothing in the standard certifies a model, only a tool.

## 2. How the language thinks (6.1)

**Service.** A service is value delivered to one party by another through a well-defined interface and available to a community, which may be the public. Service-oriented architecture is a way of describing organizations, communities and systems so that people, organizations and systems provide services to each other (6.1.1).

**Business and IT.** The standard treats SOA as an approach to architecture for any kind of system, including organizations and processes, not only information technology. A services architecture may be a business architecture, a mission architecture, a community architecture or an IT systems architecture, and all can be equally service oriented (6.1.2).

**Three ways to specify a service (6.1.3).** The same ideas appear in three levels of ceremony, which the language supports side by side:

- **Simple interface.** One interface, used as the type of a Service port on the provider and a Request port on the consumer. One-way: the consumer calls, the provider answers, and the provider makes no assumption about who calls. It is the degenerate case of both the others.
- **Service interface.** A ServiceInterface is defined from the provider's side. It provides the interfaces the provider offers and uses the interfaces it expects of the consumer, and may own a protocol (a behavior) for the exchange. It types a Service port on the provider and a Request port on the consumer. Best when one or two parties are involved and existing capabilities are being exposed.
- **Service contract.** A ServiceContract sits in the middle between the parties: it defines the roles (provider, consumer, possibly others), the interfaces that type each role, and the choreography. Each participant's port is typed by the interface for its role, and that binds the participant to the contract. Best when an enterprise or community architecture is defined first and services are built or adapted to fit, or when more than two parties are involved.

The practical difference: whether the interaction is defined once, separately from the participants (contract), or on each participant's own Service and Request (service interface).

**Top-down and bottom-up (6.1.4).** Services may be identified by designing services architectures, by organizing capabilities into a hierarchy, by working from business processes, by exposing existing assets, or by finding shared data. Whatever the route, a service is formalized by a service description: its purpose and the protocol for using and providing it. Provider implementation may use methods (behaviors owned by the participant), event handling, or delegation to internal parts. Logical services are kept apart from their physical realizations.

**Key concepts of basic services (6.1.5).** Participants provide services through ports marked as Service, and request them through ports marked as Request. The port's type says how to use the service: a plain interface for the simplest case, otherwise a ServiceInterface.

## 3. Simple interfaces and interface-based SOA (6.2, 6.2.1)

A simple interface needs nothing else; it may optionally be wrapped in a ServiceInterface or ServiceContract (6.2).

A ServiceInterface has three parts: the provided and required interfaces (ordinary UML interfaces it realizes and uses), the ServiceInterface itself as a class, and an owned behavior that is the protocol (6.2.1). Its enclosed parts are the roles of the connected parties: the part typed by the realized interface is the provider, the part typed by the used interface is the consumer. The information it carries is: the service name; the provided interactions; the consumer's needs; each operation or reception with its preconditions, postconditions, inputs, outputs and exceptions; the protocol; implementation rules for providers; constraints that say whether the service achieved its purpose; and the capabilities it exposes (6.2.1, Table 6.1 in 6.4.17).

On the participant, a port marked Service and typed by the ServiceInterface is where the service is offered. A port marked Request and typed by the same ServiceInterface is where it is consumed. A Request is the conjugate of a Service: provided and required interfaces swap, and a tilde before the type name shows it. Because they are conjugate, a Request and a Service of the same type can be connected (6.2.1.2).

## 4. Services architectures (6.2.2)

A **ServicesArchitecture** is a network of participant roles providing and consuming services for a purpose. Participants play roles in it; a role is the function an entity performs in a context, while a Participant is the type that fills it. It is a collaboration. It has two granularities:

- **Community level.** A top-level view of independent participants working together. No controlling entity is assumed. Often called a business-to-business architecture.
- **Participant level.** How the parts of one participant (departments, components) work together to provide that participant's services. It usually has an associated business process, and roles outside the participant are drawn with dashed outlines (shared aggregation in UML) to show they are external.

A participant fills a role if it has ports with types compatible with the services the role must provide and consume. The same participant can play roles in many architectures. A participant that realizes an architecture must adhere to it. Architectures can be composed from other architectures and contracts, so they can describe systems "all the way down".

## 5. Service contracts (6.2.3, 6.2.4)

A **ServiceContract** is a UML collaboration made binding. It defines the terms, interfaces and choreography that parties must agree to, directly or indirectly, for the service to be enacted. Each role has a type, an interface or a service interface. The choreography is a behavior owned by the contract (an interaction, activity, state or timing description) that says what passes between the parties and when, without saying how any party does its part. A participant is bound by a contract when a port is typed by a role's interface; unlike a plain UML collaboration, no explicit collaboration use is needed.

Ordinary case: two roles, a Provider interface and a Consumer interface. The consumer normally starts the exchange. The Consumer interface uses the Provider interface (the consumer calls the provider); the Provider interface may use the Consumer interface (callbacks). A contract can have more than two parties; the standard's example is an escrow purchase where a mediator sits between purchaser and seller. A contract can nest other contracts, which makes it a compound contract. One contract can specialize another. A simple interface can be wrapped in a contract so it can take part in an architecture.

Two styles of use are equivalent for a binary contract: each participant's port typed by its own role's interface (consumer side typed by the Consumer interface), or both ports typed by the Provider interface with the consumer's marked Request. For more than two parties the Request style works less well.

An existing bottom-up service can be joined to a top-down contract with an adapter (6.2.4.5).

## 6. Capabilities (6.2.5)

A **Capability** is the ability to act and produce an outcome that achieves a result. Capabilities let an architect talk about what must be done before deciding who does it. They can be organized into packages and layers, have usage dependencies on each other, and own behaviors that are the methods of their operations. A Capability can realize a ServiceInterface (the interface is the specification, the capability the implementation), a Participant can realize a Capability, and a participant can have parts typed by Capabilities. A ServiceInterface can **expose** a Capability without realizing it: a looser statement that the interface provides access to the capability. Exposure can identify candidate services.

## 7. Business motivation (6.2.6)

A ServiceContract or any other behaviored classifier can realize an element of the business motivation model (vision, goal, objective, mission, strategy, tactic, policy, regulation) through a MotivationRealization. This ties services to the reason they exist, while keeping business and IT concerns apart. A ServiceContract can also realize use cases; the use case's actors may type the contract's roles.

## 8. The profile (6.3, 6.4)

Figures 6.24 to 6.29 show the profile in six groups: BMM integration, contracts, services, service data, milestones and capabilities. Each concept is described in 6.4. For every one the standard gives the UML concept it extends, attributes, constraints, semantics, notation and examples. In summary (full detail in `language.yaml`):

| Concept | Extends | In brief |
|---|---|---|
| Agent | Component | A participant with its own life cycle; its active flag is true (6.4.1) |
| Attachment | Property | A part of a message carried alongside it; optional encoding and media type (6.4.2) |
| Capability | Class | Ability to act toward a result (6.4.3) |
| Consumer | Interface or Class | Type of the consumer role (6.4.4) |
| Collaboration | Collaboration | Adds a strictness default (6.4.5) |
| CollaborationUse | CollaborationUse | Adds strictness; role bindings must be compatible when strict (6.4.6) |
| Expose | Dependency | ServiceInterface to Capability (6.4.7) |
| MessageType | DataType, Class, Signal | Pure data exchanged between parties (6.4.8) |
| Milestone | Comment | Progress marker in a behavior (6.4.9) |
| Participant | Class | Party that provides and consumes services (6.4.10) |
| Port | Port | Adds a flag for whether a connector is required (6.4.11) |
| Property | Property | Adds an identifying flag (6.4.12) |
| Provider | Interface or Class | Type of the provider role (6.4.13) |
| Request | Port | Conjugate port where a service is consumed (6.4.14) |
| ServiceChannel | Connector | Path between a Request and a Service (6.4.15) |
| ServiceContract | Collaboration | Binding agreement among the parties (6.4.16) |
| ServiceInterface | Class | Provider-side definition of a service, type of Service and Request ports (6.4.17) |
| Service | Port | Port where a service is offered (6.4.18) |
| ServicesArchitecture | Collaboration | How participants work together for a purpose (6.4.19) |

**Agent (6.4.1).** An autonomous, interactive, adaptive classification of entities. It is a Participant with the added ability to be an active participant: it has its own thread of control or life cycle. A plain Participant's needs and capabilities are static; an Agent's may change over time. A Participant's own classifier behavior is limited to a constructor; an Agent's is its life cycle. Constraint: the active flag is always true.

**Attachment and Message Type (6.4.2, 6.4.8).** A MessageType is a value object: pure data with no identity, no operations, no behaviors, only public attributes of primitive or message type. It excludes headers and protocol details and may not depend on the location or environment of either party. Aggregations are the only associations allowed. It may also be applied to a Class (whose identity is then ignored). Service operations come in two parameter styles: document style (at most one in, one out and one exception parameter, all of message type) and RPC style (any number of in, inout and out parameters and a return, of primitive or data type). Everything is call by value. An Attachment marks a part of a message that is attached, not embedded, and can have its own encoding and media type.

**Capability (6.4.3).** As in section 6 above. Shown in context on a service dependencies diagram. Capabilities realize service interfaces, depend on each other and are exposed by them.

**Provider and Consumer (6.4.4, 6.4.13).** The two interfaces that type contract roles. Both are bound by the contract's constraints and behavior. The Consumer uses the Provider; the Provider may use the Consumer.

**Collaboration and CollaborationUse (6.4.5, 6.4.6).** Each has a strictness flag. A collaboration's flag sets the default for each use of it. A strict use means the parts bound to roles must be compatible with them: the same type, a type that specializes or realizes the role's type, or a type that has at least the role type's attributes and operations; and the owning classifier's behaviors must be compatible with the collaboration's behavior. A non-strict use means the modeler warrants that the part can play the role. A ServiceContract is binding without a collaboration use when the types are compatible. Compatibility between role types is a semantic variation point: left to modelers and tools.

**Expose (6.4.7).** From a ServiceInterface to a Capability; it says the interface provides operations and information consistent with the capability. It is not a realization.

**Milestone (6.4.9).** A comment-style marker in a behavior that carries an integer progress value and optionally a signal and expressions. It lets a behavior be analyzed for liveness or traced for monitoring. It adds nothing to the functional meaning of the behavior and may be ignored by implementations.

**Participant (6.4.10).** A party or component that provides or consumes services. A participant is a provider if it offers a service and a consumer if it uses one, usually both. It has ports, marked Service and Request, as its interaction points; it may own a behavior or process, and a participant architecture. Constraint: a Participant cannot realize or use interfaces directly, only through its ports (the inside of a component that implements it is not bound by this). It implements a service operation by a method (an owned behavior), by event handling, or by delegation to a part or to another participant, and the standard leaves the choice and the mix to the designer. A participant can be a specification realized by another participant.

**Port (6.4.11).** Adds a flag saying whether a connector is required on the port. When required (the default), every instance of the port must have a connector or service channel; when not, the owner can work without one. The standard also mentions UML's service convention for ports (client-facing versus implementation-facing).

**Property (6.4.12).** Adds an identifying flag. An identifying property helps tell apart instances of its classifier, for example a purchase order number, and carries correlation in messages. A classifier can have several, and compound identifiers use a class or data type with the flag.

**Request (6.4.14) and Service (6.4.18).** Two ports on a participant. A Service is where it offers a service and a Request is where it consumes one. Both are typed by a ServiceInterface or a plain Interface. A Request is conjugated; a Service has an incoming direction. A Request can connect to any Service whose type is compatible. Either may be linked to a business motivation element to show its intended goal or value proposition, and may carry constraints for qualities of service. A service is more than a single operation call: it may involve a conversation with a protocol.

**ServiceChannel (6.4.15).** A connector between a Request and a Service. One end is a Request and the other a Service, and they must be compatible. Compatibility is structural and behavioral. Structural: same type, or the Service's type specializes or realizes the Request's type, or their needs and capabilities match operation for operation (including in the other direction), or any of these holds for the part of a service interface a port covers. Behavioral compatibility is a semantic variation point. The channel's contract behavior must be compatible with the protocols of the ports. Loose coupling means compatibility does not require a common type or a common contract.

**ServiceContract (6.4.16).** As in section 5. Role types must be a service interface or an interface or class marked Provider or Consumer, with at least one of each kind. The role types must use the types of the roles they connect to. A contract can specialize another, can nest others and can be one of the artifacts that formalizes requirements and service-level agreements.

**ServiceInterface (6.4.17).** As in section 3. Constraint: all its parts are typed by the interfaces it realizes or uses. It can realize any number of interfaces (some platform-specific models may restrict to one). It can own protocols of any behavior kind and constraints that state what success means. It may have ports of its own, which allows a composite service built from smaller services between the same parties. A ServiceInterface with more than two parts supports services where work is divided among several parties; then the combination of the channels through the port must be compatible with the protocol.

**ServicesArchitecture (6.4.19).** As in section 4. Constraint: its parts are typed by a Participant or a Capability; each participant that fills a role has a port for each role binding attached to it, with a type compliant with the role's type in the contract. Optional but recommended. A participant's roles correspond to the swim lanes of a related business process.

## 9. Categorization (7)

SoaML adds a general way to classify model elements along several independent dimensions at once (owner, architectural layer, location, status). UML allows an element in only one package; categorization lifts that limit.

- A **Catalog** is a package-like collection of Categories and other Catalogs. It may contain nothing else.
- A **Category** is a kind of information about elements (for example owner or cost). It must be in a Catalog. Its attributes and constraints describe it. Its meaning is up to the modeler, and the standard does not say what being categorized implies.
- A **CategoryValue** is an instance of a Category that supplies values for its attributes. Its classifier must be a Category.
- A **Categorization** links any element to a Category or a CategoryValue. Its target must be one of those. An element can have many categorizations and a category can apply to many elements.

Three placeholders (NodeDescriptor, FreeFormDescriptor, FreeFormValue) stand for elements of the OMG Reusable Asset Specification. Categorization is optional in the profile compliance point. The worked example (7.3.3) uses a catalog of owners and gives each participant its owner and a cost per use.

## 10. Business motivation integration (8)

SoaML offers two things for linking services to the business motivation model: a placeholder for a motivation element, to be replaced by a real business motivation profile or metamodel, and a MotivationRealization, which is a realization from a behaviored classifier (for example a contract) to a motivation element. The link is optional and assumes the business motivation model is available as a profile or a mergeable package. The standard's example shows a vision, goals, objectives, mission, strategies and tactics for processing purchase orders, and a contract that realizes several of them.

## 11. The metamodel (9)

The metamodel form extends UML in five areas: participants, services, interfaces, service contracts and service data, plus capabilities and categorization. A participant that provides services holds "service points" and one that consumes holds "request ports"; the relations "offers" and "makes" are derived from the owned ports by kind. A ServiceInterface used on a Service port means the owner can implement it; on a Request port, the owner uses it. Section 9.2 maps the profile to the metamodel. The profile is what this skill describes; the two are equivalent by design.

## 12. Annexes (informative)

- **Annex A** compares SoaML concepts with the OASIS service-oriented architecture reference model, the OASIS reference architecture and The Open Group SOA ontology. It records, among other points, that service discovery and descriptions for discovering services are out of scope.
- **Annex B** is the running example: a dealer network (dealers, manufacturers, shippers) with a purchasing service made of an ordering service and an invoicing service, a manufacturer's internal architecture, a purchase-order business process and the participant components behind the roles. It shows the whole chain from services architecture to contracts to participants, ports and interfaces.
- Annexes C (a purchase-order example with a vendor tool) and D (a mapping to the Business Process Definition Metamodel) were not read.

## 13. Silences and variation points

- **No diagram types or viewpoints.** SoaML adds keywords and icon decorations to UML notation but names no diagram kinds. The informal views the examples use are listed in `SKILL.md`.
- **Semantic variation points.** The standard leaves to modelers and tools: the compatibility of types used as roles in a collaboration use; behavioral compatibility of component realizations; behavioral compatibility between Requests and Services; when the owned rules of a ServiceInterface are evaluated; and how its behaviors are checked against participants' behaviors.
- **What is not covered.** Service discovery, registries and descriptions for finding services; policy languages (policies are constraints without a prescribed form); quality-of-service models (the standard points to a separate OMG specification).
- **Undefined terms.** The standard uses "ParticipantArchitecture" and names "NoteDescriptor" without defining them. Several spellings of the service and request port concepts are used across the document.
