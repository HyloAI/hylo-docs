# Execution model { #execution-and-improvement-model }

How execution, evaluation, learning and deployment fit together. For a first run, use the
[quickstart](../getting-started/quickstart.md); for system boundaries, read [Architecture](../design/overview.md).

## Experiments


**One episode loop for everything.** Evaluation, campaigns, the Studio's sandbox and a workcell next to a robot run
the same loop. When deployment had a loop of its own, what the gate approved in simulation was not what the robot
ran; with one loop it is.

**Everything an episode does is recorded, and everything else reads the record.** Each episode writes an append-only
event stream: observations, the agent's chunks and decisions, memory retrievals, every safety review, every executed
action, results. Scoring, diagnosis, replay, learners and the Studio read only these traces. Formats made for
training data, for service calls or for chat messages each miss some of this (reasoning, memory, safety) or cannot be
replayed, so the trace is Hylo's own and those formats are export targets.

**An experiment's identity is what it measures.** The digest covers the benchmark, environment, agent, safety, trace
and timing settings, and leaves out where the experiment runs: output directories, worker counts, interpreters and
paths. Configs name runtimes and store ids, and each machine resolves them, so the same experiment has the same
identity on a workstation, a GPU machine and a robot computer.

**Timing is part of the experiment.** In `sync` timing the world waits for every policy call; in `realtime` it does
not, and actions that went stale while the policy computed are dropped. A slow policy behaves differently on a robot
than in a waiting simulation, so the difference is something to measure, not to hide. Realtime runs on a
deterministic virtual clock in simulation, so it can be repeated.

**Problems surface before the first step.** The agent and the environment are checked for compatibility (control
mode, rotation format, action dimensions) when they are bound, and privileged simulator state goes to the trace for
scoring, never to the agent.

## Policy agents


**The loop knows only agents.** The episode loop calls an agent and nothing else. Policies, reasoners, memory and
world models live inside agents. Building a reasoner-plus-policy loop into the core would fix one way of thinking
about robots in place, and an end-to-end model that needs no reasoner would then be the odd one out.

**A policy proposes, an agent decides.** A policy samples action chunks from an observation. An agent decides how to
use them: how many to sample, which to take, how many steps to run before asking again, when to resample, whether
memory or a critic biases them. These components compose when their observation, action and conditioning
interfaces match. A technique that needs flow noise, critic inputs or video context requires a compatible policy.

**Randomness comes only from seeds.** A stochastic policy may draw its noise only from the seeds it is given, and
agents derive the seeds from the task, the chunk and the sample. Two agents compared on the same initial state draw
matching noise when the runtime uses the same draw order and batching protocol. Keep those conditions fixed in
paired comparisons: changing batch composition can change a shared RNG stream even with the same scene seeds.

**Heavy stacks stay out of process.** A policy with its own dependencies runs in its own runtime behind the same
contract, and its trace events are relayed to the episode. No simulator, model framework or vision-language-action
model is required by the core.

**The contract is checked, not assumed.** A conformance check runs every policy through shape, finiteness and seed
determinism before it is used.

## Evaluation


**Only the agent may differ.** A comparison means something only when everything except the agent was the same: the
tasks and their initial states, the environment, the safety settings, the timing, the scorers. A protocol fixes all
of these and leaves the agent as its single free input. It is versioned and digested, and changing anything in it
makes a new protocol rather than a different result under the old name.

**Scorers read traces, never agents.** A scorer sees what happened in an episode, recorded in its trace, and nothing
of the agent's internals. A vision-language-action model, a language-model agent and a hand-written program are
therefore scored in exactly the same way, and a score can be recomputed later from the stored traces. Privileged
simulator state goes into the trace for scoring and is never shown to the agent.

**Pair, do not pool.** Two agents are compared on the same tasks with the same seeds, episode by episode. Which
situations happened to be hard then cancels out, and only the pairs where exactly one agent succeeded carry
information. That is why two agents whose intervals overlap can still differ clearly, and why the same paired test
decides promotion in campaigns.

