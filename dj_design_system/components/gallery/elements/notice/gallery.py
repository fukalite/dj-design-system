"""Gallery configuration and variants for the built-in dds__notice component."""

from dj_design_system import gallery


config = gallery.GalleryConfig(
    group="Elements",
    param_defaults={
        "variant": "info",
        "title": "Information",
        "content": "Component changes are reflected automatically in the preview canvas.",
    },
    variants=[
        gallery.Variant(
            name="maximal",
            label="Warning Alert with Custom Icon",
            description="Notice in warning state showcasing explicit icon, title, and role.",
            kwargs={
                "variant": "warning",
                "title": "Deprecated Parameter",
                "icon": "warning",
                "role": "alert",
                "content": "Support for legacy CSS class parameters will be removed in a future release.",
            },
        ),
    ],
)
