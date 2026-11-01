# Testing

Every package tests itself. A test double lets the harness check its contracts without a simulator. The real
simulators check what the double cannot. A boundary lint keeps the repositories apart.

## Running tests

Run these from the workspace directory, not from `bench/`:

```bash
uv run pytest                                   # every present repository, plus the boundary lint
uv run pytest harness                           # one repository
uv run pytest harness/packages/hylo-core        # one package
uv run pytest harness/dev                       # the boundary lint only
uv run pytest -rs                               # also list why tests skipped
```

Tests that need a missing repository skip. To check that a repository stands on its own, build a workspace from
fresh clones:

```bash
mkdir /tmp/ws && cd /tmp/ws
git clone /path/to/harness harness && git clone /path/to/bench bench      # any subset that includes the harness
bash harness/dev/bootstrap.sh                                             # writes pyproject.toml, runs uv sync
uv run pytest
```

There is no CI. Before pushing, run `uv run pytest` in a workspace with the repositories you changed, and
`uv run hylo conformance CONFIG --agent` on the MuJoCo example configs.

Unit tests run on the test double or on recorded data, finish in seconds, and need nothing but the venv. Tests in
bench, plugins and the CLI templates run MuJoCo episodes. The LIBERO test starts the simulator in its own venv.

## Tests that skip

