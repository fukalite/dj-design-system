"""Inline SVG icon primitive for the built-in dds gallery."""

import typing

from dj_design_system import components, parameters


ICON_NAMES: tuple[str, ...] = (
    "external-link",
    "eye",
    "code",
    "file-code",
    "monitor",
    "box-model",
    "ruler",
    "rtl",
    "component",
    "doc",
    "folder",
    "folder-open",
    "search",
    "menu",
    "close",
    "chevron-right",
    "chevron-down",
    "copy",
    "check",
    "sun",
    "moon",
    "reset",
    "info",
    "success",
    "warning",
    "error",
)

ICON_SIZES: tuple[str, ...] = ("xs", "sm", "md", "lg")
DEFAULT_ICON_SIZE = "md"


class Icon(components.TagComponent):
    """Inline SVG icon primitive with semantic sizing and accessibility support.

    Renders a single 24x24 stroke-based SVG icon from the built-in gallery icon
    set. When ``label`` is omitted or empty, the icon is treated as purely
    decorative and rendered with ``aria-hidden="true"``. When ``label`` is
    provided, the icon is exposed to assistive technologies with ``role="img"``
    and ``aria-label``.

    Args:
        name: Identifier of the icon to render from ``ICON_NAMES``.
        size: Semantic size token step (``"xs"``, ``"sm"``, ``"md"``, ``"lg"``).
        label: Optional accessible label for non-decorative icons.
    """

    template_name = "dj_design_system/components/elements/icon/icon.html"

    name = parameters.StrParam(
        description="Icon identifier.",
        choices=list(ICON_NAMES),
    )
    size = parameters.StrParam(
        description="Semantic icon size.",
        default=DEFAULT_ICON_SIZE,
        required=False,
        choices=list(ICON_SIZES),
    )
    label = parameters.StrParam(
        description="Accessible label; when omitted, the icon is decorative (aria-hidden).",
        default="",
        required=False,
    )

    class Meta:
        positional_args = ["name"]

    class Media:
        css = "dj_design_system/components/elements/icon/icon.css"

    def get_context(self) -> dict[str, typing.Any]:
        """Build the template context with resolved accessibility attributes.

        Returns:
            Dictionary containing component parameters and accessibility state.
        """
        context = super().get_context()
        is_decorative = not bool(self.label)
        context["size"] = self.size or DEFAULT_ICON_SIZE
        context["is_decorative"] = is_decorative
        context["aria_hidden"] = "true" if is_decorative else None
        context["role"] = None if is_decorative else "img"
        return context
