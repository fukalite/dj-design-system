from dj_design_system.gallery import GalleryConfig, Variant


_BODY = "<p>The variant's example goes here.</p>"

config = GalleryConfig(
    variants=[
        Variant(name="basic", kwargs={"label": "Critical", "slot__body": _BODY}),
        Variant(
            name="maximal",
            kwargs={
                "label": "Security outage alert",
                "slot__description": "<p>High-severity alert for an outage.</p>",
                "slot__body": _BODY,
            },
        ),
    ]
)
