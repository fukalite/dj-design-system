"""Gallery configuration and variants for the built-in dds__button component."""

from dj_design_system import gallery


config = gallery.GalleryConfig(
    order=2,
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
            description="Primary button with leading and trailing icons, large size, and action hook.",
            kwargs={
                "label": "Open preview",
                "variant": "primary",
                "size": "lg",
                "icon": "eye",
                "icon_trailing": "external-link",
                "action": "open-preview",
            },
        ),
        gallery.Variant(
            name="primary",
            label="Primary",
            description="High-emphasis action button.",
            kwargs={"label": "Apply filters", "variant": "primary", "icon": "check"},
        ),
        gallery.Variant(
            name="ghost",
            label="Ghost",
            description="Low-emphasis borderless toolbar button.",
            kwargs={"label": "Copy code", "variant": "ghost", "icon": "copy", "size": "sm"},
        ),
        gallery.Variant(
            name="danger",
            label="Danger",
            description="Destructive action button styled with error status tokens.",
            kwargs={"label": "Reset parameters", "variant": "danger", "icon": "reset"},
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
    ],
)
