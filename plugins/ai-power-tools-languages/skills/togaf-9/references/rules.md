# TOGAF 9.1 rules

Generated from `language.yaml` (`constraints`). Do not edit by hand; change the language file and regenerate.

Each rule has a stable id of the form `TOGAF-<CAT>-nnn`. The number never changes once assigned. A rule that is retired keeps its id and is marked withdrawn rather than reused.

TOGAF 9.1 is a framework with an informal content metamodel. It states almost no requirements: the single `must` below is the one place the text obliges the architect. Everything else is guidance, a typical minimum, or a description, so most rules are `should` (a warning) or `note` (advice in the skill, not a check).

## Strength

| Strength | Meaning | Rules |
|---|---|---|
| must | The standard states it as an obligation. A model that breaks it is not well formed. | 1 |
| should | The standard gives it as guidance ("should"), a typical minimum, or a possible-relationships list that is open to tailoring. Breaking it is a warning, not an error. | 27 |
| note | The standard describes it, states an expectation or gives an option. Recorded for completeness; not checkable on its own. | 21 |

## Checkable

| Value | Meaning |
|---|---|
| static | Decidable from the model content alone. |
| partial | Some of it is decidable from the model; the rest needs a person or extra input. |
| runtime | Needs information that is not in the model (for example which extension modules the engagement chose). |
| none | Not checkable; guidance for the person modeling. |

## Categories

| Category | Name | Covers | Rules |
|---|---|---|---|
| REL | Relationship use | Which entities may be linked, by which named relationship, and in which extension module. | 2 |
| DEF | Definition and use of entities | What an entity is for and how it is meant to be used, so that an element is placed correctly. | 11 |
| EXT | Extension modules | How the optional modules are selected and what each one changes. | 9 |
| ATTR | Attributes and values | The typical attributes and the value sets the standard names. | 8 |
| ART | Artifacts | What catalogs, matrices and diagrams contain and the paths a matrix relationship is read through. | 8 |
| VIEW | Views, viewpoints and architecture description | The concepts of stakeholder, concern, viewpoint and view, and the responsibilities that come with them. | 5 |
| BB | Building blocks | What a building block is and the minimum a specification holds. | 6 |

Section references are to the chapters and sections of TOGAF Version 9.1, Part IV (chapters 33 to 37). "Figure" means a figure in the online edition. The relationship table is 34.7 and is in `language.yaml` (`relationships`); it is not repeated here.

## REL: Relationship use

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| TOGAF-REL-001 | should | A relationship between two entities should be one the content metamodel lists for that source entity, target entity and relationship name. The list is the table in 34.7. The standard presents the metamodel as the possible relationships and invites tailoring, so a link outside the table is a warning, not an error. | 33.2; 34.2.1; 34.7 | static |
| TOGAF-REL-002 | should | A relationship the table assigns to an extension module is available only when that module is part of the engagement. Relationships labeled Core are always available. Applies when: the engagement has chosen its extension modules. | 34.4; 34.7 | partial |

## DEF: Definition and use of entities

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| TOGAF-DEF-001 | should | A Process describes flow of control. It is not itself deployed. An application component implements the Function (through the services that bound it) that a process supports; an application does not implement a process. Applies when: a model links an application or technology component directly to a Process. | 34.2.1 | partial |
| TOGAF-DEF-002 | should | Function is the single entity for a bounded unit of business capability at any granularity (value chain, process area, capability, business function). Such units should be modeled as Functions. | 34.2.1 | none |
| TOGAF-DEF-003 | should | A Business Service is explicitly governed by an organization and has an explicitly defined interface. It should be owned and governed by an Organization Unit, and be defined at a granularity that matches the governance applied to it. | 34.2.1; 34.5 | partial |
| TOGAF-DEF-004 | should | A Business Service operates as the boundary of one or more Functions. | 34.2.1 | partial |
| TOGAF-DEF-005 | note | A Business Service that is supported by IT is deployed onto application components, and an application component is implemented on a suite of technology components. | 34.2.1 | none |
| TOGAF-DEF-006 | note | A Business Service supported by several application components is possible but problematic for governance. It is a sign that the service is too coarse or the components too fine. | 34.2.1 | partial |
| TOGAF-DEF-007 | note | A service in the service-oriented-architecture sense (a deployable unit of application functionality) corresponds to an application service, application component or technology component that implements or supports a Business Service, not to a Business Service. | 34.2.1 | none |
| TOGAF-DEF-008 | should | A Principle has at least a supporting rationale and a measure of importance (priority). | 34.5; 34.6 | static |
| TOGAF-DEF-009 | should | A Requirement states whether it shall be met, should be met or may be met. | 34.6 (Requirement entry) | partial |
| TOGAF-DEF-010 | note | Requirements should be specific and measurable (SMART). Concerns and requirements are different things: a concern is an area of interest and is decomposed into requirements. | 35.1 | none |
| TOGAF-DEF-011 | note | An Objective is a time-bounded milestone toward a Goal. | 34.5; 34.4.6 | partial |

