# ArchiMate 3.1, chapter by chapter

This is a summary of The Open Group's ArchiMate 3.1 Specification in our own words. It is not a substitute for the specification and does not reproduce its text; the few short quoted phrases are cited. Section numbers are the 3.1 edition's. Where the standard is silent, or states something two ways, this file says so rather than filling the gap.

Source: The Open Group, *ArchiMate 3.1 Specification*, document C197, 2019 (copyright 2012 to 2019), published 5 November 2019. The online edition requires an account, so the pages were read from archived copies, together with the open 3.1 model exchange schema, which lists the element and relationship types. The specification's relationship tables (Appendix B.5) are images; the table in `language.yaml` is a third-party capture, described in section 17 below. Figures are images too and were not read, so the generalization hierarchy is partly reconstructed (section 16).

## 1. What the standard is (chapter 1, front matter)

**Nature.** ArchiMate is a visual modeling language for describing enterprise architecture. It offers default iconography, a metamodel, derivation rules, a viewpoint mechanism and customization mechanisms. It separates concepts from notation (3.7).

**Normative parts.** The language structure, generic metamodel, relationships, layers and cross-layer dependencies (chapters 3 to 13), the viewpoint mechanism (14), the customization mechanisms (15, implementation-defined) and Appendix B (relationships) are normative. Appendix A (notation summary), D (other standards) and E (changes) are informative. Appendix C's example viewpoints are described as examples, "not a normative or exhaustive list" (C.1).

**Conformance (1.3).** A conforming tool supports the language structure and all layers, the standard iconography, the viewpoint mechanism, the customization mechanisms and the relationship rules of Appendix B. It may support the Appendix C viewpoints.

**Terminology (1.5).** "Shall" is a requirement, "should" a recommendation, "may" an option; "deprecated" and "obsolescent" mark constructs that later versions remove or discourage.

## 2. Language structure (chapter 3)

A model is a collection of concepts; a concept is an element or a relationship; an element is a behavior, structure, motivation or composite element (3.2). These generic types are abstract and not used directly in models.

**Layers and aspects (3.3 to 3.5).** Three core layers, business, application and technology (physical elements belong with technology), are crossed with three aspects: active structure, behavior and passive structure. The full framework adds motivation (an aspect), strategy, and implementation and migration. The standard calls the classification "only a global one" (3.4): an element need not sit squarely in one cell.

**Types, not instances (3.6).** At the architecture level the language models types.

**Notation (3.7 to 3.9).** Prefer the standard iconography so any reader can read any diagram (3.7). Nesting can express some structural relationships but is ambiguous when several are allowed (3.8). Colors, layer letters and corner shapes are cues with no formal meaning (3.9).

## 3. Generic metamodel (chapter 4)

**Structure and behavior (4.1).** Structure elements are either active (can perform behavior) or passive (are acted on). Active structure splits into internal (an entity capable of behavior) and external (an interface: a point of access that exposes services). Behavior elements are internal (a unit of activity), external (a service, explicitly exposed behavior) or an event (a state change). Passive structure elements are often information or data and can be physical. An event may carry a time attribute (4.1.2).

**Collaboration and interaction (4.2).** A collaboration is an aggregate of two or more internal active structure elements working together. An interaction is collective behavior that must be performed by two or more such elements, assigned directly or aggregated in a collaboration. A process is a sequence of behaviors achieving a result; a function groups behavior by criteria such as resources, competencies or location. Within a layer, composition and aggregation are permitted among processes, functions and interactions.

**Motivation (4.4).** Motivation elements give the context or reason behind the architecture. A constraint is a subtype of requirement.

**Composites (4.5).** A grouping aggregates or composes concepts of any kind that share a characteristic; it is not a view, and derivation does not cover it (4.5.1). A relationship from or to a group reads as a collective relationship with its contents but is not always expressible as derivable relationships. A location is a place where structure is located or behavior performed, modeled by aggregation from the location (4.5.2).

## 4. Relationships (chapter 5)

Eleven types in four groups, plus the junction connector. Every relationship has exactly one source and one target, each an element, a relationship or a connector. No relationship may join two relationships; the one exception is that an element can connect to another relationship, and then only by aggregation, composition or association, aggregation and composition only from a composite element (5; B.6).

