"""Tests for namespaced gallery/canvas control query parameters (#135)."""

import pytest
from django.http import QueryDict
from django.test import Client, RequestFactory
from django.urls import reverse

from dj_design_system.components import TagComponent
from dj_design_system.data import ComponentInfo
from dj_design_system.gallery import GalleryConfig, Variant
from dj_design_system.parameters.base import StrParam
from dj_design_system.services.canvas import (
    RESERVED_CANVAS_PARAMS,
    resolve_from_get_params,
)
from dj_design_system.services.canvas import (
    canvas_bg_class as _canvas_bg_class,
)
from dj_design_system.services.canvas import (
    canvas_mode_class as _canvas_mode_class,
)
from dj_design_system.services.control_params import (
    CONTROL_PARAM_NAMES,
    control_param_key,
    declares_param,
    get_control_param,
)
from dj_design_system.services.registry import component_registry
from dj_design_system.views.gallery import get_base_context


pytestmark = pytest.mark.django_db


class CollidingWidget(TagComponent):
    template_format_str = (
        '<div data-variant="{variant}" data-mode="{mode}" '
        'data-theme="{theme}" data-bg="{bg}">{label}</div>'
    )
    variant = StrParam("Widget variant", default="solid")
    mode = StrParam("Widget mode", default="compact")
    theme = StrParam("Widget theme", default="brand")
    bg = StrParam("Widget bg", default="surface")
    label = StrParam("Label", default="Hi")


class PlainWidget(TagComponent):
    template_format_str = "<span>{label}</span>"
    label = StrParam("Label", default="Hi")


@pytest.fixture
def colliding():
    config = GalleryConfig(
        variants=[Variant(name="showcase", kwargs={"label": "Showcase"})]
    )
    info = ComponentInfo(
        component_class=CollidingWidget,
        name="colliding_widget",
        app_label="demo_components",
        relative_path="colliding_widget",
    )
    info.__dict__["gallery_config"] = config
    component_registry._components.append(info)
    yield info
    component_registry._components.remove(info)


@pytest.fixture
def plain():
    config = GalleryConfig(
        variants=[Variant(name="showcase", kwargs={"label": "Showcase"})]
    )
    info = ComponentInfo(
        component_class=PlainWidget,
        name="plain_widget",
        app_label="demo_components",
        relative_path="plain_widget",
    )
    info.__dict__["gallery_config"] = config
    component_registry._components.append(info)
    yield info
    component_registry._components.remove(info)


class TestHelper:
    def test_control_param_key(self):
        assert control_param_key("theme") == "_dds_theme"

    def test_namespaced_wins_over_bare(self):
        q = QueryDict("_dds_theme=dark&theme=light")
        assert get_control_param(q, "theme") == "dark"

    def test_empty_namespaced_is_explicit_default(self):
        """An empty ``_dds_variant`` means "Default" and must not fall back to bare."""
        q = QueryDict("_dds_variant=&variant=other")
        assert get_control_param(q, "variant") == ""

    def test_bare_fallback_enabled(self):
        assert get_control_param(QueryDict("theme=light"), "theme") == "light"

    def test_bare_fallback_disabled(self):
        assert (
            get_control_param(QueryDict("theme=light"), "theme", bare_fallback=False)
            is None
        )

    def test_missing_returns_none(self):
        assert get_control_param(QueryDict(""), "mode") is None

    def test_declares_param(self, colliding):
        assert declares_param(CollidingWidget, "variant")
        assert not declares_param(PlainWidget, "variant")
        assert not declares_param(None, "variant")

    def test_reserved_canvas_params_are_namespaced_only(self):
        assert RESERVED_CANVAS_PARAMS == {
            "component",
            *(f"_dds_{n}" for n in CONTROL_PARAM_NAMES),
        }
        for bare in CONTROL_PARAM_NAMES:
            assert bare not in RESERVED_CANVAS_PARAMS


