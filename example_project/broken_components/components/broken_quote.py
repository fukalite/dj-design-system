from dj_design_system.components import BlockComponent
from dj_design_system.parameters import StrParam
from dj_design_system.slots import Slot


class BrokenQuoteComponent(BlockComponent):
    """A quote component with an intentional HTML validation error."""
    quote = StrParam("The quote text", required=True)

    class Meta:
        name = "broken_quote"
        positional_args = ["quote"]
        slots = {
            "author": Slot(required=True),
            "source": Slot(required=False),
        }
