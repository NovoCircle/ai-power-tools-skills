---
name: it4it
description: The Open Group IT4IT Standard (the IT4IT Reference Architecture), a vendor-neutral reference model for managing the business of IT and the full lifecycle of Digital Products. Use when someone is modeling or asking about IT4IT, the IT4IT value streams (Evaluate, Explore, Integrate, Deploy, Release, Consume, Operate), the Digital Value Network, functional groups (Plan, Build, Deliver, Run, Supporting Functions), functional components (Policy, Product Portfolio, Pipeline, Order, Change, Incident, Problem, Event and the rest), key data objects (Scope Agreement, Product Backlog Item, Product Release, Service Offer, Subscription, Service Contract, Actual Product Instance, Incident and more), the Digital Product Backbone, the Service Offer Backbone, the system of record fabric, the IT4IT abstraction levels, or how IT4IT relates to ITIL, ArchiMate and Digital Product management.
---

# IT4IT Reference Architecture (The Open Group IT4IT Standard 3.0, read from the public draft)

IT4IT is The Open Group's reference architecture for managing the business of IT and the end-to-end lifecycle of **Digital Products**. It says which **value streams** an organization needs, which **functional components** support them, which **data objects** those components control, and how the data objects relate. It is independent of technology, vendor and process. It is not a drawing notation and not a method: it defines a model and the levels at which that model is described.

**What this skill rests on.** The published standard (version 3.0.1, document C24A, 24 October 2024; version 3.0 is C221, 18 October 2022) needs a sign-in, so the content here comes from The Open Group's public **Snapshot draft of 3.0** (S220, February 2022). Counts and wording may differ in the published text. A newer draft, the 3.1 Snapshot (S261, October 2026), exists and is not covered. Say so when you quote a count. This guide makes no claim of conformance, and it is not affiliated with or endorsed by The Open Group.

## What you are creating

An IT4IT model describes how one organization manages its Digital Products, expressed in the standard's own vocabulary. In practice it contains some or all of:

1. A **value network** of value streams for the Digital Products the organization delivers, with the value streams' stages if needed.
2. The **functional components** the organization has or needs, arranged in functional groups.
3. The **key data objects** each component controls, and the **relationships** among data objects that keep the whole lifecycle traceable (the "system of record fabric").
4. Optional extensions at Levels 4 and 5 (capabilities, essential services, scenarios, implementation detail) that map back to Levels 1 to 3.

The point of the standard is **end-to-end traceability**: from a strategic objective, through a portfolio item, a requirement, a release and a service offer, to a running instance, an incident and the fix that returns to the backlog.

## Views: the five abstraction levels

IT4IT has no named diagram types. It describes the same model at five levels of abstraction. Levels 1 to 3 are standardized, Levels 4 and 5 are not. The standard draws these levels in its own simplified notation and in the ArchiMate language, and says the two translate into each other.

| Level | What it shows | Admits |
|---|---|---|
| **1 End-to-end overview** | Value streams, functional groups, functional components and key data objects, with the Digital Product and Service Offer backbones | Value Network, Value Stream, Functional Group, Functional Component, Key and Backbone Data Object, Data Relationship |
| **2 Value stream documentation** | For each value stream: scenarios, stages, example stakeholders, participating data objects with their components | Value Stream, Scenario, Value Stream Stage, Stakeholder, Data Object, Functional Component and Group |
| **3 Vendor-independent architecture** | Per functional group and per component: data objects with key attributes, relationships with cardinality, and data flows | Functional Group, Functional Component, Data Object, Data Relationship, System of Record and Engagement integrations |
| 4 Vendor and integrator extensions (not standardized) | Capabilities, essential services, scenarios and processes, added by vendors | Capability, Essential Service, Scenario, plus anything mappable to Levels 1 to 3 |
| 5 Implementation architecture (not standardized) | A real current or future implementation | Anything in the ArchiMate language |

## The concepts

**Level 1.**

- **Value Network**: the relationships across the value-creating functions of a digital business; replaces the older value chain, in which activities only passed work along.
- **Value Stream**: key value-creating activities for one area, where net value is added to the Digital Product. There are seven, named with a verb.
- **Functional Group**: a grouping of components and data objects. Five at Level 1 (Plan, Build, Deliver, Run, Supporting Functions) and fourteen at Level 2. A grouping only; it is not a capability model.
- **Functional Component**: the smallest self-standing unit of technology useful to a digital practitioner. It has data object inputs and outputs and affects the key data object it controls. Named with a noun.
- **Lifecycle Data Object** and **Key Data Object**: data that models an aspect of a Digital Product. Only key data objects, those needed for traceability, are in scope. One data object has exactly one controlling component.
- **Backbone Data Object**: a key data object that belongs to the **Digital Product Backbone** (Digital Product, Product Design, Product Release, Desired Product Instance, Actual Product Instance) or the **Service Offer Backbone** (Service Offer, Subscription, Chargeback Contract, Service Contract).
- **Data Relationship** and **System of Record**: the essential links among data objects, and the authoritative data they form.

