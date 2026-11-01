# Troubleshooting

Error messages as Hylo prints them, why they happen, and what to do. Paths in messages are shortened with `...`.
Commands run from `bench/` unless an entry says otherwise.

| Message starts with | Section |
|---|---|
| `... pyproject.toml is stale`, `AssertionError: run python harness/dev/workspace.py`, `ModuleNotFoundError`, `ValidationError ... extra_forbidden` | [Installing and setting up](#install-and-workspace) |
| `KeyError: "runtime '...' is not in ...` | [Installing and setting up](#install-and-workspace) |
| `EnvironmentFault`, `KeyError: "no ... plugin named`, `IncompatibleComponents`, `watchdog:` | [Running an experiment](#experiments-and-the-episode-loop) |
| `ValueError: overrides ...`, `ValueError: different protocols`, `KeyError: "unknown protocol` | [Benchmarks and scorecards](#benchmarks) |
| `SplitLeak`, `... content digest ... != manifest`, a candidate `rejected` at stage 0 | [Learning and campaigns](#artifacts-and-campaigns) |
| `artifact:... not found`, `... is referred to by`, `sync refused`, `rsync` | [The store](#the-store) |
| `[Errno 98] ... address already in use`, HTTP 401 or 409 from a workcell | [Serving and workcells](#serve-and-studio) |
| `IncompatiblePlugin`, `cannot build ...`, `warning: ... declares no contract version` | [Writing plugins](#plugins) |

## Install and workspace

??? question "`.../pyproject.toml is stale: run python harness/dev/workspace.py .` or `AssertionError: run python harness/dev/workspace.py`"
    **Cause:** the workspace file no longer matches the repositories present. A repository or package was added or
    removed, or `workspace.py` changed. `workspace.py --check` prints the first message; the boundary lint under
    pytest prints the second.

    **Fix:** in the workspace directory, run:

    ```bash
    uv run --no-project --python '>=3.11' python harness/dev/workspace.py .
    uv sync
    ```

    **Check:** `uv run pytest harness/dev` passes `test_the_workspace_file_matches_the_repositories`.

??? question "`ModuleNotFoundError: No module named 'hylo.envs.mujoco'` (or another Hylo package)"
    **Cause:** the repository that provides it is not checked out next to the harness, or `uv sync` has not run since
    it was added.

    **Fix:** run `harness/dev/bootstrap.sh` in the workspace directory. It clones missing repositories when
    `HYLO_GIT_BASE` is set, and reinstalls everything ([installation](../getting-started/installation.md)).

??? question "`pydantic_core._pydantic_core.ValidationError: ... Extra inputs are not permitted [type=extra_forbidden ...]`"
    **Cause:** the config contains a key Hylo does not know. The line before names it, for example `worker` instead of
    `workers`.

    **Fix:** correct the key. `uv run hylo schema experiment` prints the experiment schema.

??? question "`KeyError: "runtime 'libero-sim' is not in ~/.config/hylo/profile.yaml (known: -); register it with: hylo profile set-runtime libero-sim --python PATH [--env KEY=VALUE ...]"`"
    **Cause:** the config names a runtime this machine's profile does not have.

    **Fix:** for `libero-sim` and `lerobot`, run `bench/envs/libero/setup.sh`, which builds the venv and registers
    both. For any other runtime, register its venv with `uv run hylo profile set-runtime NAME --python PATH`. If you
    keep the profile elsewhere, set `HYLO_PROFILE` in the shell.

    **Check:** `uv run hylo profile show` lists the runtime. See [execution profiles](../configuration/profiles.md).

## Experiments and the episode loop

??? question "`EnvironmentFault: env server exited with code 1`, after a traceback"
    **Cause:** a remote environment's process (`env.remote`) died before it answered. Its own traceback is printed
    above. Common causes:

    - the runtime's venv lacks the environment's package;
    - rendering is not set up: LIBERO needs `MUJOCO_GL=osmesa`, `PYOPENGL_PLATFORM=osmesa` and `LD_LIBRARY_PATH`
      pointing at user-space OSMesa;
    - `LIBERO_CONFIG_PATH` does not point at the config `setup.sh` wrote.

    **Fix:** for LIBERO, rerun `bench/scripts/install-osmesa-user.sh` and `bench/envs/libero/setup.sh`. They install
    the package and register the `libero-sim` runtime with these variables.

    **Check:** `uv run hylo conformance CONFIG` starts the environment and checks it. The same failure mid-episode
    shows as `remote <method> failed: ...`, and the episode is `infra_invalid`.

??? question "A LeRobot policy fails to load its weights with an offline error from `huggingface_hub`"
    **Cause:** the `lerobot` runtime sets `HF_HUB_OFFLINE=1` and `HF_HOME` to `bench/envs/hf-home`, so nothing is
    downloaded during a run. The checkpoint is not in that cache.

    **Fix:** download it once with the runtime's `HF_HOME` and with `HF_HUB_OFFLINE` unset, or point `repo_id` at a
    cached checkpoint ([environment variables](../configuration/environment-variables.md)).

??? question "`KeyError: "no policies plugin named 'policy.nope'; known: [...]"`"
    **Cause:** no installed package registers that name in that group.

    **Fix:** check the spelling against `uv run hylo plugins` (`--all` adds the test doubles). A plugin package you
    installed with `uv pip install -e PATH` is removed by the next `uv sync`, because it is not a workspace member:
    put it under `plugins/packages/` and make it a member
    ([adding a policy, step 1](adding-a-policy.md#1-scaffold-the-package)). If `HYLO_NO_PLUGIN_AUTOLOAD=1` is set,
    installed plugins are not loaded at all: unset it.

??? question "`IncompatibleComponents: action dim: agent 7 != env 2`"
    **Cause:** the agent's spec and the environment's spec disagree. Hylo checks this before any episode runs. The
    same check reports `env does not provide state keys [...]`, `env does not provide cameras [...]`,
    `control_mode: agent ... != env ...` and `rotation_repr: ...`.

    **Fix:** pick an agent made for this environment, or adapt the agent's spec.
    `uv run hylo conformance CONFIG --agent` shows both specs.

??? question "Episodes end with `error`, `safety_abort` or `infra_invalid` instead of success or failure"
    **Cause:** see [episode statuses](../user-guide/experiments.md#runs-and-traces). `error` and `infra_invalid`
    episodes are left out of the metrics, and `error` includes the agent's own exceptions and timeouts, so check
    these counts before reading the score.

    **Fix:** read the episode's `termination_reason` ([reading a run](#inspecting-a-run)).

??? question "`watchdog: no new actions for N steps` in realtime runs"
    **Cause:** in realtime timing the action queue ran empty for more than `max_hold_steps` (default 100)
    consecutive steps. The policy is too slow for `control_hz`, or it stopped answering.

    **Fix:** compare `latency_s` or the measured latency with `refill_steps`, or raise `max_hold_steps` for slow
    policies on a simulator ([timing](../user-guide/experiments.md#timing-sync-and-realtime)).

??? question "`no target to hold for absolute control (the environment must provide hold_action)`"
    **Cause:** a realtime episode with absolute actions needs the environment's `hold_action` to know what "hold
    still" means.

    **Fix:** implement `hold_action` in the environment, or use delta actions.

## Benchmarks

??? question "`ValueError: overrides ['agent.params.kp'] would change what the protocol measures; only env.remote.*, workers`"
    **Cause:** `hylo bench run --set` may change how a protocol runs, never what it measures.

    **Fix:** change the agent (`--policy`), or write a new protocol.

??? question "`ValueError: different protocols: mujoco-reach@1 vs ...`"
    **Cause:** `hylo bench compare` pairs episodes only within one protocol digest.

    **Fix:** re-evaluate the older agent under the current protocol before comparing. `hylo bench show NAME` prints
    the current digest.

??? question "`KeyError: "unknown protocol 'nope'; built in: libero-10, libero-10-heldout, libero-10-heldout-realtime, mujoco-reach"`"
    **Fix:** use a built-in name (`uv run hylo bench list`) or a path to a protocol YAML.

## Artifacts and campaigns

??? question "`.../b/gain: content digest ca22895f89be761f != manifest 7c0e3c577ceeacab (modified after sealing)`"
    **Cause:** a file in a sealed artifact changed after `artifact.json` was written, so it is no longer what its id
    names. Mutable artifacts (a lesson book while curating) are not checked.

    **Fix:** rebuild it (rerun the learner job), or restore the original files.

    **Check:** `uv run hylo artifact PATH` verifies the artifact and prints its manifest.

??? question "`<id>: <path> now holds digest <d>`"
    **Cause:** a config or candidate references `artifact:<name>@<digest>`, and the directory the store resolves
    holds a different digest.

    **Fix:** reference the current digest, or restore the content.

??? question "`SplitLeak: gate / heldout data must never be used to build anything that is gated on it: ['gate_r1']`"
    **Cause:** a learner or judge was asked to read a `gate*` or `heldout*` split. Variants of the same guard:
    `<run> is a 'gate' run; only ['search', 'search_val'] may be used` (an explicit list of runs given to a learner)
    and `refusing to seal <dir>: source <run> is a 'gate' run` (at sealing).

    **Fix:** build from development splits (`search`, `search_val`) only. See
    [which runs a learner may read](../user-guide/learning.md#the-split-guard).

A candidate rejected by the stage-0 checks is recorded in the campaign archive with the reason:

??? question "`behaviour artifacts with unknown provenance: [...]`"
    **Cause:** the candidate references a behaviour artifact adopted without its training runs (`hylo store adopt`
    without `--source`). The stage-0 checks cannot rule out that it was trained on gate or held-out data.

    **Fix:** rebuild the artifact with a learner, or adopt it again with `--source` for each run it was built from.

??? question "`candidate <id> touches protected scope '<path>'` or `duplicate of an archived candidate`"
    **Cause:** the generator proposed a change to a [protected path](../user-guide/safety.md#safety-in-campaigns),
    or a patch the archive already holds.

    **Fix:** none needed: the stage-0 checks are working.

??? question "`prescreen: world model predicts 0.40 vs parent 0.65`"
    **Cause:** the campaign's gate settings (`protocol.prescreen`) turn on a world-model prescreen, and the model
    predicted the candidate to be worse than the parent by more than the margin (default 0.1).

    **Fix:** none needed. If it rejects candidates you expected to pass, raise `protocol.prescreen.margin` or
    remove the prescreen.

## The store

??? question "`artifact:l10-trace-v2 not found in the store at .../runs`"
    **Cause:** no run or sealed artifact with that id is under the store directory, even after the index was rebuilt.
    If another digest of the name exists, the message lists it: `...; with that name: [...]`.

    **Fix:** check which store this machine uses: `hylo store where` prints it
    ([lookup order](../configuration/profiles.md#store)). `hylo store ls --name l10-trace-v2` lists what has the
    name. If the artifact is on another machine, `hylo store pull HOST:PATH ID`.

??? question "`'l10-trace-v2' is not a store id (run:<id> or artifact:<name>[@<digest>])`"
    **Fix:** ids start with `run:` or `artifact:`. `hylo store ref PATH` prints the id of a directory.

??? question "`artifact:gain is ambiguous: ['artifact:gain@0c15194f963398b2', 'artifact:gain@7c0e3c577ceeacab']; add the digest`"
    **Cause:** a bare name works only when exactly one artifact has it.

    **Fix:** add the digest. Eight hex characters are enough.

??? question "`artifact:gain@0c15194f963398b2 was removed at Sun Nov  1 04:19:38 2026 (superseded)`"
    **Cause:** the entry was deleted with `hylo store rm`. The tombstone records when and why.

    **Fix:** rebuild the artifact, pull it from a machine that still has it, or change the reference.

??? question "`run:r1 is referred to by ['artifact:gain@0c15194f963398b2']; remove those first or pass force (with a reason)`"
    **Cause:** something still uses this entry: an artifact built from it, or a campaign that names it.

    **Fix:** `hylo store show ID` lists them. Remove those first, or force it with
    `hylo store rm ID --force --reason "..."` (the referrers are recorded).

??? question "`sync refused, 1 conflict(s): [{'path': 'b/gain', 'here': 'artifact:gain@7c0e...', 'there': 'artifact:gain@fd51...'}]`"
    **Cause:** the same path holds different content on the two machines. Sealed artifacts are never overwritten, so
    nothing was copied.

    **Fix:** rename or remove one side (`hylo store rm` there), then sync again.

??? question "`cannot list the store at robot:/data/runs: ...`, `rsync failed (N): ...`, `rsync is needed to sync with another machine`"
    **Cause:** syncing with `HOST:PATH` runs `ssh HOST hylo store --root PATH ls --json`, then `rsync`.

    **Fix:** the other machine needs ssh access without a prompt and `hylo` on its `PATH`. Otherwise pass
    `--remote-command /path/to/hylo`. This machine needs `rsync`.

    **Check:** `ssh HOST hylo store where` prints the remote store.

??? question "`run:<id>: indexed at <path> but missing in <store>`"
    **Cause:** the index lists the entry, but its directory is gone, even after a rebuild.

    **Fix:** remove `<store>/.hylo-store/index.json` and run `hylo store index`.

## Serve and studio

??? question "`ERROR:    [Errno 98] error while attempting to bind on address ('127.0.0.1', 8765): address already in use`"
    **Cause:** another process holds the port. The message comes from uvicorn.

    **Fix:** stop that process, or start on another `--port`. Default ports: policy server 8000, workcell 8100,
    Studio (`hylo playground`) 8765, and `hylo serve env` / `hylo serve agent` also 8765.

??? question "A workcell episode ends at once; `/status` shows `"state": "idle"` and `"last": {"error": "..."}`"
    **Cause:** the episode failed to start or run, for example because the policy endpoint does not answer. The
    message is also broadcast on `/events` as `{"type": "failed", ...}`. The workcell stays up.

    **Fix:** check the policy server (`hylo serve policy`) and the URL in the workcell config or the request.

??? question "HTTP 409 from `POST /episodes`: `latched fault: e-stop by operator; clear it first` / `an episode is running` / `no policy endpoint (in the request or the workcell config)`"
    **Cause and fix:**

    - An e-stop latches until an operator posts `{"type": "clear_fault"}` to `/operator`.
    - Only one episode runs at a time. Wait for it to end.
    - A policy endpoint is required, in the request or in the workcell config.

??? question "HTTP 401 `missing or wrong token`"
    **Cause:** the workcell or Studio was started with `--token`, and the request has no token or the wrong one.

    **Fix:** send `Authorization: Bearer <token>` to a workcell (and `?token=` on `/events`). Studio takes the
    `x-token` header or `?token=`. See [security](../user-guide/security.md).

## Plugins

??? question "`IncompatiblePlugin: policies plugin 'x' (pkg 1.2.0) implements hylo.policy/v1.0; this core implements hylo.policy/v0.1`"
    **Cause:** the plugin declares a contract version this core cannot run: another major version, or a newer minor
    one.

    **Fix:** install a plugin version written for this core, or upgrade the harness. See
    [versioning](versioning.md#contract-versions).

??? question "`cannot build policy 'policy.knn': TypeError: KNNPolicy.__init__() missing 1 required positional argument: 'path'`"
    **Cause:** `hylo plugin check` builds the plugin with `--params` (JSON), and this plugin needs a parameter.

    **Fix:** pass it, for example
    `hylo plugin check policy policy.knn --params '{"path": "artifact:policy.knn"}'`.

??? question "`warning: <dist> declares no contract version ...` from `hylo plugin check`"
    **Cause:** the package has no `hylo.meta` declaration, or the declaration lacks maturity or licence. The plugin
    still loads.

    **Fix:** add the declaration ([extending](../harness/extending.md), [versioning](versioning.md#contract-versions)).

## Inspecting a run

[Experiments](../user-guide/experiments.md#runs-and-traces) lists the files of a run directory.

```bash
uv run hylo trace runs/<run_dir>                        # aggregate results, status counts, episode ids
uv run hylo trace runs/<run_dir> <episode_id>           # event counts and the episode.end payload
```

The `episode.end` event carries `status` and `termination_reason`. The `termination_reason` tells failure modes
apart: `max_steps`, `terminated`, `truncated`, `sim_error`, or the text of the error that ended the episode. An
`error` event carries `phase` and `message`.

## Collecting a bug report

Include:

1. the command and its full output: the traceback, and the child process's traceback for remote components;
2. `manifest.json` of the run, which records the config, its digest, package versions, git commit, Python and
   platform;
3. `uv run hylo plugins --json` for the plugins involved, and `uv run hylo profile show`;
4. for one bad episode, `uv run hylo trace RUN_DIR EPISODE_ID`, and the episode's `.jsonl` if it is small;
5. whether it reproduces on the test double or on MuJoCo (`hylo plugin check ... --experiment`), which separates a
   plugin problem from a simulator problem.

Before you send it, remove secrets from everything you attach: command lines and output, manifests, configs and the
profile. Tokens can appear in all of them, for example as `--token` arguments or a policy endpoint's `token`.
