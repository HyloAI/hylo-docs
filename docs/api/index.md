# API Reference

The Python API of `hylo-core`: the contracts every plugin implements, the episode loop, configuration, and the formats
the repositories exchange. Plugins and leaf repositories depend on these modules only; everything else in the
harness is an implementation behind them.

| Page | Modules | What is there |
|---|---|---|
| [Contracts](contracts.md) | `core.env`, `core.agent`, `core.policy`, `core.reasoning`, `core.types`, `core.task`, `core.instrument`, `core.learning`, `core.benchmark`, `core.scoring`, `core.improvement`, `core.safety` | what an environment, agent, policy, instrument, learner and guard must provide; the data that passes between them |
| [Kernel](kernel.md) | `core.kernel`, `core.events`, `core.trace` | the one episode loop (sync and realtime), events and traces |
| [Configuration](config.md) | `core.config`, `core.profile`, `core.plugins`, `core.registry` | experiment configs and their digest, execution profiles, contract versions, the plugin registry |
| [Artifacts and store](artifacts-and-store.md) | `core.artifact`, `core.store`, `core.scorecard`, `core.deployment` | sealed artifacts and the split guard, store ids, scorecards, active versions |
| [Formats and schemas](formats.md) | (generated) | every versioned format and its JSON Schema |

Pages are generated from the docstrings and type annotations of the code checked out next to this repository
(mkdocstrings). Names that start with an underscore are left out.

Beyond the core contracts, [Packages](packages/index.md) has one page per package of every repository (21 packages:
the harness and its adapters, bench, serve, studio, plugins), with its modules, classes and functions, signatures
included, and the plugins it registers. Depend on the core contracts; read the rest to understand, extend or debug.

!!! tip "Contracts are pydantic models or protocols"
    Data contracts (`EnvSpec`, `Observation`, `ActionChunk`, `ExperimentConfig`, ...) are frozen pydantic models:
    build them with keyword arguments, copy them with `model_copy(update=...)`, and get their JSON Schema with
    `hylo schema NAME`. Behavioural contracts (`Environment`, `Agent`, `ChunkPolicy`, `Guard`, ...) are
    `typing.Protocol`s: a plugin does not inherit from them, it has the methods.
