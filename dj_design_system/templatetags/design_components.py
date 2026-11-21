import html

from django import template
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

from dj_design_system import component_registry
from dj_design_system.services import config as config_service
from dj_design_system.services import media as media_service
from dj_design_system.services.slot_node import do_slot


register = template.Library()

component_registry.register_templatetags(register)

register.tag("slot", do_slot)


@register.simple_tag
def component_stylesheets() -> str:
    """Render ``<link>`` tags for every CSS file required by registered components."""
    return media_service.build_link_tags(component_registry.get_merged_media().css)


@register.simple_tag(takes_context=True)
def component_scripts(context: template.Context | None = None) -> str:
    """Render ``<script>`` tags for every JS file required by registered components."""
    request = context.get("request") if context else None
    nonce = (
        getattr(request, "csp_nonce", None)
        if request
        else (context.get("csp_nonce") if context else None)
    )
    return media_service.build_script_tags(
        component_registry.get_merged_media().js, nonce=nonce
    )


def _extend_theme_css(urls: list[str], theme: str) -> None:
    theme_obj = config_service.get_theme(identifier=theme)
    if not theme_obj:
        return
    theme_css_bundles = media_service.get_bundle_urls(theme_obj.css_bundles, "css")
    urls.extend(theme_css_bundles)
    urls.extend(media_service.resolve_asset_url(path=path) for path in theme_obj.css)


def _extend_app_css(urls: list[str], app_label: str) -> None:
    app_cfg = config_service.get_app_settings(app_label=app_label)
    app_css_bundles = media_service.get_bundle_urls(app_cfg.css_bundles, "css")
    urls.extend(app_css_bundles)
    urls.extend(media_service.resolve_asset_url(path=path) for path in app_cfg.css)


@register.simple_tag
def global_stylesheets(app_label: str | None = None, theme: str | None = None) -> str:
    """Render ``<link>`` tags for global, theme, and app-specific CSS bundles and static paths."""
    cfg = config_service.get_config()
    urls = media_service.get_bundle_urls(cfg.css_bundles, "css") + [
        media_service.resolve_asset_url(path=path) for path in cfg.css
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
    theme_obj = config_service.get_theme(identifier=theme)
    if not theme_obj:
        return
    theme_js_bundles = media_service.get_bundle_urls(theme_obj.js_bundles, "js")
    urls.extend(theme_js_bundles)
    urls.extend(media_service.resolve_asset_url(path=path) for path in theme_obj.js)


def _extend_app_js(urls: list[str], app_label: str) -> None:
    app_cfg = config_service.get_app_settings(app_label=app_label)
    app_js_bundles = media_service.get_bundle_urls(app_cfg.js_bundles, "js")
    urls.extend(app_js_bundles)
    urls.extend(media_service.resolve_asset_url(path=path) for path in app_cfg.js)


@register.simple_tag(takes_context=True)
def global_scripts(
    context: template.Context | None = None,
    app_label: str | None = None,
    theme: str | None = None,
) -> str:
    """Render ``<script>`` tags for global, theme, and app-specific JS bundles and static paths."""
    cfg = config_service.get_config()
    urls = media_service.get_bundle_urls(cfg.js_bundles, "js") + [
        media_service.resolve_asset_url(path=path) for path in cfg.js
    ]

    if theme:
        _extend_theme_js(urls, theme)

    if app_label:
        _extend_app_js(urls, app_label)

    urls = list(dict.fromkeys(urls))
    if not urls:
        return ""

    request = context.get("request") if context else None
    nonce = (
        getattr(request, "csp_nonce", None)
        if request
        else (context.get("csp_nonce") if context else None)
    )
    if nonce:
        nonce_attr = mark_safe(f' nonce="{html.escape(str(nonce))}"')
        all_srcs = [(url,) for url in urls]
        return format_html_join(
            "\n", f'<script src="{{}}" {nonce_attr}></script>', all_srcs
        )

    all_srcs = [(url,) for url in urls]
    return format_html_join("\n", '<script src="{}"></script>', all_srcs)
