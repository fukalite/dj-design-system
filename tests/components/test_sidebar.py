"""Unit tests for the built-in ``dds__sidebar`` domain component."""

import pathlib
import re

import pytest
from django import template
from django.utils import safestring

from dj_design_system import data, gallery
from dj_design_system.components import base as components_base
from dj_design_system.components.domain import sidebar as sidebar_package
from dj_design_system.components.domain.sidebar import sidebar as sidebar_module
from dj_design_system.services import canvas as canvas_service
from dj_design_system.services import registry as registry_service
from dj_design_system.services import slot_node
from tests import conftest


APP_LABEL = "dj_design_system"
COMPONENT_NAME = "sidebar"
QUALIFIED_NAME = "dds__sidebar"
RELATIVE_PATH = "domain.sidebar"
TEMPLATE_PATH = "dj_design_system/components/domain/sidebar/sidebar.html"
CSS_MEDIA_PATH = "dj_design_system/components/domain/sidebar/sidebar.css"

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
SIDEBAR_DIR = ROOT_DIR / "dj_design_system" / "components" / "domain" / "sidebar"
SIDEBAR_PY_PATH = SIDEBAR_DIR / "sidebar.py"
SIDEBAR_HTML_PATH = SIDEBAR_DIR / "sidebar.html"
SIDEBAR_CSS_PATH = SIDEBAR_DIR / "sidebar.css"
SIDEBAR_GALLERY_PATH = SIDEBAR_DIR / "gallery.py"
SIDEBAR_INDEX_MD_PATH = SIDEBAR_DIR / "index.md"
TOKENS_CSS_PATH = (
    ROOT_DIR / "dj_design_system" / "static" / "dj_design_system" / "tokens.css"
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


def _render_template(
    source: str,
    context_data: dict[str, object] | None = None,
) -> str:
    """Render a Django template string with built-in dds component and slot tags."""
    reg = _make_registry()
    engine = template.engines["django"].engine
    lib = template.Library()
    reg.register_templatetags(library=lib)
    lib.tag(name="slot", compile_function=slot_node.do_slot)
    previous = engine.template_libraries.get("design_components")
    engine.template_libraries["design_components"] = lib
    try:
        compiled = template.Template(
            template_string="{% load design_components %}" + source
        )
        return compiled.render(context=template.Context(dict_=context_data or {}))
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
    """Extract property definitions from a CSS block string."""
    matches = re.findall(
        pattern=r"([a-zA-Z0-9_-]+)\s*:\s*([^;]+);",
        string=block_text,
    )
    return {name: value.strip() for name, value in matches}


def _make_sample_nodes() -> list[dict[str, object]]:
    """Build sample navigation nodes for sidebar rendering tests."""
    return [
        {
            "label": "Design System",
            "slug": "dj_design_system",
            "node_type": "app",
            "url": "/gallery/dj_design_system/",
            "active_path": "dj_design_system",
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
                    ],
                },
            ],
        },
    ]


class TestSidebarDiscoveryAndMetadata:
    """Verify Sidebar exports, metadata, media, slots, and registry discovery."""

    def test_exported_from_package_init_and_subclasses_block_component(self) -> None:
        """Verify Sidebar is exported in dj_design_system.components.domain.sidebar."""
        assert sidebar_package.Sidebar is sidebar_module.Sidebar
        assert issubclass(sidebar_module.Sidebar, components_base.BlockComponent)
        assert sidebar_module.Sidebar.has_slots() is True

    def test_template_media_and_slots_metadata(self) -> None:
        """Verify Sidebar relies on co-located template_name, Media.css, and header/footer slots."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]
        slots_spec = sidebar_module.Sidebar.get_slots()
        assert set(slots_spec.keys()) == {"header", "footer"}
        assert slots_spec["header"].required is False
        assert slots_spec["footer"].required is False

    def test_discovered_as_dds_sidebar_in_registry(self) -> None:
        """Verify ComponentRegistry discovers Sidebar as internal dds__sidebar."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.component_class is sidebar_module.Sidebar
        assert info.qualified_name == QUALIFIED_NAME
        assert info.relative_path == RELATIVE_PATH
        assert info.is_internal is True
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]
        assert info.media.js == []


