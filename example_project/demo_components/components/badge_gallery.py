"""Gallery configuration and variants for the BadgeComponent."""

from dj_design_system import gallery


config = gallery.GalleryConfig(
    order=2,
    variants=[
        gallery.Variant(
            name="basic", label="Default Badge", kwargs={"text": "New"}
        ),
        gallery.Variant(
            name="maximal",
            kwargs={
                "text": "Unread Messages",
                "theme": "danger",
                "classes": "font-bold",
            },
        ),
        gallery.Variant(
            name="status",
            label="System Status Indicator",
            description=(
                "Status pill used in admin dashboards to indicate service health."
            ),
            kwargs={"text": "Service Operational", "classes": "badge-status"},
            show_in_nav=True,
        ),
        gallery.Variant(
            name="counter",
            label="Dynamic Unread Counter",
            description=(
                "Demonstrates dynamic callable evaluation at render time "
                "instead of import time."
            ),
            kwargs={"text": lambda: "Pending Tasks (42)"},
            show_in_nav=True,
        ),
    ],
)
