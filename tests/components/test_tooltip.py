"""Unit tests for the built-in dds__tooltip element component."""

import pathlib
import re

import pytest
from django import template
from django.utils import safestring

from dj_design_system import data, gallery
from dj_design_system.components import base as components_base
from dj_design_system.components.gallery.elements import tooltip as tooltip_package
from dj_design_system.components.gallery.elements.tooltip import (
    tooltip as tooltip_module,
)
from dj_design_system.services import canvas as canvas_service
from dj_design_system.services import registry as registry_service
from tests import conftest


APP_LABEL = "dj_design_system"
COMPONENT_NAME = "tooltip"
QUALIFIED_NAME = "dds__tooltip"
RELATIVE_PATH = "gallery.elements.tooltip"
TEMPLATE_PATH = "dj_design_system/components/gallery/elements/tooltip/tooltip.html"
CSS_MEDIA_PATH = "dj_design_system/components/gallery/elements/tooltip/tooltip.css"
JS_MEDIA_PATH = "dj_design_system/components/gallery/elements/tooltip/tooltip.js"

TOOLTIP_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "components"
    / "gallery"
    / "elements"
    / "tooltip"
)
TOOLTIP_PY_PATH = TOOLTIP_DIR / "tooltip.py"
TOOLTIP_HTML_PATH = TOOLTIP_DIR / "tooltip.html"
TOOLTIP_CSS_PATH = TOOLTIP_DIR / "tooltip.css"
TOOLTIP_TS_PATH = TOOLTIP_DIR / "tooltip.ts"
TOOLTIP_GALLERY_PATH = TOOLTIP_DIR / "gallery.py"
TOOLTIP_INDEX_MD_PATH = TOOLTIP_DIR / "index.md"


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
    context: dict[str, object] | None = None,
) -> str:
    """Render a Django template string with built-in dds component tags registered."""
    reg = _make_registry()
    engine = template.engines["django"].engine
    lib = template.Library()
    reg.register_templatetags(library=lib)
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
    return conftest.extract_css_rule_blocks(css_text=css_text, selector=selector)


def _extract_defined_properties(block_text: str) -> dict[str, str]:
    """Extract custom property definitions from a CSS block string."""
    matches = re.findall(
        pattern=r"(--[a-z0-9_-]+)\s*:\s*([^;]+);",
        string=block_text,
    )
    return {name: value.strip() for name, value in matches}


class TestTooltipDiscoveryAndMetadata:
    """Verify Tooltip class exports, metadata, media, and registry discovery."""

    def test_exported_from_package_init(self) -> None:
        """Verify Tooltip is exported in dj_design_system.components.gallery.elements.tooltip."""
        assert tooltip_package.Tooltip is tooltip_module.Tooltip
        assert issubclass(tooltip_module.Tooltip, components_base.BlockComponent)
        assert tooltip_module.Tooltip.has_slots() is False

    def test_template_and_media_declarations(self) -> None:
        """Verify Tooltip relies on co-located template_name and Media.css/js auto-discovery."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]
        assert info.media.js == [JS_MEDIA_PATH]

    def test_discovered_as_dds_tooltip_in_registry(self) -> None:
        """Verify ComponentRegistry discovers Tooltip as internal dds__tooltip."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.component_class is tooltip_module.Tooltip
        assert info.qualified_name == QUALIFIED_NAME
        assert info.relative_path == RELATIVE_PATH
        assert info.is_builtin is True
        assert info.media.css == [CSS_MEDIA_PATH]
        assert info.media.js == [JS_MEDIA_PATH]

    def test_no_private_helper_methods_or_inline_comments_in_component(
        self,
    ) -> None:
        """Verify Tooltip defines no private _-prefixed helper methods or inline comments."""
        own_private_methods = [
            name
            for name, attr in tooltip_module.Tooltip.__dict__.items()
            if name.startswith("_") and not name.startswith("__") and callable(attr)
        ]
        assert not own_private_methods
        py_text = _read_text(path=TOOLTIP_PY_PATH)
        assert "mark_safe" not in py_text
        assert "format_html" not in py_text
        for line in py_text.splitlines():
            assert not line.lstrip().startswith("#")


class TestTooltipParametersAndContext:
    """Verify Tooltip parameter normalization and get_context() shaping."""

    def test_default_parameters_and_context_shaping(self) -> None:
        """Verify default placement, alignment, and context flags when instantiated empty."""
        comp = tooltip_module.Tooltip()
        ctx = comp.get_context()
        assert ctx["placement"] == "top"
        assert ctx["align"] == "center"
        assert ctx["tip_content"] == ""
        assert ctx["has_tip"] is False
        assert ctx["bubble_id"] == ""
        assert ctx["trigger_content"] == ""

    def test_explicit_parameters_and_context_shaping(self) -> None:
        """Verify explicit text, placement, alignment, and bubble ID in context."""
        comp = tooltip_module.Tooltip(
            text="Contextual help text",
            placement="bottom",
            align="end",
            id="custom-tip-id",
            content=safestring.mark_safe("<button>Click</button>"),
        )
        ctx = comp.get_context()
        assert ctx["placement"] == "bottom"
        assert ctx["align"] == "end"
        assert ctx["tip_content"] == "Contextual help text"
        assert ctx["has_tip"] is True
        assert ctx["bubble_id"] == "custom-tip-id"
        assert "<button>Click</button>" in ctx["trigger_content"]

    def test_invalid_placement_and_align_raise_value_error(self) -> None:
        """Verify invalid placement or align values raise ValueError from parameter descriptor."""
        with pytest.raises(expected_exception=ValueError, match="Expected one of"):
            tooltip_module.Tooltip(placement="invalid")
        with pytest.raises(expected_exception=ValueError, match="Expected one of"):
            tooltip_module.Tooltip(align="invalid")


