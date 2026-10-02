from django.utils.html import escape

from dj_design_system.components import TagComponent
from dj_design_system.components.primitives.code_block import CodeBlock
from dj_design_system.components.primitives.icon import Icon
from dj_design_system.parameters import StrParam
from dj_design_system.services.media import FOUNDATION_CSS


def _code(source: str, language: str) -> str:
    # CodeBlock unescapes its content (it normally arrives auto-escaped from a
    # template), so escape raw code first to keep literal entities intact.
    return CodeBlock(content=escape(source), language=language, variant="bare").render()


class CanvasWidget(TagComponent):
    """A live preview with switches to its template source and output HTML.

    Shows an iframe, and on request the code that rendered it
    (``template_source``, highlighted as a Django template) or the HTML it
    produced (``rendered_output``, highlighted as HTML). Pass raw code: the
    widget highlights it. The three-way switch is CSS-only radio buttons,
    so ``unique_id`` must be unique on the page.

    Give the iframe either a URL (``iframe_src``) or a whole document
    (``iframe_srcdoc``). ``sandbox_attrs`` sets the iframe's ``sandbox``.
    The widget's script sizes previews to their content when their canvas
    reports its height.

    Example usage::

        {% dds__canvas__canvas_widget unique_id="sandbox" iframe_src=canvas_url template_source=source rendered_output=output %}
    """

    template_name = "dj_design_system/ui/canvas/canvas_widget.html"

    unique_id = StrParam("Unique on the page; names the switch's radio buttons.")
    iframe_src = StrParam("URL of the preview.", required=False, default="")
    iframe_srcdoc = StrParam(
        "Whole HTML document to preview, instead of a URL.",
        required=False,
        default="",
    )
    iframe_class = StrParam(
        "The iframe's class. Defaults to the markdown canvas iframe.",
        required=False,
        default="",
    )
    sandbox_attrs = StrParam(
        "The iframe's sandbox attribute, e.g. ``allow-scripts``.",
        required=False,
        default="",
    )
    template_source = StrParam(
        "The Django template code behind the preview.", required=False, default=""
    )
    rendered_output = StrParam("The HTML it rendered.", required=False, default="")
    extra_classes = StrParam("Extra CSS classes.", required=False, default="")

    class Media:
        css = [
            FOUNDATION_CSS,
            "dj_design_system/ui/primitives/icon.css",
            "dj_design_system/ui/primitives/code_block.css",
            "dj_design_system/ui/primitives/code_highlight.css",
            "dj_design_system/ui/canvas/canvas_widget.css",
        ]
        js = "dj_design_system/ui/canvas/canvas_widget.js"

    def validate_params(self) -> None:
        if bool(self.iframe_src) == bool(self.iframe_srcdoc):
            raise ValueError(
                "CanvasWidget needs iframe_src or iframe_srcdoc, not both."
            )

    def get_context(self):
        context = super().get_context()
        context["preview_icon"] = Icon(name="eye").render()
        context["source_icon"] = Icon(name="code").render()
        context["output_icon"] = Icon(name="file-code").render()
        context["source_code"] = _code(str(self.template_source or ""), "django")
        context["output_code"] = _code(str(self.rendered_output or "").strip(), "html")
        return context
