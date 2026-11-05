# DMN 1.2 rules

Generated from `language.yaml` (`constraints`). Do not edit by hand; change the language file and regenerate.

Each rule has a stable id of the form `DMN-<CAT>-nnn`. The number never changes once assigned. A rule that is retired keeps its id and is marked withdrawn rather than reused.

## Strength

| Strength | Meaning | Rules |
|---|---|---|
| must | The standard states it as a requirement (SHALL, MUST, "must") or as a necessary condition. A model that breaks it is not well formed. Reported as an error. | 103 |
| should | The standard gives it as guidance (SHOULD), or two clauses conflict and the stricter reading would reject ordinary models. Breaking it is a warning, not an error. | 15 |
| note | The standard states it as an option, a definition or a method note. It is recorded for completeness and is not reported as a finding. | 24 |

## Checkable

| Value | Meaning |
|---|---|
| static | A validator that sees only the saved model can check it. |
| partial | Only the structure, simple cases or graph analysis can be checked; or the check needs another model (for example a business process model). |
| runtime | Needs a running instance. |
| none | Not a property of a model (it binds a tool, a drawing or a method). |

A rule may carry `applies_when`: `level` (depends on the conformance level the model targets: Level 2 restricts expressions to S-FEEL, Level 3 allows full FEEL) or `automation` (only for decision logic meant for full automation). A rule with `see_conventions` has a matching drawing convention in `language.yaml` (`conventions`).

## Categories

| Category | Name | Covers | Rules |
|---|---|---|---|
| DRD | Decision requirements graph | The elements of a Decision Requirements Graph, the three requirement kinds and which elements each may join, acyclicity, and Decision Service composition. | 18 |
| NAME | Identity and naming | Identifiers, names, and which names must differ from which. | 10 |
| STRUC | Structure and containment | What contains what, and what is referenced rather than contained. | 6 |
| LOGIC | Decision logic | How decision logic attaches to decisions and business knowledge models: value expressions, invocation, bindings, variables, item definitions and types, boxed function definitions. | 26 |
| TBL | Decision table structure | The parts of a decision table and how its rules, clauses and entries line up. | 15 |
| HIT | Hit policies | The seven hit policies, what each requires of a table, and the restrictions for compound output. | 13 |
| COV | Completeness and overlap | What it means for a decision table to be complete, exclusive or overlapping, and the rules that follow. | 6 |
| FEEL | Expression language | What a validator needs to know about S-FEEL and FEEL: where each is required, names, literals, scope, typing. The grammar itself is not reproduced. | 12 |
| CONF | Conformance | The three conformance levels and the general conformance requirements. Most bind tools, not models. | 10 |
| DI | Diagram and interchange of diagrams | Rules for a Decision Requirements Diagram and its interchange form (DMN DI). Drawing rules are conventions; the few worded as requirements are kept here. | 12 |
| XCH | Exchange format | The XML interchange form: root element, namespaces, imports, references, languages, extensions. | 6 |
| BCTX | Business context and process link | The business context elements and the link from a Decision to the business process and tasks that use it. | 4 |
| GUID | Guidance | Method notes and options that are not checkable on their own. | 4 |

Section references are to the clauses and annexes of the DMN 1.2 specification (formal/19-01-05); "p." gives the printed page where the standard is specific. Multiplicities on the individual references are in `language.yaml` (`relationships.references`) and are not repeated here. The connection table for requirements (Table 2) is `relationships.connection_tables`.

