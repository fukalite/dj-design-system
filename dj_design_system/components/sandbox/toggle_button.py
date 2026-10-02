from dj_design_system.components import TagComponent
from dj_design_system.components.primitives.button import Button
from dj_design_system.components.primitives.icon import Icon
from dj_design_system.parameters import BoolParam, StrParam
from dj_design_system.services.media import FOUNDATION_CSS


#: Toggle name -> (icon, tooltip).
TOGGLES = {
    "outline": ("box-model", "Toggle box model outline"),
    "measure": ("ruler", "Toggle measurement overlay on hover"),
    "rtl": ("rtl", "Toggle right-to-left direction"),
}


class ToggleButton(TagComponent):
    """A sandbox toolbar button that switches an effect on the canvas.

    ``outline`` outlines each element's box, ``measure`` shows an element's
    margin, padding and size on hover, and ``rtl`` sets the canvas's text
    direction to right-to-left. The button shows its state with
    ``aria-pressed``.

    Example usage::

        {% dds__sandbox__toggle_button "outline" %}
    """

    template_name = "dj_design_system/ui/sandbox/toggle_button.html"

    name = StrParam("Which effect the button toggles.", choices=list(TOGGLES))
    pressed = BoolParam("Whether the effect is on.", required=False, default=False)

    class Meta:
        positional_args = ["name"]

    class Media:
        # sandbox_toolbar.css: the toolbar group the button sits in.
        css = [
            FOUNDATION_CSS,
            "dj_design_system/ui/primitives/icon.css",
            "dj_design_system/ui/primitives/button.css",
            "dj_design_system/ui/sandbox/sandbox_toolbar.css",
            "dj_design_system/ui/sandbox/toggle_button.css",
        ]
        js = "dj_design_system/ui/sandbox/toggle_button.js"

    def get_context(self):
        context = super().get_context()
        icon, title = TOGGLES[str(self.name)]
        context["button"] = Button(
            content=Icon(name=icon).render(),
            pressed=bool(self.pressed),
            active=bool(self.pressed),
            title=title,
            extra_classes=f"gallery-sandbox-toolbar__{self.name}-toggle",
        ).render()
        return context
