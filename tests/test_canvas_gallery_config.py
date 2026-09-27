"""Tests for Smart Hybrid canvas_template and callable parameter resolution in canvas services."""

import pytest
from django.http import QueryDict

from dj_design_system.components import TagComponent
from dj_design_system.data import CanvasSpec, ComponentInfo, GalleryParameter
from dj_design_system.gallery import GalleryConfig, Variant
from dj_design_system.parameters.base import StrParam
from dj_design_system.services.canvas import (
    build_canvas_url,
    render_component,
    resolve_from_get_params,
)
from dj_design_system.services.registry import ComponentRegistry


class DummyButton(TagComponent):
    template_format_str = '<button class="btn {theme}">{label}</button>'
    label = StrParam("Button label", default="Default")
    theme = StrParam("Button theme", default="primary")


def create_test_registry(config: GalleryConfig | None = None) -> ComponentRegistry:
    """Create a registry containing a DummyButton with the given GalleryConfig."""
    reg = ComponentRegistry()
    info = ComponentInfo(
        component_class=DummyButton,
        name="dummy_button",
        app_label="test_app",
        relative_path="",
    )
    if config is not None:
        info.__dict__["gallery_config"] = config
    reg._components.append(info)
    return reg


class TestCanvasSmartHybridTemplate:
    """Tests for Smart Hybrid canvas_template wrapping and raw rendering."""

    def test_wrapper_mode_replaces_component_placeholder(self):
        config = GalleryConfig(
            canvas_template='<div class="shell">{{ component }}</div>'
        )
        reg = create_test_registry(config)
        spec = CanvasSpec(
            component_name="dummy_button",
            params={"label": "Click me", "theme": "danger"},
        )

        output = render_component(spec, reg)
        assert '<div class="shell">' in output
        assert '<button class="btn danger">Click me</button>' in output
        assert "</div>" in output
        # Ensure component HTML is not escaped
        assert "&lt;button" not in output

    def test_wrapper_mode_with_extra_context(self):
        config = GalleryConfig(
            canvas_template='<div class="shell"><header>{{ header }}</header>{{ component }}</div>',
            extra_context={"header": "Section Title"},
        )
        reg = create_test_registry(config)
        spec = CanvasSpec(
            component_name="dummy_button",
            params={"label": "Go"},
        )

        output = render_component(spec, reg)
        assert "<header>Section Title</header>" in output
        assert '<button class="btn primary">Go</button>' in output

    def test_raw_template_mode_when_placeholder_absent(self):
        config = GalleryConfig(
            canvas_template='<div class="banner"><span>Static Banner: {{ label }}</span></div>',
        )
        reg = create_test_registry(config)
        spec = CanvasSpec(
            component_name="dummy_button",
            params={"label": "Important Notice"},
        )

        output = render_component(spec, reg)
        assert '<div class="banner"><span>Static Banner: Important Notice</span></div>' in output
        # In raw mode without {{ component }}, the default component tag is not automatically rendered
        assert '<button class="btn' not in output

    def test_variant_canvas_template_overrides_config_template(self):
        config = GalleryConfig(
            canvas_template='<div class="config-wrap">{{ component }}</div>',
            variants=[
                Variant(
                    name="custom",
                    canvas_template='<div class="variant-wrap">{{ component }}</div>',
                ),
            ],
        )
        reg = create_test_registry(config)
        spec = CanvasSpec(
            component_name="dummy_button",
            params={"label": "Test"},
            variant="custom",
        )

        output = render_component(spec, reg)
        assert '<div class="variant-wrap">' in output
        assert '<div class="config-wrap">' not in output
        assert '<button class="btn primary">Test</button>' in output

    def test_variant_extra_context_merges_with_config(self):
        config = GalleryConfig(
            canvas_template='<div class="wrap">{{ prefix }} {{ suffix }}: {{ component }}</div>',
            extra_context={"prefix": "Hello", "suffix": "World"},
            variants=[
                Variant(
                    name="custom",
                    extra_context={"suffix": "Universe"},
                ),
            ],
        )
        reg = create_test_registry(config)
        spec = CanvasSpec(
            component_name="dummy_button",
            params={"label": "Test"},
            variant="custom",
        )

        output = render_component(spec, reg)
        assert "Hello Universe:" in output

    def test_no_canvas_template_renders_normally(self):
        config = GalleryConfig()
        reg = create_test_registry(config)
        spec = CanvasSpec(
            component_name="dummy_button",
            params={"label": "Plain Button"},
        )

        output = render_component(spec, reg)
        assert output == '<button class="btn primary">Plain Button</button>'


