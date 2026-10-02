#!/usr/bin/env python3
"""The report model: the contract between a repository's census and a database.

PURE. No repository calls, no COM, no file or network I/O, no clock, no
randomness. It turns a census plus a technology into a description of tables and
columns, and nothing else builds or loads anything.

This is the artifact a customer tunes. It is deliberately plain data so it can be
serialized to YAML, reviewed, edited and re-applied, in the same lineage as the
validation rulesets.

WHAT DECIDES A COLUMN'S TYPE AND DOMAIN
---------------------------------------
The technology, when it declares one; observation only as a fallback. The
difference matters: observation can only ever show the values that happen to have
been used, so an inferred enum domain is a candidate, and the gap between the
declared domain and the observed one is a FINDING rather than something to
paper over.

WHAT THIS MODULE REFUSES TO DECIDE
----------------------------------
Whether a tag is multi-valued. EA stores a multi-valued tag as one joined string,
so `regulatoryScope` holding "GLBA, FFIEC" has to be split for aggregation to be
correct - but a team name like "Risk, Compliance & Audit" is ONE value containing
a comma, and the technology declares both as `String`. The declared type cannot
tell them apart.

So this module reports `multi_value_candidates` and splits only what the caller
names in `multi_valued`. Guessing here corrupts data silently, which is the one
failure mode this whole capability exists to avoid.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict

from ea_census import (
    Entity,
    ElementCensus,
    TagStat,
    declared_shapes,
    infer_enum_domain,
    snake_case,
    split_multi_value,
    table_name,
)

#: Fixed tables, independent of the technology. `element` is load-bearing, not a
#: convenience: without it only 16 of 104 relationships in a prototype had both
#: endpoints resolvable, because edges touching an untyped element dangled.
#: Kept in step with `ddl.FRAME_DDL`, which carries the column definitions.
#: `test_ddl.py` asserts the two agree - they drifted once, with `overflow_tag`
#: defined in the DDL but missing here, so the model advertised ten frame tables
#: while eleven were created and the one holding sparse tags was invisible to
#: anything reading `model.frame`.
FRAME_TABLES = (
    "pkg",
    "element",
    "rel_all",
    "tag_value",
    "tag_coverage",
    "overflow_tag",
    "diagram",
    "diagram_object",
    "attribute",
    "operation",
    "load_run",
)

#: Declared tagged-value type -> SQL type. SQLite is dynamically typed, so these
#: are documentation as much as constraint - but the same mapping is what a
#: portable target will need, so it is stated once here.
SQL_TYPES = {
    "string": "TEXT",
    "enumeration": "TEXT",
    "boolean": "INTEGER",
    "int": "INTEGER",
    "integer": "INTEGER",
    "decimal": "REAL",
    "double": "REAL",
    "date": "TEXT",
    "datetime": "TEXT",
}

DEFAULT_SQL_TYPE = "TEXT"

#: The string forms EA actually stores for a tag the technology declares
#: `boolean`. EA has no boolean tagged-value type - it stores whatever the
#: editor or the profile's default put there - so the mapping has to be explicit
#: rather than inferred.
BOOLEAN_TRUE = frozenset({"true", "t", "yes", "y", "1"})
BOOLEAN_FALSE = frozenset({"false", "f", "no", "n", "0"})


def coerce_value(value, sql_type: str):
    """A tag's string value as its declared type, or `UNCOERCIBLE`.

    SQLite is dynamically typed, so a column declared INTEGER will store the
    string 'true' without complaint. The DDL then claims one type while the data
    is another: `WHERE audit_logging_enabled = 1` matches nothing, and a
    strictly-typed consumer refuses the column outright - which is how this was
    found, with pyarrow raising on a Parquet write (APT-2026-0225).

    An empty value on a TYPED column is NULL, never 0 or False. Empty means
    nobody filled it in, which is a coverage fact; turning it into a value would
    invent data and make `tag_coverage` disagree with the column it describes.
    On a TEXT column an empty value stays the empty string, which is what every
    build before this one wrote - changing it to NULL is a separate semantic
    decision, not part of fixing a type disagreement, and it would silently
    break any customer query testing `= ''`.

    A value that cannot be coerced is returned as `UNCOERCIBLE` rather than
    quietly written as text or dropped. An unparseable boolean is a data-quality
    finding of exactly the kind this product exists to surface.
    """
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None if sql_type in ("INTEGER", "REAL") else value
    if sql_type == "INTEGER":
        low = text.lower()
        if low in BOOLEAN_TRUE:
            return 1
        if low in BOOLEAN_FALSE:
            return 0
        try:
            return int(text)
        except ValueError:
            return UNCOERCIBLE
    if sql_type == "REAL":
        try:
            return float(text)
        except ValueError:
            return UNCOERCIBLE
    return text


class _Uncoercible:
    """Distinct from None, which means "nobody filled it in"."""

    def __repr__(self):            # pragma: no cover - debugging aid
        return "UNCOERCIBLE"

    def __bool__(self):
        return False


UNCOERCIBLE = _Uncoercible()

#: Below this share of POPULATED coverage a tag becomes an overflow row rather
#: than a column. Arbitrary, and labeled as such: it is a default that behaved
#: sensibly on one model, not a measured threshold. Callers should override it
#: deliberately rather than inherit it by accident.
DEFAULT_SPARSE_THRESHOLD = 0.05


@dataclass
class Column:
    name: str
    source_tag: str
    sql_type: str = DEFAULT_SQL_TYPE
    description: str = ""
    declared: bool = False
    enum_values: list[str] = field(default_factory=list)
    enum_source: str = ""        # "declared" | "observed" | ""
    multi_valued: bool = False
    populated: int = 0
    present: int = 0
    coverage: float = 0.0


@dataclass
class Table:
    name: str
    entity_key: str
    stereotype: str
    alias: str = ""
    description: str = ""
    profile: str = ""
    metaclasses: dict[str, int] = field(default_factory=dict)
    heterogeneous: bool = False
    declared: bool = False
    row_count: int = 0
    columns: list[Column] = field(default_factory=list)
    overflow_tags: list[str] = field(default_factory=list)


@dataclass
class ReportModel:
    technology_id: str = ""
    technology_name: str = ""
    namespace: str = ""
    sparse_tag_threshold: float = DEFAULT_SPARSE_THRESHOLD
    tables: list[Table] = field(default_factory=list)
    frame: list[str] = field(default_factory=lambda: list(FRAME_TABLES))
    multi_value_candidates: list[str] = field(default_factory=list)
    untyped_elements: int = 0
    excluded_elements: int = 0
    excluded: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Plain data, for serializing to YAML or JSON."""
        return asdict(self)

    def table_for(self, entity_key: str) -> Table | None:
        return next((t for t in self.tables if t.entity_key == entity_key), None)


