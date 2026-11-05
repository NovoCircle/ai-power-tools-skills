# UML 2.5.1 rules

Generated from `language.yaml` (`constraints`). Do not edit by hand; change the language file and regenerate.

Each rule has a stable id of the form `UML-<CAT>-nnn`. The number never changes once assigned. A rule that is retired keeps its id and is marked withdrawn rather than reused.

The file holds 580 rules: 449 formal constraints stated on metaclasses in the normative machine-readable model (clauses 7 to 20) and 131 rules stated in prose in the clauses. Counts by strength: must 555, should 8, note 17.

## Strength

| Strength | Meaning | Treatment |
|---|---|---|
| must | The standard states it as an invariant (formal constraint), or as a requirement ("shall", "must", "cannot", "only"). A model that breaks it is not well formed. | An error. |
| should | The standard gives it as guidance ("should"). | A warning. |
| note | An explanation, option or definition recorded for completeness (for example how a derived value is computed, or what a merge produces). | Advice only. |

Where the document and the machine-readable model disagree, the machine-readable model governs (clause 2). The 225 query-operation body conditions of that model are definitions, not rules, and are not listed.

## Applies when

A rule with no `applies_when` applies to every model. Otherwise:

| Value | The rule is checked when |
|---|---|
| `package-merge` | the model contains a package merge and the merge is being resolved |
| `profile-applied` | a profile is applied to a package of the model, or the model contains a profile |
| `execution` | the behavior is being executed or analyzed as a running model; the rule is about run-time state |

## Checkable

| Value | Meaning |
|---|---|
| `static` | a property or relationship of elements that a validator reading the saved model can check |
| `partial` | checkable for the structure, in simple cases, or only with type-conformance reasoning |
| `runtime` | describes running state; needs a live instance |
| `none` | not a property of a model (a requirement on tools, a definition, or an explanation) |

Rules whose strength is `must` and whose `checkable` is `static` are the candidates for machine checks; the rest are review guidance.

## Categories

| Category | Name | Covers | Rules |
|---|---|---|---|
| COM | Common structure | Elements, ownership, names, namespaces, imports, templates, types, multiplicity, constraints, dependencies (clause 7). Formal constraints. | 27 |
| VAL | Values | Literals, expressions, time and duration constraints and observations, intervals (clause 8). Formal constraints. | 11 |
| CLS | Classification | Classifiers, generalization, features, properties, operations, parameters, instances, redefinition and subsetting (clause 9). Formal constraints. | 44 |
| SIM | Simple classifiers | Data types, enumerations, signals, receptions, interfaces and their realization (clause 10). Formal constraints. | 5 |
| STR | Structured classifiers | Classes, associations, association classes, components, collaborations, connectors and ports (clause 11). Formal constraints. | 22 |
| PKG | Packages and profiles | Packages, models, profiles, stereotypes and extensions as metaclasses (clause 12). Formal constraints. | 14 |
| BEH | Common behavior | Behaviors, events and triggers (clause 13). Formal constraints. | 7 |
| SM | State machines | Regions, states, pseudostates, transitions and protocol state machines (clause 14). Formal constraints. | 47 |
| ACT | Activities | Activity nodes, edges, control and object nodes, partitions and regions (clause 15). Formal constraints. | 50 |
| ACN | Actions | Actions, pins, structured activity nodes (clause 16). Formal constraints. | 155 |
| INT | Interactions | Lifelines, messages, fragments, gates, interaction uses (clause 17). Formal constraints. | 49 |
| UC | Use cases | Use cases, actors, include and extend (clause 18). Formal constraints. | 8 |
| DEP | Deployments | Artifacts, nodes, deployment and communication paths (clause 19). Formal constraints. | 4 |
| INF | Information flows | Information flows and information items (clause 20). Formal constraints. | 6 |
| MRG | Package merge | The prose rules for merging packages (12.2.3). Stated in prose. | 15 |
| PRF | Profiles | The prose rules for profiles, stereotypes and their application (12.2.4 and 12.3.3). Stated in prose. | 20 |
| STD | Standard profile | The prose rules of the standard stereotypes (clause 22). Stated in prose. | 8 |
| SEM | Other prose rules | Prose well-formedness rules from the semantics and notation clauses 9 to 20 and 7.6 that are not formal constraints. Stated in prose. | 88 |

Section references are to the clauses of the UML 2.5.1 specification (formal/17-12-05). For a formal constraint the section is the "Constraints" subclause of the metaclass description. "Source" gives the constraint's name in the machine-readable model (`formal`) or a key for the prose rule.

## COM: Common structure

| Id | Strength | Rule | Applies to | Checkable | Section | Source |
|---|---|---|---|---|---|---|
| UML-COM-001 | must | The value specification of a constraint must evaluate to a Boolean. | Constraint | partial | 7.8.3.6 Constraints | formal: Constraint::boolean_value |
| UML-COM-002 | must | Evaluating a constraint's value specification must not change anything. | Constraint | none | 7.8.3.6 Constraints | formal: Constraint::no_side_effects |
| UML-COM-003 | must | A constraint cannot constrain itself. | Constraint | static | 7.8.3.6 Constraints | formal: Constraint::not_apply_to_self |
| UML-COM-004 | must | An element that must be owned has to have an owner. | Element | static | 7.8.6.6 Constraints | formal: Element::has_owner |
| UML-COM-005 | must | An element cannot own itself, directly or through a chain of owned elements. | Element | static | 7.8.6.6 Constraints | formal: Element::not_own_self |
| UML-COM-006 | must | The element being imported must be public or have no visibility. | ElementImport | static | 7.8.7.7 Constraints | formal: ElementImport::imported_element_is_public |
| UML-COM-007 | must | An element import is either public or private. | ElementImport | static | 7.8.7.7 Constraints | formal: ElementImport::visibility_public_or_private |
| UML-COM-008 | must | The upper bound must not be less than the lower bound. | MultiplicityElement | static | 7.8.8.8 Constraints | formal: MultiplicityElement::upper_ge_lower |
| UML-COM-009 | must | The lower bound must be a non-negative integer. | MultiplicityElement | static | 7.8.8.8 Constraints | formal: MultiplicityElement::lower_ge_0 |
| UML-COM-010 | must | A non-literal bound expression (lower or upper) must have no side effects when evaluated. | MultiplicityElement | none | 7.8.8.8 Constraints | formal: MultiplicityElement::value_specification_no_side_effects |
| UML-COM-011 | must | A non-literal bound expression (lower or upper) must be a constant expression. | MultiplicityElement | partial | 7.8.8.8 Constraints | formal: MultiplicityElement::value_specification_constant |
| UML-COM-012 | must | If a lower value is given it must be an Integer. | MultiplicityElement | static | 7.8.8.8 Constraints | formal: MultiplicityElement::lower_is_integer |
| UML-COM-013 | must | If an upper value is given it must be an UnlimitedNatural. | MultiplicityElement | static | 7.8.8.8 Constraints | formal: MultiplicityElement::upper_is_unlimitedNatural |
| UML-COM-014 | must | A named element owned by anything other than a namespace has no visibility; an unowned one (which can only be a package) may have one. | NamedElement | static | 7.8.9.8 Constraints | formal: NamedElement::visibility_needs_ownership |
| UML-COM-015 | note | Defines the qualified name: when the element and all enclosing namespaces are named, it is the enclosing names plus the element's name. | NamedElement | none | 7.8.9.8 Constraints | formal: NamedElement::has_qualified_name |
| UML-COM-016 | note | Defines the qualified name: if the element or any enclosing namespace is unnamed, there is no qualified name. | NamedElement | none | 7.8.9.8 Constraints | formal: NamedElement::has_no_qualified_name |
| UML-COM-017 | must | All members of a namespace must be told apart by name within it. | Namespace | static | 7.8.10.7 Constraints | formal: Namespace::members_distinguishable |
| UML-COM-018 | must | A namespace cannot package-import itself. | Namespace | static | 7.8.10.7 Constraints | formal: Namespace::cannot_import_self |
| UML-COM-019 | must | A namespace cannot element-import one of its own owned members. | Namespace | static | 7.8.10.7 Constraints | formal: Namespace::cannot_import_ownedMembers |
| UML-COM-020 | must | A package import is either public or private. | PackageImport | static | 7.8.11.6 Constraints | formal: PackageImport::public_or_private |
| UML-COM-021 | must | A packageable element owned by a namespace must have a visibility. | PackageableElement | static | 7.8.12.6 Constraints | formal: PackageableElement::namespace_needs_visibility |
| UML-COM-022 | must | Every substitution in a binding must refer to a formal parameter of the bound template's signature. | TemplateBinding | static | 7.8.16.5 Constraints | formal: TemplateBinding::parameter_substitution_formal |
| UML-COM-023 | must | A binding has at most one substitution for each formal parameter of the template signature. | TemplateBinding | static | 7.8.16.5 Constraints | formal: TemplateBinding::one_parameter_substitution |
| UML-COM-024 | must | A template parameter's default must be compatible with the formal parameter. | TemplateParameter | partial | 7.8.17.6 Constraints | formal: TemplateParameter::must_be_compatible |
| UML-COM-025 | must | An actual parameter must be compatible with its formal parameter (a class parameter takes a class, for example). | TemplateParameterSubstitution | partial | 7.8.18.5 Constraints | formal: TemplateParameterSubstitution::must_be_compatible |
| UML-COM-026 | must | Parametered elements are either owned by their template parameters or owned by the templated element. | TemplateSignature | static | 7.8.19.6 Constraints | formal: TemplateSignature::own_elements |
| UML-COM-027 | must | The names of a template signature's parameters must be unique. | TemplateSignature | static | 7.8.19.6 Constraints | formal: TemplateSignature::unique_parameters |

## VAL: Values

| Id | Strength | Rule | Applies to | Checkable | Section | Source |
|---|---|---|---|---|---|---|
| UML-VAL-001 | must | A duration with no expression must have exactly one observation, and it must be a duration observation. | Duration | static | 8.6.1.5 Constraints | formal: Duration::no_expr_requires_observation |
| UML-VAL-002 | must | The first-event flag is given twice when the constraint has two constrained elements, and not at all otherwise. | DurationConstraint | static | 8.6.2.6 Constraints | formal: DurationConstraint::first_event_multiplicity |
| UML-VAL-003 | must | A duration constraint constrains one or two elements. | DurationConstraint | static | 8.6.2.6 Constraints | formal: DurationConstraint::has_one_or_two_constrainedElements |
| UML-VAL-004 | must | The first-event flag is given twice when the observation has two events, and not at all otherwise. | DurationObservation | static | 8.6.4.6 Constraints | formal: DurationObservation::first_event_multiplicity |
| UML-VAL-005 | must | If languages are given, there must be as many languages as bodies. | OpaqueExpression | static | 8.6.16.7 Constraints | formal: OpaqueExpression::language_body_size |
| UML-VAL-006 | must | The behavior behind an opaque expression must have exactly one return result parameter. | OpaqueExpression | static | 8.6.16.7 Constraints | formal: OpaqueExpression::one_return_result_parameter |
| UML-VAL-007 | must | The behavior behind an opaque expression may have only non-stream in parameters or return parameters. | OpaqueExpression | static | 8.6.16.7 Constraints | formal: OpaqueExpression::only_in_or_return_parameters |
| UML-VAL-008 | must | Every operand of a string expression must be a literal string. | StringExpression | static | 8.6.17.6 Constraints | formal: StringExpression::operands |
| UML-VAL-009 | must | A string expression has either sub-expressions or operands, never both. | StringExpression | static | 8.6.17.6 Constraints | formal: StringExpression::subexpressions |
| UML-VAL-010 | must | A time constraint constrains exactly one element. | TimeConstraint | static | 8.6.18.6 Constraints | formal: TimeConstraint::has_one_constrainedElement |
| UML-VAL-011 | must | A time expression with no expression must have exactly one observation, and it must be a time observation. | TimeExpression | static | 8.6.19.5 Constraints | formal: TimeExpression::no_expr_requires_observation |

## CLS: Classification

