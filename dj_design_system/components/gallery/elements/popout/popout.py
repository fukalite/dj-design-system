"""Built-in interactive popout dropdown menu element component."""

import typing

from dj_design_system import components, parameters, slots


ALIGN_START = "start"
ALIGN_END = "end"
ALIGN_CHOICES: tuple[str, ...] = (ALIGN_START, ALIGN_END)
DEFAULT_ALIGN = ALIGN_START
DEFAULT_ROLE = "menu"
ROLE_CHOICES: tuple[str, ...] = ("menu", "dialog", "region", "none")


class Popout(components.BlockComponent):
    """Accessible dropdown menu and popover primitive backed by ``<dds-popout>``.

    Renders a ``<dds-popout class="dds-popout">`` Light DOM custom element with
    either a default trigger ``<button class="dds-popout-trigger" data-popout-trigger>``
    or custom trigger markup supplied via ``{% slot "trigger" %}``, paired with a
    floating ``<div data-popout-menu data-surface="popout">`` container.

    Args:
        label: Trigger button text label (also used as ``aria-label`` when
            ``icon_only=True`` and as fallback for ``menu_label``).
        icon: Optional leading trigger icon name.
        icon_only: Render an icon-only trigger button without label span or
            trailing chevron icon.
        align: Horizontal alignment of the floating menu (``"start"`` or ``"end"``).
        open: Whether the popout menu is initially open.
        role: ARIA role for the floating pane (``"menu"``, ``"dialog"``,
            ``"region"``, or ``"none"``).
        menu_label: Accessible ``aria-label`` for the floating surface; falls
            back to ``label`` when omitted.

    Example usage::

        {% dds__popout "Theme" icon="sun" %}
            {% slot "trigger" %}
                <button type="button" class="dds-button" data-popout-trigger aria-haspopup="true" aria-expanded="false">
                    Theme
                </button>
            {% endslot %}
        {% enddds__popout %}
    """

    label = parameters.StrParam(
        description="Trigger button label.",
        default="",
        required=False,
    )
    icon = parameters.StrParam(
        description="Optional leading trigger icon name.",
        default="",
        required=False,
    )
    icon_only = parameters.BoolParam(
        description="Render icon-only trigger button.",
        default=False,
        required=False,
    )
    align = parameters.StrParam(
        description="Menu horizontal alignment.",
        default=DEFAULT_ALIGN,
        required=False,
        choices=list(ALIGN_CHOICES),
    )
    open = parameters.BoolParam(
        description="Whether the popout menu is initially open.",
        default=False,
        required=False,
    )
    role = parameters.StrParam(
        description="ARIA role for the floating pane ('menu', 'dialog', 'region', or 'none').",
        default=DEFAULT_ROLE,
        required=False,
        choices=list(ROLE_CHOICES),
    )
    menu_label = parameters.StrParam(
        description="Accessible label for the floating menu.",
        default="",
        required=False,
    )

    class Meta:
        positional_args = ["label"]
        slots = {
            "trigger": slots.Slot(
                required=False,
                description=(
                    "Optional custom trigger markup; when omitted, renders a "
                    "default trigger button."
                ),
            ),
            "menu": slots.Slot(
                required=False,
                description="Optional floating menu content markup.",
            ),
        }

    def get_context(self) -> dict[str, typing.Any]:
        """Compute normalized template context for trigger, menu, and slots.

        Returns:
            Dictionary containing component parameters, ARIA/state flags,
            ``slots``, and ``content``.
        """
        context = super().get_context()
        state = "open" if self.open else "closed"
        aria_expanded = "true" if self.open else "false"
        resolved_menu_label = (
            str(self.menu_label) if self.menu_label else str(self.label)
        )
        has_icon = bool(self.icon)
        show_label = bool(self.label) and not self.icon_only
        aria_label = str(self.label) if self.icon_only else None
        role = self.role or DEFAULT_ROLE
        aria_haspopup = "dialog" if role == "dialog" else "true"

        context["align"] = self.align or DEFAULT_ALIGN
        context["state"] = state
        context["aria_expanded"] = aria_expanded
        context["role"] = role
        context["aria_haspopup"] = aria_haspopup
        context["resolved_menu_label"] = resolved_menu_label
        context["has_icon"] = has_icon
        context["show_label"] = show_label
        context["aria_label"] = aria_label
        context["slots"] = self.slots
        context["content"] = self.content or ""
        context["menu_content"] = (
            self.slots.get("menu")
            if (self.slots and self.slots.get("menu"))
            else (self.content or "")
        )
        return context
