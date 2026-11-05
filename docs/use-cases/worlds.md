# Build worlds { #world-construction-and-robot-motion }

Recorded scene construction and robot motions in MuJoCo. The chat-to-world recording demonstrates scene
construction and inspection; the robot-pack recordings are separate motion examples.

## Robot packs

<div class="grid" markdown>

<figure markdown>
<video src="../../assets/videos/world-quadrupeds.mp4" poster="../../assets/videos/world-quadrupeds.jpg" controls muted loop playsinline preload="none" width="100%" aria-label="Go2, Go1, A1 and Spot trotting side by side, then turning"></video>
<figcaption>Go2, Go1, A1 and Spot: 0.78 to 1.31 m forward in 4 s, then a turn, all in the same steps.</figcaption>
</figure>

<figure markdown>
<video src="../../assets/videos/world-humanoids.mp4" poster="../../assets/videos/world-humanoids.jpg" controls muted loop playsinline preload="none" width="100%" aria-label="Unitree G1 and H1 walking under pretrained policies, then turning"></video>
<figcaption>G1 and H1 leg models under pretrained walking policies: 2.2 and 2.0 m in 5 s, then a turn.</figcaption>
</figure>

<figure markdown>
<video src="../../assets/videos/world-drones.mp4" poster="../../assets/videos/world-drones.jpg" controls muted loop playsinline preload="none" width="100%" aria-label="A Crazyflie and a Skydio X2 flying three waypoints each"></video>
<figcaption>Crazyflie 2 and Skydio X2 flying three waypoints each.</figcaption>
</figure>

<figure markdown>
<video src="../../assets/videos/world-arms.mp4" poster="../../assets/videos/world-arms.jpg" controls muted loop playsinline preload="none" width="100%" aria-label="A Panda picks a cube onto a plate while a UR5e with a mounted gripper and a TidyBot base move"></video>
<figcaption>A Panda picks a cube onto a plate; a UR5e with a mounted Robotiq and a TidyBot base move in the same steps.</figcaption>
</figure>

</div>

<span id="measured-motion"></span>

[Motion measurements](../developer-guide/validation/guide-results.md#world-motion) record distance, turn and posture for the robot-pack demo.

## People

<video src="../../assets/videos/world-crowd.mp4" poster="../../assets/videos/world-crowd.jpg" controls muted loop playsinline preload="none" width="100%" aria-label="Four people walking routes around two crates while a Go1 trots across"></video>

*Four people on routes around two crates while a Go1 trots across: they plan around the crates and the dog and touch
nothing.*

## Scene construction { #chat-to-world-demo }


<video src="../../assets/videos/studio-world.mp4" poster="../../assets/videos/studio-world.jpg" controls muted playsinline preload="none" width="100%" aria-label="Recorded AI session replay: three English chat sessions build and refine a dual-arm workbench, followed by scene inspection in World Studio"></video>

*2:10 · English · Recorded AI session replay, with waits shortened. From an empty world through three build and
refinement sessions to a scene with 23 objects, including two Panda arms, followed by camera and object inspection.*

Recorded model edits are re-executed through the World API. The selected sessions retain their original messages
and tool failures; the resulting stage matches the recorded source. Two startup attempts without successful scene
changes are omitted. This demo shows scene construction and inspection; it does not demonstrate robot task execution.
The [robot-pack videos](#robot-packs) show separate recorded examples of robots moving in a world.

## Reproduce

From the **workspace root**, with the [camera renderer](../getting-started/optional-environments.md#camera-rendering) configured,
run one recorded motion workflow:

```bash
uv run python bench/adapters/hylo-env-mujoco/examples/world/showcase.py --out runs/world-showcase quadrupeds
```

The first run downloads robot assets. Inspect `results.json` and the generated videos under the output directory.
The [full results](../developer-guide/validation/tool-agents.md#worlds) include conditions and other robot families.
