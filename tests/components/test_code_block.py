"""Unit tests for the built-in ``dds__code_block`` element component."""

import pathlib
import re

import pytest
from django import template

from dj_design_system import data, gallery
from dj_design_system.components import base as components_base
from dj_design_system.components.elements import code_block as code_block_package
from dj_design_system.components.elements.code_block import (
    code_block as code_block_module,
)
from dj_design_system.services import canvas as canvas_service
from dj_design_system.services import registry as registry_service
from tests import conftest


GalleryConfig = gallery.GalleryConfig
load_gallery_config = gallery.load_gallery_config


APP_LABEL = "dj_design_system"
COMPONENT_NAME = "code_block"
QUALIFIED_NAME = "dds__code_block"
RELATIVE_PATH = "elements.code_block"
TEMPLATE_PATH = "dj_design_system/components/elements/code_block/code_block.html"
CSS_MEDIA_PATH = "dj_design_system/components/elements/code_block/code_block.css"
JS_MEDIA_PATH = "dj_design_system/components/elements/code_block/code_block.js"

CODE_BLOCK_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "components"
    / "elements"
    / "code_block"
)
CODE_BLOCK_HTML_PATH = CODE_BLOCK_DIR / "code_block.html"
CODE_BLOCK_CSS_PATH = CODE_BLOCK_DIR / "code_block.css"
CODE_BLOCK_TS_PATH = CODE_BLOCK_DIR / "code_block.ts"
CODE_BLOCK_INDEX_MD_PATH = CODE_BLOCK_DIR / "index.md"


def _make_registry() -> registry_service.ComponentRegistry:
    """Create a ComponentRegistry populated with built-in dj_design_system components."""
    reg = registry_service.ComponentRegistry()
    conftest.discover_app_into_registry(
        reg=reg,
        app_name=APP_LABEL,
        app_label=APP_LABEL,
    )
    return reg


def _render_template(source: str, context: dict[str, object] | None = None) -> str:
    """Render a Django template string with built-in dds component tags registered."""
    reg = _make_registry()
    engine = template.engines["django"].engine
    lib = template.Library()
    reg.register_templatetags(library=lib)
    previous = engine.template_libraries.get("design_components")
    engine.template_libraries["design_components"] = lib
    try:
        compiled = template.Template(
            template_string="{% load design_components %}" + source
        )
        return compiled.render(context=template.Context(dict_=context or {}))
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
    pattern = re.compile(pattern=rf"{escaped}\s*\{{([^}}]*)\}}", flags=re.DOTALL)
    return pattern.findall(string=css_text)


def _extract_defined_properties(block_text: str) -> dict[str, str]:
    """Extract custom property definitions from a CSS block string."""
    matches = re.findall(
        pattern=r"(--[a-z0-9_-]+)\s*:\s*([^;]+);",
        string=block_text,
    )
    return {name: value.strip() for name, value in matches}


class TestCodeBlockDiscoveryAndMetadata:
    """Verify CodeBlock class exports, metadata, media, and registry discovery."""

    def test_exported_from_package_init(self) -> None:
        """Verify CodeBlock is exported in dj_design_system.components.elements.code_block."""
        assert code_block_package.CodeBlock is code_block_module.CodeBlock
        assert issubclass(code_block_module.CodeBlock, components_base.TagComponent)

    def test_template_meta_and_media_declarations(self) -> None:
        """Verify CodeBlock relies on co-located template_name, positional_args, and Media."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.template_name == TEMPLATE_PATH
        assert code_block_module.CodeBlock.get_positional_args() == ["code"]
        assert info.media.css == [CSS_MEDIA_PATH]
        assert info.media.js == [JS_MEDIA_PATH]

    def test_discovered_as_dds_code_block_in_registry(self) -> None:
        """Verify ComponentRegistry discovers CodeBlock as internal dds__code_block."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.component_class is code_block_module.CodeBlock
        assert info.qualified_name == QUALIFIED_NAME
        assert info.relative_path == RELATIVE_PATH
        assert info.is_internal is True
        assert info.media.css == [CSS_MEDIA_PATH]
        assert info.media.js == [JS_MEDIA_PATH]