class TestResolveFromGetParams:
    def test_legacy_bare_variant_still_works_for_plain_component(self, plain):
        spec = resolve_from_get_params(
            QueryDict("component=demo_components__plain_widget&variant=showcase"),
            component_registry,
        )
        assert spec.variant == "showcase"
        assert spec.params == {}

    def test_legacy_bare_controls_not_leaked_as_params_for_plain_component(self, plain):
        spec = resolve_from_get_params(
            QueryDict(
                "component=demo_components__plain_widget&mode=basic&theme=dark&bg=x&label=A"
            ),
            component_registry,
        )
        assert spec.params == {"label": "A"}

    def test_bare_names_are_component_params_when_declared(self, colliding):
        spec = resolve_from_get_params(
            QueryDict(
                "component=demo_components__colliding_widget"
                "&variant=outline&mode=expanded&theme=accent&bg=muted"
            ),
            component_registry,
        )
        assert spec.variant is None
        assert spec.params == {
            "variant": "outline",
            "mode": "expanded",
            "theme": "accent",
            "bg": "muted",
        }

    def test_namespaced_variant_wins_alongside_declared_bare_variant(self, colliding):
        spec = resolve_from_get_params(
            QueryDict(
                "component=demo_components__colliding_widget"
                "&_dds_variant=showcase&variant=outline"
            ),
            component_registry,
        )
        assert spec.variant == "showcase"
        assert spec.params == {"variant": "outline"}

    def test_namespaced_controls_never_become_params(self, colliding):
        spec = resolve_from_get_params(
            QueryDict(
                "component=demo_components__colliding_widget"
                "&_dds_mode=basic&_dds_theme=dark&_dds_bg=x"
            ),
            component_registry,
        )
        assert spec.params == {}


class TestCanvasViewHelpers:
    @pytest.fixture
    def rf(self):
        return RequestFactory()

    def test_mode_namespaced(self, rf):
        req = rf.get("/?_dds_mode=basic")
        assert _canvas_mode_class(req, PlainWidget) == "canvas-wrapper--basic"

    def test_mode_bare_legacy_for_plain_component(self, rf):
        req = rf.get("/?mode=basic")
        assert _canvas_mode_class(req, PlainWidget) == "canvas-wrapper--basic"

    def test_mode_bare_ignored_when_declared(self, rf):
        req = rf.get("/?mode=basic")
        assert _canvas_mode_class(req, CollidingWidget) != "canvas-wrapper--basic"

    def test_mode_namespaced_wins_when_declared(self, rf):
        req = rf.get("/?_dds_mode=basic&mode=expanded")
        assert _canvas_mode_class(req, CollidingWidget) == "canvas-wrapper--basic"

    def test_bg_namespaced(self, rf):
        req = rf.get("/?_dds_bg=dark-grey")
        assert _canvas_bg_class(req, None, PlainWidget) == "canvas-bg-dark-grey"

    def test_bg_bare_legacy_for_plain_component(self, rf):
        req = rf.get("/?bg=dark-grey")
        assert _canvas_bg_class(req, None, PlainWidget) == "canvas-bg-dark-grey"

    def test_bg_bare_ignored_when_declared(self, rf):
        req = rf.get("/?bg=dark-grey")
        assert _canvas_bg_class(req, None, CollidingWidget) != "canvas-bg-dark-grey"

    def test_bg_namespaced_wins_when_declared(self, rf):
        req = rf.get("/?_dds_bg=dark-grey&bg=surface")
        assert _canvas_bg_class(req, None, CollidingWidget) == "canvas-bg-dark-grey"