| Id | Strength | Rule | Applies to | Checkable | Section | Source |
|---|---|---|---|---|---|---|
| UML-CLS-001 | must | An abstract behavioral feature has no methods. | BehavioralFeature | static | 9.9.2.8 Constraints | formal: BehavioralFeature::abstract_no_method |
| UML-CLS-002 | must | A classifier may specialize only classifiers of a valid type. | Classifier | static | 9.9.4.8 Constraints | formal: Classifier::specialize_type |
| UML-CLS-003 | must | A power type classifier cannot be a specific or general classifier in any of the generalizations of the set it classifies, so it is never an instance of itself and its instances are never its subclasses. | Classifier | static | 9.9.4.8 Constraints | formal: Classifier::maps_to_generalization_set |
| UML-CLS-004 | must | The parents of a classifier must not be final. | Classifier | static | 9.9.4.8 Constraints | formal: Classifier::non_final_parents |
| UML-CLS-005 | must | Generalization hierarchies are directed and acyclic: a classifier cannot be both a transitive general and a transitive specific of the same classifier. | Classifier | static | 9.9.4.8 Constraints | formal: Classifier::no_cycles_in_generalization |
| UML-CLS-006 | must | If substitutable arguments are allowed, there must be a constraining classifier. | ClassifierTemplateParameter | static | 9.9.5.6 Constraints | formal: ClassifierTemplateParameter::has_constraining_classifier |
| UML-CLS-007 | must | The classifier being parameterized has no direct features and, when it has no constraining classifier, no generalizations. | ClassifierTemplateParameter | static | 9.9.5.6 Constraints | formal: ClassifierTemplateParameter::parametered_element_no_features |
| UML-CLS-008 | must | If the parameterized classifier is not abstract, the classifier used as an argument must not be abstract. | ClassifierTemplateParameter | static | 9.9.5.6 Constraints | formal: ClassifierTemplateParameter::matching_abstract |
| UML-CLS-009 | must | The argument for a classifier template parameter is a classifier. | ClassifierTemplateParameter | static | 9.9.5.6 Constraints | formal: ClassifierTemplateParameter::actual_is_classifier |
| UML-CLS-010 | must | When constraining classifiers exist, every argument is the same as or a specialization of them (or substitutable for them if that is allowed). | ClassifierTemplateParameter | partial | 9.9.5.6 Constraints | formal: ClassifierTemplateParameter::constraining_classifiers_constrain_args |
| UML-CLS-011 | must | When constraining classifiers exist, the parameterized classifier is the same as or a specialization of them (or substitutable for them if that is allowed). | ClassifierTemplateParameter | partial | 9.9.5.6 Constraints | formal: ClassifierTemplateParameter::constraining_classifiers_constrain_parametered_element |
| UML-CLS-012 | must | All generalizations in one generalization set have the same general classifier. | GeneralizationSet | static | 9.9.8.6 Constraints | formal: GeneralizationSet::generalization_same_classifier |
| UML-CLS-013 | must | A power type of a generalization set cannot be a specific or general classifier in any of that set's generalizations. | GeneralizationSet | static | 9.9.8.6 Constraints | formal: GeneralizationSet::maps_to_generalization_set |
| UML-CLS-014 | must | An instance specification can act as a deployed artifact only if it represents an instance of an artifact. | InstanceSpecification | static | 9.9.9.6 Constraints | formal: InstanceSpecification::deployment_artifact |
| UML-CLS-015 | must | No two slots in one instance specification may have the same defining feature. | InstanceSpecification | static | 9.9.9.6 Constraints | formal: InstanceSpecification::structural_feature |
| UML-CLS-016 | must | The defining feature of each slot is a structural feature of one of the instance's classifiers (direct, inherited, private in a generalization, or a member end of an association), and not a redefined feature. | InstanceSpecification | static | 9.9.9.6 Constraints | formal: InstanceSpecification::defining_feature |
| UML-CLS-017 | must | An instance specification can act as a deployment target only if it represents an instance of a node and is a part in the structure of an enclosing node. | InstanceSpecification | static | 9.9.9.6 Constraints | formal: InstanceSpecification::deployment_target |
| UML-CLS-018 | must | An operation has at most one return parameter. | Operation | static | 9.9.11.7 Constraints | formal: Operation::at_most_one_return |
| UML-CLS-019 | must | Only a query operation may have a body condition. | Operation | static | 9.9.11.7 Constraints | formal: Operation::only_body_for_query |
| UML-CLS-020 | must | A default operation must have parameters that match the parameterized operation one by one in type, bounds, direction, ordering and uniqueness. | OperationTemplateParameter | partial | 9.9.12.5 Constraints | formal: OperationTemplateParameter::match_default_signature |
| UML-CLS-021 | must | Only in and inout parameters may have a delete effect; only out, inout and return parameters may have a create effect. | Parameter | static | 9.9.13.7 Constraints | formal: Parameter::in_and_out |
| UML-CLS-022 | must | An input parameter cannot be an exception. | Parameter | static | 9.9.13.7 Constraints | formal: Parameter::not_exception |
| UML-CLS-023 | must | A parameter can be tied to a connector end only inside a collaboration. | Parameter | static | 9.9.13.7 Constraints | formal: Parameter::connector_end |
| UML-CLS-024 | must | Reentrant behaviors cannot have stream parameters. | Parameter | static | 9.9.13.7 Constraints | formal: Parameter::reentrant_behaviors |
| UML-CLS-025 | must | A parameter cannot be both a stream and an exception. | Parameter | static | 9.9.13.7 Constraints | formal: Parameter::stream_and_exception |
| UML-CLS-026 | must | A parameter typed by a data type cannot have an effect. | Parameter | static | 9.9.13.7 Constraints | formal: Parameter::object_effect |
| UML-CLS-027 | must | All parameters of a parameter set are inputs, or all are outputs, of the same parameterized entity, which owns the set. | ParameterSet | static | 9.9.16.5 Constraints | formal: ParameterSet::same_parameterized_entity |
| UML-CLS-028 | must | If a parameterized entity has input (or output) parameters in a parameter set, those outside any set must be streaming. | ParameterSet | static | 9.9.16.5 Constraints | formal: ParameterSet::input |
| UML-CLS-029 | must | Two parameter sets cannot hold exactly the same parameters. | ParameterSet | static | 9.9.16.5 Constraints | formal: ParameterSet::two_parameter_sets |
| UML-CLS-030 | must | A property can subset another only when its context conforms to the context of the subsetted property. | Property | static | 9.9.17.8 Constraints | formal: Property::subsetting_context_conforms |
| UML-CLS-031 | must | A derived union property is read-only. | Property | static | 9.9.17.8 Constraints | formal: Property::derived_union_is_read_only |
| UML-CLS-032 | must | The composing end of a composite aggregation has an upper bound of at most 1. | Property | static | 9.9.17.8 Constraints | formal: Property::multiplicity_of_composite |
| UML-CLS-033 | must | A redefined property must be inherited from a more general classifier. | Property | static | 9.9.17.8 Constraints | formal: Property::redefined_property_inherited |
| UML-CLS-034 | must | A subsetting property may strengthen the subsetted property's type and may lower its upper bound. | Property | partial | 9.9.17.8 Constraints | formal: Property::subsetting_rules |
| UML-CLS-035 | must | A binding of a property template parameter that stands for an attribute must be to an attribute. | Property | static | 9.9.17.8 Constraints | formal: Property::binding_to_attribute |
| UML-CLS-036 | must | A derived union property is derived. | Property | static | 9.9.17.8 Constraints | formal: Property::derived_union_is_derived |
| UML-CLS-037 | must | A property can be a deployment target only if it is a kind of node and is a part in the structure of an enclosing node. | Property | static | 9.9.17.8 Constraints | formal: Property::deployment_target |
| UML-CLS-038 | must | A property may not subset a property that has the same name. | Property | static | 9.9.17.8 Constraints | formal: Property::subsetted_property_names |
| UML-CLS-039 | must | If a property is a classifier-owned end of a binary association, its owner must be the type of the opposite end. | Property | static | 9.9.17.8 Constraints | formal: Property::type_of_opposite_end |
| UML-CLS-040 | must | Only association ends can have qualifiers. | Property | static | 9.9.17.8 Constraints | formal: Property::qualified_is_association_end |
| UML-CLS-041 | must | A redefining element must be consistent with each element it redefines. | RedefinableElement | static | 9.9.18.8 Constraints | formal: RedefinableElement::redefinition_consistent |
| UML-CLS-042 | must | Only a non-leaf redefinable element can be redefined. | RedefinableElement | static | 9.9.18.8 Constraints | formal: RedefinableElement::non_leaf_redefinition |
| UML-CLS-043 | must | At least one redefinition context of the redefining element specializes a redefinition context of every redefined element. | RedefinableElement | static | 9.9.18.8 Constraints | formal: RedefinableElement::redefinition_context_valid |
| UML-CLS-044 | must | If any parent classifier is a template, the extended signature must include that classifier's signature. | RedefinableTemplateSignature | static | 9.9.19.6 Constraints | formal: RedefinableTemplateSignature::redefines_parents |

## SIM: Simple classifiers

| Id | Strength | Rule | Applies to | Checkable | Section | Source |
|---|---|---|---|---|---|---|
| UML-SIM-001 | must | A behavior that is the classifier's own behavior must not itself have a specification. | BehavioredClassifier | static | 10.5.1.6 Constraints | formal: BehavioredClassifier::class_behavior |
| UML-SIM-002 | must | The attributes of an enumeration are read-only. | Enumeration | static | 10.5.3.5 Constraints | formal: Enumeration::immutable |
| UML-SIM-003 | must | Every feature an interface owns must be public. | Interface | static | 10.5.5.5 Constraints | formal: Interface::visibility |
| UML-SIM-004 | must | A reception has the same name as its signal. | Reception | static | 10.5.8.5 Constraints | formal: Reception::same_name_as_signal |
| UML-SIM-005 | must | A reception's parameters match its signal's attributes in name, type and multiplicity. | Reception | static | 10.5.8.5 Constraints | formal: Reception::same_structure_as_signal |

## STR: Structured classifiers

| Id | Strength | Rule | Applies to | Checkable | Section | Source |
|---|---|---|---|---|---|---|
| UML-STR-001 | must | An association that specializes another has the same number of ends. | Association | static | 11.8.1.8 Constraints | formal: Association::specialized_end_number |
| UML-STR-002 | must | When one association specializes another, each of its ends matches an end of the general association and reaches the same type or a subtype. | Association | static | 11.8.1.8 Constraints | formal: Association::specialized_end_types |
| UML-STR-003 | must | Only binary associations can be aggregations. | Association | static | 11.8.1.8 Constraints | formal: Association::binary_associations |
| UML-STR-004 | must | Ends of an association with more than two ends must be owned by the association itself. | Association | static | 11.8.1.8 Constraints | formal: Association::association_ends |
| UML-STR-005 | must | Every member end of an association has a type. | Association | static | 11.8.1.8 Constraints | formal: Association::ends_must_be_typed |
| UML-STR-006 | must | An association class cannot be defined between itself and something else. | AssociationClass | static | 11.8.2.4 Constraints | formal: AssociationClass::cannot_be_defined |
| UML-STR-007 | must | The owned attributes and owned ends of an association class are separate sets. | AssociationClass | static | 11.8.2.4 Constraints | formal: AssociationClass::disjoint_attributes_ends |
| UML-STR-008 | must | Only an active class may own receptions or have a classifier behavior. | Class | static | 11.8.3.8 Constraints | formal: Class::passive_class |
| UML-STR-009 | must | All clients of a role binding are in one classifier and all suppliers are in one collaboration. | CollaborationUse | static | 11.8.5.5 Constraints | formal: CollaborationUse::client_elements |
| UML-STR-010 | must | Every collaboration role in the collaboration is bound in the collaboration use. | CollaborationUse | static | 11.8.5.5 Constraints | formal: CollaborationUse::every_role |
| UML-STR-011 | must | Each connector in the typing collaboration needs a corresponding connector between the bound elements in the context classifier, with the same or a more general type. | CollaborationUse | partial | 11.8.5.5 Constraints | formal: CollaborationUse::connectors |
| UML-STR-012 | must | A component cannot nest classifiers. | Component | static | 11.8.6.7 Constraints | formal: Component::no_nested_classifiers |
| UML-STR-013 | must | A component nested in a class cannot have packaged elements. | Component | static | 11.8.6.7 Constraints | formal: Component::no_packaged_elements |
| UML-STR-014 | must | The types of the connected elements must conform to the types of the ends of the association typing the connector, if there is one. | Connector | partial | 11.8.10.7 Constraints | formal: Connector::types |
| UML-STR-015 | must | The elements attached to a connector's ends must be owned or inherited roles of the connector's owning classifier, or ports of such roles. | Connector | static | 11.8.10.7 Constraints | formal: Connector::roles |
| UML-STR-016 | must | If a connector end names a part with port, the role must be a port defined or inherited by that part's type. | ConnectorEnd | static | 11.8.11.6 Constraints | formal: ConnectorEnd::role_and_part_with_port |
| UML-STR-017 | must | If a connector end is attached to a port of the owning classifier, no part with port is given. | ConnectorEnd | static | 11.8.11.6 Constraints | formal: ConnectorEnd::part_with_port_empty |
| UML-STR-018 | must | A connector end's multiplicity must not be more general than that of the matching end of the association typing the connector, if any. | ConnectorEnd | partial | 11.8.11.6 Constraints | formal: ConnectorEnd::multiplicity |
| UML-STR-019 | must | The property named as part with port must not be a port. | ConnectorEnd | static | 11.8.11.6 Constraints | formal: ConnectorEnd::self_part_with_port |
| UML-STR-020 | must | A port's aggregation must be composite. | Port | static | 11.8.14.7 Constraints | formal: Port::port_aggregation |
| UML-STR-021 | must | A port typed by an interface cannot have a default value. | Port | static | 11.8.14.7 Constraints | formal: Port::default_value |
| UML-STR-022 | must | Every port is owned by an encapsulated classifier. | Port | static | 11.8.14.7 Constraints | formal: Port::encapsulated_owner |

## PKG: Packages and profiles

| Id | Strength | Rule | Applies to | Checkable | Section | Source |
|---|---|---|---|---|---|---|
| UML-PKG-001 | must | The end of an extension that the extension does not own is typed by a class. | Extension | static | 12.4.1.7 Constraints | formal: Extension::non_owned_end |
| UML-PKG-002 | must | An extension is binary: it has exactly two member ends. | Extension | static | 12.4.1.7 Constraints | formal: Extension::is_binary |
| UML-PKG-003 | must | An extension end has multiplicity 0..1 or 1. | ExtensionEnd | static | 12.4.2.7 Constraints | formal: ExtensionEnd::multiplicity |
| UML-PKG-004 | must | An extension end is a composite aggregation. | ExtensionEnd | static | 12.4.2.7 Constraints | formal: ExtensionEnd::aggregation |
| UML-PKG-005 | must | An element a package owns that has a visibility is public or private. | Package | static | 12.4.5.8 Constraints | formal: Package::elements_public_or_private |
| UML-PKG-006 | must | An element imported into a profile as a metaclass reference is not specialized or generalized in that profile. | Profile | static | 12.4.7.5 Constraints | formal: Profile::metaclass_reference_not_specialized |
| UML-PKG-007 | must | All elements imported by metaclass reference or metamodel reference come from the same reference metamodel. | Profile | static | 12.4.7.5 Constraints | formal: Profile::references_same_metamodel |
| UML-PKG-008 | must | A stereotype can take part only in binary associations. | Stereotype | static | 12.4.9.6 Constraints | formal: Stereotype::binaryAssociationsOnly |
| UML-PKG-009 | must | A stereotype can generalize or specialize only another stereotype. | Stereotype | static | 12.4.9.6 Constraints | formal: Stereotype::generalize |
| UML-PKG-010 | should | A stereotype's name should not clash with a keyword name of the extended model element. | Stereotype | static | 12.4.9.6 Constraints | formal: Stereotype::name_not_clash |
| UML-PKG-011 | must | When a stereotype's property is an end of a non-extension association whose other end is not a stereotype, the other end is owned by the association. | Stereotype | static | 12.4.9.6 Constraints | formal: Stereotype::associationEndOwnership |
| UML-PKG-012 | must | The upper bound of a base property is exactly 1. | Stereotype | static | 12.4.9.6 Constraints | formal: Stereotype::base_property_upper_bound |
| UML-PKG-013 | must | If a stereotype extends only one metaclass, the base property's multiplicity is 1..1. | Stereotype | static | 12.4.9.6 Constraints | formal: Stereotype::base_property_multiplicity_single_extension |
| UML-PKG-014 | must | If a stereotype extends more than one metaclass, each base property has multiplicity 0..1, and only one of them holds a metaclass instance at a time. | Stereotype | static | 12.4.9.6 Constraints | formal: Stereotype::base_property_multiplicity_multiple_extension |

## BEH: Common behavior

| Id | Strength | Rule | Applies to | Checkable | Section | Source |
|---|---|---|---|---|---|---|
| UML-BEH-001 | must | A behaviored classifier owns at most one behavior for a given behavioral feature it specifies. | Behavior | static | 13.4.2.8 Constraints | formal: Behavior::most_one_behavior |
| UML-BEH-002 | must | A behavior that has a specification feature has the same number of parameters as that feature, and they should match (the matching is not formalized). | Behavior | partial | 13.4.2.8 Constraints | formal: Behavior::parameters_match |
| UML-BEH-003 | must | The behavioral feature a behavior specifies must be a feature, possibly inherited, of the behavior's context classifier. | Behavior | static | 13.4.2.8 Constraints | formal: Behavior::feature_of_context_classifier |
| UML-BEH-004 | must | A function behavior has at least one output parameter. | FunctionBehavior | static | 13.4.6.5 Constraints | formal: FunctionBehavior::one_output_parameter |
| UML-BEH-005 | must | The parameters of a function behavior are all typed by data types, which may nest only other data types. | FunctionBehavior | static | 13.4.6.5 Constraints | formal: FunctionBehavior::types_of_parameters |
| UML-BEH-006 | must | The time expression of a time event must give a non-negative integer. | TimeEvent | partial | 13.4.10.6 Constraints | formal: TimeEvent::when_non_negative |
| UML-BEH-007 | must | If a trigger names ports, its event must be a message event. | Trigger | static | 13.4.11.5 Constraints | formal: Trigger::trigger_with_ports |

