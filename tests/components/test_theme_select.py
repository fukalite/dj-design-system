"""Unit tests for the built-in ``dds__theme_select`` domain component."""

import pathlib
import re

import pytest
from django import template

from dj_design_system import data, gallery, types
from dj_design_system.components import base as components_base
from dj_design_system.components.domain import theme_select as theme_select_package
from dj_design_system.components.domain.theme_select import (
    theme_select as theme_select_module,
)
from dj_design_system.services import canvas as canvas_service
from dj_design_system.services import registry as registry_service
from tests import conftest


APP_LABEL = "dj_design_system"
COMPONENT_NAME = "theme_select"
QUALIFIED_NAME = "dds__theme_select"
RELATIVE_PATH = "domain.theme_select"
TEMPLATE_PATH = "dj_design_system/components/domain/theme_select/theme_select.html"
CSS_MEDIA_PATH = "dj_design_system/components/domain/theme_select/theme_select.css"
JS_MEDIA_PATH = "dj_design_system/components/domain/theme_select/theme_select.js"

THEME_SELECT_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "components"
    / "domain"
    / "theme_select"
)
THEME_SELECT_HTML_PATH = THEME_SELECT_DIR / "theme_select.html"
THEME_SELECT_CSS_PATH = THEME_SELECT_DIR / "theme_select.css"
THEME_SELECT_TS_PATH = THEME_SELECT_DIR / "theme_select.ts"
THEME_SELECT_INDEX_MD_PATH = THEME_SELECT_DIR / "index.md"


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


