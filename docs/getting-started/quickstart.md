# Quickstart

Run a controller on MuJoCo planar reach and inspect its results. A two-link arm moves its fingertip to a target.
This CPU example checks that execution and recording work before you try a model or a robot skill.

Complete [Installation](installation.md), then run the commands from **`bench/`**:

```bash
cd bench
```

## 1. Run { #1-run-an-experiment }

An experiment config names a benchmark and its split, an environment and an agent:

```yaml title="bench/examples/configs/mujoco_reach.yaml"
schema_version: hylo.experiment/v0.1
name: mujoco-reach
benchmark: {type: mujoco/reach-v0, split: validation}
env: {type: mujoco.planar_reach}
agent: {type: baseline.planar_ik, params: {kp: 0.3}}
output_dir: runs
```

```bash
uv run hylo run examples/configs/mujoco_reach.yaml
```

Each episode is printed as it ends (`[20] mujoco/planar_reach_random seed=10009 success (32 steps)`), then the run's
metrics:

```json
{
  "run_dir": "runs/mujoco-reach-validation-2342f91d706e83e9-eaf39f",
  "config_digest": "2342f91d706e83e9",
  "success_mean": 1.0,
  "safety_interventions_mean": 0.0,
  "steps_mean": 35.25,
  "n_episodes": 20,
  "n_scored": 20
}
```

The run directory contains the results and traces. Its random suffix will differ on your machine.

## 2. Inspect { #read-the-traces }

Use the `run_dir` printed above to read a run. Its last six characters are random, so yours differs
([what a run contains](../user-guide/experiments.md#runs-and-traces)):

```bash
uv run hylo trace <run_dir>                  # the metrics, then every episode id
uv run hylo trace <run_dir> <episode_id>     # one episode, for example mujoco.planar_reach_fixed-s10000-2749d014
```

For one episode, `hylo trace` counts the events and prints the episode's end record. The trace holds every action
the agent proposed (`agent.chunk`), what the safety shield decided (`safety.review`) and what was executed
(`action`):

```text
Counter({'observation': 31, 'agent.chunk': 30, 'safety.review': 30, 'action': 30, 'step.result': 30,
         'privileged.state': 30, 'episode.start': 1, 'episode.end': 1})
{
  "status": "success",
  "success": true,
  "steps": 30,
  "termination_reason": "terminated",
  "safety_interventions": 0
}
```

## Outputs { #what-you-have-now }

A completed run contains 20 scored episodes. In the recorded reference run all 20 succeed, with no safety
interventions and an average of 35.25 steps. `hylo trace` lets you inspect what was proposed and executed.
See [Experiments](../user-guide/experiments.md#runs-and-traces) for the files and event types.

## Next

- [First improvement](first-improvement.md): compare controllers and promote a better version.
- [Choose your next task](next-steps.md): worlds, policies, programs, memory or deployment.

<span id="2-score-a-policy-under-a-protocol"></span>
<span id="3-improve-a-policy-with-a-campaign"></span>
<span id="4-serve-the-promoted-version"></span>
<span id="5-look-at-it-in-studio"></span>
The evaluation, campaign, serving and Studio steps are in [First improvement](first-improvement.md).
