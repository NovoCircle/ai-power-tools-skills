# VDML 1.0 rules

Generated from `language.yaml` (`constraints`). Do not edit by hand; change the language file and regenerate.

Each rule has a stable id of the form `VDML-<CAT>-nnn`. The number never changes once assigned. A rule that is retired keeps its id and is marked withdrawn rather than reused.

## Strength

| Strength | Meaning |
|---|---|
| must | The standard states it as a requirement ("MUST", "MUST NOT", a stated constraint) or fixes it as a required multiplicity in its normative metamodel. A model that breaks it is not well formed. |
| should | The standard states it as guidance ("SHOULD NOT"), or states a principle without saying it is exclusive. Breaking it is a warning, not an error. |
| note | The standard states it as an expectation, an option, a scope statement or a method note. It is recorded for completeness and is advice. |

## Checkable

Each rule is marked `static` (decidable from the structure of the model), `partial` (decidable only where the needed measurements are present, or needing a walk across several elements), `runtime` (only decidable when the model is executed or simulated) or `none` (not a checkable condition). The mark is in `language.yaml`.

## Categories

| Category | Name | Covers | Rules |
|---|---|---|---|
| CONT | Containment and ownership | Which collaboration a role, activity, flow or assignment must belong to. | 8 |
| ROLE | Roles and assignments | Who may fill which role, and what may not be assigned to what. | 12 |
| FLOW | Flows, ports and delegations | How deliverable flows, ports, resource uses and port delegations may connect. | 21 |
| MEAS | Measurement and timing | Durations, units, and where measurements may sit. | 9 |
| VALUE | Values and value propositions | Rules on value propositions and on aggregating value elements. | 8 |
| CAP | Capabilities | Capability offers, methods and dependencies. | 9 |
| CTX | Scenarios and contexts | Scenarios, analysis contexts and delegation contexts. | 6 |
| LIB | Libraries | Definitions and categories must belong to the same library. | 9 |
| CARD | Required and bounded ends | Metamodel multiplicities that make a property mandatory or limit it to one. | 12 |
| DIAG | Diagram admission | What the standard's diagrams must or should not show. | 6 |
| CONF | Conformance and scope | Conformance points and statements about what VDML leaves out. Advice, not checkable. | 6 |

Section references are to the clauses of the VDML 1.0 specification (formal/2015-10-05) as numbered in the body of the document; "p." is the printed page number. The specification's table of contents numbers the class definitions differently from the body. "Machine-readable model" means the normative file vdml.xmi. Multiplicities on individual relationships are in `language.yaml` and are not repeated here.

## CONT: Containment and ownership

| Id | Strength | Rule | Section |
|---|---|---|---|
| VDML-CONT-001 | must | The Role that performs an Activity must be contained in the same Collaboration that contains the Activity. | 7.2.1.2.1, p. 34 |
| VDML-CONT-002 | must | Every Activity performed by a Role must be contained in the same Collaboration that contains the Role. | 7.2.1.1.5, p. 31 |
| VDML-CONT-003 | must | If an Assignment of a Role to a participant is contained in a Collaboration, that Collaboration must also contain the assigned Role. | 7.2.1.1.5, p. 31 |
| VDML-CONT-004 | must | A PortDelegation owned by a Collaboration must delegate a Port of that Collaboration to a Port of an Activity contained in that Collaboration. | 7.2.1.1.3, p. 30 |
| VDML-CONT-005 | must | An InputPort that provides the roleResource to which a Role is assigned must be contained by an Activity performed by that Role. | 7.2.1.1.5, p. 32 |
| VDML-CONT-006 | must | The Ports a Role refers to as ports it handles must be Ports of Stores. | 7.2.1.1.5, p. 32 |
| VDML-CONT-007 | must | A DeliverableFlow must not connect Ports of Activities that are contained in different Collaborations. | 7.2.1.2.4, p. 39 |
| VDML-CONT-008 | must | Only an OrgUnit owns Stores and Pools and provides CapabilityOffers. No other kind of Collaboration owns resources; a CapabilityMethod receives its resources from other sources while it performs its Activities. | 7.1.7, p. 16; 7.2.2.4.1, p. 51 |

## ROLE: Roles and assignments

