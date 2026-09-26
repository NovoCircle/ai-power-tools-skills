#!/usr/bin/env python3
"""Tests for the pure-arithmetic layout engine.

Run from the repository root:

    python -m pytest ea-diagram-composition/tools/test_compose.py -q

Nothing here touches a repository, a COM object or the filesystem. If any test
in this file needs Sparx EA to pass, the layer boundary has been broken.

Two conventions worth reading before editing:

* `assert_no_overlaps` is applied to comparable sets - all items together, all
  containers together - never to items and containers mixed. Items are nested
  inside their containers by design, so a mixed set is supposed to overlap.
* Rect intersection is tested in EA's flipped-y convention, where `top` is
  greater than `bottom`. `test_overlap_helper_*` pins that first, because every
  other no-overlap assertion in the file leans on it.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from compose import (  # noqa: E402
    DEFAULT_SPEC,
    LayoutError,
    bounding_box,
    compose_lanes,
    compose_layered_bands,
    compose_nested_grid,
    rect,
    rect_height,
    rect_width,
    rects_overlap,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def assert_no_overlaps(rects, label=""):
    """Assert that no two rects in `rects` share positive area."""
    rects = list(rects)
    for i, a in enumerate(rects):
        for b in rects[i + 1:]:
            assert not rects_overlap(a, b), (
                f"{label}: overlap between "
                f"{a.get('id', a.get('name'))} {_span(a)} and "
                f"{b.get('id', b.get('name'))} {_span(b)}"
            )


def assert_contains(outer, inner, label=""):
    """Assert `inner` sits wholly inside `outer`, in EA's convention."""
    assert inner["left"] >= outer["left"], f"{label}: left escapes {_span(outer)}"
    assert inner["right"] <= outer["right"], f"{label}: right escapes {_span(outer)}"
    # Visually lower means numerically smaller, so inner top must not be ABOVE
    # outer top, i.e. must not be greater.
    assert inner["top"] <= outer["top"], f"{label}: top escapes {_span(outer)}"
    assert inner["bottom"] >= outer["bottom"], f"{label}: bottom escapes {_span(outer)}"


def assert_valid_rect(r, label=""):
    """Every rect must be positive-area and obey EA's sign convention."""
    assert r["right"] > r["left"], f"{label}: non-positive width {_span(r)}"
    assert r["top"] > r["bottom"], f"{label}: non-positive height {_span(r)}"
    assert rect_width(r) > 0 and rect_height(r) > 0, f"{label}: zero size {_span(r)}"


def assert_result_sane(result, label=""):
    """The checks that must hold for any output of any grammar."""
    for c in result["containers"]:
        assert_valid_rect(c, f"{label} container {c['id']}")
        assert_valid_rect(c["label"], f"{label} label of {c['id']}")
        assert_contains(c, c["label"], f"{label} label of {c['id']}")
    for it in result["items"]:
        assert_valid_rect(it, f"{label} item {it['id']}")
    assert_no_overlaps(result["items"], f"{label} items")
    assert_no_overlaps(result["containers"], f"{label} containers")

    by_id = {c["id"]: c for c in result["containers"]}
    for it in result["items"]:
        assert_contains(by_id[it["container_id"]], it, f"{label} item {it['id']}")

    expected = bounding_box([*result["containers"], *result["items"]])
    assert result["bounds"] == expected, f"{label}: bounds disagree with contents"


def _span(r):
    return (
        f"(l={r['left']} t={r['top']} r={r['right']} b={r['bottom']} "
        f"{rect_width(r)}x{rect_height(r)})"
    )


def _items(*ids):
    return [{"id": i} for i in ids]


def _center_x2(r):
    """Twice the horizontal center, so integer rounding stays visible."""
    return r["left"] + r["right"]


def _center_y2(r):
    return r["top"] + r["bottom"]


# ===========================================================================
# 1. The overlap helper itself, and the coordinate convention it rests on
# ===========================================================================
def test_overlap_helper_detects_a_real_overlap():
    a = {"left": 0, "top": -50, "right": 100, "bottom": -110}
    b = {"left": 50, "top": -80, "right": 150, "bottom": -140}
    assert rects_overlap(a, b)
    assert rects_overlap(b, a)


def test_overlap_helper_is_written_for_eas_inverted_y():
    """A screen-coordinate intersection test calls this pair disjoint.

    Both rects occupy the same x range; a spans -50..-110 and b spans -60..-120,
    so they share 50 units of height. An implementation that assumed bottom is
    numerically greater than top would compare a['bottom'] <= b['top']
    (-110 <= -60, true) and wrongly report no overlap.
    """
    a = {"left": 0, "top": -50, "right": 100, "bottom": -110}
    b = {"left": 0, "top": -60, "right": 100, "bottom": -120}
    assert rects_overlap(a, b)


def test_overlap_helper_separates_disjoint_pairs():
    a = {"left": 0, "top": -50, "right": 100, "bottom": -110}
    right_of_a = {"left": 120, "top": -50, "right": 220, "bottom": -110}
    below_a = {"left": 0, "top": -150, "right": 100, "bottom": -210}
    assert not rects_overlap(a, right_of_a)
    assert not rects_overlap(a, below_a)
    assert not rects_overlap(below_a, a)


def test_abutting_rects_do_not_overlap():
    """Swimlanes that share an edge are correct geometry, not a collision."""
    a = {"left": 0, "top": -50, "right": 100, "bottom": -110}
    below = {"left": 0, "top": -110, "right": 100, "bottom": -170}
    beside = {"left": 100, "top": -50, "right": 200, "bottom": -110}
    assert not rects_overlap(a, below)
    assert not rects_overlap(a, beside)


def test_no_overlap_helper_would_fail_on_a_known_bad_set():
    """The helper has to be able to fail, or it proves nothing elsewhere."""
    bad = [
        {"id": "a", "left": 0, "top": -50, "right": 100, "bottom": -110},
        {"id": "b", "left": 50, "top": -80, "right": 150, "bottom": -140},
    ]
    with pytest.raises(AssertionError):
        assert_no_overlaps(bad, "deliberate")


def test_rect_matches_a_real_ea_placement():
    """left=50, top=-50, right=190, bottom=-110 is 140 wide and 60 tall."""
    r = rect(50, -50, 140, 60)
    assert r == {"left": 50, "top": -50, "right": 190, "bottom": -110}
    assert rect_width(r) == 140
    assert rect_height(r) == 60
    assert r["top"] > r["bottom"]


def test_rect_refuses_to_make_a_zero_size_box():
    with pytest.raises(LayoutError, match="width and height"):
        rect(0, 0, 140, 0)
    with pytest.raises(LayoutError, match="width and height"):
        rect(0, 0, -140, 60)


def test_bounding_box_takes_the_maximum_top():
    """The visual top of an EA diagram is the coordinate nearest zero."""
    rects = [rect(20, -20, 100, 40), rect(200, -300, 100, 40)]
    assert bounding_box(rects) == {
        "left": 20, "top": -20, "right": 300, "bottom": -340,
        "width": 280, "height": 320,
    }


def test_bounding_box_rejects_an_empty_set():
    with pytest.raises(LayoutError, match="at least one rect"):
        bounding_box([])


def test_moving_down_a_band_stack_makes_coordinates_more_negative():
    result = compose_layered_bands([
        {"name": "Top", "items": _items("a")},
        {"name": "Middle", "items": _items("b")},
        {"name": "Bottom", "items": _items("c")},
    ])
    tops = [c["top"] for c in result["containers"]]
    assert tops == sorted(tops, reverse=True), tops
    assert all(t < 0 for t in tops)
    for earlier, later in zip(result["containers"], result["containers"][1:]):
        assert later["top"] < earlier["bottom"], "bands must not interleave"
    assert_result_sane(result, "three bands")


