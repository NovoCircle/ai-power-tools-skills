---
name: uaf-1
description: The OMG Unified Architecture Framework (UAF) 1.0 and its profile (UAFP), a framework for describing enterprise and system-of-systems architectures as a grid of views - strategic, operational, services, personnel, resources, security, project, standards and actual-resources domains by taxonomy, structure, connectivity, processes, states, interaction scenarios, constraints, roadmap and traceability model kinds. Use when someone is modeling with UAF, UAFP, UPDM, DoDAF, MODAF or NAF concepts - capabilities, enterprise phases, operational performers and operational activities, operational exchanges, resource performers, functions, services and service specifications, organizations, posts and persons, resource artifacts and software, security assets, risks and security controls, projects and milestones, standards and protocols, actual resources - or asks what a UAF view, viewpoint or relationship such as IsCapableToPerform, Exhibits, Implements or MapsToCapability allows.
---

# Unified Architecture Framework (UAF) 1.0

UAF is the Object Management Group's framework for describing the architecture of an enterprise, a mission or a system of systems. It has three layers: a *grid* of viewpoints (domains by model kinds), a tool-independent *domain metamodel* of the concepts and relationships, and a *language* (a profile on SysML 1.4, called UAFP) derived from the metamodel. It grew out of the defense frameworks DoDAF, MODAF and NAF and is also used outside defense. It is not a method: it says what to describe and how the pieces connect, not in what order to work.

The language builds on SysML. Its diagrams are SysML diagrams (block definition, internal block, activity, state machine, sequence, parametric, requirement) and its elements extend UML and SysML elements. SysML's own rules are not repeated here.

## What you are creating

An *architecture description*: a set of **views**, each made to a **view specification** (a viewpoint in ISO 42010 terms), over one set of shared elements. A capability named in the strategic view is the same element a project delivers and an operational activity maps to. The framework keeps four things apart:

1. **Types and actual things.** Most concepts are types (a Post, an Organization, a Project, a ServiceSpecification). Their instances carry a time span and an `Actual` prefix (ActualPost, ActualOrganization, ActualProject). An actual element is classified by its matching type.
2. **Logical and physical.** Operational elements are the logical architecture, independent of any solution. Resource elements are the solution that implements them. Services sit between.
3. **Roles and the things that play them.** A part used inside another element is a *role* (OperationalRole, ResourceRole, ServiceSpecificationRole, ProjectRole). It has an owning element and a type.
4. **Relationships and the elements they join.** Every relationship has fixed kinds of element at its ends.

## The grid: diagram types

The 76 view specifications are the diagram types. Rows are domains, columns are model kinds; the number in a cell is how many view specifications it holds ('-' means none; the standard says the grid is not complete).

| Domain | Taxonomy (Tx) | Structure (Sr) | Connectivity (Cn) | Processes (Pr) | States (St) | Interaction Scenarios (Is) | Information (If) | Constraints (Ct) | Roadmap (Rm) | Traceability (Tr) |
|---|---|---|---|---|---|---|---|---|---|---|
| Metadata (Md) | placeholder | - | - | - | - | - | - | - | - | - |
| Strategic (St) | 1 | 1 | 1 | - | 1 | - | - | 1 | 2 | 1 |
| Operational (Op) | 1 | 1 | 1 | 1 | 1 | 1 | - | 1 | - | 1 |
| Services (Sv) | 1 | 1 | 1 | 1 | 1 | 1 | - | 1 | 1 | 1 |
| Personnel (Pr) | 1 | 1 | 1 | 1 | 1 | 1 | - | 3 | 3 | 1 |
| Resources (Rs) | 1 | 1 | 1 | 1 | 1 | 1 | - | 1 | 2 | 1 |
| Security (Sc) | 1 | 1 | 1 | 1 | - | - | - | 1 | - | 1 |
| Projects (Pj) | 1 | 1 | 1 | 1 | - | - | - | - | 1 | 1 |
| Standards (Sd) | 1 | 1 | - | - | - | - | - | - | 1 | 1 |
| Actual Resources (Ar) | 1 | 1 | 1 | - | - | - | - | - | - | - |

The Information column (If) is empty in every row: the information model and the parameters are columns that run across all layers and are given as separate view specifications. Outside the grid there are view specifications for the Dictionary, the Summary and Overview, Requirements, the Information Model, Parameters (Environment, Measurements) and three mappings to other standards (BPMN, IEPPV, NIEM).

