"""Gallery configuration and variants for the built-in dds__search_box component."""

from dj_design_system import gallery


SAMPLE_SEARCH_INDEX: tuple[dict[str, str], ...] = (
    {
        "label": "Button",
        "url": "/design-system/c/dds__button/",
        "type": "component",
        "breadcrumb": "Elements / Button",
        "content": "Interactive button and link primitive with variants and sizes.",
    },
    {
        "label": "Popout",
        "url": "/design-system/c/dds__popout/",
        "type": "component",
        "breadcrumb": "Elements / Popout",
        "content": "Accessible dropdown menu and popover primitive.",
    },
    {
        "label": "Design Tokens",
        "url": "/design-system/docs/tokens/",
        "type": "document",
        "breadcrumb": "Guides / Design Tokens",
        "content": "Three-tier design token architecture for the gallery.",
    },
)

config = gallery.GalleryConfig(
    group="Domain",
    param_defaults={
        "placeholder": "Search components and docs...",
        "search_index": list(SAMPLE_SEARCH_INDEX),
    },
    variants=[
        gallery.Variant(
            name="default",
            label="Default Search Box",
            description="Standard gallery search box with keyboard shortcut hint and embedded index.",
            kwargs={
                "placeholder": "Search components and docs...",
                "search_index": list(SAMPLE_SEARCH_INDEX),
            },
        ),
        gallery.Variant(
            name="custom_shortcut",
            label="Custom Shortcut & Placeholder",
            description="Search box configured with a custom placeholder and shortcut badge.",
            kwargs={
                "placeholder": "Quick jump to component...",
                "shortcut_hint": "⌘K",
                "index_id": "custom-search-index",
                "input_id": "custom-search-input",
                "results_id": "custom-search-results",
                "search_index": list(SAMPLE_SEARCH_INDEX),
            },
        ),
        gallery.Variant(
            name="without_shortcut",
            label="Without Shortcut Badge",
            description="Search box with the keyboard shortcut hint badge hidden.",
            kwargs={
                "placeholder": "Filter components...",
                "shortcut_hint": "",
                "search_index": list(SAMPLE_SEARCH_INDEX),
            },
        ),
    ],
)
