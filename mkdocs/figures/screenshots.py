"""Screenshots of studio (the playground) for the docs site (docs/assets/figures/studio-*.png).

    python docs/mkdocs/figures/screenshots.py [--url http://127.0.0.1:8765]

Needs a running playground (`hylo playground --repo <bench checkout>`) and Playwright with a Chromium build
(`pip install playwright`; `playwright install chromium`, or an existing ~/.cache/ms-playwright build).
"""

from __future__ import annotations

import argparse
import json
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "docs" / "assets" / "figures"
RUN = "l10-ab-critic-search_val-73dc98eaf0df4917-45b6ba"   # SmolVLA + chunk critic on LIBERO-10, with frames
CAMPAIGN = "evolve/libero10-llm"


def get(url: str):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read())


def main() -> None:
    from playwright.sync_api import sync_playwright

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--url", default="http://127.0.0.1:8765")
    ap.add_argument("--run", default=RUN)
    ap.add_argument("--campaign", default=CAMPAIGN)
    a = ap.parse_args()
    run = get(f"{a.url}/api/runs/{a.run}")
    episode = next(s["episode_id"] for s in run["samples"] if s["status"] == "success")
    pages = {"studio-runs.png": "/runs",
             "studio-episode.png": f"/runs/{a.run}/episodes/{urllib.parse.quote(episode)}",
             "studio-campaign.png": f"/campaigns/{urllib.parse.quote(a.campaign, safe='')}"}
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900}, color_scheme="light", device_scale_factor=1)
        for name, path in pages.items():
            page.goto(a.url + path, wait_until="networkidle")
            page.wait_for_timeout(2500)                    # frames and charts load after the first paint
            page.screenshot(path=str(OUT / name))
            print(OUT / name)
        browser.close()


if __name__ == "__main__":
    main()
