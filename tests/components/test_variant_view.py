"""Unit tests for the built-in ``dds__variant_view`` domain component."""

import dataclasses
import pathlib
import re

import pytest
from django import template
from django.utils import safestring

from dj_design_system import components, gallery
from dj_design_system.components.domain import (
    variant_view as variant_view_package,
)
from dj_design_system.components.domain.variant_view import (
    variant_view as variant_view_module,
)
from dj_design_system.services import registry as registry_service
from tests import conftest


APP_LABEL = "dj_design_system"
COMPONENT_NAME = "variant_view"
QUALIFIED_NAME = "dds__variant_view"
RELATIVE_PATH = "domain.variant_view"
TEMPLATE_PATH = (
    "dj_design_system/components/domain/variant_view/variant_view.html"
)
CSS_MEDIA_PATH = (
    "dj_design_system/components/domain/variant_view/variant_view.css"
)

VARIANT_VIEW_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "components"
    / "domain"
    / "variant_view"
)
VARIANT_VIEW_PY_PATH = VARIANT_VIEW_DIR / "variant_view.py"
VARIANT_VIEW_HTML_PATH = VARIANT_VIEW_DIR / "variant_view.html"
VARIANT_VIEW_CSS_PATH = VARIANT_VIEW_DIR / "variant_view.css"
VARIANT_VIEW_INDEX_MD_PATH = VARIANT_VIEW_DIR / "index.md"
TOKENS_CSS_PATH = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "static"
    / "dj_design_system"
    / "tokens.css"
)


@dataclasses.dataclass(frozen=True)
class StubTagSignature:
    """Stub TagSignature object exposing a ``minimal`` snippet attribute."""

    minimal: str


@dataclasses.dataclass(frozen=True)
class StubNameOnlyVariant:
    """Stub variant object with ``label=None`` to verify fallback to ``name``."""

    name: str
    label: str | None = None


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
        libraries={
            "design_components": "dj_design_system.templatetags.design_components"
        },
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


class TestVariantViewDiscoveryAndMetadata:
    """Verify VariantView exports, metadata, media, and registry discovery."""

    def test_exported_from_package_init(self) -> None:
        """Verify VariantView is exported in dj_design_system.components.domain.variant_view."""
        assert (
            variant_view_package.VariantView
            is variant_view_module.VariantView
        )
        assert issubclass(
            variant_view_module.VariantView,
            components.TagComponent,
        )

    def test_template_media_and_positional_args(self) -> None:
        """Verify VariantView declares co-located template_name, Media.css, and positional_args."""
        assert variant_view_module.VariantView.template_name == TEMPLATE_PATH
        assert variant_view_module.VariantView.Media.css == CSS_MEDIA_PATH
        assert variant_view_module.VariantView.get_positional_args() == [
            "variant_label",
        ]

    def test_discovered_as_dds_variant_view_in_registry(self) -> None:
        """Verify ComponentRegistry discovers VariantView as internal dds__variant_view."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.component_class is variant_view_module.VariantView
        assert info.qualified_name == QUALIFIED_NAME
        assert info.relative_path == RELATIVE_PATH
        assert info.is_internal is True
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]


class TestVariantViewParametersAndContext:
    """Verify parameter normalization in __init__ and context shaping in get_context()."""

    def test_default_parameters_and_empty_context(self) -> None:
        """Verify default parameters produce fallback labels and false conditional flags."""
        comp = variant_view_module.VariantView()
        ctx = comp.get_context()
        assert ctx["variant_label"] == "Variant"
        assert ctx["badge_label"] == "Variant"
        assert ctx["description_html"] == ""
        assert ctx["description_safe"] == ""
        assert ctx["has_description"] is False
        assert ctx["preview_url"] == ""
        assert ctx["has_preview"] is False
        assert ctx["sandbox_href"] == "#pane-sandbox"
        assert ctx["has_sandbox_link"] is False
        assert ctx["code"] == ""
        assert ctx["has_code"] is False
        assert ctx["iframe_title"] == "Variant preview"

    def test_normalizes_variant_and_tag_signature_objects_in_init(self) -> None:
        """Verify __init__ normalizes Variant instances and TagSignature objects to strings."""
        variant_obj = gallery.Variant(name="primary", label="Primary Button")
        signature_obj = StubTagSignature(
            minimal="{% dds__button 'Save' variant='primary' %}"
        )
        comp = variant_view_module.VariantView(
            variant_label=variant_obj,
            code=signature_obj,
        )
        ctx = comp.get_context()
        assert comp.variant_label == "Primary Button"
        assert comp.code == "{% dds__button 'Save' variant='primary' %}"
        assert ctx["variant_label"] == "Primary Button"
        assert ctx["iframe_title"] == "Primary Button preview"
        assert ctx["has_code"] is True

    def test_normalizes_variant_object_without_label_to_name(self) -> None:
        """Verify __init__ falls back to .name when a variant object's .label is None."""
        stub_variant = StubNameOnlyVariant(name="ghost_sm", label=None)
        comp = variant_view_module.VariantView(variant_label=stub_variant)
        ctx = comp.get_context()
        assert comp.variant_label == "ghost_sm"
        assert ctx["variant_label"] == "ghost_sm"

    def test_description_and_code_whitespace_handling(self) -> None:
        """Verify whitespace-only description_html or code sets has_description/has_code to False."""
        comp = variant_view_module.VariantView(
            variant_label="Custom",
            description_html="   \n  ",
            code="   \t  ",
            preview_url="/canvas/custom/",
            sandbox_href="",
        )
        ctx = comp.get_context()
        assert ctx["has_description"] is False
        assert ctx["has_code"] is False
        assert ctx["has_preview"] is True
        assert ctx["has_sandbox_link"] is False

    def test_description_safe_wraps_html_in_safestring(self) -> None:
        """Verify non-empty description_html is wrapped in SafeString."""
        comp = variant_view_module.VariantView(
            description_html="<p>Variant <strong>prose</strong>.</p>",
        )
        ctx = comp.get_context()
        assert ctx["has_description"] is True
        assert isinstance(ctx["description_safe"], safestring.SafeString)
        assert str(ctx["description_safe"]) == "<p>Variant <strong>prose</strong>.</p>"

    def test_invalid_parameter_types_raise_type_error(self) -> None:
        """Verify invalid non-string parameter types raise TypeError."""
        with pytest.raises(expected_exception=TypeError, match="Expected str"):
            variant_view_module.VariantView(preview_url=123)
        with pytest.raises(expected_exception=TypeError, match="Expected str"):
            variant_view_module.VariantView(badge_label=["invalid"])

    def test_python_module_purity_and_no_private_methods(self) -> None:
        """Verify variant_view.py has no private helper methods, comments, or mark_safe."""
        py_text = _read_text(path=VARIANT_VIEW_PY_PATH)
        assert "format_html" not in py_text
        assert "mark_safe" not in py_text
        assert "dj_design_system.services" not in py_text
        private_methods = [
            name
            for name, value in variant_view_module.VariantView.__dict__.items()
            if name.startswith("_")
            and not name.startswith("__")
            and callable(value)
        ]
        assert private_methods == []


