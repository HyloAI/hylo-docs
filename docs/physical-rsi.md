# Physical RSI

Physical recursive self-improvement uses task outcomes to propose changes, verify their effects and carry adopted
changes into later rounds. Hylo connects four capabilities in this loop: [agents](user-guide/agents.md) act in
[worlds](user-guide/worlds.md), [memory](user-guide/memory/index.md) carries experience forward, and
[skills](user-guide/skills.md) make verified capabilities reusable. People define the goals and boundaries.

![The Physical RSI loop: Build, Run, Improve, Verify and Deploy, with RSI campaigns over Improve and Verify and Serve beneath all five](assets/diagrams/physical-rsi-light.svg){ .hylo-diagram .only-light }
![The Physical RSI loop: Build, Run, Improve, Verify and Deploy, with RSI campaigns over Improve and Verify and Serve beneath all five](assets/diagrams/physical-rsi-dark.svg){ .hylo-diagram .only-dark }

## The bottleneck

Robots can act autonomously while still depending on people to drive their improvement. Teams collect runs, diagnose
failures, choose changes, evaluate candidates and decide what to deploy. When people must coordinate every turn,
robots improve only as fast as those teams can close the loop.

Physical RSI puts the system to work on that loop: a robot system uses the outcomes of physical tasks to propose and
evaluate changes, and carries the changes it adopts into the next rounds of execution and improvement. People set
the goals and boundaries and approve promotion to hardware.

Surveys of self-evolving agents describe the same shift from the other side: the field has moved from static models
towards agents that keep improving after deployment, yet almost all of that work is on software agents, while
embodied systems are still largely trained offline and updated release by release [1, 2, 3].

## Grounding

The recognised limit of self-improvement is its evaluation signal. A system that grades its own work drifts; how far
self-improvement goes tracks how trustworthy the signal is, from formal verifiers and execution feedback down to
self-assessment [4].

Physical tasks give self-improvement an external test: whether an action produced the intended result in the world.
Measured outcomes, checked under stated conditions and independently of the agent's own account, provide evidence
for keeping useful changes and rejecting failed ones. This makes physical AI a promising setting for recursive
self-improvement: the loop advances on demonstrated capability.

## The loop

| Activity | What it does | In Hylo |
|---|---|---|
| **Build** | Create, adapt or reconstruct the worlds and task conditions for development and evaluation. | [Worlds](user-guide/worlds.md) built from text with two dozen robot packs and people; benchmark environments and perturbations; recorded episodes rebuilt in simulation; outside data such as demonstrations and videos |
| **Run** | Execute policies or agents in simulation or on robots, recording actions, conditions and measured outcomes. | [Policies](user-guide/policies.md), [tool-calling agents](user-guide/tool-agents.md) and [program agents](user-guide/developing-strategies.md) on one episode loop behind the [safety shield](user-guide/safety.md) |
| **Improve** | Use development outcomes and experience to train models, update memory or change settings, prompts, programs and skills, then freeze candidates. | [Learning](user-guide/learning.md): policies, critics, world models and judges trained from runs; [memory](user-guide/memory/index.md); research sessions that write programs; [skills](user-guide/skills.md) |
| **Verify** | Evaluate frozen candidates with checks that suit their claims, kept separate from their development. | [Experiments](user-guide/experiments.md), [benchmarking](benchmarking/index.md), the campaign gate and held-out reports, sealed runs |
| **Deploy** | Activate approved versions for later runs and improvement; promotion to hardware requires human approval. | Versions and rollback, the [skill library](user-guide/memory/skills.md), [policy servers and workcells](user-guide/deployment.md) |

The main path runs from Run through Improve, Verify and Deploy back to Run: each round starts from the versions the
last one adopted. Build connects to Run in both directions. New worlds go into execution, and the tasks, failures
and recordings that execution produces guide which worlds to build next. A candidate that fails verification goes
back to Improve, and the cases that rejected it never become development data.

[Studio](user-guide/studio.md) shows the loop as it turns, and the CLI and an MCP server let people and external
agents drive it.

## Campaigns

An improvement [campaign](user-guide/campaigns.md) is the RSI engine: it connects proposals to gates. Rules,
learners and language models propose changes; a campaign tests them against the current version on cases that
played no part in proposing or choosing them, promotes only what passes, and records every promotion so it can be
rolled back. What a candidate may change is bounded: never the safety settings, the scorers, the benchmark or the
campaign itself.

## Serve

Serve runs agents behind policy servers and workcells next to a robot or simulator. A workcell owns execution,
safety checks and the recorded episode; Studio provides operator controls. The recorded robot-adapter bring-up
uses a simulated arm. Follow [Deployment](user-guide/deployment.md) to configure and validate a target setup.

## What improves

Improvement is not only retraining. A round can change runtime settings, recovery rules, prompts, programs, memory,
skills, learned components or the policy weights themselves, and the worlds the robot practises in. Each is versioned
and verified in the way that suits it, and each can carry progress into the next round: a trick found on site can
become a program or a skill now instead of waiting for the next training run.

## What you bring

You bring a starting point and a goal:

- **a robot**, described to Hylo by its arms, hands, cameras and action layout;
- **a task**, and the check that decides whether it succeeded;
- **anything you already have**, optionally: a vision-language-action model or other policy, task programs,
  demonstrations, videos, logs from other robots.

You take away versions you can deploy and roll back, with the evidence for each, and the models, programs, memory
and skills that the next round builds on.

## Control

The loop can be left to turn because each step is bounded. The task's own check decides success, never the model;
every candidate is tested on cases it was not developed on; runs are recorded as traces that can be sealed and audited;
versions can be rolled back; and promotion to hardware requires human approval. Rollback changes the active version;
it does not undo physical actions, which is why every action passes the safety shield first.

## Why now

Until recently each turn of the loop needed a person, because only people could read a failure, write the code and
build the scene. Language and vision models can now understand a task, plan, write programs and call tools, and a
simulator can build a world from a sentence. The loop can now turn without a person at every step: people set the
goals and approve what ships.

## Direction

The direction is progress that carries over: from one round to the next, and from one task and robot to the next.
Each version, program and skill carries its implementation, applicability and evidence, so later runs and agents
can build on what already works and verify it in new settings. What one robot learns becomes a starting point for
others, and each verified advance becomes material for further improvement.

## Further reading

1. Nguyen et al., [Self-Evolving AI for Humanoids: Mechanisms, Safety, and Evaluation of Post-Deployment
   Self-Improvement](https://arxiv.org/abs/2609.13236), 2026.
2. Gao et al., [A Survey of Self-Evolving Agents: What, When, How, and Where to Evolve on the Path to Artificial
   Super Intelligence](https://arxiv.org/abs/2507.21046), TMLR 2026.
3. Fang et al., [A Comprehensive Survey of Self-Evolving AI Agents: A New Paradigm Bridging Foundation Models and
   Lifelong Agentic Systems](https://arxiv.org/abs/2508.07407), 2025.
4. Chen et al., [Recursive Self-Improvement in AI: From Bounded Self-Refinement to Autonomous Research
   Loops](https://arxiv.org/abs/2607.07663), 2026.
5. Li, [Dynamic Agent Skills: A Lifecycle Survey and Taxonomy of Evolving Skill
   Libraries](https://arxiv.org/abs/2607.10113), TMLR 2026.
6. Wei et al., [A Survey of Agentic Reasoning for Large Language Models: Towards Recursively Self-Improving and
   Collective Agents](https://arxiv.org/abs/2601.12538), TMLR 2026.
7. [A Comprehensive Survey on World Models for Embodied AI](https://arxiv.org/abs/2510.16732), 2025.
