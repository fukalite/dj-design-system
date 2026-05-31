from django import template
from django.templatetags.static import static
from django.utils.html import format_html_join

from dj_design_system import component_registry
from dj_design_system.services.media import (
    build_link_tags,
    build_script_tags,
    get_bundle_urls,
)
from dj_design_system.services.slot_node import do_slot
from dj_design_system.settings import dds_settings, get_app_static, get_theme


register = template.Library()

component_registry.register_templatetags(register)

register.tag("slot", do_slot)


@register.simple_tag
def component_stylesheets() -> str:
    """Render ``<link>`` tags for every CSS file required by registered components."""
    return build_link_tags(component_registry.get_merged_media().css)


@register.simple_tag
def component_scripts() -> str:
    """Render ``<script>`` tags for every JS file required by registered components."""
    return build_script_tags(component_registry.get_merged_media().js)


def _extend_theme_css(urls: list[str], theme: str) -> None:
    theme_dict = get_theme(theme)
    if not theme_dict:
        return
    theme_css_bundles = get_bundle_urls(theme_dict.get("css_bundles", []), "css")
    theme_css = theme_dict.get("css", [])
    urls.extend(theme_css_bundles)
    urls.extend(static(path) for path in theme_css)


def _extend_app_css(urls: list[str], app_label: str) -> None:
    app_css, _ = get_app_static(app_label)
    app_css_bundles = get_bundle_urls(
        (dds_settings.APP_CSS_BUNDLES or {}).get(app_label, []), "css"
    )
    urls.extend(app_css_bundles)
    urls.extend(static(path) for path in app_css)


@register.simple_tag
def global_stylesheets(app_label: str | None = None, theme: str | None = None) -> str:
    """Render ``<link>`` tags for global, theme, and app-specific CSS bundles and static paths."""
    urls = get_bundle_urls(dds_settings.GLOBAL_CSS_BUNDLES, "css") + [
        static(path) for path in dds_settings.GLOBAL_CSS
    ]

    if theme:
        _extend_theme_css(urls, theme)

    if app_label:
        _extend_app_css(urls, app_label)

    urls = list(dict.fromkeys(urls))
    if not urls:
        return ""
    all_hrefs = [(url,) for url in urls]
    return format_html_join("\n", '<link rel="stylesheet" href="{}">', all_hrefs)


def _extend_theme_js(urls: list[str], theme: str) -> None:
    theme_dict = get_theme(theme)
    if not theme_dict:
        return
    theme_js_bundles = get_bundle_urls(theme_dict.get("js_bundles", []), "js")
    theme_js = theme_dict.get("js", [])
    urls.extend(theme_js_bundles)
    urls.extend(static(path) for path in theme_js)


def _extend_app_js(urls: list[str], app_label: str) -> None:
    _, app_js = get_app_static(app_label)
    app_js_bundles = get_bundle_urls(
        (dds_settings.APP_JS_BUNDLES or {}).get(app_label, []), "js"
    )
    urls.extend(app_js_bundles)
    urls.extend(static(path) for path in app_js)


@register.simple_tag
def global_scripts(app_label: str | None = None, theme: str | None = None) -> str:
    """Render ``<script>`` tags for global, theme, and app-specific JS bundles and static paths."""
    urls = get_bundle_urls(dds_settings.GLOBAL_JS_BUNDLES, "js") + [
        static(path) for path in dds_settings.GLOBAL_JS
    ]

    if theme:
        _extend_theme_js(urls, theme)

    if app_label:
        _extend_app_js(urls, app_label)

    urls = list(dict.fromkeys(urls))
    if not urls:
        return ""
    all_srcs = [(url,) for url in urls]
    return format_html_join("\n", '<script src="{}"></script>', all_srcs)
