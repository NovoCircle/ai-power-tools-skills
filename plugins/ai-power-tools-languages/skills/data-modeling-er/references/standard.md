# Data modeling and entity-relationship modeling: the language in plain words

This reference describes data modeling as a single language assembled from public sources. There is **no single standard, owner or version** that governs it. Each section says which source it comes from, so you can tell a rule that a formal standard states from a convention that is widely followed. Rule ids (`DATA-...`) refer to `rules.md`; the machine-readable form is `language.yaml`.

Source codes used throughout:

| Code | Source | Nature |
|---|---|---|
| CHEN76 | Peter Chen, "The Entity-Relationship Model: Toward a Unified View of Data", ACM Transactions on Database Systems 1(1), March 1976 | Paper that defines the model and a diagram technique |
| FIPS184 | FIPS PUB 184, Integration Definition for Information Modeling (IDEF1X), NIST, 21 December 1993; withdrawn 2 September 2008 | Formal US federal standard, withdrawn but public. The only precise public definition of a keyed logical data modeling language |
| CODD70 | E. F. Codd, "A Relational Model of Data for Large Shared Data Banks", Communications of the ACM, June 1970 | Paper that defines the relational model |
| KENT83 | William Kent, "A Simple Guide to Five Normal Forms in Relational Database Theory", Communications of the ACM, February 1983 | Tutorial article |
| SQLDOC | A public database manual, chapter on constraints | Public database manual, used for how SQL constraints behave. The ISO SQL standard is paywalled and was not read |
| WIKIER, CFOOT | An encyclopedia article on the entity-relationship model and an online crow's foot notation article (August 2026) | Secondary sources, used only for notation conventions and marked wherever used |

The later IDEF1X standard, IEEE 1320.2-1998 (IDEF1X97), is paywalled and was not read. Where this reference says "IDEF1X" it means the 1993 federal standard.

---

## 1. Levels of a data model

Data models are built at several levels of detail, and the sources use two different ideas of "level".

**The conceptual-logical-physical tradition (WIKIER, secondary).**

- A **conceptual** model has the least detail. It fixes scope and the main things (master entities) of the business.
- A **logical** model adds detail: operational and transactional entities, their attributes, identifiers and relationships. It does not depend on any particular database product.
- A **physical** model has enough detail to build a database, and depends on the product. It is expressed as tables, columns, keys, indexes and constraints.

**Chen's four levels of logical view (CHEN76 2.1).** Chen separates information about entities and relationships as they exist in our minds (level 1), the structure of information that represents them (level 2), data structures that do not depend on access paths (level 3), and structures that do (level 4). The entity-relationship model covers the first two levels; the relational model covers levels 3 and 2 (Chen's reading).

**IDEF1X's three view levels (FIPS184 3.10).** All three describe one logical model, in increasing completeness:

- the **entity-relationship (ER) level** has entities and relationships, may have attributes, and records no keys;
- the **key-based level** adds primary, alternate and foreign keys, and requires every entity to have a primary key;
- the **fully-attributed level** adds every relevant non-key attribute.

A model may contain views of several levels (DATA-LVL-005). These two ideas of level are different axes. IDEF1X's levels refine a logical model; the conceptual-logical-physical levels describe how far a model is from the database. See DATA-LVL-001 to DATA-LVL-008.

---

## 2. Chen's entity-relationship model

**Entities.** An entity is a thing that can be distinctly identified: a specific person, company or event. Entities of one kind form an entity set (Employee, Project, Department). The diagram shows sets, and the word "entity" in everyday use usually means the set. Entity sets need not be disjoint: a male person also belongs to the set of persons, so one set can be a subset of another (CHEN76 2.2.1; DATA-CAT-013). Chen leaves it to the modeling authority of the enterprise to decide whether something such as a marriage is an entity or a relationship (DATA-ENT-007).

**Relationships.** A relationship is an association among entities. A relationship set is a mathematical relation over entity sets, and each tuple of entities is a relationship. It may involve one entity set (a part that is a component of another part), two or more than two (supplier, project and part) (DATA-REL-009). More than one relationship set may be defined on the same entity sets (project worker and project manager both join employees and projects).

**Roles.** The role of an entity in a relationship is the function it performs there: husband and wife in a marriage (DATA-REL-011).

