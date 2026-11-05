---
name: archimate-3
description: The Open Group's ArchiMate 3.1, the modeling language for enterprise architecture. It describes an enterprise across business, application and technology layers, with physical elements, a motivation aspect (stakeholders, drivers, goals, requirements), strategy (capabilities, value streams, resources, courses of action) and implementation and migration (work packages, deliverables, plateaus, gaps), joined by eleven relationship types and shown through viewpoints. Use when someone is modeling or reviewing an enterprise architecture, building an ArchiMate model, choosing a viewpoint or view, deciding which relationship is allowed between two elements, working with business, application or technology layer elements, capability maps, value streams, motivation or goal models, transition and migration planning, or asks what ArchiMate allows.
---

# ArchiMate 3.1

ArchiMate is The Open Group's language for describing the architecture of an enterprise: what the business does, the applications and data that support it, the technology they run on, why the enterprise is making its choices, and how it plans to change. It is a modeling language, not a method, and it has a fixed set of element types, a fixed set of relationship types and a table that says which relationship may join which two elements.

This skill describes version 3.1. A short section near the end says what 3.2 changes.

## What you are creating

An ArchiMate model is a set of elements joined by relationships. Elements are typed, and the types say which layer and which aspect an element belongs to. The model describes types of things (the account-opening process, not one particular opening), not individual instances. Diagrams, catalogs and matrices are views of the model, chosen to answer one stakeholder's concerns; the standard calls the recipe for a view a viewpoint.

Everything in a model is an element with a name, plus whatever documentation you give it. The standard defines no mandatory attributes. It offers optional ones through its customization mechanism (see "Extending the language").

## Layers and aspects

Three core layers each have three aspects. Motivation, strategy and implementation and migration sit beside them.

| | Active structure (who or what acts) | Behavior (what is done) | Passive structure (what is acted on) |
|---|---|---|---|
| **Business** | Business actor, role, collaboration, interface | Business process, function, interaction, event, service | Business object, contract, representation |
| **Application** | Application component, collaboration, interface | Application process, function, interaction, event, service | Data object |
| **Technology** | Node, device, system software, technology collaboration, interface, path, communication network | Technology process, function, interaction, event, service | Artifact |

- **Physical** elements (equipment, facility, distribution network, material) extend the technology layer to the physical world.
- **Motivation** elements explain why: stakeholders and their drivers, the assessments of them, and the goals, outcomes, principles, requirements and constraints that follow.
- **Strategy** elements say what the enterprise can do and how it intends to use it: capabilities, value streams, resources and courses of action.
- **Implementation and migration** elements plan the change: work packages, deliverables, events, plateaus and gaps.
- Two **generic composites**, grouping and location, can sit anywhere.

The classification is a guide, not a cage: a real element need not fit one cell exactly. Layer colors, layer letters and corner shapes are cues only and carry no formal meaning.

## The concepts, in plain words

The standard has 58 element types; counting grouping and location as the generic composites they are, there are 60 concrete element concepts. Product and plateau are composites too. The spelling in `language.yaml` is the standard's own type name without spaces.

### Generic composites

- **Grouping**: gathers concepts (elements, relationships, or both) that belong together for some reason. It is a model element, not a view.
- **Location**: a place, conceptual or physical, where structure elements are located or behavior is performed.

### Motivation (chapter 6)

- **Stakeholder**: a person, team or organization (or a class of them) with an interest in the architecture.
- **Driver**: a condition inside or outside the enterprise that pushes it to set goals and change. A driver tied to a stakeholder is a concern.
- **Assessment**: the result of analyzing the enterprise against a driver: strengths, weaknesses, opportunities, threats.
- **Goal**: a high-level statement of intent or desired end state, usually qualitative.
- **Outcome**: an end result, tangible and possibly measurable, produced by capabilities. It can also be unwanted.
- **Principle**: a statement of a general property that should hold for any system in a context. Broader than a requirement.
- **Requirement**: a statement of need for a specific system the architecture describes.
- **Constraint**: a kind of requirement that limits how the system is realized rather than what it does.
- **Meaning**: the knowledge or interpretation given to a concept in a context.
- **Value**: the relative worth, utility or importance of a concept.

### Strategy (chapter 7)

