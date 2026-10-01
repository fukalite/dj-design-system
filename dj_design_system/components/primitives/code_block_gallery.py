from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(name="basic", kwargs={"content": "total = price * quantity"}),
        Variant(
            name="maximal",
            kwargs={
                "language": "python",
                "content": "def total(price, quantity):\n    return price * quantity",
            },
        ),
    ]
)
