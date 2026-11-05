# ArchiMate 3.1 rules

Generated from `language.yaml` (`constraints`). Do not edit by hand; change the language file and regenerate.

Each rule has a stable id of the form `ARCHIMATE-<CAT>-nnn`. The number never changes once assigned. A rule that is retired keeps its id and is marked withdrawn rather than reused.

## Strength

| Strength | Meaning | Treatment |
|---|---|---|
| must | The standard states it as a requirement ("shall", "must", "only", "cannot"). A model that breaks it is not well formed. | An error. |
| should | The standard gives it as guidance or as a definition stated only in prose. Breaking it is a finding to review, not a malformation. | A warning. |
| note | The standard states it as an explanation, an option or a method note. It is recorded for completeness and is not checkable on its own. | Advice only. |

Where a cardinality appears only in the standard's prose (a collaboration has two or more members, a gap is associated with two plateaus), the rule is graded `should`, not `must`.

## Categories

| Category | Name | Covers | Rules |
|---|---|---|---|
| REL | Relationship use | Which relationships may join which concepts, and how each type is used. | 14 |
| JCT | Junctions | How the and/or junction connector may be used. | 4 |
| DER | Derivation | How relationships may be derived from chains, and where derivation stops. | 8 |
| ELM | Element definitions | Rules that follow from what a concept is defined to be. | 9 |
| CMP | Composites | Grouping, location, product, plateau and gap. | 7 |
| CRS | Cross-domain use | How motivation, strategy, the core layers and implementation and migration connect. | 4 |
| NAM | Naming guidance | How element names should be worded. Advisory. | 4 |
| LNG | Language, notation and customization | Conformance, notation cues, deprecated constructs and the extension mechanisms. | 7 |
| VPT | Viewpoints | How a viewpoint is formed and what every viewpoint may additionally show. | 3 |

Section references are to the clauses and appendices of the ArchiMate 3.1 specification. The allowed-relationship table is data in `language.yaml` (`relationships.allowed`), not restated here; rule ARCHIMATE-REL-003 is the rule that uses it.

## REL: Relationship use

| Id | Strength | Rule | Section |
|---|---|---|---|
| ARCHIMATE-REL-001 | must | Every relationship has exactly one source and one target. Each may be an element, a relationship or a junction. | 5 |
| ARCHIMATE-REL-002 | must | No relationship may join two relationships. | 5; B.6 |
| ARCHIMATE-REL-003 | must | A relationship between two elements is allowed only if the allowed-relationship table lists its type for that source and target pair. A pair outside the table is an error. A pair inside the table is permitted, never evidence that the relationship is correct, because the table includes derivations the standard says may be wrong in a given model. | 5.7; 1.3; B.3; B.5 |
| ARCHIMATE-REL-004 | must | Association is always allowed between any two elements, and between any element and a relationship. | 5; 5.2.4 |
| ARCHIMATE-REL-005 | must | Composition, aggregation and specialization are always allowed between two elements of the same type. | 5; 5.1.1; 5.1.2; 5.4.1 |
| ARCHIMATE-REL-006 | must | A relationship that joins an element to another relationship can only be aggregation, composition or association. Aggregation or composition into a relationship is allowed only from a composite element (grouping, location or plateau); every other element may only associate with it. | 5; B.6 |
| ARCHIMATE-REL-007 | must | Within a layer, composition and aggregation are permitted among processes, functions and interactions, so a process can be composed of other processes, functions and interactions. | 4.2 |
| ARCHIMATE-REL-008 | must | The source of a structural relationship is always an element. For assignment and realization the source may also be a junction. The target may in some cases be a relationship or a junction. | 5.1 |
| ARCHIMATE-REL-009 | must | Assignment is allowed only where the relationship table gives it. In the table it chiefly joins active structure to behavior and active structure to active structure (for example an actor to a role), and technology and physical active structure to artifacts and materials (deployment and storage); it has no assignment from behavior to passive structure. The prose of 5.1.3 describes the direction more loosely; where the two disagree the table governs. | 5.1.3; B.5 |
| ARCHIMATE-REL-010 | must | Access is read at the metamodel level from the active structure or behavior element to the passive structure element, whatever the arrowhead shows. The target of access is a passive structure element: in the table, Artifact, Business Object, Contract, Data Object, Deliverable, Material, Representation, or a Grouping. | 5.2.2; B.4; B.5 |
| ARCHIMATE-REL-011 | should | Use realization for a critical contribution and influence for a non-critical one. | 5.1.4; 5.2.3 |
| ARCHIMATE-REL-012 | should | Give a name or label to any relationship that would otherwise be ambiguous. | 5 |
| ARCHIMATE-REL-013 | note | The sign and strength of an influence relationship are left to the modeler; the default is a contribution of unspecified sign and strength. | 5.2.3 |
| ARCHIMATE-REL-014 | note | Structural relationships and triggering apply to the unmodeled parts of the source: a relationship from a part also applies to the whole. Dependency and flow relationships relate a part of the target to a part of the source, so a high-level dependency does not imply the same dependency for every part. | 5.1.5; 5.2.5; 5.3.3 |

