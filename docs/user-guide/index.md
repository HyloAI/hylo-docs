<span id="guides"></span>

# Guides { #user-guides }

Choose a capability, then follow its practical guides or watch a recorded workflow. Start with [Quickstart](../getting-started/quickstart.md)
for a first run, or [Concepts](overview.md) for the terms used across Hylo.

| Capability | What you can do | Start here |
|---|---|---|
| [Physical RSI](../physical-rsi.md) | Compare candidates and carry improvements into later runs | [First improvement](../getting-started/first-improvement.md) |
| [Worlds](worlds/overview.md) | Build scenes and check physical outcomes | [Create a world](worlds.md) |
| [Agents](agents.md) | Run policies, programs or model tool calls | [Choose an agent](agents.md#choose-an-agent) |
| [Memory](memory/index.md) | Use earlier observations and experience | [Use memory](using-memory.md) |
| [Skills](skills.md) | Retrieve and apply verified implementations | [Program skills](research-and-skills.md) |

<span id="examples-and-results"></span>

## Recorded workflows { #use-cases }

See a complete task, then follow its guide to run it yourself. Each walkthrough includes a recorded demo,
its observation conditions and a reproduction entry point within the corresponding Guides topic.

| Topic | Task | Walkthrough |
|---|---|---|
| Worlds | Create and refine a scene; inspect robot motion | [World examples](worlds/examples.md) |
| Agents | Turn an instruction into tool calls and checked actions | [Control a robot](agents/robot-control.md) |
| Skills | Develop a sorting program, verify it and reuse it in later scenes | [Develop and reuse a skill](skills/development-and-reuse.md) |

## Operations { #deploy-and-operate }

| Task | Guide |
|---|---|
| Run an agent on a workcell | [Deployment](deployment.md) |
| Inspect and operate the system | [Studio](studio.md) |
| Manage runs and artifacts | [Store](store.md) |
| Configure action checks and access | [Safety](safety.md), [Security](security.md) |

## Try an example { #run-a-small-example }

From the workspace root:

```bash
uv run python harness/examples/core/02_safety_shield.py --quick
```

[Core validation](../developer-guide/validation/core.md) explains the output.

<span id="explore-the-evidence"></span>
<span id="find-a-configuration"></span>

## Next

- [Example catalogue](../getting-started/examples.md): find experiment and campaign configurations.
- [Reference](../reference/index.md): look up fields and interfaces.
- [Research](https://hyloai.github.io/research/): read experimental findings.
- [Benchmarks](https://hyloai.github.io/research/benchmarks/): explore results by evaluation protocol.
- [System validation](../developer-guide/validation/index.md): inspect engineering checks and reproduction records.
