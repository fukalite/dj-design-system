from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(name="basic", kwargs={"text": "Usage"}),
        Variant(
            name="maximal",
            kwargs={"text": "Minimal example", "level": 4, "variant": "sub"},
        ),
    ]
)