## SM: State machines

| Id | Strength | Rule | Applies to | Checkable | Section | Source |
|---|---|---|---|---|---|---|
| UML-SM-001 | must | Every exit pseudostate of a connection point reference has kind exitPoint. | ConnectionPointReference | static | 14.5.1.6 Constraints | formal: ConnectionPointReference::exit_pseudostates |
| UML-SM-002 | must | Every entry pseudostate of a connection point reference has kind entryPoint. | ConnectionPointReference | static | 14.5.1.6 Constraints | formal: ConnectionPointReference::entry_pseudostates |
| UML-SM-003 | must | A final state has no exit behavior. | FinalState | static | 14.5.2.5 Constraints | formal: FinalState::no_exit_behavior |
| UML-SM-004 | must | A final state has no outgoing transitions. | FinalState | static | 14.5.2.5 Constraints | formal: FinalState::no_outgoing_transitions |
| UML-SM-005 | must | A final state has no regions. | FinalState | static | 14.5.2.5 Constraints | formal: FinalState::no_regions |
| UML-SM-006 | must | A final state cannot refer to a submachine. | FinalState | static | 14.5.2.5 Constraints | formal: FinalState::cannot_reference_submachine |
| UML-SM-007 | must | A final state has no entry behavior. | FinalState | static | 14.5.2.5 Constraints | formal: FinalState::no_entry_behavior |
| UML-SM-008 | must | A final state has no do-activity behavior. | FinalState | static | 14.5.2.5 Constraints | formal: FinalState::no_state_behavior |
| UML-SM-009 | must | A protocol state machine has a classifier as its context, never a behavioral feature. | ProtocolStateMachine | static | 14.5.4.5 Constraints | formal: ProtocolStateMachine::classifier_context |
| UML-SM-010 | must | A protocol state machine has no deep or shallow history pseudostates. | ProtocolStateMachine | static | 14.5.4.5 Constraints | formal: ProtocolStateMachine::deep_or_shallow_history |
| UML-SM-011 | must | States of a protocol state machine have no entry, exit or do-activity behaviors. | ProtocolStateMachine | static | 14.5.4.5 Constraints | formal: ProtocolStateMachine::entry_exit_do |
| UML-SM-012 | must | All transitions of a protocol state machine are protocol transitions. | ProtocolStateMachine | static | 14.5.4.5 Constraints | formal: ProtocolStateMachine::protocol_transitions |
| UML-SM-013 | should | If a protocol transition has a call-event trigger for an operation, that operation should belong to the context classifier of its state machine. | ProtocolTransition | static | 14.5.5.6 Constraints | formal: ProtocolTransition::refers_to_operation |
| UML-SM-014 | must | A protocol transition never has an effect behavior. | ProtocolTransition | static | 14.5.5.6 Constraints | formal: ProtocolTransition::associated_actions |
| UML-SM-015 | must | A protocol transition always belongs to a protocol state machine. | ProtocolTransition | static | 14.5.5.6 Constraints | formal: ProtocolTransition::belongs_to_psm |
| UML-SM-016 | must | All transitions leaving a fork must target states in different regions of an orthogonal state. | Pseudostate | static | 14.5.6.7 Constraints | formal: Pseudostate::transitions_outgoing |
| UML-SM-017 | must | In a complete state machine, a choice has at least one incoming and one outgoing transition. | Pseudostate | static | 14.5.6.7 Constraints | formal: Pseudostate::choice_vertex |
| UML-SM-018 | must | The transition leaving an initial pseudostate may have a behavior but no trigger or guard. | Pseudostate | static | 14.5.6.7 Constraints | formal: Pseudostate::outgoing_from_initial |
| UML-SM-019 | must | In a complete state machine, a join has at least two incoming transitions and exactly one outgoing transition. | Pseudostate | static | 14.5.6.7 Constraints | formal: Pseudostate::join_vertex |
| UML-SM-020 | must | In a complete state machine, a junction has at least one incoming and one outgoing transition. | Pseudostate | static | 14.5.6.7 Constraints | formal: Pseudostate::junction_vertex |
| UML-SM-021 | must | A history pseudostate has at most one outgoing transition. | Pseudostate | static | 14.5.6.7 Constraints | formal: Pseudostate::history_vertices |
| UML-SM-022 | must | An initial pseudostate has at most one outgoing transition. | Pseudostate | static | 14.5.6.7 Constraints | formal: Pseudostate::initial_vertex |
| UML-SM-023 | must | In a complete state machine, a fork has at least two outgoing transitions and exactly one incoming transition. | Pseudostate | static | 14.5.6.7 Constraints | formal: Pseudostate::fork_vertex |
| UML-SM-024 | must | All transitions entering a join must come from different regions of an orthogonal state. | Pseudostate | static | 14.5.6.7 Constraints | formal: Pseudostate::transitions_incoming |
| UML-SM-025 | must | A region has at most one deep history pseudostate. | Region | static | 14.5.8.6 Constraints | formal: Region::deep_history_vertex |
| UML-SM-026 | must | A region has at most one shallow history pseudostate. | Region | static | 14.5.8.6 Constraints | formal: Region::shallow_history_vertex |
| UML-SM-027 | must | A region is owned by a state machine or by a state, not by both. | Region | static | 14.5.8.6 Constraints | formal: Region::owned |
| UML-SM-028 | must | A region has at most one initial pseudostate. | Region | static | 14.5.8.6 Constraints | formal: Region::initial_vertex |
| UML-SM-029 | must | Only entry-point or exit-point pseudostates can be connection points of a state. | State | static | 14.5.9.8 Constraints | formal: State::entry_or_exit |
| UML-SM-030 | must | Only a submachine state can have connection point references. | State | static | 14.5.9.8 Constraints | formal: State::submachine_states |
| UML-SM-031 | must | Only a composite state can have entry or exit point pseudostates defined. | State | static | 14.5.9.8 Constraints | formal: State::composite_states |
| UML-SM-032 | must | Connection point references used as sources or targets of transitions of a submachine state must be entry or exit points defined in the submachine. | State | static | 14.5.9.8 Constraints | formal: State::destinations_or_sources_of_transitions |
| UML-SM-033 | must | A state cannot have both a submachine and regions. | State | static | 14.5.9.8 Constraints | formal: State::submachine_or_regions |
| UML-SM-034 | must | The connection points of a state machine are pseudostates of kind entry point or exit point. | StateMachine | static | 14.5.10.7 Constraints | formal: StateMachine::connection_points |
| UML-SM-035 | must | The classifier context of a state machine cannot be an interface. | StateMachine | static | 14.5.10.7 Constraints | formal: StateMachine::classifier_context |
| UML-SM-036 | must | A state machine that is the method of a behavioral feature cannot have entry or exit connection points. | StateMachine | static | 14.5.10.7 Constraints | formal: StateMachine::method |
| UML-SM-037 | must | The context classifier of a state machine that is a behavioral feature's method is the classifier that owns the feature. | StateMachine | static | 14.5.10.7 Constraints | formal: StateMachine::context_classifier |
| UML-SM-038 | must | An external transition can leave any vertex except an entry point. | Transition | static | 14.5.11.8 Constraints | formal: Transition::state_is_external |
| UML-SM-039 | must | A join segment has no guard and no trigger. | Transition | static | 14.5.11.8 Constraints | formal: Transition::join_segment_guards |
| UML-SM-040 | must | An internal transition has a state as source and its source and target are the same. | Transition | static | 14.5.11.8 Constraints | formal: Transition::state_is_internal |
| UML-SM-041 | must | Transitions leaving pseudostates (other than the initial case) have no trigger. | Transition | static | 14.5.11.8 Constraints | formal: Transition::outgoing_pseudostates |
| UML-SM-042 | must | A join segment always originates from a state. | Transition | static | 14.5.11.8 Constraints | formal: Transition::join_segment_state |
| UML-SM-043 | must | A fork segment always targets a state. | Transition | static | 14.5.11.8 Constraints | formal: Transition::fork_segment_state |
| UML-SM-044 | must | A local transition has a composite state or an entry point as its source. | Transition | static | 14.5.11.8 Constraints | formal: Transition::state_is_local |
| UML-SM-045 | must | A transition that leaves a pseudostate in a top-level region of a state machine has no trigger. | Transition | static | 14.5.11.8 Constraints | formal: Transition::initial_transition |
| UML-SM-046 | must | A fork segment has no guard and no trigger. | Transition | static | 14.5.11.8 Constraints | formal: Transition::fork_segment_guards |
| UML-SM-047 | must | The source and target of a transition are in the same state machine as the transition. | Transition | static | 14.5.11.8 Constraints | formal: Transition::transition_vertices |

## ACT: Activities

| Id | Strength | Rule | Applies to | Checkable | Section | Source |
|---|---|---|---|---|---|---|
| UML-ACT-001 | must | A parameter whose direction is not inout has exactly one activity parameter node in the activity. | Activity | static | 15.7.1.6 Constraints | formal: Activity::maximum_one_parameter_node |
| UML-ACT-002 | must | An inout parameter has exactly two activity parameter nodes in the activity, at most one with incoming edges and at most one with outgoing edges. | Activity | static | 15.7.1.6 Constraints | formal: Activity::maximum_two_parameter_nodes |
| UML-ACT-003 | must | If an activity directly owns an edge, the edge's source and target are contained, directly or not, in that same activity. | ActivityEdge | static | 15.7.2.8 Constraints | formal: ActivityEdge::source_and_target |
| UML-ACT-004 | must | All nodes and edges contained in a group are in the same activity as the group. | ActivityGroup | static | 15.7.4.7 Constraints | formal: ActivityGroup::nodes_and_edges |
| UML-ACT-005 | must | No node or edge of a group may also be contained in its subgroups or supergroups, transitively. | ActivityGroup | static | 15.7.4.7 Constraints | formal: ActivityGroup::not_contained |
| UML-ACT-006 | must | An activity parameter node with incoming edges only must have a parameter of direction out, inout or return. | ActivityParameterNode | static | 15.7.6.5 Constraints | formal: ActivityParameterNode::no_outgoing_edges |
| UML-ACT-007 | must | The parameter of an activity parameter node comes from the containing activity. | ActivityParameterNode | static | 15.7.6.5 Constraints | formal: ActivityParameterNode::has_parameters |
| UML-ACT-008 | must | An activity parameter node has the same type as its parameter. | ActivityParameterNode | static | 15.7.6.5 Constraints | formal: ActivityParameterNode::same_type |
| UML-ACT-009 | must | An activity parameter node with outgoing edges only must have a parameter of direction in or inout. | ActivityParameterNode | static | 15.7.6.5 Constraints | formal: ActivityParameterNode::no_incoming_edges |
| UML-ACT-010 | must | An activity parameter node has only incoming or only outgoing edges, not both. | ActivityParameterNode | static | 15.7.6.5 Constraints | formal: ActivityParameterNode::no_edges |
| UML-ACT-011 | must | A non-external partition that represents a classifier and has a super-partition must sit inside a super-partition that represents a classifier containing it, by nesting or by composition. | ActivityPartition | partial | 15.7.7.6 Constraints | formal: ActivityPartition::represents_classifier |
| UML-ACT-012 | must | A partition that represents a property and has a super-partition must represent a property of the classifier the super-partition represents, or of that property's type. | ActivityPartition | partial | 15.7.7.6 Constraints | formal: ActivityPartition::represents_property_and_is_contained |
| UML-ACT-013 | must | If a partition represents a property and its super-partition represents a classifier, the other non-external sub-partitions represent properties of the same classifier. | ActivityPartition | partial | 15.7.7.6 Constraints | formal: ActivityPartition::represents_property |
| UML-ACT-014 | must | A partition that is a dimension cannot be contained in another partition. | ActivityPartition | static | 15.7.7.6 Constraints | formal: ActivityPartition::dimension_not_contained |
| UML-ACT-015 | must | A control flow cannot have object nodes at either end, except object nodes of control type. | ControlFlow | static | 15.7.9.4 Constraints | formal: ControlFlow::object_nodes |
| UML-ACT-016 | must | A decision input behavior has no input parameters when the decision node has an incoming control flow and no decision input flow. | DecisionNode | partial | 15.7.12.5 Constraints | formal: DecisionNode::zero_input_parameters |
| UML-ACT-017 | must | Apart from the decision input flow, a decision node's incoming and outgoing edges are all object flows or all control flows. | DecisionNode | static | 15.7.12.5 Constraints | formal: DecisionNode::edges |
| UML-ACT-018 | must | The decision input flow of a decision node is one of its incoming edges. | DecisionNode | static | 15.7.12.5 Constraints | formal: DecisionNode::decision_input_flow_incoming |
| UML-ACT-019 | must | With a decision input flow and a second incoming object flow, the decision input behavior has two input parameters typed to accept the tokens of the two flows. | DecisionNode | partial | 15.7.12.5 Constraints | formal: DecisionNode::two_input_parameters |
| UML-ACT-020 | must | A decision node has one or two incoming edges and at least one outgoing edge. | DecisionNode | static | 15.7.12.5 Constraints | formal: DecisionNode::incoming_outgoing_edges |
| UML-ACT-021 | must | With a decision input flow and an incoming control flow, the decision input behavior has one input parameter typed to accept the decision input flow's tokens. | DecisionNode | partial | 15.7.12.5 Constraints | formal: DecisionNode::incoming_control_one_input_parameter |
| UML-ACT-022 | must | A decision input behavior has no out or inout parameters and exactly one return parameter. | DecisionNode | static | 15.7.12.5 Constraints | formal: DecisionNode::parameters |
| UML-ACT-023 | must | With no decision input flow and an incoming object flow, the decision input behavior has one input parameter typed to accept that flow's tokens. | DecisionNode | partial | 15.7.12.5 Constraints | formal: DecisionNode::incoming_object_one_input_parameter |
| UML-ACT-024 | must | The handler body has no incoming or outgoing edges and the exception input has no incoming edges. | ExceptionHandler | static | 15.7.13.5 Constraints | formal: ExceptionHandler::handler_body_edges |
| UML-ACT-025 | must | If the protected node is an action with output pins, the handler body is an action with the same number of compatible output pins. | ExceptionHandler | partial | 15.7.13.5 Constraints | formal: ExceptionHandler::output_pins |
| UML-ACT-026 | must | The handler body is an action with one input pin, and that pin is the exception input. | ExceptionHandler | static | 15.7.13.5 Constraints | formal: ExceptionHandler::one_input |
| UML-ACT-027 | must | An edge whose source is in the handler body has its target in the handler body too, and vice versa. | ExceptionHandler | static | 15.7.13.5 Constraints | formal: ExceptionHandler::edge_source_target |
| UML-ACT-028 | must | The handler body has the same owner as the protected node. | ExceptionHandler | static | 15.7.13.5 Constraints | formal: ExceptionHandler::handler_body_owner |
| UML-ACT-029 | must | The exception input has no type, or every exception type conforms to its type. | ExceptionHandler | partial | 15.7.13.5 Constraints | formal: ExceptionHandler::exception_input_type |
| UML-ACT-030 | must | A final node has no outgoing edges. | FinalNode | static | 15.7.15.5 Constraints | formal: FinalNode::no_outgoing_edges |
| UML-ACT-031 | must | A fork node's incoming and outgoing edges are all object flows or all control flows. | ForkNode | static | 15.7.17.4 Constraints | formal: ForkNode::edges |
| UML-ACT-032 | must | A fork node has exactly one incoming edge. | ForkNode | static | 15.7.17.4 Constraints | formal: ForkNode::one_incoming_edge |
| UML-ACT-033 | must | An initial node has no incoming edges. | InitialNode | static | 15.7.18.4 Constraints | formal: InitialNode::no_incoming_edges |
| UML-ACT-034 | must | All edges leaving an initial node are control flows. | InitialNode | static | 15.7.18.4 Constraints | formal: InitialNode::control_edges |
| UML-ACT-035 | must | Each interrupting edge of a region starts inside the region and ends outside it, in the same activity. | InterruptibleActivityRegion | static | 15.7.19.5 Constraints | formal: InterruptibleActivityRegion::interrupting_edges |
| UML-ACT-036 | must | A join node has exactly one outgoing edge. | JoinNode | static | 15.7.20.6 Constraints | formal: JoinNode::one_outgoing_edge |
| UML-ACT-037 | must | If any incoming edge of a join node is an object flow, its outgoing edge is an object flow; otherwise it is a control flow. | JoinNode | static | 15.7.20.6 Constraints | formal: JoinNode::incoming_object_flow |
| UML-ACT-038 | must | A merge node has exactly one outgoing edge. | MergeNode | static | 15.7.21.4 Constraints | formal: MergeNode::one_outgoing_edge |
| UML-ACT-039 | must | A merge node's incoming and outgoing edges are all object flows or all control flows. | MergeNode | static | 15.7.21.4 Constraints | formal: MergeNode::edges |
| UML-ACT-040 | must | A selection behavior on an object flow has one input and one output parameter, correctly typed, and no side effects. | ObjectFlow | partial | 15.7.22.6 Constraints | formal: ObjectFlow::input_and_output_parameter |
| UML-ACT-041 | must | An object flow cannot have executable nodes at either end. | ObjectFlow | static | 15.7.22.6 Constraints | formal: ObjectFlow::no_executable_nodes |
| UML-ACT-042 | must | A transformation behavior has one input and one output parameter, correctly typed, and no side effects. | ObjectFlow | partial | 15.7.22.6 Constraints | formal: ObjectFlow::transformation_behavior |
| UML-ACT-043 | must | An object flow can have a selection behavior only if its source is an object node. | ObjectFlow | static | 15.7.22.6 Constraints | formal: ObjectFlow::selection_behavior |
| UML-ACT-044 | must | Object nodes connected by an object flow (possibly through control nodes) have compatible types: the downstream type is the same as or a supertype of the upstream type. | ObjectFlow | partial | 15.7.22.6 Constraints | formal: ObjectFlow::compatible_types |
| UML-ACT-045 | must | Object nodes connected by an object flow (possibly through control nodes) have the same upper bound. | ObjectFlow | static | 15.7.22.6 Constraints | formal: ObjectFlow::same_upper_bounds |
| UML-ACT-046 | must | An object flow with a constant weight cannot lead to an object node whose upper bound is lower than the weight. | ObjectFlow | partial | 15.7.22.6 Constraints | formal: ObjectFlow::target |
| UML-ACT-047 | must | An object flow cannot be both multicast and multireceive. | ObjectFlow | static | 15.7.22.6 Constraints | formal: ObjectFlow::is_multicast_or_is_multireceive |
| UML-ACT-048 | must | A selection behavior on an object node has one input parameter (supertype of the node type, non-unique, 0..*) and one output parameter (same or subtype), and no side effects. | ObjectNode | partial | 15.7.23.7 Constraints | formal: ObjectNode::input_output_parameter |
| UML-ACT-049 | must | An object node has a selection behavior exactly when its ordering is ordered. | ObjectNode | static | 15.7.23.7 Constraints | formal: ObjectNode::selection_behavior |
| UML-ACT-050 | must | If an object node is not of control type, all its incoming and outgoing edges are object flows. | ObjectNode | static | 15.7.23.7 Constraints | formal: ObjectNode::object_flow_edges |

