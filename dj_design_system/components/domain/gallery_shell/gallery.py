"""Gallery configuration and variants for the built-in dds__gallery_shell component."""

import typing

from dj_design_system import gallery


SAMPLE_NODES: tuple[dict[str, typing.Any], ...] = (
    {
        "label": "Design System",
        "slug": "dj_design_system",
        "node_type": "app",
        "url": "/gallery/dj_design_system/",
        "active_path": "dj_design_system",
        "children": [
            {
                "label": "Elements",
                "slug": "elements",
                "node_type": "folder",
                "url": "/gallery/dj_design_system/elements/",
                "active_path": "dj_design_system/elements",
                "children": [
                    {
                        "label": "Button",
                        "slug": "button",
                        "node_type": "component",
                        "url": "/gallery/dj_design_system/elements/button/",
                        "active_path": "dj_design_system/elements/button",
                        "base_active_path": "dj_design_system/elements/button",
                        "children": [
                            {
                                "label": "Primary",
                                "slug": "primary",
                                "node_type": "variant",
                                "url": "/gallery/dj_design_system/elements/button/?variant=primary",
                                "active_path": "dj_design_system/elements/button",
                                "base_active_path": "dj_design_system/elements/button",
                            },
                        ],
                    },
                ],
            },
        ],
    },
)

SAMPLE_BREADCRUMBS: tuple[dict[str, str], ...] = (
    {"label": "Domain", "url": "/gallery/dj_design_system/domain/"},
    {"label": "Gallery Shell", "url": "/gallery/dj_design_system/domain/gallery_shell/"},
)

SAMPLE_THEMES: tuple[dict[str, str], ...] = (
    {"value": "light", "label": "Light"},
    {"value": "dark", "label": "Dark"},
)

SAMPLE_SEARCH_INDEX: tuple[dict[str, str], ...] = (
    {
        "label": "Button",
        "url": "/gallery/dj_design_system/elements/button/",
        "type": "component",
        "breadcrumb": "Elements / Button",
        "content": "Polymorphic interactive button or link control.",
    },
    {
        "label": "Gallery Shell",
        "url": "/gallery/dj_design_system/domain/gallery_shell/",
        "type": "component",
        "breadcrumb": "Domain / Gallery Shell",
        "content": "Top-level application shell with topbar, sidebar drawer, and main surface.",
    },
)

DEFAULT_MAIN_HTML = "<article><h1>Component Documentation</h1><p>Main gallery viewport content.</p></article>"
CUSTOM_TOPBAR_HTML = '<div data-custom-topbar><strong>Custom Topbar</strong></div>'
CUSTOM_SIDEBAR_HTML = '<nav data-custom-sidebar><a href="/docs/">Overview</a></nav>'
CUSTOM_ACTIONS_HTML = '<a href="https://example.com" data-custom-action>Docs</a>'


config = gallery.GalleryConfig(
    group="Domain",
    param_defaults={
        "brand_name": "Design System",
        "brand_url": "/gallery/",
        "nodes": list(SAMPLE_NODES),
        "active_path": "dj_design_system/elements/button",
        "breadcrumbs": list(SAMPLE_BREADCRUMBS),
        "themes": list(SAMPLE_THEMES),
        "active_theme": "light",
        "search_index": list(SAMPLE_SEARCH_INDEX),
        "slot__main": DEFAULT_MAIN_HTML,
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Default Gallery Shell",
            description="Full gallery layout with topbar, sidebar navigation tree, and main content surface.",
            kwargs={
                "brand_name": "Design System",
                "brand_url": "/gallery/",
                "nodes": list(SAMPLE_NODES),
                "active_path": "dj_design_system/elements/button",
                "breadcrumbs": list(SAMPLE_BREADCRUMBS),
                "themes": list(SAMPLE_THEMES),
                "active_theme": "light",
                "search_index": list(SAMPLE_SEARCH_INDEX),
                "slot__main": DEFAULT_MAIN_HTML,
            },
        ),
        gallery.Variant(
            name="dark_theme_with_actions",
            label="Dark Theme With Toolbar Actions",
            description="Gallery shell rendered in dark theme with extra toolbar actions injected via slot.",
            kwargs={
                "brand_name": "Acme UI",
                "brand_url": "/gallery/",
                "nodes": list(SAMPLE_NODES),
                "active_path": "dj_design_system/elements/button",
                "active_variant": "primary",
                "breadcrumbs": list(SAMPLE_BREADCRUMBS),
                "themes": list(SAMPLE_THEMES),
                "active_theme": "dark",
                "search_index": list(SAMPLE_SEARCH_INDEX),
                "slot__toolbar_actions": CUSTOM_ACTIONS_HTML,
                "slot__main": DEFAULT_MAIN_HTML,
            },
        ),
        gallery.Variant(
            name="custom_slots",
            label="Custom Topbar & Sidebar Slots",
            description="Gallery shell overriding the default topbar and sidebar with custom slot markup.",
            kwargs={
                "slot__topbar": CUSTOM_TOPBAR_HTML,
                "slot__sidebar": CUSTOM_SIDEBAR_HTML,
                "slot__main": DEFAULT_MAIN_HTML,
            },
        ),
    ],
)
