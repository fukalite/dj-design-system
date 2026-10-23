"""Unit tests for the built-in ``dds__toolbar`` domain component."""

import pathlib
import re

import pytest
from django import template
from django.utils import safestring

from dj_design_system import data, gallery
from dj_design_system.components import base as components_base
from dj_design_system.components.domain import toolbar as toolbar_package
from dj_design_system.components.domain.toolbar import toolbar as toolbar_module
from dj_design_system.services import canvas as canvas_service
from dj_design_system.services import registry as registry_service
from dj_design_system.services import slot_node
from tests import conftest


APP_LABEL = "dj_design_system"
COMPONENT_NAME = "toolbar"
QUALIFIED_NAME = "dds__toolbar"
RELATIVE_PATH = "domain.toolbar"
TEMPLATE_PATH = "dj_design_system/components/domain/toolbar/toolbar.html"
CSS_MEDIA_PATH = "dj_design_system/components/domain/toolbar/toolbar.css"

TOOLBAR_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "components"
    / "domain"
    / "toolbar"
)
TOOLBAR_PY_PATH = TOOLBAR_DIR / "toolbar.py"
TOOLBAR_HTML_PATH = TOOLBAR_DIR / "toolbar.html"
TOOLBAR_CSS_PATH = TOOLBAR_DIR / "toolbar.css"
TOOLBAR_INDEX_MD_PATH = TOOLBAR_DIR / "index.md"


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
    lib.tag(name="slot", compile_function=slot_node.do_slot)
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


