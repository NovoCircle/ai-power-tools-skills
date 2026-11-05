---
name: vdml-1
description: The OMG Value Delivery Modeling Language (VDML) 1.0, a standard for modeling how an enterprise creates and exchanges value - value networks and business networks, collaborations and the roles in them, activity networks with deliverable flows between activities, stores and pools, business items, value propositions and value adds, capabilities and capability offers, capability methods, organization units and communities, scenarios, and measured characteristics. Use when someone is modeling value delivery, value streams or value networks, collaborations, roles and assignments, activity networks, deliverable flows, value propositions, capability maps, capability heat maps or capability management, organization structure as collaborations, or measurement dependencies, or when they ask what VDML allows or which VDML diagram to use.
---

# Value Delivery Modeling Language (VDML) 1.0

VDML is the Object Management Group's standard for analyzing and designing how an enterprise operates, with the focus on how value is created, exchanged and measured. It is a class model (a metamodel) plus a limited, normative graphical notation of eight diagram kinds. It is not a business process language: it shows who does what work, what flows between them, which capabilities support it and what value each step adds, at a level above process detail. Measures themselves come from a second OMG standard, SMM (the Structured Metrics Metamodel); VDML only says where measurements attach.

This skill describes version 1.0 (October 2015). A newer version, 1.1 (March 2018), exists and is not covered.

## What you are creating

A VDML model, one **ValueDeliveryModel**, answers these questions about an enterprise or a part of it:

1. Who works together, in which roles? (Collaborations: organization units, business networks, communities, capability methods; their Roles)
2. What work do the roles do, and what flows between them? (Activities, DeliverableFlows, BusinessItems, Stores and Pools, with Ports)
3. What value does each piece of work add, and what does the recipient get? (ValueAdds, ValuePropositions)
4. Which capabilities does the work need, and who offers them? (Capabilities, CapabilityOffers, OrgUnits, CapabilityMethods)
5. How well does it perform, under which circumstances? (MeasuredCharacteristics, Scenarios)

The standard's machine-readable model requires a name and a description on every element. Everything else follows the concepts below.

## Diagram types and what each admits

The standard defines eight diagram kinds (clause 8). Colors carry no meaning. The full notation is in `language.yaml`.

| Diagram | Use it to show | Admits |
|---|---|---|
| **Role Collaboration** (8.2) | Which Roles of one Collaboration exchange deliverables, without activity detail | Role (and its subtypes), DeliverableFlow between different Roles. A flow between Activities of the same Role is not drawn. |
| **ValueProposition Exchange** (8.3) | Which Role provides and which receives which ValueProposition; a more abstract view than the above | ValueProposition, Role, provider and recipient links |
| **Activity Network** (8.4) | The work of each Role as swim-lanes, the Stores and Pools used, flows, ports, value adds, delegation to sub-collaborations | Role, Activity, Store, Pool, ports, ValueAdd on output ports, DeliverableFlow, internal port delegations |
| **Collaboration Structure** (8.5) | Collaborations, the Roles they contain, and who fills them; an organization structure or a network | Collaboration and its four subtypes, Role, Actor, role containment, role assignment |
| **CapabilityLibrary** (8.6) | A capability map: the hierarchy of capabilities | Capability (definitions and categories), parent-child hierarchy |
| **Capability Heatmap** (8.7) | A capability map that flags capabilities needing attention | As CapabilityLibrary, with the heat state from offers' heat index against the Scenario's threshold |
| **Capability Management** (8.8) | What each OrgUnit offers and what supports each offer | CapabilityOffer, OrgUnit, CapabilityMethod, Store, Pool, Position |
| **Measurement Dependency** (8.9) | How measurements influence each other (positive or negative) | MeasuredCharacteristic, MeasurementRelationship (from SMM) |

Choosing: to explain a business network or value exchange, start with Role Collaboration and ValueProposition Exchange; to explain operations and value contributions, Activity Network; to explain structure, Collaboration Structure; to plan capabilities, CapabilityLibrary, Capability Heatmap and Capability Management; to trace root causes of weak value, Measurement Dependency.

## The concepts, in plain words

The standard has 63 classes (53 you place in a model, 10 abstract parents). The standard writes the names without spaces; the readable form is in `language.yaml`.

### Collaborations, participants and roles

