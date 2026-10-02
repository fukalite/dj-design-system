from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(
            name="basic",
            kwargs={
                "themes": [
                    {"value": "default", "label": "Default"},
                    {"value": "dark", "label": "Dark"},
                ],
                "active": "default",
            },
        ),
        Variant(
            name="maximal",
            kwargs={
                "themes": [
                    {"value": "default", "label": "Default"},
                    {"value": "dark", "label": "Dark"},
                    {"value": "high_contrast", "label": "High contrast"},
                ],
                "active": "dark",
            },
        ),
    ]
)
