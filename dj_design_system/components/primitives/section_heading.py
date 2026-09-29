from dj_design_system.components import BlockComponent
from dj_design_system.parameters import IntParam, StrParam
from dj_design_system.services.media import FOUNDATION_CSS


#: Variant -> BEM class.
VARIANT_CLASSES = {
    "section": "gallery-docs__section-heading",
    "sub": "gallery-usage__heading",
}


class SectionHeading(BlockComponent):
    """A small uppercase heading for a section of a gallery pane.

    ``section`` headings title a pane section (Description, Usage,
    Parameters); ``sub`` headings title a block within one (Minimal
    example). Pick ``level`` to fit the document outline; it doesn't change
    the look.

    Example usage::

        {% dds__primitives__section_heading %}Usage{% enddds__primitives__section_heading %}
        {% dds__primitives__section_heading variant="sub" level=4 %}Minimal example{% enddds__primitives__section_heading %}
    """

    template_name = "dj_design_system/ui/primitives/section_heading.html"

    level = IntParam(
        "Heading level, 2 to 6.", required=False, default=3, choices=[2, 3, 4, 5, 6]
    )
    variant = StrParam(
        "Visual style.",
        required=False,
        default="section",
        choices=list(VARIANT_CLASSES),
    )

    class Media:
        css = [FOUNDATION_CSS, "dj_design_system/ui/primitives/section_heading.css"]

    def get_context(self):
        context = super().get_context()
        context["heading_class"] = VARIANT_CLASSES[str(self.variant)]
        return context
