# SysML 1.5 rules

Generated from `language.yaml` (`constraints`). Do not edit by hand; change the language file and regenerate.

Each rule has a stable id of the form `SYSML-<CAT>-nnn`. The number never changes once assigned. A rule that is retired keeps its id and is marked withdrawn rather than reused.

## Strength

| Strength | Meaning |
|---|---|
| must | The standard states it as a numbered constraint, as "shall" or "shall not", or in OCL. A model that breaks it is not well formed. Reported as an error. |
| should | The standard gives it as a recommendation ("should", "recommended", "typically"). Reported as a warning. |
| note | The standard states it as a description, an expectation, a semantic explanation or the removal of a UML rule. Advice only; not reported on its own. |

## Checkable

| Value | Meaning |
|---|---|
| static | A check that sees only the saved model can decide it. |
| partial | Only the structure or simple cases can be checked; the rest needs judgment or a model of behavior. |
| runtime | Needs instances or an executing model. |
| none | Not a property of a model (guidance, definition or a rule about a tool). |

## Categories

| Category | Name | Covers | Rules |
|---|---|---|---|
| MOD | Model management | Views, viewpoints, stakeholders, element groups, rationale and problems (clause 7). | 11 |
| BLK | Blocks and properties | Blocks, the four kinds of property, connectors, property paths, adjunct and bound properties, association blocks (clause 8). | 60 |
| VAL | Value types and units | Value types, units, quantity kinds and the primitive value type library (8.3.2.15, 8.3.3). | 8 |
| PORT | Ports | Proxy ports, full ports, interface blocks and nested ports (clause 9). | 20 |
| FLOW | Flows and features | Flow properties, item flows, provided and required features, change events (clause 9). | 23 |
| CNS | Constraint blocks | Constraint blocks, constraint properties and parametric models (clause 10). | 7 |
| ACT | Activities | Control operators, rates, probabilities, buffering, optional parameters (clause 11). | 18 |
| BEH | Interactions, state machines and use cases | What SysML keeps and drops of the UML behavior diagrams, and the use case relationships (clauses 12 to 14). | 7 |
| ALLOC | Allocation | The allocate relationship and allocate activity partitions (clause 15). | 8 |
| REQ | Requirements | Requirements and the relationships between requirements and other elements (clause 16). | 23 |
| DIAG | Diagram kinds and frames | What each diagram kind is attached to and what it may show (clauses 8 to 16, Annexes A and B). | 21 |
| CONF | Language architecture and conformance | The UML subset, excluded constructs, profile mechanics and conformance (clauses 4 to 6, 17). | 11 |
| DEP | Deprecated elements | Flow ports and flow specifications, kept for compatibility (Annex C). | 8 |

Totals: 225 rules (177 must, 3 should, 45 note).

Section references are to the clauses and annexes of the SysML 1.5 specification (formal/17-05-01); a bracketed number is the number of the constraint in that sub clause's Constraints list. "Applies when" is shown only for rules that do not apply to every model.

## MOD: Model management

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| SYSML-MOD-001 | must | static | The general classifier of a conform relationship is a viewpoint. | 7.3.2.1 [1] |
| SYSML-MOD-002 | must | static | The specific classifier of a conform relationship is a view. | 7.3.2.1 [2] |
| SYSML-MOD-003 | must | static | The client of an expose relationship is a view. | 7.3.2.3 [1] |
| SYSML-MOD-004 | must | static | A view conforms to a single viewpoint. | 7.3.2.7 [1] |
| SYSML-MOD-005 | must | partial | A view's viewpoint, and its stakeholders, are derived from the general classifier of the conform generalization for which the view is the specific classifier. | 7.3.2.7 [2], [3] |
| SYSML-MOD-006 | must | partial | The methods of a viewpoint are the methods of the operations on the viewpoint that carry the create marking. | 7.3.2.8 [1] |
| SYSML-MOD-007 | must | static | A viewpoint owns at least one operation named "View" that carries the create marking. | 7.3.2.8 [2] |
| SYSML-MOD-008 | note | none | An element group owns nothing: its members are the annotated elements of its comment, an element can be in any number of groups, and being a member of a group that is a member of another group does not make the element a member of the other group. | 7.3.2.2 |
| SYSML-MOD-009 | note | none | A group asserts that its criterion applies to each member as a model element; it says nothing about instances or values of that element, or about related elements, unless the criterion text says so. | 7.3.2.2 |
| SYSML-MOD-010 | note | none | A rationale or problem is attached to any other model element in the way a comment is, including to a relationship. | 7.3.2.4; 7.3.2.5 |
| SYSML-MOD-011 | note | none | Views and viewpoints follow ISO 42010: a viewpoint frames stakeholder concerns and gives the method; a view is the model element standing for the artifact, which itself may live outside the model. | 7.1.1 |