| Id | Strength | Rule | Section |
|---|---|---|---|
| VDML-ROLE-001 | must | An Assignment must not assign a Role to both a Participant and a roleResource. | 7.2.1.2.3, p. 37 |
| VDML-ROLE-002 | must | A Role must not be assigned to more than one Participant that is a Collaboration, unless the additional Assignments are context-based (contained by a DelegationContext). | 7.2.1.2.3, p. 37 |
| VDML-ROLE-003 | must | A Role must not be assigned to itself, directly or through other Assignments. | 7.2.1.2.3, p. 37 |
| VDML-ROLE-004 | must | A Role must not be assigned to the Collaboration that contains it. | 7.2.1.2.3, p. 38 |
| VDML-ROLE-005 | must | A BusinessNetwork or a CapabilityMethod must not be a Participant in a Position (a Role in an OrgUnit) or in a Member (a Role in a Community). | 7.2.1.2.3, p. 38 |
| VDML-ROLE-006 | must | A BusinessNetwork must not be a Participant in a Performer (a Role in a CapabilityMethod). | 7.2.1.2.3, p. 38 |
| VDML-ROLE-007 | must | A BusinessNetwork has only Party roles (it may also contain nested BusinessNetworks). | 7.2.2.1.1, p. 47 |
| VDML-ROLE-008 | must | A Community has only Member roles. | 7.2.2.2, p. 47 |
| VDML-ROLE-009 | should | The roles of an OrgUnit are Positions, and the roles of a CapabilityMethod are Performers. The standard says an OrgUnit has Position roles and a CapabilityMethod has Performer roles but does not state that no other kind may occur. | 7.1.7, p. 16; 7.2.2.3, p. 49; 7.2.2.4.1, p. 52 |
| VDML-ROLE-010 | must | A Position associated with a Pool must not be assigned, directly or through other Roles, to a Collaboration. | 7.2.1.2.7, p. 42 |
| VDML-ROLE-011 | must | When an Activity has more than one InputPort that receives the roleResource for its performing Role, either the Activity has a ResourceUse relating to that set of InputPorts (making them alternatives), or every DelegationContext in which the containing Collaboration is used gives a contextBasedAssignment that assigns the Role to the resource received on one of them. | 7.2.1.2.1, p. 35 |
| VDML-ROLE-012 | note | Individual assignments of people to roles are not required in a VDML model; they would be modeled to support simulation. | 7.1.7, p. 16 |

## FLOW: Flows, ports and delegations

