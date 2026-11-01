# Policies

A **policy** is the model that turns an observation into actions. An **agent** is what the kernel runs; it holds a
policy and decides how to use it: chunk by chunk, temporally ensembled, or steered by sampling several chunks and
selecting one. Because the two are separate, any policy runs under any of these agents by configuration, and the
policy never knows it is being steered, shadowed or scored.

## The policy contract

A policy is a `policies` plugin implementing `core.policy.ChunkPolicy`:

```python
class ChunkPolicy(Protocol):
    def spec(self) -> AgentSpec: ...
    def reset(self, ctx: EpisodeContext) -> None: ...
    def default_execution_steps(self) -> int: ...
    def sample(self, observation: Observation, seeds: list[int] | None, noise_scale: float) -> np.ndarray:
        """(N, T, A) action chunks in the environment's units, one per seed."""
```

Deterministic policies (regression, retrieval, scripted) ignore the seeds. Stochastic ones (diffusion, flow
matching, sampled tokens) must derive their randomness from the seeds only. Agents derive the seeds from the task
key, the chunk index and the sample index, so a candidate and its parent face the same noise on the same init state
(common random numbers for paired tests), and every episode can be replayed.

`hylo plugin check policy NAME` runs the conformance check on a registered policy (shape, finiteness, seed
determinism); `hylo plugin new policy NAME` scaffolds one. See [extending](../harness/extending.md).

## Agents that run a policy

| Agent | Runs the policy | Key params |
|---|---|---|
| `policy` | chunk by chunk, seeded noise | `policy`, `execution_steps`, `seed_noise`, `noise_scale` |
| `temporal_ensemble` | every step, exponentially weighted over overlapping chunks (ACT) | `policy`, `m` (weight decay; 0 = plain average) |
| `steered` | `n_samples` seeded chunks per decision, one selected, optional recovery rules | `sampler`, `steering` |

```yaml
agent: {type: policy, params: {policy: {type: policy.bc, params: {path: "artifact:policy.bc"}}}}
agent: {type: temporal_ensemble, params: {policy: {type: policy.bc, params: {path: "artifact:policy.bc"}}, m: 0.01}}
agent:
  type: steered
  params:
    sampler: {type: policy.flow, params: {path: "artifact:policy.flow"}}
    steering: {n_samples: 4, selector: medoid}
```

`steering` (`agents.steering.SteeringConfig`):

| Key | Default | Meaning |
|---|---|---|
| `n_samples` | 1 | chunks drawn per decision (1 to 8; cost grows linearly on CPU) |
| `selector` | `first` | `first`, `medoid`, or `gripper_vote_medoid` (keep the gripper-majority chunks, then the medoid) |
| `noise_scale` | 1.0 | scale of the initial noise |
| `execution_steps` | the policy's | actions executed from each chunk |
| `seed_noise` | true | seeded noise (replayable, paired) |
| `rules` | `[]` | up to 4 trigger rules: a feature (`still_steps`, `grasp_attempts`, `disagreement`, `steps`), a threshold and an action (`resample` with more noise, or `backoff`: move back and reopen the gripper), with `cooldown` and `max_fires` |

Everything in `steering` is data, so a campaign can propose and gate steering changes as config patches
([campaigns](campaigns.md)).

## Reference policies

`hylo-policies` ships one small, weights-free implementation of each common policy family, in numpy only. They are
trained from your own runs (development splits only, sealed as artifacts with provenance) and serve as baselines,
for teaching, and for testing the stack end to end in seconds. They are not the published architectures at scale.

| Plugin | Family | Idea (reference) | Stochastic |
|---|---|---|---|
| `policy.knn` | retrieval | nearest neighbours in observation space, averaged chunks (VINN) | no |
| `policy.bc` | regression BC | MLP from observation to an action chunk, MSE (BC with chunking) | no |
| `policy.flow` | flow matching | velocity field from noise to the chunk, Euler integration (pi0, SmolVLA action experts) | yes |
| `policy.tokens` | tokenized actions | each dimension binned, categorical heads, sampled (RT-1, OpenVLA-style) | yes |
| `policy.mpc` | model-based planning | cross-entropy method over action sequences in a learned world model (MPC) | yes |

Learners of the same names (`policy.knn`, `policy.bc`, `policy.flow`, `policy.tokens`) build `policy_params`
artifacts from successful episodes; `world_model.state` builds the world model `policy.mpc` plans in. Common
learner params: `chunk` (default 8), `seed`, `epochs`, `hidden`, `execution_steps`, `state_keys`, `statuses`
(default `["success"]`), `max_episodes`.

