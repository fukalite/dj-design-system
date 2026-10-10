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
    ],
)
