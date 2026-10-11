"""Unit tests for the built-in ``dds__sandbox_toolbar`` domain component."""

import pathlib
import re

import pytest
from django import template

from dj_design_system import data, gallery
from dj_design_system.components import base as components_base
from dj_design_system.components.domain import (
    sandbox_toolbar as sandbox_toolbar_package,
)
from dj_design_system.components.domain.sandbox_toolbar import (
    sandbox_toolbar as sandbox_toolbar_module,
)
from dj_design_system.services import canvas as canvas_service
from dj_design_system.services import registry as registry_service
from dj_design_system.services import slot_node as slot_node_service
from tests import conftest


APP_LABEL = "dj_design_system"
COMPONENT_NAME = "sandbox_toolbar"
QUALIFIED_NAME = "dds__sandbox_toolbar"
RELATIVE_PATH = "domain.sandbox_toolbar"
TEMPLATE_PATH = (
    "dj_design_system/components/domain/sandbox_toolbar/sandbox_toolbar.html"
)
CSS_MEDIA_PATH = (
    "dj_design_system/components/domain/sandbox_toolbar/sandbox_toolbar.css"
)
JS_MEDIA_PATH = "dj_design_system/components/domain/sandbox_toolbar/sandbox_toolbar.js"

SANDBOX_TOOLBAR_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "components"
    / "domain"
    / "sandbox_toolbar"
)
SANDBOX_TOOLBAR_PY_PATH = SANDBOX_TOOLBAR_DIR / "sandbox_toolbar.py"
SANDBOX_TOOLBAR_HTML_PATH = SANDBOX_TOOLBAR_DIR / "sandbox_toolbar.html"
SANDBOX_TOOLBAR_CSS_PATH = SANDBOX_TOOLBAR_DIR / "sandbox_toolbar.css"
SANDBOX_TOOLBAR_TS_PATH = SANDBOX_TOOLBAR_DIR / "sandbox_toolbar.ts"
SANDBOX_TOOLBAR_INDEX_MD_PATH = SANDBOX_TOOLBAR_DIR / "index.md"


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
    context: dict[str, object] | None = None,
) -> str:
    """Render a Django template string with built-in dds component tags registered."""
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
    pattern = re.compile(
        pattern=rf"{escaped}\s*\{{([^}}]*)\}}",
        flags=re.DOTALL,
    )
    return pattern.findall(string=css_text)


def _extract_defined_properties(block_text: str) -> dict[str, str]:
    """Extract custom property definitions from a CSS block string."""
    matches = re.findall(
        pattern=r"(--[a-z0-9_-]+)\s*:\s*([^;]+);",
        string=block_text,
    )
    return {name: value.strip() for name, value in matches}


class TestSandboxToolbarDiscoveryAndMetadata:
    """Verify SandboxToolbar class exports, metadata, media, and registry discovery."""

    def test_exported_from_package_init(self) -> None:
        """Verify SandboxToolbar is exported in dj_design_system.components.domain.sandbox_toolbar."""
        assert (
            sandbox_toolbar_package.SandboxToolbar
            is sandbox_toolbar_module.SandboxToolbar
        )
        assert issubclass(
            sandbox_toolbar_module.SandboxToolbar,
            components_base.TagComponent,
        )

    def test_template_and_media_declarations(self) -> None:
        """Verify SandboxToolbar relies on co-located template_name and Media.css/js auto-discovery."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]
        assert info.media.js == [JS_MEDIA_PATH]

    def test_discovered_as_dds_sandbox_toolbar_in_registry(self) -> None:
        """Verify ComponentRegistry discovers SandboxToolbar as internal dds__sandbox_toolbar."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.component_class is sandbox_toolbar_module.SandboxToolbar
        assert info.qualified_name == QUALIFIED_NAME
        assert info.relative_path == RELATIVE_PATH
        assert info.is_internal is True
        assert info.media.css == [CSS_MEDIA_PATH]
        assert info.media.js == [JS_MEDIA_PATH]

    def test_no_private_helper_methods_or_inline_comments_in_component(
        self,
    ) -> None:
        """Verify SandboxToolbar defines no private _-prefixed helper methods or inline comments."""
        own_private_methods = [
            name
            for name, attr in sandbox_toolbar_module.SandboxToolbar.__dict__.items()
            if name.startswith("_") and not name.startswith("__") and callable(attr)
        ]
        assert not own_private_methods
        py_text = _read_text(path=SANDBOX_TOOLBAR_PY_PATH)
        assert "mark_safe" not in py_text
        assert "format_html" not in py_text
        for line in py_text.splitlines():
            assert not line.lstrip().startswith("#")