class TestCodeBlockParametersAndContext:
    """Verify CodeBlock parameter validation and get_context() shaping."""

    def test_default_parameters_and_context_shaping(self) -> None:
        """Verify default language='django', title='', copyable=True, stripped_code, and highlighted_code."""
        comp = code_block_module.CodeBlock(code="\r\n{% dds__icon 'copy' %}\n\r")
        ctx = comp.get_context()
        assert ctx["code"] == "\r\n{% dds__icon 'copy' %}\n\r"
        assert ctx["stripped_code"] == "{% dds__icon 'copy' %}"
        assert '<span class="cp">{%</span>' in ctx["highlighted_code"]
        assert "dds__icon" in ctx["highlighted_code"]
        assert ctx["language"] == "django"
        assert ctx["title"] == ""
        assert ctx["copyable"] is True
        assert ctx["has_title"] is False
        assert ctx["has_language"] is True
        assert ctx["header_label"] == "django"
        assert ctx["show_header"] is False
        assert ctx["show_overlay_copy"] is True

    def test_title_overrides_language_for_header_label(self) -> None:
        """Verify explicit title takes precedence over language in header_label and shows header."""
        comp = code_block_module.CodeBlock(
            code="print('ok')",
            language="python",
            title="example.py",
        )
        ctx = comp.get_context()
        assert ctx["has_title"] is True
        assert ctx["has_language"] is True
        assert ctx["header_label"] == "example.py"
        assert ctx["show_header"] is True
        assert ctx["show_overlay_copy"] is False
        assert '<span class="nb">print</span>' in ctx["highlighted_code"]

    def test_show_header_and_overlay_copy_states(self) -> None:
        """Verify show_header requires explicit title and show_overlay_copy handles untitled copyable blocks."""
        copy_only = code_block_module.CodeBlock(
            code="x = 1",
            language="",
            title="",
            copyable=True,
        ).get_context()
        assert copy_only["header_label"] == ""
        assert copy_only["show_header"] is False
        assert copy_only["show_overlay_copy"] is True

        label_only = code_block_module.CodeBlock(
            code="x = 1",
            language="python",
            title="",
            copyable=False,
        ).get_context()
        assert label_only["header_label"] == "python"
        assert label_only["show_header"] is False
        assert label_only["show_overlay_copy"] is False

        neither = code_block_module.CodeBlock(
            code="x = 1",
            language="",
            title="",
            copyable=False,
        ).get_context()
        assert neither["has_title"] is False
        assert neither["has_language"] is False
        assert neither["header_label"] == ""
        assert neither["show_header"] is False
        assert neither["show_overlay_copy"] is False

    def test_invalid_code_type_raises_type_error(self) -> None:
        """Verify passing a non-string code parameter raises TypeError."""
        with pytest.raises(expected_exception=TypeError, match="Expected str"):
            code_block_module.CodeBlock(code=None)


class TestCodeBlockRenderingAndTemplate:
    """Verify template tag rendering, positional args, HTML escaping, and template purity."""

    def test_renders_default_code_block_via_positional_arg(self) -> None:
        """Verify {% dds__code_block %} renders dds-code-block, overlay copy button, and pre/code."""
        html = _render_template(
            source="{% dds__code_block raw_code %}",
            context={"raw_code": "\n<div>Hello</div>\n"},
        ).strip()
        assert (
            '<dds-code-block class="dds-code-block" data-surface="code" data-language="django">'
            in html
        )
        assert "<header" not in html
        assert (
            '<button type="button" data-copy-trigger data-copy-overlay aria-label="Copy code">'
            in html
        )
        assert 'data-icon="copy"' in html
        assert 'data-size="sm"' in html
        assert "<span data-copy-status>Copy</span>" in html
        assert (
            "<pre><code data-code-content>&lt;div&gt;Hello&lt;/div&gt;</code></pre>"
            in html
        )

    def test_renders_with_title_and_copyable_false(self) -> None:
        """Verify explicit title renders header with [data-code-label] and copyable=False omits copy button."""
        html = _render_template(
            source='{% dds__code_block code="x = 1" language="python" title="app.py" copyable=False %}'
        ).strip()
        assert 'data-language="python"' in html
        assert '<header class="l-cluster">' in html
        assert "<span data-code-label>app.py</span>" in html
        assert "data-copy-trigger" not in html
        assert (
            '<pre><code data-code-content><span class="n">x</span> '
            '<span class="o">=</span> <span class="mi">1</span></code></pre>'
            in html
        )

    def test_omits_header_when_no_label_and_not_copyable(self) -> None:
        """Verify <header> and copy button are omitted when language='', title='', and copyable=False."""
        html = _render_template(
            source='{% dds__code_block code="plain" language="" title="" copyable=False %}'
        ).strip()
        assert "<header" not in html
        assert "data-code-label" not in html
        assert "data-copy-trigger" not in html
        assert "<pre><code data-code-content>plain</code></pre>" in html

    def test_template_contains_no_filters_or_bem(self) -> None:
        """Verify code_block.html loads design_components and has zero template filters or BEM classes."""
        template_text = _read_text(path=CODE_BLOCK_HTML_PATH)
        assert "{% load design_components %}" in template_text
        assert "|" not in template_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=template_text,
        )
        assert not bem_matches


