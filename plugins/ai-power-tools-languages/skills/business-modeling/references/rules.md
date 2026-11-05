# Business Modeling rules

Generated from `language.yaml` (`constraints`). Do not edit by hand; change the language file and regenerate.

Each rule has a stable id of the form `BIZMOD-<CAT>-nnn`. The number never changes once assigned. A rule that is retired keeps its id and is marked withdrawn rather than reused. Ids are not renumbered when rules are removed, so the numbers in a category have gaps.

Every rule comes from the OMG UML 1.x profile chapter (UML 1.3, 1.4 and 1.5), and each says which version it applies to. A rule is a well-formedness rule, a definition the chapter states as fact, or a note.

## Strength

| Strength | Meaning |
|---|---|
| must | An OMG well-formedness rule or invariant, or a definition the source states as fact. A model that breaks it is not well formed. |
| should | Guidance: the source words the rule permissively or states it in a way that one reading would reject ordinary models. Breaking it is a warning, not an error. |
| note | A description, option or method note. Recorded for completeness and not checkable on its own. |

## Applies when and checkable

| Value | Meaning |
|---|---|
| omg | The OMG profile (UML 1.3, 1.4 and 1.5). |
| omg-1.3 | The UML 1.3 text only. |
| (blank) | Language-wide. |
| static | A validator that sees only the saved model can check it. |
| partial | Only the structure or simple cases can be checked. |
| none | Not a property of a model; a definition or a judgment. |

## Categories

| Category | Name | Covers | Rules |
|---|---|---|---|
| STR | Structure and containment | What each model, package or system contains, and where an element lives. | 5 |
| GEN | Generalization | Rules for specialization between elements of this language. | 1 |
| LNK | Links | Which elements a relationship may connect, and how the relationship is shaped. | 2 |
| DEF | Definition | Statements that say what makes an element the kind of thing it is, so that it is placed correctly. | 2 |
| GUID | Guidance and scope | Method notes, optional parts and facts about the language itself; not checkable on their own. | 2 |

Section references: "OMG UML 1.4" and "UML 1.3" cite clause numbers and printed pages of those specifications.

## STR: Structure and containment

| Id | Strength | Rule | Applies | Checkable | Section |
|---|---|---|---|---|---|
| BIZMOD-STR-004 | must | A use case belongs to a single use case package; it is not split across several. | omg | static | OMG UML 1.4 4.7.1.3, p. 4-11 |
| BIZMOD-STR-005 | must | The top-level package of an Object Model is an Object System. | omg | static | OMG UML 1.4 4.7.2.1, p. 4-12 |
| BIZMOD-STR-006 | note | A Use Case System, Use Case Package, Object System and Organization Unit each 'may contain' a listed set of elements (use cases, use case packages and relationships; organization units, work units, classes and relationships). | omg | none | OMG UML 1.4 4.7.1, 4.7.2; UML 1.3 4.7.1 |
| BIZMOD-STR-007 | should | A Work Unit holds one or more entities. | omg | static | OMG UML 1.4 4.7.2.4 ('may contain'); UML 1.3 4.7.1.4 ('contains') |
| BIZMOD-STR-009 | note | Models are exterior to the business (use case models) or interior to it (object models), and a large business system may be divided into subordinate business systems. | omg | none | OMG UML 1.4 4.7, p. 4-10 |

Notes:

- BIZMOD-STR-006: The lists are permissive, are not stated to be exclusive, and omit actors, so they are not a closed-world check.
- BIZMOD-STR-007: UML 1.3 says 'contains one or more entities', UML 1.4 says 'may contain'. The weaker reading governs.

## GEN: Generalization

| Id | Strength | Rule | Applies | Checkable | Section |
|---|---|---|---|---|---|
| BIZMOD-GEN-001 | must | All elements in a generalization have the same kind: a worker inherits only from workers, a case worker only from case workers, an internal worker only from internal workers, an entity only from entities. | omg | static | OMG UML 1.4 4.8.1, p. 4-16; UML 1.3 4.8.1, p. 4-13 |

Notes:

- BIZMOD-GEN-001: The printed OCL is cut off mid-expression across two pages and, read literally, also forbids a worker being the parent of a case worker or internal worker, although those are called subtypes of worker. The sentence governs. In UML 1.3 the rule is the same sentence with no OCL.

## LNK: Links

| Id | Strength | Rule | Applies | Checkable | Section |
|---|---|---|---|---|---|
| BIZMOD-LNK-001 | should | Besides the associations UML allows, communicate and subscribe are used between the kinds, and only between the pairs, in the allowed table of this language. | omg-1.3 | static | OMG UML 1.3 4.8.2, Table 4-4 |
| BIZMOD-LNK-010 | note | In a communicate association the direction of communication is the direction of navigability. | omg-1.3 | none | OMG UML 1.3 4.7.3.1, p. 4-13 |

Notes:

- BIZMOD-LNK-001: Permissive wording ('may also be used'), so a pair outside the table is a warning. Present in UML 1.3 only.

## DEF: Definition

| Id | Strength | Rule | Applies | Checkable | Section |
|---|---|---|---|---|---|
| BIZMOD-DEF-001 | must | An Entity is passive: its objects start no interaction on their own, and it usually outlives any one interaction. | omg | none | OMG UML 1.4 4.7.3.4, p. 4-14 |
| BIZMOD-DEF-004 | must | A Worker is an abstraction of a person acting within the business. A Case Worker deals directly with actors outside the system; an Internal Worker deals only with workers and entities inside it. | omg | none | OMG UML 1.4 4.7.3.1 to 4.7.3.3 |

## GUID: Guidance and scope

| Id | Strength | Rule | Applies | Checkable | Section |
|---|---|---|---|---|---|
| BIZMOD-GUID-004 | note | The OMG profile adds no recorded properties and no constraints beyond its well-formedness rules, is not a complete definition of business modeling, and leaves all of UML available. | omg | none | OMG UML 1.3 4.5, 4.6.1, 4.6.2; UML 1.4 4.5 |
| BIZMOD-GUID-008 | note | The profile was dropped from UML 2. Its last OMG appearance is UML 1.5 (March 2003). |  | none | OMG UML 1.5 chapter 4; UML 2.0 and later (absent) |
