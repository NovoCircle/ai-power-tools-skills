# The Zachman Framework, in our own words

This reference restates the framework as its author and co-author published it. It is a summary, not a copy. Short phrases in quotation marks are under 15 words.

**Sources.**

- **1987**: J. A. Zachman, "A framework for information systems architecture", IBM Systems Journal 26(3), 1987, pp. 276 to 292. The origin. It develops the idea and describes three columns.
- **1992**: J. F. Sowa and J. A. Zachman, "Extending and formalizing the framework for information systems architecture", IBM Systems Journal 31(3), 1992, pp. 590 to 616. Six columns, the cell contents, and the seven rules of the framework (pp. 599 to 604, restated pp. 611 to 613).
- **Evolution page**: Zachman International's account of how the framework's graphic changed from 1984 to 2011. It is the source for the sixth row, for instances, for the primitive versus composite distinction, and for the 2011 wording. It was read as the author's own account; it is not a specification.

Page numbers are the journal's printed pages. The framework is **not a formal standard**. It is a classification scheme defined by its author, with no normative text and no machine-readable model.

## 1. What the framework is

It is a two-dimensional classification schema, a "periodic table" for the descriptions of an enterprise (1992 p. 602). One axis is six **columns**, the interrogatives what, how, where, who, when and why. The other axis is six **rows**, the perspectives of the people who describe or build the thing, from the planner who scopes it to the functioning enterprise itself. Where a row and a column meet is a **cell**, and every cell is a different kind of description.

It is **not a notation, a method or a metamodel with relationships**. It says what kinds of description exist and how they differ. It says nothing about how to draw them, in what order to produce them, or what tool to use (1992 pp. 591, 603; Evolution page, 2011). Each cell can use whatever notation suits it; the papers give examples only.

The idea comes from architecture and manufacturing. A building has an architect's sketch for the owner, drawings, plans for the designer, the contractor's plans, shop plans for the subcontractor and then the building. A house also has a bill of materials, functional specifications and floor plans, which are different descriptions of the same thing. Put the two together and you get a grid (1987 pp. 277 to 284).

## 2. Columns

The six columns are abstractions of one reality. Each isolates one variable and suppresses the rest, to contain the complexity of the design problem (1992 p. 593). They have **no order** (Rule 1, below).

Each column has a **basic model** made of two primitives: a **columnar variable** (the thing the column is about) and a **connector** (how two of them relate). The basic model is the same for every cell in the column.

| Column | Question | Name | Columnar variable | Connector | Basic model |
|---|---|---|---|---|---|
| A | what | Data | Entity | Relationship | entity - relationship - entity |
| B | how | Function | Function | Argument | function - argument - function (the 1987 paper reads input - process - output) |
| C | where | Network | Node | Link | node - link - node |
| D | who | People | Agent | Work | agent - work - agent |
| E | when | Time | Time (an event) | Cycle | event - cycle - event |
| F | why | Motivation | Ends | Means | ends - means - ends |

Notes from the papers: the function column's connector was renamed from "input/output" to argument, because "work product" belongs to the people column and the two should not be confused (1992 p. 597). The agent in the people column may be a person or a machine, so the paper prefers "agent" to "user". Columns A to C were described first and have long-established formalisms; columns D to F are, in the authors' words, more hypothetical, and their terminology is "suggestive, but not definitive" (1992 pp. 596, 605).

The 2011 version renamed the columns for a business audience (as reported: Process Flows, Distribution Networks, Responsibility Assignments, Timing Cycles; the first and last described as inventory and motivation). It did not change their meaning.

## 3. Rows

A row is a perspective, with its own constraints. It is not a level of detail. The model for the designer is different in nature, content and meaning from the owner's, not the owner's model with more detail added (1987 p. 281; 1992 p. 593).

| Row | Perspective | Model | What it deals with |
|---|---|---|---|
| 1 | Planner | Scope | The gross size and scope. Lists of classes, enough to decide where to invest. |
| 2 | Owner | Enterprise (business) model | The business as the owner understands it. Usability constraints. |
| 3 | Designer | System model | The logical design of the system that serves the business. Design constraints, the laws of nature. |
| 4 | Builder | Technology model | The physical design under the limits of the chosen technology. Construction constraints. |
| 5 | Subcontractor | Components | Parts specified out of context of the whole. |
| 6 | Functioning enterprise | Functioning system | The enterprise actually operating. Instances of what rows 1 to 5 describe. |

