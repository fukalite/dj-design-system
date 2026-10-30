"""Tests for the gallery views."""

import copy
import inspect
from urllib.parse import parse_qs, urlsplit

import pytest
from django.contrib.auth.models import Permission
from django.test import override_settings
from django.urls import reverse

from dj_design_system.components import BlockComponent
from dj_design_system.data import ParamRowData
from dj_design_system.forms import build_component_form
from dj_design_system.parameters.base import JSONParam, StrParam
from dj_design_system.services.gallery_context import build_param_rows
from dj_design_system.services.navigation import (
    build_breadcrumbs,
    find_node,
)
from dj_design_system.views import (
    canvas as canvas_views,
)
from dj_design_system.views import (
    component as component_views,
)
from dj_design_system.views import (
    gallery as gallery_views,
)
from dj_design_system.views import (
    gallery_index,
    get_base_context,
)


def _get_nav_tree():
    """Build and return the current navigation tree."""
    return get_base_context()["nav_tree"]


pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# URL resolution
# ---------------------------------------------------------------------------


class TestURLPatterns:
    """Test that URL patterns resolve correctly."""

    def test_gallery_index(self):
        assert reverse("gallery") == "/dds/"

    def test_gallery_node_root(self):
        url = reverse("gallery-node-root", kwargs={"app_label": "myapp"})
        assert url == "/dds/myapp/"

    def test_gallery_node_nested(self):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "myapp", "path": "elements/cards"},
        )
        assert url == "/dds/myapp/elements/cards/"

    def test_gallery_node_component(self):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "myapp", "path": "elements/icon"},
        )
        assert url == "/dds/myapp/elements/icon/"

    def test_gallery_node_document(self):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "myapp", "path": "elements/icon/accessibility"},
        )
        assert url == "/dds/myapp/elements/icon/accessibility/"


# ---------------------------------------------------------------------------
# build_breadcrumbs
# ---------------------------------------------------------------------------


class TestBuildBreadcrumbs:
    """Test the breadcrumb builder."""

    def test_simple_breadcrumbs(self):
        crumbs = build_breadcrumbs("myapp", [], "Button")
        assert len(crumbs) == 3
        assert crumbs[0]["label"] == "Gallery"
        assert crumbs[1]["label"] == "Myapp"
        assert crumbs[2]["label"] == "Button"
        assert "url" not in crumbs[2]

    def test_nested_breadcrumbs(self):
        crumbs = build_breadcrumbs("myapp", ["elements", "cards"], "Icon")
        assert len(crumbs) == 5
        assert crumbs[0]["label"] == "Gallery"
        assert crumbs[1]["label"] == "Myapp"
        assert crumbs[2]["label"] == "Elements"
        assert crumbs[3]["label"] == "Cards"
        assert crumbs[4]["label"] == "Icon"
        # All except last should have urls
        for crumb in crumbs[:-1]:
            assert "url" in crumb


# ---------------------------------------------------------------------------
# find_node
# ---------------------------------------------------------------------------


class TestFindNode:
    """Test node lookup in the navigation tree."""

    def test_finds_app_node(self):
        nav_tree = _get_nav_tree()
        if not nav_tree:
            pytest.skip("No apps with components registered")
        app = nav_tree[0]
        found = find_node(nav_tree, app.slug, [])
        assert found is app

    def test_returns_none_for_unknown_app(self):
        nav_tree = _get_nav_tree()
        assert find_node(nav_tree, "nonexistent_app_xyz", []) is None

    def test_returns_none_for_unknown_child(self):
        nav_tree = _get_nav_tree()
        if not nav_tree:
            pytest.skip("No apps with components registered")
        app = nav_tree[0]
        assert find_node(nav_tree, app.slug, ["nonexistent_child"]) is None


# ---------------------------------------------------------------------------
# View integration tests (via Django test client)
# ---------------------------------------------------------------------------


class TestGalleryIndexView:
    """Test the gallery index page."""

    def test_index_returns_200(self, client):
        response = client.get(reverse("gallery"))
        assert response.status_code == 200

    def test_index_contains_design_system_name(self, client):
        response = client.get(reverse("gallery"))
        assert (
            b"Design System" in response.content or b"design_system" in response.content
        )

    def test_index_has_nav_tree(self, client):
        response = client.get(reverse("gallery"))
        assert "nav_tree" in response.context


