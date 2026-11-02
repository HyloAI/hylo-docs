# RFC-0007: Tool-calling robot agents, run evidence and perturbed LIBERO

| | |
|---|---|
| Status | Parts 1-9 implemented (2026-11-02); first evaluations on the [showcase](../showcase/tool-agents.md#tool-calling-agents) |
| Scope | hylo-harness (hylo-core: tooling, trace chain, seal; hylo-reasoner-llm: native tool calls; hylo-code-agents: `tools.llm`, sessions, `hylo watch`, `hylo preflight`, `hylo mcp`), hylo-bench (hylo-env-libero perturbations) |
| Builds on | RFC-0005 (one episode loop, store), RFC-0006 (robot contract, manipulation toolkit, code agents) |

## Motivation

RFC-0006 gave models a robot to program: `code.llm` writes Python blocks against the toolkit. Three things that
agent cannot do well are needed for running models on robots and comparing them:

1. **Step-by-step control with checked actions.** A program block can move the robot many times before anyone
   looks at the result. A model that decides one action at a time, sees a measured receipt and fresh images after
   each one, and is refused when an action is unsafe or impossible, is easier to follow, to steer and to compare.
2. **Native tool calls.** Most served models are trained to call tools with JSON arguments; asking them for code
   blocks wastes that training and makes small models fail on syntax.
3. **Evidence that holds up.** Runs that are reported must be verifiable afterwards: which prompt and tools the
   model had, what it was shown, and that nothing in the trace was changed.

Robustness also needs measuring: a model that solves a LIBERO task may rely on where the objects start, on the
exact words, or on the camera angle.

## Design rules

- **Tools are declared once.** A tool is a closed JSON schema, a structured description and a kind (read, act,
  end). The same declaration serves native tool calls, a text protocol for models without them, MCP and the docs.
- **Acting is separate from looking.** Read calls batch; an act call must be alone in its reply, is recorded as a
  proposal bound to the observation step, executes through the kernel and the SafetyShield, and is answered by a
  measured receipt. A refusal that moved nothing costs no decision.
- **Nothing is dropped from the record.** The conversation is append-only; what the model is sent is a projection.
  Everything left out of the projection stays readable, by the model (`read_artifact`) and in the trace.
- **The task decides success.** `finish` states the agent's view; the verdict is the task's own check, never
  shown to the model.

## Part 1: native tool calls (implemented)

hylo-reasoner-llm's chat backends take `tools=[ToolSpec]` and return `ChatReply.tool_calls` (id, name, arguments,
or the raw text with an error when the arguments are not a JSON object). The conversation has one neutral shape
(assistant messages with `tool_calls`, `role: tool` results with images); OpenAI-compatible endpoints (Ollama,
vLLM, DeepSeek; optional reasoning replay) and the Anthropic API translate it at the wire. `TextTools` wraps models
without native tool calls (the coding-agent CLIs): the tools are listed in the system message and fenced `tool`
blocks are parsed from the reply.

## Part 2: typed tool surfaces (implemented)

`hylo.core.tooling` (`hylo.tools/v0.1`): `ToolDef(name, kind, help, params, fn)`, a `Surface` that checks
arguments against the closed schema (types, bounds, enums, required and unknown keys; null means "not given"),
returns `ToolReply` with structured `ToolError`s (code, message, field, whether a retry can help), and hashes its
declarations (`digest`). New registry group `hylo.surfaces` for surfaces other packages provide.

The robot surface (`hylo.codeagents.robot_surface`) wraps the RFC-0006 toolkit:

| Tool | Kind | What it does |
|---|---|---|
| `robot_state` | read | TCP pose, joints, hand opening, holding, per arm |
| `look` | read | camera images with positions, viewing directions and intrinsics |
| `locate` | read | objects described in words, measured in 3D; target handles and an outlined image |
| `pixel_to_world` | read | pixels to world points from depth; named marks cross-checked between cameras |
| `world_to_pixel` | read | world points to pixels with occlusion evidence |
| `calc` | read | exact arithmetic with numpy and rotation helpers, no loops or imports |
| `grasp_options` | read | grasp poses for a target that fit the open hand, with IK reachability |
| `reach_check` | read | IK feasibility of a pose |
| `read_artifact` | read | an earlier result or image the context stored |
| `report_issue` | read | an interface defect, kept with the run |
| `move_tcp` | act | a pose by position, delta, orientation or rotation; free (collision-free path) or straight route |
| `grasp` | act | a grasp option: pre-pose, approach, close, lift; receipt with holding before and after the lift |
| `place` | act | the held object at a point or on another target, release, retreat |
| `gripper`, `recover`, `wait` | act | hand only; back to the previous or home posture; let time pass |
| `finish` | end | success (with evidence), give_up (with a category) or abort |

Handles (`t1`, `g3`) are bound to the observation step they were measured at; using them after the robot moved is
refused as stale. Receipts give status (refused, arrived, stopped_short, episode_ended), steps, per-stage TCP
errors and holding.

## Part 3: context projection (implemented)

