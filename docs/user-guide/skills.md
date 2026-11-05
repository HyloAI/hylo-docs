# Skills

A robot skill is a reusable ability to carry out a task under stated robot, scene and observation conditions.
Hylo keeps reusable implementations with their applicability, version and validation evidence, so later agents
can build on what has already worked.

## Watch skill development and reuse

[Watch the recorded sorting-skill demo](research-and-skills.md#recorded-skill-development-demo): an AI model
extends an existing program, submits it for independent execution, passes a paired promotion gate and creates a
verified program skill that a later agent calls on new layouts. The full English walkthrough includes measured
results, observation conditions and replay provenance.

## Memory and skills

[Memory](memory/index.md) carries observations and experience forward. Skills express what can be reused to
perform a task: a procedure, a plan or a change to an agent. A remembered object location helps a decision;
a verified stacking program supplies behaviour the agent can call again.

The skill library is implemented in the memory package, but has its own retrieval, status and application rules.
See [Skill library](memory/skills.md) for kinds, triggers, evidence, commands and agent configuration.

## Develop, validate, deploy and reuse

1. State the task, robot, observations and success conditions.
2. [Develop a program](developing-strategies.md) or use a [policy](policies.md), then evaluate beyond its development cases.
3. For an improvement, compare with the current version through a [campaign](campaigns.md).
4. Keep supported results in the [skill library](memory/skills.md#building-a-library), with their evidence and scope.
5. Retrieve them for later tasks and revalidate when the robot or task conditions change.

Program skills come from promoted program candidates. Recipe skills come from role campaigns after a replay
without a model achieves the goal. These checks support different claims: recipe verification is not a paired
statistical improvement gate. [Program research](research-and-skills.md) explains the development and promotion
path; [world role campaigns](worlds.md#tasks-with-roles) explain recipe development.

## Development, verification and deployment status

Freezing a program preserves an implementation. Verification records evidence for its stated scope. Deployment
configures an agent on a policy server and workcell and requires target validation. These are separate operations;
a verified library entry does not mean that a robot is running it.

Programs, policies and controllers can all implement robot capabilities. Current library records cover specific
reuse paths; there is no common skill wrapper for every policy. The [library status rules](memory/skills.md#status)
describe which evidence changes a record's status.

## Robot skills, program skills and coding-agent skills

“Robot skill” names the task capability. A program or recipe skill is a concrete library record referring to an
implementation and evidence. A coding-agent skill is a `SKILL.md` instruction file teaching a software agent to
operate Hylo; it does not itself implement the robot's task behaviour.

## Next

- [Skill library](memory/skills.md): build a library, match skills and apply them.
- [Program research](research-and-skills.md): develop, freeze and validate a program.
- [Deployment](deployment.md): configure an implementation on a workcell.
- [Recorded results](../developer-guide/validation/tool-agents.md): measured scope, failures and unrun workflows.