class TestGalleryComponentView:
    """Test the component detail page."""

    def test_component_returns_200(self, client):
        """Test with a known component from dw_design_system."""
        nav_tree = _get_nav_tree()
        # Find the first component
        component = None
        for app in nav_tree:
            for child in app.children:
                if child.is_component:
                    component = child
                    break
                for grandchild in getattr(child, "children", []):
                    if grandchild.is_component:
                        component = grandchild
                        break
                if component:
                    break
            if component:
                break

        if component is None:
            pytest.skip("No components registered")

        response = client.get(component.url)
        assert response.status_code == 200

    def test_unknown_component_returns_404(self, user_client):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "dw_design_system", "path": "nonexistent"},
        )
        response = user_client.get(url)
        assert response.status_code == 404

    def test_component_docstring_renders_unescaped_html(self, client):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "alert"},
        )
        response = client.get(url)
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "<p>A dismissable alert banner" in content
        assert "&lt;p&gt;A dismissable alert banner" not in content

    def test_consumer_theme_does_not_force_gallery_chrome_theme_class(self, client):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "alert"},
        )
        response = client.get(f"{url}?_dds_theme=dark")
        assert response.status_code == 200
        assert "theme_body_class" not in response.context
        assert response.context["global_active_theme"] == "dark"
        assert response.context["sandbox_active_theme"] == "dark"
        content = response.content.decode("utf-8")
        assert '<html lang="en">' in content
        assert "gallery-theme-dark" not in content
        assert "gallery-theme-light" not in content

    def test_gallery_theme_cookie_dark_sets_gallery_theme_class_and_sidebar_icon(
        self, client
    ):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "alert"},
        )
        client.cookies["dds_gallery_theme"] = "dark"
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["gallery_theme"] == "dark"
        content = response.content.decode("utf-8")
        assert '<html lang="en" class="gallery-theme-dark">' in content
        assert 'data-gallery-theme="dark"' in content
        assert 'data-action="toggle-theme"' in content
        assert 'data-icon="moon"' in content

    def test_gallery_theme_cookie_light_sets_gallery_theme_class_and_sidebar_icon(
        self, client
    ):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "alert"},
        )
        client.cookies["dds_gallery_theme"] = "light"
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["gallery_theme"] == "light"
        content = response.content.decode("utf-8")
        assert '<html lang="en" class="gallery-theme-light">' in content
        assert 'data-gallery-theme="light"' in content
        assert 'data-action="toggle-theme"' in content
        assert 'data-icon="sun"' in content

    def test_consumer_theme_query_param_does_not_alter_gallery_theme_or_sidebar_button(
        self, client
    ):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "alert"},
        )
        response = client.get(f"{url}?_dds_theme=dark")
        assert response.status_code == 200
        assert response.context["global_active_theme"] == "dark"
        assert response.context["gallery_theme"] == ""
        content = response.content.decode("utf-8")
        assert '<html lang="en">' in content
        assert "gallery-theme-dark" not in content
        assert 'data-action="toggle-theme"' in content
        sidebar_footer = content[
            content.find("data-sidebar-footer") : content.find("</aside>")
        ]
        assert 'data-icon="sun"' in sidebar_footer
        assert 'data-icon="moon"' not in sidebar_footer

    def test_both_theme_selectors_operate_independently(self, client, settings):
        settings.DJ_DESIGN_SYSTEM = {
            "GALLERY_THEMES": {
                "light": {"label": "Light"},
                "dark": {"label": "Dark"},
            }
        }
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "alert"},
        )
        client.cookies["dds_gallery_theme"] = "light"
        response = client.get(f"{url}?_dds_theme=dark")
        assert response.status_code == 200
        assert response.context["global_active_theme"] == "dark"
        assert response.context["gallery_theme"] == "light"
        content = response.content.decode("utf-8")
        assert '<html lang="en" class="gallery-theme-light">' in content
        assert 'data-gallery-theme="light"' in content
        assert 'data-action="toggle-theme"' in content
        assert 'data-icon="sun"' in content
        assert "gallery-global-theme-select" in content
        assert "_dds_theme=dark" in response.context["canvas_iframe_url"]

    def test_single_theme_omits_selector(self, client):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "alert"},
        )
        response = client.get(url)
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "gallery-global-theme-select" not in content
        assert "dds-theme-select" not in content
        assert 'data-action="toggle-consumer-color-scheme"' in content
        assert 'data-variant="default"' in content

    def test_default_gallery_ui_theme_is_desert(self, client):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "alert"},
        )
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["gallery_ui_theme"] == "desert"
        content = response.content.decode("utf-8")
        assert 'data-gallery-ui-theme="desert"' in content
        assert "gallery-ui-theme-classic" not in content
        assert "data-ui-theme-select" in content

    def test_gallery_ui_theme_classic_via_cookie(self, client):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "alert"},
        )
        client.cookies["dds_gallery_ui_theme"] = "classic"
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["gallery_ui_theme"] == "classic"
        content = response.content.decode("utf-8")
        assert 'class="gallery-ui-theme-classic"' in content
        assert 'data-gallery-ui-theme="classic"' in content
        assert "Classic theme does not support dark mode" in content
        assert response.context["gallery_theme"] == ""

    def test_gallery_ui_theme_classic_suppresses_dark_mode_cookie(self, client):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "alert"},
        )
        client.cookies["dds_gallery_ui_theme"] = "classic"
        client.cookies["dds_gallery_theme"] = "dark"
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["gallery_ui_theme"] == "classic"
        assert response.context["gallery_theme"] == ""
        content = response.content.decode("utf-8")
        assert "gallery-theme-dark" not in content

    def test_gallery_ui_theme_via_query_param(self, client):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "alert"},
        )
        response = client.get(f"{url}?_dds_gallery_ui_theme=classic")
        assert response.status_code == 200
        assert response.context["gallery_ui_theme"] == "classic"
        content = response.content.decode("utf-8")
        assert 'class="gallery-ui-theme-classic"' in content
        assert 'data-gallery-ui-theme="classic"' in content

    def test_custom_gallery_ui_theme_without_dark_mode(self, client, settings):
        settings.DJ_DESIGN_SYSTEM = {
            "GALLERY_UI_THEMES": {
                "minimal": {
                    "label": "Minimal Theme",
                },
            },
            "GALLERY_DEFAULT_UI_THEME": "minimal",
        }
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "alert"},
        )
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["gallery_ui_theme"] == "minimal"
        assert response.context["gallery_ui_theme_supports_dark_mode"] is False
        content = response.content.decode("utf-8")
        assert 'class="gallery-ui-theme-minimal"' in content
        assert 'data-gallery-ui-theme="minimal"' in content
        assert 'data-gallery-ui-supports-dark-mode="false"' in content
        assert "Minimal Theme theme does not support dark mode" in content

    def test_custom_gallery_ui_theme_with_dark_mode_and_assets(self, client, settings):
        settings.DJ_DESIGN_SYSTEM = {
            "GALLERY_UI_THEMES": {
                "cyber": {
                    "label": "Cyberpunk",
                    "css": ["css/cyber.css"],
                    "js": ["js/cyber.js"],
                    "dark_mode": {
                        "css": ["css/cyber-dark.css"],
                        "js": ["js/cyber-dark.js"],
                    },
                },
            },
            "GALLERY_DEFAULT_UI_THEME": "cyber",
        }
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "alert"},
        )
        # In light mode
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["gallery_ui_theme"] == "cyber"
        assert response.context["gallery_ui_theme_supports_dark_mode"] is True
        content = response.content.decode("utf-8")
        assert 'href="/static/css/cyber.css"' in content
        assert 'src="/static/js/cyber.js"' in content
        assert "cyber-dark.css" not in content

        # In dark mode
        client.cookies["dds_gallery_theme"] = "dark"
        response_dark = client.get(url)
        assert response_dark.status_code == 200
        content_dark = response_dark.content.decode("utf-8")
        assert 'href="/static/css/cyber.css"' in content_dark
        assert 'href="/static/css/cyber-dark.css"' in content_dark
        assert 'src="/static/js/cyber.js"' in content_dark
        assert 'src="/static/js/cyber-dark.js"' in content_dark

    def test_dark_mode_toggle_enabled_on_markdown_document_when_theme_supports_dark_mode(
        self, client, settings
    ):
        settings.DJ_DESIGN_SYSTEM = {
            "GALLERY_THEMES": {
                "custom": {
                    "label": "Custom Theme",
                    "dark_mode": {},
                }
            },
            "GALLERY_DEFAULT_THEME": "custom",
        }
        url = "/dds/demo_nav/design_guidelines/"
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["active_theme_supports_dark_mode"] is True
        content = response.content.decode("utf-8")
        assert 'data-supports-dark-mode="true"' in content
        assert 'data-action="toggle-consumer-color-scheme"' in content
        assert 'data-action="toggle-consumer-color-scheme" disabled' not in content

    def test_dark_mode_toggle_falls_back_to_default_theme_on_markdown_document(
        self, client, settings
    ):
        settings.DJ_DESIGN_SYSTEM = {
            "GALLERY_THEMES": {
                "custom": {
                    "label": "Custom Theme",
                    "dark_mode": {},
                }
            },
            "GALLERY_DEFAULT_THEME": "custom",
        }
        client.cookies["dds_theme"] = "nonexistent_stale_theme"
        url = "/dds/demo_nav/design_guidelines/"
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["active_theme_supports_dark_mode"] is True
        content = response.content.decode("utf-8")
        assert 'data-supports-dark-mode="true"' in content
        assert 'data-action="toggle-consumer-color-scheme"' in content
        assert 'data-action="toggle-consumer-color-scheme" disabled' not in content

    def test_component_renders_section_headings_and_dividers(self, client):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_nav", "path": "elements/icon"},
        )
        response = client.get(url)
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "<h1 data-docs-title>Icon</h1>" in content
        assert "<h2 data-docs-heading>Description</h2>" in content
        assert "<h2 data-docs-heading>Usage</h2>" in content
        assert "<h2 data-docs-heading>Parameters</h2>" in content
        assert "<h2 data-docs-heading>Further documentation</h2>" in content
        assert "<hr data-docs-divider>" in content

    def test_variant_view_renders_parameters_and_further_documentation(self, client):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "badge"},
        )
        response = client.get(f"{url}?variant=maximal")
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "<h1 data-docs-title>Badge</h1>" in content
        assert "<h3 data-variant-subheading>Preview</h3>" in content
        assert "<h2 data-docs-heading>Parameters</h2>" in content

    def test_builtin_component_uses_fully_qualified_tag_and_suppresses_qualified_section(
        self, client
    ):
        """Built-in components (is_builtin=True) cannot be invoked with short tag names.

        All usage examples must use the fully-qualified version (dds__<name>),
        and the redundant 'Qualified tag usage' section must be suppressed.
        """
        from dj_design_system.services.navigation import clear_navigation_cache

        with override_settings(
            DJ_DESIGN_SYSTEM={"GALLERY_INCLUDE_APPS": ["dj_design_system"]}
        ):
            clear_navigation_cache()
            try:
                url = reverse(
                    "gallery-node",
                    kwargs={
                        "app_label": "dj_design_system",
                        "path": "elements/button",
                    },
                )
                response = client.get(url)
                assert response.status_code == 200
                content = response.content.decode("utf-8")

                assert response.context["tag_signature"].minimal.startswith(
                    "{% dds__button"
                )
                assert "{% dds__button" in content
                assert "Qualified tag usage" not in content
            finally:
                clear_navigation_cache()

    def test_builtin_component_variant_uses_fully_qualified_tag(self, client):
        """Variant usage for built-in components must also use the fully-qualified tag."""
        from dj_design_system.services.navigation import clear_navigation_cache

        with override_settings(
            DJ_DESIGN_SYSTEM={"GALLERY_INCLUDE_APPS": ["dj_design_system"]}
        ):
            clear_navigation_cache()
            try:
                url = reverse(
                    "gallery-node",
                    kwargs={
                        "app_label": "dj_design_system",
                        "path": "elements/button",
                    },
                )
                response = client.get(f"{url}?variant=link")
                assert response.status_code == 200
                content = response.content.decode("utf-8")

                assert response.context["variant_signature"].minimal.startswith(
                    "{% dds__button"
                )
                assert "{% dds__button" in content
            finally:
                clear_navigation_cache()

    def test_non_builtin_component_renders_short_tag_and_qualified_section(
        self, client
    ):
        """Non-builtin components with a prefix use the short tag and show Qualified tag usage."""
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "badge"},
        )
        response = client.get(url)
        assert response.status_code == 200
        content = response.content.decode("utf-8")

        assert response.context["tag_signature"].minimal.startswith("{% badge")
        assert response.context["tag_signature_long"].minimal.startswith(
            "{% demo_components__badge"
        )
        assert "Qualified tag usage" in content
        assert "demo_components__badge" in content


