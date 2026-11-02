# Quickstart

This page takes one example through the four steps: run an experiment, measure a policy, improve it with a
campaign, and deploy the promoted version to a policy server. The example is MuJoCo planar reach: a two-link arm
moves its fingertip to a target. You need the [workspace](installation.md) with the harness and bench; the optional
Studio step at the end also needs studio and its built web UI. Nothing here needs LIBERO, a GPU or downloaded
weights, and every step takes under a minute on a CPU.

This path starts from an existing controller. To develop a task strategy with robot tools or a code-writing model,
follow [Developing task strategies](../user-guide/developing-strategies.md). That path has separate rendering,
robot-asset and model requirements; the CPU example here remains a way to check the shared execution stack first.

Run every command from `bench/`, so runs land in `bench/runs`, the store you registered during installation:

```bash
cd bench
```

## 1. Run an experiment

An experiment config names a benchmark and its split, an environment and an agent:

```yaml title="bench/examples/configs/mujoco_reach.yaml"
schema_version: hylo.experiment/v0.1
name: mujoco-reach
benchmark: {type: mujoco/reach-v0, split: validation}
env: {type: mujoco.planar_reach}
agent: {type: baseline.planar_ik, params: {kp: 0.3}}
output_dir: runs
```

```bash
uv run hylo run examples/configs/mujoco_reach.yaml
```

Each episode is printed as it ends (`[20] mujoco/planar_reach_random seed=10009 success (32 steps)`), then the run's
metrics:

```json
{
  "run_dir": "runs/mujoco-reach-validation-2342f91d706e83e9-eaf39f",
  "config_digest": "2342f91d706e83e9",
  "success_mean": 1.0,
  "safety_interventions_mean": 0.0,
  "steps_mean": 35.25,
  "n_episodes": 20,
  "n_scored": 20
}
```

`config_digest` is a hash of what was measured. Changing the gain changes it. Changing the number of workers does
not, because where and how fast episodes run is not part of the measurement:

```bash
uv run hylo run examples/configs/mujoco_reach.yaml --set agent.params.kp=0.02   # "config_digest": "167e9648dec50b70"
uv run hylo run examples/configs/mujoco_reach.yaml --set workers=8              # "config_digest": "2342f91d706e83e9"
```

The weak gain also halves the success rate (`"success_mean": 0.5`). Step 3 starts from that gain.

### Read the traces

