# MuJoCo (Python bindings) Source-Level Architecture Study

> Repository: `references/simulation/mujoco` (google-deepmind/mujoco @ `a650501`, 2026-10-29, Apache-2.0)
> Scope: the focus is the `python/mujoco` bindings package (MjModel/MjData, `mj_step`, Renderer, viewer, rollout, batch), `mjx/` and `python/mujoco/usd`. For the C engine we only locate the entry functions.
> Method: static reading only (read / grep); no build, install or run, and no assets downloaded.
> Tags: **\[Implemented\]** code exists and can be traced to specific lines · **\[Docs/Interface only\]** only a documentation description or an abstract declaration · **\[Unverified\]** code exists but we have not run it · **\[Needs model/hardware\]** requires GPU, EGL/OSMesa, JAX/Warp or an external model
> Citation prefix: `references/simulation/mujoco/`. Paths below omit this prefix; for example `python/mujoco/rollout.py:50` is actually `references/simulation/mujoco/python/mujoco/rollout.py:50`.

---

## 1. Positioning and Core Capabilities

MuJoCo is a **physics engine + low-level API**, **not** an environment framework. The repository has no concepts such as `Env`, `Task`, reward or success (grepping `python/` and `mjx/` for `gymnasium|dm_control|class .*Env` finds no env classes). Gymnasium's `MujocoEnv` and dm_control's `composer.Task`/`suite` live in other repositories and are mentioned here only as background. Therefore, for Hylo, MuJoCo is a backend for the **Simulator layer**: Task, Reward and Evaluator all have to be written by us.

| Capability | Status | Evidence |
|---|---|---|
| Load models from MJCF/XML, XML strings, MJB binaries (supports assets dict or VFS) | \[Implemented\] | `python/mujoco/structs.cc:366-386` |
| Programmatic modeling `MjSpec` (from_file/from_string → compile/recompile/attach/to_xml) | \[Implemented\] | `python/mujoco/specs.cc:336-345`, `:468`, `:504`, `:619`, `:703` |
| `mj_step(m, d, nstep=1)`, releases the GIL during the call | \[Implemented\] | `python/mujoco/functions.cc:163-176` |
| reset: `mj_resetData` / `mj_resetDataKeyframe` | \[Implemented\] | `include/mujoco/mujoco.h:276`, `:282`; `src/engine/engine_io.c:1743`, `:1759` |
| Full state save and restore `mj_getState`/`mj_setState` (components selected via `mjtState` bits) | \[Implemented\] | `include/mujoco/mujoco.h:522-529`; `src/engine/engine_support.c:220`, `:288` |
| `MjModel`/`MjData` support copy, deepcopy, pickle | \[Implemented\] | `python/mujoco/structs.cc:390-396`, `:971-990` |
| Access by name (`d.sensor('x').data`, `d.actuator('a').ctrl`), and `bind` to MjSpec elements | \[Implemented\] | `python/mujoco/indexer_xmacro.h:212-214`, `python/mujoco/__init__.py:200-240` |
| Offscreen rendering `Renderer` (RGB / depth / segmentation, camera can be specified) | \[Implemented\] \[Needs model/hardware\] | `python/mujoco/rendering/classic/renderer.py:26-101`, `:132`, `:261-310` |
| GL backend selection via `MUJOCO_GL` (glfw/egl/osmesa/cgl/wgl/disable) | \[Implemented\] | `python/mujoco/rendering/classic/gl_context.py:24-56` |
| Multi-GPU EGL device selection (`MUJOCO_EGL_DEVICE_ID`, aligned with `CUDA_VISIBLE_DEVICES`) | \[Implemented\] \[Needs model/hardware\] | `python/mujoco/egl/__init__.py:132-170` |
| Multithreaded open-loop batch rollout (`rollout.rollout`), C++ thread pool, releases the GIL | \[Implemented\] \[Unverified\] | `python/mujoco/rollout.py:27-63`, `:261-345`; `python/mujoco/rollout.cc:118-169`, `:312-313` |
| `batch.Batch`: nsim simulations share nthread threads, live-bound arrays, can reset to a keyframe, and claims bit-identical results for any thread count | \[Implemented\] \[Unverified\] | `python/mujoco/batch.py:15-58`, `:116-146`, `:319-373`; `python/mujoco/batch_test.py:88` |
| Interactive viewer (`launch` blocks; `launch_passive` is a non-blocking mode returning a Handle) | \[Implemented\] \[Needs model/hardware\] | `python/mujoco/viewer.py:532-575`, `:65` |
| MJX: JAX version of `put_model/make_data/step`, with three implementations `Impl.JAX/WARP/CPP`, plus batch rendering | \[Implemented\] \[Needs model/hardware\] | `mjx/mujoco/mjx/__init__.py:18-79`; `mjx/mujoco/mjx/_src/io.py:60-75`, `:567`, `:894`; `mjx/mujoco/mjx/_src/types.py:29-35` |
| USD export (`USDExporter`) | \[Implemented\] \[Unverified\] | `python/mujoco/usd/exporter.py:36-60` |
| Filament renderer (new, based on `mjrf.Context`) | \[Implemented\] \[Unverified\] | `python/mujoco/rendering/filament/renderer.py:116`, `:138`, `:193` |
| Engine plugins (actuator/sensor/sdf/elasticity/mesh decoder), loaded automatically on import | \[Implemented\] | `python/mujoco/__init__.py:242-257`; `include/mujoco/mjplugin.h:121`, `:194`; `plugin/` |
| Determinism: bit-wise reproducible on the same version and same architecture | \[Docs/Interface only\] (this guarantee comes from the docs; the batch tests verify only part of it) | `doc/computation/index.rst:2367-2388` |

