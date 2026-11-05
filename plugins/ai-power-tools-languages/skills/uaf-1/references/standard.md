# The Unified Architecture Framework (UAF) 1.0, section by section

This is a summary of the OMG specification in our own words. It is not a substitute for the specification and does not reproduce its text; the few short quoted phrases are cited. Clause numbers are the specification's. Where the standard is silent or inconsistent, this file says so instead of filling the gap.

Sources: Object Management Group, *Unified Architecture Framework Profile (UAFP)*, version 1.0, formal/17-12-01 (clause numbers without a prefix), and its Appendix A, *The Domain Metamodel*, formal/17-12-02 (clause numbers prefixed 'DMM'). https://www.omg.org/spec/UAF/1.0/. The profile is the language tools implement; the domain metamodel is the tool-independent definition it is derived from.

## 1. What the standard is (clause 1)

**Identity.** UAF 1.0 is a formal OMG standard in the C4i, Enterprise Modeling and Systems Engineering domains. It replaces the earlier Unified Profile for DoDAF and MODAF (UPDM 2.1 and 2.2). Later versions (1.1, 1.2, 1.3) exist and are not covered here.

**Purpose.** It is a framework for describing architectures of complex systems and systems of systems: capabilities, operational activities and performers, services, people and organizations, resources (hardware, software, natural resources, information), security, projects, standards, and the actual things that fill those roles. It combines the viewpoints of DoDAF 2.02, MODAF, NAF 3.1 and the security views of DNDAF into one set, and is meant to also serve non-defense organizations. Its terms follow ISO/IEC/IEEE 42010 for architecture description (architecture, view, viewpoint, concern, stakeholder, model kind).

**Two parts.** The *domain metamodel* (DMM, Appendix A) is a UML class model of the concepts, relationships and viewpoints, written so that tool vendors who do not use UML or SysML can implement it. The *profile* (UAFP) is derived from it by mapping concepts and relationships to profile elements on SysML 1.4, so that UML and SysML tools can implement it and keep SysML's notation and engineering analysis (for example parametrics and simulation).

**Intended users (1.2).** Architects, systems engineers, program managers and their sponsors, and builders of supporting hardware and software. The profile lets a modeler describe strategic capabilities, operational activities and performers and their interfaces, services and service levels, resources and their functions and ports, security controls, human interaction, information and data schemas, and project plans.

## 2. Conformance (clause 2)

There is one compliance level: support for the profile as a SysML 1.4 profile. A tool is compliant only if every element, class, attribute, constraint, association and package structure exists as specified; it can import and export both the user model and the profile as XMI; and it can import and export UAF models with 100% fidelity, with no loss or transformation. The profile imports the SysML profile and adds constraints that pair the use of SysML and UAF elements. Nothing is said about conformance of a model, an instance or a diagram. (Rules UAF-CONF-001 to 004.)

## 3. References, terms and symbols (clauses 3 to 5)

The normative references are UML 2.5, OCL 2.4, SysML 1.4, Diagram Definition 1.1, NIEM-UML, UPDM 2.1, the UML profile for BPMN processes, ODM, IEPPV, and the donor frameworks DoDAF 2.02 (with DM2), DNDAF, IDEAS, ISO/IEC/IEEE 42010, MODAF (with MODEM) and NAF. No new terms are defined (clause 4). Clause 5 lists acronyms; the view acronyms used in sample names follow the framework conventions (for example OV for operational, SV for system, SvcV for service views).

## 4. Additional information (clause 6)

**6.1 Changes to adopted specifications.** UAFP completely replaces UPDM 2.1 and supersedes UPDM 2.2.

**6.2 Language architecture.** The profile reuses a subset of UML 2 and SysML 1.4 and adds the extensions needed for the UPDM 3.0 requirements.

**6.3 Philosophy.** The work was model-driven: a domain metamodel in UML classes represents the concepts of the donor frameworks; the viewpoints are renamed and aligned into one generic naming; the framework separates the metamodel from the presentation layer; the profile is derived from the metamodel. Every profile element is traceable to a metamodel element by an abstraction. Implementers follow the view naming conventions of the framework they implement. Behavior analysis by simulation and evaluation of non-functional requirements by parametric execution are expected of tools.

**6.4 Core principles.** Requirements-driven; driven by the domain metamodel; reuse of UML and SysML; partitioning by package; a single compliance level; interoperability through XMI. Views are expected to have a frame that reflects the underlying SysML diagram type, and elements are expected to be drawn in the notation of the metaclass they extend. (Rules UAF-VIEW-002, 003.)

**6.5 Representing constraints.** The profile's pictures use two helper dependencies, *metaconstraint* (to show which element an end must be) and *metarelationship* (to show that a concept uses a plain UML dependency or generalization). They appear only in the specification's figures, not in the interchange file. The constraints themselves are stated in structured English and can be implemented, for example, in OCL. For connectors, an end is reached through its role. (Rule UAF-GUID-002.)

## 5. The grid and the view specifications (DMM clauses 1 and 2; profile Annex A)

The metamodel arranges viewpoints in a grid. Rows are *domains* (layers of abstraction); columns are *model kinds* (types of architectural representation). The grid shows what the donor frameworks contribute and is not meant to be complete, so some cells are empty. Each cell is a view specification: a viewpoint in ISO 42010 terms, with stakeholders, concerns, a definition, a recommended implementation and the elements it shows. A view is a model built to a view specification.

**Domains.**

| Domain | Acronym | Meaning |
|---|---|---|
| Metadata | Md | Supporting information that applies to the whole architecture, rather than architectural models. |
| Strategic | St | The capability management process: the taxonomy, composition, dependencies and evolution of capabilities. |
| Operational | Op | The logical architecture of the enterprise: requirements, behavior, structure and exchanges that exhibit capabilities, independent of any solution. |
| Services | Sv | The services that directly support the operational domain; a service is a unit of work through which a provider gives a consumer a useful result. |
| Personnel | Pr | Organizational resource types, their connections and interactions, and how they grow over time. |
| Resources | Rs | The solution architecture of resources (organizational, software, artifacts, capability configurations, natural resources) that implement the operational requirements. |
| Security | Sc | Security assets and enclaves, the owners of assets, the security constraints (policy, law, guidance) and where they apply. |
| Projects | Pj | Projects and milestones, how they deliver capabilities, the organizations that contribute, and dependencies between projects. |
| Standards | Sd | The technical and non-technical standards that apply to the architecture. |
| Actual Resources | Ar | Analysis of the actual resource configurations: alternatives, what-if, trade-offs, verification and validation. |

**Model kinds.**

| Model kind | Acronym | Meaning |
|---|---|---|
| Taxonomy | Tx | All elements as a stand-alone specialization hierarchy, each with a definition and a source. |
| Structure | Sr | The dependencies, connections and relationships between elements. |
| Connectivity | Cn | The connections, relationships and interactions between elements. |
| Processes | Pr | Activity-based behavior: activities, their inputs and outputs, actions and the flows between them. |
| States | St | State-based behavior of a structural element and how it reacts to events and actions. |
| Interaction Scenarios | Is | A time-ordered examination of the exchanges between participating elements for one scenario. |
| Information | If | The information and data definition aspect, free of implementation detail. |
| Constraints | Ct | Measurements that set performance requirements, and rules governing behavior and structure. |
| Roadmap | Rm | How elements change over time, or differ at different points in time. |
| Traceability | Tr | The mapping between elements, across viewpoints and domains, and between structure and behavior. |

**Which cells hold a view specification** (the count per cell; '-' means the cell is empty by design; Metadata Taxonomy is a placeholder for extending the profile to other domains and has no diagram type).

| Domain | Tx | Sr | Cn | Pr | St | Is | If | Ct | Rm | Tr |
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

Beyond the grid there are view specifications for the Dictionary, the Summary and Overview, Requirements, the Information Model, Parameters (Environment and Measurements) and three mappings to other standards (BPMN, IEPPV, NIEM). The Information and Parameters columns run across all layers; the information model may be conceptual or logical, and a physical schema is imported or linked rather than built in the framework.

**Recommended implementations** are SysML diagram kinds (block definition, internal block, activity, state machine, sequence, parametric, requirement), tables, matrices, timelines, BPMN diagrams, UML class diagrams, or text. They are recommendations; the metamodel does not make them requirements. A view's element list is guidance for what the view shows, not a closed set (UAF-VIEW-001).

**The 76 view specifications** (name, domain, model kind, DMM clause, recommended form, elements shown):