# ===========================================================================
# 2. layered_bands
# ===========================================================================
def test_band_geometry_uses_the_declared_sizes():
    result = compose_layered_bands(
        [{"name": "Channels", "items": _items("a", "b", "c")}],
        {"origin_left": 20, "origin_top": -20, "item_width": 140,
         "item_height": 60, "item_gap_x": 20, "label_height": 28,
         "band_pad_x": 12, "band_pad_y": 12},
    )
    lefts = [it["left"] for it in result["items"]]
    assert lefts == [32, 192, 352]        # 20 + 12, stepping by 140 + 20
    assert all(it["top"] == -48 for it in result["items"])     # -20 - 28
    assert all(it["bottom"] == -108 for it in result["items"])
    band = result["containers"][0]
    assert rect_width(band) == 3 * 140 + 2 * 20 + 2 * 12
    assert rect_height(band) == 28 + 60 + 12
    assert_result_sane(result, "sized band")


def test_items_are_uniformly_sized_within_a_band_and_may_differ_between_bands():
    result = compose_layered_bands([
        {"name": "Channels", "items": _items("a", "b", "c")},
        {"name": "Applications", "items": _items("d", "e"),
         "item_width": 200, "item_height": 90},
    ])
    first = [it for it in result["items"] if it["band_index"] == 0]
    second = [it for it in result["items"] if it["band_index"] == 1]

    assert {(rect_width(i), rect_height(i)) for i in first} == {(140, 60)}
    assert {(rect_width(i), rect_height(i)) for i in second} == {(200, 90)}
    assert_result_sane(result, "mixed sizes")


def test_a_taller_band_pushes_the_next_band_further_down():
    """Band height follows contents, so the stack step is not a constant."""
    short = compose_layered_bands([
        {"name": "A", "items": _items("a")},
        {"name": "B", "items": _items("b")},
    ])
    tall = compose_layered_bands([
        {"name": "A", "items": _items("a"), "item_height": 200},
        {"name": "B", "items": _items("b")},
    ])
    assert tall["containers"][1]["top"] < short["containers"][1]["top"] - 100
    assert rect_height(tall["containers"][0]) == 28 + 200 + 12


def test_band_pitch_acts_as_a_floor_not_a_cap():
    """A band taller than band_pitch still gets its own height plus the gap."""
    loose = compose_layered_bands(
        [{"name": "A", "items": _items("a")}, {"name": "B", "items": _items("b")}],
        {"band_pitch": 400},
    )
    assert loose["containers"][1]["top"] == -20 - 400

    crowded = compose_layered_bands(
        [{"name": "A", "items": _items("a"), "item_height": 300},
         {"name": "B", "items": _items("b")}],
        {"band_pitch": 100},
    )
    step = crowded["containers"][0]["top"] - crowded["containers"][1]["top"]
    assert step == rect_height(crowded["containers"][0]) + DEFAULT_SPEC["band_gap"]
    assert_result_sane(crowded, "band_pitch floor")


def test_a_wide_band_wraps_instead_of_running_off_the_canvas():
    spec = {"wrap_width": 500}          # 140 wide, pitch 160 -> 3 per row
    result = compose_layered_bands(
        [{"name": "Capabilities", "items": _items(*"abcdefg")}], spec
    )
    rows = {}
    for it in result["items"]:
        rows.setdefault(it["row"], []).append(it)

    assert sorted(rows) == [0, 1, 2]
    assert [len(rows[r]) for r in sorted(rows)] == [3, 3, 1]
    for row_items in rows.values():
        assert len({i["top"] for i in row_items}) == 1, "a row shares one top"
        widest = max(i["right"] for i in row_items) - min(i["left"] for i in row_items)
        assert widest <= spec["wrap_width"]
    assert rows[1][0]["top"] < rows[0][0]["bottom"], "row 2 sits below row 1"
    assert rect_height(result["containers"][0]) == 28 + (2 * 80 + 60) + 12
    assert_result_sane(result, "wrapped band")


def test_wrapping_never_places_a_row_wider_than_the_wrap_width():
    for wrap in (140, 300, 460, 620, 900, 1600):
        result = compose_layered_bands(
            [{"name": "Wide", "items": _items(*[f"e{n}" for n in range(11)])}],
            {"wrap_width": wrap},
        )
        rows = {}
        for it in result["items"]:
            rows.setdefault(it["row"], []).append(it)
        for r, row_items in rows.items():
            span = max(i["right"] for i in row_items) - min(i["left"] for i in row_items)
            assert span <= wrap, f"wrap_width={wrap}, row {r} spans {span}"
        assert_result_sane(result, f"wrap_width={wrap}")


def test_left_alignment_is_the_default_and_centering_is_opt_in():
    bands = [
        {"name": "Wide", "items": _items("a", "b", "c", "d")},
        {"name": "Narrow", "items": _items("e")},
    ]
    left = compose_layered_bands(bands)
    assert {c["left"] for c in left["containers"]} == {DEFAULT_SPEC["origin_left"]}

    centered = compose_layered_bands(bands, {"align": "center"})
    wide, narrow = centered["containers"]
    assert wide["left"] == DEFAULT_SPEC["origin_left"]
    assert _center_x2(wide) == _center_x2(narrow), "band centers must agree"
    assert narrow["left"] > wide["left"]
    assert_result_sane(centered, "centered bands")


def test_centering_also_centers_a_short_row_inside_its_band():
    result = compose_layered_bands(
        [{"name": "Capabilities", "items": _items("a", "b", "c", "d", "e")}],
        {"wrap_width": 500, "align": "center"},       # rows of 3 then 2
    )
    rows = {}
    for it in result["items"]:
        rows.setdefault(it["row"], []).append(it)
    full = rows[0]
    short = rows[1]
    full_center = full[0]["left"] + full[-1]["right"]
    short_center = short[0]["left"] + short[-1]["right"]
    assert abs(full_center - short_center) <= 1
    assert_result_sane(result, "centered rows")


def test_an_empty_band_keeps_its_label_row():
    result = compose_layered_bands([
        {"name": "Channels", "items": _items("a")},
        {"name": "Reserved", "items": []},
        {"name": "Platform", "items": _items("b")},
    ])
    empty = result["containers"][1]
    assert rect_height(empty) == 28 + 12, "label row plus its padding"
    assert rect_width(empty) >= 140, "an empty band is still a visible strip"
    assert rect_height(empty["label"]) == 28
    assert result["containers"][2]["top"] < empty["bottom"]
    assert [it["band_index"] for it in result["items"]] == [0, 2]
    assert_result_sane(result, "empty band")


def test_min_band_width_widens_a_sparse_band_without_touching_a_full_one():
    result = compose_layered_bands(
        [{"name": "Sparse", "items": _items("a")},
         {"name": "Full", "items": _items("b", "c", "d", "e", "f")}],
        {"min_band_width": 700},
    )
    sparse, full = result["containers"]
    assert rect_width(sparse) == 700
    assert rect_width(full) == 5 * 140 + 4 * 20 + 2 * 12       # content decides
    assert rect_width(full) > 700
    assert_result_sane(result, "min_band_width")


def test_a_band_with_no_items_key_is_treated_as_empty():
    result = compose_layered_bands([{"name": "Placeholder"}])
    assert result["items"] == []
    assert rect_height(result["containers"][0]) > 0
    assert_result_sane(result, "no items key")


