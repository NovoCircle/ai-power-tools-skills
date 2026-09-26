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

`compose_nested_grid` - containers within containers, each laid out as a grid of
its children. Containment is the only structure; there is no sequence and
usually no connectors. This is the one that takes a recursive tree rather than a
flat list of groups.

`compose_radial` - a hub and its spokes: items distributed on a ring around a
center, optionally with a further ring hanging off each one. The one grammar
here whose arithmetic is trigonometric, so it is also the one that has to be
careful about rounding: coordinates are rounded once, at the end, so the same
ring comes out identically on every machine.

All four take plain lists of dicts and return plain dicts. No classes to
construct, nothing to subclass.

Result shape
------------
    {
      "grammar":    "layered_bands" | "lanes" | "nested_grid" | "radial",
      "items":      [ {"id", "left", "top", "right", "bottom", ...}, ... ],
      "containers": [ {"id", "name", "kind", "index", "left", "top", "right",
                       "bottom", "label": {...}}, ... ],
      "bounds":     {"left", "top", "right", "bottom", "width", "height"},
    }

`items` are nested inside their `containers` by design, so test the two sets for
mutual disjointness separately - an item is supposed to sit inside its band.

For `nested_grid`, containers nest inside CONTAINERS too, so even the container
set is not mutually disjoint there: compare siblings, not the whole set.

