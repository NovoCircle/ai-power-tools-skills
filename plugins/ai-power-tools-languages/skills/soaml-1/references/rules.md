# SoaML 1.0.1 rules

Generated from `language.yaml` (`constraints`). Do not edit by hand; change the language file and regenerate.

Each rule has a stable id of the form `SOAML-<CAT>-nnn`. The number never changes once assigned. A rule that is retired keeps its id and is marked withdrawn rather than reused.

## Strength

| Strength | Meaning |
|---|---|
| must | The standard states it as a requirement, a constraint or a "shall"-style necessity. A model that breaks it is not well formed. |
| should | The standard gives it as guidance ("should", "generally", "usually" with a recommendation). Breaking it is a warning, not an error. |
| note | The standard states it as an option, a method note, an expectation or a semantic variation point. It is recorded for completeness and is not checkable on its own. |

## Checkable

| Value | Meaning |
|---|---|
| static | A model alone can show a breach. |
| partial | A model alone shows only part of it, for example structure but not behavior. |
| runtime | It concerns how behavior unfolds; a model cannot show a breach, only review or analysis can. |
| none | It cannot be checked from a model. |

## Categories

| Category | Name | Covers | Rules |
|---|---|---|---|
| PART | Participants | What a participant may and may not do, and how it implements the services it provides. | 7 |
| PORT | Service and request ports | The typing and direction of the ports where services are offered and consumed. | 7 |
| CHAN | Service channels | What a channel connects and when a request and a service are compatible. | 6 |
| SINT | Service interfaces | How a service interface is built from realized and used interfaces, parts and protocol. | 8 |
| CONT | Service contracts | Role types, role dependencies, binding force and choreography of a service contract. | 12 |
| ARCH | Services architectures and collaboration use | What fills a role, how roles are bound, and when a binding is strict. | 9 |
| MSG | Message types and service data | What a message type may contain and how service operations are typed. | 12 |
| CAPA | Capabilities | Exposure and realization of capabilities and what each does not require. | 4 |
| CATG | Categorization | Catalogs, categories, category values and categorizations. | 6 |
| MOTV | Business motivation link | Realization of motivation elements and links from service and request ports. | 3 |
| BEHV | Behavior markers | Milestones. | 2 |
| CONF | Conformance and variation points | What conformance covers and what is left to modelers and tools. | 2 |

Totals: 78 rules: 43 must, 5 should, 30 note.

Section references are to the clauses and annexes of the SoaML 1.0.1 specification (formal/12-05-10); "p." gives the printed page. A bracketed number such as [1] is the number of the entry in the standard's own list of constraints for that concept. Multiplicities on individual relationships are in `language.yaml` and are not repeated here.

## PART: Participants

| Id | Strength | Rule | Applies when | Checkable | Section |
|---|---|---|---|---|---|
| SOAML-PART-001 | must | The active flag of an Agent is always true. |  | static | 6.4.1 (Constraints), p. 36 |
| SOAML-PART-002 | must | A Participant does not realize or use an Interface directly; it does so through its Service and Request ports. | applies to the participant itself, not to the inside of a component that implements it (PART-003) | static | 6.4.10 [1], p. 53 |
| SOAML-PART-003 | note | The inside of a component that implements a Participant is not bound by PART-002; its links to its container and to other implementation components need not use services. |  | none | 6.4.10 [2], p. 53 |
| SOAML-PART-004 | must | The implementation of a provided service is consistent with the operations, protocols and constraints of its Service Interface. |  | runtime | 6.4.10 (Semantics), p. 53 |
| SOAML-PART-005 | should | A Participant's own classifier behavior is limited to construction, not a long-running life cycle; an Agent's classifier behavior, if any, is its life cycle. |  | none | 6.4.1 (Semantics), p. 37 |
| SOAML-PART-006 | note | A Participant implements a provided service operation by a method (an owned behavior), by event handling, or by delegation to a part, another participant or a user. The standard does not constrain the choice and the means may be mixed. |  | none | 6.4.10 (Semantics), pp. 53-54 |
| SOAML-PART-007 | note | Behavioral compatibility for a realization of a Participant by another is a semantic variation point. |  | none | 6.4.10 (Semantic Variation Points), p. 54 |

