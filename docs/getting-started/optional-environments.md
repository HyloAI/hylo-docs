# Optional environments

Set up only the components needed by your next task. Complete [Installation](installation.md) first.
Run commands from the **workspace root**, unless a step changes directory.

## Studio web UI

Studio's web UI must be built once before `hylo playground` can show it. Without the build, Studio answers only
"frontend not built". The build needs Node.js 18 or later:

```bash
cd studio/web && npm install --ignore-scripts && npm run build && cd ../..
```

## Camera rendering

MuJoCo comes with bench and needs nothing else for experiments. Camera rendering, used by the table-reach vision
variant and by figures, needs an OpenGL backend. On a machine with a GPU, set `MUJOCO_GL=egl`.

Without a GPU, install CPU-only OpenGL (OSMesa). The script assumes Ubuntu 24.04 on x86_64
and installs into `~/.local/mesa` without root:

```bash
bench/scripts/install-osmesa-user.sh
```

Then set:

```bash
export MUJOCO_GL=osmesa
export PYOPENGL_PLATFORM=osmesa
export LD_LIBRARY_PATH=~/.local/mesa/root/usr/lib/x86_64-linux-gnu
```

## Strategy development tools

The workspace discovers `hylo-manip`, `hylo-code-agents` and `hylo-tools` alongside the other packages. Reference
programs need the robot assets and camera rendering above, but no chat model. Assets are cached on first use.
Model-written programs and research sessions additionally need a supported chat backend, such as Ollama or an
API configured in the model specification. A local model must already be available at that endpoint.

Heavy perception and motion tools use `uv` worker environments: their first call can install separate dependencies
and download weights. Some primary backends require model access or registered body-model files; the tools expose
fallbacks and record the backend actually used. See [Developing programs](../user-guide/developing-strategies.md)
and the [environment variables](../configuration/environment-variables.md#strategy-development).

robosuite and RoboCasa have their own setup scripts under `bench/envs/robosuite` and `bench/envs/robocasa`.
They are optional; the existing CPU quickstart does not require those runtimes or a language model.

## LIBERO and LeRobot policies

LIBERO and LeRobot need package versions that conflict with the workspace, so they run in their own venv inside
bench, through two named [runtimes](../configuration/profiles.md).

1. Install OSMesa as in [camera rendering](#camera-rendering). LIBERO renders with it.
2. Build the LIBERO venv:

    ```bash
    bench/envs/libero/setup.sh
    ```

    The script builds `bench/envs/libero/.venv` (Python 3.12, CPU) with LIBERO and `lerobot[smolvla]`. It downloads
    the LIBERO assets (`lerobot/libero-assets`, research use only) and writes a non-interactive LIBERO config.

3. Check the two runtimes the script registered:

    ```bash
    uv run hylo profile show
    ```

    | Runtime | What runs there | Environment |
    |---|---|---|
    | `libero-sim` | the LIBERO simulator (`env.remote: {runtime: libero-sim}`) | OSMesa variables, `LIBERO_CONFIG_PATH`, thread limits |
    | `lerobot` | LeRobot policies (`agent: {type: remote, params: {runtime: lerobot}}`) | `HF_HOME=bench/envs/hf-home`, `HF_HUB_OFFLINE=1` |

4. Download model weights. The `lerobot` runtime runs offline and loads weights only from `bench/envs/hf-home`.
   `setup.sh` downloads none. Put each checkpoint into that cache once. SmolVLA for LIBERO also needs its
   vision-language backbone, `HuggingFaceTB/SmolVLM2-500M-Video-Instruct`:

    ```bash
    cd bench
    HF_HOME=envs/hf-home envs/libero/.venv/bin/python -c "from huggingface_hub import snapshot_download; \
        [snapshot_download(r) for r in ('lerobot/smolvla_libero', 'HuggingFaceTB/SmolVLM2-500M-Video-Instruct')]"
    ```

    Weight licences differ from the code's; the [plugin catalogue](../developer-guide/plugin-catalogue.md) lists
    them.

## A subset of the repositories

The workspace covers whichever repositories are present; tests that need a missing one skip.

| Checkout | What you can run |
|---|---|
| `harness` | contracts, the episode loop, learners and campaigns, on the `testing.*` test plugins |
| `harness` + `bench` | MuJoCo and LIBERO experiments, protocols, scorecards, leaderboards, the examples |
| `harness` + `serve` | policy servers and workcells |
| `harness` + `studio` | Studio (building its web UI needs Node.js 18 or later) |
| `harness` + `plugins` | the example plugins, written the way a third party would |

## Next

- [Choose your next task](next-steps.md).
- [Troubleshooting](../developer-guide/troubleshooting.md).
