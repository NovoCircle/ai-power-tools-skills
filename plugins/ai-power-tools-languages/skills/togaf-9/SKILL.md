---
name: togaf-9
description: The Open Group's TOGAF 9.1 content framework and content metamodel, the structure TOGAF gives to the work products of enterprise architecture. It defines the building blocks an architecture holds (organization unit, actor, role, function, process, business service, data entity, application component, technology component, platform service, principle, requirement, capability, work package and more), the relationships between them, six optional extension modules (governance, services, process modeling, data, infrastructure consolidation, motivation), and 56 named catalogs, matrices and diagrams by ADM phase (for example the Business Footprint diagram, Application/Data matrix and Technology Portfolio catalog). Use when someone is building or reviewing a TOGAF architecture model, asks which TOGAF artifact shows what, which ADM phase produces it, what the TOGAF content metamodel allows, how core and extension content differ, or what a TOGAF catalog, matrix, diagram, deliverable or building block is.
---

# TOGAF 9.1 content framework and content metamodel

TOGAF is The Open Group's framework for enterprise architecture. Its Architecture Development Method (ADM) says how to work; its **content framework** (Part IV) says what the architecture should contain when the work is done. This skill covers the content framework: the content metamodel, and the catalogs, matrices and diagrams that present it. It covers the ADM only where it says which artifacts are produced in which phase.

**TOGAF is not a modeling-language standard.** It defines no notation, no symbols and no diagram syntax. It names the artifacts, says what each is for, and lists the entity types each holds. How an artifact is drawn is the architect's choice.

This skill describes version 9.1 (December 2011). TOGAF 9.2 (April 2018) changed the content metamodel in ways this skill does not describe, and the 10th Edition (April 2022) has a different structure. If the model follows one of those, check the differences before relying on the tables here.

## What you are creating

A TOGAF architecture is a set of **building blocks** (entities of the content metamodel, such as a business service called "Account Opening"), recorded in **catalogs** (lists), related in **matrices** (grids) and shown in **diagrams** (pictures). A **deliverable** (for example the Architecture Definition Document) is the contractual package that holds many of those artifacts. The content metamodel is the structure that keeps the artifacts consistent: it says which entity types exist, what attributes they typically carry, and which relationships are possible between them.

Most stakeholders never see the metamodel. They ask questions such as "what functionality does this application support?" and read an artifact that answers it.

## Core and extensions

The **core** metamodel is the minimum for traceability. Six **extension modules** add depth where an engagement needs it. All are optional. The standard says to choose them when the engagement is scoped (it names the Preliminary Phase in one place and the Architecture Vision phase in another), and that the grouping is a suggestion that may be tailored.

| Module | Adds | Use when |
|---|---|---|
| Governance | Measure, Service Quality, Contract; Contract/Measure catalog; Enterprise Manageability diagram | Service levels differ from service to service and must trace to objectives |
| Services | Information System Service (a kind of business service); Business Use-Case and Organization Decomposition diagrams | Business and IT describe the same capability in different terms |
| Process Modeling | Event, Control, Product; Process/Event/Control/Product catalog; Process Flow and Event diagrams | The architecture must show events, control steps or elaborate process flow |
| Data | Logical Data Component, Physical Data Component; Data Security, Data Migration and Data Lifecycle diagrams | Data location, encapsulation or access carries real risk |
| Infrastructure Consolidation | Location; logical and physical application and technology components; Location catalog and seven diagrams | Overlapping applications or technology are being consolidated |
| Motivation | Driver, Goal, Objective; Driver/Goal/Objective catalog; Goal/Objective/Service diagram | Competing drivers and objectives must be understood in a structured form |

Note: the standard's figure puts Logical Application Component and Physical Technology Component in the core and Physical Application Component and Logical Technology Component in Infrastructure Consolidation, while its text says all four belong to the extension. This skill follows the figure.

## The entities, in plain words

