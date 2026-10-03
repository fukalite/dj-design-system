from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(
            name="basic", kwargs={"data_name": "zoom", "value": "50", "content": "50%"}
        ),
        Variant(
            name="maximal",
            kwargs={
                "data_name": "viewport",
                "value": "320",
                "active": True,
                "title": "Small mobile (320px)",
                "extra_classes": "gallery-sandbox-toolbar__viewport-btn",
                "content": "Small mobile — 320px",
            },
        ),
    ]
)
