# Run and artifact store

Runs and artifacts are referenced by **id**, not by path. A store is a directory tree on one machine in which every
run and every sealed artifact has a global id; configs name ids, and each machine resolves them to its own paths
([RFC-0005](../rfcs/RFC-0005-architecture-measurement-and-placement.md), part 2). The store also refuses to delete
anything that something else still refers to, and copies runs and artifacts between machines.

![Store ids, references and sync](../assets/diagrams/store.svg){ .hylo-figure }

*Ids name content; the index records what each artifact was built from and what each campaign refers to; push and
pull copy entries between machines.*

## Set up the store

```bash
uv run hylo store init bench/runs          # this machine's store, recorded in the profile
uv run hylo store where
uv run hylo store ls                       # every run and artifact, by id
uv run hylo store ls --kind artifact --json
```

The store root is, in order: `--root` on the command line, `$HYLO_STORE`, `store:` in this machine's
[execution profile](../configuration/profiles.md), and otherwise `./runs` relative to the working directory.

## Ids

| Id | Names |
|---|---|
| `run:<run_id>` | a run (a directory with `evallog.json`); run ids already end in a random suffix |
| `artifact:<name>@<digest>` | a sealed artifact (a directory with `artifact.json`): its manifest name and content digest |
| `artifact:<name>@<prefix>` | the same, with a digest prefix of at least 8 hex characters |
| `artifact:<name>` | allowed only while exactly one artifact has that name |

```bash
uv run hylo store ref bench/runs/judges/l10-trace-v2     # -> artifact:l10-trace-v2@54a1efadf00d34d8
uv run hylo store show artifact:l10-trace-v2             # entry, path on this machine, what it was built from, referrers
```

An id that is not found lists the ids with the same name; an ambiguous one lists the candidates; an id that was
removed says when and why.

## Reference artifacts in configs

```yaml
agent:
  type: remote
  params:
    ref: lerobot.noise_steered
    runtime: lerobot
    params:
      repo_id: lerobot/smolvla_libero
      memory: {type: action_bank, params: {path: "artifact:l10-noise-search-v1@2687768fc5102b06", frozen: true}}
```

- The experiment digest is taken over the id, so it pins the artifact's content, not where it is.
- The registry replaces ids with this machine's paths when it builds a component, after the digest was taken. A
  plugin still receives a path; nothing in a plugin changes.
- The run's `manifest.json` records every id the config used, with the full id and the path it resolved to
  (`artifacts:`), so a name-only id is pinned after the fact.
- Learner job inputs accept run ids (`"inputs": ["run:<run_id>"]`).
- The gate resolves ids in candidate patches, checks that the content still has the referenced digest, and refuses
  behaviour artifacts whose provenance is unknown. Generators that seal artifacts (`learn`, `critic.chunk_value`) put
  ids, not paths, into candidates.

## The index and what refers to what

`<root>/.hylo-store/index.json` is a cache, rebuilt by walking the tree whenever an id is not found (`hylo store index`
rebuilds it explicitly). Besides ids and paths it records references:

- an artifact refers to what it was built from (its provenance: runs and other artifacts);
- a campaign (`campaign:<path>`) refers to every run and artifact its archive or promotion ledger names: by id, by a
  path inside an entry, or by a run id appearing in a path recorded on another machine.

## Delete safely

```bash
uv run hylo store rm run:<run_id>
uv run hylo store rm artifact:old-critic@1a2b3c4d --force --reason "superseded by l10-v2"
```

`hylo store rm` refuses while anything refers to the entry, and lists what does. `--force` deletes anyway. Either way a
tombstone in `<root>/.hylo-store/tombstones.jsonl` records what was removed, when, why and what referred to it, so a
later lookup of that id says it was removed instead of "not found".

!!! warning
    Do not delete run directories by hand: an artifact's provenance or a campaign's archive may still name them.

## Move runs and artifacts between machines

```bash
uv run hylo store pull robot-host:/home/lab/runs                        # runs recorded on the robot computer
uv run hylo store push gpu-box:/data/runs artifact:l10-trace-v2@54a1efad --with-sources
uv run hylo store push /mnt/backup/runs --dry-run                       # what would be copied
```

| Option | Meaning |
|---|---|
| `LOCATION` | `PATH` or `HOST:PATH` (ssh and rsync) |
| `IDS ...` | what to copy (default: everything) |
| `--with-sources` | also what the selected artifacts were built from |
| `--dry-run` | print the plan |
| `--remote-wc` | the `hylo` command on the other machine (default `hylo`) |

The other side is listed with its own `hylo store ls --json`, so `hylo` must be installed there. Sealed artifacts are
never re-copied or overwritten. The same path holding a different entry on the other side is a conflict, and then
nothing is copied. Runs and mutable artifacts (such as lesson books) are brought up to date.

!!! note "Not yet"
    Sync has been tested between two local stores only, not yet over ssh. Studio shows ids but still walks
    directories for its listings, and workcell `output_dir` and campaign `out_dir` are still relative to the working
    directory: register the directory they write to as the store.

## Adopt older directories

Artifacts built before manifests existed can be sealed in place, with the runs they were built from:

```bash
uv run hylo store adopt bench/runs/memory/l10-search-v1 --kind action_memory --role behaviour \
    --source run:rsi-l10-parent-search-10507bae9c9e95b3-31f1e5
```

Without any `--source`, the provenance is recorded as unknown. Such an artifact can still be used in experiments,
but the gate refuses it as a behaviour artifact in a candidate, because a leak of gate or held-out data cannot be
ruled out.
