# UPDM 2.1 rules

Generated from `language.yaml` (`constraints`). Do not edit by hand; change the language file and regenerate.

Each rule has a stable id of the form `UPDM-<CAT>-nnn`. The number never changes once assigned. A rule that is retired keeps its id and is marked withdrawn rather than reused.

## Strength

| Strength | Meaning |
|---|---|
| must | The profile states it as a formal constraint (a "must" or "has to be" rule) or the specification states it with "must". A model that breaks it is not well formed. |
| should | The specification gives it as a recommendation or as guidance on what a view expects. Breaking it is a warning, not an error. |
| note | The specification states it as an expectation, an option or a method note. It is recorded for completeness and is not checkable on its own. |

Where a rule says "a Capability", it means a Capability or any element that specializes it. The standard's constraint text varies on this point (some entries add "or its specializations", some do not); the rules read all of them the same way. Alias elements (the DoDAF and MODAF names) inherit every rule of the element they alias.

## Categories

| Category | Name | Covers | Rules |
|---|---|---|---|
| CONF | Conformance | What a tool must support to claim conformance at level 0 or level 1. | 9 |
| GEN | General structure | Rules that hold broadly: abstract elements, aliases, dates, enterprise phases, rule kinds. | 12 |
| END | Relationship ends | Which kinds of element a relationship, annotation or constraint may attach to at each end. | 74 |
| TYP | Typing | Which kind a role, port, instance or slot must be typed or classified by. | 52 |
| OWN | Ownership and behavior wiring | Which owner, attributes, ports, operations, parameters and called behaviors each element may have. | 55 |
| XCH | Exchanges | What an operational exchange conveys for each exchange kind. | 6 |
| SYS | SysML pairing (level 1) | Which SysML element must accompany a profile element at compliance level 1. | 39 |
| VIEW | Views and ordering | What a view or milestone sequence expects, and how DoDAF and MODAF views relate. | 14 |
| GUID | Guidance | Method notes and expectations that are not checkable on their own. | 3 |

Total: 264 rules (240 must, 6 should, 18 note).

Section references: a number such as 8.3.1.1.4.4 is the clause of the UPDM 2.1 specification (formal/13-08-04) that holds the element named in brackets; "A", "B" and "C" refer to the annexes; "2.1.1" and "2.1.2" to the compliance levels. Properties named in the rules (client, supplier, classifier, type, class, owner and so on) are the UML properties of the extended element.

## CONF: Conformance

| Id | Strength | Rule | Section |
|---|---|---|---|
| UPDM-CONF-001 | must | A tool conforms at compliance level 0 only if every element, attribute, constraint, association and package structure scoped to the level 0 package, including its sub-packages, exists and complies with the specification. | 2.1.1 |
| UPDM-CONF-002 | must | A conforming tool supports exchange of both the user model and the profile through the XMI interchange format. | 2.1.1; 2.1.2 |
| UPDM-CONF-003 | must | A level 0 tool imports and exports level 0 models with full fidelity, with no loss and no transformation. | 2.1.1 |
| UPDM-CONF-004 | must | A level 0 tool imports level 1 models with only minimal loss. | 2.1.1 |
| UPDM-CONF-005 | must | Compliance level 1 includes everything in level 0, imports the whole SysML profile with its sub-profiles, and adds the constraints that pair SysML elements with level 0 elements (rules UPDM-SYS-001 to 039). | 2.1.2; 8.1 |
| UPDM-CONF-006 | must | A level 1 tool imports and exports level 1 models with full fidelity, with no loss and no transformation. | 2.1.2 |
| UPDM-CONF-007 | must | A level 1 tool imports level 0 models with no loss, transforming where necessary. | 2.1.2 |
| UPDM-CONF-008 | note | Level 0 imports a minimum of ten SoaML elements (Capability, ServiceInterface, Expose, Attachment, Request, Service, MessageType, Property, ServiceChannel, Participant); they are used as SoaML defines them and are not redocumented. | 2.1.1; 7.6.2; 8.3.1 |
| UPDM-CONF-009 | note | The specification states that it conforms to DoDAF 2.02 at level 3, the physical data model; each tool vendor remains responsible for its own conformance claim. The DoD CIO did not expect export of the physical exchange specification or a four-dimensional implementation. | 3.4.1 |

## GEN: General structure

| Id | Strength | Rule | Section |
|---|---|---|---|
| UPDM-GEN-001 | must | If the architecture framework of an ArchitecturalDescription is DoDAF, only aliases scoped under the DoDAF elements may be used; if it is MODAF, only the MODAF aliases; if it is not set, no aliases may be used. | 8.3.1.1.2.7 (ArchitecturalDescription) |
| UPDM-GEN-002 | must | The start and end of an EnterprisePhase must fall within the start and end of the enterprise it belongs to, the whole life cycle. | 8.3.1.1.6.1 (EnterprisePhase) |
| UPDM-GEN-003 | must | All the ProjectThemes owned by a ProjectMilestone must be typed by the same StatusIndicators. | 8.3.1.3.1.1 (ProjectMilestone) |
| UPDM-GEN-004 | must | The rule kind of a DesignRule is Guidance. | 8.3.1.5 (DesignRule) |
| UPDM-GEN-005 | must | The client and supplier of a Forecast must be the same specialization of SubjectOfForecast (Software to Software, Standard to Standard, and so on). | 8.3.1.1.7.4 (Forecast) |
| UPDM-GEN-006 | must | An abstract element is never applied directly; only its concrete specializations are used. Thirty-three elements are abstract. | XMI isAbstract flags; 8.3.1 entries marked abstract |
| UPDM-GEN-007 | note | Where DoDAF and MODAF name the same concept differently, the profile defines one element and gives the other framework's name as an alias by specialization. Alias elements add no new rules; they inherit all constraints of the element they alias. | 7.6.1 |
| UPDM-GEN-008 | note | The Core elements are common to DoDAF and MODAF and are always used together with the DoDAF or MODAF elements; nothing prevents using DoDAF and MODAF elements in one model. | 8.3.1.1 |
| UPDM-GEN-009 | must | Dates and times are written in the ISO 8601 date-time format with a time zone designator (YYYY-MM-DDThh:mm:ssTZD). | 8.3.1.1.3 (ISO8601DateTime) |
| UPDM-GEN-010 | note | Nearly every profile element specializes UPDMElement and so may carry a URI, links to the standards it conforms to, boundary dates, and links to measurement sets for quantitative metrics. | 8.3.1.1.2.2 |
| UPDM-GEN-011 | note | Every profile element traces to a domain-metamodel concept; the diagrams that show constraints and dependencies between profile elements are documentation notation and are not part of the interchanged profile. | 7.2; 7.4 |
| UPDM-GEN-012 | note | The profile is built to be extended: StereotypeExtension records an additional element that the profile does not define, and OntologyReference elements link to external ontologies; custom (user-defined) views are supported. | 1; 8.3.1.3.2.2 |

