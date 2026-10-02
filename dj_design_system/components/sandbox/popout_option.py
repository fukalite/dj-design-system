from dj_design_system.components import BlockComponent
from dj_design_system.components.primitives.button import Button
from dj_design_system.parameters import BoolParam, StrParam
from dj_design_system.services.media import FOUNDATION_CSS


class PopoutOption(BlockComponent):
    """One choice in a ``Popout``'s panel.

    The option carries its value as a data attribute named by
    ``data_name``, e.g. ``data_name="zoom" value="50"`` renders
    ``data-zoom="50"``; scripts read it when the option is chosen.

    Example usage::

        {% dds__sandbox__popout_option data_name="zoom" value="50" active=True %}
            50%
        {% enddds__sandbox__popout_option %}
    """

    template_name = "dj_design_system/ui/sandbox/popout_option.html"

    data_name = StrParam("Name of the data attribute, e.g. ``zoom``.")
    value = StrParam("The option's value.")
    active = BoolParam(
        "Whether this is the current choice.", required=False, default=False
    )
    title = StrParam("Tooltip text.", required=False)
    extra_classes = StrParam(
        "Extra CSS classes, e.g. a hook for scripts.", required=False, default=""
    )

    class Media:
        css = [FOUNDATION_CSS, "dj_design_system/ui/primitives/button.css"]

    def get_context(self):
        context = super().get_context()
        context["option"] = Button(
            content=self.content,
            variant="option",
            active=self.active,
            title=self.title,
            extra_classes=self.extra_classes,
            attrs={f"data-{self.data_name}": self.value},
        ).render()
        return context
