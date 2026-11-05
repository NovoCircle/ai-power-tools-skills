---
name: soaml-1
description: The OMG Service oriented architecture Modeling Language (SoaML) 1.0.1, a UML profile for specifying and designing services - participants that provide and consume services through service ports and request ports, service interfaces, service contracts and their choreography, provider and consumer roles, service channels, services architectures, capabilities, message types, categorization and a link to business motivation. Use when someone is modeling a service oriented architecture (SOA) in UML, services and service participants, service contracts or service interfaces, services architectures, service and request points, capabilities, or message types, or when they ask what SoaML allows.
---

# SoaML 1.0.1

SoaML is the Object Management Group's standard for modeling services and service-oriented architecture. It is a UML profile: it takes UML concepts (class, port, collaboration, interface) and gives them service meaning, with an equivalent metamodel for tools that extend UML directly. It is a language, not a method.

**SoaML defines no diagram types and no viewpoints.** It adds keywords and icon decorations to UML notation. The views below are the informal ones its own examples use; any named diagram kind, template or layout belongs to whatever draws the model.

## What you are creating

A SoaML model answers a chain of questions about a community, an organization or a system:

1. Who provides and uses services? (Participants, Agents)
2. Where does each one offer or consume a service? (Service and Request ports)
3. What exactly is the service? (Service Interface, or Service Contract with Provider and Consumer roles)
4. How do the parties fit together for a purpose? (Services Architecture)
5. What abilities lie behind the services? (Capabilities)
6. What information moves between them? (Message Types)
7. Why does it exist? (a link to a business motivation model)

Each SoaML concept **extends one UML concept**, and the standard defines it that way. The base is named below and in `language.yaml` (`extends`). A SoaML concept is applied to an element of that UML kind: a Participant to a class, a Service to a port, a Service Contract to a collaboration, and so on.

## Three ways to specify a service

The language supports three levels side by side. Pick by how many parties are involved and where the agreement lives.

| Approach | Use when | You create |
|---|---|---|
| **Simple interface** | One-way, no protocol, no assumption about the caller | One interface, used as the type of a Service port and a Request port |
| **Service interface** | One or two parties; exposing existing capability; the provider defines the terms | A Service Interface that realizes the provider's interface(s), uses the consumer's, and may own a protocol; it types a Service port on the provider and a Request port on the consumer |
| **Service contract** | An enterprise or community architecture comes first; or more than two parties | A Service Contract with roles typed by Provider and Consumer interfaces and a choreography; each participant's port is typed by its role's interface, which binds it |

The simple interface is the degenerate case of both others.

## Informal views

None is a standard diagram type. Each is what the standard's own examples draw.

