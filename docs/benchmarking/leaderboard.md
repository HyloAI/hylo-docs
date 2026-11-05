# Run and compare evaluations

<span id="leaderboards"></span>

A leaderboard is every scorecard of one evaluation protocol (name, version and digest), ranked by success. There is
no server: scorecards are JSON files, and `hylo bench leaderboard` collects them from directories.

## Running policies

Commands on this page run from `bench/`. `--policy` takes an agent spec, in one of three forms: JSON, an experiment
config YAML (its agent is used), or a plugin name.

=== "Agent spec"

    ```bash
    uv run hylo bench run mujoco-reach --name ik-0.3 \
        --policy '{"type": "baseline.planar_ik", "params": {"kp": 0.3}}'
    ```

=== "Experiment config"

    ```bash
    uv run hylo bench run libero-10-heldout --name smolvla-steered \
        --policy examples/configs/libero10_steered.yaml --workers 12
    ```

=== "Plugin name"

    ```bash
    uv run hylo bench run mujoco-reach --name random --policy baseline.random
    ```

| Option | Meaning |
|---|---|
| `--name` | the agent's name on the leaderboard; the scorecard file is the name with other characters than `A-Za-z0-9_.-` replaced by `-`, and a name that maps to an existing file overwrites it |
| `--out DIR` | runs go to `DIR/runs`, scorecards to `DIR/scorecards` (default: the working directory) |
| `--workers N` | parallel episodes |
| `--set KEY=VALUE` | execution settings only ([which keys](protocols.md#the-digest)) |
| `--notes TEXT` | stored in the scorecard |

Use digest-pinned [store ids](../user-guide/store.md) for artifacts so the scorecard names the exact weights.

## Ranking and comparing

```bash
uv run hylo bench leaderboard                          # ./scorecards
uv run hylo bench leaderboard runs/policies/scorecards --json
uv run hylo bench compare scorecards/mujoco-reach/flow-steering-4.json scorecards/mujoco-reach/bc.json
```

The leaderboard prints one Markdown table per protocol digest: rank, agent name, success %, 95% interval, scored
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

`candidate_wins` and `parent_wins` count episodes only the candidate or only the baseline solved (the key name is
shared with campaigns). The test is explained in [compare two scorecards](index.md#statistics).

## The reference-policy leaderboard

Published rankings now live in [Research → Benchmarks](https://hyloai.github.io/research/benchmarks/).
The [MuJoCo reach benchmark](https://hyloai.github.io/research/benchmarks/mujoco-reach/)
separates the recorded protocol versions and links their source records.

To generate your own reference-policy scorecards, run from `bench/`:

```bash
uv run python examples/policies/compare.py --out runs/policies
uv run hylo bench leaderboard runs/policies/scorecards
```

Compare only scorecards with the same protocol name, version and digest. A published historical ranking
may use a different digest from your current installation.

## Publishing results

- A scorecard is the unit to share.
- `run_dir` is a path on your machine. To share the traces too, keep the run in the
  [store](../user-guide/store.md) and copy it to the other side with `hylo store push`.
- Report held-out protocols for anything a campaign improved (`libero-10-heldout`, not `libero-10`).

## Next

- Train artifacts from runs: [learning](../user-guide/learning.md).
- Improve an agent with a [campaign](../user-guide/campaigns.md).
