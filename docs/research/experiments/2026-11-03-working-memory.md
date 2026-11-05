# Working Memory Evaluation

> Archived implementation: the Working Memory runtime, agent, dedicated prompt gate and RoboMME runners were removed on 2026-11-04. The text and results below describe the historical experiment, not currently available APIs. The removed source and tests are retained in `hyloai/runs/retired-working-memory/2026-11-04/source.tar.gz`, with hashes in `manifest.json`. SimpleMemVLA, event-memory primitives and the shared evolution framework remain available.

Date: 2026-11-03. This experiment implements the runtime proposed in
[RFC-0009](../../rfcs/RFC-0009-benchmark-memory.md), following the
[performance review](../comparisons/memory-performance-review.md).
It is independent of the earlier [heuristic pilot](2026-11-03-robomme-memory-pilot.md).

## Implementation

\[Implemented\] `hylo-core` defines evidence, working-state patches, history requests,
bounded execution contracts and receipts. `hylo-memory` stores original RGB blobs with
SHA-256 checks, episode isolation, observation/availability clocks, chronological queries
and explicit omissions. Working-state updates reject unseen citations, stale revisions,
ambiguous updates and silent removal of pending intentions. Earlier interpretations remain
in an append-only journal. These checks protect provenance, not semantic correctness
(`harness/packages/hylo-core/src/hylo/core/working_memory.py:1`;
`harness/packages/hylo-memory/src/hylo/memory/working.py:1`).

\[Implemented\] The new RoboMME runner uses one frozen model for memory writing, interval
selection, current-image grounding and planning. Decisions delegate at most 64 control
steps to the existing frozen VLA, in chunks of at most 16. A robot-state guard may request
earlier review. Receipts record attempts and observations; they never certify success.
The runner uses no color-region rules, task-name dispatch or dedicated physical-event
counter (`harness/examples/memory/robomme/run_working.py:1`).

\[Implemented\] A native `WorkingMemoryAgent` also composes these stores/contracts with
Hylo's existing `Agent` interface. Its injected planner receives allowlisted images/state
and episode-local memory, not `EpisodeContext` or evaluator fields. A command adapter
targets the motor agent's declared interface. CPU tests verify budget accounting and
that reward, success and extra oracle fields do not enter planner/motor step inputs.
This adapter has not yet been benchmarked through the Hylo kernel; the RoboMME results
below use its dedicated benchmark runner
(`harness/packages/hylo-agents/src/hylo/agents/working_memory.py:1`).

\[Implemented\] Development prompt candidates can use the existing `CandidateRegistry`
through `MemoryPromptCampaign`. A predeclared finite campaign requires fresh validation
pairs, matching prompts/reset evidence/runtime fingerprints, a paired exact one-sided
test with candidate-budget adjustment, minimum gain and family regression checks.
Failed gates consume their panel; activation and rollback remain versioned. This is an
implemented gate, not evidence of a successful prompt optimization campaign
(`harness/packages/hylo-evolve/src/hylo/evolve/memory_prompt.py:1`).

## Protocol

The primary comparison is `history` versus `working`, with the same reasoner, frozen
grounded-subgoal pi0.5 checkpoint, observations, motor interface and control limits.
`history` includes the last 16 frames and up to 48 uniformly sampled earlier frames.
`working` includes recent/reset/history samples, revisioned claims and up to two requested
interval reads within a 64-historical-frame decision budget. Both receive native current
front/wrist views and the last execution receipt. Working memory additionally processes
demonstration prefixes with self-carried state. Report this cost; the comparison is not
token-matched. Test episodes never update the cross-episode prompt/program library.
This compares the combined memory policy against a sampled-history control. It does not
separately identify the contributions of state, frame selection, demonstration processing
and retrieval; those require additional ablations under fixed inference budgets.

Task instructions enter the planner; task IDs, evaluator success, seeds, reward and hidden
object state do not. Public reset/demo frames are retained. Original benchmark scoring
and termination remain intact. Invalid model outputs and exhausted model-call budgets
count as failures, including paired statistics. Infrastructure errors are separately
enumerated; all attempted episodes remain in per-attempt rates.

All 16 original RoboMME tasks are the evaluation inventory. Training episodes are used
for interface calibration. The previously inspected validation IDs 0/3 are not fresh
validation data. The canonical complete benchmark is 50 test episodes/task; a smaller
validation panel must be labeled accordingly.