## DRD: Decision requirements graph

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| DMN-DRD-001 | must | static | Requirements may join only the pairs of elements in the connection table (11 pairs), and the pair of element types fixes the kind of requirement: Decision to Decision, Input Data to Decision = information; Business Knowledge Model or Decision Service to Decision or Business Knowledge Model = knowledge; Knowledge Source, Decision or Input Data to Knowledge Source, and Knowledge Source to Decision or Business Knowledge Model = authority. | 6.2.3; Table 2 |
| DMN-DRD-002 | must | static | No requirement may end in an Input Data element: an Input Data element requires nothing. | 6.2.3 |
| DMN-DRD-003 | must | static | The Information Requirements of a valid Decision Requirements Graph form a directed acyclic graph. | 6.2.2.1 |
| DMN-DRD-004 | must | static | The requirement subgraph of a Decision is acyclic: a Decision does not require itself, directly or through other requirements. The Decision that holds an Information Requirement must not lie in the requirement subgraph of the Decision it requires. | 6.3.7, p. 52 |
| DMN-DRD-005 | must | static | The requirement subgraph of a Business Knowledge Model is acyclic: it does not require itself, directly or indirectly. A Business Knowledge Model holding a Knowledge Requirement must not lie in the subgraph of the knowledge it requires. | 6.3.9, pp. 56-57; 6.3.14 |
| DMN-DRD-006 | must | static | The requirement subgraph of a Decision Service (itself plus the subgraphs of its encapsulated and output decisions) is acyclic: a Decision Service does not require itself, directly or indirectly. | 6.3.10, pp. 58-59 |
| DMN-DRD-007 | must | static | An Information Requirement references a required Decision or a required Input Data, but not both, and references one of them. | 6.3.13, p. 61 |
| DMN-DRD-008 | must | static | A Knowledge Requirement references a required Invocable (a Business Knowledge Model or a Decision Service), and is held by a Decision or a Business Knowledge Model. | 6.3.14, p. 62 |
| DMN-DRD-009 | must | static | An Authority Requirement held by a Decision or a Business Knowledge Model references a Knowledge Source. One held by a Knowledge Source references a Knowledge Source, a Decision or an Input Data element. | 6.3.15; Table 21 |
| DMN-DRD-010 | must | static | A required element must be defined in the same decision model or in an imported one, and a requirement is well formed only if the element it requires is well formed. A Decision Requirements Graph is self-contained: the immediate requirements of every Decision are present in it. | 6.1; 6.3.13; 6.3.14, pp. 35, 61-62 |
| DMN-DRD-011 | must | partial | If a Decision or Business Knowledge Model holds a Knowledge Requirement on an invocable element, the logic of the holder must contain an invocation of that element with an expression for each of its parameters. | 6.2.2.2, p. 38 |
| DMN-DRD-012 | must | static | A Decision Service has one or more output decisions. | 6.3.10; Table 16 |
| DMN-DRD-013 | must | static | At least one of the encapsulated decisions and the input decisions of a Decision Service is specified. | 6.3.10, p. 58 |
| DMN-DRD-014 | must | static | Every Decision that the output decisions of a Decision Service require, directly or indirectly, is an encapsulated decision of the service, an input decision of it, or required by one of its input decisions. | 5.3.3; 10.4, pp. 32, 151 |
| DMN-DRD-015 | note | static | Only the output decisions and one of the encapsulated or input decision lists need be given. The remaining lists (required input data, the other decision list) can be inferred from the decision model, or, if given, validated against it. | 5.3.3, p. 32 |
| DMN-DRD-016 | note | none | Knowledge Sources and Authority Requirements have no execution semantics. The standard gives example uses (a document or person that governs a decision; analytics that derive business knowledge from data and decision results) and leaves the details of use to the implementer. | 6.2.2.3, p. 39 |
| DMN-DRD-017 | note | none | A Decision may have no Business Knowledge Model, one, or several. Using one to encapsulate logic is a matter of style and methodology. | 5.3.1, p. 28 |
| DMN-DRD-018 | note | none | A Decision Service is stateless and free of side effects. It is complete if it contains logic to evaluate all its encapsulated decisions on every possible input, and a request is valid if it supplies every input decision and input datum the evaluated decisions need. | 5.3.3, pp. 32-33 |

## NAME: Identity and naming

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| DMN-NAME-001 | must | static | An element identifier, when present, is an XML ID and is unique within the decision model (within its containing Definitions). | 6.3.1; Table 3, p. 45 |
| DMN-NAME-002 | must | static | Every named element (Definitions, Import, Element Collection, Decision, Business Knowledge Model, Decision Service, Input Data, Knowledge Source, Item Definition, Information Item, business context element) has a name. | 6.3.1; Table 4, p. 46 |
| DMN-NAME-003 | must | static | The name of an invocable element (Business Knowledge Model or Decision Service) differs from the name of every other invocable, Input Data, Decision and import in the decision model. | 6.3.7; 6.3.9, pp. 52, 56 |
| DMN-NAME-004 | must | static | The name of an Input Data element differs from the name of every other Decision, Input Data, Business Knowledge Model, Decision Service and import in the decision model. | 6.3.11, p. 60 |
| DMN-NAME-005 | must | static | An import name is distinct from the names of the other imports, Decisions, Input Data, Business Knowledge Models, Decision Services and Item Definitions of the importing model. | 6.3.3, p. 49 |
| DMN-NAME-006 | must | static | The name of an Item Definition is distinct from the names of the other Item Definitions and imports in the same model. | 7.3.2, p. 71 |
| DMN-NAME-007 | must | static | The name of an item component is unique within its containing Item Definition or component. | 7.3.2, p. 72 |
| DMN-NAME-008 | must | static | An Information Item has a name, and the name is unique within its scope. | 7.3.3, p. 72 |
| DMN-NAME-009 | must | static | The variable of an invocable element (Business Knowledge Model or Decision Service) carries the same name as the element. | 6.3.9, p. 57; 6.3.10, p. 58 |
| DMN-NAME-010 | should | static | When elements are mapped to the expression language, the name of the variable of a Decision or Input Data element is the same as the (possibly qualified) name of the element, which keeps variable names unique. | 7.1, p. 66 |

