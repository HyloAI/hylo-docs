# Architecture overview

This page maps [Physical RSI, Worlds, Agents, Memory and Skills](../getting-started/concepts.md) to their
implementation: execution, recorded evidence, evaluation, improvement and deployment.

## At a glance

![Hylo architecture at a glance: proposers, candidates, gate and versions; the store; the agent, shield and environment loop; Serve; five properties](../assets/diagrams/architecture-glance-light.svg){ .hylo-diagram .only-light }
![Hylo architecture at a glance: proposers, candidates, gate and versions; the store; the agent, shield and environment loop; Serve; five properties](../assets/diagrams/architecture-glance-dark.svg){ .hylo-diagram .only-dark }

## Concepts and components

| Concept | Implementation | Details |
|---|---|---|
| RSI | learning jobs, candidate generation, evaluation gates, version registry | [Campaigns](../user-guide/campaigns.md), [Learning](../user-guide/learning.md) |
| Worlds | stage descriptions, robot packs, simulator environments and goal checks | [Worlds](../user-guide/worlds.md) |
| Agents | policy agents, programs and typed tool calls through the episode loop | [Agents](../user-guide/agents.md) |
| Memory | spatial facts, scoped events, episode video, action banks and lesson books, with distinct consumers and lifetimes | [Memory](../user-guide/memory/index.md) |
| Skills | versioned library records, verification evidence, retrieval and application by supported agents | [Skills](../user-guide/skills.md) |

## Design goals

| Goal | Design response |
|---|---|
| A light core | `hylo-core` holds contracts, the episode loop, the safety shield, the trace and the plugin registry, and depends on a few small libraries; it contains no simulator, model, memory backend, scorer or improvement algorithm |
| No simulator is required | an environment is a contract; simulators and robots are plugins, and those with conflicting dependencies run in their own runtime behind the same contract |
| Not tied to a language model or a VLA | the episode loop knows only agents; policies, reasoners, memory and world models are parts of an agent |
| Reasoning, memory and improvement can each be replaced | separate packages that meet only through core contracts and the trace |
| Scores independent of the agent | scorers read traces only |
| Reproducible results | versioned configs with a digest, a run manifest, and seeds partitioned so that no seed crosses splits |
| Evidence from real simulators | a test double serves unit and conformance tests only; every example, protocol and campaign runs on a real simulator |
| Works with existing tools | an openpi-compatible policy server, LeRobot policies, robots and datasets |

## From runs to deployed versions

![Data flow: an experiment produces a run and traces, which give a scorecard; learners turn runs into artifacts, which candidates use; the gate decides, the active version goes to a workcell, and its episodes become runs](../assets/diagrams/architecture-light.svg){ .hylo-diagram .only-light }
![Data flow: an experiment produces a run and traces, which give a scorecard; learners turn runs into artifacts, which candidates use; the gate decides, the active version goes to a workcell, and its episodes become runs](../assets/diagrams/architecture-dark.svg){ .hylo-diagram .only-dark }

*The data flow behind Run, Improve, Verify and Deploy: the workcell's episodes become new runs.*

Experiments produce runs and traces. Evaluation scores them; learners turn permitted data into sealed artifacts.
Campaigns propose changes, test candidates and record promotions in `active.json`. A policy server can follow
that version, and a workcell records new episodes as ordinary runs. Promotion alone changes nothing on a robot:
the server and workcell must be configured, and hardware deployment requires human review and target validation.
See [Campaigns](../user-guide/campaigns.md) and [Deployment](../user-guide/deployment.md) for the operational rules.

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

## Layers

![The core holds the episode loop, the safety shield and the trace store. The loop asks an agent for actions and passes each through the shield to an environment, and records everything in the trace. Evaluation runs episodes on fixed splits and scores them from traces only. Improvement proposes candidates, evaluates them through the evaluation layer and promotes a version, which becomes the agent.](../assets/diagrams/layers-light.svg){ .hylo-diagram .only-light }
![The core holds the episode loop, the safety shield and the trace store. The loop asks an agent for actions and passes each through the shield to an environment, and records everything in the trace. Evaluation runs episodes on fixed splits and scores them from traces only. Improvement proposes candidates, evaluates them through the evaluation layer and promotes a version, which becomes the agent.](../assets/diagrams/layers-dark.svg){ .hylo-diagram .only-dark }

Each boundary in the picture stops one kind of coupling:

- **Agents and environments meet only in the loop.** An agent never touches an environment, and an environment never
  calls an agent. The loop passes observations one way and approved actions the other, so the shield cannot be
  bypassed and privileged simulator state can go to the trace without reaching the agent.
- **Evaluation sees episodes, not agents.** It decides which tasks and initial states run and scores the traces
  afterwards. Any agent is scored the same way, and a score can be recomputed from stored traces.
