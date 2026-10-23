"""Gallery configuration and variants for the built-in dds__theme_select component."""

from dj_design_system import gallery


STANDARD_THEMES: tuple[dict[str, str], ...] = (
    {"value": "light", "label": "Light"},
    {"value": "dark", "label": "Dark"},
)

EXTENDED_THEMES: tuple[dict[str, str], ...] = (
    {"value": "light", "label": "Light"},
    {"value": "dark", "label": "Dark"},
    {"value": "high-contrast-dark", "label": "High Contrast Dark"},
)


config = gallery.GalleryConfig(
    group="Domain",
    param_defaults={
        "themes": list(STANDARD_THEMES),
        "active_theme": "light",
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Light Theme Active",
            description="Standard theme selector with Light selected.",
            kwargs={
                "themes": list(STANDARD_THEMES),
                "active_theme": "light",
            },
        ),
    ],
)
