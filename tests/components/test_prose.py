"""Unit tests for the built-in ``dds__prose`` domain component."""

import pathlib
import re

import pytest
from django import template
from django.utils import safestring

from dj_design_system import components, data, gallery
from dj_design_system.components.domain import prose as prose_package
from dj_design_system.components.domain.prose import prose as prose_module
from dj_design_system.services import canvas as canvas_service
from dj_design_system.services import registry as registry_service
from tests import conftest


APP_LABEL = "dj_design_system"
COMPONENT_NAME = "prose"
QUALIFIED_NAME = "dds__prose"
RELATIVE_PATH = "domain.prose"
TEMPLATE_PATH = "dj_design_system/components/domain/prose/prose.html"
CSS_MEDIA_PATH = "dj_design_system/components/domain/prose/prose.css"

PROSE_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "components"
    / "domain"
    / "prose"
)
PROSE_PY_PATH = PROSE_DIR / "prose.py"
PROSE_HTML_PATH = PROSE_DIR / "prose.html"
PROSE_CSS_PATH = PROSE_DIR / "prose.css"
PROSE_INDEX_MD_PATH = PROSE_DIR / "index.md"
TOKENS_CSS_PATH = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "static"
    / "dj_design_system"
    / "tokens.css"
)
EXPECTED_STYLED_ELEMENTS: tuple[str, ...] = (
    "h1",
    "h2",
    "h3",
    "h4",
    "p",
    "ul",
    "ol",
    "li",
    "a",
    "code",
    "pre",
    "blockquote",
    "table",
    "th",
    "td",
    "hr",
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


class TestProseDiscoveryAndMetadata:
    """Verify Prose exports, metadata, media, and registry discovery."""

    def test_exported_from_package_init(self) -> None:
        """Verify Prose is exported in dj_design_system.components.domain.prose."""
        assert prose_package.Prose is prose_module.Prose
        assert issubclass(prose_module.Prose, components.BlockComponent)

    def test_template_media_and_positional_args(self) -> None:
        """Verify Prose relies on co-located template_name, Media.css, and positional_args."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]
        assert prose_module.Prose.get_positional_args() == ["html"]

    def test_discovered_as_dds_prose_in_registry(self) -> None:
        """Verify ComponentRegistry discovers Prose as internal dds__prose."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.component_class is prose_module.Prose
        assert info.qualified_name == QUALIFIED_NAME
        assert info.relative_path == RELATIVE_PATH
        assert info.is_internal is True
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]