class TestSandboxToolbarParametersAndContext:
    """Verify SandboxToolbar parameter normalization and get_context() shaping."""

    def test_default_parameters_and_context_shaping(self) -> None:
        """Verify default backgrounds, viewports, zoom levels, and flags when instantiated empty."""
        comp = sandbox_toolbar_module.SandboxToolbar()
        ctx = comp.get_context()
        assert ctx["variants"] is None
        assert ctx["normalized_variants"] == []
        assert ctx["active_variant"] == ""
        assert ctx["active_variant_label"] == "Default"
        assert ctx["has_variants"] is False
        assert ctx["active_background"] == "white"
        assert ctx["active_background_label"] == "White"
        assert ctx["normalized_backgrounds"] == [
            {"value": "white", "label": "White", "is_selected": True},
            {"value": "light", "label": "Light", "is_selected": False},
            {"value": "dark", "label": "Dark", "is_selected": False},
        ]
        assert ctx["active_viewport"] == "responsive"
        assert ctx["active_viewport_label"] == "Responsive"
        assert len(ctx["normalized_viewports"]) == 7
        assert ctx["normalized_viewports"][0] == {
            "value": "responsive",
            "label": "Responsive",
            "is_selected": True,
        }
        assert ctx["active_zoom"] == "100"
        assert ctx["active_zoom_label"] == "100%"
        assert len(ctx["normalized_zoom_levels"]) == 6
        assert ctx["normalized_zoom_levels"][2] == {
            "value": "100",
            "label": "100%",
            "is_selected": True,
        }
        assert ctx["outline_active"] is False
        assert ctx["measure_active"] is False
        assert ctx["rtl_active"] is False
        assert ctx["has_canvas_url"] is False
        assert ctx["has_reset_url"] is False
        assert ctx["resolved_aria_label"] == "Sandbox controls"

    def test_normalizes_variant_instances_dicts_and_non_string_active_inputs(
        self,
    ) -> None:
        """Verify Variant instances, dicts, integer active_zoom, and URLs normalize in context."""
        primary_variant = gallery.Variant(
            name="primary",
            label="Primary Button",
        )
        variants_input = [
            primary_variant,
            {"name": "ghost", "label": "Ghost Button"},
            "danger",
        ]
        comp = sandbox_toolbar_module.SandboxToolbar(
            variants=variants_input,
            active_variant=primary_variant,
            component_url="/gallery/button/",
            backgrounds=[
                {"value": "light", "label": "Light Canvas"},
                {"value": "dark", "label": "Dark Canvas"},
            ],
            active_background="dark",
            viewports=[
                {"value": "320", "label": "Mobile 320px"},
                {"value": "1024", "label": "Desktop 1024px"},
            ],
            active_viewport="1024",
            zoom_levels=["75", "150"],
            active_zoom=150,
            outline_active=True,
            measure_active=True,
            rtl_active=True,
            canvas_url="/canvas/button/",
            reset_url="/gallery/button/?reset=1",
            aria_label="Custom sandbox toolbar",
        )
        assert comp.active_variant == "primary"
        assert comp.active_zoom == "150"

        ctx = comp.get_context()
        assert ctx["has_variants"] is True
        assert ctx["active_variant_label"] == "Primary Button"
        assert ctx["normalized_variants"] == [
            {
                "name": "primary",
                "label": "Primary Button",
                "href": "/gallery/button/?variant=primary",
                "is_selected": True,
            },
            {
                "name": "ghost",
                "label": "Ghost Button",
                "href": "/gallery/button/?variant=ghost",
                "is_selected": False,
            },
            {
                "name": "danger",
                "label": "Danger",
                "href": "/gallery/button/?variant=danger",
                "is_selected": False,
            },
        ]
        assert ctx["active_background"] == "dark"
        assert ctx["active_background_label"] == "Dark Canvas"
        assert ctx["active_viewport"] == "1024"
        assert ctx["active_viewport_label"] == "Desktop 1024px"
        assert ctx["active_zoom"] == "150"
        assert ctx["active_zoom_label"] == "150%"
        assert ctx["normalized_zoom_levels"] == [
            {"value": "75", "label": "75%", "is_selected": False},
            {"value": "150", "label": "150%", "is_selected": True},
        ]
        assert ctx["outline_active"] is True
        assert ctx["measure_active"] is True
        assert ctx["rtl_active"] is True
        assert ctx["has_canvas_url"] is True
        assert ctx["has_reset_url"] is True
        assert ctx["resolved_aria_label"] == "Custom sandbox toolbar"

    def test_unmatched_active_values_fall_back_gracefully(self) -> None:
        """Verify unmatched active_variant uses Default and unmatched background/viewport/zoom fall back."""
        comp = sandbox_toolbar_module.SandboxToolbar(
            variants=[{"name": "primary", "label": "Primary"}],
            active_variant="nonexistent",
            component_url="/gallery/button/?theme=dark",
            active_background="nonexistent",
            active_viewport="9999",
            active_zoom="999",
            aria_label="",
        )
        ctx = comp.get_context()
        assert ctx["active_variant_label"] == "Default"
        assert (
            ctx["normalized_variants"][0]["href"]
            == "/gallery/button/?theme=dark&variant=primary"
        )
        assert ctx["active_background"] == "white"
        assert ctx["active_background_label"] == "White"
        assert ctx["active_viewport"] == "responsive"
        assert ctx["active_viewport_label"] == "Responsive"
        assert ctx["active_zoom"] == "50"
        assert ctx["active_zoom_label"] == "50%"
        assert ctx["resolved_aria_label"] == "Sandbox controls"

    def test_invalid_list_parameter_raises_type_error(self) -> None:
        """Verify passing a non-list to ListParam attributes raises TypeError."""
        with pytest.raises(expected_exception=TypeError, match="Expected list"):
            sandbox_toolbar_module.SandboxToolbar(variants="invalid")
        with pytest.raises(expected_exception=TypeError, match="Expected list"):
            sandbox_toolbar_module.SandboxToolbar(backgrounds="invalid")
        with pytest.raises(expected_exception=TypeError, match="Expected list"):
            sandbox_toolbar_module.SandboxToolbar(viewports="invalid")
        with pytest.raises(expected_exception=TypeError, match="Expected list"):
            sandbox_toolbar_module.SandboxToolbar(zoom_levels="invalid")