class TestGalleryFolderView:
    """Test the folder view."""

    def test_unknown_app_returns_404(self, user_client):
        url = reverse(
            "gallery-node-root",
            kwargs={"app_label": "nonexistent_app"},
        )
        response = user_client.get(url)
        assert response.status_code == 404

    def test_app_root_returns_200(self, client):
        nav_tree = _get_nav_tree()
        if not nav_tree:
            pytest.skip("No apps with components registered")
        app = nav_tree[0]
        response = client.get(app.url)
        assert response.status_code == 200


class TestGalleryDocumentView:
    """Test the standalone document view."""

    def test_unknown_doc_returns_404(self, user_client):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "dw_design_system", "path": "nonexistent"},
        )
        response = user_client.get(url)
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Form integration tests
# ---------------------------------------------------------------------------


def _find_component_with_params(nav_tree):
    """Return the first component node that has at least one parameter, or None."""
    for node in _collect_all_nodes(nav_tree):
        if node.is_component and node.component.component_class.get_params():
            return node
    return None


def _find_block_component_with_params(nav_tree):
    """Return the first non-slotted block component node that has at least one parameter."""
    from dj_design_system.components import BlockComponent

    for node in _collect_all_nodes(nav_tree):
        if not node.is_component:
            continue

        component_class = node.component.component_class
        if (
            issubclass(component_class, BlockComponent)
            and component_class.get_params()
            and not component_class.has_slots()
        ):
            return node

    return None