## 2. Directory Layout and Architecture

```
mujoco/
├── include/mujoco/      C API headers: mujoco.h (functions), mjmodel.h, mjdata.h, mjplugin.h, mjxmacro.h
├── src/engine/          C engine: engine_forward.c (mj_step/mj_forward), engine_io.c (reset), engine_support.c (state)
├── src/user/            MJCF compiler / mjSpec
├── plugin/              actuator, sensor, sdf, elasticity, *_decoder (obj/stl/gmsh/usd)
├── python/mujoco/       pybind11 bindings (_structs, _functions, _specs, _render, _rollout, _batch, _simulate, _callbacks)
│   ├── rendering/classic/   Renderer + GLContext selection (egl/osmesa/glfw/cgl)
│   ├── rendering/filament/  Filament renderer
│   ├── rollout.py / batch.py  CPU-parallel batch simulation
│   ├── viewer.py            passive and active viewer (_simulate)
│   ├── usd/                 USD export
│   └── sysid/, minimize.py  system identification and least-squares tools
├── mjx/mujoco/mjx/      JAX/Warp backend (namespace package mujoco-mjx)
├── model/               example MJCF (humanoid, flex, mug, plugin examples ...)
└── simulate/, studio/, unity/, wasm/   GUI / Unity / WebAssembly frontends
```

```mermaid
graph TD
  subgraph Python["python/mujoco (pybind11)"]
    S[_structs: MjModel / MjData / MjOption] --> F[_functions: mj_step / mj_forward / mj_resetData / mj_get/setState]
    SP[_specs: MjSpec] -->|compile| S
    R[rendering.classic.Renderer] --> RC[_render: MjrContext / mjr_render / mjr_readPixels]
    R --> GL[GLContext: EGL / OSMesa / GLFW / CGL]
    RO[rollout.py -> _rollout] --> F
    B[batch.py -> _batch] --> F
    V[viewer.py -> _simulate]
    U[usd.USDExporter]
  end
  subgraph C["libmujoco (C)"]
    ENG[engine_forward.c mj_step]
    IO[engine_io.c mj_resetData]
    ST[engine_support.c mj_getState/mj_setState]
    PL[mjp_registerPlugin / plugin .so]
  end
  F --> ENG & IO & ST
  S --> PL
  MJX[mjx: put_model / make_data / step  JAX|Warp|CPP] -.->|reads| S
  GymEnv[External: Gymnasium MujocoEnv / dm_control] -.-> Python
```