## EXT: Extension modules

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| TOGAF-EXT-001 | note | The core metamodel is the minimum content for traceability. Extension modules are optional and are chosen to meet the needs of the engagement; the grouping of entities into modules is a suggestion that the architects may tailor. | 34.2.1; 34.4 | static |
| TOGAF-EXT-002 | should | The extension modules to use should be selected when the engagement is scoped: the Preliminary Phase in 34.2.1, the Architecture Vision phase in 34.4. The standard names both. | 34.2.1; 34.4 | runtime |
| TOGAF-EXT-003 | should | An entity, relationship or artifact that belongs to an extension module should appear in a model only when that module has been selected. Core content is always available. Applies when: the engagement has chosen its extension modules. | 34.2.1; 34.4; Figures 34-7, 35-3 | partial |
| TOGAF-EXT-004 | note | Governance extension: Measure, Service Quality and Contract are added. A Measure links an Objective to a Business Service. A Service Quality is a reusable service-level profile applied to a Business Service or a Contract. A Contract formalizes a service interaction. | 34.4.1 | static |
| TOGAF-EXT-005 | should | Services extension: Information System Service is a kind of Business Service. It inherits every relationship a Business Service has, and one new relationship links it to a Business Service. Applies when: the Services extension is selected. | 34.4.2; Figure 34-12 | static |
| TOGAF-EXT-006 | note | Process Modeling extension: Event sits between Actor, Process and Service; Control relates to a Process; Product links Organization Unit and Process. | 34.4.3 | static |
| TOGAF-EXT-007 | should | Data extension: a Logical Data Component encapsulates Data Entities and a Physical Data Component extends it. A Physical Data Component is related to an Application Component. When the Infrastructure Consolidation extension is also used, that component is a Physical Application Component, and the Physical Data Component is also related to a Location. Applies when: the Data extension is selected. | 34.4.4; 34.4.5 | partial |
| TOGAF-EXT-008 | should | Infrastructure Consolidation extension: location becomes an entity. The location attribute on Organization, Actor, Application Component, Data Component and Technology Component is removed and replaced by a relationship to a Location. Application and Technology Components each gain a logical and a physical kind. Applies when: the Infrastructure Consolidation extension is selected. | 34.4.5 | partial |
| TOGAF-EXT-009 | note | Motivation extension: Driver, Goal and Objective are added and link an Organization Unit to a Business Service. Drivers motivate Organization Units and create Goals; Goals are realized through Objectives. | 34.4.6 | static |

## ATTR: Attributes and values

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| TOGAF-ATTR-001 | note | The attributes in 34.6 are typical, not mandatory. Every entity typically carries ID, Name and Description, and optionally Category, Source and Owner. Beyond these, the standard lists further typical attributes for particular entities. | 34.6 | static |
| TOGAF-ATTR-002 | should | Standards class takes one of six values: Non-Standard, Proposed Standard, Provisional Standard, Standard, Phasing-Out Standard, Retired Standard. It is typical for Business Service, Function, Process, Service, Application Component, Information System Service, Logical and Physical Application Component, Logical and Physical Data Component, Logical and Physical Technology Component, Platform Service and Technology Component. | 34.6 | static |
| TOGAF-ATTR-003 | should | Lifecycle status of a Physical Application Component takes one of five values: Proposed, In Development, Live, Phasing Out, Retired. | 34.6 (Physical Application Component entry) | static |
| TOGAF-ATTR-004 | should | Principle category takes one of six values: Guiding, Business, Data, Application, Integration, Technology. | 34.6 (Principle entry) | static |
| TOGAF-ATTR-005 | should | Data Entity category takes one of two values: Message, Internally Stored Entity. | 34.6 (Data Entity entry) | static |
| TOGAF-ATTR-006 | should | Work Package category takes one of five values: Work Package, Work Stream, Project, Program, Portfolio. | 34.6 (Work Package entry) | static |
| TOGAF-ATTR-007 | note | Location category is Region, Country, Building or Specific Location. The nature of the business may introduce other kinds of location, so the set is open. | 34.6 (Location entry) | static |
| TOGAF-ATTR-008 | note | The category of a Logical Technology Component, Physical Technology Component and Platform Service comes from the TOGAF Technical Reference Model, which may be extended. | 34.6 | none |

