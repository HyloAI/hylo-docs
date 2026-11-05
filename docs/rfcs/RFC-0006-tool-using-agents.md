# RFC-0006: Tool-using agents, program candidates and the manipulation toolkit

| | |
|---|---|
| Status | Core workflows implemented with recorded runs (2026-11-01/02); Panda, LIBERO, ALOHA and fixed-base G1 measured. Free-scene/motion-free showcases and robosuite/RoboCasa formal program evaluations remain pending; see the showcase for per-workflow limits. |
| Scope | hylo-harness (hylo-core, new hylo-manip, hylo-agents, hylo-evolve, hylo-memory, hylo-reasoner-llm, new tool adapters), hylo-bench (manipulation environments), hylo-studio |
| Builds on | RFC-0001 (contracts, kernel), RFC-0002 (splits, gate), RFC-0003 (skills), RFC-0005 (one episode loop, store) |
| Results | Recorded runs, numbers and videos of the finished workflows: [Showcase > Tool-using agents](../developer-guide/validation/tool-agents.md) |

## Motivation

Turning a task requirement into an executable robot strategy requires task programming, perception/planning/control
integration and repeated validation. New tasks, changed scenes, efficiency goals and observed failures can all
motivate this work. Reusable robot tools and model-written programs reduce that development effort within Hylo's
wider execution, evaluation, improvement and deployment stack. They are one strategy-development path alongside
existing model policies and learned controllers.

Every agent in Hylo today runs a learned or hand-written controller and changes it through declarative patches. Three
results say this is not enough:

1. **Hand-written levers rarely change outcomes** (roadmap, "what the experiments say"): rule triggers changed 0 to 3
   of 100 LIBERO episodes; the one consistent lever was the replanning interval.
2. **The candidate space is narrow.** `CandidateKind` already names `code` and `prompt`, but no generator produces
   them and nothing could run them safely (technology gap analysis 1.6: "sandbox for self-generated content", BUILD).
3. **There is no contact task** in our MuJoCo set (roadmap v0.1: planar and table reach only), so manipulation skills
   cannot be measured without LIBERO.

A capable language model that writes short programs against a small set of robot tools (see, segment, fit a box,
choose a grasp, plan, move, check) can solve tabletop tasks without task-specific training. Written down as a
program, such a solution is also a candidate like any other: it can be gated on unseen init states, confirmed on
held-out, stored as a skill and rolled back. Hylo is the right place for this because the kernel, the SafetyShield,
the trace and the gate already exist: a program that moves the robot goes through the same checks as a VLA.

## Design rules

- **The kernel stays in charge.** A tool call that moves the robot becomes an `ActionChunk` of joint targets that the
  kernel executes step by step through the SafetyShield. Model calls and tool calls are trace events.
- **Same tools on every robot.** Tools know a robot only through `RobotSpec` (part 1) and the observation layout.
- **Privileged information is explicit.** Segmentation from the simulator is an observation the config turns on, so
  it is part of the digest and a privileged run is never ranked with an unprivileged one.
- **Programs are data until gated.** A generated program is validated (allowed names, no imports beyond `math` and
  `numpy`), runs in a restricted namespace with only the tools, and is promoted only through the gate.
- **Workflows stay small and task-agnostic.** No task names in shared code; a failure without a general fix is
  recorded, not tuned. Each workflow stays under 1,000 lines.

## Part 1: robot contract and agent-ended episodes (implemented 2026-11-01)

- `hylo.core.robot` (`hylo.robot/v0.1`): `RobotSpec` (arms, hands, cameras, notes for agents), `ArmSpec` (model
  file, joints, ee frame, base pose, limits, home, action slices), `HandSpec` (parallel or dexterous, TCP in the ee
  frame, open / closed commands, presets), `CameraSpec`. A common TCP convention (+x approach, +y closing axis).
- `EnvSpec.robot` carries it, so remote environments forward it without new protocol messages.
- Observation layout for manipulation environments: `q.<arm>`, `hand.<arm>` (measured), `<cam>`, `<cam>.depth`,
  optional `<cam>.seg`, and camera intrinsics and poses in `extra["cameras"]`.
- `END_EPISODE` (`hylo.core.agent`): an agent marks its last chunk with `provenance["end_episode"]`; the kernel ends
  the episode before executing it, with reason `agent_done`, and the last step's task predicate decides success.

