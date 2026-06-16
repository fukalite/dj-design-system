"""Template tags and filters for the gallery UI."""

from __future__ import annotations

import html

from django import template

from dj_design_system.services.canvas_renderer import build_canvas_srcdoc
from dj_design_system.settings import get_default_theme, get_theme
from dj_design_system.types import Theme


register = template.Library()

BASE_INDENT_PX = 0
INDENT_PER_LEVEL_PX = 16


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
