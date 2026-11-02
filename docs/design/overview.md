# Architecture overview

This page maps the robot-skill lifecycle onto the execution, evaluation, improvement and deployment mechanisms,
and explains what checks each hand-off. [Robot skills](../user-guide/skills.md) defines the user-facing lifecycle;
[Concepts](../getting-started/concepts.md) defines the terms.

## From skill requirements to validated implementations

A skill is a task capability with stated applicability, implementation, evidence and version/dependencies. The
architecture supports these through existing task specs, agents, runs, artifacts, campaigns and skill-library
records. It does not yet give every policy a common skill record or expose a universal skill dashboard.

| Skill activity | Implementation | Main project |
|---|---|---|
| Develop | robot tools, program agents, model integration and research sessions | Harness |
| Run | agent/environment contracts, kernel, SafetyShield and traces | Harness, Serve |
| Validate | task environments, evaluation protocols, scorecards and gate tests | Bench, Harness Eval |
| Improve | learning, candidate generation, paired gates and version registry | Harness Learn/Evolve |
| Deploy | policy server, robot adapter, workcell and operator channel | Serve |
| Inspect and reuse | research/run/campaign views, skill libraries and program-skill retrieval | Studio, Harness Memory/Code Agents |

![Task requirements and robot tools produce a program; programs and existing policies use shared execution and recorded validation](../assets/diagrams/strategy-development-light.svg){ .hylo-diagram .only-light }
![Task requirements and robot tools produce a program; programs and existing policies use shared execution and recorded validation](../assets/diagrams/strategy-development-dark.svg){ .hylo-diagram .only-dark }

Strategy development addresses the programming and integration between a task requirement and working robot
behaviour. The robot contract in core describes the hardware; `hylo-manip` provides perception, grasping and
planning tools; code agents combine them into task programs. Heavy model tools run in independent workers.

A new task can start with a hand-written program or model-assisted development, followed by execution and
validation against task requirements. An existing strategy can enter an improvement campaign for a paired
comparison and promotion. Existing model policies enter the execution loop directly. These are starting points
into the same stack, with different validation claims. See [Developing robot skills](../user-guide/developing-strategies.md)
and [Skill research, validation and reuse](../user-guide/research-and-skills.md).

## From runs to deployed versions

![Data flow: an experiment produces a run and traces, which give a scorecard; learners turn runs into artifacts, which candidates use; the gate decides, the active version goes to a workcell, and its episodes become runs](../assets/diagrams/architecture-light.svg){ .hylo-diagram .only-light }
![Data flow: an experiment produces a run and traces, which give a scorecard; learners turn runs into artifacts, which candidates use; the gate decides, the active version goes to a workcell, and its episodes become runs](../assets/diagrams/architecture-dark.svg){ .hylo-diagram .only-dark }

*Run, Measure, Improve and Deploy as one loop: the workcell's episodes become new runs.*

1. **Run.** An [experiment](../user-guide/experiments.md) runs one split of a benchmark. It records one trace per
   episode and the results, and the store files the run under an id.
2. **Measure.** An evaluation protocol fixes everything except the agent being scored, and writes a
   [scorecard](../benchmarking/index.md). A leaderboard ranks the scorecards of one protocol.
