# System measurements

These examples report evidence for RSI, Worlds, Agents, Memory and Skills, with the supporting execution,
evaluation and deployment mechanisms. Each result applies to the robot, observations and task conditions measured.

[Tool-using agents](tool-agents.md) distinguishes hand-written programs from model-developed programs and records
observation privileges, failures and unrun paths. Use the [agent guide](../user-guide/agents.md) to choose a starting point.

One runnable example set per layer of the stack, each with the result it measured. Every number here was produced
by the scripts on the layer's page, on a 128-core CPU workstation with no GPU (2026-11-01), with fixed seeds; each
script has a `--quick` mode that a smoke test runs. Null and negative results are reported as they came out.

| Layer | Headline result | Page |
|---|---|---|
| Core | Proposed actions up to 9.42 never reach the robot above 1.00, four attempts to bypass the shield fail; 90/90 episodes replay bit-exact from their traces; the same config in process, over stdio and over WebSocket gives identical actions (+0.33 ms per step over WebSocket) | [Core](core.md) |
| Memory | With targets visible for only 5 steps, spatial memory takes success from 0.00 to 0.75 (300 pairs, p = 4e-68); a skill derived from a campaign takes fresh scenes from 0.47 to 0.86; action memory gives +6 points on both revisited and new scenes, not significant | [Memory](memory.md) |
| Agents | One config line swaps the rule chooser (76.7%) for a local LLM or a VLM that sees only the camera image (100%, about 2 s per decision); replanning every step loses to open-loop chunks (4 vs 13 episodes); shadow candidates leave the executed actions bit-identical | [Agents](agents.md) |
| Instruments | A success judge that sees fingertip and target reaches AUC 0.986; given all state, it learns a termination shortcut instead; a learned world model ranks 9 controllers with Spearman 0.91 but is optimistic; the chunk critic is a null result | [Instruments](instruments.md) |
| Learning | Flow policies from 10 to 160 demonstrations go from 0.40 to 0.85 on held-out; online CEM lifts the held-out rate from 0.46 to 0.84; calibrated judges label another cell's episodes at 0.82-0.91 precision, below the 0.95 they were calibrated for | [Learning](learning.md) |
| Evolution | A campaign improves a noisy policy from 0.44 to 0.76 on 500 held-out episodes; 11 of 14 adversarial candidates are refused before any episode runs; A/A changes are promoted in under 3% of draws, and the default gate detects a 10-point effect only 26% of the time; a field regression rolls back after 40 episodes | [Evolution](evolution.md) |
| Benchmarks | A nine-policy leaderboard under one protocol digest; a changed safety limit puts a scorecard on a different board; paired comparison finds a significant difference (p = 0.005) where the confidence intervals overlap; 16 remote workers run MPC 9.9x faster with identical episodes | [Benchmarks](benchmarks.md) |
| Plugins | A guard written outside the harness slows the fingertip near the target from 0.24 to 0.05 m/s; a minimum-effect gate blocks a significant but small gain; an online learner as a candidate generator is promoted from 0.35 to 1.00 | [Plugins](plugins.md) |
| Runtime | 1,500 steps at 30 Hz with no deadline miss and 3.6 ms median policy round trip; a 3 s policy stall is held still and aborted by the watchdog; an e-stop stops the arm within one control period and stays latched; a campaign's promotion and rollback switch what the policy server deploys | [Runtime](runtime.md) |
| Tool-using agents | Six perception-only Panda programs at 1.00; a program written by a local model passes the gate (0.95 vs 0.50, p = 0.002); 3 of 6 model-written scenes solved; our own episodes replay in physics, external ones do not; LIBERO programs at 0.98 / 0.96 / 0.86 with privileged segmentation; a local model through typed tools solves 8 of 9 pick_place, put_in_bowl and stack episodes zero-shot; in worlds, four quadrupeds trot, two humanoids walk under pretrained policies and two drones reach their waypoints | [Tool-using agents](tool-agents.md) |

## What the examples found

The examples also exercised paths no test covered. Issues they found are tracked with the code; the ones that bear on
trust in a result:

- Where a component runs must not change what is measured, but a WebSocket environment changes the config digest.
- The rate-limit guard can be undone by a guard that runs after it.
- A mutable behaviour artifact skips the tamper check.
- A malformed candidate from a generator stops the whole campaign cycle instead of being refused.
- Skill derivation recognises only the remote steering path.

## Running them

```bash
# from the development workspace (harness/dev/bootstrap.sh)
uv run python harness/examples/core/02_safety_shield.py           # one example, full run
uv run python harness/examples/core/02_safety_shield.py --quick   # under a minute
uv run pytest harness/tests/test_examples_core.py                 # every core example in quick mode
```

Output goes to `runs/examples/` in each repository; MuJoCo renders need an OpenGL backend (on a CPU machine:
`bench/scripts/install-osmesa-user.sh`).