class TestCanvasIframeView:
    def test_declared_params_render_as_component_values(self, colliding):
        response = Client().get(
            reverse("gallery-canvas-iframe"),
            {
                "component": "demo_components__colliding_widget",
                "variant": "outline",
                "mode": "expanded",
                "theme": "accent",
                "bg": "muted",
            },
        )
        html = response.content.decode()
        assert response.status_code == 200
        assert "gallery-canvas-error" not in html
        assert 'data-variant="outline"' in html
        assert 'data-mode="expanded"' in html
        assert 'data-theme="accent"' in html
        assert 'data-bg="muted"' in html

    def test_controls_and_params_coexist(self, colliding):
        response = Client().get(
            reverse("gallery-canvas-iframe"),
            {
                "component": "demo_components__colliding_widget",
                "_dds_variant": "showcase",
                "_dds_mode": "basic",
                "_dds_theme": "default",
                "_dds_bg": "dark-grey",
                "variant": "outline",
                "theme": "accent",
            },
        )
        html = response.content.decode()
        assert "gallery-canvas-error" not in html
        assert 'data-variant="outline"' in html
        assert 'data-theme="accent"' in html
        assert 'data-label="' not in html
        assert "Showcase" in html  # variant kwargs applied
        assert "canvas-wrapper--basic" in html
        assert "canvas-bg-dark-grey" in html

    def test_legacy_bare_controls_work_for_plain_component(self, plain):
        response = Client().get(
            reverse("gallery-canvas-iframe"),
            {
                "component": "demo_components__plain_widget",
                "variant": "showcase",
                "mode": "basic",
                "bg": "dark-grey",
            },
        )
        html = response.content.decode()
        assert "gallery-canvas-error" not in html
        assert "Showcase" in html
        assert "canvas-wrapper--basic" in html
        assert "canvas-bg-dark-grey" in html


class TestGalleryBaseContext:
    @pytest.fixture
    def rf(self):
        return RequestFactory()

    def test_namespaced_controls(self, rf):
        ctx = get_base_context(rf.get("/?_dds_theme=dark&_dds_variant=showcase"))
        assert ctx["active_theme"] == "dark"
        assert ctx["active_variant"] == "showcase"

    def test_bare_controls_on_navigation_urls(self, rf):
        ctx = get_base_context(rf.get("/?theme=dark&variant=showcase"))
        assert ctx["active_theme"] == "dark"
        assert ctx["active_variant"] == "showcase"

    def test_bare_names_are_component_values_on_sandbox_submission(self, rf):
        """On a sandbox submission, a bare ``variant``/``theme`` is a component value."""
        ctx = get_base_context(
            rf.get("/?_iss=1&_dds_variant=showcase&variant=outline&theme=accent")
        )
        assert ctx["active_variant"] == "showcase"
        assert ctx["active_theme"] != "accent"

    def test_empty_namespaced_variant_means_default(self, rf):
        ctx = get_base_context(rf.get("/?_iss=1&_dds_variant=&variant=outline"))
        assert ctx["active_variant"] is None


class TestComponentViewSandbox:
    def _url(self):
        return reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "colliding_widget"},
        )

    def test_navigation_variant_selects_preset(self, colliding):
        response = Client().get(f"{self._url()}?variant=showcase")
        assert response.status_code == 200
        assert response.context["active_variant"].name == "showcase"

    def test_sandbox_submission_bare_variant_is_component_value(self, colliding):
        response = Client().get(
            f"{self._url()}?_iss=1&_dds_theme=default&variant=outline&label=X"
        )
        assert response.status_code == 200
        assert response.context["active_variant"] is None
        assert response.context["form"].is_valid()
        assert "variant=outline" in response.context["canvas_iframe_url"]

    def test_sandbox_submission_bare_theme_is_component_value(self, colliding):
        response = Client().get(
            f"{self._url()}?_iss=1&_dds_theme=default&theme=accent&label=X"
        )
        assert response.status_code == 200
        assert response.context["active_theme"] == "default"
        assert "theme=accent" in response.context["canvas_iframe_url"]
        assert "_dds_theme=default" in response.context["canvas_iframe_url"]

    def test_sandbox_submission_empty_variant_resets_to_default(self, colliding):
        response = Client().get(
            f"{self._url()}?_iss=1&_dds_theme=default&_dds_variant=&variant=outline"
        )
        assert response.status_code == 200
        assert response.context["active_variant"] is None