**Attributes and value sets.** Facts about an entity or relationship are attribute-value pairs. Values such as "3" or "red" belong to value sets such as feet or color. An attribute is a function that maps an entity (or relationship) to a value or to a combination of values, so a name can map to first name together with last name (DATA-ATT-006). Relationships can have attributes: the percentage of time an employee is committed to a project belongs to neither the employee nor the project, only to the pairing (CHEN76 2.2.3).

**Keys and weak entities.** An entity is identified by a key: a group of attributes that maps one-to-one onto the entities. When no natural key exists, define an artificial attribute (DATA-KEY-008). Some entities cannot be identified by their own attributes alone. A dependent of an employee is identified by the dependent's name together with the supporting employee's key. Chen calls these **weak entities**, and restricts the identifying relationship to a binary one-to-many relationship in which the existence of the many side depends on the one side (DATA-ENT-005). A relationship is identified by the keys of the entities it involves (DATA-REL-012).

**Diagram technique.** An entity set is a rectangle and a relationship set is a diamond; lines join them, and roles are written on the lines. The mapping of a relationship is written as 1, m or n: one-to-many, many-to-many, one-to-one. A minimum number may also be specified. An arrow in the relationship between employee and dependent shows that a dependent's existence depends on its employee, and the dependent entity set is drawn as a special rectangle (CHEN76 3.1; DATA-REL-010). Chen's paper shows attributes in tables; ovals for attributes, underlined keys and double lines for total participation are later conventions (WIKIER, secondary).

**Integrity.** Chen shows that explicit entities and relationships make integrity rules clearer. Deleting an entity deletes the entities whose existence depends on it and the relationships that involve it (CHEN76 3.5; DATA-ENT-006).

**Relation to the relational model.** Entity and relationship sets map to tables ("relations"): an entity set to an entity relation, a relationship set to a relationship relation whose key is made of the keys of the entities involved, a weak entity to a table whose key includes the owner's key. Chen observes that this comes out close to third normal form but with clearer meaning (CHEN76 2.3, 4.1.3; DATA-NRM-007).

---

## 3. IDEF1X

IDEF1X was developed from the US Air Force's integrated computer-aided manufacturing program, drawing on the relational model, Chen's model and the generalization concepts of Smith and Smith. It describes the syntax, semantics and rules for building a logical model of data that can be turned into a database design (FIPS184 1.2, Background). It is withdrawn as a federal standard, but remains the clearest public rule book. Where a rule is specific to it, `language.yaml` marks it `applies_when: idef1x`.

### 3.1 Entities, attributes and domains

An **entity** represents a set of real or abstract things with common characteristics; an individual is an entity instance (FIPS184 3.1). An entity is **identifier-independent** if each instance can be identified without knowing its relationships, and **identifier-dependent** if identification depends on a relationship to another entity (DATA-ENT-004). Each entity has a unique name, a singular noun phrase, and appears once per diagram (DATA-ENT-003, DATA-ENT-008, DATA-NAM-002).

A **domain** is a named set of values of one data type. A **base domain** has a type (character, numeric, boolean by default; dates and others allowed) and optionally a **value list** or a **range**. A **typed domain** narrows a base domain or another typed domain; domain subtyping must not contain a cycle. Domains are defined once and reused, and a value must satisfy the rules of its domain and all its ancestors (DATA-ATT-007 to DATA-ATT-010).

An **attribute** is a domain used in an entity. Every attribute is owned by exactly one entity, which is the **single-owner rule**; an instance has at most one value for an attribute, the **no-repeat rule**; every primary key attribute has a value; a non-key attribute that may be null is marked optional (DATA-ATT-001 to DATA-ATT-005).

### 3.2 Relationships

IDEF1X has three constructs.

**Specific connection relationships (parent-child).** Each child instance relates to zero or one parent instance; a parent relates to many. The parent's primary key is contributed to the child as a **foreign key** (see 3.4). There are three kinds:

- **Identifying.** The whole parent key becomes part of the child's primary key. Each child has exactly one parent. The child is identifier-dependent. Drawn as a solid line, child box with rounded corners.
- **Mandatory non-identifying.** The parent key is a non-key attribute of the child; the child must have exactly one parent. Dashed line.
- **Optional non-identifying.** As above, but the child may have no parent. Dashed line with a small diamond at the parent end.

