from dj_design_system.components import TagComponent
from dj_design_system.components.primitives.icon import ICON_NAMES, Icon
from dj_design_system.parameters import StrParam
from dj_design_system.services.media import FOUNDATION_CSS


#: Variant -> BEM class.
VARIANT_CLASSES = {
    "overlay": "gallery-doc-preview__sandbox-link",
}


class IconButton(TagComponent):
    """A small round icon-only control.

    Renders an ``<a>`` when ``href`` is given, otherwise a
    ``<button type="button">``. The icon is decorative, so ``label`` is
    required: it becomes both the tooltip and the accessible name.

    The ``overlay`` variant is the pill that sits over a documentation
    preview and fades in when the preview is hovered.

    Example usage::

        {% dds__primitives__icon_button "external-link" "Open in sandbox" href="#pane-sandbox" %}
    """

    template_name = "dj_design_system/ui/primitives/icon_button.html"

    icon = StrParam("Which icon to draw.", choices=ICON_NAMES)
    label = StrParam("Accessible name and tooltip. Required.")
    href = StrParam(
        "Link target. Renders an ``<a>`` instead of a button.", required=False
    )
    variant = StrParam(
        "Visual style.",
        required=False,
        default="overlay",
        choices=list(VARIANT_CLASSES),
    )
    extra_classes = StrParam("Extra CSS classes.", required=False)

    class Meta:
        positional_args = ["icon", "label"]

    class Media:
        css = [
            FOUNDATION_CSS,
            "dj_design_system/ui/primitives/icon.css",
            "dj_design_system/ui/primitives/icon_button.css",
        ]

    def validate_params(self) -> None:
        if not self.label:
            raise ValueError("IconButton requires a non-empty 'label'.")

    def get_context(self):
        context = super().get_context()
        classes = [VARIANT_CLASSES[str(self.variant)]]
        if self.extra_classes:
            classes.append(self.extra_classes)
        context["button_classes"] = " ".join(classes)
        context["icon_html"] = Icon(name=self.icon).render()
        return context
