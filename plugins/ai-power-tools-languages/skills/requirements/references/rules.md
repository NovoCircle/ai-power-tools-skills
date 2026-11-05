# Requirements modeling rules

Generated from `language.yaml` (`constraints`). Do not edit by hand; change the language file and regenerate.

Each rule has a stable id of the form `REQ-<CAT>-nnn`. The number never changes once assigned. A rule that is retired keeps its id and is marked withdrawn rather than reused.

## Where the rules come from

No single standards body owns a requirements language. The rules come from two public sources, and the basis column says which:

| Basis | Meaning |
|---|---|
| iso-summary | ISO/IEC/IEEE 29148:2018, taken from third-party summaries of its clauses. The standard is paid and was not read, so its wording of strength is unknown and these rules are `should` or `note`. Section numbers are the standard's clause numbers. |
| sysml-skill | OMG SysML 1.5 clause 16, as described by the `sysml-1` skill. The section column quotes that skill's rule id (`SYSML-REQ-nnn`). |
| inferred | A reading of the sources, not stated by any of them. |

## Strength

| Strength | Meaning |
|---|---|
| must | A formal constraint on a relationship's ends, stated as a constraint by the source. Breaking it is an error. |
| should | Guidance, a characteristic, or a cardinality stated only in prose. Breaking it is a warning, not an error. |
| note | An expectation, an option or a method note, recorded for completeness and not checkable on its own. |

## Checkable

| Value | Meaning |
|---|---|
| static | A program that sees only the saved model can check it. |
| partial | Only the structure or simple cases can be checked (for example a word list), the rest needs a reader. |
| runtime | Needs process or history, not only the saved model. |
| none | A judgment, not something a program can read. |

## Categories

| Category | Name | Covers | Rules |
|---|---|---|---|
| KIND | Classification | What a requirement is: its level (business, stakeholder, system, system element) and its type, and how the kinds are told apart. | 5 |
| ATTR | Attributes | The descriptive attributes a requirement carries: identifier, statement, rationale, priority, source, verification method and the rest. | 14 |
| QUAL | Quality of one requirement | The nine characteristics of a well-formed requirement, its construct, and the language criteria for its wording. | 21 |
| SET | Quality of a requirement set | The characteristics of a set of requirements taken together. | 10 |
| TRACE | Traceability | Which links a requirement must have: to a source, to a verifying entity, to a parent, to a design element. | 12 |
| REL | Relationship endpoints | Which kinds of element a requirement relationship may join. | 11 |
| VERIF | Verification | How a requirement is verified: method, criteria, record. | 6 |
| SPEC | Information items | What the requirements specifications are and what they hold. | 8 |
| GUID | Guidance | Method notes and recommendations that are not checkable on their own. | 5 |

Section references are to the clauses of ISO/IEC/IEEE 29148:2018, or to the pointer ids named above. Where a rule applies only to some elements or in some situations, the statement or the `applies_when` note says so.

## KIND: Classification

| Id | Strength | Checkable | Basis | Rule | Section |
|---|---|---|---|---|---|
| REQ-KIND-001 | should | static | iso-summary | Every requirement has a level: business, stakeholder, system, system element (including software). | 5.2.5; clause 7 |
| REQ-KIND-002 | should | static | iso-summary | Every requirement has a type: functional or performance, interface, process, quality (non-functional), usability or quality in use, or human factors; constraint, policy and regulation, and transition requirements are further types. | 5.2.8 |
| REQ-KIND-003 | should | none | iso-summary | Necessary implementation constraints are defined and validated with the stakeholders, including those of interfacing and enabling systems and of regulation. | 6.4.3.3 |
| REQ-KIND-005 | should | static | iso-summary | A quality requirement names its quality category, from the quality category value set or one the project defines. (applies when: quality requirement) | 9.6.18; 9.5.5 |
| REQ-KIND-009 | should | none | iso-summary | A requirement expresses a capability or performance of the system, not of the user or operator. | 5.2.4 |

## ATTR: Attributes

