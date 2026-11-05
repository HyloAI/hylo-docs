# Configuration

What an experiment measures, where its components run on one machine, and how plugins are found. For the YAML side,
see the [experiment config schema](../harness/experiment-schema.md) and [execution profiles](../configuration/profiles.md);
for how plugins are found, see the [plugin system](../harness/plugin-system.md).

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

## Plugin metadata { #contract-versions-and-plugin-metadata }

::: hylo.core.plugins
    options:
      heading_level: 3
      show_if_no_docstring: true

## Plugin registry

::: hylo.core.registry
    options:
      heading_level: 3
      show_if_no_docstring: true
