# RFC-0003: Experience Memory and Skills

- Status: Draft
- Date: 2026-10-30
- Builds on: RFC-0001 (contracts, layering), RFC-0002 (physical RSI protocol), `design/interfaces/memory.md`
- Evidence: `research/projects/memory-experience.md`, `research/projects/memory-landscape.md`

## 1. Goal

Let a frozen-VLA agent improve from its own experience at three levels, through one set of contracts:

| Layer | Stores | Read by | Grain | Written by |
|---|---|---|---|---|
| **Action memory** | verified (observation key -> action chunk) segments | the policy sampler (prior-initialised flow sampling) | every chunk | a builder over development traces |
| **Lessons** | language strategies and pitfalls, with helpful / harmful counters and evidence | planner, LLM proposer | every episode / cycle | an LLM reflector + deterministic curator |
| **Skills** | verified, versioned procedures for a task family (plans, steering, recovery, later learned primitives) | skill selector at reset; planner | every episode | promotion through the RSI gate only |

Non-goals for v0.1: executable code skills (RFC-0001 D5 still pending), 3D spatial memory for manipulation, training
memory modules inside the policy (OnEvoMemory-style cross-attention).

## 2. Principles

1. **Only verified experience is written** (Retrieve-then-Steer: unverified memory is worse than none). Verification =
   simulator success now; a calibrated VLM judge later (`judge` field records which).
2. **Memories are artifacts, not state.** A memory/lesson/skill set used in an evaluation is a frozen snapshot with
   a content digest recorded in the run manifest and the agent spec, so paired, parallel evaluation stays
   reproducible. Online writing is a separate deployment mode that declares its order dependence.
3. **Development data only.** Builders read `search` / `search_val` episodes; gate and held-out episodes never enter
   any memory that is then gated on them (same rule as the critic and self-training).
4. **Declarative bodies.** Skills are data (plan templates, steering configs, rule sets, weight references); no
   generated code runs.
5. **Every read and write is a trace event** (`memory.retrieval`, `memory.write`, `lesson.used`, `skill.applied`),
   so outcomes can be attributed to the memory that influenced them.

## 3. Module map

```
wc-core        core/experience.py      contracts + protocols (no implementation)
                 ActionSegment, ActionMemory, Lesson, LessonBook, Skill, SkillLibrary, PriorSampler
wc-memory      memory/action_bank.py   numpy cosine bank, FIFO cap, npz snapshot + digest
               memory/lessons.py       lesson book over MemoryStore (SEMANTIC items): ADD/UPVOTE/DOWNVOTE/EDIT/RETIRE
               memory/skills.py        directory library (JSON + digest), lifecycle, trigger matching, SKILL.md export
wc-agents      agents/memory_steer.py  retrieval -> DTW filter -> elite prior -> confidence -> t0 (policy-agnostic)
               agents/skills.py        SkillAgent: pick a verified skill at reset, apply its body to the inner agent
               agents/planner.py       (existing) planner gets retrieved lessons + plan skills via a provider
wc-policy-*    lerobot/prior_sampler.py  PriorSampler: flow integration from x_t0 = (1-t0) prior + t0 eps
wc-reasoner-llm llm/reflector.py       LLM extracts lessons from traces (contrastive same-state pairs)
wc-evolve      evolve/experience.py    builders + proposers: ActionMemoryProposer (L1), LessonCurator (per cycle),
                                        SkillPromoter (on promotion), skill/lesson counters from gate verdicts
```

Layering is unchanged: core defines contracts; memory implements stores; agents consume through protocols; policy
adapters implement `PriorSampler`; evolve and reasoner-llm write. New plugin groups are not needed: stores are
`memory` plugins, writers are `generators`.

## 4. Contracts (wc-core, sketch)

```python
class ActionSegment(Contract):        # one verified decision point
    key: NDArray                      # normalised retrieval key (pooled visual features or thumbnails + proprio)
    actions: NDArray                  # (T, A) executed chunk, unnormalised
    task_id: str; step: int; progress: float          # progress in [0, 1] before success
    source: EpisodeRef                # run_id, episode_id, split, judge

class ActionMemory(Protocol):
    def add(self, segs: Sequence[ActionSegment]) -> int: ...
    def query(self, key: np.ndarray, task_id: str | None, k: int) -> list[tuple[ActionSegment, float]]: ...
    def snapshot(self) -> str: ...                      # content digest; frozen banks refuse add()

class Lesson(Contract):
    id: str; scope: str               # "task:<id>" | "family:<tag>" | "global"
    kind: Literal["strategy", "pitfall"]
    title: str; content: str          # ReasoningBank {title, description, content}
    helpful: int = 0; harmful: int = 0
    evidence: list[EpisodeRef]; status: Literal["active", "retired"] = "active"

class Skill(Contract):
    name: str; version: str; description: str          # name + description = the progressive-disclosure index
    applies_to: SkillTrigger          # instruction pattern / task tags / env name
    body: PlanSkill | SteeringSkill | RecoverySkill | WeightsSkill
    status: Literal["proposed", "verified", "refuted", "deprecated"]
    verdicts: dict[str, int]          # useful / misleading / not_applicable (usage feedback)
    evidence: SkillEvidence           # gate stats, archive entry, digest of the source candidate

class PriorSampler(ChunkSampler, Protocol):            # extends the steering sampler
    def sample(self, obs, seeds, noise_scale, prior: np.ndarray | None = None, t0: float = 1.0) -> np.ndarray: ...
```

