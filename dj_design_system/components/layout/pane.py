from django.utils.html import format_html_join

from dj_design_system.components import BlockComponent
from dj_design_system.parameters import DictParam, StrParam
from dj_design_system.services.media import FOUNDATION_CSS


#: Variant -> the pane's role class, which SplitPane's layout rules target.
VARIANT_CLASSES = {
    "documentation": "gallery-documentation",
    "sandbox": "gallery-sandbox",
}


class Pane(BlockComponent):
    """One pane of a ``SplitPane``: a small uppercase header over a scrolling body.

    Example usage::

        {% dds__layout__pane title="Documentation" pane_id="pane-docs" body_classes="gallery-docs" %}
            ...
        {% enddds__layout__pane %}
    """

    template_name = "dj_design_system/ui/layout/pane.html"

    title = StrParam("Header text.")
    pane_id = StrParam("The pane's ``id``, e.g. a link target.", required=False)
    variant = StrParam(
        "Which pane of the split this is.",
        required=False,
        default="documentation",
        choices=list(VARIANT_CLASSES),
    )
    body_classes = StrParam("Extra CSS classes for the body.", required=False)
    body_attrs = DictParam(
        "Extra HTML attributes for the body, e.g. a hook for scripts. Escaped.",
        required=False,
    )

    class Media:
        css = [FOUNDATION_CSS, "dj_design_system/ui/layout/pane.css"]

    def get_context(self):
        context = super().get_context()
        context["pane_class"] = VARIANT_CLASSES[str(self.variant)]
        context["body_extra_attrs"] = format_html_join(
            "", ' {}="{}"', (self.body_attrs or {}).items()
        )
        return context
