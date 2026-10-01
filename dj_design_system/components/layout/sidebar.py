from dj_design_system.components import BlockComponent
from dj_design_system.parameters import StrParam
from dj_design_system.services.media import FOUNDATION_CSS
from dj_design_system.slots import Slot


class Sidebar(BlockComponent):
    """The dark left-hand column with the library's title, search and navigation.

    On narrow screens it slides in from the left when the mobile menu
    toggle is checked.

    Example usage::

        {% dds__layout__sidebar title=design_system_name title_url="/dds/" %}
            {% slot "search" %}...{% endslot %}
            {% slot "nav" %}...{% endslot %}
        {% enddds__layout__sidebar %}
    """

    template_name = "dj_design_system/ui/layout/sidebar.html"

    title = StrParam("The library's name, shown at the top.")
    title_url = StrParam("Where the title links to, usually the gallery home.")

    class Meta:
        slots = {
            "search": Slot(description="The search box and its results."),
            "nav": Slot(required=True, description="The navigation tree."),
        }

    class Media:
        css = [FOUNDATION_CSS, "dj_design_system/ui/layout/sidebar.css"]
