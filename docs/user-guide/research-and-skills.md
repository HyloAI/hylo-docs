# Develop and reuse a program skill

Improve an existing task program with a model, let a campaign evaluate the frozen candidate, and make a promoted
program available to a later agent. The supplied example starts from a deliberately weak stacking program.
Promotion depends on the results; a new model session may produce no qualifying candidate.

## Before you start

You need the [workspace](../getting-started/installation.md), [camera rendering](../getting-started/optional-environments.md#camera-rendering)
and an Ollama endpoint serving `gpt-oss:20b`. The shipped campaign names that model and uses automatic approval
in simulation. All commands below run from the **workspace root** and write under `runs/campaign/`.
Use a fresh output directory for a new experiment; reusing an existing campaign directory can resume its state.

The model receives the parent's source and develops on three `search` cases. The campaign evaluates frozen
programs as `code.program`, without model calls during their execution. The [recorded case](../developer-guide/validation/tool-agents.md#program-improvement)
reports the conditions and results; the [sorting demo](../use-cases/program-skills.md) is a separate experiment.

## 1. Develop and evaluate a candidate { #improve-an-existing-program-through-a-campaign }

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

The [recorded stacking campaign](../developer-guide/validation/tool-agents.md) reports the gate and held-out results, including
its deliberately weak parent and privileged simulator observations.

## 2. Check the promotion

Inspect `runs/campaign/campaign/cycle-01/cycle_report.json` and the status printed above. A successful path has a
promoted candidate and an `active.json` pointing to it. If no candidate passes, inspect the research session under
`runs/campaign/research/`; do not derive or claim a verified program skill from an unsuccessful run.

The gate supports the comparison with this parent under the declared conditions. A held-out report is kept for
review. For hardware use, configure `approval: manual` before running the campaign and validate the target setup.

## 3. Build and use the skill library { #reuse-a-promoted-program }

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

## Inspect sessions in Studio

```bash
uv run hylo playground --repo . --sessions research=runs/research
```

The [Research page](studio.md#research) reads recorded sessions: turns, code, output, camera views, submissions,
frozen source, usage and cost. It also links campaign candidates when their evidence names the session. It does
not provide an interactive model-development editor or start research sessions from this page.

<video src="../../assets/videos/studio-research.mp4" poster="../../assets/videos/studio-research.jpg" controls muted playsinline preload="none" width="100%" aria-label="The Studio's Research page: a session's turns, submissions and frozen program, the campaign that promoted it, the program skill"></video>

*A research session's turns, submissions and frozen program; the campaign that promoted it; the verified program skill in the library.*

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

## Phase-guided evolution

`harness.program` is an optional proposer in `hylo-code-agents`. It uses phase-scoped program repair and notes within Hylo's research runtime and campaign gate.

The model proposes observable phases, repairs `solve(robot)` on search cases, and can
distill notes connecting a failed case to a successful replay in the selected program.
All selected development cases must pass before a candidate is returned. Invalid notes
are discarded without discarding an otherwise valid program.

```yaml
proposer:
  type: harness.program
  params:
    model: {backend: ollama, model: gpt-oss:20b, reasoning_effort: low}
    dev: 6
    budget: {turns: 40, submits: 6, resets: 12}
    out_root: runs/harness-program/proposals
    repair_campaigns: [runs/harness-program]
```

Use this block within a campaign configuration. The alias requires the updated adapter
entry-point metadata; the equivalent module reference is
`hylo.codeagents.harness_evolution:HarnessEvolutionProposer`.

Completed program revisions are automatically submitted within the budget. Unchanged
collected source and explicit submissions are not duplicated. The ordinary `research.llm`
proposer retains its explicit-submission behavior. Planning and optional distillation
share the total model-call budget with development.

Repair notes and their evidence share the sealed program artifact. Recall checks both
artifact integrity and the digest recorded in the admitted candidate, and reads only
active promoted lineages. A gate-passing candidate awaiting approval contributes no notes.
Rollback removes the retired branch's notes from subsequent recall. A note's transfer to
another task remains unverified even when its containing program passed a gate.

The phase plan is guidance for generated code, not a centrally enforced phase interpreter.
Using a frozen VLA requires a toolkit that exposes one; there is no automatic SimpleMemVLA
handover. The recorded real-model probes produced no promoted candidate. See the
[phase-guided example and probe results](../developer-guide/validation/phase-guided.md) before choosing this experimental path.

The example campaign, workflow diagram and probe runner are under
`harness/adapters/hylo-code-agents/examples/harness_evolution/` in the workspace.
See the [code-agent API](../api/packages/hylo-code-agents.md) and [campaign guide](campaigns.md)
for the surrounding runtime and version lifecycle.

## Recipe skills from role campaigns

World tasks have a separate development and replay-verification path. See [role campaigns](worlds.md#tasks-with-roles)
and [recipe skills](memory/skills.md#recipe-skills) for how their results enter the same library.

## Recorded skill-development demo

[Watch the recorded case, including results, conditions and provenance](../use-cases/program-skills.md).

## Next

- [Skill library](memory/skills.md): retrieve and apply program skills.
- [Campaigns](campaigns.md): promotion, approval and rollback.
