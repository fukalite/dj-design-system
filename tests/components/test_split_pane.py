"""Unit tests for the built-in ``dds__split_pane`` domain component."""

import pathlib
import re

import pytest
from django import template
from django.utils import safestring

from dj_design_system import data, gallery
from dj_design_system.components import base as components_base
from dj_design_system.components.domain import split_pane as split_pane_package
from dj_design_system.components.domain.split_pane import (
    split_pane as split_pane_module,
)
from dj_design_system.services import canvas as canvas_service
from dj_design_system.services import registry as registry_service
from dj_design_system.services import slot_node as slot_node_service
from tests import conftest


APP_LABEL = "dj_design_system"
COMPONENT_NAME = "split_pane"
QUALIFIED_NAME = "dds__split_pane"
RELATIVE_PATH = "domain.split_pane"
TEMPLATE_PATH = "dj_design_system/components/domain/split_pane/split_pane.html"
CSS_MEDIA_PATH = "dj_design_system/components/domain/split_pane/split_pane.css"
JS_MEDIA_PATH = "dj_design_system/components/domain/split_pane/split_pane.js"

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
SPLIT_PANE_DIR = (
    ROOT_DIR / "dj_design_system" / "components" / "domain" / "split_pane"
)
SPLIT_PANE_PY_PATH = SPLIT_PANE_DIR / "split_pane.py"
SPLIT_PANE_HTML_PATH = SPLIT_PANE_DIR / "split_pane.html"
SPLIT_PANE_CSS_PATH = SPLIT_PANE_DIR / "split_pane.css"
SPLIT_PANE_TS_PATH = SPLIT_PANE_DIR / "split_pane.ts"
SPLIT_PANE_GALLERY_PATH = SPLIT_PANE_DIR / "gallery.py"
SPLIT_PANE_INDEX_MD_PATH = SPLIT_PANE_DIR / "index.md"
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
    lib.tag(name="slot", compile_function=slot_node_service.do_slot)
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


