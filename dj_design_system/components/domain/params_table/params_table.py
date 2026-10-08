"""Built-in parameters table domain component."""

import typing

from dj_design_system import components, parameters


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

    template_name = (
        "dj_design_system/components/domain/params_table/params_table.html"
    )
    _template_name = template_name

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

    class Media:
        css = "dj_design_system/components/domain/params_table/params_table.css"

    def get_context(self) -> dict[str, typing.Any]:
        """Build the normalized template context for the parameters table.

        Returns:
            Dictionary containing normalized ``params``, ``normalized_params``,
            ``slots_list``, ``normalized_slots``, ``has_params``, ``has_slots``,
            ``title``, ``has_title``, and ``empty_message``.
        """
        context = super().get_context()
        raw_params = list(self.params) if self.params is not None else []
        normalized_params: list[dict[str, typing.Any]] = []

        for raw_item in raw_params:
            if isinstance(raw_item, (tuple, list)) and len(raw_item) == 2:
                raw_name: typing.Any = raw_item[0]
                spec: typing.Any = raw_item[1]
            elif isinstance(raw_item, dict):
                raw_name = raw_item.get("name", "")
                spec = (
                    raw_item["spec"]
                    if "spec" in raw_item and raw_item["spec"] is not None
                    else raw_item
                )
            else:
                raw_name = getattr(raw_item, "name", "")
                nested_spec = getattr(raw_item, "spec", None)
                spec = nested_spec if nested_spec is not None else raw_item

            if isinstance(spec, dict):
                raw_type_name: typing.Any = spec.get("type_name")
                raw_type: typing.Any = spec.get("type")
                raw_required: typing.Any = spec.get("required", False)
                raw_default: typing.Any = spec.get("default")
                raw_choices: typing.Any = spec.get("choices")
                raw_description: typing.Any = spec.get("description")
            else:
                raw_type_name = getattr(spec, "type_name", None)
                raw_type = getattr(spec, "type", None)
                raw_required = getattr(spec, "required", False)
                raw_default = getattr(spec, "default", None)
                raw_choices = getattr(spec, "choices", None)
                raw_description = getattr(spec, "description", None)

            if raw_type_name:
                type_name = str(raw_type_name)
            elif isinstance(raw_type, str) and raw_type:
                type_name = raw_type
            elif getattr(raw_type, "__name__", None):
                type_name = str(getattr(raw_type, "__name__"))
            elif isinstance(raw_type, tuple) and raw_type:
                type_name = " | ".join(
                    getattr(item, "__name__", str(item)) for item in raw_type
                )
            elif raw_type is not None:
                type_name = str(raw_type)
            else:
                type_name = FALLBACK_TYPE_NAME

            required = bool(raw_required)
            required_label = REQUIRED_LABEL if required else OPTIONAL_LABEL
            required_variant = REQUIRED_VARIANT if required else OPTIONAL_VARIANT
            has_default = raw_default is not None
            default_display = (
                str(raw_default) if has_default else EMPTY_CELL_PLACEHOLDER
            )
            choices = (
                [str(choice) for choice in raw_choices]
                if raw_choices is not None
                else []
            )
            has_choices = bool(choices)
            description = (
                str(raw_description)
                if raw_description
                else EMPTY_CELL_PLACEHOLDER
            )
            name = str(raw_name) if raw_name is not None else ""

            normalized_params.append(
                {
                    "name": name,
                    "type_name": type_name,
                    "required": required,
                    "required_label": required_label,
                    "required_variant": required_variant,
                    "has_default": has_default,
                    "default_display": default_display,
                    "choices": choices,
                    "has_choices": has_choices,
                    "description": description,
                }
            )

        raw_slots = list(self.slots_list) if self.slots_list is not None else []
        normalized_slots: list[dict[str, typing.Any]] = []

        for raw_slot in raw_slots:
            if isinstance(raw_slot, (tuple, list)) and len(raw_slot) == 2:
                raw_slot_name: typing.Any = raw_slot[0]
                slot_spec: typing.Any = raw_slot[1]
            elif isinstance(raw_slot, dict):
                raw_slot_name = raw_slot.get("name", "")
                if "slot" in raw_slot and raw_slot["slot"] is not None:
                    slot_spec = raw_slot["slot"]
                elif "spec" in raw_slot and raw_slot["spec"] is not None:
                    slot_spec = raw_slot["spec"]
                else:
                    slot_spec = raw_slot
            else:
                raw_slot_name = getattr(raw_slot, "name", "")
                nested_slot = getattr(raw_slot, "slot", None) or getattr(
                    raw_slot, "spec", None
                )
                slot_spec = nested_slot if nested_slot is not None else raw_slot

            if isinstance(slot_spec, dict):
                slot_required_raw: typing.Any = slot_spec.get("required", False)
                slot_default_raw: typing.Any = slot_spec.get("default")
                slot_description_raw: typing.Any = slot_spec.get("description")
            else:
                slot_required_raw = getattr(slot_spec, "required", False)
                slot_default_raw = getattr(slot_spec, "default", None)
                slot_description_raw = getattr(slot_spec, "description", None)

            slot_required = bool(slot_required_raw)
            slot_required_label = (
                REQUIRED_LABEL if slot_required else OPTIONAL_LABEL
            )
            slot_required_variant = (
                REQUIRED_VARIANT if slot_required else OPTIONAL_VARIANT
            )
            slot_has_default = (
                slot_default_raw is not None and slot_default_raw != ""
            )
            slot_default_display = (
                str(slot_default_raw)
                if slot_has_default
                else EMPTY_CELL_PLACEHOLDER
            )
            slot_description = (
                str(slot_description_raw)
                if slot_description_raw
                else EMPTY_CELL_PLACEHOLDER
            )
            slot_name = str(raw_slot_name) if raw_slot_name is not None else ""

            normalized_slots.append(
                {
                    "name": slot_name,
                    "required": slot_required,
                    "required_label": slot_required_label,
                    "required_variant": slot_required_variant,
                    "has_default": slot_has_default,
                    "default_display": slot_default_display,
                    "description": slot_description,
                }
            )

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
