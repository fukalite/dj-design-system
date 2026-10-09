"""Built-in parameters table domain component."""

import typing

from dj_design_system import components, data, parameters


DEFAULT_EMPTY_MESSAGE = "This component has no parameters."
DEFAULT_TITLE = "Parameters"
EMPTY_CELL_PLACEHOLDER = "—"
FALLBACK_TYPE_NAME = "any"
OPTIONAL_LABEL = "Optional"
OPTIONAL_VARIANT = "neutral"
REQUIRED_LABEL = "Required"
REQUIRED_VARIANT = "error"


class ParamsTable(components.TagComponent):
    """Domain gallery component for displaying a component's parameters and slots.

    Renders a ``<section class="dds-params-table">`` containing an optional
    section heading, a compact ``dds__table`` listing parameter metadata
    (name, type badge, requirement badge, default value, choices badges, and
    description) or an empty-state message when no parameters exist, and an
    optional secondary ``dds__table`` for named ``BlockComponent`` slots.

    Args:
        params: Component parameter tuples ``(name, spec)`` or parameter dicts.
        slots_list: Optional slot tuples ``(name, slot)`` or slot dicts.
        title: Section heading rendered inside ``<h3 data-params-heading>``.
        empty_message: Fallback message rendered when ``params`` is empty.

    Example usage::

        {% dds__params_table params %}
        {% dds__params_table params=param_rows slots_list=slots title="Parameters" %}
    """

    params = parameters.ListParam(  # type: ignore[assignment]
        description="Component parameter tuples (name, spec) or dicts.",
        default=None,
        required=False,
    )
    slots_list = parameters.ListParam(
        description="Optional slot tuples (name, slot) or dicts.",
        default=None,
        required=False,
    )
    title = parameters.StrParam(
        description="Section heading.",
        default=DEFAULT_TITLE,
        required=False,
    )
    empty_message = parameters.StrParam(
        description="Message shown when no parameters are defined.",
        default=DEFAULT_EMPTY_MESSAGE,
        required=False,
    )

    class Meta:
        positional_args = ["params"]

    def get_context(self) -> dict[str, typing.Any]:
        """Build the normalized template context for the parameters table.

        Returns:
            Dictionary containing normalized ``params``, ``normalized_params``,
            ``slots_list``, ``normalized_slots``, ``has_params``, ``has_slots``,
            ``title``, ``has_title``, and ``empty_message``.
        """
        context = super().get_context()
        raw_params = list(self.params) if self.params is not None else []
        normalized_params: list[dict[str, typing.Any]] = [
            data.ParamTableRowData.from_raw(
                raw_item,
                empty_placeholder=EMPTY_CELL_PLACEHOLDER,
                fallback_type_name=FALLBACK_TYPE_NAME,
            ).to_dict()
            for raw_item in raw_params
        ]

        raw_slots = list(self.slots_list) if self.slots_list is not None else []
        normalized_slots: list[dict[str, typing.Any]] = [
            data.SlotTableRowData.from_raw(
                raw_slot,
                empty_placeholder=EMPTY_CELL_PLACEHOLDER,
            ).to_dict()
            for raw_slot in raw_slots
        ]

        title = str(self.title) if self.title else ""
        context["params"] = normalized_params
        context["normalized_params"] = normalized_params
        context["slots_list"] = normalized_slots
        context["normalized_slots"] = normalized_slots
        context["has_params"] = bool(normalized_params)
        context["has_slots"] = bool(normalized_slots)
        context["title"] = title
        context["has_title"] = bool(self.title)
        context["empty_message"] = self.empty_message or DEFAULT_EMPTY_MESSAGE
        return context
