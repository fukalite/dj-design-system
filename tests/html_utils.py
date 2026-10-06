"""Helpers for asserting on rendered component HTML and component CSS."""

from html.parser import HTMLParser
from pathlib import Path

from django.template import Context, Template

import dj_design_system


STATIC = Path(dj_design_system.__file__).parent / "static" / "dj_design_system"


def render(source: str, **context) -> str:
    html = Template("{% load design_components %}" + source).render(Context(context))
    return html.strip()


class _Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def tags(html: str) -> list[tuple[str, dict[str, str | None]]]:
    """Return ``(tag, attrs)`` for every start tag, in document order."""
    parser = _Tags()
    parser.feed(html)
    return parser.tags


def root(html: str) -> tuple[str, dict[str, str | None]]:
    return tags(html)[0]


def css_homes(selector: str) -> list[str]:
    """Return the stylesheets (relative to the app's static dir) with a rule
    whose line starts with ``selector``, e.g. ``".gallery-params {"``."""
    return [
        str(path.relative_to(STATIC))
        for path in sorted(STATIC.rglob("*.css"))
        if any(line.startswith(selector) for line in path.read_text().splitlines())
    ]
