# Learning beyond the agent's own rollouts: video, demonstrations, values, world models

Date: 2026-10-31. Scope: what "learning" components a frozen-VLA RSI harness should be able to host, and where
they plug in (RFC-0004). Claims are as reported by the papers (mostly self-reported; not reproduced here). Items
marked "from memory" were not re-checked in this survey.

## 1. Learning from video (no action labels)

| Route | Idea | Examples | Needs |
|---|---|---|---|
| Latent-action pretraining | infer a discrete "latent action" from consecutive frames, pretrain a VLA on it, map latents to real actions with a little robot data | LAPA (arXiv 2410.11758), ConLA (2602.00557), JALA (2602.21736, 7.5M clips), CLAP (2601.04061) | unlabelled video, GPU |
| Hand pose -> pseudo-actions | estimate 3D hand / wrist pose in egocentric video and retarget to robot actions | EgoVLA (2507.12440), ACE-Ego-0 (2606.17200, 1.48K h of pseudo-labelled human video with reliability weighting) | egocentric video, pose estimation, GPU |
| Video world models | learn action-conditioned prediction; imagine rollouts, generate data, evaluate policies | WorldGym (ICLR 2026), Ctrl-World (2510.10125), RoboWorld (2607.02642), WorldEval (2505.19017); V-JEPA 2-AC, Cosmos / DreamGen (from memory) | large video corpora, GPU |
| Progress / reward from video | learn or prompt "how far along is the task" | GVL (ICLR 2025, VLM orders shuffled frames), TOPReward (2602.19313, zero-shot from token probabilities), Large Reward Models (2603.16065), ViVa (2604.08168) | video + task text; small models feasible on CPU |

## 2. Learning from the agent's own experience

- **RECAP / pi\*0.6** (2511.14759, RSS 2026): a value function gives per-step advantage; the policy is conditioned on
  advantage, so failures and human corrections are usable training data.
- **SimpleVLA-RL** (2509.09674, ICLR 2026): outcome-reward GRPO on a VLA; near state of the art on LIBERO.
- **Learning While Deploying** (2605.00416): fleet-scale learning from autonomous deployment data.
- **Latent / noise-space adaptation of a frozen policy**: FlowDAgger (adapts a frozen flow policy from corrections in
  latent space; pi0.5 0.13 -> 0.80 with 50 demos + 10 corrections, project page); DSRL (RL over the diffusion /
  flow initial noise, from memory). These fit a frozen-VLA harness directly: the policy is untouched and the learned
  component is small.

## 3. Other sources

Human corrections (HG-DAgger 1810.02890, ROVE 2606.17011) need a teleoperation channel; cross-embodiment data and
web co-training change the base model; surveys (2607.13104, 2609.13236) stress safety-critical exploration and
non-stationarity as the open problems of embodied self-improvement.

## 4. Consequences for worldcurrent

1. A **value / progress model** is the hub: RECAP, ViVa and DSRL depend on one, and the same model serves as the
   success judge that RFC-0003 M5 needs. First step: zero-shot VLM judge vs a judge trained on our traces, both
   calibrated against LIBERO ground truth.
2. **Frozen-policy learners** (noise / latent space) are the best fit for our hardware (CPU) and our architecture
   (`PriorSampler`); our finding that SmolVLA's velocity field is contractive (guidance acts at small t0) informs
   their design.
3. **World models are instruments**: they may pre-screen candidates, never replace the gate.
4. **Video pretraining and RL fine-tuning** are L4 weight candidates; they need the GPU and dataset approval, and
   enter through the same learner -> sealed artifact -> gate path.