**Context and change (associated with every other entity):** **Principle** (a qualitative statement of what the architecture is expected to achieve, with a reason and a priority), **Requirement** (a quantitative statement of need), **Constraint** (an external factor limiting approaches), **Assumption** (a probable fact not yet validated), **Gap** (the difference between two states, used between baseline and target), **Work Package** (a set of actions to achieve objectives; part of a project, a project, or a program) and **Capability** (a business outcome delivered by work packages).

**Business architecture:**

- **Organization Unit**: a unit of resources with its own goals, objectives and measures (external parties and partners can be units too). It owns functions and owns and governs business services.
- **Actor**: a person, organization or system that has a role and takes part in activity. **Role**: the part an actor plays.
- **Function**: a bounded unit of business capability at any level of granularity (value chain, process area, capability, business function all become functions).
- **Process**: a flow of control between or within functions or services. A process is not deployed; it describes how a function executes.
- **Business Service**: behavior offered through a defined interface and deliberately governed by an organization. It bounds one or more functions. **Service** is the generic term; business, information system and platform services are the three kinds.
- **Location** (extension): a place where business activity happens.
- Extensions: **Driver**, **Goal**, **Objective** (motivation); **Measure**, **Service Quality**, **Contract** (governance); **Event**, **Control**, **Product** (process modeling).

**Data:** **Data Entity** (data a domain expert recognizes as a discrete thing). Data extension: **Logical Data Component** and **Physical Data Component**, which group data entities for governance and deployment.

**Application:** **Application Component** (application functionality aligned to implementation), in two kinds: **Logical** (a class of application, independent of implementation) and **Physical** (an actual deployable instance). **Information System Service** (extension) is the automated part of a business service.

**Technology:** **Technology Component**, in two kinds: **Logical** (a class of product) and **Physical** (a specific product). **Platform Service** is the technical capability the infrastructure provides to applications.

## Relationships, in summary

The standard lists 121 possible relationships (source entity, target entity, name, module), in a table in 34.7. It gives no multiplicities and no relationship attributes. The full table is in `language.yaml`. The main chains:

- An **organization unit** contains **actors** and owns **functions** and **business services**. An actor belongs to one, performs tasks in **roles**, performs functions, takes part in processes, consumes services and supplies or consumes data entities.
- A **function** is bounded by a **service** and is realized by **processes**. A process orchestrates functions and services, involves actors, precedes or follows other processes and decomposes.
- A **service** provides and consumes **data entities**, is realized through **logical application components**, and is implemented on **logical technology components**. Logical application components operate on data entities; physical application components are realized by **physical technology components**; logical technology components supply **platform services**.
- Most entity types decompose into their own kind.
- Extensions add: measures track objectives and services; contracts govern services and meet service qualities; events are generated and resolved by actors, processes and services; controls guide processes; drivers motivate organization units and create goals; goals are realized through objectives; locations contain and host physical components; physical components extend logical ones; logical data components encapsulate data entities.

Most relationships appear in both directions under paired names (Actor performs Function, Function is performed by Actor): read it as one link seen from either end.

The table is the standard's list of **possible** relationships and it can be tailored. A link outside it is a warning, not an error. The table has no rows for principle, requirement, constraint, assumption or gap (the figures say they are associated with every entity) or for the single "application component" and "technology component" entities; several artifact descriptions also name relationships the table lacks. Do not treat the table as proof that a link is right, only as the standard's own list.

## Artifacts, by ADM phase

56 artifacts: 14 catalogs, 10 matrices, 32 diagrams. 36 are core; 20 belong to an extension module (marked). The standard recommends them for the phase shown ("may be created"). **Catalogs** and **matrices** hold the entity types listed; for diagrams the entities are read from the standard's description and are not a closed list. The full per-artifact list is in `language.yaml` (`diagram_types`).

