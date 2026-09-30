from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    order=2,
    variants=[
        Variant(name="basic", label="Default Badge", kwargs={"text": "New"}),
        Variant(
            name="maximal",
            kwargs={
                "text": "Unread Messages",
                "theme": "danger",
                "classes": "font-bold",
            },
        ),
        Variant(
            name="status",
            label="System Status Indicator",
            description="Status pill used in admin dashboards to indicate service health.",
            kwargs={"text": "Service Operational", "classes": "badge-status"},
            show_in_nav=True,
        ),
        Variant(
            name="counter",
            label="Dynamic Unread Counter",
            description="Demonstrates dynamic callable evaluation at render time instead of import time.",
            kwargs={"text": lambda: "Pending Tasks (42)"},
            show_in_nav=True,
        ),
    ],
)
