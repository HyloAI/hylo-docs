# RFC-0005: What is measured, where it runs, and one episode loop

| | |
|---|---|
| Status | Parts 1 and 3 implemented (2026-10-31); parts 2 and 4 implemented, part 5 partly (2026-11-01); part 6 proposed |
| Scope | hylo-harness (hylo-core, hylo-eval, hylo-agents), hylo-bench, hylo-serve, deployments |
| Builds on | RFC-0001 (contracts), RFC-0002 (gate), RFC-0004 (artifacts), design/repository-structure.md |

## Motivation

Six structural problems found in the code on 2026-10-31, ordered by how much they threaten the trust in a result:

1. **An experiment's identity included where it ran.** The config digest excluded only `output_dir` and `workers`;
   `env.remote.python`, `LD_LIBRARY_PATH`, `HF_HOME` were hashed, and eight shipped configs and protocols held
   machine paths, relative to the working directory. The same experiment on another machine was a different
   experiment, and LIBERO commands only worked from one directory.
2. **Runs and artifacts have no identity beyond a path.** Artifacts are referenced as `runs/judges/l10-trace-v2`;
   provenance lists run directory names. Deleting old runs left dangling provenance with nothing to stop it, and
   deployment runs recorded on a robot reach the workstation only by copying.
3. **Two episode loops.** Evaluation ran core's `EpisodeRunner`; deployment ran serve's `RealtimeEpisodeRunner`
   (which imported a private kernel helper). What the gate approved in simulation was not the loop the robot ran.
4. **Plugins carry no contract version or metadata** (licence, maturity), which the repository split needs.
5. **hylo-agents mixes roles**: decision-making agents, instruments (judges, critic, world model), reasoners, test
   doubles.
6. **No job layer**: campaigns run in a foreground process; studio jobs are bare subprocesses.

## Part 1: experiments vs execution profiles (implemented)

- `ExperimentConfig.measured()` is what the digest covers. Left out: `output_dir`, `workers`, and a remote agent's
  `runtime` / `python` / `env`; `env.remote` is hashed as absent (`null`), the way a local environment always was.
  `timing` is measured but left out while it is the default (sync). So digests of local experiments and protocols
  did not change. Protocol digests treat `env.remote` the same way.
- **Execution profiles** (`core.profile`, `hylo.profile/v0.1`): one file per machine (`$HYLO_PROFILE`, else
  `~/.config/hylo/profile.yaml`) maps runtime names to an interpreter and environment variables. Configs
  name a runtime (`remote: {runtime: libero-sim}`, agent params `runtime: lerobot`); explicit `python` / `env` still
  work and override it. `hylo profile show | set-runtime | remove-runtime`; bench's `envs/libero/setup.sh` registers
  `libero-sim` and `lerobot` with absolute paths.
- Result: every shipped LIBERO config, protocol and workcell template is free of machine paths and runs from any
  directory; the same experiment has the same digest on the workstation, the GPU box and the robot computer.
- Consequence: digests of experiments that had `env.remote` (all LIBERO ones) changed once. (A first version left
  `env.remote` out of the hashed dictionary altogether, which changed every digest, local ones included, and split
  the mujoco-reach scorecards onto two boards; fixed on 2026-11-01. Runs recorded between 2026-10-31 and that fix
  carry the intermediate digests.) Runs keep the digest
  they were recorded with; comparisons by digest across this change need the run's manifest config.
- Artifact and memory paths inside agent params were still working-directory relative; part 2 replaced them with
  store ids.

## Part 3: one episode loop (implemented)

- `core.kernel.EpisodeRunner` is the only loop. `Timing` (in core; part of what is measured) selects:
  - `sync` (default): the world waits for each policy call, a chunk runs `execution_steps` actions; event payloads
    are as before;
  - `realtime`: refill at `refill_steps` (adaptive to recent latency), aligned merge that drops the actions that
    went stale while the chunk was computed, hold action when the queue is empty, watchdog after `max_hold_steps`,
    `virtual` clock (deterministic, latency measured or fixed by `latency_s`) or `wall` clock (worker thread,
    control-rate loop).
