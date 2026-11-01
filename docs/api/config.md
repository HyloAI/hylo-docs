# Configuration

What an experiment measures, where its components run on one machine, and how plugins are found. The
[experiment config schema](../harness/experiment-schema.md) documents the YAML format;
[execution profiles](../configuration/profiles.md) and the [plugin catalogue](../developer-guide/plugin-catalogue.md)
the other two from the user's side.

## Experiment configs

::: worldcurrent.core.config
    options:
      heading_level: 3
      show_if_no_docstring: true

## Execution profiles

::: worldcurrent.core.profile
    options:
      heading_level: 3
      show_if_no_docstring: true
      filters: ["!^_", "!^main$"]

## Contract versions and plugin metadata

::: worldcurrent.core.plugins
    options:
      heading_level: 3
      show_if_no_docstring: true

## Plugin registry

::: worldcurrent.core.registry
    options:
      heading_level: 3
      show_if_no_docstring: true