def test_single_band_single_item():
    result = compose_layered_bands([{"name": "Only", "items": _items("solo")}])
    assert len(result["items"]) == 1
    assert len(result["containers"]) == 1
    item = result["items"][0]
    assert (rect_width(item), rect_height(item)) == (140, 60)
    assert item["row"] == 0 and item["column"] == 0
    assert_result_sane(result, "single item")


def test_band_item_records_carry_the_callers_id_and_name():
    result = compose_layered_bands([
        {"name": "Channels", "id": "band-channels",
         "items": [{"id": "elem-7", "name": "Online Banking"}]},
    ])
    item = result["items"][0]
    assert item["id"] == "elem-7"
    assert item["name"] == "Online Banking"
    assert item["container_id"] == "band-channels"
    assert item["band"] == "Channels"
    assert set(("left", "top", "right", "bottom")) <= set(item)
    assert result["containers"][0]["id"] == "band-channels"


def test_bands_survive_a_wide_sweep_of_shapes():
    shapes = [
        [1],
        [1, 1, 1],
        [0],
        [0, 3, 0],
        [12],
        [5, 1, 9, 2],
        [1] * 8,
        [30, 1],
    ]
    for shape in shapes:
        bands = []
        n = 0
        for b, count in enumerate(shape):
            ids = [f"e{n + k}" for k in range(count)]
            n += count
            bands.append({"name": f"Band {b}", "items": _items(*ids)})
        result = compose_layered_bands(bands, {"wrap_width": 620})
        assert len(result["items"]) == sum(shape)
        assert len(result["containers"]) == len(shape)
        assert_result_sane(result, f"shape {shape}")


# ===========================================================================
# 3. lanes
# ===========================================================================
def test_items_at_the_same_index_align_across_lanes_horizontally():
    """The invariant that makes a swimlane readable: a handoff lines up."""
    result = compose_lanes([
        {"name": "Customer", "items": _items("c1", "c2", "c3")},
        {"name": "Front Office", "items": _items("f1", "f2")},
        {"name": "Operations", "items": _items("o1", "o2", "o3")},
    ])
    by_index = {}
    for it in result["items"]:
        by_index.setdefault(it["index"], []).append(it)

    assert sorted(by_index) == [0, 1, 2]
    for idx, group in by_index.items():
        assert len({i["left"] for i in group}) == 1, f"index {idx} lefts disagree"
        assert len({i["right"] for i in group}) == 1, f"index {idx} rights disagree"
        assert len({i["slot_start"] for i in group}) == 1
        assert len({i["slot_extent"] for i in group}) == 1

    # and successive indexes really do advance along the flow axis
    lefts = [by_index[i][0]["left"] for i in sorted(by_index)]
    assert lefts == sorted(lefts) and len(set(lefts)) == 3
    assert_result_sane(result, "horizontal lanes")


def test_alignment_holds_when_lanes_size_their_items_differently():
    """Slots still agree; item centers agree to within one EA unit.

    Slot extent is the longest item at that index, and each item is centered in
    its slot with integer arithmetic, so an odd difference in size leaves a
    half-unit that has to land somewhere.
    """
    result = compose_lanes([
        {"name": "Customer", "items": _items("c1", "c2"), "item_width": 200},
        {"name": "Operations", "items": _items("o1", "o2"), "item_width": 145},
    ])
    by_index = {}
    for it in result["items"]:
        by_index.setdefault(it["index"], []).append(it)

    for idx, group in by_index.items():
        assert len({i["slot_start"] for i in group}) == 1, f"index {idx} slots differ"
        assert len({i["slot_extent"] for i in group}) == 1
        assert {i["slot_extent"] for i in group} == {200}
        centers = {_center_x2(i) for i in group}
        assert max(centers) - min(centers) <= 1, f"index {idx} centers drift"
    assert_result_sane(result, "mixed lane item widths")


def test_slot_length_is_the_longest_item_in_any_lane_not_the_first_lane():
    """The widest lane sets the slot wherever it happens to sit in the order.

    Reversing the lanes must produce the same slot table, and the narrow lane's
    items must be inset within it rather than butted against its start.
    """
    wide_first = compose_lanes([
        {"name": "Customer", "items": _items("c1", "c2"), "item_width": 240},
        {"name": "Operations", "items": _items("o1", "o2")},
    ])
    wide_last = compose_lanes([
        {"name": "Operations", "items": _items("o1", "o2")},
        {"name": "Customer", "items": _items("c1", "c2"), "item_width": 240},
    ])

    def slots(result):
        return sorted({(i["index"], i["slot_start"], i["slot_extent"])
                       for i in result["items"]})

    assert slots(wide_first) == slots(wide_last)
    assert [s[2] for s in slots(wide_first)] == [240, 240]

    for result in (wide_first, wide_last):
        for item in result["items"]:
            if rect_width(item) == 240:
                assert item["left"] == item["slot_start"]
            else:
                assert item["left"] == item["slot_start"] + 50   # (240 - 140) // 2
        assert_result_sane(result, "wide lane not first")


def test_vertical_lanes_flow_downward_and_still_align():
    result = compose_lanes(
        [
            {"name": "Customer", "items": _items("c1", "c2", "c3")},
            {"name": "Operations", "items": _items("o1", "o2")},
        ],
        orientation="vertical",
    )
    assert result["orientation"] == "vertical"

    # lanes sit side by side, left to right
    lefts = [c["left"] for c in result["containers"]]
    assert lefts == sorted(lefts) and len(set(lefts)) == 2
    assert {c["top"] for c in result["containers"]} == {DEFAULT_SPEC["origin_top"]}

    by_index = {}
    for it in result["items"]:
        by_index.setdefault(it["index"], []).append(it)
    for idx, group in by_index.items():
        assert len({i["top"] for i in group}) == 1, f"index {idx} tops disagree"
        assert len({i["bottom"] for i in group}) == 1

    lane0 = [i for i in result["items"] if i["lane_index"] == 0]
    tops = [i["top"] for i in sorted(lane0, key=lambda i: i["index"])]
    assert tops == sorted(tops, reverse=True), "flow runs downward"
    assert_result_sane(result, "vertical lanes")


def test_items_are_centered_across_the_lane_thickness():
    result = compose_lanes([
        {"name": "Customer", "items": _items("c1")},
        {"name": "Operations", "items": _items("o1")},
    ])
    for container in result["containers"]:
        item = next(i for i in result["items"]
                    if i["container_id"] == container["id"])
        top_gap = container["top"] - item["top"]
        bottom_gap = item["bottom"] - container["bottom"]
        assert abs(top_gap - bottom_gap) <= 1, "item not centered across the lane"
        assert top_gap >= DEFAULT_SPEC["lane_pad"]


def test_lane_thickness_follows_the_largest_item_in_that_lane():
    result = compose_lanes([
        {"name": "Customer", "items": _items("c1")},
        {"name": "Operations", "items": _items("o1"), "item_height": 160},
    ])
    thin, thick = result["containers"]
    assert rect_height(thin) == 60 + 2 * DEFAULT_SPEC["lane_pad"]
    assert rect_height(thick) == 160 + 2 * DEFAULT_SPEC["lane_pad"]
    assert rect_height(thick) > rect_height(thin)
    assert_result_sane(result, "adaptive thickness")


def test_min_lane_thickness_pads_a_thin_lane_and_yields_to_a_thick_one():
    result = compose_lanes(
        [{"name": "Thin", "items": _items("a")},
         {"name": "Thick", "items": _items("b"), "item_height": 300}],
        {"min_lane_thickness": 200},
    )
    thin, thick = result["containers"]
    assert rect_height(thin) == 200
    assert rect_height(thick) == 300 + 2 * DEFAULT_SPEC["lane_pad"]
    assert_result_sane(result, "min_lane_thickness")


