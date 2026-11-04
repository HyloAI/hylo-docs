# Program research

Use a model to develop a task program on development cases, freeze a qualifying submission and evaluate it
separately. A session can inspect the scene, try robot actions, reset cases and submit `solve(robot)` programs.
Freezing preserves the implementation; subsequent checks establish its capability and whether a revision improves
its parent.

The recorded promotion example improves an existing stacking program. From-scratch local-model sessions have
not produced a successful development program in the recorded evaluation; see [results and limitations](../showcase/tool-agents.md).

## Recorded skill-development demo

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
[stacking improvement and reuse result](../showcase/tool-agents.md) remains a separate experiment.

## Start a development session

Prepare [the tools, environment and model backend](developing-strategies.md#prepare-the-environment). From the
workspace root, the existing stacking experiment can be used as a development environment:

```bash
uv run hylo research harness/adapters/hylo-code-agents/examples/campaign/experiment.yaml \
    --model ollama:gpt-oss:20b --dev 3 --budget turns=30,resets=6,submits=3 \
    --out runs/research/stack
```

This command requires that model at the configured Ollama endpoint. It uses `search` cases and does not
automatically pass the experiment's parent program to the model. A campaign's `research.llm` generator can pass
the parent program as described below. The command returns a nonzero status if no program qualifies for freezing.

During a session:

- `robot` is the manipulation toolkit on the live episode.
- `reset(case)` starts another development attempt and reports the previous outcome.
- `submit(source)` validates a program and evaluates it on the development cases without model calls.
- `finish()` ends development; turn, reset, submission, token and cost budgets can also end it.

Inspect `summary.json`, `log.jsonl`, the `submissions/` directory and, when one qualifies, `frozen/`. A frozen
program records its source, entry point, artifact digest and provenance. It has not been promoted merely by being frozen.

## Evaluate a frozen program

`hylo research --evaluate search_val` evaluates after the session; `--with-parent` also evaluates the configured
agent for a paired comparison. Post-session outcomes are not fed back into that session's model. Evaluation can
also be run later with `code.program` and its sealed artifact.

Use development and validation results while iterating. Reserve gate and held-out states for a predeclared
decision and final report. Once you use a result to choose or edit a program, it is no longer independent evidence
for that choice. A standalone `--evaluate` command does not run the campaign promotion protocol.

## Improve an existing program through a campaign

`research.llm` is a candidate generator for the ordinary campaign cascade. It can expose a `code.program` parent's
source to the model, freeze a submission and propose it as a code candidate. The campaign owns the subsequent
validation, paired gate, held-out report, approval and version registry.

```bash
uv run hylo evolve run harness/adapters/hylo-code-agents/examples/campaign/campaign.yaml
uv run hylo evolve status runs/campaign/campaign
```

The shipped example uses one cycle and automatic approval in simulation. Its output paths are relative to the
working directory. Keep them consistent when resuming. For deployment, review
[approval and rollback](campaigns.md) and [Security](security.md); an approval happens after candidate evaluation.

The [recorded stacking campaign](../showcase/tool-agents.md) reports the gate and held-out results, including
its deliberately weak parent and privileged simulator observations.

## Reuse a promoted program

The current program-skill path creates an explicit skill-library record. It binds a name/version, applicability,
the sealed implementation and gate evidence. Policies and controllers can also implement robot skills, but the
CLI below specifically derives records for promoted program candidates.

Derive program skills from the campaign's promoted candidates:

```bash
uv run hylo research skills runs/campaign/campaign --library runs/skills --family stack
```

Configure a later `code.llm` agent with `agent.params.skills: runs/skills`. Verified program skills are retrieved
by instruction similarity and made available as `skills.<name>(robot)`. A skill references the sealed program and
its gate evidence; it is not a new trained checkpoint. Applicability and validation are limited to the recorded
robot, task and observation conditions. Revalidate when those conditions change.

## Recipe skills from role campaigns

World tasks have a separate development and replay-verification path. See [role campaigns](worlds.md#tasks-with-roles)
and [recipe skills](memory/skills.md#recipe-skills) for how their results enter the same library.

## Inspect sessions in Studio

```bash
uv run hylo playground --repo . --sessions research=runs/research
```

The [Research page](studio.md#research) reads recorded sessions: turns, code, output, camera views, submissions,
frozen source, usage and cost. It also links campaign candidates when their evidence names the session. It does
not provide an interactive model-development editor or start research sessions from this page.

<video src="../../assets/videos/studio-research.mp4" poster="../../assets/videos/studio-research.jpg" controls muted playsinline preload="none" width="100%" aria-label="The Studio's Research page: a session's turns, submissions and frozen program, the campaign that promoted it, the program skill"></video>

*A research session's turns, submissions and frozen program; the campaign that promoted it; the verified program skill in the library.*

## Next

- [Skill library](memory/skills.md): retrieve and apply program skills.
- [Campaigns](campaigns.md): promotion, approval and rollback.