## BLK: Blocks and properties

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| SYSML-BLK-001 | must | static | An association whose two ends are both typed by blocks has exactly two ends. | 8.3.2.4 [1] |
| SYSML-BLK-002 | must | static | A connector owned by a block has exactly two ends. This covers binding connectors, which are not typed by an association. | 8.3.2.4 [2] |
| SYSML-BLK-003 | must | static | A property typed by a block and owned by an association has no name and is not a navigable end owned by the association. | 8.3.2.4 [3] |
| SYSML-BLK-004 | must | static | A property typed by a block is an end of an association. An inverse end, owned by another block or by the association, always exists so the inverse multiplicity can be recorded. | 8.3.2.4 [4] |
| SYSML-BLK-005 | must | static | A property owned by a block or value type and typed by a value type has composite aggregation. | 8.3.2.4 [6] |
| SYSML-BLK-006 | must | runtime | Within an instance of a block, the values of properties with composite aggregation form an acyclic graph: an instance never contains itself through a chain of composite properties. | 8.3.2.4 [7] |
| SYSML-BLK-007 | must | static | Every classifier that specializes a block is itself a block (or a specialization of a block). | 8.3.2.4 [8] |
| SYSML-BLK-008 | note | none | SysML removes two UML rules about connectors: that the elements attached to connector ends are roles of the owning classifier or ports of such roles, and that the part with a port is not itself a port. Connector ends may therefore reach nested properties. | 8.3.2.4 [5], [9] |
| SYSML-BLK-009 | must | static | The principal of an adjunct property is a connector, call action, object node, variable, parameter, submachine state or interaction use. | 8.3.2.2 [1] |
| SYSML-BLK-010 | must | static | An adjunct property has the same name as its principal. | 8.3.2.2 [2] |
| SYSML-BLK-011 | must | static | An adjunct property whose principal is a connector or a call action is composite. | 8.3.2.2 [3] |
| SYSML-BLK-012 | must | static | An adjunct property is owned, at least indirectly, by an element that owns its principal, or by a specialization of that element. | 8.3.2.2 [4] |
| SYSML-BLK-013 | must | static | An adjunct property whose principal is a connector, object node, variable or parameter has the same type as the principal or one of the principal's generalizations. | 8.3.2.2 [5] |
| SYSML-BLK-014 | must | static | A connector that is the principal of an adjunct property is typed by an association block. | 8.3.2.2 [6] |
| SYSML-BLK-015 | must | static | When both adjunct property and connector property apply to a property, they have the same principal and connector. | 8.3.2.2 [7] |
| SYSML-BLK-016 | must | static | An adjunct property whose principal is a call action is composite, is typed by the invoked behavior or a generalization of it (for an operation call, one that generalizes every behavior that might be dispatched), and has upper multiplicity one when the invoked behavior is not reentrant. | 8.3.2.2 [8] |
| SYSML-BLK-017 | must | static | An adjunct property whose principal is an object node has lower multiplicity zero and an upper multiplicity at least that of the node's upper bound. | 8.3.2.2 [9] |
| SYSML-BLK-018 | must | static | An adjunct property whose principal is a variable or parameter has a lower multiplicity no greater than, and an upper multiplicity no less than, that of the principal. | 8.3.2.2 [10] |
| SYSML-BLK-019 | must | static | An adjunct property whose principal is an interaction use or submachine state is composite and typed by the invoked interaction or state machine, or a generalization of it. | 8.3.2.2 [11] |
| SYSML-BLK-020 | must | partial | The two ends of a binding connector have the same type or compatible types, so that equality of their values can be defined. | 8.3.2.3 [1] |
| SYSML-BLK-021 | must | static | A property with a bound reference is the role of an end of at least one binding connector, or is generalized by such a property through redefinition. | 8.3.2.5 [1] |
| SYSML-BLK-022 | must | static | The bound end of a bound reference is the end of that binding connector opposite the property. | 8.3.2.5 [2] |
| SYSML-BLK-023 | must | partial | The role of the bound end is reachable by navigation from instances of the owning block, and is neither the bound reference itself nor a property related to it by redefinition. | 8.3.2.5 [3] |
| SYSML-BLK-024 | must | static | The last element of a bound reference's binding path is the role of its bound end; the earlier elements are the property path of the nested connector end, if any. | 8.3.2.5 [4] |
| SYSML-BLK-025 | must | static | A bound reference is a reference property or a value property. | 8.3.2.5 [5] |
| SYSML-BLK-026 | must | static | A bound reference with upper multiplicity greater than one is ordered and non-unique. | 8.3.2.5 [6] |
| SYSML-BLK-027 | must | static | A bound reference is not applied to a property that is related by redefinition to another property with a bound reference. | 8.3.2.5 [7] |
| SYSML-BLK-028 | must | static | The binding connector of a bound reference does not have the same property, or properties related by redefinition, at both ends. | 8.3.2.5 [8] |
| SYSML-BLK-029 | must | static | A classifier behavior property is applied only to properties owned (not inherited) by blocks that have a classifier behavior. | 8.3.2.6 [1] |
| SYSML-BLK-030 | must | static | A classifier behavior property is composite. | 8.3.2.6 [2] |
| SYSML-BLK-031 | must | static | A classifier behavior property is typed by the classifier behavior of its owning block or a generalization of it. | 8.3.2.6 [3] |
| SYSML-BLK-032 | must | static | A connector property is applied only to properties of blocks. | 8.3.2.7 [1] |
| SYSML-BLK-033 | must | static | The connector of a connector property is owned or inherited by a block that owns the property. | 8.3.2.7 [2] |
| SYSML-BLK-034 | must | static | A connector property is composite. | 8.3.2.7 [3] |
| SYSML-BLK-035 | must | static | The type of the connector of a connector property is an association block. | 8.3.2.7 [4] |
| SYSML-BLK-036 | must | static | A connector property has the same name and type as its connector. | 8.3.2.7 [5] |
| SYSML-BLK-037 | must | static | A directed relationship with a property path has a source context when its source is a property and has none otherwise; likewise for the target context. | 8.3.2.8 [1], [2] |
| SYSML-BLK-038 | must | static | A directed relationship's source (target) is a property when its source (target) property path has a value. | 8.3.2.8 [3], [4] |
| SYSML-BLK-039 | must | static | The first property of a source or target property path is owned by the corresponding context or one of its generalizations. | 8.3.2.8 [5], [6] |
| SYSML-BLK-040 | must | static | Each later property of a property path is owned by the block or value type that types the preceding property, or a generalization of it. | 8.3.2.8 [7]; 8.3.2.10 [1] |
| SYSML-BLK-041 | must | static | The type of the last property of a source (target) property path owns or inherits the source (target) of the relationship. | 8.3.2.8 [8], [9] |
| SYSML-BLK-042 | must | static | A distributed property is applied only to properties of blocks or value types. | 8.3.2.9 [1] |
| SYSML-BLK-043 | must | static | An end path multiplicity is applied only to properties related by redefinition to a property that has a bound reference. | 8.3.2.11 [1] |
| SYSML-BLK-044 | must | static | The lower value of an end path multiplicity is not negative. | 8.3.2.11 [2] |
| SYSML-BLK-045 | must | static | The first property of a nested connector end's path is owned by the block that owns the connector, or one of its generalizations. | 8.3.2.12 [1] |
| SYSML-BLK-046 | must | static | The type of the last property of a nested connector end's path owns or inherits the property that is the role of the connector end. | 8.3.2.12 [2] |
| SYSML-BLK-047 | must | static | A nested connector end is applied only to connector ends. | 8.3.2.12 [3] |
| SYSML-BLK-048 | must | static | A participant property is applied only to properties of association blocks. | 8.3.2.13 [1] |
| SYSML-BLK-049 | must | static | A participant property is not a member end of an association. | 8.3.2.13 [2] |
| SYSML-BLK-050 | must | static | A participant property has aggregation none. | 8.3.2.13 [3] |
| SYSML-BLK-051 | must | static | The end of a participant property is a member end of the association block that owns the property. | 8.3.2.13 [4] |
| SYSML-BLK-052 | must | static | A participant property has the same type as the end it refers to. | 8.3.2.13 [5] |
| SYSML-BLK-053 | must | static | A participant property has multiplicity 1. | 8.3.2.13 [6] |
| SYSML-BLK-054 | must | static | A property-specific type is the type of one and only one property. | 8.3.2.14 [1] |
| SYSML-BLK-055 | must | static | A property-specific type has no name. | 8.3.2.14 [2] |
| SYSML-BLK-056 | must | static | A property-specific type specializes at most the single classifier that was named as its starting type; with no starting type it specializes nothing. | 8.3.2.14 |
| SYSML-BLK-057 | note | none | Four kinds of property are recognized: part (typed by a block, composite), reference (typed by a block, not composite), value (typed by a value type, always composite) and constraint (typed by a constraint block). Ports are a further category of property. | 8.3.2.4; 8.3.1.2.1 |
| SYSML-BLK-058 | note | partial | A block's internal connectors are always available. An encapsulated block (isEncapsulated true) is a black box: a part typed by it connects only through its ports or to its outer boundary; otherwise connections may reach its internal structure through nested connector ends. | 8.3.2.4 |
| SYSML-BLK-059 | note | none | Nested connector ends do not follow strict encapsulation; they are for cases where adding intermediate properties at each level is not feasible. The connector is owned by the nearest block that owns both ends. | 8.3.1.2.6 |
| SYSML-BLK-060 | must | partial | If a property of a block has initial values for properties of its type, its default value is an instance value that refers to an unnamed instance specification owned by the package that owns the outermost containing block. | 8.3.2.4 (initial values) |