## PORT: Service and request ports

| Id | Strength | Rule | Applies when | Checkable | Section |
|---|---|---|---|---|---|
| SOAML-PORT-001 | must | The type of a Service is a Service Interface or an Interface. |  | static | 6.4.18 [1], p. 78 |
| SOAML-PORT-002 | must | The direction of a Service is incoming. |  | none | 6.4.18 [2], p. 78 |
| SOAML-PORT-003 | must | The type of a Request is a Service Interface or an Interface. |  | static | 6.4.14 [1], p. 61 |
| SOAML-PORT-004 | must | A Request is conjugated: the provided and required interfaces of its type are inverted. |  | static | 6.4.14 [2], p. 61 |
| SOAML-PORT-005 | must | Where connectorRequired is true (the default), every instance of the port has at least one connector or Service Channel attached. Where it is false, the owning classifier can work without one. | connectorRequired is true | partial | 6.4.11 (Semantics), p. 56 |
| SOAML-PORT-006 | note | The provided and required interfaces of a Service or Request are derived from its type. For a Service Interface type: provided are the interfaces it realizes, required are the interfaces it uses, and a Request swaps the two. For a plain Interface type: a Service provides it and requires nothing; a Request requires it. |  | static | 6.4.14 and 6.4.18 (Semantics), pp. 61-62, 77 |
| SOAML-PORT-007 | note | The service flag of a port (a convention of UML) distinguishes client-facing ports from ports used only to implement the participant; all such ports are Service or Request ports. |  | none | 6.4.11 (Semantics), p. 56 |

## CHAN: Service channels

| Id | Strength | Rule | Applies when | Checkable | Section |
|---|---|---|---|---|---|
| SOAML-CHAN-001 | must | One end of a Service Channel is a Request and the other a Service, in an architecture. |  | static | 6.4.15 [1], p. 63 |
| SOAML-CHAN-002 | must | The Request and the Service connected by a Service Channel are compatible. |  | partial | 6.4.15 [2], p. 63 |
| SOAML-CHAN-003 | must | A Request and a Service are compatible only if at least one holds: (1) they have the same type, an Interface or a Service Interface; (2) the type of the Service specializes or realizes the type of the Request; (3) the Service provides an operation for every operation used through the Request, the Request provides one for every operation used through the Service, and their protocols fit; (4) any of these holds for the subset of a Service Interface defined by a port on it. |  | partial | 6.4.15 (Semantics), p. 64 |
| SOAML-CHAN-004 | must | The contract behavior of a Service Channel is compatible with the protocols specified for the connected Requests and Services. |  | runtime | 6.4.15 [3], p. 63 |
| SOAML-CHAN-005 | note | Behavioral compatibility between Requests and Services is a semantic variation point. Compatibility does not require the same type or a common contract; the standard keeps coupling loose on purpose. |  | none | 6.4.15 (Semantics, Semantic Variation Points), pp. 63-64 |
| SOAML-CHAN-006 | must | Where a Service Interface has more than two parts, the combination of all the channels through a service port is compatible with the port's protocol, not each channel on its own. | the Service Interface has more than two parts | runtime | 6.4.17.1 (Examples, Figures 6.50 to 6.52), pp. 74-75 |

## SINT: Service interfaces

