from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(
            name="basic",
            kwargs={
                "items": [
                    {"id": "gallery-tab-docs", "label": "Documentation"},
                    {"id": "gallery-tab-sandbox", "label": "Sandbox"},
                ]
            },
        ),
        Variant(
            name="maximal",
            kwargs={
                "items": [
                    {"id": "gallery-tab-docs", "label": "Documentation"},
                    {"id": "gallery-tab-sandbox", "label": "Sandbox"},
                ],
                "checked": "gallery-tab-sandbox",
                "label": "Documentation and Sandbox view switcher",
            },
        ),
    ]
)
