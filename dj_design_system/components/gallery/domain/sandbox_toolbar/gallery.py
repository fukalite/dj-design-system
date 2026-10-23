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
        gallery.Variant(
            name="with_variants",
            label="With Variant Presets",
            description=(
                "Sandbox toolbar displaying a variant preset switcher alongside "
                "canvas controls."
            ),
            kwargs={
                "variants": list(SAMPLE_VARIANTS),
                "active_variant": "primary",
                "component_url": "/gallery/dj_design_system/elements/button/",
            },
        ),
        gallery.Variant(
            name="active_inspection_and_links",
            label="Active Inspection Toggles & Action Links",
            description=(
                "Sandbox toolbar with dark background, tablet viewport, 125% "
                "zoom, enabled inspection toggles, reset link, and standalone "
                "canvas link."
            ),
            kwargs={
                "variants": list(SAMPLE_VARIANTS),
                "active_variant": "danger",
                "component_url": "/gallery/dj_design_system/elements/button/",
                "active_background": "dark",
                "active_viewport": "768",
                "active_zoom": "125",
                "outline_active": True,
                "measure_active": True,
                "rtl_active": True,
                "reset_url": "/gallery/dj_design_system/elements/button/",
                "canvas_url": "/gallery/dj_design_system/elements/button/canvas/",
            },
        ),
    ],
)