## Part 2: the manipulation toolkit, hylo-manip (implemented 2026-11-01)

A new harness package `hylo-manip` (`hylo.manip`, depends on hylo-core, numpy, scipy, mujoco). Stateless tools over
one robot; the agent keeps its own object list. The facade is `Tools`, exposed to programs as `robot`:

| Verb | Returns | What it does |
|---|---|---|
| `robot.status()` | dict | step, step budget, instruction, ended, joint positions, measured hand state, TCP poses per arm |
| `robot.look()` | `View` | the latest observation as per-camera RGB, depth, intrinsics and pose; fused world points |
| `robot.find(view, labels)` | `list[Mask]` | instance masks for text labels, from the configured segmenter (env segmentation, colour, VLM marks) |
| `robot.table(view)` | `Table` | the support plane height and extent, from depth (RANSAC) |
| `robot.objects(view, masks, table)` | `list[Detection]` | per mask: label, score, world points fused across cameras, outliers and table points removed |
| `robot.box(points, table)` | `Box` | oriented box: centre, size, yaw, bottom height |
| `robot.fit(model_points, observed)` | `Fit` | rigid registration (ICP) of a known shape to observed points |
| `robot.grasps(points, table, scene=None, arm=None)` | `list[Goal]` | ranked grasp goals for a parallel hand from the points (top-down and side, antipodal checks) |
| `robot.hand_grasps(points, table, kind="power", arm=None)` | `list[Goal]` | dexterous hand: top-down multi-finger grasps across the object's faces, opening to `HandSpec.open` and closing to a preset (`power`, `pinch`, ...) |
| `robot.grasp_at(tcp, hand=None, arm=None)` | `Goal` | a grasp goal for a TCP pose chosen by the program |
| `robot.hand_points(hand=None, arm=None)` | array | the hand's surface in the TCP frame at a command or preset (how far a closed hand reaches past the TCP) |
| `robot.place_at(obj_in_tcp, obj_points_or_box, xy, yaw=None, table=None, hover=0.03, scene=None, support=None, arm=None)` | `Goal` | where the TCP must go so a held object rests at `xy`, on the table or on what `scene` shows under it (a plate, a block to stack on); the object rides along as attached geometry |
| `robot.Goal(verb, arm=None, tcp=None, pre=None, hand_before=None, hand=None, rank=0, free=None, attached=None)` | `Goal` | any other motion: reach, lift, push, press, retreat; `attached`: held object points in the TCP frame |
| `robot.plan(goals, table=None, scene=None)` | `Plan` or None | the first reachable goal: IK, collision-free joint path (RRT-Connect, shortcut), straight final approach, timed to control steps |
| `robot.run(plan)` | dict | executes it (through the kernel and the shield): steps, ended, final joints, hand, TCP, TCP error; `run({arm: plan, ...}, sync=False)` moves several arms at once |
| `robot.together(plans, sync=False)` | `Plan` or None | one plan for several arms from the same moment; `sync` re-times them to start and stop together with their TCPs in step (both hands on one object); every step is checked for arms touching each other or the robot |
| `robot.holding(arm=None)` | bool | parallel hand: pads stopped between open and closed; dexterous: fingers stopped short of a closing command |
| `robot.carried(view, points, tcp_before, tcp_now, table)` | dict | did the object move with the hand (lifted, offset) |
| `robot.show(view_or_image, note="")` | None | attach an image to the agent's next turn (and to the trace) |