| Id | Strength | Checkable | Basis | Rule | Section |
|---|---|---|---|---|---|
| REQ-ATTR-001 | should | static | iso-summary | Every requirement has an identifier, and no two requirements have the same identifier. | 5.2.8; SYSML-REQ-007 |
| REQ-ATTR-002 | should | runtime | iso-summary | An identifier is never changed or reused, even when the requirement is revised or deleted, so that tracing stays intact. | 5.2.8 |
| REQ-ATTR-003 | should | static | iso-summary | Every requirement has a statement (its text). | 5.2.4; SYSML-REQ-007 |
| REQ-ATTR-004 | should | static | iso-summary | Every requirement has a rationale, pointing to the analysis, trade study, model or simulation behind it. | 5.2.8; 6.4.3.3 |
| REQ-ATTR-005 | should | static | iso-summary | Every requirement has a stakeholder priority. | 5.2.8 |
| REQ-ATTR-007 | should | static | iso-summary | The source of every requirement is recorded. Recorded as a link, so this rule is checked by REQ-TRACE-001. | 6.3.3.7; 6.4.3.3 |
| REQ-ATTR-008 | should | static | iso-summary | Every requirement has a verification method, ideally assigned as the requirement is written. | 6.4.3.3; 6.5.2.2 |
| REQ-ATTR-009 | should | static | iso-summary | Every requirement has a version stating which text is being implemented and how volatile it is. | 5.2.8 |
| REQ-ATTR-010 | should | static | iso-summary | Every requirement has an owner who maintains it, approves its changes and reports its status. | 5.2.8 |
| REQ-ATTR-011 | should | static | iso-summary | Every requirement has a risk value, including risk inherited from its parent and risk from immature technology. | 5.2.8 |
| REQ-ATTR-012 | note | none | iso-summary | A requirement may carry the assumed difficulty of meeting it. | 5.2.8 |
| REQ-ATTR-013 | should | static | iso-summary | Every requirement has a type, used to group requirements for analysis and allocation. | 5.2.8 |
| REQ-ATTR-016 | should | partial | iso-summary | Priority is stated on a scale the stakeholders have agreed, or as high, medium or low. | 5.2.8 |
| REQ-ATTR-017 | should | none | iso-summary | Conditions, constraints and extra detail are held as attributes of the requirement (for example the rationale), not packed into its statement. | 5.2.4; 5.2.5 |

## QUAL: Quality of one requirement

| Id | Strength | Checkable | Basis | Rule | Section |
|---|---|---|---|---|---|
| REQ-QUAL-001 | should | none | iso-summary | A requirement is necessary: it states an essential capability, characteristic, constraint or quality factor, its removal would leave a gap that nothing else fills, and it is still current. A planned expiry or applicability date is marked. | 5.2.5 |
| REQ-QUAL-002 | should | none | iso-summary | A requirement is appropriate: its detail and intent suit the level of the entity it is stated for, leaving architecture and design free where possible, with extra detail held in attributes such as rationale. | 5.2.5 |
| REQ-QUAL-003 | should | partial | iso-summary | A requirement is unambiguous: it can be read in one way only and is simply stated. | 5.2.5 |
| REQ-QUAL-004 | should | partial | iso-summary | A requirement is complete: it can be understood without further information. | 5.2.5 |
| REQ-QUAL-005 | should | partial | iso-summary | A requirement is singular: it states one capability, characteristic, constraint or quality factor, although several conditions may apply. | 5.2.5 |
| REQ-QUAL-006 | should | none | iso-summary | A requirement is feasible: it can be achieved within cost, schedule and technical limits at acceptable risk. | 5.2.5 |
| REQ-QUAL-007 | should | partial | iso-summary | A requirement is verifiable: its realization can be proven to the customer at the level where it sits, helped by being measurable. | 5.2.5 |
| REQ-QUAL-008 | should | none | iso-summary | A requirement is correct: it is a faithful expression of the need it came from. | 5.2.5 |
| REQ-QUAL-009 | should | partial | iso-summary | A requirement is conforming: it follows the approved template and style where one applies. | 5.2.5 |
| REQ-QUAL-010 | should | partial | iso-summary | A requirement names its subject (for example the system or the software) and states either an action or a constraint on that subject, answering a problem, objective or stakeholder concern. | 5.2.4 |
| REQ-QUAL-011 | should | partial | iso-summary | Where it applies, a requirement carries measurable conditions and is bounded by constraints. | 5.2.4 |
| REQ-QUAL-012 | should | partial | iso-summary | The project agrees the marker words before writing starts: shall for a requirement, will for a fact, futurity or purpose, should for a goal that is not a requirement, may for an allowance. | 5.2.4 |
| REQ-QUAL-013 | should | partial | iso-summary | The words "must" and "shall be able to" are avoided, and so are negative and passive phrasing. | 5.2.4 |
| REQ-QUAL-014 | should | partial | iso-summary | Requirements-engineering terms are defined once and used consistently. | 5.2.4 |
| REQ-QUAL-015 | should | none | iso-summary | A requirement says what the system of interest needs, not how it is achieved; design decisions appear only as they are recognized from higher levels during allocation. | 5.2.7 |
| REQ-QUAL-016 | should | partial | iso-summary | Vague and unbounded wording is avoided: superlatives, subjective language, vague pronouns, ambiguous adverbs and adjectives, open-ended phrases, comparatives, loopholes such as if possible or as applicable, and words implying totality such as all or never. | 5.2.7 |
| REQ-QUAL-017 | should | partial | iso-summary | The logic words "or" and "and/or" are avoided in a requirement; such a requirement is split into separate requirements. | 5.2.7 |
| REQ-QUAL-018 | should | partial | iso-summary | A reference to another document gives its date, version and the applicable part. | 5.2.7 |
| REQ-QUAL-019 | should | partial | iso-summary | Every assumption behind a requirement is documented and validated, in an attribute such as rationale or in an accompanying document. | 5.2.7; 9.5.19 |
| REQ-QUAL-020 | should | none | iso-summary | A definition is written as a declarative statement, not as a requirement. | 5.2.7 |
| REQ-QUAL-021 | note | none | iso-summary | The nine characteristics apply to stakeholder requirements, system requirements and system element requirements alike. | 5.2.5 |