| Id | Strength | Rule | Applies when | Checkable | Section |
|---|---|---|---|---|---|
| SOAML-SINT-001 | must | All parts of a Service Interface are typed by the Interfaces the Service Interface realizes or uses. |  | static | 6.4.17 [1], p. 71 |
| SOAML-SINT-002 | must | The interface of the provider is the type of one of the parts of the Service Interface and is realized by it; the interface of the consumer, if there is one, is used by it. |  | static | 6.2.1, p. 13 |
| SOAML-SINT-003 | note | Provided interfaces are designated by realization and required interfaces by usage. Typically one of each, not always. |  | static | 6.2.1, p. 12; 6.4.17, p. 73 |
| SOAML-SINT-004 | note | A Service Interface can realize any number of Interfaces; some platform-specific models may restrict that to at most one. |  | none | 6.4.17 (Semantics), p. 73 |
| SOAML-SINT-005 | note | A Service Interface may own behaviors of any UML behavior kind (its protocol) and constraints stating what successful use of the service accomplishes. |  | none | 6.2.1, p. 12; 6.4.17 (Semantics), p. 73 |
| SOAML-SINT-006 | note | When the constraints of a Service Interface are evaluated, and how its behaviors are checked against participants' behaviors, are semantic variation points. |  | none | 6.4.17.1, p. 73 |
| SOAML-SINT-007 | note | A Service Interface may own Service or Request ports; together they make up a larger composite service between the same parties, and a participant may connect the whole service or any one sub-service. |  | none | 6.4.17, p. 71; 6.4.16, p. 70 |
| SOAML-SINT-008 | should | A Service Interface is a class that realizes and uses interfaces; it is not itself an interface. |  | static | 6.4.17 (Extends Metaclass), p. 70; 6.2.1, p. 12 |

## CONT: Service contracts

| Id | Strength | Rule | Applies when | Checkable | Section |
|---|---|---|---|---|---|
| SOAML-CONT-001 | must | Each role in a Service Contract has a type that is a Service Interface, or an Interface or Class marked as a Provider or a Consumer. |  | static | 6.4.16 (Description), p. 65; (Semantics), p. 67 |
| SOAML-CONT-002 | must | A Service Contract has at least one Provider and at least one Consumer among its role types. | the role types are Interfaces or Classes marked as Provider or Consumer | static | 6.4.16 (Semantics), p. 67 |
| SOAML-CONT-003 | must | The type of each role in a Service Contract has a uses dependency on the type of every role it is connected to. |  | static | 6.4.16 [5], p. 67 |
| SOAML-CONT-004 | must | A specialized Service Contract complies with the more general one; it may restrict the behavior or the operations used. |  | runtime | 6.4.16 (Description), p. 65 |
| SOAML-CONT-005 | must | A party that plays a role in a Service Contract, including a participant with a port typed by a role type, is bound by the contract: its interfaces, exchange patterns, behavior and message formats. The Provider and Consumer interfaces are bound by the constraints and behavior of their contract. |  | runtime | 6.4.16 (Description, Semantics), pp. 65, 67; 6.4.4 and 6.4.13 (Constraints), pp. 41, 59 |
| SOAML-CONT-006 | must | Where a Service Interface owns a behavior and is also used as a type in a Service Contract, the Service Interface's behavior complies with the contract. |  | runtime | 6.4.16 (Semantics), p. 67 |
| SOAML-CONT-007 | should | Specify the protocol in the Service Contract or in the Service Interface, not in both. |  | none | 6.4.16 (Semantics), p. 67 |
| SOAML-CONT-008 | note | A Service Interface may fulfill zero or more Service Contracts; usually it fulfills one. |  | none | 6.4.16 (Examples), p. 67 |
| SOAML-CONT-009 | note | A Service Contract may have any number of roles, usually two. It may own a behavior (the choreography) of any UML behavior kind; the choreography is not required. |  | none | 6.4.16, pp. 65, 68 |
| SOAML-CONT-010 | note | A Service Contract that uses nested Service Contracts is a compound contract; nesting may go to any level. A compound contract is not the same as a service implemented by calling other services. |  | none | 6.4.16, pp. 65, 69 |
| SOAML-CONT-011 | note | A Collaboration Use is not required for a Service Contract when the types are compatible; the contract binds the types of its roles. |  | none | 6.4.5, p. 42; 6.4.6, p. 43; 6.4.16, p. 65 |
| SOAML-CONT-012 | note | For a Service Contract with more than two parties, typing the consumer's port with the provider's interface and marking it a Request works less well than typing each port with its own role's interface. |  | none | 6.2.4.2, p. 23 |

## ARCH: Services architectures and collaboration use

