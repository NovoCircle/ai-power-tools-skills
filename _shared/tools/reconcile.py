#!/usr/bin/env python3
"""Reconcile a built database against the repository it came from.

PURE. No repository calls, no COM, no file or network I/O, no clock, no
randomness. It compares two sets of counts and reports.

WHY THIS EXISTS AT ALL
----------------------
A prototype database once passed every internal check it had - zero orphans,
every count reconciling against its own census, two query engines agreeing with
each other - while under-reporting the model, because the EXTRACT was incomplete.
Both sides were reading the same short input.

Verifying a pipeline against itself proves consistency, never completeness.

So the repository side of every check here must be computed from repository rows,
and - this is the part that is easy to get wrong - computed CORRECTLY. The first
version of this reconciliation resolved an element's profile with
`re.search(r"FQName=...")`, which returns the FIRST match only, so a
multi-stereotype element was counted under one stereotype and missing from the
other. The database was right and the checker was wrong, which is the better
direction to fail in but still a defect.

That is why the repository side is built from `ea_census`, which parses every
`@STEREO` block, rather than from a query written fresh here. One parse, one
rule, used by both the loader and its auditor.

A check that cannot be run is NOT a pass. `status` has three values, and
`ok` requires zero failures AND zero skips.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ea_census import ElementCensus

PASS = "pass"
FAIL = "fail"
SKIPPED = "skipped"


@dataclass
class Check:
    dimension: str
    label: str
    repository: int | None = None
    database: int | None = None
    status: str = PASS
    detail: str = ""

    @property
    def delta(self) -> int | None:
        if self.repository is None or self.database is None:
            return None
        return self.database - self.repository


@dataclass
class Reconciliation:
    checks: list[Check] = field(default_factory=list)

    def add(self, dimension: str, label: str,
            repository: int | None, database: int | None, detail: str = "") -> Check:
        if repository is None or database is None:
            c = Check(dimension, label, repository, database, SKIPPED,
                      detail or "one side was not supplied")
        else:
            c = Check(dimension, label, repository, database,
                      PASS if repository == database else FAIL, detail)
        self.checks.append(c)
        return c

    def skip(self, dimension: str, label: str, reason: str) -> Check:
        c = Check(dimension, label, None, None, SKIPPED, reason)
        self.checks.append(c)
        return c

    @property
    def failures(self) -> list[Check]:
        return [c for c in self.checks if c.status == FAIL]

    @property
    def skipped(self) -> list[Check]:
        return [c for c in self.checks if c.status == SKIPPED]

    @property
    def ok(self) -> bool:
        """A skipped check is not a pass.

        The release gate in this repository reports GREEN while skipping a check
        it could not run, and that is filed as a defect. Not repeating it here.
        """
        return not self.failures and not self.skipped

    @property
    def exit_code(self) -> int:
        """0 only when everything ran and everything matched.

        The prototype printed NOT RECONCILED and returned 0, so any pipeline
        reading the exit status saw success.
        """
        return 0 if self.ok else 1

    def summary(self) -> str:
        n = len(self.checks)
        if self.ok:
            return f"{n} checks, 0 failures - RECONCILED"
        bits = [f"{n} checks", f"{len(self.failures)} failure(s)"]
        if self.skipped:
            bits.append(f"{len(self.skipped)} skipped")
        return ", ".join(bits) + " - NOT RECONCILED"

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "checks": len(self.checks),
            "failures": len(self.failures),
            "skipped": len(self.skipped),
            "detail": [
                {"dimension": c.dimension, "label": c.label,
                 "repository": c.repository, "database": c.database,
                 "delta": c.delta, "status": c.status, "detail": c.detail}
                for c in self.checks
            ],
        }


def repository_entity_counts(census: ElementCensus) -> dict[str, int]:
    """Per-entity counts taken from the census.

    Deliberately NOT a fresh query. The census already applies the provenance
    rule and parses every `@STEREO` block, and a second implementation here is
    how the two sides drift apart - which is exactly the class of bug this
    function's own history demonstrates.
    """
    return {e.key: e.count for e in census.entities}


def reconcile(census: ElementCensus,
              database_counts: dict[str, int],
              *,
              entity_key_of_table: dict[str, str] | None = None,
              scalars: dict[str, tuple[int | None, int | None]] | None = None
              ) -> Reconciliation:
    """Compare a database against the repository census that produced it.

    `database_counts` is table name -> row count, read back from the built
    database. `entity_key_of_table` maps those table names to census entity
    keys; without it, keys are assumed to be table names.

    `scalars` carries the other dimensions - connectors, tagged values,
    attributes, diagrams - as label -> (repository, database). Pass None on
    either side to record the check as SKIPPED rather than silently omitting it.
    """
    rec = Reconciliation()
    repo_counts = repository_entity_counts(census)
    key_of = entity_key_of_table or {}

    # Entities the database holds
    for table in sorted(database_counts):
        key = key_of.get(table, table)
        want = repo_counts.get(key)
        if want is None:
            rec.add("entity", table, None, database_counts[table],
                    f"table maps to entity key {key!r}, which the census does not report")
            continue
        rec.add("entity", table, want, database_counts[table])

    # Entities the repository has and the database does not. A table silently
    # absent is the failure mode nobody notices, so it gets a 0 on the database
    # side rather than being skipped over.
    tables_by_key = {key_of.get(t, t) for t in database_counts}
    for key in sorted(repo_counts):
        if key not in tables_by_key:
            rec.add("entity", f"<no table for {key}>", repo_counts[key], 0,
                    "present in the repository, absent from the database")

    for label, (want, got) in sorted((scalars or {}).items()):
        rec.add("scalar", label, want, got)

    return rec


def format_report(rec: Reconciliation) -> str:
    """A plain-text report. Deterministic, and failures are not buried."""
    lines = []
    for dim in sorted({c.dimension for c in rec.checks}):
        lines.append(f"=== {dim.upper()} ===")
        for c in [x for x in rec.checks if x.dimension == dim]:
            mark = {PASS: "OK  ", FAIL: "FAIL", SKIPPED: "SKIP"}[c.status]
            repo = "-" if c.repository is None else c.repository
            db = "-" if c.database is None else c.database
            line = f"  {mark} {c.label:<48} repo={repo:<8} db={db}"
            if c.detail:
                line += f"   ({c.detail})"
            lines.append(line)
        lines.append("")
    lines.append(rec.summary())
    return "\n".join(lines)


def domain_violations(model, rows: dict[str, list[dict]], *,
                      separator: str = ",") -> list[dict]:
    """Values that fall outside a DECLARED enum domain.

    Checked against the entity rows rather than `tag_value`, because the bridge is
    keyed by element and the same tag name can be declared with different domains
    on different stereotypes - so only the per-table rows say which domain applies.

    Only declared domains are checkable. An observed domain is by construction
    every value that was seen, so it cannot be violated; the gap between the two
    is `DRIFT_ENUM_OBSERVED_UNDECLARED` in the census, which is a different
    finding about the technology rather than about the data.

    A violation is not a load failure. It is a governance finding, reported with
    a count so a reviewer can see whether it is one typo or a whole convention
    nobody declared.
    """
    out: list[dict] = []
    for table in model.tables:
        for col in table.columns:
            if col.enum_source != "declared" or not col.enum_values:
                continue
            allowed = set(col.enum_values)
            counts: dict[str, int] = {}
            for row in rows.get(table.name, []):
                raw = row.get(col.name)
                if raw is None or str(raw).strip() == "":
                    continue            # absent is coverage, not a violation
                parts = ([p.strip() for p in str(raw).split(separator)]
                         if col.multi_valued else [str(raw).strip()])
                for p in parts:
                    if p and p not in allowed:
                        counts[p] = counts.get(p, 0) + 1
            for value in sorted(counts):
                out.append({"table": table.name, "column": col.name,
                            "tag": col.source_tag, "value": value,
                            "count": counts[value]})
    return out


# There is deliberately NO function here folding domain violations into a
# Reconciliation.
#
# One was written and the first live run killed it. A value outside a declared
# enumeration is in the repository and is in the database, so the load was
# faithful - which is the only question a reconciliation answers. Failing the
# build on it meant `load_run.reconciled = 0` and a manifest saying `ok: false`
# over a database that had loaded all 298 elements correctly, and it would do that
# on every customer model carrying any governance drift at all. Surfacing drift is
# the capability; it is not an error condition. Violations travel in the data
# dictionary and the manifest, where a reader can see them, and the reconciliation
# stays a statement about load fidelity.
