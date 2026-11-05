# TOGAF 9.1 content framework and content metamodel, section by section

This is a summary of Part IV of The Open Group's TOGAF Version 9.1 in our own words. It is not a substitute for the standard and it does not reproduce its text; the few short quoted phrases are cited. Chapter and section numbers are the standard's. Where the standard is silent or inconsistent, this file says so rather than filling the gap.

Source: The Open Group, *TOGAF Version 9.1*, December 2011 (document G116), Part IV: Architecture Content Framework, chapters 33 to 37, and the Enterprise Continuum chapter (39) for context. Read from archived copies of the online edition at `pubs.opengroup.org/architecture/togaf91-doc/arch/`.

## 1. What the standard is

TOGAF is a framework and a body of guidance for enterprise architecture, published as an Open Group Standard. Part IV is the part that says what an architecture should contain once the Architecture Development Method (ADM) has run. It is a companion to the ADM: the ADM describes the work, Part IV describes the result (33.3).

TOGAF 9.1 is **not a modeling-language standard.** It prescribes no notation, no symbols and no diagram syntax. What it does define is:

- a vocabulary of work products (deliverables, artifacts, building blocks), 33.1;
- a **content metamodel**: the types of building block an architecture may hold, typical attributes for each, and the relationships possible between them, 34;
- a set of **catalogs, matrices and diagrams**, named and described, that present that content to stakeholders, 35.6;
- a stakeholder-and-view vocabulary taken from ISO/IEC 42010:2007, with eight recommended views, 35.1 and 35.7;
- descriptions of the deliverables the ADM consumes and produces, 36;
- the idea of building blocks, 37.

The metamodel is informal: prose definitions, a table of attributes, a table of relationships and figures. The standard presents it as a structure for organizations that "implement their architecture within an architecture tool" (34.1) and expects it to be tailored.

## 2. Work products (33.1)

- **Deliverable.** A contractually specified work product that stakeholders formally review, agree and sign off. Deliverables are the output of projects; those in document form are archived at the end of a project or moved to the Architecture Repository.
- **Artifact.** An architectural work product that describes an aspect of the architecture. Artifacts are generally **catalogs** (lists of things), **matrices** (relationships between things) or **diagrams** (pictures of things). A deliverable may hold many artifacts; artifacts form the content of the repository. Example: the Architecture Definition Document is a deliverable that holds artifacts such as a process flow diagram (36.2.3).
- **Building block.** A potentially re-usable component of business, IT or architectural capability. **Architecture building blocks** describe required capability and shape the specification of solution building blocks. **Solution building blocks** are the components that implement the capability. A building block may start as a name and an outline and later be decomposed and fully specified.

An artifact is a view of building blocks: a process flow diagram (an artifact) may describe a target call handling process (a building block) and also the actors in it (33.1).

## 3. The content metamodel (34)

### 3.1 Aim

The content metamodel defines the entities that let architectural concepts be captured, stored, filtered, queried and shown in a way that supports consistency, completeness and traceability (34.2.2). Most stakeholders do not need to know the metamodel; they ask questions such as which functionality an application supports. Catalogs, matrices and diagrams answer them (34.2.1).

### 3.2 Core and extensions (34.2.1, 34.4)

The **core** metamodel is the minimum set of content that supports traceability across artifacts. Optional **extension modules** add more specific or deeper content. The standard names six. All are optional, chosen to suit the engagement; the grouping is a suggestion and architects may tailor it. When the choice is made differs between sections: 34.2.1 says the Preliminary Phase, 34.4 says the Architecture Vision phase.

Figure 34-4 organizes the whole metamodel by ADM phase: principles, requirements and roadmap; business architecture; information systems architecture (data and application); technology architecture; and architecture realization.

### 3.3 The core entities and what holds them together

The standard's own explanation of the core (34.2.1) rests on a few ideas:

- **Process describes flow.** A process is a flow of interactions between functions and services and cannot be physically deployed. Every process describes the flow of execution of a function. An application implements a function that has a process, not a process.
- **Function describes units of business capability at all levels of granularity.** The word covers value chain, process area, capability and business function; any bounded unit of business capability is a function.
- **Business services support organizational objectives and are defined at a granularity that suits the governance needed.** A business service is the boundary of one or more functions. A service in the SOA sense (a deployable unit of application functionality) is closer to an application service, application component or technology component.
- **Business services are deployed onto application components.** An IT-supported business service is deployed onto application components, which decompose hierarchically. Several components supporting one service is possible but problematic for governance, and signals a too-coarse service or too-fine components.
- **Application components are deployed onto technology components.** An application is typically implemented on several technology components (hardware, application server software, application services).

