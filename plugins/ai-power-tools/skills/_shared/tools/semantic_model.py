#!/usr/bin/env python3
"""The semantic model: the contract between a report model and Power BI.

PURE. No repository calls, no COM, no file or network I/O, no clock, no
randomness. It turns a `ReportModel` into a description of tables, relationships
and measures, and nothing else writes or applies anything.

WHY THIS LAYER EXISTS
---------------------
`report_model.py` is the shared contract between a census and a DATABASE: it
carries tables, columns, types, enums and coverage. It says nothing about
relationships or measures, because `APT-2026-0210` only ever needed DDL - the
relationship structure lived implicitly in `frame.py` and `ddl.py`.

Relationships and measures are precisely what a semantic model IS. So all three
Power BI paths - `APT-2026-0211` (reporting database), `APT-2026-0212` (Parquet
direct) and `APT-2026-0230` (live SQL views) - hang off this module, and the ONLY
thing that varies between them is where a table's rows come from:

    ReportModel  ->  SemanticModel  ->  TMDL text
                                          ^
                               Parquet.Document(...) | Sql.Database(...)

That makes "identical output whichever path a customer picks" structurally true
rather than aspirational, and `test_tmdl.py` asserts it.

WHY THE RELATIONSHIPS ARE GENERATED AND NEVER INFERRED
------------------------------------------------------
Measured 2026-10-02 on the reference model, 40 tables loaded with no
relationships defined. Power BI's own auto-detect produced 63 relationships
where the model needs 38. Twenty-eight were invented from shared enum values -
two tables related because both happened to hold a `data_classification` value.
Both `_rel_all` endpoints, which is the entire graph traversal, were NOT DETECTED
AT ALL. One correct relationship was switched off silently because two paths
competed. Nothing in Power BI reports any of this; the report looks finished.

The generated set is 38 relationships with exactly ONE inactive by design.

WHAT THIS MODULE REFUSES TO DECIDE
----------------------------------
Where the rows come from. A partition source is passed to the renderer, not
chosen here, because the eligible sources are a fact about the customer's estate
and this module cannot know it.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict

from ddl import FRAME_DDL, physical
from report_model import ReportModel

#: SQL type -> TMDL data type. `report_model.SQL_TYPES` already maps a declared
#: tagged-value type to SQL; this is the second leg of the same journey, kept
#: here rather than inlined so the whole mapping is reviewable in two places
#: instead of five.
TMDL_TYPES = {
    "TEXT": "string",
    "INTEGER": "int64",
    "REAL": "double",
}

DEFAULT_TMDL_TYPE = "string"

#: The hub, in the database's own vocabulary. A reference to "any of N
#: vocabulary tables" is polymorphic, and a relational model has exactly three
#: ways to express that - a discriminator column, one bridge per type, or a
#: shared key table. This is the third. Settled in `APT-2026-0226`; do not
#: re-litigate.
HUB = physical("element")

#: The relationship table is the one piece of plumbing that stays VISIBLE, under
#: a business name, because it has to host the traversal measures.
#:
#: The reason is measured, not stylistic: hiding removes 10 of the 11 plumbing
#: tables from the field list, but Power BI keeps a hidden table visible when it
#: hosts visible measures. Measures on the hub therefore defeat the hiding and
#: the customer sees `_keymap` in a field list they were promised would be their
#: business vocabulary.
#:
#: The alternative - a synthetic one-row measure table - was rejected: it needs a
#: constant partition, which under DirectQuery makes the model composite for no
#: benefit. Hosting the measures on the table whose rows they count is both
#: honest and free. Its columns are hidden individually, so the field list shows
#: a measure group and nothing else.
DEFAULT_MEASURE_HOST = "Relationships"

#: Key columns are hidden on every vocabulary table. They are join plumbing, and
#: a field list offering `ea_guid` on 29 tables is noise the customer did not ask
#: for. READ by `_entity_columns`, so editing this changes the output - it was
#: briefly a constant that declared the policy while the policy was hardcoded
#: elsewhere, which is the restate-and-drift failure these modules avoid.
HIDDEN_ENTITY_COLUMNS = frozenset({"ea_guid"})


@dataclass
class SemanticColumn:
    name: str
    data_type: str = DEFAULT_TMDL_TYPE
    source_column: str = ""
    is_hidden: bool = False
    format_string: str = ""
    summarize_by: str = "none"
    description: str = ""

    def __post_init__(self) -> None:
        if not self.source_column:
            self.source_column = self.name


@dataclass
class Measure:
    name: str
    expression: str
    format_string: str = "0"
    description: str = ""


@dataclass
class SemanticTable:
    #: The name in the model, which is what the customer reads in the field list.
    name: str
    #: The name in the database, Parquet set or view schema. The two differ only
    #: where a plumbing table is surfaced under a business name, so the renderer
    #: needs both: `name` for TMDL identifiers, `source_name` for the partition.
    source_name: str = ""
    is_hidden: bool = False
    description: str = ""
    columns: list[SemanticColumn] = field(default_factory=list)
    measures: list[Measure] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.source_name:
            self.source_name = self.name


@dataclass
class Relationship:
    name: str
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    #: "many" or "one". A 1:1 is declared from the entity side.
    from_cardinality: str = "many"
    #: "automatic" or "bothDirections". Power BI REJECTS THE WHOLE TMDL FILE on
    #: apply if a one-to-one does not carry bothDirections, so this is not a
    #: preference.
    cross_filtering: str = "automatic"
    is_active: bool = True
    #: Why this relationship exists. Carried into the generated TMDL as a
    #: comment, because the next person to open the file will otherwise wonder
    #: whether the inactive one is a mistake.
    why: str = ""


@dataclass
class SemanticModel:
    culture: str = "en-US"
    hub: str = HUB
    measure_host: str = DEFAULT_MEASURE_HOST
    tables: list[SemanticTable] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Plain data, for serializing to YAML or JSON."""
        return asdict(self)

    def table(self, name: str) -> SemanticTable | None:
        return next((t for t in self.tables if t.name == name), None)

    @property
    def inactive(self) -> list[Relationship]:
        return [r for r in self.relationships if not r.is_active]


