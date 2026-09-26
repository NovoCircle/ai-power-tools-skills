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

import re
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
    "check_crossings",
    "check_color_is_explained",
    "check_title_present",
    "check_connector_labels",
    "check_collapsed_connectors_annotated",
    "check_labels_fit",
    "is_stalled",
    "LABEL_MARGIN",
    "LABEL_MARGIN",
]

# A size difference under this many units is not an inconsistency - EA nudges
# geometry, and flagging a 2-unit delta would make the rule noise.
SIZE_TOLERANCE = 4

# Likewise for spacing, judged on the SPREAD rather than on exact equality.
PITCH_TOLERANCE = 8

# How close a label may come to its element's border before it reads as
# touching it. Calibrated against a real generated diagram rather than chosen:
# on a capability map it separates exactly the two names that look wrong
# (margins of 5 and 6) from the next-tightest box at 10, so the boundary sits
# anywhere in (6, 10) and 8 is the midpoint.
LABEL_MARGIN = 8

# Element kinds that can carry a grouping's name, and that can serve as a drawn
# title. Plain EA type names, available in every notation - this is not a
# metamodel branch, it is the vocabulary EA itself uses for `Object_Type`.
_CONTAINER_TYPES = frozenset({"boundary", "package", "grouping"})
_TITLE_TYPES = frozenset({"text", "note", "boundary"})

# Words that count as annotating a deliberate simplification.
_ANNOTATION_WORDS = ("collaps", "combined", "merged", "aggregated",
                     "simplified", "summar")

_MIN_BOX = 20.0          # smaller SVG rects are decoration, not elements
# How far the drawn box may exceed the stored rect before it is worth saying.
# EA's border and shadow account for a few pixels either way; a name that does
# not fit adds tens.
_RENDER_SLACK = 6.0
_BASELINE_SLACK = 6.0    # a baseline may sit just below the box and still fit

_SVG_TEXT_RE = re.compile(
    r'<text\s+x="(?P<x>[-\d.]+)"\s+y="(?P<y>[-\d.]+)"'
    r'(?:\s+textLength="(?P<tl>[-\d.]+)")?'
    r'(?P<attrs>[^>]*)>(?P<body>.*?)</text>',
    re.DOTALL,
)
_SVG_RECT_RE = re.compile(
    r'<rect\s+x="(?P<x>[-\d.]+)"\s+y="(?P<y>[-\d.]+)"\s+'
    r'width="(?P<w>[-\d.]+)"\s+height="(?P<h>[-\d.]+)"'
)
_ENTITIES = (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
             ("&quot;", '"'), ("&apos;", "'"))


def _kind_of(obj: Mapping[str, Any]) -> str:
    return (obj.get("type") or "").strip().lower()


def _looks_like_annotation(text: Optional[str]) -> bool:
    lowered = (text or "").lower()
    return any(word in lowered for word in _ANNOTATION_WORDS)


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
    # Rules that could not run, and why. Distinct from `suppressed`, which is a
    # deliberate choice: this is a rule that WANTED to run and lacked its
    # input. A clean report with entries here has checked less than it looks.
    not_run: list[str] = field(default_factory=list)

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
# Rules that read identity as well as geometry
# ---------------------------------------------------------------------------
def _segments_cross(p1, p2, p3, p4) -> bool:
    """Proper segment intersection; shared endpoints do not count.

    Connectors meeting at a shared element are not a crossing, and counting
    them would make every hub-and-spoke diagram look terrible.
    """
    def orient(a, b, c):
        val = (b[1] - a[1]) * (c[0] - b[0]) - (b[0] - a[0]) * (c[1] - b[1])
        return 0 if abs(val) < 1e-9 else (1 if val > 0 else 2)

    if p1 in (p3, p4) or p2 in (p3, p4):
        return False
    o1, o2, o3, o4 = (orient(p1, p2, p3), orient(p1, p2, p4),
                      orient(p3, p4, p1), orient(p3, p4, p2))
    return o1 != o2 and o3 != o4


