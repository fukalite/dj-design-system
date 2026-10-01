from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(name="basic", kwargs={"title": "Documentation"}),
        Variant(
            name="maximal",
            kwargs={
                "title": "Sandbox",
                "pane_id": "pane-sandbox",
                "variant": "sandbox",
                "body_classes": "",
            },
        ),
    ]
)
