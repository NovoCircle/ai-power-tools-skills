#!/usr/bin/env python3
"""Tests for source reconciliation.

    python -m pytest _shared/tools/test_reconcile.py -q

Nothing here touches a repository, a COM object or the filesystem.

Several of these exist because the prototype this replaces got them wrong in a
way that looked like success.
"""
from __future__ import annotations

from ea_census import build_stereotype_index, census_elements
from reconcile import FAIL, PASS, SKIPPED, Reconciliation, format_report, reconcile

NS = "WestbrookBankArchitecture"


def stereo_row(guid, *blocks):
    desc = "".join("@STEREO;Name=%s;%s@ENDSTEREO;" % (n, ("FQName=%s;" % fq) if fq else "")
                   for n, fq in blocks)
    return {"Client": guid, "Description": desc}


def obj(guid, metaclass, stereotype=""):
    return {"ea_guid": guid, "Object_Type": metaclass, "Stereotype": stereotype}


def test_matching_counts_pass():
    rec = Reconciliation()
    rec.add("entity", "app", 45, 45)
    assert rec.ok is True
    assert rec.exit_code == 0
    assert "RECONCILED" in rec.summary()


def test_a_mismatch_fails_and_the_exit_code_is_non_zero():
    """The prototype printed NOT RECONCILED and returned 0, so every pipeline
    reading the exit status saw success."""
    rec = Reconciliation()
    rec.add("entity", "app", 46, 47)
    assert rec.ok is False
    assert rec.exit_code == 1
    assert "NOT RECONCILED" in rec.summary()
    assert rec.failures[0].delta == 1


def test_a_skipped_check_is_not_a_pass():
    """A gate that stopped checking passes everything. The release gate in this
    repository reports GREEN while skipping a check it could not run, which is
    filed as a defect; not repeating it here."""
    rec = Reconciliation()
    rec.add("entity", "app", 45, 45)
    rec.skip("scalar", "connectors", "database not reachable")
    assert rec.failures == []
    assert rec.ok is False           # still not OK
    assert rec.exit_code == 1
    assert "skipped" in rec.summary()


def test_a_missing_side_records_a_skip_rather_than_comparing_against_none():
    rec = Reconciliation()
    rec.add("scalar", "connectors", None, 12)
    assert rec.checks[0].status == SKIPPED
    assert rec.checks[0].delta is None


def test_repository_side_is_taken_from_the_census_so_multi_stereotypes_count():
    """The defect this module's own history demonstrates: resolving the profile
    with a first-match-only search counted a multi-stereotype element under one
    stereotype and missed it under the other. The database was right and the
    checker was wrong."""
    sor, app = "%s::WBASystemOfRecord" % NS, "%s::WBABusinessApplication" % NS
    objects = [obj("{M}", "Component", "WBASystemOfRecord")]
    xrefs = [stereo_row("{M}", ("WBASystemOfRecord", sor), ("WBABusinessApplication", app))]
    census = census_elements(objects, build_stereotype_index(xrefs))

    rec = reconcile(census, {"system_of_record": 1, "business_application": 1},
                    entity_key_of_table={"system_of_record": sor,
                                         "business_application": app})
    assert rec.ok is True
    assert [c.status for c in rec.checks] == [PASS, PASS]


def test_an_entity_with_no_table_is_reported_as_a_failure_not_an_absence():
    """A table silently missing is the failure nobody notices, so it gets an
    explicit 0 on the database side rather than being skipped over."""
    objects = [obj("{1}", "Component", "Thing")]
    census = census_elements(objects, {})
    rec = reconcile(census, {})
    assert len(rec.failures) == 1
    f = rec.failures[0]
    assert f.repository == 1 and f.database == 0
    assert "absent from the database" in f.detail


def test_a_table_the_census_does_not_know_about_is_flagged():
    census = census_elements([obj("{1}", "Component", "Thing")], {})
    rec = reconcile(census, {"Thing|Component": 1, "mystery": 7})
    mystery = [c for c in rec.checks if c.label == "mystery"][0]
    assert mystery.status == SKIPPED
    assert "census does not report" in mystery.detail


def test_scalars_are_compared_alongside_entities():
    census = census_elements([obj("{1}", "Component", "Thing")], {})
    rec = reconcile(census, {"Thing|Component": 1},
                    scalars={"connectors": (123, 123), "tagged values": (949, 900)})
    assert len(rec.failures) == 1
    assert rec.failures[0].label == "tagged values"
    assert rec.failures[0].delta == -49


def test_report_is_deterministic_and_names_failures():
    census = census_elements([obj("{1}", "Component", "Thing")], {})
    rec = reconcile(census, {"Thing|Component": 2})
    text = format_report(rec)
    assert format_report(rec) == text
    assert "FAIL" in text
    assert "NOT RECONCILED" in text


def test_to_dict_is_machine_readable_and_carries_the_verdict():
    rec = Reconciliation()
    rec.add("entity", "app", 46, 47)
    d = rec.to_dict()
    assert d["ok"] is False
    assert d["failures"] == 1
    assert d["detail"][0]["delta"] == 1


def test_an_empty_reconciliation_is_ok_but_proves_nothing():
    """Honest about its own limits: zero checks cannot fail. A caller must
    assert it actually ran checks, which is what the count is for."""
    rec = Reconciliation()
    assert rec.ok is True
    assert len(rec.checks) == 0
