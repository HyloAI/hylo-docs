"""README art for every Hylo repository: banners, the stack map and one or two diagrams per repository.

    uv run --no-project --with fonttools --with uharfbuzz --with pillow python docs/mkdocs/figures/readme_art.py

Run from the development workspace (the repositories side by side). Writes `<repo>/.github/assets/*.svg` (the org
profile: `org-profile/profile/assets/`), each in a light and a dark version for a `<picture>` element, and copies the
recorded figures the READMEs show from `docs/assets/figures/`.

Text is shaped with HarfBuzz and drawn as outlines (Inter and JetBrains Mono, SIL Open Font License, downloaded once
to ~/.cache/hylo/fonts), so a figure looks the same on every viewer: an SVG shown through <img> cannot load fonts.
Each glyph is stored once per file and placed with <use>. Colours are the site's (graphite, paper, cinnabar).
"""

from __future__ import annotations

import io
import shutil
import urllib.request
import zipfile
from dataclasses import dataclass, field
from html import escape
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[3]
FIGURES = Path(__file__).resolve().parents[2] / "docs" / "assets" / "figures"
FONT_CACHE = Path.home() / ".cache" / "hylo" / "fonts"
FONT_ZIPS = {
    "https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip":
        ["Inter-Regular", "Inter-Medium", "Inter-SemiBold", "Inter-Bold", "InterDisplay-Bold",
         "InterDisplay-ExtraBold"],
    "https://github.com/JetBrains/JetBrainsMono/releases/download/v2.304/JetBrainsMono-2.304.zip":
        ["JetBrainsMono-Regular", "JetBrainsMono-Medium", "JetBrainsMono-Bold"],
}
FACES = {"r": "Inter-Regular", "m": "Inter-Medium", "sb": "Inter-SemiBold", "b": "Inter-Bold",
         "db": "InterDisplay-Bold", "dx": "InterDisplay-ExtraBold",
         "mono": "JetBrainsMono-Medium", "monor": "JetBrainsMono-Regular", "monob": "JetBrainsMono-Bold"}

LIGHT = dict(bg="#f7f6f2", surface="#ffffff", sunk="#efede6", ink="#171c22", muted="#5b6168", faint="#8b9096",
             line="#e2dfd6", line2="#cdc9be", accent="#c8442d", accent_soft="#f8e6e0", accent_ink="#ffffff",
             kernel="#171c22", kernel_ink="#f7f6f2", logo="#c8442d", shade="#000000")
DARK = dict(bg="#121416", surface="#1a1d21", sunk="#22262b", ink="#eceae4", muted="#a2a6ab", faint="#73787e",
            line="#2b2f34", line2="#3b4047", accent="#e8664d", accent_soft="#33201c", accent_ink="#121416",
            kernel="#eceae4", kernel_ink="#121416", logo="#c8442d", shade="#000000")
THEMES = {"light": LIGHT, "dark": DARK}


# ---------------------------------------------------------------- fonts and text
def _fetch_fonts() -> None:
    FONT_CACHE.mkdir(parents=True, exist_ok=True)
    for url, names in FONT_ZIPS.items():
        if all((FONT_CACHE / f"{n}.ttf").exists() for n in names):
            continue
        with urllib.request.urlopen(url, timeout=120) as r:
            z = zipfile.ZipFile(io.BytesIO(r.read()))
        for member in z.namelist():
            stem = Path(member).stem
            if member.endswith(".ttf") and stem in names and "variable" not in member.lower():
                (FONT_CACHE / f"{stem}.ttf").write_bytes(z.read(member))


class Font:
    def __init__(self, key: str, path: Path) -> None:
        import uharfbuzz as hb
        from fontTools.ttLib import TTFont

        self.key = key
        self._hb = hb
        self.hbfont = hb.Font(hb.Face(path.read_bytes()))
        tt = TTFont(path)
        self.upem = tt["head"].unitsPerEm
        self.glyphset, self.order = tt.getGlyphSet(), tt.getGlyphOrder()
        self._paths: dict[int, str] = {}

    def shape(self, s: str) -> list[tuple[int, int, int, int]]:
        if not s:
            return []
        buf = self._hb.Buffer()
        buf.add_str(s)
        buf.guess_segment_properties()
        self._hb.shape(self.hbfont, buf, {"kern": True, "liga": True, "calt": True})
        return [(i.codepoint, p.x_advance, p.x_offset, p.y_offset)
                for i, p in zip(buf.glyph_infos, buf.glyph_positions)]

    def path(self, gid: int) -> str:
        if gid not in self._paths:
            from fontTools.pens.svgPathPen import SVGPathPen

            pen = SVGPathPen(self.glyphset, ntos=lambda v: str(round(v)))
            self.glyphset[self.order[gid]].draw(pen)
            self._paths[gid] = pen.getCommands()
        return self._paths[gid]