| Id | Strength | Rule | Section |
|---|---|---|---|
| VDML-FLOW-001 | must | A DeliverableFlow must connect Ports of two Activities, or a Port of an Activity with a Port of a Store. A flow between two Stores is not allowed. | 7.2.1.2.4, p. 39; 7.1.9, p. 20 |
| VDML-FLOW-002 | must | A DeliverableFlow that connects to a Port of a Store must not have a duration. | 7.2.1.2.4, p. 39 |
| VDML-FLOW-003 | must | The BusinessItem that a Store receives or provides through DeliverableFlows must be the same BusinessItem the Store holds as its resource. | 7.2.1.2.6, p. 41 |
| VDML-FLOW-004 | must | A PortContainer other than an Activity or a Collaboration that is a CapabilityMethod must not contain a Port with isIntermediate false. (Stores and Pools, and Collaborations that are not CapabilityMethods, use only intermediate ports.) | 7.2.4.3.1, p. 64 |
| VDML-FLOW-005 | must | A Port of a Collaboration must not have a planningPercentage. | 7.2.4.3.1, p. 64 |
| VDML-FLOW-006 | must | A Port of a Collaboration must not have a condition. | 7.2.4.3.1, p. 64 |
| VDML-FLOW-007 | must | A Port of a Collaboration must not have a batchSize. | 7.2.4.3.1, p. 64 |
| VDML-FLOW-008 | must | A Port of a Collaboration or of a Store must not have an offset. | 7.2.4.3.1, p. 64 |
| VDML-FLOW-009 | must | A Port that has an offset must be an intermediate Port (isIntermediate true). | 7.2.4.3.1, p. 64 |
| VDML-FLOW-010 | must | An intermediate Port of an Activity must have an offset. | 7.2.4.3.1, p. 64 |
| VDML-FLOW-011 | must | An InputDelegation must map an InputPort of an Activity to an InputPort of a Collaboration, or an InputPort of a Collaboration to an InputPort of an Activity contained in that Collaboration. | 7.2.4.4.2, p. 67 |
| VDML-FLOW-012 | must | An OutputDelegation must map an OutputPort of an Activity to an OutputPort of a Collaboration, or an OutputPort of a Collaboration to an OutputPort of an Activity contained in that Collaboration. | 7.2.4.4.3, p. 67 |
| VDML-FLOW-013 | must | An InputPort of an Activity contained in a Collaboration must not be mapped by InputDelegations to more than one InputPort of that containing Collaboration. | 7.2.4.4.2, p. 67 |
| VDML-FLOW-014 | must | An OutputPort of an Activity contained in a Collaboration must not be mapped by OutputDelegations to more than one OutputPort of that containing Collaboration. | 7.2.4.4.3, p. 67 |
| VDML-FLOW-015 | must | A Port that is not an InputPort of an Activity, and is not the recipient of a non-fungible BusinessItem from a Store, must not have a correlationExpression. | 7.2.4.3.3, p. 65 |
| VDML-FLOW-016 | must | A ResourceUse of an Activity must relate only to Ports of that Activity. | 7.2.1.2.1, p. 34 |
| VDML-FLOW-017 | must | A ResourceUse must not be defined for resources that are not received from Stores. | 7.2.1.2.2, p. 36 |
| VDML-FLOW-018 | must | An Activity must not have a recurrenceInterval when it receives inputs from anything other than Stores. | 7.2.1.2.1, p. 34 |
| VDML-FLOW-019 | must | A ResourceUse must not have a duration when its resource is consumed (resourceIsConsumed true), unless the ResourceUse also names its deliverable. | 7.2.1.2.2, p. 36 |
| VDML-FLOW-020 | note | A flow from one Activity to another means the receiving Activity needs that BusinessItem as input. Flows in an activity network always point toward completion of the result. | 7.1.9, p. 20 |
| VDML-FLOW-021 | note | Model only the resources that matter to a high-level analysis: parts of high value and machines that must be scheduled. Facilities, small parts, supplies and utilities are usually folded into capability overhead or activity cost. | 7.1.11, p. 21 |

## MEAS: Measurement and timing

| Id | Strength | Rule | Section |
|---|---|---|---|
| VDML-MEAS-001 | must | The duration of each ResourceUse of an Activity must not be longer than the duration of the Activity. | 7.2.1.2.1, p. 34 |
| VDML-MEAS-002 | must | The offset of a Port of an Activity must not be longer than the duration of the Activity. | 7.2.1.2.1, p. 34 |
| VDML-MEAS-003 | must | For each Port of an Activity, its offset plus the longest duration of a ResourceUse that relates to it must not be longer than the duration of the Activity. | 7.2.1.2.1, p. 34 |
| VDML-MEAS-004 | must | The unit of the Measure behind a planningPercentage (on a ResourceUse or a Port) must be percent. | 7.2.1.2.2, p. 36; 7.2.4.3.1, p. 64 |
| VDML-MEAS-005 | must | When a MeasuredCharacteristic has more than one Measurement, each Measurement must be in a separate Observation tied to a separate AnalysisContext. | 7.2.4.1.5, p. 61 |
| VDML-MEAS-006 | must | The inventoryLevel of a Pool must not be larger than the poolSize of that Pool. | 7.2.1.2.7, p. 42 |
| VDML-MEAS-007 | must | Measurements attach to VDML elements only through MeasuredCharacteristics; VDML narrows the SMM link between element and measurement to MeasuredCharacteristic. | 7.2.4.1, p. 59 |
| VDML-MEAS-008 | note | Measurements are statistical figures for a typical unit of production over a period (averages, possibly with variance), not measurements of one specific unit. Different units of production in related collaborations must be reconciled when combined. | 7.1.9, p. 20; 7.1.12, p. 22 |
| VDML-MEAS-009 | note | VDML defines no specific measures. Industry or professional measure libraries (SMM) are expected to supply them. | 1.1, p. 3; 7.1.12, p. 22 |

## VALUE: Values and value propositions

