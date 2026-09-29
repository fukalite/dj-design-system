from dj_design_system.components import BlockComponent
from dj_design_system.services.media import FOUNDATION_CSS
from dj_design_system.slots import Slot


class Table(BlockComponent):
    """A compact data table with uppercase column headings.

    Fill the ``head`` slot with header rows and the ``body`` slot with data
    rows; inline ``<code>`` in cells gets a subtle background. On narrow
    screens the table scrolls sideways instead of squashing.

    Example usage::

        {% dds__primitives__table %}
            {% slot "head" %}<tr><th>Name</th><th>Type</th></tr>{% endslot %}
            {% slot "body" %}<tr><td><code>label</code></td><td>str</td></tr>{% endslot %}
        {% enddds__primitives__table %}
    """

    template_name = "dj_design_system/ui/primitives/table.html"

    class Meta:
        slots = {
            "head": Slot(description="Header rows (<tr> with <th> cells)."),
            "body": Slot(required=True, description="Data rows (<tr> with <td> cells)."),
        }

    class Media:
        css = [FOUNDATION_CSS, "dj_design_system/ui/primitives/table.css"]
