# UAF 1.0 rules

Generated from `language.yaml` (`constraints`). Do not edit by hand; change the language file and regenerate.

Each rule has a stable id of the form `UAF-<CAT>-nnn`. The number never changes once assigned. A rule that is retired keeps its id and is marked withdrawn rather than reused.

## Strength

| Strength | Meaning |
|---|---|
| must | The standard states it with 'must' or 'has to be', or gives a property a multiplicity of exactly one. A model that breaks it is not well formed. |
| should | The standard gives it as a recommendation or as guidance on what a view shows. Breaking it is a warning, not an error. |
| note | The standard states it as an expectation, an option or a method note. It is recorded for completeness and is not checkable on its own. |

Where a rule says 'a Capability', it means a Capability or any element that specializes it. The standard's constraint text varies on this point (some entries add 'or its specializations', some do not); the rules read all of them the same way.

## Categories

| Category | Name | Covers | Rules |
|---|---|---|---|
| CONF | Conformance | What a tool must support to claim conformance to the profile. | 4 |
| GEN | General structure | Rules that hold for every element: abstract elements, dates, the common root. | 6 |
| END | Relationship ends | Which kinds of element a relationship, annotation or constraint may attach to at each end. | 92 |
| TYP | Typing | Which kind a role, port, instance or slot must be typed or classified by, and what owns it. | 76 |
| OWN | Ownership and behavior wiring | Which owner, operations, ports, parameters and called behaviors each element may have. | 38 |
| XCH | Exchanges | What an exchange may convey for each exchange kind, and what may realize an exchange. | 10 |
| VAL | Value rules | Rules on the values of several properties taken together (dates, status types, paired ends). | 3 |
| CARD | Cardinality | Properties that must have a value (multiplicity of exactly one). | 17 |
| VIEW | Views and the grid | What a view may show and how views are framed. | 6 |
| GUID | Guidance | Method notes and expectations that are not checkable on their own. | 4 |

Total: 256 rules (242 must, 1 should, 13 note).

Section references: a plain number (7.1.5.3) is a clause of the UAFP specification (formal/17-12-01); 'DMM' means the domain metamodel (formal/17-12-02); a bare '2' is the conformance clause. Properties named in the rules (client, supplier, class, type, classifier, and so on) are the UML properties the standard constrains: client and supplier are the ends of a dependency or abstraction; informationSource and informationTarget the ends of a flow; class the element that owns a part; type what the part is typed by; classifier what an instance is an instance of.

## CONF: Conformance

| Id | Strength | Rule | Section |
|---|---|---|---|
| UAF-CONF-001 | must | A tool conforms to the UAF profile at its single compliance level, which is a profile of SysML 1.4 that imports the SysML profile and defines constraints pairing the use of SysML elements with UAF elements. | 2 |
| UAF-CONF-002 | must | Every element, attribute, constraint, association and package structure the profile defines exists in the implementation and complies with the specification. | 2 |
| UAF-CONF-003 | must | The implementation supports XMI import and export of both the user model and the profile. | 2 |
| UAF-CONF-004 | must | The implementation imports and exports UAF profile models with no loss and no transformation (full fidelity). | 2 |

## GEN: General structure

| Id | Strength | Rule | Section |
|---|---|---|---|
| UAF-GEN-001 | must | An abstract element is never used directly; only its concrete specializations are used. Thirty-three elements are abstract. | 7.1 (isAbstract entries); DMM 1.4 (legend) |
| UAF-GEN-002 | must | The start and end dates of an actual element are written as ISO 8601 date-times with a time zone designator (YYYY-MM-DDThh:mm:ssTZD). | 7.1.3.1 (ISO8601DateTime, ActualState) |
| UAF-GEN-003 | note | Every UAF element specializes UAFElement and so may carry a URI and a link to the standards it conforms to. | 7.1.13 (UAFElement) |
| UAF-GEN-004 | note | Every measurable element can be measured by applying MeasurementSets, and actual values are recorded by ActualMeasurementSets. | 7.1.2 (MeasurableElement) |
| UAF-GEN-005 | note | The Metadata Taxonomy cell is a placeholder for extending the profile to other domains and has no diagram type of its own. | DMM 1.1 (note f) |
| UAF-GEN-006 | note | Every profile element can be traced to a domain metamodel element; the profile is derived from the metamodel by mapping its concepts and relationships. | 6.3 |

## END: Relationship ends

