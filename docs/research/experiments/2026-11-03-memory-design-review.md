# Memory Design Review

Date: 2026-11-03. This reviews [RFC-0009](../../rfcs/RFC-0009-benchmark-memory.md)
after the completed [RoboMME diagnostic pilot](2026-11-03-robomme-memory-pilot.md).
It is a design review, not a new experiment or benchmark result.

## Scope

The user requested multiple reviewers, including Opus, to challenge completeness and
usefulness. Three native sub-agents independently reviewed architecture, learning and
evaluation, then exchanged objections. They used the parent model; this is role diversity,
not three distinct model families. The primary agent checked their findings against local
source and reconciled the development plan. Local reference repositories were not executed
or modified.

Claude Code was located in an IDE extension directory outside `PATH`. A separate
tool-disabled review was requested with `--model opus`, using the RFC, pilot report and
three implementation files supplied as numbered text. The returned usage metadata lists
`claude-opus-5-5` and auxiliary `claude-haiku-5-5` usage. The Opus response explicitly
limits its claims to that snapshot; it did not independently inspect the reference clones.
Its critique was then sent to all three native reviewers for a second exchange.

## Findings

The roadmap covers the major memory demands, but it is not yet a complete trainable
algorithm. The storage and evidence foundations are useful. The revised model-managed
system remains a proposal whose utility must be tested separately from the earlier
heuristic bundle. No reviewer discussion establishes benchmark superiority.

