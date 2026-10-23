"""Built-in code block element component with copy-to-clipboard support."""

import html
import typing

import pygments
from django.utils import safestring
from pygments import formatters, lexers
from pygments import util as pygments_util

from dj_design_system import components, parameters


DEFAULT_LANGUAGE = "django"
DJANGO_LANGUAGES: tuple[str, ...] = ("django", "html+django", "jinja")
DJANGO_TAG_MARKERS: tuple[str, ...] = ("{%", "{{", "{#")
LINE_BREAK_CHARS = "\r\n"
PYGMENTS_STYLE = "monokai"


class CodeBlock(components.TagComponent):
    """Formatted code snippet viewer with optional header label and copy button.

    Use ``CodeBlock`` (``{% dds__code_block %}``) to render source code snippets,
    template usage examples, or configuration blocks on the ``code`` surface
    (``data-surface="code"``). Enhanced client-side via the Light DOM
    ``<dds-code-block>`` custom element to support one-click clipboard copying
    and ``dds:copy`` event dispatching.

    Args:
        code: Source code snippet to render.
        language: Code language identifier (defaults to ``"django"``).
        title: Optional header title or filename override.
        copyable: Whether to display the copy-to-clipboard trigger button.

    Example usage::

        {% dds__code_block "{% dds__button 'Save' %}" %}

        {% dds__code_block code=python_snippet language="python" title="views.py" %}
    """

    template_name = (
        "dj_design_system/components/elements/code_block/code_block.html"
    )
    _template_name = template_name

    code = parameters.StrParam(description="Source code snippet to render.")
    language = parameters.StrParam(
        description="Code language identifier.",
        default=DEFAULT_LANGUAGE,
        required=False,
    )
    title = parameters.StrParam(
        description="Optional header title or filename.",
        default="",
        required=False,
    )
    copyable = parameters.BoolParam(
        description="Whether to display the copy-to-clipboard button.",
        default=True,
        required=False,
    )

    class Meta:
        positional_args = ["code"]

    class Media:
        css = "dj_design_system/components/elements/code_block/code_block.css"
        js = "dj_design_system/components/elements/code_block/code_block.js"

    def get_context(self) -> dict[str, typing.Any]:
        """Compute normalized template context for code formatting and header state.

        Returns:
            Dictionary containing component parameters, ``stripped_code``,
            ``highlighted_code``, ``has_title``, ``has_language``,
            ``header_label``, ``show_header``, and ``show_overlay_copy``.
        """
        context = super().get_context()
        title = "" if self.title is None else str(self.title)
        language = "" if self.language is None else str(self.language)
        stripped_code = (
            str(self.code).strip(LINE_BREAK_CHARS)
            if self.code is not None
            else ""
        )
        has_title = bool(title)
        has_language = bool(language)
        header_label = title if title else language
        show_header = has_title
        show_overlay_copy = bool(self.copyable) and not show_header
        highlighted_code = self._highlight_snippet(
            code=stripped_code,
            language=language,
        )

        context["language"] = language
        context["title"] = title
        context["stripped_code"] = stripped_code
        context["highlighted_code"] = highlighted_code
        context["has_title"] = has_title
        context["has_language"] = has_language
        context["header_label"] = header_label
        context["show_header"] = show_header
        context["show_overlay_copy"] = show_overlay_copy
        return context

    def _highlight_snippet(
        self,
        *,
        code: str,
        language: str,
    ) -> safestring.SafeString:
        """Return syntax-highlighted HTML for ``code`` or escaped fallback text.

        Args:
            code: Stripped source code snippet.
            language: Language identifier for lexer selection.

        Returns:
            SafeString containing Pygments-highlighted HTML or escaped text.
        """
        if not code:
            return safestring.mark_safe("")
        normalized_lang = language.lower().strip()
        if not normalized_lang:
            return safestring.mark_safe(html.escape(s=code))
        if normalized_lang in DJANGO_LANGUAGES and not any(
            marker in code for marker in DJANGO_TAG_MARKERS
        ):
            return safestring.mark_safe(html.escape(s=code))
        try:
            if normalized_lang in DJANGO_LANGUAGES:
                lexer = lexers.DjangoLexer(stripnl=False)
            elif normalized_lang == "html":
                lexer = lexers.HtmlLexer(stripnl=False)
            else:
                lexer = lexers.get_lexer_by_name(
                    _alias=normalized_lang,
                    stripnl=False,
                )
            formatter = formatters.HtmlFormatter(
                style=PYGMENTS_STYLE,
                noclasses=False,
                nowrap=True,
            )
            highlighted = pygments.highlight(
                code=code,
                lexer=lexer,
                formatter=formatter,
            ).strip(LINE_BREAK_CHARS)
            if highlighted:
                return safestring.mark_safe(highlighted)
        except (ValueError, TypeError, pygments_util.ClassNotFound):
            pass
        return safestring.mark_safe(html.escape(s=code))

