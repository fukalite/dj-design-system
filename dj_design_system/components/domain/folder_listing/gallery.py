"""Gallery configuration and variants for the built-in dds__folder_listing component."""

from dj_design_system import gallery


MIXED_FOLDER_ITEMS: tuple[dict[str, object], ...] = (
    {
        "label": "Elements",
        "url": "/gallery/elements/",
        "node_type": "folder",
        "children": ["badge", "button", "icon", "notice"],
    },
    {
        "label": "Button",
        "url": "/gallery/elements/button/",
        "node_type": "component",
        "children": ["basic"],
    },
    {
        "label": "Getting Started",
        "url": "/gallery/docs/getting-started/",
        "node_type": "document",
    },
    {
        "label": "Primary Action",
        "url": "/gallery/elements/button/?variant=primary",
        "node_type": "variant",
    },
)

COLLECTION_FOLDER_ITEMS: tuple[dict[str, object], ...] = (
    {
        "label": "Badge",
        "url": "/gallery/elements/badge/",
        "node_type": "component",
    },
    {
        "label": "Breadcrumb",
        "url": "/gallery/elements/breadcrumb/",
        "node_type": "component",
    },
    {
        "label": "Notice",
        "url": "/gallery/elements/notice/",
        "node_type": "component",
    },
)

config = gallery.GalleryConfig(
    group="Domain",
    param_defaults={
        "title": "Components",
        "items": list(MIXED_FOLDER_ITEMS),
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Mixed Folder Contents",
            description="Folder listing displaying nested folders, components, documents, and variants.",
            kwargs={
                "title": "Components",
                "items": list(MIXED_FOLDER_ITEMS),
            },
        ),
        gallery.Variant(
            name="with_debug_hint",
            label="Folder with Authoring Hint",
            description="Component collection folder displaying the index.md customisation notice.",
            kwargs={
                "title": "Elements",
                "items": list(COLLECTION_FOLDER_ITEMS),
                "show_debug_hint": True,
            },
        ),
        gallery.Variant(
            name="empty",
            label="Empty Folder State",
            description="Fallback empty state with custom message and authoring hint.",
            kwargs={
                "title": "Experimental",
                "items": [],
                "empty_message": "No components have been registered in this folder yet.",
                "show_debug_hint": True,
            },
        ),
    ],
)