| Id | Strength | Rule | Section |
|---|---|---|---|
| UAF-END-001 | must | An Alias may annotate only a UAFElement (or a specialization of it). | 7.1.1 |
| UAF-END-002 | must | A Definition may annotate only a UAFElement (or a specialization of it). | 7.1.1 |
| UAF-END-003 | must | The client of a SameAs must be a UAFElement (or a specialization of it). | 7.1.1 |
| UAF-END-004 | must | The supplier of a SameAs must be a UAFElement (or a specialization of it). | 7.1.1 |
| UAF-END-005 | must | When the supplier is an OperationalActivity, the client must be an OperationalAgent; when the supplier is a ServiceFunction, the client must be a ServiceSpecification; when the supplier is a Function other than a ProjectActivity, the client must be a ResourcePerformer; when the supplier is a ProjectActivity, the client must be a Project. | 7.1.3.3 |
| UAF-END-006 | must | When the client is an OperationalAgent, the supplier must be an OperationalActivity; when the client is a ServiceSpecification, the supplier must be a ServiceFunction; when the client is a ResourcePerformer, the supplier must be a Function other than a ProjectActivity; when the client is a Project, the supplier must be a ProjectActivity. | 7.1.3.3 |
| UAF-END-007 | must | When the supplier is an OperationalActivityAction, the client must be an OperationalRole; when the supplier is a ServiceFunctionAction, the client must be a ServiceSpecificationRole; when the supplier is a FunctionAction other than a ProjectActivityAction, the client must be a ResourceRole; when the supplier is a ProjectActivityAction, the client must be a ProjectRole. | 7.1.3.3 |
| UAF-END-008 | must | When the client is an OperationalRole, the supplier must be an OperationalActivityAction; when the client is a ServiceSpecificationRole, the supplier must be a ServiceFunctionAction; when the client is a ResourceRole, the supplier must be a FunctionAction other than a ProjectActivityAction. (The standard states no supplier rule for a ProjectRole client.) | 7.1.3.3 |
| UAF-END-009 | must | An ArchitectureMetadata may annotate only an ArchitecturalDescription (or a specialization of it). | 7.1.3.4 |
| UAF-END-010 | must | An Information may annotate only a ConceptItem (or a specialization of it). | 7.1.3.4 |
| UAF-END-011 | must | A Metadata may annotate only a UAFElement (or a specialization of it). | 7.1.3.4 |
| UAF-END-012 | must | The client of an ArchitecturalReference must be an ArchitecturalDescription (or a specialization of it). | 7.1.3.6 |
| UAF-END-013 | must | The supplier of an ArchitecturalReference must be an ArchitecturalDescription (or a specialization of it). | 7.1.3.6 |
| UAF-END-014 | must | When the supplier is an OperationalAgent, the client must be a ResourcePerformer; an OperationalActivity or a ServiceFunction, a Function; a ServiceInterface or an OperationalInterface, a ResourceInterface; an OperationalConnector or a ResourceConnector, a ResourceConnector; an OperationalExchange, a ResourceExchange; an OperationalRole, a ResourceRole; an ActualEnduringTask, an OperationalActivity; an InformationElement, a DataElement. | 7.1.3.6 |
| UAF-END-015 | must | When the client is a ResourcePerformer, the supplier must be an OperationalAgent; a Function, an OperationalActivity or a ServiceFunction; a ResourceInterface, a ServiceInterface or an OperationalInterface; a ResourceConnector, an OperationalConnector or a ResourceConnector; a ResourceExchange, an OperationalExchange; a ResourceRole, an OperationalRole; an OperationalActivity, an ActualEnduringTask; a DataElement, an InformationElement. | 7.1.3.6 |
| UAF-END-016 | must | A VisionStatement may annotate only an EnterpriseVision (or a specialization of it). | 7.1.4.1 |
| UAF-END-017 | must | The client of a CapabilityForTask must be a Capability (or a specialization of it). | 7.1.4.3 |
| UAF-END-018 | must | The supplier of a CapabilityForTask must be an ActualEnduringTask (or a specialization of it). | 7.1.4.3 |
| UAF-END-019 | must | The client of an AchievedEffect must be an Achiever (or a specialization of it). | 7.1.4.4 |
| UAF-END-020 | must | The supplier of an AchievedEffect must be an ActualState (or a specialization of it). | 7.1.4.4 |
| UAF-END-021 | must | The client of a DesiredEffect must be a Desirer (or a specialization of it). | 7.1.4.4 |
| UAF-END-022 | must | The supplier of a DesiredEffect must be an ActualState (or a specialization of it). | 7.1.4.4 |
| UAF-END-023 | must | The client of an Exhibits must be a CapableElement (or a specialization of it). | 7.1.4.5 |
| UAF-END-024 | must | The supplier of an Exhibits must be a Capability (or a specialization of it). | 7.1.4.5 |
| UAF-END-025 | must | The client of a MapsToCapability must be an Activity (or a specialization of it). | 7.1.4.5 |
| UAF-END-026 | must | The supplier of a MapsToCapability must be a Capability (or a specialization of it). | 7.1.4.5 |
| UAF-END-027 | must | The client of an OrganizationInEnterprise must be an ActualOrganization (or a specialization of it). | 7.1.4.5 |
| UAF-END-028 | must | The supplier of an OrganizationInEnterprise must be an ActualEnterprisePhase (or a specialization of it). | 7.1.4.5 |
| UAF-END-029 | must | The client of an ArbitraryConnector must be a ConceptRole (or a specialization of it). | 7.1.5.1 |
| UAF-END-030 | must | The supplier of an ArbitraryConnector must be a ConceptRole (or a specialization of it). | 7.1.5.1 |
| UAF-END-031 | must | Each end of an OperationalConnector must attach to an OperationalRole or an OperationalPort (or a specialization of either). | 7.1.5.3 |
| UAF-END-032 | must | The information source of an OperationalExchange must be an OperationalPerformer (or a specialization of it). | 7.1.5.3 |
| UAF-END-033 | must | The information target of an OperationalExchange must be an OperationalPerformer (or a specialization of it). | 7.1.5.3 |
| UAF-END-034 | must | The source of an OperationalControlFlow must be an OperationalActivityAction (or a specialization of it). | 7.1.5.4 |
| UAF-END-035 | must | The target of an OperationalControlFlow must be an OperationalActivityAction (or a specialization of it). | 7.1.5.4 |
| UAF-END-036 | must | An OperationalConstraint may constrain only a SubjectOfOperationalConstraint (or a specialization of it). | 7.1.5.8 |
| UAF-END-037 | must | Each end of a ServiceConnector must attach to a ServicePort or a ServiceSpecificationRole (or a specialization of either). | 7.1.6.3 |
| UAF-END-038 | must | A ServicePolicy may constrain only a ServiceSpecification (or a specialization of it). | 7.1.6.7 |
| UAF-END-039 | must | The client of a Consumes must be an OperationalActivity (or a specialization of it). | 7.1.6.8 |
| UAF-END-040 | must | The supplier of a Consumes must be a ServiceSpecification (or a specialization of it). | 7.1.6.8 |
| UAF-END-041 | must | The information source of a Command must be an OrganizationalResource (or a specialization of it). | 7.1.7.2 |
| UAF-END-042 | must | The information target of a Command must be an OrganizationalResource (or a specialization of it). | 7.1.7.2 |
| UAF-END-043 | must | The information source of a Control must be a PhysicalResource (or a specialization of it). | 7.1.7.2 |
| UAF-END-044 | must | The information target of a Control must be a PhysicalResource (or a specialization of it). | 7.1.7.2 |
| UAF-END-045 | must | The client of a CompetenceToConduct must be a Function (or a specialization of it). | 7.1.7.3 |
| UAF-END-046 | must | The supplier of a CompetenceToConduct must be a Competence (or a specialization of it). | 7.1.7.3 |
| UAF-END-047 | must | The client of a CompetenceForRole must be a ResourceRole (or a specialization of it). | 7.1.7.4 |
| UAF-END-048 | must | The supplier of a CompetenceForRole must be a Competence (or a specialization of it). | 7.1.7.4 |
| UAF-END-049 | must | The client of a RequiresCompetence must be an OrganizationalResource (or a specialization of it). | 7.1.7.4 |
| UAF-END-050 | must | The supplier of a RequiresCompetence must be a Competence (or a specialization of it). | 7.1.7.4 |
| UAF-END-051 | must | The client of a ResponsibleFor must be an ActualResponsibleResource (or a specialization of it). | 7.1.7.5 |
| UAF-END-052 | must | The supplier of a ResponsibleFor must be an ActualProject or an ActualResponsibility (or a specialization of it). | 7.1.7.5 |
| UAF-END-053 | must | Each end of a ResourceConnector must attach to a ResourcePort or a ResourceRole (or a specialization of either). | 7.1.8.3 |
| UAF-END-054 | must | The information source of a ResourceExchange must be a ResourcePerformer (or a specialization of it). | 7.1.8.3 |
| UAF-END-055 | must | The information target of a ResourceExchange must be a ResourcePerformer (or a specialization of it). | 7.1.8.3 |
| UAF-END-056 | must | The source of a FunctionControlFlow must be a FunctionAction (or a specialization of it). | 7.1.8.4 |
| UAF-END-057 | must | The target of a FunctionControlFlow must be a FunctionAction (or a specialization of it). | 7.1.8.4 |
| UAF-END-058 | must | A ResourceConstraint may constrain only a SubjectOfResourceConstraint (or a specialization of it). | 7.1.8.8 |
| UAF-END-059 | must | The client of a Forecast must be a SubjectOfForecast (or a specialization of it). | 7.1.8.9 |
| UAF-END-060 | must | The supplier of a Forecast must be a SubjectOfForecast (or a specialization of it). | 7.1.8.9 |
| UAF-END-061 | must | The client of a VersionSuccession must be a VersionOfConfiguration (or a specialization of it). | 7.1.8.9 |
| UAF-END-062 | must | The supplier of a VersionSuccession must be a VersionOfConfiguration (or a specialization of it). | 7.1.8.9 |
| UAF-END-063 | must | The client of an Enhances must be an EnhancedSecurityControl (or a specialization of it). | 7.1.9.3 |
| UAF-END-064 | must | The supplier of an Enhances must be a SecurityControl (or a specialization of it). | 7.1.9.3 |
| UAF-END-065 | must | The client of a Protects must be a SecurityControl (or a specialization of it). | 7.1.9.3 |
| UAF-END-066 | must | The supplier of a Protects must be an Asset (or a specialization of it). | 7.1.9.3 |
| UAF-END-067 | must | The client of a ProtectsInContext must be a SecurityControlAction. (The profile defines no element of that name.) | 7.1.9.3 |
| UAF-END-068 | must | The supplier of a ProtectsInContext must be an OperationalRole, a ResourceRole, an OperationalConnector, a ResourceConnector or a SecurityProperty (or a specialization of it). | 7.1.9.3 |
| UAF-END-069 | must | A SecurityConstraint may constrain only a SubjectOfSecurityConstraint (or a specialization of it). | 7.1.9.4 |
| UAF-END-070 | must | A SecurityControlFamily may annotate only a SecurityControl (or a specialization of it). | 7.1.9.4 |
| UAF-END-071 | must | The client of an Affects must be a Risk (or a specialization of it). | 7.1.9.5 |
| UAF-END-072 | must | The supplier of an Affects must be an Asset (or a specialization of it). | 7.1.9.5 |
| UAF-END-073 | must | The client of an AffectsInContext must be a Risk (or a specialization of it). | 7.1.9.5 |
| UAF-END-074 | must | The supplier of an AffectsInContext must be an AssetRole (or a specialization of it). | 7.1.9.5 |
| UAF-END-075 | must | The client of a Mitigates must be a SecurityControl (or a specialization of it). | 7.1.9.5 |
| UAF-END-076 | must | The supplier of a Mitigates must be a Risk (or a specialization of it). | 7.1.9.5 |
| UAF-END-077 | must | The client of an OwnsRisk must be an OrganizationalResource (or a specialization of it). | 7.1.9.5 |
| UAF-END-078 | must | The supplier of an OwnsRisk must be a Risk (or a specialization of it). | 7.1.9.5 |
| UAF-END-079 | must | The client of an OwnsRiskInContext must be a ResourceRole (or a specialization of it). | 7.1.9.5 |
| UAF-END-080 | must | The supplier of an OwnsRiskInContext must be a Risk (or a specialization of it). | 7.1.9.5 |
| UAF-END-081 | must | The client of a MilestoneDependency must be an ActualProjectMilestone (or a specialization of it). | 7.1.10.3 |
| UAF-END-082 | must | The supplier of a MilestoneDependency must be an ActualProjectMilestone (or a specialization of it). | 7.1.10.3 |
| UAF-END-083 | must | The client of a ProjectSequence must be an ActualProject (or a specialization of it). | 7.1.10.3 |
| UAF-END-084 | must | The supplier of a ProjectSequence must be an ActualProject (or a specialization of it). | 7.1.10.3 |
| UAF-END-085 | must | The information source of an ActualResourceRelationship must be an ActualResource (or a specialization of it). | 7.1.12.3 |
| UAF-END-086 | must | The information target of an ActualResourceRelationship must be an ActualResource (or a specialization of it). | 7.1.12.3 |
| UAF-END-087 | must | The client of a FillsPost must be an ActualPerson (or a specialization of it). | 7.1.12.3 |
| UAF-END-088 | must | The supplier of a FillsPost must be an ActualPost (or a specialization of it). | 7.1.12.3 |
| UAF-END-089 | must | The client of a ProvidesCompetence must be an ActualOrganizationalResource (or a specialization of it). | 7.1.12.4 |
| UAF-END-090 | must | The supplier of a ProvidesCompetence must be a Competence (or a specialization of it). | 7.1.12.4 |
| UAF-END-091 | must | The client of an OwnsProcess must be an ActualOrganizationalResource (or a specialization of it). | 7.1.12.5 |
| UAF-END-092 | must | The supplier of an OwnsProcess must be an OperationalActivity (or a specialization of it). | 7.1.12.5 |

