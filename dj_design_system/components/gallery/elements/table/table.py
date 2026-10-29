"""Built-in table component for structured tabular data."""

import typing

from dj_design_system import components, parameters, slots


DENSITY_COMPACT = "compact"
DENSITY_DEFAULT = "default"


class Table(components.BlockComponent):
    """A responsive table component with named slots for header and body rows.

    Wraps a semantic HTML ``<table>`` inside a horizontally scrollable container
    (``.dds-table``) so wide tables do not overflow their parent layout.

    Use the ``default`` density for general tabular content in documentation and
    data views, and ``compact`` density for dense metadata or parameter tables.

    When to Use:
        - Displaying structured datasets, parameter specifications, or comparison matrices.
        - Use ``density="default"`` for general documentation tables.
        - Use ``density="compact"`` for dense parameter or metadata listings.
    """

    caption = parameters.StrParam(
        description="Optional accessible table caption.",
        default="",
        required=False,
    )
    density = parameters.StrParam(
        description="Row padding density.",
        default=DENSITY_DEFAULT,
        required=False,
        choices=[DENSITY_COMPACT, DENSITY_DEFAULT],
    )

    class Meta:
        slots = {
            "head": slots.Slot(
                required=False,
                description="Table header rows (<tr> with <th> cells).",
            ),
            "body": slots.Slot(
                required=True,
                description="Table body rows (<tr> with <td> cells).",
            ),
            "foot": slots.Slot(
                required=False,
                description="Optional table footer rows (<tr> with <td> or <th> cells).",
            ),
        }

    def get_context(self) -> dict[str, typing.Any]:
        """Compute template context including caption presence flag and resolved aria-label.

        Returns:
            A context dictionary containing parameters, ``has_caption``,
            ``resolved_aria_label``, and ``slots``.
        """
        context = super().get_context()
        context["has_caption"] = bool(self.caption)
        context["resolved_aria_label"] = self.caption or "Data table"
        return context
