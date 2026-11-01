# Adding an environment

You will add a simulator and end with a scorecard under your own evaluation protocol. The example, `slider`, is a
point on a rail that must reach a goal. `hylo-env-mujoco` and `hylo-env-libero` in hylo-bench are the full
references. You need the [development workspace](../getting-started/installation.md).

An environment is the simulator **plus** the task logic. It decides success; the agent never does.

## 1. Create the package

There is no `hylo plugin new` template for environments. From the workspace root, create the package by hand in
`plugins/packages/`:

```text
plugins/packages/hylo-env-slider/
├── pyproject.toml
└── src/hylo_env_slider/
    ├── __init__.py       # META
    └── env.py            # SliderEnv, slider_benchmark, SliderPolicy
```

```toml title="pyproject.toml"
[project]
name = "hylo-env-slider"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["hylo-core", "numpy>=1.24"]
license = "Apache-2.0"

[project.entry-points."hylo.envs"]
"slider" = "hylo_env_slider.env:SliderEnv"

[project.entry-points."hylo.benchmarks"]
"slider-v0" = "hylo_env_slider.env:slider_benchmark"

[project.entry-points."hylo.policies"]
"slider.p" = "hylo_env_slider.env:SliderPolicy"

[project.entry-points."hylo.meta"]
"hylo-env-slider" = "hylo_env_slider:META"

[build-system]
requires = ["hatchling>=1.24"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/hylo_env_slider"]
```

```python title="src/hylo_env_slider/__init__.py"
META = {"contracts": {"envs": "hylo.env/v0.1", "benchmarks": "hylo.benchmark/v0.1", "policies": "hylo.policy/v0.1"},
        "maturity": "unverified"}
```

`META` and maturity: [extending Hylo](../harness/extending.md).

## 2. Write the environment

An environment has four methods: `spec`, `reset`, `step` and `close` ([contracts](../api/contracts.md)).

```python title="src/hylo_env_slider/env.py"
"""A point on a rail that must reach a goal: the smallest useful Environment."""

from __future__ import annotations

import numpy as np

from hylo.core.agent import AgentSpec, EpisodeContext
from hylo.core.benchmark import Benchmark, rsi_splits
from hylo.core.task import TaskInstance, TaskSpec
from hylo.core.types import (Action, ActionSemantics, BoxSpace, EnvCapabilities, EnvSpec, Observation,
                             ObservationSpec, StepResult)

MAX_STEP = 0.02           # metres per control step at |action| = 1
SEMANTICS = ActionSemantics(control_mode="eef_delta_pos", frame="base", dim_labels=("x",), max_step=(MAX_STEP,))


class SliderEnv:
    def __init__(self, control_hz: float = 20.0) -> None:
        self.control_hz = control_hz
        self.pos = self.goal = 0.0
        self.task: TaskInstance | None = None

    def spec(self) -> EnvSpec:                            # cheap: no simulator work here
        return EnvSpec(
            name="slider", version="0.1",
            observation=ObservationSpec(state={"pos": (1,), "goal": (1,)}, units={"pos": "m", "goal": "m"}),
            action=BoxSpace(shape=(1,), low=(-1.0,), high=(1.0,), semantics=SEMANTICS),
            control_hz=self.control_hz,
            capabilities=EnvCapabilities(seedable=True))

    def reset(self, task: TaskInstance) -> Observation:
        rng = np.random.default_rng(task.seed)            # everything random comes from the seed
        self.task = task
        self.pos = float(rng.uniform(-0.5, 0.5))
        self.goal = float(task.spec.params.get("goal", rng.uniform(-0.5, 0.5)))
        return self._observe()

    def _observe(self) -> Observation:
        return Observation(state={"pos": np.array([self.pos]), "goal": np.array([self.goal])},
                           instruction=self.task.spec.instruction)

    def step(self, action: Action) -> StepResult:
        self.pos += float(np.asarray(action.data).reshape(-1)[0]) * MAX_STEP
        if not np.isfinite(self.pos):                     # an infrastructure fault, not a policy failure
            return StepResult(observation=self._observe(), reward=None, terminated=False, truncated=True,
                              info={"sim_error": "position is not finite"})
        if abs(self.pos) > 1.0:
            return StepResult(observation=self._observe(), reward=None, terminated=True, truncated=False,
                              success=False, info={"fail_reason": "left the rail"})
        success = abs(self.pos - self.goal) < 0.01
        return StepResult(observation=self._observe(), reward=-abs(self.pos - self.goal), terminated=success,
                          truncated=False, success=success)

    def close(self) -> None:
        pass
```

