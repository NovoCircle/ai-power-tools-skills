# Requirements modeling, section by section

This is a summary in our own words of the public sources the requirements language is built from. It does not reproduce them. Where a short phrase is quoted it is under 15 words and cited.

**Read this first about the sources.** No single standards body owns a requirements modeling language. Two sources are used:

1. **ISO/IEC/IEEE 29148:2018**, Systems and software engineering, Life cycle processes, Requirements engineering (Edition 2, November 2018; reviewed and confirmed 2024; https://www.iso.org/standard/72089.html). It is a standard of processes and information items. It defines no metamodel and no notation. **The standard is paid and was not read.** Everything attributed to it below comes from third-party summaries of its clauses, so the clause numbers are the standard's but the wording and strength ("shall" or "should") are not confirmed. An edition under development, DIS 29148, is expected to replace it.
2. **OMG SysML 1.5**, clause 16, which defines the requirement relationships. Described in full by the SysML language skill (`sysml-1`); this file points to it and does not repeat it.

Each section says which source a statement comes from. "Summary" means a third-party summary of the 29148 clause.

## 1. What the language is

A requirement is a statement that expresses a need together with the constraints and conditions on it, written in a form that can be checked. In a model, requirements are elements: each has a text, an identifier and attributes, belongs to a level and a type, and is linked to the things it comes from, the things that implement it and the things that show it is met.

The language does not say how to draw requirements. It says what a requirement is, what makes one good, what it must be linked to, and what the specifications that hold requirements contain. (Summary of 29148 clause 5 and clause 7.)

## 2. Levels (29148 clause 5.2.5 and clause 7)

29148 speaks of stakeholder, system and system element requirements, and has one specification for each level (the stakeholder, system and software requirements specifications) plus a business requirements specification. The language takes:

| Level | What it states | Source |
|---|---|---|
| Business | Why the change is wanted: goals, objectives, outcomes. | 29148 clause 7 and 9.3 (summary) |
| Stakeholder | What a stakeholder or class of stakeholders needs, with acceptance criteria and no implementation detail. | 29148 9.4 (summary) |
| System | What the complete system must deliver. | 29148 9.5 (summary) |
| System element | What one element must do, usually derived by allocating system requirements during architecture definition. A software requirement is a system element requirement for a software element. | 29148 5.2.5, 5.3.2, 6.5.1.2, 9.6 (summary); the software generalization is our inference |

## 3. Types (29148 clause 5.2.8, 6.4.3.3, clause 9)

The type is an attribute of a requirement and is independent of its level. 29148 lists these types: functional and performance, interface, process, quality or non-functional, usability and quality in use, and human factors (5.2.8, summary). The specification clauses add three more kinds that stand as requirements of their own: constraints (6.4.3.3), policy and regulation requirements (9.5.15), and transition requirements (6.4.3.3).

- **Functional**: what a function, system or element must do.
- **Performance**: how well, in measures of performance and technical performance measures.
- **Interface**: how elements interface and interact; traceable to both sides of the interface (6.5.1.2).
- **Quality (non-functional)**: a quality of the whole, ideally measurable. The system specification names usability and quality in use; the software specification names reliability, availability, security, maintainability and portability (9.6.18).
- **Human factors**: allocation of functions to people, personnel-equipment interaction, facilities (9.5.9).
- **Constraint**: a necessary implementation or design limit, validated with stakeholders (6.4.3.3).
- **Policy and regulation**: an organization policy, business practice or outside regulation stated as a requirement (9.5.15).
- **Transition**: a temporary capability needed only to reach the future state; migration, installation, acceptance (6.4.3.3).

**Business rule.** The BMM language defines a business rule as a kind of directive. This language treats a business rule as a source of requirements, not as a requirement itself. 29148 turns policies and regulations into requirements (9.5.15).

## 4. The requirement construct (29148 clause 5.2.4, summary)

A well-formed requirement names its subject and states either an action or a constraint on that subject. It answers a problem, objective or stakeholder concern, carries measurable conditions where they apply, is bounded by constraints, expresses a capability or performance of the system rather than of its user or operator, and can be verified. The project agrees marker words before writing starts: "shall" for a requirement, "will" for a fact, futurity or purpose, "should" for a goal that is not a requirement, "may" for an allowance. "Must" and "shall be able to" are avoided, and so are negative and passive phrasing. Terms are defined once and used consistently. Conditions and constraints are captured as attributes. Requirements may be ranked or weighted by priority.

## 5. Characteristics of one requirement (29148 clause 5.2.5, summary)

A requirement is:

| Characteristic | Meaning in our words |
|---|---|
| Necessary | An essential capability, characteristic, constraint or quality factor; its removal would leave a gap; still current; any expiry date marked. |
| Appropriate | Detail and intent suit the level; architecture and design left free where possible; extra detail in attributes such as rationale. |
| Unambiguous | One reading only, simply stated. |
| Complete | Understood without further information. |
| Singular | One capability, characteristic, constraint or quality factor, although several conditions may apply. |
| Feasible | Achievable within cost, schedule and technical limits at acceptable risk. |
| Verifiable | Its realization can be proven to the customer at its level; measurable helps. |
| Correct | A faithful expression of the need it came from. |
| Conforming | Follows the approved template and style where one applies. |

## 6. Language criteria (29148 clause 5.2.7, summary)

Requirements say what is needed, not how it is achieved. Vague and unbounded wording defeats verification and is avoided: superlatives, subjective language, vague pronouns, ambiguous adverbs and adjectives, open-ended phrases, comparatives, loopholes such as "if possible" or "as applicable", words implying totality such as "all" or "never", and references that omit the date, version or applicable part. "Or" and "and/or" are avoided; such a requirement is split. Every assumption behind a requirement is documented and validated, in an attribute such as rationale or in an accompanying document. Definitions are declarative statements, not requirements.

## 7. Characteristics of a set (29148 clause 5.2.6, summary)

A set of requirements is:

| Characteristic | Meaning |
|---|---|
| Complete | Stands alone and describes the needed capabilities, characteristics, constraints and quality factors without outside information. Holds no unresolved open-item markers (to be defined, to be specified, to be resolved); those that remain have a timeframe set by risk and dependencies. Completeness improves when every relevant requirement type, life cycle stage and stakeholder group is covered. |
| Consistent | Requirements are unique, do not conflict or overlap, use homogeneous units and measurement systems, and each term keeps one meaning. |
| Feasible | Achievable as a whole, which includes being affordable. |
| Comprehensible | What is expected and how it relates to the containing system is clear. |
| Able to be validated | Meeting the set will practically achieve the needs within cost, schedule, technical, legal and regulatory limits. |

The set is checked against these so that requirements creep does not later drive cost, schedule or quality.

## 8. Attributes (29148 clause 5.2.8, 6.4.3.3)

A requirement carries descriptive attributes with it:

- **Identifier**: unique, never changed or reused, even when the requirement is revised or deleted, so tracing stays intact.
- **Statement**: the requirement text (5.2.4).
- **Version**: which text is being implemented and how volatile it is.
- **Owner**: who maintains it, approves changes and reports status.
- **Priority**: stakeholder priority, agreed on a scale or as high, medium or low.
- **Risk**: including inherited risk and risk from immature technology.
- **Rationale**: points to the analysis, trade study, model or simulation behind it.
- **Difficulty**: the assumed difficulty.
- **Type**: groups requirements for analysis and allocation.
- **Source**: where it comes from; recorded for every requirement (6.3.3.7, 6.4.3.3).
- **Verification method**: how it will be verified (6.4.3.3).

## 9. Traceability and derived requirements (29148 clauses 5.3.2, 6.x; summary)

Stakeholders view the system at different levels, so requirements are written below the system of interest by allocating system requirements to elements during architecture definition. Derived requirements state relationships between elements, give clarity at the lower level, or impose design constraints or performance levels on elements. Some can be derived only once part of the architecture exists. Critical requirements, those with high risk or affecting public safety, the environment or health, are analyzed more rigorously. Iteration back to requirements is expected.

Traceability is set up and kept so that:

- every requirement's source can be recovered and the effect of a change predicted (6.4.3.5);
- each requirement traces **downward** to lower-level requirements (through allocation), to the architecture, to the elements that implement it and to the entities that verify it, and **upward** to its parents or the needs it came from;
- a requirement that came out of a trade study or design study traces to that study, and the study traces to the requirements that informed it;
- trace links between stakeholder needs and stakeholder requirements show how the formal requirements meet the stakeholder objectives (6.3.3.7);
- coverage can be shown: every stakeholder requirement is met in the design and every lower-level requirement is justified (6.4.3.5);
- interface requirements are traceable to both sides of the interface (6.5.1.2);
- the links are under configuration control (6.3.3.7, 6.6.2.2.3).

The **relationship vocabulary** is not 29148's. It comes from SysML clause 16 (via `sysml-1`): derive, satisfy, verify, refine, trace, copy and containment, with endpoint constraints. See the relationship summary in `SKILL.md` and the table in `language.yaml`.

## 10. Verification (29148 clause 6.5.2.2, summary)

An appropriate verification method, with its criteria, is chosen for every verification action, ideally assigned as the requirement is written, and documented in a requirements verification and traceability matrix or as statements in a verification plan. Each method says how compliance will be shown (including success criteria and how the item is closed), who leads it, when it happens (an event-based milestone rather than a date) and where. Four standard methods give the objective evidence:

- **Inspection**: examination against named documents or drawings.
- **Analysis**: including modeling and simulation where realistic testing is impractical. Analysis by similarity is acceptable only when the items match in design, manufacture and use, the earlier verification was equal or stricter and the intended environment is no harsher.
- **Demonstration**: a qualitative showing of function with little or no instrumentation, naming witnesses, steps and special resources.
- **Test**: quantitative verification under controlled real or simulated conditions, naming witnesses, facility, equipment, conditions, personnel qualifications, data to collect, repeatability criteria and analysis methods.

Certification, a written assurance usually from an independent party against a recognized standard, is sometimes used instead.

**Validation** (6.5.3.2, 6.5.3.3, summary) shows that what was built meets the needs the stakeholders expressed. The trace is kept for every validated element and can be held in the traceability matrix or a comparable item.

## 11. Information items (29148 clause 7 and 9, summary)

Requirements engineering produces a business requirements specification (BRS), a stakeholder requirements specification (StRS), a system requirements specification (SyRS) and, under ISO/IEC/IEEE 12207, a software requirements specification (SRS), each with the content clause 9 defines. Several instances of each may be produced, they may carry other titles or sit inside other items, and physical documents are not required if the content is readily reachable and logically organized, for example in a modeling repository. An operational concept (OpsCon) describes scenarios, user roles and workflows.

- **Common content (9.2):** identification, front matter, definitions, references, acronyms.
- **BRS (9.3):** organization-level reasons, the business environment and processes, high-level system proposal.
- **StRS (9.4):** background and goals, environment, stakeholder requirements with acceptance criteria and no implementation detail, operating modes, user classes.
- **SyRS (9.5):** reasons and scope; functional requirements; usability and quality in use; human system integration; modes and states; physical, adaptability and environmental requirements; security; policies and regulations; verification; assumptions and dependencies.
- **SRS (9.6):** purpose and scope; the product's relationship to its context; major functions and their allocation to software elements; the requirements themselves; external interfaces; usability; logical data requirements; software attributes (reliability, availability, security, maintainability, portability); verification; supporting information. Requirements here are detailed enough to design, build and verify the current increment and show all the characteristics.

Only parts of clause 9 were reachable through the summaries; the lists above are not complete.

## 12. Conformance (clause 4, summary)

An organization may claim conformance to the processes, to the information items, or to both. No body certifies against the standard. It permits user stories in place of formal "shall" statements, according to one vendor summary (unverified).

## 13. What the sources do not give

- No metamodel, so no abstract syntax, no machine-readable model and no relationship table.
- No multiplicities.
- No drawing rules. The requirement diagram of SysML is described by `sysml-1`.
- No wording of strength for the 29148 clauses, because the standard was not read.
