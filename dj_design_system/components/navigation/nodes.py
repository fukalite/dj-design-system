"""Normalise navigation nodes for the navigation components.

The components accept real :class:`~dj_design_system.data.NavNode` objects
(as the gallery passes them) or plain dicts with the same information (as
gallery examples pass them through the sandbox)::

    {"type": "app" | "folder" | "component" | "document" | "variant",
     "label": "Cards", "url": "/dds/demo/cards/", "active_path": "cards",
     "children": [...]}

Variant nodes also carry ``slug`` and ``base_active_path`` (their
component's path), and any node can carry a custom ``icon``.
"""

from typing import Any

from dj_design_system.data import NavNode


def normalise(node: Any) -> dict[str, Any]:
    """Return ``node`` as a plain dict with ``type``, ``label``, ``slug``,
    ``url``, ``active_path``, ``base_active_path``, ``icon`` and ``children``
    (normalised recursively)."""
    if isinstance(node, NavNode):
        return {
            "type": node.node_type.value,
            "label": node.label,
            "slug": node.slug,
            "url": node.url,
            "active_path": node.active_path,
            "base_active_path": node.base_active_path,
            "icon": node.icon or "",
            "children": [normalise(child) for child in node.children],
        }
    return {
        "type": node.get("type", "folder"),
        "label": node.get("label", ""),
        "slug": node.get("slug", ""),
        "url": node.get("url", ""),
        "active_path": node.get("active_path", ""),
        "base_active_path": node.get("base_active_path", ""),
        "icon": node.get("icon") or "",
        "children": [normalise(child) for child in node.get("children") or []],
    }