- **Resource**: an asset the enterprise owns or controls. It is structure, neither active nor passive.
- **Capability**: an ability the enterprise, a person or a system has, realized by the core elements. Behavior.
- **Value stream**: a sequence of activities that creates an overall result for a customer or stakeholder. Behavior.
- **Course of action**: an approach or plan for configuring capabilities and resources to reach a goal. Strategies and tactics are kinds of it, not separate concepts. Behavior.

### Business (chapter 8)

- **Business actor**: a person or organization unit that can perform behavior. **Business role**: the responsibility to perform specific behavior, which an actor can fulfill. **Business collaboration**: two or more actors or roles working together on collective behavior, possibly only for a while. **Business interface**: a point of access where a business service is available.
- **Business process**: a sequence of behavior that achieves a specific result. **Business function**: behavior grouped by chosen criteria such as skills or resources. **Business interaction**: collective behavior of a collaboration. **Business event**: an organizational state change. **Business service**: explicitly defined behavior exposed to the environment.
- **Business object**: a concept used within a business domain, usually a type. **Contract**: a formal or informal agreement between provider and consumer; a kind of business object. **Representation**: a perceptible form of the information a business object carries.
- **Product**: a coherent collection of services and/or passive structure with a contract, offered as a whole to customers. A composite that can span layers.

### Application (chapter 9)

- **Application component**: a modular, replaceable piece of application functionality. **Application collaboration**: two or more components (or collaborations) acting together. **Application interface**: a point of access to application services.
- **Application process, function, interaction**: automated behavior of the same three kinds as in the business layer. **Application event**: an application state change. **Application service**: exposed application behavior.
- **Data object**: data structured for automated processing.

### Technology (chapter 10)

- **Node**: a computational or physical resource that hosts, manipulates or interacts with other such resources. **Device**: a physical IT resource. **System software**: software that provides an environment, such as an operating system or database. **Technology collaboration**: nodes (or collaborations) working together. **Technology interface**: a point of access to technology services. **Path**: a link between nodes through which they exchange data, energy or material. **Communication network**: a set of structures connecting nodes.
- **Technology process, function, interaction**, **technology event** and **technology service**: the behavior counterparts.
- **Artifact**: a piece of data used or produced in development or deployment: a file, executable, script, table.
- **Technology object** is the standard's name for the passive parent of artifact and material. It is abstract: use artifact or material.

### Physical (chapter 11)

- **Equipment**: machines, tools or instruments that create, use, store, move or transform materials. **Facility**: a physical structure such as a factory or building that houses equipment. **Distribution network**: a physical network that transports materials or energy, the physical realization of a path. **Material**: tangible matter or energy.

### Implementation and migration (chapter 13)

- **Work package**: a series of actions with a start and an end, aimed at specific results within time and resource limits.
- **Deliverable**: a precisely defined result of a work package. **Implementation event**: an instantaneous state change related to implementation or migration.
- **Plateau**: a relatively stable state of the architecture during a limited period. A composite.
- **Gap**: a statement of the difference between two plateaus.

### Abstract concepts

The standard also names abstract parents: structure element, active structure element, behavior element, passive structure element, motivation element, composite element, and the layer-level internal active structure, internal behavior and passive structure elements. They organize the language and are never instantiated in a model. `language.yaml` lists them and marks every generalization link the specification does not state in words as inferred.

## Relationships

Eleven relationship types in four groups, plus one connector. Each relationship has exactly one source and one target.

| Group | Relationship | Use it when |
|---|---|---|
| Structural | **Composition** | One thing consists of others and the parts go with the whole. |
| Structural | **Aggregation** | One thing groups others, and the parts can exist without it. |
| Structural | **Assignment** | Something is given the responsibility for, or performs, behavior; or a node holds an artifact. |
| Structural | **Realization** | One thing plays a critical part in making a more abstract thing real. |
| Dependency | **Serving** | One thing provides its functionality to another. |
| Dependency | **Access** | Behavior or an active element reads or writes a passive element. |
| Dependency | **Influence** | One thing helps or hinders a motivation element. Sign and strength are yours to record. |
| Dependency | **Association** | Things are related and nothing else fits, or you do not yet know how. |
| Dynamic | **Triggering** | One thing causes or precedes another in time. |
| Dynamic | **Flow** | Something (information, goods, money) moves from one thing to another. Not causal by itself. |
| Other | **Specialization** | One thing is a particular kind of another. |
| Connector | **Junction** | Several relationships of the same type are joined with and, or or. |

