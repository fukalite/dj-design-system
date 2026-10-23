"""Built-in interactive option item for dds__popout menus."""

import typing

from dj_design_system import components, parameters
from dj_design_system.components.elements import icon as icon_element


class PopoutOption(components.TagComponent):
    """Polymorphic menu item or selectable radio option inside a ``dds__popout`` menu.

    Renders an ``<a class="dds-popout-option" role="menuitem">`` link when
    ``href`` is non-empty and ``disabled`` is ``False``, or a
    ``<button type="button" class="dds-popout-option" role="menuitemradio">``
    control otherwise. Emits ``data-popout-option`` and ``data-value`` hooks so
    the parent ``<dds-popout>`` Light DOM custom element can manage selection
    state and dispatch ``dds:popout-select`` events.

    Args:
        label: Visible option text label (also used as fallback for ``value``).
        value: Option value payload; falls back to ``label`` when empty.
        icon: Optional leading icon name from ``ICON_NAMES``.
        selected: Whether this option is currently checked (``aria-checked="true"``).
        disabled: Whether this option is disabled (forces ``<button disabled>``).
        href: Optional link URL; renders an ``<a>`` tag when not disabled.

    Example usage::

        {% dds__popout_option "Light" value="light" icon="sun" selected=True %}
        {% dds__popout_option "Documentation" href="/docs/" icon="external-link" %}
    """

    label = parameters.StrParam(description="Option text label.")
    value = parameters.StrParam(
        description="Option value payload.",
        default="",
        required=False,
    )
    icon = parameters.StrParam(
        description="Optional leading icon name.",
        default="",
        required=False,
        choices=["", *icon_element.ICON_NAMES],
    )
    selected = parameters.BoolParam(
        description="Whether this option is currently selected.",
        default=False,
        required=False,
    )
    disabled = parameters.BoolParam(
        description="Whether this option is disabled.",
        default=False,
        required=False,
    )
    href = parameters.StrParam(
        description="Optional link URL.",
        default="",
        required=False,
    )

    class Meta:
        positional_args = ["label"]

    def get_context(self) -> dict[str, typing.Any]:
        """Compute normalized template context for button or link option rendering.

        Returns:
            Dictionary containing component parameters and pre-computed
            ``is_link``, ``resolved_value``, ``aria_checked``, and ``has_icon``
            values.
        """
        context = super().get_context()
        is_link = bool(self.href) and not self.disabled
        resolved_value = str(self.value) if self.value else str(self.label)
        aria_checked = "true" if self.selected else "false"
        has_icon = bool(self.icon)

        context["is_link"] = is_link
        context["resolved_value"] = resolved_value
        context["aria_checked"] = aria_checked
        context["has_icon"] = has_icon
        return context
