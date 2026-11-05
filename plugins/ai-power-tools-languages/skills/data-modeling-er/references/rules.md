# Data modeling and entity-relationship modeling: rules

Generated from `language.yaml` (`constraints`). Do not edit by hand; change the language file and regenerate.

Each rule has a stable id of the form `DATA-<CAT>-nnn`. The number never changes once assigned. A rule that is retired keeps its id and is marked withdrawn rather than reused.

This language has no single governing standard. Each rule cites the source it comes from (codes are explained in `references/standard.md`): CHEN76 (Chen, 1976), FIPS184 (IDEF1X, 1993, withdrawn), CODD70, KENT83, PGDOC (a public database manual), and the secondary sources WIKIER and CFOOT. "[reconstructed]" marks a rule that is our reading rather than a sentence of a source.

## Strength

| Strength | Meaning |
|---|---|
| must | A source states it as a requirement, a rule of the language or a constraint of the model. A model that breaks it is not well formed. |
| should | A source gives it as guidance, or a rule is stated by a source but this language treats it as guidance (the second and third normal forms). Breaking it is a warning, not an error. |
| note | A source states it as an expectation, an option, a convention or an observation. It is recorded for completeness and is not checkable on its own. |

## Scope: `applies_when`

| Token | Applies to |
|---|---|
| (none) | Always |
| keyed-level | Models that record keys: IDEF1X key-based and fully-attributed views, and any logical model with attributes and identifiers |
| er-level | The IDEF1X entity-relationship level, where keys are not recorded |
| chen | Chen's model and diagram technique |
| idef1x | IDEF1X notation |
| idef1x-or-crows-foot | A model drawn in IDEF1X or crow's foot notation |
| physical | The table level |

`checkable` says what can verify a rule: `static` (the saved structure alone), `partial` (the structure only, or simple cases), `runtime` (needs instance data), `none` (judgment or documentation).

## Categories

| Category | Name | Covers | Rules |
|---|---|---|---|
| ENT | Entities and identification | What an entity is, how it is identified, dependence and uniqueness of names. | 9 |
| ATT | Attributes and domains | Ownership, single values, nulls, domains and their rules. | 10 |
| KEY | Keys | Candidate, primary, alternate and foreign keys, migration, role names and referential integrity at the logical level. | 8 |
| REL | Relationships and cardinality | Connection, non-specific and Chen relationships, participation, cardinality and naming. | 17 |
| CAT | Subtypes and supertypes | Categories, clusters, discriminators and their keys. | 13 |
| LVL | Model levels and completeness | What a conceptual, key-based or fully-attributed view must and may contain; model statements. | 8 |
| NAM | Names and documentation | Glossary, naming style and lexical rules. | 6 |
| PHY | Physical level | Tables, columns, primary, foreign and unique keys, referential integrity, indexes. | 16 |
| MAP | Logical to physical | How logical constructs become physical ones. | 8 |
| NRM | Normalization guidance | Normal forms as guidance; trade-offs. | 7 |

Totals: 102 rules, 64 must, 16 should, 22 note.

Section references are to the numbered sections and pages of the sources (see the source codes above); "p." gives the printed page.

## ENT: Entities and identification

