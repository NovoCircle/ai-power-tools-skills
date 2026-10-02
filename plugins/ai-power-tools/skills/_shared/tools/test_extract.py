#!/usr/bin/env python3
"""Tests for the extraction layer's decision logic.

    python -m pytest _shared/tools/test_extract.py -q

`extract.py` is the one module here that talks COM, but its SCOPE RESOLUTION is
ordinary arithmetic over rows and is tested with a fake extractor. Nothing here
touches a repository, a COM object or the filesystem. The COM call itself -
`GetActiveObject` plus `SQLQuery` - is the untested surface, deliberately: it is
one line, and faking it would test the fake.
"""
from __future__ import annotations

import extract as ex_mod
from extract import CENSUS_QUERIES, STRUCTURE_QUERIES, Extractor, resolve_scope


class FakeRepo:
    """Returns canned rows and records the SQL it was asked to run."""

    def __init__(self, rows):
        self.rows = rows
        self.seen = []

    def SQLQuery(self, sql):          # noqa: N802 - matches EA's COM name
        self.seen.append(sql)
        return sql


def fake_extractor(rows):
    repo = FakeRepo(rows)
    return Extractor(repo, lambda _: rows), repo


def chain(depth):
    """A package chain 1 -> 2 -> ... -> depth+1, parented at 0."""
    out = [{"Package_ID": "1", "Parent_ID": "0"}]
    for i in range(2, depth + 2):
        out.append({"Package_ID": str(i), "Parent_ID": str(i - 1)})
    return out


def test_a_flat_subtree_resolves():
    rows = [{"Package_ID": "1", "Parent_ID": "0"},
            {"Package_ID": "2", "Parent_ID": "1"},
            {"Package_ID": "3", "Parent_ID": "1"}]
    ex, _ = fake_extractor(rows)
    ids, depth, truncated = resolve_scope(ex, 1)
    assert ids == [1, 2, 3]
    assert depth == 1
    assert truncated is False


def test_a_deep_chain_is_NOT_truncated():
    """The shipped `_package_subtree_ids` caps at max_depth=8 and `continue`s
    past anything deeper with no warning and no flag, so a deep tree silently
    loses its leaves (APT-2026-0216). This walks the whole tree.

    12 levels is past that cap on purpose.
    """
    ex, _ = fake_extractor(chain(12))
    ids, depth, truncated = resolve_scope(ex, 1)
    assert len(ids) == 13             # root + 12
    assert 13 in ids                  # the deepest package survives
    assert depth == 12                # and the depth reached is reported
    assert truncated is False


def test_depth_reached_is_reported_so_a_caller_can_see_how_deep_it_went():
    ex, _ = fake_extractor(chain(3))
    _, depth, _ = resolve_scope(ex, 1)
    assert depth == 3


def test_a_cycle_does_not_hang():
    """The only guard the walk needs. A self-parenting package is malformed but
    has been seen in real repositories."""
    rows = [{"Package_ID": "1", "Parent_ID": "2"},
            {"Package_ID": "2", "Parent_ID": "1"}]
    ex, _ = fake_extractor(rows)
    ids, _, _ = resolve_scope(ex, 1)
    assert sorted(ids) == [1, 2]


def test_unparseable_package_rows_are_skipped_not_fatal():
    rows = [{"Package_ID": "x", "Parent_ID": "0"},
            {"Package_ID": "2", "Parent_ID": "1"}]
    ex, _ = fake_extractor(rows)
    ids, _, _ = resolve_scope(ex, 1)
    assert ids == [1, 2]


def test_a_root_with_no_children_resolves_to_itself():
    ex, _ = fake_extractor([{"Package_ID": "9", "Parent_ID": "0"}])
    ids, depth, _ = resolve_scope(ex, 9)
    assert ids == [9]
    assert depth == 0


def test_resolution_is_deterministic_regardless_of_row_order():
    rows = [{"Package_ID": "3", "Parent_ID": "1"},
            {"Package_ID": "2", "Parent_ID": "1"},
            {"Package_ID": "1", "Parent_ID": "0"}]
    ex1, _ = fake_extractor(rows)
    ex2, _ = fake_extractor(list(reversed(rows)))
    assert resolve_scope(ex1, 1)[0] == resolve_scope(ex2, 1)[0]


def test_every_statement_is_logged_with_its_cost():
    """The issued-SQL log is a deliverable: when a count is questioned, the
    statement that produced it has to be readable."""
    ex, _ = fake_extractor([{"Package_ID": "1", "Parent_ID": "0"}])
    ex.query("SELECT 1", "probe")
    entry = ex.sql_log[-1]
    assert entry["label"] == "probe"
    assert entry["sql"] == "SELECT 1"
    assert "ms" in entry and "rows" in entry


def test_reserved_word_columns_are_bracketed():
    """Read from EA's schema rather than guessed: t_attribute needs [Type] and
    [Scope], t_operation needs them too, t_connectortag needs [VALUE]."""
    assert "[Type]" in STRUCTURE_QUERIES["attribute"]
    assert "[Scope]" in STRUCTURE_QUERIES["attribute"]
    assert "[Type]" in STRUCTURE_QUERIES["operation"]
    assert "[VALUE]" in STRUCTURE_QUERIES["connectortag"]


def test_diagram_uses_its_real_type_column():
    """t_diagram's type column is Diagram_Type, NOT Type - a guess here returns
    an invalid-column error at best and a modal dialog at worst."""
    assert "Diagram_Type" in STRUCTURE_QUERIES["diagram"]
    assert "Diagram_ID" in STRUCTURE_QUERIES["diagram"]


def test_queries_stay_inside_the_portable_subset():
    """No CTEs, no window functions, no backend-specific syntax. EA reports a
    statement its backend cannot run as a modal dialog that holds the COM
    connection, so every later call appears to hang rather than erroring."""
    for sql in list(CENSUS_QUERIES.values()) + list(STRUCTURE_QUERIES.values()):
        upper = sql.upper()
        assert upper.lstrip().startswith("SELECT")
        for banned in ("WITH ", "OVER(", "OVER (", "LIMIT ", "TOP ", "::"):
            assert banned not in upper


def test_int_coercion_returns_a_sentinel_rather_than_raising():
    assert ex_mod._int("4") == 4
    assert ex_mod._int(None) == -1
    assert ex_mod._int("not a number") == -1


def test_the_connector_query_pulls_the_guid_that_makes_provenance_resolvable():
    """t_xref keys stereotype provenance by GUID. Without ea_guid here,
    `rel_all.profile` could only ever be empty - a column that ships always-NULL
    reads as "no connector has a profile", which is a claim, not an absence."""
    assert "ea_guid" in STRUCTURE_QUERIES["connector"]
