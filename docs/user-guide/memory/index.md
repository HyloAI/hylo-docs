# Memory

Memory carries observations and experience into later decisions. Spatial memory recalls where something was;
action memory retrieves motions that succeeded; lessons help a proposer use previous experience when choosing
its next change.

[Skills](../skills.md) are a related, distinct capability: reusable procedures and agent changes with applicability
and verification evidence. Their library lives in the memory package; its kinds, status and reuse rules are
documented under [Skill library](skills.md).

## Memory and its consumers

| Memory | What it keeps | Who uses it |
|---|---|---|
| [Spatial](spatial.md) | facts about objects and places, with time and frame information | a reasoner recalling an observation |
| [Action](action.md) | motion segments from successful development episodes | a frozen flow policy retrieving a sampling prior |
| [Lessons](lessons.md) | notes distilled from experience and credited by outcomes | a proposer planning its next change |

Each kind serves a different decision and has its own retrieval mechanism. A policy can use action memory
without a lesson book, and a reasoner can recall spatial facts without changing the policy.
[Skills](../skills.md) provide the related path for retrieving and applying verified procedures or agent changes.

## Design space

- **Keep provenance.** Spatial facts record what was observed and when. Action banks use successful development
  episodes; skills and lessons carry the evidence appropriate to their source.
- **Respect evaluation boundaries.** Development builds persistent banks and libraries. During evaluation they
  are frozen, while spatial observations can still be written within an episode.
- **Make use inspectable.** Memory digests and trace events identify what influenced a decision. Refuted skills
  and retired lessons remain available as records of what did not work.

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

The [memory examples](../../showcase/memory.md) report paired measurements and reproduction commands. Spatial
memory helped when targets became occluded, and a verified steering skill helped on fresh MuJoCo scenes.
Action-memory gains depend on retrieval quality; the recorded LIBERO results do not establish a reliable gain.

## In the Studio

The Experience page shows every skill library, lesson book and action bank under the runs directory, with status and evidence.

<video src="../../assets/videos/studio-experience.mp4" poster="../../assets/videos/studio-experience.jpg" controls muted playsinline preload="none" width="100%" aria-label="The Studio's Experience page: skill libraries with gate evidence, lesson books and their curation log, an action bank"></video>

*Skill libraries with their gate evidence, lesson books with their curation log, and an action bank.*

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
