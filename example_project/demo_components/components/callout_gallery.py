from dj_design_system import gallery


config = gallery.GalleryConfig(
    variants=[
        gallery.Variant(
            name="basic",
            kwargs={"slot__message": "Your changes have been saved."},
        ),
        gallery.Variant(
            name="maximal",
            kwargs={
                "tone": "warning",
                "slot__message": "Your free trial ends in 3 days.",
            },
        ),
        gallery.Variant(
            name="with_actions",
            label="With Actions",
            description="Fills the optional actions slot with a call to action.",
            kwargs={
                "title": "Trial ending soon",
                "tone": "warning",
                "slot__message": "Your free trial ends in 3 days.",
                "slot__actions": '<a href="#">Upgrade now</a>',
            },
        ),
    ],
)
