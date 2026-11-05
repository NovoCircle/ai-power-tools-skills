---
name: business-modeling
description: The UML business modeling extensions - the way UML is used to describe a business, as defined by the OMG "UML Profile for Business Modeling" in the UML 1.x specifications. A business is shown from outside as a use case model (use case system, use case packages, use cases and actors) and from inside as an object model (object system, organization units, work units, workers, case workers, internal workers and entities), with communicate and subscribe associations between them. Use when someone is modeling a business with use case models and object models, workers and entities, or when they ask what the OMG business modeling profile, its kinds or its communicate and subscribe associations allow.
---

# Business Modeling: the UML business modeling extensions

This is a way of using UML to describe a business, not an invented language. A business model is an ordinary UML model whose elements carry a business meaning: a use case is something the business does for someone outside it, an actor is someone outside the business, a class is a role or a thing the business handles. For the UML elements themselves (use case, actor, class, package, subsystem, association, generalization) read the UML skill (`uml-2`); this skill covers only what the business modeling extensions add.

**The source is a thin chapter.** It is the "UML Profile for Business Modeling" in the OMG UML specifications 1.3, 1.4 and 1.5 (UML 1.3 presents it as a defined profile; 1.4 and 1.5 call it an "example profile"). It labels UML elements with a business keyword, defines a few kinds and association keywords, and adds a few well-formedness rules. It is not a complete definition of business modeling.

**The profile was dropped from UML 2** and has no current standard. No newer version exists.

## What you are creating

A business model has two views of the same business.

1. **The outside view** (the use case model). The business as use cases and the people and organizations outside it as actors, grouped in use case packages under a use case system. It answers: what does the business do, and for whom?
2. **The inside view** (the object model). The things inside the business: the organization units and work units that group its parts, the workers who do the work and the entities they handle, under an object system. It answers: who does the work, and with what?

The profile defines no diagram types. It labels the package and class kinds with a keyword in guillemets, so each model element shows what kind it is.

## The concepts

Every concept is a UML element with a keyword. The UML base is given in brackets.

### Outside: the use case model

- **Use Case Model** [Model]: the model of the business from outside.
- **Use Case System** [Package]: the top-level package of a use case model. It may hold use case packages, use cases and relationships.
- **Use Case Package** [Package]: a package of use cases and relationships. A use case belongs to one use case package and is not split across several.

The profile has no business actor or business use case of its own. It uses the plain UML actor and use case.

### Inside: the object model

- **Object Model** [Model]: the model of the things inside the business. Its top-level package is an object system.
- **Object System** [Subsystem]: the top-level subsystem of an object model. It may hold organization units, work units, classes and relationships.
- **Organization Unit** [Subsystem]: a subsystem that stands for a unit of the real organization. It may hold other organization units, work units, classes and relationships.
- **Work Unit** [Subsystem]: a task-oriented set of objects that forms a recognizable whole to the end user. It holds one or more entities and may have a facade showing the part of them relevant to the task.

### Workers and entities

- **Worker** [Class]: an abstraction of a person acting within the business. A worker may work with other workers and operate on entities.
  - **Case Worker**: a worker who deals directly with actors outside the system.
  - **Internal Worker**: a worker who deals only with other workers and entities inside the system.
- **Entity** [Class]: a passive class. Its objects start no interaction on their own, and it usually outlives any one interaction.

### Realization

- **Use Case Realization** [Collaboration]: a kind named in the UML 1.3 summary table only. The text read says nothing more about it, and UML 1.4 and 1.5 do not list it.

Specialization: Case Worker and Internal Worker specialize Worker. Nothing else specializes anything. The source declares nothing abstract. The profile defines no enumerations and adds no recorded properties.

## Relationships

- **communicate** (association): instances of the associated elements interact. It may be one-way or two-way, and the direction of communication is the direction of navigability.
- **subscribe** (association): the source (the subscriber) is notified when an event occurs in the target (the publisher). The association carries a specification of the events.

Both may join actors, case workers, entities, work units and internal workers. UML 1.3 gives a table of the pairs allowed (in `language.yaml`). It is permissive ("may also be used") and not symmetric, and UML 1.4 and 1.5 do not repeat it.

