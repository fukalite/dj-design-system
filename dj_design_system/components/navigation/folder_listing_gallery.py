from dj_design_system.gallery import GalleryConfig, Variant


_ITEMS = [
    {"type": "folder", "label": "Cards", "url": "/cards/", "children": [{}]},
    {"type": "component", "label": "Alert", "url": "/alert/"},
    {"type": "document", "label": "Guidelines", "url": "/guidelines/"},
]
config = GalleryConfig(
    variants=[
        Variant(name="basic", kwargs={"items": _ITEMS}),
        Variant(name="maximal", kwargs={"items": _ITEMS, "title": "Contents"}),
    ]
)
