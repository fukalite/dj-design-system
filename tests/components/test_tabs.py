"""Unit tests for the built-in ``dds__tabs`` element component."""

import dataclasses
import pathlib
import re

import pytest
from django import template
from django.utils import safestring

from dj_design_system import data, gallery
from dj_design_system.components import base as components_base
from dj_design_system.components.elements import tabs as tabs_package
from dj_design_system.components.elements.tabs import tabs as tabs_module
from dj_design_system.services import canvas as canvas_service
from dj_design_system.services import registry as registry_service
from tests import conftest


APP_LABEL = "dj_design_system"
COMPONENT_NAME = "tabs"
QUALIFIED_NAME = "dds__tabs"
RELATIVE_PATH = "elements.tabs"
TEMPLATE_PATH = "dj_design_system/components/elements/tabs/tabs.html"
CSS_MEDIA_PATH = "dj_design_system/components/elements/tabs/tabs.css"
JS_MEDIA_PATH = "dj_design_system/components/elements/tabs/tabs.js"

TABS_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "components"
    / "elements"
    / "tabs"
)
TABS_PY_PATH = TABS_DIR / "tabs.py"
TABS_HTML_PATH = TABS_DIR / "tabs.html"
TABS_CSS_PATH = TABS_DIR / "tabs.css"
TABS_TS_PATH = TABS_DIR / "tabs.ts"
TABS_INDEX_MD_PATH = TABS_DIR / "index.md"


@dataclasses.dataclass(frozen=True)
class TabItemStub:
    """Typed tab item stub used to verify object attribute normalization."""

    id: str
    label: str
    icon: str | None = None
    badge: str | None = None
    content: str | None = None


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


