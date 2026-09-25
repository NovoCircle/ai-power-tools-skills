#!/usr/bin/env python3
"""Language bindings: diagram conventions as data.

Every modeling language has its own diagram types, its own sizing and spacing,
its own title convention, its own routing habits, and its own catalog of
standard views. If those live in code, every new notation is an engineering
task and the library never covers more than the few that were hard-coded.

So they live in data - one YAML binding per technology - and this module is the
loader. It validates a binding, resolves `extends`, and translates a diagram
type's conventions into the `spec` dict `compose.py` already takes.

THE LAYER BOUNDARY
------------------
`compose.py` contains no technology name and must not import this module. The
dependency runs one way only: a binding is data that *feeds* the engine. A test
in `test_bindings.py` asserts both halves of that, because a single
`if technology == ...` in the engine would quietly undo the whole design.

WHY `spacing` USES THE ENGINE'S OWN KEY NAMES
---------------------------------------------
The original schema sketch wrote `pitch: {h: 40, v: 70}`. `compose.py`
distinguishes a *gap* (space between two boxes) from a *pitch* (leading edge to
leading edge, so it includes the box), and raises when a pitch is smaller than
the item it must step over. A binding author writing `pitch: 40` next to a
100-wide item has written a layout that cannot be composed - and would not find
out until generation time.

`spacing` is therefore validated against `compose.DEFAULT_SPEC` itself: a
binding can only name a key the engine really has, spelled the way the engine
spells it, so the translation to a spec is the identity and cannot drift. A
binding that says `pitch:` is rejected with the key it probably meant.

MEASURED, NOT ASSUMED
---------------------
The numbers in the shipped bindings were measured from real diagrams rather
than estimated, and the measurements corrected the sketch more than once:

  * BPMN's technology id is `BPMN2.0`, not `BPMN2`, and its diagram type is
    `Business Process` - with a space. A binding keyed on a guessed id resolves
    to nothing, silently, which is the worst failure mode this schema has.
  * EA 17.1's built-in ArchiMate3 MDG names its stereotypes with an
    `ArchiMate_` prefix (`ArchiMate_ApplicationComponent`), and that prefixed
    form is what lands in `t_object.Stereotype`. BPMN2.0 uses no prefix.
    Hence `stereotype_prefix` as data: a binding lists notation concepts the
    way the notation's own specification names them, and the prefix is applied
    to get what EA stores.
  * ArchiMate diagrams are spaced more generously horizontally than
    vertically; BPMN flows are tighter than either. Both were measured from
    element rects, not eyeballed.

PyYAML
------
Bindings are YAML, matching the shipped ArchiMate conformance ruleset, and
PyYAML is loaded the same way `validate_model` loads it: if it is missing, the
error says so and names the install. Loading is always `safe_load`, so a
binding cannot carry executable content - `!!python/object` is refused by the
parser rather than by a check here.
"""
from __future__ import annotations

import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from compose import DEFAULT_SPEC  # noqa: E402

__all__ = [
    "BindingError",
    "Binding",
    "DiagramTypeBinding",
    "Viewpoint",
    "PresentationProfile",
    "GRAMMARS",
    "IMPLEMENTED_GRAMMARS",
    "ROUTE_NAMES",
    "CHANNELS",
    "TITLE_CONVENTIONS",
    "load_binding",
    "load_binding_text",
    "find_binding",
    "available_bindings",
]


class BindingError(ValueError):
    """A binding is not valid.

    The message always names the offending key using its path into the
    document - `diagram_types.Application.channels.fill`,
    `viewpoints.ApplicationCooperation.diagram_type` - so an author can find it
    without guessing. That is the whole point of validating on load: a binding
    with a typo'd route name or a diagram type nothing declares would otherwise
    fail much later, as a diagram that came out wrong.
    """


# ---------------------------------------------------------------------------
# Closed vocabularies
# ---------------------------------------------------------------------------
# The four grammars, and whether `compose.py` can actually compose one. A
# binding is allowed to name a grammar that is not implemented yet - ArchiMate's
# Motivation viewpoints really are trees, and saying `layered-bands` instead
# would be a lie recorded as data. `is_implemented` is how a consumer finds out
# before it tries, rather than after.
GRAMMARS: dict[str, bool] = {
    "layered-bands": True,
    "lanes": True,
    "nested-grid": False,
    "computed-geometry": False,
}
IMPLEMENTED_GRAMMARS = frozenset(k for k, v in GRAMMARS.items() if v)

# Route names as the server accepts them, from EA's own connector right-click >
# Line Style submenu. SOURCE OF TRUTH is `_ROUTE_STYLES` / `_BEZIER_MODE` in
# ea_mcp_server.server; this is a validation copy, so a typo in a binding is
# caught on load instead of at write time.
#
# The skills bundle deliberately does NOT import the server -- it is a separate
# product, and a customer install has no server source on the path -- so the copy
# cannot be derived. `test_route_names_match_the_server` pins it against an
# accidental edit HERE; it cannot see a rename on the server side, which would
# leave both copies agreeing with each other and neither with EA. That drift is
# caught by the server's own generation suite, which takes every route from a
# binding and asserts EA holds it -- but only when that suite runs, since it
# needs a live repository.
ROUTE_NAMES = frozenset({
    "direct",
    "autorouting",
    "customline",
    "treevertical",
    "treehorizontal",
    "lateralvertical",
    "lateralhorizontal",
    "orthogonalsquare",
    "orthogonalrounded",
    "bezier",
})

