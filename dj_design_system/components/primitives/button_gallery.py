from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(name="basic", kwargs={"content": "Responsive"}),
        Variant(
            name="maximal",
            kwargs={
                "content": "Toggle outline",
                "variant": "toolbar",
                "active": True,
                "pressed": True,
                "title": "Toggle outline",
                "expanded": False,
                "controls": "gallery-bg-panel",
                "extra_classes": "",
            },
        ),
    ]
)