class TestGalleryComponentFormIntegration:
    """Test that the parameter form is wired up correctly in the component view."""

    def test_param_rows_in_context(self, client):
        """Component pages should include param_rows in the template context."""
        nav_tree = _get_nav_tree()
        component = _find_component_with_params(nav_tree)
        if component is None:
            pytest.skip("No components with params registered")

        response = client.get(component.url)
        assert response.status_code == 200
        assert "param_rows" in response.context

    def test_form_in_context(self, client):
        """Component pages should include a form object in the template context."""
        nav_tree = _get_nav_tree()
        component = _find_component_with_params(nav_tree)
        if component is None:
            pytest.skip("No components with params registered")

        response = client.get(component.url)
        assert response.status_code == 200
        assert "form" in response.context

    def test_form_is_unbound_without_get_params(self, client):
        """Form should be unbound when no param GET keys are present."""
        nav_tree = _get_nav_tree()
        component = _find_component_with_params(nav_tree)
        if component is None:
            pytest.skip("No components with params registered")

        response = client.get(component.url)
        assert response.status_code == 200
        assert not response.context["form"].is_bound

    def test_form_is_bound_with_param_get_keys(self, client):
        """Form should be bound when at least one param key appears in GET."""
        nav_tree = _get_nav_tree()
        component = _find_component_with_params(nav_tree)
        if component is None:
            pytest.skip("No components with params registered")

        params = component.component.component_class.get_params()
        first_param_name = next(iter(params))

        response = client.get(component.url, {first_param_name: "test"})
        assert response.status_code == 200
        assert response.context["form"].is_bound

    def test_form_uses_initial_data_on_first_load(self, client):
        """When the component page first loads without parameters, form should have initial data from gallery kwargs."""
        from django.test import RequestFactory

        from dj_design_system.services.gallery_context import (
            get_form_and_sandbox_spec as _get_form_and_sandbox_spec,
        )
        from dj_design_system.services.tag_signature import generate_tag_signature

        nav_tree = _get_nav_tree()
        component = _find_component_with_params(nav_tree)
        if component is None:
            pytest.skip("No components with params registered")

        request = RequestFactory().get(component.url)
        component_class = component.component.component_class
        tag_signature = generate_tag_signature(
            component_class, canvas_component_name=component.component.qualified_name
        )

        form, form_kwargs, sandbox_spec = _get_form_and_sandbox_spec(
            request, component_class, tag_signature
        )

        assert not form.is_bound
        # Check that form.initial has been populated with data from tag_signature.maximal_spec
        # It should contain at least the keyword parameters
        assert form.initial
        for k, v in tag_signature.maximal_spec.params.items():
            if k in form.fields:
                assert form.initial[k] == v

    def test_required_model_param_falls_back_when_unsubmitted_in_get(self):
        """When form is bound to GET with other params but a required ModelParam is omitted/unselected, form_kwargs should fall back to tag_signature.maximal_spec value."""
        from unittest.mock import MagicMock

        from django.test import RequestFactory

        from dj_design_system.components import BlockComponent
        from dj_design_system.data import CanvasSpec
        from dj_design_system.parameters import StrParam
        from dj_design_system.parameters.model import ModelParam
        from dj_design_system.services.gallery_context import (
            get_form_and_sandbox_spec as _get_form_and_sandbox_spec,
        )
        from dj_design_system.services.tag_signature import TagSignature

        dummy_qs = MagicMock()
        dummy_qs.order_by.return_value = dummy_qs
        dummy_qs.values_list.return_value = []
        dummy_qs.filter.return_value = dummy_qs

        class DummyModel:
            objects = dummy_qs

        class DummyModelParam(ModelParam):
            class Meta:
                model = DummyModel
                fields = ["name"]

        class MyComponent(BlockComponent):
            title = StrParam("Title")
            user = DummyModelParam("User", required=True)

        fake_instance = DummyModel()
        maximal_spec = CanvasSpec(
            component_name="my_component",
            params={"title": "Hello", "user": fake_instance},
        )
        tag_sig = TagSignature(
            minimal="",
            maximal="",
            minimal_html="",
            maximal_html="",
            minimal_spec=maximal_spec,
            maximal_spec=maximal_spec,
        )

        request = RequestFactory().get("/?title=CustomTitle")
        form, form_kwargs, sandbox_spec = _get_form_and_sandbox_spec(
            request, MyComponent, tag_sig
        )

        assert form.is_bound
        assert form_kwargs.get("title") == "CustomTitle"
        assert form_kwargs.get("user") == fake_instance

    def test_positional_values_kept_for_template_source(self):
        """Positional values go to the spec's positional_args but stay in form_kwargs for the template source."""
        from django.test import RequestFactory

        from dj_design_system.components import TagComponent
        from dj_design_system.parameters import StrParam
        from dj_design_system.services.gallery_context import (
            get_form_and_sandbox_spec,
        )
        from dj_design_system.services.tag_signature import (
            generate_current_tag_signature,
            generate_tag_signature,
        )

        class PositionalComponent(TagComponent):
            template_format_str = "<p>{label}</p>"
            label = StrParam("Label")

            class Meta:
                positional_args = ["label"]

        request = RequestFactory().get("/?label=Chosen")
        form, form_kwargs, sandbox_spec = get_form_and_sandbox_spec(
            request,
            PositionalComponent,
            generate_tag_signature(PositionalComponent),
        )

        assert form_kwargs == {"label": "Chosen"}
        assert sandbox_spec.positional_args == ("Chosen",)
        assert "label" not in sandbox_spec.params
        current = generate_current_tag_signature(PositionalComponent, form_kwargs)
        assert '"Chosen"' in current.minimal

    def test_is_sandbox_form_submission(self):
        """is_sandbox_form_submission returns True if and only if _iss is in GET."""
        from django.test import RequestFactory

        from dj_design_system.services.control_params import SANDBOX_SUBMISSION_PARAM
        from dj_design_system.services.gallery_context import (
            is_sandbox_form_submission as _is_sandbox_form_submission,
        )

        rf = RequestFactory()
        assert not _is_sandbox_form_submission(rf.get("/?variant=foo&theme=dark"))
        assert _is_sandbox_form_submission(rf.get(f"/?{SANDBOX_SUBMISSION_PARAM}=1"))
        assert _is_sandbox_form_submission(
            rf.get(f"/?{SANDBOX_SUBMISSION_PARAM}=1&variant=foo")
        )

    def test_param_rows_length_matches_params(self, client):
        """param_rows should contain one entry per component parameter.

        For BlockComponent subclasses an extra 'content' row is prepended.
        """
        from dj_design_system.components import BlockComponent

        nav_tree = _get_nav_tree()
        component = _find_component_with_params(nav_tree)
        if component is None:
            pytest.skip("No components with params registered")

        component_class = component.component.component_class
        params = component_class.get_params()
        extra = 1 if issubclass(component_class, BlockComponent) else 0
        response = client.get(component.url)
        assert len(response.context["param_rows"]) == len(params) + extra

    def test_param_rows_contain_required_keys(self, client):
        """Each entry in param_rows should have 'name', 'spec', and 'field' keys."""
        nav_tree = _get_nav_tree()
        component = _find_component_with_params(nav_tree)
        if component is None:
            pytest.skip("No components with params registered")

        response = client.get(component.url)
        for row in response.context["param_rows"]:
            assert "name" in row
            assert "spec" in row
            assert "field" in row

    def test_param_rows_handles_tuple_type(self):
        """build_param_rows should handle parameter specs with tuple type definitions without raising AttributeError."""
        from dj_design_system.components import BlockComponent
        from dj_design_system.forms import build_component_form
        from dj_design_system.parameters.base import JSONParam
        from dj_design_system.services.gallery_context import (
            build_param_rows as _build_param_rows,
        )

        class TupleParamComponent(BlockComponent):
            data = JSONParam("JSON data")

        form_class = build_component_form(TupleParamComponent)
        form = form_class()
        params = TupleParamComponent.get_params()
        rows = _build_param_rows(form, params, TupleParamComponent)

        data_row = next(r for r in rows if r["name"] == "data")
        assert (
            "dict | list | str | int | float | bool | NoneType"
            in data_row["spec"].type_name
        )

    def test_page_renders_with_valid_get_param(self, client):
        """A component page should return 200 when valid param data is supplied via GET."""
        nav_tree = _get_nav_tree()
        component = _find_component_with_params(nav_tree)
        if component is None:
            pytest.skip("No components with params registered")

        params = component.component.component_class.get_params()
        first_param_name, first_spec = next(iter(params.items()))

        # Determine a value compatible with the param type.
        from dj_design_system.parameters import BoolParam, StrParam

        if isinstance(first_spec, BoolParam):
            get_data = {first_param_name: "True"}
        elif isinstance(first_spec, StrParam) and first_spec.choices:
            get_data = {first_param_name: str(first_spec.choices[0])}
        elif isinstance(first_spec, StrParam):
            get_data = {first_param_name: "hello"}
        else:
            pytest.skip("First param is a ModelParam — skip value injection")

        response = client.get(component.url, get_data)
        assert response.status_code == 200

    def test_form_auto_submit_js_in_rendered_html(self, client):
        """The rendered page should contain the htmx-wired parameter form."""
        nav_tree = _get_nav_tree()
        component = _find_component_with_params(nav_tree)
        if component is None:
            pytest.skip("No components with params registered")

        response = client.get(component.url)
        assert response.status_code == 200
        assert b"dds-sandbox-params" in response.content
        assert b"hx-get" in response.content

    def test_htmx_partial_returns_fragment(self, client):
        """An htmx request returns only the sandbox fragment, not the full page."""
        nav_tree = _get_nav_tree()
        component = _find_component_with_params(nav_tree)
        if component is None:
            pytest.skip("No components with params registered")

        response = client.get(component.url, HTTP_HX_REQUEST="true")
        assert response.status_code == 200
        # Fragment should contain the canvas and form but NOT the full page shell.
        assert b"dds-canvas-widget" in response.content
        assert b"<html" not in response.content

    def test_block_content_updates_current_usage(self, client):
        """Block content entered in the form should be reflected in current usage."""
        nav_tree = _get_nav_tree()
        component = _find_block_component_with_params(nav_tree)
        if component is None:
            pytest.skip("No block components with params registered")

        response = client.get(component.url, {"content": "Updated body"})
        assert response.status_code == 200
        assert response.context["current_signature"] is not None
        assert "Updated body" in response.context["current_signature"].minimal


