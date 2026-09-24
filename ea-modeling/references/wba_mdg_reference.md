# Working with the WBA MDG — Full Detail

Detail supporting [`../SKILL.md`](../SKILL.md) §10. Read that section first for the one-line
rule (confirm the MDG is loaded before tagging); this file carries the verification SQL and the
tag-applicability rule.

---

## Confirm MDG is active before tagging

Before setting any WBA tagged values, confirm the MDG is loaded:
```
ea_analyze(operation="execute_sql", params={"sql": """
    SELECT * FROM t_document
    WHERE DocType = 'MDGXml' AND DocName = 'WestbrookBankArchitecture'
"""})
```

If the result is empty, the MDG has not been imported into the model. Import it with the
`ea-mdg-deploy` skill before proceeding.

## Tagged value namespace confirmation

The first successful `ea_model(operation="set_tagged_value", ...)` response will include the fully-qualified tag name,
e.g. `WestbrookBankArchitecture::WBAVendorSystem::criticality`. This confirms the MDG is
active and the tag schema is being honoured.

## MDG stereotype → allowed tags

The rule is simpler than a per-stereotype matrix suggests: the **base set of 6** tags
(`criticality`, `lifecycle`, `businessOwner`, `technicalOwner`, `dataClassification`,
`regulatoryScope`) applies to **all 14** WBA stereotypes. The **AI set of 4**
(`modelGovernanceClass`, `humanInLoopRequired`, `auditLoggingEnabled`, `dataResidency`)
applies **only** to the three AI stereotypes: `WBAAIGateway`, `WBAAIService`, `WBAAIModel`.
See `_shared/references/westbrook-example.md` section 3 for the canonical list — this file
does not repeat it so there is exactly one source of truth for tag names and enum values.

> **Canon fix made during the 2026-09-23 split:** this section previously carried a
> per-stereotype checkmark matrix covering only 6 of the 14 stereotypes, using the tag names
> `humanInLoop` / `auditLogging` (canon: `humanInLoopRequired` / `auditLoggingEnabled`), and
> incorrectly marking `modelGovernanceClass` as applicable to non-AI stereotypes
> (`WBABusinessApplication`, `WBAVendorSystem`, `WBABusinessService`, `WBADataAsset`). It also
> listed `vendor`, `product`, `pciScopeJustification`, and `pciControlOwner`, none of which are
> part of the canonical 10-tag WBA set. That matrix has been replaced with the rule above, which
> matches canon exactly. Nothing was silently dropped — the corrected content is captured here.
