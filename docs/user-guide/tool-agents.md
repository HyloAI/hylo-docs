# Tool agents { #tool-calling-agents }

`tools.llm` lets a chat model operate a robot through typed tools, one checked action at a time. The model can
measure freely: find objects, turn pixels into world points, compute, and ask for grasp poses. Every action it
takes is a proposal that runs through the kernel and the safety shield, and the next message brings a measured
receipt and fresh camera images. The task's own check decides success; the model never sees it.

Use it to try a model on a task without writing a program, to watch how a model approaches a robot problem, and to
collect conversations that worked. For a frozen, model-free implementation use `code.program`; for a model that
writes Python against the same tools use `code.llm` (see [Programs](developing-strategies.md)).

## Run an agent { #run-it }

The environment must publish a robot description (`mujoco.panda_table`, `mujoco.aloha_table`, `mujoco.g1_table`,
or `libero` in its tool mode). Complete [Installation](../getting-started/installation.md), configure
[camera rendering](../getting-started/optional-environments.md#camera-rendering), and make `qwen3.5:35b-a3b`
available at your Ollama endpoint. Run commands from the **workspace root**. Create `runs/configs/` and save
this complete configuration as `runs/configs/tools-llm-stack.yaml`:

```yaml
schema_version: hylo.experiment/v0.1
name: tools-llm-stack
benchmark: {type: mujoco/manip-v0, params: {tasks: [stack], validation: 3}, split: validation}
env: {type: mujoco.panda_table, params: {cameras: [front, side, wrist], segmentation: true}}
agent:
  type: tools.llm
  params:
    model: {backend: ollama, model: qwen3.5:35b-a3b, vision: true, reasoning_effort: none}
    max_decisions: 20        # actions that moved (or could have moved) the robot
    max_calls: 60            # model calls in the episode
    inbox: runs/steer/inbox.jsonl
trace: {record_privileged: false}
```

```bash
uv run hylo preflight runs/configs/tools-llm-stack.yaml --out runs/tools-llm-stack   # check before running
MUJOCO_GL=osmesa uv run hylo run runs/configs/tools-llm-stack.yaml
uv run hylo watch <run_dir>                                                     # follow it in the terminal
```

`hylo preflight` loads the config and its plugins, checks free storage, makes four live calls to the model (a text
reply, an image, a tool call with the right arguments, an answer that uses a tool result) and resets the
environment once. With `--out` the results are kept with the run.

Models: any OpenAI-compatible endpoint (Ollama, vLLM, DeepSeek), the Anthropic API, or a coding-agent CLI. Models
without native tool calls get the tools described in the prompt and write calls as fenced blocks. For local
reasoning models, `reasoning_effort: none` keeps replies short.

<video src="../../assets/videos/studio-live.mp4" poster="../../assets/videos/studio-live.jpg" controls muted playsinline preload="none" width="100%" aria-label="A tool-calling agent running one MuJoCo stack episode from the Studio's Live sandbox"></video>

*The same agent started from the Studio's Live sandbox: cameras (RGB, depth, segmentation) and the event log while a local model stacks two blocks, then the replay.*

## Tools

| Tool | Kind | What it does |
|---|---|---|
| `robot_state` | read | each arm's tool pose, joints, hand opening and whether it holds something |
| `look` | read | the camera images with each camera's position, direction and intrinsics |
| `locate` | read | objects described in words, measured in 3D; returns target handles and an outlined image |
| `pixel_to_world`, `world_to_pixel` | read | pixels to world points from depth (named points are cross-checked between cameras); points to pixels with occlusion evidence |
| `calc` | read | exact arithmetic with numpy and rotation helpers |
| `grasp_options`, `reach_check` | read | grasp poses for a target that fit the open hand; whether a pose is reachable |
| `read_artifact`, `report_issue` | read | reopen an older result the context stored; note an interface problem |
| `move_tcp` | action | move the tool point to a pose, on a collision-free path or in a straight line |
| `grasp`, `place` | action | execute a grasp option (approach, close, lift); put the held object at a point or on a target |
| `gripper`, `recover`, `wait` | action | open or close; back to the previous or home posture; let time pass |
| `finish` | end | success with the evidence, give up with a reason, or abort |

Rules the agent works under:

- Read tools can share one reply. An action must be the only call in its reply, and ends the model's turn.
- Target and grasp handles are tied to the moment they were measured; after the robot moves they are refused as
  stale and must be measured again.
- A refused action that moved nothing does not count as a decision. The same action refused three times in a row
  ends the episode.
- `finish(success)` states the model's view only. Episodes are scored by the task's check.

## Live control { #watch-and-steer }

```bash
uv run hylo watch runs/<run-dir>                        # the newest episode, followed while it runs
uv run hylo watch runs/<run-dir> --replay --speed 4     # a finished episode on its recorded timing
uv run hylo watch runs/<run-dir> --inbox runs/steer/inbox.jsonl --interactive   # type to steer
uv run hylo watch --say "the target is the small cup" --inbox runs/steer/inbox.jsonl
```

Each model turn, tool call, receipt and operator message is one line. A message sent to the inbox reaches the model
before its next call. Any message marks the episode `human_assisted`; such episodes do not count as autonomous
results and are left out of training exports.

<video src="../../assets/videos/terminal-watch.mp4" poster="../../assets/videos/terminal-watch.jpg" controls muted playsinline preload="none" width="100%" aria-label="hylo watch replaying a recorded tool-calling episode in a terminal"></video>

*`hylo watch --replay` on a recorded episode: each model turn, read calls in blue, actions in orange with their receipts, a refused call in red that the model then corrects, and the verdict.*

## Inspect results { #read-the-results }

Per episode, the trace has the model's turns (`agent.tool.turn`), every tool result, every action proposal and its
receipt, and a summary: model calls, decisions, refusals, tokens, cost, why it stopped, and the outcome the model
stated. The prompt is recorded by layer (protocol, evidence rules, boundary, robot description), each with a digest,
together with the digest of the tool set.

Inspect the [recorded trace example](../developer-guide/validation/guide-results.md#tool-agent-trace) for
model turns, proposals, receipts and the episode summary.

```bash
uv run hylo seal runs/<run-dir>             # check every hash chain, list every file, make the run read-only
uv run hylo seal --verify runs/<run-dir>    # anything changed, added or removed since sealing
uv run hylo chats runs/<run-dir> --out chats.jsonl   # successful, unsteered conversations as training records
```

Every trace line carries the hash of the line before it, so a changed, removed or reordered line is found. Sealing
is refused when a chain is broken or when a model-visible event contains privileged keys.

## Task variations { #perturbed-libero }

LIBERO tasks can be changed in seven ways, to measure what an agent or a policy relies on. Declare them on the
benchmark; each variant is its own task:

```yaml
benchmark:
  type: libero
  params: {suite: libero_goal, task_indices: [8], perturb: [position, language, task]}   # three variants
  # perturb: [[position, object]]                                                          # one combined variant
env: {type: libero, params: {control: joint_position, tool_obs: true, segmentation: true}}
```

![The seven perturbations on one LIBERO task](../assets/figures/libero-perturbations.jpg)

| Perturbation | What changes |
|---|---|
| `position` | the object the goal moves trades start positions with another movable object |
| `task` | a different goal in the same scene, with a rewritten instruction, checked by LIBERO's own goal predicate (27 of the 40 tasks of four suites have one) |
| `language` | the instruction is replaced by a paraphrase (three per instruction) |
| `object` | movable objects are recoloured |
| `camera` | the main camera moves about its view axis |
| `noise` | pixel noise and a glare spot on every image |
| `robot_init` | the arm starts from offset joints |

Every observation reports what was changed. Perturbations work in both LIBERO modes, for VLA policies as well as
tool agents.

## Control model { #why-tool-calls }

`tools.llm` lets a model call typed tools one step at a time. Each action returns a checked receipt before the
next decision, and the trace records the prompt, tools, observations and outcome. Use [program agents](developing-strategies.md)
when the model should write a reusable sequence of actions in Python.

<span id="design"></span>
<span id="recorded-robot-control-demo"></span>

## Next

- [Robot-control demo](../use-cases/robot-control.md): a recorded episode with checked actions.

- [Execution model](../developer-guide/execution-model.md#tool-calling-agents): runtime and implementation details.

- [Worlds](worlds.md): build scenes with other robots and let a model run them.
- [Programs](developing-strategies.md): programs and code agents with the same tools.
- [Validation records](../developer-guide/validation/tool-agents.md#tool-calling-agents): measured results and what does not work yet.