## 3. Core Interfaces and Key Classes

```python
# Loading (python/mujoco/structs.cc:366-386)
MjModel.from_xml_path(filename: str, assets: dict[str, bytes] | None = None, vfs: MjVfs | None = None) -> MjModel
MjModel.from_xml_string(xml: str, assets=None, vfs=None) -> MjModel
MjModel.from_binary_path(filename: str, assets=None, vfs=None) -> MjModel
MjData(model: MjModel)                                   # structs.cc:960
MjSpec.from_file(filename, include=None, assets=None, vfs=None) -> MjSpec   # specs.cc:336
spec.compile() -> MjModel; spec.recompile(m, d) -> MjData; spec.attach(...); spec.to_xml() -> str

# Simulation (functions.cc:163-176; include/mujoco/mujoco.h)
mj_step(m: MjModel, d: MjData, nstep: int = 1) -> None    # modifies d in place; releases the GIL during the call
mj_forward(m, d) -> None; mj_step1 / mj_step2             # mujoco.h:203-212
mj_resetData(m, d) -> None; mj_resetDataKeyframe(m, d, key: int) -> None   # mujoco.h:276, 282
mj_getState(m, d, state: np.ndarray, sig: mjtState) ; mj_setState(m, d, state, sig)  # mujoco.h:522-529
mj_name2id(m, type: mjtObj, name: str) -> int             # mujoco.h:618
set_mjcb_control(fn)                                       # callbacks.cc:487 (global C callback)

# Data fields (include/mujoco/mjdata.h)
d.ctrl (nu,)  :188 ; d.sensordata (nsensordata,) :205 ; d.qpos / d.qvel / d.time / d.warning
m.actuator_ctrlrange (nu,2), m.actuator_ctrllimited  # mjmodel.h:812-813 → source of the action spec

# Rendering (python/mujoco/rendering/classic/renderer.py)
class Renderer:
    def __init__(self, model, height=240, width=320, max_geom=10000, font_scale=...)  # :29
    def update_scene(self, data, camera: int|str|MjvCamera = -1, scene_option=None)    # :261
    def render(self, *, out: np.ndarray | None = None) -> np.ndarray  # (H,W,3) uint8 or (H,W) depth  :132
    def enable_depth_rendering(); enable_segmentation_rendering(); close()             # :118-129, :316

# Batch (python/mujoco/rollout.py, batch.py)
rollout.rollout(model, data, initial_state, control=None, *, control_spec=mjSTATE_CTRL,
                skip_checks=False, nstep=None, initial_warmstart=None, state=None,
                sensordata=None, chunk_size=None, persistent_pool=False) -> (state[nb,ns,nstate], sensordata[nb,ns,nsens])  # :261
class Batch(model, nsim, nthread=0, persistent=False)                 # batch.py:116
    bind(name) -> np.ndarray (nsim, ...) live view                     # :189
    step(ids=None, nstep=1, stage=mjSTAGE_NONE)                        # :319
    reset(ids=None, keyframe=-1, stage=mjSTAGE_ACC)                    # :349
    rollout(nstep, control=None, control_spec=..., record=('qpos',), ids=None, out=None) -> dict  # :470
    get_data(sim, data=None) -> MjData                                 # :444 (used for per-env rendering)

# Viewer (python/mujoco/viewer.py)
launch(model=None, data=None, *, loader=None, ...) -> None             # :532 blocking
launch_passive(model, data, *, key_callback=None, ...) -> Handle       # :556 (macOS requires mjpython)

# MJX (mjx/mujoco/mjx/_src)
put_model(m, device=None, impl=None) -> mjx.Model                      # io.py:567
make_data(m, device=None, impl=None) -> mjx.Data                       # io.py:894
step(m: Model, d: Data) -> Data   # pure function, can be jax.vmap / jit           # forward.py:564
```

