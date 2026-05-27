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
from dj_design_system.settings import dds_settings


register = template.Library()

component_registry.register_templatetags(register)

# Register the {% slot "name" %}...{% endslot %} tag globally
register.tag("slot", do_slot)


@register.simple_tag
def component_stylesheets() -> str:
    """Render ``<link>`` tags for every CSS file required by registered components.

    Merges the CSS paths from all discovered components, deduplicating across
    components, and returns safe HTML ready to embed in ``<head>``.
    """
    return build_link_tags(component_registry.get_merged_media().css)


@register.simple_tag
def component_scripts() -> str:
    """Render ``<script>`` tags for every JS file required by registered components.

    Merges the JS paths from all discovered components, deduplicating across
    components, and returns safe HTML ready to embed before ``</body>``.
    """
    return build_script_tags(component_registry.get_merged_media().js)


@register.simple_tag
def global_stylesheets(app_label: str = None, theme: str = None) -> str:
    """Render ``<link>`` tags for global, theme, and app-specific CSS bundles and static paths.

    Sources (in order):

    1. Webpack bundles listed in ``GLOBAL_CSS_BUNDLES`` - each entry is a
       tuple of args for ``webpack_loader.utils.get_files``, e.g.
       ``("main",)`` or ``("main", "MY_CONFIG")``.  Skipped when
       ``webpack_loader`` is not installed.
    2. Static file paths listed in ``GLOBAL_CSS`` - each resolved via
       Django's ``{% static %}`` tag.
    3. Theme-specific bundles and CSS paths (if theme is provided).
    4. App-specific bundles and CSS paths (if app_label is provided).

    Returns an empty string when all lists are empty.
    """
    all_hrefs = [
        (url,) for url in get_bundle_urls(dds_settings.GLOBAL_CSS_BUNDLES, "css")
    ] + [(static(path),) for path in dds_settings.GLOBAL_CSS]

    if theme:
        from dj_design_system.settings import get_theme

        theme_dict = get_theme(theme)
        if theme_dict:
            theme_css_bundles = get_bundle_urls(
                theme_dict.get("css_bundles", []), "css"
            )
            theme_css = theme_dict.get("css", [])
            all_hrefs.extend((url,) for url in theme_css_bundles)
            all_hrefs.extend((static(path),) for path in theme_css)

    if app_label:
        from dj_design_system.settings import get_app_static

        app_css, _ = get_app_static(app_label)
        app_css_bundles = get_bundle_urls(
            dds_settings.APP_CSS_BUNDLES.get(app_label, []), "css"
        )
        all_hrefs.extend((url,) for url in app_css_bundles)
        all_hrefs.extend((static(path),) for path in app_css)

    if not all_hrefs:
        return ""
    return format_html_join("\n", '<link rel="stylesheet" href="{}">', all_hrefs)


@register.simple_tag
def global_scripts(app_label: str = None, theme: str = None) -> str:
    """Render ``<script>`` tags for global, theme, and app-specific JS bundles and static paths.

    Sources (in order):

    1. Webpack bundles listed in ``GLOBAL_JS_BUNDLES`` - each entry is a
       tuple of args for ``webpack_loader.utils.get_files``, e.g.
       ``("main",)`` or ``("main", "MY_CONFIG")``.  Skipped when
       ``webpack_loader`` is not installed.
    2. Static file paths listed in ``GLOBAL_JS`` - each resolved via
       Django's ``{% static %}`` tag.
    3. Theme-specific bundles and JS paths (if theme is provided).
    4. App-specific bundles and JS paths (if app_label is provided).

    Returns an empty string when all lists are empty.
    """
    all_srcs = [
        (url,) for url in get_bundle_urls(dds_settings.GLOBAL_JS_BUNDLES, "js")
    ] + [(static(path),) for path in dds_settings.GLOBAL_JS]

    if theme:
        from dj_design_system.settings import get_theme

        theme_dict = get_theme(theme)
        if theme_dict:
            theme_js_bundles = get_bundle_urls(theme_dict.get("js_bundles", []), "js")
            theme_js = theme_dict.get("js", [])
            all_srcs.extend((url,) for url in theme_js_bundles)
            all_srcs.extend((static(path),) for path in theme_js)

    if app_label:
        from dj_design_system.settings import get_app_static

        _, app_js = get_app_static(app_label)
        app_js_bundles = get_bundle_urls(
            dds_settings.APP_JS_BUNDLES.get(app_label, []), "js"
        )
        all_srcs.extend((url,) for url in app_js_bundles)
        all_srcs.extend((static(path),) for path in app_js)

    if not all_srcs:
        return ""
    return format_html_join("\n", '<script src="{}"></script>', all_srcs)
