"""Gallery configuration and variants for the built-in dds__notice component."""

from dj_design_system import gallery


config = gallery.GalleryConfig(
    group="Elements",
    param_defaults={
        "content": "Component changes are reflected automatically in the preview canvas.",
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Info",
            description="Minimal informational notice with automatic status icon.",
            kwargs={},
        ),
        gallery.Variant(
            name="success",
            label="Success",
            description="Positive status notice for completed actions or verified states.",
            kwargs={
                "variant": "success",
                "title": "Configuration Valid",
                "content": "All discovered components passed parameter and template validation.",
            },
        ),
        gallery.Variant(
            name="warning",
            label="Warning",
            description="Caution notice rendered with role='alert' for attention-required states.",
            kwargs={
                "variant": "warning",
                "title": "Deprecated Parameter",
                "content": "Support for legacy CSS class parameters will be removed in a future release.",
            },
        ),
        gallery.Variant(
            name="error",
            label="Error",
            description="Critical alert notice rendered with role='alert' for error conditions.",
            kwargs={
                "variant": "error",
                "title": "Rendering Failed",
                "content": "Required slot content was omitted when invoking the block component.",
            },
        ),
        gallery.Variant(
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
        gallery.Variant(
            name="no_icon",
            label="Icon Suppressed",
            description="Minimal callout without an icon via icon='none'.",
            kwargs={
                "variant": "info",
                "title": "Unadorned Note",
                "icon": "none",
                "content": "A simple callout banner without a leading status icon.",
            },
        ),
        gallery.Variant(
            name="static_warning",
            label="Static Warning with Role Override",
            description="Warning notice with role='note' to avoid intrusive live region alerts.",
            kwargs={
                "variant": "warning",
                "title": "Migration Note",
                "role": "note",
                "content": "Please migrate to the new component API at your earliest convenience.",
            },
        ),
    ],
)
