# Use memory

Select memory for a decision your agent actually makes. The memory backend and its consuming agent must support
the same interface; adding a memory plugin alone does not make an arbitrary model use it.

## Choose a path

| Your agent needs | Memory | Consumer |
|---|---|---|
| Positions after objects leave view | [Spatial](memory/spatial.md) | a composable agent or reasoner |
| Exact order, counts or pending observations | [Events](memory/events.md) | an extractor and `EventMemoryAgent` |
| Video history for a compatible frozen VLA | [Video](memory/video.md) | the optional SimpleMemVLA runtime |
| Successful motions as a sampling prior | [Action](memory/action.md) | a compatible flow policy with steering |
| Experience when proposing a change | [Lessons](memory/lessons.md) | the `experience` proposer |
| An executable capability already verified | [Skill library](memory/skills.md) | the supported consumer for that skill kind |

## Run an event-memory example

Complete [Installation](../getting-started/installation.md). From the **workspace root**, run the CPU example:

```bash
uv run python harness/examples/memory/06_event_memory.py --quick
```

It exercises scoped event storage and recall and prints `40/40` complete-evidence cases correct. The example uses supplied observations
and does not require a visual model. [Event memory](memory/events.md#example) shows the minimal Python API.

## Connect the consumer

For spatial memory, start with the [composable agent configuration](memory/spatial.md#using-it-in-an-agent).
For event memory, supply an observation extractor and recall queries to the wrapper. For video memory, match the
checkpoint's camera, state, controller and runtime requirements before loading the model.

Persistent action banks and skill libraries need development data or promotion evidence first. Follow their
building steps before putting a path in an agent configuration; a path alone does not create the artifact.

## Check the boundary

Keep persistent experience sources frozen during evaluation. Episode-local history can update from permitted
observations, but must be scoped and reset so another evaluation episode cannot read it. Check the recorded
retrievals and compare with the same agent without that memory under matching task conditions.

## Next

- [Memory](memory/index.md): writing, retrieval and evaluation boundaries.
- [Skill library](memory/skills.md): build and apply reusable capabilities.
- [Benchmarking](../benchmarking/index.md): compare agents under a fixed protocol.
