# MVP v0.1: Minimal Credible Loop

!!! note "Historical scope"
    This is the original v0.1 planning snapshot. For current implementation boundaries, see
    [Architecture](overview.md); for current priorities, see [Roadmap](roadmap.md).

> Goal: with the fewest components, prove that the **Execute → Trace → Score → Diagnose → Improve → Validate → Promote/Rollback** loop holds in real simulation (MuJoCo) and on one external benchmark, with all actions passing through the same safety checkpoint.
> Non-goals: full RSI, an in-house world model, distributed training, real robots.
> Starting point: the interface prototype (about 2.7k lines, 38 tests; removed 2026-10-31, in the git history) has validated the interface shape of the test double + MuJoCo + remote Env + memory + offline improvement loop.

## 1. Feature List and Priorities

### P0: without these it is not v0.1

| # | Feature | Acceptance criteria | Estimate (person-weeks) |
|---|---|---|---|
| P0-1 | **hylo-core**: contracts, Kernel, ChunkExecutor, error taxonomy, EventBus, Trace v0.1 (JSONL + blob), Registry, Config/Manifest | All prototype tests migrated and passing; core depends only on numpy+pyyaml; import-lint passes | 3 |
| P0-2 | **SafetyShield**: port the inspect-robots Approver chain (MIT, with attribution); mandatory guards; in real-robot mode, any modification aborts | Guard conformance tests: NaN aborts, out-of-bounds is clipped, extra guards cannot loosen bounds, rotation representations are not clipped per dimension | 1 |
| P0-3 | **EnvServer** protocol v0.1 (two transports: stdio + WebSocket) | Remote and in-process episodes with the same seed match step by step; protocol version mismatch is rejected; no pickle | 1 |
| P0-4 | **Test-double environment** (unit tests only) + conformance kit | Any Env adapter can self-check with `hylo conformance env <ref>` | 1 |
| P0-5 | **MuJoCo adapter + first-party task set `hylo-mj-v0`**: reach, push (object contact), disturbance recovery, occlusion memory (object briefly visible) | ≥ 4 tasks, each with train/validation/heldout seed tables; snapshot restores exactly; divergence → infra_invalid; 100 episodes < 60 s on CPU | 3 |
| P0-6 | **hylo-eval**: Benchmark/split, Scorer (success/safety/steps/latency), EvaluationRunner (sequential + SQLite queue resume), EvalLog, paired McNemar | Resuming after interruption does not repeat completed episodes; Scorer can re-score historical Traces independently of env/agent | 2 |
| P0-7 | **Baseline Agents**: scripted controller, random; **ComposableAgent** + Reasoner protocol + rule-based Reasoner | The composed Agent's decision/retrieval events fully enter the Trace | 1.5 |
| P0-8 | **Swappable Reasoner: LLM (OpenAI-compatible endpoint)** structured output → Decision; records model/tokens/latency/prompt hash | Within the same experiment config, changing only `agent.params.reasoner` switches between rule-based and LLM; when the LLM is unavailable, the episode abstains with `error` instead of crashing | 1.5 |
| P0-9 | **Local Episodic + Spatial Memory** (SQLite) + WorkingMemory | Memory conformance: dedup, key invalidation, as_of, radius, forget; on the occlusion-memory task, the success-rate difference between with-memory and without-memory is significant (McNemar p<0.05) | 1.5 |
| P0-10 | **Offline Reflection + Candidate Validation**: diagnostic bucketing, config-patch candidates, protected scope, gate (paired + regression + safety), Registry (promote/rollback/ledger), held-out report-only | `hylo evolve` completes one round on `hylo-mj-v0`; adversarial candidates are rejected; rollback works | 2 |
| P0-11 | **CLI**: `hylo run / eval / evolve / trace show / conformance` | Every example command in the docs is executed in CI | 1 |
| | **P0 total** | | **≈ 19** |

### P1: complete before the v0.1 release if possible

| # | Feature | Acceptance criteria | Estimate |
|---|---|---|---|
| P1-1 | **External Benchmark Adapter: vla-eval bridge (Served mode)** | Run ≥ 1 suite end to end using vla-eval's LIBERO image; our Agent acts as the model server; Trace records `mode=served` | 2 |
| P1-2 | **openpi remote Policy client** (WS wire-protocol compatible) | Complete handshake, inference and chunk execution against an openpi server (or protocol simulator) | 1 |
| P1-3 | **LIBERO EnvServer (py3.8 container)** direct adaptation (BDDL → Predicate, init states → InitStateRef) | The same LIBERO task has consistent success rates on the bridge path and the direct-adaptation path (± statistical error) | 2 |
| P1-4 | Trace export: LeRobotDataset v3, Rerun | Exported data can be loaded by LeRobot (schema validation) | 1.5 |
| P1-5 | Shadow replay (for Critic-rule candidates) | Recall/FP report of the new rule on the parent's Traces | 1.5 |
| | **P1 total** | | **≈ 8** |

