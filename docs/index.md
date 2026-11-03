---
hide:
  - navigation
  - toc
---

<div class="hylo-hero" markdown>

# Physical RSI: robots that build on their own progress

<p class="hylo-tagline">Hylo turns robot improvement into a loop the system can drive: build worlds, run tasks,
improve, verify against physical outcomes and deploy what passes. Each round starts from what the last one adopted.</p>

[Get started](getting-started/installation.md){ .md-button .md-button--primary }
[Quickstart](getting-started/quickstart.md){ .md-button }
[Physical RSI](physical-rsi.md){ .md-button }

</div>

## Physical RSI

Robots can act autonomously while still depending on people to drive their improvement: teams collect runs, diagnose
failures, choose changes, evaluate candidates and decide what to deploy. Hylo puts the system to work on that loop.
People set the goals and boundaries and approve promotion to hardware.

Physical tasks give self-improvement an external test: whether an action produced the intended result in the world.
Hylo keeps the changes that measured outcomes support and rejects the rest, so the loop advances on demonstrated
capability.

![The Physical RSI loop: Build, Run, Improve, Verify and Deploy, with RSI campaigns over Improve and Verify and Serve beneath all five](assets/diagrams/physical-rsi-light.svg){ .hylo-diagram .only-light }
![The Physical RSI loop: Build, Run, Improve, Verify and Deploy, with RSI campaigns over Improve and Verify and Serve beneath all five](assets/diagrams/physical-rsi-dark.svg){ .hylo-diagram .only-dark }

[Why Physical RSI →](physical-rsi.md)

<div class="grid cards" markdown>

-   **Worlds** · Build

    ---

    Describe a scene in words, place any of 24 robot packs in it, add people and disturbances, and edit it in
    small checked steps. Checks report why a goal is not met. Recorded episodes can be rebuilt in simulation.

    [Worlds →](user-guide/worlds.md)

-   **Agents and policies** · Run

    ---

    A model operates the robot one checked tool call at a time, or writes a task program against perception,
    grasping and motion-planning tools. Vision-language-action models and other policies run on the same loop.

    [Tool-calling agents →](user-guide/tool-agents.md) · [Develop a skill →](user-guide/developing-strategies.md) ·
    [Policies →](user-guide/policies.md)

-   **Training** · Improve

    ---

    Learners turn recorded runs into sealed artifacts: policies, fine-tuned weights, value critics, world models
    and success judges, each with the runs and splits it was built from.

    [Learning →](user-guide/learning.md)

-   **Memory** · Improve

    ---

    Spatial memory, action memory and lessons keep what the robot saw and what worked, built only from verified
    development experience. Every read and write is recorded.

    [Memory →](user-guide/memory/index.md)

-   **Campaigns** · Improve and Verify

    ---

    The RSI engine: rules, learners and language models propose changes, from runtime settings and programs to
    policy weights, and a campaign promotes only those that pass its gate.

    [Campaigns →](user-guide/campaigns.md) · [Skill research →](user-guide/research-and-skills.md)

-   **Evaluation** · Verify

    ---

    A protocol fixes everything except the agent being scored. Candidates are tested on episodes they were not
    developed on; every run is a trace you can replay step by step.

    [Experiments →](user-guide/experiments.md) · [Benchmarking →](benchmarking/index.md) ·
    [Leaderboard →](benchmarking/leaderboard.md)

-   **Skills** · Improve and Deploy

    ---

    A verified program or recipe becomes a skill with its applicability, version and evidence attached. Later
    agents retrieve it by instruction or by the reason a goal failed.

    [Skills →](user-guide/skills.md) · [Skill reuse →](user-guide/research-and-skills.md#reuse-a-promoted-program)

-   **Serve and deployment** · Deploy

    ---

    Serve runs the active version behind a policy server and a workcell next to the robot, with the safety shield
    and an operator's stop button, and is designed to serve every model the loop uses.

    [Deployment →](user-guide/deployment.md) · [Safety →](user-guide/safety.md)

</div>

[Studio](user-guide/studio.md) shows worlds, research sessions, runs, replays, comparisons, campaigns and workcell
controls in one place. Start it with `hylo playground`.

## Choose a starting point

- **Bring an existing policy:** follow the [CPU quickstart](getting-started/quickstart.md), then [connect your policy](user-guide/policies.md).
- **Develop a robot skill:** use the [robot tools and code agents](user-guide/developing-strategies.md), then inspect the recorded results.
- **Try robots in a scene:** describe a [world](user-guide/worlds.md) with any of 24 robot packs, run it by hand or
  with `hylo world chat`, and record camera data.
- **Let a model operate the robot:** run [`tools.llm`](user-guide/tool-agents.md) on a benchmark task, watch it with
  `hylo watch`, and seal the run.
- **Improve or reuse a skill:** run a [research session](user-guide/research-and-skills.md), compare with a baseline through a campaign, or retrieve a verified program skill.

New-task development starts with execution and task validation. A claim of improvement uses a separate comparison
with a baseline and, for campaign promotion, the gate. The [showcase](showcase/tool-agents.md) reports the conditions,
measured results and current limits of the new workflows.

## The stack

Six layers, from the kernel at the base to the workbench on top, and the repositories that implement them.

![The six layers of the Hylo stack and the repositories that implement them](assets/diagrams/stack-light.svg){ .hylo-diagram .only-light }
![The six layers of the Hylo stack and the repositories that implement them](assets/diagrams/stack-dark.svg){ .hylo-diagram .only-dark }

## Where next

- [Physical RSI](physical-rsi.md): the problem Hylo addresses and how the loop works.
- [Architecture](design/overview.md): how development, execution, evaluation and deployment connect.
- [Extending](harness/extending.md): add your own environment, policy, learner or generator.
- [CLI reference](cli/index.md): every `hylo` command and its options.
- [Plugin catalogue](developer-guide/plugin-catalogue.md): every plugin, with what it has been run on.
