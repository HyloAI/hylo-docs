# Execution profiles

An experiment config says **what** is measured. Where an interpreter lives, which rendering library to load and
where the model cache is differ from machine to machine, and must not change an experiment's identity. They live in
the machine's execution profile instead ([RFC-0005 part 1](../rfcs/RFC-0005-architecture-measurement-and-placement.md)).

A profile (`wc.profile/v0.1`, `worldcurrent.core.profile`) is one YAML file per machine:

```yaml
schema_version: wc.profile/v0.1
runtimes:
  libero-sim:                                    # the LIBERO simulator
    python: /home/me/worldcurrent/bench/envs/libero/.venv/bin/python
    env:
      MUJOCO_GL: osmesa
      PYOPENGL_PLATFORM: osmesa
      LD_LIBRARY_PATH: ~/.local/mesa/root/usr/lib/x86_64-linux-gnu
      LIBERO_CONFIG_PATH: /home/me/worldcurrent/bench/envs/libero/config
      OMP_NUM_THREADS: '1'
      LP_NUM_THREADS: '2'
  lerobot:                                       # LeRobot policies (SmolVLA, pi0, ...)
    python: /home/me/worldcurrent/bench/envs/libero/.venv/bin/python
    env:
      HF_HOME: /home/me/worldcurrent/bench/envs/hf-home
      HF_HUB_OFFLINE: '1'
      TOKENIZERS_PARALLELISM: 'false'
store: /home/me/worldcurrent/bench/runs           # the run and artifact store
```

It is found at `$WC_PROFILE`, else `~/.config/worldcurrent/profile.yaml`. A machine without a profile has no
runtimes and uses `./runs` as its store.

## Runtimes

A runtime is a named interpreter plus environment variables: the venv a component runs in when it cannot share
the main one (a simulator with pinned dependencies, a policy stack with its own torch, a robot SDK). Configs name the
runtime and never a path:

```yaml
env:
  type: libero
  remote: {runtime: libero-sim}                  # the environment runs in a subprocess with this runtime
agent:
  type: remote
  params:
    ref: lerobot.steered
    runtime: lerobot                             # the agent too
    params: {repo_id: lerobot/smolvla_libero}
```

The same config therefore runs on the workstation, the GPU machine and the robot computer, from any directory, and
has the same digest on all of them: `env.remote` and a remote agent's `runtime`, `python` and `env` are left out of
the digest.

## Commands

```bash
uv run wc profile show                                       # the profile and where it is
uv run wc profile set-runtime robot --python ~/robot/.venv/bin/python --env HF_HOME=~/hf
uv run wc profile remove-runtime robot
uv run wc store init ~/worldcurrent/runs                     # record this machine's store (see the store guide)
```

`set-runtime` adds or replaces a runtime. `--python` is stored as an absolute path without following symlinks, so a
venv's interpreter keeps its venv. `--env KEY=VALUE` can be repeated; values are stored as given.

`bench/envs/libero/setup.sh` builds the LIBERO + LeRobot venv and registers both runtimes (`libero-sim` and
`lerobot`) with the paths of the bench checkout it ran in. Running it again re-registers them.

## Resolution rules

When a component starts in a runtime (`worldcurrent.core.profile.resolve`):

1. the runtime named in the config is looked up in this machine's profile; an unknown name is an error that says
   which runtimes exist and how to register the missing one;
2. explicit `python` and `env` in the config, if any, override the runtime's (for a one-off; they are not
   measured either);
3. `~` and `$VARS` in the interpreter path and in every value are expanded when the component starts, not when the
   profile is written;
4. the subprocess gets the parent's environment plus these variables.

The store directory follows its own order: `--root` on `wc store`, then `$WC_STORE`, then `store:` in the profile,
then `./runs` ([store](../user-guide/store.md)).

## Machines in a lab

| Machine | Typical runtimes | Store |
|---|---|---|
| workstation | `libero-sim`, `lerobot` | the main store, where campaigns and benchmarks write |
| GPU machine | `lerobot` (policy server, learners) | its own, synced with `wc store push/pull` |
| robot computer | `robot` (the robot SDK venv) | where the workcell writes, pulled by the workstation |

The profile is personal to each machine and is not committed anywhere. What is shared (workcell configs, safety
limits) belongs in the [deployments repository](deployments-repo.md).
