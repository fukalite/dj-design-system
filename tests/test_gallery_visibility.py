"""Tests for GALLERY_EXCLUDE_APPS and GALLERY_SHOW_BUILTIN_COMPONENTS."""

import json
from contextlib import contextmanager

import pytest
from django import template
from django.test import RequestFactory, override_settings
from django.urls import reverse

from dj_design_system.api.views import ComponentRegistryView
from dj_design_system.services.navigation import (
    _build_navigation,
    build_search_index,
    clear_navigation_cache,
)
from dj_design_system.services.registry import ComponentRegistry, component_registry
from dj_design_system.services.visibility import (
    get_gallery_components,
    get_hidden_apps,
    is_app_visible,
)
from dj_design_system.settings import dds_settings
from tests.conftest import discover_app_into_registry


pytestmark = pytest.mark.django_db

BUILTINS = {
    "fixture_vis/crumb.py": """
        from dj_design_system.components import TagComponent


        class CrumbComponent(TagComponent):
            template_format_str = "<span>builtin crumb</span>"
    """
}


@contextmanager
def dds(**options):
    """Override ``DJ_DESIGN_SYSTEM`` with the given options.

    The navigation tree is cached per process, so it is rebuilt on the way in
    and out.
    """
    clear_navigation_cache()
    try:
        with override_settings(DJ_DESIGN_SYSTEM=options):
            yield
    finally:
        clear_navigation_cache()


@pytest.fixture()
def registry(builtin_modules):
    """Built-ins plus two consumer apps."""
    builtin_modules(BUILTINS)
    reg = ComponentRegistry()
    discover_app_into_registry(reg, "dj_design_system", "dj_design_system")
    discover_app_into_registry(
        reg, "example_project.demo_components", "demo_components"
    )
    discover_app_into_registry(reg, "example_project.demo_single", "demo_single")
    return reg


@pytest.fixture()
def global_builtins(builtin_modules):
    """Temporarily add the fixture built-ins to the global registry."""
    builtin_modules(BUILTINS)
    before = list(component_registry._components)
    discover_app_into_registry(
        component_registry, "dj_design_system", "dj_design_system"
    )
    yield
    component_registry._components[:] = before


def _apps(infos) -> set[str]:
    return {i.app_label for i in infos}


def _nav_apps(nav_tree) -> set[str]:
    return {node.slug for node in nav_tree}


class TestDefaults:
    def test_exclude_apps_defaults_to_empty(self):
        with dds():
            assert dds_settings.GALLERY_EXCLUDE_APPS == []

    def test_show_builtins_defaults_to_false(self):
        with dds():
            assert dds_settings.GALLERY_SHOW_BUILTIN_COMPONENTS is False


class TestHiddenApps:
    def test_builtins_hidden_by_default(self):
        with dds():
            assert get_hidden_apps() == {"dj_design_system"}
            assert not is_app_visible("dj_design_system")
            assert is_app_visible("demo_components")

    def test_builtins_hidden_when_exclude_list_omits_them(self):
        with dds(GALLERY_EXCLUDE_APPS=["demo_single"]):
            assert get_hidden_apps() == {"dj_design_system", "demo_single"}

    def test_builtins_shown_when_enabled(self):
        with dds(GALLERY_SHOW_BUILTIN_COMPONENTS=True):
            assert get_hidden_apps() == set()
            assert is_app_visible("dj_design_system")

    def test_builtins_hidden_when_enabled_but_excluded(self):
        with dds(
            GALLERY_SHOW_BUILTIN_COMPONENTS=True,
            GALLERY_EXCLUDE_APPS=["dj_design_system"],
        ):
            assert not is_app_visible("dj_design_system")

    def test_consumer_apps_can_be_hidden(self):
        with dds(GALLERY_EXCLUDE_APPS=["demo_single"]):
            assert not is_app_visible("demo_single")
            assert is_app_visible("demo_components")


