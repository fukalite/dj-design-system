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
    "code",
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
        - ``code``: Monospace technical pill for parameter types and code identifiers.

    Example usage::

        {% dds__badge "Optional" %}
        {% dds__badge "Required" variant="error" %}
        {% dds__badge "str" variant="code" %}
    """

    label = parameters.StrParam(description="Badge text content.")
    variant = parameters.StrParam(
        description="Semantic badge style.",
        default=DEFAULT_VARIANT,
        required=False,
        choices=list(BADGE_VARIANTS),
    )

    class Meta:
        positional_args = ["label"]

    def get_context(self) -> dict[str, typing.Any]:
        """Return the normalized template context for rendering the badge.

        Returns:
            Dictionary containing ``label`` and resolved ``variant``.
        """
        context = super().get_context()
        context["label"] = self.label
        context["variant"] = (
            self.variant if self.variant is not None else DEFAULT_VARIANT
        )
        return context
