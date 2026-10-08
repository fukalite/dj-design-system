"""Unit tests for the built-in dds__popout and dds__popout_option components."""

import pathlib
import re

import pytest
from django import template
from django.utils import safestring

from dj_design_system import data, gallery
from dj_design_system.components import base as components_base
from dj_design_system.components.elements import icon as icon_module
from dj_design_system.components.elements import popout as popout_package
from dj_design_system.components.elements import (
    popout_option as popout_option_package,
)
from dj_design_system.components.elements.popout import popout as popout_module
from dj_design_system.components.elements.popout_option import (
    popout_option as popout_option_module,
)
from dj_design_system.services import canvas as canvas_service
from dj_design_system.services import registry as registry_service
from dj_design_system.services import slot_node
from tests import conftest


APP_LABEL = "dj_design_system"
ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
ELEMENTS_DIR = ROOT_DIR / "dj_design_system" / "components" / "elements"

POPOUT_DIR = ELEMENTS_DIR / "popout"
POPOUT_PY_PATH = POPOUT_DIR / "popout.py"
POPOUT_HTML_PATH = POPOUT_DIR / "popout.html"
POPOUT_CSS_PATH = POPOUT_DIR / "popout.css"
POPOUT_TS_PATH = POPOUT_DIR / "popout.ts"
POPOUT_GALLERY_PATH = POPOUT_DIR / "gallery.py"
POPOUT_INDEX_MD_PATH = POPOUT_DIR / "index.md"

POPOUT_OPTION_DIR = ELEMENTS_DIR / "popout_option"
POPOUT_OPTION_PY_PATH = POPOUT_OPTION_DIR / "popout_option.py"
POPOUT_OPTION_HTML_PATH = POPOUT_OPTION_DIR / "popout_option.html"
POPOUT_OPTION_CSS_PATH = POPOUT_OPTION_DIR / "popout_option.css"
POPOUT_OPTION_GALLERY_PATH = POPOUT_OPTION_DIR / "gallery.py"
POPOUT_OPTION_INDEX_MD_PATH = POPOUT_OPTION_DIR / "index.md"


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
    pattern = re.compile(pattern=rf"{escaped}\s*\{{([^}}]*)\}}", flags=re.DOTALL)
    return pattern.findall(string=css_text)


def _extract_defined_properties(block_text: str) -> dict[str, str]:
    """Extract property definitions from a CSS block string."""
    matches = re.findall(
        pattern=r"([a-zA-Z0-9_-]+)\s*:\s*([^;]+);",
        string=block_text,
    )
    return {name: value.strip() for name, value in matches}


class TestPopoutDiscoveryAndExports:
    """Verify exports, registry discovery, and metadata for Popout and PopoutOption."""

    def test_popout_exports_and_inheritance(self) -> None:
        """Verify Popout is exported from package and module and subclasses BlockComponent."""
        assert popout_package.Popout is popout_module.Popout
        assert issubclass(popout_module.Popout, components_base.BlockComponent)
        assert popout_module.Popout.has_slots() is True

    def test_popout_option_exports_and_inheritance(self) -> None:
        """Verify PopoutOption is exported from package and module and subclasses TagComponent."""
        assert popout_option_package.PopoutOption is popout_option_module.PopoutOption
        assert issubclass(
            popout_option_module.PopoutOption,
            components_base.TagComponent,
        )

    def test_registry_discovers_dds_popout_and_dds_popout_option(self) -> None:
        """Verify ComponentRegistry registers dds__popout and dds__popout_option."""
        reg = _build_registry()

        popout_info = reg.get_by_name(name="popout", app_label=APP_LABEL)
        assert popout_info.component_class is popout_module.Popout
        assert popout_info.qualified_name == "dds__popout"
        assert popout_info.relative_path == "elements.popout"
        assert popout_info.is_internal is True
        assert (
            popout_info.template_name
            == "dj_design_system/components/elements/popout/popout.html"
        )
        assert popout_info.media.css == [
            "dj_design_system/components/elements/popout/popout.css"
        ]
        assert popout_info.media.js == [
            "dj_design_system/components/elements/popout/popout.js"
        ]
        assert popout_module.Popout.get_positional_args() == ["label"]

        option_info = reg.get_by_name(name="popout_option", app_label=APP_LABEL)
        assert option_info.component_class is popout_option_module.PopoutOption
        assert option_info.qualified_name == "dds__popout_option"
        assert option_info.relative_path == "elements.popout_option"
        assert option_info.is_internal is True
        assert (
            option_info.template_name
            == "dj_design_system/components/elements/popout_option/popout_option.html"
        )
        assert option_info.media.css == [
            "dj_design_system/components/elements/popout_option/popout_option.css"
        ]
        assert popout_option_module.PopoutOption.get_positional_args() == ["label"]


