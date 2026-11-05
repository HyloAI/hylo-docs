# Worlds

A world is a simulation in which agents can act and receive measured feedback. It contains robots, objects,
cameras and goals. Use it to develop a task or explore a scene; use a benchmark when you need a fixed comparison.

## World model { #stage-world-and-task }

| Term | Meaning |
|---|---|
| Stage | The saved scene description: entities, poses and robot packs, with revision history |
| World | The running simulation built from a stage revision |
| Task | An instruction and an explicit goal checked against what happened |

Changing a stage does not change a running world until it is rebuilt. Actions name the world generation they
were planned for, so an action based on an earlier build can be refused. Receipts describe the measured motion;
goal checks decide whether the requested result holds.

## Agent integration { #how-agents-use-worlds }

A person, a model or a coding agent can edit a stage, build it, act and check outcomes through the same world
tools. Robot packs supply models and supported controls. Camera observations can feed an agent's memory;
role campaigns can retain replay-verified action recipes as skills.

A successful goal check establishes an outcome in that scene. Comparing improvements across tasks requires a
separate evaluation protocol; a world session alone is not that comparison.

## Next

- [Create and run a world](../worlds.md): build a small scene and check a physical outcome.
- [World reference](../../reference/worlds.md): stage fields, robot packs, actions and goals.
- [World examples](examples.md): recorded scenes, robot motions and their conditions.
