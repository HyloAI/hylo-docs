# Memory

Memory is how what a robot agent experienced becomes useful later: where an object was before it was hidden, what a
successful motion looked like in a similar scene, which change helped last time and which did not. Hylo keeps four
kinds of memory, each a plugin of the `memory` group, each recorded in the run so a result can be traced to the
memory it used.

| Kind | Plugin | Remembers | Used by |
|---|---|---|---|
| Spatial and episodic | `sqlite` | facts with a time and a place: what was seen where, and when | agents that reason over objects (`composable.object_reach`) |
| Action memory | `action_bank` | motion segments from verified successes, keyed by what the policy saw | `memory.steered`, which biases a policy toward remembered motions |
| Skills | `skill_library` | verified procedures for a task family: steering and recovery settings, plans, programs, recipes | the `skills` agent, `code.llm`, improvement campaigns, role campaigns |
| Lessons | `lesson_book` | short written lessons from earlier attempts, with helpful and harmful counts | language-model proposers and planners in improvement campaigns |

Rules the memories follow:

- **Recorded.** An agent that reads a bank or a library puts its content digest in the agent spec, so two runs that
  used different memories never look the same.
- **Frozen for evaluation.** An action bank loaded from disk, and a skill library or lesson book opened with
  `frozen: true`, refuse every write: an evaluation cannot learn from the episodes it is scoring. (Spatial memory is
  the agent's working memory within a run and is written as it goes.)
- **Evidence decides.** Skills become verified only through the gate (or, for recipes, a replay that achieves the
  goal), and lessons gain or lose standing from the outcomes of the candidates that cited them, never from a model's
  opinion.
- **Nothing silently disappears.** Facts about the world are invalidated rather than deleted; refuted skills stay in
  the library so later proposals can see what was tried.

## Spatial memory

An agent writes what it perceives (an object's pose, with the time it was seen) and recalls it when the object is
no longer visible. Queries can ask by key, by kind, by time range or by distance from a point.

```yaml
agent:
  type: composable.object_reach
  params:
    chooser: {type: chooser.rule_color}
    memory: {type: sqlite, params: {path: runs/memory/table.sqlite}}   # ":memory:" for one run only
```

Every write and retrieval is a trace event (`memory.write`, `memory.retrieval`), so a replay shows which decisions
came from memory.

## Action memory

`memory.steered` wraps a steerable policy (a flow policy, or a VLA through its adapter). At every decision it
retrieves the most similar verified segments, drops inconsistent ones, combines the rest into a prior and starts the
policy's sampling from it: the more confident the retrieval, the stronger the bias. With nothing usable it leaves
the policy unchanged, and the current observation always has the last word.

```yaml
agent:
  type: memory.steered
  params:
    sampler: {type: policy.flow, params: {path: runs/artifacts/flow}}
    memory: {type: action_bank, params: {path: runs/memory/bank, frozen: true}}
    memory_steer: {k: 10, same_task: true, sim_floor: 0.9}
```

A bank is a folder (`bank.npz`, `bank.json`; no pickle). It holds at most a fixed number of segments, oldest first
out. Banks are built only from simulator-verified successes on development splits, never from gate or held-out
episodes:

- MuJoCo: the memory examples (`harness/examples/memory/03_action_memory_scene_recall.py`,
  `05_memory_across_sessions.py`) build banks from earlier runs, including one that grows from session to session.
- LeRobot policies on LIBERO: keys are the policy's own visual tokens, and the agent is
  `hylo.policies.lerobot.experience_agent:make_experience_agent`.

```bash
uv run python -m hylo.policies.lerobot.memory_build --runs runs/<search runs> --out runs/memory/libero10 \
    --repo-id lerobot/smolvla_libero --task-prefix libero/libero_10/
```

The build also writes `build_report.json` with nearest-neighbour similarities, which is what `sim_floor` should be
set against.

## Skills

A skill is data, never code: a name, a version, a description, a trigger, a body and its evidence.

| Skill kind | Body | Applied by |
|---|---|---|
| `steering`, `recovery` | a steering configuration or recovery rules | the `skills` agent, for one episode |
| `plan` | subgoal templates, filled from the instruction | the `skills` agent through a subgoal planner |
| `weights` | a reference to trained weights | an improvement campaign, as configuration |
| `program` | a sealed `solve(robot)` program with its gate evidence | `code.llm`, as `skills.<name>(robot)` |
| `recipe` | the tool calls that solved a world task | role campaigns, offered when a goal fails for the same reasons |

A skill's trigger says when it applies: an instruction pattern (with named slots), task tags, an environment, or a
failure signature (the reason codes a goal check reported). Its status follows the evidence: proposed, then verified
or refuted; a verified skill can later be deprecated.

```bash
uv run hylo skills runs/campaign/campaign --out runs/skills/reach --tags mujoco reach    # skills from a campaign
uv run hylo research skills runs/campaign/campaign --library runs/skills --family stack  # program skills
```

```yaml
agent:
  type: skills
  params:
    skills: {type: skill_library, params: {path: runs/skills/reach, frozen: true}}
    inner: {type: steered, params: {...}}
```

Each application is a `skill.applied` trace event, so outcomes can be attributed to the skill. A library can also be
exported as one `SKILL.md` per verified skill, for a language model to scan and read on demand.

## Lessons

A lesson is a short note distilled from experience ("a narrower grasp slips on flat boxes"), scoped to a task
family, with helpful and harmful counts. A reflector model proposes changes (add, upvote, downvote, edit, retire);
the lesson book applies them deterministically, turns a near-duplicate addition into an upvote and retires a lesson
once its harmful count is two above its helpful one. Every change is appended to the book's `ops.jsonl`.

Lessons take effect through an improvement campaign's proposer:

```yaml
proposer:
  type: experience
  params:
    inner: {type: llm.steering, params: {...}}
    lessons: {type: lesson_book, params: {path: runs/lessons/reach}}
    skills: {type: skill_library, params: {path: runs/skills/reach}}
    reflector: {type: llm.reflector, params: {...}}
```

Before each round the archive so far becomes skills, the lessons that decided candidates relied on are credited, and
the proposer sees the lessons and the skills' status (never the gate numbers, so it cannot fit itself to the gate).

## What it achieved

Measured on MuJoCo tasks on a CPU workstation; details and commands on the [showcase](../showcase/memory.md).

| Experiment | Result |
|---|---|
| Spatial memory with targets visible for 5 steps | success 0.00 → 0.75 (300 pairs, p = 4e-68); no effect when nothing is hidden |
| A skill derived from a campaign, on fresh scenes | 0.47 → 0.86 (200 pairs, p = 6e-19) |
| Action memory, revisited and new scenes | +6 points on both, not significant |
| Action memory across six sessions | small gains that grow with the bank, pooled +5.6 points |

## Limits

- Action memory has not shown a reliable gain on LIBERO: on unseen start states it was 0.08 below the plain policy.
- Lessons change behaviour only through a language model that reads them; on their own they do nothing.
- `memory.steered` assumes the last action dimension is the gripper.
- MuJoCo banks are built with helper functions in the examples; only the LeRobot builder is a command.
- `tools.llm` and world sessions keep their context only within an episode or session; across tasks, only role
  campaigns reuse experience (as recipe skills).

## Next

- [Showcase: Memory](../showcase/memory.md): the runnable examples and their results.
- [Memory interfaces](../harness/interfaces/memory.md): the contracts a new memory backend implements.
- [Skill research, validation and reuse](research-and-skills.md): program skills and recipe skills.
- [Campaigns](campaigns.md): where skills and lessons are produced and credited.
