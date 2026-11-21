"""Tests for Phase 4 runtime consumers of typed and devolved settings."""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest import mock

import pytest
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.signals import setting_changed
from django.http import Http404
from django.template import Context, Library, Template
from django.test import Client, RequestFactory, override_settings
from django.urls import reverse

from dj_design_system.api.views import ComponentRegistryView, ComponentRenderView
from dj_design_system.components import TagComponent
from dj_design_system.config import (
    AppSettings,
    CanvasBackground,
    CanvasSettings,
    DesignSystemSettings,
    DirectorySettings,
    GallerySettings,
    Theme,
)
from dj_design_system.data import ComponentInfo, NavNode
from dj_design_system.exceptions import ComponentDoesNotExist
from dj_design_system.parameters import StrParam
from dj_design_system.services import canvas as canvas_service
from dj_design_system.services import canvas_renderer as canvas_renderer_service
from dj_design_system.services import config as config_service
from dj_design_system.services import gallery_context as gallery_context_service
from dj_design_system.services import media as media_service
from dj_design_system.services import navigation as navigation_service
from dj_design_system.services.registry import ComponentRegistry
from dj_design_system.types import FlattenStrategy, NodeType


class _DummyWidget(TagComponent):
    label = StrParam(default="hi")
    template_format_str = "<span>{label}</span>"


class _DummyAlert(TagComponent):
    text = StrParam(default="alert")
    template_format_str = "<div>{text}</div>"


class TestGalleryEnabledGuard:
    @pytest.mark.django_db
    def test_gallery_views_return_404_when_disabled(self) -> None:
        cfg = DesignSystemSettings(gallery=GallerySettings(enabled=False))
        client = Client()
        with override_settings(DJ_DESIGN_SYSTEM=cfg):
            assert client.get(reverse("gallery")).status_code == 404
            assert client.get(reverse("gallery-canvas-iframe")).status_code == 404
            assert (
                client.get(
                    reverse(
                        "gallery-node-root", kwargs={"app_label": "demo_components"}
                    )
                ).status_code
                == 404
            )

    @pytest.mark.django_db
    def test_rest_api_views_return_404_when_gallery_disabled(
        self, registry_with_demo_components
    ) -> None:
        cfg = DesignSystemSettings(gallery=GallerySettings(enabled=False))
        factory = RequestFactory()

        with override_settings(DJ_DESIGN_SYSTEM=cfg):
            reg_view = ComponentRegistryView.as_view(
                registry=registry_with_demo_components
            )
            with pytest.raises(Http404):
                reg_view(factory.get("/api/registry/"))

            render_view = ComponentRenderView.as_view(
                registry=registry_with_demo_components
            )
            with pytest.raises(Http404):
                render_view(
                    factory.post(
                        "/api/render/",
                        data=json.dumps({"name": "demo_components__alert"}),
                        content_type="application/json",
                    )
                )


