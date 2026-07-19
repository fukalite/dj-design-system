from dj_design_system.components import BlockComponent
from dj_design_system.parameters import StrParam


class AlertComponent(BlockComponent):
    """A dismissable alert banner that wraps arbitrary content.

    Demonstrates a ``BlockComponent`` with a ``StrParam(css_class=True)`` — the
    level is automatically injected into the root element's class list.omatically.

    Note it's specifically only available in the "dark" theme.

    Example usage::

        {% alert "warning" %}
            Your session will expire in 5 minutes.
        {% endalert %}
    """

    template_format_str = (
        "<div class='alert alert-{level} {classes}' role='alert'>{content}</div>"
    )
    level = StrParam(
        "Alert level modifier",
        default="info",
        choices=["info", "success", "warning", "error"],
        css_class=True,
    )

    class Meta:
        positional_args = ["level"]
        available_themes = ["dark"]
