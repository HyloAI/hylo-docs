# Docs

How to build this site and how to write its pages. The reader is whoever maintains hylo-docs.

## Building

From the development workspace (the repositories side by side, see
[installation](../getting-started/installation.md)):

```bash
uv sync --group docs
uv run mkdocs serve -f docs/mkdocs.yml                    # http://127.0.0.1:8000, rebuilt on change
uv run mkdocs build -f docs/mkdocs.yml --strict           # the full site; any warning fails the build
uv run mkdocs build -f docs/mkdocs.public.yml --strict    # the public site
```

Build with `--strict` before every commit: broken links, missing images and API references that do not resolve are
errors. The hylo-docs README says how to publish the public site.

A repository that is not checked out does not fail the build. Each page generated from it shows a "Not built"
warning instead, and `--strict` still passes. Before publishing, check for placeholders and broken built links, including raw HTML resources and fragments:

```bash
uv run python docs/mkdocs/check_site.py docs/site
uv run python docs/mkdocs/check_site.py docs/site-public --url-prefix /hylo-docs/
```

## Generated pages

`mkdocs.yml` owns the shared navigation. `mkdocs.public.yml` inherits it; the public hook removes Internal and
excluded entries. Add a page to that shared navigation once. Generated module, command-family and workflow
pages are reached through their indexes and listed under `not_in_nav` so they do not overwhelm the sidebar.

| Page | Source | Edit |
|---|---|---|
| User Guide, Benchmarking, Configuration, most of Developer Guide | `docs/` in hylo-docs | the Markdown file |
| Developers > Plugin development/Internals; Reference > Interfaces and experiment schema | `harness/docs/`, copied at build time | the file in hylo-harness |
| [CLI Reference](../cli/index.md) | every `hylo` subcommand's `--help` | the argparse help in the code |
| [Plugin catalogue](plugin-catalogue.md) | every installed plugin's contract, maturity and licence | the package's `hylo.meta` declaration |
| [Examples](../getting-started/examples.md) | the header comment of each config in `bench/examples/` and `plugins/examples/` | the config file |
| [Formats and schemas](../api/formats.md) | the format table and `hylo schema` | the code |
| API Reference: the core pages | a short hand-written intro in `docs/api/`, then the docstrings | the intro here, the rest in the code |
| API package indexes and module pages | the docstrings of every package | the code |
| Examples and results | curated case pages plus generated example README records | the case page or source README |

`mkdocs/gen_pages.py` writes the generated pages. API pages are short hand-written intros; mkdocstrings fills them
from the code's docstrings, which therefore appear on the public site verbatim. Docstrings follow the same writing
rules as pages.

## Public and internal site

`mkdocs.yml` builds everything. `mkdocs.public.yml` builds the public site: it leaves out `rfcs/`, `research/`, the
strategy summary, `internal/`, and `design/` except `design/overview.md`.

The public hook (`mkdocs/public_hook.py`) turns links to the left-out pages into plain text. It does not remove the
words around them. "See RFC-0005" stays on the public page, pointing at nothing. So user pages never cite RFCs,
research notes or internal design pages, linked or not.

## Images

- `docs/assets/diagrams/<name>-{light,dark}.svg`: architecture and flow diagrams, each in a light and a dark
  version, in the same style as the README figures. Edit `mkdocs/figures/diagrams.py`, not the SVGs, and regenerate
  them from the workspace with
  `uv run --no-project --with fonttools --with uharfbuzz --with pillow python docs/mkdocs/figures/diagrams.py`.
  Reference both versions; the page shows the one for the current colour scheme:

```markdown
![The improvement loop](../assets/diagrams/improvement-loop-light.svg){ .hylo-diagram .only-light }
![The improvement loop](../assets/diagrams/improvement-loop-dark.svg){ .hylo-diagram .only-dark }

*One campaign cycle: diagnose, propose, screen, gate, approve.*
```

- `docs/assets/figures/*.png`: charts made from recorded runs (`mkdocs/figures/make_figures.py`) and Studio
  screenshots (`mkdocs/figures/screenshots.py`). The public site leaves out the Studio screenshots. Reference them
  with the `hylo-figure` class, which gives them a light card in dark mode.

