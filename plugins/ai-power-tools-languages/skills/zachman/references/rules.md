# Zachman Framework rules

Generated from `language.yaml` (`constraints`). Do not edit by hand; change the language file and regenerate.

Each rule has a stable id of the form `ZF-<CAT>-nnn`. The number never changes once assigned. A rule that is retired keeps its id and is marked withdrawn rather than reused.

## Strength

| Strength | Meaning |
|---|---|
| must | The source states it as a rule of the framework ("Rule 1" to "Rule 7" in the 1992 paper) or as a defining property. A model that breaks it is not a use of the framework. |
| should | The source gives it as guidance or as the usual case ("at a minimum", "should", "generally"). Breaking it is a warning, not an error. |
| note | The source states it as an observation, an option or a method note. It is recorded for completeness and is not checkable on its own. |

## Checkable

| Value | Meaning |
|---|---|
| static | A validator that sees only the saved model can check it, provided the model carries each element's cell (row and column) as a label or a place. |
| partial | Only the structure can be checked (for example that an element sits in a cell); the meaning cannot. |
| none | A statement about meaning, intent or method. Not checkable from a model. |

## Categories

| Category | Name | Covers | Rules |
|---|---|---|---|
| COL | Columns | The six question words, their order (none), their basic models and the uniqueness of each column's primitives. | 5 |
| ROW | Rows | The six perspectives and how they differ: not decompositions, additive constraints, instances only in the last row. | 8 |
| CELL | Cells and classification | Placing each element or model in exactly one cell and keeping its concept and notation inside that cell. | 7 |
| PRIM | Primitives and composites | What a primitive model is and what makes a model a composite. | 3 |
| INT | Integration | How the cells of a row and of a column relate and what a row's integration gives. | 4 |
| REC | Recursion | The framework applies to itself and to versions of itself. | 1 |
| GUID | Guidance and scope | Method notes and statements about what the framework does not define. | 5 |

Section references: "1987" is Zachman, IBM Systems Journal 26(3), 1987; "1992" is Sowa and Zachman, IBM Systems Journal 31(3), 1992 (printed page numbers; "Rule n" is the numbered rule of the framework in that paper); "Evolution page" is Zachman International's history of the framework's graphic. `applies_when` limits a rule to the scope row (`scope-row`) or to the other rows (`not-scope-row`).

## COL: Columns

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| ZF-COL-001 | must | static | The framework has exactly six columns, one for each question word: what, how, where, who, when, why. Every classified element or model belongs to one of them. | 1992 p. 596 (extended framework); 1987 pp. 282 to 283 |
| ZF-COL-002 | must | none | The columns have no order. Order implies priority and biases the design toward one aspect, so no column comes first and none is more important than another. The tabular order is only a concession to flat displays. | 1992 p. 599 (Rule 1); p. 611 |
| ZF-COL-003 | must | partial | Each column has one simple basic model made of two primitives, a columnar variable and a connector, and it is the same generic model for every cell of the column (for example entity - relationship - entity in the what column). | 1992 pp. 600 to 601 (Rule 2); p. 611 |
| ZF-COL-004 | must | static | The basic model of each column is unique to it. No primitive of one column (entity and relationship, function and argument, node and link, agent and work, time and cycle, ends and means) recurs, in name or in concept, as a primitive of another column. | 1992 p. 601 (Rule 3); p. 612 |
| ZF-COL-005 | note | none | The framework presents its two classifications, interrogatives across and perspectives down, as comprehensive and complete, so that the cells at their intersections are too. | Evolution page, 2011 entry ("What has not changed") |

## ROW: Rows

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| ZF-ROW-001 | must | static | The framework has six rows, from the scope of the enterprise to the functioning enterprise itself: planner (scope), owner (enterprise model), designer (system model), builder (technology model), subcontractor (components) and the functioning enterprise. The 1992 paper counts five rows and shows the functioning system beneath them; the sixth row is taken from the author-side history. | 1992 pp. 591 to 593; Evolution page, 2001 and 2011 entries |
| ZF-ROW-002 | must | none | Each row is a distinct, unique perspective with its own set of constraints. The constraints that matter to the owner, the designer and the builder are different. | 1992 pp. 601 to 602 (Rule 4) |
| ZF-ROW-003 | must | none | Rows are not decompositions of one another. A lower row is a transformation of the row above it, different in nature and meaning, not the same description at a finer level of detail. Level of detail varies inside any one cell. | 1987 p. 281; 1992 p. 593; Evolution page, 2004 and 2011 entries |
| ZF-ROW-004 | must | partial | The meaning of a column's primitive changes from row to row (a business entity for the owner, a data entity for the designer, a segment or row for the builder). An element that stands for the primitive at one row's meaning does not also stand for it at another row's meaning. | 1992 p. 601 (Rule 4); 1987 pp. 284 to 288 |
| ZF-ROW-005 | must | partial | Instances (particular occurrences, such as a named city or an actual record) belong only in the last row, the functioning enterprise. Rows 1 to 5 hold abstractions: classes, types and lists of them. | Evolution page, 2001 and 2011 entries |
| ZF-ROW-006 | should | none | When a constraint at a lower row conflicts with the model of a higher row, the people responsible for the two rows talk it through, and the owner is told and an alternative negotiated where needed. | 1992 p. 593 |
| ZF-ROW-007 | should | none | The constraints of a lower row are added to the model of the row above it. The new model should not become so different that the higher-row model can no longer be recognized in it or inferred from it. | 1992 p. 593 |
| ZF-ROW-008 | note | none | The rows deal with different kinds of constraint: the owner with usability constraints in the conceptual view, the designer with design constraints in the logical view, the builder with construction constraints (the state of the art in methods and technology) in the physical view. | 1992 p. 601 (Rule 4) |

