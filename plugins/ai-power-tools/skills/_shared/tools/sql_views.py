#!/usr/bin/env python3
"""Express the logical model as SQL views over EA's physical schema.

PURE. No repository calls, no COM, no file or network I/O, no clock, no
randomness. Report model in, `CREATE VIEW` text out.

The third emitter on the shared contract (`APT-2026-0230`), beside
`load.build_database` and `parquet_out.build_parquet`. Those write a snapshot;
this writes DDL the customer runs once, after which Power BI reads the
repository live.

    census + technology -> report model -> +- SQLite + Parquet   (0211)
                                           +- Parquet            (0212)
                                           +- SQL view DDL       (THIS)

The views are generated once, from the census and the technology, and are then
static. An element stereotyped later appears immediately; a new stereotype or
tagged value needs the views regenerated. `REGENERATION_TRIGGER` says so in the
DDL header.

Placement reads `_stereo_block`, which parses `t_xref.Description` into one row
per `@STEREO;...@ENDSTEREO;` block. Whether an application carries an FQName is
a property of a block, not of the row: a multi-stereotype element packs several
blocks into one Description, and matches one table per block.

Declared-versus-observed drift, exclusion counts and the governance gate are
not reproduced here. They run in AI Power Tools against EA.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ddl import FRAME_DDL, physical
from report_model import BOOLEAN_FALSE, BOOLEAN_TRUE, ReportModel

#: Declared SQL type -> SQL Server type, beside `report_model.SQL_TYPES`,
#: `parquet_out.PARQUET_TYPES` and `semantic_model.TMDL_TYPES`. INTEGER is
#: `bigint` and REAL is `float` so a view column is as wide as the 64-bit
#: SQLite and Parquet columns. Every numeric type the emitter writes is read
#: from here; `test_the_numeric_types_are_written_only_in_the_type_map`
#: enforces that.
SQLSERVER_TYPES = {
    "TEXT": "nvarchar(max)",
    "INTEGER": "bigint",
    "REAL": "float",
}

_BIGINT = SQLSERVER_TYPES["INTEGER"]
_FLOAT = SQLSERVER_TYPES["REAL"]
_NTEXT = SQLSERVER_TYPES["TEXT"]

#: The declared types `_coerced_value` casts: every entry except TEXT.
NUMERIC_TYPES = frozenset(SQLSERVER_TYPES) - {"TEXT"}

#: Dialects with a tested emitter. Any other is refused rather than emitted.
SUPPORTED_DIALECTS = ("sqlserver",)

REGENERATION_TRIGGER = (
    "Regenerate these views whenever the modeling technology changes - a new "
    "stereotype or a new tagged value. Stereotyping an element against an "
    "EXISTING stereotype needs no regeneration: the views are static, the data "
    "is live, and that element appears immediately."
)

#: EA's own marker for a stereotype application.
XREF_NAME = "Stereotypes"
XREF_CONNECTOR_TYPE = "connector property"


class DialectError(Exception):
    pass


@dataclass
class ViewSet:
    dialect: str = ""
    ea_build: str = ""
    #: view name -> CREATE VIEW statement, in dependency order.
    views: dict[str, str] = field(default_factory=dict)
    header: str = ""

    @property
    def names(self) -> list[str]:
        return list(self.views)

    def script(self) -> str:
        """The whole thing as one runnable script."""
        parts = [self.header] if self.header else []
        for name in self.views:
            parts.append(f"{self.views[name]}\nGO\n")
        return "\n".join(parts)


def _q(identifier: str) -> str:
    """Bracket-quote an identifier, doubling any `]` inside it."""
    return "[" + identifier.replace("]", "]]") + "]"


def _lit(text: str) -> str:
    """An N-prefixed string literal with `'` doubled.

    The `N` matters because every column it is compared against is `nvarchar`:
    without it, a character outside the database's code page becomes `?` and
    the predicate matches nothing.
    """
    return "N'" + text.replace("'", "''") + "'"


def _comment(text: str) -> str:
    """Comment text with every line break replaced by a space.

    The header interpolates model values into `--` comments. A line break in
    one would end the comment and leave the rest of the value as DDL.
    """
    return text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")


def placement_predicate(table) -> str:
    """The test that places an element in one vocabulary table.

    A profile-bound table matches a block by FQName. An ad-hoc table matches a
    block with no FQName by stereotype name and metaclass, or, for an element
    with no stereotype block at all, `t_object.Stereotype` and metaclass. The
    two ad-hoc shapes follow `ea_census.entity_key` and `census_elements`.
    """
    key = table.entity_key
    # The shape is decided by `profile`, not by looking for `|` in the key: a
    # qualified name held in `t_object.Stereotype` gives a key containing both
    # `|` and `::`, and a stereotype name may itself contain `|`.
    if not table.profile:
        name = table.stereotype
        metaclass = key.rpartition("|")[2]
        return (f"(EXISTS (SELECT 1 FROM {_q('_stereo_block')} sb\n"
                f"                WHERE sb.ea_guid = o.ea_guid\n"
                f"                  AND sb.fqname = {_lit('')}\n"
                f"                  AND sb.stereo_name = {_lit(name)})\n"
                f"        OR (NOT EXISTS (SELECT 1 FROM {_q('_stereo_block')} sb2\n"
                f"                        WHERE sb2.ea_guid = o.ea_guid)\n"
                f"            AND o.Stereotype = {_lit(name)}))\n"
                f"       AND o.Object_Type = {_lit(metaclass)}")
    return (f"EXISTS (SELECT 1 FROM {_q('_stereo_block')} sb\n"
            f"               WHERE sb.ea_guid = o.ea_guid\n"
            f"                 AND sb.fqname = {_lit(key)})")


def _header(model: ReportModel, dialect: str, ea_build: str) -> str:
    lines = [
        "-- Logical reporting views over an Enterprise Architect repository.",
        "-- GENERATED - do not hand-edit. Regenerate instead.",
        "--",
        f"-- technology : {_comment(model.technology_name or model.technology_id)}",
        f"-- namespace  : {_comment(model.namespace)}",
        f"-- tables     : {len(model.tables)} vocabulary + {len(FRAME_DDL)} plumbing",
        f"-- dialect    : {dialect}",
    ]
    if ea_build:
        # EA's physical schema is not a public contract and can change between
        # builds. Stamping the build makes such a break diagnosable.
        lines.append(f"-- ea build   : {_comment(ea_build)}  <- these views were "
                     f"written against this schema")
    lines += ["--", "-- " + REGENERATION_TRIGGER.replace(". ", ".\n-- "), ""]
    return "\n".join(lines)


# ----------------------------------------------------------------- plumbing


def _stereo_block_view() -> str:
    """One row per stereotype block, with its name and FQName.

    The SQL counterpart of `ea_census.parse_stereotype_blocks`. `STRING_SPLIT`
    takes a one-character separator, so each block start is prefixed with
    CHAR(1) and the text is split on it. The name is read after `;Name=`,
    which does not occur inside `;FQName=`.
    """
    def field(prefix: str, alias: str) -> str:
        n = len(prefix)
        return (
            f"       CASE WHEN CHARINDEX({_lit(prefix)}, b.value) > 0\n"
            f"            THEN SUBSTRING(b.value, CHARINDEX({_lit(prefix)}, b.value) + {n},\n"
            f"                 CHARINDEX(';', b.value + ';',\n"
            f"                           CHARINDEX({_lit(prefix)}, b.value) + {n})\n"
            f"                 - CHARINDEX({_lit(prefix)}, b.value) - {n})\n"
            f"            ELSE '' END AS {alias}")

    return (
        f"CREATE VIEW {_q('_stereo_block')} AS\n"
        f"SELECT x.Client AS ea_guid,\n"
        f"       x.Type AS applies_to,\n"
        f"{field(';Name=', 'stereo_name')},\n"
        f"{field('FQName=', 'fqname')}\n"
        f"FROM t_xref x\n"
        f"CROSS APPLY STRING_SPLIT(\n"
        # Any CHAR(1) already in the text is removed before it is used as the
        # separator. The cast is there because `Description` is `ntext`; it
        # types no logical-model column, so it is not read from
        # `SQLSERVER_TYPES`.
        f"    REPLACE(REPLACE(CAST(x.Description AS nvarchar(max)),\n"
        f"                    CHAR(1), ''),\n"
        f"            '@STEREO;', CHAR(1) + '@STEREO;'), CHAR(1)) b\n"
        f"WHERE x.Name = {_lit(XREF_NAME)}\n"
        f"  AND b.value LIKE '@STEREO;%';"
    )


def _keymap_view(model: ReportModel) -> str:
    """The hub: one row per placed element.

    `entity_table` is the first table in model order that places the element,
    as `frame.element_rows` writes it; a `CASE` returns its first match.
    """
    whens = [f"           WHEN {placement_predicate(t)}\n"
             f"           THEN {_lit(t.name)}" for t in model.tables]
    if not whens:
        # A CASE whose only result is the NULL constant does not compile, so an
        # empty model gets typed NULL columns, like the other empty views.
        return (f"CREATE VIEW {_q(physical('element'))} AS\n"
                f"SELECT CAST(NULL AS nvarchar(40)) AS ea_guid,\n"
                f"       CAST(NULL AS nvarchar(255)) AS entity_table,\n"
                f"       CAST(NULL AS {_BIGINT}) AS package_id\n"
                f"WHERE 1 = 0;")
    case = "\n".join(whens)
    return (
        f"CREATE VIEW {_q(physical('element'))} AS\n"
        f"SELECT o.ea_guid,\n"
        f"       CASE\n{case}\n"
        f"       END AS entity_table,\n"
        f"       CAST(o.Package_ID AS {_BIGINT}) AS package_id\n"
        f"FROM t_object o\n"
        f"WHERE CASE\n{case}\n"
        f"      END IS NOT NULL;"
    )


def _pkg_view() -> str:
    """The package tree, with path and depth, by recursive CTE.

    A package whose parent is missing, zero or itself is a root with a NULL
    parent, as in `frame.package_rows`; dropping it would drop every element
    under it. A NULL name contributes `''` to `path`, also as there, so it does
    not empty the path of its subtree. Depth starts at 0.
    """
    return (
        f"CREATE VIEW {_q(physical('pkg'))} AS\n"
        f"WITH tree AS (\n"
        f"    SELECT CAST(p.Package_ID AS {_BIGINT}) AS Package_ID,\n"
        f"           CAST(NULL AS {_BIGINT}) AS Parent_ID, p.Name,\n"
        f"           CAST(COALESCE(p.Name, '') AS {_NTEXT}) AS path,\n"
        f"           CAST(0 AS {_BIGINT}) AS depth\n"
        f"    FROM t_package p\n"
        f"    WHERE p.Parent_ID IS NULL OR p.Parent_ID = 0\n"
        f"       OR p.Parent_ID = p.Package_ID\n"
        f"       OR NOT EXISTS (SELECT 1 FROM t_package q\n"
        f"                      WHERE q.Package_ID = p.Parent_ID)\n"
        f"    UNION ALL\n"
        f"    SELECT CAST(c.Package_ID AS {_BIGINT}), CAST(c.Parent_ID AS {_BIGINT}),\n"
        f"           c.Name,\n"
        f"           CAST(t.path + '/' + COALESCE(c.Name, '') AS {_NTEXT}),\n"
        f"           CAST(t.depth + 1 AS {_BIGINT})\n"
        f"    FROM t_package c\n"
        f"    JOIN tree t ON t.Package_ID = c.Parent_ID\n"
        f"                AND c.Parent_ID <> c.Package_ID\n"
        f")\n"
        f"SELECT Package_ID AS package_id, NULLIF(Parent_ID, 0) AS parent_id,\n"
        f"       COALESCE(Name, '') AS name,\n"
        f"       path, depth\n"
        f"FROM tree;"
    )


def _rel_all_view() -> str:
    """Connectors whose BOTH endpoints are placed.

    Scoped to the key map on both ends, exactly as `frame.relationship_rows`
    does: an edge touching an unplaced element would dangle, and a dangling row
    makes an inner join return quietly fewer rows than a total read elsewhere.
    """
    hub = _q(physical("element"))
    return (
        f"CREATE VIEW {_q(physical('rel_all'))} AS\n"
        f"SELECT CAST(c.Connector_ID AS {_BIGINT}) AS connector_id,\n"
        f"       so.ea_guid AS source_guid,\n"
        f"       eo.ea_guid AS target_guid,\n"
        f"       COALESCE(c.Connector_Type, '') AS connector_type,\n"
        f"       COALESCE(c.Stereotype, '') AS stereotype,\n"
        f"       COALESCE(cs.profile, '') AS profile,\n"
        f"       COALESCE(c.Name, '') AS name\n"
        f"FROM t_connector c\n"
        f"JOIN t_object so ON so.Object_ID = c.Start_Object_ID\n"
        f"JOIN t_object eo ON eo.Object_ID = c.End_Object_ID\n"
        f"JOIN {hub} ks ON ks.ea_guid = so.ea_guid\n"
        f"JOIN {hub} kt ON kt.ea_guid = eo.ea_guid\n"
        f"LEFT JOIN (SELECT sb.ea_guid,\n"
        f"                  MAX(CASE WHEN CHARINDEX('::', sb.fqname) > 0\n"
        f"                           THEN LEFT(sb.fqname,\n"
        f"                                     CHARINDEX('::', sb.fqname) - 1)\n"
        f"                           ELSE '' END) AS profile\n"
        f"           FROM {_q('_stereo_block')} sb\n"
        f"           WHERE sb.applies_to = {_lit(XREF_CONNECTOR_TYPE)}\n"
        f"           GROUP BY sb.ea_guid) cs ON cs.ea_guid = c.ea_guid;"
    )


def _tag_value_view(model: ReportModel) -> str:
    """The multi-value bridge: one row per value, never per tag.

    Only tags the model declares multi-valued are split on `,`, because a single
    value may itself contain a comma. Both arms trim, as `pivot` strips every
    tagged value, and empty values are dropped.
    """
    multi = sorted({c.source_tag for t in model.tables for c in t.columns
                    if c.multi_valued})
    hub = _q(physical("element"))
    if multi:
        in_list = ", ".join(_lit(m) for m in multi)
        split = (
            f"UNION ALL\n"
            f"SELECT k.ea_guid, p.Property AS tag, LTRIM(RTRIM(v.value)) AS value\n"
            f"FROM t_objectproperties p\n"
            f"JOIN t_object o ON o.Object_ID = p.Object_ID\n"
            f"JOIN {hub} k ON k.ea_guid = o.ea_guid\n"
            f"CROSS APPLY STRING_SPLIT(p.Value, ',') v\n"
            f"WHERE p.Property IN ({in_list})\n"
            f"  AND LTRIM(RTRIM(COALESCE(v.value, ''))) <> ''\n"
        )
        single_filter = f"  AND p.Property NOT IN ({in_list})\n"
    else:
        split = ""
        single_filter = ""
    return (
        f"CREATE VIEW {_q(physical('tag_value'))} AS\n"
        f"SELECT k.ea_guid, p.Property AS tag, LTRIM(RTRIM(p.Value)) AS value\n"
        f"FROM t_objectproperties p\n"
        f"JOIN t_object o ON o.Object_ID = p.Object_ID\n"
        f"JOIN {hub} k ON k.ea_guid = o.ea_guid\n"
        f"WHERE LTRIM(RTRIM(COALESCE(p.Value, ''))) <> ''\n"
        f"{single_filter}"
        f"{split};"
    )


def _simple_join_view(view: str, select: str, source: str,
                      guid_column: str) -> str:
    """A frame view scoped to the key map on one guid column."""
    hub = _q(physical("element"))
    return (
        f"CREATE VIEW {_q(view)} AS\n"
        f"SELECT {select}\n"
        f"FROM {source}\n"
        f"JOIN {hub} k ON k.ea_guid = {guid_column};"
    )


def _overflow_tag_view(model: ReportModel) -> str:
    """Sparse tags, which became rows rather than columns.

    Empty values are kept, matching `pivot`, which writes an overflow row for
    every such tag on a placed element whether or not it is populated.
    `_tag_value` drops empty values; the two bridges differ here on purpose.
    """
    overflow = sorted({tag for t in model.tables for tag in t.overflow_tags})
    hub = _q(physical("element"))
    if not overflow:
        return (f"CREATE VIEW {_q(physical('overflow_tag'))} AS\n"
                f"SELECT CAST(NULL AS nvarchar(40)) AS ea_guid,\n"
                f"       CAST(NULL AS nvarchar(255)) AS tag,\n"
                f"       CAST(NULL AS {_NTEXT}) AS value\n"
                f"WHERE 1 = 0;")
    # Scoped per table, by that table's placement predicate. A tag is overflow
    # for one stereotype and may be an ordinary column on another, and
    # `_keymap.entity_table` names only the first table a multi-stereotype
    # element is placed in.
    parts = []
    for t in model.tables:
        if not t.overflow_tags:
            continue
        in_list = ", ".join(_lit(tag) for tag in sorted(t.overflow_tags))
        parts.append(
            f"SELECT o.ea_guid, p.Property AS tag, p.Value AS value\n"
            f"FROM t_object o\n"
            f"JOIN t_objectproperties p ON p.Object_ID = o.Object_ID\n"
            f"WHERE {placement_predicate(t)}\n"
            f"  AND p.Property IN ({in_list})")
    return (f"CREATE VIEW {_q(physical('overflow_tag'))} AS\n"
            + "\nUNION ALL\n".join(parts) + ";")


def _load_run_view(model: ReportModel, ea_build: str) -> str:
    """There is no build on this path, so this describes the connection.

    It exists because the semantic model expects the same table set on every
    path. `run_id` is `live`, and the counts are NULL because nothing is
    reconciled here.
    """
    return (
        f"CREATE VIEW {_q(physical('load_run'))} AS\n"
        f"SELECT CAST('live' AS nvarchar(40)) AS run_id,\n"
        f"       CONVERT(nvarchar(30), SYSUTCDATETIME(), 126) AS run_at,\n"
        f"       CAST({_lit(model.technology_name or model.technology_id)}"
        f" AS nvarchar(255)) AS repository,\n"
        f"       CAST({_lit(ea_build or '')} AS nvarchar(100)) AS spec_hash,\n"
        f"       CAST(NULL AS {_BIGINT}) AS rows_loaded,\n"
        f"       CAST(NULL AS {_BIGINT}) AS reconciled,\n"
        f"       CAST(NULL AS {_BIGINT}) AS mismatches;"
    )


def _tag_coverage_view(model: ReportModel) -> str:
    """Coverage per declared column, computed live."""
    hub = _q(physical("element"))
    parts = []
    for t in model.tables:
        for c in t.columns:
            parts.append(
                # The casts set the column type; the sums still accumulate in
                # `int`.
                f"SELECT {_lit(t.name)} AS table_name, {_lit(c.source_tag)} AS tag,\n"
                f"       CAST(COALESCE(SUM(CASE WHEN p.Property IS NOT NULL"
                f" THEN 1 ELSE 0 END), 0) AS {_BIGINT}) AS present,\n"
                f"       CAST(COALESCE(SUM(CASE WHEN LTRIM(RTRIM(COALESCE(p.Value, '')))"
                f" <> '' THEN 1 ELSE 0 END), 0) AS {_BIGINT}) AS populated,\n"
                f"       CAST(COUNT(DISTINCT o.ea_guid) AS {_BIGINT}) AS total,\n"
                # Divided by COUNT(DISTINCT), the denominator `total` uses,
                # because `t_objectproperties` can hold the same tag twice for
                # one element.
                f"       CASE WHEN COUNT(DISTINCT o.ea_guid) = 0 THEN 0.0 ELSE\n"
                # Rounded as `tag_coverage` rounds.
                f"            ROUND(CAST(SUM(CASE WHEN"
                f" LTRIM(RTRIM(COALESCE(p.Value, ''))) <> ''"
                f" THEN 1 ELSE 0 END) AS {_FLOAT})\n"
                f"                  / COUNT(DISTINCT o.ea_guid), 4) END AS coverage\n"
                f"FROM t_object o\n"
                f"LEFT JOIN t_objectproperties p\n"
                f"       ON p.Object_ID = o.Object_ID AND p.Property = {_lit(c.source_tag)}\n"
                f"WHERE {placement_predicate(t)}")
    if not parts:
        return (f"CREATE VIEW {_q(physical('tag_coverage'))} AS\n"
                f"SELECT CAST(NULL AS nvarchar(255)) AS table_name,\n"
                f"       CAST(NULL AS nvarchar(255)) AS tag,\n"
                f"       CAST(NULL AS {_BIGINT}) AS present, CAST(NULL AS {_BIGINT}) AS populated,\n"
                f"       CAST(NULL AS {_BIGINT}) AS total, CAST(NULL AS {_FLOAT}) AS coverage\n"
                f"WHERE 1 = 0;")
    return (f"CREATE VIEW {_q(physical('tag_coverage'))} AS\n"
            + "\nUNION ALL\n".join(parts) + ";")


# -------------------------------------------------------------- vocabulary


#: Indent for the continuation lines of a multi-line `CASE` in an entity column.
_VALUE_INDENT = " " * 26


def _coerced_value(column) -> str:
    """One tagged value as its declared type: `report_model.coerce_value` in SQL.

    Trimmed first, as `pivot` strips before it coerces. TEXT is returned trimmed
    and uncast, so an empty value stays `''`. On a typed column an empty value
    is NULL; on INTEGER, EA's boolean strings map to 1 and 0, compared
    lowercased as the Python does; anything else goes through `TRY_CAST`, so a
    value that does not convert is NULL where `pivot` leaves the column unset.

    Known limit: `LTRIM`/`RTRIM` remove spaces only, where `str.strip()`
    removes all whitespace, and `TRY_CAST` accepts fewer numeric spellings than
    `int()`/`float()`. Such a value can be NULL here and populated in the
    reporting database.
    """
    value = "LTRIM(RTRIM(COALESCE(p.Value, '')))"
    if column.sql_type not in NUMERIC_TYPES:
        return value
    lines = [f"CASE WHEN {value} = {_lit('')} THEN NULL"]
    if column.sql_type == "INTEGER":
        for literals, result in ((BOOLEAN_TRUE, "1"), (BOOLEAN_FALSE, "0")):
            in_list = ", ".join(_lit(s) for s in sorted(literals))
            lines.append(f"{_VALUE_INDENT}WHEN LOWER({value}) IN ({in_list})"
                         f" THEN {result}")
    # A subscript: everything past the early return is a key of the map.
    cast = SQLSERVER_TYPES[column.sql_type]
    lines.append(f"{_VALUE_INDENT}ELSE TRY_CAST({value} AS {cast}) END")
    return "\n".join(lines)


def _entity_view(table) -> str:
    """One view per stereotype, in the customer's own business vocabulary.

    One correlated `TOP 1` subquery per column, coerced by `_coerced_value`.
    Column order matches `ddl.entity_table_ddl` and `load.entity_columns`. An
    absent tag is NULL on any column type.

    `ORDER BY p.PropertyID DESC` makes `TOP 1` deterministic and takes the later
    of two rows for the same tag. That reproduces `pivot`, which lets a later
    row overwrite an earlier one, so a populated value can lose to an empty
    duplicate. It is a `pivot` defect (`APT-2026-0239`), reproduced here so the
    paths agree, and it agrees only where extract order is `PropertyID` order.
    """
    cols = [
        "       o.ea_guid,",
        "       COALESCE(o.Name, '') AS name,",
        "       COALESCE(o.Object_Type, '') AS metaclass,",
    ]
    for c in table.columns:
        cols.append(
            f"       (SELECT TOP 1 {_coerced_value(c)}\n"
            f"          FROM t_objectproperties p\n"
            f"         WHERE p.Object_ID = o.Object_ID\n"
            f"           AND p.Property = {_lit(c.source_tag)}\n"
            f"         ORDER BY p.PropertyID DESC) AS {_q(c.name)},")
    body = "\n".join(cols).rstrip(",")
    return (
        f"CREATE VIEW {_q(table.name)} AS\n"
        f"SELECT\n{body}\n"
        f"FROM t_object o\n"
        f"WHERE {placement_predicate(table)};"
    )


def build_views(model: ReportModel, *, dialect: str = "sqlserver",
                ea_build: str = "") -> ViewSet:
    """Every view expressing the logical model, in dependency order.

    `_stereo_block` first because the key map reads it, then the key map because
    everything else is scoped to it.
    """
    if dialect not in SUPPORTED_DIALECTS:
        raise DialectError(
            f"{dialect!r} is not a supported dialect. Supported: "
            f"{', '.join(SUPPORTED_DIALECTS)}. Emitting SQL for an untested "
            f"backend is how a customer gets a script nobody has run."
        )

    views: dict[str, str] = {
        "_stereo_block": _stereo_block_view(),
        physical("element"): _keymap_view(model),
        physical("pkg"): _pkg_view(),
        physical("rel_all"): _rel_all_view(),
        physical("tag_value"): _tag_value_view(model),
        physical("overflow_tag"): _overflow_tag_view(model),
        physical("tag_coverage"): _tag_coverage_view(model),
        physical("load_run"): _load_run_view(model, ea_build),
        # Not scoped to the key map: a diagram exists whether or not anything
        # on it is placed.
        physical("diagram"): (
            f"CREATE VIEW {_q(physical('diagram'))} AS\n"
            f"SELECT CAST(d.Diagram_ID AS {_BIGINT}) AS diagram_id,\n"
            f"       COALESCE(d.Name, '') AS name,\n"
            f"       COALESCE(d.Diagram_Type, '') AS diagram_type,\n"
            f"       CAST(d.Package_ID AS {_BIGINT}) AS package_id\n"
            f"FROM t_diagram d;"),
        physical("diagram_object"): _simple_join_view(
            physical("diagram_object"),
            f"CAST(do.Diagram_ID AS {_BIGINT}) AS diagram_id, o.ea_guid AS ea_guid",
            "t_diagramobjects do\nJOIN t_object o ON o.Object_ID = do.Object_ID",
            "o.ea_guid"),
        physical("attribute"): _simple_join_view(
            physical("attribute"),
            f"CAST(a.ID AS {_BIGINT}) AS attribute_id, o.ea_guid AS element_guid,\n"
            "COALESCE(a.Name, '') AS name,\n"
            "       COALESCE(a.Type, '') AS attr_type, COALESCE(a.Scope, '') AS scope",
            "t_attribute a\nJOIN t_object o ON o.Object_ID = a.Object_ID",
            "o.ea_guid"),
        physical("operation"): _simple_join_view(
            physical("operation"),
            f"CAST(op.OperationID AS {_BIGINT}) AS operation_id, o.ea_guid AS element_guid,\n"
            "       COALESCE(op.Name, '') AS name, COALESCE(op.Type, '') AS return_type, COALESCE(op.Scope, '') AS scope",
            "t_operation op\nJOIN t_object o ON o.Object_ID = op.Object_ID",
            "o.ea_guid"),
    }
    for table in model.tables:
        views[table.name] = _entity_view(table)

    return ViewSet(dialect=dialect, ea_build=ea_build, views=views,
                   header=_header(model, dialect, ea_build))


def drop_script(view_set: ViewSet) -> str:
    """Drop in reverse dependency order, so a regeneration is re-runnable."""
    lines = [f"DROP VIEW IF EXISTS {_q(n)};\nGO" for n in reversed(view_set.names)]
    return "\n".join(lines) + "\n"
