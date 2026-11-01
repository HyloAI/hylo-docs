# Adding a policy

This tutorial takes a new policy from an empty directory to a scorecard on the `mujoco-reach` leaderboard. Each step
was run while writing it, and the outputs shown are real. It assumes the
[development workspace](../getting-started/installation.md) with hylo-bench next to the harness: MuJoCo
planar reach is the environment throughout.

A policy is the model inside an agent: given an observation, it draws action chunks, one per noise seed. You write
the policy. The agents in hylo-agents run it, temporally ensemble it or steer it, and the kernel, the SafetyShield,
traces, benchmarks and the gate treat it like any other policy. If your decision logic is more than drawing chunks
from one model (planning, switching between models, a remote service with its own loop), write an agent instead
(`hylo plugin new agent NAME`); see [interfaces: agent](../harness/interfaces/agent.md).

| Step | What you get |
|---|---|
| [1. Scaffold](#1-scaffold-the-package) | a plugin package that already passes its conformance check |
| [2. The contract](#2-the-contract) | `spec`, `reset`, `default_execution_steps`, `sample` |
| [3. Declare it](#3-declare-the-contract-version-maturity-and-licence) | contract version, maturity, licence |
| [4. Check it](#4-check-it) | conformance from pytest and from `hylo plugin check` |
| [5. Run it](#5-run-it-with-the-three-agents) | under `policy`, `temporal_ensemble` and `steered` |
| [6. Learn it](#6-a-learned-policy-weights-from-a-sealed-artifact) | weights from development runs, sealed, referenced by store id |
| [7. Score it](#7-score-it-and-put-it-on-the-leaderboard) | a scorecard and a place on the leaderboard |
| [8. Wrap an external model](#8-wrapping-an-external-model) | LeRobot, openpi, and models in another venv |

## 1. Scaffold the package

```bash
uv run hylo plugin new policy my-reacher --dir plugins
```

```text
created plugins/hylo-plugin-my-reacher
  install: uv pip install -e plugins/hylo-plugin-my-reacher
  check:   uv run pytest plugins/hylo-plugin-my-reacher/tests && hylo plugin check policy my-reacher
```

```text
plugins/hylo-plugin-my-reacher/
├── pyproject.toml                 # dependencies, the entry point, the declaration
├── src/hylo_my_reacher/
│   ├── __init__.py                # META: contract version and maturity
│   └── plugin.py                  # MyReacherPolicy
└── tests/test_wc_my_reacher.py    # conformance, and "it reaches the target"
```

The entry point is what makes the policy findable by name. Nothing in Hylo is edited:

```toml title="pyproject.toml"
[project]
name = "hylo-plugin-my-reacher"
version = "0.1.0"
dependencies = ["hylo-core", "hylo-agents", "numpy>=1.24"]

[project.entry-points."hylo.policies"]
"my-reacher" = "hylo_my_reacher.plugin:MyReacherPolicy"

[project.entry-points."hylo.meta"]
"hylo-plugin-my-reacher" = "hylo_my_reacher:META"
```

Install it into the workspace venv with `uv pip install -e plugins/hylo-plugin-my-reacher`. Until then, or to try
something without installing it, any plugin can be named as `module:attr` with its module on `PYTHONPATH`, for
example `type: "hylo_my_reacher.plugin:MyReacherPolicy"`. The commands below were run that way.

## 2. The contract

`core.policy.ChunkPolicy` ([API](../api/contracts.md)) has four methods:

```python
class ChunkPolicy(Protocol):
    def spec(self) -> AgentSpec: ...
    def reset(self, ctx: EpisodeContext) -> None: ...
    def default_execution_steps(self) -> int: ...
    def sample(self, observation: Observation, seeds: list[int] | None, noise_scale: float) -> np.ndarray:
        """(N, T, A) action chunks in the environment's units, one per seed (N = len(seeds), or 1 if None)."""
```

It is a `typing.Protocol`: you do not inherit from anything, you provide the methods. The generated policy drives
the planar arm with two-link inverse kinematics plus seeded noise:

```python title="src/hylo_my_reacher/plugin.py"
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

    def sample(self, observation: Observation, seeds: list[int] | None, noise_scale: float = 1.0) -> np.ndarray:
        s = observation.state
        err = (self._ik(*np.asarray(s["target_pos"], float)[:2]) - np.asarray(s["qpos"], float) + np.pi) % (2 * np.pi) - np.pi
        a = np.clip(self.gain * err / self.max_step, -1.0, 1.0)
        rngs = [np.random.default_rng(x) for x in seeds] if seeds else [np.random.default_rng()]
        return np.stack([np.clip(a + self.noise * noise_scale * r.standard_normal((self.horizon, 2)), -1.0, 1.0)
                         for r in rngs])                                    # (N, T, A)
```

What each method is for:

`spec()`
:   The policy's identity and its assumptions. Every key in `required_state` and `required_cameras` must exist in
    the environment's observations. `action_dim`, `control_mode` and `rotation_repr` must match the environment's
    action space. The kernel checks this before the first step (`core.compat`): a mismatch in control mode,
    rotation or dimension stops the run; a different frame or gripper convention gives a warning. A learned policy
    also sets `weights_license`.

`reset(ctx)`
:   Clears per-episode state. `ctx.emit(type, payload)` writes your own events into the trace.

`default_execution_steps()`
:   How many actions of a chunk run before the next call, unless the agent overrides it. It must not exceed the
    chunk length `T`.

`sample(observation, seeds, noise_scale)`
:   Returns `(N, T, A)` chunks in the environment's action units. A stochastic policy draws **all** of its
    randomness from the seeds. The agents derive the seeds from the task key, the chunk index and the sample index,
    so a candidate and its parent see the same noise on the same init state (the paired gate depends on this), and
    every episode can be replayed. A deterministic policy ignores the seeds and returns `N` identical chunks.
    `noise_scale` scales the noise; 1.0 is the policy's own level.

!!! warning "Units and bounds"
    Chunks are in the units of the environment's action space; here, normalised joint deltas in [-1, 1]. The
    SafetyShield clips anything outside the bounds and counts larger excursions as safety interventions
    ([safety](../user-guide/safety.md)). On a robot, any modification aborts the episode.

## 3. Declare the contract version, maturity and licence

```python title="src/hylo_my_reacher/__init__.py"
# the contract version this plugin implements and how far it has been verified (hylo.core.plugins);
# set maturity to implemented once it has run end to end on its target, and add `license` to pyproject.toml
META = {"contracts": {"policies": "hylo.policy/v0.1"}, "maturity": "unverified"}
```

The registry reads this declaration before it imports the plugin, and refuses an incompatible contract version:
another major version, or a newer minor version than the core implements. `hylo plugins` lists the declaration, and
the [plugin catalogue](plugin-catalogue.md) is generated from it. Add `license = "..."` to `pyproject.toml` for the
code, and a per-plugin `weights` entry when the policy needs weights under another licence:

```python
META = {"contracts": {"policies": "hylo.policy/v0.1"}, "maturity": "implemented",
        "plugins": {"policies/my-reacher": {"weights": "CC-BY-NC-4.0 (checkpoint my-org/my-reacher-v1)"}}}
```

See [versioning](versioning.md) for what a contract version promises.

## 4. Check it

The generated tests run the policy conformance check and one episode on MuJoCo planar reach:

```bash
uv run pytest plugins/hylo-plugin-my-reacher/tests
```

```text
..                                                                       [100%]
2 passed in 0.19s
```

The same check from the command line, for any registered plugin (or a `module:attr` reference):

```bash
uv run hylo plugin check policy my-reacher
```

```text
policy MyReacherPolicy: PASS
  [  ok] spec is compatible with the environment: my-reacher
  [  ok] sample returns finite (N, T, A) chunks of the action shape: chunk 8 x 2
  [  ok] the same seeds give the same chunks: stochastic (seeded)
  [  ok] default_execution_steps is within the chunk
```

- `--params '{"gain": 0.5}'` passes constructor arguments.
- `--experiment CONFIG` checks against another environment. By default the check uses MuJoCo planar reach when it
  is installed, and the test double otherwise.
- `hylo plugin check` also warns when the declaration, the maturity or the licence is missing.

More in [testing](testing.md).

## 5. Run it with the three agents

The policy never knows which agent runs it. Write an experiment config
([experiments](../user-guide/experiments.md)):

=== "policy"

    ```yaml title="my_reacher.yaml"
    schema_version: hylo.experiment/v0.1
    name: mujoco-reach-my-reacher
    benchmark: {type: mujoco/reach-v0, split: validation}
    env: {type: mujoco.planar_reach}
    agent: {type: policy, params: {policy: {type: my-reacher}}}
    output_dir: runs
    ```

    Runs `default_execution_steps()` actions of each chunk, then asks again. `execution_steps:` overrides it.

=== "temporal_ensemble"

    ```yaml
    agent: {type: temporal_ensemble, params: {policy: {type: my-reacher}, m: 0.01}}
    ```

    ACT's temporal ensembling. It asks for a chunk every step and executes the weighted average of every prediction
    for the current step, with weights `exp(-m * i)` over the predictions, oldest first (`m: 0` is a plain average).

=== "steered"

    ```yaml
    agent:
      type: steered
      params:
        sampler: {type: my-reacher, params: {noise: 0.2}}
        steering: {n_samples: 4, selector: medoid}
    ```

    Draws `n_samples` seeded chunks per decision (at most 8) and executes one. The selector is `first`, `medoid` or
    `gripper_vote_medoid`. Recovery `rules` can fire on stalls. Steering only helps stochastic policies.

```bash
uv run hylo run my_reacher.yaml
```

With `steered` as above, all 20 validation episodes succeed, in 37.7 steps on average (38.2 with `n_samples: 1`).
Agent parameters are in [policies](../user-guide/policies.md#agents-that-run-a-policy) and the
[hylo-agents API](../api/packages/hylo-agents.md).

## 6. A learned policy: weights from a sealed artifact

A learned policy loads its weights in `__init__` from a directory, and that directory is a **sealed artifact**. A
learner writes it from development runs, with a manifest (`artifact.json`) that records its content digest and the
runs it was built from ([learning](../user-guide/learning.md)). The reference policies in hylo-policies show the
pattern: `ReferencePolicy.__init__(path)` reads `policy.json` and `policy.npz` and names itself after the artifact's
digest, and the learners of the same names write and seal those files. To write your own learner, see
[adding a learner](adding-a-learner.md).

Record demonstrations on a development split, train, and look up the artifact's id:

```bash
uv run hylo run bench/examples/configs/mujoco_reach.yaml --split search --output runs/demos \
    --set benchmark.params.protocol=rsi            # 80 expert episodes on the RFC-0002 search split
```

```json title="job.json"
{"learner": "policy.bc", "inputs": ["runs/demos"], "out": "runs/artifacts/my-bc",
 "params": {"chunk": 8, "epochs": 150, "hidden": 128, "execution_steps": 4}}
```

```bash
uv run hylo learn job.json
uv run hylo store ref runs/artifacts/my-bc
```

```text
{"out": "runs/artifacts/my-bc", "kind": "policy_params", "role": "behaviour", "digest": "f028e911e9b90d43",
 "splits": ["search"], "metrics": {"episodes": 80, "samples": 2858, ..., "train_mse": 0.0268}}
artifact:policy.bc@f028e911e9b90d43
```

Reference the artifact by id, not by path. The registry resolves the id to this machine's path when it builds the
policy, after the experiment digest was taken, so the config means the same content on every machine
([store](../user-guide/store.md)):

```yaml
agent:
  type: temporal_ensemble
  params:
    policy: {type: policy.bc, params: {path: "artifact:policy.bc@f028e911"}}
```

The run's `manifest.json` pins what was used:

```json
"artifacts": {"artifact:policy.bc@f028e911": {"id": "artifact:policy.bc@f028e911e9b90d43",
                                              "path": "/.../runs/artifacts/my-bc"}}
```

Your own learned policy does the same: take a `path` parameter, load from it, report the digest in `spec()`
(`components`) and the licence in `weights_license`.

!!! note "Only the gate activates a behaviour artifact"
    A learned policy is a `behaviour` artifact. Running it in an experiment is fine. Deploying it as an improvement
    goes through a campaign's gate, which re-checks the artifact's digest and provenance
    ([campaigns](../user-guide/campaigns.md)).

## 7. Score it and put it on the leaderboard

A protocol fixes the benchmark, split, environment, seeds and timing. `hylo bench run` scores an agent under a
protocol and writes a scorecard ([benchmarking](../benchmarking/index.md)):

```bash
uv run hylo bench run mujoco-reach --name my-reacher \
    --policy '{"type": "policy", "params": {"policy": {"type": "my-reacher"}}}'
```

```text
{
  "scorecard": "./scorecards/mujoco-reach/my-reacher.json",
  "success_mean": 1.0,
  "success_ci95": [0.963, 1.0],
  "n": 100
}
```

`--policy` takes an agent spec as JSON, an experiment config YAML (its agent is used) or a plugin name. `--out`
moves the `runs/` and `scorecards/` roots. Then rank and compare:

```bash
uv run hylo bench leaderboard scorecards
uv run hylo bench compare scorecards/mujoco-reach/my-reacher.json scorecards/mujoco-reach/bc.json   # candidate, baseline
```

```text
### mujoco-reach v1  (`5e0c57ef414a0b21`)

| # | policy | success % | 95% CI | episodes | mean steps |
|---|---|---|---|---|---|
| 1 | my-reacher | 100.0 | 96.3–100.0 | 100 | 37 |
| 2 | flow | 83.0 | 74.5–89.1 | 100 | 56 |
| 3 | bc | 71.0 | 61.5–79.0 | 100 | 68 |
```

Scorecards share a board only when their protocol digests match. `compare` runs a paired one-sided McNemar test
over the same 100 episodes. See [leaderboards](../benchmarking/leaderboard.md).

## 8. Wrapping an external model

Most real policies come with their own stack (torch, JAX, a particular version of `transformers`). Three patterns
keep that stack out of the harness's venv.

=== "In another venv (LeRobot)"

    `hylo-policy-lerobot` registers `LeRobotAgent` both as a policy (`lerobot`) and as an agent. Its `sample()`:

    - builds one batch of `N` copies of the observation;
    - draws the flow-matching noise from the seeds with `torch.Generator().manual_seed(seed)`;
    - returns the unnormalised `(N, T, A)` chunk.

    `spec()` maps cameras and state keys explicitly and reports `repo_id@type` and the weights licence.

    The model runs in its own venv. The `remote` agent starts it as a subprocess, and a runtime from this machine's
    [profile](../configuration/profiles.md) says which venv:

    ```yaml
    agent:
      type: remote
      params:
        ref: lerobot.steered                        # resolved inside the lerobot venv
        runtime: lerobot                            # hylo profile set-runtime lerobot --python ... --env ...
        params: {repo_id: lerobot/smolvla_libero, num_threads: 4, steering: {n_samples: 1, seed_noise: true}}
    ```

    Install your package (with hylo-core and hylo-agents) into that venv as well. The runtime name and the interpreter
    never enter the experiment digest.

=== "Behind a server (openpi)"

    `hylo-policy-openpi` is a client of openpi's own policy server. `OpenPIAgent(url=..., preset="libero")`:

    - maps the observation to openpi's input keys: images resized with padding to 224, the 8-D LIBERO state, the
      instruction as prompt;
    - receives `{"actions": (H, 7)}`;
    - executes the first `execution_steps` of them.

    The model runs on a GPU box in openpi's JAX or PyTorch stack; the kernel, the SafetyShield and the trace stay
    here.

    ```yaml
    agent: {type: openpi, params: {url: "ws://gpu-box:8000", preset: libero, execution_steps: 5}}
    ```

    Its maturity is `unverified`: it has not been run end to end here.

=== "As a Hylo policy server"

    Any agent can be served over WebSocket and used from an experiment or a workcell:

    ```bash
    uv run hylo serve policy --config my_reacher.yaml --port 8001          # serves the config's agent
    ```

    ```yaml
    agent: {type: remote.ws, params: {url: "ws://gpu-box:8001/hylo"}}
    workers: 1                                   # the policy server takes one session at a time
    ```

    See [deployment](../user-guide/deployment.md#policy-server).

Whatever the transport, the policy's `spec()` travels with it, and the compatibility check runs before the first
step.

## Next

- Train the policy inside a campaign and let the gate decide: [campaigns](../user-guide/campaigns.md),
  [adding a learner](adding-a-learner.md).
- Put it on a robot: [deployment](../user-guide/deployment.md).
- Contract details: [extending](../harness/extending.md), [plugin system](../harness/plugin-system.md),
  [hylo-policies API](../api/packages/hylo-policies.md), [`hylo plugin`](../cli/index.md#hylo-plugin).
