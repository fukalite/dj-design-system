"""Built-in folder listing domain component."""

import typing

from dj_design_system import components, data, parameters
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

    def get_context(self) -> dict[str, typing.Any]:
        """Build the normalized template context for the folder listing.

        Returns:
            Dictionary containing normalized ``items``, ``normalized_items``,
            ``title``, ``has_title``, ``has_items``, ``empty_message``, and
            ``show_debug_hint``.
        """
        context = super().get_context()
        raw_items = list(self.items) if self.items is not None else []
        normalized_items: list[dict[str, typing.Any]] = []

        for raw_item in raw_items:
            parsed = data.NavItemInputData.from_raw(
                raw_item,
                default_label_from_name=True,
                default_url=DEFAULT_ITEM_URL,
            )

            if parsed.is_component or parsed.node_type == "component":
                node_kind = "component"
                default_icon = "component"
                badge_label = "Component"
                badge_variant = "info"
            elif parsed.is_document or parsed.node_type in ("document", "doc"):
                node_kind = "document"
                default_icon = "doc"
                badge_label = "Document"
                badge_variant = "neutral"
            elif parsed.is_variant or parsed.node_type == "variant":
                node_kind = "variant"
                default_icon = "code"
                badge_label = "Variant"
                badge_variant = "code"
            else:
                node_kind = "folder"
                default_icon = "folder"
                badge_label = "Folder"
                badge_variant = "neutral"

            icon = (
                parsed.icon if parsed.icon in icon_element.ICON_NAMES else default_icon
            )

            if parsed.child_count is not None:
                child_count = parsed.child_count
            elif parsed.has_children is False:
                child_count = 0
            else:
                child_count = len(parsed.children)

            if child_count == 1:
                child_count_label = "1 item"
            elif child_count > 1:
                child_count_label = f"{child_count} items"
            else:
                child_count_label = ""

            normalized_items.append(
                {
                    "label": parsed.label,
                    "url": parsed.url,
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
