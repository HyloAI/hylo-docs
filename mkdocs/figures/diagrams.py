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
from readme_art import THEMES, Doc, Repo, improvement_loop as hylo_loop, stack_map  # noqa: E402

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
            "Run: an experiment produces a run with its traces. Measure: an evaluation protocol scores runs into a "
            "scorecard. Improve: a learner turns runs into an artifact, which becomes a candidate, and the gate "
            "decides. Deploy: the promoted active version runs on a workcell, whose episodes come back as runs.")
    d.card()
    top, bot, h = 96, 296, 64
    group(d, 40, 490, 62, "Run")
    group(d, 580, 760, 62, "Measure")
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
    group(d, 26, 550, 392, "Improve", below=True)
    group(d, 602, 934, 392, "Deploy", below=True)
    d.arrow([(350, top + h + 2), (350, 228), (96, 228), (96, bot - 4)], "accent")
    d.label(223, 233, "learn", fill="accent", size=15)
    d.arrow([(864, bot - 2), (864, 228), (440, 228), (440, top + h + 4)], "accent")
    d.label(652, 233, "episodes become runs", fill="accent", size=15)
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


# ---------------------------------------------------------------- the home page: the loop and the stack
def home_stack(T: dict) -> Doc:
    return stack_map(T, Repo("docs", ("hylo-", "docs"), "", set()))


DIAGRAMS = {"architecture": architecture, "repositories": repositories, "episode-loop": episode_loop,
            "improvement-loop": improvement_cycle, "splits": splits, "store": store, "deployment": deployment,
            "hylo-loop": hylo_loop, "stack": home_stack}


if __name__ == "__main__":
    for name, fn in DIAGRAMS.items():
        for theme, T in THEMES.items():
            print(fn(T).save(OUT / f"{name}-{theme}.svg"))
