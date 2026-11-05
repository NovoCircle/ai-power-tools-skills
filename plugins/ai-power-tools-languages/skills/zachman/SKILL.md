---
name: zachman
description: The Zachman Framework for Enterprise Architecture, a six-by-six classification schema for describing an enterprise. Columns are the six interrogatives (what, how, where, who, when, why, standing for data, function, network, people, time, motivation); rows are the perspectives (planner or scope, owner or enterprise model, designer or system model, builder or technology model, subcontractor or components, the functioning enterprise). Use when someone is classifying models or artifacts into Zachman cells, building or reading a Zachman matrix or grid, asking what belongs in a cell (for example the owner's data cell or the designer's function cell), asking whether a model is primitive or composite, or asking what the rules of the framework require (columns have no order, each cell is unique, rows are not levels of detail).
---

# Zachman Framework for Enterprise Architecture

The Zachman Framework is a **classification schema**, not a notation and not a method. It does not tell you how to draw anything or in what order to work. It tells you what kinds of description of an enterprise exist, and how they differ, so each model or artifact can be put in exactly one place. J. A. Zachman published it in 1987; the rules below are the seven rules he and J. F. Sowa stated in 1992. It is not a formal standard, and it has no machine-readable model. Details: `references/standard.md`.

**It defines no diagram types.** The matrix itself is a picture of the schema, not a diagram a model contains. Each cell can use whatever notation suits it; the papers give examples only.

## What you are creating

You are placing descriptions of an enterprise in a grid of **6 columns by 6 rows = 36 cells**, and keeping each description inside its cell. A well-formed use of the framework has these properties:

- Every element or model sits in exactly one cell.
- The concept an element stands for fits the cell it sits in.
- A model in a cell uses only that cell's two primitives and no other column's.
- Instances appear only in the last row.
- Models that mix columns are recognized as composites, not placed in a cell as if primitive.

## Columns: the six interrogatives (no order)

Each column has one basic model made of a **columnar variable** and a **connector**:

| Column | Question | Variable | Connector | Basic model |
|---|---|---|---|---|
| A Data | what | Entity | Relationship | entity - relationship - entity |
| B Function | how | Function | Argument | function - argument - function |
| C Network | where | Node | Link | node - link - node |
| D People | who | Agent | Work (work product) | agent - work - agent |
| E Time | when | Time (event) | Cycle | event - cycle - event |
| F Motivation | why | Ends | Means | ends - means - ends |

The columns have no order. Do not present one as first, primary or "the" place to start.

## Rows: the perspectives (not levels of detail)

| Row | Perspective | Model | What it deals with |
|---|---|---|---|
| 1 | Planner | Scope | Lists of classes; gross scope. |
| 2 | Owner | Enterprise (business) model | The business in the owner's terms. |
| 3 | Designer | System model | Logical design of the system that serves the business. |
| 4 | Builder | Technology model | Physical design under chosen technology. |
| 5 | Subcontractor | Components | Parts specified out of context of the whole. |
| 6 | Functioning enterprise | Functioning system | The enterprise operating; instances of what rows 1 to 5 describe. |

**Rows are not decompositions.** Row 3 is not a more detailed row 2. Each row is a different perspective with different constraints, and the meaning of the column's primitive changes from row to row. Level of detail varies *inside* each cell. If someone says "drill down from row 2 to row 3", correct it: the owner's model is transformed into the designer's, not refined.

## What each cell holds

The primitive's meaning changes with the row. A few examples (the full table is in `references/standard.md` and `language.yaml`):

- **Data**: a class of business thing (1) → business entity (2) → data entity (3) → segment or row (4) → field (5).
- **Function**: a class of business process (1) → business process (2) → application function (3) → computer function (4) → language statement (5).
- **Network**: major business location (1) → business unit at a location (2) → system function such as a processor (3) → hardware and system software (4) → address (5).
- **People**: class of agent (1) → organization unit (2) → role (3) → user (4) → identity (5). *Partly garbled in the source; hypothetical in the paper.*
- **Time**: major event (1) → business event (2) → system event (3) → execute (4) → interrupt (5).
- **Motivation**: major objective and strategy (1) → business objective and strategy (2) → criterion and option (3) → condition and action (4) → subcondition and step (5). *Partly garbled in the source; hypothetical in the paper.*
- **Row 6** holds instances of all of these.

Row 1 cells are lists. They need not define the connector.

## Relationships, in summary

The framework defines no relationships between elements beyond the connector inside each basic model. What it does state, structurally:

- A cell is in exactly one row and one column; each row and column pair is one cell.
- A cell model is held in exactly one cell and uses only that column's two primitives.
- Cells of one row are related to each other, at a minimum; a row's integrated whole is a **Row Composite**, a complete picture from that row's perspective.
- A cell in a column depends on the cell above and below it; down a column the relationship is **transformation**, not decomposition.
- An **Instance** (row 6) instantiates an abstraction from rows 1 to 5.
- A **Composite Model** combines two or more cell models, ordinarily across columns.

## The rules that matter most

Full list with ids, strengths and sources: `references/rules.md`. In order of how often they decide a case:

1. **One cell per element** (ZF-CELL-002). Every element or model is classified into exactly one cell. This is the rule a model can carry: record each element's row and column, and a check can find elements with none, or with two. Everything else below is partly or wholly judgment.
2. **Concept must fit the cell** (ZF-CELL-003). A business entity belongs in the owner's data cell, a data entity in the designer's, a business process in the owner's function cell, an application function in the designer's. The same word in two rows is two different concepts.
3. **Primitive models use only their own column's primitives** (ZF-CELL-004, ZF-PRIM-001, ZF-COL-004). A process drawn inside an entity model, or control arrows drawn inside a process model, makes it a composite (ZF-PRIM-002). Composites are legitimate working models; they are not cell models.
4. **Rows are transformations, not detail** (ZF-ROW-003). Warn when a model is described as "the detailed version of" a model in another row.
5. **Instances in row 6 only** (ZF-ROW-005). A named city, a specific account number or a particular branch is an instance. Row 1 holds the class.
6. **Columns have no order** (ZF-COL-002) and **cells use their own notations** (ZF-CELL-005).
7. **Integration** (ZF-INT-001 to 003): cells of a row are related, and cells in a column depend on their neighbors above and below. Warn when a cell is edited without a look at its neighbors.

Do not extend the framework. It does not define a required order of work, a maturity scale, or a relationship notation; do not invent them.

## Short example: classifying a few things at Westbrook Bank

Westbrook Bank is a fictitious bank used for illustration. Substitute your own enterprise.

| Item | Cell | Why |
|---|---|---|
| "Customer" as the bank's people see it | A2 (data, owner) | A business entity, in business terms. |
| "Customer" as a table of records | A3 (data, designer) | A data entity; a different concept from A2 even with the same name. |
| "Open a retail account" | B2 (function, owner) | A business process. |
| "Account-opening service" in the system | B3 (function, designer) | An application function. |
| Branch network, headquarters, call center | C2 (network, owner) | Business units at locations. |
| Branch manager | D3 (people, designer) | A role. |
| Month-end close | E2 (time, owner) | A business event, with the business cycle that repeats it. |
| "Reduce account-opening time" | F2 (motivation, owner) | A business objective. |
| Account 000123 of one customer | row 6 | An instance; the class "Account" lives in A2 and A3. |

Two cases to flag. A single box labeled "Customer opens an account" that mixes the thing (A) and the process (B) is a **composite**, not a cell model; split it, or keep it as a labeled composite outside the cells. A document that says "the logical design is the detailed version of the business model" contradicts ZF-ROW-003.

## Data types and attributes

Coverage: none. The framework defines no data types and no attributes; its cells name kinds of description and the two primitives of each column, not typed fields. Nothing to look up. `language.yaml` states this under `data_types`.

## How it is drawn

Sizes and spacing come from `../_languages/layout-standard.yaml`, and the concept mapping from `layout` in `language.yaml`.

Coverage: none for symbols. The framework defines no shapes, icons, line styles or connector drawings, and this guide does not invent any; each cell uses whatever notation suits it, and the papers give examples only (`classification.cells[].example_notations`). What the author's figures do show is the layout of the grid: a matrix with the six columns across the top (each heading naming its two primitives), the six rows down the side from scope to the functioning system, and in each cell a caption, a small example sketch and a legend equating each primitive with its meaning at that row. The column order carries no meaning. The 2011 graphic adds integration lines across a row, crooked arrows down a column, and level of detail shown inside each cell. These are illustrations, not requirements. Details and sections: `notation` in `language.yaml`.

## Newer version and limits

This skill describes the six-by-six form with the 1992 naming. The author's 2011 graphic, "Zachman Framework 3.0: The Enterprise Ontology", renamed rows and columns for a business audience and gave row 6 full weight; its logic is the same. Column aliases are in `language.yaml`.

## References

- `references/standard.md`: the framework in our own words, with the full cell tables and the seven rules.
- `references/rules.md`: the 33 rules with ids, strengths, checkability and sources.
- `language.yaml`: columns, rows, all 36 cells, concepts, relationships and rules as data.
