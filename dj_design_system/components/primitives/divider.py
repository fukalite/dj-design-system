from dj_design_system.components import TagComponent
from dj_design_system.services.media import FOUNDATION_CSS


class Divider(TagComponent):
    """A horizontal rule separating sections of a documentation pane.

    Example usage::

        {% dds__primitives__divider %}
    """

    template_name = "dj_design_system/ui/primitives/divider.html"

    class Media:
        css = [FOUNDATION_CSS, "dj_design_system/ui/primitives/divider.css"]
