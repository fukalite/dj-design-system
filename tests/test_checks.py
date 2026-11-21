"""Tests for dj_design_system system checks."""

from __future__ import annotations

from types import SimpleNamespace
from unittest import mock

from django.apps import apps
from django.core.checks import Error, Warning, run_checks
from django.test import override_settings

from dj_design_system.checks import (
    check_design_system_settings,
    check_gallery_settings,
)
from dj_design_system.config import (
    AppSettings,
    CanvasBackground,
    CanvasSettings,
    DarkModeConfig,
    DesignSystemSettings,
    DirectorySettings,
    GallerySettings,
    Theme,
)
from dj_design_system.constants import BUILTIN_APP_LABEL, BUILTIN_PREFIX
from dj_design_system.types import FlattenStrategy


class TestGallerySettingsChecks:
    def test_clean_defaults_produce_no_messages(self) -> None:
        messages = check_gallery_settings()
        assert messages == []

    def test_e001_invalid_include_apps_type(self) -> None:
        with override_settings(DJ_DESIGN_SYSTEM={"GALLERY_INCLUDE_APPS": "not-a-list"}):
            messages = check_gallery_settings()
        assert len(messages) == 1
        assert isinstance(messages[0], Error)
        assert messages[0].id == "dj_design_system.E001"

    def test_e002_invalid_exclude_apps_type(self) -> None:
        with override_settings(DJ_DESIGN_SYSTEM={"GALLERY_EXCLUDE_APPS": 123}):
            messages = check_gallery_settings()
        assert len(messages) == 1
        assert isinstance(messages[0], Error)
        assert messages[0].id == "dj_design_system.E002"

    def test_e003_overlapping_apps(self) -> None:
        with override_settings(
            DJ_DESIGN_SYSTEM={
                "GALLERY_INCLUDE_APPS": ["demo_components", "demo_single"],
                "GALLERY_EXCLUDE_APPS": ["demo_single"],
            }
        ):
            messages = check_gallery_settings()
        error_ids = [m.id for m in messages if isinstance(m, Error)]
        assert "dj_design_system.E003" in error_ids
        err = next(m for m in messages if m.id == "dj_design_system.E003")
        assert "demo_single" in err.msg

    def test_w001_redundant_exclude_apps_when_include_set(self) -> None:
        with override_settings(
            DJ_DESIGN_SYSTEM={
                "GALLERY_INCLUDE_APPS": ["demo_components"],
                "GALLERY_EXCLUDE_APPS": ["demo_single"],
            }
        ):
            messages = check_gallery_settings()
        warning_ids = [m.id for m in messages if isinstance(m, Warning)]
        assert "dj_design_system.W001" in warning_ids

    def test_w002_uninstalled_apps(self) -> None:
        with override_settings(
            DJ_DESIGN_SYSTEM={
                "GALLERY_INCLUDE_APPS": ["non_existent_app_foo"],
            }
        ):
            messages = check_gallery_settings()
        warning_ids = [m.id for m in messages if isinstance(m, Warning)]
        assert "dj_design_system.W002" in warning_ids
        warn = next(m for m in messages if m.id == "dj_design_system.W002")
        assert "non_existent_app_foo" in warn.msg

    def test_django_check_runner_finds_registered_check(self) -> None:
        with override_settings(
            DJ_DESIGN_SYSTEM={
                "GALLERY_INCLUDE_APPS": ["non_existent_app_bar"],
            }
        ):
            all_messages = run_checks(tags=["dj_design_system"])
        assert any(m.id == "dj_design_system.W002" for m in all_messages)