The 1992 paper numbers five rows, 30 cells, and shows the functioning system beneath them. The author's account of the later graphics treats the sixth row as part of the framework: abstractions live in rows 1 to 5, and the result of the architecture, the enterprise with its instances, is row 6 (Evolution page, 2001 and 2011). In the 2011 account the six rows are the reification steps of an idea: identification, definition, representation, specification, configuration and instantiation. Their audience names in 2011 are reported as Executive, Business Management, Architect, Engineer, Technician and Enterprise.

**Row constraints are additive.** The constraints of a lower row are added to the model of the row above, to give a new model at a new perspective. The new model should still allow the higher-row model to be inferred from it. When a lower-row constraint conflicts with the higher-row model, the people responsible for the two rows talk and the owner is told and offered an alternative (1992 p. 593).

## 4. Cells

Each cell holds a primitive model of its column's basic form, with the primitives given the meaning the row gives them. The meaning of "entity" is a business entity for the owner, a data entity for the designer, a segment or row for the builder, a field for the subcontractor (1987 pp. 284 to 288; 1992 p. 601).

The cells, by column. The first name is the cell's description; the second and third are the variable and the connector at that row's meaning.

**Column A, Data (what)**

| Row | Cell | Entity | Relationship |
|---|---|---|---|
| 1 | list of things important to the business | a class of business thing | not defined |
| 2 | semantic model | business entity | business rule or constraint |
| 3 | logical data model | data entity | data relationship |
| 4 | physical data design | segment or row, by technology | pointer or key |
| 5 | data definition | field | address |
| 6 | the data held | instance | instance |

**Column B, Function (how)**

| Row | Cell | Function | Argument |
|---|---|---|---|
| 1 | list of processes | a class of business process | not defined |
| 2 | process flow model | business process | business resource |
| 3 | application architecture | application function | user view |
| 4 | system design | computer function | screen or device format |
| 5 | program | language statement | control block |
| 6 | the programs running | instance | instance |

**Column C, Network (where)**

| Row | Cell | Node | Link |
|---|---|---|---|
| 1 | list of locations | major business location | not defined |
| 2 | logistics network | business unit at a location | business linkage |
| 3 | distributed system architecture | system function (processor, storage) | conceptual line type |
| 4 | system architecture | hardware and system software | line specification |
| 5 | network architecture | address | protocol |
| 6 | the network in place | instance | instance |

**Column D, People (who)**. Partly garbled in the text layer; read with care.

| Row | Cell | Agent | Work |
|---|---|---|---|
| 1 | list of organizations | major organization unit | not defined |
| 2 | organization (work) model | organization unit | work product |
| 3 | human interface architecture | role | deliverable |
| 4 | presentation architecture | user | job |
| 5 | security architecture | identity | transaction |
| 6 | the people working | instance | instance |

**Column E, Time (when)**

| Row | Cell | Time | Cycle |
|---|---|---|---|
| 1 | list of events | major event | major cycle |
| 2 | master schedule | business event | business cycle |
| 3 | processing structure | system event | processing cycle |
| 4 | control structure | execute | component cycle |
| 5 | timing definition | interrupt | machine cycle |
| 6 | the schedule followed | instance | instance |

**Column F, Motivation (why)**. Partly garbled in the text layer; hypothetical in the source.

| Row | Cell | Ends | Means |
|---|---|---|---|
| 1 | list of objectives | major objective | major strategy |
| 2 | business plan | business objective | business strategy |
| 3 | knowledge architecture | criterion | option |
| 4 | knowledge design | condition | action |
| 5 | knowledge definition | subcondition | step |
| 6 | the strategy followed | instance | instance |

The scope row is a list. The 1987 paper says that in the scope cell one "might not expect to be definitive about" the relationship between entities, and that its entity is the owner row's entity at a higher level of aggregation (p. 284). The scope row's job is to support the decision of where to invest by putting the whole list in front of the planner; the items not chosen are as telling as those chosen.

## 5. The seven rules of the framework (1992, pp. 599 to 604; 611 to 613)

