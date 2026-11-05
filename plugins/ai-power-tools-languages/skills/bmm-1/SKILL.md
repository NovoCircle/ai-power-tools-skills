---
name: bmm-1
description: The OMG Business Motivation Model (BMM) 1.3, a standard vocabulary for describing why an enterprise does what it does - its ends (vision, goals, objectives), its means (mission, strategies, tactics, business policies, business rules), the influencers that act on it, and the assessments (SWOT-style strengths, weaknesses, opportunities, threats) that connect the two. Use when someone is modeling business motivation, strategy or strategic plans, goals and objectives, ends and means, courses of action, directives, business policies and business rules, regulations and other influencers, or SWOT and risk assessments, or when they ask what BMM, the Business Rules Group motivation model, or a motivation model allows.
---

# Business Motivation Model (BMM) 1.3

BMM is the Object Management Group's standard for describing the reasons behind what an enterprise does. It is a vocabulary plus a set of facts that connect the words. It is not a method and it is not a drawing notation.

**BMM defines no diagram types and no symbols.** Its only statement about drawing is an informative annex with three non-normative conventions (a box for a concept, a box inside a box for "is a category of", a labeled line for a fact that relates two concepts). Anything beyond that, such as shapes, colors or named diagram kinds, belongs to whatever tool draws the model, not to the standard.

## What you are creating

A BMM model answers a chain of questions for one enterprise or one part of it:

1. What is going on around and inside the enterprise? (Influencers)
2. What do we conclude from that? (Assessments)
3. What do we want to achieve? (Ends)
4. What will we do about it, and under what governance? (Means)

Everything in the model is an element with a name and a description, and the standard defines nothing else about an element. Record the people and dates behind an element (who defined it, who assessed it, when) if you can; the standard recommends it as an audit trail but does not require it.

## The concepts, in plain words

The standard has 33 concepts. The spelling below is how the standard writes the names in its model (no spaces); the readable form is in `language.yaml`.

### Ends - what the enterprise wants

- **End**: something the enterprise wants to accomplish. It says what, not how.
- **Vision**: the overall picture of the future the enterprise wants. Long term, often broad, possibly unreachable. Optional.
- **DesiredResult**: a more specific End, a state or target the enterprise intends to maintain. It is either a Goal or an Objective.
- **Goal**: a continuing, qualitative state or condition to bring about or sustain. It amplifies a Vision and is narrow enough for Objectives to quantify.
- **Objective**: an attainable, time-targeted, measurable target met in order to achieve a Goal.
- **DesiredResultCategory**: a category the stakeholders choose for grouping Desired Results (for example service levels or regulatory compliance). The standard supplies none.

### Means - what the enterprise does about it

- **Means**: anything that can be called on to achieve Ends: a capability, a technique, a restriction, an instrument. It excludes the tasks that use it and who does them.
- **Mission**: the ongoing, day-to-day operating activity that makes the Vision real. Planned by Strategies. Optional.
- **CourseOfAction**: an approach or plan for configuring part of the enterprise to channel effort toward Desired Results. It is either a Strategy or a Tactic. It is not a Business Process.
- **Strategy**: the essential Course of Action for achieving Ends, Goals in particular. Longer term and broader.
- **Tactic**: a Course of Action that details a Strategy. Shorter term and narrower; generally aimed at Objectives.
- **Directive**: a declarative statement that defines, constrains or liberates some part of the enterprise and governs Courses of Action. It is either a Business Policy or a Business Rule.
- **BusinessPolicy**: a Directive that guides the enterprise but cannot be enforced directly, because it needs interpretation (usually through Business Rules) to tell whether it is being followed.
- **BusinessRule**: a Directive that is practicable: a person who understands it can look at a situation and decide whether the enterprise complies. Atomic and precisely worded.

### Influencers - what acts on the enterprise

- **Influencer**: a neutral fact about something that can change how the enterprise uses Means or reaches Ends.
- **InternalInfluencer** and **ExternalInfluencer**: an Influencer from inside, or outside, the enterprise's boundaries. An Influencer is classed as internal or external either by one of these subclasses or by being placed in an internal or external Influencer Category.
- **Regulation**: an External Influencer that is an order from an authority. A Directive can play the role of a Regulation.
- **InfluencerCategory**: a category of Influencer. The standard suggests defaults such as Competitor, Customer, Partner, Supplier, Technology, Assumption, Corporate Value, Habit, Issue and Infrastructure.
- **InfluencingOrganization**: an organization that is a source of Influencers. An internal Organization Unit can play it.
- **OrganizationCategory**: a category of Influencing Organization. The standard supplies none.

