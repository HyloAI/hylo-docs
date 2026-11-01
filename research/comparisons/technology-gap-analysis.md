# Technology Gap Analysis

> This file answers the Mission's core question: **what existing projects already cover, and what we genuinely need to research and develop ourselves.**
> Evidence comes from source-level research of 20 repositories (`research/projects/`). Every coverage item tagged [Implemented] has traceable source code; but we **have not run** any third-party code, so "covered" means "the code exists and is reasonably structured", not "validated as usable".

## 0. Conclusions first

The existing open-source ecosystem is already fairly complete along the chain of **"scoring a single VLA on a single benchmark"** (simulation, benchmarks, policy inference, batch evaluation, protocols).
The real gaps are concentrated in **cross-layer** areas:

1. **A unified and enforced Physical AI contract**: observation/action semantics, chunk execution and safety handled at the same observable checkpoint. Existing projects each have half of it; none has all of it.
2. **A replayable unified Trace**: none of the existing projects has an episode store that simultaneously records obs/action/reasoning/memory/safety/score evidence and can be replayed offline.
3. **Physical memory**: no project covers all four memory types (working/episodic/spatial/skill); general-purpose memory libraries lack spatial semantics, and spatial memory libraries lack an agent interface.
4. **A trustworthy RSI closed loop**: Zetta proved that "declarative candidates + paired statistical gate" is feasible, but it lacks validation/held-out separation, rollback, physical safety guardrails and cross-benchmark regression, and it is bound to LIBERO.
5. **A composable Reasoning × Policy × Memory × World Model Agent**: existing projects are either pure VLA (no reasoning/memory hooks) or an LLM that treats everything as a tool (loop handed to an external SDK, making safety and timing hard to control).

**These are worldcurrent's R&D priorities. Everything else is integrated via dependencies, protocol compatibility or external processes.**

## 1. Coverage matrix

Legend: ●=mature implementation, directly usable  ◐=partial implementation/needs rework  ○=design or docs only  ✕=missing 
"Our action": **USE**=use directly (dependency/external run)  **COMPAT**=protocol/format compatible  **PORT**=port and rewrite  **BUILD**=build in-house

### 1.1 Harness Core

| Capability | Best existing implementation | Coverage | Gap | Action |
|---|---|---|---|---|
| Episode execution loop | inspect-robots `rollout.py`, vla-eval runner | ◐ | No timeout/retry (IR); loop on the benchmark side (vla-eval); no reasoning/memory hooks | **BUILD** (lightweight Kernel) |
| Dual mode (Driven/Served) | — | ✕ | No project supports both "owning the loop" and "being driven by an external benchmark as a model server" | **BUILD** |
| Plugin registration | inspect-robots entry points, vla-eval `module:Class` | ● | — | **PORT** (~200 lines) |
| Event bus / lifecycle hooks | inspect-robots LogSink fan-out | ◐ | Serves logging only; no typed events | **BUILD** |
| Error classification | inspect-robots errors, vla-eval phase | ● | — | **PORT** |
| Process isolation / remote components | RPent RPC, vla-eval Docker, XPolicyLab WS | ◐ | Each does its own thing; pickle risk; no unified EnvServer | **BUILD** (EnvServer/PolicyServer) + **COMPAT** |
| Batch scheduling / sharding / resume | vla-eval SQLite work queue | ● | — | **PORT** (pattern) |
| Experiment configuration and reproducibility | inspect-robots `derive_seed`; Zetta protocol | ◐ | No versioned experiment schema, no complete run manifest | **BUILD** |

### 1.2 Environment / Benchmark

| Capability | Best existing implementation | Coverage | Gap | Action |
|---|---|---|---|---|
| Physics simulation | MuJoCo / SAPIEN / Isaac | ● | — | **USE** |
| Manipulation task suites | LIBERO, RoboCasa, ManiSkill | ● | Mutually exclusive dependencies | **USE** (separate venv/container) |
| Containerized benchmarks | vla-eval Docker images | ● | — | **USE** (bridge) |
| Unified Env contract (separate success/terminated/truncated, lazy spec, capability declaration, privileged isolation) | — | ✕ | 4 projects, 4 semantics | **BUILD** |
| Unified TaskSpec (declarative + callable, file/seed/snapshot initialization, dynamic instructions) | — | ✕ | LIBERO/RoboCasa two poles | **BUILD** |
| Scorer/Grader separation, abstention, infra accounting | inspect-robots, Zetta | ● | — | **PORT** |
| Paired statistical comparison | Zetta McNemar | ● | — | **PORT** |
| Benchmark versioning + split management | — | ○ | Only Zetta has splits, within a campaign | **BUILD** |
| Own MuJoCo task set (controllable tasks for RSI/memory research) | — | ✕ | Existing suites are not designed for memory/recovery | **BUILD** |

