#!/usr/bin/env python3
"""Pure-arithmetic layout engine for composed diagrams.

This is the code corner of the diagram-composition skill. It turns a plain-data
description of what belongs on a diagram into rectangles, and does nothing else:
no repository calls, no COM, no file or network I/O, no clock, no randomness.
Same input, same output, every time.

Modeling-language specifics do not belong in this file. Sizes, spacing, wrap
widths and label areas arrive in a `spec` dict supplied by the caller - in
practice from a per-language binding held as data. There is no branch here on a
technology id, a profile name or a stereotype, and adding one would be a design
error: the arithmetic of a band of boxes is the same whatever notation the boxes
are eventually drawn in.

Coordinate convention
---------------------
Sparx EA's diagram coordinates are not the usual screen coordinates, and getting
this backwards silently corrupts everything downstream.

    left, right   positive, increasing rightward       right > left
    top, bottom   NEGATIVE, increasing upward          top > bottom

So:

    width  = right - left
    height = top - bottom          <-- not bottom - top

A real element placed by EA 17.1: left=50, top=-50, right=190, bottom=-110. That
is 140 wide and 60 tall. Moving an element DOWN the diagram makes both `top` and
`bottom` MORE negative. The visual top of a diagram is the coordinate nearest
zero, which means "the topmost rect" is the one with the LARGEST `top`.

Every rect this module produces obeys that convention, and `rects_overlap` is
written for it. Build rects with `rect()` rather than by hand.

Grammars implemented here
-------------------------
`compose_layered_bands` - horizontal bands stacked top to bottom, items laid out
left to right inside each band, wrapping to further rows when a band is wider
than the wrap width.

`compose_lanes` - swimlanes: parallel tracks, each carrying a sequence of items
that flows along the lane. Items at the same sequence index across different
lanes line up on the flow axis, which is what makes a handoff readable.

Both take plain lists of dicts and return plain dicts. No classes to construct,
nothing to subclass.

Result shape
------------
    {
      "grammar":    "layered_bands" | "lanes",
      "items":      [ {"id", "left", "top", "right", "bottom", ...}, ... ],
      "containers": [ {"id", "name", "kind", "index", "left", "top", "right",
                       "bottom", "label": {...}}, ... ],
      "bounds":     {"left", "top", "right", "bottom", "width", "height"},
    }

`items` are nested inside their `containers` by design, so test the two sets for
mutual disjointness separately - an item is supposed to sit inside its band.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

__all__ = [
    "LayoutError",
    "DEFAULT_SPEC",
    "compose_layered_bands",
    "compose_lanes",
    "rect",
    "rect_width",
    "rect_height",
    "rects_overlap",
    "bounding_box",
]


class LayoutError(ValueError):
    """A layout description or spec that cannot produce sane geometry.

    Raised in preference to returning rects that are negative, zero-sized or
    overlapping. The message always names the offending field, using the
    caller's own path into the input - `bands[2].items[0].id`, `spec.h_pitch` -
    so the caller can find it without guessing.
    """


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
# Units are EA diagram units, which for practical purposes are pixels at 100%
# zoom. These numbers are deliberately generous: a caller that supplies no spec
# at all should still get something a person would accept, not something that
# merely fails to crash.
#
# A value of None means "derive it" - see _band_metrics and _lane_metrics for
# the derivation. Deriving the pitch from size plus gap is what lets a caller
# override one item size without also having to restate every pitch.
DEFAULT_SPEC: dict[str, Any] = {
    # Where the top-left of the composition goes. `origin_top` is negative
    # because EA's vertical axis is.
    "origin_left": 20,
    "origin_top": -20,

    # Item box size. Uniform within a band or a lane; see the note in
    # _band_metrics on why that is a rule and not an accident.
    "item_width": 140,
    "item_height": 60,

    # Gaps used to derive pitches when a pitch is not given outright.
    "item_gap_x": 20,
    "item_gap_y": 20,

    # Pitch = step from one item's leading edge to the next one's, along the
    # axis named. Must be at least the item's extent on that axis, or items
    # would overlap. None -> item extent + matching gap.
    "h_pitch": None,      # left edge to left edge, within a band row
    "row_pitch": None,    # top edge to top edge, between wrapped rows

    # Widest a band's content may get before it wraps to another row.
    "wrap_width": 900,

    # "left" or "center" - how bands line up against each other.
    "align": "left",

    # Label areas. A band reserves a strip across its top; a horizontal lane
    # reserves a column down its left; a vertical lane reserves a strip across
    # its top.
    "label_height": 28,
    "label_width": 140,

    # Band container padding and stacking.
    "band_pad_x": 12,
    "band_pad_y": 12,
    "band_gap": 30,           # vertical gap between one band and the next
    "band_pitch": None,       # optional MINIMUM band-top to band-top step
    "min_band_width": None,   # None -> item_width + 2 * band_pad_x

    # Lane container padding and stacking.
    "lane_pad": 12,
    "lane_gap": 0,                # swimlanes normally abut; 0 makes them touch
    "item_gap_flow": 30,          # gap between successive slots along the flow
    "flow_pitch": None,           # optional MINIMUM slot-start to slot-start step
    "min_lane_thickness": None,   # None -> item cross extent + 2 * lane_pad
}

_ANY_INT_KEYS = frozenset({"origin_left", "origin_top"})
_POSITIVE_KEYS = frozenset({
    "item_width", "item_height", "wrap_width", "label_height", "label_width",
})
_NON_NEGATIVE_KEYS = frozenset({
    "item_gap_x", "item_gap_y", "item_gap_flow",
    "band_pad_x", "band_pad_y", "band_gap", "lane_pad", "lane_gap",
})
_OPTIONAL_POSITIVE_KEYS = frozenset({
    "h_pitch", "row_pitch", "band_pitch", "flow_pitch",
    "min_band_width", "min_lane_thickness",
})
_ALIGNMENTS = ("left", "center")
_ORIENTATIONS = ("horizontal", "vertical")

# Keys a single band or lane may override for itself. Different bands are
# allowed to size their items differently; items within one band are not.
_BAND_OVERRIDES = frozenset({
    "item_width", "item_height", "h_pitch", "row_pitch", "wrap_width",
    "label_height",
})
_LANE_OVERRIDES = frozenset({"item_width", "item_height"})


# ---------------------------------------------------------------------------
# Rect primitives - all in EA's convention
# ---------------------------------------------------------------------------
def rect(left: int, top: int, width: int, height: int) -> dict[str, int]:
    """Build a rect from its top-left corner plus a size, in EA's convention.

    `top` is expected to be negative or zero; `bottom` comes out below it, which
    in EA means numerically smaller. Width and height must be positive - a
    zero-size rect is a bug, not a degenerate case worth supporting.
    """
    if width <= 0 or height <= 0:
        raise LayoutError(
            f"rect: width and height must both be positive, got "
            f"width={width}, height={height}"
        )
    return {"left": left, "top": top, "right": left + width, "bottom": top - height}


def rect_width(r: Mapping[str, int]) -> int:
    """Width of a rect: right - left."""
    return r["right"] - r["left"]


def rect_height(r: Mapping[str, int]) -> int:
    """Height of a rect: top - bottom, because EA's vertical axis is inverted."""
    return r["top"] - r["bottom"]