class TestSidebarParametersAndContext:
    """Verify parameter validation, active_variant normalization, and get_context()."""

    def test_default_parameters_and_context(self) -> None:
        """Verify default parameters produce expected normalized context flags."""
        comp = sidebar_module.Sidebar()
        ctx = comp.get_context()
        assert comp.nodes is None
        assert comp.search_index is None
        assert ctx["brand_name"] == "Design System"
        assert ctx["brand_url"] == "/"
        assert ctx["aria_label"] == "Gallery sidebar"
        assert ctx["nodes"] == []
        assert ctx["active_path"] == ""
        assert ctx["active_variant"] == ""
        assert ctx["search_index"] == []
        assert ctx["show_search"] is False
        assert ctx["has_header_slot"] is False
        assert ctx["has_footer_slot"] is False
        assert ctx["has_content"] is False
        assert ctx["slots"] == {"header": "", "footer": ""}
        assert ctx["content"] == ""

    def test_normalizes_variant_instance_and_slots_and_content(self) -> None:
        """Verify Variant instance normalization in __init__ and slot/content flags in get_context()."""
        variant_obj = gallery.Variant(name="primary", label="Primary")
        comp = sidebar_module.Sidebar(
            content="<p>Extra sidebar note</p>",
            slots={
                "header": safestring.SafeString("<h2>Custom Brand</h2>"),
                "footer": safestring.SafeString("<small>v2.0</small>"),
            },
            brand_name="",
            brand_url="",
            aria_label="",
            nodes=_make_sample_nodes(),
            active_path="dj_design_system/elements/button",
            active_variant=variant_obj,
            search_index=[{"label": "Button", "url": "/button/"}],
            show_search=True,
        )
        assert comp.active_variant == "primary"
        assert isinstance(comp.content, safestring.SafeString)
        assert isinstance(comp.slots["header"], safestring.SafeString)
        assert isinstance(comp.slots["footer"], safestring.SafeString)

        ctx = comp.get_context()
        assert ctx["brand_name"] == "Design System"
        assert ctx["brand_url"] == "/"
        assert ctx["aria_label"] == "Gallery sidebar"
        assert len(ctx["nodes"]) == 1
        assert len(ctx["search_index"]) == 1
        assert ctx["active_variant"] == "primary"
        assert ctx["show_search"] is True
        assert ctx["has_header_slot"] is True
        assert ctx["has_footer_slot"] is True
        assert ctx["has_content"] is True

    def test_whitespace_only_content_sets_has_content_false(self) -> None:
        """Verify whitespace-only content sets has_content=False."""
        comp = sidebar_module.Sidebar(content="   \n  ")
        ctx = comp.get_context()
        assert ctx["has_content"] is False

    def test_invalid_parameter_types_raise_type_error(self) -> None:
        """Verify passing non-list nodes or search_index raises TypeError."""
        with pytest.raises(expected_exception=TypeError, match="Expected list"):
            sidebar_module.Sidebar(nodes="invalid")
        with pytest.raises(expected_exception=TypeError, match="Expected list"):
            sidebar_module.Sidebar(search_index="invalid")

    def test_python_module_contains_no_private_methods_or_mark_safe(self) -> None:
        """Verify sidebar.py has no private helper methods, format_html, or mark_safe."""
        py_text = _read_text(path=SIDEBAR_PY_PATH)
        assert "format_html" not in py_text
        assert "mark_safe" not in py_text
        private_defs = re.findall(
            pattern=r"def _(?![_a-z]+__)[a-z0-9_]+",
            string=py_text,
        )
        assert not private_defs


class TestSidebarRenderingAndTemplate:
    """Verify HTML rendering via template tags, child components, slots, and escaping."""

    def test_renders_default_sidebar_with_brand_and_nav_tree(self) -> None:
        """Verify default sidebar renders <aside>, brand link, and dds__nav_tree without search or footer."""
        html = _render_template(
            source=(
                '{% dds__sidebar brand_name="Acme DS" brand_url="/acme/" '
                'nodes=nodes active_path="dj_design_system/elements/button" %}'
                "{% enddds__sidebar %}"
            ),
            context_data={"nodes": _make_sample_nodes()},
        )
        assert (
            '<aside class="dds-sidebar" data-surface="sidebar" '
            'aria-label="Gallery sidebar">' in html
        )
        assert "<div data-sidebar-header>" in html
        assert '<a href="/acme/" data-sidebar-brand>Acme DS</a>' in html
        assert "data-sidebar-search" not in html
        assert "<div data-sidebar-body>" in html
        assert '<dds-nav-tree class="dds-nav-tree">' in html
        assert 'aria-current="page" data-active="true"' in html
        assert "data-sidebar-footer" not in html

    def test_renders_search_box_when_show_search_is_true(self) -> None:
        """Verify show_search=True renders <div data-sidebar-search> with dds__search_box."""
        html = _render_template(
            source=(
                "{% dds__sidebar nodes=nodes show_search=True "
                "search_index=search_index %}"
                "{% enddds__sidebar %}"
            ),
            context_data={
                "nodes": _make_sample_nodes(),
                "search_index": [
                    {
                        "label": "Button",
                        "url": "/gallery/dj_design_system/elements/button/",
                        "type": "component",
                    },
                ],
            },
        )
        assert "<div data-sidebar-search>" in html
        assert '<dds-search-box class="dds-search-box"' in html
        assert "/gallery/dj_design_system/elements/button/" in html

    def test_renders_custom_header_and_footer_slots_and_direct_content(self) -> None:
        """Verify header and footer slots replace brand link and append footer section."""
        slot_html = _render_template(
            source=(
                '{% dds__sidebar aria_label="Custom sidebar" %}'
                '{% slot "header" %}<span class="custom-header">Header</span>{% endslot %}'
                '{% slot "footer" %}<span class="custom-footer">Footer</span>{% endslot %}'
                "{% enddds__sidebar %}"
            ),
        )
        assert 'aria-label="Custom sidebar"' in slot_html
        assert '<span class="custom-header">Header</span>' in slot_html
        assert "data-sidebar-brand" not in slot_html
        assert "<div data-sidebar-footer>" in slot_html
        assert '<span class="custom-footer">Footer</span>' in slot_html

        _make_registry()
        direct_html = sidebar_module.Sidebar(
            content=safestring.SafeString("<div data-extra-body>Extra body</div>"),
            nodes=_make_sample_nodes(),
        ).render()
        assert "<div data-extra-body>Extra body</div>" in direct_html

    def test_escapes_untrusted_brand_and_aria_label(self) -> None:
        """Verify untrusted strings in brand_name, brand_url, and aria_label are HTML-escaped."""
        html = _render_template(
            source=(
                "{% dds__sidebar brand_name=brand_name brand_url=brand_url "
                "aria_label=aria_label %}"
                "{% enddds__sidebar %}"
            ),
            context_data={
                "brand_name": "<script>alert(1)</script>",
                "brand_url": '"/onload="evil()',
                "aria_label": 'Sidebar "unsafe"',
            },
        )
        assert "<script>alert(1)</script>" not in html
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
        assert "Sidebar &quot;unsafe&quot;" in html

    def test_template_contains_no_filters_and_no_bem(self) -> None:
        """Verify sidebar.html loads design_components and has zero filters or BEM."""
        template_text = _read_text(path=SIDEBAR_HTML_PATH)
        assert template_text.startswith("{% load design_components %}")
        assert "|" not in template_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=template_text,
        )
        assert not bem_matches


