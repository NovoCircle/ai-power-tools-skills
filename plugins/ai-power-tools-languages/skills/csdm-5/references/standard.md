# ServiceNow Common Service Data Model (CSDM) 5, in our own words

This reference restates the CSDM 5 white paper (ServiceNow, published 6 May 2025; the PDF was refreshed with working
links on 16 June 2025) in our own words, with page citations. Pages are the printed page numbers of the white paper,
which has no numbered sections, so a citation reads "p. N, heading". Short quoted phrases are under 15 words.

**What CSDM is.** CSDM is a **data model defined by one vendor, ServiceNow**. It is not a formal standard: no standards
body owns it, it has no conformance clause and no published schema. It is "best practice guidance" (cover) on where to
place service-related data in ServiceNow's configuration database (the CMDB), and which relationships and references
to use between that data. ServiceNow's own products are described as "CSDM-conforming" when they read and write this
model (p. 3). It is not a product, an implementation guide, a set of reports, code to install or an automatic fix for
past implementations (p. 3).

**The names are the model.** Because the platform's table names and relationship types are what products read, this
language keeps them exactly as the paper writes them (lower case, underscores).

**Second source.** ServiceNow's product documentation (Brazil release, updated 10 September 2026) is cited as "docs". It confirms the paper's relationship list and says some things the paper doesn't.

**Latest version.** CSDM 5 is the latest ServiceNow publishes as of November 2026. Older versions: CSDM 1 (2018), 2.0, 3.0 (about
October 2020), 4.0 (draft, January 2022). A community comment describes a draft toward CSDM 6, but no CSDM 6 paper had been published when this was researched.

---

## 1. Purpose and principles (pp. 3-7)

CSDM began in 2017 as a collaboration between product teams who found that customers and partners had each invented their own service
data models, which blocked features that work across products. The first release (2018) reduced 127 different service classifications to
three service types (p. 4). CSDM 5 widens the aim from technology workflows toward an enterprise and operational service model that
also covers utilities, manufacturing, health care, financial services and other industries (pp. 4-5).

Ten principles guided it (p. 7): simplified concepts; designed for reporting and analytics; prescriptive relationships (use them as the main way to
link CSDM tables); a data model shared across products; agreed definitions used wherever a table, reference or attribute is used; shared tables
supplied in the base system or a free store app; consistent data integrations; limited upgrade impact; data governance and process; documented
guidance from each product team.

What is new in CSDM 5 (p. 6): an Ideation and Strategy domain; software bill of materials; system component, software component and service
offering product models; product feature; value stream with an expanded business process model; teams; defined life cycle stages and statuses; a
DevOps change data model; service instance types beyond application service; an AI data model; and table label changes (technical service
became technology management service).

## 2. Service life cycle and domains (pp. 8-14)

The core view of CSDM 5 is an end-to-end **service life cycle** (p. 8): an idea is captured and judged in Ideation and Strategy; if the business
invests, it is detailed in Design and Planning; built in Build and Integration; released in Service Delivery; and used, with its value measured, in
Service Consumption. Each stage feeds back to earlier stages. Foundation supports every stage.

CSDM 5 has **seven domains** (p. 14). A domain is a grouping of data that supports activity in the platform, "largely based on common function" (p. 10).

| Domain | Holds (summary) | Personas the paper names |
|---|---|---|
| Foundation | Referential data used by the other domains: value streams, business process, contracts, product models, product features, bills of materials, CMDB groups, life cycle values, common data (company, business unit, department, location, group, user), teams, knowledge. Not used in CMDB relationships except Business Process, which is a CMDB table. | Process Owner, Data Steward, Product Owner, Contract Manager |
| Ideation and Strategy (new) | Product ideas, planning items, strategic plans, strategic priorities, goals, targets. | Product Owner |
| Design and Planning | Business capabilities, business applications, information objects: the logical design. Not direct targets of incident, problem and change. | enterprise architect, application owner |
| Build and Integration | SDLC components, the DevOps change data model, AI digital assets: build effort. Not direct targets of incident, problem and change. | Teams |
| Service Delivery (formerly Manage Technical Services) | Service instances (application services and the new siblings), applications, APIs, infrastructure, technology management services and offerings, dynamic CI groups. Operational: selectable in incident, problem and change. | Service Instance Owner, Service Delivery Owner, Service Provider |
| Service Consumption (formerly Sell/Consume) | Business services, business service offerings, request catalog. Operational. | Business Relationship Manager, Customer Service Manager |
| Manage Portfolios | A view across parts of the other domains, so a service owner can oversee both services and the applications behind them. Not a set of tables. | service owner roles |

