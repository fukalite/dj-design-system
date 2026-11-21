"""Tests for settings migration service and `manage.py migrate_dds_settings`."""

from __future__ import annotations

import io
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest
from django.apps import AppConfig, apps
from django.core.management import CommandError, call_command
from django.test import override_settings

from dj_design_system.config import (
    AppSettings,
    DesignSystemSettings,
    GallerySettings,
)
from dj_design_system.services import config as config_service
from dj_design_system.services import settings_migration
from dj_design_system.types import FlattenStrategy, NodeType


class TestExecEquivalenceGolden:
    def test_generated_code_executes_to_equal_design_system_settings(self) -> None:
        legacy = {
            "DESIGN_SYSTEM_NAME": "Golden DS",
            "ENABLE_GALLERY": False,
            "GALLERY_IS_PUBLIC": False,
            "GALLERY_NAV_ORDER": [NodeType.COMPONENT, NodeType.FOLDER],
            "GLOBAL_CSS": ["site/base.css"],
            "GLOBAL_JS": ["site/app.js"],
            "GLOBAL_CSS_BUNDLES": [("main",)],
            "GLOBAL_JS_BUNDLES": [("app", "CUSTOM")],
            "GALLERY_CANVAS_EXTRA_BACKGROUNDS": {
                "warm": {"label": "Warm", "color": "#fef3e2"},
            },
            "GALLERY_CANVAS_DEFAULT_BACKGROUND": "warm",
            "GALLERY_CANVAS_HTML_ATTRS": {"html": {"data-env": "preview"}},
            "GALLERY_CODEHILITE_STYLE": "",
            "GALLERY_THEMES": {
                "brand": {
                    "label": "Brand",
                    "css": ["brand.css"],
                    "canvas_background": "warm",
                    "dark_mode": {
                        "html_attrs": {"html": {"class": "dark"}},
                        "canvas_background": "dark-grey",
                    },
                }
            },
            "GALLERY_DEFAULT_THEME": "brand",
            "GALLERY_UI_THEMES": {
                "custom_ui": {"label": "Custom UI"},
            },
            "GALLERY_DEFAULT_UI_THEME": "custom_ui",
            "GALLERY_INCLUDE_APPS": ["demo_components"],
            "GALLERY_EXCLUDE_APPS": ["demo_single"],
            "GALLERY_EXTRA_CSS": ["gallery.css"],
            "GALLERY_DOC_VARIANTS": {"minimal": True, "maximal": False},
            "APP_THEMES": {"demo_components": ["brand"]},
            "APP_CSS": {"demo_components": ["demo.css"]},
            "APP_JS": {"demo_components": ["demo.js"]},
            "APP_CSS_BUNDLES": {"demo_components": [("demo_css",)]},
            "APP_JS_BUNDLES": {"demo_components": [("demo_js", "CUSTOM")]},
            "APP_CANVAS_HTML_ATTRS": {
                "demo_components": {"body": {"class": "demo-body"}}
            },
            "COMPONENT_DIRECTORIES": {
                "demo_components": {
                    "": {
                        "prefix": "ui",
                        "flatten": FlattenStrategy.ALL,
                        "label": "Demo",
                    },
                    "cards": {
                        "prefix": "cards",
                        "flatten": FlattenStrategy.LEAF,
                        "promote_to_app": True,
                        "label": "Cards",
                    },
                }
            },
        }
        expected = config_service.adapt_legacy_settings(raw=legacy)
        rendered = settings_migration.render_project_settings(
            config=expected,
            format_with_ruff=False,
        )
        namespace: dict[str, object] = {}
        exec(rendered, namespace)
        actual = namespace["DJ_DESIGN_SYSTEM"]
        assert actual == expected

    def test_include_defaults_emits_default_fields(self) -> None:
        cfg = DesignSystemSettings()
        minimal = settings_migration.render_project_settings(
            config=cfg,
            include_defaults=False,
            format_with_ruff=False,
        )
        verbose = settings_migration.render_project_settings(
            config=cfg,
            include_defaults=True,
            format_with_ruff=False,
        )
        assert "DesignSystemSettings()" in minimal
        assert "name='Django Design System'" in verbose
        assert "gallery=GallerySettings(" in verbose


class TestAstManualHints:
    def test_detects_unpacking_env_vars_base_dir_and_callables(self) -> None:
        source = """
from functools import partial
import os
DJ_DESIGN_SYSTEM = {
    **base_settings.DJ_DESIGN_SYSTEM,
    "GALLERY_IS_PUBLIC": os.getenv("PUBLIC", "1") == "1",
    "GLOBAL_CSS": [str(BASE_DIR / "static" / "site.css")],
    "GALLERY_DOC_VARIANTS": {
        "custom": {
            "param_factory": lambda cls: {},
            "slot_factory": partial(dict, a=1),
        }
    },
}
"""
        hints = settings_migration.inspect_settings_source(source=source)
        joined = "\n".join(hints)
        assert ".replace(" in joined
        assert "Dynamic expression" in joined
        assert "BASE_DIR" in joined
        assert "Callable" in joined

    def test_missing_assignment_reports_warning(self) -> None:
        hints = settings_migration.inspect_settings_source(source="DEBUG = True\n")
        assert any("could not locate" in hint.lower() for hint in hints)