| Phase | Catalogs (entities) | Matrices (axes) | Diagrams |
|---|---|---|---|
| Preliminary | Principles (Principle) | | |
| A Vision | | Stakeholder Map (no formal entities) | Value Chain; Solution Concept |
| B Business | Organization/Actor (organization unit, actor, location); Driver/Goal/Objective [Motivation] (+ organization unit, optionally measure); Role; Business Service/Function (organization unit, function, business service, optionally information system service); Location [IC]; Process/Event/Control/Product [Process]; Contract/Measure [Governance] | Business Interaction; Actor/Role | Business Footprint; Business Service/Information; Functional Decomposition; Product Lifecycle; Goal/Objective/Service [Motivation]; Business Use-Case [Services]; Organization Decomposition [Services]; Process Flow [Process]; Event [Process] |
| C Data | Data Entity/Data Component (data entity, logical and physical data component) | Data Entity/Business Function; Application/Data (logical application component by data entity) | Conceptual Data; Logical Data; Data Dissemination; Data Security [Data]; Data Migration [Data]; Data Lifecycle [Data] |
| C Application | Application Portfolio (information system service, logical and physical application component); Interface (logical and physical application component) | Application/Organization; Role/Application; Application/Function; Application Interaction | Application Communication; Application and User Location; Application Use-Case; Enterprise Manageability [Governance]; Process/Application Realization [IC]; Software Engineering [IC]; Application Migration [IC]; Software Distribution [IC] |
| D Technology | Technology Standards; Technology Portfolio (platform service, logical and physical technology component) | Application/Technology | Environments and Locations; Platform Decomposition; Processing [IC]; Networked Computing/Hardware [IC]; Communications Engineering [IC] |
| E Opportunities and Solutions | | | Project Context; Benefits |
| Requirements Management | Requirements (requirement, assumption, constraint, gap) | | |

[IC] = Infrastructure Consolidation.

A few readings worth knowing:

- The **Business Footprint** diagram links business goals, organization units, functions and services, and maps functions to the technology that delivers them. It is the senior-stakeholder view that traces a technical component to the goal it serves.
- The **Functional Decomposition** diagram shows an organization's capabilities on one page, so scope and decisions can be layered on as a heat-map.
- The **Application/Function**, **Role/Application** and **Application/Organization** matrices are not direct relationships. Each is read through a path in the metamodel (an organization unit owns services, actors of that unit use them, application components realize them). The standard says these need validating.
- The **Application/Data** matrix reads logical application component against data entity (who creates, reads, updates and deletes what).
- The **Data Entity/Business Function** matrix assigns data ownership to organizations.
- A **Stakeholder Map** matrix uses no formal entities on purpose; the Vision phase is informal.

## Views

Eight recommended views, each for a stakeholder group: Business Architecture (users), Enterprise Security (security engineers), Software Engineering, System Engineering, Communications Engineering, Data Flow (database engineers), Enterprise Manageability (operations) and Acquirer (purchasers). A **view** is what the stakeholder sees; a **viewpoint** says how to build and read it. Every view has a viewpoint, at least implicitly. Concerns are areas of interest; requirements are how a concern is made concrete.

## The rules that matter most

TOGAF states almost no hard rules; most guidance below is `should` (warning) or `note` (advice). The full list is in `references/rules.md`.

- **TOGAF-REL-001 (should):** use relationships the metamodel table lists. A link outside it is a warning.
- **TOGAF-REL-002 and EXT-003 (should):** use extension entities, relationships and artifacts only when that module has been chosen for the engagement.
- **TOGAF-DEF-001 (should):** a process describes flow and is not deployed. Application and technology components implement the function and its services, not the process.
- **TOGAF-DEF-003 and DEF-004 (should):** a business service is owned and governed by an organization unit and bounds at least one function.
- **TOGAF-DEF-006 (note):** a business service supported by several application components is a sign of a service that is too coarse or components that are too fine.
- **TOGAF-DEF-008 (should):** every principle has a rationale and a priority.
- **TOGAF-DEF-009 (should):** every requirement says whether it shall, should or may be met.
- **TOGAF-ART-002 to ART-004 (should):** read the three composite matrices through their paths; a cell is supported only if the path exists.
- **TOGAF-VIEW-004 (must):** develop views of both the baseline and the target architecture. This is the standard's only obligation, and it cannot be checked from a model alone.
- **TOGAF-ATTR rules (should/note):** attributes are typical, not mandatory. Where the standard gives a value set (standards class, lifecycle status, principle category, work package category) use it.

