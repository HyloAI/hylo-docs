# Memory

A robot agent without memory starts every episode from nothing. It looks for an object that it saw a moment ago
and that is now behind the gripper, it rediscovers a motion that worked yesterday in the same scene, and an
improvement campaign proposes again a change that last week's campaign already measured and refuted. Memory is
how Hylo carries experience forward: from one step to the next, from one episode to the next, and from one
campaign to the next.

## The problem with memory

Remembering is easy; remembering safely is not. Each of these failures has been seen in practice:

- **Unverified memory is worse than none.** A bank that stores what the agent did, rather than what worked, steers
  the agent back towards its own failures.
- **Memory can leak the test.** If episodes of the split that decides promotion are written into memory, the agent
  is scored on situations it has already been shown, and the gain is an artefact.
- **A model that grades its own notes reinforces its mistakes.** A note survives because the model likes it, not
  because it helped.
- **Memory that cannot be traced makes results unexplainable.** Two runs that look identical may have used
  different memories, and nobody can say which decision came from where.

The design therefore answers four questions for every kind of memory: what is worth remembering, when it is
written, when it is read, and who decides that it can be trusted.

## Memory at four layers of an agent

An agent in Hylo is built in layers that work at different rates: a policy that samples a motion at every decision,
a reasoner that decides at every reasoning step, a configuration that holds for an episode, and an improvement loop
that proposes changes once per round. Experience is useful at each of these layers, but in a different form, and it
must arrive at the rate the layer works at. So instead of one store for everything, each layer has its own kind of
memory, shaped for what that layer consumes.

![Each kind of memory attaches to one layer of an agent: lessons to the improvement loop's proposer, once per round; skills to the agent's configuration, once per episode; spatial memory to the reasoner, at each reasoning step; action memory to the policy's sampling, at each decision.](../../assets/diagrams/memory-layers-light.svg){ .hylo-diagram .only-light }
![Each kind of memory attaches to one layer of an agent: lessons to the improvement loop's proposer, once per round; skills to the agent's configuration, once per episode; spatial memory to the reasoner, at each reasoning step; action memory to the policy's sampling, at each decision.](../../assets/diagrams/memory-layers-dark.svg){ .hylo-diagram .only-dark }

| Layer | Consumes | So its memory holds | Memory |
|---|---|---|---|
| Policy sampling | a starting point for the next motion | motion segments from successful episodes, keyed the way the policy sees a situation | [action memory](action.md) |
| Reasoner | facts about the scene | positions and times of what was perceived | [spatial memory](spatial.md) |
| Agent configuration | settings, plans and rules for one episode | verified changes and procedures, with the condition under which they apply | [skills](skills.md) |
| Improvement loop | ideas for the next change | short written lessons, ranked by how the changes that relied on them fared | [lessons](lessons.md) |

The lower the layer, the more concrete the memory and the more often it is read; the higher the layer, the more
abstract it is and the longer it lives. Each memory talks only to its own layer, through that layer's existing
interface: action memory gives the sampler a starting point, spatial memory answers the reasoner's queries, a skill
is a configuration patch, a lesson is text in a proposer's prompt. No layer needs to know that memory exists in
order to work without it.

## Design space

Every memory system makes the same handful of choices. These are Hylo's, and why.

| Question | Options | Choice | Why |
|---|---|---|---|
| What is stored? | everything the agent did, or only what worked | only experience the simulator, a gate or a replay verified | unverified memory steers an agent back towards its failures |
| From which data? | any episode, or development data only | development splits only | memory built from the splits that decide promotion would leak the test |
| Who decides it is right? | the model that wrote it, or the outcomes | outcomes: gate verdicts, replays, credit from cited candidates | a model grading its own notes reinforces its mistakes |
| When is it written? | continuously, or between runs | between runs and campaign rounds; frozen during evaluation | results must not depend on the order in which parallel episodes finished |
| How does it act? | replace the agent's decision, or bias it | bias: a prior for sampling, a patch for one episode, text for a proposer | a wrong memory should cost a little, not everything |
| What form does it take? | code, or data | data (configuration, templates, segments, text); programs only as sealed artifacts run in a sandbox | data can be inspected, compared, applied and undone |
| What happens to old memory? | delete, or invalidate | invalidate facts, keep refuted skills and retired lessons | queries "as of" a time, and proposers that do not repeat refuted ideas |
| Can its effect be traced? | opaque, or recorded | digests in the agent spec, events in the trace | an outcome must be attributable to the memory that influenced it |

## When it is written and read

The moment of writing matters as much as the content. Writing during an evaluation would let the agent learn from
the episodes being scored, and would make the result depend on the order in which parallel episodes happened to
finish. So writing and reading are separated in time.

![During an episode, spatial facts are written while visible and memory is read at every decision. After development runs, a bank is built from verified successes. During a campaign, verdicts become skills and credit lessons, which the proposer reads. At evaluation nothing is written: banks, skills and lessons are frozen and only read.](../../assets/diagrams/memory-timeline-light.svg){ .hylo-diagram .only-light }
![During an episode, spatial facts are written while visible and memory is read at every decision. After development runs, a bank is built from verified successes. During a campaign, verdicts become skills and credit lessons, which the proposer reads. At evaluation nothing is written: banks, skills and lessons are frozen and only read.](../../assets/diagrams/memory-timeline-dark.svg){ .hylo-diagram .only-dark }

1. **During an episode.** The reasoner writes what it perceives to spatial memory and recalls it when perception
   fails. A `skills` agent applies matching skills when the episode starts. A memory-steered policy retrieves from
   its bank at every decision. Apart from a spatial memory file you chose to keep, nothing that outlives the run is
   written.
2. **After development runs.** The successful episodes of the development splits, and only those, are turned into
   an action bank. The bank is sealed with a digest and never changes again; a newer bank is a new artifact.
3. **During a campaign.** After every round, the archive's verdicts become skills with the status their evidence
   supports, the lessons that the decided candidates relied on are credited, and a reflector distils new lessons from
   development episodes. The proposer reads lessons and skill status before planning the next round.
4. **At evaluation.** Banks, skill libraries and lesson books are opened frozen and refuse every write. The agent
   spec records each one's digest, so the result names exactly the memory it used.

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

The results follow the design's own logic. Spatial memory helps exactly when perception fails and not otherwise. A
skill helps on fresh scenes because it carries a verdict, not a guess. Action memory helps where the retrieval key
says something about the outcome (a low-dimensional state) and not where it does not (pooled image features on a
layout the bank has never seen); because it only biases the policy, the cost of a poor retrieval stays small.

## Limits

- Action memory has not given a reliable gain on LIBERO.
- Lessons change behaviour only through a language model that reads them.
- Tool-calling agents and world sessions keep context only within an episode or session; across tasks, only role
  campaigns reuse experience (as recipe skills).
- An online mode, in which a deployed agent writes memory while it works, is not part of this release: it would
  make results depend on the order of episodes, and needs its own way of reporting that.

??? info "Where memory lives on disk"

    ```text
    runs/memory/table.sqlite             spatial memory: one table of items with both time axes and positions
    runs/memory/l10-search-v1/           an action bank: bank.json, bank.npz, build_report.json, artifact.json
    runs/skills/reach/                   a skill library: one <name>@<version>.json per skill version
    runs/lessons/reach/                  a lesson book: lessons.json and the ops.jsonl log
    ```

    The Studio's Experience page shows skill libraries with status and evidence, lesson books with their recent
    operations, and action banks with their provenance (see [Studio](../studio.md#pages)). The contracts a new
    backend implements are in [Memory interfaces](../../harness/interfaces/memory.md).
