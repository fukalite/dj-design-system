"""Unit tests for the built-in ``dds__folder_listing`` domain component."""

import dataclasses
import pathlib
import re

import pytest
from django import template

from dj_design_system import data, gallery, types
from dj_design_system.components import base as components_base
from dj_design_system.components.domain import (
    folder_listing as folder_listing_package,
)
from dj_design_system.components.domain.folder_listing import (
    folder_listing as folder_listing_module,
)
from dj_design_system.services import registry as registry_service
from tests import conftest


APP_LABEL = "dj_design_system"
COMPONENT_NAME = "folder_listing"
QUALIFIED_NAME = "dds__folder_listing"
RELATIVE_PATH = "domain.folder_listing"
TEMPLATE_PATH = (
    "dj_design_system/components/domain/folder_listing/folder_listing.html"
)
CSS_MEDIA_PATH = (
    "dj_design_system/components/domain/folder_listing/folder_listing.css"
)

FOLDER_LISTING_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "components"
    / "domain"
    / "folder_listing"
)
FOLDER_LISTING_PY_PATH = FOLDER_LISTING_DIR / "folder_listing.py"
FOLDER_LISTING_HTML_PATH = FOLDER_LISTING_DIR / "folder_listing.html"
FOLDER_LISTING_CSS_PATH = FOLDER_LISTING_DIR / "folder_listing.css"
FOLDER_LISTING_INDEX_MD_PATH = FOLDER_LISTING_DIR / "index.md"
TOKENS_CSS_PATH = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "static"
    / "dj_design_system"
    / "tokens.css"
)


@dataclasses.dataclass(frozen=True)
class StubFolderItem:
    """Attribute-based folder item stub for testing object normalization."""

    label: str
    url: str = ""
    node_type: str | None = None
    icon: str | None = None
    children: tuple[object, ...] = ()
    has_children: bool | None = None
    is_component: bool = False
    is_document: bool = False
    is_variant: bool = False


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


