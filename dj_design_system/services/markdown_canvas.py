"""Markdown extension for embedding live canvas previews.

Provides a ``CanvasExtension`` that registers a ``Preprocessor`` to find
fenced ``canvas`` blocks and replace them with an HTML widget containing
a live preview iframe and a syntax-highlighted code block.

Syntax
------
In markdown files::

    ```canvas
    {% icon "check" size="large" %}
    ```

Block components::

    ```canvas
    {% callout type="warning" %}Warning content{% endcallout %}
    ```

The preprocessor parses the Django template tag syntax, builds a
``CanvasSpec``, and outputs an iframe (``src`` URL pointing to ``_canvas/``)
plus a highlighted code block with a toggle.
"""

from __future__ import annotations

import html
import re
from typing import TYPE_CHECKING

from django.template.loader import render_to_string
from markdown import Extension
from markdown.postprocessors import Postprocessor
from markdown.preprocessors import Preprocessor

from dj_design_system.services.canvas_renderer import (
    build_canvas_srcdoc,
    render_canvas_block,
)
from dj_design_system.services.registry import component_registry
from dj_design_system.services.tag_signature import highlight_code, highlight_html


if TYPE_CHECKING:
    from markdown import Markdown


# ---------------------------------------------------------------------------
# Widget HTML builder
# ---------------------------------------------------------------------------


def _build_widget_html(
    source: str,
    srcdoc: str,
    rendered_html: str,
    unique_id: str,
) -> str:
    """Build the HTML widget with preview iframe, code block, and toggle.

    Radio inputs are placed as direct children of the wrapper so CSS
    ``:checked ~ .target`` selectors can show/hide preview and code.

    """
    code_markup = highlight_code(source) or html.escape(source)
    html_markup = highlight_html(rendered_html.strip()) or html.escape(
        rendered_html.strip()
    )

    context = {
        "unique_id": unique_id,
        "source_html": code_markup,
        "rendered_output_html": html_markup,
        "iframe_srcdoc": srcdoc,
        "sandbox_attrs": "allow-scripts",
    }
    return render_to_string("dj_design_system/canvas_widget.html", context)


def _build_error_html(message: str, source: str = "", debug: bool = False) -> str:
    """Build error HTML for invalid canvas blocks."""
    error = f'<p style="color:red;">Canvas error: {html.escape(message)}</p>'
    if debug and source:
        escaped = html.escape(source)
        error += f"<pre><code>{escaped}</code></pre>"
    return error


# ---------------------------------------------------------------------------
# Markdown Preprocessor
# ---------------------------------------------------------------------------

# Matches a fenced canvas block: ```canvas ... ``` or ```gallery ... ```
_FENCE_RE = re.compile(
    r"^[ \t]{0,3}```(?:canvas|gallery)\s*$\n"  # opening fence
    r"(.*?)\n"  # content (non-greedy)
    r"^[ \t]{0,3}```\s*$",  # closing fence
    re.MULTILINE | re.DOTALL,
)

# Matches fenced blocks with no language or generic languages (py, python)
# that contain Django template syntax, and re-tags them as html+django.
_UNLABELLED_FENCE_RE = re.compile(
    r"^[ \t]{0,3}```(py|python)?\s*$\n"  # opening: no lang or py/python
    r"(.*?)\n"  # content
    r"^[ \t]{0,3}```\s*$",  # closing
    re.MULTILINE | re.DOTALL,
)

_DJANGO_SYNTAX_RE = re.compile(r"\{[%{]")


class DjangoLangPreprocessor(Preprocessor):
    """Re-tag fenced blocks containing Django syntax as ``html+django``.

    Runs before the canvas preprocessor and fenced_code. Blocks with no
    language tag (or ``py``/``python``) that contain ``{%`` or ``{{`` are
    relabelled so codehilite uses the Django/Jinja template lexer.
    """

    def run(self, lines: list[str]) -> list[str]:
        text = "\n".join(lines)
        text = _UNLABELLED_FENCE_RE.sub(self._maybe_retag, text)
        return text.split("\n")

    @staticmethod
    def _maybe_retag(match: re.Match) -> str:
        content = match.group(2)
        if _DJANGO_SYNTAX_RE.search(content):
            return f"```html+django\n{content}\n```"
        return match.group(0)