# Visual channels a diagram can carry a variable in. `channels` exists because
# each notation ALREADY claims some of these; a second variable has to go
# somewhere else, and a binding that lets an agent recolor ArchiMate fills has
# broken the notation while looking like a feature.
CHANNELS = frozenset({
    "fill", "border", "border_width", "line_color", "line_style",
    "font_color", "opacity", "icon", "size", "position",
})

# `drawn`     - the diagram carries a drawn title element on the canvas.
# `frame-header` - EA's own diagram frame supplies it; drawing one would double up.
#
# Recorded per diagram type because neither can be the silent default. Measured
# across the 147-diagram corpus the split tracks notation almost perfectly:
# 13 of 13 ArchiMate diagrams draw a title, 10 of 11 BPMN diagrams rely on the
# frame. (The corpus catalog spells the second one `frame-only`.)
TITLE_CONVENTIONS = ("drawn", "frame-header")

# Presentation-profile keys, from the detail/review/executive scheme. Each maps
# onto a whole-diagram display setting or onto the parallel-connector collapse.
_PROFILE_KEYS = frozenset({
    "connector_labels", "connector_stereotypes", "element_stereotypes",
    "compartments", "notes", "collapse_parallel", "direction_only",
    "description",
})
_COMPARTMENT_VALUES = ("all", "none")

_SPEC_KEYS = frozenset(DEFAULT_SPEC)

_TOP_LEVEL_KEYS = frozenset({
    "technology", "extends", "stereotype_prefix", "display_name", "notes",
    "diagram_types", "viewpoints", "presentation_profiles",
})
_DIAGRAM_TYPE_KEYS = frozenset({
    "grammar", "title", "sizing", "spacing", "routing", "channels", "notes",
    "base",
})
_VIEWPOINT_KEYS = frozenset({
    "diagram_type", "intent", "admits", "grammar", "notes",
})
_ROUTING_KEYS = frozenset({"default", "trunk_for", "notes"})
_CHANNEL_BLOCK_KEYS = frozenset({"fill", "claimed", "free", "notes"})


# ---------------------------------------------------------------------------
# Validation helpers - every one names the path it was given
# ---------------------------------------------------------------------------
def _mapping(value: Any, where: str) -> dict:
    if not isinstance(value, Mapping):
        raise BindingError(
            f"{where}: expected a mapping, got {type(value).__name__}")
    return dict(value)


def _str_list(value: Any, where: str) -> tuple[str, ...]:
    if isinstance(value, str) or not isinstance(value, Sequence):
        raise BindingError(
            f"{where}: expected a list of strings, got "
            f"{type(value).__name__}")
    out = []
    for i, entry in enumerate(value):
        if not isinstance(entry, str) or not entry.strip():
            raise BindingError(
                f"{where}[{i}]: expected a non-empty string, got {entry!r}")
        out.append(entry.strip())
    return tuple(out)