## END: Relationship ends

| Id | Strength | Rule | Section |
|---|---|---|---|
| UPDM-END-001 | must | The source of an ActualOrganizationRelationship must be an ActualOrganizationalResource (or a specialization of it). | 8.3.1.1.4.4.18.1 (ActualOrganizationRelationship) |
| UPDM-END-002 | must | The target of an ActualOrganizationRelationship must be a ResourceInteraction (or a specialization of it). (The standard labels this the realizes end and names ResourceInteraction; ActualOrganizationalResource is probably meant. Kept as written.) | 8.3.1.1.4.4.18.1 (ActualOrganizationRelationship) |
| UPDM-END-003 | must | What an ActualOrganizationRelationship conveys must be an ExchangeElement (or a specialization of it). | 8.3.1.1.4.4.18.1 (ActualOrganizationRelationship) |
| UPDM-END-004 | must | The client of a FillsPost must be an ActualPerson (or a specialization of it). | 8.3.1.1.4.4.18.1 (FillsPost) |
| UPDM-END-005 | must | The supplier of a FillsPost must be an ActualPost (or a specialization of it). | 8.3.1.1.4.4.18.1 (FillsPost) |
| UPDM-END-006 | must | The client of a ProvidesCompetence must be a CompetenceProvider (or a specialization of it). | 8.3.1.1.4.4.18.2 (ProvidesCompetence) |
| UPDM-END-007 | must | The supplier of a ProvidesCompetence must be a Competence (or a specialization of it). | 8.3.1.1.4.4.18.2 (ProvidesCompetence) |
| UPDM-END-008 | must | The client of a RequiresCompetence must be a CompetenceRequirer (or a specialization of it). | 8.3.1.1.4.4.18.2 (RequiresCompetence) |
| UPDM-END-009 | must | The supplier of a RequiresCompetence must be a Competence (or a specialization of it). | 8.3.1.1.4.4.18.2 (RequiresCompetence) |
| UPDM-END-010 | must | The client of an ArbitraryConnector must be a ConceptRole (or a specialization of it). | 8.3.1.1.4.4 (ArbitraryConnector) |
| UPDM-END-011 | must | The supplier of an ArbitraryConnector must be a ConceptRole (or a specialization of it). | 8.3.1.1.4.4 (ArbitraryConnector) |
| UPDM-END-012 | must | The role at each end of a Needline must be a NodeRole or a NodePort (or a specialization of them). | 8.3.1.1.4.4 (Needline) |
| UPDM-END-013 | must | The information source of a Command must be an OrganizationalResource (or a specialization of it). | 8.3.1.1.4.3 (Command) |
| UPDM-END-014 | must | The information target of a Command must be an OrganizationalResource (or a specialization of it). | 8.3.1.1.4.3 (Command) |
| UPDM-END-015 | must | What a Command conveys must be an ExchangeElement (or a specialization of it). | 8.3.1.1.4.3 (Command) |
| UPDM-END-016 | must | A connector that realizes an OperationalExchange must be a Needline or a ServiceChannel (or a specialization of them). | 8.3.1.1.4.3 (OperationalExchange) |
| UPDM-END-017 | must | An activity edge that realizes an OperationalExchange must be an OperationalActivityEdge (or a specialization of it). | 8.3.1.1.4.3 (OperationalExchange) |
| UPDM-END-018 | must | The information source of an OperationalExchange must be a Node (or a specialization of it). | 8.3.1.1.4.3 (OperationalExchange) |
| UPDM-END-019 | must | The information target of an OperationalExchange must be a Node (or a specialization of it). | 8.3.1.1.4.3 (OperationalExchange) |
| UPDM-END-020 | must | A message that realizes an OperationalExchange must be an OperationalMessage (or a specialization of it). | 8.3.1.1.4.3 (OperationalExchange) |
| UPDM-END-021 | must | The role at each end of a ResourceInterface must be a ResourceRole (or a specialization of it). | 8.3.1.1.7.4 (ResourceInterface) |
| UPDM-END-022 | must | The client of a Forecast must be a SubjectOfForecast (or a specialization of it). | 8.3.1.1.7.4 (Forecast) |
| UPDM-END-023 | must | The supplier of a Forecast must be a SubjectOfForecast (or a specialization of it). | 8.3.1.1.7.4 (Forecast) |
| UPDM-END-024 | must | The role at each end of a ResourceConnector must be a ResourcePort (or a specialization of it). | 8.3.1.1.7.4 (ResourceConnector) |
| UPDM-END-025 | must | What a ResourceInteraction conveys must be a ResourceInteractionItem (or a specialization of it). | 8.3.1.1.7.3 (ResourceInteraction) |
| UPDM-END-026 | must | An activity edge that realizes a ResourceInteraction must be a FunctionEdge (or a specialization of it). | 8.3.1.1.7.3 (ResourceInteraction) |
| UPDM-END-027 | must | A connector that realizes a ResourceInteraction must be a ResourceInterface, a ResourceConnector or a ServiceChannel (or a specialization of them). | 8.3.1.1.7.3 (ResourceInteraction) |
| UPDM-END-028 | must | The information source of a ResourceInteraction must be a SystemResource (or a specialization of it). | 8.3.1.1.7.3 (ResourceInteraction) |
| UPDM-END-029 | must | The information target of a ResourceInteraction must be a SystemResource (or a specialization of it). | 8.3.1.1.7.3 (ResourceInteraction) |
| UPDM-END-030 | must | What realizes a ResourceInteraction must be a ResourceInterface or an ActualOrganizationRelationship (or a specialization of them). | 8.3.1.1.7.3 (ResourceInteraction) |
| UPDM-END-031 | must | The client of an ArchitecturalReference must be an ArchitecturalDescription (or a specialization of it). | 8.3.1.1.2.7 (ArchitecturalReference) |
| UPDM-END-032 | must | The supplier of an ArchitecturalReference must be an ArchitecturalDescription (or a specialization of it). | 8.3.1.1.2.7 (ArchitecturalReference) |
| UPDM-END-033 | must | The client of an IsCapableOfPerforming must be a Node, a SystemResource or a ServiceInterface (or a specialization of them). | 8.3.1.1.2.3 (IsCapableOfPerforming) |
| UPDM-END-034 | must | The supplier of an IsCapableOfPerforming must be an OperationalActivity, a Function or a ServiceFunction (or a specialization of them). | 8.3.1.1.2.3 (IsCapableOfPerforming) |
| UPDM-END-035 | must | The client of an Implements must be a SystemResource, a ResourceInteraction, a Function or a ServiceFunction (or a specialization of them). | 8.3.1.1.2.3 (Implements) |
| UPDM-END-036 | must | The supplier of an Implements must be a Node, an OperationalActivity, an OperationalExchange or a Function (or a specialization of them). | 8.3.1.1.2.3 (Implements) |
| UPDM-END-037 | must | The client of a Details must be an EntityItem (or a specialization of it). | 8.3.1.1.8.5 (Details) |
| UPDM-END-038 | must | The supplier of a Details must be an ExchangeElement (or a specialization of it). | 8.3.1.1.8.5 (Details) |
| UPDM-END-039 | must | The type at each end of an EntityRelationship must be an EntityItem (or a specialization of it). | 8.3.1.1.8.5 (EntityRelationship) |
| UPDM-END-040 | must | The client of a MapsToCapability must be an Activity (or a specialization of it). | 8.3.1.1.6.1 (MapsToCapability) |
| UPDM-END-041 | must | The supplier of a MapsToCapability must be a Capability (or a specialization of it). | 8.3.1.1.6.1 (MapsToCapability) |
| UPDM-END-042 | must | The client of an Exhibits must be a CapableElement (or a specialization of it). | 8.3.1.1.6.1 (Exhibits) |
| UPDM-END-043 | must | The supplier of an Exhibits must be a Capability (or a specialization of it). | 8.3.1.1.6.1 (Exhibits) |
| UPDM-END-044 | must | The client of an OrganizationalProjectRelationship must be an ActualProject (or a specialization of it). | 8.3.1.1.1.1 (OrganizationalProjectRelationship) |
| UPDM-END-045 | must | The supplier of an OrganizationalProjectRelationship must be an ActualOrganizationalResource (or a specialization of it). | 8.3.1.1.1.1 (OrganizationalProjectRelationship) |
| UPDM-END-046 | must | The client of an ActivityPartOfProject must be a ProjectActivity (or a specialization of it). | 8.3.1.2.1 (ActivityPartOfProject) |
| UPDM-END-047 | must | The supplier of an ActivityPartOfProject must be an ActualProject (or a specialization of it). | 8.3.1.2.1 (ActivityPartOfProject) |
| UPDM-END-048 | must | The client of a DesiredEffect must be a Desirer (or a specialization of it). | 8.3.1.2.5 (DesiredEffect) |
| UPDM-END-049 | must | The supplier of a DesiredEffect must be a DesiredState (or a specialization of it). | 8.3.1.2.5 (DesiredEffect) |
| UPDM-END-050 | must | The client of a Trustline must be a Node (or a specialization of it). | 8.3.1.3.3.3 (Trustline) |
| UPDM-END-051 | must | The supplier of a Trustline must be a Node (or a specialization of it). | 8.3.1.3.3.3 (Trustline) |
| UPDM-END-052 | must | The client of an OwnsProcess must be an ActualOrganizationalResource (or a specialization of it). | 8.3.1.3.3.1 (OwnsProcess) |
| UPDM-END-053 | must | The supplier of an OwnsProcess must be a Process (or a specialization of it). | 8.3.1.3.3.1 (OwnsProcess) |
| UPDM-END-054 | must | What a Control conveys must be an ExchangeElement (or a specialization of it). | 8.3.1.3.3.2 (Control) |
| UPDM-END-055 | must | The information source of a Control must be an OrganizationalResource (or a specialization of it). | 8.3.1.3.3.2 (Control) |
| UPDM-END-056 | must | The information target of a Control must be a ResourceArtifact (or a specialization of it). | 8.3.1.3.3.2 (Control) |
| UPDM-END-057 | must | The client of a ProjectSequence must be an ActualProject (or a specialization of it). | 8.3.1.3.1.1 (ProjectSequence) |
| UPDM-END-058 | must | The supplier of a ProjectSequence must be an ActualProject (or a specialization of it). | 8.3.1.3.1.1 (ProjectSequence) |
| UPDM-END-059 | must | The client of a MilestoneSequence must be a ProjectMilestone (or a specialization of it). | 8.3.1.3.1.1 (MilestoneSequence) |
| UPDM-END-060 | must | The supplier of a MilestoneSequence must be a ProjectMilestone (or a specialization of it). | 8.3.1.3.1.1 (MilestoneSequence) |
| UPDM-END-061 | must | The client of a SameAs must be an UPDMElement (or a specialization of it). | 8.3.1.3.2.2 (SameAs) |
| UPDM-END-062 | must | The supplier of a SameAs must be any model element. | 8.3.1.3.2.2 (SameAs) |
| UPDM-END-063 | must | The client of an Overlap must be an UPDMElement (or a specialization of it). | 8.3.1.3.2.2 (Overlap) |
| UPDM-END-064 | must | The supplier of an Overlap must be any model element. | 8.3.1.3.2.2 (Overlap) |
| UPDM-END-065 | must | What a Contract conveys must be a Semantic or a Transactional (or a specialization of them). | 8.3.1.4 (Contract) |
| UPDM-END-066 | must | An ArchitectureMetadata may annotate only an ArchitecturalDescription (or a specialization of it). | 8.3.1.1.2.7 (ArchitectureMetadata) |
| UPDM-END-067 | must | A StandardConfiguration may annotate only a CapabilityConfiguration (or a specialization of it). | 8.3.1.1.8 (StandardConfiguration) |
| UPDM-END-068 | must | An Information may annotate only an UPDMElement (or a specialization of it). | 8.3.1.2.2 (Information) |
| UPDM-END-069 | must | A Definition may annotate only an UPDMElement (or a specialization of it). | 8.3.1.3.2.2 (Definition) |
| UPDM-END-070 | must | An Alias may annotate only an UPDMElement (or a specialization of it). | 8.3.1.3.2.2 (Alias) |
| UPDM-END-071 | must | A StereotypeExtension may annotate only an UPDMElement (or a specialization of it). | 8.3.1.3.2.2 (StereotypeExtension) |
| UPDM-END-072 | must | An OperationalConstraint may constrain only a SubjectOfOperationalConstraint (or a specialization of it). | 8.3.1.1.4.4 (OperationalConstraint) |
| UPDM-END-073 | must | A ResourceConstraint may constrain only a SubjectOfResourceConstraint (or a specialization of it). | 8.3.1.1.7.4 (ResourceConstraint) |
| UPDM-END-074 | must | A ServicePolicy may constrain only a ServiceInterface (or a specialization of it). | 8.3.1.1.5.2 (ServicePolicy) |