### P2: explicitly deferred to v0.2+

RoboCasa/ManiSkill EnvServer; async Reasoner; LangGraph Reasoner adapter; DSPy GEPA generator; Skill Memory and the skill validation gate; Spark-DSG spatial backend; World Model interface implementation; Batched env; real-robot adapters; distributed evaluation.

## 2. Key Interfaces (v0.1 freeze scope)

The following protocols are frozen at the v0.1 release (changes within `0.x` require an RFC):

| Interface | Document |
|---|---|
| `Environment`, `EnvSpec`, `Observation`, `StepResult`, `ActionSemantics` | `interfaces/environment.md` |
| `TaskSpec`, `TaskInstance`, `Benchmark`, `Scorer`, `Score` | `interfaces/benchmark.md` |
| `Agent`, `AgentSpec`, `EpisodeContext`, `ActionChunk` | `interfaces/agent.md` |
| `Reasoner`, `Decision` | `interfaces/reasoner.md` |
| `MemoryItem`, `MemoryQuery`, `MemoryStore` | `interfaces/memory.md` |
| `Candidate`, `CandidateRegistry`, Gate rules | `interfaces/improvement.md` |
| `hylo.experiment/v0.1`, `hylo.trace/v0.1`, `hylo.evallog/v0.1`, `hylo.envserver/v0.1` | `experiment-schema.md`, `execution-lifecycle.md` |

## 3. Testing and Acceptance

| Layer | Content | Threshold |
|---|---|---|
| Unit | ≥ 85% line coverage per package; invariants of contract types | CPU CI < 5 min |
| Conformance | Env / Agent / Memory / Scorer conformance suites | All first-party adapters pass |
| Determinism | Two runs with the same seed on MuJoCo (single-threaded) and the test double produce bit-identical Trace actions | R2 |
| End-to-end | (1) `hylo eval` runs the baseline on `hylo-mj-v0` validation; (2) `hylo evolve` completes one round and produces a ledger; (3) one LIBERO suite runs end to end via the bridge | Nightly sim CI |
| Safety | Adversarial test set: NaN, out-of-bounds, overspeed, rotation out-of-bounds, candidates attempting to modify safety, Agents attempting to read privileged state | All intercepted and recorded |
| Research usability | Memory task: significant difference between with and without memory; recovery task: post-disturbance success rate is measurable | Report goes into `hylo-research/experiments/` |

**v0.1 Definition of Done**: all P0 complete and passing the thresholds above; P1-1 complete; the four protocol versions in the docs frozen; one internal technical report (baseline, memory ablation, one RSI cycle).

## 4. Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| vla-eval images unusable on our GPU/driver/headless environment | Medium | P1-1 delayed | Validate first on a standard GPU machine; P1-3 direct adaptation as an alternative path |
| LIBERO rendering (EGL) and py3.8 container build | Medium | P1-3 delayed | Reuse the approach of vla-eval's Dockerfile; first get it running without images (state-only) |
| v0.1 contract design needs major changes after integrating a real VLA | Medium | High | Move P1-2 up to week 4 as a "contract stress test"; complete before freeze |
| LLM Reasoner latency/cost makes evaluation too slow | High | Medium | Rule-based Reasoner as default; LLM only on small splits; caching (prompt hash) |
| MuJoCo multithreading/version causes nondeterminism | Low | Medium | Single-threaded by default; manifest records the mujoco version; R2 tests |
| Simple MuJoCo tasks make RSI conclusions meaningless | High | Medium | State explicitly that v0.1 only validates the process; v0.2 does real RSI on LIBERO/RoboCasa |
| Scope creep (doing world models/skill learning early) | High | High | The P2 list in this file is the "not doing" list; changes require an RFC |
| Weight/asset licensing | Medium | High | Registry enforces `weights_license`; assets are not redistributed (see license-matrix) |

## 5. Effort and Staffing

- P0 ≈ 19 person-weeks, P1 ≈ 8 person-weeks, integration/docs/buffer ≈ 20% → **about 32 person-weeks**.
- Recommended **3 engineers × 10–11 weeks**: A (Core + Safety + Remote + CLI), B (MuJoCo task set + Bench + bridge/LIBERO), C (Agents + Reasoner + Memory + Evolve).
- Week 4 milestone: P0-1..4 complete + openpi client prototype (contract stress test). Week 8: all P0 complete. Weeks 10–11: P1 + technical report.

## 6. Dependency List (v0.1)

| Dependency | Purpose | Location |
|---|---|---|
| numpy, pyyaml | core | hylo-core |
| mujoco ≥ 3.1 | simulation | hylo-env-mujoco |
| websockets, msgpack | remote protocol (vla-eval / openpi compatible) | hylo-core[remote], bridge |
| openai (or httpx) | LLM Reasoner | hylo-reasoner-llm |
| pytest | testing | dev |
| Docker, NVIDIA Container Toolkit | LIBERO / vla-eval containers | sim CI |
