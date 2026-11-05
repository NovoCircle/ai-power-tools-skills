---
name: updm-2
description: The OMG Unified Profile for DoDAF and MODAF (UPDM) 2.1, a UML profile for describing enterprise and system-of-systems architectures once and producing both DoDAF 2.02 and MODAF 1.2 views from it - capabilities and enterprise phases, operational nodes, activities, needlines and exchanges, systems resources, functions and interfaces, services, organizations, posts and actual persons, projects and milestones, standards and forecasts, measurements and environments. Use when someone is modeling with UPDM, DoDAF, MODAF or NAF, builds views such as AV-1, OV-1, OV-2, OV-5, SV-1, SvcV-1, CV-2, StV-2, PV-2, StdV-1 or TV-1, or asks what a node, performer, capability, needline, operational exchange, capability configuration, resource interaction or milestone allows, how DoDAF and MODAF views map to each other, or how UPDM relates to UML, SysML and UAF.
---

# Unified Profile for DoDAF and MODAF (UPDM) 2.1

UPDM is the Object Management Group's UML profile for describing the architecture of an enterprise or a system of systems the way two defense frameworks require: the US DoDAF (version 2.02) and the UK MODAF (version 1.2). It defines one set of elements and produces the views of both frameworks from it. It is not a method and it defines no drawing notation: views are UML and SysML diagrams that show UPDM elements.

**UPDM has been replaced.** The Unified Architecture Framework (UAF) is its successor; use the `uaf-1` skill for UAF. This skill describes UPDM 2.1 as published (version 2.1.1 of 2017, also ISO/IEC 19513, is a later edition and is not described).

**It builds on other languages.** UPDM elements extend UML elements (classes, properties, dependencies, information flows, connectors, activities, state machines, interactions). Level 1 also imports SysML. Level 0 imports ten SoaML elements. This skill does not repeat their rules; use the `uml-2`, `sysml-1` and `soaml-1` skills for them.

## What you are creating

An *architectural description*: a package of **views**, each made to a **viewpoint**, over one set of shared elements. A node named in an operational view is the same element a systems function is implemented against and a capability is exhibited by. Four ideas hold the language together:

1. **Types and actual things.** Most concepts are types (Organization, Post, Person, ProjectType). Their instances carry an `Actual` prefix (ActualOrganization, ActualPost, ActualPerson, ActualProject). An actual element is classified by its matching type.
2. **Logical and solution.** Operational elements (Node, OperationalActivity, OperationalExchange) are the logical architecture and are independent of materiel. Systems elements (SystemResource and its kinds, Function, ResourceInteraction) are the solution that implements them. Services sit between. `Implements` ties the two.
3. **One model, two vocabularies.** The Core elements serve both frameworks. Where DoDAF and MODAF name a concept differently, the profile defines it once and gives the other framework's name as an alias (Performer for Node, System for ResourceArtifact, Skill for Competence, Vision for EnterpriseVision). An alias is a specialization with no rules of its own. The architectural description records the framework in use (DoDAF, MODAF or NAF) and only that framework's aliases may be used.
4. **Roles and the things that play them.** A part used inside another element is a *role* (NodeRole, ResourceRole, ConceptRole, ProjectMilestoneRole); it has an owner and a type.

## Compliance levels

- **Level 0:** UPDM over UML 2, with ten imported SoaML elements.
- **Level 1:** everything in level 0, plus the whole SysML profile, plus 39 rules that pair a UPDM element with a SysML one (for example a Capability is also a SysML Block, an OperationalExchange is also an ItemFlow, a NodePort is also a FlowPort, an EnterpriseGoal is also a Requirement). Rule ids UPDM-SYS-001 to 039.

## Views: DoDAF models and MODAF views on one profile

The standard does not define diagram types. It defines the elements, and Annex B describes 47 *products* that realize the 52 DoDAF 2.02 models and the 47 MODAF 1.2 views. Each product below gives the DoDAF and MODAF names that share it, and the concern.

