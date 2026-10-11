"""Built-in semantic notice / callout element component."""

import typing

from dj_design_system import components, parameters


DEFAULT_VARIANT = "info"
NOTICE_VARIANTS: tuple[str, ...] = ("info", "success", "warning", "error")
ALERT_VARIANTS: tuple[str, ...] = ("warning", "error")


class Notice(components.BlockComponent):
    """A semantic callout banner for informational notes, confirmations, warnings, and errors.

    Use ``Notice`` (``{% dds__notice %}``) to surface contextual feedback,
    admonitions, deprecation warnings, or error messages alongside prose or
    interactive controls. Automatically maps ``warning`` and ``error`` variants
    to ``role="alert"`` and ``info`` and ``success`` variants to ``role="note"``.

    Variants:
        - ``info`` (default): General informational callout or tip.
        - ``success``: Positive confirmation or verified status message.
        - ``warning``: Caution, deprecation, or non-blocking alert.
        - ``error``: Critical failure, validation blocker, or destructive warning.

    Example usage::

        {% dds__notice variant="info" title="Note" %}
            Changes take effect immediately.
        {% enddds__notice %}

        {% dds__notice variant="error" title="Configuration Error" %}
            Missing required template setting.
        {% enddds__notice %}
    """

    variant = parameters.StrParam(
        description="Semantic status level.",
        default=DEFAULT_VARIANT,
        required=False,
        choices=list(NOTICE_VARIANTS),
    )
    title = parameters.StrParam(
        description="Optional notice heading.",
        default="",
        required=False,
    )
    icon = parameters.StrParam(
        description="Optional icon override; pass 'none' to suppress the icon.",
        default="",
        required=False,
    )
    role = parameters.StrParam(
        description="Optional ARIA role override ('note', 'alert', 'region', or '').",
        default="",
        required=False,
    )

    def get_context(self) -> dict[str, typing.Any]:
        """Compute template context with resolved icon, ARIA role, and title state.

        Returns:
            Dictionary containing component parameters, ``resolved_icon``,
            ``show_icon``, ``role``, and ``has_title``.
        """
        context = super().get_context()
        variant = self.variant if self.variant is not None else DEFAULT_VARIANT
        show_icon = self.icon != "none"
        resolved_icon = (
            self.icon
            if self.icon and self.icon != "none"
            else variant
        )
        resolved_role = (
            self.role
            if self.role
            else ("alert" if variant in ALERT_VARIANTS else "note")
        )
        has_title = bool(self.title)

        context["variant"] = variant
        context["title"] = self.title if self.title is not None else ""
        context["content"] = self.content if self.content is not None else ""
        context["show_icon"] = show_icon
        context["resolved_icon"] = resolved_icon
        context["icon"] = self.icon if self.icon is not None else ""
        context["role"] = resolved_role
        context["has_title"] = has_title
        return context
