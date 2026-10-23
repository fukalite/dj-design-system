"""Template tags and filters for the gallery UI."""

from __future__ import annotations

import html

from django import template
from django.utils.html import json_script

from dj_design_system.data import NavNode
from dj_design_system.gallery import Variant
from dj_design_system.services import media as media_service
from dj_design_system.services import navigation as navigation_service
from dj_design_system.services.canvas_renderer import build_canvas_srcdoc
from dj_design_system.services.control_params import (
    SANDBOX_SUBMISSION_PARAM,
    get_control_param,
)
from dj_design_system.services.registry import component_registry
from dj_design_system.settings import dds_settings, get_default_theme, get_theme
from dj_design_system.types import Theme


register = template.Library()

BASE_INDENT_PX = 0
INDENT_PER_LEVEL_PX = 16


@register.simple_tag
def builtin_component_stylesheets() -> str:
    """Output ``<link>`` tags for all built-in ``dds`` component stylesheets."""
    media = component_registry.get_builtin_media()
    return media_service.build_link_tags(css_paths=media.css)


@register.simple_tag
def gallery_extra_stylesheets() -> str:
    """Output ``<link>`` tags for user-configured gallery extra stylesheets."""
    extra_paths = dds_settings.GALLERY_EXTRA_CSS or []
    return media_service.build_link_tags(css_paths=extra_paths)


@register.simple_tag(takes_context=True)
def gallery_ui_theme_stylesheets(
    context: template.Context | dict | None = None,
) -> str:
    """Output ``<link>`` tags for active gallery UI theme stylesheets."""
    if not context:
        return ""
    active_ui_theme = context.get("active_ui_theme")
    if not active_ui_theme or not isinstance(active_ui_theme, Theme):
        return ""
    css_paths = list(active_ui_theme.css)
    bundles = list(active_ui_theme.css_bundles)
    gallery_theme = context.get("gallery_theme")
    if (
        gallery_theme == "dark"
        and active_ui_theme.supports_dark_mode
        and active_ui_theme.dark_mode
    ):
        css_paths.extend(active_ui_theme.dark_mode.css)
        bundles.extend(active_ui_theme.dark_mode.css_bundles)

    bundle_urls = media_service.get_bundle_urls(bundles, "css")
    all_css = bundle_urls + css_paths
    return media_service.build_link_tags(css_paths=all_css)


@register.simple_tag(takes_context=True)
def gallery_ui_theme_scripts(
    context: template.Context | dict | None = None,
) -> str:
    """Output ``<script>`` tags for active gallery UI theme scripts."""
    if not context:
        return ""
    active_ui_theme = context.get("active_ui_theme")
    if not active_ui_theme or not isinstance(active_ui_theme, Theme):
        return ""
    js_paths = list(active_ui_theme.js)
    bundles = list(active_ui_theme.js_bundles)
    gallery_theme = context.get("gallery_theme")
    if (
        gallery_theme == "dark"
        and active_ui_theme.supports_dark_mode
        and active_ui_theme.dark_mode
    ):
        js_paths.extend(active_ui_theme.dark_mode.js)
        bundles.extend(active_ui_theme.dark_mode.js_bundles)

    bundle_urls = media_service.get_bundle_urls(bundles, "js")
    all_js = bundle_urls + js_paths
    request = (
        context.get("request")
        if isinstance(context, dict) or hasattr(context, "get")
        else None
    )
    nonce = getattr(request, "csp_nonce", None) if request else None
    return media_service.build_script_tags(all_js, nonce=nonce)


@register.simple_tag(takes_context=True)
def builtin_component_scripts(
    context: template.Context | dict | None = None,
) -> str:
    """Output ``<script type="module">`` tags for all built-in ``dds`` component scripts."""
    media = component_registry.get_builtin_media()
    request = context.get("request") if context else None
    nonce = getattr(request, "csp_nonce", None) if request else None
    return media_service.build_script_tags(media.js, nonce=nonce, is_module=True)


@register.simple_tag(takes_context=True)
def gallery_search_index_script(
    context: template.Context | dict | None = None,
) -> str:
    """Output a ``<script id="gallery-search-index" type="application/json">`` tag."""
    search_index = context.get("search_index", []) if context else []
    return json_script(search_index, "gallery-search-index")


@register.filter
def add_indent(depth: int) -> int:
    """Convert a tree depth to a left-padding value in pixels."""
    try:
        depth = int(depth)
    except (TypeError, ValueError):
        depth = 0
    return BASE_INDENT_PX + (depth * INDENT_PER_LEVEL_PX)


@register.simple_tag
def nav_link_is_active(
    node: NavNode, active_path: str, active_variant: Variant | str | None
) -> bool:
    """Return whether a leaf nav link is the current page.

    ``active_variant`` is either a ``Variant`` (component pages) or a plain
    slug string (raw ``?variant=`` query value); both are accepted.
    """
    if not node.is_variant:
        return active_path == node.active_path and not active_variant
    if active_path != node.base_active_path:
        return False
    active_slug = getattr(active_variant, "name", active_variant)
    return active_slug == node.slug


@register.simple_tag
def nav_folder_is_open(node: NavNode, active_path: str) -> bool:
    """Return whether a folder nav node is expanded on initial render.

    Args:
        node: The folder or expandable navigation node to check.
        active_path: The active gallery route path for the current request.

    Returns:
        True when the current page is the folder itself or one of its descendants.
    """
    return navigation_service.is_nav_folder_open(node=node, active_path=active_path)


class CanvasNode(template.Node):
    """Render children inside an ``<iframe srcdoc="...">``."""

    def __init__(self, nodelist: template.NodeList):
        self.nodelist = nodelist

    def _resolve_theme(self, context: template.Context) -> Theme | None:
        theme_val = context.get("active_theme")
        if not theme_val:
            request = context.get("request")
            if request:
                theme_val = get_control_param(
                    request.GET,
                    "theme",
                    bare_fallback=SANDBOX_SUBMISSION_PARAM not in request.GET,
                )
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