| View | Domain | Kind | DMM clause | Recommended form | Admits |
|---|---|---|---|---|---|
| Strategic Taxonomy | Strategic | Taxonomy (Tx) | 2.1.1 | SysML Block Definition Diagram | Capability |
| Strategic Structure | Strategic | Structure (Sr) | 2.1.2 | SysML Block Definition Diagram | ActualEnduringTask, ActualEnterprisePhase, ActualOrganization, ActualResponsibleResource, Capability, CapableElement, EnduringTask, EnterpriseGoal, EnterprisePhase, EnterpriseVision, Exhibits, OrganizationInEnterprise, WholeLifeEnterprise |
| Strategic Connectivity | Strategic | Connectivity (Cn) | 2.1.3 | SysML Block Definition Diagram; SysML Internal Block Diagram | Capability |
| Strategic States | Strategic | States (St) | 2.1.4 | SysML Block Definition Diagram | AchievedEffect, Achiever, ActualOrganization, ActualOrganizationalResource, ActualPerson, ActualPost, ActualResource, ActualResponsibleResource, ActualState, Capability, CapabilityConfiguration, DesiredEffect, Desirer, FieldedCapability, NaturalResource, OperationalAgent, OperationalPerformer, Organization, OrganizationalResource, Person, PhysicalResource, Post, Project, ResourceArchitecture, ResourceArtifact, ResourceMitigation, ResourcePerformer, Software, Technology |
| Strategic Constraints | Strategic | Constraints (Ct) | 2.1.5 | tabular format; SysML Block Definition Diagram | Capability, Measurement, PropertySet |
| Strategic Roadmap: Deployment | Strategic | Roadmap (Rm) | 2.1.6 | timeline; tabular format; SysML Block Definition Diagram | ActualEnterprisePhase, ActualOrganization, ActualPerson, ActualPost, ActualProject, ActualProjectMilestone, ActualResource, ActualResponsibleResource, Capability, CapabilityConfiguration, CapableElement, EnterprisePhase, Exhibits, ResourceArchitecture, ResourcePerformer, ResponsibleFor |
| Strategic Roadmap: Phasing | Strategic | Roadmap (Rm) | 2.1.6 | timeline; tabular format; SysML Block Definition Diagram | ActualProject, ActualProjectMilestone, ActualResource, Capability, CapabilityConfiguration, CapableElement, Exhibits, FieldedCapability, Project, ResourceArchitecture, ResourcePerformer |
| Strategic Traceability | Strategic | Traceability (Tr) | 2.1.7 | matrix; SysML Block Definition Diagram | Activity, ActualEnduringTask, Capability, CapabilityForTask, Function, Implements, MapsToCapability, OperationalActivity, StandardOperationalActivity |
| Operational Taxonomy | Operational | Taxonomy (Tx) | 2.2.1 | SysML Block Definition Diagram | Asset, CapabilityConfiguration, ConceptItem, HighLevelOperationalConcept, Location, NaturalResource, OperationalAgent, OperationalPerformer, Organization, OrganizationalResource, PhysicalResource, Post, ResourceArchitecture, ResourceArtifact, ResourcePerformer, Software |
| Operational Structure | Operational | Structure (Sr) | 2.2.2 | SysML Block Definition Diagram; SysML Internal Block Diagram | ActualLocation, Asset, Capability, CapableElement, Environment, Exhibits, IsCapableToPerform, KnownResource, LocationHolder, OperationalActivity, OperationalAgent, OperationalArchitecture, OperationalConnector, OperationalExchange, OperationalExchangeItem, OperationalInterface, OperationalMethod, OperationalParameter, OperationalPerformer, OperationalPort, OperationalRole, ProblemDomain |
| Operational Connectivity | Operational | Connectivity (Cn) | 2.2.3 | tabular format | CapabilityConfiguration, Exchange, GeoPoliticalExtentType, InformationElement, IsCapableToPerform, MeasurableElement, MeasurementSet, NaturalResource, OperationalActivity, OperationalActivityAction, OperationalActivityEdge, OperationalAgent, OperationalConnector, OperationalExchange, OperationalExchangeItem, OperationalInterface, OperationalPerformer, OperationalPort, OperationalRole, OrganizationalResource, PhysicalResource, ResourceArchitecture, ResourceArtifact, ResourcePerformer |
| Operational Processes | Operational | Processes (Pr) | 2.2.4 | SysML Activity Diagram; SysML Block Definition Diagram; BPMN Process Diagram | Activity, ActivityPerformableUnderCondition, ActualEnduringTask, ActualMeasurementSet, ActualService, Condition, EnduringTask, Implements, IsCapableToPerform, MeasurableElement, OperationalActivity, OperationalActivityAction, OperationalActivityEdge, OperationalAgent, OperationalExchange, OperationalExchangeItem, OperationalMethod, OperationalParameter, OperationalPerformer, OperationalRole, PerformsInContext, RequiredServiceLevel, ServiceSpecification, StandardOperationalActivity |
| Operational States | Operational | States (St) | 2.2.5 | SysML State Diagram | OperationalAgent, OperationalStateDescription |
| Operational Interaction Scenario | Operational | Interaction Scenarios (Is) | 2.2.6 | SysML Sequence Diagram; BPMN Collaboration Diagram | Activity, OperationalActivity, OperationalExchange, OperationalMessage, OperationalMethod, OperationalPerformer, OperationalRole |
| Operational Constraints | Operational | Constraints (Ct) | 2.2.7 | tabular format; SysML Block Definition Diagram; SysML Parametric Diagram | ConstraintBlock, DataModel, InformationElement, OperationalActivity, OperationalAgent, OperationalConstraint, OperationalExchange, OperationalPerformer, Rule, SubjectOfOperationalConstraint |
| Operational Traceability | Operational | Traceability (Tr) | 2.2.8 | matrix; SysML Block Definition Diagram | Activity, Capability, CapableElement, Exhibits, MapsToCapability, OperationalActivity, OperationalAgent, OperationalArchitecture, OperationalPerformer |
| Services Taxonomy | Services | Taxonomy (Tx) | 2.3.1 | SysML Block Definition Diagram | ActualMeasurement, ActualMeasurementSet, ActualService, Measurement, PropertySet, ProvidedServiceLevel, RequiredServiceLevel, ServicePolicy, ServiceSpecification |
| Services Structure | Services | Structure (Sr) | 2.3.2 | SysML Block Definition Diagram; SysML Internal Block Diagram | InformationElement, Measurement, OperationalExchangeItem, PropertySet, ServiceConnector, ServiceInterface, ServiceMethod, ServiceParameter, ServicePort, ServiceSpecification |
| Services Connectivity | Services | Connectivity (Cn) | 2.3.3 | SysML Block Definition Diagram; SysML Internal Block Diagram; tabular format | ActualMeasurementSet, ActualService, MeasurableElement, ProvidedServiceLevel, RequiredServiceLevel, ServiceInterface, ServiceMethod, ServiceParameter, ServicePort, ServiceSpecification |
| Services Processes | Services | Processes (Pr) | 2.3.4 | SysML Block Definition Diagram; SysML Internal Block Diagram; tabular format | InformationElement, IsCapableToPerform, OperationalExchangeItem, ServiceFunction, ServiceFunctionAction, ServiceMethod, ServiceParameter, ServiceSpecification |
| Services States | Services | States (St) | 2.3.5 | SysML State Machine Diagram | ServiceSpecification, ServiceStateDescription |
| Services Interaction Scenarios | Services | Interaction Scenarios (Is) | 2.3.6 | SysML Sequence Diagram | ServiceFunction, ServiceMessage, ServiceMethod, ServiceSpecification |
| Services Constraints | Services | Constraints (Ct) | 2.3.7 | tabular format; SysML Parametric Diagram | ConstraintBlock, Rule, ServicePolicy, ServiceSpecification |
| Services Roadmap | Services | Roadmap (Rm) | 2.3.8 | timeline; SysML Block Definition Diagram; SysML Internal Block Diagram | ActualProject, ActualProjectMilestone, MilestoneDependency, ServiceSpecification, VersionedElement, VersionOfConfiguration, VersionSuccession, WholeLifeConfiguration |
| Services Traceability | Services | Traceability (Tr) | 2.3.9 | timeline; SysML Block Definition Diagram; SysML Internal Block Diagram | Capability, Consumes, Exhibits, OperationalActivity, ServiceSpecification |
| Personnel Taxonomy | Personnel | Taxonomy (Tx) | 2.4.1 | SysML Block Definition Diagram | Organization, OrganizationalResource, Person, PhysicalResource, Post, ResourcePerformer, Responsibility |
| Personnel Structure | Personnel | Structure (Sr) | 2.4.2 | SysML Block Definition Diagram; SysML Internal Block Diagram | Command, Control, Organization, OrganizationalResource, Person, PhysicalResource, Post, ResourceConnector, ResourceExchange, ResourcePerformer, ResourceRole, Responsibility |
| Personnel Connectivity | Personnel | Connectivity (Cn) | 2.4.3 | tabular format | Activity, Command, Control, DataElement, Environment, Exchange, Function, FunctionAction, FunctionEdge, IsCapableToPerform, MeasurableElement, Measurement, MeasurementSet, Organization, OrganizationalResource, Person, PhysicalResource, Post, PropertySet, Resource, ResourceConnector, ResourceExchange, ResourceExchangeItem, ResourceInterface, ResourcePerformer, ResourcePort, ResourceRole |
| Personnel Processes | Personnel | Processes (Pr) | 2.4.4 | SysML Activity Diagram; SysML Block Definition Diagram; BPMN Process Diagram | Activity, ActivityPerformableUnderCondition, Condition, DataElement, Function, FunctionAction, FunctionEdge, Implements, IsCapableToPerform, OperationalActivity, Organization, OrganizationalResource, PerformsInContext, PhysicalResource, Post, ResourceExchange, ResourceExchangeItem, ResourceParameter, ResourcePerformer, ResourceRole |
| Personnel States | Personnel | States (St) | 2.4.5 | SysML State Diagram | Organization, OrganizationalResource, Person, PhysicalResource, Post, ResourcePerformer, ResourceStateDescription, Responsibility |
| Personnel Interaction Scenarios | Personnel | Interaction Scenarios (Is) | 2.4.6 | SysML Sequence Diagram; BPMN Collaboration Diagram | Activity, DataElement, Function, Organization, OrganizationalResource, Person, PhysicalResource, Post, ResourceExchange, ResourceExchangeItem, ResourceMessage, ResourceMethod, ResourcePerformer, ResourceRole, Responsibility |
| Personnel Constraints: Competence | Personnel | Constraints (Ct) | 2.4.7 | SysML Block Definition Diagram | ActualOrganization, ActualOrganizationalResource, ActualPerson, ActualPost, ActualResponsibility, ActualResponsibleResource, Competence, CompetenceForRole, CompetenceToConduct, Function, Organization, OrganizationalResource, Person, PhysicalResource, Post, ProvidesCompetence, RequiresCompetence, ResourcePerformer, ResourceRole, Responsibility |
| Personnel Constraints: Drivers | Personnel | Constraints (Ct) | 2.4.7 | tabular format; SysML Parametric Diagram; SysML Block Definition Diagram | Activity, ActualMeasurement, ActualMeasurementSet, Function, IsCapableToPerform, MeasurableElement, Measurement, MeasurementSet, Organization, OrganizationalResource, Person, PhysicalResource, Post, ResourceConstraint, ResourcePerformer, Responsibility, Rule, SubjectOfResourceConstraint |
| Personnel Constraints: Performance | Personnel | Constraints (Ct) | 2.4.7 | SysML Block Definition Diagram | Activity, ActivityPerformableUnderCondition, ActualMeasurement, ActualMeasurementSet, ActualOrganizationalResource, ActualPerson, ActualPost, ActualPropertySet, ActualResource, ActualResponsibleResource, ActualState, Condition, DesiredEffect, Desirer, Function, IsCapableToPerform, MeasurableElement, Measurement, MeasurementSet, Organization, OrganizationalResource, Person, PhysicalResource, Post, ResourcePerformer, Responsibility |
| Personnel Roadmap: Availability | Personnel | Roadmap (Rm) | 2.4.8 | timeline; SysML Block Definition Diagram | ActualMeasurement, ActualOrganizationalResource, ActualPerson, ActualPost, ActualProject, ActualProjectMilestone, ActualPropertySet, ActualResource, ActualResponsibleResource, ActualState, Asset, Measurement, OrganizationalResource, Person, PhysicalResource, Post, Project, ProjectMilestone, PropertySet, ResourcePerformer |
| Personnel Roadmap: Evolution | Personnel | Roadmap (Rm) | 2.4.8 | timeline; SysML Block Definition Diagram; SysML Internal Block Diagram | ActualProject, ActualProjectMilestone, MilestoneDependency, Organization, OrganizationalResource, Person, PhysicalResource, Post, ResourcePerformer, Responsibility, VersionedElement, VersionOfConfiguration, VersionSuccession, WholeLifeConfiguration |
| Personnel Roadmap: Forecast | Personnel | Roadmap (Rm) | 2.4.8 | timeline; tabular format; SysML Block Definition Diagram | ActualEnterprisePhase, ActualPropertySet, ActualState, Asset, Competence, Forecast, Organization, OrganizationalResource, Person, PhysicalResource, Post, ResourcePerformer, Responsibility, SubjectOfForecast |
| Personnel Traceability | Personnel | Traceability (Tr) | 2.4.9 | matrix; SysML Block Definition Diagram | Function, Implements, OperationalActivity, ServiceFunction |
| Resources Taxonomy | Resources | Taxonomy (Tx) | 2.5.1 | SysML Block Definition Diagram | Asset, CapabilityConfiguration, Implements, Measurement, NaturalResource, OperationalAgent, OperationalPerformer, Organization, OrganizationalResource, Person, PhysicalResource, Post, PropertySet, ResourceArchitecture, ResourceArtifact, ResourceExchange, ResourceMitigation, ResourcePerformer, ResourceRole, Responsibility, Software, System |
| Resources Structure | Resources | Structure (Sr) | 2.5.2 | SysML Internal Block Diagram | Asset, CapabilityConfiguration, Measurement, NaturalResource, PhysicalResource, PropertySet, Protocol, ProtocolImplementation, ResourceArchitecture, ResourceArtifact, ResourceConnector, ResourceExchange, ResourceInterface, ResourceMitigation, ResourcePerformer, ResourcePort, ResourceRole, Software |
| Resources Connectivity | Resources | Connectivity (Cn) | 2.5.3 | tabular format | Activity, CapabilityConfiguration, Exchange, Function, FunctionAction, FunctionEdge, IsCapableToPerform, MeasurableElement, Measurement, MeasurementSet, NaturalResource, Organization, OrganizationalResource, Person, PhysicalResource, Post, PropertySet, Resource, ResourceArchitecture, ResourceArtifact, ResourceConnector, ResourceExchange, ResourceExchangeItem, ResourceInterface, ResourceMitigation, ResourcePerformer, ResourcePort, ResourceRole, Software, Technology |
| Resources Processes | Resources | Processes (Pr) | 2.5.4 | SysML Activity Diagram; SysML Block Definition Diagram | Activity, ActivityPerformableUnderCondition, Condition, DataElement, Function, FunctionAction, FunctionEdge, Implements, OperationalActivity, PerformsInContext, PhysicalResource, ResourceArchitecture, ResourceExchange, ResourceExchangeItem, ResourceParameter, ResourcePerformer, ResourceRole |
| Resources States | Resources | States (St) | 2.5.5 | SysML State Diagram | ResourcePerformer, ResourceStateDescription |
| Resources Interaction Scenarios | Resources | Interaction Scenarios (Is) | 2.5.6 | SysML Sequence Diagram | Activity, Function, ResourceExchange, ResourceExchangeItem, ResourceMessage, ResourceMethod, ResourcePerformer, ResourceRole |
| Resources Constraints | Resources | Constraints (Ct) | 2.5.7 | tabular format; SysML Block Definition Diagram; SysML Parametric Diagram; OCL | ActualResource, CapabilityConfiguration, ConstraintBlock, DataElement, Function, NaturalResource, Organization, OrganizationalResource, Person, PhysicalResource, Post, ResourceArchitecture, ResourceArtifact, ResourceConstraint, ResourcePerformer, ResourceRole, Responsibility, Rule, SubjectOfResourceConstraint |
| Resources Roadmap: Evolution | Resources | Roadmap (Rm) | 2.5.8 | timeline; SysML Block Definition Diagram; SysML Internal Block Diagram | ActualProject, ActualProjectMilestone, MilestoneDependency, ResourcePerformer, VersionedElement, VersionOfConfiguration, VersionSuccession, WholeLifeConfiguration |
| Resources Roadmap: Forecast | Resources | Roadmap (Rm) | 2.5.8 | timeline; tabular format; SysML Block Definition Diagram | ActualEnterprisePhase, ActualPropertySet, ActualState, CapabilityConfiguration, Forecast, NaturalResource, PhysicalResource, ResourceArchitecture, ResourceArtifact, ResourceMitigation, ResourcePerformer, Software, SubjectOfForecast, Technology |
| Resources Traceability | Resources | Traceability (Tr) | 2.5.9 | matrix; SysML Block Definition Diagram | Function, Implements, IsCapableToPerform, OperationalActivity, OperationalAgent, ResourcePerformer, ServiceFunction |
| Security Taxonomy | Security | Taxonomy (Tx) | 2.6.1 | SysML Internal Block Diagram; SysML Block Definition Diagram | ActualLocation, Asset, DataElement, InformationElement, LocationHolder, Measurement, MeasurementSet, OperationalAgent, OperationalPerformer, PropertySet, ResourceArchitecture, ResourcePerformer, SecurityAvailability, SecurityCategory, SecurityClassification, SecurityClassificationKind, SecurityEnclave, SecurityIntegrity, SecurityMeasurement |
| Security Structure | Security | Structure (Sr) | 2.6.2 | SysML Internal Block Diagram; SysML Block Definition Diagram | Asset, DataElement, InformationElement, OperationalAgent, OperationalConnector, OperationalExchange, OperationalPerformer, OperationalPort, OperationalRole, ResourceConnector, ResourceExchange, ResourcePerformer, ResourcePort, ResourceRole, SecurityCategory, SecurityProperty |
| Security Connectivity | Security | Connectivity (Cn) | 2.6.3 | tabular format | Asset, Caveat, MeasurableElement, MeasurementSet, OperationalAgent, OperationalConnector, OperationalExchange, OperationalExchangeItem, OperationalInterface, OperationalPerformer, OperationalPort, OperationalRole, ResourceConnector, ResourceExchange, ResourceExchangeItem, ResourceInterface, ResourcePerformer, ResourcePort, ResourceRole, SecurityConstraint, SubjectOfSecurityConstraint |
| Security Processes | Security | Processes (Pr) | 2.6.4 | SysML Activity Diagram; SysML Block Definition Diagram | Activity, Asset, EnhancedSecurityControl, Enhances, Function, FunctionAction, IsCapableToPerform, MeasurableElement, MeasurementSet, OperationalActivity, OperationalActivityAction, OperationalAgent, OperationalRole, PerformsInContext, Protects, ProtectsInContext, ResourcePerformer, ResourceRole, SecurityControl, SecurityControlAction, SecurityControlFamily |
| Security Constraints | Security | Constraints (Ct) | 2.6.5 | tabular or matrix format; SysML Block Definition Diagram; SysML Parametric Diagram; OCL | ActualMeasurement, ActualPropertySet, ActualResource, ActualResponsibleResource, ActualRisk, Affects, Asset, AssetRole, Measurement, OperationalAgent, OperationalRole, PropertySet, ResourcePerformer, ResourceRole, Risk, Rule, SecurityConstraint, SubjectOfSecurityConstraint |
| Security Traceability | Security | Traceability (Tr) | 2.6.6 | matrix; SysML Block Definition Diagram | Affects, AssetRole, Mitigates, OperationalRole, OwnsRisk, ResourceRole, Risk, SecurityProperty |
| Project Taxonomy | Projects | Taxonomy (Tx) | 2.7.1 | SysML Block Definition Diagram | ActualProject, ActualProjectMilestone, MilestoneDependency, Project, ProjectMilestone, ProjectMilestoneRole, ProjectSequence |
| Project Structure | Projects | Structure (Sr) | 2.7.2 | SysML Block Definition Diagram | ActualOrganization, ActualPost, ActualProject, ActualPropertySet, ActualResponsibleResource, ActualState, Project, ProjectMilestone, ProjectMilestoneRole, ProjectTheme, ResourceRole, ResponsibleFor, StatusIndicators |
| Project Connectivity | Projects | Connectivity (Cn) | 2.7.3 | SysML Block Definition Diagram | Project, ProjectMilestone, ProjectMilestoneRole, ResourcePerformer |
| Project Processes | Projects | Processes (Pr) | 2.7.4 | SysML Activity Diagram; SysML Block Definition Diagram | ActualProject, DataElement, Function, FunctionAction, FunctionEdge, GeoPoliticalExtentType, IsCapableToPerform, Organization, OrganizationalResource, PerformsInContext, PhysicalResource, Post, Project, ProjectActivity, ProjectActivityAction, ResourceExchange, ResourceExchangeItem, ResourcePerformer, ResourceRole, ResourceSignal |
| Project Roadmap | Projects | Roadmap (Rm) | 2.7.5 | timeline; tabular format; SysML Block Definition Diagram | ActualProject, ActualProjectMilestone, ActualProjectMilestoneRole, ActualPropertySet, ActualResource, ActualState, CapabilityConfiguration, FieldedCapability, MilestoneDependency, Project, ProjectMilestone, ProjectMilestoneRole, ProjectSequence, ProjectStatus, ProjectTheme, ResourceArchitecture, ResourcePerformer, StatusIndicators |
| Project Traceability | Projects | Traceability (Tr) | 2.7.6 | matrix; SysML Block Definition Diagram | ActualProject, ActualProjectMilestone, ActualResource, Capability, CapableElement, Exhibits, ResourcePerformer |
| Standards Taxonomy | Standards | Taxonomy (Tx) | 2.8.1 | SysML Block Definition Diagram | ActualOrganization, CapabilityConfiguration, Protocol, ProtocolStack, ResourceArchitecture, ResourcePerformer, Standard, StandardOperationalActivity, UAFElement |
| Standards Structure | Standards | Structure (Sr) | 2.8.2 | SysML Internal Block Diagram | Protocol, ProtocolLayer, ProtocolStack, Standard |
| Standards Roadmap | Standards | Roadmap (Rm) | 2.8.3 | timeline; tabular format; SysML Block Definition Diagram | ActualEnterprisePhase, Forecast, Protocol, Standard, SubjectOfForecast |
| Standards Traceability | Standards | Traceability (Tr) | 2.8.4 | tabular format; matrix format; SysML Block Definition Diagram | Protocol, Standard, UAFElement |
| Actual Resources Taxonomy | Actual Resources | Taxonomy (Tx) | 2.9.1 | SysML Block Definition Diagram; SysML Internal Block Diagram | ActualMeasurement, ActualOrganization, ActualOrganizationalResource, ActualPerson, ActualPost, ActualPropertySet, ActualResource, ActualResponsibility, ActualResponsibleResource, CapabilityConfiguration, FieldedCapability, Organization, Person, Post, ResourcePerformer, Responsibility |
| Actual Resources Structure | Actual Resources | Structure (Sr) | 2.9.2 | SysML Block Definition Diagram; SysML Internal Block Diagram | ActualOrganization, ActualOrganizationalResource, ActualPerson, ActualPost, ActualResource, ActualResponsibility, ActualResponsibleResource, CapabilityConfiguration, Competence, FieldedCapability, Organization, Person, Post, ProvidesCompetence, ResourcePerformer, Responsibility, ResponsibleFor |
| Actual Resources Connectivity | Actual Resources | Connectivity (Cn) | 2.9.3 | tabular format; SysML Block Definition Diagram; SysML Internal Block Diagram; SysML Sequence Diagram | ActualOrganization, ActualOrganizationalResource, ActualPerson, ActualPost, ActualResource, ActualResourceRelationship, ActualResponsibility, ActualResponsibleResource, FieldedCapability |
| Dictionary | Dictionary | Dictionary (Dc) | 2.10 | text; table format | Alias, Definition, Information, SameAs, UAFElement |
| Summary & Overview | Summary and Overview | Summary and Overview (SmOv) | 2.11 | text; free form diagram; table format | ActualEnterprisePhase, ActualOrganizationalResource, ArchitecturalDescription, ArchitecturalReference, Architecture, ArchitectureMetadata, Concern, EnterprisePhase, Exhibits, Metadata, OperationalArchitecture, OrganizationalResource, PropertySet, ResourceArchitecture, Stakeholder, View, Viewpoint, WholeLifeEnterprise |
| Requirements | Requirements | Requirements (Rq) | 2.12 | SysML Requirement Diagram; tabular format; matrix format | Refine, Requirement, Satisfy, Trace, UAFElement, Verify |
| Information Model | Information | Information (If) | 2.13 | SysML Block Definition Diagram | DataElement, DataModel, Implements, InformationElement |
| Parameters: Environment | Parameters | Parameters (Pm) | 2.14 | SysML Block Definition Diagram | Activity, ActualCondition, ActualEnvironment, ActualLocation, ActualPropertySet, ActualResource, Asset, Condition, Environment, EnvironmentProperty, GeoPoliticalExtentType, Location, LocationHolder, OperationalRole, ResourcePerformer, ResourceRole |
| Parameters: Measurements | Parameters | Parameters (Pm) | 2.14 | SysML Block Definition Diagram | ActualMeasurement, ActualMeasurementSet, ActualPropertySet, ActualService, ActualState, Capability, Competence, Condition, EnterprisePhase, MeasurableElement, Measurement, MeasurementSet, Project, PropertySet, ProvidedServiceLevel, RequiredServiceLevel, Resource, ServiceInterface, ServiceSpecification |
| BPMN | Other | Other (Ot) | 2.15 | BPMN Process Diagram | InformationElement, IsCapableToPerform, OperationalActivity, OperationalActivityAction, OperationalActivityEdge, OperationalAgent, OperationalExchange, OperationalExchangeItem, OperationalPerformer, OperationalRole, PerformsInContext, ResourcePerformer |
| IEPPV | Other | Other (Ot) | 2.15 | UML Class Diagram; SysML Block Diagram | Abstraction, FilteredSemanticElement, InformationElement, InformationSpecification, Message, OperationalExchange, OperationalExchangeItem |
| NIEM | Other | Other (Ot) | 2.15 | UML Class Diagram; SysML Block Diagram | Abstraction, DataElement, DataModel, DataObject, InformationElement, InformationModel |

