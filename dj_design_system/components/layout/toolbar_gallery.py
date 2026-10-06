from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(name="basic", kwargs={"slot__start": "<a href='/'>Gallery</a>"}),
        Variant(
            name="maximal",
            kwargs={
                "slot__start": "<a href='/'>Gallery</a> / Components",
                "slot__actions": "<span>Actions</span>",
            },
        ),
    ]
)
