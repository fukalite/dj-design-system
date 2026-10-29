"""Unit tests for the built-in ``dds__nav_tree`` composite component."""

import dataclasses
import pathlib
import re

import pytest
from django import template

from dj_design_system import data, gallery, types
from dj_design_system.components import base as components_base
from dj_design_system.components.gallery.composites import nav_tree as nav_tree_package
from dj_design_system.components.gallery.composites.nav_tree import (
    nav_tree as nav_tree_module,
)
from dj_design_system.services import registry as registry_service
from tests import conftest


APP_LABEL = "dj_design_system"
COMPONENT_NAME = "nav_tree"
QUALIFIED_NAME = "dds__nav_tree"
RELATIVE_PATH = "gallery.composites.nav_tree"
TEMPLATE_PATH = "dj_design_system/components/gallery/composites/nav_tree/nav_tree.html"
CSS_MEDIA_PATH = "dj_design_system/components/gallery/composites/nav_tree/nav_tree.css"
JS_MEDIA_PATH = "dj_design_system/components/gallery/composites/nav_tree/nav_tree.js"

NAV_TREE_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "components"
    / "gallery"
    / "composites"
    / "nav_tree"
)
NAV_TREE_PY_PATH = NAV_TREE_DIR / "nav_tree.py"
NAV_TREE_HTML_PATH = NAV_TREE_DIR / "nav_tree.html"
NAV_TREE_CSS_PATH = NAV_TREE_DIR / "nav_tree.css"
NAV_TREE_TS_PATH = NAV_TREE_DIR / "nav_tree.ts"
NAV_TREE_INDEX_MD_PATH = NAV_TREE_DIR / "index.md"


@dataclasses.dataclass(frozen=True)
class DuckNode:
    """Duck-typed navigation node stub for testing object attribute normalization."""

    label: str
    slug: str
    type: str = "component"
    url: str = ""
    active_path: str = ""
    base_active_path: str = ""
    icon: str | None = None
    children: tuple["DuckNode", ...] = ()
    has_index_doc: bool = False


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
    return conftest.extract_css_rule_blocks(css_text=css_text, selector=selector)


def _extract_defined_properties(block_text: str) -> dict[str, str]:
    """Extract custom property definitions from a CSS block string."""
    matches = re.findall(
        pattern=r"(--[a-z0-9_-]+)\s*:\s*([^;]+);",
        string=block_text,
    )
    return {name: value.strip() for name, value in matches}


def _make_four_level_dict_tree() -> list[dict[str, object]]:
    """Build a 4-level dictionary navigation tree covering app, folder, component, doc, and variant."""
    return [
        {
            "label": "Design System",
            "slug": "dj_design_system",
            "node_type": "app",
            "url": "/gallery/dj_design_system/",
            "active_path": "dj_design_system",
            "children": [
                {
                    "label": "Elements",
                    "slug": "elements",
                    "node_type": "folder",
                    "url": "/gallery/dj_design_system/elements/",
                    "active_path": "dj_design_system/elements",
                    "children": [
                        {
                            "label": "Button",
                            "slug": "button",
                            "node_type": "component",
                            "url": "/gallery/dj_design_system/elements/button/",
                            "active_path": "dj_design_system/elements/button",
                            "base_active_path": "dj_design_system/elements/button",
                            "children": [
                                {
                                    "label": "Primary",
                                    "slug": "primary",
                                    "node_type": "variant",
                                    "url": "/gallery/dj_design_system/elements/button/?variant=primary",
                                    "active_path": "dj_design_system/elements/button",
                                    "base_active_path": "dj_design_system/elements/button",
                                },
                                {
                                    "label": "Ghost",
                                    "slug": "ghost",
                                    "node_type": "variant",
                                    "url": "/gallery/dj_design_system/elements/button/?variant=ghost",
                                    "active_path": "dj_design_system/elements/button",
                                    "base_active_path": "dj_design_system/elements/button",
                                },
                            ],
                        },
                        {
                            "label": "Getting Started",
                            "slug": "getting_started",
                            "node_type": "document",
                            "url": "/gallery/dj_design_system/elements/getting_started/",
                            "active_path": "dj_design_system/elements/getting_started",
                        },
                    ],
                },
            ],
        },
    ]


