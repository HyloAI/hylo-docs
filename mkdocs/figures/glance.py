"""Overview figures in the infographic style: coloured columns, line icons, numbered lanes.

Registered in diagrams.py (DIAGRAMS) and generated with the other diagrams, in a light and a dark version. These
figures use a small categorical palette (one hue per layer) in addition to the site's cinnabar, which stays reserved
for Physical RSI. Icons are drawn here as simple strokes on a 24-unit grid.
"""

from __future__ import annotations

from readme_art import Doc, measure

# ---------------------------------------------------------------- palette: one hue per layer, per theme
HUES = {
    "light": {"green": ("#2f855a", "#e8f4ec"), "blue": ("#2563a6", "#e7eef8"), "indigo": ("#4a4fb8", "#ebebf8"),
              "violet": ("#7a4bb0", "#f1eaf8"), "teal": ("#127a7a", "#e3f2f1"), "amber": ("#a8660b", "#fbf0dc"),
              "rose": ("#b23a55", "#f9e6eb")},
    "dark": {"green": ("#3f9d6b", "#16241c"), "blue": ("#3f82c9", "#152131"), "indigo": ("#6b70d6", "#1b1c30"),
             "violet": ("#9a6fd0", "#231a2e"), "teal": ("#2a9b9b", "#122525"), "amber": ("#c98a2c", "#2a2013"),
             "rose": ("#d0607b", "#2d1820")},
}


def hue(d: Doc, name: str) -> tuple[str, str]:
    """(strong, tint) of a hue in the document's theme."""
    return HUES["dark" if d.T["bg"] == "#121416" else "light"][name]


# ---------------------------------------------------------------- icons (24-unit grid, stroked)
ICONS = {
    "terminal": '<rect x="2.5" y="4" width="19" height="16" rx="2.5"/><path d="M6.5 9.5l3 2.5-3 2.5M12 15h5"/>',
    "plug": '<path d="M9 2.5v5M15 2.5v5M6 7.5h12v4a6 6 0 0 1-12 0zM12 17.5v4"/>',
    "chat": '<path d="M4 4.5h16v11H10l-5 4v-4H4z"/><path d="M8.5 10h.01M12 10h.01M15.5 10h.01"/>',
    "code": '<path d="M8 7l-5 5 5 5M16 7l5 5-5 5M14 4.5l-4 15"/>',
    "arm": '<path d="M3.5 20.5h11M7 20.5v-4M7 16.5l4.5-7.5 6 3M17.5 12l3-2M17.5 12l3 2"/>'
           '<circle cx="7" cy="16.5" r="1.7"/><circle cx="11.5" cy="9" r="1.7"/>',
    "loop": '<path d="M20 11a8 8 0 0 0-14.6-4.4M4.5 3.5v3.6h3.6M4 13a8 8 0 0 0 14.6 4.4M19.5 20.5v-3.6h-3.6"/>',
    "shield": '<path d="M12 2.8l8 3v6.2c0 5-3.4 8.2-8 9.4-4.6-1.2-8-4.4-8-9.4V5.8z"/><path d="M8.6 12l2.4 2.4 4.4-4.6"/>',
    "list": '<path d="M9 6.5h11M9 12h11M9 17.5h11M4.5 6.5h.01M4.5 12h.01M4.5 17.5h.01"/>',
    "cube": '<path d="M12 2.5l8.5 4.8v9.4L12 21.5l-8.5-4.8V7.3z"/><path d="M3.8 7.4L12 12l8.2-4.6M12 12v9.3"/>',
    "flask": '<path d="M9 3h6M10 3v6.2L5 18a2 2 0 0 0 1.8 3h10.4A2 2 0 0 0 19 18l-5-8.8V3M7.5 14.5h9"/>',
    "eye": '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/>',
    "server": '<rect x="3" y="3.5" width="18" height="7" rx="2"/><rect x="3" y="13.5" width="18" height="7" rx="2"/>'
              '<path d="M7 7h.01M7 17h.01"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="M8 12.2l2.7 2.7L16 9.6"/>',
    "upload": '<path d="M12 16V4M7 9l5-5 5 5M4 20h16"/>',
    "bars": '<path d="M5 20v-7M12 20V5M19 20v-10M3 20.5h18"/>',
    "layers": '<path d="M12 3l9 5-9 5-9-5zM3 13l9 5 9-5"/>',
    "star": '<path d="M12 3.2l2.6 5.5 6 .7-4.5 4.1 1.2 6L12 16.6l-5.3 2.9 1.2-6L3.4 9.4l6-.7z"/>',
    "book": '<path d="M4 4.5h6a2 2 0 0 1 2 2v13a2 2 0 0 0-2-2H4zM20 4.5h-6a2 2 0 0 0-2 2v13a2 2 0 0 1 2-2h6z"/>',
    "wrench": '<path d="M14.5 6.5a4.2 4.2 0 0 0 5.2 5.2l-8.6 8.6a2.1 2.1 0 0 1-3-3l8.6-8.6a4.2 4.2 0 0 0-5.2-5.2"/>'
              '<path d="M14.5 6.5l2.8 2.8"/>',
    "database": '<ellipse cx="12" cy="5.5" rx="8" ry="3"/><path d="M4 5.5v13c0 1.7 3.6 3 8 3s8-1.3 8-3v-13'
                'M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    "person": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/>',
    "lock": '<rect x="4.5" y="10.5" width="15" height="10.5" rx="2"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/>',
    "pin": '<path d="M12 21.5s-6.5-6-6.5-11a6.5 6.5 0 0 1 13 0c0 5-6.5 11-6.5 11z"/><circle cx="12" cy="10.5" r="2.3"/>',
    "brain": '<path d="M9 4.5a3 3 0 0 0-3 3 3 3 0 0 0-2 5.2A3.2 3.2 0 0 0 7 18a3 3 0 0 0 5 1.2V5.7A3 3 0 0 0 9 4.5z'
             'M15 4.5a3 3 0 0 1 3 3 3 3 0 0 1 2 5.2A3.2 3.2 0 0 1 17 18a3 3 0 0 1-5 1.2"/>',
    "gauge": '<path d="M4 17a8 8 0 1 1 16 0"/><path d="M12 17l4-5"/>',
    "cross": '<circle cx="12" cy="12" r="9"/><path d="M9 9l6 6M15 9l-6 6"/>',
}