FONTS: dict[str, Font] = {}


def font(key: str) -> Font:
    if not FONTS:
        _fetch_fonts()
        for k, name in FACES.items():
            FONTS[k] = Font(k, FONT_CACHE / f"{name}.ttf")
    return FONTS[key]


def measure(s: str, face: str = "sb", size: float = 17, track: float = 0.0) -> float:
    f = font(face)
    run = f.shape(s)
    return (sum(a for _, a, _, _ in run) + track * f.upem * max(len(run) - 1, 0)) * size / f.upem


def wrap(s: str, face: str, size: float, width: float) -> list[str]:
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}".strip()
        if cur and measure(trial, face, size) > width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + ([cur] if cur else [])


def mix(a: str, b: str, t: float) -> str:
    """Blend two #rrggbb colours: t = 0 gives a, t = 1 gives b."""
    pa = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    pb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(pa, pb))


# ---------------------------------------------------------------- the SVG document
class Doc:
    def __init__(self, w: int, h: int, T: dict, title: str, desc: str) -> None:
        self.w, self.h, self.T, self.title, self.desc = w, h, T, title, desc
        self.body: list[str] = []
        self.defs: list[str] = []
        self.glyphs: dict[str, str] = {}
        self.markers: set[str] = set()

    def c(self, color: str) -> str:
        return self.T.get(color, color)

    def add(self, s: str) -> None:
        self.body.append(s)

    # -- text
    def text(self, x: float, y: float, s: str, face: str = "sb", size: float = 17, fill: str = "ink",
             anchor: str = "start", track: float = 0.0, opacity: float | None = None) -> float:
        f = font(face)
        k = size / f.upem
        run = f.shape(s)
        tu = track * f.upem
        w = (sum(a for _, a, _, _ in run) + tu * max(len(run) - 1, 0)) * k
        x0 = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
        uses, cx = [], 0.0
        for gid, adv, xo, yo in run:
            d = f.path(gid)
            if d:
                gname = f"{f.key}{gid}"
                self.glyphs[gname] = d
                yattr = f' y="{round(yo)}"' if yo else ""
                uses.append(f'<use href="#{gname}" x="{round(cx + xo)}"{yattr}/>')
            cx += adv + tu
        op = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<g transform="translate({x0:.1f} {y:.1f}) scale({k:.5f} {-k:.5f})" fill="{self.c(fill)}"{op}>'
                 + "".join(uses) + "</g>")
        return w

    def lines(self, x: float, y: float, rows: list[str], lh: float, **kw) -> None:
        for i, row in enumerate(rows):
            self.text(x, y + i * lh, row, **kw)

    # -- shapes
    def rect(self, x, y, w, h, fill="surface", stroke=None, rx=12, sw=1.5, dash=None, opacity=None) -> None:
        st = f' stroke="{self.c(stroke)}" stroke-width="{sw}"' if stroke else ""
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
                 f'fill="{self.c(fill)}"{st}{ds}{op}/>')

    def poly(self, pts, fill, stroke=None, sw=1.2) -> None:
        st = f' stroke="{self.c(stroke)}" stroke-width="{sw}" stroke-linejoin="round"' if stroke else ""
        p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.add(f'<polygon points="{p}" fill="{self.c(fill)}"{st}/>')

    def arrow(self, pts, color="muted", sw=2.0, dash=None, both=False, head=True, rounded=10) -> None:
        col = self.c(color)
        self.markers.add(col)
        d = _rounded_path(pts, rounded)
        m = f' marker-end="url(#m{col[1:]})"' if head else ""
        if both:
            m += f' marker-start="url(#m{col[1:]})"'
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" '
                 f'stroke-linejoin="round"{ds}{m}/>')

    def label(self, x, y, s, anchor="middle", fill="muted", size=14, face="m", plate="bg") -> None:
        """An edge label on a plate in the colour behind it, so it stays legible over lines."""
        w = measure(s, face, size)
        x0 = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
        self.rect(x0 - 6, y - size + 1, w + 12, size + 8, plate, rx=6)
        self.text(x0, y + 2, s, face, size, fill)

    def pill(self, x, y, s, *, face="mono", size=14, h=28, fill="sunk", stroke=None, color="ink", padx=12,
             track=0.0, anchor="start", opacity=None) -> float:
        w = measure(s, face, size, track) + 2 * padx
        x0 = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
        self.rect(x0, y, w, h, fill, stroke, rx=h / 2, sw=1.2, opacity=opacity)
        self.text(x0 + padx, y + h / 2 + size * 0.36, s, face, size, color, track=track)
        return w

    def box(self, x, y, w, h, title, sub=None, kind="plain", tface="sb", tsize=17, sface="r", ssize=14.5,
            align="middle", dash=None) -> None:
        fill, stroke, tcol, scol, sw = {
            "plain": ("surface", "line2", "ink", "muted", 1.5),
            "soft": ("accent_soft", "accent", "ink", "muted", 1.5),
            "accent": ("accent", "accent", "accent_ink", "accent_ink", 1.5),
            "kernel": ("kernel", "kernel", "kernel_ink", "kernel_ink", 1.5),
            "ghost": ("sunk", "line2", "ink", "muted", 1.3),
        }[kind]
        self.rect(x, y, w, h, fill, stroke, rx=12, sw=sw, dash=dash or ("5 4" if kind == "ghost" else None))
        subs = [] if sub is None else ([sub] if isinstance(sub, str) else list(sub))
        lh = ssize + 5
        block = tsize * 0.72 + (len(subs) * lh + 3 if subs else 0)
        ty = y + h / 2 - block / 2 + tsize * 0.72
        tx = x + w / 2 if align == "middle" else x + 18
        self.text(tx, ty, title, tface, tsize, tcol, anchor=align)
        for i, s in enumerate(subs):
            self.text(tx, ty + 6 + (i + 1) * lh - 3, s, sface, ssize, scol, anchor=align,
                      opacity=0.85 if kind in ("accent", "kernel") else None)

    def card(self) -> None:
        """The figure's own background: a rounded card in the page colour."""
        self.add(f'<rect x="0.75" y="0.75" width="{self.w - 1.5}" height="{self.h - 1.5}" rx="20" '
                 f'fill="{self.c("bg")}" stroke="{self.c("line")}" stroke-width="1.5"/>')

    def logo(self, x, y, size) -> None:
        s = size / 64
        self.add(f'<g transform="translate({x} {y}) scale({s:.4f})"><rect width="64" height="64" rx="14" '
                 f'fill="{self.T["logo"]}"/><g fill="none" stroke="#ffffff" stroke-width="5" stroke-linecap="round">'
                 '<path d="M10 22c7-7 15 7 22 0s15 7 22 0"/><path d="M10 33c7-7 15 7 22 0s15 7 22 0" opacity=".78"/>'
                 '<path d="M10 44c7-7 15 7 22 0s15 7 22 0" opacity=".56"/></g></g>')

    def save(self, path: Path) -> Path:
        markers = "".join(
            f'<marker id="m{c[1:]}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="11" markerHeight="11" '
            f'orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M0,0.8 L10,5 L0,9.2 z" '
            f'fill="{c}"/></marker>' for c in sorted(self.markers))
        glyphs = "".join(f'<path id="{k}" d="{d}"/>' for k, d in sorted(self.glyphs.items()))
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" '
               f'height="{self.h}" role="img" aria-labelledby="t d">\n'
               f'<title id="t">{escape(self.title)}</title>\n<desc id="d">{escape(self.desc)}</desc>\n'
               f'<defs>{glyphs}{markers}{"".join(self.defs)}</defs>\n' + "\n".join(self.body) + "\n</svg>\n")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(svg)
        return path


