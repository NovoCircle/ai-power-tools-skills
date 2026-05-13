# AI Power Tools — Shipped Skills Library

Canonical, version-controlled set of Claude skills for **[AI Power Tools
for Enterprise Architect](https://github.com/NovoCircle/ai-power-tools-releases)**
— the MCP server that drives Sparx Systems Enterprise Architect via COM.

## How to install

If you have AI Power Tools v0.6.0 or later installed in Claude Desktop:

> *"Install the AI Power Tools skills."*

Claude will call the `install_skills` MCP tool, which fetches this
bundle from `releases/latest` and copies the skills to your skill
directory. Re-running the tool later picks up newer skill versions.

For older AI Power Tools versions (0.5.x and earlier) the skills are
bundled inside the `.mcpb` package; this repo is for the new fetch-on-
demand flow added in 0.6.0.

## What's in the bundle

| Skill | Purpose |
|---|---|
| `ea-com` | EA COM API automation patterns from Python |
| `ea-mcp-modeling` | Build EA models via the MCP server — phases, defects, verification |
| `ea-mdg-author` | Author MDG Technology XML files for Sparx EA |
| `ea-mdg-deploy` | Deploy and test an EA MDG Technology |
| `ea-mcp-validation` | Author `validate_model` YAML rule sidecars |
| `ea-mcp-quicklinker` | Author Quick Linker `stereotypedrelationships` for custom MDGs |

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

## Contributing

Skill content edits are welcome. PRs against this repo are independent
of the binary product's release cycle.

## License

MIT. See [LICENSE](LICENSE).