## TYP: Typing

| Id | Strength | Rule | Section |
|---|---|---|---|
| UPDM-TYP-001 | must | The classifier of an ActualOrganization must be an Organization (or a specialization of it). | 8.3.1.1.4.4.18.1 (ActualOrganization) |
| UPDM-TYP-002 | must | Every slot of an ActualOrganization must be an ActualOrganizationRole (or a specialization of it). | 8.3.1.1.4.4.18.1 (ActualOrganization) |
| UPDM-TYP-003 | must | The classifier of an ActualPost must be a Post (or a specialization of it). | 8.3.1.1.4.4.18.1 (ActualPost) |
| UPDM-TYP-004 | must | The classifier of an ActualPerson must be a Person (or a specialization of it). | 8.3.1.1.4.4.18.1 (ActualPerson) |
| UPDM-TYP-005 | must | The instance that owns an ActualOrganizationRole must be an ActualOrganization (or a specialization of it). | 8.3.1.1.4.4.18.1 (ActualOrganizationRole) |
| UPDM-TYP-006 | must | The defining feature of an ActualOrganizationRole must be a ResourceRole (or a specialization of it). | 8.3.1.1.4.4.18.1 (ActualOrganizationRole) |
| UPDM-TYP-007 | must | The type of a NodeRole must be a Node (or a specialization of it). | 8.3.1.1.4.4 (NodeRole) |
| UPDM-TYP-008 | must | The class that owns a NodeRole must be a NodeParent (or a specialization of it). | 8.3.1.1.4.4 (NodeRole) |
| UPDM-TYP-009 | must | The type of a ConceptRole must be a ConceptItem (or a specialization of it). | 8.3.1.1.4.4 (ConceptRole) |
| UPDM-TYP-010 | must | The type of a NodePort must be an OperationalExchangeItem (or a specialization of it). | 8.3.1.1.4.4 (NodePort) |
| UPDM-TYP-011 | must | The type of a KnownResource must be a SystemResource (or a specialization of it). | 8.3.1.1.4.4 (KnownResource) |
| UPDM-TYP-012 | must | The type of an OperationalParameter must be an OperationalExchangeItem (or a specialization of it). | 8.3.1.1.4.1 (OperationalParameter) |
| UPDM-TYP-013 | must | The type of a ResourcePort must be a ResourceInteractionItem (or a specialization of it). | 8.3.1.1.7.4 (ResourcePort) |
| UPDM-TYP-014 | must | The class that owns a ResourceRole must be a SystemResource (or a specialization of it). | 8.3.1.1.7.4 (ResourceRole) |
| UPDM-TYP-015 | must | The type of a ResourceRole must be a SystemResource (or a specialization of it). | 8.3.1.1.7.4 (ResourceRole) |
| UPDM-TYP-016 | must | The classifier of a FieldedCapability must be a CapabilityConfiguration (or a specialization of it). | 8.3.1.1.7.4 (FieldedCapability) |
| UPDM-TYP-017 | must | The class that owns a VersionOfConfiguration must be a WholeLifeConfiguration (or a specialization of it). | 8.3.1.1.7.4 (VersionOfConfiguration) |
| UPDM-TYP-018 | must | The type of a VersionOfConfiguration must be a SystemResource (or a specialization of it). | 8.3.1.1.7.4 (VersionOfConfiguration) |
| UPDM-TYP-019 | must | The type of a ResourceParameter must be a ResourceInteractionItem (or a specialization of it). | 8.3.1.1.7.1 (ResourceParameter) |
| UPDM-TYP-020 | must | The classifier of an ActualPropertySet must be a PropertySet (or a specialization of it). | 8.3.1.1.2.5 (ActualPropertySet) |
| UPDM-TYP-021 | must | Every slot of an ActualPropertySet must be an ActualProperty (or a specialization of it). | 8.3.1.1.2.5 (ActualPropertySet) |
| UPDM-TYP-022 | must | The defining feature of an ActualProperty must be a Property (or a specialization of it). | 8.3.1.1.2.5 (ActualProperty) |
| UPDM-TYP-023 | must | The instance that owns an ActualProperty must be a PropertySet (or a specialization of it). (The standard names PropertySet; ActualPropertySet is probably meant. Kept as written.) | 8.3.1.1.2.5 (ActualProperty) |
| UPDM-TYP-024 | must | The defining feature of an ActualMeasurement must be a Measurement (or a specialization of it). | 8.3.1.1.2.5 (ActualMeasurement) |
| UPDM-TYP-025 | must | The classifier of an ActualLocation must be a LocationType (or a specialization of it). | 8.3.1.1.2.4 (ActualLocation) |
| UPDM-TYP-026 | must | The class that owns an EnvironmentProperty must be an Environment (or a specialization of it). | 8.3.1.1.2.4 (EnvironmentProperty) |
| UPDM-TYP-027 | must | The type of an EnvironmentProperty must be a ConditionType (or a specialization of it). | 8.3.1.1.2.4 (EnvironmentProperty) |
| UPDM-TYP-028 | must | The type of a ServicePort must be a ServiceInterface (or a specialization of it). | 8.3.1.1.5.2 (ServicePort) |
| UPDM-TYP-029 | must | Every actual property set of a ServicePort must be a ServiceLevelValueSet (or a specialization of it). | 8.3.1.1.5.2 (ServicePort) |
| UPDM-TYP-030 | must | Every slot of a ServiceLevelValueSet must be a ServiceLevelValue (or a specialization of it). | 8.3.1.1.5.2 (ServiceLevelValueSet) |
| UPDM-TYP-031 | must | The type of a ServiceParameter must be a Resource (or a specialization of it). | 8.3.1.1.5.1 (ServiceParameter) |
| UPDM-TYP-032 | must | The signal that a ServiceMessageHandler handles must be an AsynchronousMessage (or a specialization of it). | 8.3.1.1.5.1 (ServiceMessageHandler) |
| UPDM-TYP-033 | must | The class that owns a TemporalPart must be an EnterprisePhase (or a specialization of it). | 8.3.1.1.6.1 (TemporalPart) |
| UPDM-TYP-034 | must | The type of a TemporalPart must be an EnterprisePhase (or a specialization of it). | 8.3.1.1.6.1 (TemporalPart) |
| UPDM-TYP-035 | must | The class that owns a StructuralPart must be an EnterprisePhase (or a specialization of it). | 8.3.1.1.6.1 (StructuralPart) |
| UPDM-TYP-036 | must | The type of a StructuralPart must be an EnterprisePhase (or a specialization of it). | 8.3.1.1.6.1 (StructuralPart) |
| UPDM-TYP-037 | must | The type of a CapabilityProperty must be a Capability (or a specialization of it). | 8.3.1.1.6.1 (CapabilityProperty) |
| UPDM-TYP-038 | must | The classifier of an ActualProject must be a Project (or a specialization of it). (The standard names Project, which is the DoDAF alias of ActualProject; ProjectType is probably meant. Kept as written.) | 8.3.1.1.1.1 (ActualProject) |
| UPDM-TYP-039 | must | The defining feature of an ActualProjectMilestoneRole must be a ProjectMilestoneRole (or a specialization of it). | 8.3.1.1.1.1 (ActualProjectMilestoneRole) |
| UPDM-TYP-040 | must | The instance that owns an ActualProjectMilestoneRole must be an ActualProject (or a specialization of it). | 8.3.1.1.1.1 (ActualProjectMilestoneRole) |
| UPDM-TYP-041 | must | The class that owns a ProjectMilestoneRole must be a Project (or a specialization of it). (The standard names Project, which is the DoDAF alias of ActualProject; ProjectType is probably meant. Kept as written.) | 8.3.1.1.1.1 (ProjectMilestoneRole) |
| UPDM-TYP-042 | must | The type of a ProjectMilestoneRole must be a ProjectMilestone (or a specialization of it). | 8.3.1.1.1.1 (ProjectMilestoneRole) |
| UPDM-TYP-043 | must | The class that owns a ConditionProperty must be a Condition (or a specialization of it). | 8.3.1.2.2.4 (ConditionProperty) |
| UPDM-TYP-044 | must | The classifier of a GeoPoliticalExtent must be a GeoPoliticalExtentType (or a specialization of it). | 8.3.1.2.2.4 (GeoPoliticalExtent) |
| UPDM-TYP-045 | must | The class that owns a ProblemDomain must be a LogicalArchitecture (or a specialization of it). | 8.3.1.3.3.3 (ProblemDomain) |
| UPDM-TYP-046 | must | The type of a ProblemDomain must be a Node (or a specialization of it). | 8.3.1.3.3.3 (ProblemDomain) |
| UPDM-TYP-047 | must | The classifier of an ActualProjectMilestone must be a ProjectMilestone (or a specialization of it). | 8.3.1.3.1.1 (ActualProjectMilestone) |
| UPDM-TYP-048 | must | Every slot of an ActualProjectMilestone must be a ProjectStatus (or a specialization of it). | 8.3.1.3.1.1 (ActualProjectMilestone) |
| UPDM-TYP-049 | must | The defining feature of a ProjectStatus must be a ProjectTheme (or a specialization of it). | 8.3.1.3.1.2 (ProjectStatus) |
| UPDM-TYP-050 | must | The type of a ProjectTheme must be a StatusIndicators (or a specialization of it). | 8.3.1.3.1.2 (ProjectTheme) |
| UPDM-TYP-051 | must | The class that owns a ProtocolLayer must be a Protocol (or a specialization of it). | 8.3.1.3.5 (ProtocolLayer) |
| UPDM-TYP-052 | must | The type of a ProtocolLayer must be a Protocol (or a specialization of it). | 8.3.1.3.5 (ProtocolLayer) |

