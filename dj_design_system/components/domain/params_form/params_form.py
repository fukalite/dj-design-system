"""Built-in sandbox parameters form domain component."""

import typing

from django.utils import safestring

from dj_design_system import components, parameters


DEFAULT_EMPTY_MESSAGE = "This component has no configurable parameters."
DEFAULT_HX_TARGET = "closest [data-gallery-sandbox-body]"


class ParamsForm(components.TagComponent):
    """Domain gallery component for editing component parameters in the live sandbox.

    Renders a ``<dds-params-form class="dds-params-form" data-surface="sandbox">``
    custom element containing an HTMX-enabled GET ``<form data-params-form>``
    when parameter rows exist, or an empty-state ``<p data-params-empty>``
    message when the component declares no configurable parameters.

    Each row in ``param_rows`` is normalised in ``get_context()`` and delegated
    to ``{% dds__form_field %}`` inside an Every Layout ``<l-stack data-params-fields>``.

    Args:
        param_rows: Parameter form row dicts or objects with ``name``, ``spec``,
            and ``field`` entries.
        action_url: Form GET ``action`` and ``hx-get`` URL.
        active_theme: Active theme value preserved as a hidden ``_dds_theme`` input.
        active_variant: Active variant name (or ``Variant`` instance) preserved
            as a hidden ``_dds_variant`` input.
        hx_target: HTMX target selector for live sandbox swaps.
        empty_message: Fallback message displayed when ``param_rows`` is empty.

    Example usage::

        {% dds__params_form param_rows action_url=request.path active_theme=active_theme active_variant=active_variant %}
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
    active_theme = parameters.StrParam(
        description="Active theme value preserved as hidden '_dds_theme' input.",
        default="",
        required=False,
    )
    active_variant = parameters.StrParam(
        description="Active variant name (or Variant instance) preserved as hidden '_dds_variant' input.",
        default="",
        required=False,
    )
    hx_target = parameters.StrParam(
        description="HTMX target selector for live sandbox swaps.",
        default=DEFAULT_HX_TARGET,
        required=False,
    )
    empty_message = parameters.StrParam(
        description="Message displayed when the component has no editable parameters.",
        default=DEFAULT_EMPTY_MESSAGE,
        required=False,
    )

    class Meta:
        positional_args = ["param_rows"]

    def __init__(self, **kwargs: typing.Any) -> None:
        """Initialise ParamsForm and normalise active_variant objects to their name string.

        Args:
            **kwargs: Component parameter keyword arguments.
        """
        if (
            "active_variant" in kwargs
            and kwargs["active_variant"] is not None
            and not isinstance(kwargs["active_variant"], str)
        ):
            kwargs["active_variant"] = str(
                getattr(kwargs["active_variant"], "name", kwargs["active_variant"])
            )
        super().__init__(**kwargs)

    def get_context(self) -> dict[str, typing.Any]:
        """Build the normalised template context for the sandbox parameters form.

        Returns:
            Dictionary containing ``param_rows``, ``normalized_rows``,
            ``has_rows``, ``action_url``, ``has_action_url``, ``active_theme``,
            ``has_active_theme``, ``active_variant``, ``has_active_variant``,
            ``hx_target``, and ``empty_message``.
        """
        context = super().get_context()
        raw_rows = list(self.param_rows) if self.param_rows is not None else []
        normalized_rows: list[dict[str, typing.Any]] = []

        for raw_item in raw_rows:
            if isinstance(raw_item, dict):
                raw_name: typing.Any = raw_item.get("name", "")
                raw_label: typing.Any = raw_item.get("label")
                raw_spec: typing.Any = raw_item.get("spec")
                raw_field: typing.Any = raw_item.get("field")
                raw_field_id: typing.Any = raw_item.get("field_id", "")
                raw_description: typing.Any = raw_item.get("description")
                raw_required: typing.Any = raw_item.get("required", False)
                raw_item_errors: typing.Any = raw_item.get("errors")
            else:
                raw_name = getattr(raw_item, "name", "")
                raw_label = getattr(raw_item, "label", None)
                raw_spec = getattr(raw_item, "spec", None)
                raw_field = getattr(raw_item, "field", None)
                raw_field_id = getattr(raw_item, "field_id", "")
                raw_description = getattr(raw_item, "description", None)
                raw_required = getattr(raw_item, "required", False)
                raw_item_errors = getattr(raw_item, "errors", None)

            name = str(raw_name) if raw_name is not None else ""
            label = str(raw_label) if raw_label else name
            field_id = str(
                getattr(raw_field, "id_for_label", None) or raw_field_id or f"id_{name}"
            )
            description = str(
                getattr(raw_spec, "description", None)
                or (raw_spec.get("description") if isinstance(raw_spec, dict) else None)
                or raw_description
                or ""
            )
            if raw_spec is not None:
                required = bool(
                    getattr(raw_spec, "required", False)
                    if not isinstance(raw_spec, dict)
                    else raw_spec.get("required", False)
                )
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
            if has_field_html:
                field_html: safestring.SafeString | str = safestring.SafeString(
                    str(raw_field)
                )
            else:
                field_html = ""

            normalized_rows.append(
                {
                    "name": name,
                    "label": label,
                    "field_id": field_id,
                    "description": description,
                    "required": required,
                    "errors": errors,
                    "error": error,
                    "has_field_html": has_field_html,
                    "field_html": field_html,
                }
            )

        has_rows = bool(normalized_rows)
        action_url = self.action_url or ""
        has_action_url = bool(action_url)
        active_theme = self.active_theme or ""
        has_active_theme = bool(active_theme)
        active_variant = self.active_variant or ""
        has_active_variant = bool(active_variant)
        hx_target = self.hx_target or DEFAULT_HX_TARGET
        empty_message = self.empty_message or DEFAULT_EMPTY_MESSAGE

        context["param_rows"] = normalized_rows
        context["normalized_rows"] = normalized_rows
        context["has_rows"] = has_rows
        context["action_url"] = action_url
        context["has_action_url"] = has_action_url
        context["active_theme"] = active_theme
        context["has_active_theme"] = has_active_theme
        context["active_variant"] = active_variant
        context["has_active_variant"] = has_active_variant
        context["hx_target"] = hx_target
        context["empty_message"] = empty_message
        return context