def check_crossings(objects: Sequence[Mapping[str, Any]],
                    links: Sequence[Mapping[str, Any]],
                    report: LintReport) -> int:
    """Count connector crossings, straight line center to center.

    An approximation, and honest about it: it ignores the actual routed path,
    so an orthogonal diagram's real crossing count differs. It is still the
    right metric for COMPARISON - between two versions of one diagram, fewer is
    better - which is what a correction loop needs.

    Reported as `info`, because this rule cannot tell a REMOVABLE crossing from
    a necessary one. Some graphs are not planar and no reordering helps.

    `crossings_measured_over` is recorded beside the count on purpose. Zero
    crossings over zero measurable links is not a result, and for a long time
    this rule reported exactly that - the endpoints it needs were absent from
    the payload, so every diagram scored zero. A count without its denominator
    is how that stayed invisible.
    """
    by_id = {int(o["element_id"]): o for o in objects}
    segments = []
    for link in links:
        src, tgt = link.get("source_element_id"), link.get("target_element_id")
        if src in by_id and tgt in by_id:
            segments.append((_center(by_id[src]), _center(by_id[tgt])))

    crossings = 0
    for i, (p1, p2) in enumerate(segments):
        for p3, p4 in segments[i + 1:]:
            if _segments_cross(p1, p2, p3, p4):
                crossings += 1

    report.metrics["crossings"] = crossings
    report.metrics["crossings_are_approximate"] = True
    report.metrics["crossings_measured_over"] = len(segments)
    if links and not segments:
        report.not_run.append(
            "crossings: no link carried both endpoint element ids, so nothing "
            "was measured"
        )
    if crossings:
        report.add(Finding(
            rule="crossings", severity="info",
            message=(f"{crossings} connector crossing(s), measured center to "
                     f"center over {len(segments)} link(s); some may be "
                     f"unavoidable"),
            correction="reorder elements within their row or container where "
                       "the crossings are incidental rather than structural",
        ))
    return crossings


def check_color_is_explained(objects: Sequence[Mapping[str, Any]],
                             report: LintReport) -> None:
    """Color that varies must be decodable.

    A correctness rule, not a style preference: color carrying information the
    reader cannot decode is a diagram that misleads.

    Two things count as explaining it, because both genuinely do - a legend,
    and a named container grouping the elements that share a color. A banded
    diagram whose bands are named needs no separate legend; the band names ARE
    the key, and demanding one anyway would be noise.

    A warning rather than an error: several fills are not always an encoding.
    """
    fills = {o.get("fill") for o in objects if o.get("fill")}
    report.metrics["distinct_fills"] = len(fills)
    if len(fills) < 2:
        # One color carries no information, so there is nothing to decode.
        return

    explained = any(
        "legend" in (o.get("name") or "").lower()
        or (_kind_of(o) in _CONTAINER_TYPES and (o.get("name") or "").strip())
        for o in objects
    )
    if explained:
        return

    report.add(Finding(
        rule="unexplained-color", severity="warning",
        message=(f"{len(fills)} fill colors are in use and nothing labels "
                 f"what they mean"),
        correction="add a legend, or name the containers that group each "
                   "color -- a banded diagram's band names are its key",
    ))


def check_title_present(objects: Sequence[Mapping[str, Any]],
                        title_convention: Optional[str],
                        report: LintReport) -> None:
    """Only fires when the convention calls for a DRAWN title.

    Most diagrams correctly use the frame header instead and some have no title
    at all, so firing unconditionally would flag the majority of a real corpus
    for doing the right thing. `title_convention` is the caller's to supply: it
    is a convention, not something the geometry knows.
    """
    if (title_convention or "").strip().lower() != "drawn":
        return
    if not any(_kind_of(o) in _TITLE_TYPES for o in objects):
        report.add(Finding(
            rule="missing-title", severity="warning",
            message="this diagram's convention draws a title block; none found",
            correction="add a Text element as a title block",
        ))