def test_lanes_abut_exactly_by_default():
    horizontal = compose_lanes([
        {"name": "A", "items": _items("a")},
        {"name": "B", "items": _items("b"), "item_height": 120},
        {"name": "C", "items": _items("c")},
    ])
    for upper, lower in zip(horizontal["containers"], horizontal["containers"][1:]):
        assert lower["top"] == upper["bottom"], "horizontal lanes must touch"
    assert len({rect_width(c) for c in horizontal["containers"]}) == 1

    vertical = compose_lanes(
        [{"name": "A", "items": _items("a")}, {"name": "B", "items": _items("b")}],
        orientation="vertical",
    )
    for left_lane, right_lane in zip(vertical["containers"], vertical["containers"][1:]):
        assert right_lane["left"] == left_lane["right"], "vertical lanes must touch"
    assert len({rect_height(c) for c in vertical["containers"]}) == 1


def test_lane_gap_separates_lanes_when_asked():
    result = compose_lanes(
        [{"name": "A", "items": _items("a")}, {"name": "B", "items": _items("b")}],
        {"lane_gap": 24},
    )
    upper, lower = result["containers"]
    assert upper["bottom"] - lower["top"] == 24
    assert_result_sane(result, "separated lanes")


def test_a_lane_label_area_never_collides_with_its_items():
    result = compose_lanes([{"name": "Customer", "items": _items("c1", "c2")}])
    label = result["containers"][0]["label"]
    for item in result["items"]:
        assert not rects_overlap(label, item)
    assert rect_width(label) == DEFAULT_SPEC["label_width"]
    assert rect_height(label) == rect_height(result["containers"][0])

    vertical = compose_lanes(
        [{"name": "Customer", "items": _items("c1", "c2")}], orientation="vertical"
    )
    vlabel = vertical["containers"][0]["label"]
    for item in vertical["items"]:
        assert not rects_overlap(vlabel, item)
    assert rect_height(vlabel) == DEFAULT_SPEC["label_height"]


def test_an_empty_lane_is_valid_geometry():
    result = compose_lanes([
        {"name": "Customer", "items": _items("c1", "c2")},
        {"name": "Risk", "items": []},
    ])
    empty = result["containers"][1]
    assert rect_height(empty) >= 60 + 2 * DEFAULT_SPEC["lane_pad"]
    assert rect_width(empty) == rect_width(result["containers"][0])
    assert_result_sane(result, "empty lane")


def test_every_lane_empty_still_produces_lane_bands():
    result = compose_lanes([{"name": "A"}, {"name": "B"}])
    assert result["items"] == []
    assert len(result["containers"]) == 2
    for c in result["containers"]:
        assert_valid_rect(c, "all-empty lanes")
    assert_result_sane(result, "all-empty lanes")


def test_single_lane_single_item():
    result = compose_lanes([{"name": "Only", "items": _items("solo")}])
    assert len(result["items"]) == 1
    item = result["items"][0]
    assert item["index"] == 0
    assert item["slot_extent"] == 140
    assert_result_sane(result, "single lane")


def test_flow_pitch_acts_as_a_floor_on_slot_spacing():
    tight = compose_lanes([{"name": "A", "items": _items("a", "b")}])
    loose = compose_lanes(
        [{"name": "A", "items": _items("a", "b")}], {"flow_pitch": 400}
    )
    tight_step = tight["items"][1]["left"] - tight["items"][0]["left"]
    loose_step = loose["items"][1]["left"] - loose["items"][0]["left"]
    assert tight_step == 140 + DEFAULT_SPEC["item_gap_flow"]
    assert loose_step == 400
    assert_result_sane(loose, "flow_pitch")


def test_lanes_survive_a_wide_sweep_of_shapes():
    shapes = [[1], [0], [0, 0], [1, 5], [3, 3, 3], [7, 1, 4], [1] * 6, [12, 0, 2]]
    for orientation in ("horizontal", "vertical"):
        for shape in shapes:
            lanes = []
            n = 0
            for lane_no, count in enumerate(shape):
                ids = [f"e{n + k}" for k in range(count)]
                n += count
                lanes.append({"name": f"Lane {lane_no}", "items": _items(*ids)})
            result = compose_lanes(lanes, orientation=orientation)
            assert len(result["items"]) == sum(shape)
            assert len(result["containers"]) == len(shape)
            assert_result_sane(result, f"{orientation} shape {shape}")


# ===========================================================================
# 4. Determinism
# ===========================================================================
def test_bands_are_deterministic():
    bands = [
        {"name": "Channels", "items": _items("a", "b", "c", "d", "e")},
        {"name": "Applications", "items": _items("f", "g"), "item_width": 200},
        {"name": "Reserved", "items": []},
    ]
    spec = {"wrap_width": 460, "align": "center", "band_gap": 25}
    first = compose_layered_bands(bands, spec)
    second = compose_layered_bands(bands, spec)
    assert first == second


def test_lanes_are_deterministic():
    lanes = [
        {"name": "Customer", "items": _items("c1", "c2", "c3")},
        {"name": "Operations", "items": _items("o1"), "item_height": 120},
    ]
    first = compose_lanes(lanes, {"lane_pad": 8}, orientation="vertical")
    second = compose_lanes(lanes, {"lane_pad": 8}, orientation="vertical")
    assert first == second


def test_output_does_not_depend_on_spec_key_insertion_order():
    forwards = {"item_width": 150, "item_height": 70, "wrap_width": 700,
                "band_gap": 40, "align": "center"}
    backwards = {k: forwards[k] for k in reversed(list(forwards))}
    bands = [{"name": "A", "items": _items("a", "b", "c", "d", "e", "f")},
             {"name": "B", "items": _items("g")}]
    assert compose_layered_bands(bands, forwards) == compose_layered_bands(
        bands, backwards
    )


# ===========================================================================
# 5. Validation - a clear error beats silently wrong geometry
# ===========================================================================
def test_negative_and_zero_sizes_are_rejected_by_name():
    with pytest.raises(LayoutError, match=r"spec\.item_width"):
        compose_layered_bands([{"name": "A", "items": _items("a")}],
                              {"item_width": -140})
    with pytest.raises(LayoutError, match=r"spec\.item_height"):
        compose_layered_bands([{"name": "A", "items": _items("a")}],
                              {"item_height": 0})
    with pytest.raises(LayoutError, match=r"spec\.band_gap"):
        compose_layered_bands([{"name": "A", "items": _items("a")}],
                              {"band_gap": -5})


def test_zero_pitch_is_rejected():
    with pytest.raises(LayoutError, match=r"spec\.h_pitch"):
        compose_layered_bands([{"name": "A", "items": _items("a")}], {"h_pitch": 0})
    with pytest.raises(LayoutError, match=r"spec\.row_pitch"):
        compose_layered_bands([{"name": "A", "items": _items("a")}], {"row_pitch": 0})
    with pytest.raises(LayoutError, match=r"spec\.flow_pitch"):
        compose_lanes([{"name": "A", "items": _items("a")}], {"flow_pitch": 0})


def test_a_pitch_smaller_than_the_item_is_rejected_rather_than_overlapped():
    with pytest.raises(LayoutError, match="h_pitch.*smaller than item_width"):
        compose_layered_bands([{"name": "A", "items": _items("a", "b")}],
                              {"h_pitch": 100})
    with pytest.raises(LayoutError, match="row_pitch.*smaller than item_height"):
        compose_layered_bands([{"name": "A", "items": _items("a", "b")}],
                              {"row_pitch": 40})


