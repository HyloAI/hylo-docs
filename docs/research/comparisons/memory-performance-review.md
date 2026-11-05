# Memory Performance Review

Research date: 2026-11-03, Asia/Singapore. This review supplements the
[benchmark protocols](memory-benchmark-comparison.md) and the pinned
[source studies](../projects/memory-landscape.md). All external scores are
**author-reported**, including leaderboard submissions; none were reproduced here.
“Best” below means highest found in the specified primary-source table and protocol,
not an exhaustive or independently verified global record.

## Comparison Boundaries

A result must carry its task inventory, observation/action permissions, model, adaptation
data, episode count and aggregation rule. A frozen model can still use a trained
benchmark-specific checkpoint. No additional weight updates, no development adaptation,
and no cross-test-episode adaptation are three different conditions.

The RoboMME board was retrieved on this date and labels its data update 2026-10-30.
It separates open-model Standard and proprietary-model Agentic tracks and marks oracle
references. SERA is absent from the fetched board; its paper/README result is recorded
separately. Source: [official leaderboard](https://robomme.github.io/leaderboard.html).

## RoboMME Results

All rows below describe the original 16 tasks, normally 50 test episodes/task. Scores
are percentages; the table is a configuration comparison, not one controlled ranking.

| Method | Author-reported success | Configuration and comparison boundary | Evidence |
|---|---:|---|---|
| Astra-Guide | 97.125 | Highest non-oracle system in the fetched board; frozen Astra and GroundSG VLA, hybrid joint/EEF actions, experience updated across scored test episodes; one run | [Pinned submission](https://github.com/RoboMME/robomme_benchmark/blob/3818966a5b2adffcd39e2b98b262a76e97648218/doc/submission/astra-guide-vla.md#training-and-evaluation-details) |
| MEMI-Astra-Act | 97.0 | Offline task-specific prompt optimization; RGB/proprioception to EEF waypoints; no VLA and no model-weight updates | [Author report, §3.2](https://memi-robot.github.io/) |
| Embodied-Astra | 92.125 | Frozen frontier VLM, sampled full conversation history, direct EEF waypoints; no RoboMME weight updates | [Paper, §§3–4](https://arxiv.org/html/2610.17350) |
| SimpleMemVLA | 88.25 | Highest Standard-track entry in the fetched board; trained native-video VLA; not an external memory plugin | [Leaderboard](https://robomme.github.io/leaderboard.html); [paper, Table 10](https://arxiv.org/html/2609.05533) |
| 3-tier Astra | 79.125 | Frontier planner, GroundSG VLA and separately trained completion monitor | [Leaderboard configuration](https://robomme.github.io/leaderboard.html) |
| PonderPounce | 60.83 | Trained context/action stack; board result, distinct from larger-data paper configurations | [Leaderboard](https://robomme.github.io/leaderboard.html) |
| T²Mem | 56.83 | Trained policy-internal memory; not a frozen-policy harness | [Leaderboard](https://robomme.github.io/leaderboard.html) |
| SERA | 51.38 | Selected evolved harness, compared with its own base agent at 44.38; released selected bundles are not included | `references/memory/SERA/README.md:237`; `references/memory/SERA/README.md:280`; `references/memory/SERA/README.md:302` |
| FrameSamp+Modul | 44.51 | Trained VLA memory integration | [Leaderboard](https://robomme.github.io/leaderboard.html) |
| MemER | 42.38 | Trained keyframe/subgoal adapter plus GroundSG executor | `references/memory/robomme_policy_learning/examples/robomme/subgoal_prediction/qwenvl/api_memer.py:27`; [leaderboard](https://robomme.github.io/leaderboard.html) |
| MEMI-Astra-Plan | 99.375 | Oracle reference: simulator-segmentation-derived textual perception and ground-truth subgoal controller; not an RGB-only end-to-end competitor | [Author report, §3.1](https://memi-robot.github.io/) |

\[Unverified\] The relevant conclusion for Hylo is that strong systems without additional
weight training exist, but their scores do not isolate memory. In particular, Astra-Guide
is not evidence for a frozen experience library, and direct-waypoint agents are not
controlled comparisons against Hylo's current joint-action VLA. Its released `final`
experience preset contains test-derived experience and must not initialize Hylo's clean
held-out evaluation. [Pinned README, Experience presets](https://github.com/Legend717/astra-guide-vla/blob/dc3074cc234945dfaad1ffd5e48d5da490f7e736/README.md#experience-presets).

The board's author/maintainer-reported API totals are approximately $3,000 for Astra-Guide,
$706 for MEMI-Act and $310 for Embodied-Astra, excluding local GPU compute. These are
different configurations, not cost-normalized measurements. [Leaderboard metric notes](https://robomme.github.io/leaderboard.html).

The same reported family breakdown shows why one overall winner is not a universal
memory recipe. These are configuration-level results, not causal module comparisons:

| Method | Counting | Permanence | Reference | Imitation |
|---|---:|---:|---:|---:|
| Astra-Guide | 97.0 | 97.5 | 97.0 | 97.0 |
| MEMI-Astra-Act | 98.5 | 97.0 | 98.0 | 94.5 |
| Embodied-Astra | 87.5 | 97.0 | 99.0 | 85.0 |
| SimpleMemVLA | 91.5 | 96.0 | 82.5 | 83.0 |
| SERA | 49.0 | 57.0 | 69.5 | 30.0 |

Sources: [official task data](https://robomme.github.io/leaderboard.html) and
`references/memory/SERA/README.md:286`. Oracle configurations are excluded here.

## Other Suites

| Evaluation scope | Strongest result found in the reviewed source | Important comparison limit | Primary source |
|---|---|---|---|
| MIKASA original five-task VLA subset | SimpleMemVLA 74.0; MemoryVLA++ 44.4 and MemoryVLA 41.2 in the same published comparison | Five tasks, 100 episodes/task; trained models. Neither the original 32-task RL suite nor the current 90-task VLA suite | [SimpleMemVLA, Table 3](https://arxiv.org/html/2609.05533) |
| MIKASA current 90-task VLA inventory | No verified full-90-task winner established by this review | Reference pi0.5 result is 21.1 on only 14 tasks, 20 episodes/task, different seeds from the canonical 50-episode protocol. Do not rank it against the five-task 74.0 | [MIKASA-Robo-VLA, §5.2 and Appendix D](https://arxiv.org/html/2610.00604v1) |
| RMBench nine shared tasks | BridgeVLA++ 96.0; SimpleMemVLA 94.0 | Both author reports, 100 episodes/task, different trained systems; BridgeVLA++ uses projected 3D observations. Audit modality, seeds and data before a controlled comparison | [BridgeVLA++, Table 1 and Method](https://bridgevla-plus.github.io/); [SimpleMemVLA, Table 1](https://arxiv.org/html/2609.05533) |
| RMBench original paper | Mem-0 42.0 overall, 52.8 on M(1), 28.5 on M(n) | Historical reference, no longer the strongest result found; trained execution memory and completion classifier | [RMBench, Tables 1–2](https://arxiv.org/html/2603.01229v3) |
| MEMOBench 30 tasks | Contrastive Memory Alignment 34.7 at replan step 5; unaligned memory module 31.9 | Best setting in the reviewed paper, not a live leaderboard; averages are over four memory types, not the unequal task inventory. All policies are fine-tuned | [MEMOBench, Tables 2–3](https://arxiv.org/html/2609.07047) |

SimpleMemVLA is trained separately per suite; its native-video/action integration and
prefix-cache implementation cannot simply be added to an arbitrary frozen VLA. Its
source is useful for timestamped history, temporal order and inference-cost baselines.
The 94.0 RMBench average excludes the extra Place-Mat task. [Paper, §§3–4 and Appendix A](https://arxiv.org/html/2609.05533).

The MIKASA five-task comparison is ShellGameTouch, InterceptMedium and RememberColor
with 3/5/9 candidates. The separate recurrent μVLA evaluations use different trained and
held-out task panels; their aggregates also cannot rank the full 90-task suite.
[MIKASA-Robo-VLA, §5.3 and Appendix J](https://arxiv.org/html/2610.00604v1).

MEMOBench's 51.9 oracle-memory result additionally fine-tunes and evaluates with
ground-truth memory text; it is not a deployable score or a strict upper bound for Hylo.
Checkpoint metrics measure environment predicates associated with memory operations,
not direct inspection of a memory database. The current dataset remains CC BY-NC 4.0:
use independently authored diagnostics, not copied annotations or an official-score claim.
[Paper, §5.4](https://arxiv.org/html/2609.07047);
[dataset terms](https://huggingface.co/datasets/SunSeaLucky/MEMOBench#license).

## Mechanism Evidence

The code mechanisms below are traceable but were not executed in this review.
\[Implemented\] identifies source, \[Unverified\] its transfer to Hylo, and
\[Needs model/hardware\] the corresponding runtime requirement.

| Reference | Actual mechanism | Hylo decision |
|---|---|---|
| MEMI | Annotate/evaluate/critique/revise prompts without weight updates. Act evaluation during optimization uses teacher-forced previous annotated memory; unused fields derive from model-reported reads | Adopt prompt/schema search and causal replay; additionally test self-carried memory and field-removal interventions. Do not equate reported reads with causal necessity. [Pinned iteration](https://github.com/memi-robot/memi/blob/bb6c37ce6c14bd1a204c86a91cc0cb36f565a1f0/memi/act/loop/iteration.py#L20), [policy](https://github.com/memi-robot/memi/blob/bb6c37ce6c14bd1a204c86a91cc0cb36f565a1f0/memi/act/loop/policy.py#L28), [loss](https://github.com/memi-robot/memi/blob/bb6c37ce6c14bd1a204c86a91cc0cb36f565a1f0/memi/act/loop/loss.py#L49) |
| Astra-Guide | Versioned bounded VLA delegation; observed robot-state guards can request review; stale/pending delegations are rejected | Adopt execution contracts and evidence-linked progress review, with Hylo development-only experience updates. A robot guard is not proof of object-task completion. [Pinned scheduler](https://github.com/Legend717/astra-guide-vla/blob/dc3074cc234945dfaad1ffd5e48d5da490f7e736/scripts/robomme_agent/scheduling.py#L94) |
| SERA | Typed lessons and interventions, hybrid experience retrieval, candidate lineage and separate panels | Reuse the artifact/data patterns, not a growing collection of task-name controllers. `references/memory/SERA/scripts/codex_rollout/skill_retrieval.py:108`; `references/memory/SERA/scripts/codex_rollout/self_evolve_v5.py:250` |
| HarnessPAI | Fixed program within rollout; code revision and failure-repair skill distillation between rollouts | Independently implement reusable procedures after measured applicability; no code reuse without a license. `references/memory/HarnessPAI/harnesspai/evolution/loop.py:340`; `references/memory/HarnessPAI/harnesspai/evolution/loop.py:793` |
| eMEM | SQL evidence plus semantic, spatial and temporal indexes | Backend pattern; add frame/clock/revision semantics and preserve raw evidence. It is not benchmark-solving intelligence. `references/memory/emem/emem/types.py:42`; `references/memory/emem/emem/store.py:1039`; `references/memory/emem/emem/store.py:534` |
| RoboMME memory variants | Retain images/features, temporal positions and states; internal variants change the model | Reuse external evidence organization; retain trained variants as separate reference systems. `references/memory/robomme_policy_learning/src/mme_vla_suite/shared/mem_buffer.py:24`; `references/memory/robomme_policy_learning/src/mme_vla_suite/models/integration/history_pi0.py:247` |

HarnessPAI's author-reported LIBERO-PRO 96.5 is a different benchmark and protocol:
50 seeds include 15 evolution seeds. It does not establish superiority on any of the four
memory suites. Its task-program and skill-loop designs remain relevant independently of
that score (`references/memory/HarnessPAI/README.md:93`;
`references/memory/HarnessPAI/README.md:97`).

## Design Implications

\[Docs/Interface only\] These are Hylo decisions, not upstream empirical conclusions:

1. Make **frozen-model working memory and prompt/program improvement** the main route.
   No selector fine-tuning, learned completion head or joint VLA training is required.
2. Establish a strong sampled-full-history baseline with the same reasoning model and
   executor before assuming compressed memory is better. Preserve dense source evidence
   so a mistaken interpretation can be checked later.
3. Maintain a small decision state with evidence references: identities, current beliefs,
   events, outstanding goals and procedures. Let a model propose its task-relevant fields;
   generic types enforce semantics rather than choosing a benchmark-specific policy.
4. Couple remembered state to bounded execution and completion review. Correct recall
   alone does not fix geometry, contact, timing or a mismatched action interface.
5. Report frozen-library memory comparisons, full-harness comparisons and optional
   cross-episode adaptation separately. Model strength, context budget and motor tools
   are explicit experiment axes.
6. Keep all task families on the roadmap. RoboMME is runnable first; MIKASA needs a
   compatible frozen executor/bridge, RMBench a bimanual bridge, and MEMOBench remains
   a diagnostic design reference under the current artifact boundary.

The concrete design and experiment sequence are in
[RFC-0009](../../rfcs/RFC-0009-benchmark-memory.md#integrated-plan).

## Verification Status

The [expanded method screening](memory-method-screening.md) adds robot policies, external
harnesses and general agent-memory systems, with an evaluation order based on results and
artifact availability. Its later screening work is separate from the verification scope below.

No new GPU benchmark, training, package install, dataset download or checkpoint download
was performed. Existing reference clones and their MANIFEST pins were not changed.
Primary pages and selected additional source files were saved as inert snapshots under
`runs/memory-20261103/redesign-sources/`, with URLs and content hashes in its manifest.
New source reads are pinned to MEMI `bb6c37ce6c14bd1a204c86a91cc0cb36f565a1f0`
and Astra-Guide `dc3074cc234945dfaad1ffd5e48d5da490f7e736`; these are online reads,
not new full repository audits. RMBench/MEMOBench remain paper-only studies.

The leaderboard's embedded data was parsed without executing its JavaScript. Recomputed
task means agree with the displayed rounded scores above; that checks transcription,
not rollout authenticity. A failed PDF extraction was replaced by the author's arXiv HTML
tables; MEMOBench alignment numbers are explicitly attributed to that version.
