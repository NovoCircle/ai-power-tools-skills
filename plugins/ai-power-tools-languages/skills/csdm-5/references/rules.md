# CSDM 5 rules

Generated from `language.yaml` (`constraints`). Do not edit by hand; change the language file and regenerate.

Each rule has a stable id of the form `CSDM-<CAT>-nnn`. The number never changes once assigned. A rule that is retired keeps its id and is marked withdrawn rather than reused.

CSDM is a vendor-defined data model, not a formal standard, and its white paper is guidance. It rarely says "must". The grading below is ours and is stated so a ruleset can be consistent.

## Strength

| Strength | Meaning |
|---|---|
| must | The paper states a flat limit, definition or prohibition ("cannot", "is not a CI", "single level", "not editable", "must be identified"). A model that breaks it is not well formed. |
| should | The paper recommends it ("should", "recommended", "best practice") or states a consequence of not following it. Breaking it is a warning, not an error. |
| note | The paper describes, offers an option or reports product behavior. Recorded for completeness; not checkable on its own. |

## Checkable

`static` can be judged from the model's structure alone; `partial` can be judged for some cases; `runtime` depends on how records are used in operation; `none` is guidance for people.

## Categories

| Category | Name | Covers | Rules |
|---|---|---|---|
| SVC | Service model | Business, technology management and application services, their offerings and the groups that manage them. | 13 |
| TBL | Table placement | Which entities are configuration items, which are not, and where each entity is stored. | 11 |
| REL | Relationship use | Which relationships to create between CSDM entities and why. | 8 |
| HIER | Hierarchy and data quality | Capability levels, parent references and a few data rules on referential data. | 8 |
| LCY | Life cycle | The stage and stage status attributes and how they are adopted. | 5 |
| ADOPT | Adoption and migration | The staged adoption path and the migration steps. | 7 |
| PRIN | Principles and scope | The principles and the statements of what CSDM is and is not. | 4 |

Section references are to the CSDM 5 white paper by printed page number and heading; the paper has no numbered sections. "docs" means ServiceNow's product documentation, Brazil release, updated 10 September 2026. Relationship lists, multiplicities and table names are in `language.yaml` and are not repeated here.

## SVC: Service model

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| CSDM-SVC-001 | must | A Business Service and a Technology Management Service are each single level: neither forms a hierarchy of services of its own kind. | p. 11, What is a Service? | static |
| CSDM-SVC-002 | should | Every operational Business Service and Technology Management Service has at least one Service Offering. | pp. 43, 45, 54-55 | static |
| CSDM-SVC-003 | should | A CI relates, through Dynamic CI Groups, to only one Technology Management Service and one Technology Management Service Offering. A CI may belong to several Dynamic CI Groups if only one of them is related to a Technology Management Service. Reason given: manager, support and change group data is copied down to the CIs and would be overwritten. | pp. 43-44, Dynamic CI Group | partial |
| CSDM-SVC-004 | must | A Dynamic CI Group contains CIs and cannot contain other groups. | p. 43, Dynamic CI Group | static |
| CSDM-SVC-005 | must | A Dynamic CI Group has a service classification of Application Service or Technical Service, and the classification decides whether it acts as a query-based application service or as a group managed by a Technology Management Service Offering. | p. 44, Dynamic CI Group | static |
| CSDM-SVC-006 | should | Offerings of one service that have different commitments are represented by different service level agreement definitions. | p. 45, Business Service Offering | none |
| CSDM-SVC-007 | should | The offering of an Application Service is exposed through the related Business Service Offering or Technology Management Service Offering. | p. 39, Application Services | partial |
| CSDM-SVC-008 | should | Each distinct deployment of a business application (each environment and region) is represented by its own Application Service. | pp. 11, 54, Crawl Stage | partial |
| CSDM-SVC-009 | note | The Service Classification attribute sits on the parent service table and is inherited by every service type; it is normally filled in from the CI's class. | p. 37, What is Service Classification attribute? | none |
| CSDM-SVC-010 | note | The service instance types added in CSDM 5 (data, connection, network, operational process, facility) are model only: they have no user interface, need manual creation and are not part of event impact analysis. There is no expectation of using them unless local needs require it. | pp. 37-38, Service Instance | none |
| CSDM-SVC-011 | must | The Service Delivery Network is not an entity. It is the set of interconnected Connection Service Instances and Network Service Instances. | pp. 39-41, Service Delivery Network | static |
| CSDM-SVC-012 | note | A single installed Application can support several Application Services; there is no one-to-one relationship between the two. | p. 41, Application | none |
| CSDM-SVC-013 | should | The Application table is not an inventory or portfolio of applications (that is the Business Application table). It holds discoverable instances of code on one host, and manual population is not recommended. | pp. 41, 53 | partial |

