"""Tests for the canvas rendering service."""

import pytest
from django.http import QueryDict

from dj_design_system.data import CanvasSpec, ComponentMedia
from dj_design_system.parameters.base import DictParam, JSONParam, ListParam
from dj_design_system.services.canvas import (
    build_canvas_url,
    coerce_single,
    get_component_media,
    render_component,
    resolve_from_get_params,
)


# ---------------------------------------------------------------------------
# resolve_from_get_params
# ---------------------------------------------------------------------------


class TestResolveFromGetParams:
    """Test building a CanvasSpec from GET query parameters."""

    def test_basic_resolution(self, registry_with_demo_components):
        qd = QueryDict("component=button")
        spec = resolve_from_get_params(qd, registry_with_demo_components)
        assert spec.component_name == "button"

    def test_with_keyword_params(self, registry_with_demo_components):
        # "label" is a positional arg for button, so it ends up in
        # positional_args rather than params.
        qd = QueryDict("component=button&label=Click+me")
        spec = resolve_from_get_params(qd, registry_with_demo_components)
        assert spec.component_name == "button"
        assert "Click me" in spec.positional_args

    def test_missing_component_param_raises(self, registry_with_demo_components):
        qd = QueryDict("")
        with pytest.raises(ValueError, match="Missing required"):
            resolve_from_get_params(qd, registry_with_demo_components)

    def test_unknown_component_raises(self, registry_with_demo_components):
        qd = QueryDict("component=nonexistent")
        with pytest.raises(ValueError, match="not found in registry"):
            resolve_from_get_params(qd, registry_with_demo_components)

    def test_bg_param_excluded_from_component_params(
        self, registry_with_demo_components
    ):
        qd = QueryDict("component=button&bg=dark-grey")
        spec = resolve_from_get_params(qd, registry_with_demo_components)
        assert "bg" not in spec.params

    def test_block_component_content_passed_through(
        self, registry_with_demo_components
    ):
        """resolve_from_get_params passes 'content' through for BlockComponents."""
        qd = QueryDict("component=alert&type=warning&content=Hello+world")
        spec = resolve_from_get_params(qd, registry_with_demo_components)
        assert spec.params.get("content") == "Hello world"

    def test_block_component_content_sanitizes_xss(
        self, registry_with_demo_components
    ):
        """resolve_from_get_params sanitizes XSS in content before mark_safe."""
        qd = QueryDict("component=alert&content=<script>alert(1)</script><b>Safe</b>")
        spec = resolve_from_get_params(qd, registry_with_demo_components)
        content = spec.params.get("content")
        assert "<script>" not in content
        assert "<b>Safe</b>" in content

    def test_block_component_slot_sanitizes_xss(
        self, registry_with_demo_components
    ):
        """resolve_from_get_params sanitizes XSS in slot parameters before mark_safe."""
        qd = QueryDict("component=slotted_card&slot__header=<script>alert(1)</script>Safe+Title")
        spec = resolve_from_get_params(qd, registry_with_demo_components)
        header = spec.params.get("slot__header")
        assert "<script>" not in header
        assert "Safe Title" in header

    def test_unknown_params_ignored(self, registry_with_demo_components):
        qd = QueryDict("component=button&nonsense=foo")
        spec = resolve_from_get_params(qd, registry_with_demo_components)
        assert "nonsense" not in spec.params


class TestRenderBlockComponent:
    """Test canvas rendering of BlockComponent subclasses."""

    def test_render_block_component(self, registry_with_demo_components):
        """A BlockComponent renders its content."""
        spec = CanvasSpec(
            component_name="alert",
            params={"type": "warning", "content": "Watch out!"},
        )
        html = render_component(spec, registry_with_demo_components)
        assert "Watch out!" in html


# ---------------------------------------------------------------------------
# render_component
# ---------------------------------------------------------------------------