def _rounded_path(pts, r) -> str:
    """A polyline with rounded corners."""
    pts = [q for i, q in enumerate(pts) if i == 0 or q != pts[i - 1]]
    if len(pts) < 3 or not r:
        return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    out = [f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"]
    for (x0, y0), (x1, y1), (x2, y2) in zip(pts, pts[1:], pts[2:]):
        import math

        d1, d2 = math.hypot(x1 - x0, y1 - y0), math.hypot(x2 - x1, y2 - y1)
        rr = min(r, d1 / 2, d2 / 2)
        ax, ay = x1 - (x1 - x0) / d1 * rr, y1 - (y1 - y0) / d1 * rr
        bx, by = x1 + (x2 - x1) / d2 * rr, y1 + (y2 - y1) / d2 * rr
        out.append(f"L{ax:.1f},{ay:.1f} Q{x1:.1f},{y1:.1f} {bx:.1f},{by:.1f}")
    out.append(f"L{pts[-1][0]:.1f},{pts[-1][1]:.1f}")
    return " ".join(out)


# ---------------------------------------------------------------- the stack
LAYERS = [  # top to bottom
    ("Workbench", "Inspect skill development and execution", [("studio", "studio")]),
    ("Evolution", "Improve skill implementations and versions", [("harness", "harness · learn, evolve")]),
    ("Evaluation", "Validate skills under stated conditions", [("bench", "bench"), ("harness", "harness · eval")]),
    ("Cognition", "Implement skills with tools and policies", [("harness", "harness · manip, agents")]),
    ("Runtime", "Run skill implementations within limits",
     [("serve", "serve"), ("deployments-template", "deployments-template")]),
    ("Kernel", "One kernel for models, simulators and robots", [("harness", "harness · core"),
                                                                  ("plugins", "plugins")]),
]


@dataclass
class Repo:
    key: str                       # directory in the workspace
    word: tuple[str, str]          # wordmark: (quiet prefix, name)
    tagline: str
    layers: set[str]
    figures: list = field(default_factory=list)          # diagram functions
    copies: dict = field(default_factory=dict)           # asset name -> (source in docs figures, crop box or None)

    @property
    def assets(self) -> Path:
        base = WORKSPACE / self.key
        return base / "profile" / "assets" if self.key == "org-profile" else base / ".github" / "assets"


def stack_glyph(d: Doc, cx: float, y0: float, lit: dict[str, float], hw=150, hh=58, t=13, gap=38) -> None:
    """Six isometric slabs, Workbench on top; lit layers in cinnabar (value = strength)."""
    T = d.T
    n = len(LAYERS)
    for i in reversed(range(n)):                     # bottom first: upper slabs cover lower ones
        name = LAYERS[i][0]
        y = y0 + i * gap
        top = [(cx, y), (cx + hw, y + hh), (cx, y + 2 * hh), (cx - hw, y + hh)]
        left = [(cx - hw, y + hh), (cx, y + 2 * hh), (cx, y + 2 * hh + t), (cx - hw, y + hh + t)]
        right = [(cx, y + 2 * hh), (cx + hw, y + hh), (cx + hw, y + hh + t), (cx, y + 2 * hh + t)]
        s = lit.get(name, 0.0)
        if s:
            base = mix(T["surface"], T["accent"], s)
            d.poly(left, mix(base, T["shade"], 0.18))
            d.poly(right, mix(base, T["shade"], 0.32))
            gid = f"slab{i}"
            d.defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">'
                          f'<stop offset="0" stop-color="{mix(base, "#ffffff", 0.16)}"/>'
                          f'<stop offset="1" stop-color="{base}"/></linearGradient>')
            d.poly(top, f"url(#{gid})", mix(base, T["shade"], 0.1), 1)
        else:
            d.poly(left, T["sunk"], T["line2"], 1)
            d.poly(right, mix(T["sunk"], T["shade"], 0.06), T["line2"], 1)
            d.poly(top, T["surface"], T["line2"], 1.2)
        # label at the slab's right corner
        ly = y + hh + t / 2
        col = "accent" if s >= 0.5 else "muted"
        d.add(f'<line x1="{cx + hw + 8}" y1="{ly}" x2="{cx + hw + 26}" y2="{ly}" stroke="{d.c(col)}" '
              f'stroke-width="1.5"/>')
        d.text(cx + hw + 34, ly + 6.5, name, "b" if s >= 0.5 else "sb", 19, col)