### Train and score them on MuJoCo reach

=== "All at once"

    ```bash
    cd bench
    uv run python examples/policies/compare.py    # data -> every learner -> mujoco-reach scorecards -> leaderboard (~3 min)
    ```

=== "Step by step"

    ```bash
    cd bench
    uv run hylo run examples/configs/mujoco_reach.yaml --split search --output runs/policies/demos \
        --set benchmark.params.protocol=rsi                    # demonstrations, from a development split
    uv run hylo learn examples/policies/jobs/flow.json           # a sealed policy_params artifact
    uv run hylo store ls --kind artifact                         # its id: artifact:policy.flow@<digest>
    uv run hylo run examples/configs/mujoco_policy_flow_steered.yaml
    uv run hylo bench run mujoco-reach --name flow-steered \
        --policy examples/configs/mujoco_policy_flow_steered.yaml
    ```

    `mujoco_policy_flow_steered.yaml` references the sampler as `artifact:policy.flow`: without a digest, the one
    artifact with that name in the store; the run's manifest pins the full id it used.

![mujoco-reach leaderboard](../assets/figures/leaderboard-mujoco-reach.png){ .wc-figure }

*`compare.py` on this project's workstation: 120 demonstration episodes from the search and search_val splits;
the mujoco-reach protocol (100 held-out episodes on seeds never used for learning); 95% Wilson intervals.*

| # | Policy | Success % | 95% CI | Mean steps |
|---|---|---|---|---|
| 1 | expert (IK controller) | 100.0 | 96.3–100.0 | 36 |
| 2 | mpc (world model from expert and random-action runs) | 86.0 | 77.9–91.5 | 60 |
| 3 | flow + steering, 4 samples | 84.0 | 75.6–89.9 | 54 |
| 4 | bc + temporal ensemble | 83.0 | 74.5–89.1 | 56 |
| 5 | flow | 83.0 | 74.5–89.1 | 56 |
| 6 | bc | 71.0 | 61.5–79.0 | 68 |
| 7 | tokens | 68.0 | 58.3–76.3 | 74 |
| 8 | knn | 64.0 | 54.2–72.7 | 76 |

Neighbouring rows overlap. Compare two scorecards with `hylo bench compare A.json B.json` (exact paired McNemar)
before reading a difference into them: flow + steering against bc, for example, gives p = 0.005.

## LeRobot and openpi policies

=== "LeRobot (SmolVLA, pi0, ...)"

    The `hylo-policy-lerobot` adapter runs LeRobot policies on CPU in the `lerobot` runtime (installed by bench's
    LIBERO setup). `lerobot` is both a policy and an agent; the factories wrap it:

    | Agent | What it adds |
    |---|---|
    | `lerobot` | the policy, chunk by chunk |
    | `lerobot.steered` | `SteeredAgent`: seeded noise, sample-and-select, recovery rules |
    | `lerobot.critic_steered` | samples `n_samples` chunks and executes the one a learned chunk critic values most |
    | `lerobot.memory_steered` | starts flow sampling from an action retrieved from its own successes (action memory) |
    | `lerobot.noise_steered` | biases the initial noise towards noise that produced similar successful chunks |

    ```yaml
    agent:
      type: remote
      params:
        ref: lerobot.steered
        runtime: lerobot
        params: {repo_id: lerobot/smolvla_libero, num_threads: 4, steering: {n_samples: 1, seed_noise: true}}
    ```

    `LeRobotAgent` params include `repo_id`, `device` (`cpu`), `camera_map`, `state_keys`, `n_action_steps`,
    `num_threads` and `action_semantics`.

=== "openpi"

    `openpi` (`hylo-policy-openpi`) is a client for an openpi policy server over WebSocket (`url`, default
    `ws://127.0.0.1:8000`, and an input `preset`, default `libero`). It is **unverified** here: no openpi server
    and checkpoint have been run with it yet.

![SmolVLA on LIBERO-10](../assets/figures/libero-episode-strip.png){ .wc-figure }

*SmolVLA (`lerobot/smolvla_libero`) on a LIBERO-10 task, every 10th camera frame of one episode.*

Weight licences differ per checkpoint: PaliGemma-based pi0 / pi0.5 checkpoints are under the Gemma Terms of Use. The
[plugin catalogue](../developer-guide/plugin-catalogue.md) lists each plugin's maturity and licences.

## Policies in other processes

A policy whose dependencies conflict with the workspace runs in its own runtime behind the `remote` agent, as
above. A policy on another machine runs behind a policy server (`hylo serve policy`) and is reached with the
`remote.ws` agent; see [deployment](deployment.md).
