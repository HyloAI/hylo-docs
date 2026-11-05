# Benchmark Memory Validation

Date: 2026-11-03. This records executed local checks for [RFC-0009](../../rfcs/RFC-0009-benchmark-memory.md).
**No RoboMME, MIKASA, RMBench or MEMOBench success rate was measured.** The robot experiment uses MuJoCo,
allowed structured observations and a fixed analytic controller, not a VLA. The event diagnostics use reference
event inputs, not image recognition. These boundaries matter when interpreting the results.

The [machine-readable evidence](2026-11-03-benchmark-memory.results.json) includes result payloads, source hashes,
base commit, environment versions, test commands and artifact checksums. Full traces remain under
`runs/memory-20261103/` in the workspace. No dependency, model, dataset or third-party repository was installed,
downloaded or executed for these checks.

## Changes Under Test

- Scoped SQLite deduplication and fact replacement; lossless pose/clock round-trip; exact expiration filters;
  fuller snapshot semantics; additive legacy migration and atomic backdate rejection.
- An episode event journal with idempotent writes, evidence references, ordered history, exact queries,
  explicit unknown/partial results and reset/resume semantics.
- Observation-only signal extraction and `EventMemoryAgent`, which observes every kernel step, compiles
  bounded evidence into the unchanged agent's instruction and caps execution chunks when configured.

