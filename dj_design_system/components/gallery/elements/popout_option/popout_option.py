"""Built-in interactive option item for dds__popout menus."""

import typing

from dj_design_system import components, parameters


ROLE_MENUITEM = "menuitem"
ROLE_MENUITEMRADIO = "menuitemradio"
ROLE_MENUITEMCHECKBOX = "menuitemcheckbox"
ROLE_CHOICES: tuple[str, ...] = (
    "",
    ROLE_MENUITEM,
    ROLE_MENUITEMRADIO,
    ROLE_MENUITEMCHECKBOX,
)


class PopoutOption(components.TagComponent):
    """Polymorphic menu item or selectable option inside a ``dds__popout`` menu.

    Renders an ``<a class="dds-popout-option" role="menuitem">`` link when
    ``href`` is non-empty (retaining link semantics with ``aria-disabled="true"``
    when disabled), or a ``<button type="button" class="dds-popout-option">``
    control otherwise. Emits ``data-popout-option`` and ``data-value`` hooks so
    the parent ``<dds-popout>`` Light DOM custom element can manage selection
    state and dispatch ``dds:popout-select`` events.

    When to Use:
        - Rendering selectable radio-style options inside a ``{% dds__popout %}`` menu.
        - Rendering action items (``role="menuitem"``) inside an action or overflow menu.
        - Rendering navigation links (``href="..."``) inside a flyout or navigation menu.
    """

    label = parameters.StrParam(description="Option text label.")
    value = parameters.StrParam(
        description="Option value payload.",
        default="",
        required=False,
    )
    role = parameters.StrParam(
        description="ARIA menu item role ('menuitem', 'menuitemradio', or 'menuitemcheckbox').",
        default="",
        required=False,
        choices=list(ROLE_CHOICES),
    )
    icon = parameters.StrParam(
        description="Optional leading icon name.",
        default="",
        required=False,
    )
    shortcut = parameters.StrParam(
        description="Optional keyboard shortcut text hint.",
        default="",
        required=False,
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
            ``is_link``, ``resolved_role``, ``resolved_value``, ``is_checkable``,
            ``aria_checked``, ``has_icon``, and ``has_shortcut`` values.
        """
        context = super().get_context()
        is_link = bool(self.href)
        resolved_value = str(self.value) if self.value else str(self.label)
        if self.role:
            resolved_role = self.role
        elif is_link:
            resolved_role = ROLE_MENUITEM
        else:
            resolved_role = ROLE_MENUITEMRADIO

        is_checkable = resolved_role in (ROLE_MENUITEMRADIO, ROLE_MENUITEMCHECKBOX)
        aria_checked = "true" if self.selected else "false"
        has_icon = bool(self.icon)
        has_shortcut = bool(self.shortcut)

        context["is_link"] = is_link
        context["resolved_role"] = resolved_role
        context["resolved_value"] = resolved_value
        context["is_checkable"] = is_checkable
        context["aria_checked"] = aria_checked
        context["has_icon"] = has_icon
        context["has_shortcut"] = has_shortcut
        return context