Stakeholders and concerns for each view are in the specification (DMM clause 2); in summary, strategic views serve capability portfolio managers and enterprise architects; operational views, business architects and systems engineers; services, solution providers and software architects; personnel, human-resources staff; resources, systems engineers and implementers; security, security architects, security engineers and risk analysts; projects, program and portfolio managers; standards, solution providers and architects.

## 6. The element catalog (profile clause 7.1)

The profile defines 226 elements in packages that mirror the grid: Dictionary, Parameters, Metadata, Strategic, Operational, Services, Personnel, Resources, Security, Project, Standards, Actual Resources, and Summary and Overview. Each entry gives its package, whether it is abstract, its generalizations, the UML metaclass it extends, a description, its attributes and association ends, and its constraints. Thirty-three are abstract groupings. Fifteen are enumerations (and StatusIndicators, an enumerated type). The nine elements in the last rows marked 'DMM only' exist only in the domain metamodel. 'Kind' is a classification used by this library, not by the standard.


#### Dictionary

| Concept | Clause | Kind | Generalization | Abstract | Extends | In | Definition |
|---|---|---|---|---|---|---|---|
| Alias | 7.1.1 | annotation | MeasurableElement | no | Comment | UAFP+DMM | An alternative name recorded for an element. |
| Definition | 7.1.1 | annotation | MeasurableElement | no | Comment | UAFP+DMM | A textual description of an element of the architecture. |
| SameAs | 7.1.1 | relationship | MeasurableElement | no | Dependency | UAFP+DMM | Asserts that two elements denote the same real-world thing. |

#### Parameters

| Concept | Clause | Kind | Generalization | Abstract | Extends | In | Definition |
|---|---|---|---|---|---|---|---|
| ActualCondition | 7.1.2 | actual | ActualPropertySet | no | InstanceSpecification | UAFP+DMM | The actual situation of an environment or location, with a time span. |
| ActualEnvironment | 7.1.2 | actual | ActualCondition | no | InstanceSpecification | UAFP+DMM | The actual circumstances of an Environment. |
| ActualLocation | 7.1.2 | actual | ActualCondition | no | InstanceSpecification | UAFP+DMM | An actual physical place, described for example by an address or coordinates. |
| ActualMeasurement | 7.1.2 | actual | ActualState | no | Slot | UAFP+DMM | A real, required or estimated value given to a Measurement. |
| ActualMeasurementKind | 7.1.2 | enumeration | - | no | enumeration | UAFP only | Says whether an ActualMeasurement is a real-world value, a required value or an estimate. Literals: Actual, Required, Estimate. |
| ActualMeasurementSet | 7.1.2 | actual | ActualPropertySet | no | InstanceSpecification | UAFP+DMM | A group of ActualMeasurements. |
| ActualPropertySet | 7.1.2 | actual | ActualState | no | InstanceSpecification | UAFP+DMM | A group of actual property values held by an element. |
| Condition | 7.1.2 | type | PropertySet (also ValueType) | no | DataType | UAFP+DMM | The location, environment or geopolitical extent in which an activity can be performed. |
| Environment | 7.1.2 | type | Condition | no | DataType | UAFP+DMM | The environmental factors in which something exists or works. |
| EnvironmentKind | 7.1.2 | enumeration | - | no | enumeration | UAFP only | The kind of an Environment. Literals: TerrainType, WeatherConditions, LightConditions, CBRNEnvironment, SituationType. |
| EnvironmentProperty | 7.1.2 | usage | MeasurableElement | no | Property | UAFP+DMM | A property of an Environment typed by a Condition (a Location, GeoPoliticalExtentType or Environment). |
| GeoPoliticalExtentType | 7.1.2 | type | ResourceExchangeItem, OperationalExchangeItem, Condition | no | DataType | UAFP+DMM | A geospatial extent whose borders are set by agreement or declaration of political parties. |
| GeoPoliticalExtentTypeKind | 7.1.2 | enumeration | - | no | enumeration | UAFP only | The kind of a GeoPoliticalExtentType. Literals: GeoFeatureType, RegionOfCountryType, CountryType, RegionOfWorldType, FacilityType, SiteType, InstallationType, OtherType. |
| Location | 7.1.2 | type | ConceptItem, Condition | no | DataType | UAFP+DMM | The general area in which a LocationHolder must be. |
| LocationHolder | 7.1.2 | abstract | UAFElement | yes | Element | UAFP+DMM | Grouping of elements that may be tied to a Location. |
| LocationKind | 7.1.2 | enumeration | - | no | enumeration | UAFP only | The shape or form of an ActualLocation. Literals: SolidVolume, Surface, Line, Point, GeoStationaryPoint, PlanarSurface, PolygonArea, RectangularArea, ElipticalArea, CircularArea, Other. |
| LocationTypeKind | 7.1.2 | enumeration | - | no | enumeration | UAFP only | The shape or form of a Location type. Literals: OtherType, SolidVolumeType, SurfaceType, LineType, PointType, GeoStationaryPointType, PlanarSurfaceType, PolygonAreaType, RectangularAreaType, ElipticalAreaType, CircularAreaType. |
| MeasurableElement | 7.1.2 | abstract | UAFElement | yes | Element | UAFP+DMM | Grouping of elements to which MeasurementSets can be applied. |
| Measurement | 7.1.2 | usage | MeasurableElement | no | Property | UAFP+DMM | A measurable property of something in the physical world, in a unit of measure. |
| MeasurementSet | 7.1.2 | type | PropertySet (also ValueType) | no | DataType | UAFP+DMM | A collection of Measurements. |
| PropertySet | 7.1.2 | abstract | UAFElement | yes | Element | UAFP+DMM | Grouping of architectural elements that can own Measurements. |

#### Metadata

