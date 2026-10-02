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
        # code_highlight.css last: its dark theme for code blocks overrides
        # the page's own pre styles.
        css = [
            FOUNDATION_CSS,
            "dj_design_system/ui/layout/page.css",
            "dj_design_system/ui/primitives/code_highlight.css",
        ]
