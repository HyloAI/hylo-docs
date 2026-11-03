---
hide:
  - navigation
  - toc
---

<div class="hylo-hero" markdown>

# Robots that improve themselves

<p class="hylo-tagline">Hylo is an engine for Physical RSI. Robots practise in worlds, act through tools, remember,
improve, verify every change against physical outcomes, and share what they learn as skills.</p>

[Get started](getting-started/installation.md){ .md-button .md-button--primary }
[Quickstart](getting-started/quickstart.md){ .md-button }
[Physical RSI](physical-rsi.md){ .md-button }

</div>

## Physical RSI

AI has started to improve itself, but robots still improve only as fast as the people working on them: people
collect the data, read the failures, retrain and decide what ships. Hylo hands that loop to the robot. People set
the goals and approve what ships; the robot practises, acts, remembers, improves and proves each change.

Recursive self-improvement is limited by grounding: a system that grades itself drifts. Robots have the firmest
ground truth there is. Whether the cup was lifted is settled by physics, not by the model's opinion, so every step
of the loop is checked against physical outcomes.

![The Physical RSI loop: practise in worlds, act with tools, remember, improve, verify, share skills, deploy](assets/diagrams/physical-rsi-light.svg){ .hylo-diagram .only-light }
![The Physical RSI loop: practise in worlds, act with tools, remember, improve, verify, share skills, deploy](assets/diagrams/physical-rsi-dark.svg){ .hylo-diagram .only-dark }

[Why Physical RSI →](physical-rsi.md)

<div class="grid cards" markdown>

-   **Practise in worlds**

    ---

    Describe a scene in words, place any of 24 robot packs in it, add people and disturbances, and edit it in
    small checked steps. Every revision is kept; checks report why a goal is not met.

    [Worlds →](user-guide/worlds.md)

-   **Act with tools**

    ---

    A model operates the robot one checked tool call at a time, or writes a task program against perception,
    grasping and motion-planning tools. Existing policies run on the same execution kernel.

    [Tool-calling agents →](user-guide/tool-agents.md) · [Develop a skill →](user-guide/developing-strategies.md) ·
    [Policies →](user-guide/policies.md)

-   **Remember**

    ---

    Spatial memory, action memory and lessons keep what the robot saw and what worked. Every read and write is
    recorded, so an outcome can be traced to the memory that shaped it.

    [Memory →](user-guide/memory/index.md)

-   **Improve**

    ---

    Learners turn runs into sealed artifacts. A campaign diagnoses failures and proposes changes, from runtime
    settings and programs to learned components and policy weights.

    [Learning →](user-guide/learning.md) · [Campaigns →](user-guide/campaigns.md) ·
    [Skill research →](user-guide/research-and-skills.md)

-   **Verify**

    ---

    A change is tested on episodes it was not developed on and promoted only if it passes the gate. Every run is
    recorded as a trace you can replay step by step, and sealed so it can be checked afterwards.

    [Experiments →](user-guide/experiments.md) · [Benchmarking →](benchmarking/index.md) ·
    [Leaderboard →](benchmarking/leaderboard.md)

-   **Share skills**

    ---

    A verified program or recipe becomes a skill in the library, with its applicability, version and evidence
    attached. Later agents retrieve it by instruction or by the reason a goal failed.

    [Skills →](user-guide/skills.md) · [Skill reuse →](user-guide/research-and-skills.md#reuse-a-promoted-program)

-   **Deploy**

    ---

    A workcell runs the promoted version on a robot with the same episode loop the benchmark used, behind the
    safety shield and an operator's stop button. Its episodes come back as new experience.

    [Deployment →](user-guide/deployment.md) · [Safety →](user-guide/safety.md)

-   **Watch the loop**

    ---

    Studio shows worlds, research sessions, runs, replays, comparisons, campaigns and workcell controls in one
    place. Start it with `hylo playground`.

    [Studio →](user-guide/studio.md)

</div>

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
