# Validation { #system-validation }

<span id="system-measurements"></span>

Inspect the checks behind execution, safety boundaries, evaluation and deployment. These records describe
the implementation and conditions tested; they are not a hardware certification or a general capability ranking.

| Mechanism | Validation record |
|---|---|
| Action bounds, deterministic replay and process placement | [Core](core.md) |
| Control deadlines, watchdog, emergency stop and version changes | [Runtime](runtime.md) |
| External guards, effect-size gates and learner integration | [Plugins](plugins.md) |
| Judges, learned world models and critics | [Instruments](instruments.md) |
| Upstream parity and regression episodes | [Video-memory integration](video-memory.md) |

<span id="running-them"></span>

## Run a check { #reproduce-a-check }

Run from the workspace root:

```bash
uv run python harness/examples/core/02_safety_shield.py --quick
uv run pytest harness/tests/test_examples_core.py
```

The linked records identify source scripts, full-run conditions and known failures. Their results are dated
observations; use the scripts to check a different implementation or environment.

## Results { #experimental-results }

For analysis and measured outcomes, visit [Research](https://hyloai.github.io/research/) and
[Benchmarks](https://hyloai.github.io/research/benchmarks/). The [reproduction records](records.md) retain
full tables and commands next to the originating scripts.

<span id="what-the-examples-found"></span>

## Recorded issues { #known-issues-in-the-recorded-system-checks }

The earlier system measurements reported these implementation gaps; consult the current code and issue records
before assuming they have been resolved:

- A WebSocket environment changes the configuration digest.
- A later guard can undo a rate-limit guard.
- A mutable behaviour artifact skips the tamper check.
- A malformed generator candidate can stop the campaign cycle.
- The skill-derivation CLI recognises only the remote steering path.
