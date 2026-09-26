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
import json
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


# ===========================================================================
# Rules that read identity, not only geometry
# ===========================================================================
# These are the rules that were INERT in the scorer this linter replaces: they
# read `name`, `type`, `fill` and the link endpoints, and `verify_diagram` did
# not return any of them. Their tests passed because the fixtures invented what
# the rules wanted. So every test below that could be written against a real
# captured payload is written against one - see `real_payload`.
_REAL_PAYLOAD = (
    Path(__file__).resolve().parents[3]
    / "ai-power-tools" / "ea-mcp-server" / "tests" / "fixtures"
    / "verify_diagram_real_payload.json"
)


def _load_real(name):
    if not _REAL_PAYLOAD.is_file():
        pytest.skip(f"real payload fixture not present at {_REAL_PAYLOAD}")
    return json.loads(_REAL_PAYLOAD.read_text(encoding="utf-8"))[name]


def test_the_hand_built_fixture_cannot_invent_a_field_production_lacks():
    """The fix for the whole class of bug, not just the three rules.

    A hand-built fixture that supplies a key `verify_diagram` never returns
    makes a rule look like it works. Three rules were inert for exactly that
    reason. This compares the keys `box()` produces against the keys a REAL
    captured payload has, and fails if the helper can conjure one.

    If this fails after a deliberate `verify_diagram` change, re-capture the
    fixture - do not widen the allowance here, because the allowance is the
    thing under test.
    """
    real = _load_real("FieldProbe")
    real_object_keys = set(real["objects"][0])
    sample = box(1, left=0, top=-40, name="X", type="Class", fill="#112233")
    invented = set(sample) - real_object_keys
    assert not invented, (
        f"the test helper produces keys production never returns: {invented}"
    )

    real_link_keys = set(real["links"][0])
    link_sample = {"connector_id": 1, "stored": True, "route": "Direct",
                   "name": "uses", "source_element_id": 1,
                   "target_element_id": 2}
    invented_links = set(link_sample) - real_link_keys - {"stored"}
    assert not invented_links, invented_links


def test_a_real_payload_lints_without_crashing():
    """Every rule, over geometry EA actually produced."""
    real = _load_real("FieldProbe")
    report = lint_diagram(real)
    assert isinstance(report.metrics["objects"], int)
    assert report.metrics["objects"] == 2
    # The denominator matters: zero crossings over zero measurable links is not
    # a result, and reporting it as one is what hid the inert rule for months.
    assert report.metrics["crossings_measured_over"] == 1


# ---------------------------------------------------------------------------
# Crossings
# ---------------------------------------------------------------------------
def test_crossings_are_counted_between_link_endpoints():
    objects = [box(1, left=0, top=-40), box(2, left=400, top=-40),
               box(3, left=0, top=-240), box(4, left=400, top=-240)]
    links = [
        {"connector_id": 10, "stored": True, "route": "Direct",
         "source_element_id": 1, "target_element_id": 4, "name": "a"},
        {"connector_id": 11, "stored": True, "route": "Direct",
         "source_element_id": 3, "target_element_id": 2, "name": "b"},
    ]
    report = lint_diagram(verified(objects, links))
    assert report.metrics["crossings"] == 1
    assert report.metrics["crossings_measured_over"] == 2
    assert any(f.rule == "crossings" for f in report.findings)


def test_crossings_are_info_because_some_are_unavoidable():
    """A rule that called every crossing a defect would fire on correct
    diagrams, and those are the rules that get a linter switched off."""
    objects = [box(1, left=0, top=-40), box(2, left=400, top=-40),
               box(3, left=0, top=-240), box(4, left=400, top=-240)]
    links = [
        {"connector_id": 10, "stored": True, "source_element_id": 1,
         "target_element_id": 4, "name": "a"},
        {"connector_id": 11, "stored": True, "source_element_id": 3,
         "target_element_id": 2, "name": "b"},
    ]
    report = lint_diagram(verified(objects, links))
    crossing = [f for f in report.findings if f.rule == "crossings"]
    assert crossing and crossing[0].severity == "info"
    assert report.clean