**Conclusion**: all APIs follow a "model + data + free functions" style. There is no reward/terminated/obs convention; an action is just writing values into `d.ctrl`; the observation is assembled by the caller from `qpos/qvel/sensordata`/render output.

## 4. Core Execution Flow

```mermaid
sequenceDiagram
  participant H as Harness (Hylo)
  participant Py as mujoco (pybind11)
  participant C as libmujoco
  participant GL as Renderer/GLContext
  H->>Py: MjModel.from_xml_path(xml) ; MjData(m)
  H->>Py: reset: mj_resetDataKeyframe(m,d,k) or mj_resetData
  Py->>C: engine_io.c:1743/1759
  H->>H: Task.initialize_episode(rng): write randomized values into d.qpos / m.body_pos (MuJoCo provides no RNG)
  H->>Py: mj_forward(m,d)  (refresh derived quantities and sensordata)
  loop each control step
    H->>Py: d.ctrl[:] = clip(action, m.actuator_ctrlrange)
    H->>Py: mj_step(m,d,nstep=frame_skip)   (releases GIL)
    Py->>C: mj_checkPos/Vel → mj_forward → mj_checkAcc (auto-reset on divergence) → integrator
    H->>Py: read d.sensordata / d.qpos / d.warning
    opt when images are needed
      H->>GL: renderer.update_scene(d, camera="wrist"); renderer.render()
    end
    H->>H: Task.reward(), Task.success(), Evaluator.record()   ← not provided by MuJoCo
  end
  H->>GL: renderer.close()
```

Key details:
- The order inside `mj_step` is checkPos → checkVel → `mj_forward` → `mj_checkAcc` → integrator (`src/engine/engine_forward.c:2330-2365`). **If qacc contains NaN/Inf, the engine silently performs `mj_resetData` and increments the `warning[mjWARN_BADQACC]` counter** (`src/engine/engine_forward.c:97-112`), unless `mjDSBL_AUTORESET` is set. Our `step()` must check `d.warning` and map this case to `truncated=True` plus `info["sim_error"]`; otherwise the episode will silently restart from the initial state. \[Implemented\]
- After `mj_step`, derived quantities (`xpos`, sensordata) correspond to the state **before the last substep**. `batch.py:29-31` and `:327-335` state this explicitly: before reading sensors you may need to call `mj_forward` or use `stage=mjSTAGE_VEL`. \[Implemented\]

## 5. Extension Points and Plugin Mechanism

| Extension point | Mechanism | Evidence | Status |
|---|---|---|---|
| New task / scene | Write MJCF, or assemble programmatically with `MjSpec` (attach robot and objects). There is no task registry | `python/mujoco/specs.cc:336`, `:703` | \[Implemented\] |
| Engine plugins (custom actuator/sensor/passive force/SDF) | C struct `mjpPlugin` + `mjp_registerPlugin`, auto-registered via `mjPLUGIN_LIB_INIT`; on import the Python package loads `mujoco/plugin/*.so` via `ctypes.CDLL` | `include/mujoco/mjplugin.h:121`, `:194-216`; `include/mujoco/mujoco.h:690-695`, `:1556`; `python/mujoco/__init__.py:242-257` | \[Implemented\] |
| Physics callbacks | `set_mjcb_control/passive/contactfilter` (global, process-wide). `batch` requires callbacks to be C functions; passing a Python function raises ValueError | `python/mujoco/callbacks.cc:484-490`; `python/mujoco/batch.py:53-56` | \[Implemented\] |
| Rendering backend | Set the `MUJOCO_GL` environment variable, or switch to Filament / MJX batch rendering | `python/mujoco/rendering/classic/gl_context.py:24-56` | \[Implemented\] |
| Asset injection | `assets: dict[str, bytes]` or `MjVfs` (bypasses the filesystem) | `python/mujoco/structs.cc:366-386`; `python/mujoco/vfs_test.py` | \[Implemented\] |
| Acceleration backend | Use MJX `impl='jax'|'warp'|'cpp'`; on GPU the default is JAX, set `MJX_GPU_DEFAULT_WARP=true` to switch to Warp | `mjx/mujoco/mjx/_src/io.py:60-75` | \[Implemented\] \[Needs model/hardware\] |

