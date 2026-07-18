from dj_design_system.components import TagComponent
from dj_design_system.parameters import (
    BoolParam,
    StrParam,
)


class ButtonComponent(TagComponent):
    """A configurable button with size and variant modifiers.

    Demonstrates:
    - ``StrParam`` with positional args
    - ``StrParam(css_class=True)`` — value injected as a CSS modifier class
    - ``BoolParam(css_class=True)`` — adds a CSS class when truthy
    - Co-located CSS file (``button.css``) discovered automatically
    - Co-located HTML template (``button.html``) discovered automatically

    Example usage::

        {% button "Save changes" %}
        {% button "Delete" variant="danger" disabled=True %}
    """

    label = StrParam("The button label.")
    variant = StrParam(
        "Variant modifier",
        required=False,
        default="primary",
        choices=["primary", "secondary", "danger"],
        css_class=True,
    )
    disabled = BoolParam(
        "Renders the button as disabled.", required=False, css_class=True
    )

    class Meta:
        positional_args = ["label"]

    def get_context(self):
        ctx = super().get_context()
        ctx["disabled_attr"] = "disabled" if self.disabled else ""
        return ctx
