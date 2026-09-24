---
name: ea-change-management
description: Manage baselines and change history in a Sparx EA repository via ea_repository and ea_analyze — when to baseline (whole model vs. one package), how to read a compare_baseline diff, the destructive behavior of apply_baseline and how to protect against it, and using get_updates_in_range / get_user_activity to answer "what changed, when, and by whom." Use before a risky bulk edit or MDG/ruleset rollout, when asked to snapshot, diff, or roll back model state, or when investigating recent changes or an editor's activity in a Sparx EA model.
---

# EA Change Management — Baselines and Audit History

*Tools: `ea_repository` (baseline operations) and `ea_analyze` (audit-trail operations),
AI Power Tools for Sparx EA v2.1.0+*

Run the `ea-start-here` preflight first — confirm the right repository is open before touching
baselines. A baseline captured against, or applied to, the wrong model is a wasted afternoon at
best.

## When to use

- Before a bulk edit, import, or MDG/ruleset rollout you might need to undo.
- To find out what changed in a package or the whole repository over a time window, and who
  changed it.
- To compare current state against a known-good snapshot before deciding whether to keep a change.
- **Not** for source-controlled model files (`.xml`/`.eaxmi` exports under version control) —
  that's a different workflow. This skill covers EA's own baseline mechanism, stored inside the
  `.qea`/`.eap` file itself.

## Operations at a glance

| Operation | Call | What it does |
|---|---|---|
| Create a baseline | `ea_repository(operation="create_baseline", params={"package_id": ..., "version": ..., "notes": ...})` | Snapshots a package subtree into the repository as a compressed document. |
| List baselines | `ea_repository(operation="list_baselines", params={"package_id": ...})` | Lists snapshots taken against that package. |
| Compare to a baseline | `ea_repository(operation="compare_baseline", params={"package_id": ..., "baseline_guid": ...})` | Diffs current package state against a named snapshot. Read-only. |
| **Apply a baseline** | `ea_repository(operation="apply_baseline", params={"package_id": ..., "baseline_guid": ...})` | **Overwrites current package content with the snapshot.** See the warning below before you call this. |
| Updates in a time window | `ea_analyze(operation="get_updates_in_range", params={"start": ..., "end": ..., "kind": ...})` | Repository-wide list of elements/packages/diagrams created or modified in `[start, end]`. |
| Activity by user | `ea_analyze(operation="get_user_activity", params={"start": ..., "end": ...})` | Repository-wide edit counts grouped by the author who made them. |

`create_baseline` and `apply_baseline` are writes. `list_baselines`, `compare_baseline`,
`get_updates_in_range`, and `get_user_activity` are reads.

---

## 1. Baselining — the decision, not just the call

A baseline is a full snapshot of one package's subtree, stored as a compressed document inside
the repository file itself (`t_document`, `DocType='Baseline'`). The scope is always **the whole
subtree under `package_id`**, whether that's one small domain package or the entire model root —
there is no partial-subtree baseline.

Pick scope by what you're protecting against, not by habit:

| Situation | Baseline scope |
|---|---|
| About to run a repository-wide MDG upgrade, bulk import, or model-wide cleanup | The model root package |
| About to restructure or bulk-edit one domain (e.g. a single business-area package) | That package only — faster to create, faster to compare, and the diff stays readable |
| Scheduled/periodic audit snapshot | The model root, on a cadence, so `get_updates_in_range` between two baselines tells the full story |
| Handing a package to another team or tool to edit | That package, immediately before the handoff — gives you a clean "before" to diff against later |
| Trying out an MDG or ruleset change | A dedicated scratch package, never a real content package — see §3 |

Package-level baselines are cheaper and easier to reason about: a diff against a 20-element
package is something you can actually read, where a diff against the whole model is not. Default
to the narrowest package that contains the change you're protecting against, and reserve
whole-model baselines for whole-model operations.

Every baseline adds a blob to the repository file. Baselining large subtrees frequently grows the
`.qea` file; if that matters, check size with SQL before making it a habit:

```sql
SELECT DocID, DocName, LENGTH(BinContent) AS bytes
FROM t_document WHERE DocType = 'Baseline'
```

`list_baselines` returns `version` and `notes` intact, but `date` and `author` come back empty —
don't build logic that depends on them being populated. If you need authoritative baseline
metadata, query `t_document` directly.

---

## 2. Reading a `compare_baseline` result

`compare_baseline(package_id, baseline_guid)` is read-only — it does not touch model content, so
it's safe to run at any time, including against a package you don't own, to answer "has anything
changed since this snapshot."

Conceptually it reports the difference between the package's current state and the named
baseline: elements/connectors/diagrams added since the snapshot, ones removed, and ones whose
attributes or tagged values changed. Read it as three buckets — **added**, **removed**,
**modified** — and for anything in the modified bucket, check which tagged values moved, not just
that the element changed. A `criticality` flip from `Business-Critical` to `Standard` and a typo
fix in `notes` both show up as "modified"; only the diff detail tells them apart.

> **If `compare_baseline` appears to hang, look at EA's screen.** EA reports an unrunnable
> query as a modal dialog that holds the COM connection until someone clicks OK, so every
> later call appears to hang too. See
> [`../_shared/references/ea-ui-verification.md`](../_shared/references/ea-ui-verification.md).

---

## 3. `apply_baseline` — the most destructive operation in this set

`apply_baseline(package_id, baseline_guid)` **overwrites the current content of `package_id` with
the baseline's snapshot.** The server's own response includes this warning verbatim:

> "this operation overwrites current model content with the baseline state"

That means, plainly: **every element, connector, diagram, and tagged-value change made in that
package since the baseline was taken is discarded**, including work by other people, not just
yours. It is not a merge and not a selective revert — it replaces the subtree wholesale.

