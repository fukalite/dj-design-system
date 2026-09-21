from dj_design_system.components import TagComponent
from dj_design_system.parameters import StrParam


class BrokenButtonComponent(TagComponent):
    """A button with an intentional visual regression (inline magenta style)."""
    
    label = StrParam("The button label.")

    class Meta:
        positional_args = ["label"]
