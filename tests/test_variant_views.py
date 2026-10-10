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
        assert b"_dds_variant=maximal" in response.content
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
        assert b'<input type="hidden" name="_iss" value="1"' in response.content
        assert (
            b'<input type="hidden" name="_dds_variant" value="maximal"'
            in response.content
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

    def test_component_with_variant_param_renders_and_submits_in_sandbox(
        self, client: Client
    ):
        """A component declaring a 'variant' parameter (like SlottedCardComponent) can view presets and submit sandbox edits without parameter collision (#135)."""
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "card/slotted_card"},
        )
        # 1. Navigating to ?variant=product loads an unbound form without validation errors
        response = client.get(f"{url}?variant=product")
        assert response.status_code == 200
        assert response.context["active_variant"].name == "product"
        form = response.context["form"]
        assert not form.is_bound
        assert form.initial.get("variant") == "elevated"

        # 2. Submitting the sandbox form with both _dds_variant=product and component param variant=outlined
        submit_response = client.get(
            f"{url}?_iss=1&_dds_theme=default&_dds_variant=product&title=Pro&variant=outlined&slot__body=Body"
        )
        assert submit_response.status_code == 200
        assert submit_response.context["active_variant"].name == "product"
        bound_form = submit_response.context["form"]
        assert bound_form.is_bound
        assert bound_form.is_valid()
        iframe_url = submit_response.context["canvas_iframe_url"]
        assert "_dds_variant=product" in iframe_url
        assert "variant=outlined" in iframe_url

        # 3. Submitting the sandbox form on default variant with component param variant=outlined
        submit_default_response = client.get(
            f"{url}?_iss=1&_dds_theme=default&title=Pro&variant=outlined&slot__body=Body"
        )
        assert submit_default_response.status_code == 200
        assert submit_default_response.context["active_variant"] is None
        bound_default_form = submit_default_response.context["form"]
        assert bound_default_form.is_bound
        assert bound_default_form.is_valid()
        iframe_default_url = submit_default_response.context["canvas_iframe_url"]
        assert "variant=outlined" in iframe_default_url

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

    def test_unbound_variant_sandbox_spec_omits_redundant_query_params(
        self, custom_variant_component, client: Client
    ):
        """When viewing a variant with an unbound form, canvas_iframe_url resolves kwargs via variant= on the server rather than duplicating kwargs in the URL (#162)."""
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "demo_components", "path": "variant_demo_btn"},
        )
        response = client.get(f"{url}?variant=danger")
        assert response.status_code == 200
        iframe_url = response.context["canvas_iframe_url"]
        assert "variant=danger" in iframe_url
        assert "Delete+All" not in iframe_url

    def test_component_page_code_snippets_and_preview_urls_carry_block_content(
        self, client: Client
    ):
        """Component page's code snippets and preview URLs carry the same configured block content (#154)."""
        from dj_design_system.components import BlockComponent

        class AlertBox(BlockComponent):
            template_format_str = '<div class="alert">{content}</div>'

        cfg = GalleryConfig(
            param_defaults={"content": "Default alert body"},
            variants=[
                Variant(name="maximal", kwargs={"content": "Detailed alert body"}),
            ],
            bigger_variant="maximal",
        )
        info = ComponentInfo(
            component_class=AlertBox,
            name="alert_box",
            app_label="demo_components",
            relative_path="alert_box",
        )
        info.__dict__["gallery_config"] = cfg
        component_registry._components.append(info)
        try:
            url = reverse(
                "gallery-node",
                kwargs={"app_label": "demo_components", "path": "alert_box"},
            )
            response = client.get(url)
            assert response.status_code == 200
            sig = response.context["tag_signature"]
            assert "Default alert body" in sig.minimal
            assert "Detailed alert body" in sig.maximal
            assert "Default+alert+body" in response.context["minimal_preview_url"]
            assert "Detailed+alert+body" in response.context["maximal_preview_url"]
        finally:
            component_registry._components.remove(info)


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
