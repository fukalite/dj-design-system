"""Tests for the component directories service."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from django.apps import AppConfig

from dj_design_system.services import component_dirs as component_dirs_service


DEMO_APP_DIR = Path(__file__).parent.parent / "example_project" / "demo_components"


def _app_config(label: str, path: Path | str) -> MagicMock:
    config = MagicMock(spec=AppConfig)
    config.label = label
    config.path = str(path)
    return config


class TestGetComponentsDir:
    def test_returns_existing_components_dir(self) -> None:
        config = _app_config("demo_components", DEMO_APP_DIR)
        assert component_dirs_service.get_components_dir(app_config=config) == (
            DEMO_APP_DIR / "components"
        )

    def test_returns_none_without_components_dir(self, tmp_path: Path) -> None:
        config = _app_config("empty", tmp_path)
        assert component_dirs_service.get_components_dir(app_config=config) is None

    def test_returns_none_when_components_is_a_file(self, tmp_path: Path) -> None:
        (tmp_path / "components").write_text("")
        config = _app_config("odd", tmp_path)
        assert component_dirs_service.get_components_dir(app_config=config) is None


class TestGetComponentsDirs:
    def test_maps_labels_to_dirs_skipping_apps_without_one(
        self, tmp_path: Path
    ) -> None:
        configs = [
            _app_config("demo_components", DEMO_APP_DIR),
            _app_config("empty", tmp_path),
        ]
        with patch(
            "dj_design_system.services.component_dirs.apps.get_app_configs",
            return_value=configs,
        ):
            dirs = component_dirs_service.get_components_dirs()

        assert dirs == {"demo_components": DEMO_APP_DIR / "components"}
