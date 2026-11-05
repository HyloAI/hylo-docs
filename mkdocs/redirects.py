"""Keep published URLs working after pages move, without indexing duplicate content."""

from html import escape
import json
import shutil
from pathlib import Path
from urllib.parse import urljoin

from mkdocs.structure.files import File
from mkdocs.utils import get_relative_url


REDIRECTS = {
    'showcase/studio.md': 'developer-guide/validation/studio.md',
    'showcase/core.md': 'developer-guide/validation/core.md',
    'showcase/memory.md': 'developer-guide/validation/memory.md',
    'showcase/agents.md': 'developer-guide/validation/agents.md',
    'showcase/instruments.md': 'developer-guide/validation/instruments.md',
    'showcase/learning.md': 'developer-guide/validation/learning.md',
    'showcase/evolution.md': 'developer-guide/validation/evolution.md',
    'showcase/benchmarks.md': 'developer-guide/validation/benchmarks.md',
    'showcase/plugins.md': 'developer-guide/validation/plugins.md',
    'showcase/runtime.md': 'developer-guide/validation/runtime.md',
    'showcase/tool-agents.md': 'developer-guide/validation/tool-agents.md',
    'showcase/phase-guided.md': 'developer-guide/validation/phase-guided.md',
    'showcase/video-memory.md': 'developer-guide/validation/video-memory.md',
    'showcase/system-results.md': 'developer-guide/validation/index.md',
    'showcase/tool-agents-robot-toolkit.md': 'developer-guide/validation/tool-agents-robot-toolkit.md',
    'showcase/tool-agents-program-improvement.md': 'developer-guide/validation/tool-agents-program-improvement.md',
    'showcase/tool-agents-scene-builder.md': 'developer-guide/validation/tool-agents-scene-builder.md',
    'showcase/tool-agents-free-form-scenes.md': 'developer-guide/validation/tool-agents-free-form-scenes.md',
    'showcase/tool-agents-replay-to-simulation.md': 'developer-guide/validation/tool-agents-replay-to-simulation.md',
    'showcase/tool-agents-motion-studio.md': 'developer-guide/validation/tool-agents-motion-studio.md',
    'showcase/tool-agents-motion-characters-and-free-mode.md': 'developer-guide/validation/tool-agents-motion-characters-and-free-mode.md',
    'showcase/tool-agents-two-arms-and-a-humanoid.md': 'developer-guide/validation/tool-agents-two-arms-and-a-humanoid.md',
    'showcase/tool-agents-libero.md': 'developer-guide/validation/tool-agents-libero.md',
    'showcase/tool-agents-perception-and-motion-tools.md': 'developer-guide/validation/tool-agents-perception-and-motion-tools.md',
    'showcase/tool-agents-live-code-as-policy-runs.md': 'developer-guide/validation/tool-agents-live-code-as-policy-runs.md',
    'showcase/tool-agents-tool-calling-agents.md': 'developer-guide/validation/tool-agents-tool-calling-agents.md',
    'showcase/tool-agents-worlds.md': 'developer-guide/validation/tool-agents-worlds.md',
    'showcase/tool-agents-what-does-not-work-yet.md': 'developer-guide/validation/tool-agents-what-does-not-work-yet.md',
    'showcase/tool-agents-credits.md': 'developer-guide/validation/tool-agents-credits.md',

    "getting-started/concepts.md": "user-guide/overview.md",
    "concepts/worlds.md": "user-guide/worlds/overview.md",
}


def on_post_build(config):
    # Preserve published image URLs as well as document URLs. The public build
    # already excludes internal Studio assets from this source directory.
    assets = Path(config.site_dir) / "developer-guide/validation/assets"
    if assets.is_dir():
        shutil.copytree(assets, Path(config.site_dir) / "showcase/assets", dirs_exist_ok=True)
    for source, target in REDIRECTS.items():
        old = File(source, config.docs_dir, config.site_dir, config.use_directory_urls)
        new = File(target, config.docs_dir, config.site_dir, config.use_directory_urls)
        if not Path(new.abs_dest_path).is_file():
            if target == "developer-guide/validation/studio.md":
                continue  # Studio records are excluded from the public site.
            if target.startswith("developer-guide/validation/tool-agents-"):
                # A checkout without hylo-code-agents generates only the index.
                target = "developer-guide/validation/tool-agents.md"
                new = File(target, config.docs_dir, config.site_dir, config.use_directory_urls)
        if not Path(new.abs_dest_path).is_file():
            raise ValueError(f"Redirect target was not built: {target}")
        destination = Path(old.abs_dest_path)
        if destination.exists():
            raise ValueError(f"Redirect would overwrite a page: {source}")
        relative = get_relative_url(new.url, old.url)
        canonical = urljoin(config.site_url, new.url) if config.site_url else relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n'
            '<title>Page moved</title><meta name="robots" content="noindex">\n'
            f'<link rel="canonical" href="{escape(canonical, quote=True)}">\n'
            '<script>location.replace('
            f'{json.dumps(relative)} + location.search + location.hash);</script>\n'
            f'<meta http-equiv="refresh" content="0; url={escape(relative, quote=True)}">\n'
            '</head><body><article><p>This page has moved. '
            f'<a href="{escape(relative, quote=True)}">Continue to the guide.</a>'
            '</p></article></body></html>\n',
            encoding="utf-8",
        )
