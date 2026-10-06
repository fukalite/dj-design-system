from django.template.loader import render_to_string

from dj_design_system.components import TagComponent
from dj_design_system.components.primitives.table import Table
from dj_design_system.parameters import ListParam
from dj_design_system.parameters.base import _get_type_name
from dj_design_system.services.media import FOUNDATION_CSS


_FIELDS = ("type_name", "required", "default", "choices", "description")


def _row(entry) -> dict:
    if isinstance(entry, dict):
        return {"name": entry["name"], **{f: entry.get(f) for f in _FIELDS}}
    name, spec = entry
    row = {"name": name, **{f: getattr(spec, f, None) for f in _FIELDS}}
    if not row["type_name"]:
        row["type_name"] = _get_type_name(getattr(spec, "type", type(spec)))
    return row


class ParamsTable(TagComponent):
    """A component's parameters: name, type, required, default, choices and description.

    Pass ``(name, spec)`` pairs, as the gallery's component view provides,
    or dicts with ``name``, ``type_name``, ``required``, ``default``,
    ``choices`` and ``description``. With none it says the component has no
    parameters.

    Example usage::

        {% dds__docs__params_table params %}
    """

    template_name = "dj_design_system/ui/docs/params_table.html"

    parameters = ListParam("The parameters, as (name, spec) pairs or dicts.")

    class Meta:
        positional_args = ["parameters"]

    class Media:
        css = [FOUNDATION_CSS, "dj_design_system/ui/primitives/table.css"]

    def get_context(self):
        context = super().get_context()
        rows = [_row(entry) for entry in self.parameters or []]
        if rows:
            context["table"] = Table(
                slots={
                    "head": render_to_string(
                        "dj_design_system/ui/docs/params_table_head.html"
                    ),
                    "body": render_to_string(
                        "dj_design_system/ui/docs/params_table_rows.html",
                        {"rows": rows},
                    ),
                }
            ).render()
        return context
