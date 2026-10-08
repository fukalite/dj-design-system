"""Unit tests for the built-in ``dds__breadcrumb`` element component."""

import dataclasses
import pathlib
import re

import pytest
from django import template

from dj_design_system import gallery
from dj_design_system.components import base as components_base
from dj_design_system.components.elements import breadcrumb as breadcrumb_package
from dj_design_system.components.elements import icon as icon_package
from dj_design_system.components.elements.breadcrumb import (
    breadcrumb as breadcrumb_module,
)
from dj_design_system.services import registry as registry_service
from tests import conftest


APP_LABEL = "dj_design_system"
COMPONENT_NAME = "breadcrumb"
QUALIFIED_NAME = "dds__breadcrumb"
RELATIVE_PATH = "elements.breadcrumb"
TEMPLATE_PATH = "dj_design_system/components/elements/breadcrumb/breadcrumb.html"
CSS_MEDIA_PATH = "dj_design_system/components/elements/breadcrumb/breadcrumb.css"

BREADCRUMB_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "components"
    / "elements"
    / "breadcrumb"
)
BREADCRUMB_PY_PATH = BREADCRUMB_DIR / "breadcrumb.py"
BREADCRUMB_HTML_PATH = BREADCRUMB_DIR / "breadcrumb.html"
BREADCRUMB_CSS_PATH = BREADCRUMB_DIR / "breadcrumb.css"
BREADCRUMB_INDEX_MD_PATH = BREADCRUMB_DIR / "index.md"


@dataclasses.dataclass(frozen=True)
class TrailNode:
    """Typed trail item stub used to test attribute-based normalization."""

    label: str
    url: str | None = None
    href: str | None = None
    icon: str | None = None


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


