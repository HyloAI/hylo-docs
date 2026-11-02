# Environment variables

The variables Hylo reads, and the third-party variables its setup relies on.

## Where to set them

=== "In the profile (recommended)"

    Set a component's variables on its runtime in the [execution profile](profiles.md). `set-runtime` replaces the
    whole runtime, so pass every variable again:

    ```bash
    uv run hylo profile set-runtime robot --python ~/robot/.venv/bin/python \
        --env HF_HOME=~/hf --env HF_HUB_OFFLINE=1
    ```

    For LIBERO, run `bench/envs/libero/setup.sh` instead: it registers the full set.

=== "In a config (one-off)"

    ```yaml
    env:
      type: libero
      remote: {runtime: libero-sim, env: {OMP_NUM_THREADS: "2", LP_NUM_THREADS: "4"}}
    ```

=== "In the shell"

    ```bash
    MUJOCO_GL=osmesa PYOPENGL_PLATFORM=osmesa LD_LIBRARY_PATH=~/.local/mesa/root/usr/lib/x86_64-linux-gnu \
        uv run pytest bench/adapters/hylo-env-mujoco
    ```

Variables in the profile or a config reach only that component's subprocess. Set `HYLO_PROFILE`, `HYLO_STORE` and
the contributor variables in the shell: Hylo reads them before it starts any component.

## Hylo

| Variable | Read by | Meaning | Default |
|---|---|---|---|
| `HYLO_PROFILE` | every `hylo` command | path of this machine's execution profile | `~/.config/hylo/profile.yaml` |
| `HYLO_STORE` | every `hylo` command | the store directory; overrides `store:` in the profile | the profile's `store:`, else `./runs` |
| `HYLO_NO_PLUGIN_AUTOLOAD` | the plugin registry | `1`: ignore installed plugin packages; only `module:attr` references and plugins registered in code work | unset: installed plugins load |

## Tokens

Hylo has no fixed token variable. `hylo serve env` and `hylo serve agent` take `--token-env NAME`, and a `remote.ws`
agent takes `token_env: NAME` in its params, so the token never appears on a command line. `hylo serve policy`,
`hylo serve workcell` and `hylo playground` take `--token VALUE`, which shows in the machine's process list. The
templates keep the token in `HYLO_TOKEN`. [Security](../user-guide/security.md) covers each service.

## Rendering and simulators

| Variable | Used by | Meaning |
|---|---|---|
| `MUJOCO_GL` | MuJoCo, LIBERO | renderer: `osmesa` (CPU, user-space Mesa) or `egl` (GPU). Unset: no off-screen rendering, so no image observations |
| `PYOPENGL_PLATFORM` | LIBERO (robosuite) | must match `MUJOCO_GL` (`osmesa`) |
| `LD_LIBRARY_PATH` | the `libero-sim` runtime | where the user-space `libOSMesa.so` is |
| `LIBERO_CONFIG_PATH` | LIBERO | the non-interactive LIBERO config that `setup.sh` writes |
| `OMP_NUM_THREADS`, `LP_NUM_THREADS` | numpy, OSMesa (llvmpipe) | threads per simulator process; kept low because benchmarks run many workers |

## Models

| Variable | Used by | Meaning |
|---|---|---|
| `HF_HOME` | LeRobot, Hugging Face Hub | the model and dataset cache (`bench/envs/hf-home` in the `lerobot` runtime) |
| `HF_HUB_OFFLINE` | LeRobot | `1`: never download, use the cache. Set in the `lerobot` runtime |
| `TOKENIZERS_PARALLELISM` | tokenizers | `false`: no fork warnings in worker processes |
| `TORCHDYNAMO_DISABLE` | torch | `1`: no `torch.compile` |

## Strategy development

| Variable | Read by | Meaning | Default |
|---|---|---|---|
| `HYLO_ASSETS` | robot and motion asset loaders | cache for downloaded robot/character assets, robot packs and policy files | `~/.cache/hylo/assets` |
| `HYLO_STAGES` | `hylo stage` | where stages are kept | `runs/stages` |
| `HYLO_TOOLS_CACHE` | tool runner | worker requests, outputs and small model assets | `~/.cache/hylo/tools` |
| `HYLO_TOOLS_THREADS` | tool runner | CPU threads per worker | `32` |
| `HYLO_TOOLS_UV` | tool runner | `uv` executable used for independent worker environments | `uv` on PATH |

Choose chat endpoints, model names and budgets in the model/session specification. API backends can read provider
credentials from environment variables; keep credentials out of configs and recorded prompts. Model access and
body-model registration requirements are backend-specific. See [Developing robot skills](../user-guide/developing-strategies.md).

## Development

| Variable | Read by | Meaning | Default |
|---|---|---|---|
| `HYLO_GIT_BASE` | `harness/dev/bootstrap.sh` | clone missing repositories from `$HYLO_GIT_BASE/hylo-<name>.git` | unset: missing repositories are skipped |
| `HYLO_HARNESS` | `bench/envs/libero/setup.sh` | the harness checkout to install into the LIBERO venv | `../harness`, side by side |
| `HYLO_TEST_LLM` | the LLM reasoner tests | `1`: run the tests that call a local Ollama server | unset: skipped |