def _sql_type(declared_type: str) -> str:
    return SQL_TYPES.get((declared_type or "").strip().lower(), DEFAULT_SQL_TYPE)


def detect_multi_value_candidates(stats: list[TagStat], *, separator: str = ",",
                                  min_share: float = 0.25) -> list[str]:
    """Tags whose values often contain the separator.

    A CANDIDATE list, never an instruction. A tag lands here when at least
    `min_share` of its distinct values contain the separator - which is true of a
    genuinely multi-valued tag and also of a free-text field whose values happen
    to contain commas. Distinguishing them needs a human or a convention; this
    just stops the question being invisible.
    """
    out = []
    for st in stats:
        if not st.values:
            continue
        hits = sum(1 for v in st.values if separator in v)
        if hits / len(st.values) >= min_share:
            out.append(st.tag)
    return sorted(out)


def build_column(st: TagStat, total: int, declared_tag: dict | None,
                 *, multi_valued: bool = False) -> Column:
    """One column from one tag's statistics, enriched by the technology."""
    declared_tag = declared_tag or {}
    domain = [v for v in (declared_tag.get("values") or []) if v]
    enum_source = ""
    if domain:
        enum_source = "declared"
    else:
        inferred = infer_enum_domain(st)
        if inferred:
            domain, enum_source = inferred, "observed"

    return Column(
        name=snake_case(st.tag),
        source_tag=st.tag,
        sql_type=_sql_type(declared_tag.get("type", "")),
        description=(declared_tag.get("description") or "").strip(),
        declared=bool(declared_tag),
        enum_values=list(domain),
        enum_source=enum_source,
        multi_valued=multi_valued,
        populated=st.populated,
        present=st.present,
        coverage=round(st.coverage(total), 4),
    )


