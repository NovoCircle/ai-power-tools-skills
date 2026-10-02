# AI Power Tools — Shipped Skills Library

Canonical, version-controlled set of Claude skills for **[AI Power Tools
for Sparx EA](https://github.com/NovoCircle/ai-power-tools-releases)** —
the MCP server that drives Sparx Systems Enterprise Architect via COM.

This library covers **Sparx Enterprise Architect only**. [AI Power Tools for Microsoft
Visio](https://github.com/NovoCircle/ai-power-tools-visio-releases) is a separate product and
ships its skills separately, with its own manifest, installer and release cadence. Nothing is
shared between them, and no Visio skill is ever installed from here.

## How to install

One plugin. It carries these skills **and** the AI Power Tools MCP server, so there is a
single thing to install and a single thing to update.

```
claude plugin marketplace add NovoCircle/ai-power-tools-skills
claude plugin install ai-power-tools@novocircle
```

Restart Claude afterwards: plugin changes are staged, not applied to a running session.

That works on every surface Claude offers — the CLI, the desktop Code tab, VS Code, Claude
Desktop chat and Cowork. Plugins are the only mechanism all of them load.

You still need Enterprise Architect installed on the same Windows machine. The server drives
EA over COM, so it has to run where EA runs. A Cowork session in the cloud reaches it through
Claude Desktop on your workstation — that relocates the conversation, not EA.

In Claude Desktop you can instead download `ai-power-tools.plugin` from the
[latest release](https://github.com/NovoCircle/ai-power-tools-skills/releases/latest) and
upload it in the app. That copy is per machine and does not update itself; the marketplace
does.

### Coming from `install_skills`?

Before 3.5.0 the skills arrived through the `install_skills` MCP tool, which copied them into
`~/.claude/skills`. The plugin supersedes that, and `install_skills` now declines rather than
writing a second copy — a machine carrying both loads every skill twice, once unprefixed and
once as `ai-power-tools:<name>`, because they are different sources and nothing deduplicates
across them.

To clear the older copies, download **`migrate-to-plugin.ps1`** from the
[latest server release](https://github.com/NovoCircle/ai-power-tools-releases/releases/latest)
and run it:

```powershell
.\migrate-to-plugin.ps1 -WhatIf     # show what would go, change nothing
.\migrate-to-plugin.ps1             # list it, then ask before removing
```

It prints the skills it would remove, names the ones it will **not** touch, and does nothing
until you type `YES`.

**Do not delete `~/.claude/skills` by hand.** It may also hold skills for AI Power Tools for
Microsoft Visio — a separate product with its own installer — and any skills you wrote
yourself. The script knows the difference because it reads the installer's own record of what
it wrote; a directory listing cannot tell them apart. Anything you edited locally is backed up
before removal.

This is a one-time job, which is why it ships as a script rather than living in the product.

### Version

The skills, the MCP server and the VS Code extension share one version and ship together, so
there is one number to reason about rather than three.

## What's in the bundle

Nineteen skills, plus the `_shared` reference directory. `manifest.json` is the authoritative
list — the groupings below are for reading, not for machines.

Start with **`ea-start-here`**. It runs a short session preflight and routes to the right skill,
which is quicker than choosing from the list below.

### Core

| Skill | Purpose |
|---|---|
| `ea-start-here` | Entry point — session preflight, then routing to the right skill |
| `ea-modeling` | Build EA models via the MCP server — build order, defects, verification |
| `ea-navigation-diagrams` | Click-through "navigation diagrams" over hierarchical data |
| `ea-help` | Fallback for a task no skill covers — find the procedure in Sparx's user guide for the running EA version, drive it, verify it |
| `ea-diagnostic` | Produce a structured diagnostic report for support |

### Diagrams

| Skill | Purpose |
|---|---|
| `ea-diagram-advisor` | Which diagram type and viewpoint expresses what the reader wants to understand, from measured content |
| `ea-diagram-composition` | Compose a diagram that reads as deliberate — layout grammar, geometry, styling, then verify and lint |

### MDG technologies

| Skill | Purpose |
|---|---|
| `ea-mdg-assess` | Work out what language situation a repository is actually in, before acting |
| `ea-mdg-author` | Author MDG Technology XML — stereotypes, tagged values, toolboxes, Quick Linker |
| `ea-mdg-model-build` | Build an MDG from a profile model that already exists in a repository |
| `ea-mdg-deploy` | Deploy an MDG and prove it works |

### Quality

| Skill | Purpose |
|---|---|
| `ea-validation` | Author and run `validate_model` YAML conformance rulesets |
| `ea-ruleset-author` | Build a complete ruleset for a modeling language from scratch |
| `ea-model-hygiene` | Find and fix model decay — orphans, inconsistent usage, safe deletion |
| `ruleset-archimate31` | A shipped ArchiMate 3.1 conformance ruleset for `validate_model` — 27 rules, no `SKILL.md` |

### Lifecycle and reporting

| Skill | Purpose |
|---|---|
| `ea-change-management` | Baselines and change history — what changed, when, by whom |
| `ea-import-export` | XMI interchange, document generation, diagram export to image/SVG/Visio |
| `ea-stakeholder-reporting` | Portfolio roll-ups and business-language output for non-modelers |

### Developer

| Skill | Purpose |
|---|---|
| `ea-com` | Drive EA from Python via the COM API rather than through MCP |

### Shared references

`_shared/references/` installs alongside the skills and is linked from them. It holds the
canonical Westbrook Bank example specification, the generated list of every server operation,
and shared guidance on EA latency and file encoding. It contains no `SKILL.md` and does not load
as a skill.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `install_skills` returns `error: "fetch_failed"` | GitHub unreachable, or no network | Retry. The source is always `releases/latest` on this repo |
| Files were written but Claude does not offer the skills | The host has not re-scanned its skill directory | Restart the host, or toggle the extension off and on again |
| Re-running the install does not pick up newer skill text | A file whose content differs from both this bundle and the installer's own record of what it wrote is treated as yours and preserved, and reported on `skipped_local_edits` | Re-run with `force=True`; the bundled copy then overwrites it. A file you never edited is not listed there — an upgrade of an untouched file is applied |
| `install_skills` returns `error: "server_too_old"` | The server is below the bundle-wide `min_server_version`. The bundle is all-or-nothing, so nothing was written | Upgrade AI Power Tools to the version named in the message, then re-run |
| `install_skills` returns `complete: false` | Some requested file is not in place — see `incomplete_hint` for which of `skipped_incompatible`, `skipped_local_edits` or `errors` accounts for it | Follow the hint. `ok: true` only means the call ran |
| A skill comes back on `skipped_incompatible` | Its `min_server_version` is above the running server | Upgrade the server. The bundle-wide floor is server 3.0.0 |
| A file appears in `errors` with `sha256 mismatch` | The published asset does not hash to `manifest.json` | Nothing to fix locally — the installer refuses a file it cannot verify rather than writing it. Report it |
| Two skills give contradictory guidance on one subject | A pre-2.2.0 install left the old names beside the new ones (`ea-mcp-validation` beside `ea-validation`) | Ask Claude to prune the legacy skills; it dry-runs first, then confirm to apply |
| Skills sit in `%APPDATA%\Claude\skills` and never load | That was the pre-2.2.0 default, and no Claude surface reads it | Prune, then re-run the install. Every target now resolves to `~/.claude/skills` |

For anything not in this table, ask Claude to run `ea-diagnostic` and send the report to
help@novocircle.com.

## Manifest

`manifest.json` is the authoritative listing of skills, versions, and
per-file SHA-256 hashes. The MCP installer reads it on every run to
detect updates and skip unchanged files.

Per-skill fields:

* `name` — folder name in this repo and in the customer's skill dir
* `title`, `description` — buyer-readable
* `version` — bump when the skill content materially changes
* `min_server_version` — earliest AI Power Tools version that can use
  this skill (gates skills that reference tools added in newer releases)
* `files` — paths relative to repo root
* `sha256` — per-file hash; installer uses these to short-circuit the
  download for unchanged files

Bundle-level fields:

* `bundle_version` — independent of the product version; bumps on every
  published release of this repo
* `min_server_version` — bundle-wide floor, enforced **all or nothing**:
  a server below it receives no files at all and
  `error: "server_too_old"` naming the version needed. The bundle is
  built, tested and released as a set, so half of it is not a smaller
  version of it — it is skill documents describing operations the
  binary does not have. Separate from the per-skill field above, which
  is the finer-grained statement used by bundles that set a lower
  bundle floor

## Release process

The skills, the MCP server and the VS Code extension ship **together, on one version**. A
release is one number across both repositories, not a skills release that happens to coincide
with a server one.

```
python tools/regen-manifest.py     # refresh the sha256 map
python tools/gate.py               # release blocker if red
python tools/build-plugin.py       # emits dist/ai-power-tools.plugin
python tools/publish-bundle.py                 # stage + verify, publishes nothing
python tools/publish-bundle.py --publish vX.Y.Z --notes-file docs/release-notes/X.Y.Z.md
python tools/publish-bundle.py --verify-published
```

`publish-bundle.py` exists because the folklore version of this failed: the bundle reached
2.0.0 through 2.3.0 on `main` and **no 2.x release was ever cut**, so `install_skills` kept
serving 1.4.1 for weeks against a 2.3.0 server. The script refuses rather than guesses, and
`--verify-published` re-fetches the release from outside and re-hashes it, because a bundle
whose bytes do not match its manifest is rejected by every customer's installer and there is
no other way to find out.

Three files carry the version and must agree — `manifest.json`'s `bundle_version`,
`plugins/ai-power-tools/.claude-plugin/plugin.json`, and the `ai-power-tools` entry in
`.claude-plugin/marketplace.json`. `tools/build-plugin.py` refuses to build when they differ,
so drift fails at build time rather than reaching a customer as two numbers for one product.

### Ordering across the two repositories

The plugin references the server's `.mcpb` by a **pinned** release URL, so the server release
has to exist first:

1. Release the server from `NovoCircle/ai-power-tools` (`build.py --publish`), which publishes
   the `.mcpb`, the `.vsix` and `migrate-to-plugin.ps1` to `ai-power-tools-releases`.
2. Point `mcpServers` in `plugin.json` at that tag.
3. Release the bundle from here.

Pinned rather than `releases/latest` on purpose: a floating reference would mean a later server
release silently changes which binary every already-installed plugin pulls, including for
customers who installed months ago and changed nothing.

## Versioning policy

- **One version across the product.** The bundle, the plugin, the MCP server and the VS Code
  extension carry the same number and ship together. The binary is sometimes byte-identical
  between two versions, because a skills-only change still bumps it. That is the cost of one
  number, and it is cheaper than explaining three.
- **Per-skill `version`** bumps only when that skill's content changes. It is a record of what
  moved, not a compatibility gate.
- **`min_server_version`** is vestigial for plugin users, since the plugin ships the server it
  was built against and the two cannot disagree. It still matters for machines that have not
  migrated off `install_skills`, where an older server can meet a newer bundle, so the field is
  maintained and the bundle-wide floor is still enforced all-or-nothing.

  The per-skill floor is derived from the skill's own text, not chosen: take every operation
  the skill names, take the release each was introduced in, and the highest is the floor. Left
  to drift it becomes decorative — for bundle 3.0.0, seven entries declared `1.0.0` while their
  text called operations added as late as 3.0.0. Treat the result as a **lower bound**: roughly
  a third of operations are never named in the server `CHANGELOG.md`, so they contribute
  nothing to the maximum. The bundle-wide floor is the guard that does not depend on this being
  right.

## Authoring a new skill

Each skill is a folder under the repo root containing at minimum a
`SKILL.md` with YAML frontmatter:

```markdown
---
name: ea-something
description: One sentence describing when Claude should invoke this skill.
---

# Body of the skill — Markdown.
```

Keep the description tight and trigger-oriented — Claude uses it to
decide whether to invoke the skill. After adding files, regenerate
`manifest.json` and follow the release process above.

### Customer names

Never put a real customer's name, model name, MDG id, stereotype prefix, project
code, or employee name into a skill. Convert every example to Westbrook Bank;
read `_shared/references/westbrook-example.md` before writing a new example
instead of inventing a parallel one. `tools/gate.py` fails the build on
real-customer strings — run it before any release.

## Contributing

Skill content edits are welcome. PRs against this repo are independent
of the binary product's release cycle.

## Related

- [AI Power Tools for Sparx EA](https://github.com/NovoCircle/ai-power-tools-releases) — the MCP
  server these skills drive, and its installer
- [AI Power Tools for Microsoft Visio](https://github.com/NovoCircle/ai-power-tools-visio-releases)
  — the separate Visio product. Its skills are not installed from here

## License

MIT. See [LICENSE](LICENSE).