**Honest intervals at the edges.** Success rates are reported with Wilson intervals, which stay inside 0 to 1 and do
not collapse to a point at 100 of 100.

**What is measured, not where.** The digest covers what defines the measurement and leaves out where it ran
(machine paths, interpreters, worker counts), so the same protocol has the same identity on every machine. Code
versions are recorded beside each scorecard rather than inside the digest. Scorecards from different protocol
digests are refused, not compared.

**Timing is part of the measurement.** A policy that waits for the world (`sync`) and one that runs while the world
moves (`realtime`) are different measurements. A protocol can score what a robot would run, with a fixed latency;
never with a measured one, which would depend on the machine and its load.

## Campaigns


**An improvement is an experiment, not an edit.** A rule, a learner or a language model can propose a change; none of
them is trusted. A change is kept only when a paired test on initial states that played no part in proposing or
choosing it agrees, and every kept change can be undone. The proposer's confidence counts for nothing.

**Four splits, one job each.** Data that has been used to make a decision is no longer an independent test of that
decision. So the initial states are divided by job: `search` to diagnose failures (proposers see these),
`search_val` to choose among candidates, `gate` for one confirmatory test of the chosen candidate, and `heldout` for
the report to the person who approves, never used to choose. Choosing on gate data would turn the gate into one more
selection step; reporting on selection data would overstate the gain.

**Spend episodes where they can matter.** Episodes are the expensive resource, so the cascade orders its checks by
cost. Stage 0 costs nothing: protected settings, validity, novelty, the provenance of any artifact the candidate
names. Stage 1 runs a few pairs to drop clear losers. Stage 2 screens on all of `search_val`. Only the best reach the
gate.

**Pair everything.** Parent and candidate use matched initial states and episode seeds. Keep the model, controller,
batching and RNG protocol fixed when attributing a difference to memory or program changes. Scene seeds alone do
not guarantee identical policy noise under different batch schedules. The default paired success test uses the
pairs in which exactly one version succeeded.

**One error budget per cycle.** A cycle tests several candidates and may look at the gate more than once. Holm
correction across candidates and an alpha-spending schedule across looks keep the chance of promoting a change that
does not help at `alpha` per cycle.

**Better on average is not enough.** A candidate that raises the mean but breaks one task, or needs more safety
interventions, is vetoed: success on any task may not fall beyond a tolerance, and interventions may not rise beyond
one per episode.

**Changes are declarative, and the goalposts are protected.** A candidate is a config patch, which may name a sealed
artifact or a sealed program. It may not touch safety, the benchmark, the trace, the scorers, the environment or the
campaign's own settings: a change that raises its score by loosening safety or editing the scorer has improved
nothing.

**Cheap and reversible first.** Improvements form a ladder by cost and risk. A frozen policy is improved from the
bottom up, and every rung passes the same gate.

![Improvements are ordered by cost and risk. Steering settings and recovery rules need only rollouts and change nothing permanent. Learned components need training. Policy weights need hours of training and change the most. A frozen policy is improved from the bottom up; every rung goes through the same gate.](../assets/diagrams/improvement-ladder-light.svg){ .hylo-diagram .only-light }
![Improvements are ordered by cost and risk. Steering settings and recovery rules need only rollouts and change nothing permanent. Learned components need training. Policy weights need hours of training and change the most. A frozen policy is improved from the bottom up; every rung goes through the same gate.](../assets/diagrams/improvement-ladder-dark.svg){ .hylo-diagram .only-dark }

**Every promotion can be undone.** A candidate can be promoted only over the version that is active; the ledger
records every promotion and rollback, with who and why. Configure `approval: manual` for hardware deployment so
a person can review the held-out report before activation; the current campaign default is `auto`.

## Learning


**One pipeline for everything learned.** Learning from the agent's own runs, from demonstrations, from video, and
learning judges or world models all take the same path: data, an optional labeller, a learner, a sealed artifact, a
candidate, the gate. Before this pipeline, each learner had its own export, its own split guard and its own output
format; now a new learner only has to read runs and write an artifact.