- **Collaboration**: a group of participants joined for a shared purpose. It owns its roles, activities, flows and business items. Four kinds: BusinessNetwork, Community, OrgUnit, CapabilityMethod.
- **Participant** (abstract): anything that can fill a Role: an Actor, a Collaboration, or a Role.
- **Actor, Person**: an indivisible participant, human or not; a Person is a human Actor.
- **Role**: the part a participant plays in one Collaboration. A Role performs Activities, provides and receives ValuePropositions, and can handle store ports.
- **Assignment**: says which Participant fills a Role, or that it is filled dynamically by a resource received on an InputPort. Held by the Collaboration or, for one use only, by a context.
- **BusinessNetwork / Party**: a collaboration among independent economic entities that exchange products, services and money; only Party roles.
- **Community / Member**: a loose association with shared interest (a market segment); only Member roles.
- **OrgUnit / Position**: an organizational collaboration responsible for resources (a company, department, committee); Position roles. The only collaboration that owns Stores and Pools and offers capabilities.
- **CapabilityMethod / Performer**: a shareable activity network that delivers a capability; Performer roles. It owns no resources.

### Activity networks

- **Activity**: work done by one Role inside a Collaboration, with a duration, ports, resource uses, an optional capability requirement and an optional delegation to a sub-collaboration.
- **DeliverableFlow**: the transfer of one BusinessItem from an OutputPort to an InputPort. Tangible (contractual, revenue-bearing) or intangible (informal, relationship-building). Only between two Activities or between an Activity and a Store.
- **BusinessItem**: anything conveyed from provider to recipient: a part, an order, a contract, information, money. Is a resource for one Activity and a deliverable for another.
- **Store / Pool**: a container for one kind of resource, owned by one OrgUnit. A Pool holds reusable resources that come back after use.
- **ResourceUse**: how an Activity uses or consumes a resource from its input ports.
- **Port (InputPort, OutputPort)** and **PortContainer** (Activity, Store, Collaboration): the connection points. **InputDelegation, OutputDelegation** map a delegating Activity's ports to the sub-collaboration's ports, or a Collaboration's ports to ports of its own Activities.

### Values

- **ValueProposition**: the values offered to a recipient Role, expressed as the recipient's satisfaction. Has a provider Role, a recipient Role, components and an optional overall-satisfaction component.
- **ValuePropositionComponent**: the recipient's view of one value: weight (percent) and satisfaction level.
- **ValueAdd**: an Activity's, Store's or Collaboration's contribution to a value, on an output port. May be positive or negative.
- **ValueElement** (abstract): the parent of the two; supports aggregation so a value can be traced to its sources.

### Capabilities

- **Capability** (abstract), **CapabilityDefinition**, **CapabilityCategory**: the ability to do a kind of work. Kept in a CapabilityLibrary, in a hierarchy. **CapabilityDependency**: one capability needs a deliverable another provides.
- **CapabilityOffer**: one OrgUnit's ability to perform a capability, with the methods, stores and pools that support it, and a heat index.
- **ReleaseControl**: how a CapabilityOffer picks the next piece of work (default first come, first served). Mostly for simulation.

### Models, scenarios and contexts

- **ValueDeliveryModel**: the top-level container and unit of exchange; at least one Scenario.
- **Scenario**: the root analysis context: one consistent business use case with its own measurements. One may be the **common** scenario that supplies default measurements.
- **DelegationContext**: created when an Activity delegates to a Collaboration; holds the port delegations and any role assignments for that use. **AnalysisContext** (abstract) is their parent.

### Measurement and core elements

- **MeasuredCharacteristic**: a measurable property of an element. Measurements (from SMM) live in observations, one per context. **MeasurableElement** (abstract) is the set of elements that can have them.
- **VdmlElement** (abstract): root of everything; name, description, Attributes (name-value pairs), Annotations (notes).
- **Expression, Operand**: selects among alternatives (for example a port condition).

### Libraries

Five libraries keep names and definitions consistent: **BusinessItemLibrary**, **ValueLibrary**, **CapabilityLibrary**, **PracticeLibrary**, **RoleLibrary**, each holding definitions and categories (BusinessItemDefinition and BusinessItemCategory, ValueDefinition and ValueCategory, CapabilityDefinition and CapabilityCategory, PracticeDefinition and PracticeCategory, RoleDefinition and RoleCategory).

