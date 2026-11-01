# Deployments repository

What runs on a lab's robots is configuration, not code, and it is the lab's own: robot names, network addresses,
joint limits, safety limits. It lives in a private `<lab>-deployments` repository, started from
`deployments-template`. The repository holds configuration only; every component it names (environments, agents,
guards) is registered by an installed worldcurrent repository.

```text
<lab>-deployments/
├── README.md
└── workcells/
    ├── sim_arm.yaml          a simulated arm, no hardware: bring-up and operator flow
    ├── so101.yaml            an SO-101 arm through LeRobot's Robot interface
    └── libero10_sim.yaml     LIBERO-10 in simulation, with the robot-side runtime
```

```bash
uv run wc serve workcell --config workcells/sim_arm.yaml --port 8102
uv run wc serve workcell --config workcells/so101.yaml --host 0.0.0.0 --port 8100 --token $WC_TOKEN
```

## A workcell config

Each file is one workcell (`WorkcellConfig`; all fields in [deployment](../user-guide/deployment.md#workcells)).
The template for a real arm:

```yaml
name: so101
env:
  type: lerobot.robot
  remote: {runtime: robot}              # the robot computer's venv with lerobot + feetech (execution profile)
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
policy: {url: "ws://gpu-box:8000/wc", protocol: wc}
runtime: {clock: wall, refill_steps: 10, max_hold_steps: 30, require_reset_confirm: true, verdict_timeout_s: 120}
safety: {max_delta: 8.0}
image_every: 5
max_steps: 900
output_dir: runs/workcell
```

## Calibration and limits

| What | Where | Notes |
|---|---|---|
| motor calibration | LeRobot's own calibration, keyed by the robot `id` (`arm1`) | done with LeRobot's tools on the robot computer; not stored by worldcurrent |
| joint limits | `env.params.action_low` / `action_high` | in the robot's units (degrees, gripper 0-100); required for a real robot |
| per-step limit in the robot | `robot.params.max_relative_target` | LeRobot clamps each commanded change; keep it |
| home pose | `env.params.home`, `home_steps` | reset moves there by interpolation, each step within the shield's limits |
| cameras | `env.params.cameras` | robot camera name to observation name (`agentview`, `wrist`) |
| control rate | `env.params.control_hz` | the wall-clock loop rate |

## Safety limits and keep-out zones

`safety` configures the SafetyShield of the workcell ([safety](../user-guide/safety.md)). The mandatory guards
(non-finite actions abort first, the action box is enforced last) are always on; config can only add guards or
tighten limits:

```yaml
safety:
  max_delta: 8.0                                   # largest change per step, in action units
  guards:
    - type: keep_out                               # a box the controlled point must not enter
      params: {state_key: eef_pos, low: [0.3, -0.2, 0.0], high: [0.6, 0.2, 0.3], action_dims: [0, 1, 2], margin: 0.02}
```

`keep_out` zeroes the delta-position components that would move the point (`state_key`, read from the observation
state) into the box or deeper into it; it needs a Cartesian end-effector state and delta-position actions, so it does
not apply to joint-space control such as the SO-101 template. Other built-in guards: `delta_limit`, `workspace`,
`norm_limit`; labs can add their own guard plugins ([extending](../harness/extending.md)).

The SafetyShield is a software layer, not a certified safety function: keep the robot's own limits and a hardware
e-stop within reach.

## Tokens and addresses

- Never commit tokens. Pass them at start-up (`--token $WC_TOKEN`) from the machine's environment or a secret
  store; policy endpoints in a config may carry `token`, but prefer giving it when starting the episode.
- A workcell binds to `127.0.0.1` unless `--host` says otherwise; expose it (`0.0.0.0`) only on a robot network and
  always with `--token`.
- Policy server addresses (`policy.url`) name hosts on your network (`gpu-box`); the control plane can also choose
  the endpoint per episode.

## Machine-specific settings

Interpreter paths and environment variables of the robot computer belong in its
[execution profile](profiles.md) (`wc profile set-runtime robot ...`), not in the repository: the config says
`remote: {runtime: robot}` and works on any robot computer that registered that runtime.
