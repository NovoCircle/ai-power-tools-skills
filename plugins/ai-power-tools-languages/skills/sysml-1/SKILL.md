---
name: sysml-1
description: The OMG Systems Modeling Language (SysML) 1.5, a UML profile for systems engineering and model-based systems engineering (MBSE). Covers blocks and value types, parts, references and value properties, ports (proxy and full) and item flows, constraint blocks and parametric models, requirements and their relationships (satisfy, verify, refine, trace, derive, copy, containment), allocation, views and viewpoints, and the nine diagram types (requirement, block definition, internal block, parametric, package, activity, sequence, state machine, use case). Use when someone is modeling a system, system decomposition, interfaces, requirements traceability or verification, performance analysis or allocation of function to structure with SysML, or asks what SysML, a block definition diagram, an internal block diagram, a parametric diagram or a requirement diagram allows.
---

# OMG Systems Modeling Language (SysML) 1.5

SysML is the Object Management Group's general-purpose modeling language for systems engineering. It is a **profile of UML 2.5**: it reuses a subset of UML and adds a few concepts, notations and three small libraries. The version described here is 1.5 (May 2017). Later versions exist (1.6 in 2019, 1.7 in 2024, and a new language, SysML v2, in 2025) and are not described.

A separate UML skill describes the UML concepts SysML reuses (classes, properties, ports, connectors, associations, activities, interactions, state machines, use cases, packages, profiles). This skill names those concepts where SysML uses them and describes only what SysML adds, restricts or leaves out.

## What you are creating

A SysML model describes a system (and, if you wish, its environment, its requirements and the engineering analyses of it) as:

1. **Requirements**: what the system must do, with their traceability to design and to verification.
2. **Structure**: blocks (types of system or system element), the parts they are made of, the values they carry, and how parts are connected and what flows between them.
3. **Behavior**: activities, interactions, state machines and use cases that say what the structure does.
4. **Constraints and analysis**: reusable constraints (equations, rules) bound to properties of the structure.
5. **Cross-cutting mappings**: allocation of function to structure, and views for stakeholders.

Everything that can appear in any diagram is an element of one model; diagrams show parts of it.

## The nine diagram types and what each admits

Every SysML diagram has a **frame** naming the model element it belongs to (rules SYSML-DIAG-001 to -011). Names in capitals are concepts in `language.yaml`.

| Diagram (abbreviation) | Frame element | What it admits |
|---|---|---|
| **Requirement** (req) | a package or a requirement | Only requirements, packages, other classifiers, test cases and rationale, with containment, derive, satisfy, verify, refine, copy and trace. Callouts show other elements' relationships to a requirement. |
| **Block definition** (bdd) | a block, constraint block or package | Blocks, interface blocks, constraint blocks, value types, enumerations, actors, units and quantity kinds; packages; associations (part, shared, reference), generalization, dependencies, item flows; ports, flow properties and directed features in compartments. Activities, interactions and state machines appear as blocks. |
| **Internal block** (ibd) | a block | The properties of the framed block (part, reference, value, constraint and port), connectors, binding connectors, item flows, initial values, provided and required interfaces, allocation and requirement callouts. |
| **Parametric** (par) | a block | Constraint properties with their parameters, and the properties of the context block bound to them, joined by **binding connectors only**. |
| **Package** (pkg) | a package or model | Packages and models with containment, import and access; views, viewpoints, stakeholders, element groups, rationale and problems; dependencies, conform and expose; also profile definitions and model libraries. |
| **Activity** (act) | an activity | UML activity nodes and edges, partitions, regions, plus control operators, rates, probabilities, buffering and optional parameters; allocation partitions. |
| **Sequence** (sd) | an interaction | Lifelines, messages, execution specifications, interaction uses, combined fragments, constraints and observations. |
| **State machine** (stm) | a state machine | States, regions, pseudostates, transitions, entry and exit points. Behavior state machines only. |
| **Use case** (uc) | a package | Use cases, actors, subject, communication, include, extend, generalization. |

Package, sequence, state machine and use case diagrams are UML diagrams reused unchanged; block definition, internal block and activity diagrams are UML diagrams with SysML changes; requirement and parametric diagrams are new. SysML has **no** object, communication, interaction overview, timing, deployment, component or profile diagram. Tables and matrices (for example an allocation table or a requirements table) are allowed notations but are not diagrams in this taxonomy.

## Concepts, grouped

Definitions are in `language.yaml`; the groups below are the ones the standard uses.

