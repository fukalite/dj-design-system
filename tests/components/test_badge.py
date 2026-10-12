"""Unit tests for the built-in ``dds__badge`` element component."""

import pathlib
import re

import pytest
from django import template

from dj_design_system import gallery
from dj_design_system.components import base as components_base
from dj_design_system.components.gallery.elements import badge as badge_package
from dj_design_system.components.gallery.elements.badge import badge as badge_module
from dj_design_system.services import registry as registry_service
from tests import conftest


GalleryConfig = gallery.GalleryConfig
load_gallery_config = gallery.load_gallery_config


APP_LABEL = "dj_design_system"
COMPONENT_NAME = "badge"
QUALIFIED_NAME = "dds__badge"
RELATIVE_PATH = "gallery.elements.badge"
TEMPLATE_PATH = "dj_design_system/components/gallery/elements/badge/badge.html"
CSS_MEDIA_PATH = "dj_design_system/components/gallery/elements/badge/badge.css"
DEFAULT_VARIANT = "neutral"
EXPECTED_VARIANTS = (
    "neutral",
    "info",
    "success",
    "warning",
    "error",
)
STATUS_VARIANTS = ("info", "success", "warning", "error")

BADGE_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "components"
    / "gallery"
    / "elements"
    / "badge"
)
BADGE_HTML_PATH = BADGE_DIR / "badge.html"
BADGE_CSS_PATH = BADGE_DIR / "badge.css"


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
    library = template.Library()
    reg.register_templatetags(library=library)
    engine = template.Engine(
        loaders=["dj_design_system.loaders.ComponentsTemplateLoader"],
    )
    engine.template_builtins.append(library)
    compiled = engine.from_string(template_code=source)
    return compiled.render(context=template.Context(dict_=context or {}))


def _read_text(path: pathlib.Path) -> str:
    """Read UTF-8 text from a file path."""
    return path.read_text(encoding="utf-8")


def _extract_rule_blocks(css_text: str, selector: str) -> list[str]:
    """Extract CSS declaration blocks for a specific selector."""
    return conftest.extract_css_rule_blocks(css_text=css_text, selector=selector)


def _extract_defined_properties(block_text: str) -> dict[str, str]:
    """Extract property and custom property definitions from a CSS block string."""
    matches = re.findall(
        pattern=r"([a-zA-Z0-9_-]+)\s*:\s*([^;]+);",
        string=block_text,
    )
    return {name: value.strip() for name, value in matches}


class TestBadgeDiscoveryAndMetadata:
    """Verify Badge class exports, metadata, media, and registry discovery."""

    def test_exported_from_package_init(self) -> None:
        """Verify Badge is exported in dj_design_system.components.gallery.elements.badge."""
        assert badge_package.Badge is badge_module.Badge
        assert issubclass(badge_module.Badge, components_base.TagComponent)

    def test_template_and_media_declarations(self) -> None:
        """Verify Badge relies on co-located template_name and Media.css auto-discovery."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]
        assert badge_module.Badge.get_positional_args() == ["label"]

    def test_discovered_as_dds_badge_in_registry(self) -> None:
        """Verify ComponentRegistry discovers Badge as internal dds__badge."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.component_class is badge_module.Badge
        assert info.qualified_name == QUALIFIED_NAME
        assert info.relative_path == RELATIVE_PATH
        assert info.is_builtin is True
        assert info.media.css == [CSS_MEDIA_PATH]


class TestBadgeParametersAndContext:
    """Verify Badge parameter validation and get_context() normalization."""

    def test_default_variant_and_context(self) -> None:
        """Verify default variant is 'neutral' and is_code is False in get_context()."""
        comp = badge_module.Badge(label="Optional")
        ctx = comp.get_context()
        assert ctx["label"] == "Optional"
        assert ctx["variant"] == DEFAULT_VARIANT
        assert ctx["is_code"] is False

    def test_none_variant_normalizes_to_default(self) -> None:
        """Verify passing variant=None resolves to 'neutral' in get_context()."""
        comp = badge_module.Badge(label="Draft", variant=None)
        ctx = comp.get_context()
        assert ctx["variant"] == DEFAULT_VARIANT
        assert ctx["is_code"] is False

    def test_is_code_parameter_sets_flag_in_context(self) -> None:
        """Verify is_code=True sets is_code flag in get_context()."""
        comp = badge_module.Badge(label="str", is_code=True)
        ctx = comp.get_context()
        assert ctx["is_code"] is True

    @pytest.mark.parametrize("variant", EXPECTED_VARIANTS)
    def test_valid_variants_accepted(self, variant: str) -> None:
        """Verify all semantic badge variants are accepted and rendered."""
        comp = badge_module.Badge(label="Status", variant=variant)
        html = comp.render().strip()
        assert html == f'<span class="dds-badge" data-variant="{variant}">Status</span>'

    def test_invalid_variant_raises_value_error(self) -> None:
        """Verify an unsupported variant raises ValueError."""
        with pytest.raises(expected_exception=ValueError, match="Expected one of"):
            badge_module.Badge(label="Bad", variant="unknown")

    def test_invalid_label_type_raises_type_error(self) -> None:
        """Verify a non-string label raises TypeError."""
        with pytest.raises(expected_exception=TypeError, match="Expected str"):
            badge_module.Badge(label=123)


