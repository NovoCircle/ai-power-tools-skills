#!/usr/bin/env python3
"""Check a generated diagram before anyone is shown it.

This is the check half of the generate-check-correct loop. It consumes exactly
what `verify_diagram` returns and makes no repository calls of its own, so it
can run anywhere the verify payload can be carried.

LANGUAGE-NEUTRAL BY CONSTRUCTION
---------------------------------
Every rule reads geometry and presentation - rects, sizes, routes, fills - and
nothing reads the metamodel. No notation name, no technology id, no element
classification branches anything here. That is what lets one linter serve every
modeling language, including one nobody has written a binding for: "these boxes
overlap" and "these connectors cross needlessly" are not metamodel questions.

The module is held to the same bar as the layout engine, and a test enforces it
over identifiers AND string constants - including these docstrings. Naming a
language even in prose is how the first special case gets justified later.

The same property is why this module does not import `bindings`. A binding's
presentation profile is translated to a plain mapping by the CALLER and handed
in as `profile=`; see `PROFILE_KEYS`. A test asserts the import is absent,
because the boundary is the design.

WHAT A CLEAN REPORT MEANS
-------------------------
"No defect this linter knows how to measure." It is NOT a claim that the
diagram reads well. Known blind spots are listed in
`references/verification.md` and kept there deliberately, so that a clean
report is never quoted as more than it is.

EA COORDINATES
--------------
`top` and `bottom` are negative and `top > bottom`, so `height = top - bottom`.
`_normalize_rect` is the only function here that reasons about it; everything
else works in the conventional top-left-origin space it returns.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Optional, Sequence

__all__ = [
    "Finding",
    "LintReport",
    "PROFILE_KEYS",
    "SUPPRESSED_BY",
    "MAX_CORRECTION_PASSES",
    "SIZE_TOLERANCE",
    "PITCH_TOLERANCE",
    "lint_diagram",
    "check_no_overlaps",
    "check_within_canvas",
    "check_uniform_sizing",
    "check_pitch_consistency",
    "check_routing",
    "is_stalled",
]

# A size difference under this many units is not an inconsistency - EA nudges
# geometry, and flagging a 2-unit delta would make the rule noise.
SIZE_TOLERANCE = 4

# Likewise for spacing, judged on the SPREAD rather than on exact equality.
PITCH_TOLERANCE = 8

# How many correction passes the loop may take before it must stop and say so.
# A loop that keeps going until it is happy either terminates or lies; this one
# terminates. `is_stalled` is how a caller detects the other failure - passes
# that change nothing - without waiting for the budget to run out.
MAX_CORRECTION_PASSES = 3

# The presentation keys this linter understands. A caller builds this mapping
# from whatever it uses to describe a view; from a binding's profile it is:
#
#     profile = {**p.display_settings(), "collapses_parallel": p.collapses_parallel}
#
# Anything else in the mapping is ignored rather than rejected, because a
# profile vocabulary is allowed to grow without breaking the linter.
PROFILE_KEYS = (
    "hide_connector_labels",
    "hide_element_stereotypes",
    "hide_connector_stereotypes",
    "show_element_notes",
    "hide_attribute_types",
    "hide_operation_return_types",
    "hide_operation_brackets",
    "collapses_parallel",
)

# Rules a profile deliberately makes moot. This table is the whole of
# profile-awareness, and it is a table rather than a branch so that it can be
# read, tested exhaustively, and extended without touching a rule.
#
# The reason this is a correctness requirement and not a nicety: a linter that
# rejects every executive view gets switched off, and a switched-off linter
# protects nothing.
SUPPRESSED_BY: dict[str, str] = {
    "missing-connector-labels": "hide_connector_labels",
}


@dataclass(frozen=True)
class Finding:
    """One thing wrong, stated so it can be acted on rather than just read."""

    rule: str
    severity: str            # "error" | "warning" | "info"
    message: str
    subjects: tuple = ()     # element ids / connector ids involved
    correction: str = ""     # what to do about it

    def __str__(self) -> str:
        where = f" {list(self.subjects)}" if self.subjects else ""
        return f"[{self.severity}] {self.rule}{where}: {self.message}"


@dataclass
class LintReport:
    findings: list[Finding] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    suppressed: list[str] = field(default_factory=list)

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "warning"]

    @property
    def clean(self) -> bool:
        """No ERRORS. Warnings and info are reported and do not block.

        Deliberately not "no findings at all": several warnings here fire on
        diagrams that are correct for their context, and a bar nobody can clear
        is a bar nobody uses.
        """
        return not self.errors

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)

    def signature(self) -> tuple:
        """What the report is, for comparing one pass against the next.

        Ignores message wording so that a rule whose message includes a
        coordinate does not look like a different finding each pass.
        """
        return tuple(sorted((f.rule, f.severity, tuple(f.subjects))
                            for f in self.findings))


def is_stalled(previous: Optional[LintReport], current: LintReport) -> bool:
    """True when a correction pass changed nothing the linter can see.

    The loop's other failure mode. Running the budget out on passes that each
    fix nothing wastes time and ends with the same honest-but-late answer, so a
    caller should stop at the first stall and report what is left.
    """
    if previous is None:
        return False
    return previous.signature() == current.signature()


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def _normalize_rect(obj: Mapping[str, Any]) -> tuple[int, int, int, int]:
    """`(x0, y0, x1, y1)` in a conventional top-left-origin space.

    EA's y axis increases downward and placement uses negative tops, so the
    numerically LARGER value is the visual top. Flipping once here means no
    other function has to remember the convention.
    """
    left, right = int(obj["left"]), int(obj["right"])
    top, bottom = int(obj["top"]), int(obj["bottom"])
    x0, x1 = min(left, right), max(left, right)
    y0, y1 = -max(top, bottom), -min(top, bottom)
    return x0, y0, x1, y1


def _overlap(a: Mapping[str, Any], b: Mapping[str, Any]) -> bool:
    ax0, ay0, ax1, ay1 = _normalize_rect(a)
    bx0, by0, bx1, by1 = _normalize_rect(b)
    # Touching edges are not an overlap: a band and its contents legitimately
    # share an edge. NOTE that this means no-overlap never implies whitespace,
    # so any rule about spacing must measure the spacing itself.
    return ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1


def _contains(outer: Mapping[str, Any], inner: Mapping[str, Any]) -> bool:
    ox0, oy0, ox1, oy1 = _normalize_rect(outer)
    ix0, iy0, ix1, iy1 = _normalize_rect(inner)
    return ox0 <= ix0 and oy0 <= iy0 and ox1 >= ix1 and oy1 >= iy1


def _center(obj: Mapping[str, Any]) -> tuple[float, float]:
    x0, y0, x1, y1 = _normalize_rect(obj)
    return (x0 + x1) / 2.0, (y0 + y1) / 2.0


def _width(obj: Mapping[str, Any]) -> int:
    """Width, from the rect rather than from a `width` key.

    `verify_diagram` supplies `width`, but a caller assembling a payload by
    hand may not, and the rect is always there. Deriving it removes a way for
    the two to disagree.
    """
    x0, _, x1, _ = _normalize_rect(obj)
    return x1 - x0


def _height(obj: Mapping[str, Any]) -> int:
    _, y0, _, y1 = _normalize_rect(obj)
    return y1 - y0


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------
def check_no_overlaps(objects: Sequence[Mapping[str, Any]],
                      report: LintReport) -> None:
    """Overlapping elements are the most visible failure a generator makes.

    Containment is exempt: nesting is how EA expresses composition, and a
    grammar that nests deliberately - a capability map, a domain map - must not
    be punished for doing its job.
    """
    overlapping = []
    for i, a in enumerate(objects):
        for b in objects[i + 1:]:
            if not _overlap(a, b):
                continue
            if _contains(a, b) or _contains(b, a):
                continue
            overlapping.append((a["element_id"], b["element_id"]))

    report.metrics["overlaps"] = len(overlapping)
    for pair in overlapping:
        report.add(Finding(
            rule="overlap", severity="error",
            message="two elements overlap without one containing the other",
            subjects=pair,
            correction="move one element, or widen the pitch for this row",
        ))


def check_within_canvas(objects: Sequence[Mapping[str, Any]],
                        canvas: Mapping[str, Any],
                        report: LintReport) -> None:
    """Placement outside the canvas renders, but exports clipped.

    A warning rather than an error: EA grows the canvas on some paths, so this
    is "look at it", not "this is broken".
    """
    cx, cy = int(canvas.get("cx") or 0), int(canvas.get("cy") or 0)
    if not cx or not cy:
        return
    outside = []
    for obj in objects:
        x0, y0, x1, y1 = _normalize_rect(obj)
        if x1 > cx or y1 > cy or x0 < 0 or y0 < 0:
            outside.append(obj["element_id"])
    report.metrics["outside_canvas"] = len(outside)
    if outside:
        report.add(Finding(
            rule="out-of-canvas", severity="warning",
            message=f"{len(outside)} element(s) fall outside the {cx}x{cy} canvas",
            subjects=tuple(outside),
            correction="grow the diagram's cx/cy, or tighten the layout",
        ))


def check_uniform_sizing(roles: Mapping[str, Sequence[Mapping[str, Any]]],
                         report: LintReport) -> None:
    """Elements playing the same role should be the same size.

    `roles` maps a role name to the objects in it. **The caller decides what a
    role is**, because that is a language question and this module does not
    answer language questions. Two elements can share a container and still be
    different roles - a small round event beside a wide rectangular step - and
    requiring those to be one size would be requiring a 110x60 circle.
    """
    inconsistent = []
    for role, members in (roles or {}).items():
        if len(members) < 2:
            continue
        widths = {_width(o) for o in members}
        heights = {_height(o) for o in members}
        if (max(widths) - min(widths) > SIZE_TOLERANCE
                or max(heights) - min(heights) > SIZE_TOLERANCE):
            inconsistent.append(role)
            report.add(Finding(
                rule="uniform-sizing", severity="error",
                message=(f"elements in role {role!r} vary in size "
                         f"(widths {sorted(widths)}, heights {sorted(heights)})"),
                subjects=tuple(o["element_id"] for o in members),
                correction=f"give every {role} the same width and height",
            ))
    report.metrics["roles_with_inconsistent_sizing"] = len(inconsistent)


def check_pitch_consistency(rows: Iterable[Sequence[Mapping[str, Any]]],
                            report: LintReport) -> None:
    """Spacing between neighbors in a row should be even.

    Judged on the SPREAD, against `PITCH_TOLERANCE`, rather than on exact
    equality - EA nudges geometry and exact equality would be noise.

    WHAT IS MEASURED DEPENDS ON WHETHER THE ROW IS UNIFORMLY SIZED
    ---------------------------------------------------------------
    For a row of equally sized elements, the edge-to-edge GAP is measured.

    For a row whose elements differ in size, the CENTER-TO-CENTER pitch is
    measured instead. That is not a loosening: a flow that puts a 30-wide event
    next to a 110-wide activity has a rhythm the reader perceives as the even
    spacing of centers, and both the edge gaps and the leading edges necessarily
    vary around it. The two measures are identical for equal sizes.

    A MIXED-SIZE ROW ALSO GETS A FLOOR ON THE GAP ITSELF
    -----------------------------------------------------
    Even center pitch says nothing about whether the boxes touch. Widths
    alternating `a, b, a, b` with `a + b = 2 * pitch` drive EVERY edge gap to
    zero while the center spread stays at zero - a row with no whitespace
    anywhere, reported clean. Leaning on `check_no_overlaps` to bound that does
    not work, because touching is exempt from the overlap rule by design.

    A wrapped row is TWO rows and the caller passes it as two. Compensating
    here would paper over that and lose the single mis-spaced element this rule
    exists to catch.
    """
    worst = 0
    for row in rows or []:
        ordered = sorted(row, key=lambda o: _normalize_rect(o)[0])
        if len(ordered) < 3:
            continue
        widths = {_width(o) for o in ordered}
        uniform = max(widths) - min(widths) <= SIZE_TOLERANCE
        gaps = [_normalize_rect(b)[0] - _normalize_rect(a)[2]
                for a, b in zip(ordered, ordered[1:])]
        if uniform:
            measure, spacings = "gaps", gaps
        else:
            measure = "center pitches"
            spacings = [int(_center(b)[0] - _center(a)[0])
                        for a, b in zip(ordered, ordered[1:])]
            if gaps and min(gaps) <= 0:
                report.add(Finding(
                    rule="pitch", severity="error",
                    message=(f"elements in a row touch or overlap their "
                             f"neighbors (gaps {gaps}); even center spacing "
                             f"does not make a row with no whitespace readable"),
                    subjects=tuple(o["element_id"] for o in ordered),
                    correction="increase the slot pitch for this row",
                ))
        spread = max(spacings) - min(spacings) if spacings else 0
        worst = max(worst, spread)
        if spread > PITCH_TOLERANCE:
            report.add(Finding(
                rule="pitch", severity="warning",
                message=f"uneven spacing within a row ({measure} {spacings})",
                subjects=tuple(o["element_id"] for o in ordered),
                correction="space elements in a row evenly",
            ))
    report.metrics["worst_pitch_spread"] = worst


def check_routing(links: Sequence[Mapping[str, Any]],
                  expected_route: Optional[str],
                  report: LintReport) -> None:
    """Connectors should use the route the notation calls for, deliberately.

    A link with NO route at all is the interesting case: it means nothing was
    chosen, which is how a diagram ends up with EA's defaults instead of a
    decision.
    """
    stored = [link for link in links if link.get("stored")]
    report.metrics["links_stored"] = len(stored)
    report.metrics["links_unstyled"] = sum(1 for link in stored
                                           if not link.get("route"))

    unrouted = [link["connector_id"] for link in stored if not link.get("route")]
    if unrouted:
        report.add(Finding(
            rule="routing-unset", severity="warning",
            message=f"{len(unrouted)} connector(s) have no route set",
            subjects=tuple(unrouted),
            correction="set an explicit route so the diagram does not depend "
                       "on EA's default",
        ))

    if expected_route:
        wanted = expected_route.strip().lower()
        wrong = [link["connector_id"] for link in stored
                 if (link.get("route") or "").lower() != wanted]
        if wrong:
            report.add(Finding(
                rule="routing-mismatch", severity="warning",
                message=(f"{len(wrong)} connector(s) do not use the expected "
                         f"{expected_route} routing"),
                subjects=tuple(wrong),
                correction=f"set route={expected_route} on these connectors",
            ))


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def _suppressed_rules(profile: Optional[Mapping[str, Any]]) -> set[str]:
    """Rule ids this profile deliberately makes moot."""
    if not profile:
        return set()
    return {rule for rule, key in SUPPRESSED_BY.items() if profile.get(key)}


def lint_diagram(
    verified: Mapping[str, Any],
    profile: Optional[Mapping[str, Any]] = None,
    roles: Optional[Mapping[str, Sequence[Mapping[str, Any]]]] = None,
    rows: Optional[Iterable[Sequence[Mapping[str, Any]]]] = None,
    expected_route: Optional[str] = None,
) -> LintReport:
    """Lint one `verify_diagram` result.

    `profile` is a plain mapping of presentation settings - see `PROFILE_KEYS`.
    It suppresses the rules a view deliberately makes moot, and the suppressed
    rule ids come back on the report so that a suppression is visible rather
    than silent.

    `roles` and `rows` are the caller's grouping: which elements play the same
    role, which sit in the same row. Those are composition facts the generator
    knows and geometry alone does not, and guessing them here would invent the
    metamodel this module deliberately does not have. Omit them and the rules
    that need them simply do not run.
    """
    report = LintReport()
    objects = list(verified.get("objects") or [])
    links = list(verified.get("links") or [])

    report.metrics["objects"] = len(objects)
    report.metrics["links"] = len(links)
    suppressed = _suppressed_rules(profile)
    report.suppressed = sorted(suppressed)

    check_no_overlaps(objects, report)
    check_within_canvas(objects, verified.get("canvas") or {}, report)
    check_uniform_sizing(roles or {}, report)
    check_pitch_consistency(rows or [], report)
    check_routing(links, expected_route, report)

    report.metrics["errors"] = len(report.errors)
    report.metrics["findings"] = len(report.findings)
    return report
