# Versioning and compatibility

This page lists what carries a version or a digest, and what changes it.

| Kind | Example | Answers |
|---|---|---|
| Contract version | `hylo.policy/v0.1` | can this plugin run on this core? |
| Format schema version | `hylo.scorecard/v0.1` | can this file or message be read? |
| Digest | `config_digest: 2342f91d706e83e9` | is this the same experiment, protocol or content? |
| Package version | `0.1.0.dev0` | which code is installed? |

Until the first release, contracts and formats may change without a deprecation period.

## Plugin contracts

Every plugin group is a contract with a version, named `hylo.<name>/v0.1` after the group in the singular
(`envs` is `hylo.env/v0.1`, `gate_tests` is `hylo.gate_test/v0.1`). All are at v0.1. The
[plugin system](../harness/plugin-system.md) lists the groups.

A plugin package declares the versions it implements in a `META` dictionary, registered under the `hylo.meta`
entry-point group ([extending](../harness/extending.md)):

```python
META = {"contracts": {"policies": "hylo.policy/v0.1", "learners": "hylo.learner/v0.1"}, "maturity": "implemented"}
```

A declared version runs on this core when it names the same contract, has the same major version, and its minor
version is not newer than the core's:

| Plugin declares | Core implements | Loads? |
|---|---|---|
| `hylo.policy/v0.1` | `hylo.policy/v0.1` | yes |
| `hylo.policy/v1.0` | `hylo.policy/v1.3` | yes: the core still supports what v1.0 plugins use |
| `hylo.policy/v1.4` | `hylo.policy/v1.3` | no: the plugin may use features this core lacks |
| `hylo.policy/v0.1` | `hylo.policy/v1.0` | no: another major version |

The plugin registry checks the declaration before it imports an entry point, and raises `IncompatiblePlugin` on a
mismatch. A plugin without a declaration still loads and is listed as undeclared, and `hylo plugin check` warns.
`module:attr` references are not checked, because there is no package to ask.

## File and message formats

Files read through a Hylo contract (experiment configs, profiles, protocols, artifact manifests, scorecards, the
store index, campaign configs) carry their schema version. They are refused when the version or a key is unknown,
rather than misread. Old `wc.*` ids are renamed first (see [Older data](#older-data)). Workcell configs have no
version field but also refuse unknown keys. `evallog.json` is read as plain JSON: its `version` key is not checked.

| Format | Version | Written as |
|---|---|---|
| Experiment config | `hylo.experiment/v0.1` | config YAML; the run's `manifest.json` |
| Execution profile | `hylo.profile/v0.1` | `~/.config/hylo/profile.yaml` |
| Store index | `hylo.store/v0.1` | `<store>/.hylo-store/index.json` |
| Artifact manifest | `hylo.artifact/v0.1` | `artifact.json` |
| Trace events | `hylo.trace/v0.1` | `episodes/<id>.jsonl`, recorded in `manifest.json` |
| Eval log | `hylo.evallog/v0.1` (key `version`) | `evallog.json` |
| Scorecard | `hylo.scorecard/v0.1` | `scorecards/<protocol>/<policy>.json` |
| Protocol | `hylo.protocol/v0.1` | protocol YAML |
| Campaign config | `hylo.evolve/v0.1` | campaign YAML |
| Active version | `hylo.active/v0.1` | a campaign's `active.json` |
| Workcell API | `hylo.workcell/v0.1` | HTTP and WebSocket messages; workcell run manifests |
| Env server protocol | `hylo.envserver/v0.1` | the `hello` line of a remote environment |
| Agent server protocol | `hylo.agentserver/v0.1` | the `hello` of a remote agent or policy server |
| Ingested runs | `hylo.external/v0.1` | `manifest.json` of an external-data run |

The remote protocols are matched exactly: a client that receives another `hello` fails with
`protocol mismatch ...`. Artifact payloads carry their own versions, and each loader refuses another version.
`hylo schema NAME` prints the JSON Schema of the experiment config, task, env spec, agent spec, candidate, memory
item and benchmark ([formats](../api/formats.md)).

## Digests

A digest names what something is, so that two results can be compared and an artifact cannot change unseen. All are
SHA-256, truncated to 16 hex characters.

| Digest | Over | Left out |
|---|---|---|
| Experiment (`config_digest`) | what the experiment measures ([rules](../user-guide/experiments.md#when-two-runs-are-comparable)) | where results go, workers, placement |
| Benchmark | id, version, every task's digest, the splits | |
| Task | the whole task spec | |
| Protocol | the protocol definition ([rules](../benchmarking/protocols.md#the-digest)) | description, workers, requirements, placement |
| Artifact content | every file under the artifact directory, with its relative path | `artifact.json` itself |
| Learner job | the learner, inputs, splits and params | the output directory |
| Candidate | the patch, the parent and the kind | its random id |

Store ids are `artifact:<name>@<content digest>`, and stage 0 of a campaign re-verifies the content of every
artifact a candidate references.

Changing what a digest covers changes it for every new run. Older runs and scorecards keep the digest they were
recorded with, so they no longer compare.

## Older data

Hylo reads data written under its former name:

- schema ids `wc.<name>/v<x>` are read as `hylo.<name>/v<x>`;
- module references `worldcurrent.*` are read as `hylo.*`, and `wc_examples` as `hylo_examples`;
- the policy server still answers on `/wc` as well as `/hylo`;
- a workcell config's `protocol: wc` is read as `hylo`.

Nothing is rewritten on disk. Experiment and protocol digests recorded under the old name differ from the digests
the same definitions get now, because the schema id is part of what is hashed. The same holds for runs recorded
before placement (`env.remote`) was left out of the digest. To compare with such a run, run the older agent again.
Artifact content digests did not change, so older store ids still resolve.

## Package versions

There are 23 packages, all at `0.1.0.dev0`. Nothing is released to PyPI, and the repositories have no tags. Install
from the GitHub repositories (`https://github.com/HyloAI/hylo-<name>`), as
[installation](../getting-started/installation.md) describes. In a development workspace every package is installed
editable from its checkout, so the version does not tell two installs apart.

A run's `manifest.json` records the versions of the main Hylo packages and the git commit of the directory the run
started in. When that directory is not inside a git repository, as with the workspace directory, the commit is
empty.