## ACN: Actions

| Id | Strength | Rule | Applies to | Checkable | Section | Source |
|---|---|---|---|---|---|---|
| UML-ACN-001 | must | The number of result pins equals the number of in and inout parameters of the operation named by the trigger, with consistent type, ordering and multiplicity. | AcceptCallAction | partial | 16.14.1.5 Constraints | formal: AcceptCallAction::result_pins |
| UML-ACN-002 | must | An accept-call action has exactly one trigger and it is for a call event. | AcceptCallAction | static | 16.14.1.5 Constraints | formal: AcceptCallAction::trigger_call_event |
| UML-ACN-003 | must | An accept-call action has isUnmarshall true. | AcceptCallAction | static | 16.14.1.5 Constraints | formal: AcceptCallAction::unmarshall |
| UML-ACN-004 | must | If isUnmarshall is false and any trigger is a signal or time event, there is exactly one result pin with multiplicity 1..1. | AcceptEventAction | static | 16.14.2.7 Constraints | formal: AcceptEventAction::one_output_pin |
| UML-ACN-005 | must | An accept-event action has no input pins. | AcceptEventAction | static | 16.14.2.7 Constraints | formal: AcceptEventAction::no_input_pins |
| UML-ACN-006 | must | A plain accept-event action whose triggers are only change or call events has no output pins. | AcceptEventAction | static | 16.14.2.7 Constraints | formal: AcceptEventAction::no_output_pins |
| UML-ACN-007 | must | If isUnmarshall is true, there is exactly one signal-event trigger and the result pins match the signal's attributes in number, type, ordering and compatible multiplicity. | AcceptEventAction | partial | 16.14.2.7 Constraints | formal: AcceptEventAction::unmarshall_signal_events |
| UML-ACN-008 | must | If isUnmarshall is false and all triggers are signal events, the single result pin has no type or every signal conforms to it. | AcceptEventAction | partial | 16.14.2.7 Constraints | formal: AcceptEventAction::conforming_type |
| UML-ACN-009 | must | The from-action of an action input pin has only action input pins as its input pins. | ActionInputPin | static | 16.14.4.5 Constraints | formal: ActionInputPin::input_pin |
| UML-ACN-010 | must | The from-action of an action input pin has exactly one output pin. | ActionInputPin | static | 16.14.4.5 Constraints | formal: ActionInputPin::one_output_pin |
| UML-ACN-011 | must | The from-action of an action input pin has no edges into or out of it or its pins. | ActionInputPin | static | 16.14.4.5 Constraints | formal: ActionInputPin::no_control_or_object_flow |
| UML-ACN-012 | must | A value pin is required. | AddStructuralFeatureValueAction | static | 16.14.5.6 Constraints | formal: AddStructuralFeatureValueAction::required_value |
| UML-ACN-013 | must | Adding to an ordered feature needs one insert-at pin (UnlimitedNatural, 1..1) unless values replace all; an unordered feature has none. | AddStructuralFeatureValueAction | static | 16.14.5.6 Constraints | formal: AddStructuralFeatureValueAction::insertAt_pin |
| UML-ACN-014 | must | A value pin is required. | AddVariableValueAction | static | 16.14.6.6 Constraints | formal: AddVariableValueAction::required_value |
| UML-ACN-015 | must | Adding to an ordered variable needs one insert-at pin (UnlimitedNatural, 1..1) unless values replace all; otherwise there is none. | AddVariableValueAction | static | 16.14.6.6 Constraints | formal: AddVariableValueAction::insertAt_pin |
| UML-ACN-016 | must | The number of argument pins equals the number of the signal's attributes. | BroadcastSignalAction | static | 16.14.7.5 Constraints | formal: BroadcastSignalAction::number_of_arguments |
| UML-ACN-017 | must | Each argument pin has the type, ordering and multiplicity of the matching signal attribute. | BroadcastSignalAction | partial | 16.14.7.5 Constraints | formal: BroadcastSignalAction::type_ordering_multiplicity |
| UML-ACN-018 | must | A broadcast signal action names no port. | BroadcastSignalAction | static | 16.14.7.5 Constraints | formal: BroadcastSignalAction::no_onport |
| UML-ACN-019 | must | Argument pins match the in and inout parameters of the called behavior or operation in number, type, ordering and multiplicity. | CallAction | partial | 16.14.8.8 Constraints | formal: CallAction::argument_pins |
| UML-ACN-020 | must | Result pins match the inout, out and return parameters of the called behavior or operation in number, type, ordering and multiplicity. | CallAction | partial | 16.14.8.8 Constraints | formal: CallAction::result_pins |
| UML-ACN-021 | must | Only a synchronous call action can have result pins. | CallAction | static | 16.14.8.8 Constraints | formal: CallAction::synchronous_call |
| UML-ACN-022 | must | A call behavior action names no port. | CallBehaviorAction | static | 16.14.9.6 Constraints | formal: CallBehaviorAction::no_onport |
| UML-ACN-023 | must | The operation (or the named port, with a provided or required interface that has the operation) must be a feature of the target pin's type. | CallOperationAction | partial | 16.14.10.6 Constraints | formal: CallOperationAction::type_target_pin |
| UML-ACN-024 | must | A clause's body output pins are output pins of actions in its body. | Clause | static | 16.14.11.5 Constraints | formal: Clause::body_output_pins |
| UML-ACN-025 | must | The decider pin is on an action in the clause's test section and is a Boolean pin of multiplicity 1..1. | Clause | static | 16.14.11.5 Constraints | formal: Clause::decider_output |
| UML-ACN-026 | must | A clause's test and body sections are disjoint. | Clause | static | 16.14.11.5 Constraints | formal: Clause::test_and_body |
| UML-ACN-027 | must | The object pin has multiplicity 1..1. | ClearAssociationAction | static | 16.14.12.5 Constraints | formal: ClearAssociationAction::multiplicity |
| UML-ACN-028 | must | The pin's type conforms to the type of at least one member end of the association. | ClearAssociationAction | partial | 16.14.12.5 Constraints | formal: ClearAssociationAction::same_type |
| UML-ACN-029 | must | The result pin has the same type as the object pin. | ClearStructuralFeatureAction | partial | 16.14.13.5 Constraints | formal: ClearStructuralFeatureAction::type_of_result |
| UML-ACN-030 | must | The result pin has multiplicity 1..1. | ClearStructuralFeatureAction | static | 16.14.13.5 Constraints | formal: ClearStructuralFeatureAction::multiplicity_of_result |
| UML-ACN-031 | must | Result pins of a conditional node have no incoming edges. | ConditionalNode | static | 16.14.15.7 Constraints | formal: ConditionalNode::result_no_incoming |
| UML-ACN-032 | must | A conditional node has no input pins. | ConditionalNode | static | 16.14.15.7 Constraints | formal: ConditionalNode::no_input_pins |
| UML-ACN-033 | must | An executable node appears in the test or body of at most one clause. | ConditionalNode | static | 16.14.15.7 Constraints | formal: ConditionalNode::one_clause_with_executable_node |
| UML-ACN-034 | must | Each clause has as many body output pins as the node has result pins, compatible in order in type, multiplicity, ordering and uniqueness. | ConditionalNode | partial | 16.14.15.7 Constraints | formal: ConditionalNode::matching_output_pins |
| UML-ACN-035 | must | The executable nodes in all clauses' test and body parts are exactly the executable nodes contained in the conditional node. | ConditionalNode | static | 16.14.15.7 Constraints | formal: ConditionalNode::executable_nodes |
| UML-ACN-036 | must | No two clauses are predecessors of each other, directly or indirectly. | ConditionalNode | static | 16.14.15.7 Constraints | formal: ConditionalNode::clause_no_predecessor |
| UML-ACN-037 | must | The association is not abstract. | CreateLinkAction | static | 16.14.16.6 Constraints | formal: CreateLinkAction::association_not_abstract |
| UML-ACN-038 | must | The result pin has multiplicity 1..1. | CreateLinkObjectAction | static | 16.14.17.5 Constraints | formal: CreateLinkObjectAction::multiplicity |
| UML-ACN-039 | must | The result pin's type is the association of the action. | CreateLinkObjectAction | partial | 16.14.17.5 Constraints | formal: CreateLinkObjectAction::type_of_result |
| UML-ACN-040 | must | The association must be an association class. | CreateLinkObjectAction | static | 16.14.17.5 Constraints | formal: CreateLinkObjectAction::association_class |
| UML-ACN-041 | must | The classifier is not abstract. | CreateObjectAction | static | 16.14.18.5 Constraints | formal: CreateObjectAction::classifier_not_abstract |
| UML-ACN-042 | must | The result pin has multiplicity 1..1. | CreateObjectAction | static | 16.14.18.5 Constraints | formal: CreateObjectAction::multiplicity |
| UML-ACN-043 | must | The classifier is not an association class. | CreateObjectAction | static | 16.14.18.5 Constraints | formal: CreateObjectAction::classifier_not_association_class |
| UML-ACN-044 | must | The result pin's type is the action's classifier. | CreateObjectAction | partial | 16.14.18.5 Constraints | formal: CreateObjectAction::same_type |
| UML-ACN-045 | must | The target pin has multiplicity 1..1. | DestroyObjectAction | static | 16.14.20.6 Constraints | formal: DestroyObjectAction::multiplicity |
| UML-ACN-046 | must | The target pin has no type. | DestroyObjectAction | static | 16.14.20.6 Constraints | formal: DestroyObjectAction::no_type |
| UML-ACN-047 | must | An expansion node is the input or the output of a region, not both and not neither. | ExpansionNode | static | 16.14.22.5 Constraints | formal: ExpansionNode::region_as_input_or_output |
| UML-ACN-048 | must | An input pin may have outgoing edges only when owned by a structured activity node, and they must target nodes inside it. | InputPin | static | 16.14.24.5 Constraints | formal: InputPin::outgoing_edges_structured_only |
| UML-ACN-049 | must | The input pins of a link action are exactly those referenced by its end data. | LinkAction | static | 16.14.26.7 Constraints | formal: LinkAction::same_pins |
| UML-ACN-050 | must | The end data of a link action all belong to one association and cover all and only its member ends. | LinkAction | static | 16.14.26.7 Constraints | formal: LinkAction::same_association |
| UML-ACN-051 | must | The ends in the end data must not be static. | LinkAction | static | 16.14.26.7 Constraints | formal: LinkAction::not_static |
| UML-ACN-052 | must | Creation data for an ordered association end needs one insert-at pin (UnlimitedNatural, 1..1) unless values replace all; unordered ends have none. | LinkEndCreationData | static | 16.14.27.7 Constraints | formal: LinkEndCreationData::insertAt_pin |
| UML-ACN-053 | must | The value pin's type conforms to the type of the association end. | LinkEndData | partial | 16.14.28.7 Constraints | formal: LinkEndData::same_type |
| UML-ACN-054 | must | The value pin has multiplicity 1..1. | LinkEndData | static | 16.14.28.7 Constraints | formal: LinkEndData::multiplicity |
| UML-ACN-055 | must | The value pin is not also a qualifier value pin. | LinkEndData | static | 16.14.28.7 Constraints | formal: LinkEndData::end_object_input_pin |
| UML-ACN-056 | must | The property must be a member end of an association. | LinkEndData | static | 16.14.28.7 Constraints | formal: LinkEndData::property_is_association_end |
| UML-ACN-057 | must | The qualifiers must be qualifiers of the association end. | LinkEndData | static | 16.14.28.7 Constraints | formal: LinkEndData::qualifiers |
| UML-ACN-058 | must | Destruction data for an ordered non-unique end needs one destroy-at pin (UnlimitedNatural, 1..1) unless duplicates are destroyed; otherwise there is none. | LinkEndDestructionData | static | 16.14.29.7 Constraints | formal: LinkEndDestructionData::destroyAt_pin |
| UML-ACN-059 | must | Result pins of a loop node have no incoming edges. | LoopNode | static | 16.14.30.7 Constraints | formal: LoopNode::result_no_incoming |
| UML-ACN-060 | must | Loop variable inputs have no outgoing edges. | LoopNode | static | 16.14.30.7 Constraints | formal: LoopNode::input_edges |
| UML-ACN-061 | must | The executable nodes in the setup, test and body parts are exactly the executable nodes contained in the loop node. | LoopNode | static | 16.14.30.7 Constraints | formal: LoopNode::executable_nodes |
| UML-ACN-062 | must | Body output pins are output pins of actions in the loop body. | LoopNode | static | 16.14.30.7 Constraints | formal: LoopNode::body_output_pins |
| UML-ACN-063 | must | The test and body parts are disjoint. | LoopNode | static | 16.14.30.7 Constraints | formal: LoopNode::setup_test_and_body |
| UML-ACN-064 | must | There are as many body output pins as loop variables, compatible in order in type, multiplicity, ordering and uniqueness. | LoopNode | partial | 16.14.30.7 Constraints | formal: LoopNode::matching_output_pins |
| UML-ACN-065 | must | There are as many loop variable inputs as loop variables, matching in type, uniqueness and multiplicity. | LoopNode | partial | 16.14.30.7 Constraints | formal: LoopNode::matching_loop_variables |
| UML-ACN-066 | must | There are as many result pins as loop variables, matching in type, uniqueness and multiplicity. | LoopNode | partial | 16.14.30.7 Constraints | formal: LoopNode::matching_result_pins |
| UML-ACN-067 | must | All edges leaving loop variable pins have targets inside the loop node. | LoopNode | static | 16.14.30.7 Constraints | formal: LoopNode::loop_variable_outgoing |
| UML-ACN-068 | must | If languages are given, there are as many languages as bodies. | OpaqueAction | static | 16.14.31.6 Constraints | formal: OpaqueAction::language_body_size |
| UML-ACN-069 | must | An output pin may have incoming edges only when owned by a structured activity node, and their sources must be inside it. | OutputPin | static | 16.14.32.4 Constraints | formal: OutputPin::incoming_edges_structured_only |
| UML-ACN-070 | must | A control pin has control type. | Pin | static | 16.14.33.6 Constraints | formal: Pin::control_pins |
| UML-ACN-071 | must | A pin's multiplicity is not unique. | Pin | static | 16.14.33.6 Constraints | formal: Pin::not_unique |
| UML-ACN-072 | must | The value pin has multiplicity 1..1. | QualifierValue | static | 16.14.34.5 Constraints | formal: QualifierValue::multiplicity_of_qualifier |
| UML-ACN-073 | must | The value pin's type conforms to the type of the qualifier property. | QualifierValue | partial | 16.14.34.5 Constraints | formal: QualifierValue::type_of_qualifier |
| UML-ACN-074 | must | The qualifier is a qualifier of the association end of the owning link end data. | QualifierValue | static | 16.14.34.5 Constraints | formal: QualifierValue::qualifier_attribute |
| UML-ACN-075 | must | The result pin's type is the classifier. | ReadExtentAction | partial | 16.14.36.5 Constraints | formal: ReadExtentAction::type_is_classifier |
| UML-ACN-076 | must | The result pin has multiplicity 0..*. | ReadExtentAction | static | 16.14.36.5 Constraints | formal: ReadExtentAction::multiplicity_of_result |
| UML-ACN-077 | must | The object pin has no type. | ReadIsClassifiedObjectAction | static | 16.14.37.6 Constraints | formal: ReadIsClassifiedObjectAction::no_type |
| UML-ACN-078 | must | The result pin has multiplicity 1..1. | ReadIsClassifiedObjectAction | static | 16.14.37.6 Constraints | formal: ReadIsClassifiedObjectAction::multiplicity_of_output |
| UML-ACN-079 | must | The result pin is typed Boolean. | ReadIsClassifiedObjectAction | partial | 16.14.37.6 Constraints | formal: ReadIsClassifiedObjectAction::boolean_result |
| UML-ACN-080 | must | The object pin has multiplicity 1..1. | ReadIsClassifiedObjectAction | static | 16.14.37.6 Constraints | formal: ReadIsClassifiedObjectAction::multiplicity_of_input |
| UML-ACN-081 | must | The result pin has the type and ordering of the open association end. | ReadLinkAction | partial | 16.14.38.6 Constraints | formal: ReadLinkAction::type_and_ordering |
| UML-ACN-082 | must | The open end's multiplicity is compatible with the result pin's multiplicity. | ReadLinkAction | partial | 16.14.38.6 Constraints | formal: ReadLinkAction::compatible_multiplicity |
| UML-ACN-083 | must | The open end is visible to the object performing the action. | ReadLinkAction | static | 16.14.38.6 Constraints | formal: ReadLinkAction::visibility |
| UML-ACN-084 | must | Exactly one end data (the open end) has no value pin. | ReadLinkAction | static | 16.14.38.6 Constraints | formal: ReadLinkAction::one_open_end |
| UML-ACN-085 | must | The open end is navigable. | ReadLinkAction | static | 16.14.38.6 Constraints | formal: ReadLinkAction::navigable_open_end |
| UML-ACN-086 | must | The end property is a member end of an association. | ReadLinkObjectEndAction | static | 16.14.39.5 Constraints | formal: ReadLinkObjectEndAction::property |
| UML-ACN-087 | must | The object pin has multiplicity 1..1. | ReadLinkObjectEndAction | static | 16.14.39.5 Constraints | formal: ReadLinkObjectEndAction::multiplicity_of_object |
| UML-ACN-088 | must | The association's ends are not static. | ReadLinkObjectEndAction | static | 16.14.39.5 Constraints | formal: ReadLinkObjectEndAction::ends_of_association |
| UML-ACN-089 | must | The result pin has the type of the end property. | ReadLinkObjectEndAction | partial | 16.14.39.5 Constraints | formal: ReadLinkObjectEndAction::type_of_result |
| UML-ACN-090 | must | The result pin has multiplicity 1..1. | ReadLinkObjectEndAction | static | 16.14.39.5 Constraints | formal: ReadLinkObjectEndAction::multiplicity_of_result |
| UML-ACN-091 | must | The object pin's type is the association class that owns the end property. | ReadLinkObjectEndAction | partial | 16.14.39.5 Constraints | formal: ReadLinkObjectEndAction::type_of_object |
| UML-ACN-092 | must | The association of the end is an association class. | ReadLinkObjectEndAction | static | 16.14.39.5 Constraints | formal: ReadLinkObjectEndAction::association_of_association |
| UML-ACN-093 | must | The object pin has multiplicity 1..1. | ReadLinkObjectEndQualifierAction | static | 16.14.40.5 Constraints | formal: ReadLinkObjectEndQualifierAction::multiplicity_of_object |
| UML-ACN-094 | must | The object pin's type is the association class that owns the end carrying the qualifier. | ReadLinkObjectEndQualifierAction | partial | 16.14.40.5 Constraints | formal: ReadLinkObjectEndQualifierAction::type_of_object |
| UML-ACN-095 | must | The qualifier property has multiplicity 1..1. | ReadLinkObjectEndQualifierAction | static | 16.14.40.5 Constraints | formal: ReadLinkObjectEndQualifierAction::multiplicity_of_qualifier |
| UML-ACN-096 | must | The association's ends are not static. | ReadLinkObjectEndQualifierAction | static | 16.14.40.5 Constraints | formal: ReadLinkObjectEndQualifierAction::ends_of_association |
| UML-ACN-097 | must | The result pin has multiplicity 1..1. | ReadLinkObjectEndQualifierAction | static | 16.14.40.5 Constraints | formal: ReadLinkObjectEndQualifierAction::multiplicity_of_result |
| UML-ACN-098 | must | The result pin has the type of the qualifier property. | ReadLinkObjectEndQualifierAction | partial | 16.14.40.5 Constraints | formal: ReadLinkObjectEndQualifierAction::same_type |
| UML-ACN-099 | must | The association of the qualifier's end is an association class. | ReadLinkObjectEndQualifierAction | static | 16.14.40.5 Constraints | formal: ReadLinkObjectEndQualifierAction::association_of_association |
| UML-ACN-100 | must | The qualifier property is a qualifier of an association end. | ReadLinkObjectEndQualifierAction | static | 16.14.40.5 Constraints | formal: ReadLinkObjectEndQualifierAction::qualifier_attribute |
| UML-ACN-101 | must | A read-self action has a context classifier. | ReadSelfAction | static | 16.14.41.5 Constraints | formal: ReadSelfAction::contained |
| UML-ACN-102 | must | The result pin has multiplicity 1..1. | ReadSelfAction | static | 16.14.41.5 Constraints | formal: ReadSelfAction::multiplicity |
| UML-ACN-103 | must | If the action is in a behavior that is a method, the operation of that method is not static. | ReadSelfAction | static | 16.14.41.5 Constraints | formal: ReadSelfAction::not_static |
| UML-ACN-104 | must | The result pin's type is the context classifier. | ReadSelfAction | partial | 16.14.41.5 Constraints | formal: ReadSelfAction::type |
| UML-ACN-105 | must | The structural feature's multiplicity is compatible with the result pin's. | ReadStructuralFeatureAction | partial | 16.14.42.5 Constraints | formal: ReadStructuralFeatureAction::multiplicity |
| UML-ACN-106 | must | The result pin has the type and ordering of the structural feature. | ReadStructuralFeatureAction | partial | 16.14.42.5 Constraints | formal: ReadStructuralFeatureAction::type_and_ordering |
| UML-ACN-107 | must | The result pin has the type and ordering of the variable. | ReadVariableAction | partial | 16.14.43.5 Constraints | formal: ReadVariableAction::type_and_ordering |
| UML-ACN-108 | must | The variable's multiplicity is compatible with the output pin's. | ReadVariableAction | partial | 16.14.43.5 Constraints | formal: ReadVariableAction::compatible_multiplicity |
| UML-ACN-109 | must | The object pin has no type. | ReclassifyObjectAction | static | 16.14.44.6 Constraints | formal: ReclassifyObjectAction::input_pin |
| UML-ACN-110 | must | None of the new classifiers is abstract. | ReclassifyObjectAction | static | 16.14.44.6 Constraints | formal: ReclassifyObjectAction::classifier_not_abstract |
| UML-ACN-111 | must | The object pin has multiplicity 1..1. | ReclassifyObjectAction | static | 16.14.44.6 Constraints | formal: ReclassifyObjectAction::multiplicity |
| UML-ACN-112 | must | The reducer behavior has two input parameters and one output parameter, typed to fit the collection's element type. | ReduceAction | partial | 16.14.45.6 Constraints | formal: ReduceAction::reducer_inputs_output |
| UML-ACN-113 | must | The type of the collection pin is a collection. | ReduceAction | partial | 16.14.45.6 Constraints | formal: ReduceAction::input_type_is_collection |
| UML-ACN-114 | must | The reducer's output type conforms to the result pin's type. | ReduceAction | partial | 16.14.45.6 Constraints | formal: ReduceAction::output_types_are_compatible |
| UML-ACN-115 | must | Removing from an ordered non-unique feature takes a single remove-at pin and no value pin unless duplicates are removed; otherwise a value pin and no remove-at pin. | RemoveStructuralFeatureValueAction | static | 16.14.46.6 Constraints | formal: RemoveStructuralFeatureValueAction::removeAt_and_value |
| UML-ACN-116 | must | Removing from an ordered non-unique variable takes a single remove-at pin and no value pin unless duplicates are removed; otherwise a value pin and no remove-at pin. | RemoveVariableValueAction | static | 16.14.47.6 Constraints | formal: RemoveVariableValueAction::removeAt_and_value |
| UML-ACN-117 | must | Reply value pins match the out, inout and return parameters of the operation in the reply-to-call trigger's event, in number, type, ordering and multiplicity. | ReplyAction | partial | 16.14.48.5 Constraints | formal: ReplyAction::pins_match_parameter |
| UML-ACN-118 | must | The event of the reply-to-call trigger is a call event. | ReplyAction | static | 16.14.48.5 Constraints | formal: ReplyAction::event_on_reply_to_call_trigger |
| UML-ACN-119 | must | If a port is named, it is a feature of the target pin's type. | SendObjectAction | partial | 16.14.49.5 Constraints | formal: SendObjectAction::type_target_pin |
| UML-ACN-120 | must | Each argument pin has the type, ordering and multiplicity of the matching signal attribute. | SendSignalAction | partial | 16.14.50.5 Constraints | formal: SendSignalAction::type_ordering_multiplicity |
| UML-ACN-121 | must | The argument pins match the signal's attributes in number and order. | SendSignalAction | static | 16.14.50.5 Constraints | formal: SendSignalAction::number_order |
| UML-ACN-122 | must | If a port is named, it is a feature of the target pin's type. | SendSignalAction | partial | 16.14.50.5 Constraints | formal: SendSignalAction::type_target_pin |
| UML-ACN-123 | must | The object pin has multiplicity 1..1. | StartClassifierBehaviorAction | static | 16.14.52.5 Constraints | formal: StartClassifierBehaviorAction::multiplicity |
| UML-ACN-124 | must | If the object pin has a type, that type or an ancestor has a classifier behavior. | StartClassifierBehaviorAction | partial | 16.14.52.5 Constraints | formal: StartClassifierBehaviorAction::type_has_classifier |
| UML-ACN-125 | must | The object pin has multiplicity 1..1. | StartObjectBehaviorAction | static | 16.14.53.6 Constraints | formal: StartObjectBehaviorAction::multiplicity_of_object |
| UML-ACN-126 | must | The object pin's type is a behavior or a behaviored classifier with a classifier behavior. | StartObjectBehaviorAction | partial | 16.14.53.6 Constraints | formal: StartObjectBehaviorAction::type_of_object |
| UML-ACN-127 | must | A start-object-behavior action names no port. | StartObjectBehaviorAction | static | 16.14.53.6 Constraints | formal: StartObjectBehaviorAction::no_onport |
| UML-ACN-128 | must | The object pin has multiplicity 1..1. | StructuralFeatureAction | static | 16.14.54.6 Constraints | formal: StructuralFeatureAction::multiplicity |
| UML-ACN-129 | must | The feature is owned or inherited by the object pin's type, or is an owned end of a binary association whose opposite end's type the pin's type conforms to. | StructuralFeatureAction | partial | 16.14.54.6 Constraints | formal: StructuralFeatureAction::object_type |
| UML-ACN-130 | must | The feature is visible to the object performing the action. | StructuralFeatureAction | static | 16.14.54.6 Constraints | formal: StructuralFeatureAction::visibility |
| UML-ACN-131 | must | The structural feature is not static. | StructuralFeatureAction | static | 16.14.54.6 Constraints | formal: StructuralFeatureAction::not_static |
| UML-ACN-132 | must | The structural feature has exactly one featuring classifier. | StructuralFeatureAction | static | 16.14.54.6 Constraints | formal: StructuralFeatureAction::one_featuring_classifier |
| UML-ACN-133 | must | Edges leaving a structured node's output pins go to targets outside it. | StructuredActivityNode | static | 16.14.55.8 Constraints | formal: StructuredActivityNode::output_pin_edges |
| UML-ACN-134 | must | A structured node's edges are those whose source and target are inside it and not both inside a deeper nested structured node. | StructuredActivityNode | static | 16.14.55.8 Constraints | formal: StructuredActivityNode::edges |
| UML-ACN-135 | must | Edges entering a structured node's input pins come from sources outside it. | StructuredActivityNode | static | 16.14.55.8 Constraints | formal: StructuredActivityNode::input_pin_edges |
| UML-ACN-136 | must | The input pins have multiplicity 1..1. | TestIdentityAction | static | 16.14.56.5 Constraints | formal: TestIdentityAction::multiplicity |
| UML-ACN-137 | must | The input pins have no type. | TestIdentityAction | static | 16.14.56.5 Constraints | formal: TestIdentityAction::no_type |
| UML-ACN-138 | must | The result pin is typed Boolean. | TestIdentityAction | partial | 16.14.56.5 Constraints | formal: TestIdentityAction::result_is_boolean |
| UML-ACN-139 | must | The unmarshall type has at least one structural feature. | UnmarshallAction | static | 16.14.57.5 Constraints | formal: UnmarshallAction::structural_feature |
| UML-ACN-140 | must | The number of result pins equals the number of the unmarshall type's attributes. | UnmarshallAction | static | 16.14.57.5 Constraints | formal: UnmarshallAction::number_of_result |
| UML-ACN-141 | must | Each result pin is compatible with the matching attribute in type, ordering and multiplicity. | UnmarshallAction | partial | 16.14.57.5 Constraints | formal: UnmarshallAction::type_ordering_and_multiplicity |
| UML-ACN-142 | must | The object pin has multiplicity 1..1. | UnmarshallAction | static | 16.14.57.5 Constraints | formal: UnmarshallAction::multiplicity_of_object |
| UML-ACN-143 | must | The object pin's type conforms to the unmarshall type. | UnmarshallAction | partial | 16.14.57.5 Constraints | formal: UnmarshallAction::object_type |
| UML-ACN-144 | must | A value pin has no incoming edges. | ValuePin | static | 16.14.58.5 Constraints | formal: ValuePin::no_incoming_edges |
| UML-ACN-145 | must | The type of the value specification conforms to the value pin's type. | ValuePin | partial | 16.14.58.5 Constraints | formal: ValuePin::compatible_type |
| UML-ACN-146 | must | The result pin of a value specification action has multiplicity 1..1. | ValueSpecificationAction | static | 16.14.59.5 Constraints | formal: ValueSpecificationAction::multiplicity |
| UML-ACN-147 | must | The type of the value specification conforms to the type of the result pin. | ValueSpecificationAction | partial | 16.14.59.5 Constraints | formal: ValueSpecificationAction::compatible_type |
| UML-ACN-148 | must | A variable action is in the scope of its variable. | VariableAction | static | 16.14.60.6 Constraints | formal: VariableAction::scope_of_variable |
| UML-ACN-149 | must | At least one end must be visible from the context classifier of the write link action. | WriteLinkAction | static | 16.14.61.5 Constraints | formal: WriteLinkAction::allow_access |
| UML-ACN-150 | must | The result pin has multiplicity 1..1. | WriteStructuralFeatureAction | static | 16.14.62.6 Constraints | formal: WriteStructuralFeatureAction::multiplicity_of_result |
| UML-ACN-151 | must | The value pin's type conforms to the type of the structural feature. | WriteStructuralFeatureAction | partial | 16.14.62.6 Constraints | formal: WriteStructuralFeatureAction::type_of_value |
| UML-ACN-152 | must | The value pin has multiplicity 1..1. | WriteStructuralFeatureAction | static | 16.14.62.6 Constraints | formal: WriteStructuralFeatureAction::multiplicity_of_value |
| UML-ACN-153 | must | The result pin has the same type as the object pin. | WriteStructuralFeatureAction | partial | 16.14.62.6 Constraints | formal: WriteStructuralFeatureAction::type_of_result |
| UML-ACN-154 | must | The value pin's type conforms to the type of the variable. | WriteVariableAction | partial | 16.14.63.6 Constraints | formal: WriteVariableAction::value_type |
| UML-ACN-155 | must | The value pin has multiplicity 1..1. | WriteVariableAction | static | 16.14.63.6 Constraints | formal: WriteVariableAction::multiplicity |

