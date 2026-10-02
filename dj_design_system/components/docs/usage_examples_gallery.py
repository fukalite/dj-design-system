from dj_design_system.gallery import GalleryConfig, Variant


_BLOCK = '<div class="gallery-usage__block"><p>{}</p></div>'

config = GalleryConfig(
    variants=[
        Variant(name="basic", kwargs={"content": _BLOCK.format("Minimal example")}),
        Variant(
            name="maximal",
            kwargs={
                "content": _BLOCK.format("Minimal example")
                + _BLOCK.format("Bigger example")
            },
        ),
    ]
)
