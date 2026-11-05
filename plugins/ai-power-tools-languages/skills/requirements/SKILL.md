---
name: requirements
description: Requirements modeling - requirements as model elements, their levels (business, stakeholder, system, system element, software) and types (functional, performance, interface, quality or non-functional with its quality categories, constraint, business rule, policy and regulation, transition), the attributes good practice expects (identifier, statement, rationale, priority, source, verification), the characteristics of a well-formed requirement and of a requirement set (ISO/IEC/IEEE 29148 - necessary, unambiguous, verifiable, singular, complete, consistent), and traceability (derive, satisfy, verify, refine, trace, allocate; every requirement traces to a source and is verified). Use when someone is modeling, writing, reviewing or tracing requirements, building a requirements specification (BRS, StRS, SyRS, SRS), setting up requirement attributes or a traceability or verification matrix, or asking what a good requirement or requirement set looks like. Built from ISO/IEC/IEEE 29148 and SysML, not from one owner.
---

# Requirements modeling

No single standards body owns a requirements modeling language. This skill describes the one the public sources share: **ISO/IEC/IEEE 29148:2018** for what a requirement is, what makes it good, what it carries and what it links to; and **SysML** (the `sysml-1` skill) for the relationship vocabulary and its endpoint rules. That skill is pointed to, not repeated: use it for satisfy, verify, refine, trace, derive, copy and containment in detail, and for the SysML requirement diagram.

**Two honesty notes.** 29148 is a paid standard and was read only through third-party summaries, so every rule taken from it is graded `should` or `note`, and its exact wording is unconfirmed. And 29148 defines no notation and no diagram types: it defines the requirement, its attributes, its quality and the specifications that hold requirements. A requirements model in this language is a set of elements and links, presented as specifications and matrices.

## What you are creating

A requirements model records, for one program, product or system:

1. **The requirements**, each a statement of one need with its attributes, at a level and of a type.
2. **Where each came from**: the stakeholders, needs, source documents, business rules, trade studies and parent requirements.
3. **What implements each**: the design elements it is allocated to and that satisfy it.
4. **What shows each is met**: the verification entities that verify it, and the validation of the stakeholder level.
5. **The specifications** that present them: business, stakeholder, system and software requirements specifications, and the traceability and verification matrices.

## Views: no diagram types

29148 defines no diagram. It defines information items and two matrices. The SysML requirement diagram is described by `sysml-1`.

| View | What it admits |
|---|---|
| Business requirements specification (BRS) | Business requirements, needs and stakeholders. |
| Stakeholder requirements specification (StRS) | Stakeholder requirements, needs, stakeholders, constraints. |
| System requirements specification (SyRS) | System and system element requirements of every type, constraints, assumptions. |
| Software requirements specification (SRS) | Software requirements of the types functional, performance, interface, quality, usability, constraint, transition, and assumptions. |
| Operational concept (OpsCon) | Scenarios, user roles and workflows: stakeholders and needs. |
| Requirements traceability matrix (RTM) | For each requirement, its trace links: derive, allocate, satisfy, verify, sourced from. |
| Verification cross-reference matrix (VCRM) | For each requirement, its verification method, criteria, lead, event and venue. |

A specification can be a document or a part of a repository; physical documents are not required if the content is reachable and logically organized.

## Concepts, grouped

Definitions are in `language.yaml`. There are 30 concepts.

**Requirement levels** (what the requirement is stated about)

- **Requirement**: the general concept; every requirement is given a level and a type.
- **Business requirement**: why the change is wanted (goals, objectives, outcomes).
- **Stakeholder requirement**: what a stakeholder needs, with acceptance criteria and without implementation detail.
- **System requirement**: what the system as a whole must deliver.
- **System element requirement**: what one element must do, usually derived by allocation. **Software requirement** is the software case.

**Requirement types** (what the requirement requires; independent of level)