## STRUC: Structure and containment

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| DMN-STRUC-001 | must | static | The Definitions element contains all DRG elements, Item Definitions, business context elements, Element Collections and Artifacts of a model. Requirements, bindings, clauses, decision rules, imports and the like are contained in a DRG element, or in an element that is, at any depth. | 6.3.2; 6.3.5, pp. 47, 49-50 |
| DMN-STRUC-002 | must | static | An Element Collection references the DRG elements it groups; it does not contain them. DRG elements are contained only in Definitions. | 6.3.4, p. 49 |
| DMN-STRUC-003 | must | static | A requirement references the element it requires and does not contain it. Decisions, Input Data, Business Knowledge Models and Knowledge Sources are contained only in Definitions. | 6.3.13; 6.3.14; 6.3.15, pp. 61-63 |
| DMN-STRUC-004 | must | static | Imports are explicitly defined. An Import has an import type and a namespace, and may give a location. | 6.3.3, p. 48 |
| DMN-STRUC-005 | must | static | An Association has exactly one source and exactly one target, which may be any DMN element. Direction None draws no arrowhead; One puts the arrowhead at the target; Both puts one at each end. | 6.3.6.1; Table 8, p. 50 |
| DMN-STRUC-006 | must | static | An extension attribute carries a value or a reference to a value (valueRef), never both. | 6.3.16.2; Table 23, p. 64 |

