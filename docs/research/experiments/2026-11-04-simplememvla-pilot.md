# SimpleMemVLA Pilot

Date: 2026-11-04. The frozen released SimpleMemVLA RoboMME checkpoint completed a
four-task test subset with **40/40 successes**, no excluded episodes and no recorded
episode errors. This is a measured full-system pilot, not a full RoboMME leaderboard
score or evidence of an improvement from Hylo's external memory.

## Results

| Task | Test episode IDs | Successes | Excluded |
| --- | --- | ---: | ---: |
| PickXtimes | 0–9 | 10/10 | 0 |
| VideoUnmask | 0–9 | 10/10 | 0 |
| PickHighlight | 0–9 | 10/10 | 0 |
| PatternLock | 0–9 | 10/10 | 0 |
| Total | Fixed subset | **40/40** | **0** |

The closed-loop group ran for **1,151.1 seconds (19 minutes 11 seconds)**, excluding model
loading. It made 52 shared-batch inference calls. All 40 planned task/episode identities
match the final outcomes and the per-episode terminal success events. All 40 resets passed.
The process exited and the A100 was released after completion. A minute-level read-only
watchdog recorded progress and terminated when the job finished.

## Protocol

The four task families were selected before the test outcomes; each uses the first ten
native test IDs without resampling. All 40 environments share one inference batch, ordered
round-robin by task. Native environment reset, observations, instructions, actions and
success predicates are retained. Each episode has at most 1,300 control steps, executes
16 actions per decision, uses ten denoising steps, temperature 1.0 and at most 64 subtask
tokens. Torch and NumPy start at seed 0. Weights are frozen; no training was performed.

Source: `OpenBMB/SimpleMemVLA@453d6ec293e63318bbc2bce545d0b9256ab1bc51`.
Checkpoint: `yinchenghust/simplememvla_robomme@6bf7204311496b93f12889cad0eaf3fcbddc35e4`.
The model file SHA-256 is
`3d0fa9de73353cbd3e0e6c9b798b3747b7126931d42ce3a8cd510be767ffce69`.

Runtime: ecolab A100 80GB, Python 3.11, Torch 2.9.1, Transformers 5.11.0, bf16, SDPA,
FLA 0.2.2 and causal-conv1d 1.6.2.post1. An external runtime adapter replaces the
nonoverlapping visual Conv3d patch projection with its equivalent GEMM. CPU equivalence
tests and a checkpoint-weight numerical check passed; see the
[method screening](../comparisons/memory-method-screening.md) for tolerances and batch
measurements. Original cloned sources remain unchanged. A separate CPU routing test
checks that heterogeneous tasks retain their instruction and outcome identities through
the native pool and group evaluator.

## Interpretation

The pilot is encouraging evidence that this released checkpoint and execution stack can
solve these four selected memory task families. Ten episodes per task are insufficient
to establish robustness across all tasks or difficulty distributions. No memory-off
control was run, so these results do not isolate memory's causal contribution. They are
also not comparable directly to a score averaged over all 16 RoboMME tasks.

Runtime deviations include the projection implementation, dependency versions, SDPA and
heterogeneous batching. Batching changes random-number consumption relative to native
per-task evaluation. Videos were disabled to avoid collisions in the native mixed-task
video filenames; all terminal outcomes and inference timings were logged.

Test IDs 0–9 for these four tasks are now observed. If this pilot informs subsequent
tuning, those episodes must not be presented as fresh evaluation data. The prior automatic
800-episode run remains held at the user's request. Earlier completed training groups
(`PickXtimes` 50/50 and `VideoUnmask` 50/50) are separate integration checks and are not
pooled with these test results.

## Artifacts

- [Hylo memory integration](2026-11-04-simplememvla-integration.md): subsequent source parity
  and eight-episode implementation regression, reported separately from this pilot.
- [Results and protocol](2026-11-04-simplememvla-pilot.results.json), including artifact hashes
  and denominator checks.
- Local raw results, protocol, progress and watchdog history:
  `runs/memory-20261104/simplememvla-v1/ecolab/test-targeted-v1/`.
- Remote run: `~/hylo-memory-eval/evals/simplememvla-v1/test-targeted-v1/` on ecolab.
- Runtime and monitor: `targeted-pilot.py`, `fast_runtime.py`, `test-mixed-routing.py`
  and `watch-targeted.py` under `runs/memory-20261104/simplememvla-v1/`.
