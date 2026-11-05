# Video-memory integration checks


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
