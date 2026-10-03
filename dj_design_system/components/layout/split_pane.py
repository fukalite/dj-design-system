from dj_design_system.components import BlockComponent
from dj_design_system.services.media import FOUNDATION_CSS
from dj_design_system.slots import Slot


class SplitPane(BlockComponent):
    """Two panes, stacked on most screens and side by side from 1800px wide.

    When stacked, one pane shows at a time: the split's
    ``gallery-split--show-sandbox`` modifier (set by the tabs' script) swaps
    the documentation pane for the sandbox pane. Fill it with two ``Pane``
    components.

    Example usage::

        {% dds__layout__split_pane %}
            {% slot "primary" %}...{% endslot %}
            {% slot "secondary" %}...{% endslot %}
        {% enddds__layout__split_pane %}
    """

    template_name = "dj_design_system/ui/layout/split_pane.html"

    class Meta:
        slots = {
            "primary": Slot(required=True, description="The documentation pane."),
            "secondary": Slot(required=True, description="The sandbox pane."),
        }

    class Media:
        css = [
            FOUNDATION_CSS,
            "dj_design_system/ui/layout/pane.css",
            "dj_design_system/ui/layout/split_pane.css",
        ]