## OWN: Ownership and behavior wiring

| Id | Strength | Rule | Section |
|---|---|---|---|
| UPDM-OWN-001 | must | Every attribute owned by a HighLevelOperationalConcept must be a ConceptRole (or a specialization of it). | 8.3.1.1.4.4 (HighLevelOperationalConcept) |
| UPDM-OWN-002 | must | What a Node is capable of performing must be only an OperationalActivity (or a specialization of it). | 8.3.1.1.4.4 (Node) |
| UPDM-OWN-003 | must | Every port owned by a Node must be a NodePort or a ServicePort (or a specialization of them). | 8.3.1.1.4.4 (Node) |
| UPDM-OWN-004 | must | Every operation owned by a Node must be a NodeOperation (or a specialization of it). | 8.3.1.1.4.4 (Node) |
| UPDM-OWN-005 | must | Every parameter owned by a NodeOperation must be an OperationalParameter (or a specialization of it). | 8.3.1.1.4.1 (NodeOperation) |
| UPDM-OWN-006 | must | The behavior that an OperationalActivityAction calls must be an OperationalActivity (or a specialization of it). | 8.3.1.1.4.1 (OperationalActivityAction) |
| UPDM-OWN-007 | must | The activity that an OperationalActivityAction calls must be an OperationalActivity (or a specialization of it). | 8.3.1.1.4.1 (OperationalActivityAction) |
| UPDM-OWN-008 | must | Every parameter owned by an OperationalActivity must be an OperationalParameter (or a specialization of it). | 8.3.1.1.4.1 (OperationalActivity) |
| UPDM-OWN-009 | must | The operation invoked by the receive event of an OperationalMessage must be a NodeOperation (or a specialization of it). | 8.3.1.1.4.1 (OperationalMessage) |
| UPDM-OWN-010 | must | The owner of an OperationalStateDescription must be a SubjectOfOperationalStateMachine (or a specialization of it). | 8.3.1.1.4.1 (OperationalStateDescription) |
| UPDM-OWN-011 | must | Every state in the regions of an OperationalStateDescription must be an OperationalState (or a specialization of it). | 8.3.1.1.4.1 (OperationalStateDescription) |
| UPDM-OWN-012 | must | An OperationalActivityEdge must be owned, directly or indirectly, by an OperationalActivity (or a specialization of it). | 8.3.1.1.4.1 (OperationalActivityEdge) |
| UPDM-OWN-013 | must | Every state machine owned by a SubjectOfOperationalStateMachine must be an OperationalStateDescription (or a specialization of it). (The standard names OperationalStateMachine, which no element defines; read as OperationalStateDescription.) | 8.3.1.1.4.1 (SubjectOfOperationalStateMachine) |
| UPDM-OWN-014 | must | The owner of an OperationalEventTrace must be a Node (or a specialization of it). | 8.3.1.1.4.1 (OperationalEventTrace) |
| UPDM-OWN-015 | must | Every message in an OperationalEventTrace must be an OperationalMessage (or a specialization of it). | 8.3.1.1.4.1 (OperationalEventTrace) |
| UPDM-OWN-016 | must | Every operation owned by a SystemResource must be a ResourceOperation (or a specialization of it). | 8.3.1.1.7.4 (SystemResource) |
| UPDM-OWN-017 | must | What a SystemResource performs must be only a Function (or a specialization of it). (The standard writes "Functions".) | 8.3.1.1.7.4 (SystemResource) |
| UPDM-OWN-018 | must | Every port owned by a SystemResource must be a ServicePort (or a specialization of it). The same section defines ResourcePort as an interface a resource provides, and UPDM-END-024 requires each end of a ResourceConnector to be a ResourcePort, so the standard conflicts with itself here. | 8.3.1.1.7.4 (SystemResource) |
| UPDM-OWN-019 | must | The owner of a ResourceStateMachine must be a SystemResource (or a specialization of it). | 8.3.1.1.7.1 (ResourceStateMachine) |
| UPDM-OWN-020 | must | Every state in the regions of a ResourceStateMachine must be a ResourceState (or a specialization of it). | 8.3.1.1.7.1 (ResourceStateMachine) |
| UPDM-OWN-021 | must | A FunctionEdge must be owned, directly or indirectly, by a Function (or a specialization of it). | 8.3.1.1.7.1 (FunctionEdge) |
| UPDM-OWN-022 | must | Every parameter owned by a Function must be a ResourceParameter (or a specialization of it). | 8.3.1.1.7.1 (Function) |
| UPDM-OWN-023 | must | The owner of a ResourceEventTrace must be a Resource (or a specialization of it). | 8.3.1.1.7.1 (ResourceEventTrace) |
| UPDM-OWN-024 | must | Every message in a ResourceEventTrace must be a ResourceMessage (or a specialization of it). | 8.3.1.1.7.1 (ResourceEventTrace) |
| UPDM-OWN-025 | must | The operation invoked by the receive event of a ResourceMessage must be a ResourceOperation (or a specialization of it). | 8.3.1.1.7.1 (ResourceMessage) |
| UPDM-OWN-026 | must | Every parameter owned by a ResourceOperation must be a ResourceParameter (or a specialization of it). | 8.3.1.1.7.1 (ResourceOperation) |
| UPDM-OWN-027 | must | The behavior that a FunctionAction calls must be a Function (or a specialization of it). | 8.3.1.1.7.1 (FunctionAction) |
| UPDM-OWN-028 | must | The activity that a FunctionAction calls must be a Function (or a specialization of it). | 8.3.1.1.7.1 (FunctionAction) |
| UPDM-OWN-029 | must | Every classifier owned by a DataModel must be an EntityItem (or a specialization of it). | 8.3.1.1.7.2 (DataModel) |
| UPDM-OWN-030 | must | Every attribute owned by a PropertySet must be a Property (or a specialization of it). | 8.3.1.1.2.5 (PropertySet) |
| UPDM-OWN-031 | must | Every attribute owned by a MeasurementSet must be a Measurement (or a specialization of it). | 8.3.1.1.2.5 (MeasurementSet) |
| UPDM-OWN-032 | must | Every attribute owned by an Environment must be an EnvironmentProperty (or a specialization of it). | 8.3.1.1.2.4 (Environment) |
| UPDM-OWN-033 | must | Every port owned by a Participant must be a ServicePort (or a specialization of it). A Node is a Participant by inheritance, and UPDM-OWN-003 allows a NodePort or a ServicePort on a Node, so the standard conflicts with itself here. The more specific clause, UPDM-OWN-003, governs a Node. | 8.3.1.1.2.6 (Participant) |
| UPDM-OWN-034 | must | Every attribute owned by an EntityItem must be an EntityAttribute (or a specialization of it). | 8.3.1.1.8.5 (EntityItem) |
| UPDM-OWN-035 | must | An EntityAttribute may be applied only to properties owned by an EntityItem (or a specialization of it). | 8.3.1.1.8.5 (EntityAttribute) |
| UPDM-OWN-036 | must | Every feature of a ServiceInterface must be a ServiceFeature (or a specialization of it). | 8.3.1.1.5.2 (ServiceInterface) |
| UPDM-OWN-037 | must | Every attribute owned by a ServiceInterface must be a ServiceAttribute (or a specialization of it). | 8.3.1.1.5.2 (ServiceInterface) |
| UPDM-OWN-038 | must | Every parameter owned by a ServiceOperation must be a ServiceParameter (or a specialization of it). | 8.3.1.1.5.1 (ServiceOperation) |
| UPDM-OWN-039 | must | The operation invoked by the receive event of a ServiceMessage must be a ServiceOperation (or a specialization of it). | 8.3.1.1.5.1 (ServiceMessage) |
| UPDM-OWN-040 | must | Every parameter owned by a ServiceFeature must be a ServiceParameter (or a specialization of it). | 8.3.1.1.5.1 (ServiceFeature) |
| UPDM-OWN-041 | must | The owner of a ServiceFeature must be a ServiceInterface (or a specialization of it). | 8.3.1.1.5.1 (ServiceFeature) |
| UPDM-OWN-042 | must | The owner of a ServiceInteraction must be a ServiceInterface (or a specialization of it). | 8.3.1.1.5.1 (ServiceInteraction) |
| UPDM-OWN-043 | must | Every message in a ServiceInteraction must be a ServiceMessage (or a specialization of it). | 8.3.1.1.5.1 (ServiceInteraction) |
| UPDM-OWN-044 | must | The owner of a ServiceFunctionEdge must be a ServiceFunction (or a specialization of it). | 8.3.1.1.5.1 (ServiceFunctionEdge) |
| UPDM-OWN-045 | must | Every parameter owned by a ServiceFunction must be a ServiceParameter (or a specialization of it). | 8.3.1.1.5.1 (ServiceFunction) |
| UPDM-OWN-046 | must | The owner of a ServiceStateMachine must be a ServiceInterface (or a specialization of it). | 8.3.1.1.5.1 (ServiceStateMachine) |
| UPDM-OWN-047 | must | The behavior that a ServiceFunctionAction calls must be a ServiceFunction (or a specialization of it). | 8.3.1.1.5.1 (ServiceFunctionAction) |
| UPDM-OWN-048 | must | The activity that a ServiceFunctionAction calls must be a ServiceFunction (or a specialization of it). | 8.3.1.1.5.1 (ServiceFunctionAction) |
| UPDM-OWN-049 | must | Every attribute owned by a Capability must be a CapabilityProperty (or a specialization of it). | 8.3.1.1.6.1 (Capability) |
| UPDM-OWN-050 | must | Every attribute owned by a ProjectType must be a ProjectMilestoneRole (or a specialization of it). | 8.3.1.1.1.1 (ProjectType) |
| UPDM-OWN-051 | must | Every attribute owned by a Condition must be a ConditionProperty (or a specialization of it). | 8.3.1.2.2.4 (Condition) |
| UPDM-OWN-052 | must | Every attribute owned by a ProjectMilestone must be a ProjectTheme (or a specialization of it). | 8.3.1.3.1.1 (ProjectMilestone) |
| UPDM-OWN-053 | must | Every attribute owned by a Transactional must be a TransactionalAttribute (or a specialization of it). | 8.3.1.4 (Transactional) |
| UPDM-OWN-054 | must | Every attribute owned by a Wrapper must be a WrapperAttribute (or a specialization of it). | 8.3.1.4 (Wrapper) |
| UPDM-OWN-055 | must | Every attribute owned by a Semantic must be a SemanticAttribute (or a specialization of it). | 8.3.1.4 (Semantic) |