`radial` returns no containers at all, and an item's `container_id` names the
ITEM it hangs from - the hub, or the spoke it branches off. It also carries
`center` and the `radius` actually used, which can exceed the one asked for.
"""
from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any, Optional

__all__ = [
    "LayoutError",
    "DEFAULT_SPEC",
    "compose_layered_bands",
    "compose_lanes",
    "compose_nested_grid",
    "compose_radial",
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

    # Nested-grid containers. `grid_pad` is constant on every side; the top
    # inset is `grid_pad + label_height`, so the title strip is cleared rather
    # than being what the padding is made of.
    #
    # Same shape as the container arithmetic documented in the
    # `ea-navigation-diagrams` skill (PAD_L/R, PAD_T "room for the container's
    # own title", PAD_B), with the pads parameterized instead of fixed at
    # 45/60/40 and PAD_T decomposed into `label_height + grid_pad`. If that
    # skill's numbers are ever revised, these are the knobs that express them.
    "grid_pad": 12,
    "grid_columns": None,     # None -> ceil(sqrt(n)), which keeps a grid squarish
    "max_grid_depth": 3,      # levels of containment allowed; deeper is REFUSED

    # Radial rings. `radius` is a FLOOR: a ring whose items would collide at
    # that distance is widened until they do not, and the radius actually used
    # comes back on the result.
    "radius": 220,
    "start_angle": 0,         # degrees clockwise from twelve o'clock
    "sweep": 360,             # how much of the circle to use
    "max_ring_depth": 2,      # rings allowed; deeper is REFUSED
}

# `start_angle` may legitimately be negative or zero: it is a bearing, not a
# size, and "start at ten o'clock" is -60.
_ANY_INT_KEYS = frozenset({"origin_left", "origin_top", "start_angle"})
_POSITIVE_KEYS = frozenset({
    "item_width", "item_height", "wrap_width", "label_height", "label_width",
    "max_grid_depth", "radius", "sweep", "max_ring_depth",
})
_NON_NEGATIVE_KEYS = frozenset({
    "item_gap_x", "item_gap_y", "item_gap_flow",
    "band_pad_x", "band_pad_y", "band_gap", "lane_pad", "lane_gap",
    "grid_pad",
})
_OPTIONAL_POSITIVE_KEYS = frozenset({
    "h_pitch", "row_pitch", "band_pitch", "flow_pitch",
    "min_band_width", "min_lane_thickness",
    "grid_columns",
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

# What one nested-grid container may restate for its OWN DIRECT CHILDREN. It
# does not cascade to grandchildren: each level states its own sizing, which is
# what "levels may differ, siblings may not" means in practice.
_GRID_OVERRIDES = frozenset({
    "item_width", "item_height", "label_height", "grid_columns",
})

# What one radial node may restate for its OWN ring.
_RADIAL_OVERRIDES = frozenset({"item_width", "item_height", "radius"})

# The widest arc a branch may occupy. Without a cap, a two-item ring gives each
# branch 180 degrees and the outer items sweep back across the center.
_MAX_BRANCH_SWEEP = 120.0


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
        out.append(_check_item(raw_item, f"{where}[{j}]", seen))
    return out


def _check_item(
    raw_item: Any, iwhere: str, seen: dict[str, str]
) -> Mapping[str, Any]:
    """Validate one item and claim its id. Shared by all three grammars.

    Pulled out of `_collect_items` so the nested grid, which meets its items one
    at a time while walking a tree rather than as a flat list, claims ids from
    the same registry with the same messages. Two grammars enforcing id
    uniqueness two ways is how one of them ends up not enforcing it.
    """
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
    return item


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


# ---------------------------------------------------------------------------
# Grammar: nested_grid
# ---------------------------------------------------------------------------
def _grid_metrics(
    node: Mapping[str, Any], spec: Mapping[str, Any], where: str
) -> dict:
    """Resolve the sizing one grid level applies to its own direct children.

    Held on the PARENT, never on the child, which is what makes "uniform within
    a level" structural rather than a rule a caller has to remember: a leaf has
    nowhere to state a size of its own, so siblings cannot disagree.
    """
    return {
        "item_width": _override(node, "item_width", spec, _GRID_OVERRIDES, where),
        "item_height": _override(node, "item_height", spec, _GRID_OVERRIDES, where),
        "label_height": _override(node, "label_height", spec, _GRID_OVERRIDES, where),
        "grid_columns": _override(node, "grid_columns", spec, _GRID_OVERRIDES, where),
    }


def _near_square_columns(n: int) -> int:
    """Columns for `n` cells so the grid comes out close to square.

    `ceil(sqrt(n))`, computed with integers because floating point at the
    boundary would make a 16-cell grid 5 columns wide on some machines and 4 on
    others, and this module promises the same output everywhere.
    """
    c = 1
    while c * c < n:
        c += 1
    return c


def _plan_grid(
    raw_children: Any,
    where: str,
    level: int,
    s: Mapping[str, Any],
    metrics: Mapping[str, Any],
    seen_items: dict[str, str],
    seen_groups: dict[str, str],
) -> dict[str, Any]:
    """Measure one grid bottom-up, returning its natural size and child plans.

    Recursive: a child carrying `items` is a container, and its natural size is
    whatever its own grid needs plus padding. Nothing is placed here - the tree
    has to be measured from the leaves up before anything can be positioned,
    because a container's size is its content's size.
    """
    children = _require_list(raw_children, where)
    plans: list[dict[str, Any]] = []

    for k, raw in enumerate(children):
        cwhere = f"{where}[{k}]"
        child = _require_mapping(raw, cwhere)
        # The presence of the `items` KEY is the discriminator, not its
        # truthiness: `items: []` is a deliberately empty container, and a
        # container that collapsed into a leaf when its last child was removed
        # would be a diagram that silently changed shape.
        if "items" in child:
            if level > s["max_grid_depth"]:
                raise LayoutError(
                    f"{cwhere}: nesting is {level} containers deep, and this "
                    f"grammar refuses more than max_grid_depth "
                    f"({s['max_grid_depth']}); past about three levels a reader "
                    f"can no longer tell which box owns which. Split the "
                    f"diagram, or raise spec.max_grid_depth deliberately"
                )
            name = _named(child, cwhere)
            group_id = child.get("id")
            if group_id is not None:
                if group_id in seen_groups:
                    raise LayoutError(
                        f"{cwhere}.id: duplicate container id {group_id!r}, "
                        f"already used at {seen_groups[group_id]}"
                    )
                if group_id in seen_items:
                    raise LayoutError(
                        f"{cwhere}.id: container id {group_id!r} is already "
                        f"used by an item at {seen_items[group_id]}; containers "
                        f"and items are both mapped back onto model elements, "
                        f"so one id cannot mean both"
                    )
                seen_groups[group_id] = cwhere
            cm = _grid_metrics(child, s, cwhere)
            inner = _plan_grid(
                child.get("items"), f"{cwhere}.items", level + 1, s, cm,
                seen_items, seen_groups,
            )
            plans.append({
                "kind": "container",
                "node": child,
                "name": name,
                "index": k,
                "metrics": cm,
                "inner": inner,
                "width": inner["grid_width"] + 2 * s["grid_pad"],
                "height": (cm["label_height"] + inner["grid_height"]
                           + 2 * s["grid_pad"]),
            })
        else:
            item = _check_item(child, cwhere, seen_items)
            plans.append({
                "kind": "item",
                "node": item,
                "index": k,
                "width": metrics["item_width"],
                "height": metrics["item_height"],
            })

    n = len(plans)
    if n:
        columns = metrics["grid_columns"]
        if columns is None:
            columns = _near_square_columns(n)
        columns = max(1, min(columns, n))
        rows = _ceil_div(n, columns)
        col_widths = [0] * columns
        row_heights = [0] * rows
        for k, p in enumerate(plans):
            r, c = divmod(k, columns)
            col_widths[c] = max(col_widths[c], p["width"])
            row_heights[r] = max(row_heights[r], p["height"])
        grid_width = sum(col_widths) + (columns - 1) * s["item_gap_x"]
        grid_height = sum(row_heights) + (rows - 1) * s["item_gap_y"]
    else:
        # An empty container keeps one cell's worth of space, so it stays a
        # visible labeled box that says "this grouping exists and is
        # deliberately unpopulated" instead of collapsing to its title.
        columns = rows = 0
        col_widths = []
        row_heights = []
        grid_width = metrics["item_width"]
        grid_height = metrics["item_height"]

    return {
        "plans": plans,
        "columns": columns,
        "rows": rows,
        "col_widths": col_widths,
        "row_heights": row_heights,
        "grid_width": grid_width,
        "grid_height": grid_height,
    }


def _place_grid(
    grid: Mapping[str, Any],
    left: int,
    top: int,
    s: Mapping[str, Any],
    metrics: Mapping[str, Any],
    depth: int,
    parent_id: Any,
    path: str,
    containers: list[dict[str, Any]],
    out_items: list[dict[str, Any]],
) -> None:
    """Place one already-measured grid with its content box at (`left`, `top`).

    Column widths and row heights come from the measure pass, so a container
    fills its cell and a leaf keeps its exact size centered in its cell. That
    split is the whole quality decision here: stretching leaves to their
    column's width would align the edges at the cost of the uniform-sizing rule,
    and the rule wins.
    """
    columns = grid["columns"]
    for k, p in enumerate(grid["plans"]):
        r, c = divmod(k, columns)
        cell_left = left + sum(grid["col_widths"][:c]) + c * s["item_gap_x"]
        cell_top = top - (sum(grid["row_heights"][:r]) + r * s["item_gap_y"])
        cell_w = grid["col_widths"][c]
        cell_h = grid["row_heights"][r]

        if p["kind"] == "container":
            cm = p["metrics"]
            child_path = f"{path}{k}"
            group_id = p["node"].get("id") or f"group_{child_path}"
            # A container keeps the size its CONTENTS need and is anchored at
            # its cell's top-left; it does not stretch to fill the cell. That
            # is the corpus's rule and it is worth the ragged edge it produces:
            # containers sized alike make a grouping of two look as important
            # as a grouping of twenty, which is the failure this grammar is
            # most often accused of. Snapping every container to its cell drew
            # a four-child capability and a two-child one at exactly the same
            # 324x192 -- tidier, and wrong about the thing the diagram is for.
            #
            # Leaves are the opposite case and stay centered in their cells:
            # they carry no content of their own to be sized by, so uniformity
            # is the only honest size for them.
            group_rect = rect(cell_left, cell_top, p["width"], p["height"])
            containers.append({
                "id": group_id,
                "name": p["name"],
                "kind": "group",
                "index": p["index"],
                "depth": depth,
                "parent_id": parent_id,
                "row": r,
                "column": c,
                "label": rect(cell_left, cell_top, p["width"],
                              cm["label_height"]),
                **group_rect,
            })
            _place_grid(
                p["inner"],
                cell_left + s["grid_pad"],
                cell_top - cm["label_height"] - s["grid_pad"],
                s, cm, depth + 1, group_id, f"{child_path}_",
                containers, out_items,
            )
        else:
            item_w = metrics["item_width"]
            item_h = metrics["item_height"]
            placed = rect(
                cell_left + (cell_w - item_w) // 2,
                cell_top - (cell_h - item_h) // 2,
                item_w,
                item_h,
            )
            record = {
                "id": p["node"]["id"],
                "container_id": parent_id,
                "depth": depth,
                "index": p["index"],
                "row": r,
                "column": c,
                **placed,
            }
            if isinstance(p["node"].get("name"), str):
                record["name"] = p["node"]["name"]
            out_items.append(record)


def compose_nested_grid(
    nodes: Sequence[Mapping[str, Any]],
    spec: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Lay out containers within containers, each as a grid of its children.

    `nodes` is the top level of a recursive tree. A node carrying `items` is a
    container and needs a `name`; a node without `items` is a leaf and needs an
    `id`:

        [{"name": "Retail", "items": [
            {"name": "Onboarding", "items": [{"id": 101}, {"id": 102}]},
            {"id": 103}]},
         {"name": "Payments", "items": [{"id": 104}]}]

    Containment is the only structure this grammar expresses. There is no
    sequence and usually no connectors - a nesting that also needs arrows to be
    read is a graph, and one of the other grammars or EA's own layout will serve
    it better.

    Behavior worth knowing:

    * **Grids come out close to square** - `ceil(sqrt(n))` columns - because a
      grouping rendered as one long row reads as a list and loses the grouping.
      Set `grid_columns` to fix a count; a container may set its own.
    * **Cell sizing is uniform within a level and may differ between levels.**
      Item size is stated by the PARENT (`item_width`, `item_height`, overridable
      per container for its own direct children, not cascading), so sibling
      leaves cannot disagree about their size - the one thing that most makes a
      generated diagram look machine-made.
    * **Containers are sized by their contents and nothing else.** A container
      with twenty children is visibly bigger than one with two - which is the
      whole point of drawing the grouping - so a container is NOT stretched to
      fill its cell, and a row of containers can end at different depths. Cells
      are still sized by the widest and tallest member of their column and row,
      so siblings never collide; the slack simply stays empty. A leaf keeps its
      exact size, centered in its cell.
    * **Padding is constant** (`grid_pad`) on every side, with the title strip
      (`label_height`) as an extra inset at the top, so a container's own name
      never sits on top of its children.
    * **Depth is bounded and a deeper tree is REFUSED**, not warned about:
      `max_grid_depth` defaults to 3 levels of containment. A warning would need
      a channel in the result that nothing reads; an error names the offending
      path, and a caller who genuinely wants four levels raises the bound
      deliberately. Leaves may sit at any level, including inside the deepest
      container.
    * An empty container keeps its label and one cell of space rather than
      collapsing, so the emptiness is visible and the author has to mean it.

    Item ids must be unique across the whole tree, as in the other grammars, and
    a container `id` may not collide with another container's or with an item's -
    both are mapped back onto model elements. Root-level leaves come back with
    `container_id: None`, since nothing encloses them.

    Returns the result dict described in the module docstring, with `depth`,
    `row`, `column` and `parent_id` on containers and `depth`, `row`, `column`
    and `container_id` on items. Raises `LayoutError` for any input that cannot
    yield sane geometry.
    """
    s = _resolve_spec(spec)
    raw_nodes = _require_list(nodes, "nodes")
    if not raw_nodes:
        raise LayoutError("nodes: at least one node is required, got an empty list")

    root_metrics = {
        "item_width": s["item_width"],
        "item_height": s["item_height"],
        "label_height": s["label_height"],
        "grid_columns": s["grid_columns"],
    }
    seen_items: dict[str, str] = {}
    seen_groups: dict[str, str] = {}
    grid = _plan_grid(nodes, "nodes", 1, s, root_metrics, seen_items, seen_groups)

    containers: list[dict[str, Any]] = []
    out_items: list[dict[str, Any]] = []
    _place_grid(
        grid, s["origin_left"], s["origin_top"], s, root_metrics,
        1, None, "", containers, out_items,
    )

    return {
        "grammar": "nested_grid",
        "items": out_items,
        "containers": containers,
        "bounds": _bounds([*containers, *out_items]),
    }


