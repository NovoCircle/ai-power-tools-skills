#!/usr/bin/env python3
"""Build the SQLite reporting database from a report model and a pivot result.

IMPURE, and the only impure thing here is the plumbing. Every decision - which
tables exist, which columns, which rows, which values - was already made by the
pure modules upstream. This module creates tables, inserts rows, and counts what
landed. It does not decide anything, and it does not compare: comparing is
`reconcile.py`'s job, because a loader that grades its own work is not a check.

    python -m pytest _shared/tools/test_load.py -q

NO CLOCK
--------
`run_id` and `run_at` are REQUIRED parameters, not defaults read from the system
clock. A module that stamps its own timestamp cannot be tested for the value it
stamps, and the run identity belongs to the pipeline that owns the run, not to
the function that happens to write the row.

EVERY STATEMENT IS LOGGED, NO VALUE IS
--------------------------------------
`LoadResult.sql_log` holds the statement text in issue order, with a row count
for the parameterized inserts - never the bindings. The log is a build artifact
that gets attached to tickets and pasted into chat; the values are customer
content. Statement text plus count is what makes a build reproducible and
reviewable, and it is also all that can be published safely.

AN UNKNOWN COLUMN IS AN ERROR, NOT A DROPPED VALUE
--------------------------------------------------
A row dict carrying a key the table has no column for raises `LoadError`. The
tempting alternative - ignore it and insert the rest - is precisely the silent
data loss this whole capability exists to prevent, and it would be invisible in
the reconciliation because the row count would still match.
"""
from __future__ import annotations

import pathlib
import sqlite3
from dataclasses import dataclass, field

from ddl import FRAME_DDL, generate_ddl, quote
from report_model import ReportModel


class LoadError(Exception):
    """A load was refused. Never raised for an empty table - only for a build
    that would have written something other than what it was given."""


#: Written by this module, never by a caller: the loader owns the audit row.
LOAD_RUN = "load_run"


@dataclass
class LoadResult:
    database: str = ""
    run_id: str = ""
    #: Table name -> rows counted by reading the database back, not by counting
    #: what was handed in. A count taken from the input would pass even if the
    #: insert never happened.
    rows_by_table: dict[str, int] = field(default_factory=dict)
    sql_log: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def statements(self) -> int:
        return len(self.sql_log)

    @property
    def rows_loaded(self) -> int:
        """Total rows, excluding the audit row the loader writes itself."""
        return sum(n for t, n in self.rows_by_table.items() if t != LOAD_RUN)

    def to_dict(self) -> dict:
        return {
            "database": self.database,
            "run_id": self.run_id,
            "statements": self.statements,
            "rows_loaded": self.rows_loaded,
            "rows_by_table": dict(sorted(self.rows_by_table.items())),
            "warnings": list(self.warnings),
        }


def entity_columns(model: ReportModel) -> dict[str, list[str]]:
    """Column order per entity table, matching `ddl.entity_table_ddl` exactly.

    Spelled out in one place so the insert and the `CREATE TABLE` cannot drift.
    They drifted once between `FRAME_TABLES` and `FRAME_DDL`, and the symptom was
    a table that existed but was invisible to everything reading the model.
    """
    return {t.name: ["ea_guid", "name", "metaclass"] + [c.name for c in t.columns]
            for t in model.tables}


def frame_columns() -> dict[str, list[str]]:
    return {name: [c for c, _ in spec] for name, spec in FRAME_DDL.items()}


class _Writer:
    """Thin wrapper whose only extra job is logging what it issued."""

    def __init__(self, conn: sqlite3.Connection, log: list[str]) -> None:
        self.conn = conn
        self.log = log

    def ddl(self, statement: str) -> None:
        self.log.append(statement)
        self.conn.execute(statement)

    def insert(self, table: str, columns: list[str], rows: list[dict]) -> int:
        """Insert `rows` into `table`, aligned to `columns`.

        A missing key becomes NULL - that is a genuinely absent value. An extra
        key raises, because it is a value with nowhere to go.
        """
        if not rows:
            # Logged anyway: "zero rows for this table" is a fact about the
            # build, and a silent absence is what hides an empty extract.
            self.log.append(f"-- INSERT INTO {quote(table)}: 0 rows")
            return 0
        known = set(columns)
        for i, row in enumerate(rows):
            unknown = sorted(set(row) - known)
            if unknown:
                raise LoadError(
                    f"{table}: row {i} carries {unknown!r}, which the table has no "
                    f"column for. Columns are {columns!r}. Refusing to load rather "
                    f"than drop a value."
                )
        cols = ", ".join(quote(c) for c in columns)
        marks = ", ".join("?" for _ in columns)
        sql = f"INSERT INTO {quote(table)} ({cols}) VALUES ({marks})"
        self.log.append(f"{sql}   -- {len(rows)} rows")
        self.conn.executemany(sql, [[row.get(c) for c in columns] for row in rows])
        return len(rows)