## TYP: Typing

| Id | Strength | Rule | Section |
|---|---|---|---|
| UAF-TYP-001 | must | The classifier of an ActualCondition must be a Condition (or a specialization of it). | 7.1.2 |
| UAF-TYP-002 | must | The classifier of an ActualEnvironment must be an Environment (or a specialization of it). | 7.1.2 |
| UAF-TYP-003 | must | The classifier of an ActualLocation must be a Location (or a specialization of it). | 7.1.2 |
| UAF-TYP-004 | must | The defining feature of an ActualMeasurement must be a Measurement (or a specialization of it). | 7.1.2 |
| UAF-TYP-005 | must | The instance that owns an ActualMeasurement must be an ActualPropertySet (or a specialization of it). | 7.1.2 |
| UAF-TYP-006 | must | The classifier of an ActualMeasurementSet must be a MeasurementSet (or a specialization of it). | 7.1.2 |
| UAF-TYP-007 | must | The slots of an ActualMeasurementSet must be an ActualMeasurement (or a specialization of it). | 7.1.2 |
| UAF-TYP-008 | must | The classifier of an ActualPropertySet must be a PropertySet (or a specialization of it). | 7.1.2 |
| UAF-TYP-009 | must | The class that owns an EnvironmentProperty must be an Environment (or a specialization of it). | 7.1.2 |
| UAF-TYP-010 | must | The type of an EnvironmentProperty must be a Condition (or a specialization of it). | 7.1.2 |
| UAF-TYP-011 | must | The class that owns a Measurement must be a PropertySet (or a specialization of it). | 7.1.2 |
| UAF-TYP-012 | must | The classifier of an ActualEnterprisePhase must be an EnterprisePhase (or a specialization of it). | 7.1.4.1 |
| UAF-TYP-013 | must | The class that owns a CapabilityProperty must be a Capability (or a specialization of it). | 7.1.4.2 |
| UAF-TYP-014 | must | The type of a CapabilityProperty must be a Capability (or a specialization of it). | 7.1.4.2 |
| UAF-TYP-015 | must | The class that owns a StructuralPart must be an EnterprisePhase (or a specialization of it). | 7.1.4.2 |
| UAF-TYP-016 | must | The type of a StructuralPart must be an EnterprisePhase (or a specialization of it). | 7.1.4.2 |
| UAF-TYP-017 | must | The class that owns a TemporalPart must be an EnterprisePhase (or a specialization of it). | 7.1.4.2 |
| UAF-TYP-018 | must | The type of a TemporalPart must be an EnterprisePhase (or a specialization of it). | 7.1.4.2 |
| UAF-TYP-019 | must | The classifier of an ActualEnduringTask must be an EnduringTask (or a specialization of it). | 7.1.4.3 |
| UAF-TYP-020 | must | The class that owns a ConceptRole must be a HighLevelOperationalConcept (or a specialization of it). | 7.1.5.1 |
| UAF-TYP-021 | must | The type of a ConceptRole must be a ConceptItem (or a specialization of it). | 7.1.5.1 |
| UAF-TYP-022 | must | The type of an OperationalParameter must be an OperationalExchangeItem (or a specialization of it). | 7.1.5.2 |
| UAF-TYP-023 | must | The class that owns an OperationalPort must be an OperationalPerformer (or a specialization of it). | 7.1.5.2 |
| UAF-TYP-024 | must | The type of an OperationalPort must be an OperationalInterface (or a specialization of it). | 7.1.5.2 |
| UAF-TYP-025 | must | The class that owns an OperationalRole must be an OperationalAgent (or a specialization of it). | 7.1.5.2 |
| UAF-TYP-026 | must | The type of an OperationalRole must be an OperationalAgent (or a specialization of it). | 7.1.5.2 |
| UAF-TYP-027 | must | The class that owns a ProblemDomain must be an OperationalArchitecture (or a specialization of it). | 7.1.5.2 |
| UAF-TYP-028 | must | The type of a ProblemDomain must be an OperationalPerformer (or a specialization of it). | 7.1.5.2 |
| UAF-TYP-029 | must | The class that owns an OperationalSignalProperty must be an OperationalSignal (or a specialization of it). | 7.1.5.3 |
| UAF-TYP-030 | must | The type of an OperationalSignalProperty must be an OperationalExchangeItem (or a specialization of it). | 7.1.5.3 |
| UAF-TYP-031 | must | The type of a ServiceParameter must be an OperationalExchangeItem (or a specialization of it). | 7.1.6.2 |
| UAF-TYP-032 | must | The class that owns a ServicePort must be a ServiceSpecification (or a specialization of it). | 7.1.6.2 |
| UAF-TYP-033 | must | The type of a ServicePort must be a ServiceInterface (or a specialization of it). | 7.1.6.2 |
| UAF-TYP-034 | must | The class that owns a ServiceSpecificationRole must be a ServiceSpecification (or a specialization of it). | 7.1.6.2 |
| UAF-TYP-035 | must | The type of a ServiceSpecificationRole must be a ServiceSpecification (or a specialization of it). | 7.1.6.2 |
| UAF-TYP-036 | must | The type of a ResourceParameter must be a ResourceExchangeItem (or a specialization). The standard names this target ResourceInteractionItem, which it does not define. | 7.1.8.2 |
| UAF-TYP-037 | must | The type of a ResourcePort must be a ResourceInterface (or a specialization of it). | 7.1.8.2 |
| UAF-TYP-038 | must | The class that owns a ResourcePort must be a ResourcePerformer (or a specialization of it). | 7.1.8.2 |
| UAF-TYP-039 | must | The type of a ResourceRole must be a ResourcePerformer (or a specialization of it). | 7.1.8.2 |
| UAF-TYP-040 | must | The class that owns a ResourceRole must be a ResourcePerformer (or a specialization of it). | 7.1.8.2 |
| UAF-TYP-041 | must | The class that owns a ResourceSignalProperty must be a ResourceSignal (or a specialization of it). | 7.1.8.3 |
| UAF-TYP-042 | must | The type of a ResourceSignalProperty must be a ResourceExchangeItem (or a specialization of it). | 7.1.8.3 |
| UAF-TYP-043 | must | The class that owns a VersionOfConfiguration must be a WholeLifeConfiguration (or a specialization of it). | 7.1.8.9 |
| UAF-TYP-044 | must | The type of a VersionOfConfiguration must be a VersionedElement (or a specialization of it). | 7.1.8.9 |
| UAF-TYP-045 | must | The class that owns a SecurityProperty must be an Asset (or a specialization of it). | 7.1.9.2 |
| UAF-TYP-046 | must | When the class is an OperationalAgent, the type of a SecurityProperty must be an InformationElement; when the class is a ResourcePerformer, a DataElement; when the class is an InformationElement, an InformationElement; when the class is a DataElement, a DataElement (each or a specialization). | 7.1.9.2 |
| UAF-TYP-047 | must | The class that owns a ProjectMilestoneRole must be a Project (or a specialization of it). | 7.1.10.2 |
| UAF-TYP-048 | must | The type of a ProjectMilestoneRole must be a ProjectMilestone (or a specialization of it). | 7.1.10.2 |
| UAF-TYP-049 | must | The class that owns a ProjectRole must be a Project (or a specialization of it). | 7.1.10.2 |
| UAF-TYP-050 | must | The type of a ProjectRole must be a Project (or a specialization of it). | 7.1.10.2 |
| UAF-TYP-051 | must | The defining feature of a ProjectStatus must be a ProjectTheme (or a specialization of it). | 7.1.10.2 |
| UAF-TYP-052 | must | The class that owns a ProjectTheme must be a ProjectMilestone (or a specialization of it). | 7.1.10.2 |
| UAF-TYP-053 | must | The type of a ProjectTheme must be a StatusIndicators (or a specialization of it). | 7.1.10.2 |
| UAF-TYP-054 | must | The classifier of an ActualProject must be a Project (or a specialization of it). | 7.1.10.5 |
| UAF-TYP-055 | must | The slots of an ActualProject must be an ActualProjectRole or an ActualProjectMilestoneRole (or a specialization of it). | 7.1.10.5 |
| UAF-TYP-056 | must | The classifier of an ActualProjectMilestone must be a ProjectMilestone (or a specialization of it). | 7.1.10.5 |
| UAF-TYP-057 | must | The defining feature of an ActualProjectMilestoneRole must be a ProjectMilestoneRole (or a specialization of it). | 7.1.10.5 |
| UAF-TYP-058 | must | The instance that owns an ActualProjectMilestoneRole must be an ActualProject (or a specialization of it). | 7.1.10.5 |
| UAF-TYP-059 | must | The instance given as the value of an ActualProjectMilestoneRole must be an ActualProjectMilestone (or a specialization of it). | 7.1.10.5 |
| UAF-TYP-060 | must | The defining feature of an ActualProjectRole must be a ProjectRole (or a specialization of it). | 7.1.10.5 |
| UAF-TYP-061 | must | The instance that owns an ActualProjectRole must be an ActualProject (or a specialization of it). | 7.1.10.5 |
| UAF-TYP-062 | must | The instance given as the value of an ActualProjectRole must be an ActualProject (or a specialization of it). | 7.1.10.5 |
| UAF-TYP-063 | must | The class that owns a ProtocolLayer must be a Protocol (or a specialization of it). | 7.1.11.2 |
| UAF-TYP-064 | must | The type of a ProtocolLayer must be a Protocol (or a specialization of it). | 7.1.11.2 |
| UAF-TYP-065 | must | The classifier of an ActualOrganization must be an Organization (or a specialization of it). | 7.1.12.1 |
| UAF-TYP-066 | must | The slots of an ActualOrganization must be an ActualOrganizationRole (or a specialization of it). | 7.1.12.1 |
| UAF-TYP-067 | must | The classifier of an ActualPerson must be a Person (or a specialization of it). | 7.1.12.1 |
| UAF-TYP-068 | must | The classifier of an ActualPost must be a Post (or a specialization of it). | 7.1.12.1 |
| UAF-TYP-069 | must | The classifier of an ActualResource must be a ResourcePerformer (or a specialization of it). | 7.1.12.1 |
| UAF-TYP-070 | must | The classifier of an ActualResponsibility must be a Responsibility (or a specialization of it). | 7.1.12.1 |
| UAF-TYP-071 | must | The classifier of a FieldedCapability must be a CapabilityConfiguration (or a specialization of it). | 7.1.12.1 |
| UAF-TYP-072 | must | The instance that owns an ActualOrganizationRole must be an ActualOrganization (or a specialization of it). | 7.1.12.2 |
| UAF-TYP-073 | must | The defining feature of an ActualResourceRole must be a ResourceRole (or a specialization of it). | 7.1.12.2 |
| UAF-TYP-074 | must | The instance that owns an ActualResourceRole must be an ActualResource (or a specialization of it). | 7.1.12.2 |
| UAF-TYP-075 | must | An ActualResourceRelationship must realize a ResourceExchange (or a specialization of it). | 7.1.12.3 |
| UAF-TYP-076 | must | The classifier of an ActualService must be a ServiceSpecification (or a specialization of it). | 7.1.12.4 |

