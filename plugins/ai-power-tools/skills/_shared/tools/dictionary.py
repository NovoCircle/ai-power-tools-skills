#!/usr/bin/env python3
"""The data dictionary and the build manifest.

PURE. No repository calls, no COM, no file or network I/O, no clock, no
randomness. In, a report model and a load result; out, a Markdown string and a
JSON-able dict. The caller writes them to disk.

    python -m pytest _shared/tools/test_dictionary.py -q

WHY THIS IS A DELIVERABLE AND A .sql FILE IS NOT
-----------------------------------------------
SQLite carries its own schema, so a DDL file beside the database duplicates it
and nothing reads it. What is NOT recoverable from the schema is the part a
person needs: which tagged value a column came from, how much of it is actually
populated, whether its enumeration is the declared one or merely what happened to
be used, and which tags were routed to overflow instead of becoming columns. A
column whose coverage is 11% looks exactly like one at 100% in a table definition,
and that is the number that turns a roll-up into a confident wrong answer.

So the dictionary leads with coverage, states the source tag for every column, and
names every caveat that would otherwise have to be rediscovered by whoever first
disbelieves a figure.
"""
from __future__ import annotations

from ddl import FRAME_DDL
from report_model import ReportModel

#: One line per frame table, in FRAME_DDL's order. `test_dictionary.py` asserts
#: the keys match FRAME_DDL exactly - the model's table tuple and the DDL drifted
#: once already, and a dictionary that omits a table is how that stays invisible.
FRAME_PURPOSE = {
    "pkg": "The package tree in scope, with each package's path and depth.",
    "element": ("The key map: which entity table each element landed in, and "
                "which package it lives in. Not a business table - it carries no "
                "name, metaclass or stereotype, because those belong to the "
                "entity tables. Diagram membership and relationship endpoints "
                "resolve against it, never against a typed table."),
    "rel_all": "Every relationship between in-scope elements.",
    "tag_value": ("The multi-value bridge: one row per VALUE, not per tag. "
                  "Measures and filters must use this, not the flattened column."),
    "tag_coverage": ("How much of each column is actually populated. Read this "
                     "before trusting any aggregate."),
    "overflow_tag": ("Tags too sparse to earn a column, kept as key/value so the "
                     "load discards nothing."),
    "diagram": "Diagrams in scope. Geometry is deliberately not captured.",
    "diagram_object": "Which elements appear on which diagram.",
    "attribute": "Attributes of in-scope elements.",
    "operation": "Operations of in-scope elements.",
    "load_run": ("One row per build: when it ran, against what, how many rows "
                 "landed, and whether it reconciled."),
}


def _pct(x: float) -> str:
    return f"{x * 100:.0f}%"


def _esc(text: str) -> str:
    """Keep a pipe in a description from breaking the table it sits in."""
    return (text or "").replace("|", "\\|").replace("\n", " ").strip()