def chips(d: Doc, x, y, w, items, stroke, fill="surface", size=14.5, h=26, gap=6, face="m") -> float:
    """Small boxes for the parts inside a container: laid out in rows that wrap and are centred in [x, x + w].
    Returns the height used."""
    rows, row, rw = [], [], 0.0
    for it in items:
        iw = measure(it, face, size) + 18
        if row and rw + gap + iw > w:
            rows.append((row, rw)); row, rw = [], 0.0
        rw = rw + (gap if row else 0) + iw
        row.append((it, iw))
    if row:
        rows.append((row, rw))
    for r, (row, rw) in enumerate(rows):
        cx = x + (w - rw) / 2
        ry = y + r * (h + gap)
        for it, iw in row:
            d.rect(cx, ry, iw, h, fill, stroke, rx=6, sw=1.1)
            d.text(cx + 9, ry + h / 2 + size * 0.36, it, face, size, "ink")
            cx += iw + gap
    return len(rows) * (h + gap) - gap


def icon(d: Doc, name: str, x: float, y: float, size: float, color: str, sw: float = 1.9) -> None:
    """A line icon whose top-left corner is (x, y)."""
    s = size / 24
    d.add(f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.4f})" fill="none" stroke="{d.c(color)}" '
          f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>')


def header(d: Doc, x, y, w, h, title, color, size=16) -> None:
    """A saturated header bar with white text, rounded on top."""
    d.add(f'<path d="M{x} {y + h} V{y + 10} a10 10 0 0 1 10 -10 H{x + w - 10} a10 10 0 0 1 10 10 V{y + h} z" '
          f'fill="{color}"/>')
    size = min(size, size * (w - 20) / measure(title, "b", size))
    d.text(x + w / 2, y + h / 2 + size * 0.36, title, "b", size, "#ffffff", anchor="middle")


def column(d: Doc, x, y, w, h, title, hname, hh=40) -> tuple[str, str]:
    strong, tint = hue(d, hname)
    d.add(f'<path d="M{x} {y + hh} H{x + w} V{y + h - 10} a10 10 0 0 1 -10 10 H{x + 10} a10 10 0 0 1 -10 -10 z" '
          f'fill="{tint}"/>')
    header(d, x, y, w, hh, title, strong)
    return strong, tint


def chip(d: Doc, cx, y, s, strong, tint, h=30, size=15, ic=None, w=None) -> float:
    """A centred chip; returns its width."""
    tw = measure(s, "sb", size) + (24 if ic else 0)
    w = w or tw + 26
    x = cx - w / 2
    d.rect(x, y, w, h, "surface", strong, rx=8, sw=1.2)
    tx = cx - tw / 2
    if ic:
        icon(d, ic, tx, y + h / 2 - 9, 18, strong)
        tx += 24
    d.text(tx, y + h / 2 + size * 0.36, s, "sb", size, "ink")
    return w


