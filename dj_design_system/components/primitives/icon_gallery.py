from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(name="basic", kwargs={"name": "external-link"}),
        Variant(
            name="maximal",
            kwargs={"name": "folder-open", "size": 32, "extra_classes": ""},
        ),
    ]
)
