# Video-memory checks { #video-memory-integration-checks }


The recorded 2026-11-04 integration checked 18 sampling comparisons against pinned upstream
code. Five GPU comparisons with batch 2 matched prepared inputs, subtask text and action
chunks bitwise. The Hylo memory bridge completed 8/8 RoboMME regression episodes across
PickXtimes, VideoUnmask, PickHighlight and PatternLock.

Those episode IDs had already been observed. This establishes implementation regression,
not a fresh held-out success estimate or improvement over another memory method. The
native agent lifecycle has CPU coverage; a full native Hylo kernel-to-RoboMME evaluation
remains unverified. Longer windows, alternative frame selection and background prefill
are possible experiments, not implemented or validated improvements.

## Reproduce

The [adapter reproduction instructions](https://github.com/HyloAI/hylo-harness/tree/main/adapters/hylo-policy-simplememvla#reproduction)
identify the pinned model environment and opt-in differential checks. Follow [Video memory](../../user-guide/memory/video.md)
for the native agent configuration and its integration boundary.

## Dependencies

- Upstream source: `OpenBMB/SimpleMemVLA@453d6ec293e63318bbc2bce545d0b9256ab1bc51`.
- Checkpoint: `yinchenghust/simplememvla_robomme@6bf7204311496b93f12889cad0eaf3fcbddc35e4`.
- [Memory API](../../api/packages/hylo-memory.md) and [adapter API](../../api/packages/hylo-policy-simplememvla.md).
- Implementation diagrams and reproduction instructions:
  `harness/packages/hylo-memory/docs/simplememvla/README.md` and
  `harness/adapters/hylo-policy-simplememvla/README.md` in the workspace.

The packages retain upstream MIT attribution. Model processing remains a separate pinned
dependency; the memory backend alone can run on CPU without loading it.
