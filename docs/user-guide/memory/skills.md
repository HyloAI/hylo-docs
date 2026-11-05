# Skill library

The library stores versioned [skills](../skills.md), their applicability, status and evidence. Its records hold data:
a configuration change, a subgoal plan, a reference to trained weights or to a sealed program, or a list of tool calls. A skill library is a
folder with one JSON file per skill version (`<name>@<version>.json`). Agents look skills up when a task starts,
when a code agent writes its next block, when a proposer plans a round, or when a goal fails.

## Build a library { #building-a-library }

You need an existing campaign archive. The commands below run from the **workspace root**; replace the campaign
paths with your own. For a complete example that produces a promoted program before building the library, follow
[Develop and reuse a program skill](../research-and-skills.md).

```bash
# steering and weights skills from an improvement campaign's archive
uv run hylo skills runs/campaigns/l10 --out runs/skills/libero10 --tags libero libero_10 --env libero
# program skills from a campaign's promoted code candidates
uv run hylo research skills runs/campaigns/pick --library runs/skills/manip --family pick_place
```

`hylo skills` turns every decided archive entry into a skill version with the status its evidence supports, and is
safe to run again: entries already in the library are skipped. Candidates that change something other than the
steering configuration or the weights are not expressible as skills and are listed as skipped.

The `experience` proposer runs the same conversion before every round of a campaign, so a library grows while the
campaign runs (see [Lessons](lessons.md#the-experience-proposer)). Role campaigns add recipe skills themselves, after
the verifier's replay.

## Select skills { #design }

Only verified skills are applied. Matching uses the task, environment or failure signature, depending on the skill
kind. Program retrieval uses instruction similarity. A skill record references its implementation and evidence;
programs are checked again before being offered to a code agent.

<span id="skill-kinds"></span>
<span id="triggers"></span>
<span id="status"></span>

See the [supported kinds](../../reference/memory.md#skill-kinds), [matching rules](../../reference/memory.md#triggers)
and [status transitions](../../reference/memory.md#status). Refuted skills remain in the library as evidence of
unsuccessful candidates. Proposers see their status without the gate's effect sizes or p-values.

## Apply skills { #applying-skills }

The fragments below belong in an experiment configuration. Prepare the library first and choose an inner
agent compatible with the selected skill kinds. The `...` in the first fragment must be replaced with that
agent's configuration.

### Skill agent { #the-skills-agent }

```yaml
agent:
  type: skills
  params:
    skills: {type: skill_library, params: {path: runs/skills/libero10, frozen: true}}
    kinds: [steering, recovery, plan]              # the default
    inner:
      type: planner.subgoal
      params: {inner: {type: steered, params: {...}}}
```

At the start of each episode the library is matched against the task's instruction, tags and environment. The best
skill of each kind is applied for that episode only:

- a steering skill is merged into the nearest steered agent in the wrapped chain;
- a recovery skill's rules are appended to that agent's rules (at most four rules in total);
- a plan skill's templates are filled with the trigger's slots and given to the nearest subgoal agent; a plan with
  a missing slot is not applied.

Everything is undone at the end of the episode. Each application is a `skill.applied` event, and the episode ends
with a summary of the skills used and the outcome, so results can be attributed to the skill.

The agent spec names the library by digest, for example
`library(<digest>,verified=1,kinds=steering,recovery,plan)`.

### Program skills

```yaml
agent:
  type: code.llm
  params:
    model: {backend: ollama, model: qwen3.5:35b-a3b, vision: true}
    skills: runs/skills/manip        # a path opens the library frozen
    max_skills: 3
    min_skill_similarity: 0.2
```

The most similar verified program skills are offered to the model as functions, `skills.<name>(robot, **kw)`, with
their descriptions and preconditions. Before a skill is offered, its program is read back, its digest compared with
the one in the skill, and its source checked by the sandbox; a skill that fails is skipped and reported. See
[Program skills](../research-and-skills.md#reuse-a-promoted-program).

### Recipe skills

In a role campaign, a solved development task becomes a recipe keyed by the reason codes its goal failed with at
the start. When a later task fails for the same reasons, the matching recipes, with their steps, are offered to the
worker on its retry. Held-out tasks run last with the library frozen. See
[Worlds](../worlds.md#tasks-with-roles).

### Model export { #for-a-language-model }

`SkillLibrary.export_skill_md(dir)` writes one `SKILL.md` per verified skill (name and description as front matter,
trigger, body and evidence below), so a model can scan the index and read a skill only when it needs it. Proposers
get an index of all skills with their status but without gate numbers: a proposer that saw effect sizes could fit
itself to the gate split.

## Constraints { #limits }

- `hylo skills` recognises the steering path of a remote agent (`agent.params.params.steering`); campaigns that
  steer a local agent need the conversion functions called from a script, as the memory example does.
- Weights skills are not applied per episode; reloading a policy is a configuration change for a campaign.
- Matching instructions to programs uses word overlap, not embeddings.

<span id="what-it-achieved"></span>

## Next

- [Program skills](../research-and-skills.md): develop a program and reuse it through the library.
- [Memory reference](../../reference/memory.md#skill-library): kinds, matching and status.
- [Recorded results](../../developer-guide/validation/guide-results.md#skill-library): measurements and reproduction commands.