3. **Improve: artifacts.** [Learners](../user-guide/learning.md) build artifacts from runs: memories, critics, judges, world
   models, policy weights. Each is sealed with a content digest and its source runs
   ([artifact roles](../user-guide/learning.md#artifact-roles)).
4. **Improve: candidates.** Generators propose candidates as config patches, including sealed program references.
   Research sessions develop code on development cases; their model does not see gate or held-out outcomes.
   Other generators can read the campaign archive, including past candidates' gate results
   ([who reads which split](../user-guide/campaigns.md#splits)).
5. **Improve: the gate.** A [campaign](../user-guide/campaigns.md)'s stage-0 checks reject candidates that touch
   protected settings. The rest are screened against the current version on `search_val`, and the best is tested
   by the gate on the `gate` split. The gate never reads `heldout`.
6. **Improve: promotion.** A candidate that passes becomes the campaign's active version (`active.json`), which a policy
   server can follow. By default this is automatic. Use `approval: manual` for anything that runs on hardware, so a
   person approves first. `hylo evolve rollback` undoes a promotion.
7. **Deploy.** Promotion alone changes nothing on a robot. A policy server must follow the campaign's
   `active.json`, and a [workcell](../user-guide/deployment.md) must connect to that server. The workcell runs the
   active version through the same episode loop, and its episodes are recorded as runs that flow back through the
   store to step 1.

## One episode loop

One episode loop runs every episode: in evaluation, in Studio's live sandbox and in a workcell next to a robot. It
passes every action through the safety shield, and every step emits events that a trace store writes per episode.
Replay, scoring, judges, learners and Studio all read these traces. Timing (`sync` by default, or `realtime`) is
part of what an experiment measures ([timing](../user-guide/experiments.md#timing-sync-and-realtime)). Realtime
uses a deterministic virtual clock by default; on hardware, set `clock: wall`
([deployment](../user-guide/deployment.md)).

## Three rules

1. **The episode loop only knows contracts.** It runs an agent against an environment. Policies, memories,
   reasoners and world models live inside agents. Any simulator, robot or policy stack plugs in as a plugin.
2. **Every action passes the safety shield.** Agents cannot bypass it, and campaign candidates may not change the
   safety settings. Overrides you write into a campaign config yourself are not checked
   ([what is protected](../user-guide/safety.md#safety-in-campaigns)).
3. **Scoring reads traces only.** A scorer sees what happened, never the agent's internals.

## Measurement vs placement

An experiment's identity is what it measures. Configs name runtimes and store ids, never paths, and each machine
resolves them ([profiles](../configuration/profiles.md), [store](../user-guide/store.md)). So an experiment has the
same digest on every machine; the one placement detail that is hashed is a `remote.ws` URL. The digest does not
cover code versions or unpinned artifacts
([when two runs are comparable](../user-guide/experiments.md#what-is-measured-the-digest)). A result in simulation
does not by itself predict the result on a robot.

## Packages and repositories

![The repositories: bench, serve, studio and plugins build on hylo-harness; serve needs hylo-core only; docs and the deployments template hold no code](../assets/diagrams/repositories-light.svg){ .hylo-diagram .only-light }
![The repositories: bench, serve, studio and plugins build on hylo-harness; serve needs hylo-core only; docs and the deployments template hold no code](../assets/diagrams/repositories-dark.svg){ .hylo-diagram .only-dark }

*The harness is the base, and the leaf repositories depend on it only.*

| Repository | Package | What it holds |
|---|---|---|
| **hylo-harness** | `hylo-core` | contracts, episode loop, safety shield, traces, plugin registry, store, `hylo` command |
| | `hylo-eval` | benchmarks, splits, runner, scorers, paired statistics, gate tests |
| | `hylo-agents` | agents that run a policy: plain, ensembled, steered; baselines |
| | `hylo-policies` | reference policies, one per family, trained from your runs |
| | `hylo-memory` | action memory, lessons, skills |
| | `hylo-reasoners` | rule-based reasoners and choosers |
| | `hylo-instruments` | success judges, value models, world models: they never act |
| | `hylo-learn` | learner jobs, judge calibration and labelling, external data |
| | `hylo-evolve` | campaigns: generators, the cascade, the gate, approvals, active versions |
| | `hylo-catalog` | read-only queries over runs, campaigns and artifacts |
| | `hylo-cli` | the harness's `hylo` subcommands |
| | `hylo-manip` | robot tools: perception, kinematics, grasping and planning; current kinematics backend: MuJoCo |
| | adapters | `hylo-code-agents`, `hylo-tools`, `hylo-policy-lerobot`, `hylo-policy-openpi`, `hylo-reasoner-llm`, `hylo-proposer-llm`, `hylo-data-video` |
| **hylo-bench** | `hylo-bench` | evaluation protocols, scorecards, leaderboards, paired comparison |
| | `hylo-robosuite-contract` | shared robot-contract mapping for robosuite-based environments |
| | adapters | `hylo-env-mujoco`, `hylo-env-libero`, `hylo-env-robosuite`, `hylo-env-robocasa` |
| **hylo-serve** | `hylo-serve` | the policy server and the workcell |
| | adapters | `hylo-env-lerobot-robot`: LeRobot robots and a simulated arm |
| **hylo-studio** | `hylo-playground` | research/session record viewer, run explorer, web UI and workcell control plane |
| **hylo-plugins** | `hylo-plugin-examples` | example plugins, written as a third party would |
| **hylo-docs** | (no code) | this site |
| **hylo-deployments-template** | (no code) | a template for a lab's private workcell configs and safety limits |

Leaves never import each other, and serve's packages depend on `hylo-core` alone. Leaves cooperate only through
[formats](../api/formats.md) defined in `hylo-core`: traces, artifact manifests, store ids, scorecards, `active.json`
and the workcell API. A boundary lint enforces this ([contributing](../developer-guide/contributing.md)).

## Key decisions

| Decision | Why |
|---|---|
| A light core with contracts and plugins; heavy stacks out of process | No simulator, LLM or VLA is mandatory. Components with conflicting dependencies run in their own venvs. |
| Improvement is a gated experiment | A change is kept only if a paired test on unseen initial states agrees ([campaigns](../user-guide/campaigns.md#design)). |
| Experience as memory and skills, not only weights | Retrieved successes, lessons and skills steer a frozen policy and are cheap to roll back. Each kind of memory serves one layer of an agent, is built only from verified development data, and is frozen during evaluation ([memory](../user-guide/memory/index.md#memory-at-four-layers-of-an-agent)). |
| A model decides what; deterministic layers decide what is valid and what happened | A language model edits a world through checked patches, acts through controllers, and learns the result only from measured receipts and checks, so its mistakes cannot make the world inconsistent ([worlds](../user-guide/worlds.md#from-language-to-a-world)). |
| Looking is separate from acting | A tool-calling agent may measure freely, but each action is a proposal tied to what was seen, answered by a measured receipt; the task's check, hidden from the model, decides success ([tool-calling agents](../user-guide/tool-agents.md#design)). |
| Everything learned is a sealed artifact with a role | Each role earns trust its own way, and provenance travels with the artifact ([learning](../user-guide/learning.md#design)). |
| Measurement separated from placement; one episode loop; store ids | The same identity on every machine, and the loop a robot runs. |
| One base repository and leaves | Changes to the base are atomic, the leaves stay independent, and the robot side stays small. |

## Current limits

- Model-assisted development has recorded successes on specific simulated tasks. The promoted stacking program
  improves a deliberately weak parent; from-scratch local-model research remains unsuccessful. Free-scene and
  motion-free showcases and formal robosuite/RoboCasa program evaluations remain unrun.
- Program execution uses an in-process restricted namespace. Artifact/candidate validation and guard ordering
  have known gaps; see [Security](../user-guide/security.md) and [Showcase](../showcase/index.md).
- Campaigns run in the foreground of the shell that started them. Studio starts jobs as local subprocesses; it does
  not queue them.
- The robot path has run with a simulated arm. No physical robot has been connected.