| Id | Strength | Rule | Applies when | Checkable | Section |
|---|---|---|---|---|---|
| SOAML-ARCH-001 | must | The parts of a Services Architecture are typed by a Participant or a Capability. |  | static | 6.4.19 [1], p. 81 |
| SOAML-ARCH-002 | must | Each participant that fills a role in a Services Architecture has a port for each role binding attached to it, and the type of that port is compliant with the type of the role in the Service Contract. |  | partial | 6.4.19 [1], p. 81; 6.2.3, p. 19 |
| SOAML-ARCH-003 | must | Each use of a service in a Services Architecture is represented by a Service Contract bound to the roles of participants. |  | static | 6.4.19 (Description), p. 80 |
| SOAML-ARCH-004 | must | A Collaboration Use binds each role of its Collaboration to a part of the owning classifier. |  | static | 6.4.6 (Semantics), p. 44 |
| SOAML-ARCH-005 | must | When a Collaboration Use is strict, each part is compatible with the role it is bound to: the same type; a type that specializes the role type; a type that realizes it; or a type that has at least the owned attributes and operations of the role type. The owning classifier's behaviors are also compatible with the Collaboration's owned behavior. | isStrict is true (the default) | partial | 6.4.6, pp. 43-44; 6.4.16 [1]-[4], pp. 66-67 |
| SOAML-ARCH-006 | note | The strictness of a Collaboration sets the default for each Collaboration Use typed by it. A non-strict use means the modeler warrants that the part can play the role even though the types are not compatible. |  | static | 6.4.5 and 6.4.6, pp. 42-43 |
| SOAML-ARCH-007 | must | A participant that realizes a Services Architecture adheres to the architecture it specifies. |  | runtime | 6.2.2, p. 15 |
| SOAML-ARCH-008 | note | Using a Services Architecture is optional but recommended. A community-level architecture assumes no controlling entity; a participant-level architecture usually has a business process, whose swim lanes correspond to the participant roles. |  | none | 6.4.19 (Description), p. 80; 6.2.2, p. 16 |
| SOAML-ARCH-009 | note | Compliance between the types named as roles in a collaboration use is a semantic variation point, determined by modelers or tools. |  | none | 6.4.6 (Semantic Variation Points), p. 44 |

## MSG: Message types and service data

| Id | Strength | Rule | Applies when | Checkable | Section |
|---|---|---|---|---|---|
| SOAML-MSG-001 | must | A Message Type has no owned operations. |  | static | 6.4.8 [1], p. 48 |
| SOAML-MSG-002 | must | A Message Type has no owned behaviors. |  | static | 6.4.8 [2], p. 48 |
| SOAML-MSG-003 | must | All owned attributes of a Message Type are public. |  | static | 6.4.8 [3], p. 48 |
| SOAML-MSG-004 | must | The owned attributes of a Message Type are of a primitive type or of a Message Type. |  | static | 6.4.2 (Semantics), p. 38 |
| SOAML-MSG-005 | must | Associations between a Message Type and other message or data types are aggregations. |  | static | 6.4.8 (Examples), p. 49 |
| SOAML-MSG-006 | must | A document-style service operation has at most one in, one out and one exception parameter (an out parameter marked as an exception), and every parameter is typed by a Message Type. | the operation is document style | static | 6.4.8 (Semantics), p. 48 |
| SOAML-MSG-007 | must | An RPC-style service operation may have any number of in, inout and out parameters and a return value; the type of each is a primitive type or a data type. | the operation is RPC style | static | 6.4.8 (Semantics), pp. 48-49 |
| SOAML-MSG-008 | must | Service operations use call by value: parameters are value objects or data transfer objects, and no service operation assumes anything about the identity or location of a parameter. |  | none | 6.4.8 (Semantics), p. 49 |
| SOAML-MSG-009 | must | A Message Type holds domain or service content only: no header or protocol-specific information, and no dependency on the environment, location or information system of either party. |  | none | 6.4.8 (Description), pp. 47-48 |
| SOAML-MSG-010 | should | A Message Type is generally applied to a data type; it may be applied to a class, whose identity is then ignored, because existing models often do not tell the two apart. |  | static | 6.4.8 (Description, Note), p. 48 |
| SOAML-MSG-011 | note | An Attachment marks a part of a message that is attached rather than embedded; it may carry an encoding and a media type of its own. |  | none | 6.4.2, pp. 38-39 |
| SOAML-MSG-012 | note | An identifying property helps distinguish instances of its classifier and correlate messages in long-running exchanges. A classifier may have several, and compound identifiers use a class or data type with the flag set. |  | none | 6.4.12, p. 58; 6.4.8, p. 48 |

