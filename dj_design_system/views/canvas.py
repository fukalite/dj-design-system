"""Canvas iframe rendering and styling views/helpers."""

import html

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.utils.html import format_html, format_html_join
from django.views.decorators.clickjacking import xframe_options_sameorigin

from dj_design_system.services.canvas import (
    get_component_media,
    render_component,
    resolve_component,
    resolve_from_get_params,
)
from dj_design_system.services.media import get_bundle_urls
from dj_design_system.services.registry import component_registry
from dj_design_system.settings import (
    dds_settings,
    get_app_html_attrs,
    get_app_static,
    get_backgrounds,
    get_default_background,
    get_default_theme,
    get_theme,
)
from dj_design_system.types import CanvasMode, Theme
from dj_design_system.views.decorators import gallery_access_required


def _canvas_mode_class(request: HttpRequest) -> str:
    """Return the CSS class for the canvas mode from GET params."""
    mode_param = request.GET.get("mode")
    if mode_param:
        try:
            mode = CanvasMode(mode_param)
        except ValueError:
            mode = CanvasMode.EXTENDED
    else:
        mode = CanvasMode.EXTENDED
    return f"canvas-wrapper--{mode.value}"


def _flatten_attrs(attrs: dict[str, str]) -> str:
    """Convert a dict of HTML attributes to a safe attribute string."""
    if not attrs:
        return ""
    parts = format_html_join(" ", '{}="{}"', attrs.items())
    return format_html(" {}", parts)


def _canvas_html_attrs(
    theme_dict: Theme | None = None, app_label: str | None = None
) -> tuple[str, str]:
    """Return ``(html_attrs, body_attrs)`` strings from settings, theme, and app."""
    raw = dds_settings.GALLERY_CANVAS_HTML_ATTRS
    html_dict = dict(raw.get("html", {}))
    body_dict = dict(raw.get("body", {}))

    if theme_dict:
        theme_raw = theme_dict.html_attrs
        html_dict.update(theme_raw.get("html", {}))
        body_dict.update(theme_raw.get("body", {}))

    if app_label:
        app_raw = get_app_html_attrs(app_label)
        html_dict.update(app_raw.get("html", {}))
        body_dict.update(app_raw.get("body", {}))

    return _flatten_attrs(html_dict), _flatten_attrs(body_dict)


def _canvas_bg_class(request: HttpRequest, theme_dict: Theme | None = None) -> str:
    """Return the CSS class for the canvas background from GET params, theme, or settings."""
    bg_param = request.GET.get("bg")
    if bg_param:
        for bg in get_backgrounds():
            if bg["value"] == bg_param:
                return f"canvas-bg-{bg['value']}"
        if theme_dict and isinstance(theme_dict.canvas_background, dict):
            if bg_param == f"theme-{theme_dict.value}":
                return f"canvas-bg-theme-{theme_dict.value}"

    if theme_dict and theme_dict.canvas_background:
        if isinstance(theme_dict.canvas_background, str):
            return f"canvas-bg-{theme_dict.canvas_background}"
        elif isinstance(theme_dict.canvas_background, dict):
            return f"canvas-bg-theme-{theme_dict.value}"

    default = get_default_background()
    return f"canvas-bg-{default['value']}"


def _canvas_bg_styles(
    theme_dict: Theme | None = None, request: HttpRequest | None = None
) -> str:
    """Generate ``<style>`` CSS rules for all configured canvas backgrounds."""
    rules = []
    for bg in get_backgrounds():
        rules.append(f".canvas-bg-{bg['value']} {{ background: {bg['color']}; }}")
        rules.append(f".gallery-bg-chip-{bg['value']} {{ background: {bg['color']}; }}")

    if theme_dict and isinstance(theme_dict.canvas_background, dict):
        bg = theme_dict.canvas_background
        if "color" in bg:
            rules.append(
                f".canvas-bg-theme-{theme_dict.value} {{ background: {bg['color']}; }}"
            )

    nonce_attr = ""
    if request:
        nonce = getattr(request, "csp_nonce", None)
        if nonce:
            nonce_attr = f' nonce="{html.escape(str(nonce))}"'

    return f"<style{nonce_attr}>\n" + "\n".join(rules) + "\n</style>"