### Assessments - what the enterprise concludes

- **Assessment**: a judgment that an Influencer affects how the enterprise uses Means or achieves Ends. Different people or times can assess the same thing differently.
- **AssessmentCategory**: a category of Assessment. The standard suggests SWOT: Strength, Weakness, Opportunity, Threat. These are four instances of the concept, not four concepts.
- **PotentialImpact**: an evaluation that quantifies or qualifies some aspect of an Assessment. It is either a Risk or a PotentialReward.
- **Risk**: a Potential Impact that signals possible loss or harm.
- **PotentialReward**: a Potential Impact that signals possible gain.

### Placeholders - defined elsewhere, referenced here

The standard names seven concepts that other standards or the enterprise's own models define in full. Include only those that matter to a governance decision; the standard does not ask for a complete asset or organization structure.

- **OrganizationUnit**: a unit in the organization structure (department, team, role, committee, project).
- **BusinessProcess**: a flow of activities that does work.
- **Asset**, **FixedAsset**, **Resource**, **Offering**: something of value the enterprise owns. A Fixed Asset is kept and reused (equipment, brands, skills). A Resource is consumed and replenished (cash, materials, capacity). An Offering is a specification of a product or service, a kind of Fixed Asset.
- **Liability**: a reservation of actual resources to meet commitments.

### Specialization

Vision, DesiredResult specialize End; Goal, Objective specialize DesiredResult. Mission, CourseOfAction, Directive specialize Means; Strategy, Tactic specialize CourseOfAction; BusinessPolicy, BusinessRule specialize Directive. InternalInfluencer, ExternalInfluencer specialize Influencer; Regulation specializes ExternalInfluencer. Risk, PotentialReward specialize PotentialImpact. FixedAsset, Resource specialize Asset; Offering specializes FixedAsset. A relationship on a general concept applies to everything below it. A bare End, Means or Directive is allowed: the standard declares no concept abstract, so no concept is flagged merely for being general.

## Relationships

The standard defines 54 relationships (listed fully, with the roles at each end and the multiplicity, in `language.yaml`). Read each as a sentence from source to target. Unless a rule says otherwise, every relationship is many-to-many and optional at both ends. In summary:

- **Ends**: a Goal amplifies a Vision (at most one); an Objective quantifies a Goal; a Mission makes a Vision operative (at most one); Desired Results include more specific Desired Results of the same kind; Desired Result Categories categorize Desired Results.
- **Means**: a Strategy is a component of the plan for a Mission; a Tactic implements a Strategy; a Course of Action channels efforts toward a Desired Result; a Directive governs a Course of Action and supports achievement of a Desired Result; a Course of Action is formulated based on a Directive; Courses of Action include and enable one another; a Business Policy is the basis for a Business Rule; Business Policies include more specific ones; a Tactic effects the enforcement level of a Business Rule; a Directive acts as a Regulation.
- **Influencers and assessments**: an Assessment judges an Influencer, affects an End or a Means, identifies a Potential Impact, provides impetus for a Directive (as does a Potential Impact), and may use another Assessment; categories categorize their members and nest as broader and narrower; an Influencing Organization is a source of an Influencer.
- **Organization**: an Organization Unit defines an End, establishes a Means, makes an Assessment, recognizes an Influencer, acts as an Influencing Organization (at most one unit per organization), and is responsible for Business Processes, Assets and Liabilities; a Strategy determines Organization Units.
- **Realization and resources**: a Business Process realizes a Course of Action, delivers an Offering and manages an Asset; a Course of Action deploys an Asset, defines an Offering and discharges a Liability; a Business Policy governs, and a Business Rule guides, a Business Process; a Directive governs use of an Asset; a Fixed Asset provides a Resource; a Liability claims a Resource; an Offering requires a Resource and uses a Fixed Asset.

## The rules that matter most

The full list, 39 rules with ids, is in `references/rules.md`. The ones to keep in front of you:

- Every Assessment judges at least one Influencer, affects at least one End or Means, identifies at least one Potential Impact, and is made by at least one Organization Unit. Every End is defined by at least one Organization Unit. The standard states these only in its prose, so a model that breaks one gets a warning, not an error. (BMM-CARD-001 to 004)
- A Goal amplifies at most one Vision; a Mission makes at most one Vision operative. (BMM-CARD-005, 006)
- An Objective is attainable, time-targeted and measurable, with explicit criteria. (BMM-QUAL-001)
- Goals include only Goals and Objectives only Objectives; only "quantifies" joins the two. (BMM-HIER-001)
- Relationships that connect a concept to its own kind are transitive and may not loop. (BMM-HIER-002)
- A Business Rule is practicable and atomic; a Business Policy is not directly enforceable. (BMM-DEF-002)
- An Influencer leads to a Business Policy only through an Assessment that identifies a Potential Impact. (BMM-REL-004)
- Every Course of Action should be governed by some Directive. (BMM-REL-002)
- An Influencer is stated neutrally; qualitative words mean it is really an Assessment. (BMM-QUAL-006)