class TestTabsDiscoveryAndMetadata:
    """Verify Tabs class exports, metadata, media, and registry discovery."""

    def test_exported_from_package_init(self) -> None:
        """Verify Tabs is exported in dj_design_system.components.elements.tabs."""
        assert tabs_package.Tabs is tabs_module.Tabs
        assert issubclass(tabs_module.Tabs, components_base.BlockComponent)

    def test_template_media_and_positional_args(self) -> None:
        """Verify Tabs declares co-located template_name, Media.css, Media.js, and positional_args."""
        assert tabs_module.Tabs.template_name == TEMPLATE_PATH
        assert tabs_module.Tabs.Media.css == CSS_MEDIA_PATH
        assert tabs_module.Tabs.Media.js == JS_MEDIA_PATH
        assert tabs_module.Tabs.get_positional_args() == ["tabs"]

    def test_discovered_as_dds_tabs_in_registry(self) -> None:
        """Verify ComponentRegistry discovers Tabs as internal dds__tabs."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.component_class is tabs_module.Tabs
        assert info.qualified_name == QUALIFIED_NAME
        assert info.relative_path == RELATIVE_PATH
        assert info.is_internal is True
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]
        assert info.media.js == [JS_MEDIA_PATH]


class TestTabsParametersAndContext:
    """Verify parameter validation and get_context() normalization."""

    def test_default_parameters_and_empty_context(self) -> None:
        """Verify default parameters produce empty normalized_tabs and resolved_active=''."""
        comp = tabs_module.Tabs()
        ctx = comp.get_context()
        assert comp.tabs == []
        assert comp.active_tab == ""
        assert ctx["aria_label"] == "Tabs"
        assert ctx["resolved_active"] == ""
        assert ctx["normalized_tabs"] == []
        assert ctx["has_inline_panels"] is False
        assert ctx["has_slot_content"] is False

    def test_normalizes_dict_items_and_defaults_to_first_tab(self) -> None:
        """Verify dict items normalize all fields and default resolved_active to first tab."""
        comp = tabs_module.Tabs(
            tabs=[
                {
                    "id": "overview",
                    "label": "Overview",
                    "icon": "eye",
                    "content": "Overview panel",
                },
                {
                    "id": "code",
                    "label": "Code",
                    "badge": "HTML",
                    "content": "Code panel",
                },
            ]
        )
        ctx = comp.get_context()
        assert ctx["resolved_active"] == "overview"
        assert ctx["has_inline_panels"] is True
        assert ctx["has_slot_content"] is False
        assert ctx["normalized_tabs"] == [
            {
                "id": "overview",
                "label": "Overview",
                "icon": "eye",
                "has_icon": True,
                "badge": "",
                "has_badge": False,
                "content": "Overview panel",
                "has_content": True,
                "tab_dom_id": "dds-tab-overview",
                "panel_dom_id": "dds-panel-overview",
                "is_active": True,
                "aria_selected": "true",
                "tabindex": "0",
            },
            {
                "id": "code",
                "label": "Code",
                "icon": "",
                "has_icon": False,
                "badge": "HTML",
                "has_badge": True,
                "content": "Code panel",
                "has_content": True,
                "tab_dom_id": "dds-tab-code",
                "panel_dom_id": "dds-panel-code",
                "is_active": False,
                "aria_selected": "false",
                "tabindex": "-1",
            },
        ]

    def test_normalizes_object_items_and_honours_matching_active_tab(self) -> None:
        """Verify object items normalize and matching active_tab selects that tab."""
        comp = tabs_module.Tabs(
            tabs=[
                TabItemStub(id="first", label="First"),
                TabItemStub(
                    id="second",
                    label="Second",
                    icon="doc",
                    badge="New",
                ),
            ],
            active_tab="second",
            aria_label="Custom tabs",
            content=safestring.mark_safe(s="  <div role='tabpanel'>Slot</div>  "),
        )
        ctx = comp.get_context()
        assert ctx["aria_label"] == "Custom tabs"
        assert ctx["resolved_active"] == "second"
        assert ctx["has_inline_panels"] is False
        assert ctx["has_slot_content"] is True
        assert ctx["normalized_tabs"][0]["is_active"] is False
        assert ctx["normalized_tabs"][0]["aria_selected"] == "false"
        assert ctx["normalized_tabs"][0]["tabindex"] == "-1"
        assert ctx["normalized_tabs"][1]["is_active"] is True
        assert ctx["normalized_tabs"][1]["aria_selected"] == "true"
        assert ctx["normalized_tabs"][1]["tabindex"] == "0"
        assert ctx["normalized_tabs"][1]["has_icon"] is True
        assert ctx["normalized_tabs"][1]["has_badge"] is True

    def test_unknown_active_tab_falls_back_to_first_tab(self) -> None:
        """Verify an unrecognized active_tab falls back to the first tab's ID."""
        comp = tabs_module.Tabs(
            tabs=[
                {"id": "alpha", "label": "Alpha"},
                {"id": "beta", "label": "Beta"},
            ],
            active_tab="nonexistent",
        )
        ctx = comp.get_context()
        assert ctx["resolved_active"] == "alpha"
        assert ctx["normalized_tabs"][0]["is_active"] is True
        assert ctx["normalized_tabs"][1]["is_active"] is False

    def test_invalid_tabs_type_raises_type_error(self) -> None:
        """Verify passing a non-list to tabs raises TypeError."""
        with pytest.raises(expected_exception=TypeError, match="Expected list"):
            tabs_module.Tabs(tabs="invalid")

    def test_python_module_contains_no_html_building_or_child_instantiation(
        self,
    ) -> None:
        """Verify tabs.py contains no HTML string building or child component imports."""
        py_text = _read_text(path=TABS_PY_PATH)
        assert "format_html" not in py_text
        assert "mark_safe" not in py_text
        assert "Icon(" not in py_text
        assert "Badge(" not in py_text