| Id | Strength | Rule | Section |
|---|---|---|---|
| VDML-VALUE-001 | must | The overallSatisfaction of a ValueProposition must be one of that ValueProposition's own components. | 7.2.1.3.1, p. 43 |
| VDML-VALUE-002 | must | The overallSatisfaction component of a ValueProposition must not itself have a percentageWeight. | 7.2.1.3.1, p. 43 |
| VDML-VALUE-003 | must | The provider of a ValueProposition must not be its recipient. | 7.2.1.3.1, p. 43 |
| VDML-VALUE-004 | must | The unit of the Measure behind the percentageWeight of a ValuePropositionComponent must be percent. | 7.2.1.3.2, p. 44 |
| VDML-VALUE-005 | must | When a ValueElement has no valueDefinition, its isAtomic must be empty. | 7.2.1.3.4, p. 46 |
| VDML-VALUE-006 | must | The valueDefinition of an atomic ValueElement (isAtomic true) must differ from the valueDefinition of each ValueElement it is aggregatedFrom. | 7.2.1.3.4, p. 46 |
| VDML-VALUE-007 | must | At least one of the aggregatedFrom ValueElements, among those that have a valueDefinition, of a non-atomic ValueElement (isAtomic false) must refer to the same ValueDefinition as that ValueElement. | 7.2.1.3.4, p. 46 |
| VDML-VALUE-008 | note | A ValueAdd belongs to an OutputPort. A ValueProposition represents the recipient's view and may be the modeling business's estimate of that view. A contribution may be positive or negative. | 7.1.2, p. 13; 7.2.1.3, p. 42 |

## CAP: Capabilities

| Id | Strength | Rule | Section |
|---|---|---|---|
| VDML-CAP-001 | must | When a CapabilityMethod supports more than one CapabilityOffer, possibly provided by different OrgUnits, those offers must be for the same Capability. | 7.2.2.4.1, p. 52 |
| VDML-CAP-002 | must | When a CapabilityMethod supports a CapabilityOffer and both refer to a Capability, they must refer to the same Capability. | 7.2.2.4.1, p. 52 |
| VDML-CAP-003 | must | A CapabilityDependency with an external source (isFromExternalSource true) must not have a source CapabilityDefinition connected. | 7.2.5.3.5, p. 77 |
| VDML-CAP-004 | must | A CapabilityDependency with an external target (isForExternalTarget true) must not have a target CapabilityDefinition connected. | 7.2.5.3.5, p. 77 |
| VDML-CAP-005 | should | The CapabilityOffer an Activity applies (appliedCapabilityOffer) should match the Capability the Activity requires (capabilityRequirement). | 7.2.1.2.1, p. 34 |
| VDML-CAP-006 | should | An Activity should not delegate directly to a CapabilityMethod. It engages the method through its OrgUnit, using a CapabilityOffer. | Annex A, Capability Method, p. 109 |
| VDML-CAP-007 | note | When a CapabilityOffer has no ReleaseControl, the assumed work-release strategy is first come, first served. | 7.2.2.3.4, p. 50 |
| VDML-CAP-008 | must | When an OrgUnit fills the Role that performs several Activities, the OrgUnit must have CapabilityOffers that support the Capability each of those Activities requires. | 7.1.8, p. 19 |
| VDML-CAP-009 | must | When a Role performs several Activities that require different Capabilities, the Participant that fills the Role must be able to provide each of those Capabilities. | 7.1.9, p. 19 |

## CTX: Scenarios and contexts

| Id | Strength | Rule | Section |
|---|---|---|---|
| VDML-CTX-001 | must | A ValueDeliveryModel must not have more than one common Scenario (isCommon true). | 7.2.3.1.1, p. 54 |
| VDML-CTX-002 | must | The common Scenario must not contain DelegationContexts and must not have contextStores, contextCollaborations or releaseControls. | 7.2.3.2.2, p. 58 |
| VDML-CTX-003 | must | A Scenario must not have more than one ReleaseControl for the same CapabilityOffer. | 7.2.3.2.2, p. 58 |
| VDML-CTX-004 | must | The DelegationContext in which an Activity delegates its work to a Collaboration must be owned by a DelegationContext in which the Activity's own Collaboration is used, or by a Scenario when that Collaboration is directly related to the Scenario. | 7.2.3.2.1, p. 57 |
| VDML-CTX-005 | must | When an Activity delegates its work in more than one DelegationContext, those DelegationContexts must be owned by different AnalysisContexts in which the Activity's own Collaboration is used. | 7.2.3.2.1, p. 57 |
| VDML-CTX-006 | must | A PortDelegation held by a DelegationContext must map Ports of that context's delegatedActivity to Ports of its contextCollaboration. | 7.2.3.2.3, p. 58 |