### Choosing among them

Ask the questions in order and stop at the first yes.

1. Is it a kind of the other thing? Specialization.
2. Is it made of the other thing? Composition if the parts disappear with the whole, aggregation if they do not.
3. Does it do the other thing, or hold it? Assignment (an actor or node to the behavior it performs or the artifact it holds).
4. Does it make the other thing real or achieve it? Realization (a process realizes a service; an outcome realizes a goal; an artifact realizes a component). Use influence instead when the contribution is not critical.
5. Does it provide what the other thing needs? Serving.
6. Does it read or write the other thing? Access, and only toward passive structure.
7. Does it come before, or move something to, the other thing? Triggering for cause and sequence; flow for transfer.
8. Does it affect a goal, requirement or other motivation element? Influence.
9. None of these, or undecided? Association.

Whatever you choose, the pair must appear in the allowed table. The table in `language.yaml` (`relationships.allowed`) lists, for every source and target concept, the letters of the relationship types allowed. A pair outside the table is an error. A pair inside it is permitted, not recommended: the table includes derived relationships the standard says can be wrong in a given model, so it is an upper bound, not a statement that the relationship is right. Association is always allowed between any two elements.

If the prose of the specification and the table disagree (assignment is the case that matters), read the table. Assignment, for example, chiefly joins active structure to behavior and to other active structure (an actor to a role), and technology and physical active structure to artifacts and materials; the table has no assignment from behavior to passive structure.

### Derivation, in plain words

Two relationships in a chain can often be replaced by one between the ends. A is assigned to B and B realizes C, so A realizes C. The new relationship takes the weaker of the two when both are structural (strongest to weakest: composition, aggregation, assignment, realization); a structural relationship followed by a dependency or dynamic one hands you the dependency or dynamic one. Specialization and triggering chain freely.

Three cautions. Derivation only goes from more detail to less; it never adds detail. It does not work through a grouping, and between the core layers and motivation, strategy or implementation and migration only realization and influence can be derived. Access can be derived only toward passive structure. The standard also lists "potential" derivations that may or may not hold in a particular model; check them before relying on them. You may draw a derived relationship without drawing the chain behind it.

### The junction rule

A junction joins relationships of one type, in an and or an or variant. It accepts access, assignment, flow, influence, association, realization, triggering and serving, and never composition, aggregation or specialization. A path through junctions is valid only if a direct relationship of that type between the two end elements would be valid. Several in and one out, one in and several out, and several of both are all fine. An or junction means inclusive or exclusive or; the standard gives it no execution meaning.

## Viewpoints

A viewpoint says which concepts to use and how to show them for a set of stakeholder concerns. The standard describes 25 example viewpoints; they are examples, not an exhaustive or normative list. In any viewpoint you may also use grouping, junctions and all relationships. Full admitted-concept lists are in `language.yaml`.

| Viewpoint | Scope | Shows |
|---|---|---|
| Organization | business | Actors, roles, collaborations and interfaces, and where they are |
| Application Structure | application | Components, interfaces, collaborations and their data |
| Information Structure | business and application | Business objects, representations, data objects and artifacts |
| Technology | technology | Nodes, software, networks, technology behavior and artifacts |
| Layered | all layers | Everything in the core layers on one view |
| Physical | technology and physical | Equipment, facilities, networks and materials |
| Product | business to technology | A product with its services, contracts and what supports them |
| Application Usage | business and application | How applications support business behavior |
| Technology Usage | application and technology | How technology supports applications |
| Business Process Cooperation | business and application | How processes and the systems behind them work together |
| Application Cooperation | application | How applications work together |
| Service Realization | business and application | How services are realized by behavior and components |
| Implementation and Deployment | application and technology | Software deployed onto platforms |
| Stakeholder | motivation | Stakeholders, drivers and assessments |
| Goal Realization | motivation | Goals refined down to requirements |
| Requirements Realization | motivation to core | Requirements and the elements that realize them |
| Motivation | motivation | The whole motivation aspect |
| Strategy | strategy | Courses of action, capabilities, value streams, resources |
| Capability Map | strategy | Capabilities and resources against outcomes |
| Value Stream | strategy | A value stream and the capabilities that serve it |
| Outcome Realization | strategy to core | How outcomes are realized |
| Resource Map | strategy | Resources and capabilities, and the work packages that change them |
| Project | implementation and migration | Work packages, deliverables, events and who is involved |
| Migration | implementation and migration | Plateaus and the gaps between them |
| Implementation and Migration | all | Projects together with the architecture they change |