class TestThemeSelectDiscoveryAndMetadata:
    """Verify ThemeSelect class exports, metadata, media, and registry discovery."""

    def test_exported_from_package_init(self) -> None:
        """Verify ThemeSelect is exported in dj_design_system.components.domain.theme_select."""
        assert theme_select_package.ThemeSelect is theme_select_module.ThemeSelect
        assert issubclass(theme_select_module.ThemeSelect, components_base.TagComponent)

    def test_template_meta_and_media_declarations(self) -> None:
        """Verify ThemeSelect declares co-located template_name, positional_args, and Media."""
        assert theme_select_module.ThemeSelect.template_name == TEMPLATE_PATH
        assert theme_select_module.ThemeSelect.get_positional_args() == ["themes"]
        assert theme_select_module.ThemeSelect.Media.css == CSS_MEDIA_PATH
        assert theme_select_module.ThemeSelect.Media.js == JS_MEDIA_PATH

    def test_discovered_as_dds_theme_select_in_registry(self) -> None:
        """Verify ComponentRegistry discovers ThemeSelect as internal dds__theme_select."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.component_class is theme_select_module.ThemeSelect
        assert info.qualified_name == QUALIFIED_NAME
        assert info.relative_path == RELATIVE_PATH
        assert info.is_internal is True
        assert info.media.css == [CSS_MEDIA_PATH]
        assert info.media.js == [JS_MEDIA_PATH]

    def test_no_private_helper_methods_defined_on_component(self) -> None:
        """Verify ThemeSelect defines no private _-prefixed helper methods."""
        own_private_methods = [
            name
            for name, attr in theme_select_module.ThemeSelect.__dict__.items()
            if name.startswith("_") and not name.startswith("__") and callable(attr)
        ]
        assert not own_private_methods


class TestThemeSelectParametersAndContext:
    """Verify ThemeSelect parameter validation and get_context() shaping."""

    def test_default_parameters_when_themes_omitted(self) -> None:
        """Verify defaults when themes is None or empty."""
        comp = theme_select_module.ThemeSelect()
        ctx = comp.get_context()
        assert ctx["themes"] is None
        assert ctx["normalized_themes"] == []
        assert ctx["resolved_active_theme"] == "light"
        assert ctx["active_icon"] == "sun"
        assert ctx["has_themes"] is False
        assert ctx["has_multiple_themes"] is False
        assert ctx["label"] == "Global Theme"
        assert ctx["select_id"] == "gallery-global-theme-select"

    def test_normalizes_theme_dataclasses_dicts_and_strings(self) -> None:
        """Verify Theme objects, dicts, and strings normalize with value, label, icon, and is_selected."""
        themes_input = [
            types.Theme(value="light", label="Light Mode"),
            {"value": "dark", "label": "Dark Mode"},
            "solarized-dark",
        ]
        comp = theme_select_module.ThemeSelect(
            themes=themes_input,
            active_theme="dark",
            label="Canvas Theme",
            select_id="canvas-theme-select",
        )
        ctx = comp.get_context()
        assert ctx["resolved_active_theme"] == "dark"
        assert ctx["active_icon"] == "moon"
        assert ctx["has_themes"] is True
        assert ctx["has_multiple_themes"] is True
        assert ctx["label"] == "Canvas Theme"
        assert ctx["select_id"] == "canvas-theme-select"
        assert ctx["normalized_themes"] == [
            {
                "value": "light",
                "label": "Light Mode",
                "icon": "sun",
                "is_selected": False,
            },
            {
                "value": "dark",
                "label": "Dark Mode",
                "icon": "moon",
                "is_selected": True,
            },
            {
                "value": "solarized-dark",
                "label": "Solarized-dark",
                "icon": "moon",
                "is_selected": False,
            },
        ]

    def test_falls_back_to_first_theme_when_active_theme_unmatched(self) -> None:
        """Verify resolved_active_theme falls back to normalized_themes[0]['value'] when unmatched."""
        comp = theme_select_module.ThemeSelect(
            themes=[{"value": "dark-high-contrast", "label": "High Contrast"}],
            active_theme="nonexistent",
        )
        ctx = comp.get_context()
        assert ctx["resolved_active_theme"] == "dark-high-contrast"
        assert ctx["active_icon"] == "moon"
        assert ctx["has_themes"] is True
        assert ctx["has_multiple_themes"] is False
        assert ctx["normalized_themes"][0]["is_selected"] is True

    def test_empty_themes_with_dark_active_theme_sets_moon_icon(self) -> None:
        """Verify active_icon is moon when themes is empty and active_theme contains dark."""
        comp = theme_select_module.ThemeSelect(
            themes=[],
            active_theme="custom-dark",
        )
        ctx = comp.get_context()
        assert ctx["resolved_active_theme"] == "custom-dark"
        assert ctx["active_icon"] == "moon"
        assert ctx["has_themes"] is False
        assert ctx["has_multiple_themes"] is False

    def test_invalid_themes_type_raises_type_error(self) -> None:
        """Verify passing a non-list themes parameter raises TypeError."""
        with pytest.raises(expected_exception=TypeError, match="Expected list"):
            theme_select_module.ThemeSelect(themes="invalid")


class TestThemeSelectRenderingAndTemplate:
    """Verify template tag rendering, positional args, child icon, and template purity."""

    def test_renders_theme_select_via_positional_arg(self) -> None:
        """Verify {% dds__theme_select %} renders root custom element, icon, select, and options."""
        themes_list = [
            {"value": "light", "label": "Light"},
            {"value": "dark", "label": "Dark"},
        ]
        html = _render_template(
            source='{% dds__theme_select themes_list active_theme="dark" %}',
            context={"themes_list": themes_list},
        ).strip()
        assert (
            '<dds-theme-select class="dds-theme-select" data-active-theme="dark">'
            in html
        )
        assert "<div data-theme-control>" in html
        assert 'data-icon="moon"' in html
        assert 'data-size="sm"' in html
        assert (
            '<select id="gallery-global-theme-select" data-theme-select '
            'aria-label="Global Theme" title="Global Theme">' in html
        )
        assert '<option value="light">Light</option>' in html
        assert '<option value="dark" selected>Dark</option>' in html

    def test_renders_custom_label_and_select_id(self) -> None:
        """Verify custom label and select_id attributes render on the select element."""
        themes_list = [{"value": "light", "label": "Light"}]
        html = _render_template(
            source=(
                '{% dds__theme_select themes=themes_list label="Sandbox Theme" '
                'select_id="sandbox-theme" %}'
            ),
            context={"themes_list": themes_list},
        ).strip()
        assert 'data-active-theme="light"' in html
        assert 'data-icon="sun"' in html
        assert (
            '<select id="sandbox-theme" data-theme-select '
            'aria-label="Sandbox Theme" title="Sandbox Theme">' in html
        )
        assert '<option value="light" selected>Light</option>' in html

    def test_template_contains_no_filters_or_bem(self) -> None:
        """Verify theme_select.html loads design_components and has zero template filters or BEM classes."""
        template_text = _read_text(path=THEME_SELECT_HTML_PATH)
        assert "{% load design_components %}" in template_text
        assert "|" not in template_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=template_text,
        )
        assert not bem_matches


class TestThemeSelectStylesheet:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, and formatting in theme_select.css."""

    def test_wrapped_in_layer_blocks_and_sets_root_layout(self) -> None:
        """Verify theme_select.css wraps rules in @layer blocks and sets inline-flex and zero margin."""
        css_text = _read_text(path=THEME_SELECT_CSS_PATH)
        assert css_text.startswith("@layer blocks {")
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector="dds-theme-select,\n  .dds-theme-select",
        )
        assert root_blocks
        assert "align-items: center;" in root_blocks[0]
        assert "display: inline-flex;" in root_blocks[0]
        assert "margin: 0;" in root_blocks[0]

    def test_tier_3_tokens_map_exclusively_from_tier_2_tokens(self) -> None:
        """Verify dds-theme-select defines --_theme-select-* tokens mapped only from --dds-* tokens."""
        css_text = _read_text(path=THEME_SELECT_CSS_PATH)
        assert "--_dds-" not in css_text
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector="dds-theme-select,\n  .dds-theme-select",
        )
        root_props = _extract_defined_properties(block_text="\n".join(root_blocks))
        assert root_props
        for token_name, token_val in root_props.items():
            assert token_name.startswith("--_theme-select-")
            assert token_val.startswith("var(--dds-")

        mapped_values = " ".join(root_props.values())
        for expected_family in (
            "--dds-control-",
            "--dds-text-control-",
            "--dds-state-",
            "--dds-space-",
        ):
            assert expected_family in mapped_values

    def test_css_formatting_and_no_bem(self) -> None:
        """Verify zero BEM selectors, single quotes, and alphabetized declarations."""
        css_text = _read_text(path=THEME_SELECT_CSS_PATH)
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


