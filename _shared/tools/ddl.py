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
    # The key map. NOT a business table: it carries no name, no metaclass and no
    # stereotype, because those belong to the entity tables and duplicating them
    # here is what made the database look like EA's metamodel (APT-2026-0226).
    #
    # It exists because a reference to "any of 29 entity tables" is polymorphic,
    # and a relational model has exactly three ways to express that: a
    # discriminator column, one bridge table per type, or a shared key table.
    # This is the third. Diagram membership and relationship endpoints resolve
    # against it, never against a typed table.
    "element": [
        ("ea_guid", "TEXT"), ("entity_table", "TEXT"), ("package_id", "INTEGER"),
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

#: What each frame table is CALLED IN THE DATABASE. The pipeline keeps its own
#: vocabulary - `frame_rows["element"]` - and the physical name is applied once,
#: here, at the DDL and load boundary.
#:
#: The underscore is the whole point. A customer opening the database is
#: promised their business vocabulary, and sorting the plumbing to the bottom
#: under a prefix that reads as internal is what makes the promise true
#: (APT-2026-0226). `element` becomes `_keymap` because that is what it is once
#: the business columns are gone.
PHYSICAL_NAME = {
    "element": "_keymap",
    "pkg": "_pkg",
    "rel_all": "_rel_all",
    "tag_value": "_tag_value",
    "tag_coverage": "_tag_coverage",
    "overflow_tag": "_overflow_tag",
    "diagram": "_diagram",
    "diagram_object": "_diagram_object",
    "attribute": "_attribute",
    "operation": "_operation",
    "load_run": "_load_run",
}


def physical(name: str) -> str:
    """The database name for a frame table; an entity table is its own name."""
    return PHYSICAL_NAME.get(name, name)


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
    return f"CREATE TABLE {quote(physical(name))} (\n{body}\n);"


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
