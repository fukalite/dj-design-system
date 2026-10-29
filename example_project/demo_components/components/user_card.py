"""User profile card component for example_project.demo_components."""

import typing

from dj_design_system import components, parameters


class UserCardComponent(components.TagComponent):
    """Renders a card displaying a user's name, email, and active status.

    Demonstrates ``UserParam`` — the ``user`` object is automatically
    unpacked into ``user_first_name``, ``user_last_name``, ``user_email``
    and ``user_is_active`` template variables, and the ``user-active``
    CSS class is applied when the user is active.

    Example usage::

        {% user_card user %}
    """

    template_format_str = (
        "<div class='user-card {classes}'>"
        "<h3>{user_first_name} {user_last_name}</h3>"
        "<p class='user-card__email'>{user_email}</p>"
        "</div>"
    )
    user = parameters.UserParam("The user to display.", required=False)

    class Meta:
        positional_args = ["user"]

    def get_context(self) -> dict[str, typing.Any]:
        """Populate default user attributes when no user instance is provided."""
        context = super().get_context()
        context.setdefault("user_first_name", "Jane")
        context.setdefault("user_last_name", "Smith")
        context.setdefault("user_email", "jane.smith@example.com")
        return context
