"""Unit tests for the built-in dds__icon component."""

import pathlib
import re

import pytest
from django import template

import dj_design_system.components.elements.icon as icon_package
import dj_design_system.components.elements.icon.icon as icon_module
from dj_design_system import gallery
from dj_design_system.components.elements.icon import ICON_NAMES, Icon
from dj_design_system.services import registry as registry_service
from tests import conftest


ICON_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "components"
    / "elements"
    / "icon"
)
ICON_CSS_PATH = ICON_DIR / "icon.css"
ICON_HTML_PATH = ICON_DIR / "icon.html"
ICON_INDEX_MD_PATH = ICON_DIR / "index.md"

EXPECTED_ICON_NAMES: tuple[str, ...] = (
    "external-link",
    "eye",
    "code",
    "file-code",
    "monitor",
    "box-model",
    "ruler",
    "rtl",
    "component",
    "doc",
    "folder",
    "folder-open",
    "search",
    "menu",
    "close",
    "chevron-right",
    "chevron-down",
    "copy",
    "check",
    "sun",
    "moon",
    "reset",
    "info",
    "success",
    "warning",
    "error",
)

EXPECTED_SIZES: tuple[str, ...] = ("xs", "sm", "md", "lg")


def _build_builtin_registry() -> registry_service.ComponentRegistry:
    """Create a fresh ComponentRegistry populated with built-in dds components."""
    reg = registry_service.ComponentRegistry()
    conftest.discover_app_into_registry(
        reg=reg,
        app_name="dj_design_system",
        app_label="dj_design_system",
    )
    return reg


def _render_template_tag(source: str) -> str:
    """Render a template snippet with built-in dds component tags registered."""
    reg = _build_builtin_registry()
    library = template.Library()
    reg.register_templatetags(library=library)
    engine = template.Engine()
    engine.template_builtins.append(library)
    return engine.from_string(template_code=source).render(context=template.Context())


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


class TestIconExportsAndDiscovery:
    """Verify exports, registry discovery, and metadata for dds__icon."""

    def test_exports_from_module_and_package(self) -> None:
        """Verify Icon and ICON_NAMES are exported from icon.py and __init__.py."""
        assert icon_package.Icon is Icon
        assert icon_module.Icon is Icon
        assert icon_package.ICON_NAMES == EXPECTED_ICON_NAMES
        assert icon_module.ICON_NAMES == EXPECTED_ICON_NAMES
        assert isinstance(ICON_NAMES, tuple)

    def test_registry_discovers_dds_icon(self) -> None:
        """Verify ComponentRegistry registers Icon as dds__icon."""
        reg = _build_builtin_registry()
        info = next(i for i in reg.list_all() if i.name == "icon")
        assert info.component_class is Icon
        assert info.app_label == "dj_design_system"
        assert info.relative_path == "elements.icon"
        assert info.qualified_name == "dds__icon"
        assert info.is_internal is True
        assert (
            info.template_name == "dj_design_system/components/elements/icon/icon.html"
        )
        assert info.media.css == ["dj_design_system/components/elements/icon/icon.css"]


class TestIconParametersAndContext:
    """Verify parameter validation and get_context() shaping."""

    def test_default_parameters_and_decorative_context(self) -> None:
        """Verify omitted label produces decorative aria-hidden context."""
        comp = Icon(name="eye")
        ctx = comp.get_context()
        assert ctx["name"] == "eye"
        assert ctx["size"] == "md"
        assert ctx["label"] == ""
        assert ctx["is_decorative"] is True
        assert ctx["aria_hidden"] == "true"
        assert ctx["role"] is None

    def test_labelled_icon_context_is_accessible(self) -> None:
        """Verify providing label produces role='img' and omits aria-hidden."""
        comp = Icon(name="search", size="lg", label="Search")
        ctx = comp.get_context()
        assert ctx["name"] == "search"
        assert ctx["size"] == "lg"
        assert ctx["label"] == "Search"
        assert ctx["is_decorative"] is False
        assert ctx["aria_hidden"] is None
        assert ctx["role"] == "img"

    def test_invalid_icon_name_raises_value_error(self) -> None:
        """Verify unknown icon identifier raises ValueError."""
        with pytest.raises(expected_exception=ValueError):
            Icon(name="nonexistent-icon")

    def test_invalid_size_raises_value_error(self) -> None:
        """Verify unsupported size raises ValueError."""
        with pytest.raises(expected_exception=ValueError):
            Icon(name="eye", size="2xl")

    def test_no_html_or_mark_safe_in_python_module(self) -> None:
        """Verify icon.py contains zero HTML/SVG strings or mark_safe calls."""
        source = (ICON_DIR / "icon.py").read_text(encoding="utf-8")
        assert "mark_safe" not in source
        assert "format_html" not in source
        assert "<svg" not in source
        assert "<path" not in source


