"""Gallery configuration and variants for the built-in dds__toolbar component."""

from dj_design_system import gallery


SAMPLE_BREADCRUMBS: tuple[dict[str, str], ...] = (
    {"label": "Domain", "url": "/design-system/components/domain/"},
    {"label": "Toolbar", "url": "/design-system/components/domain/toolbar/"},
)

SAMPLE_THEMES: tuple[dict[str, str], ...] = (
    {"value": "light", "label": "Light"},
    {"value": "dark", "label": "Dark"},
)

SAMPLE_SEARCH_INDEX: tuple[dict[str, str], ...] = (
    {
        "label": "Button",
        "url": "/design-system/components/elements/button/",
        "type": "component",
        "breadcrumb": "Elements / Button",
        "content": "Polymorphic interactive button or link control.",
    },
    {
        "label": "Toolbar",
        "url": "/design-system/components/domain/toolbar/",
        "type": "component",
        "breadcrumb": "Domain / Toolbar",
        "content": "Top gallery header bar with breadcrumbs, search, and theme selector.",
    },
)


config = gallery.GalleryConfig(
    group="Domain",
    param_defaults={
        "brand_name": "Design System",
        "brand_url": "/",
        "show_search": True,
        "show_menu_toggle": True,
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Default Gallery Toolbar",
            description="Minimal toolbar with drawer toggle, brand link, and search box.",
            kwargs={
                "brand_name": "Design System",
                "brand_url": "/",
            },
        ),
        gallery.Variant(
            name="with_breadcrumbs_and_themes",
            label="Breadcrumbs and Theme Selector",
            description="Full gallery topbar with breadcrumb trail, search index, and theme selector.",
            kwargs={
                "brand_name": "Acme UI",
                "brand_url": "/design-system/",
                "breadcrumbs": list(SAMPLE_BREADCRUMBS),
                "themes": list(SAMPLE_THEMES),
                "active_theme": "dark",
                "search_index": list(SAMPLE_SEARCH_INDEX),
            },
        ),
        gallery.Variant(
            name="minimal_brand_only",
            label="Minimal Brand Bar",
            description="Compact header bar with menu toggle and search hidden.",
            kwargs={
                "brand_name": "Component Docs",
                "brand_url": "/docs/",
                "show_search": False,
                "show_menu_toggle": False,
            },
        ),
    ],
)
