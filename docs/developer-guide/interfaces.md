# Interface notes

These notes explain component responsibilities, lifecycle constraints and integration choices.
Use the [Python API](../api/index.md) for exact signatures and defaults, and the
[plugin catalogue](plugin-catalogue.md) for available implementations.

| Component | Design and integration notes | Current API |
|---|---|---|
| Environment | [Environment notes](../harness/interfaces/environment.md) | [Environment contracts](../api/contracts.md#environments) |
| Agent and policy | [Agent notes](../harness/interfaces/agent.md) | [Agent contracts](../api/contracts.md#agents) |
| Reasoner | [Reasoner notes](../harness/interfaces/reasoner.md) | [Reasoning contracts](../api/contracts.md#reasoners-choosers-planners-reflectors) |
| Memory | [Memory notes](../harness/interfaces/memory.md) | [Core memory module](../api/modules/hylo-core/hylo.core.memory.md) |
| Benchmark | [Benchmark notes](../harness/interfaces/benchmark.md) | [Benchmark contracts](../api/contracts.md#benchmarks) |
| Improvement | [Improvement notes](../harness/interfaces/improvement.md) | [Generator and campaign contracts](../api/contracts.md#generators-and-campaign-records) |

Some notes retain prototype results and versioned design proposals. Those sections describe their original
scope; they do not establish current implementation support. Check the linked API and plugin catalogue before
using an interface. Reproduction evidence belongs in [Validation](validation/index.md).
