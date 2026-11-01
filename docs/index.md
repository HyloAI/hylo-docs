---
hide:
  - navigation
  - toc
---

<div class="hylo-hero" markdown>

# The stack for physical AI

<p class="hylo-tagline">Hylo runs robot policies in simulation and on robots, records every episode, scores policies
under fixed protocols, improves them through gated campaigns, and deploys the promoted version to a workcell.</p>

[Get started](getting-started/installation.md){ .md-button .md-button--primary }
[Quickstart](getting-started/quickstart.md){ .md-button }
[Concepts](getting-started/concepts.md){ .md-button }

</div>

## What you do with Hylo

![Run, measure, improve through a gate, deploy; episodes on the robot come back as runs](assets/diagrams/hylo-loop-light.svg){ .hylo-diagram .only-light }
![Run, measure, improve through a gate, deploy; episodes on the robot come back as runs](assets/diagrams/hylo-loop-dark.svg){ .hylo-diagram .only-dark }

<div class="grid cards" markdown>

-   **Run**

    ---

    An experiment config names an environment, an agent and a set of episodes. Run it, and every episode is
    recorded as a trace you can replay step by step.

    [Experiments →](user-guide/experiments.md) · [Policies →](user-guide/policies.md)

-   **Measure**

    ---

    An evaluation protocol fixes everything except the agent being scored: episodes, seeds and timing. Each result
    is a scorecard, and a leaderboard ranks the scorecards of one protocol.

    [Benchmarking →](benchmarking/index.md) · [Leaderboard →](benchmarking/leaderboard.md)

-   **Improve**

    ---

    Learners turn runs into sealed artifacts. A campaign proposes changes, tests them against the current version
    on episodes it did not choose them on, and promotes a change only if it passes the gate.

    [Learning →](user-guide/learning.md) · [Campaigns →](user-guide/campaigns.md)

-   **Deploy**

    ---

    A workcell runs the promoted version on a robot with the same episode loop the benchmark used, behind the
    safety shield and an operator's stop button.

    [Deployment →](user-guide/deployment.md) · [Safety →](user-guide/safety.md)

</div>

[Studio](user-guide/studio.md) is one UI over all four steps: browse runs, replay episodes, compare policies, follow
campaigns and operate workcells. Start it with `hylo playground`.

## The stack

Six layers, from the kernel at the base to the workbench on top, and the repositories that implement them.

![The six layers of the Hylo stack and the repositories that implement them](assets/diagrams/stack-light.svg){ .hylo-diagram .only-light }
![The six layers of the Hylo stack and the repositories that implement them](assets/diagrams/stack-dark.svg){ .hylo-diagram .only-dark }

## Where next

- [Architecture](design/overview.md): how the four steps connect, and the packages behind them.
- [Extending](harness/extending.md): add your own environment, policy, learner or generator.
- [CLI reference](cli/index.md): every `hylo` command and its options.
- [Plugin catalogue](developer-guide/plugin-catalogue.md): every plugin, with what it has been run on.
