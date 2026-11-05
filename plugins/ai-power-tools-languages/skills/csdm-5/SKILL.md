---
name: csdm-5
description: The ServiceNow Common Service Data Model (CSDM) 5, a vendor-defined data model that says where service data belongs in a ServiceNow configuration database (CMDB) and which relationships to use - business capability, business application, information object, SDLC component, application service and other service instances, technology management service (formerly technical service) and its offerings, dynamic CI group, business service and business service offering, service portfolio, request catalog, product models, value streams, and the seven domains (Foundation, Ideation and Strategy, Design and Planning, Build and Integration, Service Delivery, Service Consumption, Manage Portfolios). Use when someone is modeling services for IT service management or a service catalog, mapping applications to services to infrastructure, planning a CMDB or service mapping rollout, or asks what CSDM, the CSDM domains, the crawl-walk-run-fly path, Figure 16 relationships, or the life cycle stage and stage status values allow.
---

# ServiceNow Common Service Data Model (CSDM) 5

CSDM is ServiceNow's guidance on where to put service-related data in its configuration database (the CMDB) and how to link it. **It is a data model defined by one vendor, not a formal standard.** No standards body owns it, it has no conformance clause and no published schema. Its authority is the vendor's white paper and product documentation, and its names (platform table names and relationship types) are what the vendor's products read, so this language keeps them exactly.

CSDM is not a drawing notation either. The white paper draws views (a one-page conceptual model, a life cycle strip, a layered system model, a relationship figure), but it defines no symbols a diagram must follow.

Version covered: **CSDM 5** (white paper published 6 May 2025; product documentation updated September 2026), the latest ServiceNow publishes as of November 2026. Earlier versions: 1 (2018), 2.0, 3.0 (about 2020), 4.0 draft (January 2022).

## What you are creating

A CSDM model describes, for one organization, a chain from idea to consumption:

1. **Why and what** - strategy, goals, ideas and planning items (Ideation and Strategy).
2. **The logical design** - capabilities, business applications, information types (Design and Planning).
3. **The build** - software components and AI assets (Build and Integration).
4. **The running services** - deployed service instances, applications, infrastructure, and the technology services and offerings that manage them (Service Delivery).
5. **What the business consumes** - business services and offerings, the catalog, the portfolio (Service Consumption).
6. **Shared reference data** under all of it (Foundation): value streams, business processes, contracts, product models, locations, groups, users, companies.

Manage Portfolios is a view across parts of the other domains, for service owners. It is not a set of tables.

## Views the paper draws, and what each admits

| View | What it shows | What it admits |
|---|---|---|
| Conceptual Model (Figure 4) | The seven domains on one page; Foundation along the bottom; Manage Portfolio at the center. Solid arrow = relationship, dashed arrow = reference. | The headline entities of each domain, for example Business Capability, Business Application, Information Object, SDLC Component, Product Idea, Planning Item, Service Instance, Technology Management Service and Offering, Dynamic CI Group, Business Service and Offering, Request Catalog, and the Foundation data. |
| End-to-End Service Life Cycle (Figures 2 and 6) | The domains as stages in order: Ideation and Strategy, Design and Planning, Build and Integration, Service Delivery, Service Consumption, with Foundation beneath. | Domains, not individual entities. |
| Domain Entities (Figure 3) | Entity categories under each stage, over bands for business model, enterprise architecture, solution architecture, service model, sales and support. | Categories of entity, not individual concepts. |
| Digital System Model (Figure 5) | Four layers (process, service, functional, infrastructure), design entities left and operational entities right. | Business Process; Information Object, Service Instance, Service Offering; Business Application, System Component Model; Product Model and the hardware CIs. |
| Configuration Item Relationships (Figure 16) | From (parent), Relationship or Reference, To (child). Three line kinds: entity relation (a reference), CMDB relation (arrow with a relationship type), many-to-many map. | The entities and relationships listed in `language.yaml`. |
| Table Names and Labels (Figure 15) | A table of each entity and its platform table, with the service classification where one applies. | Every entity that has a table. |
| Value Stream Mapping (Figure 7), Product Model Classes (Figure 8), Life Cycle models (Figures 9-14) | Mapping of value streams to capabilities and processes; the product model class tree; the stage and status values per life cycle process. | See `language.yaml` (`life_cycle`, product model concepts). |

## Data types and attributes

Coverage is partial: the paper defines no data types. It names attributes on some concepts and gives fixed values for a few, such as Service Classification, Location Type, and the life cycle stages and statuses. Attributes that matter most are Life Cycle Stage and Life Cycle Stage Status on every CI, Model ID, and Service Classification. For the full table definitions the product documentation points to the platform dictionary, which is not read here. See `data_types` in `language.yaml`, and `attributes` on each concept.

## How it is drawn