- **Functional**: what must be done. **Performance**: how well. **Interface**: how elements interact, traceable to both sides.
- **Quality (non-functional)**: a quality of the whole, stated so it can be measured, with a **quality category**. 29148 names reliability, availability, security, maintainability, portability, usability and performance. A project may use its own list. **Usability** is a quality requirement.
- **Human factors**: allocation of functions to people, personnel-equipment interaction.
- **Constraint**: a necessary design or implementation limit, validated with stakeholders.
- **Policy and regulation requirement**: an organization policy, business practice or outside regulation turned into a requirement.
- **Transition requirement**: temporary; needed only to reach the future state.
- **Process requirement**: a requirement on a process to follow.

**Related things**

- **Stakeholder**, **Need** (before it is stated as a requirement), **Source document**, **Trade study**, **Assumption**.
- **Business rule**: a directive that guides what the business does, as the BMM language defines it. A source of requirements, **not itself a requirement** in this language.
- **Design element**: what a requirement is allocated to and what satisfies it.
- **Verification entity**: a test case, analysis, inspection record or demonstration that shows a requirement is met.

**Information items**: the four requirements specifications and the operational concept.

## The attributes a requirement carries

Identifier (unique, never changed or reused), statement, rationale, priority, source, verification method, version, owner, risk, difficulty, type. Conditions and constraints are attributes too, not part of the sentence. 29148 lists these. The set is a default: a project decides which it keeps. Priority takes a scale the stakeholders agree, commonly high, medium, low. Verification method is inspection, analysis, demonstration or test.

## Relationship rules, in summary

Direction is client to supplier. The SysML skill describes the first seven in full.

- **Derive**: requirement to requirement; the derived requirement points at its parent.
- **Contain**: a compound requirement contains sub-requirements; only requirements nest in a requirement.
- **Satisfy**: a design element to the requirement it fulfills.
- **Verify**: a verification entity to the requirement it shows is met.
- **Refine**: an element to the requirement it makes more precise.
- **Trace**: a weak general link; do not mix it with the others.
- **Copy**: a slave requirement whose text is a read-only copy of its master's.
- **Allocate**: a requirement to the design element that receives it.
- **Sourced from**: a requirement to its origin: stakeholder, need, source document, trade study, business rule or parent requirement.
- **Constrained by**, **assumes**, **specified in**, and a need **held by** a stakeholder.

There is no table of allowed pairs in any source. `language.yaml` lists the endpoints. Outside them the language says nothing; the REL rules mark the ones that are errors.

## The rules that matter most

The full list, 92 rules with ids, strength and the clause or pointer each comes from, is in `references/rules.md`. Five are `must` (errors): the endpoint rules for derive, satisfy, verify, copy and containment, taken from SysML. The rest are `should` (warnings) or `note` (advice). The ones to keep in front of you:

- **Every requirement has a unique identifier, a statement, a rationale, a priority, a source and a verification method.** (REQ-ATTR-001, -003, -004, -005, -007, -008)
- **Every requirement traces to a source** so it can be recovered: a stakeholder, need, source document, trade study, business rule or parent. (REQ-TRACE-001)
- **Every system, system element and software requirement is verified by something.** Stakeholder and business requirements are validated instead. (REQ-TRACE-002, -003)
- **Every system requirement is allocated to a design element, and satisfied by one.** (REQ-TRACE-004, -005)
- **Every requirement below the business level traces up to a parent or need**, so lower requirements are justified; every stakeholder requirement is covered below. (REQ-TRACE-006, -007)
- **A well-formed requirement is** necessary, appropriate, unambiguous, complete, singular, feasible, verifiable, correct and conforming. (REQ-QUAL-001 to -009)
- **Wording**: shall for a requirement, will for a fact, should for a goal, may for an allowance; no "must", no "or" or "and/or", no vague or totality words, no unresolved "to be determined". (REQ-QUAL-012, -013, -016, -017, REQ-SET-002)
- **A well-formed set is** complete, consistent, feasible, comprehensible and able to be validated: no conflicts or overlaps, one unit system, one meaning per term. (REQ-SET-001 to -009)
- **A verification method has criteria**: inspection, analysis, demonstration or test, with how compliance is shown, who leads, when and where. (REQ-VERIF-001 to -003)

