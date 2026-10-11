"""Tests for dj_design_system system checks."""

from django.core.checks import Error, Warning, run_checks
from django.test import override_settings

from dj_design_system.checks import check_gallery_settings


class TestGallerySettingsChecks:
    def test_clean_defaults_produce_no_messages(self):
        messages = check_gallery_settings()
        assert messages == []

    def test_e001_invalid_include_apps_type(self):
        with override_settings(DJ_DESIGN_SYSTEM={"GALLERY_INCLUDE_APPS": "not-a-list"}):
            messages = check_gallery_settings()
        assert len(messages) == 1
        assert isinstance(messages[0], Error)
        assert messages[0].id == "dj_design_system.E001"

    def test_e002_invalid_exclude_apps_type(self):
        with override_settings(DJ_DESIGN_SYSTEM={"GALLERY_EXCLUDE_APPS": 123}):
            messages = check_gallery_settings()
        assert len(messages) == 1
        assert isinstance(messages[0], Error)
        assert messages[0].id == "dj_design_system.E002"

    def test_e003_overlapping_apps(self):
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

    def test_w001_redundant_exclude_apps_when_include_set(self):
        with override_settings(
            DJ_DESIGN_SYSTEM={
                "GALLERY_INCLUDE_APPS": ["demo_components"],
                "GALLERY_EXCLUDE_APPS": ["demo_single"],
            }
        ):
            messages = check_gallery_settings()
        warning_ids = [m.id for m in messages if isinstance(m, Warning)]
        assert "dj_design_system.W001" in warning_ids

    def test_w002_uninstalled_apps(self):
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

    def test_django_check_runner_finds_registered_check(self):
        with override_settings(
            DJ_DESIGN_SYSTEM={
                "GALLERY_INCLUDE_APPS": ["non_existent_app_bar"],
            }
        ):
            all_messages = run_checks(tags=["dj_design_system"])
        assert any(m.id == "dj_design_system.W002" for m in all_messages)
