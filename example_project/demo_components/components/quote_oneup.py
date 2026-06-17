from dj_design_system.components import BlockComponent
from dj_design_system.slots import Slot
from dj_design_system.parameters import StrParam

class QuoteOneUpComponent(BlockComponent):
    quote = StrParam("The quote text", required=True)

    class Meta:
        name = "quote_oneup"
        positional_args = ["quote"]
        slots = {
            "author": Slot(required=True),
            "source": Slot(required=False),
        }
