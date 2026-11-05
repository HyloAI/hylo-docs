# Event memory { #event-memory }

`EventMemory` stores episode-scoped observations in a SQLite journal and answers exact
queries over their recorded order. It supports latest, first, nth, count, sequence,
unseen, pending and elapsed-time recall. Each answer carries evidence references and a
`known`, `partial` or `unknown` status.

This is a storage and recall component, not a visual detector. An extractor or adapter
must turn permitted observations into events. Missing perception cannot become a known
fact merely because it was written to memory.

## Store and recall { #example }

```python
from hylo.core.episode_memory import EpisodeScope, MemoryEvent, RecallQuery
from hylo.memory.episode import EventMemory

memory = EventMemory()
memory.reset(EpisodeScope(task_id="example", episode_id="episode-1"))
memory.append([MemoryEvent(
    id="cue-1", step=0, time=0.0, kind="cue", subject="target",
    value="blue", evidence=("observation:0:front",), source="visible-cue-adapter",
)])
answer = memory.recall(RecallQuery(name="target", op="latest", kind="cue", subject="target"))
assert answer.status == "known" and answer.value == "blue"
memory.close()
```

The cue value above is example input supplied by an adapter. The journal does not infer
it from an image. Event IDs must be stable; repeating the same ID and payload is
idempotent, while reusing an ID for different evidence is rejected. Events have increasing
`(step, order)` positions and nondecreasing times.

## Evidence

An observed count is a lower bound unless the caller explicitly declares complete coverage.
Negative queries require both coverage and a defined universe. Observation gaps or ambiguous
evidence can produce `unknown`; exceeding the event budget raises an error rather than
silently discarding the early events that a later query might require.

Reset selects a task/episode scope. Reopening existing evidence requires `resume=True`;
ordinary reset refuses to reuse a scope that already contains events. Persistent journals
can retain audit evidence without making it available to another episode's recall.

## Agent integration { #agent-integration }

`EventMemoryAgent` wraps an existing agent with an extractor and recall queries. It makes
the recalled context available through the wrapped agent's instruction. The reference
`SignalExtractor` consumes declared, agent-visible state signals; it is not an RGB detector
and must not be connected to privileged simulator fields on a visual benchmark.

## Verification

CPU tests cover scoped persistence, event ordering, duplicate handling, evidence gaps,
bounded recall and agent composition. These establish the storage/recall behavior, not a
general visual-memory benchmark benefit.

For contracts and implementation, see the [core API](../../api/packages/hylo-core.md),
[memory API](../../api/packages/hylo-memory.md) and [agents API](../../api/packages/hylo-agents.md).
Runnable CPU examples live at `harness/examples/memory/06_event_memory.py` and
`harness/examples/memory/07_event_memory_occlusion.py` in the workspace.

## Next

- [Use memory](../using-memory.md): choose a consuming agent.
- [Memory interfaces](../../harness/interfaces/memory.md): current contracts and lifecycle rules.