Model kinds, in one line each: **Taxonomy** is the hierarchy of types; **Structure** shows parts, ports and relationships; **Connectivity** the connections and exchanges; **Processes** activity flows; **States** state machines; **Interaction Scenarios** time-ordered messages; **Constraints** measurements and rules; **Roadmap** change over time; **Traceability** mappings between elements and domains.

### What each domain's views admit (key elements)

| Domain | Views admit mainly |
|---|---|
| Strategic | Capability, CapabilityProperty, EnterprisePhase and its parts, EnterpriseGoal, EnterpriseVision, EnduringTask, Exhibits, MapsToCapability, DesiredEffect and AchievedEffect |
| Operational | OperationalPerformer, OperationalRole, OperationalPort, OperationalInterface, OperationalConnector, OperationalExchange, OperationalActivity and its actions and flows, OperationalStateDescription, OperationalMessage, InformationElement, OperationalConstraint, HighLevelOperationalConcept |
| Services | ServiceSpecification, ServicePort, ServiceInterface, ServiceConnector, ServiceFunction, ServiceStateDescription, ServiceMessage, ServicePolicy, ProvidedServiceLevel, RequiredServiceLevel, Consumes |
| Personnel | Organization, Person, Post, Responsibility, Command, Control, Competence, RequiresCompetence, CompetenceForRole, ResourceRole |
| Resources | ResourcePerformer kinds (System, Software, ResourceArtifact, NaturalResource, CapabilityConfiguration), ResourcePort, ResourceInterface, ResourceConnector, ResourceExchange, Function and its actions and flows, DataElement, ResourceConstraint, Forecast, Technology, VersionedElement |
| Security | Asset, AssetRole, SecurityEnclave, SecurityProperty, SecurityControl and its family, Enhances, Protects, Risk, Affects, Mitigates, OwnsRisk, SecurityConstraint |
| Projects | Project, ProjectMilestone and roles, ProjectTheme, StatusIndicators, ProjectActivity, ActualProject, ActualProjectMilestone, MilestoneDependency, ProjectSequence |
| Standards | Standard, Protocol, ProtocolStack, ProtocolLayer |
| Actual Resources | ActualOrganization, ActualPerson, ActualPost, ActualResource, ActualResponsibility, FieldedCapability, FillsPost, ResponsibleFor, ActualResourceRelationship |

The full list of elements each view specification admits is in `language.yaml` under `diagram_types`. A view's element list is guidance (rule UAF-VIEW-001, a warning), not a closed set.

## Concepts, grouped

226 elements in the profile (plus 9 that exist only in the domain metamodel). Full definitions, generalizations and properties are in `language.yaml` and `references/standard.md`.

- **Common roots (abstract).** UAFElement is the root of everything and carries a URI and a link to the standards it conforms to. MeasurableElement can be measured by MeasurementSets; PropertySet owns Measurements; ActualState gives a start and end date. Other abstract groupings used as relationship ends: Activity, CapableElement, Desirer, Achiever, Resource, Exchange, OperationalAgent, OperationalExchangeItem, PhysicalResource, ResourcePerformer, ResourceExchangeItem, Asset, AssetRole, the SubjectOf... groupings, ActualOrganizationalResource and ActualResponsibleResource. Thirty-three are abstract in the profile (SecurityMeasurement is abstract in the metamodel only) and are never used directly.
- **Parameters and metadata.** Measurement, MeasurementSet, ActualMeasurement; Condition, Environment, Location, GeoPoliticalExtentType; Alias, Definition, SameAs, Metadata, Information, Rule.
- **Strategic.** Capability, EnterprisePhase (WholeLifeEnterprise), EnterpriseGoal, EnterpriseVision, EnduringTask and ActualEnduringTask, ActualEnterprisePhase.
- **Operational.** OperationalPerformer (with OperationalArchitecture and KnownResource as OperationalAgents), OperationalRole, OperationalPort, OperationalInterface, OperationalExchange, OperationalActivity, InformationElement.
- **Services.** ServiceSpecification, ServiceSpecificationRole, ServicePort, ServiceInterface, ServiceFunction, ServicePolicy.
- **Personnel.** Organization, Person, Post, Responsibility (all OrganizationalResources), Competence.
- **Resources.** ResourcePerformer is the abstract parent of System, Software, ResourceArtifact, NaturalResource, CapabilityConfiguration and the organizational resources; ResourceRole, ResourcePort, ResourceInterface, Function, DataElement, DataModel, Technology.
- **Security.** Asset, SecurityEnclave, SecurityControl, Risk, SecurityProperty, SecurityConstraint.
- **Projects.** Project, ProjectMilestone, ProjectTheme, StatusIndicators, ProjectActivity.
- **Standards.** Standard, Protocol, ProtocolStack, ProtocolLayer.
- **Actual resources.** The `Actual` counterparts of organizations, persons, posts, responsibilities, resources, projects and services, FieldedCapability, ProvidedServiceLevel and RequiredServiceLevel.
- **Summary.** ArchitecturalDescription, View, Viewpoint, Concern, Stakeholder.
- **Enumerations.** Fifteen kinds that qualify an element: for example OperationalExchangeKind, ResourceInteractionKind, RoleKind, ProjectKind, EnvironmentKind, RuleKind, DataModelKind.

