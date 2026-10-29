"""Gallery configuration and variants for the built-in dds__nav_tree component."""

from dj_design_system import gallery


SAMPLE_NODES: tuple[dict[str, object], ...] = (
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
                            {
                                "label": "Ghost",
                                "slug": "ghost",
                                "node_type": "variant",
                                "url": "/gallery/dj_design_system/elements/button/?variant=ghost",
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

config = gallery.GalleryConfig(
    group="Composites",
    param_defaults={
        "nodes": list(SAMPLE_NODES),
        "active_path": "dj_design_system/elements/button",
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Active Component Node",
            description="Navigation tree with an expanded folder hierarchy and active component node.",
            kwargs={
                "nodes": list(SAMPLE_NODES),
                "active_path": "dj_design_system/elements/button",
            },
        ),
    ],
)
