"""Informational card component for example_project.demo_components."""

from dj_design_system import parameters
from example_project.demo_components.components.card import abstract_card


class InfoCardComponent(abstract_card.AbstractCardComponent):
    """A simple informational card with a title, body text, and optional footer.

    Demonstrates:
    - Inheriting from an abstract component
    - ``BoolParam`` for a toggle flag
    - A nested subfolder layout (``components/card/``)

    Example usage::

        {% info_card "Getting started" "Read the quickstart guide." %}
        {% info_card "Tips" "Use keyword args for clarity." show_footer=True %}
    """

    template_format_str = (
        "<div class='card {classes}'>"
        "<h3 class='card__title'>{title}</h3>"
        "<p class='card__body'>{body}</p>"
        "</div>"
    )
    title = parameters.StrParam("The card heading.")
    body = parameters.StrParam("The card body text.")
    show_footer = parameters.BoolParam(
        "Show a decorative footer rule.", required=False
    )

    class Meta:
        positional_args = ["title", "body"]
