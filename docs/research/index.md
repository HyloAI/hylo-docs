# Research

We study the source code and architecture of existing open-source Physical AI projects, and use it to design our own Physical AI Stack. The [executive summary](../EXECUTIVE-SUMMARY.md) records the original design snapshot; start with [Concepts](../user-guide/overview.md) for the current product framing.

Source-level reports on the open-source projects Hylo learns from, cross-project comparisons, and dated
experiment records. Third-party sources are cloned read-only under `references/` at the root of this repository
(gitignored; `references/MANIFEST.md` records URL, commit and licence).

## Current conclusions

| Area | Current conclusion | Evidence and next question |
|---|---|---|
| Agent and simulator boundaries | Plugins meet through core contracts; heavy dependencies use separate runtimes. | [Architecture](../design/overview.md), [harness comparison](comparisons/harness-comparison.md) |
| Memory | Episode-local observation history and persistent experience have different consumers and evaluation rules. | [Design review](experiments/2026-11-03-memory-design-review.md), [method screening](comparisons/memory-method-screening.md); compare matched end-to-end methods before claiming gains |
| SimpleMemVLA | The optional integration has parity and regression evidence; native kernel-to-RoboMME evaluation remains unverified. | [Integration record](experiments/2026-11-04-simplememvla-integration.md); regression episodes are not fresh held-out evidence |
| Phase-guided program repair | The implementation exists, but the recorded real-model probes produced no promoted candidate. | [Program-evolution record](experiments/2026-11-04-harness-program-evolution.md) |
| Working Memory prototype | The model-managed runtime and dedicated prompt gate were withdrawn; event-memory primitives remain. | [RFC-0009](../rfcs/RFC-0009-benchmark-memory.md), [historical evaluation](experiments/2026-11-03-working-memory.md) |
| Improvement on LIBERO | Results depend on the proposed change and evaluation power; earlier studies do not establish general gains. | [RSI cycle](experiments/2026-10-30-libero10-rsi-cycle1.md), [action-memory experiment](experiments/2026-10-30-experience-memory-libero10.md) |

## Experiment records

Records preserve their dates and tested implementations. Read their conditions before comparing numbers.

- [SimpleMemVLA Pilot](experiments/2026-11-04-simplememvla-pilot.md).
- [SimpleMemVLA Integration](experiments/2026-11-04-simplememvla-integration.md).
- [Harness Program Evolution](experiments/2026-11-04-harness-program-evolution.md).
- [Working Memory Evaluation](experiments/2026-11-03-working-memory.md).
- [RoboMME Memory Pilot](experiments/2026-11-03-robomme-memory-pilot.md).
- [Memory Design Review](experiments/2026-11-03-memory-design-review.md).
- [Benchmark Memory Validation](experiments/2026-11-03-benchmark-memory.md).
- [Success judges on LIBERO-10: trained on traces vs zero-shot VLM (2026-10-31)](experiments/2026-10-31-success-judges-libero10.md).
- [RFC-0004 W1-W4: external data, world model, noise-space steering, shadow mode (2026-10-31)](experiments/2026-10-31-rfc0004-w1-w4.md).
- [LIBERO-10 RSI cycle 1 (2026-10-30): frozen SmolVLA, rule proposer](experiments/2026-10-30-libero10-rsi-cycle1.md).
- [Experience memory and chunk critic on LIBERO-10 (2026-10-30)](experiments/2026-10-30-experience-memory-libero10.md).

## Research report index

| Category | Reports |
|---|---|
| Harness | [vla-evaluation-harness](projects/vla-evaluation-harness.md) · [inspect-robots](projects/inspect-robots.md) · [RPent](projects/rpent.md) · [XPolicyLab](projects/xpolicylab.md) |
| Simulation / Benchmark | [MuJoCo](projects/mujoco.md) · [ManiSkill](projects/maniskill.md) · [LIBERO](projects/libero.md) · [RoboCasa](projects/robocasa.md) |
| Policies | [LeRobot](projects/lerobot.md) · [openpi](projects/openpi.md) |
| Reasoning | [LangGraph](projects/langgraph.md) · [DSPy](projects/dspy.md) |
| Memory | [memory-landscape](projects/memory-landscape.md) (ReMEmbR, ConceptGraphs, Spark-DSG, ASPIRE, mem0, Graphiti + 27 candidates verified) |
| RSI | [Zetta-Embodiment](projects/zetta-embodiment.md) · [agent-lightning](projects/agent-lightning.md) |

Comparisons: [harness](comparisons/harness-comparison.md) · [simulator](comparisons/simulator-comparison.md) · [benchmark](comparisons/benchmark-comparison.md) · [agent/policy](comparisons/agent-policy-comparison.md) · [memory](comparisons/memory-comparison.md) · [rsi](comparisons/rsi-comparison.md) · [license](comparisons/license-matrix.md) · [**gap analysis**](comparisons/technology-gap-analysis.md)

## Rules

1. Third-party code under `references/` is read-only: do not modify it, install it, run its install scripts, or import it from our code. When cloning, do not fetch weights, LFS or submodules, and skip files larger than 2 MB.
2. Ported code must cite the source repo, commit and original license, and be registered in the product repo's `THIRD_PARTY_NOTICES.md`.
3. Copying code from projects marked "Design only" in the [license-matrix](comparisons/license-matrix.md) is prohibited.
4. Capability tags in reports: **\[Implemented\]** traceable code exists · **\[Docs/Interface only\]** · **\[Unverified\]** code exists but we have not run it · **\[Needs model/hardware\]**.

## Rebuilding references

```bash
# Re-clone using the URLs and commits in references/MANIFEST.md:
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 --filter=blob:limit=2m --no-recurse-submodules <url> references/<category>/<name>
git -C references/<category>/<name> fetch --depth 1 origin <sha> && git -C references/<category>/<name> checkout <sha>
```
