# Testing the skills library

One command, from the repository root:

```
python -m pytest
```

`pytest.ini` sets the paths and prints every skip with its reason (`-rs`). The same command runs in
CI (`.github/workflows/gate.yml`). To run one file, name it:
`python -m pytest plugins/ai-power-tools/skills/ea-diagram-composition/tools/test_lint.py`.
A full run takes about 15 minutes; the chevron sweep is more than 2,000 of the 5,400 tests.

None of these tests start Enterprise Architect, Visio or any GUI.

## Where a test goes

A test lives beside the module it tests, in the same `tools/` folder, named for the module:

```
<skill>/tools/test_<module>.py        # tests <skill>/tools/<module>.py
```

- A bug fix adds a test to that module's file. A new file is for a new module (a new grammar or
  binding that has its own module), not for a new ticket.
- Test module basenames are unique across the whole repository. pytest imports each test file by
  its basename, so two files called `test_x.py` collide.
- Tests are not moved between folders. Most of them ship to customers (see below), so a move is a
  release.

## PINS: which backlog items a module pins

Every test module defines a module-level tuple of the backlog ids it pins:

```python
PINS = ("APT-2026-0155",)
```

or, when it pins no filed defect, an empty tuple with a one-line comment saying why:

```python
# No backlog item is pinned: these tests cover designed behavior, not a filed defect.
PINS = ()
```

Also start a regression test's docstring with the id (`"""APT-2026-0155: ..."""`). Then
`grep -rn APT-2026-0155` finds every test for an id, and the id survives a rename.
`tools/test_suite_conventions.py` fails when a module has no `PINS`, when an entry is not of the
form `APT-2026-nnnn`, or when two test modules share a basename.

## Data the tests depend on

Some tests need data that is not in this repository. They skip when it is absent, and the skip reason
names what is missing (`-rs` prints it). A skip is not a pass: a run that skips a dependency has not
checked what that dependency covers.

| Dependency | Covers | How to provide it |
|---|---|---|
| PyYAML | the binding and ruleset test files (`test_bindings.py`, `test_ruleset_archimate31.py`, parts of `test_measure_binding.py`, `test_advise.py`) | `python -m pip install pyyaml` |
| pyarrow | the Parquet writer tests in `test_parquet_tables.py` | `python -m pip install pyarrow` |
| Sparx's `EAExample.qea` | 138 test functions in the `test_bindings*.py` files and `test_measure_binding.py` | Install Enterprise Architect (the model is read from `%ProgramFiles%\Sparx Systems\EA\EAExample.qea`), or set `EA_EXAMPLE_MODEL` to its path. It is read directly as SQLite from a copy; EA is never started. |
| The server repository (`ea-mcp-server`) | 3 tests in `test_lint.py` that check the linter against a payload captured from the real server (`tests/fixtures/verify_diagram_real_payload.json`) | Check the server repository out so that `ai-power-tools/ea-mcp-server` sits beside this repository's folder, or set `EA_MCP_SERVER_REPO` to its path. |

Install the first two with `python -m pip install pytest pyyaml pyarrow`, as CI does.

## These tests ship to customers

25 of the 28 test files are listed in `manifest.json` and are installed with the skills. Any edit to
one of them changes its sha256, so after editing a test:

```
python tools/regen-manifest.py
python tools/gate.py
```

and commit the regenerated `manifest.json`. Never edit `manifest.json` by hand. The tests in
`tools/` and `security/checks/` are not shipped (nor is this file, `pytest.ini`, or
`tools/test_suite_conventions.py`).

Because they ship, test files must keep LF line endings and carry no real customer names, absolute
local paths or personal identifiers; use Westbrook Bank for any example. `tools/gate.py` enforces this.