- The operator channel (stop, latched e-stop, reset confirmation, verdicts) and the hold action moved to core.
  Both modes share the SafetyShield, error classification (agent errors, environment faults, safety aborts,
  `sim_error`), compatibility checking at bind time (new for the workcell) and the trace events.
- serve's `RealtimeEpisodeRunner` is now a thin wrapper (workcell config and result shape); the workcell and the
  benchmark run the same code.
- `ExperimentConfig.timing` and `Protocol.timing`: a benchmark can score what a robot would run. New protocol
  `libero-10-heldout-realtime` (virtual clock, latency fixed at 0.5 s per chunk). A measured latency is not used in a
  protocol: it depends on the machine and its load, and a protocol digest must mean the same everywhere.
- First reading (SmolVLA + steering, LIBERO-10 held-out, 2 tasks x 10 init states): sync 0.20 success, realtime
  0.05 with 19 holds per episode; 3 discordant pairs, all favouring sync (one-sided p = 0.125). Too few episodes
  for a conclusion; enough to show the gap is measurable and probably real.

## Part 2: a run and artifact store (implemented)

- `core.store` (`hylo.store/v0.1`). A store is a directory tree on one machine; the profile says which
  (`hylo store init PATH` sets `store:`; else `$HYLO_STORE`, else `./runs`). Every run (an `evallog.json`) and sealed
  artifact (an `artifact.json`) under it has an id: `run:<run_id>` (run ids already end in a random suffix, so no
  digest is needed) and `artifact:<name>@<digest>` (a digest prefix of at least 8 hex characters works; a bare
  `artifact:<name>` only when exactly one artifact has that name).
- Configs reference artifacts by id. The registry resolves ids to this machine's paths when it builds a component
  (`Registry.build`), after the experiment digest was taken over the ids: the same config means the same content
  on every machine, and a plugin still receives a path. The run manifest pins every id it used (full id and the
  path it resolved to). Learner job inputs accept run and artifact ids. The gate resolves ids, checks that the
  content still has the referenced digest, and refuses behaviour artifacts whose provenance is unknown.
  Generators that seal artifacts (`learn`, `critic.chunk_value`) put ids into candidate patches.
- The index (`<root>/.hylo-store/index.json`) is a cache: a miss rebuilds it by walking the tree (108 entries under
  bench/runs in 0.2 s). It records what each artifact was built from (its provenance) and what each campaign's
  archive and promotion ledger names: ids, paths inside an entry, or run ids as path components (paths recorded
  before a move).
- Referential integrity: `hylo store rm ID` refuses while anything refers to the entry; `--force --reason` deletes
  anyway. Either way a tombstone (`tombstones.jsonl`) records what was removed, why, and what referred to it, and a
  later lookup of the id reports the removal instead of "not found".
- Sync: `hylo store push|pull PATH|HOST:PATH [ID ...] [--with-sources] [--dry-run]`, rsync over ssh, with the other
  side listed by its own `hylo store ls --json`. Sealed artifacts are never re-copied or overwritten; the same path
  holding a different entry is a conflict and nothing is copied; runs and mutable artifacts are brought up to date.
- `hylo store adopt DIR --kind --role [--source RUN ...]` seals a directory built before manifests existed, with the
  sources the caller states, or "unknown provenance" when none are known (recorded, and refused by the gate for
  behaviour artifacts). Adopted here: `memory/l10-search-v1` (its build report lists its two search runs) and
  `critics/l10-v1` (no record of its training runs: unknown provenance).
