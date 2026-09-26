# Verification — checking a diagram you generated

Generating a diagram is half the job. This file is the other half: what to check, what the check
can and cannot see, and how to stop.

The loop is **compose → place → style → route → verify → lint → correct**, and it is bounded. Three
correction passes, then you report what is left. A loop that runs until it is satisfied either
terminates or lies about having finished.

---

## 1. The stale-render trap — read this before anything else

**EA caches a diagram's render.** If the underlying rows changed since EA last drew it — a direct
SQL write, a placement made from a different process or a different session — asking for the image
can return the previous one. It looks plausible. It is not the diagram you just built.

A check that skips the reload **certifies a diagram it never saw.**

`verify_diagram` reloads unconditionally and has no flag to skip it, deliberately: the one thing a
verification step must not offer is a faster mode that invalidates the verification. Use it rather
than `get_diagram_png` or `get_diagram_svg` when the point is to *check* something.

Those two are the right calls when you already trust the state and just want the picture, and both
take `refresh=True` when you do not.

---

## 2. What verification actually reads

`verify_diagram(diagram_id=..., include_svg=True)` returns the placed geometry EA holds after the
reload: per-object rects, sizes and z-order; per-link routing, color, width and label state; the
canvas extents; and, on request, the rendered SVG.

Two properties of that payload matter more than the field list:

**It is EA's own rendering.** `get_diagram_svg` and `get_diagram_png` both call EA's
`Project.PutDiagramImageToFile`. The SVG is not a reimplementation of EA's drawing — it *is* EA
drawing. That is why the SVG is authoritative for color and for paint order.

**A color readback proves nothing; a render does.** EA stores whatever integer you wrote and hands
it back on request, whether or not it draws with it. Some shapes refuse a fill outright — the write
succeeds, the property reads back correctly, and EA paints the element in its own colors, because
the shape script owns the fill. `set color → read color` asserts your own input and passes against
an implementation that stores it and never draws it.

So: **check color by looking at the render.** In the SVG, `fill="#RRGGBB"` and `stroke="#RRGGBB"`
are readable with a regex. No image decoding required.

---

## 3. The linter

`tools/lint.py`. It consumes a `verify_diagram` result and nothing else — no repository calls of its
own — so it runs anywhere you can carry the payload.

```python
import lint

report = lint.lint_diagram(verified, profile=..., roles=..., rows=..., expected_route=...)
if not report.clean:
    for finding in report.errors:
        print(finding.rule, finding.subjects, "->", finding.correction)
```

### It is language-neutral by construction

Every rule reads geometry and presentation. Nothing reads the metamodel, and no notation name
appears anywhere in the module — a test enforces that over identifiers *and* string constants,
including docstrings. One linter therefore serves every modeling language, including one nobody has
written a binding for, because "these boxes overlap" is not a metamodel question.

The consequence you have to live with: **the linter cannot know what two elements have in common.**
That is why `roles` and `rows` are yours to supply.

### `roles` and `rows` are yours to supply, and omitting them is not free

- `roles` maps a role name to the objects playing it. Uniform sizing is checked *within* a role,
  never across roles — two elements can share a container and legitimately differ in size.
- `rows` is a list of rows, each a list of objects. Spacing is checked per row.

Omit them and those rules **do not run**. They do not guess. Guessing which elements share a role
from their coordinates would invent the metamodel the module refuses to have, and it would do it
silently, which is worse than not checking.

A wrapped row is **two rows**. Pass it as two. The rule will not compensate, because compensating
would blind it to the single mis-spaced element it exists to catch.

### Severity

- **error** — the diagram is wrong. Overlapping elements, a row with no whitespace, elements in one
  role at different sizes. `report.clean` is false.
- **warning** — look at it. Often correct in context: out-of-canvas placement, an unset route, an
  unexplained set of fills. Does not block.
- **info** — a measurement, not a judgment.

`report.clean` means **no errors**, not "no findings". A bar nobody can clear is a bar nobody uses,
and a linter that rejects every legitimate view gets switched off — after which it protects nothing.

---

## 4. Profiles: why suppression is correctness, not convenience

A presentation profile says how much detail a view shows. An executive view that deliberately hides
connector labels must not then be told its connector labels are missing.

Pass the profile as a plain mapping. From a binding's profile:

```python
p = binding.profile("executive")
profile = {**p.display_settings(), "collapses_parallel": p.collapses_parallel}
report = lint.lint_diagram(verified, profile=profile)
```

`lint.PROFILE_KEYS` lists what is understood; anything else in the mapping is ignored rather than
rejected, so a profile vocabulary can grow without breaking the linter. `lint.SUPPRESSED_BY` is the
whole of profile-awareness — one table, readable and testable, rather than a branch inside a rule.

**A profile can never suppress a structural defect.** Overlapping elements are wrong under every
profile. Presentation settings switch off rules about *what is shown*, never rules about *where
things are*. There is a test per profile key asserting exactly that.

Suppressed rule ids come back on `report.suppressed`. A suppression must be visible, or a clean
report overstates what was checked.

---

## 5. The correction loop, and how to stop

```python
previous = None
for attempt in range(lint.MAX_CORRECTION_PASSES):
    verified = verify_diagram(diagram_id=..., include_svg=True)
    report = lint.lint_diagram(verified, profile=profile, roles=roles, rows=rows)
    if report.clean:
        break
    if lint.is_stalled(previous, report):
        break          # this pass changed nothing; another will not help
    apply_corrections(report.errors)
    previous = report
```

Two stopping conditions, because there are two ways to fail:

- **The budget runs out.** Say so. "Three passes, these four errors remain" is a useful report;
  "done" is not.
- **A pass changes nothing.** `is_stalled` compares report signatures, ignoring message wording so
  that a coordinate in a message does not look like a new finding. Stop at the first stall rather
  than burning the remaining budget on passes that each fix nothing.

Either way, **report honestly what is left.** The loop's value comes from being trusted, and one
"done" over a diagram with four overlaps costs more trust than twenty honest partial reports.

---

## 6. What the linter cannot see

Kept here on purpose. A clean report means *no defect this linter knows how to measure* — it is not
a claim that the diagram reads well, and the list of what it misses is the difference between those
two statements.

- **Whether the grammar was the right choice.** A capability model laid out as swimlanes will lint
  clean. It is still the wrong diagram.
- **Whether the content belongs on one diagram at all.** Forty elements can be spaced perfectly.
- **Whether a name means anything.** "Component 7" and "Payment Authorization" are the same to every
  rule here.
- **Whether a container's grouping is honest.** A group called "Other" holding a third of the
  content lints clean and is a confession.
- **Whether the layout matches the reader's mental order.** Foundations at the top is a choice the
  linter cannot second-guess.

When a rule *can* be built for something on this list, it should be. Until then, the honest report
is "clean, and here is what clean does not cover" — which is why this section exists in a file the
skill points at rather than in a comment nobody reads.

---

## 7. Look at it

The rules above were all added because something shipped that they would have caught. Several were
added because a diagram **scored clean and looked wrong** — ragged container widths, a name running
into its own icon, a band stopping short of its neighbors.

Render it and look. `verify_diagram(include_image=True)` returns the picture. The linter is the
floor, not the ceiling.
