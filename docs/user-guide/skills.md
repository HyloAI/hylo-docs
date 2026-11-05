# Skills

Reuse a task implementation with its applicability, version and verification evidence. A skill can supply a
program, a sequence of tool calls, a plan or a change to an agent.

## Reuse paths

| You want to | Start here |
|---|---|
| Develop a program and reuse it in later tasks | [Program skills](research-and-skills.md) |
| Build a library and configure a consuming agent | [Skill library](memory/skills.md) |
| Reuse tool calls after matching goal failures | [Recipe skills](memory/skills.md#recipe-skills) |

## Representation

A library record connects four things: an implementation, the conditions in which it applies, a version and
the evidence supporting its status. Its body can hold a configuration change, subgoal templates, a reference to
a sealed program or a sequence of tool calls. This makes a useful result reusable without asking a model to
rediscover the same procedure from an earlier conversation.

The consuming component determines what can be applied. A skill agent can adjust steering or recovery rules
for an episode; a code agent can call a program; a role campaign can offer a recipe after a matching goal failure.
A weights change is evaluated as a campaign candidate. These paths share library concepts, but each needs its
own compatible execution mechanism.

## Lifecycle { #develop-validate-deploy-and-reuse }

1. Define the task, robot, observations and success conditions.
2. Develop an implementation and evaluate it beyond its development cases.
3. Add it to the library with the evidence required by its reuse path.
4. Retrieve it for matching tasks and revalidate when the conditions change.

Program skills require a campaign promotion gate. Recipe skills require a successful replay without a model;
that replay checks task success and does not establish a paired statistical improvement.

### Evidence and status

A newly proposed skill is retained as a candidate. Passing the applicable gate or replay makes it verified;
rejection can refute it, and an inconclusive improvement remains proposed. A promoted program that later fails
revalidation can be deprecated. Only verified entries are eligible for application. Failed entries remain
available as evidence of what was tried, rather than disappearing and being proposed again without context.

![Skill evidence determines whether a proposed entry becomes verified or refuted, remains proposed, or is deprecated after failed revalidation.](../assets/diagrams/skill-status-light.svg){ .hylo-diagram .only-light }
![Skill evidence determines whether a proposed entry becomes verified or refuted, remains proposed, or is deprecated after failed revalidation.](../assets/diagrams/skill-status-dark.svg){ .hylo-diagram .only-dark }

<span id="development-verification-and-deployment-status"></span>

Freezing preserves an implementation. Verification supports its stated scope. [Deployment](deployment.md)
configures an agent on a server and workcell and requires target validation. A verified library entry does not
mean that a robot is running it.

## Retrieval and execution

Matching uses the task's instruction, tags, environment or goal-failure reasons, depending on the skill kind.
For example, a role campaign can retrieve a recipe when a new task fails the same checks as the task that
produced it. Program skills are ranked by instruction and description similarity; the current retrieval uses
word overlap. Matching suggests applicability, so new robots, sensors or task conditions still need validation.

Before a program is offered to a code agent, its source is read back, its digest is compared with the recorded
version and its code is checked against the execution restrictions. The model receives callable functions with
descriptions and preconditions. This separates selecting a known implementation from generating new task code.

The skill agent applies steering, recovery and plan changes for the current episode and restores the wrapped
agent afterwards. Applications and outcomes are recorded so users can inspect which skill influenced a result.
During evaluation the library is frozen: reuse can change an episode's behaviour without silently learning a
new shared skill from that episode's score.

## Skill types { #robot-skills-program-skills-and-coding-agent-skills }

“Robot skill” names a task capability. A program or recipe skill is a library record referencing an implementation
and evidence. A coding-agent skill is a `SKILL.md` instruction file for a software agent operating Hylo.
Policies and controllers can implement robot capabilities, but the library does not wrap every policy in a
common skill format. See the [supported kinds](../reference/memory.md#skill-kinds).

## Memory and skills

[Memory](memory/index.md) supplies earlier observations and experience; skills supply something an agent can
apply or execute. A remembered location informs a decision. A retrieved sorting program supplies the behaviour.

<span id="watch-skill-development-and-reuse"></span>

## Next

- [Program skills](research-and-skills.md): develop, verify and reuse a program.
- [Skill library](memory/skills.md): build a library and configure retrieval.
- [Sorting demo](skills/development-and-reuse.md): watch a recorded development and reuse workflow.
