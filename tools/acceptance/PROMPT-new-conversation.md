# Prompt: run a batch of acceptance cases in a new conversation

Use this when you want a full or occasional run outside a build conversation. Open a new Claude
Code conversation in Claude Desktop with the workspace root as its folder. Make sure no other
conversation is running live tests against Enterprise Architect. Then paste the text below,
filling in the two lines in angle brackets.

---

Run acceptance cases for the AI Power Tools skills.

- **Cases:** <for example "every case of ea-validation and ea-modeling", or "every INVARIANT case">
- **Server under test:** <the full path to the built `ea-mcp-server.exe`, or "the installed one">

Follow `products/ai-power-tools-skills/tools/acceptance/RUN-IN-BUILD.md` exactly, as the
conversation that runs the cases. Run one case at a time; Enterprise Architect allows one live
session per machine. Skip and record as skipped any case that is BLOCKED, any Prolaborate case,
and any case whose Setup is prose only.

**Skill-choice cases.** For cases whose Covers line names a routing or "when to use" heading,
give the helper only the ask. Leave out the skill path, and tell it to use the skills installed
for this conversation. Record which skill its reply says it used.

Do not change any skill, case file or product code while running. Write results only under
`research/acceptance-runs/`. When the batch is done, tell me:
- passed, failed and skipped, per skill;
- each failure in one line, with the check that failed;
- the total tokens and the time the batch took.

Before you start, ask me about anything this prompt leaves unclear.
