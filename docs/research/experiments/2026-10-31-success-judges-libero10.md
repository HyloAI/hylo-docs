# Success judges on LIBERO-10: trained on traces vs zero-shot VLM (2026-10-31)

Purpose: RFC-0004 A3 / RFC-0003 M5. Can an instrument label episode outcomes from what a real robot records (camera
frames, proprio, instruction), so that memory and training data can be written without simulator ground truth?

Inputs a judge may use: the last observation that has both camera frames (traces keep a frame every 10 steps),
its proprio state, the task. Not allowed: privileged state, episode length, termination reason (a LIBERO episode
ends the moment it succeeds, so length would leak the label).

## Setup

- `judge.trace` (artifact `runs/judges/l10-trace-v1`, digest 54a1efadf00d34d8; rebuilt 2026-10-31 as `l10-trace-v2` from the three LIBERO runs alone: identical weights, digest and calibration, without the two test-double runs that v1's provenance listed but its task filter never read; likewise `l10-image-v2`): numpy MLP ensemble on proprio + task
  one-hot + 8x8 grayscale thumbnails of the agentview and wrist frames. Trained on the `search` split only (init
  states 0-19; 600 episodes from the two LIBERO-10 campaigns and the RSI run; 4323 frames, with early frames of
  successful episodes as extra negatives). CPU, 4 s.
- `judge.vlm`: qwen3.5:35b-a3b via Ollama, zero-shot. Both final frames and the instruction; asked for completed +
  confidence. Median latency 2.7 s per episode on CPU.
- Calibration (`wc calibrate`): `search_val` runs (init states 20-29, unseen by `judge.trace`), LIBERO-10 tasks only,
  the same seeded random sample of 300 episodes for both judges (base rate 0.58). The ground truth is the
  simulator outcome.

## Results

| Judge | AUC | Brier | ECE | Precision / recall at the 0.95-precision threshold | Ready to label |
|---|---|---|---|---|---|
| judge.trace | **0.93** | 0.12 | 0.12 | 0.95 / **0.55** (threshold 0.994) | yes |
| judge.vlm | 0.61 | 0.41 | 0.41 | 1.00 / 0.13 (threshold 0.95) | no |

The 600-episode calibration of `judge.trace` (seed 0) gives the same picture (AUC 0.92, recall 0.55 at precision
0.95). Within-task AUC is 0.71-1.0 on the 9 tasks that have both outcomes (5 of 9 at 1.0), so the judge reads the
scene change, not which task is easy.

The VLM never claimed a failed episode was complete (0 / 126), but it recognised only 23 of 174 successes. Its
reasons point at two causes:
1. the last stored frame is up to 9 steps before success: "the robot is still holding a mug", "the tomato sauce
   bottle is still on the table";
2. occlusion and viewpoint: "the bowl is not visible inside the drawer".

## Interpretation

- A small judge trained on our own labelled traces is usable now, as a high-precision labeller: at threshold 0.994
  it labels about half of the successes with ~5% false positives. That is enough to grow an action memory or a
  self-training set from unlabelled episodes, provided writes use the precision threshold and the judge stays
  calibrated on the deployment distribution.
- Zero-shot VLM judging is not usable for labelling here. It is conservative (no false positives in 300), so as a
  veto ("never write an episode the VLM calls a failure") it costs recall but not precision.
- Both judges are limited by frame cadence. Recording the frame at the moment the episode ends would help the VLM
  most. That change is to the kernel and is not made yet.

## Caveats

- `judge.trace` is calibrated on the same scenes (LIBERO-10) and the same policy's behaviour it was trained on; only
  the init states are new. Transfer to new scenes, policies or real cameras is untested and expected to be worse.
- n = 300 episodes; per-task estimates rest on 25-35 episodes each.
