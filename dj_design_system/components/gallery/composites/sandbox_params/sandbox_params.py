"""Built-in sandbox parameters form composite component."""

from __future__ import annotations

import dataclasses
import typing

from django.utils import safestring

from dj_design_system import components, parameters, slots


DEFAULT_EMPTY_MESSAGE = "This component has no configurable parameters."


@dataclasses.dataclass(frozen=True)
class FormFieldRowData:
    """Normalized parameter form row for ``SandboxParams``."""

    name: str
    label: str
    field_id: str
    description: str
    required: bool
    errors: list[str]
    error: str
    has_field_html: bool
    field_html: typing.Any

    @staticmethod
    def read_field(
        raw: typing.Any,
        key: str,
        default: typing.Any = None,
    ) -> typing.Any:
        """Read *key* from a mapping or attribute from an object."""
        if isinstance(raw, dict):
            return raw.get(key, default)
        return getattr(raw, key, default)

    @classmethod
    def from_raw(cls, raw_item: typing.Any) -> FormFieldRowData:
        """Normalise a ``ParamRowData``, dict, or duck-typed row object."""
        raw_name = cls.read_field(raw_item, "name", "")
        raw_label = cls.read_field(raw_item, "label")
        raw_spec = cls.read_field(raw_item, "spec")
        raw_field = cls.read_field(raw_item, "field")
        raw_field_id = cls.read_field(raw_item, "field_id", "")
        raw_description = cls.read_field(raw_item, "description")
        raw_required = cls.read_field(raw_item, "required", False)
        raw_item_errors = cls.read_field(raw_item, "errors")

        name = str(raw_name) if raw_name is not None else ""
        label = str(raw_label) if raw_label else name
        field_id = str(
            getattr(raw_field, "id_for_label", None) or raw_field_id or f"id_{name}"
        )
        spec_desc = (
            cls.read_field(raw_spec, "description") if raw_spec is not None else None
        )
        description = str(spec_desc or raw_description or "")
        if raw_spec is not None:
            required = bool(cls.read_field(raw_spec, "required", False))
        else:
            required = bool(raw_required)

        field_errors = getattr(raw_field, "errors", None)
        raw_errors = field_errors if field_errors is not None else raw_item_errors
        if isinstance(raw_errors, str):
            errors = [raw_errors] if raw_errors else []
        elif raw_errors is not None:
            errors = [str(err) for err in raw_errors]
        else:
            errors = []
        error = " ".join(errors)

        has_field_html = raw_field is not None
        field_html: typing.Any = (
            safestring.SafeString(str(raw_field)) if has_field_html else ""
        )
        return cls(
            name=name,
            label=label,
            field_id=field_id,
            description=description,
            required=required,
            errors=errors,
            error=error,
            has_field_html=has_field_html,
            field_html=field_html,
        )

    def to_dict(self) -> dict[str, typing.Any]:
        """Return a dictionary representation for template contexts."""
        return {
            "name": self.name,
            "label": self.label,
            "field_id": self.field_id,
            "description": self.description,
            "required": self.required,
            "errors": self.errors,
            "error": self.error,
            "has_field_html": self.has_field_html,
            "field_html": self.field_html,
        }

    def __getitem__(self, key: str) -> typing.Any:
        return self.to_dict()[key]


class SandboxParams(components.BlockComponent):
    """Composite gallery component for editing component parameters in the live sandbox.

    Renders a ``<dds-sandbox-params class="dds-sandbox-params" data-surface="sandbox">``
    custom element containing an HTMX-enabled GET ``<form data-params-form>``
    when parameter rows exist, or an empty-state ``<p data-params-empty>``
    message when the component declares no configurable parameters.

    Each row in ``param_rows`` is normalised in ``get_context()`` and delegated
    to ``{% dds__form_field %}`` inside an Every Layout ``<l-stack data-params-fields>``.
    Additional hidden routing inputs can be injected via ``{% slot "extra_inputs" %}``.

    When to Use:
        - Rendering the parameter customization form in the component sandbox pane.
        - Updating live component previews dynamically on parameter field changes.
    """

    param_rows = parameters.ListParam(
        description="Parameter form row dicts with 'name', 'spec', and 'field'.",
        default=None,
        required=False,
    )
    action_url = parameters.StrParam(
        description="Form GET action URL (and hx-get URL).",
        default="",
        required=False,
    )
    hx_target = parameters.StrParam(
        description="Optional HTMX target selector for live sandbox swaps.",
        default="",
        required=False,
    )
    empty_message = parameters.StrParam(
        description="Message displayed when the component has no editable parameters.",
        default=DEFAULT_EMPTY_MESSAGE,
        required=False,
    )

    class Meta:
        positional_args = ["param_rows"]
        slots = {
            "extra_inputs": slots.Slot(
                required=False,
                description=(
                    "Optional extra hidden or control inputs rendered inside "
                    "the form before parameter fields."
                ),
            ),
        }

    def get_context(self) -> dict[str, typing.Any]:
        """Build the normalised template context for the sandbox parameters form.

        Returns:
            Dictionary containing ``param_rows``, ``normalized_rows``,
            ``has_rows``, ``action_url``, ``has_action_url``, ``hx_target``,
            ``has_hx_target``, ``extra_inputs``, and ``empty_message``.
        """
        context = super().get_context()
        raw_rows = list(self.param_rows) if self.param_rows is not None else []
        normalized_rows: list[dict[str, typing.Any]] = [
            FormFieldRowData.from_raw(raw_item).to_dict() for raw_item in raw_rows
        ]

        has_rows = bool(normalized_rows)
        action_url = self.action_url or ""
        has_action_url = bool(action_url)
        hx_target = self.hx_target or ""
        has_hx_target = bool(hx_target)
        empty_message = self.empty_message or DEFAULT_EMPTY_MESSAGE

        context["param_rows"] = normalized_rows
        context["normalized_rows"] = normalized_rows
        context["has_rows"] = has_rows
        context["action_url"] = action_url
        context["has_action_url"] = has_action_url
        context["hx_target"] = hx_target
        context["has_hx_target"] = has_hx_target
        context["empty_message"] = empty_message
        return context

