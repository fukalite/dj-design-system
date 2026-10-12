"""Gallery configuration and variants for the built-in dds__breadcrumb component."""

from dj_design_system import gallery
from dj_design_system.components.gallery.elements.breadcrumb import BreadcrumbItem


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

DEEP_ITEMS = [
    BreadcrumbItem(label="Root", url="/", icon="folder"),
    BreadcrumbItem(label="Design System", url="/gallery/", icon="folder-open"),
    BreadcrumbItem(label="Elements", url="/gallery/elements/", icon="folder"),
    BreadcrumbItem(label="Navigation", url="/gallery/elements/#nav", icon="doc"),
    BreadcrumbItem(label="Breadcrumb", icon="component"),
]

config = gallery.GalleryConfig(
    group="Elements",
    param_defaults={
        "items": BASIC_ITEMS,
    },
)

