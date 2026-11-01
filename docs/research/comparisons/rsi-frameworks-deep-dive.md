# RSI Frameworks Deep Dive: How the Best Self-Improvement Systems Are Built

> Second RSI study (2026-10-30). Source-level reports: `research/projects/rsi-{dgm,sica,openevolve,shinkaevolve,gepa,adas,voyager,eureka,vla-steering,rlinf,simplevla-rl}.md`, plus the earlier `zetta-embodiment.md`, `agent-lightning.md`, `dspy.md`, `memory-landscape.md` (ASPIRE).
> Everything below is from static reading; reported gains are the authors' numbers, not reproduced by us unless stated.

## 1. The landscape in one table

| Family | Framework | Unit of improvement | Who proposes | Who decides | Selection structure | Isolation of candidates |
|---|---|---|---|---|---|---|
| Self-modifying agents | DGM | the agent's own code (git diff) | the agent itself, after an LLM diagnosis of failed benchmark logs | benchmark accuracy, staged 1 → 10 → 50 tasks | open-ended archive, parent weight `sigmoid(10(acc−0.5)) / (1+children)` | Docker; evaluator files excluded from the editable workspace (`.dockerignore`) |
| | SICA | the agent's own code | the agent (meta-improvement step) | benchmark score; base = latest version above best's lower 95% bound | linear lineage | weak: overseer, budgets, prompts are agent-editable |
| Evolutionary program search | OpenEvolve | marked code blocks (diffs or rewrites) | LLM ensemble, prompted with elites + inspirations + artifacts | evaluator `combined_score`, optional cascade | MAP-Elites grid + islands + migration | none (same process; timeouts do not kill threads) |
| | ShinkaEvolve | code blocks; also evolves its own prompts | LLM ensemble with novelty rejection before evaluation | evaluator; public/private metric split | islands, weighted parent sampling, cost budget | none (subprocess killed on timeout, env inherited) |
| Prompt / program optimizers | GEPA | text components of a system (prompts, instructions) | reflection LM reading execution traces + textual feedback | minibatch sum (accept), Pareto frontier over validation instances | per-instance Pareto frontier, merge | n/a (text only) |
| | ADAS | agent code as `forward()` | meta-agent with archive of past agents | validation accuracy (shown to correlate ~0.1 with test) | archive | none (`exec` with live API client) |
| Embodied skills / rewards | Voyager | skills as JS code | GPT-4 with env errors + critic feedback | GPT-4 self-verification critic (final state only) | skill library, embedding retrieval, overwrite by name | none (`eval` in bot server) |
| | Eureka / DrEureka | reward code (+ DR ranges) | GPT-4 with per-component reward statistics | task success metric of trained policies (best-of-N) | best-of-N per iteration | none; safety is prompt text |
| Frozen-VLA steering | RoboMonkey | which of N sampled actions to execute | — (sampling) | 7B VLM verifier (CUDA only) | per-step best-of-N | n/a |
| | V-GPS | which of N sampled actions | — | offline-RL value function (scores first action of chunk only) | per-step best-of-N | n/a |
| | DSRL | the latent noise fed to a frozen diffusion/flow policy | RL (SAC) over a 32-d noise action | environment reward | RL policy | n/a |
| | SAFE | — (failure detection) | — | sample-disagreement / learned probe (ROC-AUC ~77 on pi0/LIBERO-10) | — | — |
| Weight-level RL | RLinf | VLA weights (pi0, OpenVLA) via PPO/GRPO; RECAP offline | RL | success reward | — | Ray workers |
| | SimpleVLA-RL | OpenVLA-OFT weights via GRPO | RL | binary success, groups of 8 | — | — |
| (studied earlier) | Zetta | declarative critic + recovery bundles | Codex stages with causal diagnosis | paired McNemar gates, shadow replay | lineage, promote only | declarative only; code plugins disabled |

## 2. Cross-cutting findings

