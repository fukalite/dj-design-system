from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(name="basic", kwargs={"name": "outline"}),
        Variant(name="maximal", kwargs={"name": "measure", "pressed": True}),
    ]
)
