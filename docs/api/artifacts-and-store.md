# Artifacts and store

Everything the system learns is a sealed, digest-pinned artifact with provenance
([RFC-0004](../rfcs/RFC-0004-learning-pipeline.md)); runs and artifacts have store ids that configs reference
instead of paths ([RFC-0005 part 2](../rfcs/RFC-0005-architecture-measurement-and-placement.md)). Scorecards and
active versions are the formats bench and serve exchange. User guides: [learning](../user-guide/learning.md),
[the store](../user-guide/store.md), [benchmarking](../benchmarking/index.md),
[deployment](../user-guide/deployment.md).

## Artifacts and the split guard

::: worldcurrent.core.artifact
    options:
      heading_level: 3
      show_if_no_docstring: true

## Store

::: worldcurrent.core.store
    options:
      heading_level: 3
      show_if_no_docstring: true
      members: [Store, Entry, Index, Location, StoreError, is_ref, has_refs, resolve_refs, default_root, adopt, sync, plan_sync, STORE_SCHEMA]

## Scorecards

::: worldcurrent.core.scorecard
    options:
      heading_level: 3
      show_if_no_docstring: true

## Active versions

::: worldcurrent.core.deployment
    options:
      heading_level: 3
      show_if_no_docstring: true
