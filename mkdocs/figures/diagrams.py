"""The architecture diagrams of the docs site, as SVG (docs/assets/diagrams/*.svg).

    uv run python docs/mkdocs/figures/diagrams.py            # from the docs repository

Each diagram is laid out by hand below (coordinates in a 960-unit-wide view box); this file only saves repeating the
SVG boilerplate. Drawn on white: the site shows them on a light card in dark mode.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "docs" / "assets" / "diagrams"
FONT = "IBM Plex Sans, Helvetica, Arial, sans-serif"   # inside <img> the viewer's system font: leave room
MONO = "IBM Plex Mono, Menlo, Consolas, monospace"
TEAL, TEAL2, TEAL_BG = "#0d5c63", "#2a7f86", "#e6f2f3"
ORANGE, ORANGE_BG = "#c2410c", "#fdeee6"
INK, MUTED, LINE, PANEL = "#334155", "#64748b", "#cbd5e1", "#f1f5f9"

STYLE = f"""
  text {{ font-family: {FONT}; fill: {INK}; }}
  .t {{ font-size: 13px; font-weight: 600; }}
  .s {{ font-size: 11px; fill: {MUTED}; }}
  .h {{ font-size: 15px; font-weight: 700; }}
  .cap {{ font-size: 11px; font-weight: 600; letter-spacing: .06em; fill: {MUTED}; }}
  .m {{ font-family: {MONO}; font-size: 11px; }}
  .w {{ fill: #ffffff; }}
"""


class SVG:
    def __init__(self, w: int, h: int, title: str, desc: str) -> None:
        self.w, self.h, self.parts = w, h, []
        self.title, self.desc = title, desc

    def add(self, s: str) -> None:
        self.parts.append(s)

    def rect(self, x, y, w, h, fill="#fff", stroke=LINE, rx=8, dash=None, sw=1.2):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" '
                 f'stroke-width="{sw}"{d}/>')

    def text(self, x, y, s, cls="s", anchor="start", fill=None, weight=None, size=None):
        extra = (f' fill="{fill}"' if fill else "") + (f' font-weight="{weight}"' if weight else "") + \
                (f' font-size="{size}"' if size else "")
        self.add(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}"{extra}>{escape(s)}</text>')

    def box(self, x, y, w, h, title, lines=(), *, fill="#fff", stroke=LINE, tfill=None, center=True, dash=None,
            sw=1.2, lh=14, tsize=None):
        self.rect(x, y, w, h, fill, stroke, dash=dash, sw=sw)
        cx = x + w / 2 if center else x + 10
        anchor = "middle" if center else "start"
        n = len(lines)
        top = y + h / 2 - (n * lh) / 2 + 4 if n else y + h / 2 + 5
        self.text(cx, top, title, "t", anchor, fill=tfill, size=tsize)
        for i, l in enumerate(lines):
            self.text(cx, top + (i + 1) * lh, l, "s", anchor)

    def line(self, pts, color=MUTED, arrow=True, dash=None, sw=1.5):
        d = "M" + " L".join(f"{x},{y}" for x, y in pts)
        m = f' marker-end="url(#a-{color[1:]})"' if arrow else ""
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{ds}{m}/>')

    def curve(self, d, color=MUTED, arrow=True, dash=None, sw=1.5):
        m = f' marker-end="url(#a-{color[1:]})"' if arrow else ""
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{ds}{m}/>')

    def chip(self, x, y, s, fill=TEAL_BG, stroke=TEAL2, color=TEAL, mono=False, w=None):
        w = w or (len(s) * (6.6 if mono else 6.3) + 16)
        self.rect(x, y, w, 22, fill, stroke, rx=11, sw=1)
        self.text(x + w / 2, y + 15, s, "m" if mono else "s", "middle", fill=color, weight=None if mono else "600")
        return w

    def save(self, name: str) -> Path:
        markers = "".join(
            f'<marker id="a-{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
            for c in (MUTED, TEAL, TEAL2, ORANGE, INK))
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" '
               f'height="{self.h}" role="img" aria-labelledby="title desc">\n'
               f'<title id="title">{escape(self.title)}</title>\n<desc id="desc">{escape(self.desc)}</desc>\n'
               f'<defs><style>{STYLE}</style>{markers}</defs>\n'
               f'<rect width="{self.w}" height="{self.h}" fill="#ffffff"/>\n' + "\n".join(self.parts) + "\n</svg>\n")
        OUT.mkdir(parents=True, exist_ok=True)
        p = OUT / f"{name}.svg"
        p.write_text(svg)
        return p


# ---------------------------------------------------------------- 1. architecture
def architecture() -> Path:
    s = SVG(960, 660, "worldcurrent architecture",
            "Leaf repositories (bench, serve, studio, plugins) build on the harness packages, whose base is wc-core; "
            "adapters connect simulators, robots, policy stacks and LLMs.")
    s.text(30, 30, "LEAF REPOSITORIES", "cap")
    leaves = [("bench", ["protocols · scorecards", "leaderboards · suites"]),
              ("serve", ["policy server", "workcell · robots"]),
              ("studio", ["playground", "control plane · UI"]),
              ("plugins", ["examples and", "community plugins"])]
    for i, (n, l) in enumerate(leaves):
        s.box(30 + i * 172, 42, 160, 66, n, l, fill="#fff", stroke=TEAL2, tfill=TEAL)
    s.text(738, 30, "NO CODE", "cap")
    s.box(738, 42, 192, 30, "docs", fill=PANEL, stroke=LINE, dash="4 3")
    s.box(738, 78, 192, 30, "deployments-template", fill=PANEL, stroke=LINE, dash="4 3", tsize=12)
    for i in range(4):
        x = 110 + i * 172
        s.line([(x, 110), (x, 142)], TEAL2)
    s.text(738, 134, "↓ depend on the harness only", "s", fill=TEAL)

    s.rect(20, 146, 920, 352, TEAL_BG, TEAL2, rx=12)
    s.text(34, 168, "WORLDCURRENT-HARNESS (THE BASE)", "cap", fill=TEAL)
    pk = [("wc-eval", ["experiments", "benchmarks"]), ("wc-agents", ["policy runners", "steering"]),
          ("wc-policies", ["reference", "policies"]), ("wc-memory", ["action bank", "lessons, skills"]),
          ("wc-learn", ["learners", "calibration"]), ("wc-evolve", ["campaigns", "the gate"]),
          ("wc-catalog", ["queries over", "runs"]), ("cli", ["worldcurrent-cli", "wc commands"])]
    for i, (n, l) in enumerate(pk):
        s.box(34 + i * 113, 180, 105, 64, n, l, tsize=12)
    s.rect(34, 258, 892, 96, "#ffffff", TEAL, rx=10, sw=1.6)
    s.text(48, 282, "wc-core", "h", fill=TEAL)
    s.text(48, 300, "what every package shares (numpy + pydantic only)", "s")
    chips = ["contracts", "EpisodeRunner", "SafetyShield", "registry", "plugin contracts", "traces",
             "artifacts", "store ids", "profiles", "remote wire", "scorecards", "workcell API"]
    x, y = 372, 266
    for c in chips:
        w = len(c) * 7 + 16
        if x + w > 916:
            x, y = 372, y + 28
        s.chip(x, y, c, w=w)
        x += w + 6
    for i in range(8):
        x = 86 + i * 113
        s.line([(x, 246), (x, 256)], TEAL2)

    s.text(34, 380, "ADAPTERS: plugins found by name through entry points", "cap", fill=TEAL)
    ad = [("wc-policy-lerobot", "harness"), ("wc-policy-openpi", "harness"), ("wc-reasoner-llm", "harness"),
          ("wc-proposer-llm", "harness"), ("wc-data-video", "harness"), ("wc-env-mujoco", "bench"),
          ("wc-env-libero", "bench"), ("wc-env-lerobot-robot", "serve")]
    for i, (n, repo) in enumerate(ad):
        col, row = i % 4, i // 4
        s.box(34 + col * 224, 390 + row * 52, 216, 44, n, [f"in worldcurrent-{repo}"],
              stroke=TEAL2 if repo == "harness" else LINE, tsize=12, lh=13)

    s.line([(480, 500), (480, 528)], MUTED)
    s.text(490, 520, "adapters wrap", "s")
    s.text(30, 548, "OUTSIDE WORLDCURRENT", "cap")
    ext = [("LeRobot", ["SmolVLA, pi0/pi0.5", "robot drivers"]), ("openpi", ["policy server"]),
           ("Ollama", ["LLMs and VLMs"]), ("datasets", ["videos, demos"]), ("MuJoCo", ["reach, table"]),
           ("LIBERO", ["robosuite tasks"]), ("robot arms", ["SO-101, sim arm"])]
    for i, (n, l) in enumerate(ext):
        s.box(34 + i * 128, 558, 120, 58, n, l, fill=PANEL, stroke=LINE)
    s.text(930, 646, "Arrows: depends on. wc-core imports no other worldcurrent package.", "s", "end")
    return s.save("architecture")


# ---------------------------------------------------------------- 2. repositories
def repositories() -> Path:
    s = SVG(960, 560, "worldcurrent repositories and how they depend on each other",
            "bench, serve, studio and plugins depend only on the harness and never import each other; they cooperate "
            "through formats defined in wc-core. serve declares only wc-core, so a robot computer installs little.")
    leaves = [("worldcurrent-bench", ["benchmark scoring", "LIBERO / MuJoCo suites"], "harness"),
              ("worldcurrent-serve", ["policy server · workcell", "robot computer side"], "wc-core only"),
              ("worldcurrent-studio", ["playground", "control plane · UI"], "harness"),
              ("worldcurrent-plugins", ["examples, written as", "a third party would"], "harness")]
    for i, (n, l, dep) in enumerate(leaves):
        x = 30 + i * 230
        s.box(x, 30, 210, 70, n, l, stroke=TEAL2, tfill=TEAL)
        color = ORANGE if dep == "wc-core only" else TEAL2
        s.line([(x + 105, 102), (x + 105, 188)], color)
        s.rect(x + 105 - 46, 132, 92, 22, "#fff", color, rx=11, sw=1)
        s.text(x + 105, 147, dep, "s", "middle", fill=color, weight="600")
    for i in range(3):
        x = 240 + i * 230
        s.text(x + 10, 70, "✕", "t", "middle", fill=ORANGE, size=16)
    s.text(480, 120, "leaves never import each other", "s", "middle", fill=ORANGE, weight="600")

    s.rect(30, 190, 900, 210, TEAL_BG, TEAL2, rx=12)
    s.text(50, 218, "worldcurrent-harness", "h", fill=TEAL)
    s.text(272, 218, "the base: core, eval, agents, memory, learn, evolve, catalog, policies, adapters, wc", "s")
    s.rect(50, 234, 860, 150, "#fff", TEAL, rx=10, sw=1.4)
    s.text(66, 256, "FORMATS IN WC-CORE: THE ONLY WAY THE REPOSITORIES TALK TO EACH OTHER", "cap", fill=TEAL)
    fm = [("registry names", "envs, agents, policies … by name"), ("traces", "every episode, event by event"),
          ("artifacts + store ids", "artifact:<name>@<digest>"), ("active.json", "what a policy server deploys"),
          ("scorecards", "wc.scorecard/v0.1"), ("wire protocol", "msgpack-numpy over websockets"),
          ("workcell API", "wc.workcell/v0.1 over HTTP"), ("wc subcommands", "each package adds its own")]
    for i, (a, b) in enumerate(fm):
        col, row = i % 4, i // 4
        x, y = 66 + col * 210, 270 + row * 54
        s.chip(x, y, a, w=196)
        s.text(x + 98, y + 38, b, "s", "middle")

    s.text(30, 440, "NO IMPORTABLE CODE", "cap")
    s.box(30, 452, 260, 62, "worldcurrent-docs", ["this site: guides, design, RFCs,", "research, generated references"],
          fill=PANEL, dash="4 3")
    s.box(310, 452, 290, 62, "<lab>-deployments (template)", ["serve's workcell configs, calibration,",
                                                               "safety limits: per lab, private"],
          fill=PANEL, dash="4 3")
    s.box(620, 452, 140, 62, "site", ["planned"], fill="#fff", dash="2 4")
    s.text(930, 540, "harness/dev/repos.toml; checked by harness/dev/test_boundaries.py", "s", "end")
    return s.save("repositories")


# ---------------------------------------------------------------- 3. episode loop
def episode_loop() -> Path:
    s = SVG(960, 664, "One episode loop, two timings",
            "core.kernel.EpisodeRunner in sync mode (the world waits for each policy call) and realtime mode (policy "
            "calls overlap execution, stale actions are dropped, a hold action fills an empty queue).")
    x0, cw = 150, 36                                  # step grid

    def axis(y, n, label):
        s.line([(x0, y), (x0 + n * cw + 10, y)], MUTED)
        for i in range(n + 1):
            s.add(f'<line x1="{x0 + i * cw}" y1="{y - 3}" x2="{x0 + i * cw}" y2="{y + 3}" stroke="{MUTED}"/>')
            if i % 2 == 0:
                s.text(x0 + i * cw, y + 16, str(i), "s", "middle")
        s.text(x0 + n * cw + 16, y + 4, label, "s")

    def cell(i, y, label, fill, stroke, color=INK, dash=None, w=1):
        s.rect(x0 + i * cw + 2, y, cw * w - 4, 26, fill, stroke, rx=5, dash=dash, sw=1)
        if label:
            s.text(x0 + i * cw + cw * w / 2, y + 17, label, "s", "middle", fill=color, weight="600")

    # sync
    s.text(30, 34, "SYNC", "h", fill=TEAL)
    s.text(90, 34, "(default): the world waits for every policy call; a chunk runs execution_steps actions", "s")
    s.text(30, 76, "policy", "t")
    s.text(30, 116, "robot", "t")
    for k, start in enumerate((0, 6, 12)):
        cell(start, 58, f"act(o{start - 2 * k if k else 0})" if False else "policy call", TEAL_BG, TEAL2, TEAL, w=2)
        s.rect(x0 + start * cw + 2, 98, 2 * cw - 4, 26, "#fff", LINE, rx=5, dash="3 3", sw=1)
        s.text(x0 + start * cw + cw, 115, "world waits", "s", "middle")
        for j in range(4):
            if start + 2 + j < 18:
                cell(start + 2 + j, 98, f"a{j}", "#fff", TEAL2, TEAL)
    axis(150, 18, "wall time")
    s.text(30, 190, "Benchmarks score the policy alone: latency never changes an outcome.", "s")

    # realtime
    yb = 232
    s.text(30, yb, "REALTIME", "h", fill=ORANGE)
    s.text(118, yb, "the robot keeps its control rate; the next chunk is computed while the current one runs", "s")
    s.text(30, yb + 44, "policy", "t")
    s.text(30, yb + 84, "chunks", "t")
    s.text(30, yb + 154, "executed", "t")
    s.text(30, yb + 194, "shield", "t")
    s.text(30, yb + 226, "trace", "t")
    calls = [(0, 3), (5, 8), (10, 13), (15, 18)]
    for k, (req, arr) in enumerate(calls):
        s.rect(x0 + req * cw + 2, yb + 26, (arr - req) * cw - 4, 26, TEAL_BG, TEAL2, rx=5, sw=1)
        s.text(x0 + (req + arr) * cw / 2, yb + 43, f"chunk {k + 1} (o{req})", "s", "middle", fill=TEAL, weight="600")
        row = yb + 66 + (k % 2) * 34                  # chunks overlap in time: alternate rows
        for j in range(8):
            i = req + j
            if i >= 18:
                break
            if arr >= 18:                              # not arrived within the picture
                cell(i, row, "", "#fff", LINE, dash="2 3")
                continue
            stale = i < arr
            cell(i, row, "" if stale else f"{k + 1}·{j}", "#fff" if stale else TEAL_BG, LINE if stale else TEAL2,
                 TEAL, dash="2 3" if stale else None)
            if stale:
                xx = x0 + i * cw
                s.add(f'<line x1="{xx + 8}" y1="{row + 6}" x2="{xx + cw - 8}" y2="{row + 20}" stroke="{ORANGE}" '
                      f'stroke-width="1.3"/>')
        if arr < 18:
            s.line([(x0 + arr * cw, yb + 54), (x0 + arr * cw, row - 2)], TEAL2)
    executed = ["hold"] * 3 + [f"1·{j}" for j in range(3, 8)] + [f"2·{j}" for j in range(3, 8)] + \
        [f"3·{j}" for j in range(3, 8)]
    for i, e in enumerate(executed[:18]):
        if e == "hold":
            cell(i, yb + 136, "hold", ORANGE_BG, ORANGE, ORANGE)
        else:
            cell(i, yb + 136, e, "#fff", TEAL2, TEAL)
    for i in range(18):
        xx = x0 + i * cw + cw / 2
        s.add(f'<path d="M{xx - 6},{yb + 176} L{xx + 6},{yb + 176} L{xx + 6},{yb + 184} L{xx},{yb + 190} '
              f'L{xx - 6},{yb + 184} z" fill="{ORANGE_BG}" stroke="{ORANGE}" stroke-width="1"/>')
        s.add(f'<circle cx="{xx}" cy="{yb + 222}" r="3.5" fill="{TEAL2}"/>')
    axis(yb + 252, 18, "robot steps")
    notes = [("aligned merge", "chunk 2 is computed from o5 and arrives at step 8: its actions 0–2 went stale while it "
              "was computed and are dropped"),
             ("refill", "the next chunk is requested when ≤ refill_steps actions remain, earlier if recent latency "
              "says so"),
             ("hold, watchdog", "an empty queue executes the hold action; more than max_hold_steps holds in a row "
              "abort"),
             ("clock", "virtual: latency measured or fixed (latency_s), deterministic, for benchmarks; wall: a worker "
              "thread, on robots")]
    for i, (a_, b_) in enumerate(notes):
        y = yb + 292 + i * 26
        s.text(30, y, a_, "t", fill=ORANGE if i == 2 else TEAL)
        s.text(160, y, b_, "s")
    s.text(930, 650, "k·j = action j of chunk k. Every executed action passes the SafetyShield; every step is traced "
           "(both modes).", "s", "end")
    return s.save("episode-loop")


# ---------------------------------------------------------------- 4. improvement loop
def improvement_loop() -> Path:
    s = SVG(960, 600, "One improvement cycle",
            "A campaign cycle: diagnose the parent, propose candidates, check them (stage 0), select on search_val "
            "(stages 1-2), confirm on the gate split with sequential looks (stage 3), report on held-out data, "
            "approve and promote.")
    W, H = 196, 108
    top = [("parent", ["the registry's active version"], TEAL),
           ("diagnosis", ["parent on search:", "failure buckets, traces"], TEAL),
           ("generators", ["config patches, learned", "artifacts (store ids)"], TEAL),
           ("stage 0", ["protected scope · schema", "provenance: no gate/heldout", "store ids verified",
                        "unknown provenance refused", "novelty · opt. prescreen"], ORANGE)]
    for i, (t, l, c) in enumerate(top):
        x = 50 + i * 228
        s.box(x, 40, W, H if i < 3 else 128, t, l, stroke=c, tfill=c, fill=ORANGE_BG if c == ORANGE else "#fff")
        if i < 3:
            s.line([(x + W + 2, 94), (x + 226, 94)], TEAL2)
    bot = [("stages 1–2", ["search_val, paired with", "the parent; stage 1 drops", "clearly worse ones early"], TEAL),
           ("stage 3: the gate", ["gate, then gate_r1 … looks", "Holm at the spent α", "vetoes: task regression,",
                                  "more safety interventions"], ORANGE),
           ("held-out report", ["heldout split, the winner", "only; never used", "for selection"], TEAL),
           ("approval", ["auto, or manual:", "pending_approval.json", "wc evolve approve"], ORANGE)]
    yb = 250
    for i, (t, l, c) in enumerate(reversed(bot)):
        x = 50 + i * 228
        s.box(x, yb, W, 120, t, l, stroke=c, tfill=c, fill=ORANGE_BG if c == ORANGE else "#fff")
    # stage0 -> stages 1-2 (rightmost bottom)
    s.line([(832, 170), (832, 246)], TEAL2)
    for i in range(3):
        x = 50 + (3 - i) * 228
        s.line([(x - 2, yb + 60), (x - 30, yb + 60)], TEAL2)
    s.box(50, 430, 424, 70, "promotion", ["registry ledger · ACTIVE · active.json → wc serve policy --campaign"],
          stroke=TEAL, tfill=TEAL, fill=TEAL_BG)
    s.line([(148, yb + 122), (148, 428)], TEAL)
    s.box(506, 430, 196, 70, "wc evolve rollback", ["restores the previous", "active version"], stroke=ORANGE, tfill=ORANGE)
    s.line([(504, 465), (476, 465)], ORANGE)
    s.curve("M48,465 C20,465 20,94 46,94", TEAL, sw=1.6)
    s.add(f'<text x="16" y="280" class="s" text-anchor="middle" fill="{TEAL}" font-weight="600" '
          f'transform="rotate(-90 16 280)">next cycle</text>')
    # verdicts
    s.text(730, 448, "VERDICTS IN archive.jsonl", "cap")
    for i, (v, c) in enumerate([("rejected", ORANGE), ("archived", MUTED), ("gated_fail", ORANGE),
                                ("gate_passed → promoted", TEAL)]):
        s.text(730, 466 + i * 16, v, "m", fill=c)
    s.text(50, 548, "Every candidate is archived with its stages. Only the top finalists of stages 1–2 (more wins than "
           "losses against the parent) reach the gate split.", "s")
    s.text(50, 566, "Generators and learners read only search / search_val (the split guard refuses gate and held-out "
           "data at build time and again at stage 0).", "s")
    return s.save("improvement-loop")


# ---------------------------------------------------------------- 5. splits
def splits() -> Path:
    s = SVG(960, 470, "RFC-0002 splits of the init states",
            "50 LIBERO init states split by rsi bounds (20, 30, 40): search 0-19, search_val 20-29, gate 30-39, "
            "heldout 40-49, and which part of the system may read each.")
    x0, cw, y = 150, 15.6, 52
    parts = [("search", 0, 20, TEAL2, "#d5eaec"), ("search_val", 20, 30, TEAL, "#b9dcdf"),
             ("gate", 30, 40, ORANGE, "#fbd9c7"), ("heldout", 40, 50, INK, "#e2e8f0")]
    s.text(30, 30, "LIBERO-10 TASK: 50 OFFICIAL INIT STATES, protocol: rsi, bounds (20, 30, 40)", "cap")
    for name, a, b, stroke, fill in parts:
        for i in range(a, b):
            s.rect(x0 + i * cw, y, cw - 2, 30, fill, stroke, rx=3, sw=.8)
        s.text(x0 + (a + b) / 2 * cw, y + 50, name, "t", "middle", fill=stroke)
        s.text(x0 + (a + b) / 2 * cw, y + 66, f"states {a}–{b - 1}", "s", "middle")
    for i in (0, 10, 20, 30, 40, 49):
        s.text(x0 + i * cw + cw / 2 - 1, y - 6, str(i), "s", "middle")
    s.text(30, y + 20, "init state", "t")
    s.text(30, 148, "Replicates reuse an init state with new policy noise (seed + r·50); gate_looks > 1 adds gate_r1, "
           "gate_r2 … (replicates of the gate states) for sequential looks.", "s")

    rows = [("diagnosis of the parent", ["read", "—", "—", "—"]),
            ("generators, learners, judges", ["read", "read", "refused", "refused"]),
            ("selection (stages 1–2)", ["—", "read", "—", "—"]),
            ("the gate (stage 3)", ["—", "—", "read", "—"]),
            ("report after the gate", ["—", "—", "—", "read"])]
    ty = 176
    s.text(30, ty, "WHO MAY READ IT", "cap")
    for j, (name, *_rest) in enumerate(parts):
        a, b = parts[j][1], parts[j][2]
        s.text(x0 + (a + b) / 2 * cw, ty, name, "t", "middle", fill=parts[j][3])
    for r, (who, cells) in enumerate(rows):
        yy = ty + 14 + r * 40
        s.rect(20, yy, 920, 34, PANEL if r % 2 == 0 else "#fff", "none", rx=4)
        s.text(30, yy + 22, who, "t")
        for j, c in enumerate(cells):
            a, b = parts[j][1], parts[j][2]
            cx = x0 + (a + b) / 2 * cw
            if c == "read":
                s.chip(cx - 26, yy + 6, "read", w=52)
            elif c == "refused":
                s.chip(cx - 34, yy + 6, "refused", fill=ORANGE_BG, stroke=ORANGE, color=ORANGE, w=68)
            else:
                s.text(cx, yy + 22, "—", "s", "middle")
    s.text(30, 404, "The split guard (core.artifact) refuses gate and held-out runs when an artifact is built, the "
           "seal refuses them in provenance, and the gate re-checks", "s")
    s.text(30, 420, "every artifact a candidate references. Held-out numbers are reported, never used to choose.", "s")
    s.text(930, 452, "worldcurrent.eval.benchmark.rsi_splits", "m", "end", fill=MUTED)
    return s.save("splits")


# ---------------------------------------------------------------- 6. store
def store() -> Path:
    s = SVG(960, 600, "The run and artifact store",
            "Runs and sealed artifacts get ids; configs reference ids that the registry resolves to this machine's "
            "paths; the index records provenance and referrers; deletion is refused while referred to; stores sync "
            "between machines.")
    s.rect(20, 20, 580, 500, TEAL_BG, TEAL2, rx=12)
    s.text(36, 44, "ONE STORE (the profile's store: …/runs)", "cap", fill=TEAL)
    runs = ["run:rsi-l10-parent-search-…31f1e5", "run:libero10-steered-…9b8983", "run:libero10-steered-…d528f7"]
    for i, r in enumerate(runs):
        s.rect(36, 60 + i * 38, 270, 28, "#fff", TEAL2, rx=6, sw=1)
        s.text(46, 79 + i * 38, r, "m", fill=TEAL)
    s.rect(380, 84, 204, 56, "#fff", TEAL, rx=8, sw=1.6)
    s.text(392, 106, "artifact:l10-trace-v2", "m", fill=TEAL, weight="600")
    s.text(392, 124, "@54a1efadf00d34d8", "m", fill=TEAL)
    for i in range(3):
        s.line([(308, 74 + i * 38), (376, 112)], TEAL2)
    s.text(392, 76, "provenance: built from", "s")
    s.rect(36, 186, 270, 46, "#fff", LINE, rx=6, sw=1)
    s.text(46, 206, "campaign:evolve/…", "m")
    s.text(46, 223, "archive.jsonl, registry ledger", "s")
    s.curve("M308,209 C370,209 420,190 430,144", ORANGE, dash="4 3")
    s.text(440, 190, "refers to", "s", fill=ORANGE, weight="600")
    s.text(440, 206, "(ids in candidate patches)", "s", fill=ORANGE)

    s.text(36, 266, "A CONFIG NAMES CONTENT, NOT A PLACE", "cap", fill=TEAL)
    s.rect(36, 276, 548, 30, "#fff", LINE, rx=6, sw=1)
    s.text(48, 296, 'judge: {path: "artifact:l10-trace-v2@54a1efad"}', "m")
    s.line([(120, 308), (120, 334)], TEAL2)
    s.text(132, 322, "digest taken over the id; registry.build then resolves it", "s")
    s.rect(36, 338, 548, 30, "#fff", TEAL2, rx=6, sw=1)
    s.text(48, 358, "/home/you/…/runs/judges/l10-trace-v2  (pinned in the run)", "m", fill=TEAL)

    s.rect(36, 392, 548, 110, ORANGE_BG, ORANGE, rx=8, sw=1.2)
    s.text(48, 414, "wc store rm run:rsi-l10-parent-search-…", "m", fill=ORANGE, weight="600")
    s.text(48, 434, "refused: referred to by artifact:l10-trace-v2@… and 3 more", "s")
    s.text(48, 456, "wc store rm … --force --reason \"…\"", "m", fill=ORANGE)
    s.text(48, 476, "deletes and appends a tombstone: a later lookup of the id says", "s")
    s.text(48, 492, "when and why it was removed, instead of \"not found\"", "s")

    s.text(624, 44, "BETWEEN MACHINES (rsync over ssh)", "cap")
    ms = [("robot computer", ["workcell episodes"], 60), ("workstation", ["the main store"], 230),
          ("GPU box", ["policy server, training"], 400)]
    for n, l, y in ms:
        s.box(640, y, 290, 70, n, l, stroke=INK)
    s.line([(720, 132), (720, 226)], TEAL)                     # robot -> workstation
    s.text(728, 176, "pull: runs", "s", fill=TEAL, weight="600")
    s.line([(876, 226), (876, 132)], ORANGE)
    s.text(868, 194, "push: artifacts", "s", "end", fill=ORANGE, weight="600")
    s.line([(720, 396), (720, 302)], TEAL)                     # GPU box -> workstation
    s.text(728, 346, "pull: runs, artifacts", "s", fill=TEAL, weight="600")
    s.line([(876, 302), (876, 396)], ORANGE)
    s.text(868, 364, "push: artifacts", "s", "end", fill=ORANGE, weight="600")
    notes = ["(run on the workstation)", "wc store pull robot:/path/runs", "wc store push robot:/path/runs artifact:…",
             "Sealed artifacts are never re-copied or", "overwritten; the same path holding something",
             "else is a conflict: nothing is copied."]
    for i, t in enumerate(notes):
        s.text(624, 482 + i * 17, t, "m" if i in (1, 2) else "s", fill=INK if i in (1, 2) else MUTED)
    s.text(36, 548, "ids: run:<run_id> · artifact:<name>@<digest> (a prefix of ≥ 8 hex characters works)", "s")
    s.text(36, 566, "index: <store>/.wc-store/index.json, a cache rebuilt by walking the tree on a miss", "s")
    s.text(930, 596, "worldcurrent.core.store · wc store", "m", "end", fill=MUTED)
    return s.save("store")


# ---------------------------------------------------------------- 7. deployment
def deployment() -> Path:
    s = SVG(960, 644, "Deployment topology",
            "The workstation runs studio's control plane, campaigns and the main store; the robot computer runs the "
            "workcell, its safety shield and the robot adapter; a GPU box serves the policy.")

    def machine(x, y, w, h, name, sub):
        s.rect(x, y, w, h, PANEL, INK, rx=12, sw=1.2)
        s.text(x + 14, y + 22, name, "h")
        s.text(x + 14, y + 38, sub, "s")

    s.box(36, 12, 248, 44, "operator's browser", ["studio UI: start, watch, stop, label"], tsize=12, lh=13)

    machine(20, 70, 280, 330, "Workstation", "studio, campaigns, the main store")
    s.box(36, 118, 248, 62, "wc playground :8765", ["control plane, run explorer,", "live sandbox, campaigns"],
          stroke=TEAL2, tfill=TEAL)
    s.box(36, 194, 248, 54, "wc evolve · wc bench", ["campaigns, the gate, scorecards"], stroke=TEAL2, tfill=TEAL)
    s.box(36, 262, 248, 54, "store", ["runs and artifacts by id"], stroke=TEAL2, tfill=TEAL)
    s.box(36, 330, 248, 50, "active.json", ["the promoted version"], stroke=ORANGE, tfill=ORANGE)

    machine(330, 70, 300, 380, "Robot computer", "installs wc-core + wc-serve only")
    s.box(346, 118, 268, 52, "wc serve workcell :8101", ["workcell API, wc.workcell/v0.1"], stroke=TEAL2, tfill=TEAL)
    s.box(346, 182, 268, 56, "EpisodeRunner", ["core.kernel: realtime timing, wall clock"], stroke=TEAL2, tfill=TEAL)
    s.box(346, 250, 268, 56, "SafetyShield", ["guards, workspace, keep-out,", "latched e-stop, watchdog"],
          stroke=ORANGE, tfill=ORANGE, fill=ORANGE_BG)
    s.box(346, 318, 268, 44, "lerobot.robot", ["robot adapter (LeRobot Robot)"], stroke=INK, lh=13)
    s.box(346, 374, 268, 56, "operator channel", ["stop, e-stop, clear fault,", "reset done, verdict"], stroke=INK)
    s.line([(480, 452), (480, 488)], INK)
    s.text(488, 476, "joint targets", "s")
    s.box(385, 490, 190, 50, "robot arm", ["SO-101, or the simulated arm"], stroke=INK, lh=13)

    machine(660, 70, 280, 220, "GPU box", "inference")
    s.box(676, 118, 248, 70, "wc serve policy :8001", ["websocket /wc, msgpack-numpy", "(or the openpi protocol)"],
          stroke=TEAL2, tfill=TEAL)
    s.box(676, 200, 248, 54, "policy weights", ["e.g. lerobot/smolvla_libero"])

    s.line([(262, 58), (262, 114)], INK)                                    # browser -> control plane
    s.text(292, 40, "HTTP :8765", "s", fill=INK, weight="600")
    s.line([(286, 144), (342, 144)], TEAL)                                  # control plane -> workcell
    s.text(314, 134, "HTTP", "s", "middle", fill=TEAL, weight="600")
    s.line([(616, 210), (644, 210), (644, 152), (672, 152)], TEAL)          # runner -> policy server
    s.line([(330, 289), (288, 289)], TEAL2, dash="5 4")                     # store pull
    s.line([(160, 382), (160, 590), (924, 590), (924, 294)], ORANGE, dash="5 4")
    s.text(600, 582, "wc serve policy --campaign DIR serves the active version", "s", "middle", fill=ORANGE)

    s.text(660, 330, "LINKS", "cap")
    legend = [(TEAL, None, "HTTP workcell API"),
              (TEAL, None, "websocket: obs → chunk"),
              (TEAL2, "5 4", "wc store pull: runs"),
              (ORANGE, "5 4", "promoted version")]
    for i, (c, d, t) in enumerate(legend):
        y = 352 + i * 22
        s.line([(660, y), (700, y)], c, arrow=False, dash=d, sw=2)
        s.text(710, y + 4, t, "s")
    s.text(20, 616, "Workcell API: /status /episodes /operator /events. Ports as in the examples: policy 8001 (8002 "
           "for the bring-up wave), workcells", "s")
    s.text(20, 632, "8101 / 8102, playground 8765. Tokens are passed with --token, never in configs.", "s")
    return s.save("deployment")


if __name__ == "__main__":
    for f in (architecture, repositories, episode_loop, improvement_loop, splits, store, deployment):
        print(f())