class TestVariantViewRenderingAndTemplate:
    """Verify HTML rendering via template tags, child components, and template purity."""

    def test_renders_full_variant_view_with_all_sections(self) -> None:
        """Verify full variant view renders header badge, title, description, preview, sandbox link, and code block."""
        html = _render_template(
            source=(
                '{% dds__variant_view "Primary Action" '
                "description_html=desc "
                'preview_url="/canvas/button/?variant=primary" '
                "code=code "
                'badge_label="Preset" '
                'sandbox_href="#custom-sandbox" %}'
            ),
            context={
                "desc": "<p>Primary call to action.</p>",
                "code": "{% dds__button 'Save' variant='primary' %}",
            },
        )
        assert '<section class="dds-variant-view" data-surface="docs">' in html
        assert "<l-stack>" in html
        assert "<l-cluster data-variant-header>" in html
        assert 'class="dds-badge"' in html
        assert 'data-variant="info"' in html
        assert ">Preset<" in html
        assert "<h2 data-variant-title>Primary Action</h2>" in html
        assert (
            "<div data-variant-description><p>Primary call to action.</p></div>"
            in html
        )
        assert '<div data-variant-preview data-surface="stage">' in html
        assert (
            '<iframe src="/canvas/button/?variant=primary" name="variant" '
            'data-canvas-id="variant" title="Primary Action preview"></iframe>'
            in html
        )
        assert "<div data-variant-sandbox-link>" in html
        assert 'href="#custom-sandbox"' in html
        assert 'aria-label="Open in sandbox"' in html
        assert 'data-icon="external-link"' in html
        assert "<dds-code-block" in html
        assert "dds__button" in html
        assert "primary" in html

    def test_omits_optional_sections_when_not_provided(self) -> None:
        """Verify description, preview stage, and code block are omitted when empty."""
        html = _render_template(source='{% dds__variant_view "Minimal Variant" %}')
        assert "<h2 data-variant-title>Minimal Variant</h2>" in html
        assert ">Variant<" in html
        assert "data-variant-description" not in html
        assert "data-variant-preview" not in html
        assert "data-variant-sandbox-link" not in html
        assert "<dds-code-block" not in html

    def test_omits_sandbox_link_when_sandbox_href_is_empty(self) -> None:
        """Verify sandbox button is omitted when sandbox_href is empty even if preview_url is set."""
        html = _render_template(
            source=(
                '{% dds__variant_view "Preview Only" '
                'preview_url="/canvas/button/" sandbox_href="" %}'
            ),
        )
        assert "data-variant-preview" in html
        assert 'src="/canvas/button/"' in html
        assert "data-variant-sandbox-link" not in html

    def test_escapes_untrusted_html_in_variant_label_and_badge_label(self) -> None:
        """Verify untrusted HTML in variant_label and badge_label is escaped."""
        html = _render_template(
            source="{% dds__variant_view variant_label=label badge_label=badge %}",
            context={
                "label": "<script>alert(1)</script>",
                "badge": "<b>Unsafe</b>",
            },
        )
        assert "<script>" not in html
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
        assert "&lt;b&gt;Unsafe&lt;/b&gt;" in html

    def test_template_contains_no_filters_or_bem(self) -> None:
        """Verify variant_view.html loads design_components and has no filters or BEM."""
        template_text = _read_text(path=VARIANT_VIEW_HTML_PATH)
        assert template_text.startswith("{% load design_components %}")
        assert "|" not in template_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=template_text,
        )
        assert not bem_matches
        assert "--" not in template_text


