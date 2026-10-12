"""Gallery configuration and variants for the built-in dds__sandbox_toolbar component."""

from dj_design_system import gallery


SAMPLE_VARIANTS: tuple[dict[str, str], ...] = (
    {"name": "default", "label": "Default Button"},
    {"name": "primary", "label": "Primary Action"},
    {"name": "danger", "label": "Danger Action"},
)


config = gallery.GalleryConfig(
    group="Domain",
    param_defaults={
        "active_background": "white",
        "active_viewport": "responsive",
        "active_zoom": "100",
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Default Sandbox Toolbar",
            description=(
                "Standard sandbox toolbar with background, viewport, zoom "
                "popout selectors and inspection toggles."
            ),
            kwargs={
                "active_background": "white",
                "active_viewport": "responsive",
                "active_zoom": "100",
            },
        ),
    ],
)
