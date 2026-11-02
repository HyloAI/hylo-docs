# Robot skills and their lifecycle

Hylo helps teams develop, validate, deploy and accumulate robot skills. A skill is a reusable ability to carry
out a class of tasks under stated conditions: for example, stack blocks on a table with a particular robot and
observation setup. New tasks, changed scenes and goals for speed or reliability can all motivate skill development.

This is the user-facing way to connect the stack. The kernel, agents, policies, tools, evaluation and deployment
services retain their technical responsibilities.

![Develop and run a skill, validate it, version and deploy the implementation, reuse it and improve it with new evidence](../assets/diagrams/skill-lifecycle-light.svg){ .hylo-diagram .only-light }
![Develop and run a skill, validate it, version and deploy the implementation, reuse it and improve it with new evidence](../assets/diagrams/skill-lifecycle-dark.svg){ .hylo-diagram .only-dark }

## Design

**A skill is a claim, not a piece of code.** The same capability can have several implementations (a program, a
model policy, a controller), and one model policy can carry several capabilities. What makes something a skill is
the claim that it does a class of tasks under stated conditions, and the evidence for that claim. So a skill is
defined by five parts, of which the implementation is only one.

**Evidence holds only for the conditions it was measured under.** A success rate measured in simulation, with
privileged segmentation, on one robot, says nothing yet about a different camera or a real arm. The conditions
travel with every result, and a change in conditions calls for validation again, not for trust.

**Developing and validating are separate acts.** Whatever an implementation was tuned on cannot be its evidence.
An implementation is frozen first and then tested on cases it was never developed on. A first skill is checked
against its task requirements; an improvement is compared with the version it replaces, through the gate. These are
two different questions and need two different tests.

**Frozen, verified and deployed are three different states.** Freezing keeps an implementation unchanged; it does not
mean it works. Verification records that it passed a test; it changes nothing on a robot. Deployment happens only
when a person points a policy server and a workcell at a version. Each step is owned by a different mechanism, so
none of them can be skipped by accident.

**The lifecycle maps onto existing mechanisms instead of wrapping them.** Policies, programs and configurations are
validated and deployed in different ways. Hylo does not force one skill wrapper around all of them; it connects the
records each mechanism already keeps (sessions, runs, artifacts, campaign versions, skill-library records), so the
difference between them stays visible.

## What defines a skill

| Part | Questions it answers | Current mechanisms |
|---|---|---|
| Task and applicability | What does it do? On which robot, scenes and observations? | task specs, robot contract, experiment config, skill triggers and preconditions |
| Implementation | How does the robot perform it? | a program, model policy, controller or agent composition |
| Validation evidence | What was measured, on which cases, with what limits? | traces, run results, scorecards and campaign gate/held-out reports |
| Version and dependencies | Which implementation and assets were tested? | program/artifact digests, manifests, campaign versions and runtime configuration |
| Use and feedback | How is it called and what happens when used? | agent configuration, program-skill retrieval, workcell runs and skill feedback |

A model policy can implement several task capabilities, and one task capability may have several implementations.
Keep the implementation and its validation conditions attached to each result. Simulation success, privileged
segmentation and performance on one robot establish evidence for those conditions only.

## Develop, validate, deploy and reuse

1. **Define the goal.** Describe the task, robot, observations, success conditions and constraints.
2. **Develop and run.** Bring a policy or controller, write a program using robot tools, or use a model-assisted
   research session. Inspect execution and iterate on development cases.
3. **Validate.** Freeze the implementation and test separate cases. A first skill is checked against its task
   requirements. A claimed improvement also needs comparison with the previous version; campaign promotion uses the gate.
4. **Version and deploy.** Review the implementation, evidence and dependencies. Configure the selected agent or
   campaign version on a policy server and workcell, and validate it on the target robot.
5. **Reuse and improve.** Retrieve a verified program skill, reuse an implementation/configuration, or develop a new
   version. Collect execution evidence and revalidate when conditions change.

These activities have multiple starting points. An existing policy can enter execution and validation directly;
a new task can begin with development. A failure is one kind of evidence, alongside new requirements and efficiency goals.

## Development, verification and deployment status

The lifecycle above describes activities; it is not a single status field implemented across all packages.

- Development sessions record attempts and frozen submissions. Freezing preserves an implementation; it does not
  mark it verified or deploy it.
- The current `Skill`/`SkillLibrary` records use `proposed`, `verified`, `refuted` and `deprecated`. They support
  plan, steering, recovery, weights and program kinds. Automatic derivation and reuse depend on the kind; the
  documented new path derives program skills from promoted code candidates.
- A campaign's active version is recorded separately in `active.json`. A policy server and workcell must be
  configured to run it. `verified` is not a deployment status.

The current interfaces are research sessions, runs, artifacts, campaign versions and skill-library records.
There is no universal skill dashboard or common skill wrapper for every policy. The guides map each lifecycle
activity to the mechanisms available today.

## Robot skills, program skills and coding-agent skills

| Term | Meaning |
|---|---|
| Robot skill | the task capability used to explain the product workflow |
| Program skill | a `Skill(kind="program")` record referencing a sealed program, applicability and gate evidence; a code agent can retrieve and call it |
| Recipe skill | a `Skill(kind="recipe")` record: the tool calls that solved a world task, keyed by the reasons its goal failed at the start, admitted only after a replay without a model achieved the goal |
| Coding-agent skill | a `SKILL.md` instruction file under `harness/agent-skills/` teaching a software agent to operate Hylo commands |

Program skills are one implementation/reuse path for robot capabilities. The instruction files document how to
operate the tooling; they do not themselves provide a robot's task behaviour.

## Where to start

- [Developing robot skills](developing-strategies.md): tools, program agents and a reference execution.
- [Skill research, validation and reuse](research-and-skills.md): development sessions, independent checks, campaigns and program skills.
- [Memory](memory/index.md): spatial memory, action memory, skill libraries and lessons.
- [Policies](policies.md): connect an existing model or controller.
- [Benchmarking](../benchmarking/index.md): fixed protocols and comparable evidence.
- [Deployment](deployment.md): policy servers, workcells and target validation.
- [Studio](studio.md): inspect the records from these activities.

The [showcase](../showcase/tool-agents.md) reports what has run, under which conditions, including unsuccessful
results and unrun workflows. It does not establish general autonomous skill acquisition or cross-robot transfer.