Figures 34-2 and 34-6 draw the core: an organization unit at the top contains actors, owns functions and owns and governs business services; actors take roles and take part in processes; functions are bounded by services; processes orchestrate and decompose functions and services; services use data entities and are realized through application components, which are implemented on technology components, which are supplied by platform services. Principle, Constraint, Assumption, Requirement, Gap and Work Package are associated with all other entities, and Capability is delivered by work packages.

### 3.4 Catalogs, matrices and diagrams (34.2.1)

The metamodel is a technique for ordering architectural information; stakeholders see it through three kinds of artifact. **Catalogs** carry metadata from the metamodel, which supports query and analysis. **Matrices** show relationships between two or more entities, and suit list-style relationships that are hard to draw (the example is a create-read-update-delete grid of applications against data). **Diagrams** render content graphically and can also be used to populate content or to check completeness; each can be made several times in different styles for different concerns. Ad hoc catalogs, matrices and diagrams produced by querying the repository are not restricted or defined by the metamodel.

### 3.5 The six extension modules (34.4)

| Module | Purpose in the standard's words, summarized | Entities added | Artifacts added |
|---|---|---|---|
| Governance | More structured data on objectives and business services, for operational governance: measures tied to objectives and services, contracts on service interactions, reusable service-quality profiles. | Measure, Service Quality, Contract | Contract/Measure Catalog; Enterprise Manageability Diagram |
| Services | A more refined service portfolio by adding information system services beside business services, so business and technical stakeholders can each describe services their own way. | Information System Service (a kind of business service) | Business Use-Case Diagram; Organization Decomposition Diagram |
| Process Modeling | Detailed process flow: events as triggers, controls as decision and governance steps, products as outputs. Typically enterprise architecture does not go this deep. | Event, Control, Product | Process/Event/Control/Product Catalog; Process Flow Diagram; Event Diagram |
| Data | Logical and physical encapsulations of data entities into units that can be governed and deployed. | Logical Data Component, Physical Data Component | Data Security, Data Migration and Data Lifecycle Diagrams |
| Infrastructure Consolidation | For fragmented application and technology portfolios being consolidated: location becomes an entity, and application and technology components split into logical (a class) and physical (an actual item) kinds. | Location, and the logical and physical application and technology components | Location Catalog; seven diagrams (Process/Application Realization, Software Engineering, Application Migration, Software Distribution, Processing, Networked Computing/Hardware, Communications Engineering) |
| Motivation | Drivers, goals and objectives that motivate the organization to provide business services, so service contracts and performance measurement can be defined better. | Driver, Goal, Objective | Driver/Goal/Objective Catalog; Goal/Objective/Service Diagram |

Each module's section also says when to use it and points to a related external standard (for example COBIT and ITPMF for governance, BPMN and SPEM for process, BMM for motivation, UML and SysML for infrastructure consolidation). Figure 34-7 shows which entity belongs to which module. In that figure Logical Application Component and Physical Technology Component are core and Physical Application Component and Logical Technology Component are extension entities; the text of 34.4.5 puts all four in the extension.

### 3.6 The entities (34.5)

The standard defines 35 entities.

- **Business architecture, organization:** Organization Unit (a unit of resources with its own goals, objectives and measures, possibly external), Actor (a person, organization or system that plays a role in starting or taking part in activity), Role (the part an actor plays), Location (a place where activity happens, extension).
- **Business architecture, function:** Function (business capability at any granularity), Process (flow of control), Business Service (defined interface, deliberately governed), Service (the generic term), Event, Control and Product (process-modeling extension), Contract and Service Quality (governance extension).
- **Motivation and measurement:** Driver, Goal, Objective (motivation extension), Measure (governance extension).
- **Context and change:** Principle, Requirement, Constraint, Assumption, Gap, Capability, Work Package.
- **Data:** Data Entity (core), Logical Data Component, Physical Data Component (data extension).
- **Application:** Application Component, Logical Application Component, Physical Application Component, Information System Service.
- **Technology:** Technology Component, Logical Technology Component, Physical Technology Component, Platform Service.

Definitions in the standard are one to three sentences with an example. Notable points: a Principle has at least a rationale and a measure of importance; a Requirement is a quantitative statement, a Principle a qualitative one; an Objective is time-bounded; a Capability is a business-focused outcome delivered by work packages; a Gap is a difference between two states (used for gap analysis between baseline and target).

