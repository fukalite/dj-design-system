from django.utils.html import format_html

from dj_design_system.components import BlockComponent
from dj_design_system.parameters import StrParam
from dj_design_system.slots import Slot


class CalloutComponent(BlockComponent):
    """A highlighted callout with a message and an optional actions area.

    The ``message`` slot is required; the ``actions`` slot is optional and
    its wrapper is omitted entirely when nothing is supplied.

    Example usage::

        {% callout title="Heads up" %}
            {% slot "message" %}Your trial ends in 3 days.{% endslot %}
            {% slot "actions" %}<a href="/billing/">Upgrade</a>{% endslot %}
        {% endcallout %}
    """

    title = StrParam("Optional heading shown above the message.", required=False)
    tone = StrParam(
        "Colour treatment of the callout.",
        default="neutral",
        choices=["neutral", "success", "warning"],
        css_class=True,
    )

    class Meta:
        slots = {
            "message": Slot(required=True, description="Main callout text."),
            "actions": Slot(
                required=False, description="Optional links or buttons below the text."
            ),
        }

    def render(self) -> str:
        title = (
            format_html("<p class='callout__title'>{}</p>", self.title)
            if self.title
            else ""
        )
        actions = (
            format_html("<div class='callout__actions'>{}</div>", self.slots["actions"])
            if self.slots.get("actions")
            else ""
        )
        return format_html(
            "<aside class='callout {}'>{}<div class='callout__message'>{}</div>{}</aside>",
            self.get_classes_string(),
            title,
            self.slots["message"],
            actions,
        )