class TestManualAndDelegatedNavOrder:
    def test_app_order_pins_apps_before_numeric_order_and_alpha(self) -> None:
        components = [
            ComponentInfo(
                component_class=_DummyWidget,
                name="w",
                app_label="zeta",
                relative_path="",
            ),
            ComponentInfo(
                component_class=_DummyWidget,
                name="w",
                app_label="alpha",
                relative_path="",
            ),
            ComponentInfo(
                component_class=_DummyWidget,
                name="w",
                app_label="beta",
                relative_path="",
            ),
            ComponentInfo(
                component_class=_DummyWidget,
                name="w",
                app_label="gamma",
                relative_path="",
            ),
        ]
        cfg = DesignSystemSettings(
            gallery=GallerySettings(app_order=("gamma", "alpha")),
            apps={
                "zeta": AppSettings(order=-10),
                "beta": AppSettings(order=5),
            },
        )
        with override_settings(DJ_DESIGN_SYSTEM=cfg):
            tree = navigation_service._build_navigation(
                components=components,
                app_component_paths={},
            )
        assert [node.slug for node in tree] == ["gamma", "alpha", "zeta", "beta"]

    def test_app_and_directory_nav_order_pin_slugs_and_buckets(self, tmp_path) -> None:
        comp_root = tmp_path / "components"
        comp_root.mkdir()
        (comp_root / "intro.md").write_text("# Intro\n")
        (comp_root / "guide.md").write_text("# Guide\n")
        sub = comp_root / "primitives"
        sub.mkdir()
        (sub / "tokens.md").write_text("# Tokens\n")

        components = [
            ComponentInfo(
                component_class=_DummyWidget,
                name="widget",
                app_label="demo_nav",
                relative_path="",
            ),
            ComponentInfo(
                component_class=_DummyAlert,
                name="alert",
                app_label="demo_nav",
                relative_path="primitives",
            ),
            ComponentInfo(
                component_class=_DummyWidget,
                name="badge",
                app_label="demo_nav",
                relative_path="primitives",
            ),
        ]
        cfg = DesignSystemSettings(
            apps={
                "demo_nav": AppSettings(
                    nav_order=(
                        "intro",
                        NodeType.COMPONENT,
                        NodeType.FOLDER,
                        NodeType.DOCUMENT,
                    ),
                    directories={
                        "primitives": DirectorySettings(
                            label="Primitives",
                            nav_order=("badge", "tokens", NodeType.COMPONENT),
                        )
                    },
                )
            }
        )
        with override_settings(DJ_DESIGN_SYSTEM=cfg):
            tree = navigation_service._build_navigation(
                components=components,
                app_component_paths={"demo_nav": comp_root},
            )

        assert len(tree) == 1
        root_children = [child.slug for child in tree[0].children]
        assert root_children == ["intro", "widget", "primitives", "guide"]

        primitives_node = tree[0].children[2]
        assert [child.slug for child in primitives_node.children] == [
            "badge",
            "tokens",
            "alert",
        ]

    def test_promoted_directory_label_used_in_breadcrumbs(self) -> None:
        cfg = DesignSystemSettings(
            apps={
                "demo_components": AppSettings(
                    directories={
                        "foundations": DirectorySettings(
                            label="Design Foundations",
                            promote_to_app=True,
                        )
                    }
                )
            }
        )
        with override_settings(DJ_DESIGN_SYSTEM=cfg):
            crumbs = navigation_service.build_breadcrumbs(
                "foundations", [], "Typography"
            )
        assert crumbs[1]["label"] == "Design Foundations"


