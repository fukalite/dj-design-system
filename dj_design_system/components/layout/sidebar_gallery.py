from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(
            name="basic",
            kwargs={
                "title": "Example Component Library",
                "title_url": "/",
                "slot__nav": "<nav class='gallery-nav'></nav>",
            },
        ),
        Variant(
            name="maximal",
            kwargs={
                "title": "Example Component Library",
                "title_url": "/",
                "slot__search": "<div class='gallery-sidebar__search'>Search</div>",
                "slot__nav": "<nav class='gallery-nav'></nav>",
            },
        ),
    ]
)
