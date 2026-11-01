# Learning

Everything Hylo learns comes from recorded runs and becomes a sealed **artifact**: a directory with an
`artifact.json` manifest (`hylo.artifact/v0.1`) that records what it is, a content digest, and its provenance (the
builder, its parameters, and the runs and data it was built from). The trace store is the single source of truth;
artifacts are derived from it ([RFC-0004](../rfcs/RFC-0004-learning-pipeline.md)).

## Artifact kinds and roles

| Role | Kinds | Changes | Trusted when |
|---|---|---|---|
| `behaviour` | `action_memory`, `value_model`, `noise_policy`, `policy_weights`, `policy_params` | what the robot does | the gate promotes a candidate that uses it |
| `instrument` | `success_judge`, `progress_model`, `world_model` | what is measured or labelled | it is calibrated against ground truth |
| `proposal` | `lesson_book`, `skill_library` | only what generators propose | outcome votes curate it |
| `data` | `dataset` | what learners can read | its labels come from the source or a calibrated judge |

The gate's verdict never makes an instrument trustworthy, and calibration never activates a behaviour artifact:
the two trust paths are separate.

## The split guard

![RFC-0002 splits](../assets/diagrams/splits.svg){ .hylo-figure }

*Learners read only the development splits. Gate and held-out runs are refused when a job starts, refused again when
an artifact is sealed, and checked again by the gate for every artifact a candidate references.*

- `TrainJob.splits` defaults to `("search", "search_val")`; asking for a `gate*` or `heldout*` split raises
  `SplitLeak` before anything is read.
- Learners collect inputs with `development_runs()`, which skips other splits when scanning a directory and refuses
  them when given an explicit list.
- `write_manifest` refuses to seal an artifact with a gate or held-out source.
- Runs produced inside a learned model (world-model pre-screening) are never treated as training data unless a job
  asks for the `synthetic` split.
- Ingested external data has split `external:<name>` and is read only when a job includes `external`.

## Run a learner job

A job names a `learners` plugin, its inputs, where to seal the artifact, and parameters:

```json title="bench/examples/policies/jobs/flow.json"
{"learner": "policy.flow", "inputs": ["runs/policies/demos"], "out": "runs/policies/artifacts/flow",
 "params": {"chunk": 8, "epochs": 300, "integration_steps": 10}}
```

```bash
cd bench
uv run hylo learn examples/policies/jobs/flow.json
uv run hylo learn job.json --python bench/envs/libero/.venv/bin/python     # in another venv
```

| Field | Meaning |
|---|---|
| `learner` | a `learners` plugin name or `module:attr` |
| `inputs` | run directories, directories to search for runs, or store ids (`run:<id>`) |
| `out` | the artifact directory this job seals |
| `splits` | splits it may read (default `search`, `search_val`) |
| `params` | the learner's parameters |

A job is resumable: if `out` already holds a verified artifact sealed by the same job (the job digest covers
everything but `out`), it is not run again. `--python` runs the learner with another interpreter
(`python -m hylo.learn.jobs`), for learners whose dependencies live in a runtime's venv.

Learners that ship (see the [plugin catalogue](../developer-guide/plugin-catalogue.md) for maturity):

| Learner | Builds |
|---|---|
| `policy.knn`, `policy.bc`, `policy.flow`, `policy.tokens` | reference policies ([policies](policies.md)) |
| `world_model.state` | a state world model (for `policy.mpc` and world-model pre-screening) |
| `critic.chunk_value` | a chunk critic for critic steering |
| `judge.trace` | a success judge from traces |
| `lerobot.action_memory`, `lerobot.noise_prior` | action memories and noise priors for LeRobot steering |
| `lerobot.expert_iteration` | fine-tuned LeRobot weights from successful episodes (unverified: smoke run only) |

Online learners (policy search that acts while it learns, for example the plugins repository's `examples.cem`) use
the same jobs; see [extending](../harness/extending.md).

## Inspect and reference an artifact

```bash
uv run hylo artifact runs/policies/artifacts/flow     # verify (digest intact, no gate / held-out sources), print the manifest
uv run hylo store ref runs/policies/artifacts/flow    # its store id: artifact:policy.flow@<digest>
```

Configs reference artifacts by store id, never by path:

```yaml
sampler: {type: policy.flow, params: {path: "artifact:policy.flow@8d782faf2668f0bd"}}
```

See [store](store.md) for ids, deletion protection and moving artifacts between machines.

## Success judges and calibration

A success judge (`instruments` group) labels an episode from its trace when no simulator says whether it succeeded:
on a robot, or for external data. A judge is trusted only after calibration on runs whose outcome is known.

```bash
uv run hylo learn judge-job.json                                       # learner judge.trace -> a success_judge artifact
uv run hylo calibrate --judge '{"type": "judge.trace", "params": {"path": "artifact:l10-trace-v2@54a1efadf00d34d8"}}' \
    --runs RUN_DIR [RUN_DIR ...] --artifact JUDGE_DIR      # JUDGE_DIR: the judge's artifact directory
```

Calibration reads development splits by default (`--splits`) and compares the judge's scores with the simulator's
outcomes. It reports AUC, Brier score, expected calibration error, and the lowest threshold that reaches the target
precision (`--target-precision`, default 0.95) with the recall there. The judge is `ready` to label when enough
episodes were scored (at least 50), the target precision is reachable, and the recall at that threshold is at least 0.3. With
`--artifact`, the judge's own training runs are excluded and the report is stored in the judge's manifest.

| Judge (LIBERO-10) | AUC | Precision / recall at the 0.95-precision threshold | Ready to label |
|---|---|---|---|
| `judge.trace` | 0.93 | 0.95 / 0.55 (threshold 0.994) | yes |
| `judge.vlm` | 0.61 | 1.00 / 0.13 (threshold 0.95) | no |

*From this project's experiment record
([success judges on LIBERO-10](../research/experiments/2026-10-31-success-judges-libero10.md)).*

## External data

Demonstrations, videos and other robots' logs enter as ordinary runs with split `external:<name>`, sealed as `data`
artifacts that record origin and licence:

```bash
uv run hylo ingest spec.json          # {"source": {"type", "params"}, "name", "licence", "out", "image_every", "assume_success"}
uv run hylo label RUN_DIR --judge bench/runs/judges/l10-trace-v2     # label unlabelled episodes with a ready judge
uv run hylo contamination EXTERNAL_RUN --protected bench/runs/rsi-libero10/runs
```

- `hylo label` labels only ingested runs, only with a `ready` judge, at no less than its calibrated threshold, and
  never runs the judge was built from. An episode below the threshold stays unlabelled; a low score is never called
  a failure.
- `hylo contamination` compares each external episode's initial state with the initial states of protected (gate and
  held-out) episodes of the same task. External data that reproduces protected init states must not be used to build
  anything that is then gated on them.

Data sources are `datasources` plugins: `video.frames` and `video.files` (hylo-data-video) and `lerobot.dataset`
(hylo-policy-lerobot, unverified here: dataset downloads have not been approved yet).