**The trace store is the only source of truth.** Everything learned is derived from recorded runs, and a sealed
artifact records which runs and splits it read, which builder made it, with which parameters, and its content
digest. Persistent experience artifacts can use the same provenance pipeline as learned weights. Episode-local
observation memory has a separate lifecycle, described in [Memory](../user-guide/memory/index.md).

**Three roles, three ways to earn trust.** What an artifact is allowed to influence decides how it must be trusted.

![A behaviour artifact changes what the robot does and is trusted only through the gate. An instrument measures or labels and is trusted through calibration against ground truth. A proposal artifact changes what gets proposed and is trusted through outcome votes.](../assets/diagrams/trust-paths-light.svg){ .hylo-diagram .only-light }
![A behaviour artifact changes what the robot does and is trusted only through the gate. An instrument measures or labels and is trusted through calibration against ground truth. A proposal artifact changes what gets proposed and is trusted through outcome votes.](../assets/diagrams/trust-paths-dark.svg){ .hylo-diagram .only-dark }

An instrument never decides a gate verdict: in simulation the gate scores with ground truth, and a world model may
only decide which candidates are worth real episodes. An instrument is never calibrated on, and never labels, the
data it was built from. A model used in two roles is approved separately for each.

**Split integrity is enforced twice.** When an artifact is sealed, a guard refuses any provenance that includes gate
or held-out runs. When a candidate reaches the gate, stage 0 checks again that every artifact it names still has its
digest and never saw those splits. One bias is accepted and recorded: an artifact built from `search_val` can favour
itself in the screen that uses `search_val`; the gate split stays clean.

**Outside data comes in as runs.** External datasets and videos enter as runs under their own split, with origin,
licence and how their labels were made, and are checked against the gate and held-out initial states, so they follow
the same rules as everything else.

## Deployment


**Three roles in three places.** Computation goes where the accelerators are (the policy server); safety, timing and
the record go where the robot is (the workcell); people can watch and operate from anywhere (the control plane), but
the control plane holds nothing that moves and never sends actions. The roles can share one laptop or use three
machines without changing anything else.

**The robot runs the loop the gate approved.** The workcell runs the same episode loop as evaluation, in realtime
timing. What a campaign promoted in simulation is executed by the same code on the robot.

**The robot keeps moving while the policy thinks.** Inference takes time, and a robot can neither stop the world
nor execute actions that were planned for a moment that has passed. An action queue is refilled before it runs out,
actions that went stale during inference are dropped, the arm holds its position when the queue is empty, and a
watchdog ends the episode when the policy stops answering.

**Promotion changes nothing on a robot by itself.** A promoted version reaches the robot only when a policy server
follows the campaign's active version and a workcell connects to that server. Anything that runs on hardware should
be approved by a person first.

**Robot episodes never claim success.** There is no ground truth on a robot. An episode is labelled by the operator's
verdict or by a calibrated judge, and the label records which.

**The robot side stays small.** The serving package depends on the core alone, so the robot computer installs little,
and its episodes come back to the workstation as ordinary runs that can be scored, learned from and improved on.

## Tool-calling agents


