# Execution profiles

Anything that depends only on the machine (interpreters, renderers, model caches, the store) goes in its execution
profile, not in the experiment config.

## Configure this machine

```bash
uv run hylo profile show                         # the profile and where it is
uv run hylo profile set-runtime robot --python ~/robot/.venv/bin/python --env HF_HOME=~/hf
uv run hylo profile remove-runtime robot
cd bench && uv run hylo store init runs          # record bench/runs as this machine's store
```

`set-runtime` replaces the entire runtime. Pass every `--env` you want to keep, or the ones you leave out are gone.
`--env KEY=VALUE` can be repeated, and values are stored as given. `--python` is stored as an absolute path without
resolving symlinks, so the interpreter stays in its venv.

`bench/envs/libero/setup.sh` builds the LIBERO and LeRobot venv and registers two runtimes, `libero-sim` and
`lerobot`, with the paths of the bench checkout it ran in. Run it again to re-register them.

## The profile file

Each machine has one profile: `~/.config/hylo/profile.yaml`, or wherever `$HYLO_PROFILE` points. A machine without a
profile has no runtimes.

```yaml title="~/.config/hylo/profile.yaml"
schema_version: hylo.profile/v0.1
runtimes:
  libero-sim:                                    # the LIBERO simulator
    python: /home/me/hylo/bench/envs/libero/.venv/bin/python
    env:
      MUJOCO_GL: osmesa
      LIBERO_CONFIG_PATH: /home/me/hylo/bench/envs/libero/config
store: /home/me/hylo/bench/runs                  # the run and artifact store
```

[Environment variables](environment-variables.md) lists the variables a runtime usually carries.

## Runtimes

A *named runtime* is a Python interpreter plus environment variables, for a component that needs its own venv: a
simulator with pinned dependencies, a policy stack with its own torch, a robot SDK. Configs name it, never a path:

```yaml
env:
  type: libero
  remote: {runtime: libero-sim}                  # run the environment in a subprocess with this runtime
```

A remote agent names its runtime the same way ([experiments](../user-guide/experiments.md)). The `runtime:` block of
a workcell config is something else: it holds the workcell's realtime timing settings.

When a component starts in a runtime:

1. Hylo looks up the name in this machine's profile. An unknown name is an error that lists the known runtimes and
   the `set-runtime` command that registers the missing one.
2. An explicit `python` or `env` in the config overrides the runtime's values, for a one-off.
3. `~` and `$VARS` in environment values, and in a `python` written by hand, are expanded when the component starts.
4. The subprocess gets the parent's environment plus the runtime's variables.

## Store

Hylo finds the store in this order: `--root` on `hylo store`, then `$HYLO_STORE`, then `store:` in the profile, then
`./runs`. `hylo store where` prints the one in use. See [the store](../user-guide/store.md).

## Machines in a lab

| Machine | Typical runtimes | Store |
|---|---|---|
| workstation | `libero-sim`, `lerobot` | the main store, where campaigns and benchmarks write |
| GPU machine | `lerobot` (policy server, learners) | its own, synced with `hylo store push` and `pull` |
| robot computer | `robot` (the robot SDK venv) | where the workcell writes, pulled by the workstation |

The profile belongs to one machine and is not committed anywhere. What a lab shares (workcell configs, safety
limits) belongs in the [deployments repository](deployments-repo.md).