- Shipped configs now name ids (`libero10_critic`, `libero10_memory`, `libero10_noise`,
  `mujoco_policy_flow_steered`; studio's default judge). Checked: LIBERO + SmolVLA with the noise-steering memory
  referenced by id, run from an unrelated directory: success, the id pinned in the run manifest.
- Not yet: sync with another machine is tested between two local stores only (no ssh host here); the catalog and
  studio show ids but still walk directories for their listings; workcell `output_dir` and campaign `out_dir` are
  still relative to the working directory (register the directory they write to as the store).

## Part 4: contract versions and plugin metadata (implemented)

- `core.plugins`: every plugin group is a versioned contract (`CONTRACTS`: `hylo.env/v0.1`, `hylo.agent/v0.1`,
  `hylo.policy/v0.1`, ... one per group). Compatible means the same contract and major version, and a minor version
  not newer than the core's.
- Each distribution declares, in one `META` dictionary under the `hylo.meta` entry-point group (a module
  with no heavy imports, so listing never loads a plugin): the contract version per group, a default maturity, and
  per-plugin overrides (maturity, weights licence, notes). The code licence is the distribution's `license`.
  Maturity is `implemented` (run end to end on its target, with recorded runs), `unverified`, `needs-hardware`, or
  `test-double` (every `testing.*` plugin).
- The registry checks the declaration before importing an entry point and refuses an incompatible one
  (`IncompatiblePlugin`); an undeclared plugin still loads and is listed as undeclared. `module:attr` references
  are not checked (no distribution to ask).
- `hylo plugins [--all] [--json]` lists contract, maturity, licence, weights and notes; `hylo plugin check` warns when a
  declaration, maturity or licence is missing; `hylo plugin new` generates the declaration (maturity `unverified`).
- All 16 plugin distributions declare v0.1. Maturity was set from the recorded runs (which plugin types appear in
  run manifests and campaign archives): 59 implemented, 23 unverified, 6 test doubles (e.g. unverified: openpi, the
  generic memory / noise steering agents, the experience, learn, critic and self-training generators, lesson books
  and skill libraries, the VLM judge), 1 needs-hardware (`lerobot.robot`: it has run with the simulated arm only).
  Weights: LeRobot checkpoints per model card (PaliGemma-based pi0 / pi0.5 under the Gemma Terms of Use), openpi
  checkpoints under the Gemma Terms of Use, LLM plugins under the served model's licence.
- Not yet: studio does not show maturity and licence next to the components it runs.

## Part 5: contracts in hylo-core, one plugin group per role (partly implemented, 2026-11-01)

Done:

- Every plugin group's contract is defined in hylo-core (`core.plugins.CONTRACT_OBJECTS`, checked by a test):
  `core.benchmark` (Benchmark and the split functions, moved from hylo-eval), `core.scoring` (Score, Scorer,
  PairedComparison, GateTest), `core.improvement` (Candidate, StageResult, ArchiveEntry, Proposer) and
  `core.reasoning` (Reasoner, Chooser, Planner, and a new Reflector contract). The old modules re-export the
  names, so existing imports keep working. A plugin of any group now depends on hylo-core alone: hylo-reasoner-llm,
  hylo-env-mujoco and hylo-env-libero dropped their dependencies on hylo-agents and hylo-eval.
- `reasoners` was three interfaces under one version; it is now four groups, each with its own contract version:
  `reasoners` (hylo.reasoner), `choosers` (hylo.chooser), `planners` (hylo.planner), `reflectors` (hylo.reflector).
  Plugin names did not change.
- One generator contract: the old `CandidateGenerator` and `GainRuleGenerator` are gone. The single-cycle loop on
  standard splits (`improvement_cycle`, used by the demos) takes the same `Proposer` as campaigns; `rule.gain`
  gained `adaptive` (scale up on timeouts, down on oscillation or safety aborts).

Not done:

- Splitting the hylo-agents package itself: hylo-agents (decision-making), hylo-instruments (judges, value models,
  world models), hylo-reasoners (rule-based reasoners). With the contracts in core this is a packaging change only;
  it matters once the robot computer should install decision-making alone.

## Part 6: a job layer (proposed)

- `core.jobs` contract: a job is a `hylo` command with resources (CPU threads, GPU, runtime); a local executor with a
  queue, concurrency limits, resume and logs; studio and campaigns submit jobs instead of starting processes.
- Later executors: a GPU box over SSH, a cluster scheduler.

## Order

1 and 3 first (done): they decide whether a measurement can be trusted and whether it transfers to the robot.
2 and 4 next (done): required before the repositories are split and before more than one machine shares results.
5 and 6 when the robot computer and the GPU box are in regular use.
