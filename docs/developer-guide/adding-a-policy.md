# Add a policy { #adding-a-policy }

You will write a policy, run it on MuJoCo planar reach, and end with its scorecard on the `mujoco-reach` leaderboard
next to a baseline. You need the [development workspace](../getting-started/installation.md) with hylo-bench.

A policy is the model inside an agent; built-in agents decide how its chunks run ([policies](../user-guide/policies.md)).
If your decision logic is more than drawing chunks from one model, write an [agent](../harness/interfaces/agent.md)
instead (`hylo plugin new agent NAME`).

## 1. Create a package { #1-scaffold-the-package }

From the workspace root, create the package in `plugins/packages/`:

```bash
uv run hylo plugin new policy my-reacher --dir plugins/packages
```

```text
plugins/packages/hylo-plugin-my-reacher/
├── pyproject.toml              # dependencies and entry points
├── src/wc_my_reacher/
│   ├── __init__.py             # META: contract version and maturity
│   └── plugin.py               # MyReacherPolicy
└── tests/test_wc_my_reacher.py # conformance, and "it reaches the target"
```

Add a licence line under `[project]` in `pyproject.toml`, for example `license = "Apache-2.0"`. Then add the package
to the workspace and install it:

```bash
uv run python harness/dev/workspace.py      # adds every package in plugins/packages/ to the workspace
uv sync                                     # add the --group options you used in Installation
cd bench
uv run hylo plugins | grep my-reacher
```

```text
policies     my-reacher                     hylo.policy/v0.1     unverified      Apache-2.0
```

A package in `plugins/packages/` is a workspace member, so every `uv sync` keeps it installed, editable. Do not use
the `uv pip install -e` hint that `hylo plugin new` prints: the next `uv sync` removes a package installed that way.
From here on, run commands from `bench/`. `META` and maturity: [extending Hylo](../harness/extending.md).

## 2. Implement the contract { #2-the-contract }

A policy provides four methods and inherits from nothing ([contracts](../api/contracts.md)). The generated policy
drives the planar arm with two-link inverse kinematics plus seeded noise. These are the methods you change:

```python title="src/wc_my_reacher/plugin.py (excerpt)"
class MyReacherPolicy:
    def __init__(self, gain: float = 0.3, horizon: int = 8, noise: float = 0.05, l1: float = 0.3, l2: float = 0.25,
                 max_step: float = 0.05) -> None:
        self.gain, self.horizon, self.noise, self.l1, self.l2, self.max_step = gain, horizon, noise, l1, l2, max_step

    def spec(self) -> AgentSpec:
        # what it reads and what its actions mean: checked against the environment before the first step
        return AgentSpec(name="my-reacher", version="0.1", required_state=("qpos", "target_pos"),
                         action_semantics=ActionSemantics(control_mode="joint_delta", frame="base"), action_dim=2,
                         components={"policy": "my-reacher@0.1"})

    def reset(self, ctx: EpisodeContext) -> None:
        pass

    def default_execution_steps(self) -> int:
        return max(1, self.horizon // 2)

    # _ik(x, y): two-link inverse kinematics, as generated

    def sample(self, observation: Observation, seeds: list[int] | None, noise_scale: float = 1.0) -> np.ndarray:
        s = observation.state
        err = (self._ik(*np.asarray(s["target_pos"], float)[:2]) - np.asarray(s["qpos"], float) + np.pi) % (2 * np.pi) - np.pi
        a = np.clip(self.gain * err / self.max_step, -1.0, 1.0)
        rngs = [np.random.default_rng(x) for x in seeds] if seeds else [np.random.default_rng()]
        return np.stack([np.clip(a + self.noise * noise_scale * r.standard_normal((self.horizon, 2)), -1.0, 1.0)
                         for r in rngs])                                    # (N, T, A)
```

`spec()`
:   The policy's identity and assumptions. Every key in `required_state` and `required_cameras` must exist in the
    environment's observations, and `action_dim` and the action semantics must match its action space. Before the
    first step, the episode loop compares this with the environment. A different control mode, rotation or action
    size stops the run. A different frame or gripper convention only warns.

`reset(ctx)`
:   Clears per-episode state. `ctx.emit(type, payload)` writes your own events into the trace.

`default_execution_steps()`
:   How many actions of a chunk run before the next call, unless the agent overrides it. It must not exceed the
    chunk length `T`.

`sample(observation, seeds, noise_scale)`
:   Returns `(N, T, A)` chunks, one per seed (`N = 1` when `seeds` is `None`). Draw **all** randomness from
    `seeds`. Agents derive each seed from the task, the chunk index and the sample index, so a candidate and its
    parent see the same noise on the same init state. The campaign's paired tests rely on this. A deterministic
    policy ignores the seeds and returns `N` identical chunks. `noise_scale` scales the noise; 1.0 is the policy's
    own level.

!!! warning "Units and bounds"
    Chunks are in the units of the environment's action space: here, normalised joint deltas in [-1, 1]. The
    safety shield clips anything outside the bounds and counts larger excursions as interventions
    ([safety](../user-guide/safety.md)).