Skill bodies v0.1: `PlanSkill` (subgoal template with slots from the instruction), `SteeringSkill` (a SteeringConfig
patch), `RecoverySkill` (trigger rules), `WeightsSkill` (a policy or adapter reference, e.g. from L4 self-training).

## 5. Runtime composition

```
SkillAgent                     reset: match verified skills to the task; apply SteeringSkill / RecoverySkill to the
  SubgoalAgent                        inner config, hand PlanSkill + lessons to the planner  -> skill.applied
    MemorySteeredAgent         every chunk: key -> top-K -> DTW filter -> elite prior -> t0   -> memory.retrieval
      PriorSampler (LeRobot)   flow sampling from x_t0; t0 = 1 means the unchanged policy
```

All layers are optional and configured as data, e.g.

```yaml
agent:
  type: remote
  params:
    ref: worldcurrent.policies.lerobot.experience_agent:make_experience_agent
    params:
      repo_id: lerobot/smolvla_libero
      steering: {n_samples: 1, execution_steps: 25}
      action_memory: {path: runs/memory/l10-v1, digest: 9f..., k: 10, sim_floor: 0.9, t0: {min: 0.3, max: 1.0}}
      skills: {path: runs/skills/l10, digest: 1a...}
      lessons: {path: runs/lessons/l10.sqlite, digest: 7c..., top_k: 5}
```

Composition with existing steering: a prior replaces pure noise for the first sample; `n_samples > 1` draws the rest
from noise, and the chunk critic / gripper vote picks among them, so memory, critic and voting stack.

## 6. Integration with RSI (RFC-0002)

| When | Component | What happens |
|---|---|---|
| after a cycle's search runs | `ActionMemoryProposer` (unit L1) | build a bank from verified development segments; propose `agent...action_memory` as a candidate; gated like any patch |
| after each cycle | `LessonCurator` | LLM reflector reads failure diagnoses and same-state success/failure pairs (CRN makes these plentiful); curator applies delta ops; counters move with gate verdicts of candidates that cited a lesson |
| on promotion | `SkillPromoter` | the promoted patch becomes a `verified` skill for the task family it was gated on, with the gate statistics as evidence; refuted candidates become `refuted` skills so they are not re-proposed |
| proposal time | LLM steering proposer | receives top lessons and relevant skills in its prompt, so cycles accumulate knowledge instead of re-diagnosing from scratch |

The gate still decides everything that changes behaviour; memory only changes *what gets proposed* and *what the
agent conditions on*, never the acceptance rule.

## 7. Evaluation plan

1. **Action memory, LIBERO-10**: bank from `search` successes, evaluate on `search_val` (unseen init states), paired
   with CRN against the same agent without memory; then a gated campaign. Ablations: replay vs prior-init, fixed vs
   confidence t0, success-prefix vs whole episode, bank size.
2. **Lessons**: campaigns with and without the lesson book on the same budget; metric = cycles / episodes until the
   first promotion and promoted effect size.
3. **Skills**: transfer within task families (e.g. "put both X and Y in the basket" scenes): a skill verified on one
   scene, evaluated on its siblings.
4. **Judge readiness**: precision / recall of a VLM success judge against BDDL ground truth before any memory is
   written without simulator labels.

## 8. Plan

| Step | Content | Depends on |
|---|---|---|
| M1 | core contracts; ActionBank; PriorSampler for SmolVLA; MemorySteeredAgent; builder; unit tests | - |
| M2 | LIBERO-10 action-memory A/B on search_val; ActionMemoryProposer | M1 |
| M3 | SkillLibrary + SkillAgent + SkillPromoter (from existing archive/registry) | M1 contracts |
| M4 | LessonBook + LLM reflector + curator; proposer and planner read lessons | M3 |
| M5 | VLM success judge, calibrated on LIBERO ground truth; online-memory deployment mode | M2 |

## 9. Open questions

1. Retrieval key: SmolVLA's own visual tokens (paper choice, needs a forward pass we already do) vs cheap thumbnails.
2. Skill granularity: per task, per scene, or per instruction pattern; how to infer families without hand tags.
3. Whether learned primitives (adapters from L4 self-training) count as skills or as policies.