class TestNavTreeDiscoveryAndMetadata:
    """Verify NavTree exports, metadata, media, and registry discovery."""

    def test_exported_from_package_init(self) -> None:
        """Verify NavTree and NavTreeNode are exported in dj_design_system.components.gallery.composites.nav_tree."""
        assert nav_tree_package.NavTree is nav_tree_module.NavTree
        assert nav_tree_package.NavTreeNode is nav_tree_module.NavTreeNode
        assert dataclasses.is_dataclass(nav_tree_module.NavTreeNode)
        assert nav_tree_package.__all__ == ["NavTree", "NavTreeNode"]
        assert issubclass(nav_tree_module.NavTree, components_base.TagComponent)

    def test_template_media_and_positional_args(self) -> None:
        """Verify NavTree relies on co-located template_name, Media.css/js, and positional_args."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]
        assert info.media.js == [JS_MEDIA_PATH]
        assert nav_tree_module.NavTree.get_positional_args() == ["nodes"]

    def test_discovered_as_dds_nav_tree_in_registry(self) -> None:
        """Verify ComponentRegistry discovers NavTree as internal dds__nav_tree."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.component_class is nav_tree_module.NavTree
        assert info.qualified_name == QUALIFIED_NAME
        assert info.relative_path == RELATIVE_PATH
        assert info.is_builtin is True
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]
        assert info.media.js == [JS_MEDIA_PATH]


