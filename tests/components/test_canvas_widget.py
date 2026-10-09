"""Unit tests for the built-in ``dds__canvas_widget`` domain component."""

import pathlib
import re

import pytest
from django import template

from dj_design_system import data, gallery
from dj_design_system.components import base as components_base
from dj_design_system.components.domain import (
    canvas_widget as canvas_widget_package,
)
from dj_design_system.components.domain.canvas_widget import (
    canvas_widget as canvas_widget_module,
)
from dj_design_system.services import canvas as canvas_service
from dj_design_system.services import registry as registry_service
from dj_design_system.services import slot_node as slot_node_service
from tests import conftest


APP_LABEL = "dj_design_system"
COMPONENT_NAME = "canvas_widget"
QUALIFIED_NAME = "dds__canvas_widget"
RELATIVE_PATH = "domain.canvas_widget"
TEMPLATE_PATH = (
    "dj_design_system/components/domain/canvas_widget/canvas_widget.html"
)
CSS_MEDIA_PATH = (
    "dj_design_system/components/domain/canvas_widget/canvas_widget.css"
)
JS_MEDIA_PATH = (
    "dj_design_system/components/domain/canvas_widget/canvas_widget.js"
)

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
CANVAS_WIDGET_DIR = (
    ROOT_DIR / "dj_design_system" / "components" / "domain" / "canvas_widget"
)
CANVAS_WIDGET_PY_PATH = CANVAS_WIDGET_DIR / "canvas_widget.py"
CANVAS_WIDGET_HTML_PATH = CANVAS_WIDGET_DIR / "canvas_widget.html"
CANVAS_WIDGET_CSS_PATH = CANVAS_WIDGET_DIR / "canvas_widget.css"
CANVAS_WIDGET_TS_PATH = CANVAS_WIDGET_DIR / "canvas_widget.ts"
CANVAS_WIDGET_GALLERY_PATH = CANVAS_WIDGET_DIR / "gallery.py"
CANVAS_WIDGET_INDEX_MD_PATH = CANVAS_WIDGET_DIR / "index.md"
TOKENS_CSS_PATH = (
    ROOT_DIR / "dj_design_system" / "static" / "dj_design_system" / "tokens.css"
)


def _make_registry() -> registry_service.ComponentRegistry:
    """Create a ComponentRegistry populated with built-in dj_design_system components."""
    reg = registry_service.ComponentRegistry()
    conftest.discover_app_into_registry(
        reg=reg,
        app_name=APP_LABEL,
        app_label=APP_LABEL,
    )
    return reg


def _render_template(
    source: str,
    context_data: dict[str, object] | None = None,
) -> str:
    """Render a Django template string with built-in dds component and slot tags."""
    reg = _make_registry()
    engine = template.engines["django"].engine
    lib = template.Library()
    reg.register_templatetags(library=lib)
    lib.tag(name="slot", compile_function=slot_node_service.do_slot)
    previous = engine.template_libraries.get("design_components")
    engine.template_libraries["design_components"] = lib
    try:
        compiled = template.Template(
            template_string="{% load design_components %}" + source
        )
        return compiled.render(
            context=template.Context(dict_=context_data or {})
        )
    finally:
        if previous is None:
            engine.template_libraries.pop("design_components", None)
        else:
            engine.template_libraries["design_components"] = previous


def _read_text(path: pathlib.Path) -> str:
    """Read UTF-8 text from a file path."""
    return path.read_text(encoding="utf-8")


def _extract_rule_blocks(css_text: str, selector: str) -> list[str]:
    """Extract CSS declaration blocks for a specific selector."""
    escaped = re.escape(pattern=selector)
    pattern = re.compile(
        pattern=rf"{escaped}\s*\{{([^}}]*)\}}",
        flags=re.DOTALL,
    )
    return pattern.findall(string=css_text)


def _extract_defined_properties(block_text: str) -> dict[str, str]:
    """Extract property definitions from a CSS block string."""
    matches = re.findall(
        pattern=r"([a-zA-Z0-9_-]+)\s*:\s*([^;]+);",
        string=block_text,
    )
    return {name: value.strip() for name, value in matches}