## SET: Quality of a requirement set

| Id | Strength | Checkable | Basis | Rule | Section |
|---|---|---|---|---|---|
| REQ-SET-001 | should | partial | iso-summary | A requirement set is complete: it stands alone, describing the needed capabilities, characteristics, constraints and quality factors without outside information. | 5.2.6 |
| REQ-SET-002 | should | partial | iso-summary | A requirement set holds no unresolved open-item markers (to be defined, to be specified, to be resolved); any that remain have a timeframe for settling them, set by risk and dependencies. | 5.2.6 |
| REQ-SET-003 | note | none | iso-summary | Completeness improves when every relevant requirement type, every life cycle stage and every stakeholder group is covered. | 5.2.6 |
| REQ-SET-004 | should | partial | iso-summary | A requirement set is consistent: its requirements are unique and do not conflict or overlap. | 5.2.6 |
| REQ-SET-005 | should | partial | iso-summary | A requirement set uses homogeneous units and measurement systems. | 5.2.6 |
| REQ-SET-006 | should | partial | iso-summary | Each term in a requirement set keeps one meaning throughout. | 5.2.6 |
| REQ-SET-007 | should | none | iso-summary | A requirement set is feasible as a whole, which includes being affordable. | 5.2.6 |
| REQ-SET-008 | should | none | iso-summary | A requirement set is comprehensible: what is expected, and how it relates to the containing system, is clear. | 5.2.6 |
| REQ-SET-009 | should | none | iso-summary | A requirement set is able to be validated: meeting the set will practically achieve the needs within cost, schedule, technical, legal and regulatory limits. | 5.2.6 |
| REQ-SET-010 | note | none | iso-summary | The set is checked against these properties so that requirements creep does not later drive cost, schedule or quality. | 5.2.6 |

## TRACE: Traceability

