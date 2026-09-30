from dj_design_system.components import TagComponent
from dj_design_system.parameters import ListParam
from dj_design_system.services.media import FOUNDATION_CSS


class Breadcrumb(TagComponent):
    """The trail of links from the gallery home to the current page.

    Pass a list of ``{"label": ..., "url": ...}`` crumbs; the last is the
    current page and needs no ``url``. On narrow screens a trail of more
    than two crumbs collapses to the first and last, with an ellipsis that
    opens the rest in a CSS-only flyout.

    Example usage::

        {% dds__navigation__breadcrumb breadcrumbs %}
    """

    template_name = "dj_design_system/ui/navigation/breadcrumb.html"

    crumbs = ListParam("Crumbs, each a dict with ``label`` and ``url``.")

    class Meta:
        positional_args = ["crumbs"]

    class Media:
        # toolbar.css first: the flyout's link rules override the toolbar's.
        css = [
            FOUNDATION_CSS,
            "dj_design_system/ui/layout/toolbar.css",
            "dj_design_system/ui/navigation/breadcrumb.css",
        ]