## The rules that matter most

The full list, 12 rules with ids, is in `references/rules.md` (5 must, 2 should, 5 note):

- All elements of a generalization have the same kind: a worker inherits only from workers, an entity only from entities. (BIZMOD-GEN-001)
- A use case belongs to one use case package. (BIZMOD-STR-004)
- An object model's top-level package is an object system. (BIZMOD-STR-005)
- A work unit holds one or more entities. (BIZMOD-STR-007, should)
- An entity is passive; a case worker deals with outside actors and an internal worker only with insiders. (BIZMOD-DEF-001, BIZMOD-DEF-004)
- Communicate and subscribe are used between the pairs in the UML 1.3 table. (BIZMOD-LNK-001, should)

## Telling similar concepts apart

- **Actor or worker.** An actor is outside the business. A worker is inside, carrying out the work.
- **Case worker or internal worker.** Does the worker deal directly with outside actors (case worker) or only with insiders (internal worker)?
- **Worker or entity.** A worker may interact with other workers and operate on entities. An entity is passive and starts none.
- **Organization unit or work unit.** An organization unit mirrors a unit of the real organization. A work unit groups the entities around one task.
- **Use case system or use case package.** The use case system is the top-level package of a use case model; a use case package is a package of use cases inside it.
- **Use case model or object model.** The use case model is the view from outside, the object model the view from inside.

## A short example

Westbrook Bank, a fictitious bank, models how it opens accounts for small businesses. The names below are an illustration; use your own business's actors, use cases, workers and entities.

**Outside.** A use case model for Westbrook Bank has a use case system, and in it a use case package, Account Services, holding the use case Open Business Account. The actor is Small Business Customer, associated with the use case.

**Inside.** The object model has an object system, and in it an organization unit, Retail Banking, which holds a work unit, Account Opening. The work unit holds two entities, Account Application and Customer Profile. Account Opening Officer is a case worker, because the officer deals directly with the customer. Compliance Reviewer is an internal worker. The case worker communicates with the actor Small Business Customer (a pair the UML 1.3 table allows), and Compliance Reviewer subscribes to Account Application, so the reviewer is told when something happens to an application.

## Data types and attributes

Coverage: none. The profile defines no data types, enumerations, units or attributes of its own (OMG UML 1.3 4.6.1; UML 1.4 4.5). Each kind keeps the attributes of the UML element it labels, and any type comes from UML (`uml-2`); the source does not say how the UML 1.x types it was written against map to UML 2. See `data_types` in `language.yaml`.

## How it is drawn

Coverage: informative. The profile defines no symbols beyond UML with a keyword, apart from four small icons for classes. See `notation` in `language.yaml` for each kind, with its section.

Sizes and spacing come from `../_languages/layout-standard.yaml`; the mapping of each concept to a size class is the `layout` block in `language.yaml`.

- **Package kinds** (use case model, use case system, use case package, object model, object system, organization unit, work unit): the UML package symbol with the keyword in guillemets above the name, for example «workUnit». A model or subsystem icon at the upper right is optional; the chapter does not draw it.
- **Class kinds** (worker, case worker, internal worker, entity): the UML class box with the keyword, or an icon with the name below it. Worker and internal worker: a circle holding a stick figure, with a small arrowhead on top of the circle. Case worker: the same figure without the arrowhead, with a short horizontal line and a vertical bar leaving its left side. Entity: a circle resting on a short horizontal line. Case worker and internal worker are shown as subtypes of worker.
- **Communicate and subscribe**: the UML association line with the keyword on it and no icon.
- **Use case realization**: the source gives no drawing.

The source states no sizes or colors and defines no diagram type.

## References

- `references/standard.md`: the source, section by section, in our own words, with citations.
- `references/rules.md`: all 12 rules with stable ids (`BIZMOD-<CAT>-nnn`), strength, version and source section.
- `language.yaml`: the machine-readable form: 12 concepts, 2 relationships with the allowed-pairs table, and the rules.