1. **Almost nobody handles evaluation noise.** OpenEvolve and ShinkaEvolve score each candidate once and keep it on any strict improvement. GEPA accepts a child when its sum over a 3-example minibatch beats the parent's (a no-op child passes about 34% of the time with binary success). DGM uses fixed task counts without tests. Only Zetta (and our loop) apply a paired statistical test. With binary LIBERO success and stochastic flow-matching policies, noise handling is the single most important design choice.
2. **Validation leaks into search everywhere.** GEPA silently reuses the train set as validation when none is given; Eureka shows the selection metric to the generator and reports best-of-N on the same task; RLinf and SimpleVLA-RL train and evaluate on the same LIBERO init states; ADAS's own result files show validation-to-test rank correlation of 0.06–0.14. A held-out split that the proposer never sees is not optional.
3. **The evaluator must be out of the candidate's reach, physically.** DGM's real defence is that the outer loop and evaluation harness are not inside the workspace the agent edits. SICA keeps its overseer and budgets in agent-editable code and pays for it. Protected-scope checks on the diff are necessary but not sufficient.
4. **Code candidates are run with essentially no isolation** in every framework that allows them (ADAS `exec`, Voyager `eval`, OpenEvolve/ShinkaEvolve in-process or env-inheriting subprocesses). This confirms keeping `kind="code"` disabled until we have a real sandbox.
5. **Archives beat hill-climbing for exploration, but promotion must stay strict.** DGM/ShinkaEvolve/OpenEvolve keep every valid candidate and sample parents with exploration bonuses; GEPA keeps per-instance winners (Pareto). None of them separates "kept in the archive" from "deployed". We should: archive broadly, promote only through the gate.
6. **Feedback quality matters more than the optimizer.** GEPA's textual feedback per component, Eureka's per-component reward statistics, DGM's diagnosis of failed logs: the proposer is only as good as the evidence it reads. Our traces (per-step state, decisions, safety reviews, privileged state) are richer than any of these.
7. **Frozen flow-matching VLAs are steerable through their noise.** SmolVLA (`predict_action_chunk(noise=)`) and pi0/pi0.5 accept injected noise of shape (B, 50, 32). This gives three things at once: replayable stochastic rollouts (common random numbers for paired comparisons), best-of-N sampling, and a small action space for RL (DSRL: a 32-d noise policy).
8. **Sample disagreement is a strong, free failure signal.** SAFE reports action variance across samples matching a learned failure detector on pi0/LIBERO-10. Together with our own diagnosis (failures dominated by repeated grasps and long stalls; successes almost never stall), this gives cheap runtime critics.
9. **Weight-level RL is feasible but expensive on our hardware.** The RLinf trick (make one denoising step stochastic and use its Gaussian log-prob) transfers to SmolVLA; the SimpleVLA-RL recipe (binary reward, GRPO groups of 8, keep groups with 10–90% success, asymmetric clip) is well tested. Neither uses a KL anchor or held-out init states. RECAP (advantage-conditioned fine-tuning) works offline on existing traces.

## 3. What to adopt (and from where)

| Mechanism | Source | How it lands in Hylo |
|---|---|---|
| Paired comparison with common random numbers | our gate + SmolVLA/pi0 `noise=` | seed each chunk's noise from (episode seed, chunk index); parent and candidate see identical noise on identical init states |
| Four-way split + sealed held-out | lessons from GEPA, Eureka, ADAS, RLinf | init states: diagnose/search 0–19, search-validation 20–29, gate 30–39, held-out 40–49; proposer sees only search metrics (ShinkaEvolve public/private) |
| Multiple-testing control | Eureka lesson | Holm correction across candidates in a cycle, or a confirmatory re-test of the winner on the gate split |
| Cascade evaluation with early stop | OpenEvolve cascade, ShinkaEvolve early stop (fixed) | stage 0 static checks + advisory critique; stage 1 few seeds with sequential test (SPRT / Beta-Binomial) to drop clear losers; stage 2 full search-validation; `stage_reached` stored separately |
| Novelty check before rollouts | ShinkaEvolve | reject candidates whose patch is equivalent to an archived one before spending simulator time |
| Archive with exploration-weighted parent sampling | DGM, ShinkaEvolve | `archive` (every valid candidate, lineage) separate from `registry` (promoted versions) |
| Evaluator outside the candidate workspace | DGM | candidates are data; evaluation code, splits and scorers are never inputs to the proposer |
| Hypothesis ledger | SICA, Zetta | every candidate states a falsifiable hypothesis; outcome recorded yes/no with evidence |
| Reflective text mutation with rollout feedback | GEPA (adapter protocol) | for reasoner/VLM prompts and recovery-rule text; components outside the seed are untouchable |
| Runtime critics from cheap signals | SAFE, our diagnosis | stall length, grasp attempts, sample disagreement → trigger recovery |
| Sample-and-select | RoboMonkey (gripper vote, skip when samples agree) | N seeded noises → gripper majority vote → medoid chunk |
| Chunk-level value critic | V-GPS (scored only the first action; we score the chunk) | trained on our traces with −1/step reward (time-to-go), no success labels needed |
| Noise-space RL | DSRL-SAC (not DSRL-NA, which needs the denoiser per update) | per-task 32-d noise policy as a learned candidate |
| Weight-level GRPO + KL | RLinf log-prob, SimpleVLA-RL recipe | SmolVLA action expert only; KL to the frozen start policy; result is a `policy_ref` candidate |
| Run budgets | ShinkaEvolve `max_api_costs` | budget in LLM tokens + simulator CPU-seconds per cycle |

## 4. What not to adopt

- Any `exec`/`eval` of model-written code without a sandbox (ADAS, Voyager, OpenEvolve, ShinkaEvolve).
- Single-shot scoring and strict-improvement acceptance (OpenEvolve, ShinkaEvolve, GEPA's minibatch rule) as a promotion criterion.
- Self-verification by the same model that proposed (Voyager) as the deciding signal.
- GEPA's default reflection prompt line that asks to embed niche facts from examples (memorisation).
- Paraphrasing the frozen VLA's task instruction as an improvement unit (SmolVLA was trained on fixed LIBERO templates; untested and likely out of distribution).
- Code from repositories without a license (V-GPS, DSRL original, RIPT-VLA) or non-commercial ones (FAIL-Detect): design only.

## 5. Implications

The proposal for physical RSI on LIBERO that follows from this study is in `design/rfcs/RFC-0002-physical-rsi.md`.