# ---------------------------------------------------------------------------
# Smoke test: walk the entire nav tree and hit every URL
# ---------------------------------------------------------------------------


def _collect_all_nodes(nodes):
    """Recursively collect all NavNode objects from a tree."""
    result = []
    for node in nodes:
        result.append(node)
        if node.children:
            result.extend(_collect_all_nodes(node.children))
    return result


class TestParamsTable:
    """A parameter's name must not shadow the dict method the table loops over."""

    def test_param_named_items(self, client, monkeypatch):
        from dj_design_system.parameters import StrParam
        from dj_design_system.services.registry import component_registry

        info = component_registry.get_by_name("badge", app_label="demo_components")
        original = info.component_class.get_params
        extra = StrParam("Named like dict.items.", required=False, default="")
        monkeypatch.setattr(
            info.component_class,
            "get_params",
            classmethod(lambda cls: {**original(), "items": extra}),
        )

        response = client.get(reverse("gallery") + "demo_components/badge/")

        assert response.status_code == 200
        assert b"<code data-param-name>items</code>" in response.content


class TestSmokeAllPages:
    """Walk the entire navigation tree and assert every page renders."""

    MULTI_THEME_SETTINGS = {
        "GALLERY_THEMES": {
            "theme_a": {
                "label": "Theme A",
                "canvas_background": "white",
                "html_attrs": {"html": {"class": "theme-a"}},
                "dark_mode": {
                    "canvas_background": {"color": "rgb(18, 19, 23)"},
                    "html_attrs": {"html": {"class": "theme-a is-dark"}},
                },
            },
            "dark": {
                "label": "Dark Theme",
                "canvas_background": {"color": "#f9f6f0"},
                "html_attrs": {"html": {"class": "theme-b"}},
            },
        },
        "GALLERY_DEFAULT_THEME": "theme_a",
        "GALLERY_UI_THEMES": {
            "desert": {"label": "Desert", "dark_mode": {}},
            "classic": {"label": "Classic"},
        },
        "GALLERY_DEFAULT_UI_THEME": "desert",
    }

    def test_every_nav_node_returns_200(self, client):
        """Every node in the nav tree should have a resolvable URL that returns 200."""
        nav_tree = _get_nav_tree()
        all_nodes = _collect_all_nodes(nav_tree)

        if not all_nodes:
            pytest.skip("No navigation nodes registered")

        errors = []
        for node in all_nodes:
            url = node.url
            response = client.get(url)
            if response.status_code != 200:
                errors.append(f"{url} -> {response.status_code} ({node.label})")

        assert errors == [], "Pages that failed:\n" + "\n".join(errors)

    def test_every_page_returns_200_with_multiple_themes(self, client, settings):
        """Every gallery page (index, folder, doc, component) renders when 2+ themes are configured (#268)."""
        settings.DJ_DESIGN_SYSTEM = self.MULTI_THEME_SETTINGS
        index_response = client.get(reverse("gallery"))
        assert index_response.status_code == 200
        assert b"gallery-global-theme-select" in index_response.content

        nav_tree = _get_nav_tree()
        all_nodes = _collect_all_nodes(nav_tree)
        errors = []
        for node in all_nodes:
            response = client.get(node.url)
            if response.status_code != 200:
                errors.append(f"{node.url} -> {response.status_code} ({node.label})")
        assert errors == [], "Pages that failed under multi-theme:\n" + "\n".join(
            errors
        )

    def test_no_undefined_template_variables_across_gallery_views(
        self, client, settings
    ):
        """Ensure gallery views do not reference undefined template context variables (#268)."""
        templates_cfg = copy.deepcopy(settings.TEMPLATES)
        templates_cfg[0]["OPTIONS"]["string_if_invalid"] = "__UNDEFINED_VAR:%s__"
        settings.TEMPLATES = templates_cfg
        settings.DJ_DESIGN_SYSTEM = self.MULTI_THEME_SETTINGS

        urls_to_check = [
            reverse("gallery"),
            "/dds/demo_components/card/",
            "/dds/demo_nav/elements/",
            "/dds/demo_nav/design_guidelines/",
            "/dds/demo_components/alert/",
            "/dds/demo_components/badge/?variant=status",
        ]
        for url in urls_to_check:
            response = client.get(path=url)
            assert response.status_code == 200
            html = response.content.decode("utf-8")
            assert "__UNDEFINED_VAR:" not in html, (
                f"Undefined template variable rendered on {url}"
            )

    def test_index_page_renders(self, client):
        response = client.get(reverse("gallery"))
        assert response.status_code == 200
        assert b"dds-nav-tree" in response.content

    def test_breadcrumbs_present_on_component_page(self, client):
        """Component pages should have breadcrumb links."""
        nav_tree = _get_nav_tree()
        component = None
        for node in _collect_all_nodes(nav_tree):
            if node.is_component:
                component = node
                break

        if component is None:
            pytest.skip("No components registered")

        response = client.get(component.url)
        assert response.status_code == 200
        assert b"dds-breadcrumb" in response.content
        assert b"Gallery" in response.content

    def test_nav_tree_rendered_in_sidebar(self, client):
        """The nav tree should be rendered in the sidebar."""
        nav_tree = _get_nav_tree()
        if not nav_tree:
            pytest.skip("No apps registered")

        response = client.get(reverse("gallery"))
        # Check the first app label appears in the response
        first_app = nav_tree[0]
        assert first_app.label.encode() in response.content

    def test_active_state_on_component_page(self, client):
        """The active component should be highlighted in the sidebar."""
        nav_tree = _get_nav_tree()
        component = None
        for node in _collect_all_nodes(nav_tree):
            if node.is_component:
                component = node
                break

        if component is None:
            pytest.skip("No components registered")

        response = client.get(component.url)
        assert response.status_code == 200
        assert b'data-active="true"' in response.content


