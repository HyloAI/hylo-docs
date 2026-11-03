# Concepts

Hylo is organised around **Physical RSI, Worlds, Agents, Memory and Skills**. Physical RSI is the improvement
loop connecting the other four: agents act in worlds, memory carries experience forward, and skills make verified
capabilities reusable. The operational terms used by commands and configs are listed below.

## Physical RSI

Physical recursive self-improvement uses task outcomes to propose changes, verify them and carry adopted changes
into later rounds. A campaign implements the comparison and promotion process; learning supplies new artifacts.
Read [Physical RSI](../physical-rsi.md) for the loop and its boundaries, then
[Campaigns](../user-guide/campaigns.md) to run an improvement experiment.

## Worlds

A world is a simulation built from a scene description with robots, objects, cameras and goals. It provides a place
for agents to act and receive measured feedback. Benchmark environments provide fixed tasks for comparison;
robot adapters connect execution to hardware. See [Worlds](../user-guide/worlds.md).

## Agents

An agent decides actions from observations and instructions. It can run a policy, execute a program or let a model
call typed tools. Policies, planners and memory are components an agent may use. See
[Agents](../user-guide/agents.md) to choose an approach.

## Memory

Memory carries observations and experience into later decisions: spatial facts, successful action segments and
lessons from previous attempts. Different memories have different write and retrieval rules; evaluation must
respect their data boundaries. See [Memory](../user-guide/memory/index.md).

## Skills

A skill is a reusable task capability with stated applicability and evidence. Supported library records let agents
reuse programs, recipes and other verified changes. Memory answers what was observed or learned; skills describe
what can be applied to do a task. See [Skills](../user-guide/skills.md) and the
[Skill library](../user-guide/memory/skills.md). Library support depends on the implementation and consuming agent.

## Working terms

These terms name the mechanisms used to operate the five concepts. Follow the linked guides for their rules.

??? info "Execution: experiments, agents and records"

    | Term | Meaning |
    |---|---|
    | <span id="experiment"></span>Experiment | A config naming the benchmark split, environment, agent, safety and timing; each execution produces a run. See [Experiments](../user-guide/experiments.md). |
    | <span id="environment"></span>Environment | The simulator or robot interface supplying observations, actions and control rate. |
    | <span id="agent"></span>Agent | The logic deciding actions, using a policy, program or model with tools. |
    | <span id="policy"></span>Policy | A model or controller producing actions from observations. See [Policies](../user-guide/policies.md). |
    | <span id="run"></span>Run | The record of an execution: manifest, episode results and traces. |
    | <span id="episode"></span>Episode | One attempt at a task from an initial state until termination. |
    | <span id="trace"></span>Trace | The episode's event log: observations, proposed and executed actions, checks and outcomes. |
    | <span id="safety-shield"></span>Safety shield | The action checkpoint between the agent and environment. See [Safety](../user-guide/safety.md). |
    | <span id="timing"></span>Timing | Whether simulation waits for inference (`sync`) or continues while it computes (`realtime`). See [Timing](../user-guide/experiments.md#timing-sync-and-realtime). |
    | <span id="digest"></span>Digest | A hash of measured config settings; it excludes most placement settings but includes a `remote.ws` URL. It does not cover code versions. See [comparability](../user-guide/experiments.md#what-is-measured-the-digest). |

??? info "Development and reuse"

    | Term | Meaning |
    |---|---|
    | <span id="robot-skill"></span>Robot skill | A task capability under stated robot, scene and observation conditions, with implementation and evidence. |
    | <span id="task-strategy"></span>Task strategy | The task logic implemented by a policy, controller or program. |
    | <span id="robot-tools"></span>Robot contract and tools | The robot description and tools for perception, grasping, planning and execution. |
    | <span id="program-agent"></span>Program agent | `code.program` executes a task program; `code.llm` writes code during an episode. See [Developing programs](../user-guide/developing-strategies.md). |
    | <span id="research-session"></span>Research session | Model-assisted program development on development cases, producing a qualifying frozen submission. See [Program research](../user-guide/research-and-skills.md). |
    | <span id="program-skill"></span>Program skill | A library record referencing a promoted program, its applicability and evidence. |
    | <span id="coding-agent-skill"></span>Coding-agent skill | A `SKILL.md` instruction file teaching a software agent to operate Hylo. |

??? info "Improvement and evaluation"

    | Term | Meaning |
    |---|---|
    | <span id="artifact"></span>Artifact | A sealed derived result with a digest and provenance, such as weights, a memory bank or a program. See [Learning](../user-guide/learning.md). |
    | <span id="campaign"></span>Campaign | A process proposing changes, evaluating them and promoting at most one per cycle after its gate. See [Campaigns](../user-guide/campaigns.md). |
    | <span id="learner"></span>Learner | A plugin producing an artifact from permitted data; the split guard refuses gate and held-out runs. |
    | <span id="judge"></span>Judge | An instrument labelling outcomes without ground truth, calibrated against known outcomes. |
    | <span id="generator"></span>Generator and candidate | A generator proposes candidate config changes; the YAML key is `proposer`. Protected settings cannot be changed by candidates. |
    | <span id="split"></span>Split | A named set of initial states. Campaigns use `search`, `search_val`, `gate` and `heldout`; see [access rules](../user-guide/campaigns.md#splits). |
    | <span id="gate"></span>Gate | The confirmatory paired test on the gate split, with regression and safety vetoes. |
    | <span id="active-version"></span>Active version | The campaign version recorded in `active.json`; manual approval delays activation. Activation alone does not deploy a robot. |
    | <span id="evaluation-protocol"></span>Evaluation protocol | Fixed episodes, seeds, timing and scoring for comparable scorecards. A leaderboard ranks results under one protocol. See [Benchmarking](../benchmarking/index.md). |

??? info "Deployment and configuration"

    | Term | Meaning |
    |---|---|
    | <span id="workcell"></span>Workcell | The process next to a robot or simulator that runs episodes, records them and accepts operator commands. See [Deployment](../user-guide/deployment.md). |
    | <span id="policy-server"></span>Policy server | Serves an agent over the network; with `--campaign`, it follows the active version. |
    | <span id="store-id"></span>Store id | A run or artifact reference resolved to a local path on each machine. See [Store](../user-guide/store.md). |
    | <span id="runtime"></span>Runtime and execution profile | A runtime names an interpreter and environment; the profile locates runtimes and the store on a machine. See [Profiles](../configuration/profiles.md). |
    | <span id="plugin"></span>Plugin | An installed implementation found through a registered name. See [Extending](../harness/extending.md). |

## Next

- [Quickstart](quickstart.md): run the CPU example through execution, evaluation and improvement.
- [Agents](../user-guide/agents.md): choose how to act in a world or benchmark.
- [Architecture](../design/overview.md): how the implementation connects these concepts.
