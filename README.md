# hylo-docs

Documentation for [Hylo](https://hyloai.github.io/), the stack for physical AI: user guide, benchmarking, developer
guide, design and RFCs, research notes and experiment records, API and CLI reference. Built with MkDocs Material.

```bash
# from the development workspace (the repositories side by side; hylo-harness: dev/bootstrap.sh)
uv sync --group docs
uv run mkdocs serve -f docs/mkdocs.yml          # http://127.0.0.1:8000, reloads on edits
uv run mkdocs build -f docs/mkdocs.yml --strict # what CI would run; output in docs/site/
```

| Path | What |
|---|---|
| `docs/` | the pages (Markdown) and `assets/` (diagrams, figures, stylesheet) |
| `mkdocs.yml` | site configuration and navigation |
| `mkdocs/gen_pages.py` | pages generated at build time from the code repositories: harness reference docs, CLI reference, plugin catalogue, examples, formats |
| `mkdocs/figures/` | scripts that regenerate the figures from recorded runs |
| `references/` | third-party sources studied in the research notes (read-only, gitignored; `MANIFEST.md` records URL, commit and licence) |

**Public site:** https://hyloai.github.io/hylo-docs/ (product docs only: no research notes, strategy summary, RFCs
or internal design documents; see `mkdocs.public.yml`). To publish it again, from this directory in the workspace:

```bash
uv run mkdocs gh-deploy -f mkdocs.public.yml --force --no-history
```

Generated pages need the code repositories checked out next to this one; without them the build still succeeds and
those pages say what is missing.

## License

Apache License 2.0 (see [LICENSE](LICENSE)). Copyright 2026 Hylo AI.