| Test | Skips unless | To enable |
|---|---|---|
| `hylo-env-libero`: `test_remote_libero_episode_runs_end_to_end` | the `libero-sim` runtime is in the profile (or `bench/envs/libero/.venv` exists), and user-space OSMesa is installed | `bench/scripts/install-osmesa-user.sh`, then `bench/envs/libero/setup.sh` ([installation](../getting-started/installation.md#libero-and-lerobot-policies)) |
| `hylo-env-mujoco`: `test_vision_variant_adds_camera_images_only_while_visible` | `MUJOCO_GL` is `egl` or `osmesa` | `MUJOCO_GL=osmesa PYOPENGL_PLATFORM=osmesa LD_LIBRARY_PATH=~/.local/mesa/root/usr/lib/x86_64-linux-gnu uv run pytest bench/adapters/hylo-env-mujoco` |
| `hylo-reasoner-llm`: the live LLM chooser test | `HYLO_TEST_LLM=1` | a local Ollama server with the configured model, then `HYLO_TEST_LLM=1 uv run pytest harness/adapters/hylo-reasoner-llm` |
| `hylo-cli`: the policy and agent template tests | `hylo.envs.mujoco` is importable | check out hylo-bench next to the harness |
| `hylo-plugin-examples`: all | `hylo.envs.mujoco` is importable | hylo-bench |
| `hylo-playground`: the control-plane test with a real workcell | `hylo.serve` is importable (a fake workcell is used otherwise) | hylo-serve |
| `hylo-playground`: `test_playground.py` | `httpx` is importable | the workspace's `dev` dependency group, which `uv sync` installs |

## Tests for a new package

1. Put tests in `<package>/tests/`, importing the package by its installed name.
2. Call the conformance check for each plugin the package registers (see below). The `hylo plugin new` templates
   generate tests that already do.
3. Use `check_experiment()` for environment-dependent checks, so the tests run with the harness alone and on MuJoCo
   when bench is present.
4. Skip, with a reason, what needs hardware, a model download, a network service, another repository or an optional
   dependency (`pytest.importorskip(..., reason=...)`, `pytest.mark.skipif(..., reason=...)`). Never skip for a
   missing required dependency: that is a packaging error, and the test should fail.
5. Keep tests that run a simulator small (a few episodes, short `max_steps`), seeded, and asserting on outcomes that
   do not depend on timing. A realtime test uses `timing: {mode: realtime, clock: virtual}` with a fixed
   `latency_s`, so it is deterministic.

The steps for creating the package itself are in [contributing](contributing.md#adding-a-package).

### The test double

`hylo.testing` ships with hylo-core. Its plugins are named `testing.*`, are declared `test-double` in the
[plugin catalogue](plugin-catalogue.md), and are hidden from `hylo plugins` unless `--all` is given.

| Plugin | Group | Package |
|---|---|---|
| `testing.point_reach` | envs | hylo-core |
| `testing/reach-v0` | benchmarks | hylo-eval |
| `testing.p_controller`, `testing.landmark` | agents | hylo-agents |
| `testing.rule_landmark` | reasoners | hylo-reasoners |
| `testing.summary` | learners | hylo-core |

!!! warning "A test double, not an evaluation environment"
    It exists so contract tests run without a simulator. Examples, protocols, campaigns and published numbers use
    real simulators (MuJoCo, LIBERO).

`hylo.testing.setup.check_experiment(experiment=None, prefer="auto")` chooses where environment-dependent checks
run. An explicit experiment (a config path or an `ExperimentConfig`) always wins.

| `prefer` | Result |
|---|---|
| `"auto"` | MuJoCo planar reach (with the IK controller) when hylo-bench's `mujoco.planar_reach` is registered, else the test double |
| `"mujoco"` | MuJoCo planar reach, or `RuntimeError: MuJoCo planar reach is not installed (hylo-bench: hylo-env-mujoco)` |
| `"double"` | the test double |

A conformance test for a policy. `MyPolicy` stands for your own class:

```python
from hylo.testing.conformance import check_policy
from hylo.testing.setup import check_experiment, env_and_task

def test_conformance():
    env, task = env_and_task(check_experiment())
    try:
        report = check_policy(MyPolicy(), env, task)
        assert report.ok, report.summary()
    finally:
        env.close()
```

## Conformance kits

Every contract has a check that a plugin's own tests call. The checks live in `hylo.testing.conformance` (hylo-core),
`hylo.eval.conformance`, `hylo.learn.conformance` and `hylo.evolve.conformance`. The CLI runs the same checks on any
registered plugin or config:

| Contract | Check | From the CLI |
|---|---|---|
| environment | `check_environment` | `hylo conformance CONFIG` |
| agent | `check_agent` | `hylo conformance CONFIG --agent`, `hylo plugin check agent NAME` |
| policy | `check_policy` | `hylo plugin check policy NAME` |
| guard | `check_guard` | `hylo plugin check guard NAME` |
| memory store | `check_memory_store` | |
| scorer | `check_scorer` | |
| gate test | `check_gate_test` (hylo-eval) | `hylo plugin check gate_test NAME` |
| learner, online learner | `check_learner` (hylo-learn) | `hylo plugin check learner NAME`, `hylo plugin check online_learner NAME` |
| data source | `check_datasource` (hylo-learn) | `hylo plugin check datasource NAME` |
| success judge | `check_judge` (hylo-learn) | `hylo plugin check judge NAME` |
| generator | `check_generator` (hylo-evolve) | `hylo plugin check generator NAME` |

`hylo plugin check` builds the plugin with `--params` (JSON). It runs environment-dependent checks on
`--experiment`, else MuJoCo planar reach when installed, else the test double. It also warns when the plugin's
declaration (contract version, maturity, licence) is missing.

```bash
uv run hylo plugin check policy policy.flow --params '{"path": "artifact:policy.flow"}'
uv run hylo plugin check learner my-recap
uv run hylo conformance bench/examples/configs/mujoco_reach.yaml --agent
```

The learner and generator checks record runs on the `search`, `search_val` and `gate` splits. With `--experiment`,
name a config whose benchmark has those splits (on MuJoCo: `benchmark: {..., params: {protocol: rsi}}`).
`bench/examples/configs/mujoco_reach.yaml` uses the standard splits, so the learner check fails on it with
`KeyError: 'search'`.

## The boundary lint

`harness/dev/test_boundaries.py` runs one test per [repository and package rule](contributing.md#repository-and-package-rules);
`uv run pytest harness/dev -v` lists them. The path rule reads code and config files (`.py`, `.yaml`, `.yml`,
`.toml`, `.ts`, `.tsx`, `.json`) in the code repositories. It does not read shell scripts, hylo-docs or the
deployments template.

## Layout

| Where | What |
|---|---|
| `<repo>/<packages or adapters>/<dist>/tests/` | a package's own tests, next to its code; they import the package as installed |
| `harness/tests/integration/` | cross-package checks inside the harness: remote environments and agents in another process, memory used through the episode loop |
| `harness/dev/test_boundaries.py` | the boundary lint for every repository that is checked out |
| `bench/packages/hylo-bench/tests/testing-reach.yaml` | a protocol over the test double, for hylo-bench's own tests only (not shipped) |