class TestSplitAppsClassification:
    def test_classifies_local_vs_third_party_and_detects_edge_cases(
        self, tmp_path: Path
    ) -> None:
        local_dir = tmp_path / "my_local_app"
        local_dir.mkdir()
        (local_dir / "apps.py").write_text("default = False\n")

        existing_ds_dir = tmp_path / "already_migrated"
        existing_ds_dir.mkdir()

        venv_dir = tmp_path / ".venv" / "lib" / "site-packages" / "vendor_pkg"
        venv_dir.mkdir(parents=True)

        local_default_cfg = AppConfig(
            "my_local_app",
            SimpleNamespace(
                __file__=str(local_dir / "__init__.py"), __path__=[str(local_dir)]
            ),
        )
        local_default_cfg.label = "custom_label"

        migrated_cfg = SimpleNamespace(
            name="already_migrated",
            label="already_migrated",
            path=str(existing_ds_dir),
            design_system=AppSettings(prefix="am"),
        )
        vendor_cfg = SimpleNamespace(
            name="vendor_pkg",
            label="vendor_pkg",
            path=str(venv_dir),
        )
        builtin_cfg = SimpleNamespace(
            name="dj_design_system",
            label="dj_design_system",
            path=str(tmp_path / "dj_design_system"),
        )
        django_cfg = SimpleNamespace(
            name="django.contrib.admin",
            label="admin",
            path=str(tmp_path / "admin"),
        )

        app_map = {
            "custom_label": local_default_cfg,
            "already_migrated": migrated_cfg,
            "vendor_pkg": vendor_cfg,
            "dj_design_system": builtin_cfg,
            "admin": django_cfg,
        }

        with mock.patch.object(apps, "get_app_config", side_effect=app_map.__getitem__):
            local_info = settings_migration.classify_app(
                app_label="custom_label", project_root=tmp_path
            )
            migrated_info = settings_migration.classify_app(
                app_label="already_migrated", project_root=tmp_path
            )
            vendor_info = settings_migration.classify_app(
                app_label="vendor_pkg", project_root=tmp_path
            )
            builtin_info = settings_migration.classify_app(
                app_label="dj_design_system", project_root=tmp_path
            )
            django_info = settings_migration.classify_app(
                app_label="admin", project_root=tmp_path
            )

        assert local_info.is_local is True
        assert local_info.has_apps_py is True
        assert local_info.uses_default_app_config is True
        assert migrated_info.is_local is True
        assert migrated_info.already_has_design_system is True
        assert vendor_info.is_local is False
        assert builtin_info.is_local is False
        assert django_info.is_local is False


class TestMigrateDdsSettingsCommand:
    def test_default_stdout_and_missing_ruff_fallback(self) -> None:
        out = io.StringIO()
        with (
            override_settings(
                DJ_DESIGN_SYSTEM={
                    "DESIGN_SYSTEM_NAME": "CLI Test",
                    "APP_CSS": {"demo_components": ["demo.css"]},
                }
            ),
            mock.patch("shutil.which", return_value=None),
        ):
            call_command("migrate_dds_settings", stdout=out)
        output = out.getvalue()
        assert "DesignSystemSettings(" in output
        assert "name='CLI Test'" in output

    def test_split_apps_and_app_filter(self) -> None:
        out = io.StringIO()
        with override_settings(
            DJ_DESIGN_SYSTEM={
                "APP_CSS": {
                    "demo_components": ["demo.css"],
                    "demo_single": ["single.css"],
                }
            }
        ):
            call_command(
                "migrate_dds_settings",
                "--split-apps",
                "--app",
                "demo_components",
                "--no-format",
                stdout=out,
            )
        output = out.getvalue()
        assert "demo_components" in output
        assert "AppSettings(" in output
        assert "demo_single" not in output

    def test_check_flag_fails_on_legacy_dict_and_passes_on_typed(self) -> None:
        with override_settings(DJ_DESIGN_SYSTEM={"DESIGN_SYSTEM_NAME": "Old"}):
            with pytest.raises(CommandError):
                call_command("migrate_dds_settings", "--check")

        out = io.StringIO()
        with override_settings(
            DJ_DESIGN_SYSTEM=DesignSystemSettings(
                name="Migrated",
                gallery=GallerySettings(is_public=True),
            )
        ):
            call_command("migrate_dds_settings", "--check", stdout=out)
        assert "clean" in out.getvalue().lower() or "migrated" in out.getvalue().lower()