def _text(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BindingError(f"{where}: expected a non-empty string, got {value!r}")
    return value.strip()


def _positive_int(value: Any, where: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise BindingError(
            f"{where}: expected a whole number, got {value!r}")
    if value <= 0:
        raise BindingError(f"{where}: expected a positive number, got {value}")
    return value


def _reject_unknown(present: Mapping, allowed: frozenset, where: str,
                    hints: Mapping[str, str] | None = None) -> None:
    """Refuse keys the schema does not define.

    Silently ignoring an unrecognized key is how a binding ends up not doing
    what its author plainly wrote. `hints` upgrades the common mistakes from
    "unknown key" to "you meant this one".
    """
    unknown = sorted(set(present) - allowed)
    if not unknown:
        return
    hints = hints or {}
    parts = []
    for key in unknown:
        if key in hints:
            parts.append(f"{key!r} ({hints[key]})")
        else:
            parts.append(repr(key))
    raise BindingError(
        f"{where}: unknown key{'s' if len(unknown) > 1 else ''} "
        f"{', '.join(parts)}. Known keys: {', '.join(sorted(allowed))}")


def _normalize_route(name: str) -> str:
    return "".join(ch for ch in str(name).lower() if ch.isalnum())


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------
class PresentationProfile:
    """How much detail a view shows - orthogonal to its diagram type.

    The same content can be duplicated into a second diagram under a different
    profile, giving a live detail view *and* a live executive view of one model
    rather than a screenshot of one of them.
    """

    __slots__ = ("name", "settings")

    def __init__(self, name: str, settings: Mapping[str, Any]):
        self.name = name
        self.settings = dict(settings)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"PresentationProfile({self.name!r}, {self.settings!r})"

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    @property
    def collapses_parallel(self) -> bool:
        return bool(self.settings.get("collapse_parallel", False))

    def display_settings(self) -> dict[str, bool]:
        """Translate to `set_diagram_display` keyword arguments.

        Only the settings this profile actually states are returned, so a
        profile that says nothing about stereotypes leaves them alone rather
        than asserting a default it never chose.

        The polarity flips: a profile says what it *shows*, EA is told what to
        *hide*. That inversion is worth doing in exactly one place.

        WHAT `compartments` CAN AND CANNOT DO
        -------------------------------------
        `compartments: none` does NOT remove the attribute and operation
        compartments. EA's `SuppressedCompartments` was measured through six
        value shapes against a class with attributes and operations and changed
        nothing every time, so there is no verified way to take a compartment
        off. What IS available is reducing its detail to names: attributes read
        as `balance` rather than `balance: Decimal`, operations as `getBalance`
        rather than `getBalance(): Decimal`.

        So `none` and any explicit list both mean "least detail EA will give
        us", and `all` means full detail. That is a smaller promise than the
        profile vocabulary suggests, and saying so here is better than emitting
        a setting that silently does nothing.

        Every key emitted below was verified by rendering against content it
        could bite on. Nothing is emitted on faith.
        """
        out: dict[str, bool] = {}
        if "connector_labels" in self.settings:
            out["hide_connector_labels"] = not self.settings["connector_labels"]
        if "element_stereotypes" in self.settings:
            out["hide_element_stereotypes"] = (
                not self.settings["element_stereotypes"])
        if "connector_stereotypes" in self.settings:
            out["hide_connector_stereotypes"] = (
                not self.settings["connector_stereotypes"])
        if "notes" in self.settings:
            # A SHOW, not a hide: EA does not draw element notes by default, so
            # this is the one setting whose polarity does not flip.
            out["show_element_notes"] = bool(self.settings["notes"])
        if "compartments" in self.settings:
            full_detail = self.settings["compartments"] == "all"
            for key in ("hide_attribute_types", "hide_operation_return_types",
                        "hide_operation_brackets"):
                out[key] = not full_detail
        return out


class DiagramTypeBinding:
    """One diagram type's conventions, ready to hand to the engine."""

    __slots__ = ("technology", "name", "base", "grammar", "title", "sizing",
                 "spacing", "routing", "channels", "notes")

    def __init__(self, technology: str, name: str, data: Mapping[str, Any]):
        self.technology = technology
        self.name = name
        for slot in ("base", "grammar", "title", "notes"):
            setattr(self, slot, data.get(slot, ""))
        self.sizing = dict(data["sizing"])
        self.spacing = dict(data["spacing"])
        self.routing = dict(data["routing"])
        self.channels = dict(data["channels"])

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"DiagramTypeBinding({self.technology}::{self.name})"

    @property
    def mdg_diagram_type(self) -> str:
        """The `MDGDgm=` value EA writes for this diagram type."""
        return f"{self.technology}::{self.name}"

    @property
    def grammar_is_implemented(self) -> bool:
        """Whether `compose.py` can compose this grammar.

        False is a real answer, not an error: the binding is recording what the
        notation does. A consumer that finds False should say so and fall back
        to a plain graph layout rather than composing the wrong shape.
        """
        return GRAMMARS.get(self.grammar, False)

    @property
    def draws_its_own_title(self) -> bool:
        return self.title == "drawn"

    def size_for(self, concept: str = "") -> tuple[int, int]:
        """Box size for a notation concept, falling back to `default`.

        Takes the concept name (`ApplicationComponent`), not the stored
        stereotype (`ArchiMate_ApplicationComponent`); use
        `Binding.concept_for` if you are holding the latter.
        """
        entry = self.sizing.get(concept) or self.sizing["default"]
        return int(entry["w"]), int(entry["h"])

    def claimed_channels(self) -> dict[str, str]:
        """Channel -> what the notation already uses it for."""
        claimed = {}
        fill = self.channels.get("fill")
        if fill:
            claimed["fill"] = fill
        for channel, meaning in (self.channels.get("claimed") or {}).items():
            claimed[channel] = meaning
        return claimed

    def free_channels(self) -> tuple[str, ...]:
        """Channels a second variable may legitimately use."""
        return tuple(self.channels.get("free") or ())

    def channel_is_free(self, channel: str) -> bool:
        return channel in self.free_channels()

    def default_route(self) -> str:
        return self.routing["default"]

    def route_for(self, relationship: str) -> str:
        """The route for a relationship type.

        `trunk_for` names the relationship types this notation habitually draws
        as a shared trunk - ArchiMate's Realization and Aggregation fan into
        one line rather than radiating - so they get the orthogonal route even
        where the diagram type's default is something looser.
        """
        if relationship in (self.routing.get("trunk_for") or ()):
            return self.routing.get("trunk_route", "OrthogonalSquare")
        return self.routing["default"]

    def spec(self, overrides: Mapping[str, Any] | None = None) -> dict:
        """Build a `compose.py` spec from this diagram type's conventions.

        `sizing.default` becomes `item_width`/`item_height`; `spacing` is
        copied across verbatim, because its keys are the engine's own. Caller
        overrides win, so a caller can widen one diagram without editing the
        binding - but an override naming a key the engine does not have is
        refused here rather than by the engine, where the message would not
        mention the binding.
        """
        width, height = self.size_for()
        spec: dict[str, Any] = {"item_width": width, "item_height": height}
        spec.update(self.spacing)
        for key, value in (overrides or {}).items():
            if key not in _SPEC_KEYS:
                raise BindingError(
                    f"spec override {key!r} is not a layout spec key. "
                    f"Known keys: {', '.join(sorted(_SPEC_KEYS))}")
            spec[key] = value
        return spec


class Viewpoint:
    """A standard view the notation itself defines.

    Notations publish their own catalogs - ArchiMate's viewpoints, TOGAF's
    deliverables, UAF's views. Holding that catalog as data is what lets the
    selection logic stay generic instead of growing a branch per notation.
    """

    __slots__ = ("technology", "name", "diagram_type", "intent", "admits",
                 "grammar", "notes")

    def __init__(self, technology: str, name: str, data: Mapping[str, Any]):
        self.technology = technology
        self.name = name
        self.diagram_type = data["diagram_type"]
        self.intent = tuple(data.get("intent") or ())
        self.admits = tuple(data.get("admits") or ())
        self.grammar = data.get("grammar", "")
        self.notes = data.get("notes", "")

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Viewpoint({self.technology}::{self.name})"

    def admits_concept(self, concept: str) -> bool:
        return concept in self.admits

    @property
    def effective_grammar(self) -> str:
        """This viewpoint's own grammar, or `""` to mean its diagram type's.

        A viewpoint override is not decoration. ArchiMate's Capability and
        Organization viewpoints are nested grids drawn on a `Business` diagram
        type whose grammar is `layered-bands`, so a consumer that reads the
        diagram type's grammar and ignores the override composes a capability
        map as bands.
        """
        return self.grammar

    @property
    def grammar_is_implemented(self) -> Optional[bool]:
        """Whether `compose.py` can compose THIS viewpoint's grammar.

        `None` when the viewpoint states no grammar of its own -- ask the
        diagram type instead. The distinction matters: `False` means "we know we
        cannot", `None` means "this viewpoint has no opinion", and returning
        `False` for both would make every ordinary viewpoint look unsupported.

        Without this, the documented path -- rank viewpoints, take one, ask its
        diagram type whether the grammar is implemented -- answers `True` for a
        nested grid and composes it as bands.
        """
        if not self.grammar:
            return None
        return GRAMMARS.get(self.grammar, False)


class Binding:
    """One technology's diagram conventions."""

    __slots__ = ("technology", "display_name", "extends", "stereotype_prefix",
                 "notes", "source", "diagram_types", "viewpoints",
                 "presentation_profiles")

    def __init__(self, data: Mapping[str, Any], source: str = "<memory>"):
        self.source = source
        self.technology = data["technology"]
        self.display_name = data.get("display_name", "") or self.technology
        self.extends = data.get("extends") or None
        self.stereotype_prefix = data.get("stereotype_prefix", "") or ""
        self.notes = data.get("notes", "")
        self.diagram_types = {
            name: DiagramTypeBinding(self.technology, name, body)
            for name, body in data["diagram_types"].items()
        }
        self.viewpoints = {
            name: Viewpoint(self.technology, name, body)
            for name, body in (data.get("viewpoints") or {}).items()
        }
        self.presentation_profiles = {
            name: PresentationProfile(name, body)
            for name, body in (data.get("presentation_profiles") or {}).items()
        }

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Binding({self.technology!r}, {len(self.diagram_types)} types)"

    # -- lookups, all raising rather than returning None ---------------------
    def diagram_type(self, name: str) -> DiagramTypeBinding:
        try:
            return self.diagram_types[name]
        except KeyError:
            raise BindingError(
                f"{self.technology}: no diagram type {name!r}. Declared: "
                f"{', '.join(sorted(self.diagram_types))}") from None

    def viewpoint(self, name: str) -> Viewpoint:
        try:
            return self.viewpoints[name]
        except KeyError:
            raise BindingError(
                f"{self.technology}: no viewpoint {name!r}. Declared: "
                f"{', '.join(sorted(self.viewpoints)) or '(none)'}") from None

    def profile(self, name: str) -> PresentationProfile:
        try:
            return self.presentation_profiles[name]
        except KeyError:
            raise BindingError(
                f"{self.technology}: no presentation profile {name!r}. "
                f"Declared: "
                f"{', '.join(sorted(self.presentation_profiles)) or '(none)'}"
            ) from None

    # -- the prefix problem -------------------------------------------------
    def stereotype_for(self, concept: str) -> str:
        """`ApplicationComponent` -> `ArchiMate_ApplicationComponent`.

        What EA stores in `t_object.Stereotype`. The prefix is per-technology
        data because it is not guessable: EA 17.1's built-in ArchiMate3 MDG
        prefixes, BPMN2.0 does not, and an install carrying a differently built
        MDG can differ again.
        """
        return f"{self.stereotype_prefix}{concept}"

    def concept_for(self, stereotype: str) -> str:
        """The inverse. A stereotype without the prefix is returned unchanged.

        Unchanged rather than rejected: models contain elements stereotyped
        from other technologies, or from none, and a lookup helper is the wrong
        place to have an opinion about that.
        """
        if self.stereotype_prefix and stereotype.startswith(
                self.stereotype_prefix):
            return stereotype[len(self.stereotype_prefix):]
        return stereotype

    def diagram_type_for_mdgdgm(self, mdgdgm: str) -> DiagramTypeBinding | None:
        """Resolve an `MDGDgm=<Tech>::<DiagramType>` value against this binding.

        Returns None when the value names another technology, so a caller can
        try the next binding. Note that only about half of real diagrams carry
        `MDGDgm` at all - the rest identify themselves through `Diagram_Type` -
        so resolution needs a second path, which is `APT-2026-0147`.
        """
        technology, _, diagram_type = str(mdgdgm).partition("::")
        if technology != self.technology:
            return None
        return self.diagram_types.get(diagram_type)

    def viewpoints_admitting(self, concepts: Sequence[str]) -> list[Viewpoint]:
        """Viewpoints that admit every concept given, best coverage first.

        Ranking is on admissibility only. Intent matching and content
        profiling belong to the advisor, not to the data layer.
        """
        wanted = set(concepts)
        matches = [vp for vp in self.viewpoints.values()
                   if wanted <= set(vp.admits)]
        return sorted(matches, key=lambda vp: (len(vp.admits), vp.name))


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def _validate_channels(block: Any, where: str) -> dict:
    channels = _mapping(block, where)
    _reject_unknown(channels, _CHANNEL_BLOCK_KEYS, where)
    if "fill" not in channels:
        raise BindingError(
            f"{where}.fill: required. State what the notation uses fill for, "
            f"or `~` if fill is genuinely unclaimed. This block is the "
            f"mechanized form of 'each notation already claims some visual "
            f"channels', so leaving it out is not a neutral default.")
    fill = channels["fill"]
    if fill is not None and not isinstance(fill, str):
        raise BindingError(
            f"{where}.fill: expected a string describing what fill means, or "
            f"`~`, got {fill!r}")

    claimed = _mapping(channels.get("claimed") or {}, f"{where}.claimed")
    for channel, meaning in claimed.items():
        if channel not in CHANNELS:
            raise BindingError(
                f"{where}.claimed.{channel}: not a visual channel. Known: "
                f"{', '.join(sorted(CHANNELS))}")
        if not isinstance(meaning, str) or not meaning.strip():
            raise BindingError(
                f"{where}.claimed.{channel}: expected a string describing "
                f"what it means, got {meaning!r}")
    if "fill" in claimed:
        raise BindingError(
            f"{where}.claimed.fill: fill is declared by {where}.fill, not "
            f"here. Two places to say one thing is one place too many.")

    free = _str_list(channels.get("free") or [], f"{where}.free")
    for i, channel in enumerate(free):
        if channel not in CHANNELS:
            raise BindingError(
                f"{where}.free[{i}]: {channel!r} is not a visual channel. "
                f"Known: {', '.join(sorted(CHANNELS))}")
    # The one cross-check that matters: a channel cannot be both spoken for and
    # available. A binding that says so has told a consumer it is safe to
    # overwrite something the notation needs.
    spoken_for = set(claimed) | ({"fill"} if fill else set())
    conflict = sorted(spoken_for & set(free))
    if conflict:
        raise BindingError(
            f"{where}.free: {', '.join(repr(c) for c in conflict)} "
            f"{'is' if len(conflict) == 1 else 'are'} already claimed by this "
            f"notation, so listing "
            f"{'it' if len(conflict) == 1 else 'them'} as free would tell a "
            f"consumer it is safe to overwrite the notation's own meaning.")
    if len(set(free)) != len(free):
        raise BindingError(f"{where}.free: contains a duplicate")

    out = {"fill": fill, "free": free, "claimed": claimed}
    if channels.get("notes"):
        out["notes"] = channels["notes"]
    return out


def _validate_sizing(block: Any, where: str) -> dict:
    sizing = _mapping(block, where)
    if "default" not in sizing:
        raise BindingError(
            f"{where}.default: required. Every diagram type needs a fallback "
            f"box size; per-concept entries are refinements of it.")
    out = {}
    for concept, entry in sizing.items():
        path = f"{where}.{concept}"
        size = _mapping(entry, path)
        _reject_unknown(size, frozenset({"w", "h"}), path,
                        {"width": "use 'w'", "height": "use 'h'"})
        for axis in ("w", "h"):
            if axis not in size:
                raise BindingError(f"{path}.{axis}: required")
        out[concept] = {"w": _positive_int(size["w"], f"{path}.w"),
                        "h": _positive_int(size["h"], f"{path}.h")}
    return out


def _validate_spacing(block: Any, where: str) -> dict:
    spacing = _mapping(block or {}, where)
    _reject_unknown(
        spacing, _SPEC_KEYS, where,
        {
            "pitch": "a pitch includes the box it steps over; you probably "
                     "mean item_gap_x / item_gap_y",
            "h": "use item_gap_x",
            "v": "use item_gap_y",
            "gap_x": "use item_gap_x",
            "gap_y": "use item_gap_y",
        },
    )
    # Values are not range-checked here. `compose.py` owns those rules - a
    # pitch smaller than its item, a negative gap - and duplicating them would
    # give two answers that can disagree. What is checked is the key, because
    # an unknown key is the failure the engine cannot see.
    return dict(spacing)


def _validate_routing(block: Any, where: str) -> dict:
    routing = _mapping(block, where)
    _reject_unknown(routing, _ROUTING_KEYS | {"trunk_route"}, where)
    if "default" not in routing:
        raise BindingError(
            f"{where}.default: required. Leaving the route unstated means "
            f"every connector falls back to whatever EA last did, which is "
            f"not a convention.")
    for key in ("default", "trunk_route"):
        if key not in routing:
            continue
        name = _text(routing[key], f"{where}.{key}")
        if _normalize_route(name) not in ROUTE_NAMES:
            raise BindingError(
                f"{where}.{key}: {name!r} is not a route EA accepts. Known: "
                f"Direct, AutoRouting, CustomLine, TreeVertical, "
                f"TreeHorizontal, LateralVertical, LateralHorizontal, "
                f"OrthogonalSquare, OrthogonalRounded, Bezier")
    out = {"default": _text(routing["default"], f"{where}.default")}
    if "trunk_route" in routing:
        out["trunk_route"] = _text(routing["trunk_route"],
                                   f"{where}.trunk_route")
    if "trunk_for" in routing:
        out["trunk_for"] = _str_list(routing["trunk_for"],
                                     f"{where}.trunk_for")
        if "trunk_route" not in out:
            out["trunk_route"] = "OrthogonalSquare"
    if routing.get("notes"):
        out["notes"] = routing["notes"]
    return out


def _validate_diagram_type(name: str, block: Any, where: str) -> dict:
    body = _mapping(block, where)
    _reject_unknown(body, _DIAGRAM_TYPE_KEYS, where)

    grammar = _text(body.get("grammar"), f"{where}.grammar")
    if grammar not in GRAMMARS:
        raise BindingError(
            f"{where}.grammar: {grammar!r} is not one of the four grammars. "
            f"Known: {', '.join(sorted(GRAMMARS))}. The variety of real "
            f"diagrams resolves into these four; if this diagram type "
            f"genuinely needs a fifth, that is a finding, not a binding.")

    title = _text(body.get("title"), f"{where}.title")
    if title not in TITLE_CONVENTIONS:
        raise BindingError(
            f"{where}.title: {title!r} is not a title convention. Known: "
            f"{', '.join(TITLE_CONVENTIONS)}. Neither can be the silent "
            f"default - the corpus splits by notation, so a diagram with two "
            f"titles and a diagram with none are equally likely mistakes.")

    if "sizing" not in body:
        raise BindingError(f"{where}.sizing: required")
    if "routing" not in body:
        raise BindingError(f"{where}.routing: required")
    if "channels" not in body:
        raise BindingError(f"{where}.channels: required")

    out = {
        "grammar": grammar,
        "title": title,
        "sizing": _validate_sizing(body["sizing"], f"{where}.sizing"),
        "spacing": _validate_spacing(body.get("spacing"), f"{where}.spacing"),
        "routing": _validate_routing(body["routing"], f"{where}.routing"),
        "channels": _validate_channels(body["channels"], f"{where}.channels"),
    }
    for optional in ("base", "notes"):
        if body.get(optional):
            out[optional] = _text(body[optional], f"{where}.{optional}")
    return out


def _validate_viewpoint(name: str, block: Any, where: str,
                        diagram_types: Mapping[str, Any]) -> dict:
    body = _mapping(block, where)
    _reject_unknown(body, _VIEWPOINT_KEYS, where)

    diagram_type = _text(body.get("diagram_type"), f"{where}.diagram_type")
    if diagram_type not in diagram_types:
        raise BindingError(
            f"{where}.diagram_type: {diagram_type!r} is not declared by this "
            f"binding. Declared: {', '.join(sorted(diagram_types))}")

    out: dict[str, Any] = {"diagram_type": diagram_type}
    if "intent" in body:
        out["intent"] = _str_list(body["intent"], f"{where}.intent")
    if "admits" in body:
        admits = _str_list(body["admits"], f"{where}.admits")
        if len(set(admits)) != len(admits):
            raise BindingError(f"{where}.admits: contains a duplicate")
        out["admits"] = admits
    if body.get("grammar"):
        grammar = _text(body["grammar"], f"{where}.grammar")
        if grammar not in GRAMMARS:
            raise BindingError(
                f"{where}.grammar: {grammar!r} is not one of the four "
                f"grammars. Known: {', '.join(sorted(GRAMMARS))}")
        out["grammar"] = grammar
    if body.get("notes"):
        out["notes"] = _text(body["notes"], f"{where}.notes")
    return out


def _validate_profile(name: str, block: Any, where: str) -> dict:
    body = _mapping(block, where)
    _reject_unknown(body, _PROFILE_KEYS, where,
                    {"hide_connector_labels":
                     "profiles say what they SHOW; use connector_labels"})
    out: dict[str, Any] = {}
    for key, value in body.items():
        if key in ("description",):
            out[key] = _text(value, f"{where}.{key}")
        elif key == "compartments":
            if isinstance(value, str):
                if value not in _COMPARTMENT_VALUES:
                    raise BindingError(
                        f"{where}.compartments: {value!r} is not "
                        f"{' or '.join(repr(v) for v in _COMPARTMENT_VALUES)}, "
                        f"and not a list of compartment names")
                out[key] = value
            else:
                out[key] = _str_list(value, f"{where}.compartments")
        else:
            if not isinstance(value, bool):
                raise BindingError(
                    f"{where}.{key}: expected true or false, got {value!r}")
            out[key] = value
    # `direction_only` says "show one line per pair, with its direction" - it is
    # meaningless unless something is being collapsed, and a profile that sets
    # it alone reads as if it does something.
    if out.get("direction_only") and not out.get("collapse_parallel"):
        raise BindingError(
            f"{where}.direction_only: only means something under "
            f"collapse_parallel, which this profile does not set.")
    return out


def _validate(doc: Any, source: str) -> dict:
    data = _mapping(doc, source)
    _reject_unknown(data, _TOP_LEVEL_KEYS, source,
                    {"diagramTypes": "use diagram_types",
                     "technology_id": "use technology"})

    technology = _text(data.get("technology"), f"{source}.technology")
    if "::" in technology:
        raise BindingError(
            f"{source}.technology: {technology!r} contains '::'. The "
            f"technology id is the part BEFORE the '::' in an "
            f"`MDGDgm=<Tech>::<DiagramType>` value.")

    if not data.get("diagram_types"):
        raise BindingError(
            f"{source}.diagram_types: required, and must declare at least one "
            f"diagram type")
    raw_types = _mapping(data["diagram_types"], f"{source}.diagram_types")

    out: dict[str, Any] = {
        "technology": technology,
        "extends": data.get("extends") or None,
        "diagram_types": {
            name: _validate_diagram_type(
                name, body, f"{source}.diagram_types.{name}")
            for name, body in raw_types.items()
        },
    }
    if out["extends"] is not None:
        out["extends"] = _text(out["extends"], f"{source}.extends")
        if out["extends"] == technology:
            raise BindingError(
                f"{source}.extends: a binding cannot extend itself")
    # Recorded ONLY when the document declares it, because `""` has to survive
    # as a statement rather than as an absence. A child binding whose install
    # carries an unprefixed build of its parent's technology says so by writing
    # `stereotype_prefix: ""`, and `_merge` must not overwrite that with the
    # parent's prefix. Checked before coercion: `data.get(...) or ""` would turn
    # `0` and `[]` into `""` and pass a type check that never ran.
    if "stereotype_prefix" in data:
        prefix = data["stereotype_prefix"]
        if prefix is None:
            prefix = ""            # `stereotype_prefix: ~` means no prefix
        if not isinstance(prefix, str):
            raise BindingError(
                f"{source}.stereotype_prefix: expected a string or omitted, "
                f"got {prefix!r}")
        out["stereotype_prefix"] = prefix
    for optional in ("display_name", "notes"):
        if data.get(optional):
            out[optional] = _text(data[optional], f"{source}.{optional}")

    out["viewpoints"] = {
        name: _validate_viewpoint(
            name, body, f"{source}.viewpoints.{name}", out["diagram_types"])
        for name, body in _mapping(data.get("viewpoints") or {},
                                   f"{source}.viewpoints").items()
    }
    out["presentation_profiles"] = {
        name: _validate_profile(
            name, body, f"{source}.presentation_profiles.{name}")
        for name, body in _mapping(data.get("presentation_profiles") or {},
                                   f"{source}.presentation_profiles").items()
    }
    return out


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def _yaml():
    try:
        import yaml  # type: ignore
    except ImportError:  # pragma: no cover - environment-dependent
        raise BindingError(
            "PyYAML is required to read a language binding; "
            "pip install pyyaml") from None
    return yaml


def _parse(text: str, source: str) -> Any:
    yaml = _yaml()
    try:
        # safe_load, always. It is why a binding cannot carry executable
        # content: `!!python/object` is refused by the parser, not by a check
        # here that someone could forget to run.
        return yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise BindingError(f"{source}: not valid YAML: {exc}") from None


def load_binding_text(text: str, source: str = "<memory>") -> Binding:
    """Validate and load a binding from YAML text. Used by the tests."""
    return Binding(_validate(_parse(text, source), source), source=source)


def load_binding(path: str | Path, _seen: frozenset[str] = frozenset()
                 ) -> Binding:
    """Load, validate and resolve a binding file.

    `extends` is resolved against the same directory, child keys winning over
    the parent's, so a house binding can restate one diagram type without
    copying the rest. A cycle is refused by name rather than by recursion
    depth.
    """
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise BindingError(f"cannot read binding {path}: {exc}") from None

    source = path.name
    data = _validate(_parse(text, source), source)
    parent_id = data.get("extends")
    if parent_id:
        if parent_id in _seen or data["technology"] in _seen:
            chain = ", ".join(sorted(_seen | {data["technology"]}))
            raise BindingError(
                f"{source}.extends: cycle through {chain}")
        parent_path = _binding_path(parent_id, path.parent)
        if parent_path is None:
            raise BindingError(
                f"{source}.extends: no binding for technology {parent_id!r} "
                f"in {path.parent}")
        parent = load_binding(parent_path,
                              _seen=_seen | {data["technology"]})
        data = _merge(parent, data)
    return Binding(data, source=source)


def _merge(parent: Binding, child: dict) -> dict:
    """Child over parent, one level into each catalog.

    A diagram type the child restates replaces the parent's entirely rather
    than merging field by field. Field-level merging would let a child inherit
    half a convention - a parent's `channels` under a child's `grammar` - which
    is harder to reason about than restating the type.
    """
    merged = dict(child)
    for catalog, attribute in (("diagram_types", "diagram_types"),
                                 ("viewpoints", "viewpoints"),
                                 ("presentation_profiles",
                                  "presentation_profiles")):
        inherited = {
            name: _unwrap(value)
            for name, value in getattr(parent, attribute).items()
        }
        inherited.update(child.get(catalog) or {})
        merged[catalog] = inherited
    # `not merged.get(...)` cannot tell `""` from absent, and the difference is
    # load-bearing: a child that declares `stereotype_prefix: ""` is stating that
    # ITS technology has no prefix, and silently inheriting the parent's would
    # make every stereotype lookup miss without complaining.
    if "stereotype_prefix" not in merged:
        merged["stereotype_prefix"] = parent.stereotype_prefix
    return merged


def _unwrap(value: Any) -> Any:
    """Turn a parent's loaded object back into the dict form `Binding` takes."""
    if isinstance(value, DiagramTypeBinding):
        out = {"grammar": value.grammar, "title": value.title,
               "sizing": value.sizing, "spacing": value.spacing,
               "routing": value.routing, "channels": value.channels}
        for optional in ("base", "notes"):
            if getattr(value, optional):
                out[optional] = getattr(value, optional)
        return out
    if isinstance(value, Viewpoint):
        out = {"diagram_type": value.diagram_type}
        for name in ("intent", "admits", "grammar", "notes"):
            if getattr(value, name):
                out[name] = getattr(value, name)
        return out
    if isinstance(value, PresentationProfile):
        return dict(value.settings)
    return value  # pragma: no cover - defensive


def _bindings_dir(directory: str | Path | None = None) -> Path:
    if directory is not None:
        return Path(directory)
    return _HERE.parent / "bindings"


def _slug(technology: str) -> str:
    """`BPMN2.0` -> `bpmn2.0`. The id is authoritative; the filename is a slug.

    Lowercased and with path separators and spaces flattened, so a technology
    id containing `/` (several UAF ids do) cannot escape the bindings
    directory.
    """
    out = []
    for ch in technology.strip().lower():
        out.append(ch if (ch.isalnum() or ch in "._-") else "-")
    return "".join(out).strip("-") or "binding"


def _binding_path(technology: str, directory: Path) -> Path | None:
    candidate = directory / f"{_slug(technology)}.yaml"
    if candidate.is_file():
        return candidate
    # Fall back to reading each binding's declared id, which is authoritative -
    # a file named anything at all still binds the technology it says it does.
    for path in sorted(directory.glob("*.yaml")):
        try:
            doc = _parse(path.read_text(encoding="utf-8"), path.name)
        except (BindingError, OSError):
            continue
        if isinstance(doc, Mapping) and doc.get("technology") == technology:
            return path
    return None


def find_binding(technology: str,
                 directory: str | Path | None = None) -> Binding | None:
    """Load the binding for a technology id, or None if there is not one.

    None rather than an exception: not having a binding for a technology is
    normal - most repositories use several we have never bound - and a caller
    should say so and fall back, not crash. What must NOT happen is composing
    against the wrong binding, which is why the declared `technology` is
    checked rather than trusting the filename.
    """
    directory = _bindings_dir(directory)
    if not directory.is_dir():
        return None
    path = _binding_path(technology, directory)
    if path is None:
        return None
    binding = load_binding(path)
    if binding.technology != technology:  # pragma: no cover - defensive
        return None
    return binding


def available_bindings(directory: str | Path | None = None) -> dict[str, str]:
    """`{technology id: filename}` for every valid binding on hand.

    Invalid bindings are omitted rather than raising, so one bad file does not
    make the whole catalog unreadable; load it directly to see why.
    """
    directory = _bindings_dir(directory)
    if not directory.is_dir():
        return {}
    out = {}
    for path in sorted(directory.glob("*.yaml")):
        try:
            binding = load_binding(path)
        except BindingError:
            continue
        out[binding.technology] = path.name
    return out
