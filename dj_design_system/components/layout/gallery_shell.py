from dj_design_system.components import BlockComponent
from dj_design_system.components.layout.mobile_menu_toggle import MobileMenuToggle
from dj_design_system.services.media import FOUNDATION_CSS
from dj_design_system.slots import Slot


class GalleryShell(BlockComponent):
    """The gallery's full-height frame: sidebar on the left, main area on the right.

    Renders the mobile menu toggle before the sidebar, then a ``<main>``
    holding the toolbar above a scrolling content area. It sets the
    gallery's font, text colour and background, which everything inside
    inherits.

    Example usage::

        {% dds__layout__gallery_shell %}
            {% slot "sidebar" %}...{% endslot %}
            {% slot "toolbar" %}...{% endslot %}
            {% slot "content" %}...{% endslot %}
        {% enddds__layout__gallery_shell %}
    """

    template_name = "dj_design_system/ui/layout/gallery_shell.html"

    class Meta:
        slots = {
            "sidebar": Slot(required=True, description="The sidebar, e.g. a Sidebar."),
            "toolbar": Slot(description="The toolbar above the content."),
            "content": Slot(required=True, description="The page content."),
        }

    class Media:
        css = [
            FOUNDATION_CSS,
            "dj_design_system/ui/layout/mobile_menu_toggle.css",
            "dj_design_system/ui/layout/gallery_shell.css",
        ]

    def get_context(self):
        context = super().get_context()
        context["menu_toggle"] = MobileMenuToggle().render()
        return context