def rects_overlap(a: Mapping[str, int], b: Mapping[str, int]) -> bool:
    """True when two rects share positive area, in EA's flipped-y convention.

    Rects that merely touch along an edge do not overlap - abutting swimlanes
    are correct geometry, not a collision. The vertical test is the one that
    catches people out: `a` is above `b` when a's BOTTOM is at or above b's TOP,
    and "above" means numerically greater.
    """
    if a["right"] <= b["left"] or b["right"] <= a["left"]:
        return False
    if a["bottom"] >= b["top"] or b["bottom"] >= a["top"]:
        return False
    return True


def bounding_box(rects: Sequence[Mapping[str, int]]) -> dict[str, int]:
    """Smallest rect enclosing all of `rects`, plus its width and height.

    `top` is the MAXIMUM of the tops and `bottom` the minimum, because the
    visual top of an EA diagram is the coordinate nearest zero.
    """
    if not rects:
        raise LayoutError("bounding_box: needs at least one rect")
    return _bounds(rects)


def _bounds(rects: Sequence[Mapping[str, int]]) -> dict[str, int]:
    left = min(r["left"] for r in rects)
    right = max(r["right"] for r in rects)
    top = max(r["top"] for r in rects)
    bottom = min(r["bottom"] for r in rects)
    return {
        "left": left,
        "top": top,
        "right": right,
        "bottom": bottom,
        "width": right - left,
        "height": top - bottom,
    }


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def _as_int(value: Any, where: str) -> int:
    """Coerce a number to a whole EA unit, rejecting anything that is not one.

    bool is rejected on purpose: True would otherwise sail through as 1 and
    produce geometry nobody asked for.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise LayoutError(f"{where}: expected a number, got {type(value).__name__}")
    return int(round(value))


def _require_mapping(value: Any, where: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise LayoutError(f"{where}: expected a dict, got {type(value).__name__}")
    return value


def _require_list(value: Any, where: str) -> list[Any]:
    """Accept any ordered sequence except a string, and keep the caller's order.

    Order is the whole input here - band order is stacking order, item order is
    reading order - so a set or a bare dict is rejected rather than quietly
    iterated in whatever order it happens to have.
    """
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise LayoutError(
            f"{where}: expected a list, got {type(value).__name__}"
        )
    return list(value)


def _resolve_spec(spec: Mapping[str, Any] | None) -> dict[str, Any]:
    """Validate a caller spec and fill in the defaults it left out.

    Unknown keys are an error. A typo like `itemWidth` would otherwise be
    ignored in silence and the caller would spend the afternoon wondering why
    their sizing had no effect.
    """
    out = dict(DEFAULT_SPEC)
    if spec is None:
        return out
    spec = _require_mapping(spec, "spec")

    unknown = sorted(k for k in spec if k not in DEFAULT_SPEC)
    if unknown:
        raise LayoutError(
            f"spec: unknown key(s) {', '.join(repr(k) for k in unknown)}; "
            f"valid keys are {', '.join(sorted(DEFAULT_SPEC))}"
        )

    for key, value in spec.items():
        where = f"spec.{key}"
        if key == "align":
            if value not in _ALIGNMENTS:
                raise LayoutError(
                    f"{where}: expected one of {_ALIGNMENTS}, got {value!r}"
                )
            out[key] = value
        elif key in _ANY_INT_KEYS:
            out[key] = _as_int(value, where)
        elif key in _POSITIVE_KEYS:
            n = _as_int(value, where)
            if n <= 0:
                raise LayoutError(f"{where}: must be positive, got {n}")
            out[key] = n
        elif key in _NON_NEGATIVE_KEYS:
            n = _as_int(value, where)
            if n < 0:
                raise LayoutError(f"{where}: must not be negative, got {n}")
            out[key] = n
        elif key in _OPTIONAL_POSITIVE_KEYS:
            if value is None:
                out[key] = None
            else:
                n = _as_int(value, where)
                if n <= 0:
                    raise LayoutError(
                        f"{where}: must be positive when given (or None to "
                        f"derive it), got {n}"
                    )
                out[key] = n
        else:  # pragma: no cover - only reachable if a default loses its class
            raise LayoutError(f"{where}: no validation rule for this key")
    return out


def _override(
    holder: Mapping[str, Any],
    key: str,
    spec: Mapping[str, Any],
    allowed: frozenset[str],
    where: str,
) -> Any:
    """Read a per-band / per-lane override, falling back to the spec value."""
    if key not in holder:
        return spec[key]
    if key not in allowed:  # pragma: no cover - guarded by caller's key list
        raise LayoutError(f"{where}.{key}: not overridable per band or lane")
    value = holder[key]
    if value is None and key in _OPTIONAL_POSITIVE_KEYS:
        return None
    n = _as_int(value, f"{where}.{key}")
    if n <= 0:
        raise LayoutError(f"{where}.{key}: must be positive, got {n}")
    return n


def _collect_items(
    raw: Any, where: str, seen: dict[str, str]
) -> list[Mapping[str, Any]]:
    """Validate one band's or lane's item list and its ids.

    Ids must be unique across the whole composition, not just within a band: the
    caller uses them to map rects back onto model elements, and a duplicate
    there means two elements silently sharing one rect.
    """
    items = _require_list(raw, where)
    out: list[Mapping[str, Any]] = []
    for j, raw_item in enumerate(items):
        iwhere = f"{where}[{j}]"
        item = _require_mapping(raw_item, iwhere)
        item_id = item.get("id")
        # Any hashable id is accepted and preserved VERBATIM -- ints as ints,
        # strings as strings. The primary consumer maps these back onto EA
        # element ids, which are integers, so demanding strings would force a
        # str() at every call site and invite the classic "123" != 123 bug when
        # the result is matched back against the model.
        if item_id is None or (isinstance(item_id, str) and not item_id.strip()):
            raise LayoutError(
                f"{iwhere}.id: every item needs a non-empty id, got {item_id!r}"
            )
        try:
            hash(item_id)
        except TypeError:
            raise LayoutError(
                f"{iwhere}.id: item id must be hashable so it can be checked "
                f"for uniqueness, got {type(item_id).__name__}"
            ) from None
        if item_id in seen:
            raise LayoutError(
                f"{iwhere}.id: duplicate item id {item_id!r}, already used at "
                f"{seen[item_id]}"
            )
        seen[item_id] = iwhere
        out.append(item)
    return out


def _named(holder: Mapping[str, Any], where: str) -> str:
    name = holder.get("name")
    if not isinstance(name, str) or not name.strip():
        raise LayoutError(
            f"{where}.name: a non-empty string name is required, got {name!r}"
        )
    return name


def _ceil_div(n: int, d: int) -> int:
    return -(-n // d)


# ---------------------------------------------------------------------------
# Grammar: layered_bands
# ---------------------------------------------------------------------------
def _band_metrics(band: Mapping[str, Any], spec: Mapping[str, Any], where: str) -> dict:
    """Resolve one band's sizing, honoring its own overrides.

    Item size is per band, never per item. Uniform sizing within a band is a
    quality rule: a row of boxes at four different widths reads as four
    different kinds of thing even when it is one kind, and a reader spends
    attention decoding the variation instead of the content.
    """
    item_w = _override(band, "item_width", spec, _BAND_OVERRIDES, where)
    item_h = _override(band, "item_height", spec, _BAND_OVERRIDES, where)
    label_h = _override(band, "label_height", spec, _BAND_OVERRIDES, where)
    wrap_w = _override(band, "wrap_width", spec, _BAND_OVERRIDES, where)

    h_pitch = _override(band, "h_pitch", spec, _BAND_OVERRIDES, where)
    if h_pitch is None:
        h_pitch = item_w + spec["item_gap_x"]
    row_pitch = _override(band, "row_pitch", spec, _BAND_OVERRIDES, where)
    if row_pitch is None:
        row_pitch = item_h + spec["item_gap_y"]

    if h_pitch < item_w:
        raise LayoutError(
            f"{where}: h_pitch ({h_pitch}) is smaller than item_width "
            f"({item_w}); items would overlap"
        )
    if row_pitch < item_h:
        raise LayoutError(
            f"{where}: row_pitch ({row_pitch}) is smaller than item_height "
            f"({item_h}); rows would overlap"
        )
    if wrap_w < item_w:
        raise LayoutError(
            f"{where}: wrap_width ({wrap_w}) is smaller than item_width "
            f"({item_w}); not even one item would fit on a row"
        )
    return {
        "item_width": item_w,
        "item_height": item_h,
        "label_height": label_h,
        "wrap_width": wrap_w,
        "h_pitch": h_pitch,
        "row_pitch": row_pitch,
    }


def compose_layered_bands(
    bands: Sequence[Mapping[str, Any]],
    spec: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Lay out horizontal bands stacked top to bottom.

    `bands` is an ordered list, first band at the top:

        [{"name": "Channels", "items": [{"id": "e1"}, {"id": "e2"}]},
         {"name": "Applications", "items": [...], "item_width": 180}]

    A band may carry `id` (used as its container id) and may override
    `item_width`, `item_height`, `h_pitch`, `row_pitch`, `wrap_width` and
    `label_height` for itself. Items carry `id` (required) and optionally
    `name`, which is passed through to the result.

    Behavior worth knowing:

    * Items run left to right, stepping by `h_pitch`, wrapping to a further row
      once a row would exceed `wrap_width`.
    * Every item in a band is the same size. Different bands may differ.
    * A band's height follows its contents. Bands step down by
      `band_height + band_gap`, or by `band_pitch` if that is larger - which is
      how a configurable vertical pitch and content-driven height coexist.
    * An empty band keeps its label row rather than collapsing to nothing.
    * `align` is "left" (default) or "center". Centered bands are centered
      against the widest band, and their rows are centered within them.

    Returns the result dict described in the module docstring. Raises
    `LayoutError` for any input that cannot yield sane geometry.
    """
    s = _resolve_spec(spec)
    raw_bands = _require_list(bands, "bands")
    if not raw_bands:
        raise LayoutError("bands: at least one band is required, got an empty list")

    pad_x = s["band_pad_x"]
    pad_y = s["band_pad_y"]
    min_band_width = s["min_band_width"]

    seen_ids: dict[str, str] = {}
    plans: list[dict[str, Any]] = []

    for i, raw_band in enumerate(raw_bands):
        where = f"bands[{i}]"
        band = _require_mapping(raw_band, where)
        name = _named(band, where)
        m = _band_metrics(band, s, where)
        items = _collect_items(band.get("items", []), f"{where}.items", seen_ids)

        per_row = (m["wrap_width"] - m["item_width"]) // m["h_pitch"] + 1
        per_row = max(1, per_row)
        row_count = _ceil_div(len(items), per_row) if items else 0

        # Width of the widest row actually used, so a band with two items is
        # not padded out to the wrap width.
        widest_row_items = min(len(items), per_row) if items else 0
        content_width = (
            (widest_row_items - 1) * m["h_pitch"] + m["item_width"]
            if widest_row_items
            else 0
        )
        rows_height = (
            (row_count - 1) * m["row_pitch"] + m["item_height"] if row_count else 0
        )

        floor_width = (
            min_band_width if min_band_width is not None
            else m["item_width"] + 2 * pad_x
        )
        band_width = max(content_width + 2 * pad_x, floor_width)
        # The label strip doubles as the band's top padding; pad_y is the gap
        # below the last row. An empty band therefore still stands label_height
        # + pad_y tall, which is the visible "label row" of an empty band.
        band_height = m["label_height"] + rows_height + pad_y

        plans.append({
            "band": band,
            "name": name,
            "index": i,
            "metrics": m,
            "items": items,
            "per_row": per_row,
            "row_count": row_count,
            "content_width": content_width,
            "band_width": band_width,
            "band_height": band_height,
        })

    widest = max(p["band_width"] for p in plans)
    containers: list[dict[str, Any]] = []
    out_items: list[dict[str, Any]] = []

    band_top = s["origin_top"]
    for p in plans:
        m = p["metrics"]
        if s["align"] == "center":
            band_left = s["origin_left"] + (widest - p["band_width"]) // 2
        else:
            band_left = s["origin_left"]

        band_rect = rect(band_left, band_top, p["band_width"], p["band_height"])
        container = {
            "id": p["band"].get("id") or f"band_{p['index']}",
            "name": p["name"],
            "kind": "band",
            "index": p["index"],
            "label": rect(band_left, band_top, p["band_width"], m["label_height"]),
            **band_rect,
        }
        containers.append(container)

        content_left = band_left + pad_x
        items_top = band_top - m["label_height"]
        for j, item in enumerate(p["items"]):
            row, col = divmod(j, p["per_row"])
            items_this_row = min(p["per_row"], len(p["items"]) - row * p["per_row"])
            row_width = (items_this_row - 1) * m["h_pitch"] + m["item_width"]
            if s["align"] == "center":
                row_left = content_left + (p["content_width"] - row_width) // 2
            else:
                row_left = content_left

            r = rect(
                row_left + col * m["h_pitch"],
                items_top - row * m["row_pitch"],
                m["item_width"],
                m["item_height"],
            )
            record = {
                "id": item["id"],
                "container_id": container["id"],
                "band": p["name"],
                "band_index": p["index"],
                "index": j,
                "row": row,
                "column": col,
                **r,
            }
            if isinstance(item.get("name"), str):
                record["name"] = item["name"]
            out_items.append(record)

        step = p["band_height"] + s["band_gap"]
        if s["band_pitch"] is not None:
            step = max(step, s["band_pitch"])
        band_top -= step

    return {
        "grammar": "layered_bands",
        "items": out_items,
        "containers": containers,
        "bounds": _bounds([*containers, *out_items]),
    }


