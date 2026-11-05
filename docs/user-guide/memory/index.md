# Memory

Give an agent access to earlier observations and experience. Memory can retain object locations, recall event
history, supply video context, retrieve successful motions or inform the next proposed change.

## Memory types { #memory-and-its-consumers }

| Capability | Use | Consumer |
|---|---|---|
| Recall object locations | [Spatial memory](spatial.md) | a composable agent or reasoner |
| Recall event order and counts | [Event memory](events.md) | an agent with an observation extractor |
| Use earlier camera frames | [Video memory](video.md) | a compatible frozen SimpleMemVLA agent |
| Retrieve successful motions | [Action memory](action.md) | a flow policy supporting memory steering |
| Learn from previous attempts | [Lessons](lessons.md) | the `experience` proposer |

A backend needs a consumer that reads it. Adding a memory plugin alone does not make an arbitrary model use
memory. For reusable procedures and agent changes, see [Skills](../skills.md).

<span id="choosing-a-memory"></span>

## Quickstart

[Use memory](../using-memory.md) starts with a CPU event-recall example, then explains how to connect a consumer.
Choose a backend above for its configuration and integration steps.

<span id="design-space"></span>

## Memory lifetime { #when-it-is-written-and-read }

| Scope | Written | Read |
|---|---|---|
| Episode history | from permitted observations during an episode | by the agent in that episode |
| Action banks | from successful development episodes | by a compatible policy, with the bank frozen |
| Lessons | from development diagnostics and credited campaign outcomes | by a proposer planning its next change |

![Episode history updates within an episode; development builds persistent banks and lessons, which stay frozen during evaluation.](../../assets/diagrams/memory-timeline-light.svg){ .hylo-diagram .only-light }
![Episode history updates within an episode; development builds persistent banks and lessons, which stay frozen during evaluation.](../../assets/diagrams/memory-timeline-dark.svg){ .hylo-diagram .only-dark }

## Constraints { #limits }

- Scope and reset episode history so another evaluation episode cannot read it. A persistent journal can retain
  audit evidence without exposing that evidence to later episodes.
- Freeze shared banks, skill libraries and lesson books during evaluation. Record their digests with the agent.
- Verify that the consumer uses the retrieved context. Lessons require a model that reads them; action-memory
  benefit depends on retrieval quality and needs a comparison on the target task.
- Tool-agent and world-session context stays within its episode or session. Role campaigns reuse experience
  across tasks through [recipe skills](skills.md#recipe-skills).

## Studio { #in-the-studio }

The Experience page shows skill libraries, lesson books and action banks under the runs directory, with their
status and evidence.

<video src="../../assets/videos/studio-experience.mp4" poster="../../assets/videos/studio-experience.jpg" controls muted playsinline preload="none" width="100%" aria-label="Studio Experience: skill libraries, lesson books and action banks"></video>

<span id="what-it-achieved"></span>

## Next

- [Use memory](../using-memory.md): connect a backend to an agent.
- [Memory reference](../../reference/memory.md): fields, queries and storage rules.
- [Recorded results](../../developer-guide/validation/guide-results.md): measured benefits and failures.
