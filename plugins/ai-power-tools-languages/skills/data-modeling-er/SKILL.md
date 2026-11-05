---
name: data-modeling-er
description: Data modeling and entity-relationship (ER) modeling as one language - entities, attributes, domains, primary, alternate and foreign keys, relationships and cardinality (Chen, IDEF1X and crow's foot notations), weak entities, subtypes and supertypes (category clusters), associative entities, and the physical level of tables, columns, unique and foreign key constraints, referential integrity and indexes. Use it when creating, reviewing or validating an ER diagram or ERD, a conceptual, logical or physical data model, an IDEF1X view, a crow's foot diagram, a schema design, or when resolving many-to-many relationships, choosing keys, or checking normal forms.
---

# Data modeling and entity-relationship (ER) modeling

## What you are creating

A data model says what an organization needs to remember and how the facts relate. This skill treats data modeling and ER modeling as **one language** that is drawn at three levels of abstraction:

- **Conceptual**: the main things of the business and how they relate. Least detail. Many-to-many relationships are fine here.
- **Logical**: entities, attributes, identifiers (keys), relationships with cardinality, subtypes. Independent of any database product. Every entity has a key, every many-to-many is resolved.
- **Physical**: the tables, columns, primary key, unique and foreign key constraints, referential actions and indexes that a particular database needs.

**No single standard, owner or version governs this language.** It is assembled from four public sources, and every rule says which one it comes from and where it applies:

- Peter Chen's 1976 paper, which defines the entity-relationship model (relationships as first-class, n-ary, with roles and attributes; weak entities).
- IDEF1X, the US federal standard FIPS 184 (1993, withdrawn 2008 but public), which gives precise rules for keyed logical models: identifying and non-identifying relationships, key migration, category clusters, three view levels.
- Crow's foot (information engineering) notation, a family of drawing conventions with no governing document I could read; described by secondary sources only.
- The relational model (keys, foreign keys, normal forms) and the way SQL constraints behave.

Newer IDEF1X (IEEE 1320.2-1998) was not read. Write down which notation a model uses, because some rules differ (see "Rules that depend on the notation").

## Diagram types and what each admits

| Diagram type | Admits | Notes |
|---|---|---|
| Chen diagram | Entity, weak entity, relationship (n-ary, with attributes), attribute | Rectangles for entity sets, diamonds for relationships, roles and 1, m, n on the lines, a special box for a weak entity. |
| IDEF1X entity-relationship view | Entity, connection relationship, category cluster, non-specific (many-to-many) relationship, attribute (optional), note | No keys. The conceptual-to-early-logical form. |
| IDEF1X key-based view | Dependent and independent entities, identifying, mandatory and optional non-identifying relationships, category clusters, primary, alternate and foreign keys, attributes, notes | No many-to-many. Every entity has a primary key. |
| IDEF1X fully-attributed view | Everything in the key-based view, with every relevant non-key attribute | The finished logical model. |
| Crow's foot diagram | Entity, weak entity, associative entity, attribute, keys, relationships as lines with ring, bar and crow's foot ends | Relationships carry no attributes. Use the category cluster for subtypes. |
| Physical data model diagram | Table, column, primary key, unique, foreign key and check constraints, index | Notation not defined by the sources; conventionally crow's foot or IDEF1X style. |

A model may mix views of different levels, with unique view names (DATA-LVL-005).

## The concepts

**Entities.** An *entity* is a set of things of one kind. A *weak* (identifier-dependent) entity is identified through a relationship with an owner and carries the owner's key. An *associative* entity resolves a many-to-many relationship. A *generic* entity (supertype) is divided into *category* entities (subtypes).

**Attributes and domains.** An *attribute* belongs to exactly one entity and takes one value per instance. A *domain* (Chen: value set) is a named set of values with a data type and optionally a value list or range; *typed* domains narrow other domains.

**Keys.** A *candidate key* uniquely identifies instances with no unneeded attribute. One is the *primary key*; the rest are *alternate keys*. A *foreign key* is the parent's (or generic's) primary key migrated into the child, so the child can point to its parent.

**Relationships.** In IDEF1X and crow's foot, a *connection* joins a parent and a child: *identifying* (the parent key becomes part of the child key), *mandatory non-identifying* (the child must have a parent) or *optional non-identifying* (it may not). A *categorization* ties a generic entity to its category entities through a *category cluster* (complete or incomplete, with an optional discriminator). A *non-specific* relationship is many-to-many and exists only at the entity-relationship level. In Chen, a *relationship* is an element with roles, a mapping (1:1, 1:n, m:n) and attributes of its own.