| Viewpoint (DoDAF / MODAF) | Products | What they show |
|---|---|---|
| All (AV / AV) | AV-1, AV-2, Environment Elements, Measurements | Overview and summary information; the integrated dictionary of terms and aliases; environments; measurable properties. |
| Capability / Strategic (CV / StV) | CV-1/StV-1 to CV-6/StV-6, CV-7 | Vision, capability taxonomy, phasing over time, dependencies, mapping to organizations or deployment, mapping to operational activities; CV-7 maps services to capabilities. |
| Operational (OV / OV) | OV-1, OV-2, OV-3, OV-4 Actual, OV-4 Typical, OV-5, OV-6a, OV-6b, OV-6c, OV-7/DIV-1/DIV-2 | High-level operational concept; nodes and their needlines; operational exchanges; organizations and posts; the activity model; rules, state transitions and event traces; information and logical data models. DoDAF splits OV-5 into 5a and 5b; MODAF splits OV-1 into 1a, 1b, 1c. |
| Systems (SV, SvcV / SV) | SV-1/SvcV-1 to SV-9/SvcV-9, SV-10a/b/c, SV-11/DIV-3, SV-12 | Resource composition and interaction; ports, flows and protocols; matrices; functionality; traceability from operational activities; performance measures; evolution over time; technology and skills forecast; constraints, state transitions and event traces; the physical data model; service provision and composition. |
| Service (SvcV, CV-7 / SOV) | SOV-1 to SOV-5 (4a, 4b, 4c) | Service taxonomy, interface specification, constraints, states, interactions and functionality. MODAF services are specifications; DoDAF services describe implementations in performers, so the two map only partly. |
| Project / Acquisition (PV / AcV) | AcV-1/PV-1, AcV-2/PV-2, PV-3 | Projects and their organizations; timelines and milestones; the capabilities a project delivers. |
| Standards (StdV / TV) | TV-1&2/StdV-1&2 | The standards profile and the standards forecast. |

Views present only in one framework: DoDAF has PV-3, DIV-1 and the SV-5a/5b split; MODAF has SOV-1 to SOV-5, SV-2a/2b/2c, SV-12a/12b and OV-1a/1b/1c. Table C.3 of the standard (in `language.yaml`, `view_mapping`) gives the model-by-model correspondence. UPDM also allows user-defined views.

The `language.yaml` file lists each product with its concern and the key concepts its description points to. The standard's figures that list exactly which elements each view admits are images, so the key concepts are a guide, not a closed list.

## The concepts, by area

The profile has 226 elements (33 abstract groupings). The readable lists are in `references/standard.md`; every element with its generalization, base, attributes and definition is in `language.yaml`.

- **Architecture description:** ArchitecturalDescription, Viewpoint, View, ArchitecturalReference, Metadata, ArchitectureMetadata; ontology links (OntologyReference, ExternalType, SameAs, Overlap, Alias, Definition).
- **Strategic:** EnterprisePhase (with TemporalPart, StructuralPart, WholeLifeEnterprise), EnterpriseVision, EnterpriseGoal, EnduringTask, Capability, CapabilityProperty, Exhibits, MapsToCapability, DesiredEffect.
- **Operational structure:** Node (alias Performer), SecurityDomain, NodeRole, NodePort, Needline, LogicalArchitecture, ProblemDomain, KnownResource, HighLevelOperationalConcept, ConceptRole, Mission, OperationalConstraint.
- **Operational behavior and flows:** OperationalActivity (and StandardOperationalActivity), its actions, edges and parameters, NodeOperation, OperationalStateDescription, OperationalEventTrace, OperationalMessage, OperationalExchange, Command, Control.
- **Organization:** Organization, Post, Person, Responsibility, RoleType, Competence and ProvidesCompetence/RequiresCompetence; the actual forms ActualOrganization, ActualPost, ActualPerson, FillsPost.
- **Systems:** SystemResource kinds (ResourceArtifact with Software and Materiel, Organization, Post, CapabilityConfiguration), ResourcePort, ResourceInterface, ResourceConnector, ResourceInteraction, Function, ResourceStateMachine, ResourceEventTrace, WholeLifeConfiguration, FieldedCapability, Forecast, ResourceConstraint.
- **Services:** ServiceInterface, ServicePort (Service, Request), ServiceOperation, ServiceFunction, ServiceInteraction, ServiceStateMachine, ServiceLevelValueSet, ServicePolicy, ServiceAccess.
- **Acquisition:** ProjectType, ActualProject, ProjectMilestone and ActualProjectMilestone (IncrementMilestone, DeployedMilestone, NoLongerUsedMilestone, OutOfServiceMilestone), ProjectTheme, ProjectStatus, ProjectSequence, ProjectActivity.
- **Standards and data:** Standard (TechnicalStandard, FunctionalStandard, Protocol), ProtocolLayer, LogicalDataModel, PhysicalDataModel, EntityItem, EntityAttribute, EntityRelationship, ExchangeElement.
- **Measurements and environment:** MeasurementSet, Measurement, ActualPropertySet, ActualMeasurement, Environment, LocationType, ActualLocation, GeoPoliticalExtent.
- **Information exchange (SOPES) and design rules (SwAF):** Semantic, Transactional, Wrapper, Contract; DesignRule.

