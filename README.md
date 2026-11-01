# hylo-docs

The Hylo documentation site: user guide, benchmarking, developer guide, design and RFCs, research notes and
experiment records, API and CLI reference. Built with MkDocs Material, the way vLLM builds its docs.

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

Generated pages need the code repositories checked out next to this one; without them the build still succeeds and
those pages say what is missing.
