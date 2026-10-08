"""Gallery configuration and variants for the built-in dds__sidebar component."""

from dj_design_system import gallery


SAMPLE_NODES = (
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
                    {
                        "label": "Tokens Guide",
                        "slug": "tokens",
                        "node_type": "document",
                        "url": "/gallery/dj_design_system/elements/tokens/",
                        "active_path": "dj_design_system/elements/tokens",
                    },
                ],
            },
        ],
    },
)

SAMPLE_SEARCH_INDEX = (
    {
        "label": "Button",
        "url": "/gallery/dj_design_system/elements/button/",
        "type": "component",
        "breadcrumb": "Design System / Elements",
        "content": "Interactive button primitive.",
    },
    {
        "label": "Tokens Guide",
        "url": "/gallery/dj_design_system/elements/tokens/",
        "type": "document",
        "breadcrumb": "Design System / Elements",
        "content": "Three-tier design token reference.",
    },
)

CUSTOM_HEADER_HTML = "<strong>Acme UI Kit</strong>"
CUSTOM_FOOTER_HTML = "<span>v1.0.0</span>"

config = gallery.GalleryConfig(
    group="Domain",
    param_defaults={
        "brand_name": "Design System",
        "brand_url": "/gallery/",
        "nodes": list(SAMPLE_NODES),
        "active_path": "dj_design_system/elements/button",
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Default Sidebar",
            description="Standard gallery sidebar with brand link and active navigation tree.",
            kwargs={
                "brand_name": "Design System",
                "brand_url": "/gallery/",
                "nodes": list(SAMPLE_NODES),
                "active_path": "dj_design_system/elements/button",
            },
        ),
        gallery.Variant(
            name="with_search",
            label="Sidebar With Search",
            description="Sidebar displaying the embedded search box above the navigation tree.",
            kwargs={
                "brand_name": "Design System",
                "brand_url": "/gallery/",
                "nodes": list(SAMPLE_NODES),
                "active_path": "dj_design_system/elements/button",
                "active_variant": "primary",
                "show_search": True,
                "search_index": list(SAMPLE_SEARCH_INDEX),
            },
        ),
        gallery.Variant(
            name="custom_slots",
            label="Custom Header & Footer Slots",
            description="Sidebar overriding the header and footer via named slots.",
            kwargs={
                "nodes": list(SAMPLE_NODES),
                "active_path": "dj_design_system/elements/tokens",
                "slot__header": CUSTOM_HEADER_HTML,
                "slot__footer": CUSTOM_FOOTER_HTML,
            },
        ),
    ],
)