def tmdl_type(sql_type: str) -> str:
    return TMDL_TYPES.get((sql_type or "").strip().upper(), DEFAULT_TMDL_TYPE)


def _format_string(data_type: str) -> str:
    return "0" if data_type == "int64" else ""


def _rel_name(from_table: str, from_column: str, to_table: str) -> str:
    """A deterministic, unique relationship identifier.

    Includes the source COLUMN because `_rel_all` relates to the hub twice and
    the two differ only by which endpoint they join on.
    """
    parts = f"{from_table}_{from_column}_to_{to_table}"
    safe = "".join(c if c.isalnum() else "_" for c in parts)
    return "gen_" + safe.strip("_").lower()


def _frame_columns(frame_key: str, *, hide_all: bool) -> list[SemanticColumn]:
    """Columns for a frame table, read from the DDL rather than restated.

    `ddl.FRAME_DDL` is the single declared place the frame's shape lives, and
    `test_ddl.py` already asserts it agrees with `report_model.FRAME_TABLES`.
    Restating the columns here is how the two drift.
    """
    out = []
    for name, sql_type in FRAME_DDL[frame_key]:
        dt = tmdl_type(sql_type)
        out.append(SemanticColumn(name=name, data_type=dt, is_hidden=hide_all,
                                  format_string=_format_string(dt)))
    return out