class TestPopoutParametersAndContext:
    """Verify parameter validation, slot declaration, and get_context() shaping for Popout."""

    def test_default_parameters_and_context(self) -> None:
        """Verify default Popout parameters and computed context values."""
        comp = popout_module.Popout(label="Theme")
        ctx = comp.get_context()
        assert ctx["label"] == "Theme"
        assert ctx["icon"] == ""
        assert ctx["icon_only"] is False
        assert ctx["align"] == "start"
        assert ctx["open"] is False
        assert ctx["menu_label"] == ""
        assert ctx["state"] == "closed"
        assert ctx["aria_expanded"] == "false"
        assert ctx["resolved_menu_label"] == "Theme"
        assert ctx["has_icon"] is False
        assert ctx["show_label"] is True
        assert ctx["aria_label"] is None
        assert ctx["slots"] == {"trigger": ""}
        assert ctx["content"] == ""

    def test_open_end_aligned_with_menu_label_and_icon_context(self) -> None:
        """Verify open=True, align='end', menu_label, and icon context shaping."""
        comp = popout_module.Popout(
            content=safestring.SafeString("<button>Option</button>"),
            label="Viewport",
            icon="monitor",
            align="end",
            open=True,
            menu_label="Choose viewport preset",
        )
        ctx = comp.get_context()
        assert ctx["state"] == "open"
        assert ctx["aria_expanded"] == "true"
        assert ctx["align"] == "end"
        assert ctx["resolved_menu_label"] == "Choose viewport preset"
        assert ctx["has_icon"] is True
        assert ctx["show_label"] is True
        assert ctx["aria_label"] is None
        assert ctx["content"] == "<button>Option</button>"

    def test_icon_only_context_shaping(self) -> None:
        """Verify icon_only=True hides visible label and sets aria_label."""
        comp = popout_module.Popout(
            label="More actions",
            icon="menu",
            icon_only=True,
        )
        ctx = comp.get_context()
        assert ctx["has_icon"] is True
        assert ctx["show_label"] is False
        assert ctx["aria_label"] == "More actions"

    def test_trigger_slot_declaration_and_invalid_choices(self) -> None:
        """Verify trigger slot metadata and choice validation for icon and align."""
        slots_spec = popout_module.Popout.get_slots()
        assert "trigger" in slots_spec
        assert slots_spec["trigger"].required is False

        params = popout_module.Popout.get_params()
        assert params["icon"].choices == ["", *icon_module.ICON_NAMES]
        assert params["align"].choices == ["start", "end"]

        with pytest.raises(expected_exception=ValueError, match="Expected one of"):
            popout_module.Popout(label="Theme", align="center")
        with pytest.raises(expected_exception=ValueError, match="Expected one of"):
            popout_module.Popout(label="Theme", icon="invalid-icon")


class TestPopoutOptionParametersAndContext:
    """Verify parameter validation and get_context() shaping for PopoutOption."""

    def test_default_parameters_and_value_fallback(self) -> None:
        """Verify PopoutOption defaults and resolved_value fallback to label."""
        comp = popout_option_module.PopoutOption(label="Light")
        ctx = comp.get_context()
        assert ctx["label"] == "Light"
        assert ctx["value"] == ""
        assert ctx["icon"] == ""
        assert ctx["selected"] is False
        assert ctx["disabled"] is False
        assert ctx["href"] == ""
        assert ctx["is_link"] is False
        assert ctx["resolved_value"] == "Light"
        assert ctx["aria_checked"] == "false"
        assert ctx["has_icon"] is False

    def test_selected_custom_value_and_icon_context(self) -> None:
        """Verify explicit value, selected=True, and icon context flags."""
        comp = popout_option_module.PopoutOption(
            label="Dark Theme",
            value="dark",
            icon="moon",
            selected=True,
        )
        ctx = comp.get_context()
        assert ctx["resolved_value"] == "dark"
        assert ctx["aria_checked"] == "true"
        assert ctx["has_icon"] is True
        assert ctx["is_link"] is False

    def test_href_and_disabled_interaction(self) -> None:
        """Verify is_link is True only when href is provided and disabled is False."""
        link_ctx = popout_option_module.PopoutOption(
            label="Docs",
            href="/docs/",
        ).get_context()
        assert link_ctx["is_link"] is True

        disabled_link_ctx = popout_option_module.PopoutOption(
            label="Docs",
            href="/docs/",
            disabled=True,
        ).get_context()
        assert disabled_link_ctx["is_link"] is False

    def test_invalid_icon_raises_value_error(self) -> None:
        """Verify invalid icon name on PopoutOption raises ValueError."""
        with pytest.raises(expected_exception=ValueError, match="Expected one of"):
            popout_option_module.PopoutOption(label="Option", icon="nonexistent")