![The chat model measures with read tools and gets results back. An action goes as a proposal through the kernel and the safety shield to the environment, and the model gets a measured receipt with new images. The task's check scores the episode and is hidden from the model. Every event is in a hash-chained trace.](../assets/diagrams/tool-agent-loop-light.svg){ .hylo-diagram .only-light }
![The chat model measures with read tools and gets results back. An action goes as a proposal through the kernel and the safety shield to the environment, and the model gets a measured receipt with new images. The task's check scores the episode and is hidden from the model. Every event is in a hash-chained trace.](../assets/diagrams/tool-agent-loop-dark.svg){ .hylo-diagram .only-dark }

**Looking is separate from acting.** Read tools (locate, measure, compute, ask for grasp poses) can be batched in one
reply and change nothing. An action must be the only call in its reply. It is recorded as a proposal tied to the
observation it was decided on, runs through the kernel and the safety shield, and is answered with a measured
receipt and fresh images. The model therefore sees the effect of every action before it decides the next one.

**Measurements expire.** A target or grasp handle is tied to the moment it was measured. Once the robot has moved,
an old handle is refused as stale and the model has to measure again: positions taken before a motion may no longer
be true after it.

**Refusing is not failing.** An action the shield or the planner refuses, and that moved nothing, does not count as a
decision, so a model is not punished for asking for something impossible and then correcting itself. Three identical
refusals in a row end the episode, so it cannot loop forever.

**The task decides success.** `finish(success)` records what the model believes. The episode is scored by the task's
own check, which the model never sees: a model that could see the check could stop the moment it passed, or argue
with it.

**Nothing is dropped from the record.** Long episodes outgrow the model's context, so what the model is sent is a
projection: recent turns verbatim, older results as references it can reopen, and under pressure a structured
summary. The conversation itself is append-only, and everything left out of the projection stays in the trace.

**The evidence holds up.** The prompt is recorded layer by layer with digests, every trace line carries the hash of
the line before it, and a sealed run can be checked later for any change. A person can steer a running episode, but
any message marks it as human-assisted, and such episodes are kept out of autonomous results and training exports.

**Tools are declared once.** Each tool is one declaration (a kind, a closed argument schema and structured help).
The same declaration serves native tool calls, a text protocol for models without them, the MCP server and these
docs, so they cannot drift apart.

**The same execution path as every agent.** A tool action becomes action chunks that the episode kernel executes
step by step through the safety shield, exactly as it does for a policy or a code agent. A model's run is therefore
scored, traced and limited in the same way as any other agent's, and the results can be compared directly.

??? info "Under the hood"

    - **Tool surface.** Every tool is typed: a name, a kind (`read`, `act` or `end`), a closed JSON schema for its
      arguments, and help in six parts (purpose, when to use, effect, returns, limits, errors). Calls are checked
      against the schema before they run; a bad call returns a structured error, not an exception.
    - **Model backends.** Messages use one neutral format with tool calls and tool results; adapters translate it for
      OpenAI-compatible endpoints (including reasoning replay for models that need it) and the Anthropic API. Models
      without native tool calls write fenced `tool` blocks, which are parsed into the same calls.
    - **Prompt layers.** The system prompt is built from four layers (protocol, evidence rules, boundary, robot
      description), each recorded with its digest.
    - **Context.** Older tool results are stored and replaced by references the model can reopen with `read_artifact`;
      under token pressure older turns are folded into a summary with seven fixed keys (`progress`, `confirmed`,
      `ruled_out`, `attempts`, `constraints`, `avoid`, `next_checks`). A tool call and its result are always
      kept or dropped together.

??? example "One recorded episode, call by call"

    The `stack` episode in the video, with `qwen3.5:35b-a3b` running locally:

    | Call | The model | The robot and the tools |
    |---|---|---|
    | 1 | locates both blocks in one reply: two read calls | purple block `t1` and green block `t2`, measured in 3D at step 0 |
    | 2 | asks for grasp options on `t1` | options that fit the open hand; `g3` is top-down with no IK error |
    | 3 | grasps with `g3`: an action, alone in its reply | proposal tied to step 0; receipt after 84 steps: closed with 0.6 mm error, lifted with 4.0 mm, holding before and after the lift |
    | 4 | locates the green block again, since the robot has moved and `t2` would now be refused as stale | the same block as `t7`, measured at step 84 |
    | 5 | places on `t7` | lowered and released with 1.4 mm error; the episode ends, and the task's check reports success |

    Five model calls, two decisions, no refusals, 127 control steps, 93 seconds of wall time.

## Worlds


The design starts from a division of labour. A language model is good at deciding what a scene should contain and
what to do next; it is unreliable at exact geometry, at remembering field names, and at judging its own results. A
simulator is exact, but knows nothing about what anyone wants. So the model decides what, and a chain of
deterministic layers turns that into a simulation and turns the simulation back into measured facts. Each layer
accepts only what it can check, and each boundary is there to stop one kind of mistake.

![The chat model decides what to do and nothing else. Edits go as patches, are validated against a stage revision, and are compiled with robot packs into a MuJoCo model; a build starts a new world generation. Actions name that generation and run through controllers. What happened comes back as measured receipts and checks.](../assets/diagrams/world-layers-light.svg){ .hylo-diagram .only-light }
![The chat model decides what to do and nothing else. Edits go as patches, are validated against a stage revision, and are compiled with robot packs into a MuJoCo model; a build starts a new world generation. Actions name that generation and run through controllers. What happened comes back as measured receipts and checks.](../assets/diagrams/world-layers-dark.svg){ .hylo-diagram .only-dark }

**Language to patches.** The model never writes a scene file. It edits through tool calls whose arguments are
checked against a closed schema: add, remove, update or move one entity. A scene file written in one piece is long,
fails as a whole, and cannot be compared or merged with someone else's change. A patch is small, says exactly what
it changes, and can be checked before anything happens.

**Patches to stage revisions.** The stage is the single description of the scene, shared by the model, the Studio
and a person. A patch is validated as a whole (unique names, existing parents, no mounting cycles, valid rotations,
one geometry per entity) and applied to the revision it was based on. A valid patch makes a new revision; an
invalid or outdated one changes nothing. Because every revision is kept, every step can be undone.

**Stage to compiled model.** A robot is named, not described: the stage says `pack: go2`, and the pack supplies the
model files at a pinned commit, the home posture, the drive, the gripper and the controls. Compilation attaches each
robot under its own prefix in one MuJoCo model, together with the shapes, meshes, cameras, lights and people. A
language model cannot be expected to write a robot model, and a robot model written anew for each scene would never
be the same twice.

**Compiled model to world.** A build starts a new generation of the world and reports what is hard to see in data:
which entities are fixed in place and which can move, and which parts overlap at the start. Problems surface before
anything moves, and the generation is what every later action is bound to.

**Actions through controllers.** The model asks for intents at its own pace: walk forward at this speed, move the
tool point there, fly to this point, run this walking policy. Controllers turn each intent into control at the
simulation rate (a trot gait, inverse kinematics, attitude control, a pretrained policy). A model decides once every
few seconds; a robot needs commands hundreds of times a second, so the model is never asked for joint torques.

**World to receipts and checks.** What happened is measured by the simulation and returned as receipts (distance,
turn, joint error, whether the gripper holds something). Goals are predicates evaluated on the world, and a failure
names what was expected, what was measured and why (`NOT_LIFTED`, `DISTANCE_NOT_MET`). These are the model's only
source of facts about the result, and the feedback it corrects itself with: a refused patch is fixed, an overlap is
moved apart, a failed check leads to another action.

The model can be wrong at every step without the world becoming inconsistent: a bad patch is refused, a stale
action is refused, an impossible request returns as a failed receipt, an unmet goal is reported with its
measurements. What the layers cannot prevent is a model that misreports its result or rewrites its own goal (a local
model was recorded lowering its own threshold until the check passed). That is why a goal that decides success is
defined outside the session, as in [role campaigns](../user-guide/worlds.md#tasks-with-roles), and why results are read from receipts and
checks rather than from the model's summary.


**Actions are bound to what was seen.** A model decides on a picture of the past. An action names the generation it
was decided on, and after a rebuild or a reset an old action is refused as stale. An action id makes retries safe:
the same id never runs twice. Several robots' actions in one call start in the same step.

**Time passes only during actions.** While the model thinks, the world stands still, so a slow model sees the same
world as a fast one and a session can be replayed.

**Robots come from pinned sources, and weights are never executed.** Robot models are fetched from their public
repositories at a fixed commit and checked file by file; nothing is vendored. Pretrained walking policies are read
from their files as tensors and run with numpy, and a policy is refused when its joints or timing do not match the
robot.

**The same tools for everyone.** A chat model, a person in the Studio, a coding agent over MCP and a role campaign
all use the same tools, so whatever a model claims it did can be checked with the same calls.
