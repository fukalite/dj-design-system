"""Built-in recursive navigation tree composite component for the dds gallery."""

import dataclasses
import typing

from dj_design_system import components, parameters
from dj_design_system.components.gallery.elements import icon as icon_element


DEFAULT_ARIA_LABEL = "Component navigation"
DEFAULT_NODE_URL = "#"
FOLDER_STATE_CLOSED = "closed"
FOLDER_STATE_OPEN = "open"
ICON_CODE = "code"
ICON_COMPONENT = "component"
ICON_COMPONENT_VARIANTS = "component-variants"
ICON_DOC = "doc"
ICON_FOLDER = "folder"
ICON_VARIANT = "variant"
NODE_KIND_APP = "app"
NODE_KIND_FOLDER = "folder"
NODE_KIND_LEAF = "leaf"
NODE_TYPE_APP = "app"
NODE_TYPE_COMPONENT = "component"
NODE_TYPE_DOCUMENT = "document"
NODE_TYPE_FOLDER = "folder"
NODE_TYPE_VARIANT = "variant"


@dataclasses.dataclass(frozen=True)
class NavTreeNode:
    """Normalized navigation tree node data contract for ``NavTree``."""

    label: str
    slug: str
    node_type: str = ""
    url: str = DEFAULT_NODE_URL
    active_path: str = ""
    base_active_path: str = ""
    children: list[typing.Any] = dataclasses.field(default_factory=list)
    icon: str = ""
    is_component: bool | None = None
    is_document: bool | None = None
    is_variant: bool | None = None
    has_children: bool | None = None
    has_index_doc: bool = False

    @staticmethod
    def read_field(
        source: typing.Any,
        key: str,
        default: typing.Any = None,
    ) -> typing.Any:
        """Read an attribute or dictionary key from a raw navigation node."""
        if isinstance(source, dict):
            return source.get(key, default)
        return getattr(source, key, default)

    @classmethod
    def from_raw(
        cls,
        raw_node: typing.Any,
        *,
        default_url: str = DEFAULT_NODE_URL,
    ) -> "NavTreeNode":
        """Normalise a ``NavTreeNode``, ``NavNode``, dict, or duck-typed object."""
        raw_label = cls.read_field(raw_node, "label")
        if raw_label is None:
            raw_label = ""
        raw_slug = cls.read_field(raw_node, "slug", "")
        raw_type = (
            cls.read_field(raw_node, "node_type")
            or cls.read_field(raw_node, "type")
            or cls.read_field(raw_node, "node_kind")
            or ""
        )
        raw_url = cls.read_field(raw_node, "url") or cls.read_field(raw_node, "href")
        raw_active = cls.read_field(raw_node, "active_path", "")
        raw_base_active = cls.read_field(raw_node, "base_active_path", "")
        raw_children_val = cls.read_field(raw_node, "children")
        raw_icon = cls.read_field(raw_node, "icon")
        raw_is_component = cls.read_field(raw_node, "is_component")
        raw_is_document = cls.read_field(raw_node, "is_document")
        raw_is_variant = cls.read_field(raw_node, "is_variant")
        raw_has_children = cls.read_field(raw_node, "has_children")
        raw_has_index_doc = cls.read_field(raw_node, "has_index_doc")
        if raw_has_index_doc is None:
            raw_has_index_doc = cls.read_field(raw_node, "index_doc_path") is not None

        node_type_val = getattr(raw_type, "value", raw_type)
        node_type = str(node_type_val).lower() if node_type_val else ""
        children = (
            list(raw_children_val)
            if isinstance(raw_children_val, (list, tuple, set))
            else (list(raw_children_val) if raw_children_val is not None else [])
        )
        return cls(
            label=str(raw_label) if raw_label is not None else "",
            slug=str(raw_slug) if raw_slug is not None else "",
            node_type=node_type,
            url=str(raw_url) if raw_url else default_url,
            active_path=str(raw_active) if raw_active else "",
            base_active_path=str(raw_base_active) if raw_base_active else "",
            children=children,
            icon=str(raw_icon) if raw_icon else "",
            is_component=(
                bool(raw_is_component) if raw_is_component is not None else None
            ),
            is_document=(
                bool(raw_is_document) if raw_is_document is not None else None
            ),
            is_variant=(bool(raw_is_variant) if raw_is_variant is not None else None),
            has_children=(
                bool(raw_has_children) if raw_has_children is not None else None
            ),
            has_index_doc=bool(raw_has_index_doc),
        )


