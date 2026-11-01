# Troubleshooting

Failure messages as worldcurrent prints them, why they happen, and what to do. Long paths are shortened with `...`.
Where the message comes from a library rather than from worldcurrent, the page says so.

## Inspecting a run

Most questions about an experiment are answered by its run directory (see
[runs and traces](../user-guide/experiments.md#runs-and-traces)):

```bash
uv run wc trace runs/<run_dir>                        # aggregate results, status counts, episode ids
uv run wc trace runs/<run_dir> <episode_id>           # event counts and the episode.end payload
```

| Look at | For |
|---|---|
| `evallog.json` | per-episode `status`, `steps`, scores and trace path; the benchmark digest and split |
| `manifest.json` | the measured config and its `config_digest`, package versions, git commit, and the store ids the run used (`artifacts`) |
| `episodes/<id>.jsonl` | every event; `episode.end` carries `status` and `termination_reason`; an `error` event carries `phase` and `message` |
| [studio](../user-guide/studio.md) | replay with camera frames, actions, policy calls and the event log, and A/B comparison of two runs |

The `termination_reason` tells failure modes apart: `max_steps`, `terminated`, `truncated`, `sim_error`, or the
text of the error that ended the episode.

## Install and workspace

??? question "`.../pyproject.toml is stale: run python harness/dev/workspace.py .`"
    The workspace file no longer matches the repositories present (a repository or package was added or removed,
    or `workspace.py` changed). `uv run pytest harness/dev` reports the same thing as a failed
    `test_the_workspace_file_matches_the_repositories` ("run python harness/dev/workspace.py").

    ```bash
    python harness/dev/workspace.py .       # in the workspace directory
    uv sync
    ```

??? question "`ModuleNotFoundError: No module named 'worldcurrent.envs.mujoco'` (or another worldcurrent package)"
    The repository that provides it is not checked out next to the harness, or `uv sync` has not run since it was
    added. Run `harness/dev/bootstrap.sh` in the workspace directory; it clones missing repositories when
    `WC_GIT_BASE` is set and reinstalls everything ([installation](../getting-started/installation.md)).

??? question "`pydantic_core._pydantic_core.ValidationError: ... Extra inputs are not permitted [type=extra_forbidden ...]`"
    Every contract (`ExperimentConfig`, protocols, workcell configs, profiles) refuses unknown keys, so a typo
    fails loudly instead of being ignored. The line before names the field (for example `worker` instead of
    `workers`). Fix the key; `wc schema experiment` prints the schema.

## Runtimes and the profile

??? question "`KeyError: "runtime 'libero-sim' is not in ~/.config/worldcurrent/profile.yaml (known: -); register it with: wc profile set-runtime libero-sim --python PATH [--env KEY=VALUE ...]"`"
    The config names a runtime this machine's profile does not have. On a LIBERO machine, `bench/envs/libero/setup.sh`
    registers `libero-sim` and `lerobot`; otherwise register the venv yourself. `WC_PROFILE` selects another profile
    file. See [execution profiles](../configuration/profiles.md).

    ```bash
    uv run wc profile show
    uv run wc profile set-runtime robot --python ~/robot/.venv/bin/python --env LD_LIBRARY_PATH=...
    ```

??? question "`EnvironmentFault: env server exited with code 1`, after a traceback"
    A remote environment's process (`env.remote`) died before it answered; its own traceback is printed above,
    because the child's stderr goes to the terminal. Common causes:

    - the runtime's venv lacks the environment's package (reinstall it there: `setup.sh` does);
    - rendering is not set up: LIBERO needs `MUJOCO_GL=osmesa`, `PYOPENGL_PLATFORM=osmesa` and
      `LD_LIBRARY_PATH` pointing at user-space OSMesa (`~/.local/mesa/root/usr/lib/x86_64-linux-gnu`, installed
      by `bench/scripts/install-osmesa-user.sh`); the profile's `libero-sim` runtime carries these;
    - `LIBERO_CONFIG_PATH` does not point at the config `setup.sh` wrote.

    The same failure mid-episode becomes `remote <method> failed: ...` and the episode is `infra_invalid`.

??? question "A LeRobot policy fails to load its weights with an offline error from `huggingface_hub`"
    The `lerobot` runtime sets `HF_HUB_OFFLINE=1` and `HF_HOME` to `bench/envs/hf-home`, so a checkpoint must
    already be in that cache: nothing is downloaded during a run. Download it once with the runtime's `HF_HOME`
    and `HF_HUB_OFFLINE` unset, or point `repo_id` at a cached checkpoint. See
    [environment variables](../configuration/environment-variables.md).

## The store

The store's messages come from `wc store` (prefixed `wc store:`) or from a run that resolves ids. See
[the store](../user-guide/store.md).

??? question "`artifact:l10-trace-v2 not found in the store at .../runs`"
    No run or sealed artifact with that id is under the store directory, even after the index was rebuilt. Check
    which store this machine uses (`wc store where`: the profile's `store:`, else `$WC_STORE`, else `./runs`), and
    `wc store ls --name l10-trace-v2`. When the artifact is on another machine, `wc store pull HOST:PATH ID`. When a
    different digest of the name exists, the message lists it: `...; with that name: [...]`.

??? question "`'l10-trace-v2' is not a store id (run:<id> or artifact:<name>[@<digest>])`"
    Ids start with `run:` or `artifact:`. `wc store ref PATH` prints the id of a directory.

??? question "`artifact:gain is ambiguous: ['artifact:gain@0c15194f963398b2', 'artifact:gain@7c0e3c577ceeacab']; add the digest`"
    A bare name works only when exactly one artifact has it. Add the digest (8 hex characters are enough).

??? question "`artifact:gain@0c15194f963398b2 was removed at Sun Nov  1 04:19:38 2026 (superseded)`"
    The entry was deleted with `wc store rm`, and the tombstone records when and why. Rebuild the artifact, pull it
    from a machine that still has it, or change the reference.

??? question "`run:r1 is referred to by ['artifact:gain@0c15194f963398b2']; remove those first or pass force (with a reason)`"
    Deletion protection: an artifact was built from the run, or a campaign's archive or ledger names it
    (`campaign:<dir>`). `wc store show ID` lists the referrers. Delete them first, or
    `wc store rm ID --force --reason "..."`, which still records the referrers in the tombstone.

??? question "`sync refused, 1 conflict(s): [{'path': 'b/gain', 'here': 'artifact:gain@7c0e...', 'there': 'artifact:gain@fd51...'}]`"
    The same path holds different content on the two machines. Sealed artifacts are never overwritten, so nothing
    was copied. Rename or remove one side (`wc store rm` there), then sync again.

??? question "`cannot list the store at robot:/data/runs: ...`, `rsync failed (N): ...`, `rsync is needed to sync with another machine`"
    Syncing with `HOST:PATH` runs `ssh HOST wc store --root PATH ls --json` and `rsync`. The other machine needs ssh
    access without a prompt and `wc` on its `PATH` (or `--remote-wc /path/to/wc`); this machine needs `rsync`.
    Between two local directories, a plain copy is used when `rsync` is missing.

??? question "`run:<id>: indexed at <path> but missing in <store>`"
    The index lists the entry but its directory is gone, even after a rebuild. Remove `<store>/.wc-store/index.json`
    and run `wc store index`.

## Artifacts and the split guard

??? question "`.../b/gain: content digest ca22895f89be761f != manifest 7c0e3c577ceeacab (modified after sealing)`"
    A file in a sealed artifact changed after `artifact.json` was written, so it is no longer what its id names.
    Rebuild it (rerun the learner job), or restore the original files. Mutable artifacts (a lesson book while
    curating) are not checked.

??? question "`<id>: <path> now holds digest <d>`"
    A config or candidate references `artifact:<name>@<digest>`, and the directory the store resolves holds a
    different digest. Reference the current digest, or restore the content.

??? question "`SplitLeak: gate / heldout data must never be used to build anything that is gated on it: ['gate_r1']`"
    A learner, judge or generator was asked to read a `gate*` or `heldout*` split. Variants of the same guard:
    `<run> is a 'gate' run; only ['search', 'search_val'] may be used` (an explicit list of runs given to a learner)
    and `refusing to seal <dir>: source <run> is a 'gate' run` (at sealing). Build from development splits only;
    see [the split guard](../user-guide/learning.md#the-split-guard).

??? question "A candidate is `rejected` with `behaviour artifacts with unknown provenance: [...]`"
    The candidate references a behaviour artifact adopted without its training runs (`wc store adopt` without
    `--source`), so the gate cannot rule out a leak of gate or held-out data. Rebuild the artifact with a learner,
    or adopt it with its sources. Other stage-0 rejections in the archive: `candidate <id> touches protected scope
    '<path>'`, `duplicate of an archived candidate`, `prescreen: world model predicts ...`.

## Plugins

??? question "`KeyError: "no policies plugin named 'policy.nope'; known: [...]"`"
    The name is not registered in that group. `wc plugins` lists what is installed (`--all` adds the test doubles);
    a plugin package must be installed (`uv sync` in the workspace, or `uv pip install -e`) for its entry points to
    exist. A `module:attr` reference bypasses the registry.

??? question "`IncompatiblePlugin: policies plugin 'x' (pkg 1.2.0) implements wc.policy/v1.0; this core implements wc.policy/v0.1`"
    The plugin declares a contract version this core cannot run: another major version, or a newer minor one.
    Install a plugin version written for this core, or upgrade the harness. See [versioning](versioning.md).

??? question "`cannot build policy 'policy.knn': TypeError: KNNPolicy.__init__() missing 1 required positional argument: 'path'`"
    `wc plugin check` builds the plugin with `--params` (JSON), and this one needs a parameter. For example:
    `wc plugin check policy policy.knn --params '{"path": "artifact:policy.knn"}'`.

??? question "`warning: <dist> declares no contract version ...` from `wc plugin check`"
    The package has no `worldcurrent.meta` declaration, or it lacks maturity or licence. The plugin still loads;
    add the declaration ([extending](../harness/extending.md), [versioning](versioning.md)).

## Experiments and the episode loop

??? question "`IncompatibleComponents: action dim: agent 7 != env 2`"
    Raised when the agent is bound to the environment, before any episode runs: their specs disagree. Other
    errors of the same check: `env does not provide state keys [...]`, `env does not provide cameras [...]`,
    `control_mode: agent ... != env ...`, `rotation_repr: ...`. Differences in `frame` and `gripper` are only
    warnings (recorded as `compat_warnings` in `episode.start`). `wc conformance CONFIG --agent` shows the specs.

??? question "Episodes end with `error`, `safety_abort` or `infra_invalid` instead of success or failure"
    | Status | Cause | `termination_reason` examples |
    |---|---|---|
    | `error` | the agent raised, timed out (`agent.act took 1.234s > 1.0s`, when the runner has an `act_timeout_s`), or the realtime watchdog fired | `watchdog: no new actions for 101 steps` |
    | `safety_abort` | a guard refused an action, or the operator stopped the episode | `non-finite action at step 12`, `stopped by the operator` |
    | `infra_invalid` | the environment failed or the simulator diverged; not the policy's fault and not scored | `reset failed: ...`, `step failed: ...`, `sim_error` |

    `error` and `infra_invalid` episodes are abstentions: excluded from the metrics, not scored as failures. A run
    with many of them measures the setup, not the policy.

??? question "`watchdog: no new actions for N steps` in realtime runs"
    In `timing: realtime` the queue ran empty for more than `max_hold_steps` (default 100) consecutive steps: the
    policy is too slow for `control_hz`, or it stopped answering. Check `latency_s` / measured latency against
    `refill_steps`, or raise `max_hold_steps` for slow policies on a simulator. See
    [timing](../user-guide/experiments.md#timing-sync-and-realtime).

??? question "`no target to hold for absolute control (the environment must provide hold_action)`"
    A realtime episode with absolute actions needs the environment's `hold_action` to know what "hold still" means.
    Implement it in the environment, or use delta actions.

## Benchmarks

??? question "`ValueError: overrides ['agent.params.kp'] would change what the protocol measures; only env.remote.*, workers`"
    `wc bench run --set` only changes how a protocol runs, never what it measures; otherwise the scorecard would
    not belong to the protocol. Change the policy instead (`--policy`), or write a new protocol.

??? question "`ValueError: different protocols: mujoco-reach@1 vs ...`"
    `wc bench compare` pairs episodes only within one protocol digest. Two scorecards of one protocol name differ
    when the protocol definition changed (for LIBERO protocols, once in RFC-0005); rerun the older policy.

??? question "`KeyError: "unknown protocol 'nope'; built in: libero-10, libero-10-heldout, libero-10-heldout-realtime, mujoco-reach"`"
    Use a built-in name (`wc bench list`) or a path to a protocol YAML.

## Serve and studio

??? question "`ERROR:    [Errno 98] error while attempting to bind on address ('127.0.0.1', 8765): address already in use`"
    From uvicorn: another process holds the port (often an earlier playground, workcell or policy server). Stop it,
    or start on another `--port`. The ports used in the examples: 8001 and 8002 policy servers, 8101 and 8102
    workcells, 8765 the playground.

??? question "A workcell episode ends at once; `/status` shows `"state": "idle"` and `"last": {"error": "..."}`"
    The episode failed to start or run, for example because the policy endpoint does not answer; the message is
    also broadcast on `/events` as `{"type": "failed", ...}`. The workcell stays up. Check the policy server
    (`wc serve policy`) and the URL in the workcell config or the request.

??? question "HTTP 409 from `POST /episodes`: `latched fault: e-stop by operator; clear it first` / `an episode is running` / `no policy endpoint (in the request or the workcell config)`"
    An e-stop latches until an operator posts `{"type": "clear_fault"}` to `/operator`; only one episode runs at a
    time; and a policy endpoint is required. Studio's operator station sends these events. See
    [deployment](../user-guide/deployment.md).

??? question "HTTP 401 `missing or wrong token`"
    The workcell was started with `--token`: send `Authorization: Bearer <token>` (and `?token=` on `/events`).
    Keep tokens in environment variables, not in configs.

## Collecting a bug report

Include:

1. the command and its full output (the traceback, and the child process's traceback for remote components);
2. `manifest.json` of the run, which records the config, its digest, package versions, git commit, Python and
   platform;
3. `uv run wc plugins --json` for the plugins involved, and `uv run wc profile show` with secrets removed;
4. for one bad episode, `uv run wc trace RUN_DIR EPISODE_ID`, and the episode's `.jsonl` if it is small;
5. whether it reproduces on the test double or MuJoCo (`wc plugin check ... --experiment`), which separates a
   plugin problem from a simulator problem.