### 3.7 Attributes (34.6)

The standard gives **typical attributes**; none is mandatory. Every entity typically has ID, Name, Description, Category, Source and Owner. Beyond that:

- Most application, data, technology and service entities carry a *standards class* (six values from Non-Standard to Retired Standard) and four standard dates (creation, last review, next review, retire).
- A Physical Application Component adds a lifecycle status (five values), release dates and a long list of non-functional characteristics (availability, manageability, security, scalability and so on, 25 in all).
- A Contract carries the same style of non-functional characteristics, plus caller and called service and capacity figures.
- Principle has category (six values), priority, statement, rationale, implication and metric. Requirement has statement (shall, should or may), rationale and acceptance criteria. Capability has business value and increments. Actor has a headcount estimate, goal and tasks. Organization Unit has headcount. Process has criticality, manual or automated, and volumetrics. Data Entity has category (message or internally stored), privacy and retention classification. Work Package has category (work package, work stream, project, program, portfolio) and capability delivered. Physical Technology Component has product, module, vendor and version.
- Some entities have no additional attributes (Constraint, Gap, Control, Driver, Event, Goal, Measure, Objective, Product, Service Quality). Assumption has no row at all.

The full list with descriptions is in `language.yaml`.

### 3.8 Relationships (34.7)

The relationship table has **121 rows**, each naming a source entity, target entity, a relationship name and the module it belongs to. It states no multiplicity. In outline:

- **Organization:** an organization unit contains actors and owns functions; an actor belongs to one, performs tasks in roles, performs and interacts with functions, takes part in processes, consumes services and supplies or consumes data entities.
- **Function and process:** a function is bounded by a service and supported by or realized by processes; a process orchestrates functions and services, involves actors, precedes or follows other processes and decomposes into them.
- **Service:** a service is owned and governed by an organization unit, is provided to actors, provides and consumes data entities, supports and is realized by processes, is realized through logical application components and implemented on logical technology components. Services consume and decompose other services.
- **Application and technology:** logical application components operate on data entities, communicate, decompose and implement services; physical application components are realized by physical technology components; logical technology components supply platform services and provide a platform for services.
- **Extensions:** the table's other rows, grouped by module, add the governance links (measures track objectives and services; contracts govern services and meet service qualities), the process-modeling links (events generated and resolved, controls guiding processes, products produced), the data links (logical and physical data components encapsulating data entities and application components), the infrastructure-consolidation links (location containing, hosting; logical extended by physical) and the motivation links (drivers create and motivate, goals realized through objectives).
- **Decomposition** (the same entity type) exists for most entities. Most relationships appear in both directions under paired names.

The standard also states a few relationships outside the table: the link from an information system service to a business service, and several relationships in the descriptions of artifacts (see section 8).

## 4. Architectural artifacts (35)

### 4.1 Views and viewpoints (35.1 to 35.5)

TOGAF adopts ISO/IEC 42010:2007 (shown in the figure as IEEE 1471). A **system** has an **architecture**, which an **architecture description** documents. Stakeholders have concerns; a **view** represents the whole system from the perspective of related concerns; a **viewpoint** says how to build and use a view, what information it holds, which techniques to use and why. A view is what you see, a viewpoint where you look from. Every view has a viewpoint, at least implicitly. Concerns and requirements are not the same thing: a concern is an area of interest and is decomposed into requirements (SMART ones).

The architect must develop views of both baseline and target architectures, to give the context for gap analysis in Phases B, C and D (35.2.1). The architect is responsible for completeness (all pertinent concerns addressed) and integrity (views connected, conflicts reconciled and trade-offs shown). The standard encourages but does not mandate ISO/IEC 42010 (35.2.2).

### 4.2 Artifacts by ADM phase (35.6, Figure 35-3)

56 artifacts, grouped by the phase in which they are recommended. The ADM phases' own output lists are in Part II (not summarized here). Entity lists are in `language.yaml` under `diagram_types`.

