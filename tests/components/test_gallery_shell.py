"""Unit tests for the built-in ``dds__gallery_shell`` domain component."""

import pathlib
import re

import pytest
from django import template
from django.utils import safestring

from dj_design_system import data, gallery
from dj_design_system.components import base as components_base
from dj_design_system.components.domain import gallery_shell as gallery_shell_package
from dj_design_system.components.domain.gallery_shell import (
    gallery_shell as gallery_shell_module,
)
from dj_design_system.services import canvas as canvas_service
from dj_design_system.services import registry as registry_service
from dj_design_system.services import slot_node
from tests import conftest


APP_LABEL = "dj_design_system"
COMPONENT_NAME = "gallery_shell"
QUALIFIED_NAME = "dds__gallery_shell"
RELATIVE_PATH = "domain.gallery_shell"
TEMPLATE_PATH = "dj_design_system/components/domain/gallery_shell/gallery_shell.html"
CSS_MEDIA_PATH = "dj_design_system/components/domain/gallery_shell/gallery_shell.css"
JS_MEDIA_PATH = "dj_design_system/components/domain/gallery_shell/gallery_shell.js"

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
GALLERY_SHELL_DIR = (
    ROOT_DIR / "dj_design_system" / "components" / "domain" / "gallery_shell"
)
GALLERY_SHELL_PY_PATH = GALLERY_SHELL_DIR / "gallery_shell.py"
GALLERY_SHELL_HTML_PATH = GALLERY_SHELL_DIR / "gallery_shell.html"
GALLERY_SHELL_CSS_PATH = GALLERY_SHELL_DIR / "gallery_shell.css"
GALLERY_SHELL_TS_PATH = GALLERY_SHELL_DIR / "gallery_shell.ts"
GALLERY_SHELL_GALLERY_PATH = GALLERY_SHELL_DIR / "gallery.py"
GALLERY_SHELL_INDEX_MD_PATH = GALLERY_SHELL_DIR / "index.md"
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
    """Build sample navigation nodes for gallery_shell rendering tests."""
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


class TestGalleryShellDiscoveryAndMetadata:
    """Verify GalleryShell exports, metadata, media, slots, and registry discovery."""

    def test_exported_from_package_init_and_subclasses_block_component(self) -> None:
        """Verify GalleryShell is exported in dj_design_system.components.domain.gallery_shell."""
        assert gallery_shell_package.GalleryShell is gallery_shell_module.GalleryShell
        assert issubclass(
            gallery_shell_module.GalleryShell,
            components_base.BlockComponent,
        )
        assert gallery_shell_module.GalleryShell.has_slots() is True

    def test_template_media_and_slots_metadata(self) -> None:
        """Verify GalleryShell relies on co-located template_name, Media.css/js, and 4 optional slots."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]
        assert info.media.js == [JS_MEDIA_PATH]
        slots_spec = gallery_shell_module.GalleryShell.get_slots()
        assert set(slots_spec.keys()) == {
            "topbar",
            "sidebar",
            "toolbar_actions",
            "main",
        }
        for slot_obj in slots_spec.values():
            assert slot_obj.required is False

    def test_discovered_as_dds_gallery_shell_in_registry(self) -> None:
        """Verify ComponentRegistry discovers GalleryShell as internal dds__gallery_shell."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.component_class is gallery_shell_module.GalleryShell
        assert info.qualified_name == QUALIFIED_NAME
        assert info.relative_path == RELATIVE_PATH
        assert info.is_internal is True
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]
        assert info.media.js == [JS_MEDIA_PATH]

    def test_python_module_contains_no_private_methods_or_mark_safe(self) -> None:
        """Verify gallery_shell.py has no private helper methods, format_html, or mark_safe."""
        own_private_methods = [
            name
            for name, attr in gallery_shell_module.GalleryShell.__dict__.items()
            if name.startswith("_") and not name.startswith("__") and callable(attr)
        ]
        assert not own_private_methods
        py_text = _read_text(path=GALLERY_SHELL_PY_PATH)
        assert "format_html" not in py_text
        assert "mark_safe" not in py_text
        private_defs = re.findall(
            pattern=r"def _(?![_a-z]+__)[a-z0-9_]+",
            string=py_text,
        )
        assert not private_defs


