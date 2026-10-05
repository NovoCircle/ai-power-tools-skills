#!/usr/bin/env python3
"""Emit the reporting tables as Parquet, with real declared types.

The sink that pairs with `load.build_database`. It takes THE SAME INPUTS - the
report model, the pivot result and the frame rows - so the Parquet set and the
SQLite set are the same shape by construction rather than by agreement:

    census -> report model -> pivot + frame rows -> +- build_database   (SQLite)
                                                    +- build_parquet    (Parquet)

That is what makes `APT-2026-0211` and `APT-2026-0212` the same capability with
two sinks. 0211 writes both; 0212 writes only Parquet and never stands up a
relational stage. If the two sinks could disagree about the shape, none of the
Power BI findings would apply to one of the paths.

WHY PARQUET AND NOT CSV
-----------------------
Because the format carries the schema. Measured: the same three all-text tables
loaded through Excel arrived as `Column1...ColumnN`, since Power BI promotes row
0 to a header only when its types differ from the body. From Parquet the column
names and types were right on the first attempt with no Power Query step. That
is the whole reason this module exists, so a CSV fallback would quietly give
back the defect the format was chosen to remove. **pyarrow is REQUIRED and
stated** - never substituted. Excel is never an output format.

PYARROW IS DELIBERATELY NOT A CORE DEPENDENCY
---------------------------------------------
The transform is pure Python and deterministic, and must stay installable and
testable without a compiled wheel. So the dependency lives here, behind
`PYARROW_AVAILABLE`, and `parquet_schema()` - everything about the SHAPE of the
output - is pure and testable with pyarrow absent.

TYPES ARE DECLARED, NEVER INFERRED FROM THE DATA
------------------------------------------------
A column's type comes from the technology, through `report_model`. Inferring it
from the values would make the schema a function of which rows happen to be
populated, so a refresh could silently change a column's type. `APT-2026-0225`
is the related defect: six columns declared INTEGER held the string 'true', and
it was found precisely BY pointing a typed consumer at the output. Coercion
already happened in `pivot`; this module does not re-coerce and does not repair.
"""
from __future__ import annotations

import pathlib
from dataclasses import dataclass, field

from ddl import FRAME_DDL, physical
from load import (LOAD_RUN, entity_columns, frame_columns, pivot_notes,
                  pivot_warnings)
from report_model import ReportModel

try:  # pragma: no cover - environment-dependent
    import pyarrow as pa
    import pyarrow.parquet as pq
    PYARROW_AVAILABLE = True
except ImportError:  # pragma: no cover - environment-dependent
    pa = pq = None
    PYARROW_AVAILABLE = False

#: Declared SQL type -> Parquet logical type. A third leg of the same journey as
#: `report_model.SQL_TYPES` and `semantic_model.TMDL_TYPES`, named here so all
#: three are greppable together.
PARQUET_TYPES = {
    "TEXT": "string",
    "INTEGER": "int64",
    "REAL": "double",
}

DEFAULT_PARQUET_TYPE = "string"

ENTITY_PREFIX = (("ea_guid", "TEXT"), ("name", "TEXT"), ("metaclass", "TEXT"))


class ParquetError(Exception):
    pass


@dataclass
class ParquetResult:
    directory: str = ""
    run_id: str = ""
    #: PHYSICAL table name -> rows written. Keyed as the files are named, so a
    #: reconciliation can compare it to the database without translating.
    rows_by_table: dict[str, int] = field(default_factory=dict)
    files: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def rows_written(self) -> int:
        return sum(self.rows_by_table.values())


def parquet_type(sql_type: str) -> str:
    return PARQUET_TYPES.get((sql_type or "").strip().upper(), DEFAULT_PARQUET_TYPE)


def parquet_schema(model: ReportModel) -> dict[str, list[tuple[str, str]]]:
    """PHYSICAL table name -> [(column, parquet type)], for every table.

    Pure, and the one place the output's shape is decided. Derived from
    `ddl.FRAME_DDL` and the report model rather than restated, because a
    restatement is how the schema and the loader drift - `overflow_tag` was once
    in the DDL and missing from the model, and the symptom was a table that
    existed and was invisible.
    """
    out: dict[str, list[tuple[str, str]]] = {}
    for name, spec in FRAME_DDL.items():
        out[physical(name)] = [(c, parquet_type(t)) for c, t in spec]
    for table in model.tables:
        cols = [(c, parquet_type(t)) for c, t in ENTITY_PREFIX]
        cols += [(c.name, parquet_type(c.sql_type)) for c in table.columns]
        out[table.name] = cols
    return out


def _arrow_schema(columns: list[tuple[str, str]]):
    kinds = {"string": pa.string(), "int64": pa.int64(), "double": pa.float64()}
    # Every field is nullable: an absent tagged value is a genuinely absent
    # value, and refusing nulls would mean inventing one.
    return pa.schema([pa.field(name, kinds[kind], nullable=True)
                      for name, kind in columns])


