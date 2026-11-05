# Spatial memory

Spatial memory stores facts about the world with a place and a time: "the red block was at (0.31, −0.12) on the
table at t = 4.2 s". An agent writes what it perceives while it can see it, and recalls it once it cannot. The
reference backend is `sqlite`: one SQLite file (or `:memory:` for a single run), queried by key, kind, time, place
and text.

![While the targets are visible, the reasoner perceives them and writes them to spatial memory; once they are hidden, it queries the memory and acts on the remembered positions.](../../assets/diagrams/spatial-recall-light.svg){ .hylo-diagram .only-light }
![While the targets are visible, the reasoner perceives them and writes them to spatial memory; once they are hidden, it queries the memory and acts on the remembered positions.](../../assets/diagrams/spatial-recall-dark.svg){ .hylo-diagram .only-dark }

## Connect an agent { #using-it-in-an-agent }

Composable agents pair a reasoner (slow, event-triggered decisions) with a policy (every step). The reasoner gets
the memory store, a per-episode working memory with a fixed capacity, and an event emitter.

```yaml
agent:
  type: composable.object_reach
  params:
    chooser: {type: chooser.rule_color}        # or chooser.llm / chooser.vlm
    memory: {type: sqlite, params: {path: ":memory:"}}   # the default; a file path keeps it across runs
```

`composable.object_reach` writes every visible object as a spatial item keyed by episode and object, and when the
objects are hidden it recalls them from memory instead. The chooser decides which object the instruction means,
from seen or remembered objects alike, so the same code serves both. `memory: null` turns memory off.

A reasoner of your own uses the same contracts:

```python
from hylo.core.memory import MemoryItem, MemoryKind, MemoryQuery, Pose, TimeSpan

def remember(rctx, obj_id, xy, t):
    item = MemoryItem(kind=MemoryKind.SPATIAL, key=f"{rctx.episode_id}:{obj_id}", content=f"{obj_id} at {xy}",
                      entities=(obj_id,), scope={"episode_id": rctx.episode_id},
                      pose=Pose(frame_id="table", position=(*xy, 0.0)), event_time=TimeSpan(start=t))
    res = rctx.memory.write([item])
    rctx.emit("memory.write", {"op": "write", "events": [list(e) for e in res.events]})

def recall(rctx, near_xy, radius=0.2):
    q = MemoryQuery(kinds=frozenset({MemoryKind.SPATIAL}), scope={"episode_id": rctx.episode_id},
                    near=(Pose(frame_id="table", position=(*near_xy, 0.0)), radius))
    hits = rctx.memory.query(q)
    rctx.emit("memory.retrieval", {"n_hits": len(hits)})
    return hits
```

Emit the events yourself: they are what makes a decision from memory visible in a replay.

## Behaviour { #design }

The reasoner writes observed objects and queries them when perception loses the target. Scope writes and queries
to the episode. The same chooser handles visible and remembered objects.

Locations and times are structured fields. A newer keyed fact invalidates the earlier one while preserving
history; expire a remembered location when it proves wrong. See the [storage rules](../../reference/memory.md#writes-and-invalidation).

## Inspect retrieval { #in-the-trace }

Use the trace to check `memory.write`, `memory.retrieval` and `agent.decision` events. A decision's
`object_source` distinguishes `seen` from `remembered` objects. The [recorded trace](../../developer-guide/validation/guide-results.md#spatial-trace)
shows the switch after targets become hidden.

<span id="items"></span>
<span id="writes-and-invalidation"></span>
<span id="queries"></span>

See [Memory reference](../../reference/memory.md#spatial-memory) for item fields, writes and queries.

## Constraints { #limits }

- Text search uses substring matching.
- Spatial queries require positions in the same frame.
- Memory does not resolve language: an instruction the chooser misreads is misread with memory too.

<span id="what-it-achieved"></span>

## Next

- [Recorded results](../../developer-guide/validation/guide-results.md#spatial-memory): measurements, conditions and reproduction commands.
- [Use memory](../using-memory.md): match a memory to its consuming agent.
- [Memory](index.md): lifetime and evaluation boundaries.
