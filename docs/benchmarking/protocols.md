# Protocols

A protocol (`wc.protocol/v0.1`, `worldcurrent.bench.protocol.Protocol`) is everything about an evaluation except the
policy. Protocols ship with wc-bench as YAML files (`packages/wc-bench/src/worldcurrent/bench/protocols/`) and are
named by their file name; any YAML file with the same fields works too (`wc bench run path/to/protocol.yaml ...`).

## Fields

| Field | Measured | Meaning |
|---|---|---|
| `schema_version` | yes | `wc.protocol/v0.1` |
| `name`, `version` | yes | the identity shown on leaderboards; change `version` whenever anything measured changes |
| `benchmark` | yes | `{type, split, params}`: the benchmark plugin, the split that is scored, its parameters |
| `env` | yes, except `env.remote` | `{type, params}` of the environment plugin; `remote` says where the simulator runs |
| `safety` | yes | SafetyShield config: `max_delta`, `guards: [{type, params}]` ([safety](../user-guide/safety.md)) |
| `trace` | yes | `record_privileged`, `image_every` |
| `timing` | yes, unless default | `sync` (default) or `realtime` with its clock, latency and refill settings |
| `seed` | yes | base seed of the run |
| `description` | no | what the protocol is for |
| `workers` | no | parallel episodes: how fast, not what |
| `requires` | no | what must be installed or set up, for humans |

## The digest

`wc bench show NAME` prints the protocol and its digest: sha256 (first 16 hex characters) over the measured
fields. Left out:

- `description`, `workers`, `requires`;
- `env.remote`: where the simulator runs (a runtime name, an interpreter, environment variables) is placement, not
  measurement ([RFC-0005](../rfcs/RFC-0005-architecture-measurement-and-placement.md));
- `timing` while it is the default (sync).

A scorecard records the digest it was measured under. Leaderboards group scorecards by (name, version, digest),
and `wc bench compare` refuses scorecards of different digests: a protocol edited without a new version would
otherwise mix incomparable numbers.

`wc bench run --set` accepts only what does not change the digest: `env.remote.*`, `workers` and `output_dir`.
Anything else is refused, because the scorecard would no longer belong to the protocol.

!!! note "Where the simulator runs is hashed as local"
    Since RFC-0005 `env.remote` is hashed as if absent (`null`), the way a local environment always was. Local
    protocols kept their digests (mujoco-reach v1 is `5e0c57ef414a0b21`, as before); protocols that ran the
    simulator in another process (the LIBERO ones) changed once. Scorecards keep the digest they were written
    with, so a LIBERO scorecard from before that change sits on its own board.

## Built-in protocols

| Protocol | Benchmark and split | Episodes | Timing | Requires |
|---|---|---|---|---|
| `mujoco-reach` | `mujoco/reach-v0`, held-out seeds (50 per task) | 100: a fixed and a random target | sync | wc-env-mujoco |
| `libero-10` | LIBERO-10, all 50 stored init states per task | 500 | sync | wc-env-libero, `envs/libero/setup.sh` |
| `libero-10-heldout` | LIBERO-10, RFC-0002 held-out init states 40-49 | 100 | sync | as above |
| `libero-10-heldout-realtime` | as `libero-10-heldout` | 100 | realtime, virtual clock, 0.5 s per chunk | as above |

```bash
uv run wc bench list
```

**mujoco-reach.** A planar two-link arm reaching a fixed and a random target in MuJoCo, 50 held-out seeds each. Fast
(a few seconds per policy on CPU) and deterministic; the reference-policy [leaderboard](leaderboard.md) uses it.

**libero-10.** The official LIBERO-10 protocol (long-horizon tasks): all 50 stored init states of each of the 10
tasks. These include the init states that improvement campaigns develop on (RFC-0002: search 0-19, search_val
20-29, gate 30-39). For a policy that a campaign improved on LIBERO-10, report `libero-10-heldout` instead.

**libero-10-heldout.** Only the held-out init states 40-49, which no learner and no gate ever reads
([splits](../user-guide/campaigns.md)): a fair test for policies improved by campaigns.

**libero-10-heldout-realtime.** The same 100 episodes as a robot would run them. The simulated arm keeps executing
while the policy computes its next chunk; actions that went stale during inference are dropped and gaps are held
([the episode loop](../user-guide/deployment.md#the-realtime-runner)). Latency is fixed at 0.5 s per chunk (a GPU
policy server), not measured: a measured latency depends on the machine and its load, and a protocol must mean the
same everywhere. The gap to `libero-10-heldout` is what deployment costs a policy.

```yaml
timing: {mode: realtime, clock: virtual, latency_s: 0.5, refill_steps: 2}
```

!!! info "A first reading"
    SmolVLA with steering, 2 LIBERO-10 tasks x 10 held-out init states: 0.20 success in sync timing, 0.05 in
    realtime timing (19 held steps per episode); 3 discordant pairs, all favouring sync (one-sided p = 0.125). Too
    few episodes for a conclusion, enough to show that the gap is measurable.

The LIBERO protocols run the simulator in its own venv through the `libero-sim` runtime of the
[execution profile](../configuration/profiles.md); `bench/envs/libero/setup.sh` builds the venv and registers it.

## Writing a protocol

Copy a built-in protocol and change what you measure:

```yaml
schema_version: wc.protocol/v0.1
name: mujoco-table
version: "1"
description: |
  MuJoCo table reach: held-out seeds of every table task.
benchmark: {type: mujoco/table-v0, split: heldout}
env: {type: mujoco.table_reach}
safety: {max_delta: 0.5}                     # as examples/configs/mujoco_table_memory.yaml
trace: {record_privileged: true, image_every: 0}
workers: 8
requires: [wc-env-mujoco]
```

```bash
uv run wc bench show protocols/mujoco-table.yaml          # check the digest
uv run wc bench run protocols/mujoco-table.yaml --policy composable.object_reach --name object-reach
```

- Use a split that no campaign learns from or gates on (`heldout`) if improved policies will be scored.
- Keep `workers` out of your reasoning about results: it changes speed, not the digest.
- Bump `version` for any change to a measured field, and say what changed in `description`.

To ship a protocol with wc-bench, add the YAML file to `packages/wc-bench/src/worldcurrent/bench/protocols/`.

## The test protocol

`bench/packages/wc-bench/tests/testing-reach.yaml` runs the [test double](../developer-guide/contributing.md#test-doubles)
(`testing.point_reach`). It exists for wc-bench's own unit tests and is not shipped: test doubles never produce
published numbers.