Use the `run_dir` printed above to read a run. Its last six characters are random, so yours differs
([what a run contains](../user-guide/experiments.md#runs-and-traces)):

```bash
uv run hylo trace <run_dir>                  # the metrics, then every episode id
uv run hylo trace <run_dir> <episode_id>     # one episode, for example mujoco.planar_reach_fixed-s10000-2749d014
```

For one episode, `hylo trace` counts the events and prints the episode's end record. The trace holds every action
the agent proposed (`agent.chunk`), what the safety shield decided (`safety.review`) and what was executed
(`action`):

```text
Counter({'observation': 31, 'agent.chunk': 30, 'safety.review': 30, 'action': 30, 'step.result': 30,
         'privileged.state': 30, 'episode.start': 1, 'episode.end': 1})
{
  "status": "success",
  "success": true,
  "steps": 30,
  "termination_reason": "terminated",
  "safety_interventions": 0
}
```

## 2. Score a policy under a protocol

An evaluation protocol fixes everything except the agent being scored. `mujoco-reach` is 100 episodes: a fixed and
a random target, 50 held-out seeds each.

```bash
uv run hylo bench list
uv run hylo bench run mujoco-reach --name ik-0.3 \
    --policy '{"type": "baseline.planar_ik", "params": {"kp": 0.3}}'
```

The run ends with the scorecard's path and its success rate:

```json
{
  "scorecard": "scorecards/mujoco-reach/ik-0.3.json",
  "success_mean": 1.0,
  "success_ci95": [0.963, 1.0],
  "n": 100
}
```

Score a second policy, then rank and compare the two:

```bash
uv run hylo bench run mujoco-reach --name ik-0.05 \
    --policy '{"type": "baseline.planar_ik", "params": {"kp": 0.05}}'
uv run hylo bench leaderboard        # every scorecard under scorecards/, per protocol, best first
uv run hylo bench compare scorecards/mujoco-reach/ik-0.05.json scorecards/mujoco-reach/ik-0.3.json
```

```text
### mujoco-reach v1  (`a76c7037efb84660`)

| # | policy | success % | 95% CI | episodes | mean steps |
|---|---|---|---|---|---|
| 1 | ik-0.05 | 100.0 | 96.3–100.0 | 100 | 68 |
| 2 | ik-0.3 | 100.0 | 96.3–100.0 | 100 | 36 |
```

Both policies succeed on all 100 episodes, so they tie, and ties are listed by name. `ik-0.3` needs about half the
steps. `compare` pairs the scorecards episode by episode for a one-sided exact McNemar test. Neither policy wins an
episode the other loses, so p = 1.0:

```json
{"candidate": "ik-0.05", "baseline": "ik-0.3", "n_pairs": 100, "candidate_wins": 0, "parent_wins": 0, "p_value": 1.0}
```

More in [benchmarking](../benchmarking/index.md).

## 3. Improve a policy with a campaign

A campaign tries changes to a config and keeps one only if it beats the current version on episodes it was not
chosen on. Here the IK controller starts with the weak gain from step 1 (`kp: 0.02`), and a rule-based generator
proposes 2× and 4× the gain:

```yaml title="bench/examples/evolve/mujoco_reach_gain.yaml"
schema_version: hylo.evolve/v0.1
name: mujoco-reach-gain
experiment: ../configs/mujoco_reach.yaml
experiment_overrides: {agent.params.kp: 0.02, workers: 16, benchmark.params: {protocol: rsi, gate_looks: 2}}
proposer: {type: rule.gain, params: {path: agent.params.kp, factors: [2.0, 4.0]}}
protocol: {alpha: 0.05, gate_looks: 2, stage1_pairs: 20}
cycles: 3
stop_after_no_progress: 1
approval: auto
out_dir: runs/evolve/mujoco-reach-gain
```

The generator is configured under `proposer`, and the top-level `protocol:` block holds the gate settings, not an
evaluation protocol. `benchmark.params: {protocol: rsi}` gives the campaign its four
[splits](../user-guide/campaigns.md#splits): `search`, `search_val`, `gate` and `heldout`.

```bash
uv run hylo evolve run examples/evolve/mujoco_reach_gain.yaml
```

```text
[cycle 1] parent = base config
[cycle 1] parent-search                      search     success=0.450 n=80
[cycle 1] parent-search_val                  search_val success=0.400 n=40
[cycle 1] cand-8786c03a32-search_val         search_val success=1.000 n=40
[cycle 1] cand-dca7bbd596-search_val         search_val success=1.000 n=40
[cycle 1] parent-gate                        gate       success=0.350 n=40
[cycle 1] cand-8786c03a32-gate               gate       success=1.000 n=40
[cycle 1] cand-8786c03a32-heldout            heldout    success=1.000 n=40
[cycle 1] parent-heldout                     heldout    success=0.400 n=40
[cycle 1] done: promoted=cand-8786c03a32 heldout={...}
[cycle 2] parent = cand-8786c03a32
...
[cycle 2] done: promoted=None heldout=null
{
  "cycles_done": 2,
  "stopped": "no promotion in 1 consecutive cycles",
  "out_dir": "runs/evolve/mujoco-reach-gain"
}
```

Timings are left out above. Cycle 1 promotes a candidate: on held-out episodes, success rises from 0.40 to 1.00 in
this run (24 wins, no losses, 40 pairs). Cycle 2 finds nothing better, so the campaign stops
(`stop_after_no_progress: 1`). Candidate ids differ from run to run. Check the result:

```bash
uv run hylo evolve status examples/evolve/mujoco_reach_gain.yaml
```

Among other fields, the status shows the active version and the change it makes to the base config:

```json
{
  "active": "cand-8786c03a32",
  "effective_patch": {"agent.params.kp": 0.04},
  "pending_approval": null
}
```

The campaign writes its active version to `runs/evolve/mujoco-reach-gain/active.json`, which step 4 serves.
`hylo evolve rollback` would undo the promotion ([campaigns](../user-guide/campaigns.md)); keep it for now.

## 4. Serve the promoted version

A policy server serves a campaign's active version and follows later promotions and rollbacks. It needs no
hardware:

```bash
uv run hylo serve policy --campaign runs/evolve/mujoco-reach-gain      # port 8000 by default; Ctrl+C stops it
```

```text
[policy] ws://127.0.0.1:8000/wc and /openpi (version cand-8786c03a32)
```

A workcell next to a robot connects to this server; see [Deployment](../user-guide/deployment.md).

## 5. Look at it in Studio

Studio shows the runs, episodes and campaigns from the steps above. Build its web UI once
([installation](installation.md#studio-web-ui)), then start it from `bench/`:

```bash
uv run hylo playground          # http://127.0.0.1:8765
```

It shows `runs/` and `examples/` of the directory it starts in. Open **Runs & replays** to step through an
episode, and **Self-improvement** to follow the campaign ([Studio](../user-guide/studio.md)).

## Next

- [Concepts](concepts.md): the vocabulary used everywhere else.
- [Campaigns](../user-guide/campaigns.md): splits, the gate, approval and rollback.
- [Deployment](../user-guide/deployment.md): run the promoted version on a workcell.
- [Examples](examples.md): every shipped config, including LIBERO-10 with SmolVLA.
