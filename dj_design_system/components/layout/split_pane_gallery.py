from dj_design_system.gallery import GalleryConfig, Variant


_PANES = {
    "slot__primary": "<div class='gallery-split__pane gallery-documentation'>Docs</div>",
    "slot__secondary": "<div class='gallery-split__pane gallery-sandbox'>Sandbox</div>",
}

config = GalleryConfig(
    variants=[
        Variant(name="basic", kwargs=_PANES),
        Variant(name="maximal", kwargs=_PANES),
    ]
)
