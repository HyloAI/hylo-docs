# Security

Who can make Hylo do what, over the network or through a config, and how to deploy it safely. This page is the
reference for tokens and Studio roles. Robot limits are on [safety](safety.md).

!!! danger "A config is code"
    A config can name a component by `module:attr` instead of a plugin name, and Hylo imports and calls it with the
    config's `params`. So a config, a `--set` override or a campaign patch can run any importable Python function,
    as the user running Hylo. Treat everyone who can submit a config as someone with a shell on that machine.

## Access boundaries { #what-is-exposed-where }

Every service binds to the loopback interface unless you pass `--host 0.0.0.0`. No service terminates TLS or
manages user accounts, so tokens travel in clear text over `http://` and `ws://`. Without a token, anyone who can
reach the port can do everything the last column lists.

| Service | Default bind | Token | Anyone who passes the check can |
|---|---|---|---|
| `hylo serve policy` | `127.0.0.1:8000` | `--token`: `Authorization: Bearer <token>`, or openpi's `Api-Key <token>`. `/healthz` is open; `/meta`, `/hylo` and `/openpi` need the token. | get action chunks from the served agent and read its spec |
| `hylo serve env`, `hylo serve agent` | `127.0.0.1:8765` | `--token-env NAME` reads the token from an environment variable: `Authorization: Bearer <token>`. `/healthz` is open. | drive the component: step the simulator, or get actions from the agent. The component is fixed when the server starts; clients cannot choose what is loaded. |
| `hylo serve workcell` | `127.0.0.1:8100` | `--token`: `Authorization: Bearer <token>` on HTTP, `?token=<token>` on `/events`. `/healthz` is open. | start episodes on the robot, send operator events, watch the live stream, and read `/status`, which includes the configured policy endpoint and its `token` |
| `hylo playground` (Studio) | `127.0.0.1:8765` | `--token`, or role tokens with `--role-token`: `x-token` header or `?token=` | depends on the role ([below](#studio-roles)) |

Only `hylo serve env` and `hylo serve agent` read the token from an environment variable. `hylo serve policy`,
`hylo serve workcell` and `hylo playground` take it on the command line, so it shows in the process list of that
machine.

## Recommendations

1. **Keep services on loopback.** Reach them through an SSH tunnel (`ssh -L 8100:127.0.0.1:8100 robot-host`) or a
   reverse proxy that terminates TLS and authenticates users. Use `wss://` and `https://` through that proxy.
2. **Set a token on everything that leaves loopback.** Use one token per service, so that revoking one does not
   stop the others. Keep tokens out of repositories.
3. **Give Studio role tokens** whenever more than one person can reach it.
4. **Install plugins you trust, and accept configs only from people you would give a shell.** A plugin is Python
   code that runs with your permissions, and Hylo has no allowlist for `module:attr`. `hylo plugins` lists what is
   installed and from which package.
5. **Know what manual approval protects.** It controls promotion, not execution: by the time a candidate waits
   for approval, the campaign has already run its config, including any `module:attr` its patch names. The protected keys
   ([safety](safety.md#safety-in-campaigns)) do not restrict which components a patch names.
6. **Check how third-party checkpoints are loaded.** Hylo's own formats are JSON, `.npy` and `.npz`. Hylo never
   unpickles them and refuses object dtypes. A learner or adapter that loads third-party checkpoints follows that
   library's rules, for example PyTorch's `torch.load`.

## Generated code { #model-written-programs }

`code.llm`, `code.program` and research submissions use AST validation and a restricted Python namespace. Imports,
private attributes and file operations are restricted, and a watchdog interrupts Python execution. The program
runs in a thread in the host process: this is not an operating-system jail, memory is not limited, and a call
blocked in C code can stop only when it returns. For untrusted programs, use a separately isolated environment
with bounded resources. The SafetyShield checks robot actions; it is not host-process isolation.

Campaign approval controls promotion after evaluation. It does not prevent a candidate from executing during
evaluation. Sealed program artifacts should be immutable and digest-pinned. Current validation has known gaps:
a manifest marked `mutable` bypasses the digest check, and the code-candidate check does not bind an arbitrary
agent configuration to the actual referenced program. Treat configs and candidates as trusted inputs until
those checks are tightened; do not describe the current gate as a host-code security boundary.

## Worlds and MCP

- `hylo mcp` serves the world tools over stdio to the program that started it: whoever controls that agent can
  edit stages, run robots and write exports under the stage's output folder. It opens no network port.
- The Studio's World page starts `hylo world chat` subprocesses with the configured model; give it a role token
  when the port is reachable by others.
- Pretrained policies are never deserialised by a general unpickler: their tensors are read with a reader that
  knows only tensor rebuilding and refuses any other object, and they run with numpy.
- Robot models and policy files are fetched from pinned commits and checked file by file against recorded digests;
  a changed cached file is refused.

## Studio roles

Studio checks the token on every API call and maps it to a role:

- With no `--token` and no `--role-token`, anyone who can reach the port has every role, including approver.
- The token given with `--token` has the approver role.
- Each `--role-token ROLE=TOKEN` adds a token for that role.

| Role | Can |
|---|---|
| viewer | read everything, watch workcell streams, and press the e-stop of a workcell (the e-stop is never gated behind a higher role; a plain `stop` needs the operator role) |
| operator | everything a viewer can, plus run live sandbox episodes, start jobs (`run`, `evolve`, `learn` with any `--python` interpreter, `calibrate`), start workcell episodes, and send every operator event |
| approver | everything an operator can, plus approve a campaign's pending candidate or roll back its active version |

Jobs and live sandbox episodes take configs and overrides, so **the operator role can run code on the Studio
machine**. Give it only to people you would give a shell to.

## Constraints { #known-gaps }

These are current behaviours to plan around:

- The workcell compares tokens with a plain string comparison. The policy server and the `hylo serve env` and
  `hylo serve agent` servers use a constant-time comparison.
- The workcell's `/status` returns the policy endpoint from its config, token included. Studio shows that status to
  every role, viewers included. Give the policy token per episode (in the `StartEpisode` request, or with Studio's
  `--policy NAME=URL#TOKEN`) rather than in the workcell config.

## Next

- [Studio](studio.md): start the web UI and operate workcells.
- [Execution profiles](../configuration/profiles.md): where runtimes and the store are set on each machine.