def check_connector_labels(links: Sequence[Mapping[str, Any]],
                           report: LintReport) -> None:
    """A stored connector with no name leaves the relationship to be inferred.

    Suppressed under a profile that hides connector labels - see
    `SUPPRESSED_BY`. That suppression is why this rule can exist at all: some
    views hide these deliberately, and a rule that fired anyway would be the
    one that gets the whole linter switched off.

    Only STORED links are judged. EA draws a relationship between two placed
    elements whether or not a presentation row exists, and a line with no row
    has no label state to read.
    """
    stored = [link for link in links if link.get("stored")]
    unlabeled = [link["connector_id"] for link in stored
                 if not (link.get("name") or "").strip()]
    labeled = [link["connector_id"] for link in stored
               if (link.get("name") or "").strip()]
    report.metrics["connectors_unlabeled"] = len(unlabeled)

    # INCONSISTENT labeling is the defect. Unlabeled connectors are not:
    # several notations leave their ordinary flows unnamed as a convention, and
    # a rule that fired on all of them would report a correct diagram as broken
    # every time -- which is how a linter gets switched off.
    #
    # Measured on a real generated diagram whose six sequence flows are
    # deliberately unnamed: the first version of this rule reported all six.
    # Some labeled and some not is the case worth a word, because then the
    # blank ones read as omissions rather than as convention.
    if unlabeled and labeled:
        report.add(Finding(
            rule="missing-connector-labels", severity="warning",
            message=(f"{len(labeled)} connector(s) are labeled and "
                     f"{len(unlabeled)} are not, so the blank ones read as "
                     f"oversights rather than as a convention"),
            subjects=tuple(unlabeled),
            correction="label these too, or remove the labels from the others "
                       "so the diagram is consistent",
        ))


def check_collapsed_connectors_annotated(
        objects: Sequence[Mapping[str, Any]],
        links: Sequence[Mapping[str, Any]],
        profile: Optional[Mapping[str, Any]],
        report: LintReport) -> None:
    """Exists ONLY under a profile that collapses parallel connectors.

    Collapsing several relationships into one line is a real simplification and
    a real loss: the reader sees one line with no way to know it stands for
    four. That is fine when it is stated and misleading when it is not, so
    under a collapsing profile the diagram has to carry something saying so.

    The only rule here that a profile turns ON rather than off.
    """
    if not (profile or {}).get("collapses_parallel"):
        return
    annotated = (any(_looks_like_annotation(o.get("name")) for o in objects)
                 or any(_looks_like_annotation(k.get("name")) for k in links))
    report.metrics["collapse_annotated"] = bool(annotated)
    if not annotated:
        report.add(Finding(
            rule="collapsed-connectors-unannotated", severity="error",
            message=("this view collapses parallel connectors and nothing on "
                     "the diagram says so -- one line standing for several "
                     "relationships reads as one relationship"),
            correction="add a note or legend stating that parallel "
                       "relationships have been collapsed",
        ))


# ---------------------------------------------------------------------------
# Label fit, measured from the render
# ---------------------------------------------------------------------------
def _svg_text_runs(svg: str) -> list[dict]:
    """Every rendered line, with the width EA itself measured for it."""
    out = []
    for m in _SVG_TEXT_RE.finditer(svg):
        length = m.group("tl")
        if length is None:
            continue
        body = re.sub(r"<[^>]+>", "", m.group("body"))
        for entity, char in _ENTITIES:
            body = body.replace(entity, char)
        out.append({
            "x": float(m.group("x")), "y": float(m.group("y")),
            "length": float(length), "text": body.strip(),
        })
    return out


def _svg_boxes(svg: str) -> list[tuple]:
    return [(float(m.group("x")), float(m.group("y")),
             float(m.group("w")), float(m.group("h")))
            for m in _SVG_RECT_RE.finditer(svg)]


