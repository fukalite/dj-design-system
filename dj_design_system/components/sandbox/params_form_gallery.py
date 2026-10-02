from dj_design_system.gallery import GalleryConfig, Variant


_ROW = '<div class="gallery-params-form__row"><label class="gallery-params-form__label" for="id_{name}"><code>{name}</code><span class="gallery-params-form__hint">{hint}</span></label><div class="gallery-params-form__field"><input type="text" name="{name}" value="{value}" id="id_{name}"></div></div>'
config = GalleryConfig(
    variants=[
        Variant(
            name="basic",
            kwargs={
                "url": "#",
                "content": _ROW.format(
                    name="label", hint="The button label.", value="Save"
                ),
            },
        ),
        Variant(
            name="maximal",
            kwargs={
                "url": "#",
                "theme": "dark",
                "content": _ROW.format(
                    name="label", hint="The button label.", value="Save"
                )
                + _ROW.format(name="size", hint="Button size.", value="large"),
            },
        ),
    ]
)
