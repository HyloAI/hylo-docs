# RFC-0004: Learning Pipeline and Derived Artifacts

- Status: Implemented (A1-A3, W1-W4); video world models and RL fine-tuning wait for a GPU
- Date: 2026-10-31
- Builds on: RFC-0001 (contracts, layering), RFC-0002 (physical RSI protocol, L3/L4 units), RFC-0003 (experience memory)
- Evidence: `research/projects/learning-from-video.md`, `research/experiments/2026-10-31-success-judges-libero10.md`, `research/experiments/2026-10-31-rfc0004-w1-w4.md`

## 1. Goal

Make "learning" one pipeline instead of one script per method, so that learning from the agent's own rollouts,
from demonstrations, from video, and learning world models all plug into the same contracts and the same gate:

```
data source -> (labeler) -> learner -> sealed artifact -> candidate (config patch) -> RSI gate -> promotion
```

Before this RFC the system already had five learners with their own export, split guard and output format: chunk
critic (L3), expert iteration (L4), LeRobot export, action-memory builder (RFC-0003 M1), lesson reflector (M4).

## 2. Principle: the trace store is the only source of truth

Everything the system learns is a **derived artifact**: a directory built from traces (or an external source) by a
builder, sealed with an `artifact.json` manifest that records its kind, role, content digest and provenance (which
runs and splits it read, which builder and parameters, which other artifacts it depends on). Memory and learning are
the same thing architecturally; they differ only in the builder (retrieval index, LLM curation, gradient descent).

## 3. Three roles, three trust paths

| Role | Examples | Used by | Trusted through |
|---|---|---|---|
| **behaviour**: changes what the robot does | action memory, critic / value model used to select chunks, noise policy, policy weights, skills | the runtime agent stack | the RSI gate only |
| **instrument**: measures or labels | success judge, progress model used for labelling, world model | data labelling; pre-screening candidates | calibration against ground truth (`CalibrationReport`) |
| **proposal**: changes what is proposed | lessons, the skill index shown to proposers | proposers | outcome votes (RFC-0003 M4) |

Hard rules:
1. An instrument never decides a gate verdict. In simulation the gate scores with ground truth; a world model may
   only decide which candidates are worth real evaluation budget.
2. An instrument is never calibrated on, and never labels, the data it was built from (`calibrate_judge` excludes
   the runs in its provenance).
3. One model may play two roles (a value model selecting chunks and labelling progress); each use is approved on its
   own trust path.

## 4. Split integrity, enforced twice

- **At build time**: one guard for every builder (`core.artifact.check_splits`, `development_runs`). Development
  splits (`search`, `search_val`) and external sources may be read; `gate*` and `heldout*` never. `write_manifest`
  refuses to seal an artifact whose provenance lists a forbidden split.
- **At gate time**: stage 0 of `run_cycle` resolves every filesystem path in a candidate patch to its artifact
  (`referenced_artifacts`), re-verifies the digest and the provenance, and rejects the candidate before any rollout
  if the artifact was modified after sealing or saw gate / held-out data. Verified artifacts are recorded in the
  archive entry's evidence (kind, role, digest, splits).

Known, accepted bias: an artifact built from `search_val` biases stage-2 selection (which uses `search_val`); the
gate split stays clean. The splits are recorded in evidence so the bias is visible.

## 5. Contracts and modules

```
hylo-core   core/artifact.py    SourceRef, Provenance, ArtifactManifest; dir_digest, write_manifest, verify,
                              referenced_artifacts; check_splits, development_runs (the one split guard)
          core/learning.py    TrainJob, Learner, DataSource, Labeler; run_job (in-process), launch (any interpreter:
                              `python -m hylo.learn.jobs job.json`, in hylo-learn), resumable by job digest
          core/instrument.py  SuccessJudge, ValueModel, WorldModel protocols; Judgement; CalibrationReport,
                              calibration_report, calibrate_judge
          testing/learners.py SummaryLearner (dependency-free learner for tests and conformance)
hylo-evolve evolve/learning.py  LearningProposer ("learn"): run a learner job on the cycle's development runs, check
                              manifest metrics (`require`), fill a patch template ({artifact}, {metrics.x})
hylo-agents critic_train.py     CriticLearner ("critic.chunk_value"), seals a value_model
hylo-agents judges.py           TraceJudgeLearner ("judge.trace" learner) + TraceSuccessJudge ("judge.trace" instrument)
hylo-reasoner-llm judge.py      VLMSuccessJudge ("judge.vlm"): zero-shot VLM on the final frames + instruction
hylo-cli              hylo learn JOB.json, hylo calibrate ..., hylo artifact PATH
hylo-policy-lerobot             export.py (seals a dataset), selftrain.py ExpertIterationLearner ("lerobot.expert_iteration",
                              seals policy_weights), memory_build.py ActionMemoryLearner ("lerobot.action_memory")
```