Before any new validation outcome, the first panel was fixed to validation IDs **1 and 7**
for every task. Source metadata labels these easy and hard for all 16 tasks: 32 pairs,
64 attempts, 1,300 control steps and at most 120 model calls per episode. Condition order
alternates across the two selected IDs and tasks. This is a stratified exploratory panel,
not the official test distribution or a promotion gate. The plan and metadata hashes are
saved under `runs/memory-20261103/working-v1/validation-plan.json` and
`validation-metadata.json`. Workers run in separate processes; a failed worker retains
completed results and explicitly records missing attempts as infrastructure errors.

## Runtime

Remote workspace: `/home/gaobin/hylo-memory-eval`, physical GPU 1 only. The existing
SERA/RoboMME/ManiSkill/checkpoint pins are documented in the earlier pilot. No new model
weights or training data were downloaded. Qwen3.6-27B was already cached at snapshot
`6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`; the inference server loaded it successfully
in bfloat16 with the frozen pi0.5 server on the same GPU. This changes the reasoning model
relative to the earlier Qwen3.5-9B pilot, so cross-pilot deltas cannot isolate memory.
The final backend uses the already installed vLLM 0.19.0, greedy structured JSON output,
non-thinking decoding, no prefix caching, and an isolated Triton/vLLM cache. Both conditions
use this same backend. This evaluates one frozen inference configuration; it does not
establish the best achievable result with the architecture or another reasoning model.
Episodes run sequentially, with a single-threaded vision HTTP service and vLLM
`max_num_seqs=1`. The fixed panel is a queued evaluation, **not batched inference**.
The motor server isolates per-connection policy state but also executes inference
synchronously. Wall-clock measurements therefore describe this serial configuration,
not optimized multi-environment throughput.

## Calibration

The first training-only integration attempt exposed an exact point-token formatting
mismatch (`point_1` versus `<point_1>`) and a baseline parser that unnecessarily rejected
unused memory annotations. Both were fixed before validation. Bare point names now compile
to the same coordinates; baseline annotations are logged and discarded rather than
persisted. The interrupted calibration retains its completed failures, partial episode,
source archive and raw responses under remote `results/working-calibration-v1`.
The corrected calibration uses separate immutable source/output directories. A later
training-only backend probe encountered a stale/incompatible Triton cache (`cubin` missing);
an isolated cache passed two real-image requests. The initial vLLM memory reservation
also left insufficient space for SAPIEN. It was reduced from 0.74 to 0.64 of GPU memory
before validation. These initialization failures are infrastructure diagnostics, not
evidence about memory performance. Runtime source snapshots v1–v8 and their logs remain
under the remote workspace; no failed calibration artifact was overwritten.

The validation snapshot v8 also retains uncommitted memory proposals across a history-read
continuation and removes the archive's episode-scope identifier from model-visible query
references. The full identifier remains in audit artifacts. This prevents task/split metadata
embedded in that identifier from entering the planner. These changes precede validation;
the final calibration uses v7. Source and server fingerprints are checked before each
validation worker, and changing either interrupts the panel.

Under the earlier Transformers calibration, VideoUnmask train-0 succeeded in both
conditions: working memory used 120 actions/8 calls, sampled history used 229 actions/12
calls. PickHighlight history then timed out at 1,300 actions. These are training outcomes
from an earlier backend configuration, not held-out results or estimates of memory gain.

The final vLLM calibration completed all eight training attempts without infrastructure
or output-schema errors. Each row below is one train-0 pair; these are development
observations, not benchmark scores.

| Task | History outcome, actions, calls | Working outcome, actions, calls |
|---|---|---|
| VideoUnmask | Success, 766, 26 | Success, 226, 13 |
| PickHighlight | Timeout, 1,300, 41 | Success, 197, 7 |
| PickXtimes | Timeout, 1,300, 44 | Failure, 909, 31 |
| PatternLock | Failure, 65, 5 | Failure, 18, 4 |

Working memory succeeded in 2/4 training cases versus 1/4 for history. There was only one
discordant pair; this is not evidence of a general improvement. None of the four working
episodes requested an interval read, so this calibration does not establish retrieval's
utility. In PickXtimes the model claimed two completed cycles and pressed the termination
button, but the benchmark rejected the result. In PickHighlight it temporarily described
the red cube as held while the recorded frame still showed it on the table. Evidence
citations and revision checks do not themselves ensure correct visual interpretation.