| Phase | Catalogs | Matrices | Diagrams |
|---|---|---|---|
| Preliminary | Principles | none | none |
| A Architecture Vision | none | Stakeholder Map | Value Chain; Solution Concept |
| B Business Architecture | Organization/Actor; Driver/Goal/Objective; Role; Business Service/Function; Location; Process/Event/Control/Product; Contract/Measure | Business Interaction; Actor/Role | Business Footprint; Business Service/Information; Functional Decomposition; Product Lifecycle; Goal/Objective/Service; Business Use-Case; Organization Decomposition; Process Flow; Event |
| C Data Architecture | Data Entity/Data Component | Data Entity/Business Function; Application/Data | Conceptual Data; Logical Data; Data Dissemination; Data Security; Data Migration; Data Lifecycle |
| C Application Architecture | Application Portfolio; Interface | Application/Organization; Role/Application; Application/Function; Application Interaction | Application Communication; Application and User Location; Application Use-Case; Enterprise Manageability; Process/Application Realization; Software Engineering; Application Migration; Software Distribution |
| D Technology Architecture | Technology Standards; Technology Portfolio | Application/Technology | Environments and Locations; Platform Decomposition; Processing; Networked Computing/Hardware; Communications Engineering |
| E Opportunities and Solutions | none | none | Project Context; Benefits |
| Requirements Management | Requirements | none | none |

36 of the 56 are core; 20 belong to an extension module (colored in Figure 35-3). 35.6 describes each artifact in a short passage: its purpose, what it supports, which metamodel entities it holds (stated as a list for every catalog and for the matrices) and, for several, techniques (entity relationship or simplified class models for the Conceptual Data Diagram; swim-lanes for the Process Flow Diagram; heat-maps layered on the Functional Decomposition Diagram).

Three matrices are said to rest on composite relationships that "need validating": Application/Organization (organization units own services; actors of those units use services; services are realized by application components), Role/Application (a role accesses a function; the function is bounded by a service; the service is realized by an application component) and Application/Function (a function is bounded by a service; the service is realized by an application component).

### 4.3 Recommended views (35.7)

Eight views, each described by stakeholders, concerns and key issues: Business Architecture (users), Enterprise Security (security engineers), Software Engineering (software engineers), System Engineering (systems engineers), Communications Engineering (communications engineers), Data Flow (database engineers), Enterprise Manageability (operations and management staff) and Acquirer (purchasers). The standard calls them "a starting point" and not an exhaustive set, and "guides" rather than "a full definition of a viewpoint". Some views have an artifact of the same name. Much of the text is general architecture guidance (security concepts, software tiers, client/server models) rather than modeling rules.

## 5. Deliverables (36)

36.1 lists 21 deliverables with the ADM phases that produce and consume them (for example the Architecture Definition Document, Architecture Requirements Specification, Architecture Roadmap, Architecture Vision, Statement of Architecture Work, Request for Architecture Work, Tailored Architecture Framework). 36.2 describes each with a purpose and typical contents and says the contents are examples, to be referenced rather than copied. The Architecture Definition Document is the container for the core artifacts and spans business, data, application and technology for the baseline, transition and target states. The Architecture Vision carries the Value Chain and Solution Concept diagrams.

## 6. Building blocks (37)

A building block is a package of functionality defined to meet business needs. It has a type that corresponds to a content metamodel entity, a defined boundary generally recognizable as a thing by domain experts, and may interoperate with others. It may be assembled from or be part of other building blocks, ideally re-usable, replaceable and well specified, and its boundary and specification are loosely coupled to its implementation. Architecture building blocks relate to the Architecture Continuum and carry a minimum specification (functionality and attributes, interfaces, interoperability, dependencies, mapping to organization entities and policies). Solution building blocks relate to the Solutions Continuum and are product-aware; their specification adds the implemented interfaces, mapping to IT topology, shared attributes, performance, design drivers and constraints, and the relationships to architecture building blocks (37.2.3, 37.2.4). An architecture needs only the building blocks relevant to its business problem (37.3.1.1).

## 7. Newer versions

TOGAF Version 9.2 was launched on 16 April 2018 (document C182) with further emphasis on business architecture and a restructured document set; the release says it made key enhancements to the Content Metamodel. The TOGAF Standard, 10th Edition (document C220) was announced on 25 April 2022 with a modular document set. This summary describes 9.1 only; 9.2 and the 10th Edition have not been compared.

## 8. Gaps and inconsistencies in the standard

These are the gaps in the standard that change how a model is read:

- The standard disagrees with itself about which entities are core (the text of 34.2.1, Figure 34-6 and Figure 34-7 differ), and about when extensions are chosen.
- The relationship table has no rows for Principle, Constraint, Assumption, Requirement, Gap, Application Component or Technology Component, and no row for Information System Service.
- Several artifact descriptions name relationships the table does not list (Business Service communicates with Business Service, a data entity's owning organization unit, Application Service consumes Application Service).
- The attributes are typical, not mandatory, and the table is incomplete (no row for Assumption).
- Nothing in Part IV defines a notation. How an artifact is drawn is left to the architect.
