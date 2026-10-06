from dj_design_system.components import BlockComponent
from dj_design_system.services.media import FOUNDATION_CSS


class SandboxCanvas(BlockComponent):
    """The area of the sandbox pane that holds the component's canvas.

    The content is the sandbox's ``CanvasWidget``. It fills the space between
    the toolbar and the parameter drawer, and the toolbar's script marks it
    with ``gallery-sandbox__canvas--viewport`` while a fixed viewport width is
    chosen.

    Example usage::

        {% dds__sandbox__sandbox_canvas %}
            {% dds__canvas__canvas_widget unique_id="sandbox" iframe_src=canvas_iframe_url %}
        {% enddds__sandbox__sandbox_canvas %}
    """

    template_name = "dj_design_system/ui/sandbox/sandbox_canvas.html"

    class Media:
        css = [FOUNDATION_CSS, "dj_design_system/ui/sandbox/sandbox_canvas.css"]
