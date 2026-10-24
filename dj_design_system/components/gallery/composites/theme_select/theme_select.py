"""Built-in gallery theme selector composite component."""

import dataclasses
import typing

from dj_design_system import components, parameters


DEFAULT_ACTIVE_THEME = "light"
DEFAULT_LABEL = "Global Theme"
DEFAULT_SELECT_ID = "gallery-global-theme-select"
DEFAULT_ICON = "sun"


@dataclasses.dataclass(frozen=True)
class ThemeOption:
    """Typed theme option descriptor for ``ThemeSelect``.

    Attributes:
        value: Theme identifier string.
        label: Human-readable display label for the theme.
    """

    value: str
    label: str


class ThemeSelect(components.TagComponent):
    """Gallery theme selector control with Light DOM custom element enhancement.

    Use ``ThemeSelect`` (``{% dds__theme_select %}``) in the gallery topbar or
    sandbox toolbar to allow switching between configured consumer component
    themes. Accepts ``ThemeOption`` or ``Theme`` dataclass instances,
    dictionaries with ``value`` and ``label`` keys, or plain theme identifier
    strings, normalizing them in ``get_context()``.

    When to Use:
        - Allowing users to switch the active consumer component preview theme in the topbar or sandbox toolbar.
        - Presenting a dropdown list of themes that dispatches ``dds:theme-change`` events.
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
    show_icon = parameters.BoolParam(
        description="Whether to render the leading icon.",
        default=True,
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
        extracted_options: list[ThemeOption] = []

        for raw_item in raw_themes:
            if isinstance(raw_item, ThemeOption):
                extracted_options.append(raw_item)
            elif isinstance(raw_item, (tuple, list)) and len(raw_item) >= 2:
                extracted_options.append(
                    ThemeOption(value=str(raw_item[0]), label=str(raw_item[1]))
                )
            elif isinstance(raw_item, str):
                label_text = raw_item.capitalize() if raw_item.islower() else raw_item
                extracted_options.append(ThemeOption(value=raw_item, label=label_text))
            elif isinstance(raw_item, dict):
                raw_val = raw_item.get("value")
                raw_lbl = raw_item.get("label")
                val_str = str(raw_val) if raw_val is not None else ""
                lbl_str = (
                    str(raw_lbl)
                    if raw_lbl is not None
                    else (val_str.capitalize() if val_str.islower() else val_str)
                )
                extracted_options.append(ThemeOption(value=val_str, label=lbl_str))
            else:
                raw_val = getattr(raw_item, "value", None)
                raw_lbl = getattr(raw_item, "label", None)
                val_str = str(raw_val) if raw_val is not None else ""
                lbl_str = (
                    str(raw_lbl)
                    if raw_lbl is not None
                    else (val_str.capitalize() if val_str.islower() else val_str)
                )
                extracted_options.append(ThemeOption(value=val_str, label=lbl_str))

        theme_values = [opt.value for opt in extracted_options]
        if self.active_theme and self.active_theme in theme_values:
            resolved_active_theme = str(self.active_theme)
        elif extracted_options:
            resolved_active_theme = extracted_options[0].value
        else:
            resolved_active_theme = str(self.active_theme or DEFAULT_ACTIVE_THEME)

        normalized_themes: list[dict[str, typing.Any]] = [
            {
                "value": opt.value,
                "label": opt.label,
                "is_selected": opt.value == resolved_active_theme,
            }
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
        context["show_icon"] = bool(self.show_icon)
        context["normalized_themes"] = normalized_themes
        context["has_themes"] = bool(normalized_themes)
        context["has_multiple_themes"] = len(normalized_themes) > 1
        return context