## Relationships in summary

A relationship is itself an element that extends a UML dependency, abstraction, information flow, connector, activity edge or message. The standard gives no multiplicity: every relationship is many-to-many and optional. Ends are fixed by rule (UAF-END-nnn). The ones used most:

| Relationship | From (source) | To (target) |
|---|---|---|
| IsCapableToPerform | OperationalAgent / ServiceSpecification / ResourcePerformer / Project | OperationalActivity / ServiceFunction / Function / ProjectActivity (matching pairs only) |
| PerformsInContext | OperationalRole / ServiceSpecificationRole / ResourceRole / ProjectRole | OperationalActivityAction / ServiceFunctionAction / FunctionAction / ProjectActivityAction (matching pairs only) |
| Exhibits | CapableElement | Capability |
| MapsToCapability | Activity | Capability |
| CapabilityForTask | Capability | ActualEnduringTask |
| DesiredEffect / AchievedEffect | Desirer / Achiever | ActualState |
| OperationalExchange | OperationalPerformer | OperationalPerformer |
| ResourceExchange | ResourcePerformer | ResourcePerformer |
| OperationalConnector / ServiceConnector / ResourceConnector | role or port | role or port (of its own domain) |
| Implements | the resource-side element | the operational- or service-side element it implements (Function to OperationalActivity, ResourceExchange to OperationalExchange, DataElement to InformationElement, and so on) |
| Consumes | OperationalActivity | ServiceSpecification |
| Protects / Mitigates / Affects | SecurityControl / SecurityControl / Risk | Asset / Risk / Asset |
| OwnsRisk | OrganizationalResource | Risk |
| FillsPost | ActualPerson | ActualPost |
| ResponsibleFor | ActualResponsibleResource | ActualProject or ActualResponsibility |
| MilestoneDependency / ProjectSequence | ActualProjectMilestone / ActualProject | the same kind |
| Forecast | SubjectOfForecast | the same specialization of SubjectOfForecast |

Parts use typing rather than relationships: a role names the element that owns it (its class) and the element it is typed by (OperationalRole: class and type are both OperationalAgents; ResourcePort: class a ResourcePerformer, type a ResourceInterface).

## The rules that matter most

The 256 rules (242 must, 1 should, 13 note) are in `references/rules.md`; the same ids are in `language.yaml`. These matter most:

1. **UAF-GEN-001** Never use an abstract element directly. Use its concrete specializations.
2. **UAF-END-nnn** Every relationship joins the kinds of element its definition names. For example an OperationalAgent is capable of performing only OperationalActivity; a ResourcePerformer only Function; a ServiceSpecification only ServiceFunction; a Project only ProjectActivity (UAF-END-005, 006).
3. **UAF-END-005 to 008** IsCapableToPerform and PerformsInContext must pair the domains correctly: operational with operational, service with service, resource with resource, project with project.
4. **UAF-END-014, 015** Implements always points from the lower, solution-side element to the higher, requirement-side element of the matching kind.
5. **UAF-XCH-001, 007** What an exchange conveys depends on its kind: information exchange conveys an InformationElement, materiel exchange a ResourceArtifact, energy exchange a NaturalResource, and so on; resource communication conveys a DataElement.
6. **UAF-TYP-nnn** Every actual element is classified by its matching type (ActualPost by Post, ActualProject by Project, FieldedCapability by CapabilityConfiguration); every role has an owner and a type of the right kind.
7. **UAF-OWN-nnn** A performer owns only methods, ports and parameters of its own domain; a called action points to an activity of its own domain; activity edges and state machines have the right owner.
8. **UAF-VAL-001** The dates of an actual enterprise phase fall inside the dates of the phase that holds it.
9. **UAF-VAL-002** A Forecast joins two elements of the same kind (Software to Software, Standard to Standard).
10. **UAF-VAL-003** All themes of one project milestone use the same status indicator type.
11. **UAF-CARD-nnn** Properties with multiplicity exactly one must have a value: for example the kind of an ActualLocation, Environment, Location, Rule, Information, ResourceRole, ActualProject, ActualProjectMilestone and WholeLifeConfiguration, and the viewpoint of a View.
12. **UAF-GEN-002** Dates are ISO 8601 date-times with a time zone.
13. **UAF-VIEW-001** (warning) A view shows the elements its view specification lists.
14. **UAF-CONF-001 to 004** A tool conforms by supporting the profile on SysML 1.4, with lossless model and profile interchange.

