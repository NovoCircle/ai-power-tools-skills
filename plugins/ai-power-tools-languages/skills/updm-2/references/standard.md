# The Unified Profile for DoDAF and MODAF (UPDM) 2.1, section by section

This is a summary of the OMG specification in our own words. It is not a substitute for the specification and does not reproduce its text; the few short quoted phrases are cited. Clause numbers are the specification's. Where the standard is silent or inconsistent, this file says so instead of filling the gap.

Source: Object Management Group, *Unified Profile for DoDAF and MODAF (UPDM)*, version 2.1, formal/13-08-04, https://www.omg.org/spec/UPDM/2.1/ (July 2013 on the OMG page; the cover says August 2013), and its normative profile file dtc/12-10-04. A later version 2.1.1 (May 2017, also ISO/IEC 19513) exists and is not described here. UPDM has been succeeded by the Unified Architecture Framework (UAF); see the `uaf-1` language skill.

## 1. What the standard is (clause 1)

**Purpose.** UPDM is a language for describing the architecture of an enterprise or a system of systems in the way two defense architecture frameworks require: the US Department of Defense Architecture Framework (DoDAF 2.02) and the UK Ministry of Defence Architecture Framework (MODAF 1.2). It also supports the NATO Architecture Framework implicitly, because MODAF and NAF had converged.

**One profile for two frameworks.** DoDAF and MODAF each have a meta-model (DM2 and M3) and a set of views. UPDM does not keep two languages. It defines one set of elements: a **Core** common to both, plus a small number of DoDAF-only and MODAF-only elements. Where the two frameworks give the same concept different names, the profile defines the concept once and gives the other name as an *alias*, a specialization with no new rules. The 52 DoDAF models and 47 MODAF views (more than 50 viewpoints in all) are then produced from the one set of elements (6.2.2, 7.6.1).

**A profile, not a method.** UPDM extends UML 2. It says what to describe and how the pieces connect. It does not say in what order to work, and it defines no drawing notation of its own: views are UML and SysML diagrams that show profile elements.

**What it can describe (clause 1).** Operational concepts and activities, nodes and their exchanges; systems and services, their functions, ports, interfaces and protocols; capabilities and the strategic intent of the enterprise; the projects and milestones that acquire systems; standards and forecasts; performance and measurements; the people, organizations and posts involved; and the related doctrine, organization, training, materiel, leadership, personnel and facilities concerns.

## 2. Conformance (clause 2)

There are two compliance levels.

- **Level 0** extends UML 2 and imports ten SoaML elements (Capability, ServiceInterface, Expose, Attachment, Request, Service, MessageType, Property, ServiceChannel, Participant). A tool conforms when every element, attribute, constraint, association and package structure of the level 0 package exists and is compliant, it can exchange both the user model and the profile through XMI, it exchanges level 0 models with no loss, and it reads level 1 models with only minimal loss.
- **Level 1** includes all of level 0 and imports the whole SysML profile with its sub-profiles. It adds 39 constraints that pair SysML elements with UPDM elements, so that a UPDM model can be carried straight into SysML modeling. A level 1 tool exchanges level 1 models with no loss and reads level 0 models with no loss, transforming where needed.

The specification also states that it conforms to DoDAF 2.02 at conformance level 3 (physical data model); each vendor remains responsible for its own claim (3.4.1). Conformance is about tools, not about a particular model.

## 3. Language architecture (clause 7)

UPDM was built model-first: a domain metamodel of the DoDAF and MODAF concepts was made first, each concept was mapped to a profile element (each profile element is linked to its metamodel element), the profile was refactored for tools and reuse, and the specification was generated from the profile (7.2). The core principles are that it is driven by requirements and by the domain metamodel, reuses UML, SysML and SoaML wherever practical, partitions the model by package, has two compliance levels, and inherits XMI interchange from UML (7.3).

**How constraints are written (7.4, 7.5).** A rule on a relationship is a constraint on the UML properties of the extended element, for example "the client of an Exhibits must be a CapableElement and its supplier a Capability". The specification's diagrams draw such rules as special dependencies (for constraints, for relationships that are plain UML ones, and for relationships that are profile elements); those dependencies are documentation only and are not part of the interchanged profile. The formal text of each constraint is short English; level 1 constraints are in OCL.

**Aliases (7.6.1).** Aliasing is done by specialization. The architectural description records which framework it follows (DoDAF, MODAF or NAF) and the aliases allowed depend on that choice.

**Reuse (7.6.2 to 7.6.4).** SoaML elements imported at level 0 are used as SoaML defines them. The full SysML profile at level 1 can be used and drawn in the SysML way next to UPDM elements. The SOPES elements, added at level 1, give higher fidelity to information-exchange requirements.

