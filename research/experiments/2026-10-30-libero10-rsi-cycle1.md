# LIBERO-10 RSI cycle 1 (2026-10-30): frozen SmolVLA, rule proposer

Setup: `examples/rsi_libero/run_cycle.py`, `lerobot/smolvla_libero` frozen, SteeredAgent with seeded noise (common random
numbers), RFC-0002 protocol: search = init states 0-19 (200 episodes), search_val = 20-29, gate = 30-39, heldout = 40-49
(100 episodes each, 10 tasks). CPU only, 24 workers, about 18 episodes/min. Cycle wall time 56 min.

## Diagnosis (parent, search split): success 0.495
Failure buckets (one failure can be in both): regrasp (>= 3 grasp attempts) 80%, stall (>= 30 still steps) 44%, other 3%.

## Candidates

| Candidate | Hypothesis | search_val (parent 0.54) | Verdict |
|---|---|---|---|
| stall_backoff @ 20 still steps | backing off converts stalls into successes | 0.55 (2 W / 1 L) | archived |
| stall_backoff @ 30 | same | 0.55 (1 W / 0 L) | archived |
| regrasp_resample noise x1.5 | resampling escapes repeated grasp failures | 0.54 (0 / 0) | archived |
| regrasp_resample noise x2.0 | same | 0.53 (0 / 1) | archived |
| vote over 4 samples | avoids unlucky samples | 0.52 (8 / 10) | archived |
| execution_steps 25 (replan twice as often) | reacts to drift sooner | **0.62** | **gate: 0.53 vs 0.44, 19 W / 10 L, one-sided McNemar p = 0.068 -> not promoted** |

## Readings
- The protocol refused a promotion on insufficient evidence: the gate is a single confirmatory test at alpha = 0.05.
- Replanning every 25 steps helped on three disjoint sets of init states: +12 points (init 0-9, steering sweep),
  +8 (search_val), +9 (gate). Each test alone has about 30 discordant pairs, which is underpowered for a ~10-point effect.
- With common random numbers the rule candidates changed almost no episodes (0-3 discordant pairs of 100): the
  triggers rarely fire or their recovery does not change the outcome. The diagnosis buckets are real, but the
  hand-written recoveries do not address them.
- Next: power the gate (noise replicates on the gate init states, with alpha spending across looks), and replace the
  rule proposer with an LLM proposer that reads failure traces.
