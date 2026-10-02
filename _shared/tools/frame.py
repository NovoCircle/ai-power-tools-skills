#!/usr/bin/env python3
"""EA rows into frame rows.

PURE. No repository calls, no COM, no file or network I/O, no clock, no
randomness. In, the row dicts `extract.py` wrote; out, row dicts shaped to
`ddl.FRAME_DDL`.

    python -m pytest _shared/tools/test_frame.py -q

WHY THIS IS A MODULE AND NOT A FEW LINES IN THE CALLER
-----------------------------------------------------
Because it was a few lines in the caller, and the caller populated two of the
eleven frame tables. An acceptance run then reported a reconciled build over a
database whose `element` table - the one every relationship endpoint resolves
against - was empty. The shaping is small but it is not obvious, and two
independent copies of it is how the two drift.

EVERY FOREIGN REFERENCE MUST RESOLVE AGAINST `element`
-----------------------------------------------------
A relationship, diagram placement, attribute or operation whose element is out of
scope or excluded is DROPPED here rather than written with an unresolvable key.
A dangling row is worse than an absent one: it inflates a count and produces an
inner join that silently returns fewer rows than the user is reading totals from.
`dangling()` checks the result so that claim is verified rather than asserted.
"""
from __future__ import annotations

from report_model import ReportModel


def _int(v):
    """None rather than a sentinel: a missing id is absent, not -1."""
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def package_rows(packages: list[dict], *,
                 in_scope: set[int] | None = None) -> list[dict]:
    """Rows for `pkg`, with each package's path and depth computed host-side.

    `path` is a `/`-joined name chain, so a reporting tool can group by it without
    walking a parent chain in a query language that may have no recursion.

    A package whose parent is missing (out of scope, or a dangling Parent_ID) is
    treated as a root rather than dropped - losing a package would lose every
    element under it from the grouping, which is a bigger error than a path that
    starts lower than the model root.
    """
    name_of: dict[int, str] = {}
    parent_of: dict[int, int | None] = {}
    for p in packages:
        pid = _int(p.get("Package_ID"))
        if pid is None:
            continue
        if in_scope is not None and pid not in in_scope:
            continue
        name_of[pid] = p.get("Name") or ""
        parent = _int(p.get("Parent_ID")) or None
        # A package that is its own parent would make the walk below spin; the
        # `seen` set would stop it, but recording it as a root is the honest shape.
        parent_of[pid] = None if parent == pid else parent

    def chain(pid: int) -> list[str]:
        names, seen, cur = [], set(), pid
        while cur is not None and cur in name_of and cur not in seen:
            seen.add(cur)
            names.append(name_of[cur])
            nxt = parent_of.get(cur)
            cur = nxt if nxt in name_of else None
        return list(reversed(names))

    out = []
    for pid in sorted(name_of):
        names = chain(pid)
        out.append({
            "package_id": pid,
            "parent_id": parent_of.get(pid) if parent_of.get(pid) in name_of else None,
            "name": name_of[pid],
            "path": "/".join(names),
            "depth": len(names) - 1,
        })
    return out


def element_rows(elements: list[dict],
                 model: ReportModel,
                 placement: dict[str, list[str]],
                 *,
                 excluded_guids: set[str] | None = None) -> list[dict]:
    """Rows for `element`: every in-scope element whatever its typing.

    This is the load-bearing table. In a prototype that lacked it only 16 of 104
    relationships had both endpoints resolvable, because every edge touching an
    untyped element dangled.

    `entity_table` names where the element landed, or None when nowhere. For a
    MULTI-STEREOTYPE element it names the FIRST table in model order, because one
    column cannot hold a one-to-many and joining names with a separator would
    reintroduce exactly the comma hazard `tag_value` exists to avoid. The complete
    mapping stays recoverable by joining this table to each entity table on
    `ea_guid`, which is how a reporting tool would traverse it in any case.
    """
    excluded_guids = excluded_guids or set()
    order = {t.name: i for i, t in enumerate(model.tables)}
    by_key = {t.entity_key: t for t in model.tables}

    out = []
    for el in elements:
        guid = el.get("ea_guid", "")
        if not guid or guid in excluded_guids:
            continue
        tables = [by_key[k] for k in placement.get(guid, []) if k in by_key]
        tables.sort(key=lambda t: order[t.name])
        first = tables[0] if tables else None
        out.append({
            "ea_guid": guid,
            "object_id": _int(el.get("Object_ID")),
            "name": el.get("Name", ""),
            "metaclass": el.get("Object_Type", ""),
            # A placed element takes the stereotype the census resolved from
            # t_xref. An unplaced one takes t_object.Stereotype as observed - that
            # column holds only the first of several and may name a stereotype no
            # loaded technology declares, which is a finding rather than a reason
            # to blank it.
            "stereotype": first.stereotype if first else (el.get("Stereotype") or ""),
            "profile": first.profile if first else "",
            "entity_table": first.name if first else None,
            "package_id": _int(el.get("Package_ID")),
        })
    return out