### Telling similar concepts apart

- **Node or SystemResource.** A Node is a logical operational entity; a SystemResource is the physical, organizational or functional resource that realizes it. A CapabilityConfiguration is the composite of resources configured to give a capability.
- **OperationalActivity or Function.** An OperationalActivity is work, independent of how it is done; a Function is an activity in the context of the resource that performs it. A Function `Implements` an OperationalActivity.
- **Needline or OperationalExchange.** A Needline is the requirement to exchange between nodes (a connector); an OperationalExchange is the flow it bundles.
- **Capability or Function.** A Capability is a high-level ability, timeless; it is exhibited by a capable element and reached by mapping activities to it.
- **Organization (type) or ActualOrganization.** The type defines the kind of group; the actual element is a specific real one, classified by its type.
- **Alias or Core element.** DoDAF and MODAF names that are aliases add no rules; apply the rules of the element they alias.

## Relationships in summary

Thirty-six elements are relationships; each fixes the kinds of element at each end. The full list with ends is in `language.yaml` (`relationships`). The ones used most:

- **Exhibits:** a capable element (node, resource, enterprise phase) provides a Capability. **MapsToCapability:** an Activity is part of a Capability.
- **IsCapableOfPerforming:** a Node, SystemResource or ServiceInterface to an OperationalActivity, Function or ServiceFunction. **Implements:** solution side to logical side.
- **OperationalExchange:** Node to Node, conveying what its kind says. **ResourceInteraction:** SystemResource to SystemResource. **Needline, ResourceInterface, ResourceConnector:** connectors with fixed end roles.
- **FillsPost:** ActualPerson to ActualPost. **ProvidesCompetence / RequiresCompetence:** to a Competence.
- **Acquisition:** ProjectSequence, MilestoneSequence, OrganizationalProjectRelationship, ActivityPartOfProject.

No multiplicity is stated for any relationship; each is many-to-many and optional at both ends.

## The rules that matter most

The full list, 264 rules, is in `references/rules.md`. Read each "must be X" as "X or a specialization of X". The ones to keep in front of you:

- **Do not apply an abstract element directly.** Thirty-three are abstract groupings. (UPDM-GEN-006)
- **Relationship ends.** A relationship connects only the kinds the profile lists: Exhibits ends at a Capability; MapsToCapability starts from an Activity; FillsPost joins ActualPerson to ActualPost; OperationalExchange joins Nodes; ResourceInteraction joins SystemResources; Needline ends are NodeRoles or NodePorts. (UPDM-END-nnn)
- **An operational exchange conveys what its kind says:** information exchange an ExchangeElement, materiel a ResourceArtifact, energy an Energy, organizational an OrganizationalResource, configuration a CapabilityConfiguration, geo-political a GeoPoliticalExtent. (UPDM-XCH-001 to 006)
- **Typing.** A NodeRole is typed by a Node, a ResourceRole by a SystemResource, a NodePort by an operational exchange item, a ResourcePort by a resource interaction item; an ActualPost is classified by a Post, an ActualOrganization by an Organization. (UPDM-TYP-nnn)
- **Ownership.** A Node owns NodePorts (or service ports) and NodeOperations; an OperationalActivity's parameters are OperationalParameters; a Function's parameters are ResourceParameters; a ServiceInterface's features are ServiceFeatures. (UPDM-OWN-nnn)
- **Aliases follow the framework.** If the framework is DoDAF only DoDAF aliases may be used; if MODAF, only MODAF aliases; if unset, none. (UPDM-GEN-001)
- **At level 1, pair with SysML:** Block, ValueType, ItemFlow, FlowPort, Requirement as listed. (UPDM-SYS-001 to 039)
- **Milestones keep an order the framework does not enforce:** increment, then deployed, then no longer used, then out of service. These are warnings. (UPDM-VIEW-006 to 010)
- **Only one strategic view across a set of descriptions; populate the All views whenever the description changes.** Warnings. (UPDM-VIEW-001, 002)