class TestSplitPaneDiscoveryAndMetadata:
    """Verify SplitPane exports, metadata, media, slots, and registry discovery."""

    def test_exported_from_package_init_and_subclasses_block_component(self) -> None:
        """Verify SplitPane is exported in dj_design_system.components.domain.split_pane."""
        assert split_pane_package.SplitPane is split_pane_module.SplitPane
        assert issubclass(
            split_pane_module.SplitPane,
            components_base.BlockComponent,
        )
        assert split_pane_module.SplitPane.has_slots() is True

    def test_template_media_and_slots_metadata(self) -> None:
        """Verify SplitPane declares co-located template_name, Media.css/js, and primary/secondary slots."""
        assert split_pane_module.SplitPane.template_name == TEMPLATE_PATH
        assert split_pane_module.SplitPane.Media.css == CSS_MEDIA_PATH
        assert split_pane_module.SplitPane.Media.js == JS_MEDIA_PATH
        slots_spec = split_pane_module.SplitPane.get_slots()
        assert set(slots_spec.keys()) == {"primary", "secondary"}
        assert slots_spec["primary"].required is False
        assert slots_spec["secondary"].required is False

    def test_discovered_as_dds_split_pane_in_registry(self) -> None:
        """Verify ComponentRegistry discovers SplitPane as internal dds__split_pane."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.component_class is split_pane_module.SplitPane
        assert info.qualified_name == QUALIFIED_NAME
        assert info.relative_path == RELATIVE_PATH
        assert info.is_internal is True
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]
        assert info.media.js == [JS_MEDIA_PATH]

    def test_python_module_contains_no_private_methods_comments_or_mark_safe(
        self,
    ) -> None:
        """Verify split_pane.py has no private helper methods, inline comments, format_html, or mark_safe."""
        own_private_methods = [
            name
            for name, attr in split_pane_module.SplitPane.__dict__.items()
            if name.startswith("_") and not name.startswith("__") and callable(attr)
        ]
        assert not own_private_methods
        py_text = _read_text(path=SPLIT_PANE_PY_PATH)
        assert "format_html" not in py_text
        assert "mark_safe" not in py_text
        for line in py_text.splitlines():
            assert not line.lstrip().startswith("#")


class TestSplitPaneParametersAndContext:
    """Verify parameter validation, ratio clamping, ARIA orientation, and get_context()."""

    def test_default_parameters_and_context(self) -> None:
        """Verify default parameters produce expected normalized context values."""
        comp = split_pane_module.SplitPane()
        ctx = comp.get_context()
        assert ctx["resolved_orientation"] == "horizontal"
        assert ctx["separator_aria_orientation"] == "vertical"
        assert ctx["resolved_min_ratio"] == 20
        assert ctx["resolved_max_ratio"] == 80
        assert ctx["resolved_ratio"] == 50
        assert ctx["primary_content"] == ""
        assert ctx["secondary_content"] == ""
        assert ctx["primary_label"] == ""
        assert ctx["secondary_label"] == ""
        assert ctx["primary_surface"] == "docs"
        assert ctx["secondary_surface"] == "sandbox"
        assert ctx["resolved_resizer_label"] == "Resize panes"
        assert ctx["has_primary_label"] is False
        assert ctx["has_secondary_label"] is False
        assert ctx["has_primary_surface"] is True
        assert ctx["has_secondary_surface"] is True
        assert ctx["slots"] == {"primary": "", "secondary": ""}
        assert ctx["content"] == ""

    def test_vertical_orientation_inverts_separator_aria_orientation(self) -> None:
        """Verify vertical split orientation sets separator aria-orientation to horizontal."""
        comp = split_pane_module.SplitPane(orientation="vertical")
        ctx = comp.get_context()
        assert ctx["resolved_orientation"] == "vertical"
        assert ctx["separator_aria_orientation"] == "horizontal"

    def test_clamps_min_max_and_initial_ratios_within_bounds(self) -> None:
        """Verify min_ratio, max_ratio, and initial_ratio clamp to [10, 90] and respect min <= initial <= max."""
        comp_low = split_pane_module.SplitPane(
            min_ratio=2,
            max_ratio=98,
            initial_ratio=5,
        )
        ctx_low = comp_low.get_context()
        assert ctx_low["resolved_min_ratio"] == 10
        assert ctx_low["resolved_max_ratio"] == 90
        assert ctx_low["resolved_ratio"] == 10

        comp_high = split_pane_module.SplitPane(
            min_ratio=30,
            max_ratio=70,
            initial_ratio=85,
        )
        ctx_high = comp_high.get_context()
        assert ctx_high["resolved_min_ratio"] == 30
        assert ctx_high["resolved_max_ratio"] == 70
        assert ctx_high["resolved_ratio"] == 70

        comp_inverted = split_pane_module.SplitPane(
            min_ratio=65,
            max_ratio=40,
            initial_ratio=50,
        )
        ctx_inverted = comp_inverted.get_context()
        assert ctx_inverted["resolved_min_ratio"] == 65
        assert ctx_inverted["resolved_max_ratio"] == 65
        assert ctx_inverted["resolved_ratio"] == 65

    def test_slots_and_direct_content_fallback_and_surface_flags(self) -> None:
        """Verify primary slot overrides content fallback, and empty surface strings disable surface attributes."""
        comp_fallback = split_pane_module.SplitPane(
            content="<p>Direct primary</p>",
            primary_surface="",
            secondary_surface="",
            primary_label="Left",
            secondary_label="Right",
            resizer_label="",
        )
        ctx_fallback = comp_fallback.get_context()
        assert isinstance(comp_fallback.content, safestring.SafeString)
        assert ctx_fallback["primary_content"] == "<p>Direct primary</p>"
        assert ctx_fallback["secondary_content"] == ""
        assert ctx_fallback["has_primary_surface"] is False
        assert ctx_fallback["has_secondary_surface"] is False
        assert ctx_fallback["has_primary_label"] is True
        assert ctx_fallback["has_secondary_label"] is True
        assert ctx_fallback["resolved_resizer_label"] == "Resize panes"

        comp_slots = split_pane_module.SplitPane(
            content="<p>Ignored fallback</p>",
            slots={
                "primary": "<p>Slot primary</p>",
                "secondary": "<p>Slot secondary</p>",
            },
        )
        assert isinstance(comp_slots.slots["primary"], safestring.SafeString)
        assert isinstance(comp_slots.slots["secondary"], safestring.SafeString)
        ctx_slots = comp_slots.get_context()
        assert ctx_slots["primary_content"] == "<p>Slot primary</p>"
        assert ctx_slots["secondary_content"] == "<p>Slot secondary</p>"

    def test_invalid_orientation_or_ratio_type_raises_error(self) -> None:
        """Verify invalid orientation choice raises ValueError and non-int ratio raises TypeError."""
        with pytest.raises(
            expected_exception=ValueError,
            match="Expected one of",
        ):
            split_pane_module.SplitPane(orientation="diagonal")
        with pytest.raises(expected_exception=TypeError, match="Expected int"):
            split_pane_module.SplitPane(initial_ratio="fifty")


class TestSplitPaneRenderingAndTemplate:
    """Verify HTML rendering via template tags, slots, ARIA attributes, and escaping."""

    def test_renders_default_horizontal_split_pane_with_slots(self) -> None:
        """Verify default horizontal split pane renders root attributes, separator ARIA, and slot bodies."""
        html = _render_template(
            source=(
                "{% dds__split_pane %}"
                '{% slot "primary" %}<div class="pane-a">Pane A</div>{% endslot %}'
                '{% slot "secondary" %}<div class="pane-b">Pane B</div>{% endslot %}'
                "{% enddds__split_pane %}"
            ),
        )
        assert '<dds-split-pane class="dds-split-pane"' in html
        assert 'data-orientation="horizontal"' in html
        assert 'data-min-ratio="20"' in html
        assert 'data-max-ratio="80"' in html
        assert 'style="--_split-pane-ratio: 50%;"' in html
        assert '<div data-split-pane="primary" data-surface="docs">' in html
        assert '<div data-split-pane="secondary" data-surface="sandbox">' in html
        assert "data-split-pane-header" not in html
        assert (
            '<div data-split-pane-body><div class="pane-a">Pane A</div></div>'
            in html
        )
        assert (
            '<div data-split-pane-body><div class="pane-b">Pane B</div></div>'
            in html
        )
        assert "data-split-resizer" in html
        assert 'role="separator"' in html
        assert 'tabindex="0"' in html
        assert 'aria-orientation="vertical"' in html
        assert 'aria-label="Resize panes"' in html
        assert 'aria-valuemin="20"' in html
        assert 'aria-valuemax="80"' in html
        assert 'aria-valuenow="50"' in html

    def test_renders_vertical_split_pane_with_labels_and_custom_surfaces(
        self,
    ) -> None:
        """Verify vertical orientation, pane headers, custom surfaces, and omitted surface when empty."""
        html = _render_template(
            source=(
                '{% dds__split_pane orientation="vertical" initial_ratio=65 '
                'min_ratio=25 max_ratio=75 primary_surface="stage" '
                'secondary_surface="" primary_label="Canvas" '
                'secondary_label="Markup" resizer_label="Adjust split" %}'
                '{% slot "primary" %}<p>Top</p>{% endslot %}'
                '{% slot "secondary" %}<p>Bottom</p>{% endslot %}'
                "{% enddds__split_pane %}"
            ),
        )
        assert 'data-orientation="vertical"' in html
        assert 'data-min-ratio="25"' in html
        assert 'data-max-ratio="75"' in html
        assert 'style="--_split-pane-ratio: 65%;"' in html
        assert '<div data-split-pane="primary" data-surface="stage">' in html
        assert '<div data-split-pane="secondary">' in html
        assert "<div data-split-pane-header>Canvas</div>" in html
        assert "<div data-split-pane-header>Markup</div>" in html
        assert 'aria-orientation="horizontal"' in html
        assert 'aria-label="Adjust split"' in html
        assert 'aria-valuemin="25"' in html
        assert 'aria-valuemax="75"' in html
        assert 'aria-valuenow="65"' in html

    def test_escapes_untrusted_labels_and_surfaces(self) -> None:
        """Verify untrusted strings in labels and surface attributes are HTML-escaped."""
        html = _render_template(
            source=(
                "{% dds__split_pane primary_label=primary_label "
                "secondary_label=secondary_label "
                "primary_surface=primary_surface "
                "resizer_label=resizer_label %}"
                "{% enddds__split_pane %}"
            ),
            context_data={
                "primary_label": "<script>alert(1)</script>",
                "secondary_label": "<b>Unsafe</b>",
                "primary_surface": 'docs" data-evil="1',
                "resizer_label": 'Resize "unsafe"',
            },
        )
        assert "<script>alert(1)</script>" not in html
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
        assert "&lt;b&gt;Unsafe&lt;/b&gt;" in html
        assert 'data-surface="docs&quot; data-evil=&quot;1"' in html
        assert 'aria-label="Resize &quot;unsafe&quot;"' in html

    def test_template_contains_no_filters_and_no_bem(self) -> None:
        """Verify split_pane.html has zero template filters and zero BEM classes."""
        template_text = _read_text(path=SPLIT_PANE_HTML_PATH)
        assert "|" not in template_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=template_text,
        )
        assert not bem_matches


class TestSplitPaneStylesheet:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, and formatting in split_pane.css."""

    def test_wrapped_in_layer_blocks_and_sets_root_layout(self) -> None:
        """Verify split_pane.css wraps rules in @layer blocks and sets flex layout and margin: 0."""
        css_text = _read_text(path=SPLIT_PANE_CSS_PATH)
        assert css_text.startswith("@layer blocks {")
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector="dds-split-pane,\n  .dds-split-pane",
        )
        assert root_blocks
        props = _extract_defined_properties(block_text=root_blocks[0])
        assert props.get("margin") == "0"
        assert props.get("display") == "flex"
        assert props.get("flex-direction") == "row"

    def test_tier_3_tokens_map_exclusively_from_tier_2_tokens_in_tokens_css(
        self,
    ) -> None:
        """Verify all --_split-pane-* tokens map exclusively from Tier 2 --dds-* tokens in tokens.css."""
        css_text = _read_text(path=SPLIT_PANE_CSS_PATH)
        tokens_text = _read_text(path=TOKENS_CSS_PATH)
        assert "--_dds-" not in css_text

        defined_tier_2_tokens = set(
            re.findall(pattern=r"(--dds-[a-z0-9-]+)\s*:", string=tokens_text)
        )
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector="dds-split-pane,\n  .dds-split-pane",
        )
        root_props = _extract_defined_properties(block_text="\n".join(root_blocks))
        tier_3_props = {
            name: value
            for name, value in root_props.items()
            if name.startswith("--_")
        }
        assert tier_3_props
        for name, value in tier_3_props.items():
            assert name.startswith("--_split-pane-")
            match = re.fullmatch(pattern=r"var\((--dds-[a-z0-9-]+)\)", string=value)
            assert match is not None
            assert match.group(1) in defined_tier_2_tokens

    def test_no_bem_single_quotes_and_alphabetized_declarations(self) -> None:
        """Verify zero BEM selectors, single quotes, and alphabetised declarations."""
        css_text = _read_text(path=SPLIT_PANE_CSS_PATH)
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


