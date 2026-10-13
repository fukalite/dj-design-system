import html
from typing import TYPE_CHECKING, Optional

from django.template import Context, Template
from django.templatetags.static import static
from django.utils.html import format_html, format_html_join

from dj_design_system.constants import BUILTIN_APP_LABEL, BUILTIN_GALLERY_CSS
from dj_design_system.services import media as media_service
from dj_design_system.services.registry import component_registry
from dj_design_system.settings import (
    dds_settings,
    get_app_html_attrs,
    get_app_static,
    get_backgrounds,
    get_default_background,
)
from dj_design_system.types import ColorScheme, Theme


if TYPE_CHECKING:
    from dj_design_system.services.registry import ComponentRegistry


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
    all_hrefs = media_service.get_bundle_urls(
        dds_settings.GLOBAL_CSS_BUNDLES, "css"
    ) + [media_service.resolve_asset_url(path=path) for path in dds_settings.GLOBAL_CSS]
    return format_html_join(
        "", '<link rel="stylesheet" href="{}">', ((href,) for href in all_hrefs)
    )


def global_js_urls() -> list[str]:
    """Return the URLs of the global JS (webpack bundles + static)."""
    return media_service.get_bundle_urls(dds_settings.GLOBAL_JS_BUNDLES, "js") + [
        media_service.resolve_asset_url(path=path) for path in dds_settings.GLOBAL_JS
    ]


def build_global_js_tags() -> str:
    """Build ``<script>`` tags for global JS (webpack bundles + static)."""
    return format_html_join(
        "", '<script src="{}"></script>', ((src,) for src in global_js_urls())
    )


def build_theme_app_media(
    theme_dict: Optional[Theme],
    app_label: Optional[str],
    color_scheme: ColorScheme = ColorScheme.LIGHT,
) -> tuple[str, str]:
    """Build CSS and JS tags for the specified theme and app."""
    theme_css = list(theme_dict.css) if theme_dict else []
    theme_js = list(theme_dict.js) if theme_dict else []
    theme_css_bundles = (
        media_service.get_bundle_urls(theme_dict.css_bundles, "css")
        if theme_dict
        else []
    )
    theme_js_bundles = (
        media_service.get_bundle_urls(theme_dict.js_bundles, "js") if theme_dict else []
    )

    if (
        color_scheme == ColorScheme.DARK
        and theme_dict
        and theme_dict.supports_dark_mode
        and theme_dict.dark_mode
    ):
        theme_css.extend(theme_dict.dark_mode.css)
        theme_js.extend(theme_dict.dark_mode.js)
        theme_css_bundles.extend(
            media_service.get_bundle_urls(theme_dict.dark_mode.css_bundles, "css")
        )
        theme_js_bundles.extend(
            media_service.get_bundle_urls(theme_dict.dark_mode.js_bundles, "js")
        )

    app_css: list[str] = []
    app_js: list[str] = []
    app_css_bundles: list[str] = []
    app_js_bundles: list[str] = []
    if app_label:
        app_css, app_js = get_app_static(app_label)
        app_css_bundles = media_service.get_bundle_urls(
            dds_settings.APP_CSS_BUNDLES.get(app_label, []), "css"
        )
        app_js_bundles = media_service.get_bundle_urls(
            dds_settings.APP_JS_BUNDLES.get(app_label, []), "js"
        )

    theme_css_urls = theme_css_bundles + [
        media_service.resolve_asset_url(path=p) for p in theme_css
    ]
    app_css_urls = app_css_bundles + [
        media_service.resolve_asset_url(path=p) for p in app_css
    ]
    css_urls = list(dict.fromkeys(theme_css_urls + app_css_urls))

    theme_js_urls = theme_js_bundles + [
        media_service.resolve_asset_url(path=p) for p in theme_js
    ]
    app_js_urls = app_js_bundles + [
        media_service.resolve_asset_url(path=p) for p in app_js
    ]
    js_urls = list(dict.fromkeys(theme_js_urls + app_js_urls))

    theme_app_css_tags = format_html_join(
        "", '<link rel="stylesheet" href="{}">', ((u,) for u in css_urls)
    )
    theme_app_js_tags = format_html_join(
        "", '<script src="{}"></script>', ((u,) for u in js_urls)
    )
    return theme_app_css_tags, theme_app_js_tags


def build_markdown_canvas_media(
    *,
    app_label: str = "",
    registry: Optional["ComponentRegistry"] = None,
) -> tuple[str, str]:
    """Build component CSS and JS tags for markdown canvas previews.

    Aggregates merged public component media with built-in component media
    and gallery styling when previewing built-in framework components.
    """
    reg = registry if registry is not None else component_registry
    media = reg.get_merged_media()
    css_paths = list(media.css)
    js_paths = list(media.js)
    if app_label == BUILTIN_APP_LABEL:
        builtin_media = reg.get_builtin_media()
        css_paths = list(
            dict.fromkeys(
                [
                    BUILTIN_GALLERY_CSS,
                    *builtin_media.css,
                    *css_paths,
                ]
            )
        )
        js_paths = list(dict.fromkeys([*builtin_media.js, *js_paths]))
    return (
        media_service.build_link_tags(css_paths),
        media_service.build_script_tags(js_paths),
    )


