from dj_design_system.data import GalleryParameter
from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    order=5,
    variants=[
        Variant(
            name="basic",
            label="Simple Quote",
            kwargs={
                "quote": "To be or not to be",
                "slot__author": "William Shakespeare",
            },
        ),
        Variant(
            name="maximal",
            label="Attributed Literature Quote",
            kwargs={
                "quote": "To be or not to be, that is the question.",
                "slot__author": GalleryParameter(
                    value="<strong>William Shakespeare</strong>",
                    code='"<strong>William Shakespeare</strong>"',
                ),
                "slot_source": GalleryParameter(
                    value="<cite>Hamlet</cite>", code='"<cite>Hamlet</cite>"'
                ),
            },
        ),
        Variant(
            name="featured",
            label="Hero Editorial Callout",
            description="Editorial quote formatted within an artistic framed container block.",
            kwargs={
                "quote": "Design is not just what it looks like and feels like. Design is how it works.",
                "slot__author": "Steve Jobs",
                "slot__source": "The New York Times",
            },
            canvas_template="""
<div style="max-width: 650px; margin: 2rem auto; padding: 2.5rem; background: #fafaf9; border-left: 6px solid #e11d48; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); font-family: Georgia, serif;">
    {{ component }}
</div>
""",
            show_in_nav=True,
        ),
    ],
)