## LOGIC: Decision logic

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| DMN-LOGIC-001 | must | partial | Every variable that a Decision value expression refers to belongs to a required Decision, required Input Data or required knowledge, and the variable of each required Decision and Input Data is referred to in that expression. | 7.1, p. 66; 7.3.3, p. 73 |
| DMN-LOGIC-002 | must | partial | Every parameter of a Business Knowledge Model is a variable used in the value expression of that Business Knowledge Model. | 7.3.3, p. 73 |
| DMN-LOGIC-003 | must | static | If a Decision requires more than one Business Knowledge Model, its value expression is a literal expression that says how they are invoked and combined. | 7.1, pp. 66-67 |
| DMN-LOGIC-004 | must | static | If a Decision requires no Business Knowledge Model, its value expression is a literal expression or a decision table that gives the whole logic. | 7.1, p. 67 |
| DMN-LOGIC-005 | must | partial | If a Decision requires exactly one Business Knowledge Model and elaborates its result, the value expression is a literal expression. Only when it requires exactly one and does not elaborate may the value expression be an invocation. | 7.1, p. 67 |
| DMN-LOGIC-006 | must | static | A Business Knowledge Model that requires other Business Knowledge Models has an explicit value expression that says how they are invoked and their results combined. | 7.1, p. 66 |
| DMN-LOGIC-007 | must | static | The called function of an Invocation in a Decision is the encapsulated logic of the Business Knowledge Model that the Decision requires. | 7.3.5, p. 75 |
| DMN-LOGIC-008 | should | static | An Invocation has exactly one binding for each parameter of the encapsulated logic it calls. Clause 7.3.5 says so; clause 7.3.6 requires only that the bound names be a subset of the parameters, and clause 10.3.2.13.4 binds an unsupplied named parameter to null. | 7.3.5, p. 75 |
| DMN-LOGIC-009 | must | static | The parameter names in the bindings of an Invocation are a subset of the formal parameters of the called function. | 7.3.6, p. 75 |
| DMN-LOGIC-010 | note | none | A Decision with exactly one Knowledge Requirement and nothing to add can use an Invocation as its logic. The Invocation then lets many Decisions reuse the same Business Knowledge Model, each with its own bindings. | 7.3.5, pp. 74-75; 5.3.1 |
| DMN-LOGIC-011 | must | static | A literal expression has text or imported values, never both, and the import type of imported values agrees with the expression language of the expression. | 7.3.4, p. 74 |
| DMN-LOGIC-012 | must | partial | The text of a literal expression is a valid expression in its expression language (the language of the Definitions unless overridden on the expression). The standard semantics apply only if every literal expression is valid. | 7.3.4; Table 26, p. 74 |
| DMN-LOGIC-013 | must | static | If the expression that defines the output of a Decision names a type, that type is the type of the Decision. | 7.3.1, p. 71 |
| DMN-LOGIC-014 | must | partial | The type of an Information Item is compatible with the type of the DMN element from which it takes its value. | 7.3.3, p. 73 |
| DMN-LOGIC-015 | must | static | An Item Definition is defined in exactly one of two ways: by a type reference (possibly restricted by allowed values) or by a composition of item components. | 7.3.2, p. 72 |
| DMN-LOGIC-016 | must | partial | Allowed values of an Item Definition are unary tests, their type is consistent with the Item Definition, and when present they give the complete range of the Item Definition. | 7.3.2; 9.5.1, pp. 72, 100 |
| DMN-LOGIC-017 | must | static | A type reference to a built-in type omits any prefix. A type reference to an imported type is qualified with the import name, and the external document is imported by an Import that gives both its namespace and its name. | 7.3.2; 12.3.2, pp. 71, 182 |
| DMN-LOGIC-018 | must | static | The boxed expression of a Business Knowledge Model is a boxed function definition, or a decision table whose input expressions are taken to be the parameter names. | 10.2.1.7, p. 107 |
| DMN-LOGIC-019 | must | static | A boxed function definition has a kind (FEEL, PMML or Java; FEEL when omitted), parameters and a body. A FEEL body is a FEEL expression that uses the parameters. A Java or PMML body is a context giving the mapping information. | 10.2.1.7, p. 108 |
| DMN-LOGIC-020 | must | static | Mapping information for an externally defined function is a context of one of two forms. Java form: a class name on the classpath and a method signature of a public static method with argument type names only. PMML form: the identifier of a PMML document and, optionally, the name of a model in it (the first model if none). | 10.3.2.13.2, p. 128 |
| DMN-LOGIC-021 | should | none | Externally defined functions are deterministic and free of side effects. The standard does not fully define a model that uses them. | 10.3.2.13.2, pp. 128-129 |
| DMN-LOGIC-022 | should | static | FEEL contexts, function definitions, relations and lists are modeled as Context, Function Definition, Relation and List elements, and drawn as boxed expressions, whenever possible (when they are top-level expressions). | 10.5, p. 152 |
| DMN-LOGIC-023 | must | static | Context entry names in a boxed context are legal names in the expression language. The values and the optional result are boxed expressions. | 10.2.1.4, p. 105 |
| DMN-LOGIC-024 | must | static | A boxed invocation lists at least one parameter; a function with no parameters is invoked in textual form. | 10.2.1.3, p. 103 |
| DMN-LOGIC-025 | must | static | A top-level boxed expression has a name box holding the name of the DRG element whose logic it is. | 7.2.1, p. 67; 10.2.1, p. 101 |
| DMN-LOGIC-026 | note | none | Knowledge Sources are documentation of the decision logic and are not part of it. They have no representation at the decision logic level. | 7.1, p. 66 |

