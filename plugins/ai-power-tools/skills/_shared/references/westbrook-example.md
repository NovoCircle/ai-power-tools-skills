# Westbrook Bank - canonical example specification

Westbrook Bank is the fictitious organization used in every example, walkthrough, test fixture
and demo across the AI Power Tools skills. It exists so that no real customer's name, model or
metamodel shape ever ships.

**Read this file before writing a new example. Do not invent a parallel vocabulary.**

Ground truth is the MDG technology file `WBA_MDG.xml` and the model `WestbrookBank.qea` in the
Westbrook demo directory. Where this document and that file disagree, the file wins and this
document is the bug.

---

## 1. The name slots

Several different things are easy to confuse. They are not interchangeable.

| Slot | Value | Where it appears |
|---|---|---|
| Organization | Westbrook Bank | Prose, narrative, element notes |
| MDG technology id | `WBA` | The `id=` attribute of `<MDG.Technology>`; what EA registers and what `get_mdg_from_runtime` reports |
| Technology display name | `WestbrookBankArchitecture` | User-facing technology name; the key used in the server's language tables |
| Full technology title | `WBA (Westbrook Bank Architecture)` | The `name=` attribute of `<MDG.Technology>` |
| Stereotype namespace prefix | `WBA` | Every qualified stereotype: `WBA::WBABusinessApplication` |
| Model file | `WestbrookBank.qea` | Every path example |
| Conformance rule id prefix | `WBA-` | Ruleset rule ids, e.g. `WBA-APP-001` |

Note the deliberate doubling in `WBA::WBABusinessApplication`. The namespace is `WBA` and every
stereotype name also begins with `WBA`. That is what the MDG actually declares. Do not "correct"
it to `WBA::BusinessApplication`.

Both `WBA` and `WestbrookBankArchitecture` are accepted as installed-technology identifiers by
the server. When an example needs one value, prefer `WBA` for anything EA-facing (stereotype
references, MDG lookups, SQL against `t_object.Stereotype`) and `WestbrookBankArchitecture` for
anything presented to a person as the language name.

---

## 2. Element stereotypes - all 14

This is the complete set. There are no others. If an example needs a concept that is not in this
table, use the closest entry rather than inventing a new stereotype.

| Stereotype | Alias | EA metaclass | Tag set |
|---|---|---|---|
| `WBABusinessApplication` | Business Application | Component | base |
| `WBABusinessService` | Business Service | Component | base |
| `WBAVendorSystem` | Vendor System | Component | base |
| `WBARegulatedFunction` | Regulated Function | Component | base |
| `WBASystemOfRecord` | System of Record | Component | base |
| `WBAAIGateway` | AI Gateway | Component | base + AI |
| `WBAAIService` | AI Service | Component | base + AI |
| `WBAAIModel` | AI Model | Class | base + AI |
| `WBADataAsset` | Data Asset | Class | base |
| `WBADataEntity` | Data Entity | Class | base |
| `WBAGovernedElement` | Governed Element | Class | base |
| `WBARegulatedActivity` | Regulated Activity | Activity | base |
| `WBACustomerTouchpoint` | Customer Touchpoint | Activity | base |
| `WBAExternalCall` | External Call | Activity | base |

Metaclass distribution: 7 Component, 4 Class, 3 Activity.

The metaclass matters. An example that creates a `WBAAIModel` must create it as a **Class**, not
a Component - `create_element` with the wrong base type produces an element the MDG will not
recognize and no toolbox will offer.

---

## 3. Tagged values - all 10

Every stereotype carries the **base** set of 6. The three AI stereotypes
(`WBAAIGateway`, `WBAAIService`, `WBAAIModel`) additionally carry the **AI** set of 4.

### Base set (all 14 stereotypes)

| Tag | Type | Permitted values |
|---|---|---|
| `criticality` | enumeration | `Mission-Critical`, `Business-Critical`, `Important`, `Standard` |
| `lifecycle` | enumeration | `Strategic`, `Current`, `Sunset`, `Deprecated`, `Retired` |
| `businessOwner` | String | free text - a team or role, never a real person's name |
| `technicalOwner` | String | free text - a team or role, never a real person's name |
| `dataClassification` | enumeration | `Public`, `Internal`, `Confidential`, `Restricted` |
| `regulatoryScope` | String | free text, e.g. `PCI-DSS`, `GDPR`, `SOX` |