## Data types and attributes

Partly defined by the standard (`coverage: partial`). UPDM has no primitive types of its own: attributes use String, Boolean and the other types of the `uml-2` skill. It adds one date-time type, ISO8601DateTime (8.3.1.1.3), twelve enumerations (for example RoleKind, RuleKind, OperationalExchangeKind and ArchitectureFrameworkKind, each with its literals) and the security classification enumeration of the DoDAF class library (8.2.1). The seven ready-made measurement sets of that library are named but their members are not listed. Each concept entry in `language.yaml` lists its attributes with name, type and multiplicity; many attribute types are other UPDM elements. The full list is under `data_types` in `language.yaml`.

## How it is drawn

The standard gives no symbols of its own (`coverage: informative`). A UPDM element is drawn as the UML element it extends, with its name in guillemets above the element's name; the extended UML element is the `uml_base` of each concept. Only the non-normative Annex D sample problem shows views, as UML and SysML diagrams: class boxes with a keyword, part boxes written name : type, small squares for ports, underlined names for actual elements, dashed arrows for dependencies, and solid lines with a small filled triangle for resource interactions. Matrix views are tables. `language.yaml` states the default under `notation` and lists only what differs.

Sizes and spacing come from `../_languages/layout-standard.yaml`; which element type each concept takes is in `layout` in `language.yaml`.

## A short example

Westbrook Bank, a fictitious bank, describes its small-business onboarding in a UPDM-style architecture. This is an illustration; use your own enterprise's elements, your own tooling and your own choice of framework.

An **EnterprisePhase** "FY Digital Onboarding" has an **EnterpriseVision** and an **EnterpriseGoal** "Open a business account in one day". A **Capability** "Business Account Opening" is **exhibited** (Exhibits) by the **Node** "Retail Banking Operations". The Node performs (IsCapableOfPerforming) the **OperationalActivity** "Verify Applicant Identity", which **MapsToCapability** the capability. A **Needline** joins the Node to the Node "Credit Bureau Services"; it bundles an **OperationalExchange** of kind information exchange that conveys the **ExchangeElement** "Identity Check Request". The **Organization** "Retail Banking" has the **Post** "Account Opening Officer"; an **ActualPerson** fills (FillsPost) the matching **ActualPost**.

On the solution side, a **CapabilityConfiguration** "Digital Onboarding Platform" (a SystemResource) contains **ResourceRole**s typed by **ResourceArtifact**s, linked by **ResourceInterface**s; a **Function** "Check Identity" **Implements** the OperationalActivity. The views drawn from this are OV-1, OV-2, OV-5, StV-2/CV-2, SV-1 and SV-5; the dictionary is AV-2.

## References

- `references/standard.md`: the standard section by section, in our own words, with the DoDAF and MODAF view tables.
- `references/rules.md`: all 264 rules with stable ids (`UPDM-<CAT>-nnn`), strength and source section.
- `language.yaml`: the machine-readable form: 226 concepts, 36 relationships, 21 role elements, the DoDAF and MODAF viewpoints, the 47 products, and the rules.
- Related skills: `uml-2`, `sysml-1`, `soaml-1`, `uaf-1`.
