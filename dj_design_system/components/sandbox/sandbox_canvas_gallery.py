from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(name="basic", kwargs={"content": "<p>The sandbox canvas.</p>"}),
        Variant(name="maximal", kwargs={"content": "<p>The sandbox canvas.</p>"}),
    ]
)
