#!/usr/bin/env python3
"""Express the logical model as SQL views over EA's physical schema.

PURE. No repository calls, no COM, no file or network I/O, no clock, no
randomness. Report model in, `CREATE VIEW` text out.

This is the third emitter on the shared contract (`APT-2026-0230`). Where
`load.build_database` and `parquet_out.build_parquet` produce a SNAPSHOT our
toolchain wrote, this produces DDL the customer owns and runs once, after which
Power BI reads their repository live and we have no runtime involvement at all.

    census + technology -> report model -> +- SQLite + Parquet   (0211)
                                           +- Parquet            (0212)
                                           +- SQL view DDL       (THIS)

WHY GENERATING SQL IS DEFENSIBLE HERE AND WAS NOT IN 0210
---------------------------------------------------------
`PLAN-APT-0210` §4.4 rejected SQL for the pivot: it "would be generated per
stereotype per run: unvalidatable and different every time someone adds a tagged
value." That objection does not transfer. Here the SQL is generated ONCE at
setup, from the census plus the technology, and is then static DDL the customer
can read, review and put in source control. Regenerating per RUN was the
complaint; regenerating per SCHEMA CHANGE is ordinary database work.

The consequence has to be stated rather than discovered: the views are static
and the data is live, so an element stereotyped AFTER generation appears
immediately, but a NEW STEREOTYPE gets no view until the views are regenerated.
`REGENERATION_TRIGGER` is that statement, and it is emitted into the DDL header.

HOW AN ELEMENT IS PLACED, AND WHY THE TRAILING SEMICOLON MATTERS
----------------------------------------------------------------
EA records a stereotype application in `t_xref.Description` as one or more
`@STEREO;...@ENDSTEREO;` blocks. An element is placed by a stereotype only when
its block carries `FQName=` - a bare `Name=` is an ad-hoc application, which the
census reports as drift rather than placing. Getting that wrong dropped 24
elements in the prototype.

The generator knows every FQName from the census, so it tests for the literal
rather than parsing blocks in SQL:

    Description LIKE '%FQName=<ns>::<name>;%'

**The trailing semicolon is load-bearing.** Without it `WBAVendorSystem` also
matches `WBAVendorSystemGateway`, and a technology with one name a prefix of
another would silently over-place every element of the longer one.

A multi-stereotype element matches several of these at once. Measured on the
reference model: `WBABusinessApplication` counts 46 by `t_object.Stereotype` and
**47** by correct block reading, because one element carries two stereotypes and
the column only mirrors the first.

WHAT THESE VIEWS DELIBERATELY DO NOT DO
---------------------------------------
Coverage, declared-versus-observed drift, exclusion counts and the governance
gate. Settled 2026-10-02: those stay in AI Power Tools running against EA, which
talks to whatever backend the customer has. Re-implementing the census rules a
second time in a second language is exactly what `APT-2026-0210` structured
itself to prevent.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ddl import FRAME_DDL, physical
from report_model import ReportModel

#: Dialects with a tested emitter. An unsupported backend is told so rather than
#: handed SQL nobody has ever run - `APT-2026-0218` is already open on an
#: unparenthesized join that may not survive Jet, and generated SQL multiplies
#: that exposure.
SUPPORTED_DIALECTS = ("sqlserver",)

REGENERATION_TRIGGER = (
    "Regenerate these views whenever the modeling technology changes - a new "
    "stereotype or a new tagged value. Stereotyping an element against an "
    "EXISTING stereotype needs no regeneration: the views are static, the data "
    "is live, and that element appears immediately."
)

#: EA's own marker for a stereotype application.
XREF_NAME = "Stereotypes"
XREF_ELEMENT_TYPE = "element property"
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
    """Bracket-quote. SQL Server's own form, and it tolerates a leading `_`."""
    return "[" + identifier.replace("]", "]]") + "]"


def _lit(text: str) -> str:
    return "'" + str(text).replace("'", "''") + "'"


