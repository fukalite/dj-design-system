from dj_design_system.gallery import GalleryConfig, Variant


_HEAD = "<tr><th>Name</th><th>Type</th><th>Description</th></tr>"
_ROW = "<tr><td><code>{}</code></td><td><code>{}</code></td><td>{}</td></tr>"
config = GalleryConfig(
    variants=[
        Variant(
            name="basic",
            kwargs={"slot__body": _ROW.format("label", "str", "The button label.")},
        ),
        Variant(
            name="maximal",
            kwargs={
                "slot__head": _HEAD,
                "slot__body": _ROW.format("label", "str", "The button label.")
                + _ROW.format("variant", "str", "Visual style."),
            },
        ),
    ]
)
