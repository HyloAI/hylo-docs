# Contracts

Every plugin group's contract lives in hylo-core, so a plugin depends on hylo-core alone. What a plugin must provide, and the data that passes between the kernel, environments and agents. The
[plugin system](../harness/plugin-system.md) explains how plugins are registered; the
[interfaces](../harness/interfaces/environment.md) explain the design behind each contract; the
[plugin catalogue](../developer-guide/plugin-catalogue.md) lists what implements them.

## Environments

::: hylo.core.env
    options:
      heading_level: 3
      show_if_no_docstring: true

## Agents

::: hylo.core.agent
    options:
      heading_level: 3
      show_if_no_docstring: true

## Policies

::: hylo.core.policy
    options:
      heading_level: 3
      show_if_no_docstring: true

## Reasoners, choosers, planners, reflectors

::: hylo.core.reasoning
    options:
      heading_level: 3
      show_if_no_docstring: true

## Shared data types

::: hylo.core.types
    options:
      heading_level: 3
      show_if_no_docstring: true

## Tasks

::: hylo.core.task
    options:
      heading_level: 3
      show_if_no_docstring: true

## Instruments

::: hylo.core.instrument
    options:
      heading_level: 3
      show_if_no_docstring: true

## Learners

::: hylo.core.learning
    options:
      heading_level: 3
      show_if_no_docstring: true

## Benchmarks

::: hylo.core.benchmark
    options:
      heading_level: 3
      show_if_no_docstring: true

## Scorers and gate tests

::: hylo.core.scoring
    options:
      heading_level: 3
      show_if_no_docstring: true

## Generators and campaign records

::: hylo.core.improvement
    options:
      heading_level: 3
      show_if_no_docstring: true

## Safety

::: hylo.core.safety
    options:
      heading_level: 3
      show_if_no_docstring: true
