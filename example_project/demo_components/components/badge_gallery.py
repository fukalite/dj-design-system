from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(name="basic", kwargs={"text": "New"}),
        Variant(
            name="maximal",
            kwargs={
                "text": "Unread Messages",
                "theme": "danger",
                "classes": "font-bold",
            },
        ),
    ]
)
