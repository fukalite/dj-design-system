"""Built-in gallery theme selector domain component."""

import typing

from dj_design_system import components, parameters


DEFAULT_ACTIVE_THEME = "light"
DEFAULT_LABEL = "Global Theme"
DEFAULT_SELECT_ID = "gallery-global-theme-select"
ICON_MOON = "moon"
ICON_SUN = "sun"


class ThemeSelect(components.TagComponent):
    """Gallery theme selector control with Light DOM custom element enhancement.

    Use ``ThemeSelect`` (``{% dds__theme_select %}``) in the gallery topbar or
    sandbox toolbar to allow switching between configured design system themes.
    Accepts ``Theme`` dataclass instances, dictionaries with ``value`` and
    ``label`` keys, or plain theme identifier strings, normalizing them in
    ``get_context()`` with automatic ``sun`` / ``moon`` icon resolution.

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
        extracted_themes: list[tuple[str, str]] = []

        for raw_item in raw_themes:
            if isinstance(raw_item, str):
                raw_value: typing.Any = raw_item
                raw_label: typing.Any = (
                    raw_item.capitalize() if raw_item.islower() else raw_item
                )
            elif isinstance(raw_item, dict):
                raw_value = raw_item.get("value")
                raw_label = raw_item.get("label")
                if raw_label is None and raw_value is not None:
                    val_str = str(raw_value)
                    raw_label = val_str.capitalize() if val_str.islower() else val_str
            else:
                raw_value = getattr(raw_item, "value", None)
                raw_label = getattr(raw_item, "label", None)
                if raw_label is None and raw_value is not None:
                    val_str = str(raw_value)
                    raw_label = val_str.capitalize() if val_str.islower() else val_str

            value = str(raw_value) if raw_value is not None else ""
            label = str(raw_label) if raw_label is not None else value
            extracted_themes.append((value, label))

        theme_values = [value for value, _ in extracted_themes]
        if self.active_theme and self.active_theme in theme_values:
            resolved_active_theme = str(self.active_theme)
        elif extracted_themes:
            resolved_active_theme = extracted_themes[0][0]
        else:
            resolved_active_theme = str(self.active_theme or DEFAULT_ACTIVE_THEME)

        normalized_themes: list[dict[str, typing.Any]] = []
        for value, label in extracted_themes:
            icon = ICON_MOON if "dark" in value.lower() else ICON_SUN
            is_selected = value == resolved_active_theme
            normalized_themes.append(
                {
                    "value": value,
                    "label": label,
                    "icon": icon,
                    "is_selected": is_selected,
                }
            )

        active_icon = (
            ICON_MOON if "dark" in resolved_active_theme.lower() else ICON_SUN
        )
        resolved_label = str(self.label) if self.label else DEFAULT_LABEL
        resolved_select_id = (
            str(self.select_id) if self.select_id else DEFAULT_SELECT_ID
        )

        context["label"] = resolved_label
        context["select_id"] = resolved_select_id
        context["resolved_active_theme"] = resolved_active_theme
        context["active_icon"] = active_icon
        context["normalized_themes"] = normalized_themes
        context["has_themes"] = bool(normalized_themes)
        context["has_multiple_themes"] = len(normalized_themes) > 1
        return context