| Concept | Clause | Kind | Generalization | Abstract | Extends | In | Definition |
|---|---|---|---|---|---|---|---|
| ActualState | 7.1.3.1 | abstract | UAFElement | yes | Element | UAFP+DMM | Gives a time span (start and end) to elements realized as instances. |
| ISO8601DateTime | 7.1.3.1 | type | UAFElement | no | LiteralString | UAFP+DMM | A date and time written in the ISO 8601 format with time zone. |
| Exchange | 7.1.3.2 | relationship | MeasurableElement (also ItemFlow) | yes | InformationFlow | UAFP+DMM | Grouping of OperationalExchange and ResourceExchange, the flows of Resources. |
| Resource | 7.1.3.2 | abstract | PropertySet | yes | Element | UAFP+DMM | Grouping of everything an Exchange can convey. |
| Activity | 7.1.3.3 | abstract | MeasurableElement | yes | Activity | UAFP+DMM | Grouping of behaviors (OperationalActivity, Function) that a performer can carry out. |
| CapableElement | 7.1.3.3 | abstract | UAFElement | yes | Element | UAFP+DMM | Grouping of structural elements that can perform behavior. |
| IsCapableToPerform | 7.1.3.3 | relationship | MeasurableElement (also Allocate) | no | Abstraction | UAFP+DMM | Traces a CapableElement to an Activity it can perform. |
| PerformsInContext | 7.1.3.3 | relationship | MeasurableElement (also Allocate) | no | Abstraction | UAFP+DMM | Says a role performs an action in a particular context or configuration. |
| ArchitectureMetadata | 7.1.3.4 | annotation | Metadata | no | Comment | UAFP+DMM | Extra facts about an ArchitecturalDescription, such as method and notation used. |
| Information | 7.1.3.4 | annotation | MeasurableElement | no | Comment | UAFP+DMM | Describes the state of something of interest in any medium. |
| InformationKind | 7.1.3.4 | enumeration | - | no | enumeration | UAFP only | The kind of an Information item. Literals: Information, DomainInformation, PositionReferenceFrame, PedigreeInformation, Data. |
| Metadata | 7.1.3.4 | annotation | MeasurableElement | no | Comment | UAFP+DMM | A comment attached to any element that links it to a semantic-web style category and scheme. |
| Rule | 7.1.3.5 | abstract | MeasurableElement | yes | Constraint | UAFP+DMM | Grouping of every kind of constraint. |
| RuleKind | 7.1.3.5 | enumeration | - | no | enumeration | UAFP only | The kind of a Rule. Literals: StructuralAssertion, ActionAssertion, Derivation, Contract, Constraint, Guidance, SecurityPolicy, Caveat. |
| ArchitecturalReference | 7.1.3.6 | relationship | MeasurableElement | no | Dependency | UAFP+DMM | States that one architectural description refers to another. |
| Implements | 7.1.3.6 | relationship | MeasurableElement (also Allocate) | no | Abstraction | UAFP+DMM | Traces an element at a lower level of abstraction to the equivalent element it implements above. |
| ActivityPerformableUnderCondition | 3.1.1.4 (DMM) | type | MeasurableElement | no | - | DMM only | The environment under which an Activity is performed. |

#### Strategic

| Concept | Clause | Kind | Generalization | Abstract | Extends | In | Definition |
|---|---|---|---|---|---|---|---|
| ActualEnterprisePhase | 7.1.4.1 | actual | ActualPropertySet, CapableElement, Achiever | no | InstanceSpecification | UAFP+DMM | An actual phase of an enterprise endeavor, with dates. |
| Capability | 7.1.4.1 | type | PropertySet, Desirer (also Block) | no | Class | UAFP+DMM | An enterprise's ability to achieve a desired effect, measured by specified measures. |
| EnterpriseGoal | 7.1.4.1 | type | PropertySet (also Requirement) | no | Class | UAFP+DMM | A continuing state or condition the enterprise wants to bring about; amplifies a vision. |
| EnterprisePhase | 7.1.4.1 | type | PropertySet, CapableElement (also Block) | no | Class | UAFP+DMM | A current or future state of the whole-life enterprise or of another phase. |
| EnterpriseVision | 7.1.4.1 | type | PropertySet (also Block) | no | Class | UAFP+DMM | The future state the enterprise wants, without saying how to reach it. |
| VisionStatement | 7.1.4.1 | annotation | MeasurableElement | no | Comment | UAFP+DMM | A comment that words an EnterpriseVision. |
| WholeLifeEnterprise | 7.1.4.1 | type | EnterprisePhase | no | Class | UAFP+DMM | A purposeful endeavor of any size made of structural and temporal parts. |
| CapabilityProperty | 7.1.4.2 | usage | MeasurableElement | no | Property | UAFP+DMM | A Capability used as a part of another Capability. |
| StructuralPart | 7.1.4.2 | usage | MeasurableElement | no | Property | UAFP only | An EnterprisePhase used as a spatial part of another. |
| TemporalPart | 7.1.4.2 | usage | MeasurableElement | no | Property | UAFP only | An EnterprisePhase used as a temporal part of another. |
| ActualEnduringTask | 7.1.4.3 | actual | CapableElement, ActualPropertySet | no | InstanceSpecification | UAFP+DMM | An actual undertaking the enterprise treats as essential to its goals. |
| CapabilityForTask | 7.1.4.3 | relationship | MeasurableElement (also Allocate) | no | Abstraction | UAFP+DMM | Says a Capability is needed for an enterprise to conduct a phase of an enduring task. |
| EnduringTask | 7.1.4.3 | type | PropertySet (also Block) | no | Class | UAFP+DMM | A template for a strategic statement of what the enterprise does. |
| AchievedEffect | 7.1.4.4 | relationship | MeasurableElement | no | Dependency | UAFP+DMM | Links an achiever's actual state to the desired effect it attempts to meet. |
| Achiever | 7.1.4.4 | abstract | UAFElement | yes | InstanceSpecification | UAFP+DMM | Grouping of actual elements that can deliver a desired effect. |
| DesiredEffect | 7.1.4.4 | relationship | MeasurableElement | no | Dependency | UAFP+DMM | Links a desirer to the actual state it wants. |
| Desirer | 7.1.4.4 | abstract | UAFElement | yes | Class | UAFP+DMM | Grouping of elements that can desire an effect. |
| Exhibits | 7.1.4.5 | relationship | MeasurableElement (also Allocate) | no | Abstraction | UAFP+DMM | Says a capable element meets a Capability under given conditions. |
| MapsToCapability | 7.1.4.5 | relationship | MeasurableElement (also Allocate) | no | Abstraction | UAFP+DMM | Says an Activity contributes to providing a Capability. |
| OrganizationInEnterprise | 7.1.4.5 | relationship | MeasurableElement (also Allocate) | no | Abstraction | UAFP+DMM | Places an actual organization in an actual enterprise phase. |

#### Operational

| Concept | Clause | Kind | Generalization | Abstract | Extends | In | Definition |
|---|---|---|---|---|---|---|---|
| ArbitraryConnector | 7.1.5.1 | relationship | MeasurableElement | no | Dependency | UAFP only | A drawn link between concept roles in a high-level operational concept. |
| ConceptItem | 7.1.5.1 | abstract | UAFElement | yes | Element | UAFP+DMM | Grouping of items that can appear in a high-level operational concept. |
| ConceptRole | 7.1.5.1 | usage | MeasurableElement | no | Property | UAFP only | A ConceptItem used within a high-level operational concept. |
| HighLevelOperationalConcept | 7.1.5.1 | type | PropertySet (also Block) | no | Class | UAFP+DMM | The resources and locations needed for an operational scenario, seen as a whole. |
| KnownResource | 7.1.5.2 | type | OperationalPerformer, ResourcePerformer | no | Class | UAFP+DMM | A known resource that plays a part in the operational architecture. |
| OperationalAgent | 7.1.5.2 | abstract | Asset, SubjectOfOperationalConstraint, CapableElement, Desirer | yes | Class | UAFP+DMM | Grouping of operational performers and operational architectures. |
| OperationalArchitecture | 7.1.5.2 | type | OperationalAgent, Architecture | no | Class | UAFP+DMM | A model of the architecture seen from the operational side. |
| OperationalMethod | 7.1.5.2 | usage | MeasurableElement | no | Operation | UAFP+DMM | A behavior of an OperationalPerformer, specified by an OperationalActivity. |
| OperationalParameter | 7.1.5.2 | usage | MeasurableElement | no | Parameter | UAFP+DMM | An input or output of an OperationalActivity, typed by an exchange item. |
| OperationalPerformer | 7.1.5.2 | type | OperationalAgent | no | Class | UAFP+DMM | A logical performer able to carry out operational activities that produce and use resources. |
| OperationalPort | 7.1.5.2 | usage | MeasurableElement (also ProxyPort) | no | Port | UAFP+DMM | An interaction point of an OperationalPerformer defined by an OperationalInterface. |
| OperationalRole | 7.1.5.2 | usage | MeasurableElement, LocationHolder, SubjectOfSecurityConstraint, AssetRole | no | Property | UAFP+DMM | Use of an operational agent as a part within another agent. |
| ProblemDomain | 7.1.5.2 | usage | OperationalRole | no | Property | UAFP+DMM | The part of an operational architecture that sets the scope of the problem. |
| OperationalConnector | 7.1.5.3 | relationship | MeasurableElement | no | Connector | UAFP+DMM | A channel between operational roles that can carry operational exchanges. |
| OperationalExchange | 7.1.5.3 | relationship | Exchange, SubjectOfOperationalConstraint | no | InformationFlow | UAFP+DMM | A flow that can exist between operational performers (information, people, materiel, energy). |
| OperationalExchangeItem | 7.1.5.3 | abstract | Resource | yes | - | UAFP+DMM | Grouping of what an OperationalExchange can convey. |
| OperationalExchangeKind | 7.1.5.3 | enumeration | - | no | enumeration | UAFP only | The kind of thing an OperationalExchange conveys. Literals: MaterielExchange, OrganizationalExchange, EnergyExchange, InformationExchange, ConfigurationExchange, GeoPoliticalExtentExchange. |
| OperationalInterface | 7.1.5.3 | type | PropertySet (also InterfaceBlock) | no | Class | UAFP+DMM | A contract between an OperationalPerformer and those it interacts with. |
| OperationalSignal | 7.1.5.3 | behavior | OperationalExchangeItem | no | Signal | UAFP only | An asynchronous communication between operational performers with no reply. |
| OperationalSignalProperty | 7.1.5.3 | usage | MeasurableElement | no | Property | UAFP only | A property of an OperationalSignal typed by an exchange item. |
| OperationalActivity | 7.1.5.4 | behavior | Activity, SubjectOfOperationalConstraint | no | Activity | UAFP+DMM | A logical process described independently of how it is carried out. |
| OperationalActivityAction | 7.1.5.4 | behavior | MeasurableElement | no | CallBehaviorAction | UAFP+DMM | A call of an OperationalActivity inside another. |
| OperationalActivityEdge | 7.1.5.4 | relationship | MeasurableElement | yes | ActivityEdge | UAFP+DMM | Grouping of operational control flows and object flows. |
| OperationalControlFlow | 7.1.5.4 | relationship | OperationalActivityEdge | no | ControlFlow | UAFP only | Flow of control between operational actions. |
| OperationalObjectFlow | 7.1.5.4 | relationship | OperationalActivityEdge | no | ObjectFlow | UAFP only | Flow of resources between operational actions. |
| StandardOperationalActivity | 7.1.5.4 | behavior | OperationalActivity | no | Activity | UAFP+DMM | An operational activity that is a standard operating procedure. |
| OperationalStateDescription | 7.1.5.5 | behavior | MeasurableElement | no | StateMachine | UAFP+DMM | A state machine for how an operational agent reacts to events. |
| OperationalMessage | 7.1.5.6 | relationship | MeasurableElement | no | Message | UAFP+DMM | A message in an operational event trace that carries an operational exchange. |
| InformationElement | 7.1.5.7 | type | Asset, OperationalExchangeItem, SubjectOfOperationalConstraint | no | Class | UAFP+DMM | An item of information flowing between operational performers. |
| OperationalConstraint | 7.1.5.8 | type | Rule | no | Constraint | UAFP+DMM | A rule governing an operational element. |
| SubjectOfOperationalConstraint | 7.1.5.8 | abstract | UAFElement | yes | Element | UAFP+DMM | Grouping of elements an OperationalConstraint may govern. |

#### Services

| Concept | Clause | Kind | Generalization | Abstract | Extends | In | Definition |
|---|---|---|---|---|---|---|---|
| ServiceSpecification | 7.1.6.1 | type | PropertySet, VersionedElement, CapableElement (also Block) | no | Class | UAFP+DMM | The specification of a set of functionality one element provides for others. |
| ServiceMethod | 7.1.6.2 | usage | MeasurableElement | no | Operation | UAFP+DMM | A behavior of a ServiceSpecification, specified by a ServiceFunction. |
| ServiceParameter | 7.1.6.2 | usage | MeasurableElement | no | Parameter | UAFP+DMM | An input or output of a ServiceFunction or service specification. |
| ServicePort | 7.1.6.2 | usage | MeasurableElement (also ProxyPort) | no | Port | UAFP+DMM | An interaction point of a service specification defined by a ServiceInterface. |
| ServiceSpecificationRole | 7.1.6.2 | usage | MeasurableElement | no | Property | UAFP only | Use of a service specification as a part of another. |
| ServiceConnector | 7.1.6.3 | relationship | MeasurableElement | no | Connector | UAFP+DMM | A channel between two service specifications, one consuming the other. |
| ServiceInterface | 7.1.6.3 | type | PropertySet (also InterfaceBlock) | no | Class | UAFP+DMM | A contract naming the methods and message handlers a service specification realizes. |
| ServiceFunction | 7.1.6.4 | behavior | Activity | no | Activity | UAFP+DMM | The abstract behavior of service specifications regardless of implementation. |
| ServiceFunctionAction | 7.1.6.4 | behavior | MeasurableElement | no | CallBehaviorAction | UAFP+DMM | A call of a ServiceFunction inside another. |
| ServiceStateDescription | 7.1.6.5 | behavior | MeasurableElement | no | StateMachine | UAFP+DMM | A state machine for how a service specification reacts to events. |
| ServiceMessage | 7.1.6.6 | relationship | MeasurableElement | no | Message | UAFP+DMM | A message in a service event trace. |
| ServicePolicy | 7.1.6.7 | type | Rule | no | Constraint | UAFP+DMM | A constraint governing the use of service specifications. |
| Consumes | 7.1.6.8 | relationship | MeasurableElement (also Allocate) | no | Abstraction | UAFP+DMM | Says a service helps carry out an operational activity. |

#### Personnel

