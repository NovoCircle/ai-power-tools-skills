#!/usr/bin/env python3
"""Turn tagged-value rows into entity rows, host-side.

PURE. No repository calls, no COM, no file or network I/O, no clock, no
randomness. In, plain row dicts; out, plain row dicts.

WHY THE PIVOT IS NOT SQL
------------------------
The column list is discovered from data, so a SQL pivot would have to be
GENERATED per stereotype per run: different SQL text every time somebody adds a
tagged value, unvalidatable ahead of time, and different again per backend.
Fixed Python over variable data is the arrangement that can be tested and
debugged. Fixed SQL over variable data is the arrangement that cannot.

THE LOAD NEVER DISCARDS DATA
----------------------------
Three outputs, and between them every tagged value lands somewhere:

  * the entity row - one column per tag that cleared the sparse threshold
  * `tag_value`   - the bridge, one row PER VALUE, which is what measures and
                    filters must use
  * `overflow_tag`- sparse tags, kept as key/value rather than dropped

Anything that cannot be placed is returned in `unplaced` rather than silently
vanishing, because a load that quietly loses rows is the failure this capability
exists to prevent.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ea_census import split_multi_value
from report_model import ReportModel, Table


@dataclass
class PivotResult:
    #: table name -> list of row dicts
    rows: dict[str, list[dict]] = field(default_factory=dict)
    tag_value: list[dict] = field(default_factory=list)
    overflow: list[dict] = field(default_factory=list)
    coverage: list[dict] = field(default_factory=list)
    #: Tag rows that reached NOWHERE - not a column, not overflow, not the
    #: bridge. Should be empty, and is reported rather than dropped so "should
    #: be" is checkable.
    #:
    #: This is deliberately narrower than "its element has no entity table". An
    #: untyped element still gets its values into `tag_value`, because the
    #: bridge is keyed by element rather than by table - that is the honest
    #: remainder working as designed, not a loss. Counting those as unplaced
    #: reported 88 false losses on a real model.
    unplaced: list[dict] = field(default_factory=list)

    @property
    def total_rows(self) -> int:
        return sum(len(v) for v in self.rows.values())


def pivot(model: ReportModel,
          elements: list[dict],
          property_rows: list[dict],
          placement: dict[str, list[str]],
          *,
          excluded_guids: set[str] | None = None,
          guid_of_property=lambda r: r.get("ea_guid", ""),
          separator: str = ",") -> PivotResult:
    """Pivot tags into entity rows.

    `elements` need `ea_guid`, `Name` and `Object_Type`. `property_rows` need
    `Property` and `Value`, with `guid_of_property` yielding the owning element's
    guid. `placement` is the census's guid -> entity keys mapping.

    A multi-stereotype element appears in SEVERAL entity tables, because it IS
    several things. Its tags are written to each, and its `tag_value` rows are
    written ONCE - the bridge is keyed by element, not by table, so duplicating
    them there would double every count taken through it.
    """
    result = PivotResult()
    # EA's own machinery - report packages, model documents - carries tags like
    # ReportName and SearchValue. They are not business content, the census
    # already excluded their elements, and counting them here reported 29 rows
    # of EA scaffolding as lost customer data.
    excluded_guids = excluded_guids or set()
    by_key: dict[str, Table] = {t.entity_key: t for t in model.tables}
    for t in model.tables:
        result.rows[t.name] = []

    el_by_guid = {e.get("ea_guid", ""): e for e in elements}

    # tags per element, in input order
    tags_by_guid: dict[str, list[tuple[str, str]]] = {}
    for r in property_rows:
        guid = guid_of_property(r)
        if not guid or guid in excluded_guids:
            continue
        tag = (r.get("Property") or "").strip()
        if not tag:
            continue
        tags_by_guid.setdefault(guid, []).append((tag, (r.get("Value") or "").strip()))

    multi = {c.source_tag for t in model.tables for c in t.columns if c.multi_valued}

    # ---- entity rows, one per (element, entity it belongs to)
    for guid, keys in sorted(placement.items()):
        el = el_by_guid.get(guid, {})
        tags = tags_by_guid.get(guid, [])
        for key in keys:
            table = by_key.get(key)
            if table is None:
                continue
            row = {
                "ea_guid": guid,
                "name": el.get("Name", ""),
                "metaclass": el.get("Object_Type", ""),
            }
            col_by_tag = {c.source_tag: c for c in table.columns}
            overflow_tags = set(table.overflow_tags)
            for tag, value in tags:
                col = col_by_tag.get(tag)
                if col is not None:
                    # The flattened column stays for display. Measures use the
                    # bridge; that is the point of having both.
                    row[col.name] = value
                elif tag in overflow_tags:
                    result.overflow.append({"ea_guid": guid, "tag": tag, "value": value})
            for c in table.columns:
                row.setdefault(c.name, None)
            result.rows[table.name].append(row)

    # ---- tag_value bridge, once per element regardless of how many tables it is in
    for guid in sorted(tags_by_guid):
        for tag, value in tags_by_guid[guid]:
            if not value:
                continue            # an empty tag is coverage, not a value
            values = split_multi_value(value, separator=separator) if tag in multi else [value]
            for v in values:
                result.tag_value.append({"ea_guid": guid, "tag": tag, "value": v})

    # ---- coverage, straight from the model so one number has one source
    for t in model.tables:
        for c in t.columns:
            result.coverage.append({
                "table_name": t.name, "tag": c.source_tag,
                "present": c.present, "populated": c.populated,
                "total": t.row_count, "coverage": c.coverage,
            })

    # ---- anything that reached nowhere at all
    #
    # A value lands in the bridge whatever its element's typing, so the only
    # genuinely lost rows are EMPTY values on an element with no entity table:
    # no column to sit in, no overflow routing, and nothing for the bridge to
    # carry. Those are coverage facts about an untyped element, which the
    # `element` frame table records separately.
    in_a_table = set(placement)
    for guid in sorted(tags_by_guid):
        if guid in in_a_table:
            continue
        for tag, value in tags_by_guid[guid]:
            if not value:
                result.unplaced.append({"ea_guid": guid, "tag": tag, "value": value})

    return result