## CAPA: Capabilities

| Id | Strength | Rule | Applies when | Checkable | Section |
|---|---|---|---|---|---|
| SOAML-CAPA-001 | must | The source of an Expose is a Service Interface and its target is the exposed Capability. |  | static | 6.4.7 (Description), p. 46 |
| SOAML-CAPA-002 | note | Expose is not realization. Neither an Expose nor a Capability's realization of a Service Interface requires the two sides to have the same operations or properties. |  | none | 6.4.7 (Semantics), p. 47 |
| SOAML-CAPA-003 | note | Capabilities may have usage dependencies on each other, be organized into packages and layers, own behaviors that are the methods of their operations, and type parts of participants. |  | none | 6.4.3, p. 40; 6.2.5, p. 29 |
| SOAML-CAPA-004 | should | A participant that provides a service has a capability to provide it; different providers may have different capabilities for the same service. |  | none | 6.1.3, p. 8 |

## CATG: Categorization

| Id | Strength | Rule | Applies when | Checkable | Section |
|---|---|---|---|---|---|
| SOAML-CATG-001 | must | A Catalog contains only Categories, Category Values or other Catalogs. |  | static | 7.3.1 [1], p. 84 |
| SOAML-CATG-002 | must | The target of a Categorization is a Category or a Category Value. |  | static | 7.3.2 [1], p. 85 |
| SOAML-CATG-003 | must | A Category is contained in a Catalog. |  | static | 7.3.3 [1], p. 86 |
| SOAML-CATG-004 | must | The classifier of a Category Value is a Category. |  | static | 7.3.4 [1], p. 88 |
| SOAML-CATG-005 | note | Categorization is optional under the profile compliance point. The meaning of being in a Category is left to the modeler, and one element may be categorized in many ways. |  | none | 2, p. 2; 7.3.1 (Semantics), p. 84 |
| SOAML-CATG-006 | note | The properties of a Category are owned by that Category and cannot be reused by another Category, unlike free-form descriptors in the reusable asset specification. |  | none | 7.3.5, p. 89 |

## MOTV: Business motivation link

| Id | Strength | Rule | Applies when | Checkable | Section |
|---|---|---|---|---|---|
| SOAML-MOTV-001 | must | A Motivation Realization is a realization from a behaviored classifier (a Service Contract is the example) to a business motivation element. |  | static | 8.3.2, p. 92; 6.2.6, p. 32 |
| SOAML-MOTV-002 | note | The link to the business motivation model is optional and assumes the motivation model is available as a profile or as a package that can be merged. |  | none | 8.1, p. 91 |
| SOAML-MOTV-003 | note | A Service or a Request may be connected to a business motivation element to show its intended value proposition or goals, and may carry constraints stating qualities of service. |  | none | 6.4.18, p. 77; 6.4.14, p. 61 |

## BEHV: Behavior markers

| Id | Strength | Rule | Applies when | Checkable | Section |
|---|---|---|---|---|---|
| SOAML-BEHV-001 | must | A Milestone has an integer progress value. |  | static | 6.4.9 (Attributes), p. 51 |
| SOAML-BEHV-002 | note | A Milestone adds nothing to the functional meaning of a behavior; implementations may ignore it. |  | none | 6.4.9, pp. 51-52 |

## CONF: Conformance and variation points

| Id | Strength | Rule | Applies when | Checkable | Section |
|---|---|---|---|---|---|
| SOAML-CONF-001 | note | Compliance means UML at the L3 compliance level plus the extensions, as a profile or as a metamodel merged into UML. Three compliance points exist: P1 the profile, P2 the basic metamodel, P3 the metamodel with the business motivation link. The categorization package is optional in P1. |  | none | 2, pp. 1-3 |
| SOAML-CONF-002 | note | The standard leaves these to modelers and tools as semantic variation points: compliance between collaboration role types; behavioral compatibility of component realizations and of Requests with Services; when a Service Interface's constraints are evaluated and how its behaviors are checked. |  | none | 6.4.6, 6.4.10, 6.4.15, 6.4.17.1 |