def icon_card(d: Doc, x, y, w, h, ic, lines, strong, solid=False, size=16) -> None:
    """A card with a centred icon above one or two centred lines of text."""
    if solid:
        d.rect(x, y, w, h, strong, strong, rx=10)
        col = "#ffffff"
    else:
        d.rect(x, y, w, h, "surface", strong, rx=10, sw=1.4)
        col = strong
    lines = lines if isinstance(lines, list) else [lines]
    block = 30 + 8 + len(lines) * (size + 4)
    top = y + (h - block) / 2
    icon(d, ic, x + w / 2 - 15, top, 30, col, sw=1.8)
    for i, ln in enumerate(lines):
        d.text(x + w / 2, top + 38 + size * 0.8 + i * (size + 4), ln, "b", size, "#ffffff" if solid else "ink",
               anchor="middle")


# ---------------------------------------------------------------- 1. Hylo at a glance (home page)
def h_card(d: Doc, x, y, w, h, ic, label, strong, solid=False, size=16) -> None:
    """A card with an icon on the left and a short label."""
    d.rect(x, y, w, h, strong if solid else "surface", strong, rx=10, sw=1.4)
    col = "#ffffff" if solid else strong
    icon(d, ic, x + 16, y + h / 2 - 12, 24, col)
    d.text(x + 52, y + h / 2 + size * 0.36, label, "b", size, "#ffffff" if solid else "ink")


def at_a_glance(T: dict) -> Doc:
    d = Doc(960, 486, T, "Hylo at a glance",
            "Three control modes, general models, hybrid control and action models, run through one execution "
            "layer: the episode loop, the safety shield and traces, on worlds, benchmarks and real robots. Physical "
            "RSI turns outcomes into improvements, verifies them and deploys them back into control. Serve provides "
            "model serving to every layer.")
    d.card()
    top, bh = 16, 300
    c2 = column(d, 16, top, 404, bh, "Control", "blue")
    c3 = column(d, 444, top, 216, bh, "Execution", "indigo")
    c4 = column(d, 698, top, 246, bh, "Environments", "violet")
    for i, (num, title) in enumerate([("01", "General models"), ("02", "Hybrid control"), ("03", "Action models")]):
        ly = 72 + i * 80
        d.rect(30, ly, 376, 66, "surface", c2[1], rx=10)
        d.add(f'<circle cx="62" cy="{ly + 33}" r="17" fill="{c2[0]}"/>')
        d.text(62, ly + 38, num, "b", 14, "#ffffff", anchor="middle")
        d.text(94, ly + 39, title, "b", 17, "ink")
        d.arrow([(408, ly + 33), (440, ly + 33)], c2[0], 2.4)
    for i, (ic, s) in enumerate([("loop", "Episode loop"), ("shield", "Safety shield"), ("list", "Traces")]):
        h_card(d, 458, 72 + i * 80, 188, 66, ic, s, c3[0], solid=True)
    for i, (ic, s) in enumerate([("cube", "Worlds"), ("flask", "Benchmarks"), ("arm", "Real robots")]):
        h_card(d, 712, 72 + i * 80, 218, 66, ic, s, c4[0])
    d.arrow([(663, 185), (695, 185)], c4[0], 2.6, both=True)

    d.rect(16, 334, 928, 84, "accent_soft", "accent", rx=12, sw=1.6)
    d.text(36, 382, "Physical RSI", "b", 17, "accent")
    cards = [("Deploy", "upload"), ("Verify", "check"), ("Improve", "bars"), ("Outcomes", "eye")]
    xs = [176, 368, 560, 752]
    for x, (s, ic) in zip(xs, cards):
        d.rect(x, 354, 172, 44, "surface", "accent", rx=8, sw=1.2)
        tw = measure(s, "sb", 16) + 28
        icon(d, ic, x + 86 - tw / 2, 365, 20, "accent")
        d.text(x + 86 - tw / 2 + 28, 381.5, s, "sb", 16, "ink")
    for a, b in zip(xs, xs[1:]):
        d.arrow([(b - 3, 376), (a + 172 + 5, 376)], "accent", 2.2)
    d.arrow([(262, 352), (262, 320)], "accent", 2.6)
    d.arrow([(838, 318), (838, 350)], "accent", 2.6)

    d.rect(16, 432, 928, 40, "kernel", "kernel", rx=12)
    tw = measure("Serve", "b", 17) + 30
    icon(d, "server", 480 - tw / 2, 441, 22, "kernel_ink")
    d.text(480 - tw / 2 + 30, 458, "Serve", "b", 17, "kernel_ink")
    return d