## TBL: Table placement

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| CSDM-TBL-001 | must | A Product Model is not a CI, and product model classes are not CMDB classes. A CI points to its Product Model through the model reference, which every CMDB table has. | p. 18, Product (Models) | static |
| CSDM-TBL-002 | must | A Contract is not a CI. | p. 16, Contract | static |
| CSDM-TBL-003 | must | The common data entities (Company, Business Unit, Department, Location, Building, Group, User) are not CIs. | p. 27, Common Data | static |
| CSDM-TBL-004 | must | A CMDB Group is not a CI. | pp. 18-19, CMDB Group | static |
| CSDM-TBL-005 | must | Foundation tables are referential data and are not used in CMDB relationships. Business Process is the exception because it is a CMDB table. (The paper states the first sentence flatly and then draws a CMDB relationship for Business Process; the exception is our reading.) | p. 14, Foundation Domain | static |
| CSDM-TBL-006 | should | A Business Application and an SDLC Component are not operational CIs and should not be used in incident, problem or change. | pp. 53-54, Crawl Stage | runtime |
| CSDM-TBL-007 | note | Records in the Design and Planning and Build and Integration domains are not direct targets of incident, problem and change. Service Delivery and Service Consumption tables are operational and can be selected in them. | pp. 31, 34, 36, 45 | none |
| CSDM-TBL-008 | should | Each entity is stored in the table, with the service classification, that the paper's table mapping gives. The paper says the mapping will continue to evolve. | p. 47, CSDM 5 Table Names and Labels | static |
| CSDM-TBL-009 | note | The service offering table holds both Business Service Offerings and Technology Management Service Offerings; the service classification says which. | pp. 43, 45 | none |
| CSDM-TBL-010 | should | A Business Application's singular reference to a Business Process is legacy from CSDM 5 and is not recommended; relationships that allow one to many exist. | p. 33, Business applications | static |
| CSDM-TBL-011 | note | Business Process, Business Capability and Business Application are manually maintained CIs. Application and infrastructure CIs are normally created by discovery. | pp. 16, 32, 41, 53 | none |

