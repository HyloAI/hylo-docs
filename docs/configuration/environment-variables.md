# Environment variables

What worldcurrent reads from the environment, and the third-party variables its setup relies on. Variables that
belong to one machine (paths, renderers, caches) are best set per runtime in the
[execution profile](profiles.md), so they reach exactly the component that needs them.

## worldcurrent

| Variable | Read by | Meaning | Default |
|---|---|---|---|
| `WC_PROFILE` | `core.profile` | path of this machine's execution profile | `~/.config/worldcurrent/profile.yaml` |
| `WC_STORE` | `core.store` | the run and artifact store directory; overrides `store:` in the profile | the profile's `store`, else `./runs` |
| `WORLDCURRENT_NO_PLUGIN_AUTOLOAD` | `core.registry` | `1`: do not load plugins from entry points; only explicitly registered plugins and `module:attr` references resolve | unset (entry points load) |
| `WC_HARNESS` | `bench/envs/libero/setup.sh` | the harness checkout to install into the LIBERO venv | `../harness` (side by side) |
| `WC_GIT_BASE` | `harness/dev/bootstrap.sh` | clone missing repositories from `$WC_GIT_BASE/worldcurrent-<name>.git` | unset: missing repositories are skipped |
| `WC_TEST_LLM` | the LLM reasoner tests | `1`: run the tests that call the local Ollama server | unset (skipped) |

Tokens are never read from a fixed variable. Pass them on the command line (`--token`) or name a variable that holds
one: `wc serve env|agent ... --token-env WC_TOKEN`, or `token_env: WC_TOKEN` in a `remote.ws` agent's params. The
templates use `$WC_TOKEN` by convention.

## Rendering and simulators

| Variable | Used by | Meaning |
|---|---|---|
| `MUJOCO_GL` | MuJoCo, LIBERO | renderer: `osmesa` (CPU, the user-space Mesa from `bench/scripts/install-osmesa-user.sh`) or `egl` (GPU). Unset: no off-screen rendering; image observations and the rendering tests are skipped |
| `PYOPENGL_PLATFORM` | LIBERO (robosuite) | must match `MUJOCO_GL` (`osmesa`) |
| `LD_LIBRARY_PATH` | the `libero-sim` runtime | where the user-space `libOSMesa.so` is (`~/.local/mesa/root/usr/lib/x86_64-linux-gnu`) |
| `LIBERO_CONFIG_PATH` | LIBERO | the non-interactive LIBERO config written by `setup.sh` (`bench/envs/libero/config`) |
| `OMP_NUM_THREADS`, `LP_NUM_THREADS` | numpy / OSMesa (llvmpipe) | threads per simulator process; kept low because benchmarks run many workers |

## Models

| Variable | Used by | Meaning |
|---|---|---|
| `HF_HOME` | LeRobot, Hugging Face Hub | the model and dataset cache (`bench/envs/hf-home` in the `lerobot` runtime) |
| `HF_HUB_OFFLINE` | LeRobot | `1`: never download; use the cache. Set in the `lerobot` runtime and by the self-training learner (unless already set) |
| `TOKENIZERS_PARALLELISM` | tokenizers | `false`: no fork warnings in worker processes (set by the action-memory builder and the self-training learner) |
| `TORCHDYNAMO_DISABLE` | torch | `1`: no torch.compile; set by some LIBERO configs (`libero10_memory`, `libero10_noise`) and by self-training |

## Where to set them

=== "In the profile (recommended)"

    ```bash
    uv run wc profile set-runtime libero-sim --python bench/envs/libero/.venv/bin/python \
        --env MUJOCO_GL=osmesa --env PYOPENGL_PLATFORM=osmesa
    ```

=== "In a config (one-off)"

    ```yaml
    env:
      type: libero
      remote: {runtime: libero-sim, env: {OMP_NUM_THREADS: "2", LP_NUM_THREADS: "4"}}
    ```

=== "In the shell"

    ```bash
    MUJOCO_GL=osmesa uv run pytest bench/adapters/wc-env-mujoco
    ```

Variables in the profile or a config reach only the subprocess of that component; the parent process and other
components are not affected. None of them enter the experiment digest.