class CanvasPreprocessor(Preprocessor):
    """Preprocessor that extracts ```canvas blocks and replaces them with iframe widgets."""

    def __init__(self, md: Markdown, app_label: str, debug: bool):
        super().__init__(md)
        self.app_label = app_label
        self.debug = debug
        self._counter = 0
        self.ext_stash: dict[str, str] = {}

    def run(self, lines: list[str]) -> list[str]:
        """Process all lines, replacing canvas blocks with HTML widgets."""
        text = "\n".join(lines)
        text = _FENCE_RE.sub(self._replace_match, text)
        return text.split("\n")

    def _replace_match(self, match: re.Match) -> str:
        """Replace a single canvas fence match with widget HTML."""
        source = match.group(1).strip()
        self._counter += 1
        unique_id = str(self._counter)

        try:
            from django.templatetags.static import static

            rendered_html = render_canvas_block(source)
            media = component_registry.get_merged_media()
            component_css = "".join(
                f'<link rel="stylesheet" href="{static(u)}">' for u in media.css
            )
            component_js = "".join(
                f'<script src="{static(u)}"></script>' for u in media.js
            )
            srcdoc = build_canvas_srcdoc(
                rendered_html=rendered_html,
                component_css=component_css,
                component_js=component_js,
                mode_class="canvas-wrapper--basic",
                app_label=self.app_label,
                iframe_id=unique_id,
            )
            widget_html = _build_widget_html(source, srcdoc, rendered_html, unique_id)
            token = f"CANVAS_STASH_{unique_id}"
            self.ext_stash[token] = widget_html
            return f"\n\n{token}\n\n"
        except Exception as exc:
            error_html = _build_error_html(str(exc), source, self.debug)
            token = f"CANVAS_STASH_{unique_id}"
            self.ext_stash[token] = error_html
            return f"\n\n{token}\n\n"


# ---------------------------------------------------------------------------
# Markdown Extension
# ---------------------------------------------------------------------------


class CanvasPostprocessor(Postprocessor):
    """Postprocessor to restore canvas widget HTML."""

    def __init__(self, stash: dict[str, str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stash = stash

    def run(self, text: str) -> str:
        for token, html_str in self.stash.items():
            # Paragraph processor might have wrapped our token
            text = text.replace(f"<p>{token}</p>", html_str)
            text = text.replace(token, html_str)
        return text


class CanvasExtension(Extension):
    """Markdown extension that parses ```canvas blocks into Django gallery components."""

    def __init__(self, **kwargs):
        self.config = {
            "app_label": ["", "The Django app label to load static media for"],
            "debug": [False, "Enable debug mode"],
        }
        super().__init__(**kwargs)
        self.stash: dict[str, str] = {}

    def extendMarkdown(self, md: Markdown) -> None:
        """Register preprocessors.

        CanvasPreprocessor (priority 32) replaces canvas blocks with widgets
        before any generic fence retagging runs. DjangoLangPreprocessor
        (priority 30) then re-tags remaining fenced blocks containing Django
        syntax. Both run before fenced_code (priority 25).
        """
        preprocessor = CanvasPreprocessor(
            md,
            app_label=self.getConfig("app_label"),
            debug=self.getConfig("debug"),
        )
        preprocessor.ext_stash = self.stash
        md.preprocessors.register(preprocessor, "canvas", 32)
        md.preprocessors.register(DjangoLangPreprocessor(md), "django-lang", 30)
        md.postprocessors.register(
            CanvasPostprocessor(self.stash, md), "canvas-post", 10
        )
