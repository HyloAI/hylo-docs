# SimpleMemVLA Integration

Date: 2026-11-04. SimpleMemVLA is implemented as one optional Hylo memory and agent
variant. The Hylo video-memory implementation produced **bitwise-identical actions** to
the pinned upstream implementation at five history boundaries, and completed **8/8**
RoboMME implementation-regression episodes on an ecolab A100. No training was performed.

## Scope

`hylo.memory.simplememvla.SimpleMemVLAHistory` owns the episode-local RGB buffers,
frame-index sampling, short-history padding, temporal patch identities and feature-cache
storage. The default released configuration retains a 60-second front-camera window
sampled at 2 fps, plus the current wrist image. Reset clears all episode state. Owned
frame copies and atomic camera validation protect against buffer reuse and partial ticks.

The optional `hylo-policy-simplememvla` package exposes a shared frozen inference runtime,
independent memory sessions and the `simplememvla` agent entry point. The native Hylo
agent records each executed control step, avoids duplicating the current frame at the
next decision, accepts an explicit demonstration prefix and maps the released checkpoint's
seven arm joints and one gripper value. Model code, image processing, language/subtask
decoding and the action head remain dependencies of the pinned upstream source. This is
a faithful memory integration, not a standalone reimplementation of the neural network.

This option requires a compatible video-conditioned checkpoint; it is not a transparent
memory attachment for arbitrary frozen VLAs. Other Hylo memory schemes remain independent.
It uses a streaming video API rather than the semantic `MemoryStore` protocol. Configure
`agent.type: simplememvla` and a local `checkpoint` after installing the optional adapter
in the inference environment. Full configuration and interface details are in
`harness/adapters/hylo-policy-simplememvla/README.md`.

## Verification

| Layer | Check | Result |
| --- | --- | --- |
| CPU unit and regression tests | Memory suite, new adapter and existing working-memory agent | 58 passed |
| Package boundaries | New adapter imports, package classification and workspace generation | 4 passed |
| Upstream sampling | Fixed and variable windows at nine positions through frame 2,400 | 18 comparisons passed |
| GPU differential | Batch 2 at frames 0, 16, 1,190, 1,206 and 1,300 | Inputs and subtasks equal; actions bitwise equal |
| GPU numerical error | Maximum absolute action difference over those checks | 0.0 |
| Closed-loop regression | Four tasks, native test IDs 0 and 1, initial batch 8 | 8/8 successes; 0 excluded |

The GPU differential test changes one row's instruction at frame 1,206 and uses different
RGB inputs for the two rows. It checks short-history padding, long histories, window
rollover, prompt changes, episode-local caches and reset. Both sides share the same frozen
model, runtime acceleration and per-comparison random seed. The test establishes parity
for these inputs and this environment, not every possible input or numerical backend.

| Task | Test episode IDs | Successes |
| --- | --- | ---: |
| PickXtimes | 0, 1 | 2/2 |
| VideoUnmask | 0, 1 | 2/2 |
| PickHighlight | 0, 1 | 2/2 |
| PatternLock | 0, 1 | 2/2 |

Closed-loop evaluation took **157.35 seconds**, excluding model loading and differential
checks, with 39 shared-batch inference calls. Eight environments started together; finished
episodes left the active batch. Native observations, reset, state normalization, action
execution and success predicates were retained. Torch and NumPy started at seed 0;
episodes used at most 1,300 control steps, 16 executed actions per decision, ten denoising
steps, temperature 1.0 and at most 64 subtask tokens. The process exited and released the GPU.

These IDs were already observed in the [40-episode upstream pilot](2026-11-04-simplememvla-pilot.md).
This regression must not be pooled with that pilot or presented as fresh held-out evidence.
There is no memory-off control, cross-method gain estimate or full 16-task benchmark score.

## Integration Boundary

GPU closed-loop evaluation used the Hylo memory sessions with the native RoboMME evaluator.
The native Hylo `SimpleMemVLAAgent` lifecycle and observation/action mapping were tested
on CPU with an injected model double; a full Hylo kernel-to-RoboMME run is not part of this
record. Its plugin maturity therefore remains `unverified`. The native agent seeds each
decision from the episode seed and decision index; upstream-style batching uses a shared
RNG stream. Different batching or seed protocols need not yield the same trajectory.

The supported embodiment is the released Panda joint-position/gripper interface at 20 Hz.
The adapter does not convert controller units, gripper conventions or embodiments. Model
dependencies are optional, local weights are required and no weights are downloaded by
the adapter. Upstream MIT notices are included in both affected packages and their wheels.

## Provenance

- Source: `OpenBMB/SimpleMemVLA@453d6ec293e63318bbc2bce545d0b9256ab1bc51`.
- Checkpoint: `yinchenghust/simplememvla_robomme@6bf7204311496b93f12889cad0eaf3fcbddc35e4`.
- Model SHA-256: `3d0fa9de73353cbd3e0e6c9b798b3747b7126931d42ce3a8cd510be767ffce69`.
- Runtime: A100 80GB, Python 3.11, Torch 2.9.1, Transformers 5.11.0, bf16, SDPA,
  FLA 0.2.2 and causal-conv1d 1.6.2.post1. Both comparison paths use the same validated
  Conv3d-to-GEMM projection replacement as the upstream pilot.
- [Machine-readable results](2026-11-04-simplememvla-integration.results.json) include
  protocol, outcomes, source archive hash and raw-artifact hashes.
- Raw local artifacts: `runs/memory-20261104/hylo-simplememvla-v1/`; remote artifacts:
  `~/hylo-memory-eval/evals/hylo-simplememvla-v1/` on ecolab.
- Opt-in differential script:
  `harness/adapters/hylo-policy-simplememvla/tests/verify_upstream.py`.

The source archive captures the code executed remotely. Later documentation, packaging
metadata and plugin maturity edits are not part of that archive; inference, agent, bridge
and memory implementation files match the executed source hashes. Original reference
checkouts were not modified.