# ---------------------------------------------------------------------------
# Grammar: radial
# ---------------------------------------------------------------------------
def _ring_metrics(node: Mapping[str, Any], spec: Mapping[str, Any],
                  where: str) -> dict:
    """Resolve the sizing one ring applies to its own children."""
    return {
        "item_width": _override(node, "item_width", spec, _RADIAL_OVERRIDES, where),
        "item_height": _override(node, "item_height", spec, _RADIAL_OVERRIDES, where),
        "radius": _override(node, "radius", spec, _RADIAL_OVERRIDES, where),
    }


def _polar(center_x: int, center_y: int, radius: int, degrees: float) -> tuple:
    """A point on a circle, rounded to whole EA units.

    Angles run CLOCKWISE from twelve o'clock, because that is how a reader
    describes one of these diagrams - "starting at the top and going round" -
    and matching the description costs nothing here while saving an inversion
    at every call site.

    EA's vertical axis is inverted, so a point ABOVE the center has a LARGER
    (less negative) y. Rounding is `int(round(...))`, applied once, to the
    coordinate rather than to the angle: rounding the angle first would let a
    ring of twelve drift visibly by the time it closed.
    """
    radians = math.radians(degrees - 90.0)
    return (int(round(center_x + radius * math.cos(radians))),
            int(round(center_y - radius * math.sin(radians))))