## JCT: Junctions

| Id | Strength | Rule | Section |
|---|---|---|---|
| ARCHIMATE-JCT-001 | must | All relationships joined to one junction are of the same type. | 5; 5.5.1 |
| ARCHIMATE-JCT-002 | must | A junction can be used with access, assignment, flow, influence, association, realization, triggering and serving. It cannot be used with composition, aggregation or specialization. | 5.5.1; B.6 |
| ARCHIMATE-JCT-003 | must | A chain of same-type relationships through junctions is valid only if a direct relationship of that type between the two end elements would be valid. | 5; 5.5.1 |
| ARCHIMATE-JCT-004 | note | A junction may have several incoming and one outgoing relationship, one incoming and several outgoing, or several of both. Arrowheads into a junction may be omitted. An or junction covers both inclusive and exclusive or. A junction has no formal execution semantics. | 5.5.1 |

## DER: Derivation

| Id | Strength | Rule | Section |
|---|---|---|---|
| ARCHIMATE-DER-001 | note | Derivation goes from more detail to less detail. It cannot add detail. A derived relationship is valid but is not drawn in the metamodel figures. | 5.7 |
| ARCHIMATE-DER-002 | note | A modeler may draw a relationship that is a valid derivation without modeling the relationships it was derived from. | 5.7 |
| ARCHIMATE-DER-003 | must | The relationships a derivation starts from must themselves be allowed by the table. Derivation does not apply to relationships that involve a grouping. Between core elements and motivation, strategy or implementation and migration elements, only realization and influence can be derived. | B.1 |
| ARCHIMATE-DER-004 | must | Across domains, derivation is limited. From implementation and migration, core or strategy elements to a motivation element only realization or influence can be derived, and nothing the other way. From core or implementation and migration elements to a strategy element only realization, and nothing the other way. From an implementation and migration element to a core element only realization, and nothing the other way. Nothing is derivable between two domains through an intermediary in a third. | B.4 |
| ARCHIMATE-DER-005 | must | Access from a to b can be derived only if b is a passive structure element. For a passive structure target only access or assignment can be derived; from a passive structure source only realization or influence. | B.4 |
| ARCHIMATE-DER-006 | must | Relationships allowed from a concept to itself are also allowed among that concept, its specializations, and sibling specializations (for example a node and a facility). | B.4 |
| ARCHIMATE-DER-007 | must | The derivation restrictions apply only to derived relationships. A relationship drawn in a metamodel figure is allowed by definition. Product and plateau can aggregate or compose only the concepts shown in their metamodel fragments. | B.4 |
| ARCHIMATE-DER-008 | should | Potential derivations (PDR 1 to 11) may be wrong in a given model and must be checked by the modeler before they are used. | B.3 |

## ELM: Element definitions

| Id | Strength | Rule | Section |
|---|---|---|---|
| ARCHIMATE-ELM-001 | should | A collaboration aggregates two or more internal active structure elements. Application and technology collaborations may also aggregate other collaborations of the same kind. | 4.2; 8.2.3; 9.2.2; 10.2.4 |
| ARCHIMATE-ELM-002 | should | An interaction is collective behavior performed by two or more internal active structure elements, assigned directly or aggregated in a collaboration. | 4.2 |
| ARCHIMATE-ELM-003 | note | A business collaboration need not be a permanent organizational unit. | 8.2.3 |
| ARCHIMATE-ELM-004 | must | The abstract concepts (the generic structure, behavior and passive structure concepts, and the layer-level internal active structure, internal behavior and passive structure concepts) are not instantiated in models. Only their specializations are. | 3.2; 8.1 |
| ARCHIMATE-ELM-005 | must | A contract is a specialization of a business object. | 8.4.2 |
| ARCHIMATE-ELM-006 | must | A constraint is a kind of requirement. | 4.4; 6.3.5 |
| ARCHIMATE-ELM-007 | note | An event may carry a time attribute. | 4.1.2; 13.2.3 |
| ARCHIMATE-ELM-008 | note | A work package has a clearly defined start and end date. An implementation event is instantaneous. | 13.2.1; 13.2.3 |
| ARCHIMATE-ELM-009 | note | At the architecture level the language models types, not instances. | 3.6 |

## CMP: Composites

| Id | Strength | Rule | Section |
|---|---|---|---|
| ARCHIMATE-CMP-001 | must | A grouping is joined to each of its members by aggregation or composition. A grouping may also have other relationships with any element that can be the other end, and with another grouping. | 4.5.1; B.6 |
| ARCHIMATE-CMP-002 | note | A relationship from or to a grouping reads as a collective relationship with the grouping's contents. This is not always expressible as simple derivable relationships. | 4.5.1 |
| ARCHIMATE-CMP-003 | should | Do not use a grouping where a view is meant; a grouping is a model element, not a view. | 4.5.1 |
| ARCHIMATE-CMP-004 | should | Show a location with aggregation from the location to the structure elements located there, or to the behavior performed there. | 4.5.2 |
| ARCHIMATE-CMP-005 | must | A product aggregates or composes services and passive structure elements across layers, and only the concepts shown in its metamodel fragment. | 8.5.1; B.4 |
| ARCHIMATE-CMP-006 | note | A plateau may aggregate or compose any core concept and may realize part of the architecture. | 13.4 |
| ARCHIMATE-CMP-007 | should | A gap is associated with two plateaus and with the core concepts that exist in only one of them. | 13.2.5; 13.4 |

