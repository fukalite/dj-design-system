from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(
            name="basic",
            kwargs={
                "crumbs": [{"label": "Gallery", "url": "/"}, {"label": "Components"}]
            },
        ),
        Variant(
            name="maximal",
            kwargs={
                "crumbs": [
                    {"label": "Gallery", "url": "/"},
                    {"label": "Demo Nav", "url": "/demo_nav/"},
                    {"label": "Elements", "url": "/demo_nav/elements/"},
                    {"label": "Icon"},
                ]
            },
        ),
    ]
)