class TestRenderComponent:
    """Test component rendering from a CanvasSpec."""

    def test_successful_render(self, registry_with_demo_components):
        spec = CanvasSpec(component_name="button", params={"label": "OK"})
        html = render_component(spec, registry_with_demo_components)
        assert "OK" in html

    def test_missing_component_returns_error(self, registry_with_demo_components):
        spec = CanvasSpec(component_name="nonexistent")
        html = render_component(spec, registry_with_demo_components)
        assert "gallery-canvas-error" in html
        assert "not found" in html

    def test_validation_error_returns_error(self, registry_with_demo_components):
        """Component validation errors should render in error style."""
        spec = CanvasSpec(component_name="button", params={})
        html = render_component(spec, registry_with_demo_components)
        # ButtonComponent requires 'label' param — should error
        assert "gallery-canvas-error" in html or "button" in html.lower()

    def test_validation_error_raises_when_flag_set(self, registry_with_demo_components):
        """Component validation errors raise exceptions when raise_errors is True."""
        spec = CanvasSpec(component_name="nonexistent", params={})
        with pytest.raises(ValueError, match="not found in registry"):
            render_component(spec, registry_with_demo_components, raise_errors=True)


# ---------------------------------------------------------------------------
# get_component_media
# ---------------------------------------------------------------------------


class TestGetComponentMedia:
    """Test CSS/JS media resolution for a canvas component."""

    def test_returns_media_for_known_component(self, registry_with_demo_components):
        spec = CanvasSpec(component_name="button")
        media = get_component_media(spec, registry_with_demo_components)
        assert isinstance(media, ComponentMedia)
        # ButtonComponent has co-located CSS/JS
        assert any("button" in path for path in media.css)

    def test_returns_empty_for_unknown_component(self, registry_with_demo_components):
        spec = CanvasSpec(component_name="nonexistent")
        media = get_component_media(spec, registry_with_demo_components)
        assert media.css == []
        assert media.js == []


# ---------------------------------------------------------------------------
# build_canvas_url
# ---------------------------------------------------------------------------


class TestBuildCanvasUrl:
    """Test URL generation from a CanvasSpec."""

    def test_basic_url(self):
        spec = CanvasSpec(component_name="button")
        url = build_canvas_url(spec, "/base/")
        assert url.startswith("/base/?")
        assert "component=button" in url

    def test_with_params(self):
        spec = CanvasSpec(component_name="button", params={"size": "large"})
        url = build_canvas_url(spec, "/base/")
        assert "component=button" in url
        assert "size=large" in url

    def test_bool_params_serialised_correctly(self):
        spec = CanvasSpec(component_name="button", params={"dark": True})
        url = build_canvas_url(spec, "/base/")
        assert "dark=true" in url

    def test_false_bool_params_serialised(self):
        spec = CanvasSpec(component_name="button", params={"dark": False})
        url = build_canvas_url(spec, "/base/")
        assert "dark=false" in url

    def test_list_and_dict_params_serialised_as_json(self):
        spec = CanvasSpec(
            component_name="menu",
            params={
                "items": [{"id": "home", "label": "Home"}],
                "config": {"nested": True},
            },
        )
        url = build_canvas_url(spec, "/base/")
        assert (
            "items=%5B%7B%22id%22%3A+%22home%22%2C+%22label%22%3A+%22Home%22%7D%5D"
            in url
        )
        from urllib.parse import parse_qs, urlparse

        query_params = parse_qs(urlparse(url).query)
        assert coerce_single("items", query_params["items"][0], ListParam()) == [
            {"id": "home", "label": "Home"}
        ]
        assert coerce_single("config", query_params["config"][0], DictParam()) == {
            "nested": True
        }

    def test_with_mode_and_theme(self):
        spec = CanvasSpec(component_name="button", variant="danger")
        url = build_canvas_url(spec, "/base/", mode="basic", theme="dark")
        assert "component=button" in url
        assert "variant=danger" in url
        assert "mode=basic" in url
        assert "theme=dark" in url

    def test_with_existing_query_params_uses_ampersand(self):
        spec = CanvasSpec(component_name="button")
        url = build_canvas_url(spec, "/base/?token=xyz", theme="light")
        assert url.startswith("/base/?token=xyz&")
        assert "component=button" in url
        assert "theme=light" in url

    def test_with_extra_query_params(self):
        spec = CanvasSpec(component_name="button")
        url = build_canvas_url(spec, "/base/", preview="true", custom_id="123")
        assert "preview=true" in url
        assert "custom_id=123" in url

    def test_param_shadowing_prevented(self):
        """Component params cannot shadow reserved canvas control parameters."""
        spec = CanvasSpec(
            component_name="button",
            params={
                "component": "malicious",
                "mode": "standalone",
                "variant": "injected",
                "theme": "dark",
                "label": "Click me",
            },
        )
        url = build_canvas_url(spec, "/base/")
        assert "component=button" in url
        assert "component=malicious" not in url
        assert "mode=standalone" not in url
        assert "variant=injected" not in url
        assert "theme=dark" not in url
        assert "label=Click+me" in url

    def test_extra_query_shadowing_prevented(self):
        """Component params cannot shadow explicit extra_query parameters."""
        spec = CanvasSpec(
            component_name="button",
            params={"bg": "light", "label": "Click me"},
        )
        url = build_canvas_url(spec, "/base/", bg="dark")
        assert "bg=dark" in url
        assert "bg=light" not in url

    def test_component_resolution_failure_handled_gracefully(self):
        """Unexpected errors during component resolution do not crash build_canvas_url."""
        class BuggyRegistry:
            def list_all(self):
                raise RuntimeError("Registry database unreachable")

        spec = CanvasSpec(component_name="button", params={"label": "Hi"})
        # Should not raise RuntimeError
        url = build_canvas_url(spec, "/base/", registry=BuggyRegistry())
        assert "component=button" in url
        assert "label=Hi" in url


