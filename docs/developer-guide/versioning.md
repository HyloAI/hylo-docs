# Versioning and compatibility

The repositories never import each other's code. They cooperate through versioned contracts and formats defined
in wc-core, and results are identified by digests of what was measured. This page lists everything that carries a
version or a digest, what changes it, and what is not settled yet.

| Kind | Example | Answers |
|---|---|---|
| Contract version | `wc.policy/v0.1` | can this plugin run on this core? |
| Format schema version | `wc.scorecard/v0.1` | can this file or message be read? |
| Digest | `config_digest: c26fef49863a7b7a` | is this the same experiment, protocol or content? |
| Package version | `0.1.0.dev0` | which code is installed? |

## Contract versions

Each plugin group is a contract with a version (`worldcurrent.core.plugins.CONTRACTS`; RFC-0005 part 4). All are
at v0.1:

| Group | Contract | Group | Contract |
|---|---|---|---|
| `envs` | `wc.env/v0.1` | `generators` | `wc.generator/v0.1` |
| `agents` | `wc.agent/v0.1` | `learners` | `wc.learner/v0.1` |
| `policies` | `wc.policy/v0.1` | `instruments` | `wc.instrument/v0.1` |
| `reasoners` | `wc.reasoner/v0.1` | `datasources` | `wc.datasource/v0.1` |
| `memory` | `wc.memory/v0.1` | `guards` | `wc.guard/v0.1` |
| `scorers` | `wc.scorer/v0.1` | `gate_tests` | `wc.gate_test/v0.1` |
| `benchmarks` | `wc.benchmark/v0.1` | | |

A plugin package declares the version it implements in its `META` dictionary, registered under the
`worldcurrent.meta` entry-point group (see [extending](../harness/extending.md)):

```python
META = {"contracts": {"policies": "wc.policy/v0.1", "learners": "wc.learner/v0.1"}, "maturity": "implemented"}
```

**Compatibility rule** (`core.plugins.compatible`): a declared version runs on this core when it names the same
contract, has the same major version, and its minor version is not newer than the core's.

| Plugin declares | Core implements | Loads? |
|---|---|---|
| `wc.policy/v0.1` | `wc.policy/v0.1` | yes |
| `wc.policy/v1.0` | `wc.policy/v1.3` | yes: the core still supports what v1.0 plugins use |
| `wc.policy/v1.4` | `wc.policy/v1.3` | no: the plugin may use features this core lacks |
| `wc.policy/v0.1` | `wc.policy/v1.0` | no: another major version |

The registry checks the declaration before it imports an entry point and raises `IncompatiblePlugin` on a
mismatch. A plugin without a declaration still loads and is listed as undeclared; `wc plugin check` warns.
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
| Experiment config | `wc.experiment/v0.1` | `core.config` | config YAML; the run's `manifest.json` |
| Execution profile | `wc.profile/v0.1` | `core.profile` | `~/.config/worldcurrent/profile.yaml` |
| Store index | `wc.store/v0.1` | `core.store` | `<store>/.wc-store/index.json` |
| Artifact manifest | `wc.artifact/v0.1` | `core.artifact` | `artifact.json` |
| Trace events | `wc.trace/v0.1` | `core.events` (`TRACE_SCHEMA`) | `episodes/<id>.jsonl`, recorded in `manifest.json` |
| Eval log | `wc.evallog/v0.1` | `eval.runner` (`EVALLOG_VERSION`) | `evallog.json` |
| Scorecard | `wc.scorecard/v0.1` | `core.scorecard` | `scorecards/<protocol>/<policy>.json` |
| Protocol | `wc.protocol/v0.1` | `bench.protocol` | protocol YAML |
| Campaign config | `wc.evolve/v0.1` | `evolve.campaign` | campaign YAML |
| Active version | `wc.active/v0.1` | `core.deployment` | a campaign's `active.json` |
| Workcell API | `wc.workcell/v0.1` | `core.remote.workcell` | HTTP and WebSocket messages; workcell run manifests |
| Env server protocol | `wc.envserver/v0.1` | `core.remote.protocol` | the `hello` line of a remote environment |
| Agent server protocol | `wc.agentserver/v0.1` | `core.remote.agent_server` | the `hello` of a remote agent or policy server |
| Ingested runs | `wc.external/v0.1` | `learn.data` | `manifest.json` of an external-data run |

The remote protocols are matched exactly: a client that receives another `hello` fails with
`protocol mismatch: ...`. Artifacts also version their own payloads (`wc.action_bank/v0.1`, `wc.critic/v0.1`,
`wc.world_model/v0.1`, `wc.reference_policy/v0.1`, `wc.selftrain/v0.1`), and each loader refuses a payload of
another version. `wc schema NAME` prints the JSON Schema of the main contracts ([formats](../api/formats.md)).

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
  episodes, and `wc bench compare` refuses scorecards with different protocol digests;
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

A change to what a digest covers is a breaking change for comparisons: older runs and scorecards keep the digest
they were recorded with. Make such a change through an RFC and say which digests change.

## Package versions and releases

All 21 packages are at `0.1.0.dev0`. Nothing has been released or published yet, and the repositories have no
remotes. Within a development workspace every package is installed editable from its checkout, so the versions
that matter are the git commits, which each run's `manifest.json` records together with the installed packages'
versions.

## Compatibility between repositories

- The harness is the only base. bench, studio and plugins depend on the harness, and serve on wc-core only (a robot
  computer installs nothing else). Leaves never import each other ([repository structure](../design/repository-structure.md)).
- They cooperate through the formats above, all defined in wc-core: registry names, traces, store ids and artifacts,
  `active.json`, scorecards, the remote protocols, the workcell API, and `wc` subcommands.
- The boundary lint enforces this in every workspace ([testing](testing.md#the-boundary-lint)).

What is decided for later releases (repository structure, section 6), not yet practised:

- each repository is versioned on its own (semver), and the contract schemas are the compatibility surface;
- the harness is released first and then the leaves, and each leaf states the harness versions it supports;
- a breaking contract change starts with an RFC, bumps the harness's major version, and each leaf follows.

There is no deprecation policy yet. No contract or format has been deprecated so far.