## 6. Dependencies and Runtime Requirements

- Python package: `requires-python >=3.11`, dependencies `glfw, numpy, pyopengl, websockets>=13` (`python/pyproject.toml:12`, `:27-32`); extras include `usd = [usd-core, pillow]` and `sysid` (`:67-82`). \[Implemented\]
- Building from source requires setting the `MUJOCO_PATH` and `MUJOCO_PLUGIN_PATH` environment variables; setup.py copies the plugin .so files (`python/setup.py:35-36`, `:167-171`, `:201-215`). C dependencies are pulled via FetchContent during the CMake stage: tinyxml2, tinyobjloader, ccd, qhull, miniz, Eigen3, abseil, etc. (`cmake/MujocoDependencies.cmake:17-56`). **We should only use the PyPI wheel and not build it ourselves.** \[Docs/Interface only\]
- Rendering: on headless Linux set `MUJOCO_GL=egl` (requires GPU driver and libEGL) or `MUJOCO_GL=osmesa` (pure CPU, very slow). Both modules set or validate `PYOPENGL_PLATFORM` and raise an error immediately if it conflicts with another library's setting (`python/mujoco/egl/__init__.py:22-31`, `python/mujoco/osmesa/__init__.py:22-31`). Offscreen resolution is limited by `<visual><global offwidth/offheight>` in the MJCF (`python/mujoco/rendering/classic/renderer.py:57-75`). \[Needs model/hardware\]
- Physics simulation: **pure CPU, no GPU required**. When CI runs the Python tests it sets `MUJOCO_GL: disable` (`.github/workflows/build.yml:270-275`, `.github/workflows/build_steps.sh:460-463`), so **most rendering paths are skipped in CI** (`python/mujoco/render_test.py:71-72`). \[Implemented\]
- MJX: requires `jax, jaxlib, scipy, trimesh, mujoco>=3.17.1.dev0`, optionally `warp-lang==1.18.0` (`mjx/pyproject.toml:28-41`). The Warp implementation requires a CUDA GPU (`mjx/mujoco/mjx/_src/io.py:98-99`). \[Needs model/hardware\]
- macOS: `launch_passive` must run under `mjpython`, and `mjpython` is only installed on Darwin (`python/setup.py:438-440`).

## 7. License and Reuse Constraints

- The main repository is Apache-2.0 (`LICENSE`). Example MJCF files under `model/` carry an Apache-2.0 header (e.g. `model/flex/gripper.xml:1-12`) and can be reused provided the NOTICE is retained. \[Implemented\]
- Embedded third-party components: `python/mujoco/studio/netimgui/LICENSE` is MIT, `python/mujoco/studio/implot/LICENSE-2.0.txt` is Apache-2.0. Dependencies pulled by CMake (qhull, tinyxml2, etc.) each have their own licenses, which only affect source-build distribution; when using the wheel, upstream packaging is responsible. \[Unverified\]
- **Robot and scene assets are not in this repository**. MuJoCo Menagerie (Franka, UR5e, etc.) is a separate repository where each model has its own LICENSE, and some are not Apache. LIBERO/robosuite assets also have their own licenses. These asset licenses need to be registered separately in `research/comparisons/license-matrix.md`. \[Docs/Interface only\]
- Mesh files in `model/` (e.g. `model/mug/mug.obj`) have no separate license statement and are assumed by default to be covered by the repository license. \[Unverified\]

