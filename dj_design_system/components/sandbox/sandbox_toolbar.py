from dj_design_system.components import BlockComponent
from dj_design_system.services.media import FOUNDATION_CSS


class SandboxToolbar(BlockComponent):
    """The bar of tools above the sandbox canvas.

    The content is the tools: ``Popout``s for the canvas background
    (``panel_name="bg"``), viewport width (``viewport``) and zoom
    (``zoom``), and ``ToggleButton``s. The toolbar's script applies the
    chosen background, viewport and zoom to the sandbox canvas, and keeps
    them when the sandbox reloads.

    Example usage::

        {% dds__sandbox__sandbox_toolbar %}
            {% dds__sandbox__toggle_button "outline" %}
        {% enddds__sandbox__sandbox_toolbar %}
    """

    template_name = "dj_design_system/ui/sandbox/sandbox_toolbar.html"

    class Media:
        # The content is Popouts, PopoutOptions and ToggleButtons.
        css = [
            FOUNDATION_CSS,
            "dj_design_system/ui/primitives/icon.css",
            "dj_design_system/ui/primitives/button.css",
            "dj_design_system/ui/sandbox/sandbox_toolbar.css",
            "dj_design_system/ui/sandbox/popout.css",
            "dj_design_system/ui/sandbox/toggle_button.css",
        ]
        js = [
            "dj_design_system/ui/sandbox/popout.js",
            "dj_design_system/ui/sandbox/sandbox_toolbar.js",
            "dj_design_system/ui/sandbox/toggle_button.js",
        ]