## XCH: Exchanges

| Id | Strength | Rule | Section |
|---|---|---|---|
| UPDM-XCH-001 | must | When the exchange kind of an OperationalExchange is InformationExchange, what it conveys must be an ExchangeElement (or a specialization of it). | 8.3.1.1.4.3 (OperationalExchange) |
| UPDM-XCH-002 | must | When the exchange kind of an OperationalExchange is MaterielExchange, what it conveys must be a ResourceArtifact (or a specialization of it). | 8.3.1.1.4.3 (OperationalExchange) |
| UPDM-XCH-003 | must | When the exchange kind of an OperationalExchange is EnergyExchange, what it conveys must be an Energy (or a specialization of it). | 8.3.1.1.4.3 (OperationalExchange) |
| UPDM-XCH-004 | must | When the exchange kind of an OperationalExchange is OrganizationalExchange, what it conveys must be an OrganizationalResource (or a specialization of it). | 8.3.1.1.4.3 (OperationalExchange) |
| UPDM-XCH-005 | must | When the exchange kind of an OperationalExchange is ConfigurationExchange, what it conveys must be a CapabilityConfiguration (or a specialization of it). | 8.3.1.1.4.3 (OperationalExchange) |
| UPDM-XCH-006 | must | When the exchange kind of an OperationalExchange is GeoPoliticalExtentExchange, what it conveys must be a GeoPoliticalExtent (or a specialization of it). | 8.3.1.1.4.3 (OperationalExchange) |