## REL: Relationship use

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| CSDM-REL-001 | should | Use the prescribed relationships and references (the paper's relationship figure) as the main way to link CSDM entities. | p. 7, principle 3; p. 48 | static |
| CSDM-REL-002 | should | Use the prescribed relationships between the CIs. If they are missing (for example Business Application uses Application Service), functions such as technology portfolio risk assessment will not work. | p. 48, Relationships in CSDM | static |
| CSDM-REL-003 | should | When mapping infrastructure relationships by hand, create the relationships that discovery would create. | p. 48, Relationships in CSDM | none |
| CSDM-REL-004 | should | Create a CI relationship between each Business Capability and its Business Applications, and between Business Applications and their Application Services. | p. 31, Business capabilities | static |
| CSDM-REL-005 | note | A Business Application is manually managed, so its relationships to deployed instances (Application Services) are created by hand. | p. 32, Business applications | none |
| CSDM-REL-006 | note | Impact analysis follows relationships in the reverse direction. The relationship type is for the most part not critical, but should be followed. | p. 48, Relationships in CSDM | none |
| CSDM-REL-007 | note | Not every CSDM object is a CMDB table and not every object has relationships. | p. 48, Relationships in CSDM | none |
| CSDM-REL-008 | should | A Business Application relates to Application Services, and not to any other type of Service Instance. | docs, CI relationships | static |

## HIER: Hierarchy and data quality

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| CSDM-HIER-001 | must | A Business Capability hierarchy has no more than six levels. | pp. 31-32, Business capabilities | static |
| CSDM-HIER-002 | should | A capability hierarchy that seems to need more than six levels is a candidate to be split into several capabilities, the lower levels being processes and tasks rather than capabilities. | p. 31, Business capabilities | none |
| CSDM-HIER-003 | must | Only a leaf Business Capability (one with no children) can be deleted. | p. 32, Business capability update guidance | partial |
| CSDM-HIER-004 | must | A Business Capability cannot be its own ancestor: no circular parent relationships. | p. 32, Business capability update guidance | static |
| CSDM-HIER-005 | note | A Business Capability's level is assigned from its parent and recalculated when the parent changes. | p. 32, Business capability update guidance | none |
| CSDM-HIER-006 | must | A Location flagged as a duplicate names a primary Location. | p. 28, Location Management | static |
| CSDM-HIER-007 | should | Internal Company entries form a hierarchy of legal entities, not of business units. | p. 51, Foundation Stage | none |
| CSDM-HIER-008 | note | Registering an Application Service lets administrators define uniqueness and required fields for the first record, before choosing how it is populated. | p. 39, Application Services | none |

## LCY: Life cycle

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| CSDM-LCY-001 | must | Life Cycle Stage and Life Cycle Stage Status are two attributes on every CI; together they uniquely specify an object's status. | pp. 19-20, CSDM Life Cycle | partial |
| CSDM-LCY-002 | must | Life cycle stages and stage statuses are provided by ServiceNow and are not editable. | p. 20, CSDM Life Cycle | none |
| CSDM-LCY-003 | must | An object takes only the stage and status values of its own life cycle process: product, tangible, intangible, document or location. | pp. 20-27, Life Cycle Processes | static |
| CSDM-LCY-004 | note | Adopting the new life cycle fields is optional. A mapping from the legacy status attributes is available, and after the Xanadu family release there is no ongoing synchronization with them. | p. 20, CSDM Life Cycle | none |
| CSDM-LCY-005 | should | Evaluate dependencies on the legacy status attributes before enabling the new life cycle fields, and test the new product-instance synchronization in non-production first, because turning it off again may lose data. | p. 20, CSDM Life Cycle | none |

## ADOPT: Adoption and migration

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| CSDM-ADOPT-001 | should | Adopt CSDM in stages (Foundation, Crawl, Walk, Run, Fly) rather than implementing every part at once. | p. 51, How to adopt the CSDM standard | none |
| CSDM-ADOPT-002 | should | Foundation stage: populate Company, Business Unit, Department, Location, Group, User, CMDB Group, Product Models and Contracts first. | pp. 51-53, Foundation Stage | partial |
| CSDM-ADOPT-003 | should | Crawl stage: Business Application, Application Service, Application (discoverable) and server or host (discoverable). SDLC Component is optional here and can wait for the Fly stage. | pp. 53-54, Crawl Stage | partial |
| CSDM-ADOPT-004 | should | Walk stage: Technology Management Service, Technology Management Service Offering and Dynamic CI Group. | pp. 54-55, Walk Stage | partial |
| CSDM-ADOPT-005 | should | Run stage: Service Portfolio (not a CMDB table), Business Service and Business Service Offering. | pp. 55-56, Run Stage | partial |
| CSDM-ADOPT-006 | should | Fly stage: Request Catalog, Business Capability and Information Object. The Information Object may be needed sooner if requirements say so. | pp. 56-57, Fly Stage | partial |
| CSDM-ADOPT-007 | should | Migrating from a nonconforming table: back up the data; map attributes (best practice, keep, refactor, do not need); identify every dependency on the old table in reports, rules and scripts; refactor attributes; then migrate and fix the dependencies. Moving a CI to another class can lose data held in attributes outside the new table hierarchy. | pp. 58-59, Migrating into CSDM | none |

## PRIN: Principles and scope

| Id | Strength | Rule | Section | Checkable |
|---|---|---|---|---|
| CSDM-PRIN-001 | should | Agreed CSDM definitions are used wherever a table, reference or attribute is used. | p. 7, principle 5 | none |
| CSDM-PRIN-002 | note | Ten principles guide CSDM: simplified concepts; designed for reporting and analytics; prescriptive relationships; a data model shared across products; agreed definitions; shared tables supplied by default; consistent data integrations; limited upgrade impact; data governance and process; documented product guidance. | p. 7, CSDM Key Principles | none |
| CSDM-PRIN-003 | note | CSDM is not a product, an implementation guide, a set of reports, code to install or an automatic fix for past implementations. The core tables need no purchase, though plugins may be needed for some elements. | p. 3, CSDM Introduction | none |
| CSDM-PRIN-004 | note | The model is designed to be extended; for example a customer can add a service classification value. | p. 10, CSDM Conceptual Model | none |

Total: 56 rules.
