# OMG Systems Modeling Language (SysML) 1.5: the standard in our own words

Source: OMG SysML 1.5, formal/17-05-01 (May 2017), https://www.omg.org/spec/SysML/1.5/ , with the normative machine-readable model (`SysML.xmi`, ptc/16-12-10) and, for Annex B, `SysMLDI.xmi` (ptc/16-12-11). Section numbers are the standard's own. Short phrases in quotation marks are under 15 words. The rules are in `rules.md`; the concepts, relationships and diagram kinds are in `language.yaml`.

SysML is a **profile of UML 2.5**. It reuses a subset of UML (called UML4SysML) and adds its own concepts, notations and three small model libraries. This reference names the UML concepts SysML reuses and points to the UML language skill for them; it describes only what SysML adds or changes.

---

## 1. Scope and purpose (clauses 1, 3)

SysML is a general-purpose modeling language for systems engineering. It supports specification, analysis, design, verification and validation of systems that may include hardware, software, information, processes, people and facilities. It is meant to be learned by systems engineers and implemented by tool vendors, and to be customized for domains such as automotive, aerospace and communications. It is "particularly effective" for requirements, structure, behavior, allocations and constraints on system properties for engineering analysis (clause 1). Because it builds on UML 2.5, systems engineers and software engineers can share models of software-intensive systems (clause 1).

SysML supports no particular method. A method may add constraints on how a construct or diagram kind is used (clause 1).

## 2. Language architecture (clause 4)

