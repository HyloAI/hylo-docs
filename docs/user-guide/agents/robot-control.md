# Control a robot { #a-model-controlling-a-robot }

Let a model turn a stacking instruction into robot tool calls, checking each action before continuing.
The video shows one successful Panda simulation episode with `qwen3.5:35b-a3b`; it does not establish
an aggregate success rate or hardware performance.


<video src="../../../assets/videos/tools-llm-stack.mp4" poster="../../../assets/videos/tools-llm-stack.jpg" controls muted playsinline preload="none" width="100%" aria-label="Recorded AI robot-control walkthrough: English task instruction, model tool calls, Panda grasp and place motions, measured receipts and the independent task verdict"></video>

*1:45 · English · Recorded episode walkthrough. “Stack the purple block on the green block”: locate both blocks,
choose a grasp, pick up the purple block, measure the target again, then place. Front and wrist cameras show the
motion alongside the original model's tool calls and measured receipts.*

??? info "Recording details"

    The selected `qwen3.5:35b-a3b` episode has **five model calls, two robot actions and 127 control steps**, ending in
    success according to the task's own check. It has no operator messages or safety interventions. This is one
    recorded simulation episode, not a new aggregate evaluation or a hardware demonstration.

    The presentation replays the original actions in MuJoCo at higher camera resolution. All 128 recorded joint and
    gripper states, including reset, match exactly; the replay reaches the same success verdict. The original trace's
    531 hash-chained events verify. Model waits are shortened and robot motions are slowed for readability; selected
    model text is shown as trace excerpts. The original run took 92.6 seconds.
    [Replay provenance](../../assets/videos/tools-llm-stack.provenance.json) records the source trace hash and verification.

## Try it { #reproduce-the-workflow }

Follow the [tool-calling agent guide](../tool-agents.md). A new model run may produce a different result. The recorded conditions and provenance above describe this case.
