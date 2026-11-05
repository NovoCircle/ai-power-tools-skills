# The Value Delivery Modeling Language 1.0, section by section

This is a summary of the OMG specification in our own words. It is not a substitute for the specification, and it does not reproduce its text; the few short quoted phrases are cited. Clause and annex numbers are the specification's, as numbered in the body of the document (its table of contents numbers the class clauses differently). "p." is the printed page number. Where the standard is silent or inconsistent, this file says so rather than filling the gap.

Source: Object Management Group, *Value Delivery Metamodel (VDML)*, version 1.0, formal/2015-10-05, October 2015, with the normative machine-readable model vdml.xmi (https://www.omg.org/spec/VDML/1.0/). A newer version, 1.1 (March 2018), exists and is not covered here.

## 1. What the standard is

**Identity.** VDML is an OMG standard in the Business Modeling domain, version 1.0, published October 2015 under a non-assert intellectual property mode. It was submitted by two companies and developed with business-network and capability specialists (clause 6). It is a formal standard: a metamodel with a limited normative graphical notation.

**Purpose (1.1).** A standard language for analyzing and designing how an enterprise operates, with the focus on creating and exchanging value. It abstracts the operation of the enterprise for business executives and carries supporting detail for analysts, so that strategy and business models can be linked to the activities, roles and capabilities that run the enterprise. Four challenges are named: modeling tangible and intangible value flows, modeling complex collaborations and business networks, modeling business activity flexibly in high-variability settings, and sharing capabilities across the business.

**What it is not (1.1).** It is not a business process language. It provides a view different from process modeling by concentrating on the consumption and production of deliverables and on the statistical performance and value contribution of activities (cost, quality, duration), and it avoids the operational control detail of processes. It does not simulate, but its metamodel is meant to carry the data a simulation needs. It does not define the measures themselves: it relies on a second standard (SMM, the Structured Metrics Metamodel) for measure libraries and measurements.

**Central idea (7.1).** A *Collaboration* of *Participants* in *Roles* performs *Activities* that exchange *BusinessItems* as *DeliverableFlows*; each Activity contributes *ValueAdds*, which are aggregated into the *ValuePropositions* delivered to recipients; the *Capabilities* that the Activities need are offered by *OrgUnits* and defined in a *CapabilityLibrary*; *Scenarios* give the same model different sets of measurements.

## 2. Conformance (clause 2)

Three levels. **Full VDML conformance (2.1)** supports the normative graphical notation and imports and exports models that follow the metamodel and SMM. **VDML Metamodel conformance (2.2)** imports and exports the model interchange form without implementing the notation; it is a subset of the first. **VDML Collaboration Modeling conformance (2.3)** is a further subset for organizational structures: it implements only 22 classes (ValueDeliveryModel, VdmlElement, MeasurableElement, Attribute, Annotation, MeasuredCharacteristic, PortContainer, Collaboration, Role, RoleDefinition, RoleLibrary, RoleCategory, Participant, Actor, Person, Assignment, OrgUnit, Position, Community, Member, BusinessNetwork, Party), and associations from those to other classes may have multiplicity zero and be ignored.

Annex A (glossary) is normative; Annexes B and C are informative (clause 8 introduction to the annexes, p. 107).

## 3. How the metamodel is organized (clause 7)

The metamodel is a single package, VDML, that imports the SMM package (7.2.6.1). It has 63 classes: 53 concrete and 10 abstract. The standard groups them as: collaboration and value creation (collaborations and participants, activity networks, values and value propositions); collaboration sub-types; models and scenarios; core elements; libraries; and the link to SMM (7.2). Clause 7.1 first explains each cluster informally; 7.2 gives the class definitions with properties and constraints.

**Relationships.** The standard has no relationship catalog. Its relationships are the associations of the metamodel, shown in the figures and in each class's property table. The 129 associations are in `language.yaml`. About half are compositions (a container owning its parts).

**Constraints.** Stated in prose, under each class, as "Constraints" bullets. The metamodel file contains none. They are listed with ids in `rules.md`.

## 4. Models, scenarios and contexts (7.1.1, 7.1.13, 7.2.3)

**ValueDeliveryModel (7.2.3.1.1).** The entry point and top-level container of one VDML model: scenarios, collaborations, actors, and the five kinds of library. It is the unit of model exchange. A model has at least one Scenario and at most one *common* Scenario. Containing something in a model does not stop other models from referring to it; the standard says models enable re-use. The text names AnalysisContext as its superclass; the machine-readable model names VdmlElement.

**AnalysisContext (abstract, 7.2.3.2.1).** The set of measurements of one particular use of one or more Collaborations, or of Stores used as decoupling points between them. Each context has its own SMM Observation, so a measured characteristic can have different measurements in different contexts. It can also hold *context-based Assignments* (role assignments that apply only in this context). Contexts form a tree with a Scenario at the root.

**Scenario (7.2.3.2.2).** The root context: a consistent business use case with its own measurements and possibly different delegations. Properties: `type` (free text such as as-is or to-be), `isCommon`, `horizon`, `heatThreshold`, `contextCollaboration` (the top-level collaborations in scope), `contextActor`, release controls. The *common* Scenario supplies initial measurements for any measured characteristic until a context gives its own. It may not contain delegation contexts or have context stores, context collaborations or release controls.

**DelegationContext (7.2.3.2.3).** Created when an Activity delegates its work to a Collaboration (usually a CapabilityMethod). It names the Collaboration (`contextCollaboration`) and the Activity (`delegatedActivity`), holds the port delegations for that use, and may hold role assignments. A delegation context is owned by its parent context. One Collaboration can thus be used in several places in one Scenario, each with different measurements and assignments.

Two uses of the same Collaboration within one use of another are illustrated in Figure 7.4 (7.1.13); scenarios and context trees in Figure 7.5.

## 5. Collaborations, participants and roles (7.1.4, 7.2.1.1)

**Collaboration (7.2.1.1.3).** The fundamental organizational concept: several Participants, each in a Role, working together for a shared purpose. A Collaboration contains its Roles, its Activities, its DeliverableFlows, its BusinessItems, its internal port delegations and the fixed Assignments of its Roles. It is both a Participant and a PortContainer. It has four sub-types (section 6 below). A Participant's own Roles can in turn fill Roles elsewhere ("roles in roles").

**Participant (abstract, 7.2.1.1.4).** Anything that can fill a Role: an Actor, a Collaboration, or a Role. It may be named in the model or determined dynamically from a resource.

**Actor, Person (7.2.1.1.1, 7.2.1.1.2).** An Actor is an individual (indivisible) Participant, human or not. A Person is a human Actor.

**Role (7.2.1.1.5).** An expected pattern of behavior or capability profile tied to participation in one Collaboration. Properties: `isLead`; link to a `roleDefinition` in a role library; the Activities it performs (`performedWork`); the Ports it handles; the ValuePropositions it provides and receives; its Assignments. A Role in the Collaboration where it is contained performs that Collaboration's Activities. Constraints: the Activities a Role performs must be in the same Collaboration that contains the Role; an Assignment contained in a Collaboration must name a Role that Collaboration contains; an InputPort that provides the resource a Role is assigned to must belong to an Activity performed by that Role; the Ports a Role handles must be Store ports.

**Assignment (7.2.1.2.3).** Says how a Role is, or can be, filled. It names one Role and at most one Participant (an OrgUnit, Position, Actor or another Role), or instead one or more InputPorts whose received resources determine the Participant at run time (`roleResource`). Held in the Collaboration (context-independent) or in an AnalysisContext (context-dependent). Constraints: not both a Participant and a roleResource; a Role not assigned to more than one Collaboration-Participant unless the extra Assignments are context-based; a Role not assigned to itself, directly or indirectly, nor to its containing Collaboration; BusinessNetworks and CapabilityMethods may not be Participants in Positions or Members; BusinessNetworks may not be Participants in Performers.

**CalendarService (7.2.1.1.6).** A placeholder for the calendar that decides when a resource is available. Needed only for simulation; the calendar's structure is out of scope.

## 6. Collaboration sub-types (7.1.5 to 7.1.8, 7.2.2)

VDML defines four specializations of Collaboration. Each adds meaning and limits which Roles can occur.

- **BusinessNetwork (7.2.2.1.1) and Party (7.2.2.1.2).** A collaboration among independent economic entities that exchange products, services and usually money; its Roles are *Party* roles only. It can nest other BusinessNetworks. A Party role can be filled by a company, an agency, an individual, or a Community representing many similar entities of which one takes part in a given exchange. Value propositions sent and received by each Party determine the net value of taking part.
- **Community (7.2.2.2.1) and Member (7.2.2.2.2).** A loose association with a shared interest (a market segment, a professional body, a standards group); its Roles are *Member* roles only.
- **OrgUnit (7.2.2.3.1) and Position (7.2.2.3.2).** An administrative or functional organizational collaboration with responsibility for defined resources: a company, business unit, department, or a less formal committee, project or task force. It has *Position* roles (defined job positions, which may be vacant) and is the only collaboration type that owns resources (Stores and Pools), owns CapabilityMethods, and offers capabilities through CapabilityOffers. Typical organizations are hierarchies, but a Position can also fill roles in other OrgUnits.
- **CapabilityMethod (7.2.2.4.1) and Performer.** A shareable collaboration specification (activities, flows, business items, capability requirements, roles) that delivers a capability and its value contributions. Its Roles are *Performers* (a name the standard uses but defines no clause for). It owns no resources. It is owned by one OrgUnit, but other OrgUnits may apply it to support their own offers. An Activity does not delegate straight to a CapabilityMethod; the OrgUnit that fills the Activity's Role uses the method through its CapabilityOffer (Annex A, Capability Method). A CapabilityMethod can be viewed as a case type of case management.

## 7. Activity networks (7.1.9 to 7.1.11, 7.2.1.2)

**Activity (7.2.1.2.1).** Work contributed to a Collaboration by one Role. It sits in a network joined by DeliverableFlows. Properties: `performingRole`; `capabilityRequirement` (a Capability from a library); `appliedCapabilityOffer` (the offer chosen when several match); `delegationContext` (where it delegates its work); `resourceUse`; `implementedPractice`; a required `duration`; an optional `recurrenceInterval` (pace of a scheduled activity). Constraints: the performing Role is in the same Collaboration; resource-use durations and port offsets are not longer than the Activity; an Activity that receives inputs other than from Stores has no recurrence interval; a ResourceUse relates only to ports of its own Activity; when several role-resource InputPorts exist, either a ResourceUse relates them or each delegation context assigns the Role to one of them.

**ResourceUse (7.2.1.2.2).** How an Activity uses or consumes a resource it receives on InputPorts: the quantity, whether it is consumed or reusable, whether alternatives are exclusive, a condition, a planning percentage, a duration, and optionally an output it depends on (`deliverable`). Only resources received from Stores can have a ResourceUse. Whether the activity is pulled by other inputs or pushed by the resource is set by `inputDriven`.

**DeliverableFlow (7.2.1.2.4).** The transfer of one BusinessItem from an OutputPort (provider) to an InputPort (recipient). `isTangible` true means something contracted or expected by the recipient that may generate revenue; false means unpaid, non-contractual, relationship-building. Optional duration (delay between provider and recipient) and channel (mechanism such as e-mail, REST, mail). It connects ports of two Activities, or a port of an Activity and a port of a Store, never two Stores, never ports of Activities in different Collaborations, and a flow into or out of a Store has no duration.

**BusinessItem (7.2.1.2.5).** Anything that can be acquired or created that conveys information, an obligation or other value: parts, products, orders, emails, contracts, currency. A class of things that is a resource for one Activity and a deliverable for another. `isFungible` and `isShareable` say whether instances are interchangeable and usable in several places at once. It can point to a BusinessItemDefinition in a library.

**Store (7.2.1.2.6) and Pool (7.2.1.2.7).** A Store is a container of one kind of resource (identified by a BusinessItem), owned by one OrgUnit, with a required duration (time resources stay) and an optional inventory level. The BusinessItem that flows into or out of it must be the one it holds. A Pool is a Store of *reusable* resources that return after use; it adds a pool size, the Positions of the Actors that belong to it, and a calendar. A Pool's inventory level may not exceed its pool size, and Positions associated with a Pool may not be assigned to Collaborations. Non-fungible resources in a Store are matched to business items by an expression; in non-simulated models a Store carries only average size and holding period.

**Resources (7.1.11).** A resource is anything an Activity uses or consumes. The standard advises modeling only resources that matter to a high-level analysis.

## 8. Ports and delegations (7.1.10, 7.2.4.3, 7.2.4.4)

**PortContainer (abstract, 7.2.4.3.4)** is anything that carries ports: Activity, Store, Collaboration.

**Port (abstract, 7.2.4.3.1), InputPort (7.2.4.3.3), OutputPort (7.2.4.3.2).** The connection points for inputs and outputs. DeliverableFlows link ports. OutputPorts carry the ValueAdds delivered with that output. Properties: `isIntermediate` (whether the port may be used at any time, or only at the start of an input or end of an output), `offset` (time from activity start to receipt of an input, or from delivery of an output to completion), `planningPercentage` (probability of use), `condition`, `batchSize`, `handler` (the Role responsible for the port), `inputDefinition` and `outputDefinition` (library elements that define the type handled). InputPorts may have a `correlationExpression` selecting the instance of a non-fungible item. Constraints include: Collaboration ports have no planning percentage, condition, batch size or offset; Store ports have no offset; a port with an offset must be intermediate and an intermediate port of an Activity must have an offset; Stores and Pools (and Collaborations other than CapabilityMethods) may not have ports with isIntermediate false; planning percentage is measured in percent.

**PortDelegation (abstract, 7.2.4.4.1), InputDelegation (7.2.4.4.2), OutputDelegation (7.2.4.4.3).** Map a port of a delegating Activity to a port of the Collaboration it delegates to (inside a DelegationContext), or map a port of a Collaboration to a port of an Activity inside it (the Collaboration's own internal delegations). Ports of a Collaboration act as an interface that hides its internal organization. An Activity port inside a Collaboration may not be mapped to more than one port of that Collaboration. Through delegation, the ValueAdds entering a delegating Activity are inputs to the sub-collaboration and its ValueAdds become the Activity's outputs.

## 9. Values and value propositions (7.1.2, 7.2.1.3)

**Value (7.2.1.3, 7.1.2).** A measurable factor of benefit, of interest to a recipient, in association with a BusinessItem. It may be intrinsic to a deliverable (composition, performance) or conveyed by it (price, a warranty, environmental impact). Different recipients may be more or less satisfied with the same measurement.

**ValueProposition (7.2.1.3.1).** The values offered to a recipient, evaluated as the recipient's satisfaction. It has a provider Role and a recipient Role (never the same), components, and an optional overall-satisfaction component, which is one of its own components and has no weight. It can be compared to a competitor's.

**ValuePropositionComponent (7.2.1.3.2).** The recipient's view of one value: its relative importance (`percentageWeight`, in percent) and satisfaction level. It aggregates from ValueAdds and other components.

**ValueAdd (7.2.1.3.3).** The contribution of an Activity, Store or Collaboration to a value, attached to one of its OutputPorts; positive or negative; may aggregate from other ValueAdds.

**ValueElement (abstract, 7.2.1.3.4).** The parent of the two. It enables value aggregation (`aggregatedFrom`, `aggregatedTo`), so a delivered value can be traced back to its sources, and can refer to a ValueDefinition, a `valueMeasurement` and benchmarks. `isAtomic` controls whether an element can be aggregated from elements of the same kind of value. Three constraints govern atomic and non-atomic elements.

## 10. Capabilities (7.1.3, 7.2.2.3.3, 7.2.5.3)

**CapabilityOffer (7.2.2.3.3).** The ability of one OrgUnit to do a kind of work, using resources that it manages together and possibly capability methods. It is owned and provided by exactly one OrgUnit. It can name the Capability it offers, the CapabilityMethods and Stores or Pools that support it, release controls, a location, and a `heatIndex` (a measure compared with the Scenario's `heatThreshold` to flag capabilities needing attention). Multiple OrgUnits may offer the same capability, which opens opportunities to consolidate.

**ReleaseControl (7.2.2.3.4).** The strategy that sets which waiting Activity instance a CapabilityOffer starts next. The default is first come, first served. Mainly for simulation.

**Capability (abstract), CapabilityDefinition, CapabilityCategory (7.2.5.3.2 to 7.2.5.3.4).** A capability is the ability to perform a kind of work and deliver desired value. A library entry is either a definition or a category, and requirements and offers may refer to either (a requirement can start at category level and be refined to a definition). Definitions and categories form a hierarchy (`parentCapability`, `childCapability`).

**CapabilityDependency (7.2.5.3.5).** A possible dependency between two capabilities: one needs a deliverable the other provides (the `deliverableDefinition`). It may suggest a flow between activities. `isFromExternalSource` and `isForExternalTarget` mean the source or target is not named explicitly (a Store or delegation supplies or receives it); then the matching definition must not be connected.

**CapabilityLibrary (7.2.5.3.1).** The taxonomy of capabilities and dependencies; the basis for a capability map or heat map.

## 11. Core elements (7.2.4.1, 7.2.4.2)

**VdmlElement (abstract).** The root of all classes: a name, a description, an optional `represents` reference (to something in another model or system), user Attributes and Annotations. **Attribute** is a name-value pair; **Annotation** is a text note. **MeasurableElement (abstract)** is the subset of elements that can carry user-defined **MeasuredCharacteristics**; a MeasuredCharacteristic is defined against an SMM Characteristic and its Measurements live in Observations, one per AnalysisContext. When a characteristic has more than one measurement, each is in a separate observation and context. VDML narrows SMM so that measurements attach only to MeasuredCharacteristics.

**Expression, Operand (7.2.4.2).** An Expression is a statement that evaluates over model objects without changing them and selects among alternatives (a port condition, a correlation, a resource-use condition). Its Operands are MeasuredCharacteristics under optional aliases.

## 12. Libraries (7.1.15, 7.2.5)

Five library kinds, each a taxonomy of definitions and categories that keeps a concept named and defined the same everywhere in a model: **BusinessItemLibrary** (with BusinessItemDefinition, BusinessItemCategory; BusinessItemLibraryElement is the abstract parent so ports can refer to either), **ValueLibrary** (ValueDefinition, ValueCategory), **CapabilityLibrary** (above), **PracticeLibrary** (PracticeDefinition, PracticeCategory) and **RoleLibrary** (RoleDefinition, RoleCategory). A practice is a proven way of handling a type of work. In every library a category and its parent and child categories, and a definition and its categories, must belong to the same library. Elements that refer to the same definition are considered similar. Shared industry libraries with local extensions are expected. Libraries are optional; they can carry suggested characteristics for the things they define.

## 13. Measurement and SMM (7.1.12, 7.2.6)

VDML relies on SMM for measures. A *Measure* is a method that characterizes an attribute by a comparable quantification or qualification; a *Characteristic* is the feature measured; a *Measurement* is the result; *Observations* group measurements. A VDML element may have different measurements for the same measured characteristic in different analysis contexts. Measurements describe statistical values per unit of production over a period, so where related collaborations have different units of production (for example one tire versus one automobile) the values must be adjusted. The details of SMM are not repeated in VDML.

## 14. Notation (clause 8)

Eight diagram kinds, each with its own shapes (8.1 lists them). Shapes are described in `language.yaml` under each diagram type.

1. **Role Collaboration (8.2).** Roles as ovals joined by flows; the Activity detail is left out. A flow between Activities of one Role, or between an Activity and a Store port that the same Role handles, must not be drawn. An expand button on a Role oval means it is assigned to a Collaboration.
2. **ValueProposition Exchange (8.3).** A more abstract view: Roles and the ValuePropositions they provide and receive.
3. **Activity Network (8.4).** Roles as swim-lanes, Activities, Stores, Pools, flows, port shapes with variants, internal port delegations (dotted).
4. **Collaboration Structure (8.5).** Collaborations (with a marker per sub-type), Roles contained by them, and assignment of Roles to Participants; can represent an organization structure.
5. **CapabilityLibrary (8.6).** A capability map; hierarchy by containment.
6. **Capability Heatmap (8.7).** The same, with thick borders where offers' heat index reaches the threshold.
7. **Capability Management (8.8).** OrgUnits with their CapabilityOffers on the boundary and supporting methods, Stores, Pools and Positions inside when expanded. Positions associated with Pools should not be shown inside the OrgUnit; unassigned Positions may be.
8. **Measurement Dependency (8.9).** MeasuredCharacteristics as thin rectangles and MeasurementRelationships as connectors with a plus or minus marker for positive or negative influence.

Colors in the examples carry no meaning. The notation is expected to evolve, and tabular displays are expected to complement it (1.1, 8.1).

## 15. Annexes

**Annex A (glossary, normative)** defines 39 terms in VDML's context and says where each term comes from. **Annex B (informative)** shows how VDML concepts line up with other techniques: value networks, REA, e3value, capability maps, value streams, the business model cube and canvas, POA, strategic planning (BMM), balanced scorecard and strategy maps, and BPMN. **Annex C (informative)** points to two use cases (manufacturing, healthcare) in separate OMG documents, developed before the metamodel was final.

## 16. Where the standard is silent or inconsistent

- The table of contents numbers the class clauses differently from the body.
- The text and the machine-readable model disagree on the superclass of ValueDeliveryModel and, in the class clause, of Collaboration; property tables are displaced by page breaks. The machine-readable model is followed for the shape of the model and the text for meaning and constraints.
- `Performer` has no class clause.
- The `isIntermediate` default (false) conflicts with the constraint that Stores and some Collaborations may have no non-intermediate ports.
- The heat threshold is "beyond" in 7.2.2.3.3 and "equal to or above" in 8.7.
- The standard says nothing about which tangible value or price a flow carries beyond `isTangible`; measures come from SMM libraries that the standard does not define.
