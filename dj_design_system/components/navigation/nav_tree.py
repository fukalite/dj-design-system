from typing import Any

from dj_design_system.components import TagComponent
from dj_design_system.components.navigation.nodes import normalise
from dj_design_system.components.primitives.icon import Icon
from dj_design_system.parameters import ListParam, StrParam
from dj_design_system.services.media import FOUNDATION_CSS


def _icon(name: str) -> str:
    return Icon(
        name=name, extra_classes=f"gallery-nav__icon gallery-nav__icon--{name}"
    ).render()


class NavTree(TagComponent):
    """The sidebar's navigation: app groups, collapsible folders and page links.

    Pass the gallery's navigation tree (``NavNode`` objects, or dicts with
    ``type``, ``label``, ``url``, ``active_path`` and ``children``) and the
    current ``active_path``. Folders on the active path start open, and the
    current page is highlighted. Folders are native ``<details>`` elements,
    so they work without JavaScript.

    Example usage::

        {% dds__navigation__nav_tree nav_tree active_path=active_path %}
    """

    template_name = "dj_design_system/ui/navigation/nav_tree.html"

    nodes = ListParam("Top-level nodes, one per app.")
    active_path = StrParam("The current page's path within its app.", required=False)

    class Meta:
        positional_args = ["nodes"]

    class Media:
        # icon.css first: the nav's own icon rules refine the Icon defaults.
        css = [
            FOUNDATION_CSS,
            "dj_design_system/ui/primitives/icon.css",
            "dj_design_system/ui/navigation/nav_tree.css",
        ]

    def _prepare(self, node: dict[str, Any], depth: int) -> dict[str, Any]:
        active_path = self.active_path or ""
        children = node["children"]
        child_depth = 1 if node["type"] == "app" else depth + 1
        prepared = {
            **node,
            "depth": depth,
            "is_app": node["type"] == "app",
            "has_children": bool(children),
            "is_active": active_path == node["active_path"],
            "is_open": bool(active_path) and node["active_path"] in active_path,
            "children": [self._prepare(child, child_depth) for child in children],
        }
        if prepared["has_children"]:
            prepared["icon"] = _icon(
                "component" if node["type"] == "component" else "folder"
            )
        elif node["type"] in ("component", "document"):
            prepared["icon"] = _icon(
                "component" if node["type"] == "component" else "doc"
            )
        return prepared

    def get_context(self):
        context = super().get_context()
        context["tree"] = [
            self._prepare(normalise(node), depth=0) for node in self.nodes or []
        ]
        return context
