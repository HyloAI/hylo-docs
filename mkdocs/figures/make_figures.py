"""Figures of the docs site made from real runs (docs/assets/figures/*.png).

    uv run --group demo python docs/mkdocs/figures/make_figures.py [--store PATH] [only ...]

Reads runs from the run and artifact store (`--store`, else this machine's profile; see `hylo store where`).
MuJoCo renders need offscreen OpenGL: MUJOCO_GL=osmesa PYOPENGL_PLATFORM=osmesa
LD_LIBRARY_PATH=~/.local/mesa/root/usr/lib/x86_64-linux-gnu (bench/scripts/install-osmesa-user.sh).

Colours: one teal for a single series; teal (candidate) and amber (parent) for the paired chart, a pair checked with
the data-viz palette validator (lightness, chroma, colour-blind separation, contrast on white).
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "docs" / "assets" / "figures"
TEAL, AMBER, REF = "#00909c", "#d97706", "#b8c2cf"
INK, MUTED, GRID = "#1f2937", "#5b6576", "#e5e9ef"
DPI = 200

plt.rcParams.update({
    "font.family": ["DejaVu Sans", "sans-serif"], "font.size": 10.5, "axes.edgecolor": GRID,
    "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED, "axes.titlesize": 12.5,
    "axes.titleweight": "bold", "axes.titlecolor": INK, "axes.titlelocation": "left", "figure.facecolor": "white",
    "axes.facecolor": "white", "savefig.facecolor": "white", "axes.spines.top": False, "axes.spines.right": False,
})


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def save(fig, name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / name
    fig.savefig(p, dpi=DPI, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    return p


# ---------------------------------------------------------------- 8. leaderboard
def leaderboard(store: Path) -> Path:
    cards = [json.loads(f.read_text()) for f in sorted((store / "policies/scorecards/mujoco-reach").glob("*.json"))]
    cards.sort(key=lambda c: c["metrics"]["success_mean"])
    fig, ax = plt.subplots(figsize=(8, 4.2))
    y = np.arange(len(cards))
    for i, c in enumerate(cards):
        m, (lo, hi) = c["metrics"]["success_mean"], c["success_ci95"]
        expert = c["policy"].startswith("expert")
        ax.barh(i, m, height=0.56, color=REF if expert else TEAL, zorder=2)
        ax.plot([lo, hi], [i, i], color=INK, lw=1.2, zorder=3, solid_capstyle="butt")
        for x in (lo, hi):
            ax.plot([x, x], [i - 0.12, i + 0.12], color=INK, lw=1.2, zorder=3)
        ax.text(min(hi, 1.0) + 0.012, i, f"{m:.0%}", va="center", ha="left", color=INK, fontsize=10)
    names = [c["policy"] + ("  (reference)" if c["policy"].startswith("expert") else "") for c in cards]
    ax.set_yticks(y, names, color=INK)
    ax.set_xlim(0, 1.08)
    ax.set_xticks([0, .25, .5, .75, 1.0], ["0%", "25%", "50%", "75%", "100%"])
    ax.xaxis.grid(True, color=GRID, lw=1, zorder=0)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    n = cards[0]["metrics"]["n_episodes"]
    ax.set_title(f"Success on mujoco-reach, {n} held-out episodes per policy")
    ax.set_xlabel("success rate (bar) with 95% Wilson interval (whiskers)")
    return save(fig, "leaderboard-mujoco-reach.png")


# ---------------------------------------------------------------- 9. campaign
def campaign(store: Path) -> Path:
    root = store / "evolve/mujoco-reach-gain"
    cfg = json.loads((root / "evolve_config.json").read_text())
    path = cfg["proposer"]["params"]["path"]
    base = cfg["experiment_overrides"][path]
    groups = []                                    # (label, parent rate, candidate rate, pairs)
    for cyc in sorted(root.glob("cycle-*")):
        rep = json.loads((cyc / "cycle_report.json").read_text())
        best = max(rep["entries"], key=lambda e: (e["verdict"] == "promoted", len(e["stages"])), default=None)
        if not best or not best["stages"]:
            continue
        kp = best["candidate"]["patch"][path]
        parent_kp = base if rep["parent_id"] is None else prev_kp
        n = cyc.name.split("-")[1].lstrip("0")
        for s in best["stages"]:
            if s["stage"] == 2:
                groups.append((f"cycle {n}\nselection\n(search_val)", s["parent_success"], s["success"], s["n_pairs"],
                               parent_kp, kp))
            if s["stage"] == 3:
                groups.append((f"cycle {n}\ngate", s["parent_success"], s["success"], s["n_pairs"], parent_kp, kp))
        if rep.get("heldout"):
            h = rep["heldout"]
            groups.append((f"cycle {n}\nheld-out\nreport", h["parent_success"], h["candidate_success"],
                           h["paired"]["n_pairs"], parent_kp, kp))
        prev_kp = kp if rep.get("promoted") else parent_kp
    fig, ax = plt.subplots(figsize=(8, 4.2))
    x = np.arange(len(groups))
    w = 0.32
    for i, (label, p, c, n, pk, ck) in enumerate(groups):
        for off, rate, color in ((-w / 2 - .02, p, AMBER), (w / 2 + .02, c, TEAL)):
            lo, hi = wilson(round(rate * n), n)
            ax.bar(i + off, rate, width=w, color=color, zorder=2)
            ax.plot([i + off, i + off], [lo, hi], color=INK, lw=1.1, zorder=3)
            ax.text(i + off, hi + .025, f"{rate:.0%}", ha="center", va="bottom", fontsize=9.5, color=INK)
        ax.text(i, -0.25, f"kp {pk:g} vs {ck:g}", ha="center", fontsize=8.5, color=MUTED, transform=ax.get_xaxis_transform())
    ax.set_xticks(x, [g[0] for g in groups], color=INK, fontsize=9.5)
    ax.tick_params(axis="x", length=0)
    ax.set_ylim(0, 1.14)
    ax.set_yticks([0, .25, .5, .75, 1.0], ["0%", "25%", "50%", "75%", "100%"])
    ax.yaxis.grid(True, color=GRID, lw=1, zorder=0)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    from matplotlib.patches import Patch

    ax.legend(handles=[Patch(color=AMBER, label="parent"), Patch(color=TEAL, label="candidate")], frameon=False,
              loc="upper left", bbox_to_anchor=(0, 1.02), ncol=2, fontsize=9.5)
    ax.set_title("Campaign mujoco-reach-gain: the controller gain, gated", pad=22)
    ax.set_ylabel("success rate, 95% Wilson interval")
    return save(fig, "campaign-mujoco-reach-gain.png")


# ---------------------------------------------------------------- 10. LIBERO frames
def libero_strip(store: Path, run: str, n_frames: int = 7, camera: str = "agentview") -> Path:
    from hylo.core.trace import TraceStore

    rd = store / run
    log = json.loads((rd / "evallog.json").read_text())
    sample = next(s for s in log["samples"] if s["status"] == "success")
    tr = TraceStore(rd).read(sample["episode_id"])
    frames = [(i, o) for i, o in enumerate(tr.of_type("observation")) if (o["payload"].get("images") or {}).get(camera) is not None]
    pick = [frames[round(k * (len(frames) - 1) / (n_frames - 1))] for k in range(n_frames)]
    instruction = pick[0][1]["payload"].get("instruction") or sample["task_id"]
    fig, axes = plt.subplots(1, n_frames, figsize=(2.0 * n_frames, 2.55))
    for ax, (i, o) in zip(axes, pick):
        img = np.asarray(o["payload"]["images"][camera], dtype=np.uint8)
        ax.imshow(img)                                 # stored upright (the LIBERO adapter rotates)
        ax.set_axis_off()
        step = (o["payload"].get("step") if isinstance(o["payload"].get("step"), int) else i)
        ax.set_title(f"step {step}", fontsize=9.5, color=MUTED, fontweight="normal", loc="center")
    fig.suptitle(f"SmolVLA on LIBERO-10: “{instruction}” — success in {sample['steps']} steps",
                 x=0.01, ha="left", fontsize=11, color=INK, fontweight="bold")
    fig.subplots_adjust(left=0.004, right=0.996, bottom=0.01, top=0.8, wspace=0.03)
    return save(fig, "libero-episode-strip.png")


# ---------------------------------------------------------------- 11. MuJoCo scenes
def mujoco_scenes() -> Path:
    import mujoco

    from hylo.core.task import TaskInstance
    from hylo.envs.mujoco.planar_reach import PlanarReachEnv, mujoco_benchmark
    from hylo.envs.mujoco.table_reach import TableReachEnv, table_benchmark

    images = []
    env = PlanarReachEnv()
    env.reset(TaskInstance(spec=mujoco_benchmark().tasks[0], seed=3))
    env.model.vis.headlight.ambient[:] = 0.45                  # the model has no lights or floor of its own
    env.model.vis.headlight.diffuse[:] = 0.6
    r = mujoco.Renderer(env.model, 480, 640)
    cam = mujoco.MjvCamera()
    cam.lookat[:] = (0.12, 0.05, 0.0)
    cam.elevation, cam.azimuth, cam.distance = -90, 90, 1.25    # from above: the arm moves in the plane
    r.update_scene(env.data, camera=cam)
    img = r.render().copy()
    img[img.max(axis=2) < 6] = (238, 241, 244)                 # empty space (black) as a light backdrop
    images.append(("mujoco.planar_reach (from above)", img))
    env.close() if hasattr(env, "close") else None
    t = TableReachEnv()
    t.reset(TaskInstance(spec=table_benchmark().tasks[0], seed=3))
    images.append(("mujoco.table_reach", t.render("front", 640, 480)))
    t.close()
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6))
    for ax, (name, img) in zip(axes, images):
        ax.imshow(img)
        ax.set_axis_off()
        ax.set_title(name, fontsize=10.5, loc="center", fontweight="bold", color=INK)
    fig.subplots_adjust(wspace=0.04)
    return save(fig, "mujoco-scenes.png")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--store", help="the run store (default: this machine's profile)")
    ap.add_argument("--libero-run", default="critic-ab/l10-ab-critic-search_val-73dc98eaf0df4917-45b6ba")
    ap.add_argument("only", nargs="*")
    a = ap.parse_args()
    if a.store:
        store = Path(a.store)
    else:
        from hylo.core.store import default_root

        store = default_root()
    jobs = {"leaderboard": lambda: leaderboard(store), "campaign": lambda: campaign(store),
            "libero": lambda: libero_strip(store, a.libero_run), "mujoco": mujoco_scenes}
    for name, job in jobs.items():
        if not a.only or name in a.only:
            print(job())


if __name__ == "__main__":
    main()
