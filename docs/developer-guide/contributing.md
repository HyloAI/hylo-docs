# Contributing

The rules for changing code in the Hylo repositories, and how to commit. [Architecture](../design/overview.md) shows
how the repositories fit together.

## Workspace { #the-development-workspace }

Follow [installation](../getting-started/installation.md): it checks the repositories out side by side and installs
every package editable into one venv. After you add or remove a package, regenerate the workspace file from the
workspace directory (the script needs Python 3.11 or later):

```bash
uv run --no-project --python '>=3.11' python harness/dev/workspace.py .
uv sync
```

The boundary lint fails while the workspace file is stale.

## Repository rules { #repository-and-package-rules }

`harness/dev/repos.toml` lists the repositories and what each may depend on. `harness/dev/test_boundaries.py`
enforces these rules:

1. **Package layering.** Every `hylo.*` import in a package's `src/`, and every `module:attr` or `-m module` string,
   targets a package allowed for it in the lint's `ALLOWED` map ([package layering](../harness/dependency-graph.md)).
   Heavy libraries (torch, jax, mujoco, ...) are imported only in the adapter that wraps them.
2. **Repositories.** A package imports or declares only packages of its own repository and of the repositories it
   depends on. The leaves (bench, serve, studio, plugins) depend on the harness and never on each other. The harness
   depends on no leaf.
3. **Robot side.** serve's packages declare no Hylo dependency except `hylo-core`, so a robot computer needs no
   other Hylo package.
4. **No `../<repo>/` paths.** Code and configs never point into a sibling repository. Shell scripts that need a
   sibling checkout read it from an environment variable such as `HYLO_HARNESS`.
5. **The workspace file is current.**

## Add a package { #adding-a-package }

1. Create it under `packages/`, or under `adapters/` if it wraps a third-party stack, in the right repository. Give
   it a `pyproject.toml` (hatchling, `src/` layout, a `license`), `src/` and `tests/`.
2. Register its plugins under the `hylo.<group>` entry-point groups. Declare their contract versions and maturity
   under `hylo.meta` ([plugin system](../harness/plugin-system.md), [plugin catalogue](plugin-catalogue.md)).
3. Add its module prefix to `OWNER` and its allowed dependencies to `ALLOWED` in `harness/dev/test_boundaries.py`.
4. Regenerate the workspace file (above) and run `uv sync`.
5. Write its tests as described in [testing](testing.md#tests-for-a-new-package), and run them.

A plugin outside the Hylo repositories is a package of its own. `uv run hylo plugin new <group> <name>` scaffolds
one that passes its conformance check as generated ([extending](../harness/extending.md)).

## Commits

- Run the tests and the boundary lint ([testing](testing.md)). Both must pass.
- One logical change per commit, in the repository it belongs to.
- State what changed in the summary line. In the body, say why, and which tests or real runs you checked.
- When you copy third-party code, record its source URL, commit and licence next to the copied code.
- Discuss a change to a contract, a format or what an experiment measures with the maintainers before you write it.
  Bump the format's version when the change is not backward compatible ([versioning](versioning.md)).

## Documentation

Docs live in hylo-docs; its README says how to build them. A repository's own reference docs live in its `docs/`
directory. The harness's are rendered on this site under Developer Guide.
