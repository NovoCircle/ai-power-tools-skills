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

HOW AN ELEMENT IS PLACED
------------------------
EA records a stereotype application in `t_xref.Description` as one or more
`@STEREO;...@ENDSTEREO;` blocks. `_stereo_block` parses those into one row per
BLOCK, carrying the stereotype's name and its FQName, and every placement
predicate reads that view by EQUALITY.

**It is a parser rather than a `LIKE` over the whole Description, and that is
the point.** `carries an FQName` is a property of a BLOCK, not of the row: a
multi-stereotype element packs several blocks into one Description, so a
substring test cannot tell "this element has an ad-hoc Device application" from
"this element has some other stereotype that happens to be profile-bound". An
earlier draft of this module did use a `LIKE` with a trailing semicolon to
avoid prefix collisions; parsing removes the need for that trick entirely.

A multi-stereotype element matches several predicates at once. Measured on the
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
from report_model import BOOLEAN_FALSE, BOOLEAN_TRUE, ReportModel

#: Declared SQL type -> SQL Server type. The fourth leg of the same journey as
#: `report_model.SQL_TYPES`, `parquet_out.PARQUET_TYPES` and
#: `semantic_model.TMDL_TYPES`, named here so all four are greppable together -
#: and declared rather than inlined because the width is part of the value.
#:
#: INTEGER is **bigint, not int**. SQLite's INTEGER is 64-bit and
#: `PARQUET_TYPES` maps INTEGER to `int64`, so a 32-bit `int` here is a
#: NARROWER type than every other path: MEASURED, a tagged value of 3000000000
#: is 3000000000 in the database and in Parquet and `TRY_CAST(... AS int)`
#: silently makes it NULL in the view. 2147483647 agrees and 2147483648 does
#: not, which is exactly the kind of boundary a fixture never contains.
#: Power BI maps `bigint` and `int` both to Int64, so this costs the `.pbip`
#: identity nothing.
#:
#: TEXT is listed for completeness and is never cast: `_coerced_value` returns
#: the trimmed value before it reaches `TRY_CAST`, because text needs no
#: conversion and `nvarchar(max)` is what the column already is.
SQLSERVER_TYPES = {
    "TEXT": "nvarchar(max)",
    "INTEGER": "bigint",
    "REAL": "float",
}

DEFAULT_SQLSERVER_TYPE = "nvarchar(max)"

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
    """An N-prefixed literal, because every column it is compared against is
    `nvarchar`.

    Without the `N` the literal is parsed under the database's default
    collation codepage, so a stereotype or tagged-value name carrying a
    character outside it becomes `?` and the predicate matches nothing - the
    silent-empty-table failure again, this time triggered by an international
    customer's model rather than by our code.
    """
    return "N'" + text.replace("'", "''") + "'"


def _comment(text: str) -> str:
    """Comment text with every line break removed.

    A `--` comment runs to end of LINE, so a CR or LF inside an interpolated
    value closes the comment and leaves the remainder of that value as
    EXECUTABLE DDL in a script the customer runs with schema rights. Comment
    text is the one place in this module that does not reach the parser, and
    that is exactly what makes it the one place it would be reached from.

    These values come out of a model - `technology_name`, `namespace`, an EA
    build string - not out of our own constants, so they are input and are
    treated as input, the same as every literal routed through `_lit`.
    """
    return text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")