class TestTooltipRenderingAndTemplate:
    """Verify template tag rendering and accessibility attributes."""

    def test_renders_trigger_and_tooltip_bubble(self) -> None:
        """Verify basic {% dds__tooltip %} wraps trigger and renders accessible bubble."""
        html = _render_template(
            source=(
                '{% dds__tooltip text="RtL direction" placement="bottom" %}'
                "<button>Action</button>"
                "{% enddds__tooltip %}"
            )
        ).strip()
        assert (
            '<dds-tooltip class="dds-tooltip" data-state="closed" '
            'data-placement="bottom" data-align="center"' in html
        )
        assert "<button>Action</button>" in html
        assert 'class="dds-tooltip-bubble"' in html
        assert "data-tooltip-bubble" in html
        assert 'role="tooltip"' in html
        assert "hidden" in html
        assert "RtL direction" in html

    def test_empty_tooltip_renders_no_bubble(self) -> None:
        """Verify empty tooltip renders trigger without an empty bubble."""
        html = _render_template(
            source="{% dds__tooltip %}<button>Plain</button>{% enddds__tooltip %}"
        ).strip()
        assert "<button>Plain</button>" in html
        assert "data-tooltip-bubble" not in html

    def test_explicit_id_renders_on_bubble(self) -> None:
        """Verify explicit id renders on data-tooltip-bubble element."""
        html = _render_template(
            source=(
                '{% dds__tooltip text="Help" id="action-tip" %}'
                "<button>Action</button>"
                "{% enddds__tooltip %}"
            )
        ).strip()
        assert 'id="action-tip"' in html

    def test_template_contains_no_filters_or_bem(self) -> None:
        """Verify tooltip.html loads design_components and has zero template filters or BEM."""
        template_text = _read_text(path=TOOLTIP_HTML_PATH)
        assert "{% load design_components %}" in template_text
        assert "|" not in template_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=template_text,
        )
        assert not bem_matches


class TestTooltipStylesheet:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, and formatting in tooltip.css."""

    def test_wrapped_in_layer_blocks_and_sets_root_layout(self) -> None:
        """Verify tooltip.css wraps rules in @layer blocks and sets zero outer margin."""
        css_text = _read_text(path=TOOLTIP_CSS_PATH)
        assert css_text.startswith("@layer blocks {")
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-tooltip",
        )
        assert root_blocks
        assert "position: relative;" in root_blocks[0]
        assert "margin: 0;" in root_blocks[0]

    def test_tier_3_tokens_map_exclusively_from_tier_2_tokens(self) -> None:
        """Verify .dds-tooltip defines --_tooltip-* tokens mapped only from --dds-* tokens."""
        css_text = _read_text(path=TOOLTIP_CSS_PATH)
        assert "--_dds-" not in css_text
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-tooltip",
        )
        root_props = _extract_defined_properties(block_text="\n".join(root_blocks))
        assert root_props
        for token_name, token_val in root_props.items():
            assert token_name.startswith("--_tooltip-")
            assert token_val.startswith("var(--dds-")

        mapped_values = " ".join(root_props.values())
        for expected_family in (
            "--dds-surface-popout-",
            "--dds-text-control-",
            "--dds-space-",
            "--dds-layer-overlay-",
        ):
            assert expected_family in mapped_values


class TestTooltipGalleryAndDocs:
    """Verify co-located gallery.py and index.md for dds__tooltip."""

    def test_gallery_config_renders(self) -> None:
        """Verify gallery.py exports a valid GalleryConfig without first-class variants."""
        reg = _make_registry()
        cfg = gallery.load_gallery_config(
            source_dir=TOOLTIP_DIR,
            component_name=COMPONENT_NAME,
        )
        assert isinstance(cfg, gallery.GalleryConfig)
        assert cfg.group == "Elements"
        assert len(cfg.variants) == 0
        spec = data.CanvasSpec(
            component_name=QUALIFIED_NAME,
        )
        rendered = canvas_service.render_component(
            spec=spec,
            registry=reg,
            raise_errors=True,
        )
        assert 'class="dds-tooltip"' in rendered
        assert 'role="tooltip"' in rendered

    def test_index_md_exists_and_documents_component(self) -> None:
        """Verify index.md exists and documents dds__tooltip with canvas placements."""
        doc_text = _read_text(path=TOOLTIP_INDEX_MD_PATH)
        assert "dds__tooltip" in doc_text
        assert "dds-tooltip" in doc_text
        assert "```canvas" in doc_text
        assert "WCAG 2.1 SC 1.4.13" in doc_text