## 8. Strengths, Weaknesses and Risks

**Strengths**
- The low-level API is stable and orthogonal: `MjModel`/`MjData` are separate; state can be fully serialized (`mj_getState` with `mjSTATE_INTEGRATION`, or pickle), which naturally supports reset-to-state, replay, tree search and world-model data collection. \[Implemented\]
- The docs promise determinism (same version, same architecture); `batch` claims bit-identical results for any thread count, with `test_lockstep` and `test_rollout_matches_mujoco_rollout` tests (`python/mujoco/batch_test.py:88`, `:787`). \[Implemented\] \[Unverified\]
- CPU parallelism is natively implemented: both `rollout` and `Batch` run in a C++ thread pool and release the GIL (`python/mujoco/rollout.cc:312-313`, `python/mujoco/batch.cc:189`, `:242`); the bindings also support free-threaded Python (`mod_gil_not_used`, `python/mujoco/functions.cc:40`; mutex in `python/mujoco/gil.h:22-28`; tests in `python/mujoco/thread_safety_test.py:15-23`). \[Implemented\]
- The physics part does not depend on a GPU, making it suitable for smoke tests in CI.

**Weaknesses and risks**
- **No env, task, reward, success or seeding abstractions**. MuJoCo itself contains no RNG: `sensor_noise` appears only in the compiler `src/user/user_model.cc` and is not used by the engine. Randomization must be done by our Task layer with an explicit `np.random.Generator`. \[Implemented\]
- Silent auto-reset on divergence (see §4); if not handled, it will contaminate evaluation results. \[Implemented\]
- `Renderer` is bound to a GL context and **cannot be shared across threads**. Each worker needs its own Renderer; releasing it requires `as_current()` (`python/mujoco/rendering/classic/renderer.py:316-343`). EGL and OSMesa can only be chosen (one or the other) via environment variable at import time; the same process cannot switch. \[Implemented\]
- By default `Batch` has multiple simulations share an MjData, so derived fields that were not computed get mixed with values from other simulations; sleep/IPC models must set `persistent=True` (`python/mujoco/batch.py:43-50`). Batch rendering requires `get_data(sim)` first and then rendering one by one; there is no batched rendering. \[Implemented\]
- No bit-wise consistency guarantee across versions or platforms (`doc/computation/index.rst:2383-2386`). Evaluation results should record `mujoco.__version__` (`python/mujoco/__init__.py:259`). Some contact sensor reduce options are inherently non-deterministic (`doc/XMLreference.rst:9315`, `:9414`). \[Docs/Interface only\]
- The main-branch API changes quickly (`batch.py`, the filament renderer and `gil.h` are all new files from 2026), so the version must be pinned when used.

## 9. Components Worth Reusing

1. **The whole `mujoco` PyPI wheel**, as the `MuJoCoSimulator` backend. Directly reuse `MjModel/MjData/mj_step/mj_getState/mj_setState`.
2. **`rendering.classic.Renderer`** as the implementation of `render(camera)`, plus multi-GPU selection via `MUJOCO_GL` and `MUJOCO_EGL_DEVICE_ID`.
3. **`mujoco.batch.Batch`** as the CPU vectorization backend: `reset(ids, keyframe)` maps exactly to partial reset, and `bind()` provides zero-copy obs and action views.
4. **`mujoco.rollout`**, for open-loop planning, MPC and world-model data generation (self-improvement module).
5. **`MjSpec`**, for programmatic scene assembly and domain randomization (the Task layer generates scene variants).
6. **MJX** (optional), used when JAX end-to-end differentiability or large GPU batches are needed.

## 10. Capabilities Not Worth Rebuilding

