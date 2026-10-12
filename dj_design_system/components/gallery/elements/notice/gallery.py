"""Gallery configuration and variants for the built-in dds__notice component."""

from dj_design_system import gallery


config = gallery.GalleryConfig(
    group="Elements",
    param_defaults={
        "variant": "info",
        "title": "Information",
        "content": "Component changes are reflected automatically in the preview canvas.",
    },
)