class TestGalleryShellParametersAndContext:
    """Verify parameter defaults, active_variant normalization, and get_context() shaping."""

    def test_default_parameters_and_context(self) -> None:
        """Verify default parameters produce expected normalized context flags."""
        comp = gallery_shell_module.GalleryShell()
        ctx = comp.get_context()
        assert comp.nodes is None
        assert comp.breadcrumbs is None
        assert comp.themes is None
        assert comp.search_index is None
        assert ctx["brand_name"] == "Design System"
        assert ctx["brand_url"] == "/"
        assert ctx["resolved_theme"] == "light"
        assert ctx["active_theme"] == "light"
        assert ctx["nodes"] == []
        assert ctx["active_path"] == ""
        assert ctx["active_variant"] == ""
        assert ctx["breadcrumbs"] == []
        assert ctx["themes"] == []
        assert ctx["search_index"] == []
        assert ctx["has_topbar_slot"] is False
        assert ctx["has_sidebar_slot"] is False
        assert ctx["has_toolbar_actions_slot"] is False
        assert ctx["toolbar_actions_content"] == ""
        assert ctx["main_content"] == ""
        assert ctx["has_main_content"] is False
        assert ctx["slots"] == {
            "topbar": "",
            "sidebar": "",
            "toolbar_actions": "",
            "main": "",
        }
        assert ctx["content"] == ""

    def test_normalizes_variant_instance_and_slots_and_content(self) -> None:
        """Verify Variant instance normalization in __init__ and slot/content flags in get_context()."""
        variant_obj = gallery.Variant(name="primary", label="Primary")
        breadcrumbs = [{"label": "Domain", "url": "/domain/"}]
        themes = [
            {"value": "light", "label": "Light"},
            {"value": "dark", "label": "Dark"},
        ]
        search_index = [{"label": "Button", "url": "/button/"}]
        comp = gallery_shell_module.GalleryShell(
            content="<p>Fallback content</p>",
            slots={
                "topbar": safestring.SafeString("<header>Custom Topbar</header>"),
                "sidebar": safestring.SafeString("<aside>Custom Sidebar</aside>"),
                "toolbar_actions": safestring.SafeString("<button>Action</button>"),
                "main": safestring.SafeString("<h1>Main Slot</h1>"),
            },
            brand_name="Acme DS",
            brand_url="/acme/",
            nodes=_make_sample_nodes(),
            active_path="dj_design_system/elements/button",
            active_variant=variant_obj,
            breadcrumbs=breadcrumbs,
            themes=themes,
            active_theme="dark",
            search_index=search_index,
        )
        assert comp.active_variant == "primary"
        assert isinstance(comp.content, safestring.SafeString)
        assert isinstance(comp.slots["topbar"], safestring.SafeString)
        assert isinstance(comp.slots["sidebar"], safestring.SafeString)
        assert isinstance(comp.slots["toolbar_actions"], safestring.SafeString)
        assert isinstance(comp.slots["main"], safestring.SafeString)

        ctx = comp.get_context()
        assert ctx["brand_name"] == "Acme DS"
        assert ctx["brand_url"] == "/acme/"
        assert ctx["resolved_theme"] == "dark"
        assert ctx["active_theme"] == "dark"
        assert len(ctx["nodes"]) == 1
        assert ctx["active_path"] == "dj_design_system/elements/button"
        assert ctx["active_variant"] == "primary"
        assert ctx["breadcrumbs"] == breadcrumbs
        assert ctx["themes"] == themes
        assert ctx["search_index"] == search_index
        assert ctx["has_topbar_slot"] is True
        assert ctx["has_sidebar_slot"] is True
        assert ctx["has_toolbar_actions_slot"] is True
        assert ctx["toolbar_actions_content"] == "<button>Action</button>"
        assert ctx["main_content"] == "<h1>Main Slot</h1>"
        assert ctx["has_main_content"] is True

    def test_main_content_falls_back_to_block_content_when_main_slot_empty(
        self,
    ) -> None:
        """Verify main_content falls back to self.content when main slot is not provided."""
        comp = gallery_shell_module.GalleryShell(
            content=safestring.SafeString("<section>Python Body</section>"),
            brand_name="",
            brand_url="",
            active_theme="",
        )
        ctx = comp.get_context()
        assert ctx["brand_name"] == "Design System"
        assert ctx["brand_url"] == "/"
        assert ctx["resolved_theme"] == "light"
        assert ctx["main_content"] == "<section>Python Body</section>"
        assert ctx["has_main_content"] is True

    def test_whitespace_only_main_content_sets_has_main_content_false(self) -> None:
        """Verify whitespace-only main_content sets has_main_content=False."""
        comp = gallery_shell_module.GalleryShell(content="   \n  ")
        ctx = comp.get_context()
        assert ctx["has_main_content"] is False

    def test_invalid_list_parameters_raise_type_error(self) -> None:
        """Verify passing non-list to nodes, breadcrumbs, themes, or search_index raises TypeError."""
        with pytest.raises(expected_exception=TypeError, match="Expected list"):
            gallery_shell_module.GalleryShell(nodes="invalid")
        with pytest.raises(expected_exception=TypeError, match="Expected list"):
            gallery_shell_module.GalleryShell(breadcrumbs="invalid")
        with pytest.raises(expected_exception=TypeError, match="Expected list"):
            gallery_shell_module.GalleryShell(themes="invalid")
        with pytest.raises(expected_exception=TypeError, match="Expected list"):
            gallery_shell_module.GalleryShell(search_index="invalid")