class TestSplitPaneGalleryAndDocs:
    """Verify co-located gallery.py and index.md for dds__split_pane."""

    def test_gallery_config_variants_render(self) -> None:
        """Verify gallery.py exports a valid GalleryConfig whose variants all render."""
        assert SPLIT_PANE_GALLERY_PATH.is_file()
        reg = _make_registry()
        cfg = gallery.load_gallery_config(
            source_dir=SPLIT_PANE_DIR,
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
            assert '<dds-split-pane class="dds-split-pane"' in rendered
            assert 'role="separator"' in rendered

    def test_index_md_exists_and_documents_component(self) -> None:
        """Verify index.md exists and documents dds__split_pane, parameters, and slots."""
        assert SPLIT_PANE_INDEX_MD_PATH.is_file()
        doc_text = _read_text(path=SPLIT_PANE_INDEX_MD_PATH)
        assert "dds__split_pane" in doc_text
        assert "dds-split-pane" in doc_text
        for documented_item in (
            "orientation",
            "initial_ratio",
            "min_ratio",
            "max_ratio",
            "primary_surface",
            "secondary_surface",
            "primary_label",
            "secondary_label",
            "resizer_label",
            "primary",
            "secondary",
        ):
            assert documented_item in doc_text


class TestSplitPaneTypeScriptCustomElement:
    """Verify Light DOM <dds-split-pane> TypeScript contract in split_pane.ts."""

    def test_split_pane_ts_implements_custom_element_and_lifecycle_contract(
        self,
    ) -> None:
        """Verify split_pane.ts defines DDSSplitPaneElement, AbortController, and registration."""
        assert SPLIT_PANE_TS_PATH.is_file()
        ts_text = _read_text(path=SPLIT_PANE_TS_PATH)
        assert (
            "import type { DDSCustomElement } from '../../types.js';"
            in ts_text
        )
        assert "export class DDSSplitPaneElement" in ts_text
        assert "extends HTMLElement" in ts_text
        assert "implements DDSCustomElement {" in ts_text
        assert "private abortController: AbortController | null = null;" in ts_text
        assert "this.abortController?.abort();" in ts_text
        assert "this.abortController = new AbortController();" in ts_text
        assert "connectedCallback(): void {" in ts_text
        assert "disconnectedCallback(): void {" in ts_text
        assert (
            "this.querySelector<HTMLElement>('[data-split-resizer]')"
            in ts_text
        )
        assert "if (!customElements.get('dds-split-pane')) {" in ts_text
        assert (
            "customElements.define('dds-split-pane', DDSSplitPaneElement);"
            in ts_text
        )
        assert "attachShadow" not in ts_text
        assert "document.querySelector" not in ts_text
        assert "\t" not in ts_text
        for line in ts_text.splitlines():
            assert len(line) <= 80
            assert line == line.rstrip()

    def test_split_pane_ts_implements_pointer_and_keyboard_resize_contract(
        self,
    ) -> None:
        """Verify split_pane.ts handles pointer drag, keyboard resize, clamping, and dds:split-resize."""
        ts_text = _read_text(path=SPLIT_PANE_TS_PATH)
        assert (
            "Number(this.getAttribute('data-min-ratio') ?? '20') || 20"
            in ts_text
        )
        assert (
            "Number(this.getAttribute('data-max-ratio') ?? '80') || 80"
            in ts_text
        )
        assert "this.getAttribute('data-orientation') === 'vertical'" in ts_text
        assert "const STEP_PERCENT = 5;" in ts_text
        assert "this.setAttribute('data-dragging', 'true');" in ts_text
        assert "this.removeAttribute('data-dragging');" in ts_text
        assert "setPointerCapture" in ts_text
        for pointer_event in (
            "pointerdown",
            "pointermove",
            "pointerup",
            "pointercancel",
        ):
            assert f"'{pointer_event}'" in ts_text
        for key in (
            "ArrowLeft",
            "ArrowRight",
            "ArrowUp",
            "ArrowDown",
            "Home",
            "End",
        ):
            assert f"'{key}'" in ts_text
        assert "event.preventDefault();" in ts_text
        assert (
            "this.style.setProperty('--_split-pane-ratio', `${ratio}%`);"
            in ts_text
        )
        assert "resizer.setAttribute('aria-valuenow', String(ratio));" in ts_text
        assert "'dds:split-resize'" in ts_text
        assert "bubbles: true" in ts_text
        assert "detail: { ratio, orientation }" in ts_text