## LIB: Libraries

| Id | Strength | Rule | Section |
|---|---|---|---|
| VDML-LIB-001 | must | If a BusinessItemDefinition belongs to a BusinessItemCategory, the category must be contained in the same BusinessItemLibrary as the definition. | 7.2.5.1.2, p. 69 |
| VDML-LIB-002 | must | A BusinessItemCategory must be contained in the same BusinessItemLibrary as its parent and child categories. | 7.2.5.1.3, p. 70 |
| VDML-LIB-003 | must | If a ValueDefinition belongs to a ValueCategory, the category must belong to the same ValueLibrary as the definition. | 7.2.5.2.2, p. 71 |
| VDML-LIB-004 | must | A ValueCategory must be contained in the same ValueLibrary as its parent and child categories. | 7.2.5.2.3, p. 72 |
| VDML-LIB-005 | must | If a PracticeDefinition belongs to a PracticeCategory, the category must belong to the same PracticeLibrary as the definition. | 7.2.5.4.2, p. 78 |
| VDML-LIB-006 | must | A PracticeCategory must be contained in the same PracticeLibrary as its parent and child categories. | 7.2.5.4.3, p. 79 |
| VDML-LIB-007 | must | If a RoleDefinition belongs to a RoleCategory, the category must belong to the same RoleLibrary as the definition. | 7.2.5.5.2, p. 80 |
| VDML-LIB-008 | must | A RoleCategory must be contained in the same RoleLibrary as its parent and child categories. | 7.2.5.5.3, p. 81 |
| VDML-LIB-009 | note | Libraries keep names and definitions consistent across a model. Elements that refer to the same definition are treated as similar. Shared industry libraries with local extensions are expected. | 7.2.5, p. 67 |

## CARD: Required and bounded ends

| Id | Strength | Rule | Section |
|---|---|---|---|
| VDML-CARD-001 | must | Each contained element has exactly one container: a Role, Activity, DeliverableFlow, BusinessItem is in one Collaboration; a Position in one OrgUnit; a Party in one BusinessNetwork; a Member in one Community; a Performer in one CapabilityMethod; a Port in one PortContainer; a library entry in one library; a ValueAdd in one OutputPort; a ResourceUse in one Activity; a ValueProposition component in one ValueProposition; every library and Actor in one ValueDeliveryModel. | 7.2.1 to 7.2.5 (composition ends); machine-readable model |
| VDML-CARD-002 | must | An Activity and a Store each have exactly one duration, and a ResourceUse has exactly one quantity. | 7.2.1.2.1, p. 34; 7.2.1.2.7, p. 41; 7.2.1.2.2, p. 35 |
| VDML-CARD-003 | must | A DeliverableFlow has exactly one deliverable BusinessItem, one provider OutputPort and one recipient InputPort. An OutputPort provides at most one flow and an InputPort receives at most one flow. | 7.2.1.2.4, p. 38; 7.2.4.3.2, p. 64; 7.2.4.3.3, p. 65 |
| VDML-CARD-004 | must | An Assignment assigns exactly one Role and names at most one Participant. | 7.2.1.2.3, p. 37 |
| VDML-CARD-005 | must | A Store holds exactly one BusinessItem as its resource and has exactly one owning OrgUnit. | 7.2.1.2.7, p. 41 |
| VDML-CARD-006 | must | A CapabilityOffer has exactly one providing OrgUnit and a CapabilityMethod has exactly one owning OrgUnit. | 7.2.2.3.3, p. 50; 7.2.2.4.1, p. 52 |
| VDML-CARD-007 | must | A DelegationContext has exactly one parentContext, one contextCollaboration and one delegatedActivity. | 7.2.3.2.3, p. 58 |
| VDML-CARD-008 | must | A PortDelegation (InputDelegation or OutputDelegation) has exactly one source port and one target port. | 7.2.4.4.2, p. 67; 7.2.4.4.3, p. 67 |
| VDML-CARD-009 | must | A CapabilityDependency has exactly one deliverableDefinition (a BusinessItemDefinition). | 7.2.5.3.5, p. 76 |
| VDML-CARD-010 | must | A ValueDeliveryModel contains at least one Scenario. | 7.2.3.1.1, p. 54 |
| VDML-CARD-011 | must | These properties are required: the name and description of every element; the type of a Scenario; the strategy of a ReleaseControl; the tag and value of an Attribute; the text of an Annotation; the measuredCharacteristic of an Operand. The text of the standard does not state a multiplicity for name and description; the machine-readable model makes both required. | 7.2.4.1; machine-readable model |
| VDML-CARD-012 | must | An Activity has at most one performing Role, at most one capabilityRequirement and at most one appliedCapabilityOffer. A Port has at most one handler Role. A ValueProposition has at most one provider and one recipient. A Role has at most one RoleDefinition. A BusinessItem has at most one BusinessItemDefinition. | 7.2.1.2.1, p. 34; 7.2.4.3.1, p. 64; 7.2.1.3.1, p. 43; 7.2.1.1.5, p. 31; 7.2.1.2.5, p. 40 |

