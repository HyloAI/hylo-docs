# Studio

worldcurrent-studio is the playground: one web UI over runs, campaigns, learning artifacts and workcells, and the
control plane for robots. `wc-playground` is the FastAPI backend (`wc playground`); `web/` is the React front end,
built into the package.

The playground reads runs and campaigns through the harness's catalog, runs `wc` commands as jobs (the same commands
a person would type, with the same checks), and talks to workcells through the workcell API. It never sends
actions to a robot.

![The runs page: every recorded run with its benchmark, split, success and episodes](../assets/figures/studio-runs.png){ .wc-figure }

## Starting it

```bash
cd studio/web && npm install --ignore-scripts && npm run build && cd ../..   # once; Node >= 18
uv run wc playground --repo bench                                          # http://127.0.0.1:8765
```

| Option | Default | Meaning |
|---|---|---|
| `--repo DIR` | `.` | the working directory: the UI shows its `examples/configs`, `examples/evolve` and `runs/`, and runs jobs in it (a bench checkout) |
| `--root DIR` | `runs` | the runs directory, relative to `--repo` |
| `--host`, `--port` | `127.0.0.1`, `8765` | |
| `--token SECRET` | none | require the token on every API call (`x-token` header or `?token=`; open the UI once with `?token=SECRET`) |
| `--judge PATH_OR_ID` | `artifact:l10-trace-v2@54a1efadf00d34d8` when in the store | the success judge for progress curves; a path or a [store id](store.md) |
| `--workcell NAME=URL[#TOKEN]` | none | a workcell service (repeatable) |
| `--policy NAME=WS_URL[#TOKEN]` | none | a policy server endpoint (repeatable) |
| `--role-token ROLE=TOKEN` | none | viewer / operator / approver tokens (repeatable) |

Development with hot reload: `uv run wc-playground` and, in `studio/web`, `npm run dev` (Vite proxies `/api`).

## Pages

| Page | What it shows and does |
|---|---|
| Overview | runs, campaigns and artifacts at a glance, the improvement cascade over every campaign |
| Live sandbox | one episode of any experiment config, streamed frame by frame |
| Runs | every recorded run; per-task success; episode replay |
| Compare | two runs paired on (task, seed) |
| Self-improvement | campaigns, cycles, candidates, gate statistics, the ledger; approve or roll back |
| Experience & learning | skills, lessons, action memories, sealed artifacts with provenance and calibration |
| Jobs | `wc run`, `wc evolve run` and `wc calibrate` in the background, with their logs |
| Operator station | episodes on a workcell with a chosen policy server; reset, verdicts, stop, e-stop |

### Runs and replay

The runs page lists every run under the runs directory (benchmark, split, agent, success, episodes), filtered by
split or text. Opening an episode replays it from its trace: camera frames, executed actions, chunk boundaries, safety
interventions, and the success judge's estimate along the episode.

![Episode replay: camera frames, actions, chunk boundaries and the judge's progress estimate](../assets/figures/studio-episode.png){ .wc-figure }

### Compare

Two runs of the same benchmark split, paired on (task, seed): wins and losses, the one-sided exact McNemar p-value,
per-task deltas, and side-by-side replays of the discordant pairs (where one run succeeded and the other failed).
This is the same test as [`wc bench compare`](../benchmarking/index.md#statistics) and the gate.

### Self-improvement

Every campaign under the runs directory: its cycles, the candidates with their hypotheses, the search_val and
group-sequential gate statistics, vetoes, the promotion ledger and the active version
([campaigns](campaigns.md)). A candidate that passed the gate and waits for approval can be approved here
(`wc evolve approve`); the active version can be rolled back with a reason (`wc evolve rollback`). Both need the
approver role.

![A campaign: cycles, candidates and gate statistics](../assets/figures/studio-campaign.png){ .wc-figure }

### Live sandbox

Runs one episode of any experiment config (MuJoCo, LIBERO with SmolVLA, ...) through the unchanged kernel and
SafetyShield, streamed as it happens. You choose the task and init state from the benchmark, change config
overrides, and give the agent a different instruction (the environment's task and success check stay the same).
Overrides of the protected scopes (safety, benchmark, trace, scoring) are refused. Environment and agent stay warm
between episodes of the same configuration, since loading a VLA takes tens of seconds.

Live episodes are saved under `runs/playground/live/<run_id>` with split `playground`, which no learner and no gate
ever reads.

### Jobs

Starts the CLI in the background in the `--repo` directory and follows its log (`runs/playground/jobs/<id>.log`).
Jobs are subprocesses of the playground; there is no queue or scheduler yet (RFC-0005 part 6). The page offers
evaluation, campaigns and judge calibration; the API (`POST /api/jobs`) also accepts `learn` jobs.

### Operator station

The control plane for workcells: pick a workcell (`--workcell`) and a policy server (`--policy`), start an episode
on a benchmark task or with a free-form instruction, and follow the workcell's live stream. When the workcell waits,
confirm the scene reset (`reset_done`) or judge the outcome (success, partial, failure); stop an episode, press the
e-stop, clear a latched fault. See [deployment](deployment.md#operating-a-workcell) for what each event does.

```bash
uv run wc serve policy --agent '{"type": "bringup.wave", "params": {"amplitude": 12, "horizon": 15}}' --port 8002
uv run wc serve workcell --config deployments-template/workcells/sim_arm.yaml --port 8102
uv run wc playground --repo bench --workcell sim-arm=http://127.0.0.1:8102 --policy wave=ws://127.0.0.1:8002/wc
```

## Roles

Without `--role-token` (and without `--token`) the local user has every role. With role tokens:

| Role | Can |
|---|---|
| viewer | read everything, and press the e-stop (stopping is never gated behind a higher role) |
| operator | start episodes; reset, verdict, stop, clear a fault; the live sandbox; jobs |
| approver | everything, plus approving and rolling back campaign versions |

The server binds to 127.0.0.1 by default. Put it behind your own authentication before exposing it on a network.
