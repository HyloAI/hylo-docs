# Python API

Find Python contracts and implementation APIs here. Core contracts define the boundary between Hylo plugins;
the package index provides the complete module inventory.

| You need | Start here |
|---|---|
| Environment, agent, policy, reasoner, benchmark or learning contracts | [Core contracts](contracts.md) |
| Episode execution, events and traces | [Episode loop](kernel.md) |
| Experiment models, execution profiles and plugin registration | [Configuration API](config.md) |
| Artifacts, store IDs, scorecards and active versions | [Artifacts and store](artifacts-and-store.md) |
| Memory records, queries and store protocol | [Core memory module](modules/hylo-core/hylo.core.memory.md) |
| Any other package or module | [Package index](packages/index.md) |

## Working with contracts

Data contracts such as `EnvSpec`, `Observation`, `ActionChunk` and `ExperimentConfig` are frozen pydantic models.
Build them with keyword arguments, copy them with `model_copy(update=...)`, and obtain a JSON Schema with
`model_json_schema()`. Behavioural contracts such as `Environment`, `Agent`, `ChunkPolicy` and `Guard` are
`typing.Protocol`s: a plugin implements their methods without inheriting from them.

The core pages and module pages render docstrings and type annotations from the checked-out code.
A module covered by a core page links back to that page from the package index, so its API has one definition.
Names starting with an underscore are omitted. Inclusion in the package index is not a stability guarantee;
plugins should depend on the core contracts at their integration boundary.

## Related references

- [Configuration](../reference/configuration.md): YAML fields and machine settings.
- [Data formats & schemas](formats.md): versioned records and JSON Schemas.
- [Plugin catalogue](../developer-guide/plugin-catalogue.md): registered implementations and declared maturity.
- [Interface notes](../developer-guide/interfaces.md): integration semantics and design context.