def compose_radial(
    nodes: Sequence[Mapping[str, Any]],
    spec: Mapping[str, Any] | None = None,
    hub: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """Lay out items on a ring around a center: a hub and its spokes.

    `nodes` is the ring, in order. `hub`, when given, is the thing at the
    center - `{"id": ..., "name": ...}` - and is placed as an item rather than
    as a container, because it is one of the things on the diagram rather than
    something enclosing them:

        compose_radial(
            [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}],
            hub={"id": 100, "name": "Customer"},
        )

    A node carrying `items` gets its own outer ring, laid out over the arc it
    occupies, which is what turns a hub-and-spoke into a radial tree.

    Behavior worth knowing:

    * **Angles run clockwise from twelve o'clock**, which is how a reader
      describes one of these. `start_angle` moves the first item.
    * **`sweep` is how much of the circle to use**, 360 by default. A smaller
      sweep gives a fan rather than a ring, and the items are spread across it
      INCLUSIVE of both ends - a 180-degree sweep of three items puts one at
      each end and one in the middle, which is what a half-circle of three is
      meant to look like. A full circle does not repeat the first position.
    * **Uniform sizing within a ring.** Stated by the parent, so siblings
      cannot disagree - the same rule the other grammars follow.
    * **The radius is a floor, not a promise.** If the items would collide at
      the radius given, the ring is widened until they do not, and the radius
      actually used comes back on the result. A grammar that produced a
      deliberately overlapping ring because the caller passed a small number
      would be obeying the letter of the spec and drawing a bad diagram.
    * **Depth is bounded** by `max_ring_depth`, default 2, and a deeper tree is
      REFUSED rather than warned about - the same decision the nested grid
      makes, for the same reason: the result dict has no channel a warning
      could travel down that anything reads.

    THE CONNECTORS ARE NOT THIS GRAMMAR'S JOB, and for these diagrams that
    matters more than usual. Reference radial diagrams commonly use curved or
    arced connectors; the routing vocabulary available here has no arc, so a
    generated equivalent will carry straight or Bezier lines. The geometry is
    equivalent; the drawing is not identical, and saying so is part of using
    this grammar honestly.

    Returns the result dict described in the module docstring. Items carry
    `angle` and `ring`, so a caller can reason about the arrangement without
    recovering it from coordinates. Raises `LayoutError` for any input that
    cannot yield sane geometry.
    """
    s = _resolve_spec(spec)
    raw_nodes = _require_list(nodes, "nodes")
    if not raw_nodes:
        raise LayoutError("nodes: at least one node is required, got an empty list")

    seen_ids: dict[str, str] = {}
    out_items: list[dict[str, Any]] = []

    hub_item = None
    if hub is not None:
        hub_item = _check_item(hub, "hub", seen_ids)

    # The center is chosen after the outermost radius is known, so the whole
    # composition can start at `origin_left`/`origin_top` like every other
    # grammar rather than at a center the caller has to compute.
    plan = _plan_ring(raw_nodes, "nodes", 1, s, seen_ids, float(s["sweep"]))
    extent = plan["outer_radius"] + max(plan["max_item_w"], plan["max_item_h"])
    center_x = s["origin_left"] + extent
    center_y = s["origin_top"] - extent

    if hub_item is not None:
        record = {
            "id": hub_item["id"],
            "container_id": None,
            "ring": 0,
            "angle": 0.0,
            "index": 0,
            **rect(center_x - s["item_width"] // 2,
                   center_y + s["item_height"] // 2,
                   s["item_width"], s["item_height"]),
        }
        if isinstance(hub_item.get("name"), str):
            record["name"] = hub_item["name"]
        out_items.append(record)

    _place_ring(plan, center_x, center_y, s, 1,
                hub_item["id"] if hub_item else None,
                s["start_angle"], s["sweep"], out_items)

    return {
        "grammar": "radial",
        "items": out_items,
        "containers": [],
        "center": {"x": center_x, "y": center_y},
        "radius": plan["radius"],
        "bounds": _bounds(out_items),
    }


def _plan_ring(raw_nodes: Any, where: str, level: int, s: Mapping[str, Any],
               seen_ids: dict, sweep: float) -> dict:
    """Measure one ring and everything outside it, from the inside out.

    The SWEEP has to be known here, not only at placement, because it decides
    the angular step and therefore how far apart the items actually are. The
    first version widened the radius using the full-circle step on the reasoning
    that a closed ring is the tightest case. It is not: five items across a
    90-degree fan step 22.5 degrees apart where a full circle would step 72, so
    the fan collided while the ring was fine. Planning and placement now derive
    the angles from one function so they cannot disagree.
    """
    if level > s["max_ring_depth"]:
        raise LayoutError(
            f"{where}: nesting is {level} rings deep, and this grammar refuses "
            f"more than max_ring_depth ({s['max_ring_depth']}); a radial "
            f"diagram past two rings stops being readable from the center. "
            f"Split it, or raise spec.max_ring_depth deliberately"
        )
    children = _require_list(raw_nodes, where)
    if not children:
        raise LayoutError(f"{where}: a ring needs at least one node")

    metrics = {
        "item_width": s["item_width"],
        "item_height": s["item_height"],
        "radius": s["radius"],
    }
    plans = []
    for k, raw in enumerate(children):
        cwhere = f"{where}[{k}]"
        node = _require_mapping(raw, cwhere)
        raw_inner = node.get("items") if "items" in node else None
        item = _check_item(node, cwhere, seen_ids)
        plans.append({"node": item, "index": k, "inner": None,
                      "raw_inner": raw_inner, "where": cwhere})

    count = len(plans)
    step = _angular_step(count, sweep)
    branch_sweep = min(abs(step) or abs(sweep), _MAX_BRANCH_SWEEP)

    # The radius is a floor. Widen it until neighbours on this ring cannot
    # touch: the chord between two of them, at the step actually used, must
    # clear the wider extent plus a gap.
    need = max(metrics["item_width"], metrics["item_height"]) + s["item_gap_x"]
    radius = metrics["radius"]
    if count > 1 and step:
        half = math.radians(abs(step) / 2.0)
        if math.sin(half) > 0:
            radius = max(radius, int(math.ceil(need / (2.0 * math.sin(half)))))

    for entry in plans:
        if entry["raw_inner"] is not None:
            entry["inner"] = _plan_ring(
                entry["raw_inner"], f"{entry['where']}.items",
                level + 1, s, seen_ids, branch_sweep)

    outer = radius
    for entry in plans:
        if entry["inner"]:
            outer = max(outer, radius + entry["inner"]["outer_radius"])
    return {
        "plans": plans,
        "radius": radius,
        "outer_radius": outer,
        "metrics": metrics,
        "step": step,
        "branch_sweep": branch_sweep,
        "max_item_w": metrics["item_width"],
        "max_item_h": metrics["item_height"],
    }


def _angular_step(count: int, sweep: float) -> float:
    """Degrees between neighbours on a ring of `count` over `sweep`.

    A closed ring divides by the count, so the last item does not land back on
    the first. A partial sweep divides by one less, spreading the items
    INCLUSIVE of both ends - a half circle of three is one at each end and one
    in the middle, which is what a half circle of three should look like.
    """
    if count <= 1:
        return 0.0
    if abs(sweep) >= 360.0:
        return sweep / count
    return sweep / (count - 1)


def _place_ring(plan: Mapping[str, Any], center_x: int, center_y: int,
                s: Mapping[str, Any], ring: int, parent_id: Any,
                start_angle: float, sweep: float,
                out_items: list) -> None:
    """Place one measured ring, then anything hanging off it."""
    plans = plan["plans"]
    metrics = plan["metrics"]
    radius = plan["radius"]
    # The step was decided during planning, because the radius depends on it.
    step = plan["step"]

    for entry in plans:
        angle = start_angle + step * entry["index"]
        x, y = _polar(center_x, center_y, radius, angle)
        record = {
            "id": entry["node"]["id"],
            "container_id": parent_id,
            "ring": ring,
            "angle": round(angle % 360.0, 3),
            "index": entry["index"],
            **rect(x - metrics["item_width"] // 2,
                   y + metrics["item_height"] // 2,
                   metrics["item_width"], metrics["item_height"]),
        }
        if isinstance(entry["node"].get("name"), str):
            record["name"] = entry["node"]["name"]
        out_items.append(record)

        if entry["inner"]:
            # An outer ring is centered on its parent and occupies the arc the
            # parent owns, so a radial tree's branches do not interleave.
            own_sweep = plan["branch_sweep"]
            inner_count = len(entry["inner"]["plans"])
            branch_start = angle - own_sweep / 2.0 if inner_count > 1 else angle
            _place_ring(entry["inner"], x, y, s, ring + 1,
                        entry["node"]["id"], branch_start, own_sweep,
                        out_items)