- Physics integration, contact solving, MJCF parsing, the keyframe mechanism, state serialization: all provided by the engine.
- Headless GL context management (EGL device enumeration, OSMesa): use `mujoco.GLContext` directly.
- Multithreaded batch stepping and rollout: do not wrap `mj_step` in Python multiprocessing ourselves; use `Batch`/`rollout` first, and only move to a process pool when rendering isolation is needed.
- Interactive debugging viewer: `viewer.launch_passive`.
- USD export (for Isaac/Omniverse visualization): `mujoco.usd.USDExporter`.

## 11. Source Index of Key Implementations

| Topic | Location (`references/simulation/mujoco/...`) |
|---|---|
| Package entry, plugin auto-loading, version | `python/mujoco/__init__.py:54-80`, `:242-259` |
| MjModel load / copy / pickle | `python/mujoco/structs.cc:365-400` |
| MjData construction / copy / pickle | `python/mujoco/structs.cc:959-990` |
| `mj_step` binding (nstep, GIL release) | `python/mujoco/functions.cc:163-176` |
| C API: step/forward/reset/state/name2id | `include/mujoco/mujoco.h:203-212`, `:276-282`, `:522-529`, `:618` |
| `mj_step` implementation | `src/engine/engine_forward.c:2330-2365` |
| Auto-reset on divergence | `src/engine/engine_forward.c:58-112` |
| reset implementation | `src/engine/engine_io.c:1743-1770` |
| get/setState implementation | `src/engine/engine_support.c:220-300` |
| ctrlrange / sensor definitions | `include/mujoco/mjmodel.h:812-813`, `:831`; `include/mujoco/mjdata.h:188`, `:205` |
| Renderer | `python/mujoco/rendering/classic/renderer.py:26-352` |
| GL backend selection | `python/mujoco/rendering/classic/gl_context.py:24-56` |
| EGL device selection | `python/mujoco/egl/__init__.py:132-170` |
| rollout (Py / C++) | `python/mujoco/rollout.py:27-345`; `python/mujoco/rollout.cc:76-170`, `:312-330` |
| Batch | `python/mujoco/batch.py:15-58`, `:116-540`; `python/mujoco/batch.cc` |
| Viewer | `python/mujoco/viewer.py:65`, `:532-575` |
| MjSpec | `python/mujoco/specs.cc:333-345`, `:468`, `:504`, `:619`, `:703` |
| Callbacks | `python/mujoco/callbacks.cc:484-490` |
| Plugin ABI | `include/mujoco/mjplugin.h:121`, `:194-216`; `include/mujoco/mujoco.h:690-695`, `:1556` |
| MJX public API / impl selection | `mjx/mujoco/mjx/__init__.py:18-79`; `mjx/mujoco/mjx/_src/io.py:60-110`, `:567`, `:894`; `mjx/mujoco/mjx/_src/forward.py:564` |
| USD export | `python/mujoco/usd/exporter.py:36-60`, `:210` |
| Determinism docs | `doc/computation/index.rst:2367-2388`; `doc/programming/simulation.rst:370-380` |
| Tests | `python/mujoco/bindings_test.py`, `rollout_test.py` (28 tests), `batch_test.py` (47), `thread_safety_test.py`, `render_test.py`, `renderer_test.py`, `viewer_test.py`, `specs_test.py` |
| CI | `.github/workflows/build.yml:270-275`; `.github/workflows/build_steps.sh:460-463` |

## 12. Mapping to Hylo Environment Interface

MuJoCo can only provide the **Simulator** layer. A `MuJoCoSimulator` adapter plus our own `Task` and `Evaluator` together make up a complete Environment.