def _entity_columns(table) -> list[SemanticColumn]:
    """Columns for one vocabulary table, matching `ddl.entity_table_ddl`."""
    out = [
        SemanticColumn(name="ea_guid", data_type="string",
                       is_hidden="ea_guid" in HIDDEN_ENTITY_COLUMNS,
                       description="EA's stable identifier, and the join key."),
        SemanticColumn(name="name", data_type="string",
                       is_hidden="name" in HIDDEN_ENTITY_COLUMNS),
        SemanticColumn(name="metaclass", data_type="string",
                       is_hidden="metaclass" in HIDDEN_ENTITY_COLUMNS),
    ]
    for c in table.columns:
        dt = tmdl_type(c.sql_type)
        out.append(SemanticColumn(
            name=c.name,
            data_type=dt,
            is_hidden=c.name in HIDDEN_ENTITY_COLUMNS,
            format_string=_format_string(dt),
            description=c.description,
        ))
    return out


def traversal_measures(host: str, hub: str) -> list[Measure]:
    """The measures Power BI cannot produce on its own.

    Verified against SQLite ground truth 145/145, including all 22 cases where
    an element has inbound edges and no outbound ones - which is exactly where a
    model that silently reuses the active relationship gives a wrong answer that
    looks plausible.

    The zero-filled pair is not decoration. `SUMMARIZECOLUMNS` DROPS A ROW when
    every measure on it is BLANK: measured, 65 of 145 elements returned. DAX
    returns BLANK rather than 0 for an element with no edges in a direction, so
    a table visual built on the bare measures silently omits more than half the
    estate.
    """
    outbound = f"COUNTROWS('{host}')"
    inbound = (f"CALCULATE(COUNTROWS('{host}'), "
               f"USERELATIONSHIP('{host}'[target_guid], '{hub}'[ea_guid]))")
    return [
        Measure("Outbound edges", outbound,
                description="Edges where this element is the SOURCE. "
                            "Uses the active relationship."),
        Measure("Inbound edges", inbound,
                description="Edges where this element is the TARGET. Without "
                            "USERELATIONSHIP this silently returns the outbound count."),
        Measure("Outbound edges (zero-filled)", f"COALESCE({outbound}, 0)",
                description="Outbound count forced to zero. Use this in a table "
                            "visual: SUMMARIZECOLUMNS drops any row whose every "
                            "measure is BLANK."),
        Measure("Inbound edges (zero-filled)", f"COALESCE({inbound}, 0)",
                description="Inbound count forced to zero, for the same reason."),
    ]


def _relationships(entity_tables: list[str], *,
                   hub: str, host: str) -> list[Relationship]:
    """The 38-relationship hub shape, scaled to however many entities exist.

    Every vocabulary table is a 1:1 extension of the hub. Everything else hangs
    off the hub too. `package_id` is routed through the hub ONLY - vocabulary
    tables reaching `_pkg` independently is what created the ambiguous filter
    path that Power BI resolved by silently deactivating a real relationship.
    """
    out: list[Relationship] = []

    for t in entity_tables:
        out.append(Relationship(
            name=_rel_name(t, "ea_guid", hub),
            from_table=t, from_column="ea_guid",
            to_table=hub, to_column="ea_guid",
            from_cardinality="one",
            cross_filtering="bothDirections",
            why="vocabulary table is a 1:1 extension of the hub; Power BI "
                "rejects a one-to-one without bothDirections",
        ))

    #: Many-to-one into the hub. `_attribute` and `_operation` join on
    #: `element_guid`, not `ea_guid` - a detail that silently produces nothing
    #: if assumed.
    many_to_hub = [
        (physical("tag_value"), "ea_guid",
         "ALL multi-valued tag filtering goes through here, never the flat column"),
        (physical("overflow_tag"), "ea_guid", "sparse tags, below the column threshold"),
        (physical("attribute"), "element_guid", "attributes resolve to the hub"),
        (physical("operation"), "element_guid", "operations resolve to the hub"),
        (physical("diagram_object"), "ea_guid",
         "diagram membership; auto-detect deactivated this one silently"),
    ]
    # No `if table in present` guard. The frame is fixed and `FRAME_DDL` is
    # always walked in full, so the test could never be false - and it guarded
    # only five of the nine, so it was not even consistent with itself. A guard
    # that cannot fire reads like a handled case and is not one.
    for table, column, why in many_to_hub:
        out.append(Relationship(
            name=_rel_name(table, column, hub),
            from_table=table, from_column=column,
            to_table=hub, to_column="ea_guid",
            why=why,
        ))

    out += [
        Relationship(
            name=_rel_name(host, "source_guid", hub),
            from_table=host, from_column="source_guid",
            to_table=hub, to_column="ea_guid",
            why="outbound traversal; the column names do not match so Power BI "
                "cannot infer it",
        ),
        Relationship(
            name=_rel_name(host, "target_guid", hub),
            from_table=host, from_column="target_guid",
            to_table=hub, to_column="ea_guid",
            is_active=False,
            why="inbound traversal. INACTIVE BY DESIGN - one table pair may have "
                "only one active relationship. Reach it with USERELATIONSHIP",
        ),
        Relationship(
            name=_rel_name(hub, "package_id", physical("pkg")),
            from_table=hub, from_column="package_id",
            to_table=physical("pkg"), to_column="package_id",
            why="the ONLY path to the package tree; per-table package_id "
                "relationships would be ambiguous",
        ),
        Relationship(
            name=_rel_name(physical("diagram_object"), "diagram_id", physical("diagram")),
            from_table=physical("diagram_object"), from_column="diagram_id",
            to_table=physical("diagram"), to_column="diagram_id",
            why="diagram membership. `_diagram.package_id` is deliberately NOT "
                "related: it would close a loop through the hub and Power BI "
                "would deactivate one side of it without saying so",
        ),
    ]
    return out


