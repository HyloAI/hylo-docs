# Use memory

Select memory for a decision your agent actually makes. The memory backend and its consuming agent must support
the same interface; adding a memory plugin alone does not make an arbitrary model use it.

## Choose a backend { #choose-a-path }

Use the [memory types](memory/index.md#memory-and-its-consumers) to match your task to a backend and consumer.
The example below uses event memory: it records supplied observations and recalls their order without a model.

## Run the example { #run-an-event-memory-example }

Complete [Installation](../getting-started/installation.md). From the **workspace root**, run the CPU example:

```bash
uv run python harness/examples/memory/06_event_memory.py --quick
```

Expected output includes `40/40` correct complete-evidence cases. These cases check storage and recall from
supplied observations; they do not evaluate visual perception. [Event memory](memory/events.md#example) shows the minimal Python API.

## Connect an agent { #connect-the-consumer }

For spatial memory, start with the [composable agent configuration](memory/spatial.md#using-it-in-an-agent).
For event memory, supply an observation extractor and recall queries to the wrapper. For video memory, match the
checkpoint's camera, state, controller and runtime requirements before loading the model.

Persistent action banks and skill libraries need development data or promotion evidence first. Follow their
building steps before putting a path in an agent configuration; a path alone does not create the artifact.

## Evaluation boundaries { #check-the-boundary }

Keep persistent experience sources frozen during evaluation. Episode-local history can update from permitted
observations, but must be scoped and reset so another evaluation episode cannot read it. Check the recorded
retrievals and compare with the same agent without that memory under matching task conditions.

## Next

- [Memory](memory/index.md): writing, retrieval and evaluation boundaries.
- [Skill library](memory/skills.md): build and apply reusable capabilities.
- [Benchmarking](../benchmarking/index.md): compare agents under a fixed protocol.