| Priority | Finding | Evidence | Decision |
|---|---|---|---|
| P0 | The central query-conditioned reader is not implemented | Current frame retrieval takes a temporal cutoff; report selection uses early/latest topics and lexical overlap. `harness/packages/hylo-memory/src/hylo/memory/frames.py:39`; `harness/packages/hylo-memory/src/hylo/memory/visual.py:99` | Build a replaceable budgeted selector/reader that returns original evidence IDs and can reopen ordered clips |
| P0 | Learning targets and labels are underspecified | The RFC's learning table lists candidate methods, not an executable training recipe. [Learning and Evolution](../../rfcs/RFC-0009-benchmark-memory.md#learning-and-evolution) | First learn reversible query-conditioned evidence ranking and sufficiency; define causal examples and independent labels before training |
| P0 | Correct memory may not translate into executable commands | The current visual plan exposes a short subgoal and up to two image points. `harness/packages/hylo-memory/src/hylo/memory/visual.py:35` | Test permitted-evidence rescue and command feasibility separately; diagnose reader/grounding/control interactions |
| P0 | Delayed interpretation is incompatible with the current event-only contract | `MemoryEvent` has one event time; append rejects decreasing time. `harness/packages/hylo-core/src/hylo/core/episode_memory.py:24`; `harness/packages/hylo-memory/src/hylo/memory/episode.py:75` | Add availability-aware interpretation revisions without rewriting sensory evidence or duplicating physical events |
| P1 | Six capabilities can become six expensive modules before utility is known | [Shared Capabilities](../../rfcs/RFC-0009-benchmark-memory.md#shared-capabilities) | Treat capabilities as a coverage map. Start with archive, selector/reader and existing executor; add modules at measured bottlenecks |
| P1 | Future paired statistics could exclude candidate-caused failures | Paired analysis excludes statuses beyond success/fail/timeout, although per-attempt rates retain them. `harness/examples/memory/robomme/summarize.py:33` | Fix before the next confirmatory run; retain agent failures as failures and predeclare unrelated infrastructure handling |
| P1 | Promotion principles are not a complete campaign protocol | [Promotion Protocol](../../rfcs/RFC-0009-benchmark-memory.md#promotion-protocol); `harness/packages/hylo-evolve/src/hylo/evolve/protocol.py:69`; `harness/packages/hylo-evolve/src/hylo/evolve/protocol.py:151` | Specify one main comparator, practical effect target, sample allocation, repeated-candidate accounting and family regression uncertainty |

\[Implemented\] The source pointers above establish the current interface and analysis
behavior, not the proposed repairs. \[Docs/Interface only\] The decisions are specifications
for subsequent implementation. \[Unverified\] Their performance effect has not been run.
\[Needs model/hardware\] Learned selectors and closed-loop benchmark comparisons require
model inference/training and the authorized remote runtime.

## Disagreements

The learning and evaluation reviewers initially favored an execution or memory "ceiling"
experiment. The architecture reviewer challenged that name and ordering: oracle evidence
or commands can be unavailable, distribution-shifted or interact poorly with a nonlinear
planner. They do not establish a strict achievable upper bound. The reviewers agreed to
use **bottleneck probes**, performed alongside the minimal reading implementation rather
than as a reason to postpone it.

They also distinguished necessary causal contracts from a complete belief graph. Immutable
evidence IDs, available-at times and auditable returned bundles are needed immediately.
Rich entity hypotheses, learned trackers and full revision machinery can be introduced as
their corresponding asynchronous/event components are built. The current synchronous
journal should not be presented as already supporting those semantics.

Opus challenged the conservative sequencing: begin trained outer-module development
early, and test a joint grounded-subgoal/keyframe predictor instead of assuming retrieval
alone will fix the observed errors. This is accepted as a **competing candidate**, not a
proven superior architecture. The native reviewers agreed that a zero-shot selector need
not succeed before supervised learning begins. They required a trained-planner/uniform-
history control so improved grounding is not mislabeled as improved memory.

The primary agent and native reviewers rejected several stronger claims in the first
Opus response:

- The bundled pilot does not establish that the ledger caused its wins. A one-frame
  reset prefix does not eliminate later report/gallery effects. Per-task differences
  suggest ablations, not a causal decomposition.
- A reference-command success rate below an arbitrary threshold cannot establish that
  memory cannot improve that family. These are interventions on a particular stack,
  not strict ceilings.
- Validation IDs 0–7 would include the already inspected 0 and 3. That panel cannot be
  presented as fresh confirmation for this revised design.
- Confidence on observing a model emission is not confidence in its physical claim.
  Current report storage preserves that distinction; typed downstream interpretation
  needs protection, rather than reclassifying every report count as a physical count
  (`harness/packages/hylo-memory/src/hylo/memory/visual.py:79`).
- A fixed confidence-interval width or full-suite runtime does not follow from 128 pairs
  or a small pilot's average latency. Precision depends on discordance and task variation;
  new-task runtime and selection cost must be measured.
- The withdrawn count-template guard and the evaluated event monitor are different
  artifacts. This review does not reactivate the user-rejected candidate.

Opus also correctly identified the frame store's repeated `max(self._frames)` scan and
in-memory full-image retention as scaling concerns (`harness/packages/hylo-memory/src/hylo/memory/frames.py:26`).
Its separate claim that report selection recomputes the entire snapshot was not supported:
the journal returns a cached incremental digest (`harness/packages/hylo-memory/src/hylo/memory/episode.py:161`).
These checks illustrate why reviewer agreement or model confidence does not replace source
verification.

In its second response, Opus accepted the corrections on bundled-result attribution,
the withdrawn guard, contaminated validation IDs, oracle ceilings, precision/runtime
estimates and keeping MIKASA on the roadmap. It retained a substantive disagreement:
the fixed planner may mishandle even correctly retrieved evidence, so reranker-first
must not become a reason to postpone learning a better outer planner.

Its revised proposal uses a shared outer VLM adapter with evidence-selection and native
subgoal objectives, evaluated both through the existing planner and through its learned
subgoal output. This is a credible candidate, subject to actual model-interface and
training feasibility. The accepted crossed comparison is recorded in
[Review Decisions](../../rfcs/RFC-0009-benchmark-memory.md#review-decisions).

The primary agent did **not** adopt the second response's claim that an interval including
zero falsifies generalization. That result can simply be underpowered. Nor does one
unchanged output under cue substitution prove exclusive reliance on priors. Counterfactual
probes need valid alternative cues, relevance checks and aggregate outcomes. For a
confirmatory stopping conclusion, compare the effect interval with a predeclared minimum
useful gain; otherwise record uncertainty or an engineering resource-allocation decision.

## Minimal System

\[Docs/Interface only\] The next system is:

`permitted observation archive → query-conditioned evidence selection → ordered evidence bundle → reader/subgoal → frozen executor`

The archive retains original images. A frozen-VLM selector supplies the first baseline;
a learned outer reranker is a replaceable candidate. Neither requires VLA parameter
updates. A model-directed selector without the released adapter is a structural baseline,
not a MemER reproduction; the pinned upstream code loads an adapter
(`references/memory/robomme_policy_learning/examples/robomme/subgoal_prediction/qwenvl/api_memer.py:27`).

Each supervised example contains episode/scene identity, decision time, question, current
observation, available candidate evidence IDs, relevant frames or ordered bundles, hard
wrong-object/wrong-time negatives and an insufficient-evidence label. Split scenes and
episodes before deriving decision prefixes. Do not use a planner's own explanation as
ground truth or broadcast terminal task success to every selected frame.

The initial objective combines relevant-versus-irrelevant ranking, multi-frame evidence
coverage/order and sufficiency prediction. Compare evidence retrieval, grounded answers
and closed-loop outcomes separately. If retrieval improves but answers do not, inspect
the reader; if answers improve but actions do not, inspect grounding and execution.
An unchanged answer after removal of an essential cue is a reason to investigate shortcut
use, not by itself proof of its cause.

In parallel, test a trained outer grounded-subgoal predictor with evidence selection.
Cross the existing and trained planners with uniform and learned evidence selection;
keep the VLA fixed. Train with both evidence distributions so the uniform control is
not an unsupported inference format. Supervision combines native command prediction,
evidence coverage/order and insufficiency labels, including delayed-cue examples.
This jointly addresses grounding and selection, while the crossed controls identify
which component contributed. A learned joint model may be the better system even when
its gain is not a pure memory gain; report that distinction rather than forbidding it.

## Next Comparison

1. Use new development episodes spanning memory families. Independently identify decisive
   clips within the agent's permitted pre-decision history. Compare ordinary retrieval,
   uniform/random retrieval and curated evidence at equal input quotas. Reference-command
   feasibility is a separate diagnostic through the supported action interface.
2. Implement the replaceable reader/selector while these probes run. Retain all selector
   candidate access and inference cost. Equal final frame counts do not imply equal total
   compute when one method reads the full archive to select them.
3. Freeze one candidate against a primary uniform-history comparator. Recent-window and
   the historical heuristic are secondary controls. Fix planner, grounding, executor,
   action tools, resolution and declared budgets; report success/cost curves if total
   budgets differ.
4. Treat inspected pilot val IDs 0 and 3 as development evidence for subsequent designs.
   Keep final test metadata untouched. Select a fresh validation panel and sample size
   from development discordance, desired practical effect and a predeclared statistical
   policy. A small exploratory panel is not a promotion gate.
5. Keep every family visible. An underpowered regression interval is inconclusive, not
   evidence that the family is protected. Failure of a candidate triggers diagnosis and
   a new development revision, not removal of difficult tasks from the scorecard.

The completed pilot remains eight paired episodes, with three memory wins and no losses,
one-sided exact McNemar `p=0.125`, and unequal input/inference cost. It supports further
investigation of that archived heuristic bundle. It does not validate the revised learned
architecture. There were no invalid pairs, so the identified future analysis-policy issue
does not change those historical numbers ([pilot results](2026-11-03-robomme-memory-pilot.md#evaluation-status)).

## Review Artifacts

The local review directory is `runs/memory-20261103/design-review/`. Review prompts and
model responses are evidence of the discussion only; they are not benchmark artifacts or
independent validation of source claims. The primary agent remains responsible for the
accepted decisions and for separating proposals from measured behavior.

`opus-prompt.txt` and `opus-followup-prompt.txt` retain the exact supplied contexts;
`opus-result.json` and `opus-followup-result.json` retain CLI responses and model-usage
metadata. The corresponding `opus-review.md` and `opus-followup-review.md` are extracted
response text, including claims rejected above. They should not be read as endorsed
source findings. No model weights, benchmark results or runtime implementation changed
in this review.
