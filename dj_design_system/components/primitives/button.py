from django.utils.html import format_html_join

from dj_design_system.components import BlockComponent
from dj_design_system.parameters import BoolParam, DictParam, StrParam
from dj_design_system.services.media import FOUNDATION_CSS


#: Variant -> BEM class. Modifiers such as ``--active`` hang off this class.
VARIANT_CLASSES = {
    "toolbar": "gallery-sandbox-toolbar__btn",
    "option": "gallery-sandbox-toolbar__popout-option",
}


class Button(BlockComponent):
    """A plain ``<button type="button">`` for gallery controls.

    The ``toolbar`` variant is the bordered sandbox toolbar button; ``option``
    is a row in a toolbar popout menu. ARIA state is only rendered when set,
    so a toggle button passes ``pressed`` and a disclosure button passes
    ``expanded`` and ``controls``. Scripts that toggle the state should keep
    the ``--active`` modifier and the ARIA attribute in step.

    Example usage::

        {% dds__primitives__button pressed=False title="Toggle outline" %}
            {% dds__primitives__icon "box-model" %}
        {% enddds__primitives__button %}
    """

    template_name = "dj_design_system/ui/primitives/button.html"

    variant = StrParam(
        "Visual style.",
        required=False,
        default="toolbar",
        choices=list(VARIANT_CLASSES),
    )
    active = BoolParam(
        "Render the variant's ``--active`` modifier.", required=False, default=False
    )
    pressed = BoolParam(
        "Toggle state, rendered as ``aria-pressed``. Leave unset for a"
        " button that isn't a toggle.",
        required=False,
    )
    expanded = BoolParam(
        "Disclosure state, rendered as ``aria-expanded``.", required=False
    )
    controls = StrParam(
        "ID of the element this button controls, rendered as ``aria-controls``.",
        required=False,
    )
    title = StrParam("Tooltip text.", required=False)
    extra_classes = StrParam(
        "Extra CSS classes, e.g. a hook for scripts.", required=False
    )
    attrs = DictParam(
        "Extra HTML attributes, e.g. ``{'data-zoom': '50'}``. Values are escaped.",
        required=False,
    )

    class Media:
        css = [FOUNDATION_CSS, "dj_design_system/ui/primitives/button.css"]

    def get_context(self):
        context = super().get_context()
        base = VARIANT_CLASSES[str(self.variant)]
        classes = [base]
        if self.active:
            classes.append(f"{base}--active")
        if self.extra_classes:
            classes.append(self.extra_classes)
        context["button_classes"] = " ".join(classes)
        context["extra_attrs"] = format_html_join(
            "", ' {}="{}"', (self.attrs or {}).items()
        )
        return context
