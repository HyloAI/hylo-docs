# Program development and skill reuse


<video src="../../assets/videos/skills-sorting.mp4" poster="../../assets/videos/skills-sorting.jpg" controls muted playsinline preload="none" width="100%" aria-label="From Experience to Verified Skills: an English walkthrough of AI program development, independent verification and skill reuse on a Panda sorting task"></video>

*2:33 · English · Recorded research walkthrough and physics replay. A deliberately limited one-object-per-colour
starter becomes a program for sorting multiple objects into matching trays. The video follows the actual source
revision, complete-program execution, independent evaluation, skill-library record and later skill call.*

The model is **claude:sonnet**. It develops `solve(robot)` using four development cases; the selected submission
passes **4/4**. Submission evaluation and subsequent candidate tests execute
as `code.program`, without model calls during execution. This is program development, not model-weight training.
The starter and its robot-tool helpers were supplied; this is not a from-scratch result. Two preceding local-model
development attempts produced no qualifying candidate; the video follows the selected Claude session.

| Evaluation | Starter | Candidate | Scope |
| --- | --- | --- | --- |
| Independent promotion gate | 8% | 92% | 12 paired scenes; 10 candidate-only wins, 0 parent-only wins; p = 0.000977 |
| Held-out report | 8% | 83% | 12 paired scenes; report only, not candidate selection |
| Later agent using the skill | — | 3/3 | Separate validation scenes; actual retrieval and skill calls recorded |

The program skill **`sort_by_colour@1`** references implementation digest **`33387ae26b8c9df8`** and the campaign's
promotion evidence. Later agents retrieve the verified program by instruction similarity, verify its artifact
integrity and call `skills.sort_by_colour(robot)`. The reuse episodes are additional observations, not a paired
comparison against an agent without skills.

**Conditions and presentation.** One task family, one Panda simulation, two 160 × 120 RGB-D cameras and simulator
instance segmentation. This does not establish real-world visual recognition, hardware transfer or performance
on other task families. The polished interface presents saved research records; it is not a live Studio authoring
interface. Physics is replayed from recorded approved actions with higher-resolution presentation cameras, full
visual meshes and restyled lighting/table appearance. Model waits are shortened and motion timing is edited for
readability. Every replayed joint/gripper state and final task verdict is checked against its source trace.

[Source and replay provenance](../assets/videos/skills-sorting.provenance.json) includes the experiment conditions,
paired results, skill identity, source trace hashes, replay checks and video hashes. The earlier
[stacking improvement and reuse result](tool-agents.md) remains a separate experiment.


## Reproduce the workflow

Follow the [program development and reuse guide](../user-guide/research-and-skills.md). A new model run may produce a different result. The recorded conditions and provenance above describe this case.