Kinematics load `ArmSpec.model` with MuJoCo (MJCF directly, URDF through MuJoCo's importer); collision uses the
model's collision geoms against the table plane and observed points (KD-tree). `run` is the only verb that moves the
robot; it is implemented by an executor the agent provides (part 4), so the toolkit itself never touches an
environment. The toolkit has its own tests on the Panda model and a stub executor. Arm-specific verbs take `arm=`,
defaulting to the robot's only arm (the older form with the arm name first still works). `plan` moves one arm while
the others hold still and count as obstacles (arms of one model through MuJoCo contacts, arms of different models as
surface points).

Robot points are removed from observations with every geom of the robot model (visual ones and the fixed base
included: that is what cameras see); collision checks use the collision geoms. Reference programs, one `solve(robot)`
per `mujoco/manip-v0` task using cameras and the environment's segmentation only, live in
`hylo-code-agents/examples/programs` with a runner that evaluates them through `hylo run`.

## Part 3: manipulation environments in hylo-bench (implemented 2026-11-02)

`mujoco.panda_table` in hylo-env-mujoco: a Franka Panda with its parallel hand (MuJoCo Menagerie model, Apache-2.0,
fetched at a pinned commit into the asset cache on first use, never vendored), a table, RGB-D cameras (front, side,
wrist), joint-position control at 20 Hz, optional segmentation. A seeded task family, benchmark `mujoco/manip-v0`
with the RFC-0002 splits:

| Task | Success predicate |
|---|---|
| `pick_place` | a named object rests on a named target |
| `stack` | two or three blocks stacked in a named order |
| `put_in_bowl` | a named object inside a bowl |
| `push_to_zone` | an object pushed into a marked zone (too wide to grasp) |
| `press_by_number` | buttons pressed in the order the instruction gives |
| `sort_by_colour` | objects of each colour in that colour's tray |

Two-arm and humanoid tables (implemented 2026-11-02, hylo-env-mujoco, shared base `arm_table.py`): two ViperX 300
arms from the Menagerie ALOHA model (`mujoco.aloha_table`: cameras overhead, front and on both wrists) and the Unitree
G1 with three-finger hands from the Menagerie (`mujoco.g1_table`: pelvis fixed, legs and waist rigid, each arm and
hand one ArmSpec with a dexterous HandSpec; cameras head and front). Both fetch their models at the pinned commit and
verify them against per-file digests. Benchmarks with the RFC-0002 splits, measured on the validation split (20
episodes per task; oracle: privileged scripted agent; program: a perception-only `solve(robot)`):

| Benchmark | Task | Success predicate | Oracle | Program |
|---|---|---|---|---|
| `mujoco/bimanual-v0` | `handover` | a bar from where only one arm reaches into a zone only the other reaches | 1.00 | 1.00 |
| `mujoco/bimanual-v0` | `lift_box` | a box wider than a gripper lifted by its two end handles, level, for one second | 1.00 | 1.00 |
| `mujoco/bimanual-v0` | `two_bins` | one block per arm into its bin within a step limit that one arm after the other misses | 1.00 | 1.00 |
| `mujoco/humanoid-v0` | `pick_place` | a block on a plate with one hand (claw grasp from above) | 1.00 | 0.80 |
| `mujoco/humanoid-v0` | `two_hands` | a block per hand onto its plate within a step limit that one hand after the other misses | 0.90 | 0.50 |
| `mujoco/humanoid-v0` | `press_button` | the button of the named colour pushed down with the closed hand | 0.90 | 1.00 |

A two-handed box lift for the G1 was tried and left out: the three-finger claw could not hold a handle firmly enough
for the box to stay level. The G1's index finger presses buttons poorly too (the arm reaches the fingers-down posture
over too little of the table), so the button is pushed with the closed hand.