class TestPrefixedShortNamesFalseSupport:
    def test_short_names_false_registers_only_qualified_tags_and_skips_unscoped_lookup(
        self,
    ) -> None:
        app_cfg = SimpleNamespace(
            label="contrib_ui",
            design_system=AppSettings(
                prefix="cui",
                flatten=FlattenStrategy.ALL,
                short_names=False,
            ),
        )
        fake_mod = SimpleNamespace(__name__=_DummyWidget.__module__)
        _DummyWidget.__module__ = fake_mod.__name__

        with (
            override_settings(DJ_DESIGN_SYSTEM=DesignSystemSettings()),
            mock.patch.object(apps, "get_app_config", return_value=app_cfg),
            mock.patch.object(
                ComponentRegistry,
                "_find_colocated_template",
                return_value=None,
            ),
        ):
            config_service.clear_config_cache()
            reg = ComponentRegistry()
            with mock.patch(
                "inspect.getmembers", return_value=[("_DummyWidget", _DummyWidget)]
            ):
                reg._discover_module(fake_mod, "contrib_ui", "elements.buttons")

        infos = reg.list_by_app("contrib_ui")
        assert len(infos) == 1
        info = infos[0]
        assert info.qualified_name == "cui___dummy_widget"
        assert info.qualified_only is True

        with pytest.raises(ComponentDoesNotExist):
            reg.get_by_name("_dummy_widget")
        assert reg.get_by_name("_dummy_widget", app_label="contrib_ui") is info

        lib = Library()
        reg.register_templatetags(lib)
        assert "cui___dummy_widget" in lib.tags
        assert "_dummy_widget" not in lib.tags

    def test_presentation_only_directory_inherits_parent_app_prefix(self) -> None:
        cfg = DesignSystemSettings(
            apps={
                "brand_app": AppSettings(
                    prefix="brand",
                    flatten=FlattenStrategy.ALL,
                    directories={
                        "cards": DirectorySettings(
                            label="Card Collection",
                            promote_to_app=True,
                        )
                    },
                )
            }
        )
        reg = ComponentRegistry()
        with override_settings(DJ_DESIGN_SYSTEM=cfg):
            resolved = reg._resolve_namespace_prefix("brand_app", "cards.hero")
        assert resolved == ("brand", ("cards", "hero"), FlattenStrategy.ALL)

    def test_qualified_only_component_hides_duplicate_qualified_usage_block(
        self,
    ) -> None:
        info = ComponentInfo(
            component_class=_DummyWidget,
            name="widget",
            app_label="contrib_ui",
            relative_path="elements",
            namespace_prefix="cui",
            namespace_remaining_parts=("elements",),
            flatten_strategy=FlattenStrategy.ALL,
            qualified_only=True,
        )
        tpl = Template("{% include 'dj_design_system/gallery/panes/docs/usage.html' %}")
        rendered = tpl.render(
            Context(
                {
                    "component_info": info,
                    "usage_examples": [],
                    "tag_signature_long": SimpleNamespace(minimal="{% cui__widget %}"),
                }
            )
        )
        assert "Qualified tag usage" not in rendered

    def test_gallery_context_uses_qualified_name_for_qualified_only_component(
        self,
    ) -> None:
        info = ComponentInfo(
            component_class=_DummyWidget,
            name="widget",
            app_label="contrib_ui",
            relative_path="",
            namespace_prefix="cui",
            namespace_remaining_parts=(),
            flatten_strategy=FlattenStrategy.ALL,
            qualified_only=True,
        )
        node = NavNode(
            label="Widget",
            slug="widget",
            node_type=NodeType.COMPONENT,
            component=info,
            url="/gallery/contrib_ui/widget/",
        )
        with mock.patch.object(
            _DummyWidget, "get_app_label", return_value="contrib_ui"
        ):
            ctx = gallery_context_service.build_component_page_context(
                query_params={},
                cookies={},
                base_context={},
                node=node,
                app_label="contrib_ui",
                path_parts=[],
            )
        assert "cui__widget" in ctx["tag_signature"].minimal

    def test_flatten_without_prefix_uses_app_label_and_flattens(self) -> None:
        cfg = DesignSystemSettings(
            apps={"flat_app": AppSettings(flatten=FlattenStrategy.ALL)}
        )
        reg = ComponentRegistry()
        with override_settings(DJ_DESIGN_SYSTEM=cfg):
            resolved = reg._resolve_namespace_prefix("flat_app", "cards.hero")
        assert resolved == ("flat_app", ("cards", "hero"), FlattenStrategy.ALL)