class TestIconRendering:
    """Verify HTML rendering across all 26 icons, sizes, and template tag calls."""

    @pytest.mark.parametrize("icon_name", EXPECTED_ICON_NAMES)
    def test_renders_every_supported_icon_with_svg_shapes(self, icon_name: str) -> None:
        """Verify each icon in ICON_NAMES renders an <svg> with child shape elements."""
        _build_builtin_registry()
        html = Icon(name=icon_name).render()
        assert 'class="dds-icon"' in html
        assert f'data-icon="{icon_name}"' in html
        assert 'data-size="md"' in html
        assert 'viewBox="0 0 24 24"' in html
        assert any(
            tag in html
            for tag in ("<path ", "<circle ", "<rect ", "<polyline ", "<line ")
        )

    @pytest.mark.parametrize("size", EXPECTED_SIZES)
    def test_renders_each_semantic_size(self, size: str) -> None:
        """Verify each size choice renders the corresponding data-size attribute."""
        _build_builtin_registry()
        html = Icon(name="check", size=size).render()
        assert f'data-size="{size}"' in html

    def test_decorative_icon_html_attributes(self) -> None:
        """Verify decorative icon renders aria-hidden='true' and no role or aria-label."""
        _build_builtin_registry()
        html = Icon(name="folder").render()
        assert 'aria-hidden="true"' in html
        assert "role=" not in html
        assert "aria-label=" not in html

    def test_accessible_icon_html_attributes(self) -> None:
        """Verify labelled icon renders role='img' and aria-label without aria-hidden."""
        _build_builtin_registry()
        html = Icon(name="warning", label="Warning indicator").render()
        assert 'role="img"' in html
        assert 'aria-label="Warning indicator"' in html
        assert "aria-hidden=" not in html

    def test_renders_via_dds_icon_template_tag_positional_and_kwargs(self) -> None:
        """Verify {% dds__icon %} supports positional name and keyword arguments."""
        pos_html = _render_template_tag(source='{% dds__icon "external-link" %}')
        assert 'data-icon="external-link"' in pos_html
        assert 'data-size="md"' in pos_html
        assert 'aria-hidden="true"' in pos_html

        kw_html = _render_template_tag(
            source='{% dds__icon "close" size="sm" label="Close modal" %}'
        )
        assert 'data-icon="close"' in kw_html
        assert 'data-size="sm"' in kw_html
        assert 'role="img"' in kw_html
        assert 'aria-label="Close modal"' in kw_html


class TestIconStylesheetAndColocation:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, and co-located files."""

    def test_css_layer_and_tier_3_tokens(self) -> None:
        """Verify icon.css wraps rules in @layer blocks and defines Tier 3 tokens."""
        css_text = ICON_CSS_PATH.read_text(encoding="utf-8")
        assert "@layer blocks {" in css_text
        assert "--_dds-" not in css_text

        root_blocks = _extract_rule_blocks(css_text=css_text, selector=".dds-icon")
        assert root_blocks
        props = _extract_defined_properties(block_text="\n".join(root_blocks))

        for token_name in (
            "--_icon-size-xs",
            "--_icon-size-sm",
            "--_icon-size-md",
            "--_icon-size-lg",
            "--_icon-color",
        ):
            assert token_name in props
            assert props[token_name].startswith("var(--dds-")

        assert props.get("margin") == "0"
        assert props.get("display") == "inline-block"
        assert props.get("vertical-align") == "middle"
        assert props.get("flex-shrink") == "0"

        for size in EXPECTED_SIZES:
            size_blocks = _extract_rule_blocks(
                css_text=css_text,
                selector=f".dds-icon[data-size='{size}']",
            )
            assert size_blocks

    def test_css_formatting_and_zero_bem(self) -> None:
        """Verify zero BEM selectors, single quotes, and alphabetised declarations."""
        css_text = ICON_CSS_PATH.read_text(encoding="utf-8")
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
        """Verify icon.html has no BEM or template filters and gallery.py/index.md work."""
        html_source = ICON_HTML_PATH.read_text(encoding="utf-8")
        assert "|" not in html_source
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=html_source,
        )
        assert not bem_matches

        _build_builtin_registry()
        cfg = gallery.load_gallery_config(
            source_dir=ICON_DIR,
            component_name="icon",
        )
        assert cfg.variants
        for variant in cfg.variants:
            rendered = Icon(**variant.kwargs).render()
            assert "<svg" in rendered

        assert ICON_INDEX_MD_PATH.is_file()
        assert ICON_INDEX_MD_PATH.read_text(encoding="utf-8").strip()