Two more viewpoints, **Goal Contribution** (influence between goals and requirements) and **Principles** (principles and the goals that motivate them), are named in the standard's introduction but not specified. Use them as names only.

Each viewpoint can be classed by purpose (designing, deciding, informing) and by content (one layer and one aspect, several of either, or both). Choose the viewpoint from the stakeholder's question first; the concepts follow from it.

## The rules that matter most

The full list, 60 rules with ids, is in `references/rules.md`. The ones to keep in front of you:

- Every relationship has one source and one target; no relationship may join two relationships. (ARCHIMATE-REL-001, 002)
- A relationship between two elements must appear in the allowed table. (ARCHIMATE-REL-003)
- Access always points at passive structure. (ARCHIMATE-REL-010)
- A junction carries one relationship type, and never composition, aggregation or specialization. (ARCHIMATE-JCT-001, 002)
- A relationship drawn to another relationship can only be association, or aggregation or composition from a composite element. (ARCHIMATE-REL-006)
- A grouping is joined to its members by aggregation or composition. (ARCHIMATE-CMP-001)
- Abstract concepts are never instantiated; a contract is a kind of business object; a constraint is a kind of requirement. (ARCHIMATE-ELM-004 to 006)
- A collaboration has two or more members and an interaction needs two or more performers. These are definitions stated in prose, so treat a miss as a warning. (ARCHIMATE-ELM-001, 002)
- Use realization for a critical contribution and influence for a non-critical one. (ARCHIMATE-REL-011)
- Do not use the deprecated constructs: "used by", the two-ended assignment notation, the required-interface notation. (ARCHIMATE-LNG-006)

## Telling similar concepts apart

- **Business actor, role or collaboration.** The actor is who (a person or unit), the role is the responsibility an actor fulfills, and a collaboration is several of them working together.
- **Service or interface.** A service is behavior the provider promises. An interface is where the service is reached. One interface can offer several services.
- **Process, function or interaction.** A process is a sequence with a result. A function groups behavior by skill or resource, whatever the sequence. An interaction is behavior that needs two or more performers together.
- **Business object, representation, data object or artifact.** A business object is a business concept. A representation is a form it takes (a letter, a screen). A data object is the same information structured for a system. An artifact is the physical file or table that holds it when deployed.
- **Goal, outcome, principle, requirement or constraint.** A goal is the intent, an outcome the result achieved, a principle a rule of thumb for all systems in a context, a requirement a need of a specific system, and a constraint a requirement that limits the way the system is realized.
- **Capability, value stream or course of action.** A capability is what the enterprise can do, a value stream the sequence that delivers value to someone, and a course of action the plan for configuring them.
- **Capability or resource.** A capability is an ability. A resource is an asset the ability uses.
- **Grouping, location, plateau or product.** All four collect other things. A grouping collects by any common trait, a location by place, a plateau by a state of the architecture in time, a product by what is offered together to customers.
- **Work package or deliverable.** The work package is the effort; the deliverable is what it produces.
- **Aggregation or composition.** Ask whether the part can exist, on its own, without the whole.

## A short example

Westbrook Bank, a fictitious bank, wants small businesses to open accounts quickly.

**Why (motivation).** The driver "Competitors offer same-day account opening" influences the goal "Small businesses find account opening easy". An outcome "Business accounts active within one day" realizes the goal. A requirement "Verify identity during the online application" realizes the outcome, and an assessment "Business deposits are at risk" is associated with the driver.

**What the bank can do (strategy).** The capability "Business account opening" realizes the outcome; a course of action "Digitize account opening" realizes it too.

