"""Unit tests for the built-in dds__button component."""

import pathlib
import re

import pytest
from django import template

from dj_design_system import gallery
from dj_design_system.components import TagComponent
from dj_design_system.components.elements import button as button_package
from dj_design_system.components.elements.button import Button
from dj_design_system.components.elements.button import button as button_module
from dj_design_system.components.elements.icon import ICON_NAMES
from dj_design_system.services import registry as registry_service
from dj_design_system.templatetags import design_components
from tests import conftest


BUTTON_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "components"
    / "elements"
    / "button"
)
BUTTON_CSS_PATH = BUTTON_DIR / "button.css"
BUTTON_HTML_PATH = BUTTON_DIR / "button.html"
BUTTON_PY_PATH = BUTTON_DIR / "button.py"
BUTTON_INDEX_MD_PATH = BUTTON_DIR / "index.md"

EXPECTED_VARIANTS: tuple[str, ...] = ("default", "primary", "ghost", "danger")
EXPECTED_SIZES: tuple[str, ...] = ("sm", "md", "lg")
EXPECTED_BUTTON_TYPES: tuple[str, ...] = ("button", "submit", "reset")


def _build_builtin_registry() -> registry_service.ComponentRegistry:
    """Create a ComponentRegistry populated with built-in dds components."""
    reg = registry_service.ComponentRegistry()
    conftest.discover_app_into_registry(
        reg=reg,
        app_name="dj_design_system",
        app_label="dj_design_system",
    )
    reg.register_templatetags(library=design_components.register)
    return reg


def _render_template_tag(
    source: str,
    context_data: dict[str, object] | None = None,
) -> str:
    """Render a template snippet with built-in dds component tags registered."""
    reg = _build_builtin_registry()
    library = template.Library()
    reg.register_templatetags(library=library)
    engine = template.Engine(
        loaders=[
            "dj_design_system.loaders.ComponentsTemplateLoader",
            "django.template.loaders.app_directories.Loader",
        ],
        libraries={"design_components": "dj_design_system.templatetags.design_components"},
    )
    engine.template_builtins.append(library)
    return engine.from_string(template_code=source).render(
        context=template.Context(dict_=context_data or {})
    )


def _extract_rule_blocks(css_text: str, selector: str) -> list[str]:
    """Extract all CSS declaration blocks for a given selector."""
    escaped = re.escape(pattern=selector)
    pattern = re.compile(pattern=rf"{escaped}\s*\{{([^}}]*)\}}", flags=re.DOTALL)
    return pattern.findall(string=css_text)


def _extract_defined_properties(block_text: str) -> dict[str, str]:
    """Extract custom property and declaration definitions from a CSS block."""
    matches = re.findall(
        pattern=r"([a-zA-Z0-9_-]+)\s*:\s*([^;]+);",
        string=block_text,
    )
    return {name: value.strip() for name, value in matches}


class TestButtonExportsAndDiscovery:
    """Verify exports, registry discovery, and metadata for dds__button."""

    def test_exports_from_module_and_package(self) -> None:
        """Verify Button is exported from button.py and __init__.py."""
        assert button_package.Button is Button
        assert button_module.Button is Button
        assert issubclass(Button, TagComponent)

    def test_registry_discovers_dds_button(self) -> None:
        """Verify ComponentRegistry registers Button as dds__button."""
        reg = _build_builtin_registry()
        info = reg.get_by_name(name="button", app_label="dj_design_system")
        assert info.component_class is Button
        assert info.app_label == "dj_design_system"
        assert info.relative_path == "elements.button"
        assert info.qualified_name == "dds__button"
        assert info.is_internal is True
        assert (
            info.template_name
            == "dj_design_system/components/elements/button/button.html"
        )
        assert info.media.css == [
            "dj_design_system/components/elements/button/button.css"
        ]
        assert Button.get_positional_args() == ["label"]