class TestNavTreeParametersAndContext:
    """Verify parameter validation and 4-level get_context() normalization."""

    def test_default_parameters_and_empty_context(self) -> None:
        """Verify default parameters produce empty normalized_nodes and has_nodes=False."""
        comp = nav_tree_module.NavTree()
        ctx = comp.get_context()
        assert comp.nodes is None
        assert comp.active_path == ""
        assert comp.active_variant == ""
        assert ctx["aria_label"] == "Component navigation"
        assert ctx["normalized_nodes"] == []
        assert ctx["has_nodes"] is False

    def test_normalizes_four_levels_and_expands_ancestors_for_active_component(
        self,
    ) -> None:
        """Verify 4 levels normalize with depths 0..3, active state, and ancestor expansion."""
        comp = nav_tree_module.NavTree(
            nodes=_make_four_level_dict_tree(),
            active_path="/dj_design_system/elements/button/?theme=dark",
        )
        ctx = comp.get_context()
        assert ctx["has_nodes"] is True

        app_node = ctx["normalized_nodes"][0]
        assert app_node["node_kind"] == "app"
        assert app_node["depth"] == 0
        assert app_node["is_active"] is False

        folder_node = app_node["children"][0]
        assert folder_node["node_kind"] == "folder"
        assert folder_node["depth"] == 1
        assert folder_node["is_open"] is True
        assert folder_node["folder_state"] == "open"
        assert folder_node["aria_expanded"] == "true"
        assert folder_node["folder_id"] == "dj_design_system-elements"
        assert (
            folder_node["children_dom_id"]
            == "dds-nav-children-dj_design_system-elements"
        )
        assert folder_node["resolved_icon"] == "folder"

        button_node = folder_node["children"][0]
        assert button_node["node_kind"] == "folder"
        assert button_node["depth"] == 2
        assert button_node["is_active"] is True
        assert button_node["is_open"] is True
        assert button_node["resolved_icon"] == "component-variants"

        primary_node = button_node["children"][0]
        assert primary_node["node_kind"] == "leaf"
        assert primary_node["depth"] == 3
        assert primary_node["is_variant"] is True
        assert primary_node["is_active"] is False
        assert primary_node["resolved_icon"] == "variant"

        doc_node = folder_node["children"][1]
        assert doc_node["node_kind"] == "leaf"
        assert doc_node["depth"] == 2
        assert doc_node["resolved_icon"] == "doc"

    def test_active_variant_accepts_variant_instance_or_slug(self) -> None:
        """Verify active_variant matches variant nodes when passed a Variant instance or slug."""
        variant_obj = gallery.Variant(name="primary", label="Primary")
        comp = nav_tree_module.NavTree(
            nodes=_make_four_level_dict_tree(),
            active_path="dj_design_system/elements/button",
            active_variant=variant_obj,
        )
        ctx = comp.get_context()
        button_node = ctx["normalized_nodes"][0]["children"][0]["children"][0]
        primary_node = button_node["children"][0]
        ghost_node = button_node["children"][1]

        assert button_node["is_active"] is False
        assert button_node["is_open"] is True
        assert primary_node["is_active"] is True
        assert ghost_node["is_active"] is False

    def test_normalizes_navnode_and_duck_typed_objects_and_resolves_icons(
        self,
    ) -> None:
        """Verify NavNode dataclasses and duck-typed objects resolve icons and fallback URLs."""
        variant_obj = gallery.Variant(name="compact")
        nav_variant = data.NavNode(
            label="Compact",
            slug="compact",
            node_type=types.NodeType.VARIANT,
            variant=variant_obj,
            icon="eye",
            url="/gallery/app/comp/?variant=compact",
            active_path="app/comp",
            base_active_path="app/comp",
        )
        folder_nav = data.NavNode(
            label="Widgets",
            slug="widgets",
            node_type=types.NodeType.FOLDER,
            children=[nav_variant],
            url="/gallery/app/widgets/",
            active_path="app/widgets",
        )
        duck_doc = DuckNode(
            label="Overview",
            slug="overview",
            type="custom",
            has_index_doc=True,
        )
        duck_custom_icon = DuckNode(
            label="Search",
            slug="search",
            type="component",
            icon="not-a-valid-icon",
        )

        comp = nav_tree_module.NavTree(
            nodes=[folder_nav, duck_doc, duck_custom_icon],
            active_path="app/comp",
            active_variant="compact",
        )
        ctx = comp.get_context()
        nodes = ctx["normalized_nodes"]

        assert nodes[0]["node_kind"] == "folder"
        assert nodes[0]["is_open"] is True
        assert nodes[0]["children"][0]["resolved_icon"] == "eye"
        assert nodes[0]["children"][0]["is_active"] is True

        assert nodes[1]["url"] == "#"
        assert nodes[1]["resolved_icon"] == "doc"

        assert nodes[2]["resolved_icon"] == "component"

    def test_component_with_only_document_children_has_variants_false_and_component_icon(
        self,
    ) -> None:
        """Verify a component whose only child is a document gets has_variants=False and resolved_icon='component'."""
        doc_node = data.NavNode(
            label="Overview",
            slug="overview",
            node_type=types.NodeType.DOCUMENT,
            doc_path=pathlib.Path("overview.md"),
        )
        comp_node = data.NavNode(
            label="Button",
            slug="button",
            node_type=types.NodeType.COMPONENT,
            component=conftest.make_info("button"),
            children=[doc_node],
            url="/gallery/app/button/",
            active_path="app/button",
        )
        assert comp_node.has_variants is False

        parsed = nav_tree_module.NavTreeNode.from_raw(comp_node)
        assert parsed.has_variants is False

        tree = [comp_node]
        comp = nav_tree_module.NavTree(nodes=tree)
        ctx = comp.get_context()
        normalized = ctx["normalized_nodes"][0]

        assert normalized["resolved_icon"] == "component"
        assert normalized["node_kind"] == "folder"

        html = comp.render()
        assert 'data-icon="component-variants"' not in html
        assert 'data-icon="component"' in html

        from dj_design_system.services.navigation import normalize_folder_items

        folder_items = normalize_folder_items(items=[comp_node])
        assert folder_items[0]["icon"] == "component"
        assert folder_items[0]["node_kind"] == "component"

    def test_invalid_nodes_type_raises_type_error(self) -> None:
        """Verify passing a non-list to nodes raises TypeError."""
        with pytest.raises(expected_exception=TypeError, match="Expected list"):
            nav_tree_module.NavTree(nodes="invalid")

    def test_python_module_contains_no_private_methods_or_html_building(
        self,
    ) -> None:
        """Verify nav_tree.py has no private helper methods, nested defs, NavItemInputData coupling, or HTML building."""
        py_text = _read_text(path=NAV_TREE_PY_PATH)
        assert "format_html" not in py_text
        assert "mark_safe" not in py_text
        assert "Icon(" not in py_text
        assert "NavItemInputData" not in py_text
        private_defs = re.findall(
            pattern=r"def _(?![_a-z]+__)[a-z0-9_]+", string=py_text
        )
        assert not private_defs


