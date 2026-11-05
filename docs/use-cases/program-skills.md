# Reuse a skill { #program-development-and-skill-reuse }

Turn an existing sorting program into a verified skill, then let another agent call it on new layouts.
This recorded simulation uses a supplied starter and robot tools, RGB-D cameras and instance segmentation.
It demonstrates program development and reuse within one Panda sorting task family.


<video src="../../assets/videos/skills-sorting.mp4" poster="../../assets/videos/skills-sorting.jpg" controls muted playsinline preload="none" width="100%" aria-label="From Experience to Verified Skills: an English walkthrough of AI program development, independent verification and skill reuse on a Panda sorting task"></video>

*2:33 · English · Recorded research walkthrough and physics replay. A deliberately limited one-object-per-colour
starter becomes a program for sorting multiple objects into matching trays. The video follows the actual source
revision, complete-program execution, independent evaluation, skill-library record and later skill call.*

??? info "Recording details"

    The model is **claude:sonnet**. It develops `solve(robot)` using four development cases; the selected submission
    passes **4/4**. Submission evaluation and subsequent candidate tests execute
    as `code.program`, without model calls during execution. This is program development, not model-weight training.
    The starter and its robot-tool helpers were supplied; this is not a from-scratch result. Two preceding local-model
    development attempts produced no qualifying candidate; the video follows the selected Claude session.

    The recorded candidate passes an independent promotion gate and is then evaluated on held-out scenes.
    Later agents retrieve and call `sort_by_colour@1` in separate validation scenes.

    **Conditions.** One Panda sorting task family, two RGB-D cameras and simulator instance segmentation.
    The video presents recorded actions with edited timing and higher-resolution replay cameras. The starter and
    robot-tool helpers were supplied. This does not establish hardware transfer or recognition in real-world images.

Read [Developing a program into a reusable skill](https://hyloai.github.io/research/articles/program-skills/)
for the full evaluation, preceding failed attempts, reuse evidence and limitations.
[Replay provenance](../assets/videos/skills-sorting.provenance.json) identifies the source traces and video checks.

## Try it { #reproduce-the-workflow }

Follow the [program development and reuse guide](../user-guide/research-and-skills.md). A new model run may produce a different result. The recorded conditions and provenance above describe this case.
