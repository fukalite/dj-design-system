_ROW = (
    '<div class="gallery-params-form__row">'
    '<label class="gallery-params-form__label" for="id_{name}"><code>{name}</code>'
    '<span class="gallery-params-form__hint">{hint}</span></label>'
    '<div class="gallery-params-form__field">'
    '<input type="text" name="{name}" value="{value}" id="id_{name}"></div></div>'
)

basic_kwargs = {
    "url": "#",
    "content": _ROW.format(name="label", hint="The button label.", value="Save"),
}

maximal_kwargs = {
    "url": "#",
    "theme": "dark",
    "content": _ROW.format(name="label", hint="The button label.", value="Save")
    + _ROW.format(name="size", hint="Button size.", value="large"),
}
