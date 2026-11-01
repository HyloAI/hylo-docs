"""The diagrams of the docs site, as SVG (docs/assets/diagrams/*.svg).

    uv run python docs/mkdocs/figures/diagrams.py            # from the docs repository

Each diagram is laid out by hand below (coordinates in a 960-unit-wide view box); this file only saves repeating the
SVG boilerplate. Drawn on white: the site shows them on a light card in dark mode.

Style rules, so the figures stay readable at page width:
- short labels (five words at most), no subtitles under a box title, no legends, footnotes or code identifiers;
- text at least 15px in the 960-wide view box;
- one accent colour (TEAL) on neutral greys.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "docs" / "assets" / "diagrams"
FONT = "IBM Plex Sans, Helvetica, Arial, sans-serif"   # inside <img> the viewer's system font: leave room
TEAL, TEAL_BG, TEAL_SOFT = "#0d5c63", "#e3f0f1", "#b8d9dc"
INK, MUTED, LINE, PANEL = "#1e293b", "#475569", "#94a3b8", "#f1f5f9"
WHITE = "#ffffff"

STYLE = f"""
  text {{ font-family: {FONT}; fill: {INK}; }}
  .n {{ font-size: 17px; font-weight: 600; }}
  .e {{ font-size: 15px; fill: {MUTED}; paint-order: stroke; stroke: {WHITE}; stroke-width: 5px;
        stroke-linejoin: round; }}
  .h {{ font-size: 18px; font-weight: 700; }}
  .g {{ font-size: 17px; font-weight: 700; fill: {TEAL}; }}