## Data types and attributes

Coverage: partial. UAF defines no primitive types or units of its own; the String, Boolean, Integer and Real that its attributes use are UML's (`inherits_from: uml-2`). What it does define is one date-time format (ISO8601DateTime, written like 2027-03-01T09:30:00-08:00, clause 7.1.3.1), 17 enumerations (the 15 kinds, StatusIndicators, and the metamodel's SecurityClassificationKind) such as RoleKind, ProjectKind and RuleKind with their values, five data-type elements (Condition, Environment, GeoPoliticalExtentType, Location, MeasurementSet), and an Annex B library of property groups (BillingItem, Duration, ExchangeProperties and others) with two more enumerations, Periodicity and PricingType. Each concept entry in `language.yaml` lists its own attributes under `attributes` with name, type and multiplicity; the Annex B groups carry theirs inside `data_types.types`. All of it is under `data_types` and `concepts.elements`.

## How it is drawn

Coverage: informative. UAF has no symbols of its own. It expects each element to be drawn in the standard SysML or UML notation of the metaclass it extends (a class box, a part box, a port square, a rounded rectangle for an activity, a dashed line for a dependency), inside a frame of the diagram type the view is based on, with the stereotype name as the keyword. Each view specification recommends a form (block definition, internal block, activity, state machine, sequence, parametric or requirement diagram, table, matrix or timeline) under `diagram_types`. The figures in the specification show how the profile is defined, not how a model looks. `notation` in `language.yaml` gives one `default` that says this, and lists under `not_specified` the 33 elements the profile marks abstract, which are never drawn directly, and the 9 concepts that exist only in the metamodel (one of them, SecurityMeasurement, is abstract there). To draw a UAF element, find its `uml_base` and use the `sysml-1` guide for a SysML element or the `uml-2` guide for a UML one.

Sizes and spacing come from `../_languages/layout-standard.yaml`; which element type each concept takes is in `layout` in `language.yaml`.

## A short example (Westbrook Bank, fictitious)

Westbrook Bank wants to show how it settles card payments. The values are an illustration; substitute your own organization, names and views.

- **Strategic.** Capability *Card Payment Settlement*. EnterprisePhase *2027 Payments Modernization* with EnterpriseGoal *Settle card payments same day*.
- **Operational.** OperationalPerformer *Payment Operations Unit* IsCapableToPerform OperationalActivity *Settle Card Transactions*; the activity MapsToCapability *Card Payment Settlement*. The performer Exhibits the capability. An OperationalExchange *Settlement Instruction* (information exchange, conveying an InformationElement) runs from *Payment Operations Unit* to *Card Network Gateway*.
- **Services.** ServiceSpecification *Card Authorization Service*; the activity *Settle Card Transactions* Consumes it.
- **Resources.** System *Core Banking Platform* (a ResourcePerformer) IsCapableToPerform Function *Post Settlement Entries*; that function Implements the operational activity; a ResourceExchange carries a DataElement *Settlement Record*.
- **Personnel and actual resources.** Post *Settlement Analyst*; ActualPerson *J. Doe* FillsPost ActualPost *Settlement Analyst, Westbrook Operations*; ActualOrganization *Westbrook Bank Payments*.
- **Security.** The DataElement *Settlement Record* is an Asset (Asset is abstract, so the concrete element is used); Risk *Unauthorized settlement change* Affects it; SecurityControl *Dual approval* Mitigates the risk.
- **A seeded defect.** A ServiceSpecification IsCapableToPerform an OperationalActivity breaks UAF-END-005 and 006: a service specification may perform only a ServiceFunction.

## References

- `references/standard.md`: the standard section by section, with the full concept, relationship and view tables.
- `references/rules.md`: the 256 rules with ids and sections.
- `language.yaml`: the machine-readable concepts, relationships, grid, diagram types (view specifications with what each admits) and constraints.
- Source: Object Management Group, Unified Architecture Framework Profile 1.0 (formal/17-12-01) and its Appendix A, the Domain Metamodel (formal/17-12-02), https://www.omg.org/spec/UAF/1.0/. Versions 1.1, 1.2 and 1.3 exist and are not described here.
