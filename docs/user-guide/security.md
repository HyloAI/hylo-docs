# Security

This page is about who can make Hylo do what over a network or through a config. Keeping the robot within
limits is a different subject: see [safety](safety.md).

!!! danger "A config is code"
    A component in a config can be named by `module:attr` as well as by a registered name, and the registry imports
    and calls it with the config's `params` (`Registry.resolve` in `core/registry.py`). A config, an override
    (`--set agent.type=...`) or a campaign patch can therefore run any importable callable with any arguments, as
    the user who runs Hylo. Treat everyone who can submit a config as someone with a shell on that machine.

## What is exposed where

| Service | Default bind | Authentication | Who can do what |
|---|---|---|---|
| `hylo serve policy` | `127.0.0.1:8000` | optional shared token: `Authorization: Bearer <token>` or openpi's `Api-Key <token>` (`--token`) | anyone with the token gets actions from the served policy |
| `hylo serve env` / `hylo serve agent` | `127.0.0.1` | optional bearer token (`--token-env NAME` reads it from the environment) | the component is fixed when the server starts; clients cannot choose what is loaded |
| `hylo serve workcell` | `127.0.0.1:8100` | optional bearer token on HTTP, `?token=` on the event stream; `/healthz` is open | anyone with the token can start episodes and send operator events to a robot |
| `hylo playground` (studio) | `127.0.0.1:8765` | optional `--token`, or role tokens `--role-token viewer=... operator=... approver=...` | see [roles](#studio-roles) |

Every service binds to the loopback interface unless told otherwise (`--host 0.0.0.0`). Tokens travel in clear text
over `http://` and `ws://`: none of the servers terminates TLS.

## Recommendations

1. **Keep services on loopback** and reach them through an SSH tunnel (`ssh -L 8100:127.0.0.1:8100 robot-host`)
   or a reverse proxy that terminates TLS and authenticates users. Use `wss://` / `https://` through that proxy.
2. **Set a token on everything that leaves loopback**, from an environment variable, never from a file in a
   repository (the [deployments repository](../configuration/deployments-repo.md) keeps tokens out of its configs).
   Use one token per service, so that revoking one does not stop the others.
3. **Give studio role tokens** whenever more than one person can reach it. Without role tokens (and without
   `--token`) the local user has every role.
4. **Install plugins you trust.** A plugin is Python code that runs with your permissions; the registry loads it by
   name from its entry points. `hylo plugins` lists what is installed and from which package.
5. **Review candidate patches before approving** (`approval: manual` in a campaign): a patch can change any
   component. Generators only produce config patches, and model-generated code is never executed, but a patch can
   still name a `module:attr`. Stage 0 refuses patches to the protected scopes (`safety`, `benchmark`, `trace`, `scorers`, `env`,
   `evolution`, `schema_version`) and checks the provenance of referenced artifacts; it does not restrict which components a patch names.
6. **Treat run directories as data you produced.** Traces, manifests and artifacts are JSON, msgpack and `.npz`
   files; Hylo never unpickles them (`core.codec`, `core.remote.wire`: object dtypes are refused). A
   learner or adapter that loads third-party checkpoints follows that library's rules (for example PyTorch
   `torch.load`).

## Studio roles

| Role | Can |
|---|---|
| viewer | read everything; press the e-stop of a workcell (stopping is never gated behind a higher role) |
| operator | everything a viewer can, plus start live runs, jobs (`run`, `evolve`, `learn` (with any `--python` interpreter), `calibrate`) and workcell episodes, and send operator events |
| approver | everything an operator can, plus approve or roll back a campaign's promotion |

Because jobs and live runs take configs and overrides, **the operator role can run code on the studio machine**
(see the warning at the top). Give it to people you would give a shell to.

## Remote components

Remote environments and agents (`env.remote`, the `remote` agent, `remote.ws`) exchange msgpack messages with
numpy arrays encoded explicitly (`core.remote.wire`); pickle is never used, and object or void dtypes are refused.
A subprocess component (`env.remote: {runtime: ...}`) is started by Hylo itself from this machine's
[profile](../configuration/profiles.md); a WebSocket component (`hylo serve env|agent`) is chosen by whoever starts
the server, not by its clients.

## Known gaps

- No TLS termination and no user accounts in any service: put a proxy in front for anything beyond a trusted
  network.
- No allowlist for `module:attr` references: a deployment that must accept configs from less trusted users needs
  one (only registered plugin names), which does not exist yet.
- The workcell compares its token with a plain string comparison (`serve/workcell.py`), while the policy server
  and the WebSocket servers use a constant-time comparison.
