"""Unit tests for the built-in ``dds__notice`` element component."""

import pathlib
import re

import pytest
from django import template
from django.utils import safestring

from dj_design_system import data
from dj_design_system.components import base as components_base
from dj_design_system.components.elements import notice as notice_package
from dj_design_system.components.elements.icon import ICON_NAMES
from dj_design_system.components.elements.notice import notice as notice_module
from dj_design_system.gallery import GalleryConfig, load_gallery_config
from dj_design_system.services import canvas as canvas_service
from dj_design_system.services import registry as registry_service
from tests import conftest


APP_LABEL = "dj_design_system"
COMPONENT_NAME = "notice"
QUALIFIED_NAME = "dds__notice"
RELATIVE_PATH = "elements.notice"
TEMPLATE_PATH = "dj_design_system/components/elements/notice/notice.html"
CSS_MEDIA_PATH = "dj_design_system/components/elements/notice/notice.css"
DEFAULT_VARIANT = "info"
EXPECTED_VARIANTS = ("info", "success", "warning", "error")

NOTICE_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "components"
    / "elements"
    / "notice"
)
NOTICE_HTML_PATH = NOTICE_DIR / "notice.html"
NOTICE_CSS_PATH = NOTICE_DIR / "notice.css"
NOTICE_INDEX_MD_PATH = NOTICE_DIR / "index.md"


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