class TestTabsRenderingAndTemplate:
    """Verify template tag rendering, child composition, panel branching, and purity."""

    def test_renders_tablist_triggers_and_inline_panels(self) -> None:
        """Verify <dds-tabs>, tablist, tab triggers, icons, badges, and inline panels render."""
        items = [
            {
                "id": "preview",
                "label": "Preview",
                "icon": "eye",
                "content": "Preview body",
            },
            {
                "id": "code",
                "label": "Source",
                "badge": "2",
                "content": "Source body",
            },
        ]
        html = _render_template(
            source='{% dds__tabs tabs active_tab="code" aria_label="View modes" %}{% enddds__tabs %}',
            context={"tabs": items},
        )
        assert '<dds-tabs class="dds-tabs" data-active-tab="code">' in html
        assert '<div role="tablist" aria-label="View modes" class="l-cluster">' in html
        assert (
            '<button type="button" role="tab" id="dds-tab-preview" '
            'data-tab-trigger="preview" aria-selected="false" '
            'aria-controls="dds-panel-preview" tabindex="-1">'
        ) in html
        assert (
            '<button type="button" role="tab" id="dds-tab-code" '
            'data-tab-trigger="code" aria-selected="true" '
            'aria-controls="dds-panel-code" tabindex="0">'
        ) in html
        assert 'data-icon="eye"' in html
        assert 'data-size="sm"' in html
        assert 'class="dds-badge"' in html
        assert (
            '<div role="tabpanel" id="dds-panel-preview" '
            'data-tab-panel="preview" aria-labelledby="dds-tab-preview" hidden>'
            "Preview body</div>"
        ) in html
        assert (
            '<div role="tabpanel" id="dds-panel-code" '
            'data-tab-panel="code" aria-labelledby="dds-tab-code">'
            "Source body</div>"
        ) in html

    def test_renders_slotted_custom_panels(self) -> None:
        """Verify block body content renders when supplied by the caller."""
        items = [
            {"id": "one", "label": "One"},
            {"id": "two", "label": "Two"},
        ]
        html = _render_template(
            source=(
                "{% dds__tabs tabs=items %}"
                '<div role="tabpanel" id="dds-panel-one" data-tab-panel="one">Custom 1</div>'
                "{% enddds__tabs %}"
            ),
            context={"items": items},
        )
        assert (
            '<div role="tabpanel" id="dds-panel-one" data-tab-panel="one">Custom 1</div>'
            in html
        )

    def test_escapes_untrusted_labels_and_inline_content(self) -> None:
        """Verify untrusted HTML in tab labels and string content is escaped."""
        items = [
            {
                "id": "xss",
                "label": "<script>alert(1)</script>",
                "content": "<img src=x onerror=alert(1)>",
            }
        ]
        html = _render_template(
            source="{% dds__tabs tabs=items %}{% enddds__tabs %}",
            context={"items": items},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
        assert "&lt;img src=x onerror=alert(1)&gt;" in html

    def test_template_contains_no_filters_or_bem(self) -> None:
        """Verify tabs.html loads design_components and has zero filters or BEM classes."""
        template_text = _read_text(path=TABS_HTML_PATH)
        assert template_text.startswith("{% load design_components %}")
        assert "|" not in template_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=template_text,
        )
        assert not bem_matches


