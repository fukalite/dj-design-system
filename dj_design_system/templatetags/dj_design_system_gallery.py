"""Template tags and filters for the gallery UI."""

from __future__ import annotations

import html

from django import template
from django.utils.html import strip_tags

from dj_design_system.services.canvas_renderer import build_canvas_srcdoc
from dj_design_system.services.media import (
    build_link_tags,
    build_script_tags,
    get_gallery_media,
)
from dj_design_system.settings import get_default_theme, get_theme
from dj_design_system.types import Theme


register = template.Library()

BASE_INDENT_PX = 0
INDENT_PER_LEVEL_PX = 16


@register.simple_tag
def gallery_stylesheets() -> str:
    """Render ``<link>`` tags for ``foundation.css`` and internal component CSS."""
    return build_link_tags(get_gallery_media().css)


@register.simple_tag(takes_context=True)
def gallery_scripts(context: template.Context) -> str:
    """Render ``<script>`` tags for internal component JS, with any CSP nonce."""
    request = context.get("request")
    nonce = getattr(request, "csp_nonce", None) if request else None
    return build_script_tags(get_gallery_media().js, nonce=nonce)


@register.simple_tag(takes_context=True)
def sandbox_toolbar_options(context: template.Context) -> dict:
    """The sandbox toolbar's popout options, for ``gallery/toolbar.html``.

    The component view provides them as ``toolbar_options``. Templates that
    include the toolbar with only ``canvas_backgrounds`` and
    ``active_bg_value`` get them built from those.
    """
    from dj_design_system.services.sandbox_toolbar import build_toolbar_options

    return context.get("toolbar_options") or build_toolbar_options(
        context.get("canvas_backgrounds"), context.get("active_bg_value")
    )


@register.simple_tag(takes_context=True)
def gallery_nav_node(context: template.Context, node, depth: int = 0) -> str:
    """Render one navigation node with ``NavTree``, for ``gallery/navtree.html``."""
    from dj_design_system.components.navigation.nav_tree import NavTree

    tree = NavTree(nodes=[node], active_path=context.get("active_path") or "")
    return tree.render_node(node, depth=int(depth))


@register.filter
def highlighted_code(markup: str) -> str:
    """Recover the code from syntax-highlighted (or escaped) HTML.

    For ``canvas_widget.html``, whose callers pass highlighted code but whose
    ``CanvasWidget`` takes raw code and highlights it itself.
    """
    return html.unescape(strip_tags(str(markup or "")))


@register.filter
def add_indent(depth: int) -> int:
    """Convert a tree depth to a left-padding value in pixels."""
    try:
        depth = int(depth)
    except (TypeError, ValueError):
        depth = 0
    return BASE_INDENT_PX + (depth * INDENT_PER_LEVEL_PX)


class CanvasNode(template.Node):
    """Render children inside an ``<iframe srcdoc="...">``."""

    def __init__(self, nodelist: template.NodeList):
        self.nodelist = nodelist

    def _resolve_theme(self, context: template.Context) -> Theme | None:
        theme_val = context.get("active_theme")
        if not theme_val:
            request = context.get("request")
            if request:
                theme_val = request.GET.get("theme")
        if not theme_val:
            theme_val = get_default_theme().value
        return get_theme(theme_val)

    def render(self, context: template.Context) -> str:
        rendered_component = self.nodelist.render(context)

        component_css = context.get("_canvas_component_css", "")
        component_js = context.get("_canvas_component_js", "")
        bg_class = context.get("_canvas_bg_class")
        mode_class = context.get("_canvas_mode_class", "canvas-wrapper--basic")

        theme_dict = self._resolve_theme(context)
        component_info = context.get("component_info")
        app_label = component_info.app_label if component_info else None

        iframe_doc = build_canvas_srcdoc(
            rendered_html=rendered_component,
            component_css=component_css,
            component_js=component_js,
            theme_dict=theme_dict,
            app_label=app_label,
            bg_class=bg_class,
            mode_class=mode_class,
        )

        escaped_doc = html.escape(iframe_doc)
        return (
            f'<iframe class="gallery-canvas" srcdoc="{escaped_doc}" '
            f'title="Component preview"></iframe>'
        )


@register.tag("canvas")
def do_canvas(parser: template.Parser, token: template.Token) -> CanvasNode:
    """Render the enclosed component tag(s) inside an isolated iframe."""
    nodelist = parser.parse(("endcanvas",))
    parser.delete_first_token()
    return CanvasNode(nodelist)
