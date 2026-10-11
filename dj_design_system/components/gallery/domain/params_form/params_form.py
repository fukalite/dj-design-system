"""Built-in sandbox parameters form domain component."""

import typing

from dj_design_system import components, data, parameters


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
        normalized_rows: list[dict[str, typing.Any]] = [
            data.FormFieldRowData.from_raw(raw_item).to_dict() for raw_item in raw_rows
        ]

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
