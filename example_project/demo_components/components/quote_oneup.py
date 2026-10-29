"""Slotted pull-quote component for example_project.demo_components."""

from dj_design_system import components, parameters, slots


class QuoteOneUpComponent(components.BlockComponent):
    """A pull-quote block component with required ``author`` and optional ``source`` slots."""

    quote = parameters.StrParam("The quote text", required=True)

    class Meta:
        name = "quote_oneup"
        positional_args = ["quote"]
        slots = {
            "author": slots.Slot(required=True),
            "source": slots.Slot(required=False),
        }