class TestPopoutAndOptionRendering:
    """Verify HTML rendering for Popout and PopoutOption across states and slots."""

    def test_renders_default_closed_popout_with_trigger_and_hidden_menu(self) -> None:
        """Verify closed Popout renders default trigger button, chevron, and hidden menu."""
        _build_registry()
        menu_html = popout_option_module.PopoutOption(
            label="Light",
            value="light",
            icon="sun",
            selected=True,
        ).render()
        html = popout_module.Popout(
            content=safestring.SafeString(menu_html),
            label="Theme",
            icon="sun",
        ).render()
        assert (
            '<dds-popout class="dds-popout" data-align="start" data-state="closed">'
            in html
        )
        assert (
            '<button type="button" data-popout-trigger aria-haspopup="true" '
            'aria-expanded="false">' in html
        )
        assert 'data-icon="sun"' in html
        assert "<span>Theme</span>" in html
        assert 'data-icon="chevron-down"' in html
        assert (
            '<div data-popout-menu data-surface="popout" role="menu" '
            'aria-label="Theme" hidden>' in html
        )
        assert 'role="menuitemradio"' in html

    def test_renders_open_end_aligned_icon_only_popout(self) -> None:
        """Verify open=True omits hidden and icon_only=True sets aria-label and omits chevron."""
        _build_registry()
        html = popout_module.Popout(
            content=safestring.SafeString(""),
            label="More options",
            icon="menu",
            icon_only=True,
            align="end",
            open=True,
            menu_label="Actions menu",
        ).render()
        assert (
            '<dds-popout class="dds-popout" data-align="end" data-state="open">' in html
        )
        assert (
            '<button type="button" data-popout-trigger aria-haspopup="true" '
            'aria-expanded="true" aria-label="More options">' in html
        )
        assert 'data-icon="menu"' in html
        assert "<span>More options</span>" not in html
        assert 'data-icon="chevron-down"' not in html
        assert (
            '<div data-popout-menu data-surface="popout" role="menu" '
            'aria-label="Actions menu">' in html
        )
        assert " hidden>" not in html

    def test_renders_custom_trigger_slot(self) -> None:
        """Verify Popout renders custom trigger slot markup when provided."""
        html = _render_template(
            source=(
                '{% dds__popout "Theme" %}'
                '{% slot "trigger" %}'
                '<button type="button" data-popout-trigger class="custom-trigger">'
                "Custom"
                "</button>"
                "{% endslot %}"
                "{% enddds__popout %}"
            )
        )
        assert 'class="custom-trigger"' in html
        assert 'data-icon="chevron-down"' not in html

    def test_renders_popout_option_button_and_link_modes(self) -> None:
        """Verify {% dds__popout_option %} renders button or link appropriately."""
        btn_html = _render_template(
            source=(
                '{% dds__popout_option "Dark" value="dark" icon="moon" '
                "selected=True disabled=True %}"
            )
        )
        assert (
            '<button type="button" class="dds-popout-option" role="menuitemradio" '
            'data-popout-option data-value="dark" aria-checked="true" disabled>'
            in btn_html
        )
        assert 'data-icon="moon"' in btn_html
        assert "<span>Dark</span>" in btn_html

        link_html = _render_template(
            source='{% dds__popout_option "Docs" href="/docs/" icon="external-link" %}'
        )
        assert (
            '<a class="dds-popout-option" role="menuitem" data-popout-option '
            'data-value="Docs" href="/docs/">' in link_html
        )
        assert 'data-icon="external-link"' in link_html
        assert "<span>Docs</span>" in link_html


