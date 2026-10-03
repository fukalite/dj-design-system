from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(
            name="basic",
            kwargs={
                "slot__sidebar": '<aside class="gallery-sidebar">Sidebar</aside>',
                "slot__content": "<p>Content</p>",
            },
        ),
        Variant(
            name="maximal",
            kwargs={
                "slot__sidebar": '<aside class="gallery-sidebar">Sidebar</aside>',
                "slot__toolbar": '<div class="gallery-toolbar">Toolbar</div>',
                "slot__content": "<p>Content</p>",
            },
        ),
    ]
)
