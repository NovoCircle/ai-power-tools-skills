# Enterprise deployment

How to get AI Power Tools for Sparx EA — the MCP server and the skills — onto a
fleet of machines, and how updates reach them afterwards.

## What actually gets deployed

**One plugin.** From 3.5.0 the skills and the MCP server ship together and carry the same
version, so there is one artifact to approve, deploy and update.

| Artifact | What it is | Scope |
|---|---|---|
| `ai-power-tools` plugin | The skills, plus the MCP server it declares by pinned release URL | Per machine or per org, depending on route |

The plugin does not carry the ~40 MB binary. It names a release asset, and Claude Code
downloads and extracts it into the plugin cache on first use. One plugin version maps to
exactly one server build, because the reference is pinned rather than floating — a later
server release cannot change what an already-installed plugin loads.

A standalone `.mcpb` is still published for the Claude Desktop extension path, and the
extension's own updater still polls for it. That path remains for installations that predate
the plugin; new deployments do not need it.

## How this works when Cowork runs in the cloud

Cowork defaults to a cloud sandbox, which attaches back to Claude Desktop running on a
physical machine. The desktop mounts the plugin's files into the sandbox and proxies the
plugin's MCP server back to the host, so Enterprise Architect stays local while the session
runs remotely.

The practical consequence: **the machine still needs Claude Desktop and a working EA
install.** A cloud Cowork session is not a way to avoid deploying to the workstation — it is a
different place for the conversation to run, not a different place for EA to run.

Enterprise Architect is Windows-only and the server drives it over COM, so the server must run
in the *same* Windows environment as EA. For a macOS user that means the whole stack inside a
Windows VM; native Claude Desktop talking to EA under Wine cannot work, because the COM
boundary sits between them.

## Deploying the skills plugin

Three routes. Pick by how the organization manages its fleet.

### Route A — Claude Code, per user

For developers using the CLI, the desktop Code tab, or VS Code:

```bash
claude plugin marketplace add NovoCircle/ai-power-tools-skills
claude plugin install ai-power-tools@novocircle
```

### Route B — Desktop upload, per machine

For a single workstation with no central management: upload
`ai-power-tools.plugin` through Claude Desktop. The file is built by
`tools/build-plugin.py` and attached to each GitHub release.

This route is **per machine and does not sync**. A user with two workstations
uploads twice, and nothing tells them when a newer build exists. It suits pilots
and single-seat installs, not a fleet.

### Route C — Managed settings, fleet-wide

The route for an organization. Declare the marketplace and the plugin in the
admin-controlled settings source, and every machine picks it up without the user
doing anything.

Windows, either of:

- the `HKLM\SOFTWARE\Policies\ClaudeCode` registry key
- `C:\Program Files\ClaudeCode\managed-settings.json`

macOS and Linux: `/etc/claude-code/managed-settings.json`

```json
{
  "extraKnownMarketplaces": {
    "novocircle": {
      "source": {
        "source": "github",
        "repo": "NovoCircle/ai-power-tools-skills",
        "ref": "v3.0.1"
      }
    }
  },
  "enabledPlugins": {
    "ai-power-tools@novocircle": true
  }
}
```

Two things to know about this route:

- A marketplace on a **network location must be declared in user or managed
  settings**. Project and local scope are refused for network sources, so
  managed settings is the correct admin-trusted home for it.
- `ref` pins the marketplace to a git ref. Pin it to a release tag in any
  environment where an unreviewed skill change would be unwelcome. Omit `ref`
  and machines track the default branch.

## How updates work

Updates differ by route, and only one of them is automatic.

| Route | How a new version arrives | Automatic? |
|---|---|---|
| A — marketplace, per user | `claude plugin marketplace update novocircle` then `claude plugin update ai-power-tools` | No — user runs it |
| B — desktop upload | Re-upload the new `.plugin` | No — and nothing prompts |
| C — managed settings, unpinned | Marketplace refresh picks up the default branch | Yes |
| C — managed settings, pinned | Edit `ref` in the policy; machines follow on next refresh | Yes, once you bump the ref |