## INT: Interactions

| Id | Strength | Rule | Applies to | Checkable | Section | Source |
|---|---|---|---|---|---|---|
| UML-INT-001 | must | The action an action execution specification refers to is owned by the same interaction that owns the specification. | ActionExecutionSpecification | static | 17.12.1.5 Constraints | formal: ActionExecutionSpecification::action_referenced |
| UML-INT-002 | must | For a break operator, the operand covers all lifelines covered by the enclosing fragment. | CombinedFragment | static | 17.12.3.7 Constraints | formal: CombinedFragment::break |
| UML-INT-003 | must | The consider and ignore operators are used only by the consider-ignore fragment subtype. | CombinedFragment | static | 17.12.3.7 Constraints | formal: CombinedFragment::consider_and_ignore |
| UML-INT-004 | must | A combined fragment with operator opt, loop, break, assert or neg has exactly one operand. | CombinedFragment | static | 17.12.3.7 Constraints | formal: CombinedFragment::opt_loop_break_neg |
| UML-INT-005 | must | A consider-ignore fragment's operator is consider or ignore. | ConsiderIgnoreFragment | static | 17.12.4.5 Constraints | formal: ConsiderIgnoreFragment::consider_or_ignore |
| UML-INT-006 | must | The named elements of a consider-ignore fragment are of a kind that can be a message signature: an operation or a signal. | ConsiderIgnoreFragment | static | 17.12.4.5 Constraints | formal: ConsiderIgnoreFragment::type |
| UML-INT-007 | must | A continuation is the very first or the very last fragment in the enclosing operand. | Continuation | static | 17.12.5.5 Constraints | formal: Continuation::first_or_last_interaction_fragment |
| UML-INT-008 | must | Continuations with the same name (in interactions with the same context) cover corresponding lifelines. | Continuation | partial | 17.12.5.5 Constraints | formal: Continuation::same_name |
| UML-INT-009 | must | A continuation is global: it covers all lifelines covered by the enclosing operand. | Continuation | static | 17.12.5.5 Constraints | formal: Continuation::global |
| UML-INT-010 | must | No other occurrence may appear below a destruction occurrence on the same lifeline within an operand. | DestructionOccurrenceSpecification | static | 17.12.6.4 Constraints | formal: DestructionOccurrenceSpecification::no_occurrence_specifications_below |
| UML-INT-011 | must | The start and finish occurrences of an execution specification are on the same lifeline. | ExecutionSpecification | static | 17.12.8.6 Constraints | formal: ExecutionSpecification::same_lifeline |
| UML-INT-012 | must | An actual gate has exactly one matching formal gate in the referred interaction. | Gate | static | 17.12.9.5 Constraints | formal: Gate::actual_gate_matched |
| UML-INT-013 | must | A gate inside a combined fragment has exactly one matching gate outside it. | Gate | static | 17.12.9.5 Constraints | formal: Gate::inside_cf_matched |
| UML-INT-014 | must | A gate outside a combined fragment has a matching gate inside it for each operand (alt) or exactly one (other operators). | Gate | static | 17.12.9.5 Constraints | formal: Gate::outside_cf_matched |
| UML-INT-015 | must | No two formal gates of an interaction have the same name. | Gate | static | 17.12.9.5 Constraints | formal: Gate::formal_gate_distinguishable |
| UML-INT-016 | must | No two actual gates of an interaction use have the same name. | Gate | static | 17.12.9.5 Constraints | formal: Gate::actual_gate_distinguishable |
| UML-INT-017 | must | No two outside gates of a combined fragment have the same name. | Gate | static | 17.12.9.5 Constraints | formal: Gate::outside_cf_gate_distinguishable |
| UML-INT-018 | must | No two inside gates attached to messages whose other ends are in the same operand have the same name. | Gate | static | 17.12.9.5 Constraints | formal: Gate::inside_cf_gate_distinguishable |
| UML-INT-019 | must | An occurrence cannot be ordered before itself through a chain of general orderings. | GeneralOrdering | static | 17.12.10.5 Constraints | formal: GeneralOrdering::irreflexive_transitive_closure |
| UML-INT-020 | must | An interaction is not contained in another interaction. | Interaction | static | 17.12.11.5 Constraints | formal: Interaction::not_contained |
| UML-INT-021 | must | Minimum and maximum iteration counts appear only on the constraint of a loop combined fragment's operand. | InteractionConstraint | static | 17.12.12.5 Constraints | formal: InteractionConstraint::minint_maxint |
| UML-INT-022 | must | A minimum iteration count evaluates to a non-negative integer. | InteractionConstraint | partial | 17.12.12.5 Constraints | formal: InteractionConstraint::minint_non_negative |
| UML-INT-023 | must | A maximum iteration count evaluates to a positive integer. | InteractionConstraint | partial | 17.12.12.5 Constraints | formal: InteractionConstraint::maxint_positive |
| UML-INT-024 | must | Dynamic variables used in the constraint belong to the connectable element of the covered lifeline. | InteractionConstraint | partial | 17.12.12.5 Constraints | formal: InteractionConstraint::dynamic_variables |
| UML-INT-025 | note | The constraint may refer to global or write-once data. | InteractionConstraint | none | 17.12.12.5 Constraints | formal: InteractionConstraint::global_data |
| UML-INT-026 | must | If a maximum is given, a minimum is given too and the maximum is at least the minimum. | InteractionConstraint | partial | 17.12.12.5 Constraints | formal: InteractionConstraint::maxint_greater_equal_minint |
| UML-INT-027 | must | A guard refers only to values local to its lifeline or global to the interaction. | InteractionOperand | partial | 17.12.14.5 Constraints | formal: InteractionOperand::guard_contain_references |
| UML-INT-028 | must | A guard is placed directly before the first occurrence of its operand. | InteractionOperand | static | 17.12.14.5 Constraints | formal: InteractionOperand::guard_directly_prior |
| UML-INT-029 | must | Actual gates of an interaction use match the formal gates of the referred interaction by name and corresponding messages. | InteractionUse | static | 17.12.16.6 Constraints | formal: InteractionUse::gates_match |
| UML-INT-030 | must | Arguments of an interaction use are constants, parameters of the enclosing interaction, or attributes of the classifier owning it. | InteractionUse | partial | 17.12.16.6 Constraints | formal: InteractionUse::arguments_are_constants |
| UML-INT-031 | must | The return value recipient is a property of a connectable element represented by a lifeline that the use covers. | InteractionUse | static | 17.12.16.6 Constraints | formal: InteractionUse::returnValueRecipient_coverage |
| UML-INT-032 | must | The arguments of an interaction use correspond to the parameters of the referred interaction. | InteractionUse | partial | 17.12.16.6 Constraints | formal: InteractionUse::arguments_correspond_to_parameters |
| UML-INT-033 | must | The type of the return value corresponds to the type of the return value recipient. | InteractionUse | partial | 17.12.16.6 Constraints | formal: InteractionUse::returnValue_type_recipient_correspondence |
| UML-INT-034 | must | An interaction use covers all lifelines of the enclosing interaction that are common with lifelines of the referred interaction. | InteractionUse | partial | 17.12.16.6 Constraints | formal: InteractionUse::all_lifelines |
| UML-INT-035 | must | A lifeline has a selector exactly when the connectable element it represents is multivalued. | Lifeline | static | 17.12.17.5 Constraints | formal: Lifeline::selector_specified |
| UML-INT-036 | must | A lifeline common to lifelines in interactions referred to by two uses in one enclosing interaction is common to a lifeline in the enclosing interaction. | Lifeline | partial | 17.12.17.5 Constraints | formal: Lifeline::interaction_uses_share_lifeline |
| UML-INT-037 | must | The classifier that contains the represented connectable element is the same as, or an ancestor of, the classifier containing the enclosing interaction. | Lifeline | static | 17.12.17.5 Constraints | formal: Lifeline::same_classifier |
| UML-INT-038 | must | A lifeline selector is a literal string or a literal integer. | Lifeline | static | 17.12.17.5 Constraints | formal: Lifeline::selector_int_or_string |
| UML-INT-039 | must | If a message's send and receive events are on the same lifeline, the send is ordered before the receive. | Message | static | 17.12.18.7 Constraints | formal: Message::sending_receiving_message_event |
| UML-INT-040 | must | Arguments of a message are attributes of the sending lifeline, constants, symbolic values, parameters of the enclosing interaction, or attributes of the class owning the interaction. | Message | partial | 17.12.18.7 Constraints | formal: Message::arguments |
| UML-INT-041 | must | Both ends of a message are enclosed in the same fragment, so messages do not cross combined fragment or operand boundaries. | Message | static | 17.12.18.7 Constraints | formal: Message::cannot_cross_boundaries |
| UML-INT-042 | must | When the signature is a signal, the arguments correspond to the signal's attributes. | Message | partial | 17.12.18.7 Constraints | formal: Message::signature_is_signal |
| UML-INT-043 | must | If both message ends are occurrence specifications, the message's connector goes between the parts represented by their lifelines. | Message | static | 17.12.18.7 Constraints | formal: Message::occurrence_specifications |
| UML-INT-044 | must | A message signature refers to an operation (sort synchCall, asynchCall or reply) or to a signal (sort asynchSignal), and the message has the same name as the signature. | Message | static | 17.12.18.7 Constraints | formal: Message::signature_refer_to |
| UML-INT-045 | must | A call message with an operation signature has arguments corresponding to the operation's in and inout parameters. | Message | partial | 17.12.18.7 Constraints | formal: Message::signature_is_operation_request |
| UML-INT-046 | must | A reply message with an operation signature has arguments corresponding to the operation's out, inout and return parameters. | Message | partial | 17.12.18.7 Constraints | formal: Message::signature_is_operation_reply |
| UML-INT-047 | must | Decomposition commutes: where a lifeline is decomposed and an interaction use covers it, the referred interaction decomposes it by referencing the use's counterpart. | PartDecomposition | partial | 17.12.24.4 Constraints | formal: PartDecomposition::commutativity_of_decomposition |
| UML-INT-048 | must | A decomposed lifeline's sequence of constructs is matched one-to-one, in order, by constructs in the decomposition (fragments by extra-global fragments, uses by global uses, plain occurrences by formal gates). | PartDecomposition | partial | 17.12.24.4 Constraints | formal: PartDecomposition::assume |
| UML-INT-049 | must | Part decomposition applies only to parts of internal structures, not to parts of collaborations. | PartDecomposition | static | 17.12.24.4 Constraints | formal: PartDecomposition::parts_of_internal_structures |