## CELL: Cells and classification

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| ZF-CELL-001 | must | static | Every cell is identified by exactly one row and one column, and each combination of a row and a column is exactly one cell: six rows by six columns, 36 cells. | 1992 pp. 591, 602 (Rule 5) |
| ZF-CELL-002 | must | static | Every classified element or model is placed in exactly one cell. No meta entity shows up in more than one cell. | 1992 p. 602 (Rule 5) |
| ZF-CELL-003 | must | partial | The concept an element stands for must be one of the two primitives of its cell's column, at the meaning its cell's row gives it. A business entity belongs only in the data cell of the owner row, a data entity only in the data cell of the designer row, a business process only in the function cell of the owner row, an application function only in the function cell of the designer row. | 1992 p. 602 (Rule 5); 1987 pp. 284 to 290 |
| ZF-CELL-004 | must | partial | A model in a cell uses only the primitives of that cell's own column. A model that also uses a primitive of another column is not a model of that cell. | 1992 pp. 601, 611 to 612 (Rules 2 and 3); Evolution page |
| ZF-CELL-005 | should | none | Different cells call for different notations. A cell's notation should not be widened to carry content that belongs to another cell, because that complicates the design and can damage the integrity of the other cell (for example drawing a data store on a process-flow model). | 1992 p. 603 |
| ZF-CELL-006 | note | none | The context of a cell defines the meaning of the words used in the models in it. | Evolution page, 2011 entry |
| ZF-CELL-007 | should | partial | A scope-row cell is a list of classes of the column's first primitive (things, processes, locations, organizations, events, objectives). It need not define the connector, and relationships among the listed items are not expected to be definitive. (applies when: scope-row) | 1987 p. 284; 1992 Figure 1 |

## PRIM: Primitives and composites

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| ZF-PRIM-001 | must | partial | A primitive model has exactly two kinds of meta entity, a columnar variable and a connector, joined in the form variable - connector - variable. (applies when: not-scope-row) | 1992 pp. 600 to 601 (Rule 2); Evolution page, 2011 entry |
| ZF-PRIM-002 | must | partial | A model that binds primitives of more than one column into one structure is a composite and is not a primitive. It is not placed in a cell as that cell's primitive model. Examples from the history: a process (a verb) hard-bound into an entity model, and control and mechanism arrows hard-bound into a process model. | Evolution page (1984, 1987, 1993, 2001 and 2003 entries); 1992 p. 603 |
| ZF-PRIM-003 | note | none | Primitives combine in many ways into compounds, just as chemical elements do. A composite built by combining primitives is a legitimate working model; the framework treats the primitive cells as the elements and the composites as combinations of them. | 1992 p. 603 (Rule 5) |

## INT: Integration

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| ZF-INT-001 | must | none | The composite, or integration, of all the cell models of one row is a complete model from the perspective of that row. | 1992 p. 603 (Rule 6); p. 612 |
| ZF-INT-002 | should | partial | Each cell of a row is related, at a minimum, to every other cell of that row, because each is one abstraction of the same reality. Where a dependency exists, a change to one cell is likely to affect the other. | 1992 p. 603 (Rule 6) |
| ZF-INT-003 | should | partial | Within a column, a cell depends on the cell above it and the cell below it. A change to a cell is likely to affect both. | 1992 p. 603 (Rule 6) |
| ZF-INT-004 | should | none | Each cell description added to a row, including every cell of a column the framework defines later, must be consistent with that row's perspective. | 1992 p. 603 (Rule 6) |

## REC: Recursion

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| ZF-REC-001 | note | none | The logic is recursive. It can describe any complex product, an enterprise, an information system or a tool maker; it can be applied to as-is and to-be versions; and it can be applied to the framework itself, since each cell is an engineering product with its own owner, designer and builder. | 1992 pp. 603 to 605 (Rule 7); p. 613 |

## GUID: Guidance and scope

| Id | Strength | Checkable | Rule | Section |
|---|---|---|---|---|
| ZF-GUID-001 | note | none | The framework is a classification, not a method. It prescribes no order in which cells are populated; a methodology chooses a subset of cells and a sequence, and the cell produced first strongly influences the ones that follow. | 1992 p. 591, p. 603; Evolution page, 2011 entry |
| ZF-GUID-002 | note | none | For the people, time and motivation columns the cell contents are hypothetical and the terminology is suggestive, not definitive. The rules of the framework must still be followed when filling those cells. | 1992 pp. 596, 605 |
| ZF-GUID-003 | note | none | The names of the primitives and of the rows and columns have changed over time (the function connector was renamed from input and output to argument; the work connector is read as work product; the 2011 version renamed rows and columns for a business audience) without changing the structure or the rules. | 1992 p. 597; Evolution page, 2011 entry |
| ZF-GUID-004 | note | none | The framework defines no relationship notation, no diagram type and no drawing rule. It classifies descriptions; each cell may use whatever notation suits it. | 1992 pp. 591, 593 |
| ZF-GUID-005 | note | none | The entity at the scope row is the same kind of thing as the owner row's entity, only at a higher level of aggregation. It supports the decision about where to invest, so the entities not selected are as significant as those selected. | 1987 p. 284 |
