# Research sessions and program skills

A research session helps develop a task program through repeated experiments. The model can inspect development
cases, try robot actions, reset cases and submit `solve(robot)` programs. The best qualifying submission is frozen
as a program artifact. Separate evaluation establishes what that program can do beyond its development cases.

This supports both new-task development and revision of an existing program. The recorded promotion example
improves an existing stacking program; from-scratch local-model sessions have not yet produced a successful
development program. See [the results and limitations](../showcase/tool-agents.md).

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

In the recorded stacking campaign, the candidate scored 0.95 against 0.50 at the gate (20 pairs, p = 0.002),
and 1.00 against 0.60 on held-out (20 pairs). This was one task and a deliberately weak hand-written parent, with
simulator segmentation. It is evidence for that program improvement, not for general autonomous task development.

## Reuse a promoted program

Derive program skills from the campaign's promoted candidates:

```bash
uv run hylo research skills runs/campaign/campaign --library runs/skills --family stack
```

Configure a later `code.llm` agent with `agent.params.skills: runs/skills`. Verified program skills are retrieved
by instruction similarity and made available as `skills.<name>(robot)`. A skill references the sealed program and
its gate evidence; it is not a new trained checkpoint. Applicability and validation are limited to the recorded
robot, task and observation conditions. Revalidate when those conditions change.

## Inspect sessions in Studio

```bash
uv run hylo playground --repo . --sessions research=runs/research
```

The [Research page](studio.md#research) reads recorded sessions: turns, code, output, camera views, submissions,
frozen source, usage and cost. It also links campaign candidates when their evidence names the session. It does
not provide an interactive model-development editor or start research sessions from this page.
