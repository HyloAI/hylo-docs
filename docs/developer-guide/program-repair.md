# Program repair

!!! warning "Experimental"
    Recorded real-model probes produced no promoted candidate. Use the
    [probe results](validation/phase-guided.md) to assess this path. For the standard workflow, follow
    [Program skills](../user-guide/research-and-skills.md).

## Phase-guided repair

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
[phase-guided example and probe results](validation/phase-guided.md) before choosing this experimental path.

The example campaign, workflow diagram and probe runner are under
`harness/adapters/hylo-code-agents/examples/harness_evolution/` in the workspace.
See the [code-agent API](../api/packages/hylo-code-agents.md) and [campaign guide](../user-guide/campaigns.md)
for the surrounding runtime and version lifecycle.
