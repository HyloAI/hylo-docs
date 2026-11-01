# Docs

This site is built with MkDocs and the Material theme from hylo-docs, in the
[development workspace](contributing.md#the-development-workspace), so that it can generate pages from the code
repositories next to it.

## Building

```bash
uv sync --group docs                                # mkdocs-material, mkdocstrings, mkdocs-gen-files, glightbox
uv run mkdocs serve -f docs/mkdocs.yml              # http://127.0.0.1:8000, rebuilt on change
uv run mkdocs build -f docs/mkdocs.yml --strict     # site/ in the docs repository; any warning fails the build
```

Run them from the workspace directory. The `docs` dependency group is part of the workspace file that
`harness/dev/workspace.py` writes. MkDocs prints notices about its own future and the theme's; set
`NO_MKDOCS_2_WARNING=1 DISABLE_MKDOCS_2_WARNING=true` to silence them.

Always build with `--strict` before committing: broken links, missing images and API references that do not
resolve are errors.

## Layout

```text
docs/                              hylo-docs
├── mkdocs.yml                     site config and navigation
├── mkdocs/gen_pages.py            pages generated at build time
├── docs/                          the content
│   ├── index.md
│   ├── getting-started/  user-guide/  configuration/  benchmarking/  developer-guide/
│   ├── design/  rfcs/  research/  api/
│   └── assets/                    logo, stylesheets, diagrams/ (SVG), figures/ (PNG)
└── references/                    third-party sources, read-only, gitignored (not part of the site)
```

The navigation is explicit in `mkdocs.yml`: a new page appears only once it is listed there.

## Generated pages

`mkdocs/gen_pages.py` writes these at build time; edit the source, not the page:

| Page | Generated from |
|---|---|
| Developer Guide > Extending, Interfaces, Internals; the experiment config schema | `harness/docs/` (copied as `harness/...`) |
| [CLI Reference](../cli/index.md) | `hylo --help` and every subcommand's `--help`, from the installed packages |
| [Plugin catalogue](plugin-catalogue.md) | `hylo.core.plugins.catalogue()`: every installed plugin's contract, maturity, licence |
| [Examples](../getting-started/examples.md) | `bench/examples/{configs,evolve}`, `plugins/examples/{configs,evolve}`: each config with its header comment |
| [Formats and schemas](../api/formats.md) | the format table, and the JSON Schemas `hylo schema` prints |

The [API Reference](../api/index.md) pages are written by hand but filled by mkdocstrings from the harness's
docstrings (`::: hylo.core.policy`). A repository that is not checked out gives a page that says so instead
of failing the build.

## Images

- `docs/assets/diagrams/*.svg`: architecture and flow diagrams, drawn by hand on a white background.
- `docs/assets/figures/*.png`: charts and screenshots made from recorded runs and the running system.
- Reference them with the `hylo-figure` class, which gives them a light card in dark mode, and an italic caption:

```markdown
![The improvement loop](../assets/diagrams/improvement-loop.svg){ .hylo-figure }

*One campaign cycle: diagnose, propose, screen, gate, approve.*
```

Small flows that change often can be Mermaid diagrams in a `mermaid` code block instead.

## Style

- English; British spelling (licence, behaviour).
- Short sentences, plain words, no marketing. Say what something does and what it does not do yet.
- Task-oriented pages: a short introduction, then sections with runnable `uv run hylo ...` commands, tables for
  options, admonitions only where they help.
- Every option, default, path and number must come from the code or from a recorded result, and say which.
- Link with relative paths to other pages (`../user-guide/store.md`); the strict build checks them.