## OWN: Ownership and behavior wiring

| Id | Strength | Rule | Section |
|---|---|---|---|
| UAF-OWN-001 | must | The behavior that specifies an OperationalMethod must be an OperationalActivity (or a specialization of it). | 7.1.5.2 |
| UAF-OWN-002 | must | The parameters owned by an OperationalMethod must be an OperationalParameter (or a specialization of it). | 7.1.5.2 |
| UAF-OWN-003 | must | An OperationalPerformer may be capable of performing only OperationalActivity elements (or their specializations). | 7.1.5.2 |
| UAF-OWN-004 | must | The operations owned by an OperationalPerformer must be an OperationalMethod (or a specialization of it). | 7.1.5.2 |
| UAF-OWN-005 | must | The ports owned by an OperationalPerformer must be an OperationalPort (or a specialization of it). | 7.1.5.2 |
| UAF-OWN-006 | must | The operations owned by an OperationalInterface must be an OperationalMethod (or a specialization of it). | 7.1.5.3 |
| UAF-OWN-007 | must | The parameters owned by an OperationalActivity must be an OperationalParameter (or a specialization of it). | 7.1.5.4 |
| UAF-OWN-008 | must | The activity that owns an OperationalActivityAction must be an OperationalActivity (or a specialization of it). | 7.1.5.4 |
| UAF-OWN-009 | must | The behavior called by an OperationalActivityAction must be an OperationalActivity (or a specialization of it). | 7.1.5.4 |
| UAF-OWN-010 | must | An OperationalActivityEdge must be owned, directly or indirectly, by an OperationalActivity (or a specialization). | 7.1.5.4 |
| UAF-OWN-011 | must | An OperationalStateDescription must be owned by an OperationalAgent (or a specialization of it). | 7.1.5.5 |
| UAF-OWN-012 | must | The operation on which an OperationalMessage receives its event must be an OperationalMethod (or a specialization of it). | 7.1.5.6 |
| UAF-OWN-013 | must | An InformationElement must be owned by a DataModel (or a specialization of it). | 7.1.5.7 |
| UAF-OWN-014 | must | The behavior that specifies a ServiceMethod must be a ServiceFunction (or a specialization of it). | 7.1.6.2 |
| UAF-OWN-015 | must | The parameters owned by a ServiceMethod must be a ServiceParameter (or a specialization of it). | 7.1.6.2 |
| UAF-OWN-016 | must | A ServiceMethod must be owned by a ServiceSpecification (or a specialization of it). | 7.1.6.2 |
| UAF-OWN-017 | must | The operations owned by a ServiceInterface must be a ServiceMethod (or a specialization of it). | 7.1.6.3 |
| UAF-OWN-018 | must | The parameters owned by a ServiceFunction must be a ServiceParameter (or a specialization of it). | 7.1.6.4 |
| UAF-OWN-019 | must | The activity that owns a ServiceFunctionAction must be a ServiceFunction (or a specialization of it). | 7.1.6.4 |
| UAF-OWN-020 | must | The behavior called by a ServiceFunctionAction must be a ServiceFunction (or a specialization of it). | 7.1.6.4 |
| UAF-OWN-021 | must | A ServiceStateDescription must be owned by a ServiceSpecification (or a specialization of it). | 7.1.6.5 |
| UAF-OWN-022 | must | The operation on which a ServiceMessage receives its event must be a ServiceMethod (or a specialization of it). | 7.1.6.6 |
| UAF-OWN-023 | must | A ResourcePerformer may be capable of performing only Function elements (or their specializations). | 7.1.8.1 |
| UAF-OWN-024 | must | The operations owned by a ResourcePerformer must be a ResourceMethod (or a specialization of it). | 7.1.8.1 |
| UAF-OWN-025 | must | The ports owned by a ResourcePerformer must be a ResourcePort (or a specialization of it). | 7.1.8.1 |
| UAF-OWN-026 | must | The behavior that specifies a ResourceMethod must be a Function (or a specialization of it). | 7.1.8.2 |
| UAF-OWN-027 | must | The parameters owned by a ResourceMethod must be a ResourceParameter (or a specialization of it). | 7.1.8.2 |
| UAF-OWN-028 | must | The operations owned by a ResourceInterface must be a ResourceMethod (or a specialization of it). | 7.1.8.3 |
| UAF-OWN-029 | must | The parameters owned by a Function must be a ResourceParameter (or a specialization of it). | 7.1.8.4 |
| UAF-OWN-030 | must | The activity that owns a FunctionAction must be a Function (or a specialization of it). | 7.1.8.4 |
| UAF-OWN-031 | must | The behavior called by a FunctionAction must be a Function (or a specialization of it). | 7.1.8.4 |
| UAF-OWN-032 | must | A FunctionEdge must be owned, directly or indirectly, by a Function (or a specialization). | 7.1.8.4 |
| UAF-OWN-033 | must | A ResourceStateDescription must be owned by a ResourcePerformer (or a specialization of it). | 7.1.8.5 |
| UAF-OWN-034 | must | The operation on which a ResourceMessage receives its event must be a ResourceMethod (or a specialization of it). | 7.1.8.6 |
| UAF-OWN-035 | must | A DataElement must be owned by a DataModel (or a specialization of it). | 7.1.8.7 |
| UAF-OWN-036 | must | The behavior a SecurityProcessAction calls must be a SecurityControl (the standard states this under the name SecurityControlAction). | 7.1.9.3 |
| UAF-OWN-037 | must | The behavior called by a ProjectActivityAction must be a ProjectActivity (or a specialization of it). | 7.1.10.4 |
| UAF-OWN-038 | must | The activity that owns a ProjectActivityAction must be a ProjectActivity (or a specialization of it). | 7.1.10.4 |