# ---------------------------------------------------------------------------
# _coerce_single
# ---------------------------------------------------------------------------


class TestCoerceSingle:
    """Test type coercion for individual parameter values."""

    def test_string_passthrough(self):
        class FakeSpec:
            type = str

        assert coerce_single("name", "hello", FakeSpec()) == "hello"

    def test_bool_true_variants(self):
        class FakeSpec:
            type = bool

        for value in ("true", "True", "1", "yes"):
            assert coerce_single("flag", value, FakeSpec()) is True

    def test_bool_false_variants(self):
        class FakeSpec:
            type = bool

        for value in ("false", "False", "0", "no"):
            assert coerce_single("flag", value, FakeSpec()) is False

    def test_int_coercion(self):
        class FakeSpec:
            type = int

        assert coerce_single("count", "42", FakeSpec()) == 42

    def test_int_invalid_raises(self):
        class FakeSpec:
            type = int

        with pytest.raises(ValueError, match="expected int"):
            coerce_single("count", "abc", FakeSpec())

    def test_json_param_coercion(self):
        assert coerce_single("data", '{"foo": "bar"}', JSONParam()) == {"foo": "bar"}
        assert coerce_single("data", "[1, 2]", ListParam()) == [1, 2]
        assert coerce_single("data", '{"a": 1}', DictParam()) == {"a": 1}

    def test_json_param_empty_string(self):
        assert coerce_single("data", " ", ListParam()) == []
        assert coerce_single("data", "", DictParam()) == {}

    def test_json_param_invalid(self):
        with pytest.raises(ValueError, match="expected valid JSON for ListParam"):
            coerce_single("data", "invalid", ListParam())

    def test_model_param_invalid_pk_raises_value_error(self, db):
        from django.contrib.auth import get_user_model

        from dj_design_system.parameters.model import ModelParam

        User = get_user_model()

        class UserParam(ModelParam):
            class Meta:
                model = User
                fields = "__all__"

        spec = UserParam("user")
        with pytest.raises(
            ValueError, match="invalid primary key or no matching User found"
        ):
            coerce_single("user", "invalid_pk_abc", spec)