class TestSandboxToolbarRenderingAndTemplate:
    """Verify template tag rendering, child components, and template purity."""

    def test_renders_default_sandbox_toolbar_controls_and_toggles(self) -> None:
        """Verify default {% dds__sandbox_toolbar %} renders toolbar landmark, popouts, and toggles."""
        html = _render_template(source="{% dds__sandbox_toolbar %}").strip()
        assert (
            '<dds-sandbox-toolbar class="dds-sandbox-toolbar" data-surface="sandbox" '
            'role="toolbar" aria-label="Sandbox controls">' in html
        )
        assert "<l-cluster data-sandbox-controls>" in html
        assert 'data-sandbox-control="variant"' not in html
        assert 'data-sandbox-control="background"' in html
        assert 'data-sandbox-control="viewport"' in html
        assert 'data-sandbox-control="zoom"' in html
        assert '<div data-sandbox-toggles class="l-cluster">' in html
        assert 'data-action="toggle-outline"' in html
        assert 'data-icon="box-model"' in html
        assert 'data-action="toggle-measure"' in html
        assert 'data-icon="ruler"' in html
        assert 'data-action="toggle-rtl"' in html
        assert 'data-icon="rtl"' in html
        assert 'data-action="reset-params"' not in html
        assert 'target="_blank"' not in html

    def test_renders_variants_reset_and_canvas_links_when_provided(self) -> None:
        """Verify variants popout, reset button, and standalone canvas link render when configured."""
        variants = [
            {"name": "primary", "label": "Primary"},
            {"name": "ghost", "label": "Ghost"},
        ]
        html = _render_template(
            source=(
                "{% dds__sandbox_toolbar variants=variants "
                'active_variant="primary" component_url="/gallery/button/" '
                "outline_active=True measure_active=True rtl_active=True "
                'reset_url="/gallery/button/" canvas_url="/canvas/button/" %}'
            ),
            context={"variants": variants},
        ).strip()
        assert 'data-sandbox-control="variant"' in html
        assert "<span>Primary</span>" in html
        assert 'href="/gallery/button/?variant=primary"' in html
        assert 'href="/gallery/button/?variant=ghost"' in html
        assert 'aria-pressed="true"' in html
        assert 'data-action="reset-params"' in html
        assert 'href="/gallery/button/"' in html
        assert 'href="/canvas/button/"' in html
        assert 'target="_blank"' in html

    def test_template_contains_no_filters_or_bem(self) -> None:
        """Verify sandbox_toolbar.html loads design_components and has zero template filters or BEM."""
        template_text = _read_text(path=SANDBOX_TOOLBAR_HTML_PATH)
        assert "{% load design_components %}" in template_text
        assert "|" not in template_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=template_text,
        )
        assert not bem_matches