## 3. Validate { #3-check-it }

```bash
uv run pytest ../plugins/packages/hylo-plugin-my-reacher/tests
uv run hylo plugin check policy my-reacher
```

```text
2 passed in 0.23s
policy MyReacherPolicy: PASS
  [  ok] spec is compatible with the environment: my-reacher
  [  ok] sample returns finite (N, T, A) chunks of the action shape: chunk 8 x 2
  [  ok] the same seeds give the same chunks: stochastic (seeded)
  [  ok] default_execution_steps is within the chunk
```

The generated tests run the conformance check and one full episode that must reach the target. `hylo plugin check`
checks only the interface and warns about missing metadata. Neither measures quality; step 5 does. More options are
in [testing](testing.md).

## 4. Run { #4-run-it }

Save an experiment config in `bench/` ([experiments](../user-guide/experiments.md)). The `policy` agent runs your
policy:

```yaml title="my_reacher.yaml"
schema_version: hylo.experiment/v0.1
name: mujoco-reach-my-reacher
benchmark: {type: mujoco/reach-v0, split: validation}
env: {type: mujoco.planar_reach}
agent: {type: policy, params: {policy: {type: my-reacher}}}
output_dir: runs
```

```bash
uv run hylo run my_reacher.yaml
```

```json
{
  "run_dir": "runs/mujoco-reach-my-reacher-validation-76e6326fbd816822-13c8a6",
  "config_digest": "76e6326fbd816822",
  "success_mean": 1.0,
  "safety_interventions_mean": 0.0,
  "steps_mean": 35.85,
  "n_episodes": 20,
  "n_scored": 20
}
```

The policy never knows which agent runs it. `temporal_ensemble` and `steered` take the same policy
([choose an agent](../user-guide/policies.md#agents-that-run-a-policy)):

```yaml
agent: {type: steered, params: {sampler: {type: my-reacher, params: {noise: 0.2}}, steering: {n_samples: 4, selector: medoid}}}
```

## 5. Evaluate { #5-score-it-on-the-leaderboard }

An [evaluation protocol](../benchmarking/protocols.md) fixes everything except the agent being scored. Score the agent
that runs your policy, and the planar IK baseline, under the `mujoco-reach` protocol:

```bash
uv run hylo bench run mujoco-reach --name my-reacher \
    --policy '{"type": "policy", "params": {"policy": {"type": "my-reacher"}}}'
uv run hylo bench run mujoco-reach --name planar-ik --policy baseline.planar_ik
uv run hylo bench leaderboard scorecards
uv run hylo bench compare scorecards/mujoco-reach/my-reacher.json scorecards/mujoco-reach/planar-ik.json
```

```text
### mujoco-reach v1  (`a76c7037efb84660`)

| # | policy | success % | 95% CI | episodes | mean steps |
|---|---|---|---|---|---|
| 1 | my-reacher | 100.0 | 96.3–100.0 | 100 | 37 |
| 2 | planar-ik | 100.0 | 96.3–100.0 | 100 | 36 |
```

```json
{
  "candidate": "my-reacher",
  "baseline": "planar-ik",
  "n_pairs": 100,
  "candidate_wins": 0,
  "parent_wins": 0,
  "p_value": 1.0
}
```

No episode separates the two, so `p_value` is 1.0 ([compare two scorecards](../benchmarking/index.md#statistics)).

## Variants

**Learned weights.** The constructor takes a `path` to a sealed artifact and loads the weights from it. Configs
reference the artifact by its store id, `spec()` reports the artifact's digest in `components`, and `weights_license`
names the licence of the weights ([learning](../user-guide/learning.md), [store](../user-guide/store.md)).

**A model with its own stack.** Three ways keep its dependencies out of the workspace venv:

=== "In another venv"

    ```yaml
    agent:
      type: remote
      params: {ref: lerobot.steered, runtime: lerobot, params: {repo_id: lerobot/smolvla_libero}}
    ```

    `runtime` names an interpreter from this machine's [profile](../configuration/profiles.md). Install your package,
    hylo-core and hylo-agents into that venv.

=== "Behind a server"

    ```yaml
    agent: {type: openpi, params: {url: "ws://gpu-box:8000", preset: libero, execution_steps: 5}}
    ```

    A client of openpi's own policy server. The episode loop, the safety shield and the trace stay on this machine.

=== "As a Hylo policy server"

    ```bash
    uv run hylo serve policy --config my_reacher.yaml --port 8001
    ```

    ```yaml
    agent: {type: remote.ws, params: {url: "ws://gpu-box:8001/hylo"}}
    ```

    Serves the config's agent over WebSocket, one session at a time ([deployment](../user-guide/deployment.md)).

## Next

- Improve the policy with a campaign: [campaigns](../user-guide/campaigns.md), [adding a learner](adding-a-learner.md).
- Put it on a robot: [deployment](../user-guide/deployment.md).
- Reference: [extending Hylo](../harness/extending.md), [plugin system](../harness/plugin-system.md),
  [hylo-policies API](../api/packages/hylo-policies.md), [`hylo plugin`](../cli/index.md#hylo-plugin).