**Never call `apply_baseline` against a package you did not baseline yourself for this purpose.**
On a shared repository, a package-level apply can silently erase a colleague's concurrent edits
with no separate confirmation step. Treat every `apply_baseline` call as irreversible unless you
have already taken the precaution below.

### Before you call it

1. **Take a fresh baseline of the current state first**, even if you're sure you want to revert.
   That's your undo for the undo — without it, reverting a bad revert means reconstructing content
   by hand.
2. **Re-confirm `package_id` and `baseline_guid` immediately before the call** — re-run
   `list_baselines` and `get_repository_info`. Applying the right snapshot to the wrong package
   (or vice versa) is the expensive version of this mistake.
3. **Coordinate with anyone else working in that package.** Reads are safe to run anytime; this
   write is not.
4. **After the call, verify explicitly** — query the package's contents with
   `ea_analyze(operation="execute_sql", ...)` or `ea_model(operation="list_elements_in_package", ...)`
   rather than trusting the response alone. See §4: a failed-looking response is not proof nothing
   happened, and a success-looking one deserves the same read-back.

`apply_baseline` does not restore. It reports `baseline_restore_not_applied` and changes nothing
— see §4 for what to do instead. Verify the package contents either way rather than trusting the
response.

---

## 4. Failure modes hit during verification

All four found while verifying this skill against a live, small (2-element) scratch package —
not edge cases from a large or unusual repository.

- **A call that appears to hang is usually a modal dialog**, not a slow operation. EA raises
  one for any SQL its backend cannot run, and it holds the COM connection until dismissed.
  Look at the screen before retrying — see
  [`../_shared/references/ea-ui-verification.md`](../_shared/references/ea-ui-verification.md).
- **`apply_baseline` does not currently restore.** It runs without error and reports
  `baseline_restore_not_applied` when the package still differs from the baseline, rather
  than claiming a success it did not achieve. **Restore through EA's UI instead** — right-click
  the package ▸ Package Control ▸ Baselines ▸ select ▸ Restore — which is drivable with
  computer use.
- **`get_updates_in_range` / `get_user_activity` silently return zero rows for ISO-8601
  timestamps.** Both expect `start`/`end` as `YYYY-MM-DD HH:MM:SS`, matching how
  `t_object.CreatedDate`/`ModifiedDate` are actually stored — not `2026-09-23T00:00:00Z`. Passing
  the ISO form is **not an error**; it just returns an empty result set, which reads exactly like
  "nothing changed in that window." Confirmed reproducible on both operations. Always use the
  space-separated form.
- **Neither audit operation takes a `package_id`.** Both are repository-wide. To answer a
  package-scoped question, filter the returned items by `package_id` client-side, or query
  `t_object`/`t_package` directly with `execute_sql` and a `WHERE Package_ID = ...` clause.

---

## 5. Audit trail — what changed, when, and by whom

Two read-only, repository-wide operations answer complementary questions.

```python
# What was created or modified in this window?
ea_analyze(operation="get_updates_in_range", params={
    "start": "2026-09-23 00:00:00",
    "end": "2026-09-23 23:59:59",
    "kind": "elements",   # default; also valid: "packages", "diagrams"
})

# Who was active, and how much did each person touch?
ea_analyze(operation="get_user_activity", params={
    "start": "2026-09-23 00:00:00",
    "end": "2026-09-23 23:59:59",
})
```

`get_updates_in_range` returns one row per changed item (`kind`, `id`, `name`, `type`,
`package_id`, `modified`). `kind="elements"` (the default) includes packages alongside ordinary
elements — packages are objects too, in EA's terms. `kind="connectors"` is **not** a valid value;
connector-level history isn't tracked by this operation.

`get_user_activity` returns one row per author with `elements_modified`, `diagrams_modified`, and
`last_active`. The `author` value is the raw EA/Windows login that made the edit, not a chosen
display name — handle it like any other personal identifier: fine to read inside your own
repository for audit purposes, but don't copy it verbatim into shared tickets, documentation, or
examples.

Combine the two: `get_user_activity` tells you *who* to ask about a window of change,
`get_updates_in_range` tells you *what* they touched, and (once verified in your environment)
`compare_baseline` against a snapshot from before that window tells you exactly what changed on
each item.

---

## See also

- [`../_shared/references/latency.md`](../_shared/references/latency.md) — wait/screenshot
  guidance if verifying a baseline or revert through the EA desktop UI rather than by query.
- `ea-start-here` — session preflight; run it before any of the writes in this skill.
- `ea-mdg-model-build` — a different, heavier-weight use of "baseline" (renaming and locking a
  protected package root before an MDG rebuild). Same EA feature, different purpose; don't
  conflate the two.
- [`references/worked-example.md`](references/worked-example.md) — a full create → change →
  audit → clean-up walkthrough against Westbrook Bank elements.

## Verify in EA's UI

EA reports success it has not earned, and reports failure as a modal dialog that blocks the
COM connection rather than as an error you can catch. Neither shows up in a tool response.

- **If a call seems to hang, screenshot EA and read the dialog before concluding anything.**
  It names the cause. Dismiss from the front — dialogs stack, and a later call can be queued
  behind one raised by an earlier one. Windows reporting EA as "Responding" means nothing.
- **After any diagram create or edit, reload the diagram, screenshot it, and look.**
  `ok: true` means rows were written, not that elements landed where you intended, that
  styling applied, or that the result is readable.
- **Without computer use**, say so and ask the user to look — never report a hang you have
  not diagnosed or a diagram you have not seen.

Full procedure: [`../_shared/references/ea-ui-verification.md`](../_shared/references/ea-ui-verification.md)