### 1.3 Intelligence (Policy / Reasoning / World Model)

| Capability | Best existing implementation | Coverage | Gap | Action |
|---|---|---|---|---|
| VLA inference and weights | LeRobot, openpi, vla-eval servers | ● | Weight licenses | **USE** (remote/adapter) |
| Policy contract (chunk, spec, provenance) | LeRobot `ChunkPolicySpec`/`ActionProvenance` | ◐ | Bound to LeRobot tensor format | **BUILD** (following LeRobot fields) |
| Action semantics and compatibility checks | inspect-robots ActionSemantics + vla-eval DimSpec vocabulary | ◐ | Validation only warns (vla-eval) | **PORT** + enforcement |
| Chunk execution (replanning, ensembling, RTC) | LeRobot, inspect-robots Controller | ◐ | vla-eval ensemble does not take effect; openpi only does open-loop truncation | **BUILD** (ChunkExecutor) |
| Remote inference protocol | openpi WS, vla-eval WS, LeRobot Zenoh | ● | No versioning (openpi)| **COMPAT** |
| LLM/VLM reasoning and tool calling | RPent `@tool` + Toolkit; LLM SDK | ◐ | Loop handed to external SDK, excessive permissions | **PORT** (tool layer) + **BUILD** (Reasoner contract) |
| Optimizable reasoning programs | DSPy | ● | Thread parallelism unsuitable for simulation | **USE** (offline) |
| Slow state-graph planner | LangGraph | ● | Unsuitable for control frequencies | **USE** (optional adapter) |
| Dual-frequency Reasoner↔Policy composition (event-triggered, asynchronous) | — | ✕ | No project defines it | **BUILD** |
| World Model interface (prediction, imagined rollouts, evaluation as Env) | — | ✕ | This study found no open-source harness-level abstraction | **BUILD** (interface first, models later) |

### 1.4 Memory

| Capability | Best existing implementation | Coverage | Gap | Action |
|---|---|---|---|---|
| Text fact/semantic memory | mem0, Graphiti, LangGraph Store | ● | No spatial semantics | **USE** (optional backend) |
| Bi-temporal/invalidation semantics | Graphiti | ● | — | **PORT** (schema) |
| 3D scene graph storage | Spark-DSG | ● | C++ dependency; no agent interface | **USE** (production backend) |
| Perception→object graph association/fusion | ConceptGraphs | ◐ | Batch processing, research code | **PORT** (rules) |
| Skill library + validation gate | ASPIRE | ◐ | Much of it is a prompt protocol rather than code | **BUILD** (following the protocol) |
| Unified MemoryItem / MemoryQuery (spatio-temporal first-class fields) | — | ✕ | None | **BUILD** |
| Observable retrieval (retrievals go into Trace, ratings written back) | — | ✕ | None | **BUILD** |
| Episode → Memory write policy | ReMEmbR (non-commercial), RPent file merging | ○ | — | **BUILD** |

### 1.5 Evolution (RSI)

| Capability | Best existing implementation | Coverage | Gap | Action |
|---|---|---|---|---|
| Failure diagnosis (deterministic signals + multiple hypotheses) | Zetta | ◐ | Bound to LIBERO, depends on Codex | **PORT** (schema) + **BUILD** |
| Declarative candidates (critic/recovery bundle) | Zetta | ◐ | Only two kinds: critic/recovery | **PORT** + extension |
| Prompt/program optimization | DSPy GEPA/MIPROv2 | ● | Offline | **USE** |
| LLM weight RL | agent-lightning + verl | ◐ | vLLM LLMs only; no versioning | **USE** (optional, later) |
| Shadow replay | Zetta | ● | Needs replayable Trace | **PORT** |
| Paired gate, regression | Zetta | ● | Regression skipped by default for LIBERO | **PORT** |
| Validation / held-out separation | Zetta (partial) | ◐ | No independent validation before promotion | **BUILD** |
| Candidate Registry (versions, parent chain, promote, **rollback**) | Zetta (no rollback) | ◐ | No rollback | **BUILD** |
| Protected scope (candidates cannot change safety/scoring/benchmark) | — | ✕ | None | **BUILD** |

