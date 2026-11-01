# Concepts

The vocabulary used throughout Hylo. Each entry names the code that defines it; the other pages assume these
meanings.

![Architecture](../assets/diagrams/architecture.svg){ .wc-figure }

*Contracts and the kernel in hylo-core; evaluation, agents, memory, learning and campaigns on top; adapters connect
simulators, robots and policy stacks; the leaf repositories use all of it through the same formats.*

## Running

Experiment config
:   A YAML file (`hylo.experiment/v0.1`, `core.config.ExperimentConfig`) naming a benchmark and split, an
    environment, an agent, and optionally safety limits, trace options, timing and a seed. `hylo run CONFIG`
    evaluates it. See [experiments](../user-guide/experiments.md) and the
    [schema](../harness/experiment-schema.md).

Digest
:   A 16-hex-digit hash of what an experiment *measures* (`ExperimentConfig.measured()`). Placement is left out:
    where results go (`output_dir`), how many workers, and where components run (`env.remote`, a remote agent's
    `runtime` / `python` / `env`). So the same experiment has the same digest on a workstation, a GPU box and a robot
    computer, and two runs with the same digest are directly comparable.

Benchmark, task, split
:   A benchmark (`benchmarks` plugin, `core.benchmark.Benchmark`) is a set of tasks plus named splits of their
    initial states (seeds). The `rsi` protocol of [RFC-0002](../rfcs/RFC-0002-physical-rsi.md) partitions init
    states into four splits with different readers: `search` (diagnosis; generators may read these traces),
    `search_val` (candidate selection), `gate` (confirmation, plus `gate_r1`, ... for further looks) and `heldout`
    (report only). Learners read only `search` and `search_val`.

![RFC-0002 splits](../assets/diagrams/splits.svg){ .wc-figure }

Environment
:   A simulator or a robot behind `core.env.Environment`: `spec()`, `reset(task)`, `step(action)`, `close()`.
    The spec declares observation and action spaces, the action's control mode, the control rate and capabilities
    (for example `real_robot`). An environment may run in another process and venv (`env.remote`).

Agent
:   What the kernel runs (`core.agent.Agent`): `spec()`, `reset(ctx)`, `act(observation) -> ActionChunk`,
    `on_step(result)`, `on_episode_end(outcome)`. Agents hold decision logic: running a policy, steering it,
    planning, using memory.

Policy
:   The model inside an agent (`core.policy.ChunkPolicy`, `policies` group): given an observation, `sample()` draws
    action chunks, one per noise seed, shaped `(N, T, A)`. Stochastic policies derive their randomness only from
    the seeds, so a candidate and its parent face the same noise on the same init state. See
    [policies](../user-guide/policies.md).

Action chunk
:   A sequence of `T` actions predicted at once; the agent executes `execution_steps` of them before asking again.

Timing
:   How policy time relates to robot time (`core.kernel.Timing`). `sync` (default): the world waits for each
    policy call. `realtime`: the world keeps moving while the next chunk is computed, stale actions are dropped and
    a hold action fills gaps, on a `virtual` clock (deterministic, with a fixed or measured latency) or a `wall`
    clock (a real control loop). One loop, `core.kernel.EpisodeRunner`, does both.

Safety shield
:   The checkpoint between every agent and every environment (`core.safety.SafetyShield`). A finite check runs
    first and a bounds clamp last; configured guards run in between. See [safety](../user-guide/safety.md).

Trace
:   The event log of one episode (`core.trace`): episode start, observations, proposed chunks, safety reviews,
    executed actions, step results, end. Scorers read traces only, so scoring never depends on the agent.

Run
:   One evaluation of one split: a directory with `evallog.json` (per-episode results and scores),
    `manifest.json` (config, digest, package versions, pinned store ids) and the episode traces.

## Learning