def placement_predicate(table) -> str:
    """The test that places an element in one vocabulary table.

    THREE SHAPES. `ea_census.entity_key` keys a
    profile-bound application by its FQName and an ad-hoc one by
    `name|metaclass` - a bare name is ambiguous across languages, so the
    metaclass has to carry identity.

    Reading only the FQName form silently emptied 14 of 29 tables on the
    reference model and left the key map 14 elements short, which then cascaded
    into the relationship and diagram views. Measured, not hypothetical.
    """
    key = table.entity_key
    # The SHAPE is decided by `profile`, not by looking for a `|` in the key.
    # Sniffing the key misclassifies in both directions: a bare
    # `t_object.Stereotype` holding a qualified name gives a key with BOTH `|`
    # and `::` and would be read as profile-bound, matching nothing and leaving
    # the table silently empty; and a stereotype name containing `|` would
    # mis-split the metaclass. `profile` and `stereotype` are already on the
    # table and say exactly what is needed.
    if not table.profile:
        name = table.stereotype
        metaclass = key.rpartition("|")[2]
        # THREE shapes, not two. Besides an ad-hoc block in `t_xref`, an element
        # with NO xref entry at all falls back to the bare `t_object.Stereotype`
        # column - `census_elements` says so and two elements on the reference
        # model are exactly that: an Actor stereotyped BusinessActor and a
        # Component stereotyped SystemSoftware, each with zero xref rows.
        # Missing them left the key map 2 short and emptied both their tables.
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
        # EA's physical schema is not a public contract: Sparx can change the
        # t_xref encoding between builds, and in this path that break lands in
        # views the CUSTOMER owns, silently, on upgrade. Stamping the build is
        # the cheapest thing that makes the breakage diagnosable.
        lines.append(f"-- ea build   : {_comment(ea_build)}  <- these views were "
                     f"written against this schema")
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
        f"{field(';Name=', 'stereo_name')},\n"
        f"{field('FQName=', 'fqname')}\n"
        f"FROM t_xref x\n"
        f"CROSS APPLY STRING_SPLIT(\n"
        # Any CHAR(1) already in the data is stripped BEFORE it is used as the
        # separator. Nothing EA writes into a stereotype block should contain
        # one, but the failure if it did is silent and expensive: the fragment
        # after it fails the LIKE and is dropped, the fragment before it loses
        # its FQName, and a profile-bound application quietly demotes to ad-hoc
        # - which empties a table. One REPLACE removes the assumption.
        f"    REPLACE(REPLACE(CAST(x.Description AS nvarchar(max)),\n"
        f"                    CHAR(1), ''),\n"
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
    if not whens:
        # SQL Server rejects a CASE whose only result is the NULL constant
        # (Msg 8133). The sibling empty-case views use typed CAST(NULL) columns;
        # this one does the same rather than emitting SQL that will not compile.
        return (f"CREATE VIEW {_q(physical('element'))} AS\n"
                f"SELECT CAST(NULL AS nvarchar(40)) AS ea_guid,\n"
                f"       CAST(NULL AS nvarchar(255)) AS entity_table,\n"
                f"       CAST(NULL AS int) AS package_id\n"
                f"WHERE 1 = 0;")
    case = "\n".join(whens)
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
    """The package tree, with path and depth, by recursive CTE.

    AN ANCHOR ROW IS A ROOT IN EVERY COLUMN, NOT ONLY IN THE `WHERE`
    ---------------------------------------------------------------
    The anchor deliberately keeps a package whose parent is missing, zero, or
    itself. A root that still CARRIES the broken parent is worse than dropping
    it would have been: `parent_id` is a shipped `INTEGER` column and anything
    walking the chain follows it to a row this view does not contain, or round
    and round a self-reference. `frame.package_rows` nulls both cases - a
    self-parent at `parent_of[pid] = None if parent == pid else parent`, a
    dangling one at `parent_of.get(pid) if ... in name_of else None` - so the
    anchor carries `CAST(NULL AS int)` and agrees with it by construction
    rather than by the outer `NULLIF`, which only ever caught zero.

    `Name` IS NULLABLE AND `path` IS COMPUTED FROM IT
    -------------------------------------------------
    `NULL + '/' + 'x'` is NULL in SQL Server, so one NULL package name emptied
    `path` for that package AND for every descendant - the recursion propagates
    it the whole way down. The outer `SELECT` already coalesced the projected
    `name`; `path` was missed because it is built rather than projected, which
    is the kind of column a NULL-versus-empty-string pass walks straight past.
    `frame.package_rows` coalesces at `name_of[pid] = p.get("Name") or ""`, so
    a NULL-named child of `Model` is `'Model/'` there and now here.
    """
    return (
        f"CREATE VIEW {_q(physical('pkg'))} AS\n"
        f"WITH tree AS (\n"
        f"    SELECT p.Package_ID, CAST(NULL AS int) AS Parent_ID, p.Name,\n"
        f"           CAST(COALESCE(p.Name, '') AS nvarchar(max)) AS path, 0 AS depth\n"
        f"    FROM t_package p\n"
        # A package whose parent does not exist, or which is its own parent,
        # is treated as a ROOT rather than dropped - matching
        # `frame.package_rows`, which does this deliberately: losing a package
        # loses every element under it from the grouping, which is a bigger
        # error than a path that starts lower than the model root. Dropping it
        # here would also orphan those elements from `_keymap.package_id`, the
        # only path to the package tree.
        f"    WHERE p.Parent_ID IS NULL OR p.Parent_ID = 0\n"
        f"       OR p.Parent_ID = p.Package_ID\n"
        f"       OR NOT EXISTS (SELECT 1 FROM t_package q\n"
        f"                      WHERE q.Package_ID = p.Parent_ID)\n"
        f"    UNION ALL\n"
        f"    SELECT c.Package_ID, c.Parent_ID, c.Name,\n"
        f"           CAST(t.path + '/' + COALESCE(c.Name, '') AS nvarchar(max)),\n"
        f"           t.depth + 1\n"
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
        f"SELECT c.Connector_ID AS connector_id,\n"
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

    BOTH ARMS TRIM, because `pivot` stores every tagged value as
    `(r.get("Value") or "").strip()` before anything else sees it. The split arm
    trimmed each part and the single arm did not, which is not a difference a
    row count can see: `'Business-Critical '` and `'Business-Critical'` are the
    same member of the same column in the database and two different members in
    Power BI, which is the same failure the blank-versus-empty-string pass was
    about.
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
                f"       COALESCE(SUM(CASE WHEN p.Property IS NOT NULL THEN 1 ELSE 0 END), 0)"
                f" AS present,\n"
                f"       COALESCE(SUM(CASE WHEN LTRIM(RTRIM(COALESCE(p.Value, ''))) <> ''"
                f" THEN 1 ELSE 0 END), 0) AS populated,\n"
                f"       COUNT(DISTINCT o.ea_guid) AS total,\n"
                # Divided by COUNT(DISTINCT), the same denominator `total`
                # uses. COUNT(*) counts JOINED rows, and `t_objectproperties`
                # carries no unique index on (Object_ID, Property) - so a
                # repeated tag made the ratio disagree with its own numerator
                # and denominator: 44/48 printed beside total=47.
                f"       CASE WHEN COUNT(DISTINCT o.ea_guid) = 0 THEN 0.0 ELSE\n"
                # Rounded to 4 places, as `tag_coverage` does. Without it the
                # two paths disagree in the tail - 0.9362 against
                # 0.9361702127659575 - which is a difference no row count can
                # see and which a report would surface as two different numbers.
                f"            ROUND(CAST(SUM(CASE WHEN"
                f" LTRIM(RTRIM(COALESCE(p.Value, ''))) <> ''"
                f" THEN 1 ELSE 0 END) AS float)\n"
                f"                  / COUNT(DISTINCT o.ea_guid), 4) END AS coverage\n"
                f"FROM t_object o\n"
                f"LEFT JOIN t_objectproperties p\n"
                f"       ON p.Object_ID = o.Object_ID AND p.Property = {_lit(c.source_tag)}\n"
                f"WHERE {placement_predicate(t)}")
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