class TestTabsStylesheet:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, and formatting in tabs.css."""

    def test_wrapped_in_layer_blocks_and_sets_block_display_and_zero_margin(
        self,
    ) -> None:
        """Verify tabs.css wraps rules in @layer blocks and sets display: block; margin: 0."""
        css_text = _read_text(path=TABS_CSS_PATH)
        assert css_text.startswith("@layer blocks {")
        root_blocks = _extract_rule_blocks(css_text=css_text, selector="dds-tabs")
        assert root_blocks
        assert "display: block;" in root_blocks[0]
        assert "margin: 0;" in root_blocks[0]

    def test_tier_3_tokens_map_exclusively_from_tier_2_tokens(self) -> None:
        """Verify all --_tabs-* tokens map exclusively from Tier 2 --dds-* tokens."""
        css_text = _read_text(path=TABS_CSS_PATH)
        assert "--_dds-" not in css_text
        root_blocks = _extract_rule_blocks(css_text=css_text, selector="dds-tabs")
        root_props = _extract_defined_properties(block_text="\n".join(root_blocks))
        assert root_props
        for name, value in root_props.items():
            assert name.startswith("--_tabs-")
            assert value.startswith("var(--dds-")

        for required_domain in (
            "var(--dds-surface-",
            "var(--dds-control-",
            "var(--dds-state-",
            "var(--dds-text-",
            "var(--dds-space-",
        ):
            assert required_domain in css_text

    def test_styles_role_tab_and_selected_state_with_alphabetized_declarations(
        self,
    ) -> None:
        """Verify [role='tab'] and [role='tab'][aria-selected='true'] rules and CSS formatting."""
        css_text = _read_text(path=TABS_CSS_PATH)
        assert "dds-tabs [role='tab']" in css_text
        assert "dds-tabs [role='tab'][aria-selected='true']" in css_text
        assert '"' not in css_text
        assert "!important" not in css_text
        assert ".dds-icon" not in css_text
        assert ".dds-badge" not in css_text
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


class TestTabsTypeScriptCustomElement:
    """Verify Light DOM <dds-tabs> TypeScript implementation in tabs.ts."""

    def test_tabs_ts_implements_contract_and_keyboard_navigation(self) -> None:
        """Verify tabs.ts defines DDSTabsElement, AbortController, ARIA queries, and events."""
        ts_text = _read_text(path=TABS_TS_PATH)
        assert "import type { DDSCustomElement } from '../../types.js';" in ts_text
        assert (
            "export class DDSTabsElement extends HTMLElement implements DDSCustomElement"
            in ts_text
        )
        assert "AbortController" in ts_text
        assert "connectedCallback()" in ts_text
        assert "disconnectedCallback()" in ts_text
        assert '[role="tab"][data-tab-trigger]' in ts_text
        assert '[role="tabpanel"][data-tab-panel]' in ts_text
        for key in ("ArrowRight", "ArrowLeft", "Home", "End"):
            assert f"'{key}'" in ts_text
        assert "aria-selected" in ts_text
        assert "tabindex" in ts_text
        assert "panel.hidden = !isMatch;" in ts_text
        assert "this.dataset.activeTab = tabId;" in ts_text
        assert (
            "this.dispatchEvent(\n      new CustomEvent('dds:tab-change', { bubbles: true, detail: { tabId } }),\n    );"
            in ts_text
            or "this.dispatchEvent(new CustomEvent('dds:tab-change', { bubbles: true, detail: { tabId } }))"
            in ts_text
        )
        assert "if (!customElements.get('dds-tabs'))" in ts_text
        assert "customElements.define('dds-tabs', DDSTabsElement);" in ts_text
        assert "attachShadow" not in ts_text
        assert "document.querySelector" not in ts_text
        for line in ts_text.splitlines():
            assert len(line) <= 80
            assert line == line.rstrip()


class TestTabsGalleryAndDocs:
    """Verify co-located gallery.py and index.md for dds__tabs."""

    def test_gallery_config_variants_render(self) -> None:
        """Verify gallery.py exports a valid GalleryConfig whose variants all render."""
        reg = _make_registry()
        cfg = gallery.load_gallery_config(
            source_dir=TABS_DIR,
            component_name=COMPONENT_NAME,
        )
        assert isinstance(cfg, gallery.GalleryConfig)
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
            assert '<dds-tabs class="dds-tabs"' in rendered

    def test_index_md_exists_and_documents_component(self) -> None:
        """Verify index.md exists and documents dds__tabs, <dds-tabs>, and parameters."""
        doc_text = _read_text(path=TABS_INDEX_MD_PATH)
        assert "dds__tabs" in doc_text
        assert "<dds-tabs>" in doc_text
        assert "tabs" in doc_text
        assert "active_tab" in doc_text
        assert "aria_label" in doc_text
        assert "dds:tab-change" in doc_text
