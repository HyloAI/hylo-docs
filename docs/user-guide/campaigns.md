# Campaigns

A campaign improves an experiment's agent one tested change at a time. Each cycle asks a **generator** for candidate
config changes and promotes at most one, only if a paired test against the current version (the *parent*) on init
states not used for selection confirms it. Promotion is automatic by default. Set `approval: manual` for anything
that will run on hardware.

![One campaign cycle: parent, diagnose, generate, screen, gate, approve, promote; the archive feeds past results to the generator](../assets/diagrams/improvement-loop-light.svg){ .hylo-diagram .only-light }
![One campaign cycle: parent, diagnose, generate, screen, gate, approve, promote; the archive feeds past results to the generator](../assets/diagrams/improvement-loop-dark.svg){ .hylo-diagram .only-dark }

*One cycle. The promoted candidate is the next cycle's parent.*

## Run { #run-a-campaign }

Commands on this page run from `bench/`. This is the quickstart's campaign:

```yaml title="examples/evolve/mujoco_reach_gain.yaml"
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

- `proposer`: the generator.
- `protocol`: the gate settings.
- `benchmark.params.protocol: rsi`: the campaign's [split scheme](#splits).

```bash
cd bench
uv run hylo evolve run examples/evolve/mujoco_reach_gain.yaml
uv run hylo evolve status examples/evolve/mujoco_reach_gain.yaml
```

The `experiment` path is resolved against the campaign file. `out_dir` is resolved against the working directory, so
run every `hylo evolve` command for a campaign from `bench/`. That also keeps the campaign inside the store. If you
ran the quickstart, `status` shows its result and `run` continues the same campaign from its state file, up to
`cycles`. `--set KEY=VALUE` overrides a key of the campaign config.

## Results

`hylo evolve status` prints the campaign state, the active version and its lineage, the combined patch, any pending
approval, and the archive size. `stopped` says why the campaign ended: `all cycles done`,
`no promotion in N consecutive cycles`, `budget exhausted` or `waiting for manual approval`.

```text
runs/evolve/mujoco-reach-gain/
  evolve_config.json        the config as run
  campaign_state.json       cycles done, history with held-out results, why it stopped
  archive.jsonl             every candidate: patch, hypothesis, stages reached, verdict, evidence
  registry/                 the promotion ledger (ledger.jsonl) and the active candidate (ACTIVE)
  active.json               the active version as an agent spec, which deployment reads
  cycle-01/                 the cycle's runs and cycle_report.json
  pending_approval.json     only while a candidate waits for manual approval
