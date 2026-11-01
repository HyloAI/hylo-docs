# Experiments

An experiment is one config file that says what to measure: a benchmark split, an environment, an agent, and
optionally safety limits, trace options, timing and a seed. `hylo run` evaluates it and writes a run. Everything else in
Hylo (protocols, campaigns, learners, studio) builds on experiments.

## Run a config

```bash
uv run hylo run bench/examples/configs/mujoco_reach.yaml
uv run hylo run bench/examples/configs/mujoco_reach.yaml --split heldout --set agent.params.kp=0.1 --set workers=8
uv run hylo run bench/examples/configs/mujoco_reach.yaml --output /tmp/runs
```

| Option | Meaning |
|---|---|
| `--split SPLIT` | evaluate another split of the benchmark (default: `benchmark.split` in the config) |
| `--set KEY=VALUE` | dotted-path override, value parsed as YAML; repeatable (`--set benchmark.params.suite=libero_goal`) |
| `--output DIR` | where the run directory goes (default: the config's `output_dir`, `runs`) |

`hylo run` prints one line per finished episode on stderr, then a JSON summary on stdout: `run_dir`, `config_digest`,
`success_mean`, `safety_interventions_mean`, `steps_mean`, `n_episodes` and `n_scored`.

## The config

```yaml
schema_version: hylo.experiment/v0.1
name: mujoco-guarded
benchmark: {type: mujoco/reach-v0, split: validation}      # a "benchmarks" plugin, its params, the split
env: {type: mujoco.planar_reach}                           # an "envs" plugin; remote: {...} to run it elsewhere
agent: {type: baseline.planar_ik, params: {kp: 0.3}}       # an "agents" plugin
safety: {max_delta: 0.5, guards: [{type: norm_limit, params: {max_norm: 1.2}}]}
trace: {record_privileged: true, image_every: 1}
timing: {mode: sync}
seed: 0
workers: 8
output_dir: runs
```

| Key | Default | Measured | Meaning |
|---|---|---|---|
| `name` | required | yes | the experiment's name; starts every run id |
| `benchmark` | required | yes | `{type, params, split}`; split defaults to `validation` |
| `env` | required | yes, except `env.remote` | `{type, params, remote}` |
| `agent` | required | yes, except placement | `{type, params}`; `type` is a plugin name or `module:attr` |
| `safety` | `{}` | yes | extra guards and limits ([safety](safety.md)) |
| `trace` | `record_privileged: true`, `image_every: 1` | yes | store privileged simulator state; keep camera images every N steps (0 = never) |
| `timing` | sync | yes (left out while default) | [sync or realtime execution](#timing-sync-and-realtime) |
| `seed` | 0 | yes | |
| `tags` | `()` | yes | free labels |
| `workers` | 1 | no | parallel episode workers, each with its own environment and agent |
| `output_dir` | `runs` | no | where run directories go |

The full schema is the [experiment config schema](../harness/experiment-schema.md); `hylo schema experiment` prints
it as JSON Schema.

## What is measured: the digest

`ExperimentConfig.measured()` is the part of a config that defines the experiment, and `digest()` hashes it. Left
out are where results go (`output_dir`), parallelism (`workers`) and where components run: `env.remote` and a remote
agent's `runtime`, `python` and `env`. So:

- the same experiment has the same digest on every machine and from every directory;
- two runs with the same digest measured the same thing and can be compared episode by episode;
- moving a component to another venv or process never changes the digest; changing any measured value does.

`timing` is measured, but left out while it is the default, so digests from before realtime timing existed stay
valid. Artifacts are referenced by [store id](store.md) (`artifact:<name>@<digest>`), so the digest pins their
content, not their location.

## Where components run

An environment or an agent can run in another process, with another interpreter. Experiments name a **runtime**
from this machine's [execution profile](../configuration/profiles.md), never a path:

=== "Environment"

    ```yaml
    env:
      type: libero
      remote: {runtime: libero-sim}          # the simulator runs in the libero-sim venv
    ```

    `remote: {}` runs the environment in a subprocess of the current interpreter
    (`bench/examples/configs/mujoco_reach_remote.yaml`).

=== "Agent"

    ```yaml
    agent:
      type: remote
      params:
        ref: lerobot.steered                 # the agent plugin to build in the other process
        runtime: lerobot
        params: {repo_id: lerobot/smolvla_libero, steering: {n_samples: 1, seed_noise: true}}
    ```

`runtime` comes from the profile; explicit `python:` and `env:` entries are still accepted and override the
runtime's for a one-off. None of them enter the digest. Component processes talk msgpack over pipes
(`core.remote`); `remote.ws` components connect over WebSocket instead.

## Timing: sync and realtime

![Sync and realtime episode loops](../assets/diagrams/episode-loop.svg){ .hylo-figure }

*In sync mode the world waits for every chunk. In realtime mode it keeps moving while the next chunk is computed;
actions that went stale are dropped and the hold action fills any gap.*

One loop, `core.kernel.EpisodeRunner`, runs every episode, in benchmarks and on robots. `timing` selects how
policy time relates to robot time:

| Key | Default | Meaning |
|---|---|---|
| `mode` | `sync` | `sync`: the world waits for each policy call. `realtime`: it keeps executing while the next chunk is computed |
| `clock` | `virtual` | realtime only. `virtual`: simulated, deterministic latency. `wall`: a real control loop on a worker thread |
| `control_hz` | the environment's | control rate of the realtime loop |
| `refill_steps` | 2 | request the next chunk when this many queued actions remain |
| `adaptive_refill` | true | ... or earlier, when the queue covers only the recent latency plus one step |
| `latency_s` | measured | virtual clock: a fixed inference latency per chunk instead of the measured one |
| `max_hold_steps` | 100 | watchdog: the episode ends as an error after this many consecutive hold steps |
| `require_reset_confirm` | false | wait for the operator's `reset_done` before an episode starts (workcells) |
| `verdict_timeout_s` | 0.0 | how long to wait for an operator's verdict when the environment cannot judge success |

```bash
uv run hylo run bench/examples/configs/mujoco_reach.yaml --set timing.mode=realtime --set timing.latency_s=0.25
```

A realtime episode records, at its end, how many hold steps it needed (`holds`) and how many chunks were requested
(`chunks`). The protocol `libero-10-heldout-realtime` scores LIBERO-10 this way, with latency fixed at 0.5 s per chunk:
a measured latency depends on the machine and its load, and a protocol must mean the same everywhere.

!!! note "A first reading"
    SmolVLA with steering on LIBERO-10 held-out, 2 tasks x 10 init states: 0.20 success in sync mode, 0.05 in
    realtime mode with about 19 holds per episode. 3 discordant pairs, all favouring sync (one-sided p = 0.125):
    too few episodes for a conclusion, but the gap is measurable
    ([RFC-0005](../rfcs/RFC-0005-architecture-measurement-and-placement.md)).

## Runs and traces

A run directory is named `<name>-<split or label>-<digest>-<6 hex>` and contains:

| File | Content |
|---|---|
| `evallog.json` | run id, benchmark id / version / digest / split, the agent's spec, aggregate results, one sample per episode (task, seed, status, steps, scores, trace path) |
| `manifest.json` | the measured config and its digest, the benchmark, the agent spec, git commit, Python, platform and package versions, and the store ids the config used, pinned to full ids and paths |
| `episodes/<episode_id>.jsonl` | the episode's events; large arrays (camera images, point clouds) are stored once in `blobs/<sha256>.npy` |

Each episode ends with a status:

| Status | When |
|---|---|
| `success` / `failure` | the environment says so (terminated or truncated at the task's `max_steps`) |
| `safety_abort` | a guard aborted the episode (on a real robot, any intervention aborts) |
| `error` | the agent failed, or the realtime watchdog fired |
| `infra_invalid` | the environment faulted or the simulator diverged (`sim_error`); not the policy's fault, not scored as a failure |

Read runs with `hylo trace RUN_DIR [EPISODE_ID]`, in [studio](studio.md), or programmatically with
`hylo.core.trace.TraceStore`.

## Check a config before a long run

```bash
uv run hylo conformance bench/examples/configs/mujoco_reach.yaml            # the environment against its contract
uv run hylo conformance bench/examples/configs/mujoco_reach.yaml --agent    # and the agent (two full episodes)
```

The environment check covers: `spec()` is cheap and typed and survives JSON; `reset` returns an observation matching
the spec and is deterministic in the seed; `step` reports success, termination and truncation separately;
`snapshot` / `restore` reproduces a trajectory (when supported); `close()` works. The agent check runs two full
episodes and expects the same result for the same seed (`--nondeterministic` skips that). `--spec-budget` sets how
many seconds `spec()` may take, which matters for remote environments that start a process.

## Splits

Benchmarks define named splits of init states. MuJoCo reach has `train`, `validation` and `heldout` (standard) or
the four RFC-0002 splits (`benchmark.params.protocol: rsi`); LIBERO suites have `validation` / `heldout` over the
official 50 init states, or the RFC-0002 splits with `protocol: rsi`. Which split each component may read is
fixed: see [campaigns](campaigns.md#splits) and [learning](learning.md#the-split-guard).
