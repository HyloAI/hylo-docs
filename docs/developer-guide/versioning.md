# Versioning and compatibility

The repositories never import each other's code. They cooperate through versioned contracts and formats defined
in hylo-core, and results are identified by digests of what was measured. This page lists everything that carries a
version or a digest, what changes it, and what is not settled yet.

| Kind | Example | Answers |
|---|---|---|
| Contract version | `hylo.policy/v0.1` | can this plugin run on this core? |
| Format schema version | `hylo.scorecard/v0.1` | can this file or message be read? |
| Digest | `config_digest: 2342f91d706e83e9` | is this the same experiment, protocol or content? |
| Package version | `0.1.0.dev0` | which code is installed? |

## Contract versions

Each plugin group is a contract with a version (`hylo.core.plugins.CONTRACTS`; RFC-0005 part 4). All are
at v0.1:

| Group | Contract | Group | Contract |
|---|---|---|---|
| `envs` | `hylo.env/v0.1` | `generators` | `hylo.generator/v0.1` |
| `agents` | `hylo.agent/v0.1` | `learners` | `hylo.learner/v0.1` |
| `policies` | `hylo.policy/v0.1` | `instruments` | `hylo.instrument/v0.1` |
| `reasoners` | `hylo.reasoner/v0.1` | `datasources` | `hylo.datasource/v0.1` |
| `choosers` | `hylo.chooser/v0.1` | `planners` | `hylo.planner/v0.1` |
| `reflectors` | `hylo.reflector/v0.1` | | |
| `memory` | `hylo.memory/v0.1` | `guards` | `hylo.guard/v0.1` |
| `scorers` | `hylo.scorer/v0.1` | `gate_tests` | `hylo.gate_test/v0.1` |
| `benchmarks` | `hylo.benchmark/v0.1` | | |

A plugin package declares the version it implements in its `META` dictionary, registered under the
`hylo.meta` entry-point group (see [extending](../harness/extending.md)):

```python
META = {"contracts": {"policies": "hylo.policy/v0.1", "learners": "hylo.learner/v0.1"}, "maturity": "implemented"}
```

**Compatibility rule** (`core.plugins.compatible`): a declared version runs on this core when it names the same
contract, has the same major version, and its minor version is not newer than the core's.

| Plugin declares | Core implements | Loads? |
|---|---|---|
| `hylo.policy/v0.1` | `hylo.policy/v0.1` | yes |
| `hylo.policy/v1.0` | `hylo.policy/v1.3` | yes: the core still supports what v1.0 plugins use |
| `hylo.policy/v1.4` | `hylo.policy/v1.3` | no: the plugin may use features this core lacks |
| `hylo.policy/v0.1` | `hylo.policy/v1.0` | no: another major version |

The registry checks the declaration before it imports an entry point and raises `IncompatiblePlugin` on a
mismatch. A plugin without a declaration still loads and is listed as undeclared; `hylo plugin check` warns.
`module:attr` references are not checked, because there is no package to ask.

**When to bump** (a proposal for after v0.x; nothing has been bumped yet):

- *minor*: the core adds something a plugin may use (a new optional method, a new optional spec field), and every
  plugin written for the previous minor version still works;
- *major*: a plugin written for the previous version could break (a method's signature or meaning changes, a field
  becomes required). A major change starts with an RFC ([repository structure](../design/repository-structure.md),
  section 6).

## Format schema versions

Every file or message that crosses a repository or a process carries its schema version. The data contracts are
pydantic models with `extra="forbid"` and the version as a `Literal`, so a file of another version, or with an
unknown key, is refused when it is read instead of being misread.

| Format | Version | Defined in | Written as |
|---|---|---|---|
| Experiment config | `hylo.experiment/v0.1` | `core.config` | config YAML; the run's `manifest.json` |
| Execution profile | `hylo.profile/v0.1` | `core.profile` | `~/.config/hylo/profile.yaml` |
| Store index | `hylo.store/v0.1` | `core.store` | `<store>/.hylo-store/index.json` |
| Artifact manifest | `hylo.artifact/v0.1` | `core.artifact` | `artifact.json` |
| Trace events | `hylo.trace/v0.1` | `core.events` (`TRACE_SCHEMA`) | `episodes/<id>.jsonl`, recorded in `manifest.json` |
| Eval log | `hylo.evallog/v0.1` | `eval.runner` (`EVALLOG_VERSION`) | `evallog.json` |
| Scorecard | `hylo.scorecard/v0.1` | `core.scorecard` | `scorecards/<protocol>/<policy>.json` |
| Protocol | `hylo.protocol/v0.1` | `bench.protocol` | protocol YAML |
| Campaign config | `hylo.evolve/v0.1` | `evolve.campaign` | campaign YAML |
| Active version | `hylo.active/v0.1` | `core.deployment` | a campaign's `active.json` |
| Workcell API | `hylo.workcell/v0.1` | `core.remote.workcell` | HTTP and WebSocket messages; workcell run manifests |
| Env server protocol | `hylo.envserver/v0.1` | `core.remote.protocol` | the `hello` line of a remote environment |
| Agent server protocol | `hylo.agentserver/v0.1` | `core.remote.agent_server` | the `hello` of a remote agent or policy server |
| Ingested runs | `hylo.external/v0.1` | `learn.data` | `manifest.json` of an external-data run |