class TestThemeSelectCustomElementTypeScript:
    """Verify Light DOM <dds-theme-select> TypeScript and DOM contract."""

    def test_ts_implements_custom_element_contract(self) -> None:
        """Verify theme_select.ts defines DDSThemeSelectElement, persistence, and dds:theme-change."""
        assert THEME_SELECT_TS_PATH.is_file()
        ts_text = _read_text(path=THEME_SELECT_TS_PATH)
        assert "import type { DDSCustomElement } from '../../types.js';" in ts_text
        assert (
            "export class DDSThemeSelectElement" in ts_text
            and "extends HTMLElement" in ts_text
            and "implements DDSCustomElement" in ts_text
        )
        assert "new AbortController()" in ts_text
        assert "this.abortController?.abort()" in ts_text
        assert "disconnectedCallback(): void" in ts_text
        assert "this.querySelector<HTMLSelectElement>(" in ts_text
        assert "'[data-theme-select]'" in ts_text
        assert "const theme = selectEl.value;" in ts_text
        assert "this.dataset.activeTheme = theme;" in ts_text
        assert "document.cookie =" in ts_text
        assert "'dds_theme=' +" in ts_text
        assert "encodeURIComponent(theme) +" in ts_text
        assert "'; path=/; max-age=31536000; SameSite=Lax';" in ts_text
        assert "window.localStorage.setItem('dds_theme', theme);" in ts_text
        assert "new CustomEvent('dds:theme-change'" in ts_text
        assert "bubbles: true," in ts_text
        assert "detail: { theme }," in ts_text
        assert "if (!customElements.get('dds-theme-select'))" in ts_text
        assert (
            "customElements.define('dds-theme-select', DDSThemeSelectElement);"
            in ts_text
        )
        assert "attachShadow" not in ts_text
        assert "document.querySelector" not in ts_text
        assert "document.getElementById" not in ts_text

    def test_ts_styleguide_formatting_and_jsdoc(self) -> None:
        """Verify theme_select.ts uses single quotes, <=80 chars per line, no tabs, and JSDoc."""
        ts_text = _read_text(path=THEME_SELECT_TS_PATH)
        assert '"' not in ts_text
        assert "\t" not in ts_text
        assert "@fileoverview" in ts_text
        assert "@param {HTMLSelectElement} selectEl" in ts_text
        for line in ts_text.splitlines():
            assert len(line) <= 80
            assert line == line.rstrip()


class TestThemeSelectGalleryAndDocs:
    """Verify co-located gallery.py and index.md for dds__theme_select."""

    def test_gallery_config_variants_render(self) -> None:
        """Verify gallery.py exports a valid GalleryConfig whose variants all render."""
        reg = _make_registry()
        cfg = gallery.load_gallery_config(
            source_dir=THEME_SELECT_DIR,
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
            assert "<dds-theme-select" in rendered
            assert 'class="dds-theme-select"' in rendered
            assert "data-theme-select" in rendered

    def test_index_md_exists_and_documents_component(self) -> None:
        """Verify index.md exists and documents dds__theme_select and <dds-theme-select>."""
        doc_text = _read_text(path=THEME_SELECT_INDEX_MD_PATH)
        assert "dds__theme_select" in doc_text
        assert "dds-theme-select" in doc_text
        assert "dds:theme-change" in doc_text
