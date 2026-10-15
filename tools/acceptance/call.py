"""Call one AI Power Tools for EA operation on a built server, and log the call for the acceptance checks.

    python tools/acceptance/call.py <tool> <operation> '<params json>'
    python tools/acceptance/call.py ping

The server is EA_MCP_EXE (the build under test). When ACCEPTANCE_CALL_LOG names a file, every call is
appended to it as one JSON line ({"tool", "operation", "params", "ok"}); the `tools` checks in a case
are read from that log. Prints the tool's result text. Exit 1 when the tool reports an error.
Needs the `mcp` package (the server's development environment has it).
"""
import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def _log(tool, operation, params, ok):
    path = os.environ.get("ACCEPTANCE_CALL_LOG")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"tool": tool, "operation": operation, "params": params, "ok": ok}) + "\n")


async def main(tool, operation, params):
    exe = os.environ.get("EA_MCP_EXE")
    if not exe:
        sys.exit("EA_MCP_EXE is not set: point it at the built ea-mcp-server.exe under test")
    server = StdioServerParameters(command=exe, args=[], env=dict(os.environ))
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            if tool == "ping":
                result = await session.call_tool("ping", {})
            else:
                result = await session.call_tool(tool, {"operation": operation, "params": params})
                if operation == "start_reporting_refresh" and not result.isError:
                    run_id = json.loads(result.content[0].text).get("run_id")
                    while run_id:
                        await asyncio.sleep(2)
                        result = await session.call_tool(tool, {"operation": "get_reporting_refresh",
                                                                "params": {"run_id": run_id}})
                        if json.loads(result.content[0].text).get("status") != "running":
                            break
            _log(tool, operation, params, not result.isError)
            for block in result.content:
                text = getattr(block, "text", None)
                print(text if text is not None else f"<{block.type} content>")
            if result.isError:
                sys.exit(1)


if __name__ == "__main__":
    tool = sys.argv[1]
    operation = sys.argv[2] if len(sys.argv) > 2 else ""
    params = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
    asyncio.run(main(tool, operation, params))
