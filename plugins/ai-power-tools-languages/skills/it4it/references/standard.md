# IT4IT Standard 3.0, read from the public draft, section by section

This is a summary of The Open Group's IT4IT Standard in our own words. It is not a substitute for the standard, and it does not reproduce its text; the few short quoted phrases are cited. Clause numbers are those of the standard's text. Where the standard is silent or inconsistent, this file says so rather than filling the gap.

Source: The Open Group, *IT4IT Standard, Version 3.0.1: A Reference Architecture for Managing Digital*, document C24A, published 24 October 2024 (https://publications.opengroup.org/c24a), which supersedes version 3.0 (C221, 18 October 2022). **The text summarized here is the public Snapshot draft of version 3.0 (document S220, February 2022; https://pubs.opengroup.org/it4it/3.0/snapshot/), because the published 3.0 and 3.0.1 texts require a sign-in.** Wording, counts and figure content in the published text may differ. A newer draft, the 3.1 Snapshot (S261, 12 October 2026), exists and was not read. Section numbers below are the Snapshot's. This summary makes no claim of conformance.

## 1. What the standard is

IT4IT is a reference architecture for managing the business of information technology and the full lifecycle of **Digital Products**, from investment decision to end of life. It prescribes a target architecture: a set of **value streams**, the **functional components** that support them, and the **data objects** those components control, with the relationships among the data objects. It is independent of technology, vendor, organization structure, process model and methodology. Its stated purpose is to shift the focus of digital investment from projects to products and to give organizations a common structure that frameworks such as ITIL, COBIT and SAFe can sit on.

It is a **formal standard** of The Open Group, produced by the IT4IT Forum. It is not a notation and not a method. It describes its model in the ArchiMate language and also ships a simplified notation for readers who do not know ArchiMate (chapter 11).

## 2. Conformance and terms (clause 1)

The Snapshot says it is a draft and that conformance must not be claimed to it (1.3). The published editions' conformance clause was not read. The standard uses "shall" for requirements, "should" for recommendations, "may" for options, "can" for possible behaviors, and treats "will" as "shall" (1.5). Normative references: the ArchiMate 3.1 specification and its model exchange format (1.4).

## 3. Digital Management (chapter 3): Level 1

Chapter 3 is the overview and defines **Level 1** of the abstraction levels (section 11 below).

- **Functional groups.** Four groups of functions deliver the end-to-end outcome: **Plan** (formerly Strategy to Portfolio), **Build** (formerly Requirement to Deploy), **Deliver** (formerly Request to Fulfill) and **Run** (formerly Detect to Correct). A fifth, **Supporting Functions**, is defined only by the minimum other functions must supply (3.1).
- **Digital Value Network.** The standard moves from Porter's value chain to a value network: value is created through complex interaction among many systems and organizations, so supporting capabilities, business partners, vendors and regulators all take part (3.2).
- **Seven value streams.** Evaluate, Explore, Integrate, Deploy, Release, Consume and Operate. A value stream is a sequence of activities that creates a result for a customer, stakeholder or end user, and links directly to the organization's business model (3.3).
- **Functional components and the data model.** The four groups decompose into eight functional groups, populated by functional components that control key data objects. The text's summary says 33 components and 44 key data objects; Appendix A lists 35 and 46 (the difference is the Financial Management components, see section 10 below) (3.4).

## 4. Digital Product (chapter 4)

The chapter defines the single entity that runs through every value stream.

**Definition.** A Digital Product is a service, physical item or digital item that gives a consumer an agreed outcome; incorporates and needs software to do so; is expected to need active management of the software and its resources over a lifecycle in the way its provider prescribes; and is described by a formal offer exchanged for an explicit price (4.4). Its criteria: it must include one or more Service Offers that define Service Contract options; it may be delivered as an instance; it may be consumed inside or outside the organization; it may depend on, or be made of, other Digital Products; and it must provide human or machine interfaces.

**Parts.** The *system* is the technology the provider manages (software, compute, networking, supporting resources, recursively). The *Service Offer* describes possible contract terms from the consumer's side and must hold every element that would become part of the contract. When a consumer accepts an offer an *instance* is created and a *Service Contract* records the relationship, including warranties and service levels, usage and financial rules, audit rights and lifecycle commitments. A *price* need not relate to cost, but a product manager should be able to explain return on investment over the lifecycle (4.4.1 to 4.4.4).

**From service to product.** In version 2.1 the managed entity was the IT Service and its Service System; here it is the Digital Product and its System, covering digital and not labor-based services (4.5).

**Granularity and dependency.** A product may be composed of, or depend on, other products; internal products benefit from the same formalism as external ones: objective financial insight, comparable options and long-term planning (4.7, 4.8). Examples are websites, mobile applications, operational technology, smart devices, digital platforms (4.6).

**Management.** Portfolios have three perspectives: market-facing, internal-facing and foundational (4.9). The Digital Product Manager combines technology competence with product-management competence (4.10). Two lifecycle concerns apply: the system lifecycle and the contract lifecycle; the system should not be retired before contract obligations end, and end-of-life must be handled with recourse for consumers (4.12, 4.15). Code, dependencies and instance resources must be managed until no active consumers remain (4.13), and data governance, including retention and privacy, applies throughout (4.14). Consumers may be internal or external, human or machine, and the Service Offer should define the interaction methods for each (4.18). Product instances can be linked to configuration records through foreign keys to the Subscription record (4.19).

## 5. Value streams (chapter 5): Level 2

Each value stream is documented by an overview, its key stakeholder, the value it delivers, its dependencies on the other value streams, scenarios (situations that trigger it) and stages. Each stage lists entrance and exit criteria, a value item, activities (with shall, should and may), example stakeholders and the data objects that take part, each with the component that controls it. The stages are explicitly not a sequence (11.8.1).


### 5.1 Evaluate value stream

Continuous assessment of the whole Digital Product Portfolio to align it with business strategy and find new product opportunities. Key stakeholder: Product Portfolio Manager. Value: Optimized product portfolio and a portfolio investment plan with funding.

- **Depends on:** Explore, Integrate, Deploy, Release, Consume, Operate.
- **Scenarios (4):** Consider a New Digital Product; Perform Digital Product Governance; Rationalize the Product Portfolio; Plan Product Portfolio Investments.
- **Stages (5), with participating data objects:**
  - Gather Influencers: Policy, Strategic Objective, Strategic Theme.
  - Identify Gaps: Digital Product, Policy, Product Backlog Item, Scope Agreement, Strategic Objective, Strategic Theme, Value Stream.
  - Propose Investments: Budget Item, Digital Product, Policy, Portfolio Backlog Item, Scope Agreement, Strategic Objective, Strategic Theme, Value Stream.
  - Define Backlog Mandates: Architecture Blueprint, Architecture Roadmap Item, Digital Product, Policy, Portfolio Backlog Item, Product Backlog Item, Scope Agreement, Strategic Objective, Strategic Theme, Value Stream.
  - Ensure Governance: Digital Product, Policy, Portfolio Backlog Item, Scope Agreement, Strategic Objective, Strategic Theme, Value Stream.

### 5.2 Explore value stream

Continuous exploration of new features and directions for a Digital Product, working from the Scope Agreements Evaluate produces. Key stakeholder: Product Manager. Value: Accepted, planned product backlog with a detailed Scope Agreement, release roadmap and resources.

- **Depends on:** Evaluate, Integrate.
- **Scenarios (4):** Investigate a New Digital Product Idea; Optimize a Digital Product; Refine Digital Product Feasibility; Retire Digital Product.
- **Stages (4), with participating data objects:**
  - Prioritize Backlog Items: Digital Product, Policy, Portfolio Backlog Item, Scope Agreement, Strategic Objective, Strategic Theme.
  - Define Digital Product Architecture: Architecture Blueprint, Policy, Portfolio Backlog Item, Product Design, Strategic Objective, Strategic Theme.
  - Refine Product Backlog: Architecture Blueprint, Architecture Roadmap Item, Digital Product, Policy, Portfolio Backlog Item, Product Backlog Item, Product Design, Requirement, Scope Agreement.
  - Finalize Roadmap & Scope Agreement: Architecture Roadmap Item, Digital Product, Policy, Portfolio Backlog Item, Product Backlog Item, Product Design, Scope Agreement.

### 5.3 Integrate value stream

Designs, builds and tests a new Product Release in non-production environments and makes it ready to deploy. Key stakeholder: Product Manager with the Development Teams. Value: A new Product Release accepted and ready for deployment and release.

- **Depends on:** Explore, Consume, Deploy, Operate.
- **Scenarios (4):** Develop a New or Initial Product Release; Configure an Off-the-Shelf or SaaS Product for Use; Deliver an Emergency Change or Hotfix; Update of a Vendor Product.
- **Stages (4), with participating data objects:**
  - Plan Product Release: Defect, Policy, Portfolio Backlog Item, Problem, Product Backlog Item, Requirement, Scope Agreement, Test Plan.
  - Design & Develop: Defect, Policy, Product Backlog Item, Product Design, Requirement, Source, Test Case, Test Plan.
  - Build, Integrate, & Test: Build Package, Fulfillment Book, Pipeline, Product Release, Requirement, Source, Test Case, Test Plan.
  - Accept & Publish Release: Defect, Desired Product Instance, Fulfillment Book, Log, Order, Product Backlog Item, Product Release, Requirement, Scope Agreement, Subscription, Test Case, Test Plan.

### 5.4 Deploy value stream

Installs, updates or removes a Product Release in the production environment. Key stakeholder: Product Manager. Value: Product Releases are installed safely without unexpected outages of running instances.

- **Depends on:** Integrate, Consume.
- **Scenarios (3):** Deploy a First Product Release for a New Digital Product; Deploy a New Product Release Version for a Digital Product; Disable or Remove Existing Product Release Instances of a Digital Product.
- **Stages (4), with participating data objects:**
  - Plan & Approve Deployment: Actual Product Instance, Change, Desired Product Instance, Product Release, Service Contract.
  - Fulfill Deployment: Actual Product Instance, Change, Desired Product Instance, Fulfillment Book, Knowledge Item, Problem, Product Release, Resource, Runbook, Service Monitor.
  - Validate Deployment: Actual Product Instance, Change, Desired Product Instance, Problem, Product Release, Resource, Runbook, Service Contract.
  - Observe Deployment: Actual Product Instance, Event, KPI, Log, Service Contract.

### 5.5 Release value stream

Makes Service Offers available to consumers for ordering a new, changed or decommissioned product instance or its support. Key stakeholder: Catalog Manager. Value: Managed, consumable Service Offers for the Digital Product.

- **Depends on:** Deploy.
- **Scenarios (4):** Release a New Service Offer; Change an Existing Service Offer; Bundle Existing Service Offers; Terminate a Service Offer.
- **Stages (3), with participating data objects:**
  - Define Service Offer: Cost Model, Fulfillment Book, Knowledge Item, Product Release, Service Contract, Service Offer.
  - Implement Service Offer: Knowledge Item, Service Offer Catalog, Service Offer.
  - Publish Service Offer: Cost Model, Knowledge Item, Service Offer Catalog, Service Offer.

### 5.6 Consume value stream

The consumer's lifecycle: select an offer, order, get fulfillment, get support and get status. Key stakeholder: Customer or consumer (person or system). Value: Consumers find offerings and obtain deployed, supported products under a Service Contract.

- **Depends on:** Release, Operate.
- **Scenarios (4):** Order a New Desired Product Instance; Order an Actual Product Instance Modification; Order an Actual Product Instance Termination; Order an Actual Product Instance Support.
- **Stages (5), with participating data objects:**
  - Select an Offer: Entitlement, Identity, Interaction, Service Offer Catalog, Service Offer.
  - Agree to Service Offer: Interaction, Order, Service Contract.
  - Subscribe to Service Offer: Actual Product Instance, Change, Chargeback Contract, Cost Model, Desired Product Instance, Fulfillment Book, Order, Resource, Service Contract, Subscription.
  - Provide Service Support: Incident, Interaction, Knowledge Item, Subscription.
  - Publish Service Status: Chargeback Contract, Chargeback Record, Incident, KPI, Service Contract, Subscription, Usage Record.

### 5.7 Operate value stream

Keeps deployed instances available and performing within their Service Contract, including compliance and security. Key stakeholder: Consumer. Value: The instance operates and can be consumed as the Service Contract agrees.

- **Depends on:** Deploy, Consume.
- **Scenarios (5):** Remediate an Identified Back-End Issue; Ensure Disaster Recovery Objectives; Remediate a major Event or Incident; Remediate Consumer Front-End Issue; Perform Scheduled Maintenance.
- **Stages (3), with participating data objects:**
  - Detect Issue: Actual Product Instance, Event, Incident, Interaction, Log, Service Contract, Service Monitor.
  - Diagnose Issue: Actual Product Instance, Event, Incident, Knowledge Item, Log, Problem, Runbook, Service Contract.
  - Resolve Issue: Actual Product Instance, Change, Event, Incident, Interaction, Knowledge Item, Log, Runbook, Service Contract.


The stakeholders named across the stages are examples only (11.8.4): Business Analyst, Business Stakeholder, Catalog Manager, Chief Security Officer, Compliance Manager, Consumer, Data Protection Officer, Development Team, Enterprise Architect, External Stakeholder, Operations Manager, Product Architect, Product Manager, Product Portfolio Manager, Release & Deployment Manager, Risk Analyst, Scrum Master, Security Analyst, Security Architect, Security Officer, Service Desk Agent, Support Specialist, Test Specialist, Vendor Manager.

## 6. Plan functions (chapter 6)

Plan covers digital strategy and the portfolio of Digital Products. It ensures policy compliance, tracks Scope Agreements and the Portfolio Backlog, and prepares for Build. It is used by the Evaluate and Explore value streams. Two functions: **Strategy** (Policy, Strategy and Enterprise Architecture components) and **Portfolio** (Portfolio Backlog, Proposal and Product Portfolio components).


### 6.1 Strategy function

#### 6.1.1 Policy functional component

Creates, reviews, approves and audits the policies the digital organization follows, internal and external. Supports the value streams: Evaluate, Explore, Integrate.

- **Policy data object** (6.1.1.1). A rule or directive the digital organization maintains and must comply with.
  - Key attributes: Id, Name, Description, Applicable Geography.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Policy to Digital Product (n:m)
    - Policy to Architecture Roadmap Item (n:m)
    - Policy to Portfolio Backlog Item (n:m)
    - Policy to Requirement (n:m)

#### 6.1.2 Strategy functional component

Maintains the portfolio strategy in line with business strategy, as themes and the objectives that serve them. Supports the value streams: Evaluate, Explore.

- **Strategic Theme data object** (6.1.2.1). A statement of direction that groups strategic objectives and gives context to portfolio decisions.
  - Key attributes: Id, Name, Description.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Strategic Theme to Strategic Objective (n:m)
- **Strategic Objective data object** (6.1.2.2). A specific, actionable goal with measurable outcomes for named stakeholders.
  - Key attributes: Id, Name, Description.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Strategic Theme to Strategic Objective (n:m)
    - Strategic Objective to Portfolio Backlog Item (n:m)
    - Strategic Objective to Architecture Roadmap Item (n:m)

#### 6.1.3 Enterprise Architecture functional component

Develops the enterprise architectures that keep the product portfolio coherent: roadmaps, blueprints and reusable building blocks. Supports the value streams: Evaluate, Explore.

- **Architecture Roadmap Item data object** (6.1.3.1). A work package on a timeline that realizes a step toward the target architecture.
  - Key attributes: Id, Name, Status, TargetDate, Roadmaps, Description.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Policy to Architecture Roadmap Item (n:m)
    - Strategic Objective to Architecture Roadmap Item (n:m)
    - Architecture Roadmap Item to Product Backlog Item (n:m)
    - Portfolio Backlog Item to Architecture Roadmap Item (n:1)
    - Architecture Roadmap Item to Value Stream (n:m)
    - Architecture Roadmap Item to Architecture Blueprint (n:m)
- **Architecture Blueprint data object** (6.1.3.2). An approved architecture definition: the building blocks, including Digital Products, and how they relate.
  - Key attributes: Id, Name, Description, Version, Artifact List.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Architecture Roadmap Item to Architecture Blueprint (n:m)
    - Architecture Blueprint to Digital Product (n:m)
- **Value Stream data object** (6.1.3.3). An end-to-end view of how value reaches a stakeholder, for the business or for managing Digital Products.
  - Key attributes: Id, Name, Description, Stakeholder, Value Stream Id (N).
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Architecture Roadmap Item to Value Stream (n:m)
    - Value Stream to Digital Product (n:m)


### 6.2 Portfolio function

#### 6.2.1 Portfolio Backlog functional component

Manages the lifecycle and visibility of portfolio-level work items, grouped and prioritized. Supports the value streams: Evaluate, Explore, Integrate.

- **Portfolio Backlog Item data object** (6.2.1.1). A discrete statement of portfolio-level work with acceptance criteria and funding needs.
  - Key attributes: Id, Name, Description, Prioritization, Acceptance Criteria, Related Products, Demand Profile, Cost Estimation.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Policy to Portfolio Backlog Item (n:m)
    - Strategic Objective to Portfolio Backlog Item (n:m)
    - Portfolio Backlog Item to Architecture Roadmap Item (n:1)
    - Portfolio Backlog Item to Scope Agreement (1:1) [conflict between sections]
    - Portfolio Backlog Item to Digital Product (n:m) [conflict between sections]
    - Portfolio Backlog Item to Product Backlog Item (1:n)
    - Requirement to Portfolio Backlog Item (n:m)
    - Problem to Portfolio Backlog Item (1:1)

#### 6.2.2 Proposal functional component

Evaluates the feasibility and resources needed to answer a demand and manages proposals through proposed, approved, active, deferred and rejected states. Supports the value streams: Evaluate, Explore, Integrate.

- **Scope Agreement data object** (6.2.2.1). A proposal built from rationalized Portfolio Backlog Items: budget, benefits, scope and status.
  - Key attributes: Id, Description, Business Entity, Anticipated Business Value (optional), Proposed Budget, Approved Budget, Status, Context.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Portfolio Backlog Item to Scope Agreement (1:1) [conflict between sections]
    - Scope Agreement to Budget Item (n:1)
    - Scope Agreement to Product Backlog Item (1:n)
    - Digital Product to Scope Agreement (n:m)

#### 6.2.3 Product Portfolio functional component

Organizes every Digital Product into portfolios by ownership, value stream, product line or investment group. Supports the value streams: Evaluate, Explore.

- **Digital Product data object** (6.2.3.1). Digital Product Backbone data object. The entity that represents a product across its whole lifecycle and every value stream.
  - Key attributes: Id, Name, Description, Product Manager, Investment Status, Portfolio, Business Criticality, Security Risk, Budget, Total Cost of Ownership (TCO), Profit/Loss.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Policy to Digital Product (n:m)
    - Architecture Blueprint to Digital Product (n:m)
    - Value Stream to Digital Product (n:m)
    - Portfolio Backlog Item to Digital Product (n:m) [conflict between sections]
    - Digital Product to Scope Agreement (n:m)
    - Digital Product to Product Design (1:n)
    - Digital Product to Digital Product (n:m)
    - Product Backlog Item to Digital Product (n:1)
    - Source to Digital Product (n:1)
    - Budget Item to Digital Product (n:1)


## 7. Build functions (chapter 7)

Build covers creating, enhancing and maintaining Digital Products: planning work, designing, developing or configuring, testing and releasing. It is process-agnostic (Scrum, Kanban, project methods and test-driven development all fit) and covers custom software, cloud-native applications, packaged software, SaaS and infrastructure products. Used by Integrate, Deploy and Release. Two functions: **Develop** and **Test**.


### 7.1 Develop function

#### 7.1.1 Product Backlog functional component

Manages the work items that design and deliver new releases of a product. Supports the value streams: Evaluate, Explore, Integrate.

- **Product Backlog Item data object** (7.1.1.1). A unit of work on a product: epic, feature, story or task.
  - Key attributes: Id, Title, Type, Description, Status, Parent Id, Budget, Actual Spend, Start Date, End Date, Size, Definition of Done, Priority, Value.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Architecture Roadmap Item to Product Backlog Item (n:m)
    - Portfolio Backlog Item to Product Backlog Item (1:n)
    - Scope Agreement to Product Backlog Item (1:n)
    - Product Backlog Item to Digital Product (n:1)
    - Product Backlog Item to Product Backlog Item (1:n)
    - Product Backlog Item to Product Backlog Item (n:m)
    - Product Backlog Item to Product Release (n:1) [conflict between sections]
    - Product Backlog Item to Product Design (n:1)
    - Product Backlog Item to Source (n:m)
    - Product Backlog Item to Defect (n:m) [conflict between sections]
    - Product Backlog Item to Requirement (n:m)
    - Product Backlog Item to Test Case (n:m)

#### 7.1.2 Requirement functional component

Keeps the long-lived functional and non-functional requirements of a product, including security, privacy and service levels. Supports the value streams: Explore, Integrate.

- **Requirement data object** (7.1.2.1). A long-lived statement of required functionality or a non-functional condition.
  - Key attributes: Id, Name, Description, Purpose, Type, Status, Reference, Priority, Owner, Version.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Policy to Requirement (n:m)
    - Requirement to Portfolio Backlog Item (n:m)
    - Product Backlog Item to Requirement (n:m)
    - Requirement to Product Design (n:m)
    - Requirement to Requirement (n:m)
    - Requirement to Test Case (1:n) [conflict between sections]

#### 7.1.3 Product Design functional component

Creates and maintains the design of a Digital Product so that it meets requirements, architecture and policy. Supports the value streams: Explore, Integrate.

- **Product Design data object** (7.1.3.1). Digital Product Backbone data object. The design artifacts for a Digital Product and the changes made to them for a release.
  - Key attributes: Id, Name, Description, Version, Artifacts.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Digital Product to Product Design (1:n)
    - Product Backlog Item to Product Design (n:1)
    - Requirement to Product Design (n:m)
    - Product Design to Product Release (1:n)

#### 7.1.4 Source Control functional component

Holds all source code and configuration under version control and traces every change to backlog items. Supports the value streams: Integrate.

- **Source data object** (7.1.4.1). Source code and configuration under version control that realizes the design.
  - Key attributes: Id, Version, Repository, Owner, Date/Time, Person Id(s), Tags, Comments.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Product Backlog Item to Source (n:m)
    - Source to Pipeline (n:m)
    - Source to Build Package (n:m)
    - Source to Test Case (n:m)
    - Source to Defect (n:m)
    - Source to Digital Product (n:1)

#### 7.1.5 Pipeline functional component

Orchestrates building, verifying, testing and deploying changes to deliver a validated release. Supports the value streams: Integrate.

- **Pipeline data object** (7.1.5.1). The orchestrated build, test and deployment workflow that delivers a release.
  - Key attributes: Id, Name, Version.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Source to Pipeline (n:m)
    - Pipeline to Test Plan (n:m) [conflict between sections]
    - Pipeline to Build Package (1:n)
    - Pipeline to Product Release Blueprint (1:n)
    - Pipeline to Change (1:n)

#### 7.1.6 Build Package functional component

Is the authoritative store for build packages and their artifacts. Supports the value streams: Integrate.

- **Build Package data object** (7.1.6.1). A deployable collection of build artifacts kept in a secure repository.
  - Key attributes: Id, Name, Description, Type, Status, Compliance Status, Version, Tags and Metadata.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Source to Build Package (n:m)
    - Pipeline to Build Package (1:n)
    - Build Package to Test Plan (n:m)
    - Build Package to Product Release Blueprint (n:m)
    - Build Package to Build Package (n:m)
    - Test Case to Build Package (n:m)

#### 7.1.7 Release Composition functional component

Manages the Product Release and creates the Blueprint used to deploy and operate it. Supports the value streams: Integrate, Deploy, Release.

- **Product Release data object** (7.1.7.1). Digital Product Backbone data object. A candidate or actual release of a Digital Product with its documentation and artifacts.
  - Key attributes: Id, Name, Description, Status, Version, Tags, Deployment Model, Actual Spend.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Product Backlog Item to Product Release (n:1) [conflict between sections]
    - Product Design to Product Release (1:n)
    - Product Release to Product Release Blueprint (n:1) [conflict between sections]
    - Product Release to Defect (n:m)
    - Product Release to Desired Product Instance (1:n)
    - Product Release to Product Release (n:m)
    - Product Release to Test Plan (n:m)
- **Product Release Blueprint data object** (7.1.7.2). The specification and procedures for deploying and operating a release.
  - Key attributes: Id, Name, Description, Version, Deployment Model.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Pipeline to Product Release Blueprint (1:n)
    - Build Package to Product Release Blueprint (n:m)
    - Product Release to Product Release Blueprint (n:1) [conflict between sections]
    - Service Offer to Product Release Blueprint (n:1) [conflict between sections]


### 7.2 Test function

#### 7.2.1 Test functional component

Plans, orchestrates and runs the tests, including reviews, that show a release meets the requirements. Supports the value streams: Integrate.

- **Test Case data object** (7.2.1.1). A definition of how to validate one aspect of a release.
  - Key attributes: Id, Name, Description, Status, Result.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Product Backlog Item to Test Case (n:m)
    - Requirement to Test Case (1:n) [conflict between sections]
    - Source to Test Case (n:m)
    - Test Case to Build Package (n:m)
    - Test Case to Test Plan (n:m)
    - Test Case to Defect (1:n)
    - Test Case to Test Case (1:n)
- **Test Plan data object** (7.2.1.2). A plan that fixes test scope and coverage and lists the Test Cases to run.
  - Key attributes: Id, Name, Description, Status, Version, Test Runs.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Pipeline to Test Plan (n:m) [conflict between sections]
    - Build Package to Test Plan (n:m)
    - Test Case to Test Plan (n:m)
    - Product Release to Test Plan (n:m)
    - Test Plan to Test Plan (n:m)

#### 7.2.2 Defect functional component

Tracks defects with their origin, status, importance and links to requirements and problems. Supports the value streams: Integrate.

- **Defect data object** (7.2.2.1). An issue with a release that must be remediated to meet the requirements.
  - Key attributes: Id, Title, Description, Status.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Product Backlog Item to Defect (n:m) [conflict between sections]
    - Source to Defect (n:m)
    - Product Release to Defect (n:m)
    - Test Case to Defect (1:n)
    - Problem to Defect (1:n)


## 8. Deliver functions (chapter 8)

Deliver is a consumption-driven engagement model that goes beyond classic service request management: it gives consumers one place to find and obtain what they need and supports fulfillment, costing, knowledge sharing, self-service and collaboration. Used by Release, Consume and Deploy. Two functions: **Consume** and **Fulfill**.


### 8.1 Consume function

#### 8.1.1 Consumption Experience functional component

Is the single front end through which consumers request, get support and see status. Supports the value streams: Consume, Operate.

- **Interaction data object** (8.1.1.1). A consumer request for assistance through any channel; it is routed to an order, change, incident or request for information.
  - Key attributes: Id, Description, Status, Opened For, Assigned To, Opened, Updated.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Interaction to Identity (n:1) [conflict between sections]
    - Interaction to Order (n:1) [conflict between sections]
    - Interaction to Incident (1:n)
    - Interaction to Knowledge Item (1:n) [conflict between sections]
    - Service Offer to Interaction (n:1)

#### 8.1.2 Identity functional component

Controls the identities of consumers, human or machine, and the entitlements that govern access. Supports the value streams: Consume.

- **Identity data object** (8.1.2.1). A consumer (person or machine) who may use the consumption experience.
  - Key attributes: Id, Name, Discriminator, Location, Creation Date, Expiry Date, Organization Id.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Interaction to Identity (n:1) [conflict between sections]
    - Identity to Order (1:n)
    - Identity to Entitlement (1:n) [conflict between sections]
    - Subscription to Identity (n:1)
- **Entitlement data object** (8.1.2.2). A grant or denial of access to Service Offers and resources.
  - Key attributes: Id, Type.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Identity to Entitlement (1:n) [conflict between sections]
    - Entitlement to Service Offer (n:1)

#### 8.1.3 Offer functional component

Aggregates published services into consumable Service Offers and groups them into catalogs. Supports the value streams: Release, Consume.

- **Service Offer Catalog data object** (8.1.3.1). A collection of Service Offers offered to certain consumers.
  - Key attributes: Id, Name.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Service Offer Catalog to Service Offer (n:m)
- **Service Offer data object** (8.1.3.2). Service Offer Backbone data object. The definition of what can be ordered, with price, delivery terms and service levels.
  - Key attributes: Id, Catalog Id, Name, Start Date, Expiry Date, Status, Price, Required Value.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Service Offer to Product Release Blueprint (n:1) [conflict between sections]
    - Entitlement to Service Offer (n:1)
    - Service Offer Catalog to Service Offer (n:m)
    - Service Offer to Order (1:n)
    - Service Offer to Subscription (n:m) [conflict between sections]
    - Service Offer to Interaction (n:1)
    - Service Offer to Service Offer (n:m)

#### 8.1.4 Order functional component

Turns clean orders into fulfillment requests and keeps subscriptions current. Supports the value streams: Integrate, Consume.

- **Order data object** (8.1.4.1). A formal request to create, change or remove a consumer's use of a Service Offer.
  - Key attributes: Id, Status, Date, Latest Fulfill Date, Actual Fulfill Date, Required Value.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Interaction to Order (n:1) [conflict between sections]
    - Identity to Order (1:n)
    - Service Offer to Order (1:n)
    - Order to Subscription (n:m)
    - Order to Change (1:n) [conflict between sections]
- **Subscription data object** (8.1.4.2). Service Offer Backbone data object. The consumer's right to access a service.
  - Key attributes: Id, Status, Start Date, Expiry Date.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Subscription to Identity (n:1)
    - Service Offer to Subscription (n:m) [conflict between sections]
    - Order to Subscription (n:m)
    - Subscription to Chargeback Contract (1:n)
    - Subscription to Desired Product Instance (n:1)
    - Subscription to Service Contract (1:1)

#### 8.1.5 Chargeback functional component

Provides chargeback or showback from subscriptions, service contracts and usage. Supports the value streams: Consume.

- **Chargeback Contract data object** (8.1.5.1). Service Offer Backbone data object. The financial agreement between consumer and provider: billing rule and frequency.
  - Key attributes: Id, Status, Rule, Frequency.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Subscription to Chargeback Contract (1:n)
    - Chargeback Contract to Chargeback Record (1:n) [conflict between sections]
    - Usage Record to Chargeback Contract (n:1) [conflict between sections]
- **Chargeback Record data object** (8.1.5.2). The actual charge or showback amount for one billing period.
  - Key attributes: Id, Status, From Date, To Date, Amount.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Chargeback Contract to Chargeback Record (1:n) [conflict between sections]
    - Chargeback Record to Usage Record (1:n)
    - Cost Model to Chargeback Record (1:n)


### 8.2 Fulfill function

#### 8.2.1 Change functional component

Controls the lifecycle of changes so they are captured, assessed and implemented in an auditable way that limits business risk. Supports the value streams: Deploy, Consume, Operate.

- **Change data object** (8.2.1.1). A proposed change to one or more configuration items, with approval and risk.
  - Key attributes: Id, Title, Description, Category, Approval Status, Risk, Planned Start Time, Planned End Time, Assigned To.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Pipeline to Change (1:n)
    - Order to Change (1:n) [conflict between sections]
    - Change to Desired Product Instance (1:n)
    - Change to Change (n:m)
    - Incident to Change (1:n) [conflict between sections]
    - Problem to Change (1:n)
    - Event to Change (1:n)

#### 8.2.2 Fulfillment Orchestration functional component

Orchestrates the delivery of orders across one or more fulfillment components. Supports the value streams: Integrate, Deploy, Consume.

- **Desired Product Instance data object** (8.2.2.1). Digital Product Backbone data object. The specification of a product deployment that meets the requirements in an Order or Change.
  - Key attributes: Id, Name, Type, Configuration Items, Create Time, Last Modified Time.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Product Release to Desired Product Instance (1:n)
    - Subscription to Desired Product Instance (n:1)
    - Change to Desired Product Instance (1:n)
    - Desired Product Instance to Actual Product Instance (1:1)
    - Desired Product Instance to Fulfillment Book (m:n)
    - Desired Product Instance to Resource (1:n)
    - Desired Product Instance to Desired Product Instance (n:m)

#### 8.2.3 Resource functional component

Manages the pool of resources that support product instances. Supports the value streams: Deploy, Consume.

- **Resource data object** (8.2.3.1). A limited asset that can be allocated to a Digital Product.
  - Key attributes: Id, Type, Status.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Desired Product Instance to Resource (1:n)
    - Resource to Usage Record (1:n)
    - Cost Model to Resource (1:n)

#### 8.2.4 Fulfillment functional component

Documents and automates fulfillment activities such as provisioning, modifying and decommissioning. Supports the value streams: Integrate, Deploy, Release, Consume.

- **Fulfillment Book data object** (8.2.4.1). A runbook that fulfills individual resources for orchestration.
  - Key attributes: Id, Category, Description, Execution Time.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Desired Product Instance to Fulfillment Book (m:n)

#### 8.2.5 Usage functional component

Tracks the actual usage of subscribed services and its cost. Supports the value streams: Consume.

- **Usage Record data object** (8.2.5.1). A measurement of consumption of a service or component.
  - Key attributes: Id, Usage Date From, Usage Date To, Units, Unit Type.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Chargeback Record to Usage Record (1:n)
    - Usage Record to Chargeback Contract (n:1) [conflict between sections]
    - Resource to Usage Record (1:n)


## 9. Run functions (chapter 9)

Run supports operation of Digital Products: assuring that running services stay within stated boundaries and are secure, and giving an overview of digital operations. The chapter lists Evaluate, Consume and Deploy as related value streams; the component sections also list Operate. Two functions: **Support** and **Assure**.


### 9.1 Support function

#### 9.1.1 Service Level functional component

Designs and manages service contracts and KPIs and watches compliance with them. Supports the value streams: Deploy, Release, Consume, Operate.

- **Service Contract data object** (9.1.1.1). Service Offer Backbone data object. The service characteristics and measurement terms; a template for logical services, an instance for realized ones.
  - Key attributes: Id, Name, Type, Provider, Consumer, Start Date, End Date, Support Calendar, Adherence Calculation Periodicity, Maintenance Window.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Subscription to Service Contract (1:1)
    - Incident to Service Contract (n:m)
    - Actual Product Instance to Service Contract (1:n)
    - Service Contract to KPI (n:m) [conflict between sections]
- **KPI data object** (9.1.1.2). The definition of a measured objective, its thresholds and its calculation.
  - Key attributes: Id, Name, Timestamp, Metric, Algorithm.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Service Contract to KPI (n:m) [conflict between sections]

#### 9.1.2 Incident functional component

Restores normal service quickly and tracks the lifecycle of incidents. Supports the value streams: Consume, Operate.

- **Incident data object** (9.1.2.1). An unplanned interruption or quality reduction of a service.
  - Key attributes: Id, Title, Category, Subcategory, Status, Status Time, Outage Start Time, Outage End Time, Severity, Priority, Description, Assigned To.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Interaction to Incident (1:n)
    - Incident to Change (1:n) [conflict between sections]
    - Incident to Service Contract (n:m)
    - Incident to Problem (n:m)
    - Incident to Knowledge Item (n:m)
    - Incident to Runbook (n:m)
    - Incident to Actual Product Instance (n:m)
    - Event to Incident (n:m)
    - Incident to Incident (n:m)

#### 9.1.3 Problem functional component

Manages the underlying causes of severe or repeating incidents and feeds fixes back to development and planning. Supports the value streams: Integrate, Deploy, Operate.

- **Problem data object** (9.1.3.1). The underlying cause of severe or repeating incidents, tracked to resolution.
  - Key attributes: Id, Title, Category, Subcategory, Description, Status, Status Time, Assigned To.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Problem to Defect (1:n)
    - Problem to Change (1:n)
    - Incident to Problem (n:m)
    - Problem to Portfolio Backlog Item (1:1)
    - Problem to Knowledge Item (n:m)
    - Problem to Actual Product Instance (n:m)

#### 9.1.4 Knowledge functional component

Holds searchable content, including known errors, for consumers and operators. Supports the value streams: Deploy, Release, Consume, Operate.

- **Knowledge Item data object** (9.1.4.1). Searchable content for operators and consumers, including known errors.
  - Key attributes: Id, Title, Status, Author Id, Publish Date, Expiry Date, Body.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Interaction to Knowledge Item (1:n) [conflict between sections]
    - Incident to Knowledge Item (n:m)
    - Problem to Knowledge Item (n:m)
    - Knowledge Item to Knowledge Item (n:m)


### 9.2 Assure function

#### 9.2.1 Configuration functional component

Tracks Actual Product Instances and the relationships among their parts. Supports the value streams: Deploy, Consume, Operate.

- **Actual Product Instance data object** (9.2.1.1). Digital Product Backbone data object. The realized deployment of a Desired Product Instance, with its configuration items.
  - Key attributes: Id, Name, Type, Configuration Items, Create Time, Last Modified Time, Owner, Location.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Desired Product Instance to Actual Product Instance (1:1)
    - Actual Product Instance to Service Contract (1:n)
    - Incident to Actual Product Instance (n:m)
    - Problem to Actual Product Instance (n:m)
    - Runbook to Actual Product Instance (n:m)
    - Actual Product Instance to Event (n:m)
    - Service Monitor to Actual Product Instance (1:n)
    - Actual Product Instance to Actual Product Instance (n:m)

#### 9.2.2 Monitoring functional component

Creates and runs monitors across every layer of a service and stores the results. Supports the value streams: Integrate, Deploy, Operate.

- **Service Monitor data object** (9.2.2.1). The definition of operational measurement for an instance or its parts.
  - Key attributes: Id, Name, Description, Type, Measurement Definitions, Last Run Time, Last Run Status.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Service Monitor to Actual Product Instance (1:n)
    - Service Monitor to Log (1:n)
- **Log data object** (9.2.2.2). A record of information about configuration items for understanding health and usage.
  - Key attributes: Id, Timestamp, Data.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Service Monitor to Log (1:n)
    - Log to Event (n:m)

#### 9.2.3 Event functional component

Manages events from detection through correlation, prioritization and closing. Supports the value streams: Deploy, Operate.

- **Event data object** (9.2.3.1). An alert signifying a change of state of a monitored item or instance.
  - Key attributes: Id, Name, Category, Type, Status, Status Time, Severity, Threshold Definitions, Assigned To, Is Correlated.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Event to Incident (n:m)
    - Actual Product Instance to Event (n:m)
    - Log to Event (n:m)
    - Event to Change (1:n)
    - Event to Event (n:m)
    - Event to Runbook (n:m)

#### 9.2.4 Diagnostics & Remediation functional component

Provides manual and automated runbooks that diagnose and remediate faults. Supports the value streams: Deploy, Operate.

- **Runbook data object** (9.2.4.1). A routine set of operator procedures, manual or automated.
  - Key attributes: Id, Description, Category, Execution Time.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Incident to Runbook (n:m)
    - Runbook to Actual Product Instance (n:m)
    - Event to Runbook (n:m)


## 10. Supporting functions (chapter 10)

The Supporting Capabilities underpin the Digital Value Network and serve many value streams and components. They are tied to enterprise shared functions such as finance, HR and procurement but need extensions for managing Digital Products. **They are not normative in this version**; chapter 10 describes them and defines functional components and data objects only for Financial Management.


### 10.1 Financial Management function

#### 10.1.1 Cost Modeling functional component

Associates cost elements with the resources that bear them, as the reference for chargeback. Supports the value streams: Release, Consume.

- **Cost Model data object** (10.1.1.1). How a Digital Product accounts for the cost of the services it delivers.
  - Key attributes: Id, Name, Description, Status, Version, Calculation, Resource Type, Resource Id, Resource Unit of Work, Cost per Unit of Work, Time Period.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Cost Model to Chargeback Record (1:n)
    - Cost Model to Resource (1:n)

#### 10.1.2 Investment functional component

Manages the portfolio of authorized investments and the budget cycle. Supports the value streams: Evaluate.

- **Budget Item data object** (10.1.2.1). An approved investment for one or more Digital Products in a financial period.
  - Key attributes: Id, Financial Period, Investment Type, Approved Budget, Spend, Forecast.
  - Relationships (as the standard writes the cardinality, first-named side first):
    - Scope Agreement to Budget Item (n:1)
    - Budget Item to Digital Product (n:1)


### 10.2 to 10.6 The other Supporting Functions

These five are described but not defined with components, key attributes or relationships.

- **Governance Risk & Compliance (10.2)** embeds security, risk and compliance in digital delivery, including vendors: risk assessment methods, a risk register, mitigation plans, audits, compliance monitoring. Closely linked to the Policy component. Example data objects: risk assessments, risks, vendor risks, audit findings, compliance evidence, risk issues.
- **Workforce Management (10.3)** supports HR aspects of digital delivery: onboarding, teams, resource planning, competencies, job profiles. Example data objects: employee, job profile and roles, team, resource allocation, linked to Identity.
- **Sourcing & Vendor Management (10.4)** manages the vendors, contracts and purchase orders in the digital ecosystem. Sub-capabilities: contract management, procurement, vendor management. Example data objects: vendor, contract, purchase order.
- **Intelligence & Reporting (10.5)** provides data management, analytics and reporting across components, with a standard data catalog and data governance. Example data objects: metrics and KPIs.
- **Collaboration & Communication (10.6)** supports communication between stakeholders: online collaboration, email and chat, alerting and notification, integrated with the delivery pipeline and incident handling.


## 11. IT4IT definitions and metamodel (chapter 11)

### 11.1 to 11.6 Metamodel and abstraction levels

The standard says its metamodel has **ten normative concepts** plus non-normative ones, drawn in Figure 75 (an image). The text defines these concepts and they are listed in `language.yaml`. The metamodel is an ArchiMate solution pattern, and the reference architecture is available as an ArchiMate model in the exchange format (11, 11.6).

The reference architecture is presented at **five abstraction levels**, an approach borrowed from the TM Forum's eTOM work. The upper levels are vendor- and implementation-independent; the lower ones are specific. Only the first three are standardized (11.2):

| Level | Content | Status | Where |
|---|---|---|---|
| 1 | Seven value streams; four functional groups plus Supporting Functions; the Digital Product; key data objects; the functional components that control them; the Product and Service Offer backbones | Normative | Chapters 3, 4; 11.7 |
| 2 | Value stream stages, scenarios and stakeholders; the data objects used by each stage | Normative | Chapter 5; 11.8 |
| 3 | Functional components, data objects with key attributes, relationships with cardinality, data flows | Normative | Chapters 6 to 10; 11.9 |
| 4 | Vendor and system integrator extensions: capabilities, essential services, scenarios and processes | Not normative | 11.10 |
| 5 | Implementation architecture; the full ArchiMate language may be used | Not normative | 11.10.5 |

Levels 2 and 3 together are the formal reference architecture (11.6).

### 11.7 Level 1 concepts

- **Value Network:** the relationships among value-creating functions; the evolution of Porter's value chain, in which each activity both consumes and produces value (11.7.1).
- **Value Stream:** key value-creating activities for a discrete area where net value is added to the Digital Product. Named with a verb; not in "x2y" form; no "continuous" prefix (11.7.2).
- **Functional Group:** an ArchiMate grouping that gathers components and data objects. Level 1 has five groups, Level 2 fourteen. It is not a capability model (11.7.3).
- **Functional Component:** the smallest self-standing unit of technology useful to a digital practitioner; needs data object inputs and outputs; must affect a key data object it controls. Named with a noun (11.7.4).
- **Lifecycle Data Object:** data that annotates or models an aspect of a Digital Product being planned, built, offered or consumed. Only **key** data objects, those needed for end-to-end traceability, are in scope. One data object is controlled by exactly one component. Named with a noun (11.7.5).
- **System of Record:** an authoritative source system; the lifecycle data objects are the authoritative data (11.7.6).
- **Relationships:** the essential links between data objects. They form the "system of record fabric"; no reflexive relationships are said to be defined in this version (11.7.7).
- **Digital Product Backbone:** the key data objects that give a holistic view of a product across its states: Digital Product, Product Design, Product Release, Desired Product Instance, Actual Product Instance (11.7.8).
- **Service Offer Backbone:** the key data objects that control and define consumption: Service Offer, Subscription, Chargeback Contract, Service Contract. The link from a Service Offer to a Product Release goes through the Product Release Blueprint (11.7.9).

### 11.8 Level 2 concepts

A **scenario** is a situation that triggers a value stream (ArchiMate: Outcome). A **value stream stage** refines a value stream, with entry and exit criteria, main activities, example stakeholders and participating data objects with their functions. A **stakeholder** is a persona or role proposed for a stage (ArchiMate: Stakeholder); the standard does not require any, and they must be refined at Level 5 (11.8.1 to 11.8.4).

### 11.9 Level 3 concepts

- **Key attributes** are the vendor-independent minimum every implementation must support, not values every instance must have. The most basic are a unique identifier and a lifecycle status. Names do not repeat the object name ("Id", not "IncidentId") and use dot notation to qualify ("Incident.Id") (11.9.1).
- **Cardinality** has three forms: 1:1, 1:n and n:m, each meaning "can relate"; UML multiplicity, which would say a relationship must exist, is not specified. Relationships are written "A to B (x:y)" in each data object's section. Reading: "Incident to Change (1:n)" means one incident can relate to several changes, and a change to only one incident (11.9.2).
- **Data flow** shows where components must integrate. It is not a process. **System of record integrations** are data flows refined to keep two data objects' relationship consistent; all three conditions must hold: the flow creates a relationship between data objects in the connected components, the objects have a direct relationship to keep, and their lifecycles are interlocked. **Engagement integrations** support the value streams and are guidance only (11.9.3 to 11.9.5).

### 11.10 Levels 4 and 5

Not normative and owned by the consumers of the standard. Vendors may add attributes, non-key data objects, process, canonical data models and integration techniques, provided everything can be mapped back to Levels 1 to 3 and the prescribed model is not changed. **Capabilities** are a non-normative refinement of the Level 2 groups. **Essential services** (create, read, update, delete and similar actions on data objects) replace point-to-point integrations. **Scenarios** are narratives with a master document: introduction, requirements, process flow and an automation specification (11.10).

### Notation and the ArchiMate mapping

Data objects: black circles for key and orange for backbone in the simplified notation; primary components blue rectangles and secondary ones gray; system of record integrations a black dotted line with a solid arrow named for the data object transferred; engagement integrations a blue dotted line with a solid arrow. ArchiMate mapping stated by the standard: functional component = Application Function; data object = Data Object; functional group = Grouping; value stream and stage = Value Stream; scenario = Outcome; stakeholder = Stakeholder; essential service = Application Service; integrations = collaboration and interaction concepts (11.7 to 11.10).

## Appendices

- **Appendix A** cross-references functional components, data objects and value streams alphabetically in four tables (A.1 components, A.2 data objects, A.3 value streams, A.4 data objects per component per value stream). Those tables are captured in `language.yaml` as the `value_streams` field of each component and data object, and `data_objects` per stage.
- **Appendix B** (informative) gives the rationale: the choice of value streams and functional components, related standards and non-normative capability lists per value stream group (strategy and architecture, demand and portfolio, financial management, governance, project, release and deployment, requirements, software engineering, test, change, configuration, request management, supplier, service level, access, operations, event, incident, application, capacity, availability and problem management), and the roadmap of scenarios to come (multi-vendor availability and capacity, service-level management, hybrid requirements, change and configuration, self-service and knowledge, risk, asset management, intelligence and reporting) (B.1 to B.6).
- **Appendix C** lists acronyms.

## Earlier versions

Version 2.1 (C171, January 2017) and 2.0 (C155, October 2015) used four value streams (Strategy to Portfolio, Requirement to Deploy, Request to Fulfill, Detect to Correct) arranged as an IT Value Chain, and a Service Model Backbone built around the IT Service. Version 3.0 replaced the chain with the network and the service with the Digital Product, and gave each of the four value streams' groups a place as a functional group (Snapshot preface; 2.1 front matter).

## Gaps and inconsistencies in the text

The ones to know before using this summary: the published text was not read; the component and data object counts disagree between chapter 3 and Appendix A; 20 relationships are stated with different cardinalities at their two ends; the individual data flows are only in figures.
