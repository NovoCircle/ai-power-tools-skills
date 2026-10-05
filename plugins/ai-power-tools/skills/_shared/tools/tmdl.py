#!/usr/bin/env python3
"""Render a semantic model as TMDL.

PURE. No file or network I/O, no clock, no randomness. It turns a
`SemanticModel` plus a partition source into text, keyed by the path each piece
belongs at. Writing it to disk is the caller's job.

THE CALLER MUST WRITE WITH `newline=""`
---------------------------------------
Every string this module returns is CRLF-terminated, because Power BI's own
projects are and a generated file that deviates is rejected on apply. On Windows
`open(path, "w")` translates "\\n" to "\\r\\n", which would turn our "\\r\\n" into
"\\r\\r\\n". So:

    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)

UTF-8 without a BOM, likewise read off a real project rather than assumed.

FORMAT RULES THAT ARE NOT PREFERENCES
-------------------------------------
TMDL is TAB-indented; spaces do not parse. A one-to-one relationship must carry
`crossFilteringBehavior: bothDirections` or Power BI rejects THE WHOLE FILE on
apply - not the offending line. Descriptions are `///` lines PRECEDING the object
they describe. All of this was read from a Power BI 2.158 project on disk.

LINEAGE TAGS ARE DERIVED, NEVER MINTED
--------------------------------------
Every tag is `uuid5` of the object's path under a fixed namespace, so two runs
over the same model produce byte-identical files and a report's field bindings
survive regeneration. Minting fresh GUIDs per run is what would break them.
Whether a report survives a tag that genuinely CHANGES is still untested - see
`APT-2026-0211`.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass

from semantic_model import Relationship, SemanticModel, SemanticTable

#: Fixed namespace, so a tag is a pure function of the object's path. Changing
#: this value re-tags every object in every model anyone has generated, which
#: is the one change here that could break an existing report.
NS = uuid.UUID("6f1b7a52-0b4e-5c7a-9d33-0e5a7c2f41aa")

NEWLINE = "\r\n"
T = "\t"

#: Read from a 2.158 project. Version-pinned facts about the host, not choices.
COMPATIBILITY_LEVEL = "1606"


def lineage_tag(kind: str, path: str) -> str:
    return str(uuid.uuid5(NS, f"{kind}:{path}"))


def ident(name: str) -> str:
    """A TMDL identifier, quoted only when it has to be."""
    if name and all(c.isalnum() or c in "_" for c in name):
        return name
    return "'" + name.replace("'", "''") + "'"


def description_lines(text: str, indent: str) -> list[str]:
    """`///` lines preceding an object. Collapsed to one line each."""
    if not text:
        return []
    flat = " ".join(text.split())
    return [f"{indent}/// {flat}"]


# --------------------------------------------------------------- partitions


@dataclass
class ParquetSource:
    """Power BI reads files our toolchain produced. `APT-2026-0211` / `0212`.

    Deliberately bare M: no `Table.PromoteHeaders`, no `TransformColumnTypes`.
    A self-describing format needs neither, and that is measured - the same
    tables loaded via Excel arrived as `Column1...ColumnN`.
    """
    directory: str
    mode: str = "import"
    suffix: str = ".parquet"

    def expression(self, table: SemanticTable) -> list[str]:
        sep = "" if self.directory.endswith(("\\", "/")) else "\\"
        path = f"{self.directory}{sep}{table.source_name}{self.suffix}"
        return [
            "let",
            f'    Source = Parquet.Document(File.Contents("{path}"))',
            "in",
            "    Source",
        ]


@dataclass
class SqlSource:
    """Power BI reads the repository itself, through generated views.

    `APT-2026-0230`, where DirectQuery is the primary mode. The traversal
    measures have NOT been verified under DirectQuery - that verification is
    part of `0230` and must not be carried over from the Import result.
    """
    server: str
    database: str
    schema: str = "dbo"
    mode: str = "directQuery"

    def expression(self, table: SemanticTable) -> list[str]:
        return [
            "let",
            f'    Source = Sql.Database("{self.server}", "{self.database}"),',
            f'    Data = Source{{[Schema="{self.schema}",'
            f'Item="{table.source_name}"]}}[Data]',
            "in",
            "    Data",
        ]


def partition_block(table: SemanticTable, source) -> list[str]:
    """The partition, and the ONLY part of a table file that varies by path.

    `test_tmdl.py` asserts that: render a model for two sources and everything
    outside this block is byte-identical.
    """
    out = [f"{T}partition {ident(table.name)} = m",
           f"{T}{T}mode: {source.mode}",
           f"{T}{T}source ="]
    out += [f"{T * 4}{line}" for line in source.expression(table)]
    out.append("")
    return out


# ------------------------------------------------------------------ tables


def render_column(table: SemanticTable, column) -> list[str]:
    path = f"{table.name}.{column.name}"
    out = description_lines(column.description, T)
    out.append(f"{T}column {ident(column.name)}")
    out.append(f"{T}{T}dataType: {column.data_type}")
    if column.is_hidden:
        out.append(f"{T}{T}isHidden")
    if column.format_string:
        out.append(f"{T}{T}formatString: {column.format_string}")
    out += [f"{T}{T}lineageTag: {lineage_tag('column', path)}",
            f"{T}{T}summarizeBy: {column.summarize_by}",
            f"{T}{T}sourceColumn: {column.source_column}",
            "",
            # `Automatic` alongside an explicit `summarizeBy` looks like a
            # contradiction - it says the CLIENT chose. VERIFIED 2026-10-05
            # against the live engine that it does not override us:
            # TMSCHEMA_COLUMNS reports SummarizeBy=2 (None) on all 235 real
            # columns, including the INTEGER ones, and the 40 at 1 (Default) are
            # Power BI's own RowNumber columns. A model that DOES sum was open
            # on another engine at the same time for contrast.
            f"{T}{T}annotation SummarizationSetBy = Automatic",
            ""]
    return out


def render_measure(measure) -> list[str]:
    out = description_lines(measure.description, T)
    out.append(f"{T}measure {ident(measure.name)} = {measure.expression}")
    if measure.format_string:
        out.append(f"{T}{T}formatString: {measure.format_string}")
    out.append("")
    return out


def render_table(table: SemanticTable, source) -> str:
    lines = description_lines(table.description, "")
    lines.append(f"table {ident(table.name)}")
    if table.is_hidden:
        lines.append(f"{T}isHidden")
    lines += [f"{T}lineageTag: {lineage_tag('table', table.name)}", ""]
    for measure in table.measures:
        lines += render_measure(measure)
    for column in table.columns:
        lines += render_column(table, column)
    lines += partition_block(table, source)
    lines += [f"{T}annotation PBI_ResultType = Table", ""]
    return NEWLINE.join(lines)


# ----------------------------------------------------------- relationships


def render_relationship(rel: Relationship) -> list[str]:
    # NO description line. MEASURED 2026-10-02 on Power BI 2.158.1177.0: a `///`
    # line before `relationship` sets a `description` property, and
    # `SingleColumnRelationship` has none. The whole project then fails to open
    # with "Property 'description' is unknown and is not expected in the
    # situation it appears" - no file named, no line number, and the semantic
    # model does not load at all.
    #
    # Tables, columns and measures DO take descriptions. Relationships do not.
    # `Relationship.why` is kept on the dataclass because the rationale is worth
    # having - it just cannot travel in the TMDL.
    out = [f"relationship {rel.name}"]
    if not rel.is_active:
        out.append(f"{T}isActive: false")
    if rel.cross_filtering != "automatic":
        out.append(f"{T}crossFilteringBehavior: {rel.cross_filtering}")
    if rel.from_cardinality != "many":
        out.append(f"{T}fromCardinality: {rel.from_cardinality}")
    out += [f"{T}fromColumn: {ident(rel.from_table)}.{ident(rel.from_column)}",
            f"{T}toColumn: {ident(rel.to_table)}.{ident(rel.to_column)}",
            ""]
    return out


def render_relationships(model: SemanticModel) -> str:
    lines: list[str] = []
    for rel in model.relationships:
        lines += render_relationship(rel)
    return NEWLINE.join(lines)


# ------------------------------------------------------- model and friends


def render_model(model: SemanticModel) -> str:
    names = [t.name for t in model.tables]
    lines = [
        "model Model",
        f"{T}culture: {model.culture}",
        f"{T}defaultPowerBIDataSourceVersion: powerBI_V3",
        f"{T}sourceQueryCulture: {model.culture}",
        f"{T}valueFilterBehavior: independent",
        f"{T}dataAccessOptions",
        f"{T}{T}legacyRedirects",
        f"{T}{T}returnErrorValuesAsNull",
        "",
        # 0 suppresses Power BI's automatic LocalDateTable_* and
        # DateTableTemplate_* tables.
        #
        # That behavior was observed against a DATETIME-typed column. Since
        # APT-2026-0226 the schema exposes none - `report_model.SQL_TYPES` maps
        # both `date` and `datetime` to TEXT - so the current model does not
        # stress it, and this annotation is emitted to keep the suppression true
        # if a datetime column is ever exposed rather than because it was
        # re-observed here.
        "annotation __PBI_TimeIntelligenceEnabled = 0",
        "",
        "annotation PBI_QueryOrder = [%s]" % ",".join('"%s"' % n for n in names),
        "",
    ]
    lines += [f"ref table {ident(n)}" for n in names]
    lines += ["", f"ref cultureInfo {model.culture}", ""]
    return NEWLINE.join(lines)


def render_database(compatibility_level: str = COMPATIBILITY_LEVEL) -> str:
    return NEWLINE.join(["database",
                         f"{T}compatibilityLevel: {compatibility_level}",
                         ""])


def render_culture(culture: str = "en-US") -> str:
    return NEWLINE.join([
        f"cultureInfo {culture}",
        "",
        f"{T}linguisticMetadata = ",
        f"{T * 3}{{",
        f'{T * 3}  "Version": "1.0.0",',
        f'{T * 3}  "Language": "{culture}"',
        f"{T * 3}}}",
        "",
        f"{T}{T}contentType: json",
        "",
    ])


def render_definition(model: SemanticModel, source) -> dict[str, str]:
    """Every file in a `.pbip` semantic model's `definition/` folder.

    Keyed by path relative to `definition/`, with forward slashes. The caller
    writes them - see the module docstring on `newline=""`.
    """
    out = {
        "database.tmdl": render_database(),
        "model.tmdl": render_model(model),
        "relationships.tmdl": render_relationships(model),
        f"cultures/{model.culture}.tmdl": render_culture(model.culture),
    }
    for table in model.tables:
        out[f"tables/{table.name}.tmdl"] = render_table(table, source)
    return out
