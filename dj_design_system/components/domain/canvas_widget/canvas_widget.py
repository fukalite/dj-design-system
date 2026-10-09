"""Built-in interactive canvas widget domain component for the dds gallery."""

import html
import re
import typing

from dj_design_system import components, parameters


MODE_PREVIEW = "preview"
MODE_CODE = "code"
MODE_HTML = "html"
MODE_CHOICES: tuple[str, ...] = (MODE_PREVIEW, MODE_CODE, MODE_HTML)
DEFAULT_CANVAS_ID = "canvas"
DEFAULT_MODE = MODE_PREVIEW
DEFAULT_VIEWPORT = "responsive"
DEFAULT_BACKGROUND = "white"
DEFAULT_ZOOM = "100"
DEFAULT_TITLE = "Component preview"
HTML_TAG_PATTERN = r"<[^>]+>"
HIGHLIGHT_DIV_MARKER = '<div class="highlight"'
PRE_TAG_MARKER = "<pre"
SPAN_TAG_MARKER = '<span class="'
HTML_ENTITY_LT_MARKER = "&lt;"
LINE_BREAK_CHARS = "\r\n"
ARIA_TRUE = "true"
ARIA_FALSE = "false"


class CanvasWidget(components.TagComponent):
    """Isolated iframe preview stage with template source and HTML code drawers.

    Renders a ``<dds-canvas-widget class="dds-canvas-widget">`` Light DOM custom
    element that hosts an isolated ``<iframe>`` preview stage
    (``[data-canvas-stage]`` on ``data-surface="stage"``) alongside optional
    template source (``[data-canvas-panel="code"]``) and rendered HTML output
    (``[data-canvas-panel="html"]``) drawers delegating to
    ``{% dds__code_block %}`` on ``data-surface="code"``.

    When ``show_toggles=True`` and either ``source_code`` or ``rendered_html``
    is provided, renders a ``[data-canvas-toggles]`` mode switcher bar with
    ``{% dds__icon %}`` buttons for toggling between ``"preview"``, ``"code"``,
    and ``"html"`` panels.

    Args:
        canvas_id: Unique identifier for the canvas instance and postMessage
            resize correlation.
        iframe_src: URL for the isolated preview iframe.
        iframe_srcdoc: Inline HTML document string for srcdoc preview embedding.
        source_code: Raw or highlighted template source code snippet.
        rendered_html: Raw or highlighted rendered HTML output snippet.
        mode: Initial active panel mode (``'preview'``, ``'code'``, or ``'html'``).
        viewport: Initial viewport width preset (``'responsive'`` or pixel width
            string such as ``'768'``).
        background: Initial canvas stage background preset (``'white'``,
            ``'light'``, ``'dark'``).
        zoom: Initial zoom percentage string (e.g. ``'100'``).
        sandbox_attrs: Optional iframe sandbox attribute value.
        title: Accessible title attribute for the preview iframe.
        show_toggles: Whether to render the preview/code/html mode toggle bar.

    Example usage::

        {% dds__canvas_widget "/gallery/canvas/?component=dds__button" canvas_id="main" source_code="{% dds__button 'Save' %}" rendered_html="<button class='dds-button'>Save</button>" %}

        {% dds__canvas_widget iframe_srcdoc="<button>Hello</button>" background="dark" viewport="768" zoom="125" %}
    """

    canvas_id = parameters.StrParam(
        default=DEFAULT_CANVAS_ID,
        required=False,
        description=(
            "Unique identifier for the canvas instance and postMessage resize "
            "correlation."
        ),
    )
    iframe_src = parameters.StrParam(
        default="",
        required=False,
        description="URL for the isolated preview iframe.",
    )
    iframe_srcdoc = parameters.StrParam(
        default="",
        required=False,
        description="Inline HTML document string for srcdoc preview embedding.",
    )
    source_code = parameters.StrParam(
        default="",
        required=False,
        description="Raw or highlighted template source code snippet.",
    )
    rendered_html = parameters.StrParam(
        default="",
        required=False,
        description="Raw or highlighted rendered HTML output snippet.",
    )
    mode = parameters.StrParam(
        default=DEFAULT_MODE,
        required=False,
        choices=list(MODE_CHOICES),
        description="Initial active panel mode ('preview', 'code', or 'html').",
    )
    viewport = parameters.StrParam(
        default=DEFAULT_VIEWPORT,
        required=False,
        description=(
            "Initial viewport width preset ('responsive' or pixel width string "
            "such as '768')."
        ),
    )
    background = parameters.StrParam(
        default=DEFAULT_BACKGROUND,
        required=False,
        description=(
            "Initial canvas stage background preset ('white', 'light', 'dark')."
        ),
    )
    zoom = parameters.StrParam(
        default=DEFAULT_ZOOM,
        required=False,
        description="Initial zoom percentage string (e.g. '100').",
    )
    sandbox_attrs = parameters.StrParam(
        default="",
        required=False,
        description="Optional iframe sandbox attribute value.",
    )
    title = parameters.StrParam(
        default=DEFAULT_TITLE,
        required=False,
        description="Accessible title attribute for the preview iframe.",
    )
    show_toggles = parameters.BoolParam(
        default=True,
        required=False,
        description="Whether to render the preview/code/html mode toggle bar.",
    )

    class Meta:
        positional_args = ["iframe_src"]

    def __init__(self, **kwargs: typing.Any) -> None:
        """Initialise the canvas widget, normalising numeric or percentage zoom inputs.

        Args:
            **kwargs: Component parameter keyword arguments.
        """
        zoom_value = kwargs.get("zoom")
        if (
            zoom_value is not None
            and isinstance(zoom_value, int | float)
            and not isinstance(zoom_value, bool)
        ):
            kwargs["zoom"] = str(zoom_value).rstrip("%")
        elif isinstance(zoom_value, str):
            kwargs["zoom"] = zoom_value.rstrip("%")
        super().__init__(**kwargs)

    def get_context(self) -> dict[str, typing.Any]:
        """Compute normalized code snippets, stage attributes, and mode flags.

        Returns:
            Dictionary containing resolved canvas attributes, plain-text code
            snippets, and mode visibility/ARIA state flags for
            ``canvas_widget.html``.
        """
        context = super().get_context()
        resolved_canvas_id = (
            str(self.canvas_id) if self.canvas_id else DEFAULT_CANVAS_ID
        )
        resolved_mode = (
            str(self.mode) if self.mode in MODE_CHOICES else DEFAULT_MODE
        )
        resolved_viewport = (
            str(self.viewport) if self.viewport else DEFAULT_VIEWPORT
        )
        resolved_background = (
            str(self.background) if self.background else DEFAULT_BACKGROUND
        )
        resolved_zoom = (
            str(self.zoom).rstrip("%") if self.zoom else DEFAULT_ZOOM
        )
        resolved_title = str(self.title) if self.title else DEFAULT_TITLE

        iframe_src = str(self.iframe_src) if self.iframe_src else ""
        iframe_srcdoc = str(self.iframe_srcdoc) if self.iframe_srcdoc else ""
        sandbox_attrs = str(self.sandbox_attrs) if self.sandbox_attrs else ""

        raw_source_code = str(self.source_code) if self.source_code else ""
        if (
            HIGHLIGHT_DIV_MARKER in raw_source_code
            or PRE_TAG_MARKER in raw_source_code
            or SPAN_TAG_MARKER in raw_source_code
        ):
            stripped_source = re.sub(
                pattern=HTML_TAG_PATTERN,
                repl="",
                string=raw_source_code,
            )
            normalized_source_code = html.unescape(s=stripped_source).strip(
                LINE_BREAK_CHARS
            )
        else:
            normalized_source_code = raw_source_code.strip(LINE_BREAK_CHARS)

        raw_rendered_html = (
            str(self.rendered_html) if self.rendered_html else ""
        )
        if (
            HIGHLIGHT_DIV_MARKER in raw_rendered_html
            or PRE_TAG_MARKER in raw_rendered_html
            or (
                SPAN_TAG_MARKER in raw_rendered_html
                and HTML_ENTITY_LT_MARKER in raw_rendered_html
            )
        ):
            stripped_rendered = re.sub(
                pattern=HTML_TAG_PATTERN,
                repl="",
                string=raw_rendered_html,
            )
            normalized_rendered_html = html.unescape(s=stripped_rendered).strip(
                LINE_BREAK_CHARS
            )
        else:
            normalized_rendered_html = raw_rendered_html.strip(LINE_BREAK_CHARS)

        has_src = bool(iframe_src)
        has_srcdoc = bool(iframe_srcdoc)
        has_sandbox_attrs = bool(sandbox_attrs)
        has_source_code = bool(normalized_source_code.strip())
        has_rendered_html = bool(normalized_rendered_html.strip())
        show_mode_toggles = bool(self.show_toggles) and (
            has_source_code or has_rendered_html
        )

        is_preview_mode = resolved_mode == MODE_PREVIEW
        is_code_mode = resolved_mode == MODE_CODE
        is_html_mode = resolved_mode == MODE_HTML
        preview_aria_pressed = ARIA_TRUE if is_preview_mode else ARIA_FALSE
        code_aria_pressed = ARIA_TRUE if is_code_mode else ARIA_FALSE
        html_aria_pressed = ARIA_TRUE if is_html_mode else ARIA_FALSE

        context["resolved_canvas_id"] = resolved_canvas_id
        context["resolved_mode"] = resolved_mode
        context["resolved_viewport"] = resolved_viewport
        context["resolved_background"] = resolved_background
        context["resolved_zoom"] = resolved_zoom
        context["resolved_title"] = resolved_title
        context["iframe_src"] = iframe_src
        context["iframe_srcdoc"] = iframe_srcdoc
        context["sandbox_attrs"] = sandbox_attrs
        context["normalized_source_code"] = normalized_source_code
        context["normalized_rendered_html"] = normalized_rendered_html
        context["has_src"] = has_src
        context["has_srcdoc"] = has_srcdoc
        context["has_sandbox_attrs"] = has_sandbox_attrs
        context["has_source_code"] = has_source_code
        context["has_rendered_html"] = has_rendered_html
        context["show_mode_toggles"] = show_mode_toggles
        context["is_preview_mode"] = is_preview_mode
        context["is_code_mode"] = is_code_mode
        context["is_html_mode"] = is_html_mode
        context["preview_aria_pressed"] = preview_aria_pressed
        context["code_aria_pressed"] = code_aria_pressed
        context["html_aria_pressed"] = html_aria_pressed
        return context
