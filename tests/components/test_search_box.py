"""Unit tests for the built-in dds__search_box domain component."""

import dataclasses
import json
import pathlib
import re

from django import template

from dj_design_system import data, gallery
from dj_design_system.components import base as components_base
from dj_design_system.components.domain import search_box as search_box_package
from dj_design_system.components.domain.search_box import (
    search_box as search_box_module,
)
from dj_design_system.services import canvas as canvas_service
from dj_design_system.services import registry as registry_service
from dj_design_system.services import slot_node
from tests import conftest


APP_LABEL = "dj_design_system"
ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
DOMAIN_DIR = ROOT_DIR / "dj_design_system" / "components" / "domain"

SEARCH_BOX_DIR = DOMAIN_DIR / "search_box"
SEARCH_BOX_PY_PATH = SEARCH_BOX_DIR / "search_box.py"
SEARCH_BOX_HTML_PATH = SEARCH_BOX_DIR / "search_box.html"
SEARCH_BOX_CSS_PATH = SEARCH_BOX_DIR / "search_box.css"
SEARCH_BOX_TS_PATH = SEARCH_BOX_DIR / "search_box.ts"
SEARCH_BOX_GALLERY_PATH = SEARCH_BOX_DIR / "gallery.py"
SEARCH_BOX_INDEX_MD_PATH = SEARCH_BOX_DIR / "index.md"


@dataclasses.dataclass(frozen=True)
class _SampleIndexEntry:
    """Sample object entry for testing attribute-based search index normalization."""

    name: str
    href: str
    type: str = "component"
    breadcrumb: str = "Elements"
    content: str = "Object-based entry content"


def _build_registry() -> registry_service.ComponentRegistry:
    """Create a ComponentRegistry populated with built-in dds components."""
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
    reg = _build_registry()
    engine = template.engines["django"].engine
    lib = template.Library()
    reg.register_templatetags(library=lib)
    lib.tag(name="slot", compile_function=slot_node.do_slot)
    previous = engine.template_libraries.get("design_components")
    engine.template_libraries["design_components"] = lib
    try:
        compiled = template.Template(
            template_string="{% load design_components %}" + source
        )
        return compiled.render(context=template.Context(dict_=context_data or {}))
    finally:
        if previous is None:
            engine.template_libraries.pop("design_components", None)
        else:
            engine.template_libraries["design_components"] = previous


