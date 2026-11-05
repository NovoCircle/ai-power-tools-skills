# DMN 1.2: the standard in our own words

Source: Object Management Group, Decision Model and Notation (DMN) 1.2, formal/19-01-05, January 2019 (https://www.omg.org/spec/DMN/1.2/). Normative machine-readable files: DMN12.xsd, DMNDI12.xsd, DMN12.xmi, DMNDI12.xmi (https://www.omg.org/spec/DMN/1.2/About-DMN). Section numbers and printed page numbers (which equal the PDF page numbers) refer to that document. Everything below is summarized; quotations are rare and short.

DMN has later versions (1.3 February 2021, 1.4 April 2023, 1.5 August 2024, 1.6 September 2026, 1.7 in beta). This skill describes 1.2 only and says nothing about what changed.

## 1. What DMN is (clauses 1, 4, 5)

DMN is a notation and a model for describing decisions so that business analysts, developers and managers read the same picture. It has two levels that can be used alone or together (5.1, 5.3):

- the **decision requirements level**: which decisions an organization makes, what each depends on (data, other decisions, areas of business knowledge, authorities), shown as a Decision Requirements Graph drawn in one or more Decision Requirements Diagrams;
- the **decision logic level**: how each decision's result is computed, written as boxed expressions (decision tables, calculations, contexts, functions) in an expression language called FEEL.

DMN is meant to sit between business process models and executable logic. It is independent of BPMN, but a decision can be tied to the business process and tasks that use it (5.1, 6.3.7, Annex A). DMN prescribes no method (5.2.4).

Three uses (5.2): modeling human decision-making, modeling requirements for automated decisions, implementing automated decisions. A project may use all three: an as-is model, a to-be model, an executable model.

A decision here is the act of determining an output value from input values using decision logic, not the chosen option itself (5.3.1).

The specification is organized as: scope (1), conformance (2), references (3), additional information (4), introduction (5), requirements and the DRD (6), relating logic to requirements (7), decision tables (8), S-FEEL (9), FEEL (10), a worked example (11), exchange formats (12), diagram interchange (13), annexes on BPMN (A) and a glossary (B).

## 2. Conformance (clause 2)

Software may claim conformance only if it fully matches the applicable compliance points; partial matches may say "based on" the specification (2.1). Three levels (2.1, p. 15):

| Level | Requires | Expressions |
|---|---|---|
| 1 | Clauses 6 (requirements), 7 (decision logic) and 8 (decision table) | Not interpreted. If interpreted, consistent with clause 7. |
| 2 | Level 1 plus S-FEEL (clause 9) | Literal expressions restricted to S-FEEL, which must be interpreted. |
| 3 | Clauses 6, 7, 8 and the full FEEL of clause 10 (so also Levels 2 and 1) | Full FEEL, including the boxed expressions of clause 10. |

All levels also meet the general requirements of 2.2:

- **Visual appearance** (2.2.1). Use the shapes, icons and markers the specification shows. Size, color, line style and text position are flexible unless the specification fixes them. Extensions are allowed if they add markers, add a new kind of artifact shape that does not clash with a defined one, add color with its own meaning, or change a line style without clashing; they must not change the specified shape of a defined element or marker.
- **Decision semantics** (2.2.2). Any interpretation a tool gives to a diagram element is consistent with the specified semantics.
- **Attributes and model associations** (2.2.3). For each mandatory attribute a tool gives users a way to create and view its value. Where a graphical form is required it is used; where optional, a graphical or other mechanism may be used.

The text of clause 2 still says "DMN 1.1" in this version; it is read as applying to 1.2.

## 3. The decision requirements level (clause 6)

### 3.1 The graph and its elements (6.1, 6.2, Table 1)

A Decision Requirements Graph (DRG) models a domain of decision-making: the elements and the dependencies between them. It is self-contained: all requirements of every decision are in the same graph (6.1). A Decision Requirements Diagram (DRD) is a picture of a DRG, or of part of it (6.2.4).

Five DRG elements:

| Element | Meaning | Drawn as (6.2.1) |
|---|---|---|
| Decision | The act of determining an output from inputs, using logic that may call business knowledge models. | Rectangle, solid lines |
| Business Knowledge Model | A function that encapsulates business know-how: rules, a decision table, an analytic model. | Rectangle with two clipped corners |
| Input Data | Information used as input by decisions; its value comes from outside the model. | Shape with two parallel sides and two semicircular ends |
| Knowledge Source | An authority for a decision or knowledge model: a person, policy, regulation, analytic insight. | Shape with three straight sides and one wavy side |
| Decision Service | A set of reusable decisions exposed as a service, callable inside the model or from outside (for example from a process task). | Rounded rectangle with a heavy border; expanded or collapsed |

The name of an element is shown inside its shape unless a diagram label supplies other text (6.2.1).

Two annotation artifacts: a **Text Annotation** (explanatory text, drawn as a square bracket with text) and an **Association** (a dotted connector from an annotation to the element it explains), (6.1, Table 1).

### 3.2 Requirements (6.2.2)

Dependencies are of three kinds. The kind is fixed by the types of the two elements joined (6.2.3).

- **Information Requirement**: a decision needs the output of another decision, or input data. Drawn as a solid line with a solid arrowhead, in the direction of information flow (toward the decision that needs it). The Information Requirements of a valid graph form a directed acyclic graph (6.2.2.1). A diagram showing only decisions, input data and information requirements is equivalent to a data-flow diagram.
- **Knowledge Requirement**: a decision or business knowledge model invokes a business knowledge model or decision service. Drawn as a dashed line with an open arrowhead, toward the element that needs the knowledge. If an element holds a knowledge requirement on an invocable element b, its logic must contain an invocation of b with an expression for each of b's parameters (6.2.2.2).
- **Authority Requirement**: an element depends on another that acts as a source of guidance or knowledge. Drawn as a dashed line with a filled circular head, from the authority to the governed element. Two uses: (a) from a Knowledge Source to a Decision, Business Knowledge Model or another Knowledge Source (a document, person or group governs the logic); (b) from Input Data and Decisions to a Knowledge Source, where the Knowledge Source stands for an analytic model derived from data and results and the business knowledge model for the logic generated from it (6.2.2.3). Knowledge Sources and Authority Requirements have no execution semantics; the standard leaves their application to implementers.

### 3.3 Connection rules (6.2.3, Table 2)

The permitted connections (required element, element that requires it, kind): Decision to Decision (information); Decision to Knowledge Source (authority); Business Knowledge Model to Decision (knowledge); Business Knowledge Model to Business Knowledge Model (knowledge); Decision Service to Decision (knowledge); Decision Service to Business Knowledge Model (knowledge); Input Data to Decision (information); Input Data to Knowledge Source (authority); Knowledge Source to Decision (authority); Knowledge Source to Business Knowledge Model (authority); Knowledge Source to Knowledge Source (authority). Nothing may end in Input Data: input data requires nothing.

### 3.4 Partial views and the Listed Input Data option (6.2.1.3, 6.2.4)

A DRD may be a partial or filtered view: it can hide categories of elements or collapse areas of the network. An element with requirements not displayed should carry an ellipsis. Tools must let users specify and display properties not normally shown (for example the processes and tasks using a decision).

A tool may offer the Listed Input Data option: input data is not drawn as separate shapes but listed inside each decision that requires it. If input data is not drawn it is listed on every decision that requires it, unless deliberately hidden.

### 3.5 Decision Service (5.3.3, 6.2.5, 6.3.10)

A decision service has output decisions (the results it returns), encapsulated decisions (evaluated inside it), input decisions (results supplied by the caller) and input data. To define one it is enough to give the output decisions and either the encapsulated or input decisions; the rest can be inferred from the model or, if given, validated against it. Each decision the output decisions require, directly or indirectly, must be encapsulated, supplied as input, or required by an input decision. A service is stateless and side-effect free. It is "complete" if it can evaluate every encapsulated decision for all inputs; a request is "valid" if it supplies all the inputs needed.

Drawing (6.2.5): a rounded rectangle with a heavy border. The border encloses all the encapsulated decisions and no other decisions or input data (other elements may sit inside the border but are not part of the definition). If the outputs are fewer than the encapsulated decisions, a straight solid line divides the shape: the part with the service name holds the output decisions, the other holds the remaining encapsulated decisions. A collapsed form hides the decisions. The same service is not shown both expanded and collapsed in one diagram. Decision services are overlays: they do not enclose their decisions, so a decision may be required by decisions outside.

## 4. The requirements metamodel (6.3)

All model elements descend from **DMNElement**, which has an optional id (an XML ID unique within the model), a description and a label, and extension hooks (6.3.1). **NamedElement** adds a required name. The model container is **Definitions** (6.3.2): it has a namespace, optional default expression and type language (URIs; FEEL by default), optional exporter and exporterVersion, and contains DRG elements, item definitions, business context elements, element collections, imports, artifacts and optional diagram interchange data. **Import** (6.3.3) brings in another DMN model, an XML schema, a PMML file or other documents; imports are explicit. **ElementCollection** (6.3.4) groups DRG elements by reference. **DRGElement** (6.3.5) is the abstract superclass of Decision, InputData, KnowledgeSource and Invocable (which has BusinessKnowledgeModel and DecisionService).

| Class | What the standard says (section) |
|---|---|
| Decision (6.3.7) | May have a question and allowed answers, a decision logic expression, a variable for its result and the three requirement kinds. Its requirement subgraph (itself plus everything it requires) is acyclic. Business context links: supported objectives, impacted performance indicators, decision makers, decision owners, and the processes and tasks that use it. |
| Invocable, BusinessKnowledgeModel (6.3.9) | An invocable holds a variable with the same name as the element, so decisions can call it by name. A business knowledge model holds a function definition (the reusable logic) with parameters, and may hold knowledge and authority requirements. Its subgraph is acyclic. Its name differs from every other invocable, input data, decision and import. |
| DecisionService (6.3.10) | Output decisions (one or more), encapsulated decisions, input decisions, input data. At least one of encapsulated and input decisions is given. Its variable has the service's name. Its subgraph is acyclic. |
| InputData (6.3.11) | Defines a variable (with an optional type) holding its value. Has no requirement subgraph; always well formed. Its name differs from every other decision, input data, business knowledge model, decision service and import. |
| KnowledgeSource (6.3.12) | Optional location URI, type (for example policy document, regulation, analytic insight), owner (organizational unit), and authority requirements. |
| InformationRequirement (6.3.13) | Held by a decision. References a required decision or a required input data, not both. Well formed when the referenced element is well formed, the holder is not in the referenced decision's subgraph, and the referenced element is in the same or an imported model. |
| KnowledgeRequirement (6.3.14) | Held by a decision or business knowledge model. References a required invocable. Well formed when the referenced element is well formed, a holder that is a business knowledge model is not in the referenced element's subgraph, and the referenced element is in the same or an imported model. |
| AuthorityRequirement (6.3.15) | Held by a decision, business knowledge model or knowledge source. References a required knowledge source; when held by a knowledge source it may also reference a required decision or input data. |
| Association, TextAnnotation (6.3.6) | Association: a source and target (any DMN element) and a direction None, One (arrowhead at target) or Both. Text annotation: text and a MIME-type format (plain text by default). |
| BusinessContextElement, OrganisationalUnit, PerformanceIndicator (6.3.8) | Placeholders for definitions from other OMG metamodels. An organizational unit makes or owns decisions; a performance indicator is impacted by decisions. |
| Extensibility (6.3.16) | ExtensionElements hold foreign elements; ExtensionAttribute holds a named value or a reference to one, not both. Only the additions may be lost in interchange. |

A decision, business knowledge model or decision service is **well formed** when it and everything in its requirement subgraph meet the referential and acyclicity constraints above: none requires itself, directly or indirectly.

## 5. Relating decision logic to requirements (clause 7)

Each decision and each business knowledge model may carry a **value expression** that describes how its result is computed (7.1). Expression kinds: literal expression (text in an expression language, FEEL by default; may be plain English or pseudo-code at Level 1), decision table (clause 8), invocation (a tabular call of a business knowledge model or decision service), plus the FEEL boxed expressions of clause 10. Boxed expressions nest.

**Variables** link the two levels (7.1, 7.3.3). Each decision and each input data defines a variable holding its value; each information requirement brings that variable into scope in the requiring decision. A business knowledge model's parameters are its variables. A variable referred to in a decision's expression must belong to a required decision, input data or knowledge, and the variable of each required decision and input data must be referred to in the expression. The decision defines the lexical scope of its input variables.

**Which expression a decision uses** (7.1): with more than one required business knowledge model, a literal expression that combines them; with none, a literal expression or decision table giving the whole logic; with exactly one and some elaboration, a literal expression; with exactly one and no elaboration, optionally an invocation that only binds parameters. A business knowledge model that requires others has an explicit expression invoking them. Knowledge sources are documentation, not part of the logic.

**Notation** (7.2): a top-level boxed expression has a name box holding the name of its DRG element; the name is the only visual link between a DRD element and its boxed expression. A string literal may be shown italicized without quotes (and then contains no comma); a date or time literal may be shown bold italic. A boxed invocation shows the name of the called function and a row per binding (parameter name, binding expression).

**Metamodel** (7.3):

- *Expression* (abstract) may name a type; if it defines a decision's output, that type is the decision's type.
- *ItemDefinition* describes the structure and range of data: a base type (a FEEL built-in, an imported type or another item definition) optionally restricted by allowed values (unary tests), or a composition of item components, but not both. A flag marks collections. Its name differs from other item definitions and imports.
- *InformationItem* is a variable: required name unique in its scope, a type compatible with the element it takes its value from.
- *LiteralExpression*: optional text and expression language, or imported values (never both); text must be valid in the language.
- *Invocation*: a called function (an expression whose value is a function, most commonly a business knowledge model) and bindings. For a decision it is the encapsulated logic of the business knowledge model the decision requires. One binding per parameter (7.3.5); bound names are a subset of the parameters (7.3.6).
- *Binding*: a parameter and the expression whose value it receives.

## 6. Decision tables (clause 8)

### 6.1 Structure (8.1)

A decision table is a tabular set of related input and output expressions organized into rules. It has:

- a name (the information item it is the value of, usually the decision or business knowledge model);
- zero or more **input clauses**, each an input expression and optional input values (the expected values);
- one or more **output clauses**: with several, each is named and the table returns a context with one entry per output; with one, it has no name;
- zero or more **annotation clauses**, each named; annotation entries are not part of the result and are ignored in hit policy checks;
- one or more **rules**, each with one input entry per input clause (a unary test, or "-" for irrelevant), one output entry per output clause (an expression) and annotation entries, in the order of the clauses.

A rule matches when every input expression value satisfies its input entry; a rule with no input entries always matches. A value satisfies an entry if it equals a listed value, is in a listed list or range, satisfies a unary test, or makes a boolean expression using the special variable `?` true (8.3.3).

### 6.2 Notation (8.2)

Orientation: rules as rows, rules as columns, or crosstab (two input dimensions, outputs lower right). Inputs are left of (or above) outputs. Line style is normative: double lines separate inputs from outputs, outputs from annotations, and the headers from the entries; other cells use single lines. Color is only suggested. The hit policy letter sits in the top-left cell (horizontal) or bottom-left (vertical). Rule numbers run from 1 and are required for First and Rule order tables. A crosstab is always Unique and has no indicator.

Input entry cells with identical content can be merged when adjacent and preceded by the same prior cells; output cells cannot be merged (except in a crosstab). A shorthand for vertical single-output tables lists the output values once and marks each rule's value with X and the rest with "-". A table with a "-" input entry is called contracted, otherwise expanded. Evaluating input expressions has no side effects.

Input values should be **exclusive** (disjoint) and **complete** (cover the domain): "<5, <10" overlap; "<5, >5" is incomplete (8.2.4). Input entries should be "-" or a subset of the input values (8.2.7). Output values, if given, restrict the outputs; their order sets priority for Priority and Output order. A default output may be underlined in the list of output values.

### 6.3 Overlap and completeness (8.1, 8.2.4)

Two input entries of one input expression are disjoint if they share no value, overlapping otherwise; "-" overlaps every entry. Two rules overlap if all their corresponding input entries overlap; they are disjoint if at least one pair is disjoint. A table is **complete** if its rules cover all combinations of the expected input values of all input expressions. A complete table gives no default output value; for an incomplete table a default may be given, and with no default an unmatched input yields null (10.3.2.10). For full automation the logic must be complete (5.2.2).

### 6.4 Hit policies (8.2.10, 8.3.1, 10.3.2.10)

The hit policy says what a table returns when more than one rule matches. It defaults to Unique. It is shown as a single letter; it is mandatory except for Unique. Tools may support a subset of the policies but always support Unique.

| Policy | Letter | Kind | Meaning |
|---|---|---|---|
| Unique | U | single | No rules overlap; one rule matches. The default. |
| Any | A | single | Rules may overlap but all matching rules give equal outputs (annotations ignored); otherwise the policy is incorrect and the result undefined. |
| Priority | P | single | Several rules may match with different outputs; the output earliest in the ordered output-values list wins, independent of rule order. |
| First | F | single | The first matching rule by rule order is returned. Meaning depends on order; use with care. |
| Output order | O | multiple | All hits, ordered by the output-values list (highest priority first). |
| Rule order | R | multiple | All hits in rule order. |
| Collect | C | multiple | All hits in arbitrary order, as a list. An operator may be added: C+ sum, C< minimum, C> maximum, C# count. |

Compound output (two or more output clauses) supports Unique, Any, Priority, First, Rule order and Collect without an operator; Collect operators are undefined over several outputs. Output order is listed as supported for compound output in 8.2.10 (with an example) but required to be single-output in 10.3.2.10. For Priority and Output order with compound output, priority is decided over the outputs that have output values, left to right (or top to bottom).

Execution (10.3.2.10): match every rule; if none, return the default or null; otherwise order the matches by rule number for First and Rule order, build one output per match (a context for compound output), and either return the first (single hit) or the list or aggregate (multiple hit).

### 6.5 Metamodel (8.3)

DecisionTable (an Expression) has inputs, outputs, annotations, rules, a hit policy (UNIQUE, FIRST, PRIORITY, ANY, COLLECT, RULE ORDER, OUTPUT ORDER; default UNIQUE), an optional aggregation (SUM, COUNT, MIN, MAX, for COLLECT), a preferred orientation (Rule-as-Row, Rule-as-Column, CrossTable) and an optional output label. InputClause: optional input expression and input values. OutputClause: optional name, type reference, output values and default output entry (name and type per the rules above). DecisionRule: input entries (unary tests), output entries (literal expressions, at least one) and annotation entries; each in the order of its clauses; each output entry consistent with the type of its output clause.

Examples in 8.4 (Table 35) show one table of each hit policy; they are not repeated here.

## 7. S-FEEL and FEEL (clauses 9 and 10)

### 7.1 S-FEEL (clause 9)

S-FEEL is a small subset of FEEL for the expressions in decision tables, the default for Level 2. It has arithmetic (+, -, *, /, **, negation), comparisons (=, !=, <, <=, >, >=), simple literals (numbers, strings, booleans, and date, time and duration made with `date(...)`, `time(...)`, `duration(...)`), qualified names, intervals with open and closed ends, and "simple unary tests": a list of simple tests, `not(...)` of such a list, or "-" (38 grammar rules, 9.2). Its data types are the FEEL types with simplified number and date definitions (9.3). Comparison needs two operands of the same type, except that the two duration types may be compared for equality; strings and booleans are compared only for equality (9.4). Where S-FEEL is the language, each part of a table is restricted: input expressions and output entries are simple expressions; input values, output values and input entries are simple unary tests; item definition allowed values are simple unary tests; invocation binding formulas are simple expressions (9.5). The standard itself notes that few complete decision models can be written with S-FEEL alone (9.1).

### 7.2 Boxed expressions (10.2)

All decision logic can be shown as boxed expressions. The kinds are: decision table, boxed FEEL expression, boxed invocation, boxed context, boxed list, relation and boxed function. A **boxed context** is a set of named entries and an optional result; entry names are legal FEEL names; without a result the entries are visible outside the context, with a result they are not. A **boxed list** is a list of boxed expressions. A **relation** is a list of similar contexts drawn like a table. A **boxed function** has a kind (FEEL, PMML or Java; FEEL if omitted), parameters in parentheses and a body; a business knowledge model's expression is a boxed function or a decision table whose inputs are the parameters. A boxed invocation needs at least one parameter; a parameterless call is written in text.

### 7.3 FEEL (10.3), what a validator needs

FEEL ("Friendly Enough Expression Language") has no side effects, a simple data model (numbers, strings, dates, times, durations, lists, contexts, functions), a readable syntax and three-valued logic (true, false, null). Its meaning is fully defined; all conformant tools interpret it the same way except for externally defined functions.

- **Grammar:** 66 numbered rules (10.3.1.2): expressions (for, if, quantified, disjunction, conjunction, comparison, arithmetic, instance of, path, filter, function invocation, literal, unary test, name), unary tests, names, literals, invocation with positional or named parameters, lists, function definitions, contexts. Operator precedence follows the order of the alternatives. Java-style comments are allowed. The full grammar is not reproduced here.
- **Names** are sequences of tokens, so extra spaces inside a name do not matter. A name may not start with a reserved word. A name that looks like an expression (`a-b`) is resolved by matching against names in scope, longest first; punctuation can force the other reading (10.3.1.4, 10.3.1.6).
- **Literals:** numbers, strings, booleans, null. Dates, times and durations have no literal syntax; they are made with the built-in functions `date`, `time`, `date and time` and `duration` (10.3.1.3).
- **Types:** number, string, boolean, days and time duration, years and months duration, time, date and time; constructed list, context and function types; a lattice with Any on top and Null at the bottom. Comparison is defined only between conforming types (10.3.2.9).
- **Contexts** evaluate in dependency order; an entry may use earlier entries but not itself; references are acyclic (10.3.2.6, 10.3.2.11).
- **Functions:** built-in, user-defined (closures) and externally defined (Java: a public static method; PMML: a document and model). Positional calls supply every parameter; named calls bind missing parameters to null (10.3.2.13).
- **Built-in functions** (10.3.4): conversion (`date`, `time`, `date and time`, `duration`, `years and months duration`, `number`, `string`), boolean (`not`), string (`substring`, `string length`, `upper case`, `lower case`, `substring before`, `substring after`, `replace`, `contains`, `starts with`, `ends with`, `matches`, `split`), list (`list contains`, `count`, `min`, `max`, `sum`, `mean`, `all`, `any`, `sublist`, `append`, `concatenate`, `insert before`, `remove`, `reverse`, `index of`, `union`, `distinct values`, `flatten`, `product`, `median`, `stddev`, `mode`), numeric (`decimal`, `floor`, `ceiling`, `abs`, `modulo`, `sqrt`, `log`, `exp`, `odd`, `even`) and `sort`; context functions `get value` and `get entries`. A built-in given a value outside its domain returns null and should log a diagnostic (10.3.2.16).
- **Decision services:** a service means a function whose parameters are the input data and input decisions and whose body is a context assembled from the encapsulated decisions and the knowledge they require (10.4).
- **XML data** is mapped to contexts and lists (10.3.3); namespaces are not supported by the mapping.
- **Metamodel for boxed expressions** (10.5): Context and ContextEntry, FunctionDefinition (formal parameters, body, kind), List and Relation (rows and columns). FEEL contexts, functions, relations and lists should be modeled as these elements whenever possible.

## 8. The worked example (clause 11)

A loan-origination example with a business process, a DRD of several decisions with their input data and business knowledge models, the decision logic as boxed expressions, and a run of the decision model. It illustrates the notation; it adds no rules and is not summarized further.

## 9. Exchange formats (clause 12)

The root element of each file is Definitions. A model may span several files; the set of files is self-contained: whatever a file uses is imported, directly or indirectly. Each file declares a namespace (which may differ across files). Files may import non-DMN documents such as XML schemas and PMML files (12.3.1). References across files use an href whose fragment is the id of the target and which has no query; a fragment-only href refers within the same file; type references use names qualified by the import name (12.3.2). Incomplete models can be interchanged: tools disregard missing required attributes and relax minimum bounds above zero (12.1).

## 10. Diagram interchange (clause 13)

DMN DI interchanges the layout of Decision Requirements Diagrams between tools. It adds no meaning: a diagram needs both its DI data and the model it points to, and it does not check that the diagram is correct. Diagrams of boxed expressions and decision tables are not covered (13.1).

- A **DMNDI** holds shared styles and all diagrams of a Definitions. A **DMNDiagram** is an ordered collection of shapes and edges (the order is the stacking order, later on top); it has a name, documentation, a resolution (300 per inch by default), optional size and styles; it cannot hold another diagram; only positive coordinates are used.
- A **DMNShape** depicts a Decision, Business Knowledge Model, Input Data, Knowledge Source, Decision Service or Text Annotation; it has bounds and may say whether input data is listed inside a decision, whether a decision service is collapsed, and carry a divider line for a decision service. A **DMNEdge** depicts an Information, Knowledge or Authority Requirement or an Association and has at least two waypoints. Each shape and edge references exactly one model element; one with no valid reference is not drawn.
- A **DMNLabel** may sit inside a shape or edge; its text, if present, replaces the element's name. A **DMNStyle** carries non-normative appearance (fill, stroke, font colors and font), resolved by precedence: the element's local style, its shared style, the diagram's local style, the diagram's shared style, then defaults.
- Clause 13.5 gives, for each model element, its depiction (the shapes of 3.1 above, edges as in 3.2, associations with no, one or two arrowheads).

## 11. Relation to BPMN (Annex A, informative; 6.3.7)

A decision can be associated with the business processes and tasks that use it; a tool must let users record these associations for each decision. A cross-model check, if offered, can verify that a decision is not tied to tasks in processes it is not itself tied to, and that every task tied to a decision lies in a process tied to it; inconsistency between task and process associations is not allowed. Process tasks relevant to decisions: the Business Rule Task is the natural fit, but a decision may be associated with any task. Decisions feed process gateways or later tasks. A decision service is the usual way to call a decision model from a process.

## 12. Glossary highlights (Annex B)

Well formed: an element or requirement that meets referential integrity and acyclicity constraints. Requirement subgraph: the transitive closure of the requirements of an element. Hit: the matching of all input expressions of a rule. Single hit: a table that returns the output of one rule. Multiple hit: a table that may return outputs from several rules. Crosstab: an orientation in which two input expressions form the two dimensions and outputs fill a grid. Aggregation: the single result produced from several hits (sum, minimum, maximum, count).