"""


class SVG:
    def __init__(self, w: int, h: int, title: str, desc: str) -> None:
        self.w, self.h, self.parts = w, h, []
        self.title, self.desc = title, desc

    def add(self, s: str) -> None:
        self.parts.append(s)

    def rect(self, x, y, w, h, fill=WHITE, stroke=LINE, rx=10, dash=None, sw=1.5):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" '
                 f'stroke-width="{sw}"{d}/>')

    def text(self, x, y, s, cls="n", anchor="middle", fill=None):
        f = f' style="fill:{fill}"' if fill else ""             # style: the class's fill would win
        self.add(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}"{f}>{escape(s)}</text>')

    def node(self, x, y, w, h, label, *, accent=False, fill=None, stroke=None, dash=None, rx=10):
        """A box with a centred label; '\\n' in the label breaks the line."""
        self.rect(x, y, w, h, fill or (TEAL if accent else WHITE), stroke or (TEAL if accent else LINE),
                  rx=rx, dash=dash)
        lines = label.split("\n")
        lh = 21
        top = y + h / 2 - (len(lines) - 1) * lh / 2 + 6
        for i, line in enumerate(lines):
            self.text(x + w / 2, top + i * lh, line, "n", fill=WHITE if accent else None)

    def arrow(self, pts, color=MUTED, dash=None, both=False, sw=2):
        d = "M" + " L".join(f"{x},{y}" for x, y in pts)
        self.path(d, color, dash, both, sw)

    def path(self, d, color=MUTED, dash=None, both=False, sw=2, head=True):
        m = f' marker-end="url(#a-{color[1:]})"' if head else ""
        if both:
            m += f' marker-start="url(#a-{color[1:]})"'
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{ds}{m}/>')

    def label(self, x, y, s, anchor="middle", fill=None):
        """An edge label: grey, with a white halo so it stays legible over lines."""
        self.text(x, y, s, "e", anchor, fill)

    def group(self, x1, x2, y, s, below=False):
        """A stage name over (or under) a group of boxes: accent text and a thin accent rule."""
        self.add(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{TEAL}" stroke-width="2"/>')
        self.text(x1, y + 24 if below else y - 10, s, "g", "start")

    def save(self, name: str) -> Path:
        markers = "".join(
            f'<marker id="a-{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
            f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
            for c in (MUTED, TEAL, INK))
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" '
               f'height="{self.h}" role="img" aria-labelledby="title desc">\n'
               f'<title id="title">{escape(self.title)}</title>\n<desc id="desc">{escape(self.desc)}</desc>\n'
               f'<defs><style>{STYLE}</style>{markers}</defs>\n'
               f'<rect width="{self.w}" height="{self.h}" fill="{WHITE}"/>\n' + "\n".join(self.parts) + "\n</svg>\n")
        OUT.mkdir(parents=True, exist_ok=True)
        p = OUT / f"{name}.svg"
        p.write_text(svg)
        return p


# ---------------------------------------------------------------- 1. architecture: the data flow
def architecture() -> Path:
    s = SVG(960, 440, "How data flows through Hylo",
            "Run: an experiment produces a run with its traces. Measure: an evaluation protocol scores runs into a "
            "scorecard. Improve: a learner turns runs into an artifact, which becomes a candidate, and the gate "
            "decides. Deploy: the promoted active version runs on a workcell, whose episodes come back as runs.")
    top, bot, h = 96, 296, 64
    # Run and Measure
    s.group(40, 490, 62, "Run")
    s.group(580, 760, 62, "Measure")
    s.node(40, top, 170, h, "Experiment")
    s.node(300, top, 190, h, "Run and traces")
    s.node(580, top, 180, h, "Scorecard")
    s.arrow([(212, top + h / 2), (296, top + h / 2)])
    s.arrow([(492, top + h / 2), (576, top + h / 2)])
    # Improve and Deploy
    xs, w = [26, 218, 410, 602, 794], 140
    names = ["Artifact", "Candidate", "Gate", "Active\nversion", "Workcell"]
    for x, n in zip(xs, names):
        s.node(x, bot, w, h, n, accent=n == "Gate")
    for a, b in zip(xs, xs[1:]):
        s.arrow([(a + w + 2, bot + h / 2), (b - 4, bot + h / 2)])
    s.group(26, 550, 392, "Improve", below=True)
    s.group(602, 934, 392, "Deploy", below=True)
    # runs feed learning; workcell episodes come back as runs
    s.arrow([(350, top + h + 2), (350, 228), (96, 228), (96, bot - 4)], TEAL)
    s.label(223, 220, "learn")
    s.arrow([(864, bot - 2), (864, 228), (440, 228), (440, top + h + 4)], TEAL)
    s.label(652, 220, "episodes become runs")
    return s.save("architecture")


# ---------------------------------------------------------------- 2. repositories
def repositories() -> Path:
    s = SVG(960, 440, "Hylo repositories and how they depend on each other",
            "bench, serve, studio and plugins each depend only on the harness and never on each other. serve depends "
            "on hylo-core alone, so a robot computer installs little. docs and the deployments template hold no code.")
    leaves = ["hylo-bench", "hylo-serve", "hylo-studio", "hylo-plugins"]
    xs, w = [40, 262, 484, 706], 200
    for x, n in zip(xs, leaves):
        s.node(x, 36, w, 60, n)
    s.rect(40, 170, 866, 150, TEAL_BG, TEAL, rx=14)
    s.text(62, 204, "hylo-harness", "h", "start", fill=TEAL)
    s.node(262, 232, 200, 60, "hylo-core", accent=True)
    s.node(560, 232, 320, 60, "Packages and adapters")
    s.arrow([(558, 262), (466, 262)])
    for x, n in zip(xs, leaves):
        cx = x + w / 2
        if n == "hylo-serve":
            s.arrow([(cx, 98), (cx, 228)], TEAL)
            s.label(cx + 12, 150, "hylo-core only", "start", fill=TEAL)
        else:
            s.arrow([(cx, 98), (cx, 166)])
    s.text(40, 386, "No code", "h", "start", fill=MUTED)
    s.node(160, 356, 200, 50, "hylo-docs", fill=PANEL, dash="5 4")
    s.node(390, 356, 280, 50, "Deployments template", fill=PANEL, dash="5 4")
    return s.save("repositories")


# ---------------------------------------------------------------- 3. episode loop
def episode_loop() -> Path:
    s = SVG(960, 420, "One episode loop, two timings",
            "In sync mode the world waits while the policy computes each chunk. In realtime mode the robot keeps "
            "moving: the next chunk is computed while the current one runs, and the robot holds until the first "
            "chunk arrives.")
    x0, cw, rh = 170, 42, 34                      # 18 steps, 34-high rows

    def block(a, b, y, label="", kind="act"):
        x, w = x0 + a * cw + 2, (b - a) * cw - 4
        if kind == "policy":
            s.rect(x, y, w, rh, TEAL, TEAL, rx=6)
        elif kind == "wait":
            s.rect(x, y, w, rh, WHITE, LINE, rx=6, dash="4 4")
        elif kind == "hold":
            s.rect(x, y, w, rh, PANEL, LINE, rx=6)
        else:
            s.rect(x, y, w, rh, TEAL_BG, TEAL, rx=6)
        if label:
            s.text(x + w / 2, y + rh / 2 + 6, label, "e" if kind == "wait" else "n",
                   fill=MUTED if kind in ("wait", "hold") else None)

    def lane(y, title, calls, robot):
        s.text(30, y, title, "h", "start")
        py, ry = y + 22, y + 82
        s.text(30, py + rh / 2 + 6, "Policy", "n", "start", fill=MUTED)
        s.text(30, ry + rh / 2 + 6, "Robot", "n", "start", fill=MUTED)
        for a, b in calls:
            block(a, b, py, kind="policy")
            if b < 18:
                s.arrow([(x0 + b * cw, py + rh + 2), (x0 + b * cw, ry - 4)], TEAL)
        for a, b, label, kind in robot:
            block(a, b, ry, label, kind)

    lane(36, "Sync: the world waits", [(0, 2), (6, 8), (12, 14)],
         [(0, 2, "waits", "wait"), (2, 6, "chunk 1", "act"), (6, 8, "", "wait"), (8, 12, "chunk 2", "act"),
          (12, 14, "", "wait"), (14, 18, "chunk 3", "act")])
    lane(210, "Realtime: the robot keeps moving", [(0, 3), (4, 7), (8, 11), (12, 15)],
         [(0, 3, "hold", "hold"), (3, 7, "chunk 1", "act"), (7, 11, "chunk 2", "act"), (11, 15, "chunk 3", "act"),
          (15, 18, "chunk 4", "act")])
    s.arrow([(x0, 380), (x0 + 18 * cw + 10, 380)])
    s.label(x0 + 18 * cw + 6, 404, "time", "end")
    return s.save("episode-loop")


# ---------------------------------------------------------------- 4. improvement loop
def improvement_loop() -> Path:
    s = SVG(960, 380, "One improvement cycle",
            "A campaign cycle: start from the parent, diagnose its failures, generate candidates, screen them, "
            "confirm the best at the gate, approve, and promote; the promoted version is the next cycle's parent. "
            "Every candidate is archived, and generators can read the archive.")
    w, h, top, bot = 150, 64, 40, 270
    cx = [150, 370, 590, 810]
    for c, n in zip(cx, ["Parent", "Diagnose", "Generate", "Screen"]):
        s.node(c - w / 2, top, w, h, n)
    for c, n in zip(cx[1:], ["Promote", "Approve", "Gate"]):
        s.node(c - w / 2, bot, w, h, n, accent=n == "Gate")
    for a, b in zip(cx, cx[1:]):
        s.arrow([(a + w / 2 + 2, top + h / 2), (b - w / 2 - 4, top + h / 2)], TEAL)
        if a > cx[0]:
            s.arrow([(b - w / 2 - 2, bot + h / 2), (a + w / 2 + 4, bot + h / 2)], TEAL)
    s.arrow([(810, top + h + 2), (810, bot - 4)], TEAL)                          # screen -> gate
    s.arrow([(cx[1] - w / 2 - 2, bot + h / 2), (150, bot + h / 2), (150, top + h + 4)], TEAL)   # promote -> parent
    s.label(162, 192, "next cycle", "start", fill=TEAL)
    # the archive: every verdict is kept, generators read it
    s.node(530, 166, 120, 46, "Archive", fill=PANEL)
    s.arrow([(734, bot - 2), (654, 198)], MUTED, dash="5 4")
    s.arrow([(590, 164), (590, top + h + 4)], MUTED, dash="5 4")
    s.label(602, 140, "past results", "start")
    return s.save("improvement-loop")


# ---------------------------------------------------------------- 5. splits
def splits() -> Path:
    s = SVG(960, 216, "The four splits and who reads each",
            "A benchmark's episodes are split four ways: search (40 percent) is read by diagnosis and generators; "
            "search_val (20 percent) by screening and learners; gate (20 percent) by the gate; heldout (20 percent) "
            "only for the report to the approver.")
    x, y, h, unit = 40, 40, 60, 176
    bands = [("search", 2, TEAL_BG, None, "Diagnosis and\ngenerators"),
             ("search_val", 1, TEAL_BG, None, "Screening and\nlearners"),
             ("gate", 1, TEAL, WHITE, "The gate"),
             ("heldout", 1, PANEL, None, "Report to\nthe approver")]
    for name, n, fill, color, reader in bands:
        w = n * unit
        s.rect(x + 2, y, w - 4, h, fill, TEAL if fill != PANEL else LINE, rx=8)
        s.text(x + w / 2, y + h / 2 + 6, name, "n", fill=color)
        s.arrow([(x + w / 2, y + h + 4), (x + w / 2, y + h + 40)])
        for i, line in enumerate(reader.split("\n")):
            s.text(x + w / 2, y + h + 66 + i * 22, line, "n")
        x += w
    return s.save("splits")


# ---------------------------------------------------------------- 6. store
def store() -> Path:
    s = SVG(960, 400, "The run and artifact store",
            "In one store, every run and artifact has an id. An artifact records the runs it was built from and "
            "campaigns refer to runs and artifacts. A config, outside the store, names an artifact by id. "
            "Between machines, the workstation pulls runs from the robot computer and pushes artifacts to the GPU box.")
    s.rect(20, 20, 560, 270, TEAL_BG, TEAL, rx=14)
    s.text(42, 56, "One store", "h", "start", fill=TEAL)
    # runs as a small stack
    s.rect(64, 76, 170, 60, WHITE, LINE, rx=10)
    s.rect(57, 83, 170, 60, WHITE, LINE, rx=10)
    s.node(50, 90, 170, 60, "Runs")
    s.node(360, 90, 180, 60, "Artifact")
    s.node(50, 206, 170, 60, "Campaign")
    s.arrow([(358, 120), (238, 120)])
    s.label(298, 108, "built from")
    s.arrow([(135, 204), (135, 154)])
    s.label(147, 186, "refers to", "start")
    s.arrow([(222, 214), (358, 152)])
    # a config is not in the store: it names an artifact by id
    s.node(360, 326, 180, 60, "Config")
    s.arrow([(450, 324), (450, 154)])
    s.label(462, 240, "names by id", "start")

    s.text(620, 56, "Between machines", "h", "start", fill=TEAL)
    mx, mw, mh = 640, 280, 60
    s.node(mx, 90, mw, mh, "Robot computer", fill=PANEL)
    s.node(mx, 200, mw, mh, "Workstation", fill=PANEL, stroke=TEAL)
    s.node(mx, 310, mw, mh, "GPU box", fill=PANEL)
    s.arrow([(780, 152), (780, 196)], TEAL)
    s.label(792, 180, "pull runs", "start")
    s.arrow([(780, 262), (780, 306)], TEAL)
    s.label(792, 290, "push artifacts", "start")
    return s.save("store")


# ---------------------------------------------------------------- 7. deployment
def deployment() -> Path:
    s = SVG(960, 510, "Deployment topology",
            "The workstation runs Studio and holds the store. The robot computer runs the workcell, with the episode "
            "loop and the safety shield, and drives the robot arm. A GPU box runs the policy server, which serves the "
            "promoted version. Studio talks to the workcell over HTTP, the workcell to the policy server over a "
            "WebSocket, and the workcell's runs are copied to the store.")

    def machine(x, y, w, h, name):
        s.rect(x, y, w, h, PANEL, LINE, rx=14)
        s.text(x + 20, y + 32, name, "h", "start")

    machine(20, 80, 270, 260, "Workstation")
    s.node(45, 130, 220, 60, "Store")
    s.node(45, 240, 220, 60, "Studio")

    machine(345, 80, 270, 260, "Robot computer")
    s.rect(370, 125, 220, 195, WHITE, TEAL, rx=10)
    s.text(480, 154, "Workcell", "n", fill=TEAL)
    s.node(390, 172, 180, 52, "Episode loop", fill=TEAL_BG, stroke=TEAL)
    s.node(390, 240, 180, 52, "Safety shield", fill=TEAL_BG, stroke=TEAL)

    machine(670, 80, 270, 140, "GPU box")
    s.node(695, 130, 220, 60, "Policy server")

    s.node(380, 420, 200, 60, "Robot arm", fill=PANEL, stroke=INK)

    s.arrow([(368, 160), (269, 160)], TEAL)                 # workcell -> store
    s.label(318, 148, "runs")
    s.arrow([(267, 270), (366, 270)], TEAL)                 # studio -> workcell
    s.label(318, 258, "HTTP")
    s.arrow([(594, 160), (691, 160)], TEAL, both=True)      # workcell <-> policy server
    s.label(642, 148, "WebSocket")
    s.arrow([(480, 322), (480, 416)], INK)                  # workcell -> arm
    s.label(492, 380, "actions", "start")
    s.arrow([(230, 128), (230, 44), (850, 44), (850, 126)], TEAL, dash="6 5")    # store -> policy server
    s.label(540, 36, "promoted version")
    return s.save("deployment")


if __name__ == "__main__":
    for f in (architecture, repositories, episode_loop, improvement_loop, splits, store, deployment):
        print(f())