- **Reuse.** SysML reuses a subset of UML (UML4SysML). Table 4.1 lists the UML metaclasses excluded (for example components, nodes, deployments, collaborations, templates, protocol state machines, expansion regions, and the UML diagram-interchange classes); Table 4.2 lists those included. A UML construct is part of the subset only if it appears in a SysML diagram elements table or in a normative usage example (6.2.2).
- **Extensions.** SysML extends UML through the profile mechanism, plus diagram extensions (new or changed notation) and model libraries. The extensions are packaged as Model Elements, Blocks, Constraint Blocks, Ports and Flows, Activities, Allocations, Requirements, and Deprecated Elements (4.3). Trace and Refine from UML's standard profile are the basis of requirement traceability.
- **Design principles.** Requirements driven (by the OMG's UML for Systems Engineering request for proposal), reuse of UML, extension only where needed, partitioning by package, layering on the UML metamodel, and interoperability by XMI and by ISO 10303-233 (4.2).
- **Libraries.** Three normative model libraries: PrimitiveValueTypes (8.3.3.1), UnitAndQuantityKind (8.3.3.2) and ControlValues (11.3.3). Unqualified Boolean, Integer, Real and String mean the UML primitive types when used to define a SysML extension and the PrimitiveValueTypes value types everywhere else (4.3).
- **Diagrams.** Nine diagram kinds (4.5, Annex A); see section 16 below.

## 3. Conformance (clause 5)

An implementation conforms only if it supports all three types together: abstract syntax (create, read, update and delete instances of the SysML extensions and library elements, and validate well-formedness against the SysML constraints), concrete syntax (the notation in the Diagram Elements tables and diagram extension sub clauses; extra notation is allowed), and model interchange (XMI for every valid SysML model). Conformance does not include the deprecated elements (5.1, 5.2).

## 4. Language formalism (clause 6)

SysML is specified by UML modeling techniques plus precise natural language. Each clause has an Overview, Diagram Elements (concrete syntax and abstract syntax references), UML Extensions (diagram extensions, and semantic extensions with their constraints) and Usage Examples. Each constraint is text and may be followed by OCL; the OCL takes precedence if they disagree (6.2.3). Boolean metaattributes start with "is"; enumeration types end with "Kind"; no visibilities are drawn because all elements are public (6.3).

## 5. Model elements (clause 7)

- **Package diagram.** A package diagram organizes the model into packages with import and access relationships. Models, packages, comments, constraints, dependencies (including realization and refine) and the model management elements below can appear on any diagram kind (7.2).
- **Comment kinds.** A *rationale* records the justification for a decision and attaches to any element, including a relationship (7.3.2.5). A *problem* records a deficiency or failure of elements to satisfy a need (7.3.2.4). An *element group* collects possibly unlike elements by annotation, with a criterion; it owns nothing, and an element may be in many groups (7.3.2.2).
- **Views and viewpoints** (ISO 42010). A *viewpoint* states the stakeholders, purpose, concerns, languages, method and presentation rules for a kind of view; it has at least one operation called View. A *view* stands for an artifact presented to stakeholders and conforms to exactly one viewpoint (the conform relationship, a generalization from view to viewpoint). A view exposes (the expose dependency) the model elements where its query begins. A *stakeholder* has concerns (7.1.1, 7.3.2).
- **Not included.** Package merge between user packages is not supported (7.3.1.1).

## 6. Blocks (clause 8)

- **Block.** A *block* (UML class with an extension) is a modular unit that describes a system or any element of interest, with structural and behavioral features: properties, operations, receptions, connectors, behaviors. Blocks form trees of components; they can describe logical or physical decomposition, hardware, software or people (8.1, 8.3.2.4).
- **Properties.** Four classifications: a *part property* (typed by a block, composite), a *reference property* (typed by a block, not composite), a *value property* (typed by a value type, always composite), and a *constraint property* (typed by a constraint block, composite; clause 10). A port is a further category of property (clause 9). A property is a role or usage in its enclosing block; the same block can be used in several roles with different values. An instance of a block belongs to at most one whole at a time (8.1, 8.3.2.4).
- **Associations.** A part association has a black diamond, a shared association a white diamond (no specific semantics), a reference association none. SysML equates navigation with ownership by a block; the only association end an association may own is an unnamed end that carries an inverse multiplicity. N-ary and qualified associations, arrowheads on both ends, non-navigability crosses and ownership dots are not included (8.3.1.3, 8.3.2.4).
- **Connectors.** A block has an internal structure of connectors between its properties; a connector has exactly two ends, may be typed by an association (or an association block), may cross nested property boundaries (nested connector end) and may have a path of properties at each end. A connector structurally links properties and behaviorally carries communication and item flow, together or apart (8.3.2.4, 8.3.2.12).
- **Binding connector.** A connector that says the two ends hold equal values or refer to the same block instance; its ends have the same or compatible types (8.3.2.3).
- **Association block.** A block applied to an association class: its instances link the ends, it may own properties and connectors, and it can type connectors to reuse the same structure. Participant properties identify the objects at each end; connector properties hold the instances created by a connector (8.3.2.7, 8.3.2.13).
- **Property paths and bound references.** A multi-level path of properties lets directed relationships, connector ends and other elements reach nested properties (8.3.2.8, 8.3.2.10). A *bound reference* marks a property bound by a binding connector so that it constrains nested properties; its type and multiplicity constrain the values reached by the binding path, and an *end path multiplicity* constrains how many values are reached at the end of the path for each object on it (8.3.2.5, 8.3.2.11).
- **Adjunct and classifier behavior properties.** An *adjunct property* has the values of a principal element (a connector, call action, object node, variable, parameter, interaction use or submachine state). A *classifier behavior property* has the executions of a block's classifier behavior (8.3.2.2, 8.3.2.6).
- **Property-specific type.** A type name in square brackets says a property has a local specialization of that type, owned by the block that owns the property, with additions or redefinitions; the classifier is unnamed and the type of exactly one property (8.3.2.14).
- **Distributed property.** A property to which a probability distribution is applied (8.3.2.9).
- **Initial values.** Context-specific values for nested properties are shown in an initial values compartment of an internal block diagram and are stored as an instance value that refers to an unnamed instance specification (8.3.1.2.8, 8.3.2.4).
- **Encapsulation.** A block with isEncapsulated true is a black box: parts typed by it connect only through ports or to their outer boundary (8.3.2.4).
- **Value types and units.** A *value type* (UML data type with an extension) defines values that cannot be the target of a reference. It may carry a *unit* and a *quantity kind*. A *quantity kind* is a kind of quantity that can be stated in defined units; a *unit* is a quantity in terms of which other quantities of the same kind are stated. Both are non-abstract library blocks; an instance specification classified by one defines a particular unit or kind of quantity, identified by its definition URI. A value type can state a quantity kind without a unit (8.3.2.15, 8.3.3.2). The PrimitiveValueTypes library has Boolean, Complex (real and imaginary parts), Integer, Number (abstract), Real and String (8.3.3.1).

## 7. Ports and flows (clause 9)

- **Ports** are points at which external entities connect to and interact with a block in ways that differ from, or are more limited than, connecting to the block itself. SysML extends UML ports to nest: a port typed by a block that has ports has nested ports (9.1).
- **Proxy port.** Exposes features of the owning block or of its internal parts through external connectors; it is not a separate element, it is typed by an *interface block*, and its nested ports are also proxy ports. **Full port.** A separate element of the system with its own features, parts and behaviors; not behavioral, not conjugated. A port that is neither is simply a port. A port is never both proxy and full (9.1.3, 9.3.2.8, 9.3.2.12).
- **Interface block.** A block with no behaviors and no internal parts other than ports, whose ports are typed only by interface blocks (9.3.2.9).
- **Flow property.** One kind of item (data, material, energy) that can flow in, out or in and out of a block; typed by a value type, block or signal. A conjugated port reverses direction. Flow occurs between matching flow properties: direction and type match, names match if several remain (9.3.2.7).
- **Provided and required features.** An operation, reception or non-flow property of a block can be marked *provided* (the block supports it), *required* (other blocks must support it for this block), or both. Invocation or access across a connector occurs when a provided feature matches the required one by kind, names, directions, types, multiplicities, order, uniqueness and conditions (9.3.2.4).
- **Item flow.** What does flow between usages across a connector or association, as against what can flow (flow properties). It is compatible with the flow properties at each end, and may name an item property that holds the flowing values (9.3.2.11).
- **Nested port support.** Actions and triggers can name a port reached by a path of nested ports; change structural feature events model changes in the values of a structural feature and have a matching accept-event action (9.3.2.1, 9.3.2.3, 9.3.2.10, 9.3.2.13).
- **Deprecation.** Flow ports and flow specifications are deprecated; see section 17.

## 8. Constraint blocks (clause 10)

A *constraint block* is a block that packages a constraint (an expression such as F = m * a) together with its parameters so it can be reused to constrain properties of other blocks. A *constraint property* is a usage of a constraint block inside another block. Constraint blocks can be nested. A *parametric diagram*, a restricted internal block diagram, shows constraint properties and the properties they constrain, joined by binding connectors. SysML does not prescribe a language for the expression; constraints are non-causal and the interpretation must be supplied. Constraint blocks can support trade-off analysis (an objective function; Annex E, non-normative) (10.1, 10.2, 10.3, 10.4).

## 9. Activities (clause 11)

SysML reuses UML activities and adds:

- **Control as data.** A *control operator* behavior takes and returns *control values* (enable, disable) so it can disable actions that are already executing, not only start them (11.1.1, 11.3.2.2, 11.3.3).
- **Continuous systems.** *Rate* (items per time interval) on edges and streaming parameters, with *continuous* and *discrete* specializations; *no buffer* and *overwrite* on object nodes (11.1.2, 11.3.2).
- **Probability** on edges leaving decision nodes or object nodes and on output parameter sets; values between zero and one that sum to one (11.1.3, 11.3.2.7).
- **Optional** parameters (lower multiplicity zero) (11.3.2.6).
- **Activities as blocks.** Activities, like all UML behaviors, are classes whose instances are executions. On a block definition diagram an activity appears as a block with the activity keyword; composition between activities means ending the whole ends the parts' executions; adjunct properties tie the part ends to call actions and object nodes to their types (11.1.4, 11.3.1.1).
- **Timelines.** The UML simple time model (time and duration constraints) is used; the UML timing diagram is not included (11.1.5).

## 10. Interactions, state machines and use cases (clauses 12 to 14)

- **Interactions.** Only the sequence diagram is kept, with the full set of UML interaction operators. Communication, interaction overview and timing diagrams are excluded as redundant or immature. Interactions appear as blocks on block definition diagrams (12.1, 12.3).
- **State machines.** The UML behavior state machine is kept (states with entry, do and exit activities; composite states with sequential or concurrent regions; the pseudostates; transitions). Protocol state machines are excluded (13.1).
- **Use cases.** The UML use case diagram is kept unchanged: use cases, actors, the subject (system boundary), communication paths, include, extend (with condition and extension points) and generalization (14.1, 14.3). Use cases are realized by activity, sequence and state machine diagrams (14.1).

## 11. Allocations (clause 15)

*Allocation* is the cross-association of elements in different structures or hierarchies of a model, at an abstract and sometimes tentative level; a precursor to concrete relationships. The *allocate* relationship is a directed relationship (an abstraction) between any two named elements, with exactly one client (from) and one supplier (to). Typical uses: behavior to structure (activities to blocks, actions to parts), flow to flow (object flow to connector or item flow, object node to flow property), structure to structure (abstract to concrete). An *allocate activity partition* depicts the allocation on an activity diagram (15.1, 15.3.2). Allocations can be shown in compartments, callouts, tables and matrices (15.2, 15.4.3). Pin-to-port allocation and control flow allocation are not specifically addressed (15.3.2.1).

## 12. Requirements (clause 16)

- A *requirement* (a UML class with an extension, and a kind of abstract requirement) specifies a capability or condition that must (or should) be satisfied. It has a text and a unique id; users may add properties such as verification status or risk. It owns no operations or attributes, takes part in no association or generalization, and types nothing (16.3.2.1, 16.3.2.5).
- **Compound requirements.** A requirement can contain nested requirements (UML nested classifiers) forming a hierarchy; by default all sub-requirements must be satisfied for the compound requirement to be satisfied (16.1, 16.3.2.5).
- **Relationships between requirements and other elements** (16.1, 16.3.2): *derive* (a derived requirement to its source), *satisfy* (a design element to the requirement it fulfills), *verify* (a test case or other element to the requirement it can verify), *refine* (an element that refines a requirement, or the reverse), *trace* (a general weak link, not recommended with the others), *copy* (a slave requirement whose text is a read-only copy of a master requirement, for reuse). Satisfy, verify, derive and copy are specializations of trace in the machine-readable model.
- A *test case* is a behavior or operation whose return parameter is a verdict (pass, fail, inconclusive, error), consistent with the UML testing profile (16.3.2.6).
- A rationale can be attached to a requirement or to any of these relationships (16.1).
- **Requirement diagram** shows requirements, packages, other classifiers, test cases and rationale, with the relationships; a requirements table shows properties and relationships in columns or as a sparse matrix (16.3.1).
- Requirement kinds (functional, interface, performance, physical, design constraint) are a non-normative example (Annex E.3).

## 13. Profiles and model libraries (clause 17)

This clause explains the UML profile mechanism SysML uses: a profile extends metaclasses with new elements that carry properties and constraints, is applied to a package (strictly, if only the metaclasses the profile references are to be used), and can be extended further by users. A *model library* is a package of reusable model elements. Notations show applied extensions as keywords and attribute values in the element, a note or a compartment. Guidance (17.4.4): a profile extension suits a concept that is not class-based, whose properties reference other model elements, or which describes modeling data rather than system data; a subclass suits properties with a separate value for each instance that subclasses inherit. SysML has no profile diagram; profile definitions are drawn on package diagrams.

## 14. Diagrams (Annex A, informative; clause 4.5)

Nine diagram kinds: activity (act), block definition (bdd), internal block (ibd), package (pkg), parametric (par), requirement (req), sequence (sd), state machine (stm), use case (uc).

| Kind | Basis | Frame element | Short purpose |
|---|---|---|---|
| Requirement | new | package or requirement | text requirements and their relationships to other elements |
| Block definition | modified UML class diagram | block, constraint block or package | definition of blocks, value types and their relationships |
| Internal block | modified UML composite structure diagram | block or constraint block | internal structure: parts, ports, connectors, flows |
| Parametric | new; restricted internal block diagram | block or constraint block | constraint properties bound to properties of the context |
| Package | UML package diagram | package or model | organization of the model; views; profile definitions |
| Activity | modified UML activity diagram | activity | flow of control and data among actions |
| Sequence | UML sequence diagram | interaction | message exchange between lifelines |
| State machine | UML state machine diagram | state machine | states and transitions |
| Use case | UML use case diagram | package | usage of a subject by actors |

Every diagram has a frame (required in SysML), a heading `<diagramKind> [modelElementType] <modelElementName> [diagramName]` and a contents area. Diagrams may mix kinds of element carefully (for example a state machine nested in a block compartment) but the kinds of element on a diagram kind must stay constrained and well specified. Callouts and compartments carry requirements and allocations onto diagrams of other kinds. Tables, matrices, graphs and trees are optional alternative notations outside the taxonomy. A *diagram usage* (a context diagram, a block hierarchy) is a constrained use of a diagram kind. Annex B (informative) defines a diagram-interchange model for SysML diagrams: an element per diagram kind, the default namespace, the dashed-control-flow flag and the rounded-constraint-property flag.

## 15. Non-normative extensions (Annex E)

Optional extensions not part of the standard proper: enhanced functional flow block diagrams (EFFBD), streaming and non-streaming activities; requirement kinds with source, risk and verification method (analysis, demonstration, inspection, test); an objective function and measure of effectiveness for trade studies; QUDV (a fuller model of quantities, units, dimensions and values); a model library of ISO 80000 units and quantity kinds; probability distributions; and property-based requirements. They are not concepts of this language file.

## 16. Sample problem (Annex D, informative) and traceability (Annex F)

The hybrid sport-utility vehicle sample problem applies the nine diagram kinds to one system; it is the standard's worked example. Annex F records how the SysML requirements in the request for proposal are met. Neither was summarized here.

## 17. Deprecated elements (Annex C, normative)

*Flow ports* and *flow specifications* are deprecated and kept for backward compatibility; they are excluded from conformance. A flow port is an interaction point through which items flow; atomic (typed by one block, value type or signal) or non-atomic (typed by a flow specification, which lists flow properties only). Guidelines convert a flow port to a proxy port typed by an interface block that owns the flow properties, to a full port, or to a plain port. The old view and viewpoint model and the old unit and quantity kind model were not deprecated but changed in later versions, with transition guidelines (C.4 to C.6).

## 18. Newer versions

SysML 1.6 (December 2019), 1.7 (June 2024) and SysML v2 (September 2025) exist. This reference describes 1.5 only. See `language.yaml` for the list.