def _assign_runs_to_boxes(boxes, runs) -> dict:
    """Group runs by the box that owns them: `{box_index: [run, ...]}`.

    A run belongs to the box it sits horizontally within whose top is NEAREST
    above it. Nesting therefore resolves correctly - an inner box's top is
    lower than its parent's, so it wins for its own children.

    THE OBVIOUS IMPLEMENTATION IS WRONG, and was written first: collecting only
    the runs that fall INSIDE the box, with a few pixels of slack below. That
    filters out exactly the lines that overflow, so a name spilling out of the
    bottom of its box was measured over the lines that still fitted and
    reported as fitting. The rule looked like it worked and could not fire on
    its own headline case.

    So there is no vertical cutoff here at all. A run below its box is still
    that box's run, which is the whole point.
    """
    grouped: dict = {}
    for run in runs:
        run_left = run["x"]
        run_right = run["x"] + run["length"]
        best = None
        best_key = None
        for i, (x, y, w, h) in enumerate(boxes):
            # OVERLAP, not center containment. A run that overflows badly has
            # its center outside the box -- which is exactly the case this rule
            # exists to catch, so keying on the center made the rule blind to
            # its own headline defect and silently reassigned the run to the
            # diagram frame, where it fitted.
            overlap = min(run_right, x + w) - max(run_left, x)
            if overlap <= 0:
                continue
            if run["y"] < y - _BASELINE_SLACK:
                continue          # the run sits above this box entirely
            key = (y, overlap)
            if best is None or key > best_key:
                best, best_key = i, key
        if best is not None:
            grouped.setdefault(best, []).append(run)
    return grouped