class TestReviewHardeningEdgeCases:
    @pytest.mark.django_db
    def test_gallery_disabled_returns_404_even_for_permitted_user_when_private(
        self,
    ) -> None:
        user_model = get_user_model()
        user = user_model.objects.create_user(username="viewer", password="pw")
        perm = Permission.objects.get(codename="can_view_gallery")
        user.user_permissions.add(perm)

        cfg = DesignSystemSettings(
            gallery=GallerySettings(enabled=False, is_public=False)
        )
        client = Client()
        client.force_login(user)
        with override_settings(DJ_DESIGN_SYSTEM=cfg):
            assert client.get(reverse("gallery")).status_code == 404

    def test_media_get_bundle_urls_accepts_bare_string_specs(self) -> None:
        with (
            mock.patch.object(media_service, "_WEBPACK_AVAILABLE", True),
            mock.patch.object(
                media_service,
                "_webpack_get_files",
                side_effect=lambda name, extension, config: [
                    {"url": f"/{config}/{name}.{extension}"}
                ],
                create=True,
            ),
        ):
            urls = media_service.get_bundle_urls(["main", ("admin", "CUSTOM")], "css")
        assert urls == ["/DEFAULT/main.css", "/CUSTOM/admin.css"]

    def test_canvas_renderer_tombstones_and_canvas_background(self) -> None:
        cfg = DesignSystemSettings(
            canvas=CanvasSettings(
                html_attrs={"body": {"data-global": "keep", "data-drop": "old"}},
                backgrounds={"warm": CanvasBackground(label="Warm", color="#fef0e0")},
                default_background="warm",
            )
        )
        theme = Theme(
            value="brand",
            label="Brand",
            html_attrs={"body": {"data-drop": None, "data-theme": "yes"}},
            canvas_background=CanvasBackground(label="Brand BG", color="#123456"),
        )
        with override_settings(DJ_DESIGN_SYSTEM=cfg):
            _, body_attrs = canvas_renderer_service.build_html_attrs(theme_dict=theme)
            styles = canvas_renderer_service.build_canvas_bg_styles(theme_dict=theme)
            bg_cls = canvas_service.canvas_bg_class({}, theme_dict=theme)
        assert 'data-global="keep"' in body_attrs
        assert 'data-theme="yes"' in body_attrs
        assert "data-drop" not in body_attrs
        assert "#fef0e0" in styles
        assert "#123456" in styles
        assert bg_cls == "canvas-bg-theme-brand"

    def test_app_root_slug_pins_do_not_leak_into_subfolders(self, tmp_path) -> None:
        comp_root = tmp_path / "components"
        sub = comp_root / "nested"
        sub.mkdir(parents=True)
        (comp_root / "zeta.md").write_text("# Zeta\n")
        (sub / "zeta.md").write_text("# Sub Zeta\n")
        (sub / "alpha.md").write_text("# Sub Alpha\n")

        cfg = DesignSystemSettings(
            apps={
                "leak_app": AppSettings(
                    nav_order=("zeta", NodeType.DOCUMENT, NodeType.FOLDER),
                )
            }
        )
        with override_settings(DJ_DESIGN_SYSTEM=cfg):
            tree = navigation_service._build_navigation(
                components=[],
                app_component_paths={"leak_app": comp_root},
            )
        assert [c.slug for c in tree[0].children] == ["zeta", "nested"]
        nested = tree[0].children[1]
        assert [c.slug for c in nested.children] == ["alpha", "zeta"]

    def test_nav_order_alphabetical_and_setting_changed_clears_nav_cache(self) -> None:
        components = [
            ComponentInfo(
                component_class=_DummyWidget,
                name="beta",
                app_label="alpha_app",
                relative_path="",
            ),
            ComponentInfo(
                component_class=_DummyAlert,
                name="alpha",
                app_label="alpha_app",
                relative_path="",
            ),
        ]
        cfg = DesignSystemSettings(gallery=GallerySettings(nav_order="alphabetical"))
        with override_settings(DJ_DESIGN_SYSTEM=cfg):
            tree = navigation_service._build_navigation(
                components=components,
                app_component_paths={},
            )
        assert [c.slug for c in tree[0].children] == ["alpha", "beta"]

        with mock.patch.object(
            navigation_service, "clear_navigation_cache"
        ) as mock_clear:
            setting_changed.send(
                sender=self.__class__,
                setting="DJ_DESIGN_SYSTEM",
                value=cfg,
                enter=True,
            )
        mock_clear.assert_called_once()
