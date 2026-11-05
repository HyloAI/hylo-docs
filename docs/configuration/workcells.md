# Workcell configuration

Fields read by `hylo serve workcell --config FILE`, defined by `hylo.serve.workcell.WorkcellConfig`.
For setup and operator steps, use [Deployment](../user-guide/deployment.md).
Keep shared YAML files in a [deployments repository](deployments-repo.md).

## Fields

`hylo serve workcell` takes `--config` (required), `--host` (default `127.0.0.1`), `--port` (default `8100`) and
`--token`. Its config:

| Field | Default | Meaning |
|---|---|---|
| `name` | required | the workcell's name; its run is `<output_dir>/workcell-<name>` |
| `env` | required | any environment plugin, local or in another venv (`remote: {runtime: ...}`) |
| `benchmark` | none | a benchmark whose `validation` tasks can be started by `task_id`; without it, free-form instructions only |
| `policy` | none | default policy endpoint: `url`, `protocol` (`hylo` or `openpi`), `token`, `params` |
| `runtime` | see below | the episode loop's timing |
| `safety` | `{}` | safety shield config: `max_delta`, `guards` ([safety](../user-guide/safety.md#configure-guards)) |
| `image_every` | `10` | keep every n-th camera frame in the trace; every frame is streamed live |
| `split` | `deployment` | the split recorded episodes get |
| `max_steps` | `600` | step limit for free-form instructions; benchmark tasks have their own |
| `output_dir` | `runs/workcell` | where the run is written, relative to the working directory |

The workcell's `runtime:` block holds the episode loop's timing. It takes the keys of an experiment's
[`timing:`](../user-guide/experiments.md#timing-sync-and-realtime), with these differences:

| Key | Workcell default | Meaning |
|---|---|---|
| `mode` | `realtime` | experiments default to `sync` |
| `clock` | `virtual` | set `wall` on hardware ([robot setup](../user-guide/deployment.md#2-the-robot-computer)) |
| `require_reset_confirm` | `false` | wait for the operator's `reset_done` before the move to home |
| `verdict_timeout_s` | `0` | how long to wait for a verdict when the environment cannot judge success |
| `record_privileged` | `true` | store privileged state, when the environment has any |

`runtime.image_every` has no effect: the top-level `image_every` decides which frames the trace keeps.

## Example

The template for a real arm:

```yaml title="workcells/so101.yaml"
name: so101
env:
  type: lerobot.robot
  remote: {runtime: robot}              # named runtime from this machine's profile: the venv with lerobot + feetech
  params:
    robot:
      type: so101_follower
      params: {port: /dev/ttyACM0, id: arm1, max_relative_target: 10.0}
    cameras: {}                         # e.g. {front: agentview, wrist: wrist} with configured cameras
    action_low: [-110, -100, -100, -100, -160, 0]
    action_high: [110, 100, 100, 100, 160, 100]
    home: [0, -90, 90, 0, 0, 10]
    home_steps: 90
    control_hz: 30
policy: {url: "ws://gpu-box:8000/hylo", protocol: hylo}   # protocol: the policy wire protocol (hylo or openpi)
runtime:                                # realtime execution settings, not a named runtime
  clock: wall                           # the default is virtual: always set wall on hardware
  refill_steps: 10
  max_hold_steps: 30
  require_reset_confirm: true
  verdict_timeout_s: 120
safety: {max_delta: 8.0}
image_every: 5
max_steps: 900
output_dir: runs/workcell
```

!!! warning "Set `clock: wall` on hardware"
    The `runtime:` block's `clock` defaults to `virtual`. A real robot needs `clock: wall`.

| What | Where | Notes |
|---|---|---|
| motor calibration | LeRobot's own calibration, keyed by the robot `id` (`arm1`) | made with LeRobot's tools on the robot computer; Hylo does not store it |
| joint limits (the action box) | `env.params.action_low`, `action_high` | in the robot's units (degrees, gripper 0-100); required for a real robot |
| per-step limit in the robot | `env.params.robot.params.max_relative_target` | LeRobot clamps each commanded change; keep it |
| home pose | `env.params.home`, `home_steps` | reset moves there by interpolation; each step is clipped to the action box only and does not pass through the safety shield ([safety](../user-guide/safety.md#safety-on-robots)) |
| cameras | `env.params.cameras` | robot camera name to observation name (`agentview`, `wrist`) |
| control rate | `env.params.control_hz` | the wall-clock loop rate |

## Safety limits

`safety:` can only add guards or tighten limits. The action box itself comes from `action_low` and `action_high` in
this file, so review changes there as safety changes. [Safety](../user-guide/safety.md#configure-guards) describes
every guard.

## API { #python-api-and-service-endpoints }

- [Serve package](../api/packages/hylo-serve.md): configuration models and runtime implementation.
- [Workcell API](../user-guide/deployment.md#workcell-api): HTTP endpoints and request types.
