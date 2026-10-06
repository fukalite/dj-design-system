from dj_design_system.components import BlockComponent
from dj_design_system.services.media import FOUNDATION_CSS


class Page(BlockComponent):
    """A padded, scrolling page for the gallery's standalone views.

    Styles the headings, paragraphs and code inside it, e.g. the gallery
    home, folder listings and documentation pages.

    Example usage::

        {% dds__layout__page %}<h1>Components</h1>{% enddds__layout__page %}
    """

    template_name = "dj_design_system/ui/layout/page.html"

    class Media:
        css = [FOUNDATION_CSS, "dj_design_system/ui/layout/page.css"]
