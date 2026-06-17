import html
from typing import Optional

from django.template import Context, Template
from django.templatetags.static import static

from dj_design_system.services.media import get_bundle_urls
from dj_design_system.settings import (
    dds_settings,
    get_app_html_attrs,
    get_app_static,
    get_backgrounds,
    get_default_background,
)
from dj_design_system.types import Theme


def render_canvas_block(source: str) -> str:
    """Render canvas block content through the Django template engine.

    Wraps the source in {% load design_components %} and renders it
    using Django's Template + Context. Returns the rendered HTML fragment.
    """
    template_str = "{% load design_components %}\n" + source
    tmpl = Template(template_str)
    return tmpl.render(Context())


def build_global_css_tags() -> str:
    """Build ``<link>`` tags for global CSS (webpack bundles + static)."""
    all_hrefs = [
        url for url in get_bundle_urls(dds_settings.GLOBAL_CSS_BUNDLES, "css")
    ] + [static(path) for path in dds_settings.GLOBAL_CSS]
    return "".join(f'<link rel="stylesheet" href="{href}">' for href in all_hrefs)


def build_theme_app_media(
    theme_dict: Optional[Theme], app_label: Optional[str]
) -> tuple[str, str]:
    """Build CSS and JS tags for the specified theme and app."""
    theme_css = theme_dict.css if theme_dict else []
    theme_js = theme_dict.js if theme_dict else []
    theme_css_bundles = (
        get_bundle_urls(theme_dict.css_bundles, "css") if theme_dict else []
    )
    theme_js_bundles = (
        get_bundle_urls(theme_dict.js_bundles, "js") if theme_dict else []
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


def build_bg_styles() -> str:
    """Build CSS rules for all configured canvas backgrounds."""
    bg_rules = "".join(
        f".canvas-bg-{bg['value']}{{background:{bg['color']};}}"
        for bg in get_backgrounds()
    )
    return f"<style>{bg_rules}</style>"


def build_resize_script(iframe_id: str = "") -> str:
    """Build the ResizeObserver script used by auto-height iframes."""
    id_field = f'id:"{iframe_id}",' if iframe_id else ""
    return (
        "<script>"
        "(function(){"
        'var w=document.querySelector(".canvas-wrapper");'
        "if(!w||!window.parent||window.parent===window)return;"
        "new ResizeObserver(function(){"
        "window.parent.postMessage({"
        f'type:"canvas-resize",{id_field}height:document.documentElement.scrollHeight'
        '},"*");'
        "}).observe(w);"
        "})();"
        "</script>"
    )


def _flatten_attrs(attrs: dict[str, str]) -> str:
    """Convert a dict to an HTML attribute string with leading space."""
    if not attrs:
        return ""
    return " " + " ".join(f'{k}="{html.escape(v)}"' for k, v in attrs.items())


def build_html_attrs(
    theme_dict: Optional[Theme] = None, app_label: Optional[str] = None
) -> tuple[str, str]:
    """Build the HTML and BODY attributes for the canvas document.

    Returns a tuple of (html_attrs_str, body_attrs_str).
    """
    raw = dds_settings.GALLERY_CANVAS_HTML_ATTRS
    html_dict = dict(raw.get("html", {}))
    body_dict = dict(raw.get("body", {}))

    if theme_dict:
        html_dict.update(theme_dict.html_attrs.get("html", {}))
        body_dict.update(theme_dict.html_attrs.get("body", {}))
    if app_label:
        html_dict.update(get_app_html_attrs(app_label).get("html", {}))
        body_dict.update(get_app_html_attrs(app_label).get("body", {}))

    return _flatten_attrs(html_dict), _flatten_attrs(body_dict)


def build_canvas_srcdoc(
    rendered_html: str,
    component_css: str = "",
    component_js: str = "",
    theme_dict: Optional[Theme] = None,
    app_label: Optional[str] = None,
    bg_class: Optional[str] = None,
    mode_class: str = "canvas-wrapper--basic",
    iframe_id: str = "",
) -> str:
    """Build a full HTML document for srcdoc embedding.

    Args:
        rendered_html: The HTML content to place inside the canvas wrapper.
        component_css: Any component-specific <link> tags.
        component_js: Any component-specific <script> tags.
        theme_dict: Optional theme dictionary.
        app_label: Optional app label.
        bg_class: Optional background CSS class. Defaults to the configured default.
        mode_class: The canvas mode class (e.g. 'canvas-wrapper--basic').
        iframe_id: Optional ID to uniquely identify this canvas instance for resize events.
    """
    global_css = build_global_css_tags()
    canvas_css_tag = (
        f'<link rel="stylesheet" href="{static("dj_design_system/canvas.css")}">'
    )

    basic_mode_css = ""
    if mode_class == "canvas-wrapper--basic":
        basic_mode_css = (
            "<style>"
            "html, body { min-height: 0 !important; height: auto !important; overflow: hidden !important; }"
            ".canvas-wrapper--basic { display: flex !important; justify-content: center !important; align-items: center !important; }"
            "</style>"
        )

    if bg_class is None:
        bg_class = f"canvas-bg-{get_default_background()['value']}"

    theme_app_css_tags, theme_app_js_tags = build_theme_app_media(theme_dict, app_label)
    bg_styles = build_bg_styles()
    resize_script = build_resize_script(iframe_id=iframe_id)
    html_attrs_str, body_attrs_str = build_html_attrs(theme_dict, app_label)

    iframe_doc = (
        "<!DOCTYPE html>"
        f'<html lang="en"{html_attrs_str}>'
        "<head>"
        '<meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"{global_css}"
        f"{canvas_css_tag}"
        f"{theme_app_css_tags}"
        f"{component_css}"
        f"{basic_mode_css}"
        f"{bg_styles}"
        "</head>"
        f"<body{body_attrs_str}>"
        f'<div class="canvas-wrapper {mode_class} {bg_class}">'
        f"{rendered_html}"
        "</div>"
        f"{component_js}"
        f"{theme_app_js_tags}"
        f"{resize_script}"
        "</body>"
        "</html>"
    )

    return iframe_doc