**Level 2.** **Scenario** (a situation that triggers a value stream), **Value Stream Stage** (a refinement with entrance and exit criteria, activities, example stakeholders and participating data objects), **Stakeholder** (a proposed persona or role, never a requirement).

**Level 3.** **Key Attribute** (the vendor-independent minimum), **Data Flow**, **System of Record Integration** (keeps a relationship between two data objects consistent) and **Engagement Integration** (guidance).

**Level 4.** **Capability**, **Essential Service** and **Process** (non-normative).

**Digital Product concepts (chapter 4).** **Digital Product**, **Service Offer**, **Service Contract**, **System** and **Digital Product Instance**.

### The reference model the standard specifies (per the Snapshot)

| Group | Functional components (data objects each controls) |
|---|---|
| **Plan: Strategy** | Policy (Policy); Strategy (Strategic Theme, Strategic Objective); Enterprise Architecture (Architecture Roadmap Item, Architecture Blueprint, Value Stream) |
| **Plan: Portfolio** | Portfolio Backlog (Portfolio Backlog Item); Proposal (Scope Agreement); Product Portfolio (Digital Product) |
| **Build: Develop** | Product Backlog (Product Backlog Item); Requirement; Product Design; Source Control (Source); Pipeline; Build Package; Release Composition (Product Release, Product Release Blueprint) |
| **Build: Test** | Test (Test Case, Test Plan); Defect |
| **Deliver: Consume** | Consumption Experience (Interaction); Identity (Identity, Entitlement); Offer (Service Offer Catalog, Service Offer); Order (Order, Subscription); Chargeback (Chargeback Contract, Chargeback Record) |
| **Deliver: Fulfill** | Change; Fulfillment Orchestration (Desired Product Instance); Resource; Fulfillment (Fulfillment Book); Usage (Usage Record) |
| **Run: Support** | Service Level (Service Contract, KPI); Incident; Problem; Knowledge (Knowledge Item) |
| **Run: Assure** | Configuration (Actual Product Instance); Monitoring (Service Monitor, Log); Event; Diagnostics & Remediation (Runbook) |
| Supporting: Financial Management | Cost Modeling (Cost Model); Investment (Budget Item) |
| Supporting: five more functions | Governance Risk & Compliance; Workforce Management; Sourcing & Vendor Management; Intelligence & Reporting; Collaboration & Communication. Described, not defined with components or attributes. |

That is **35 components and 46 data objects** (Appendix A). The Snapshot's chapter 3 says 33 and 44; the difference is the four Financial Management items.

**The seven value streams** (each with 3 to 5 stages and 3 to 5 scenarios): **Evaluate** (portfolio assessment against strategy), **Explore** (feature and direction exploration for a product), **Integrate** (design, build and test a Product Release), **Deploy** (install, update or remove a release in production), **Release** (make Service Offers available), **Consume** (select, order, support and report on a service as a consumer), **Operate** (keep instances within their Service Contract). Evaluate depends on all the others; the full dependency lists, stages and the data objects each stage uses are in `language.yaml` (`reference_model.value_streams`).

## Relationship rules in summary

- Each data object section lists the **key relationships** it "shall maintain". There are **114 data relationships** in the reference model (`reference_model.data_relationships`). Only these are defined; others may exist locally but are outside the standard.
- **Cardinality has three forms**: `1:1`, `1:n` and `n:m`, written "A to B (x:y)". Each means "can relate". The standard never says a relationship **must** exist and does not use UML multiplicity. "Incident to Change (1:n)" means one incident can relate to several changes and a change to only one incident.
- Twenty relationships are stated with **different cardinalities at their two ends** (for example Service Offer to Subscription). The language file records the first-stated direction and flags the conflict. Treat those as unsettled.
- Twenty relationships appear in only one data object's section.
- The standard says this version defines **no reflexive relationships**, yet lists some (for example Digital Product to Digital Product, Change to Change). Treat them as intended but unspecified.
- The link between a **Service Offer** and a **Product Release** goes through the **Product Release Blueprint**.
- Data flows between components are of two kinds: **system of record integrations** (keep related data objects consistent) and **engagement integrations** (guidance). A data flow becomes a system of record integration only if it creates a relationship between the two data objects, the objects have a direct relationship to keep, and their lifecycles are interlocked. The individual flows are in the standard's figures, not in its text.

## Data types and attributes

The standard defines no data types, lengths, or lists of values. What it does define is the **key attribute**: each of the 46 data objects lists the attributes it shall have, 292 in all, each with a name and a short description. A key attribute need not have a value on every instance, and Anticipated Business Value on Scope Agreement is the only one marked optional. The names are in `language.yaml` under `reference_model.data_objects[].key_attributes`, and `data_types` records the coverage.

