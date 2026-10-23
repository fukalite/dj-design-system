"""Unit tests for the built-in ``dds__badge`` element component."""

import pathlib
import re

import pytest
from django import template

from dj_design_system import gallery
from dj_design_system.components import base as components_base
from dj_design_system.components.elements import badge as badge_package
from dj_design_system.components.elements.badge import badge as badge_module
from dj_design_system.services import registry as registry_service
from tests import conftest


GalleryConfig = gallery.GalleryConfig
load_gallery_config = gallery.load_gallery_config


APP_LABEL = "dj_design_system"
COMPONENT_NAME = "badge"
QUALIFIED_NAME = "dds__badge"
RELATIVE_PATH = "elements.badge"
TEMPLATE_PATH = "dj_design_system/components/elements/badge/badge.html"
CSS_MEDIA_PATH = "dj_design_system/components/elements/badge/badge.css"
DEFAULT_VARIANT = "neutral"
EXPECTED_VARIANTS = (
    "neutral",
    "info",
    "success",
    "warning",
    "error",
    "code",
)
STATUS_VARIANTS = ("info", "success", "warning", "error")

BADGE_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "components"
    / "elements"
    / "badge"
)
BADGE_HTML_PATH = BADGE_DIR / "badge.html"
BADGE_CSS_PATH = BADGE_DIR / "badge.css"
BADGE_INDEX_MD_PATH = BADGE_DIR / "index.md"


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


class TestBadgeDiscoveryAndMetadata:
    """Verify Badge class exports, metadata, media, and registry discovery."""

    def test_exported_from_package_init(self) -> None:
        """Verify Badge is exported in dj_design_system.components.elements.badge."""
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
        assert info.is_internal is True
        assert info.media.css == [CSS_MEDIA_PATH]


class TestBadgeParametersAndContext:
    """Verify Badge parameter validation and get_context() normalization."""

    def test_default_variant_and_context(self) -> None:
        """Verify default variant is 'neutral' and normalized in get_context()."""
        comp = badge_module.Badge(label="Optional")
        ctx = comp.get_context()
        assert ctx["label"] == "Optional"
        assert ctx["variant"] == DEFAULT_VARIANT

    def test_none_variant_normalizes_to_default(self) -> None:
        """Verify passing variant=None resolves to 'neutral' in get_context()."""
        comp = badge_module.Badge(label="Draft", variant=None)
        ctx = comp.get_context()
        assert ctx["variant"] == DEFAULT_VARIANT

    @pytest.mark.parametrize("variant", EXPECTED_VARIANTS)
    def test_valid_variants_accepted(self, variant: str) -> None:
        """Verify all 6 semantic badge variants are accepted and rendered."""
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
        assert props["--_badge-text-color"] == f"var(--dds-status-{status}-text-color)"

    def test_code_variant_remaps_font_to_tier_2_code_tokens(self) -> None:
        """Verify [data-variant='code'] remaps --_badge-font and code typography tokens."""
        css_text = _read_text(path=BADGE_CSS_PATH)
        blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-badge[data-variant='code']",
        )
        assert blocks
        props = _extract_defined_properties(block_text="\n".join(blocks))
        assert props["--_badge-bg-color"] == "var(--dds-control-bg-color)"
        assert props["--_badge-border-color"] == "var(--dds-control-border-color)"
        assert props["--_badge-font"] == "var(--dds-text-code-font)"
        assert props["--_badge-text-color"] == "var(--dds-text-default-color)"

    def test_css_formatting_and_no_bem(self) -> None:
        """Verify zero BEM selectors, single quotes, and alphabetized declarations."""
        css_text = _read_text(path=BADGE_CSS_PATH)
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


class TestBadgeGalleryAndDocs:
    """Verify co-located gallery.py and index.md for dds__badge."""

    def test_gallery_config_variants_render(self) -> None:
        """Verify gallery.py exports a valid GalleryConfig whose variants all render."""
        cfg = load_gallery_config(
            source_dir=BADGE_DIR,
            component_name=COMPONENT_NAME,
        )
        assert isinstance(cfg, GalleryConfig)
        assert len(cfg.variants) >= 6
        for variant in cfg.variants:
            rendered = badge_module.Badge(**variant.kwargs).render()
            assert 'class="dds-badge"' in rendered

    def test_index_md_exists_and_documents_component(self) -> None:
        """Verify index.md exists and documents dds__badge and its variants."""
        doc_text = _read_text(path=BADGE_INDEX_MD_PATH)
        assert "dds__badge" in doc_text
        for variant in EXPECTED_VARIANTS:
            assert variant in doc_text
