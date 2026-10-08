"""Configurable button component for example_project.demo_components."""

import typing

from dj_design_system import components, parameters


class ButtonComponent(components.TagComponent):
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

    label = parameters.StrParam("The button label.")
    variant = parameters.StrParam(
        "Variant modifier",
        required=False,
        default="primary",
        choices=["primary", "secondary", "danger"],
        css_class=True,
    )
    disabled = parameters.BoolParam(
        "Renders the button as disabled.", required=False, css_class=True
    )

    class Meta:
        positional_args = ["label"]

    def get_context(self) -> dict[str, typing.Any]:
        """Populate ``disabled_attr`` for the co-located button template."""
        ctx = super().get_context()
        ctx["disabled_attr"] = "disabled" if self.disabled else ""
        return ctx