Cardinality is stated at the child end: zero, one or more (the default), `P` for one or more, `Z` for zero or one, an exact number, or a range; anything else is recorded in a note (DATA-REL-004). A relationship is named with a verb phrase from the parent's perspective, with an optional second phrase for the reverse (DATA-REL-006, DATA-REL-014). Only non-identifying relationships may be recursive (DATA-REL-005).

**Categorization relationships.** One generic entity (supertype) and one or more category entities (subtypes). A **category cluster** is a set of mutually exclusive categories. The cluster is **complete** when every generic instance belongs to a category, **incomplete** otherwise. An optional **discriminator** attribute in the generic entity says which category an instance belongs to. A category has the same primary key as its generic entity, and is always identifier-dependent. An entity may be generic in several clusters, and a category may be generic in another (DATA-CAT-001 to DATA-CAT-013). Drawn as a circle with an underline: one line for incomplete, two for complete.

**Non-specific relationships (many-to-many).** Allowed only at the ER level. They are replaced by specific relationships, usually through an **associative (intersection) entity** that is a child of both original entities (DATA-REL-007, DATA-REL-008). The standard mentions the associative entity in passing and does not define it.

### 3.3 Keys

- A **candidate key** is one or more attributes whose values uniquely identify every instance; it contains no unneeded attribute (smallest-key rule, DATA-KEY-001).
- The **primary key** is the candidate key chosen as identifier; the others are **alternate keys**. Every entity has a primary key at the key-based and fully-attributed levels (DATA-ENT-001).
- A **foreign key** results from **migrating** the parent's (or generic's) primary key into the child (or category). Only primary key attributes migrate; every child holds one foreign key for each relationship in which it is child, with as many attributes as the parent's primary key (DATA-KEY-003, DATA-KEY-004).
- A foreign key whose attributes are all part of the child's primary key makes the relationship identifying; if only part of the key lies in the child's primary key (a "split key") the relationship is non-identifying (DATA-REL-003).
- A **role name** is given to a migrated attribute when the same key reaches an entity more than once. Occurrences whose values may differ get different role names; occurrences that must be equal get the same name (DATA-KEY-005, DATA-KEY-006).

### 3.4 Notes, glossary and lexical rules

Every model has a statement of purpose, a statement of scope and a description of the author's conventions (DATA-LVL-006). It has a glossary defining every view, entity and domain (DATA-NAM-001). Notes, numbered in parentheses, carry constraints that cannot be drawn. Path assertions say whether an ancestor reached by two paths must be the same instance or different ones; exclusive-or between relationships is also a note (DATA-REL-015, DATA-REL-016). IDEF1X also sets lexical rules: names begin with a letter, use letters, digits, dashes, underscores and spaces, up to 120 characters, and are case insensitive (DATA-NAM-003).

### 3.5 Normalization inside IDEF1X

The standard words two normal form requirements as rules for key-based and fully-attributed views: every non-key attribute depends on the whole primary key, and no non-key attribute depends on another non-key attribute (FIPS184 3.8.3(g)(h)). This language treats normal forms as guidance (section 8).

---

## 4. Crow's foot (information engineering) notation

Crow's foot has no governing document that I could read. It descends from the information engineering method and from the early diagrams of Gordon Everest (1976) and was spread by the CASE tools of the 1980s (WIKIER, secondary). Two secondary sources describe it and agree.

