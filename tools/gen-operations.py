"""Generate `_shared/references/operations.md` from the server's own source.

Every operation a skill can call is defined in one of the meta-tool dispatch
tables in the server's ``server.py``. Those tables, and the per-operation
docstrings behind them, are the only authoritative list. Anything written by
hand drifts, and the drift is invisible: a skill confidently names an operation
that does not exist, and nobody finds out until a customer tries it.

This reads the dispatch tables straight out of the source with ``ast`` — no
import, no running server — and writes the reference. Re-run it whenever the
server changes.

Usage:
    python tools/gen-operations.py [path-to-server.py]

Also used by tools/gate.py, which imports ``collect_operations`` to check that
every operation a skill mentions actually exists.
"""
from __future__ import annotations

import ast
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Default location of the server source, relative to this repo.
DEFAULT_SERVER = (
    ROOT.parent / "ai-power-tools" / "ea-mcp-server" / "ea_mcp_server" / "server.py"
)

META_TOOLS = ("ea_model", "ea_diagram", "ea_analyze", "ea_mdg", "ea_validate",
              "ea_repository")


def _first_sentence(doc: str | None) -> str:
    """The first sentence of a docstring, flattened to one line."""
    if not doc:
        return ""
    text = " ".join(doc.strip().split())
    for stop in (". ", "! ", "? "):
        if stop in text:
            return text.split(stop)[0].strip() + "."
    return text if len(text) < 200 else text[:197].rstrip() + "..."


def collect_operations(server_path: Path) -> dict[str, dict[str, str]]:
    """Return {meta_tool: {operation: one-line description}}.

    Reads the literal dispatch dicts inside each meta-tool function. A dict
    entry whose value is a plain name is resolved to that function's docstring.
    """
    tree = ast.parse(server_path.read_text(encoding="utf-8"))
    funcs: dict[str, ast.FunctionDef] = {
        n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
    }

    out: dict[str, dict[str, str]] = {}
    for tool in META_TOOLS:
        fn = funcs.get(tool)
        if fn is None:
            continue
        ops: dict[str, str] = {}
        for node in ast.walk(fn):
            if not isinstance(node, ast.Dict):
                continue
            for k, v in zip(node.keys, node.values):
                if not (isinstance(k, ast.Constant) and isinstance(k.value, str)):
                    continue
                if not isinstance(v, ast.Name):
                    continue
                target = funcs.get(v.id)
                ops[k.value] = _first_sentence(
                    ast.get_docstring(target) if target else None
                )
        if ops:
            out[tool] = dict(sorted(ops.items()))
    return out


def render(ops: dict[str, dict[str, str]], server_version: str) -> str:
    total = sum(len(v) for v in ops.values())
    lines: list[str] = []
    w = lines.append

    w("# EA MCP operations reference")
    w("")
    w("**Generated — do not edit by hand.** Produced by `tools/gen-operations.py` from the")
    w("server's dispatch tables. Re-run it after any server change rather than editing here.")
    w("")
    w(f"Server version: `{server_version}` · {total} operations across {len(ops)} meta-tools.")
    w("")
    w("Every operation is called the same way:")
    w("")
    w("```")
    w('<meta_tool>(operation="<name>", params={"arg": value, ...})')
    w("```")
    w("")
    w("All arguments go inside `params`. Passing them as top-level keys is the single most")
    w("common call error and produces a format error, not a result.")
    w("")
    w("If an operation is not in this list, it does not exist. Do not infer one from a pattern.")
    w("")

    for tool, entries in ops.items():
        w("---")
        w("")
        w(f"## `{tool}` — {len(entries)} operations")
        w("")
        w("| Operation | What it does |")
        w("|---|---|")
        for name, desc in entries.items():
            w(f"| `{name}` | {desc or '—'} |")
        w("")
    return "\n".join(lines) + "\n"


def _server_version(server_path: Path) -> str:
    init = server_path.parent / "__init__.py"
    try:
        for line in init.read_text(encoding="utf-8").splitlines():
            if line.startswith("__version__"):
                return line.split("=", 1)[1].strip().strip('"\'')
    except OSError:
        pass
    return "unknown"


def main() -> int:
    server = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SERVER
    if not server.is_file():
        print(f"Server source not found: {server}", file=sys.stderr)
        return 1

    ops = collect_operations(server)
    if not ops:
        print("No dispatch tables found — has server.py changed shape?", file=sys.stderr)
        return 1

    dst = ROOT / "_shared" / "references" / "operations.md"
    dst.parent.mkdir(parents=True, exist_ok=True)
    # newline="" keeps LF on Windows; a CRLF asset breaks the manifest hashes.
    with io.open(dst, "w", encoding="utf-8", newline="") as fh:
        fh.write(render(ops, _server_version(server)))

    total = sum(len(v) for v in ops.values())
    print(f"Wrote {dst.relative_to(ROOT).as_posix()} — "
          f"{total} operations across {len(ops)} meta-tools")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