class TestGalleryShellRenderingAndTemplate:
    """Verify template tag rendering, child component delegation, slots, and template purity."""

    def test_renders_default_gallery_shell_with_toolbar_sidebar_and_main(self) -> None:
        """Verify default {% dds__gallery_shell %} delegates to dds__toolbar and dds__sidebar."""
        breadcrumbs = [
            {"label": "Domain", "url": "/domain/"},
            {"label": "Gallery Shell", "url": "/domain/gallery_shell/"},
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
                '{% dds__gallery_shell brand_name="Acme DS" brand_url="/acme/" '
                'nodes=nodes active_path="dj_design_system/elements/button" '
                'active_variant="primary" breadcrumbs=breadcrumbs '
                'themes=themes active_theme="dark" search_index=search_index %}'
                '{% slot "toolbar_actions" %}<a href="/repo" data-extra-action>Repo</a>{% endslot %}'
                '{% slot "main" %}<article data-main-doc>Documentation</article>{% endslot %}'
                "{% enddds__gallery_shell %}"
            ),
            context_data={
                "nodes": _make_sample_nodes(),
                "breadcrumbs": breadcrumbs,
                "themes": themes,
                "search_index": search_index,
            },
        ).strip()
        assert (
            '<dds-gallery-shell class="dds-gallery-shell" '
            'data-drawer-state="closed" data-theme="dark">' in html
        )
        assert "<div data-shell-topbar>" in html
        assert '<header class="dds-toolbar" data-surface="topbar">' in html
        assert '<a href="/acme/" data-toolbar-brand>Acme DS</a>' in html
        assert '<nav class="dds-breadcrumb"' in html
        assert (
            '<dds-theme-select class="dds-theme-select" data-active-theme="dark">'
            in html
        )
        assert '<a href="/repo" data-extra-action>Repo</a>' in html
        assert '<div class="l-sidebar" data-shell-body>' in html
        assert (
            '<div class="dds-gallery-shell-backdrop" data-surface="overlay" '
            'data-shell-backdrop hidden aria-hidden="true"></div>' in html
        )
        assert '<div data-shell-sidebar id="dds-gallery-drawer">' in html
        assert '<aside class="dds-sidebar" data-surface="sidebar"' in html
        assert '<dds-nav-tree class="dds-nav-tree">' in html
        assert (
            '<main class="dds-gallery-shell-main" data-surface="docs" '
            'data-shell-main id="gallery-main-content">'
            "<article data-main-doc>Documentation</article></main>" in html
        )

    def test_renders_custom_topbar_and_sidebar_slots_and_direct_content(self) -> None:
        """Verify topbar and sidebar slots override default dds__toolbar and dds__sidebar."""
        html = _render_template(
            source=(
                "{% dds__gallery_shell %}"
                '{% slot "topbar" %}<div data-custom-topbar>Custom Header</div>{% endslot %}'
                '{% slot "sidebar" %}<nav data-custom-sidebar>Custom Nav</nav>{% endslot %}'
                '{% slot "main" %}<p data-custom-main>Body</p>{% endslot %}'
                "{% enddds__gallery_shell %}"
            ),
        ).strip()
        assert "<div data-custom-topbar>Custom Header</div>" in html
        assert 'class="dds-toolbar"' not in html
        assert "<nav data-custom-sidebar>Custom Nav</nav>" in html
        assert 'class="dds-sidebar"' not in html
        assert "<p data-custom-main>Body</p>" in html

        _make_registry()
        direct_html = gallery_shell_module.GalleryShell(
            content=safestring.SafeString(
                "<div data-direct-main>Direct Python Content</div>"
            ),
        ).render()
        assert "<div data-direct-main>Direct Python Content</div>" in direct_html

    def test_escapes_untrusted_brand_and_theme_parameters(self) -> None:
        """Verify untrusted strings in brand_name, brand_url, and active_theme are HTML-escaped."""
        html = _render_template(
            source=(
                "{% dds__gallery_shell brand_name=brand_name brand_url=brand_url "
                "active_theme=active_theme %}"
                "{% enddds__gallery_shell %}"
            ),
            context_data={
                "brand_name": "<script>alert(1)</script>",
                "brand_url": '"/onload="evil()',
                "active_theme": 'light" data-evil="1',
            },
        )
        assert "<script>alert(1)</script>" not in html
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
        assert 'data-theme="light&quot; data-evil=&quot;1"' in html

    def test_template_contains_no_filters_and_no_bem(self) -> None:
        """Verify gallery_shell.html loads design_components and has zero filters or BEM."""
        template_text = _read_text(path=GALLERY_SHELL_HTML_PATH)
        assert template_text.startswith("{% load design_components %}")
        assert "|" not in template_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=template_text,
        )
        assert not bem_matches