def test_links_with_no_endpoints_are_reported_as_unmeasured():
    """The exact failure that made this rule inert: links present, endpoints
    absent, and a confident `crossings: 0` on every diagram."""
    objects = [box(1, left=0, top=-40), box(2, left=400, top=-40)]
    links = [{"connector_id": 10, "stored": True, "route": "Direct"}]
    report = lint_diagram(verified(objects, links))
    assert report.metrics["crossings_measured_over"] == 0
    assert any("crossings" in note for note in report.not_run)


def test_connectors_meeting_at_a_shared_element_do_not_cross():
    objects = [box(1, left=0, top=-40), box(2, left=400, top=-40),
               box(3, left=200, top=-240)]
    links = [
        {"connector_id": 10, "stored": True, "source_element_id": 1,
         "target_element_id": 3, "name": "a"},
        {"connector_id": 11, "stored": True, "source_element_id": 2,
         "target_element_id": 3, "name": "b"},
    ]
    report = lint_diagram(verified(objects, links))
    assert report.metrics["crossings"] == 0


# ---------------------------------------------------------------------------
# Color
# ---------------------------------------------------------------------------
def test_two_fills_with_nothing_explaining_them_is_a_warning():
    objects = [box(1, left=0, top=-40, name="A", type="Class", fill="#cc3300"),
               box(2, left=200, top=-40, name="B", type="Class", fill="#336699")]
    report = lint_diagram(verified(objects))
    assert any(f.rule == "unexplained-color" for f in report.findings)
    assert report.clean, "unexplained color is a warning, not an error"


def test_one_fill_carries_no_information():
    objects = [box(1, left=0, top=-40, name="A", type="Class", fill="#cc3300"),
               box(2, left=200, top=-40, name="B", type="Class", fill="#cc3300")]
    report = lint_diagram(verified(objects))
    assert not [f for f in report.findings if f.rule == "unexplained-color"]


def test_a_named_container_explains_the_colors():
    """A banded diagram's band names ARE its key; demanding a separate legend
    on top would be noise, and noisy rules get ignored."""
    objects = [box(1, left=0, top=-40, name="A", type="Class", fill="#cc3300"),
               box(2, left=200, top=-40, name="B", type="Class", fill="#336699"),
               box(9, left=0, top=-20, width=400, height=200,
                   name="Channels", type="Boundary")]
    report = lint_diagram(verified(objects))
    assert not [f for f in report.findings if f.rule == "unexplained-color"]


def test_an_unnamed_container_explains_nothing():
    objects = [box(1, left=0, top=-40, name="A", type="Class", fill="#cc3300"),
               box(2, left=200, top=-40, name="B", type="Class", fill="#336699"),
               box(9, left=0, top=-20, width=400, height=200,
                   name="", type="Boundary")]
    report = lint_diagram(verified(objects))
    assert any(f.rule == "unexplained-color" for f in report.findings)


def test_a_legend_explains_the_colors():
    objects = [box(1, left=0, top=-40, name="A", type="Class", fill="#cc3300"),
               box(2, left=200, top=-40, name="B", type="Class", fill="#336699"),
               box(9, left=0, top=-400, name="Legend", type="Text")]
    report = lint_diagram(verified(objects))
    assert not [f for f in report.findings if f.rule == "unexplained-color"]


# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------
def test_a_drawn_title_convention_with_no_title_is_reported():
    objects = [box(1, left=0, top=-40, name="A", type="Class")]
    report = lint_diagram(verified(objects), title_convention="drawn")
    assert any(f.rule == "missing-title" for f in report.findings)


def test_the_frame_header_convention_needs_no_drawn_title():
    """Most diagrams correctly use EA's frame header. Firing unconditionally
    would flag the majority of a real corpus for doing the right thing."""
    objects = [box(1, left=0, top=-40, name="A", type="Class")]
    report = lint_diagram(verified(objects), title_convention="frame-header")
    assert not [f for f in report.findings if f.rule == "missing-title"]


