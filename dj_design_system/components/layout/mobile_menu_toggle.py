from dj_design_system.components import TagComponent
from dj_design_system.services.media import FOUNDATION_CSS


class MobileMenuToggle(TagComponent):
    """The CSS-only hamburger that slides the sidebar in on narrow screens.

    A hidden checkbox, its hamburger label and a click-to-close overlay.
    No JavaScript: the sidebar and overlay react to the checkbox with
    ``:checked ~`` sibling selectors, so render this immediately before the
    sidebar, inside the same parent (``GalleryShell`` does this).

    Example usage::

        {% dds__layout__mobile_menu_toggle %}
    """

    template_name = "dj_design_system/ui/layout/mobile_menu_toggle.html"

    class Media:
        css = [FOUNDATION_CSS, "dj_design_system/ui/layout/mobile_menu_toggle.css"]