def check_labels_fit(objects: Sequence[Mapping[str, Any]],
                     svg_text: Optional[str],
                     report: LintReport) -> None:
    """Names that overflow their box, or sit hard against its border.

    EXACT, not estimated. EA's SVG carries `textLength` on every text run - its
    own measured advance width in pixels - so this compares EA's numbers with
    EA's rects rather than guessing from a character count. Measured over 458
    text runs across eight probe diagrams: every run carried `textLength`, and
    EA never truncates, never adds an ellipsis and never shrinks the font. It
    emits the whole string and lets it overflow.

    Two findings, because they are two problems:

    * `label-clipped` (error) - the text leaves the box. It is cut off in an
      export, and it is wrong under every profile.
    * `label-cramped` (warning) - it fits with less than `LABEL_MARGIN` px to
      spare on its tightest side. Legible, but it reads as touching the border.

    `LABEL_MARGIN` is calibrated, not invented: on a real generated capability
    map it separates exactly the two names that look wrong (margins of 5 and 6)
    from the next-tightest box at 10. The boundary is anywhere in (6, 10).

    Everything is measured in the SVG's own coordinate space, so no EA-to-SVG
    transform is needed. Findings are attributed back to an element by matching
    the rendered text against the object's name, which is why this rule needs
    `name` on the objects.

    Requires `include_svg=True`. Without the markup the rule cannot run and
    says so on `report.not_run`, rather than passing silently - a check that
    quietly does nothing is worse than one that is absent.
    """
    if not svg_text:
        report.metrics["labels_measured"] = 0
        report.not_run.append(
            "label-fit: no svg_text in the payload; call verify_diagram with "
            "include_svg=True"
        )
        return

    runs = _svg_text_runs(svg_text)
    boxes = [b for b in _svg_boxes(svg_text)
             if b[2] >= _MIN_BOX and b[3] >= _MIN_BOX]
    by_name: dict[str, Any] = {}
    _stored_width: dict[Any, int] = {}
    for obj in objects:
        name = " ".join((obj.get("name") or "").split())
        if name and name not in by_name:
            by_name[name] = obj["element_id"]
        _stored_width[obj["element_id"]] = _width(obj)

    grouped = _assign_runs_to_boxes(boxes, runs)
    measured = 0
    unmatched = 0
    for index, box in enumerate(boxes):
        mine = grouped.get(index) or []
        if not mine:
            continue
        measured += 1
        x, y, w, h = box
        text_left = min(r["x"] for r in mine)
        text_right = max(r["x"] + r["length"] for r in mine)
        last_baseline = max(r["y"] for r in mine)
        label = " ".join(r["text"] for r in sorted(mine, key=lambda r: r["y"]))
        label = " ".join(label.split())

        # NO MATCH, NO FINDING. Only a box whose text is exactly one known
        # element's name is judged.
        #
        # EA draws MDG-stereotyped elements with a shape script, which emits
        # paths rather than a `<rect>`. On such a diagram the only rects are
        # the drawn containers, so every element's text falls to the band that
        # encloses it and the "label" becomes every name in the band
        # concatenated -- which then reports a spectacular overflow against a
        # box it does not belong to. Measured on a real generated diagram: one
        # band reported its label as five element names and two connector
        # labels run together.
        #
        # Skipping is the right answer rather than a cleverer attribution.
        # This rule is a quality warning, and a quality warning that fires
        # wrongly on a whole notation is how the linter gets switched off. A
        # missed cramped label costs far less than that.
        if label not in by_name:
            unmatched += 1
            continue
        subjects = (by_name[label],)

        # The matched box must be able to BE this element's outline. A shape
        # script emits several rects per element -- an icon box, a compartment
        # divider -- and judging a name against one of those reports an
        # overflow against a rectangle the name was never drawn inside.
        # Measured: an ArchiMate element 100 units wide reported its name as
        # overflowing by 37px, against a sub-rect narrower than the element.
        # EA only ever GROWS a drawn box, so anything narrower than the stored
        # width is not the outline.
        stored_w = _stored_width.get(subjects[0])
        if stored_w and w < stored_w - _RENDER_SLACK:
            unmatched += 1
            continue

        # EA GROWS THE DRAWN BOX rather than clipping a name it cannot break.
        # Measured: a 30-character unbreakable name in a 100-wide element
        # renders 128px wide, a 49-character one renders 188px, while
        # `verify_diagram` keeps reporting the stored width of 100.
        #
        # That makes this the rule that matters, and it is not about text at
        # all: the diagram does not look like its own geometry. Every other
        # rule here reads the stored rects, so a box that draws 88px wider than
        # it measures can sit on top of its neighbour while the overlap rule
        # sees a comfortable gap.
        if subjects:
            stored = _stored_width.get(subjects[0])
            if stored and w - stored > _RENDER_SLACK:
                report.add(Finding(
                    rule="render-exceeds-rect", severity="error",
                    message=(f"{label!r} does not fit, so EA draws this "
                             f"element {int(w)}px wide while its geometry says "
                             f"{int(stored)}px -- the render is "
                             f"{int(w - stored)}px wider than anything else "
                             f"here can see"),
                    subjects=subjects,
                    correction="widen this element to at least "
                               f"{int(w)}px, or shorten the name so it fits "
                               "the width you chose",
                ))
                continue

        overflow_x = max(0.0, x - text_left) + max(0.0, text_right - (x + w))
        overflow_y = max(0.0, last_baseline - (y + h))
        if overflow_x > 0 or overflow_y > 0:
            report.add(Finding(
                rule="label-clipped", severity="error",
                message=(f"{label!r} overflows its element by "
                         f"{int(max(overflow_x, overflow_y))}px and is cut off "
                         f"in an export"),
                subjects=subjects,
                correction="widen or heighten this element, or shorten the name",
            ))
            continue
        side_margin = min(text_left - x, (x + w) - text_right)
        if side_margin < LABEL_MARGIN:
            report.add(Finding(
                rule="label-cramped", severity="warning",
                message=(f"{label!r} comes within {int(side_margin)}px of its "
                         f"element border and reads as touching it"),
                subjects=subjects,
                correction=f"widen this element so the label clears its border "
                           f"by at least {LABEL_MARGIN}px",
            ))
    report.metrics["labels_measured"] = measured
    report.metrics["labels_unmatched"] = unmatched
    if unmatched and not measured:
        report.not_run.append(
            f"label-fit: none of {unmatched} text block(s) matched a single "
            f"element name, so nothing was judged -- this notation is probably "
            f"drawn with shape scripts, which emit paths rather than rects"
        )


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
    title_convention: Optional[str] = None,
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
    check_crossings(objects, links, report)
    check_color_is_explained(objects, report)
    check_title_present(objects, title_convention, report)
    check_collapsed_connectors_annotated(objects, links, profile, report)
    check_labels_fit(objects, verified.get("svg_text"), report)
    if "missing-connector-labels" not in suppressed:
        check_connector_labels(links, report)

    report.metrics["errors"] = len(report.errors)
    report.metrics["findings"] = len(report.findings)
    return report
