from dj_design_system.data import GalleryParameter
from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(
            name="basic",
            kwargs={
                "quote": "To be or not to be",
                "slot_author": "William Shakespeare",
            },
        ),
        Variant(
            name="maximal",
            kwargs={
                "quote": "To be or not to be, that is the question.",
                "slot_author": GalleryParameter(
                    value="<strong>William Shakespeare</strong>",
                    code='"<strong>William Shakespeare</strong>"',
                ),
                "slot_source": GalleryParameter(
                    value="<cite>Hamlet</cite>", code='"<cite>Hamlet</cite>"'
                ),
            },
        ),
    ]
)
