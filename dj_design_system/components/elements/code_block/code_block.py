"""Built-in code block element component with copy-to-clipboard support."""

import typing

from dj_design_system import components, parameters


DEFAULT_LANGUAGE = "django"


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

    template_name = "dj_design_system/components/elements/code_block/code_block.html"
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
            ``has_title``, ``has_language``, ``header_label``, and
            ``show_header``.
        """
        context = super().get_context()
        title = "" if self.title is None else str(self.title)
        language = "" if self.language is None else str(self.language)
        stripped_code = str(self.code).strip("\r\n")
        has_title = bool(title)
        has_language = bool(language)
        header_label = title if title else language
        show_header = bool(header_label) or bool(self.copyable)

        context["language"] = language
        context["title"] = title
        context["stripped_code"] = stripped_code
        context["has_title"] = has_title
        context["has_language"] = has_language
        context["header_label"] = header_label
        context["show_header"] = show_header
        return context
