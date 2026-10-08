"""Unit tests for the built-in ``dds__usage_example`` domain component."""

import pathlib
import re

import pytest
from django import template

from dj_design_system import components, data, gallery
from dj_design_system.components.domain import (
    usage_example as usage_example_package,
)
from dj_design_system.components.domain.usage_example import (
    usage_example as usage_example_module,
)
from dj_design_system.services import registry as registry_service
from dj_design_system.services import tag_signature as tag_signature_service
from tests import conftest


APP_LABEL = "dj_design_system"
COMPONENT_NAME = "usage_example"
QUALIFIED_NAME = "dds__usage_example"
RELATIVE_PATH = "domain.usage_example"
TEMPLATE_PATH = (
    "dj_design_system/components/domain/usage_example/usage_example.html"
)
CSS_MEDIA_PATH = (
    "dj_design_system/components/domain/usage_example/usage_example.css"
)

USAGE_EXAMPLE_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "components"
    / "domain"
    / "usage_example"
)
USAGE_EXAMPLE_PY_PATH = USAGE_EXAMPLE_DIR / "usage_example.py"
USAGE_EXAMPLE_HTML_PATH = USAGE_EXAMPLE_DIR / "usage_example.html"
USAGE_EXAMPLE_CSS_PATH = USAGE_EXAMPLE_DIR / "usage_example.css"
USAGE_EXAMPLE_INDEX_MD_PATH = USAGE_EXAMPLE_DIR / "index.md"
TOKENS_CSS_PATH = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "static"
    / "dj_design_system"
    / "tokens.css"
)


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


def _make_sample_signature() -> tag_signature_service.TagSignature:
    """Create a sample TagSignature instance for testing code input normalisation."""
    spec = data.CanvasSpec(component_name="dds__button")
    return tag_signature_service.TagSignature(
        minimal='{% dds__button "Save" %}',
        maximal='{% dds__button "Save" variant="primary" %}',
        minimal_html="",
        maximal_html="",
        minimal_spec=spec,
        maximal_spec=spec,
    )


