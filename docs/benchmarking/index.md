# Benchmarking

To compare agents fairly, score each under the same **evaluation protocol**: a frozen, versioned experiment that
fixes everything except the agent being scored (the agent usually wraps a policy). Each run writes a **scorecard**.
The scorecards of one protocol form a **leaderboard**, and any two can be compared episode by episode.

The agent is passed as `--policy`. Despite the flag's name, it takes an agent spec.

## Scoring

Commands on this page run from `bench/`.

```bash
cd bench
uv run hylo bench list                     # built-in protocols, their versions and digests
uv run hylo bench show mujoco-reach        # one protocol, with its digest
```

Score a baseline and a candidate under the same protocol:

```bash
uv run hylo bench run mujoco-reach --name ik-0.02 \
    --policy '{"type": "baseline.planar_ik", "params": {"kp": 0.02}}'
uv run hylo bench run mujoco-reach --name ik-0.3 \
    --policy '{"type": "baseline.planar_ik", "params": {"kp": 0.3}}'
```

```json title="Output of the second run"
{
  "scorecard": "scorecards/mujoco-reach/ik-0.3.json",
  "success_mean": 1.0,
  "success_ci95": [0.963, 1.0],
  "n": 100
}
```

`hylo bench run` writes the run to `OUT/runs/` and the scorecard to `OUT/scorecards/<protocol>/<name>.json`.
`--out` sets `OUT`; the default is the working directory. All options are in the
[CLI reference](../cli/index.md#hylo-bench).

## Statistics

```bash
uv run hylo bench compare scorecards/mujoco-reach/ik-0.3.json scorecards/mujoco-reach/ik-0.02.json
```

```json title="Output"
{
  "candidate": "ik-0.3",
  "baseline": "ik-0.02",
  "n_pairs": 100,
  "candidate_wins": 59,
  "parent_wins": 0,
  "p_value": 1.734723475976807e-18
}
```

`hylo bench compare CANDIDATE BASELINE` pairs the episodes both scorecards share by task and seed (`n_pairs`; an
episode either side abstained on is dropped). A one-sided exact McNemar test on the pairs where exactly one agent
succeeded (`candidate_wins`, `parent_wins`) asks whether the candidate wins more often. Two agents whose
intervals overlap can still differ clearly this way
([example](leaderboard.md#the-reference-policy-leaderboard)). Scorecards with different protocol digests are refused.

The success interval is the 95% Wilson score interval, which stays inside [0, 1]: 100 successes in 100 episodes give
[96.3%, 100%].

## Scorecards

A scorecard is a self-contained JSON file:

| Field | Content |
|---|---|
| `protocol`, `protocol_version`, `protocol_digest` | what was measured |
| `policy`, `agent` | the name given with `--name`, and the agent spec that ran |
| `metrics` | `success_mean`, `steps_mean`, `safety_interventions_mean`, `n_episodes`, `n_scored`, ... |
| `success_ci95` | the 95% Wilson score interval on the success rate |
| `per_task` | success and episode count per task |
| `episodes` | per-episode success keyed `task#seed`, which `compare` pairs on |
| `run_dir`, `config_digest`, `code` | the run it came from on this machine, its config digest, and the git commit and package versions that ran |
| `notes`, `created_at` | free text (`--notes`), and when it was written |

## Protocols vs experiments

An [experiment config](../user-guide/experiments.md) says what to run: benchmark and split, environment, agent,
safety, trace, timing. A protocol is an experiment with the agent left out:

| | Experiment config | Evaluation protocol |
|---|---|---|
| Agent | part of the config | the only free input (`--policy`) |
| Who writes it | anyone, for any run | built in, or your own YAML; a change is a new version |
| Identity | config digest | protocol name, version and digest |
| Result | a run (`evallog.json`, traces) | a run plus a scorecard |
| Comparable with | runs with the same config digest and code versions | scorecards with the same protocol digest |

The protocol digest does not cover package versions. Each scorecard records them under `code`
([the digest](protocols.md#the-digest)).

## Next

- The built-in [protocols](protocols.md), and how to write your own.
- Put several agents on a [leaderboard](leaderboard.md).
- Improve an agent with a [campaign](../user-guide/campaigns.md), whose gate uses the same paired test by default.
