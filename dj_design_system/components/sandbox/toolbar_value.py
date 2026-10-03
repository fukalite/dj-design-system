from dj_design_system.components import TagComponent
from dj_design_system.parameters import StrParam
from dj_design_system.services.media import FOUNDATION_CSS


#: The toolbar popouts whose toggle shows their current value.
VALUE_NAMES = ["viewport", "zoom"]


class ToolbarValue(TagComponent):
    """The current value shown on a sandbox toolbar popout's button.

    ``name`` is the popout (``viewport`` or ``zoom``); the toolbar's script
    updates the ``text`` when an option is chosen.

    Example usage::

        {% dds__sandbox__toolbar_value "zoom" "100%" %}
    """

    template_name = "dj_design_system/ui/sandbox/toolbar_value.html"

    name = StrParam("Which popout's value this is.", choices=VALUE_NAMES)
    text = StrParam("The value to show.")

    class Meta:
        positional_args = ["name", "text"]

    class Media:
        css = [FOUNDATION_CSS, "dj_design_system/ui/sandbox/toolbar_value.css"]