Artifact
:   Anything learned, sealed as a directory with an `artifact.json` manifest (`hylo.artifact/v0.1`,
    `core.artifact`): kind, content digest, and provenance (the builder and the runs it was built from). Roles
    decide how it is trusted:

    | Role | Examples | Trusted when |
    |---|---|---|
    | `behaviour` | action memory, critic, noise prior, policy weights | the gate promotes a candidate that uses it |
    | `instrument` | success judge, progress or world model | it is calibrated against ground truth |
    | `proposal` | lesson book, skill library | curated by outcome votes; only changes what is proposed |
    | `data` | an ingested external dataset | it is labelled by its source or a calibrated judge |

Store id
:   The global name of a run or artifact in this machine's store: `run:<run_id>` or `artifact:<name>@<digest>`.
    Configs reference artifacts by id; ids are resolved to local paths when a component is built. See
    [store](../user-guide/store.md).

Learner
:   A `learners` plugin that turns runs (and other artifacts) into one sealed artifact (`Learner.fit(job)`), driven
    by a `TrainJob` JSON (`hylo learn`). Learners read development splits only. See
    [learning](../user-guide/learning.md).

Judge, calibration
:   A success judge (`instruments` group) labels episodes without the simulator's ground truth. It is calibrated
    on runs whose outcome is known (`hylo calibrate`: AUC, precision and recall at a threshold), and only then used to
    label data (`hylo label`).

## Improving

Campaign
:   Repeated improvement cycles on one experiment (`hylo.evolve/v0.1`, `hylo evolve run`). Each cycle diagnoses the
    parent's search runs, asks a generator for candidates, evaluates them in a cascade and promotes at most one
    through the gate. See [campaigns](../user-guide/campaigns.md).

Generator, candidate
:   A `generators` plugin proposes candidates: config patches (dotted paths and values) with a hypothesis.
    Patches may not touch protected scopes (`safety`, `benchmark`, `trace`, `scorers`, `evolution`,
    `schema_version`, `env`).

Gate
:   The confirmatory test that decides promotion: a paired test (McNemar by default) on the gate split, possibly
    over several group-sequential looks, with regression and safety vetoes. The held-out result is reported, never
    used for selection.

Active version
:   What a campaign currently deploys, written as `active.json` (`hylo.active/v0.1`, `core.deployment`). A policy
    server can serve it (`hylo serve policy --campaign DIR`).

## Benchmarking and deployment

Protocol, scorecard, leaderboard
:   A protocol (`hylo.protocol/v0.1`, bench) fixes everything except the policy; its digest covers only what is
    measured. Running a policy under it gives a scorecard (`hylo.scorecard/v0.1`): success with a 95% Wilson
    interval and every episode. Leaderboards rank scorecards of one protocol. See
    [benchmarking](../benchmarking/index.md).

Policy server, workcell
:   serve's two processes next to hardware. A policy server (`hylo serve policy`) answers chunk requests over
    WebSocket. A workcell (`hylo serve workcell`) owns one robot or simulator, runs episodes with the realtime kernel,
    and takes operator input (stop, latched e-stop, reset confirmation, verdicts). See
    [deployment](../user-guide/deployment.md).

Runtime, execution profile
:   A runtime is a named interpreter plus environment variables on one machine (for example `libero-sim`). The
    execution profile (`hylo.profile/v0.1`, `~/.config/hylo/profile.yaml`) lists them and the store
    location. Configs name runtimes, never paths. See [profiles](../configuration/profiles.md).

## Extending

Plugin, contract, maturity
:   Everything that varies is a plugin registered under a `Hylo.<group>` entry point. Each group is a
    versioned contract (`hylo.policy/v0.1`, ...); a package declares the version it implements and each plugin's
    maturity: `implemented` (run end to end on its target), `unverified`, `needs-hardware` or `test-double`. The
    registry refuses an incompatible contract version. See the [plugin catalogue](../developer-guide/plugin-catalogue.md)
    and [extending](../harness/extending.md).

Test double
:   `hylo.testing` and the `testing.*` plugins: a point-reach environment and simple agents for unit and
    conformance tests only. Every example, protocol and campaign runs on a real simulator.
