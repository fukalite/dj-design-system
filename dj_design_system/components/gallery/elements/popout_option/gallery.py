"""Gallery configuration and variants for the built-in dds__popout_option component."""

from dj_design_system import gallery


config = gallery.GalleryConfig(
    group="Elements",
    param_defaults={
        "label": "Light theme",
        "value": "light",
    },
)
