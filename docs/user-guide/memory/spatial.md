# Spatial memory

Spatial memory stores facts about the world with a place and a time: "the red block was at (0.31, −0.12) on the
table at t = 4.2 s". An agent writes what it perceives while it can see it, and recalls it once it cannot. The
reference backend is `sqlite`: one SQLite file (or `:memory:` for a single run), queried by key, kind, time, place
and text.

## Items

Every fact is a memory item:

| Field | Meaning |
|---|---|
| `kind` | `spatial`, `episodic`, `semantic`, `working` or `skill` |
| `content` | a short text description |
| `key` | the identity of the thing described, for example `<episode>:obj_0`; a newer item with the same kind and key replaces it |
| `pose` | a position (and optional orientation) in a named frame, such as `table` |
| `event_time` | when it was observed: a start, an optional end, and the clock (`sim` or `wall`) |
| `payload` | structured data, for example `{"rgb": [0.85, 0.1, 0.1]}` |
| `entities`, `scope` | the entities it is about; the task, robot or episode it belongs to |
| `confidence`, `source` | how sure the writer was; which component wrote it |

## Writes and invalidation

Time is kept twice: when the fact was true in the world, and when it was recorded. Writing an item has one of
three effects, reported back to the writer and in the `memory.write` trace event:

- `ADD`: a new fact.
- `INVALIDATE`: an earlier fact with the same kind and key stops being valid from the new item's time. It is not
  deleted: a query "as of" an earlier time still finds it.
- `SKIP_DUP`: the same content is already stored and valid, so nothing is written.

`forget` marks matching items as expired (for example, a remembered location that turned out to be empty). Nothing
is ever removed from the file.

## Queries

| Query field | Effect |
|---|---|
| `kinds`, `key` | restrict to these kinds or this identity |
| `text` | items whose content contains the text |
| `entities`, `scope` | any of these entities; all of these scope values |
| `near` | within a radius of a pose (same frame); closer items score higher |
| `time_range` | observed during this interval |
| `as_of` | what was valid at that time, including facts that were invalidated later |
| `include_invalidated` | also return replaced facts |
| `k` | at most this many hits (default 10) |

Each hit has a score (confidence and, for spatial queries, closeness) and the time it stopped being valid, if it
did.

## Using it in an agent

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

## What it achieved

On the MuJoCo table with targets visible for only the first 5 steps, `composable.object_reach` went from 0.00 to
0.75 success with spatial memory (300 pairs, p = 4e-68); per task, 0.99 on direct and push instructions and 0.27 on
indirect ones ("the colour of a ripe tomato"), which the rule-based chooser cannot resolve with or without memory.
With targets always visible, memory changed nothing (0.75 both ways). In a single traced episode, the recalled
positions matched the true ones exactly and the agent switched from seen to remembered objects at step 5.

```bash
uv run python examples/memory/01_spatial_memory_occlusion.py      # in the harness repository
uv run python examples/memory/02_observable_retrieval.py          # one episode's writes and retrievals
```

## Limits

- Text search is a substring match; there are no embeddings yet.
- Spatial queries need the same frame; there is no transform between frames.
- Memory does not resolve language: an instruction the chooser misreads is misread with memory too.
