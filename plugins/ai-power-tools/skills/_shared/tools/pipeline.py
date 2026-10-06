#!/usr/bin/env python3
"""The reporting-database build, assembled once.

`ea-reporting-database` and `ea-power-bi` call these functions rather than
copying the sequence into each skill, so the scoping and the reconciliation are
written and tested in one place.

    infer_namespace           the profile namespace, read off the census
    prepare                   extract rows + technology -> model, pivot, frame
    reconcile_against         the repository side against counts read back
    write_reports             reconciliation.txt and data-dictionary.md
    build_reporting_database  load, reconcile, record, and write all five files

Everything here is pure except `write_reports` and `build_reporting_database`,
which write files.
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass

from dictionary import data_dictionary
from dictionary import manifest as build_manifest
from ea_census import (build_stereotype_index, census_elements,
                       infer_technology_namespace, tag_coverage)
from frame import (attribute_rows, dangling, diagram_object_rows, diagram_rows,
                   element_rows, operation_rows, package_rows, relationship_rows)
from load import (build_database, database_counts, record_reconciliation,
                  scalar_counts)
from pivot import pivot
from reconcile import domain_violations, format_report, reconcile
from report_model import build_report_model


class PipelineError(Exception):
    """A frame row references an element the key map does not hold."""


@dataclass
class Prepared:
    """Everything a sink needs, built from one snapshot's extract rows."""
    tables: dict
    census: object
    model: object
    result: object
    frame_rows: dict
    guid_by_id: dict
    #: Guids of the elements placed in an entity table: the key map's rows.
    placed: set


def infer_namespace(tables: dict, mdg: dict | None) -> str:
    """The profile namespace the census finds in `t_xref` FQNames for the
    stereotypes `mdg` declares. Pass it to `prepare` as `namespace`."""
    census = census_elements(tables["object"], build_stereotype_index(tables["xref"]))
    declared = {s["name"] for s in (mdg or {}).get("stereotypes", [])}
    return infer_technology_namespace(census, declared)


def prepare(tables: dict, mdg: dict | None, *, namespace: str = "",
            strip_prefix: str = "", sparse_threshold: float = 0.05,
            multi_valued: set | None = None) -> Prepared:
    """Census, report model, pivot and frame from a snapshot's extract rows.

    `tables` is `open_snapshot(...).tables`. `mdg` is the technology definition
    from `get_mdg_from_runtime`, or None when no technology is loaded. The other
    arguments pass to `build_report_model`.

    Every frame row that refers to an element is scoped to the elements placed
    in an entity table, because those are the only ones the key map holds. An
    element with no stereotype is outside the database, so a diagram placement
    or a connector that touches one is left out rather than written as a row
    that resolves against nothing. Raises `PipelineError` if any row still does.
    """
    objects, props = tables["object"], tables["objectproperties"]
    xref_index = build_stereotype_index(tables["xref"])
    census = census_elements(objects, xref_index)
    guid_by_id = {int(o["Object_ID"]): o["ea_guid"] for o in objects}

    def guid_of_property(row):
        return guid_by_id.get(int(row["Object_ID"]), "")

    tag_stats = {e.key: tag_coverage(e, props, guid_of_property)
                 for e in census.entities}
    model = build_report_model(census, tag_stats, mdg, namespace=namespace,
                               strip_prefix=strip_prefix,
                               sparse_threshold=sparse_threshold,
                               multi_valued=multi_valued)
    result = pivot(model, objects, props, census.placement,
                   excluded_guids=census.excluded_guids,
                   guid_of_property=guid_of_property)

    model_keys = {t.entity_key for t in model.tables}
    placed = {o["ea_guid"] for o in objects
              if o["ea_guid"] not in census.excluded_guids
              and any(k in model_keys for k in census.placement.get(o["ea_guid"], ()))}

    def profile_of(guid):
        return next((s.profile for s in xref_index.get(guid, []) if s.profile), "")

    frame_rows = {
        "pkg": package_rows(tables["package"]),
        "element": element_rows(objects, model, census.placement,
                                excluded_guids=census.excluded_guids),
        "rel_all": relationship_rows(tables["connector"], guid_by_id,
                                     guids_in_scope=placed, profile_of=profile_of),
        "diagram": diagram_rows(tables["diagram"]),
        "attribute": attribute_rows(tables["attribute"], guid_by_id,
                                    guids_in_scope=placed),
        "operation": operation_rows(tables["operation"], guid_by_id,
                                    guids_in_scope=placed),
    }
    frame_rows["diagram_object"] = diagram_object_rows(
        tables["diagramobjects"], guid_by_id,
        diagram_ids={r["diagram_id"] for r in frame_rows["diagram"]},
        guids_in_scope=placed)

    unresolved = dangling(dict(frame_rows, tag_value=result.tag_value,
                               overflow_tag=result.overflow))
    if unresolved:
        raise PipelineError(
            f"{len(unresolved)} frame rows reference an element the key map does "
            f"not hold, for example {unresolved[:3]}")
    return Prepared(tables=tables, census=census, model=model, result=result,
                    frame_rows=frame_rows, guid_by_id=guid_by_id, placed=placed)


