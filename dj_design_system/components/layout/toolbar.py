from dj_design_system.components import BlockComponent
from dj_design_system.services.media import FOUNDATION_CSS
from dj_design_system.slots import Slot


class Toolbar(BlockComponent):
    """The bar across the top of the main area.

    The ``start`` slot, usually a breadcrumb, sits on the left; the
    ``actions`` slot, such as theme and tab controls, on the right.

    Example usage::

        {% dds__layout__toolbar %}
            {% slot "start" %}<a href="/dds/">Gallery</a>{% endslot %}
            {% slot "actions" %}...{% endslot %}
        {% enddds__layout__toolbar %}
    """

    template_name = "dj_design_system/ui/layout/toolbar.html"

    class Meta:
        slots = {
            "start": Slot(
                required=True, description="Left-hand content, e.g. a breadcrumb."
            ),
            "actions": Slot(description="Right-hand controls."),
        }

    class Media:
        css = [FOUNDATION_CSS, "dj_design_system/ui/layout/toolbar.css"]