- **Improvement works through evaluation.** A campaign never measures anything itself: it asks the evaluation layer to
  run splits, and its only output is a version that becomes the agent. Improvement methods can be added without
  touching how anything is measured.
- **Packages depend downwards only.** Agents, memory, evaluation and improvement depend on the core, never on each
  other's internals; a boundary check enforces it.

## What an episode records

| Event | Written by | Used for |
|---|---|---|
| `episode.start` | episode loop | task digest, seed, split, agent component versions, guards |
| `observation` | episode loop | replay, training-data export |
| `agent.chunk` | episode loop | what the policy proposed, with latency and provenance |
| `agent.decision` | the agent's reasoner or planner | following its reasoning, diagnosing failures |
| `memory.retrieval`, `memory.write` | the agent's memory | whether memory helped or misled the agent |
| `safety.review` | safety shield | proposed and approved action, and why it was changed |
| `action` | episode loop | the action actually executed |
| `step.result` | episode loop | reward, termination, success, info |
| `privileged.state` | environment | ground truth for scorers and diagnosis only |
| `error` | episode loop | what failed, in which phase |
| `episode.end` | episode loop | success, failure, error, safety abort or invalid infrastructure |

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
| | adapters | `hylo-code-agents`, `hylo-tools`, `hylo-policy-lerobot`, `hylo-policy-openpi`, `hylo-policy-simplememvla`, `hylo-reasoner-llm`, `hylo-proposer-llm`, `hylo-data-video` |
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
| Experience as memory and skills, not only weights | Retrieved successes, lessons and skills steer a frozen policy and are cheap to roll back. Persistent experience banks and libraries are built from development data and frozen during evaluation; episode-local spatial, event and video memory can record permitted observations ([memory](../user-guide/memory/index.md#memory-and-its-consumers)). |
| A model decides what; deterministic layers decide what is valid and what happened | A language model edits a world through checked patches, acts through controllers, and learns the result only from measured receipts and checks, so its mistakes cannot make the world inconsistent ([worlds](../user-guide/worlds.md#from-language-to-a-world)). |
| Looking is separate from acting | A tool-calling agent may measure freely, but each action is a proposal tied to what was seen, answered by a measured receipt; the task's check, hidden from the model, decides success ([tool-calling agents](../user-guide/tool-agents.md#design)). |
| Everything learned is a sealed artifact with a role | Each role earns trust its own way, and provenance travels with the artifact ([learning](../user-guide/learning.md#design)). |
| Measurement separated from placement; one episode loop; store ids | The same identity on every machine, and the loop a robot runs. |
| One base repository and leaves | Changes to the base are atomic, the leaves stay independent, and the robot side stays small. |

## Alternatives considered

| Choice | Alternative | Why not |
|---|---|---|
| The episode loop owns execution | the benchmark owns the loop, or a language-model framework does | a benchmark-owned loop gives up per-step control, injected disturbances, isolation of privileged state and shadow replay; a model framework leaves safety and timing to code Hylo does not control |
| The agent is the only intelligence the loop knows | the loop orchestrates a reasoner and a policy itself | that builds one cognitive architecture into the core, and end-to-end models need no reasoner |
| An own event-sourced trace | a training-dataset format, service-tracing spans, or chat-model evaluation logs | none of them records reasoning, memory and safety and can also be replayed step by step; they are export targets instead |
| A plain loop, not an agent-graph framework | running control through a graph-execution framework | its per-step overhead does not fit control at 5 to 50 Hz, and it brings a heavy dependency into the core |
| Declarative candidates | letting a model generate and run code directly | without an isolated runtime that is unsafe; code enters only as sealed programs through research sessions, in a restricted namespace |
| Typed contracts that refuse unknown fields | plain data classes | a typo fails loudly, every contract has a JSON schema, and one serialisation path serves traces, protocols and configs; the cost was about 5 µs per step against a 20 ms budget |
| One base repository with leaf repositories | one repository per package, or a single package | per-package repositories need coordinated releases for every contract change; a single package cannot enforce layering or let anyone install the core alone |
| No pickle in any protocol | pickle for convenience | loading pickle runs code; arrays travel as typed, whitelisted data |

## Current limits

- Model-assisted development has recorded successes on specific simulated tasks. The promoted stacking program
  improves a deliberately weak parent; from-scratch local-model research remains unsuccessful. Free-scene and
  motion-free showcases and formal robosuite/RoboCasa program evaluations remain unrun.
- Program execution uses an in-process restricted namespace. Artifact/candidate validation and guard ordering
  have known gaps; see [Security](../user-guide/security.md) and [Showcase](../showcase/index.md).
- Campaigns run in the foreground of the shell that started them. Studio starts jobs as local subprocesses; it does
  not queue them.
- The robot path has run with a simulated arm. No physical robot has been connected.
