from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(
            name="basic",
            kwargs={
                "field": {
                    "name": "label",
                    "help_text": "The button label.",
                    "value": "Save",
                }
            },
        ),
        Variant(
            name="maximal",
            kwargs={
                "field": {
                    "name": "variant",
                    "help_text": "Visual style.",
                    "value": "danger",
                    "choices": ["primary", "secondary", "danger"],
                    "errors": ["Danger buttons need a confirmation step."],
                }
            },
        ),
    ]
)