def placement_predicate(table) -> str:
    """The test that places an element in one vocabulary table.

    TWO SHAPES, because the census has two. `ea_census.entity_key` keys a
    profile-bound application by its FQName and an ad-hoc one by
    `name|metaclass` - a bare name is ambiguous across languages, so the
    metaclass has to carry identity.

    Reading only the FQName form silently emptied 14 of 29 tables on the
    reference model and left the key map 14 elements short, which then cascaded
    into the relationship and diagram views. Measured, not hypothetical.
    """
    key = table.entity_key
    if "|" in key and "::" not in key:
        name, _, metaclass = key.partition("|")
        # THREE shapes, not two. Besides an ad-hoc block in `t_xref`, an element
        # with NO xref entry at all falls back to the bare `t_object.Stereotype`
        # column - `census_elements` says so and two elements on the reference
        # model are exactly that: an Actor stereotyped BusinessActor and a
        # Component stereotyped SystemSoftware, each with zero xref rows.
        # Missing them left the key map 2 short and emptied both their tables.
        return (f"(EXISTS (SELECT 1 FROM {_q('_stereo_block')} sb\n"
                f"                WHERE sb.ea_guid = o.ea_guid\n"
                f"                  AND sb.fqname = ''\n"
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
        f"-- technology : {model.technology_name or model.technology_id}",
        f"-- namespace  : {model.namespace}",
        f"-- tables     : {len(model.tables)} vocabulary + {len(FRAME_DDL)} plumbing",
        f"-- dialect    : {dialect}",
    ]
    if ea_build:
        # EA's physical schema is not a public contract: Sparx can change the
        # t_xref encoding between builds, and in this path that break lands in
        # views the CUSTOMER owns, silently, on upgrade. Stamping the build is
        # the cheapest thing that makes the breakage diagnosable.
        lines.append(f"-- ea build   : {ea_build}  <- these views were written "
                     f"against this schema")
    lines += ["--", "-- " + REGENERATION_TRIGGER.replace(". ", ".\n-- "), ""]
    return "\n".join(lines)


# ----------------------------------------------------------------- plumbing