class TestBreadcrumbDiscoveryAndMetadata:
    """Verify Breadcrumb exports, metadata, media, and registry discovery."""

    def test_exported_from_package_init(self) -> None:
        """Verify Breadcrumb is exported in dj_design_system.components.elements.breadcrumb."""
        assert breadcrumb_package.Breadcrumb is breadcrumb_module.Breadcrumb
        assert issubclass(breadcrumb_module.Breadcrumb, components_base.TagComponent)

    def test_template_media_and_positional_args(self) -> None:
        """Verify Breadcrumb declares co-located template_name, Media.css, and positional_args."""
        assert breadcrumb_module.Breadcrumb.template_name == TEMPLATE_PATH
        assert breadcrumb_module.Breadcrumb.Media.css == CSS_MEDIA_PATH
        assert breadcrumb_module.Breadcrumb.get_positional_args() == ["items"]

    def test_discovered_as_dds_breadcrumb_in_registry(self) -> None:
        """Verify ComponentRegistry discovers Breadcrumb as internal dds__breadcrumb."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.component_class is breadcrumb_module.Breadcrumb
        assert info.qualified_name == QUALIFIED_NAME
        assert info.relative_path == RELATIVE_PATH
        assert info.is_internal is True
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]


class TestBreadcrumbParametersAndContext:
    """Verify parameter validation and get_context() item normalization."""

    def test_default_parameters_and_empty_context(self) -> None:
        """Verify default parameters produce empty normalized_items and has_items=False."""
        comp = breadcrumb_module.Breadcrumb()
        ctx = comp.get_context()
        assert comp.items == []
        assert ctx["aria_label"] == "Breadcrumb"
        assert ctx["separator_icon"] == "chevron-right"
        assert ctx["normalized_items"] == []
        assert ctx["has_items"] is False

    def test_normalizes_dict_items_and_clears_current_url(self) -> None:
        """Verify dict items with url/href/icon normalize and final item clears url."""
        comp = breadcrumb_module.Breadcrumb(
            items=[
                {"label": "Gallery", "url": "/gallery/", "icon": "folder"},
                {"label": "Elements", "href": "/gallery/elements/"},
                {
                    "label": "Breadcrumb",
                    "url": "/gallery/elements/breadcrumb/",
                    "icon": "component",
                },
            ]
        )
        ctx = comp.get_context()
        assert ctx["has_items"] is True
        assert ctx["normalized_items"] == [
            {
                "label": "Gallery",
                "url": "/gallery/",
                "icon": "folder",
                "is_current": False,
                "has_url": True,
                "has_icon": True,
            },
            {
                "label": "Elements",
                "url": "/gallery/elements/",
                "icon": None,
                "is_current": False,
                "has_url": True,
                "has_icon": False,
            },
            {
                "label": "Breadcrumb",
                "url": None,
                "icon": "component",
                "is_current": True,
                "has_url": False,
                "has_icon": True,
            },
        ]

    def test_normalizes_object_and_plain_string_items(self) -> None:
        """Verify objects with attributes and plain strings normalize properly."""
        comp = breadcrumb_module.Breadcrumb(
            items=[
                TrailNode(label="Docs", href="/docs/", icon="doc"),
                TrailNode(label="Guides"),
                "Getting Started",
            ]
        )
        ctx = comp.get_context()
        assert ctx["has_items"] is True
        assert ctx["normalized_items"] == [
            {
                "label": "Docs",
                "url": "/docs/",
                "icon": "doc",
                "is_current": False,
                "has_url": True,
                "has_icon": True,
            },
            {
                "label": "Guides",
                "url": None,
                "icon": None,
                "is_current": False,
                "has_url": False,
                "has_icon": False,
            },
            {
                "label": "Getting Started",
                "url": None,
                "icon": None,
                "is_current": True,
                "has_url": False,
                "has_icon": False,
            },
        ]

    def test_separator_icon_choices_match_icon_names(self) -> None:
        """Verify separator_icon choices match ICON_NAMES from dds__icon."""
        assert breadcrumb_module.Breadcrumb.separator_icon.choices == list(
            icon_package.ICON_NAMES
        )

    def test_invalid_separator_icon_raises_value_error(self) -> None:
        """Verify an unknown separator_icon raises ValueError."""
        with pytest.raises(expected_exception=ValueError, match="Expected one of"):
            breadcrumb_module.Breadcrumb(separator_icon="not-an-icon")

    def test_invalid_items_type_raises_type_error(self) -> None:
        """Verify passing a non-list to items raises TypeError."""
        with pytest.raises(expected_exception=TypeError, match="Expected list"):
            breadcrumb_module.Breadcrumb(items="invalid")

    def test_python_module_contains_no_html_building_or_icon_instantiation(
        self,
    ) -> None:
        """Verify breadcrumb.py contains no HTML string building or Icon class import."""
        py_text = _read_text(path=BREADCRUMB_PY_PATH)
        assert "format_html" not in py_text
        assert "mark_safe" not in py_text
        assert "Icon(" not in py_text


class TestBreadcrumbRenderingAndTemplate:
    """Verify HTML rendering via template tags, Python API, and template purity."""

    def test_renders_semantic_nav_and_ordered_list(self) -> None:
        """Verify <nav class='dds-breadcrumb'> wraps <ol class='l-cluster'>."""
        trail = [
            {"label": "Home", "url": "/"},
            {"label": "Components", "href": "/components/"},
            {"label": "Breadcrumb", "url": "/components/breadcrumb/"},
        ]
        html = _render_template(
            source="{% dds__breadcrumb items %}",
            context={"items": trail},
        )
        assert '<nav class="dds-breadcrumb" aria-label="Breadcrumb">' in html
        assert '<ol class="l-cluster">' in html
        assert '<a href="/">' in html
        assert '<a href="/components/">' in html
        assert '<span aria-current="page">' in html
        assert 'href="/components/breadcrumb/"' not in html

    def test_renders_separator_icon_between_items_only(self) -> None:
        """Verify separator icon renders before non-first items at size xs."""
        trail = [
            {"label": "First", "url": "/first/"},
            {"label": "Second", "url": "/second/"},
            {"label": "Third"},
        ]
        html = _render_template(
            source='{% dds__breadcrumb items=trail separator_icon="chevron-right" %}',
            context={"trail": trail},
        )
        assert html.count('data-icon="chevron-right"') == 2
        assert html.count('data-size="xs"') == 2

    def test_renders_item_icons_and_static_ancestors(self) -> None:
        """Verify item icons render at size xs and URL-less ancestors render as <span>."""
        trail = [
            {"label": "Root", "icon": "folder"},
            {"label": "Leaf", "icon": "component"},
        ]
        html = _render_template(
            source='{% dds__breadcrumb items=trail aria_label="Path" %}',
            context={"trail": trail},
        )
        assert 'aria-label="Path"' in html
        assert 'data-icon="folder"' in html
        assert 'data-icon="component"' in html
        assert 'data-icon="chevron-right"' in html
        assert "<a " not in html
        assert html.count('aria-current="page"') == 1

    def test_escapes_html_in_labels_and_aria_label(self) -> None:
        """Verify untrusted HTML in item labels and aria_label is escaped."""
        html = _render_template(
            source="{% dds__breadcrumb items=trail aria_label=label %}",
            context={
                "trail": [{"label": "<script>alert(1)</script>"}],
                "label": 'Nav "unsafe"',
            },
        )
        assert "<script>" not in html
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
        assert "Nav &quot;unsafe&quot;" in html

    def test_template_contains_no_filters_or_bem(self) -> None:
        """Verify breadcrumb.html loads design_components and has no filters or BEM."""
        template_text = _read_text(path=BREADCRUMB_HTML_PATH)
        assert template_text.startswith("{% load design_components %}")
        assert "|" not in template_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=template_text,
        )
        assert not bem_matches
        assert "--" not in template_text


class TestBreadcrumbStylesheet:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, and formatting in breadcrumb.css."""

    def test_wrapped_in_layer_blocks_and_sets_zero_margin(self) -> None:
        """Verify breadcrumb.css wraps rules in @layer blocks and sets margin: 0."""
        css_text = _read_text(path=BREADCRUMB_CSS_PATH)
        assert css_text.startswith("@layer blocks {")
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-breadcrumb",
        )
        assert root_blocks
        assert "margin: 0;" in root_blocks[0]

    def test_tier_3_tokens_map_exclusively_from_tier_2_tokens(self) -> None:
        """Verify all --_breadcrumb-* tokens map exclusively from Tier 2 --dds-* tokens."""
        css_text = _read_text(path=BREADCRUMB_CSS_PATH)
        assert "--_dds-" not in css_text
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-breadcrumb",
        )
        root_props = _extract_defined_properties(block_text="\n".join(root_blocks))
        assert root_props
        for name, value in root_props.items():
            assert name.startswith("--_breadcrumb-")
            assert value.startswith("var(--dds-")

        for required_domain in (
            "var(--dds-text-",
            "var(--dds-state-",
            "var(--dds-space-",
        ):
            assert required_domain in css_text

    def test_no_bem_single_quotes_and_alphabetized_declarations(self) -> None:
        """Verify zero BEM selectors, single quotes, and alphabetised declarations."""
        css_text = _read_text(path=BREADCRUMB_CSS_PATH)
        assert '"' not in css_text
        assert "!important" not in css_text
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