```

Archive verdicts: `rejected` (stage 0 or 1), `archived` (not sent to the gate), `gated_fail`, `gate_passed`
(confirmed, not promoted, for example while waiting for approval) and `promoted`. Ids and paths in the archive and
ledger protect the runs and artifacts they name from deletion ([store](store.md)).

## Candidate evaluation { #the-cascade-and-the-gate }

The parent runs on `search`, and its failures are sorted into buckets. The generator returns up to `max_candidates`
config patches, each with a hypothesis. The cascade (stages 0 to 2) screens them, and the gate (stage 3) confirms the
best against the parent:

![The cascade: stage 0 checks without runs, stage 1 an early check on search_val, stage 2 a screen on all of search_val, stage 3 the gate on the gate split, then a report on heldout.](../assets/diagrams/cascade-light.svg){ .hylo-diagram .only-light }
![The cascade: stage 0 checks without runs, stage 1 an early check on search_val, stage 2 a screen on all of search_val, stage 3 the gate on the gate split, then a report on heldout.](../assets/diagrams/cascade-dark.svg){ .hylo-diagram .only-dark }

| Stage | Runs on | What happens |
|---|---|---|
| 0 | nothing yet | stage-0 checks: reject patches that touch a protected section, are invalid or already archived, or reference (by store id, or by a path inside a sealed artifact) an artifact that was modified, built from gate or held-out runs, or (for behaviour artifacts) is of unknown provenance; a path to a directory without `artifact.json` is not checked; optional world-model pre-screen |
| 1 | the first `stage1_pairs` pairs of `search_val` | reject when the parent leads by `stage1_max_deficit` wins or more |
| 2 | all of `search_val` | keep candidates that win more pairs than they lose; the best `gate_top_k` go to the gate |
| 3 | `gate`, then `gate_r1`, ... | paired test against the parent (McNemar by default), Holm-corrected across candidates, with sequential looks, futility stopping, and regression and safety vetoes |
| report | `heldout` | the first candidate that passed and the parent, paired; recorded with `used_for_selection: false` |

Then, with `approval: auto`, the candidate becomes the active version and the next cycle's parent. With
`approval: manual` the campaign stops and waits. Candidates and parent share seeds and policy noise, so every
comparison is paired.

Candidates may not change the [protected settings](safety.md#safety-in-campaigns). Timing and agent code are
not protected.

## Splits

A campaign needs four disjoint splits, which the `rsi` split scheme provides.

![The four splits: search for diagnosis and generators, search_val for screening and learners, gate for the gate, heldout for the report to the approver.](../assets/diagrams/splits-light.svg){ .hylo-diagram .only-light }
![The four splits: search for diagnosis and generators, search_val for screening and learners, gate for the gate, heldout for the report to the approver.](../assets/diagrams/splits-dark.svg){ .hylo-diagram .only-dark }

| Split | MuJoCo reach seeds | LIBERO init states | Used for |
|---|---|---|---|
| `search` | 30000–30039 | 0–19 | diagnosis and learning |
| `search_val` | 30040–30059 | 20–29 | selection (stages 1 and 2) |
| `gate` | 30060–30079 | 30–39 | confirmation (stage 3) |
| `heldout` | 30080–30099 | 40–49 | the report |

LIBERO's boundaries are `rsi_bounds` (default `[20, 30, 40]`). On MuJoCo reach every seed runs on both tasks.

### Split access

| Split | Runs read by | Results visible to |
|---|---|---|
| `search` | diagnosis; generators, through the diagnosis; learners | generators |
| `search_val` | the cascade; learners; the `learn` generator, which trains on the cycle's `search` and `search_val` runs by default | generators, through the archive |
| `gate`, `gate_r1`, ... | the gate | generators, through the archive |
| `heldout` | the report only: the cascade and the gate never read it | the approver, in `pending_approval.json`; generators, through the archive entries of promoted candidates |

The gate reuses its init states every cycle, so after cycle 1 generators have seen gate results on them. The
`experience` generator and lesson books use these results on purpose.

### Held-out sets

| Benchmark | Held-out scored by the protocol | Held-out a campaign reports on |
|---|---|---|
| MuJoCo reach | `mujoco-reach`: the standard `heldout` split, seeds 20000–20049 | `rsi` `heldout`: seeds 30080–30099 |
| LIBERO-10 | `libero-10-heldout`: init states 40–49 | `rsi` `heldout`: init states 40–49, the same states |

### Gate looks

With `gate_looks: K` the gate tests up to K times, stopping early once a candidate passes or no longer leads. Each
further look runs a replicate of the gate split (`gate_r1`, ...). On LIBERO it reuses the gate init states with new
policy noise. On MuJoCo reach it uses new seeds (`gate_r1` is 30160–30179). Set the same value twice:
`benchmark.params.gate_looks` makes the benchmark provide the replicates, and the `gate_looks` gate setting makes the
gate use them.

## Generators

Generators are `generators` plugins:

| Generator | Proposes |
|---|---|
| `rule.gain` | scaled values of one numeric config path |
| `rule.steering` | steering rules (resample, back off) from failure buckets such as stalls and regrasps |
| `llm.steering` | steering patches from a local LLM that reads failure traces (hylo-proposer-llm, through Ollama) |
| `learn` | trains an artifact with a learner each cycle and patches the config to use it; `{artifact}` in the patch template becomes its store id when the artifact lands inside the store, else its path |
| `critic.chunk_value` | trains a chunk critic and proposes critic steering |
| `experience` | wraps another generator and gives it lessons and skills built from the archive |
| `selftrain.expert_iteration` | fine-tunes the policy on its own successful episodes |

How far each is tested: [plugin catalogue](../developer-guide/plugin-catalogue.md). To write your own, run
`hylo plugin new generator NAME` and see
[adding a generator](../developer-guide/adding-a-generator.md).

## Program candidates { #program-development-and-code-candidates }

Developing a first program and comparing a revision with a baseline have different evidence requirements.
Use [Program skills](research-and-skills.md) for development and independent evaluation; use a campaign to
compare a proposed change with the current version and promote it through the gate.

The `research.llm` generator develops code on `search` cases, optionally starting from a `code.program` parent.
It freezes a qualifying submission as a program artifact and proposes a `code` candidate. The same cascade,
paired gate, held-out report and approval path apply. A program that succeeded during development has not yet
passed these checks. Follow [Program skills](research-and-skills.md) for the development and reuse steps.

For experimental phase-guided repair and note recall, see [Program repair](../developer-guide/program-repair.md).

| Proposer | Changes | Training |
| --- | --- | --- |
| `rule.gain`, `rule.steering`, `llm.steering` | Runtime parameters or steering | None |
| `experience` | Supplies lessons and skill evidence to an inner proposer | Depends on the inner proposer |
| `research.llm` | Executable program | None |
| `harness.program` | Phase-guided program and repair notes | None |
| `critic.chunk_value` | Action-chunk ranking around a frozen policy | Critic training |
| `learn`, `selftrain.expert_iteration` | Learner artifacts or policy checkpoint | Explicit training path |

Select one proposer through `proposer.type`; additional packages provide the model-based
options. These choices do not automatically combine into one algorithm. See the
[campaign API](../api/packages/hylo-evolve.md) for implementation details.

## Version control { #approve-roll-back-shadow }

<video src="../../assets/videos/studio-campaigns.mp4" poster="../../assets/videos/studio-campaigns.jpg" controls muted playsinline preload="none" width="100%" aria-label="The Studio's self-improvement pages: a candidate's cascade, an approval, the rollback form and the A/B arena"></video>

*In the Studio: each candidate's path through the cascade, a campaign whose candidates all failed the gate, a candidate approved by hand, the rollback form, and the parent and promoted version paired on held-out states.*

```bash
uv run hylo evolve approve runs/evolve/my-campaign          # recorded with your user name
uv run hylo evolve run runs/evolve/my-campaign              # continue after approval
uv run hylo evolve rollback runs/evolve/my-campaign --reason "regression seen on the robot"
uv run hylo evolve shadow runs/evolve/my-campaign --candidate cand-9147236d7d
uv run hylo evolve status runs/evolve/my-campaign --publish  # also rewrite active.json
```

The target is the campaign config or the campaign directory.

- With `approval: manual`, a candidate that passes the gate waits in `pending_approval.json` and the campaign stops.
  `hylo evolve approve` promotes it. Run `hylo evolve run` again to continue.
- `rollback` restores the parent of the active version. The ledger records who did it and why (`--reason`).
- `shadow` runs the active version with the candidate riding along: it sees every observation but never acts. The
  report says how often and how far it would have acted differently. Run it before trying a candidate on a robot.
  The candidate may change only `agent.*` keys.

## LIBERO campaigns { #libero-10-campaigns }

`examples/evolve/` has three campaigns on frozen SmolVLA in LIBERO-10: `libero10_steering.yaml` (rule-based
steering), `libero10_llm.yaml` (an LLM proposes steering) and `libero10_selftrain.yaml` (expert iteration, manual
approval). They need `envs/libero/setup.sh`. `libero10_steering.yaml` and `libero10_llm.yaml` set `budget_s: 28800`
(8 hours), `libero10_selftrain.yaml` 43200 (12 hours): no new cycle starts after that. It is a limit, not an
estimate.

<span id="reference"></span>
<span id="design"></span>

## Next

- [Campaign configuration](../configuration/campaigns.md): campaign and gate settings, defaults and limits.

- [Execution model](../developer-guide/execution-model.md#campaigns): runtime and implementation details.

- Serve the promoted version on a robot: [deployment](deployment.md). A policy server started with
  `hylo serve policy --campaign DIR` follows `active.json`.
- Approve or roll back from the browser: [studio](studio.md).
