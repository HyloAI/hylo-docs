# Research

We study the source code and architecture of existing open-source Physical AI projects, and use it to design our own Physical AI Stack. The [executive summary](../EXECUTIVE-SUMMARY.md) records the original design snapshot; start with [Concepts](../getting-started/concepts.md) for the current product framing.

Source-level reports on the open-source projects Hylo learns from, cross-project comparisons, and dated
experiment records. Third-party sources are cloned read-only under `references/` at the root of this repository
(gitignored; `references/MANIFEST.md` records URL, commit and licence).

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
