"""Badge component for example_project.demo_components."""

from dj_design_system import components, parameters


class BadgeComponent(components.TagComponent):
    """A small badge label, useful for status indicators or counts.

    The simplest structural pattern: a single file with an inline template.

    Note it's specifically only available in the "default" theme.

    Example usage::

        {% badge "New" %}
    """

    template_format_str = "<span class='badge {classes}'>{text}</span>"
    text = parameters.StrParam("The badge text.")

    class Meta:
        positional_args = ["text"]
        available_themes = ["default"]