| Id | Strength | Checkable | Applies when | Rule | Section |
|---|---|---|---|---|---|
| DATA-ENT-001 | must | static | keyed-level | Every entity has at least one candidate key and exactly one candidate key is designated the primary key. The key attributes are owned by the entity or migrated into it through a relationship. | FIPS184 3.1.3(c), 3.8.1, 3.8.3(a), pp. 9, 26-27; CHEN76 2.3.1, p. 14 |
| DATA-ENT-002 | note | none | er-level | At the entity-relationship (conceptual) level no keys are recorded, but the instances of each entity must still be distinguishable. Say how in the entity definition. [reconstructed] | FIPS184 3.10.1, 3.10.3(b), pp. 31-32; CHEN76 2.3.1 |
| DATA-ENT-003 | must | static | always | Each entity has a unique name in the model. The same name always has the same meaning, and the same meaning is not carried by different names unless they are aliases. No view contains two entities whose names are synonyms. | FIPS184 3.1.3(a)(f)(g), p. 9; B.5.3.5 |
| DATA-ENT-004 | must | static | keyed-level | An entity is identifier-dependent exactly when it is the child in an identifying relationship or a category in a categorization. Every other entity is identifier-independent. A child in an identifying relationship is always dependent; a child in only non-identifying relationships stays independent. | FIPS184 3.1.3(e), 3.5.4(e)(f), 3.6.2, B.5.3.13, pp. 9, 20, 22 |
| DATA-ENT-005 | must | static | chen | A weak entity cannot be identified by its own attribute values alone. It is identified by those values together with the key of one owner entity, through a binary one-to-many relationship in which the existence of the weak entity depends on the owner. | CHEN76 2.3.2, pp. 17-18 |
| DATA-ENT-006 | must | runtime | always | An existence-dependent instance never exists without its parent or owner. Deleting the parent either deletes the dependents or is refused. Existence dependence arises from weak entities, identifying relationships, categorizations and mandatory non-identifying relationships. | CHEN76 3.5 Table III, p. 25; FIPS184 2.27, p. 3 |
| DATA-ENT-007 | note | none | always | Whether something is modeled as an entity or as a relationship is a modeling decision. Let one authority settle it for the enterprise so the choice is consistent. | CHEN76 2.2 footnote 1, p. 10 |
| DATA-ENT-008 | must | static | always | An entity appears at most once in a given diagram, though it may appear in any number of diagrams and views. | FIPS184 3.1.2, p. 9 |
| DATA-ENT-009 | note | none | always | One real-world thing may be represented by more than one entity in a view (a person as both employee and buyer), and one instance may stand for a combination of things (a married couple). | FIPS184 3.1.1, p. 7 |

## ATT: Attributes and domains

| Id | Strength | Checkable | Applies when | Rule | Section |
|---|---|---|---|---|---|
| DATA-ATT-001 | must | static | keyed-level | Every attribute is owned by exactly one entity (single-owner rule). An attribute reaches another entity only by migrating as a foreign key. An attribute that does not apply to all instances of an entity belongs on a category entity. | FIPS184 3.4.1, 3.4.3(b)(c), B.5.3.15-16, pp. 13-14, 141-142 |
| DATA-ATT-002 | must | partial | always | An instance of an entity has at most one value for each of its attributes (no-repeat rule). A repeating group is not an attribute; model it as a further entity. | FIPS184 3.4.3(e), p. 15; CHEN76 2.2.3, p. 12; CODD70 1.4, p. 381 |
| DATA-ATT-003 | must | runtime | always | Every instance has a value for every attribute in its primary key. | FIPS184 3.4.3(d), B.5.3.10; PGDOC 5.5.4 |
| DATA-ATT-004 | must | static | keyed-level | A non-key attribute that may be null is marked optional. A primary key attribute is never optional. | FIPS184 3.4.3(f), B.5.3.10, pp. 15, 139 |
| DATA-ATT-005 | must | static | idef1x | Every attribute is defined on exactly one domain. Several attributes may share a domain. | FIPS184 2.19, 3.4.3(a), p. 3 |
| DATA-ATT-006 | note | none | chen | In Chen's model an attribute is a function from an entity set or relationship set into a value set or a product of value sets (a name drawn from first-name and last-name). Attribute and value set are distinct even when they share a name. | CHEN76 2.2.3, p. 12 |
| DATA-ATT-007 | must | static | always | A domain is a base domain or a typed domain. A typed domain narrows exactly one base or typed domain and references it. No domain is, directly or indirectly, a narrowing of itself. | FIPS184 3.2.3(b)(h)(i)(j), B.5.3.2, pp. 11-12, 136 |
| DATA-ATT-008 | must | runtime | always | A domain rule is a value list or a range. A value must satisfy its own domain rule and the rules of every ancestor domain. An alias domain has no rule of its own. | FIPS184 3.2.1, 3.2.3(d)-(g), B.5.3.4, pp. 10-11, 137 |
| DATA-ATT-009 | note | none | always | A base domain has a data type: character, numeric or boolean by default. Other types such as dates, times and binary may also be used. | FIPS184 3.2.1, 3.2.3(c), pp. 10-11 |
| DATA-ATT-010 | must | runtime | always | Each value in a domain has a unique representation within that domain (state names, abbreviations or numbers, but not the first letter alone). | FIPS184 3.2.1, p. 10 |