def _stereo_block_view() -> str:
    """ONE ROW PER STEREOTYPE BLOCK, with its name and FQName pulled out.

    This is the SQL equivalent of `ea_census.parse_stereotype_blocks`, and it is
    a view rather than a substring test for a reason: a multi-stereotype element
    packs several `@STEREO;...@ENDSTEREO;` blocks into ONE `t_xref.Description`,
    and `A has an FQName` is a property of a BLOCK, not of the row. Matching
    against the whole string cannot tell "this element has an ad-hoc Device
    application" from "this element has some other stereotype that happens to be
    profile-bound".

    Splitting: `STRING_SPLIT` takes a single-character separator, so each block
    start is prefixed with CHAR(1) and the string is split on that. CHAR(1) is
    not a character EA writes into a stereotype block.

    `Name=` is also a substring of `FQName=`, so the name is read from the FIRST
    occurrence - EA always writes Name first within a block.
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
        f"{field('Name=', 'stereo_name')},\n"
        f"{field('FQName=', 'fqname')}\n"
        f"FROM t_xref x\n"
        f"CROSS APPLY STRING_SPLIT(\n"
        f"    REPLACE(CAST(x.Description AS nvarchar(max)),\n"
        f"            '@STEREO;', CHAR(1) + '@STEREO;'), CHAR(1)) b\n"
        f"WHERE x.Name = {_lit(XREF_NAME)}\n"
        f"  AND b.value LIKE '@STEREO;%';"
    )


def _keymap_view(model: ReportModel) -> str:
    """The hub: one row per PLACED element.

    `entity_table` names the FIRST table in model order for a multi-stereotype
    element, which is what `frame.element_rows` writes. A CASE evaluated in
    model order gives exactly that, because CASE returns on first match.
    """
    whens = [f"           WHEN {placement_predicate(t)}\n"
             f"           THEN {_lit(t.name)}" for t in model.tables]
    case = "\n".join(whens) if whens else "           WHEN 1 = 0 THEN NULL"
    return (
        f"CREATE VIEW {_q(physical('element'))} AS\n"
        f"SELECT o.ea_guid,\n"
        f"       CASE\n{case}\n"
        f"       END AS entity_table,\n"
        f"       o.Package_ID AS package_id\n"
        f"FROM t_object o\n"
        f"WHERE CASE\n{case}\n"
        f"      END IS NOT NULL;"
    )


def _pkg_view() -> str:
    """The package tree, with path and depth, by recursive CTE."""
    return (
        f"CREATE VIEW {_q(physical('pkg'))} AS\n"
        f"WITH tree AS (\n"
        f"    SELECT p.Package_ID, p.Parent_ID, p.Name,\n"
        f"           CAST(p.Name AS nvarchar(max)) AS path, 1 AS depth\n"
        f"    FROM t_package p\n"
        f"    WHERE p.Parent_ID IS NULL OR p.Parent_ID = 0\n"
        f"    UNION ALL\n"
        f"    SELECT c.Package_ID, c.Parent_ID, c.Name,\n"
        f"           CAST(t.path + '/' + c.Name AS nvarchar(max)), t.depth + 1\n"
        f"    FROM t_package c\n"
        f"    JOIN tree t ON t.Package_ID = c.Parent_ID\n"
        f")\n"
        f"SELECT Package_ID AS package_id, Parent_ID AS parent_id, Name AS name,\n"
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
        f"SELECT c.Connector_ID AS connector_id,\n"
        f"       so.ea_guid AS source_guid,\n"
        f"       eo.ea_guid AS target_guid,\n"
        f"       c.Connector_Type AS connector_type,\n"
        f"       c.Stereotype AS stereotype,\n"
        f"       COALESCE(cs.profile, '') AS profile,\n"
        f"       c.Name AS name\n"
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
    """The multi-value bridge: ONE ROW PER VALUE, never per tag.

    This is the table the whole capability's headline number depends on. A
    flattened column breaks aggregation silently - exact-match counting a tag
    holding both "GLBA" and "GLBA, FFIEC" understates by about half. Measured on
    the reference model: 31 applications in regulatory scope through the bridge,
    14 counted naively.

    Only tags the caller declared multi-valued are split. The module that owns
    that decision refuses to guess and so does this one: a team name like
    "Risk, Compliance & Audit" is ONE value containing a comma, and the
    technology declares it the same way it declares a genuinely multi-valued tag.
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
        f"SELECT k.ea_guid, p.Property AS tag, p.Value AS value\n"
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

    NO empty-value filter, deliberately, and this is the one place the frame's
    two bridges disagree: `pivot` writes an overflow row for every tag it finds
    on a placed element whether or not the value is populated, while `tag_value`
    writes only populated ones. Measured: 69 overflow rows in the database
    against 2 once empties are filtered out.

    The view matches the pivot, because the requirement is that the paths agree.
    Whether the pivot SHOULD write empty overflow rows is a separate question
    about `pivot.py`, and silently differing here would hide it rather than
    settle it.
    """
    overflow = sorted({tag for t in model.tables for tag in t.overflow_tags})
    hub = _q(physical("element"))
    if not overflow:
        return (f"CREATE VIEW {_q(physical('overflow_tag'))} AS\n"
                f"SELECT CAST(NULL AS nvarchar(40)) AS ea_guid,\n"
                f"       CAST(NULL AS nvarchar(255)) AS tag,\n"
                f"       CAST(NULL AS nvarchar(max)) AS value\n"
                f"WHERE 1 = 0;")
    # SCOPED PER TABLE. A tag is overflow for ONE stereotype - it fell below the
    # column threshold there - and may be a perfectly ordinary column on
    # another. Matching the tag name globally emitted 553 rows where the
    # database held 69, because every placed element contributed its value for
    # any tag that was sparse anywhere.
    # Scoped by PLACEMENT, not by `_keymap.entity_table`. `entity_table` names
    # only the FIRST table a multi-stereotype element landed in, so scoping on
    # it drops that element's overflow rows for every other table it belongs to
    # - measured, 2 rows emitted against the 69 the pivot writes. The pivot
    # walks each table and writes overflow for the elements placed IN it, so
    # the view has to use the same predicate the entity views use.
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
    """There is no build on this path, so this describes the CONNECTION.

    It exists because the semantic model is shared across all three paths and
    expects the same table set. Saying "live" rather than inventing a run id is
    the honest reading: `reconciled` is NULL because nothing reconciled this -
    the quality apparatus runs against EA, not in these views.
    """
    return (
        f"CREATE VIEW {_q(physical('load_run'))} AS\n"
        f"SELECT CAST('live' AS nvarchar(40)) AS run_id,\n"
        f"       CONVERT(nvarchar(30), SYSUTCDATETIME(), 126) AS run_at,\n"
        f"       CAST({_lit(model.technology_name or model.technology_id)}"
        f" AS nvarchar(255)) AS repository,\n"
        f"       CAST({_lit(ea_build or '')} AS nvarchar(100)) AS spec_hash,\n"
        f"       CAST(NULL AS int) AS rows_loaded,\n"
        f"       CAST(NULL AS int) AS reconciled,\n"
        f"       CAST(NULL AS int) AS mismatches;"
    )


def _tag_coverage_view(model: ReportModel) -> str:
    """Coverage, computed live rather than loaded.

    Non-negotiable in the database and non-negotiable here: a roll-up over a
    partly-populated tag produces a confident wrong number, and a BI report is
    exactly where that gets believed.
    """
    hub = _q(physical("element"))
    parts = []
    for t in model.tables:
        for c in t.columns:
            parts.append(
                f"SELECT {_lit(t.name)} AS table_name, {_lit(c.source_tag)} AS tag,\n"
                f"       SUM(CASE WHEN p.Property IS NOT NULL THEN 1 ELSE 0 END) AS present,\n"
                f"       SUM(CASE WHEN LTRIM(RTRIM(COALESCE(p.Value, ''))) <> ''"
                f" THEN 1 ELSE 0 END) AS populated,\n"
                f"       COUNT(*) AS total,\n"
                f"       CASE WHEN COUNT(*) = 0 THEN 0.0 ELSE\n"
                f"            CAST(SUM(CASE WHEN LTRIM(RTRIM(COALESCE(p.Value, ''))) <> ''"
                f" THEN 1 ELSE 0 END) AS float) / COUNT(*) END AS coverage\n"
                f"FROM {hub} k\n"
                f"JOIN t_object o ON o.ea_guid = k.ea_guid\n"
                f"LEFT JOIN t_objectproperties p\n"
                f"       ON p.Object_ID = o.Object_ID AND p.Property = {_lit(c.source_tag)}\n"
                f"WHERE k.entity_table = {_lit(t.name)}")
    if not parts:
        return (f"CREATE VIEW {_q(physical('tag_coverage'))} AS\n"
                f"SELECT CAST(NULL AS nvarchar(255)) AS table_name,\n"
                f"       CAST(NULL AS nvarchar(255)) AS tag,\n"
                f"       CAST(NULL AS int) AS present, CAST(NULL AS int) AS populated,\n"
                f"       CAST(NULL AS int) AS total, CAST(NULL AS float) AS coverage\n"
                f"WHERE 1 = 0;")
    return (f"CREATE VIEW {_q(physical('tag_coverage'))} AS\n"
            + "\nUNION ALL\n".join(parts) + ";")


# -------------------------------------------------------------- vocabulary


def _entity_view(table) -> str:
    """One view per stereotype, in the customer's own business vocabulary.

    The tagged-value pivot: one correlated subquery per column, generated once
    at setup from the census. Column ORDER matches `ddl.entity_table_ddl` and
    `load.entity_columns`, so a column maps to the same place on every path.
    """
    cols = [
        "       o.ea_guid,",
        "       o.Name AS name,",
        "       o.Object_Type AS metaclass,",
    ]
    for c in table.columns:
        cols.append(
            f"       (SELECT TOP 1 p.Value FROM t_objectproperties p\n"
            f"         WHERE p.Object_ID = o.Object_ID\n"
            f"           AND p.Property = {_lit(c.source_tag)}) AS {_q(c.name)},")
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
    everything else is scoped to it - the same ordering reason the loader has
    for writing the frame before the entity tables.
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
        # NOT scoped to the key map: a diagram exists whether or not anything on
        # it is placed. Measured on the reference model, 10 of 25 diagrams hold
        # no logical object at all - use case, sequence, activity, state - so a
        # catalog built from this legitimately shows fewer than half of them.
        physical("diagram"): (
            f"CREATE VIEW {_q(physical('diagram'))} AS\n"
            f"SELECT d.Diagram_ID AS diagram_id, d.Name AS name,\n"
            f"       d.Diagram_Type AS diagram_type, d.Package_ID AS package_id\n"
            f"FROM t_diagram d;"),
        physical("diagram_object"): _simple_join_view(
            physical("diagram_object"),
            "do.Diagram_ID AS diagram_id, o.ea_guid AS ea_guid",
            "t_diagramobjects do\nJOIN t_object o ON o.Object_ID = do.Object_ID",
            "o.ea_guid"),
        physical("attribute"): _simple_join_view(
            physical("attribute"),
            "a.ID AS attribute_id, o.ea_guid AS element_guid, a.Name AS name,\n"
            "       a.Type AS attr_type, a.Scope AS scope",
            "t_attribute a\nJOIN t_object o ON o.Object_ID = a.Object_ID",
            "o.ea_guid"),
        physical("operation"): _simple_join_view(
            physical("operation"),
            "op.OperationID AS operation_id, o.ea_guid AS element_guid,\n"
            "       op.Name AS name, op.Type AS return_type, op.Scope AS scope",
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
