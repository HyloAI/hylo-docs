# Physical Memory Comparison

> Question answered: how do we plug in swappable short-term (Working), episodic (Episodic), spatial (Spatial) and skill (Skill) memory?
> Sources: `research/projects/memory-landscape.md` (33 candidates checked, 6 cloned and read in depth), `langgraph.md` (Store), `rpent.md`/`zetta-embodiment.md` (memory file merging).

## 1. Cross-review of existing implementations

| Project | Memory type | Storage | Retrieval | Write/update strategy | Spatio-temporal semantics | License |
|---|---|---|---|---|---|---|
| ReMEmbR (NVIDIA) | Episodic (robot patrol captions) | Milvus | Text vectors + position/time **also treated as vectors for L2 nearest neighbor** `milvus_memory.py:37-69` | Batched writes over 3s caption windows | No radius/time window/coordinate frame | **NVIDIA non-commercial**: borrow design only |
| ConceptGraphs | Spatial (open-vocabulary 3D object graph) | In-memory/pickle | CLIP similarity + geometry | Observation association: weighted geometric IoU + semantic similarity, weighted-average features after merging `slam/utils.py:178-222` | 3D point cloud/bbox | MIT |
| Spark-DSG (MIT-SPARK) | Spatial (hierarchical dynamic scene graph) | C++ graph + Python bindings | Graph traversal, hierarchy | `mergeNodes`, `is_active/is_predicted`, change-feed `dynamic_scene_graph.h:389-450` | Hierarchy + observation intervals + trajectories | BSD |
| ASPIRE (NVlabs) | Skill (skill library) | Directory + content hash | Trigger matching | **proposer→verifier→promote**, usage ratings (useful/misleading/wrong/n.a.), sandbox validation `cap_harness/runtime.py:159-200` | — | Apache-2.0 |
| mem0 | Semantic/Episodic text facts | Pluggable vector stores (~28 kinds) + SQLite history | semantic + BM25 + entity boost | **Current OSS only does ADD** (`prompts.py:472`), md5 deduplication | None | Apache-2.0 |
| Graphiti (Zep) | Temporal knowledge graph | Graph database | Hybrid retrieval + graph | **Bi-temporal**: valid_at/invalid_at + created_at/expired_at; new facts invalidate old facts rather than deleting them `edge_operations.py:748-782` | Strong temporal, no spatial | Apache-2.0 |
| LangGraph Store | KV + optional vectors | Postgres/SQLite | namespace + simple comparison filters + text embedding | Defined by the application | None | MIT |
| RPent / Zetta | Task notes / parameter blocks | Markdown files | Injected into prompt | Evidence counting promotes confidence `memory/manager.py:99-122` | None | Apache-2.0 |

## 2. Key conclusions

1. **No single project covers all four memory types**; moreover, the most mature general-purpose memory libraries (mem0, Graphiti, LangGraph Store) **have no spatial semantics**. The core difficulties of physical memory — coordinate frames, pose correction, object identity association, joint spatio-temporal queries like "where did I last see it" — must be defined by us.
2. **Time and pose must be first-class fields** (not embeddings): `event_time: TimeSpan`, `pose: Pose(frame_id, ...)`, with dedicated indexes (interval tree, KD/R-tree). ReMEmbR's approach is a counterexample.
3. **Physical world state changes** → Episodic/Semantic adopt a Graphiti-style bi-temporal model that invalidates rather than deletes (`valid_from/valid_to` + `recorded_at/expired_at`), supporting `as_of` queries.
4. **Spatial memory is a graph**: adopt Spark-DSG's hierarchical schema (OBJECTS/PLACES/ROOMS/AGENTS), using ConceptGraphs' association/fusion rules on write. The MVP only needs a simplified Python implementation (object nodes + observation intervals + radius queries).
5. **Writes to skill memory must pass through a validation gate**, which is exactly where the Memory and Evolution layers meet: skill candidate (from RSI) → independent validation (from the Benchmark layer) → promotion to `verified`. Skills are versioned artifacts; each run records the content hash of the skill library.
6. **Retrieval results must be structured and enter the Trace**: `Hit(item, score, score_details)`; each Agent retrieval is written to the Trace as a `RetrievalRecord`, so RSI can diagnose "whether the failure was caused by misleading memory" (the prerequisite for ASPIRE's `misleading` rating).

## 3. Unified interface (summary; full definition in `design/interfaces/memory.md`)

```python
class MemoryStore(Protocol):
    kind: MemoryKind                     # working | episodic | semantic | spatial | skill
    def write(self, items: Sequence[MemoryItem]) -> WriteResult      # ADD/UPDATE/MERGE/INVALIDATE/SKIP_DUP
    def query(self, q: MemoryQuery) -> list[Hit]                     # text/embedding/time_range/as_of/near/object_ids/relation
    def consolidate(self, *, scope=None, budget=None) -> ConsolidationReport
    def forget(self, selector: MemoryQuery, *, mode="expire") -> int
    def snapshot(self) -> str                                        # content-hash version, written into the run manifest
```

`MemorySystem` is the routing/fusion layer over multiple `MemoryStore`s (dispatches queries by kind, RRF fusion) and is held by the Agent; the Kernel is only responsible for calling `on_episode_end()` at episode boundaries to trigger the working→episodic flush and consolidation.

## 4. Backend selection

| Subtype | MVP backend | Production candidates |
|---|---|---|
| Working | In-process ring buffer (bounded) | Same |
| Episodic | **SQLite + local vectors (numpy brute force/FAISS optional)** | mem0 vector layer / Graphiti (fact layer) / pgvector |
| Spatial | Python object graph + KD-tree radius queries | Spark-DSG (PyPI `spark-dsg`, BSD) |
| Skill | Directory + JSON metadata + content hash + state machine | Same + sandboxed execution (subprocess/container) |

## 5. Reusable / borrow design only

- Usable as a dependency or rewritten: Spark-DSG (BSD), ConceptGraphs (MIT), ASPIRE (Apache-2.0), mem0 (Apache-2.0), Graphiti (Apache-2.0).
- **Borrow design only, do not copy code**: ReMEmbR, RAVEN (NVIDIA non-commercial); MemoryVLA, PRISM (no license).
- Code risks (not run, static observation): ReMEmbR uses `eval()` to parse LLM output and retries infinitely on errors; mem0's ADD-only approach leads to conflicting facts coexisting.