def _extract_rule_blocks(css_text: str, selector: str) -> list[str]:
    """Extract all CSS declaration blocks for a given selector."""
    escaped = re.escape(pattern=selector)
    pattern = re.compile(
        pattern=rf"{escaped}(?:\s*,\s*\.[a-z0-9-]+)?\s*\{{([^}}]*)\}}",
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


class TestSearchBoxDiscoveryAndExports:
    """Verify exports, registry discovery, and metadata for SearchBox."""

    def test_search_box_exports_and_inheritance(self) -> None:
        """Verify SearchBox is exported from package and module and subclasses TagComponent."""
        assert search_box_package.SearchBox is search_box_module.SearchBox
        assert issubclass(
            search_box_module.SearchBox,
            components_base.TagComponent,
        )

    def test_registry_discovers_dds_search_box(self) -> None:
        """Verify ComponentRegistry registers dds__search_box with CSS and JS media."""
        reg = _build_registry()
        info = reg.get_by_name(name="search_box", app_label=APP_LABEL)
        assert info.component_class is search_box_module.SearchBox
        assert info.qualified_name == "dds__search_box"
        assert info.relative_path == "domain.search_box"
        assert info.is_internal is True
        assert (
            info.template_name
            == "dj_design_system/components/domain/search_box/search_box.html"
        )
        assert info.media.css == [
            "dj_design_system/components/domain/search_box/search_box.css"
        ]
        assert info.media.js == [
            "dj_design_system/components/domain/search_box/search_box.js"
        ]
        assert search_box_module.SearchBox.get_positional_args() == ["placeholder"]


class TestSearchBoxParametersAndContext:
    """Verify parameter defaults and get_context() normalization for SearchBox."""

    def test_default_parameters_and_context(self) -> None:
        """Verify default SearchBox parameters and computed context values."""
        comp = search_box_module.SearchBox()
        ctx = comp.get_context()
        assert ctx["placeholder"] == "Search components and docs..."
        assert ctx["aria_label"] == "Search components and documentation"
        assert ctx["index_id"] == "gallery-search-index"
        assert ctx["input_id"] == "gallery-search-input"
        assert ctx["results_id"] == "gallery-search-results"
        assert ctx["shortcut_hint"] == "/"
        assert ctx["has_shortcut"] is True
        assert ctx["search_index"] == []
        assert ctx["normalized_index"] == []
        assert str(ctx["search_index_json"]) == "[]"

    def test_normalizes_dict_and_object_entries_and_escapes_script_closing_tags(
        self,
    ) -> None:
        """Verify get_context() normalizes index entries and escapes </ sequences in JSON."""
        raw_index = [
            {
                "label": "Button",
                "url": "/c/button/",
                "type": "component",
                "breadcrumb": "Elements / Button",
                "content": "Contains </script> tag in docs",
            },
            _SampleIndexEntry(
                name="Icon",
                href="/c/icon/",
            ),
        ]
        comp = search_box_module.SearchBox(
            placeholder="Quick search...",
            aria_label="Quick search input",
            search_index=raw_index,
            index_id="custom-idx",
            input_id="custom-in",
            results_id="custom-res",
            shortcut_hint="⌘K",
        )
        ctx = comp.get_context()
        assert ctx["placeholder"] == "Quick search..."
        assert ctx["aria_label"] == "Quick search input"
        assert ctx["index_id"] == "custom-idx"
        assert ctx["input_id"] == "custom-in"
        assert ctx["results_id"] == "custom-res"
        assert ctx["shortcut_hint"] == "⌘K"
        assert ctx["has_shortcut"] is True
        assert len(ctx["normalized_index"]) == 2
        assert ctx["normalized_index"][0] == {
            "label": "Button",
            "url": "/c/button/",
            "type": "component",
            "breadcrumb": "Elements / Button",
            "content": "Contains </script> tag in docs",
        }
        assert ctx["normalized_index"][1] == {
            "label": "Icon",
            "url": "/c/icon/",
            "type": "component",
            "breadcrumb": "Elements",
            "content": "Object-based entry content",
        }

        raw_json = str(ctx["search_index_json"])
        assert "</script>" not in raw_json
        assert "<\\/script>" in raw_json
        parsed = json.loads(s=raw_json)
        assert parsed == ctx["normalized_index"]

    def test_empty_shortcut_hint_disables_has_shortcut(self) -> None:
        """Verify passing shortcut_hint='' sets has_shortcut=False."""
        comp = search_box_module.SearchBox(shortcut_hint="")
        ctx = comp.get_context()
        assert ctx["shortcut_hint"] == ""
        assert ctx["has_shortcut"] is False


class TestSearchBoxRendering:
    """Verify HTML rendering for SearchBox across parameters and template tags."""

    def test_renders_default_search_box_markup(self) -> None:
        """Verify default SearchBox renders combobox input, shortcut badge, listbox, and JSON script."""
        _build_registry()
        html = search_box_module.SearchBox(
            search_index=[
                {
                    "label": "Tabs",
                    "url": "/c/tabs/",
                    "type": "component",
                    "breadcrumb": "Elements / Tabs",
                    "content": "Accessible tabs",
                }
            ]
        ).render()
        assert (
            '<dds-search-box class="dds-search-box" data-state="closed" '
            'data-index-id="gallery-search-index">' in html
        )
        assert "<div data-search-field>" in html
        assert 'data-icon="search"' in html
        assert (
            '<input type="search" id="gallery-search-input" data-search-input '
            'placeholder="Search components and docs..." autocomplete="off" '
            'role="combobox" aria-autocomplete="list" aria-expanded="false" '
            'aria-controls="gallery-search-results" '
            'aria-label="Search components and documentation">' in html
        )
        assert '<kbd data-search-shortcut aria-hidden="true">/</kbd>' in html
        assert (
            '<div id="gallery-search-results" data-search-results '
            'data-surface="popout" role="listbox" aria-label="Search results" hidden>'
            "</div>" in html
        )
        assert (
            '<script id="gallery-search-index" type="application/json" '
            "data-search-index>" in html
        )
        assert '"label": "Tabs"' in html

    def test_renders_via_template_tag_without_shortcut(self) -> None:
        """Verify {% dds__search_box %} positional placeholder and hidden shortcut badge."""
        html = _render_template(
            source='{% dds__search_box "Filter docs..." shortcut_hint="" %}'
        )
        assert 'placeholder="Filter docs..."' in html
        assert "data-search-shortcut" not in html


class TestSearchBoxStylesheetAndHygiene:
    """Verify CSS @layer blocks, Tier 3 tokens, code hygiene, and gallery configs."""

    def test_search_box_css_layer_and_tier_3_tokens(self) -> None:
        """Verify search_box.css uses @layer blocks on dds-search-box and maps Tier 3 from Tier 2."""
        css_text = SEARCH_BOX_CSS_PATH.read_text(encoding="utf-8")
        assert "@layer blocks {" in css_text
        assert "--_dds-" not in css_text

        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector="dds-search-box",
        )
        assert root_blocks
        root_block_text = "\n".join(root_blocks)
        props = _extract_defined_properties(block_text=root_block_text)
        assert props.get("display") == "block"
        assert props.get("margin") == "0"
        assert props.get("position") == "relative"

        token_defs = re.findall(
            pattern=r"(--_search-box-[a-z0-9-]+)\s*:\s*([^;]+);",
            string=css_text,
        )
        assert token_defs
        for _name, value in token_defs:
            assert value.strip().startswith("var(--dds-")

        for required_domain in (
            "var(--dds-surface-popout-",
            "var(--dds-control-",
            "var(--dds-state-",
            "var(--dds-text-",
            "var(--dds-space-",
        ):
            assert required_domain in root_block_text

    def test_css_formatting_alphabetical_order_and_zero_bem(self) -> None:
        """Verify zero BEM selectors, single quotes, and alphabetised declarations."""
        css_text = SEARCH_BOX_CSS_PATH.read_text(encoding="utf-8")
        assert "!important" not in css_text
        assert '"' not in css_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=css_text,
        )
        assert not bem_matches

        for block in re.findall(pattern=r"\{([^{}]+)\}", string=css_text):
            prop_names = re.findall(
                pattern=r"^\s*([a-z0-9_-]+)\s*:",
                string=block,
                flags=re.MULTILINE,
            )
            assert prop_names == sorted(prop_names)

    def test_python_and_template_hygiene(self) -> None:
        """Verify search_box.py has no private methods/mark_safe and search_box.html has no filters."""
        py_source = SEARCH_BOX_PY_PATH.read_text(encoding="utf-8")
        assert "mark_safe" not in py_source
        assert "format_html" not in py_source
        private_defs = re.findall(
            pattern=r"^\s+def _(?![_a-z]+__)[a-z0-9_]+\(",
            string=py_source,
            flags=re.MULTILINE,
        )
        assert not private_defs

        html_source = SEARCH_BOX_HTML_PATH.read_text(encoding="utf-8")
        assert "{% load design_components %}" in html_source
        assert "|" not in html_source
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=html_source,
        )
        assert not bem_matches

    def test_gallery_config_and_docs_render_cleanly(self) -> None:
        """Verify gallery.py and index.md exist and all variants render via canvas_service."""
        assert SEARCH_BOX_GALLERY_PATH.is_file()
        assert SEARCH_BOX_INDEX_MD_PATH.is_file()

        reg = _build_registry()
        cfg = gallery.load_gallery_config(
            source_dir=SEARCH_BOX_DIR,
            component_name="search_box",
        )
        assert cfg.variants
        for variant in cfg.variants:
            spec = data.CanvasSpec(
                component_name="dds__search_box",
                variant=variant.name,
            )
            rendered = canvas_service.render_component(
                spec=spec,
                registry=reg,
                raise_errors=True,
            )
            assert '<dds-search-box class="dds-search-box"' in rendered