class TestGalleryComponents:
    def test_default_hides_builtins(self, registry):
        with dds():
            infos = get_gallery_components(registry)
        assert _apps(infos) == {"demo_components", "demo_single"}

    def test_show_builtins(self, registry):
        with dds(GALLERY_SHOW_BUILTIN_COMPONENTS=True):
            infos = get_gallery_components(registry)
        assert _apps(infos) == {"dj_design_system", "demo_components", "demo_single"}

    def test_excluded_consumer_app(self, registry):
        with dds(
            GALLERY_SHOW_BUILTIN_COMPONENTS=True, GALLERY_EXCLUDE_APPS=["demo_single"]
        ):
            infos = get_gallery_components(registry)
        assert _apps(infos) == {"dj_design_system", "demo_components"}


class TestNavigationAndSearch:
    def test_nav_and_search_exclude_hidden_apps(self, registry):
        with dds(GALLERY_EXCLUDE_APPS=["demo_single"]):
            nav = _build_navigation(
                components=registry.list_all(), app_component_paths={}
            )
        assert _nav_apps(nav) == {"demo_components"}
        search_apps = {entry["url"].split("/")[2] for entry in build_search_index(nav)}
        assert search_apps == {"demo_components"}

    def test_nav_includes_builtins_when_enabled(self, registry):
        with dds(GALLERY_SHOW_BUILTIN_COMPONENTS=True):
            nav = _build_navigation(
                components=registry.list_all(), app_component_paths={}
            )
        assert "dj_design_system" in _nav_apps(nav)

    def test_nav_excludes_hidden_app_markdown_docs(self, registry, tmp_path):
        (tmp_path / "readme.md").write_text("# Docs only\n")
        with dds(GALLERY_EXCLUDE_APPS=["docs_app"]):
            nav = _build_navigation(
                components=registry.list_all(),
                app_component_paths={"docs_app": tmp_path},
            )
        assert "docs_app" not in _nav_apps(nav)


class TestViews:
    def test_hidden_app_node_returns_404(self, client):
        url = reverse("gallery-node-root", kwargs={"app_label": "demo_single"})
        assert client.get(url).status_code == 200
        with dds(GALLERY_EXCLUDE_APPS=["demo_single"]):
            assert client.get(url).status_code == 404

    def test_hidden_component_node_returns_404(self, client, global_builtins):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "dj_design_system", "path": "fixture_vis/crumb"},
        )
        with dds():
            assert client.get(url).status_code == 404
        with dds(GALLERY_SHOW_BUILTIN_COMPONENTS=True):
            assert client.get(url).status_code == 200

    def test_index_total_excludes_hidden_components(self, client, global_builtins):
        with dds(GALLERY_SHOW_BUILTIN_COMPONENTS=True):
            shown = client.get(reverse("gallery")).context["total_components"]
        with dds():
            default = client.get(reverse("gallery")).context["total_components"]
        with dds(GALLERY_EXCLUDE_APPS=["demo_single"]):
            fewer = client.get(reverse("gallery")).context["total_components"]

        assert shown == len(component_registry.list_all())
        assert default == shown - 1
        assert fewer == default - len(component_registry.list_by_app("demo_single"))

    def test_index_search_index_excludes_hidden_apps(self, client, global_builtins):
        with dds():
            index = client.get(reverse("gallery")).context["search_index"]
        assert not any("/dj_design_system/" in entry["url"] for entry in index)


class TestApi:
    def _listed_apps(self, registry) -> set[str]:
        request = RequestFactory().get("/api/registry/")
        response = ComponentRegistryView.as_view(registry=registry)(request)
        return {item["app_label"] for item in json.loads(response.content)}

    def test_api_hides_builtins_by_default(self, registry):
        with dds():
            assert self._listed_apps(registry) == {"demo_components", "demo_single"}

    def test_api_excludes_listed_apps(self, registry):
        with dds(
            GALLERY_SHOW_BUILTIN_COMPONENTS=True, GALLERY_EXCLUDE_APPS=["demo_single"]
        ):
            assert self._listed_apps(registry) == {
                "dj_design_system",
                "demo_components",
            }


class TestHiddenComponentsStillRender:
    def test_hidden_builtin_renders_as_tag(self, registry):
        library = template.Library()
        registry.register_templatetags(library)
        engine = template.Engine()
        engine.template_builtins.append(library)
        with dds(GALLERY_EXCLUDE_APPS=["demo_single"]):
            html = engine.from_string("{% dds__fixture_vis__crumb %}{% pill %}").render(
                template.Context()
            )
        assert "builtin crumb" in html
        assert "pill" in html