# ---------------------------------------------------------------------------
# Grammar: lanes
# ---------------------------------------------------------------------------
def _lane_metrics(lane: Mapping[str, Any], spec: Mapping[str, Any], where: str) -> dict:
    """Resolve one lane's item sizing. Uniform within the lane, as with bands."""
    return {
        "item_width": _override(lane, "item_width", spec, _LANE_OVERRIDES, where),
        "item_height": _override(lane, "item_height", spec, _LANE_OVERRIDES, where),
    }


def compose_lanes(
    lanes: Sequence[Mapping[str, Any]],
    spec: Mapping[str, Any] | None = None,
    orientation: str = "horizontal",
) -> dict[str, Any]:
    """Lay out swimlanes: parallel tracks, each carrying a sequence of items.

    `lanes` is an ordered list, first lane at the top (horizontal) or at the
    left (vertical):

        [{"name": "Customer", "items": [{"id": "a1"}, {"id": "a2"}]},
         {"name": "Operations", "items": [{"id": "b1"}]}]

    `orientation` is "horizontal" (lanes stack downward, items flow left to
    right) or "vertical" (lanes sit side by side, items flow downward). A lane
    may carry `id` and may override `item_width` and `item_height`.

    The invariant that earns this grammar its keep: **items at the same sequence
    index across different lanes line up on the flow axis.** Index 2 in every
    lane occupies the same slot, so a handoff from one lane to another reads as
    a step across rather than a step diagonally. Each slot is as long as the
    longest item at that index in any lane, and each item is centered in its
    slot; `slot_start` and `slot_extent` come back on every item so a caller can
    check the alignment itself.

    Other behavior worth knowing:

    * Lane thickness follows the largest item in that lane, across the lane.
    * Items are centered across the lane's thickness.
    * A lane's label area is reserved inside its container rect and returned as
      `label`; the container rect covers the whole lane, label included.
    * `lane_gap` defaults to 0, so lanes abut the way swimlanes normally do.
      Abutting rects touch but do not overlap.
    * An empty lane is valid and still gets a label area and its minimum
      thickness.

    Returns the result dict described in the module docstring. Raises
    `LayoutError` for any input that cannot yield sane geometry.
    """
    if orientation not in _ORIENTATIONS:
        raise LayoutError(
            f"orientation: expected one of {_ORIENTATIONS}, got {orientation!r}"
        )
    s = _resolve_spec(spec)
    raw_lanes = _require_list(lanes, "lanes")
    if not raw_lanes:
        raise LayoutError("lanes: at least one lane is required, got an empty list")

    horizontal = orientation == "horizontal"
    pad = s["lane_pad"]

    seen_ids: dict[str, str] = {}
    plans: list[dict[str, Any]] = []
    for i, raw_lane in enumerate(raw_lanes):
        where = f"lanes[{i}]"
        lane = _require_mapping(raw_lane, where)
        name = _named(lane, where)
        m = _lane_metrics(lane, s, where)
        items = _collect_items(lane.get("items", []), f"{where}.items", seen_ids)
        # Flow extent runs along the lane; cross extent runs across it.
        flow_extent = m["item_width"] if horizontal else m["item_height"]
        cross_extent = m["item_height"] if horizontal else m["item_width"]
        min_thickness = s["min_lane_thickness"]
        if min_thickness is None:
            min_thickness = cross_extent + 2 * pad
        thickness = max(cross_extent + 2 * pad, min_thickness)
        plans.append({
            "lane": lane,
            "name": name,
            "index": i,
            "metrics": m,
            "items": items,
            "flow_extent": flow_extent,
            "cross_extent": cross_extent,
            "thickness": thickness,
        })

    # One global slot table, shared by every lane. This is the alignment.
    slot_count = max(len(p["items"]) for p in plans)
    slot_extents = [
        max(
            (p["flow_extent"] for p in plans if len(p["items"]) > k),
            default=0,
        )
        for k in range(slot_count)
    ]
    slot_starts: list[int] = []
    cursor = 0
    for k, extent in enumerate(slot_extents):
        slot_starts.append(cursor)
        step = extent + s["item_gap_flow"]
        if s["flow_pitch"] is not None:
            step = max(step, s["flow_pitch"])
        cursor += step
    total_flow = (slot_starts[-1] + slot_extents[-1]) if slot_count else 0

    label_along_flow = s["label_width"] if horizontal else s["label_height"]
    lane_length = label_along_flow + pad + total_flow + pad

    containers: list[dict[str, Any]] = []
    out_items: list[dict[str, Any]] = []

    lane_left = s["origin_left"]
    lane_top = s["origin_top"]
    for p in plans:
        m = p["metrics"]
        thickness = p["thickness"]
        if horizontal:
            lane_rect = rect(lane_left, lane_top, lane_length, thickness)
            label = rect(lane_left, lane_top, s["label_width"], thickness)
            flow_origin = lane_left + s["label_width"] + pad
            cross_offset = (thickness - m["item_height"]) // 2
        else:
            lane_rect = rect(lane_left, lane_top, thickness, lane_length)
            label = rect(lane_left, lane_top, thickness, s["label_height"])
            flow_origin = lane_top - s["label_height"] - pad
            cross_offset = (thickness - m["item_width"]) // 2

        container = {
            "id": p["lane"].get("id") or f"lane_{p['index']}",
            "name": p["name"],
            "kind": "lane",
            "index": p["index"],
            "orientation": orientation,
            "label": label,
            **lane_rect,
        }
        containers.append(container)

        for k, item in enumerate(p["items"]):
            start = slot_starts[k]
            extent = slot_extents[k]
            lead = (extent - p["flow_extent"]) // 2  # center the item in its slot
            if horizontal:
                r = rect(
                    flow_origin + start + lead,
                    lane_top - cross_offset,
                    m["item_width"],
                    m["item_height"],
                )
                slot_start_abs = flow_origin + start
            else:
                r = rect(
                    lane_left + cross_offset,
                    flow_origin - start - lead,
                    m["item_width"],
                    m["item_height"],
                )
                slot_start_abs = flow_origin - start
            record = {
                "id": item["id"],
                "container_id": container["id"],
                "lane": p["name"],
                "lane_index": p["index"],
                "index": k,
                "slot_start": slot_start_abs,
                "slot_extent": extent,
                **r,
            }
            if isinstance(item.get("name"), str):
                record["name"] = item["name"]
            out_items.append(record)

        if horizontal:
            lane_top -= thickness + s["lane_gap"]
        else:
            lane_left += thickness + s["lane_gap"]

    return {
        "grammar": "lanes",
        "orientation": orientation,
        "items": out_items,
        "containers": containers,
        "bounds": _bounds([*containers, *out_items]),
    }
