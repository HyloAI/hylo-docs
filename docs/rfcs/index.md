# RFCs

Design decisions that change contracts, formats, what an experiment measures, or how the repositories fit together
are written as RFCs before (or while) they are implemented. Each RFC records its status at the top; this table
repeats it.

| RFC | Title | Status | In one line |
|---|---|---|---|
| [RFC-0001](RFC-0001.md) | Harness core architecture and v0.1 scope | Accepted with amendments (2026-10-30) | the contracts, the kernel, plugins by entry point, heavy components out of process, and what v0.1 includes |
| [RFC-0002](RFC-0002-physical-rsi.md) | Physical RSI on LIBERO (frozen VLA first, weights second) | Implemented (2026-10-30/31); weight-level units unverified | improvement as a gated experiment: development, gate and held-out splits of init states, a cascade and a sequential paired test, approval before promotion |
| [RFC-0003](RFC-0003-experience-memory-skills.md) | Experience memory and skills | Draft (2026-10-30) | action memories of verified successes, lessons and skills that steer a frozen policy |
| [RFC-0004](RFC-0004-learning-pipeline.md) | Learning pipeline and derived artifacts | Implemented (A1-A3, W1-W4; video world models and RL fine-tuning wait for a GPU) | learners build sealed artifacts with provenance and a role (behaviour, instrument, proposal); one split guard; calibrated judges |
| [RFC-0005](RFC-0005-architecture-measurement-and-placement.md) | What is measured, where it runs, and one episode loop | Parts 1-4 implemented (2026-10-31, 2026-11-01); part 5 partly; part 6 proposed | experiments vs execution profiles, one episode loop, a run and artifact store, contract versions and plugin metadata |
| [RFC-0006](RFC-0006-tool-using-agents.md) | Tool-using agents, program candidates and the manipulation toolkit | All parts implemented (2026-11-01/02) | agents that write programs against robot tools, programs as gated candidates and skills, a Panda tabletop task set |
| [RFC-0007](RFC-0007-tool-calling-robot-agents.md) | Tool-calling robot agents, run evidence and perturbed LIBERO | Parts 1-9 implemented (2026-11-02) | a model calls typed robot tools one checked action at a time; lossless context; hash-chained, sealed runs; watching and steering; seven LIBERO perturbations |
| [RFC-0008](RFC-0008-stage-worlds.md) | Stages, worlds and robot packs for model-driven robotics | Parts 1-11 implemented (2026-11-02) | scenes as revisioned entity trees, a MuJoCo world with 24 robot packs, actions with receipts, checks with reason codes, people, pretrained walking policies, role campaigns, the Studio world page |

Statuses are the RFCs' own status lines.

## RFCs on the loop

Each RFC builds part of the [Physical RSI](../physical-rsi.md) loop: Build, Run, Improve, Verify and Deploy. An RFC
can contribute to several activities.

| Activity | RFCs | What they contribute |
|---|---|---|
| Build | [RFC-0008](RFC-0008-stage-worlds.md), [RFC-0006](RFC-0006-tool-using-agents.md), [RFC-0007](RFC-0007-tool-calling-robot-agents.md), [RFC-0004](RFC-0004-learning-pipeline.md) | revisioned worlds from 24 robot packs, people and checks with reason codes; manipulation task sets, scene building and replay to simulation; LIBERO perturbations; outside data entering as runs |
| Run | [RFC-0006](RFC-0006-tool-using-agents.md), [RFC-0007](RFC-0007-tool-calling-robot-agents.md), [RFC-0005](RFC-0005-architecture-measurement-and-placement.md) | the robot contract, manipulation tools and program agents; one checked tool call at a time; one episode loop for every context |
| Improve | [RFC-0002](RFC-0002-physical-rsi.md), [RFC-0004](RFC-0004-learning-pipeline.md), [RFC-0003](RFC-0003-experience-memory-skills.md), [RFC-0006](RFC-0006-tool-using-agents.md) | campaigns and the improvement ladder; learners and sealed artifacts; memory and lessons from verified development experience; research sessions and programs as candidates |
| Verify | [RFC-0002](RFC-0002-physical-rsi.md), [RFC-0004](RFC-0004-learning-pipeline.md), [RFC-0005](RFC-0005-architecture-measurement-and-placement.md), [RFC-0007](RFC-0007-tool-calling-robot-agents.md), [RFC-0008](RFC-0008-stage-worlds.md) | splits, cascade and the paired gate; trust by artifact role; the run store and protocols; sealed runs; replay checks for recipes |
| Deploy | [RFC-0002](RFC-0002-physical-rsi.md), [RFC-0003](RFC-0003-experience-memory-skills.md), [RFC-0005](RFC-0005-architecture-measurement-and-placement.md) | promotion with approval and rollback; the skill library; execution profiles, placement and workcells |

Across the loop, [RFC-0001](RFC-0001.md) provides the contracts, the kernel, the safety shield and the trace, and
[RFC-0005](RFC-0005-architecture-measurement-and-placement.md) the placement of runtimes and model servers. Skills
connect Improve and Deploy: RFC-0003 defines the library, RFC-0006 supplies program skills and RFC-0008 supplies
replay-verified recipes.

## Writing an RFC

- Number it next (`RFC-0009-<slug>.md`) and add it to this table and to the navigation in `mkdocs.yml`.
- Start with a status table (status, scope, what it builds on), then the motivation: the concrete problem, found in
  the code or in a result.
- Give each part its own section with what changes, what it costs (for example, digests that change once), and how
  it was checked. Mark parts as proposed or implemented, with dates, as they land.