## Telling similar things apart

- **Stakeholder need or stakeholder requirement.** A need is what a stakeholder wants before anyone has written it as a testable statement; a stakeholder requirement is that statement.
- **Verify or validate.** Verification shows a requirement is met (built right); validation shows what was built meets the stakeholders' needs (the right thing built).
- **Functional or quality requirement.** Functional says what the system does; quality says how well, for the system as a whole, and is measurable.
- **Constraint or requirement.** A constraint limits the solution and is not for the team to change; a requirement states something the solution must do or be.
- **Derive, allocate or satisfy.** Derive links a requirement to its parent requirement. Allocate assigns a requirement to the design element that receives it. Satisfy links the element back to the requirement it fulfills.

## A short example

Westbrook Bank, a fictitious bank, wants business customers to open an account the same day. This is an illustration; use your own program, levels, types and attribute names.

- **Business requirement BR-01** (rationale: deposits are moving to competitors; priority high; source: the retail banking sponsor): "Business customers can open an account in one business day."
- **Stakeholder requirement SR-04**, derived from BR-01, sourced from the stakeholder "Relationship manager" and the need "Verify a new customer without a branch visit": "A relationship manager shall be able to verify a business customer's identity during the online application."
- **System requirement SYS-12** (functional), derived from SR-04, allocated to the design element "Onboarding service": "The Onboarding service shall return an identity-check result within 5 seconds of submission." (A quality requirement SYS-13, category performance, states that 95 percent of checks complete within 5 seconds at peak load.)
- **Verification**: the test case "Identity check latency under peak load" verifies SYS-12 and SYS-13; method test, criterion 95 percent within 5 seconds, lead the quality team, event the integration milestone.
- **Business rule**: "Customer identity is verified before an account is opened" is captured as a business rule. It is a source of SYS-12, not a requirement; SYS-12 is sourced from it.
- The **system requirements specification** holds SYS-12 and SYS-13; the **traceability matrix** shows BR-01 down to the test case.

A reviewer would flag a requirement here with no source (REQ-TRACE-001), one with no verifier (REQ-TRACE-002), SYS-13 if it said "fast" (REQ-QUAL-016), and any pair joined by "or".

## Data types and attributes

Partial, and only from summaries of 29148: the sources define no type system, no primitive types and no type for any attribute. They name value lists for four things, kept in `language.yaml` under `data_types` as enumerations: verification method (inspection, analysis, demonstration, test; 6.5.2.2), priority (high, medium, low, or a scale the stakeholders agree; 5.2.8), requirement type (5.2.8) and quality category (9.6.18, an open set). The twelve attributes of a requirement, with their sections, sit on the Requirement entry and every level and type inherits them; no other concept has a defined attribute, and no source gives a multiplicity.

## How it is drawn

Not defined. The sources give no symbol, shape, line style or diagram type for any concept or relationship, so none is stated here and none should be invented. 29148 presents requirements as specifications and as two matrices (traceability and verification), described under Views above. The one drawing of requirements, the SysML requirement diagram, is described in the `sysml-1` skill. Sizes and spacing come from `../_languages/layout-standard.yaml`, and the mapping from each concept to an element type comes from `layout` in `language.yaml`.

## References

- `references/standard.md`: the sources section by section, in our own words, with clause citations.
- `references/rules.md`: all 92 rules with stable ids (`REQ-<CAT>-nnn`), strength, checkability, basis and section.
- `language.yaml`: the machine-readable form: concepts (with the attributes on Requirement), data types, notation, value sets, relationships and the rules.
- The `sysml-1` skill for the relationship detail this one points to.