class TestToolbarDiscoveryAndMetadata:
    """Verify Toolbar class exports, metadata, media, and registry discovery."""

    def test_exported_from_package_init(self) -> None:
        """Verify Toolbar is exported in dj_design_system.components.domain.toolbar."""
        assert toolbar_package.Toolbar is toolbar_module.Toolbar
        assert issubclass(toolbar_module.Toolbar, components_base.BlockComponent)

    def test_template_meta_slots_and_media_declarations(self) -> None:
        """Verify Toolbar declares co-located template_name, slots, and Media.css."""
        assert toolbar_module.Toolbar.template_name == TEMPLATE_PATH
        assert toolbar_module.Toolbar.has_slots() is True
        slot_defs = toolbar_module.Toolbar.get_slots()
        assert set(slot_defs.keys()) == {"leading", "actions"}
        assert slot_defs["leading"].required is False
        assert slot_defs["actions"].required is False
        assert toolbar_module.Toolbar.Media.css == CSS_MEDIA_PATH

    def test_discovered_as_dds_toolbar_in_registry(self) -> None:
        """Verify ComponentRegistry discovers Toolbar as internal dds__toolbar."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.component_class is toolbar_module.Toolbar
        assert info.qualified_name == QUALIFIED_NAME
        assert info.relative_path == RELATIVE_PATH
        assert info.is_internal is True
        assert info.media.css == [CSS_MEDIA_PATH]

    def test_no_private_helper_methods_or_mark_safe_in_component(self) -> None:
        """Verify Toolbar defines no private _-prefixed helper methods and avoids mark_safe."""
        own_private_methods = [
            name
            for name, attr in toolbar_module.Toolbar.__dict__.items()
            if name.startswith("_") and not name.startswith("__") and callable(attr)
        ]
        assert not own_private_methods
        py_text = _read_text(path=TOOLBAR_PY_PATH)
        assert "mark_safe" not in py_text


class TestToolbarParametersAndContext:
    """Verify Toolbar parameter defaults, validation, and get_context() shaping."""

    def test_default_parameters_and_context_flags(self) -> None:
        """Verify defaults when instantiated without arguments."""
        comp = toolbar_module.Toolbar()
        ctx = comp.get_context()
        assert ctx["brand_name"] == "Design System"
        assert ctx["brand_url"] == "/"
        assert ctx["breadcrumbs"] == []
        assert ctx["themes"] == []
        assert ctx["search_index"] == []
        assert ctx["active_theme"] == "light"
        assert ctx["show_search"] is True
        assert ctx["show_menu_toggle"] is True
        assert ctx["has_breadcrumbs"] is False
        assert ctx["has_themes"] is False
        assert ctx["has_leading_slot"] is False
        assert ctx["has_actions_slot"] is False
        assert ctx["has_content"] is False
        assert ctx["content"] == ""

    def test_custom_parameters_slots_and_content_shaping(self) -> None:
        """Verify get_context() shapes lists, slots, and content with SafeString wrapping."""
        breadcrumbs = [{"label": "Domain", "url": "/domain/"}, {"label": "Toolbar"}]
        themes = [{"value": "light", "label": "Light"}, {"value": "dark", "label": "Dark"}]
        search_index = [{"label": "Button", "url": "/button/"}]
        comp = toolbar_module.Toolbar(
            content="<span>Extra</span>",
            slots={
                "leading": safestring.SafeString("<span>Custom Leading</span>"),
                "actions": safestring.SafeString("<button>Action</button>"),
            },
            brand_name="Acme DS",
            brand_url="/acme/",
            breadcrumbs=breadcrumbs,
            themes=themes,
            active_theme="dark",
            search_index=search_index,
            show_search=False,
            show_menu_toggle=False,
        )
        assert isinstance(comp.content, safestring.SafeString)
        assert isinstance(comp.slots["leading"], safestring.SafeString)
        assert isinstance(comp.slots["actions"], safestring.SafeString)

        ctx = comp.get_context()
        assert ctx["brand_name"] == "Acme DS"
        assert ctx["brand_url"] == "/acme/"
        assert ctx["breadcrumbs"] == breadcrumbs
        assert ctx["themes"] == themes
        assert ctx["search_index"] == search_index
        assert ctx["active_theme"] == "dark"
        assert ctx["show_search"] is False
        assert ctx["show_menu_toggle"] is False
        assert ctx["has_breadcrumbs"] is True
        assert ctx["has_themes"] is True
        assert ctx["has_leading_slot"] is True
        assert ctx["has_actions_slot"] is True
        assert ctx["has_content"] is True

    def test_whitespace_only_content_sets_has_content_false(self) -> None:
        """Verify whitespace-only block content sets has_content to False."""
        comp = toolbar_module.Toolbar(content="   \n  ")
        ctx = comp.get_context()
        assert ctx["has_content"] is False

    def test_empty_strings_fall_back_to_defaults(self) -> None:
        """Verify empty brand_name, brand_url, and active_theme fall back to defaults."""
        comp = toolbar_module.Toolbar(
            brand_name="",
            brand_url="",
            active_theme="",
        )
        ctx = comp.get_context()
        assert ctx["brand_name"] == "Design System"
        assert ctx["brand_url"] == "/"
        assert ctx["active_theme"] == "light"

    def test_invalid_list_parameter_raises_type_error(self) -> None:
        """Verify passing a non-list to breadcrumbs, themes, or search_index raises TypeError."""
        with pytest.raises(expected_exception=TypeError, match="Expected list"):
            toolbar_module.Toolbar(breadcrumbs="invalid")


class TestToolbarRenderingAndTemplate:
    """Verify template tag rendering, child component delegation, slots, and template purity."""

    def test_renders_default_toolbar_structure(self) -> None:
        """Verify default {% dds__toolbar %} renders header, menu toggle, brand, and search box."""
        html = _render_template(
            source="{% dds__toolbar %}{% enddds__toolbar %}",
        ).strip()
        assert '<header class="dds-toolbar" data-surface="topbar">' in html
        assert "<l-cluster data-toolbar-inner>" in html
        assert "<l-cluster data-toolbar-leading>" in html
        assert "<l-cluster data-toolbar-actions>" in html
        assert 'data-action="toggle-drawer"' in html
        assert 'aria-label="Toggle navigation"' in html
        assert '<a href="/" data-toolbar-brand>Design System</a>' in html
        assert '<dds-search-box class="dds-search-box"' in html
        assert "data-toolbar-breadcrumb" not in html
        assert "<dds-theme-select" not in html

    def test_renders_breadcrumbs_themes_and_search_index(self) -> None:
        """Verify breadcrumbs, themes, and search_index delegate to child dds components."""
        breadcrumbs = [
            {"label": "Domain", "url": "/domain/"},
            {"label": "Toolbar", "url": "/domain/toolbar/"},
        ]
        themes = [
            {"value": "light", "label": "Light"},
            {"value": "dark", "label": "Dark"},
        ]
        search_index = [
            {"label": "Button", "url": "/button/", "type": "component"},
        ]
        html = _render_template(
            source=(
                '{% dds__toolbar brand_name="Acme" brand_url="/ds/" '
                "breadcrumbs=breadcrumbs themes=themes "
                'active_theme="dark" search_index=search_index %}'
                "{% enddds__toolbar %}"
            ),
            context={
                "breadcrumbs": breadcrumbs,
                "themes": themes,
                "search_index": search_index,
            },
        ).strip()
        assert '<a href="/ds/" data-toolbar-brand>Acme</a>' in html
        assert "<div data-toolbar-breadcrumb>" in html
        assert '<nav class="dds-breadcrumb"' in html
        assert '<a href="/domain/">' in html
        assert '<span aria-current="page">' in html
        assert '<dds-theme-select class="dds-theme-select" data-active-theme="dark">' in html
        assert "Button" in html

    def test_leading_slot_overrides_breadcrumbs_and_actions_slot_renders(self) -> None:
        """Verify leading slot overrides breadcrumbs and actions/content render in actions cluster."""
        breadcrumbs = [{"label": "Ignored", "url": "/ignored/"}]
        html = _render_template(
            source=(
                "{% dds__toolbar breadcrumbs=breadcrumbs "
                "show_search=False show_menu_toggle=False %}"
                '{% slot "leading" %}<span data-custom-leading>Custom Trail</span>{% endslot %}'
                '{% slot "actions" %}<button type="button" data-custom-action>Act</button>{% endslot %}'
                "{% enddds__toolbar %}"
            ),
            context={"breadcrumbs": breadcrumbs},
        ).strip()
        assert "toggle-drawer" not in html
        assert "<dds-search-box" not in html
        assert '<div data-toolbar-breadcrumb><span data-custom-leading>Custom Trail</span></div>' in html
        assert "Ignored" not in html
        assert '<button type="button" data-custom-action>Act</button>' in html

        direct_html = toolbar_module.Toolbar(
            content="<span data-extra-content>Trailing</span>",
            show_search=False,
            show_menu_toggle=False,
        ).render()
        assert "<span data-extra-content>Trailing</span>" in direct_html

    def test_template_contains_no_filters_or_bem(self) -> None:
        """Verify toolbar.html loads design_components and has zero template filters or BEM classes."""
        template_text = _read_text(path=TOOLBAR_HTML_PATH)
        assert "{% load design_components %}" in template_text
        assert "|" not in template_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=template_text,
        )
        assert not bem_matches


class TestToolbarStylesheet:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, and formatting in toolbar.css."""

    def test_wrapped_in_layer_blocks_and_sets_root_layout(self) -> None:
        """Verify toolbar.css wraps rules in @layer blocks and sets block display and zero margin."""
        css_text = _read_text(path=TOOLBAR_CSS_PATH)
        assert css_text.startswith("@layer blocks {")
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-toolbar",
        )
        assert root_blocks
        assert "display: block;" in root_blocks[0]
        assert "margin: 0;" in root_blocks[0]

    def test_tier_3_tokens_map_exclusively_from_tier_2_tokens(self) -> None:
        """Verify .dds-toolbar defines --_toolbar-* tokens mapped only from --dds-* tokens."""
        css_text = _read_text(path=TOOLBAR_CSS_PATH)
        assert "--_dds-" not in css_text
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-toolbar",
        )
        root_props = _extract_defined_properties(block_text="\n".join(root_blocks))
        assert root_props
        for token_name, token_val in root_props.items():
            assert token_name.startswith("--_toolbar-")
            assert token_val.startswith("var(--dds-")

        mapped_values = " ".join(root_props.values())
        for expected_family in (
            "--dds-surface-topbar-",
            "--dds-text-",
            "--dds-state-",
            "--dds-space-",
        ):
            assert expected_family in mapped_values

    def test_css_formatting_and_no_bem(self) -> None:
        """Verify zero BEM selectors, single quotes, and alphabetized declarations."""
        css_text = _read_text(path=TOOLBAR_CSS_PATH)
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


class TestToolbarGalleryAndDocs:
    """Verify co-located gallery.py and index.md for dds__toolbar."""

    def test_gallery_config_variants_render(self) -> None:
        """Verify gallery.py exports a valid GalleryConfig whose variants all render."""
        reg = _make_registry()
        cfg = gallery.load_gallery_config(
            source_dir=TOOLBAR_DIR,
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
            assert '<header class="dds-toolbar" data-surface="topbar">' in rendered
            assert "data-toolbar-brand" in rendered

    def test_index_md_exists_and_documents_component(self) -> None:
        """Verify index.md exists and documents dds__toolbar parameters and slots."""
        doc_text = _read_text(path=TOOLBAR_INDEX_MD_PATH)
        assert "dds__toolbar" in doc_text
        assert "dds-toolbar" in doc_text
        assert "brand_name" in doc_text
        assert "leading" in doc_text
        assert "actions" in doc_text