#: Where a multi-line `CASE` in an entity column lines up under the `TOP 1`.
_VALUE_INDENT = " " * 26


def _coerced_value(column) -> str:
    """One tagged value as its DECLARED type - `report_model.coerce_value` in SQL.

    THE TYPE IS PART OF THE VALUE, AND THIS IS THE ONLY TYPED COPY
    --------------------------------------------------------------
    `pivot` runs every entity-column value through `coerce_value` because the
    flattened column is the only typed copy of it - `tag_value` is a bridge over
    tags of every type at once and stays text. Emitting `COALESCE(p.Value, '')`
    for every column regardless of type published a DIFFERENT VALUE under the
    same column name on a column the database and Parquet both type:

        tag value, INTEGER column | database / Parquet | emitted before
        --------------------------|--------------------|---------------
        'true'                    | 1                  | 'true'
        ''                        | NULL               | ''
        'maybe'                   | NULL + a report row| 'maybe', silently

    `WHERE audit_logging_enabled = 1` is the measure that matches nothing, and
    `report_model.coerce_value` states that consequence in advance. A column that
    "maps to the same place on every path" with a different type and a different
    value does not satisfy this module's contract.

    FOUR THINGS, IN `coerce_value`'s OWN ORDER
    ------------------------------------------
    1. TRIM FIRST. `pivot` strips before it coerces, so `' 7 '` is 7 and not
       uncoercible, and `'Business-Critical '` is one member rather than two.

       **KNOWN LIMIT, not parity.** `LTRIM`/`RTRIM` remove the SPACE character
       only, where Python's `str.strip()` removes every Unicode whitespace. So a
       value padded with a TAB or a non-breaking space keeps its padding here and
       loses it in the database, and `'\\t1'` on an INTEGER column publishes NULL
       where the database holds 1. MEASURED on SQL Server 2022.

       Accepted rather than closed: `TRIM(chars FROM ...)` is 2022-only, nested
       `REPLACE` would rewrite interiors as well as edges, and a `PATINDEX`
       expression runs to a paragraph per column and still misses most of the
       Unicode space category. The exposure is a tagged value padded with
       something other than a space, which is rare and visible in `tag_value`.
       Documented here so the next person meets a decision rather than a puzzle.
    2. EMPTY ON A TYPED COLUMN IS NULL, never 0 and never ''. Empty means nobody
       filled it in, which is a coverage fact; a 0 there would invent data and
       make `tag_coverage` disagree with the column it describes. On TEXT an
       empty value stays `''`, which is what every build before this one wrote.
    3. BOOLEAN STRINGS ON EVERY INTEGER COLUMN. EA has no boolean tagged-value
       type - a declared boolean arrives as whatever the editor or the profile
       default put there - and `coerce_value` applies the mapping on the SQL
       type, which is all either path can see. `LOWER()` because the Python
       lowercases and a case-sensitive server collation would otherwise disagree
       with it on `'TRUE'`.
    4. UNCOERCIBLE IS NULL HERE. `pivot` leaves the column unset and records a
       data-quality finding; the finding has nowhere to go in a view, so the
       view publishes the same NULL and nothing else. `TRY_CAST` is how: it
       yields NULL exactly where `int()`/`float()` raise.

    THE WIDTH IS PART OF THE TYPE
    -----------------------------
    The target type comes from `SQLSERVER_TYPES`, declared at the top of this
    module, and INTEGER is **bigint**. A 32-bit `int` is a narrower type than
    SQLite's 64-bit INTEGER and than Parquet's `int64`, so it is a different
    value: MEASURED, 3000000000 survives both other paths and `TRY_CAST(... AS
    int)` silently makes it NULL. That is this docstring's own argument - the
    type is part of the value - applied one step further than the first version
    of this function took it.
    """
    value = "LTRIM(RTRIM(COALESCE(p.Value, '')))"
    if column.sql_type not in ("INTEGER", "REAL"):
        return value
    lines = [f"CASE WHEN {value} = {_lit('')} THEN NULL"]
    if column.sql_type == "INTEGER":
        for literals, result in ((BOOLEAN_TRUE, "1"), (BOOLEAN_FALSE, "0")):
            in_list = ", ".join(_lit(s) for s in sorted(literals))
            lines.append(f"{_VALUE_INDENT}WHEN LOWER({value}) IN ({in_list})"
                         f" THEN {result}")
    cast = SQLSERVER_TYPES.get(column.sql_type, DEFAULT_SQLSERVER_TYPE)
    lines.append(f"{_VALUE_INDENT}ELSE TRY_CAST({value} AS {cast}) END")
    return "\n".join(lines)


