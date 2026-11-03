"""The diagrams of the docs site, as SVG in a light and a dark version (docs/assets/diagrams/<name>-{light,dark}.svg).

    uv run --no-project --with fonttools --with uharfbuzz python docs/mkdocs/figures/diagrams.py   # from the workspace

Drawn with the README art's engine (readme_art.py: text as Inter outlines, the site's graphite, paper and cinnabar),
so a diagram looks the same in every browser and matches the README figures. Each diagram is laid out by hand below,
in a 960-unit-wide view box. Pages show the version that matches the site's colour scheme:

    ![Alt text](../assets/diagrams/store-light.svg){ .hylo-diagram .only-light }
    ![Alt text](../assets/diagrams/store-dark.svg){ .hylo-diagram .only-dark }

Style rules, so the figures stay readable at page width:
- short labels (five words at most), no subtitles under a box title, no legends, footnotes or code identifiers;
- text at least 15px in the 960-wide view box;
- one accent colour (cinnabar) on neutral greys.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from glance import architecture_glance, at_a_glance, chips, control_modes, model_and_robot  # noqa: E402
from readme_art import (THEMES, Doc, Repo, bench_flow, deployments_sync, improvement_loop as hylo_loop,  # noqa: E402
                        stack_map, studio_plane)

OUT = Path(__file__).resolve().parents[2] / "docs" / "assets" / "diagrams"

KINDS = {  # fill, stroke, text, dash
    "plain": ("surface", "line2", "ink", None),
    "soft": ("accent_soft", "accent", "ink", None),
    "accent": ("accent", "accent", "accent_ink", None),
    "kernel": ("kernel", "kernel", "kernel_ink", None),
    "panel": ("sunk", "line2", "ink", None),
    "ghost": ("sunk", "line2", "muted", "5 4"),
}


def node(d: Doc, x, y, w, h, label, kind="plain", stroke=None, rx=12, size=17) -> None:
    """A box with a centred label; '\\n' in the label breaks the line."""
    fill, st, ink, dash = KINDS[kind]
    d.rect(x, y, w, h, fill, stroke or st, rx=rx, sw=1.8 if stroke else 1.5, dash=dash)
    lines = label.split("\n")
    lh = size + 5
    top = y + h / 2 - (len(lines) - 1) * lh / 2 + size * 0.36
    for i, line in enumerate(lines):
        d.text(x + w / 2, top + i * lh, line, "sb", size, ink, anchor="middle")


def group(d: Doc, x1, x2, y, s, below=False) -> None:
    """A stage name over (or under) a group of boxes: accent text and a thin accent rule."""
    d.add(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{d.c("accent")}" stroke-width="2"/>')
    d.text(x1, y + 26 if below else y - 12, s, "b", 18, "accent")


# ---------------------------------------------------------------- 1. architecture: the data flow
def architecture(T: dict) -> Doc:
    d = Doc(960, 440, T, "How data flows through Hylo",
            "Run: an experiment produces a run with its traces. Verify: an evaluation protocol scores runs into a "
            "scorecard. Improve: a learner turns runs into an artifact, which becomes a candidate. Verify: the gate "
            "decides. Deploy: the promoted active version runs on a workcell, whose episodes come back as runs.")
    d.card()
    top, bot, h = 96, 296, 64
    group(d, 40, 490, 62, "Run")
    group(d, 580, 760, 62, "Verify")
    node(d, 40, top, 170, h, "Experiment")
    node(d, 300, top, 190, h, "Run and traces")
    node(d, 580, top, 180, h, "Scorecard", "soft")
    d.arrow([(212, top + h / 2), (296, top + h / 2)])
    d.arrow([(492, top + h / 2), (576, top + h / 2)])
    xs, w = [26, 218, 410, 602, 794], 140
    for x, n in zip(xs, ["Artifact", "Candidate", "Gate", "Active\nversion", "Workcell"]):
        node(d, x, bot, w, h, n, "accent" if n == "Gate" else "plain")
    for a, b in zip(xs, xs[1:]):
        d.arrow([(a + w + 2, bot + h / 2), (b - 4, bot + h / 2)])
    group(d, 26, 358, 392, "Improve", below=True)
    group(d, 410, 550, 392, "Verify", below=True)
    group(d, 602, 934, 392, "Deploy", below=True)
    d.arrow([(350, top + h + 2), (350, 228), (96, 228), (96, bot - 4)], "accent")
    d.label(223, 233, "learn", fill="accent", size=15)
    d.arrow([(864, bot - 2), (864, 228), (440, 228), (440, top + h + 4)], "accent")
    d.label(652, 233, "episodes become runs", fill="accent", size=15)
    return d


def strategy_development(T: dict) -> Doc:
    d = Doc(960, 330, T, "Robot skill development through task programs",
            "A task requirement and robot tools produce a program. The program enters the same execution kernel "
            "as an existing policy. Runs provide task validation. A baseline comparison is a separate step for "
            "an improvement claim, followed by the campaign gate and versioned reuse.")
    d.card()
    node(d, 28, 40, 210, 64, "Skill goal")
    node(d, 300, 40, 270, 64, "Robot tools and code", "soft")
    node(d, 632, 40, 220, 64, "Program")
    d.arrow([(240, 72), (296, 72)], "accent")
    d.arrow([(572, 72), (628, 72)], "accent")
    node(d, 28, 204, 210, 64, "Existing policy")
    node(d, 300, 204, 270, 64, "Shared execution", "kernel")
    node(d, 632, 204, 300, 64, "Runs and validation", "soft")
    d.arrow([(240, 236), (296, 236)], "accent")
    d.arrow([(742, 106), (742, 154), (436, 154), (436, 200)], "accent", rounded=12)
    d.arrow([(572, 236), (628, 236)], "accent")
    return d


# ---------------------------------------------------------------- 2. repositories
def repositories(T: dict) -> Doc:
    d = Doc(960, 440, T, "Hylo repositories and how they depend on each other",
            "bench, serve, studio and plugins each depend only on the harness and never on each other. serve depends "
            "on hylo-core alone, so a robot computer installs little. docs and the deployments template hold no code.")
    d.card()
    leaves = ["hylo-bench", "hylo-serve", "hylo-studio", "hylo-plugins"]
    xs, w = [40, 262, 484, 706], 200
    for x, n in zip(xs, leaves):
        node(d, x, 36, w, 60, n)
    d.rect(40, 170, 866, 150, "accent_soft", "accent", rx=16)
    d.text(62, 206, "hylo-harness", "b", 18, "accent")
    node(d, 262, 232, 200, 60, "hylo-core", "kernel")
    node(d, 560, 232, 320, 60, "Packages and adapters")
    d.arrow([(558, 262), (466, 262)])
    for x, n in zip(xs, leaves):
        cx = x + w / 2
        if n == "hylo-serve":
            d.arrow([(cx, 98), (cx, 228)], "accent")
            d.label(cx + 12, 140, "hylo-core only", "start", fill="accent", size=15)
        else:
            d.arrow([(cx, 98), (cx, 166)])
    d.text(40, 387, "No code", "b", 18, "muted")
    node(d, 160, 356, 200, 50, "hylo-docs", "ghost")
    node(d, 390, 356, 280, 50, "Deployments template", "ghost")
    return d


# ---------------------------------------------------------------- 3. episode loop
def episode_loop(T: dict) -> Doc:
    d = Doc(960, 420, T, "One episode loop, two timings",
            "In sync mode the world waits while the policy computes each chunk. In realtime mode the robot keeps "
            "moving: the next chunk is computed while the current one runs, and the robot holds until the first "
            "chunk arrives.")
    d.card()
    x0, cw, rh = 170, 42, 34

    def block(a, b, y, label="", kind="act"):
        x, w = x0 + a * cw + 2, (b - a) * cw - 4
        style = {"policy": ("accent", "accent", None), "wait": ("bg", "line2", "4 4"),
                 "hold": ("sunk", "line2", None), "act": ("accent_soft", "accent", None)}[kind]
        d.rect(x, y, w, rh, style[0], style[1], rx=8, sw=1.4, dash=style[2])
        if label:
            muted = kind in ("wait", "hold")
            d.text(x + w / 2, y + rh / 2 + 5.5, label, "r" if muted else "sb", 15.5, "muted" if muted else "ink",
                   anchor="middle")

    def lane(y, title, calls, robot):
        d.text(30, y, title, "b", 18, "ink")
        py, ry = y + 22, y + 82
        d.text(30, py + rh / 2 + 6, "Policy", "sb", 16, "muted")
        d.text(30, ry + rh / 2 + 6, "Robot", "sb", 16, "muted")
        for a, b in calls:
            block(a, b, py, kind="policy")
            if b < 18:
                d.arrow([(x0 + b * cw, py + rh + 2), (x0 + b * cw, ry - 4)], "accent", 1.8)
        for a, b, label, kind in robot:
            block(a, b, ry, label, kind)

    lane(42, "Sync: the world waits", [(0, 2), (6, 8), (12, 14)],
         [(0, 2, "waits", "wait"), (2, 6, "chunk 1", "act"), (6, 8, "", "wait"), (8, 12, "chunk 2", "act"),
          (12, 14, "", "wait"), (14, 18, "chunk 3", "act")])
    lane(214, "Realtime: the robot keeps moving", [(0, 3), (4, 7), (8, 11), (12, 15)],
         [(0, 3, "hold", "hold"), (3, 7, "chunk 1", "act"), (7, 11, "chunk 2", "act"), (11, 15, "chunk 3", "act"),
          (15, 18, "chunk 4", "act")])
    d.arrow([(x0, 380), (x0 + 18 * cw + 10, 380)], "muted", 1.6)
    d.text(x0 + 18 * cw + 10, 404, "time", "m", 15, "muted", anchor="end")
    return d


# ---------------------------------------------------------------- 4. improvement cycle
def improvement_cycle(T: dict) -> Doc:
    d = Doc(960, 380, T, "One improvement cycle",
            "A campaign cycle: start from the parent, diagnose its failures, generate candidates, screen them, "
            "confirm the best at the gate, approve, and promote; the promoted version is the next cycle's parent. "
            "Every candidate is archived, and generators can read the archive.")
    d.card()
    w, h, top, bot = 150, 64, 40, 270
    cx = [150, 370, 590, 810]
    for c, n in zip(cx, ["Parent", "Diagnose", "Generate", "Screen"]):
        node(d, c - w / 2, top, w, h, n)
    for c, n in zip(cx[1:], ["Promote", "Approve", "Gate"]):
        node(d, c - w / 2, bot, w, h, n, "accent" if n == "Gate" else "plain")
    for a, b in zip(cx, cx[1:]):
        d.arrow([(a + w / 2 + 2, top + h / 2), (b - w / 2 - 4, top + h / 2)], "accent")
        if a > cx[0]:
            d.arrow([(b - w / 2 - 2, bot + h / 2), (a + w / 2 + 4, bot + h / 2)], "accent")
    d.arrow([(810, top + h + 2), (810, bot - 4)], "accent")
    d.arrow([(cx[1] - w / 2 - 2, bot + h / 2), (150, bot + h / 2), (150, top + h + 4)], "accent", rounded=14)
    d.label(164, 192, "next cycle", "start", fill="accent", size=15)
    node(d, 530, 166, 120, 46, "Archive", "panel", size=16)
    d.arrow([(734, bot - 2), (654, 200)], "muted", dash="5 4")
    d.arrow([(590, 164), (590, top + h + 4)], "muted", dash="5 4")
    d.label(604, 140, "past results", "start", size=15)
    return d


# ---------------------------------------------------------------- 5. splits
def splits(T: dict) -> Doc:
    d = Doc(960, 224, T, "The four splits and who reads each",
            "A benchmark's episodes are split four ways: search (40 percent) is read by diagnosis and generators; "
            "search_val (20 percent) by screening and learners; gate (20 percent) by the gate; heldout (20 percent) "
            "only for the report to the approver.")
    d.card()
    x, y, h, unit = 40, 36, 60, 176
    bands = [("search", 2, "soft", "Diagnosis and\ngenerators"), ("search_val", 1, "soft", "Screening and\nlearners"),
             ("gate", 1, "accent", "The gate"), ("heldout", 1, "panel", "Report to\nthe approver")]
    for name, n, kind, reader in bands:
        w = n * unit
        node(d, x + 2, y, w - 4, h, name, kind, rx=10)
        d.arrow([(x + w / 2, y + h + 4), (x + w / 2, y + h + 38)], "muted", 1.6)
        for i, line in enumerate(reader.split("\n")):
            d.text(x + w / 2, y + h + 66 + i * 22, line, "m", 16, "muted", anchor="middle")
        x += w
    return d


# ---------------------------------------------------------------- 6. store
def store(T: dict) -> Doc:
    d = Doc(960, 400, T, "The run and artifact store",
            "In one store, every run and artifact has an id. An artifact records the runs it was built from and "
            "campaigns refer to runs and artifacts. A config, outside the store, names an artifact by id. "
            "Between machines, the workstation pulls runs from the robot computer and pushes artifacts to the GPU box.")
    d.card()
    d.rect(20, 20, 560, 270, "accent_soft", "accent", rx=16)
    d.text(42, 58, "One store", "b", 18, "accent")
    d.rect(64, 76, 170, 60, "surface", "line2", rx=12)
    d.rect(57, 83, 170, 60, "surface", "line2", rx=12)
    node(d, 50, 90, 170, 60, "Runs")
    node(d, 360, 90, 180, 60, "Artifact")
    node(d, 50, 206, 170, 60, "Campaign")
    d.arrow([(358, 120), (238, 120)])
    d.label(298, 108, "built from", size=15, plate="accent_soft")
    d.arrow([(135, 204), (135, 154)])
    d.label(149, 186, "refers to", "start", size=15, plate="accent_soft")
    d.arrow([(222, 214), (358, 152)])
    node(d, 360, 326, 180, 60, "Config", "panel")
    d.arrow([(450, 324), (450, 154)])
    d.label(464, 236, "names by id", "start", size=15, plate="accent_soft")
    d.text(620, 58, "Between machines", "b", 18, "accent")
    mx, mw, mh = 640, 280, 60
    node(d, mx, 90, mw, mh, "Robot computer", "panel")
    node(d, mx, 200, mw, mh, "Workstation", "panel", stroke="accent")
    node(d, mx, 310, mw, mh, "GPU box", "panel")
    d.arrow([(780, 152), (780, 196)], "accent")
    d.label(794, 180, "pull runs", "start", fill="accent", size=15)
    d.arrow([(780, 262), (780, 306)], "accent")
    d.label(794, 290, "push artifacts", "start", fill="accent", size=15)
    return d


# ---------------------------------------------------------------- 7. deployment
def deployment(T: dict) -> Doc:
    d = Doc(960, 510, T, "Deployment topology",
            "The workstation runs Studio and holds the store. The robot computer runs the workcell, with the episode "
            "loop and the safety shield, and drives the robot arm. A GPU box runs the policy server, which serves the "
            "promoted version. Studio talks to the workcell over HTTP, the workcell to the policy server over a "
            "WebSocket, and the workcell's runs are copied to the store.")
    d.card()

    def machine(x, y, w, h, name):
        d.rect(x, y, w, h, "sunk", "line2", rx=16)
        d.text(x + 20, y + 34, name, "b", 18, "ink")

    machine(20, 80, 270, 260, "Workstation")
    node(d, 45, 130, 220, 60, "Store")
    node(d, 45, 240, 220, 60, "Studio")
    machine(345, 80, 270, 260, "Robot computer")
    d.rect(370, 125, 220, 195, "surface", "accent", rx=14, sw=1.8)
    d.text(480, 156, "Workcell", "b", 17, "accent", anchor="middle")
    node(d, 390, 172, 180, 52, "Episode loop", "soft", size=16)
    node(d, 390, 240, 180, 52, "Safety shield", "accent", size=16)
    machine(670, 80, 270, 140, "GPU box")
    node(d, 695, 130, 220, 60, "Policy server")
    node(d, 380, 420, 200, 60, "Robot arm", "kernel")
    d.arrow([(368, 160), (269, 160)], "accent")
    d.label(318, 147, "runs", size=15)
    d.arrow([(267, 270), (366, 270)], "accent")
    d.label(318, 257, "HTTP", size=15)
    d.arrow([(594, 160), (691, 160)], "accent", both=True)
    d.label(642, 147, "WebSocket", size=15)
    d.arrow([(480, 322), (480, 416)], "ink", 2.2)
    d.label(494, 376, "actions", "start", size=15)
    d.arrow([(230, 128), (230, 44), (850, 44), (850, 126)], "accent", 1.8, dash="6 5", rounded=12)
    d.label(540, 50, "promoted version", fill="accent", size=15)
    return d



# ---------------------------------------------------------------- 8. concepts: the words, by step
def concept_map(T: dict) -> Doc:
    d = Doc(960, 396, T, "The main concepts, by step",
            "Run: an experiment gives a run, with one trace per episode. Improve: learners build artifacts, which "
            "candidates use. Verify: a protocol scores runs into a scorecard, and the gate decides on candidates. "
            "Deploy: the active version is served by a policy server to a workcell, whose episodes become runs.")
    d.card()
    cols = [("Run", ["Experiment", "Run", "Trace"]), ("Improve", ["Learner", "Artifact", "Candidate"]),
            ("Verify", ["Protocol", "Scorecard", "Gate"]), ("Deploy", ["Active version", "Policy server", "Workcell"])]
    w, g, y0, ph = 198, 40, 24, 290
    x0 = (960 - 4 * w - 3 * g) / 2
    for i, (head, items) in enumerate(cols):
        x = x0 + i * (w + g)
        d.rect(x, y0, w, ph, "sunk", "line2", rx=16)
        d.text(x + 20, y0 + 38, head, "b", 19, "accent")
        for j, t in enumerate(items):
            y = y0 + 62 + j * 76
            node(d, x + 16, y, w - 32, 52, t, "accent" if t == "Gate" else "plain")
            if j < 2:
                d.arrow([(x + w / 2, y + 54), (x + w / 2, y + 74)], "muted", 1.6)
        if i < 3:
            d.arrow([(x + w + 6, y0 + ph / 2), (x + w + g - 6, y0 + ph / 2)], "accent", 2.2)
    xa, xb, yb = x0 + 3 * (w + g) + w / 2, x0 + w / 2, y0 + ph + 52
    d.arrow([(xa, y0 + ph + 3), (xa, yb), (xb, yb), (xb, y0 + ph + 6)], "accent", 2, dash="7 6", rounded=16)
    d.label((xa + xb) / 2, yb + 6, "episodes become runs", fill="accent", size=16)
    return d


def episode_step(T: dict) -> Doc:
    d = Doc(960, 352, T, "One step of an episode",
            "The environment sends an observation to the agent, which asks its policy and proposes an action. The "
            "safety shield reviews it, and the executed action goes to the environment. The trace records every "
            "step.")
    d.card()
    d.rect(330, 28, 300, 124, "surface", "line2", rx=16)
    d.text(350, 60, "Agent", "b", 18, "ink")
    node(d, 360, 78, 240, 52, "Policy", "soft")
    node(d, 40, 196, 220, 64, "Environment")
    node(d, 700, 196, 220, 64, "Safety shield", "accent")
    d.arrow([(150, 194), (150, 90), (326, 90)], "muted", rounded=14)
    d.label(238, 96, "observation", size=15)
    d.arrow([(632, 90), (810, 90), (810, 192)], "accent", rounded=14)
    d.label(721, 96, "proposed action", fill="accent", size=15)
    d.arrow([(698, 228), (264, 228)], "accent", 2.2)
    d.label(480, 234, "executed action", fill="accent", size=15)
    node(d, 40, 292, 880, 40, "Trace: every step recorded", "ghost", size=16)
    for x in (150, 810):
        d.arrow([(x, 262), (x, 288)], "faint", 1.6, dash="4 4")
    return d


# ---------------------------------------------------------------- 9. safety shield
def safety_shield(T: dict) -> Doc:
    d = Doc(960, 262, T, "The safety shield",
            "Every action the agent proposes passes the finite check, the workspace guard, the configured guards and "
            "the bounds clamp before it reaches the environment. A non-finite action aborts the episode.")
    d.card()
    names = [("Agent", "plain"), ("Finite\ncheck", "soft"), ("Workspace\nguard", "soft"),
             ("Configured\nguards", "soft"), ("Bounds\nclamp", "soft"), ("Environment", "plain")]
    w, g, y, h = 124, 34, 72, 70
    x0 = (960 - 6 * w - 5 * g) / 2
    for i, (t, k) in enumerate(names):
        x = x0 + i * (w + g)
        node(d, x, y, w, h, t, k, size=16)
        if i < 5:
            d.arrow([(x + w + 4, y + h / 2), (x + w + g - 4, y + h / 2)], "accent" if 0 < i < 5 else "muted", 2)
    gx1, gx2 = x0 + (w + g), x0 + 4 * (w + g) + w
    group(d, gx1, gx2, 50, "Safety shield")
    fx = x0 + (w + g) + w / 2
    d.arrow([(fx, y + h + 2), (fx, 196)], "accent", 1.8, dash="5 4")
    d.label(fx + 12, 172, "not finite", "start", fill="accent", size=15)
    node(d, fx - 90, 200, 180, 44, "Abort episode", "accent", size=16)
    return d


# ---------------------------------------------------------------- 10. learning: runs to a sealed artifact
def learning_flow(T: dict) -> Doc:
    d = Doc(960, 306, T, "From runs to a sealed artifact",
            "A learner reads search and search_val runs and seals one artifact, recording its digest and the runs it "
            "was built from. The split guard refuses gate and held-out runs.")
    d.card()
    splits_ = [("search", "soft"), ("search_val", "soft"), ("gate", "ghost"), ("heldout", "ghost")]
    for i, (t, k) in enumerate(splits_):
        node(d, 40, 30 + i * 62, 180, 46, t, k, size=16)
    d.arrow([(222, 53), (290, 53), (290, 105), (356, 105)], "accent", rounded=12)
    d.arrow([(222, 115), (290, 115), (290, 105), (356, 105)], "accent", rounded=12)
    for y in (177, 239):
        d.arrow([(222, y), (296, y)], "faint", 1.6, dash="4 4", head=False)
    d.add(f'<line x1="300" y1="160" x2="300" y2="256" stroke="{d.c("accent")}" stroke-width="4" '
          'stroke-linecap="round"/>')
    d.text(316, 214, "split guard", "sb", 16, "accent")
    node(d, 360, 70, 200, 70, "Learner")
    node(d, 680, 70, 240, 70, "Sealed artifact", "kernel")
    d.arrow([(562, 105), (676, 105)], "accent", 2.2)
    d.label(619, 92, "seal", fill="accent", size=15)
    return d


# ---------------------------------------------------------------- 11. campaigns: the cascade
def cascade(T: dict) -> Doc:
    d = Doc(960, 330, T, "The cascade and the gate",
            "Stage 0 checks each candidate without running it. Stage 1 runs the first pairs of search_val, stage 2 "
            "all of search_val. Stage 3, the gate, confirms the best on the gate split. The held-out split is only "
            "reported.")
    d.card()
    rows = [("Stage 0", "Checks", "no runs", 640, "plain"), ("Stage 1", "Early check", "search_val", 520, "plain"),
            ("Stage 2", "Screen", "search_val", 400, "plain"), ("Stage 3", "Gate", "gate", 280, "accent"),
            ("Report", "Held-out report", "heldout", 280, "ghost")]
    for i, (stage, title, split, w, k) in enumerate(rows):
        y = 26 + i * 58
        d.text(40, y + 29, stage, "sb", 16, "muted")
        node(d, 480 - w / 2, y, w, 44, title, k, size=16.5)
        d.text(920, y + 28, split, "mono", 15, "muted", anchor="end")
    return d


# ---------------------------------------------------------------- 12. profiles: one name, each machine's venv
def runtimes(T: dict) -> Doc:
    d = Doc(960, 318, T, "Configs name runtimes",
            "A config names a runtime, such as libero-sim. Each machine's execution profile resolves the name to its "
            "own Python interpreter and environment variables, so the same config runs on every machine.")
    d.card()
    d.rect(290, 26, 380, 56, "kernel", rx=12)
    d.text(480, 60, "remote: {runtime: libero-sim}", "mono", 16, "kernel_ink", anchor="middle")
    for x, name in ((40, "Workstation"), (510, "GPU machine")):
        d.rect(x, 136, 410, 160, "sunk", "line2", rx=16)
        d.text(x + 20, 170, name, "b", 18, "ink")
        node(d, x + 20, 196, 150, 60, "Profile")
        node(d, x + 216, 196, 174, 60, "Python and\nenv vars", "soft", size=16)
        d.arrow([(x + 172, 226), (x + 212, 226)], "accent")
    d.arrow([(400, 84), (400, 110), (245, 110), (245, 132)], "muted", rounded=12)
    d.arrow([(560, 84), (560, 110), (715, 110), (715, 132)], "muted", rounded=12)
    d.label(480, 115, "same name", size=15)
    return d


# ---------------------------------------------------------------- 13. experiments: where components run
def placement(T: dict) -> Doc:
    d = Doc(960, 290, T, "Where components run",
            "An environment or an agent runs in the episode loop's process by default. It can run in a subprocess, "
            "in a named runtime's venv, or on another machine behind a WebSocket server.")
    d.card()
    d.rect(30, 26, 300, 238, "sunk", "line2", rx=16)
    d.text(50, 60, "hylo run", "mono", 16, "muted")
    node(d, 60, 116, 240, 64, "Episode loop", "accent")
    rows = [("subprocess", "Same interpreter"), ("named runtime", "Runtime's venv"), ("WebSocket", "Another machine")]
    for i, (how, where) in enumerate(rows):
        y = 34 + i * 80
        node(d, 640, y, 280, 60, where, "kernel" if i == 2 else "plain")
        d.arrow([(302, 148), (470, 148), (470, y + 30), (636, y + 30)], "accent" if i == 2 else "muted", rounded=12)
        d.label(552, y + 36, how, fill="accent" if i == 2 else "muted", size=15)
    return d


# ---------------------------------------------------------------- 14. tool-calling agents: proposal and receipt
def tool_agent_loop(T: dict) -> Doc:
    d = Doc(960, 400, T, "A tool-calling agent's loop",
            "The chat model measures with read tools and gets results back. An action goes as a proposal through the "
            "kernel and the safety shield to the environment, and the model gets a measured receipt with new images. "
            "The task's check scores the episode and is hidden from the model. Every event is in a hash-chained trace.")
    d.card()
    node(d, 40, 150, 180, 72, "Chat model")
    d.rect(282, 36, 260, 254, "sunk", "line2", rx=16)
    d.text(302, 68, "Tools", "b", 18, "ink")
    node(d, 312, 88, 200, 60, "Read tools", "soft")
    node(d, 312, 196, 200, 60, "Action tool", "accent")
    node(d, 614, 196, 150, 60, "Kernel and\nshield", "kernel", size=16)
    node(d, 800, 196, 120, 60, "Environment", size=16)
    node(d, 790, 88, 140, 60, "Task check", "ghost", size=16)
    d.text(860, 74, "hidden from model", "m", 15, "muted", anchor="middle")
    d.arrow([(222, 172), (266, 172), (266, 118), (308, 118)], "muted", both=True, rounded=12)
    d.label(266, 146, "measure", size=15)
    d.arrow([(222, 202), (266, 202), (266, 226), (308, 226)], "accent", rounded=12)
    d.arrow([(514, 226), (610, 226)], "accent", 2.2)
    d.label(562, 214, "proposal", fill="accent", size=15)
    d.arrow([(766, 226), (796, 226)], "accent", 2.2)
    d.arrow([(860, 194), (860, 152)], "faint", 1.6, dash="4 4")
    d.arrow([(860, 258), (860, 318), (130, 318), (130, 226)], "muted", rounded=14)
    d.label(480, 324, "receipt and new images", size=15)
    node(d, 40, 346, 880, 36, "Trace: hash-chained events", "ghost", size=16)
    return d


# ---------------------------------------------------------------- 17. spatial memory: write while visible
def spatial_recall(T: dict) -> Doc:
    d = Doc(960, 280, T, "Remembering what was seen",
            "While the targets are visible, the reasoner perceives them and writes them to spatial memory. Once they "
            "are hidden, it queries the memory and acts on the remembered positions.")
    d.card()
    d.rect(30, 26, 300, 150, "sunk", "line2", rx=16)
    d.text(50, 58, "Visible", "b", 18, "ink")
    d.rect(350, 26, 580, 150, "sunk", "line2", rx=16)
    d.text(370, 58, "Hidden", "b", 18, "ink")
    node(d, 60, 88, 240, 60, "Perceive and write", "soft")
    node(d, 380, 88, 220, 60, "Query memory")
    node(d, 670, 88, 230, 60, "Remembered target", "accent")
    d.arrow([(602, 118), (666, 118)], "accent", 2.2)
    node(d, 380, 206, 220, 50, "Spatial memory", "kernel", size=16.5)
    d.arrow([(180, 150), (180, 231), (376, 231)], "accent", rounded=12)
    d.label(250, 225, "write", fill="accent", size=15)
    d.arrow([(490, 204), (490, 152)], "muted")
    d.label(530, 186, "recall", size=15)
    return d


# ---------------------------------------------------------------- 18. action memory: a steered decision
def action_steer(T: dict) -> Doc:
    d = Doc(960, 300, T, "One decision with action memory",
            "The policy's own key retrieves the most similar verified segments from the bank. Outliers are dropped, "
            "the rest form a prior and a start time, and flow sampling starts from the prior while the policy still "
            "sees the current observation. With nothing usable, the policy runs unchanged.")
    d.card()
    names = [("Observation", "plain"), ("Retrieve\ntop k", "soft"), ("Drop\noutliers", "soft"),
             ("Prior and\nstart time", "soft"), ("Flow\nsampling", "accent"), ("Action\nchunk", "plain")]
    w, g, y, h = 124, 34, 110, 70
    x0 = (960 - 6 * w - 5 * g) / 2
    cx = [x0 + i * (w + g) + w / 2 for i in range(6)]
    for i, (t, k) in enumerate(names):
        node(d, x0 + i * (w + g), y, w, h, t, k, size=16)
        if i < 5:
            d.arrow([(x0 + i * (w + g) + w + 4, y + h / 2), (x0 + (i + 1) * (w + g) - 4, y + h / 2)],
                    "accent" if i else "muted", 2)
    d.label(x0 + w + g / 2, y + h / 2 - 12, "key", size=15)
    d.arrow([(cx[0], y - 2), (cx[0], 60), (cx[4], 60), (cx[4], y - 4)], "muted", rounded=12, dash="5 4")
    d.label((cx[0] + cx[4]) / 2, 66, "current observation", size=15)
    node(d, cx[1] - 75, 222, 150, 50, "Action bank", "kernel", size=16)
    d.arrow([(cx[1], 220), (cx[1], y + h + 4)], "accent")
    node(d, cx[3] - 80, 222, 160, 50, "Unchanged policy", "ghost", size=16)
    d.arrow([(cx[3], y + h + 2), (cx[3], 218)], "faint", 1.6, dash="4 4")
    d.label(cx[3] + 10, 206, "nothing usable", "start", size=15)
    return d


# ---------------------------------------------------------------- 19. skills: status follows evidence
def skill_status(T: dict) -> Doc:
    d = Doc(960, 240, T, "A skill's status",
            "A new skill is proposed. A passed gate or a successful replay verifies it; a failed gate with no gain "
            "refutes it; a gain that is not significant leaves it proposed. A verified skill that fails revalidation "
            "is deprecated.")
    d.card()
    node(d, 40, 90, 180, 60, "Proposed")
    node(d, 470, 40, 180, 60, "Verified", "accent")
    node(d, 470, 150, 180, 60, "Refuted", "ghost")
    node(d, 790, 40, 130, 60, "Deprecated", "ghost", size=16)
    d.arrow([(222, 110), (300, 110), (300, 70), (466, 70)], "accent", rounded=12)
    d.label(383, 62, "gate passed", fill="accent", size=15)
    d.arrow([(222, 130), (300, 130), (300, 180), (466, 180)], "muted", rounded=12)
    d.label(383, 172, "no gain", size=15)
    d.arrow([(652, 70), (786, 70)], "muted")
    d.label(719, 62, "fails later", size=15)
    d.text(130, 182, "not significant: retest", "m", 15, "muted", anchor="middle")
    return d


# ---------------------------------------------------------------- 20. lessons: one experience round
def experience_round(T: dict) -> Doc:
    d = Doc(960, 330, T, "One round with experience",
            "The proposer reads lessons and skill status and proposes candidates. The campaign's gate decides them and "
            "the archive records the verdicts. From the archive, skills are derived and the lessons that candidates "
            "cited are credited; a reflector adds lesson operations from development episodes.")
    d.card()
    node(d, 380, 30, 200, 60, "Proposer", "accent")
    node(d, 720, 135, 200, 60, "Campaign gate", "kernel")
    node(d, 380, 240, 200, 60, "Archive")
    node(d, 40, 135, 200, 60, "Skills and lessons", "soft", size=16.5)
    node(d, 380, 135, 200, 60, "Reflector", "ghost")
    d.arrow([(582, 60), (820, 60), (820, 131)], "accent", rounded=14)
    d.label(700, 66, "candidates", fill="accent", size=15)
    d.arrow([(820, 197), (820, 270), (584, 270)], "muted", rounded=14)
    d.label(700, 276, "verdicts", size=15)
    d.arrow([(376, 270), (140, 270), (140, 199)], "muted", rounded=14)
    d.label(258, 276, "derive, credit", size=15)
    d.arrow([(140, 131), (140, 60), (376, 60)], "accent", rounded=14)
    d.label(258, 66, "lessons, skill status", fill="accent", size=15)
    d.arrow([(376, 165), (244, 165)], "muted", dash="5 4")
    d.label(310, 158, "operations", size=15)
    return d


# ---------------------------------------------------------------- 21. memory: when it is written and read
def memory_timeline(T: dict) -> Doc:
    d = Doc(960, 340, T, "When memory is written and read",
            "During an episode, spatial facts are written while visible and memory is read at every decision. After "
            "development runs, a bank is built from verified successes. During a campaign, verdicts become skills and "
            "credit lessons, which the proposer reads. At evaluation nothing is written: banks, skills and lessons are "
            "frozen and only read.")
    d.card()
    cols = [("In an episode", 150), ("After runs", 350), ("In a campaign", 550), ("At evaluation", 750)]
    d.arrow([(150, 40), (934, 40)], "faint", 1.6)
    for name, x in cols:
        d.text(x + 90, 74, name, "sb", 17, "accent" if name == "At evaluation" else "ink", anchor="middle")
    d.text(40, 136, "Writes", "b", 17, "muted")
    d.text(40, 250, "Reads", "b", 17, "muted")
    writes = [("Spatial facts\nwhile visible", "soft"), ("Bank from\nverified successes", "soft"),
              ("Skills from verdicts,\nlesson credits", "soft"), ("Nothing", "ghost")]
    reads = [("Skills at start,\nmemory each decision", "plain"), ("Nothing", "ghost"),
             ("Lessons and skill\nstatus, by proposer", "plain"), ("Frozen memory,\nread only", "accent")]
    for (w, wk), (r, rk), (_, x) in zip(writes, reads, cols):
        node(d, x, 96, 180, 70, w, wk, size=15.5)
        node(d, x, 210, 180, 70, r, rk, size=15.5)
    d.add(f'<line x1="742" y1="92" x2="742" y2="286" stroke="{d.c("accent")}" stroke-width="3" '
          'stroke-linecap="round"/>')
    d.text(742, 312, "freeze", "sb", 15, "accent", anchor="middle")
    return d


# ---------------------------------------------------------------- 22. worlds: from language to a world
def world_layers(T: dict) -> Doc:
    d = Doc(960, 470, T, "From language to a world",
            "The chat model decides what to do and nothing else. Edits go as patches, are validated against a stage "
            "revision, and are compiled with robot packs into a MuJoCo model; a build starts a new world generation. "
            "Actions name that generation and run through controllers. What happened comes back as measured receipts "
            "and checks.")
    d.card()
    node(d, 330, 26, 300, 54, "Chat model", "accent")
    d.text(316, 58, "decides what", "m", 15, "muted", anchor="end")
    for i, t in enumerate(("Patches", "Stage revisions", "Compiled model")):
        node(d, 120, 120 + i * 80, 280, 52, t, "soft" if i == 0 else "plain", size=16.5)
    for i, t in enumerate(("Actions", "Controllers")):
        node(d, 560, 120 + i * 80, 280, 52, t, "soft" if i == 0 else "plain", size=16.5)
    node(d, 330, 360, 300, 56, "World", "kernel")
    d.arrow([(430, 82), (430, 100), (260, 100), (260, 116)], "accent", rounded=10)
    d.label(345, 106, "edit", fill="accent", size=15)
    d.arrow([(530, 82), (530, 100), (700, 100), (700, 116)], "accent", rounded=10)
    d.label(615, 106, "act", fill="accent", size=15)
    d.arrow([(260, 174), (260, 196)], "muted")
    d.label(272, 190, "validated", "start", size=15)
    d.arrow([(260, 254), (260, 276)], "muted")
    d.label(272, 270, "packs by name", "start", size=15)
    d.arrow([(260, 334), (260, 388), (326, 388)], "muted", rounded=10)
    d.label(250, 368, "new generation", "end", size=15)
    d.arrow([(700, 174), (700, 196)], "muted")
    d.label(712, 190, "bound to generation", "start", size=15)
    d.arrow([(700, 254), (700, 330), (560, 330), (560, 356)], "muted", rounded=10)
    d.label(630, 336, "simulated steps", size=15)
    d.arrow([(632, 400), (900, 400), (900, 53), (634, 53)], "accent", rounded=14)
    d.label(900, 240, "measured", fill="accent", size=15)
    d.text(480, 450, "the system decides what is valid and what happened", "m", 15, "muted", anchor="middle")
    return d


# ---------------------------------------------------------------- 24. memory: four layers of an agent
def memory_layers(T: dict) -> Doc:
    d = Doc(960, 360, T, "Memory at four layers of an agent",
            "Each kind of memory attaches to one layer of an agent: lessons to the improvement loop's proposer, once "
            "per round; skills to the agent's configuration, once per episode; spatial memory to the reasoner, at each "
            "reasoning step; action memory to the policy's sampling, at each decision.")
    d.card()
    group(d, 200, 500, 44, "Agent layer")
    group(d, 620, 900, 44, "Memory")
    rows = [("per round", "Improvement loop", "Lessons", "cited"), ("per episode", "Agent configuration", "Skills", "applied"),
            ("per step", "Reasoner", "Spatial memory", "recalled"), ("per decision", "Policy sampling", "Action memory", "biases")]
    for i, (rate, layer, mem, verb) in enumerate(rows):
        y = 70 + i * 70
        d.text(40, y + 33, rate, "m", 15, "muted")
        node(d, 200, y, 300, 52, layer, size=16.5)
        node(d, 620, y, 280, 52, mem, "soft", size=16.5)
        d.arrow([(618, y + 26), (504, y + 26)], "accent")
        d.label(560, y + 20, verb, fill="accent", size=15)
    d.arrow([(150, 72), (150, 326)], "faint", 1.6)
    d.text(160, 348, "faster, closer to the motor command", "m", 14, "muted")
    return d


# ---------------------------------------------------------------- 23. skills: from evidence to reuse
def skill_journey(T: dict) -> Doc:
    d = Doc(960, 320, T, "From evidence to reuse",
            "Improvement campaigns and research sessions add skills that passed a gate; role campaigns add recipes "
            "that a model-free replay confirmed. Agents find them in the library by instruction and tags, by "
            "similarity to the instruction, or by the reasons a goal failed.")
    d.card()
    srcs = [("Improvement campaign", "gate"), ("Research session", "gate"), ("Role campaign", "replay")]
    uses = [("Skills agent", "match"), ("Code agent", "similar"), ("World worker", "by failure")]
    for i, (s, ev) in enumerate(srcs):
        y = 40 + i * 92
        node(d, 40, y, 220, 60, s, "panel", size=16)
        d.arrow([(262, y + 30), (330, y + 30), (330, 160), (396, 160)], "muted", rounded=12)
        d.label(296, y + 16, ev, size=15)
    node(d, 400, 110, 160, 100, "Skill library", "kernel")
    for i, (u, how) in enumerate(uses):
        y = 40 + i * 92
        node(d, 720, y, 200, 60, u, size=16)
        d.arrow([(562, 160), (630, 160), (630, y + 30), (716, y + 30)], "accent", rounded=12)
        d.label(674, y + 16, how, fill="accent", size=15)
    return d


# ---------------------------------------------------------------- 25. campaigns: the improvement ladder
def improvement_ladder(T: dict) -> Doc:
    d = Doc(960, 330, T, "The improvement ladder",
            "Improvements are ordered by cost and risk. Steering settings and recovery rules need only rollouts and "
            "change nothing permanent. Learned components need training. Policy weights need hours of training and "
            "change the most. A frozen policy is improved from the bottom up; every rung goes through the same gate.")
    d.card()
    rungs = [("Policy weights", "hours of training", "accent"), ("Learned components", "training and rollouts", "soft"),
             ("Recovery rules", "rollouts only", "plain"), ("Steering settings", "rollouts only", "plain")]
    for i, (t, cost, k) in enumerate(rungs):
        y = 30 + i * 70
        node(d, 200, y, 300, 52, t, k, size=16.5)
        d.text(530, y + 32, cost, "m", 15, "muted")
    d.arrow([(150, 300), (150, 36)], "faint", 1.6)
    d.text(40, 50, "more cost,", "m", 15, "muted")
    d.text(40, 70, "more risk", "m", 15, "muted")
    node(d, 720, 100, 200, 130, "Same gate\nfor every rung", "kernel", size=16.5)
    for i in range(4):
        y = 30 + i * 70 + 26
        d.arrow([(680, y), (700, y), (700, 165), (716, 165)], "faint", 1.4, rounded=8, head=(i == 3))
    return d


# ---------------------------------------------------------------- 26. learning: three roles, three trust paths
def trust_paths(T: dict) -> Doc:
    d = Doc(960, 290, T, "Three roles, three ways to earn trust",
            "A behaviour artifact changes what the robot does and is trusted only through the gate. An instrument "
            "measures or labels and is trusted through calibration against ground truth. A proposal artifact changes "
            "what gets proposed and is trusted through outcome votes.")
    d.card()
    group(d, 40, 330, 44, "Role")
    group(d, 640, 920, 44, "Trusted through")
    rows = [("Behaviour", "changes what the robot does", "The gate", "accent"),
            ("Instrument", "measures and labels", "Calibration", "kernel"),
            ("Proposal", "changes what is proposed", "Outcome votes", "soft")]
    for i, (role, what, trust, k) in enumerate(rows):
        y = 70 + i * 70
        node(d, 40, y, 290, 52, role, "panel", size=16.5)
        d.arrow([(332, y + 26), (636, y + 26)], "muted")
        d.label(484, y + 20, what, size=15)
        node(d, 640, y, 280, 52, trust, k, size=16.5)
    return d


# ---------------------------------------------------------------- 27. architecture: the layers
def layers(T: dict) -> Doc:
    d = Doc(960, 500, T, "The layers and their boundaries",
            "The core holds the episode loop, the safety shield and the trace store. The loop asks an agent for "
            "actions and passes each through the shield to an environment, and records everything in the trace. "
            "Evaluation runs episodes on fixed splits and scores them from traces only. Improvement proposes "
            "candidates, evaluates them through the evaluation layer and promotes a version, which becomes the agent.")
    d.card()
    node(d, 100, 26, 820, 56, "Improvement: candidates, cascade, gate, versions", "soft", size=16.5)
    node(d, 100, 116, 820, 56, "Evaluation: benchmarks, splits, scorers, statistics", "soft", size=16.5)
    d.rect(100, 210, 820, 120, "sunk", "accent", rx=16, sw=1.6)
    d.text(120, 240, "Core", "b", 18, "accent")
    node(d, 180, 250, 210, 60, "Episode loop", "kernel")
    node(d, 430, 250, 190, 60, "Safety shield", "accent")
    node(d, 660, 250, 230, 60, "Trace store", "plain")
    node(d, 100, 384, 380, 90, "Agents: policies, reasoners,\nmemory, instruments", size=16.5)
    node(d, 540, 384, 380, 90, "Environments: simulators,\nrobots", size=16.5)
    d.arrow([(510, 84), (510, 112)], "muted")
    d.label(522, 102, "runs splits", "start", size=15)
    d.arrow([(285, 174), (285, 246)], "muted")
    d.label(297, 194, "episodes", "start", size=15)
    d.arrow([(775, 248), (775, 176)], "muted")
    d.label(763, 194, "scores read traces", "end", size=15)
    d.arrow([(285, 312), (285, 380)], "muted", both=True)
    d.label(297, 352, "observation, action", "start", size=15)
    d.arrow([(392, 280), (426, 280)], "accent", 2.2)
    d.arrow([(525, 312), (525, 346), (730, 346), (730, 380)], "accent", 2.2, rounded=10)
    d.label(628, 352, "approved action", fill="accent", size=15)
    d.arrow([(622, 280), (656, 280)], "faint", 1.6)
    d.arrow([(98, 54), (70, 54), (70, 429), (96, 429)], "accent", rounded=10)
    d.text(16, 226, "active", "m", 14, "accent")
    d.text(16, 244, "version", "m", 14, "accent")
    return d


# ---------------------------------------------------------------- the home page and Physical RSI: the loop
def physical_rsi(T: dict) -> Doc:
    d = Doc(960, 318, T, "The Physical RSI loop",
            "Build worlds, run tasks, improve, verify candidates and deploy approved versions. Active versions feed "
            "later runs, and run outcomes can guide new worlds. Failed candidates go back to Improve. Campaigns "
            "connect proposals to gates, and Serve provides model serving across the loop.")
    d.card()
    stages = [("Build", ["Worlds", "Data"], 152), ("Run", ["Policies", "Agents"], 152),
              ("Improve", ["Training", "Memory", "Programs", "Skills"], 200), ("Verify", ["Benchmarks", "Gates"], 152),
              ("Deploy", ["Versions", "Workcells"], 152)]
    gap, y, h = 26, 62, 112
    xs, x = [], 24
    for name, parts, w in stages:
        xs.append(x)
        d.rect(x, y, w, h, "surface", "line2", rx=12)
        d.text(x + w / 2, y + 28, name, "b", 18, "ink", anchor="middle")
        chips(d, x + 10, y + 42, w - 20, parts, "line2", fill="sunk", size=14.5, h=26)
        x += w + gap
    ws = [w for _, _, w in stages]
    mid = y + 30
    d.arrow([(xs[0] + ws[0] + 3, mid), (xs[1] - 3, mid)], "accent", both=True)
    d.arrow([(xs[1] + ws[1] + 2, mid - 8), (xs[2] - 4, mid - 8)], "accent")
    d.arrow([(xs[2] + ws[2] + 2, mid - 8), (xs[3] - 4, mid - 8)], "accent")
    d.arrow([(xs[3] - 2, mid + 14), (xs[2] + ws[2] + 4, mid + 14)], "accent", dash="5 4")
    d.arrow([(xs[3] + ws[3] + 2, mid - 8), (xs[4] - 4, mid - 8)], "accent")
    d.arrow([(xs[4] + ws[4] / 2, y + h + 2), (xs[4] + ws[4] / 2, 214), (xs[1] + ws[1] / 2, 214),
             (xs[1] + ws[1] / 2, y + h + 4)], "accent", rounded=12)
    d.label((xs[4] + ws[4] / 2 + xs[1] + ws[1] / 2) / 2, 219, "active version", fill="accent", size=15)
    d.add(f'<line x1="{xs[2]}" y1="40" x2="{xs[3] + ws[3]}" y2="40" stroke="{d.c("accent")}" stroke-width="2"/>')
    d.text((xs[2] + xs[3] + ws[3]) / 2, 30, "Campaigns", "b", 15.5, "accent", anchor="middle")
    d.rect(24, 258, 912, 44, "kernel", "kernel", rx=12)
    d.text(480, 286, "Serve", "b", 17, "kernel_ink", anchor="middle")
    return d


# ---------------------------------------------------------------- the home page: the loop and the stack
def home_stack(T: dict) -> Doc:
    return stack_map(T, Repo("docs", ("hylo-", "docs"), "", set()))


DIAGRAMS = {"architecture": architecture, "strategy-development": strategy_development,
            "repositories": repositories, "episode-loop": episode_loop,
            "improvement-loop": improvement_cycle, "splits": splits, "store": store, "deployment": deployment,
            "hylo-loop": hylo_loop, "stack": home_stack, "concept-map": concept_map, "episode-step": episode_step,
            "safety-shield": safety_shield, "learning-flow": learning_flow, "cascade": cascade, "runtimes": runtimes,
            "placement": placement, "bench-flow": bench_flow, "deployments-sync": deployments_sync,
            "studio-plane": studio_plane, "tool-agent-loop": tool_agent_loop,
            "spatial-recall": spatial_recall, "action-steer": action_steer,
            "skill-status": skill_status, "experience-round": experience_round, "memory-timeline": memory_timeline,
            "world-layers": world_layers, "memory-layers": memory_layers, "skill-journey": skill_journey,
            "improvement-ladder": improvement_ladder, "trust-paths": trust_paths, "layers": layers,
            "physical-rsi": physical_rsi, "at-a-glance": at_a_glance, "control-modes": control_modes,
            "architecture-glance": architecture_glance, "model-and-robot": model_and_robot}


if __name__ == "__main__":
    for name, fn in DIAGRAMS.items():
        for theme, T in THEMES.items():
            print(fn(T).save(OUT / f"{name}-{theme}.svg"))