The paper also gives a four-layer **Digital System Model** (pp. 12-13), with design entities on the left and operational entities on the right in each layer:
the (business) process layer, the service (logical) layer, the functional layer, and the infrastructure layer.

## 3. What a service is (pp. 10-12)

A CSDM service is a business or utility service that provides a specific outcome to its consumer and has a standards-conforming service definition,
service delivery model, service delivery network model and service consumption model (p. 10). Services have three aspects: the interaction, the offering and
the service system (p. 11). Three service types ship, and customers can extend the classification (p. 11):

- **Business Service**: published to business users; typically underpins business capabilities; the most abstract and highest value level; seen the way the customer sees it,
  not the way IT names it; single level (no hierarchy); an operational CI used for impact analysis; has one or more business service offerings. Table `cmdb_ci_service_business`.
- **Technology Management Service** (called Technical Service in CSDM 4 and before): published to service consumers; provides the administrative and operational
  functions to manage the technologies layered under business and application services; provider focused; single level; an operational CI. Table `cmdb_ci_service_technical`.
- **Service Instance** (the table that application services extend): the instantiation of a service. An **Application Service** is a logical or designated instance of a business
  application or application function, based on the deployed system and software stack, designated by environment (development, test, production) or by region or line of
  business. It can be created by manual mapping, service mapping with an entry point, tags or a dynamic query. Data, connection, network, facility and operational process
  service instances are its siblings. Table `cmdb_ci_service_auto`.

A **service offering** is a stratification of a service into options (location, environment, pricing, availability, capability, support group, approval group, packaging). It
consists of one or more **service commitments**, the obligations agreed between provider and consumer. A **service offering subscription** records which parties have access
(pp. 43, 45, 56). The service offering table `service_offering` holds both business and technology management offerings; the **service classification** attribute (inherited from the
parent service table `cmdb_ci_service`) tells which (pp. 37, 43, 45).

## 4. Foundation domain (pp. 14-29)

- **Value stream** (`cmn_value_stream`), its **category** (`cmn_value_stream_categories`, 16 shipped categories) and **stage** (`cmn_value_stream_stage`), and two mapping tables,
  `cmn_value_stream_capability` and `cmn_value_stream_process`, that tie value streams and stages to business capabilities and business processes many to many (pp. 14-15).
- **Business Process** (`cmdb_ci_business_process`): a method of related steps to reach a business goal; manually maintained CI with criticality (declared and determined),
  confidentiality, integrity and availability impact, review frequency (monthly, quarterly, semi-annual, annually, none) and next review date; can nest through a parent (p. 16).
- **Contract** (`ast_contract`): not a CI; uses contract model types (p. 16).
- **Product model** (`cmdb_model`): not a CI. Everything is a product (goods and services sold, services released for your own use, things purchased) (p. 16). Ten base types:
  Application Model (version-agnostic); System Component Model (version-specific) with Software Component Model, Service Offering Model, Firmware Model and AI System Product Model
  beneath it; Service Model; Software Model (software asset management, entitlement use); Content Product Model; Contract Model; Facility Model; Hardware Model; Consumable Model;
  Enterprise Good Model (p. 17). Product model classes are not CMDB classes (p. 18). CIs reference their product model through a model reference on every CMDB table (p. 18).
- **Product feature**: what a product does; supports release; connects to stories, code and tests (p. 18). **Software bill of materials**: inventory of the components of a software product (p. 18).
- **CMDB Group** (`cmdb_group`): a set of CIs from saved queries, encoded queries or manual entries; not a CI (pp. 18-19).
- **Life cycle**: two standard attributes on every CI, Life Cycle Stage and Life Cycle Stage Status, replace roughly eight legacy state and status attributes. The pair uniquely specifies an object's status. Values
  are fixed by ServiceNow. Five processes use them: product, tangible, intangible, document and location (pp. 19-27). Stage lists are in `language.yaml` under `life_cycle`, taken from the figures, which also say which kinds of record each status applies to. The written definitions differ in places, and `life_cycle.differences` records how.