# ---------------------------------------------------------------------------
# Toolbar buttons on component pages
# ---------------------------------------------------------------------------


class TestToolbarButtons:
    """Test that all sandbox toolbar buttons render on component pages."""

    @staticmethod
    def _get_component_response(client):
        nav_tree = _get_nav_tree()
        for node in _collect_all_nodes(nav_tree):
            if node.is_component:
                return client.get(node.url)
        pytest.skip("No components registered")

    def test_outline_toggle(self, client):
        response = self._get_component_response(client=client)
        assert b'data-action="toggle-outline"' in response.content

    def test_measure_toggle(self, client):
        response = self._get_component_response(client=client)
        assert b'data-action="toggle-measure"' in response.content

    def test_rtl_toggle(self, client):
        response = self._get_component_response(client=client)
        assert b'data-action="toggle-rtl"' in response.content

    def test_viewport_toggle(self, client):
        response = self._get_component_response(client=client)
        assert b'data-sandbox-control="viewport"' in response.content

    def test_zoom_toggle(self, client):
        response = self._get_component_response(client=client)
        assert b'data-sandbox-control="zoom"' in response.content

    def test_bg_toggle(self, client):
        response = self._get_component_response(client=client)
        assert b'data-sandbox-control="background"' in response.content

    def test_measure_script_data_attribute(self, client):
        response = self._get_component_response(client=client)
        assert b'data-action="toggle-measure"' in response.content

    def test_viewport_presets(self, client):
        response = self._get_component_response(client=client)
        content = response.content
        assert b'data-value="320"' in content
        assert b'data-value="1920"' in content
        assert b'data-value="2560"' in content
        assert b'data-value="responsive"' in content


