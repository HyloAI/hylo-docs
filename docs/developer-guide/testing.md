# Testing

Every package tests itself. A test double lets the harness check its contracts without a simulator. The real
simulators check what the double cannot. A boundary lint keeps the repositories apart. This page covers how the
tests are laid out, how to run them, which tests skip and how to enable them, and what a new package should add.
For the workspace itself, see [contributing](contributing.md).

## Layout

| Where | What |
|---|---|
| `<repo>/<packages or adapters>/<dist>/tests/` | a package's own tests, next to its code; they import the package as installed |
| `harness/tests/integration/` | cross-package checks inside the harness: remote environments and agents in another process (`core.remote`), memory used by an agent through the kernel |
| `harness/dev/test_boundaries.py` | the boundary lint for every repository that is checked out (below) |
| `bench/packages/hylo-bench/tests/testing-reach.yaml` | a protocol over the test double, for hylo-bench's own tests only (not shipped) |

The workspace `pyproject.toml` (written by `harness/dev/workspace.py`) sets `testpaths` to the present code
repositories and `--import-mode=importlib`, so test files in different packages may share names.

## Running tests

```bash
uv run pytest                                   # every present repository, plus the boundary lint
uv run pytest harness                           # one repository
uv run pytest harness/packages/hylo-core          # one package
uv run pytest harness/dev                       # the boundary lint only
uv run pytest -rs                               # also list why tests skipped
```

A workspace does not need every repository. The harness alone, or the harness and one leaf, is a complete workspace,
and the tests adapt to what is present: the lint checks only the packages it finds, and tests that need a missing
repository skip. To check that a repository stands on its own, build a workspace from fresh clones:

```bash
mkdir /tmp/ws && cd /tmp/ws
git clone /path/to/harness harness && git clone /path/to/bench bench      # any subset that includes the harness
bash harness/dev/bootstrap.sh                                             # writes pyproject.toml, uv sync
uv run pytest
```

On the split of 2026-11-01 every subset passed: the harness alone 208 tests, the harness and bench 237, the harness
and serve 233, the harness and studio 217, the harness and plugins 217, all seven repositories 283 (plus skips).

## The boundary lint

`harness/dev/test_boundaries.py` reads `harness/dev/repos.toml` and checks:

| Test | Rule |
|---|---|
| `test_every_package_is_classified` | every present package is listed in the lint's `ALLOWED` table (a new package must be added) |
| `test_layering_never_points_from_the_base_to_a_leaf` | no package's allowed imports reach a repository it may not depend on |
| `test_package_imports_respect_layering` | each `Hylo.*` import in `src/`, and each `"pkg.mod:attr"` or `-m pkg.mod` string, targets an allowed package; heavy dependencies (`torch`, `jax`, `mujoco`, `langchain_core`, `langgraph`, `dspy`, `robosuite`) are imported only where allowed (`mujoco` in hylo-env-mujoco, `torch` in hylo-policy-lerobot) |
| `test_declared_dependencies_stay_within_reachable_repositories` | `pyproject.toml` dependencies stay within reachable repositories; a robot-side repository (serve) declares only `hylo-core` |
| `test_no_code_reaches_into_another_repository_by_path` | no code or config file contains a `../<repo>/` path (install scripts use an environment variable such as `HYLO_HARNESS`) |
| `test_the_workspace_file_matches_the_repositories` | the workspace `pyproject.toml` is what `workspace.py` would write now |

The rules and their reasons are in [repository structure](../design/repository-structure.md) and the
[package layering](../harness/dependency-graph.md).

## The test double

`hylo.testing` ships with hylo-core. Its plugins are named `testing.*`, are declared `test-double` in the
[plugin catalogue](plugin-catalogue.md), and are hidden from `hylo plugins` unless `--all` is given.

| Plugin | Group | Package |
|---|---|---|
| `testing.point_reach` | envs | hylo-core (`hylo.testing.point_reach`) |
| `testing/reach-v0` | benchmarks | hylo-eval |
| `testing.p_controller`, `testing.landmark` | agents | hylo-agents |
| `testing.rule_landmark` | reasoners | hylo-reasoners |
| `testing.summary` | learners | hylo-core (`hylo.testing.learners`) |

!!! warning "A test double, not an evaluation environment"
    It exists so contract tests run without a simulator. Examples, protocols, campaigns and published numbers use
    real simulators (MuJoCo, LIBERO).

`hylo.testing.setup.check_experiment(experiment=None, prefer="auto")` chooses where environment-dependent
checks run:

