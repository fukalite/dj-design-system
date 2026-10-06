from dj_design_system.components import BlockComponent
from dj_design_system.parameters import StrParam
from dj_design_system.services.media import FOUNDATION_CSS


class ParamsForm(BlockComponent):
    """The sandbox's parameter form, in a drawer that can be resized.

    The content is the form's rows (``FormRow``). Changing a field reloads
    the sandbox with HTMX: the form requests ``url`` with the fields as GET
    parameters and swaps the result into the nearest
    ``[data-gallery-sandbox-body]``. ``theme`` and, on a variant's page,
    ``active_variant`` are sent along as hidden fields. Drag the bar at the
    top of the drawer, or focus it and use the arrow keys, to resize it.

    Example usage::

        {% dds__sandbox__params_form url=request.path theme=active_theme active_variant=active_variant.name %}
            {% for field in form %}{% dds__sandbox__form_row field %}{% endfor %}
        {% enddds__sandbox__params_form %}
    """

    template_name = "dj_design_system/ui/sandbox/params_form.html"

    url = StrParam("Where the form sends its GET request: the component page.")
    theme = StrParam(
        "The active theme, sent as a hidden field.", required=False, default=""
    )
    active_variant = StrParam(
        "The active gallery variant's name, sent as a hidden field.",
        required=False,
        default="",
    )

    class Media:
        # form_row.css: the content is FormRows.
        css = [
            FOUNDATION_CSS,
            "dj_design_system/ui/sandbox/form_row.css",
            "dj_design_system/ui/sandbox/params_form.css",
        ]
        js = "dj_design_system/ui/sandbox/params_form.js"