# ---------------------------------------------------------------------------
# gallery_access_required — auth paths
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGalleryAccessRequired:
    """Test the gallery_access_required decorator when gallery is not public."""

    @override_settings(DJ_DESIGN_SYSTEM={"GALLERY_IS_PUBLIC": False})
    def test_unauthenticated_redirects(self, client):
        response = client.get(reverse("gallery"))
        assert response.status_code == 302
        assert "/accounts/login/" in response["Location"]

    @override_settings(DJ_DESIGN_SYSTEM={"GALLERY_IS_PUBLIC": False})
    def test_unauthenticated_redirect_encodes_next(self, client):
        """Characters decoded from the path must not break the login query string."""
        gallery = reverse("gallery")
        response = client.get(f"{gallery}demo%26next%3Dhttps%3A%2F%2Fevil.example/")
        assert response.status_code == 302
        query = parse_qs(urlsplit(response["Location"]).query)
        assert query["next"] == [f"{gallery}demo&next%3Dhttps://evil.example/"]

    @override_settings(DJ_DESIGN_SYSTEM={"GALLERY_IS_PUBLIC": False})
    def test_unauthenticated_redirect_preserves_query_string(self, client):
        response = client.get(reverse("gallery") + "?theme=dark")
        assert response.status_code == 302
        assert f"next={reverse('gallery')}%3Ftheme%3Ddark" in response["Location"]

    @override_settings(
        DJ_DESIGN_SYSTEM={"GALLERY_IS_PUBLIC": False},
        LOGIN_URL="https://sso.example.com/login/",
    )
    def test_unauthenticated_redirect_supports_absolute_login_url(self, client):
        response = client.get(reverse("gallery"))
        assert response.status_code == 302
        assert response["Location"].startswith("https://sso.example.com/login/?next=")

    @override_settings(DJ_DESIGN_SYSTEM={"GALLERY_IS_PUBLIC": False})
    def test_authenticated_without_permission_is_forbidden(
        self, client, django_user_model
    ):
        user = django_user_model.objects.create_user(username="unprivileged")
        client.force_login(user)
        response = client.get(reverse("gallery"))
        assert response.status_code == 403

    @override_settings(DJ_DESIGN_SYSTEM={"GALLERY_IS_PUBLIC": False})
    def test_authenticated_with_permission_allowed(self, client, django_user_model):
        user = django_user_model.objects.create_user(username="privileged")
        perm = Permission.objects.get(codename="can_view_gallery")
        user.user_permissions.add(perm)
        client.force_login(user)
        response = client.get(reverse("gallery"))
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# _render_markdown — codehilite disabled branch
# ---------------------------------------------------------------------------


class TestRenderMarkdown:
    """Test _render_markdown internals."""

    @override_settings(DJ_DESIGN_SYSTEM={"GALLERY_CODEHILITE_STYLE": ""})
    def test_no_codehilite_when_style_empty(self, client):
        """A document page renders without codehilite when the style is empty."""

        nav_tree = get_base_context()["nav_tree"]
        demo_nav_app = next((a for a in nav_tree if a.slug == "demo_nav"), None)
        if demo_nav_app is None:
            pytest.skip("demo_nav not in nav tree")

        # Find the accessibility document node
        def _find_doc(node):
            if node.is_document:
                return node
            for child in node.children:
                found = _find_doc(child)
                if found:
                    return found
            return None

        doc_node = _find_doc(demo_nav_app)
        if doc_node is None:
            pytest.skip("No document node in demo_nav")

        response = client.get(doc_node.url)
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# _canvas_html_attrs — non-empty attrs branch
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCanvasHtmlAttrs:
    """Test that GALLERY_CANVAS_HTML_ATTRS is reflected in the canvas iframe."""

    @override_settings(
        DJ_DESIGN_SYSTEM={
            "GALLERY_CANVAS_HTML_ATTRS": {
                "html": {"class": "govuk-template"},
                "body": {"class": "govuk-template__body"},
            }
        }
    )
    def test_html_attrs_in_canvas_response(self, client):
        from django.urls import reverse

        url = reverse("gallery-canvas-iframe")
        response = client.get(url, {"component": "rich_button", "label": "Test"})
        content = response.content.decode()
        assert "govuk-template" in content


class TestCSPCompliance:
    def test_csp_nonce_in_gallery_views(self, rf):
        request = rf.get("/dds/")
        request.csp_nonce = "sample-nonce-987"
        response = gallery_index(request)
        content = response.content.decode()
        assert 'nonce="sample-nonce-987"' in content

    def test_no_inline_style_attributes_in_index(self, rf):
        request = rf.get("/dds/")
        response = gallery_index(request)
        content = response.content.decode()
        assert 'style="' not in content

    def test_single_gallery_search_index_script_in_rendered_page(self, rf):
        request = rf.get("/dds/")
        response = gallery_index(request)
        content = response.content.decode()
        assert content.count('<script id="gallery-search-index"') == 1