## XCH: Exchanges

| Id | Strength | Rule | Section |
|---|---|---|---|
| UAF-XCH-001 | must | The element an OperationalExchange conveys depends on its exchange kind: for InformationExchange an InformationElement; for MaterielExchange a ResourceArtifact; for EnergyExchange a NaturalResource; for OrganizationalExchange an OrganizationalResource; for ConfigurationExchange a CapabilityConfiguration; for GeoPoliticalExtentExchange a GeoPoliticalExtentType (each or a specialization). | 7.1.5.3 |
| UAF-XCH-002 | must | The activity edge that realizes an OperationalExchange must be an OperationalActivityEdge (or a specialization of it). | 7.1.5.3 |
| UAF-XCH-003 | must | The connector that realizes an OperationalExchange must be an OperationalConnector (or a specialization of it). | 7.1.5.3 |
| UAF-XCH-004 | must | The message that realizes an OperationalExchange must be an OperationalMessage (or a specialization of it). | 7.1.5.3 |
| UAF-XCH-005 | must | The element conveyed by a Command must be a DataElement (or a specialization of it). | 7.1.7.2 |
| UAF-XCH-006 | must | The element conveyed by a Control must be a DataElement (or a specialization of it). | 7.1.7.2 |
| UAF-XCH-007 | must | The element a ResourceExchange conveys depends on its exchange kind: for ResourceCommunication a DataElement; for ResourceMovement a PhysicalResource; for ResourceEnergyFlow a NaturalResource; for GeoPoliticalExtentExchange a GeoPoliticalExtentType (each or a specialization). | 7.1.8.3 |
| UAF-XCH-008 | must | The activity edge that realizes a ResourceExchange must be a FunctionEdge (or a specialization of it). | 7.1.8.3 |
| UAF-XCH-009 | must | The connector that realizes a ResourceExchange must be a ResourceConnector (or a specialization of it). | 7.1.8.3 |
| UAF-XCH-010 | must | The message that realizes a ResourceExchange must be a ResourceMessage (or a specialization of it). | 7.1.8.3 |

