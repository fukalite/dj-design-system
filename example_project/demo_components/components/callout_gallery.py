from django.utils.safestring import mark_safe

from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(
            name="basic",
            kwargs={"slot__message": "Your changes have been saved."},
        ),
        # Deliberately leaves the optional "actions" slot empty: the maximal
        # usage example should show the callout without it.
        Variant(
            name="maximal",
            kwargs={
                "title": "Trial ending soon",
                "tone": "warning",
                "slot__message": "Your free trial ends in 3 days.",
            },
        ),
        Variant(
            name="with_actions",
            label="With Actions",
            description="Fills the optional actions slot with a call to action.",
            kwargs={
                "title": "Trial ending soon",
                "tone": "warning",
                "slot__message": "Your free trial ends in 3 days.",
                "slot__actions": mark_safe("<a href='#'>Upgrade now</a>"),
            },
        ),
    ],
)