## VAL: Value types and units

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| SYSML-VAL-001 | must | static | Every classifier that specializes a value type is itself a value type. | 8.3.2.15 [1] |
| SYSML-VAL-002 | must | static | The unit of a value type is an instance specification classified by Unit (from the unit and quantity kind library) or a specialization of it. | 8.3.2.15 [2] |
| SYSML-VAL-003 | must | static | The quantity kind of a value type is an instance specification classified by QuantityKind or a specialization of it. | 8.3.2.15 [3] |
| SYSML-VAL-004 | must | static | The only valid use of a quantity kind instance is to be referenced by the quantity kind of a value type or of a unit; the only valid use of a unit instance is to be referenced by the unit of a value type. | 8.3.3.2.1; 8.3.3.2.2 |
| SYSML-VAL-005 | note | partial | Two instance specifications represent the same unit (or quantity kind) if and only if both have a definition URI and the two are equal. | 8.3.3.2.1; 8.3.3.2.2 |
| SYSML-VAL-006 | note | none | A value type may state a quantity kind without a unit, to type a value in a form independent of any unit. | 8.3.2.15 |
| SYSML-VAL-007 | note | none | Unqualified Boolean, Integer, Real and String mean the UML primitive types when defining a SysML extension, and the value types of the primitive value type library everywhere else. | 4.3 |
| SYSML-VAL-008 | note | none | A value type may carry its own properties and operations, as a UML data type can, and may be structured. | 8.3.2.15 |