## SYS: SysML pairing (level 1)

| Id | Strength | Rule | Section |
|---|---|---|---|
| UPDM-SYS-001 | must | At compliance level 1, a UML element to which Software is applied must also have the SysML Block applied. | 8.3 (Software) |
| UPDM-SYS-002 | must | At compliance level 1, a UML element to which HighLevelOperationalConcept is applied must also have the SysML Block applied. | 8.3 (HighLevelOperationalConcept) |
| UPDM-SYS-003 | must | At compliance level 1, a UML element to which EntityItem is applied must also have the SysML Block applied. | 8.3 (EntityItem) |
| UPDM-SYS-004 | must | At compliance level 1, a UML element to which CapabilityConfiguration is applied must also have the SysML Block applied. | 8.3 (CapabilityConfiguration) |
| UPDM-SYS-005 | must | At compliance level 1, a UML element to which Node is applied must also have the SysML Block applied. | 8.3 (Node) |
| UPDM-SYS-006 | must | At compliance level 1, a UML element to which System is applied must also have the SysML Block applied. | 8.3 (System) |
| UPDM-SYS-007 | must | At compliance level 1, a UML element to which Energy is applied must also have the SysML Block applied. | 8.3 (Energy) |
| UPDM-SYS-008 | must | At compliance level 1, a UML element to which ResourceArtifact is applied must also have the SysML Block applied. | 8.3 (ResourceArtifact) |
| UPDM-SYS-009 | must | At compliance level 1, a UML element to which Environment is applied must also have the SysML Block applied. | 8.3 (Environment) |
| UPDM-SYS-010 | must | At compliance level 1, a UML element to which ExternalType is applied must also have the SysML Block applied. | 8.3 (ExternalType) |
| UPDM-SYS-011 | must | At compliance level 1, a UML element to which Capability is applied must also have the SysML Block applied. | 8.3 (Capability) |
| UPDM-SYS-012 | must | At compliance level 1, a UML element to which ExchangeElement is applied must also have the SysML Block applied. | 8.3 (ExchangeElement) |
| UPDM-SYS-013 | must | At compliance level 1, a UML element to which LogicalArchitecture is applied must also have the SysML Block applied. | 8.3 (LogicalArchitecture) |
| UPDM-SYS-014 | must | At compliance level 1, a UML element to which Materiel is applied must also have the SysML Block applied. | 8.3 (Materiel) |
| UPDM-SYS-015 | must | At compliance level 1, a UML element to which Organization is applied must also have the SysML Block applied. | 8.3 (Organization) |
| UPDM-SYS-016 | must | At compliance level 1, a UML element to which OrganizationType is applied must also have the SysML Block applied. | 8.3 (OrganizationType) |
| UPDM-SYS-017 | must | At compliance level 1, a UML element to which Performer is applied must also have the SysML Block applied. | 8.3 (Performer) |
| UPDM-SYS-018 | must | At compliance level 1, a UML element to which PersonType is applied must also have the SysML Block applied. | 8.3 (PersonType) |
| UPDM-SYS-019 | must | At compliance level 1, a UML element to which PhysicalArchitecture is applied must also have the SysML Block applied. | 8.3 (PhysicalArchitecture) |
| UPDM-SYS-020 | must | At compliance level 1, a UML element to which Post is applied must also have the SysML Block applied. | 8.3 (Post) |
| UPDM-SYS-021 | must | At compliance level 1, a UML element to which SecurityDomain is applied must also have the SysML Block applied. (The standard writes the SecurityDomain constraint against Node; read as SecurityDomain.) | 8.3 (SecurityDomain) |
| UPDM-SYS-022 | must | At compliance level 1, a UML element to which ServiceAccess is applied must also have the SysML Block applied. | 8.3 (ServiceAccess) |
| UPDM-SYS-023 | must | At compliance level 1, a UML element to which Responsibility is applied must also have the SysML Block applied. | 8.3 (Responsibility) |
| UPDM-SYS-024 | must | At compliance level 1, a UML element to which RoleType is applied must also have the SysML Block applied. | 8.3 (RoleType) |
| UPDM-SYS-025 | must | At compliance level 1, a UML element to which LightCondition is applied must also have the SysML ValueType applied. | 8.3 (LightCondition) |
| UPDM-SYS-026 | must | At compliance level 1, a UML element to which LocationType is applied must also have the SysML ValueType applied. | 8.3 (LocationType) |
| UPDM-SYS-027 | must | At compliance level 1, a UML element to which Climate is applied must also have the SysML ValueType applied. | 8.3 (Climate) |
| UPDM-SYS-028 | must | At compliance level 1, a UML element to which MeasurementSet is applied must also have the SysML ValueType applied. | 8.3 (MeasurementSet) |
| UPDM-SYS-029 | must | At compliance level 1, a UML element to which Condition is applied must also have the SysML ValueType applied. | 8.3 (Condition) |
| UPDM-SYS-030 | must | At compliance level 1, a UML element to which GeoPoliticalExtentType is applied must also have the SysML ValueType applied. | 8.3 (GeoPoliticalExtentType) |
| UPDM-SYS-031 | must | At compliance level 1, a UML element to which SecurityAttributesGroup is applied must also have the SysML ValueType applied. | 8.3 (SecurityAttributesGroup) |
| UPDM-SYS-032 | must | At compliance level 1, a UML element to which MeasureType is applied must also have the SysML ValueType applied. | 8.3 (MeasureType) |
| UPDM-SYS-033 | must | At compliance level 1, a UML element to which OperationalExchange is applied must also have the SysML ItemFlow applied. | 8.3 (OperationalExchange) |
| UPDM-SYS-034 | must | At compliance level 1, a UML element to which ResourceInteraction is applied must also have the SysML ItemFlow applied. | 8.3 (ResourceInteraction) |
| UPDM-SYS-035 | must | At compliance level 1, a UML element to which Control is applied must also have the SysML ItemFlow applied. | 8.3 (Control) |
| UPDM-SYS-036 | must | At compliance level 1, a UML element to which Command is applied must also have the SysML ItemFlow applied. (The standard names this element Commands.) | 8.3 (Command) |
| UPDM-SYS-037 | must | At compliance level 1, a UML element to which NodePort is applied must also have the SysML FlowPort applied. | 8.3 (NodePort) |
| UPDM-SYS-038 | must | At compliance level 1, a UML element to which ResourcePort is applied must also have the SysML FlowPort applied. | 8.3 (ResourcePort) |
| UPDM-SYS-039 | must | At compliance level 1, a UML element to which EnterpriseGoal is applied must also have the SysML Requirement applied. | 8.3 (EnterpriseGoal) |