class TestButtonParametersAndValidation:
    """Verify parameter validation rules and get_context() shaping."""

    def test_default_parameters_and_context(self) -> None:
        """Verify default parameter values and computed context keys."""
        comp = Button(label="Save")
        ctx = comp.get_context()
        assert ctx["label"] == "Save"
        assert ctx["variant"] == "default"
        assert ctx["size"] == "md"
        assert ctx["icon"] == ""
        assert ctx["icon_trailing"] == ""
        assert ctx["icon_only"] is False
        assert ctx["href"] == ""
        assert ctx["target"] == ""
        assert ctx["button_type"] == "button"
        assert ctx["disabled"] is False
        assert ctx["pressed"] is None
        assert ctx["action"] == ""
        assert ctx["is_link"] is False
        assert ctx["resolved_href"] is None
        assert ctx["resolved_target"] is None
        assert ctx["resolved_rel"] is None
        assert ctx["aria_pressed"] is None
        assert ctx["aria_label"] is None
        assert ctx["has_icon"] is False
        assert ctx["has_trailing_icon"] is False
        assert ctx["show_label"] is True
        assert ctx["icon_size"] == "md"
        assert ctx["has_action"] is False

    def test_validate_params_icon_only_requires_label(self) -> None:
        """Verify icon_only=True without label raises ValueError."""
        with pytest.raises(
            expected_exception=ValueError,
            match="icon_only buttons require a 'label' for accessibility.",
        ):
            Button(icon="search", icon_only=True)

    def test_validate_params_icon_only_requires_icon(self) -> None:
        """Verify icon_only=True without icon raises ValueError."""
        with pytest.raises(
            expected_exception=ValueError,
            match="icon_only buttons require an 'icon' name.",
        ):
            Button(label="Search", icon_only=True)

    def test_validate_params_requires_label_or_icon(self) -> None:
        """Verify omitting both label and icon raises ValueError."""
        with pytest.raises(
            expected_exception=ValueError,
            match="Button requires at least a 'label' or an 'icon'.",
        ):
            Button()

    def test_non_icon_only_with_icon_and_empty_label_is_valid(self) -> None:
        """Verify non-icon_only button with an icon and empty label passes validation."""
        comp = Button(icon="check")
        ctx = comp.get_context()
        assert ctx["has_icon"] is True
        assert ctx["show_label"] is False
        assert ctx["aria_label"] is None

    def test_link_and_disabled_interaction_in_context(self) -> None:
        """Verify href resolves to link only when disabled is False."""
        active_link = Button(
            label="Docs",
            href="https://example.com",
            target="_blank",
        ).get_context()
        assert active_link["is_link"] is True
        assert active_link["resolved_href"] == "https://example.com"
        assert active_link["resolved_target"] == "_blank"
        assert active_link["resolved_rel"] == "noopener noreferrer"

        same_tab_link = Button(
            label="Internal",
            href="/docs/",
            target="_self",
        ).get_context()
        assert same_tab_link["is_link"] is True
        assert same_tab_link["resolved_target"] == "_self"
        assert same_tab_link["resolved_rel"] is None

        disabled_link = Button(
            label="Docs",
            href="https://example.com",
            target="_blank",
            disabled=True,
        ).get_context()
        assert disabled_link["is_link"] is False
        assert disabled_link["resolved_href"] is None
        assert disabled_link["resolved_target"] is None
        assert disabled_link["resolved_rel"] is None

    def test_pressed_icon_only_icon_size_and_action_context(self) -> None:
        """Verify pressed, icon_only, icon_size, and has_action context resolution."""
        pressed_true = Button(label="Pin", pressed=True).get_context()
        assert pressed_true["aria_pressed"] == "true"

        pressed_false = Button(label="Pin", pressed=False).get_context()
        assert pressed_false["aria_pressed"] == "false"

        icon_only_sm = Button(
            label="Close",
            icon="close",
            icon_trailing="chevron-right",
            icon_only=True,
            size="sm",
            action="close-panel",
        ).get_context()
        assert icon_only_sm["aria_label"] == "Close"
        assert icon_only_sm["show_label"] is False
        assert icon_only_sm["has_icon"] is True
        assert icon_only_sm["has_trailing_icon"] is False
        assert icon_only_sm["icon_size"] == "sm"
        assert icon_only_sm["has_action"] is True

        large_btn = Button(label="Expand", size="lg", icon="eye").get_context()
        assert large_btn["icon_size"] == "md"

    def test_invalid_parameter_choices_raise_value_error(self) -> None:
        """Verify invalid variant, size, icon, or button_type raises ValueError."""
        with pytest.raises(expected_exception=ValueError):
            Button(label="Save", variant="outline")
        with pytest.raises(expected_exception=ValueError):
            Button(label="Save", size="xl")
        with pytest.raises(expected_exception=ValueError):
            Button(label="Save", icon="unknown-icon")
        with pytest.raises(expected_exception=ValueError):
            Button(label="Save", icon_trailing="unknown-icon")
        with pytest.raises(expected_exception=ValueError):
            Button(label="Save", button_type="menu")

    def test_no_html_or_mark_safe_in_python_module(self) -> None:
        """Verify button.py contains zero HTML strings or mark_safe calls."""
        source = BUTTON_PY_PATH.read_text(encoding="utf-8")
        assert "mark_safe" not in source
        assert "format_html" not in source
        assert "<button" not in source
        assert "<svg" not in source


