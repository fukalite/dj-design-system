from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(
            name="basic",
            kwargs={
                "variant": "warning",
                "content": "<p>Components must be registered before use.</p>",
            },
        ),
        Variant(
            name="maximal",
            kwargs={
                "variant": "hint",
                "snapshot": False,
                "content": "<p>Add an <code>index.md</code> file to this folder.</p>",
            },
        ),
    ]
)