class TestCanvasCallableResolution:
    """Tests for resolving callable parameters and extra_context at render time."""

    def test_param_defaults_callable_evaluated(self):
        call_count = 0

        def get_dynamic_label():
            nonlocal call_count
            call_count += 1
            return f"Dynamic #{call_count}"

        config = GalleryConfig(
            param_defaults={"label": get_dynamic_label},
        )
        reg = create_test_registry(config)
        # Omit label so param_defaults is used
        spec = CanvasSpec(component_name="dummy_button", params={})

        output1 = render_component(spec, reg)
        assert "Dynamic #1" in output1

        output2 = render_component(spec, reg)
        assert "Dynamic #2" in output2

    def test_spec_params_callable_evaluated(self):
        config = GalleryConfig()
        reg = create_test_registry(config)
        spec = CanvasSpec(
            component_name="dummy_button",
            params={"label": lambda: "Computed from Param"},
        )

        output = render_component(spec, reg)
        assert "Computed from Param" in output

    def test_variant_kwargs_callable_evaluated(self):
        config = GalleryConfig(
            variants=[
                Variant(
                    name="dyn",
                    kwargs={"label": lambda: "From Variant Callable"},
                ),
            ],
        )
        reg = create_test_registry(config)
        spec = CanvasSpec(
            component_name="dummy_button",
            params={},
            variant="dyn",
        )

        output = render_component(spec, reg)
        assert "From Variant Callable" in output

    def test_gallery_parameter_callable_evaluated(self):
        config = GalleryConfig()
        reg = create_test_registry(config)
        spec = CanvasSpec(
            component_name="dummy_button",
            params={
                "label": GalleryParameter(value=lambda: "From GalleryParameter"),
            },
        )

        output = render_component(spec, reg)
        assert "From GalleryParameter" in output

    def test_extra_context_callable_evaluated(self):
        config = GalleryConfig(
            canvas_template='<div class="shell"><span>{{ now }}</span>{{ component }}</div>',
            extra_context={"now": lambda: "2026-09-27"},
        )
        reg = create_test_registry(config)
        spec = CanvasSpec(component_name="dummy_button", params={"label": "Hi"})

        output = render_component(spec, reg)
        assert "<span>2026-09-27</span>" in output

    def test_canvas_template_error_handling(self):
        config = GalleryConfig(
            canvas_template='<div>{% invalid_tag %}</div>',
        )
        reg = create_test_registry(config)
        spec = CanvasSpec(component_name="dummy_button", params={})

        with pytest.raises(Exception):
            render_component(spec, reg, raise_errors=True)

        error_html = render_component(spec, reg, raise_errors=False)
        assert 'class="gallery-canvas-error"' in error_html


class TestCanvasVariantIntegration:
    """Tests for variant handling in resolve_from_get_params, build_canvas_url, and render_component."""

    def test_resolve_from_get_params_extracts_variant(self):
        reg = create_test_registry()
        qd = QueryDict("component=dummy_button&variant=danger&label=Delete")
        spec = resolve_from_get_params(qd, reg)

        assert spec.component_name == "dummy_button"
        assert spec.variant == "danger"
        assert spec.params.get("label") == "Delete"
        assert "variant" not in spec.params

    def test_build_canvas_url_includes_variant(self):
        spec = CanvasSpec(
            component_name="dummy_button",
            params={"label": "Click"},
            variant="secondary",
        )
        url = build_canvas_url(spec, "/canvas/")
        assert "component=dummy_button" in url
        assert "variant=secondary" in url
        assert "label=Click" in url

    def test_unknown_variant_raises_when_requested(self):
        config = GalleryConfig(
            variants=[Variant(name="primary")],
        )
        reg = create_test_registry(config)
        spec = CanvasSpec(
            component_name="dummy_button",
            variant="nonexistent",
        )

        with pytest.raises(ValueError, match="Variant 'nonexistent' not found"):
            render_component(spec, reg, raise_errors=True)

        error_html = render_component(spec, reg, raise_errors=False)
        assert "gallery-canvas-error" in error_html
        assert "Variant &#x27;nonexistent&#x27; not found" in error_html or "Variant 'nonexistent' not found" in error_html

    def test_variant_positional_args_used_when_not_in_spec(self):
        class ButtonWithPositional(TagComponent):
            template_format_str = '<button class="{theme}">{label}</button>'
            label = StrParam("Label")
            theme = StrParam("Theme", default="btn")

            @classmethod
            def get_positional_args(cls) -> list[str]:
                return ["label"]

        reg = ComponentRegistry()
        cfg = GalleryConfig(
            variants=[
                Variant(name="warn", positional_args=("Caution",)),
            ]
        )
        info = ComponentInfo(
            component_class=ButtonWithPositional,
            name="button_pos",
            app_label="test_app",
            relative_path="",
        )
        info.__dict__["gallery_config"] = cfg
        reg._components.append(info)

        spec = CanvasSpec(component_name="button_pos", variant="warn")
        output = render_component(spec, reg)
        assert '<button class="btn">Caution</button>' in output
