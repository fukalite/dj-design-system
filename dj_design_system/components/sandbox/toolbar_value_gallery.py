from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(name="basic", kwargs={"name": "zoom", "text": "100%"}),
        Variant(name="maximal", kwargs={"name": "viewport", "text": "Tablet — 768px"}),
    ]
)