| Concept | Clause | Kind | Generalization | Abstract | Extends | In | Definition |
|---|---|---|---|---|---|---|---|
| Organization | 7.1.7.1 | type | OrganizationalResource | no | Class | UAFP+DMM | A group of persons, posts, organizations and responsibilities for a purpose. |
| OrganizationalResource | 7.1.7.1 | abstract | PhysicalResource, Stakeholder | yes | Class | UAFP+DMM | Grouping of Organization, Person, Post and Responsibility. |
| Person | 7.1.7.1 | type | OrganizationalResource | no | Class | UAFP+DMM | A type of human being, describing what must be known about actual persons. |
| Post | 7.1.7.1 | type | OrganizationalResource | no | Class | UAFP+DMM | A type of job or position a person can fill. |
| Responsibility | 7.1.7.1 | type | OrganizationalResource | no | Class | UAFP+DMM | A type of duty required of a person or organization. |
| Command | 7.1.7.2 | relationship | ResourceExchange | no | InformationFlow | UAFP+DMM | A resource exchange in which one organizational resource commands another. |
| Control | 7.1.7.2 | relationship | ResourceExchange | no | InformationFlow | UAFP+DMM | A resource exchange in which one physical resource controls another. |
| CompetenceToConduct | 7.1.7.3 | relationship | MeasurableElement (also Allocate) | no | Abstraction | UAFP+DMM | Links a Function to the competences needed to conduct it. |
| Competence | 7.1.7.4 | type | SubjectOfForecast, PropertySet (also Block) | no | Class | UAFP+DMM | A set of abilities defined by knowledge, skill and aptitude. |
| CompetenceForRole | 7.1.7.4 | relationship | MeasurableElement (also Allocate) | no | Abstraction | UAFP+DMM | Links an organizational role to the competences it requires. |
| RequiresCompetence | 7.1.7.4 | relationship | MeasurableElement (also Allocate) | no | Abstraction | UAFP+DMM | Says an organizational resource must have given competences. |
| ResponsibleFor | 7.1.7.5 | relationship | MeasurableElement (also Allocate) | no | Abstraction | UAFP+DMM | Says a responsible resource is answerable for a project or responsibility. |
| ResponsibleRoleKind | 7.1.7.5 | enumeration | - | no | enumeration | UAFP only | The kind of responsible role. Literals: Manager, ResponsibleOwner. |

#### Resources

| Concept | Clause | Kind | Generalization | Abstract | Extends | In | Definition |
|---|---|---|---|---|---|---|---|
| CapabilityConfiguration | 7.1.8.1 | type | ResourceArchitecture | no | Class | UAFP+DMM | Physical and human resources, and their interactions, assembled to meet a capability. |
| NaturalResource | 7.1.8.1 | type | PhysicalResource | no | Class | UAFP+DMM | A physical resource found in nature, such as oil, water or coal. |
| PhysicalResource | 7.1.8.1 | abstract | ResourcePerformer | yes | Class | UAFP+DMM | Grouping of organizational resources, resource artifacts and natural resources. |
| ResourceArchitecture | 7.1.8.1 | type | ResourcePerformer, Architecture | no | Class | UAFP+DMM | A model of the architecture seen from the resource side. |
| ResourceArtifact | 7.1.8.1 | type | PhysicalResource | no | Class | UAFP+DMM | A man-made object containing no human beings. |
| ResourcePerformer | 7.1.8.1 | abstract | Asset, ResourceExchangeItem, SubjectOfResourceConstraint, VersionedElement, CapableElement, SubjectOfForecast, OperationalExchangeItem, Desirer | yes | Class | UAFP+DMM | Grouping of elements that can perform functions. |
| Software | 7.1.8.1 | type | ResourceArtifact | no | Class | UAFP+DMM | A resource artifact that is an executable computer program. |
| System | 7.1.8.1 | type | ResourceArchitecture | no | Class | UAFP+DMM | An integrated set of elements that accomplish a defined objective. |
| ResourceMethod | 7.1.8.2 | usage | MeasurableElement | no | Operation | UAFP+DMM | A behavior of a ResourcePerformer, specified by a Function. |
| ResourceParameter | 7.1.8.2 | usage | MeasurableElement | no | Parameter | UAFP+DMM | An input or output of a Function, typed by a resource exchange item. |
| ResourcePort | 7.1.8.2 | usage | MeasurableElement, ProtocolImplementation (also ProxyPort) | no | Port | UAFP+DMM | An interaction point of a ResourcePerformer defined by a ResourceInterface. |
| ResourceRole | 7.1.8.2 | usage | LocationHolder, SubjectOfResourceConstraint, MeasurableElement, SubjectOfSecurityConstraint, AssetRole | no | Property | UAFP+DMM | Use of a ResourcePerformer as a part inside another. |
| RoleKind | 7.1.8.2 | enumeration | - | no | enumeration | UAFP only | The kind of role a ResourceRole plays. Literals: Part, Component, UsedConfiguration, HumanResource, Platform, System, SubOrganization, PostRole, ResponsibilityRole, Equipment, SubSystemPart, UsedPhysicalArchitecture, HostedSoftware, ArtifactComponent, NaturalResourceComponent, Other. |
| ResourceConnector | 7.1.8.3 | relationship | MeasurableElement, ProtocolImplementation | no | Connector | UAFP+DMM | A channel for exchange between two resource roles. |
| ResourceExchange | 7.1.8.3 | relationship | Exchange | no | InformationFlow | UAFP+DMM | A flow that can exist between resource performers (data, people, materiel, energy). |
| ResourceExchangeItem | 7.1.8.3 | abstract | Resource | yes | - | UAFP+DMM | Grouping of what a ResourceExchange can convey. |
| ResourceInteractionKind | 7.1.8.3 | enumeration | - | no | enumeration | UAFP only | The kind of a ResourceExchange. Literals: ResourceCommunication, ResourceMovement, ResourceEnergyFlow, GeoPoliticalExtentExchange. |
| ResourceInterface | 7.1.8.3 | type | PropertySet (also InterfaceBlock) | no | Class | UAFP+DMM | A contract between resource performers and those they interact with. |
| ResourceSignal | 7.1.8.3 | behavior | ResourceExchangeItem | no | Signal | UAFP only | An asynchronous communication between resource performers with no reply. |
| ResourceSignalProperty | 7.1.8.3 | usage | MeasurableElement | no | Property | UAFP only | A property of a ResourceSignal typed by an exchange item. |
| Function | 7.1.8.4 | behavior | Activity, SubjectOfResourceConstraint | no | Activity | UAFP+DMM | An activity described relative to the resource performer able to do it. |
| FunctionAction | 7.1.8.4 | behavior | MeasurableElement | no | CallBehaviorAction | UAFP+DMM | A call of a Function showing a ResourceRole performs it in a context. |
| FunctionControlFlow | 7.1.8.4 | relationship | FunctionEdge | no | ControlFlow | UAFP only | Flow of control between function actions. |
| FunctionEdge | 7.1.8.4 | relationship | MeasurableElement | yes | ActivityEdge | UAFP+DMM | Grouping of function control flows and object flows. |
| FunctionObjectFlow | 7.1.8.4 | relationship | FunctionEdge | no | ObjectFlow | UAFP only | Flow of resources between function actions. |
| ResourceStateDescription | 7.1.8.5 | behavior | MeasurableElement | no | StateMachine | UAFP+DMM | A state machine for how a resource performer reacts to events. |
| ResourceMessage | 7.1.8.6 | relationship | MeasurableElement | no | Message | UAFP+DMM | A message in a resource event trace that carries a resource exchange. |
| DataElement | 7.1.8.7 | type | ResourceExchangeItem, SubjectOfResourceConstraint, Asset | no | Class | UAFP+DMM | A formal representation of data managed or exchanged by systems. |
| DataModel | 7.1.8.7 | type | SubjectOfOperationalConstraint | no | Package | UAFP+DMM | A structure of data types and their relationships without implementation detail. |
| DataModelKind | 7.1.8.7 | enumeration | - | no | enumeration | UAFP only | The level of a DataModel. Literals: Conceptual, Logical, Physical. |
| ResourceConstraint | 7.1.8.8 | type | Rule | no | Constraint | UAFP+DMM | A rule governing the structure or function of an implementation. |
| SubjectOfResourceConstraint | 7.1.8.8 | abstract | UAFElement | yes | Element | UAFP+DMM | Grouping of elements a ResourceConstraint may govern. |
| Forecast | 7.1.8.9 | relationship | MeasurableElement | no | Dependency | UAFP+DMM | A planned move from one asset, standard or competence to a later one. |
| SubjectOfForecast | 7.1.8.9 | abstract | UAFElement | yes | Class | UAFP+DMM | Grouping of elements a Forecast may concern. |
| Technology | 7.1.8.9 | type | ResourceArtifact | no | Class | UAFP+DMM | A technology domain such as mechanical, electronic or mobile telephony. |
| VersionedElement | 7.1.8.9 | abstract | UAFElement | yes | Class | UAFP+DMM | Grouping of resource performers and service specifications that have versions. |
| VersionOfConfiguration | 7.1.8.9 | usage | MeasurableElement | no | Property | UAFP+DMM | A versioned element used as a version of a whole-life configuration. |
| VersionSuccession | 7.1.8.9 | relationship | MeasurableElement | no | Dependency | UAFP+DMM | Says one version of a configuration follows another. |
| WholeLifeConfiguration | 7.1.8.9 | type | PropertySet (also Block) | no | Class | UAFP+DMM | A set of versioned elements. |
| WholeLifeConfigurationKind | 7.1.8.9 | enumeration | - | no | enumeration | UAFP only | The kind of whole-life configuration. Literals: Service, ResourcePerformer, OrganizationalResource. |
| ProtocolImplementation | 7.1.8.10 | abstract | UAFElement | yes | Element | UAFP+DMM | Grouping of elements that can implement protocols. |

#### Security

| Concept | Clause | Kind | Generalization | Abstract | Extends | In | Definition |
|---|---|---|---|---|---|---|---|
| Asset | 7.1.9.1 | abstract | ConceptItem, PropertySet, LocationHolder, SubjectOfSecurityConstraint (also Block) | yes | Class | UAFP+DMM | Grouping of elements that can be the subject of security analysis. |
| OperationalMitigation | 7.1.9.1 | type | OperationalArchitecture | no | Class | UAFP+DMM | Security measures chosen to protect an operational asset against cyber risk. |
| ResourceMitigation | 7.1.9.1 | type | ResourceArchitecture | no | Class | UAFP+DMM | Security measures chosen to protect a resource asset against cyber risk. |
| SecurityEnclave | 7.1.9.1 | type | ResourceArchitecture | no | Class | UAFP+DMM | A set of information systems under one authority and one security policy. |
| AssetRole | 7.1.9.2 | abstract | UAFElement | yes | Element | UAFP+DMM | Grouping of elements that can be the subject of security analysis in a context. |
| SecurityProperty | 7.1.9.2 | usage | MeasurableElement, AssetRole | no | Property | UAFP+DMM | Assigns a security marking to an asset, including an aggregated marking. |
| EnhancedSecurityControl | 7.1.9.3 | type | SecurityControl | no | Class | UAFP+DMM | A control that adds function to, or strengthens, a basic security control. |
| Enhances | 7.1.9.3 | relationship | MeasurableElement (also DeriveReqt) | no | Abstraction | UAFP+DMM | Relates an enhanced security control to the control it enhances. |
| Protects | 7.1.9.3 | relationship | MeasurableElement | no | Dependency | UAFP+DMM | Says a security control is required to protect an asset. |
| ProtectsInContext | 7.1.9.3 | relationship | MeasurableElement | no | Dependency | UAFP+DMM | Says a security control action protects an asset in a role or connector context. |
| SecurityProcess | 7.1.9.3 | behavior | OperationalActivity, Function | no | Activity | UAFP only | A security procedure that satisfies a security control requirement. |
| SecurityProcessAction | 7.1.9.3 | behavior | OperationalActivityAction, FunctionAction | no | CallBehaviorAction | UAFP only | A call of a SecurityProcess inside another. |
| ActualRisk | 7.1.9.4 | actual | ActualPropertySet | no | InstanceSpecification | UAFP+DMM | An instance of a Risk holding its measured values. |
| Risk | 7.1.9.4 | type | PropertySet (also Block) | no | Class | UAFP+DMM | A statement of the impact of an event on assets, with a measure. |
| SecurityConstraint | 7.1.9.4 | type | Rule | no | Constraint | UAFP+DMM | A rule stating security laws, regulations, guidance and policy. |
| SecurityControl | 7.1.9.4 | type | PropertySet (also Requirement) | no | Class | UAFP+DMM | A safeguard prescribed to protect confidentiality, integrity and availability. |
| SecurityControlFamily | 7.1.9.4 | type | SecurityControl | no | Class | UAFP+DMM | A grouping of security controls on one security topic. |
| SubjectOfSecurityConstraint | 7.1.9.4 | abstract | UAFElement | yes | Element | UAFP+DMM | Grouping of elements a SecurityConstraint may govern. |
| Affects | 7.1.9.5 | relationship | MeasurableElement | no | Dependency | UAFP+DMM | Says a risk applies to an asset. |
| AffectsInContext | 7.1.9.5 | relationship | MeasurableElement | no | Dependency | UAFP only | Says a risk applies to an asset role in a context. |
| Mitigates | 7.1.9.5 | relationship | MeasurableElement | no | Dependency | UAFP+DMM | Relates a security control to a risk it manages. |
| OwnsRisk | 7.1.9.5 | relationship | MeasurableElement (also Allocate) | no | Abstraction | UAFP+DMM | Relates a risk to the organizational resource that must carry out its mitigation. |
| OwnsRiskInContext | 7.1.9.5 | relationship | MeasurableElement (also Allocate) | no | Abstraction | UAFP only | Relates a risk to the organizational role that carries out mitigation in a context. |
| SecurityControlAction | 3.1.7.3 (DMM) | type | OperationalActivityAction, FunctionAction | no | - | DMM only | A call of a SecurityControl inside another, showing how a set of controls protects an asset at an operational role. |
| Caveat | 3.1.7.4 (DMM) | type | SecurityConstraint | no | - | DMM only | A statement of alternate conditions under which a rule does not hold. |
| SecurityAvailability | 3.1.7.4 (DMM) | type | SecurityMeasurement | no | - | DMM only | A security measurement of availability; the text gives no definition. |
| SecurityCategory | 3.1.7.4 (DMM) | type | MeasurementSet | no | - | DMM only | A set of security measurements; the text gives no definition. |
| SecurityClassification | 3.1.7.4 (DMM) | type | SecurityMeasurement | no | - | DMM only | The security categories determined for each kind of information an information system handles, as confidentiality, integrity and availability impacts. |
| SecurityClassificationKind | 3.1.7.4 (DMM) | enumeration | - | no | enumeration | DMM only | The acceptable values of a security category: potential impact of low, moderate or high. Literals: low, moderate, high. |
| SecurityIntegrity | 3.1.7.4 (DMM) | type | SecurityMeasurement | no | - | DMM only | A security measurement of integrity; the text gives no definition. |
| SecurityMeasurement | 3.1.7.4 (DMM) | abstract | Measurement | yes | - | DMM only | Grouping of security measurements; the text gives no definition. |