def banner(T: dict, r: Repo) -> Doc:
    W, H = 1280, 400
    d = Doc(W, H, T, f"{''.join(r.word)}: {r.tagline}",
            f"Banner of {''.join(r.word)}, part of Hylo, the stack for physical AI. The six layers of the stack, "
            f"from Workbench on top to Kernel at the base; highlighted: {', '.join(sorted(r.layers)) or 'all'}.")
    d.defs.append(f'<clipPath id="cardclip"><rect width="{W}" height="{H}" rx="28"/></clipPath>')
    d.defs.append('<linearGradient id="wavefade" x1="0" y1="0" x2="1" y2="0"><stop offset="0.45" stop-color="#fff" '
                  'stop-opacity="0"/><stop offset="0.8" stop-color="#fff" stop-opacity="1"/></linearGradient>'
                  f'<mask id="wavemask"><rect width="{W}" height="{H}" fill="url(#wavefade)"/></mask>')
    d.add('<g clip-path="url(#cardclip)">')
    d.rect(0, 0, W, H, "bg", rx=0)
    waves = []                                      # the logo's waves as a faint texture on the right
    for i in range(16):
        y = 18 + i * 26
        seg = "".join("c21-21 45 21 66 0" if j == 0 else "s45 21 66 0" for j in range(12))
        waves.append(f'<path d="M420 {y}{seg}"/>')
    d.add(f'<g mask="url(#wavemask)" fill="none" stroke="{T["line2"]}" stroke-width="1.4" opacity="0.45">'
          + "".join(waves) + "</g>")
    d.add("</g>")
    d.add(f'<rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="28" fill="none" '
          f'stroke="{T["line"]}" stroke-width="1.5"/>')

    lit = {name: 1.0 for name in r.layers} if r.layers else {n: 0.55 + 0.09 * i for i, (n, _, _) in
                                                               enumerate(reversed(LAYERS))}
    stack_glyph(d, 950, 44, lit)

    x = 72
    d.logo(x, 84, 52)
    if r.key != "org-profile":
        d.text(x + 68, 84 + 35, "Hylo", "b", 26, "ink")
    pre, name = r.word
    size = 92.0
    while measure(pre + name, "dx", size) > 700:
        size -= 2
    base = 236
    wpre = d.text(x - size * 0.04, base, pre, "dx", size, "faint") if pre else 0
    d.text(x - size * 0.04 + wpre, base, name, "dx", size, "ink")
    d.lines(x, base + 54, wrap(r.tagline, "m", 26, 640), 36, face="m", size=26, fill="muted")
    return d