| `prefer` | Result |
|---|---|
| `"auto"` | MuJoCo planar reach (with the IK controller) when hylo-bench's `mujoco.planar_reach` is registered, else the test double |
| `"mujoco"` | MuJoCo planar reach, or `RuntimeError: MuJoCo planar reach is not installed (hylo-bench: hylo-env-mujoco)` |
| `"double"` | the test double |

An explicit experiment (a config path or an `ExperimentConfig`) always wins. `env_and_task(cfg)` returns a fresh
environment of that experiment and its first task instance.

## Conformance kits

Each contract has a check that a plugin's own tests call; `hylo plugin check` and `hylo conformance` run the same
checks on any registered plugin or config. The full table is in [contributing](contributing.md#conformance-kits).

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

```bash
uv run hylo plugin check policy policy.flow --params '{"path": "artifact:policy.flow"}'
uv run hylo plugin check learner my-recap --experiment bench/examples/configs/mujoco_reach.yaml
uv run hylo conformance bench/examples/configs/mujoco_reach.yaml --agent
```

The `hylo plugin new` templates generate a package whose tests already call its group's check.

## Tests that skip

| Test | Skips unless | To enable |
|---|---|---|
| `hylo-env-libero`: `test_remote_libero_episode_runs_end_to_end` | the `libero-sim` runtime is in the profile (or `bench/envs/libero/.venv` exists) and `~/.local/mesa/root/usr/lib/x86_64-linux-gnu/libOSMesa.so.8` exists | `bench/scripts/install-osmesa-user.sh`, then `bench/envs/libero/setup.sh` ([installation](../getting-started/installation.md)) |
| `hylo-env-mujoco`: `test_vision_variant_adds_camera_images_only_while_visible` | `MUJOCO_GL` is `egl` or `osmesa` | `MUJOCO_GL=osmesa PYOPENGL_PLATFORM=osmesa LD_LIBRARY_PATH=~/.local/mesa/root/usr/lib/x86_64-linux-gnu uv run pytest bench/adapters/hylo-env-mujoco` |
| `hylo-env-mujoco`: all | `mujoco` is importable | installed by hylo-env-mujoco |
| `hylo-reasoner-llm`: the live LLM chooser test | `HYLO_TEST_LLM=1` | a local Ollama server with the configured model, then `HYLO_TEST_LLM=1 uv run pytest harness/adapters/hylo-reasoner-llm` |
| `hylo-cli`: the policy and agent template tests | `hylo.envs.mujoco` is importable | check out hylo-bench next to the harness |
| `hylo-plugin-examples`: all | `hylo.envs.mujoco` is importable | hylo-bench |
| `hylo-playground`: the control-plane test with a real workcell | `hylo.serve` is importable (a fake workcell is used otherwise) | hylo-serve |
| `hylo-playground`: all | `fastapi` and `httpx` are importable | the workspace's `dev` dependency group |
| `hylo-core`: `test_ws_transport` | `websockets` is importable | a dependency of hylo-core |

`uv run pytest -rs` prints each skip with its reason.

## Unit tests and real-simulator tests

Unit tests run on the test double or on recorded data, finish in seconds, and need nothing but the venv. Tests in
bench (`hylo-env-mujoco`, `hylo-bench`), plugins and the CLI templates run MuJoCo episodes, and the LIBERO test starts
the simulator in its own venv. The whole suite takes about 3.5 minutes on the development workstation.

Keep tests that run a simulator small (a few episodes, short `max_steps`), seeded, and asserting on outcomes that
do not depend on timing. A realtime test uses `timing: {mode: realtime, clock: virtual}` with a fixed `latency_s`,
so it is deterministic.

## Tests for a new package

1. Put tests in `<package>/tests/`, importing the package by its installed name.
2. Call the conformance check for each plugin the package registers (the `hylo plugin new` templates show how).
3. Use `check_experiment()` for environment-dependent checks, so the tests run with the harness alone and on
   MuJoCo when bench is present.
4. Skip, with a reason, what needs hardware, a model download, a network service or another repository
   (`pytest.importorskip(..., reason=...)`, `pytest.mark.skipif(..., reason=...)`); never fail for a missing
   optional dependency.
5. Add the package to the lint's `ALLOWED` table, then run `python harness/dev/workspace.py .` in the workspace and
   `uv sync` (see [contributing](contributing.md#adding-a-package)).

## CI

CI is deferred. There is no CI configuration in the repositories yet. A CI job would run, per repository and for
the full workspace: `harness/dev/bootstrap.sh`, `uv run pytest`, and `hylo conformance` with `--agent` on the MuJoCo
example configs.
