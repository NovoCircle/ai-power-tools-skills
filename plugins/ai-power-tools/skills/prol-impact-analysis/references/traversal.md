# Traversal — endpoints, algorithm and the growth problem

Measured against Prolaborate 5.6.1.40 as a Super Admin. Where something was not measured it says so.

Example organization is Westbrook Bank throughout.

---

## 1. There is no depth parameter

Every relationship read in Prolaborate is **one hop**. No endpoint takes a depth, and the Analyzer
interface expands one node at a time by hand.

So multi-hop impact analysis is a **breadth-first search you implement**. You own:

- the **frontier** and the visited set,
- the **depth cap**,
- **cycle handling**,
- and the honest statement of what you did not reach.

## 2. The reads

| Call | Verb | Returns |
|---|---|---|
| `/api/element/GetTraceability` | POST | `connectorGroup[]` for one element, grouped by connector type; each group has `relatedElements[]` with `connectorDirection`, `connectorGuid` and the neighbour's identity |
| `/api/diagrammer/GetElementsConnectors` | POST | `elementGuids[]` in → `connectors[]` with `source` / `target`. **The efficient frontier call** |
| `/api/diagrammer/GetRelatedElements` | GET | a pre-grouped jstree-style tree |
| `/api/element/GetConnectedElementsList` | POST | neighbours per MDG connector-attribute id — a field-driven lookup, not a generic walk. Carries `[CheckForAPILimit]` |
| `/api/element/GetElementAncestorWithACL` | POST | ancestor chain; route is singular, method is plural |
| `/api/diagrammer/GetAll` | GET | saved Analyzer views |

**Use `GetTraceability` to seed and `GetElementsConnectors` to expand.** One call per frontier
beats one call per node, and the frontier is where the cost is.

### Do not call the writes on this controller

`api/diagrammer` serves **two features** — Analyzer views and Prolaborate diagrams — behind one
controller. The `type` parameter that distinguishes them on `Get` and `OpenInDiagrammerView` is
**undecoded**, so `Create`, `Update` and `Delete` cannot be aimed safely. Create and edit views
through the interface.

*(Partially decoded 2026-10-02: the canvas route `/repositories/canvastree/<repo>/<id>/<mode>`
uses `0` for "not yet saved" and a GUID afterwards. That is the route's id segment, **not** the
`type` parameter on those API actions, which remains unknown.)*

## 3. The traversal

```js
async function impact(seedGuid, { maxDepth = 2, follow = null, maxNodes = 300 } = {}) {
  const visited = new Map();              // guid -> { element, depth }
  const edges   = new Map();              // connectorGuid -> edge
  let frontier  = [seedGuid];
  visited.set(seedGuid, { depth: 0 });

  for (let depth = 1; depth <= maxDepth && frontier.length; depth++) {
    const res = await post('/api/diagrammer/GetElementsConnectors',
                           { repositoryId, elementGuids: frontier, userId });

    const next = [];
    for (const c of res.connectors) {
      if (follow && !follow.includes(c.stereotype)) continue;   // see the note below
      edges.set(c.guid, c);
      for (const end of [c.source, c.target]) {
        if (!end || visited.has(end)) continue;                 // cycle + revisit guard
        if (visited.size >= maxNodes) return done('node cap');
        visited.set(end, { depth });
        next.push(end);
      }
    }
    frontier = next;
  }
  return { visited, edges, reachedCap: frontier.length > 0 };
}
```

**The three rules that matter:**

1. **De-duplicate on `guid`, always.** It is the cycle guard and the revisit guard at once. A
   dependency graph is not a tree.
2. **Cap, and report the cap.** `reachedCap` is the difference between "nothing further is
   affected" and "I stopped looking". Those are not the same answer and must never be reported the
   same way.
3. **Filtering by relationship type is a modelling decision, not a detail.** Following
   `Aggregation` answers a containment question; following `Supports` answers a dependency
   question. Following everything answers neither clearly. Say which you followed.

### A trap carried over from `prol-matrix`

Connector payloads carry **both** `baseType` (e.g. `Association`) and `stereotype` (e.g.
`Supports`). The product itself uses both in one screen — the traceability panel groups by base
type while the filter chips group by stereotype.

**Decide which one your `follow` list matches, and say so.** A filter written against `Association`
and applied to data keyed by `Supports` silently matches nothing, and an empty result looks like
"nothing is affected".

Direction fields are not reliable for deciding which end is which — see `prol-matrix`
`references/reading-a-matrix.md` §5, where that was measured across eleven profiles. For impact
analysis you usually want the undirected neighbourhood anyway; if direction matters, say which
direction you followed and verify it against the data rather than the declared setting.

## 4. The growth problem, measured

Counts read from the Analyzer's own filter panel during the walk:

| After | Nodes | Connectors |
|---|---|---|
| seed placed | 1 | 0 |
| 25 one-hop neighbours added | 26 | 25 |
| **2 more elements added at hop two** | **28** | **63** |

**Two nodes, thirty-eight new connectors.**

The cause is structural and applies to any traversal, not just the UI: **a newly reached element
brings all of its edges to elements already in the set**, not only the edge you arrived on. In a
densely modelled area — where many applications support many capabilities — each new node closes
many triangles at once.

Consequences for a skill:

- **Node count is a poor budget. Edge count is the real one.** Report both.
- **Readability collapses before the node cap is hit.** The graph above was unreadable at 28 nodes.
- **Hop 2 is usually the interesting one and hop 3 is usually the one that ruins the picture.**
  Default to `maxDepth: 2`, expand further only on request, and show the counts first.

## 5. Reporting

A useful impact answer states, every time:

| | Example |
|---|---|
| the seed | `Payments Gateway` |
| the depth reached | 2 hops |
| the relationship types followed | `Supports`, `Aggregation` |
| what was found | 61 elements, 184 relationships |
| **whether a cap was hit** | **stopped at the depth cap — more exists beyond** |
| the identity it was read as | Super Admin, so ACL filtering may not have applied |

The last two lines are the ones people omit and the ones that make the answer trustworthy.

## 6. Not measured

- **Cycles.** None were encountered on the test data; de-duplication was confirmed only on a direct
  back-reference. The guard above is written from the shape of the problem, not from a measurement.
- **`GetConnectedElementsList` rate limiting.** It carries `[CheckForAPILimit]`; the limit is
  unknown. Two endpoints share its contract — one on `api/element`, one on `api/externalintegration`
  — with different rate limiting.
- **ACL behaviour for a restricted user.** Everything was read as Super Admin.
- **Large-graph behaviour.** The largest view built was 28 nodes. Nothing here establishes how the
  canvas or the endpoints behave at hundreds.
