# Experience Memory and Skills for a Frozen-VLA Robot Stack

> Survey date: 2026-10-30. Complements `memory-landscape.md` (spatial / episodic infrastructure, skill libraries
> cloned under `references/memory/`). This note covers what that survey did not: **memory of the agent's own
> experience** (what worked, what failed, why) and how it can improve a frozen VLA at test time.
> Sources are papers, project pages and READMEs read on the web; nothing was cloned or run for this note.
> Tags: **[Paper]** numbers as reported by the authors, not reproduced; **[Code]** a public repository exists;
> **\[No code found\]** none located.

## 1. Two families

| Family | Unit stored | Consumer | Representative work |
|---|---|---|---|
| **Action memory** (non-parametric, low level) | successful (observation key, action chunk) segments | the policy's sampler | Retrieve-then-Steer, OnEvoMemory, MemER |
| **Lesson memory** (language, high level) | distilled strategies and pitfalls with usage counters | planner / prompt / improvement proposer | ReasoningBank, ExpeL, ACE, REFLECT |
| (Procedural skills) | verified reusable procedures with versions | planner / tool use | Voyager, ASPIRE, Agent Skills (SKILL.md) |

## 2. Action memory

### Retrieve-then-Steer (arXiv 2605.10094) [Paper] \[No code found\]
Online success memory for **generative** VLAs (flow matching / diffusion), policy weights frozen.
- **Write**: each episode is buffered; only episodes judged successful are written, and only the prefix
  before the progress peak. Success is judged by a pretrained progress critic (VLAC), no human labels.
- **Key**: the VLA's own visual patch tokens, 2x2 pooled, flattened, concatenated over views, normalised.
- **Retrieve**: cosine top-K (K = 10) with a similarity floor; drop inconsistent candidates by median
  pairwise multivariate DTW between their action chunks.
- **Aggregate**: softmax-over-similarity weights; weighted mean for positions, geodesic mean for rotations,
  weighted vote for a discrete gripper.
- **Steer**: start the flow sampler from an intermediate point `x_t0 = (1 - t0) a_elite + t0 eps` and integrate
  the unchanged velocity field from t0 to 0, so the current observation still conditions the result. `t0` is a
  sigmoid of retrieval confidence (high similarity + low DTW dispersion -> small t0, strong guidance; no valid
  retrieval -> the base sampler).
- **Results**: LIBERO-10: pi0 81.6 -> 84.4, pi0.5 92.4 -> 94.4; SimplerEnv CogACT 75.8 -> 79.5; real
  bimanual tasks +6 to +12 points. Inference cost 1.10x.
- **Ablations that matter for us**: direct replay of the retrieved chunk *hurts* (87.8 vs 92.4 base);
  output interpolation is weaker than prior-initialised sampling (93.0 vs 94.4); **unverified memory hurts**
  (87.6, below the no-memory baseline); success prefixes beat full successful trajectories (94.4 vs 91.8);
  a FIFO memory of 5k entries is as good as unlimited.

### OnEvoMemory (arXiv 2608.08749, ECCV-W 2026) [Paper] \[No code found\]
Value-guided memory for a frozen pretrained policy (QwenOFT): short-term FIFO + elite bank (high value) +
transition bank (large value change), read through gated cross-attention into the frozen action decoder;
only the value estimator and memory modules are trained. LIBERO-Long-10: 86.2 -> 88.6 (offline memory)
-> 90.2 (one round of online rollouts, 20 per task). Needs training memory modules; no ablations reported.

### MemER (ICLR 2026, arXiv 2510.20328) [Paper]
A high-level policy learns to select task-relevant keyframes from its own history and conditions a VLA on
them; targets non-Markovian tasks (object permanence), which LIBERO-10 mostly is not.

## 3. Lesson memory