def test_a_wrap_width_narrower_than_one_item_is_rejected():
    with pytest.raises(LayoutError, match="wrap_width.*smaller than item_width"):
        compose_layered_bands([{"name": "A", "items": _items("a")}],
                              {"wrap_width": 100})


def test_an_item_with_no_id_names_its_own_position():
    with pytest.raises(LayoutError, match=r"bands\[1\]\.items\[2\]\.id"):
        compose_layered_bands([
            {"name": "A", "items": _items("a")},
            {"name": "B", "items": [{"id": "b"}, {"id": "c"}, {"name": "no id"}]},
        ])
    with pytest.raises(LayoutError, match=r"lanes\[0\]\.items\[0\]\.id"):
        compose_lanes([{"name": "A", "items": [{"id": "  "}]}])


def test_duplicate_item_ids_are_rejected_across_the_whole_composition():
    with pytest.raises(LayoutError, match="duplicate item id 'a'"):
        compose_layered_bands([
            {"name": "A", "items": _items("a")},
            {"name": "B", "items": _items("b", "a")},
        ])


def test_an_unknown_spec_key_is_an_error_not_a_shrug():
    with pytest.raises(LayoutError, match="unknown key"):
        compose_layered_bands([{"name": "A", "items": _items("a")}],
                              {"itemWidth": 200})


def test_bad_enum_values_are_rejected():
    with pytest.raises(LayoutError, match=r"spec\.align"):
        compose_layered_bands([{"name": "A", "items": _items("a")}],
                              {"align": "middle"})
    with pytest.raises(LayoutError, match="orientation"):
        compose_lanes([{"name": "A", "items": _items("a")}], orientation="sideways")


def test_a_band_or_lane_needs_a_name():
    with pytest.raises(LayoutError, match=r"bands\[0\]\.name"):
        compose_layered_bands([{"items": _items("a")}])
    with pytest.raises(LayoutError, match=r"lanes\[1\]\.name"):
        compose_lanes([{"name": "A"}, {"name": "   "}])


def test_the_wrong_container_type_is_reported_with_its_path():
    with pytest.raises(LayoutError, match=r"bands\[0\]: expected a dict"):
        compose_layered_bands(["Channels"])
    with pytest.raises(LayoutError, match=r"bands\[0\]\.items: expected a list"):
        compose_layered_bands([{"name": "A", "items": {"id": "a"}}])
    with pytest.raises(LayoutError, match="bands: expected a list"):
        compose_layered_bands({"name": "A"})
    with pytest.raises(LayoutError, match="spec: expected a dict"):
        compose_layered_bands([{"name": "A", "items": _items("a")}], spec=[1, 2])


def test_nothing_to_place_is_an_error_not_an_empty_canvas():
    with pytest.raises(LayoutError, match="at least one band"):
        compose_layered_bands([])
    with pytest.raises(LayoutError, match="at least one lane"):
        compose_lanes([])


def test_booleans_are_not_accepted_as_sizes():
    with pytest.raises(LayoutError, match=r"spec\.item_width: expected a number"):
        compose_layered_bands([{"name": "A", "items": _items("a")}],
                              {"item_width": True})


def test_a_bad_per_band_override_names_the_band():
    with pytest.raises(LayoutError, match=r"bands\[1\]\.item_height"):
        compose_layered_bands([
            {"name": "A", "items": _items("a")},
            {"name": "B", "items": _items("b"), "item_height": -60},
        ])
    with pytest.raises(LayoutError, match=r"lanes\[0\]\.item_width"):
        compose_lanes([{"name": "A", "items": _items("a"), "item_width": 0}])


if __name__ == "__main__":       # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))


# ---------------------------------------------------------------------------
# Item ids: any hashable, preserved verbatim
# ---------------------------------------------------------------------------

def test_integer_ids_are_accepted_and_preserved():
    """EA element ids are integers.

    Requiring strings would force a str() at every call site and invite the
    classic "123" != 123 bug when the composed rects are matched back against
    the model.
    """
    result = compose_layered_bands([
        {"name": "Band", "items": [{"id": 13477}, {"id": 13478}]},
    ])
    ids = [item["id"] for item in result["items"]]
    assert ids == [13477, 13478]
    assert all(isinstance(i, int) for i in ids), "ids must not be stringified"


def test_mixed_id_types_still_collide_when_equal():
    """Uniqueness is by value, so a duplicate is caught whatever its type."""
    with pytest.raises(LayoutError, match="duplicate"):
        compose_layered_bands([
            {"name": "Band", "items": [{"id": 7}, {"id": 7}]},
        ])


def test_int_and_string_forms_of_the_same_number_are_different_ids():
    """7 and "7" are genuinely different element references; treating them as
    the same would be a guess about the caller's intent."""
    result = compose_layered_bands([
        {"name": "Band", "items": [{"id": 7}, {"id": "7"}]},
    ])
    assert [item["id"] for item in result["items"]] == [7, "7"]


def test_a_missing_id_is_still_an_error():
    with pytest.raises(LayoutError, match="non-empty id"):
        compose_layered_bands([{"name": "Band", "items": [{"name": "no id"}]}])


def test_an_unhashable_id_is_rejected_with_a_clear_reason():
    with pytest.raises(LayoutError, match="hashable"):
        compose_layered_bands([{"name": "Band", "items": [{"id": ["a", "list"]}]}])


# ===========================================================================
# 6. Nested grid
# ===========================================================================
# `assert_result_sane` deliberately does NOT apply here. Two of its checks are
# wrong for this grammar by design:
#
#   * it asserts no two containers overlap, and a subdomain inside a domain is
#     supposed to overlap its parent;
#   * it looks every item's `container_id` up in the container table, and a
#     root-level leaf has none.
#
# So this grammar gets its own sanity helper, which is strictly stronger: it
# checks no-overlap among SIBLINGS at every level and containment at every
# level, rather than once over one flat set.
def _tree_index(result):
    """Group a nested-grid result by parent, so siblings can be compared.

    Returns `{parent_id: [rect, ...]}` covering containers and items together,
    because a leaf and a container sharing a parent are siblings and must not
    overlap each other either.
    """
    by_parent = {}
    for c in result["containers"]:
        by_parent.setdefault(c["parent_id"], []).append(c)
    for it in result["items"]:
        by_parent.setdefault(it["container_id"], []).append(it)
    return by_parent


def assert_nested_result_sane(result, label=""):
    """Every check that must hold for any nested grid, at every level."""
    containers = {c["id"]: c for c in result["containers"]}
    for c in result["containers"]:
        assert_valid_rect(c, f"{label} container {c['id']}")
        assert_valid_rect(c["label"], f"{label} label of {c['id']}")
        assert_contains(c, c["label"], f"{label} label of {c['id']}")
    for it in result["items"]:
        assert_valid_rect(it, f"{label} item {it['id']}")

    by_parent = _tree_index(result)
    for parent_id, siblings in by_parent.items():
        assert_no_overlaps(siblings, f"{label} siblings under {parent_id!r}")
        if parent_id is not None:
            for child in siblings:
                assert_contains(
                    containers[parent_id], child,
                    f"{label} {child.get('id')} inside {parent_id!r}",
                )

    # Containment is transitive, but assert it against every ancestor anyway:
    # a child that fits its parent while its parent overflows the grandparent
    # is the failure this grammar is most likely to produce.
    for c in result["containers"]:
        ancestor = containers.get(c["parent_id"])
        while ancestor is not None:
            assert_contains(ancestor, c, f"{label} {c['id']} in {ancestor['id']}")
            ancestor = containers.get(ancestor["parent_id"])

    expected = bounding_box([*result["containers"], *result["items"]])
    assert result["bounds"] == expected, f"{label}: bounds disagree with contents"