#### Project

| Concept | Clause | Kind | Generalization | Abstract | Extends | In | Definition |
|---|---|---|---|---|---|---|---|
| ActualMilestoneKind | 7.1.10.1 | enumeration | - | no | enumeration | UAFP only | The kind of an actual project milestone. Literals: InService, Deployed, NoLongerUsed, OutOfService, Other. |
| Project | 7.1.10.1 | type | OrganizationalResource | no | Class | UAFP+DMM | A type of time-limited endeavor needed to meet capability needs. |
| ProjectKind | 7.1.10.1 | enumeration | - | no | enumeration | UAFP only | The kind of a project. Literals: Programme, Portfolio, Project, PersonnelDevelopment. |
| ProjectMilestone | 7.1.10.1 | type | PropertySet (also Block) | no | Class | UAFP+DMM | A type of event in a project by which progress is measured. |
| ProjectMilestoneRole | 7.1.10.2 | usage | MeasurableElement | no | Property | UAFP+DMM | The role a milestone plays within a project. |
| ProjectRole | 7.1.10.2 | usage | ResourceRole | no | Property | UAFP only | Use of a Project as a part of another. |
| ProjectStatus | 7.1.10.2 | actual | UAFElement | no | Slot | UAFP+DMM | The progress level of a project theme at a given milestone. |
| ProjectTheme | 7.1.10.2 | usage | MeasurableElement | no | Property | UAFP+DMM | An aspect by which project progress is measured. |
| StatusIndicators | 7.1.10.2 | enumeration | MeasurableElement (also ValueType) | no | Enumeration | UAFP+DMM | The enumerated statuses a project theme can have. |
| MilestoneDependency | 7.1.10.3 | relationship | MeasurableElement | no | Dependency | UAFP+DMM | Says one actual milestone follows another. |
| ProjectSequence | 7.1.10.3 | relationship | MeasurableElement | no | Dependency | UAFP+DMM | Says one actual project cannot start before another ends. |
| ProjectActivity | 7.1.10.4 | behavior | Function | no | Activity | UAFP only | An activity carried out during a project. |
| ProjectActivityAction | 7.1.10.4 | behavior | FunctionAction | no | CallBehaviorAction,Activity | UAFP only | A call of a ProjectActivity inside another. |
| ActualProject | 7.1.10.5 | actual | ActualOrganizationalResource, Achiever | no | InstanceSpecification | UAFP+DMM | A time-limited endeavor providing a set of actual resources. |
| ActualProjectMilestone | 7.1.10.5 | actual | ActualPropertySet | no | InstanceSpecification | UAFP+DMM | An event with a start date from which actual project progress is measured. |
| ActualProjectMilestoneRole | 7.1.10.5 | actual | ActualState | no | Slot | UAFP+DMM | An actual milestone applied to a milestone role of an actual project. |
| ActualProjectRole | 7.1.10.5 | actual | ActualState | no | Slot | UAFP only | An actual project applied to a project role. |

#### Standards

| Concept | Clause | Kind | Generalization | Abstract | Extends | In | Definition |
|---|---|---|---|---|---|---|---|
| Protocol | 7.1.11.1 | type | Standard | no | Class | UAFP+DMM | A standard for communication over a network, possibly layered. |
| ProtocolStack | 7.1.11.1 | type | Protocol | no | Class | UAFP+DMM | A protocol made of protocol layers forming a complete stack. |
| Standard | 7.1.11.1 | type | SubjectOfForecast, PropertySet (also Block) | no | Class | UAFP+DMM | A ratified, peer-reviewed specification that guides or constrains the architecture. |
| ProtocolLayer | 7.1.11.2 | usage | MeasurableElement | no | Property | UAFP+DMM | Use of a Protocol as a layer within another. |

#### Actual Resources

| Concept | Clause | Kind | Generalization | Abstract | Extends | In | Definition |
|---|---|---|---|---|---|---|---|
| ActualOrganization | 7.1.12.1 | actual | ActualResponsibleResource | no | InstanceSpecification | UAFP+DMM | An actual formal or informal organizational unit. |
| ActualOrganizationalResource | 7.1.12.1 | abstract | Stakeholder, ActualResource | yes | InstanceSpecification | UAFP+DMM | Grouping of actual organizations, persons and posts. |
| ActualPerson | 7.1.12.1 | actual | ActualResponsibleResource | no | InstanceSpecification | UAFP+DMM | An individual human being. |
| ActualPost | 7.1.12.1 | actual | ActualResponsibleResource | no | InstanceSpecification | UAFP+DMM | A specific post, an instance of a Post type. |
| ActualResource | 7.1.12.1 | actual | ActualPropertySet, SubjectOfResourceConstraint, Achiever | no | InstanceSpecification | UAFP+DMM | A role in an organization that carries authority to perform a function. |
| ActualResponsibility | 7.1.12.1 | actual | ActualOrganizationalResource | no | InstanceSpecification | UAFP+DMM | The duty required of a person or organization, as an instance. |
| ActualResponsibleResource | 7.1.12.1 | abstract | ActualOrganizationalResource | yes | InstanceSpecification | UAFP+DMM | Grouping of responsible actual organizational resources. |
| FieldedCapability | 7.1.12.1 | actual | ActualResource | no | InstanceSpecification | UAFP+DMM | An actual, fully realized capability typed by a CapabilityConfiguration. |
| ActualOrganizationRole | 7.1.12.2 | actual | ActualResourceRole | no | Slot | UAFP only | An actual organizational resource applied to a resource role. |
| ActualResourceRole | 7.1.12.2 | actual | UAFElement | no | Slot | UAFP only | An instance of a resource performer in a role. |
| ActualResourceRelationship | 7.1.12.3 | relationship | UAFElement (also ItemFlow) | no | InformationFlow | UAFP+DMM | Relates actual resources that can carry out an actual responsibility. |
| FillsPost | 7.1.12.3 | relationship | MeasurableElement (also Allocate) | no | Abstraction | UAFP only | Says an actual person fills an actual post. |
| ActualService | 7.1.12.4 | actual | ActualMeasurementSet, ActualPropertySet | no | InstanceSpecification | UAFP+DMM | An instance of a ServiceSpecification. |
| ProvidedServiceLevel | 7.1.12.4 | actual | ActualService | no | InstanceSpecification | UAFP+DMM | A service level the provider actually delivers. |
| ProvidesCompetence | 7.1.12.4 | relationship | MeasurableElement | no | Dependency | UAFP+DMM | Says an actual organizational resource provides given competences. |
| RequiredServiceLevel | 7.1.12.4 | actual | ActualService | no | InstanceSpecification | UAFP+DMM | A service level required of the provider. |
| OwnsProcess | 7.1.12.5 | relationship | MeasurableElement (also Allocate) | no | Abstraction | UAFP only | Says an actual organizational resource owns an operational activity. |

#### Summary and Overview

| Concept | Clause | Kind | Generalization | Abstract | Extends | In | Definition |
|---|---|---|---|---|---|---|---|
| ArchitecturalDescription | 7.1.13 | type | MeasurableElement | no | Package | UAFP+DMM | A work product giving executive-level summary information about an architecture. |
| Architecture | 7.1.13 | abstract | UAFElement | yes | Class | UAFP+DMM | Grouping of generic architectures (operational and resource). |
| Concern | 7.1.13 | type | PropertySet (also Block) | no | Class | UAFP+DMM | An interest in an enterprise phase held by one or more stakeholders. |
| Stakeholder | 7.1.13 | abstract | UAFElement | yes | Element | UAFP+DMM | An individual, team or organization with an interest in an enterprise phase. |
| UAFElement | 7.1.13 | abstract | - | yes | Element | UAFP+DMM | Root grouping of every UAF element; carries a URI and a conformance link. |
| View | 7.1.13 | type | PropertySet (also View) | no | Class | UAFP+DMM | An architecture view expressing the architecture under one viewpoint. |
| Viewpoint | 7.1.13 | type | PropertySet (also Viewpoint) | no | Class | UAFP+DMM | A viewpoint framing one or more concerns for given stakeholders. |

### 6.1 Properties and association ends

| Concept | Property | Type and multiplicity | Kind |
|---|---|---|---|
| Alias | nameOwner | String[*] | attribute |
| Definition | author | String[*] | attribute |
| ActualLocation | address | String[0..1] | attribute |
| ActualLocation | customKind | String[0..1] | attribute |
| ActualLocation | locationNamedByAddress | Boolean[1] | attribute |
| ActualLocation | locationKind | LocationKind[1] | association end |
| ActualMeasurement | intention | ActualMeasurementKind[1] | association end |
| ActualMeasurementSet | appliesFor | MeasurableElement[*] | association end |
| Environment | kind | EnvironmentKind[1] | association end |
| GeoPoliticalExtentType | customKind | String[0..1] | attribute |
| GeoPoliticalExtentType | kind | GeoPoliticalExtentTypeKind[1] | association end |
| Location | customKind | String[0..1] | attribute |
| Location | kind | LocationTypeKind[1] | association end |
| LocationHolder | physicalLocation | ActualLocation[0..*] | association end |
| LocationHolder | requiredEnvironment | Environment[0..*] | association end |
| MeasurableElement | actualMeasurementSet | ActualMeasurementSet[*] | association end |
| MeasurableElement | measurementSet | MeasurementSet[*] | association end |
| Measurement | environmentalContext | Condition[0..1] | association end |
| MeasurementSet | appliesFor | MeasurableElement[*] | association end |
| ActualState | endDate | ISO8601DateTime[0..1] | attribute |
| ActualState | startDate | ISO8601DateTime[0..1] | attribute |
| Activity | activityPerformableUnderCondition | Condition[*] | association end |
| Information | informationKind | InformationKind[1] | association end |
| Metadata | category | String[0..1] | attribute |
| Metadata | dublinCoreElement | String[0..1] | attribute |
| Metadata | metaDataScheme | String[0..1] | attribute |
| Metadata | name | String[0..1] | attribute |
| Rule | ruleKind | RuleKind[1] | association end |
| ActualEnterprisePhase | goal | EnterpriseGoal[*] | association end |
| ActualEnterprisePhase | operationalArchitectureOfEnterprisePhase | OperationalArchitecture[*] | association end |
| ActualEnterprisePhase | resourceArchitectureOfEnterprisePhase | ResourceArchitecture[*] | association end |
| ActualEnterprisePhase | statementTask | ActualEnduringTask[*] | association end |
| ActualEnterprisePhase | vision | EnterpriseVision[*] | association end |
| EnterpriseGoal | benefits | String[0..*] | attribute |
| EnterpriseGoal | enterprisePhase | ActualEnterprisePhase[*] | association end |
| EnterpriseVision | statement | VisionStatement[*] | attribute |
| EnterpriseVision | enterprisePhase | ActualEnterprisePhase[0..1] | association end |
| AchievedEffect | desiredEffect | DesiredEffect[*] | association end |
| DesiredEffect | achievedEffect | AchievedEffect[*] | association end |
| Exhibits | environmentalConditions | Environment[*] | association end |
| OperationalExchange | trustlevel | Real[0..1] | attribute |
| OperationalExchange | exchangeKind | OperationalExchangeKind[0..1] | association end |
| OperationalExchangeItem | activity | OperationalActivity[*] | association end |
| OperationalActivity | affectedResource | OperationalExchangeItem[*] | association end |
| ResponsibleFor | endDate | ISO8601DateTime[0..1] | attribute |
| ResponsibleFor | startDate | ISO8601DateTime[0..1] | attribute |
| ResponsibleFor | ResponsibleRoleKind | ResponsibleRoleKind[1] | association end |
| CapabilityConfiguration | doctrine | StandardOperationalActivity[*] | association end |
| ResourcePerformer | isStandardConfiguration | Boolean[default false] | attribute |
| ResourcePerformer | milestone | ProjectMilestone[*] | association end |
| ResourceRole | RoleKind | RoleKind[1] | association end |
| ResourceConnector | boundaryCondition | Environment[*] | association end |
| ResourceExchange | exchangeKind | ResourceInteractionKind[unstated] | association end |
| ResourceExchangeItem | function | Function[*] | association end |
| Function | affectedResource | ResourceExchangeItem[*] | association end |
| DataModel | kind | DataModelKind[unstated] | association end |
| Forecast | forecastPeriod | ActualEnterprisePhase[*] | association end |
| VersionedElement | versionReleasedAtMilestone | ActualProjectMilestone[*] | association end |
| VersionedElement | versionWithdrawnAtMilestone | ActualProjectMilestone[*] | association end |
| WholeLifeConfiguration | kind | WholeLifeConfigurationKind[1] | association end |
| ProtocolImplementation | implements | Protocol[*] | association end |
| Asset | categoryCategorizesAsset | MeasurementSet[0..1] | association end |
| ActualRisk | actualRiskOwner | ActualResponsibleResource[0..1] | association end |
| ActualRisk | affectedActualResource | ActualResource[0..1] | association end |
| SecurityControl | mitigatingActualResource | ActualResource[*] | association end |
| ProjectMilestone | resource | ResourcePerformer[*] | association end |
| ActualProject | ownedMilestone | ActualProjectMilestone[*] | association end |
| ActualProject | projectKind | ProjectKind[1] | association end |
| ActualProjectMilestone | endDate | ISO8601DateTime[0] | attribute |
| ActualProjectMilestone | actualResource | ActualResource[*] | association end |
| ActualProjectMilestone | kind | ActualMilestoneKind[1] | association end |
| ActualProjectMilestone | versionReleased | VersionedElement[*] | association end |
| ActualProjectMilestone | versionWithdrawn | VersionedElement[*] | association end |
| Standard | mandatedDate | ISO8601DateTime[0..1] | attribute |
| Standard | retiredDate | ISO8601DateTime[0..1] | attribute |
| Standard | ratifiedBy | ActualOrganization[*] | association end |
| ActualOrganization | serviceType | String[0..1] | attribute |
| ActualOrganization | shortName | String[0..1] | attribute |
| ActualOrganization | ratifiedStandards | Standard[*] | association end |
| ActualResource | actualCondition | ActualCondition[0..*] | association end |
| ActualResource | milestone | ActualProjectMilestone[*] | association end |
| FillsPost | endDate | ISO8601DateTime[0..1] | attribute |
| FillsPost | startDate | ISO8601DateTime[0..1] | attribute |
| ArchitecturalDescription | approvalAuthority | String[*] | attribute |
| ArchitecturalDescription | architect | String[*] | attribute |
| ArchitecturalDescription | assumptionAndConstraint | String[*] | attribute |
| ArchitecturalDescription | creatingOrganization | String[*] | attribute |
| ArchitecturalDescription | dateCompleted | String[0..1] | attribute |
| ArchitecturalDescription | purpose | String[*] | attribute |
| ArchitecturalDescription | recommendations | String[*] | attribute |
| ArchitecturalDescription | summaryOfFindings | String[*] | attribute |
| ArchitecturalDescription | toBe | Boolean[1] | attribute |
| ArchitecturalDescription | toolsUsed | String[*] | attribute |
| ArchitecturalDescription | architectureFramework | String[1] | association end |
| ArchitecturalDescription | view | View[*] | association end |
| ArchitecturalDescription | viewPoint | Viewpoint[1] | association end |
| Architecture | describedBy | ArchitecturalDescription[*] | association end |
| Concern | systemConcern | ActualEnterprisePhase[*] | association end |
| Stakeholder | stakeholderConcern | Concern[*] | association end |
| UAFElement | URI | String[0..1] | attribute |
| UAFElement | conformsTo | Standard[*] | association end |
| View | viewpoint | Viewpoint[1] | association end |
| Viewpoint | languages | String[*] | attribute |
| Viewpoint | methods | String[*] | attribute |
| Viewpoint | purpose | String[0..1] | attribute |
| Viewpoint | concern | Concern[*] | association end |
| Viewpoint | stakeholder | Stakeholder[*] | association end |