**Physical.** A *table* has *columns*. A *primary key constraint*, *unique constraint*, *foreign key constraint* and *check constraint* belong to a table. A foreign key has a delete action and an update action: no action, restrict, cascade, set null or set default. An *index* speeds access and carries no meaning of its own.

## Relationship rules in summary

- A connection joins exactly two entities. Child cardinality is zero or more (default), one or more, zero or one, an exact number, or a range. An identifying or mandatory relationship gives each child exactly one parent; an optional one gives zero or one (DATA-REL-001 to DATA-REL-004).
- A relationship is identifying exactly when the parent's whole primary key lies inside the child's primary key (DATA-REL-003). Only non-identifying relationships can be recursive (DATA-REL-005).
- A category entity has one generic entity and the generic's primary key; it is always dependent (DATA-CAT-001, -004, -005). A discriminator belongs to the generic and names the category (DATA-CAT-007).
- A foreign key references the parent's primary key, one foreign key attribute for each key attribute, and only primary key attributes migrate (DATA-KEY-003, -004). Physically it may reference a primary key or a unique constraint, with matching column counts and types (DATA-PHY-005, -006).
- A many-to-many relationship is allowed conceptually, replaced by an associative entity at the key-based level (DATA-REL-007), and never remains at the physical level (DATA-PHY-010).
- In IDEF1X and crow's foot, a relationship has no attributes; a fact about an association goes on an associative entity (DATA-REL-013). In Chen's model, a relationship may have attributes and may be n-ary (DATA-REL-009, -012).
- A weak entity is identified by its own partial key plus the owner's key (DATA-ENT-005, DATA-MAP-006).

## Cardinality notations side by side

Each notation states the count look-across: the mark at one end says how many instances of that end's entity go with one instance of the other.

| Meaning | Chen | Crow's foot | IDEF1X |
|---|---|---|---|
| Exactly one | `1` | bar, bar | no mark at the parent end |
| Zero or one | `1` with a partial-participation mark | ring, bar | `Z`; or a diamond at an optional parent |
| Zero or more | `n` or `m` | ring, crow's foot | plain dot at the child end |
| One or more | `n` with minimum 1 | bar, crow's foot | `P` |
| Exactly n, or n to m | min and max stated | not expressible | the number or range |
| Many-to-many | m:n relationship | crow's feet at both ends | dot at both ends, entity-relationship level only |
| Identifying | weak entity | solid line (tool-dependent) | solid line, rounded child |
| Non-identifying | regular entity | dashed line | dashed line |

These are drawing conventions, not constraints. The rules above hold whichever notation you use.

## The rules that matter most

1. **Every entity has a key** at the logical level, and every table has a primary key (DATA-ENT-001, DATA-PHY-002).
2. **Every foreign key references a key**, with matching columns (DATA-KEY-003, DATA-PHY-005, DATA-PHY-006).
3. **No unresolved many-to-many** at the key-based level or the physical level (DATA-REL-007, DATA-PHY-010).
4. **Referential integrity** holds; choose delete and update actions from the dependence between tables: cascade for components, restrict for independent tables, set null for optional links (DATA-KEY-007, DATA-PHY-007 to -009).
5. **Single owner, single value**: each attribute belongs to one entity and has one value per instance (DATA-ATT-001, DATA-ATT-002).
6. **Identifying means whole key inside**: the identifying/non-identifying choice follows from the keys, and foreign key columns are not null for identifying and mandatory relationships (DATA-REL-003, DATA-MAP-002, DATA-MAP-003).
7. **Subtypes carry the generic's key** and are mutually exclusive within a cluster (DATA-CAT-003, -004).
8. **Normal forms are guidance.** Aim for second and third normal form in logical models; treat fourth and fifth as advice; record deliberate denormalization (DATA-NRM-001 to DATA-NRM-006).

## Rules that depend on the notation

- Chen only: relationships with attributes and n-ary relationships, the 1, m, n mapping, roles on the lines (DATA-REL-009 to -012).
- IDEF1X only: naming and lexical rules, domain for every attribute, glossary and model statements (DATA-NAM-003, DATA-ATT-005, DATA-LVL-006).
- IDEF1X and crow's foot: relationships without attributes (DATA-REL-013).
- Entity-relationship level versus key-based level: keys appear only at the second (DATA-LVL-001 to -004).
- Physical: DATA-PHY-001 to -016 and DATA-MAP-002 to -008.

