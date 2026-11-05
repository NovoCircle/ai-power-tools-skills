# The UML business modeling extensions, source by source

This file summarizes the source in our own words. It does not reproduce it; the few short quoted phrases are cited. "p." is a page of the cited document. Where the source is silent or inconsistent, this file says so rather than filling the gap.

## 1. What this language is, and what it is not

One source defines "business modeling" in UML here: the **OMG profile**, the "UML Profile for Business Modeling" in the OMG UML specifications 1.1 to 1.5 (read: 1.3, February 2000; 1.4, September 2001; 1.5, March 2003). It is a chapter of an OMG specification. UML 1.3 presents it as one of two defined profiles. From UML 1.4 it is called an "example profile".

**The profile was dropped from UML 2.** The UML 2.0 specification (July 2005) and every later one define no business modeling profile; UML 1.5 (March 2003) is the last OMG specification that prints it. No newer version of the profile exists. UML 2 has its own standard profiles for other purposes.

The profile does not add new concepts to UML. It labels ordinary UML elements (a model, a package, a subsystem, a class, a collaboration, an association) with a business keyword written in guillemets, and it adds a few well-formedness rules. A business model is therefore an ordinary UML model whose elements carry business meaning. For the UML elements themselves, read the UML language skill (`uml-2`); this file describes only what the profile adds.

## 2. The idea: two models, seen from outside and inside

The profile organizes a business model in two kinds of model. A business is described by models that are **exterior** or **interior** to it (OMG UML 1.4, 4.7):

- The **use case model** looks at the business from outside. It shows the business's processes as use cases and the outside parties (customers, partners, suppliers) as actors.
- The **object model** looks inside. It shows the things inside the business: the people who do the work, the things they handle, and how they are grouped.

A large business system may be divided into subordinate business systems.

## 3. The OMG profile

Source: OMG UML 1.4, chapter 4 example 2 (printed pp. 4-9 to 4-16); the same in UML 1.5 (printed pp. 4-9 to 4-16); UML 1.3 chapter 4 part 2 (printed pp. 4-8 to 4-14), with differences noted.

**Introduction (4.5).** The profile shows how UML can be customized for business modeling. It stresses common kinds and some useful terminology. It is defined only through extension kinds and constraints; it adds no recorded properties (UML 1.3 4.6.1 says it adds none; 1.4 says profiles commonly include them but this one has none). It is "not meant to be a complete definition" of business modeling (UML 1.3 4.5).

**Summary (4.6, 4.7).** UML 1.4 lists 13 kinds. In UML 1.3 the table lists 13 as well, but they differ: 1.3 has use-case realization and omits communicate; 1.4 has communicate and omits use-case realization.

| Kind | UML element it labels | Notes |
|---|---|---|
| Use Case Model | Model | |
| Use Case System | Package | Top-level package of a use case model. |
| Use Case Package | Package | |
| Object Model | Model | Top-level package is an object system. |
| Object System | Subsystem | Top-level subsystem of an object model. |
| Organization Unit | Subsystem | A unit of the real organization. |
| Work Unit | Subsystem | A task-oriented group of entities with an optional facade. |
| Worker | Class | A person acting within the business. |
| Case Worker | Class (a subtype of worker) | A worker who deals directly with outside actors. |
| Internal Worker | Class (a subtype of worker) | A worker who deals only with inside workers and entities. |
| Entity | Class | A passive class that outlives any one interaction. |
| Communicate | Association | Instances of the associated elements interact. |
| Subscribe | Association | The source is notified when an event occurs in the target. |
| Use Case Realization (1.3 only) | Collaboration | Listed in the 1.3 table; no further description in the text read. |

**What the profile does not define.** It has no business actor or business use case of its own: it uses the plain UML actor and use case. It has no recorded properties and no enumerations.

**Well-formedness (4.8).**

- In a generalization all elements must have the same kind (a worker class inherits only from worker classes, an entity only from entities). The printed OCL is cut off mid-expression across two pages; read literally it also stops a worker being the parent of a case worker or internal worker, which contradicts the table that calls them subtypes. The sentence governs.
- Besides the combinations UML allows, **communicate** and **subscribe** may be used between the kinds in Table 4-4 of UML 1.3 (reproduced in `language.yaml`). The table is not symmetric and exists in 1.3 only.
- Added constraints are added to, and do not change, those of the UML elements.

**Notation (4.7.x).** Package kinds show their keyword in guillemets, optionally with the Model or Subsystem icon at the top right. Class kinds show a keyword or the profile's icons (the four icons are described in `language.yaml` under `notation`). Tools and users may add icons. Association kinds show a keyword and no icon.

## 4. Diagram types

The profile defines no diagram type or notation beyond the labeling above, apart from the four class icons. `language.yaml` therefore lists none.

## 5. Gaps

The source leaves some points unsettled. The main ones are the status of the Table 4-4 pairs (UML 1.3 only), the Subsystem versus package inconsistency, and the cut-off generalization OCL.
