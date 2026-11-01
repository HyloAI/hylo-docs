# Executive Summary: worldcurrent Physical AI Stack

> 2026-10-30 | Basis: source-level study of 20 open-source repositories (14 assigned + 6 verified memory projects), 8 cross-project comparisons, and a runnable prototype (about 2.7k lines, 38 tests passing).
> All third-party code was only read statically; "existing implementation" in this document means the code exists and is traceable, **not that we have run and verified it**.

## 1. What overall architecture should we adopt?

**A lightweight Kernel that owns the execution loop + enforced type contracts + a single safety checkpoint + an event-sourced Trace**; everything else (simulators, benchmarks, VLAs, reasoning models, memory backends, improvement algorithms) plugs in through protocols and plugins.

```text
Evolution  ── offline: diagnose → candidate → protected scope → paired validation → held-out report-only → promotion/rollback
Benchmark  ── TaskSpec + train/validation/heldout splits; Scorer reads Trace only
Kernel     ── reset → Agent.act → ChunkExecutor → SafetyShield → step; all events written to Trace
Agent      ── Reasoner (slow, event-triggered) + Policy (fast) + Memory + [World Model]
Environment── in-process (MuJoCo; a test double for unit tests) | EnvServer out-of-process (LIBERO/RoboCasa each in own venv) | Served mode (vla-eval containers)
```

The Kernel has two run modes. In Driven mode the Kernel owns the loop itself, giving the most control. In Served mode our Agent acts as a vla-eval model server and is driven by their benchmark containers; this has the lowest cost for ecosystem reuse. Both modes keep the same safety checkpoint and Trace.

## 2. Which open-source project is the best Harness reference?

**inspect-robots is the best architectural reference**: it has typed Observation/Action, action semantics with bind-time compatibility checks, an Approver safety chain, error classification, and separates Grader from Scorer; its core depends only on numpy and is MIT-licensed.
But it has two flaws: its logs cannot replay a trial, and its programmatic API approves all actions by default.

**vla-evaluation-harness is the best ecosystem reference**: Docker images for 20 benchmarks, 17 model servers, a msgpack protocol, and SQLite-sharded resume. We choose to be **protocol-compatible** with it rather than use it as our skeleton. The reason is that its loop lives on the benchmark side, its contract is `Dict[str, Any]`, and it has no hooks for reasoning or memory.

**Zetta-Embodiment is the best RSI reference**. It has declarative candidate bundles, shadow replay, a paired McNemar gate, and a resumable state machine. But we need to fix four of its problems: no independent validation split, no rollback, use of simulator privileged information by default, and granting the LLM full permissions by default.

## 3. Which existing components can be integrated directly?

| Component | Approach |
|---|---|
| MuJoCo | PyPI dependency (already used in the prototype) |
| vla-eval benchmark images + model servers | Protocol-compatible + run as external containers |
| openpi policy servers | WebSocket wire-protocol compatible (no import) |
| LIBERO / RoboCasa / ManiSkill | Each runs in its own venv, connected via EnvServer |
| LeRobot | Optional policy adapter + LeRobotDataset v3 export |
| inspect-robots ActionSemantics / compat / Approver | Port (MIT, with attribution) |
| RPent `@tool` + Toolkit dispatch | Port (Apache-2.0, with attribution) |
| Zetta gate / critic schema | Borrow the design and rewrite |
| DSPy (GEPA), LangGraph | Optional adapter packages (offline candidate generation / slow planner) |
| Spark-DSG, mem0, Graphiti | Optional memory backends |

## 4. Which capabilities should we build ourselves?

1. **Execution Kernel and enforced contracts**: control-mode incompatibility is an error, not a warning; `success`, `terminated` and `truncated` are kept separate; simulation errors must be reported, never silent.
2. **SafetyShield as the single checkpoint**: actions produced by VLAs, LLMs, recovery skills and RSI candidates must all pass through it.
3. **A replayable unified Trace**: covers obs, action, decision, memory, safety, score and privileged state; privileged state is only for the Scorer and diagnostics.
4. **A unified Physical Memory layer**: time intervals and poses with frame_id are first-class fields; stale facts are invalidated rather than deleted; retrieval is observable; skill writes go through a validation gate.
5. **A credible RSI loop**: train, validation and held-out three-way split, a defined protected scope, and a Registry that supports promote and rollback.
6. **A composable Agent**: Reasoner and Policy cooperate at two frequencies; a World Model can be wrapped as an Environment for evaluation.
7. **Our own research task suite**: based on MuJoCo, covering three task categories: memory, disturbance recovery, and long-horizon.