## VAL: Value rules

| Id | Strength | Rule | Section |
|---|---|---|---|
| UAF-VAL-001 | must | The start and end dates of an ActualEnterprisePhase must fall within the start and end dates of the enclosing ActualEnterprisePhase that holds it as a slot value. | 7.1.4.1 |
| UAF-VAL-002 | must | The client and the supplier of a Forecast must be the same specialization of SubjectOfForecast (for example Software to Software, Standard to Standard). | 7.1.8.9 |
| UAF-VAL-003 | must | All the ProjectTheme properties owned by one ProjectMilestone must be typed by the same StatusIndicators (or a specialization). | 7.1.10.1 |

## CARD: Cardinality

| Id | Strength | Rule | Section |
|---|---|---|---|
| UAF-CARD-001 | must | Every ActualLocation must have exactly one locationNamedByAddress (Boolean). | 7.1.2 |
| UAF-CARD-002 | must | Every ActualLocation must have exactly one locationKind (LocationKind). | 7.1.2 |
| UAF-CARD-003 | must | Every ActualMeasurement must have exactly one intention (ActualMeasurementKind). | 7.1.2 |
| UAF-CARD-004 | must | Every Environment must have exactly one kind (EnvironmentKind). | 7.1.2 |
| UAF-CARD-005 | must | Every GeoPoliticalExtentType must have exactly one kind (GeoPoliticalExtentTypeKind). | 7.1.2 |
| UAF-CARD-006 | must | Every Location must have exactly one kind (LocationTypeKind). | 7.1.2 |
| UAF-CARD-007 | must | Every Information must have exactly one informationKind (InformationKind). | 7.1.3.4 |
| UAF-CARD-008 | must | Every Rule must have exactly one ruleKind (RuleKind). | 7.1.3.5 |
| UAF-CARD-009 | must | Every ResponsibleFor must have exactly one ResponsibleRoleKind (ResponsibleRoleKind). | 7.1.7.5 |
| UAF-CARD-010 | must | Every ResourceRole must have exactly one RoleKind (RoleKind). | 7.1.8.2 |
| UAF-CARD-011 | must | Every WholeLifeConfiguration must have exactly one kind (WholeLifeConfigurationKind). | 7.1.8.9 |
| UAF-CARD-012 | must | Every ActualProject must have exactly one projectKind (ProjectKind). | 7.1.10.5 |
| UAF-CARD-013 | must | Every ActualProjectMilestone must have exactly one kind (ActualMilestoneKind). | 7.1.10.5 |
| UAF-CARD-014 | must | Every ArchitecturalDescription must have exactly one toBe (Boolean). | 7.1.13 |
| UAF-CARD-015 | must | Every ArchitecturalDescription must have exactly one architectureFramework (String). | 7.1.13 |
| UAF-CARD-016 | must | Every ArchitecturalDescription must have exactly one viewPoint (Viewpoint). | 7.1.13 |
| UAF-CARD-017 | must | Every View must have exactly one viewpoint (Viewpoint). | 7.1.13 |