def build_database(path,
                   model: ReportModel,
                   pivot_result,
                   frame_rows: dict[str, list[dict]] | None = None,
                   *,
                   run_id: str,
                   run_at: str,
                   repository: str = "",
                   spec_hash: str = "",
                   overwrite: bool = False) -> LoadResult:
    """Create the database at `path` and load it.

    `pivot_result` supplies the entity rows and the three derived tables
    (`tag_value`, `overflow_tag`, `tag_coverage`). `frame_rows` supplies the rest
    of the frame - `pkg`, `element`, `rel_all`, `diagram`, `diagram_object`,
    `attribute`, `operation` - as table name -> row dicts. `load_run` is written
    by this function and must not appear in `frame_rows`.

    Refuses to overwrite an existing file unless `overwrite=True`. A refresh that
    silently replaces the database somebody is reporting off is not a refresh.
    """
    path = pathlib.Path(path)
    frame_rows = dict(frame_rows or {})
    result = LoadResult(database=str(path), run_id=run_id)

    if LOAD_RUN in frame_rows:
        raise LoadError(f"{LOAD_RUN} is written by the loader; do not pass it in")
    if path.exists() and not overwrite:
        raise LoadError(f"{path} exists; pass overwrite=True to replace it")

    frame_cols = frame_columns()
    unknown_tables = sorted(set(frame_rows) - set(frame_cols))
    if unknown_tables:
        raise LoadError(f"not frame tables: {unknown_tables!r}")

    if path.exists():
        path.unlink()
    path.parent.mkdir(parents=True, exist_ok=True)

    ent_cols = entity_columns(model)
    if pivot_result.unplaced:
        result.warnings.append(
            f"{len(pivot_result.unplaced)} tag row(s) reached no table - see the "
            "pivot result; these are empty values on untyped elements")

    conn = sqlite3.connect(str(path))
    try:
        w = _Writer(conn, result.sql_log)
        for statement in generate_ddl(model):
            w.ddl(statement)

        # Frame first, so `element` is populated before anything references it.
        derived = {
            "tag_value": pivot_result.tag_value,
            "overflow_tag": pivot_result.overflow,
            "tag_coverage": pivot_result.coverage,
        }
        for name in FRAME_DDL:
            if name == LOAD_RUN:
                continue
            rows = derived.get(name, frame_rows.get(name, []))
            w.insert(name, frame_cols[name], rows)

        for table_name, cols in ent_cols.items():
            w.insert(table_name, cols, pivot_result.rows.get(table_name, []))

        # The audit row goes in before the read-back so it is counted like any
        # other row, with reconciled/mismatches left NULL until there is a
        # reconciliation to record. A build that claims to be reconciled before
        # anything checked it is the defect this column exists to expose.
        w.insert(LOAD_RUN, frame_cols[LOAD_RUN], [{
            "run_id": run_id, "run_at": run_at, "repository": repository,
            "spec_hash": spec_hash, "rows_loaded": None,
            "reconciled": None, "mismatches": None,
        }])

        for name in list(FRAME_DDL) + list(ent_cols):
            sql = f"SELECT COUNT(*) FROM {quote(name)}"
            result.sql_log.append(sql)
            result.rows_by_table[name] = conn.execute(sql).fetchone()[0]

        sql = (f"UPDATE {quote(LOAD_RUN)} SET {quote('rows_loaded')} = ? "
               f"WHERE {quote('run_id')} = ?")
        result.sql_log.append(sql)
        conn.execute(sql, (result.rows_loaded, run_id))
        conn.commit()
    finally:
        conn.close()
    return result


def record_reconciliation(path, run_id: str, reconciliation) -> bool:
    """Persist a reconciliation verdict onto its `load_run` row.

    Separate from `build_database` on purpose: the database counts do not exist
    until the load has happened, so the verdict cannot be known while writing the
    row. Returns False when no row matched, rather than reporting a success that
    updated nothing - the same failure the gate makes when it reports GREEN for a
    check it skipped.
    """
    conn = sqlite3.connect(str(path))
    try:
        cur = conn.execute(
            f"UPDATE {quote(LOAD_RUN)} SET {quote('reconciled')} = ?, "
            f"{quote('mismatches')} = ? WHERE {quote('run_id')} = ?",
            (1 if reconciliation.ok else 0,
             len(reconciliation.failures) + len(reconciliation.skipped),
             run_id))
        conn.commit()
        return cur.rowcount == 1
    finally:
        conn.close()


def database_counts(path, model: ReportModel) -> dict[str, int]:
    """Entity-table row counts read back from a built database.

    This is the database side of the reconciliation. Only entity tables: the
    frame is reconciled through `scalars`, where each dimension's repository
    figure comes from its own extract rather than from the census.
    """
    conn = sqlite3.connect(str(path))
    try:
        out = {}
        for t in model.tables:
            out[t.name] = conn.execute(
                f"SELECT COUNT(*) FROM {quote(t.name)}").fetchone()[0]
        return out
    finally:
        conn.close()


def scalar_counts(path) -> dict[str, int]:
    """Frame-table row counts read back, for the non-entity dimensions."""
    conn = sqlite3.connect(str(path))
    try:
        return {name: conn.execute(
            f"SELECT COUNT(*) FROM {quote(name)}").fetchone()[0]
            for name in FRAME_DDL}
    finally:
        conn.close()
