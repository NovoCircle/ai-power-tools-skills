# Running acceptance cases inside a build or development conversation

This is the procedure a Claude Code conversation follows to run acceptance cases
(`plugins/ai-power-tools/skills/<skill>/references/test-cases.md`) against a server it has just
built. It runs on your Claude subscription inside the conversation you are already in: each case
is handed to a background helper agent, one at a time. Nothing here needs an extra account or key.

## When to run, and which cases

- **A change to a skill or to the server:** the cases of the skills the change touches. A server
  change touches every skill whose cases call the operations it changed.
- **A release build:** the set the person asks for (for example, every INVARIANT case).
- **Never in parallel, and never while a live pytest run is going.** Enterprise Architect allows one
  live session per machine.
- **Skip, and record as skipped:** cases marked `BLOCKED`, Prolaborate cases, and cases whose
  `**Setup:**` is prose only (a case with a `setup` block runs; see "Setup blocks" in
  `tools/acceptance-case-template.md`).

## Before the first case

- `EA_MCP_EXE` names the built `ea-mcp-server.exe` under test. In a release build that is
  `mcpb-build\bin\ea-mcp-server.exe`, never the installed extension.
- `PY` is a Python that has the `mcp` package. The server's development environment
  (`ea-mcp-server\.venv`) has it.
- EA is open with exactly one window, on the Westbrook Bank model. Note its full path as `ORIGINAL`.
- `RUN` is `research/acceptance-runs/<YYYY-MM-DD>-<label>/` under the workspace root. It is not
  inside a repository: transcripts and model copies stay out of git.

## For each case

1. **Prepare.** Make `$RUN/<skill>/<TC>/` (call it `D`). Copy `ORIGINAL` to `D/model/WestbrookBank.qea`,
   and make `D/output/` plus a folder for each other `<name-dir>` the case names. When the case has
   no `setup` block, run:
   `$PY tools/acceptance/check_case.py before <case-file> <TC> --run-dir D`.
   (With a `setup` block, the snapshot is taken after the setup: see step 2.)
2. **Open the copy.** First check that the copy exists: a path EA cannot find raises a "File not
   found" dialog that blocks every later call. Build the parameters with a JSON library rather than
   by hand, because Windows backslashes break hand-quoted JSON. Then, with `ACCEPTANCE_CALL_LOG`
   unset, run:
   `$PY tools/acceptance/call.py ea_repository open_project '{"project_path": "<D>\\model\\WestbrookBank.qea"}'`.
   Confirm that `get_repository_info` names the copy. If a call does not return, take a
   screenshot of EA and clear any dialog with computer use. Never kill EA.

   **If the case has a `setup` block,** build the starting state now, with `ACCEPTANCE_CALL_LOG`
   unset: `$PY tools/acceptance/setup_case.py <case-file> <TC> --run-dir D`. If it reports `SETUP FAILED`, the
   copy is half built: throw it away and start the case again. Then reopen `ORIGINAL` (this closes
   the copy), run `check_case.py before ... --run-dir D` on the closed copy, and open the copy again
   and confirm the title.
3. **Hand the case to a helper.** Use the Agent tool (general-purpose, Sonnet, run in the
   foreground, one case at a time) with the helper brief below, filled in for the case. Set
   `ACCEPTANCE_CALL_LOG=<D>/calls.jsonl` for the helper's calls.
4. **Save the reply.** Write the helper's final message, unedited, to `D/reply.md`. Record its
   token count, tool uses and duration from the Agent result.
5. **Close the copy.** Reopen `ORIGINAL` with `open_project` (log unset), then confirm the title.
6. **Check.** Run any `call` checks by hand, before step 5 if they need the copy open. Then run:
   `$PY tools/acceptance/check_case.py after <case-file> <TC> --run-dir D`.
7. **Grade.** For each `grade` line, decide yes or no from `D/reply.md` alone, and quote the
   sentence that decides it. Judge each `manual` line the same way. Write the verdicts to
   `D/grades.json`. Grade what the reply says, not what you think the helper meant.
8. **Verdict.** The case passes when every check passes. Add one line to `$RUN/summary.md`: skill,
   case, verdict, failed checks, tokens, duration.

When every non-skipped case of a skill has run, update `tools/results/skill-acceptance.json`
(`{"version": "<release>", "skills": {"<skill>": {"passed": n, "total": m}}}`) and regenerate the
register. A sample run does not update it.

## Helper brief (fill in the angle-bracket fields)

> You are Claude, helping an enterprise architect who works in Sparx Enterprise Architect. Follow
> the skill whose instructions are in `<W>/plugins/ai-power-tools/skills/<skill>/SKILL.md`, and the
> files it points to under that folder and `_shared/references/`. Read them first.
>
> To act on Enterprise Architect, use only this command, through Bash:
> `<PY> <W>/tools/acceptance/call.py <tool> <operation> '<params json>'`
> (`EA_MCP_EXE` and `ACCEPTANCE_CALL_LOG` are already set). The operations are the ones the skill
> names. Do not use any `mcp__` tool. Use computer use, a browser or the web only where the skill
> tells you to, and say in your reply what you looked at. Never open, close or restart Enterprise
> Architect. Write files only under `<D>/output/`. EA already has the model open.
>
> The person asks: "<the case's Ask, verbatim>"
>
> Do what the skill says. Your final message is your reply to the person, written for them.

Do not tell the helper anything else about the case: not its checks, its pass, its failure
description, or that it is a test.

## What one run per case can and cannot tell you

The first trial (five cases, 2026-10-15) gave different headline answers to the same question on
the same model. One pass is evidence that a skill can do the job, not that it does so reliably.
Before a skill's score counts toward the 80% threshold, run its INVARIANT cases more than once.
Measured cost: about 125,000 helper tokens per case, plus the conversation's own checking and
grading.

## What this does not test

- **Skill choice.** The helper is told which skill to follow. Cases about routing to the right
  skill need a conversation that finds the skill on its own (see
  `PROMPT-new-conversation.md`).
- **Isolation.** Nothing technically stops the helper from using other tools. The call log shows
  only the calls it made through `call.py`; computer use and web reads are not logged, so the
  `tools` checks that name them are judged from the reply.
- **`ping`.** Call it as `call.py ping '<params json>'`; its parameters are logged like any other
  call's.
