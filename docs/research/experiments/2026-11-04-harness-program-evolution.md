# Harness Program Evolution

Date: 2026-11-04. Hylo now has an optional `harness.program` evolution strategy that
independently adapts HarnessPAI's program-repair and phase-scoped repair-memory design.
It does not train model weights. Mechanical integration tests pass, but **the real-model
probes produced no successful candidate**. This is an implemented experimental strategy,
not a demonstrated robot benchmark improvement.

## Scope

[Implemented] The strategy asks a reasoning model for observable phases, develops a
`solve(robot)` program on `search` cases, and distills repairs with references to failed
cases and successful replays. All selected development cases must succeed before a
candidate can enter the existing selection and independent gate. A valid program can
proceed without notes if distillation fails. Candidate approval and rollback remain owned
by the existing campaign protocol.

[Implemented] Repair recall reads active promoted lineages from configured campaigns.
Pending, rejected and rolled-back branches do not contribute notes. Notes are sealed
together with the program and evidence; the sealed digest must match the admitted
candidate's artifact digest. A note describes a repair to a gate-passing program, not an
independently validated phase skill or evidence of transfer. Retrieval currently uses
lexical overlap and phase-name matching.

[Implemented] The strategy enables automatic evaluation of completed program revisions.
Explicit submissions are not duplicated, unchanged collected source is not automatically
resubmitted, and the submission budget remains binding. Other research proposers retain
their existing explicit-submission behavior. Toolkit context now reports overridden
runtime signatures while retaining the public verb list and type descriptions.

Implementation and the workflow diagram are in
`harness/adapters/hylo-code-agents/examples/harness_evolution/README.md`.
The main sources are `src/hylo/codeagents/harness_evolution.py`, `phase_memory.py`,
`research.py` and `prompt.py` under that adapter; tests are in
`tests/test_harness_evolution.py`.

## Verification

| Check | Result | Interpretation |
| --- | --- | --- |
| Strategy and existing research, toolkit, prompt, campaign and protocol tests | 33 passed | Ten strategy cases plus 23 regression cases |
| Strategy suite after the additional artifact-replacement check | 11 passed | Includes ten cases above; 34 distinct cases across both checks |
| Scripted-model integration | Failed program, successful repair, gate, approval, recall and rollback passed | Exercises the real Hylo kernel and protocol with a scripted reasoning model |
| Real-model CPU toy probes | Five attempts, no candidate promoted | No autonomous improvement demonstrated |

The CPU toy has two instruction families, putting a red or blue block in a bin.
Its `FakeTools` perception uses privileged test-double state. This is not RoboMME,
MIKASA-Robo, or a deployment-observation-only robot test. CPU refers to the environment;
the local model service's inference hardware was not established by this probe.

## Model Probes

Each probe ran one campaign cycle, with an inactive baseline and two development cases:
`testing/toy_put_red#0` and `testing/toy_put_blue#0`. Baseline `search` and `search_val`
each contained 12 episodes. No candidate reached gate or held-out evaluation.
The existing local Ollama service supplied the model; no weights or dependencies were
downloaded for this work. Results are development feedback, not benchmark test scores.

| Attempt | Model | Change or condition | Outcome |
| --- | --- | --- | --- |
| v1 | gpt-oss:20b | Initial strategy, 12 total calls, 60,000-token budget, 60-second request timeout | No submitted program; tool-call mistakes and between-call token-budget exhaustion |
| v2 | qwen3.5:35b-a3b | 16 total calls, 180,000-token budget, 90-second request timeout | Planning request timed out; no completed model reply |
| v3 | gpt-oss:20b | First toolkit-reference fix | No submitted program; fallback context omitted types and exposed unsuitable helper methods |
| v4 | gpt-oss:20b | Correct runtime signatures with public verbs and type descriptions retained | No submitted program; model rewrote definitions without calling `submit()` and made invalid attribute assumptions |
| v5 | gpt-oss:20b | Automatic evaluation of completed revisions | Four submitted programs; each solved 0/2 development cases; no candidate |

Attempts v2-v5 used the same nominal 16-call, four-submission, four-reset and 180,000-token
limits with a 90-second per-request timeout. Planning and optional distillation count
toward the total call budget. Token limits are checked between requests and can be
exceeded by the final request. A timeout is an attempted request even when accounting
contains zero completed replies.

The fifth attempt obtained evaluator feedback, but its programs still targeted the red
block on both instructions and failed to complete either task. Correct orchestration did
not compensate for poor program synthesis. Its four submissions are adaptive revisions
on the same two cases, not eight independent benchmark samples. No repair notes were
admitted in any real-model attempt.

All attempts, including failures, remain under `runs/evolution-20261104/harness-program-v1`
through `harness-program-v5`. The [machine-readable record](2026-11-04-harness-program-evolution.results.json)
includes outcome counts, elapsed time, source records and evidence hashes. Each attempt
used its saved source revision; the final recall integrity check was added after v5.

## Limits

[Unverified] A phase plan guides generated code; there is no central interpreter enforcing
its completion predicates, per-phase budget or handover decisions. The existing runtime
still enforces overall execution and episode limits. Cross-task repair transfer and
memory-driven improvement remain unverified.

[Needs model/hardware] A frozen VLA can be called only when the configured robot toolkit
exposes that action model. This strategy does not add a generic VLA driver or automatically
wrap the existing SimpleMemVLA agent. A robot benchmark evaluation needs that integration,
a suitable reasoning model, deployment-visible observations and a predeclared evaluation
protocol. Video failure diagnosis and VLA training-data generation are not implemented.

The next performance experiment should compare this strategy with `research.llm` under
the same competent reasoning model, toolkit, development cases and model-call budget,
then ablate repair recall on disjoint task families. A successful scripted test or a
development solution alone would not establish an advantage.

## Design Sources

The [HarnessPAI source study](../projects/memory-landscape.md) pins commit
`3af7d561d531ce3e3a3884a3f801c41b8b98e2fe`. That snapshot has no project license;
Hylo independently implements the design using its own runtime, without copying upstream
source, prompts or templates. Static design references are:

- Program phases and handover: `references/memory/HarnessPAI/harnesspai/code_library/TEMPLATE.md:20`
  and `references/memory/HarnessPAI/harnesspai/code_library/TEMPLATE.md:187`.
- Development promotion and repair writeback: `references/memory/HarnessPAI/harnesspai/evolution/loop.py:793`
  and `references/memory/HarnessPAI/harnesspai/evolution/loop.py:839`.
- Phase retrieval: `references/memory/HarnessPAI/harnesspai/memory/skill/query.py:44`
  and `references/memory/HarnessPAI/harnesspai/memory/skill/query.py:112`.
- Writeback checks: `references/memory/HarnessPAI/harnesspai/memory/skill/writeback.py:389`.

The reference worktree is unpopulated. It was read with `git show` at the recorded commit,
without executing or modifying the reference repository.
