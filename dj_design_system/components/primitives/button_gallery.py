from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(name="basic", kwargs={}),
        Variant(
            name="maximal",
            kwargs={
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
