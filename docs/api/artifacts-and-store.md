# Artifacts and store

What Hylo learns is saved as an artifact: a directory with a content digest and a record of what it was built from,
sealed unless marked mutable. Configs can refer to runs and artifacts by store id instead of path. Scorecards and
active versions are the formats bench and serve exchange. User guides: [learning](../user-guide/learning.md),
[the store](../user-guide/store.md), [benchmarking](../benchmarking/index.md),
[deployment](../user-guide/deployment.md).

## Artifacts { #artifacts-and-the-split-guard }

::: hylo.core.artifact
    options:
      heading_level: 3
      show_if_no_docstring: true

## Store

::: hylo.core.store
    options:
      heading_level: 3
      show_if_no_docstring: true
      members: [Store, Entry, Index, Location, StoreError, is_ref, has_refs, resolve_refs, default_root, adopt, sync, plan_sync, STORE_SCHEMA]

## Scorecards

::: hylo.core.scorecard
    options:
      heading_level: 3
      show_if_no_docstring: true

## Active versions

::: hylo.core.deployment
    options:
      heading_level: 3
      show_if_no_docstring: true