class TestCanvasWidgetDiscoveryAndMetadata:
    """Verify CanvasWidget exports, metadata, media, and registry discovery."""

    def test_exported_from_package_init_and_subclasses_tag_component(
        self,
    ) -> None:
        """Verify CanvasWidget is exported in dj_design_system.components.domain.canvas_widget."""
        assert (
            canvas_widget_package.CanvasWidget
            is canvas_widget_module.CanvasWidget
        )
        assert issubclass(
            canvas_widget_module.CanvasWidget,
            components_base.TagComponent,
        )

    def test_template_media_and_positional_args_metadata(self) -> None:
        """Verify CanvasWidget relies on co-located template_name, Media.css/js, and positional_args."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]
        assert info.media.js == [JS_MEDIA_PATH]
        assert canvas_widget_module.CanvasWidget.get_positional_args() == [
            "iframe_src",
        ]

    def test_discovered_as_dds_canvas_widget_in_registry(self) -> None:
        """Verify ComponentRegistry discovers CanvasWidget as internal dds__canvas_widget."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.component_class is canvas_widget_module.CanvasWidget
        assert info.qualified_name == QUALIFIED_NAME
        assert info.relative_path == RELATIVE_PATH
        assert info.is_internal is True
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]
        assert info.media.js == [JS_MEDIA_PATH]

    def test_python_module_contains_no_private_methods_comments_or_mark_safe(
        self,
    ) -> None:
        """Verify canvas_widget.py has no private helper methods, inline comments, format_html, or mark_safe."""
        own_private_methods = [
            name
            for name, attr in canvas_widget_module.CanvasWidget.__dict__.items()
            if name.startswith("_")
            and not name.startswith("__")
            and callable(attr)
        ]
        assert not own_private_methods
        py_text = _read_text(path=CANVAS_WIDGET_PY_PATH)
        assert "format_html" not in py_text
        assert "mark_safe" not in py_text
        for line in py_text.splitlines():
            assert not line.lstrip().startswith("#")