Calibration totals were 116 calls, 590,458 input tokens and 38,259 output tokens for history;
55 calls, 164,494 input tokens and 12,710 output tokens for working memory. Faster failure
can reduce these totals, so aggregate cost reductions must not be interpreted as equal-task
efficiency gains. Full RGB/action evidence remains in remote
`results/working-calibration-final-v2`; metadata, raw responses and analysis are mirrored at
`runs/memory-20261103/working-v1/calibration` locally.

## Results

The fixed validation panel completed all 64 attempts across 16 tasks. Sampled history
succeeded in **4/32 cases (12.5%)**, working memory in **2/32 (6.25%)**. There were zero
working-memory-only wins, two losses and 30 ties; no pairs were incomplete or invalid.
The exact two-sided McNemar p-value is 0.5: this small panel does not establish a statistically
significant difference and provides no evidence of improvement. This is the fixed exploratory
validation panel, not the official 800-episode test. The
[machine-readable snapshot](2026-11-03-working-memory.results.json) retains configuration,
individual outcomes, costs and paired statistics. Current evidence does not support
promoting this working-memory configuration as a performance improvement.

All 32 working episodes made no explicit interval reads. Their 1,554 model calls
included 365 demonstration calls; history used 1,201 calls. Therefore this panel
tests model-maintained summaries and automatic frame selection without demonstrating
useful retrieval behavior. In VideoPlaceOrder validation-7, working memory used 50 calls
on the demonstration and exhausted the 120-call budget after 271 executed actions. Its
recorded belief claimed completion while the benchmark remained active. This is a measured
failure mode, not evidence that a citation-backed claim is correct. The source artifacts
remain available under the corresponding `workers/VideoPlaceOrder-07` directory.

CPU tests exercise evidence integrity, causal reads, atomic revisions,
pending-intention retention, baseline isolation, command compilation, paired-failure
accounting and candidate activation/rollback. These tests are not robot success rates.
The broad CPU check passed 108 tests; after the final reader changes, 24 targeted tests
passed. Logs are retained under `runs/memory-20261103/working-v1/`.

A validation attempt exposed a repair-path defect: a malformed generated response contained
tens of thousands of whitespace characters, and echoing it in the repair prompt exceeded
the model context limit. The frozen v8 panel counts this as an agent failure. A subsequent
local fix trims and bounds the repair excerpt while retaining the full invalid output in
the audit log; ten runner tests passed, including two new oversized-output regression cases.
This fix was **not** deployed to the completed panel or measured on GPU. Any future
evaluation of it must use a new source manifest; the current score belongs to archived v8.

A separate local server revision adds bounded HTTP request microbatching for vLLM.
Four batching tests verify response isolation, error delivery, recovery, capacity and
cancelled requests; together with the repaired runner, 14 targeted tests passed. The final
broad CPU regression passed **114 tests in 80.56 seconds**, recorded in
`runs/memory-20261103/working-v1/final-cpu-tests.log`. The separate GPU throughput probe
completed on 2026-11-04: six serial requests took 52.63 seconds, while six requests sent
in concurrent pairs took 29.58 seconds, an observed **1.78x request-throughput ratio**.
All twelve outputs parsed as JSON and matched the warmup output. Both traffic conditions
used the same size-two server, 200 ms collection window and training image, with prefix
caching disabled. This small fixed-payload probe establishes that requests were batched;
it is not a representative workload study or a robot success-rate improvement. Its artifact
is `runs/memory-20261103/working-v1/working-batch-probe-v1.json`. The completed robot panel
used the serial episode scheduler and the earlier server revision.

## Remaining Scope

The runtime currently provides temporal interval reads and model-maintained typed claims;
it does not implement a learned association tracker, semantic image reranker or independently
verified physical-event detector. Program-skill synthesis and a full automated development
search are not claimed as implemented by the prompt gate. MIKASA requires a compatible
EEF-delta frozen executor; RMBench requires its bimanual execution bridge. Neither can
inherit the RoboMME joint-action checkpoint unchanged. MEMOBench remains a diagnostic
design reference under the current noncommercial artifact boundary.