- **Common data** (not CIs; p. 27): `core_company`, `business_unit`, `cmn_department`, `cmn_location`, `cmn_building`, `sys_user_group`, `sys_user`. Locations carry a source id, a type
  (Region through Room), a managed-by group, a duplicate-versus-primary flag and life cycle values (p. 28).
- **Teams**: a related list on a CI tying a group to it by group type (Change, Managed by, Support) (p. 29). **Knowledge**: knowledge bases and articles (p. 29).

## 5. Ideation and Strategy domain (pp. 29-30)

Product idea (`sn_align_core_product_idea`), planning item (`sn_align_core_planning_item`: a demand, project, epic or custom work item), strategic plan (`sn_gf_plan`: a mission, vision and value
statement), strategic priority (`sn_gf_strategy`), goal (`sn_gf_goal`: a broad qualitative outcome) and target (`sn_gf_goal_target`: a quantifiable measure). Planning items are aligned to goals and
targets. Product models, value streams and business processes are the foundation entities that contribute here (p. 30).

## 6. Design and Planning domain (pp. 31-33)

- **Business Capability** (`cmdb_ci_business_capability`): what the organization does, not how. Hierarchical; levels are assigned from the parent and recalculated when it changes; no more than six levels; only a leaf can
  be deleted; no circular parentage. A hierarchy that needs more than six levels should be split, the lower levels being processes and tasks (pp. 31-32). The paper recommends creating CI relationships between
  capabilities and business applications, and between business applications and application services (p. 31).
- **Business Application** (`cmdb_ci_business_app`): the logical representation of all software and infrastructure configured to provide business functionality, across all environments and regions; manually managed, so
  its relationships are created by hand; not required but recommended for planning mergers, divestitures, cloud migration and cost reduction (p. 32). A type attribute can mark platform applications and platform hosts (p. 32).
  Its singular reference to Business Process is legacy from CSDM 5 (p. 33).
- **Information Object** (`cmdb_ci_information_object`): the type of information at the conceptual or logical tier, with attributes such as sensitivity; referenced by business applications to scope governance and compliance
  (types such as personal or payment-card data) (p. 33).

## 7. Build and Integration domain (pp. 34-35)

- **SDLC Component** (`cmdb_ci_sdlc_component`): one unique development effort of code, a part of a business application or technology. Type Application (microservices, APIs) or Infrastructure (database or security
  configuration). A deployed Application-type component is an application service; a deployed Infrastructure-type component is the infrastructure CI whose configuration it describes (p. 35). Not an operational CI (p. 53).
- **DevOps change data model**: the data that connects a DevOps toolchain to platform work records (p. 34).
- **AI digital assets**: the AI System Digital Asset (deployable source, binaries and components of an AI or generative AI service) plus model, dataset and prompt digital assets (p. 35).

## 8. Service Delivery domain (pp. 36-44)

New in CSDM 5: service instances beyond application services (data and AI, operational process, facility, connection, network); service classes beyond digital products (utilities, manufacturing, retail, transportation); APIs and operational technology
as first-class parts of the delivery system; generative AI as a first-class entity (pp. 36-37). The **Service Classification** attribute on the parent service table is a legacy choice list reused to tell service types apart; it is filled automatically from the CI's class (p. 37).
There is **no user interface** for service instances as of CSDM 5, the new types are model-only, there is no expectation of use unless local needs require it, and they are not part of event impact analysis (pp. 37-38).

Application service (p. 39): registered first, populated later; population by service mapping and manual (`cmdb_ci_service_discovered`), tags (`cmdb_ci_service_by_tags` in the table list; `cmdb_ci_service_tags` in the text), calculated (`cmdb_ci_service_calculated`) or query based
(`cmdb_ci_query_based_service`). Its relationships include business applications, business services, technology management services, applications and infrastructure CIs. The offering of application services should be exposed through the related business or technology
management service offering. Siblings: data (`cmdb_ci_data_service_instance`), connection (`cmdb_ci_connection_service_instance`), network (`cmdb_ci_network_service_instance`), operational process (`cmdb_ci_operational_process_service_instance`), facility
(`cmdb_ci_facility_service_instance`); network function `cmdb_ci_network_function_instance` (pp. 39-40). The **Service Delivery Network** is not an entity: it is the set of interconnected connection and network service instances (pp. 39-41).