class TestNavTreeRenderingAndTemplate:
    """Verify HTML rendering via template tags, attributes, and template purity."""

    def test_renders_root_custom_element_and_nav_landmark(self) -> None:
        """Verify <dds-nav-tree class='dds-nav-tree'> wraps <nav class='dds-nav-tree-nav'>."""
        html = _render_template(
            source='{% dds__nav_tree nodes active_path="dj_design_system/elements/button" %}',
            context={"nodes": _make_four_level_dict_tree()},
        )
        assert '<dds-nav-tree class="dds-nav-tree"' in html
        assert (
            '<nav class="dds-nav-tree-nav" aria-label="Component navigation">' in html
        )
        assert "<div data-nav-group>" in html
        assert (
            '<div data-nav-folder data-state="open" '
            'data-folder-id="dj_design_system-elements">' in html
        )
        assert (
            '<a href="/gallery/dj_design_system/elements/button/" '
            'data-nav-link data-depth="2" aria-current="page" data-active="true">'
            in html
        )
        assert (
            '<button type="button" data-nav-toggle aria-expanded="true" '
            'aria-controls="dds-nav-children-dj_design_system-elements" '
            'aria-label="Toggle Elements">' in html
        )
        assert (
            '<div id="dds-nav-children-dj_design_system-elements" data-nav-children>'
            in html
        )
        assert 'data-variant-link="true"' in html
        assert 'data-icon="chevron-right"' in html

    def test_renders_closed_folder_with_hidden_children(self) -> None:
        """Verify closed folders render data-state='closed', aria-expanded='false', and hidden."""
        html = _render_template(
            source="{% dds__nav_tree nodes=nodes %}",
            context={"nodes": _make_four_level_dict_tree()},
        )
        assert (
            '<div data-nav-folder data-state="closed" '
            'data-folder-id="dj_design_system-elements">' in html
        )
        assert 'aria-expanded="false"' in html
        assert (
            '<div id="dds-nav-children-dj_design_system-elements" '
            "data-nav-children hidden>" in html
        )

    def test_escapes_untrusted_labels_and_aria_label(self) -> None:
        """Verify untrusted HTML in node labels and aria_label is escaped."""
        html = _render_template(
            source="{% dds__nav_tree nodes=nodes aria_label=label %}",
            context={
                "nodes": [{"label": "<script>alert(1)</script>", "slug": "xss"}],
                "label": 'Sidebar "unsafe"',
            },
        )
        assert "<script>" not in html
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
        assert "Sidebar &quot;unsafe&quot;" in html

    def test_template_contains_no_filters_no_legacy_tags_and_no_bem(self) -> None:
        """Verify nav_tree.html loads only design_components and has zero filters or BEM."""
        template_text = _read_text(path=NAV_TREE_HTML_PATH)
        assert template_text.startswith("{% load design_components %}")
        assert "dj_design_system_gallery" not in template_text
        assert "|" not in template_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=template_text,
        )
        assert not bem_matches

    def test_renders_arbitrary_depth_beyond_four_levels(self) -> None:
        """Verify nested folders, components, and variants at depth >= 4 render without truncation."""
        deep_tree = [
            {
                "label": "Consumer App",
                "slug": "consumer",
                "node_type": "app",
                "url": "/gallery/consumer/",
                "active_path": "consumer",
                "children": [
                    {
                        "label": "Forms",
                        "slug": "forms",
                        "node_type": "folder",
                        "url": "/gallery/consumer/forms/",
                        "active_path": "consumer/forms",
                        "children": [
                            {
                                "label": "Inputs",
                                "slug": "inputs",
                                "node_type": "folder",
                                "url": "/gallery/consumer/forms/inputs/",
                                "active_path": "consumer/forms/inputs",
                                "children": [
                                    {
                                        "label": "Date Picker",
                                        "slug": "date_picker",
                                        "node_type": "component",
                                        "url": "/gallery/consumer/forms/inputs/date_picker/",
                                        "active_path": "consumer/forms/inputs/date_picker",
                                        "base_active_path": "consumer/forms/inputs/date_picker",
                                        "children": [
                                            {
                                                "label": "Range",
                                                "slug": "range",
                                                "node_type": "variant",
                                                "url": "/gallery/consumer/forms/inputs/date_picker/?variant=range",
                                                "active_path": "consumer/forms/inputs/date_picker",
                                                "base_active_path": "consumer/forms/inputs/date_picker",
                                            },
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
        ]
        html = _render_template(
            source='{% dds__nav_tree nodes active_path="consumer/forms/inputs/date_picker" active_variant="range" %}',
            context={"nodes": deep_tree},
        )
        assert 'data-depth="4"' in html
        assert "<span>Range</span>" in html
        assert 'data-variant-link="true"' in html


class TestNavTreeStylesheet:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, and formatting in nav_tree.css."""

    def test_wrapped_in_layer_blocks_and_sets_block_display_and_zero_margin(
        self,
    ) -> None:
        """Verify nav_tree.css wraps rules in @layer blocks and sets display: block; margin: 0."""
        css_text = _read_text(path=NAV_TREE_CSS_PATH)
        assert css_text.startswith("@layer blocks {")
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector="dds-nav-tree,\n  .dds-nav-tree",
        )
        assert root_blocks
        assert "display: block;" in root_blocks[0]
        assert "margin: 0;" in root_blocks[0]

    def test_tier_3_tokens_map_exclusively_from_tier_2_tokens(self) -> None:
        """Verify all --_nav-tree-* tokens map exclusively from Tier 2 --dds-* tokens."""
        css_text = _read_text(path=NAV_TREE_CSS_PATH)
        assert "--_dds-" not in css_text
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector="dds-nav-tree,\n  .dds-nav-tree",
        )
        root_props = _extract_defined_properties(block_text="\n".join(root_blocks))
        assert root_props
        for name, value in root_props.items():
            assert name.startswith("--_nav-tree-")
            assert value.startswith("var(--dds-")

        for required_domain in (
            "var(--dds-control-",
            "var(--dds-state-",
            "var(--dds-text-",
            "var(--dds-space-",
        ):
            assert required_domain in css_text

        assert "--_nav-tree-active-border-color" not in css_text

    def test_css_boundary_encapsulation(self) -> None:
        """Verify child component selectors do not leak into nav_tree.css and nesting is native."""
        css_text = _read_text(path=NAV_TREE_CSS_PATH)
        assert ".dds-icon" not in css_text
        assert "& [data-nav-group]" in css_text
        assert "& [data-nav-link]" in css_text
        assert "dds-nav-tree [" not in css_text

    def test_sidebar_scroll_container_padding_at_panel_edge(self) -> None:
        """Verify sidebar body sets padding: 0; and delegates padding to child nav."""
        sidebar_css_path = (
            pathlib.Path(__file__).resolve().parent.parent.parent
            / "dj_design_system"
            / "static"
            / "dj_design_system"
            / "areas"
            / "sidebar.css"
        )
        css_text = _read_text(path=sidebar_css_path)
        body_rule_index = css_text.find("& [data-sidebar-body] {")
        footer_rule_index = css_text.find("& [data-sidebar-footer] {")
        assert body_rule_index != -1
        assert footer_rule_index > body_rule_index
        body_block = css_text[body_rule_index:footer_rule_index]
        assert "padding: 0;" in body_block
        assert "& nav {" in body_block
        assert "padding-block: var(--_sidebar-padding-block);" in body_block
        assert "padding-inline: var(--_sidebar-padding-inline);" in body_block


class TestNavTreeGalleryAndDocs:
    """Verify co-located gallery.py and index.md for dds__nav_tree."""

    def test_gallery_config_variants_render(self) -> None:
        """Verify gallery.py exports a valid GalleryConfig whose variants all render."""
        _make_registry()
        cfg = gallery.load_gallery_config(
            source_dir=NAV_TREE_DIR,
            component_name=COMPONENT_NAME,
        )
        assert isinstance(cfg, gallery.GalleryConfig)
        assert len(cfg.variants) == 1
        for variant in cfg.variants:
            direct_html = nav_tree_module.NavTree(**variant.kwargs).render()
            assert 'class="dds-nav-tree"' in direct_html
            rendered = _render_template(
                source=(
                    "{% dds__nav_tree nodes=nodes active_path=active_path "
                    "active_variant=active_variant aria_label=aria_label %}"
                ),
                context={
                    "nodes": variant.kwargs.get("nodes", []),
                    "active_path": variant.kwargs.get("active_path", ""),
                    "active_variant": variant.kwargs.get("active_variant", ""),
                    "aria_label": variant.kwargs.get(
                        "aria_label", "Component navigation"
                    ),
                },
            )
            assert 'class="dds-nav-tree"' in rendered

    def test_index_md_exists_and_documents_component(self) -> None:
        """Verify index.md exists and documents <dds-nav-tree> behaviour and accessibility."""
        doc_text = _read_text(path=NAV_TREE_INDEX_MD_PATH)
        assert "<dds-nav-tree" in doc_text
        assert "Behaviour & Accessibility" in doc_text
        assert "aria-current" in doc_text
