from dj_design_system.components import TagComponent
from dj_design_system.services.media import FOUNDATION_CSS


class SearchBox(TagComponent):
    """The sidebar's search input and its results listbox.

    Its script searches the JSON index the page embeds as
    ``gallery-search-index`` (with Django's ``json_script``), showing
    matches in place of the ``gallery-nav`` navigation as you type. Escape
    clears the search. Render it in the sidebar, above a ``NavTree``.

    Example usage::

        {{ search_index|json_script:"gallery-search-index" }}
        {% dds__navigation__search_box %}
    """

    template_name = "dj_design_system/ui/navigation/search_box.html"

    class Media:
        # nav_tree.css first: results reuse the nav tree's type icons.
        css = [
            FOUNDATION_CSS,
            "dj_design_system/ui/primitives/icon.css",
            "dj_design_system/ui/navigation/nav_tree.css",
            "dj_design_system/ui/navigation/search_box.css",
        ]
        js = "dj_design_system/ui/navigation/search_box.js"
