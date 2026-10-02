from dj_design_system.components import BlockComponent
from dj_design_system.parameters import StrParam
from dj_design_system.services.media import FOUNDATION_CSS


class PageHeader(BlockComponent):
    """A page's main heading, followed by an optional introduction.

    The content is the introduction, usually a paragraph or two. Use it at
    the top of a ``Page``, which styles the heading.

    Example usage::

        {% dds__layout__page_header title=folder_label %}{% enddds__layout__page_header %}
        {% dds__layout__page_header title=design_system_name %}<p>Browse the library.</p>{% enddds__layout__page_header %}
    """

    template_name = "dj_design_system/ui/layout/page_header.html"

    title = StrParam("The page's heading.")

    class Media:
        css = [FOUNDATION_CSS]