def test_no_stated_convention_means_no_title_rule():
    objects = [box(1, left=0, top=-40, name="A", type="Class")]
    report = lint_diagram(verified(objects))
    assert not [f for f in report.findings if f.rule == "missing-title"]


def test_a_text_element_satisfies_a_drawn_title():
    objects = [box(1, left=0, top=-40, name="A", type="Class"),
               box(2, left=0, top=-10, name="Landscape", type="Text")]
    report = lint_diagram(verified(objects), title_convention="drawn")
    assert not [f for f in report.findings if f.rule == "missing-title"]


# ---------------------------------------------------------------------------
# Connector labels, and the profile that makes them moot
# ---------------------------------------------------------------------------
def test_inconsistent_connector_labeling_is_reported():
    """PARTIAL labeling is the defect, not absent labeling.

    Rewritten after the first version fired on a real generated diagram whose
    six sequence flows are deliberately unnamed -- which is that notation's
    convention, not an error. A rule that reports a correct diagram every time
    is the rule that gets the linter switched off.
    """
    links = [
        {"connector_id": 5, "stored": True, "route": "Direct", "name": "uses"},
        {"connector_id": 6, "stored": True, "route": "Direct", "name": ""},
    ]
    report = lint_diagram(verified([box(1, left=0, top=-40)], links))
    finding = [f for f in report.findings
               if f.rule == "missing-connector-labels"]
    assert finding, [str(f) for f in report.findings]
    assert finding[0].subjects == (6,), "only the blank one is the oversight"


def test_uniformly_unlabeled_connectors_are_a_convention_not_a_defect():
    links = [{"connector_id": 5, "stored": True, "route": "Direct", "name": ""},
             {"connector_id": 6, "stored": True, "route": "Direct", "name": ""}]
    report = lint_diagram(verified([box(1, left=0, top=-40)], links))
    assert not [f for f in report.findings
                if f.rule == "missing-connector-labels"]
    assert report.metrics["connectors_unlabeled"] == 2, (
        "the count is still reported; only the finding is withheld"
    )


def test_an_executive_profile_does_not_report_missing_connector_labels():
    """The item's own example, and the reason profile-awareness is a
    correctness requirement: a linter that rejects every executive view gets
    switched off, and then it protects nothing."""
    links = [{"connector_id": 5, "stored": True, "route": "Direct",
              "name": "uses"},
             {"connector_id": 6, "stored": True, "route": "Direct", "name": ""}]
    report = lint_diagram(verified([box(1, left=0, top=-40)], links),
                          profile={"hide_connector_labels": True})
    assert not [f for f in report.findings
                if f.rule == "missing-connector-labels"]
    assert "missing-connector-labels" in report.suppressed


def test_an_unstored_link_has_no_label_state_to_judge():
    links = [{"connector_id": 5, "stored": False, "name": ""}]
    report = lint_diagram(verified([box(1, left=0, top=-40)], links))
    assert not [f for f in report.findings
                if f.rule == "missing-connector-labels"]


# ---------------------------------------------------------------------------
# Collapsed connectors: the one rule a profile turns ON
# ---------------------------------------------------------------------------
def test_collapsing_without_saying_so_is_an_error():
    links = [{"connector_id": 5, "stored": True, "route": "Direct",
              "name": "uses"}]
    report = lint_diagram(verified([box(1, left=0, top=-40, name="A")], links),
                          profile={"collapses_parallel": True})
    assert any(f.rule == "collapsed-connectors-unannotated"
               for f in report.findings)
    assert not report.clean


def test_an_annotation_satisfies_the_collapse_rule():
    objects = [box(1, left=0, top=-40, name="A", type="Class"),
               box(2, left=0, top=-300, type="Note",
                   name="Parallel relationships collapsed for readability")]
    links = [{"connector_id": 5, "stored": True, "name": "uses"}]
    report = lint_diagram(verified(objects, links),
                          profile={"collapses_parallel": True})
    assert not [f for f in report.findings
                if f.rule == "collapsed-connectors-unannotated"]


