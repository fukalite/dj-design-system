from django.utils.html import format_html_join

from dj_design_system.components import BlockComponent
from dj_design_system.components.primitives.button import Button
from dj_design_system.parameters import DictParam, StrParam
from dj_design_system.services.media import FOUNDATION_CSS
from dj_design_system.slots import Slot


class Popout(BlockComponent):
    """A toolbar button that opens a panel below it.

    Clicking the button (the ``toggle`` slot) opens the panel (the
    ``options`` slot, usually ``PopoutOption``s) and closes any other popout.
    Clicking outside the panel, or choosing an option, closes it again.
    ``panel_name`` names the panel for scripts (``data-gallery-panel``) and
    is the group's modifier class, e.g. ``gallery-sandbox-toolbar__zoom``.

    Example usage::

        {% dds__sandbox__popout panel_id="gallery-zoom-panel" panel_name="zoom" title="Zoom level" %}
            {% slot "toggle" %}100%{% endslot %}
            {% slot "options" %}...{% endslot %}
        {% enddds__sandbox__popout %}
    """

    template_name = "dj_design_system/ui/sandbox/popout.html"

    panel_id = StrParam("The panel's ID, unique on the page.")
    panel_name = StrParam("Names the panel for scripts, e.g. ``zoom``.")
    title = StrParam("The button's tooltip.")
    toggle_class = StrParam(
        "Extra CSS classes on the button, e.g. a hook for scripts.",
        required=False,
        default="",
    )
    panel_attrs = DictParam(
        "Extra HTML attributes on the panel, e.g. ``{'data-initial-bg': 'white'}``."
        " Values are escaped.",
        required=False,
    )

    class Meta:
        slots = {
            "toggle": Slot(required=True, description="The button's content."),
            "options": Slot(
                required=True, description="The panel's content, e.g. PopoutOptions."
            ),
        }

    class Media:
        # sandbox_toolbar.css: the toolbar group the popout is placed by.
        css = [
            FOUNDATION_CSS,
            "dj_design_system/ui/primitives/button.css",
            "dj_design_system/ui/sandbox/sandbox_toolbar.css",
            "dj_design_system/ui/sandbox/popout.css",
        ]
        js = "dj_design_system/ui/sandbox/popout.js"

    def get_context(self):
        context = super().get_context()
        context["toggle_button"] = Button(
            content=self.slots["toggle"],
            expanded=False,
            controls=self.panel_id,
            title=self.title,
            extra_classes=self.toggle_class,
        ).render()
        context["extra_panel_attrs"] = format_html_join(
            "", ' {}="{}"', (self.panel_attrs or {}).items()
        )
        return context