## KEY: Keys

| Id | Strength | Checkable | Applies when | Rule | Section |
|---|---|---|---|---|---|
| DATA-KEY-001 | must | static | always | A primary or alternate key contains only attributes needed for unique identification. Dropping any attribute would stop the key identifying every instance (smallest-key rule). | FIPS184 3.8.3(f), p. 27; CODD70 1.3, p. 380 |
| DATA-KEY-002 | note | none | always | A key may be one attribute or several. An attribute may belong to more than one key. An entity may have any number of alternate keys, each numbered. Key attributes may be owned or migrated. | FIPS184 3.8.2, 3.8.3(b)-(e), pp. 26-27 |
| DATA-KEY-003 | must | static | keyed-level | Each child or category entity holds a foreign key for every connection or categorization in which it is child or category. The foreign key has as many attributes as the parent (or generic) primary key, and each foreign key attribute references exactly one primary key attribute of that parent. | FIPS184 3.9.3(a)(g), B.5.3.23, pp. 30-31, 144-145 |
| DATA-KEY-004 | must | static | keyed-level | Only primary key attributes migrate. Every migrated attribute is a primary key attribute of a related parent or generic entity, and every primary key attribute of a parent or generic entity migrates into each related child or category entity. | FIPS184 3.4.1, 3.9.3(d), pp. 13, 30 |
| DATA-KEY-005 | must | static | keyed-level | When the same key migrates into an entity more than once, give each occurrence its own role name if the values may differ, and the same name (or none) if they must always be equal. A role name is unique and means one thing. | FIPS184 3.9.1.1, 3.9.3(e)(f), pp. 28, 31 |
| DATA-KEY-006 | must | static | keyed-level | A child must not hold two complete foreign keys that identify the same ancestor instance unless they arrive through separate relationship paths with intervening entities. | FIPS184 3.9.3(c), p. 30 |
| DATA-KEY-007 | must | runtime | always | Referential integrity. A child instance whose foreign key attributes all have values has a parent instance with an equal primary key. In an identifying or mandatory relationship the foreign key is never null; in an optional relationship the requirement holds only when the foreign key has values. | FIPS184 3.5.2.4, 3.5.4(b)(c), pp. 18-20; CODD70 1.3, p. 380 |
| DATA-KEY-008 | note | none | always | If no attribute set identifies an entity, define an artificial attribute (a surrogate) so that identification is possible. When several keys exist, choose a semantically meaningful one as the primary key. | CHEN76 2.3.1, p. 14 |

## REL: Relationships and cardinality