def build_semantic_model(model: ReportModel, *,
                         culture: str = "en-US",
                         measure_host: str = DEFAULT_MEASURE_HOST) -> SemanticModel:
    """Turn a report model into a semantic model.

    Deterministic: vocabulary tables in the model's order, which the census
    already fixed, then frame tables in `FRAME_DDL`'s declared order.
    """
    hub = HUB
    host_source = physical("rel_all")

    # The measure host sits alongside the vocabulary tables, so its name must
    # not collide with one. A collision is SILENT: `render_definition` keys its
    # files by table name, so one simply disappears, and `model.tmdl` emits
    # `ref table` twice. Analysis Services compares table names
    # case-insensitively, so `relationships` and `Relationships` collide too.
    # Checked against the FRAME as well as the vocabulary. A guard that covers
    # only half the names it shares a namespace with reads as covered while the
    # failure it exists to make loud is still reachable.
    taken = {t.name for t in model.tables} | {physical(k) for k in FRAME_DDL}
    clash = next((n for n in sorted(taken)
                  if n.casefold() == measure_host.casefold()), None)
    if clash is not None:
        raise ValueError(
            f"measure_host {measure_host!r} collides with the table {clash!r} "
            f"(names are compared case-insensitively, as Analysis Services "
            f"does). Pass a different measure_host.")

    tables: list[SemanticTable] = []

    for t in model.tables:
        tables.append(SemanticTable(
            name=t.name,
            description=t.description,
            columns=_entity_columns(t),
        ))

    for frame_key in FRAME_DDL:
        name = physical(frame_key)
        if name == host_source:
            # Visible, business-named, every column hidden. See
            # DEFAULT_MEASURE_HOST for why this one is not hidden with the rest.
            tables.append(SemanticTable(
                name=measure_host,
                source_name=host_source,
                is_hidden=False,
                description="Relationships between elements, and the traversal "
                            "measures over them.",
                columns=_frame_columns(frame_key, hide_all=True),
                measures=traversal_measures(measure_host, hub),
            ))
            continue
        tables.append(SemanticTable(
            name=name,
            is_hidden=True,
            columns=_frame_columns(frame_key, hide_all=False),
        ))

    entity_names = [t.name for t in model.tables]

    return SemanticModel(
        culture=culture,
        hub=hub,
        measure_host=measure_host,
        tables=tables,
        relationships=_relationships(entity_names,
                                     hub=hub, host=measure_host),
    )
