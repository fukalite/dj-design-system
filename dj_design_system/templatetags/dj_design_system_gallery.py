"""Template tags and filters for the gallery UI."""

from __future__ import annotations

import html

from django import template
from django.templatetags.static import static

from dj_design_system.services.media import get_bundle_urls
from dj_design_system.settings import (
    dds_settings,
    get_app_html_attrs,
    get_app_static,
    get_backgrounds,
    get_default_background,
    get_default_theme,
    get_theme,
)
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
            theme_val = get_default_theme()["value"]
        return get_theme(theme_val)

    def _build_theme_app_media(
        self, theme_dict: Theme | None, app_label: str | None
    ) -> tuple[str, str]:
        theme_css = theme_dict["css"] if theme_dict else []
        theme_js = theme_dict["js"] if theme_dict else []
        theme_css_bundles = (
            get_bundle_urls(theme_dict.get("css_bundles", []), "css")
            if theme_dict
            else []
        )
        theme_js_bundles = (
            get_bundle_urls(theme_dict.get("js_bundles", []), "js")
            if theme_dict
            else []
        )

        app_css: list[str] = []
        app_js: list[str] = []
        app_css_bundles: list[str] = []
        app_js_bundles: list[str] = []
        if app_label:
            app_css, app_js = get_app_static(app_label)
            app_css_bundles = get_bundle_urls(
                dds_settings.APP_CSS_BUNDLES.get(app_label, []), "css"
            )
            app_js_bundles = get_bundle_urls(
                dds_settings.APP_JS_BUNDLES.get(app_label, []), "js"
            )

        theme_css_urls = theme_css_bundles + [static(p) for p in theme_css]
        app_css_urls = app_css_bundles + [static(p) for p in app_css]
        css_urls = list(dict.fromkeys(theme_css_urls + app_css_urls))

        theme_js_urls = theme_js_bundles + [static(p) for p in theme_js]
        app_js_urls = app_js_bundles + [static(p) for p in app_js]
        js_urls = list(dict.fromkeys(theme_js_urls + app_js_urls))

        theme_app_css_tags = "".join(
            f'<link rel="stylesheet" href="{u}">' for u in css_urls
        )
        theme_app_js_tags = "".join(f'<script src="{u}"></script>' for u in js_urls)
        return theme_app_css_tags, theme_app_js_tags

    def _build_bg_styles(self) -> str:
        bg_rules = "".join(
            f".canvas-bg-{bg['value']}{{background:{bg['color']};}}"
            for bg in get_backgrounds()
        )
        return f"<style>{bg_rules}</style>"

    def _build_resize_script(self) -> str:
        return (
            "<script>"
            "(function(){"
            'var w=document.querySelector(".canvas-wrapper");'
            "if(!w||!window.parent||window.parent===window)return;"
            "new ResizeObserver(function(){"
            "window.parent.postMessage("
            '{type:"canvas-resize",height:document.documentElement.scrollHeight},"*");'
            "}).observe(w);"
            "})();"
            "</script>"
        )

    def render(self, context: template.Context) -> str:
        rendered_component = self.nodelist.render(context)
        global_css = self._global_css_tags()
        canvas_css_tag = (
            f'<link rel="stylesheet" href="{static("dj_design_system/canvas.css")}">'
        )

        component_css = context.get("_canvas_component_css", "")
        component_js = context.get("_canvas_component_js", "")

        bg_class = context.get(
            "_canvas_bg_class",
            f"canvas-bg-{get_default_background()['value']}",
        )
        mode_class = context.get("_canvas_mode_class", "canvas-wrapper--basic")

        theme_dict = self._resolve_theme(context)
        component_info = context.get("component_info")
        app_label = component_info.app_label if component_info else None

        theme_app_css_tags, theme_app_js_tags = self._build_theme_app_media(
            theme_dict, app_label
        )
        bg_styles = self._build_bg_styles()
        resize_script = self._build_resize_script()

        iframe_doc = (
            "<!DOCTYPE html>"
            f'<html lang="en"{self._html_attrs(theme_dict, app_label)}>'
            "<head>"
            '<meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f"{global_css}"
            f"{canvas_css_tag}"
            f"{theme_app_css_tags}"
            f"{component_css}"
            f"{bg_styles}"
            "</head>"
            f"<body{self._body_attrs(theme_dict, app_label)}>"
            f'<div class="canvas-wrapper {mode_class} {bg_class}">'
            f"{rendered_component}"
            "</div>"
            f"{component_js}"
            f"{theme_app_js_tags}"
            f"{resize_script}"
            "</body>"
            "</html>"
        )

        escaped_doc = html.escape(iframe_doc)
        return (
            f'<iframe class="gallery-canvas" srcdoc="{escaped_doc}" '
            f'title="Component preview"></iframe>'
        )

    def _global_css_tags(self) -> str:
        """Build ``<link>`` tags for global CSS (webpack bundles + static)."""
        all_hrefs = [
            url for url in get_bundle_urls(dds_settings.GLOBAL_CSS_BUNDLES, "css")
        ] + [static(path) for path in dds_settings.GLOBAL_CSS]
        return "".join(f'<link rel="stylesheet" href="{href}">' for href in all_hrefs)

    @staticmethod
    def _flatten_attrs(attrs: dict[str, str]) -> str:
        """Convert a dict to an HTML attribute string with leading space."""
        if not attrs:
            return ""
        return " " + " ".join(f'{k}="{html.escape(v)}"' for k, v in attrs.items())

    def _html_attrs(self, theme_dict=None, app_label=None) -> str:
        raw = dds_settings.GALLERY_CANVAS_HTML_ATTRS
        html_dict = dict(raw.get("html", {}))
        if theme_dict:
            html_dict.update(theme_dict.get("html_attrs", {}).get("html", {}))
        if app_label:
            html_dict.update(get_app_html_attrs(app_label).get("html", {}))
        return self._flatten_attrs(html_dict)

    def _body_attrs(self, theme_dict=None, app_label=None) -> str:
        raw = dds_settings.GALLERY_CANVAS_HTML_ATTRS
        body_dict = dict(raw.get("body", {}))
        if theme_dict:
            body_dict.update(theme_dict.get("html_attrs", {}).get("body", {}))
        if app_label:
            body_dict.update(get_app_html_attrs(app_label).get("body", {}))
        return self._flatten_attrs(body_dict)


@register.tag("canvas")
def do_canvas(parser: template.Parser, token: template.Token) -> CanvasNode:
    """Render the enclosed component tag(s) inside an isolated iframe."""
    nodelist = parser.parse(("endcanvas",))
    parser.delete_first_token()
    return CanvasNode(nodelist)
