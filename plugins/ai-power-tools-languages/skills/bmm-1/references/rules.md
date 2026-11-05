# BMM 1.3 rules

Generated from `language.yaml` (`constraints`). Do not edit by hand; change the language file and regenerate.

Each rule has a stable id of the form `BMM-<CAT>-nnn`. The number never changes once assigned. A rule that is retired keeps its id and is marked withdrawn rather than reused.

## Strength

| Strength | Meaning |
|---|---|
| must | The standard states it as a requirement or a necessity clause. A model that breaks it is not well formed. |
| should | The standard gives it as guidance ("should", "generally", "tends to"), or states a cardinality only in its prose. Breaking it is a warning, not an error. |
| note | The standard states it as an expectation, an option or a method note. It is recorded for completeness and is not checkable on its own. |

## Categories

| Category | Name | Covers | Rules |
|---|---|---|---|
| CARD | Cardinality and necessity | How many of one concept a relationship may or must connect, including the default that everything is optional. | 8 |
| HIER | Hierarchy | Rules for the relationships that connect a concept to its own kind (broader and narrower, includes and included). | 3 |
| DEF | Definition | Rules that state what makes one concept different from a neighbor, so that an element is placed correctly. | 3 |
| REL | Relationship use | Rules about which concepts should or must be connected, and by what route. | 7 |
| QUAL | Statement quality | Rules about how the text of an element is worded, so that it matches the concept it claims to be. | 9 |
| GUID | Guidance and scope | Method notes, optional parts of the model and recommendations that are not checkable on their own. | 9 |

Section references are to the clauses and annexes of the BMM 1.3 specification (formal/15-05-19); "p." gives the printed page where the standard is specific. Multiplicities on the individual relationships are in `language.yaml` and are not repeated here.

## CARD: Cardinality and necessity

| Id | Strength | Rule | Section |
|---|---|---|---|
| BMM-CARD-001 | should | Every Assessment judges at least one Influencer and affects the achievement of at least one End or the employment of at least one Means. | 9.2 (Assessment entry), p. 59 |
| BMM-CARD-002 | should | Every Assessment identifies at least one Potential Impact. | 9.2 (Assessment entry), p. 59 |
| BMM-CARD-003 | should | Every Assessment is made by at least one Organization Unit. | 9.2 (Organization Unit entry), p. 68 |
| BMM-CARD-004 | should | Every End is defined by at least one Organization Unit. | 9.2 (Organization Unit entry), p. 68 |
| BMM-CARD-005 | must | A Goal amplifies at most one Vision. | 9.2 (Goal entry), p. 65 |
| BMM-CARD-006 | must | A Mission makes operative at most one Vision. | 9.2 (Mission entry), p. 66 |
| BMM-CARD-007 | must | An Influencing Organization is played by at most one Organization Unit, and a Regulation is the role of at most one Directive. | 8.5.3; 8.5.4; normative machine-readable model |
| BMM-CARD-008 | must | Unless a rule says otherwise, every relationship is many-to-many and optional at both ends. | 6.1; Annex A |

## HIER: Hierarchy

| Id | Strength | Rule | Section |
|---|---|---|---|
| BMM-HIER-001 | must | A Desired Result includes only Desired Results of its own kind: Goals include Goals and Objectives include Objectives. The only link between a Goal and an Objective is that the Objective quantifies the Goal. | 9.2 (Desired Result entry), p. 63; 8.2.6.1 |
| BMM-HIER-002 | must | Each of the nine relationships that connect a concept to itself (listed in 8.7) is transitive and may not form a loop: a category cannot, directly or through its descendants, include or categorize its own ancestor. | 8.7, p. 58 |
| BMM-HIER-003 | should | A Course of Action includes Courses of Action of the same kind (Strategies with Strategies, Tactics with Tactics), and one Course of Action enables another of the same kind in the usual case. | 8.3.12.1; 8.3.12.2 |

## DEF: Definition

| Id | Strength | Rule | Section |
|---|---|---|---|
| BMM-DEF-001 | note | A Business Policy is under the enterprise's control: an authorized party chooses it from alternatives in response to one or more Assessments. | 8.3.10; 9.2 (Business Policy entry) |
| BMM-DEF-002 | must | A Business Rule is practicable and atomic: one aspect of governance in the enterprise's standard vocabulary, which a person can check directly against a situation. A Business Policy is neither directly practicable nor directly automatable. | 8.3.9; 8.3.11; 9.2 |
| BMM-DEF-003 | must | An enforcement level applies only to behavior-guiding rules, never to definitional rules, which are true by definition. A Tactic is what sets the enforcement level of a Business Rule. | 8.3.7 and footnote 4; 9.2 |

## REL: Relationship use

