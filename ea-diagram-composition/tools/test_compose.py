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