class TestProseParametersAndContext:
    """Verify Prose parameter validation and get_context() shaping."""

    def test_default_parameters_and_empty_context(self) -> None:
        """Verify default parameters produce empty prose_html, false flags, and constrained measure."""
        comp = prose_module.Prose()
        ctx = comp.get_context()
        assert ctx["html"] == ""
        assert ctx["title"] == ""
        assert ctx["measure"] is True
        assert ctx["prose_html"] == ""
        assert ctx["has_title"] is False
        assert ctx["has_body"] is False
        assert ctx["constrain_measure"] is True
        assert comp.content == ""

    def test_html_parameter_populates_safe_prose_html(self) -> None:
        """Verify html parameter is wrapped as SafeString and sets has_body=True."""
        comp = prose_module.Prose(
            html="<p>Trusted markdown</p>",
            title="Architecture",
            measure=False,
        )
        ctx = comp.get_context()
        assert isinstance(ctx["prose_html"], safestring.SafeString)
        assert ctx["prose_html"] == "<p>Trusted markdown</p>"
        assert ctx["has_title"] is True
        assert ctx["has_body"] is True
        assert ctx["constrain_measure"] is False

    def test_block_content_fallback_when_html_omitted(self) -> None:
        """Verify block content is wrapped as SafeString and used when html parameter is empty."""
        comp = prose_module.Prose(content=safestring.SafeString("<p>Block fallback</p>"))
        assert isinstance(comp.content, safestring.SafeString)
        ctx = comp.get_context()
        assert isinstance(ctx["prose_html"], safestring.SafeString)
        assert ctx["prose_html"] == "<p>Block fallback</p>"
        assert ctx["has_body"] is True

    def test_html_parameter_takes_precedence_over_block_content(self) -> None:
        """Verify explicit html parameter overrides block content."""
        comp = prose_module.Prose(
            content="<p>Ignored block</p>",
            html="<p>Explicit html</p>",
        )
        ctx = comp.get_context()
        assert ctx["prose_html"] == "<p>Explicit html</p>"
        assert ctx["has_body"] is True

    def test_whitespace_only_body_sets_has_body_false(self) -> None:
        """Verify whitespace-only html or content sets has_body=False."""
        comp = prose_module.Prose(html="   \n\t  ")
        ctx = comp.get_context()
        assert ctx["has_body"] is False

    def test_invalid_parameter_types_raise_type_error(self) -> None:
        """Verify invalid parameter types raise TypeError."""
        with pytest.raises(expected_exception=TypeError, match="Expected str"):
            prose_module.Prose(html=123)
        with pytest.raises(expected_exception=TypeError, match="Expected str"):
            prose_module.Prose(title=456)
        with pytest.raises(expected_exception=TypeError, match="Expected bool"):
            prose_module.Prose(measure="yes")

    def test_python_module_purity_and_no_private_methods(self) -> None:
        """Verify prose.py has no private helper methods, format_html, or service imports."""
        py_text = _read_text(path=PROSE_PY_PATH)
        assert "format_html" not in py_text
        assert "dj_design_system.services" not in py_text
        private_methods = [
            name
            for name, value in prose_module.Prose.__dict__.items()
            if name.startswith("_")
            and not name.startswith("__")
            and callable(value)
        ]
        assert private_methods == []


class TestProseRenderingAndTemplate:
    """Verify template tag rendering, positional args, measure attribute, and template purity."""

    def test_renders_positional_html_with_title_and_constrained_measure(self) -> None:
        """Verify positional html argument renders trusted HTML, title heading, and constrained attribute."""
        html = _render_template(
            source='{% dds__prose "<p>Hello <strong>world</strong>.</p>" title="Guide" %}{% enddds__prose %}'
        ).strip()
        assert (
            '<div class="dds-prose" data-surface="docs" data-measure="constrained">'
            in html
        )
        assert "<h1 data-prose-title>Guide</h1>" in html
        assert (
            "<div data-prose-body><p>Hello <strong>world</strong>.</p></div>"
            in html
        )

    def test_renders_block_content_with_unconstrained_measure(self) -> None:
        """Verify block body content renders without data-measure when measure=False."""
        html = _render_template(
            source="{% dds__prose measure=False %}<h2>Section</h2><p>Copy</p>{% enddds__prose %}"
        ).strip()
        assert '<div class="dds-prose" data-surface="docs">' in html
        assert 'data-measure="constrained"' not in html
        assert "data-prose-title" not in html
        assert "<div data-prose-body><h2>Section</h2><p>Copy</p></div>" in html

    def test_omits_title_and_body_wrappers_when_empty(self) -> None:
        """Verify empty prose component omits both data-prose-title and data-prose-body."""
        html = _render_template(
            source="{% dds__prose %}{% enddds__prose %}"
        ).strip()
        assert (
            html
            == '<div class="dds-prose" data-surface="docs" data-measure="constrained">\n  \n  \n</div>'
            or (
                "data-prose-title" not in html
                and "data-prose-body" not in html
                and 'class="dds-prose"' in html
            )
        )
        assert "data-prose-title" not in html
        assert "data-prose-body" not in html

    def test_escapes_untrusted_html_in_title_while_preserving_trusted_prose_html(
        self,
    ) -> None:
        """Verify title escapes HTML characters while prose_html renders unescaped."""
        html = _render_template(
            source="{% dds__prose html=doc_html title=raw_title %}{% enddds__prose %}",
            context={
                "raw_title": "<script>alert(1)</script>",
                "doc_html": "<p><code>dds__prose</code></p>",
            },
        )
        assert "<script>" not in html
        assert (
            "<h1 data-prose-title>&lt;script&gt;alert(1)&lt;/script&gt;</h1>"
            in html
        )
        assert "<div data-prose-body><p><code>dds__prose</code></p></div>" in html

    def test_template_contains_no_filters_or_bem(self) -> None:
        """Verify prose.html has zero template filters or BEM class names."""
        template_text = _read_text(path=PROSE_HTML_PATH)
        assert "|" not in template_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=template_text,
        )
        assert not bem_matches
        assert "--" not in template_text


