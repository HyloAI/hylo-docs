---
hide:
  - navigation
  - toc
---

<div class="hylo-hero" markdown>

# Hylo

<p class="hylo-tagline">Evaluate robot policies, learn from what they did, improve them behind a statistical gate, and run
the approved version on a robot, with one set of contracts from simulation to hardware.</p>

[Get started](getting-started/installation.md){ .md-button .md-button--primary }
[Quickstart](getting-started/quickstart.md){ .md-button }
[Concepts](getting-started/concepts.md){ .md-button }

</div>

![Hylo layers: simulators, robots and models reach the harness through adapters; bench, serve, studio and plugins build on the harness](assets/diagrams/architecture.svg){ .wc-figure }

## What it does

<div class="grid cards" markdown>

-   **Measure**

    ---

    An experiment config says what is measured; where it runs is a property of the machine. Every episode is
    traced step by step, and a digest identifies the experiment on any computer.

    [Experiments →](user-guide/experiments.md)

-   **Benchmark**

    ---

    Protocols fix the episodes, seeds and timing; scorecards carry Wilson intervals; leaderboards compare
    policies, and pairs are tested with McNemar.

    [Benchmarking →](benchmarking/index.md)

-   **Run any policy**

    ---

    One chunk-policy contract covers retrieval, behaviour cloning, flow matching, tokenized actions and
    model-based planning, plus SmolVLA and pi0 through LeRobot and openpi.

    [Policies →](user-guide/policies.md)

-   **Learn**

    ---

    Learners turn development runs into sealed, digest-pinned artifacts: critics, memories, world models,
    success judges. Gate and held-out data can never be read.

    [Learning →](user-guide/learning.md)

-   **Improve, behind a gate**

    ---

    Campaigns propose candidates, screen them, and promote only what passes a sequential paired test on
    episodes no learner has seen, after a person approves.

    [Campaigns →](user-guide/campaigns.md)

-   **Deploy**

    ---

    A workcell runs the same episode loop as the benchmark, in real time, behind the SafetyShield and an
    operator channel; a policy server serves the approved version.

    [Deployment →](user-guide/deployment.md)

</div>

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

| Repository | What it holds |
|---|---|
| **hylo-harness** | the base: contracts and episode kernel, evaluation, agents, memory, learning, campaigns, the run catalog and store, adapters to policy stacks and LLMs, the `hylo` command |
| **hylo-bench** | protocols, scorecards and leaderboards; the MuJoCo and LIBERO suites and their setup |
| **hylo-serve** | policy server, workcell, real-time runner, operator channel, robot adapters |
| **hylo-studio** | the playground: run explorer, live sandbox, campaigns, the control plane for workcells |
| **hylo-plugins** | example and community plugins, written the way a third party would |
| **hylo-docs** | this site: design, RFCs, research notes and experiment records |
| **deployments-template** | template for a lab's private configuration: workcells, calibration, safety limits |

Every leaf builds on the harness alone and cooperates with the others through formats defined in `hylo-core`
([repository structure](design/repository-structure.md)).

[Design overview](design/overview.md){ .md-button }
[Extending](harness/extending.md){ .md-button }
[CLI reference](cli/index.md){ .md-button }
[Plugin catalogue](developer-guide/plugin-catalogue.md){ .md-button }