def relationship_rows(connectors: list[dict],
                      guid_by_id: dict[int, str],
                      *,
                      guids_in_scope: set[str] | None = None,
                      profile_of=None) -> list[dict]:
    """Rows for `rel_all`. BOTH endpoints must resolve, or the row is dropped.

    `profile_of` takes a connector guid and returns its profile namespace, for a
    stereotype that came from a technology rather than being typed free-hand. Pass
    None and `profile` is empty - honest for an extract that did not pull connector
    provenance, rather than a guess that reads like a fact.
    """
    out = []
    for c in connectors:
        src = guid_by_id.get(_int(c.get("Start_Object_ID")) or -1, "")
        tgt = guid_by_id.get(_int(c.get("End_Object_ID")) or -1, "")
        if not src or not tgt:
            continue
        if guids_in_scope is not None and (
                src not in guids_in_scope or tgt not in guids_in_scope):
            continue
        guid = c.get("ea_guid") or ""
        out.append({
            "connector_id": _int(c.get("Connector_ID")),
            "source_guid": src,
            "target_guid": tgt,
            "connector_type": c.get("Connector_Type") or "",
            "stereotype": c.get("Stereotype") or "",
            "profile": (profile_of(guid) if profile_of and guid else "") or "",
            "name": c.get("Name") or "",
        })
    return out


def diagram_rows(diagrams: list[dict], *,
                 in_scope: set[int] | None = None) -> list[dict]:
    """Rows for `diagram`. Geometry is deliberately not captured (decision 10)."""
    out = []
    for d in diagrams:
        pid = _int(d.get("Package_ID"))
        if in_scope is not None and pid not in in_scope:
            continue
        out.append({
            "diagram_id": _int(d.get("Diagram_ID")),
            "name": d.get("Name") or "",
            # Diagram_Type, not Type - EA's column naming is inconsistent and
            # this one has been got wrong before.
            "diagram_type": d.get("Diagram_Type") or "",
            "package_id": pid,
        })
    return out


def diagram_object_rows(diagram_objects: list[dict],
                        guid_by_id: dict[int, str],
                        *,
                        diagram_ids: set[int] | None = None,
                        guids_in_scope: set[str] | None = None) -> list[dict]:
    """Rows for `diagram_object`. Both ends must resolve."""
    out = []
    for d in diagram_objects:
        did = _int(d.get("Diagram_ID"))
        guid = guid_by_id.get(_int(d.get("Object_ID")) or -1, "")
        if did is None or not guid:
            continue
        if diagram_ids is not None and did not in diagram_ids:
            continue
        if guids_in_scope is not None and guid not in guids_in_scope:
            continue
        out.append({"diagram_id": did, "ea_guid": guid})
    return out


def attribute_rows(attributes: list[dict],
                   guid_by_id: dict[int, str],
                   *,
                   guids_in_scope: set[str] | None = None) -> list[dict]:
    """Rows for `attribute`. `Type` and `Scope` are reserved words in EA's SQL,
    which is why the extract brackets them; here they are plain keys."""
    out = []
    for a in attributes:
        guid = guid_by_id.get(_int(a.get("Object_ID")) or -1, "")
        if not guid:
            continue
        if guids_in_scope is not None and guid not in guids_in_scope:
            continue
        out.append({
            "attribute_id": _int(a.get("ID")),
            "element_guid": guid,
            "name": a.get("Name") or "",
            "attr_type": a.get("Type") or "",
            "scope": a.get("Scope") or "",
        })
    return out


def operation_rows(operations: list[dict],
                   guid_by_id: dict[int, str],
                   *,
                   guids_in_scope: set[str] | None = None) -> list[dict]:
    """Rows for `operation`. Its primary key is OperationID, where t_attribute's
    is ID - another EA naming inconsistency worth stating once."""
    out = []
    for o in operations:
        guid = guid_by_id.get(_int(o.get("Object_ID")) or -1, "")
        if not guid:
            continue
        if guids_in_scope is not None and guid not in guids_in_scope:
            continue
        out.append({
            "operation_id": _int(o.get("OperationID")),
            "element_guid": guid,
            "name": o.get("Name") or "",
            "return_type": o.get("Type") or "",
            "scope": o.get("Scope") or "",
        })
    return out


#: Frame table -> the columns that must resolve against `element.ea_guid`.
FOREIGN_GUIDS = {
    "rel_all": ("source_guid", "target_guid"),
    "diagram_object": ("ea_guid",),
    "attribute": ("element_guid",),
    "operation": ("element_guid",),
    "tag_value": ("ea_guid",),
    "overflow_tag": ("ea_guid",),
}


def dangling(frame_rows: dict[str, list[dict]]) -> list[dict]:
    """References in the frame that do not resolve against `element`.

    Should always be empty, and is returned rather than asserted so that "should
    be" is checkable by the caller and by a test. An unresolvable key inflates a
    count and makes an inner join quietly return fewer rows than the total the
    reader is looking at.
    """
    known = {r.get("ea_guid") for r in frame_rows.get("element", [])}
    out = []
    for table, columns in FOREIGN_GUIDS.items():
        for row in frame_rows.get(table, []):
            for col in columns:
                guid = row.get(col)
                if guid and guid not in known:
                    out.append({"table": table, "column": col, "value": guid})
    return out