**Structural (5.1).**
- *Composition* (5.1.1): a whole consists of parts and they depend on it for existence. Always allowed between two elements of the same type.
- *Aggregation* (5.1.2): a whole combines parts without existence dependency. Always allowed between two elements of the same type.
- *Assignment* (5.1.3): allocation of responsibility, performance of behavior, storage or execution. The old notation with a ball at both ends is deprecated. The prose describes the direction as active structure to behavior, behavior to passive structure, or active to passive structure; the relationship table has no behavior-to-passive assignment (section 16).
- *Realization* (5.1.4): an entity plays a critical role in creating, achieving, sustaining or operating a more abstract entity. For non-critical contributions use influence.
- Structural relationships apply to unmodeled parts of the source: a relationship from a part also applies to the whole (5.1.5).

**Dependency (5.2).**
- *Serving* (5.2.1): an element provides its functionality to another. "Used by" is the deprecated earlier name.
- *Access* (5.2.2): behavior and active structure elements observe or act on passive structure. At the metamodel level the direction is always toward the passive element; the arrow in a drawing may show read access instead.
- *Influence* (5.2.3): an element affects the realization of a motivation element. The sign and strength are the modeler's.
- *Association* (5.2.4): an unspecified relationship, or one nothing else covers; undirected unless marked. Always allowed between any two elements, and between an element and a relationship.
- Dependencies relate a part of the target to a part of the source; a high-level dependency does not imply the same dependency for every part (5.2.5).

**Dynamic (5.3).** *Triggering* is a temporal or causal relationship; *flow* is a transfer (of information, goods, money) and does not imply causality. Triggering applies to unmodeled parts of the source like the structural relationships; flow relates parts like a dependency (5.3.3).

**Other (5.4).** *Specialization*: an element is a particular kind of another. Always allowed between two elements of the same type.

**Junction (5.5.1).** A relationship connector, not a relationship. It joins relationships of one type, in an and or an or variant. It can be used with access, assignment, flow, influence, association, realization, triggering and serving. A chain through junctions is valid only if a direct relationship of that type between the end elements would be valid. Several in with one out, one in with several out, and several of both are allowed; arrowheads into a junction may be omitted. The or junction covers inclusive and exclusive or, and the standard gives it no execution semantics.

**Derivation (5.7).** Relationships can be derived from chains. Derivation only goes from more detail to less. Derived relationships are valid but not drawn in the metamodel figures, and a modeler may draw one without modeling its constituents. The relationship tables show all permitted relationships between two elements, and a tool shall support them (5.7; 1.3).

## 5. Motivation (chapter 6)

Ten elements: stakeholder (6.2.1), driver (6.2.2, a driver tied to a stakeholder is a concern), assessment (6.2.3), goal (6.3.1), outcome (6.3.2), principle (6.3.3), requirement (6.3.4), constraint (6.3.5), meaning (6.4.1) and value (6.4.2). Meaning and value can be associated with any concept. A requirement, and by derivation a principle, outcome or goal, can be related to structure or behavior elements by realization, with influence as the weaker alternative (6.6). Business internal active structure elements may be assigned to a stakeholder.

## 6. Strategy (chapter 7)

Four elements: resource (7.2.1, structure that is neither active nor passive), capability (7.3.1), value stream (7.3.2, with stages joined by flow and served by capabilities) and course of action (7.3.3, of which strategies and tactics are categories, not separate concepts). Core behavior elements realize capabilities and value streams; structure elements realize resources; capabilities, value streams, courses of action and resources may realize or influence requirements; a course of action may realize or influence an outcome (7.6).

## 7. Business layer (chapter 8)

Thirteen elements. Active structure: business actor (8.2.1), role (8.2.2), collaboration (8.2.3) and interface (8.2.4). Behavior: process (8.3.1), function (8.3.2), interaction (8.3.3), event (8.3.4) and service (8.3.5). Passive structure: business object (8.4.1), contract (8.4.2, a specialization of business object), representation (8.4.3). Composite: product (8.5.1), which aggregates or composes services and passive structure elements across layers and only the concepts in its metamodel fragment. The business internal active structure, behavior and passive structure elements are abstract (8.1).

## 8. Application layer (chapter 9)

Nine elements. Active structure: application component (9.2.1), collaboration (9.2.2) and interface (9.2.3). Behavior: function (9.3.1), interaction (9.3.2), process (9.3.3), event (9.3.4) and service (9.3.5). Passive structure: data object (9.4.1), which may realize a business object and may be realized by an artifact. An application collaboration is a specialization of the application internal active structure element and may aggregate other collaborations.