## CRS: Cross-domain use

| Id | Strength | Rule | Section |
|---|---|---|---|
| ARCHIMATE-CRS-001 | must | A requirement (and, by derivation, a principle, outcome or goal) can be related to structure or behavior elements by realization. Influence is allowed as the weaker relationship. | 6.6 |
| ARCHIMATE-CRS-002 | must | Strategy elements: internal and external behavior elements realize capabilities and value streams; structure elements realize resources; capabilities, value streams, courses of action and resources may realize or influence requirements; a course of action may realize or influence an outcome. | 7.6 |
| ARCHIMATE-CRS-003 | note | Cross-layer relationships are typically serving (for example application service to business behavior, application interface to business role) and realization (for example data object or technology object to business object, artifact to application component). These are typical examples, not the only permitted ones; the table governs. | 12.1; 12.2 |
| ARCHIMATE-CRS-004 | note | Business internal active structure elements may be assigned to a stakeholder or to a work package. A deliverable may realize core concepts. Meaning and value can be associated with any concept. | 6.4.1; 6.4.2; 6.6; 13.4 |

## NAM: Naming guidance

| Id | Strength | Rule | Section |
|---|---|---|---|
| ARCHIMATE-NAM-001 | should | Name stakeholders, drivers, resources, equipment, facilities, materials and the objects of each layer (business objects, data objects, technology objects) with nouns. | 6.2.1; 6.2.2; 7.2.1; 8.4.1; 9.4.1; 10.4; 11.2 |
| ARCHIMATE-NAM-002 | should | Name an assessment with a noun or a very short sentence, a meaning with a noun or noun phrase, and express a functional value as an action or a state. | 6.2.3; 6.4.1; 6.4.2 |
| ARCHIMATE-NAM-003 | should | Name a capability with a compound noun or gerund ("what we do") and a value stream with a verb-noun phrase in the active. | 7.3.1; 7.3.2 |
| ARCHIMATE-NAM-004 | should | Name an outcome so that it identifies an end result at a definite future point, an implementation event with a verb in the perfect tense, and a facility with a noun that names its type. | 6.3.2; 13.2.3; 11.2.2 |

## LNG: Language, notation and customization

| Id | Strength | Rule | Section |
|---|---|---|---|
| ARCHIMATE-LNG-001 | note | A conforming tool supports the language structure, generic metamodel, relationships, layers and cross-layer dependencies (chapters 3 to 13), the standard iconography, the viewpoint mechanism, the customization mechanisms and Appendix B. It may support the Appendix C viewpoints. This rule is about tools, not about models. | 1.3 |
| ARCHIMATE-LNG-002 | should | Prefer the standard iconography wherever possible, so that any ArchiMate reader can read any diagram. | 3.7 |
| ARCHIMATE-LNG-003 | note | Colors carry no formal meaning. The layer colors, the layer letters (M, S, B, A, T, P, I) and the corner-shape conventions are notational cues. | 3.9 |
| ARCHIMATE-LNG-004 | note | Nesting one element in another may express some structural relationships, but it is ambiguous when several relationships are allowed between the two elements. | 3.8; 5.1 |
| ARCHIMATE-LNG-005 | must | A specialized concept inherits the allowed relationships of its parent and keeps its parent's definition. Relationships may be specialized too. | 15.2 |
| ARCHIMATE-LNG-006 | should | Deprecated or removed constructs: "used by" (renamed serving), the two-ended black-ball notation for assignment, and the required-interface notation (abolished in 3.0). Do not use them in new models. | 5.2.1; 5.1.3; E.1 |
| ARCHIMATE-LNG-007 | note | The standard defines no mandatory attributes. Attributes and profiles are optional and are the customization mechanism of chapter 15. The exchange schema adds three optional properties: an access type on access, a modifier on influence and a directed flag on association. | 15; 15.1 |

## VPT: Viewpoints

| Id | Strength | Rule | Section |
|---|---|---|---|
| ARCHIMATE-VPT-001 | note | A viewpoint is created by selecting the subset of metamodel concepts (elements and relationships) needed for its concerns, then defining a representation: a diagram, a catalog, a matrix or another visualization. A view need not be visual. | 14.4 |
| ARCHIMATE-VPT-002 | note | In every viewpoint, in addition to the elements it specifies, a grouping, a junction and an or junction may be used. | C |
| ARCHIMATE-VPT-003 | note | The example viewpoints of Appendix C are not a normative or exhaustive list. A conforming tool may support them. | C.1; 1.3 |
