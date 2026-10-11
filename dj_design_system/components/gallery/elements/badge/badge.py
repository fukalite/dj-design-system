"""Built-in badge element component."""

import typing

from dj_design_system import components, parameters


DEFAULT_VARIANT = "neutral"
BADGE_VARIANTS: tuple[str, ...] = (
    "neutral",
    "info",
    "success",
    "warning",
    "error",
)


class Badge(components.TagComponent):
    """A compact inline badge element for status labels, metadata, and type pills.

    Use ``Badge`` to display concise, non-interactive categorical labels,
    parameter requirements, status indicators, or technical type annotations
    within the gallery and documentation views.

    Variants:
        - ``neutral`` (default): General-purpose metadata pill using control surface styling.
        - ``info``: Informational status or highlighted note pill.
        - ``success``: Positive status, active state, or completion indicator.
        - ``warning``: Caution or deprecation indicator.
        - ``error``: Required parameter indicator, error state, or critical status.

    Parameters:
        label: Badge text content. Positional argument 1.
        variant: Semantic status style (``"neutral"``, ``"info"``, ``"success"``, ``"warning"``, ``"error"``).
        is_code: Render badge text as inline monospace code.

    Example usage::

        {% dds__badge "Optional" %}
        {% dds__badge "Required" variant="error" %}
        {% dds__badge "str" is_code=True %}
        {% dds__badge "DeprecatedType" variant="warning" is_code=True %}
    """

    label = parameters.StrParam(description="Badge text content.")
    variant = parameters.StrParam(
        description="Semantic badge style.",
        default=DEFAULT_VARIANT,
        required=False,
        choices=list(BADGE_VARIANTS),
    )
    is_code = parameters.BoolParam(
        description="Render badge text as inline monospace code.",
        default=False,
        required=False,
    )

    class Meta:
        positional_args = ["label"]

    def get_context(self) -> dict[str, typing.Any]:
        """Return the normalized template context for rendering the badge.

        Returns:
            Dictionary containing ``label``, resolved ``variant``, and ``is_code`` flag.
        """
        context = super().get_context()
        context["label"] = self.label
        context["variant"] = (
            self.variant if self.variant is not None else DEFAULT_VARIANT
        )
        context["is_code"] = bool(self.is_code)
        return context