A plugin update needs a **restart to apply** — the new version is staged, not
swapped into a running session.

`install_skills` is retired. It still exists on machines that have it, but from 3.5.0 it declines once the plugin supplies the same skills and points at the migration script instead of writing a second copy.

## Cutting a release that serves every route

Three files carry the version and must agree:

- `manifest.json` → `bundle_version`
- `plugins/ai-power-tools/.claude-plugin/plugin.json` → `version`
- `.claude-plugin/marketplace.json` → the `ai-power-tools` entry's `version`

`tools/build-plugin.py` refuses to build when they disagree, so drift fails at
build time rather than reaching a customer as two version numbers for the same
skills.

```bash
python tools/regen-manifest.py     # refresh hashes
python tools/gate.py               # release blocker if red
python tools/build-plugin.py       # emits dist/ai-power-tools.plugin
```

Tag the release, attach `dist/ai-power-tools.plugin` alongside the existing
flattened bundle assets, and bump any pinned `ref` in customer policies.

## Constraints worth knowing before you hit them

**A required `user_config` field with no default breaks sandboxed Cowork.** When
the desktop proxies an MCPB server to the host, it drops any server whose manifest
declares a `user_config` entry that is `required: true` with no `default`. The
server disappears with a log line and no user-facing error. The current manifest
has no such field — every entry is optional or defaulted — and it must stay that
way. The pre-2.0.0 manifest's required `license_key` would have been dropped.

**Policy can block marketplaces outright.** An organization can disable
third-party marketplaces, in which case Route C is unavailable and the plugin has
to arrive through the organization's own provisioning instead.

**Route B does not scale and does not notify.** Treat desktop upload as a pilot
mechanism, not a deployment one.

## Moving from `install_skills`

Before 3.5.0 the skills arrived through the `install_skills` MCP tool, which copied them into
`~/.claude/skills`. The plugin supersedes that, and `install_skills` now declines rather than
writing a second copy.

The two are additive. A machine carrying both loads every skill twice — once unprefixed, once
as `ai-power-tools:<name>` — because they are different sources and nothing deduplicates
across them. That is double the always-on token cost and leaves it ambiguous which copy
answers.

Clearing the older copies is a **one-time job per machine**, done with a script rather than a
product feature:

```powershell
.\migrate-to-plugin.ps1 -WhatIf     # show what would go, change nothing
.\migrate-to-plugin.ps1             # list it, then ask before removing
.\migrate-to-plugin.ps1 -Force      # unattended; the list is still printed
```

`migrate-to-plugin.ps1` ships with each server release on `ai-power-tools-releases`. It prints
the skills it would remove, names the ones it will **not** touch, and deletes nothing until the
operator types `YES`. `-Force` exists for unattended fleet use.

**Do not script a delete of `~/.claude/skills`.** That directory may also hold skills for AI
Power Tools for Microsoft Visio — a separate product with its own installer — and any skills a
user wrote themselves. The migration script can tell them apart because it reads the
installer's own record of what it wrote; a directory listing cannot. Files edited locally are
copied to a timestamped backup under `~/.claude/backups/` before removal and named in the
summary.

For a fleet, the sequence is: deploy the plugin through managed settings, then run the script
once per machine that previously used `install_skills`.

## Verifying a deployment

On a target machine, after install and a restart:

```bash
claude plugin list
```

Expect `ai-power-tools@novocircle`, enabled, at the version you deployed.

```bash
claude plugin details ai-power-tools
```

Expect `Skills (19)`. `_shared` is correctly not among them — it carries no
`SKILL.md` and ships only so the skills' relative links resolve.

In a Cowork session, confirm both halves arrived: ask for a skill by name
(`ea-modeling`), and confirm the EA tools are reachable, which exercises the host
bridge back to the workstation.