## ART: Artifacts

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| TOGAF-ART-001 | should | A catalog lists only building blocks of the entity types the standard assigns to that catalog. A matrix relates the entity types the standard names for its axes. See each artifact in language.yaml. | 35.6 | partial |
| TOGAF-ART-002 | should | The relationship behind the Application/Organization matrix is a composite and needs validating: Organization Units own Services; Actors belonging to those Organization Units use Services; Services are realized by Logical or Physical Application Components. A cell is supported only if that path exists. | 35.6.5 (Application/Organization Matrix) | partial |
| TOGAF-ART-003 | should | The relationship behind the Role/Application matrix is a composite and needs validating: a Role accesses a Function; the Function is bounded by a Service; the Service is realized by a Logical or Physical Application Component. | 35.6.5 (Role/Application Matrix) | partial |
| TOGAF-ART-004 | should | The relationship behind the Application/Function matrix is a composite and needs validating: a Function is bounded by a Service; the Service is realized by a Logical or Physical Application Component. | 35.6.5 (Application/Function Matrix) | partial |
| TOGAF-ART-005 | note | A deliverable may contain many artifacts and artifacts form the content of the repository. The Architecture Definition Document is the container for the core artifacts across business, data, application and technology, for each state (baseline, transition, target). | 33.1; 36.2.3 | none |
| TOGAF-ART-006 | note | Each artifact is recommended for production in the ADM phase 35.6 lists it under. The standard says the artifacts "may be created" there; the phase is a recommendation, not a requirement. | 35.6 | none |
| TOGAF-ART-007 | note | The Stakeholder Map matrix uses no specific metamodel entities, because stakeholder mapping is sensitive and the Architecture Vision phase is informal. | 35.6.2 (Stakeholder Map Matrix) | none |
| TOGAF-ART-008 | note | Catalogs, matrices and diagrams can also be generated on demand by querying the repository. Such ad hoc artifacts are not restricted or defined by the content metamodel. | 34.2.1 | none |

## VIEW: Views, viewpoints and architecture description

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| TOGAF-VIEW-001 | note | Every view has an associated viewpoint, at least implicitly. A viewpoint is generic and re-usable; a view is specific to the architecture it was made for. | 35.1 | none |
| TOGAF-VIEW-002 | should | A viewpoint defines how to construct and use a view, the information that appears in it, the modeling techniques for expressing and analyzing that information, and the rationale (purpose and audience). | 35.1 | partial |
| TOGAF-VIEW-003 | should | An architecture description identifies at least one stakeholder and at least one concern, selects at least one viewpoint, is organized by at least one view and aggregates at least one model. Each stakeholder has at least one concern. A view conforms to a viewpoint. | Figure 35-1; 35.1 | partial |
| TOGAF-VIEW-004 | must | The architect must develop pertinent views of both the Baseline Architecture and the Target Architecture, which gives the context for gap analysis at the end of Phases B, C and D. | 35.2.1 | none |
| TOGAF-VIEW-005 | note | The architect is responsible for completeness (all pertinent stakeholder concerns addressed) and integrity (the views connected, conflicting concerns reconciled, trade-offs shown), within the limit of fitness for purpose. | 35.2.1 | none |

## BB: Building blocks

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| TOGAF-BB-001 | should | A building block has a type that corresponds to a content metamodel entity, a defined boundary generally recognizable as a thing by domain experts, and may interoperate with other building blocks. | 37.2.2 | partial |
| TOGAF-BB-002 | note | A building block specification should be loosely coupled to its implementation, so it can be realized several ways without changing its boundary or specification. | 37.2.2 | none |
| TOGAF-BB-003 | note | An architecture need only contain the building blocks relevant to the business problem it addresses. | 37.3.1.1 | none |
| TOGAF-BB-004 | should | An Architecture Building Block specification includes at least: fundamental functionality and attributes (including security capability and manageability); interfaces (chosen set, supplied); interoperability and relationship with other building blocks; dependent building blocks with required functionality and named interfaces; a map to business and organizational entities and policies. | 37.2.3.2 | none |
| TOGAF-BB-005 | should | A Solution Building Block specification includes at least: specific functionality and attributes; interfaces (the implemented set); required building blocks and the interfaces used; a mapping to the IT topology and operational policies; shared attributes such as security, manageability, localizability and scalability; performance and configurability; design drivers and constraints, including the physical architecture; the relationships between solution and architecture building blocks. | 37.2.4.2 | none |
| TOGAF-BB-006 | note | Architecture Building Blocks capture architecture requirements and direct and guide the development of Solution Building Blocks. | 37.2.3.1 | none |
