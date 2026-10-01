#!/usr/bin/env python3
"""DDL generation for a reporting database.

PURE. No repository calls, no COM, no file or network I/O, no clock, no
randomness. It turns a report model into `CREATE TABLE` statements and returns
them as strings.

v1 does NOT emit a `.sql` file as a deliverable - SQLite carries its own schema,
so a file beside the database duplicates it and nothing reads it. This module
exists because something still has to CREATE the tables in process. When a
portable target (Azure SQL, Fabric) is taken up it will need genuinely portable
DDL rather than SQLite's dialect, which is why the type mapping lives in
`report_model.SQL_TYPES` rather than being inlined here.

PORTABLE SUBSET ONLY
--------------------
Plain `CREATE TABLE`, quoted identifiers, no backend-specific types, no
constraints beyond primary keys. The reason is not elegance: EA reports a
statement its backend cannot run as a MODAL DIALOG that holds the COM connection
until a human dismisses it. Every later call then appears to hang. A narrow SQL
subset is how that is avoided.
"""
from __future__ import annotations

from report_model import ReportModel, Table

#: The frame. Fixed, technology-independent, and every column is spelled out
#: here rather than derived, so the shape is reviewable in one place.
FRAME_DDL: dict[str, list[tuple[str, str]]] = {
    "pkg": [
        ("package_id", "INTEGER"), ("parent_id", "INTEGER"), ("name", "TEXT"),
        ("path", "TEXT"), ("depth", "INTEGER"),
    ],
    # Every in-scope element, whatever its stereotype. `entity_table` names where
    # it landed, NULL when nowhere. Load-bearing: relationship endpoints resolve
    # against this, never against the typed tables, or every edge touching an
    # untyped element dangles.
    "element": [
        ("ea_guid", "TEXT"), ("object_id", "INTEGER"), ("name", "TEXT"),
        ("metaclass", "TEXT"), ("stereotype", "TEXT"), ("profile", "TEXT"),
        ("entity_table", "TEXT"), ("package_id", "INTEGER"),
    ],
    "rel_all": [
        ("connector_id", "INTEGER"), ("source_guid", "TEXT"), ("target_guid", "TEXT"),
        ("connector_type", "TEXT"), ("stereotype", "TEXT"), ("profile", "TEXT"),
        ("name", "TEXT"),
    ],
    # The multi-value bridge: one row per VALUE, not per tag. A flattened column
    # breaks aggregation silently - exact-match counting of a tag holding both
    # "GLBA" and "GLBA, FFIEC" understates by about half.
    "tag_value": [
        ("ea_guid", "TEXT"), ("tag", "TEXT"), ("value", "TEXT"),
    ],
    # Non-negotiable. A roll-up over a partly-populated tag produces a confident
    # wrong number, and a BI report is exactly where that gets believed.
    "tag_coverage": [
        ("table_name", "TEXT"), ("tag", "TEXT"), ("present", "INTEGER"),
        ("populated", "INTEGER"), ("total", "INTEGER"), ("coverage", "REAL"),
    ],
    "overflow_tag": [
        ("ea_guid", "TEXT"), ("tag", "TEXT"), ("value", "TEXT"),
    ],
    "diagram": [
        ("diagram_id", "INTEGER"), ("name", "TEXT"), ("diagram_type", "TEXT"),
        ("package_id", "INTEGER"),
    ],
    "diagram_object": [
        ("diagram_id", "INTEGER"), ("ea_guid", "TEXT"),
    ],
    "attribute": [
        ("attribute_id", "INTEGER"), ("element_guid", "TEXT"), ("name", "TEXT"),
        ("attr_type", "TEXT"), ("scope", "TEXT"),
    ],
    "operation": [
        ("operation_id", "INTEGER"), ("element_guid", "TEXT"), ("name", "TEXT"),
        ("return_type", "TEXT"), ("scope", "TEXT"),
    ],
    # Refresh audit, and where the source reconciliation result is persisted.
    "load_run": [
        ("run_id", "TEXT"), ("run_at", "TEXT"), ("repository", "TEXT"),
        ("spec_hash", "TEXT"), ("rows_loaded", "INTEGER"),
        ("reconciled", "INTEGER"), ("mismatches", "INTEGER"),
    ],
}

FRAME_KEYS = {
    "pkg": "package_id",
    "element": "ea_guid",
    "diagram": "diagram_id",
    "attribute": "attribute_id",
    "operation": "operation_id",
}


def quote(identifier: str) -> str:
    """Double-quote an identifier, doubling any embedded quote.

    Double quotes are the SQL standard form and are accepted by SQLite, Jet,
    T-SQL and Oracle. Backticks and square brackets are not portable.
    """
    return '"' + identifier.replace('"', '""') + '"'


def entity_table_ddl(table: Table) -> str:
    """`CREATE TABLE` for one entity table.

    `ea_guid` is the primary key: it is EA's stable natural key and survives a
    rebuild, where a row number does not.
    """
    cols = [f"  {quote('ea_guid')} TEXT NOT NULL", f"  {quote('name')} TEXT"]
    cols.append(f"  {quote('metaclass')} TEXT")
    for c in table.columns:
        cols.append(f"  {quote(c.name)} {c.sql_type}")
    cols.append(f"  PRIMARY KEY ({quote('ea_guid')})")
    body = ",\n".join(cols)
    return f"CREATE TABLE {quote(table.name)} (\n{body}\n);"


def frame_table_ddl(name: str) -> str:
    spec = FRAME_DDL[name]
    cols = [f"  {quote(c)} {t}" for c, t in spec]
    key = FRAME_KEYS.get(name)
    if key:
        cols.append(f"  PRIMARY KEY ({quote(key)})")
    body = ",\n".join(cols)
    return f"CREATE TABLE {quote(name)} (\n{body}\n);"


def generate_ddl(model: ReportModel, *, include_frame: bool = True) -> list[str]:
    """Every `CREATE TABLE` for a report model, frame first.

    Frame first so a loader can populate `element` before anything references
    it. Deterministic: frame tables in their declared order, entity tables in
    the model's order, which the census already fixed.
    """
    out: list[str] = []
    if include_frame:
        for name in FRAME_DDL:
            out.append(frame_table_ddl(name))
    for table in model.tables:
        out.append(entity_table_ddl(table))
    return out
