# Action memory

Action memory lets a frozen flow policy draw on its own past successes. The bank stores segments from episodes that
the simulator verified as successful: what the policy saw (as a retrieval key) and the action chunk it produced
then. At each decision the agent retrieves similar segments and starts the policy's sampling from them instead of
from pure noise. The policy still integrates its own velocity field from the current observation, so memory biases
the action; it never replays one.

## How a decision works

1. The policy computes a retrieval key inside its own forward pass (for SmolVLA, its pooled visual tokens), so
   retrieval costs no extra encoder call.
2. The bank returns the `k` most similar segments by cosine similarity, from the same task by default, and drops
   those below `sim_floor`.
3. Segments whose motion disagrees with the rest (dynamic time warping over the first steps, more than `dtw_mad`
   median absolute deviations from the median) are dropped.
4. The rest are combined into a prior: a similarity-weighted mean for motion, a weighted vote for the gripper (the
   nearest segment's gripper when the vote is split).
5. Confidence, from the similarity and from how much the segments agree, sets where sampling starts: `t0` between
   `t0_min` (confident, a strong bias) and `t0_max` (weak). With nothing usable, `t0 = 1`: exactly the unchanged
   policy.

Each decision emits `memory.retrieval` with the candidates found and kept, the mean similarity, the dispersion, the
confidence, `t0` and the source episodes of the top hits.

## Configuration

`memory.steered` wraps a sampler that implements the prior-sampling protocol. For LeRobot flow policies such as
SmolVLA, use `lerobot.memory_steered`, which runs the policy in its own runtime:

```yaml
agent:
  type: remote
  params:
    ref: lerobot.memory_steered
    runtime: lerobot
    params:
      repo_id: lerobot/smolvla_libero
      steering: {n_samples: 1, seed_noise: true}
      memory: {type: action_bank, params: {path: "artifact:l10-search-v1@40a84dd1afab4a5c"}}
      memory_steer: {k: 10, same_task: true, sim_floor: 0.95, t0_min: 0.1, t0_max: 0.7}
```

The full LIBERO-10 config is `bench/examples/configs/libero10_memory.yaml`.

| Setting | Default | Meaning |
|---|---|---|
| `k` | 10 | segments retrieved |
| `same_task` | true | retrieve only from the same task |
| `sim_floor` | 0.9 | minimum cosine similarity; calibrate it against the bank's build report |
| `temperature` | 0.05 | softmax temperature over similarity when weighting segments |
| `dtw_mad` | 2.0 | how far from the others a segment may be before it is dropped |
| `compare_steps` | the execution steps | prefix length compared between segments |
| `t0_min`, `t0_max` | 0.1, 0.7 | the range of start times; smaller is a stronger bias |
| `fixed_t0` | none | ignore confidence and always start here (for ablations) |
| `dispersion_scale` | 0.5 | disagreement at which confidence roughly halves |
| `gripper_dim` | −1 | the action dimension treated as the gripper |

SmolVLA's velocity field pulls hard towards its own action: on LIBERO, a prior almost one standard deviation away
moves the result about 40% of the way at `t0 = 0.1` and hardly at all from `t0 = 0.4`. Useful guidance therefore
lives at small `t0`.

## Building a bank

A bank is a folder with `bank.npz` (keys, chunks, lengths) and `bank.json` (schema, digest, and each segment's
task, step, progress and source episode); no pickle. It holds at most `capacity` segments (50,000 by default),
oldest first out. Loading checks the content against the recorded digest.

For LeRobot policies, build from the runs of development splits, with the policy's own keys:

```bash
envs/libero/.venv/bin/python -m hylo.policies.lerobot.memory_build --runs runs/<search runs> \
    --splits search --out runs/memory/l10-search-v1 --repo-id lerobot/smolvla_libero
uv run hylo store ref runs/memory/l10-search-v1        # an artifact id for configs
```

Only chunks from simulator-verified successful episodes are stored, and replays of identical episodes are stored
once. The builder seals the folder as an `action_memory` artifact and writes `build_report.json` with
nearest-neighbour similarity statistics: set `sim_floor` from those. The same builder runs as a learner job
(`lerobot.action_memory`) through `hylo learn`.

For other policies, collect segments from successful episodes and add them to a bank in a script; the MuJoCo memory
examples do this (`examples/memory/_common.py: segments_from_run`), including a bank that each session extends and
saves for the next.

## Noise memory

`lerobot.noise_steered` is a variant that remembers the initial noise that led to successful chunks instead of the
chunks themselves, and mixes it with fresh noise over the full flow. Build its bank with
`memory_build --store noise`. On unseen LIBERO start states it made no difference (0.55 and 0.54 against 0.54).

## What it achieved

| Setting | Result |
|---|---|
| MuJoCo planar reach, revisited scenes | 0.75 → 0.81 (p = 0.29) |
| MuJoCo planar reach, new scenes | 0.69 → 0.75 (p = 0.24) |
| Six sessions on the same workcell, each extending the bank | +4, +5, +7, +11, +1 points in sessions 2–6; pooled +5.6 |
| LIBERO-10, SmolVLA, bank from other start states | 0.54 → 0.46 |
| LIBERO-10, same scenes, fixed `t0` 0.2 | 0.54 → 0.62 (p = 0.10) |

On MuJoCo the key is the policy's 8-dimensional state, so a neighbour from another scene is still informative. On
LIBERO the key is pooled image features, which carry no information about the outcome on an unseen layout. Looser
retrieval (`k` 10, floor 0.95) with a well-tuned policy made results worse on MuJoCo in a development run. Treat
action memory as an experiment to measure on your task, not a default.

```bash
uv run python examples/memory/03_action_memory_scene_recall.py    # in the harness repository
uv run python examples/memory/05_memory_across_sessions.py
```

## Limits

- The sampler must implement the prior-sampling protocol (`sample(..., prior_fn=...)` and `retrieval_key`).
  LeRobot flow policies do; the reference `policy.flow` does not on its own.
- The gripper dimension is always aggregated by vote; there is no option for robots without a gripper.
- Banks for policies other than LeRobot are built in scripts, not with a command.