def build_report_model(census: ElementCensus,
                       tag_stats: dict[str, list[TagStat]],
                       mdg: dict | None = None,
                       *,
                       namespace: str = "",
                       sparse_threshold: float = DEFAULT_SPARSE_THRESHOLD,
                       multi_valued: set[str] | None = None,
                       strip_prefix: str = "") -> ReportModel:
    """Turn a census into a table-and-column description.

    `tag_stats` maps an entity key to its `TagStat` list. `mdg` is the shape
    `get_mdg_from_runtime` returns, and supplies aliases, descriptions, declared
    types and complete enum domains - matched on STEREOTYPE NAME, never on
    technology id, because the id and the FQName namespace do not match.

    Every entity gets a table, including one with a single row. An earlier
    prototype skipped stereotypes with fewer than three instances and thereby
    dropped sixteen of them - exactly the governance drift a census exists to
    surface.
    """
    mdg = mdg or {}
    multi_valued = multi_valued or set()
    declared = {s["name"]: s for s in mdg.get("stereotypes", []) if s.get("name")}

    model = ReportModel(
        technology_id=mdg.get("tech_id", "") or mdg.get("technology_id", ""),
        technology_name=mdg.get("technology_name", ""),
        namespace=namespace,
        sparse_tag_threshold=sparse_threshold,
        untyped_elements=len(census.untyped_guids),
        excluded_elements=len(census.excluded_guids),
        excluded={
            **{f"ea_internal:{k}": v for k, v in sorted(census.excluded_ea_internal.items())},
            **{f"profile_authoring:{k}": v
               for k, v in sorted(census.excluded_profile_authoring.items())},
        },
    )

    taken: set[str] = set()
    candidates: set[str] = set()

    for ent in census.entities:                      # already deterministically ordered
        spec = declared.get(ent.stereotype, {})
        alias = (spec.get("alias") or "").strip()
        tbl = Table(
            name=table_name(ent, taken,
                            alias_of=(lambda e, a=alias: a) if alias else None,
                            strip_prefix=strip_prefix),
            entity_key=ent.key,
            stereotype=ent.stereotype,
            alias=alias,
            description=(spec.get("notes") or "").strip(),
            profile=ent.profile,
            metaclasses=dict(sorted(ent.metaclasses.items())),
            heterogeneous=ent.is_heterogeneous,
            declared=bool(spec),
            row_count=ent.count,
        )

        stats = tag_stats.get(ent.key, [])
        candidates.update(detect_multi_value_candidates(stats))
        tag_specs = {t["name"]: t for t in spec.get("tagged_values", []) if t.get("name")}

        for st in stats:
            if st.coverage(ent.count) < sparse_threshold:
                # Not dropped - routed to the overflow table, and named here so
                # the routing is visible rather than a silent absence.
                tbl.overflow_tags.append(st.tag)
                continue
            tbl.columns.append(build_column(
                st, ent.count, tag_specs.get(st.tag),
                multi_valued=st.tag in multi_valued))

        tbl.columns.sort(key=lambda c: c.name)
        tbl.overflow_tags.sort()
        model.tables.append(tbl)

    model.multi_value_candidates = sorted(candidates)
    return model
