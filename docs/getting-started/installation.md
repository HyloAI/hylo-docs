# Installation

This page sets up a workspace that can run the [quickstart](quickstart.md), and checks that it works.

You need Linux, Python 3.10 or newer and [uv](https://docs.astral.sh/uv/). The first CPU experiment needs no GPU, language model, camera renderer or downloaded weights.
Run the setup commands below from the new workspace root.

## The development workspace

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

## The run and artifact store

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

## Optional setup

Only follow these when your chosen task needs them:

- <span id="studio-web-ui"></span>[Studio web UI](optional-environments.md#studio-web-ui).
- <span id="camera-rendering"></span>[Camera rendering](optional-environments.md#camera-rendering).
- <span id="strategy-development-tools"></span>[Strategy development tools](optional-environments.md#strategy-development-tools).
- <span id="libero-and-lerobot-policies"></span>[LIBERO and LeRobot policies](optional-environments.md#libero-and-lerobot-policies).
- <span id="a-subset-of-the-repositories"></span>[A subset of the repositories](optional-environments.md#a-subset-of-the-repositories).

For example videos or figures, run `uv sync --group demo` from the workspace root. To build the docs, use
`uv sync --group docs`. The default `dev` group contains the test tools.

## Next

[Run your first experiment](quickstart.md). Setup is complete when `hylo plugins` lists the two plugins above.
