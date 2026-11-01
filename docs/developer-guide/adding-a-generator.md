# Adding a generator

You will write a generator that proposes controller-gain changes, then run a campaign to test whether a candidate
passes the gate. To build a model from runs instead, write a [learner](adding-a-learner.md). You need the
[development workspace](../getting-started/installation.md) with hylo-bench.

## 1. Create and install the package

From the workspace root, create the package in `plugins/packages/`:

```bash
uv run hylo plugin new generator my-gain --dir plugins/packages
```

This creates `plugins/packages/hylo-plugin-my-gain` with the module `wc_my_gain`. Add `license = "Apache-2.0"` (or
your licence) under `[project]` in its `pyproject.toml`. Then add it to the workspace and install it, as in
[adding a policy](adding-a-policy.md#1-scaffold-the-package). From here on, run commands from `bench/`:

```bash
uv run python harness/dev/workspace.py
uv sync                                     # add the --group options you used in Installation
cd bench
uv run hylo plugins | grep my-gain
```

```text
generators   my-gain                        hylo.generator/v0.1  unverified      Apache-2.0
```

## 2. Write propose()

A generator has a `name` and one method, `propose(diagnosis, cfg, parent_id, archive)`, which returns
`(Candidate, hypothesis)` pairs ([contracts](../api/contracts.md)). The scaffold scales one numeric config value.
Update its hypothesis to state the expected improvement:

```python title="src/wc_my_gain/plugin.py"
from __future__ import annotations

from hylo.core.improvement import Candidate


class MyGainProposer:
    name = "my-gain@0.1"

    def __init__(self, path: str = "agent.params.kp", factors: tuple[float, ...] = (1.5,)) -> None:
        self.path, self.factors = path, factors

    def propose(self, diagnosis, cfg, parent_id, archive):
        node = cfg.model_dump(mode="json")
        for k in self.path.split("."):
            node = node[k]
        return [(Candidate(patch={self.path: float(node) * f}, rationale=f"scale by {f}", parent_id=parent_id,
                           generator=self.name), f"scaling {self.path} by {f} raises the success rate")
                for f in self.factors]
```

What `propose()` receives:

- `diagnosis`: the parent's `search` results, including failure summaries and the `run_dir` for reading traces.
- `cfg`: the parent's experiment config. `parent_id` names the parent.
- `archive`: previous candidates and their results, including gate results
  ([what generators see](../user-guide/campaigns.md#splits)).

Each `Candidate` is a `patch` of dotted config paths, a `rationale`, the `parent_id` and the `generator` name. A patch
may not touch the [protected settings](../user-guide/safety.md#safety-in-campaigns).

## 3. Check it

```bash
uv run hylo plugin check generator my-gain
```

```text
generator my-gain@0.1: PASS
  [  ok] proposes (Candidate, hypothesis) pairs: 1 candidates
  [  ok] candidates stay outside protected scopes and apply to the config
  [  ok] candidates name their generator
```

The check calls `propose()` once with a MuJoCo planar reach diagnosis. A PASS means the candidates are well formed and
allowed, not that they help.

## 4. Run it in a campaign

A campaign configures its generator under the `proposer` key. Save this in `bench/`:

```yaml title="gain_campaign.yaml"
schema_version: hylo.evolve/v0.1
name: mujoco-reach-my-gain
experiment: examples/configs/mujoco_reach.yaml
experiment_overrides: {benchmark.params: {protocol: rsi}, agent.params.kp: 0.02}
proposer: {type: my-gain, params: {factors: [4.0, 10.0]}}
cycles: 1
out_dir: runs/evolve/mujoco-reach-my-gain
```

The parent starts with a weak gain, `kp: 0.02`.

```bash
uv run hylo evolve run gain_campaign.yaml
```

```text
[cycle 1] parent-search                      search     success=0.450 n=80 (2s)
[cycle 1] parent-search_val                  search_val success=0.400 n=40 (1s)
[cycle 1] cand-71e72a5f60-search_val         search_val success=1.000 n=40 (0s)
[cycle 1] cand-223390d4c4-search_val         search_val success=1.000 n=40 (0s)
[cycle 1] parent-gate                        gate       success=0.350 n=40 (1s)
[cycle 1] cand-71e72a5f60-gate               gate       success=1.000 n=40 (0s)
[cycle 1] cand-71e72a5f60-heldout            heldout    success=1.000 n=40 (0s)
[cycle 1] parent-heldout                     heldout    success=0.400 n=40 (1s)
[cycle 1] done: promoted=cand-71e72a5f60 heldout={...}
```

## 5. Read the verdict

`runs/evolve/mujoco-reach-my-gain/archive.jsonl` has one entry per candidate. `kp: 0.08` (factor 4) passed the gate
and was `promoted`. `kp: 0.2` (factor 10) succeeded on `search_val` but was `archived` without entering the gate
([read the result](../user-guide/campaigns.md#results)).

## Next

- Propose from a learned artifact with the built-in `learn` generator: [adding a learner](adding-a-learner.md).
- Run and approve campaigns: [campaigns](../user-guide/campaigns.md).
- Reference: [hylo-evolve API](../api/packages/hylo-evolve.md), [`hylo evolve`](../cli/index.md#hylo-evolve),
  [`hylo plugin`](../cli/index.md#hylo-plugin).