class TestVariantViewStylesheet:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, and formatting in variant_view.css."""

    def test_wrapped_in_layer_blocks_and_sets_zero_margin(self) -> None:
        """Verify variant_view.css wraps rules in @layer blocks and sets margin: 0."""
        css_text = _read_text(path=VARIANT_VIEW_CSS_PATH)
        assert css_text.startswith("@layer blocks {")
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-variant-view",
        )
        assert root_blocks
        assert "margin: 0;" in root_blocks[0]
        assert "display: block;" in root_blocks[0]

    def test_tier_3_tokens_map_exclusively_from_defined_tier_2_tokens(self) -> None:
        """Verify all --_variant-view-* tokens map to Tier 2 tokens defined in tokens.css."""
        css_text = _read_text(path=VARIANT_VIEW_CSS_PATH)
        tokens_text = _read_text(path=TOKENS_CSS_PATH)
        defined_tier_2 = set(
            re.findall(pattern=r"(--dds-[a-z0-9-]+)\s*:", string=tokens_text)
        )

        assert "--_dds-" not in css_text
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-variant-view",
        )
        root_props = _extract_defined_properties(block_text="\n".join(root_blocks))
        assert root_props
        for name, value in root_props.items():
            assert name.startswith("--_variant-view-")
            match = re.fullmatch(pattern=r"var\((--dds-[a-z0-9-]+)\)", string=value)
            assert match is not None
            assert match.group(1) in defined_tier_2

    def test_no_bem_single_quotes_and_alphabetized_declarations(self) -> None:
        """Verify zero BEM selectors, single quotes, and alphabetised declarations."""
        css_text = _read_text(path=VARIANT_VIEW_CSS_PATH)
        assert '"' not in css_text
        assert "!important" not in css_text
        assert ".dds-badge" not in css_text
        assert ".dds-button" not in css_text
        assert ".dds-code-block" not in css_text
        assert "dds-code-block" not in css_text
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


class TestVariantViewGalleryAndDocs:
    """Verify co-located gallery.py and index.md for dds__variant_view."""

    def test_gallery_config_variants_render(self) -> None:
        """Verify gallery.py exports a valid GalleryConfig whose variants all render."""
        _make_registry()
        cfg = gallery.load_gallery_config(
            source_dir=VARIANT_VIEW_DIR,
            component_name=COMPONENT_NAME,
        )
        assert isinstance(cfg, gallery.GalleryConfig)
        assert len(cfg.variants) >= 3
        for variant in cfg.variants:
            rendered = _render_template(
                source=(
                    "{% dds__variant_view variant_label=variant_label "
                    "description_html=description_html preview_url=preview_url "
                    "code=code badge_label=badge_label sandbox_href=sandbox_href %}"
                ),
                context={
                    "variant_label": variant.kwargs.get("variant_label", ""),
                    "description_html": variant.kwargs.get(
                        "description_html", ""
                    ),
                    "preview_url": variant.kwargs.get("preview_url", ""),
                    "code": variant.kwargs.get("code", ""),
                    "badge_label": variant.kwargs.get("badge_label", "Variant"),
                    "sandbox_href": variant.kwargs.get(
                        "sandbox_href", "#pane-sandbox"
                    ),
                },
            )
            assert 'class="dds-variant-view"' in rendered

    def test_index_md_exists_and_documents_component(self) -> None:
        """Verify index.md exists and documents dds__variant_view and its parameters."""
        doc_text = _read_text(path=VARIANT_VIEW_INDEX_MD_PATH)
        assert "dds__variant_view" in doc_text
        assert "variant_label" in doc_text
        assert "description_html" in doc_text
        assert "preview_url" in doc_text
        assert "code" in doc_text
        assert "badge_label" in doc_text
        assert "sandbox_href" in doc_text