## Telling similar concepts apart

- **Goal or Objective.** A Goal is qualitative and continuing ("small businesses find opening an account easy"). An Objective is the same intent made measurable and dated ("95 percent of complete applications opened within one business day by the end of next year"). If you cannot say when and how you will know, it is a Goal. If it has a deadline and a number, it is an Objective.
- **Strategy or Tactic.** A Strategy is the broad, longer-term approach; a Tactic is a narrower, shorter-term step that implements it. Strategies generally serve Goals and Tactics serve Objectives, but the standard does not enforce the pairing, and where the line falls is the enterprise's own call.
- **Business Policy or Business Rule.** Ask whether a person can look at a situation and say, directly, "we comply" or "we do not". If yes it is a Business Rule. If it needs interpreting first it is a Business Policy, and the rules that interpret it are derived from it.
- **End or Means.** An End says what the enterprise wants to be or achieve. A Means says what it uses or does. A Course of Action is a Means; a Desired Result is an End.
- **Influencer or Assessment.** An Influencer is a neutral fact. An Assessment is a judgment about what that fact means for Ends or Means. "A competitor offers same-day account opening" is an Influencer; "this threatens our deposit growth" is an Assessment.
- **Mission or Strategy.** A Mission is what the enterprise does every day, in three parts: an action, a product or service, a market. Strategies are the plans that make the Mission happen.
- **Course of Action or Business Process.** A Course of Action is a plan for how to configure the enterprise. A Business Process is the work that carries it out. They are different concepts, joined by "realizes".

## A short example

Westbrook Bank, a fictitious bank, looks at its small-business customers.

An Influencer states: "A regional credit union now opens business accounts the same day." It is external, categorized as Competitor, and recognized by the Retail Banking Organization Unit. An Assessment, categorized as Threat, judges it: "Small-business deposits may move to the credit union." The Assessment identifies a Risk, "Loss of small-business deposits", and provides impetus for a Business Policy.

The Ends: the Vision is "The bank small businesses trust for everyday banking." A Goal amplifies it: "Opening and using a business account is fast and dependable." An Objective quantifies the Goal: "Within 12 months, 95 percent of complete business account applications are opened within one business day."

The Means: the Mission is "Provide business accounts and payment services to small businesses." A Strategy, "Make business account opening digital from application to first use", is a component of the plan for the Mission and channels efforts toward the Goal. A Tactic, "Verify identity during the online application instead of at a branch", implements the Strategy and is aimed at the Objective. The Business Policy "Westbrook Bank verifies the identity of every business customer before an account is opened" governs the Strategy and is the basis for the Business Rule "An account may be opened only when the identity check status is verified". A Tactic effects the Rule's enforcement level.

This is an illustration. Use your own enterprise's elements, and your own category scheme where the standard leaves it open.

## Data types and attributes

The standard defines no data types (coverage: none). Its only attributes are `name` and `description`, which every concept carries through a common superclass (9.3); it states no type or multiplicity for either. Anything else you record about an element, such as who defined it, when, an Objective's time target or its measuring criteria, has no attribute in the standard. `language.yaml` lists the two attributes under each concept, in `data_types`.

## How it is drawn

The standard defines no diagram types and no symbols. Its informative Annex A gives three non-normative conventions (coverage: informative): a box is a concept, a box inside a box means "is a category of", and a line between two boxes is a relationship, labeled with a verb phrase in each direction so it reads as a sentence. Annex A adds two marks: an asterisk after the name of a box that stands for a relationship with three or more participants, and a shaded box for a concept outside the model's scope. It gives no shape, color or layout for any individual concept or relationship, so a tool that draws BMM chooses its own and should not present it as the standard's. See `notation` in `language.yaml`. Sizes and spacing come from `../_languages/layout-standard.yaml`, and the mapping from each concept to an element type comes from `layout` in `language.yaml`.

## References

- `references/standard.md`: the standard section by section, in our own words, with citations.
- `references/rules.md`: all 39 rules with stable ids (`BMM-<CAT>-nnn`), strength and source section.
- `language.yaml`: the machine-readable form: concepts, the 54 relationships with roles and multiplicity, and the rules.