## VIEW: Views and ordering

| Id | Strength | Rule | Section |
|---|---|---|---|
| UPDM-VIEW-001 | should | An enterprise has many architectural descriptions, each with its own operational, systems, standards and all views, but only one strategic view exists across them. | 8.3.1.1.6 |
| UPDM-VIEW-002 | should | The All views should be populated whenever an architecture is created or modified, because they carry the information needed to find and reuse the model. | 8.3.1.1.2 |
| UPDM-VIEW-003 | note | A pure operational view is independent of materiel; where needed, it may carry high-level systems data as overlays. | 8.3.1.1.4 |
| UPDM-VIEW-004 | note | The Operational View of MODAF corresponds to the logical architecture of the enterprise. | B.2.3 |
| UPDM-VIEW-005 | note | MODAF divides OV-4 into a typical form (the possible relationships between organizational resources, the same as the DoDAF OV-4) and an actual form (a special form of SV-1 whose resources are restricted to organizational ones). | B.2.3.4; B.2.3.5 |
| UPDM-VIEW-006 | note | Four project milestones have an implied order that the framework does not enforce and the architect must keep: an IncrementMilestone, then a DeployedMilestone, then a NoLongerUsedMilestone, then an OutOfServiceMilestone. | B.2.1.2 |
| UPDM-VIEW-007 | should | An IncrementMilestone should have a date that precedes all the other milestones for the same uniquely identifiable system resource. | B.2.1.2 |
| UPDM-VIEW-008 | should | A DeployedMilestone should have a date after the IncrementMilestone of the same system resource and should associate that resource with a specific organization. | B.2.1.2 |
| UPDM-VIEW-009 | should | A NoLongerUsedMilestone should have a date after the DeployedMilestone for the same system resource and organization, and should not exist without that DeployedMilestone. | B.2.1.2 |
| UPDM-VIEW-010 | should | An OutOfServiceMilestone should have a date at or after the latest NoLongerUsedMilestone for the system resource, and requires that no organization still has the resource deployed; if the resource was never deployed it should fall after the IncrementMilestone. | B.2.1.2 |
| UPDM-VIEW-011 | note | Capabilities are timeless and are not related to time directly. Time is related through an IncrementMilestone tied to a CapabilityConfiguration that exhibits the capability. A configuration that later realizes a different capability should be a new configuration, treated as a version of a master configuration. | B.2.5.4 |
| UPDM-VIEW-012 | note | An ArbitraryConnector is a visual indication in a high-level operational concept and cannot be related to any architectural semantics. | 8.3.1.1.4.4 |
| UPDM-VIEW-013 | note | A standards view covers one time period; emerging standards for a future period are shown in a standards forecast. A standards view references elements from the systems views (SV-1, 2, 4, 6), the service views (SvcV-1, 2, 4, 6) and the data views (DIV-2, DIV-3). | 8.3.1.1.8 |
| UPDM-VIEW-014 | note | The DoDAF and MODAF service concepts differ: MODAF services are specifications, DoDAF services describe implementations in particular performers. The mapping between the service views of the two is partial. | C.3.2 |

## GUID: Guidance

| Id | Strength | Rule | Section |
|---|---|---|---|
| UPDM-GUID-001 | note | Stakeholders of an architecture include end users and tool vendors; the specification is organized around the metamodels, not the views, while still supporting the more than 50 views that can be derived and user-defined views. | 6.2 |
| UPDM-GUID-002 | note | NAF is supported implicitly through the convergence of MODAF and NAF; the annex maps NAF 3.1 and MODAF views and elements. | 1; C.2 |
| UPDM-GUID-003 | note | UPDM was developed model-first: the domain metamodel was mapped to profile elements, with each profile element linked to its metamodel element, and the specification generated from the profile. | 7.2 |