## UC: Use cases

| Id | Strength | Rule | Applies to | Checkable | Section | Source |
|---|---|---|---|---|---|---|
| UML-UC-001 | must | An actor can have associations only to use cases, components and classes, and those associations are binary. | Actor | static | 18.2.1.4 Constraints | formal: Actor::associations |
| UML-UC-002 | must | An actor must have a name. | Actor | static | 18.2.1.4 Constraints | formal: Actor::must_have_name |
| UML-UC-003 | must | The extension points an extend refers to belong to the use case being extended. | Extend | static | 18.2.2.5 Constraints | formal: Extend::extension_points |
| UML-UC-004 | must | An extension point must have a name. | ExtensionPoint | static | 18.2.3.5 Constraints | formal: ExtensionPoint::must_have_name |
| UML-UC-005 | must | Use cases can take part only in binary associations. | UseCase | static | 18.2.5.6 Constraints | formal: UseCase::binary_associations |
| UML-UC-006 | must | A use case cannot have an association to another use case with the same subject. | UseCase | static | 18.2.5.6 Constraints | formal: UseCase::no_association_to_use_case |
| UML-UC-007 | must | A use case cannot include use cases that directly or indirectly include it. | UseCase | static | 18.2.5.6 Constraints | formal: UseCase::cannot_include_self |
| UML-UC-008 | must | A use case must have a name. | UseCase | static | 18.2.5.6 Constraints | formal: UseCase::must_have_name |

