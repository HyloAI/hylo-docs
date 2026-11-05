# Physical RSI

Use task outcomes to propose changes, compare them with the current agent and carry adopted versions into later
runs. Hylo connects [worlds](user-guide/worlds/overview.md), [agents](user-guide/agents.md),
[memory](user-guide/memory/index.md) and [skills](user-guide/skills.md) through this improvement loop.

People define the tasks, success checks and operating boundaries. Campaign promotion defaults to `auto`;
configure `approval: manual` for anything that will run on hardware and validate the target deployment.

![The Physical RSI loop: Build, Run, Improve, Verify and Deploy.](assets/diagrams/physical-rsi-light.svg){ .hylo-diagram .only-light }
![The Physical RSI loop: Build, Run, Improve, Verify and Deploy.](assets/diagrams/physical-rsi-dark.svg){ .hylo-diagram .only-dark }

<span id="the-bottleneck"></span>
<span id="grounding"></span>

## Improvement loop { #the-loop }

| Step | Capability | Guide |
|---|---|---|
| Build | Create scenes, robots and task conditions | [Worlds](user-guide/worlds.md) |
| Run | Execute an agent and record actions and outcomes | [Experiments](user-guide/experiments.md) |
| Improve | Produce candidate settings, programs or learned artifacts | [Campaigns](user-guide/campaigns.md), [Learning](user-guide/learning.md) |
| Verify | Compare frozen candidates under declared conditions | [Benchmarking](benchmarking/index.md) |
| Deploy | Activate a version for later execution and retain rollback | [Deployment](user-guide/deployment.md) |

Each round starts from the version the previous round adopted. A rejected candidate stays in the archive;
it does not replace the active version. Task checks provide feedback independently of an agent's own summary.

## Campaigns

A campaign diagnoses failures, asks a generator for changes, screens candidates and applies a paired promotion
gate. It records the evidence and version history. Generators may propose settings, steering rules, programs or
learner artifacts. They cannot change the protected safety, scoring or benchmark settings.

Start with [First improvement](getting-started/first-improvement.md) for a complete CPU example, then use
[Campaigns](user-guide/campaigns.md) to configure your own loop.

## Reusable outputs { #what-improves }

- **Agent versions** retain adopted configuration changes and rollback history.
- **Artifacts** retain weights, critics, world models, judges or memory banks with their provenance.
- **Skills** retain reusable programs or procedures with applicability and verification evidence.

Each output has its own validation path. A calibrated judge is an instrument; it does not become a promoted
agent. A verified program skill is available for reuse; it does not deploy itself onto a robot.

## Inputs { #what-you-bring }

Bring a task and its success conditions, a simulation or robot interface, and a starting agent. Existing models,
programs, demonstrations and recorded runs can supply that starting point. Follow [Agents](user-guide/agents.md)
to choose the execution mode and [Learning](user-guide/learning.md#external-data) to ingest external data.

<span id="serve"></span>

## Operation { #control }

[Serve](user-guide/deployment.md) runs agents through policy servers and workcells. [Studio](user-guide/studio.md)
shows runs and campaigns and provides operator controls. Every executed action passes the safety shield.
Rollback changes the active version; it does not undo physical actions.

Keep development and evaluation data separate, retain observation conditions with results, and revalidate
when the task or robot changes. Simulation evidence supports its stated conditions; hardware needs target validation.

<span id="why-now"></span>
<span id="direction"></span>
<span id="further-reading"></span>

## Next

- [First improvement](getting-started/first-improvement.md): run the complete loop.
- [Campaigns](user-guide/campaigns.md): configure generation, gates and approval.
- [Research](https://hyloai.github.io/research/): measured outcomes and experimental analysis.