## 7. Relationships (profile clause 7.1)

Relationships are elements that extend a UML dependency, abstraction, information flow, connector, activity edge or message. The standard gives no multiplicities for them. Their ends are limited by constraints, summarized here and stated as rules in `rules.md`.

| Relationship | Extends | Source end | Target end | Clause |
|---|---|---|---|---|
| SameAs | Dependency | UAFElement | UAFElement | 7.1.1 |
| Exchange (abstract) | InformationFlow | (not constrained) | (not constrained) | 7.1.3.2 |
| IsCapableToPerform | Abstraction | see pairs below | see pairs below | 7.1.3.3 |
| PerformsInContext | Abstraction | see pairs below | see pairs below | 7.1.3.3 |
| ArchitecturalReference | Dependency | ArchitecturalDescription | ArchitecturalDescription | 7.1.3.6 |
| Implements | Abstraction | see pairs below | see pairs below | 7.1.3.6 |
| CapabilityForTask | Abstraction | Capability | ActualEnduringTask | 7.1.4.3 |
| AchievedEffect | Dependency | Achiever | ActualState | 7.1.4.4 |
| DesiredEffect | Dependency | Desirer | ActualState | 7.1.4.4 |
| Exhibits | Abstraction | CapableElement | Capability | 7.1.4.5 |
| MapsToCapability | Abstraction | Activity | Capability | 7.1.4.5 |
| OrganizationInEnterprise | Abstraction | ActualOrganization | ActualEnterprisePhase | 7.1.4.5 |
| ArbitraryConnector | Dependency | ConceptRole | ConceptRole | 7.1.5.1 |
| OperationalConnector | Connector | OperationalRole or OperationalPort (each end) | OperationalRole or OperationalPort (each end) | 7.1.5.3 |
| OperationalExchange | InformationFlow | OperationalPerformer | OperationalPerformer | 7.1.5.3 |
| OperationalActivityEdge (abstract) | ActivityEdge | (not constrained) | (not constrained) | 7.1.5.4 |
| OperationalControlFlow | ControlFlow | OperationalActivityAction | OperationalActivityAction | 7.1.5.4 |
| OperationalObjectFlow | ObjectFlow | (not constrained) | (not constrained) | 7.1.5.4 |
| OperationalMessage | Message | (not constrained) | (not constrained) | 7.1.5.6 |
| ServiceConnector | Connector | ServicePort or ServiceSpecificationRole (each end) | ServicePort or ServiceSpecificationRole (each end) | 7.1.6.3 |
| ServiceMessage | Message | (not constrained) | (not constrained) | 7.1.6.6 |
| Consumes | Abstraction | OperationalActivity | ServiceSpecification | 7.1.6.8 |
| Command | InformationFlow | OrganizationalResource | OrganizationalResource | 7.1.7.2 |
| Control | InformationFlow | PhysicalResource | PhysicalResource | 7.1.7.2 |
| CompetenceToConduct | Abstraction | Function | Competence | 7.1.7.3 |
| CompetenceForRole | Abstraction | ResourceRole | Competence | 7.1.7.4 |
| RequiresCompetence | Abstraction | OrganizationalResource | Competence | 7.1.7.4 |
| ResponsibleFor | Abstraction | ActualResponsibleResource | ActualProject or ActualResponsibility | 7.1.7.5 |
| ResourceConnector | Connector | ResourcePort or ResourceRole (each end) | ResourcePort or ResourceRole (each end) | 7.1.8.3 |
| ResourceExchange | InformationFlow | ResourcePerformer | ResourcePerformer | 7.1.8.3 |
| FunctionControlFlow | ControlFlow | FunctionAction | FunctionAction | 7.1.8.4 |
| FunctionEdge (abstract) | ActivityEdge | (not constrained) | (not constrained) | 7.1.8.4 |
| FunctionObjectFlow | ObjectFlow | (not constrained) | (not constrained) | 7.1.8.4 |
| ResourceMessage | Message | (not constrained) | (not constrained) | 7.1.8.6 |
| Forecast | Dependency | SubjectOfForecast | SubjectOfForecast | 7.1.8.9 |
| VersionSuccession | Dependency | VersionOfConfiguration | VersionOfConfiguration | 7.1.8.9 |
| Enhances | Abstraction | EnhancedSecurityControl | SecurityControl | 7.1.9.3 |
| Protects | Dependency | SecurityControl | Asset | 7.1.9.3 |
| ProtectsInContext | Dependency | SecurityControlAction | OperationalRole or ResourceRole or OperationalConnector or ResourceConnector or SecurityProperty | 7.1.9.3 |
| Affects | Dependency | Risk | Asset | 7.1.9.5 |
| AffectsInContext | Dependency | Risk | AssetRole | 7.1.9.5 |
| Mitigates | Dependency | SecurityControl | Risk | 7.1.9.5 |
| OwnsRisk | Abstraction | OrganizationalResource | Risk | 7.1.9.5 |
| OwnsRiskInContext | Abstraction | ResourceRole | Risk | 7.1.9.5 |
| MilestoneDependency | Dependency | ActualProjectMilestone | ActualProjectMilestone | 7.1.10.3 |
| ProjectSequence | Dependency | ActualProject | ActualProject | 7.1.10.3 |
| ActualResourceRelationship | InformationFlow | ActualResource | ActualResource | 7.1.12.3 |
| FillsPost | Abstraction | ActualPerson | ActualPost | 7.1.12.3 |
| ProvidesCompetence | Dependency | ActualOrganizationalResource | Competence | 7.1.12.4 |
| OwnsProcess | Abstraction | ActualOrganizationalResource | OperationalActivity | 7.1.12.5 |

Pairs for relationships whose ends depend on each other (source end to target end):

- **IsCapableToPerform**: OperationalAgent to OperationalActivity; ServiceSpecification to ServiceFunction; ResourcePerformer to Function; Project to ProjectActivity. A Function other than a ProjectActivity is paired with a ResourcePerformer; a ProjectActivity only with a Project.
- **PerformsInContext**: OperationalRole to OperationalActivityAction; ServiceSpecificationRole to ServiceFunctionAction; ResourceRole to FunctionAction; ProjectRole to ProjectActivityAction. A FunctionAction other than a ProjectActivityAction is paired with a ResourceRole; the standard states the ProjectRole pairing for the client end only.
- **Implements**: ResourcePerformer to OperationalAgent; Function to OperationalActivity; Function to ServiceFunction; ResourceInterface to ServiceInterface; ResourceInterface to OperationalInterface; ResourceConnector to OperationalConnector; ResourceConnector to ResourceConnector; ResourceExchange to OperationalExchange; ResourceRole to OperationalRole; OperationalActivity to ActualEnduringTask; DataElement to InformationElement.

### 7.1 Typed parts, ports, instances and ownership

| Element | Property | Must be | Clause |
|---|---|---|---|
| ActualCondition | classifier | Condition | 7.1.2 |
| ActualEnvironment | classifier | Environment | 7.1.2 |
| ActualLocation | classifier | Location | 7.1.2 |
| ActualMeasurement | definingFeature | Measurement | 7.1.2 |
| ActualMeasurement | owningInstance | ActualPropertySet | 7.1.2 |
| ActualMeasurementSet | classifier | MeasurementSet | 7.1.2 |
| ActualMeasurementSet | slot | ActualMeasurement | 7.1.2 |
| ActualPropertySet | classifier | PropertySet | 7.1.2 |
| EnvironmentProperty | class | Environment | 7.1.2 |
| EnvironmentProperty | type | Condition | 7.1.2 |
| Measurement | class | PropertySet | 7.1.2 |
| ActualEnterprisePhase | classifier | EnterprisePhase | 7.1.4.1 |
| CapabilityProperty | class | Capability | 7.1.4.2 |
| CapabilityProperty | type | Capability | 7.1.4.2 |
| StructuralPart | class | EnterprisePhase | 7.1.4.2 |
| StructuralPart | type | EnterprisePhase | 7.1.4.2 |
| TemporalPart | class | EnterprisePhase | 7.1.4.2 |
| TemporalPart | type | EnterprisePhase | 7.1.4.2 |
| ActualEnduringTask | classifier | EnduringTask | 7.1.4.3 |
| ConceptRole | class | HighLevelOperationalConcept | 7.1.5.1 |
| ConceptRole | type | ConceptItem | 7.1.5.1 |
| OperationalMethod | method | OperationalActivity | 7.1.5.2 |
| OperationalMethod | ownedParameter | OperationalParameter | 7.1.5.2 |
| OperationalParameter | type | OperationalExchangeItem | 7.1.5.2 |
| OperationalPerformer | ownedOperation | OperationalMethod | 7.1.5.2 |
| OperationalPerformer | ownedPort | OperationalPort | 7.1.5.2 |
| OperationalPort | class | OperationalPerformer | 7.1.5.2 |
| OperationalPort | type | OperationalInterface | 7.1.5.2 |
| OperationalRole | class | OperationalAgent | 7.1.5.2 |
| OperationalRole | type | OperationalAgent | 7.1.5.2 |
| ProblemDomain | class | OperationalArchitecture | 7.1.5.2 |
| ProblemDomain | type | OperationalPerformer | 7.1.5.2 |
| OperationalInterface | ownedOperation | OperationalMethod | 7.1.5.3 |
| OperationalSignalProperty | class | OperationalSignal | 7.1.5.3 |
| OperationalSignalProperty | type | OperationalExchangeItem | 7.1.5.3 |
| OperationalActivity | ownedParameter | OperationalParameter | 7.1.5.4 |
| OperationalActivityAction | activity | OperationalActivity | 7.1.5.4 |
| OperationalActivityAction | behavior | OperationalActivity | 7.1.5.4 |
| OperationalStateDescription | owner | OperationalAgent | 7.1.5.5 |
| OperationalMessage | receiveEvent.event.operation | OperationalMethod | 7.1.5.6 |
| InformationElement | owner | DataModel | 7.1.5.7 |
| ServiceMethod | method | ServiceFunction | 7.1.6.2 |
| ServiceMethod | ownedParameter | ServiceParameter | 7.1.6.2 |
| ServiceMethod | owner | ServiceSpecification | 7.1.6.2 |
| ServiceParameter | type | OperationalExchangeItem | 7.1.6.2 |
| ServicePort | class | ServiceSpecification | 7.1.6.2 |
| ServicePort | type | ServiceInterface | 7.1.6.2 |
| ServiceSpecificationRole | class | ServiceSpecification | 7.1.6.2 |
| ServiceSpecificationRole | type | ServiceSpecification | 7.1.6.2 |
| ServiceInterface | ownedOperation | ServiceMethod | 7.1.6.3 |
| ServiceFunction | ownedParameter | ServiceParameter | 7.1.6.4 |
| ServiceFunctionAction | activity | ServiceFunction | 7.1.6.4 |
| ServiceFunctionAction | behavior | ServiceFunction | 7.1.6.4 |
| ServiceStateDescription | owner | ServiceSpecification | 7.1.6.5 |
| ServiceMessage | receiveEvent.event.operation | ServiceMethod | 7.1.6.6 |
| ResourcePerformer | ownedOperation | ResourceMethod | 7.1.8.1 |
| ResourcePerformer | ownedPort | ResourcePort | 7.1.8.1 |
| ResourceMethod | method | Function | 7.1.8.2 |
| ResourceMethod | ownedParameter | ResourceParameter | 7.1.8.2 |
| ResourcePort | type | ResourceInterface | 7.1.8.2 |
| ResourcePort | class | ResourcePerformer | 7.1.8.2 |
| ResourceRole | type | ResourcePerformer | 7.1.8.2 |
| ResourceRole | class | ResourcePerformer | 7.1.8.2 |
| ResourceInterface | ownedOperation | ResourceMethod | 7.1.8.3 |
| ResourceSignalProperty | class | ResourceSignal | 7.1.8.3 |
| ResourceSignalProperty | type | ResourceExchangeItem | 7.1.8.3 |
| Function | ownedParameter | ResourceParameter | 7.1.8.4 |
| FunctionAction | activity | Function | 7.1.8.4 |
| FunctionAction | behavior | Function | 7.1.8.4 |
| ResourceStateDescription | owner | ResourcePerformer | 7.1.8.5 |
| ResourceMessage | receiveEvent.event.operation | ResourceMethod | 7.1.8.6 |
| DataElement | owner | DataModel | 7.1.8.7 |
| VersionOfConfiguration | class | WholeLifeConfiguration | 7.1.8.9 |
| VersionOfConfiguration | type | VersionedElement | 7.1.8.9 |
| SecurityProperty | class | Asset | 7.1.9.2 |
| ProjectMilestoneRole | class | Project | 7.1.10.2 |
| ProjectMilestoneRole | type | ProjectMilestone | 7.1.10.2 |
| ProjectRole | class | Project | 7.1.10.2 |
| ProjectRole | type | Project | 7.1.10.2 |
| ProjectStatus | definingFeature | ProjectTheme | 7.1.10.2 |
| ProjectTheme | class | ProjectMilestone | 7.1.10.2 |
| ProjectTheme | type | StatusIndicators | 7.1.10.2 |
| ProjectActivityAction | behavior | ProjectActivity | 7.1.10.4 |
| ProjectActivityAction | activity | ProjectActivity | 7.1.10.4 |
| ActualProject | classifier | Project | 7.1.10.5 |
| ActualProject | slot | ActualProjectRole or ActualProjectMilestoneRole | 7.1.10.5 |
| ActualProjectMilestone | classifier | ProjectMilestone | 7.1.10.5 |
| ActualProjectMilestoneRole | definingFeature | ProjectMilestoneRole | 7.1.10.5 |
| ActualProjectMilestoneRole | owningInstance | ActualProject | 7.1.10.5 |
| ActualProjectMilestoneRole | value.instance | ActualProjectMilestone | 7.1.10.5 |
| ActualProjectRole | definingFeature | ProjectRole | 7.1.10.5 |
| ActualProjectRole | owningInstance | ActualProject | 7.1.10.5 |
| ActualProjectRole | value.instance | ActualProject | 7.1.10.5 |
| ProtocolLayer | class | Protocol | 7.1.11.2 |
| ProtocolLayer | type | Protocol | 7.1.11.2 |
| ActualOrganization | classifier | Organization | 7.1.12.1 |
| ActualOrganization | slot | ActualOrganizationRole | 7.1.12.1 |
| ActualPerson | classifier | Person | 7.1.12.1 |
| ActualPost | classifier | Post | 7.1.12.1 |
| ActualResource | classifier | ResourcePerformer | 7.1.12.1 |
| ActualResponsibility | classifier | Responsibility | 7.1.12.1 |
| FieldedCapability | classifier | CapabilityConfiguration | 7.1.12.1 |
| ActualOrganizationRole | owningInstance | ActualOrganization | 7.1.12.2 |
| ActualResourceRole | definingFeature | ResourceRole | 7.1.12.2 |
| ActualResourceRole | owningInstance | ActualResource | 7.1.12.2 |
| ActualResourceRelationship | realizes | ResourceExchange | 7.1.12.3 |
| ActualService | classifier | ServiceSpecification | 7.1.12.4 |