1. **The columns have no order.** Order implies priority and creates a bias toward one aspect. The paper's examples: programmers who want function first, data people who want data first. The tabular order is a concession to flat displays. The formalization draws the six as peers (p. 599, p. 611).
2. **Each column has a simple, basic model.** One columnar variable, one connector, the same for every cell of the column. It is generic because it is the same for each cell and "meta" because it is a model of the enterprise model (pp. 600 to 601, 611).
3. **The basic model of each column is unique.** No primitive repeats, in name or in concept, in another column. Entity is not function; relationship is not argument. They may be related because they abstract the same enterprise, but they are separate concepts (pp. 601, 612).
4. **Each row is a distinct, unique perspective.** It deals with different constraints, so the meaning of a column's primitive changes from row to row. Owner: usability constraints. Designer: design constraints. Builder: construction constraints (pp. 601 to 602, 612).
5. **Each cell is unique.** Follows from rules 3 and 4. No meta entity appears in more than one cell: business entity only in the owner's data cell, data entity only in the designer's data cell, business process only in the owner's function cell, application function only in the designer's function cell. The cells work as a classification, "like chemical elements", and the entities combine into compounds. A corollary: different cells call for different notations, and widening one cell's notation to carry another's content complicates the design and can damage the other (pp. 602 to 603).
6. **The integration of all cell models in one row is a complete model from that row's perspective.** Each new cell must fit the row's perspective. At a minimum each cell is related to every other cell in its row, and within a column each cell depends on the one above and the one below. A change in one cell is likely to affect them (p. 603).
7. **The logic is recursive.** It applies to a building, an airplane, an enterprise, an information system, a tool maker; it applies to as-is and to-be versions; and it applies to the framework itself, since each cell is an engineering product with its own owner, designer and builder (pp. 603 to 605, 613).

## 6. Primitive and composite models

The author's later account draws a distinction the 1992 paper only hints at ("compounds"). A cell holds a **primitive** model: the column's two primitives, nothing else. A model that hard-binds a second column's primitive is a **composite** (Evolution page). The examples from the history: an entity-relationship notation that carried a diamond for a process, and a process notation that carried vertical arrows for controls and mechanisms. Each bound a verb into a model of nouns, or a control into a model of functions, so neither was a pure model of its cell. The author later said cells should hold only primitives (1984, 1987, 1993, 2001 and 2003 entries).

This does not forbid composites as working models. The 1992 paper says primitives combine "in endless ways" into the compounds that real systems need (p. 603). It says that the cell is the element, and that a composite is a combination of elements.

Note that the word "composite" appears in two senses. Rule 6 calls the integration of a row's cell models a "composite". The history calls a model that mixes columns a "composite". In this skill, **Row Composite** is the first and **Composite Model** is the second.

## 7. Transformation, integration and instances

The author's later account states three ideas that the 1992 rules imply.

- **Vertical movement is transformation.** Down a column, each cell is the previous cell's model redesigned for a new perspective, a step of reification, not a more detailed version of it. Level of detail is a variable inside a cell, from high at its top to fine at its bottom (Evolution page, 2004 and 2011; also 1987 p. 281).
- **Horizontal movement is integration.** The cells in a row describe one reality from one perspective and are related (Rule 6).
- **Instances are in the last row only.** Proper nouns and countable occurrences are instances. An instance embedded in a higher row binds things together and makes the architecture rigid. The abstractions are rows 1 to 5; the result is row 6 (Evolution page, 2001).

## 8. What the framework does not define

- Diagram types, symbols, views or viewpoints.
- Relationships or connectors between elements, beyond the connector inside each column's basic model.
- A method, a sequence of cells, or maturity levels. A methodology picks a subset of cells and an order (1992 p. 603).
- The contents of columns D to F beyond the suggestive tables.

## 9. Newer version

**Zachman Framework 3.0, "The Enterprise Ontology"** (2011) is the author's current graphic. Its logic is the same as the 1992 rules; its labels and presentation differ (aliases above; integration lines across rows; row 6 given full weight; the subtitle calling the framework an ontology). This reference describes the earlier six-by-six form. The 3.0 graphic and its cell texts are copyrighted and were not read.