## DEP: Deployments

| Id | Strength | Rule | Applies to | Checkable | Section | Source |
|---|---|---|---|---|---|---|
| UML-DEP-001 | must | The ends of a communication path are typed by deployment targets. | CommunicationPath | static | 19.5.2.4 Constraints | formal: CommunicationPath::association_ends |
| UML-DEP-002 | must | The deployment target of a deployment specification is an execution environment. | DeploymentSpecification | static | 19.5.5.6 Constraints | formal: DeploymentSpecification::deployment_target |
| UML-DEP-003 | must | The deployed elements of a target involved in a deployment with a deployment specification are components. | DeploymentSpecification | static | 19.5.5.6 Constraints | formal: DeploymentSpecification::deployed_elements |
| UML-DEP-004 | must | The internal structure of a node, if defined, consists only of parts typed by nodes. | Node | static | 19.5.10.6 Constraints | formal: Node::internal_structure |

## INF: Information flows

| Id | Strength | Rule | Applies to | Checkable | Section | Source |
|---|---|---|---|---|---|---|
| UML-INF-001 | must | The sources and targets of an information flow conform to those of its realizing relationships (or the reverse). | InformationFlow | partial | 20.2.1.5 Constraints | formal: InformationFlow::must_conform |
| UML-INF-002 | must | Sources and targets of an information flow are actors, nodes, use cases, artifacts, classes, components, ports, properties, interfaces, packages, activity nodes, activity partitions, behaviors or instance specifications (unless its classifier is a relationship). | InformationFlow | static | 20.2.1.5 Constraints | formal: InformationFlow::sources_and_targets_kind |
| UML-INF-003 | must | An information flow conveys only classifiers that are allowed to represent an information item. | InformationFlow | static | 20.2.1.5 Constraints | formal: InformationFlow::convey_classifiers |
| UML-INF-004 | must | The sources and targets of an information item's flows are subsets of those of the item it represents, and only classes, interfaces, information items, signals and components can realize it. | InformationItem | partial | 20.2.2.5 Constraints | formal: InformationItem::sources_and_targets |
| UML-INF-005 | must | An information item has no features, no generalizations and no associations. | InformationItem | static | 20.2.2.5 Constraints | formal: InformationItem::has_no |
| UML-INF-006 | must | An information item cannot be instantiated. | InformationItem | static | 20.2.2.5 Constraints | formal: InformationItem::not_instantiable |

## MRG: Package merge

| Id | Strength | Rule | Applies to | Checkable | Section | Source |
|---|---|---|---|---|---|---|
| UML-MRG-001 | must | There are no cycles in the graph of package merges. |  | static (package-merge) | 12.2.3.3 rule 1 | prose: merge-no-cycles |
| UML-MRG-002 | must | A package cannot merge a package that contains it, directly or indirectly. |  | static (package-merge) | 12.2.3.3 rule 2 | prose: merge-not-container |
| UML-MRG-003 | must | A package cannot merge a package that it contains, directly or indirectly. |  | static (package-merge) | 12.2.3.3 rule 3 | prose: merge-not-contained |
| UML-MRG-004 | must | A merged element whose metatype is not Package, Class, DataType, Property, Association, Operation, Constraint, Enumeration or EnumerationLiteral cannot have a receiving element with the same name and metatype unless that receiving element is an exact copy of it. |  | partial (package-merge) | 12.2.3.3 rule 4 | prose: merge-unlisted-metatype-copy |
| UML-MRG-005 | must | A package merge is valid only if all the merge constraints needed to perform it are satisfied; otherwise the merge is ill formed and the model is invalid. |  | partial (package-merge) | 12.2.3.3 rule 5 | prose: merge-valid-iff-constraints |
| UML-MRG-006 | must | Matching typed elements (properties, parameters) have conforming types: the same type or, for classes and data types, a common supertype; for other types, the same type. |  | partial (package-merge) | 12.2.3.3 rule 6 | prose: merge-conforming-types |
| UML-MRG-007 | must | A receiving element has no explicit references to any merged element. |  | partial (package-merge) | 12.2.3.3 rule 7 | prose: merge-no-explicit-reference |
| UML-MRG-008 | must | Redefinitions of matching redefinable elements must not conflict. |  | partial (package-merge) | 12.2.3.3 rule 8 | prose: merge-redefinitions-not-conflicting |
| UML-MRG-009 | must | Every classifier in the merged package and in the receiving package has a non-empty qualified name and can be told apart from the others in its package. |  | static (package-merge) | 12.2.3.4 | prose: merge-package-classifiers-named |
| UML-MRG-010 | must | Matching properties have the same isStatic and the same isUnique, and their constraints do not conflict. |  | partial (package-merge) | 12.2.3.6 | prose: merge-property-static-unique |
| UML-MRG-011 | must | For merging binary associations, the receiving end must be composite if the matching merged end is, and must be owned by the association if the matching merged end is. |  | static (package-merge) | 12.2.3.7 | prose: merge-association-binary-ends |
| UML-MRG-012 | must | A receiving operation has isQuery true if the matching merged operation does. |  | static (package-merge) | 12.2.3.8 | prose: merge-operation-query |
| UML-MRG-013 | must | Matching enumeration literals appear in the same order. |  | static (package-merge) | 12.2.3.9 | prose: merge-literal-order |
| UML-MRG-014 | must | Constraints of merged and receiving elements must be mutually non-contradictory. |  | partial (package-merge) | 12.2.3.10 | prose: merge-constraints-consistent |
| UML-MRG-015 | note | The merge result is defined by rules: visibility private only if both are private; abstract and final only if both are; derived if either is; lower bound the lesser; upper bound the greater; stereotypes from either side kept; read-only only if both; ordered if either; unique only if both. |  | none (package-merge) | 12.2.3.3 (transformation rules) | prose: merge-results |

## PRF: Profiles

| Id | Strength | Rule | Applies to | Checkable | Section | Source |
|---|---|---|---|---|---|---|
| UML-PRF-001 | must | Applying, in strict mode, profiles whose available metaclass sets do not overlap is invalid. |  | partial (profile-applied) | 12.3.3.1.1 | prose: profile-strict-disjoint |
| UML-PRF-002 | must | Except for stereotypes and extensions, every type defined or imported in a profile is a class, association, data type, primitive type or enumeration as in the CMOF-compliant subset; no other specialization is allowed. |  | static | 12.3.3.1.1 | prose: profile-types-restricted |
| UML-PRF-003 | must | Profile-defined types are used only as the type of properties in the profile or as the general classifier of another profile-defined type, never as types of elements in the models the profile is applied to. |  | static | 12.3.3.1.1 | prose: profile-types-use |
| UML-PRF-004 | must | A profile-defined binary association has at most one composite end; its other end has aggregation none. |  | static | 12.3.3.1.1 | prose: profile-association-one-composite |
| UML-PRF-005 | must | A property of a stereotype or profile-defined class can be composite only if its type is a profile-defined class; a property typed by a profile-defined data type, primitive type or enumeration has aggregation none. |  | static | 12.3.3.1.1 | prose: profile-composite-property-type |
| UML-PRF-006 | must | A composite property of a stereotype cannot be typed by a stereotype or by a metaclass. |  | static | 12.3.3.4 | prose: stereotype-composite-not-stereotype-or-metaclass |
| UML-PRF-007 | must | A stereotype's association has an owned attribute typed by the opposite class; where the opposite class is not a stereotype, the opposite end is owned by the association. |  | static | 12.3.3.1.1 | prose: stereotype-binary-opposite |
| UML-PRF-008 | must | A stereotype extends a metaclass through an Extension, never by generalization. |  | static | 12.3.3.4 | prose: stereotype-extends-by-extension |
| UML-PRF-009 | must | A stereotype can extend only a metaclass referenced by a metaclass reference, or contained in a package referenced by a metamodel reference, of the closest profile that contains the stereotype. |  | static | 12.3.3.4 | prose: stereotype-extensible-metaclasses |
| UML-PRF-010 | must | A stereotype that extends several metaclasses is applied to exactly one instance of one of them at a time. |  | static (profile-applied) | 12.3.3.4 | prose: stereotype-single-instance-at-a-time |
| UML-PRF-011 | must | The same stereotype, or a subtype of it, is never applied twice to the same element. |  | static (profile-applied) | 12.3.3.6 | prose: stereotype-not-applied-twice |
| UML-PRF-012 | must | If an extension is required, an instance of the stereotype is applied to every instance of the extended metaclass in a model the profile is applied to, otherwise the model is not well formed. |  | static (profile-applied) | 12.3.3.3; 12.3.3.6 | prose: stereotype-required-extension |
| UML-PRF-013 | must | A conforming tool supports stereotype owned attributes; owned operations and behaviors are optional. |  | none | 12.3.3.4 | prose: stereotype-attributes-supported |
| UML-PRF-014 | must | A profile nested in another profile and applied by itself states its own metaclass and metamodel references if it contains stereotypes; references are not inherited from the containing profile. |  | static (profile-applied) | 12.3.3.3 | prose: nested-profile-references |
| UML-PRF-015 | note | Applying a profile applies its nested and imported profiles; only public stereotypes of an applied profile can be applied to elements. |  | none (profile-applied) | 12.3.3.3 | prose: profile-application-recursive |
| UML-PRF-016 | note | Removing an applied profile deletes the instances of its stereotypes and leaves the rest of the model intact. |  | none (profile-applied) | 12.3.3.3 | prose: profile-removal |
| UML-PRF-017 | note | The visibility and alias of an ElementImport used as a metaclass reference are ignored. |  | none | 12.3.3.1.1 | prose: metaclass-reference-ignores-visibility |
| UML-PRF-018 | note | Reserved image formats are SVG, GIF, PNG, JPG, WMF, EMF and BMP, and `MIME:` followed by a MIME type. |  | none | 12.3.3.5 | prose: image-format |
| UML-PRF-019 | must | A package's packaged elements have public or private visibility only; protected and package visibility are not allowed. |  | static | 12.2.4 | prose: package-visibility-two-values |
| UML-PRF-020 | should | A package URI should be unique and unchanged once assigned. |  | partial | 12.2.3.1 | prose: package-uri |

## STD: Standard profile

| Id | Strength | Rule | Applies to | Checkable | Section | Source |
|---|---|---|---|---|---|---|
| UML-STD-001 | must | A conforming tool supports all the stereotypes of the Standard Profile. |  | none | 22.1 | prose: standard-profile-support |
| UML-STD-002 | must | A standard stereotype is applied only to elements of the metaclass listed for it in Table 22.1 (for example Auxiliary and Focus to Class; Realization and Specification to Classifier; Document, Executable, File, Library, Script and Source to Artifact; Entity, Implement, Process, Service, Subsystem and BuildComponent to Component; Framework and ModelLibrary to Package; Metamodel and SystemModel to Model; Call, Create, Instantiate, Responsibility and Send to Usage; Derive, Refine and Trace to Abstraction; Create and Destroy also to BehavioralFeature). |  | static | 22.3 | prose: standard-stereotype-applies-to |
| UML-STD-003 | must | A Call usage has an operation as its client and an operation as its supplier (or the classes that contain them). |  | static | 22.3 | prose: std-call |
| UML-STD-004 | must | A Send usage has an operation as its client and a signal as its supplier. |  | static | 22.3 | prose: std-send |
| UML-STD-005 | must | A Create usage has a classifier as its client and the classifier it creates as its supplier. |  | static | 22.3 | prose: std-create-usage |
| UML-STD-006 | must | An Instantiate usage is between classifiers: operations on the client create instances of the supplier. |  | static | 22.3 | prose: std-instantiate |
| UML-STD-007 | note | Document, Executable, Library, Script and Source are subclasses of File. |  | none | 22.3 | prose: std-file-subclasses |
| UML-STD-008 | must | A model library does not contain profiles or stereotypes (it may contain profile applications and stereotype applications). |  | static | 22.3 | prose: std-modellibrary |

## SEM: Other prose rules