## Relationships

The standard has no relationship catalog. Its relationships are the 129 associations of the metamodel (listed fully, with roles, multiplicity and containment, in `language.yaml`). In summary:

- **Containment**: a Collaboration contains its Roles, Activities, DeliverableFlows, BusinessItems, internal port delegations and fixed Assignments; a PortContainer contains its Ports; an OutputPort contains its ValueAdds; an OrgUnit contains its Positions, Stores (and Pools), CapabilityOffers and owned CapabilityMethods; a ValueDeliveryModel contains scenarios, collaborations, actors and libraries.
- **Flows**: a DeliverableFlow has exactly one deliverable BusinessItem, one provider OutputPort and one recipient InputPort; each port takes at most one flow.
- **Work and roles**: a Role performs Activities; an Assignment ties one Role to a Participant (or to a resource); a Port may have a handler Role; a ValueProposition has a provider and a recipient Role.
- **Capabilities**: an Activity requires a Capability and may apply a CapabilityOffer; a CapabilityOffer is provided by one OrgUnit and supported by CapabilityMethods and Stores or Pools; a CapabilityMethod is owned by one OrgUnit and supports offers; a CapabilityDependency joins two CapabilityDefinitions through a deliverable.
- **Delegation**: an Activity delegates to a Collaboration through a DelegationContext, which owns the port delegations.
- **Libraries**: elements refer to definitions in libraries; categories nest as parent and child.

## The rules that matter most

The full list, 106 rules with ids, is in `references/rules.md`. The ones to keep in front of you:

- The Role that performs an Activity is in the same Collaboration as the Activity, and Assignments in a Collaboration name Roles of that Collaboration. (VDML-CONT-001 to 003)
- A DeliverableFlow connects two Activities, or an Activity and a Store, never two Stores, and never Activities in different Collaborations. (VDML-FLOW-001, VDML-CONT-007)
- A Store holds one BusinessItem and the flows into and out of it carry that same item. (VDML-FLOW-003)
- Port timing hangs together: a port with an offset is intermediate, an intermediate Activity port has an offset, offsets and resource-use durations fit inside the Activity's duration. Stores and Pools have only intermediate ports; so set the flag explicitly. (VDML-FLOW-004, 009, 010; VDML-MEAS-001 to 003)
- A Role is not assigned to a Participant and a resource at once, not to itself, not to its own Collaboration; a BusinessNetwork has only Party roles and a Community only Member roles. (VDML-ROLE-001, 003, 004, 007, 008)
- A ValueProposition's provider is not its recipient, and its overall satisfaction is one of its components and has no weight. (VDML-VALUE-001 to 003)
- A CapabilityMethod and the offers it supports are for the same Capability. (VDML-CAP-001, 002)
- A model has at most one common Scenario, and the common Scenario has no delegation contexts. (VDML-CTX-001, 002)
- In every library, a category belongs to the same library as its definitions and its parent and child categories. (VDML-LIB-001 to 008)
- Every Activity and Store has a duration; every DeliverableFlow has a deliverable, a provider and a recipient. (VDML-CARD-002, 003)
- Should (warnings): an Activity applies the CapabilityOffer that matches the Capability it requires, and does not delegate straight to a CapabilityMethod but through an OrgUnit's offer. (VDML-CAP-005, 006)
- Drawing: a Role Collaboration diagram never shows a flow between Activities of the same Role. (VDML-DIAG-001, 002)

## Telling similar concepts apart

- **Collaboration or Role.** A Collaboration is the group; a Role is the part one participant plays in it. A Collaboration can itself fill a Role in another Collaboration.
- **Activity or CapabilityMethod.** An Activity is one Role's work inside a Collaboration; a CapabilityMethod is a whole shareable network of activities that an Activity can engage through an OrgUnit's offer.
- **CapabilityDefinition or CapabilityOffer.** A definition is the library's standard name for a kind of ability; an offer is one OrgUnit actually providing it. Several OrgUnits can offer the same capability.
- **Store or Pool.** A Store holds resources that are used up or passed on; a Pool holds reusable resources that return after use (people with a skill, machines).
- **BusinessItem or Store.** The BusinessItem is the kind of thing; the Store is where a quantity of it waits.
- **ValueAdd or ValueProposition.** A ValueAdd is one step's contribution to a value; a ValueProposition is what the recipient gets overall, built from components that aggregate ValueAdds.
- **Tangible or intangible flow.** Tangible: contractual, expected, may generate revenue. Intangible: unpaid, informal, builds the relationship (knowledge, goodwill).
- **Scenario or ValueDeliveryModel.** The model holds the design; each Scenario gives it a set of measurements for one situation, such as current and future state.