The remote protocols are matched exactly: a client that receives another `hello` fails with
`protocol mismatch: ...`. Artifacts also version their own payloads (`hylo.action_bank/v0.1`, `hylo.critic/v0.1`,
`hylo.world_model/v0.1`, `hylo.reference_policy/v0.1`, `hylo.selftrain/v0.1`), and each loader refuses a payload of
another version. `hylo schema NAME` prints the JSON Schema of the main contracts ([formats](../api/formats.md)).

## Digests

A digest names what something *is*, so that two results can be compared and an artifact cannot change unseen.
All are SHA-256, truncated to 16 hex characters.

| Digest | Over | Left out |
|---|---|---|
| Experiment (`config_digest`) | `ExperimentConfig.measured()`: schema version, name, benchmark, env, agent, seed, safety, trace options, tags, and `timing` when it is not the default | `output_dir`, `workers`; `env.remote` is hashed as absent (`null`); a remote agent's `runtime`, `python` and `env` |
| Benchmark | id, version, every task's digest, the splits | |
| Task | the whole `TaskSpec` | |
| Protocol | the protocol definition | `description`, `workers`, `requires`; `env.remote` hashed as absent; `timing` while it is the default |
| Artifact content | every file under the artifact directory, with its relative path | `artifact.json` itself |
| Learner job | the `TrainJob` (learner, inputs, splits, params) | `out` |
| Candidate | the patch, the parent and the kind | its random id |

What the digests are used for:

- runs record the experiment digest and the benchmark digest; a campaign compares parent and candidate on the same
  episodes, and `hylo bench compare` refuses scorecards with different protocol digests;
- store ids are `artifact:<name>@<content digest>`; the gate re-verifies the content of every referenced artifact;
- a learner job whose output is already sealed with the same job digest is not run again;
- a campaign rejects a candidate whose patch it has already archived (compared as canonical JSON).

!!! note "History: where components run left the digest (RFC-0005)"
    Since RFC-0005, where a component runs is not part of what is measured, so the same experiment has the same
    digest on every machine. The first version (2026-10-31) dropped `env.remote` from the hashed dictionary
    altogether, which changed every digest, local ones included. On 2026-11-01 it was changed to hash `env.remote`
    as absent, the way local environments always were, so local experiments and protocols kept their earlier
    digests (mujoco-reach v1 is `5e0c57ef414a0b21`), and only experiments that ran the simulator in another
    process (LIBERO) changed once. Runs recorded between the two changes carry the intermediate digests.
    `timing` is hashed only when it is not the default (sync), so introducing it changed no digest.

!!! note "History: the rename to Hylo (2026-11-01)"
    Schema ids moved from `wc.<name>/v<x>` to `hylo.<name>/v<x>` and modules from `worldcurrent.*` to `hylo.*`.
    Because the schema id is part of every config and protocol, every experiment and protocol digest changed once
    (mujoco-reach v1: `5e0c57ef414a0b21` -> `a76c7037efb84660`). Artifact content digests did not change, so store
    ids such as `artifact:l10-trace-v2@54a1efadf00d34d8` are still valid. Data written before the rename stays
    readable: `wc.*` schema ids and `worldcurrent.*` module references are read as their `hylo.*` names
    (`hylo.core.contract.current_schema` / `current_module`), the policy server still answers on `/wc`, and a
    workcell config may still say `protocol: wc`.

A change to what a digest covers is a breaking change for comparisons: older runs and scorecards keep the digest
they were recorded with. Make such a change through an RFC and say which digests change.

## Package versions and releases

All 21 packages are at `0.1.0.dev0`. Nothing has been released or published yet, and the repositories have no
remotes. Within a development workspace every package is installed editable from its checkout, so the versions
that matter are the git commits, which each run's `manifest.json` records together with the installed packages'
versions.

## Compatibility between repositories

- The harness is the only base. bench, studio and plugins depend on the harness, and serve on hylo-core only (a robot
  computer installs nothing else). Leaves never import each other ([repository structure](../design/repository-structure.md)).
- They cooperate through the formats above, all defined in hylo-core: registry names, traces, store ids and artifacts,
  `active.json`, scorecards, the remote protocols, the workcell API, and `hylo` subcommands.
- The boundary lint enforces this in every workspace ([testing](testing.md#the-boundary-lint)).

What is decided for later releases (repository structure, section 6), not yet practised:

- each repository is versioned on its own (semver), and the contract schemas are the compatibility surface;
- the harness is released first and then the leaves, and each leaf states the harness versions it supports;
- a breaking contract change starts with an RFC, bumps the harness's major version, and each leaf follows.

There is no deprecation policy yet. No contract or format has been deprecated so far.
