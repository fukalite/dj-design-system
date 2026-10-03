from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(name="basic", kwargs={}),
        Variant(name="maximal", kwargs={"value": "dark-grey", "label": "Dark grey"}),
    ]
)