Implementation and source locations are listed in [RFC-0009](../../rfcs/RFC-0009-benchmark-memory.md#implemented-foundation).
The detailed regression cases are in `harness/packages/hylo-memory/tests/test_sqlite_semantics.py:15`,
`harness/packages/hylo-memory/tests/test_episode.py:23`, and
`harness/packages/hylo-agents/tests/test_event_memory.py:49`.

## Automated Checks

| Check | Result | Scope |
|---|---:|---|
| Core, memory, agents, memory integration and all seven memory examples | 166 passed | Includes the new event journal/wrapper, existing action memory/skills and example smoke runs |
| Dependency/repository boundaries | 66 passed | No new leaf imports, heavy model dependencies or cross-repository source imports |
| Python compatibility | Passed | Changed Python files parse with Python 3.10 grammar |
| Diff formatting | Passed | `git diff --check` in harness and docs |
| Documentation build | Passed | MkDocs built to `/tmp/hylo-memory-docs-build`; research tags escaped to avoid false cross-references |

The functional suite emitted one existing numerical-overflow warning from the critic test's sigmoid calculation;
it did not fail and that implementation was not changed. These checks are not a full workspace regression suite.

Regression cases include cross-episode deduplication/replacement, simulation time zero, orientation and wall-clock
round-trip, exact 3D radius expiration, scope/entity filters, legacy schema migration, conflicting event IDs,
transactional batch failure, missing anchors, reversed event bounds, repeated ordered cues, delayed intentions,
ambiguous updates, missing observation coverage, explicit resume, mutable-payload isolation and cues inside chunks.

## Event Diagnostics

Command from `harness/`:

```bash
../.venv/bin/python examples/memory/06_event_memory.py \
  --out /home/bingao/hyloai/runs/memory-20261103/event-diagnostics-v2
```

The generator covers spatial, object, capacity, sequential, tracking, negative, checklist, temporal, procedural
and prospective demands, with 100 seeds per category (`10000` through `10099`). Expected answers are constructed
by the task generator; the journal receives observable events and query definitions. All **1,000 complete-evidence
cases were correct**. The result file reports no failing cases
(`harness/examples/memory/06_event_memory.py:29`; machine-readable evidence, `artifacts.event-diagnostics-v2`).

The last-event and eight-event FIFO controls answered none of these deliberately delayed cases correctly. Each
case inserts more than eight distractors after the relevant cue, and a truncated prefix is explicitly marked as
missing coverage. Thus this is a retention/operation stress test, **not a fair leaderboard comparison with a
trained memory baseline**, not evidence of perfect perception, and not proof that all benchmark tasks are solved.
Visual identity tracking, motor execution and language understanding remain outside these probes.

## MuJoCo Control Experiment

Command from `harness/`:

```bash
../.venv/bin/python examples/memory/07_event_memory_occlusion.py \
  --out /home/bingao/hyloai/runs/memory-20261103/event-mujoco-v2 --workers 4
```

Protocol:

- Existing `mujoco/table-v0` validation tasks: direct language, indirect language and push; 100 seeds per task.
- Same fixed, stateless `SceneController`, color chooser, analytic IK, safety configuration and one-step action
  execution in both conditions. Memory off uses current visible scene measurements; memory on additionally
  receives the event journal's earlier scene evidence through `EventMemoryAgent`.
- Objects visible for five control steps versus always visible. All task seeds are paired within each condition.
- No simulator-privileged trace recording and no policy learning. Structured object positions/colors are allowed
  observations in this **local** task; they would not be permitted as privileged inputs on an RGB-only benchmark.

Source: `harness/examples/memory/07_event_memory_occlusion.py:29` and its `main` evaluation loop; exact result
payloads are retained in the companion JSON under `artifacts.event-mujoco-v2`.

| Task | Paired episodes | Hidden after step five, memory off | Hidden after step five, event memory | Always visible, off/on |
|---|---:|---:|---:|---:|
| Direct instruction | 100 | 0/100 | 99/100 | 99/100, 99/100 |
| Indirect instruction | 100 | 0/100 | 30/100 | 30/100, 30/100 |
| Push | 100 | 0/100 | 99/100 | 99/100, 99/100 |
| Combined | 300 | 0/300 | 228/300 | 228/300, 228/300 |

Hidden-condition paired difference: **+0.76**, with 228 wins and zero losses; exact two-sided McNemar
`p = 4.637e-69`. The reported pooled Wilson 95% interval for memory-on success is `[0.7086, 0.8048]`.
The always-visible control has zero discordant pairs and `p = 1`. The command executed 1,200 simulator episodes
across both conditions and both visibility settings, taking about **30.2 seconds** on this workspace.
All 1,200 attempted episodes were recorded as success or failure, with no error or `infra_invalid` outcome.
These are observed measurements, not upstream author reports; runtime is machine-specific.

Interpretation: the new runtime path preserves early evidence well enough for the fixed controller to continue
under occlusion. It leaves the always-visible outcome unchanged in this sample. The indirect task remains poor
with and without occlusion because the simple chooser cannot reliably interpret indirect color descriptions.
Memory storage does not fix that planner limitation.

This comparison establishes memory-on versus memory-off functionality; **it does not establish an incremental
success-rate gain over Hylo's previous `ObjectReasoner` spatial-memory implementation**. The experiment used
validation seeds, not an independent promotion/held-out protocol, and did not promote any candidate or skill.
An initial development invocation exposed that evaluation reuses a worker's agent across episodes; the example
was corrected to keep its backend open across resets. Only the completed `event-mujoco-v2` run supplies the table.

## Existing Spatial-Memory Regression

The unchanged `01_spatial_memory_occlusion.py --quick` example was also run with the revised SQLite backend.
It achieved 24/30 with memory and 0/30 without under occlusion; the always-visible control was 24/30 in both
conditions. This is an additional regression check, not the new event-wrapper experiment. Its separate result is
retained under `artifacts.mujoco-occlusion` in the companion evidence file.

## Remaining Evidence

The workspace has MuJoCo but no installed PyTorch, ManiSkill or SAPIEN and no visible NVIDIA device. Consequently,
there are no visual-extractor precision/recall measurements, frozen-VLA ablations, RoboMME/MIKASA scores or
external benchmark reproduction claims. The actual ready components are CPU storage/recall, a structured-signal
extractor and a tested agent composition boundary.

The next external validation requires a compatible frozen executor, observation-only visual extraction,
benchmark adapters and the pinned simulator/model environment. [RFC-0009](../../rfcs/RFC-0009-benchmark-memory.md#promotion-protocol)
specifies the paired development/validation/test protocol and task coverage. Permission to pursue the work is
already given; the missing inputs are runtime resources and model/interface selection.