class TestProseStylesheet:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, element coverage, and formatting in prose.css."""

    def test_wrapped_in_layer_blocks_and_sets_zero_margin(self) -> None:
        """Verify prose.css wraps rules in @layer blocks and sets margin: 0 and display: block."""
        css_text = _read_text(path=PROSE_CSS_PATH)
        assert css_text.startswith("@layer blocks {")
        assert "@layer reset" not in css_text
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-prose",
        )
        assert root_blocks
        assert "margin: 0;" in root_blocks[0]
        assert "display: block;" in root_blocks[0]

    def test_tier_3_tokens_map_exclusively_from_defined_tier_2_tokens(self) -> None:
        """Verify all --_prose-* tokens map exclusively to Tier 2 tokens defined in tokens.css."""
        css_text = _read_text(path=PROSE_CSS_PATH)
        tokens_text = _read_text(path=TOKENS_CSS_PATH)
        defined_tier_2 = set(
            re.findall(pattern=r"(--dds-[a-z0-9-]+)\s*:", string=tokens_text)
        )

        assert "--_dds-" not in css_text
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-prose",
        )
        root_props = _extract_defined_properties(block_text="\n".join(root_blocks))
        assert root_props
        assert "--_prose-measure" in root_props
        assert (
            root_props["--_prose-measure"] == "var(--dds-layout-prose-measure)"
        )
        for name, value in root_props.items():
            assert name.startswith("--_prose-")
            match = re.fullmatch(pattern=r"var\((--dds-[a-z0-9-]+)\)", string=value)
            assert match is not None
            assert match.group(1) in defined_tier_2

    @pytest.mark.parametrize(
        argnames="element",
        argvalues=EXPECTED_STYLED_ELEMENTS,
    )
    def test_styles_all_required_descendant_prose_elements(
        self, element: str
    ) -> None:
        """Verify prose.css includes scoped rules for all required descendant HTML elements."""
        css_text = _read_text(path=PROSE_CSS_PATH)
        pattern = re.compile(pattern=rf"\.dds-prose\s+{element}\b")
        assert pattern.search(string=css_text) is not None

    def test_no_bem_single_quotes_and_alphabetized_declarations(self) -> None:
        """Verify zero BEM selectors, single quotes, and alphabetised declarations."""
        css_text = _read_text(path=PROSE_CSS_PATH)
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


class TestProseGalleryAndDocs:
    """Verify co-located gallery.py and index.md for dds__prose."""

    def test_gallery_config_variants_render(self) -> None:
        """Verify gallery.py exports a valid GalleryConfig whose variants all render."""
        reg = _make_registry()
        cfg = gallery.load_gallery_config(
            source_dir=PROSE_DIR,
            component_name=COMPONENT_NAME,
        )
        assert isinstance(cfg, gallery.GalleryConfig)
        assert cfg.group == "Domain"
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
            assert 'class="dds-prose"' in rendered

    def test_index_md_exists_and_documents_component(self) -> None:
        """Verify index.md exists and documents dds__prose and its parameters."""
        doc_text = _read_text(path=PROSE_INDEX_MD_PATH)
        assert "dds__prose" in doc_text
        assert "html" in doc_text
        assert "title" in doc_text
        assert "measure" in doc_text