- **Blocks and properties.** A **Block** is the modular unit of system description. Its properties are classified as **part properties** (typed by a block, composite), **reference properties** (typed by a block, not composite), **value properties** (typed by a value type) and **constraint properties** (typed by a constraint block). Supporting concepts: **BindingConnector** (equal values or same instance at both ends), **AssociationBlock**, **ParticipantProperty**, **ConnectorProperty**, **AdjunctProperty**, **ClassifierBehaviorProperty**, **BoundReference** and **EndPathMultiplicity**, **NestedConnectorEnd**, **PropertySpecificType**, **DistributedProperty**.
- **Value types and units.** A **ValueType** types values that cannot be referenced; it may carry a **Unit** and a **QuantityKind**. The primitive value types are Boolean, Number (abstract), Integer, Real, Complex and String.
- **Ports and flows.** **ProxyPort** (exposes features of the owner or its parts, typed by an **InterfaceBlock**), **FullPort** (a separate element with its own features), **FlowProperty** (what can flow in, out or inout), **DirectedFeature** (provided, required or both), **ItemFlow** (what does flow on a connector or association), nested-port actions and triggers, change structural feature events.
- **Constraint blocks.** A **ConstraintBlock** packages a constraint and its parameters for reuse; a **ConstraintProperty** is a usage.
- **Activity extensions.** **ControlOperator** and **ControlValue** (control as data), **Rate** with **Continuous** and **Discrete**, **Probability**, **NoBuffer**, **Overwrite**, **Optional**.
- **Requirements.** **Requirement** (with a text and an id), **TestCase**, and the relationships **Satisfy**, **Verify**, **DeriveReqt**, **Refine**, **Trace**, **Copy**; **AbstractRequirement** is the abstract base.
- **Allocation.** **Allocate** and **AllocateActivityPartition**.
- **Model management.** **View**, **Viewpoint**, **Stakeholder**, **Conform**, **Expose**, **ElementGroup**, **Rationale**, **Problem**.
- **Deprecated.** **FlowPort** and **FlowSpecification**: use proxy ports typed by interface blocks that own flow properties instead.

## Relationship rules, in summary

The standard has no table of allowed pairs; each relationship's ends are stated with it. Dependencies run from **client** (arrow tail) to **supplier** (arrowhead).

- **Satisfy** and **Verify**: any named element to a requirement (or a specialization). A design element satisfies; a test case, or any element that can decide it, verifies.
- **DeriveReqt** and **Copy**: requirement to requirement. For derive the client is the derived requirement; for copy the client is the slave whose text is a read-only copy of the supplier (master).
- **Refine** and **Trace**: any named element to any named element, one client and one supplier. A requirement is typically the supplier of refine; trace is weak and best not mixed with the others.
- **Containment of requirements** is nesting: a compound requirement contains its sub-requirements, and only requirements nest in a requirement.
- **Allocate**: any named element to any named element, one client (from) and one supplier (to). Typical uses: behavior to structure, flow to flow, structure to structure.
- **Associations between blocks** are part (black diamond), shared (white diamond) or reference. Connectors have exactly two ends and join properties and ports. An item flow needs a connector or association between its source and target.
- **Conform**: a view to the one viewpoint it conforms to. **Expose**: a view to the elements where its query starts.
- The use case relationships are communication (actor and use case), include, extend and generalization; transitions join states and pseudostates; messages join lifelines.

## The rules that matter most

All 225 rules, with ids, are in `references/rules.md`. The ones to keep in front of you:

- **A requirement is a leaf of its own kind.** It owns no operations or attributes, takes part in no association or generalization, types nothing, and only requirements nest inside it. Every requirement has a text and a unique id. (SYSML-REQ-001 to -007)
- **Satisfy and verify point at a requirement.** Their supplier is a requirement; derive and copy have requirement kinds at both ends. (SYSML-REQ-009 to -013, -016, -019)
- **A copy's text is a read-only copy of its master's.** (SYSML-REQ-010, -011)
- **Blocks:** an association between two blocks has exactly two ends; a connector has exactly two ends; a value-typed property is composite; composite properties of an instance form no cycle; anything that specializes a block is a block. (SYSML-BLK-001 to -007)
- **Ports:** a port is never both proxy and full. A proxy port is typed by an interface block, and an interface block has no behaviors and no non-port composite properties. A full port is neither behavioral nor conjugated. (SYSML-PORT-001 to -011)
- **Flows:** a flow property is typed by a value type, block or signal; item flows need a connector or association between source and target and must fit the flow properties at both ends. (SYSML-FLOW-001, -010 to -016)
- **Constraint blocks** own only parameters, nested constraint properties, binding connectors between them and the constraint text; a property typed by a constraint block is composite; on a parametric diagram everything shown is bound, directly or through containment, to a parameter, and only binding connectors appear. (SYSML-CNS-001 to -005, SYSML-DIAG-014, -015)
- **Frames:** each diagram kind belongs to a particular kind of element (the table above). (SYSML-DIAG-003 to -011)
- **Not in SysML:** package merge, n-ary and qualified associations, components, nodes and deployments, communication, timing and interaction overview diagrams, protocol state machines. (SYSML-CONF-001 to -005, SYSML-BEH-001, -002)
- **Flow ports and flow specifications are deprecated.** They sit outside conformance; prefer proxy ports. (SYSML-DEP-001 to -008)

## Telling similar concepts apart

