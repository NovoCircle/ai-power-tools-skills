# The Business Motivation Model 1.3, section by section

This is a summary of the OMG specification in our own words. It is not a substitute for the specification, and it does not reproduce its text; the few short quoted phrases are cited. Clause and annex numbers are the specification's. "p." is the printed page number. Where the standard is silent or inconsistent, this file says so rather than filling the gap.

Source: Object Management Group, *Business Motivation Model (BMM)*, version 1.3, formal/15-05-19, April 2015, with the normative machine-readable model dtc/14-11-08 (https://www.omg.org/spec/BMM/1.3/). The model originates with the Business Rules Group.

## 1. What the standard is

**Identity.** BMM is an OMG standard in the Business Modeling domain. Version 1.3 is the current one; 1.0 (2008), 1.1 (2010) and 1.2 (2014) came before it. It was published under a royalty-free, limited intellectual property mode. (Specification front matter and About page.)

**Nature.** BMM is a metamodel: a business vocabulary and a set of fact types for describing the plans and motives of an enterprise. It is a model of the language of business planning, not a way of drawing it. It is neutral about methodology (7.4, 9.4): it says what the concepts are and how they relate, not in what order to work or who should do it.

**The central idea.** Every enterprise action should be traceable to why it exists. The standard organizes that into two halves, *Ends* (what the enterprise wants to be or achieve) and *Means* (what it uses or does), joined by *Influencers* that act on them and *Assessments* that judge how. It must be traceable both ways: forward from an influencer's impact to the processes, rules and responsibilities that follow, and backward from a process or rule to the reason it exists (7.2.3, 7.4).

## 2. Conformance (clause 2)

Conformance means a tool can import and export the standard's normative model in XMI form, following the metamodel. Nothing in the standard addresses what a conforming diagram or user interface should look like, and nothing certifies instance models. The clause cites an earlier document id for the machine-readable model than the one the About page lists as normative; this summary follows the later file (see the notes on gaps at the end).

Annexes A to H are informative. Annex G's category lists are therefore defaults, not requirements.

## 3. How the metamodel is expressed (clause 6)

**6.1 Fact types.** The vocabulary and the relationships are stated in structured English in the style of SBVR (the OMG business vocabulary standard). Each relationship is a fact type, a sentence with two or more participants ("goal amplifies vision"). Unless a fact type carries a necessity clause, it is many-to-many and optional at both ends (6.1, Annex A).

**6.2 Maintenance.** The model was maintained in a UML-based modeling tool. The figures in clauses 7 and 8 are views of that model. Because the figures are images, the vocabulary, the catalog in clause 9 and the machine-readable model are the dependable source of content.

## 4. Overview (clause 7)

**7.2 Principles.** The model has four areas: Ends, Means, Influencers, and Assessments, with a small set of concepts borrowed from other standards. Three decompositions exist, one each for desired results, courses of action and business policies; keeping them consistent with each other is left to methodology and tools (7.2.5). An organization unit can have its own BMM, refined from elements of a higher unit's model (7.2.5).

**7.3 Concepts in brief.** Section 7.3 introduces each concept in a sentence or two (End, Means, Course of Action, Directive, Influencer, Assessment, and the externally defined ones) and gives the vocabulary the later clauses elaborate. In particular it says that a Course of Action may serve more than one Strategy, and that the Strategy/Tactic distinction belongs to the enterprise (7.3.3), that the Directive "acts as" a Regulation as a role (8.3.8), and that Potential Impact can motivate a Directive, a link added in version 1.1 (7.3.6). Vision and Mission are optional (7.3.1, 7.3.2).

**7.4 Using the model.** An informative activity flow shows the dependency order in which the parts are typically filled in: identify influencers, assess their impacts, decide desired results, decide business policies, select courses of action, assign organizational responsibilities, develop business rules, and realize courses of action in business processes. It is an order of dependency, not a required procedure.

## 5. The detailed model (clause 8)

### 8.2 Ends

An End says what the enterprise wants, never how (8.2). The standard recommends, but does not require, recording who defined each End and when, as an audit trail; it adds that this "cannot always be mandated" (8.2).

- **Vision (8.2.1, 8.2.2).** A broad picture of the intended future. It is long term, often compound, possibly not fully reachable, and may be omitted. Goals amplify it. It is too broad to be measured by Objectives directly.
- **Desired Result (8.2.3).** The common kind of Goal and Objective: a state or target the enterprise intends to maintain. A Desired Result can be grouped by stakeholder-chosen Desired Result Categories (8.2.3.1) such as quality, service levels, cost and benefit, or regulatory compliance. The standard supplies none by default.
- **Goal (8.2.4).** A continuing, qualitative state to bring about or sustain, narrow enough that Objectives can quantify it. Goals are not specific in time or measure.
- **Objective (8.2.5).** An attainable, time-targeted, measurable target met in order to achieve a Goal. Time-targeted means it states an absolute or relative time frame. Measurable means it carries explicit criteria for whether it is being met, at minimum a yes-or-no basis. The statement should open with the time target and then give a quantified noun (p. 24 to 25). The standard notes the resemblance to the popular SMART formulation.
- **Decomposition (8.2.6.1).** Desired Results can include more specific ones, but only of the same kind: Goals include Goals, Objectives include Objectives. The "quantifies" relationship is the only link across the two kinds.

Strategies generally pair with Goals and Tactics with Objectives. The standard deliberately does not hard-wire this; an enterprise that wants the strict pairing adds its own constraint (8.2.3, footnote 1).

### 8.3 Means

A Means is anything that can be called on to achieve Ends: a device, capability, regime, technique, restriction, agency, instrument or method. It excludes the tasks that exploit it and who is responsible (8.3). Who established a Means, and when, is a recommended audit trail (8.3).

- **Mission (8.3.2).** The ongoing operating activity that makes the Vision real. Planned by Strategies. Optional. A good Mission statement has three brief parts and nothing more: an action, a product or service, a market or customer (p. 28).
- **Course of Action (7.3.3, 8.3.3).** An approach or plan to configure some aspect of the enterprise (things, processes, locations, people, timing, motivation) to channel effort toward Desired Results. It is action-oriented and is not a Business Process. Its two kinds are Strategy and Tactic.
- **Strategy (8.3.4).** The essential Course of Action for achieving Ends, Goals in particular. Longer term and broader than a Tactic; a component of the plan for the Mission.
- **Tactic (8.3.5).** A Course of Action that details a Strategy. Shorter term and narrower, generally aimed at Objectives. A Tactic can serve more than one Strategy.
- **Directive (8.3.6, 8.3.9).** A Means stated declaratively that defines, constrains or liberates some aspect of the enterprise, and governs Courses of Action. (SBVR calls it an element of guidance.) Every Course of Action should be governed by some Directive; one with none should be examined carefully, and too many Directives can over-constrain (p. 31). Only Directives that are explicit and officially recorded count; unstated ones cannot be addressed by the model.
- **Enforcement level (8.3.7).** Six ordered levels, strictest to loosest: strictly enforced, deferred enforcement, pre-authorized override, post-justified override, override with explanation, guideline. Only behavior-guiding rules need a level; definitional rules are true by definition. A Tactic effects the level. This is the one named concept of the model that has no class, no attribute and no catalog entry; its only formal hook is the relationship "tactic effects enforcement level of business rule".
- **Directive acts as Regulation (8.3.8).** A Directive can play the role of a Regulation, an external order from an authority such as a government body or enterprise management. It remains a Directive; it is not changed into a different thing.
- **Business Policy (8.3.10).** A Directive that controls or guides the enterprise but is not directly enforceable, because it needs interpretation (usually Business Rules) to detect violation. Less structured and often not atomic. It is under the enterprise's control, chosen by an authorized party from alternatives in response to Assessments. A policy that merely restates a Strategy trivially should be avoided (p. 35).
- **Business Rule (8.3.11).** A Directive that is practicable: a person who understands it can look at a situation and decide whether the enterprise complies. Highly structured and atomic, one aspect of governance in the enterprise's standard vocabulary. The definition is adopted from SBVR. A Rule is often, not always, derived from a Policy.
- **Decomposition (8.3.12).** Course of Action inclusion should associate like with like (Strategies with Strategies, Tactics with Tactics); enabling should generally do the same (8.3.12.1, 8.3.12.2). Business Policies include more specific Business Policies (8.3.12.3).

### 8.4 Qualitative words

Words that describe a desired end state (best, fastest, leading-edge, and so on, Table 8.11) belong in Ends and Directives. Their presence in a Mission, Strategy or Tactic signals the statement should be restated as a Desired Result or Directive. Qualitative words that do not name the end state, such as "free shipping", are fine (p. 38).

### 8.5 Influencers and Assessments

- **Influencer (8.5, 8.5.1).** A neutral fact about something that can change, or confirm the absence of change in, how the enterprise uses Means or achieves Ends. It is stated factually with no qualitative words; qualitative words show it is really an Assessment (p. 38). If a Business Rule can be derived directly from the statement, it is almost certainly not an Influencer but a Business Policy (p. 39). Describe Influencers, do not only name them. Record who recognized an Influencer, and when, if possible.
- **Influencer categories (8.5.2).** Influencers belong to the enterprise's own category scheme. Internal and External are built in (the formal model makes them specializations of Influencer). The standard's suggested general set is in Annex G. An Influencer should be placed in at least one general category and classed as internal or external; consistency across several categorizations is left to methodology (Annex G.3).
- **Influencing Organization (8.5.3).** An organization outside the modeled enterprise that is a source of Influencers. An Influencer may have several sources or none. An internal Organization Unit can play this role. Organization Categories group them; the standard supplies none.
- **Regulation (8.5.4).** The one Influencer category defined as a concept of its own, because a Directive can play the role. It is an External Influencer.
- **Assessment (8.5.5, 8.5.6).** A judgment that an Influencer affects how the enterprise uses Means or achieves Ends. It is the link between Influencers and the Ends and Means. Different people or times may judge the same thing differently. If an Assessment relates to both an End and a Means and no direct relationship joins those two, the gap should be considered carefully (8.5.5). Assessments can use other Assessments (8.5.6.1). Assessment Categories (8.5.6.2 to 8.5.6.6) group them; SWOT (Strength, Weakness, Opportunity, Threat) is the suggested default, defined as four instances of the category concept and replaceable by another scheme.
- **Potential Impact (8.5.7).** An evaluation that quantifies or qualifies an aspect of an Assessment. A Risk signals possible loss, injury, disadvantage or destruction (8.5.7.2). A Potential Reward signals probability of gain (8.5.7.3). When several Assessments attach to one End or Means, evaluate the combined impact to see trade-offs (8.5.7.1). An Influencer can lead to a Business Policy only through an Assessment that identifies a Potential Impact (p. 50).

### 8.6 Concepts defined elsewhere

The standard references, and does not define in full, concepts that belong to other standards or to the enterprise's own models. Section 7.3.7 lists three of them (Organization Unit, Business Process, Business Rule), 8.6 lists four (adding Asset), and Figure 7.4 shows five (adding Liability). They are references to things maintained elsewhere; the model needs only those relevant to governance decisions (8.6, 8.6.3).

- **Organization Unit (8.6.1).** A unit of the organization structure: corporation, department, team, role, committee, project. It defines Ends, establishes Means, recognizes Influencers, makes Assessments, and is responsible for processes, assets and liabilities.
- **Business Process (8.6.2).** A flow of activities that carries out work. The BPMN notion of a process is adopted as the placeholder definition. Business Policies govern processes; Business Rules guide them; processes realize Courses of Action.
- **Asset (8.6.3).** Something of value the enterprise owns, as an actual thing, not its accounting value. Two kinds: a Fixed Asset is held long term, maintained and reused (equipment, buildings, patents, brands, skills); a Resource is consumed and replenished (materials, cash, capacity). An Offering is a specification of a product or service the enterprise can supply, and is an intangible Fixed Asset; instances of it, such as finished goods, are Resources. A Liability is a reservation of actual resources to meet commitments, not the accounting sense.

### 8.7 Relationships that connect a concept to itself

Nine relationships join a concept to its own kind (assessment uses assessment, and the broader/narrower or includes/enables pairs for categories, courses of action, desired results and business policies). Each is transitive, and loops are not permitted: a category cannot, directly or through its descendants, categorize its own ancestor. The standard says tools that support BMM "should ensure" these constraints are enforced (p. 58).

## 6. The catalog (clause 9)

- **9.2 Concepts catalog.** Each concept with its definition, notes, general concept and necessity clauses. This is where the formal cardinality rules appear, for example that each Assessment has at least one Potential Impact (p. 59).
- **9.3 Attributes.** The only attributes defined for any concept are `name` and `description`, on the root superclass added so every concept can carry them. The audit-trail data the narrative recommends (who, when) has no attribute, and neither do an Objective's time target or measurement criteria.
- **9.4** Restates the methodology-neutral stance.
- **9.5 Association names** and **9.6 roles.** The 54 relationships, each with a UML-style name and two role names. 9.5 uses the active reading ("goal amplifies vision"); roles are given from each end. The machine-readable model agrees with the catalog on endpoints and roles, with the naming defects listed below.

The formal model has 34 classes and 54 associations. It declares no class abstract. Where the catalog's descriptions of three category concepts say they are a kind of assessment category, the formal model makes them specializations of the common root; this summary follows the formal model.

## 7. Informative annexes

- **Annex A: notation and conventions.** Reproduces the Business Rules Group's original diagram and explains three non-normative conventions, kept neutral of any modeling notation: a box is a core concept; a box inside a box means "is a category of"; a line between two boxes, or a box and itself, is a fact type labeled with verb phrases in both directions so it reads as a sentence. Nesting does not imply exclusivity or completeness, and a line does not imply it is mandatory. A fact type with three or more participants is a box named with a trailing asterisk. A shaded box marks a concept related to but outside the model's scope (pp. 77 and 78). This is the only drawing guidance in the standard. BMM defines no diagram types and no symbols.
- **Annex F: referenced concepts.** Lists the placeholder concepts and where they are defined.
- **Annex G: default categories.** Suggested sets, to be created as instances of the category concepts. Assessment categories: Strength, Weakness, Opportunity, Threat. Influencer categories, usually external: Competitor, Customer, Environment, Partner, Regulation, Supplier, Technology. Usually internal: Assumption, Corporate Value (with explicit and implicit values as narrower categories), Habit, Infrastructure, Issue, Management Prerogative, Resource. Internal and external are built into the model. Table G.1 suggests combinations and is not exhaustive. The annex contains copy errors in some notes.
- **Annexes B, C, D, E.** Metrics (informative), a worked business background, a mapping to a business architecture framework, and history. Not summarized here; none carries normative content.

## 8. Notes on the standard's own inconsistencies

- **Which machine-readable file is normative.** The conformance clause and the catalog cite an earlier id than the About page, which lists dtc/14-11-08 as normative. This summary uses the later file.
- **Multiplicity.** For four relationships the catalog requires at least one participant (an Assessment is made by at least one Organization Unit; an End is defined by at least one; an Assessment judges at least one Influencer; an Assessment identifies at least one Potential Impact) while the formal model writes no bounds, which in the usual UML reading means exactly one, and elsewhere in the same model an unwritten lower bound means optional. The language file records the catalog's "at least one" as a recommendation, not a requirement: breaking it is a warning (BMM-CARD-001 to 004).
- **Spelling of names.** The formal model and the catalog spell some association names differently, and both contain typographical errors. The language file uses the catalog's active-voice name with the typos corrected. One role name in the formal model (the Asset end of "business process manages asset") is wrong; the catalog's is used.
- **Number of externally defined concepts** varies between 7.3.7 (three), 8.6 (four) and Figure 7.4 (five).
- **Internal and external.** The text calls them built-in categories; the formal model makes them subclasses of Influencer; Annex G lists them among the category defaults.
- **Business Rule.** Described as a core Means in 8.3.11 and as an externally referenced concept in 7.3.7 and 8.6.
