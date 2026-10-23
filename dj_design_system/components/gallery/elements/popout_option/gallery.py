"""Gallery configuration and variants for the built-in dds__popout_option component."""

from dj_design_system import gallery


config = gallery.GalleryConfig(
    group="Elements",
    param_defaults={
        "label": "Light theme",
        "value": "light",
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Default Option",
            description="Unselected selectable menu option button.",
            kwargs={
                "label": "Light theme",
                "value": "light",
            },
        ),
        gallery.Variant(
            name="selected",
            label="Selected Option",
            description="Currently selected menu option with leading icon.",
            kwargs={
                "label": "Dark theme",
                "value": "dark",
                "icon": "moon",
                "selected": True,
            },
        ),
        gallery.Variant(
            name="link",
            label="Link Option",
            description="Navigation menu item rendered as an anchor element.",
            kwargs={
                "label": "Documentation",
                "href": "https://example.com/docs",
                "icon": "external-link",
            },
        ),
        gallery.Variant(
            name="action",
            label="Action Menu Item",
            description="Immediate action button item using role='menuitem'.",
            kwargs={
                "label": "Save changes",
                "icon": "check",
                "role": "menuitem",
            },
        ),
        gallery.Variant(
            name="shortcut",
            label="Option with Shortcut Hint",
            description="Menu item with keyboard shortcut hint.",
            kwargs={
                "label": "Quick search",
                "icon": "search",
                "shortcut": "⌘K",
                "role": "menuitem",
            },
        ),
        gallery.Variant(
            name="disabled",
            label="Disabled Option",
            description="Disabled menu option forcing a non-interactive button.",
            kwargs={
                "label": "Reset overrides",
                "value": "reset",
                "icon": "reset",
                "disabled": True,
            },
        ),
    ],
)