class TestCanvasWidgetParametersAndContext:
    """Verify parameter validation, zoom normalisation, HTML stripping, and get_context()."""

    def test_default_parameters_and_context(self) -> None:
        """Verify default parameters produce expected normalized context values."""
        comp = canvas_widget_module.CanvasWidget()
        ctx = comp.get_context()
        assert ctx["resolved_canvas_id"] == "canvas"
        assert ctx["resolved_mode"] == "preview"
        assert ctx["resolved_viewport"] == "responsive"
        assert ctx["resolved_background"] == "white"
        assert ctx["resolved_zoom"] == "100"
        assert ctx["resolved_title"] == "Component preview"
        assert ctx["iframe_src"] == ""
        assert ctx["iframe_srcdoc"] == ""
        assert ctx["sandbox_attrs"] == ""
        assert ctx["normalized_source_code"] == ""
        assert ctx["normalized_rendered_html"] == ""
        assert ctx["has_src"] is False
        assert ctx["has_srcdoc"] is False
        assert ctx["has_sandbox_attrs"] is False
        assert ctx["has_source_code"] is False
        assert ctx["has_rendered_html"] is False
        assert ctx["show_mode_toggles"] is False
        assert ctx["is_preview_mode"] is True
        assert ctx["is_code_mode"] is False
        assert ctx["is_html_mode"] is False
        assert ctx["preview_aria_pressed"] == "true"
        assert ctx["code_aria_pressed"] == "false"
        assert ctx["html_aria_pressed"] == "false"

    def test_normalises_numeric_and_percentage_zoom_in_init(self) -> None:
        """Verify int, float, and percentage-suffixed zoom values normalise to clean strings."""
        comp_int = canvas_widget_module.CanvasWidget(zoom=150)
        assert comp_int.zoom == "150"
        assert comp_int.get_context()["resolved_zoom"] == "150"

        comp_float = canvas_widget_module.CanvasWidget(zoom=125.5)
        assert comp_float.zoom == "125.5"
        assert comp_float.get_context()["resolved_zoom"] == "125.5"

        comp_pct = canvas_widget_module.CanvasWidget(zoom="200%")
        assert comp_pct.zoom == "200"
        assert comp_pct.get_context()["resolved_zoom"] == "200"

    def test_strips_highlighted_html_tags_and_unescapes_entities_for_code_blocks(
        self,
    ) -> None:
        """Verify highlighted <div class="highlight"> / <pre> snippets strip tags and unescape entities."""
        highlighted_source = (
            '<div class="highlight"><pre><span></span>'
            "{% dds__button &#39;Save&#39; variant=&quot;primary&quot; %}"
            "</pre></div>"
        )
        highlighted_html = (
            "<pre><code>&lt;button class=&quot;dds-button&quot;&gt;"
            "Save &amp; Close&lt;/button&gt;</code></pre>"
        )
        comp = canvas_widget_module.CanvasWidget(
            source_code=highlighted_source,
            rendered_html=highlighted_html,
            mode="code",
        )
        ctx = comp.get_context()
        assert (
            ctx["normalized_source_code"]
            == '{% dds__button \'Save\' variant="primary" %}'
        )
        assert (
            ctx["normalized_rendered_html"]
            == '<button class="dds-button">Save & Close</button>'
        )
        assert ctx["has_source_code"] is True
        assert ctx["has_rendered_html"] is True
        assert ctx["show_mode_toggles"] is True
        assert ctx["is_preview_mode"] is False
        assert ctx["is_code_mode"] is True
        assert ctx["is_html_mode"] is False
        assert ctx["preview_aria_pressed"] == "false"
        assert ctx["code_aria_pressed"] == "true"
        assert ctx["html_aria_pressed"] == "false"

        nowrap_comp = canvas_widget_module.CanvasWidget(
            source_code='<span class="cp">{%</span> <span class="k">alert</span> <span class="cp">%}</span>',
            rendered_html='<span class="p">&lt;</span><span class="nt">div</span><span class="p">&gt;</span>Hi<span class="p">&lt;/</span><span class="nt">div</span><span class="p">&gt;</span>',
        )
        nowrap_ctx = nowrap_comp.get_context()
        assert nowrap_ctx["normalized_source_code"] == "{% alert %}"
        assert nowrap_ctx["normalized_rendered_html"] == "<div>Hi</div>"

    def test_preserves_plain_rendered_html_and_respects_show_toggles_flag(
        self,
    ) -> None:
        """Verify raw rendered_html without <pre>/<div class="highlight"> is kept intact and show_toggles=False hides toggles."""
        raw_html = '<button class="dds-button">Click me</button>'
        comp = canvas_widget_module.CanvasWidget(
            rendered_html=raw_html,
            mode="html",
            show_toggles=False,
        )
        ctx = comp.get_context()
        assert ctx["normalized_rendered_html"] == raw_html
        assert ctx["has_source_code"] is False
        assert ctx["has_rendered_html"] is True
        assert ctx["show_mode_toggles"] is False
        assert ctx["is_html_mode"] is True
        assert ctx["html_aria_pressed"] == "true"

    def test_invalid_mode_or_parameter_types_raise_errors(self) -> None:
        """Verify invalid mode choice raises ValueError and invalid types raise TypeError."""
        with pytest.raises(
            expected_exception=ValueError,
            match="Expected one of",
        ):
            canvas_widget_module.CanvasWidget(mode="invalid")
        with pytest.raises(expected_exception=TypeError, match="Expected str"):
            canvas_widget_module.CanvasWidget(iframe_src=123)
        with pytest.raises(expected_exception=TypeError, match="Expected bool"):
            canvas_widget_module.CanvasWidget(show_toggles="yes")