class TestUsageExampleDiscoveryAndMetadata:
    """Verify UsageExample exports, metadata, media, and registry discovery."""

    def test_exported_from_package_init(self) -> None:
        """Verify UsageExample is exported in dj_design_system.components.domain.usage_example."""
        assert (
            usage_example_package.UsageExample
            is usage_example_module.UsageExample
        )
        assert issubclass(
            usage_example_module.UsageExample,
            components.TagComponent,
        )

    def test_template_media_and_positional_args(self) -> None:
        """Verify UsageExample declares co-located template_name, Media.css, and positional_args."""
        assert usage_example_module.UsageExample.template_name == TEMPLATE_PATH
        assert usage_example_module.UsageExample.Media.css == CSS_MEDIA_PATH
        assert usage_example_module.UsageExample.get_positional_args() == [
            "title",
            "code",
        ]

    def test_discovered_as_dds_usage_example_in_registry(self) -> None:
        """Verify ComponentRegistry discovers UsageExample as internal dds__usage_example."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.component_class is usage_example_module.UsageExample
        assert info.qualified_name == QUALIFIED_NAME
        assert info.relative_path == RELATIVE_PATH
        assert info.is_internal is True
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]


class TestUsageExampleParametersAndContext:
    """Verify parameter validation, TagSignature normalisation, and get_context() shaping."""

    def test_default_parameters_and_empty_context(self) -> None:
        """Verify default parameters produce empty strings, default IDs/anchors, and false flags."""
        comp = usage_example_module.UsageExample()
        ctx = comp.get_context()
        assert ctx["title"] == ""
        assert ctx["code"] == ""
        assert ctx["preview_url"] == ""
        assert ctx["canvas_id"] == "preview"
        assert ctx["sandbox_href"] == "#pane-sandbox"
        assert ctx["language"] == "django"
        assert ctx["has_title"] is False
        assert ctx["has_preview"] is False
        assert ctx["has_sandbox_link"] is False
        assert ctx["has_code"] is False
        assert ctx["iframe_title"] == "Component example preview"

    def test_populated_parameters_resolve_flags_and_iframe_title(self) -> None:
        """Verify populated parameters set visibility flags and custom iframe_title."""
        comp = usage_example_module.UsageExample(
            title="Minimal example",
            code='{% dds__button "Save" %}',
            preview_url="/gallery/canvas/?component=dds__button",
            canvas_id="minimal",
            sandbox_href="#sandbox-view",
            language="html",
        )
        ctx = comp.get_context()
        assert ctx["title"] == "Minimal example"
        assert ctx["code"] == '{% dds__button "Save" %}'
        assert ctx["preview_url"] == "/gallery/canvas/?component=dds__button"
        assert ctx["canvas_id"] == "minimal"
        assert ctx["sandbox_href"] == "#sandbox-view"
        assert ctx["language"] == "html"
        assert ctx["has_title"] is True
        assert ctx["has_preview"] is True
        assert ctx["has_sandbox_link"] is True
        assert ctx["has_code"] is True
        assert ctx["iframe_title"] == "Minimal example preview"

    def test_normalises_tag_signature_object_in_init(self) -> None:
        """Verify passing a TagSignature object as code normalises to signature.minimal."""
        sig = _make_sample_signature()
        comp = usage_example_module.UsageExample(
            title="Signature example",
            code=sig,
        )
        ctx = comp.get_context()
        assert comp.code == '{% dds__button "Save" %}'
        assert ctx["code"] == '{% dds__button "Save" %}'
        assert ctx["has_code"] is True

    def test_whitespace_only_code_and_empty_sandbox_href(self) -> None:
        """Verify whitespace-only code sets has_code=False and empty sandbox_href hides link."""
        comp = usage_example_module.UsageExample(
            code="   \n\t  ",
            preview_url="/gallery/canvas/",
            sandbox_href="",
        )
        ctx = comp.get_context()
        assert ctx["has_code"] is False
        assert ctx["has_preview"] is True
        assert ctx["sandbox_href"] == ""
        assert ctx["has_sandbox_link"] is False

    def test_none_fallbacks_in_get_context(self) -> None:
        """Verify explicit None parameter values fall back cleanly in get_context()."""
        comp = usage_example_module.UsageExample(
            title=None,
            code=None,
            preview_url="/gallery/canvas/",
            canvas_id=None,
            sandbox_href=None,
            language=None,
        )
        ctx = comp.get_context()
        assert ctx["title"] == ""
        assert ctx["code"] == ""
        assert ctx["canvas_id"] == "preview"
        assert ctx["sandbox_href"] == "#pane-sandbox"
        assert ctx["language"] == "django"
        assert ctx["has_sandbox_link"] is True

    def test_invalid_parameter_types_raise_type_error(self) -> None:
        """Verify non-string title or preview_url parameters raise TypeError."""
        with pytest.raises(expected_exception=TypeError, match="Expected str"):
            usage_example_module.UsageExample(title=123)
        with pytest.raises(expected_exception=TypeError, match="Expected str"):
            usage_example_module.UsageExample(preview_url=["/canvas/"])

    def test_python_module_purity_and_no_private_methods(self) -> None:
        """Verify usage_example.py has no private helper methods, comments, or service imports."""
        py_text = _read_text(path=USAGE_EXAMPLE_PY_PATH)
        assert "format_html" not in py_text
        assert "mark_safe" not in py_text
        assert "dj_design_system.services" not in py_text
        private_methods = [
            name
            for name, value in usage_example_module.UsageExample.__dict__.items()
            if name.startswith("_")
            and not name.startswith("__")
            and callable(value)
        ]
        assert private_methods == []


class TestUsageExampleRenderingAndTemplate:
    """Verify HTML rendering via template tags, child components, and template purity."""

    def test_renders_title_preview_iframe_sandbox_button_and_code_block(self) -> None:
        """Verify full usage example renders heading, stage preview, sandbox button, and code block."""
        html = _render_template(
            source=(
                '{% dds__usage_example "Minimal example" code_snippet '
                'preview_url="/gallery/canvas/?component=dds__button" '
                'canvas_id="minimal" sandbox_href="#pane-sandbox" %}'
            ),
            context={"code_snippet": '{% dds__button "Save" %}'},
        )
        assert '<section class="dds-usage-example">' in html
        assert "<l-stack>" in html
        assert "<h4 data-usage-title>Minimal example</h4>" in html
        assert '<div data-usage-preview data-surface="stage">' in html
        assert (
            '<iframe src="/gallery/canvas/?component=dds__button" '
            'name="minimal" data-canvas-id="minimal" '
            'title="Minimal example preview"></iframe>'
        ) in html
        assert "<div data-usage-sandbox-link>" in html
        assert 'class="dds-button"' in html
        assert 'href="#pane-sandbox"' in html
        assert 'aria-label="Open in sandbox"' in html
        assert 'data-icon="external-link"' in html
        assert 'data-variant="ghost"' in html
        assert 'data-size="sm"' in html
        assert 'class="dds-code-block"' in html
        assert 'data-language="django"' in html
        assert "{% dds__button &quot;Save&quot; %}" in html

    def test_renders_tag_signature_object_passed_positionally(self) -> None:
        """Verify dds__usage_example renders TagSignature.minimal when passed as positional code."""
        sig = _make_sample_signature()
        html = _render_template(
            source='{% dds__usage_example "Minimal" signature %}',
            context={"signature": sig},
        )
        assert "<h4 data-usage-title>Minimal</h4>" in html
        assert "{% dds__button &quot;Save&quot; %}" in html
        assert "data-usage-preview" not in html

    def test_omits_optional_sections_when_empty(self) -> None:
        """Verify title, preview, sandbox link, and code block omit cleanly when not provided."""
        html_empty = _render_template(source="{% dds__usage_example %}")
        assert '<section class="dds-usage-example">' in html_empty
        assert "data-usage-title" not in html_empty
        assert "data-usage-preview" not in html_empty
        assert "data-usage-sandbox-link" not in html_empty
        assert "dds-code-block" not in html_empty

        html_no_sandbox = _render_template(
            source='{% dds__usage_example preview_url="/canvas/" sandbox_href="" %}',
        )
        assert "data-usage-preview" in html_no_sandbox
        assert 'title="Component example preview"' in html_no_sandbox
        assert "data-usage-sandbox-link" not in html_no_sandbox

    def test_escapes_untrusted_html_in_title_and_code(self) -> None:
        """Verify untrusted HTML in title and code is escaped."""
        html = _render_template(
            source="{% dds__usage_example title=title code=code %}",
            context={
                "title": "<script>alert(1)</script>",
                "code": "<img src=x onerror=alert(1)>",
            },
        )
        assert "<script>" not in html
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
        assert "&lt;img src=x onerror=alert(1)&gt;" in html

    def test_template_contains_no_filters_or_bem(self) -> None:
        """Verify usage_example.html loads design_components and has no filters or BEM."""
        template_text = _read_text(path=USAGE_EXAMPLE_HTML_PATH)
        assert template_text.startswith("{% load design_components %}")
        assert "|" not in template_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=template_text,
        )
        assert not bem_matches
        assert "--" not in template_text


class TestUsageExampleStylesheet:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, and formatting in usage_example.css."""

    def test_wrapped_in_layer_blocks_and_sets_zero_margin(self) -> None:
        """Verify usage_example.css wraps rules in @layer blocks and sets margin: 0."""
        css_text = _read_text(path=USAGE_EXAMPLE_CSS_PATH)
        assert css_text.startswith("@layer blocks {")
        assert "@layer reset" not in css_text
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-usage-example",
        )
        assert root_blocks
        assert "margin: 0;" in root_blocks[0]
        assert "display: block;" in root_blocks[0]

    def test_tier_3_tokens_map_exclusively_from_defined_tier_2_tokens(self) -> None:
        """Verify all --_usage-example-* tokens map to Tier 2 tokens defined in tokens.css."""
        css_text = _read_text(path=USAGE_EXAMPLE_CSS_PATH)
        tokens_text = _read_text(path=TOKENS_CSS_PATH)
        defined_tier_2 = set(
            re.findall(pattern=r"(--dds-[a-z0-9-]+)\s*:", string=tokens_text)
        )

        assert "--_dds-" not in css_text
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-usage-example",
        )
        root_props = _extract_defined_properties(block_text="\n".join(root_blocks))
        assert root_props
        for name, value in root_props.items():
            assert name.startswith("--_usage-example-")
            match = re.fullmatch(pattern=r"var\((--dds-[a-z0-9-]+)\)", string=value)
            assert match is not None
            assert match.group(1) in defined_tier_2

    def test_no_bem_single_quotes_and_alphabetized_declarations(self) -> None:
        """Verify zero BEM selectors, single quotes, and alphabetised declarations."""
        css_text = _read_text(path=USAGE_EXAMPLE_CSS_PATH)
        assert '"' not in css_text
        assert "!important" not in css_text
        assert ".dds-button" not in css_text
        assert ".dds-code-block" not in css_text
        assert ".dds-icon" not in css_text
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