def data_dictionary(model: ReportModel,
                    *,
                    run_id: str = "",
                    run_at: str = "",
                    repository: str = "",
                    reconciliation=None,
                    domain_violations: list[dict] | None = None) -> str:
    """The human-readable schema. Deterministic for a given model."""
    out: list[str] = []
    tech = model.technology_name or model.technology_id or "(no technology)"
    out.append(f"# Data dictionary - {tech}")
    out.append("")
    out.append("| | |")
    out.append("|---|---|")
    if model.technology_id:
        out.append(f"| Technology id | `{model.technology_id}` |")
    if model.namespace:
        out.append(f"| Profile namespace | `{model.namespace}` |")
    if repository:
        out.append(f"| Repository | {_esc(repository)} |")
    if run_id:
        out.append(f"| Run | `{run_id}` |")
    if run_at:
        out.append(f"| Built | {run_at} |")
    out.append(f"| Entity tables | {len(model.tables)} |")
    out.append(f"| Frame tables | {len(model.frame)} |")
    out.append(f"| Sparse-tag threshold | {_pct(model.sparse_tag_threshold)} "
               "of populated coverage |")
    if reconciliation is not None:
        out.append(f"| Reconciliation | {_esc(reconciliation.summary())} |")
    out.append("")

    out.append("## How to read this")
    out.append("")
    out.append("- **Coverage is populated, not present.** A tag can be attached to "
               "every element and filled in on a quarter of them. The percentage "
               "here is the filled-in one, and it is the number that decides "
               "whether an aggregate over that column means anything.")
    out.append("- **Aggregate through `tag_value`, not the flattened column.** A "
               "column holding both `GLBA` and `GLBA, FFIEC` understates an "
               "exact-match count by about half.")
    out.append("- **`_keymap.entity_table` names the first table only.** An element "
               "carrying several stereotypes is genuinely several things and "
               "appears in several entity tables; join `_keymap` to each entity "
               "table on `ea_guid` for the complete mapping.")
    out.append("- **Tables prefixed `_` are plumbing, not vocabulary.** They carry "
               "the keys, bridges and audit the entity tables rest on. Report "
               "against the unprefixed tables.")
    out.append("- **A declared enumeration is the technology's; an observed one is "
               "merely what was used.** The column below says which.")
    out.append("")

    out.append("## Frame tables")
    out.append("")
    out.append("| Table | Columns | Purpose |")
    out.append("|---|---|---|")
    for name in model.frame:
        cols = ", ".join(f"`{c}`" for c, _ in FRAME_DDL.get(name, []))
        out.append(f"| `{name}` | {cols} | {_esc(FRAME_PURPOSE.get(name, ''))} |")
    out.append("")

    out.append("## Entity tables")
    out.append("")
    if not model.tables:
        out.append("None. The census found no stereotyped elements in scope.")
        out.append("")

    violations_by_col: dict[tuple[str, str], list[dict]] = {}
    for v in (domain_violations or []):
        violations_by_col.setdefault((v["table"], v["column"]), []).append(v)

    for t in model.tables:
        qualified = f"{t.profile}::{t.stereotype}" if t.profile else t.stereotype
        out.append(f"### `{t.name}`")
        out.append("")
        bits = [f"**{t.row_count}** row(s)", f"stereotype `{qualified}`"]
        if t.alias:
            bits.append(f"alias *{_esc(t.alias)}*")
        bits.append("declared by the technology" if t.declared
                    else "**observed but never declared** - the technology does "
                         "not define this stereotype")
        out.append(", ".join(bits))
        out.append("")
        if t.description:
            out.append(_esc(t.description))
            out.append("")
        if t.heterogeneous:
            spread = ", ".join(f"{m} ({n})" for m, n in t.metaclasses.items())
            out.append(f"> **One stereotype, several metaclasses:** {spread}. "
                       "Either the technology declares more than one base, or some "
                       "of these elements were given a stereotype meant for a "
                       "different kind of thing.")
            out.append("")

        out.append("| Column | Source tag | Type | Coverage | Enumeration |")
        out.append("|---|---|---|---|---|")
        out.append("| `ea_guid` | - | TEXT | 100% | - |")
        out.append("| `name` | - | TEXT | - | - |")
        out.append("| `metaclass` | - | TEXT | - | - |")
        for c in t.columns:
            if c.enum_values:
                enum = (f"{len(c.enum_values)} value(s), {c.enum_source}: "
                        + ", ".join(f"`{_esc(v)}`" for v in c.enum_values))
            else:
                enum = "-"
            cov = f"{_pct(c.coverage)} ({c.populated}/{t.row_count})"
            flags = []
            if not c.declared:
                flags.append("undeclared tag")
            if c.multi_valued:
                flags.append("multi-valued")
            name = f"`{c.name}`" + (" - " + ", ".join(flags) if flags else "")
            out.append(f"| {name} | `{_esc(c.source_tag)}` | {c.sql_type} | "
                       f"{cov} | {enum} |")
        if not t.columns:
            out.append("| *(no tagged values cleared the sparse threshold)* | | | | |")
        out.append("")
        if c_desc := [c for c in t.columns if c.description]:
            for c in c_desc:
                out.append(f"- `{c.name}` - {_esc(c.description)}")
            out.append("")
        if t.overflow_tags:
            out.append("**Routed to `overflow_tag`** (below the sparse threshold, "
                       "not discarded): "
                       + ", ".join(f"`{_esc(x)}`" for x in t.overflow_tags))
            out.append("")
        hits = [v for key, vs in violations_by_col.items() if key[0] == t.name
                for v in vs]
        if hits:
            out.append("**Outside the declared enumeration:**")
            out.append("")
            for v in hits:
                out.append(f"- `{v['column']}` = `{_esc(v['value'])}` "
                           f"({v['count']} row(s))")
            out.append("")

    if model.multi_value_candidates:
        out.append("## Possibly multi-valued, not acted on")
        out.append("")
        out.append("These tags' values often contain a comma. So do free-text "
                   "fields that merely mention one, and the declared type is "
                   "`String` either way - so this is reported for a decision "
                   "rather than guessed at, because guessing wrong splits a "
                   "team name into two.")
        out.append("")
        for tag in model.multi_value_candidates:
            out.append(f"- `{_esc(tag)}`")
        out.append("")

    if model.untyped_elements or model.excluded:
        out.append("## Not in an entity table")
        out.append("")
        out.append(f"- **{model.untyped_elements}** element(s) carry no stereotype, "
                   "so they have no business vocabulary term and are not in the "
                   "database. They were reported before the build; applying a "
                   "stereotype brings one into scope.")
        for key, n in sorted(model.excluded.items()):
            out.append(f"- **{n}** excluded, `{key}`")
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def manifest(model: ReportModel,
             load_result,
             *,
             run_id: str = "",
             run_at: str = "",
             repository: str = "",
             spec_hash: str = "",
             reconciliation=None,
             domain_violations: list[dict] | None = None) -> dict:
    """The machine-readable build record.

    Deliberately includes the reconciliation verdict and its own `ok` flag, so a
    pipeline step reading only this file can tell a good build from a bad one
    without parsing a report. `ok` is false unless the reconciliation ran AND
    passed - an absent reconciliation is not a pass.
    """
    rec = reconciliation.to_dict() if reconciliation is not None else None
    return {
        "run_id": run_id,
        "run_at": run_at,
        "repository": repository,
        "spec_hash": spec_hash,
        "ok": bool(rec and rec["ok"]),
        "technology": {
            "id": model.technology_id,
            "name": model.technology_name,
            "namespace": model.namespace,
        },
        "sparse_tag_threshold": model.sparse_tag_threshold,
        "load": load_result.to_dict(),
        "tables": [
            {"name": t.name, "stereotype": t.stereotype, "profile": t.profile,
             "declared": t.declared, "rows": t.row_count,
             "columns": [c.name for c in t.columns],
             "overflow_tags": list(t.overflow_tags)}
            for t in model.tables
        ],
        "frame": list(model.frame),
        "untyped_elements": model.untyped_elements,
        "excluded": dict(sorted(model.excluded.items())),
        "multi_value_candidates": list(model.multi_value_candidates),
        "domain_violations": list(domain_violations or []),
        "reconciliation": rec,
    }
