# Action memory

Action memory lets a frozen flow policy draw on its own past successes. The bank stores segments from episodes that
the simulator verified as successful: what the policy saw (as a retrieval key) and the action chunk it produced
then. At each decision the agent retrieves similar segments and starts the policy's sampling from them instead of
from pure noise. The policy still integrates its own velocity field from the current observation, so memory biases
the action; it never replays one.

## Configuration

First build an [action bank](#building-a-bank) from successful development runs and register its artifact id.
For the example below, prepare the [LIBERO and LeRobot runtimes](../../getting-started/optional-environments.md#libero-and-lerobot-policies)
and checkpoint. This is an `agent` fragment for an experiment; replace the example artifact id with your bank.

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

[Retrieval settings](../../reference/memory.md#retrieval-settings) lists defaults and all tuning options.

Calibrate retrieval and sampling strength on development data. Action memory can reduce success when retrieved
motions do not suit the current scene; compare with the same policy without memory before adopting it.

## Behaviour { #design }

Build a bank from successful development episodes and load it frozen for evaluation. To incorporate new
development experience, save a new artifact. Each decision retrieves similar segments and uses them as a
sampling prior while the policy still responds to the current observation.

Close, consistent neighbours give a stronger bias. Distant or disagreeing neighbours give a weaker one;
without a usable match, the policy samples as it would without memory. The policy computes retrieval keys in
its own forward pass, so retrieval needs no extra model call.

## Retrieval { #how-a-decision-works }

![The policy's own key retrieves the most similar verified segments from the bank; outliers are dropped, the rest form a prior and a start time, and flow sampling starts from the prior while the policy still sees the current observation. With nothing usable, the policy runs unchanged.](../../assets/diagrams/action-steer-light.svg){ .hylo-diagram .only-light }
![The policy's own key retrieves the most similar verified segments from the bank; outliers are dropped, the rest form a prior and a start time, and flow sampling starts from the prior while the policy still sees the current observation. With nothing usable, the policy runs unchanged.](../../assets/diagrams/action-steer-dark.svg){ .hylo-diagram .only-dark }

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

??? info "The arithmetic"

    For the kept segments `i` with similarity `s_i` and action chunk `a_i`:

    ```text
    w_i        = softmax(s_i / temperature)
    prior      = Σ w_i · a_i                          motion dimensions
    vote       = Σ w_i · sign(g_i)                    gripper dimension g
    prior_g    = sign(vote) · mean |g_i|              nearest segment's g if |vote| < 0.2
    s̄          = clip((Σ w_i · s_i − sim_floor) / (1 − sim_floor), 0, 1)
    confidence = s̄ · exp(−dispersion / dispersion_scale)
    t0         = t0_max − (t0_max − t0_min) · confidence
    x_t0       = (1 − t0) · prior + t0 · noise        then the policy integrates from t0 to 0
    ```

    `dispersion` is the mean pairwise DTW distance between the kept segments.

Each decision emits `memory.retrieval` with the matches, confidence and sampling start time. Inspect these
fields when a retrieved prior changes the result.

The chosen chunk's provenance also records `t0` and the number of segments kept, and the agent spec records the
bank: `bank(<digest>,n=<segments>,k=10,floor=0.95,t0=[0.1,0.7])`.

## Build a bank { #building-a-bank }

A bank is a folder with `bank.npz` (keys, chunks, lengths) and `bank.json` (schema, digest, and each segment's
task, step, progress and source episode); no pickle. It holds at most `capacity` segments (50,000 by default),
oldest first out. Keys are stored L2-normalised as float16, so similarity is a dot product. Loading checks the
content against the recorded digest.

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
`memory_build --store noise`. Compare it with the base policy under the same evaluation protocol.

## Constraints { #limits }

- The sampler must implement the prior-sampling protocol (`sample(..., prior_fn=...)` and `retrieval_key`).
  LeRobot flow policies do; the reference `policy.flow` does not on its own.
- The gripper dimension is always aggregated by vote; there is no option for robots without a gripper.
- Banks for policies other than LeRobot are built in scripts, not with a command.

<span id="what-it-achieved"></span>

## Next

- [Recorded results](../../developer-guide/validation/guide-results.md#action-memory): measurements, conditions and reproduction commands.
- [Use memory](../using-memory.md): match a memory to its consuming agent.
- [Memory](index.md): lifetime and evaluation boundaries.