class TestCanvasWidgetRenderingAndTemplate:
    """Verify HTML rendering via template tags, child components, and template purity."""

    def test_renders_default_preview_stage_without_toggles_when_no_code(
        self,
    ) -> None:
        """Verify default {% dds__canvas_widget %} renders root attributes and iframe stage without toggles."""
        html = _render_template(
            source='{% dds__canvas_widget "/canvas/button/" %}',
        ).strip()
        assert (
            '<dds-canvas-widget class="dds-canvas-widget" '
            'data-canvas-id="canvas" data-mode="preview" '
            'data-viewport="responsive" data-background="white" '
            'data-zoom="100">' in html
        )
        assert "data-canvas-toggles" not in html
        assert '<div data-canvas-stage data-surface="stage">' in html
        assert "<div data-canvas-viewport>" in html
        assert (
            '<iframe data-canvas-iframe data-canvas-id="canvas" '
            'src="/canvas/button/" loading="lazy" '
            'title="Component preview"></iframe>' in html
        )
        assert "data-canvas-panel" not in html

    def test_renders_mode_toggles_and_code_drawers_when_snippets_provided(
        self,
    ) -> None:
        """Verify mode toggle bar, icons, and code_block panels render when source_code and rendered_html are provided."""
        html = _render_template(
            source=(
                '{% dds__canvas_widget "/canvas/button/" '
                'canvas_id="btn-canvas" '
                "source_code=source_code "
                "rendered_html=rendered_html "
                'mode="code" '
                'viewport="768" '
                'background="dark" '
                'zoom="125" '
                'sandbox_attrs="allow-scripts" '
                'title="Button preview" %}'
            ),
            context_data={
                "source_code": "{% dds__button 'Save' %}",
                "rendered_html": '<button class="dds-button">Save</button>',
            },
        ).strip()
        assert 'data-canvas-id="btn-canvas"' in html
        assert 'data-mode="code"' in html
        assert 'data-viewport="768"' in html
        assert 'data-background="dark"' in html
        assert 'data-zoom="125"' in html
        assert (
            '<div data-canvas-toggles class="l-cluster" role="group" '
            'aria-label="Canvas view mode">' in html
        )
        assert (
            '<button type="button" data-canvas-mode="preview" '
            'aria-pressed="false" title="Preview">' in html
        )
        assert (
            '<button type="button" data-canvas-mode="code" '
            'aria-pressed="true" title="Template Source">' in html
        )
        assert (
            '<button type="button" data-canvas-mode="html" '
            'aria-pressed="false" title="Output HTML">' in html
        )
        assert 'data-icon="eye"' in html
        assert 'data-icon="code"' in html
        assert 'data-icon="file-code"' in html
        assert '<div data-canvas-stage data-surface="stage" hidden>' in html
        assert 'sandbox="allow-scripts"' in html
        assert 'title="Button preview"' in html
        assert '<div data-canvas-panel="code" data-surface="code">' in html
        assert (
            '<div data-canvas-panel="html" data-surface="code" hidden>' in html
        )
        assert "<dds-code-block" in html
        assert "Template Source" in html
        assert "Output HTML" in html

    def test_renders_srcdoc_and_escapes_untrusted_attributes(self) -> None:
        """Verify iframe_srcdoc renders and untrusted attribute values are HTML-escaped."""
        html = _render_template(
            source=(
                "{% dds__canvas_widget iframe_srcdoc=srcdoc "
                "canvas_id=canvas_id title=title %}"
            ),
            context_data={
                "srcdoc": "<button>Inline</button>",
                "canvas_id": 'id" onload="alert(1)',
                "title": '<script>alert("xss")</script>',
            },
        )
        assert 'srcdoc="&lt;button&gt;Inline&lt;/button&gt;"' in html
        assert "<script>" not in html
        assert (
            'title="&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;"'
            in html
        )
        assert 'data-canvas-id="id&quot; onload=&quot;alert(1)"' in html

    def test_template_contains_no_filters_and_no_bem(self) -> None:
        """Verify canvas_widget.html loads design_components and has zero template filters or BEM."""
        template_text = _read_text(path=CANVAS_WIDGET_HTML_PATH)
        assert template_text.startswith("{% load design_components %}")
        assert "|" not in template_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=template_text,
        )
        assert not bem_matches
        assert "--" not in template_text


