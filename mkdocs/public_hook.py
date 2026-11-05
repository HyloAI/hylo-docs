"""MkDocs hook for the public site (mkdocs.public.yml): internal pages are left out, links to them become plain
text, studio screenshots are dropped, mentions of research notes are generic."""

import posixpath
import re

INTERNAL = ("internal/", "rfcs/", "research/", "EXECUTIVE-SUMMARY.md", "design/", "developer-guide/docs.md")
KEEP = ("design/overview.md",)
LINK = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)\)")
STUDIO_SHOT = re.compile(r"^!\[[^\]]*\]\([^)]*studio-[a-z]+\.png\)(\{[^}]*\})?\s*\n(\s*\n)?(\*[^\n]*\*\s*\n)?", re.M)


def on_config(config):
    """Derive public navigation from the full site's single navigation source."""
    def public_nav(node):
        if isinstance(node, str):
            excluded = node.startswith(INTERNAL) and node not in KEEP
            return None if excluded or node == "showcase/studio.md" else node
        if isinstance(node, list):
            return [value for child in node if (value := public_nav(child))]
        return {title: value for title, child in node.items()
                if title != "Internal" and (value := public_nav(child))}

    config["nav"] = public_nav(config["nav"])
    return config


def _internal(page_uri: str, target: str) -> bool:
    if re.match(r"^[a-z]+:", target) or target.startswith("#"):
        return False
    path = target.split("#", 1)[0]
    if not path:
        return False
    full = posixpath.normpath(posixpath.join(posixpath.dirname(page_uri), path))
    return full.startswith(INTERNAL) and full not in KEEP


def on_page_markdown(markdown, page, config, files):
    uri = page.file.src_uri
    markdown = LINK.sub(lambda m: m.group(1) if _internal(uri, m.group(2)) else m.group(0), markdown)
    markdown = STUDIO_SHOT.sub("", markdown)
    if uri == "index.md":
        markdown = markdown.replace("this site: design, RFCs, research notes and experiment records",
                                    "this documentation")
    return markdown

RESEARCH_PATH = re.compile(r"(?:\.\./)*research/[\w/.-]+\.md(?: §\d+)?(?:, (?:\.\./)*research/[\w/.-]+\.md(?: §\d+)?)*")


def on_page_content(html, page, config, files):
    # docstrings rendered by mkdocstrings and plain-text mentions of internal notes
    return RESEARCH_PATH.sub("our research notes", html)