## Data types and attributes

Coverage is partial (`data_types` in `language.yaml`, 34.6). The standard names no primitive types: no string, number, date or Boolean. It gives value sets for six attributes: Standards class (six values, from Non-Standard to Retired Standard), the lifecycle status of a physical application component (five), principle category (six), data entity category (two), work package category (five) and location category (four named, open to more). The 35 content metamodel entities carry typical attributes, none mandatory; six common ones (ID, Name, Description, Category, Source, Owner) apply to all, and each entity's own list adds the rest. The standard gives no multiplicity for any attribute, and it types an attribute only through those value sets.

## How it is drawn

Sizes and spacing come from `../_languages/layout-standard.yaml`, and the concept mapping from `layout` in `language.yaml`.

The standard defines no symbols for any concept or relationship (coverage: none for symbols, `notation` in `language.yaml`). What the standard does give is the form an artifact takes: a catalog is a list, a matrix is a table, a diagram is a graphic of building blocks and their relationships. Five matrices are described as a two-dimensional table with named axes (35.6.4, 35.6.5). For a few diagrams it names a technique: entity relationship or simplified class models, swim-lanes, a heat-map over a one-page decomposition. Its worked example (35.1.1) draws locations as outer boxes with business functions nested inside. Anything else about how an artifact looks is the architect's choice.

## A short example (Westbrook Bank)

This is an illustration. Substitute your own organization, entities and artifacts.

Westbrook Bank is building the architecture for opening a retail account.

- **Organization Unit** "Retail Banking" owns **Function** "Customer Onboarding" and owns and governs **Business Service** "Account Opening". The function is bounded by that service.
- The function is realized by **Process** "Open Account". **Actor** "Branch Teller" belongs to Retail Banking and performs tasks in **Role** "Account Officer", which accesses the function.
- **Data Entity** "Customer" is provided and consumed by the service.
- **Logical Application Component** "Account Management" implements the service (the service is realized through it) and operates on "Customer". **Physical Application Component** "Account Management v7 (production)" extends it, and **Physical Technology Component** "Retail Core Server Cluster" realizes that physical component. (This needs the Infrastructure Consolidation extension; without it only the logical component and the physical technology component are used.)
- **Principle** "Data is a shared asset" has the rationale "Duplicate customer records cause errors".

The artifacts that follow from this: the **Organization/Actor catalog** lists Retail Banking and Branch Teller; the **Application/Function matrix** puts Account Management against Customer Onboarding, supported through the service "Account Opening" (rule ART-004); the **Application/Data matrix** puts Account Management against Customer; the **Application/Technology matrix** puts the physical component against the server cluster. A **Business Footprint** diagram would link the Retail Banking goal to the organization unit, function, service and technology.

## What this skill does not cover

TOGAF 9.2 and the 10th Edition. The ADM method itself, the Enterprise Continuum, the Technical Reference Model, the architecture governance chapters and the full deliverable descriptions (only where they bear on artifacts). TOGAF defines no notation, so there are no drawing rules here.

## References

- `references/standard.md`: Part IV of the standard in our own words, section by section.
- `references/rules.md`: every rule, with id, strength, section and whether it can be checked.
- `language.yaml`: the machine-readable form: 55 concepts, 143 relationships (121 from the standard's table), six extension modules, 56 artifacts with the entity types each holds, eight views, 49 rules.