# ---------------------------------------------------------------- 2. control modes
def control_modes(T: dict) -> Doc:
    d = Doc(960, 372, T, "One loop, three control modes",
            "General models such as Claude, GPT, Qwen and gpt-oss call robot tools. In hybrid control a language or "
            "vision model plans for a vision-language-action model. Action models such as SmolVLA, pi0 and pi0.5 "
            "act directly. All three run through the same Hylo kernel and safety shield, in the same loop.")
    d.card()
    cards = [("General models", ["Claude", "GPT", "Qwen", "gpt-oss"], "blue", ("LLM / VLM", "Tools")),
             ("Hybrid control", ["LLM / VLM", "VLA"], "teal", ("Planner", "VLA")),
             ("Action models", ["SmolVLA", "π0", "π0.5"], "violet", ("VLA",))]
    for i, (title, models, hname, top_boxes) in enumerate(cards):
        strong, tint = hue(d, hname)
        x, w = 16 + i * 314, 300
        cx = x + w / 2
        d.rect(x, 16, w, 284, tint, strong, rx=14, sw=1.2)
        d.text(x + 20, 50, title, "b", 21, "ink")
        chips(d, x + 12, 64, w - 24, models, strong, size=14.5, h=26)
        if len(top_boxes) == 2:
            d.rect(x + 20, 108, 110, 44, "surface", strong, rx=8, sw=1.2)
            d.text(x + 75, 136, top_boxes[0], "sb", 16, "ink", anchor="middle")
            d.rect(x + 170, 108, 110, 44, "surface", strong, rx=8, sw=1.2)
            d.text(x + 225, 136, top_boxes[1], "sb", 16, "ink", anchor="middle")
            d.arrow([(x + 133, 130), (x + 166, 130)], strong, 2, both=(i == 1))
        else:
            d.rect(x + 30, 108, w - 60, 44, "surface", strong, rx=8, sw=1.2)
            d.text(cx, 136, top_boxes[0], "sb", 16, "ink", anchor="middle")
        d.arrow([(cx, 155), (cx, 176)], strong, 2)
        d.rect(x + 30, 180, w - 60, 44, "kernel", "kernel", rx=8)
        d.text(cx, 208, "Hylo kernel", "sb", 16, "kernel_ink", anchor="middle")
        d.arrow([(cx, 227), (cx, 248)], strong, 2)
        d.rect(x + 30, 252, w - 60, 36, "surface", strong, rx=8, sw=1.2)
        d.text(cx, 276, "Robot", "sb", 16, "ink", anchor="middle")
    d.rect(16, 314, 928, 44, "accent_soft", "accent", rx=12, sw=1.5)
    s = "One loop for every mode"
    tw = measure(s, "b", 16.5) + 30
    icon(d, "loop", 480 - tw / 2, 325, 22, "accent")
    d.text(480 - tw / 2 + 30, 342, s, "b", 16.5, "accent")
    return d


