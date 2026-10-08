"""Built-in semantic notice / callout element component."""

import typing

from dj_design_system import components, parameters
from dj_design_system.components.elements import icon as icon_element


DEFAULT_VARIANT = "info"
NOTICE_VARIANTS = ["info", "success", "warning", "error"]
ALERT_VARIANTS = ("warning", "error")


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

    template_name = "dj_design_system/components/elements/notice/notice.html"
    _template_name = template_name

    variant = parameters.StrParam(
        description="Semantic status level.",
        default=DEFAULT_VARIANT,
        required=False,
        choices=NOTICE_VARIANTS,
    )
    title = parameters.StrParam(
        description="Optional notice heading.",
        default="",
        required=False,
    )
    icon = parameters.StrParam(
        description="Optional icon override; defaults to variant status icon.",
        default="",
        required=False,
        choices=["", *icon_element.ICON_NAMES],
    )

    class Media:
        css = "dj_design_system/components/elements/notice/notice.css"

    def get_context(self) -> dict[str, typing.Any]:
        """Compute template context with resolved icon, ARIA role, and title state.

        Returns:
            Dictionary containing component parameters, ``resolved_icon``,
            ``role``, and ``has_title``.
        """
        context = super().get_context()
        variant = self.variant if self.variant is not None else DEFAULT_VARIANT
        resolved_icon = str(self.icon) if self.icon else str(variant)
        role = "alert" if variant in ALERT_VARIANTS else "note"
        has_title = bool(self.title)

        context["variant"] = variant
        context["title"] = self.title if self.title is not None else ""
        context["content"] = self.content if self.content is not None else ""
        context["resolved_icon"] = resolved_icon
        context["role"] = role
        context["has_title"] = has_title
        return context
