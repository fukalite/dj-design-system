"""Form field wrapper component providing label, control slot, description, and error state."""

import typing

from dj_design_system import components, parameters, slots


LAYOUT_STACKED = "stacked"
LAYOUT_INLINE = "inline"
LAYOUT_CHOICES: tuple[str, ...] = (LAYOUT_STACKED, LAYOUT_INLINE)


class FormField(components.BlockComponent):
    """Wrap a form control widget with a label, optional helper description, and validation error.

    Use ``{% dds__form_field %}`` to give native HTML inputs, selects, and textareas
    consistent label typography, spacing, focus outlines, and accessible error
    messaging backed by Tier 2 ``--dds-control-*`` and ``--dds-status-error-*``
    tokens. Pass the control markup via ``{% slot "control" %}`` (or as default
    block content when instantiating in Python).
    """

    label = parameters.StrParam(description="Field label text.")
    field_id = parameters.StrParam(
        description="HTML id of the associated form control.",
        default="",
        required=False,
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
    required_field = parameters.BoolParam(
        description="Whether the field is required.",
        default=False,
        required=False,
    )
    layout = parameters.StrParam(
        description="Label/control layout.",
        default=LAYOUT_STACKED,
        required=False,
        choices=list(LAYOUT_CHOICES),
    )

    class Meta:
        positional_args = ["label"]
        slots = {
            "control": slots.Slot(
                required=False,
                description="Form control widget markup (falls back to default block content if omitted).",
            ),
        }

    def get_context(self) -> dict[str, typing.Any]:
        """Build template context with pre-computed boolean flags and slot fallbacks.

        Returns:
            Dictionary of template context variables for ``form_field.html``.
        """
        context = super().get_context()
        context["slots"] = self.slots
        context["content"] = self.content or ""
        context["has_field_id"] = bool(self.field_id)
        context["has_description"] = bool(self.description)
        context["has_error"] = bool(self.error)
        context["is_inline"] = self.layout == LAYOUT_INLINE
        return context