| Hylo contract | MuJoCo implementation | Responsible layer | Notes |
|---|---|---|---|
| `reset(seed, options) -> Observation` | `rng = np.random.default_rng(seed)`; `mj_resetDataKeyframe(m,d,options.get("keyframe",k))` or `mj_resetData`; `task.initialize_episode(m, d, rng)` writes qpos etc.; `mj_forward`; when `options["state"]` is given, use `mj_setState(m,d,s,mjSTATE_INTEGRATION)` | Simulator + Task | MuJoCo has no seed parameter; the seed is consumed entirely by the Task RNG |
| `step(Action) -> StepResult(obs, reward, terminated, truncated, info)` | `d.ctrl[:] = clip(a, m.actuator_ctrlrange)`; `mj_step(m,d,nstep=frame_skip)`; `reward=task.reward()`; `terminated=task.success() or task.failure()`; `truncated = t>=T or d.warning[mjWARN_BADQACC].number increases` | Simulator + Task | Must check for divergence auto-reset (`engine_forward.c:105-110`) |
| `observation_spec` | Derived statically from `m.nq/nv/nsensordata`, `m.sensor_dim`, the camera list (`m.ncam`, `mj_name2id`) plus the Renderer's H/W | Task (selects fields) | No need to reset once first to derive it, unlike ManiSkill |
| `action_spec` | `Box(low=ctrlrange[:,0], high=ctrlrange[:,1], shape=(nu,))`; unbounded when `ctrllimited=0` | Simulator | Semantics (joint position / torque / EE) are determined by the MJCF actuator; controllers must be implemented separately in the Task or Robot layer |
| task success predicate | **None**. Write `Task.success(m,d)->bool` using `d.site('x').xpos`, `d.sensor('touch').data`, and the contact list | Task | Follow ManiSkill's `evaluate()` dict convention |
| `render(camera)` | `renderer.update_scene(d, camera=name_or_id); renderer.render()`; depth / seg via `enable_*_rendering` | Simulator | One Renderer per thread or process |
| `close()` | `renderer.close()`; `Rollout.close()` / `shutdown_persistent_pool()` (`rollout.py:46`, `:247`) | Simulator | |
| Vectorized `VectorEnv` | `Batch(m, nsim, nthread)`, partial reset via `reset(ids, keyframe)`; rendering goes through `get_data(sim)` | Simulator | MJX `vmap(step)` can also be used |
| `get_state/set_state` (replay and search) | `mj_getState/mj_setState(sig=mjSTATE_INTEGRATION)`, or pickle MjData | Simulator | Not comparable across versions |

## Verification Status Summary

| Capability | Tag | Notes |
|---|---|---|
| XML/MJB loading, MjSpec | \[Implemented\] | Binding code is traceable; `specs_test.py` exists but we have not run it |
| mj_step / reset / keyframe / get/setState | \[Implemented\] | Both C and bindings are traceable |
| Auto-reset on divergence | \[Implemented\] | `engine_forward.c:97-112` |
| Determinism (same version, same architecture) | \[Docs/Interface only\] | Stated in docs; batch lockstep tests exist but we have not run them |
| GIL release / free-threading | \[Implemented\] \[Unverified\] | `call_guard` and `gil.h` exist; we have not stress-tested |
| rollout / Batch multithreading | \[Implemented\] \[Unverified\] | Tests exist; we have not run them |
| Offscreen rendering (EGL/OSMesa) | \[Implemented\] \[Needs model/hardware\] | `MUJOCO_GL=disable` in CI; most rendering tests are skipped |
| Viewer | \[Implemented\] \[Needs model/hardware\] | Requires a display / GLFW |
| MJX (JAX/Warp) | \[Implemented\] \[Needs model/hardware\] | Requires jax; Warp requires CUDA |
| Filament rendering, USD export | \[Implemented\] \[Unverified\] | New code / optional dependencies |
| Task / Reward / Success / Benchmark | \[Docs/Interface only\] (does not exist) | Must be built in-house, or follow dm_control / Gymnasium (external repositories) |
| Robot assets (Menagerie) | \[Docs/Interface only\] | Not in the repository; licenses must be checked one by one |