def _group(name, children, **extra):
    return {"name": name, "items": children, **extra}


# A two-level tree used by several tests: three top-level groups of unequal
# size, one of them nesting a further level, and one loose leaf at the top.
def _sample_tree():
    return [
        _group("Customer", [
            _group("Onboarding", _items(101, 102, 103)),
            _group("Servicing", _items(104)),
        ]),
        _group("Payments", _items(105, 106, 107, 108)),
        _group("Risk", _items(109)),
    ]


# ---------------------------------------------------------------------------
# Structure: containment and no overlaps, at every level
# ---------------------------------------------------------------------------
def test_a_nested_grid_is_sane_at_every_level():
    result = compose_nested_grid(_sample_tree())
    assert result["grammar"] == "nested_grid"
    assert_nested_result_sane(result, "sample tree")
    assert len(result["items"]) == 9
    assert {c["name"] for c in result["containers"]} == {
        "Customer", "Onboarding", "Servicing", "Payments", "Risk",
    }


def test_every_leaf_sits_inside_the_container_that_declared_it():
    """The mapping from `container_id` back to the declaring group must hold.

    Geometry alone is not enough: a leaf could sit inside the RIGHT rect while
    being reported under the wrong parent, and a caller building EA's ownership
    relationships from `container_id` would then nest the element under the
    wrong element while the picture looked correct.
    """
    result = compose_nested_grid(_sample_tree())
    by_id = {c["id"]: c for c in result["containers"]}
    declared = {
        101: "Onboarding", 102: "Onboarding", 103: "Onboarding",
        104: "Servicing",
        105: "Payments", 106: "Payments", 107: "Payments", 108: "Payments",
        109: "Risk",
    }
    for item in result["items"]:
        parent = by_id[item["container_id"]]
        assert parent["name"] == declared[item["id"]], item
        assert_contains(parent, item, f"item {item['id']}")


def test_depth_counts_grid_levels_from_one():
    result = compose_nested_grid(_sample_tree())
    depths = {c["name"]: c["depth"] for c in result["containers"]}
    assert depths["Customer"] == 1
    assert depths["Payments"] == 1
    assert depths["Onboarding"] == 2
    by_id = {c["id"]: c for c in result["containers"]}
    for item in result["items"]:
        assert item["depth"] == by_id[item["container_id"]]["depth"] + 1


def test_a_root_level_leaf_has_no_container():
    """A leaf at the top level is legitimate and comes back with no parent.

    `container_id: None` rather than a sentinel string, so a caller that forgets
    to handle it raises on the lookup instead of silently nesting the element
    under a group called "None".
    """
    result = compose_nested_grid([
        {"id": "loose"},
        _group("Grouped", _items("inner")),
    ])
    loose = next(i for i in result["items"] if i["id"] == "loose")
    assert loose["container_id"] is None
    assert loose["depth"] == 1
    assert_nested_result_sane(result, "root leaf")


# ---------------------------------------------------------------------------
# Sizing: uniform within a level, content-driven between containers
# ---------------------------------------------------------------------------
def test_every_leaf_in_one_grid_is_the_same_size():
    result = compose_nested_grid(_sample_tree())
    by_parent = {}
    for item in result["items"]:
        by_parent.setdefault(item["container_id"], []).append(item)
    for parent, items in by_parent.items():
        sizes = {(rect_width(i), rect_height(i)) for i in items}
        assert len(sizes) == 1, f"{parent}: siblings disagree about size {sizes}"


def test_a_leaf_has_nowhere_to_state_a_size_of_its_own():
    """Sibling uniformity is structural, not a rule the caller must remember.

    Item size is stated by the PARENT. A leaf carrying `item_width` is therefore
    an unknown key on a leaf - and since the leaf's only recognized key is `id`,
    the size is simply ignored rather than honoured. This test pins that it is
    ignored, because the alternative - honouring it - is what lets two siblings
    end up different sizes, the defect the grammar's own rule exists to prevent.
    """
    plain = compose_nested_grid([_group("G", [{"id": 1}, {"id": 2}])])
    shouty = compose_nested_grid([_group("G", [
        {"id": 1, "item_width": 400, "item_height": 400},
        {"id": 2},
    ])])
    assert plain["items"] == shouty["items"]
    assert plain["bounds"] == shouty["bounds"]


def test_levels_may_size_their_items_differently():
    """A container restates the size for its OWN children, not for its
    grandchildren - so "levels may differ" is expressible and does not leak."""
    result = compose_nested_grid([
        _group("Outer", [
            _group("Inner", _items(1, 2)),
            {"id": 3},
        ], item_width=200, item_height=90),
    ])
    by_id = {i["id"]: i for i in result["items"]}
    # The direct child of Outer takes Outer's override.
    assert rect_width(by_id[3]) == 200
    assert rect_height(by_id[3]) == 90
    # The grandchildren do NOT inherit it; they fall back to the spec default.
    assert rect_width(by_id[1]) == DEFAULT_SPEC["item_width"]
    assert rect_height(by_id[1]) == DEFAULT_SPEC["item_height"]
    assert rect_width(by_id[1]) != 200
    assert_nested_result_sane(result, "per-level sizing")


def test_a_container_is_sized_by_its_contents():
    """A group with many children is visibly bigger than one with few.

    This is the property that keeps a nested grid honest: containers sized alike
    would make a group holding two things look as significant as one holding
    twenty.
    """
    result = compose_nested_grid([
        _group("Big", _items(*range(1, 10))),
        _group("Small", _items(99)),
    ])
    big = next(c for c in result["containers"] if c["name"] == "Big")
    small = next(c for c in result["containers"] if c["name"] == "Small")
    assert rect_width(big) > rect_width(small)


def test_a_container_is_never_stretched_to_match_a_bigger_sibling():
    """Content sizing beats edge alignment, deliberately, for this grammar.

    The first implementation snapped every container to its cell, so a row of
    containers shared one height and the edges lined up. It looked tidier and it
    was wrong: a four-child capability and a two-child one came out at exactly
    the same 324x192, which is the failure `references/grammars.md` names for
    this grammar - "containers are sized alike so a container with two children
    looks as significant as one with twenty".

    The cost is a ragged bottom edge within a row, and that cost is accepted
    here. It is NOT the same question as `APT-2026-0152`: a band is a full-width
    strip whose raggedness reads as a mistake, while a grid of differently sized
    groups is what a capability map is supposed to look like.
    """
    result = compose_nested_grid([
        _group("Tall", [_group("A", _items(1, 2)), _group("B", _items(3, 4))]),
        _group("Short", _items(5)),
    ], spec={"grid_columns": 2})
    tall = next(c for c in result["containers"] if c["name"] == "Tall")
    short = next(c for c in result["containers"] if c["name"] == "Short")
    assert tall["row"] == short["row"] == 0
    assert tall["top"] == short["top"], "a row should still start level"
    assert rect_height(tall) > rect_height(short), (
        "the sparser container was stretched to match its sibling"
    )
    assert rect_width(tall) > rect_width(short)
    # The slack left in the cell is empty space, not a collision.
    assert_nested_result_sane(result, "ragged row")


def test_more_children_never_means_a_smaller_container():
    """The monotonic form of the rule, swept rather than spot-checked.

    Spot-checking two shapes is how the previous version of this passed while
    4-vs-2 children produced identical boxes: 9-vs-1 happened to differ.
    """
    areas = []
    for n in range(1, 13):
        result = compose_nested_grid([_group("G", _items(*range(n)))])
        group = result["containers"][0]
        areas.append(rect_width(group) * rect_height(group))
    for smaller, bigger in zip(areas, areas[1:]):
        assert bigger >= smaller, areas
    assert areas[-1] > areas[0], "twelve children must not fit in one child's box"


