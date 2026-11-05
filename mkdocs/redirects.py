"""Keep published URLs working after pages move, without indexing duplicate content."""

from html import escape
import json
from pathlib import Path
from urllib.parse import urljoin

from mkdocs.structure.files import File
from mkdocs.utils import get_relative_url


REDIRECTS = {
    "getting-started/concepts.md": "user-guide/overview.md",
    "concepts/worlds.md": "user-guide/worlds/overview.md",
}


def on_post_build(config):
    for source, target in REDIRECTS.items():
        old = File(source, config.docs_dir, config.site_dir, config.use_directory_urls)
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
