from dj_design_system.gallery import GalleryConfig, Variant


_GROUP = '<div class="gallery-sandbox-toolbar__group"><button class="gallery-sandbox-toolbar__btn {hook}" type="button" aria-pressed="false" title="{title}">{label}</button></div>'
config = GalleryConfig(
    variants=[
        Variant(
            name="basic",
            kwargs={
                "content": _GROUP.format(
                    hook="gallery-sandbox-toolbar__outline-toggle",
                    title="Toggle box model outline",
                    label="Outline",
                )
            },
        ),
        Variant(
            name="maximal",
            kwargs={
                "content": '<div class="gallery-sandbox-toolbar__group gallery-sandbox-toolbar__zoom"><button class="gallery-sandbox-toolbar__btn gallery-sandbox-toolbar__zoom-toggle" type="button" aria-expanded="false" aria-controls="example-zoom-panel" title="Zoom level"><span class="gallery-sandbox-toolbar__zoom-value">100%</span></button><div class="gallery-sandbox-toolbar__popout" id="example-zoom-panel" data-gallery-panel="zoom" hidden><button class="gallery-sandbox-toolbar__popout-option gallery-sandbox-toolbar__zoom-btn gallery-sandbox-toolbar__popout-option--active" type="button" data-zoom="100" title="Zoom 100%">100%</button></div></div>'
                + "".join(
                    (
                        _GROUP.format(
                            hook=f"gallery-sandbox-toolbar__{name}-toggle",
                            title=title,
                            label=label,
                        )
                        for name, title, label in [
                            ("outline", "Toggle box model outline", "Outline"),
                            (
                                "measure",
                                "Toggle measurement overlay on hover",
                                "Measure",
                            ),
                            ("rtl", "Toggle right-to-left direction", "RTL"),
                        ]
                    )
                )
            },
        ),
    ]
)