@xframe_options_sameorigin
@gallery_access_required
def canvas_iframe_view(request: HttpRequest) -> HttpResponse:
    """Render a single component inside a full HTML document for iframe embedding."""
    theme_val = request.GET.get("theme") or request.COOKIES.get("dds_theme")
    context = {
        "rendered_html": "",
        "component_css": "",
        "component_js": "",
        "canvas_bg_class": "",
        "canvas_bg_styles": "",
        "canvas_mode_class": _canvas_mode_class(request),
        "html_attrs": "",
        "body_attrs": "",
    }
    try:
        spec = resolve_from_get_params(request.GET, component_registry)
    except ValueError as exc:
        html_attrs, body_attrs = _canvas_html_attrs()
        context["rendered_html"] = format_html(
            '<p class="gallery-canvas-error">Canvas error: {}</p>', str(exc)
        )
        context["html_attrs"] = html_attrs
        context["body_attrs"] = body_attrs
        return render(
            request,
            "dj_design_system/canvas/iframe.html",
            context,
        )

    info = resolve_component(spec.component_name, component_registry)
    app_label = info.app_label
    component_class = info.component_class

    available_theme_values = component_class.get_available_themes()

    if not theme_val:
        config = getattr(info, "gallery_config", None)
        if config:
            variant_obj = config.get_variant(spec.variant) if spec.variant else None
            if variant_obj and variant_obj.theme:
                theme_val = variant_obj.theme
            elif config.theme:
                theme_val = config.theme

    if theme_val not in available_theme_values:
        if available_theme_values:
            default_theme_val = get_default_theme().value
            theme_val = (
                default_theme_val
                if default_theme_val in available_theme_values
                else available_theme_values[0]
            )
        else:
            theme_val = get_default_theme().value

    theme_dict = get_theme(theme_val)
    if not theme_dict:
        theme_dict = get_default_theme()

    theme_css = theme_dict.css
    theme_js = theme_dict.js
    theme_css_bundles = get_bundle_urls(theme_dict.css_bundles, "css")
    theme_js_bundles = get_bundle_urls(theme_dict.js_bundles, "js")

    app_css, app_js = get_app_static(app_label)
    app_css_bundles = get_bundle_urls(
        (dds_settings.APP_CSS_BUNDLES or {}).get(app_label, []), "css"
    )
    app_js_bundles = get_bundle_urls(
        (dds_settings.APP_JS_BUNDLES or {}).get(app_label, []), "js"
    )

    media = get_component_media(spec, component_registry)
    context["rendered_html"] = render_component(spec, component_registry)

    all_css_urls = list(
        dict.fromkeys(
            theme_css_bundles
            + [static(p) for p in theme_css]
            + app_css_bundles
            + [static(p) for p in app_css]
            + [static(p) for p in media.css]
        )
    )
    all_js_urls = list(
        dict.fromkeys(
            theme_js_bundles
            + [static(p) for p in theme_js]
            + app_js_bundles
            + [static(p) for p in app_js]
            + [static(p) for p in media.js]
        )
    )

    context["component_css"] = "".join(
        f'<link rel="stylesheet" href="{u}">' for u in all_css_urls
    )
    context["component_js"] = "".join(
        f'<script src="{u}"></script>' for u in all_js_urls
    )
    context["html_attrs"], context["body_attrs"] = _canvas_html_attrs(
        theme_dict, app_label
    )
    context["canvas_bg_class"] = _canvas_bg_class(request, theme_dict)
    context["canvas_bg_styles"] = _canvas_bg_styles(theme_dict)

    return render(
        request,
        "dj_design_system/canvas/iframe.html",
        context,
    )
