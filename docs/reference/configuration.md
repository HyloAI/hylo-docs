# Configuration

Choose the configuration you are editing. Each reference lists its fields, defaults or lookup rules.

| Configuration | What it controls |
|---|---|
| [Experiment](../harness/experiment-schema.md) | environment, agent, benchmark split, timing and recorded outputs |
| [Execution profile](../configuration/profiles.md) | this machine's named Python runtimes and store location |
| [Environment variables](../configuration/environment-variables.md) | paths, rendering, model caches and process settings |
| [Evaluation protocol](../benchmarking/protocols.md) | the fixed conditions used to compare agents |
| [Workcell](../configuration/workcells.md) | environment, policy endpoint, timing and recording on a robot computer |

An experiment describes what is measured; an execution profile resolves where components run.
A workcell's `runtime` block configures episode timing. It is distinct from a named runtime in an execution profile.

Use [Run experiments](../user-guide/experiments.md) or [Deployment](../user-guide/deployment.md) for setup steps.
[Data formats & schemas](../api/formats.md) provides machine-readable contracts;
[Configuration API](../api/config.md) documents the Python objects.