Coverage is informative: CSDM defines no notation and requires none, but its figures draw things consistently. Figures 7, 8, and 16 use rounded boxes in domain colors, and Figure 4 uses white rectangles on domain panels. A CMDB relation is a solid arrow labeled in square brackets, a reference has crow's-foot and bar marks (dashed in Figure 4), a many-to-many map has two arrowheads, and a generalization has a hollow triangle. Entities and relationships that no figure draws are listed as not specified. See `notation` in `language.yaml`.

Sizes and spacing come from `../_languages/layout-standard.yaml`, and the concept mapping from `layout` in `language.yaml`.

## The concepts, grouped by domain

Names are the paper's, written without spaces in `language.yaml`. Table names are in brackets where the paper gives them.

### Foundation (reference data; mostly not configuration items)

- **Value Stream**, **Value Stream Stage**, **Value Stream Category** (16 shipped categories). Mapped many to many to business capabilities and business processes.
- **Business Process** [`cmdb_ci_business_process`]: the one Foundation table that is a CMDB CI; manually maintained; can nest by a parent.
- **Contract** [`ast_contract`]: not a CI.
- **Product Model** [`cmdb_model`]: not a CI. Ten base types (Application, System Component with Software Component, Service Offering, Firmware and AI System children, Service, Software, Content Product with an AI Content child, Contract, Facility, Hardware, Consumable, Enterprise Good). Each has its own table. A CI points to its product model through a model reference.
- **Product Feature**, **Software Bill of Materials**, **CMDB Group** [`cmdb_group`, not a CI], **Team**, **Knowledge**.
- **Common data**, none a CI: **Company**, **Business Unit**, **Department**, **Location**, **Building**, **Group**, **User**.
- **Life cycle**: two attributes on every CI, Life Cycle Stage and Life Cycle Stage Status, with fixed values per process (product, tangible, intangible, document, location). The figures say which kinds of record each status applies to, and they are the source used here. The written definitions differ in places.

### Ideation and Strategy (new in CSDM 5)

**Product Idea**, **Planning Item**, **Strategic Plan** (mission, vision and value statements), **Strategic Priority**, **Goal** (qualitative), **Target** (quantifiable measure of a goal).

### Design and Planning (logical design; not direct targets of incident, problem or change)

**Business Capability** [`cmdb_ci_business_capability`]: what the organization does, not how; hierarchical, at most six levels. **Business Application** [`cmdb_ci_business_app`]: the portfolio entry for an application across all its environments; manually managed; not version specific. **Information Object** [`cmdb_ci_information_object`]: a type of information (for example personal or payment-card data) that a business application uses.

### Build and Integration

**SDLC Component** [`cmdb_ci_sdlc_component`], which the documentation calls an Agile development component: one separately developed part of a business application (type Application or Infrastructure). **AI System Digital Asset** and its model, dataset and prompt companions. The DevOps change data model sits here too.

### Service Delivery (operational: selectable in incident, problem and change)

- **Service Instance** [`cmdb_ci_service_auto`] is the parent of the deployed-service types: **Application Service** (four population methods, each its own table), and the CSDM 5 siblings **Data**, **Connection**, **Network**, **Operational Process** and **Facility Service Instance**. The siblings are model only: no user interface, manual creation.
- **Application** [`cmdb_ci_appl`]: a discoverable program on one host, not your application inventory. **API**, **AI Function**, **AI Application**, **Network Function** and **Network Function Application**, **Operational Technology** classes, **Infrastructure CI** (`cmdb_ci_*`). **Asset** [`alm_asset`] and **Install Base Item** [`sn_install_base_item`] sit beside CIs in the life cycle: an asset is an item whose financial value is tracked, and an install base item is something provided as a service or sold to a customer.
- **Technology Management Service** [`cmdb_ci_service_technical`], called Technical Service before CSDM 5, and its **offering** (a Service Offering with classification Technical Service).
- **Dynamic CI Group** [`cmdb_ci_query_based_service`]: CIs found by CMDB group queries; acts as a query-based application service or as a group managed by a technology management offering, by its classification.
- The **Service Delivery Network** is not an entity; it is the graph of connection and network service instances.

### Service Consumption (operational)

**Business Service** [`cmdb_ci_service_business`]: what the business sees; single level. **Business Service Offering** (a Service Offering with classification Business Service). **Service Commitment**, **Service Offering Subscription**, **Request Catalog** [`sc_catalog`, not a CI], **Catalog Item**.

### Manage Portfolios

**Portfolio**, **Service Portfolio** [`service_portfolio`, not a CI]: a hierarchical classification of business and technology management services.

### Specialization

Service Instance, Business Service, Technology Management Service and Service Offering all share the parent Service table, whose **Service Classification** attribute (Business Service, Technical Service, Application Service) every extension inherits. Application Service and the CSDM 5 siblings extend Service Instance; AI Application extends Application; the System Component Model product classes sit under Product Model. The paper never says a concept is abstract, so a general concept is not flagged merely for being general.

## Relationships in summary

The paper's Figure 16 lists the relationships it prescribes (35 entries, all in `language.yaml` with their types); the text adds about as many more references and hierarchies. Eight relationship types are named in the figure, each written Parent descriptor::Child descriptor:

- **Provided by::Provides** - Business Capability to Business Application and to Business Service; Connection Service Instance to Network Service Instance; API to Application.
- **Uses::Used by** - Business Application to Information Object and to Application Service. ServiceNow's documentation tells Enterprise Architecture Workspace users to keep the older **Consumes::Consumed by** for the Application Service link, so either is accepted there.
- **Contains::Contained by** - Business Application to SDLC Component; SDLC Component to Application Service; Technology Management Service Offering to Service Instance and to Dynamic CI Group.
- **Depends on::Used by** - Application Service, and the data, network, operational process and facility service instances, to Service Instance; Application Service to Application and to Application Service; Business Service Offering to Service Instance; Network Function to Network Function Application.
- **Connected by::Connects** - Service Instance or Connected Device to Connection Service Instance.
- **Receives data from::Sends data to** - API to Application Service and to Business Service Offering.
- **Runs on::Runs** - Application, and Network Function Application, to Infrastructure CI.
- **Operationalizes::Operationalized by** - Business Process to Business Capability.

References (an attribute, not a relationship record): "Published as" from a Technology Management Service or Business Service to its offerings; "Is part of" from those services to a Service Portfolio; the legacy reference from Business Application to Business Process; the model reference from any CI to a Product Model. Many-to-many maps join Value Streams and Stages to Business Capabilities and Business Processes.

## The rules that matter most

The full list, 56 rules with ids, is in `references/rules.md`. CSDM is guidance, so most are "should".

- Use the prescribed relationships and references as the main way to link CSDM entities; if they are missing, vendor functions such as risk assessment will not work. (CSDM-REL-001, 002)
- Product models, contracts, common data and CMDB groups are not CIs. (CSDM-TBL-001 to 004)
- Business Application and SDLC Component are not operational CIs: keep them out of incident, problem and change. (CSDM-TBL-006)
- Every operational business service and technology management service has at least one offering. (CSDM-SVC-002)
- A CI should reach only one technology management service through Dynamic CI Groups; a Dynamic CI Group cannot contain other groups. (CSDM-SVC-003, 004)
- A business capability hierarchy has at most six levels, no cycles, and only leaves are deleted. (CSDM-HIER-001, 003, 004)
- Life Cycle Stage and Stage Status are fixed attributes; an object takes only the values of its own life cycle process. (CSDM-LCY-001 to 003)
- Adopt in stages: Foundation, Crawl, Walk, Run, Fly. (CSDM-ADOPT-001 to 006)

## Telling similar concepts apart

- **Business Application, Application Service, Application.** A Business Application is the manually kept portfolio entry for the software and everything that serves it, across environments. An Application Service is one deployed instance of it (production, test, a region). An Application is a discovered program on one host. Only the last two are operational.
- **Business Service, Technology Management Service, Service Instance.** A Business Service is the outcome the business consumes. A Technology Management Service is the provider's service that keeps the technology running. A Service Instance is a deployed system, the thing the other two sit on.
- **Service, Service Offering, Service Commitment.** A service is offered in options (offerings); each offering consists of commitments (levels of availability, response, price).
- **Business Capability, Business Process, Value Stream.** A capability is what the organization does; a process is how steps are carried out; a value stream is how work flows end to end to deliver value.
- **CI or not.** If it is reference data, a product model, a contract, a group of CIs, or a catalog or portfolio, it is not a CI and does not appear in CMDB relationships (Business Process is the exception).

## A short example

Westbrook Bank, a fictitious bank, models its small-business checking service. This is an illustration; use your own entities, tables and naming.

- **Foundation.** Company "Westbrook Bank", Business Unit "Retail Banking", Group "Online Banking Support", Value Stream "Open a business account", and a Product Model for its online banking platform.
- **Ideation and Strategy.** A Product Idea "Same-day business account opening", a Planning Item for it, aligned to a Goal "Opening a business account is fast" and a Target "95 percent opened within one business day".
- **Design and Planning.** Business Capability "Account Opening" is provided by Business Application "Westbrook Online Banking", which uses the Information Object "Customer Identity Record".
- **Build and Integration.** The application contains SDLC Component "Account Opening Service" (type Application).
- **Service Delivery.** Application Services "Online Banking - Production" and "Online Banking - Test" depend on an Application and run on infrastructure. The Technology Management Service "Hosting and Operations" is published as the offering "Hosting - 24x7 Production", which contains the production Application Service.
- **Service Consumption.** Business Capability "Account Opening" is provided by Business Service "Business Account Services", published as the offering "Business Checking - Standard", which depends on the production Application Service. The service is part of the Service Portfolio "Retail Banking Services".

## References

- `references/standard.md`: the white paper, section by section, in our words, with page citations.
- `references/rules.md`: all 56 rules with stable ids (`CSDM-<CAT>-nnn`), strength, source page and checkability.
- `language.yaml`: the machine-readable form: 79 concepts with tables and domains, 72 relationships, the life cycle values, reference data, data types, how it is drawn, the rules and the views.