**Business layer.** The business role "Account Officer" is assigned to the business process "Open Business Account", which realizes the business service "Business Account Opening", realizes the requirement above, and realizes the capability. The process accesses the business object "Account Application"; the contract "Account Agreement" is a kind of business object.

**Application layer.** The application service "Application Intake" serves the process. The application component "Account Origination" realizes the service, and the service accesses the data object "Application Record", which realizes the business object "Account Application".

**Technology layer.** The node "Origination Server" is assigned the artifact "Origination Package", which realizes the component. The system software "Relational Database" serves the component.

**Change.** The work package "Launch Digital Onboarding" realizes the deliverable "Origination Release", which realizes the component.

Each of these pairs appears in the allowed table. Use your own enterprise's elements, and any viewpoint that answers your stakeholders' questions: Service Realization would show the middle of this example; Motivation the top; Project the bottom.

## Data types and attributes

Coverage: none. The specification defines no data types and no attributes for any concept; every element has a name and documentation, nothing more. It says only that any concept may carry attributes added through a profile of typed attributes (15.1), and it names no types for them. Events may have a time attribute and influence may carry a sign and strength, both left untyped (4.1.2, 13.2.3, 5.2.3). See `data_types` in `language.yaml`.

## How it is drawn

Coverage: informative. Appendix A gives one default iconography, and a conforming tool has to support it (1.3). A modeler may draw another way (3.7). Every concrete concept and relationship is described in `notation` in `language.yaml`, with its section; the abstract concepts have no drawing.

Sizes and spacing come from `../_languages/layout-standard.yaml`, and the concept mapping from `layout` in `language.yaml`.

- **Elements** are a box with a small icon in the upper right corner. In most cases the icon alone may stand in for the box. Behavior elements (process, function, interaction, service, event, and the strategy and migration behaviors) are rounded rectangles. Active and passive structure elements are plain rectangles. Passive structure is told apart by a line near the top (business object, data object), two lines (contract), or a wavy bottom edge (representation, deliverable, gap). Motivation elements are rectangles with the corners cut off diagonally. Node-like physical elements and plateau use a three-dimensional box. Grouping is a dashed rectangle with a tab; meaning is a cloud and value an ellipse.
- **Relationships** are lines. Composition and aggregation end in a filled or hollow diamond at the source. Assignment starts with a filled dot and ends in a filled arrowhead. Realization is dotted with a hollow triangle, specialization solid with a hollow triangle. Serving is solid with an open arrowhead, access dotted with an optional small arrowhead for write, read or both, influence dashed with an open arrowhead and an optional sign. Triggering is solid and flow dashed, both with a filled arrowhead. Association is a plain line, optionally with a small arrowhead when directed. A junction is a small filled (and) or hollow (or) circle.
- **Nesting** one element in another may replace a line for some structural relationships and for access (3.8).
- **Color** has no meaning in the standard. Yellow for business, blue for application and green for technology is a convention used in its examples (3.9), not a rule.

## Extending the language

The standard allows two extensions. A **profile** attaches a defined set of typed attributes to elements or relationships, so you can record criticality, ownership or a heat-map score. **Specialization** creates new element or relationship types from existing ones: the new type keeps its parent's definition and inherits every relationship its parent allows, and may add an icon. The standard defines no attributes itself; the exchange format adds three optional ones: an access type on access (read, write, read and write), a modifier on influence (for example + or -), and a directed flag on association.

## What 3.2 changes

ArchiMate 3.2 (published 19 October 2022) adds no element or relationship type. It reclassifies device, system software, facility and equipment so they are no longer subtypes of node but of a technology internal active structure element, with composition and aggregation to node. It adds a few relationship cells (for example composition and aggregation from plateau to outcome, realization from material to equipment), moves the physical elements into the technology layer chapter, rewords the derivation restrictions and several definitions, and changes some notation. This skill and its files describe 3.1.

## References

- `references/standard.md`: the standard chapter by chapter, in our own words, with citations.
- `references/rules.md`: all 60 rules with stable ids (`ARCHIMATE-<CAT>-nnn`), strength and source section.
- `language.yaml`: the machine-readable form: concepts and their generalizations, the eleven relationship types, the allowed table, the junction rule, the derivation rules, the viewpoints and the rules.