# ---------------------------------------------------------------- 3. architecture at a glance (overview page)
def architecture_glance(T: dict) -> Doc:
    d = Doc(960, 514, T, "Hylo architecture at a glance",
            "Improvement: proposers make candidates, the gate decides, and a version is promoted. The store keeps "
            "runs, traces, artifacts, versions and skills. Every episode runs on one loop: the agent proposes an "
            "action, the safety shield reviews it and the environment executes it. Serve provides model serving. "
            "Five properties hold throughout: one episode loop, one safety shield, sealed traces, a protected scope "
            "and pinned robot packs.")
    d.card()
    amb, ind = hue(d, "amber"), hue(d, "indigo")

    def plane(y, h, ic, title, color):
        d.rect(16, y, 140, h, "surface", color, rx=12, sw=1.4)
        icon(d, ic, 74, y + h / 2 - 26, 24, color)
        d.text(86, y + h / 2 + 18, title, "b", 16, color, anchor="middle")

    plane(16, 76, "bars", "Improve", d.c("accent"))
    xs = [176, 370, 564, 758]
    for x, s in zip(xs, ["Proposers", "Candidates", "Gate", "Versions"]):
        gate = s == "Gate"
        d.rect(x, 30, 172, 48, "accent" if gate else "surface", "accent", rx=10, sw=1.4)
        d.text(x + 86, 60, s, "sb", 16, "accent_ink" if gate else "ink", anchor="middle")
    for a, b in zip(xs, xs[1:]):
        d.arrow([(a + 174, 54), (b - 4, 54)], "accent", 2)

    plane(108, 76, "database", "Store", amb[0])
    d.rect(172, 108, 772, 76, amb[1], amb[0], rx=12, sw=1.2)
    chips(d, 188, 131, 740, ["runs", "traces", "artifacts", "versions", "skills"], amb[0], size=15, h=30, gap=14)

    plane(200, 150, "loop", "Run", ind[0])
    d.rect(172, 200, 772, 150, ind[1], ind[0], rx=12, sw=1.2)
    d.rect(192, 216, 224, 92, "surface", ind[0], rx=10, sw=1.3)
    d.text(304, 244, "Agent", "b", 16, "ink", anchor="middle")
    chips(d, 200, 262, 208, ["policy", "reasoner", "tools"], ind[0], fill=ind[1])
    d.rect(456, 232, 150, 60, "accent", "accent", rx=10)
    icon(d, "shield", 474, 250, 24, "accent_ink")
    d.text(550, 268, "Shield", "b", 16, "accent_ink", anchor="middle")
    d.rect(646, 216, 282, 92, "surface", ind[0], rx=10, sw=1.3)
    d.text(787, 244, "Environment", "b", 16, "ink", anchor="middle")
    chips(d, 654, 262, 266, ["worlds", "benchmarks", "robots"], ind[0], fill=ind[1])
    d.arrow([(418, 262), (452, 262)], "accent", 2.2)
    d.arrow([(608, 262), (642, 262)], "accent", 2.2)
    d.arrow([(787, 310), (787, 330), (304, 330), (304, 312)], ind[0], 2, rounded=10)

    d.rect(16, 366, 928, 40, "kernel", "kernel", rx=12)
    tw = measure("Serve", "b", 16) + 30
    icon(d, "server", 480 - tw / 2, 375, 22, "kernel_ink")
    d.text(480 - tw / 2 + 30, 392, "Serve", "b", 16, "kernel_ink")

    props = [("loop", "One loop", "indigo"), ("shield", "One shield", "rose"), ("lock", "Sealed traces", "amber"),
             ("check", "Protected scope", "green"), ("pin", "Pinned robots", "violet")]
    for i, (ic, title, hname) in enumerate(props):
        strong, tint = hue(d, hname)
        x = 16 + i * 188
        d.rect(x, 422, 176, 76, tint, strong, rx=12, sw=1.3)
        icon(d, ic, x + 76, 434, 24, strong)
        d.text(x + 88, 482, title, "b", 15.5, strong, anchor="middle")
    return d


# ---------------------------------------------------------------- 4. model side, record, robot side (concepts)
def model_and_robot(T: dict) -> Doc:
    d = Doc(960, 380, T, "Model side, record and robot side",
            "A chat model proposes actions through a tool surface; controllers and the safety shield execute them "
            "on a simulator or a robot and measure the result. The two sides meet only through the record of "
            "proposals, receipts and the trace. The task's own check reads the record and decides success.")
    d.card()
    blue, amb, rose = hue(d, "blue"), hue(d, "amber"), hue(d, "rose")
    panels = [(16, "Model side", blue, [("chat", "Chat model"), ("wrench", "Tool surface"), ("brain", "Session")]),
              (346, "The record", amb, [("book", "Proposals"), ("book", "Receipts"), ("lock", "Trace")]),
              (676, "Robot side", rose, [("gauge", "Controllers"), ("shield", "Safety shield"), ("arm", "Robot")])]
    for x, title, (strong, tint), items in panels:
        d.rect(x, 16, 268, 268, tint, strong, rx=16, sw=1.3, dash="6 5" if title == "The record" else None)
        d.text(x + 134, 50, title, "b", 18, strong, anchor="middle")
        for j, (ic, s) in enumerate(items):
            y = 72 + j * 68
            d.rect(x + 20, y, 228, 52, "surface", strong, rx=10, sw=1.3)
            icon(d, ic, x + 36, y + 14, 24, strong)
            d.text(x + 72, y + 32, s, "sb", 16, "ink")
    for (xa, xb, y, col, lab) in [(286, 344, 98, blue[0], "propose"), (616, 674, 98, amb[0], "execute"),
                                  (674, 616, 166, rose[0], "measure"), (344, 286, 166, amb[0], "read")]:
        d.arrow([(xa, y), (xb, y)], col, 2.4)
        d.label((xa + xb) / 2, y - 10, lab, fill=col, size=14.5, plate="bg")
    d.rect(366, 306, 228, 56, "accent", "accent", rx=12)
    icon(d, "check", 384, 320, 28, "accent_ink")
    d.text(422, 340, "Task check", "b", 17, "accent_ink")
    d.arrow([(480, 286), (480, 302)], "accent", 2.2)
    return d
