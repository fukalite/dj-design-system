"""Tests for Gallery component view, variant views, and sandbox preset integration."""

import pytest
from django.test import Client
from django.urls import reverse

from dj_design_system.components import TagComponent
from dj_design_system.data import ComponentInfo, GalleryParameter, NavNode
from dj_design_system.gallery import GalleryConfig, Variant
from dj_design_system.parameters.base import StrParam
from dj_design_system.services.registry import component_registry
from dj_design_system.templatetags.dj_design_system_gallery import nav_link_is_active
from dj_design_system.types import NodeType


pytestmark = pytest.mark.django_db


class VariantDemoButton(TagComponent):
    template_format_str = '<button class="btn {theme}">{label}</button>'
    label = StrParam("Button label", default="Default")
    theme = StrParam("Button theme", default="primary")


@pytest.fixture
def custom_variant_component():
    """Register a component with rich variants in the component_registry."""
    config = GalleryConfig(
        variants=[
            Variant(
                name="primary",
                label="Primary Button",
                description="The standard action button.",
                kwargs={"label": "Primary Click", "theme": "primary"},
            ),
            Variant(
                name="danger",
                label="Danger Button",
                description="Destructive action button.",
                kwargs={
                    "label": lambda: "Delete All",
                    "theme": GalleryParameter(value="danger"),
                },
                theme="light",
            ),
        ]
    )
    info = ComponentInfo(
        component_class=VariantDemoButton,
        name="variant_demo_btn",
        app_label="demo_components",
        relative_path="variant_demo_btn",
    )
    info.__dict__["gallery_config"] = config
    component_registry._components.append(info)
    yield info
    component_registry._components.remove(info)


class TestVariantViews:
    """Test component view rendering when variant query parameter is present or absent."""

    def test_main_view_without_variant_param(self, client: Client):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "badge"},
        )
        response = client.get(url)
        assert response.status_code == 200
        assert response.context.get("active_variant") is None
        assert "gallery_variants" in response.context
        # Shows minimal and maximal example sections
        assert b"Minimal example" in response.content
        assert b"Bigger example" in response.content

    def test_variant_view_with_valid_variant(self, client: Client):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "badge"},
        )
        response = client.get(f"{url}?variant=maximal")
        assert response.status_code == 200
        assert response.context.get("active_variant") is not None
        assert response.context["active_variant"].name == "maximal"
        # Focused variant view
        assert b"Maximal" in response.content
        assert b"variant=maximal" in response.content
        # Breadcrumbs contain parent component link and variant as current crumb
        breadcrumbs = response.context["breadcrumbs"]
        assert breadcrumbs[-2]["url"] == url
        assert breadcrumbs[-2]["label"] == "Badge"
        assert breadcrumbs[-1]["label"] == "Maximal"
        assert "url" not in breadcrumbs[-1]
        assert b"gallery-back-link" not in response.content

    def test_variant_view_prefills_sandbox_form(self, client: Client):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "badge"},
        )
        response = client.get(f"{url}?variant=maximal")
        assert response.status_code == 200
        form = response.context["form"]
        # In badge_gallery.py, maximal text is "Unread Messages" and theme is "danger"
        assert form.initial.get("text") == "Unread Messages"
        assert form.initial.get("theme") == "danger"

    def test_sandbox_form_contains_variant_hidden_input(self, client: Client):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "badge"},
        )
        response = client.get(f"{url}?variant=maximal")
        assert response.status_code == 200
        assert (
            b'<input type="hidden" name="variant" value="maximal"' in response.content
        )

    def test_sandbox_toolbar_contains_variant_preset_selector(self, client: Client):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "badge"},
        )
        response = client.get(f"{url}?variant=maximal")
        assert response.status_code == 200
        assert b"data-gallery-variant-select" in response.content
        assert (
            b'value="maximal"' in response.content
            or b"variant=maximal" in response.content
        )
        assert b"onchange=" not in response.content

    def test_sandbox_toolbar_variant_form_action_targets_sandbox_pane(
        self, client: Client
    ):
        """The variant preset form in the sandbox toolbar targets #pane-sandbox to avoid snapping to docs."""
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "badge"},
        )
        response = client.get(url)
        assert response.status_code == 200
        # Form action in toolbar should retain #pane-sandbox
        assert b'action="' in response.content
        assert f'action="{url}#pane-sandbox"'.encode() in response.content

    def test_unknown_variant_returns_404(self, client: Client):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "badge"},
        )
        response = client.get(f"{url}?variant=nonexistent")
        assert response.status_code == 404

    def test_custom_variant_with_callable_and_gallery_parameter(
        self, custom_variant_component, client: Client
    ):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "variant_demo_btn"},
        )
        response = client.get(f"{url}?variant=danger")
        assert response.status_code == 200
        assert response.context["active_variant"].name == "danger"
        form = response.context["form"]
        # Dynamic callable was evaluated
        assert form.initial.get("label") == "Delete All"
        # GalleryParameter was unwrapped
        assert form.initial.get("theme") == "danger"
        # Focused description rendered
        assert b"Destructive action button." in response.content

    def test_variant_view_highlights_active_variant_in_sidebar_nav(
        self, client: Client
    ):
        """Full-page variant view marks the active variant link as active in the sidebar nav (#137)."""
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "badge"},
        )
        response = client.get(f"{url}?variant=status")
        assert response.status_code == 200
        html = response.content.decode("utf-8")
        assert (
            'class="gallery-nav__link gallery-nav__link--variant gallery-nav__link--active"'
            in html
        )

    def test_toolbar_persists_state_across_variant_selection(self):
        """gallery-toolbar.js persists and restores toolbar state via sessionStorage (#151)."""
        from pathlib import Path

        js_path = Path("dj_design_system/static/dj_design_system/gallery-toolbar.js")
        content = js_path.read_text(encoding="utf-8")

        assert "sessionStorage" in content
        assert "dds_toolbar_state" in content
        assert "saveToolbarState" in content
        assert "loadToolbarState" in content


class TestNavLinkIsActive:
    """Unit tests for the ``nav_link_is_active`` template tag (#137)."""

    @staticmethod
    def _node(node_type: NodeType, **kwargs) -> NavNode:
        return NavNode(label="x", slug="danger", node_type=node_type, **kwargs)

    def test_variant_matches_variant_instance_or_slug(self):
        node = self._node(
            NodeType.VARIANT,
            variant=Variant(name="danger"),
            base_active_path="app/button",
        )
        assert nav_link_is_active(node, "app/button", Variant(name="danger"))
        assert nav_link_is_active(node, "app/button", "danger")

    def test_variant_not_active_for_other_variant_or_path(self):
        node = self._node(
            NodeType.VARIANT,
            variant=Variant(name="danger"),
            base_active_path="app/button",
        )
        assert not nav_link_is_active(node, "app/button", "basic")
        assert not nav_link_is_active(node, "app/other", "danger")
        assert not nav_link_is_active(node, "app/button", None)

    def test_non_variant_active_only_without_active_variant(self):
        node = self._node(NodeType.FOLDER, active_path="app/button")
        assert nav_link_is_active(node, "app/button", None)
        assert not nav_link_is_active(node, "app/button", "danger")
