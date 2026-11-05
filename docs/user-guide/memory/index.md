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
| [Events](events.md) | ordered, episode-scoped observations with evidence and coverage | an agent or planner requesting exact recall |
| [Video](video.md) | sampled chronological RGB history and episode-local feature caches | a compatible frozen SimpleMemVLA agent |
| [Action](action.md) | motion segments from successful development episodes | a frozen flow policy retrieving a sampling prior |
| [Lessons](lessons.md) | notes distilled from experience and credited by outcomes | a proposer planning its next change |

Each kind serves a different decision and has its own retrieval mechanism. A policy can use action memory
without a lesson book, and a reasoner can recall spatial facts without changing the policy.
[Skills](../skills.md) provide the related path for retrieving and applying verified procedures or agent changes.

## Design space

- **Keep provenance.** Spatial facts record what was observed and when. Action banks use successful development
  episodes; skills and lessons carry the evidence appropriate to their source.
- **Respect evaluation boundaries.** Development builds persistent banks and libraries. During evaluation they
  are frozen, while permitted spatial observations, events and video history can still be written within an episode.
- **Make use inspectable.** Memory digests and trace events identify what influenced a decision. Refuted skills
  and retired lessons remain available as records of what did not work.

## When it is written and read

The moment and scope of writing matter as much as the content. Updating a shared experience library from scored
episodes would make results depend on their order. Such libraries stay frozen during evaluation. Episode-local
memory continues to record permitted observations so the agent can use its own history without learning across
test episodes.

![Episode-local observations update spatial, event or video memory. Development runs build banks and campaigns update experience. During evaluation, episode-local memory still changes while shared banks, skills and lessons remain frozen.](../../assets/diagrams/memory-timeline-light.svg){ .hylo-diagram .only-light }
![Episode-local observations update spatial, event or video memory. Development runs build banks and campaigns update experience. During evaluation, episode-local memory still changes while shared banks, skills and lessons remain frozen.](../../assets/diagrams/memory-timeline-dark.svg){ .hylo-diagram .only-dark }

1. **During an episode.** The reasoner writes what it perceives to spatial memory and recalls it when perception
   fails. A `skills` agent applies matching skills when the episode starts. A memory-steered policy retrieves from
   its bank at every decision. Event-memory agents record observations in an episode scope; video-memory agents
   append RGB history and clear it at reset. Durable event journals may retain audit evidence without exposing it
   to another episode.
2. **After development runs.** The successful episodes of the development splits, and only those, are turned into
   an action bank. The bank is sealed with a digest and never changes again; a newer bank is a new artifact.
3. **During a campaign.** With the `experience` wrapper configured, archive verdicts become skills with the status
   their evidence supports, cited lessons receive credit and an optional reflector distils development lessons.
   The inner proposer can consume that context. The separate `harness.program` strategy recalls repair notes
   from active promoted lineages; arbitrary campaigns do not update every memory backend automatically.
4. **At evaluation.** Banks, skill libraries and lesson books are opened frozen and refuse every write. The agent
   spec records each one's digest, so the result names exactly the persistent experience it used. Episode-local
   spatial, event and video memory can still change from observations within that episode.

## Choosing a memory

| You want | Use |
|---|---|
| an agent that keeps track of objects it can no longer see | [spatial memory](spatial.md) with a composable agent |
| exact recall of observed event order, counts or pending intentions | [event memory](events.md) with an observation extractor |
| a frozen video-conditioned VLA to use its episode history | [video memory](video.md) with the optional `simplememvla` agent |
| a frozen flow policy (SmolVLA and similar) to repeat motions that worked in similar scenes | [action memory](action.md) |
| a change that a campaign verified to be applied automatically to matching tasks | a [steering, recovery or plan skill](skills.md) with the `skills` agent |
| a code agent to reuse a program that already passed a gate | a [program skill](skills.md#program-skills) with `code.llm` |
| world tasks to reuse tool calls that solved the same failure before | a [recipe skill](skills.md#recipe-skills) in a role campaign |
| a language-model proposer to build on what worked and avoid what did not | [lessons](lessons.md) with the `experience` proposer |

## What it achieved

The [memory examples](../../developer-guide/validation/memory.md) report paired measurements and reproduction commands. Spatial
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
- Updating shared experience libraries across evaluation episodes is not part of the frozen-library protocol.
  Episode-local observation memory is supported and must remain separate from that persistent learning.

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

## Next

- [Use memory](../using-memory.md): select a consumer and run a first example.
- [Memory interfaces](../../harness/interfaces/memory.md): implement a backend or agent integration.
