from django.utils.safestring import mark_safe

from dj_design_system.components import BlockComponent
from dj_design_system.parameters import StrParam
from dj_design_system.services.media import FOUNDATION_CSS


class CodeBlock(BlockComponent):
    """A dark, horizontally scrolling code block.

    Pass ``code`` for plain source, which is escaped, or ``highlighted`` for
    markup that is already highlighted, such as Pygments output. Without
    either, the block's content is used. Whitespace is preserved.

    ``highlighted`` is inserted unescaped: only pass trusted, generated
    markup, never user input.

    Example usage::

        {% dds__primitives__code_block code=tag_signature.minimal %}{% enddds__primitives__code_block %}
        {% dds__primitives__code_block highlighted=tag_signature.minimal_html %}{% enddds__primitives__code_block %}
    """

    template_name = "dj_design_system/ui/primitives/code_block.html"

    code = StrParam("Plain source code. Escaped.", required=False)
    highlighted = StrParam(
        "Pre-highlighted, trusted HTML. Inserted unescaped.", required=False
    )

    class Media:
        css = [FOUNDATION_CSS, "dj_design_system/ui/primitives/code_block.css"]

    def get_context(self):
        context = super().get_context()
        if self.highlighted:
            context["body"] = mark_safe(self.highlighted)  # noqa: S308 - documented as trusted
        elif self.code is not None:
            context["body"] = self.code
        else:
            context["body"] = self.content
        return context