## 4. The profile (clause 8)

The profile is organized in packages: a library (8.2), and the elements (8.3). Under the elements, **Core** (8.3.1.1) holds the elements common to both frameworks, **DoDAF** (8.3.1.2) and **MODAF** (8.3.1.3) hold what is specific to each, **SOPES** (8.3.1.4) holds seven information-exchange elements, and **SwAF** (8.3.1.5) holds one design-rule element. Each of Core, DoDAF and MODAF is split by subject area: acquisition, all-views, operational, services, strategic, systems and technical standards. The elements within each area are presented alphabetically.

There are **226 elements**: 151 in Core, 31 in DoDAF, 36 in MODAF, 7 in SOPES, 1 in SwAF. Thirty-three are abstract groupings. Each profile element extends a UML element kind (a class, a property, a dependency, an information flow, a connector and so on) and most specialize **UPDMElement**, the root that gives them a URI, links to the standards they conform to, boundary dates and links to measurements.

The DoDAF class library (8.2) adds a security classification enumeration and seven property sets (communications link, data element, exchange, information assurance, information element, operational activity and security attributes properties).

### 4.1 All elements (8.3.1.1.2)

Elements shared by every view. **ArchitecturalDescription** is the top: a package holding the scope, authors, purpose, tools, framework in use, viewpoints and views. A **Viewpoint** names stakeholders, concerns, languages and methods. A **View** is a package of architectural elements made to one or more viewpoints and covering enterprise phases (it also specializes the SysML View). **ArchitecturalReference** says one description refers to another. **Metadata** and **ArchitectureMetadata** annotate elements or the whole description. Measurements: a **MeasurementSet** groups **Measurements**; **ActualPropertySet**, **ActualProperty** and **ActualMeasurement** hold values with an intent (actual, required, estimate) and dates. Environment: **Environment**, **EnvironmentProperty**, **LocationType** and **ActualLocation** describe conditions and places; DoDAF and MODAF add aliases and kinds (Condition, Climate, LightCondition, GeoPoliticalExtent). Abstract groupings: Participant, Resource, Rule, Exchange, CapableElement, Activity.

The two behavior relationships that tie the whole profile together are **IsCapableOfPerforming** (a performer, a resource or a service interface can perform an activity) and **Implements** (a solution-side element implements a logical-side one).

### 4.2 Strategic elements (8.3.1.1.6, 8.3.1.2.5, 8.3.1.3.4)

The strategic view supports capability management: introducing, integrating, realigning and removing capabilities. Only one strategic view exists across a number of architectural descriptions. An **EnterprisePhase** is a time-bounded phase with an **EnterpriseVision** (described by VisionStatements), **EnterpriseGoals** and **EnduringTasks**; phases are divided into **TemporalPart** and **StructuralPart**; a **WholeLifeEnterprise** covers the whole life. A **Capability** has **CapabilityProperty**s. **Exhibits** says a capable element (a node, resource or phase) provides a capability; **MapsToCapability** says an activity is part of a capability; **DesiredEffect** links a desirer to a desired state. DoDAF aliases: Vision, CapabilityOfPerformer, ActivityPartOfCapability. MODAF adds **DeployedMilestone** and **NoLongerUsedMilestone**.

### 4.3 Operational elements (8.3.1.1.4, 8.3.1.2.3, 8.3.1.3.3)

The operational view is the logical architecture: it describes tasks, activities, operational elements and exchanges, independent of materiel.

- **Structure.** A **Node** is a logical entity that performs operational activities (DoDAF alias **Performer**); a **SecurityDomain** is a node with one security policy. A **LogicalArchitecture** is a composite of **NodeRole**s, a **ProblemDomain** and **KnownResource**s. **NodePort**s are the interaction points; a **Needline** connects nodes and bundles operational exchanges. A **HighLevelOperationalConcept** is made of **ConceptRole**s typed by **ConceptItem**s, joined by visual-only **ArbitraryConnector**s, for one or more **Mission**s. An **OperationalConstraint** is a rule on an operational element.
- **Organization.** Typical: **Organization**, **Post**, **Person**, **Responsibility**, **RoleType** (aliases OrganizationType, PersonType); relationships **ProvidesCompetence** and **RequiresCompetence** to a **Competence** (alias Skill). Actual: **ActualOrganization**, **ActualPost**, **ActualPerson**, **ActualOrganizationRole**, **ActualOrganizationRelationship**, **FillsPost**.
- **Behavior.** An **OperationalActivity** (also **StandardOperationalActivity** for doctrinal procedures) with **OperationalActivityAction**, **OperationalActivityEdge** and **OperationalParameter**s; a node performs it through **NodeOperation**s; **OperationalStateDescription** with **OperationalState**s; **OperationalEventTrace** with **OperationalMessage**s. **OwnsProcess** links an organizational resource to a process.
- **Flows.** An **OperationalExchange** carries something between two nodes; its exchange kind (information, materiel, energy, organizational, configuration, geo-political extent) decides what it may convey. **Command** and **Control** are resource interactions between organizational resources (and, for Control, an artifact).
- **Data.** A **LogicalDataModel** of **EntityItem**s, **EntityAttribute**s and **EntityRelationship**s.