class TestButtonRendering:
    """Verify HTML rendering across button/link modes, icons, variants, and sizes."""

    @pytest.mark.parametrize("variant", EXPECTED_VARIANTS)
    @pytest.mark.parametrize("size", EXPECTED_SIZES)
    def test_renders_button_variants_and_sizes(
        self,
        variant: str,
        size: str,
    ) -> None:
        """Verify <button> renders with data-variant, data-size, and span label."""
        _build_builtin_registry()
        html = Button(label="Run", variant=variant, size=size).render()
        assert '<button class="dds-button"' in html
        assert 'type="button"' in html
        assert f'data-variant="{variant}"' in html
        assert f'data-size="{size}"' in html
        assert "<span>Run</span>" in html
        assert "data-icon-only=" not in html

    @pytest.mark.parametrize("button_type", EXPECTED_BUTTON_TYPES)
    def test_renders_button_types_and_disabled_attribute(
        self,
        button_type: str,
    ) -> None:
        """Verify type attribute and disabled attribute on <button>."""
        _build_builtin_registry()
        html = Button(
            label="Submit",
            button_type=button_type,
            disabled=True,
        ).render()
        assert f'type="{button_type}"' in html
        assert "disabled" in html

    def test_renders_anchor_when_href_provided_and_not_disabled(self) -> None:
        """Verify <a> element renders with href, target, and rel when enabled."""
        _build_builtin_registry()
        html = Button(
            label="Open",
            href="https://example.com",
            target="_blank",
            variant="primary",
        ).render()
        assert '<a class="dds-button"' in html
        assert 'href="https://example.com"' in html
        assert 'target="_blank"' in html
        assert 'rel="noopener noreferrer"' in html
        assert "<button" not in html

    def test_renders_disabled_button_when_href_and_disabled_both_set(self) -> None:
        """Verify disabled=True forces a <button disabled> even when href is set."""
        _build_builtin_registry()
        html = Button(
            label="Open",
            href="https://example.com",
            target="_blank",
            disabled=True,
        ).render()
        assert '<button class="dds-button"' in html
        assert "disabled" in html
        assert "href=" not in html
        assert "<a " not in html

    def test_composes_dds_icon_for_leading_and_trailing_icons(self) -> None:
        """Verify leading and trailing icons render via {% dds__icon %}."""
        _build_builtin_registry()
        sm_html = Button(
            label="Copy",
            size="sm",
            icon="copy",
            icon_trailing="external-link",
        ).render()
        assert 'class="dds-icon"' in sm_html
        assert 'data-icon="copy"' in sm_html
        assert 'data-icon="external-link"' in sm_html
        assert sm_html.count('data-size="sm"') == 3

        lg_html = Button(
            label="Inspect",
            size="lg",
            icon=ICON_NAMES[0],
        ).render()
        assert f'data-icon="{ICON_NAMES[0]}"' in lg_html
        assert 'data-size="md"' in lg_html

    def test_renders_icon_only_button_with_aria_label(self) -> None:
        """Verify icon_only button sets data-icon-only and aria-label and hides span."""
        _build_builtin_registry()
        html = Button(
            label="Toggle dark mode",
            icon="moon",
            icon_trailing="sun",
            icon_only=True,
            pressed=True,
            action="toggle-theme",
        ).render()
        assert 'data-icon-only="true"' in html
        assert 'aria-label="Toggle dark mode"' in html
        assert 'aria-pressed="true"' in html
        assert 'data-action="toggle-theme"' in html
        assert 'data-icon="moon"' in html
        assert 'data-icon="sun"' not in html
        assert "<span>" not in html

    def test_renders_via_dds_button_template_tag(self) -> None:
        """Verify {% dds__button %} works with positional label and keyword args."""
        pos_html = _render_template_tag(source='{% dds__button "Apply" %}')
        assert '<button class="dds-button"' in pos_html
        assert "<span>Apply</span>" in pos_html

        kw_html = _render_template_tag(
            source=(
                '{% dds__button "Reset" variant="danger" size="sm" '
                'icon="reset" action="reset-form" pressed=False %}'
            )
        )
        assert 'data-variant="danger"' in kw_html
        assert 'data-size="sm"' in kw_html
        assert 'data-action="reset-form"' in kw_html
        assert 'aria-pressed="false"' in kw_html
        assert 'data-icon="reset"' in kw_html


