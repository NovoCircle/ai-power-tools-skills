"""Build one acceptance case's starting state on the run's copy of the model.

    python tools/acceptance/setup_case.py <case-file> <TC-nn> --run-dir D [--dry]

Run it after the copy is open in EA (RUN-IN-BUILD.md, step 2) and before the helper starts, with
ACCEPTANCE_CALL_LOG unset so the setup calls are not counted as the helper's. It reads the case's
fenced `setup` blocks and runs their lines in order through the server named by EA_MCP_EXE. `--dry`
prints the lines after their placeholders are read but makes no write (it still needs the server for
the name lookups).

A setup line is one of:

    call: <tool>.<operation> <json params> [=> <var>=<dotted.path>]
    notes-set: <diagram name> | <text>
    notes-insert: <diagram name> | <sentence>

`call` runs one server operation. `=> var=path` keeps a field of the result (for example
`=> card=element_id`) for the lines after it. `notes-set` replaces a diagram's Notes with the text,
as a person typing in EA's Notes window would. `notes-insert` adds one sentence line inside the
generated description of a diagram, above its closing marker line, as a person editing the
description would. In text, `\\n` is a line break; line ends are written as CRLF.

Names are read from the copy by placeholders in the JSON and the text: `{diagram:Name}`,
`{package:Name}` and `{element:Name}` become the id of the one object with that name (a name with
zero or several matches stops the setup), and `{$var}` becomes a value kept earlier.

`--run-dir D` is required. Before the first line runs, the setup asks `get_repository_info` which model is
open and refuses unless it is `D/model/WestbrookBank.qea`, so it can never write to ORIGINAL or to
another case's copy.

A setup that stops part-way leaves the copy half built. Throw the copy away and start the case again.
"""
import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path

PLACEHOLDER = re.compile(r"\{(diagram|package|element):([^}]+)\}")
VARIABLE = re.compile(r"\{\$(\w+)\}")
CLOSING_MARKER = "[AI Power Tools description v1 lang="

_LOOKUP_SQL = {
    "diagram": "SELECT Diagram_ID FROM t_diagram WHERE Name IN ({names})",
    "package": "SELECT Package_ID FROM t_package WHERE Name IN ({names})",
    "element": "SELECT Object_ID FROM t_object WHERE Name IN ({names})",
}


def setup_lines(case):
    """The lines of every fenced `setup` block in the case, comments and blanks dropped."""
    out, fenced, kind = [], False, None
    for line in case.splitlines():
        s = line.strip()
        if s.startswith("```"):
            fenced = not fenced
            kind = s[3:].strip() if fenced else None
            continue
        if fenced and kind == "setup" and s and not s.startswith("#"):
            out.append(s)
    return out


def case_text(case_file, tc):
    text = Path(case_file).read_text(encoding="utf-8")
    for part in re.split(r"\n(?=### TC-\d+)", text):
        if re.match(rf"### {re.escape(tc)}\b", part):
            return part
    sys.exit(f"{tc} not found in {case_file}")


def _sql_names(name):
    """The stored forms of a name: EA keeps an ampersand as itself or as &amp;."""
    forms = {name, name.replace("&", "&amp;"), name.replace("&amp;", "&")}
    return ", ".join("'" + f.replace("'", "''") + "'" for f in sorted(forms))


def lookup_id(caller, kind, name):
    result = caller.call("ea_analyze", "execute_sql",
                         {"sql": _LOOKUP_SQL[kind].format(names=_sql_names(name))})
    rows = result.get("rows") or []
    if len(rows) != 1:
        raise SetupError(f"{kind} '{name}': expected one match, found {len(rows)}")
    return list(rows[0].values())[0]


def substitute(text, caller, variables):
    """Replace {diagram:..}, {package:..}, {element:..} and {$var} in the text."""
    def name_ref(m):
        return str(lookup_id(caller, m.group(1), m.group(2).strip()))

    def var_ref(m):
        if m.group(1) not in variables:
            raise SetupError(f"{{${m.group(1)}}} used before it was kept")
        return str(variables[m.group(1)])

    return VARIABLE.sub(var_ref, PLACEHOLDER.sub(name_ref, text))


class SetupError(Exception):
    pass


def _dotted(obj, path):
    try:
        for part in path.split("."):
            obj = obj[part]
    except (KeyError, IndexError, TypeError):
        raise SetupError(f"the result has no field '{path}': {json.dumps(obj)[:200]}")
    return obj


def _norm(path):
    return str(path).replace("\\", "/").rstrip("/").lower()


def check_open_model(caller, run_dir):
    """Refuse unless the model open in EA is the run's copy."""
    want = (Path(run_dir) / "model" / "WestbrookBank.qea").resolve()
    info = caller.call("ea_repository", "get_repository_info", {})
    got = info.get("project_path") or info.get("connection_string") or ""
    if _norm(got) != _norm(want):
        raise SetupError(f"the open model is '{got}', not the run's copy '{want}'; nothing was written")


