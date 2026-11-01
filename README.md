# worldcurrent docs (Physical AI research workspace)

Study the source code and architecture of existing open-source Physical AI projects, and use it to design our own Physical AI Stack. **Read [`EXECUTIVE-SUMMARY.md`](EXECUTIVE-SUMMARY.md) first.**

## Layout

This is worldcurrent-docs: documentation that spans the code repositories. Reference documentation for a
repository's own packages lives in that repository's `docs/` (the harness: extending, package layering, interfaces,
plugin system, experiment schema).

```text
docs/
├── EXECUTIVE-SUMMARY.md        Conclusions: architecture, reference projects, reuse, build in-house, starting point, MVP
├── design/                     Our architecture
│   ├── architecture.md  repository-structure.md  mvp-v0.1.md  roadmap.md
│   └── roadmap/v0.1-plan.md
├── rfcs/                       RFC-0001 core decisions · RFC-0002 physical RSI · RFC-0003 experience memory · RFC-0004 learning
├── research/
│   ├── projects/               One source-level report per project
│   ├── comparisons/            Cross-project comparisons (key one: technology-gap-analysis.md)
│   ├── architecture/           concept-map.md: cross-project concept translation table
│   └── experiments/            Dated experiment records, with the commands and versions used
└── references/                 Third-party source (read-only, gitignored); MANIFEST.md records URL/commit/license
    └── harness/ simulation/ benchmarks/ policies/ reasoning/ memory/ evolution/
```

## Research report index

| Category | Reports |
|---|---|
| Harness | [vla-evaluation-harness](research/projects/vla-evaluation-harness.md) · [inspect-robots](research/projects/inspect-robots.md) · [RPent](research/projects/rpent.md) · [XPolicyLab](research/projects/xpolicylab.md) |
| Simulation / Benchmark | [MuJoCo](research/projects/mujoco.md) · [ManiSkill](research/projects/maniskill.md) · [LIBERO](research/projects/libero.md) · [RoboCasa](research/projects/robocasa.md) |
| Policies | [LeRobot](research/projects/lerobot.md) · [openpi](research/projects/openpi.md) |
| Reasoning | [LangGraph](research/projects/langgraph.md) · [DSPy](research/projects/dspy.md) |
| Memory | [memory-landscape](research/projects/memory-landscape.md) (ReMEmbR, ConceptGraphs, Spark-DSG, ASPIRE, mem0, Graphiti + 27 candidates verified) |
| RSI | [Zetta-Embodiment](research/projects/zetta-embodiment.md) · [agent-lightning](research/projects/agent-lightning.md) |

Comparisons: [harness](research/comparisons/harness-comparison.md) · [simulator](research/comparisons/simulator-comparison.md) · [benchmark](research/comparisons/benchmark-comparison.md) · [agent/policy](research/comparisons/agent-policy-comparison.md) · [memory](research/comparisons/memory-comparison.md) · [rsi](research/comparisons/rsi-comparison.md) · [license](research/comparisons/license-matrix.md) · [**gap analysis**](research/comparisons/technology-gap-analysis.md)

## Rules

1. Third-party code under `references/` is read-only: do not modify it, install it, run its install scripts, or import it from our code. When cloning, do not fetch weights, LFS or submodules, and skip files larger than 2 MB.
2. Ported code must cite the source repo, commit and original license, and be registered in the product repo's `THIRD_PARTY_NOTICES.md`.
3. Copying code from projects marked "Design only" in the [license-matrix](research/comparisons/license-matrix.md) is prohibited.
4. Capability tags in reports: **[Implemented]** traceable code exists · **[Docs/Interface only]** · **[Unverified]** code exists but we have not run it · **[Needs model/hardware]**.

## Rebuilding references

```bash
# Re-clone using the URLs and commits in references/MANIFEST.md:
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 --filter=blob:limit=2m --no-recurse-submodules <url> references/<category>/<name>
git -C references/<category>/<name> fetch --depth 1 origin <sha> && git -C references/<category>/<name> checkout <sha>
```