## A short example

Westbrook Bank, a fictitious bank, models how a home loan is delivered and what the customer gets.

A BusinessNetwork "Home Loan Exchange" has two Party roles, "Westbrook Bank" and "Home Buyer", and a third, "Appraiser". The Home Buyer Party is filled by a Community "Home Buyers" (a market segment). Westbrook Bank sends the "Loan Offer" and receives the "Loan Application"; the Appraiser sends the "Appraisal Report". Each flow is a DeliverableFlow; the Loan Offer is tangible, the "Closing Guidance" the Bank also sends is intangible. On a Role Collaboration diagram you see the three Roles and these flows. A ValueProposition Exchange diagram adds the "Home Loan Proposition" that Westbrook Bank provides and Home Buyer receives, built from components such as "Speed to decision" and "Rate", with the buyer's weights and satisfaction levels.

Inside Westbrook Bank, an Activity Network in the Bank's own Collaboration has Activities "Take application", "Assess credit" and "Issue offer", each performed by a Role. A Store "Application queue" sits between the first two. "Assess credit" requires the Capability "Credit assessment" and delegates to the CapabilityMethod "Standard credit assessment" through the Credit Risk OrgUnit's CapabilityOffer. Each Activity adds a ValueAdd (for example processing time and cost) on its output port, and the Bank's Collaboration aggregates them into the components of the Home Loan Proposition.

A Collaboration Structure diagram shows Westbrook Bank as an OrgUnit with a Position "Head of Credit Risk" assigned to the Credit Risk OrgUnit. A Capability Management diagram shows that OrgUnit's CapabilityOffer for "Credit assessment" supported by the method and a Pool "Credit analysts". A Capability Heatmap flags "Credit assessment" when the offer's heat index passes the Scenario's threshold.

This is an illustration. Use your own enterprise's roles, flows, capabilities and measures.

## Data types and attributes

Coverage is partial. The standard has no data-type clause. Its property tables use Boolean and String by name without defining them, and it defines one enumeration, Influence (positive or negative), on the relationship between two measurements (8.9). Percentages must be measured in percent (7.2.1.3.2, 7.2.4.3.1). Durations, quantities, offsets, weights and similar values are not VDML types: they are measurements of a MeasuredCharacteristic, defined by SMM. Attributes sit on 18 concepts; the ones that matter most are `isTangible` on DeliverableFlow, `isIntermediate` on Port and `isCommon` on Scenario. Every element also has a required name and description. The list is under `data_types` and, per concept, under `attributes` in `language.yaml`.

## How it is drawn

Coverage is normative, in clause 8, and limited: eight diagram kinds, colors carry no meaning. A Role is an oval, or a swim-lane in an Activity Network. A Collaboration is a square-cornered rectangle with a small glyph for its kind (network, organization unit, method, community). An Activity is a rounded rectangle; a Store is a downward triangle, and a Pool adds a circular arrow. Ports are small squares on the boundary, filled when they carry a ValueAdd. A DeliverableFlow is a solid arrow, dashed in the role view when intangible. A Capability is a rectangle, a CapabilityOffer a stretched hexagon, a ValueProposition a small square. Party, Member, Performer and Person have no shape of their own, and most library, context and measurement concepts have none either. Every shape, marker and line is described under `notation` in `language.yaml`.

Sizes and spacing come from `../_languages/layout-standard.yaml`; the mapping of each concept to a size class is the `layout` block in `language.yaml`.

## References

- `references/standard.md`: the standard section by section, in our own words, with citations.
- `references/rules.md`: all 106 rules with stable ids (`VDML-<CAT>-nnn`), strength and source section.
- `language.yaml`: the machine-readable form: concepts, the 129 associations with roles and multiplicity, the eight diagram types with what each admits and its notation, and the rules.