| Id | Strength | Checkable | Applies when | Rule | Section |
|---|---|---|---|---|---|
| DATA-REL-001 | must | static | always | A connection relationship joins exactly two entities, a parent and a child. | FIPS184 3.5.4(a), p. 20 |
| DATA-REL-002 | must | runtime | always | In an identifying or mandatory non-identifying relationship each child instance has exactly one parent instance. In an optional non-identifying relationship each child has zero or one parent. A parent may have zero, one or more children according to the stated cardinality. | FIPS184 3.5.4(b)(c)(d), p. 20 |
| DATA-REL-003 | must | static | keyed-level | A relationship is identifying when all primary key attributes of the parent migrate into the child primary key. If any migrated attribute lies outside the child primary key, including a split key, it is non-identifying. | FIPS184 3.9.1, B.5.3.21, pp. 27-28, 143-144 |
| DATA-REL-004 | must | static | always | The child-side cardinality of a connection is zero-one-or-more (the default), one-or-more, zero-or-one, an exact number or a range. Any other cardinality is recorded as a note. A low bound never exceeds the high bound. | FIPS184 3.5.1, 3.5.2, B.5.3.18, pp. 15-16, 142 |
| DATA-REL-005 | must | static | always | Only non-identifying relationships may be recursive (relate an instance of an entity to another instance of the same entity). | FIPS184 3.5.4(h), p. 20 |
| DATA-REL-006 | must | static | always | Relationship names between the same two entities are unique. A two-direction label states the parent perspective first. | FIPS184 3.5.3, pp. 19-20 |
| DATA-REL-007 | must | static | keyed-level | Every non-specific (many-to-many) relationship is replaced by specific relationships, typically through an associative entity that is a child of both original entities. | FIPS184 3.7.1, 3.7.3(c), 3.10.1, pp. 23-25, 31 |
| DATA-REL-008 | must | static | always | A non-specific relationship joins exactly two entities and may be recursive. An instance on either side may relate to zero, one or many instances on the other. | FIPS184 3.7.3(a)(b)(d), p. 25 |
| DATA-REL-009 | must | static | chen | A relationship is defined on one or more entity sets, not necessarily distinct, so it may be unary, binary or n-ary. More than one relationship may be defined on the same entity sets. | CHEN76 2.2.2, 3.1, pp. 11-12, 20 |
| DATA-REL-010 | should | none | chen | State for each relationship the mapping (1:1, 1:n or m:n) and, where known, the minimum and maximum number of entities on each side. | CHEN76 3.1(4), 3.2, pp. 20-21 |
| DATA-REL-011 | should | none | chen | State the role of each participating entity, especially when one entity set participates more than once in a relationship. | CHEN76 2.2.2, 3.1, pp. 11-12, 19 |
| DATA-REL-012 | must | static | chen | A relationship is identified by the keys of the entities involved. Those keys are not attributes of the relationship, which carries only its own attributes (for example a percentage of time). | CHEN76 2.3.2, p. 17 |
| DATA-REL-013 | must | static | idef1x-or-crows-foot | A relationship has no attributes. A fact about an association is held by an associative entity placed between the two entities. [reconstructed] | FIPS184 3.4.3(b), 3.7.1, pp. 14, 24; WIKIER (crow's foot notation) |
| DATA-REL-014 | should | none | always | Name a relationship with a verb phrase, in the parent-to-child direction. Entity name, relationship name, cardinality and entity name read as a true sentence, and the reverse reading also holds. Check both readings. | FIPS184 3.5.3, pp. 19-20; CFOOT section 02 |
| DATA-REL-015 | should | none | always | Where two paths lead from a descendant to the same ancestor, state whether the ancestor instances must be the same or must differ, using role names or a note. | FIPS184 3.13, pp. 34-35 |
| DATA-REL-016 | note | none | always | Boolean constraints between relationships, such as exclusive-or, are recorded as notes. If both entities refer to the same real-world thing, use a categorization instead. | FIPS184 3.13, p. 35 |
| DATA-REL-017 | note | none | always | Two traps appear in models read by queries: a fan trap, when one master fans out to several one-to-many branches and aggregates double-count, and a chasm trap, when a path between entities is missing for some instances. | WIKIER (model usability issues) |

## CAT: Subtypes and supertypes

| Id | Strength | Checkable | Applies when | Rule | Section |
|---|---|---|---|---|---|
| DATA-CAT-001 | must | static | always | A category entity has exactly one generic entity, so it belongs to exactly one cluster. | FIPS184 3.6.3(a), p. 23 |
| DATA-CAT-002 | must | static | always | An entity may be the generic entity of any number of category clusters, and a category entity may itself be the generic entity of another cluster. | FIPS184 3.6.3(b)(c), p. 23 |
| DATA-CAT-003 | must | runtime | always | Within one cluster an instance of the generic entity is associated with at most one category, so the categories are mutually exclusive. Categories in different clusters of the same generic entity are not exclusive of each other. | FIPS184 3.6.1, p. 21 |
| DATA-CAT-004 | must | static | always | The primary key of every category entity is the primary key of its generic entity, migrated through the categorization. Role names may be used. | FIPS184 3.6.3(d), 3.9.3(b), pp. 23, 30 |
| DATA-CAT-005 | must | static | always | A category entity is always identifier-dependent. Each category instance is the same real-world thing as exactly one generic instance, so the cardinality toward the category is zero or one and is not stated. | FIPS184 3.6.1, 3.6.2, pp. 21-22 |
| DATA-CAT-006 | must | static | always | No entity is its own generic ancestor: categorizations contain no cycle. | FIPS184 3.6.3(f), B.5.3.1, pp. 23, 136 |
| DATA-CAT-007 | must | static | always | A discriminator attribute belongs to the generic entity or one of its generic ancestors. No two clusters of one generic entity share a discriminator. All instances of one category share a discriminator value and different categories have different values. | FIPS184 3.6.1, 3.6.3(e)(g), B.5.3.8, pp. 21, 23, 138 |
| DATA-CAT-008 | must | static | keyed-level | Each category cluster has a discriminator attribute. At the entity-relationship level it is optional. | FIPS184 3.10.1, p. 31 |
| DATA-CAT-009 | must | static | always | The discriminator of a complete category cluster is not optional. | FIPS184 3.6.3(h), B.5.3.9, pp. 23, 139 |
| DATA-CAT-010 | must | static | keyed-level | A category entity may be the child of an identifying relationship only if the key it receives lies wholly inside its own primary key and its primary key still equals its generic entity's primary key. | FIPS184 3.6.3 (closing sentence), p. 23 |
| DATA-CAT-011 | should | none | always | Introduce a category entity when the category has attributes of its own, or takes part in relationships, that not all instances of the generic entity share. | FIPS184 2.48, 3.4.1, 3.6.1, pp. 5, 13, 20-21 |
| DATA-CAT-012 | note | none | always | A cluster is complete when every generic instance belongs to some category, and incomplete when some do not. An incomplete cluster reads "can be"; a complete one reads "must be". | FIPS184 3.6.1, 3.6.2, pp. 21-23 |
| DATA-CAT-013 | note | none | chen | Entity sets need not be disjoint: one may be a subset of another (male person within person). Chen shows no symbol for this. | CHEN76 2.2.1, p. 11 |

## LVL: Model levels and completeness

| Id | Strength | Checkable | Applies when | Rule | Section |
|---|---|---|---|---|---|
| DATA-LVL-001 | must | static | er-level | An entity-relationship level view contains entities and relationships, may contain attributes, and contains no primary, alternate or foreign keys. | FIPS184 3.10.1, 3.10.3(a)-(c), Table 1, pp. 31-32 |
| DATA-LVL-002 | must | static | keyed-level | A key-based view contains entities, relationships, primary keys and foreign keys. Entities are marked dependent or independent, connections identifying or non-identifying, non-identifying parents mandatory or optional, and each cluster has a discriminator. Non-specific relationships are prohibited. Each entity has a primary key and an alternate key for each further uniqueness constraint. | FIPS184 3.10.1, p. 31 |
| DATA-LVL-003 | must | static | keyed-level | A fully-attributed view meets every requirement of a key-based view and also contains all non-key attributes relevant to the subject of the view. | FIPS184 3.10.1, p. 32 |
| DATA-LVL-004 | note | none | er-level | At the entity-relationship level parent cardinality is not specified, entities need not be marked dependent or independent (categories count as dependent), and relationships need not be marked identifying or non-identifying. | FIPS184 3.10.3(d)(e)(f), p. 32 |
| DATA-LVL-005 | must | static | always | Each view has a unique name. A model may mix views of different levels. A view whose syntax conflicts with the standard is labeled "for exposition only". | FIPS184 3.3.3, p. 12 |
| DATA-LVL-006 | must | none | always | A model is accompanied by a statement of purpose, a statement of scope and a description of the author conventions. Author conventions never violate the rules and are consistent across the views of a model. | FIPS184 3 (introduction), 3.3.3(b), pp. 7, 12 |
| DATA-LVL-007 | must | static | always | A presentation may hide constructs (keys, attributes, role names, cardinalities) to simplify a view. All syntactic and semantic rules still hold for what is hidden. | FIPS184 3.11, p. 33 |
| DATA-LVL-008 | note | none | always | Data models are commonly built at three levels: conceptual (scope and master entities, least detail), logical (more detail, independent of any database product) and physical (enough detail to build a database, dependent on the product). Chen distinguishes four levels of logical views, from entities in the mind to access-path-dependent structures. | WIKIER (introduction); CHEN76 2.1, p. 10 |

## NAM: Names and documentation

| Id | Strength | Checkable | Applies when | Rule | Section |
|---|---|---|---|---|---|
| DATA-NAM-001 | must | none | always | The model has a glossary defining every view, entity and domain. A definition applies to every alias of the name. Views have no aliases. | FIPS184 3.12, pp. 33-34 |
| DATA-NAM-002 | should | none | always | Name entities and attributes with singular noun phrases. Abbreviations and acronyms are allowed if the name stays meaningful and consistent across the model. | FIPS184 3.1.2, 3.4.2, pp. 8, 13 |
| DATA-NAM-003 | must | static | idef1x | Names of views, entities and domains begin with a letter, use only letters, digits, dashes, underscores and spaces, and are at most 120 characters. Case and the separators space, dash and underscore are not significant. Relationship names use letters, digits and single spaces, at most 120 characters. | FIPS184 3.14.1, 3.14.4, pp. 35-37 |
| DATA-NAM-004 | must | static | always | No alias entity or alias domain is, directly or indirectly, an alias of itself. | FIPS184 B.5.3.3, B.5.3.2, pp. 136-137 |
| DATA-NAM-005 | must | static | always | Note numbers are unique within a view, and the same text applies wherever the same note number is used in a view. | FIPS184 3.13.1, p. 35 |
| DATA-NAM-006 | note | none | always | Naming a role with a noun (owner, possession) rather than a phrase (is the owner of) helps when physical column names are generated from the model, for example owner_person. | WIKIER (role naming) |

## PHY: Physical level

| Id | Strength | Checkable | Applies when | Rule | Section |
|---|---|---|---|---|---|
| DATA-PHY-001 | must | static | physical | A table has one or more columns. Column names in a table are unique; where the same domain is used twice, a role name tells the columns apart. | CODD70 1.3, p. 380 |
| DATA-PHY-002 | must | static | physical | Every table has a primary key. | PGDOC 5.5.4; CODD70 1.3, p. 380 |
| DATA-PHY-003 | must | static | physical | A table has at most one primary key constraint. It may have any number of unique constraints. | PGDOC 5.5.4 |
| DATA-PHY-004 | must | runtime | physical | The columns of a primary key are unique across the table and never null. | PGDOC 5.5.4; CODD70 1.3, p. 380 |
| DATA-PHY-005 | must | static | physical | A foreign key constraint references the primary key or a unique constraint of the referenced table. If no columns are named, the primary key is the target. | PGDOC 5.5.5; CODD70 1.3, p. 380 |
| DATA-PHY-006 | must | static | physical | A foreign key has the same number of columns as the key it references, and the column types match pairwise. | PGDOC 5.5.5 |
| DATA-PHY-007 | must | runtime | physical | Referential integrity. Every referencing row whose foreign key columns are non-null matches a row of the referenced table. By default a row escapes the check if any referencing column is null; with a full match, only if all are null. | PGDOC 5.5.5 |
| DATA-PHY-008 | must | static | physical | The delete and update action of a foreign key is one of no action (the default), restrict, cascade, set null or set default. A set-null or set-default action must still leave every other constraint satisfied (not-null columns, primary key columns, the default value existing in the referenced table). | PGDOC 5.5.5 |
| DATA-PHY-009 | should | none | physical | Choose the referential action from the dependence between the tables: cascade when the child is a component of the parent and cannot exist alone; restrict or no action when the two are independent; set null or set default for optional relationships. | PGDOC 5.5.5; CHEN76 3.5 Table III, p. 25; FIPS184 2.27 |
| DATA-PHY-010 | must | static | physical | No many-to-many relationship remains at the physical level. A third table holds a foreign key to each side (an association table). | PGDOC 5.5.5; CFOOT section 04; FIPS184 3.7.3(c) |
| DATA-PHY-011 | should | none | physical | Index the referencing columns of a foreign key when rows of the referenced table are deleted or its keys updated often. The database does not create that index for you, and each such change otherwise scans the referencing table. | PGDOC 5.5.5 |
| DATA-PHY-012 | note | none | physical | A primary key or unique constraint is enforced through a unique index. Whether two nulls count as equal in a unique constraint is implementation-defined, so rows with nulls may repeat unless the product is told otherwise. | PGDOC 5.5.3 |
| DATA-PHY-013 | note | none | physical | An index is a redundant, performance-oriented structure. It can be added or dropped without changing what the data means, and queries must not depend on it. | CODD70 1.2.2, p. 378 |
| DATA-PHY-014 | should | none | physical | Mark most columns not null. Allow null only where a value does not apply or is not known. | PGDOC 5.5.2; FIPS184 2.45 |
| DATA-PHY-015 | should | none | physical | A check constraint restricts the row being checked. It passes when the condition is true or null, so pair it with not null when a value is required. Rules across rows or tables belong to unique, foreign key or exclusion constraints, or to triggers. | PGDOC 5.5.1 |
| DATA-PHY-016 | note | none | physical | A table may reference itself (a tree, a bill of materials); the rows at the top leave the reference null. Name constraints so that errors and changes can refer to them. | PGDOC 5.5.1, 5.5.5; CODD70 1.3, p. 380 |

## MAP: Logical to physical

| Id | Strength | Checkable | Applies when | Rule | Section |
|---|---|---|---|---|---|
| DATA-MAP-001 | should | none | always | Implement each entity as a table, each attribute as a column, a primary key as a primary key constraint, an alternate key as a unique constraint and a foreign key as a foreign key constraint. [reconstructed] | CHEN76 2.3, pp. 14-17; FIPS184 1.2(d), p. 1; WIKIER (physical data model) |
| DATA-MAP-002 | must | static | physical | In an identifying relationship the foreign key columns form part of the child primary key. In a non-identifying relationship they are ordinary columns, not part of that key. | FIPS184 3.9.1, B.5.3.21, pp. 27-28, 143 |
| DATA-MAP-003 | must | static | physical | Foreign key columns are not null when the relationship is identifying or mandatory, and may be null when it is optional. | FIPS184 3.5.2.3, 3.5.2.4, B.5.3.20, pp. 18-19, 143 |
| DATA-MAP-004 | should | none | physical | Resolve a many-to-many relationship into an association table with a foreign key to each side. Its key is normally the combination of those foreign keys, and attributes of the relationship become its columns. [reconstructed] | CHEN76 2.3.2, p. 17; FIPS184 3.7.1, p. 24; CFOOT section 04 |
| DATA-MAP-005 | must | static | physical | If category entities become separate tables, the primary key of each is the primary key of the generic table and is also a foreign key to it. | FIPS184 3.6.3(d), 3.9.3(b), pp. 23, 30 |
| DATA-MAP-006 | must | static | physical | The table of a weak entity has a primary key made of the owner's key plus the weak entity's own partial key, and a foreign key to the owner table. | CHEN76 2.3.2, 3.2, pp. 17-22 |
| DATA-MAP-007 | should | none | physical | Implement a base domain as a column data type and a domain rule as a check constraint. [reconstructed] | FIPS184 3.2.1, p. 10; PGDOC 5.5.1 |
| DATA-MAP-008 | note | none | physical | An attribute that maps to a product of value sets becomes several columns (a name as first name and last name). | CHEN76 2.2.3, 4.1.1, pp. 12, 26 |

## NRM: Normalization guidance

| Id | Strength | Checkable | Applies when | Rule | Section |
|---|---|---|---|---|---|
| DATA-NRM-001 | should | partial | keyed-level | Second normal form: every non-key attribute depends on the whole primary key, not on part of it. | FIPS184 3.8.3(g), 2.43, pp. 4, 27; KENT83 3.1 |
| DATA-NRM-002 | should | partial | keyed-level | Third normal form: no non-key attribute depends on another non-key attribute. Each non-key attribute is a fact about the key, the whole key and nothing but the key. | FIPS184 3.8.3(h), 2.43, pp. 4, 27; KENT83 3.2 |
| DATA-NRM-003 | should | none | keyed-level | Fourth normal form: an entity does not hold two or more independent multi-valued facts about the same thing. | KENT83 4.1 |
| DATA-NRM-004 | note | none | keyed-level | Fifth normal form: split an entity when its information can be rebuilt from smaller pieces. It differs from fourth normal form only where a symmetric constraint exists among the pieces. | KENT83 4.2 |
| DATA-NRM-005 | note | none | always | Normalization is a design guideline, not an obligation. It prevents update anomalies but can slow retrieval. If you denormalize on purpose, record why. | KENT83 1, 7 |
| DATA-NRM-006 | note | none | always | Normal forms are defined only where identifiers are unique and singular. The same fact spelled two ways hides a violation. | KENT83 3.3 |
| DATA-NRM-007 | note | none | always | Entities and relationships built top-down with Chen's method come out close to third normal form, with clearer meaning, without a decomposition step. | CHEN76 4.1.3, pp. 28-29 |