The LIBERO adapter now exposes the robot contract (depth, camera poses, joint-position control); robosuite and
RoboCasa adapters are implemented with interface checks, with formal task-program evaluations pending. The task
families that today's suites only offer on Isaac Sim (bimanual manipulation,
humanoids, mobile manipulation) are rebuilt on engines that run on a CPU: MuJoCo first (Menagerie humanoid and
bimanual models), and Newton, the Warp-based physics engine of Isaac Lab 3, as an optional second backend (checked on
this workstation's CPU 2026-11-01). Isaac Sim itself requires an NVIDIA RTX GPU and is not a dependency.

## Part 4: the code-writing agent, `code.llm` (implemented 2026-11-01)

An agent (hylo-agents) whose policy is a language model writing one Python block per turn against `robot`:

- A persistent namespace per episode (`robot`, `np`, `math`, the model's own variables); each block is validated
  (AST allow-list) and run with a time limit; printed output, errors, robot status and images passed to `show` go
  back to the model.
- `robot.run(plan)` hands the planned joint trajectory to the kernel as one chunk and blocks the program until the
  kernel has executed it; `finish()` ends the episode (`END_EPISODE`). The program runs in a worker thread; the kernel
  thread waits while the model thinks (simulation time does not pass; on a robot the runner holds).
- Every turn is a trace event `agent.code.turn` (prompt digest, reply, code, output, error, images, tokens, cost).
- Budgets: turns, model tokens and cost, robot steps. The task's native score is never shown to the model.
- Models through hylo-reasoner-llm backends (part 7). Demonstrations: zero or one prior solution in the prompt.

## Part 5: research sessions and program candidates (implemented 2026-11-01)

A research session (`hylo research`, and generator `research.llm` in hylo-evolve):

- The model works on **development cases** (episodes of the `search` split) with resets: `reset(case)` ends the live
  episode and returns its outcome (success, steps, reason); its variables survive.
- `submit(source)` takes a program defining `solve(robot)`; it is validated, then run without the model on a fresh
  episode of every development case; the model gets each case's outcome and printed output.
- `finish()` freezes the submission with the most development successes. It becomes a `Candidate(kind="code")`
  whose patch sets `agent.type: code.program` and `agent.params.source` (stored as a sealed artifact).
- The frozen program then goes through the ordinary cascade: `search_val`, the gate on unseen init states with the
  paired test, held-out report, approval, promotion, rollback. The model never sees gate or held-out outcomes.
- `code.program` runs a frozen `solve(robot)` with the same toolkit and no model, so promoted programs cost nothing to
  run and are reproducible.

## Part 6: program skills (implemented 2026-11-02)

A promoted program becomes a skill in the skill library (RFC-0003) with its task family, preconditions as text, the
gate evidence and the artifact digest. The `code.llm` agent retrieves skills by instruction similarity and gets them
as tools (`skills.<name>(robot, **args)`); research sessions can build on them. A skill whose re-validation fails is
demoted, like any promoted version.

## Part 7: model backends and costs (implemented 2026-11-01)

hylo-reasoner-llm gains one interface for chat models with images and cost accounting: OpenAI-compatible endpoints
(Ollama, vLLM, DeepSeek), the Anthropic API, and coding-agent CLIs (Claude Code, Codex) run as subprocesses. Each
call records model, tokens, latency and cost in the trace; runs report cost per success. A local model through
Ollama is priced at $0; research summaries and the Studio research page show tokens, latency and cost per turn.

## Part 8: further workflows and tools (implemented 2026-11-02)

The original six workflows below have implementations and recorded examples, including fallbacks and unsuccessful
results. Later free-scene and motion-free showcase extensions remain unrun. Measured results and remaining failures are on
[Showcase > Tool-using agents](../developer-guide/validation/tool-agents.md).

- **Scene builder**: a model writes a MuJoCo scene from a natural-language task (objects, poses, success predicate),
  a checker validates it (loads, settles, reachable, predicate false at start), then `code.llm` solves it with
  privileged state.
- **Replay to sim**: from a recorded RGB-D episode (ours, or an external demonstration), track objects and the hand,
  build collision meshes (convex decomposition), place them in a MuJoCo scene and replay the motion; checks report
  object pose error and contact events.
- **Motion studio**: text or video to a humanoid or robot motion (motion models as tool adapters), retargeted and
  rendered.
- **Tool adapters** (`hylo-tool-*`): open-vocabulary segmentation, image-to-mesh, monocular depth, gravity
  estimation, hand and human motion from video, text-to-motion, convex decomposition, offline rendering. Each runs in
  its own environment and is verified on this workstation's CPU (torch CPU build: about 2.4 TFLOPS on 64 threads);
  a GPU only makes them faster. Models with gated weights need an access token; open alternatives are wired behind
  the same interface. Only suites built on Isaac Sim, which requires an NVIDIA RTX GPU, stay `needs-hardware`.
- **Coding-agent skills**: instruction files that let a coding agent drive `hylo run`, `hylo research` and
  `hylo evolve` from a terminal session (`harness/agent-skills/`, one `SKILL.md` per command family, also covering
  `hylo tool`, `hylo scene`, `hylo replay` and `hylo motion`).
- **Studio**: a research page (turns with code, output and images, submissions, development outcomes, cost).

## Checks

Each part lands with tests and a recorded run on this workstation (CPU): the toolkit on the Panda model, every
`mujoco/manip-v0` task solved by at least one program, `code.llm` and a research session with a local model, a
program candidate through the gate with held-out confirmation, and every tool adapter run on the CPU on a recorded
example.
