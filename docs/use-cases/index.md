# Use cases { #use-cases }

<span id="examples-and-results"></span>

See a complete task in Hylo, then follow the guide to run it yourself. Each case includes a recorded demo,
its observation conditions and a reproduction entry point.

| Task | What you will see | Start here |
|---|---|---|
| Build a world | Create and refine a scene through conversation; inspect robot motion | [World construction and motion](worlds.md) |
| Control a robot | Turn an instruction into tool calls and independently checked actions | [A model controlling a robot](robot-control.md) |
| Develop and reuse a skill | Revise a sorting program, verify it and call it in later scenes | [Program development and skill reuse](program-skills.md) |

## Results { #explore-the-evidence }

[Research](https://hyloai.github.io/research/) publishes experimental findings and their limits.
[Benchmarks](https://hyloai.github.io/research/benchmarks/) presents results grouped by evaluation protocol.
For engineering checks, see [System validation](../developer-guide/validation/index.md).

## Try it { #run-a-small-example }

From the workspace root:

```bash
uv run python harness/examples/core/02_safety_shield.py --quick
```

[Core validation](../developer-guide/validation/core.md) explains the output.

## Next { #find-a-configuration }

For configurations,
see the [example catalogue](../getting-started/examples.md); for a first installation, use the
[quickstart](../getting-started/quickstart.md).
