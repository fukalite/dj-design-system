"""Gallery configuration and variants for the built-in dds__popout_option component."""

from dj_design_system import gallery


config = gallery.GalleryConfig(
    group="Elements",
    param_defaults={
        "label": "Dark theme",
        "value": "dark",
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Radio Option",
            description="Standard selectable radio option with leading icon.",
            kwargs={
                "label": "Light theme",
                "value": "light",
                "icon": "sun",
                "selected": True,
            },
        ),
        gallery.Variant(
            name="maximal",
            label="Full Menu Item",
            description="Option showcasing role, icon, shortcut, selection, and link.",
            kwargs={
                "label": "Dark theme",
                "value": "dark",
                "role": "menuitemradio",
                "icon": "moon",
                "shortcut": "⌘D",
                "selected": True,
                "disabled": False,
                "href": "/themes/dark/",
            },
        ),
        gallery.Variant(
            name="checkbox",
            label="Checkbox Option",
            description="Toggleable menuitemcheckbox option with shortcut hint.",
            kwargs={
                "label": "Show line numbers",
                "value": "line-numbers",
                "role": "menuitemcheckbox",
                "shortcut": "⌘L",
                "selected": True,
            },
        ),
        gallery.Variant(
            name="link",
            label="Navigation Link Option",
            description="Menu item rendered as a link navigating to an external or internal URL.",
            kwargs={
                "label": "Documentation",
                "href": "https://example.com/docs",
                "icon": "external-link",
            },
        ),
        gallery.Variant(
            name="disabled",
            label="Disabled Option",
            description="Disabled option item retaining disabled semantics.",
            kwargs={
                "label": "High contrast mode",
                "value": "high-contrast",
                "icon": "eye",
                "disabled": True,
            },
        ),
    ],
)