`hylo.codeagents.tool_context.ToolContext` keeps the conversation append-only and projects it before every call:
the system and task messages verbatim; the last actions' turns verbatim (images only for the latest); older long
results stored as references with a preview; under token pressure, everything before the tail replaced by a
summary the model writes in a separate call (seven fields: progress, confirmed, ruled out, failed attempts,
constraints, what to avoid, what to re-measure; no coordinates). Calls and their results always travel together.

## Part 4: the agent `tools.llm` (implemented)

`hylo.codeagents.tool_agent.ToolLLMAgent` (`agent: {type: tools.llm}`): a prompt in named layers (protocol,
evidence rules, boundary, an embodiment card generated from the RobotSpec; each digested), the opening observation,
then model calls with every tool. Budgets: decisions, model calls, calls without an action, tokens, cost, wall
time. Replies without a tool call get a reminder and end the episode after a few. An inbox file
(`params.inbox`) lets a person send guidance mid-run; any message marks the run `human_assisted`. Events:
`agent.tool.start | turn | result | proposal | receipt | operator | finish | summary`.

## Part 5: run evidence (implemented)

- **Hash chain.** Every trace line now carries `prev` and `h` (sha256 of its canonical JSON without `h`); blobs
  are content-addressed. Old traces read unchanged (unchained).
- **`hylo seal RUN`** checks every episode's chain, scans the events that hold what a model saw for privileged
  keys, writes `seal.json` (every file with size and sha256, chain heads, the inventory's digest) and makes the
  files read-only. `--verify` reports changed, added and removed files; `--chain` checks chains only.
- **`hylo preflight CONFIG`**: config and plugins, source state, free storage, a live probe of the model (text, an
  image, a tool call with the right arguments, an answer that uses a tool result) and a first reset of the
  environment; `--out` writes `preflight.json` into the run directory.

## Part 6: watching and steering (implemented)

`hylo watch RUN` follows a running episode or replays a finished one (`--replay --speed 4`), one line per model
turn, tool call (with a condensed result), receipt, operator message and verdict. `hylo watch --say "..." --inbox
FILE` steers a running agent.

## Part 7: perturbed LIBERO (implemented)

`hylo.envs.libero.perturb`: seven kinds of change to the official scenes, declared on the task
(`benchmark params: perturb`), so one environment serves all variants and each has its own task id:

| Kind | Change |
|---|---|
| `position` | the goal's object trades start positions with another movable object |
| `task` | a different goal in the same scene: another movable object goes where the original goal put its object; the BDDL goal and the instruction are rewritten (27 of the 40 tasks of four suites have one) |
| `language` | a paraphrase of the instruction (three per instruction, written by a local model and checked to keep every object and place word) |
| `object` | movable objects recoloured |
| `camera` | the main camera moved about its view axis (yaw, pitch, distance) |
| `noise` | pixel noise and a glare spot on every image |
| `robot_init` | the arm starts from a seeded offset of its joints |

What was changed is reported in every observation (`extra["perturbation"]`).

## Part 8: MCP (implemented)

`hylo mcp --surface NAME` serves any registered surface over the Model Context Protocol (stdio), so a coding agent
can use the same tools; read-only tools are marked as such.

## Part 9: conversations as training records (implemented)

`hylo chats RUN... --out chats.jsonl` writes each successful episode's (or session's) conversation in the common
chat-completions shape (system, user, assistant with tool calls, tool results; images replaced by a note), with the
task, seed, model, surface and prompt digests. Episodes a person steered are left out unless asked for.

## Not included

- **Resource leases and admission** across machines: one workstation runs everything; the store's file locks and
  the job runner are enough here.
- **A SAPIEN-based dual-arm suite:** it needs Vulkan rendering and expert-accepted seeds produced by a CUDA motion
  planner. The two-arm task families stay on the MuJoCo ALOHA table (RFC-0006 part 3), which `tools.llm` drives
  through the same surface (`arm` on every arm tool).
- **Suites built on Isaac Sim** (an NVIDIA RTX GPU), and learned grasp proposal and GPU motion planning whose
  operators are CUDA-only: the analytic grasps and the CPU planner of RFC-0006 serve instead.
- **Reading the task's success during an episode:** deliberately absent; `finish` states the agent's view only.

## Checks

Unit and integration tests per part: wire translation for both API styles and the text protocol; schema checks and
error reporting; the projection (stored results, images, compaction that keeps pairs); `tools.llm` end to end on
hylo-manip's test kit (a scripted model: locate, grasp options, the act-alone rule, a refused unreachable move not
counted, a stale handle refused, operator guidance, place, finish); chain and seal tampering; perturbation text
rewriting and seeded choices; MCP over stdio; preflight with a scripted model. Live: `qwen3.5:35b-a3b` passes the
preflight probe and, through `tools.llm` zero-shot, solves 8 of 9 episodes of pick_place, put_in_bowl and stack on
`mujoco/manip-v0` (push_to_zone: 0 of 1; the other tasks and perturbed LIBERO are not evaluated yet; details on the
showcase).
