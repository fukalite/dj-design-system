"""Tests for dj_design_system.services.config 4-tier resolution and caching."""

from __future__ import annotations

from types import SimpleNamespace
from unittest import mock

from django.apps import apps
from django.core.signals import setting_changed
from django.test import override_settings

from dj_design_system.config import (
    AppSettings,
    CanvasBackground,
    CanvasSettings,
    DesignSystemSettings,
    DirectorySettings,
    GallerySettings,
    Theme,
)
from dj_design_system.constants import BUILTIN_APP_LABEL, BUILTIN_PREFIX
from dj_design_system.services import config as config_service
from dj_design_system.types import FlattenStrategy, NodeType


class TestRootConfigResolution:
    def test_default_config_when_setting_omitted(self) -> None:
        with override_settings():
            from django.conf import settings as django_settings

            if hasattr(django_settings, "DJ_DESIGN_SYSTEM"):
                delattr(django_settings, "DJ_DESIGN_SYSTEM")
            config_service.clear_config_cache()
            cfg = config_service.get_config()
        assert isinstance(cfg, DesignSystemSettings)
        assert cfg.name == "Django Design System"
        assert cfg.gallery.enabled is True

    def test_typed_settings_returned_directly(self) -> None:
        custom = DesignSystemSettings(
            name="Acme",
            css=("acme.css",),
            gallery=GallerySettings(enabled=False, is_public=False),
            canvas=CanvasSettings(
                backgrounds={"warm": CanvasBackground(label="Warm", color="#fff1e0")},
                default_background="warm",
            ),
        )
        with override_settings(DJ_DESIGN_SYSTEM=custom):
            assert config_service.get_config() is custom
            assert config_service.get_gallery_settings().enabled is False
            assert config_service.get_default_background().color == "#fff1e0"

    def test_legacy_dict_not_stale_on_in_place_mutation(self) -> None:
        raw: dict[str, object] = {"DESIGN_SYSTEM_NAME": "Initial"}
        with override_settings(DJ_DESIGN_SYSTEM=raw):
            assert config_service.get_config().name == "Initial"
            raw["DESIGN_SYSTEM_NAME"] = "Mutated"
            assert config_service.get_config().name == "Mutated"


