from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(name="basic", kwargs={"title": "Cards"}),
        Variant(
            name="maximal",
            kwargs={
                "title": "Example Component Library",
                "content": "<p>Browse the component library using the sidebar.</p>",
            },
        ),
    ]
)
