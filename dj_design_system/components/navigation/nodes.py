"""Normalise navigation nodes for the navigation components.

The components accept real :class:`~dj_design_system.data.NavNode` objects
(as the gallery passes them) or plain dicts with the same information (as
gallery examples pass them through the sandbox)::

    {"type": "app" | "folder" | "component" | "document",
     "label": "Cards", "url": "/dds/demo/cards/", "active_path": "cards",
     "children": [...]}
"""

from typing import Any

from dj_design_system.data import NavNode


def normalise(node: Any) -> dict[str, Any]:
    """Return ``node`` as a plain dict with ``type``, ``label``, ``url``,
    ``active_path`` and ``children`` (normalised recursively)."""
    if isinstance(node, NavNode):
        return {
            "type": node.node_type.value,
            "label": node.label,
            "url": node.url,
            "active_path": node.active_path,
            "children": [normalise(child) for child in node.children],
        }
    return {
        "type": node.get("type", "folder"),
        "label": node.get("label", ""),
        "url": node.get("url", ""),
        "active_path": node.get("active_path", ""),
        "children": [normalise(child) for child in node.get("children") or []],
    }