## DIAG: Diagram admission

| Id | Strength | Rule | Section |
|---|---|---|---|
| VDML-DIAG-001 | must | A Role Collaboration diagram must not show, as a connector, a DeliverableFlow that connects Activities performed by the same Role. | 8.2, p. 85 |
| VDML-DIAG-002 | must | A Role Collaboration diagram must not show, as a connector, a DeliverableFlow between an Activity performed by a Role and a Store port for which the same Role is the handler. Only transfers between different Roles are drawn. | 8.2, p. 85 |
| VDML-DIAG-003 | should | A Capability Management diagram should not show Positions that are associated with Pools inside the boundary of the OrgUnit; there may be many of them. | 8.8, p. 100 |
| VDML-DIAG-004 | note | A Capability Management diagram may show Positions that are not yet assigned to Participants inside the OrgUnit boundary. | 8.8, p. 100 |
| VDML-DIAG-005 | note | The Role Collaboration diagram and the Activity Network diagram can be synchronized views of the same Collaboration. | 8.4, p. 94 |
| VDML-DIAG-006 | note | Colors in the standard's example diagrams carry no meaning. The notation is limited and normative, and tabular displays are expected to complement the graphical ones. | 8.1, p. 83; 1.1, p. 3 |

## CONF: Conformance and scope

| Id | Strength | Rule | Section |
|---|---|---|---|
| VDML-CONF-001 | note | Full VDML conformance means supporting the normative graphical notation and importing and exporting models that follow the VDML metamodel and SMM. | 2.1, p. 3 |
| VDML-CONF-002 | note | VDML Metamodel conformance means importing and exporting XMI consistent with the VDML metamodel and SMM without implementing the notation. It is a subset of full conformance. | 2.2, p. 4 |
| VDML-CONF-003 | note | VDML Collaboration Modeling conformance covers 22 classes (ValueDeliveryModel, VdmlElement, MeasurableElement, Attribute, Annotation, MeasuredCharacteristic, PortContainer, Collaboration, Role, RoleDefinition, RoleLibrary, RoleCategory, Participant, Actor, Person, Assignment, OrgUnit, Position, Community, Member, BusinessNetwork, Party). Associations to other classes allow multiplicity zero and may be ignored. | 2.3, pp. 4-5 |
| VDML-CONF-004 | note | Simulation is not part of VDML 1.0. Optional simulation extensions (CalendarService, Pool and BusinessItem attributes, ReleaseControl, offsets, recurrence interval) are normative but not required for compliance. | 7.1, p. 12 |
| VDML-CONF-005 | note | VDML models the work of transformation and compares current and future state as scenarios, but it cannot model the transition itself. | 7.1.14, p. 26 |
| VDML-CONF-006 | note | When models are integrated, each library (capability, business item, value, role) of the result must be a superset of the corresponding libraries of the models being integrated, the organization structure must be reconciled so overlapping OrgUnits are merged, and delegated flows, business items and value adds must be reconciled. | 7.1.15, p. 27 |
