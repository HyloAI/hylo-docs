# Develop a program skill { #develop-and-reuse-a-program-skill }

Improve an existing task program with a model, let a campaign evaluate the frozen candidate, and make a promoted
program available to a later agent. The supplied example starts from a deliberately weak stacking program.
Promotion depends on the results; a new model session may produce no qualifying candidate.

## Setup { #before-you-start }

You need the [workspace](../getting-started/installation.md), [camera rendering](../getting-started/optional-environments.md#camera-rendering)
and an Ollama endpoint serving `gpt-oss:20b`. The shipped campaign names that model and uses automatic approval
in simulation. All commands below run from the **workspace root** and write under `runs/campaign/`.
Use a fresh output directory for a new experiment; reusing an existing campaign directory can resume its state.

The model receives the parent's source and develops on three `search` cases. The campaign evaluates frozen
programs as `code.program`, without model calls during their execution. The example uses simulator-provided observations; keep those conditions explicit when comparing agents.
See the [recorded case](../developer-guide/validation/tool-agents.md#program-improvement) for its measured scope.

## 1. Develop { #improve-an-existing-program-through-a-campaign }

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

## 2. Verify { #2-check-the-promotion }

Inspect `runs/campaign/campaign/cycle-01/cycle_report.json` and the status printed above. A successful path has a
promoted candidate and an `active.json` pointing to it. If no candidate passes, inspect the research session under
`runs/campaign/research/`; do not derive or claim a verified program skill from an unsuccessful run.

The gate supports the comparison with this parent under the declared conditions. A held-out report is kept for
review. For hardware use, configure `approval: manual` before running the campaign and validate the target setup.

## 3. Reuse { #reuse-a-promoted-program }

Derive a skill-library record from the promoted candidate. It binds the name, version, applicability, sealed
program and gate evidence:

```bash
uv run hylo research skills runs/campaign/campaign --library runs/skills --family stack
```

Configure a later `code.llm` agent with `agent.params.skills: runs/skills`. Verified program skills are retrieved
by instruction similarity and made available as `skills.<name>(robot)`. A skill references the sealed program and
its gate evidence; it is not a new trained checkpoint. Applicability and validation are limited to the recorded
robot, task and observation conditions. Revalidate when those conditions change.

Create `runs/stack-skill-reuse.yaml` with this complete configuration, keeping the model endpoint available:

```yaml
schema_version: hylo.experiment/v0.1
name: stack-skill-reuse
benchmark: {type: mujoco/manip-v0, split: validation, params: {tasks: [stack], validation: 3}}
env: {type: mujoco.panda_table, params: {cameras: [front, side, wrist], segmentation: true}}
agent:
  type: code.llm
  params:
    model: {backend: ollama, model: gpt-oss:20b, vision: false, reasoning_effort: low}
    skills: runs/skills
trace: {record_privileged: false}
output_dir: runs/skill-reuse
```

```bash
uv run hylo run runs/stack-skill-reuse.yaml
```

Inspect the printed run directory with `hylo trace`. Check whether the agent retrieved and actually called the
skill, as well as the task verdict. Retrieval does not force the model to use a skill. These validation episodes
are development observations; they are not a new paired estimate of the skill's benefit.

## Inspect sessions { #inspect-sessions-in-studio }

```bash
uv run hylo playground --repo . --sessions research=runs/research
```

The [Research page](studio.md#research) reads recorded sessions: turns, code, output, camera views, submissions,
frozen source, usage and cost. It also links campaign candidates when their evidence names the session. It does
not provide an interactive model-development editor or start research sessions from this page.

<video src="../../assets/videos/studio-research.mp4" poster="../../assets/videos/studio-research.jpg" controls muted playsinline preload="none" width="100%" aria-label="The Studio's Research page: a session's turns, submissions and frozen program, the campaign that promoted it, the program skill"></video>

*A research session's turns, submissions and frozen program; the campaign that promoted it; the verified program skill in the library.*

## Standalone development { #start-a-development-session }

Prepare [the tools, environment and model backend](developing-strategies.md#prepare-the-environment). From the
workspace root, the existing stacking experiment can be used as a development environment:

```bash
uv run hylo research harness/adapters/hylo-code-agents/examples/campaign/experiment.yaml \
    --model ollama:gpt-oss:20b --dev 3 --budget turns=30,resets=6,submits=3 \
    --out runs/research/stack
```

This command requires that model at the configured Ollama endpoint. It uses `search` cases and does not
automatically pass the experiment's parent program to the model. A campaign's `research.llm` generator can pass
the parent program in the campaign workflow above. The command returns a nonzero status if no program qualifies for freezing.

During a session:

- `robot` is the manipulation toolkit on the live episode.
- `reset(case)` starts another development attempt and reports the previous outcome.
- `submit(source)` validates a program and evaluates it on the development cases without model calls.
- `finish()` ends development; turn, reset, submission, token and cost budgets can also end it.

Inspect `summary.json`, `log.jsonl`, the `submissions/` directory and, when one qualifies, `frozen/`. A frozen
program records its source, entry point, artifact digest and provenance. It has not been promoted merely by being frozen.

## Evaluate a program { #evaluate-a-frozen-program }

`hylo research --evaluate search_val` evaluates after the session; `--with-parent` also evaluates the configured
agent for a paired comparison. Post-session outcomes are not fed back into that session's model. Evaluation can
also be run later with `code.program` and its sealed artifact.

Use development and validation results while iterating. Reserve gate and held-out states for a predeclared
decision and final report. Once you use a result to choose or edit a program, it is no longer independent evidence
for that choice. A standalone `--evaluate` command does not run the campaign promotion protocol.

<span id="phase-guided-evolution"></span>
<span id="recipe-skills-from-role-campaigns"></span>

## Related workflows

- [Program repair](../developer-guide/program-repair.md): the experimental phase-guided proposer, its
  configuration and current evidence.

- [Role campaigns](worlds.md#tasks-with-roles): develop and replay world-task solutions to create
  [recipe skills](memory/skills.md#recipe-skills) in the same library.

<span id="recorded-skill-development-demo"></span>

## Next

- [Skill library](memory/skills.md): retrieve and apply program skills.
- [Campaigns](campaigns.md): promotion, approval and rollback.
- [Sorting demo](../use-cases/program-skills.md): recorded development, verification and reuse.