| View | What it admits |
|---|---|
| **Services Architecture** | Services Architecture (collaboration), participant and capability roles, service contracts bound to the roles. At participant level: the roles inside one participant, with external roles in dashed outline |
| **Service Contract** | Service Contract (collaboration), role types (Provider, Consumer, Service Interface, interface), uses dependencies between them |
| **Choreography** | The interaction or activity owned by a contract or service interface |
| **Participants** | Participants and Agents with Service and Request ports typed by interfaces or service interfaces; connected ports (Service Channels) |
| **Service Interface** | The Service Interface, the interfaces it realizes and uses, its role parts and protocol |
| **Capabilities** (the standard's "service dependencies diagram") | Capabilities, usage dependencies between them, realized service interfaces, Expose |
| **Service Data** | Message Types, Attachments, identifying properties |
| **Categorization** | Catalogs, Categories, Category Values applied to elements |
| **Business Motivation** | Motivation elements and the Motivation Realizations from a contract |

## The concepts, in plain words

28 concepts. Each line names the UML concept it extends. The spelling is the standard's own (no spaces); readable forms are in `language.yaml`.

### Participants

- **Participant** (extends Class): the type of a party that provides or uses services: a person, organization, system, application or component. It has Service ports and Request ports, can follow any number of services architectures, and may own behaviors that implement its services. It does not realize or use interfaces directly; it does so only through its ports.
- **Agent** (extends Component, specializes Participant): a participant with its own life cycle that can adapt to its environment. A plain Participant's needs and capabilities are static; an Agent's can change over time. An Agent is always active.

### Service ports and channels

- **Service** (extends Port; the metamodel spells it ServicePoint): where a participant offers a service. Typed by a Service Interface or a plain Interface. Its direction is incoming.
- **Request** (extends Port; also spelled RequestPoint or Request Port): where a participant consumes a service. Typed the same way. A Request is **conjugate**: it uses the type where a Service implements it, so the same Service Interface can type both ends. A tilde before the type name shows it.
- **Port (refinement)** (extends Port): adds whether a connector is required on the port. Default true: every instance of the port is connected.
- **ServiceChannel** (extends Connector): the communication path between a Request and a Service. One end each; the two must be compatible.

### Service specification

- **ServiceInterface** (extends Class): the provider-side definition of a service. It realizes the interfaces the provider offers (the provided side), uses the interfaces it expects of the consumer (the required side), has role parts typed by those interfaces, and may own a protocol behavior and constraints. It is a class, not a UML interface.
- **ServiceContract** (extends Collaboration): the binding agreement among the parties. Roles typed by interfaces; an owned choreography; may use nested contracts (a compound contract) and may specialize another contract.
- **Provider** and **Consumer** (each extends Interface, or Class in a composite contract): the types of the two role kinds in a contract. The Consumer uses the Provider; the Provider may use the Consumer for callbacks. Both are bound by the contract.

### Architecture

- **ServicesArchitecture** (extends Collaboration): how participants work together for a purpose by providing and using services. Parts are Participants or Capabilities. Optional but recommended. Community level has no controlling entity; participant level shows how one participant is organized inside.
- **Collaboration (refinement)** and **CollaborationUse (refinement)** (each extends its UML concept): add a strictness flag. A strict use means each part bound to a role must be compatible with it.

### Capabilities

- **Capability** (extends Class): the ability to act and produce an outcome, independent of who provides it. Capabilities can depend on each other, realize Service Interfaces, be realized by Participants and type parts of participants.
- **Expose** (extends Dependency): a Service Interface exposes a Capability. Looser than realization.

### Service data

- **MessageType** (extends DataType, Class or Signal): pure data exchanged between parties. No operations, no behaviors, public attributes of primitive or message type, no header or protocol detail, no dependency on the location of either party.
- **Attachment** (extends Property): a part of a message carried alongside it, with its own encoding and media type.
- **Property (refinement)** (extends Property): adds an identifying flag, used for keys and correlation. Shown as `{isID=true}` or the keyword Id.

### Behavior markers

- **Milestone** (extends Comment): a progress marker in a behavior. An integer progress value and an optional signal. It adds no functional meaning.

### Categorization

An optional mechanism for organizing elements along several independent dimensions at once.

- **Catalog** (extends Package): holds categories and other catalogs, nothing else.
- **Category** (extends Artifact): a kind of information about elements. Must be in a catalog.
- **CategoryValue** (extends InstanceSpecification): a value of a category.
- **Categorization** (extends Dependency): links an element to a category or category value.
- Three placeholders for elements of the OMG Reusable Asset Specification: NodeDescriptor, FreeFormDescriptor, FreeFormValue.

### Business motivation link

- **MotivationElement** (placeholder): stands for an element of a business motivation model (vision, goal, objective, mission, strategy, tactic, policy, regulation).
- **MotivationRealization** (extends Realization): a behaviored classifier, usually a Service Contract, realizes a motivation element. The link is optional.

### Specialization

Agent specializes Participant. Category specializes NodeDescriptor, CategoryValue specializes FreeFormValue, Catalog specializes NoteDescriptor (named in the standard but not defined) and MotivationRealization specializes Realization. Nothing else specializes. The standard declares no concept abstract.

## Relationships

The standard introduces few relationship kinds of its own. Most relationships are UML relationships restricted to service meaning. In `language.yaml`: 36 relationships, each with its source and target, the UML mechanism and the section. In summary:

- **Ports.** A Participant offers any number of Services and makes any number of Requests. A Service or Request is typed by a Service Interface or an Interface.
- **Channels.** A Service Channel connects one Request and one Service.
- **Service interface.** It provides (realizes) and requires (uses) interfaces, has role parts typed by them, may own a protocol, and may own Service or Request ports when it is a compound service.
- **Contracts and architectures.** A Service Contract has roles typed by a Provider, a Consumer or a Service Interface, owns a choreography, may use nested contracts and may specialize another. A Services Architecture has roles typed by a Participant or a Capability and uses Service Contracts through role bindings. A classifier fulfills a contract or adheres to an architecture through a collaboration use.
- **Capabilities.** A Service Interface exposes a Capability; a Capability realizes a Service Interface; a Participant realizes a Capability or has a part typed by one; Capabilities use Capabilities.
- **Data.** A Message Type owns Attachments and aggregates other message or data types; service operation parameters are typed by Message Types (document style) or primitive or data types (RPC style).
- **Categorization.** A Catalog contains categories; any element can be categorized by a category or category value; a category value is classified by one category.
- **Motivation.** A behaviored classifier realizes a motivation element; a Service or Request may be linked to one.

## The rules that matter most

78 rules, in `references/rules.md`: 43 must, 5 should, 30 note. Keep these in front of you:

- A Participant does not realize or use an interface directly; only its Service and Request ports do. (SOAML-PART-002)
- The type of a Service and of a Request is a Service Interface or an Interface. A Request is conjugated. (SOAML-PORT-001, 003, 004)
- A Service Channel has a Request at one end and a Service at the other, and the two are compatible: same type, a specializing or realizing type, matching operations in both directions, or any of these for the part a port covers. (SOAML-CHAN-001 to 003)
- All parts of a Service Interface are typed by the interfaces it realizes or uses. (SOAML-SINT-001)
- A Service Contract has at least one Provider and one Consumer among its role types, and each role type uses the types of the roles it connects to. (SOAML-CONT-002, 003)
- A party with a port typed by a role's interface is bound by the contract, and a Service Interface that owns a behavior must comply with a contract it types a role for. State the protocol in one place, not both. (SOAML-CONT-005 to 007)
- The parts of a Services Architecture are Participants or Capabilities; each participant that fills a role has a port for each role binding, with a type compliant with the role. (SOAML-ARCH-001, 002)
- A Message Type has no operations, no behaviors, public attributes only, of primitive or message type, and aggregations only. A document-style service operation has at most one input, one output and one exception, all message types. (SOAML-MSG-001 to 006)
- An Expose goes from a Service Interface to a Capability. (SOAML-CAPA-001)
- A Catalog holds only categories, category values and catalogs; a Category is in a Catalog; a Categorization targets a Category or Category Value. (SOAML-CATG-001 to 004)

## Telling similar concepts apart

- **Service Interface or Service Contract.** A Service Interface defines a service from the provider's side and can stand alone. A Service Contract sits between the parties and defines every role; use it when the agreement comes first or more than two parties are involved. A Service Interface may fulfill a contract, usually one.
- **Service Interface or Interface.** A plain interface is a one-way list of operations. A Service Interface is a class that realizes and uses interfaces and can carry a protocol, so it describes two-way, conversational services.
- **Provider, Consumer, Service, Request.** Provider and Consumer type the roles in a contract. Service and Request are ports on a participant. A Service is where it offers; a Request is where it consumes. Typing a Request with the provider's interface does the same job as typing the port with the Consumer interface; for more than two parties the second works better.
- **Participant or role.** A role is the function in a context, played in a collaboration. A Participant is the type that fills it.
- **Expose or realize.** A Capability that realizes a Service Interface implements it as a specification. An Expose is looser: the interface provides access to or gives candidate services from a capability, without the same operations.
- **Services Architecture or Service Contract.** The architecture is the whole community or participant, showing how services connect participants. A contract defines one service. The architecture uses contracts.
- **Compound contract or composed implementation.** A compound contract is defined from nested contracts. A service implemented by calling other services is a participant concern, not a compound contract.
- **Participant or Agent.** An Agent has its own life cycle and changing needs and capabilities; a Participant's are static.
- **Capability or Service.** A Capability is the ability, independent of any provider. A Service is a port where a particular participant offers a service.
- **MessageType or plain data type.** A Message Type is a value object for exchange between parties: no operations, no identity, public attributes.

## A short example

Westbrook Bank, a fictitious bank, wants business customers to open an account in one business day. It does not run its own identity checks, so it uses an outside identity verifier.

The **Services Architecture** "Business Account Opening" has three participant roles: the business customer, Westbrook Bank's account opening, and an identity verifier. Two **Service Contracts** are used in it: "Application Submission" and "Identity Verification". In "Identity Verification" the role verifier is typed by the **Provider** interface IdentityChecker and the role requester by the **Consumer** interface IdentityRequester; IdentityRequester uses IdentityChecker, and IdentityChecker may use IdentityRequester to send the result back. Its **choreography** is an interaction: the requester sends a check request, the verifier replies with a result or a rejection.

The participant "Account Opening" is a **Participant**. It has a **Request** port "verifyIdentity" typed by the **Service Interface** "Identity Verification Service", and a **Service** port "submitApplication" for customers. The "Identity Verifier" participant has the matching **Service** port, typed by the same Service Interface. A **Service Channel** joins the two ports, which are compatible because they have the same type.

The **Service Interface** exposes the **Capability** "Customer Identity Verification", which the verifier participant realizes. The messages are **Message Types**: "VerificationRequest" and "VerificationResult", each with an identifying property "applicantId", and an **Attachment** "IdentityDocumentImage" to the request. The Identity Verification contract has a **Motivation Realization** to the goal "Open business accounts within one business day" from a business motivation model.

This is an illustration. Use your own services, participants and, if you take the optional categorization, your own catalogs.

## Data types and attributes

Coverage is partial. SoaML defines no primitive types or enumerations of its own. It adds the Message Type (pure data, public attributes of a primitive or message type) and the Attachment (a part of a message that travels beside it). Its few attributes use UML types: Boolean (`isStrict`, `connectorRequired`, `isID`), String (`encoding`, `mimeType`), Integer (`progress`), Signal and Expression. Each concept that has attributes lists them under `attributes` in `language.yaml`; every other concept adds none. See `data_types` there.

## How it is drawn

Coverage is normative, built on UML notation. A concept is drawn as the UML shape it extends, with its name as a keyword in guillemets above the name or with a small icon in the name compartment. Four shapes differ: a Service Contract and a Services Architecture are dashed ellipses with a dashed line under the name; a Service and a Request are small squares on a participant's border, with a ball (provided) or a socket (required) and a tilde before the type for a Request; a Milestone is a note symbol. Lines for Expose, Categorization, realizations and uses are dashed with the arrowheads UML gives them. See `notation` in `language.yaml`, which describes each shape in words. The icons of Participant, Capability, ServiceContract and ServicesArchitecture are tiny bitmaps in the standard, so their glyphs are described only roughly.

Sizes and spacing come from `../_languages/layout-standard.yaml`; the mapping of each concept to a size class is the `layout` block in `language.yaml`.

## References

- `references/standard.md`: the standard section by section, in our own words, with citations.
- `references/rules.md`: all 78 rules with stable ids (`SOAML-<CAT>-nnn`), strength, checkability and source section.
- `language.yaml`: the machine-readable form: 28 concepts, the UML concepts they extend, 36 relationships, the 78 rules and the informal views.
