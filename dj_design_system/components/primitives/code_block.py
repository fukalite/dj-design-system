import html
import textwrap

from django.utils.safestring import mark_safe

from dj_design_system.components import BlockComponent
from dj_design_system.parameters import StrParam
from dj_design_system.services.media import FOUNDATION_CSS


try:
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_by_name
    from pygments.util import ClassNotFound

    HAS_PYGMENTS = True
except ImportError:  # pragma: no cover - Pygments is optional
    HAS_PYGMENTS = False


class CodeBlock(BlockComponent):
    """A dark, horizontally scrolling code block with syntax highlighting.

    The block's content is the code. It is dedented and trimmed of blank
    lines at either end, so it can be indented to match the template, and
    whitespace inside it is preserved. Set ``language`` to any Pygments
    lexer name (``python``, ``django``, ``html``, ``css``, ...) to
    highlight it; the default, ``text``, shows it as plain text. Without
    Pygments installed, code is always shown as plain text.

    Template variables in the content are auto-escaped by Django as usual;
    the component unescapes them before highlighting, so they display as
    written rather than double-escaped.

    Example usage::

        {% dds__primitives__code_block language="python" %}
            total = price * quantity
        {% enddds__primitives__code_block %}
    """

    template_name = "dj_design_system/ui/primitives/code_block.html"

    language = StrParam(
        "Pygments lexer name for syntax highlighting, e.g. ``python`` or"
        " ``django``. ``text`` shows plain text.",
        required=False,
        default="text",
    )

    class Media:
        css = [
            FOUNDATION_CSS,
            "dj_design_system/ui/primitives/code_block.css",
            "dj_design_system/ui/primitives/code_highlight.css",
        ]

    def validate_params(self) -> None:
        if HAS_PYGMENTS and self.language != "text":
            try:
                get_lexer_by_name(str(self.language))
            except ClassNotFound:
                raise ValueError(
                    f"CodeBlock language {self.language!r} is not a Pygments lexer."
                ) from None

    def get_context(self):
        context = super().get_context()
        source = textwrap.dedent(html.unescape(str(self.content or ""))).strip("\n")
        if HAS_PYGMENTS and self.language != "text":
            lexer = get_lexer_by_name(str(self.language))
            highlighted = highlight(source, lexer, HtmlFormatter(nowrap=True))
            context["body"] = mark_safe(highlighted.rstrip("\n"))  # noqa: S308 - Pygments escapes the source
        else:
            context["body"] = source
        return context
