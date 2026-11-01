# Installation

This page sets up a workspace that can run the [quickstart](quickstart.md), and checks that it works.

You need Linux, Python 3.10 or newer and [uv](https://docs.astral.sh/uv/). No GPU is needed: everything on this page
runs on CPU. The OSMesa install script, used for camera rendering without a GPU and for LIBERO, assumes Ubuntu 24.04
on x86_64.

## Set up the workspace

Clone the harness into a new directory and run its bootstrap script there:

```bash
mkdir hylo && cd hylo
git clone https://github.com/HyloAI/hylo-harness.git harness
HYLO_GIT_BASE=https://github.com/HyloAI harness/dev/bootstrap.sh
```

The script clones bench, serve, studio, plugins and docs next to the harness. It writes a `pyproject.toml` that makes
this directory a uv workspace, and runs `uv sync`, which installs every package, editable, into `.venv`. The
deployments template is cloned separately; see [deployment](../user-guide/deployment.md). Rerun the script after you
add or remove a repository.

The workspace has three dependency groups:

| Group | Installs | For |
|---|---|---|
| `dev` (installed by default) | pytest, httpx | the tests |
| `demo` | imageio, imageio-ffmpeg, matplotlib, pillow | videos and figures from the examples |
| `docs` | mkdocs-material, mkdocstrings, mkdocs-gen-files, mkdocs-glightbox | building this site |

```bash
uv sync --group demo --group docs
```

## Register the run store

Register `bench/runs` as this machine's [store](../user-guide/store.md). The quickstart writes its runs there:

```bash
uv run hylo store init bench/runs      # recorded as `store:` in ~/.config/hylo/profile.yaml
uv run hylo store ls
```

`$HYLO_STORE`, when set, overrides the registered store. [Profiles](../configuration/profiles.md) has the full
lookup order.

## Check the installation

```bash
uv run hylo --help              # the subcommands of the installed packages
uv run hylo plugins             # every plugin: group, name, contract version, maturity, licence
```

`hylo plugins` should list `mujoco.planar_reach` and `baseline.planar_ik`; the quickstart uses both. To run the
tests, see [testing](../developer-guide/testing.md).

## Optional: Studio's web UI

Studio's web UI must be built once before `hylo playground` can show it. Without the build, Studio answers only
"frontend not built". The build needs Node.js 18 or later:

```bash
cd studio/web && npm install --ignore-scripts && npm run build && cd ../..
```

## Optional: camera rendering

MuJoCo comes with bench and needs nothing else for experiments. Camera rendering, used by the table-reach vision
variant and by figures, needs an OpenGL backend. On a machine with a GPU, set `MUJOCO_GL=egl`.

Without a GPU, install CPU-only OpenGL (OSMesa). This installs it into `~/.local/mesa` without root:

```bash
bench/scripts/install-osmesa-user.sh
```

Then set:

```bash
export MUJOCO_GL=osmesa
export PYOPENGL_PLATFORM=osmesa
export LD_LIBRARY_PATH=~/.local/mesa/root/usr/lib/x86_64-linux-gnu
```

## Optional: LIBERO and LeRobot

LIBERO and LeRobot need package versions that conflict with the workspace, so they run in their own venv inside
bench, through two named [runtimes](../configuration/profiles.md).

1. Install OSMesa as in [camera rendering](#optional-camera-rendering). LIBERO renders with it.
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

## Working on a subset of repositories

The workspace covers whichever repositories are present; tests that need a missing one skip.

| Checkout | What you can run |
|---|---|
| `harness` | contracts, the episode loop, learners and campaigns, on the `testing.*` test plugins |
| `harness` + `bench` | MuJoCo and LIBERO experiments, protocols, scorecards, leaderboards, the examples |
| `harness` + `serve` | policy servers and workcells |
| `harness` + `studio` | Studio (building its web UI needs Node.js 18 or later) |
| `harness` + `plugins` | the example plugins, written the way a third party would |

## Next

From here on, run commands from `bench/`, so runs and artifacts land in the store you registered:

- [Quickstart](quickstart.md): one example through all four steps.
- [Concepts](concepts.md): the words the other pages use.
