# Lessons

A lesson is a short note distilled from experience, such as "a narrower grasp slips on flat boxes", that a language
model can use when it proposes the next change to an agent. Lessons are kept in a lesson book: a folder with the
current lessons (`lessons.json`) and a log of every change (`ops.jsonl`).

## Configure lessons { #the-experience-proposer }

Add this proposer fragment to a [campaign](../campaigns.md). It requires the language-model backend used by
the inner proposer and reflector; the example names a model served through Ollama.

Lessons take effect through the `experience` proposer, which wraps any proposer of an improvement campaign:

![The proposer reads lessons and skill status and proposes candidates; the campaign's gate decides them and the archive records the verdicts; from the archive, skills are derived and the lessons that candidates cited are credited; a reflector adds lesson operations from development episodes.](../../assets/diagrams/experience-round-light.svg){ .hylo-diagram .only-light }
![The proposer reads lessons and skill status and proposes candidates; the campaign's gate decides them and the archive records the verdicts; from the archive, skills are derived and the lessons that candidates cited are credited; a reflector adds lesson operations from development episodes.](../../assets/diagrams/experience-round-dark.svg){ .hylo-diagram .only-dark }

```yaml
proposer:
  type: experience
  params:
    inner: {type: llm.steering, params: {model: qwen3.5:35b-a3b}}
    lessons: {type: lesson_book, params: {path: runs/lessons/reach}}
    skills: {type: skill_library, params: {path: runs/skills/reach}}
    reflector: {type: llm.reflector, params: {model: qwen3.5:35b-a3b}}
    skill_tags: [mujoco, reach]             # tags given to the skills it derives
```

Before each round:

1. The archive so far becomes skills, each with the status its evidence supports (see [Skills](skills.md#status)).
2. Lessons cited by candidates that have since been decided are credited: +1 for a verified candidate, −1 for a
   refuted one, once per candidate.
3. The reflector distils new operations from the parent's development episodes, once per run.
4. The inner proposer sees the best active lessons for the tasks at hand (up to eight, by net votes) and the index
   of skills with their status, and lists the lessons each candidate relies on.

The book records the source of each operation, so resuming a campaign does not credit the same outcome twice.

## Reflection { #the-reflector }

`llm.reflector` reads the same development-split material the steering proposer reads (per-episode timelines:
grasp steps, still periods, heights, outcome) and proposes operations. It never sees validation, gate or held-out
results, so lessons cannot carry information from the splits that decide promotion. Every `ADD` must cite episodes
it was shown; uncited or out-of-scope operations are dropped.

<span id="design"></span>
<span id="operations"></span>
<span id="a-lesson"></span>

The reflector proposes small edits to a ranked lesson book. Helpful and harmful outcomes update its counts;
a lesson retires when its harmful count reaches its helpful count plus two. See the
[operation rules](../../reference/memory.md#operations) and [lesson fields](../../reference/memory.md#a-lesson).

## Evaluate { #reading-and-evaluating }

```yaml
lessons: {type: lesson_book, params: {path: runs/lessons/reach, frozen: true}}
```

A frozen book refuses every operation. The Studio's Experience page shows each book's lessons with their counts and
its recent operations.

## Constraints { #limits }

- Lessons do nothing without a language model that reads them.
- The reflector's prompt is written for manipulation timelines; other domains need their own.
- Near-duplicate detection compares titles only.

<span id="what-it-achieved"></span>

## Next

- [Campaigns](../campaigns.md): run the improvement loop.
- [Memory reference](../../reference/memory.md#lessons): fields and operation rules.
- [Recorded results](../../developer-guide/validation/guide-results.md#lessons): measured scope.