def stack_map(T: dict, r: Repo) -> Doc:
    W, rh, gap, top = 960, 58, 8, 20
    H = top * 2 + len(LAYERS) * (rh + gap) - gap
    d = Doc(W, H, T, "The Hylo stack", "Six layers, top to bottom, and the repositories that implement each: "
            + "; ".join(f"{n}: {', '.join(p for _, p in rs)}" for n, _, rs in LAYERS)
            + f". This repository: {''.join(r.word)}.")
    d.card()
    for i, (name, _, repos) in enumerate(LAYERS):
        y = top + i * (rh + gap)
        here = any(k == r.key for k, _ in repos)
        d.rect(20, y, W - 40, rh, "accent_soft" if here else "surface", "accent" if here else "line", rx=12,
               sw=1.5 if here else 1.2)
        d.text(48, y + rh / 2 + 7, name, "b", 20, "accent" if here else "ink")
        px = W - 46
        for k, _ in reversed(repos):
            mine = k == r.key
            label = k if k != "deployments-template" else "deployments"
            px -= d.pill(px, y + (rh - 34) / 2, label, face="sb", size=16.5, h=34, padx=16, anchor="end",
                         fill="accent" if mine else "sunk", color="accent_ink" if mine else "ink",
                         stroke=None if mine else "line2") + 10
    return d


# ---------------------------------------------------------------- diagrams
def harness_architecture(T: dict) -> Doc:
    W, H = 960, 590
    d = Doc(W, H, T, "Packages of hylo-harness",
            "The packages of hylo-harness by layer. Interface: cli. Evolution: evolve and learn. Evaluation: eval and "
            "catalog. Cognition: agents, memory, policies, instruments and reasoners. Development: manip and code "
            "agents with independent model tools. All build on hylo-core, the "
            "kernel: contracts, the episode kernel, the SafetyShield, the plugin registry and the store. Adapters to "
            "LeRobot, openpi and LLMs plug into the registry through entry points.")
    d.card()
    x0, x1, bh, g = 176, 932, 60, 12

    def row(y, label, items, kind="plain"):
        d.text(40, y + bh / 2 + 6, label, "sb", 17, "muted")
        n = len(items)
        w = (x1 - x0 - g * (n - 1)) / n
        for j, t in enumerate(items):
            d.box(x0 + j * (w + g), y, w, bh, t, kind=kind, tface="mono", tsize=17)

    row(28, "Interface", ["cli"])
    row(100, "Evolution", ["evolve", "learn"])
    row(172, "Evaluation", ["eval", "catalog"])
    row(244, "Cognition", ["agents", "memory", "policies", "instruments", "reasoners"])
    row(316, "Development", ["manip", "code-agents", "tools"])
    ky, kh = 398, 106
    d.text(40, ky + 40, "Kernel", "sb", 17, "accent")
    d.rect(x0, ky, x1 - x0, kh, "kernel", rx=16)
    d.text(x0 + 26, ky + 44, "core", "dx", 30, "kernel_ink")
    cx = x0 + 26
    for c in ["contracts", "episode kernel", "SafetyShield", "plugin registry", "store"]:
        cx += d.pill(cx, ky + 60, c, face="m", size=15.5, h=32, fill="kernel", padx=14,
                     stroke=mix(T["kernel"], T["kernel_ink"], 0.35), color="kernel_ink") + 10
    ay = 528
    d.text(40, ay + 30, "Adapters", "sb", 17, "muted")
    names = ["lerobot", "openpi", "llm"]
    w = (x1 - x0 - g * 2) / 3
    for j, t in enumerate(names):
        x = x0 + j * (w + g)
        d.box(x, ay, w, 46, t, kind="ghost", tface="mono", tsize=16)
        d.arrow([(x + w / 2, ay - 2), (x + w / 2, ky + kh + 6)], "faint", 1.6)
    return d