class TestCodeBlockStylesheet:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, pre/code resets, and formatting in code_block.css."""

    def test_wrapped_in_layer_blocks_and_sets_display_block_and_zero_margin(
        self,
    ) -> None:
        """Verify code_block.css wraps rules in @layer blocks and sets display: block; margin: 0 on dds-code-block."""
        css_text = _read_text(path=CODE_BLOCK_CSS_PATH)
        assert css_text.startswith("@layer blocks {")
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector="dds-code-block",
        )
        assert root_blocks
        assert "display: block;" in root_blocks[0]
        assert "margin: 0;" in root_blocks[0]

    def test_tier_3_tokens_map_exclusively_from_tier_2_tokens(self) -> None:
        """Verify dds-code-block defines --_code-block-* tokens mapped only from --dds-* tokens."""
        css_text = _read_text(path=CODE_BLOCK_CSS_PATH)
        assert "--_dds-" not in css_text
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector="dds-code-block",
        )
        root_props = _extract_defined_properties(block_text="\n".join(root_blocks))
        assert root_props
        for token_name, token_val in root_props.items():
            assert token_name.startswith("--_code-block-")
            assert token_val.startswith("var(--dds-")

        mapped_values = " ".join(root_props.values())
        for expected_family in (
            "--dds-surface-",
            "--dds-text-code-",
            "--dds-text-caption-",
            "--dds-control-",
            "--dds-state-",
            "--dds-space-",
        ):
            assert expected_family in mapped_values

    def test_pre_and_code_formatting_resets(self) -> None:
        """Verify pre/code rules enforce white-space: pre, tab-size: 4, overflow-x: auto, and font-variant-ligatures: none."""
        css_text = _read_text(path=CODE_BLOCK_CSS_PATH)
        pre_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector="dds-code-block pre",
        )
        assert pre_blocks
        pre_block = pre_blocks[0]
        assert "font-variant-ligatures: none;" in pre_block
        assert "overflow-x: auto;" in pre_block
        assert "tab-size: 4;" in pre_block
        assert "white-space: pre;" in pre_block

    def test_css_formatting_and_no_bem(self) -> None:
        """Verify zero BEM selectors, single quotes, and alphabetized declarations."""
        css_text = _read_text(path=CODE_BLOCK_CSS_PATH)
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


class TestCodeBlockCustomElementTypeScript:
    """Verify Light DOM <dds-code-block> TypeScript source contract."""

    def test_ts_implements_custom_element_contract(self) -> None:
        """Verify code_block.ts defines DDSCodeBlockElement, AbortController, DOM queries, and dds:copy event."""
        ts_text = _read_text(path=CODE_BLOCK_TS_PATH)
        assert "import type { DDSCustomElement } from '../../types.js';" in ts_text
        assert (
            "export class DDSCodeBlockElement" in ts_text
            and "extends HTMLElement" in ts_text
            and "implements DDSCustomElement" in ts_text
        )
        assert "new AbortController()" in ts_text
        assert "disconnectedCallback()" in ts_text
        assert "[data-copy-trigger]" in ts_text
        assert "[data-code-content]" in ts_text
        assert "[data-copy-status]" in ts_text
        assert "navigator.clipboard?.writeText(code)" in ts_text
        assert "this.setAttribute('data-copied', 'true')" in ts_text
        assert "statusEl.textContent = 'Copied'" in ts_text
        assert "new CustomEvent('dds:copy'" in ts_text
        assert "customElements.define('dds-code-block', DDSCodeBlockElement)" in ts_text
        assert "attachShadow" not in ts_text
        assert "document.querySelector" not in ts_text


class TestCodeBlockGalleryAndDocs:
    """Verify co-located gallery.py and index.md for dds__code_block."""

    def test_gallery_config_variants_render(self) -> None:
        """Verify gallery.py exports a valid GalleryConfig whose variants all render."""
        reg = _make_registry()
        cfg = load_gallery_config(
            source_dir=CODE_BLOCK_DIR,
            component_name=COMPONENT_NAME,
        )
        assert isinstance(cfg, GalleryConfig)
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
            assert "<dds-code-block" in rendered
            assert 'class="dds-code-block"' in rendered
            assert 'data-surface="code"' in rendered

    def test_index_md_exists_and_documents_component(self) -> None:
        """Verify index.md exists and documents dds__code_block and <dds-code-block>."""
        doc_text = _read_text(path=CODE_BLOCK_INDEX_MD_PATH)
        assert "dds__code_block" in doc_text
        assert "dds-code-block" in doc_text
        assert "dds:copy" in doc_text
