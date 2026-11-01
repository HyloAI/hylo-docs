# RFCs

Design decisions that change contracts, formats, what an experiment measures, or how the repositories fit together
are written as RFCs before (or while) they are implemented. Each RFC records its status at the top; this table
repeats it.

| RFC | Title | Status | In one line |
|---|---|---|---|
| [RFC-0001](RFC-0001.md) | Harness core architecture and v0.1 scope | Accepted with amendments (2026-10-30) | the contracts, the kernel, plugins by entry point, heavy components out of process, and what v0.1 includes |
| [RFC-0002](RFC-0002-physical-rsi.md) | Physical RSI on LIBERO (frozen VLA first, weights second) | Implemented (2026-10-30/31); weight-level units unverified | improvement as a gated experiment: development, gate and held-out splits of init states, a cascade and a sequential paired test, approval before promotion |
| [RFC-0003](RFC-0003-experience-memory-skills.md) | Experience memory and skills | Draft (2026-10-30) | action memories of verified successes, lessons and skills that steer a frozen policy |
| [RFC-0004](RFC-0004-learning-pipeline.md) | Learning pipeline and derived artifacts | Implemented (A1-A3, W1-W4; video world models and RL fine-tuning wait for a GPU) | learners build sealed artifacts with provenance and a role (behaviour, instrument, proposal); one split guard; calibrated judges |
| [RFC-0005](RFC-0005-architecture-measurement-and-placement.md) | What is measured, where it runs, and one episode loop | Parts 1-4 implemented (2026-10-31, 2026-11-01); part 5 partly; part 6 proposed | experiments vs execution profiles, one episode loop, a run and artifact store, contract versions and plugin metadata |

Statuses are the RFCs' own status lines.

## Writing an RFC

- Number it next (`RFC-0006-<slug>.md`) and add it to this table and to the navigation in `mkdocs.yml`.
- Start with a status table (status, scope, what it builds on), then the motivation: the concrete problem, found in
  the code or in a result.
- Give each part its own section with what changes, what it costs (for example, digests that change once), and how
  it was checked. Mark parts as proposed or implemented, with dates, as they land.