def _entity_view(table) -> str:
    """One view per stereotype, in the customer's own business vocabulary.

    The tagged-value pivot: one correlated subquery per column, generated once
    at setup from the census. Column ORDER matches `ddl.entity_table_ddl` and
    `load.entity_columns`, so a column maps to the same place on every path.

    Every column is coerced to its declared type by `_coerced_value`, because
    the flattened column is the only TYPED copy of a tagged value and `pivot`
    types it. A tag that is present but empty is `''` on TEXT and NULL on a
    typed column; a tag that is ABSENT is NULL on either, because the subquery
    returns no row and `pivot` leaves the key unset.

    `ORDER BY p.PropertyID DESC` IS LOAD-BEARING, AND IT ENCODES A DEFECT
    --------------------------------------------------------------------
    `t_objectproperties` carries no unique index on `(Object_ID, Property)`, and
    the reference model really does hold duplicates: each of six tags on one
    element appears twice, once populated and once NULL, the NULL having the
    higher `PropertyID`.

    `pivot` assigns column values in extract order and lets later rows
    overwrite, so the later duplicate wins and the populated value is LOST -
    that element's six columns are empty in the database while its `tag_value`
    rows carry the real values. This view reproduces that deliberately: the
    requirement is that the paths agree, and silently disagreeing here would
    hide the defect rather than settle it.

    THE CLAIM THIS CAN HONESTLY MAKE IS NARROWER THAN "REPRODUCES IT EXACTLY".
    Reproducing extract order by `PropertyID` assumes extract order IS
    `PropertyID` order, and nothing guarantees that: `extract.py` selects
    `Object_ID, Property, Value` from `t_objectproperties` with no `ORDER BY`
    and does not select `PropertyID` at all, so the PYTHON side is the
    nondeterministic one. The live acceptance run observed the two agreeing on
    the reference model, which is evidence that the backend returned insertion
    order, not a guarantee that it will. A deterministic view is still the right
    choice - the alternative is two nondeterministic paths and a difference that
    moves between runs - but what it agrees with is the extract order that has
    been OBSERVED, and a reader should know which of those two it is relying on.

    **The underlying behavior is a defect in `pivot`, not here** - a populated
    value should not lose to an empty duplicate, and `extract.py` should order
    what `pivot` reads in order. Both belong to `pivot.py`, and fixing them
    would change what the shipped reporting database contains, so they are owed
    their own item rather than a paragraph here.

    Without an ORDER BY, `TOP 1` is NONDETERMINISTIC: it happened to return the
    populated row, so the view silently disagreed with the database on one
    element. Row counts cannot see that, and it is what the value-level
    comparison was added to catch.
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
            f"SELECT d.Diagram_ID AS diagram_id, COALESCE(d.Name, '') AS name,\n"
            f"       COALESCE(d.Diagram_Type, '') AS diagram_type,\n"
            f"       d.Package_ID AS package_id\n"
            f"FROM t_diagram d;"),
        physical("diagram_object"): _simple_join_view(
            physical("diagram_object"),
            "do.Diagram_ID AS diagram_id, o.ea_guid AS ea_guid",
            "t_diagramobjects do\nJOIN t_object o ON o.Object_ID = do.Object_ID",
            "o.ea_guid"),
        physical("attribute"): _simple_join_view(
            physical("attribute"),
            "a.ID AS attribute_id, o.ea_guid AS element_guid, COALESCE(a.Name, '') AS name,\n"
            "       COALESCE(a.Type, '') AS attr_type, COALESCE(a.Scope, '') AS scope",
            "t_attribute a\nJOIN t_object o ON o.Object_ID = a.Object_ID",
            "o.ea_guid"),
        physical("operation"): _simple_join_view(
            physical("operation"),
            "op.OperationID AS operation_id, o.ea_guid AS element_guid,\n"
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