class TestGalleryShellStylesheet:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, and formatting in gallery_shell.css."""

    def test_wrapped_in_layer_blocks_and_sets_root_layout(self) -> None:
        """Verify gallery_shell.css wraps rules in @layer blocks and sets flex column and min-height 100vh."""
        css_text = _read_text(path=GALLERY_SHELL_CSS_PATH)
        assert css_text.startswith("@layer blocks {")
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector="dds-gallery-shell,\n  .dds-gallery-shell",
        )
        assert root_blocks
        props = _extract_defined_properties(block_text=root_blocks[0])
        assert props.get("margin") == "0"
        assert props.get("display") == "flex"
        assert props.get("flex-direction") == "column"
        assert props.get("min-height") == "100vh"

    def test_tier_3_tokens_map_exclusively_from_tier_2_tokens_in_tokens_css(
        self,
    ) -> None:
        """Verify all --_gallery-shell-* tokens map exclusively from Tier 2 --dds-* tokens in tokens.css."""
        css_text = _read_text(path=GALLERY_SHELL_CSS_PATH)
        tokens_text = _read_text(path=TOKENS_CSS_PATH)
        assert "--_dds-" not in css_text

        defined_tier_2_tokens = set(
            re.findall(pattern=r"(--dds-[a-z0-9-]+)\s*:", string=tokens_text)
        )
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector="dds-gallery-shell,\n  .dds-gallery-shell",
        )
        root_props = _extract_defined_properties(block_text="\n".join(root_blocks))
        tier_3_props = {
            name: value for name, value in root_props.items() if name.startswith("--_")
        }
        assert tier_3_props
        for name, value in tier_3_props.items():
            assert name.startswith("--_gallery-shell-")
            match = re.fullmatch(pattern=r"var\((--dds-[a-z0-9-]+)\)", string=value)
            assert match is not None
            assert match.group(1) in defined_tier_2_tokens

    def test_no_bem_single_quotes_and_alphabetized_declarations(self) -> None:
        """Verify zero BEM selectors, single quotes, and alphabetised declarations."""
        css_text = _read_text(path=GALLERY_SHELL_CSS_PATH)
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

    def test_contains_no_child_component_internal_selectors(self) -> None:
        """Verify gallery_shell.css does not style internals of child components."""
        css_text = _read_text(path=GALLERY_SHELL_CSS_PATH)
        for forbidden_selector in (
            ".dds-usage-example",
            "[role='tablist']",
            "[role='tab']",
            "[data-sidebar-header]",
            "[data-split-pane-header]",
            "[data-split-resizer]",
            "[data-split-pane=",
            ".dds-tabs",
            "dds-tabs",
        ):
            assert forbidden_selector not in css_text


class TestGalleryShellCustomElementTypeScript:
    """Verify Light DOM <dds-gallery-shell> TypeScript contract in gallery_shell.ts."""

    def test_ts_implements_custom_element_and_interactivity_contract(self) -> None:
        """Verify gallery_shell.ts defines DDSGalleryShellElement, drawer toggle, and theme sync."""
        assert GALLERY_SHELL_TS_PATH.is_file()
        ts_text = _read_text(path=GALLERY_SHELL_TS_PATH)
        assert "import type { DDSCustomElement } from '../../types.js';" in ts_text
        assert (
            "export class DDSGalleryShellElement" in ts_text
            and "extends HTMLElement" in ts_text
            and "implements DDSCustomElement" in ts_text
        )
        assert "private abortController: AbortController | null = null;" in ts_text
        assert "connectedCallback(): void" in ts_text
        assert "disconnectedCallback(): void" in ts_text
        assert "this.abortController?.abort();" in ts_text
        assert "this.abortController = new AbortController();" in ts_text
        assert "this.abortController = null;" in ts_text
        assert "this.querySelectorAll<HTMLElement>(" in ts_text
        assert "'[data-action=\"toggle-drawer\"], [data-drawer-toggle]'" in ts_text
        assert "this.querySelector<HTMLElement>('[data-shell-backdrop]')" in ts_text
        assert "this.dataset.drawerState = isOpen ? 'open' : 'closed';" in ts_text
        assert (
            "trigger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');"
            in ts_text
        )
        assert "backdrop.hidden = !isOpen;" in ts_text
        assert "new CustomEvent('dds:drawer-toggle'" in ts_text
        assert "bubbles: true," in ts_text
        assert "detail: { open: isOpen }," in ts_text
        assert (
            "event.key === 'Escape' && this.dataset.drawerState === 'open'" in ts_text
        )
        assert "this.setDrawerOpen(false);" in ts_text
        assert "'dds:theme-change'" in ts_text
        assert "this.dataset.theme = theme;" in ts_text
        assert "currentUrl.searchParams.set('_dds_theme', theme);" in ts_text
        assert "iframeUrl.searchParams.set('_dds_theme', theme);" in ts_text
        assert "gallery-theme-dark" not in ts_text
        assert "gallery-theme-light" not in ts_text
        assert "includes('dark')" not in ts_text
        assert "document.documentElement" not in ts_text
        assert "document.body" not in ts_text
        assert "if (!customElements.get('dds-gallery-shell'))" in ts_text
        assert (
            "customElements.define('dds-gallery-shell', DDSGalleryShellElement);"
            in ts_text
        )

    def test_ts_enforces_light_dom_encapsulation_and_styleguide(self) -> None:
        """Verify gallery_shell.ts uses Light DOM only, scoped queries, JSDoc, and <=80 cols."""
        ts_text = _read_text(path=GALLERY_SHELL_TS_PATH)
        assert "attachShadow" not in ts_text
        assert "document.getElementById" not in ts_text
        assert "document.querySelector" not in ts_text
        for forbidden_child_ref in (
            ".dds-sandbox-toolbar",
            "data-sandbox-control",
            "dds-canvas-widget",
            '[role="tab"][data-tab-trigger]',
            "dds-outline-style",
            "dds-measure-style",
        ):
            assert forbidden_child_ref not in ts_text
        assert "\t" not in ts_text
        assert "@fileoverview" in ts_text
        assert "@param {boolean} isOpen" in ts_text
        for line in ts_text.splitlines():
            assert len(line) <= 80
            assert line == line.rstrip()


class TestGalleryShellGalleryAndDocs:
    """Verify co-located gallery.py and index.md for dds__gallery_shell."""

    def test_gallery_config_variants_render(self) -> None:
        """Verify gallery.py exports a valid GalleryConfig whose variants all render."""
        assert GALLERY_SHELL_GALLERY_PATH.is_file()
        reg = _make_registry()
        cfg = gallery.load_gallery_config(
            source_dir=GALLERY_SHELL_DIR,
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
            assert '<dds-gallery-shell class="dds-gallery-shell"' in rendered
            assert 'id="gallery-main-content"' in rendered

    def test_index_md_exists_and_documents_component(self) -> None:
        """Verify index.md exists and documents dds__gallery_shell, parameters, slots, and events."""
        assert GALLERY_SHELL_INDEX_MD_PATH.is_file()
        doc_text = _read_text(path=GALLERY_SHELL_INDEX_MD_PATH)
        assert "dds__gallery_shell" in doc_text
        assert "dds-gallery-shell" in doc_text
        for documented_item in (
            "brand_name",
            "brand_url",
            "nodes",
            "active_path",
            "active_variant",
            "breadcrumbs",
            "themes",
            "active_theme",
            "search_index",
            "topbar",
            "sidebar",
            "toolbar_actions",
            "main",
            "dds:drawer-toggle",
            "dds:theme-change",
        ):
            assert documented_item in doc_text