class TestPopoutStylesheetsAndTypeScriptContract:
    """Verify CSS @layer blocks, Tier 3 tokens, TypeScript custom element, and gallery configs."""

    def test_popout_css_layer_and_tier_3_tokens(self) -> None:
        """Verify popout.css uses @layer blocks on dds-popout and maps Tier 3 from Tier 2."""
        css_text = POPOUT_CSS_PATH.read_text(encoding="utf-8")
        assert "@layer blocks {" in css_text
        assert "--_dds-" not in css_text

        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector="dds-popout",
        )
        assert root_blocks
        root_block_text = "\n".join(root_blocks)
        props = _extract_defined_properties(block_text=root_block_text)
        assert props.get("display") == "inline-block"
        assert props.get("margin") == "0"
        assert props.get("position") == "relative"

        token_defs = re.findall(
            pattern=r"(--_popout-[a-z0-9-]+)\s*:\s*([^;]+);",
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

    def test_popout_option_css_layer_and_tier_3_tokens(self) -> None:
        """Verify popout_option.css uses @layer blocks on .dds-popout-option and Tier 3 tokens."""
        css_text = POPOUT_OPTION_CSS_PATH.read_text(encoding="utf-8")
        assert "@layer blocks {" in css_text
        assert "--_dds-" not in css_text

        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-popout-option",
        )
        assert root_blocks
        root_block_text = "\n".join(root_blocks)
        props = _extract_defined_properties(block_text=root_block_text)
        assert props.get("margin") == "0"

        token_defs = re.findall(
            pattern=r"(--_popout-option-[a-z0-9-]+)\s*:\s*([^;]+);",
            string=css_text,
        )
        assert token_defs
        for _name, value in token_defs:
            assert value.strip().startswith("var(--dds-")

    @pytest.mark.parametrize(
        "css_path",
        [POPOUT_CSS_PATH, POPOUT_OPTION_CSS_PATH],
    )
    def test_css_formatting_alphabetical_order_and_zero_bem(
        self,
        css_path: pathlib.Path,
    ) -> None:
        """Verify zero BEM selectors, single quotes, and alphabetised declarations."""
        css_text = css_path.read_text(encoding="utf-8")
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

    @pytest.mark.parametrize(
        ("py_path", "html_path"),
        [
            (POPOUT_PY_PATH, POPOUT_HTML_PATH),
            (POPOUT_OPTION_PY_PATH, POPOUT_OPTION_HTML_PATH),
        ],
    )
    def test_python_and_template_hygiene(
        self,
        py_path: pathlib.Path,
        html_path: pathlib.Path,
    ) -> None:
        """Verify Python modules contain no HTML/mark_safe and templates contain no filters/BEM."""
        py_source = py_path.read_text(encoding="utf-8")
        assert "mark_safe" not in py_source
        assert "format_html" not in py_source

        html_source = html_path.read_text(encoding="utf-8")
        assert "{% load design_components %}" in html_source
        assert "|" not in html_source
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=html_source,
        )
        assert not bem_matches

    def test_typescript_custom_element_contract(self) -> None:
        """Verify popout.ts defines DDSPopoutElement with AbortController and dds:popout-select."""
        assert POPOUT_TS_PATH.is_file()
        ts_source = POPOUT_TS_PATH.read_text(encoding="utf-8")
        assert "import type { DDSCustomElement } from '../../types.js';" in ts_source
        assert (
            "export class DDSPopoutElement extends HTMLElement implements DDSCustomElement"
            in ts_source
        )
        assert "new AbortController()" in ts_source
        assert "this.abortController?.abort()" in ts_source
        assert "this.dataset.state = isOpen ? 'open' : 'closed'" in ts_source
        assert "trigger.setAttribute('aria-expanded', String(isOpen))" in ts_source
        assert "menu.hidden = !isOpen" in ts_source
        assert "event.key === 'Escape'" in ts_source
        assert "!this.contains(event.target as Node)" in ts_source
        assert "'dds:popout-select'" in ts_source
        assert "customElements.get('dds-popout')" in ts_source
        assert "customElements.define('dds-popout', DDSPopoutElement)" in ts_source
        assert "\t" not in ts_source
        for line in ts_source.splitlines():
            assert len(line) <= 80
            assert line == line.rstrip()

    def test_gallery_configs_and_docs_render_cleanly(self) -> None:
        """Verify gallery.py and index.md exist and render for both components."""
        assert POPOUT_GALLERY_PATH.is_file()
        assert POPOUT_INDEX_MD_PATH.is_file()
        assert POPOUT_OPTION_GALLERY_PATH.is_file()
        assert POPOUT_OPTION_INDEX_MD_PATH.is_file()

        reg = _build_registry()

        popout_cfg = gallery.load_gallery_config(
            source_dir=POPOUT_DIR,
            component_name="popout",
        )
        assert popout_cfg.variants
        for variant in popout_cfg.variants:
            spec = data.CanvasSpec(
                component_name="dds__popout",
                variant=variant.name,
            )
            rendered = canvas_service.render_component(
                spec=spec,
                registry=reg,
                raise_errors=True,
            )
            assert '<dds-popout class="dds-popout"' in rendered

        option_cfg = gallery.load_gallery_config(
            source_dir=POPOUT_OPTION_DIR,
            component_name="popout_option",
        )
        assert option_cfg.variants
        for variant in option_cfg.variants:
            spec = data.CanvasSpec(
                component_name="dds__popout_option",
                variant=variant.name,
            )
            rendered = canvas_service.render_component(
                spec=spec,
                registry=reg,
                raise_errors=True,
            )
            assert 'class="dds-popout-option"' in rendered
