# Memory

Memory is how what a robot agent experienced becomes useful later: where an object was before it was hidden, what a
successful motion looked like in a similar scene, which change to an agent was verified to help, and which notes
from earlier attempts held up. Hylo keeps four kinds of memory. Each is a plugin of the `memory` group, each is a
file or folder you can open and inspect, and each is recorded in the runs that used it.

| Kind | Plugin | Remembers | Read by |
|---|---|---|---|
| [Spatial memory](spatial.md) | `sqlite` | facts with a time and a place: what was seen where, and when | reasoners of composable agents (`composable.object_reach`) |
| [Action memory](action.md) | `action_bank` | motion segments from verified successes, keyed by what the policy saw | `memory.steered`, `lerobot.memory_steered` |
| [Skills](skills.md) | `skill_library` | verified procedures: steering and recovery settings, plans, weights, programs, recipes | the `skills` agent, `code.llm`, improvement campaigns, role campaigns |
| [Lessons](lessons.md) | `lesson_book` | short written lessons from earlier attempts, with helpful and harmful counts | language-model proposers in improvement campaigns |

## How the pieces fit

Memory sits between the records Hylo already keeps (runs, campaigns, sessions) and the agents that act. Something
writes it from evidence; something else reads it at decision time.

| Kind | Written by | From | Read at |
|---|---|---|---|
| Spatial | the agent's reasoner, while it runs | what it perceives | every reasoning step of the same run (or later runs that share the file) |
| Action | `memory_build`, the `lerobot.action_memory` learner, or your own script | verified successful episodes of development splits | every policy decision |
| Skills | `hylo skills`, `hylo research skills`, the experience proposer, role campaign verifiers | campaign archives, promoted programs, replayed tool calls | episode start (`skills` agent), each turn (`code.llm`), each round (proposers), each retry (roles) |
| Lessons | the `llm.reflector`, through the lesson book's operations | development-split episode timelines | each proposal round |

Spatial memory is the agent's working knowledge of the scene. The other three are frozen artifacts during
evaluation: they are built before the run and cannot change while it is being scored.

## Rules

- **Recorded.** An agent that reads a bank or a library puts its content digest in the agent spec (for example
  `bank(40a84dd1afab4a5c,n=…,k=10,…)` or `library(…,verified=1,…)`), so two runs that used different memories never
  look the same, and the digest is checked when a saved bank is loaded.
- **Frozen for evaluation.** An action bank loaded from disk, and a skill library or lesson book opened with
  `frozen: true`, refuse every write: an evaluation cannot learn from the episodes it is scoring.
- **Development data only.** Banks, skills and lessons are built from development splits (`search`,
  `search_val`); gate and held-out episodes are never written into memory.
- **Evidence decides.** A skill becomes verified only through the gate (or, for recipes, a model-free replay that
  achieves the goal). Lessons gain or lose standing from the outcomes of the candidates that cited them, never from a
  model's opinion of itself.
- **Nothing silently disappears.** Facts about the world are invalidated rather than deleted; refuted skills and
  retired lessons stay in their files so later proposals can see what was tried.
- **Visible in traces.** Spatial and action memory emit `memory.write` and `memory.retrieval` events; skills emit
  `skill.applied`. A replay shows which decisions came from memory.

## Choosing a memory

| You want | Use |
|---|---|
| an agent that keeps track of objects it can no longer see | [spatial memory](spatial.md) with a composable agent |
| a frozen flow policy (SmolVLA and similar) to repeat motions that worked in similar scenes | [action memory](action.md) |
| a change that a campaign verified to be applied automatically to matching tasks | a [steering, recovery or plan skill](skills.md) with the `skills` agent |
| a code agent to reuse a program that already passed a gate | a [program skill](skills.md#program-skills) with `code.llm` |
| world tasks to reuse tool calls that solved the same failure before | a [recipe skill](skills.md#recipe-skills) in a role campaign |
| a language-model proposer to build on what worked and avoid what did not | [lessons](lessons.md) with the `experience` proposer |

## What it achieved

Paired comparisons on MuJoCo tasks, the same agent with and without memory on the same episodes, on a CPU
workstation (commands and full tables on the [showcase](../../showcase/memory.md)):

![Success with and without memory in the four MuJoCo memory examples](../../assets/figures/memory-results.png)

| Experiment | Result |
|---|---|
| Spatial memory, targets visible for 5 steps | 0.00 → 0.75 (300 pairs, p = 4e-68); no effect when targets stay visible |
| A verified skill from a campaign, on fresh scenes | 0.47 → 0.86 (200 pairs, p = 6e-19) |
| Action memory, revisited and new scenes | +6 points on both, not significant |
| Action memory carried across six sessions | gains that grow with the bank until session 5, pooled +5.6 points |
| Action memory on LIBERO-10 (SmolVLA) | −0.08 on unseen start states; +0.08 on the same scenes with a fixed t0 (p = 0.10) |

## Inspecting memory

- **Studio**, Experience page: skill libraries with status and evidence, lesson books with their recent operations,
  action banks, and sealed artifacts with provenance. See [Studio](../studio.md#pages).
- **Files**: a bank is `bank.json` plus `bank.npz`; a skill is one `<name>@<version>.json`; a lesson book is
  `lessons.json` plus the `ops.jsonl` log; spatial memory is an SQLite file you can query directly.
- **Traces**: `memory.retrieval` events carry what was retrieved and, for action memory, the similarity, the number
  of segments kept and the strength of the bias (`t0`).

## Limits

- Action memory helps where the retrieval key carries information about the outcome (a low-dimensional state); with
  pooled image features on unseen LIBERO layouts it did not.
- Lessons change behaviour only through a language model that reads them.
- `memory.steered` needs a policy that implements the prior-sampling protocol, and treats the last action
  dimension as the gripper.
- Tool-calling agents and world sessions keep context only within an episode or session; across tasks, only role
  campaigns reuse experience (as recipe skills).

## Pages

- [Spatial memory](spatial.md): items, writes and invalidation, queries, using it from a reasoner.
- [Action memory](action.md): how retrieval steers a policy, building banks, settings.
- [Skills](skills.md): skill kinds, triggers and status, building libraries, how each agent applies them.
- [Lessons](lessons.md): lesson operations, crediting, the experience proposer.
- [Memory interfaces](../../harness/interfaces/memory.md): the contracts a new memory backend implements.
