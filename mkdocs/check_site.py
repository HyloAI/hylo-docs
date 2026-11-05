"""Check a built documentation site's local article links, fragments and placeholders.

    python docs/mkdocs/check_site.py /tmp/hylo-docs-full
    python docs/mkdocs/check_site.py /tmp/hylo-docs-public --url-prefix /hylo-docs/

External URLs are not fetched. Paths are resolved as a browser would resolve directory URLs.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
import posixpath
import re
from urllib.parse import unquote, urlsplit


class Article(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.in_article = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if value := attributes.get("id"):
            self.ids.add(value)
        if tag == "article":
            self.in_article = True
        if self.in_article:
            for name in ("href", "src", "poster"):
                if value := attributes.get(name):
                    self.links.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag == "article":
            self.in_article = False


def check(root: Path, url_prefix: str = "/") -> list[str]:
    parsed: dict[str, Article] = {}
    failures: list[str] = []
    for path in sorted(root.rglob("*.html")):
        relative = path.relative_to(root).as_posix()
        html = path.read_text()
        article = Article()
        article.feed(html)
        parsed[relative] = article
        if re.search(r'<p class="admonition-title">(?:Not built|Not written yet)</p>', html):
            failures.append(f"{relative}: generated content is missing")
    if not parsed:
        return [f"{root}: no HTML pages found"]
    for relative, article in parsed.items():
        for url in article.links:
            parts = urlsplit(url)
            if parts.scheme or parts.netloc or not (parts.path or parts.fragment):
                continue
            path = unquote(parts.path)
            if path.startswith("/"):
                if not path.startswith(url_prefix):
                    continue  # A link elsewhere on the hosting origin.
                path = path.removeprefix(url_prefix)
            else:
                path = posixpath.normpath(posixpath.join(posixpath.dirname(relative), path)) if path else relative
            target = root / path
            if target.is_dir():
                target = target / "index.html"
            if not target.is_file():
                failures.append(f"{relative}: missing file: {url}")
                continue
            target_key = target.relative_to(root).as_posix()
            if parts.fragment and target_key in parsed and unquote(parts.fragment) not in parsed[target_key].ids:
                failures.append(f"{relative}: missing anchor: {url}")
    return sorted(set(failures))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", type=Path)
    parser.add_argument("--url-prefix", default="/")
    args = parser.parse_args()
    failures = check(args.site.resolve(), args.url_prefix)
    for failure in failures:
        print(failure)
    print(f"{len(failures)} local-link, fragment or generated-content failures")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
