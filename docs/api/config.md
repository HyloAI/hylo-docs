# Configuration

What an experiment measures, where its components run on one machine, and how plugins are found. The
[experiment config schema](../harness/experiment-schema.md) documents the YAML format;
[execution profiles](../configuration/profiles.md) and the [plugin catalogue](../developer-guide/plugin-catalogue.md)
the other two from the user's side.

## Experiment configs

::: hylo.core.config
    options:
      heading_level: 3
      show_if_no_docstring: true

## Execution profiles

::: hylo.core.profile
    options:
      heading_level: 3
      show_if_no_docstring: true
      filters: ["!^_", "!^main$"]

## Contract versions and plugin metadata

::: hylo.core.plugins
    options:
      heading_level: 3
      show_if_no_docstring: true

## Plugin registry

::: hylo.core.registry
    options:
      heading_level: 3
      show_if_no_docstring: true