def improvement_loop(T: dict) -> Doc:
    W, H = 960, 390
    d = Doc(W, H, T, "Develop robot skills; run, measure, improve and deploy",
            "A task requirement and robot tools produce a task program that enters the shared execution loop. "
            "Existing policies can enter that loop directly. Run, measure, improve through a gate and deploy. "
            "Episodes on the robot come back as runs.")
    d.card()
    d.text(40, 64, "Develop skills", "b", 19, "accent")
    d.box(200, 24, 300, 62, "Task and robot tools", tsize=18)
    d.box(570, 24, 220, 62, "Program", kind="soft", tsize=18)
    d.arrow([(504, 55), (566, 55)], "accent", 2)
    d.arrow([(680, 88), (680, 112), (132, 112), (132, 144)], "accent", 2, rounded=12)
    stages = [("Run", "hylo run"), ("Measure", "hylo bench"), ("Improve", "hylo evolve"), ("Deploy", "hylo serve")]
    w, h, y, g = 196, 128, 148, 36
    x0 = (W - 4 * w - 3 * g) / 2
    for i, (name, cmd) in enumerate(stages):
        x = x0 + i * (w + g)
        gate = name == "Improve"
        d.rect(x, y, w, h, "accent_soft" if gate else "surface", "accent" if gate else "line2", rx=16,
               sw=2 if gate else 1.5)
        d.text(x + w / 2, y + 60, name, "dx", 32, "accent" if gate else "ink", anchor="middle")
        d.text(x + w / 2, y + 96, cmd, "mono", 16, "muted", anchor="middle")
        if i < 3:
            d.arrow([(x + w + 6, y + h / 2), (x + w + g - 6, y + h / 2)], "accent", 2.2)
    xa, xb, yb = x0 + 3 * (w + g) + w / 2, x0 + w / 2, y + h + 50
    d.arrow([(xa, y + h + 3), (xa, yb), (xb, yb), (xb, y + h + 6)], "accent", 2, dash="7 6", rounded=16)
    d.label((xa + xb) / 2, yb + 6, "episodes come back as runs", fill="accent", size=16)
    return d


def bench_flow(T: dict) -> Doc:
    W, H = 960, 280
    d = Doc(W, H, T, "From protocol to leaderboard",
            "A policy and a protocol (benchmark, split, environment, safety limits, seed) go into hylo bench run, "
            "which writes runs with traces and a scorecard. Scorecards with the same protocol are comparable: they "
            "rank on a leaderboard and compare episode by episode.")
    d.card()
    d.box(28, 52, 190, 70, "Policy", tsize=18)
    d.box(28, 158, 190, 70, "Protocol", tsize=18)
    d.box(290, 105, 210, 70, "hylo bench run", kind="accent", tface="mono", tsize=17)
    d.box(572, 52, 170, 70, "Runs", tsize=18)
    d.box(572, 158, 170, 70, "Scorecard", kind="soft", tsize=18)
    d.box(790, 116, 142, 58, "Leaderboard", tsize=17)
    d.box(790, 194, 142, 58, "Compare", tsize=17)
    d.arrow([(220, 87), (254, 87), (254, 128), (286, 128)], "muted")
    d.arrow([(220, 193), (254, 193), (254, 152), (286, 152)], "muted")
    d.arrow([(502, 128), (536, 128), (536, 87), (568, 87)], "accent")
    d.arrow([(502, 152), (536, 152), (536, 193), (568, 193)], "accent")
    d.arrow([(744, 182), (766, 182), (766, 145), (786, 145)], "muted")
    d.arrow([(744, 204), (766, 204), (766, 223), (786, 223)], "muted")
    return d


def serve_topology(T: dict) -> Doc:
    W, H = 960, 520
    d = Doc(W, H, T, "Deployment with hylo-serve",
            "Three machines. The workstation runs Studio and holds the store. The robot computer runs hylo serve "
            "workcell: a real-time runner, the SafetyShield, the operator channel and the robot adapter, which drives "
            "the arm. A GPU box runs hylo serve policy, which follows a campaign's promoted version. Studio talks to "
            "the workcell over HTTP, the workcell to the policy server over a WebSocket, and recorded runs go to the "
            "store.")
    d.card()

    def machine(x, y, w, h, name):
        d.rect(x, y, w, h, "sunk", "line2", rx=16)
        d.text(x + 20, y + 34, name, "b", 18, "ink")

    machine(24, 70, 236, 280, "Workstation")
    d.box(46, 130, 192, 60, "Studio", tsize=17)
    d.box(46, 266, 192, 60, "Store", tsize=17)
    machine(292, 70, 336, 360, "Robot computer")
    d.rect(310, 116, 300, 296, "surface", "accent", rx=14, sw=1.8)
    d.text(328, 148, "hylo serve workcell", "mono", 16, "accent")
    items = [("Real-time runner", "soft"), ("SafetyShield", "accent"), ("Operator channel", "soft"),
             ("Robot adapter", "soft")]
    for i, (t, k) in enumerate(items):
        d.box(328, 166 + i * 60, 264, 50, t, kind=k, tsize=16.5)
    machine(682, 70, 254, 180, "GPU box")
    d.box(702, 130, 214, 60, "hylo serve policy", tface="mono", tsize=15.5)
    d.box(360, 456, 200, 48, "Robot arm", kind="kernel", tsize=17)
    d.arrow([(240, 160), (306, 160)], "accent", 2)
    d.label(273, 146, "HTTP", size=15)
    d.arrow([(306, 296), (242, 296)], "muted", 2)
    d.label(273, 282, "runs", size=15)
    d.arrow([(614, 160), (698, 160)], "accent", 2, both=True)
    d.label(656, 146, "WebSocket", size=15)
    d.arrow([(460, 414), (460, 452)], "ink", 2.2)
    d.arrow([(110, 68), (110, 40), (809, 40), (809, 126)], "accent", 1.8, dash="6 5", rounded=12)
    d.label(460, 46, "promoted version", fill="accent", size=15)
    return d


