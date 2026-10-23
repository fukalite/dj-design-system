"""Slotted card component for example_project.demo_components."""

from django.utils import html

from dj_design_system import components, parameters, slots


class SlottedCardComponent(components.BlockComponent):
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

    title = parameters.StrParam(
        "Optional card title displayed above the body.", required=False
    )
    variant = parameters.StrParam(
        "Visual variant of the card.",
        default="default",
        choices=["default", "elevated", "outlined"],
        css_class=True,
    )

    class Meta:
        slots = {
            "body": slots.Slot(required=True, description="Main card content."),
            "header": slots.Slot(
                required=False,
                description="Optional header area above the title.",
            ),
            "footer": slots.Slot(
                required=False,
                description="Optional footer area below the body.",
            ),
        }
        positional_args = ["title"]

    def render(self) -> str:
        """Render the slotted card HTML with escaped parameters and safe slots."""
        header = (
            html.format_html(
                "<div class='slotted-card__header'>{}</div>",
                self.slots["header"],
            )
            if self.slots.get("header")
            else ""
        )
        title = (
            html.format_html("<h3 class='slotted-card__title'>{}</h3>", self.title)
            if self.title
            else ""
        )
        footer = (
            html.format_html(
                "<div class='slotted-card__footer'>{}</div>",
                self.slots["footer"],
            )
            if self.slots.get("footer")
            else ""
        )

        return html.format_html(
            "<div class='slotted-card {}'>{}{}"
            "<div class='slotted-card__body'>{}</div>{}</div>",
            self.get_classes_string(),
            header,
            title,
            self.slots["body"],
            footer,
        )