def reconcile_against(p: Prepared, entity_counts: dict, frame_counts: dict):
    """Reconcile the repository against counts read back from what was written.

    `entity_counts` maps each entity table to its row count and `frame_counts`
    each frame table, by its `FRAME_DDL` key, to its row count: from
    `database_counts` and `scalar_counts` for a database, or from the Parquet
    files read back. The repository side is computed here from the raw extract
    rows and the placed set, not from the frame rows that produced the output.
    """
    t, gid, placed = p.tables, p.guid_by_id, p.placed
    placed_ids = {int(o["Object_ID"]) for o in t["object"] if o["ea_guid"] in placed}

    def endpoint(connector, column):
        return gid.get(int(connector[column] or -1))

    repository = {
        "pkg": len(t["package"]),
        "element": len(placed),
        "rel_all": sum(1 for c in t["connector"]
                       if endpoint(c, "Start_Object_ID") in placed
                       and endpoint(c, "End_Object_ID") in placed),
        "tag_value": sum(1 for r in t["objectproperties"]
                         if (r.get("Value") or "").strip()
                         and gid.get(int(r["Object_ID"])) in placed),
        "attribute": sum(1 for a in t["attribute"]
                         if int(a["Object_ID"]) in placed_ids),
        "operation": sum(1 for o in t["operation"]
                         if int(o["Object_ID"]) in placed_ids),
        "diagram": len(t["diagram"]),
    }
    label = {"element": "element (placed in an entity table)",
             "rel_all": "rel_all (both endpoints placed)",
             "tag_value": "tag_value (on placed elements)"}
    return reconcile(
        p.census, entity_counts,
        entity_key_of_table={m.name: m.entity_key for m in p.model.tables},
        scalars={label.get(k, k): (n, frame_counts.get(k))
                 for k, n in repository.items()})


def write_reports(p: Prepared, rec, out_dir, *, run_id: str, run_at: str,
                  repository: str) -> list[dict]:
    """Write `reconciliation.txt` and `data-dictionary.md`. Returns the domain
    violations, which the dictionary lists."""
    out_dir = pathlib.Path(out_dir)
    violations = domain_violations(p.model, p.result.rows)
    (out_dir / "reconciliation.txt").write_text(
        format_report(rec) + "\n", encoding="utf-8", newline="\n")
    (out_dir / "data-dictionary.md").write_text(
        data_dictionary(p.model, run_id=run_id, run_at=run_at,
                        repository=repository, reconciliation=rec,
                        domain_violations=violations),
        encoding="utf-8", newline="\n")
    return violations


@dataclass
class Build:
    reconciliation: object
    loaded: object
    domain_violations: list
    #: False if no `load_run` row matched the run_id, so nothing was recorded.
    recorded: bool


def build_reporting_database(p: Prepared, out_dir, *, run_id: str, run_at: str,
                             repository: str, extract_run_id: str,
                             extract_digest: str, overwrite: bool = False) -> Build:
    """Load the database, reconcile it, record the verdict, and write the files.

    Writes `reporting.sqlite`, `reconciliation.txt`, `data-dictionary.md`,
    `manifest.json` and `issued-sql.log` into `out_dir`. `overwrite=False`
    refuses an existing database.
    """
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    db = out_dir / "reporting.sqlite"
    loaded = build_database(db, p.model, p.result, p.frame_rows,
                            run_id=run_id, run_at=run_at, repository=repository,
                            extract_run_id=extract_run_id,
                            extract_digest=extract_digest, overwrite=overwrite)
    rec = reconcile_against(p, database_counts(db, p.model), scalar_counts(db))
    recorded = record_reconciliation(db, run_id, rec)
    violations = write_reports(p, rec, out_dir, run_id=run_id, run_at=run_at,
                               repository=repository)
    (out_dir / "manifest.json").write_text(json.dumps(build_manifest(
        p.model, loaded, run_id=run_id, run_at=run_at, repository=repository,
        reconciliation=rec, domain_violations=violations), indent=2),
        encoding="utf-8", newline="\n")
    (out_dir / "issued-sql.log").write_text(
        "\n".join(loaded.sql_log) + "\n", encoding="utf-8", newline="\n")
    return Build(reconciliation=rec, loaded=loaded, domain_violations=violations,
                 recorded=recorded)
