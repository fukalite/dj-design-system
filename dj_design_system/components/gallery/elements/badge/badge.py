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

    When to Use:
        - Highlighting parameter requirements (``Required``, ``Optional``) in parameter tables.
        - Displaying parameter data types (``str``, ``bool``, ``int``) using the ``is_code`` monospace style.
        - Indicating semantic status (``info``, ``success``, ``warning``, ``error``) in headers, lists, and cards.
    """

    label = parameters.StrParam(description="Badge text content.")
    variant = parameters.StrParam(
        description="Semantic badge style.",
        default=DEFAULT_VARIANT,
        required=False,
        choices=list(BADGE_VARIANTS),
        data_attr=True,
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
