# Adding a learner

You will write a learner, build a sealed artifact from development runs, and let a campaign's gate decide on a
candidate that uses it. A learner turns recorded runs into an artifact. For success judges see
[learning](../user-guide/learning.md); for generators that propose changes directly, [adding a generator](adding-a-generator.md).

You need the [development workspace](../getting-started/installation.md) with hylo-bench.

## 1. Create and install the package

From the workspace root, create the package in `plugins/packages/`:

```bash
uv run hylo plugin new learner my-recap --dir plugins/packages
```

This creates `plugins/packages/hylo-plugin-my-recap` with the module `wc_my_recap`. Add `license = "Apache-2.0"` (or
your licence) under `[project]` in its `pyproject.toml`. Then add it to the workspace and install it, as in
[adding a policy](adding-a-policy.md#1-create-and-install-the-package). From here on, run commands from `bench/`:

```bash
uv run python harness/dev/workspace.py
uv sync                                     # add the --group options you used in Installation
cd bench
uv run hylo plugins | grep my-recap
```

```text
learners     my-recap                       hylo.learner/v0.1    unverified      Apache-2.0
```

Record some runs to learn from: 80 episodes of the planar IK controller with `kp: 0.3` on a development split.

```bash
uv run hylo run examples/configs/mujoco_reach.yaml --split search --output runs/demos \
    --set benchmark.params.protocol=rsi
```

## 2. Write fit()

A learner has a `name` and one method, `fit(job) -> ArtifactManifest`. This example groups development runs by the
agent's gain and seals an artifact that records the gain with the highest success rate:

```python title="src/wc_my_recap/plugin.py"
"""Learner plugin: development runs in, one sealed artifact out."""

from __future__ import annotations

import json
from pathlib import Path

from hylo.core.artifact import ArtifactManifest, Provenance, development_runs, write_manifest


class MyRecapLearner:
    name = "my-recap@0.1"

    def fit(self, job) -> ArtifactManifest:
        param = job.params.get("param", "kp")                         # the agent parameter to recap
        sources = development_runs(job.inputs, job.splits)           # gate / held-out are refused or skipped
        outcomes: dict[float, list[bool]] = {}
        for rd, _ in sources:
            value = json.loads((rd / "manifest.json").read_text())["config"]["agent"]["params"].get(param)
            samples = json.loads((rd / "evallog.json").read_text())["samples"]
            if value is not None:
                outcomes.setdefault(value, []).extend(s["status"] == "success" for s in samples)
        rates = {v: sum(ok) / len(ok) for v, ok in outcomes.items()}
        best = max(rates, key=rates.get)                             # the value with the highest success rate
        out = Path(job.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "recap.json").write_text(json.dumps({"param": param, "success_rate": {str(v): r for v, r in rates.items()}}))
        return write_manifest(out, kind="policy_params", role="behaviour",
                              metrics={"episodes": sum(map(len, outcomes.values())), "best": best, "best_success": rates[best]},
                              provenance=Provenance(builder=self.name, sources=[r for _, r in sources], params=dict(job.params)))
```

Three rules:

Read inputs with `development_runs`
:   `development_runs(job.inputs, job.splits)` returns `(run_dir, SourceRef)` pairs for development runs only
    ([which runs a learner may read](../user-guide/learning.md#which-runs-a-learner-may-read)).

Write your files, then seal
:   Write everything into `job.out` and call `write_manifest` last. The manifest records a content digest over the
    files and every source run. Changing a file afterwards makes the artifact fail verification.

Choose `kind` and `role`
:   `role="behaviour"` means the artifact changes what the robot does, so only a promotion may activate it.
    `role="instrument"` means it measures, and it is trusted only after calibration
    ([artifact roles](../user-guide/learning.md#artifact-roles)).

## 3. Check it

```bash
uv run hylo plugin check learner my-recap
```

```text
learner my-recap: PASS
  [  ok] runs and seals a verifiable artifact: policy_params / behaviour, digest e3d96ccc61cef0ae
  [  ok] provenance lists development data only: splits ['search', 'search_val']
  [  ok] refuses gate / held-out splits
  [  ok] an identical job reuses the artifact
```

The check records the `search`, `search_val` and `gate` runs of MuJoCo planar reach and runs your learner on them. A
PASS means it seals a valid artifact from development data and refuses gate data; whether the artifact is useful is
step 5's job. The generated test in `tests/` runs the same check under pytest.

## 4. Run a job

A job names the learner, inputs, output and params ([train an artifact](../user-guide/learning.md#train-an-artifact)):

```json title="recap.json"
{"learner": "my-recap", "inputs": ["runs/demos"], "out": "runs/artifacts/recap"}
```

```bash
uv run hylo learn recap.json
```

```json
{
  "out": "runs/artifacts/recap",
  "kind": "policy_params",
  "role": "behaviour",
  "digest": "e3d96ccc61cef0ae",
  "splits": ["search"],
  "metrics": {"episodes": 80, "best": 0.3, "best_success": 1.0}
}
```

A job that asks for gate data is refused before anything is read:

```json title="leak.json"
{"learner": "my-recap", "inputs": ["runs/demos"], "out": "runs/artifacts/x", "splits": ["search", "gate"]}
```

```text
hylo learn: SplitLeak: gate / heldout data must never be used to build anything that is gated on it: ['gate']
```

Look up the artifact's store id. The artifact must be inside your [store](../user-guide/store.md), which is
`bench/runs` after Installation:

```bash
uv run hylo store ref runs/artifacts/recap
```

```text
artifact:recap@e3d96ccc61cef0ae
```

Configs reference artifacts by this id; keep the `@digest` ([use ids in configs](../user-guide/store.md#use-ids-in-configs)).

## 5. Use it in a campaign

The built-in `learn` generator connects a learner to a campaign. Each cycle it runs your learner on development runs,
checks the artifact's metrics, and proposes a config patch that uses them. A campaign configures its generator under
the `proposer` key. Save this in `bench/`:

```yaml title="recap_campaign.yaml"
schema_version: hylo.evolve/v0.1
name: mujoco-reach-recap
experiment: examples/configs/mujoco_reach.yaml
experiment_overrides: {benchmark.params: {protocol: rsi}, agent.params.kp: 0.02}
proposer:
  type: learn
  params:
    learner: my-recap
    params: {param: kp}
    data_roots: [runs/demos]
    patch: {agent.params.kp: "{metrics.best}"}
    require: {best_success: 0.9}
    hypothesis: "a gain of {metrics.best}, the best in the development runs, reaches more targets in time"
cycles: 1
out_dir: runs/evolve/mujoco-reach-recap
```

`data_roots`
:   More runs to learn from. The generator always adds this cycle's own development runs.

`patch`
:   The patch to propose. `{metrics.best}` is replaced by the value from the artifact's metrics.

`require`
:   Floors on the metrics. When one is not met, the generator proposes nothing.

The parent starts with a weak gain, `kp: 0.02`. The other parameters are in the
[hylo-evolve API](../api/packages/hylo-evolve.md).

```bash
uv run hylo evolve run recap_campaign.yaml
```

```text
[cycle 1] parent-search                      search     success=0.450 n=80 (2s)
[cycle 1] parent-search_val                  search_val success=0.400 n=40 (1s)
[cycle 1] cand-77ee16b64c-search_val         search_val success=1.000 n=40 (0s)
[cycle 1] parent-gate                        gate       success=0.350 n=40 (1s)
[cycle 1] cand-77ee16b64c-gate               gate       success=1.000 n=40 (0s)
[cycle 1] cand-77ee16b64c-heldout            heldout    success=1.000 n=40 (0s)
[cycle 1] parent-heldout                     heldout    success=0.400 n=40 (1s)
[cycle 1] done: promoted=cand-77ee16b64c heldout={...}
```

The learner read `runs/demos` and the parent's `search` and `search_val` runs from this cycle; by default the `learn`
generator reads both development splits ([splits](../user-guide/campaigns.md#splits)). It found `kp: 0.3` best, so the
candidate's patch is `{"agent.params.kp": 0.3}`. It passed the gate and was promoted. The archive entry in
`runs/evolve/mujoco-reach-recap/archive.jsonl` links the verdict to the generator `learn.my-recap@0.1` and the sealed
artifact ([read the result](../user-guide/campaigns.md#read-the-result)).

## Variants

=== "Online learner"

    An online learner learns by acting: each iteration it returns agent specs, the runner evaluates them on a
    development split, and the learner updates from the results. `hylo plugin new online_learner NAME` scaffolds one,
    and `online: true` in the `learn` generator runs it. `examples.cem` (hylo-plugins) is the reference
    ([extending Hylo](../harness/extending.md)).

=== "Heavy dependencies"

    A learner that needs torch runs in that venv: `uv run hylo learn job.json --python /path/to/venv/bin/python`, or
    `python:` in the `learn` generator. Install your package and Hylo's learning packages into that venv.

## Next

- Roles, the split guard and success judges: [learning](../user-guide/learning.md).
- Other generators: [adding a generator](adding-a-generator.md), [campaigns](../user-guide/campaigns.md).
- Reference: [hylo-learn API](../api/packages/hylo-learn.md), [hylo-evolve API](../api/packages/hylo-evolve.md),
  [`hylo learn`](../cli/index.md#hylo-learn), [`hylo evolve`](../cli/index.md#hylo-evolve),
  [`hylo plugin`](../cli/index.md#hylo-plugin).