class TestFolderListingDiscoveryAndMetadata:
    """Verify FolderListing exports, metadata, media, and registry discovery."""

    def test_exported_from_package_init(self) -> None:
        """Verify FolderListing is exported in dj_design_system.components.domain.folder_listing."""
        assert (
            folder_listing_package.FolderListing
            is folder_listing_module.FolderListing
        )
        assert issubclass(
            folder_listing_module.FolderListing,
            components_base.TagComponent,
        )

    def test_template_media_and_positional_args(self) -> None:
        """Verify FolderListing declares co-located template_name, Media.css, and positional_args."""
        assert folder_listing_module.FolderListing.template_name == TEMPLATE_PATH
        assert folder_listing_module.FolderListing.Media.css == CSS_MEDIA_PATH
        assert folder_listing_module.FolderListing.get_positional_args() == [
            "title",
            "items",
        ]

    def test_discovered_as_dds_folder_listing_in_registry(self) -> None:
        """Verify ComponentRegistry discovers FolderListing as internal dds__folder_listing."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.component_class is folder_listing_module.FolderListing
        assert info.qualified_name == QUALIFIED_NAME
        assert info.relative_path == RELATIVE_PATH
        assert info.is_internal is True
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]


class TestFolderListingParametersAndContext:
    """Verify parameter validation and get_context() item normalization."""

    def test_default_parameters_and_empty_context(self) -> None:
        """Verify default parameters produce empty items, default message, and false flags."""
        comp = folder_listing_module.FolderListing()
        ctx = comp.get_context()
        assert comp.items is None
        assert ctx["title"] == ""
        assert ctx["has_title"] is False
        assert ctx["items"] == []
        assert ctx["normalized_items"] == []
        assert ctx["has_items"] is False
        assert ctx["empty_message"] == "This folder is empty."
        assert ctx["show_debug_hint"] is False

    def test_normalizes_dict_items_across_all_node_kinds(self) -> None:
        """Verify dict items normalize icons, badges, child counts, and fallback URLs."""
        comp = folder_listing_module.FolderListing(
            title="Elements",
            items=[
                {
                    "label": "Forms",
                    "url": "/gallery/forms/",
                    "node_type": "folder",
                    "children": ["a", "b", "c"],
                },
                {
                    "label": "Button",
                    "url": "/gallery/button/",
                    "type": "component",
                    "icon": "eye",
                    "children": ["basic"],
                },
                {
                    "label": "Architecture",
                    "node_type": "document",
                    "icon": "invalid-icon-name",
                },
                {
                    "label": "Danger Button",
                    "url": "/gallery/button/?variant=danger",
                    "type": "variant",
                },
            ],
            show_debug_hint=True,
        )
        ctx = comp.get_context()
        assert ctx["title"] == "Elements"
        assert ctx["has_title"] is True
        assert ctx["has_items"] is True
        assert ctx["show_debug_hint"] is True
        assert ctx["normalized_items"] == [
            {
                "label": "Forms",
                "url": "/gallery/forms/",
                "node_kind": "folder",
                "icon": "folder",
                "badge_label": "Folder",
                "badge_variant": "neutral",
                "child_count_label": "3 items",
                "has_child_count": True,
            },
            {
                "label": "Button",
                "url": "/gallery/button/",
                "node_kind": "component",
                "icon": "eye",
                "badge_label": "Component",
                "badge_variant": "info",
                "child_count_label": "1 item",
                "has_child_count": True,
            },
            {
                "label": "Architecture",
                "url": "#",
                "node_kind": "document",
                "icon": "doc",
                "badge_label": "Document",
                "badge_variant": "neutral",
                "child_count_label": "",
                "has_child_count": False,
            },
            {
                "label": "Danger Button",
                "url": "/gallery/button/?variant=danger",
                "node_kind": "variant",
                "icon": "code",
                "badge_label": "Variant",
                "badge_variant": "code",
                "child_count_label": "",
                "has_child_count": False,
            },
        ]

    def test_normalizes_navnode_and_stub_objects(self) -> None:
        """Verify NavNode instances and attribute-based objects normalize accurately."""
        reg = _make_registry()
        button_info = reg.get_by_name(name="button", app_label=APP_LABEL)
        variant_obj = gallery.Variant(name="basic", label="Basic")

        child_doc = data.NavNode(
            label="Overview",
            slug="overview",
            node_type=types.NodeType.DOCUMENT,
            doc_path=FOLDER_LISTING_INDEX_MD_PATH,
            url="/gallery/docs/overview/",
        )
        folder_node = data.NavNode(
            label="Guides",
            slug="guides",
            node_type=types.NodeType.FOLDER,
            children=[child_doc],
            url="/gallery/guides/",
        )
        component_node = data.NavNode(
            label="Button",
            slug="button",
            node_type=types.NodeType.COMPONENT,
            component=button_info,
            url="/gallery/button/",
        )
        variant_node = data.NavNode(
            label="Basic",
            slug="basic",
            node_type=types.NodeType.VARIANT,
            variant=variant_obj,
            url="/gallery/button/?variant=basic",
        )
        stub_suppressed_children = StubFolderItem(
            label="Empty Subfolder",
            children=("hidden",),
            has_children=False,
        )

        comp = folder_listing_module.FolderListing(
            items=[
                folder_node,
                component_node,
                child_doc,
                variant_node,
                stub_suppressed_children,
            ],
        )
        ctx = comp.get_context()
        items = ctx["normalized_items"]
        assert items[0]["node_kind"] == "folder"
        assert items[0]["child_count_label"] == "1 item"
        assert items[0]["has_child_count"] is True
        assert items[1]["node_kind"] == "component"
        assert items[1]["badge_variant"] == "info"
        assert items[2]["node_kind"] == "document"
        assert items[2]["icon"] == "doc"
        assert items[3]["node_kind"] == "variant"
        assert items[3]["icon"] == "code"
        assert items[3]["badge_variant"] == "code"
        assert items[4]["url"] == "#"
        assert items[4]["has_child_count"] is False

    def test_invalid_parameter_types_raise_type_error(self) -> None:
        """Verify invalid parameter types raise TypeError."""
        with pytest.raises(expected_exception=TypeError, match="Expected list"):
            folder_listing_module.FolderListing(items="not-a-list")
        with pytest.raises(expected_exception=TypeError, match="Expected bool"):
            folder_listing_module.FolderListing(show_debug_hint="yes")

    def test_python_module_purity_and_no_private_methods(self) -> None:
        """Verify folder_listing.py has no private helper methods or HTML string building."""
        py_text = _read_text(path=FOLDER_LISTING_PY_PATH)
        assert "format_html" not in py_text
        assert "mark_safe" not in py_text
        assert "dj_design_system.services" not in py_text
        private_methods = [
            name
            for name, value in folder_listing_module.FolderListing.__dict__.items()
            if name.startswith("_")
            and not name.startswith("__")
            and callable(value)
        ]
        assert private_methods == []


class TestFolderListingRenderingAndTemplate:
    """Verify HTML rendering via template tags, child components, and template purity."""

    def test_renders_title_cards_badges_icons_and_child_counts(self) -> None:
        """Verify full folder listing renders title, grid cards, icons, badges, and meta."""
        items = [
            {
                "label": "Elements",
                "url": "/gallery/elements/",
                "node_type": "folder",
                "children": ["a", "b"],
            },
            {
                "label": "Badge",
                "url": "/gallery/elements/badge/",
                "node_type": "component",
                "children": ["basic"],
            },
        ]
        html = _render_template(
            source='{% dds__folder_listing "Components" items %}',
            context={"items": items},
        )
        assert '<section class="dds-folder-listing" data-surface="docs">' in html
        assert "<l-stack>" in html
        assert '<h1 data-folder-title>Components</h1>' in html
        assert '<ul class="l-grid" data-folder-grid>' in html
        assert (
            '<a href="/gallery/elements/" data-folder-card data-node-kind="folder">'
            in html
        )
        assert (
            '<a href="/gallery/elements/badge/" data-folder-card data-node-kind="component">'
            in html
        )
        assert 'data-icon="folder"' in html
        assert 'data-icon="component"' in html
        assert 'data-size="md"' in html
        assert "<span data-folder-label>Elements</span>" in html
        assert "<span data-folder-label>Badge</span>" in html
        assert "<span data-folder-meta>2 items</span>" in html
        assert "<span data-folder-meta>1 item</span>" in html
        assert 'class="dds-badge"' in html
        assert "data-folder-empty" not in html
        assert 'class="dds-notice"' not in html

    def test_renders_empty_state_and_debug_hint_notice(self) -> None:
        """Verify empty folder renders fallback message and optional index.md debug notice."""
        html = _render_template(
            source=(
                '{% dds__folder_listing title="Empty" items=empty_items '
                'empty_message="Nothing here yet." show_debug_hint=True %}'
            ),
            context={"empty_items": []},
        )
        assert '<h1 data-folder-title>Empty</h1>' in html
        assert "<p data-folder-empty>Nothing here yet.</p>" in html
        assert "data-folder-grid" not in html
        assert 'class="dds-notice"' in html
        assert "Customise this folder page" in html
        assert "<code>index.md</code>" in html

    def test_omits_heading_when_title_is_empty(self) -> None:
        """Verify <h1 data-folder-title> is omitted when title is empty."""
        html = _render_template(source="{% dds__folder_listing %}")
        assert "data-folder-title" not in html
        assert "<p data-folder-empty>This folder is empty.</p>" in html

    def test_escapes_untrusted_html_in_title_labels_and_empty_message(self) -> None:
        """Verify untrusted HTML in title, item labels, and empty_message is escaped."""
        html = _render_template(
            source=(
                "{% dds__folder_listing title=title items=items "
                "empty_message=empty_message %}"
            ),
            context={
                "title": "<script>alert(1)</script>",
                "items": [{"label": "<b>Injected</b>"}],
                "empty_message": "<img src=x onerror=alert(1)>",
            },
        )
        assert "<script>" not in html
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
        assert "&lt;b&gt;Injected&lt;/b&gt;" in html

    def test_template_contains_no_filters_or_bem(self) -> None:
        """Verify folder_listing.html loads design_components and has no filters or BEM."""
        template_text = _read_text(path=FOLDER_LISTING_HTML_PATH)
        assert template_text.startswith("{% load design_components %}")
        assert "|" not in template_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=template_text,
        )
        assert not bem_matches
        assert "--" not in template_text


class TestFolderListingStylesheet:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, and formatting in folder_listing.css."""

    def test_wrapped_in_layer_blocks_and_sets_zero_margin(self) -> None:
        """Verify folder_listing.css wraps rules in @layer blocks and sets margin: 0."""
        css_text = _read_text(path=FOLDER_LISTING_CSS_PATH)
        assert css_text.startswith("@layer blocks {")
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-folder-listing",
        )
        assert root_blocks
        assert "margin: 0;" in root_blocks[0]
        assert "display: block;" in root_blocks[0]

    def test_tier_3_tokens_map_exclusively_from_defined_tier_2_tokens(self) -> None:
        """Verify all --_folder-listing-* tokens map to Tier 2 tokens defined in tokens.css."""
        css_text = _read_text(path=FOLDER_LISTING_CSS_PATH)
        tokens_text = _read_text(path=TOKENS_CSS_PATH)
        defined_tier_2 = set(
            re.findall(pattern=r"(--dds-[a-z0-9-]+)\s*:", string=tokens_text)
        )

        assert "--_dds-" not in css_text
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-folder-listing",
        )
        root_props = _extract_defined_properties(block_text="\n".join(root_blocks))
        assert root_props
        for name, value in root_props.items():
            assert name.startswith("--_folder-listing-")
            match = re.fullmatch(pattern=r"var\((--dds-[a-z0-9-]+)\)", string=value)
            assert match is not None
            assert match.group(1) in defined_tier_2

    def test_no_bem_single_quotes_and_alphabetized_declarations(self) -> None:
        """Verify zero BEM selectors, single quotes, and alphabetised declarations."""
        css_text = _read_text(path=FOLDER_LISTING_CSS_PATH)
        assert '"' not in css_text
        assert "!important" not in css_text
        assert ".dds-icon" not in css_text
        assert ".dds-badge" not in css_text
        assert ".dds-notice" not in css_text
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


