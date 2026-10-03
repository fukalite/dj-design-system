from dj_design_system.components import BlockComponent
from dj_design_system.services.media import FOUNDATION_CSS


class UsageExamples(BlockComponent):
    """A column of ``UsageExample`` blocks, as on a component page.

    Example usage::

        {% dds__docs__usage_examples %}
            {% dds__docs__usage_example heading="Minimal example" code=signature.minimal %}
            {% dds__docs__usage_example heading="Bigger example" code=signature.maximal %}
        {% enddds__docs__usage_examples %}
    """

    template_name = "dj_design_system/ui/docs/usage_examples.html"

    class Media:
        css = [FOUNDATION_CSS, "dj_design_system/ui/docs/usage_examples.css"]