| Id | Strength | Rule | Applies to | Checkable | Section | Source |
|---|---|---|---|---|---|---|
| UML-SEM-001 | must | An association end may be shared or composite only if the association is binary and the other end is neither shared nor composite. |  | static | 11.5.3.1 | prose: association-aggregation-ends |
| UML-SEM-002 | must | The attributes of an association class, its member ends, and the opposite ends of associations connected to it all have distinct names. |  | static | 11.5.3.2 | prose: association-class-names |
| UML-SEM-003 | must | An association class cannot be the general classifier of an Association or of a Class (it cannot be generalized by them). |  | static | 11.5.3.2 | prose: association-class-no-generalization-target |
| UML-SEM-004 | must | If the lower bounds of the ends opposite a qualified end are not zero, the qualifier values must form a finite set, for example because they are enumerations. |  | partial | 11.5.3.1 | prose: qualifier-finite |
| UML-SEM-005 | must | Navigation arrows shown on a link between instance specifications agree with the navigability of the association ends. |  | static | 9.8.4 | prose: link-navigation-agrees |
| UML-SEM-006 | note | The old convention that non-navigable ends are owned by the association and navigable ends by the opposite classifier is deprecated; aggregation, navigability and end ownership are separate; ends owned by a class are always navigable. |  | none | 11.5.4 | prose: navigability-ownership-convention |
| UML-SEM-007 | must | A non-reentrant behavior is not invoked again while a previous execution is uncompleted. |  | runtime (execution) | 13.2.3.1 | prose: behavior-nonreentrant |
| UML-SEM-008 | must | When a behavior with exception output parameters completes, either none of them has a value or exactly one does and no other output parameter has a value. |  | runtime (execution) | 13.2.3.2 | prose: behavior-exception-outputs |
| UML-SEM-009 | must | A behavior with input parameter sets accepts inputs from only one set per execution; with output sets it posts outputs to only one set. |  | runtime (execution) | 13.2.3.2 | prose: behavior-parameterset-one |
| UML-SEM-010 | must | A behavior is the method of at most one behavioral feature, called its specification. |  | static | 13.2.3.5 | prose: behavior-method-of-one-feature |
| UML-SEM-011 | should | A method has parameters corresponding to the parameters of its operation, or to the attributes of the signal of its reception; how they are matched (exact, covariant, contravariant) is not fixed. |  | partial | 13.2.3.5 | prose: behavior-method-parameters |
| UML-SEM-012 | note | Method resolution is not mandated; the simple object-oriented process looks up the generalization hierarchy and is ill formed if no method or more than one is found along different paths. |  | none | 13.2.3.5 | prose: behavior-method-resolution |
| UML-SEM-013 | must | A relative time event is used in the context of a trigger. |  | static | 13.3.3 | prose: timeevent-relative-in-trigger |
| UML-SEM-014 | must | A history pseudostate (deep or shallow) can be defined only in a composite state. |  | static | 14.2.3.7 | prose: history-only-composite |
| UML-SEM-015 | must | In each region of a state machine or composite state that owns an entry point, there is at most one transition from the entry point to a vertex in that region. |  | static | 14.2.3.7 | prose: entrypoint-one-transition-per-region |
| UML-SEM-016 | must | Guards on transitions from an entry point must evaluate to true for the specification to be well formed. |  | runtime (execution) | 14.2.3.4.7 | prose: entrypoint-guards-true |
| UML-SEM-017 | must | The predefined guard else is associated with at most one outgoing transition of its source. |  | static | 14.2.3.8.4 | prose: else-guard-once |
| UML-SEM-018 | must | The target of a local transition differs from its source. |  | static | 14.2.3.8.1 | prose: local-target-differs |
| UML-SEM-019 | must | A transition from one region to another region of the same immediately enclosing composite state is not allowed. |  | static | 14.2.3.9.4 | prose: no-cross-region-transition |
| UML-SEM-020 | must | A state machine that is the method of a behavioral feature has parameters that match the parameters of the feature. |  | partial | 14.2.3.1 | prose: statemachine-method-parameters |
| UML-SEM-021 | must | A state can be redefined only by a state. |  | static | 14.3.3.3 | prose: redef-state |
| UML-SEM-022 | must | A submachine state can be redefined only by a submachine state whose submachine extends the redefined state's submachine. |  | static | 14.3.3.3 | prose: redef-submachine-state |
| UML-SEM-023 | must | A FinalState can be redefined only by a FinalState. |  | static | 14.3.3.3 | prose: redef-final-state |
| UML-SEM-024 | must | A pseudostate can be redefined only by a pseudostate of the same kind; a redefined connection point must be redefined by a connection point of a redefinition of the owning state. |  | static | 14.3.3.3 | prose: redef-pseudostate |
| UML-SEM-025 | must | A connection point reference can be redefined only by a connection point reference whose state redefines the original state. |  | static | 14.3.3.3 | prose: redef-connection-point-reference |
| UML-SEM-026 | must | The source of a redefining transition redefines the source of the redefined transition; its target either redefines the target or is an added vertex. |  | static | 14.3.3.4 | prose: redef-transition-source |
| UML-SEM-027 | note | If a protocol state machine is read as executable, the legal transitions for feature invocations match the triggered transitions exactly or a run-time exception occurs. |  | runtime (execution) | 14.4.3.1 | prose: protocol-executable |
| UML-SEM-028 | must | All incoming and outgoing edges of an executable node are control flows (actions pass objects through pins). |  | static | 15.2.3.2 | prose: executable-node-control-edges |
| UML-SEM-029 | must | The weight of an activity edge is a value specification that evaluates to a non-zero unlimited natural number. |  | partial | 15.2.4 | prose: edge-weight |
| UML-SEM-030 | must | Each activity edge connector label appears exactly twice on a diagram; one end has exactly one incoming edge and the other exactly one outgoing edge of the same flow type. |  | static | 15.2.4 | prose: edge-connector-paired |
| UML-SEM-031 | must | The predefined guard else is used on at most one outgoing edge of a decision node. |  | static | 15.3.3.6 | prose: decision-else-once |
| UML-SEM-032 | should | At most one guard of a decision node's outgoing edges should be true for each token. |  | none | 15.3.3.6 | prose: decision-guards-exclusive |
| UML-SEM-033 | must | A decision input behavior has no side effects. |  | none | 15.3.3.6 | prose: decision-input-no-side-effects |
| UML-SEM-034 | must | Selection and transformation behaviors on object flows have no side effects; a selection behavior's input is an unordered, non-unique 0..* bag and its output has upper bound 1. |  | none | 15.2.3.4 | prose: selection-transformation-no-side-effects |
| UML-SEM-035 | should | A merge node is shown with two or more incoming edges. |  | static | 15.3.4.3 | prose: merge-multiple-incoming |
| UML-SEM-036 | must | A fork node has a single incoming edge; a join node has a single outgoing edge. |  | static | 15.3.4.2 | prose: join-fork-single-edge |
| UML-SEM-037 | must | Values held by a variable conform to the variable's type, and the variable's multiplicity bounds the number of values held. |  | partial | 15.2.3.5 | prose: variable-values-conform |
| UML-SEM-038 | should | Actions that read and write the same variable are sequenced by control flow to avoid races. |  | none | 15.2.3.5 | prose: variable-sequence-access |
| UML-SEM-039 | must | When an activity with no streaming outputs completes, each output parameter node holds at least as many non-null object tokens as the parameter's lower bound. |  | runtime (execution) | 15.2.3.6 | prose: activity-output-tokens |
| UML-SEM-040 | should | Exception parameters on an activity are used only when aborting all flows is intended (not, for example, with isSingleExecution true). |  | none | 15.2.3.6 | prose: activity-exception-parameter-use |
| UML-SEM-041 | note | The first token to reach an activity final node ends the whole activity; a flow final node ends only its own flow. |  | runtime (execution) | 15.3.3.2 | prose: activity-final-terminates |
| UML-SEM-042 | must | If a gate of an inner combined fragment is used in one operand of an alt fragment, a gate with the same name is used in every operand. |  | static | 17.6.3.7 | prose: alt-gates-every-operand |
| UML-SEM-043 | must | The chosen operand of an alt fragment has a guard that is true at that point. |  | runtime (execution) | 17.6.3.7 | prose: alt-guard-true |
| UML-SEM-044 | must | A loop iterates at least minint and at most maxint times; a separate guard that evaluates to false ends it regardless of minint. |  | runtime (execution) | 17.6.3.17 | prose: loop-iteration |
| UML-SEM-045 | must | If a message's signature is a signal, its sort is asynchSignal and its arguments correspond to the signal's attributes. |  | static | 17.4.3.1 | prose: message-signal-sort |
| UML-SEM-046 | must | Each argument of a reply message is an expression with at most one operand. |  | static | 17.4.3.1 | prose: message-reply-arguments |
| UML-SEM-047 | must | In a request message label, either every argument is named or none is; named arguments need a signature. |  | static | 17.4.4.1 | prose: message-label-named-arguments |
| UML-SEM-048 | must | When a message has a signature, an argument is provided for every in and inout parameter or signal attribute (a hyphen is the wildcard). |  | static | 17.4.4.1 | prose: message-label-argument-for-each |
| UML-SEM-049 | must | A delete message ends in a destruction occurrence. |  | static | 17.4.4.1 | prose: message-delete-destruction |
| UML-SEM-050 | must | A lifeline identifier is not empty. |  | static | 17.3.4.1 | prose: lifeline-ident-not-empty |
| UML-SEM-051 | must | Messages at matched gates correspond: same name, message sort, signature and direction. |  | static | 17.4.3.5 | prose: gates-correspond |
| UML-SEM-052 | must | In an interaction overview diagram, branching and joining of branches are properly nested. |  | static | 17.10.1 | prose: overview-properly-nested |
| UML-SEM-053 | must | In an interaction overview diagram the object nodes of an activity diagram are replaced by inline interactions or interaction uses. |  | static | 17.10.1 | prose: overview-nodes |
| UML-SEM-054 | must | A tool makes it possible to determine the constrained element of a constraint shown as text. |  | none | 7.6.4 | prose: constraint-determinable |
| UML-SEM-055 | note | A use case's functionality is completed for the use case to complete; it is complete when the subject is in a state where no further interaction is implied. |  | runtime (execution) | 18.1.3.1 | prose: usecase-complete |
| UML-SEM-056 | must | A deployment specification is associated only with deployment targets that are execution environments. |  | static | 19.2.3 | prose: deployment-spec-target |
| UML-SEM-057 | must | The internal structure of a node consists only of other nodes. |  | static | 19.4.3 | prose: node-structure |
| UML-SEM-058 | must | An information item is realized only by classes (of all kinds), interfaces, signals and other information items. |  | static | 20.1.3 | prose: infoitem-realizers |
| UML-SEM-059 | note | A template parameter list is not empty; it can be hidden in the notation. |  | none | 7.3.4 | prose: template-parameter-syntax |
| UML-SEM-060 | must | A template element cannot be used like a non-template element of the same kind (for example a template class is not the type of a typed element); it is used only to produce bound elements or as part of another template. |  | static | 7.3.3 | prose: template-not-usable-as-nontemplate |
| UML-SEM-061 | note | A partially bound element is still a template, parameterized by the template parameters it leaves unbound; a tool may require complete binding or allow partial binding. |  | none | 7.3.3 | prose: template-partial-binding |
| UML-SEM-062 | must | If a model includes the expanded form of a bound element as well as the bound element, the expanded element has a realization dependency to the bound element. |  | static | 7.3.3 | prose: expanded-bound-element-realization |
| UML-SEM-063 | must | If imports would bring indistinguishable elements into a namespace, they are not added to it and their names must be qualified to be used there. |  | partial | 7.4.3 | prose: import-indistinguishable-qualified |
| UML-SEM-064 | must | Any value a typed element represents is an instance of its type; an untyped element may represent any value. |  | runtime (execution) | 7.5.3 | prose: typed-element-value-in-type |
| UML-SEM-065 | must | The cardinality of the collection a multiplicity element represents is within its lower and upper bounds. |  | runtime (execution) | 7.5.3 | prose: multiplicity-cardinality |
| UML-SEM-066 | must | If isUnique is true, no two values in the collection are equal. |  | runtime (execution) | 7.5.3 | prose: multiplicity-unique-values |
| UML-SEM-067 | must | Every instance of an abstract classifier is an instance of one of its specializations. |  | runtime (execution) | 9.2.3 | prose: abstract-classifier-no-direct-instance |
| UML-SEM-068 | must | The values of an attribute match its multiplicity: 0..1 none or one value of conforming type; 1..1 exactly one; j..k a collection of size between j and k; 0..0 none. |  | runtime (execution) | 9.4.3 | prose: attribute-value-matches-multiplicity |
| UML-SEM-069 | must | A structural feature with isReadOnly true is not updated after it receives an initial value. |  | runtime (execution) | 9.4.3 | prose: readonly-feature-not-updated |
| UML-SEM-070 | must | An implementation keeps the constraints implied by a property's derivation when the property is updated. |  | runtime (execution) | 9.5.3 | prose: derived-property-constraints-kept |
| UML-SEM-071 | must | A part object belongs to at most one composite object at a time, and deleting the composite deletes its part objects. |  | runtime (execution) | 9.5.3 | prose: composite-single-owner |
| UML-SEM-072 | must | The set of values of a subsetting property (duplicates removed) is included in the set of values of the subsetted property. |  | runtime (execution) | 9.5.3 | prose: subsetting-inclusion |
| UML-SEM-073 | must | The value of a derived union property is the strict union of the values of the properties that subset it. |  | runtime (execution) | 9.5.3 | prose: derived-union-is-union |
| UML-SEM-074 | note | Operation preconditions must be true when the operation is invoked; what happens otherwise is not defined. |  | runtime (execution) | 9.6.3 | prose: operation-precondition |
| UML-SEM-075 | must | Operation postconditions hold after a successful invocation by any implementation, given the preconditions held. |  | runtime (execution) | 9.6.3 | prose: operation-postcondition |
| UML-SEM-076 | must | An invocation of an operation with isQuery true does not modify the state of the instance or of any other model element. |  | runtime (execution) | 9.6.3 | prose: query-does-not-modify |
| UML-SEM-077 | must | A bound operation is owned by a classifier. |  | static | 9.6.3.2 | prose: bound-operation-owned-by-classifier |
| UML-SEM-078 | must | If a generalization set is covering, every instance of the general classifier is an instance of at least one specific classifier; if it is disjoint, no instance belongs to two. |  | runtime (execution) | 9.7.3 | prose: genset-covering-disjoint |
| UML-SEM-079 | must | An enumeration literal's name identifies it within its enumeration and is unique there. |  | static | 10.2.3 | prose: enumeration-literal-names-unique |
| UML-SEM-080 | must | An interface is not instantiated; a behaviored classifier realizes it instead. |  | partial | 10.4.3 | prose: interface-not-instantiated |
| UML-SEM-081 | must | A behaviored classifier that realizes an interface complies with the protocol state machine the interface owns. |  | runtime (execution) | 10.4.3 | prose: realizer-complies-with-protocol |
| UML-SEM-082 | must | Each feature of each effective required interface of an element at a connector end has at least one compatible feature among the effective provided interfaces of the elements at the other ends. |  | partial | 11.2.3 | prose: connector-compatible-features |
| UML-SEM-083 | must | Objects of a class hold a value for each attribute that is a member of the class, according to its type and multiplicity. |  | runtime (execution) | 11.4.3 | prose: class-attribute-values |
| UML-SEM-084 | must | A class does not access private features of another class, or protected features of a class that is not its ancestor. |  | partial | 11.4.3 | prose: class-no-private-access |
| UML-SEM-085 | must | If a specialized collaboration extends a collaboration role, the role's type there conforms to its type in the general collaboration. |  | partial | 11.7.3 | prose: collaboration-role-type-conforms |
| UML-SEM-086 | must | The expression of a time expression or a duration evaluates to a single value; the standard defines no type or unit for it. |  | partial | 8.4.3 | prose: time-expression-single-value |
| UML-SEM-087 | must | The minimum and maximum of an interval each evaluate to a single value. |  | partial | 8.5.3 | prose: interval-single-values |
| UML-SEM-088 | must | The ends of five relationships are typed by the metamodel as follows. An Include joins an including use case (includingCase) to an added use case (addition), both UseCases. An Extend joins an extension use case (extension) to an extended use case (extendedCase), both UseCases. A PackageImport joins an importing Namespace (importingNamespace) to an imported Package (importedPackage). A PackageMerge joins a receiving Package (receivingPackage) to a merged Package (mergedPackage). A Substitution joins a substituting Classifier (substitutingClassifier) to a contract Classifier (contract). Each end holds exactly one element. |  | static | 18.2.4; 18.2.2; 7.8.11; 12.4.6; 9.9.22 | prose: keyword-relationship-ends |

