# Lessons

A lesson is a short note distilled from experience, such as "a narrower grasp slips on flat boxes", that a language
model can use when it proposes the next change to an agent. Lessons are kept in a lesson book: a folder with the
current lessons (`lessons.json`) and a log of every change (`ops.jsonl`).

## A lesson

| Field | Meaning |
|---|---|
| `kind` | `strategy` (what successful episodes did) or `pitfall` (a failure pattern to avoid) |
| `scope` | `global`, or `task:<id>` for one task |
| `title`, `content` | at most 12 words; at most 60 words |
| `helpful`, `harmful` | votes: from the reflector when new episodes confirm or contradict it, and from the outcomes of candidates that relied on it |
| `evidence` | the episodes it was drawn from or confirmed by (the last 20) |
| `status` | `active` or `retired` |

## Operations

The book is never rewritten as a whole. A reflector model proposes operations, and the book applies them by fixed
rules:

| Operation | Effect |
|---|---|
| `ADD` | a new lesson; if an active lesson in the same scope has a near-identical title, it is upvoted instead |
| `UPVOTE`, `DOWNVOTE` | one more helpful or harmful count, with the episodes as evidence |
| `EDIT` | new content; the counts are kept |
| `RETIRE` | removed from retrieval, kept in the file |

A lesson whose harmful count reaches its helpful count plus two retires itself. Invalid operations are reported, not
applied. Every applied operation is appended to the log with its time and source.

## The reflector

`llm.reflector` reads the same development-split material the steering proposer reads (per-episode timelines:
grasp steps, still periods, heights, outcome) and proposes operations. It never sees validation, gate or held-out
results, so lessons cannot carry information from the splits that decide promotion. Every `ADD` must cite episodes
it was shown; uncited or out-of-scope operations are dropped.

## The experience proposer

Lessons take effect through the `experience` proposer, which wraps any proposer of an improvement campaign:

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

Step 4 is what closes the loop: a lesson gains standing only when the candidates that cite it pass the gate, so the
book's ranking follows evidence rather than the model's confidence. Resuming a campaign does not repeat a step; the
book records the source of every operation.

## Reading and evaluating

```yaml
lessons: {type: lesson_book, params: {path: runs/lessons/reach, frozen: true}}
```

A frozen book refuses every operation. The Studio's Experience page shows each book's lessons with their counts and
its recent operations.

## What it achieved

Two experience campaigns on MuJoCo planar reach wrote, read and credited a lesson book with `llm.reflector` on a
local model. The effect of lessons on promotion has not been measured separately: it needs a language model in the
loop and enough rounds to compare with and without lessons.

## Limits

- Lessons do nothing without a language model that reads them.
- The reflector's prompt is written for manipulation timelines; other domains need their own.
- Near-duplicate detection compares titles only.
