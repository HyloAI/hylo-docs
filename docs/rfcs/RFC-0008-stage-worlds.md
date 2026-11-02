# RFC-0008: Stages, worlds and robot packs for model-driven robotics

| | |
|---|---|
| Status | Parts 1-11 implemented (2026-11-02); recorded runs on the [showcase](../showcase/tool-agents.md#worlds) |
| Scope | hylo-core (stage contract and store), hylo-bench (hylo-env-mujoco: packs, composition, world, controllers, checks, crowds, policies, the `mujoco.world` surface), hylo-harness (hylo-code-agents: `hylo world`, role campaigns; hylo-tools: physicalize; hylo-memory: failure-signature skills), hylo-studio (world page) |
| Builds on | RFC-0003 (skills), RFC-0006 (scene contract, manipulation environments), RFC-0007 (tool surfaces, sessions, MCP) |

## Motivation

Everything a model could do with a robot in Hylo so far happened inside a benchmark task: a fixed table, one robot,
an episode. Building a new situation (a robot of another kind, two robots, people walking past, a camera where the
data is needed) meant writing an environment. A workspace where a person or a model describes a scene, edits it in
small checked steps, runs any of a few dozen robots in it and records what happens closes that gap. It is also
where task programs and skills get developed before they become benchmark tasks.

## Design rules

- **The scene is data with history.** Every change is a patch against a revision; nothing is lost; any revision
  can be restored.
- **Actions are bound to what was seen.** A world has a generation; an action decided on an older one is refused.
  An action id makes retries idempotent. Receipts report what the simulation measured.
- **Robots come from pinned sources.** A pack points at a model folder at a commit, verified by digest, fetched on
  first use, never vendored.
- **Weights are read, never executed.** Pretrained policies are inspected from their bytes and run with numpy.
- **Same tools for everyone.** The world is a tool surface (RFC-0007): a chat session, the Studio, a coding agent
  over MCP and a role campaign all use the same calls.

## Part 1: stages (implemented)

`hylo.core.stage` (`hylo.stage/v0.1`): an entity tree (id, parent, pose, lock; components shape, mesh, body,
collision, robot with pack, base and mount, camera, light, human) and patches (add, remove with cascade, update,
reparent) against an expected revision. `StageStore` keeps `current.json`, every revision and a log, under a file
lock; `restore(n)` commits revision n again. Validation: unique ids, existing parents and mount targets, no parent
or mount cycles, unit quaternions, one geometry kind per entity. `hylo stage list | new | show | patch | history |
restore`.

## Part 2: composition (implemented)

`hylo.envs.mujoco.compose`: a stage as one MuJoCo model built with MjSpec: shapes and meshes (free joint when
dynamic), robots attached under a frame with the prefix `<id>/` (fixed base: the free joint removed; mounted on
another entity's body), cameras on bodies, lights, people as mocap bodies. Physics options a robot model needs
(elliptic cones, impratio, integrator) carry over; keyframes are applied by name after compiling, so robots of
different models never share one; a checker floor and a sky make scale readable in every image.

## Part 3: the world (implemented)

`hylo.envs.mujoco.world.World`: generation, reset, `act` / `act_batch` (several robots start in the same step),
`advance` (time passes; drones hover, people walk), `state`, `capture` (RGB-D, segmentation by entity, intrinsics,
OpenCV camera pose, all from one step), `view` (a free viewpoint), `overlaps` (penetrations at the start). Time
passes only inside actions. Controllers:

| Action | Robots | How |
|---|---|---|
| `joints` | all | interpolation of joint targets; torque motors get a PD loop with the pack's gains |
| `gripper` | packs with a gripper | open / close / fraction; measured opening from the servo's equilibrium, `holding` when the fingers stop short |
| `tcp` | arms, mobile manipulators | damped least squares IK of the arm joints; keeps the current orientation unless one is given |
| `walk` | quadrupeds | open-loop trot: diagonal pairs in antiphase, stride from the forward command, heading held when walking straight |
| `fly` | drones | position PD, attitude PD with gains scaled to the drone's measured moment authority, allocation measured from the model |
| `base` | mobile bases | x, y, yaw joints |
| `policy` | humanoids | a pretrained walking policy (part 8) |
| `hold` | all | keep targets (drones: hover where they are) |

## Part 4: checks (implemented)

`hylo.envs.mujoco.checks`: goals as predicates (in_box, near, apart, above, contact, no_contact, joint_range,
settled, upright, lifted, reachable, no_penetration; all, any, not). A failed atom returns expected, measured and a
reason code (POSE_OUTSIDE_BOX, DISTANCE_NOT_MET, NOT_LIFTED, CONTACT_MISSING, ...); atoms that cannot be evaluated
are unverifiable and stay so under `not`. The gate refuses goals naming missing entities and flags goals already
satisfied at the start.

## Part 5: the world surface (implemented)

`mujoco.world` (group `hylo.surfaces`): stage_show, stage_history, stage_edit, stage_restore, packs, policies,
world_build, world_reset, world_state, act, advance, people, capture, view, pixel_to_world, lidar, camera_fit,
check, gate, overlaps, export. `lidar` casts a grid of rays over a camera's field of view (or a horizontal ring)
and counts hits per entity; `camera_fit` estimates a camera pose from six or more world points and their pixels
(linear estimate, then Gauss-Newton on the reprojection error). `world_build` lists which entities are fixed in
place and which can move. `export` records camera frames while actions run or time passes: `samples.jsonl` (step, time, camera pose,
world state per frame), RGB png, depth npy in metres, segmentation png, `calibration.json`. `act` and `advance` can
record a video.

## Part 6: people (implemented)

`hylo.envs.mujoco.crowd`: kinematic walkers on routes (loop, dwell, speed), paths planned by A* on a floor grid
around every other body's footprint (no corner cutting, shortened by line of sight), replanned after being blocked;
rays at knee and chest height stop them for anything in front. `people` tool: goto, stop, resume.

## Part 7: robot packs (implemented)

`hylo.envs.mujoco.packs` (`hylo.pack/v0.1`), 24 packs: arms (Panda, UR5e, UR10e, iiwa 14, xArm 7, SO-101,
ViperX 300s, ALOHA), a gripper (Robotiq 2F-85, mountable on an arm), hands (LEAP, Allegro, Shadow), quadrupeds
(Go2, Go1, A1, Spot), humanoids (G1 and H1 from MuJoCo Menagerie; G1 and H1 leg models a walking policy was trained
on), drones (Crazyflie 2, Skydio X2) and a mobile manipulator (TidyBot). Each names its asset manifest (folder,
commit, licence, a digest per file), model file, base, home keyframe, drive, gripper, tool point, legs, controls and
status. The asset cache fetches from MuJoCo Menagerie and, with `repo` in the manifest, from other repositories.

## Part 8: pretrained policies (implemented)

`hylo.envs.mujoco.policies`: `sniff` tells the format of a weights file from its bytes (ONNX, safetensors,
TorchScript, checkpoint); `read_torchscript` reads a TorchScript archive's tensors with an unpickler that only knows
tensor rebuilding and stand-ins for module objects (anything else is refused); `NumpyPolicy` runs an LSTM memory
plus an ELU MLP. A `LocoPolicy` declares joints, default angles, PD gains, observation scales, gait phase and control
period; `match` lists every difference with the robot in the world, and the world refuses a policy action while the
list is not empty. Two walking policies (G1 12 leg joints, H1 10) run on the CPU.

## Part 9: role campaigns and failure-signature skills (implemented)

`hylo roles run CAMPAIGN.yaml`: dev and held-out tasks (a stage, a request, a goal). The coordinator takes dev tasks
by goal size; a worker session works on a fresh copy of the task's stage; every tool call goes to a ledger and
counts against the budget; a dev success becomes a recipe skill (its acting calls) keyed by the failure reasons the
task started with; a verifier replays the recipe without a model on fresh copies and promotes it only when the goal
then holds; held-out tasks run last and are never used to propose or verify. `SkillTrigger.reason_codes` and
`SkillLibrary.for_failure` (hylo-memory) match skills to the reasons a check reported.

## Part 10: physicalize (implemented)

`hylo tool physicalize MESH`: collision geometry for a visual mesh in the file format a stage's `collision.parts`
reads: one box when the mesh fills its oriented box, the convex hull when nearly convex, convex parts (CoACD) when
concave, voxel boxes (filled voxels merged greedily into boxes) when a closed mesh would need too many parts; mass
from volume and density.

## Part 11: sessions and the Studio (implemented)

`hylo world chat "REQUEST"` runs a model on the world surface (RFC-0007 sessions: projected context, reads before
acts, an after-action view for vision models, a hash-chained trace for `hylo watch`, an inbox).
`hylo mcp --surface mujoco.world` serves the same tools to coding agents. The Studio's World page shows the stages,
builds a stage's world, orbits a free view, runs actions and checks by hand, and runs chat sessions (follow-up
messages go to the running session's inbox) with their transcript and after-action views.

## Not included

Isaac Sim (needs an NVIDIA RTX GPU), paid generation services, a desktop application and accounts. Newton remains
the optional second engine of RFC-0006 part 3; the world contract does not depend on MuJoCo-specific types beyond
the surface implementation.

## Checks

hylo-core tests (stage validation, patches, conflicts, locks, restore, CLI); world tests on Menagerie models (a cube
picked up through receipts and checks; stale, idempotent and refused actions; four quadrupeds trot forward and back;
two drones reach points and hover; a mobile base and a gripper mounted on an arm; a batch; people around an
obstacle; the grid planner; both walking policies forward and standing; a policy refused on the wrong robot; the
restricted reader refusing foreign objects; the surface end to end with video and dataset export); role campaign
with a scripted worker (proposal, verified replay, held-out); physicalize box merging and the worker; MCP and
sessions with a toy surface.