def test_a_leaf_is_centered_in_a_cell_taller_than_itself():
    """Derived from a sibling that fills the same row, so no literal is needed."""
    result = compose_nested_grid([
        _group("Row", [_group("HasChildren", _items(1, 2, 3)), {"id": 4}]),
    ], spec={"grid_columns": 2})
    filler = next(c for c in result["containers"] if c["name"] == "HasChildren")
    leaf = next(i for i in result["items"] if i["id"] == 4)
    assert filler["row"] == leaf["row"] == 0
    assert rect_height(leaf) < rect_height(filler), "no slack to center in"
    assert _center_y2(leaf) == _center_y2(filler)


# ---------------------------------------------------------------------------
# Grid shape
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6, 9, 10, 16, 17])
def test_grids_come_out_close_to_square(n):
    """Columns are ceil(sqrt(n)), computed here independently of the engine."""
    expected = math.isqrt(n - 1) + 1 if n > 1 else 1
    result = compose_nested_grid([_group("G", _items(*range(n)))])
    columns = max(i["column"] for i in result["items"]) + 1
    rows = max(i["row"] for i in result["items"]) + 1
    assert columns == expected, f"n={n}"
    assert rows == -(-n // expected)
    assert_nested_result_sane(result, f"square n={n}")


def test_grid_columns_fixes_the_column_count():
    result = compose_nested_grid(
        [_group("G", _items(*range(6)))], spec={"grid_columns": 3}
    )
    assert max(i["column"] for i in result["items"]) + 1 == 3
    assert max(i["row"] for i in result["items"]) + 1 == 2


def test_a_container_may_fix_its_own_column_count():
    result = compose_nested_grid([
        _group("Wide", _items(*range(4)), grid_columns=4),
        _group("Narrow", _items(*range(10, 14)), grid_columns=1),
    ])
    wide = [i for i in result["items"] if i["id"] < 10]
    narrow = [i for i in result["items"] if i["id"] >= 10]
    assert max(i["row"] for i in wide) == 0
    assert max(i["column"] for i in narrow) == 0
    assert_nested_result_sane(result, "per-container columns")


def test_more_columns_than_children_does_not_leave_empty_columns():
    """A column count above the child count collapses to the child count.

    Otherwise the container would be padded out with the width of columns that
    hold nothing, and a group of two would be drawn as wide as a group of ten.
    """
    tight = compose_nested_grid([_group("G", _items(1, 2))],
                                spec={"grid_columns": 2})
    loose = compose_nested_grid([_group("G", _items(1, 2))],
                                spec={"grid_columns": 9})
    assert tight["bounds"] == loose["bounds"]


# ---------------------------------------------------------------------------
# Whitespace between cells
# ---------------------------------------------------------------------------
# These exist because `assert_nested_result_sane` CANNOT see a missing gap.
# `rects_overlap` exempts rects that merely touch - abutting swimlanes are
# correct geometry - so a grid that dropped `item_gap_x` entirely and packed
# every cell edge to edge passed every other test in this file. A no-overlap
# rule never implies whitespace, and this grammar's whole job is whitespace.
def test_adjacent_cells_are_separated_by_the_item_gap():
    """Measured on an all-leaf grid, where a cell is exactly one item wide, so
    the leaf-to-leaf gap IS the cell gap with no centering slack in between."""
    gap_x, gap_y = 24, 18
    result = compose_nested_grid(
        [_group("G", _items(*range(6)))],
        spec={"grid_columns": 3, "item_gap_x": gap_x, "item_gap_y": gap_y},
    )
    by_cell = {(i["row"], i["column"]): i for i in result["items"]}
    assert len(by_cell) == 6
    for (row, col), item in by_cell.items():
        right = by_cell.get((row, col + 1))
        if right is not None:
            assert right["left"] - item["right"] == gap_x
        below = by_cell.get((row + 1, col))
        if below is not None:
            assert item["bottom"] - below["top"] == gap_y


def test_the_default_spec_leaves_real_whitespace_between_cells():
    """The defaults have to be usable without a spec, and a grid with no
    whitespace is not - it reads as one block, not as a set of things."""
    assert DEFAULT_SPEC["item_gap_x"] > 0
    assert DEFAULT_SPEC["item_gap_y"] > 0
    result = compose_nested_grid([_group("G", _items(1, 2, 3, 4))])
    by_cell = {(i["row"], i["column"]): i for i in result["items"]}
    assert by_cell[(0, 1)]["left"] - by_cell[(0, 0)]["right"] > 0
    assert by_cell[(0, 0)]["bottom"] - by_cell[(1, 0)]["top"] > 0


def test_sibling_containers_are_separated_by_the_item_gap():
    gap = 30
    result = compose_nested_grid(
        [_group("A", _items(1)), _group("B", _items(2))],
        spec={"grid_columns": 2, "item_gap_x": gap},
    )
    a, b = sorted(result["containers"], key=lambda c: c["left"])
    assert b["left"] - a["right"] == gap


# ---------------------------------------------------------------------------
# Padding and labels
# ---------------------------------------------------------------------------
def test_padding_is_constant_with_the_title_strip_as_an_extra_top_inset():
    """Read off a single-child container, against DEFAULT_SPEC rather than
    literals, so a change to the defaults cannot leave this test asserting a
    number nobody ships any more."""
    result = compose_nested_grid([_group("G", _items(1))])
    group = result["containers"][0]
    child = result["items"][0]
    pad = DEFAULT_SPEC["grid_pad"]
    assert child["left"] - group["left"] == pad
    assert group["right"] - child["right"] == pad
    assert group["bottom"] - child["bottom"] == -pad
    assert group["top"] - child["top"] == DEFAULT_SPEC["label_height"] + pad


def test_a_container_label_never_collides_with_its_children():
    result = compose_nested_grid(_sample_tree())
    for container in result["containers"]:
        for child in _tree_index(result).get(container["id"], []):
            assert not rects_overlap(container["label"], child), (
                f"{container['name']} label overlaps {child.get('id')}"
            )


def test_an_empty_container_keeps_its_label_and_one_cell_of_space():
    result = compose_nested_grid([_group("Planned", [])])
    group = result["containers"][0]
    assert result["items"] == []
    assert rect_width(group) == (
        DEFAULT_SPEC["item_width"] + 2 * DEFAULT_SPEC["grid_pad"]
    )
    assert rect_height(group) == (
        DEFAULT_SPEC["label_height"] + DEFAULT_SPEC["item_height"]
        + 2 * DEFAULT_SPEC["grid_pad"]
    )
    assert_nested_result_sane(result, "empty container")


def test_an_items_key_makes_a_container_even_when_it_is_empty():
    """`items: []` is a container, not a leaf that lost its children.

    The discriminator is the presence of the KEY. If it were truthiness, a group
    whose last child was removed would silently turn into a leaf - and a leaf
    with no `id` is an error, so the diagram would start failing to build for a
    reason unrelated to the edit that caused it.
    """
    result = compose_nested_grid([_group("Still A Group", [])])
    assert [c["name"] for c in result["containers"]] == ["Still A Group"]
    assert result["items"] == []


# ---------------------------------------------------------------------------
# The depth bound
# ---------------------------------------------------------------------------
def _nest(depth, leaf_id="leaf"):
    """A chain of `depth` containers with one leaf at the bottom."""
    node = {"id": leaf_id}
    for level in range(depth, 0, -1):
        node = _group(f"L{level}", [node])
    return [node]


def test_three_levels_of_containment_are_allowed_by_default():
    result = compose_nested_grid(_nest(3))
    assert max(c["depth"] for c in result["containers"]) == 3
    assert result["items"][0]["depth"] == 4
    assert_nested_result_sane(result, "three levels")


def test_nesting_past_the_bound_is_refused_and_names_the_path():
    with pytest.raises(LayoutError) as exc:
        compose_nested_grid(_nest(4))
    message = str(exc.value)
    # Wording only this branch produces - the generic "unknown key" and
    # "must be positive" messages would both match a bare "max_grid_depth".
    assert "containers deep" in message
    assert "nodes[0].items[0].items[0].items[0]" in message
    assert str(DEFAULT_SPEC["max_grid_depth"]) in message


def test_the_depth_bound_is_a_refusal_not_a_warning():
    """Recorded as a decision, not an accident: the result dict has no channel
    a warning could travel down that any caller reads, so a deeper tree raises.
    A caller who genuinely wants four levels raises the bound and says so."""
    deep = _nest(4)
    with pytest.raises(LayoutError):
        compose_nested_grid(deep)
    result = compose_nested_grid(deep, spec={"max_grid_depth": 4})
    assert max(c["depth"] for c in result["containers"]) == 4
    assert_nested_result_sane(result, "four levels, asked for")


def test_a_shallower_bound_refuses_what_the_default_allows():
    two = _nest(3)
    compose_nested_grid(two)  # fine by default
    with pytest.raises(LayoutError, match="containers deep"):
        compose_nested_grid(two, spec={"max_grid_depth": 2})


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------
def test_nested_grid_is_deterministic():
    tree = _sample_tree()
    assert compose_nested_grid(tree) == compose_nested_grid(_sample_tree())
    assert compose_nested_grid(tree) == compose_nested_grid(tree)


def test_nested_grid_ignores_spec_key_insertion_order():
    a = compose_nested_grid(_sample_tree(),
                            spec={"grid_pad": 8, "grid_columns": 2})
    b = compose_nested_grid(_sample_tree(),
                            spec={"grid_columns": 2, "grid_pad": 8})
    assert a == b


# ---------------------------------------------------------------------------
# Ids
# ---------------------------------------------------------------------------
def test_duplicate_item_ids_are_rejected_across_the_whole_tree():
    """Across branches, not just among siblings - the same registry the other
    two grammars use, which is why it is one shared helper."""
    with pytest.raises(LayoutError, match="duplicate item id"):
        compose_nested_grid([
            _group("A", [{"id": "shared"}]),
            _group("B", [_group("C", [{"id": "shared"}])]),
        ])


def test_a_duplicate_container_id_is_rejected():
    with pytest.raises(LayoutError, match="duplicate container id"):
        compose_nested_grid([
            _group("A", _items(1), id="g"),
            _group("B", _items(2), id="g"),
        ])


def test_a_container_id_may_not_collide_with_an_item_id():
    """Both are mapped back onto model elements, so one id cannot mean both."""
    with pytest.raises(LayoutError, match="already used by an item"):
        compose_nested_grid([
            _group("A", [{"id": "clash"}]),
            _group("B", _items(2), id="clash"),
        ])


def test_explicit_container_ids_are_used_verbatim():
    result = compose_nested_grid([
        _group("A", _items(1), id=4242),
        _group("B", _items(2)),
    ])
    ids = [c["id"] for c in result["containers"]]
    assert 4242 in ids
    generated = [i for i in ids if i != 4242]
    assert len(generated) == 1
    assert isinstance(generated[0], str)


def test_generated_container_ids_are_unique_across_a_deep_tree():
    result = compose_nested_grid([
        _group("A", [_group("A1", _items(1)), _group("A2", _items(2))]),
        _group("B", [_group("B1", _items(3)), _group("B2", _items(4))]),
    ])
    ids = [c["id"] for c in result["containers"]]
    assert len(ids) == len(set(ids)) == 6


# ---------------------------------------------------------------------------
# Rejections
# ---------------------------------------------------------------------------
def test_a_container_needs_a_name():
    with pytest.raises(LayoutError, match=r"nodes\[0\]\.name"):
        compose_nested_grid([{"items": _items(1)}])


def test_a_leaf_needs_an_id():
    with pytest.raises(LayoutError, match=r"nodes\[0\]\.items\[1\]\.id"):
        compose_nested_grid([_group("G", [{"id": 1}, {"name": "nameless"}])])


def test_an_empty_node_list_is_an_error_not_an_empty_canvas():
    with pytest.raises(LayoutError, match="at least one node"):
        compose_nested_grid([])


def test_grid_pad_rejects_a_negative_value():
    with pytest.raises(LayoutError, match=r"spec\.grid_pad: must not be negative"):
        compose_nested_grid([_group("G", _items(1))], spec={"grid_pad": -1})


def test_grid_pad_of_zero_is_allowed():
    """Zero padding is tight but legal - children touch the container edge, and
    touching is not overlapping in this engine."""
    result = compose_nested_grid([_group("G", _items(1))], spec={"grid_pad": 0})
    assert_nested_result_sane(result, "zero pad")


@pytest.mark.parametrize("value", [0, -3])
def test_grid_columns_rejects_a_non_positive_count(value):
    with pytest.raises(LayoutError, match=r"spec\.grid_columns: must be positive"):
        compose_nested_grid([_group("G", _items(1))],
                            spec={"grid_columns": value})


def test_max_grid_depth_rejects_zero():
    with pytest.raises(LayoutError, match=r"spec\.max_grid_depth: must be positive"):
        compose_nested_grid([_group("G", _items(1))],
                            spec={"max_grid_depth": 0})


def test_a_bad_per_container_override_names_the_container():
    with pytest.raises(LayoutError, match=r"nodes\[1\]\.item_width"):
        compose_nested_grid([
            _group("Fine", _items(1)),
            _group("Broken", _items(2), item_width=0),
        ])


def test_a_leaf_where_a_list_was_expected_is_reported_with_its_path():
    with pytest.raises(LayoutError, match=r"nodes\[0\]\.items"):
        compose_nested_grid([{"name": "G", "items": "not a list"}])


def test_a_non_mapping_node_is_reported_with_its_path():
    with pytest.raises(LayoutError, match=r"nodes\[1\]"):
        compose_nested_grid([_group("G", _items(1)), "not a dict"])


# ---------------------------------------------------------------------------
# Sweep
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("spec", [
    None,
    {"grid_pad": 0},
    {"grid_pad": 40},
    {"grid_columns": 1},
    {"grid_columns": 5},
    {"item_width": 60, "item_height": 30},
    {"item_gap_x": 0, "item_gap_y": 0},
    {"label_height": 60},
    {"origin_left": -500, "origin_top": 0},
    {"max_grid_depth": 5},
])
def test_nested_grids_survive_a_wide_sweep_of_shapes(spec):
    """Every shape the grammar is meant to take, against every sanity rule.

    `origin_top: 0` is in the sweep on purpose: a composition starting at the
    coordinate origin is the edge case where a sign error in EA's inverted y
    axis stops cancelling out and starts producing rects with negative height.
    """
    trees = [
        _sample_tree(),
        _nest(3),
        [_group("Only", [])],
        [{"id": "flat"}],
        _items(1, 2, 3, 4, 5),
        [_group("Mixed", [{"id": 1}, _group("Sub", _items(2, 3)), {"id": 4}])],
    ]
    for i, tree in enumerate(trees):
        result = compose_nested_grid(tree, spec=spec)
        assert_nested_result_sane(result, f"sweep tree {i} spec {spec}")
