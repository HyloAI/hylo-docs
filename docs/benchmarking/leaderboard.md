# Leaderboards

A leaderboard is every scorecard of one protocol (name, version and digest), ranked by success. There is no server:
scorecards are JSON files, and `wc bench leaderboard` collects them from directories.

## Running policies

`--policy` takes an agent spec as JSON, an experiment config YAML (its agent is used) or a plugin name:

=== "Agent spec"

    ```bash
    uv run wc bench run mujoco-reach --name ik-0.3 \
        --policy '{"type": "baseline.planar_ik", "params": {"kp": 0.3}}'
    ```

=== "Experiment config"

    ```bash
    uv run wc bench run libero-10-heldout --name smolvla-steered \
        --policy bench/examples/configs/libero10_steered.yaml --workers 12
    ```

=== "Plugin name"

    ```bash
    uv run wc bench run mujoco-reach --name random --policy baseline.random
    ```

| Option | Meaning |
|---|---|
| `--name` | the policy's name on the leaderboard (also the scorecard's file name) |
| `--out DIR` | runs go to `DIR/runs`, scorecards to `DIR/scorecards` (default: the current directory) |
| `--workers N` | parallel episodes |
| `--set KEY=VALUE` | execution only: `env.remote.*` (for example another runtime); anything measured is refused |
| `--notes TEXT` | stored in the scorecard |

Artifacts in the agent spec are referenced by [store id](../user-guide/store.md)
(`{"path": "artifact:policy.flow@8d782faf2668f0bd"}`), so a scorecard names the exact weights that were scored.

## Ranking and comparing

```bash
uv run wc bench leaderboard                          # ./scorecards
uv run wc bench leaderboard runs/policies/scorecards --json
uv run wc bench compare scorecards/mujoco-reach/flow-steering-4.json scorecards/mujoco-reach/bc.json
```

The leaderboard prints one Markdown table per protocol digest: rank, policy, success %, 95% interval, scored
episodes, mean steps. `compare` prints the paired result:

```json
{
  "candidate": "flow+steering-4",
  "baseline": "bc",
  "n_pairs": 100,
  "candidate_wins": 18,
  "parent_wins": 5,
  "p_value": 0.005311012268066406
}
```

`candidate_wins` counts episodes only the candidate solved, `parent_wins` those only the baseline solved; the
p-value is the one-sided exact McNemar test on them ([statistics](index.md#statistics)).

## The reference-policy leaderboard

`bench/examples/policies/compare.py` trains one policy per family from the same demonstrations and scores each under
`mujoco-reach`:

1. data from the development splits only (RFC-0002 `search` and `search_val` seeds of the `rsi` protocol): the IK
   controller's runs as demonstrations, random-action runs as exploration data for the world model;
2. one [learner](../user-guide/learning.md) per family (`policy.knn`, `policy.bc`, `policy.flow`, `policy.tokens`)
   and a state world model (`world_model.state`) for MPC, each sealed as an artifact with provenance;
3. each policy run by an agent ([policies](../user-guide/policies.md)): `policy`, ACT-style `temporal_ensemble`,
   or `steered` (4 seeded samples, the medoid executed), scored on the 100 held-out episodes.

```bash
uv run python bench/examples/policies/compare.py --out runs/policies
uv run wc bench leaderboard runs/policies/scorecards
```

![The mujoco-reach leaderboard](../assets/figures/leaderboard-mujoco-reach.png){ .wc-figure }

The recorded result (mujoco-reach v1, protocol digest `5e0c57ef414a0b21`; see [protocols](protocols.md#the-digest)):

| # | Policy | Agent | Success % | 95% CI | Mean steps |
|---|---|---|---|---|---|
| 1 | expert-ik | `baseline.planar_ik` (the demonstrator) | 100.0 | 96.3-100.0 | 36 |
| 2 | mpc-cem | `policy` with `policy.mpc` (CEM in the learned world model) | 86.0 | 77.9-91.5 | 60 |
| 3 | flow+steering-4 | `steered` with `policy.flow` | 84.0 | 75.6-89.9 | 54 |
| 4 | bc+temporal-ensemble | `temporal_ensemble` with `policy.bc` | 83.0 | 74.5-89.1 | 56 |
| 5 | flow | `policy` with `policy.flow` | 83.0 | 74.5-89.1 | 56 |
| 6 | bc | `policy` with `policy.bc` | 71.0 | 61.5-79.0 | 68 |
| 7 | tokens | `policy` with `policy.tokens` | 68.0 | 58.3-76.3 | 74 |
| 8 | knn | `policy` with `policy.knn` | 64.0 | 54.2-72.7 | 76 |

What it shows: on this task, generative chunk policies (flow) and chunk smoothing (temporal ensembling) close most of
the gap between plain behaviour cloning and the demonstrator; planning in a learned model does as well when the
model was trained on expert and random data together. Pairwise, flow + steering beats plain BC with 18 wins against
5 (p = 0.005). It is one small task: the ranking is not a claim about the policy families in general.

Rerunning `compare.py` writes scorecards with the same digest, so they join this board.

## Publishing results

- A scorecard is the unit to share: it carries the protocol digest, the agent spec, the code versions and the
  per-episode outcomes. Keep its run (`run_dir`) in the [store](../user-guide/store.md) so the traces stay
  reachable.
- Report held-out protocols for anything a campaign improved (`libero-10-heldout`, not `libero-10`).
- Compare pairwise on the same digest; do not compare means across digests.
