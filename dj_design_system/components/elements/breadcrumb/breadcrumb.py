"""Built-in breadcrumb navigation trail element component."""

import typing

from dj_design_system import components, parameters
from dj_design_system.components.elements import icon as icon_element


DEFAULT_ARIA_LABEL = "Breadcrumb"
DEFAULT_SEPARATOR_ICON = "chevron-right"


class Breadcrumb(components.TagComponent):
    """Hierarchical breadcrumb trail navigation primitive.

    Renders an accessible ``<nav class="dds-breadcrumb">`` landmark wrapping an
    Every Layout ``<ol class="l-cluster">`` trail. Each item in ``items`` may be
    provided as a dictionary (with ``label`` and optional ``url``/``href`` and
    ``icon`` keys), an object exposing those attributes, or a plain string.

    The final item in the trail is automatically marked as the current page
    (``<span aria-current="page">``) and its link URL is cleared in
    ``get_context()`` so the active location is never rendered as a redundant
    self-link. Preceding items with a ``url`` or ``href`` render as ``<a>``
    links; items without a URL render as static ``<span>`` elements.

    Example usage::

        {% dds__breadcrumb items=trail %}
        {% dds__breadcrumb items separator_icon="chevron-right" aria_label="Component path" %}
    """

    template_name = "dj_design_system/components/elements/breadcrumb/breadcrumb.html"
    _template_name = template_name

    items = parameters.ListParam(
        description=(
            "Ordered list of trail items (dicts with 'label' and optional "
            "'url'/'href' and 'icon')."
        ),
        default=None,
        required=False,
    )
    aria_label = parameters.StrParam(
        description="Accessible landmark label.",
        default=DEFAULT_ARIA_LABEL,
        required=False,
    )
    separator_icon = parameters.StrParam(
        description="Icon name rendered between trail items.",
        default=DEFAULT_SEPARATOR_ICON,
        required=False,
        choices=list(icon_element.ICON_NAMES),
    )

    class Meta:
        positional_args = ["items"]

    class Media:
        css = "dj_design_system/components/elements/breadcrumb/breadcrumb.css"

    def get_context(self) -> dict[str, typing.Any]:
        """Build the normalized template context for the breadcrumb trail.

        Returns:
            Dictionary containing resolved ``aria_label``, ``separator_icon``,
            ``normalized_items``, and ``has_items``.
        """
        context = super().get_context()
        raw_items = list(self.items) if self.items else []
        total = len(raw_items)
        normalized_items: list[dict[str, typing.Any]] = []

        for idx, raw_item in enumerate(raw_items):
            is_current = idx == total - 1
            if isinstance(raw_item, str):
                raw_label: typing.Any = raw_item
                raw_url: typing.Any = None
                raw_icon: typing.Any = None
            elif isinstance(raw_item, dict):
                raw_label = raw_item.get("label")
                if raw_label is None:
                    raw_label = raw_item.get("name", "")
                raw_url = raw_item.get("url") or raw_item.get("href")
                raw_icon = raw_item.get("icon")
            else:
                raw_label = getattr(raw_item, "label", None)
                if raw_label is None:
                    raw_label = getattr(raw_item, "name", str(raw_item))
                raw_url = getattr(raw_item, "url", None) or getattr(
                    raw_item, "href", None
                )
                raw_icon = getattr(raw_item, "icon", None)

            label = str(raw_label) if raw_label is not None else ""
            resolved_url = str(raw_url) if raw_url else None
            url = None if is_current else resolved_url
            icon = str(raw_icon) if raw_icon else None

            normalized_items.append(
                {
                    "label": label,
                    "url": url,
                    "icon": icon,
                    "is_current": is_current,
                    "has_url": bool(url),
                    "has_icon": bool(icon),
                }
            )

        context["aria_label"] = self.aria_label or DEFAULT_ARIA_LABEL
        context["separator_icon"] = self.separator_icon or DEFAULT_SEPARATOR_ICON
        context["normalized_items"] = normalized_items
        context["has_items"] = bool(normalized_items)
        return context
