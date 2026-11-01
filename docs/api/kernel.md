# Kernel

`EpisodeRunner` is the one episode loop; evaluation, Studio's live sandbox and the workcell all use it. It runs an
environment and an agent through the safety shield, in sync or realtime
[timing](../user-guide/experiments.md#timing-sync-and-realtime). Events go to an `EventBus`; a `TraceStore` writes them
to the run's trace. See also the [execution lifecycle](../harness/execution-lifecycle.md).

## Episode loop

::: hylo.core.kernel
    options:
      heading_level: 3
      show_if_no_docstring: true

## Events

::: hylo.core.events
    options:
      heading_level: 3
      show_if_no_docstring: true

## Traces

::: hylo.core.trace
    options:
      heading_level: 3
      show_if_no_docstring: true