class TestFolderListingGalleryAndDocs:
    """Verify co-located gallery.py and index.md for dds__folder_listing."""

    def test_gallery_config_variants_render(self) -> None:
        """Verify gallery.py exports a valid GalleryConfig whose variants all render."""
        _make_registry()
        cfg = gallery.load_gallery_config(
            source_dir=FOLDER_LISTING_DIR,
            component_name=COMPONENT_NAME,
        )
        assert isinstance(cfg, gallery.GalleryConfig)
        assert len(cfg.variants) >= 3
        for variant in cfg.variants:
            rendered = _render_template(
                source=(
                    "{% dds__folder_listing title=title items=items "
                    "empty_message=empty_message show_debug_hint=show_debug_hint %}"
                ),
                context={
                    "title": variant.kwargs.get("title", ""),
                    "items": variant.kwargs.get("items", []),
                    "empty_message": variant.kwargs.get(
                        "empty_message", "This folder is empty."
                    ),
                    "show_debug_hint": variant.kwargs.get(
                        "show_debug_hint", False
                    ),
                },
            )
            assert 'class="dds-folder-listing"' in rendered

    def test_index_md_exists_and_documents_component(self) -> None:
        """Verify index.md exists and documents dds__folder_listing and its parameters."""
        doc_text = _read_text(path=FOLDER_LISTING_INDEX_MD_PATH)
        assert "dds__folder_listing" in doc_text
        assert "title" in doc_text
        assert "items" in doc_text
        assert "empty_message" in doc_text
        assert "show_debug_hint" in doc_text
