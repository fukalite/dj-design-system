from dj_design_system.components import BlockComponent
from dj_design_system.parameters import StrParam
from dj_design_system.services.media import FOUNDATION_CSS
from dj_design_system.slots import Slot


class VariantView(BlockComponent):
    """A component page's focus on one gallery variant.

    A "Variant" badge and the variant's ``label`` as a heading, then its
    ``description`` (rendered Markdown) and the ``body``: usually a
    ``UsageExample`` with the variant's preview and code.

    Example usage::

        {% dds__docs__variant_view label=active_variant.label %}
            {% slot "description" %}{{ variant_description|safe }}{% endslot %}
            {% slot "body" %}{% dds__docs__usage_example heading="Preview" code=code %}{% endslot %}
        {% enddds__docs__variant_view %}
    """

    template_name = "dj_design_system/ui/docs/variant_view.html"

    label = StrParam("The variant's label.")

    class Meta:
        slots = {
            "description": Slot(
                required=False, description="The variant's description, as HTML."
            ),
            "body": Slot(required=True, description="The variant's example."),
        }

    class Media:
        # prose.css styles the description's Markdown.
        css = [
            FOUNDATION_CSS,
            "dj_design_system/ui/layout/prose.css",
            "dj_design_system/ui/docs/variant_view.css",
        ]