| Id | Strength | Checkable | Basis | Rule | Section |
|---|---|---|---|---|---|
| REQ-TRACE-001 | should | static | iso-summary | Every requirement traces to a source (a stakeholder, a need, a source document, a trade study, a business rule or a parent requirement), so that the source can be recovered. | 6.2.3.6; 6.3.3.7; 6.4.3.5 |
| REQ-TRACE-002 | should | static | iso-summary | Every system, system element and software requirement is verified by at least one verification entity. (applies when: system, system element or software requirement) | 6.4.3.5; 6.5.2.2 |
| REQ-TRACE-003 | should | static | iso-summary | Every business and stakeholder requirement can be traced to what validates it, showing that the right system was built. (applies when: validation is planned) | 6.5.3.3 |
| REQ-TRACE-004 | should | static | iso-summary | Every system requirement is allocated to at least one design element. (applies when: the architecture is defined) | 6.5.1.2; 6.4.3.5 |
| REQ-TRACE-005 | should | static | iso-summary | Every system and system element requirement is satisfied by at least one design element. (applies when: a design exists) | 6.4.3.5 |
| REQ-TRACE-006 | should | static | iso-summary | Every requirement below the business level traces upward to at least one parent requirement or the need it came from, so that every lower-level requirement is justified. | 6.4.3.5; 5.3.2 |
| REQ-TRACE-007 | should | static | iso-summary | Every stakeholder requirement is met by at least one lower-level requirement or design element, so that the coverage of stakeholder requirements can be shown. (applies when: lower levels exist) | 6.4.3.5 |
| REQ-TRACE-008 | should | static | iso-summary | An interface requirement is traceable to both sides of the interface it governs. (applies when: interface requirement) | 6.5.1.2 |
| REQ-TRACE-009 | should | partial | iso-summary | A requirement that came from a trade study or design study traces to that study, and the study traces to the higher-level requirements that informed it. (applies when: requirement from a study) | 6.4.3.5 |
| REQ-TRACE-010 | should | runtime | iso-summary | Trace links, rationale, decisions, assumptions and change history are kept under configuration control as the requirements change. | 6.3.3.7; 6.4.3.5; 6.6.2.2.3 |
| REQ-TRACE-011 | should | runtime | iso-summary | The verification and validation criteria for an element are written down when its derived requirements are created. | 6.5.1.2 |
| REQ-TRACE-012 | note | none | iso-summary | Traceability is bidirectional and supports coverage analysis, compliance analysis and impact analysis. | 6.4.3.5 |

## REL: Relationship endpoints

| Id | Strength | Checkable | Basis | Rule | Section |
|---|---|---|---|---|---|
| REQ-REL-001 | must | static | sysml-skill | Both ends of a derive relationship are requirements. | SYSML-REQ-012; SYSML-REQ-013 |
| REQ-REL-002 | must | static | sysml-skill | The target of a satisfy relationship is a requirement. | SYSML-REQ-016 |
| REQ-REL-003 | must | static | sysml-skill | The target of a verify relationship is a requirement. | SYSML-REQ-019 |
| REQ-REL-004 | must | static | sysml-skill | Both ends of a copy relationship are requirements. | SYSML-REQ-009 |
| REQ-REL-005 | must | static | sysml-skill | Only requirements are contained in a requirement. | SYSML-REQ-005 |
| REQ-REL-006 | should | partial | sysml-skill | The trace relationship has weak meaning and is not mixed with the other requirement relationships. | SYSML-REQ-021 |
| REQ-REL-007 | note | none | sysml-skill | The text of a copy is a read-only copy of its master text, and the rule applies to all sub-requirements. | SYSML-REQ-010; SYSML-REQ-011 |
| REQ-REL-008 | should | static | inferred | A requirement is not derived from itself, directly or through other derived requirements. | 5.3.2; SYSML-REQ-012 |
| REQ-REL-009 | should | static | inferred | A requirement is derived from a requirement at the same or a higher level (business, then stakeholder, then system, then system element), not from a lower one. | 5.3.2 |
| REQ-REL-010 | should | static | iso-summary | The source of an allocate relationship is a requirement and its target is a design element. | 6.5.1.2 |
| REQ-REL-012 | note | none | sysml-skill | In SysML a requirement is a leaf of its own kind: it owns no operations or attributes, takes part in no association or generalization, and types nothing. That is a rule of the SysML profile, not of this language. | SYSML-REQ-001 to -006 |

## VERIF: Verification

