# Create a world { #create-and-run-a-world }

Create a small stage, compile it into a MuJoCo world, advance the simulation and check an outcome. This first
example uses a falling cube, so it needs no model endpoint, downloaded robot assets or camera renderer.

Complete [Installation](../getting-started/installation.md). Run commands from the **workspace root**.

## Build a stage { #build-your-first-world }

Create a `runs/` directory if needed. Save the following as `runs/first_world.py`:

```python
from hylo.envs.mujoco.world_tools import Workspace

workspace = Workspace("runs/stages", "first_world")

def call(name, **arguments):
    reply = workspace.surface.call(name, arguments)
    if not reply.ok:
        raise RuntimeError(f"{name}: {reply.error}")
    return reply.result

try:
    stage = call("stage_show")
    if stage["revision"] == 0:
        call("stage_edit", expected_revision=0, ops=[
            {"op": "add", "entity": {
                "id": "table", "shape": {"type": "box", "size": [0.4, 0.4, 0.05]},
                "pose": {"pos": [0, 0, 0.35]}}},
            {"op": "add", "entity": {
                "id": "cube", "shape": {"type": "box", "size": [0.02, 0.02, 0.02]},
                "body": {"dynamic": True, "mass": 0.05}, "pose": {"pos": [0, 0, 0.6]}}},
        ])
    built = call("world_build")
    print("movable:", built["movable"])
    call("advance", seconds=1.0)
    checked = call("check", goal={"op": "contact", "a": "cube", "b": "table"})
    print("cube touches table:", checked["satisfied"])
finally:
    if workspace.world is not None:
        workspace.world.close()
```

```bash
uv run python runs/first_world.py
```

Expected output includes `movable: ['cube']` and `cube touches table: True`. The stage and its revision history
are saved under `runs/stages/first_world/`. Rerunning rebuilds that saved stage. Use another stage name for a
separate example if you have edited this one.

## Add a robot { #add-a-robot-and-inspect-the-world }

Add an entity with a `robot` pack through `stage_edit`, then rebuild before acting. Use the
[pack and action reference](../reference/worlds.md#robot-packs) to select controls supported by that robot.
Camera images and Studio's live scene view require [rendering setup](../getting-started/optional-environments.md#camera-rendering).

For an interactive view, build the [Studio frontend](../getting-started/optional-environments.md#studio-web-ui)
and run `uv run hylo playground --repo .` from the workspace root. Open **World** and select `first_world`.
Rebuild it in Studio: the Python process above has closed its simulation, while the saved stage remains.

## Model control { #a-model-at-work }

Configure a chat backend and camera rendering first. The following uses the default model configuration;
`hylo world chat --help` lists the model options. Run it from the workspace root.

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

## Role campaigns { #tasks-with-roles }

`hylo roles run CAMPAIGN.yaml` works through a set of tasks, each a stage, a request and a goal, split into
development and held-out tasks.

- A worker session solves each development task on a fresh copy of its stage. Every tool call goes into a ledger
  and counts against the task's budget.
- A solved task's actions become a recipe skill, keyed by the reasons its goal failed at the start.
- A verifier replays the recipe on fresh copies without a model. The skill joins the library only if the goal
  then holds.
- Held-out tasks run last; they are never used to propose or verify skills. When a task's goal fails with the
  same reasons, the matching skills are offered to the worker.

## Studio { #in-the-studio }

[Use the World page to inspect and operate the scene](studio.md#world).

<span id="chat-to-world-demo"></span>

[Watch the recorded scene-construction case](../use-cases/worlds.md#chat-to-world-demo).

<span id="why-worlds"></span>
<span id="from-language-to-a-world"></span>
<span id="principles"></span>
<span id="stages"></span>
<span id="robot-packs"></span>
<span id="running-a-world"></span>
<span id="checking-goals"></span>
<span id="cameras-and-data"></span>
<span id="people"></span>

## Reference

[Worlds & tools](../reference/worlds.md) covers stages, robot packs, execution, goals, cameras and people.
[World concepts](worlds/overview.md) explains the model; [execution design](../developer-guide/execution-model.md#worlds) covers implementation.

## Next

- [Tool-calling agents](tool-agents.md): run a model on a benchmark task.
- [World examples](../use-cases/worlds.md): recorded scenes and measured outcomes.
- [Security](security.md#worlds-and-mcp): world-tool execution and access boundaries.