- **Part, reference or value property.** A part is a composite usage of a block; a reference points at something owned elsewhere; a value holds a value-typed quantity. The type and the aggregation decide.
- **Flow property or item flow.** A flow property says what *can* flow in or out of a block; an item flow says what *does* flow on one connector in one context. Item flows must be compatible with the flow properties at both ends.
- **Proxy or full port.** A proxy port is a window onto the owner or its parts and has no behavior of its own; a full port is a separate element with its own behavior and features.
- **Block or constraint block.** A block describes a system element; a constraint block owns only a constraint and its parameters and is used by binding them to properties.
- **Satisfy, verify, refine, derive.** Satisfy: the design that fulfills a requirement. Verify: the test or analysis that shows it is fulfilled. Refine: a more detailed element that elaborates it. Derive: a lower-level requirement that follows from it.
- **Allocate or satisfy.** Allocation maps one model structure onto another at an abstract level (function to component); satisfy ties a design element to a requirement.
- **Include or extend.** Include inserts required common behavior into a use case; extend adds optional behavior at a named point under a condition. The standard says the choice is often subjective.

## A short example

This is an illustration with a fictitious organization. Use your own system, elements and naming. Nothing here assumes you have any particular model.

Westbrook Bank plans a new automated teller. Its engineers write a **requirement** "Withdrawal response time" with id "WB-R1" and the text "A cash withdrawal completes within 8 seconds of card validation." A **block definition diagram** defines the block *AutomatedTeller* with parts *cardReader*, *controller* and *cashDispenser*, each typed by its own block, and a value property *responseTime* typed by the value type *Duration*, which carries the unit second. The *cashDispenser* block has a **proxy port** *cashOut*, typed by an interface block that declares a flow property *banknotes* out. An **internal block diagram** of *AutomatedTeller* connects *controller* to *cashDispenser* with a connector and an item flow *banknotes*.

A **constraint block** *ResponseBudget* declares the constraint "total = t1 + t2 + t3" with four parameters. On a **parametric diagram** framed by *AutomatedTeller*, a constraint property of that type is bound by binding connectors to *responseTime* and to the response times of the three parts. A **test case** *MeasureWithdrawalTime* (a behavior returning a verdict) **verifies** the requirement; the block *AutomatedTeller* **satisfies** it; the activity "Dispense banknotes" is **allocated** to *cashDispenser*.

Rules at work: the requirement has no attributes and no associations (SYSML-REQ-001 to -003); the value property is composite (SYSML-BLK-005); the proxy port is typed by an interface block (SYSML-PORT-002); the item flow needs the connector between its ends (SYSML-FLOW-010); only binding connectors appear on the parametric diagram (SYSML-DIAG-015); the allocation has one client and one supplier (SYSML-ALLOC-002).

## Data types and attributes

The standard defines types only in part (`data_types.coverage: partial`). SysML adds the **value type**, which can carry a **unit** and a **quantity kind**, and three small libraries: the primitive value types (Boolean, Integer, Real, String, Complex, and Number as the abstract parent of the numeric ones), the unit and quantity kind library, and the control values (`disable`, `enable`). It also has the enumerations FlowDirection (`in`, `out`, `inout`), FeatureDirection (`provided`, `required`, `providedRequired`) and VerdictKind (`pass`, `fail`, `inconclusive`, `error`). It states no number representation, no literal forms and no concrete units; other types come from UML (`inherits_from: uml-2`). Attributes sit on each concept entry under `attributes` for the concepts that have them (`some_concepts`; the Annex B diagram interchange elements are not listed). See `data_types` and the concept entries in `language.yaml`.

## How it is drawn

The standard gives a symbol for almost every element in its Diagram Elements tables (`notation.coverage: normative`). Every diagram has a **frame** (a rectangle with a name tag at the upper left reading `diagramKind [type] name [diagram name]`), and the nine kinds use the abbreviations act, bdd, ibd, par, pkg, req, sd, stm and uc. The ones to know: a **block** is a box with the keyword «block» and optional compartments; a **part** is a solid box and a **reference** a dashed box on an internal block diagram; a **port** is a small square on the owner's border (with «proxy» or «full»); an **item flow** is a black triangle on a connector; a **constraint property** is a rounded box; and the requirement relationships (satisfy, verify, derive, refine, trace, copy, allocate) are dashed lines with an open arrowhead, labeled with their keyword. Package, sequence, state machine and use case diagrams use UML's notation unchanged, and a few elements have no drawing (listed under `not_specified`). See `notation` in `language.yaml`, which also lists every keyword.

Sizes and spacing come from `../_languages/layout-standard.yaml`; which element type each concept takes is in `layout` in `language.yaml`.

## References

- `references/standard.md`: the standard section by section, in our own words, with clause citations.
- `references/rules.md`: all 225 rules with stable ids (`SYSML-<CAT>-nnn`), strength, checkability and source section.
- `language.yaml`: the machine-readable form: the 86 concepts SysML defines, the 93 UML concepts it reuses, the 35 relationships, the UML subset, the nine diagram types, the data types, the notation and the rules.