## VIEW: Views and the grid

| Id | Strength | Rule | Section |
|---|---|---|---|
| UAF-VIEW-001 | should | A view built to a view specification shows only the elements listed for that specification (plus the frame elements of its diagram type). | DMM 2; profile Annex A |
| UAF-VIEW-002 | note | A view is framed by the SysML diagram type that underlies it, and its elements are drawn in the notation of the metaclass the element extends. | 6.4 |
| UAF-VIEW-003 | note | Implementers follow the view naming conventions of the framework they intend to implement. | 6.3 |
| UAF-VIEW-004 | note | To evaluate behavior and constraints, actual instances of the architectural elements are defined; parametric analysis and simulation are expected from the tool. | DMM 1.1 (note b) |
| UAF-VIEW-005 | note | The information model is a column across the layers, in conceptual or logical form; a physical schema is not built in the framework but imported or linked. | DMM 1.1 (notes c, e) |
| UAF-VIEW-006 | note | The parameters column holds the measures and environments for all layers. | DMM 1.1 (note d) |

## GUID: Guidance

| Id | Strength | Rule | Section |
|---|---|---|---|
| UAF-GUID-001 | note | Architecture descriptions use the terms of ISO/IEC/IEEE 42010 (architecture, architecture description, view, viewpoint, concern, stakeholder, model kind); the correspondence rules are expressed as constraints on the profile. | 1.2 |
| UAF-GUID-002 | note | The constraint pictures in the specification (metaconstraint and metarelationship dependencies) are for reading only; the constraints are stated in structured English and are implementable, for example, in OCL. | 6.5 |
| UAF-GUID-003 | note | The grid is not meant to be complete; gaps between domains and model kinds are intended. | DMM 1.1 |
| UAF-GUID-004 | note | The profile annex that lists which elements fit each view is informative guidance, not a requirement. | Annex A (profile) |