class TestCanvasWidgetStylesheet:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, and formatting in canvas_widget.css."""

    def test_wrapped_in_layer_blocks_and_sets_root_layout(self) -> None:
        """Verify canvas_widget.css wraps rules in @layer blocks and sets display: block and margin: 0."""
        css_text = _read_text(path=CANVAS_WIDGET_CSS_PATH)
        assert css_text.startswith("@layer blocks {")
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector="dds-canvas-widget,\n  .dds-canvas-widget",
        )
        assert root_blocks
        props = _extract_defined_properties(block_text=root_blocks[0])
        assert props.get("display") == "block"
        assert props.get("margin") == "0"

    def test_tier_3_tokens_map_exclusively_from_tier_2_tokens_in_tokens_css(
        self,
    ) -> None:
        """Verify all --_canvas-widget-* tokens map exclusively from Tier 2 --dds-* tokens in tokens.css."""
        css_text = _read_text(path=CANVAS_WIDGET_CSS_PATH)
        tokens_text = _read_text(path=TOKENS_CSS_PATH)
        assert "--_dds-" not in css_text

        defined_tier_2_tokens = set(
            re.findall(pattern=r"(--dds-[a-z0-9-]+)\s*:", string=tokens_text)
        )
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector="dds-canvas-widget,\n  .dds-canvas-widget",
        )
        root_props = _extract_defined_properties(
            block_text="\n".join(root_blocks)
        )
        tier_3_props = {
            name: value
            for name, value in root_props.items()
            if name.startswith("--_")
        }
        assert tier_3_props
        for name, value in tier_3_props.items():
            assert name.startswith("--_canvas-widget-")
            match = re.fullmatch(
                pattern=r"var\((--dds-[a-z0-9-]+)\)",
                string=value,
            )
            assert match is not None
            assert match.group(1) in defined_tier_2_tokens

        mapped_values = " ".join(tier_3_props.values())
        for expected_family in (
            "--dds-surface-stage-",
            "--dds-surface-code-",
            "--dds-control-",
            "--dds-text-control-",
            "--dds-state-",
            "--dds-space-",
        ):
            assert expected_family in mapped_values

    def test_no_bem_single_quotes_and_alphabetized_declarations(self) -> None:
        """Verify zero BEM selectors, single quotes, and alphabetised declarations."""
        css_text = _read_text(path=CANVAS_WIDGET_CSS_PATH)
        assert '"' not in css_text
        assert "!important" not in css_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=css_text,
        )
        assert not bem_matches

        rule_blocks = re.findall(pattern=r"\{([^{}]+)\}", string=css_text)
        assert rule_blocks
        for block in rule_blocks:
            prop_names = re.findall(
                pattern=r"^\s*([a-z0-9_-]+)\s*:",
                string=block,
                flags=re.MULTILINE,
            )
            assert prop_names == sorted(prop_names)


class TestCanvasWidgetGalleryAndDocs:
    """Verify co-located gallery.py and index.md for dds__canvas_widget."""

    def test_gallery_config_variants_render(self) -> None:
        """Verify gallery.py exports a valid GalleryConfig whose variants all render."""
        assert CANVAS_WIDGET_GALLERY_PATH.is_file()
        reg = _make_registry()
        cfg = gallery.load_gallery_config(
            source_dir=CANVAS_WIDGET_DIR,
            component_name=COMPONENT_NAME,
        )
        assert isinstance(cfg, gallery.GalleryConfig)
        assert cfg.group == "Domain"
        assert len(cfg.variants) >= 3
        for variant in cfg.variants:
            spec = data.CanvasSpec(
                component_name=QUALIFIED_NAME,
                variant=variant.name,
            )
            rendered = canvas_service.render_component(
                spec=spec,
                registry=reg,
                raise_errors=True,
            )
            assert '<dds-canvas-widget class="dds-canvas-widget"' in rendered
            assert "data-canvas-iframe" in rendered

    def test_index_md_exists_and_documents_component(self) -> None:
        """Verify index.md exists and documents dds__canvas_widget and all parameters."""
        assert CANVAS_WIDGET_INDEX_MD_PATH.is_file()
        doc_text = _read_text(path=CANVAS_WIDGET_INDEX_MD_PATH)
        assert "dds__canvas_widget" in doc_text
        assert "dds-canvas-widget" in doc_text
        for param_name in (
            "canvas_id",
            "iframe_src",
            "iframe_srcdoc",
            "source_code",
            "rendered_html",
            "mode",
            "viewport",
            "background",
            "zoom",
            "sandbox_attrs",
            "title",
            "show_toggles",
        ):
            assert param_name in doc_text


class TestCanvasWidgetTypeScriptCustomElement:
    """Verify Light DOM <dds-canvas-widget> TypeScript contract in canvas_widget.ts."""

    def test_canvas_widget_ts_implements_custom_element_and_lifecycle_contract(
        self,
    ) -> None:
        """Verify canvas_widget.ts defines DDSCanvasWidgetElement, AbortController, and registration."""
        assert CANVAS_WIDGET_TS_PATH.is_file()
        ts_text = _read_text(path=CANVAS_WIDGET_TS_PATH)
        assert (
            "import type { DDSCustomElement } from '../../types.js';" in ts_text
        )
        assert "export class DDSCanvasWidgetElement" in ts_text
        assert "extends HTMLElement" in ts_text
        assert "implements DDSCustomElement {" in ts_text
        assert (
            "private abortController: AbortController | null = null;" in ts_text
        )
        assert "this.abortController?.abort();" in ts_text
        assert "this.abortController = new AbortController();" in ts_text
        assert "connectedCallback(): void {" in ts_text
        assert "disconnectedCallback(): void {" in ts_text
        assert "if (!customElements.get('dds-canvas-widget')) {" in ts_text
        assert (
            "customElements.define('dds-canvas-widget', DDSCanvasWidgetElement);"
            in ts_text
        )
        assert "attachShadow" not in ts_text
        assert "document.querySelector" not in ts_text
        assert '"' not in ts_text
        assert "\t" not in ts_text
        for line in ts_text.splitlines():
            assert len(line) <= 80
            assert line == line.rstrip()

    def test_canvas_widget_ts_implements_mode_resize_and_helper_methods(
        self,
    ) -> None:
        """Verify canvas_widget.ts handles mode switching, postMessage resize, and stage preset helpers."""
        ts_text = _read_text(path=CANVAS_WIDGET_TS_PATH)
        assert "'[data-canvas-mode]'" in ts_text
        assert "'[data-canvas-stage]'" in ts_text
        assert "`[data-canvas-panel='code']`" in ts_text
        assert "`[data-canvas-panel='html']`" in ts_text
        assert "'dds:canvas-mode-change'" in ts_text
        assert "detail: { canvasId, mode }" in ts_text
        assert "data.type !== 'canvas-resize'" in ts_text
        assert "data.id === this.dataset.canvasId" in ts_text
        assert "event.source === iframe.contentWindow" in ts_text
        assert "const clampedHeight = Math.max(24, Number(data.height));" in ts_text
        assert "iframe.style.height = `${clampedHeight}px`;" in ts_text
        assert "'--_canvas-widget-iframe-height'" in ts_text
        assert "'dds:canvas-resize'" in ts_text
        assert "detail: { canvasId, height: clampedHeight }" in ts_text
        assert "setViewport(viewport: string): void {" in ts_text
        assert "setBackground(background: string): void {" in ts_text
        assert "setZoom(zoom: string): void {" in ts_text
        assert (
            "const width = viewport === 'responsive' ? '100%' : `${viewport}px`;"
            in ts_text
        )
        assert (
            "this.style.setProperty('--_canvas-widget-viewport-width', width);"
            in ts_text
        )