class TestNoticeDiscoveryAndMetadata:
    """Verify Notice class exports, metadata, media, and registry discovery."""

    def test_exported_from_package_init(self) -> None:
        """Verify Notice is exported in dj_design_system.components.elements.notice."""
        assert notice_package.Notice is notice_module.Notice
        assert issubclass(notice_module.Notice, components_base.BlockComponent)

    def test_template_and_media_declarations(self) -> None:
        """Verify Notice declares co-located template_name and Media.css."""
        assert notice_module.Notice.template_name == TEMPLATE_PATH
        assert notice_module.Notice.Media.css == CSS_MEDIA_PATH

    def test_discovered_as_dds_notice_in_registry(self) -> None:
        """Verify ComponentRegistry discovers Notice as internal dds__notice."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.component_class is notice_module.Notice
        assert info.qualified_name == QUALIFIED_NAME
        assert info.relative_path == RELATIVE_PATH
        assert info.is_internal is True
        assert info.media.css == [CSS_MEDIA_PATH]


class TestNoticeParametersAndContext:
    """Verify Notice parameter validation and get_context() shaping."""

    def test_default_parameters_and_context(self) -> None:
        """Verify default variant='info', title='', icon='', role='note', and resolved_icon='info'."""
        comp = notice_module.Notice(content=safestring.mark_safe(s="Hello"))
        ctx = comp.get_context()
        assert ctx["variant"] == DEFAULT_VARIANT
        assert ctx["title"] == ""
        assert ctx["icon"] == ""
        assert ctx["resolved_icon"] == "info"
        assert ctx["role"] == "note"
        assert ctx["has_title"] is False
        assert ctx["content"] == "Hello"

    @pytest.mark.parametrize(
        ("variant", "expected_role"),
        [
            ("info", "note"),
            ("success", "note"),
            ("warning", "alert"),
            ("error", "alert"),
        ],
    )
    def test_variant_maps_to_expected_role_and_default_icon(
        self, variant: str, expected_role: str
    ) -> None:
        """Verify each status variant sets role ('note' vs 'alert') and default resolved_icon."""
        comp = notice_module.Notice(variant=variant, title="Heading")
        ctx = comp.get_context()
        assert ctx["variant"] == variant
        assert ctx["resolved_icon"] == variant
        assert ctx["role"] == expected_role
        assert ctx["has_title"] is True
        assert ctx["title"] == "Heading"

    def test_custom_icon_override_in_context(self) -> None:
        """Verify explicit icon parameter overrides the variant status icon."""
        comp = notice_module.Notice(variant="warning", icon="doc")
        ctx = comp.get_context()
        assert ctx["resolved_icon"] == "doc"
        assert ctx["role"] == "alert"

    def test_icon_choices_include_empty_string_and_all_icon_names(self) -> None:
        """Verify icon parameter choices match ['', *ICON_NAMES]."""
        params = notice_module.Notice.get_params()
        assert params["icon"].choices == ["", *ICON_NAMES]

    def test_invalid_variant_raises_value_error(self) -> None:
        """Verify an unsupported variant raises ValueError."""
        with pytest.raises(expected_exception=ValueError, match="Expected one of"):
            notice_module.Notice(variant="critical")

    def test_invalid_icon_raises_value_error(self) -> None:
        """Verify an unknown icon name raises ValueError."""
        with pytest.raises(expected_exception=ValueError, match="Expected one of"):
            notice_module.Notice(icon="nonexistent-icon")


class TestNoticeRenderingAndTemplate:
    """Verify template tag rendering, icon composition, title branching, and template purity."""

    def test_renders_default_info_notice_without_title(self) -> None:
        """Verify default {% dds__notice %} renders aside with role='note', info icon, and no strong tag."""
        html = _render_template(
            source="{% dds__notice %}Body message.{% enddds__notice %}"
        ).strip()
        assert '<aside class="dds-notice" data-variant="info" role="note">' in html
        assert 'class="dds-icon"' in html
        assert 'data-icon="info"' in html
        assert 'data-size="md"' in html
        assert "<strong>" not in html
        assert "<div>Body message.</div>" in html

    def test_renders_error_notice_with_title_and_custom_icon(self) -> None:
        """Verify error notice with title and custom icon renders role='alert', strong heading, and icon."""
        html = _render_template(
            source=(
                '{% dds__notice variant="error" title="Fatal Error" icon="code" %}'
                "Stack trace details."
                "{% enddds__notice %}"
            )
        ).strip()
        assert '<aside class="dds-notice" data-variant="error" role="alert">' in html
        assert 'data-icon="code"' in html
        assert "<strong>Fatal Error</strong>" in html
        assert "<div>Stack trace details.</div>" in html

    def test_escapes_html_in_title(self) -> None:
        """Verify HTML characters in title parameter are escaped."""
        html = _render_template(
            source="{% dds__notice title=raw_title %}Safe body{% enddds__notice %}",
            context={"raw_title": "<script>alert(1)</script>"},
        )
        assert "<script>" not in html
        assert "<strong>&lt;script&gt;alert(1)&lt;/script&gt;</strong>" in html

    def test_template_contains_no_filters_or_bem(self) -> None:
        """Verify notice.html loads design_components and has zero template filters or BEM classes."""
        template_text = _read_text(path=NOTICE_HTML_PATH)
        assert "{% load design_components %}" in template_text
        assert "|" not in template_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=template_text,
        )
        assert not bem_matches


class TestNoticeStylesheet:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, and styleguide rules in notice.css."""

    def test_wrapped_in_layer_blocks_and_sets_zero_margin(self) -> None:
        """Verify notice.css wraps rules in @layer blocks and sets margin: 0 on .dds-notice."""
        css_text = _read_text(path=NOTICE_CSS_PATH)
        assert css_text.startswith("@layer blocks {")
        root_blocks = _extract_rule_blocks(css_text=css_text, selector=".dds-notice")
        assert root_blocks
        assert "margin: 0;" in root_blocks[0]

    def test_tier_3_tokens_map_exclusively_from_tier_2_tokens(self) -> None:
        """Verify .dds-notice defines --_notice-* tokens mapped only from --dds-* tokens."""
        css_text = _read_text(path=NOTICE_CSS_PATH)
        assert "--_dds-" not in css_text
        root_blocks = _extract_rule_blocks(css_text=css_text, selector=".dds-notice")
        root_props = _extract_defined_properties(block_text="\n".join(root_blocks))
        for expected_token in (
            "--_notice-bg-color",
            "--_notice-border-color",
            "--_notice-border-radius",
            "--_notice-border-style",
            "--_notice-border-width",
            "--_notice-font",
            "--_notice-gap",
            "--_notice-padding-block",
            "--_notice-padding-inline",
            "--_notice-text-color",
        ):
            assert expected_token in root_props
        for token_name, token_val in root_props.items():
            assert token_name.startswith("--_notice-")
            assert token_val.startswith("var(--dds-")

    @pytest.mark.parametrize("status", EXPECTED_VARIANTS)
    def test_status_variants_remap_tier_3_tokens(self, status: str) -> None:
        """Verify status variant selectors remap bg, border, and text color tokens."""
        css_text = _read_text(path=NOTICE_CSS_PATH)
        blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=f".dds-notice[data-variant='{status}']",
        )
        assert blocks
        props = _extract_defined_properties(block_text="\n".join(blocks))
        assert props["--_notice-bg-color"] == f"var(--dds-status-{status}-bg-color)"
        assert (
            props["--_notice-border-color"]
            == f"var(--dds-status-{status}-border-color)"
        )
        assert props["--_notice-text-color"] == f"var(--dds-status-{status}-text-color)"

    def test_css_formatting_and_no_bem(self) -> None:
        """Verify zero BEM selectors, single quotes, and alphabetized declarations."""
        css_text = _read_text(path=NOTICE_CSS_PATH)
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


class TestNoticeGalleryAndDocs:
    """Verify co-located gallery.py and index.md for dds__notice."""

    def test_gallery_config_variants_render(self) -> None:
        """Verify gallery.py exports a valid GalleryConfig whose variants all render."""
        reg = _make_registry()
        cfg = load_gallery_config(
            source_dir=NOTICE_DIR,
            component_name=COMPONENT_NAME,
        )
        assert isinstance(cfg, GalleryConfig)
        assert len(cfg.variants) >= 4
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
            assert 'class="dds-notice"' in rendered

    def test_index_md_exists_and_documents_component(self) -> None:
        """Verify index.md exists and documents dds__notice and its variants."""
        doc_text = _read_text(path=NOTICE_INDEX_MD_PATH)
        assert "dds__notice" in doc_text
        for variant in EXPECTED_VARIANTS:
            assert variant in doc_text
