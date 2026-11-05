# Agents

An agent decides what a robot does from its observations and task instruction. Hylo supports agents that run
policies, execute programs or ask a language model to call robot tools. They share execution, safety checks and
recorded traces, so each approach can be evaluated under explicit task and observation conditions.

## Choose an agent

| You want to | Start with | Guide |
|---|---|---|
| Run an existing model or controller | a policy agent | [Policies](policies.md) |
| Give a policy subgoals, memory or steering | a composed or steered agent | [Policy agents](policies.md#agents-that-run-a-policy) |
| Run a compatible frozen VLA with episode video history | `simplememvla` | [Video memory](memory/video.md) |
| Execute a hand-written or frozen task program | `code.program` | [Programs](developing-strategies.md) |
| Let a model write task code during an episode | `code.llm` | [Programs](developing-strategies.md) |
| Let a model call typed robot tools one step at a time | `tools.llm` | [Tool-calling agents](tool-agents.md) |

![Three control modes: general models with tools, a planner with a VLA, and action models, all through the Hylo kernel](../assets/diagrams/control-modes-light.svg){ .hylo-diagram .only-light }
![Three control modes: general models with tools, a planner with a VLA, and action models, all through the Hylo kernel](../assets/diagrams/control-modes-dark.svg){ .hylo-diagram .only-dark }

A policy is a model or controller used by an agent. The agent decides how to use its output, including chunk
execution, steering and planning. A research session is a development process that produces a program; the
resulting program can then run through `code.program` without model calls.

## Decision mechanisms

### Policies

A policy maps observations to proposed actions, often as a chunk of future steps. The agent decides how much of
that chunk to execute before observing again. It can also sample alternatives, use a critic, apply recovery rules
or retrieve a memory prior when the policy supports those interfaces. Shorter chunks allow more frequent feedback;
longer chunks reduce inference calls but commit to more actions before replanning.

A composed agent can separate slower reasoning from the control policy: a reasoner chooses a target or subgoal,
while the policy produces the motion. Keeping these components inside the agent lets a direct action model and a
planner-driven model use the same episode loop. A technique requiring flow sampling, video context or a critic
still needs a compatible policy; composition does not supply missing model capabilities.

### Programs

A program expresses task logic explicitly: perceive, choose a target, call robot tools, inspect the result and
branch or retry. `code.program` runs an existing program; `code.llm` asks a model to write code during an episode.
Developing and freezing a program moves model calls into development, so later execution can reuse the same logic
without generating it again. Its behaviour still depends on new observations, tool results and the conditions
covered by its tests. Code execution uses the restrictions described in [Security](security.md#model-written-programs).

### Tool calls

A tool-calling model alternates between observations and typed requests. Read tools can measure targets or compute
grasp options without moving the robot. An action is submitted separately, executed through the episode kernel
and safety checks, and answered with a measured receipt. The model sees the effect before choosing its next action.

Target and grasp handles are tied to the observation that produced them. After motion, stale handles are refused
and the model must measure again. This prevents old coordinates from being treated as current facts. The task's
own check determines success independently of what the model reports when it finishes.

## Execution and evidence

The episode kernel binds an agent to an environment, checks their action compatibility, obtains observations,
asks the agent for actions and passes executed steps through the safety shield. Traces record proposed and
executed actions, interventions and outcomes. Scorers read that record, allowing different agent types to be
evaluated under the same protocol.

Observation privileges and timing remain part of the comparison. In synchronous execution the world waits for
inference; in realtime execution it continues and stale actions can be dropped. Two agents are comparable only
when the task, permitted observations, controller and evaluation conditions support the comparison. A shared
execution path alone does not make different benchmark results interchangeable.

## Integration { #worlds-memory-and-skills }

Agents act in an environment: a benchmark, a [world](worlds.md) or a robot adapter. The environment supplies
observations and actions; task checks and evaluation establish the outcome.

[Memory](memory/index.md) supplies observations and experience to the components that can use them.
[Skills](skills.md) provide reusable procedures or changes with stated applicability. Support depends on the
agent and skill kind: a code agent can call program skills, while role campaigns offer recipes after matching
goal failures. The [skill library](memory/skills.md) documents each consuming path.

## Evaluation { #evaluate-and-improve }

Record an [experiment](experiments.md), inspect its traces and compare agents under a fixed
[evaluation protocol](../benchmarking/protocols.md). Declare observation privileges and task conditions in the
comparison. A [campaign](campaigns.md) can propose and test changes to an existing agent as part of Physical RSI.

Program agents execute generated code with in-process restrictions; read the
[execution boundaries](security.md#model-written-programs). Measured successes and current failures are recorded
in the [Validation records](../developer-guide/validation/tool-agents.md).

## Next

- [Policies](policies.md): configure a policy and its agent.
- [Programs](developing-strategies.md): run and edit a task program.
- [Tool-calling agents](tool-agents.md): run, watch and steer a model through typed tools.
- [Robot-control walkthrough](agents/robot-control.md): watch a recorded episode with checked actions.