## PORT: Ports

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| SYSML-PORT-001 | must | static | A port is not both a proxy port and a full port, even when one of the two markings is on a subsetted or redefined port. | 9.3.2.8 [1]; 9.3.2.12 [1] |
| SYSML-PORT-002 | must | static | A proxy port is typed only by an interface block. | 9.3.2.12 [2] |
| SYSML-PORT-003 | must | static | Ports owned by the type of a proxy port are proxy ports. | 9.3.2.12 [3] |
| SYSML-PORT-004 | should | partial | A completely specified proxy port is connected to internal parts or is behavioral. A block may declare a non-behavioral proxy port without internal connectors, to be completed in a specialization. | 9.3.2.12 |
| SYSML-PORT-005 | must | partial | When a proxy port is connected to a single internal part, the connector is a binding connector or has the same semantics as one. | 9.3.2.12 |
| SYSML-PORT-006 | must | static | A full port is not behavioral. | 9.3.2.8 [3] |
| SYSML-PORT-007 | must | static | A full port is not conjugated. | 9.3.2.8 [4] |
| SYSML-PORT-008 | must | static | A binding connector does not link a full port, directly or through other binding connectors, to another composite property of the block that owns the full port (or of that block's generalizations or specializations), unless that property is a non-full port. | 9.3.2.8 [2] |
| SYSML-PORT-009 | must | static | An interface block does not own or inherit behaviors, does not have classifier behaviors, and has no methods for its behavioral features. | 9.3.2.9 [1] |
| SYSML-PORT-010 | must | static | An interface block has no composite properties other than ports. | 9.3.2.9 [2] |
| SYSML-PORT-011 | must | static | Ports owned by an interface block are typed only by interface blocks. | 9.3.2.9 [3] |
| SYSML-PORT-012 | must | static | A trigger on a nested port has exactly one port, and that port is not a full port; the ports in its nested port path are not full ports. | 9.3.2.13 [1], [2] |
| SYSML-PORT-013 | must | static | The first port in a trigger's nested port path is owned by a block in which the trigger is used, or a generalization of it; each later port is owned by the type of the preceding one; the type of the last port owns or inherits the trigger's port. | 9.3.2.13 [3], [4], [5] |
| SYSML-PORT-014 | must | static | The nested-port trigger extension is applied only to triggers. | 9.3.2.13 [6] |
| SYSML-PORT-015 | must | static | An invocation on a nested port has a value for its port property. | 9.3.2.10 [1] |
| SYSML-PORT-016 | must | static | The first port in an invocation's nested port path is owned by a block that types the target pin, or a generalization of it; each later port is owned by the type of the preceding one; the type of the last port owns or inherits the invocation's port. | 9.3.2.10 [2], [3], [4] |
| SYSML-PORT-017 | must | static | The nested-port invocation extension is applied only to invocation actions. | 9.3.2.10 [5] |
| SYSML-PORT-018 | note | none | Invocations intended to leave the executing object are sent to it on a proxy port; invocations intended for a target object are sent to a port of that object. | 9.3.2.10 |
| SYSML-PORT-019 | note | none | A port with a type that has ports nests those ports; a conjugated port reverses the direction of flow properties and the meaning of provided and required, but its nested ports behave as if not conjugated. | 9.1.2; 9.3.2.2 |
| SYSML-PORT-020 | note | none | Items going to or from a behavioral port go to or from the owning block; items going to a non-behavioral port go to the port itself (full port) or to the internal parts it is connected to (proxy port). | 9.3.2.7 |

## FLOW: Flows and features

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| SYSML-FLOW-001 | must | static | A flow property is typed by a value type, block or signal. | 9.3.2.7 [1] |
| SYSML-FLOW-002 | must | partial | Flow between ends of a connector occurs only between matching flow properties: the directions match and the target type is the same as, or a generalization of, the source type. If several flow properties match by direction and type, their names must also match; if several still match, no flow occurs. | 9.3.2.7 |
| SYSML-FLOW-003 | must | runtime | An "in" flow property is not modified by the owning or realizing block or blocks it contains; an "out" flow property is modified only by them; "inout" can be used either way. | 9.3.2.7 |
| SYSML-FLOW-004 | must | partial | For items to flow through a proxy port, flow property directions are the same on the proxy port and on the owning block or internal part it stands in for. | 9.3.2.7 |
| SYSML-FLOW-005 | must | static | A directed feature is applied only to behavioral features, or to properties that are not flow properties. | 9.3.2.4 [1] |
| SYSML-FLOW-006 | must | static | An operation that is not provided is not associated with a behavior as its method. | 9.3.2.4 [2] |
| SYSML-FLOW-007 | must | partial | A single provided behavioral feature matches each required one: same kind (operation or reception), same names including parameter names in order, same parameter directions in order, provided in-parameter types the same or more general, provided out and return types the same or more specialized, inout types the same, and corresponding multiplicity, order and uniqueness conditions, with provided preconditions the same or more general and provided body conditions and postconditions the same or more specialized. (Applies when: required features are used across a connector.) | 9.3.2.4 |
| SYSML-FLOW-008 | must | partial | A provided non-flow property matches a required one when they have the same name; for reading, types, multiplicities, uniqueness and ordering match as out parameters do; for writing, as in parameters do; for both, they are the same. (Applies when: required features are used across a connector.) | 9.3.2.4 |
| SYSML-FLOW-009 | note | none | Meanings of "provided" and "required", and of "in" and "out", are swapped for conjugated ports. | 9.3.2.4; 9.3.2.5; 9.3.2.6 |
| SYSML-FLOW-010 | must | static | A connector or association (possibly inherited) exists between the source and the target of an item flow. | 9.3.2.11 [1] |
| SYSML-FLOW-011 | must | static | An item property is typed by a value type, block or signal. | 9.3.2.11 [2] |
| SYSML-FLOW-012 | must | static | An item property is a property of the common (possibly indirect) owner of the item flow's source and target. | 9.3.2.11 [3] |
| SYSML-FLOW-013 | must | static | An item property has no value when the item flow is realized by an association. | 9.3.2.11 [4] |
| SYSML-FLOW-014 | must | static | When an item flow has an item property, one of its conveyed classifiers is the type of that property. | 9.3.2.11 [5] |
| SYSML-FLOW-015 | must | static | When an item flow has an item property, the item flow has the same name as that property. | 9.3.2.11 [6] |
| SYSML-FLOW-016 | must | partial | An item flow on a connector is compatible with the flow properties of the usages at each end: its direction fits their directions, each conveyed classifier is the same as, a specialization of, or a generalization of at least one flow property type at each end, and the target flow property type is the same as or a generalization of the more specialized of the item flow classifier and the source flow property type. (Applies when: the connector ends have flow properties.) | 9.3.2.11 |
| SYSML-FLOW-017 | note | none | Flow properties say what can flow in or out of a block; item flows say what does flow between particular usages. This lets one block be connected in different ways in different contexts. | 9.1.4 |
| SYSML-FLOW-018 | must | static | The structural feature of a change structural feature event is not static. | 9.3.2.3 [1] |
| SYSML-FLOW-019 | must | static | The structural feature of a change structural feature event has exactly one featuring classifier. | 9.3.2.3 [2] |
| SYSML-FLOW-020 | must | static | An accept change structural feature event action has exactly one trigger, and its event is a change structural feature event. | 9.3.2.1 [1] |
| SYSML-FLOW-021 | must | static | Such an action has two result pins with the type and ordering of the structural feature and a compatible multiplicity. | 9.3.2.1 [2] |
| SYSML-FLOW-022 | must | static | The structural feature of the trigger event is owned or inherited by the context of the behavior that contains the action, and its visibility allows the object performing the action to access it. | 9.3.2.1 [3], [4] |
| SYSML-FLOW-023 | note | none | SysML removes the UML rule that an accept event action has no output pins when its triggers are only change events, for actions that carry the change structural feature extension. | 9.3.2.1 [5] |

## CNS: Constraint blocks

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| SYSML-CNS-001 | must | static | A constraint block owns only: properties that define its constraint parameters, constraint properties holding nested usages of constraint blocks, binding connectors between internally nested parameters, constraint expressions that interpret it, and general-purpose model management and crosscutting elements. | 10.3.2.1 [1] |
| SYSML-CNS-002 | must | static | Every classifier that specializes a constraint block is itself a constraint block. | 10.3.2.1 [2] |
| SYSML-CNS-003 | must | static | Every property of a block that is typed by a constraint block has composite aggregation. | 10.3.2.1 [3] |
| SYSML-CNS-004 | must | static | All properties of a constraint block are constraint parameters, except constraint properties that hold nested usages of constraint blocks. | 10.1; 10.3.2.1 |
| SYSML-CNS-005 | must | partial | On a parametric diagram, every property other than the constraint properties is either bound directly to a constraint parameter or contains a property that is, through any number of levels of containment. | 10.3.1.2 |
| SYSML-CNS-006 | note | none | SysML names and structures constraints but specifies no machine-interpretable language for them; the interpretation of a constraint block must be supplied, and constraint blocks are non-causal (they do not choose dependent and independent variables). | 10.1 |
| SYSML-CNS-007 | must | partial | The context block for the usages of constraint blocks is specified on a parametric diagram so nested property names resolve in the right namespace. | 10.1 |

## ACT: Activities

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| SYSML-ACT-001 | must | static | A behavior or operation with the control operator marking has at least one parameter typed by ControlValue; one without the marking has none. | 11.3.2.2 [1] |
| SYSML-ACT-002 | must | static | A behavior is a control operator if it is the method of an operation that is a control operator. | 11.3.2.2 [2] |
| SYSML-ACT-003 | must | static | The discrete and continuous markings are not applied to the same element. | 11.3.2.3 [1] |
| SYSML-ACT-004 | must | static | The no-buffer and overwrite markings are not applied to the same element. | 11.3.2.4 [1]; 11.3.2.5 [1] |
| SYSML-ACT-005 | must | static | A parameter with the optional marking has lower multiplicity zero; any other parameter in an activity has lower multiplicity greater than zero ("required"). | 11.3.2.6 [1] |
| SYSML-ACT-006 | must | static | A probability applies only to activity edges whose source is a decision node or object node, or to output parameter sets. | 11.3.2.7 [1] |
| SYSML-ACT-007 | must | static | If a probability is applied to an edge, it is applied to all edges leaving the same source. | 11.3.2.7 [2] |
| SYSML-ACT-008 | must | static | If a probability is applied to an output parameter set, it is applied to all parameter sets of the owning behavior or operation. | 11.3.2.7 [3] |
| SYSML-ACT-009 | must | static | When a probability is applied to output parameter sets, every output parameter is in some parameter set. | 11.3.2.7 [4] |
| SYSML-ACT-010 | must | runtime | Probabilities are between zero and one inclusive and sum to one over the edges that leave the same source (or the output parameter sets of one behavior) when they are used. | 11.3.2.7 |
| SYSML-ACT-011 | must | static | A parameter with a rate is streaming. | 11.3.2.8 [1] |
| SYSML-ACT-012 | must | partial | The rate of a parameter is no greater than the rates of edges that enter or leave the pins and parameter nodes corresponding to it. | 11.3.2.8 [2] |
| SYSML-ACT-013 | must | partial | The value of a rate is an instance of a classifier that is a value type or a distribution definition, and the denominator of its unit is a time unit. | 11.3.2.8 |
| SYSML-ACT-014 | must | static | An object node of type ControlValue has the control-type setting true. | 11.3.3.1.1 [1] |
| SYSML-ACT-015 | note | none | A control value is an input or output of a control operator, which is how control acts as data; its enable literal starts a new execution and its disable literal ends an executing behavior, which can only be restarted from the beginning. | 11.1.1; 11.3.3.1.1 |
| SYSML-ACT-016 | note | none | Activities appear on block definition diagrams as blocks. A composition association between activities means that ending the whole ends the executions of the parts, and the upper multiplicity on the part end limits concurrent synchronous executions of the invoked behavior. | 11.3.1.1.1 |
| SYSML-ACT-017 | note | none | For object nodes that are the target of continuous flows, the no-buffer and overwrite markings have the same effect. | 11.3.2.4; 11.3.2.5 |
| SYSML-ACT-018 | note | none | Rate says how many items cross an edge or parameter per time interval; it does not describe how a value changes over time. Continuous and discrete rates are independent of UML streaming. | 11.3.2.1; 11.3.2.8 |

## BEH: Interactions, state machines and use cases

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| SYSML-BEH-001 | must | static | Of the UML interaction diagrams SysML includes only the sequence diagram; communication, interaction overview and timing diagrams are excluded. | 12.1; 12.3.1.1 |
| SYSML-BEH-002 | must | static | Protocol state machines are excluded; the standard (behavior) state machines are used, and are sufficient to express protocols. | 13.1 |
| SYSML-BEH-003 | note | none | Interactions, state machines and activities are classes whose instances are executions; they appear on block definition diagrams as blocks, with the activity, interaction or state machine keyword, and are associated with the behaviors they invoke and with the types of their parameters. | 11.3.1.1.1; 12.3.1.2.1; 13.3.1.1.1 |
| SYSML-BEH-004 | note | none | The use case relationships are communication (an association between actor and use case), include, extend and generalization. A use case diagram describes how a subject is used by actors to reach a goal; the subject may be drawn as a system boundary. | 14.1 |
| SYSML-BEH-005 | note | none | An included use case is part of the normal execution of the including use case and required for the base use case's goals; an extending use case is optional, acts at a named extension point under a condition, and typically is not meaningful alone, while the extended use case is. | 14.1; 14.4 |
| SYSML-BEH-006 | note | none | Include and extend are often subjective and may be reversed according to the modeler's approach. | 14.4 |
| SYSML-BEH-007 | note | none | A use case is realized by behaviors (activity, sequence and state machine diagrams); a package named for its top-level use case can hold the lower-level use cases as an implicit trace that complements explicit trace relationships. | 14.1; 14.4 |

## ALLOC: Allocation

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| SYSML-ALLOC-001 | must | static | The allocate extension is applied only to abstractions. | 15.3.2.1 [1] |
| SYSML-ALLOC-002 | must | static | A single allocate dependency has exactly one client (from) and one supplier (to). | 15.3.2.1 [2] |
| SYSML-ALLOC-003 | must | none | Any more specialized form of allocation has constraints on its supplier and client as appropriate. | 15.3.2.1 [3] |
| SYSML-ALLOC-004 | must | static | An action in an allocate activity partition is the client (from end) of an allocate dependency whose supplier (to end) is the element that the partition represents. | 15.3.2.2 [1] |
| SYSML-ALLOC-005 | must | none | An allocate activity partition keeps the constraints, but not the semantics, of a UML activity partition: the represented classifier or property has no direct responsibility for invoking the behavior in the partition. | 15.3.2.2 [2] |
| SYSML-ALLOC-006 | note | none | Allocation is permitted between any two named elements and is a precursor to a more concrete relationship between them, their properties, operations or specializations. | 15.3.2.1 |
| SYSML-ALLOC-007 | note | none | Allocation of an object flow to a connector is an allocation of usage; it implies nothing about the defining blocks of the flow or the defining associations of the connector. Allocation of control flow and of pins to ports is not specifically addressed. | 15.3.2.1 |
| SYSML-ALLOC-008 | should | none | In a partition name, a property is designated by a fully qualified name (with a colon) and a classifier by a simple name (no colon). | 15.3.2.2 [1] |

## REQ: Requirements

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| SYSML-REQ-001 | must | static | A requirement owns no operations. | 16.3.2.5 [1] |
| SYSML-REQ-002 | must | static | A requirement owns no attributes. | 16.3.2.5 [2] |
| SYSML-REQ-003 | must | static | A requirement does not take part in associations. | 16.3.2.5 [3] |
| SYSML-REQ-004 | must | static | A requirement does not take part in generalizations. | 16.3.2.5 [4] |
| SYSML-REQ-005 | must | static | A classifier nested in a requirement is also a requirement. | 16.3.2.5 [5] |
| SYSML-REQ-006 | must | static | A requirement is not used to type any other model element. | 16.3.2.5 [6] |
| SYSML-REQ-007 | must | static | Every requirement has a text and a unique id. | 16.3.2.1 (attributes) |
| SYSML-REQ-008 | note | none | By default a compound requirement is satisfied only if all its sub-requirements are; the compound requirement may say otherwise. | 16.3.2.5 |
| SYSML-REQ-009 | must | static | A copy dependency is created only between two named elements that carry a requirement kind. | 16.3.2.2 [1] |
| SYSML-REQ-010 | must | static | The text of the client of a copy dependency is a read-only copy of the text of its supplier. | 16.3.2.2 [2] |
| SYSML-REQ-011 | must | static | The copy rule applies recursively to all sub-requirements. | 16.3.2.2 [3] |
| SYSML-REQ-012 | must | static | The supplier of a derive-requirement dependency is a requirement kind. | 16.3.2.3 [1] |
| SYSML-REQ-013 | must | static | The client of a derive-requirement dependency is a requirement kind. | 16.3.2.3 [2] |
| SYSML-REQ-014 | must | static | A refine dependency has exactly one client and one supplier. | 16.3.2.4 [2] |
| SYSML-REQ-015 | must | static | A refine marking is applied only to dependencies. | 16.3.2.4 [1] |
| SYSML-REQ-016 | must | static | The supplier of a satisfy dependency is a requirement or a specialization of one. | 16.3.2.7 [1] |
| SYSML-REQ-017 | must | static | A trace marking is applied only to dependencies. | 16.3.2.8 [1] |
| SYSML-REQ-018 | must | static | A trace dependency has exactly one client and one supplier. | 16.3.2.8 [2] |
| SYSML-REQ-019 | must | static | The supplier of a verify dependency is a requirement or a specialization of one. | 16.3.2.9 [1] |
| SYSML-REQ-020 | must | static | The type of the return parameter of a test case is VerdictKind. | 16.3.2.6 [1] |
| SYSML-REQ-021 | should | none | The trace relationship has weak semantics and is not recommended in combination with the other requirement relationships. | 16.1 |
| SYSML-REQ-022 | note | none | A rationale can be attached to a requirement or to any requirement relationship, for example to a satisfy relationship to point to a trade study, or as an alternative way to record a verify relationship. | 16.1 |
| SYSML-REQ-023 | note | none | Taxonomies of requirement kinds are created by defining specializations of the requirement; the standard gives functional, interface, performance, physical and design constraint kinds only as a non-normative example. | 16.1; E.3 |

## DIAG: Diagram kinds and frames

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| SYSML-DIAG-001 | must | partial | Every SysML diagram has a frame, a heading and a contents area (the frame is optional in UML, required in SysML). | Annex A.1; B.2.4 [1], [2] |
| SYSML-DIAG-002 | must | partial | The frame of a diagram designates a model element that is the default namespace of the elements inside it; an element from another namespace is shown with a qualified name. | Annex A.1; B.2.4 [3] |
| SYSML-DIAG-003 | must | static | An activity diagram is framed by an activity. | Annex A.1; B.2.1 [1] |
| SYSML-DIAG-004 | must | static | A block definition diagram is framed by a block (including a constraint block) or a package. | Annex A.1; B.2.3 [1] |
| SYSML-DIAG-005 | must | static | An internal block diagram is framed by a block (including a constraint block); the heading names that block and every property and connector shown belongs to it. | Annex A.1; B.2.8 [1]; 8.3.1.2.2 |
| SYSML-DIAG-006 | must | static | A package diagram is framed by a package or model. | Annex A.1; B.2.9 [1] |
| SYSML-DIAG-007 | must | static | A parametric diagram is framed by a block (including a constraint block). | Annex A.1; B.2.10 [1] |
| SYSML-DIAG-008 | must | static | A requirement diagram is framed by a package or a requirement. | Annex A.1; B.2.11 [1] |
| SYSML-DIAG-009 | must | static | A sequence diagram is framed by an interaction. | Annex A.1; B.2.7 [1] |
| SYSML-DIAG-010 | must | static | A state machine diagram is framed by a state machine. | Annex A.1; B.2.12 [1] |
| SYSML-DIAG-011 | must | static | A use case diagram is framed by a package. | Annex A.1; B.2.13 [1] |
| SYSML-DIAG-012 | note | none | The diagram kinds are activity, block definition, internal block, package, parametric, requirement, sequence, state machine and use case (nine). | Annex A.1 |
| SYSML-DIAG-013 | must | partial | A requirement diagram shows only requirements, packages, other classifiers, test cases and rationale, with the containment, derive, satisfy, verify, refine, copy and trace relationships; callouts may show the relationships of other elements to a requirement. | 16.3.1.1 |
| SYSML-DIAG-014 | must | partial | Constraint blocks are defined only on block definition diagrams or package diagrams, where they are marked with the constraint keyword. | 10.4.1 |
| SYSML-DIAG-015 | must | partial | On a parametric diagram the only connectors that may be shown are binding connectors. | 10.4.2 |
| SYSML-DIAG-016 | must | none | A definition box with no keyword on a block definition diagram is a block. | 8.3.1.1.2 |
| SYSML-DIAG-017 | must | none | An element type that is not shown in a SysML diagram elements table, or in a normative usage example, is not part of the UML subset SysML includes, even if the UML packages SysML imports support it. | 6.2.2 |
| SYSML-DIAG-018 | note | none | Any combination of SysML diagram elements is allowed only if it keeps the kinds of element on a diagram kind constrained and well specified; the diagram elements tables list the symbols that can appear, not the combinations. | Annex A.1 |
| SYSML-DIAG-019 | note | none | Package diagrams and the callout notation are the two flexible mechanisms: a package diagram can hold a wide array of packageable elements, and callouts show relationships between elements that appear on different diagram kinds. | Annex A.1 |
| SYSML-DIAG-020 | note | none | Tables and matrices, graphs and trees are optional alternative notations that are consistent with the metamodel; they are not part of the diagram taxonomy and are not standardized. | Annex A.2 |
| SYSML-DIAG-021 | note | none | A diagram usage (such as a context diagram or a block hierarchy) is a constrained use of one diagram kind and may be captured by an extension of the diagram kind. | Annex A.1 |

## CONF: Language architecture and conformance

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| SYSML-CONF-001 | must | static | A SysML model uses only the UML metaclasses in the UML4SysML subset; the metaclasses of the excluded list (for example component, node, deployment, collaboration, template, protocol state machine) are not used. | 4.1 (Tables 4.1, 4.2); 6.2.2 |
| SYSML-CONF-002 | must | static | Package merge between packages is not supported in user models. | 7.3.1.1 |
| SYSML-CONF-003 | must | partial | N-ary associations and qualified associations are excluded; an association is never shown with navigation arrowheads on both ends, with a cross on a non-navigable end, or with an ownership dot. | 8.3.1.3 |
| SYSML-CONF-004 | must | none | A value type is never given the primitive keyword. | 8.3.1.3 |
| SYSML-CONF-005 | must | none | The deployment diagram, object diagram, communication, interaction overview, timing and profile diagrams are not SysML diagram kinds; deployment can be shown on an internal block diagram and a profile definition on a package diagram. | Annex A.1 |
| SYSML-CONF-006 | note | none | Where a constraint of a profile extension element is given both in text and in OCL and the two disagree, the OCL controls. | 6.2.3 |
| SYSML-CONF-007 | note | none | A tool conforms to SysML only by supporting abstract syntax, concrete syntax and model interchange conformance together; conformance does not include the deprecated elements. | 5.1; 5.2 |
| SYSML-CONF-008 | note | partial | A model that applies the SysML profile strictly may use only the UML metaclasses the profile references. | 17.4.5 |
| SYSML-CONF-009 | note | none | The three SysML model libraries are PrimitiveValueTypes, UnitAndQuantityKind and ControlValues; the QUDV and ISO 80000 libraries are non-normative. | 4.2; Annex E |
| SYSML-CONF-010 | note | none | A profile extension element is appropriate (rather than a subclass) when the extended concept is not class-based, when the extension's properties reference other model elements, or when they describe modeling data rather than system data; a subclass is appropriate when each instance has its own values that subclasses inherit. | 17.4.4 |
| SYSML-CONF-011 | note | none | A user-defined extension of a SysML element extends the same metaclasses as its parent, inherits its properties, and does not display the parent's marking on typed elements unless a diagram extension says so. | 17.4.2 |

## DEP: Deprecated elements

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| SYSML-DEP-001 | must | static | A flow port is typed by a flow specification, block, signal or value type. (Applies when: deprecated flow ports are used.) | C.3.2.3 [1] |
| SYSML-DEP-002 | must | static | An atomic flow port has a direction and no conjugation setting. (Applies when: deprecated flow ports are used.) | C.3.2.3 [2] |
| SYSML-DEP-003 | must | static | The direction of a non-atomic flow port follows the directions of the flow properties of its flow specification (reversed if conjugated); mixed directions give inout. (Applies when: deprecated flow ports are used.) | C.3.2.3 [3] |
| SYSML-DEP-004 | must | partial | Flow ports connect to flow ports with matching flow properties by type (sent type the same or a subtype of received type), direction (opposite across an external connector unless one end is inout; the same across an internal connector) and, if still ambiguous, name; if the match is still ambiguous the connection is ill formed. (Applies when: deprecated flow ports are used.) | C.3.2.3 [4] |
| SYSML-DEP-005 | must | static | A flow port that is not connected to an internal part is behavioral. (Applies when: deprecated flow ports are used.) | C.3.2.3 [5] |
| SYSML-DEP-006 | must | static | A flow specification owns no operations or receptions. (Applies when: deprecated flow specifications are used.) | C.3.2.4 [1] |
| SYSML-DEP-007 | must | static | Every owned attribute of a flow specification is a flow property. (Applies when: deprecated flow specifications are used.) | C.3.2.4 [2] |
| SYSML-DEP-008 | note | none | Item flows are not deprecated, but with atomic flow ports they follow a deprecated compatibility rule that treats the types of the source and target ports as if they were the types of flow properties on those ports. (Applies when: deprecated flow ports are used.) | C.3.2.5 |