The rules this follows:

`spec()` declares observations and actions
:   It builds no simulator and must serialize to JSON. Declare every state key with its shape and units, cameras as
    `(H, W, 3)` uint8, and the action box with its real bounds and semantics. `max_step` says what the units mean at
    `|action| = 1`. An environment can also declare an always-on workspace limit in `EnvSpec.workspace`.

`reset()` depends on the seed only
:   Draw all reset randomness from `task.seed`: the same seed must give the same init state, so a candidate and its
    parent face the same situations. Splits are sets of seeds; if several seeds share one stored state (LIBERO
    loads `seed % 50`), keep the splits disjoint in states, not only in seeds.

`step()` separates success from ending
:   `success` is the task predicate. `terminated` means the episode is over for task reasons; add
    `info["fail_reason"]` when it failed for good. `truncated` means it stopped for other reasons. `success: None`
    means the environment cannot judge.

Simulator faults are not policy failures
:   Return `truncated=True` with `info["sim_error"]`, or raise `EnvironmentFault`. The episode is then
    `infra_invalid`, which scoring and campaigns keep apart from failures.

How the last step becomes an episode status is in [execution lifecycle](../harness/execution-lifecycle.md).
Optional capabilities, such as snapshots or privileged state, are declared in `EnvSpec.capabilities`
([interfaces: environment](../harness/interfaces/environment.md)).

## 3. Add tasks and a benchmark

A `TaskSpec` describes one task: a globally unique `id`, `version`, `instruction`, `max_steps`, environment-specific
`params` and `tags`. A `Benchmark` is tasks plus splits.

```python title="src/hylo_env_slider/env.py (continued)"
def slider_benchmark(protocol: str = "rsi", n_states: int = 50) -> Benchmark:
    tasks = (TaskSpec(id="slider/reach", version="1", instruction="reach the goal", max_steps=100, tags=("slider",)),)
    splits = rsi_splits(n_states, (20, 30, 40)) if protocol == "rsi" else {"validation": tuple(range(1000, 1020))}
    return Benchmark(id="slider-v0", version="0.1", tasks=tasks, splits=splits)
```

