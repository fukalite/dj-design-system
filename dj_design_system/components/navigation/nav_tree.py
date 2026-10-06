from typing import Any

from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe

from dj_design_system.components import TagComponent
from dj_design_system.components.navigation.nodes import normalise
from dj_design_system.components.primitives.icon import Icon
from dj_design_system.gallery import Variant
from dj_design_system.parameters import ListParam, StrParam
from dj_design_system.parameters.base import BaseParam
from dj_design_system.services.media import FOUNDATION_CSS


class _ActiveVariantParam(BaseParam):
    """The current variant: its name, or the ``Variant`` a component page has."""

    type = (str, Variant)


def _icon(name: str) -> str:
    return Icon(
        name=name, extra_classes=f"gallery-nav__icon gallery-nav__icon--{name}"
    ).render()


def _custom_icon(icon: str) -> str:
    """A node's own icon: inline SVG markup, an image URL or a CSS class."""
    if "<svg" in icon:
        return format_html(
            '<span class="gallery-nav__icon gallery-nav__icon--custom"'
            ' aria-hidden="true">{}</span>',
            mark_safe(icon),  # noqa: S308 - set by the component's gallery config
        )
    if "/" in icon or ".svg" in icon or "data:" in icon:
        return format_html(
            '<span class="gallery-nav__icon gallery-nav__icon--custom"'
            " style=\"-webkit-mask-image: url('{}'); mask-image: url('{}')\""
            ' aria-hidden="true"></span>',
            icon,
            icon,
        )
    return format_html(
        '<span class="gallery-nav__icon gallery-nav__icon--custom {}"'
        ' aria-hidden="true"></span>',
        icon,
    )


class NavTree(TagComponent):
    """The sidebar's navigation: app groups, collapsible folders and page links.

    Pass the gallery's navigation tree (``NavNode`` objects, or dicts with
    ``type``, ``label``, ``url``, ``active_path`` and ``children``), the
    current ``active_path`` and, on a variant's page, the ``active_variant``.
    Folders on the active path start open, and the current page is
    highlighted. Folders are native ``<details>`` elements, so they work
    without JavaScript.

    Example usage::

        {% dds__navigation__nav_tree nav_tree active_path=active_path active_variant=active_variant %}
    """

    template_name = "dj_design_system/ui/navigation/nav_tree.html"

    nodes = ListParam("Top-level nodes, one per app.")
    active_path = StrParam("The current page's path within its app.", required=False)
    active_variant = _ActiveVariantParam(
        "The current variant's name, on a variant's page.", required=False
    )

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
        active_variant = self.active_variant
        children = node["children"]
        child_depth = 1 if node["type"] == "app" else depth + 1
        is_variant = node["type"] == "variant"
        has_children = bool(children)
        if node["type"] == "app":
            is_active = active_path == node["active_path"]
        elif has_children:
            is_active = active_path == node["active_path"] and not active_variant
        elif is_variant:
            # A component page passes a Variant, which never equals a slug
            # string, so variant links are only active given a name.
            is_active = (
                active_path == node["base_active_path"]
                and active_variant == node["slug"]
            )
        else:
            is_active = active_path == node["active_path"] and not active_variant
        prepared = {
            **node,
            "depth": depth,
            "is_app": node["type"] == "app",
            "is_variant": is_variant,
            "has_children": has_children,
            "is_active": is_active,
            "is_open": bool(active_path)
            and (
                node["active_path"] in active_path
                or node["base_active_path"] in active_path
            ),
            "children": [self._prepare(child, child_depth) for child in children],
            "icon": self._icon_for(node, has_children),
        }
        return prepared

    @staticmethod
    def _icon_for(node: dict[str, Any], has_children: bool) -> str:
        if node["icon"]:
            return _custom_icon(node["icon"])
        if node["type"] == "component":
            return _icon("component-variants" if has_children else "component")
        if node["type"] == "document":
            return _icon("doc")
        if node["type"] == "variant":
            return _icon("variant")
        if has_children:
            return _icon("folder")
        return ""

    def get_context(self):
        context = super().get_context()
        context["tree"] = [
            self._prepare(normalise(node), depth=0) for node in self.nodes or []
        ]
        return context

    def render_node(self, node: Any, depth: int = 0) -> SafeString:
        """Render one node and its descendants, without the ``<nav>`` around them.

        For the legacy ``gallery/navtree.html`` partial, which renders a single
        node inside a ``<nav>`` of the caller's own.
        """
        return render_to_string(
            "dj_design_system/ui/navigation/nav_node.html",
            {"node": self._prepare(normalise(node), depth=depth)},
        )