def _crlf(text):
    return "\r\n".join(text.replace("\\n", "\n").replace("\r\n", "\n").replace("\r", "\n").split("\n"))


def _write_notes(caller, diagram_id, notes):
    result = caller.call("ea_diagram", "update_diagram",
                         {"diagram_id": int(diagram_id), "properties": {"Notes": notes},
                          "include_preview": False})
    if result.get("rejected_properties"):
        raise SetupError(f"Notes were rejected: {result['rejected_properties']}")
    return result


def insert_sentence(notes, sentence):
    """Add the sentence as a line above the closing marker line of the description."""
    lines = notes.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    at = next((i for i, l in enumerate(lines) if l.startswith(CLOSING_MARKER)), None)
    if at is None:
        raise SetupError("the Notes hold no description block to add a sentence to")
    lines.insert(at, sentence)
    return "\r\n".join(lines)


def run_line(line, caller, variables, dry=False):
    key, _, rest = line.partition(":")
    key, rest = key.strip(), rest.strip()
    if key == "call":
        keep = None
        if " => " in rest:
            rest, keep = rest.rsplit(" => ", 1)
        op, _, raw = rest.partition(" ")
        tool, _, operation = op.partition(".")
        try:
            params = json.loads(substitute(raw or "{}", caller, variables))
        except ValueError as exc:
            raise SetupError(f"the parameters of '{line[:80]}' are not valid JSON: {exc}")
        print(f"call {tool}.{operation} {json.dumps(params)}")
        if dry:
            return
        result = caller.call(tool, operation, params)
        if result.get("ok") is False or result.get("error"):
            raise SetupError(f"{tool}.{operation} failed: {json.dumps(result)[:300]}")
        if keep:
            var, _, path = keep.partition("=")
            variables[var.strip()] = _dotted(result, path.strip())
    elif key in ("notes-set", "notes-insert"):
        name, _, text = rest.partition("|")
        name, text = name.strip(), text.strip()
        diagram_id = lookup_id(caller, "diagram", name)
        text = substitute(text, caller, variables)
        print(f"{key} on diagram {diagram_id} ({name}): {text[:80]}")
        if dry:
            return
        if key == "notes-set":
            _write_notes(caller, diagram_id, _crlf(text))
        else:
            rows = caller.call("ea_analyze", "execute_sql",
                               {"sql": f"SELECT Notes FROM t_diagram WHERE Diagram_ID = {int(diagram_id)}"})
            current = (rows.get("rows") or [{}])[0].get("Notes") or ""
            _write_notes(caller, diagram_id, insert_sentence(current, text.replace("\\n", " ")))
    else:
        raise SetupError(f"unknown setup line '{line[:60]}'")


def run_setup(lines, caller, dry=False, run_dir=None):
    if run_dir is not None:
        check_open_model(caller, run_dir)
    variables = {}
    for line in lines:
        run_line(line, caller, variables, dry)
    return variables


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("case_file")
    ap.add_argument("tc")
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    lines = setup_lines(case_text(a.case_file, a.tc))
    if not lines:
        print("no setup lines")
        return 0
    if os.environ.get("ACCEPTANCE_CALL_LOG"):
        sys.exit("ACCEPTANCE_CALL_LOG is set: unset it so the setup is not logged as the helper's calls")
    exe = os.environ.get("EA_MCP_EXE")
    if not exe:
        sys.exit("EA_MCP_EXE is not set: point it at the built ea-mcp-server.exe under test")
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    async def go():
        server = StdioServerParameters(command=exe, args=[], env=dict(os.environ))
        async with stdio_client(server) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                loop = asyncio.get_running_loop()

                class AsyncCaller:
                    def call(self, tool, operation, params):
                        raise RuntimeError("replaced below")

                # run the synchronous setup in a thread so each call can await the session
                def sync_call(tool, operation, params):
                    fut = asyncio.run_coroutine_threadsafe(
                        session.call_tool(tool, {"operation": operation, "params": params}), loop)
                    result = fut.result()
                    text = next((getattr(b, "text", None) for b in result.content
                                 if getattr(b, "text", None)), "{}")
                    try:
                        data = json.loads(text)
                    except ValueError:
                        data = {"error": text[:300]}
                    if result.isError and not data.get("error"):
                        data["error"] = "tool error"
                    return data

                caller = AsyncCaller()
                caller.call = sync_call
                await loop.run_in_executor(None, run_setup, lines, caller, a.dry, a.run_dir)

    try:
        asyncio.run(go())
    except SetupError as exc:
        print(f"SETUP FAILED: {exc}")
        return 1
    print("setup done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