def plugin_flow(T: dict) -> Doc:
    W, H = 960, 340
    d = Doc(W, H, T, "How a plugin reaches Hylo",
            "A plugin package declares entry points in its pyproject.toml, for example a guard named "
            "examples.slow_zone. The plugin registry in hylo-core finds it by name, and experiment configs use it by "
            "that name. This repository holds five example plugins: a guard, a gate test, an online learner and two "
            "policies.")
    d.card()
    d.rect(28, 32, 420, 128, "kernel", rx=14)
    code = [('[project.entry-points."hylo.guards"]', 0.7), ('"examples.slow_zone" =', 1.0),
            ('    "hylo_examples.guards:SlowZoneGuard"', 1.0)]
    for i, (line, op) in enumerate(code):
        d.text(48, 72 + i * 30, line, "mono", 15, "kernel_ink", opacity=op)
    d.box(508, 61, 180, 70, "Plugin registry", kind="accent", tsize=17)
    d.rect(746, 32, 186, 128, "surface", "line2", rx=14)
    d.text(766, 82, "type:", "mono", 15, "muted")
    d.text(766, 112, "examples.slow_zone", "monob", 14.5, "accent")
    d.arrow([(450, 96), (504, 96)], "accent", 2.2)
    d.arrow([(690, 96), (742, 96)], "accent", 2.2)
    cards = [("guard", "slow_zone"), ("gate test", "min_effect"), ("learner", "cem"), ("policy", "ik_reacher"),
             ("policy", "mixture")]
    g, x0 = 12, 28
    w = (W - 56 - g * 4) / 5
    for i, (kind, name) in enumerate(cards):
        x = x0 + i * (w + g)
        d.rect(x, 200, w, 108, "surface", "line2", rx=14)
        d.text(x + w / 2, 244, kind, "sb", 17, "ink", anchor="middle")
        d.text(x + w / 2, 276, name, "mono", 15, "accent", anchor="middle")
    return d


def deployments_sync(T: dict) -> Doc:
    W, H = 960, 360
    d = Doc(W, H, T, "Configs name runtimes; runs travel through the store",
            "On the robot computer, a workcell config names a runtime (remote: runtime robot); the machine's "
            "execution profile resolves it to a venv and environment variables. hylo serve workcell records "
            "episodes as runs in the robot's store. The workstation pulls runs it does not have, and pushes "
            "artifacts such as a judge or a memory back. Sealed artifacts are never overwritten.")
    d.card()
    d.rect(24, 24, 470, 312, "sunk", "line2", rx=16)
    d.text(44, 58, "Robot computer", "b", 18, "ink")
    d.rect(44, 80, 210, 88, "kernel", rx=12)
    d.text(64, 116, "remote:", "mono", 15, "kernel_ink")
    d.text(80, 144, "{runtime: robot}", "mono", 15, "kernel_ink")
    d.box(290, 80, 184, 88, "Execution profile", tsize=16.5)
    d.box(44, 228, 210, 80, "hylo serve workcell", kind="soft", tface="mono", tsize=15)
    d.box(290, 228, 184, 80, "Store", tsize=17)
    d.arrow([(256, 124), (286, 124)], "muted")
    d.arrow([(149, 170), (149, 224)], "muted")
    d.arrow([(382, 170), (382, 196), (200, 196), (200, 224)], "muted", dash="5 4")
    d.arrow([(256, 268), (286, 268)], "accent")
    d.rect(686, 24, 250, 312, "sunk", "line2", rx=16)
    d.text(706, 58, "Workstation", "b", 18, "ink")
    d.box(706, 80, 210, 88, "Studio", tsize=17)
    d.box(706, 228, 210, 80, "Store", tsize=17)
    d.arrow([(476, 250), (702, 250)], "accent", 2.2)
    d.label(589, 238, "pull runs", fill="accent", size=15)
    d.arrow([(702, 290), (476, 290)], "accent", 2.2)
    d.label(589, 278, "push artifacts", fill="accent", size=15)
    d.arrow([(811, 226), (811, 172)], "muted")
    return d


