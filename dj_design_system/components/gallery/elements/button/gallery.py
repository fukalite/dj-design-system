"""Gallery configuration and variants for the built-in dds__button component."""

from dj_design_system import gallery


config = gallery.GalleryConfig(
    param_defaults={
        "label": "Save changes",
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Default Button",
            description="Standard control surface button for secondary actions.",
            kwargs={"label": "Save changes"},
        ),
        gallery.Variant(
            name="maximal",
            label="Primary Button with Icons",
            description="Primary action button showcasing variant, size, leading and trailing icons, and action hook.",
            kwargs={
                "label": "Save changes",
                "variant": "primary",
                "size": "lg",
                "icon": "check",
                "icon_trailing": "external-link",
                "action": "save-form",
            },
        ),
        gallery.Variant(
            name="link",
            label="Link Button",
            description="Anchor element styled as a button with external target and rel attributes.",
            kwargs={
                "label": "Documentation",
                "href": "https://example.com/docs",
                "target": "_blank",
                "icon_trailing": "external-link",
            },
        ),
        gallery.Variant(
            name="icon_only",
            label="Icon Only",
            description="Compact square icon button with accessible aria-label.",
            kwargs={
                "label": "Toggle theme",
                "variant": "ghost",
                "icon": "sun",
                "icon_only": True,
            },
        ),
        gallery.Variant(
            name="toggle",
            label="Toggle (Pressed)",
            description="Active toggle button with aria-pressed state.",
            kwargs={
                "label": "Pin panel",
                "icon": "box-model",
                "pressed": True,
            },
        ),
    ],
)