class TestFourTierAppResolution:
    def test_inherits_app_config_defaults_and_project_global_nav_order(self) -> None:
        app_cfg = SimpleNamespace(
            label="synthetic_app",
            design_system=AppSettings(
                prefix="syn",
                flatten=FlattenStrategy.ALL,
                short_names=False,
                themes=("dark",),
                css=("syn/base.css",),
                js=("syn/base.js",),
                canvas_html_attrs={"body": {"class": "syn-body", "data-a": "1"}},
                directories={
                    "cards": DirectorySettings(prefix="syn_cards", label="Cards"),
                },
            ),
        )
        project = DesignSystemSettings(
            gallery=GallerySettings(nav_order="alphabetical"),
        )
        with (
            override_settings(DJ_DESIGN_SYSTEM=project),
            mock.patch.object(apps, "get_app_config", return_value=app_cfg),
        ):
            config_service.clear_config_cache()
            resolved = config_service.get_app_settings(app_label="synthetic_app")

        assert resolved.prefix == "syn"
        assert resolved.flatten is FlattenStrategy.ALL
        assert resolved.short_names is False
        assert resolved.themes == ("dark",)
        assert resolved.nav_order == "alphabetical"
        assert resolved.css == ("syn/base.css",)
        assert resolved.js == ("syn/base.js",)
        assert resolved.canvas_html_attrs == {
            "body": {"class": "syn-body", "data-a": "1"}
        }
        assert "cards" in resolved.directories

    def test_project_override_merges_extra_css_tombstones_and_directories(self) -> None:
        app_cfg = SimpleNamespace(
            label="vendor_ui",
            design_system=AppSettings(
                prefix="vendor",
                themes=("default",),
                css=("vendor/base.css", "vendor/extra.css"),
                js=("vendor/app.js",),
                nav_order=("intro", NodeType.COMPONENT),
                canvas_html_attrs={"body": {"class": "vendor-body", "data-x": "1"}},
                directories={
                    "cards": DirectorySettings(prefix="vcards", label="Vendor Cards"),
                    "legacy": DirectorySettings(prefix="vlegacy"),
                },
            ),
        )
        project = DesignSystemSettings(
            apps={
                "vendor_ui": AppSettings(
                    themes=("brand",),
                    extra_css=("project/tweaks.css", "vendor/base.css"),
                    js=(),
                    extra_js=("project/custom.js",),
                    canvas_html_attrs={
                        "body": {"data-x": None, "data-y": "2"},
                    },
                    directories={
                        "legacy": None,
                        "forms": DirectorySettings(prefix="vforms"),
                    },
                ),
            }
        )
        with (
            override_settings(DJ_DESIGN_SYSTEM=project),
            mock.patch.object(apps, "get_app_config", return_value=app_cfg),
        ):
            config_service.clear_config_cache()
            resolved = config_service.get_app_settings(app_label="vendor_ui")

        assert resolved.prefix == "vendor"
        assert resolved.themes == ("brand",)
        assert resolved.nav_order == ("intro", NodeType.COMPONENT)
        assert resolved.css == (
            "vendor/base.css",
            "vendor/extra.css",
            "project/tweaks.css",
        )
        assert resolved.js == ("project/custom.js",)
        assert resolved.canvas_html_attrs["body"]["class"] == "vendor-body"
        assert "data-x" not in resolved.canvas_html_attrs["body"]
        assert resolved.canvas_html_attrs["body"]["data-y"] == "2"
        assert "cards" in resolved.directories
        assert "forms" in resolved.directories
        assert "legacy" not in resolved.directories

    def test_project_none_clears_inherited_mappings(self) -> None:
        app_cfg = SimpleNamespace(
            label="clearable",
            design_system=AppSettings(
                canvas_html_attrs={"body": {"class": "from-app"}},
                directories={"cards": DirectorySettings(prefix="c")},
            ),
        )
        project = DesignSystemSettings(
            apps={
                "clearable": AppSettings(
                    canvas_html_attrs=None,
                    directories=None,
                ),
            }
        )
        with (
            override_settings(DJ_DESIGN_SYSTEM=project),
            mock.patch.object(apps, "get_app_config", return_value=app_cfg),
        ):
            config_service.clear_config_cache()
            resolved = config_service.get_app_settings(app_label="clearable")

        assert dict(resolved.canvas_html_attrs) == {}
        assert dict(resolved.directories) == {}

    def test_uninstalled_app_resolves_without_lookup_error(self) -> None:
        project = DesignSystemSettings(
            apps={"not_installed_app": AppSettings(css=("x.css",), themes=("default",))}
        )
        with override_settings(DJ_DESIGN_SYSTEM=project):
            resolved = config_service.get_app_settings(app_label="not_installed_app")
        assert resolved.css == ("x.css",)
        assert resolved.themes == ("default",)

    def test_builtin_app_invariants_cannot_be_overridden(self) -> None:
        project = DesignSystemSettings(
            apps={
                BUILTIN_APP_LABEL: AppSettings(
                    prefix="hacked",
                    flatten=FlattenStrategy.NONE,
                    short_names=True,
                )
            }
        )
        with override_settings(DJ_DESIGN_SYSTEM=project):
            resolved = config_service.get_app_settings(app_label=BUILTIN_APP_LABEL)
        assert resolved.prefix == BUILTIN_PREFIX
        assert resolved.flatten is FlattenStrategy.ALL
        assert resolved.short_names is False

    def test_apps_ready_gate_prevents_premature_caching(self) -> None:
        project = DesignSystemSettings(name="Gated")
        with (
            override_settings(DJ_DESIGN_SYSTEM=project),
            mock.patch.object(apps, "apps_ready", False),
        ):
            config_service.clear_config_cache()
            resolved = config_service.get_app_settings(app_label="demo_components")
            assert resolved.app_label == "demo_components"
            assert config_service._APP_SETTINGS_CACHE is None

    def test_setting_changed_clears_cache_for_dj_design_system_and_installed_apps(
        self,
    ) -> None:
        first = DesignSystemSettings(
            name="First",
            themes={"one": Theme(label="One")},
            default_theme="one",
        )
        second = DesignSystemSettings(
            name="Second",
            themes={"two": Theme(label="Two")},
            default_theme="two",
        )
        with override_settings(DJ_DESIGN_SYSTEM=first):
            assert config_service.get_config().name == "First"
            assert config_service.get_default_theme().value == "one"
        with override_settings(DJ_DESIGN_SYSTEM=second):
            assert config_service.get_config().name == "Second"
            assert config_service.get_default_theme().value == "two"

        with override_settings(DJ_DESIGN_SYSTEM=first):
            _ = config_service.get_app_settings(app_label=BUILTIN_APP_LABEL)
            assert config_service._APP_SETTINGS_CACHE is not None
            assert BUILTIN_APP_LABEL in config_service._APP_SETTINGS_CACHE[1]
            setting_changed.send(
                sender=self.__class__,
                setting="INSTALLED_APPS",
                value=[],
                enter=True,
            )
            assert config_service._APP_SETTINGS_CACHE is None

    def test_all_app_settings_includes_installed_and_synthetic_apps(self) -> None:
        project = DesignSystemSettings(
            apps={"synthetic_extra": AppSettings(label="Synthetic Extra")}
        )
        with override_settings(DJ_DESIGN_SYSTEM=project):
            all_apps = config_service.get_all_app_settings()
        assert BUILTIN_APP_LABEL in all_apps
        assert "synthetic_extra" in all_apps
        assert all_apps["synthetic_extra"].label == "Synthetic Extra"