### 4.4 Systems elements (8.3.1.1.7, 8.3.1.2.6)

Models in the systems view realize, in equipment capability, the operational capability; it specifies the capability needed rather than implementation detail. A **SystemResource** (abstract) is realized as **ResourceArtifact**s (DoDAF alias **System**; includes **Software** and **Materiel**), **Organization**s and **Post**s, and **CapabilityConfiguration**s (a **PhysicalArchitecture**). **ResourcePort**, **ResourceInterface** and **ResourceConnector** give the connectivity; a **ResourceInteraction** carries **ResourceInteractionItem**s. **Function**s (with **FunctionAction**, **FunctionEdge**, **ResourceParameter**, **ResourceOperation**), **ResourceStateMachine** with **ResourceState**s and **ResourceEventTrace** with **ResourceMessage**s give behavior. A **WholeLifeConfiguration** has **VersionOfConfiguration**s; a **FieldedCapability** is a realized capability. A **Forecast** looks ahead at systems, standards or competences. A **ResourceConstraint** is a rule on an implementation. A **PhysicalDataModel** realizes a logical one.

### 4.5 Service elements (8.3.1.1.5, 8.3.1.2.4)

Services are described in the broadest sense: a unit of work through which a provider gives a consumer a useful result. A **ServiceInterface** (from SoaML) has **ServiceOperation**s, **ServiceMessageHandler**s and **ServiceAttribute**s; a **Service** or **Request** is a **ServicePort** typed by an interface; a **ServiceFunction** (with action, edge and parameter) gives the abstract behavior, a **ServiceStateMachine** and **ServiceInteraction** (with **ServiceMessage**s) the states and interactions. **ServiceLevelValueSet**s record the levels a resource delivers. **ServicePolicy** constrains providers and consumers. DoDAF adds **ServiceAccess** and **ServiceDescription**.

### 4.6 Acquisition elements (8.3.1.1.1, 8.3.1.2.1, 8.3.1.3.1)

**ProjectType** and **ActualProject** (with parts and wholes), **ProjectMilestone** and **ActualProjectMilestone** (milestones of four kinds: **IncrementMilestone**, **DeployedMilestone**, **NoLongerUsedMilestone**, **OutOfServiceMilestone**), **ProjectTheme**s with **StatusIndicators** and **ProjectStatus**, **ProjectSequence**, **MilestoneSequence**, **OrganizationalProjectRelationship** (and **ProjectOwnership**). DoDAF adds **ProjectActivity** and **ActivityPartOfProject**.

### 4.7 Technical standards (8.3.1.1.8, 8.3.1.2.7, 8.3.1.3.5)

A **Standard** (DoDAF: **TechnicalStandard**, **FunctionalStandard**) with a **Protocol**, **ProtocolImplementation** and **ProtocolLayer**; **StandardConfiguration** marks a reusable configuration. The standards view covers one time period; a forecast covers a future one, and the view references the systems, services and data views.

### 4.8 Ontology and extension (8.3.1.3.2.2) and SOPES, SwAF

**OntologyReference** elements (**ExternalType**, **ExternalIndividual**, **ExternalTuple**, **ExternalTupleType**), **SameAs**, **Overlap**, **Alias** and **Definition** link the architecture to external ontologies and dictionaries. SOPES adds **Semantic**, **Transactional** and **Wrapper** (with attributes) and **Contract**, an agreement to exchange information. SwAF adds **DesignRule**.

## 5. Relationships

A relationship is a profile element that extends a UML relationship. Its ends are fixed by constraints. There are 36 (30 with their own rules, 6 aliases), listed with their ends in `language.yaml`. Group them by what they join:

- **Behavior and capability:** IsCapableOfPerforming, Implements, MapsToCapability, Exhibits, DesiredEffect, OwnsProcess.
- **Flows:** OperationalExchange, ResourceInteraction, Command, Control, ActualOrganizationRelationship, Contract.
- **Connectors:** Needline, ResourceInterface, ResourceConnector, EntityRelationship.
- **People and competence:** ProvidesCompetence, RequiresCompetence, FillsPost, Trustline.
- **Acquisition:** OrganizationalProjectRelationship, ActivityPartOfProject, ProjectSequence, MilestoneSequence.
- **Architecture and dictionary:** ArchitecturalReference, Details, Forecast, SameAs, Overlap, ArbitraryConnector.