def studio_plane(T: dict) -> Doc:
    W, H = 960, 300
    d = Doc(W, H, T, "The studio control plane",
            "The browser connects with a role (viewer, operator or approver; the e-stop is open to every role) to "
            "hylo playground, the control plane. It starts episodes on workcells, runs hylo commands as jobs, and "
            "reads runs and campaigns through the catalog and development sessions from files. It never sends actions.")
    d.card()
    d.rect(28, 28, 236, 244, "sunk", "line2", rx=16)
    d.text(48, 64, "Browser", "b", 18, "ink")
    for i, role in enumerate(["viewer", "operator", "approver"]):
        d.pill(48 + i * 18, 92 + i * 52, role, face="mono", size=15, h=36, padx=14,
               fill="accent" if role == "approver" else "surface", stroke=None if role == "approver" else "line2",
               color="accent_ink" if role == "approver" else "ink")
    d.box(330, 110, 250, 80, "hylo playground", kind="accent", tface="mono", tsize=17)
    for i, t in enumerate(["Workcells", "Jobs", "Catalog", "Research records"]):
        y = 18 + i * 68
        d.box(648, y, 284, 56, t, tsize=17)
        d.arrow([(582, 150), (614, 150), (614, y + 28), (644, y + 28)], "accent" if i == 0 else "muted",
                rounded=12)
    d.arrow([(266, 150), (326, 150)], "accent", 2.2)
    return d


# ---------------------------------------------------------------- repositories
REPOS = [
    Repo("harness", ("hylo-", "harness"),
         "Develop robot skills, validate implementations and improve tested versions.",
         {"Kernel", "Cognition", "Evaluation", "Evolution"},
         [("architecture", harness_architecture), ("loop", improvement_loop)],
         {"campaign-mujoco-reach-gain.png": ("campaign-mujoco-reach-gain.png", None)}),
    Repo("bench", ("hylo-", "bench"), "Task environments and measured evidence for robot skills.",
         {"Evaluation"}, [("flow", bench_flow)],
         {"leaderboard-mujoco-reach.png": ("leaderboard-mujoco-reach.png", None),
          "libero-episode-strip.png": ("libero-episode-strip.png", None),
          "mujoco-scenes.png": ("mujoco-scenes.png", None)}),
    Repo("serve", ("hylo-", "serve"), "Run skill implementations on robots within configured safety limits.",
         {"Runtime"}, [("topology", serve_topology)]),
    Repo("studio", ("hylo-", "studio"), "Inspect skill development, validation evidence and deployed execution.",
         {"Workbench"}, [("control-plane", studio_plane)],
         {"studio-episode.png": ("studio-episode.png", "sidebar"),
          "studio-campaign.png": ("studio-campaign.png", "sidebar"),
          "studio-runs.png": ("studio-runs.png", "sidebar")}),
    Repo("plugins", ("hylo-", "plugins"),
         "Extend the kernel from outside: policies, environments, learners, guards and gate tests.",
         {"Kernel"}, [("flow", plugin_flow)]),
    Repo("deployments-template", ("<lab>", "-deployments"),
         "Your lab's private configs: workcells, calibration, safety limits and keep-out zones.",
         {"Runtime"}, [("sync", deployments_sync)]),
    Repo("docs", ("hylo-", "docs"), "Guides, benchmarking, design, RFCs and experiment records for the Hylo stack.",
         set()),
    Repo("site", ("hyloai", ".github.io"), "The Hylo website. Plain HTML, no build step.", set()),
    Repo("org-profile", ("", "Hylo"), "The stack for physical AI: every layer on one execution kernel.", set(), [("loop", improvement_loop)]),
]


def _copy_figure(src: Path, dst: Path, crop: str | None) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if crop is None:
        shutil.copyfile(src, dst)
        return
    from PIL import Image

    im = Image.open(src)
    if crop == "sidebar":                     # studio's navigation column: the product name lives there
        im = im.crop((232, 0, im.width, im.height))
    im.save(dst, optimize=True)


def main() -> None:
    for r in REPOS:
        if not (WORKSPACE / r.key).is_dir():
            print(f"skip {r.key}: not checked out")
            continue
        out = r.assets
        for theme, T in THEMES.items():
            banner(T, r).save(out / f"banner-{theme}.svg")
            stack_map(T, r).save(out / f"stack-{theme}.svg")
            for name, fn in r.figures:
                fn(T).save(out / f"{name}-{theme}.svg")
        for name, (src, crop) in r.copies.items():
            _copy_figure(FIGURES / src, out / name, crop)
        print(f"{r.key}: {sorted(p.name for p in out.iterdir())}")


if __name__ == "__main__":
    main()
