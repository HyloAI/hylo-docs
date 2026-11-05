# Skills

Reuse a task implementation with its applicability, version and verification evidence. A skill can supply a
program, a sequence of tool calls, a plan or a change to an agent.

## Reuse paths

| You want to | Start here |
|---|---|
| Develop a program and reuse it in later tasks | [Program skills](research-and-skills.md) |
| Build a library and configure a consuming agent | [Skill library](memory/skills.md) |
| Reuse tool calls after matching goal failures | [Recipe skills](memory/skills.md#recipe-skills) |

## Lifecycle { #develop-validate-deploy-and-reuse }

1. Define the task, robot, observations and success conditions.
2. Develop an implementation and evaluate it beyond its development cases.
3. Add it to the library with the evidence required by its reuse path.
4. Retrieve it for matching tasks and revalidate when the conditions change.

Program skills require a campaign promotion gate. Recipe skills require a successful replay without a model;
that replay checks task success and does not establish a paired statistical improvement.

<span id="development-verification-and-deployment-status"></span>

Freezing preserves an implementation. Verification supports its stated scope. [Deployment](deployment.md)
configures an agent on a server and workcell and requires target validation. A verified library entry does not
mean that a robot is running it.

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
- [Sorting demo](../use-cases/program-skills.md): watch a recorded development and reuse workflow.
