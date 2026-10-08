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

    Example usage::

        {% dds__table caption="Component parameters" density="compact" %}
            {% slot "head" %}
                <tr>
                    <th scope="col">Name</th>
                    <th scope="col">Type</th>
                </tr>
            {% endslot %}
            {% slot "body" %}
                <tr>
                    <td>caption</td>
                    <td>str</td>
                </tr>
            {% endslot %}
        {% enddds__table %}
    """

    template_name = "dj_design_system/components/elements/table/table.html"
    _template_name = template_name

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
        }

    class Media:
        css = "dj_design_system/components/elements/table/table.css"

    def get_context(self) -> dict[str, typing.Any]:
        """Compute template context including caption flag and slot mapping.

        Returns:
            A context dictionary containing parameters, ``has_caption``, and
            ``slots``.
        """
        context = super().get_context()
        context["has_caption"] = bool(self.caption)
        context["slots"] = self.slots
        return context