def test_the_collapse_rule_does_not_exist_without_a_collapsing_profile():
    """The only rule here a profile turns ON. Without one it must be silent,
    or every ordinary diagram is told to annotate something it did not do."""
    links = [{"connector_id": 5, "stored": True, "name": "uses"}]
    report = lint_diagram(verified([box(1, left=0, top=-40, name="A")], links))
    assert not [f for f in report.findings
                if f.rule == "collapsed-connectors-unannotated"]


# ---------------------------------------------------------------------------
# Label fit, measured from EA's own render
# ---------------------------------------------------------------------------
def _svg(boxes_and_text):
    """Minimal EA-shaped SVG. The attribute ORDER matters to the parser, and
    it is the order EA emits - checked against a real captured render."""
    parts = ['<svg xmlns="http://www.w3.org/2000/svg">']
    for (x, y, w, h), runs in boxes_and_text:
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" />')
        for tx, ty, tl, text in runs:
            parts.append(
                f'<text x="{tx}" y="{ty}" textLength="{tl}" '
                f'style="font-family:Calibri; font-size:10px;">{text}</text>'
            )
    parts.append("</svg>")
    return "".join(parts)


def test_a_label_that_leaves_its_box_is_an_error():
    objects = [box(1, left=35, top=-40, width=100, height=70, name="Overlong")]
    svg = _svg([((35, 40, 100, 70), [(20, 72, 130, "Overlong")])])
    report = lint_diagram({**verified(objects), "svg_text": svg})
    clipped = [f for f in report.findings if f.rule == "label-clipped"]
    assert clipped, [str(f) for f in report.findings]
    assert clipped[0].severity == "error"
    assert clipped[0].subjects == (1,), "the finding must name its element"


def test_a_label_hard_against_the_border_is_a_warning():
    """Calibrated, not invented: on a real capability map this margin
    separates exactly the two names that look wrong from the next box."""
    objects = [box(1, left=35, top=-40, width=100, height=70, name="Snug")]
    svg = _svg([((35, 40, 100, 70), [(40, 72, 90, "Snug")])])
    report = lint_diagram({**verified(objects), "svg_text": svg})
    cramped = [f for f in report.findings if f.rule == "label-cramped"]
    assert cramped and cramped[0].severity == "warning"
    assert report.clean, "cramped is legible; it must not block"


def test_a_comfortable_label_is_not_reported():
    objects = [box(1, left=35, top=-40, width=100, height=70, name="Fits")]
    svg = _svg([((35, 40, 100, 70), [(56, 72, 58, "Fits")])])
    report = lint_diagram({**verified(objects), "svg_text": svg})
    assert not [f for f in report.findings if f.rule.startswith("label-")]
    assert report.metrics["labels_measured"] == 1


def test_the_label_rule_says_when_it_could_not_run():
    """A check that quietly does nothing is worse than one that is absent."""
    objects = [box(1, left=35, top=-40, name="A")]
    report = lint_diagram(verified(objects))
    assert report.metrics["labels_measured"] == 0
    assert any("label-fit" in note for note in report.not_run)


def test_label_fit_is_measured_on_a_real_render():
    """The whole rule, against markup EA actually emitted.

    `Payments Hub` in a 100-wide box: EA measured the string at 58px and
    started it at x=56 in a box spanning 35..135, so it clears both borders by
    21px. Nothing should be reported, and `labels_measured` proves the rule
    ran rather than skipping the boxes silently.
    """
    real = _load_real("FieldProbe")
    assert real.get("svg_text"), "the fixture lost its render"
    report = lint_diagram(real)
    assert report.metrics["labels_measured"] >= 2
    assert not [f for f in report.findings if f.rule.startswith("label-")]


def test_a_run_without_textlength_is_ignored_rather_than_guessed():
    """EA supplies `textLength` on every run it draws. If one ever lacks it,
    skipping is right - estimating the width would turn an exact rule into a
    silent approximation, which is the thing this rule was built to avoid."""
    svg = ('<svg><rect x="0" y="0" width="100" height="70" />'
           '<text x="10" y="30">No length here</text></svg>')
    assert lint._svg_text_runs(svg) == []