class TestBadgeRenderingAndTemplate:
    """Verify template tag rendering, escaping, and template purity."""

    def test_renders_via_positional_template_tag(self) -> None:
        """Verify {% dds__badge 'Label' %} renders with default neutral variant."""
        html = _render_template(source='{% dds__badge "Optional" %}').strip()
        assert html == '<span class="dds-badge" data-variant="neutral">Optional</span>'

    def test_renders_via_keyword_template_tag(self) -> None:
        """Verify {% dds__badge %} supports keyword variant argument."""
        html = _render_template(
            source='{% dds__badge "Required" variant="error" %}'
        ).strip()
        assert html == '<span class="dds-badge" data-variant="error">Required</span>'

    def test_renders_code_tag_when_is_code_is_true(self) -> None:
        """Verify is_code=True wraps label in semantic <code> tag."""
        html = badge_module.Badge(label="str", is_code=True).render().strip()
        assert (
            html
            == '<span class="dds-badge" data-variant="neutral"><code>str</code></span>'
        )

    def test_renders_code_tag_with_status_variant(self) -> None:
        """Verify is_code=True composes with semantic status variants."""
        html = (
            badge_module.Badge(label="DeprecatedType", variant="warning", is_code=True)
            .render()
            .strip()
        )
        assert (
            html
            == '<span class="dds-badge" data-variant="warning"><code>DeprecatedType</code></span>'
        )

    def test_escapes_html_in_label(self) -> None:
        """Verify HTML characters in label are escaped automatically."""
        html = badge_module.Badge(label="<script>alert(1)</script>").render().strip()
        assert "<script>" not in html
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html

    def test_template_contains_no_filters_or_bem(self) -> None:
        """Verify badge.html contains zero template filters and zero BEM classes."""
        template_text = _read_text(path=BADGE_HTML_PATH)
        assert "|" not in template_text
        assert "__" not in template_text
        assert "--" not in template_text


class TestBadgeStylesheet:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, and styleguide rules in badge.css."""

    def test_wrapped_in_layer_blocks_and_sets_zero_margin(self) -> None:
        """Verify badge.css wraps rules in @layer blocks and sets margin: 0 on .dds-badge."""
        css_text = _read_text(path=BADGE_CSS_PATH)
        assert css_text.startswith("@layer blocks {")
        root_blocks = _extract_rule_blocks(css_text=css_text, selector=".dds-badge")
        assert root_blocks
        assert "margin: 0;" in root_blocks[0]

    def test_tier_3_tokens_map_exclusively_from_tier_2_tokens(self) -> None:
        """Verify .dds-badge defines --_badge-* tokens mapped only from --dds-* tokens."""
        css_text = _read_text(path=BADGE_CSS_PATH)
        assert "--_dds-" not in css_text
        root_blocks = _extract_rule_blocks(css_text=css_text, selector=".dds-badge")
        root_props = _extract_defined_properties(block_text="\n".join(root_blocks))
        for expected_token in (
            "--_badge-bg-color",
            "--_badge-border-color",
            "--_badge-font",
            "--_badge-padding-block",
            "--_badge-padding-inline",
            "--_badge-text-color",
        ):
            assert expected_token in root_props
            assert root_props[expected_token].startswith("var(--dds-")

    @pytest.mark.parametrize("status", STATUS_VARIANTS)
    def test_status_variants_remap_tier_3_tokens(self, status: str) -> None:
        """Verify status variant selectors remap bg, border, and text color tokens."""
        css_text = _read_text(path=BADGE_CSS_PATH)
        blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=f".dds-badge[data-variant='{status}']",
        )
        assert blocks
        props = _extract_defined_properties(block_text="\n".join(blocks))
        assert props["--_badge-bg-color"] == f"var(--dds-status-{status}-bg-color)"
        assert (
            props["--_badge-border-color"] == f"var(--dds-status-{status}-border-color)"
        )
        assert (
            props["--_badge-border-radius"]
            == f"var(--dds-status-{status}-border-radius)"
        )
        assert (
            props["--_badge-border-width"] == f"var(--dds-status-{status}-border-width)"
        )
        assert props["--_badge-text-color"] == f"var(--dds-status-{status}-text-color)"

    def test_nested_code_element_styles(self) -> None:
        """Verify .dds-badge > code sets monospace typography tokens."""
        css_text = _read_text(path=BADGE_CSS_PATH)
        blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-badge > code",
        )
        assert blocks
        props = _extract_defined_properties(block_text="\n".join(blocks))
        assert props["font-family"] == "var(--dds-text-code-font)"
        assert props["font-size"] == "var(--dds-text-code-size)"
        assert props["font-weight"] == "var(--dds-text-code-weight)"
        assert props["line-height"] == "var(--dds-text-code-line-height)"
        assert props["letter-spacing"] == "var(--dds-text-code-letter-spacing)"


class TestBadgeGalleryAndDocs:
    """Verify co-located gallery.py and index.md for dds__badge."""

    def test_gallery_config_variants_render(self) -> None:
        """Verify gallery.py exports a valid GalleryConfig with leaf node configuration."""
        cfg = load_gallery_config(
            source_dir=BADGE_DIR,
            component_name=COMPONENT_NAME,
        )
        assert isinstance(cfg, GalleryConfig)
        assert cfg.variants == []
        rendered = badge_module.Badge(**cfg.param_defaults).render()
        assert 'class="dds-badge"' in rendered

    def test_component_docstring_documents_usage(self) -> None:
        """Verify Badge docstring documents component and when to use it."""
        doc = badge_module.Badge.__doc__ or ""
        assert "When to Use:" in doc