class NavTree(components.TagComponent):
    """Recursive sidebar navigation tree with collapsible folders and active states.

    Renders a ``<dds-nav-tree class="dds-nav-tree">`` custom element wrapping an
    accessible ``<nav class="dds-nav-tree-nav">`` landmark. Normalises up to four
    levels of ``NavTreeNode`` dataclasses, ``NavNode`` dataclasses, dictionaries,
    or duck-typed node objects in ``get_context()`` so the template remains
    purely declarative without filters or recursive partial includes.

    When to Use:
        - Rendering the gallery sidebar navigation with collapsible folder sections and active page indicators.
        - Hierarchical navigation menus representing apps, components, documentation pages, and variants.
    """

    nodes = parameters.ListParam(
        description="Top-level navigation nodes (NavTreeNode, NavNode, or dicts).",
        default=None,
        required=False,
    )
    active_path = parameters.StrParam(
        description="Current active gallery route path.",
        default="",
        required=False,
    )
    active_variant = parameters.StrParam(
        description="Optional active variant slug or Variant instance.",
        default="",
        required=False,
    )
    aria_label = parameters.StrParam(
        description="Accessible label for the navigation landmark.",
        default=DEFAULT_ARIA_LABEL,
        required=False,
    )

    class Meta:
        positional_args = ["nodes"]

    def __init__(self, **kwargs: typing.Any) -> None:
        """Initialise the navigation tree component.

        Args:
            **kwargs: Component parameter keyword arguments.
        """
        raw_variant = kwargs.get("active_variant")
        if (
            raw_variant is not None
            and not isinstance(raw_variant, str)
            and hasattr(raw_variant, "name")
        ):
            kwargs["active_variant"] = str(raw_variant.name)
        super().__init__(**kwargs)

    def get_context(self) -> dict[str, typing.Any]:
        """Build the normalized multi-level navigation tree template context.

        Returns:
            Dictionary containing ``normalized_nodes``, ``has_nodes``, and
            ``aria_label``.
        """
        context = super().get_context()
        variant_name = getattr(self.active_variant, "name", None)
        active_variant_slug = (
            str(variant_name)
            if variant_name is not None
            else str(self.active_variant or "")
        )
        raw_active_path = (self.active_path or "").split("?")[0].strip("/")

        raw_root_nodes = list(self.nodes) if self.nodes is not None else []
        normalized_nodes: list[dict[str, typing.Any]] = []
        work_stack: list[tuple[typing.Any, int, list[dict[str, typing.Any]], str]] = [
            (raw_node, 0, normalized_nodes, "") for raw_node in reversed(raw_root_nodes)
        ]
        post_order: list[tuple[dict[str, typing.Any], bool, str]] = []

        while work_stack:
            raw_node, depth, target_list, parent_active_path = work_stack.pop()

            parsed = NavTreeNode.from_raw(
                raw_node,
                default_url=DEFAULT_NODE_URL,
            )
            label = parsed.label
            slug = parsed.slug
            url = parsed.url
            node_type = parsed.node_type

            raw_children = parsed.children
            has_children = bool(raw_children) or bool(parsed.has_children)

            is_component = (
                parsed.is_component
                if parsed.is_component is not None
                else node_type == NODE_TYPE_COMPONENT
            )
            is_document = (
                parsed.is_document
                if parsed.is_document is not None
                else node_type == NODE_TYPE_DOCUMENT
            )
            is_variant = (
                parsed.is_variant
                if parsed.is_variant is not None
                else node_type == NODE_TYPE_VARIANT
            )
            has_index_doc = parsed.has_index_doc

            node_active_path = (
                parsed.active_path.split("?")[0].strip("/")
                if parsed.active_path
                else ""
            )
            if parsed.base_active_path:
                base_active_path = parsed.base_active_path.split("?")[0].strip("/")
            elif node_active_path:
                base_active_path = node_active_path
            elif is_variant and parent_active_path:
                base_active_path = parent_active_path
            else:
                base_active_path = ""

            if is_variant:
                is_active = bool(
                    raw_active_path
                    and raw_active_path == base_active_path
                    and active_variant_slug == slug
                )
            else:
                is_active = bool(
                    raw_active_path
                    and raw_active_path == node_active_path
                    and not active_variant_slug
                )

            if node_type == NODE_TYPE_APP:
                node_kind = NODE_KIND_APP
            elif has_children:
                node_kind = NODE_KIND_FOLDER
            else:
                node_kind = NODE_KIND_LEAF

            icon_str = parsed.icon
            if icon_str in icon_element.ICON_NAMES:
                resolved_icon = icon_str
            elif is_component and has_children:
                resolved_icon = ICON_COMPONENT_VARIANTS
            elif is_component:
                resolved_icon = ICON_COMPONENT
            elif is_document or (has_index_doc and not has_children):
                resolved_icon = ICON_DOC
            elif has_children or node_type == NODE_TYPE_FOLDER:
                resolved_icon = ICON_FOLDER
            elif is_variant:
                resolved_icon = ICON_VARIANT
            else:
                resolved_icon = ICON_COMPONENT

            folder_path = base_active_path or node_active_path
            folder_id = (
                node_active_path.strip("/").replace("/", "-")
                or slug.strip("/").replace("/", "-")
                or label.lower().strip().replace(" ", "-")
                or f"node-{depth}"
            )
            children_dom_id = f"dds-nav-children-{folder_id}"

            child_dicts: list[dict[str, typing.Any]] = []
            node_dict: dict[str, typing.Any] = {
                "label": label,
                "slug": slug,
                "url": url,
                "node_kind": node_kind,
                "is_variant": is_variant,
                "depth": depth,
                "is_active": is_active,
                "is_open": False,
                "folder_state": FOLDER_STATE_CLOSED,
                "aria_expanded": "false",
                "folder_id": folder_id,
                "children_dom_id": children_dom_id,
                "resolved_icon": resolved_icon,
                "children": child_dicts,
            }
            target_list.append(node_dict)
            post_order.append((node_dict, has_children, folder_path))

            next_parent_path = folder_path or parent_active_path
            for raw_child in reversed(raw_children):
                work_stack.append((raw_child, depth + 1, child_dicts, next_parent_path))

        for node_dict, has_children, folder_path in reversed(post_order):
            if has_children:
                path_open = bool(
                    raw_active_path
                    and folder_path
                    and (
                        raw_active_path == folder_path
                        or raw_active_path.startswith(f"{folder_path}/")
                    )
                )
                child_open = any(
                    bool(child["is_active"] or child["is_open"])
                    for child in node_dict["children"]
                )
                is_open = path_open or child_open
            else:
                is_open = False

            node_dict["is_open"] = is_open
            node_dict["folder_state"] = (
                FOLDER_STATE_OPEN if is_open else FOLDER_STATE_CLOSED
            )
            node_dict["aria_expanded"] = "true" if is_open else "false"

        tree_events: list[dict[str, typing.Any]] = []
        event_stack: list[tuple[str, dict[str, typing.Any]]] = [
            ("open", node) for node in reversed(normalized_nodes)
        ]
        while event_stack:
            action, node = event_stack.pop()
            if action == "close":
                close_kind = (
                    "app_close"
                    if node["node_kind"] == NODE_KIND_APP
                    else "folder_close"
                )
                tree_events.append({"event": close_kind, "node": node})
                continue

            if node["node_kind"] == NODE_KIND_APP:
                tree_events.append({"event": "app_open", "node": node})
                event_stack.append(("close", node))
                for child in reversed(node["children"]):
                    event_stack.append(("open", child))
            elif node["node_kind"] == NODE_KIND_FOLDER:
                tree_events.append({"event": "folder_open", "node": node})
                event_stack.append(("close", node))
                for child in reversed(node["children"]):
                    event_stack.append(("open", child))
            else:
                tree_events.append({"event": "leaf", "node": node})

        context["normalized_nodes"] = normalized_nodes
        context["tree_events"] = tree_events
        context["has_nodes"] = bool(normalized_nodes)
        context["aria_label"] = self.aria_label or DEFAULT_ARIA_LABEL
        return context
