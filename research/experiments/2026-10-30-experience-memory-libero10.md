# Experience memory and chunk critic on LIBERO-10 (2026-10-30)

Setting: frozen SmolVLA (`lerobot/smolvla_libero`), LIBERO-10, CPU, seeded noise (common random numbers), RFC-0002
splits (search = init states 0-19, search_val = 20-29; gate and held-out untouched). All comparisons are paired on
the same 100 (task, init state) episodes of search_val; p-values are exact McNemar tests on discordant pairs.

## 1. Chunk value critic (L3)

Critic: numpy MLP ensemble, Monte Carlo discounted success-to-go targets, trained on search + search_val seeds 20-24
(seeds 25-29 held out from training). Agent: 4 seeded samples per decision, execution_steps 25.

| Selector | all 20-29 | seeds 25-29 (unseen by the critic) |
|---|---|---|
| gripper vote + medoid | 0.67 | 0.70 |
| critic (beta 0.5, within the vote) | 0.66 | 0.70 (+7 / -7 discordant) |

Offline, the out-of-fold same-state pair accuracy was 0.63 +/- 0.04 with all data but 0.54 +/- 0.05 once seeds
25-29 were excluded; the online null result matches the latter. The critic is data-starved: ~120 same-state contrast
pairs. Not proposed as a candidate yet.

## 2. Action memory (RFC-0003 M1, Retrieve-then-Steer mechanism)

Mechanism checks (real SmolVLA): with no prior or t0 = 1 the sampler is bit-identical to the policy. The velocity
field is strongly contractive: a prior 0.9 std away moves the output ~40% of the way at t0 = 0.1 and almost not at
all from t0 = 0.4. Keys: 7680-d pooled SigLIP tokens; nearest same-task neighbour from another episode has median
cosine 0.969 (other tasks 0.865).

Control: the same agent without memory (n_samples 1, execution_steps 50), success 0.54.

| Bank | Built from | t0 | Success | vs control |
|---|---|---|---|---|
| unseen states | 102 search successes (530 segments) | 0.42-0.61 (confidence) | 0.46 | -0.08 (+6 / -14, p = 0.115) |
| same scenes | 222 search_val successes of other configurations (1098 segments) | 0.42-0.61 | 0.55 | +0.01 (+8 / -7, p = 1.0) |
| same scenes | same | 0.2 fixed | 0.62 | +0.08 (+13 / -5, p = 0.096) |

Offline diagnosis on unseen states: retrieval aligns the task phase exactly (mean step gap 0), but the prior is no
closer to chunks of episodes that succeeded than to chunks of episodes that failed (mean |prior - executed| 0.0459 vs
0.0440). At an unseen init state the memory returns "what the policy usually does in this phase", which carries no
outcome information; pulling towards it reduces sampling diversity.

Interpretation (supported, not yet significant: -0.08 on unseen states, +0.01 with weak and +0.08 with strong
guidance on revisited scenes): Retrieve-then-Steer's LIBERO gains were measured with an online
memory on LIBERO's fixed init states, i.e. revisiting scenes. Action memory is a scene-recall mechanism; it should be
expected to help a robot that repeats scenes (a fixed workcell), not to generalise to new layouts. Our gate, which
uses unseen init states, will (correctly) not promote it for generalisation.

## 3. Experience layer, first live run

LLM reflector (qwen3.5:35b-a3b, CPU, 58 s) on the LIBERO-10 parent search run: 4 lessons, all cited, none rejected,
e.g. "pitfall: episodes with > 3 grasp attempts or long still periods often stall". Lessons are descriptive
correlations; whether they improve proposals is measured by running campaigns with and without the experience layer.

Skill library from the two LIBERO-10 campaigns: 8 skills, none verified; both execution_steps = 25 candidates
(rule-based and LLM-proposed) were +8 / +9 points on the same gate split (p 0.07 / 0.09): recorded as "proposed"
(promising, underpowered), not refuted. These two tests share the gate split and are not independent evidence.