New plugin groups: `learners`, `instruments`, `datasources`. Orchestration lives in hylo-core rather than a separate
package because a job must be runnable in every venv (the policy venv has hylo-core but not hylo-evolve); the proposer
lives in hylo-evolve. Heavy learners (video labelers, world models) will go into their own adapter
(`hylo-learn-video`), never into core.

Candidates stay `config_patch`: an artifact is referenced by path (`agent.params.critic.path: <artifact dir>`), so
no new candidate kind and no change to the protected scope are needed.

## 6. Runtime composition (unchanged, extended)

```
SkillAgent -> SubgoalAgent -> MemorySteeredAgent | CriticSteeredAgent -> PriorSampler (+ noise policy, A4)
          -> VLA policy -> SafetyShield -> Env
```
Every artifact a run uses is recorded in its trace (agent spec components) and in the archive (stage-0 evidence).

## 7. Plan

| Step | Content | Hardware | Status |
|---|---|---|---|
| A1 | core contracts, split guard, sealing, gate stage-0 provenance check, LearningProposer, plugin groups | CPU | implemented |
| A2 | existing builders sealed and exposed as learners (critic, expert iteration, export, action memory) | CPU | implemented |
| A3 | instruments: success / progress judges (zero-shot VLM `judge.vlm` vs trained on traces `judge.trace`), calibrated on LIBERO ground truth (`hylo calibrate`); completes RFC-0003 M5 | CPU | implemented |
| A4 | noise-space learner: done as W3 (offline retrieval form; the online RL form needs thousands of episodes) | CPU | see W3 |
| W1 | external data: `core/datasource.py` (ExternalEpisode, `ingest` into split external:<name> with origin and licence, `contamination_report` against gate / held-out init states), `instrument.label_run` (calibrated judges only, high-precision positives only); sources `lerobot.dataset`, `video.frames`, `video.files` (adapter hylo-data-video); `hylo ingest / label / contamination` | CPU | implemented |
| W2 | world model: `agents/world_model.py` (StateWorldModel ensemble + task-complete head, learner `world_model.state`, `WorldModelEnvironment`); `protocol.prescreen` (off by default; rejects predicted regressions before any rollout; never used by the gate); synthetic runs excluded from development data | CPU (state); GPU for video models | implemented (state) |
| W3 | noise-space steering (A4, offline DSRL counterpart): exact seed-noise recovery, `memory_build --store noise`, `NoiseSteeredAgent` mixing retrieved noise variance-preservingly | CPU | implemented; null result on unseen init states (0.55 / 0.54 vs 0.54) |
| W4 | shadow mode: `agents/shadow.py` (`ShadowAgent`, divergence events, background evaluation), `hylo evolve shadow` | CPU / robot | implemented |
| later | latent-action / hand-pose labelers (actions from video), video world models, RL fine-tuning (GRPO / RECAP), real-robot adapters | GPU, data approval, hardware | - |

Lessons and skill libraries (mutable stores) are not sealed yet; they keep their own content digests
(`snapshot()`), and frozen copies used in evaluation are referenced by digest in the agent spec.

## 8. Open questions

1. Whether to require a manifest for every path in a candidate patch (strict mode) once all builders seal.
2. Retention: sealed artifacts accumulate (weights are ~1 GB); a garbage collector must keep everything referenced
   by the registry or the archive.
3. Calibration targets per use: labelling memory needs high precision; pre-screening needs rank correlation.