### 7.2 Annotation, constraint and exchange ends

| Element | Property | Must be | Clause |
|---|---|---|---|
| Alias | annotatedElement | UAFElement | 7.1.1 |
| Definition | annotatedElement | UAFElement | 7.1.1 |
| SameAs | client | UAFElement | 7.1.1 |
| SameAs | supplier | UAFElement | 7.1.1 |
| ArchitectureMetadata | annotatedElement | ArchitecturalDescription | 7.1.3.4 |
| Information | annotatedElement | ConceptItem | 7.1.3.4 |
| Metadata | annotatedElement | UAFElement | 7.1.3.4 |
| ArchitecturalReference | client | ArchitecturalDescription | 7.1.3.6 |
| ArchitecturalReference | supplier | ArchitecturalDescription | 7.1.3.6 |
| VisionStatement | annotatedElement | EnterpriseVision | 7.1.4.1 |
| CapabilityForTask | client | Capability | 7.1.4.3 |
| CapabilityForTask | supplier | ActualEnduringTask | 7.1.4.3 |
| AchievedEffect | client | Achiever | 7.1.4.4 |
| AchievedEffect | supplier | ActualState | 7.1.4.4 |
| DesiredEffect | client | Desirer | 7.1.4.4 |
| DesiredEffect | supplier | ActualState | 7.1.4.4 |
| Exhibits | client | CapableElement | 7.1.4.5 |
| Exhibits | supplier | Capability | 7.1.4.5 |
| MapsToCapability | client | Activity | 7.1.4.5 |
| MapsToCapability | supplier | Capability | 7.1.4.5 |
| OrganizationInEnterprise | client | ActualOrganization | 7.1.4.5 |
| OrganizationInEnterprise | supplier | ActualEnterprisePhase | 7.1.4.5 |
| ArbitraryConnector | client | ConceptRole | 7.1.5.1 |
| ArbitraryConnector | supplier | ConceptRole | 7.1.5.1 |
| OperationalExchange | informationSource | OperationalPerformer | 7.1.5.3 |
| OperationalExchange | informationTarget | OperationalPerformer | 7.1.5.3 |
| OperationalExchange | realizingActivityEdge | OperationalActivityEdge | 7.1.5.3 |
| OperationalExchange | realizingConnector | OperationalConnector | 7.1.5.3 |
| OperationalExchange | realizingMessage | OperationalMessage | 7.1.5.3 |
| OperationalControlFlow | source | OperationalActivityAction | 7.1.5.4 |
| OperationalControlFlow | target | OperationalActivityAction | 7.1.5.4 |
| OperationalConstraint | constrainedElement | SubjectOfOperationalConstraint | 7.1.5.8 |
| ServicePolicy | constrainedElement | ServiceSpecification | 7.1.6.7 |
| Consumes | client | OperationalActivity | 7.1.6.8 |
| Consumes | supplier | ServiceSpecification | 7.1.6.8 |
| Command | conveyed | DataElement | 7.1.7.2 |
| Command | informationSource | OrganizationalResource | 7.1.7.2 |
| Command | informationTarget | OrganizationalResource | 7.1.7.2 |
| Control | conveyed | DataElement | 7.1.7.2 |
| Control | informationSource | PhysicalResource | 7.1.7.2 |
| Control | informationTarget | PhysicalResource | 7.1.7.2 |
| CompetenceToConduct | client | Function | 7.1.7.3 |
| CompetenceToConduct | supplier | Competence | 7.1.7.3 |
| CompetenceForRole | client | ResourceRole | 7.1.7.4 |
| CompetenceForRole | supplier | Competence | 7.1.7.4 |
| RequiresCompetence | client | OrganizationalResource | 7.1.7.4 |
| RequiresCompetence | supplier | Competence | 7.1.7.4 |
| ResponsibleFor | client | ActualResponsibleResource | 7.1.7.5 |
| ResponsibleFor | supplier | ActualProject or ActualResponsibility | 7.1.7.5 |
| ResourceExchange | informationSource | ResourcePerformer | 7.1.8.3 |
| ResourceExchange | informationTarget | ResourcePerformer | 7.1.8.3 |
| ResourceExchange | realizingActivityEdge | FunctionEdge | 7.1.8.3 |
| ResourceExchange | realizingConnector | ResourceConnector | 7.1.8.3 |
| ResourceExchange | realizingMessage | ResourceMessage | 7.1.8.3 |
| FunctionControlFlow | source | FunctionAction | 7.1.8.4 |
| FunctionControlFlow | target | FunctionAction | 7.1.8.4 |
| ResourceConstraint | constrainedElement | SubjectOfResourceConstraint | 7.1.8.8 |
| Forecast | client | SubjectOfForecast | 7.1.8.9 |
| Forecast | supplier | SubjectOfForecast | 7.1.8.9 |
| VersionSuccession | client | VersionOfConfiguration | 7.1.8.9 |
| VersionSuccession | supplier | VersionOfConfiguration | 7.1.8.9 |
| Enhances | client | EnhancedSecurityControl | 7.1.9.3 |
| Enhances | supplier | SecurityControl | 7.1.9.3 |
| Protects | client | SecurityControl | 7.1.9.3 |
| Protects | supplier | Asset | 7.1.9.3 |
| ProtectsInContext | supplier | OperationalRole or ResourceRole or OperationalConnector or ResourceConnector or SecurityProperty | 7.1.9.3 |
| SecurityConstraint | constrainedElement | SubjectOfSecurityConstraint | 7.1.9.4 |
| SecurityControlFamily | annotatedElement | SecurityControl | 7.1.9.4 |
| Affects | client | Risk | 7.1.9.5 |
| Affects | supplier | Asset | 7.1.9.5 |
| AffectsInContext | client | Risk | 7.1.9.5 |
| AffectsInContext | supplier | AssetRole | 7.1.9.5 |
| Mitigates | client | SecurityControl | 7.1.9.5 |
| Mitigates | supplier | Risk | 7.1.9.5 |
| OwnsRisk | client | OrganizationalResource | 7.1.9.5 |
| OwnsRisk | supplier | Risk | 7.1.9.5 |
| OwnsRiskInContext | client | ResourceRole | 7.1.9.5 |
| OwnsRiskInContext | supplier | Risk | 7.1.9.5 |
| MilestoneDependency | client | ActualProjectMilestone | 7.1.10.3 |
| MilestoneDependency | supplier | ActualProjectMilestone | 7.1.10.3 |
| ProjectSequence | client | ActualProject | 7.1.10.3 |
| ProjectSequence | supplier | ActualProject | 7.1.10.3 |
| ActualResourceRelationship | informationSource | ActualResource | 7.1.12.3 |
| ActualResourceRelationship | informationTarget | ActualResource | 7.1.12.3 |
| FillsPost | client | ActualPerson | 7.1.12.3 |
| FillsPost | supplier | ActualPost | 7.1.12.3 |
| ProvidesCompetence | client | ActualOrganizationalResource | 7.1.12.4 |
| ProvidesCompetence | supplier | Competence | 7.1.12.4 |
| OwnsProcess | client | ActualOrganizationalResource | 7.1.12.5 |
| OwnsProcess | supplier | OperationalActivity | 7.1.12.5 |

## 8. Constraints (profile clause 7.1, clause 2)

The standard states 219 formal constraints on 126 elements. Together with conformance requirements and the grid and view notes there are 256 rules in this library: 242 must, 1 should, 13 note. They are listed with ids in `rules.md` and in `language.yaml`. Categories: CONF (4); GEN (6); END (92); TYP (76); OWN (38); XCH (10); VAL (3); CARD (17); VIEW (6); GUID (4).

## 9. Class library (Annex B)

A library of measurement and marking classes: BillingItem, ClassificationAttributes (intelligence-community security markings), CommunicationsLinkProperties, DataElementProperties, Duration, ExchangeProperties, InformationElementProperties, OperationalActivityProperties, Periodicity, PricingType, SecurityControlAssessmentProperties, SecurityControlProperties, and SecurityImpactProperties. Their attributes are not catalogued in this library.

## 10. Where the profile and the domain metamodel differ

- **40 elements exist only in the profile:** ActualMeasurementKind, ActualMilestoneKind, ActualOrganizationRole, ActualProjectRole, ActualResourceRole, AffectsInContext, ArbitraryConnector, ConceptRole, DataModelKind, EnvironmentKind, FillsPost, FunctionControlFlow, FunctionObjectFlow, GeoPoliticalExtentTypeKind, InformationKind, LocationKind, LocationTypeKind, OperationalControlFlow, OperationalExchangeKind, OperationalObjectFlow, OperationalSignal, OperationalSignalProperty, OwnsProcess, OwnsRiskInContext, ProjectActivity, ProjectActivityAction, ProjectKind, ProjectRole, ResourceInteractionKind, ResourceSignal, ResourceSignalProperty, ResponsibleRoleKind, RoleKind, RuleKind, SecurityProcess, SecurityProcessAction, ServiceSpecificationRole, StructuralPart, TemporalPart, WholeLifeConfigurationKind.
- **9 elements exist only in the metamodel:** ActivityPerformableUnderCondition, SecurityControlAction, Caveat, SecurityAvailability, SecurityCategory, SecurityClassification, SecurityClassificationKind, SecurityIntegrity, SecurityMeasurement.
- **Generalization differences that change meaning:** the profile makes ActualEnterprisePhase an Achiever; KnownResource also a ResourcePerformer; ServiceSpecification also a CapableElement; OperationalRole and ResourceRole subjects of security constraints. The metamodel makes OperationalExchangeItem, ResourceExchangeItem and DataElement subjects of security constraints (the profile does not), Asset a subject of forecast, ActualResource a location holder, and Project a Desirer; the profile makes Project an OrganizationalResource and ActualProject an ActualOrganizationalResource and Achiever. FunctionEdge is abstract in the profile and not in the metamodel; ActualService is abstract in the metamodel and not in the profile.
- **Security control:** in the metamodel SecurityControl is an activity (an operational activity and a function) with SecurityControlAction as its call. In the profile SecurityControl is a requirement-like class and SecurityProcess and SecurityProcessAction are the activity and its call; two profile constraints still use the metamodel names.
- **Additions by the profile that only add a SysML base:** 45 elements also specialize a SysML element (Block, Requirement, Allocate, ItemFlow, DeriveReqt, InterfaceBlock, ProxyPort, ValueType, View or Viewpoint); these add SysML behavior and do not change the UAF meaning.

## 11. What the standard does not say

- No multiplicity for relationships, and no rule for object flows or the three message elements beyond what their SysML base implies.
- No rule on what makes a view complete, how many views an architecture needs, or which views are mandatory.
- No conformance of models, instances or diagrams; no check that an exchange kind is set.
- No colors or shapes beyond the SysML notation of the extended metaclass; the colors in the metamodel's figures are a legend for reading the specification only.
- The relationships' ends in the metamodel are in figures; this library takes them from the profile's constraints.