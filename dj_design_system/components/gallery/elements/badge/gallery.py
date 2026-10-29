"""Gallery configuration and variants for the built-in dds__badge component."""

from dj_design_system import gallery


config = gallery.GalleryConfig(
    group="Elements",
    param_defaults={
        "label": "Optional",
        "variant": "neutral",
        "is_code": False,
    },
)