class TestButtonStylesheetAndColocation:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, and co-located files."""

    def test_css_layer_and_tier_3_tokens(self) -> None:
        """Verify button.css wraps rules in @layer blocks and maps Tier 3 from Tier 2."""
        css_text = BUTTON_CSS_PATH.read_text(encoding="utf-8")
        assert "@layer blocks {" in css_text
        assert "--_dds-" not in css_text

        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-button",
        )
        assert root_blocks
        root_block_text = "\n".join(root_blocks)
        props = _extract_defined_properties(block_text=root_block_text)
        assert props.get("margin") == "0"

        token_defs = re.findall(
            pattern=r"(--_button-[a-z0-9-]+)\s*:\s*([^;]+);",
            string=css_text,
        )
        assert token_defs
        for _name, value in token_defs:
            assert value.strip().startswith("var(--dds-")

        for required_domain in (
            "var(--dds-control-",
            "var(--dds-state-",
            "var(--dds-status-error-",
            "var(--dds-text-control-",
            "var(--dds-space-",
        ):
            assert required_domain in root_block_text

    def test_css_formatting_and_zero_bem(self) -> None:
        """Verify zero BEM selectors, single quotes, and alphabetised declarations."""
        css_text = BUTTON_CSS_PATH.read_text(encoding="utf-8")
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

    def test_template_hygiene_and_colocated_files(self) -> None:
        """Verify button.html has no BEM or template filters and gallery.py/index.md work."""
        html_source = BUTTON_HTML_PATH.read_text(encoding="utf-8")
        assert "{% load design_components %}" in html_source
        assert "|" not in html_source
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=html_source,
        )
        assert not bem_matches

        _build_builtin_registry()
        cfg = gallery.load_gallery_config(
            source_dir=BUTTON_DIR,
            component_name="button",
        )
        assert cfg.variants
        for variant in cfg.variants:
            rendered = Button(**variant.kwargs).render()
            assert 'class="dds-button"' in rendered

        assert BUTTON_INDEX_MD_PATH.is_file()
        assert BUTTON_INDEX_MD_PATH.read_text(encoding="utf-8").strip()
