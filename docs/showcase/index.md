# Examples and results

Choose a case by what you want to understand. Each result applies to its stated tasks, observations and
implementation. The detailed records retain failed attempts and limits alongside successful runs.

| Case | What it demonstrates | Scope and entry point |
|---|---|---|
| [World construction and motion](worlds.md) | scene editing, robot controls and measured receipts | recorded MuJoCo worlds; scene-building and robot-motion demos are separate |
| [A model controlling a robot](robot-control.md) | tool calls, approved actions and independent outcomes | one recorded Panda stacking episode |
| [Program development and skill reuse](program-skills.md) | a revised program, promotion evidence and later skill calls | one simulated sorting task family with privileged segmentation |
| [Program and tool experiments](tool-agents.md) | toolkit, program improvement, LIBERO and tool-calling results | per-workflow results, failures and reproduction sources |
| [Memory](memory.md) | spatial recall, action banks and skill application | paired comparisons and null results |
| [Video-memory integration](video-memory.md) | compatibility with a pinned upstream implementation | differential and regression checks, not a fresh held-out gain |
| [Phase-guided development](phase-guided.md) | program repair with phase-scoped notes | experimental probes and current failures |
| [System measurements](system-results.md) | execution, learning, evaluation, runtime and plugin checks | a summary linking to each recorded source |

## Run a small example

From the **workspace root**, run the CPU safety-shield example:

```bash
uv run python harness/examples/core/02_safety_shield.py --quick
```

The [Core results](core.md) explains the output. Camera-based examples additionally require
[rendering setup](../getting-started/optional-environments.md#camera-rendering).

## Find a configuration

For a guided first run, use the [quickstart](../getting-started/quickstart.md). The
[complete example catalogue](../getting-started/examples.md) lists the shipped benchmark and plugin configs.
