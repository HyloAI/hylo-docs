# Deployments repository

A lab's robot setup (robot names, network addresses, joint limits, safety limits) belongs to the lab. Keep it in a
private `<lab>-deployments` repository created from the deployments template. The repository holds YAML only; every
environment, agent and guard it names comes from an installed Hylo package.

## Create it

```bash
git clone https://github.com/HyloAI/hylo-deployments-template.git mylab-deployments
cd mylab-deployments
git remote set-url origin <your lab's private repository>
```

```text
<lab>-deployments/
├── README.md
└── workcells/
    ├── sim_arm.yaml          a simulated arm, no hardware: bring-up and operator flow
    ├── so101.yaml            an SO-101 arm through LeRobot's Robot interface
    └── libero10_sim.yaml     LIBERO-10 in simulation, with the realtime runner
```

Add one workcell file per robot or simulator. Set up the robot computer first
([deployment, step 2](../user-guide/deployment.md#step-2-set-up-the-robot-computer)).

## A workcell file

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
| home pose | `env.params.home`, `home_steps` | reset moves there by interpolation; each step is clipped to the action box only and does not pass through the safety shield ([safety](../user-guide/safety.md#on-a-real-robot)) |
| cameras | `env.params.cameras` | robot camera name to observation name (`agentview`, `wrist`) |
| control rate | `env.params.control_hz` | the wall-clock loop rate |

## Safety settings

`safety:` can only add guards or tighten limits. The action box itself comes from `action_low` and `action_high` in
this file, so review changes there as safety changes. [Safety](../user-guide/safety.md#configure-guards) describes
every guard.

## What stays out

| Keep out of the repository | Put it here instead |
|---|---|
| tokens, including a policy endpoint's `token` | an environment variable or a secret store, passed when the workcell or the episode starts |
| interpreter paths, environment variables | the robot computer's [execution profile](profiles.md) |
| motor calibration | LeRobot's calibration files on the robot computer |

## Start it

From the deployments repository:

```bash
uv run hylo serve workcell --config workcells/sim_arm.yaml --port 8102
uv run hylo serve workcell --config workcells/so101.yaml --host 0.0.0.0 --port 8100 --token "$HYLO_TOKEN"
```

A workcell listens on `127.0.0.1:8100` by default. Bind it to `0.0.0.0` only on a robot network, and always with
`--token` ([security](../user-guide/security.md)). The workcell takes the token only as `--token VALUE`, so it is
visible in the robot computer's process list.