Application (`cmdb_ci_appl`): a discoverable program on one host; not an inventory of applications; manual population not recommended (pp. 41, 53). Also `cmdb_ci_api`, `cmdb_ci_network_function_application`, `cmdb_ci_function_ai`, `cmdb_ci_appl_ai_application` (extends application)
and operational technology classes (pp. 41-42). Infrastructure CIs are `cmdb_ci_*` (p. 42).

Technology management service and offering (pp. 42-44): the offering is classified Technical Service in `service_offering`; every operational technology management service should have at least one offering; the paper says a technology management service may reference a service portfolio node since the Rome
release; offerings can be requested through the request catalog from the New York release.

Dynamic CI Group (`cmdb_ci_query_based_service`, pp. 43-44): a dynamic grouping of CIs from CMDB group queries; contains CIs, not other groups; classification Application Service makes it act as a query-based application service, Technical Service makes it a group managed by a technology
management offering. Use cases: query-based application service, a managed group of infrastructure, patch management. A CI should relate through such groups to only one technology management service.

## 9. Service Consumption and Manage Portfolios (pp. 44-46)

Business service and business service offering are covered in section 3. The **request catalog** (`sc_catalog`) is a consumable view of available products, services, commitment options and offerings; **catalog items** are consumable representations of service offerings; a service is often made of several items (pp. 45-46).
Every business service should have at least one offering. Offerings with different commitments should be given different service level agreement definitions (p. 45).

A **portfolio** is a collection of services, products, projects or applications managed together; the paper covers the **service portfolio** (`service_portfolio`), a hierarchical classification of business and technology management services (p. 46).

## 10. Relationships (pp. 47-48)

Figure 15 (p. 47) maps each entity to its table and service classification. Figure 16 (p. 48) lists the relationships and references CSDM prescribes. The legend distinguishes an **entity relation** (a reference attribute), a **CMDB relation** (a relationship record between two CIs with a relationship
type written Parent descriptor::Child descriptor) and an **m2m map** (a many-to-many mapping). The relationship types named are: Provided by::Provides, Uses::Used by, Contains::Contained by, Depends on::Used by, Connected by::Connects, Receives data from::Sends data to, Runs on::Runs and Operationalizes::Operationalized by.
The docs say CSDM v5 uses Uses::Used By between a business application and an application service, and that Enterprise Architecture Workspace users should keep Consumes::Consumed by. The full list is in `language.yaml`. The paper says some products have a critical dependency on these relationships; with manual mapping, "what would discovery do?" is the test; impact analysis follows relationships in the reverse direction (p. 48).

## 11. Adoption and migration (pp. 51-60)

Adopt in stages, "foundation, crawl, walk, run, fly" (p. 51):

| Stage | Entities | Why (summary) |
|---|---|---|
| Foundation | company, business unit, department, location, group, user, CMDB group, product models, contracts | Referential data and early agreement on reporting needs. |
| Crawl | business application, SDLC component (optional), application service, application, server or host | The minimum for incident, problem and change; sets up later enterprise architecture, DevOps and service mapping use. |
| Walk | technology management service, technology management service offering, dynamic CI group | Management of CIs through offerings; groundwork for service portfolio management. |
| Run | business service portfolio, business service, business service offering | Impact assessment for business services; service owner views; subscriber detail. |
| Fly | request catalog, business capability, information object | Full model; rationalizing spend on applications and capabilities; data-type governance. |

Migrating into CSDM (pp. 58-60), five steps: back up data; map attributes (best practice, keep, refactor, do not need); identify every dependency on the old table (reports, rules, scripts, references); refactor attributes; migrate data (change the class, fix dependencies, reload attributes, validate). Moving a CI to another class
can lose data held in attributes that are not in the new table hierarchy.

## 12. What the paper does not give

No attribute is marked mandatory (other than a primary location for a duplicate location). No instance-level examples are included; the paper defers examples to separate reference blueprints (p. 61). Table names for several concepts are not stated.
