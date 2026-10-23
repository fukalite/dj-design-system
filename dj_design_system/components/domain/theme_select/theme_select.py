"""Built-in gallery theme selector domain component."""

import typing

from dj_design_system import components, data, parameters


DEFAULT_ACTIVE_THEME = "light"
DEFAULT_LABEL = "Global Theme"
DEFAULT_SELECT_ID = "gallery-global-theme-select"
DEFAULT_ICON = "sun"


class ThemeSelect(components.TagComponent):
    """Gallery theme selector control with Light DOM custom element enhancement.

    Use ``ThemeSelect`` (``{% dds__theme_select %}``) in the gallery topbar or
    sandbox toolbar to allow switching between configured consumer component
    themes. Accepts ``Theme`` dataclass instances, dictionaries with ``value``
    and ``label`` keys, or plain theme identifier strings, normalizing them in
    ``get_context()``.

    Args:
        themes: Available theme objects, dicts with ``value`` and ``label``, or
            plain string identifiers.
        active_theme: Currently active theme identifier (defaults to ``"light"``).
        label: Accessible label for the theme selector control (defaults to
            ``"Global Theme"``).
        select_id: DOM ``id`` attribute for the ``<select>`` element (defaults
            to ``"gallery-global-theme-select"``).

    Example usage::

        {% dds__theme_select themes active_theme="dark" %}

        {% dds__theme_select themes=gallery_themes active_theme=current_theme label="Canvas Theme" select_id="canvas-theme-select" %}
    """

    themes = parameters.ListParam(
        description="Available theme objects or dicts with 'value' and 'label'.",
        default=None,
        required=False,
    )
    active_theme = parameters.StrParam(
        description="Currently active theme identifier.",
        default=DEFAULT_ACTIVE_THEME,
        required=False,
    )
    label = parameters.StrParam(
        description="Accessible label for the theme selector.",
        default=DEFAULT_LABEL,
        required=False,
    )
    select_id = parameters.StrParam(
        description="DOM id for the theme select control.",
        default=DEFAULT_SELECT_ID,
        required=False,
    )

    class Meta:
        positional_args = ["themes"]

    def get_context(self) -> dict[str, typing.Any]:
        """Compute normalized theme options, active theme state, and icon name.

        Returns:
            Dictionary containing component parameters, ``normalized_themes``,
            ``resolved_active_theme``, ``active_icon``, ``has_themes``, and
            ``has_multiple_themes``.
        """
        context = super().get_context()
        raw_themes = list(self.themes) if self.themes is not None else []
        extracted_options = [
            data.SandboxControlOptionData.from_raw(raw_item) for raw_item in raw_themes
        ]

        theme_values = [opt.value for opt in extracted_options]
        if self.active_theme and self.active_theme in theme_values:
            resolved_active_theme = str(self.active_theme)
        elif extracted_options:
            resolved_active_theme = extracted_options[0].value
        else:
            resolved_active_theme = str(self.active_theme or DEFAULT_ACTIVE_THEME)

        normalized_themes: list[dict[str, typing.Any]] = [
            opt.to_dict(is_selected=(opt.value == resolved_active_theme))
            for opt in extracted_options
        ]

        resolved_label = str(self.label) if self.label else DEFAULT_LABEL
        resolved_select_id = (
            str(self.select_id) if self.select_id else DEFAULT_SELECT_ID
        )

        context["label"] = resolved_label
        context["select_id"] = resolved_select_id
        context["resolved_active_theme"] = resolved_active_theme
        context["active_icon"] = DEFAULT_ICON
        context["normalized_themes"] = normalized_themes
        context["has_themes"] = bool(normalized_themes)
        context["has_multiple_themes"] = len(normalized_themes) > 1
        return context
