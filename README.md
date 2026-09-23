# AI Power Tools — Shipped Skills Library

Canonical, version-controlled set of Claude skills for **[AI Power Tools
for Sparx EA](https://github.com/NovoCircle/ai-power-tools-releases)** —
the MCP server that drives Sparx Systems Enterprise Architect via COM.

This library covers **Sparx Enterprise Architect only**. AI Power Tools for Microsoft Visio has
its own separate skills library, with its own repository, manifest, installer and release
cadence. Nothing is shared between them, and no Visio skill is ever installed from here.

## How to install

If you have AI Power Tools for Sparx EA installed:

> *"Install the AI Power Tools skills."*

Claude calls the `install_skills` MCP tool, which fetches this bundle from `releases/latest` and
copies the skills into `~/.claude/skills`. Re-run it any time to pick up newer versions;
unchanged files are skipped.

**Bundle 2.0.0 requires server 2.2.0 or later.** Several skills document operations that are
broken or absent in earlier servers, so installing 2.0.0 against an older server is refused
per-skill rather than silently producing guidance that does not work.

### Upgrading from 1.4.1 or earlier

Two things changed that affect an existing installation.

**Skills now install to `~/.claude/skills`.** Earlier versions defaulted to
`%APPDATA%\Claude\skills`, which no Claude surface actually reads — installs reported success and
the skills never loaded. If you installed skills before 2.2.0 they are probably sitting there
unused. After upgrading the server, ask Claude to:

> *"Prune the legacy AI Power Tools skills."*

That reports what it would remove; confirm to apply. It only removes directories it can prove
came from this product, and backs up anything you edited.

**Two skills were renamed.** `ea-mcp-modeling` → `ea-modeling`, and `ea-mcp-validation` →
`ea-validation`. `ea-mcp-quicklinker` was withdrawn. Without pruning you will have both the old
and new copies installed, giving contradictory guidance on the same subject — so prune as part of
upgrading, not later.

## What's in the bundle

Start with **`ea-start-here`**. It runs a short session preflight and routes to the right skill,
which is quicker than choosing from the list below.

### Core

| Skill | Purpose |
|---|---|
| `ea-start-here` | Entry point — session preflight, then routing to the right skill |
| `ea-modeling` | Build EA models via the MCP server — build order, defects, verification |
| `ea-navigation-diagrams` | Click-through "navigation diagrams" over hierarchical data |
| `ea-diagnostic` | Produce a structured diagnostic report for support |

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
| `ea-ruleset-author` | Build a complete ruleset for a modelling language from scratch |
| `ea-model-hygiene` | Find and fix model decay — orphans, inconsistent usage, safe deletion |

### Lifecycle and reporting

| Skill | Purpose |
|---|---|
| `ea-change-management` | Baselines and change history — what changed, when, by whom |
| `ea-import-export` | XMI interchange, document generation, diagram export to image/SVG/Visio |
| `ea-stakeholder-reporting` | Portfolio roll-ups and business-language output for non-modellers |

### Developer

| Skill | Purpose |
|---|---|
| `ea-com` | Drive EA from Python via the COM API rather than through MCP |

### Shared references

`_shared/references/` installs alongside the skills and is linked from them. It holds the
canonical Westbrook Bank example specification, the generated list of every server operation,
and shared guidance on EA latency and file encoding. It contains no `SKILL.md` and does not load
as a skill.

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
* `min_server_version` — bundle-wide floor; the installer refuses to
  write any skill whose `min_server_version` exceeds the running server

## Release process

1. Edit a skill (or add a new one).
2. Bump the affected skill's `version` in `manifest.json`.
3. Bump `bundle_version` and `released_at`.
4. Regenerate the `sha256` map (see `tools/regen-manifest.py`).
5. Commit, tag (e.g. `v0.6.1`), push.
6. `gh release create vX.Y.Z` with each skill file plus `manifest.json`
   as release assets — uploaded under stable filenames so the installer
   resolves `/releases/latest/download/<filename>` reliably.

The product binary at `NovoCircle/ai-power-tools-releases` does NOT
need to be re-released for skill changes. That's the whole point.

## Versioning policy

- **bundle_version** moves independently of the product version. AI
  Power Tools v0.6.0 customers can pull bundle v0.7.x as long as the
  manifest's `min_server_version` is ≤ 0.6.0.
- **Per-skill `version`** bumps only when that skill's content changes.
- **`min_server_version` per skill** gates against tool additions. A
  skill that references a tool introduced in product v0.7.0 must set
  `min_server_version: "0.7.0"`; v0.6.0 customers see it in
  `list_available_skills` with `compatible: false`.

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

## License

MIT. See [LICENSE](LICENSE).