def _table_rows(model: ReportModel, pivot_result, frame_rows: dict,
                *, run_id: str, run_at: str, repository: str, spec_hash: str,
                rows_loaded: int | None) -> dict[str, list[dict]]:
    """Rows per PHYSICAL table name, in the same order `build_database` loads."""
    derived = {
        "tag_value": pivot_result.tag_value,
        "overflow_tag": pivot_result.overflow,
        "tag_coverage": pivot_result.coverage,
    }
    out: dict[str, list[dict]] = {}
    for name in FRAME_DDL:
        if name == LOAD_RUN:
            continue
        out[physical(name)] = list(derived.get(name, frame_rows.get(name, [])))
    for table_name in entity_columns(model):
        out[table_name] = list(pivot_result.rows.get(table_name, []))
    # The audit row, same contract as the database: `reconciled` and
    # `mismatches` stay NULL until something has actually reconciled. An output
    # that claims to be reconciled before anything checked it is the defect this
    # column exists to expose.
    out[physical(LOAD_RUN)] = [{
        "run_id": run_id, "run_at": run_at, "repository": repository,
        "spec_hash": spec_hash, "rows_loaded": rows_loaded,
        "reconciled": None, "mismatches": None,
    }]
    return out


def build_parquet(directory,
                  model: ReportModel,
                  pivot_result,
                  frame_rows: dict[str, list[dict]] | None = None,
                  *,
                  run_id: str,
                  run_at: str,
                  repository: str = "",
                  spec_hash: str = "",
                  overwrite: bool = False,
                  compression: str = "snappy") -> ParquetResult:
    """Write one Parquet file per table into `directory`.

    Mirrors `load.build_database`'s signature on purpose: the same inputs, a
    different sink. Refuses to overwrite unless asked, for the same reason -
    replacing the files somebody is reporting off is not a refresh.
    """
    # Argument validation FIRST, then the dependency. A caller who passed the
    # wrong thing has a bug whether or not pyarrow is present, and being told
    # about pyarrow instead sends them to fix the wrong problem.
    directory = pathlib.Path(directory)
    frame_rows = dict(frame_rows or {})
    if LOAD_RUN in frame_rows:
        raise ParquetError(f"{LOAD_RUN} is written by this function; do not pass it in")
    unknown = sorted(set(frame_rows) - set(frame_columns()))
    if unknown:
        raise ParquetError(f"not frame tables: {unknown!r}")

    if not PYARROW_AVAILABLE:
        raise ParquetError(
            "Parquet output needs pyarrow, which is not installed. It is kept "
            "out of the core on purpose so the transform stays installable "
            "without a compiled wheel - install pyarrow to emit Parquet, or "
            "build the SQLite database instead. CSV is not a substitute: the "
            "point of Parquet is that it carries the column types."
        )

    schemas = parquet_schema(model)
    rows = _table_rows(model, pivot_result, frame_rows, run_id=run_id,
                       run_at=run_at, repository=repository,
                       spec_hash=spec_hash, rows_loaded=None)
    # Counted before writing, so the audit row can carry the true total rather
    # than being patched afterwards the way the database does it.
    total = sum(len(r) for name, r in rows.items() if name != physical(LOAD_RUN))
    rows[physical(LOAD_RUN)][0]["rows_loaded"] = total

    existing = [str(directory / f"{n}.parquet") for n in schemas
                if (directory / f"{n}.parquet").exists()]
    if existing and not overwrite:
        raise ParquetError(
            f"{len(existing)} parquet file(s) already in {directory}; pass "
            f"overwrite=True to replace them")

    directory.mkdir(parents=True, exist_ok=True)
    result = ParquetResult(directory=str(directory), run_id=run_id)

    # THE SAME warnings the database sink raises, from the same function. They
    # were copy-pasted here once and had already drifted - `unplaced` was
    # missing, so a customer on the Parquet-only path never heard that tag rows
    # reached no table.
    result.warnings.extend(pivot_warnings(pivot_result))
    result.notes.extend(pivot_notes(pivot_result))

    # THE EMITTER OWNS THE WHOLE SET. `build_database` unlinks the database
    # first, so the SQLite sink cannot leave a table behind that the model no
    # longer has. Writing file-by-file into an existing directory can: drop a
    # stereotype, re-emit, and its `.parquet` survives as a table that is not in
    # the model and that a reconciliation keyed on the model cannot see.
    #
    # Only when `overwrite` was asked for: a stale file is not something the
    # caller named, so deleting it uninvited would be the sink reaching outside
    # what it was asked to do.
    stale = sorted(p for p in directory.glob("*.parquet")
                   if p.stem not in schemas) if overwrite else []
    for p in stale:
        p.unlink()
    if stale:
        result.notes.append(
            f"removed {len(stale)} parquet file(s) for tables no longer in the "
            f"model: {', '.join(p.stem for p in stale)}")

    for name, columns in schemas.items():
        table_rows = rows.get(name, [])
        arrays = {c: [row.get(c) for row in table_rows] for c, _ in columns}
        table = pa.table(arrays, schema=_arrow_schema(columns))
        path = directory / f"{name}.parquet"
        pq.write_table(table, path, compression=compression)
        result.rows_by_table[name] = len(table_rows)
        result.files.append(str(path))

    return result