The `protocol` argument chooses a split scheme, not an evaluation protocol; the name follows the built-in benchmarks.
`rsi_splits` gives the four [splits](../user-guide/campaigns.md#splits) that campaigns need: `search`, `search_val`,
`gate` and `heldout`, here 20, 10, 10 and 10 init states.

## 4. Install and check it

A conformance check needs an agent. Add this proportional controller, a [policy](adding-a-policy.md), to `env.py`:

```python title="src/hylo_env_slider/env.py (continued)"
class SliderPolicy:
    """A proportional controller: move a fraction `gain` of the remaining distance each step."""

    def __init__(self, gain: float = 0.5) -> None:
        self.gain = gain

    def spec(self) -> AgentSpec:
        return AgentSpec(name="slider.p", version="0.1", required_state=("pos", "goal"),
                         action_semantics=SEMANTICS, action_dim=1, components={"policy": "slider.p@0.1"})

    def reset(self, ctx: EpisodeContext) -> None:
        pass

    def default_execution_steps(self) -> int:
        return 1

    def sample(self, observation: Observation, seeds: list[int] | None, noise_scale: float = 1.0) -> np.ndarray:
        s = observation.state
        a = np.clip(self.gain * (s["goal"] - s["pos"]) / MAX_STEP, -1.0, 1.0)     # deterministic: seeds unused
        return np.tile(a.reshape(1, 1, 1), (len(seeds) if seeds else 1, 1, 1))   # (N, T=1, A=1)
```

Add the package to the workspace and install it, as in
[adding a policy](adding-a-policy.md#1-create-and-install-the-package). From here on, run commands from `bench/`:

```bash
uv run python harness/dev/workspace.py
uv sync                                     # add the --group options you used in Installation
cd bench
uv run hylo plugins | grep slider
```

```text
envs         slider                         hylo.env/v0.1        unverified      Apache-2.0
policies     slider.p                       hylo.policy/v0.1     unverified      Apache-2.0
benchmarks   slider-v0                      hylo.benchmark/v0.1  unverified      Apache-2.0
```

Save an experiment config in `bench/` and check it:

```yaml title="slider.yaml"
schema_version: hylo.experiment/v0.1
name: slider-p
benchmark: {type: slider-v0, split: search_val}
env: {type: slider}
agent: {type: policy, params: {policy: {type: slider.p}}}
output_dir: runs
```

```bash
uv run hylo conformance slider.yaml --agent
```

```text
environment SliderEnv: PASS
  [  ok] spec() is cheap and typed: 0.0 ms
  [  ok] spec survives JSON (wire format)
  [  ok] reset returns an Observation matching the spec: instruction='reach the goal'
  [  ok] reset is deterministic in the seed
  [  ok] step returns StepResult with separate success/terminated/truncated: 5 steps
  [skip] snapshot/restore reproduces the trajectory
  [  ok] close() works
agent PolicyAgent: PASS
  [  ok] spec is compatible with the environment: slider.p
  [  ok] act returns finite chunks of the env's action shape
  [  ok] reset leaves no state behind (same seed, same episode)
```

A PASS means the contract holds; it does not check your success predicate. The snapshot check skips because `slider`
does not declare `snapshot`. Options for slow or nondeterministic simulators are in [testing](testing.md).

## 5. Run it

```bash
uv run hylo run slider.yaml
```

```json
{
  "run_dir": "runs/slider-p-search_val-8961738693fd8af9-1dd60d",
  "config_digest": "8961738693fd8af9",
  "success_mean": 1.0,
  "safety_interventions_mean": 0.0,
  "steps_mean": 10.2,
  "n_episodes": 10,
  "n_scored": 10
}
```

## 6. Score it under an evaluation protocol

An [evaluation protocol](../benchmarking/protocols.md) fixes everything except the agent being scored:

```yaml title="slider-v1.yaml"
schema_version: hylo.protocol/v0.1
name: slider-reach
version: "1"
description: |
  The slider reaches its goal: the 10 held-out init states (seeds 40-49).
benchmark: {type: slider-v0, split: heldout, params: {protocol: rsi}}
env: {type: slider}
trace: {record_privileged: false, image_every: 0}
workers: 4
requires: [hylo-env-slider]
```

```bash
uv run hylo bench show slider-v1.yaml          # digest: 1fdbb3364711b868
uv run hylo bench run slider-v1.yaml --name slider.p \
    --policy '{"type": "policy", "params": {"policy": {"type": "slider.p"}}}'
uv run hylo bench leaderboard scorecards
```

```text
### slider-reach v1  (`1fdbb3364711b868`)

| # | policy | success % | 95% CI | episodes | mean steps |
|---|---|---|---|---|---|
| 1 | slider.p | 100.0 | 72.2–100.0 | 10 | 14 |
```

Ten episodes give a wide interval. The built-in protocols use 100 (MuJoCo reach) and 500 (LIBERO-10).

## Variants

=== "Subprocess, another venv"

    ```yaml
    env: {type: slider, remote: {runtime: sim}}
    ```

    ```bash
    uv run hylo profile set-runtime sim --python /path/to/venv/bin/python
    ```

    Install hylo-core and your package into that venv. A subprocess is not part of the `config_digest`
    ([when two runs are comparable](../user-guide/experiments.md#when-two-runs-are-comparable)).

=== "WebSocket, another machine"

    ```bash
    uv run hylo serve env slider --port 8799          # in the simulator's venv; --host 0.0.0.0 to expose it
    ```

    ```yaml
    env: {type: remote.ws, params: {url: "ws://sim-box:8799"}}
    ```

    Each connection gets its own environment instance. The URL is part of the `config_digest`. Use `--token-env`
    for a shared token across untrusted networks.

=== "A robot"

    A robot is an environment with three differences. It sets `real_robot=True`, so any safety-shield change aborts
    the episode. It returns `success: None` and leaves the verdict to the operator or a calibrated judge. It
    provides `hold_action(last)`, which the episode loop executes when the policy is late, and `stop()`, which it
    calls when an episode aborts for safety. `lerobot.robot` is the reference ([deployment](../user-guide/deployment.md)).

## Next

- Score policies on it: [benchmarking](../benchmarking/index.md), [adding a policy](adding-a-policy.md).
- Improve a policy on it with a campaign: [campaigns](../user-guide/campaigns.md).
- Reference: [hylo-env-mujoco API](../api/packages/hylo-env-mujoco.md),
  [hylo-env-libero API](../api/packages/hylo-env-libero.md), [`hylo conformance`](../cli/index.md#hylo-conformance),
  [`hylo serve`](../cli/index.md#hylo-serve), [`hylo bench`](../cli/index.md#hylo-bench).
