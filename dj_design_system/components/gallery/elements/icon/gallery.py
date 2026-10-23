"""Gallery configuration and variants for the built-in dds__icon component."""

from dj_design_system import gallery


config = gallery.GalleryConfig(
    order=1,
    variants=[
        gallery.Variant(
            name="basic",
            label="Default Icon",
            kwargs={"name": "component"},
        ),
        gallery.Variant(
            name="maximal",
            label="Accessible Large Icon",
            kwargs={
                "name": "search",
                "size": "lg",
                "label": "Search documentation",
            },
        ),
        gallery.Variant(
            name="extra_small",
            label="Extra Small (xs)",
            description="Compact icon size for dense inline indicators.",
            kwargs={"name": "external-link", "size": "xs"},
        ),
        gallery.Variant(
            name="small",
            label="Small (sm)",
            description="Small icon size for toolbar controls and navigation items.",
            kwargs={"name": "eye", "size": "sm"},
        ),
        gallery.Variant(
            name="large",
            label="Large (lg)",
            description="Large icon size for callouts and prominent status indicators.",
            kwargs={"name": "info", "size": "lg", "label": "Information"},
        ),
        gallery.Variant(
            name="status_success",
            label="Success Status",
            description="Success check icon for positive completion and validation states.",
            kwargs={"name": "success", "size": "md", "label": "Operation succeeded"},
        ),
        gallery.Variant(
            name="status_warning",
            label="Warning Status",
            description="Warning triangle icon for alerts requiring user attention.",
            kwargs={"name": "warning", "size": "md", "label": "Warning alert"},
        ),
        gallery.Variant(
            name="status_error",
            label="Error Status",
            description="Error alert icon for critical failures and validation errors.",
            kwargs={"name": "error", "size": "md", "label": "Error condition"},
        ),
        gallery.Variant(
            name="action_copy",
            label="Copy Action",
            description="Clipboard copy icon for copying snippets and tokens.",
            kwargs={"name": "copy", "size": "sm", "label": "Copy to clipboard"},
        ),
    ],
)
