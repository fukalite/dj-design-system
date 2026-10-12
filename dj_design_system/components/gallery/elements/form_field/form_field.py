"""Form field wrapper component providing label, block content, description, and error state."""

import typing

from dj_design_system import components, parameters


LAYOUT_STACKED = "stacked"
LAYOUT_INLINE = "inline"
LAYOUT_CHOICES: tuple[str, ...] = (LAYOUT_STACKED, LAYOUT_INLINE)


class FormField(components.BlockComponent):
    """Wrap a form control widget with a label, optional helper description, and validation error.

    Use ``{% dds__form_field %}`` to give native HTML inputs, selects, and textareas
    consistent label typography, spacing, focus outlines, and accessible error
    messaging backed by Tier 2 ``--dds-control-*`` and ``--dds-status-error-*``
    tokens. Pass the control markup as the component block content.
    """

    label = parameters.StrParam(description="Field label text.")
    field_id = parameters.StrParam(
        description="HTML id of the associated form control. Fallback ID auto-generated for description and error linkage if omitted.",
        default="",
        required=False,
    )
    required = parameters.BoolParam(
        description="Whether the field is required.",
        default=False,
        required=False,
    )
    required_field = parameters.BoolParam(
        description="Deprecated alias for required.",
        default=False,
        required=False,
    )
    layout = parameters.StrParam(
        description="Label/control layout.",
        default=LAYOUT_STACKED,
        required=False,
        choices=list(LAYOUT_CHOICES),
        data_attr=True,
    )
    description = parameters.StrParam(
        description="Optional helper description text.",
        default="",
        required=False,
    )
    error = parameters.StrParam(
        description="Optional validation error message.",
        default="",
        required=False,
    )

    class Meta:
        positional_args = ["label"]

    def get_context(self) -> dict[str, typing.Any]:
        """Build template context with pre-computed boolean flags and IDs.

        Returns:
            Dictionary of template context variables for ``form_field.html``.
        """
        context = super().get_context()
        resolved_id = self.field_id or f"dds-field-{abs(id(self))}"
        is_required = (
            self.required
            if self.required_field is None
            else bool(self.required or self.required_field)
        )
        has_description = bool(self.description)
        has_error = bool(self.error)

        context["content"] = self.content or ""
        context["field_id"] = self.field_id
        context["resolved_id"] = resolved_id
        context["description_id"] = (
            f"{resolved_id}-description" if has_description else ""
        )
        context["error_id"] = f"{resolved_id}-error" if has_error else ""
        context["has_field_id"] = bool(self.field_id)
        context["has_description"] = has_description
        context["has_error"] = has_error
        context["is_inline"] = self.layout == LAYOUT_INLINE
        context["required"] = is_required
        context["required_field"] = is_required
        context["description"] = self.description or ""
        context["error"] = self.error or ""
        return context