## TBL: Decision table structure

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| DMN-TBL-001 | must | static | A decision table has one or more rules and one or more output clauses. It may have no input clauses; a rule with no input entries always applies. | 8.1, p. 77; 8.3.3 |
| DMN-TBL-002 | must | static | Each rule has one input entry per input clause, in the order of the input clauses, and one output entry per output clause, in the order of the output clauses. Annotation entries follow the order of the annotation clauses. | 8.3.3, p. 93 |
| DMN-TBL-003 | must | static | When a table has two or more output clauses, each output clause has a name (the table returns a context with one entry per output). When it has one, the output clause has no name. Every rule annotation clause has a name. | 8.1, p. 77; 8.3.2, p. 91 |
| DMN-TBL-004 | must | static | An output clause of a single-output table does not give a type reference; one of a multiple-output table may. Each output entry is consistent with the type reference of its output clause. | 8.3.2; Table 31, p. 91; 8.3.3, p. 93 |
| DMN-TBL-005 | must | static | A decision table that is the value expression of an Information Item (a Decision, or a binding formula in a boxed invocation) names that Information Item as its information item name. One nested in another boxed expression may use the container for the name. | 8.2.5, p. 84 |
| DMN-TBL-006 | must | static | Input entries, input values and output values are unary tests; an input expression is a textual expression; an output entry is an expression. Under Conformance Level 2 each is restricted to the S-FEEL forms in clause 9.5.3. | 8.2.7, p. 85; 8.2.4, p. 83; 10.3.2.10, p. 124 |
| DMN-TBL-007 | should | partial | An input entry is "-" (irrelevant) or a subset of the input values given for its input clause. An entry outside the input values, for example below 0 when the values are 0 to 120, is reported as invalid. | 8.2.7, p. 85 |
| DMN-TBL-008 | must | static | A crosstab table is always Unique, is complete and unique by definition, and needs no hit policy indicator. | 8.2.2, p. 81; 8.2.10, p. 87; Note 1, p. 88 |
| DMN-TBL-009 | must | static | Rules are numbered consecutively from 1 when the hit policy is First or Rule order, because the meaning depends on the order. Numbering is optional for other tables and absent in a crosstab. | 8.2, p. 81; 8.3.1, p. 90 |
| DMN-TBL-010 | must | static | In the X shorthand for vertical tables with a single output (rules as columns), each rule marks at most one output value with X and every other output entry is "-". The output values are listed once, before the rules. | 8.2.9, p. 86 |
| DMN-TBL-011 | must | static | Output entry cells are never merged, except in a crosstab. Input entry cells merge only when adjacent, identical and preceded by the same (or no) prior cells. | 8.2.8-8.2.9, pp. 85-86 |
| DMN-TBL-012 | should | none | Evaluating an input expression or executing a rule has no side effect that changes the evaluation of another expression or rule of the same table. This matters most in First hit tables. | 8.2.7, p. 85 |
| DMN-TBL-013 | must | static | The preferred orientation of a table is one of Rule-as-Row, Rule-as-Column or CrossTable, and the table is shown that way. All input columns lie left of all output columns (rules as rows), all input rows above all output rows (rules as columns), and all output cells at the lower right (crosstab). | 8.3.1, p. 90 |
| DMN-TBL-014 | should | static | A default output value, if given, is one of the table output values (underlined in the list of output values) and applies only to an incomplete table. A complete table gives none. With several outputs the default is a context of output names and values. | 8.2.11, p. 89; 8.3.2, p. 92; 10.3.2.10, p. 126 |
| DMN-TBL-015 | note | none | If no rule matches, the table returns its default output value, or null if it has none. | 8.2.4, p. 83; 10.3.2.10, p. 126 |

