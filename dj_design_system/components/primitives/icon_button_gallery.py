from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(
            name="basic", kwargs={"icon": "external-link", "label": "Open in sandbox"}
        ),
        Variant(
            name="maximal",
            kwargs={
                "icon": "external-link",
                "label": "Open in sandbox",
                "href": "#pane-sandbox",
                "variant": "overlay",
                "extra_classes": "",
            },
        ),
    ]
)
