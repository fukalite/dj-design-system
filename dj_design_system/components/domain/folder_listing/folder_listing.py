"""Built-in folder listing domain component."""

import typing

from dj_design_system import components, parameters
from dj_design_system.components.elements import icon as icon_element


DEFAULT_EMPTY_MESSAGE = "This folder is empty."
DEFAULT_ITEM_URL = "#"


class FolderListing(components.TagComponent):
    """Domain gallery component for displaying the child entries of a folder node.

    Renders a ``<section class="dds-folder-listing" data-surface="docs">``
    landmark containing an optional folder heading, a responsive ``.l-grid``
    of navigable item cards (or an empty-state message when no items exist),
    and an optional ``index.md`` authoring hint notice.

    Each item card displays a semantic node icon (`folder`, `component`, `doc`,
    or `code`), the item label, a categorical ``dds__badge`` indicating the node
    kind (`Folder`, `Component`, `Document`, or `Variant`), and an optional
    child count summary when the entry has children.

    Args:
        title: Folder heading title rendered as ``<h1>`` when non-empty.
        items: Child ``NavNode`` objects or item dicts to display.
        empty_message: Fallback message displayed when ``items`` is empty.
        show_debug_hint: Whether to render the ``index.md`` authoring hint notice.

    Example usage::

        {% dds__folder_listing "Elements" items %}
        {% dds__folder_listing title="Domain" items=children show_debug_hint=True %}
    """

    template_name = (
        "dj_design_system/components/domain/folder_listing/folder_listing.html"
    )
    _template_name = template_name

    title = parameters.StrParam(
        description="Folder heading title.",
        default="",
        required=False,
    )
    items = parameters.ListParam(
        description="Child NavNode objects or item dicts to display.",
        default=None,
        required=False,
    )
    empty_message = parameters.StrParam(
        description="Fallback message when the folder has no children.",
        default=DEFAULT_EMPTY_MESSAGE,
        required=False,
    )
    show_debug_hint = parameters.BoolParam(
        description="Whether to display the index.md authoring hint notice.",
        default=False,
        required=False,
    )

    class Meta:
        positional_args = ["title", "items"]

    class Media:
        css = "dj_design_system/components/domain/folder_listing/folder_listing.css"

    def get_context(self) -> dict[str, typing.Any]:
        """Build the normalized template context for the folder listing.

        Returns:
            Dictionary containing normalized ``items``, ``normalized_items``,
            ``title``, ``has_title``, ``has_items``, ``empty_message``, and
            ``show_debug_hint``.
        """
        context = super().get_context()
        raw_items = list(self.items) if self.items else []
        normalized_items: list[dict[str, typing.Any]] = []

        for raw_item in raw_items:
            if isinstance(raw_item, dict):
                raw_label: typing.Any = raw_item.get("label")
                if raw_label is None:
                    raw_label = raw_item.get("name", "")
                raw_url: typing.Any = raw_item.get("url") or raw_item.get("href")
                raw_node_type: typing.Any = (
                    raw_item.get("node_type")
                    or raw_item.get("type")
                    or raw_item.get("node_kind")
                )
                raw_icon: typing.Any = raw_item.get("icon")
                raw_children: typing.Any = raw_item.get("children")
                raw_has_children: typing.Any = raw_item.get("has_children")
                raw_child_count: typing.Any = raw_item.get("child_count")
                is_component = bool(raw_item.get("is_component", False))
                is_document = bool(raw_item.get("is_document", False))
                is_variant = bool(raw_item.get("is_variant", False))
            else:
                raw_label = getattr(raw_item, "label", None)
                if raw_label is None:
                    raw_label = getattr(raw_item, "name", str(raw_item))
                raw_url = getattr(raw_item, "url", None) or getattr(
                    raw_item, "href", None
                )
                raw_node_type = (
                    getattr(raw_item, "node_type", None)
                    or getattr(raw_item, "type", None)
                    or getattr(raw_item, "node_kind", None)
                )
                raw_icon = getattr(raw_item, "icon", None)
                raw_children = getattr(raw_item, "children", None)
                raw_has_children = getattr(raw_item, "has_children", None)
                raw_child_count = getattr(raw_item, "child_count", None)
                is_component = bool(getattr(raw_item, "is_component", False))
                is_document = bool(getattr(raw_item, "is_document", False))
                is_variant = bool(getattr(raw_item, "is_variant", False))

            node_type_val = getattr(raw_node_type, "value", raw_node_type)
            node_type_str = str(node_type_val).lower() if node_type_val else ""

            if is_component or node_type_str == "component":
                node_kind = "component"
                default_icon = "component"
                badge_label = "Component"
                badge_variant = "info"
            elif is_document or node_type_str in ("document", "doc"):
                node_kind = "document"
                default_icon = "doc"
                badge_label = "Document"
                badge_variant = "neutral"
            elif is_variant or node_type_str == "variant":
                node_kind = "variant"
                default_icon = "code"
                badge_label = "Variant"
                badge_variant = "code"
            else:
                node_kind = "folder"
                default_icon = "folder"
                badge_label = "Folder"
                badge_variant = "neutral"

            icon_candidate = str(raw_icon) if raw_icon else ""
            icon = (
                icon_candidate
                if icon_candidate in icon_element.ICON_NAMES
                else default_icon
            )

            if isinstance(raw_child_count, int) and not isinstance(
                raw_child_count, bool
            ):
                child_count = max(0, raw_child_count)
            elif raw_has_children is False:
                child_count = 0
            elif raw_children is not None:
                child_count = len(list(raw_children))
            else:
                child_count = 0

            if child_count == 1:
                child_count_label = "1 item"
            elif child_count > 1:
                child_count_label = f"{child_count} items"
            else:
                child_count_label = ""

            label = str(raw_label) if raw_label is not None else ""
            url = str(raw_url) if raw_url else DEFAULT_ITEM_URL

            normalized_items.append(
                {
                    "label": label,
                    "url": url,
                    "node_kind": node_kind,
                    "icon": icon,
                    "badge_label": badge_label,
                    "badge_variant": badge_variant,
                    "child_count_label": child_count_label,
                    "has_child_count": bool(child_count_label),
                }
            )

        title = str(self.title) if self.title else ""
        context["title"] = title
        context["has_title"] = bool(title)
        context["items"] = normalized_items
        context["normalized_items"] = normalized_items
        context["has_items"] = bool(normalized_items)
        context["empty_message"] = self.empty_message or DEFAULT_EMPTY_MESSAGE
        context["show_debug_hint"] = bool(self.show_debug_hint)
        return context