def build_canvas_bg_styles(
    *,
    theme_dict: Optional[Theme] = None,
    csp_nonce: Optional[str] = None,
) -> str:
    """Generate ``<style>`` CSS rules for all configured canvas backgrounds.

    Args:
        theme_dict: Optional active theme containing custom canvas background rules.
        csp_nonce: Optional CSP nonce string for the ``<style>`` tag.

    Returns:
        A ``<style>`` HTML string defining background colour rules.
    """
    rules = []
    for bg in get_backgrounds():
        rules.append(
            f".canvas-bg-{bg['value']}, body:has(.canvas-bg-{bg['value']}) {{ background: {bg['color']}; }}"
        )

    if theme_dict and isinstance(theme_dict.canvas_background, dict):
        bg = theme_dict.canvas_background
        if "color" in bg:
            rules.append(
                f".canvas-bg-theme-{theme_dict.value}, body:has(.canvas-bg-theme-{theme_dict.value}) {{ background: {bg['color']}; }}"
            )

    if (
        theme_dict
        and theme_dict.supports_dark_mode
        and theme_dict.dark_mode
        and isinstance(theme_dict.dark_mode.canvas_background, dict)
    ):
        bg_dark = theme_dict.dark_mode.canvas_background
        if "color" in bg_dark:
            rules.append(
                f".canvas-bg-theme-{theme_dict.value}-dark, body:has(.canvas-bg-theme-{theme_dict.value}-dark) {{ background: {bg_dark['color']}; }}"
            )

    nonce_attr = ""
    if csp_nonce:
        nonce_attr = f' nonce="{html.escape(str(csp_nonce))}"'

    return f"<style{nonce_attr}>\n" + "\n".join(rules) + "\n</style>"


def build_resize_script(iframe_id: str = "") -> str:
    """Build the ResizeObserver script used by auto-height iframes."""
    id_field = f'id:"{iframe_id}",' if iframe_id else ""
    return (
        "<script>"
        "(function(){"
        'const w=document.querySelector(".canvas-wrapper");'
        "if(!w||!window.parent||window.parent===window)return;"
        "new ResizeObserver(function(){"
        "window.parent.postMessage({"
        f'type:"canvas-resize",{id_field}height:Math.max(w.scrollHeight,w.offsetHeight)'
        '},"*");'
        "}).observe(w);"
        "})();"
        "</script>"
    )


def _flatten_attrs(attrs: dict[str, str]) -> str:
    """Convert a dict of HTML attributes to a safe attribute string with leading space."""
    if not attrs:
        return ""
    parts = format_html_join(" ", '{}="{}"', attrs.items())
    return format_html(" {}", parts)


def build_html_attrs(
    theme_dict: Optional[Theme] = None,
    app_label: Optional[str] = None,
    color_scheme: ColorScheme = ColorScheme.LIGHT,
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
        if (
            color_scheme == ColorScheme.DARK
            and theme_dict.supports_dark_mode
            and theme_dict.dark_mode
        ):
            html_dict.update(theme_dict.dark_mode.html_attrs.get("html", {}))
            body_dict.update(theme_dict.dark_mode.html_attrs.get("body", {}))
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
    color_scheme: ColorScheme = ColorScheme.LIGHT,
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
        color_scheme: Active ColorScheme for theme styling and media.
    """
    global_css = build_global_css_tags()
    global_js = build_global_js_tags()
    canvas_css_tag = (
        f'<link rel="stylesheet" href="{static("dj_design_system/canvas.css")}">'
    )

    basic_mode_css = ""
    if mode_class == "canvas-wrapper--basic":
        basic_mode_css = (
            "<style>"
            "html, body { min-height: 0 !important; height: auto !important; overflow: hidden !important; }"
            "</style>"
        )

    if bg_class is None:
        if (
            color_scheme == ColorScheme.DARK
            and theme_dict
            and theme_dict.supports_dark_mode
            and theme_dict.dark_mode
            and theme_dict.dark_mode.canvas_background
        ):
            if isinstance(theme_dict.dark_mode.canvas_background, str):
                bg_class = f"canvas-bg-{theme_dict.dark_mode.canvas_background}"
            elif isinstance(theme_dict.dark_mode.canvas_background, dict):
                bg_class = f"canvas-bg-theme-{theme_dict.value}-dark"
        elif theme_dict and theme_dict.canvas_background:
            if isinstance(theme_dict.canvas_background, str):
                bg_class = f"canvas-bg-{theme_dict.canvas_background}"
            elif isinstance(theme_dict.canvas_background, dict):
                bg_class = f"canvas-bg-theme-{theme_dict.value}"
        else:
            bg_class = f"canvas-bg-{get_default_background()['value']}"

    theme_app_css_tags, theme_app_js_tags = build_theme_app_media(
        theme_dict, app_label, color_scheme=color_scheme
    )
    bg_styles = build_canvas_bg_styles(theme_dict=theme_dict)
    resize_script = build_resize_script(iframe_id=iframe_id)
    html_attrs_str, body_attrs_str = build_html_attrs(
        theme_dict, app_label, color_scheme=color_scheme
    )

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
        f"{global_js}"
        f"{component_js}"
        f"{theme_app_js_tags}"
        f"{resize_script}"
        "</body>"
        "</html>"
    )

    return iframe_doc
