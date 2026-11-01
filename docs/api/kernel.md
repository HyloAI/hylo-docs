# Kernel

The one episode loop and what it records. `EpisodeRunner` runs an environment and an agent through the
SafetyShield, in sync mode (the world waits for the policy) or realtime mode (the world keeps moving while the
policy computes the next chunk); evaluation, the playground's live sandbox and the workcell all use it
([RFC-0005 part 3](../rfcs/RFC-0005-architecture-measurement-and-placement.md)). Every event goes to an
`EventBus` and, through a `TraceStore`, to the run's trace. See also the
[execution lifecycle](../harness/execution-lifecycle.md).

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