### 1.6 Observability & Safety

| Capability | Best existing implementation | Coverage | Gap | Action |
|---|---|---|---|---|
| Unified replayable episode trace | RPent EnvState, Zetta trajectory | ◐ | Excludes reasoning/memory/safety; private format | **BUILD** (event-sourced Trace) |
| Training data export | LeRobotDataset v3 | ● | — | **COMPAT** (exporter) |
| Evaluation logs | inspect-robots EvalLog | ● | No step data | **COMPAT** (top-level structure aligned) |
| Visualization | Rerun, inspect-robots view | ● | — | **USE** |
| Action safety chain (clamp, delta limit, rotation-representation-aware) | inspect-robots Approver | ● | Programmatic API defaults to AutoApprover (allows everything) | **PORT** + **on by default, non-bypassable** |
| Sandbox for self-generated content | Zetta (code candidates disabled) | ◐ | No usable isolated runtime | **BUILD** (subprocess/container runner) |
| LLM planner permission control | — | ✕ | RPent/Zetta grant full Bash/Write permissions | **BUILD** (tool allowlist + read-only by default) |

## 2. What genuinely needs new R&D (ranked by value)

| # | R&D item | Why existing projects are insufficient | Research value | Engineering value |
|---|---|---|---|---|
| 1 | **Execution Kernel + enforced contract + single SafetyShield checkpoint** | Contracts scattered, validation only warns, safety off by default | Medium | **Very high** (the foundation of everything) |
| 2 | **Event-sourced unified Trace (replayable)** | No project records reasoning/memory/safety together and is replayable | High (data foundation for RSI and memory research) | Very high |
| 3 | **Unified Physical Memory layer (spatio-temporal first-class fields + observable retrieval)** | General memory has no spatial; spatial memory has no agent interface | **Very high** (core research direction) | High |
| 4 | **Trustworthy RSI closed loop (three-way split, protected scope, registry + rollback)** | Zetta is closest but lacks validation separation, rollback, physical guardrails | **Very high** | High |
| 5 | **Composable Reasoner/Policy/WorldModel/Memory Agent (dual frequency)** | Existing ones are either pure VLA or LLM-does-everything | High | High |
| 6 | **Unified TaskSpec + Benchmark versioning** | LIBERO/RoboCasa two poles, no split concept | Medium | High |
| 7 | **Controllable research task set (MuJoCo)**: targeting memory (occlusion, object movement), recovery (perturbation injection), long horizon | Existing suites are not designed for these research questions | High | Medium |
| 8 | **WorldModel-as-Environment**: run episodes of the same Kernel inside a world model | No harness-level abstraction | High | Medium |

## 3. Explicitly out of scope (outside v0.x scope)

- Building our own physics engine, renderer, GPU-parallel simulation.
- Building our own VLA or world model (interface first, models from external sources).
- Building our own distributed training framework (RL/fine-tuning left to LeRobot, openpi, verl, agent-lightning).
- Rewriting benchmark environments and Docker images (use vla-eval's).
- Building our own multi-vendor LLM client (use official SDKs / OpenAI-compatible endpoints).
- Operator TTY, HTML reports, video compositing (use inspect-robots view / Rerun).

## 4. Risk notes (uncertainties affecting the gap judgments)

- All coverage judgments are based on static reading, **[Unverified]**. In particular `mujoco.batch.Batch`, vla-eval's cross-shard batching, Zetta's full campaign and GEPA need minimal run validation during v0.1.
- If vla-eval's benchmark images are unusable in our GPU/driver environment, the benefit of "Served mode gets 20 benchmarks at zero cost" drops, and we would need to fall back to adapting LIBERO directly.
- Open-source harness abstractions in the World Model direction were not specifically surveyed this time (not on the Mission list); we recommend an additional survey round before v0.2 (e.g. Cosmos, Genie-style, DreamerV3/TD-MPC2-style codebases).
