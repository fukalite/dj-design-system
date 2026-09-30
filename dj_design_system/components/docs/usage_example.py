from django.utils.html import escape

from dj_design_system.components import TagComponent
from dj_design_system.components.primitives.code_block import CodeBlock
from dj_design_system.components.primitives.icon_button import IconButton
from dj_design_system.components.primitives.section_heading import SectionHeading
from dj_design_system.parameters import StrParam
from dj_design_system.services.media import FOUNDATION_CSS


class UsageExample(TagComponent):
    """One usage example: a small heading, an optional live preview, and code.

    ``code`` is the example's Django template code; it is highlighted for
    you. With a ``preview_url`` the example also shows a live preview, with
    an "Open in sandbox" button over it. ``preview_id`` names the preview's
    iframe so its canvas can report its height, and ``preview_title`` is the
    iframe's accessible title.

    Example usage::

        {% dds__docs__usage_example heading="Minimal example" code=signature preview_url=url preview_id="minimal" preview_title="Minimal example preview" %}
    """

    template_name = "dj_design_system/ui/docs/usage_example.html"

    heading = StrParam("The example's heading.")
    code = StrParam("The example's Django template code.")
    preview_url = StrParam("URL of a live preview.", required=False, default="")
    preview_id = StrParam(
        "Names the preview iframe. Needed with a preview.",
        required=False,
        default="",
    )
    preview_title = StrParam(
        "The preview iframe's accessible title. Needed with a preview.",
        required=False,
        default="",
    )

    class Media:
        # The heading, sandbox link and code block's CSS, then
        # canvas_widget.css: the preview's min-height overrides the canvas
        # iframe's.
        css = [
            FOUNDATION_CSS,
            "dj_design_system/ui/primitives/section_heading.css",
            "dj_design_system/ui/primitives/icon.css",
            "dj_design_system/ui/primitives/icon_button.css",
            "dj_design_system/ui/primitives/code_block.css",
            "dj_design_system/ui/primitives/code_highlight.css",
            "dj_design_system/ui/canvas/canvas_widget.css",
            "dj_design_system/ui/docs/usage_example.css",
        ]
        js = "dj_design_system/ui/canvas/canvas_widget.js"

    def validate_params(self) -> None:
        if self.preview_url and not (self.preview_id and self.preview_title):
            raise ValueError(
                "UsageExample with a preview_url needs preview_id and preview_title."
            )

    def get_context(self):
        context = super().get_context()
        context["heading_html"] = SectionHeading(
            text=self.heading, variant="sub", level=4
        ).render()
        if self.preview_url:
            context["sandbox_link"] = IconButton(
                icon="external-link",
                label="Open in sandbox",
                href="#pane-sandbox",
                variant="overlay",
            ).render()
        # CodeBlock unescapes its content, so escape the raw code first.
        context["code_html"] = CodeBlock(
            content=escape(str(self.code)), language="django"
        ).render()
        return context