class TestSandboxToolbarStylesheet:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, and formatting in sandbox_toolbar.css."""

    def test_wrapped_in_layer_blocks_and_sets_root_layout(self) -> None:
        """Verify sandbox_toolbar.css wraps rules in @layer blocks and sets zero outer margin."""
        css_text = _read_text(path=SANDBOX_TOOLBAR_CSS_PATH)
        assert css_text.startswith("@layer blocks {")
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-sandbox-toolbar",
        )
        assert root_blocks
        assert "display: block;" in root_blocks[0]
        assert "margin: 0;" in root_blocks[0]

    def test_tier_3_tokens_map_exclusively_from_tier_2_tokens(self) -> None:
        """Verify .dds-sandbox-toolbar defines --_sandbox-toolbar-* tokens mapped only from --dds-* tokens."""
        css_text = _read_text(path=SANDBOX_TOOLBAR_CSS_PATH)
        assert "--_dds-" not in css_text
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-sandbox-toolbar",
        )
        root_props = _extract_defined_properties(block_text="\n".join(root_blocks))
        assert root_props
        for token_name, token_val in root_props.items():
            assert token_name.startswith("--_sandbox-toolbar-")
            assert token_val.startswith("var(--dds-")

        mapped_values = " ".join(root_props.values())
        for expected_family in (
            "--dds-surface-sandbox-",
            "--dds-control-",
            "--dds-text-control-",
            "--dds-state-",
            "--dds-space-",
        ):
            assert expected_family in mapped_values

    def test_css_formatting_and_no_bem(self) -> None:
        """Verify zero BEM selectors, single quotes, and alphabetized declarations."""
        css_text = _read_text(path=SANDBOX_TOOLBAR_CSS_PATH)
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


class TestSandboxToolbarCustomElementTypeScript:
    """Verify Light DOM <dds-sandbox-toolbar> TypeScript contract in sandbox_toolbar.ts."""

    def test_ts_implements_custom_element_and_event_dispatch_contract(self) -> None:
        """Verify sandbox_toolbar.ts defines DDSSandboxToolbarElement and dispatches semantic events."""
        assert SANDBOX_TOOLBAR_TS_PATH.is_file()
        ts_text = _read_text(path=SANDBOX_TOOLBAR_TS_PATH)
        assert "import type { DDSCustomElement } from '../../types.js';" in ts_text
        assert (
            "export class DDSSandboxToolbarElement" in ts_text
            and "extends HTMLElement" in ts_text
            and "implements DDSCustomElement" in ts_text
        )
        assert "AbortController" in ts_text
        assert "connectedCallback(): void" in ts_text
        assert "disconnectedCallback(): void" in ts_text
        assert "'dds:popout-select'" in ts_text
        assert "'dds:sandbox-bg'" in ts_text
        assert "'dds:sandbox-viewport'" in ts_text
        assert "'dds:sandbox-zoom'" in ts_text
        assert "'dds:sandbox-toggle'" in ts_text
        assert "'dds:sandbox-reset'" in ts_text
        assert "if (!customElements.get('dds-sandbox-toolbar'))" in ts_text
        assert (
            "customElements.define('dds-sandbox-toolbar', DDSSandboxToolbarElement);"
            in ts_text
        )
        assert "attachShadow" not in ts_text
        assert "document.querySelector" not in ts_text
        assert '"' not in ts_text
        assert "\t" not in ts_text
        for line in ts_text.splitlines():
            assert len(line) <= 80
            assert line == line.rstrip()


class TestSandboxToolbarGalleryAndDocs:
    """Verify co-located gallery.py and index.md for dds__sandbox_toolbar."""

    def test_gallery_config_variants_render(self) -> None:
        """Verify gallery.py exports a valid GalleryConfig whose variants all render."""
        reg = _make_registry()
        cfg = gallery.load_gallery_config(
            source_dir=SANDBOX_TOOLBAR_DIR,
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
            assert 'class="dds-sandbox-toolbar"' in rendered
            assert 'role="toolbar"' in rendered

    def test_index_md_exists_and_documents_component(self) -> None:
        """Verify index.md exists and documents dds__sandbox_toolbar."""
        doc_text = _read_text(path=SANDBOX_TOOLBAR_INDEX_MD_PATH)
        assert "dds__sandbox_toolbar" in doc_text
        assert "dds-sandbox-toolbar" in doc_text