class TestThinViewsAndImmutableParams:
    def test_component_and_canvas_views_define_no_private_helpers(self):
        for mod in (component_views, canvas_views, gallery_views):
            private_funcs = [
                name
                for name, fn in inspect.getmembers(mod, inspect.isfunction)
                if fn.__module__ == mod.__name__ and name.startswith("_")
            ]
            assert private_funcs == [], (
                f"{mod.__name__} defines private helper functions: {private_funcs}"
            )

    def test_build_param_rows_does_not_mutate_base_param_descriptors(self):
        class ImmutableParamComponent(BlockComponent):
            title = StrParam("Title", default="Hi")
            payload = JSONParam("JSON data")

        form = build_component_form(ImmutableParamComponent)()
        params = ImmutableParamComponent.get_params()
        rows = build_param_rows(form, params, ImmutableParamComponent)

        assert all(isinstance(r, ParamRowData) for r in rows)
        for param_obj in params.values():
            assert "type_name" not in param_obj.__dict__


class TestComponentThemeOverride:
    """Tests for Issue #124: gallery component theme override indication."""

    TWO_THEMES_SETTINGS = {
        "GALLERY_THEMES": {
            "default": {
                "label": "Default Theme",
                "html_attrs": {"html": {"data-theme": "default"}},
            },
            "dark": {
                "label": "Dark Theme",
                "html_attrs": {"html": {"data-theme": "dark"}},
            },
        },
        "GALLERY_DEFAULT_THEME": "default",
    }

    def test_component_theme_override_when_unsupported_theme_selected(
        self, client, settings
    ):
        settings.DJ_DESIGN_SYSTEM = self.TWO_THEMES_SETTINGS
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "alert"},
        )
        response = client.get(url)
        assert response.status_code == 200

        # Global theme remains 'default', while sandbox active theme resolves to 'dark'
        assert response.context["global_active_theme"] == "default"
        assert response.context["sandbox_active_theme"] == "dark"
        assert response.context["is_theme_restricted"] is True
        assert response.context["is_theme_overridden"] is True
        assert response.context["component_available_themes"] == ["dark"]
        assert response.context["available_theme_labels"] == ["Dark Theme"]
        assert (
            response.context["theme_override_message"]
            == "This component only supports Dark Theme (overriding Default Theme)."
        )

        content = response.content.decode("utf-8")
        # Notice and notes present in HTML
        assert "data-theme-override-note" in content
        assert "data-theme-override-notice" in content
        assert 'data-theme-overridden="true"' in content
        assert 'data-unsupported="true"' in content
        assert "Default Theme (unsupported)" in content
        assert "Theme overridden" in content
        assert (
            "This component only supports Dark Theme (overriding Default Theme)."
            in content
        )

    def test_component_theme_restricted_when_supported_theme_selected(
        self, client, settings
    ):
        settings.DJ_DESIGN_SYSTEM = self.TWO_THEMES_SETTINGS
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "alert"},
        )
        response = client.get(f"{url}?_dds_theme=dark")
        assert response.status_code == 200

        assert response.context["global_active_theme"] == "dark"
        assert response.context["sandbox_active_theme"] == "dark"
        assert response.context["is_theme_restricted"] is True
        assert response.context["is_theme_overridden"] is False
        assert (
            response.context["theme_override_message"]
            == "This component only supports Dark Theme."
        )

        content = response.content.decode("utf-8")
        assert "data-theme-override-note" in content
        assert "data-theme-override-notice" in content
        assert 'data-theme-overridden="false"' in content
        assert "Theme restricted" in content
        assert "This component only supports Dark Theme." in content
        # Default Theme remains annotated as unsupported by the component
        assert "Default Theme (unsupported)" in content

    def test_unrestricted_component_does_not_render_override_indicators(
        self, client, settings
    ):
        settings.DJ_DESIGN_SYSTEM = self.TWO_THEMES_SETTINGS
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "button"},
        )
        response = client.get(url)
        assert response.status_code == 200

        assert response.context["is_theme_restricted"] is False
        assert response.context["is_theme_overridden"] is False

        content = response.content.decode("utf-8")
        assert "data-theme-override-note" not in content
        assert "data-theme-override-notice" not in content
        assert "data-unsupported" not in content
        assert "(unsupported)" not in content

    def test_theme_select_supported_themes_parameter(self):
        from dj_design_system.components.gallery.composites.theme_select.theme_select import (
            ThemeOption,
            ThemeSelect,
        )

        ts = ThemeSelect(
            themes=[
                ThemeOption(value="default", label="Default Theme"),
                ThemeOption(value="dark", label="Dark Theme"),
            ],
            active_theme="default",
            supported_themes=["dark"],
        )
        ctx = ts.get_context()
        normalized = ctx["normalized_themes"]
        assert len(normalized) == 2
        assert normalized[0]["value"] == "default"
        assert normalized[0]["is_supported"] is False
        assert normalized[0]["label"] == "Default Theme (unsupported)"
        assert normalized[0]["raw_label"] == "Default Theme"
        assert normalized[1]["value"] == "dark"
        assert normalized[1]["is_supported"] is True
        assert normalized[1]["label"] == "Dark Theme"
        assert normalized[1]["raw_label"] == "Dark Theme"

    def test_non_component_views_render_with_multiple_themes(self, client, settings):
        """Regression test for #268: gallery_index, folder, and document views render with 2+ themes."""
        settings.DJ_DESIGN_SYSTEM = self.TWO_THEMES_SETTINGS

        index_resp = client.get(reverse("gallery"))
        assert index_resp.status_code == 200
        assert index_resp.context["component_available_themes"] is None
        assert index_resp.context["is_theme_restricted"] is False
        index_html = index_resp.content.decode("utf-8")
        assert "gallery-global-theme-select" in index_html
        assert "data-theme-override-note" not in index_html
        assert "(unsupported)" not in index_html

        folder_resp = client.get("/dds/demo_components/card/")
        assert folder_resp.status_code == 200
        assert "gallery-global-theme-select" in folder_resp.content.decode("utf-8")

        index_doc_folder_resp = client.get("/dds/demo_nav/elements/")
        assert index_doc_folder_resp.status_code == 200
        assert "gallery-global-theme-select" in index_doc_folder_resp.content.decode(
            "utf-8"
        )

        doc_resp = client.get("/dds/demo_nav/design_guidelines/")
        assert doc_resp.status_code == 200
        assert "gallery-global-theme-select" in doc_resp.content.decode("utf-8")