| Id | Strength | Checkable | Basis | Rule | Section |
|---|---|---|---|---|---|
| REQ-VERIF-001 | should | static | iso-summary | An appropriate verification method, with its criteria, is selected for every verification action, ideally as each requirement is written. | 6.5.2.2 |
| REQ-VERIF-002 | should | static | iso-summary | A verification method is one of inspection, analysis, demonstration or test; certification is sometimes used instead. | 6.5.2.2 |
| REQ-VERIF-003 | should | partial | iso-summary | Each verification method states how compliance will be shown, the success criteria and how the item is closed, who leads, when it happens (an event-based milestone rather than a calendar date), and where. | 6.5.2.2 |
| REQ-VERIF-004 | should | none | iso-summary | Analysis by similarity is used only when the items match in design, manufacture and use, the earlier verification was equal or stricter, and the intended environment is no harsher. (applies when: analysis by similarity) | 6.5.2.2 |
| REQ-VERIF-005 | should | partial | iso-summary | Verification methods and results are recorded in a requirements traceability matrix, a verification cross-reference matrix, or verification statements in a verification plan. | 6.5.2.2 |
| REQ-VERIF-006 | note | none | iso-summary | Inspection examines against named documents or drawings; analysis includes modeling and simulation and names its tools and input data; demonstration is a qualitative showing of function; test is quantitative verification under controlled real or simulated conditions. | 6.5.2.2 |

## SPEC: Information items

| Id | Strength | Checkable | Basis | Rule | Section |
|---|---|---|---|---|---|
| REQ-SPEC-001 | should | none | iso-summary | Requirements engineering produces a business requirements specification, a stakeholder requirements specification, a system requirements specification and, under ISO/IEC/IEEE 12207, a software requirements specification, each with the content clause 9 defines. | clause 7 |
| REQ-SPEC-002 | note | none | iso-summary | Several instances of each specification may exist (for example a system requirements specification per system element); they may carry other titles or sit inside other information items if their content can be clearly referenced. Physical documents are not required if the content is readily reachable and logically organized. | clause 7 |
| REQ-SPEC-003 | should | partial | iso-summary | A specification kept in document form has identification, front matter, definitions, references and spelled-out acronyms. | 9.2 |
| REQ-SPEC-004 | should | partial | iso-summary | The requirements in a system or software requirements specification show all the characteristics of a requirement (REQ-QUAL-001 to -009) and are detailed enough to design, build and verify the current increment. | 9.6.10 |
| REQ-SPEC-005 | should | partial | iso-summary | A system or software requirements specification states how the system or software will be qualified, giving the verification approach and method alongside each requirement area. | 9.5.18; 9.6.19 |
| REQ-SPEC-006 | should | partial | iso-summary | A system requirements specification records each assumption and dependency behind its requirements. | 9.5.19 |
| REQ-SPEC-007 | note | none | iso-summary | A stakeholder requirements specification states expectations with acceptance criteria and no implementation detail; a system requirements specification turns relevant policies, business practices and outside regulation into requirements. | 9.4; 9.5.15 |
| REQ-SPEC-008 | should | runtime | iso-summary | The specifications are placed under configuration control and provided as baselined items. | 6.4.3.5; 6.6.2.2.3 |

## GUID: Guidance

| Id | Strength | Checkable | Basis | Rule | Section |
|---|---|---|---|---|---|
| REQ-GUID-001 | note | none | iso-summary | A claim of conformance may cover the processes, the information items, or both. No body certifies against the standard. | clause 4 |
| REQ-GUID-002 | should | none | iso-summary | Critical requirements, those with high risk or affecting public safety, the environment or health, are analyzed more rigorously than others. | 5.3.2 |
| REQ-GUID-003 | note | none | iso-summary | Requirements are written recursively: derived requirements arise during architecture definition, and iteration back into requirements is expected because requirements are never perfect. | 5.3.2 |
| REQ-GUID-004 | should | none | iso-summary | The whole body of stakeholder requirements is analyzed against the characteristics of one requirement and of a set, then ranked and classified, and fed back to the stakeholders to confirm their needs are captured before resources are committed. | 6.3.3.6 |
| REQ-GUID-005 | note | none | iso-summary | Requirements are configuration controlled, with rationale, decisions, assumptions, change history and categorization recorded. | 6.4.3.5 |