**Explicitly out of scope**: physics engines, VLA training frameworks, rewriting benchmark environments, LLM clients, visualization tools.

## 5. How many repositories should the first version have?

**Superseded 2026-10-31** by [design/repository-structure.md](design/repository-structure.md) (five code repositories on one base). Original decision — **one, for now** (2026-10-30): the existing `dyna-harness` repository is a multi-package uv workspace: `packages/` (wc-core, wc-eval, wc-agents, wc-memory, wc-evolve, worldcurrent-cli), `adapters/` (wc-env-mujoco, then LIBERO), and `physical-ai-research/` (this research workspace, now `docs/`). An import-lint test enforces the layering. Packages are split into separate repositories later, when an adapter gets external maintainers, needs different CI (GPU, real robot, Isaac) or carries a different license.

## 6. Which module should the first phase start with?

**`wc-core`**, including contracts, Kernel, SafetyShield, Trace and the EnvServer protocol, while building the **MuJoCo in-house task suite** in parallel.

Rationale: every other layer depends on these contracts, and the prototype has already validated their shape. In week 4 we will use the openpi client for a "contract stress test" to expose contract defects before touching a real VLA.

## 7. What exactly is the recommended MVP?

**v0.1 minimal credible loop**, 3 engineers for about 10-11 weeks (about 32 person-weeks); see `design/mvp-v0.1.md` for details:

- **P0**: wc-core; SafetyShield (port of the Approver chain); EnvServer; a test-double environment and the conformance kit; MuJoCo task suite `wc-mj-v0` (reach, push, disturbance recovery, occlusion memory); wc-eval (splits, Scorer, resume, paired statistics); baseline Agent; ComposableAgent; swappable Reasoner (rules + OpenAI-compatible LLM); SQLite episodic/spatial memory; offline diagnosis and config-patch candidates, gate, Registry and rollback; CLI.
- **P1**: vla-eval bridge (LIBERO); openpi remote policy; LIBERO EnvServer; LeRobot v3 and Rerun export; shadow replay.
- **Definition of done**: the full Execute→Promote/Rollback flow runs end to end on MuJoCo plus one external benchmark; four protocol versions are frozen; a technical report is produced that includes baselines, a memory ablation and one RSI round.

## Key findings (from source code, not READMEs)

- vla-eval's `action_ensemble` does not actually take effect (the server only pushes a new chunk when the buffer is empty), and protocol versions are exchanged but never checked. Its leaderboard numbers were extracted from papers by an LLM, not produced by running this harness.
- RPent's LIBERO results are not zero-shot: during evaluation the agent reads the successful seed-0 trajectory of the same task.
- Zetta exposes simulator privileged evidence to the critic by default; its 90.8% relies on a frontier LLM plus privileged state and should not be considered transferable to real robots.
- agent-lightning v1.0.2 is a rewrite: LitAgent, Store, Tracer and APO from the README do not exist in that version.
- inspect-robots does not depend on inspect_ai; it only re-creates its concepts in its own code.
- LIBERO and RoboCasa have mutually exclusive dependencies (Python 3.8 + robosuite 1.4, versus Python 3.11 + robosuite ≥1.5.2) and cannot be placed in the same process.
- **License risks**:
  - XPolicyLab's `policy/` mixes non-commercial, MPL and unlicensed sub-projects; vendoring it wholesale is prohibited.
  - ReMEmbR is non-commercial only.
  - ManiSkill assets are CC BY-NC.
  - π0/π0.5 weights are likely bound by the Gemma ToU; legal review is required before hosting inference externally.

## Design decisions (reviewed 2026-10-30)

1. **Repository**: single repository with multiple packages, split later (amended from the two-repository proposal). See RFC-0001 D7.
2. **The Kernel owns the loop**: accepted. A Served-mode adapter keeps vla-eval compatibility.
3. **In-house Trace format**: accepted. LeRobotDataset, Rerun and inspect-robots formats are export targets.
4. **Model-generated executable code as an RSI candidate**: **pending**. v0.1 enables declarative config-patch candidates only.
5. **First external benchmark**: **LIBERO** (vla-eval bridge first, direct EnvServer second).
6. **Contracts**: **pydantic v2** (amended from dataclasses): frozen models, `extra="forbid"`, JSON Schema export; measured overhead +5 µs per control step.
