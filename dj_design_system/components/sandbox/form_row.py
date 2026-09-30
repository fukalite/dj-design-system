from django import forms

from dj_design_system.components import TagComponent
from dj_design_system.parameters.base import JSONParam
from dj_design_system.services.media import FOUNDATION_CSS


class _FieldParam(JSONParam):
    """A bound form field, or a dict describing an example field."""

    def validate(self, value) -> None:
        if isinstance(value, dict) or isinstance(value, forms.BoundField):
            return
        raise TypeError(
            f"Expected a BoundField or an example dict but got {type(value).__name__}."
        )


def _example_field(spec: dict) -> tuple[forms.BoundField, list[str]]:
    """Build a one-field form for an example dict, so it renders a real widget."""
    name = spec["name"]
    options = {"label": name, "help_text": spec.get("help_text", ""), "required": False}
    if spec.get("choices"):
        choices = [(choice, choice) for choice in spec["choices"]]
        field: forms.Field = forms.ChoiceField(choices=choices, **options)
    else:
        field = forms.CharField(**options)
    form = type("ExampleForm", (forms.Form,), {name: field})(
        initial={name: spec.get("value")}
    )
    return form[name], list(spec.get("errors") or [])


class FormRow(TagComponent):
    """One sandbox parameter: its name and hint, its input, and any errors.

    Pass the Django ``BoundField``. The field's name labels the row and its
    help text is the hint. For an example outside a form, pass a dict with
    ``name`` and optionally ``help_text``, ``value``, ``choices`` (a select
    instead of a text input) and ``errors``.

    Example usage::

        {% for field in form %}{% dds__sandbox__form_row field %}{% endfor %}
    """

    template_name = "dj_design_system/ui/sandbox/form_row.html"

    field = _FieldParam("The BoundField, or an example dict.")

    class Meta:
        positional_args = ["field"]

    class Media:
        css = [FOUNDATION_CSS, "dj_design_system/ui/sandbox/form_row.css"]

    def get_context(self):
        context = super().get_context()
        value = self.field
        if isinstance(value, forms.BoundField):
            field, errors = value, list(value.errors)
        else:
            field, errors = _example_field(dict(value or {}))
        context.update(bound_field=field, errors=errors)
        return context