class TestBreadcrumbGalleryAndDocs:
    """Verify co-located gallery.py and index.md for dds__breadcrumb."""

    def test_gallery_config_variants_render(self) -> None:
        """Verify gallery.py exports a valid GalleryConfig whose variants all render."""
        _make_registry()
        cfg = gallery.load_gallery_config(
            source_dir=BREADCRUMB_DIR,
            component_name=COMPONENT_NAME,
        )
        assert isinstance(cfg, gallery.GalleryConfig)
        assert len(cfg.variants) >= 3
        for variant in cfg.variants:
            direct_html = breadcrumb_module.Breadcrumb(**variant.kwargs).render()
            assert 'class="dds-breadcrumb"' in direct_html
            rendered = _render_template(
                source=(
                    "{% dds__breadcrumb items=items aria_label=aria_label "
                    "separator_icon=separator_icon %}"
                ),
                context={
                    "items": variant.kwargs.get("items", []),
                    "aria_label": variant.kwargs.get("aria_label", "Breadcrumb"),
                    "separator_icon": variant.kwargs.get(
                        "separator_icon", "chevron-right"
                    ),
                },
            )
            assert 'class="dds-breadcrumb"' in rendered

    def test_index_md_exists_and_documents_component(self) -> None:
        """Verify index.md exists and documents dds__breadcrumb and its parameters."""
        doc_text = _read_text(path=BREADCRUMB_INDEX_MD_PATH)
        assert "dds__breadcrumb" in doc_text
        assert "items" in doc_text
        assert "aria_label" in doc_text
        assert "separator_icon" in doc_text