| Id | Strength | Rule | Section |
|---|---|---|---|
| BMM-REL-001 | must | An Objective that quantifies a Goal gives the basis for measuring progress toward that Goal. | 8.2.5; 9.2 (Objective entry) |
| BMM-REL-002 | should | Every Course of Action is governed by some Directive. A Course of Action with none should be examined carefully, although too many Directives can over-constrain it. | 8.3.6, p. 31 |
| BMM-REL-003 | note | A Business Rule is often, but not necessarily, derived from a Business Policy; the link is optional. | 8.3.11 |
| BMM-REL-004 | must | An Influencer leads to a Business Policy only through an Assessment that identifies a Potential Impact. | 8.5.7, p. 50 |
| BMM-REL-005 | should | When an Assessment is related to both an End and a Means and no direct relationship joins them (Course of Action channels efforts towards Desired Result, or Directive supports achievement of Desired Result), the gap should be considered carefully. | 8.5.5; 9.2 (Assessment entry) |
| BMM-REL-006 | should | Each Influencer is placed in at least one general Influencer Category and is classed as internal or external. The class may be given by a subclass (Internal Influencer or External Influencer) or by an instance of an internal or external Influencer Category; either mechanism satisfies the rule. | 8.5.2; Annex G.3 |
| BMM-REL-007 | must | A relationship between two BMM concepts is allowed only if the standard defines that relationship (one of its fact types) between those concepts or concepts they specialize. The standard's relationship catalog is held as data in this language file; a pair it does not list allows no relationship. | 9.5; 9.6 |

## QUAL: Statement quality

| Id | Strength | Rule | Section |
|---|---|---|---|
| BMM-QUAL-001 | must | An Objective is attainable, time-targeted and measurable. Time-targeted means it states an absolute or relative time frame for when it is met. Measurable means it carries explicit criteria for whether it is being met, at minimum a yes-or-no basis. | 8.2.5, p. 24; 7.3.1 |
| BMM-QUAL-002 | should | An Objective statement begins with its time target, followed by a quantified noun. | 8.2.5, p. 25 |
| BMM-QUAL-003 | should | A Goal is narrow enough that Objectives can quantify it. A Vision is too broad to be measured directly by Objectives, and Goals themselves are not specific in time or measure. | 8.2.3; 8.2.4 |
| BMM-QUAL-004 | should | A Mission statement has exactly three brief parts and nothing more: an action, a product or service, and a market or customer. It stays day to day and broad enough to cover all Strategies. | 8.3.2, p. 28 |
| BMM-QUAL-005 | should | Qualitative or comparative words that describe a desired end state (best, fastest, leading-edge) belong in Ends and Directives, not in a Mission, Strategy or Tactic. Qualitative words that do not name the end state are acceptable. | 8.4, p. 38 |
| BMM-QUAL-006 | should | An Influencer is stated neutrally and factually, with no qualitative words. A statement that carries them is really an Assessment. | 8.5, p. 38 |
| BMM-QUAL-007 | should | If a Business Rule can be derived directly from a statement, the statement is almost certainly not an Influencer; it is probably a Business Policy. | 8.5.1, p. 39 |
| BMM-QUAL-008 | should | An Influencer is described, not only named. | 8.5.1 |
| BMM-QUAL-009 | should | Avoid a Business Policy that only restates a Strategy in a trivial way. | 8.3.10, p. 35 |

## GUID: Guidance and scope

| Id | Strength | Rule | Section |
|---|---|---|---|
| BMM-GUID-001 | note | Directives that are not stated cannot be addressed by the model; to count, a Directive is explicit and recorded officially. | 8.3.6, p. 31 |
| BMM-GUID-002 | note | Strategies generally pair with Goals and Tactics with Objectives, but the standard does not enforce the pairing. An enterprise that wants it adds its own constraint. | 8.2.3 footnote 1; 7.3.3 |
| BMM-GUID-003 | note | The line between Strategy and Tactic is the enterprise's own; a Course of Action may move from one to the other over time. | 7.3.3; 8.2.3; 8.3.3.1 |
| BMM-GUID-004 | should | When several Assessments attach to one End or Means, evaluate their combined impact to expose trade-offs between Risks and Potential Rewards. | 8.5.7.1 |
| BMM-GUID-005 | note | Business Process, Organization Unit, Asset and Liability instances are references to things maintained elsewhere. Record only those relevant to governance decisions; a complete structure of assets is not required. | 8.6; 8.6.3 |
| BMM-GUID-006 | note | Keeping the three decompositions (of Desired Results, Courses of Action and Business Policies) in step with each other is left to methodology and tools. | 7.2.5 |
| BMM-GUID-007 | note | Recording who defined an End, who established a Means, who recognized an Influencer and who made an Assessment, and when, is recommended as an audit trail but cannot always be required. | 8.2; 8.3; 8.5.1; 8.5.6 |
| BMM-GUID-008 | note | Using a Vision or a Mission is optional; an enterprise can use the model without either. | 7.3.1; 7.3.2 |
| BMM-GUID-009 | note | The model should be traceable in both directions: forward from an Influencer's impact to the processes, rules and responsibilities it leads to, and backward from a process or rule to the reason it exists. | 7.2.3; 7.4 |

Total: 39 rules.