class TestSearchBoxTypeScriptCustomElement:
    """Verify Light DOM <dds-search-box> TypeScript contract in search_box.ts."""

    def test_search_box_ts_implements_custom_element_and_lifecycle_contract(
        self,
    ) -> None:
        """Verify search_box.ts defines DDSSearchBoxElement with AbortController and debounce cleanup."""
        assert SEARCH_BOX_TS_PATH.is_file()
        ts_text = SEARCH_BOX_TS_PATH.read_text(encoding="utf-8")
        assert "import type { DDSCustomElement } from '../../types.js';" in ts_text
        assert (
            "export class DDSSearchBoxElement" in ts_text
            and "extends HTMLElement" in ts_text
            and "implements DDSCustomElement" in ts_text
        )
        assert "private abortController: AbortController | null = null;" in ts_text
        assert "private debounceTimer: number | null = null;" in ts_text
        assert "connectedCallback(): void" in ts_text
        assert "disconnectedCallback(): void" in ts_text
        assert "this.abortController?.abort();" in ts_text
        assert "this.abortController = new AbortController();" in ts_text
        assert "this.abortController = null;" in ts_text
        assert "this.clearDebounceTimer();" in ts_text
        assert "window.clearTimeout(this.debounceTimer);" in ts_text
        assert "this.querySelector<HTMLInputElement>('[data-search-input]')" in ts_text
        assert "this.querySelector<HTMLElement>('[data-search-results]')" in ts_text
        assert "this.querySelector<HTMLScriptElement>('[data-search-index]')" in ts_text
        assert "if (!customElements.get('dds-search-box'))" in ts_text
        assert (
            "customElements.define('dds-search-box', DDSSearchBoxElement);" in ts_text
        )

    def test_search_box_ts_search_filtering_dom_creation_and_url_sanitization(
        self,
    ) -> None:
        """Verify index parsing, 50-result limit, safe DOM creation, and URL sanitization."""
        ts_text = SEARCH_BOX_TS_PATH.read_text(encoding="utf-8")
        assert "const MAX_RESULTS = 50;" in ts_text
        assert "JSON.parse(rawJson)" in ts_text
        assert "matches.slice(0, MAX_RESULTS)" in ts_text
        assert "new URL(rawUrl, window.location.origin)" in ts_text
        assert "parsed.protocol === 'http:' || parsed.protocol === 'https:'" in ts_text
        assert "return '#';" in ts_text
        assert "document.createElement('a')" in ts_text
        assert "document.createElement('mark')" in ts_text
        assert "document.createElement('p')" in ts_text
        assert "optionEl.setAttribute('role', 'option');" in ts_text
        assert "optionEl.setAttribute('data-search-option', '');" in ts_text
        assert "optionEl.setAttribute('data-node-type', entry.type);" in ts_text
        assert "crumbEl.setAttribute('data-search-breadcrumb', '');" in ts_text
        assert "emptyEl.setAttribute('data-search-empty', '');" in ts_text
        assert "emptyEl.textContent = 'No results found.';" in ts_text
        assert "this.dataset.state = isOpen ? 'open' : 'closed';" in ts_text
        assert (
            "inputEl.setAttribute('aria-expanded', isOpen ? 'true' : 'false');"
            in ts_text
        )
        assert "resultsEl.hidden = !isOpen;" in ts_text

    def test_search_box_ts_keyboard_navigation_shortcut_outside_click_and_events(
        self,
    ) -> None:
        """Verify ArrowDown/Up, Enter, Escape, global '/' shortcut, outside click, and dds:search-select."""
        ts_text = SEARCH_BOX_TS_PATH.read_text(encoding="utf-8")
        for key in ("ArrowDown", "ArrowUp", "Enter", "Escape", "/"):
            assert f"event.key === '{key}'" in ts_text
        assert (
            "optionEl.setAttribute('aria-selected', isActive ? 'true' : 'false');"
            in ts_text
        )
        assert "optionEl.setAttribute('data-active', 'true');" in ts_text
        assert "optionEl.removeAttribute('data-active');" in ts_text
        assert "activeOption.click();" in ts_text
        assert "new CustomEvent('dds:search-select'" in ts_text
        assert "detail: { url, label }" in ts_text
        assert "!this.contains(event.target as Node)" in ts_text
        assert "target.isContentEditable" in ts_text

    def test_search_box_ts_enforces_light_dom_encapsulation_and_styleguide(
        self,
    ) -> None:
        """Verify search_box.ts uses Light DOM only, scoped queries, single quotes, and <=80 cols."""
        ts_text = SEARCH_BOX_TS_PATH.read_text(encoding="utf-8")
        assert "attachShadow" not in ts_text
        assert "innerHTML" not in ts_text
        assert "document.getElementById" not in ts_text
        assert "document.querySelector" not in ts_text
        assert '"' not in ts_text
        assert "\t" not in ts_text
        for line in ts_text.splitlines():
            assert len(line) <= 80
            assert line == line.rstrip()