## 9. Technology layer (chapter 10)

Thirteen elements. Active structure: node (10.2.1), device (10.2.2, a specialization of node in 3.1), system software (10.2.3, a specialization of node in 3.1), technology collaboration (10.2.4), interface (10.2.5), path (10.2.6) and communication network (10.2.7). Behavior: function (10.3.1), process (10.3.2), interaction (10.3.3), event (10.3.4) and service (10.3.5). Passive structure: artifact (10.4.1), a specialization of a "technology object", which the text names as the generic passive element of the layer but which is not an element type in the exchange schema.

## 10. Physical elements (chapter 11)

Four elements: equipment (11.2.1) and facility (11.2.2), both specializations of node in 3.1; distribution network (11.2.3), the physical realization of a path; and material (11.4.1), a special kind of technology object. There are no separate physical behavior elements; technology behavior models the behavior of all nodes, equipment included (11.3).

## 11. Cross-layer dependencies (chapter 12)

Between layers the typical relationships are serving (for example application service to business behavior, application interface to business role) and realization (for example data object or technology object to business object, artifact to application component). A product may aggregate application or technology services and data or technology objects (12.1, 12.2). These are typical cases; the relationship table is the authority.

## 12. Implementation and migration (chapter 13)

Five elements. Work package (13.2.1): a series of actions with a defined start and end, within time and resource limits. Deliverable (13.2.2): a defined result of a work package. Implementation event (13.2.3): an instantaneous state change, which may carry a time attribute. Plateau (13.2.4): a relatively stable state of the architecture during a limited period; it may aggregate or compose core concepts and may realize part of the architecture (13.4). Gap (13.2.5): the difference between two plateaus, associated with both and with the core concepts unique to one (13.4). A deliverable may realize core concepts; a business internal active structure element may be assigned to a work package.

## 13. Viewpoints (chapter 14 and Appendix C)

**Mechanism (chapter 14).** The mechanism follows ISO/IEC 42010: stakeholders, concerns, viewpoints and views (14.2). A view is what you see; a viewpoint prescribes the concepts, models, techniques and visualizations; a concern may be framed by several viewpoints (14.3). A viewpoint is classed by purpose (designing, deciding, informing) and by content (details: one layer and one aspect; coherence: several layers or aspects; overview: both) (14.4.1). Creating one means choosing the subset of metamodel concepts and defining a representation, which may be a diagram, catalog, matrix or other visualization (14.4). A view need not be visual (14.4.2).

**Example viewpoints (Appendix C).** Twenty-five are described in full, each with purpose, scope and the elements it admits (listed in `language.yaml`): thirteen basic (Organization, Application Structure, Information Structure, Technology, Layered, Physical, Product, Application Usage, Technology Usage, Business Process Cooperation, Application Cooperation, Service Realization, Implementation and Deployment); four motivation (Stakeholder, Goal Realization, Requirements Realization, Motivation); five strategy (Strategy, Capability Map, Value Stream, Outcome Realization, Resource Map); three implementation and migration (Project, Migration, Implementation and Migration). Table 21 classes the basic ones as composition, support, cooperation or realization viewpoints. In every viewpoint a grouping, junction and or junction may be used as well (C). Goal Contribution and Principles are named in the introduction to the motivation viewpoints with one-line descriptions but have no section or table in 3.1.

## 14. Customization (chapter 15)

Every concept can carry attributes (15). A profile is a separately defined set of typed attributes with defaults, coupled to elements or relationships; some are predefined, others user-defined (15.1). Specialization creates new element and relationship types; the specialized concept keeps the parent's definition and inherits its allowed relationships, notation may add an icon or an angle-bracket label, and several profiles may attach to one concept (15.2). The specification defines no mandatory attributes. The exchange schema adds an access type on access, a modifier on influence and a directed flag on association.

## 15. Derivation and relationship tables (Appendix B)

**Derivation rules (B.1, B.2).** Notation `p(a,b):R` names a path. Eight rules are valid: specialization is transitive (DR 1); two structural relationships in a chain reduce to the weaker (DR 2); structural then dependency yields the dependency (DR 3); structural and dependency with a shared target yield the dependency from the dependency's source to the structural source (DR 4); structural then dynamic yields the dynamic one (DR 5); flow can be moved across a structural relationship at its target (DR 6); triggering then structural yields triggering (DR 7); triggering is transitive (DR 8). Strength, weakest to strongest: structural, realization, assignment, aggregation, composition; dependency, association, influence, access, serving.

