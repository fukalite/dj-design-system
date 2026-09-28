from django.utils.html import format_html

from dj_design_system.components import BlockComponent
from dj_design_system.parameters import StrParam
from dj_design_system.slots import Slot


class SlottedCardComponent(BlockComponent):
    """A card with named slots for header, body, and footer areas.

    Demonstrates the named slots feature — a ``BlockComponent`` with
    ``Meta.slots`` declaring multiple content areas that template authors
    fill using ``{% slot "name" %}...{% endslot %}``.

    The ``body`` slot is required; ``header`` and ``footer`` are optional
    and will be omitted from the output when not provided.

    Example usage::

        {% slotted_card title="Welcome" %}
            {% slot "header" %}
                <img src="banner.jpg" alt="Banner">
            {% endslot %}
            {% slot "body" %}
                <p>Main card content goes here.</p>
            {% endslot %}
            {% slot "footer" %}
                <button>Save</button>
            {% endslot %}
        {% endslotted_card %}

    Minimal usage (only required slot)::

        {% slotted_card %}
            {% slot "body" %}
                <p>Just the body.</p>
            {% endslot %}
        {% endslotted_card %}
    """

    title = StrParam("Optional card title displayed above the body.", required=False)
    variant = StrParam(
        "Visual variant of the card.",
        default="default",
        choices=["default", "elevated", "outlined"],
        css_class=True,
    )

    class Meta:
        slots = {
            "body": Slot(required=True, description="Main card content."),
            "header": Slot(
                required=False, description="Optional header area above the title."
            ),
            "footer": Slot(
                required=False, description="Optional footer area below the body."
            ),
        }
        positional_args = ["title"]

    def render(self) -> str:
        # format_html escapes param values (e.g. title) and passes through the
        # slots, which are already safe. Returning a plain str instead would
        # render as escaped text in the gallery canvas.
        header = (
            format_html(
                "<div class='slotted-card__header'>{}</div>", self.slots["header"]
            )
            if self.slots.get("header")
            else ""
        )
        title = (
            format_html("<h3 class='slotted-card__title'>{}</h3>", self.title)
            if self.title
            else ""
        )
        footer = (
            format_html(
                "<div class='slotted-card__footer'>{}</div>", self.slots["footer"]
            )
            if self.slots.get("footer")
            else ""
        )

        return format_html(
            "<div class='slotted-card {}'>{}{}<div class='slotted-card__body'>{}</div>{}</div>",
            self.get_classes_string(),
            header,
            title,
            self.slots["body"],
            footer,
        )
