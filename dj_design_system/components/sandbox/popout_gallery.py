from dj_design_system.gallery import GalleryConfig, Variant


_OPTION = '<button class="gallery-sandbox-toolbar__popout-option gallery-sandbox-toolbar__zoom-btn{active}" type="button" data-zoom="{zoom}" title="Zoom {zoom}%">{zoom}%</button>'
config = GalleryConfig(
    variants=[
        Variant(
            name="basic",
            kwargs={
                "panel_id": "example-zoom-panel",
                "panel_name": "zoom",
                "title": "Zoom level",
                "slot__toggle": "100%",
                "slot__options": _OPTION.format(zoom="50", active="")
                + _OPTION.format(
                    zoom="100", active=" gallery-sandbox-toolbar__popout-option--active"
                ),
            },
        ),
        Variant(
            name="maximal",
            kwargs={
                "panel_id": "example-zoom-panel",
                "panel_name": "zoom",
                "title": "Zoom level",
                "toggle_class": "gallery-sandbox-toolbar__zoom-toggle",
                "slot__toggle": '<span class="gallery-sandbox-toolbar__zoom-value">100%</span>',
                "slot__options": "".join(
                    (
                        _OPTION.format(
                            zoom=zoom,
                            active=" gallery-sandbox-toolbar__popout-option--active"
                            if zoom == "100"
                            else "",
                        )
                        for zoom in ["50", "75", "100", "125", "150", "200"]
                    )
                ),
            },
        ),
    ]
)
