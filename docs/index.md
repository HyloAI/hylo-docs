---
hide:
  - navigation
  - toc
---

<div class="hylo-hero" markdown>

# The stack for physical AI

<p class="hylo-tagline">From real-time running to cognition, evaluation and evolution, Hylo builds every layer of
physical AI on one execution kernel. These pages show how to use each layer and how to extend it.</p>

[Get started](getting-started/installation.md){ .md-button .md-button--primary }
[Quickstart](getting-started/quickstart.md){ .md-button }
[Concepts](getting-started/concepts.md){ .md-button }

</div>

## The Hylo stack

Six layers, top to bottom, all built on one execution kernel. Each card names where the layer lives and where to
read about it.

<div class="grid cards hylo-stack" markdown>

-   **6 · Workbench**

    ---

    Run tasks, replay every episode and approve releases in one workspace.
    *Hylo Studio* (hylo-studio).

    [Studio →](user-guide/studio.md)

-   **5 · Evolution**

    ---

    Turn experience into stronger versions, each one tested before release. Learners turn development runs into
    sealed artifacts; campaigns compare candidates with the current version on separate episodes and promote
    what passes, after a person approves. *Learn, Evolve* (hylo-learn, hylo-evolve).

    [Learning →](user-guide/learning.md) · [Campaigns →](user-guide/campaigns.md)

-   **4 · Evaluation**

    ---

    Measure every policy against the same standard. Protocols fix the episodes, seeds and timing; scorecards
    carry Wilson intervals; leaderboards compare policies. *Hylo Bench, Eval* (hylo-bench, hylo-eval).

    [Benchmarking →](benchmarking/index.md) · [Experiments →](user-guide/experiments.md)

-   **3 · Cognition**

    ---

    Use what the robot has seen and done to choose its next step: policies of every family, steered by memory,
    critics, skills, planners and success judges. *Memory, Agents, Policies* (hylo-memory, hylo-agents,
    hylo-policies).

    [Policies →](user-guide/policies.md)

-   **2 · Runtime**

    ---

    Run policies on robots in real time, within the safety limits you set. A workcell runs the same episode loop
    as the benchmark, behind the SafetyShield and an operator channel. *Hylo Serve* (hylo-serve).

    [Deployment →](user-guide/deployment.md) · [Safety →](user-guide/safety.md)

-   **1 · Kernel**

    ---

    One execution kernel connects models, simulators and robots through versioned plugin contracts, and keeps
    every run in one store. *Hylo Core, Plugins* (hylo-core, hylo-plugins).

    [Concepts →](getting-started/concepts.md) · [Store →](user-guide/store.md)

</div>

![How the repositories fit together: simulators, robots and models reach the kernel through adapters; bench, serve, studio and plugins build on the harness](assets/diagrams/architecture.svg){ .hylo-figure }


## Results recorded so far

| What | Result | Where |
|---|---|---|
| Reference policies on `mujoco-reach` (100 held-out episodes) | mpc 86%, flow + steering 84%, bc + temporal ensemble 83%, flow 83%, bc 71%, tokens 68%, knn 64%; the IK expert 100% | [Leaderboard](benchmarking/leaderboard.md) |
| A gated campaign on MuJoCo reach | held-out success 0.40 → 1.00 after promotion | [Campaigns](user-guide/campaigns.md) |
| SmolVLA on LIBERO-10, as a robot would run it | 0.20 success with the world waiting for each call, 0.05 in real time (2 tasks × 10 init states, 19 hold steps per episode; too few episodes for a conclusion) | [RFC-0005](rfcs/RFC-0005-architecture-measurement-and-placement.md) |
| A success judge for LIBERO-10 trained from traces | AUC 0.92 against simulator outcomes (600 episodes) | [Experiment record](research/experiments/2026-10-31-success-judges-libero10.md) |

These are small studies, recorded with their commands and versions. The [plugin catalogue](developer-guide/plugin-catalogue.md)
says which parts have run end to end and which have not.

## The repositories

| Repository | Layers | What it holds |
|---|---|---|
| **hylo-harness** | kernel, cognition, evaluation, evolution | contracts and the execution kernel, the evaluation engine, agents, memory, learning, campaigns, the run catalog and store, adapters to policy stacks and LLMs, the `hylo` command |
| **hylo-bench** | evaluation | protocols, scorecards and leaderboards; the MuJoCo and LIBERO suites and their setup |
| **hylo-serve** | runtime | policy server, workcell, real-time runner, operator channel, robot adapters |
| **hylo-studio** | workbench | run explorer, live sandbox, campaigns and approvals, the control plane for workcells |
| **hylo-plugins** | kernel | example and community plugins, written the way a third party would |
| **hylo-deployments-template** | runtime | template for a lab's private configuration: workcells, calibration, safety limits |
| **hylo-docs** | | this site |

Every leaf builds on the harness alone and cooperates with the others through formats defined in `hylo-core`
([repository structure](design/repository-structure.md)).

[Design overview](design/overview.md){ .md-button }
[Extending](harness/extending.md){ .md-button }
[CLI reference](cli/index.md){ .md-button }
[Plugin catalogue](developer-guide/plugin-catalogue.md){ .md-button }