- **Entities** are boxes, attributes are listed inside, relationships are lines.
- **Symbols at a line end** come in pairs. The **outer** symbol is the maximum and the **inner** one the minimum. A **bar** means one, a **crow's foot** (three prongs) means many, a **ring** means zero. The four cases are exactly one (bar, bar), zero or one (ring, bar), one or more (bar, crow's foot) and zero or more (ring, crow's foot). The crow's foot article's prose and its table differ on which mark is the maximum, and this reference follows the table (CFOOT).
- The symbols at an end describe the entity at that end. Read the line starting from the other entity: a crow's foot next to Order on a Customer-to-Order line means one customer has zero or more orders. Every relationship has two readings and both should be true (CFOOT section 02; DATA-REL-014).
- **Relationships cannot carry attributes.** A fact about the association (when and where an artist performed a song) makes it an associative entity (DATA-REL-013).
- **Identifying and non-identifying.** A solid line is conventionally an identifying relationship, where the parent's key is part of the child's key. A dashed line means the foreign key is an ordinary attribute. Tools disagree on this; show the key in the box as well (CFOOT section 03).
- **Many-to-many** is legal in a conceptual model and must be resolved before a physical design (DATA-REL-007, DATA-PHY-010).

I found no public description of subtype symbols in crow's foot. This language therefore uses IDEF1X's category cluster for subtypes.

---

## 5. The three cardinality notations side by side

All three state a count "look across": the mark at one end says how many instances of that end's entity go with one instance of the other.

| Meaning | Chen | Crow's foot | IDEF1X |
|---|---|---|---|
| Exactly one | `1` on that side | Bar and bar | No mark at the parent end (identifying, mandatory) |
| Zero or one | `1` with an arrow or no total participation mark (secondary) | Ring and bar | `Z` beside the child dot; small diamond at an optional parent end |
| Zero or more | `n` or `m` | Ring and crow's foot | Plain dot at the child end (default) |
| One or more | `n` with minimum 1, or a double line (secondary) | Bar and crow's foot | `P` beside the child dot |
| Exactly n, or n to m | A minimum and maximum may be given | Not expressible, use a note | Number or range beside the dot |
| Many-to-many | m:n relationship | Crow's foot at both ends | Non-specific relationship, ER level only |
| Identifying | Weak entity with existence dependence | Solid line (tool-dependent) | Solid line, rounded child |
| Non-identifying | Regular entity | Dashed line | Dashed line |

These are conventions for drawing. They are not constraints. The constraints that sit behind them (DATA-REL-002, DATA-REL-004, DATA-LVL-001 to DATA-LVL-003) apply whichever notation is used.

---

## 6. Physical level: relations, keys and SQL constraints

**Relations and tables.** In the relational model (CODD70 1.3) a relation is a set of rows (tuples), all distinct, over named domains; row order does not matter. The columns are identified by name, and when two columns share a domain a role name tells them apart (DATA-PHY-001). A table in a SQL database is the practical form.

**Keys.** A domain or combination that uniquely identifies each row is a **primary key**. A relation may have several keys that are not redundant, one chosen as the primary key. A **foreign key** is a column or combination that is not the table's own primary key but whose values are values of the primary key of some table, possibly the same table. Relational theory says every table has a primary key; SQL does not enforce it, and the manual advises following the rule (SQLDOC 5.5.4; DATA-PHY-002).

**SQL constraints** (SQLDOC 5.5):

- A **primary key constraint** makes the columns unique and not null; a table has at most one (DATA-PHY-003, DATA-PHY-004).
- A **unique constraint** makes a column or group unique; any number per table. By default two nulls are not equal, so rows with nulls may repeat; this is implementation-defined (DATA-PHY-012).
- A **not null constraint** forbids null in a column. Most columns should be not null (DATA-PHY-014).
- A **check constraint** is a Boolean condition on one row. It passes when the result is true or null (DATA-PHY-015).
- A **foreign key constraint** requires that values in the referencing columns match a row of the referenced table. The target is the primary key, or a unique constraint, of that table. Column counts and types match. A table may reference itself (DATA-PHY-005 to DATA-PHY-007, DATA-PHY-016).
- **Referential actions.** When a referenced row is deleted or its key updated, the constraint's action is one of: no action (the default; the check can be deferred), restrict (the change is refused at once), cascade (referencing rows are deleted or updated too), set null, or set default. Cascade suits a child that is a component of the parent and cannot exist alone. Restrict or no action suits independent tables. Set null or set default suit optional relationships (DATA-PHY-008, DATA-PHY-009).
- **Matching.** By default a row satisfies the foreign key if any referencing column is null; with a full match it satisfies it only if all are null (DATA-PHY-007).
- **No many-to-many.** A third, association table holds a foreign key to each side. The two foreign keys together often form its primary key, which also prevents the same pairing twice (DATA-PHY-010).
- **Indexes.** A primary key and a unique constraint are enforced through unique indexes. A foreign key does not create an index on the referencing columns; index them if the referenced rows are deleted or updated often. An index is logically redundant: it can be added or dropped without changing what the data means (CODD70 1.2.2; DATA-PHY-011 to DATA-PHY-013).

---

## 7. From logical model to physical design

The sources describe the logical model as the thing that gets transformed into a physical design (FIPS184 1.2(d), CHEN76 2.3). A conventional mapping, partly stated and partly inferred, is:

| Logical | Physical | Rule |
|---|---|---|
| Entity | Table | DATA-MAP-001 |
| Attribute | Column; a product of value sets becomes several columns | DATA-MAP-001, DATA-MAP-008 |
| Domain and domain rule | Column data type and check constraint | DATA-MAP-007 |
| Primary key | Primary key constraint | DATA-MAP-001 |
| Alternate key | Unique constraint | DATA-MAP-001 |
| Foreign key | Foreign key constraint with a referential action | DATA-MAP-001, DATA-PHY-009 |
| Identifying relationship | Foreign key columns are part of the child's primary key, not null | DATA-MAP-002, DATA-MAP-003 |
| Non-identifying relationship | Foreign key columns are ordinary columns; not null if mandatory, nullable if optional | DATA-MAP-002, DATA-MAP-003 |
| Many-to-many or relationship with attributes | Association table with a foreign key to each side; its key is normally the combination of those keys | DATA-MAP-004 |
| Weak entity | Table whose primary key is the owner's key plus a partial key, with a foreign key to the owner | DATA-MAP-006 |
| Category cluster | Separate category tables keyed by the generic's key (also a foreign key to it), or another strategy | DATA-MAP-005 |

The sources do not say how to choose among ways of implementing subtypes. They do not describe views, stored procedures, triggers or product-specific data types.

---

## 8. Normal forms are guidance

Normalization is the process of regrouping attributes to avoid update anomalies. It is a set of design guidelines, not obligations (KENT83 intro, section 7).

| Form | Guideline | Rule |
|---|---|---|
| First | Every attribute is single-valued: no repeating groups. A matter of definition rather than design choice | DATA-ATT-002 |
| Second | A non-key attribute is a fact about the whole key, not a part of it. Only matters when the key is composite | DATA-NRM-001 |
| Third | A non-key attribute is not a fact about another non-key attribute: "the key, the whole key, and nothing but the key" | DATA-NRM-002 |
| Fourth | An entity does not hold two or more independent multi-valued facts about the same thing | DATA-NRM-003 |
| Fifth | An entity whose information can be rebuilt from smaller pieces is split; differs from the fourth only where a symmetric constraint exists | DATA-NRM-004 |

Normalization prevents redundancy but can cost retrieval performance. If you denormalize deliberately, record why (DATA-NRM-005). Normal forms are defined only where identifiers are unique and singular; the same fact written two ways hides a violation (DATA-NRM-006). IDEF1X words the second and third forms as rules; this language lists them as `should`, because the sources read do not word them as requirements for every model. Boyce-Codd normal form is common in practice but none of the sources read defines it.

---

## 9. The well-formedness rules that matter most

1. Every entity at the key-based level or below has a primary key (DATA-ENT-001). Every table has one (DATA-PHY-002).
2. Every foreign key references a key: the parent's primary key logically (DATA-KEY-003), a primary key or unique constraint physically (DATA-PHY-005), with matching column count and types (DATA-PHY-006).
3. No many-to-many relationship survives past the entity-relationship level, or at the physical level (DATA-REL-007, DATA-PHY-010).
4. A single attribute has a single owner and a single value (DATA-ATT-001, DATA-ATT-002).
5. A child's relationship to its parent is identifying exactly when the parent's key is wholly in the child's key (DATA-REL-003).
6. A category has its generic's key and is always dependent (DATA-CAT-004, DATA-CAT-005).
7. Referential integrity holds: every non-null foreign key matches a parent (DATA-KEY-007, DATA-PHY-007).
8. A relationship has no attributes in IDEF1X and crow's foot; an associative entity carries them (DATA-REL-013).

## 10. What the sources do not say

- No single list of diagram types. This language describes six drawing forms (Chen diagram, the three IDEF1X views, crow's foot diagram, physical diagram).
- No notation for the physical model.
- No complete definition of crow's foot, no subtype notation in it, and no rule for which end a line style identifies.
- Nothing about temporal data, multidimensional (warehouse) design, document or graph stores, or database-product-specific features.
- Nothing about a business glossary beyond the IDEF1X glossary rule.