## An example (a fictitious organization)

Westbrook Bank is an illustration; substitute your own entities. Customers hold accounts, and an account may have several holders. Accounts belong to a branch and are either savings or checking. Each account has transactions, numbered within the account.

**Conceptual.** Customer, Account, Branch, Transaction. Customer *holds* Account (many-to-many). Branch *services* Account (one-to-many). Account *records* Transaction (one-to-many).

**Logical, key-based view.**

| Entity | Key | Other attributes and keys |
|---|---|---|
| Customer | CustomerId (primary) | Name; TaxId (alternate key AK1) |
| Branch | BranchId (primary) | BranchName |
| Account | AccountId (primary) | BranchId (foreign key, mandatory non-identifying); AccountType (discriminator); OpenedOn |
| Savings Account, Checking Account | AccountId (primary and foreign key to Account) | InterestRate / OverdraftLimit. Category cluster on Account, complete, discriminator AccountType |
| Account Holder (associative) | CustomerId, AccountId (both primary and foreign) | HolderRole. Resolves Customer holds Account |
| Transaction | AccountId (foreign), TransactionSeq (own) | Amount, PostedAt. Identifying relationship from Account; Transaction is dependent |

Relationship names read both ways: "a branch services zero or more accounts / an account is serviced by exactly one branch". The many-to-many between Customer and Account is gone, replaced by Account Holder with two identifying connections.

**Physical.** Tables `customer`, `branch`, `account`, `savings_account`, `checking_account`, `account_holder`, `transaction_entry`.

- `account_holder` has primary key (customer_id, account_id), a foreign key to `customer` and one to `account`, both not null (identifying), both with delete action *restrict*: a bank does not delete a customer's holdings silently.
- `account.branch_id` is a not null foreign key to `branch` with *restrict* (mandatory, independent tables).
- `savings_account.account_id` is its primary key and a foreign key to `account` (category table, the generic's key).
- `transaction_entry` has primary key (account_id, transaction_seq) and a foreign key to `account`. Existence depends on the account: the rule "delete the dependents or refuse" is met by *restrict* here, because transactions are never discarded with an account (DATA-ENT-006, DATA-PHY-009).
- An index on `transaction_entry.account_id` is unnecessary because it leads the primary key; an index on `account.branch_id` helps branch queries and foreign key checks (DATA-PHY-011).

## Data types and attributes

Coverage is partial. IDEF1X names three base data types for a domain (character, numeric, boolean), allows others such as dates, times and binary, and lets a domain carry a value list or a range (FIPS184 3.2.1). Chen's paper shows value-set representations only as a sample declaration (CHEN76 3.2). None of the sources read defines the column types of a physical table, so choose them from your database. Properties that the sources name for a concept (an entity number, an alternate key number, a child cardinality, a referential action) are listed on that concept in `language.yaml` under `attributes`, and the types and enumerations are under `data_types`.

## How it is drawn

Coverage is normative for IDEF1X only (FIPS184 3). Entities are boxes, square-cornered when independent and rounded when identifier-dependent, with primary key attributes above a dividing line. A relationship is a line with a small filled dot at the child end, solid when identifying and dashed when not, with a small open diamond at the parent end when the parent is optional. P, Z, a number or a range beside the dot gives the cardinality. A category cluster is a small circle with one underline (incomplete) or two (complete). A many-to-many line has a dot at both ends. Chen's diagram has rectangles, diamonds, 1, M, N labels and a double-outlined rectangle for a weak entity (CHEN76 3.1); crow's foot has ring, bar and crow's foot marks in pairs and rests on secondary sources only. The standard defines no drawing for domains, views or the physical level. `language.yaml` holds every shape, end mark and line style under `notation`. Sizes and spacing come from `../_languages/layout-standard.yaml`, and the mapping from each concept to an element type comes from `layout` in `language.yaml`.

## Where to look

- `references/standard.md`: the language in plain words with sources, notation comparison, physical constraints, mapping and normal forms.
- `references/rules.md`: every rule with its id, strength, scope and source section.
- `language.yaml`: concepts, links, diagram types, conventions and the rules in machine-readable form.