## How it is drawn

The standard gives two forms and says they translate directly: a **simplified notation** and an **ArchiMate** form. It states no duty to use either. In the simplified form, a value stream is a blue block arrow, a functional group a blue rounded rectangle, and a primary component a blue rectangle (gray if secondary). A key data object is a black circle, and a backbone data object is an orange circle. A data object sits inside the component that controls it, and a data relationship is a solid line with no cardinality drawn. Data flows run between components as dotted lines with a solid arrowhead: black for a system of record integration and blue for an engagement integration. `language.yaml` under `notation` has every concept and relationship, with its figure, and lists the ones the standard gives no drawing for. Sizes and spacing come from `../_languages/layout-standard.yaml`, and the concept mapping from `layout` in `language.yaml`.

## The rules that matter most

The 149 rules in `references/rules.md` are graded must, should or note. The ones to apply first:

1. A **functional component** must have data object inputs and outputs and must affect a key data object it controls. (IT4IT-DEF-001)
2. A **data object** can be controlled by only one functional component. (IT4IT-DEF-003)
3. Every data object supports the **key attributes** the standard lists; a unique identifier is always among them. (IT4IT-ATTR-001) A key attribute need not have a value on every instance.
4. Data objects maintain the **key relationships** listed for them, using only the three cardinalities. (IT4IT-REL-001, IT4IT-REL-002)
5. A **Digital Product** must include at least one **Service Offer** defining its Service Contract options, and must provide human or machine interfaces. (IT4IT-DEF-014, IT4IT-DEF-015) A Service Offer must carry every element that will become part of the contract (IT4IT-DEF-017).
6. **Value stream stages are not a sequence** and value streams are not process descriptions. (IT4IT-DEF-006)
7. **Naming:** value streams and groups are verbs, components and data objects are nouns, and attribute names do not repeat the object name. (IT4IT-NAME-001 to 005)
8. A system of record integration needs **three conditions** together. (IT4IT-REL-007)
9. Anything added at **Levels 4 and 5** must map back to Levels 1 to 3 and should not change them. (IT4IT-MM-003, IT4IT-MM-004)
10. Each component's **functional criteria** ("shall be the system of record for X", and so on) describe what a system playing the component supplies; they are not model content. (IT4IT-CRIT)

## Illustration: Westbrook Bank

Westbrook Bank is a fictitious reference organization. Substitute the real organization's own products, value streams and components when you model a real one.

Westbrook Bank manages **Westbrook Mobile Banking** as a market-facing Digital Product. The traceability chain a model should be able to follow:

| Step | Data object | Example |
|---|---|---|
| Strategy | Strategic Theme to Strategic Objective (n:m) | Theme "Digital-first retail banking"; objective "Open a checking account in the mobile app in under ten minutes" |
| Policy | Policy to Digital Product (n:m) | "Customer Data Retention Policy" applies to Westbrook Mobile Banking |
| Portfolio | Strategic Objective to Portfolio Backlog Item (n:m); Portfolio Backlog Item to Scope Agreement (1:1) | "Instant account opening" with its Scope Agreement and an approved budget |
| Backlog | Portfolio Backlog Item to Product Backlog Item (1:n) | Epic, then features and stories |
| Requirement and test | Product Backlog Item to Requirement (n:m); Requirement to Test Case (1:n) | "Identity checks complete in 30 seconds" with its Test Case |
| Release | Product Design to Product Release (1:n); Pipeline to Build Package (1:n); Product Release to Product Release Blueprint | Release 4.2, built by the release pipeline, with its Blueprint |
| Offer | Product Release Blueprint to Service Offer; Service Offer Catalog to Service Offer (n:m) | Offer "Mobile Banking, Personal" in the "Retail Digital Catalog" |
| Consumption | Service Offer to Order (1:n); Order to Subscription (n:m); Subscription to Service Contract (1:1) | A customer orders the offer; a Subscription and a Service Contract (99.9 percent availability, a KPI named Availability) follow |
| Deployment | Product Release to Desired Product Instance (1:n); Desired Product Instance to Actual Product Instance (1:1) | The production instance realized from release 4.2 |
| Operations | Event to Incident (n:m); Incident to Problem (n:m); Problem to Defect (1:n); Defect to Product Backlog Item | A latency event raises an incident; a problem finds the cause; a defect returns to the backlog |

Value streams touched: Evaluate and Explore plan it, Integrate builds it, Deploy and Release put it in production and in the catalog, Consume handles the customer's order, Operate keeps it running.

## Where to go next

- `references/standard.md`: the standard summarized section by section, in our own words, with the data objects, key attributes and relationships of each functional component.
- `references/rules.md`: the 149 rules, each with an id, strength and section.
- `language.yaml`: the machine-readable facts: concepts, metamodel relationships, the reference model (value streams, stages, groups, components, 46 data objects with key attributes, 114 data relationships), the constraints and the views.