### ReasoningBank (Google, ICLR 2026, arXiv 2509.25140) [Paper] \[Code: google-research/reasoning-bank\]
After each task an LLM judge labels the trajectory success/failure (no ground truth needed, robust to judge
noise) and extracts memory items `{title, description, content}`: strategies from successes, *preventative
lessons from failures*. Retrieved into context before acting; consolidation is plain append. MaTTS turns
extra test-time compute into better memories by contrasting several trajectories of the same task.
WebArena +8.3, SWE-Bench-Verified +4.6 over memory-free agents.

### ExpeL (AAAI 2024) [Code: LeapLabTHU/ExpeL]
Collect success and failure trajectories, extract cross-task insights into a list edited with
ADD / UPVOTE / DOWNVOTE / EDIT, and at inference use insights plus retrieved successful examples.

### ACE, Agentic Context Engineering (arXiv 2510.04618) [Code: ace-agent/ace, Apache-2.0]
A playbook of sectioned bullets `[slug-00042] helpful=3 harmful=1 :: advice`; Generator / Reflector / Curator
roles; *incremental delta updates* instead of rewriting (avoids "context collapse"); dedup at similarity 0.9.

### REFLECT (CoRL 2023) [Code: real-stanford/reflect]
Hierarchical summaries of multimodal robot experience feed an LLM that explains failures and plans a
correction; RoboFail dataset. RoboFailRing (2026) adds retrieval of past failures for online detection.

## 4. Procedural skills
Voyager (code skills + embedding retrieval) and ASPIRE (write gating, usage-feedback scores, version hashes)
are covered in `rsi-voyager.md` and `memory-landscape.md`. The 2026 Agent Skills / SKILL.md line (surveys
arXiv 2602.12430, 2605.07358; TMLR "Dynamic Agent Skills", arXiv 2607.10113) treats skills as lifecycle-managed,
verified artifacts with progressive disclosure; robotics coverage is still mostly SayCan / RoboGen-era.

## 5. Lessons for Hylo

1. **Write only verified experience.** Both robot papers show unverified memory is worse than none. We have
   ground-truth success in simulation; outside simulation the writer needs a judge (VLM success detector).
2. **Steer, don't replay.** Initialise the flow sampler from the memory prior at an intermediate time; keep
   the observation-conditioned velocity field in charge. This composes with our seeded-noise steering.
3. **Two layers, two consumers.** Action memory feeds the sampler every chunk; lesson memory feeds the
   planner and the improvement proposer (our LLM steering proposer already reads diagnoses; lessons make
   them cumulative across cycles).
4. **Counters, not rewrites.** Lessons carry helpful / harmful counts updated from outcomes (ExpeL, ACE),
   with evidence links to episode ids; incremental edits only.
5. **Protocol hygiene (ours, not from the papers).** Paired, parallel evaluation needs reproducibility, so a
   memory is built from development splits and *frozen* (content digest in the run manifest) for gate
   evaluation; online writing is a deployment mode, and its order dependence must be declared.

## Sources
- Retrieve-then-Steer: https://arxiv.org/abs/2605.10094
- OnEvoMemory: https://arxiv.org/abs/2608.08749
- MemoryVLA: https://github.com/shihao1895/MemoryVLA
- Awesome-Memory-for-Robotics: https://github.com/Everloom-129/Awesome-Memory-for-Robotics
- ReasoningBank: https://research.google/blog/reasoningbank-enabling-agents-to-learn-from-experience/
- ExpeL: https://arxiv.org/abs/2308.10144
- ACE: https://github.com/ace-agent/ace
- REFLECT: https://github.com/real-stanford/reflect
- RoboFailRing: https://github.com/DynamicPoet/RoboFailRing
- Agent Skills survey: https://arxiv.org/abs/2602.12430 ; Dynamic Agent Skills: https://www.alphaxiv.org/abs/2607.10113
- Benchmarks: FindingDory https://arxiv.org/abs/2506.15635 ; LIBERO-Mem https://arxiv.org/abs/2511.11478 ;
  EmbodiedMemory-Bench https://arxiv.org/abs/2609.28236