### AI set (WBAAIGateway, WBAAIService, WBAAIModel only)

| Tag | Type | Permitted values |
|---|---|---|
| `modelGovernanceClass` | enumeration | `SR-11-7-Tier-1`, `SR-11-7-Tier-2`, `Internal-Use`, `Experimental` |
| `humanInLoopRequired` | boolean | `true`, `false` |
| `auditLoggingEnabled` | boolean | `true`, `false` |
| `dataResidency` | String | free text jurisdiction, e.g. `EU`, `US-only` |

Enumeration values are exact. `Mission Critical` (space instead of hyphen) is wrong and will fail
a conformance check. `businessOwner` and `technicalOwner` take a team name such as
`Payments Engineering` - putting a person's name there reintroduces exactly the kind of
identifying detail this example exists to avoid.

---

## 4. Diagram stereotypes - all 3

| Diagram stereotype | Alias | diagramID | Toolbox referenced |
|---|---|---|---|
| `WBAApplicationView` | WBA Application Architecture | `WBA-AppView` | `WBA::WBA ArchiMate` |
| `WBAProcessView` | WBA Business Process | `WBA-ProcView` | `WBA::WBA BPMN` |
| `WBADataModelView` | WBA Data Model | `WBA-DataView` | `WBA::WBA UML` |

## 5. Toolbox pages - all 3

`WBA ArchiMate Elements`, `WBA BPMN Elements`, `WBA UML Elements`.

---

## 6. Connector stereotypes

Two different statements, often confused. Both are true.

**(a) The WBA MDG declares no connector stereotypes.** There is no `<Stereotype>` in `WBA_MDG.xml`
that applies to a connector metaclass. An example must not imply the technology ships any.

**(b) The Westbrook demo model nevertheless applies unqualified connector stereotypes.**
EA permits a stereotype string on `t_connector.Stereotype` that comes from no MDG, and the demo
model does exactly that.

Counted from the live model on 2026-09-23:

| Stereotype | Count |
|---|---|
| `Uses` | 16 |
| *(none - plain connector)* | 5 |
| `extends` | 3 |
| `Requires` | 3 |
| `part-of` | 2 |
| `Equivalent` | 2 |
| `realizes` | 1 |
| `Flows` | 1 |

All unqualified. Prefixing any of them `WBA::` would be wrong: the prefix asserts the MDG
declares it, and for connectors the MDG declares nothing.

### The governance rule matches a different set - and that is a real defect

`WBA-LFY-001` flags a connector whose source `lifecycle` is `Strategic` or `Current`, whose
target is `Deprecated`, and whose stereotype is one of:

```sql
WHERE c.Stereotype IN ('Uses', 'ConsumesService', 'Realizes', 'Flows')
```

Compare that with the table above. **Two of those four can never match:**

- `ConsumesService` does not occur in the model at all.
- `Realizes` occurs only as lower-case `realizes`, and the comparison is case-sensitive.

So the rule is effectively checking `Uses` and `Flows` only. It is not wrong in a way that
produces false positives - it silently under-reports, which is the harder kind to notice.

Do not "fix" this by editing either side to match. It is recorded as a defect, and the demo
model's tests assert the current counts, so changing one without the other breaks them.

### What this means when you write an example

- Naming the stereotypes the model actually uses is describing reality, not inventing vocabulary.
  Take them from the table above.
- Do not assume consistent casing. `realizes` and `Realizes` are different strings to SQL, and
  the model contains the lower-case one.
- `extends`, `Requires`, `part-of` and `Equivalent` are informal names that accumulated outside
  any MDG. That is realistic and is useful teaching material about model drift - but describe
  them as drift, never as the technology's vocabulary.

### What is still forbidden

The names `WBA::dependsOn`, `WBA::realizes` and `WBA::mastersData` appear in some existing
skills. They are **not** in the MDG and not in the model. Until that is reconciled, treat them as
follows:

> **Do not confuse `WBA::realizes` with `Realizes`.** They differ only by case and prefix and they
> are opposite cases. `Realizes` - capitalised, unqualified - is a real connector stereotype the
> demo model applies, listed in 6(b) above, and is fine to use. `WBA::realizes` - lower-case,
> MDG-qualified - is fabricated, claims to come from the MDG, and is not. The prefix is the tell:
> a `WBA::` prefix asserts the MDG declares it, and for connectors the MDG declares nothing.

- Do **not** introduce them into new material.
- For relationships between WBA elements, use plain UML connector types - `Dependency`,
  `Realization`, `Association`, `Aggregation` - with no stereotype.
- A skill whose subject *is* adding connector stereotypes to an MDG may show them, but must say
  plainly that they are a proposed extension and not part of the shipped WBA technology.
- The same carve-out covers a **test fixture** that exercises connector-stereotype rules.
  `validate_model`'s connector-endpoint and cardinality rule types read `t_connector.Stereotype`
  directly, so an unstereotyped connector cannot be evaluated by them at all and the feature
  would go untested. Such a fixture reuses these three names rather than inventing a fourth
  vocabulary, and labels them test-only in both the MDG XML and the rules file.

---

## 7. Authoring examples that build an MDG

A skill that teaches MDG authoring must build a **subset of the real WBA technology** - the same
stereotype names, aliases, metaclasses and tagged values given above.

Do not invent a second vocabulary under the `WBA::` namespace. Names such as `WBA::Application`,
`WBA::TechPlatform`, `WBA::BizCapability`, `WBA::DataDomain`, `WBA::RunsOn`, `WBA::Realises` and
`WBA::Integration` are **not** part of this technology. A reader who follows an authoring skill
and then a modeling skill must end up with one coherent artifact, not two that contradict each
other under the same prefix.

Note also the spelling: `Realization` / `realizes`, not `Realises`.

---

## 8. Path placeholders

Never write an absolute local path. Use these forms:

| Instead of | Write |
|---|---|
| a real model path | `<model-dir>\WestbrookBank.qea` |
| a real MDG path | `<mdg-dir>\WBA_MDG.xml` |
| a user profile path | `%APPDATA%\...` or `%USERPROFILE%\...` |
| a generic user home | `C:\Users\<you>\...` |

## 9. Rule ids

Conformance rule ids are prefixed `WBA-` and grouped by subject:
`WBA-APP-001`, `WBA-AI-001`, `WBA-DATA-001`, `WBA-GOV-001`, `WBA-LFY-001` (lifecycle),
`WBA-TV-001` (tagged values), `WBA-REL-001` (relationships), `WBA-CNX-001` (connectors).

The prefix is not optional. A bare `LFY-001` reads as an identifier from somewhere else and will
not match the demo model's tests, which use the fully qualified form.

---

## 10. Checklist before you ship an example

- [ ] Every stereotype named appears in the section 2 table, spelled exactly.
- [ ] Every stereotype is created against the metaclass that table gives it.
- [ ] Every tagged value appears in section 3, and enumeration values match exactly.
- [ ] AI-only tags are used only on `WBAAIGateway` / `WBAAIService` / `WBAAIModel`.
- [ ] No connector stereotype is used (see section 6).
- [ ] An MDG-authoring example builds a subset of the real technology (see section 7).
- [ ] No absolute path, no personal name, no real organization.
- [ ] `businessOwner` / `technicalOwner` hold a team or role, not a person.
- [ ] The qualified form is `WBA::WBAThing`, not `WBA::Thing`.

---

## 11. Known defects in the demo MDG - flag, do not silently fix

Recorded so that nobody "corrects" an example to match a broken source:

1. The `<Documentation notes=...>` string describes the technology as spanning three sub-profiles
   (WBA-ArchiMate, WBA-BPMN, WBA-UML). The file's structure does not reflect that - it declares a
   single flat `UMLProfile`. The stereotype count in that note is correct.
2. The diagram profiles reference toolboxes named `WBA::WBA ArchiMate`, `WBA::WBA BPMN` and
   `WBA::WBA UML`, but the toolbox pages are actually named `WBA ArchiMate Elements`,
   `WBA BPMN Elements` and `WBA UML Elements`. These do not match, so the custom diagrams will
   not bind to their toolboxes in EA.
3. All three toolbox pages declare no items, so they render empty.

These are defects in the demo artifact, not in this specification. Fixing them is separate work.
