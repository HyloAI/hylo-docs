# Repository Structure

> Decision (2026-10-31, supersedes RFC-0001 D7 "one repository for now"): Hylo is **five code repositories,
> a documentation repository and a deployment template**. The harness is the only base; every other code
> repository is a leaf on top of it. The development repository (`dyna-harness`) held each one as a top-level
> directory with the same contents and layout; on 2026-11-01 each directory became its own git repository (a copy
> of the committed files, without history), checked out side by side in one development workspace (section 5).

## 1. Repositories

| Repository | Directory today | Purpose | Depends on |
|---|---|---|---|
| **hylo-harness** | `harness/` | The base: contracts and kernel (hylo-core), evaluation engine (hylo-eval), agents, memory, learning (hylo-learn), improvement campaigns (hylo-evolve), run catalog (hylo-catalog), policy / LLM / data adapters, the harness's `hylo` subcommands, reference documentation | — |
| **hylo-bench** | `bench/` | Benchmarking: protocols, scorecards, leaderboards, pairwise comparison (hylo-bench); LIBERO and MuJoCo suites (hylo-env-libero, hylo-env-mujoco) and their setup (`envs/`); benchmark and campaign configs on those suites | harness |
| **hylo-serve** | `serve/` | Deployment: policy server, workcell service, real-time runner, operator channel (hylo-serve); robot adapters (hylo-env-lerobot-robot: LeRobot `Robot` interface + a simulated arm) | harness (hylo-core only, by default) |
| **hylo-studio** | `studio/` | The playground: control plane with roles, run explorer, live sandbox, campaigns, jobs (hylo-playground) and its React front end (`web/`) | harness |
| **hylo-plugins** | `plugins/` | Example and community plugins, written the way a third party would (hylo-plugin-examples), with their example configs | harness |
| **hylo-docs** | `docs/` | Unified documentation: architecture, this document, RFCs, research notes and experiment records, the third-party reference manifest | — (reads the others at build time) |
| **\<lab\>-deployments** | `deployments-template/` | Template for a lab's private repository of workcell configs, calibration and safety limits | — (configuration only) |

The interface-validation prototype that preceded the packages was removed on 2026-10-31; it remains in the git history.

A project website (landing page, public leaderboards from bench scorecards, posts) is planned as
**hylo-site**; it does not exist yet. It will read scorecards and link to the documentation, like docs.

## 2. Dependencies

```text
                                 harness (base)
   core · eval · agents · memory · learn · evolve · catalog · adapters · `hylo` · reference docs
        ▲              ▲               ▲               ▲
      bench          serve           studio          plugins

   docs, site:             read the repositories' published docs and scorecards at build time
   <lab>-deployments:      configuration that names what the repositories register
```

Rules (checked by `harness/dev/test_boundaries.py` over a development workspace):

1. **The harness depends on nothing else.** It never imports bench, serve, studio or plugins.
2. **Leaves depend only on the harness**, and never import each other.
3. **serve is robot-side:** its packages declare only `hylo-core`. A robot computer installs `hylo-core`, `hylo-serve`,
   a robot adapter and the policy package it serves, nothing else. Anything more is an optional extra.
4. **No code reaches into another repository by path.** Install scripts locate a sibling checkout through an
   environment variable with a side-by-side default (bench's `envs/libero/setup.sh`: `HYLO_HARNESS`).
   Deployment configs are exempt: they only compose installed repositories.
5. Inside each repository the package layering of `harness/docs/dependency-graph.md` still holds.

## 3. How the leaves cooperate without importing each other

Every format that one repository writes and another reads is defined in hylo-core:

| Format | Written by → read by | Defined in |
|---|---|---|
| Plugin names (`envs`, `agents`, `benchmarks`, `guards`, `gate_tests`, `learners`, ...) | any package registers → configs name them | `core.registry` |
| Runs and traces | eval (bench, campaigns), serve (deployment runs) → catalog, learn, studio | `core.trace`, `core.events`, `core.config` |
| Sealed artifacts (`artifact.json`) | learn → agents, serve, bench | `core.artifact` |
| A campaign's active version (`active.json`, hylo.active/v0.1) | evolve → the policy server (`--campaign`) | `core.deployment` |
| Scorecards (hylo.scorecard/v0.1) | bench → leaderboards, catalog, studio, site | `core.scorecard` |
| Policy protocols (hylo.agentserver/v0.1, openpi msgpack-numpy) | serve ↔ any client | `core.remote`, `core.remote.wire` |
| Environment protocol (EnvServer) | any env server ↔ eval | `core.remote` |
| Workcell API (hylo.workcell/v0.1) | serve implements → studio's control plane calls | `core.remote.workcell` |
| `hylo` subcommands (entry-point group `hylo.commands`) | each package registers → `hylo` dispatches | `core.cli` |

Changing one of these is a contract change: a versioned schema, compatibility for readers, and an RFC when it
breaks something.

## 4. Inside a repository

Every code repository has the same shape: `packages/` (and `adapters/` for packages that wrap third-party
software), `examples/`, `docs/`, a README. Each package has its own `pyproject.toml` (hatchling), its own
dependencies and its own `tests/`, and contributes to the PEP 420 namespace `Hylo.*`. Plugins are
`Hylo.<group>` entry points, so nothing finds an implementation by importing it.

What installs where:

| Machine | Installs |
|---|---|
| Robot computer | hylo-core, hylo-serve, hylo-env-lerobot-robot (+ the robot SDK in its venv) |
| GPU policy server | hylo-core, hylo-serve, the policy package (e.g. hylo-policy-lerobot, in the policy's venv) |
| Workstation (research) | the harness, bench, studio (and plugins as needed) |
| External team integrating a robot or a policy | hylo-core (contracts, protocols, conformance kit) |

## 5. Development workspace

The repositories are checked out side by side in one directory; `harness/dev/bootstrap.sh` clones the missing
ones (from `harness/dev/repos.toml`) and writes a uv workspace over all of them (`harness/dev/workspace.py`), so
every package installs editable into one venv and a change in hylo-core is visible everywhere at once. The boundary
lint and the cross-repository tests run from that workspace. The workspace directory is not a repository: its
`pyproject.toml`, `uv.lock` and `.venv` are generated.

Experiments name runtimes and store ids rather than paths (RFC-0005), so they run from any directory; config files
are passed by path (`hylo run bench/examples/configs/...`), and scripts that write `runs/` write next to where they run.

## 6. Versions and releases

- Each repository is versioned on its own (semver); the contract schemas (`hylo.experiment/v0.1`,
  `hylo.scorecard/v0.1`, `hylo.workcell/v0.1`, ...) are the compatibility surface.
- Release order: harness, then the leaves. A leaf states the harness versions it supports.
- A breaking contract change starts with an RFC, bumps the harness's major version, and each leaf follows.

## 7. When to split further

Kept inside the harness as separate packages, each ready to move out as a directory:

| Candidate | Split when |
|---|---|
| hylo-core alone | the contracts are stable (1.0, changing rarely) and outside teams depend on them, or they become an independently governed standard |
| Policy integrations (LeRobot, openpi, ...) | an upstream's churn or a separate maintainer makes them a burden in the harness |
| Protocol specification and clients | a non-Python client exists (e.g. a ROS 2 node or a C++ real-time bridge on the robot side) |
| Research notes | the code becomes public while the notes stay private |