## HIT: Hit policies

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| DMN-HIT-001 | must | static | The hit policy is one of UNIQUE, FIRST, PRIORITY, ANY, COLLECT, RULE ORDER or OUTPUT ORDER, and defaults to UNIQUE. Its indicator is U, F, P, A, C, R or O (and C+, C<, C>, C# for Collect with an operator). | 8.3.1, p. 90 |
| DMN-HIT-002 | must | static | A Unique table (the default) contains no overlapping rules: any two rules are disjoint, so only one rule can match. | 8.2.10, p. 87 |
| DMN-HIT-003 | must | static | The hit policy indicator is mandatory except on a Unique table (where it is optional), so that the type of table is clear. Tools may support a nonempty subset of the hit policies but always support Unique. | 8.2.10, p. 87 |
| DMN-HIT-004 | must | partial | In an Any table, rules may overlap only if the overlapping rules give equal output entries for every output, rule annotations ignored. If they differ the policy is incorrect and the result is undefined. | 8.2.10, p. 87 |
| DMN-HIT-005 | must | static | A Priority or Output order table gives an ordered list of output values; the order is the priority, highest first. Priority is independent of rule order. | 8.2.5, p. 84; 8.2.10, p. 87 |
| DMN-HIT-006 | should | static | An Output order table has a single output. The clause 8 text and its example also allow it with compound output; priority is then decided over the outputs that have output values, left to right or top to bottom. The two clauses disagree. | 10.3.2.10, p. 126; 8.2.10, p. 88 |
| DMN-HIT-007 | must | static | For First and Rule order the rules are explicitly ordered and numbered. For Priority and Output order the output values determine the result. | 8.3.1, p. 90 |
| DMN-HIT-008 | must | static | An aggregation operator is given only with the Collect hit policy. The operators are + (sum), < (minimum), > (maximum) and # (count). A Collect table with no operator returns the list of all hits. | 8.2.10, p. 88; 8.3.1, p. 90 |
| DMN-HIT-009 | must | static | A table with compound output (two or more output clauses) uses no Collect operator, because the operators are undefined over several outputs. | 8.2.10, p. 88; 10.3.2.10, p. 125 |
| DMN-HIT-010 | must | static | A table with compound output uses only Unique, Any, Priority, First, Rule order or Collect without an operator (Output order too, in the clause 8 reading; see DMN-HIT-006). | 8.2.10, p. 88; 10.3.2.10, p. 125 |
| DMN-HIT-011 | note | none | Single hit policies (Unique, Any, Priority, First) return the output of one rule. Multiple hit policies (Output order, Rule order, Collect) return a list or an aggregate. The initial letter tells which. | 8.2.10, p. 87 |
| DMN-HIT-012 | note | none | Rule annotations are not part of the result and are ignored in hit policy validation and in execution semantics. | 8.2.10, p. 87; 10.3.2.10, p. 124 |
| DMN-HIT-013 | note | none | Evaluation: match every rule (unordered). With no match, return the default or null. Otherwise order the matches by rule number for First and Rule order; for a single hit policy return the first of the list; for a multiple one return the list, or aggregate it with sum, count, minimum or maximum. | 10.3.2.10, pp. 125-126 |

## COV: Completeness and overlap

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| DMN-COV-001 | should | partial | A decision table is complete: its rules cover all combinations of the expected input values of all its input expressions. Completeness can be judged only against input values that are given. | 8.1, p. 77; 8.2.4, p. 83 |
| DMN-COV-002 | should | static | The input values given for an input clause are exclusive (disjoint, for example not "<5, <10") and complete (all relevant values present, for example not "<5, >5"). | 8.2.4, p. 83 |
| DMN-COV-003 | note | static | Two input entries of one input expression are disjoint if they share no value, overlapping if they do; "-" overlaps every entry. Two rules overlap if all their corresponding input entries overlap, and are disjoint if at least one pair is disjoint. | 8.1, p. 80 |
| DMN-COV-004 | must | partial | For full automation of decisions the decision logic is complete: it gives a result for every possible set of input values. (applies when: automation) | 5.2.2, p. 26 |
| DMN-COV-005 | note | none | Rule order matters only in First and Rule order tables. First tables hide the overall logic, are hard to validate by hand and need care; the last rule is often the catch-remainder. | 8.2.10, pp. 87-89; Note 2 |
| DMN-COV-006 | note | static | A table with at least one "-" input entry is contracted; the others are expanded. Tables whose entries are all true, false or "-" are historically called limited-entry; the restriction is not needed. | 8.1, p. 77; 8.2.7, p. 85 |

## FEEL: Expression language

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| DMN-FEEL-001 | must | static | At Conformance Level 1 expression text is not interpreted. At Level 2 literal expressions are restricted to S-FEEL. At Level 3 the full FEEL of clause 10 applies. S-FEEL is a subset of FEEL and is indicated by the same language URI. (applies when: level) | 2.1, p. 15; 7.1, p. 65; 9; 10 |
| DMN-FEEL-002 | must | static | Under S-FEEL: an Item Definition allowed value is a simple unary tests; an invocation binding formula is a simple expression; a decision table input expression and output entry are simple expressions; input values, output values and input entries are simple unary tests. (applies when: level) | 9.5, p. 100 |
| DMN-FEEL-003 | must | static | A name does not start with a reserved word of the grammar (a literal terminal symbol); a later part of a name may be one. Names are sequences of tokens, so extra white space inside a name is insignificant. | 10.3.1.4, p. 114 |
| DMN-FEEL-004 | must | static | Dates, times and durations have no literal syntax in FEEL. They are made from a string with the built-in functions date, time, date and time and duration. A typographical date or time literal obeys the same syntax. | 10.3.1.3, p. 114; 7.2.2.2, p. 69 |
| DMN-FEEL-005 | must | static | A typographical string literal (italic text standing for a quoted string) contains no comma and conforms to the name rule. | 7.2.2.1, p. 68 |
| DMN-FEEL-006 | must | static | A context entry expression may refer to earlier entries and to values in scope but not to its own key. The references between entries are acyclic and form a partial order, and entries are evaluated in that order. | 10.3.2.6, p. 119; 10.3.2.11.1, p. 126 |
| DMN-FEEL-007 | must | static | In a positional invocation every parameter is supplied. In a named invocation, parameters not supplied are bound to null. | 10.3.2.13.4, p. 129 |
| DMN-FEEL-008 | should | partial | Comparison is defined only between values of conforming types. Comparing, for example, a number with a boolean or a string gives no meaningful result. | 10.3.2.9, p. 119 |
| DMN-FEEL-009 | must | static | Under S-FEEL, comparison needs two operands of the same type (years and months with days and time durations may be compared for equality only), and strings and booleans are compared only for equality. Arithmetic is defined only for the type combinations listed in clause 9.4. (applies when: level) | 9.4, p. 100 |
| DMN-FEEL-010 | note | none | FEEL uses three-valued logic (true, false, null). A built-in function given a value outside its domain returns null and should report or log a diagnostic. | 10.3.2.16, p. 141; 10.3.4, p. 144 |
| DMN-FEEL-011 | note | none | A name is matched against names in scope from left to right and the longest match wins; parentheses or other punctuation disambiguate. | 10.3.1.6, p. 115 |
| DMN-FEEL-012 | note | none | FEEL has no side effects and the same meaning in every conformant implementation, except where external functions are invoked. A boxed FEEL expression is best kept simple and composed from small boxed expressions. | 10.3, p. 110; 10.2.1.2, p. 102 |

## CONF: Conformance

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| DMN-CONF-001 | must | none | A tool may claim conformance to DMN only if it fully matches the applicable compliance points. A tool that matches only some may say it is based on the specification. | 2.1, p. 15 |
| DMN-CONF-002 | must | none | Level 1 requires clauses 6 (requirements), 7 (decision logic) and 8 (decision table); expression text is not interpreted, but any interpretation given is consistent with clause 7. | 2.1, p. 15 |
| DMN-CONF-003 | must | none | Level 2 requires everything in Level 1 and interpretation of S-FEEL expressions (clause 9). | 2.1, p. 15 |
| DMN-CONF-004 | must | none | Level 3 requires clauses 6, 7, 8 and 10 (FEEL). Level 3 includes Levels 2 and 1. | 2.1, p. 15 |
| DMN-CONF-005 | must | none | Every conformance level requires the general conformance of clause 2.2. A tool that draws decision model diagrams uses the shapes, icons and markers the specification shows. | 2.2.1, p. 15 |
| DMN-CONF-006 | must | none | An extension to a diagram does not change the specified shape of a graphical element or marker (a dashed line to plain, a square to a triangle, rounded to square corners), and a new shape does not conflict with any shape or marker the standard defines. (see conventions: extension) | 2.2.1, pp. 15-16 |
| DMN-CONF-007 | must | none | Where a tool interprets a diagram element as a semantic specification of a concept, the interpretation is consistent with the semantics the standard gives. | 2.2.2, p. 16 |
| DMN-CONF-008 | must | none | For every mandatory attribute a tool gives the user a way to create and display its value on each element that has it. Where a graphical representation is required it is used; where optional, a graphical or other mechanism may be used. | 2.2.3, p. 16 |
| DMN-CONF-009 | must | none | A tool provides a way to specify and display the properties of a DRG element that a DRD does not normally show (for example, the business processes and tasks that use a Decision). | 6.2.4, p. 41 |
| DMN-CONF-010 | should | static | Where an expression is not meant to be interpreted, the tool indicates this with the language URI for uninterpreted expressions. | 8.2, p. 81 |

## DI: Diagram and interchange of diagrams

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| DMN-DI-001 | must | static | Every shape and every edge in a diagram references exactly one DMN model element. A shape or edge with no reference, or an invalid one, is not drawn. (see conventions: depiction) | 13.4.6-13.4.7; 13.5, pp. 188-190, 193 |
| DMN-DI-002 | must | static | A shape depicts a Decision, Business Knowledge Model, Input Data, Knowledge Source, Decision Service or Text Annotation. It has bounds. | 13.4.6; Table 80, pp. 188-189 |
| DMN-DI-003 | must | static | An edge depicts an Information Requirement, Knowledge Requirement, Authority Requirement or Association, and has at least two waypoints. | 13.4.7; Table 81, p. 190 |
| DMN-DI-004 | must | static | A diagram does not contain another diagram. Only positive coordinates are used for elements in a diagram. | 13.4.4, p. 185; 13.4.4, p. 186 |
| DMN-DI-005 | must | static | A DMN element appears at most once in a diagram. In particular the same Decision Service is not drawn both expanded and collapsed in one diagram. (see conventions: decision_service) | 6.2.5, p. 44 |
| DMN-DI-006 | must | static | The border of an expanded Decision Service encloses all its encapsulated decisions and no other decisions or input data (it may enclose other elements, which are then not part of its definition). If its output decisions are fewer than its encapsulated decisions, a straight solid line divides it into an output part and an encapsulated part. (see conventions: decision_service) | 6.2.5, p. 42 |
| DMN-DI-007 | must | static | The divider-line attribute applies only to a Decision Service shape (its waypoints lie on the border), the collapsed attribute only to a Decision Service shape, and the listed-input-data attribute only to an Input Data shape. | 13.4.6; Table 80, p. 189 |
| DMN-DI-008 | must | static | If an Input Data element is not drawn as a shape, it is listed on every Decision that requires it, unless it is deliberately hidden. (see conventions: listed_input_data) | 6.2.1.3, p. 37 |
| DMN-DI-009 | should | none | A DRG element with requirements that the diagram does not show is marked with an ellipsis. (see conventions: partial_views) | 6.2.4, pp. 41-42 |
| DMN-DI-010 | must | static | The exporting tool orders shapes and edges in a diagram so that anything meant to appear on top comes later in the order (z-order). | 13.4.1, p. 184 |
| DMN-DI-011 | must | static | The name of an element is displayed inside its shape unless a label gives other text, in which case the label text is displayed instead. | 13.4.8, p. 191; 6.2.1, pp. 37-38 |
| DMN-DI-012 | note | none | DMN DI interchanges laid-out DRDs only and does not check that a diagram is correct. Diagram interchange for boxed expressions and decision tables might come in a later version. A diagram needs both the DI data and the model it references. | 13.1, p. 183 |

## XCH: Exchange format

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| DMN-XCH-001 | must | static | The root element of every DMN file is Definitions. Each file declares a namespace, which may differ between the files of one model. | 12.3.1, p. 181 |
| DMN-XCH-002 | must | static | The set of files of a model is self-contained: every definition used in a file is imported, directly or indirectly, by an Import. A file may import non-DMN files (XSD, PMML) whose definitions it uses. | 12.3.1, p. 181 |
| DMN-XCH-003 | must | static | A reference to an element in another file uses a valid URI reference whose fragment is the id of the element and which has no query. A fragment-only reference points to an element in the same file. | 12.3.2, pp. 181-182 |
| DMN-XCH-004 | must | static | Expression language and type language are given as URIs. The default expression language is FEEL; the default type language is FEEL; a URI for uninterpreted text exists for pseudo-code. | 6.3.2, p. 47 |
| DMN-XCH-005 | should | none | Tools support interchange of incomplete models: they disregard attributes that the XML schema marks required but are missing, and relax lower bounds above zero. | 12.1, p. 181 |
| DMN-XCH-006 | note | none | Extension elements and attributes may be added to any DMN element. Only the additions may be lost in interchange. | 6.3.16, p. 64 |

## BCTX: Business context and process link

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| DMN-BCTX-001 | must | partial | A Decision is not associated with Tasks that belong to Processes it is not also associated with, and not with Tasks that belong to no Process it is associated with. Inconsistency between the Task and Process associations of a Decision is not allowed. (Checking needs the business process model.) | Annex A, A.5(a), p. 202 |
| DMN-BCTX-002 | should | none | A tool lets the user record, for each Decision, the Processes and Tasks that use it (and the objectives it supports, the performance indicators it affects, and its decision makers and owners). | 6.3.7, p. 52; Annex A, A.5, p. 202 |
| DMN-BCTX-003 | note | partial | Once Decisions are mapped to Tasks, a tool could verify that all Input Data are provided by earlier tasks and that decision results are used only by later tasks or gateways. No formal mapping of Item Definitions or Input Data to data objects is defined. | 5.2.2, p. 27 |
| DMN-BCTX-004 | note | none | Business context elements (organizational unit, performance indicator) are placeholders for definitions in other OMG models. The Business Rule Task is the most natural process task for a Decision, though a Decision can be associated with any Task. | 6.3.8, p. 54; Annex A, p. 201 |

## GUID: Guidance

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| DMN-GUID-001 | note | none | DMN is not tied to BPMN, and its two levels (decision requirements, decision logic) may be used on their own or together. DMN prescribes no method. | 5.1; 5.2.4, pp. 24, 28 |
| DMN-GUID-002 | note | none | Three uses: modeling human decision-making (mostly high-level, natural language), modeling requirements for automated decision-making (prescriptive, more logic), and implementing automated decisions (logic fully specified, executed through decision services). A project may use all three: as-is, to-be, executable. | 5.2, pp. 25-28 |
| DMN-GUID-003 | note | none | Few complete decision models can be built from S-FEEL alone; there is generally at least one Decision that needs full FEEL. Developers and users are encouraged to use and implement full FEEL. | 9.1, p. 97 |
| DMN-GUID-004 | note | none | A DRD that shows only Decisions, Input Data and Information Requirements is equivalent to a data-flow diagram of the communication between them at evaluation time. | 6.2.2.1, p. 38 |
