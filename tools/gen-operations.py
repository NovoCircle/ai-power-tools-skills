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
    python tools/gen-operations.py [path-to-server.py] [--version X.Y.Z]

``--version`` stamps the reference with a version other than the one the source
declares. It exists for the window between a release being decided and the
version bump landing in the server: the reference must describe the release it
ships with, not the build before it.

Also used by tools/gate.py, which imports ``collect_operations`` to check that
every operation a skill mentions actually exists.
"""
from __future__ import annotations

import ast
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Skills live under the plugin, not at the repository root.
_REFERENCE_REL = ("plugins", "ai-power-tools", "skills", "_shared", "references",
                  "operations.md")

# Default location of the server source, relative to this repo.
#
# Searched upward rather than fixed at ROOT.parent: in a git worktree the repo
# sits one level deeper (`<repo>.worktrees/<name>/`), so the sibling lookup
# missed and the op-drift check silently skipped -- printing a warning while the
# gate still reported green, which is the worst of both. Walking the parents
# finds the server from a worktree and from the main checkout alike.
_SERVER_REL = ("ai-power-tools", "ea-mcp-server", "ea_mcp_server", "server.py")


def _find_server() -> Path:
    for base in (ROOT, *ROOT.parents):
        candidate = base.parent.joinpath(*_SERVER_REL)
        if candidate.is_file():
            return candidate
    return ROOT.parent.joinpath(*_SERVER_REL)


DEFAULT_SERVER = _find_server()

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
    args = sys.argv[1:]
    version = None
    if "--version" in args:
        i = args.index("--version")
        if i + 1 >= len(args):
            print("--version needs a value, for example --version 3.6.0", file=sys.stderr)
            return 1
        version = args[i + 1]
        del args[i:i + 2]
    server = Path(args[0]) if args else DEFAULT_SERVER
    if not server.is_file():
        print(f"Server source not found: {server}", file=sys.stderr)
        return 1

    ops = collect_operations(server)
    if not ops:
        print("No dispatch tables found — has server.py changed shape?", file=sys.stderr)
        return 1

    dst = ROOT.joinpath(*_REFERENCE_REL)
    dst.parent.mkdir(parents=True, exist_ok=True)
    # newline="" keeps LF on Windows; a CRLF asset breaks the manifest hashes.
    with io.open(dst, "w", encoding="utf-8", newline="") as fh:
        fh.write(render(ops, version or _server_version(server)))

    total = sum(len(v) for v in ops.values())
    print(f"Wrote {dst.relative_to(ROOT).as_posix()} — "
          f"{total} operations across {len(ops)} meta-tools")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
