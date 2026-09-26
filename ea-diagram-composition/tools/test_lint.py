#!/usr/bin/env python3
"""Tests for the diagram linter.

Run from the repository root:

    python -m pytest ea-diagram-composition/tools/test_lint.py -q

Nothing here touches a repository, a COM object or the filesystem.

WHAT THIS FILE DOES AND DOES NOT COVER
---------------------------------------
The geometry rules - overlap, canvas, sizing, pitch, routing - are exercised in
depth by the benchmark harness's own suite, which runs them through
`scoring.score_diagram` against the corpus. Duplicating those cases here would
be two copies of one fact, and this build has already been bitten once by two
copies of a fact agreeing with each other while both were wrong.

So what is tested here is what is NEW and what is STRUCTURAL: the profile
suppression table, the loop's stopping conditions, the report's own contract,
and the layer boundary that makes the module reusable at all. Plus one case per
rule that proves it is wired into `lint_diagram` - not that the rule is correct,
but that it runs.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import lint  # noqa: E402
from lint import (  # noqa: E402
    Finding,
    LintReport,
    MAX_CORRECTION_PASSES,
    PROFILE_KEYS,
    SUPPRESSED_BY,
    is_stalled,
    lint_diagram,
)


# ---------------------------------------------------------------------------
# Fixtures, in EA's coordinate convention
# ---------------------------------------------------------------------------
def box(element_id, left, top, width=100, height=60, **extra):
    """One placed element. `top` is negative, as EA writes it."""
    return {
        "element_id": element_id,
        "left": left, "top": top,
        "right": left + width, "bottom": top - height,
        "width": width, "height": height,
        **extra,
    }


def verified(objects=(), links=(), cx=1000, cy=800):
    return {
        "ok": True,
        "objects": list(objects),
        "links": list(links),
        "canvas": {"cx": cx, "cy": cy},
    }


def _row(n, pitch=140, top=-40):
    return [box(i, left=20 + i * pitch, top=top) for i in range(n)]


# ---------------------------------------------------------------------------
# The layer boundary - the reason this module is reusable
# ---------------------------------------------------------------------------
def test_the_linter_does_not_import_the_binding_layer():
    """Language-neutral by construction, enforced rather than asserted in prose.

    A profile arrives as a plain mapping. The moment this module imports
    `bindings` it acquires an opinion about notations, and the claim that one
    linter serves a notation nobody wrote a binding for stops being true.

    Walks import STATEMENTS rather than searching the text, because a mention
    inside a docstring is documentation and must not trip this - while
    `from bindings import X` must.
    """
    tree = ast.parse((_HERE / "lint.py").read_text(encoding="utf-8"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported.append(node.module)
    forbidden = {"bindings", "compose", "yaml"}
    assert not (set(imported) & forbidden), imported


def test_the_linter_names_no_modeling_language():
    """No notation, technology id or stereotype anywhere in the module.

    Same rule the layout engine is held to. A linter that knows what ArchiMate
    is will eventually be asked to treat it specially, and then it is not one
    linter any more.

    Checked over identifiers AND string constants, because the realistic leak
    is a rule message that names a notation, not an import.
    """
    source = (_HERE / "lint.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.append(node.id)
        elif isinstance(node, ast.Attribute):
            names.append(node.attr)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            names.append(node.value)
        elif isinstance(node, ast.arg):
            names.append(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            names.append(node.name)
    blob = " ".join(names).lower()
    for notation in ("archimate", "bpmn", "sysml", "togaf", "erd", "archi"):
        assert notation not in blob, f"{notation!r} leaked into lint.py"

    # `stereotype` is deliberately NOT on that list, and the reason is worth
    # stating because it looks like an omission. It is not a modeling language;
    # it is EA's own generic term, and it reaches this module as the names of
    # display settings the server exposes - `hide_element_stereotypes` and
    # `hide_connector_stereotypes`. Suppressing stereotype TEXT is a
    # presentation decision that applies to every notation equally. What must
    # stay out is a branch on WHICH stereotype, and that is what the rest of
    # this test covers.
    assert not any(k for k in PROFILE_KEYS if k not in
                   {"hide_connector_labels", "hide_element_stereotypes",
                    "hide_connector_stereotypes", "show_element_notes",
                    "hide_attribute_types", "hide_operation_return_types",
                    "hide_operation_brackets", "collapses_parallel"}), (
        "a new profile key was added; confirm it names a presentation setting "
        "rather than a notation concept before adding it here"
    )


# ---------------------------------------------------------------------------
# The report's contract
# ---------------------------------------------------------------------------
def test_clean_means_no_errors_not_no_findings():
    """Several rules here fire on diagrams that are correct for their context.

    If `clean` meant "no findings at all" the bar would be one nobody clears,
    and a linter nobody can satisfy is a linter that gets switched off.
    """
    report = LintReport()
    report.add(Finding(rule="r", severity="warning", message="m"))
    assert report.clean
    assert report.warnings and not report.errors
    report.add(Finding(rule="r2", severity="error", message="m"))
    assert not report.clean


def test_every_finding_carries_a_correction():
    """Findings must be actionable by the loop, not merely descriptive.

    Asserted over a diagram built to trip several rules at once, so this cannot
    pass by finding nothing.
    """
    objects = [
        box(1, left=0, top=-10),
        box(2, left=50, top=-30),          # overlaps 1
        box(3, left=5000, top=-40),        # outside the canvas
    ]
    report = lint_diagram(verified(objects))
    assert report.findings, "the fixture stopped tripping any rule"
    for finding in report.findings:
        assert finding.correction.strip(), f"{finding.rule} has no correction"
        assert finding.severity in ("error", "warning", "info")
        assert finding.message.strip()


def test_a_report_signature_ignores_message_wording():
    """So a pass that changed a coordinate is not read as a different finding."""
    a, b = LintReport(), LintReport()
    a.add(Finding(rule="overlap", severity="error", message="at x=10",
                  subjects=(1, 2)))
    b.add(Finding(rule="overlap", severity="error", message="at x=40",
                  subjects=(1, 2)))
    assert a.signature() == b.signature()


# ---------------------------------------------------------------------------
# The bounded loop
# ---------------------------------------------------------------------------
def test_the_correction_budget_is_stated_and_small():
    """A loop that runs until it is happy either terminates or lies."""
    assert isinstance(MAX_CORRECTION_PASSES, int)
    assert 1 <= MAX_CORRECTION_PASSES <= 5


def test_a_pass_that_changed_nothing_is_a_stall():
    objects = [box(1, left=0, top=-10), box(2, left=50, top=-30)]
    first = lint_diagram(verified(objects))
    second = lint_diagram(verified(objects))
    assert is_stalled(first, second)


def test_the_first_pass_is_never_a_stall():
    report = lint_diagram(verified([box(1, left=0, top=-10)]))
    assert not is_stalled(None, report)


def test_a_pass_that_fixed_something_is_not_a_stall():
    before = lint_diagram(verified([box(1, left=0, top=-10),
                                    box(2, left=50, top=-30)]))
    after = lint_diagram(verified([box(1, left=0, top=-10),
                                   box(2, left=300, top=-10)]))
    assert not is_stalled(before, after)
    assert after.clean


# ---------------------------------------------------------------------------
# Profile awareness
# ---------------------------------------------------------------------------
def test_every_suppressed_rule_names_a_key_the_linter_understands():
    """The suppression table cannot reference a profile key nobody supplies.

    A typo here would silently never suppress, which is the failure mode that
    gets a linter switched off by an irritated user rather than reported.
    """
    for rule, key in SUPPRESSED_BY.items():
        assert key in PROFILE_KEYS, f"{rule!r} keys off unknown {key!r}"


def test_a_profile_suppression_is_reported_not_silent():
    """A rule that was skipped has to be visible, or a clean report overstates
    what was checked."""
    report = lint_diagram(verified([box(1, left=0, top=-10)]),
                          profile={"hide_connector_labels": True})
    assert "missing-connector-labels" in report.suppressed


def test_no_profile_suppresses_nothing():
    report = lint_diagram(verified([box(1, left=0, top=-10)]))
    assert report.suppressed == []


def test_a_profile_that_hides_nothing_suppresses_nothing():
    report = lint_diagram(verified([box(1, left=0, top=-10)]),
                          profile={"hide_connector_labels": False})
    assert report.suppressed == []


def test_an_unknown_profile_key_is_ignored_not_rejected():
    """A profile vocabulary is allowed to grow without breaking the linter."""
    report = lint_diagram(verified([box(1, left=0, top=-10)]),
                          profile={"some_future_setting": True})
    assert report.suppressed == []


@pytest.mark.parametrize("key", PROFILE_KEYS)
def test_no_profile_key_can_suppress_a_geometry_rule(key):
    """Presentation must never switch off a structural defect.

    Overlapping elements are wrong under every profile. If a future suppression
    entry ever keyed a geometry rule off a display setting, this is what says
    so - an executive view is allowed to hide labels, not to hide collisions.
    """
    objects = [box(1, left=0, top=-10), box(2, left=50, top=-30)]
    report = lint_diagram(verified(objects), profile={key: True})
    assert any(f.rule == "overlap" for f in report.findings), key
    assert not report.clean, key


# ---------------------------------------------------------------------------
# Each rule is actually wired into the driver
# ---------------------------------------------------------------------------
def test_overlapping_elements_are_an_error():
    report = lint_diagram(verified([box(1, left=0, top=-10),
                                    box(2, left=50, top=-30)]))
    assert [f.rule for f in report.findings] == ["overlap"]
    assert report.metrics["overlaps"] == 1


def test_containment_is_not_an_overlap():
    """A nested grid nests deliberately and must not be punished for it."""
    outer = box(1, left=0, top=-10, width=400, height=300)
    inner = box(2, left=40, top=-60, width=100, height=60)
    report = lint_diagram(verified([outer, inner]))
    assert report.metrics["overlaps"] == 0
    assert report.clean


def test_touching_elements_do_not_overlap_but_nothing_else_may_rely_on_that():
    """Abutting rects are correct geometry - swimlanes touch by design.

    Stated as its own test because it is load-bearing in the wrong direction:
    no-overlap never implies whitespace, so any spacing rule has to measure
    spacing itself. That has been learned twice in this programme.
    """
    a = box(1, left=0, top=-10, width=100)
    b = box(2, left=100, top=-10, width=100)
    report = lint_diagram(verified([a, b]))
    assert report.metrics["overlaps"] == 0


def test_an_element_outside_the_canvas_is_a_warning():
    report = lint_diagram(verified([box(1, left=5000, top=-40)], cx=800, cy=600))
    assert [f.rule for f in report.findings] == ["out-of-canvas"]
    assert report.clean, "out-of-canvas is a warning; EA grows some canvases"


def test_inconsistent_sizing_within_a_role_is_an_error():
    role = [box(1, left=0, top=-40, width=100),
            box(2, left=200, top=-40, width=180)]
    report = lint_diagram(verified(role), roles={"capability": role})
    assert any(f.rule == "uniform-sizing" for f in report.findings)
    assert not report.clean


def test_two_roles_may_differ_from_each_other():
    """Uniform WITHIN a role, not across roles - the caller decides what a role
    is, because that is the language question this module refuses to answer."""
    small = [box(1, left=0, top=-40, width=30, height=30),
             box(2, left=100, top=-40, width=30, height=30)]
    large = [box(3, left=200, top=-40, width=110, height=60),
             box(4, left=400, top=-40, width=110, height=60)]
    report = lint_diagram(verified(small + large),
                          roles={"event": small, "activity": large})
    assert report.metrics["roles_with_inconsistent_sizing"] == 0
    assert report.clean


def test_uneven_spacing_in_a_row_is_reported():
    row = [box(1, left=0, top=-40), box(2, left=140, top=-40),
           box(3, left=600, top=-40)]
    report = lint_diagram(verified(row), rows=[row])
    assert any(f.rule == "pitch" for f in report.findings)


def test_an_evenly_spaced_row_is_clean():
    row = _row(4)
    report = lint_diagram(verified(row), rows=[row])
    assert not [f for f in report.findings if f.rule == "pitch"]
    assert report.metrics["worst_pitch_spread"] == 0


def test_a_mixed_size_row_with_no_whitespace_is_an_error():
    """The counterexample the pitch floor exists for.

    Alternating widths with an even center pitch drive every edge gap to zero
    while the center spread stays perfect - a row with no whitespace anywhere.
    The overlap rule cannot catch it, because touching is exempt by design.
    """
    row = [box(1, left=0, top=-40, width=30),
           box(2, left=30, top=-40, width=110),
           box(3, left=140, top=-40, width=30),
           box(4, left=170, top=-40, width=110)]
    report = lint_diagram(verified(row), rows=[row])
    pitch = [f for f in report.findings if f.rule == "pitch"]
    assert any(f.severity == "error" for f in pitch), [str(f) for f in pitch]


def test_a_connector_with_no_route_is_a_warning():
    links = [{"connector_id": 7, "stored": True, "route": None}]
    report = lint_diagram(verified([box(1, left=0, top=-40)], links))
    assert any(f.rule == "routing-unset" for f in report.findings)


def test_an_unstored_link_is_not_judged_for_routing():
    """EA draws a relationship between two placed elements whether or not a
    presentation row exists. A line with no row has no route to set."""
    links = [{"connector_id": 7, "stored": False, "route": None}]
    report = lint_diagram(verified([box(1, left=0, top=-40)], links))
    assert not [f for f in report.findings if f.rule.startswith("routing")]
    assert report.metrics["links_stored"] == 0


def test_a_route_that_is_not_the_expected_one_is_reported():
    links = [{"connector_id": 7, "stored": True, "route": "Direct"}]
    report = lint_diagram(verified([box(1, left=0, top=-40)], links),
                          expected_route="OrthogonalSquare")
    assert any(f.rule == "routing-mismatch" for f in report.findings)


def test_rules_needing_a_grouping_do_not_run_without_one():
    """Omitting `roles`/`rows` must not invent them.

    Guessing which elements share a role from their geometry would be inventing
    the metamodel this module refuses to have, and it would do it silently.
    """
    row = [box(1, left=0, top=-40, width=100),
           box(2, left=200, top=-40, width=180)]
    report = lint_diagram(verified(row))
    assert report.metrics["roles_with_inconsistent_sizing"] == 0
    assert report.clean


def test_an_empty_diagram_lints_without_crashing():
    report = lint_diagram(verified([]))
    assert report.clean
    assert report.metrics["objects"] == 0