Small flows that change often can be Mermaid diagrams in a `mermaid` code block instead.

## Style

### The concepts and the guides

The five product concepts are **Physical RSI, Worlds, Agents, Memory and Skills**. Physical RSI connects the
other four. Home introduces that relationship; Concepts defines it; each topic page explains its own capability.
Skills have a separate navigation entry even though the library is implemented in the memory package.

| Content | Responsibility |
|---|---|
| Home | a brief product introduction, the five concepts and starting points |
| Concepts | how the five concepts relate; supporting command/config terms are secondary |
| RSI | the improvement loop, what can change and how outcomes support those changes |
| Worlds | scenes, robots, interactions and goal checks |
| Agents | choosing policies, programs or tool calls |
| Memory | observations and experience, storage, retrieval and data boundaries |
| Skills | reusable task capabilities, applicability, verification and reuse |
| Guides | concrete operations: run, evaluate, learn, improve, deploy and inspect |
| Examples and results | measured results, conditions, reproduction commands and failures |
| Developers | architecture, extension tutorials and contributing |
| Reference | exact CLI, configuration, contracts, formats and module API details |
| Internal | current direction, decisions, research conclusions, experiment records and historical archive |

Get started contains the minimal installation, first run, first improvement and task chooser. Optional runtime
setup lives on its own page. Concepts explains a capability; Guides completes a task; Examples and results owns
the measured evidence. Keep each fact in its primary page and link from the other contexts.

Do not retell the full improvement loop or skill lifecycle at the start of each guide. State the page's task and
link to the relevant concept. Distinguish robot capabilities, concrete library records and coding-agent instructions.
Historical design snapshots belong under the archive, with a link to the current documentation.

### Shared website wording

The website and docs use the same product introduction:

> Agents act in worlds, learn from experience and reuse verified skills. Hylo connects those capabilities through
> a measured improvement loop.

Chinese: 智能体在世界中行动，从经验中学习，并复用已验证的技能。Hylo 通过有实测依据的改进循环，将这些能力连接起来。

| English | Chinese | Scope |
|---|---|---|
| Physical RSI | Physical RSI（物理递归自我改进） | the overall improvement loop |
| Worlds | 世界 | scenes, robots, tasks and physical feedback |
| Agents | 智能体 | policy, program and tool-calling approaches |
| Memory | 记忆 | observations and experience used in later decisions |
| Skills | 技能 | reusable task capabilities with applicability and evidence |
| Campaign | 改进任务（Campaign） | candidate comparison and promotion |
| Gate | 准入评测（gate） | the confirmatory paired test, not every form of verification |
| Program skill / recipe skill | 程序技能 / 动作配方技能 | promoted programs / recipes verified by replay without a model |
| Studio | Studio | the UI; do not rename it Workbench |
| Developing programs / Program research | 开发程序 / 程序研发 | the manual and model-assisted program guides |

Website concept descriptions follow the docs home page. Buttons name their destination: Quickstart, Agents,
Developing programs, Program research, Deployment. Keep the website's English markup, Chinese dictionary and
metadata aligned when changing these terms. Its brand headline can differ from a documentation heading.

State what each verification path proves: campaign candidates pass a gate; recipes pass replay checks. Promotion
and deployment remain separate, and hardware requires target validation. Describe current Serve behaviour in
product copy; keep broader model-serving ambitions in design planning.

### Page order

Operational guides follow this order; concept pages lead with the capability and link to the relevant operations:

1. **Purpose and prerequisites**: the outcome, required model/data/runtime and explicit working directory.
2. **Do**: commands and their expected output, ready to copy.
3. **Explain**: what just happened, and why it works this way.
4. **Options**: the two or three most used; link the rest to the reference.
5. **Limits**: current limits, stated as current behaviour.
6. **Next**: a link to the next page on the spine.

### Nouns

RSI, Worlds, Agents, Memory and Skills are the primary concepts. Introduce these supporting operational terms only where needed:

| Noun | Meaning |
|---|---|
| experiment | a config file: which environment, which agent, which split |
| environment | what the agent observes and acts on: a simulator or a robot |
| agent | the logic that decides actions; may wrap a policy and add memory, guidance or a critic |
| policy | the model or controller that maps an observation to actions |
| run | the record of one execution: the traces of its episodes and the results |
| evaluation protocol | rules that fix everything except the agent being scored; its result is a scorecard |
| artifact | something learned from runs and sealed, with a record of what it was built from |
| campaign | the loop that proposes changes, evaluates them, gates them and promotes them |
| workcell | the process next to a robot that runs a promoted version with the same episode loop and takes operator commands |

Use Physical RSI for the overall improvement concept and campaign for the concrete comparison and promotion
process. Use Studio for the UI and episode loop in operational prose; kernel remains an implementation term.
Do not introduce numbered layers as a second product taxonomy.

Some words have several meanings. Say which one on first use:

- **protocol** in prose means the evaluation protocol. The YAML keys `benchmark.params.protocol` (the split scheme),
  a campaign's top-level `protocol:` (its gate settings) and `protocol: hylo` (a policy wire protocol) are other
  things.
- **runtime**: a named runtime in a profile, or the `runtime:` timing block of a workcell config.
- **registry**: the plugin registry, or a campaign's promotion ledger.
- **generator**: prose says generator; the YAML key is `proposer`.
- **gate**: only the campaign's confirmatory test on the `gate` split (stage 3). The earlier checks are the stage-0
  checks; never write "the gate refuses" for a stage-0 or store check.

### One fact, one home

Each fact lives on one page. Other pages give one sentence and a link.

| Fact | Home |
|---|---|
| the five concepts and their relationship | Concepts |
| agent selection and control modes | Agents |
| skill kinds, status, matching and application | Skill library |
| measured example results | Showcase, generated from the example READMEs |
| the splits, and who reads which | Campaigns |
| sync and realtime timing | Experiments |
| digest and placement | Concepts defines them, Experiments gives the rules |
| the roles of artifacts | Learning |
| leaderboard numbers | Leaderboard |
| what campaigns may not change, safety guarantees | Safety |
| Studio roles and tokens | Security |
| the repository table and the architecture diagram | Architecture |
| store lookup order, named runtimes | Execution profiles |
| workspace setup | Installation |
| test commands, skips, conformance checks | Testing |
| repository and package rules | Contributing |
| plugin maturity | the generated plugin catalogue |

### Sentences

- Lead with what the reader does, not with a taxonomy.
- One idea per sentence. No chains of semicolons, no stacked parentheses.
- Say what something does in plain words. Class paths and schema version strings belong in the reference and in
  code blocks, not in running prose.
- Give a guarantee with its conditions: say when it holds.
- State current behaviour, including limits; do not describe plans or history. "Studio starts jobs as local
  subprocesses. It does not queue them." not "There is no scheduler yet."
- English, British spelling (licence, behaviour). No marketing.
- Every option, default, path and number comes from the code or from a recorded result.
- Link with relative paths (`../user-guide/store.md`); the strict build checks them.
- User-facing commands run from `bench/`, where Installation registers the store. A page that runs commands
  elsewhere (the workspace directory, a deployments repository) says so before its first command block.
- Every page in Getting started, the User Guide and Benchmarking ends with a short `## Next`.

### Not in user pages

- RFC numbers and internal work-item names;
- dated experiment records, "first reading", "not yet conclusive";
- roadmap pointers: "not yet", "planned", "waits for a GPU";
- rename history and digest-change history (the "Older data" section of [versioning](versioning.md) is the one
  place for what still matters);
- internal run ids, artifact ids and directory names;
- links to `rfcs/`, `research/` or `design/` pages other than `design/overview.md`.

Keep current limitations: write them as current behaviour.

### Reviewing structural changes

- Preserve existing page URLs and useful section anchors when moving content; leave a short link at the old anchor.
- Rebuild both sites and run `check_site.py` on each output. The checker does not fetch external URLs.
- Execute new CPU-only tutorial snippets in an isolated output directory. Validate complete configuration examples;
  do not present an untested model or hardware workflow as a newly measured result.
- Edit generated content at its source, including `harness/docs`, example READMEs, CLI help and docstrings.
- Keep RFC index statuses consistent with their source status lines. Update the Research conclusions index when
  new evidence changes a current conclusion; preserve dated experiment records.
