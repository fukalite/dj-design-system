"""Gallery configuration and variants for the built-in dds__notice component."""

from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    group="Elements",
    param_defaults={
        "content": "Component changes are reflected automatically in the preview canvas.",
    },
    variants=[
        Variant(
            name="basic",
            label="Info",
            description="Default informational notice with automatic status icon.",
            kwargs={
                "variant": "info",
                "title": "Information",
                "content": "Component changes are reflected automatically in the preview canvas.",
            },
        ),
        Variant(
            name="success",
            label="Success",
            description="Positive status notice for completed actions or verified states.",
            kwargs={
                "variant": "success",
                "title": "Configuration Valid",
                "content": "All discovered components passed parameter and template validation.",
            },
        ),
        Variant(
            name="warning",
            label="Warning",
            description="Caution notice rendered with role='alert' for attention-required states.",
            kwargs={
                "variant": "warning",
                "title": "Deprecated Parameter",
                "content": "Support for legacy CSS class parameters will be removed in a future release.",
            },
        ),
        Variant(
            name="error",
            label="Error",
            description="Critical alert notice rendered with role='alert' for error conditions.",
            kwargs={
                "variant": "error",
                "title": "Rendering Failed",
                "content": "Required slot content was omitted when invoking the block component.",
            },
        ),
        Variant(
            name="maximal",
            label="Custom Icon Override",
            description="Notice with explicit title and custom icon override.",
            kwargs={
                "variant": "info",
                "title": "Documentation Tip",
                "icon": "doc",
                "content": "Co-locate an index.md file next to your component to publish usage notes.",
            },
        ),
    ],
)