class TestTypedSettingsSystemChecks:
    def test_clean_typed_defaults_produce_no_messages(self) -> None:
        with override_settings(DJ_DESIGN_SYSTEM=DesignSystemSettings()):
            assert check_design_system_settings() == []

    def test_e004_invalid_prefix_syntax(self) -> None:
        cfg = DesignSystemSettings(
            apps={"demo_components": AppSettings(prefix="Bad__Prefix")}
        )
        with override_settings(DJ_DESIGN_SYSTEM=cfg):
            messages = check_design_system_settings()
        error_ids = [m.id for m in messages if isinstance(m, Error)]
        assert "dj_design_system.E004" in error_ids

    def test_e005_reserved_dds_whole_app_prefix(self) -> None:
        cfg = DesignSystemSettings(
            apps={"demo_components": AppSettings(prefix=BUILTIN_PREFIX)}
        )
        with override_settings(DJ_DESIGN_SYSTEM=cfg):
            messages = check_design_system_settings()
        error_ids = [m.id for m in messages if isinstance(m, Error)]
        assert "dj_design_system.E005" in error_ids

    def test_e005_allows_directory_level_dds_shadowing(self, tmp_path) -> None:
        comp_dir = tmp_path / "components" / "overrides"
        comp_dir.mkdir(parents=True)
        fake_app = SimpleNamespace(
            label="consumer_app",
            path=str(tmp_path),
            design_system=AppSettings(
                directories={"overrides": DirectorySettings(prefix=BUILTIN_PREFIX)}
            ),
        )
        with (
            override_settings(DJ_DESIGN_SYSTEM=DesignSystemSettings()),
            mock.patch.object(apps, "get_app_configs", return_value=[fake_app]),
            mock.patch.object(apps, "get_app_config", return_value=fake_app),
        ):
            messages = check_design_system_settings()
        assert not any(m.id == "dj_design_system.E005" for m in messages)

    def test_e006_duplicate_effective_app_prefix(self) -> None:
        app_a = SimpleNamespace(
            name="app_a",
            label="app_a",
            path="/tmp/app_a",
            design_system=AppSettings(prefix="shared"),
        )
        app_b = SimpleNamespace(
            name="app_b",
            label="app_b",
            path="/tmp/app_b",
            design_system=AppSettings(prefix="shared"),
        )
        app_map = {"app_a": app_a, "app_b": app_b}

        with (
            override_settings(DJ_DESIGN_SYSTEM=DesignSystemSettings()),
            mock.patch.object(apps, "get_app_configs", return_value=[app_a, app_b]),
            mock.patch.object(apps, "get_app_config", side_effect=app_map.__getitem__),
        ):
            messages = check_design_system_settings()
        error_ids = [m.id for m in messages if isinstance(m, Error)]
        assert "dj_design_system.E006" in error_ids

    def test_e009_invalid_dj_design_system_type(self) -> None:
        with override_settings(DJ_DESIGN_SYSTEM="invalid-type"):
            messages = check_design_system_settings()
        error_ids = [m.id for m in messages if isinstance(m, Error)]
        assert "dj_design_system.E009" in error_ids

    def test_e010_invalid_app_config_design_system_type(self) -> None:
        bad_app = SimpleNamespace(
            name="bad_app",
            label="bad_app",
            path="/tmp/bad_app",
            design_system={"prefix": "nope"},
        )
        with (
            override_settings(DJ_DESIGN_SYSTEM=DesignSystemSettings()),
            mock.patch.object(apps, "get_app_configs", return_value=[bad_app]),
        ):
            messages = check_design_system_settings()
        error_ids = [m.id for m in messages if isinstance(m, Error)]
        assert "dj_design_system.E010" in error_ids

    def test_e011_builtin_naming_invariant_override(self) -> None:
        cfg = DesignSystemSettings(
            apps={
                BUILTIN_APP_LABEL: AppSettings(
                    prefix="custom",
                    flatten=FlattenStrategy.NONE,
                    short_names=True,
                )
            }
        )
        with override_settings(DJ_DESIGN_SYSTEM=cfg):
            messages = check_design_system_settings()
        error_ids = [m.id for m in messages if isinstance(m, Error)]
        assert "dj_design_system.E011" in error_ids

    def test_e012_theme_value_key_mismatch(self) -> None:
        cfg = DesignSystemSettings(
            themes={"brand": Theme(value="wrong", label="Brand")},
            default_theme="brand",
        )
        with override_settings(DJ_DESIGN_SYSTEM=cfg):
            messages = check_design_system_settings()
        error_ids = [m.id for m in messages if isinstance(m, Error)]
        assert "dj_design_system.E012" in error_ids

    def test_e013_promoted_directory_collisions_and_nesting(self, tmp_path) -> None:
        (tmp_path / "components" / "parent" / "child").mkdir(parents=True)
        (tmp_path / "components" / "demo_components").mkdir(parents=True)
        (tmp_path / "components" / "shared_dir").mkdir(parents=True)
        other_root = tmp_path / "other"
        (other_root / "components" / "shared_dir").mkdir(parents=True)

        fake_app = SimpleNamespace(
            name="owner_app",
            label="owner_app",
            path=str(tmp_path),
            design_system=AppSettings(
                directories={
                    "parent": DirectorySettings(promote_to_app=True),
                    "parent.child": DirectorySettings(promote_to_app=True),
                    "demo_components": DirectorySettings(promote_to_app=True),
                    "shared_dir": DirectorySettings(promote_to_app=True),
                }
            ),
        )
        other_app = SimpleNamespace(
            name="other_app",
            label="other_app",
            path=str(other_root),
            design_system=AppSettings(
                directories={
                    "shared_dir": DirectorySettings(promote_to_app=True),
                }
            ),
        )
        existing_app = SimpleNamespace(
            name="demo_components", label="demo_components", path="/tmp/other"
        )
        app_map = {
            "owner_app": fake_app,
            "other_app": other_app,
            "demo_components": existing_app,
        }

        with (
            override_settings(DJ_DESIGN_SYSTEM=DesignSystemSettings()),
            mock.patch.object(
                apps,
                "get_app_configs",
                return_value=[fake_app, other_app, existing_app],
            ),
            mock.patch.object(apps, "get_app_config", side_effect=app_map.__getitem__),
        ):
            messages = check_design_system_settings()
        e013_messages = [m for m in messages if m.id == "dj_design_system.E013"]
        assert len(e013_messages) >= 3

    def test_w003_uninstalled_app_in_apps_mapping(self) -> None:
        cfg = DesignSystemSettings(apps={"ghost_app": AppSettings(label="Ghost")})
        with override_settings(DJ_DESIGN_SYSTEM=cfg):
            messages = check_design_system_settings()
        assert any(m.id == "dj_design_system.W003" for m in messages)

    def test_w004_missing_default_theme_ui_theme_and_background(self) -> None:
        cfg = DesignSystemSettings(
            themes={"brand": Theme(label="Brand")},
            default_theme="missing_theme",
            gallery=GallerySettings(
                ui_themes={"desert": Theme(label="Desert")},
                default_ui_theme="missing_ui",
            ),
            canvas=CanvasSettings(
                backgrounds={"white": CanvasBackground(label="White", color="#fff")},
                default_background="missing_bg",
            ),
        )
        with override_settings(DJ_DESIGN_SYSTEM=cfg):
            messages = check_design_system_settings()
        w004 = [m for m in messages if m.id == "dj_design_system.W004"]
        assert len(w004) == 3

    def test_w005_unknown_theme_canvas_background_slug(self) -> None:
        cfg = DesignSystemSettings(
            themes={
                "brand": Theme(
                    label="Brand",
                    canvas_background="nonexistent-bg",
                    dark_mode=DarkModeConfig(canvas_background="also-missing"),
                )
            },
            default_theme="brand",
        )
        with override_settings(DJ_DESIGN_SYSTEM=cfg):
            messages = check_design_system_settings()
        w005 = [m for m in messages if m.id == "dj_design_system.W005"]
        assert len(w005) == 2

    def test_w006_unknown_or_empty_app_themes(self) -> None:
        cfg = DesignSystemSettings(
            apps={
                "demo_components": AppSettings(themes=("nonexistent",)),
            }
        )
        with override_settings(DJ_DESIGN_SYSTEM=cfg):
            messages = check_design_system_settings()
        assert any(m.id == "dj_design_system.W006" for m in messages)

        empty_cfg = DesignSystemSettings(
            apps={"demo_components": AppSettings(themes=())}
        )
        with override_settings(DJ_DESIGN_SYSTEM=empty_cfg):
            empty_messages = check_design_system_settings()
        assert any(m.id == "dj_design_system.W006" for m in empty_messages)

    def test_w007_nonexistent_directory_under_components(self, tmp_path) -> None:
        (tmp_path / "components").mkdir()
        fake_app = SimpleNamespace(
            label="dir_app",
            path=str(tmp_path),
            design_system=AppSettings(
                directories={"does.not.exist": DirectorySettings(label="Missing")}
            ),
        )
        with (
            override_settings(DJ_DESIGN_SYSTEM=DesignSystemSettings()),
            mock.patch.object(apps, "get_app_configs", return_value=[fake_app]),
            mock.patch.object(apps, "get_app_config", return_value=fake_app),
        ):
            messages = check_design_system_settings()
        assert any(m.id == "dj_design_system.W007" for m in messages)