class TestUsageExampleGalleryAndDocs:
    """Verify co-located gallery.py and index.md for dds__usage_example."""

    def test_gallery_config_variants_render(self) -> None:
        """Verify gallery.py exports a valid GalleryConfig whose variants all render."""
        _make_registry()
        cfg = gallery.load_gallery_config(
            source_dir=USAGE_EXAMPLE_DIR,
            component_name=COMPONENT_NAME,
        )
        assert isinstance(cfg, gallery.GalleryConfig)
        assert len(cfg.variants) >= 3
        for variant in cfg.variants:
            rendered = _render_template(
                source=(
                    "{% dds__usage_example title=title code=code "
                    "preview_url=preview_url canvas_id=canvas_id "
                    "sandbox_href=sandbox_href %}"
                ),
                context={
                    "title": variant.kwargs.get("title", ""),
                    "code": variant.kwargs.get("code", ""),
                    "preview_url": variant.kwargs.get("preview_url", ""),
                    "canvas_id": variant.kwargs.get("canvas_id", "preview"),
                    "sandbox_href": variant.kwargs.get(
                        "sandbox_href", "#pane-sandbox"
                    ),
                },
            )
            assert 'class="dds-usage-example"' in rendered

    def test_index_md_exists_and_documents_component(self) -> None:
        """Verify index.md exists and documents dds__usage_example and its parameters."""
        doc_text = _read_text(path=USAGE_EXAMPLE_INDEX_MD_PATH)
        assert "dds__usage_example" in doc_text
        assert "title" in doc_text
        assert "code" in doc_text
        assert "preview_url" in doc_text
        assert "canvas_id" in doc_text
        assert "sandbox_href" in doc_text
        assert "language" in doc_text
