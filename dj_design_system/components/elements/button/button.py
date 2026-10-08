"""Polymorphic button and link control primitive for the built-in dds gallery."""

import typing

from dj_design_system import components, parameters
from dj_design_system.components.elements import icon as icon_element


BUTTON_VARIANTS: tuple[str, ...] = ("default", "primary", "ghost", "danger")
BUTTON_SIZES: tuple[str, ...] = ("sm", "md", "lg")
BUTTON_TYPES: tuple[str, ...] = ("button", "submit", "reset")
DEFAULT_VARIANT = "default"
DEFAULT_SIZE = "md"
DEFAULT_BUTTON_TYPE = "button"
SMALL_SIZE = "sm"
MEDIUM_SIZE = "md"
BLANK_TARGET = "_blank"
NOOPENER_NOREFERRER = "noopener noreferrer"


class Button(components.TagComponent):
    """Polymorphic interactive button or link control with icon and toggle states.

    Renders a semantic button element (``.dds-button``) by default, or an anchor
    link element (``.dds-button``) when ``href`` is provided and ``disabled`` is
    ``False``. Supports leading/trailing icons via ``{% dds__icon %}``,
    accessible icon-only controls, toggle buttons via ``aria-pressed``, and
    declarative ``data-action`` hooks for parent Web Components.

    Variants:
        - ``default``: Standard bordered control surface button.
        - ``primary``: High-emphasis action button using selected state tokens.
        - ``ghost``: Low-emphasis borderless toolbar and inline action button.
        - ``danger``: Destructive action button using error status tokens.

    Args:
        label: Button text label (or accessible ``aria-label`` when ``icon_only=True``).
        variant: Visual button style (``"default"``, ``"primary"``, ``"ghost"``, ``"danger"``).
        size: Button size step (``"sm"``, ``"md"``, ``"lg"``).
        icon: Optional leading or standalone icon identifier from ``ICON_NAMES``.
        icon_trailing: Optional trailing icon identifier from ``ICON_NAMES``.
        icon_only: Render only the icon and expose ``label`` as ``aria-label``.
        href: Optional URL; renders an anchor element when non-empty and not disabled.
        target: Optional link target attribute (e.g. ``"_blank"``).
        button_type: HTML button type attribute (``"button"``, ``"submit"``, ``"reset"``).
        disabled: Whether user interaction is disabled.
        pressed: Optional boolean toggle state for ``aria-pressed`` (``"true"``/``"false"``).
        action: Optional ``data-action`` hook for parent Web Components.
    """

    template_name = "dj_design_system/components/elements/button/button.html"
    _template_name = template_name

    label = parameters.StrParam(
        description="Button text label (or accessible aria-label when icon_only=True).",
        default="",
        required=False,
    )
    variant = parameters.StrParam(
        description="Visual button style.",
        default=DEFAULT_VARIANT,
        required=False,
        choices=list(BUTTON_VARIANTS),
    )
    size = parameters.StrParam(
        description="Button size.",
        default=DEFAULT_SIZE,
        required=False,
        choices=list(BUTTON_SIZES),
    )
    icon = parameters.StrParam(
        description="Optional leading or standalone icon name.",
        default="",
        required=False,
        choices=["", *icon_element.ICON_NAMES],
    )
    icon_trailing = parameters.StrParam(
        description="Optional trailing icon name.",
        default="",
        required=False,
        choices=["", *icon_element.ICON_NAMES],
    )
    icon_only = parameters.BoolParam(
        description="Render only the icon and use label as aria-label.",
        default=False,
        required=False,
    )
    href = parameters.StrParam(
        description="Optional link URL; renders an <a> element when provided and not disabled.",
        default="",
        required=False,
    )
    target = parameters.StrParam(
        description="Optional link target (e.g. _blank).",
        default="",
        required=False,
    )
    button_type = parameters.StrParam(
        description="HTML button type attribute.",
        default=DEFAULT_BUTTON_TYPE,
        required=False,
        choices=list(BUTTON_TYPES),
    )
    disabled = parameters.BoolParam(
        description="Whether interaction is disabled.",
        default=False,
        required=False,
    )
    pressed = parameters.BoolParam(
        description="Optional toggle state for aria-pressed ('true'/'false').",
        default=None,
        required=False,
    )
    action = parameters.StrParam(
        description="Optional data-action hook for parent web components.",
        default="",
        required=False,
    )

    class Meta:
        positional_args = ["label"]

    class Media:
        css = "dj_design_system/components/elements/button/button.css"

    def validate_params(self) -> None:
        """Validate accessibility and content invariants across button parameters.

        Invoked automatically by ``BaseComponent.__init__`` and ``get_context()``.

        Raises:
            ValueError: If an ``icon_only`` button omits ``label`` or ``icon``,
                or if a standard button provides neither ``label`` nor ``icon``.
        """
        if self.icon_only and not self.label:
            raise ValueError("icon_only buttons require a 'label' for accessibility.")
        if self.icon_only and not self.icon:
            raise ValueError("icon_only buttons require an 'icon' name.")
        if not self.icon_only and not self.label and not self.icon:
            raise ValueError("Button requires at least a 'label' or an 'icon'.")

    def get_context(self) -> dict[str, typing.Any]:
        """Compute normalized template context for polymorphic button or link rendering.

        Returns:
            Dictionary containing component parameters and pre-computed state flags.
        """
        self.validate_params()
        context = super().get_context()
        variant = self.variant or DEFAULT_VARIANT
        size = self.size or DEFAULT_SIZE
        button_type = self.button_type or DEFAULT_BUTTON_TYPE
        is_link = bool(self.href) and not self.disabled
        resolved_href = self.href if is_link else None
        resolved_target = self.target if (is_link and self.target) else None
        resolved_rel = (
            NOOPENER_NOREFERRER if (is_link and self.target == BLANK_TARGET) else None
        )
        aria_pressed = (
            None if self.pressed is None else ("true" if self.pressed else "false")
        )
        aria_label = self.label if self.icon_only else None
        has_icon = bool(self.icon)
        has_trailing_icon = bool(self.icon_trailing) and not self.icon_only
        show_label = bool(self.label) and not self.icon_only
        icon_size = SMALL_SIZE if size == SMALL_SIZE else MEDIUM_SIZE
        has_action = bool(self.action)

        context["variant"] = variant
        context["size"] = size
        context["button_type"] = button_type
        context["is_link"] = is_link
        context["resolved_href"] = resolved_href
        context["resolved_target"] = resolved_target
        context["resolved_rel"] = resolved_rel
        context["aria_pressed"] = aria_pressed
        context["aria_label"] = aria_label
        context["has_icon"] = has_icon
        context["has_trailing_icon"] = has_trailing_icon
        context["show_label"] = show_label
        context["icon_size"] = icon_size
        context["has_action"] = has_action
        return context
