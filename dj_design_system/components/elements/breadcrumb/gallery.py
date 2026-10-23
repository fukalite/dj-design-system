"""Gallery configuration and variants for the built-in dds__breadcrumb component."""

from dj_design_system import gallery


BASIC_ITEMS = [
    {"label": "Gallery", "url": "/gallery/"},
    {"label": "Elements", "url": "/gallery/elements/"},
    {"label": "Breadcrumb"},
]

ICON_ITEMS = [
    {"label": "Gallery", "url": "/gallery/", "icon": "folder"},
    {"label": "Elements", "url": "/gallery/elements/", "icon": "folder-open"},
    {
        "label": "Breadcrumb",
        "url": "/gallery/elements/breadcrumb/",
        "icon": "component",
    },
]

STATIC_PARENT_ITEMS = [
    {"label": "dj_design_system"},
    {"label": "elements", "href": "/gallery/elements/"},
    {"label": "breadcrumb"},
]

config = gallery.GalleryConfig(
    group="Elements",
    param_defaults={
        "items": BASIC_ITEMS,
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Standard Trail",
            description="Three-level breadcrumb trail with linked ancestors and current page.",
            kwargs={
                "items": BASIC_ITEMS,
            },
        ),
        gallery.Variant(
            name="with_icons",
            label="Trail with Item Icons",
            description="Breadcrumb items displaying inline collection and component icons.",
            kwargs={
                "items": ICON_ITEMS,
            },
        ),
        gallery.Variant(
            name="static_ancestors",
            label="Mixed Static and Linked Ancestors",
            description="Trail containing non-interactive ancestor segments alongside links.",
            kwargs={
                "items": STATIC_PARENT_ITEMS,
            },
        ),
        gallery.Variant(
            name="maximal",
            label="Custom Landmark and Separator",
            description="Full breadcrumb with item icons, custom aria-label, and explicit separator icon.",
            kwargs={
                "items": ICON_ITEMS,
                "aria_label": "Component hierarchy",
                "separator_icon": "chevron-right",
            },
        ),
    ],
)
