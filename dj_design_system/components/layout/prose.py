from dj_design_system.components import BlockComponent
from dj_design_system.services.media import FOUNDATION_CSS


class Prose(BlockComponent):
    """Readable long-form content, such as rendered markdown documentation.

    Larger type and roomier spacing for headings, lists, tables, quotes and
    images. Use it inside a ``Page`` or a documentation ``Pane``.

    Example usage::

        {% dds__layout__prose %}{{ doc_html }}{% enddds__layout__prose %}
    """

    template_name = "dj_design_system/ui/layout/prose.html"

    class Media:
        # page.css first: prose refines the page's heading and code styles.
        css = [
            FOUNDATION_CSS,
            "dj_design_system/ui/layout/page.css",
            "dj_design_system/ui/layout/prose.css",
        ]