Further elements act as part-whole or instance relationships: NodeRole, ResourceRole, ConceptRole and similar roles say which owner may hold which type; ActualOrganizationRole and similar slots say which instance holds which value. No multiplicity is stated; each is many-to-many and optional.

## 6. Views and viewpoints (Annex B, Annex C)

**The two frameworks side by side.**

- DoDAF 2.02 has eight viewpoints: All (AV), Capability (CV), Data and Information (DIV), Operational (OV), Project (PV), Services (SvcV), Standards (StdV) and Systems (SV), with 52 models.
- MODAF 1.2 has seven: All (AV), Strategic (StV), Operational (OV), Service-Oriented (SOV), Systems (SV), Technical Standards (TV) and Acquisition (AcV), with 47 views.

**How UPDM maps both onto one profile.** Annex B describes 47 *products*, each realizing one or more DoDAF models and one or more MODAF views from the same elements. Examples: AcV-1/PV-1; StV-2/CV-2; SV-1/SvcV-1; SV-11/DIV-3; OV-7/DIV-1/DIV-2; TV-1&2&3/StdV-1&2. Table C.3 gives the model-by-model correspondence. The correspondence is close for operational, systems, capability/strategic, project/acquisition and standards views, and weak for services, where MODAF services are specifications and DoDAF services are implementations in performers. A few views exist in only one framework: DoDAF has PV-3 and DIV-1 (no direct MODAF counterpart) and the operational-to-systems traceability split into SV-5a and SV-5b; MODAF has SOV-1, SOV-2, SV-12 and the lettered communications views SV-2a/b/c. UPDM also supports user-defined (custom) views, and combined views such as the DoDAF data model that combines SV-11 and OV-7 (clause 1).

Annex B is non-normative guidance about which UPDM elements and relationships each product uses; the lists are in figures. The specification gives the following in text:

- **All views (AV-1, AV-2).** Overview and integrated dictionary. They are populated whenever an architecture is created or changed; they hold the description, scope, framework in use, definitions and aliases.
- **Capability / Strategic.** Vision (CV-1/StV-1), taxonomy (2), phasing (3), dependencies (4), mapping to organizational development or deployment (5), mapping to operational activities (6), and CV-7 for services. Capabilities are timeless; time enters through milestones that tie to a capability configuration.
- **Operational.** OV-1 high-level concept; OV-2 node (or resource-flow) relationships; OV-3 exchange matrix; OV-4 organization chart (MODAF splits it into typical and actual); OV-5 activity model; OV-6a rules, 6b state transitions, 6c event traces; OV-7/DIV-1/DIV-2 information and data models.
- **Systems and services.** SV-1 composition and interaction; SV-2 flows and communications; SV-3 matrix; SV-4 functionality; SV-5 traceability from operational activities; SV-6 flow matrix; SV-7 measures; SV-8 evolution; SV-9 technology and skills forecast; SV-10a/b/c constraints, states, event traces; SV-11/DIV-3 physical data; SV-12 service provision and composition. The service views mirror them (SvcV, SOV).
- **Standards.** Standards profile and forecast.
- **Project / Acquisition.** Clusters, timelines, and project-to-capability mapping.
- **Environment and measurements.** Two products with no DoDAF or MODAF view number.

## 7. The rules that matter most

The full list, 264 rules with ids, is in `references/rules.md`. Highlights:

1. **Ends of relationships** are fixed (UPDM-END-nnn): for example Exhibits runs from a capable element to a Capability; MapsToCapability from an Activity to a Capability; FillsPost from an ActualPerson to an ActualPost; OperationalExchange between Nodes.
2. **Typing** (UPDM-TYP-nnn): a role is typed by the matching element; an instance is classified by the matching type (an ActualPost by a Post).
3. **Ownership** (UPDM-OWN-nnn): a node owns operational operations and ports; an activity's parameters are operational parameters; a resource's parameters are resource parameters.
4. **Exchange kinds** (UPDM-XCH-nnn): an operational exchange conveys what its kind says.
5. **Level 1 pairing** (UPDM-SYS-nnn): at level 1 each listed element also carries its SysML counterpart (Block, ValueType, ItemFlow, FlowPort, Requirement).
6. **Aliases follow the framework chosen** (UPDM-GEN-001).
7. **Milestones keep their order** (UPDM-VIEW-nnn): increment, then deployed, then no longer used, then out of service; the framework does not enforce it.

## 8. The newer standard

UPDM is superseded. The Unified Architecture Framework (UAF) replaces it with a grid of views over a domain metamodel and a language built on SysML. See the `uaf-1` language skill for UAF; this skill describes UPDM as it is.