class TestSidebarStylesheet:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, and formatting in sidebar.css."""

    def test_wrapped_in_layer_blocks_and_sets_flex_column_and_zero_margin(self) -> None:
        """Verify sidebar.css wraps rules in @layer blocks and sets margin: 0; display: flex; flex-direction: column."""
        css_text = _read_text(path=SIDEBAR_CSS_PATH)
        assert css_text.startswith("@layer blocks {")
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-sidebar",
        )
        assert root_blocks
        props = _extract_defined_properties(block_text=root_blocks[0])
        assert props.get("margin") == "0"
        assert props.get("display") == "flex"
        assert props.get("flex-direction") == "column"

    def test_tier_3_tokens_map_exclusively_from_tier_2_tokens_in_tokens_css(
        self,
    ) -> None:
        """Verify all --_sidebar-* tokens map exclusively from Tier 2 --dds-* tokens defined in tokens.css."""
        css_text = _read_text(path=SIDEBAR_CSS_PATH)
        tokens_text = _read_text(path=TOKENS_CSS_PATH)
        assert "--_dds-" not in css_text

        defined_tier_2_tokens = set(
            re.findall(pattern=r"(--dds-[a-z0-9-]+)\s*:", string=tokens_text)
        )
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-sidebar",
        )
        root_props = _extract_defined_properties(block_text="\n".join(root_blocks))
        tier_3_props = {
            name: value
            for name, value in root_props.items()
            if name.startswith("--_")
        }
        assert tier_3_props
        for name, value in tier_3_props.items():
            assert name.startswith("--_sidebar-")
            match = re.fullmatch(pattern=r"var\((--dds-[a-z0-9-]+)\)", string=value)
            assert match is not None
            assert match.group(1) in defined_tier_2_tokens

    def test_no_bem_single_quotes_and_alphabetized_declarations(self) -> None:
        """Verify zero BEM selectors, single quotes, and alphabetised declarations."""
        css_text = _read_text(path=SIDEBAR_CSS_PATH)
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


class TestSidebarGalleryAndDocs:
    """Verify co-located gallery.py and index.md for dds__sidebar."""

    def test_gallery_config_variants_render(self) -> None:
        """Verify gallery.py exports a valid GalleryConfig whose variants all render."""
        assert SIDEBAR_GALLERY_PATH.is_file()
        reg = _make_registry()
        cfg = gallery.load_gallery_config(
            source_dir=SIDEBAR_DIR,
            component_name=COMPONENT_NAME,
        )
        assert isinstance(cfg, gallery.GalleryConfig)
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
            assert '<aside class="dds-sidebar" data-surface="sidebar"' in rendered

    def test_index_md_exists_and_documents_component(self) -> None:
        """Verify index.md exists and documents dds__sidebar, its parameters, and slots."""
        assert SIDEBAR_INDEX_MD_PATH.is_file()
        doc_text = _read_text(path=SIDEBAR_INDEX_MD_PATH)
        assert "dds__sidebar" in doc_text
        for documented_item in (
            "brand_name",
            "brand_url",
            "nodes",
            "active_path",
            "active_variant",
            "search_index",
            "show_search",
            "aria_label",
            "header",
            "footer",
        ):
            assert documented_item in doc_text
