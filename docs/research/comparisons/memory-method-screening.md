# Memory Method Screening

Research date: 2026-11-04, Asia/Singapore. This expands the
[performance review](memory-performance-review.md) beyond the original research repositories.
Every external number below is **author-reported**, not a Hylo reproduction. This is a
candidate screen, not an exhaustive ranking or a completed source audit of every project.
The [Hylo working-memory experiment](../experiments/2026-11-03-working-memory.md) has not
established an improvement; existing successful configurations should be evaluated before
another custom architecture is assumed to work.

## Selection Criteria

Prioritize a matching memory benchmark, a controlled memory ablation, executable code and
released weights or accessible model services. A high ordinary manipulation score does not
by itself demonstrate memory. Keep task inventory, observation permissions, action interface,
adaptation data and model strength attached to every result. Loading an already trained
checkpoint for evaluation does not require Hylo to train a new model; it does change the
executor and therefore constitutes a full-system reference, not an isolated harness gain.

## Robot Policies

| Method | Author-reported evidence | Interpretation and evaluation priority |
|---|---|---|
| **SimpleMemVLA** | RoboMME 88.25 on the board; RMBench 94.0 over nine shared tasks; original five-task MIKASA subset 74.0 | First local checkpoint candidate. Timestamped native video, rather than summaries alone. Its same-backbone RoboMME comparison reports native context 88.3 versus retrieval 31.5, token compression 22.6 and recurrence 20.6. Public suite-specific checkpoints and evaluation runners are available. [Code and results](https://github.com/OpenBMB/SimpleMemVLA), [paper](https://arxiv.org/abs/2609.05533). |
| **BridgeVLA++** | RMBench 96.0; three-task MemoryBench 99.7, versus its memory-free base 11.3 | Strong spatial-memory candidate with released weights. Uses a different 3D observation/action stack; run natively on MemoryBench/RMBench. Do not compare the 99.7 directly with RoboMME percentages. [Results](https://bridgevla-plus.github.io/), [code](https://github.com/BridgeVLA/BridgeVLA). |
| **SAM2Act+** | MemoryBench 94.3, 39.3 percentage points above SAM2Act without memory | Strong matched spatial-memory reference for BridgeVLA++. Public MemoryBench checkpoints and evaluation instructions exist. The current release notes describe changes to training and the drawer task; pin the revision and task version. [Results](https://sam2act.github.io/), [release](https://github.com/sam2act/sam2act). |
| **MemoryVLA / MemoryVLA+ / MemoryVLA++** | Original five-task MIKASA subset: 41.2 for MemoryVLA, 44.4 for MemoryVLA++; LIBERO averages use different inventories | Useful perceptual/cognitive-memory baseline. The fetched model table links MemoryVLA checkpoints while marking the ++ entries TBD. Availability of the relevant checkpoint is a prerequisite; do not substitute the older model and call it ++. [Model table](https://github.com/shihao1895/MemoryVLA). |
| **PonderPounce** | RoboMME 60.83 with base-scale data; 75.54 with 9x data | Native causal context supplies an asynchronous continuous cognition token to the action policy. Jointly trained; keep data scales separate. [Paper](https://arxiv.org/abs/2608.24115). |
| **PonderPounce-WM** | RoboMME 67.42, 6.59 points above PonderPounce in the reported comparison | Newer future-prediction variant worth screening; checkpoint and reproduction readiness still need verification. [Project](https://worv-ai.github.io/ponderpounce-wm/). |
| **T²Mem** | RoboMME 56.83 versus 17.93 for the memory-free base | Compact fast weights updated online. Relevant efficiency comparison, but its test-time updates and prior training differ from Hylo's frozen-weight runtime. [Paper](https://arxiv.org/abs/2609.36720). |
| **MemBodied** | Five RMBench tasks, 50 episodes/task: 50.0 versus stateless 6.4 and recurrent 16.8; NativeMEM 38.4, combined 45.2 | Delayed action/outcome writes and a fixed initial-scene anchor are relevant. This five-task score cannot rank against nine-task RMBench scores. Source is available; the README says trained checkpoints are not bundled. [Results](https://declare-lab.github.io/MemBodied/), [code](https://github.com/declare-lab/MemBodied). |
| **MemER** | Three real-world memory-intensive manipulation tasks; separate RoboMME implementation reviewed previously | Learned keyframe selection, temporal clustering and a low-level VLA. A useful retrieval comparator, not the strongest RoboMME result in the screened board. [Paper](https://arxiv.org/abs/2510.20328). |
| **MEM** | Long-horizon real-robot tasks spanning up to fifteen minutes | Short-term video and long-term textual memory. Relevant multiscale design; the paper's real-robot result is not a runnable RoboMME score. [Primary paper](https://www.pi.website/download/Mem.pdf). |
| **OneTwoVLA** | Real-robot long-horizon planning, recovery and adaptive reasoning | Useful reasoning/action integration reference. Do not infer a RoboMME or MIKASA rank from its real-robot demonstrations. [Paper](https://arxiv.org/abs/2505.11917). |

## External Harnesses

| Method | Author-reported evidence | Interpretation and evaluation priority |
|---|---|---|
| **MEMI-Astra-Act** | Same reported Act setup: FullHist 85.3, initializer memory 88.3, optimized memory 97.0 on 16 RoboMME tasks | Strongest screened evidence for prompt-optimized memory without new weight updates. Reproduce the released Act prompts and self-carried memory, including its full-history control. Its 99.4 Plan score uses simulator-derived perception and a ground-truth controller and is an oracle reference. [Results and ablations](https://memi-robot.github.io/). |
| **Astra-Guide** | 777/800, 97.125 on RoboMME | Strong complete harness: frozen VLA, direct EEF interventions and experience adaptation across scored episodes. Start from `initial`; `final` contains test-derived experience. Report frozen-library and online-adaptation protocols separately. [Protocol](https://github.com/Legend717/astra-guide-vla/blob/dc3074cc234945dfaad1ffd5e48d5da490f7e736/docs/results.md). |
| **Embodied-Astra** | RoboMME 92.125 | Important strong full-history/direct-waypoint control. Its executor differs from the GroundSG VLA and its score cannot isolate memory compression. [Paper](https://arxiv.org/abs/2610.17350). |
| **RoboMemory** | EmbodiedBench: +26.5 percentage points for Qwen2.5-VL-72B-Instruct in the reported comparison | Temporal, spatial, semantic and episodic memory with a dynamic spatial graph. Particularly relevant to an external harness, but its benchmark and actions differ from RoboMME. [Project](https://sp4595.github.io/robomemory/). |
| **SERA** | RoboMME 51.38 versus base agent 44.38 | Relevant self-evolution/experience reference, lower empirical priority than the above strong systems. Selected evolved bundles are not included in the audited release. [Pinned source review](../projects/memory-landscape.md). |
| **HarnessPAI** | LIBERO-PRO 96.5 under its evolution/evaluation protocol | Program evolution is relevant, but the score includes a different benchmark/protocol and is not a RoboMME result. No license in the audited snapshot: design reference, no code copying. [Pinned source review](../projects/memory-landscape.md). |

The first three high-performing agentic configurations depend on frontier reasoning models.
Replacing those models with the current Qwen service produces a new configuration, not a
reproduction of the reported score. The local process environment has no configured OpenAI
or Anthropic API key; this does not establish that no usable service exists elsewhere.

## General Agent Memory

These methods can supply external memory without changing VLA weights. Their published
conversation or retrieval results do not establish robotic task success. Before closed-loop
integration, compare them on identical timestamped robot observations and questions about
identity, order, counts, changed facts and pending actions, with one shared reader model.

| Method | Evidence and mechanism | Hylo screening decision |
|---|---|---|
| **Hindsight** | Author-reported LongMemEval 91.4 with a larger backbone; four logical networks, retain/recall/reflect, temporal/entity retrieval. [Paper](https://arxiv.org/abs/2512.12818), [system description](https://aclanthology.org/2026.acl-demo.27/). | First general-memory candidate; test whether separating observations and beliefs helps avoid persistent false conclusions. |
| **SimpleMem** | Structured compression, consolidation and query-aware retrieval; author-reported conversational accuracy/cost improvements. [Paper](https://arxiv.org/abs/2601.02553). | Lightweight retrieval comparator. It is a different project from SimpleMemVLA. |
| **Omni-SimpleMem** | The official SimpleMem repository exposes image/audio/video ingestion and retrieval; author-reported LoCoMo and Mem-Gallery results. [Repository](https://github.com/aiming-lab/SimpleMem). | Candidate for visual episodes; verify the exact multimodal benchmark and release before ranking it. |
| **EvolveMem** | The same repository exposes development-set retrieval configuration optimization with guarded revisions. [Repository](https://github.com/aiming-lab/SimpleMem). | Relevant no-new-weight optimization route. Use development-only questions and a separate held-out test. |
| **A-MEM** | Agent-written linked notes with dynamic indexing and updates. [Paper](https://arxiv.org/abs/2502.12110). | Include as an adaptive organization comparator; not evidence of superior robot control. |
| **Mem0** | Fact extraction, consolidation and retrieval, plus a graph variant; LoCoMo evaluation. [Paper](https://arxiv.org/abs/2504.19413). | Include as a simple external-memory baseline; do not rank it using incompatible vendor numbers. |
| **Zep / Graphiti** | Temporal knowledge graph with evolving relationships; DMR and LongMemEval evaluation. [Paper](https://arxiv.org/abs/2501.13956). | Relevant changed-fact and temporal-binding comparator; distinguish the open engine from the managed system. |
| **LightMem** | Sensory filtering, short-term consolidation and offline long-term updates; LongMemEval accuracy/cost comparisons. [Paper](https://arxiv.org/abs/2510.18866). | Include in cost-sensitive screening; verify online latency separately from offline consolidation. |
| **HippoRAG 2** | Graph-supported associative retrieval with passage integration and Personalized PageRank. [Paper](https://arxiv.org/abs/2502.14802). | Knowledge/skill retrieval comparator; less direct evidence for dense visual episodic control. |

## Execution Order

1. **SimpleMemVLA on RoboMME**, using its released checkpoint and native batched evaluator.
   It supplies a strong local complete-system reference with no frontier API dependency.
   Follow with its five-task MIKASA checkpoint; do not describe that as full 90-task coverage.
2. **MEMI-Act and Astra-Guide**, once their intended reasoning backend is available.
   Preserve their own action interfaces first; then compare controlled memory ablations.
3. **BridgeVLA++ and SAM2Act+ on MemoryBench**, using compatible pinned scene/task versions.
   These test spatial memory directly and complement RoboMME's wider family inventory.
4. **Hindsight, SimpleMem/Omni-SimpleMem and temporal-graph baselines** on causal robot-trace
   retrieval before spending closed-loop GPU time on every generic memory package.

This order is a resource-aware experiment decision, not a claim that these methods have
already reproduced or that any single design dominates all memory types.

On 2026-11-04 the user confirmed SimpleMemVLA as the immediate execution priority;
BridgeVLA++ work is deferred. The original Hylo panel is now complete (history 4/32,
working memory 2/32), and the separate inference microbatch probe completed. SimpleMemVLA
has passed CPU weight loading but still has no GPU rollout result. Its eight-episode
training integration check precedes the fixed 800-episode original RoboMME test.

The user subsequently requested migration to the A100 machine
`bingao@ecolab.ddns.comp.nus.edu.sg`. Both unstarted SimpleMemVLA queues on sura were
archived and stopped to prevent duplicate runs; completed experiments and checkpoint files
remain intact. SSH authentication now works. The machine has one A100 80GB PCIe,
driver 580.65.06, with 81,153 MiB free and no compute workload at inspection.
The transferred checkpoint passed its full SHA-256 check. The isolated Python 3.11
runtime passes CUDA and evaluator imports, retaining Torch 2.9.1 and SDPA from the checked
sura configuration. Native `PickXtimes` training episode 0 reset and front/wrist camera
checks passed in 4.36 seconds: both cameras produced nonconstant 256×256 RGB images and
the state vector had eight elements. The eight-episode training job launched on GPU 0
at 03:27:27 UTC with batch size 2. Its initial runtime uses the Torch fallback for Qwen's
gated-delta operations; fused optional kernels are not installed, so throughput remains
unverified. The fixed 800-episode test remains gated on eight recorded training outcomes
including at least one success. Preparation, camera artifacts, dependency freeze and queue
supervision are recorded in `runs/memory-20261104/simplememvla-v1/ecolab/` and its parent.
The initial training run subsequently completed `PickXtimes` 2/2 and `VideoUnmask` 2/2
successes. These four training outcomes are a partial integration check, not a held-out
benchmark score. At the user's request for fused kernels and larger batches, the old
test queue was held and the unfinished training process was stopped, preserving its
logs and videos. Interrupted episodes are not reported as policy failures.

An isolated runtime overlay now imports all four Qwen fast-path interfaces using
`flash-linear-attention==0.2.2` and the official Torch 2.9/CUDA 12
`causal-conv1d==1.6.2.post1` wheel. Its SHA-256 was checked against GitHub release metadata.
Torch SDPA remains the attention backend; external FlashAttention 2 is not installed.
A full-window training-video replay probe measured batches 2, 4, 8, 16, 24, 32, 48 and 50,
including cold visual features and two subsequent decisions. Selection keeps 12 GiB of
GPU headroom and chooses the largest tested batch within 10% of the best measured replay
throughput. This probe is not a closed-loop speed or accuracy measurement. The selected
batch must subsequently pass complete training integration groups before the fixed
800-episode test starts. Per-group outcomes and periodic inference timings are logged by
an external wrapper; environment and success logic remain unchanged.

Call-stack sampling isolated an additional A100 bottleneck in the visual patch `Conv3d`
projection. Because each input is exactly one nonoverlapping convolution patch, the runtime
wrapper replaces that projection with the equivalent flattened-weight GEMM. Two CPU tests
pass (float64 convolution equivalence and rejection of unsupported geometry). A check using
the released checkpoint gives maximum absolute error 0.007775 and RMS error 0.000752 against
FP32 CPU convolution on identical bf16-quantized inputs, within the declared `atol=0.02`,
`rtol=0.02` tolerance. This is an explicit numerical/runtime deviation; it does not establish
closed-loop equivalence. The original cloned source remains unchanged. With the replacement
and fused Qwen path, the initial batch-2 full-window replay took 169.2 seconds including
first-time compilation, followed by 1.46 and 1.45 seconds for subsequent two-row decisions.
These are replay timings, not end-to-end robot episode speedups or benchmark success rates.

The scan selected **batch 50**, allowing each task's 50 test episodes to share one native
evaluation group. All eight candidates returned finite actions with the expected shape.
Selected replay measurements are below; timings include input preparation and action
generation after the initial compile/feature-fill call, but exclude simulation:

| Batch | Mean subsequent call, seconds | Decisions/second | Peak Torch reserved memory, GiB |
| --- | ---: | ---: | ---: |
| 2 | 1.46 | 1.37 | 13.96 |
| 8 | 4.15 | 1.93 | 20.35 |
| 24 | 11.46 | 2.09 | 36.85 |
| 32 | 15.38 | 2.08 | 45.23 |
| 48 | 23.06 | 2.08 | 61.91 |
| 50 | 23.69 | 2.11 | 63.96 |

Batch 50 improves replay throughput by approximately 54% over **the same optimized
runtime at batch 2**, not over the original unfused evaluation. The first batch-50 call
took 104.08 seconds including compilation/feature fill. The probe uses repeated training
video and one instruction, so it does not cover every task's prompt, generated subtask or
simulator allocation. Consequently, the selected configuration now enters four full
training groups (50 episodes each, 200 total); the 800-episode test starts only after all
training outcomes are recorded, at least one succeeds, and no training group reports OOM.
Full benchmark performance and end-to-end throughput remain pending. Records are retained
in `runs/memory-20261104/simplememvla-v1/ecolab/fast-batch-probe.json`; remote execution uses
`train-fast-v1`, followed by `test-fast-v1`.

The user subsequently requested a smaller task subset before full evaluation. The training
run had completed `PickXtimes` 50/50 successes in 2,755.0 seconds and `VideoUnmask` 50/50
in 627.9 seconds, with no excluded episodes in either group. Its remaining training work
was interrupted and the automatic 800-episode test was held; interrupted work is not
reported as policy failure. A separate `test-targeted-v1` pilot now uses `PickXtimes`,
`VideoUnmask`, `PickHighlight` and `PatternLock`, with fixed **test episode IDs 0–9 per task**
(40 total). These are the same four memory families selected before the preceding results,
not a success-based task selection.

The pilot feeds all 40 environments into one shared inference batch, with round-robin task
ordering and native per-environment instructions, observations, actions and success logic.
A CPU routing test confirms that different tasks and episode IDs retain their instruction
and outcome correspondence through the native simulation pool and group evaluator.
Per-episode terminal events are logged immediately. Heterogeneous batching changes the
policy RNG stream relative to per-task evaluation and is recorded as a protocol deviation;
this is an exploratory subset result, not an official full benchmark score. Test IDs 0–9
are considered consumed for subsequent tuning. The remaining test IDs must not be described
as previously evaluated or used to select this pilot. The full 800-episode queue will not
automatically restart after this pilot.

The targeted pilot subsequently **completed with 40/40 test successes**, ten per task,
without exclusions or recorded episode errors. Its closed-loop group took 1,151.1 seconds
and 52 shared-batch inference calls. A minute-level watchdog followed it through completion;
the evaluator exited and released the GPU. The exact planned ID set, all reset outcomes
and all terminal events were checked against the final results. See the
[pilot report](../experiments/2026-11-04-simplememvla-pilot.md) for protocol deviations,
machine-readable results and interpretation. This encouraging subset result does not
reproduce the full benchmark or demonstrate a causal gain from Hylo external memory.

## Verification Status

### Leaderboard Snapshot

The 2026-11-04 official-page check expands the original candidate screen. These are published
leaderboard entries or author-reported results, not Hylo reproductions. Raw HTML, JSON and
static JavaScript data plus source URLs and SHA-256 hashes are retained under
`runs/memory-20261104/leaderboard-snapshot/`. Tables embedded in JavaScript were read as data,
without executing the downloaded code.

| Benchmark and track | Leading published entries | Interpretation |
|---|---|---|
| [RoboMME Standard](https://robomme.github.io/leaderboard.html) | SimpleMemVLA 88.25; PonderPounce 60.83; T²Mem 56.83; FrameSamp+Modul 44.51; MemER 42.38 | All 16 tasks, 800 episodes; current board entries, not every result published elsewhere. |
| RoboMME Agentic | Astra-Guide 97.125; MEMI-Astra-Act 97.0; Embodied-Astra 92.125; 3-tier Astra 79.125 | Oracle rows are excluded. Adaptation and control interfaces differ across entries. |
| [RoboMME-Plus](https://robomme.github.io/data/plus.json) | Zero-shot Agentic: Embodied-Astra 22.625, 3-tier Astra 9.5. Zero-shot Standard: PonderPounce 2.875, FrameSamp+Modul 2.75, SimpleMemVLA 2.0. One-shot Embodied-Astra: 35.25 | Keep few-shot separate from zero-shot. The SimpleMemVLA original-suite score does not establish robust transfer to the shifted tasks. |
| [RoboDojo-Sim, Memory dimension](https://robodojo-benchmark.com/leaderboard) | Agent entries sorted by Memory Score: Q0-Preview 93.68, HexaShell-Preview 84.53, EmbodiedEvo 79.40, PyRUA-Lean 68.40, WorldScape-R²SI 65.78. Non-Agent: WALL-OSS-1.0-lite 57.42, VPP2 56.01, VPP2-Preview 50.78, CogACTv2 Preview 50.46, Rex-M1 Preview 48.53 | These are Memory Scores, not overall scores or success percentages. SimpleMemVLA has Memory Score 33.71 and SR 33.22, ranking 12th among current Non-Agent entries by this column. Its README's fifth-place statement is an older September snapshot. Code/checkpoint availability for the new leaders has not been audited. |
| [RoboMemArena, unverified full-suite reports](https://robomemarena.github.io/leaderboard.html) | TSR: Astra (Codex) 67.31, SimpleMemVLA 63.6, HarnessWAM 59.6, BATON 57.7, RoboFoundry 53.5 | The benchmark explicitly marks these as unverified and warns that protocols differ. Its separate verified table starts with FrameSamp+Modul 46.15, PrediMem 38.5, MemER* 27.3. |

The new agentic leaders and Astra (Codex) expand the next source-audit list. A leaderboard
entry alone does not establish that a runnable public memory implementation is available.
RoboMME-Plus should also be added as a transfer check before calling an original-suite result
promising for Hylo. This finding does not change the already queued fixed original-suite run.

\[Unverified\] Additional upstream sources were read and pinned source trees were obtained
without executing their local scripts. README snapshots and their content hashes are saved
under `runs/memory-20261104/screening-sources/`. Runtime source clones are under
`runs/memory-20261104/reference-src/`, separate from the original MANIFEST repositories.

\[Needs model/hardware\] SimpleMemVLA code is pinned to
`453d6ec293e63318bbc2bce545d0b9256ab1bc51`. The RoboMME checkpoint metadata resolves to
`yinchenghust/simplememvla_robomme@6bf7204311496b93f12889cad0eaf3fcbddc35e4`, declares MIT,
and lists a 12,688,542,952-byte model file with SHA-256
`3d0fa9de73353cbd3e0e6c9b798b3747b7126931d42ce3a8cd510be767ffce69`.
Metadata resolution is not a successful checkpoint load or rollout. Its native evaluator
supports multiple environments per model batch. GPU execution remains to be verified.

The remote preparation job completed checkpoint acquisition, full-file SHA-256 verification
and isolated environment setup at 2026-11-04 00:49 UTC under
`~/hylo-memory-eval/evals/simplememvla-v1`. The native evaluator imports and the checkpoint's
Qwen3VLProcessor loads on CPU. The native weight loader also passed its parameter-name,
dtype and rotary-buffer checks on CPU (5,708,513,800 parameters, 127.8 seconds).
GPU rollout is still unverified.
A queued native smoke run uses idle GPUs: four tasks, two training episodes
each, group size two per GPU. Preparation failure prevents GPU launch. This is an eight-episode
integration check, not the official 800-episode test score. The supported SDPA backend and
existing Blackwell-compatible Torch 2.9.1 are declared infrastructure differences from the
upstream Torch 2.4.1 dependency pin. Source, checkpoint and environment records are retained.

A second durable job waits for all eight training outcomes, including at least one success,
then runs the fixed native RoboMME test protocol: 16 tasks, all 50 test episodes per task,
group size two per GPU, native Torch/NumPy seed zero per worker and the same inference settings. Zero training
successes or incomplete smoke coverage stops this queue for diagnosis. This is an execution
check, not a search over test configurations. The native evaluator excludes reset failures
and failed groups; Hylo therefore requires all 800 outcomes before calling the test complete
and retains the exclusion/OOM logs. No test score exists yet. Protocol and launcher are in
`runs/memory-20261104/simplememvla-v1/{test-protocol.json,test-sequence.py}` in the workspace;
remote state is `evals/simplememvla-v1/test-sequence.json`.

The user expanded GPU authorization on 2026-11-04 to all idle devices. The revised queues
select all qualifying cards at launch and use the upstream multi-GPU task partitioner.
Eligibility requires no compute process, at least 70,000 MiB free, and utilization no greater
than 5% for three samples 15 seconds apart. Occupancy is checked again after acquiring Hylo
queue locks; those locks do not reserve resources against unrelated users. GPU 1 remains
reserved for the existing experiment and throughput probe until that queue terminates.
An idle GPU elsewhere can start SimpleMemVLA without waiting for GPU 1. Actual UUIDs and task
shards are recorded; the native per-worker seed means different GPU counts change sampling
streams, so results must retain their worker configuration. Devices becoming idle after a
run launches are considered at the next launch, not added to an active evaluator. The original
waiting queues were archived and replaced; ongoing robot experiments were not restarted.
This describes the earlier sura scheduling setup; the later ecolab migration stopped those
queues as recorded above.