**Potential derivations (B.3).** Eleven further rules (PDR 1 to 11) may or may not hold in a given model and the modeler must check them.

**Restrictions (B.4).** Four domains: motivation, strategy, core (business, application, technology, physical, and the location element) and implementation and migration. From implementation and migration, core or strategy elements to a motivation element, only realization or influence can be derived, and nothing the other way. From core or implementation and migration elements to a strategy element only realization, nothing the other way. From an implementation and migration element to a core element only realization, nothing the other way. Nothing is derivable between two domains through an intermediary in a third. Access can be derived only if the target is passive structure; a passive target admits only access or assignment, and a passive source only realization or influence. Relationships allowed from a concept to itself are also allowed among it, its specializations and its sibling specializations. The restrictions apply only to derived relationships; relationships in the metamodel figures are allowed by definition. Derivation does not apply to groupings.

**Relationship tables (B.5).** The full allowed-relationship table: "From" across the top, "To" down the side, each cell holding the letters of the allowed types. The text says the tables contain all allowed relationships in the language and are built from the metamodel figures and the derivation rules. Letters: access (a), composition (c), flow (f), aggregation (g), assignment (i), influence (n), association (o), realization (r), specialization (s), triggering (t), serving (v).

**Grouping, plateau, relationships and connectors (B.6).** A small table and bullet rules: grouping and location may aggregate or compose any concept; a grouping may be the source of any relationship with any element that can be its target, and the target of any relationship from any element that can be its source; any relationship may be associated with any element; two relationships may not be joined. The junction rule is the one in section 4 above (letters a, f, i, n, o, r, t, v).

## 16. Gaps and ambiguities in the standard

1. **Generalization hierarchy.** Only a handful of generalizations are stated in the text (contract and business object, constraint and requirement, device and system software and node, equipment and facility and node, artifact and technology object, material and technology object, the application and technology collaborations). The rest are in figures that are images; `language.yaml` rebuilds them from headings and the exchange schema and marks each inferred. The parent of distribution network is not stated.
2. **Technology object.** Named in the text as a generic passive element but absent from the exchange schema. It is listed as abstract.
3. **Assignment direction.** 5.1.3 describes behavior to passive structure; the table has none, only technology and physical active structure to artifacts and materials (and to location and junction). The table is read.
4. **Relationships between relationships.** Chapter 5 says no relationship joins two relationships, while 5.2.4 allows association between a relationship and an element. B.6 resolves it: relationship to relationship is empty; element to relationship is association.
5. **Junction.** The standard has one connector with an and or an or variant; the exchange schema splits it in two. The standard's own rule is the single B.6 entry.
6. **Strategy elements.** The text calls resource a structure element "neither active nor passive" and the other three behavior elements.
7. **Goal Contribution and Principles.** Named but not specified.
8. **A permissive table.** B.5 includes potential derivations that B.3 says may be wrong, so the table is an upper bound on what is allowed, not a statement of what is correct.
9. **Qualitative guidance.** Naming guidance and the definitions of the qualitative elements are "should" statements and cannot be checked mechanically without a policy.

## 17. Provenance of the allowed table

The Appendix B.5 tables are images in the online edition and could not be read as text. The table in `language.yaml` is a third-party capture of the 3.1 relationship table (named in `standard.reference`), covering 62 concepts by 62: the 60 element concepts plus the junction and relationship pseudo-concepts, 3,841 non-empty cells. About 30 cells across three of the ten specification pages were compared with the images with no mismatch; the other seven pages were not compared. The capture's junction cells are element-specific and do not match the specification's single junction rule in every case; the rule governs. The newer 3.2 version of the same third-party table is a different table and must not be used for 3.1.

## 18. What changed from 3.0.1 and to 3.2

**3.0.1 to 3.1 (Appendix E.2).** Value stream added; an optional directed notation for association; derivation rules formalized, which removed a small number of spurious relationships (migrate by replacing such a relationship with a directed association).

**3.2 (published 19 October 2022).** No new element or relationship type. Device, system software, facility and equipment cease to be subtypes of node and become subtypes of a technology internal active structure element, with composition and aggregation to node. Composition and aggregation are added from plateau to outcome, and realization from material to equipment. Physical elements move into the technology layer chapter; derivation restrictions are reworded and a derivation rule for grouping added; several definitions improve and some notation changes.
