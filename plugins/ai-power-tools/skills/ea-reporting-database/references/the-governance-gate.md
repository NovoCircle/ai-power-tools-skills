# The governance gate

Everything here was run against a live repository before it was written down. The figures come
from the Westbrook Bank reference model and are there to show the *shape* of an answer, not as
numbers to expect.

---

## 1. What problem this solves

An element with no stereotype lands in no entity table, so it is not in the reporting database.
That is correct behavior — the database's tables are the business vocabulary, and an element
carrying no vocabulary term has no table to go in.

It becomes a problem when the element carries governance data anyway. On the reference model
three Components carry the complete tag set:

```
Client Reporting Platform     criticality=Business-Critical   regulatoryScope=GLBA
Portfolio Analytics Engine    lifecycle=Current               dataClassification=Confidential
Rebalancing Service           businessOwner / technicalOwner set
```

Somebody classified these deliberately. No report will ever show them, because the element
carries the data but not the stereotype that routes it to a table. **Lead with these.** An
untagged, unstereotyped element is merely undrawn; a tagged one is a governance gap.

---

## 2. Mapping the extract's rows

The modules speak the frame's column names and the extract speaks EA's, so the caller maps
between them. This is deliberate: it keeps `governance_gap` pure and free of any knowledge of
`t_object`.

```python
path_by_id = {int(p["Package_ID"]): p.get("Name", "") for p in packages}
guid_by_id = {int(o["Object_ID"]): o["ea_guid"] for o in objects}

elements = [{
    "ea_guid":      o["ea_guid"],
    "name":         o.get("Name") or "",
    "metaclass":    o.get("Object_Type") or "",
    "stereotype":   o.get("Stereotype") or "",
    "package_id":   int(o.get("Package_ID") or 0),
    "package_path": path_by_id.get(int(o.get("Package_ID") or 0), ""),
} for o in objects]

tags = [{
    "ea_guid": guid_by_id.get(int(p["Object_ID"]), ""),
    "tag":     p.get("Property") or "",
    "value":   p.get("Value") or "",
} for p in props]
```

Prefer the materialized `pkg.path` over the bare package name for `package_path` when you have
already built the frame — a customer reading "Investment Services" cannot tell which of two
similarly named packages is meant.

`find_ungoverned` skips `Package` elements by default. EA stores every package twice — once in
the package tree and once as an object so it can sit on a diagram — and nobody stereotypes the
object twin.

---

## 3. The three outcomes, and why they must stay apart

### `no_candidate` — there is nothing to apply

The loaded technology extends no stereotype for that element's metaclass, so no stereotype can
legally be applied to it. On the reference model this is **15 Nodes** — cloud platforms,
database platforms, infrastructure — because the technology extends `Component`, `Class` and
`Activity` only.

The useful answer here is not a suggestion. It is:

> Your technology defines no stereotype for a Node. Fifteen infrastructure elements therefore
> cannot be included. Either extend the technology to cover them, or accept the exclusion.

Extending the technology is `ea-mdg-model-build`'s job, and generating one from what a
repository already contains is exactly what that capability does.

**Never invent a suggestion here.** Applying a stereotype whose base metaclass does not match is
the documented way to get EA to accept the write and silently drop it — `update_element` warns
about precisely this.

### `ranked` — one candidate is backed by evidence

A suggestion is only made when something in the repository distinguishes one candidate. The
signal that does this in practice is **package locality**: what stereotype do the element's
stereotyped neighbors carry?

On the reference model the three governed Components sit in a package whose other three
stereotyped elements are all `WBAVendorSystem`. That is a suggestion with a stated basis, and
the `reason` field carries it:

```
3 stereotyped element(s) in the same package carry 'WBAVendorSystem', and no other
candidate for metaclass Component is backed by that evidence.
```

Offer it **with the reason**. Do not present it as certain — it is evidence, not proof, and the
customer knows their model.

### `unrankable` — several candidates, nothing to separate them

Say so and ask. Do not pick one.

This is not a weakness in the implementation, it is a property of most technologies. On the
reference technology **twelve of the fourteen stereotypes declare an identical six-tag set**, so
tag overlap scores five plausible Component stereotypes at exactly 1.0. Choosing the
alphabetically first would be a guess wearing a number.

---

## 4. Applying a stereotype

**Take a baseline first.** This is the only step in the whole skill that writes to the
customer's model, and a bulk stereotype application across a repository is exactly the change
`ea-change-management` exists to make reversible.

```python
ea_model(operation="update_element",
         params={"element_id": 34206,
                 "properties": {"StereotypeEx": "WBAVendorSystem"}})
```

### Pass the bare name

Measured 2026-10-02 on EA build 1716, with the technology loaded. Both the bare name
(`WBAVendorSystem`) and the qualified form (`WestbrookBankArchitecture::WBAVendorSystem`)
produce an identical, **profile-bound** application: EA resolves the name against the loaded
technology and writes the full `FQName` into `t_xref` itself.

```
@STEREO;Name=WBAVendorSystem;GUID={...};FQName=WestbrookBankArchitecture::WBAVendorSystem;@ENDSTEREO;
```

This matters because the census counts an application as the technology's only when `FQName` is
present. A bare-name write that produced an ad-hoc application would leave the element out of
its entity table after all, and the build would look like it had failed to apply anything.

Verified end to end: applying the bare name to two scratch Components moved the
`WBAVendorSystem` census count from 35 to 37, and both elements were placed under
`WestbrookBankArchitecture::WBAVendorSystem`.

### When the technology is not loaded

The resolution above depends on the technology being loaded in the session. If it is not, EA has
nothing to resolve the bare name against and will record an ad-hoc application — the stereotype
name with no `FQName` — which the census will report as ungoverned drift rather than placing it
in a table.

So before applying anything, confirm the technology is loaded. `ea-mdg-assess` distinguishes
installed, embedded and loaded, which are four different states and are routinely confused.
`IsTechnologyLoaded` is the test; the presence of a row in `t_trxtypes` is not.

### Verify, do not assume

`update_element` returns `ok: true` and a `stereotype_warning` field. `ok` does not mean the
stereotype landed. After applying, re-run the census and confirm the element is placed:

```python
census.placement.get(guid)   # -> ['WestbrookBankArchitecture::WBAVendorSystem']
```

---

## 5. If the customer declines

Declining is a valid answer, not an error. Say plainly what the consequence is, then build the
database without them:

> Six elements will not appear in the reporting database, three of which carry governance
> tagged values including one marked GLBA.

Record the counts with the build so the database can answer later what was left out and whether
a human was asked. A database that cannot say what it excluded invites the reader to assume it
excluded nothing.
