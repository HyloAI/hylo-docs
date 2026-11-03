# Worlds

A world is a place to try robots outside a benchmark: put a quadruped next to a table, mount a gripper on an arm,
let people walk past, and record what the cameras see. You describe the scene as a stage, build it into a MuJoCo
simulation, run robots in it with actions, and check goals. A chat model can do all of this through the same tools,
and so can a coding agent over MCP.

![A world built from a stage: a Panda at a table with a cube and a plate, a UR5e with a mounted Robotiq gripper, a TidyBot](../assets/figures/world-view.jpg)

*A world seen from a free viewpoint (the `view` tool): a Panda at a table with a cube and a plate, a UR5e with a
Robotiq gripper mounted on its wrist, and a TidyBot mobile manipulator, all from one stage.*

## Why worlds

Until worlds, everything a model could do with a robot in Hylo happened inside a benchmark task: a fixed table, one
robot, one episode. Trying a robot of another kind, two robots side by side, people walking past, or a camera where
the data is needed meant writing a new environment. Worlds close that gap. A person or a model describes a scene,
changes it in small checked steps, runs any of two dozen robots in it and records what happens. It is also where task
programs and skills are developed before they become benchmark tasks.

## From language to a world

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
defined outside the session, as in [role campaigns](#tasks-with-roles), and why results are read from receipts and
checks rather than from the model's summary.

## Principles

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

## Stages

A stage is a list of entities, each with a pose and one kind of content:

| Content | Fields |
|---|---|
| `shape` | `box`, `sphere`, `cylinder`, `capsule` or `plane`, size (half extents for boxes), colour |
| `mesh` | an obj or stl file and a scale; collision geometry from `collision` |
| `body` | for shapes and meshes: `dynamic: true` makes it movable, mass or density, friction |
| `robot` | a pack name, base `fixed` or `free`, `mount` onto another entity's body, start joints |
| `camera` | field of view and image size; it looks along its own −z axis (`look_at` builds a pose) |
| `light`, `human` | a light; a walking person with a route, speed and height |

??? example "Two entities of the stage in the picture above, as stored"

    ```json
    {"id": "panda", "parent": null, "pose": {"pos": [0.0, 0.0, 0.4], "quat": [1.0, 0.0, 0.0, 0.0]}, "locked": false,
     "robot": {"pack": "panda", "base": "fixed", "mount": null, "joints": {}}}
    {"id": "cube", "parent": null, "pose": {"pos": [0.5, -0.15, 0.42], "quat": [1.0, 0.0, 0.0, 0.0]}, "locked": false,
     "shape": {"type": "box", "size": [0.02, 0.02, 0.02], "rgba": [0.85, 0.15, 0.12, 1.0]},
     "body": {"dynamic": true, "mass": 0.05, "density": 500.0, "friction": 1.0}}
    ```

Every change is a patch against the revision you read (add, remove, update, reparent). A patch written against an
older revision is refused, so two editors cannot overwrite each other; a `locked` entity refuses changes. Every
revision is kept and any one can be restored.

??? info "Where a stage lives on disk"

    ```text
    runs/stages/lab/
      current.json        the newest revision (schema hylo.stage/v0.1)
      history/            every revision: rev-00000.json, rev-00001.json, ...
      log.jsonl           one line per revision: {"revision": 1, "digest": "027d6619eba572c8", "author": "model", "entities": 8, ...}
    ```

```bash
uv run hylo stage new lab                       # in runs/stages (or $HYLO_STAGES)
uv run hylo stage patch lab patch.json          # {"expected_revision": 0, "ops": [{"op": "add", "entity": {...}}]}
uv run hylo stage history lab
uv run hylo stage restore lab 3
```

A shape or mesh without `body: {dynamic: true}` is fixed in place. Free-base robots (quadrupeds, humanoids, drones)
take x, y and yaw from their pose and their height from the pack.

## Robot packs

| Family | Packs | Actions |
|---|---|---|
| Arms | `panda`, `ur5e`, `ur10e`, `iiwa14`, `xarm7`, `so101`, `vx300s`, `aloha` | joints, gripper, tool pose |
| Gripper and hands | `robotiq_2f85` (mount it on an arm), `leap`, `allegro`, `shadow` | gripper, joints |
| Quadrupeds | `go2`, `go1`, `a1`, `spot` | joints, walk |
| Humanoids | `g1`, `h1`, `t1`; `g1_legs`, `h1_legs` with walking policies | joints; policy |
| Drones | `crazyflie`, `x2` | fly |
| Mobile manipulator | `tidybot` | base, joints, gripper, tool pose |

<div class="grid" markdown>

<figure markdown>
<video src="../../assets/videos/world-quadrupeds.mp4" poster="../../assets/videos/world-quadrupeds.jpg" controls muted loop playsinline preload="none" width="100%" aria-label="Go2, Go1, A1 and Spot trotting side by side, then turning"></video>
<figcaption>Go2, Go1, A1 and Spot: 0.78 to 1.31 m forward in 4 s, then a turn, all in the same steps.</figcaption>
</figure>

<figure markdown>
<video src="../../assets/videos/world-humanoids.mp4" poster="../../assets/videos/world-humanoids.jpg" controls muted loop playsinline preload="none" width="100%" aria-label="Unitree G1 and H1 walking under pretrained policies, then turning"></video>
<figcaption>G1 and H1 leg models under pretrained walking policies: 2.2 and 2.0 m in 5 s, then a turn.</figcaption>
</figure>

<figure markdown>
<video src="../../assets/videos/world-drones.mp4" poster="../../assets/videos/world-drones.jpg" controls muted loop playsinline preload="none" width="100%" aria-label="A Crazyflie and a Skydio X2 flying three waypoints each"></video>
<figcaption>Crazyflie 2 and Skydio X2 flying three waypoints each.</figcaption>
</figure>

<figure markdown>
<video src="../../assets/videos/world-arms.mp4" poster="../../assets/videos/world-arms.jpg" controls muted loop playsinline preload="none" width="100%" aria-label="A Panda picks a cube onto a plate while a UR5e with a mounted gripper and a TidyBot base move"></video>
<figcaption>A Panda picks a cube onto a plate; a UR5e with a mounted Robotiq and a TidyBot base move in the same steps.</figcaption>
</figure>

</div>

Robot models come from MuJoCo Menagerie (and the two policy leg models from Unitree's training repository), fetched
at a pinned commit on first use and checked file by file against recorded digests; nothing is vendored. The `packs`
tool lists each pack's controls and status.

## Running a world

Build the newest revision with `world_build`; it reports the robots with their controls, the cameras, which
entities are fixed in place, and any parts that overlap at the start. Then act:

| Action | What it does | The receipt measures |
|---|---|---|
| `joints` | moves joints (or actuators) to targets over a duration | the largest joint error |
| `gripper` | open, close, or a fraction | opening, and `holding` when the fingers stop on something |
| `tcp` | moves an arm's tool point to a position (and orientation; by default it keeps the current one) | joint error at the end |
| `walk` | a quadruped trot, forward speed and turn in −1..1 | distance, turn, whether it stayed upright |
| `policy` | a pretrained walking policy with a velocity command | distance, speed, turn, upright |
| `fly` | a drone to a position and heading | distance from the target |
| `base` | a mobile base to x, y, yaw | joint error |
| `hold` | keeps still (drones hover) | — |

The receipts behind the quadruped video: one `walk` forward, then one with a turn, for all four robots in the same
steps.

| Robot | Forward | Turned | Upright | Base height |
|---|---|---|---|---|
| Go2 | 0.78 m, then 0.30 m | −0.6°, then 49.9° | yes | 0.252 m |
| Go1 | 1.27 m, then 0.37 m | −0.8°, then 79.2° | yes | 0.261 m |
| A1 | 1.22 m, then 0.43 m | −0.6°, then 75.0° | yes | 0.249 m |
| Spot | 1.31 m, then 0.50 m | −1.1°, then 36.9° | yes | 0.422 m |

Every action names the world generation it was decided on; after a rebuild or reset an old action is refused as
stale. Actions for different robots in one call run in the same simulation steps. Time passes only during actions
and `advance`. `act` and `advance` can record a video.

Pretrained policies are read from their files as tensors and run with numpy; nothing in a weights file is executed.
Before running one, the world compares what the policy expects (robot, joints, drive, timestep) with the robot and
refuses on any difference. `policies` lists them and reports such differences.

## Checking goals

`check` evaluates a goal on the world without stepping it. Atoms: `in_box`, `near`, `apart`, `above`, `contact`,
`no_contact`, `joint_range`, `settled`, `upright`, `lifted`, `reachable`, `no_penetration`; combined with `all`,
`any` and `not`.

```json
{"op": "all", "terms": [{"op": "lifted", "entity": "cube", "min_z": 0.5},
                        {"op": "near", "a": "cube", "b": "arm", "max_m": 0.05}]}
```

A failed atom returns what was expected, what was measured and a reason code (`NOT_LIFTED`, `DISTANCE_NOT_MET`,
`CONTACT_MISSING`, ...). From a chat session, where the cube had not been lifted high enough:

```json
{"ok": true, "satisfied": false,
 "failures": [{"atom": {"op": "above", "a": "cube", "b": "table", "min_m": 0.09}, "reason": "NOT_ABOVE",
               "expected": "height difference >= 0.09", "measured": 0.075}],
 "reasons": ["NOT_ABOVE"], "step": 6950, "generation": 2}
```

The `reasons` list is the failure signature that recipe skills are keyed by. `gate` checks a goal before work starts: it refuses goals naming missing entities and flags
goals that already hold.

## Cameras and data

- `capture`: images from camera entities, all from the same step, with depth and segmentation by entity kept for
  `pixel_to_world` (a pixel as a world point and the entity it shows).
- `view`: a picture from any viewpoint, without a camera entity.
- `lidar`: a grid of rays over a camera's field of view or a horizontal ring; hits per entity.
- `camera_fit`: a camera's pose from six or more world points and the pixels they appear at.
- `export`: frames over time while actions run: `samples.jsonl` (step, camera pose and world state per frame),
  RGB png, depth npy in metres, segmentation png, and a calibration file.

![Exported frames of a top camera while the Panda moves: RGB, depth and segmentation by entity](../assets/figures/world-dataset.jpg)

*Three exported frames of a top camera while the Panda moves: RGB, depth (nearer is brighter) and segmentation by
entity.*

For meshes, `hylo tool physicalize MESH` writes collision geometry the stage can use: one box, the convex hull,
convex parts or voxel boxes, chosen from the mesh's shape, with its mass from volume and density.

## People

A `human` entity walks its route (looping or not, with a pause at each waypoint), plans around the footprints of
everything else, and stops for anything in front of it. The `people` tool sends a person somewhere, stops them or
lets them walk on.

<video src="../../assets/videos/world-crowd.mp4" poster="../../assets/videos/world-crowd.jpg" controls muted loop playsinline preload="none" width="100%" aria-label="Four people walking routes around two crates while a Go1 trots across"></video>

*Four people on routes around two crates while a Go1 trots across: they plan around the crates and the dog and touch
nothing.*

## A model at work

```bash
MUJOCO_GL=osmesa uv run hylo world chat "a table with a red cube, a Panda that picks it up, a Go2 walking past" \
    --stage lab --vision --out runs/world-chat/lab --inbox runs/world-chat/lab/inbox.jsonl
uv run hylo watch runs/world-chat/lab
uv run hylo world tools                         # the tool manual
```

The model reads the stage before editing it, builds, acts and checks; a vision model also gets a view after every
action. The session is traced like an episode and can be steered through its inbox.

Coding agents can use the same tools over the Model Context Protocol:

```json
{"command": "uv", "args": ["run", "hylo", "mcp", "--surface", "mujoco.world", "--param", "stage=lab"]}
```

Models do make mistakes here: forgetting to make an object movable, or weakening a check until it passes. Read the
receipts and run the checks yourself before relying on a session's own summary.

## Tasks with roles

`hylo roles run CAMPAIGN.yaml` works through a set of tasks, each a stage, a request and a goal, split into
development and held-out tasks.

- A worker session solves each development task on a fresh copy of its stage. Every tool call goes into a ledger
  and counts against the task's budget.
- A solved task's actions become a recipe skill, keyed by the reasons its goal failed at the start.
- A verifier replays the recipe on fresh copies without a model. The skill joins the library only if the goal
  then holds.
- Held-out tasks run last; they are never used to propose or verify skills. When a task's goal fails with the
  same reasons, the matching skills are offered to the worker.

## In the Studio

The World page lists stages, builds a stage's world, shows a view you can orbit, runs actions and checks by hand, and
runs chat sessions with their transcript. See [Studio](studio.md#world).

<video src="../../assets/videos/studio-world.mp4" poster="../../assets/videos/studio-world.jpg" controls muted playsinline preload="none" width="100%" aria-label="The Studio's World page: building a stage, orbiting the view, an action and a goal check by hand, a chat transcript"></video>

*A stage built into a world, the free view, an action by hand with its receipt, a goal check with its reason code, and a recorded chat session's transcript.*

## Next

- [Tool-calling agents](tool-agents.md): a model operating a robot in benchmark tasks.
- [Showcase](../showcase/tool-agents.md#worlds): recorded scenes with their measured receipts.
- [Security](security.md#worlds-and-mcp): what the world tools and the MCP server expose.
